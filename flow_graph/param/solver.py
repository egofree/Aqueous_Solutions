"""Balance solver (X-PAR-02). Per-unit transfer functions compute edge rates and unit duties
from drivers.json. This first set covers the metals core acid loop and the EW cells.
check(): mass/energy closure of the solved units (must pass) and misfit against the graph
(reported; becomes a gate when X-PAR-04 writes the graph from the solver)."""
import json, os
from . import drivers as DR
from .constants import M, mw
from .sizing import electrochem as EC
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OX = {'Al2O3':{'Al':2,'O':3},'CaO':{'Ca':1,'O':1},'MgO':{'Mg':1,'O':1},'FeO':{'Fe':1,'O':1}}
HCL = mw({'H':1,'Cl':1}); NAOH = mw({'Na':1,'O':1,'H':1}); H2O = mw({'H':2,'O':1})
CHLORIDE = {'Al2O3':('AlCl3',{'Al':1,'Cl':3},2),'CaO':('CaCl2',{'Ca':1,'Cl':2},1),'MgO':('MgCl2',{'Mg':1,'Cl':2},1),'FeO':('FeCl2',{'Fe':1,'Cl':2},1)}
H2O_PER = {'Al2O3':3,'CaO':1,'MgO':1,'FeO':1}
EW_METAL = {1:('Au',3),2:('Ag',1),3:('Cu',2),4:('Pb',2),5:('Sn',2),6:('Ni',2),7:('Fe',2),8:('Cd',2),9:('Zn',2)}

def leach_acid(d):
    """Case A acid demand: oxide + n HCl -> chloride + water [GREENWOOD]; oxides from LUNAR_SOURCEBOOK."""
    feed = DR.val(d,'feed_rate_kg_d')*DR.val(d,'feed_case_A_silicate_oxide')
    ext = DR.val(d,'case_A_leach_extent'); n = DR.val(d,'hcl_stoich')
    mol_ox = {o: feed*f*ext*1000/mw(OX[o]) for o,f in DR.val(d,'case_A_oxide_fractions').items()}
    hcl_mol = sum(mol_ox[o]*n[o] for o in mol_ox)
    # closure: oxide + HCl = chloride + water (kg/d)
    m_in = sum(mol_ox[o]*mw(OX[o]) for o in mol_ox)/1000 + hcl_mol*HCL/1000
    m_out = sum(mol_ox[o]*CHLORIDE[o][2]*mw(CHLORIDE[o][1]) for o in mol_ox)/1000 + sum(mol_ox[o]*H2O_PER[o]*H2O for o in mol_ox)/1000
    return dict(hcl_kg_d=hcl_mol*HCL/1000, hcl_mol_d=hcl_mol, closure=(m_in, m_out))

def bmed(d, hcl_mol):
    """Salt split 1:1 acid:base; energy from published SEC per kg base [EDBM_WHEY_2021]."""
    base_kg = hcl_mol*NAOH/1000
    c = DR.val(d,'acid_conc_design_wt')
    return dict(acid_solution_kg_d=hcl_mol*HCL/1000/c, base_kg_d=base_kg,
                kW_published=DR.val(d,'bmed_sec_kWh_per_kg_base')*base_kg/24,
                kW_design=DR.val(d,'bmed_sec_design_kWh_per_kg_pair')*(hcl_mol*HCL/1000+base_kg)/24)

def ew(d, g):
    """Copper-equivalent sheet edges -> current by Faraday [CODATA2018, SCHLESINGER2011]."""
    R = {e['stream_id']: e['rate']['value'] for e in g['edges']}
    out = {}
    for n in range(1,10):
        m = R[f'IA-EW-MET-{n}'] + (R.get('IA-EW-SHEET',0) if n==9 else 0)
        I = EC.faraday_current_A(m, M['Cu'], 2, DR.val(d,'ew_current_efficiency_design'))
        out[f'EW_{n}'] = dict(I_A=I, P_kW=EC.dc_power_kW(I, DR.val(d,'ew_cell_voltage_V')))
    return out

def solve():
    d = DR.load(); g = json.load(open(os.path.join(ROOT,'flow_graph/plant_flow_graph.json')))
    la = leach_acid(d); bm = bmed(d, la['hcl_mol_d']); e = ew(d, g)
    return d, g, dict(leach=la, bmed=bm, ew=e)

def check():
    d, g, s = solve(); E = {x['stream_id']: x for x in g['edges']}; N = {x['unit_id']: x for x in g['nodes']}
    errs = []; mis = []
    mi, mo = s['leach']['closure']
    if abs(mi-mo) > 1e-6*max(mi,1): errs.append(f'LEACH acid stoichiometry does not close: {mi:.4f} vs {mo:.4f} kg/d')
    def cmp(what, graph, solved, ref):
        dev = (graph-solved)/solved if solved else 0
        mis.append((what, graph, solved, dev, ref))
    cmp('IA-ACID-01 HCl content, kg/d', E['IA-ACID-01']['rate']['value']*DR.val(d,'acid_conc_design_wt'), s['leach']['hcl_kg_d'], 'GREENWOOD, LUNAR_SOURCEBOOK')
    cmp('BMED_ACID kW (graph) vs published SEC at 2 M', N['BMED_ACID']['continuous_kw']['value'], s['bmed']['kW_published'], 'EDBM_WHEY_2021')
    for c,v in s['ew'].items():
        dc = next((x['rate']['value'] for x in g['edges'] if x['stream_id']==f'IA-DC-{c}'), None)
        if dc is not None: cmp(f'{c} DC kW (graph, 2.8 V AQS-ELEC-004) vs solver at ew_cell_voltage_V', dc, v['P_kW'], 'CODATA2018, SCHLESINGER2011')
    return errs, mis, s, d

if __name__ == '__main__':
    errs, mis, s, d = check()
    for m in mis: print(f'{m[0]}: graph {m[1]:.3f}, solved {m[2]:.3f}, deviation {m[3]*100:+.1f} %')
    if errs: raise SystemExit('; '.join(errs))

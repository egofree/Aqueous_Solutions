"""Balance solver (X-PAR-02). Per-unit transfer functions compute edge rates and unit duties
from drivers.json. This first set covers the metals core acid loop and the EW cells.
check(): mass/energy closure of the solved units (must pass) and misfit against the graph
(write_graph.py writes the solved values; MISFIT_TOL is the gate in test_param_misfit.py)."""
import json, os
from . import drivers as DR
from .constants import M, mw
from .sizing import electrochem as EC
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OX = {'Al2O3':{'Al':2,'O':3},'CaO':{'Ca':1,'O':1},'MgO':{'Mg':1,'O':1},'FeO':{'Fe':1,'O':1}}
HCL = mw({'H':1,'Cl':1}); NAOH = mw({'Na':1,'O':1,'H':1}); H2O = mw({'H':2,'O':1})
CHLORIDE = {'Al2O3':('AlCl3',{'Al':1,'Cl':3},2),'CaO':('CaCl2',{'Ca':1,'Cl':2},1),'MgO':('MgCl2',{'Mg':1,'Cl':2},1),'FeO':('FeCl2',{'Fe':1,'Cl':2},1)}
H2O_PER = {'Al2O3':3,'CaO':1,'MgO':1,'FeO':1}
MISFIT_TOL = 0.01   # 1 % relative misfit gate (AQS-PAR-001)
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

def evap(d, solute_kg_d, w_in, w_out, added_kg_d=0.0, unit=None):
    """Evaporative concentration of a BMED product from w_in to w_out by MVR.
    Mass: feed = solute/w_in, product = solute/w_out, water off = feed - product.
    HCl side: w_out must stay below the HCl-water azeotrope [PERRY9_HCL]; vapour is then water-rich.
    Power: in-house MVR design (X-MFG-30, flow_graph/param/evap_design.py: IAPWS-IF97 compression ratio, isentropic blower,
    recirculation pump, trim heat) when unit is given; else water off x specific MVR energy [VOGELBUSCH_MVR] (upper bound)."""
    assert w_out > w_in
    c = DR.val(d,'evap_cond_hcl_wt') if unit == 'EVAP_ACID' else 0.0   # HCl in the condensate (X-MFG-30 column, PERRY7_HCL_VLE)
    prod = (solute_kg_d+added_kg_d)/w_out
    feed = solute_kg_d/w_in if not c else prod*(w_out - c)/(w_in - c)   # condensate HCl recycles to BMED_ACID and returns in the feed
    water = feed + added_kg_d - prod
    r = dict(solute_kg_d=solute_kg_d, added_kg_d=added_kg_d, feed_kg_d=feed, product_kg_d=prod, water_kg_d=water, cond_hcl_wt=c,
             recycle_hcl_kg_d=water*c,
             kW=water/1000*DR.val(d,'mvr_kWh_per_t')/24, closure=(feed+added_kg_d, prod+water))
    if unit:
        from .evap_design import design
        r['design'] = design(d, r, unit); r['kW'] = r['design']['total_kW']
    return r

SIO2 = mw({'Si':1,'O':2})
def naoh_balance(d, g, hcl_mol):
    """NaOH demand and make-up. Precipitation: one NaOH per chloride [GREENWOOD]. Digest: SiO2 + 2 NaOH
    [GREENWOOD] on the dissolved cullet (IA-GLASS-03 less S08G, all as SiO2, bounding). BMED makes NaOH 1:1
    with the leach HCl. Make-up = demand - BMED, no credit for sodium returned in the silicate liquor (worst case)."""
    R = {x['stream_id']: x['rate']['value'] for x in g['edges']}
    ppt = hcl_mol*DR.val(d,'ppt_naoh_per_cl')
    sio2 = max(0.0, R['IA-GLASS-03'] - R['S08G'])*1000/SIO2
    dig = sio2*DR.val(d,'digest_naoh_per_sio2')
    mk = max(0.0, ppt + dig - hcl_mol)
    return dict(ppt_mol=ppt, digest_mol=dig, bmed_mol=hcl_mol, makeup_mol=mk, makeup_kg_d=mk*NAOH/1000/DR.val(d,'naoh_makeup_form'),
                ppt_kg_d=ppt*NAOH/1000, digest_kg_d=dig*NAOH/1000)

BASE_DEMAND = ('IA-BASE-01','IA-BASE-PPT')   # 20 wt% NaOH users (glass digest, hydroxide precipitation)

def ew(d, g):
    """Copper-equivalent sheet edges -> current by Faraday [CODATA2018, SCHLESINGER2011]."""
    R = {e['stream_id']: e['rate']['value'] for e in g['edges']}
    out = {}
    for n in range(1,10):
        m = R[f'IA-EW-MET-{n}'] + (R.get('IA-EW-SHEET',0) if n==9 else 0)
        I = EC.faraday_current_A(m, M['Cu'], 2, DR.val(d,'ew_current_efficiency_design'))
        out[f'EW_{n}'] = dict(I_A=I, P_kW=EC.dc_power_kW(I, DR.val(d,'ew_cell_voltage_V')),
                              P_bus_kW=EC.dc_power_kW(I, DR.val(d,'ew_cell_voltage_V')+DR.val(d,'ew_bus_drop_V')))
    dc = sum(v['P_bus_kW'] for v in out.values())
    out['RECT_EW'] = dict(I_A=sum(v['I_A'] for v in out.values()), P_dc_kW=dc,
                          P_ac_kW=dc/DR.val(d,'rect_efficiency'), loss_kW=dc/DR.val(d,'rect_efficiency')-dc)
    return out

def solve():
    d = DR.load(); g = json.load(open(os.path.join(ROOT,'flow_graph/plant_flow_graph.json')))
    la = leach_acid(d); bm = bmed(d, la['hcl_mol_d']); e = ew(d, g)
    R = {x['stream_id']: x['rate']['value'] for x in g['edges']}
    assert DR.val(d,'acid_conc_design_wt') < DR.val(d,'hcl_azeotrope_wt'), 'acid loop above the HCl azeotrope'
    ea = evap(d, R['IA-ACID-01']*DR.val(d,'acid_conc_design_wt'), DR.val(d,'bmed_product_wt_acid'), DR.val(d,'acid_conc_design_wt'), unit='EVAP_ACID')
    nb = naoh_balance(d, g, la['hcl_mol_d'])
    eb = evap(d, bm['base_kg_d'], DR.val(d,'bmed_product_wt_base'), DR.val(d,'base_conc_design_wt'), added_kg_d=nb['makeup_kg_d']*DR.val(d,'naoh_makeup_form'), unit='EVAP_BASE')
    import subprocess, sys as _s, os as _o
    root = _o.path.dirname(_o.path.dirname(_o.path.dirname(_o.path.abspath(__file__))))
    roof = json.loads(subprocess.run([_s.executable, 'docs-authority/_power_sizing.py'], cwd=root, capture_output=True, text=True, check=True).stdout)['roof']
    return d, g, dict(leach=la, bmed=bm, ew=e, evap_acid=ea, evap_base=eb, naoh=nb, roof=roof)

def check():
    d, g, s = solve(); E = {x['stream_id']: x for x in g['edges']}; N = {x['unit_id']: x for x in g['nodes']}
    errs = []; mis = []
    mi, mo = s['leach']['closure']
    if abs(mi-mo) > 1e-6*max(mi,1): errs.append(f'LEACH acid stoichiometry does not close: {mi:.4f} vs {mo:.4f} kg/d')
    for k in ('evap_acid','evap_base'):
        a, b = s[k]['closure']
        if abs(a-b) > 1e-6*max(a,1): errs.append(f'{k} mass does not close: {a:.4f} vs {b:.4f} kg/d')
    def cmp(what, graph, solved, ref):
        dev = (graph-solved)/solved if solved else 0
        mis.append((what, graph, solved, dev, ref))
    cmp('IA-ACID-01 HCl content, kg/d', E['IA-ACID-01']['rate']['value']*DR.val(d,'acid_conc_design_wt'), s['leach']['hcl_kg_d'], 'GREENWOOD, LUNAR_SOURCEBOOK')
    cmp('BMED_ACID kW vs published SEC at 2 M', N['BMED_ACID']['continuous_kw']['value'], s['bmed']['kW_published'], 'EDBM_WHEY_2021')
    w = DR.val(d,'base_conc_design_wt'); nb = s['naoh']
    cmp('IA-BASE-PPT NaOH, kg/d', E['IA-BASE-PPT']['rate']['value']*w, nb['ppt_kg_d'], 'GREENWOOD')
    cmp('IA-BASE-01 NaOH, kg/d', E['IA-BASE-01']['rate']['value']*w, nb['digest_kg_d'], 'GREENWOOD')
    if 'IA-NAOH-MU' in E: cmp('IA-NAOH-MU make-up, kg/d', E['IA-NAOH-MU']['rate']['value'], nb['makeup_kg_d'], 'NaOH balance')
    for k,u in (('evap_acid','EVAP_ACID'),('evap_base','EVAP_BASE')):
        if u in N:
            cmp(f'{u} kW', N[u]['continuous_kw']['value'], s[k]['kW'], 'X-MFG-30 in-house MVR design')
            cmp(f'{u} water off, kg/d', E[f'IA-{u}-COND']['rate']['value'], s[k]['water_kg_d'], 'PERRY9_HCL')
    for c,v in s['ew'].items():
        if c == 'RECT_EW':
            cmp('RECT_EW AC kW', N['RECT_EW']['continuous_kw']['value'], v['P_ac_kW'], 'USBM_CL_EW'); continue
        dc = next((x['rate']['value'] for x in g['edges'] if x['stream_id']==f'IA-DC-{c}'), None)
        if dc is not None: cmp(f'{c} DC kW (cell + bus drop)', dc, v['P_bus_kW'], 'CODATA2018, USBM_CL_EW')
    pv = N['PV_ARRAY']['params']; rf = s.get('roof')
    if rf:
        cmp('PV_ARRAY nameplate kWp vs roof-closed need', pv['nameplate_kw'], rf['pv_need_kWp'], 'NREL_PVWATTS, X-PAR-07')
        if pv['nameplate_kw'] > rf['pv_roof_kWp']: errs.append(f"PV {pv['nameplate_kw']} kWp exceeds roof capacity {rf['pv_roof_kWp']:.1f} kWp")
    return errs, mis, s, d

if __name__ == '__main__':
    errs, mis, s, d = check()
    for m in mis: print(f'{m[0]}: graph {m[1]:.3f}, solved {m[2]:.3f}, deviation {m[3]*100:+.1f} %')
    if errs: raise SystemExit('; '.join(errs))

def roof_close(d, P_base_kW):
    """X-PAR-07. Smallest footprint on the structural bay grid whose roof carries the PV that closes the energy balance,
    including the extension's own lighting, ventilation and envelope loads (sizing.roof). The base plate is kept; bays are
    added (single-storey extension). Returns the converged case."""
    from .sizing import roof as RF, power as PW
    v = lambda k: DR.val(d, k); bay = v('bay_mm'); bx0, by0 = int(v('base_bays_x')), int(v('base_bays_y'))
    A0 = bx0*by0*bay*bay/1e6; best = None
    for nx in range(bx0, bx0+40):
        for ny in range(by0, by0+40):
            W, D = nx*bay, ny*bay; A = W*D/1e6
            if best and A > best['footprint_m2']: continue
            ext = RF.extension_kW(A-A0, v('ext_lpd_W_m2'), v('ext_light_frac'), v('ext_Ra_L_s_m2'), v('ext_dT_mean_K'), v('ext_cop'), v('ext_sfp_W_per_L_s'), v('ext_U_roof'), v('ext_conditioned'), 2*(W+D)/1000*v('ext_wall_h_mm')/1000, v('ext_U_wall'))
            P = P_base_kW + ext['total_kW']
            need = PW.pv_kWp(P, v('night_hours'), v('storage_round_trip'), v('pv_yield_kWh_kWp_d')*v('pv_roof_yield_factor'), v('pv_system_derate'))*v('pv_oversize_factor')   # D75: 200 % of requirement
            arr, lay = RF.array_area_m2(W, D, v('ifc_perim_small_mm'), v('ifc_perim_large_mm'), v('ifc_axis_limit_mm'), v('ifc_array_max_mm'), v('ifc_path_mm'))
            have = RF.roof_kWp(arr, v('pv_module_eff'), v('pv_roof_gcr'))
            if have >= need and (best is None or A < best['footprint_m2'] or (A == best['footprint_m2'] and abs(nx*1.0/ny-4/3) < abs(best['bays_x']/best['bays_y']-4/3))):
                best = dict(bays_x=nx, bays_y=ny, W_mm=W, D_mm=D, footprint_m2=A, added_m2=A-A0, ext=ext, P_kW=P, pv_need_kWp=need,
                            array_m2=arr, layout=lay, pv_roof_kWp=have, load=RF.roof_load_kPa(v('roof_pv_dead_kPa'), v('roof_live_kPa'), v('roof_snow_kPa')))
    return best

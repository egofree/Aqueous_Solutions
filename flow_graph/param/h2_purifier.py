"""X-MFG-39 H2_PURIFIER beds (A-M-168): deoxo (2 H2 + O2 -> 2 H2O over Pd/Al2O3, bed from space velocity), chloride guard (promoted
alumina, change-out interval), and a two-bed TSA dryer (4A/13X sieve, working capacity x cycle load x margin), each bed duplicated so one is
in service while the other regenerates or is changed (redundancy rule). Water load = feed water (S49 composition) + deoxo water. Regeneration
heat = sieve + steel + water desorption (2.5 MJ/kg) per cycle, plus insulated losses (sizing/heat.py). Product spec ISO_14687 Grade D.
Run: python3 -m flow_graph.param.h2_purifier [--write]"""
import json, math, os, sys
from . import drivers as DR
from .sizing.heat import insulated_cylinder
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GP = os.path.join(ROOT, 'flow_graph/plant_flow_graph.json')
def design(d, g):
    v = lambda k: DR.val(d, k); E = {e['stream_id']: e for e in g['edges']}; S = E['IA-HDR-H2-02'] if 'IA-HDR-H2-02' in E else E['S49']   # R11 Rev AC regen: S49 was remapped (now CRYO_H2->FUEL_CELL); the purifier feed is HDR_H2 -> H2_DRYER
    h2 = S['rate']['value']*(S.get('composition') or {}).get('H2', 1.0); n = h2/2.016*1000            # mol/d
    Nm3_h = n*0.022414/24
    o2 = n*v('h2p_o2_ppmv')*1e-6; w_deoxo = 2*o2*18.015/1000                                 # kg/d
    V_deoxo = Nm3_h/v('h2p_deoxo_ghsv_h')*1000                                                 # L
    hcl = n*v('h2p_hcl_ppmv')*1e-6*36.461/1000; m_guard = hcl*v('h2p_guard_days')/v('h2p_guard_cap')
    w = S['rate']['value']*(S.get('composition') or {}).get('water', 0.0) + w_deoxo
    m_sieve = w*v('h2p_cycle_h')/24/v('h2p_sieve_work_cap')*v('h2p_bed_margin')
    V_sieve = m_sieve/0.7                                                                      # L at 0.7 kg/L bulk
    beds = {'deoxo': V_deoxo, 'guard': m_guard/0.8, 'TSA': V_sieve}
    geo = {}
    for b, V in beds.items():
        V = max(V, 0.05); D = 33.4 if V < 0.25 else 60.3; t = 3.38 if D < 40 else 3.91; idm = D - 2*t
        L = max(300, V/1000/(math.pi*(idm/1000)**2/4)*1000); geo[b] = dict(V_L=V, tube=f'DN{25 if D < 40 else 50} Sch 40 316L', L_mm=round(L), count=2)
    Lt = geo['TSA']['L_mm']/1000; steel = math.pi*(60.3 if 'DN50' in geo['TSA']['tube'] else 33.4)/1000*Lt*0.0039*8000
    cyc = 24/(2*v('h2p_cycle_h'))
    Q = (m_sieve*0.92*(v('h2p_regen_T_C') - 25) + steel*0.5*(v('h2p_regen_T_C') - 25))/1000 + w*v('h2p_cycle_h')/24*2500     # kJ per regeneration
    regen_W = Q*1000/86400*(24/v('h2p_cycle_h')); ins, loss = insulated_cylinder(v('h2p_regen_T_C'), 60.3, Lt)
    kw = (regen_W/0.7 + loss*0.5)/1000                                                        # loss while hot, half the time
    return dict(H2_kg_d=h2, Nm3_h=Nm3_h, O2_mol_d=o2, water_kg_d=w, HCl_kg_d=hcl, guard_kg=m_guard, sieve_kg=m_sieve, beds=geo, regen_W=regen_W, loss_W=loss,
                insulation_mm=ins, kW=round(kw, 4), D_mm=60, H_mm=max(g_['L_mm'] for g_ in geo.values()) + 300, T_C=v('h2p_regen_T_C'), wall_mm=3.91)
def write(g, r):
    N = {n['unit_id']: n for n in g['nodes']}; E = {e['stream_id']: e for e in g['edges']}
    U = 'H2_DRYER' if 'H2_DRYER' in N else 'H2_PURIFIER'   # R11 Rev AC regen: node renamed H2_PURIFIER -> H2_DRYER
    n = N[U]
    n['params']['design'] = json.loads(json.dumps(r, default=float)); n['continuous_kw'] = {'value': r['kW'], 'unit': 'kW', 'status': 'study', 'note': f"X-MFG-39 (A-M-168): TSA regeneration {r['regen_W']:.1f} W / 0.7 + half the insulated loss."}
    for sid in (f'SF-{U}', f'SQ-{U}'):
        if sid in E: E[sid]['rate']['value'] = r['kW']
    n['params']['size_mm'] = [600, 400, r['H_mm'] + 400]
    # X-PAR-15: feed water leaves on the TSA regeneration purge to the roof tank; product to Grade D (water taken as nil at 5 umol/mol)
    from .o2_close import _edge
    wf = 0.0
    if 'S49' in E: wf = E['S49']['rate']['value']*(E['S49'].get('composition') or {}).get('water', 0.0)   # R11 Rev AC regen: S49 has no composition now; the TSA water is set from the design value below when absent
    if 'IA-H2P-H2O' not in E:
        e = _edge('IA-H2P-H2O', U, 'VCD_TRAIN', 'L', ['mass'], 'TSA regeneration condensate', 0, 'kg/d', N[U].get('sector_id'), N['VCD_TRAIN'].get('sector_id'), {'water': 1.0}); g['edges'].append(e); E['IA-H2P-H2O'] = e
    E['IA-H2P-H2O']['rate']['value'] = round(wf, 6); E['IA-H2P-H2O']['rate']['note'] = 'X-PAR-15: feed water (S49 composition) removed by the TSA, condensed from the regeneration purge (A-M-168).'
    E['IA-H2P-H2O']['to_unit_id'] = 'VCD_TRAIN'
    if 'S49P' in E:   # R11 Rev AC regen: the S49P/S52 fuel-cell product edges left the graph with the H2 reroute; this rebookkeeping applies only where they exist
        new = round(S49['rate']['value'] - wf, 6); dlt = E['S49P']['rate']['value'] - new
        E['S52']['rate']['value'] = round(E['S52']['rate']['value'] - dlt, 6)
        E['S52']['composition'] = {'water': 1.0}                                       # fuel-cell product water; was mislabelled H2 0.98 (found by X-ELS-09/X-THM-02)          # fuel-cell water no longer carries the feed water
        E['S49P']['rate']['value'] = new; E['S49P']['composition'] = {'H2': 1.0}
        E['S49P']['rate']['note'] = 'X-PAR-15: S49 less the dried water; ISO_14687 Grade D (water and O2 <= 5 umol/mol).'
    open(GP, 'w').write(json.dumps(g, indent=2))
def write_doc(r):
    md = ['# H2_PURIFIER beds', '', 'Document number: AQS-DUTY-066', 'Revision: A', 'Date: 2026-10-15', 'Authority: AQS-PLAN-007 X-MFG-39. Generated by `flow_graph/param/h2_purifier.py`. Study. A-M-168.', '',
          f"Feed {r['H2_kg_d']:.2f} kg/d H2 ({r['Nm3_h']:.2f} Nm3/h). O2 {r['O2_mol_d']:.2f} mol/d, water {r['water_kg_d']*1000:.1f} g/d, HCl {r['HCl_kg_d']*1000:.3f} g/d. Product to ISO_14687 Grade D (water and O2 at or below 5 umol/mol, halogenates 0.05 umol/mol).", '',
          '| Bed | Volume, L | Tube | Length, mm | Count |', '|---|---|---|---|---|']
    md += [f"| {b} | {x['V_L']:.3f} | {x['tube']} | {x['L_mm']} | {x['count']} |" for b, x in r['beds'].items()]
    md += ['', f"Guard charge {r['guard_kg']*1000:.0f} g; sieve {r['sieve_kg']*1000:.0f} g per TSA bed. Regeneration {r['regen_W']:.1f} W average at {r['T_C']} C, insulation {r['insulation_mm']} mm (loss {r['loss_W']:.0f} W while hot); electric load {r['kW']*1000:.0f} W. Every bed is duplicated (one on line). All capacities and the space velocity are assumptions (A-M-168) until the bed tests.",
           '', 'X-PAR-15: the feed water now leaves on IA-H2P-H2O to VCD_TRAIN (with the fuel-cell water S52, which falls by the same mass) and S49P is dry H2 to Grade D. Deoxo water is formed from O2 that the graph does not yet carry on S49 (1000 ppm v assumed here); it is inside the TSA load above.']
    open(os.path.join(ROOT, 'docs-authority/sizing/H2_PURIFIER_BEDS.md'), 'w').write('\n'.join(md) + '\n')
def main():
    d = DR.load(); g = json.load(open(GP)); r = design(d, g); print(json.dumps(r, default=float)[:600])
    if '--write' in sys.argv: write(g, r); write_doc(r)
if __name__ == '__main__': main()

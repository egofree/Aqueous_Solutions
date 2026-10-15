"""X-MFG-33 in-house CRYO_ASU separation train (AQS-DUTY-069, A-M-175). Sized from the duty on the graph, not from an air plant.
The cold box has no air intake (IA-AIR-IN 0): its feed is the scrubbed flue from NOX_SCRUB, nitrogen with a little O2, and CO2.
Nitrogen already meets its 99 % product purity once the CO2 is out, so no cryogenic column is needed. The design is:
  1. 13X temperature-swing beds take out the CO2 (three beds, one adsorbing, one regenerating at 204 C [NASA_CDRA2015], one standby).
     Sorbent per bed = CO2 per half-cycle / working capacity; regeneration heat = (sorbent cp + steel cp) dT + n dH_ads, plus losses.
  2. The desorbed CO2 goes to an intercooled compressor, staged so the discharge stays within 150 C [API618], to the 20 bar store and is condensed at -20 C [NIST_WEBBOOK].
  3. The Ar return from WAFER_FAB passes a heated getter; He, Ne, Kr and Xe are closed inventories that pass through with no separation duty.
The EXPANDER is kept (Q-010 closed by the owner, redundancy rule): a reverse-Brayton N2 loop sized as a full working backup for the CO2 condenser chiller. It is idle in normal operation (loop streams 0) and its rated duty is in params.design (A-M-186).
Run: python3 -m flow_graph.param.cold_box [--write]"""
import json, math, os, sys
from . import drivers as DR
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GP = os.path.join(ROOT, 'flow_graph/plant_flow_graph.json')
def design(d, g):
    v = lambda k: DR.val(d, k); E = {e['stream_id']: e for e in g['edges']}; r = lambda k: float(E[k]['rate']['value'] or 0)
    co2 = r('IA-NOX-CO2'); n2 = r('IA-NOX-N2'); n = co2/44.01                        # kmol/d CO2
    x_co2 = n/(n + n2/28.013)
    per_cycle = n*v('cb_cycle_h')/24*1000; m_sorb = per_cycle/v('cb_13x_CO2_mol_kg')   # mol, kg per bed
    dT = v('cb_regen_C') - 25; cyc = 24/v('cb_cycle_h')
    q_cyc = m_sorb*(1 + v('cb_steel_to_sorbent')*0.50/v('cb_cp_sorbent_kJ_kgK'))*v('cb_cp_sorbent_kJ_kgK')*dT + per_cycle*v('cb_dH_ads_kJ_mol')   # kJ; steel cp 0.50 kJ/kg K
    P_regen = q_cyc*cyc/86400*(1 + v('cb_regen_loss_frac'))
    Q = (n + n2/28.013)*1000/86400*8.314*308.15/101325                                 # m3/s feed at 35 C
    P_blow = Q*v('cb_bed_dP_kPa')*1000/0.5/1000
    k = 1.29; x = (k - 1)/k; ns = 1
    while 308.15*(1 + ((v('cb_co2_store_bar')/1.0)**(x/ns) - 1)/0.65) - 273.15 > v('cb_T_out_max_C'): ns += 1   # API618 150 C
    rr = (v('cb_co2_store_bar')/1.0)**(1/ns); w = ns/x*8.314/0.04401*308.15*(rr**x - 1)/0.65   # J/kg
    T_st = 308.15*(1 + (rr**x - 1)/0.65) - 273.15
    P_comp = co2/86400*w/0.9/1000
    q_cond = 0.85*55 + v('cb_co2_latent_kJ_kg'); P_chill = co2/86400*q_cond/v('cb_chiller_COP')
    P_get = v('cb_getter_W')/1000
    rho_b = 650.0; Vb = m_sorb/rho_b; D = (4*Vb/(math.pi*3))**(1/3)                   # bed L/D 3, 13X bulk 650 kg/m3 (A-M-175)
    k2 = 1.4; xe = (k2 - 1)/k2; Tin = v('exp_T_in_K'); T_out = Tin*(1 - v('exp_eta_s')*(1 - v('exp_pr')**-xe))      # expander outlet, PERRY9 sec. 2 cp N2 1.04
    q_cold = co2/86400*q_cond; dq = 1.04*(248.15 - T_out); m_loop = q_cold/dq                                  # kg/s, warms to -25 C at the condenser
    w_c = 1.04*Tin*(v('exp_pr')**xe - 1)/v('exp_eta_comp'); w_e = 1.04*(Tin - T_out); P_loop = m_loop*(w_c - w_e)
    exp_bk = dict(cold_kW=q_cold, T_out_C=T_out - 273.15, loop_kg_d=m_loop*86400, shaft_kW=m_loop*w_e, net_kW=P_loop, COP=q_cold/P_loop, chiller_kW=q_cold/v('cb_chiller_COP'))
    tot = P_regen + P_blow + P_comp + P_chill + P_get
    return dict(feed_N2_kg_d=n2, feed_CO2_kg_d=co2, x_CO2=x_co2, CO2_mol_per_cycle=per_cycle, sorbent_kg_per_bed=m_sorb, beds=3, bed_D_mm=D*1000, bed_L_mm=3*D*1000,
                regen_kW=P_regen, blower_kW=P_blow, co2_comp_kW=P_comp, co2_chill_kW=P_chill, getter_kW=P_get, total_kW=tot, comp_stages=ns, comp_ratio_per_stage=rr, comp_T_out_C=T_st, expander_backup=exp_bk)
def write(g, r):
    N = {n['unit_id']: n for n in g['nodes']}; E = {e['stream_id']: e for e in g['edges']}
    n = N['CRYO_ASU']; TAG = 'X-MFG-33 (A-M-175, AQS-DUTY-069)'
    n['continuous_kw'] = {'value': round(r['total_kW'], 4), 'unit': 'kW', 'status': 'study', 'note': f"{TAG}: 13X TSA regeneration {r['regen_kW']:.2f} + blower {r['blower_kW']:.3f} + CO2 compressor {r['co2_comp_kW']:.3f} + condenser chiller {r['co2_chill_kW']:.3f} + Ar getter {r['getter_kW']:.2f} kW; no cryogenic column (no air intake)."}
    n['internals'] = '3 x 13X TSA beds, CO2 two-stage compressor and condenser, heated Ar getter; noble-gas inventories pass through'
    n['params']['internals'] = n['internals']; n['params']['design'] = dict(json.loads(json.dumps(r, default=float)), H_mm=round(r['bed_L_mm']), D_mm=round(r['bed_D_mm']))
    for sid in ('SF-CRYO_ASU', 'SQ-CRYO_ASU'): E[sid]['rate']['value'] = round(r['total_kW'], 4)
    for sid in ('IA-EXP-IN', 'IA-EXP-OUT'): E[sid]['rate']['value'] = 0.0; E[sid]['rate']['note'] = f'{TAG}: no refrigeration duty; loop idle in normal operation; standby backup (Q-010 closed)'
    x = N['EXPANDER']; x['continuous_kw']['value'] = 0.0; x['continuous_kw']['note'] = f'{TAG}: idle, no duty; retirement is Q-010'
    for sid in ('SF-EXPANDER', 'SQ-EXPANDER'): E[sid]['rate']['value'] = 0.0
    open(GP, 'w').write(json.dumps(g, indent=2))
    md = ['# CRYO_ASU separation train', '', 'Document number: AQS-DUTY-069', 'Revision: C', 'Date: 2026-10-16', 'Authority: AQS-PLAN-007 X-MFG-33 (rev C: EXPANDER kept as chiller backup, Q-010; rev B: CO2 compressor staged to the API618 discharge limit, found by AQS-SAF-004). Generated by `flow_graph/param/cold_box.py`. Study. A-M-175.', '',
          f"Feed (graph): N2 {r['feed_N2_kg_d']:.2f} kg/d (99.92 % N2, rest O2) and CO2 {r['feed_CO2_kg_d']:.2f} kg/d from NOX_SCRUB; no intake air (IA-AIR-IN 0). CO2 {r['x_CO2']*100:.1f} mol %. Nitrogen meets its 99 % product purity once the CO2 is removed, so the train has no cryogenic column.", '',
          '| Item | Design | kW |', '|---|---|---|',
          f"| CO2 TSA | 3 x 13X beds (1 adsorbing, 1 regenerating at 204 C per NASA_CDRA2015, 1 standby), {r['sorbent_kg_per_bed']:.0f} kg each at 1.5 mol/kg working capacity, {DR.val(DR.load(),'cb_cycle_h'):.0f} h half-cycle; DN{round(r['bed_D_mm'], -1):.0f} x {r['bed_L_mm']:.0f} mm 316L | {r['regen_kW']:.2f} |",
          f"| Feed blower | 10 kPa rise | {r['blower_kW']:.3f} |",
          f"| CO2 compressor | {r['comp_stages']} stages, ratio {r['comp_ratio_per_stage']:.2f}, intercooled, to 20 bar; discharge {r['comp_T_out_C']:.0f} C within the API618 150 C limit | {r['co2_comp_kW']:.3f} |",
          f"| CO2 condenser | -20 C, latent 282 kJ/kg (NIST_WEBBOOK), chiller COP 2.5 | {r['co2_chill_kW']:.3f} |",
          f"| Ar getter | heated getter on the WAFER_FAB return | {r['getter_kW']:.2f} |",
          f"| Total | | {r['total_kW']:.2f} |", '',
          'He, Ne, Kr and Xe are closed inventories that return from their stores and pass through; no separation duty. '+f"The EXPANDER is kept as the diverse backup for the condenser chiller (owner decision Q-010, redundancy rule): N2 reverse-Brayton loop, pressure ratio 5, outlet {r['expander_backup']['T_out_C']:.0f} C, {r['expander_backup']['loop_kg_d']:.0f} kg/d N2 for {r['expander_backup']['cold_kW']:.3f} kW cold at -25 C, {r['expander_backup']['net_kW']:.3f} kW net (COP {r['expander_backup']['COP']:.2f} against the chiller's 2.5). It is idle in normal operation; a chiller failure starts it. A-M-186.",
          '', 'The regeneration heat is electric in this revision. Taking it from the Q2 ladder (200-250 C) is the first saving to study. Sorbent capacity, heat of adsorption and the chiller COP are assumptions until the bed breakthrough test (A-M-175).']
    open(os.path.join(ROOT, 'docs-authority/sizing/COLD_BOX.md'), 'w').write('\n'.join(md) + '\n')
def main():
    d = DR.load(); g = json.load(open(GP)); r = design(d, g); print(json.dumps(r, default=float))
    if '--write' in sys.argv: write(g, r)
if __name__ == '__main__': main()

"""X-MFG-31 / X-SAF-04: pressurised nodes taken out of the atmospheric (API 2000) class and given API 520 gas relief cases (A-M-156).
MEOH_SYNTH loop at 50 bar (params.synthesis); CRYO_H2 and CRYO_O2 banks at 200 bar (o2_close storage); CRYO_CO2 liquid store at 20 bar, -20 C (X-MFG-33, found by AQS-SAF-004). Design pressure = operating x
press_design_margin; set = design; relieving P1 = 1.10 x set + atmosphere (API520 10 % accumulation, non-fire). Relieving load = the
blocked-outlet case: the largest inflow rate (electrolyser streams over its PV window, others daily-average). Fire case for the banks is per
cylinder to CGA_S1_1 and stays with X-SAF-04. Run before write_graph relief, which computes the orifice."""
import json, os
from . import drivers as DR, site as SITE
_D = DR.load()
from .refs import cite
GP = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'flow_graph/plant_flow_graph.json')
GAS = {'MEOH_SYNTH': dict(P_bar=_D['GAS.headers.methanol_synth_loop_P_bar']['value'], T_K=_D['GAS.headers.methanol_synth_loop_T_K']['value'], M=12.51, k=1.38, Z=1.0, fluid='3 H2 : 1 CO2 loop gas'),
       'CRYO_H2': dict(P_bar=_D['CRYO.cold-box-asu-recovery-train.CRYO_H2_store_P_bar']['value'], T_K=_D['CRYO.cold-box-asu-recovery-train.CRYO_H2_store_T_K']['value'], M=2.016, k=1.41, Z=1.13, fluid='hydrogen'),
       'HTC': dict(P_bar=_D['DIGESTER.metals-leach-train.htc_header_P_bar']['value'], T_K=_D['DIGESTER.metals-leach-train.htc_header_T_K']['value'], M=18.015, k=1.33, Z=0.95, fluid='steam from the heater at full power', W_heater=True),
       'MEAM': dict(P_bar=_D['GAS.headers.meam_header_P_bar']['value'], T_K=_D['GAS.headers.meam_header_T_K']['value'], M=23.4, k=1.25, Z=1.0, fluid='MeOH/NH3 vapour'),
       'CRYO_CO2': dict(P_bar=_D['CRYO.cold-box-asu-recovery-train.CRYO_CO2_store_P_bar']['value'], T_K=_D['CRYO.cold-box-asu-recovery-train.CRYO_CO2_store_T_K']['value'], M=44.01, k=1.29, Z=0.85, fluid='CO2 vapour off the liquid store at -20 C (AQS-DUTY-069, NIST_WEBBOOK)'),
       'CRYO_O2': dict(P_bar=_D['CRYO.cold-box-asu-recovery-train.CRYO_O2_store_P_bar']['value'], T_K=_D['CRYO.cold-box-asu-recovery-train.CRYO_O2_store_T_K']['value'], M=31.999, k=1.40, Z=0.97, fluid='oxygen'),
       'H2O_ELYZ': dict(P_bar=_D['WTR.potable-upw-train.H2O_ELYZ_suction_P_bar']['value'], T_K=_D['WTR.potable-upw-train.H2O_ELYZ_suction_T_K']['value'], M=2.016, k=1.41, Z=1.0, fluid='hydrogen side of the PEM stack at the compressor suction (h2c_P1_bar 10 bar a); O2 side on its own valve at the same set, A-M-196', W_gas_out=True),
       'HCL_BURNER': dict(P_bar=0.5, T_K=1273.15, M=36.46, k=1.30, Z=1.0, fluid='HCl flame products; deflagration case is a rupture disc to NFPA 68 at detail, A-M-196')}
def main():
    d = DR.load(); m = DR.val(d, 'press_design_margin'); win = DR.val(d, 'ely_window_h'); g = json.load(open(GP)); N = {n['unit_id']: n for n in g['nodes']}
    for u, c in GAS.items():
        ins = [e for e in g['edges'] if e['to_unit_id'] == u and e['presence'] == 'present' and (e['rate'] or {}).get('unit') == 'kg/d']
        W = (sum((e['rate']['value'] or 0) for e in g['edges'] if e['from_unit_id'] == u and e['presence'] == 'present' and e.get('phase') == 'G' and 'H2' in e['stream_id'])/win) if c.get('W_gas_out') else ((N[u].get('continuous_kw') or {}).get('value') or 0)*3600/1940.0 if c.get('W_heater') else sum((e['rate']['value'] or 0)/(win if e['from_unit_id'] == 'H2O_ELYZ' else 24) for e in ins)
        des = c['P_bar']*m*100; P1 = 1.10*des + SITE.p_process_kPa()
        p = N[u]['params']; p['design_kPa'] = round(des, 1); p.setdefault('relief_mm', 3.3)
        p['relief_basis'] = {'case': f"blocked outlet at full inflow {W:.3f} kg/h ({c['fluid']}); operating {c['P_bar']:.0f} bar, design {des/100:.1f} bar g",
                             'P1_kPa_abs': round(P1, 1), 'T_K': c['T_K'], 'M_kg_kmol': c['M'], 'k': c['k'], 'Z': c['Z'], 'W_kg_h': round(W, 4),
                             'method': f"API 520 Part I gas critical flow ({cite('API520')}); pressure class A-M-156; fire case per cylinder {cite('CGA_S1_1')} under X-SAF-04"}
    N['EVAP_ACID_VS']['params'].setdefault('relief_mm', 3.3)   # HAZOP HZ: atmospheric scrubber gets its API 2000 vent case in write_graph vent
    open(GP, 'w').write(json.dumps(g, indent=2)); print('pressurised nodes', list(GAS))
if __name__ == '__main__': main()

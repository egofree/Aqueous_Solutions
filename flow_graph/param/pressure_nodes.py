"""X-MFG-31 / X-SAF-04: pressurised nodes taken out of the atmospheric (API 2000) class and given API 520 gas relief cases (A-M-156).
MEOH_SYNTH loop at 50 bar (params.synthesis); CRYO_H2 and CRYO_O2 banks at 200 bar (o2_close storage). Design pressure = operating x
press_design_margin; set = design; relieving P1 = 1.10 x set + atmosphere (API520 10 % accumulation, non-fire). Relieving load = the
blocked-outlet case: the largest inflow rate (electrolyser streams over its PV window, others daily-average). Fire case for the banks is per
cylinder to CGA_S1_1 and stays with X-SAF-04. Run before write_graph relief, which computes the orifice."""
import json, os
from . import drivers as DR
from .refs import cite
GP = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'flow_graph/plant_flow_graph.json')
GAS = {'MEOH_SYNTH': dict(P_bar=50.0, T_K=523.15, M=12.51, k=1.38, Z=1.0, fluid='3 H2 : 1 CO2 loop gas'),
       'CRYO_H2': dict(P_bar=200.0, T_K=313.15, M=2.016, k=1.41, Z=1.13, fluid='hydrogen'),
       'HTC': dict(P_bar=15.55, T_K=473.15, M=18.015, k=1.33, Z=0.95, fluid='steam from the heater at full power', W_heater=True),
       'CRYO_O2': dict(P_bar=200.0, T_K=313.15, M=31.999, k=1.40, Z=0.97, fluid='oxygen')}
def main():
    d = DR.load(); m = DR.val(d, 'press_design_margin'); win = DR.val(d, 'ely_window_h'); g = json.load(open(GP)); N = {n['unit_id']: n for n in g['nodes']}
    for u, c in GAS.items():
        ins = [e for e in g['edges'] if e['to_unit_id'] == u and e['presence'] == 'present' and (e['rate'] or {}).get('unit') == 'kg/d']
        W = ((N[u].get('continuous_kw') or {}).get('value') or 0)*3600/1940.0 if c.get('W_heater') else sum((e['rate']['value'] or 0)/(win if e['from_unit_id'] == 'H2O_ELYZ' else 24) for e in ins)
        des = c['P_bar']*m*100; P1 = 1.10*des + 101.325
        p = N[u]['params']; p['design_kPa'] = round(des, 1)
        p['relief_basis'] = {'case': f"blocked outlet at full inflow {W:.3f} kg/h ({c['fluid']}); operating {c['P_bar']:.0f} bar, design {des/100:.1f} bar g",
                             'P1_kPa_abs': round(P1, 1), 'T_K': c['T_K'], 'M_kg_kmol': c['M'], 'k': c['k'], 'Z': c['Z'], 'W_kg_h': round(W, 4),
                             'method': f"API 520 Part I gas critical flow ({cite('API520')}); pressure class A-M-156; fire case per cylinder {cite('CGA_S1_1')} under X-SAF-04"}
    open(GP, 'w').write(json.dumps(g, indent=2)); print('pressurised nodes', list(GAS))
if __name__ == '__main__': main()

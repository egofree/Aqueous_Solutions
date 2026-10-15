"""X-PAR-02 per-unit transfer functions, storage and farm loops (AQS-PAR-003 sec. 5). Called from balance.physics().
ZNBR2 purge (S69/S69B): sized so the headspace stays at or below 25 % of the H2 LFL (1.0 vol %, NFPA 69 / NFPA 855). H2 from charge-side HER at
  0.66 % of charge current (5.5e-2 mL/h/cm2 at 20 mA/cm2, ZBFB_REVIEW2023) plus open-circuit Zn corrosion 3.2e-3 mL/h/cm2 over the electrode
  area for the non-charging hours; charge Ah from the AQS-ELEC-007 store_in_kWh at 1.82 V (SAND2000-0893); recombination with Br2 not credited.
HYDRO_SET: role from need. AQS-ELEC-007 sizes ZNBR2 for the whole night deficit and the H2/fuel-cell bank for multi-day autonomy; no storage gap
  remains for the 7 kWh/cycle hydro set (0.2 % of ZNBR2). Cycle set to zero (unit retained as roof/catch-tank water inventory only); A-M-135.
NFT: 1 L/min per gully (COOPER1996), gullies at 200 mm pitch across the 1 m unit width (80 mm gully, CROPKING_NFT).
MISTER: high-pressure aeroponics, 6 nozzles/m2 at 0.057 L/min, 4 s on / 4 min off (HPA_PRACTICE, JAE2022_AERO); A-M-136."""
import json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = 96485.0; VZB = 1.82; F_HER = 0.055/(0.020/(2*F)*22414*3600); OC = 3.2e-3; J = 20.0; LFL25 = 0.01; RHO_AIR = 1.18
CHG_H = 6.0; GULLY_PITCH = 0.2; GULLY_LPM = 1.0
NOZ_M2 = 6; NOZ_LPM = 0.015*3.785; T_ON = 4.0; T_OFF = 240.0
def _ps():
    return json.loads(subprocess.run([sys.executable, 'docs-authority/_power_sizing.py'], cwd=ROOT, capture_output=True, text=True, check=True).stdout)['bounding']
def tf(g, ps=None):
    N = {n['unit_id']: n for n in g['nodes']}; E = {e['stream_id']: e for e in g['edges']}
    def put(k, x, why):
        E[k]['rate']['value'] = round(x, 6); E[k]['rate']['note'] = (E[k]['rate'].get('note') or '').split(' | X-PAR-02 TF')[0] + f' | X-PAR-02 TF: {why} (AQS-PAR-003).'
    ps = ps or _ps(); kwh = float(ps['store_in_kWh'])
    ah = kwh*1000/VZB; mol_e = ah*3600/F; h2_chg = mol_e/2*F_HER*22.414e-3            # m3/d
    area = ah/CHG_H*1000/J                                                               # cm2 (cell-summed)
    h2_oc = OC*area*(24 - CHG_H)/1e6; h2 = h2_chg + h2_oc; q = h2/LFL25                 # m3/d purge
    put('S69', q*RHO_AIR, f'purge {q/24:.1f} m3/h holds H2 at 25 % LFL: HER {h2_chg:.2f} + open-circuit {h2_oc:.2f} m3/d H2 on {kwh:.0f} kWh/d charge (ZBFB_REVIEW2023, NFPA 69)')
    put('S69B', E['S69']['rate']['value'], 'regen return = purge (closed loop, H2 recombined with Br2 in the regen bed)')
    for t in (N['ZNBR2']['params'].get('balance_rev_l') or {}).get('terms', []):
        if t['label'].startswith('purge air'): t['value'] = round(q*RHO_AIR, 4); t['basis'] = 'X-PAR-02 TF ess_tf.py'
    N['ZNBR2']['params']['purge_basis'] = {'H2_m3_d': round(h2, 3), 'purge_m3_h': round(q/24, 2), 'HER_fraction': round(F_HER, 5), 'electrode_area_m2': round(area/1e4, 1)}
    for k in ('IA-ESS-HYDRO-CHG', 'IA-ESS-HYDRO-DIS', 'S22', 'S23', 'IA-ESS-HYDRO-ELEC'):
        put(k, 0.0, 'no storage gap after ZNBR2 (night) and the H2/fuel-cell bank (multi-day): hydro cycle not needed (A-M-135)')
    N['HYDRO_SET']['params'].update(role_from_need='none: ZNBR2 covers the night deficit, H2 bank the multi-day case (AQS-ELEC-007); 7 kWh/cycle = 0.2 % of ZNBR2. Recommend removal of turbine-pump; tanks stay as water inventory.')
    L, W = [x/1000 for x in N['NFT']['params']['size_mm'][:2]]; n = int(W/GULLY_PITCH); qn = n*GULLY_LPM*1440
    put('IA-NFT-IN', qn, f'{n} gullies x {GULLY_LPM} L/min (COOPER1996) over {L:.0f} m'); put('IA-NFT-OUT', qn, 'film return = supply')
    A = (lambda d: d[0]*d[1]/1e6)(N['MISTER']['params']['size_mm']); qm = A*NOZ_M2*NOZ_LPM*1440*T_ON/(T_ON + T_OFF)
    put('IA-MIST-IN', qm, f'{A:.0f} m2 x {NOZ_M2} nozzles/m2 x {NOZ_LPM} L/min, {T_ON:.0f} s on / {T_OFF/60:.0f} min off (HPA_PRACTICE, JAE2022_AERO)'); put('IA-MIST-OUT', qm, 'chamber drain return = supply')
    return dict(mist=qm, purge_m3_h=q/24, h2=h2, nft=qn)

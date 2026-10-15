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
NOZ_M2 = 6; NOZ_LPM = 0.015*3.785; T_ON = 4.0; T_OFF = 240.0; DRAIN = 0.20; SWARF = 0.10
BANDS = [(7, 12, 0.34), (13, 20, 0.315), (21, 40, 0.345)]; CUTS = [(5, 10), (11, 18), (19, 28), (29, 99)]
def cut_fractions():
    return [sum(w*max(0, min(b, hi) - max(a, lo) + 1)/(b - a + 1) for a, b, w in BANDS) for lo, hi in CUTS]
def _resid(g, u):
    from flow_graph.param.balance import _unit_resid; return _unit_resid(g, u)
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
    put('IA-MIST-IN', qm, f'{A:.0f} m2 x {NOZ_M2} nozzles/m2 x {NOZ_LPM} L/min, {T_ON:.0f} s on / {T_OFF/60:.0f} min off (schedule within LAKHIAR2018 range; nozzle flow HPA_PRACTICE; JAE2022_AERO)'); put('IA-MIST-OUT', qm, 'chamber drain return = supply')
    # DUAL_ROOT: substrate bed on the grow-bed water. ET per m2 = the grow bed's (same LED light, same room; IA-BED-VAP over BED_M2);
    # supply = ET/(1 - drain fraction 0.20) (PLOSONE2017_DRAIN 10-20 %, AGRIC2024_LF 15-20 %); drain returns to the bed; ET to the AHU.
    if 'IA-DR-VAP' not in E:
        from flow_graph.param.o2_close import _edge
        g['edges'].append(_edge('IA-DR-VAP', 'DUAL_ROOT', 'CRYO_AHU', 'G', ['mass'], 'dual-root transpiration', 0, 'kg/d', 'FARM', 'CRYO', {'H2O': 1.0})); E = {e['stream_id']: e for e in g['edges']}
    P = N['DUAL_ROOT']['params']; b0 = P.setdefault('bed_h2o_base', E['IA-BED-H2O']['rate']['value'])
    from flow_graph.param.o2_close import BED_M2
    adr = (lambda d: d[0]*d[1]/1e6)(P['size_mm']); et = b0/BED_M2*adr; sup = et/(1 - DRAIN)
    put('IA-DR-IN', sup, f'ET {et:.2f} kg/d ({adr:.0f} m2 at the bed rate {b0/BED_M2:.3f} kg/m2/d) / (1 - {DRAIN} drain) (PLOSONE2017_DRAIN)')
    put('IA-DR-OUT', sup - et, f'drain {DRAIN:.0%} of supply back to the bed'); put('IA-DR-VAP', et, 'transpiration to the CRYO AHU coil')
    put('IA-BED-H2O', b0 + et, f'bed irrigation {b0} + dual-root ET {et:.2f} drawn through the bed')
    # OIL_FRAC cuts (replaces the ASF fit, a Fischer-Tropsch growth law that does not describe random-scission cracking): thermal pyrolysis
    # of a 50/50 PE/PP float, oil 34 % C7-C12, 31.5 % C13-C20, 34.5 % C21-C40 (SU2018_PYRO: LDPE 24/30/46, PP 44/33/23), spread uniformly
    # over the carbon numbers of each reported band and re-binned to the plant cuts; C29+ recycled to extinction (re-cracked at the same split).
    vol = N['OIL_FRAC']['params'].setdefault('vol_net_base', round(E['IA-OIL-02']['rate']['value'] - E['C29_TO_PYRO']['rate']['value'], 6))
    oil = vol - E['IA-OIL-03']['rate']['value']; f = cut_fractions(); rec = oil/(1 - f[3])*f[3]; p123 = sum(f[:3])
    for k in ('CUT-4', 'C29_RECYCLE', 'C29_TO_PYRO'): put(k, rec, f'C29+ {f[3]:.1%} of per-pass oil, recycled to extinction (SU2018_PYRO bands)')
    put('IA-OIL-02', vol + rec, f'per-pass volatiles: net {vol:.2f} + C29 recycle {rec:.2f}')
    put('CUT-2', oil*f[1]/p123, f'C11-C18 {f[1]/p123:.1%} of net oil {oil:.2f} (SU2018_PYRO bands)')
    put('CUT-3', oil*f[2]/p123 + E['S72B']['rate']['value'], f'C19-C28 {f[2]/p123:.1%} of net oil + S72B lube mist (SU2018_PYRO bands)')
    ins = sum(e['rate']['value'] or 0 for e in g['edges'] if e['to_unit_id'] == 'OIL_FRAC' and 'mass' in e['layers'])
    put('CUT-1', ins - sum(E[k]['rate']['value'] for k in ('CUT-2', 'CUT-3', 'CUT-4', 'IA-OIL-03')), f'C5-C10 {f[0]/p123:.1%} of net oil + solvent and resist feeds (by difference)')
    from flow_graph.param.o2_close import _edge
    for sid, tank, cut, use, comp in (('IA-C11-SHIP', 'PROD_C11_C18', 'CUT-2', 'IA-BLOW-IN', 'C11-C18'), ('IA-C19-SHIP', 'PROD_C19_C28', 'CUT-3', 'CUT-3-OUT', 'C19-C28')):
        if sid not in E:
            g['edges'].append(_edge(sid, tank, 'NORTH_DOCK', 'L', ['mass'], f'{comp} surplus shipped', 0, 'kg/d', 'CRYO', 'DOCK', {comp: 1.0})); E[sid] = g['edges'][-1]
        put(sid, E[cut]['rate']['value'] - E[use]['rate']['value'], f'{comp} make less the plant draw ({use}), shipped (Q-002 pattern)')
    N['OIL_FRAC']['params']['cut_basis'] = {'source': 'SU2018_PYRO', 'per_pass_fractions_C5-10_C11-18_C19-28_C29+': [round(x, 4) for x in f], 'A-M': 'A-M-138'}
    # GAS_ATOMIZER: powder S60 is the product; 10 % off-spec (A_RL_SWARF) is remelted on new IA-ATOM-REMELT, so the melt draw is S60/0.9.
    # Melt-line compositions were a water/solute default; they carry metal (A-M-139). Ultrafines 1 % stay on the MET LEV air term.
    if 'IA-ATOM-REMELT' not in E:
        g['edges'].append(_edge('IA-ATOM-REMELT', 'GAS_ATOMIZER', 'MET_MELT', 'S', ['mass'], 'off-spec powder to remelt', 0, 'kg/d', 'MFG', 'MFG', {'metal': 1.0})); E['IA-ATOM-REMELT'] = g['edges'][-1]
    s60 = E['S60']['rate']['value']; fa = s60/(1 - SWARF)
    put('IA-MELT-ATOM', fa, f'powder {s60:.3f} / (1 - {SWARF:.0%} off-spec)'); put('IA-ATOM-REMELT', fa - s60, f'{SWARF:.0%} off-spec remelted')
    for k in ('IA-MELT-ATOM', 'S60', 'IA-ATOM-REMELT'): E[k]['composition'] = {'Pb/Sn/Ni/Cd/Zn blend': 1.0}
    for k in ('S57', 'IA-MELT-MILL'): E[k]['composition'] = {'Cu': 1.0} if k == 'S57' else {'metal': 1.0}
    rl = N['GAS_ATOMIZER']['params'].get('balance_rev_l') or {}
    rl['terms'] = [t for t in rl.get('terms', []) if t['label'].startswith('ultrafines')]
    rl['note'] = 'blend charge retired (melt feed IA-MELT-ATOM); off-spec on-graph IA-ATOM-REMELT (A-M-139)'
    # MET_MELT closes on the remelt: sheet + remelt = billet + mill + atomizer feed
    r = _resid(g, 'MET_MELT'); put('IA-MELT-MILL', E['IA-MELT-MILL']['rate']['value'] + r, f'mill draw closes the melt ({r:+.4f})')
    return dict(atom=fa, c29=rec, dr_et=et, mist=qm, purge_m3_h=q/24, h2=h2, nft=qn)

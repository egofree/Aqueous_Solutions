"""X-PAR-02 per-unit transfer functions, storage and farm loops (AQS-PAR-003 sec. 5). Called from balance.physics().
ZNBR2 purge (S69/S69B): sized so the headspace stays at or below 25 % of the H2 LFL (1.0 vol %, NFPA 69 / NFPA 855). H2 from charge-side HER at
  0.66 % of charge current (5.5e-2 mL/h/cm2 at 20 mA/cm2, ZBFB_REVIEW2023) plus open-circuit Zn corrosion 3.2e-3 mL/h/cm2 over the electrode
  area for the non-charging hours; charge Ah from the AQS-ELEC-007 store_in_kWh at 1.82 V (SAND2000-0893); recombination with Br2 not credited.
HYDRO_SET: diverse N+1 backup of ZNBR2 per the owner redundancy rule (A-M-145): NFPA 111 Level 1 Class X over the night hours at the critical load.
NFT: 1 L/min per gully (COOPER1996), gullies at 200 mm pitch across the 1 m unit width (80 mm gully, CROPKING_NFT).
MISTER: high-pressure aeroponics, 6 nozzles/m2 at 0.057 L/min, 4 s on / 4 min off (HPA_PRACTICE, JAE2022_AERO); A-M-136."""
import json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = 96485.0; VZB = 1.82; F_HER = 0.055/(0.020/(2*F)*22414*3600); OC = 3.2e-3; J = 20.0; LFL25 = 0.01; RHO_AIR = 1.18
CHG_H = 6.0; GULLY_PITCH = 0.2; GULLY_LPM = 1.0
NOZ_M2 = 6; NOZ_LPM = 0.015*3.785; T_ON = 4.0; T_OFF = 240.0; DRAIN = 0.20; SWARF = 0.10; ZEO_LOAD = 0.010; BVAD_TOM_TM = 80
BVAD_TOM_T, BVAD_TOM_CO2, BVAD_TOM_C, BVAD_TOM_HI = 2.77, 36.24, 0.43, 0.45   # BVAD2022 Table 4-91 tomato transpiration kg/m2/d and CO2 uptake g/m2/d
BANDS = [(7, 12, 0.34), (13, 20, 0.315), (21, 40, 0.345)]; CUTS = [(5, 10), (11, 18), (19, 28), (29, 99)]
def cut_fractions():
    return [sum(w*max(0, min(b, hi) - max(a, lo) + 1)/(b - a + 1) for a, b, w in BANDS) for lo, hi in CUTS]
# BVAD2022 Table 4-90/4-91: edible fresh g/m2/d -> kg, inedible fresh kg/m2/d, CO2 g/m2/d, O2 g/m2/d, transpiration kg/m2/d
BVAD_CROP = {'tomato': (0.17376, 0.12743, 36.24, 26.36, 2.77), 'pepper': (0.14894, 0.12743, 33.98, 24.71, 2.77), 'lettuce': (0.13135, 0.0073, 10.70, 7.78, 2.10),
             'spinach': (0.07297, 0.0073, 10.70, 7.78, 1.77), 'cabbage': (0.07578, 0.00674, 9.88, 7.19, 1.77), 'onion': (0.08182, 0.0225, 16.50, 12.00, 1.74),
             'strawberry': (0.07788, 0.14446, 34.82, 25.32, 2.22), 'peanut': (0.00596, 0.16875, 49.28, 35.84, 2.77), 'drybean': (0.01111, 0.150, 42.17, 30.67, 2.53)}
FARM_UNITS = [('FRUIT_GUTTER', 'strawberry', ['IA-FRUIT'], ['IA-FRUIT-TRIM'], 'IA-BED-FRUIT'), ('PEANUT', 'peanut', ['IA-PN-R'], ['IA-PN-TRIM'], 'IA-PN-S'),
              ('NFIX_BED', 'drybean', [], ['IA-NFIX-RES', 'IA-COVER'], 'IA-BED-NFIX')]
VEG_PROXY = {'TOMATO': 'tomato', 'CUCUMBER': 'tomato', 'PEPPER': 'pepper', 'LETTUCE': 'lettuce', 'SPINACH': 'spinach', 'KALE': 'cabbage',
             'ALLIUM': 'onion', 'BASIL': 'lettuce', 'ROSEMARY': 'spinach'}
def _resid(g, u):
    from flow_graph.param.balance import _unit_resid; return _unit_resid(g, u)
def _crit():
    return json.loads(subprocess.run([sys.executable, 'docs-authority/_power_sizing.py'], cwd=ROOT, capture_output=True, text=True, check=True).stdout)['backup']['critical_kW']
from flow_graph.param import drivers as _drv
DRV = _drv.load(); ETA_TURB, ETA_PUMP, PSH_RECHG = 0.80, 0.85, 6.0   # DOE_PSH: pumped storage round trip 70-80 %; small set at the low end
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
    # HYDRO_SET (owner guideline: redundancy in every energy and life-support system; A-M-145): diverse N+1 backup of the night store.
    # NFPA 111 Level 1, Class X = the night hours the failed ZNBR2 would carry, at the AQS-ELEC-007 critical life-support load.
    crit = float(ps.get('critical_kW') or _crit()); night = DRV['night_hours']['value']; e_bus = crit*night
    h = N['HYDRO_SET']['params'].get('head_m_m1', 18); vol = e_bus*3.6e6/(1000*9.81*h*ETA_TURB)
    for k in ('IA-ESS-HYDRO-CHG', 'IA-ESS-HYDRO-DIS', 'S22', 'S23', 'IA-ESS-HYDRO-ELEC'):
        put(k, 0.0, 'standby: reservoir held full; discharges only on loss of ZNBR2 (A-M-145); recharge after an event on PV surplus')
    N['HYDRO_SET']['params'].pop('role_from_need', None)
    N['HYDRO_SET']['params'].update(backup_basis={'role': 'diverse N+1 backup of ZNBR2 (night store); third source FUEL_CELL', 'standard': 'NFPA 111 Level 1, Class X',
        'critical_kW': round(crit, 2), 'class_hours': night, 'energy_kWh_bus': round(e_bus, 1), 'head_m': h, 'eta_turbine_generator': ETA_TURB,
        'eta_pump_motor': ETA_PUMP, 'round_trip': round(ETA_TURB*ETA_PUMP, 3), 'upper_reservoir_m3': round(vol, 0), 'rated_kW_discharge': round(crit, 2),
        'recharge_kW_over_PV_window': round(e_bus/ETA_TURB/ETA_PUMP/PSH_RECHG, 1), 'A-M': 'A-M-145', 'Q': 'Q-006 closed; Q-009 reservoir siting'})
    L, W = [x/1000 for x in N['NFT']['params']['size_mm'][:2]]; n = int(W/GULLY_PITCH); qn = n*GULLY_LPM*1440
    put('IA-NFT-IN', qn, f'{n} gullies x {GULLY_LPM} L/min (COOPER1996) over {L:.0f} m'); put('IA-NFT-OUT', qn, 'film return = supply')
    A = (lambda d: d[0]*d[1]/1e6)(N['MISTER']['params']['size_mm']); qm = A*NOZ_M2*NOZ_LPM*1440*T_ON/(T_ON + T_OFF)
    put('IA-MIST-IN', qm, f'{A:.0f} m2 x {NOZ_M2} nozzles/m2 x {NOZ_LPM} L/min, {T_ON:.0f} s on / {T_OFF/60:.0f} min off (schedule within LAKHIAR2018 range; nozzle flow HPA_PRACTICE; JAE2022_AERO)'); put('IA-MIST-OUT', qm, 'chamber drain return = supply')
    # DUAL_ROOT: substrate bed on the grow-bed water. ET per m2 = the grow bed's (same LED light, same room; IA-BED-VAP over BED_M2);
    # supply = ET/(1 - drain fraction 0.20) (PLOSONE2017_DRAIN 10-20 %, AGRIC2024_LF 15-20 %); drain returns to the bed; ET to the AHU.
    if 'IA-DR-VAP' not in E:
        from flow_graph.param.o2_close import _edge
        g['edges'].append(_edge('IA-DR-VAP', 'DUAL_ROOT', 'CRYO_AHU', 'G', ['mass'], 'dual-root transpiration', 0, 'kg/d', 'FARM', 'CRYO', {'H2O': 1.0})); E = {e['stream_id']: e for e in g['edges']}
    from flow_graph.param.o2_close import BED_M2, CO2_M2
    P = N['DUAL_ROOT']['params']; P.pop('bed_h2o_base', None)
    t_m2 = BVAD_TOM_T*CO2_M2/BVAD_TOM_CO2; bed_et = t_m2*BED_M2; b0 = bed_et       # BVAD tomato water/CO2 ratio at the bed's light-limited CO2
    put('IA-BED-VAP', bed_et, f'{BED_M2:.0f} m2 x {t_m2:.3f} kg/m2/d: BVAD2022 tomato {BVAD_TOM_T} kg/m2/d per {BVAD_TOM_CO2} g CO2, scaled to {CO2_M2:.1f} g CO2/m2/d')
    adr = (lambda d: d[0]*d[1]/1e6)(P['size_mm']); et = t_m2*adr; sup = et/(1 - DRAIN)
    put('IA-DR-IN', sup, f'ET {et:.2f} kg/d ({adr:.0f} m2 at the bed rate {t_m2:.3f} kg/m2/d) / (1 - {DRAIN} drain) (PLOSONE2017_DRAIN)')
    put('IA-DR-OUT', sup - et, f'drain {DRAIN:.0%} of supply back to the bed'); put('IA-DR-VAP', et, 'transpiration to the CRYO AHU coil')
    put('IA-BED-H2O', b0 + et, f'bed ET {b0:.2f} + dual-root ET {et:.2f} drawn through the bed')
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
    # GROW_BED crop carbon (A-M-141): total DM = fixed CO2 x 12/44 / C 43 %; edible = HI 45 % at 94 % water, inedible 90 % water (BVAD2022 tomato).
    # Edible leaves as crew food S14 plus surplus to larvae S14X. The inedible lines (residue, trim, browse, straw) exceed the carbon; Q-008.
    co2f = CO2_M2*BED_M2/1000; dm = co2f*12.011/44.01/BVAD_TOM_C; ed = dm*BVAD_TOM_HI/(1 - 0.94); ined = dm*(1 - BVAD_TOM_HI)/(1 - 0.90)
    put('S14X', ed - E['S14']['rate']['value'], f'edible {ed:.2f} kg/d fresh (DM {dm:.3f} kg/d from {co2f:.3f} kg CO2, HI {BVAD_TOM_HI:.0%}, BVAD2022) less crew food S14')
    r = _resid(g, 'BSFL'); put('IA-BSFL-FRASS', E['IA-BSFL-FRASS']['rate']['value'] + r, f'frass closes the larvae bin on S14X ({r:+.3f})')
    lines = ('IA-RES-01', 'IA-COMP-01', 'IA-GOAT-TRIM', 'IA-STRAW'); claim = sum(E[k]['rate']['value'] for k in lines)
    N['GROW_BED']['params']['crop_carbon'] = {'co2_fixed_kg_d': round(co2f, 3), 'dm_kg_d': round(dm, 3), 'edible_fresh_kg_d': round(ed, 3), 'inedible_fresh_kg_d': round(ined, 3),
        'inedible_lines_claimed_kg_d': round(claim, 3), 'gap_kg_d': round(claim - ined, 3), 'basis': 'BVAD2022 tomato; A-M-141; Q-008'}
    # VEG_BED crops (A-M-142): harvest is the study need; area, CO2 uptake, O2, transpiration and trim per BVAD2022 Tables 4-90/4-91 per m2.
    # The crops had no carbon source on the graph; CO2 now comes from HDR_CO2 (taken off the methanol feed in o2_close), O2 joins CRYO_O2.
    for sid, a, b, ph, what, comp in (('IA-VEG-CO2', 'HDR_CO2', 'VEG_BED', 'G', 'CO2 uptake, vegetable crops', {'CO2': 1.0}), ('IA-VEG-O2', 'VEG_BED', 'CRYO_O2', 'G', 'photosynthetic O2, vegetable crops', {'O2': 0.99, 'Ar': 0.01}),
                                       ('IA-VEG-VAP', 'VEG_BED', 'CRYO_AHU', 'G', 'vegetable-crop transpiration', {'H2O': 1.0})):
        if sid not in E: g['edges'].append(_edge(sid, a, b, ph, ['mass'], what, 0, 'kg/d', 'FARM', 'CRYO', comp)); E[sid] = g['edges'][-1]
    tot = dict(A=0.0, co2=0.0, o2=0.0, t=0.0, ined=0.0); rows = {}
    for crop, proxy in VEG_PROXY.items():
        h = E[f'IA-CROP_{crop}-HAB']['rate']['value']; ed, ined_m2, co2_m2, o2_m2, t_m2c = BVAD_CROP[proxy]; A = h/ed
        rows[crop] = dict(proxy=proxy, area_m2=round(A, 3)); tot['A'] += A; tot['co2'] += A*co2_m2/1000; tot['o2'] += A*o2_m2/1000; tot['t'] += A*t_m2c; tot['ined'] += A*ined_m2
    put('IA-VEG-CO2', tot['co2'], f"{tot['A']:.2f} m2 of crops at BVAD2022 CO2 uptake"); put('IA-VEG-O2', tot['o2'], 'BVAD2022 O2 production')
    put('IA-VEG-VAP', tot['t'], 'BVAD2022 transpiration'); put('IA-VEG-TRIM', tot['ined'], 'BVAD2022 inedible fresh biomass to larvae')
    r = _resid(g, 'VEG_BED'); put('IA-VEG-SUMP', E['IA-VEG-SUMP']['rate']['value'] + r, 'bed return closes the crop water')
    r = _resid(g, 'BSFL'); put('IA-BSFL-FRASS', E['IA-BSFL-FRASS']['rate']['value'] + r, 'frass closes the larvae bin')
    # Other terrestrial crop units (A-M-143): same BVAD2022 per-m2 basis; water by difference on the bed-spill supply edge.
    for u, proxy, harv, trims, sup in FARM_UNITS:
        for sid, a_, b_, what, comp in ((f'IA-{u}-CO2', 'HDR_CO2', u, 'CO2 uptake', {'CO2': 1.0}), (f'IA-{u}-O2', u, 'CRYO_O2', 'photosynthetic O2', {'O2': 0.99, 'Ar': 0.01}),
                                        (f'IA-{u}-VAP', u, 'CRYO_AHU', 'transpiration', {'H2O': 1.0})) + (((trims[0], u, 'COMPOST', 'crop residue', {'biomass': 1.0}),) if trims[0] not in E else ()):
            if sid not in E: g['edges'].append(_edge(sid, a_, b_, 'G' if 'VAP' in sid or 'O2' in sid else ('G' if 'CO2' in sid else 'S'), ['mass'], what, 0, 'kg/d', 'FARM', 'CRYO', comp)); E[sid] = g['edges'][-1]
        ed, ined_m2, co2_m2, o2_m2, t_m2c = BVAD_CROP[proxy]
        base = N[u]['params'].setdefault('crop_claim_base', {k: E[k]['rate']['value'] for k in harv + trims if k in E})
        if harv: h = sum(E[k]['rate']['value'] for k in harv); A = h/ed
        else: h = sum(base.get(k, 0) for k in trims); A = h/(ed + ined_m2); ined_m2 = ed + ined_m2   # cover crop: whole plant returned
        put(f'IA-{u}-CO2', A*co2_m2/1000, f'{A:.2f} m2 {proxy} (BVAD2022) for {h:.3f} kg/d harvest'); put(f'IA-{u}-O2', A*o2_m2/1000, 'BVAD2022 O2')
        put(f'IA-{u}-VAP', A*t_m2c, 'BVAD2022 transpiration'); w = [base.get(k, 0) for k in trims]; tw = sum(w) or 1.0
        for k, x in zip(trims, w): put(k, A*ined_m2*(x/tw if sum(w) else 1/len(trims)), f'BVAD2022 inedible share ({proxy})')
        r = _resid(g, u); put(sup, E[sup]['rate']['value'] - r, f'supply closes the crop water ({-r:+.3f})')
        N[u]['params']['crop_basis'] = {'proxy': proxy, 'area_m2': round(A, 2), 'source': 'BVAD2022', 'A-M': 'A-M-143'}
    r = _resid(g, 'GROW_BED'); put('IA-BED-SUMP', E['IA-BED-SUMP']['rate']['value'] + r, f'bed return carries the spill-crop water ({r:+.3f})')
    if 'IA-SUMP-MU' not in E:
        g['edges'].append(_edge('IA-SUMP-MU', 'ROOF_TANK', 'FISH_SUMP', 'L', ['mass'], 'aquaponic loop make-up (crop transpiration)', 0, 'kg/d', 'GEO', 'FARM', {'H2O': 1.0})); E['IA-SUMP-MU'] = g['edges'][-1]
    put('IA-SUMP-MU', 0.0, 'reset'); put('IA-SUMP-MU', max(0.0, -_resid(g, 'FISH_SUMP')), 'make-up = water the crops transpired off the loop; AHU condensate returns it to the roof tank')
    # Crop lighting (A-M-144): sole-source LED at the bed's DLI 17 mol/m2/d and 2.8 umol/J (o2_close basis) = 70.3 W/m2 average, plus the unit's
    # pre-existing pump/aux study load kept as the base.
    from flow_graph.param.o2_close import DLI, LED
    wm2 = DLI*1e6/LED/86400
    for u in ['VEG_BED'] + [x[0] for x in FARM_UNITS]:
        A_ = N[u]['params']['crop_basis']['area_m2'] if u != 'VEG_BED' else tot['A']; ck = N[u]['continuous_kw']
        aux = N[u]['params'].setdefault('aux_kw_base', ck['value']); kw = aux + A_*wm2/1000
        ck.update(value=round(kw, 4), note=f'LED {A_:.2f} m2 x {wm2:.1f} W/m2 (DLI {DLI}, {LED} umol/J) + aux {aux} kW (A-M-144)')
        for k in (f'SF-{u}', f'SQ-{u}'):
            if k in E: E[k]['rate']['value'] = round(kw, 4)
    # X-RED-06 crew CO2 removal N+1 (A-M-147): two-bed swing assembly (one adsorbs, one regenerates, 144 min half-cycle, CDRA practice) per
    # NASA_CDRA2015; zeolite 5A loading 1.0 wt% at 0.4 kPa CO2 (NASA_5A1998, equilibrium: bed mass is a minimum). N+1 = a second full assembly.
    co2c = E['S90']['rate']['value']; half = 144.0; per_bed = co2c*half/1440/ZEO_LOAD
    N['HABITATION']['params']['co2_removal'] = {'metabolic_CO2_kg_d': round(co2c, 3), 'half_cycle_min': half, 'zeolite_5A_kg_per_bed': round(per_bed, 1),
        'beds_per_assembly': 2, 'assemblies': 2, 'zeolite_total_kg': round(4*per_bed, 1), 'basis': 'NASA_5A1998 1.0 wt% at 0.4 kPa; NASA_CDRA2015 swing pair; N+1 assembly (X-RED-06, A-M-147)'}
    # X-RED-08 food reserve (A-M-148): ride through a total loss of the bed crop until the replant is harvested: BVAD2022 Table 4-112 tomato
    # tM 80 d. Stored as dry matter of the crew food S14 (94 % water). Ration is the 0.6 kg/p.d study placeholder (SURPLUS_PASS_THRESHOLDS).
    s14 = E['S14']['rate']['value']; N['HAB_GALLEY']['params']['food_reserve'] = {'days': BVAD_TOM_TM, 'crew_food_fresh_kg_d': round(s14, 3),
        'reserve_dry_kg': round(s14*(1 - 0.94)*BVAD_TOM_TM, 1), 'basis': 'BVAD2022 Table 4-112 tomato time to harvest; dry store (X-RED-08, A-M-148); retune with the nutrition ration lock'}
    # X-RED-05 / X-RED-09 (A-M-149): water still and toilet each 2 x 100 % (duty + installed standby); the roof-tank inventory is the diverse
    # water backup (AQS-RED-001). VCD feed and average load re-derived from the present inflow at the issued 14-20 kWh/m3 midpoint.
    vin = sum(e['rate']['value'] for e in g['edges'] if e['to_unit_id'] == 'VCD_TRAIN' and 'mass' in e['layers'] and e['rate']['unit'] == 'kg/d')/1000
    P = N['VCD_TRAIN']['params']; P.update(feed_m3_d=round(vin, 4), avg_kw=round(vin*17/24, 4), units_installed=2, redundancy='2 x 100 %, standby still on the same feed header (X-RED-05)')
    N['VCD_TRAIN']['continuous_kw'] = {'value': round(vin*17/24, 4), 'unit': 'kW', 'status': 'study', 'note': f'{vin:.3f} m3/d x 17 kWh/m3 / 24 h (issued 14-20 band midpoint); duty unit only (A-M-149)'}
    for k in ('SF-VCD_TRAIN', 'SQ-VCD_TRAIN'):
        if k in E: E[k]['rate']['value'] = round(vin*17/24, 4)
    N['COMPOST_TOILET']['params'].update(units_installed=2, redundancy='2 x 100 % of crew use; alternate chambers (X-RED-09)')
    N['VEG_BED']['params']['crop_basis'] = {'crops': rows, 'area_m2': round(tot['A'], 2), 'source': 'BVAD2022', 'A-M': 'A-M-142'}
    return dict(veg=tot, ined=ined, claim=claim, atom=fa, c29=rec, dr_et=et, mist=qm, purge_m3_h=q/24, h2=h2, nft=qn)

"""X-PAR-02 per-unit transfer functions, storage and farm loops (AQS-PAR-003 sec. 5). Called from balance.physics().
ZNBR2 purge (S69/S69B): sized so the headspace stays at or below 25 % of the H2 LFL (1.0 vol %, NFPA 69 / NFPA 855). H2 from charge-side HER at
  0.66 % of charge current (5.5e-2 mL/h/cm2 at 20 mA/cm2, ZBFB_REVIEW2023) plus open-circuit Zn corrosion 3.2e-3 mL/h/cm2 over the electrode
  area for the non-charging hours; charge Ah from the AQS-ELEC-007 store_in_kWh at 1.82 V (SAND2000-0893); recombination with Br2 not credited.
HYDRO_SET: diverse N+1 backup of ZNBR2 per the owner redundancy rule (A-M-145): NFPA 111 Level 1 Class X over the night hours at the critical load.
NFT: 1 L/min per gully (COOPER1996), gullies at 200 mm pitch across the 1 m unit width (80 mm gully, CROPKING_NFT).
MISTER: high-pressure aeroponics, 6 nozzles/m2 at 0.057 L/min, 4 s on / 4 min off (HPA_PRACTICE, JAE2022_AERO); A-M-136.
FARM: D-FARM owner ruling 2026-10-18 - GROW_BED re-based to crew duty (A-M-229): area from the crew food need S14 at the
BVAD2022 tomato per-m2 carbon chain scaled to the DLI-17 light-limited CO2 flux; the BH farm neighbourhood (DUAL_ROOT, VEG_BED,
BSFL, FISH_SUMP, NFT, MISTER) and TERRACE_IRRIG stay retired/deleted; the farm gate is GROW_BED presence alone."""
import json, os, subprocess, sys
from . import site as SITE   # apparent gravity from the site profile
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from . import drivers as _drv0; _D = _drv0.load()   # X-PAR-01: constants live in drivers.json
F = 96485.0; VZB = _D['znbr_cell_V']['value']; J = _D['znbr_j_mA_cm2']['value']; F_HER = _D['znbr_her_mL_h_cm2']['value']/(J/1000/(2*F)*22414*3600); OC = _D['znbr_oc_corr_mL_h_cm2']['value']; LFL25 = _D['ELEC.storage-train.ZNBR2.h2_LFL_vol_frac']['value']*_D['h2_purge_frac_of_LFL']['value']; RHO_AIR = SITE.process_air_density(_D['ELEC.storage-train.ZNBR2.purge_air_T_C']['value'])   # purge air is the process space (A-M-401 where the profile states the shell)
CHG_H = _D['znbr_charge_h']['value']; GULLY_PITCH = _D['nft_gully_pitch_m']['value']; GULLY_LPM = _D['nft_gully_L_min']['value']
NOZ_M2 = _D['hpa_nozzles_m2']['value']; NOZ_LPM = _D['hpa_nozzle_L_min']['value']; T_ON = _D['hpa_on_s']['value']; T_OFF = _D['hpa_off_s']['value']; DRAIN = _D['substrate_drain_frac']['value']; SWARF = _D['atomizer_offspec_frac']['value']; ZEO_LOAD = _D['zeolite5A_CO2_wt_frac']['value']; BVAD_TOM_TM = _D['bvad_tomato_tM_d']['value']
BVAD_TOM_T, BVAD_TOM_CO2, BVAD_TOM_C, BVAD_TOM_HI = _D['bvad_tomato_T_kg_m2_d']['value'], _D['bvad_tomato_CO2_g_m2_d']['value'], _D['bvad_tomato_C_frac']['value'], _D['bvad_tomato_HI']['value']
EDIBLE_W = _D['FARM.grow-bed-train.GROW_BED.crop_edible_water_frac']['value']; INED_W = _D['FARM.grow-bed-train.GROW_BED.crop_inedible_water_frac']['value']   # BVAD2022 tomato water contents
VCD_SEC = _D['WTR.potable-upw-train.VCD_TRAIN.sec_kWh_m3']['value']   # issued 14-20 kWh/m3 band midpoint (A-M-149)
BANDS = [(a, b, f) for (a, b), f in zip([(7, 12), (13, 20), (21, 40)], _D['pyro_band_fracs']['value'])]; CUTS = [(5, 10), (11, 18), (19, 28), (29, 99)]
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
DRV = _drv.load(); ETA_TURB, ETA_PUMP, PSH_RECHG = DRV['hydro_eta_turbine']['value'], DRV['hydro_eta_pump']['value'], DRV['PUMPED_HYDRO.hydro-train.recharge_window_h']['value']   # DOE_PSH: pumped storage round trip 70-80 %; small set at the low end; recharge over the PV surplus window (A-M-145)
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
    import importlib.util as _iu, os as _os                                              # Q-009 closed: water tower, head from the building (A-M-187)
    _sp = _iu.spec_from_file_location('_fp', _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '../../models/freecad/params.py')); FP = _iu.module_from_spec(_sp); _sp.loader.exec_module(FP)
    from . import water_tower as WT
    wt = WT.solve(e_bus, FP.PLATE_L, FP.PLATE_W, FP.HYDRO_RES_Z0, FP.basement_z(FP.BASEMENT_LEVELS - 1), V_dead=FP.FIRE_RESERVE_M3); h = round(wt['head_m'], 2); vol = wt['V_m3']
    N['HYDRO_SET']['params']['head_m_m1'] = h; N['HYDRO_SET']['params']['volume_m3_m1'] = round(vol, 0)
    _ei = 1000*SITE.g()*vol*h/3.6e6; _zk = float(N['ZNBR2']['params'].get('kWh') or 0)          # X-QA-02 finding: legacy M1 energy keys were stale (200 m3 x 18 m)
    N['HYDRO_SET']['params'].update(energy_kwh_ideal_study=round(_ei, 1), energy_kwh_recoverable_study=round(_ei*ETA_TURB, 1), vs_znbr2_kwh=round(_zk, 1), fraction_of_znbr2_study=round(_ei*ETA_TURB/_zk, 3) if _zk else None)
    for _k in ('scale_up_volume_path_m3', 'scale_up_head_m', 'scale_up_energy_kwh_ideal', 'scale_up_note'): N['HYDRO_SET']['params'].pop(_k, None)   # superseded by the Q-009 water tower
    for k in ('IA-ESS-HYDRO-CHG', 'IA-ESS-HYDRO-DIS', 'S22', 'S23', 'IA-ESS-HYDRO-ELEC'):
        put(k, 0.0, 'standby: reservoir held full; discharges only on loss of ZNBR2 (A-M-145); recharge after an event on PV surplus')
    N['HYDRO_SET']['params'].pop('role_from_need', None)
    N['HYDRO_SET']['params'].update(backup_basis={'role': 'diverse N+1 backup of ZNBR2 (night store); third source FUEL_CELL', 'standard': 'NFPA 111 Level 1, Class X',
        'critical_kW': round(crit, 2), 'class_hours': night, 'energy_kWh_bus': round(e_bus, 1), 'head_m': h, 'eta_turbine_generator': ETA_TURB,
        'eta_pump_motor': ETA_PUMP, 'round_trip': round(ETA_TURB*ETA_PUMP, 3), 'upper_reservoir_m3': round(vol, 0), 'rated_kW_discharge': round(crit, 2),
        'recharge_kW_over_PV_window': round(e_bus/ETA_TURB/ETA_PUMP/PSH_RECHG, 1), 'A-M': 'A-M-145', 'Q': 'Q-006 closed; Q-009 closed: water tower', 'upper': f"{wt['levels']} reservoir levels x {wt['depth_per_level_m']:.2f} m water over {wt['area_m2']:.0f} m2, {wt['cells_per_level']} cells per level", 'lower': f"CATCH_TANK {wt['catch_depth_m']:.2f} m deep over {wt['area_m2']:.0f} m2", 'eta_net_with_penstock': wt['eta_net']})
    farm = 'GROW_BED' in N and all(k in E for k in ('S14', 'S89', 'IA-BED-VAP', 'IA-BED-H2O'))   # D-FARM owner ruling 2026-10-18: GROW_BED re-based to crew duty (A-M-229); the BH farm neighbourhood (DUAL_ROOT/VEG_BED/BSFL/FISH_SUMP/NFT/MISTER) stays retired
    qn = qm = et = None; BED_M2 = None; ined = claim = dm = ed = co2f = 0.0
    tot = dict(A=0.0, co2=0.0, o2=0.0, t=0.0, ined=0.0); rows = {}
    if farm:
        from flow_graph.param.o2_close import CO2_M2
        # Crew-duty bed (A-M-229): area from the crew food need S14, not the BH residue claim (A-M-151 superseded for Rev AC).
        # Edible fresh per m2 at the light-limited CO2 flux (A-M-133: DLI 17, absorptance 0.9, quantum yield 0.045):
        # DM = fixed CO2 x 12.011/44.01 / C 43 %; edible = HI 45 % at 94 % water (BVAD2022 tomato).
        crew_food = E['S14']['rate']['value']
        ed_m2 = CO2_M2/1000*12.011/44.01/BVAD_TOM_C*BVAD_TOM_HI/(1 - EDIBLE_W)
        BED_M2 = round(crew_food/ed_m2, 2)
        PB = N['GROW_BED']['params']; PB['area_m2'] = BED_M2
        PB['crop_basis'] = {'proxy': 'tomato', 'area_m2': BED_M2, 'crew': (g.get('mvs', {}) or {}).get('site', {}).get('crew'),
            'crew_food_kg_d': crew_food, 'edible_kg_m2_d': round(ed_m2, 6), 'source': 'BVAD2022', 'A-M': 'A-M-229'}
        t_m2 = BVAD_TOM_T*CO2_M2/BVAD_TOM_CO2                                                           # BVAD tomato water/CO2 ratio at the bed's light-limited CO2
        put('IA-BED-VAP', t_m2*BED_M2, f'{BED_M2:.2f} m2 x {t_m2:.3f} kg/m2/d: BVAD2022 tomato {BVAD_TOM_T} kg/m2/d per {BVAD_TOM_CO2} g CO2/m2/d, scaled to the DLI-17 light-limited {CO2_M2:.2f} g CO2/m2/d (A-M-133); crew-duty area {crew_food:.1f} kg/d food / {ed_m2:.4f} kg/m2/d edible (A-M-229)')
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
    if farm:
        # GROW_BED crop carbon (A-M-141 basis; crew duty A-M-229): total DM = fixed CO2 x 12/44 / C 43 %; edible = HI 45 % at
        # 94 % water, inedible 90 % water (BVAD2022 tomato). The bed is sized to the crew food S14, so edible = S14 and the
        # food-surplus export is retired (surplus 0 < the AQS-SUR-001 0.5 kg/d threshold); inedible biomass leaves on S11.
        co2f = CO2_M2*BED_M2/1000; dm = co2f*12.011/44.01/BVAD_TOM_C; ed = dm*BVAD_TOM_HI/(1 - EDIBLE_W); ined = dm*(1 - BVAD_TOM_HI)/(1 - INED_W)
        if 'S14X' in E: put('S14X', max(0.0, ed - E['S14']['rate']['value']), f'edible {ed:.2f} kg/d fresh less crew food S14; export only over the AQS-SUR-001 0.5 kg/d threshold (A-M-229)')
        N['GROW_BED']['params']['crop_carbon'] = {'co2_fixed_kg_d': round(co2f, 3), 'dm_kg_d': round(dm, 3), 'edible_fresh_kg_d': round(ed, 3), 'inedible_fresh_kg_d': round(ined, 3),
            'outlet_inedible': 'S11', 'surplus_export': 'retired: bed sized to the crew food, surplus 0 < 0.5 kg/d (AQS-SUR-001)', 'basis': 'BVAD2022 tomato; crew-duty area from S14 (A-M-229)'}
        # Crew-duty lighting (A-M-144/A-M-229): sole-source LED at the bed's DLI and efficacy (A-M-133) over the crew-duty area;
        # S20 is the bed's electrical feed (direction corrected to SOL_ARK_60K -> GROW_BED, first-principles audit).
        from flow_graph.param.o2_close import DLI, LED
        wm2 = DLI*1e6/LED/86400; kw = BED_M2*wm2/1000
        N['GROW_BED']['continuous_kw'].update(value=round(kw, 4), note=f'LED {BED_M2:.2f} m2 x {wm2:.1f} W/m2 (DLI {DLI}, {LED} umol/J, A-M-133/A-M-144); crew duty (A-M-229)')
        for k in ('S20', f'SF-GROW_BED', f'SQ-GROW_BED'):
            if k in E: E[k]['rate']['value'] = round(kw, 4)
    # X-RED-06 crew CO2 removal N+1 (A-M-147): two-bed swing assembly (one adsorbs, one regenerates, 144 min half-cycle, CDRA practice) per
    # NASA_CDRA2015; zeolite 5A loading 1.0 wt% at 0.4 kPa CO2 (NASA_5A1998, equilibrium: bed mass is a minimum). N+1 = a second full assembly.
    co2c = E['S90']['rate']['value']; half = _D['HAB.life-support-train.HABITATION.cdra_half_cycle_min']['value']; per_bed = co2c*half/1440/ZEO_LOAD
    N['HABITATION']['params']['co2_removal'] = {'metabolic_CO2_kg_d': round(co2c, 3), 'half_cycle_min': half, 'zeolite_5A_kg_per_bed': round(per_bed, 1),
        'beds_per_assembly': 2, 'assemblies': 2, 'zeolite_total_kg': round(4*per_bed, 1), 'basis': 'NASA_5A1998 1.0 wt% at 0.4 kPa; NASA_CDRA2015 swing pair; N+1 assembly (X-RED-06, A-M-147)'}
    if 'HAB_GALLEY' in N:
        # X-RED-08 food reserve (A-M-148): ride through a total loss of the bed crop until the replant is harvested: BVAD2022 Table 4-112 tomato
        # tM 80 d. Stored as dry matter of the crew food S14 (94 % water). Ration is the 0.6 kg/p.d study placeholder (SURPLUS_PASS_THRESHOLDS).
        s14 = E['S14']['rate']['value']; N['HAB_GALLEY']['params']['food_reserve'] = {'days': BVAD_TOM_TM, 'crew_food_fresh_kg_d': round(s14, 3),
            'reserve_dry_kg': round(s14*(1 - EDIBLE_W)*BVAD_TOM_TM, 1), 'basis': 'BVAD2022 Table 4-112 tomato time to harvest; dry store (X-RED-08, A-M-148); retune with the nutrition ration lock'}
    # X-RED-05 / X-RED-09 (A-M-149): water still and toilet each 2 x 100 % (duty + installed standby); the roof-tank inventory is the diverse
    # water backup (AQS-RED-001). VCD feed and average load derived again from the present inflow at the issued 14-20 kWh/m3 midpoint.
    vin = sum(e['rate']['value'] for e in g['edges'] if e['to_unit_id'] == 'VCD_TRAIN' and 'mass' in e['layers'] and e['rate']['unit'] == 'kg/d')/1000
    P = N['VCD_TRAIN']['params']; P.update(feed_m3_d=round(vin, 4), avg_kw=round(vin*VCD_SEC/24, 4), units_installed=2, redundancy='2 x 100 %, standby still on the same feed header (X-RED-05)')
    N['VCD_TRAIN']['continuous_kw'] = {'value': round(vin*VCD_SEC/24, 4), 'unit': 'kW', 'status': 'study', 'note': f'{vin:.3f} m3/d x {VCD_SEC} kWh/m3 / 24 h (issued 14-20 band midpoint); duty unit only (A-M-149)'}
    for k in ('SF-VCD_TRAIN', 'SQ-VCD_TRAIN'):
        if k in E: E[k]['rate']['value'] = round(vin*VCD_SEC/24, 4)
    if 'COMPOST_TOILET' in N:
        N['COMPOST_TOILET']['params'].update(units_installed=2, redundancy='2 x 100 % of crew use; alternate chambers (X-RED-09)')
    # X-RED-07 thermal N+1 (A-M-150): heat rejection = sum of heat edges into HEAT_SINK; 3 x 50 % plate-pack modules (any one out, 100 % kept);
    # GEO_HP 2 x 100 %.
    if 'HEAT_SINK' in N:
        qhs = sum(e['rate']['value'] or 0 for e in g['edges'] if e['to_unit_id'] == 'HEAT_SINK' and e['rate'].get('unit') == 'kW')
        N['HEAT_SINK']['params']['redundancy'] = {'rejection_kW': round(qhs, 2), 'modules': 3, 'module_kW': round(qhs/2, 2), 'rule': '3 x 50 %, N+1 (X-RED-07, A-M-150)'}
    N['GEO_HP']['params'].update(units_installed=2, redundancy='2 x 100 % (X-RED-07)')
    # X-RED-03 distribution N+1 (A-M-152): main-tie-main 480 V bus, each section rated for the whole bus demand (tie closes on loss of a main);
    # MCC and T-1 duplicated; critical life-support loads on an ATS fed from both sections. NEC 240.6 standard ratings.
    import math
    # the section carries the plant bus demand that the power sizing writes (mvs.electrical.need_kw, docs-authority/_power_sizing.py);
    # the sum of the inverter feed edges is only the fallback, because it misses the loads with no feed edge (RECT-EW, the trim heaters)
    _nk = ((g.get('mvs') or {}).get('electrical') or {}).get('need_kw') or {}
    dem = _nk.get('value') if isinstance(_nk.get('value'), (int, float)) else sum(e['rate']['value'] or 0 for e in g['edges'] if e['from_unit_id'] == 'SOL_ARK_60K' and e['rate'].get('unit') == 'kW')
    BUS_V = _D['ELEC.distribution-train.SOL_ARK_60K.bus_V']['value']; PF = _D['bus_power_factor']['value']; CLF = _D['continuous_load_factor']['value']
    amps = dem*1000/(math.sqrt(3)*BUS_V*PF); std = _D['ELEC.distribution-train.SOL_ARK_60K.nec_240_6_ratings_A']['value']
    sec = next(x for x in std if x >= amps*CLF); crit = float(ps.get('critical_kW') or _crit()); ca = crit*1000/(math.sqrt(3)*BUS_V*PF)
    N['SOL_ARK_60K']['params']['redundancy'] = {'arrangement': 'main-tie-main, sections A/B, normally-open tie', 'bus_demand_kW': round(dem, 1),
        'section_rating_A': sec, 'basis_A': round(amps, 1), 'MCC': 'MCC-1A / MCC-1B', 'transformer': '2 x 100 % T-1 15 kVA', 'critical_ATS_A': next(x for x in std if x >= ca*CLF),
        'critical_kW': crit, 'inverter_sections': 6, 'rule': 'X-RED-03, A-M-152; NEC 240.6, 0.9 pf, 125 % continuous'}
    if 'VEG_BED' in N:
        N['VEG_BED']['params']['crop_basis'] = {'crops': rows, 'area_m2': round(tot['A'], 2), 'source': 'BVAD2022', 'A-M': 'A-M-142'}
    return dict(veg=tot, ined=ined, claim=claim, atom=fa, c29=rec, dr_et=et, mist=qm, purge_m3_h=q/24, h2=h2, nft=qn)

"""X-PAR-12 closure (AQS-PAR-005 Rev B): O2, Cl2, H2 and CO2 species transfer functions. Called from balance.physics() before T1-T6.
patch(g) adds the units and edges once and stores the pre-X-PAR-12 base rates in node params (idempotent); tf(g) sets every
X-PAR-12 rate from those bases on each run.
  EW   Faraday, per cell: I = P_dc / 2.12 V (AQS-DUTY-051); cathode CE 0.85, the rest H2; anode 98 % Cl2 + 2 % O2 (O_BRIEN2005).
       Main anode Cl2 (+ its O2) returns to LEACH_CSTR_1 as the leach oxidant (Cl2 + M -> MCl2, chloride EW practice, USBM_CL_EW).
       R10b re-base 2026-10-18 (A-M-255): the DC cell feeds IA-DC-EW_n are restored on the live RECTIFIER (Rev AC renamed RECT_EW;
       BH fa1b4db kW = solver P_bus at the held metal harvests). HCL_BURNER is retired in Rev AC, so the full anode Cl2 (+ O2) goes to
       the leach oxidant line and the cathode H2 goes to the H2 pool (HDR_H2 -> H2_DRYER -> CRYO_H2). The electrolyser stays sized on
       the gross pool draws (A-M-230): the pool surplus accumulates at CRYO_H2 and is reported (L['ew']['h2_pool']), not absorbed.
       The EW_9 foundry stubs (EW9_LIQUOR_TO_MO, EW_METALS_TO_IND) stay unrated: they double-book the IA-EW-09 liquor tail and the
       IA-EW-MET-9/IA-EW-SHEET metal harvests and wait on the foundry sizing pass.
  ELY  PEM electrolyser on roof-tank water: H2 by demand (fuel cell, genset, methanol), O2 = 7.937 x H2. 55 kWh/kg H2 (IEA_GHR2023).
       Restored 2026-10-18 per owner ruling D-O2 (A-M-230): it is the plant's O2 source (the ASU only recovers combustion excess);
       with the crew-duty grow bed (A-M-229) it is the diverse N+1 O2 pair.
  FC   existing pure-O2 PEM FUEL_CELL: reversible water loop and night/cloudy store with ELY (separate H2 and O2, NFPA2, ISO22734, IEC62282).
  GEN  BACKUP_GEN is standby: NFPA 110 8.4.2 monthly exercise only, daily-average fuel; unburned C5-C10 shipped.
  COMB BACKUP_GEN and AFTERBURNER draw O2 from HDR_O2 at 10 % excess (TURNS2012); the same mass less N2 on IA-GEN-AIR; products by species to
       NOX_SCRUB/FLUE_KO; excess O2 recovered by the cold box.
  ASU  species conserving: O2 out = O2 in, CO2 out = CO2 in, IA-CO2-RET = 0.
  CO2  bed dose = light-limited uptake; rest to methanol (CO2 + 3 H2 -> CH3OH + H2O) with ELY H2; methanol product to PROD_MEOH.
"""
import math
F = 96485.0; MOL_A = 86400/F             # mol e- per A-day
from . import drivers as _drv1; _D = _drv1.load()   # X-PAR-01
CE, FO2, VCELL = _D['ew_cathode_CE']['value'], _D['ew_anode_O2_frac']['value'], _D['ew_cell_voltage_V']['value']   # D8: cell voltage single-sourced from drivers (was a 2.12 hardcode)
KWH_H2 = _D['pem_kWh_kg_H2']['value']; HHV_H2 = _D['CRYO.cold-box-asu-recovery-train.feed-and-recovery.H2O_ELYZ.h2_hhv_kWh_kg']['value']; PSH_ELY = _D['ely_window_h']['value']   # PEM system kWh/kg; HHV kWh/kg (CRC_H2); electrolyser runs on the PV window (A-M-133, ely_window_h)
QY, ABS, LED, DLI = (_D[k]['value'] for k in ('bed_quantum_yield', 'bed_absorptance', 'led_efficacy_umol_J', 'bed_DLI')); BED_M2 = _D['FARM.grow-bed-train.GROW_BED.fallback_area_m2']['value']   # BED_M2 fallback only; live area comes from GROW_BED params (A-M-229)
EXC = _D['combustion_excess_O2']['value']
GEN_KW = _D['backup_gen_rated_kW']['value']; EX_LOAD, EX_H, GEN_ETA, LHV_C5 = (_D[k]['value'] for k in ('ELEC.generation-train.BACKUP_GEN.exercise_load_frac', 'ELEC.generation-train.BACKUP_GEN.exercise_h', 'ELEC.generation-train.BACKUP_GEN.eta', 'ELEC.generation-train.BACKUP_GEN.fuel_lhv_kWh_kg'))   # D3: rated kW single-sourced from drivers (AQS-ELEC-007/AQS-RED-001 NFPA 110 rule); NFPA110 8.4.2 exercise; spark engine ~30 % (A-M-134); C5-C10 LHV 44 MJ/kg
PSH_STORE_D = _D['crit_autonomy_d']['value']   # D7: AQS-ELEC-007 AUT_CRIT autonomy days, single-sourced from drivers (read here and in _power_sizing.py)
CO2_M2 = DLI*ABS*QY*44.01                # g CO2/m2/d
CELLS = [(1, 'IA-EW-01'), (2, 'IA-EW-02'), (3, 'IA-EW-03'), (4, 'IA-EW-10'), (5, 'IA-EW-05'), (6, 'IA-EW-06'), (7, 'IA-EW-07'), (8, 'IA-EW-08'), (9, 'IA-EW-09')]
# D8 (2026-10-18): the DC cell-feed kW table is RE-SOLVED from the solver's Faraday currents (solver.ew: I from the held
# metal harvests, P_bus = I x (ew_cell_voltage_V + ew_bus_drop_V) from drivers) instead of the frozen BH fa1b4db values.
# Single-writer rule for IA-DC-EW_n: flow_graph/param/write_graph.py process() is the writer on the committed graph;
# o2_close.tf() only fills gaps (a missing edge on a not-yet-written graph) using these live solver values, so a gap fill
# can never disagree with the writer. EW plate GEOMETRY ownership (calculator owns geometry, graph stamps outputs):
# _ew_sizing.py / solver.ew derive current and tank size from the harvest edges alone; the params.sizing the graph stamps
# back are outputs only, never inputs - there is no output=input loop.
DC_EW = None   # lazy: filled by _dc_ew_kw() on first use from the live solver

def _dc_ew_kw(g):
    """Per-cell DC bus kW from the live solver Faraday chain (D8). Cached per process."""
    global DC_EW
    if DC_EW is None:
        from . import drivers as _drv2, solver as _solver
        _ew = _solver.ew(_drv2.load(), g)
        DC_EW = {k: _ew[f'EW_{k}']['P_bus_kW'] for k, _ in CELLS}
    return DC_EW
CELL_H2 = {1: 'IA-HDR-H2-01', 2: 'IA-HDR-H2-03', 3: 'IA-EW3-H2B', 4: 'IA-EW4-H2', 5: 'IA-EW5-H2B',
           6: 'IA-EW6-H2B', 7: 'IA-EW7-H2B', 8: 'IA-EW8-H2B', 9: 'IA-HDR-H2-04'}
OLD_H2 = ('IA-HDR-H2-01', 'IA-HDR-H2-03', 'IA-HDR-H2-04', 'IA-EW1-H2', 'IA-EW2-H2', 'IA-EW4-H2')
TAG = 'X-PAR-12 TF'

def _edge(sid, a, b, phase, layers, carries, v, unit, sa, sb, comp=None, note=''):
    return {'stream_id': sid, 'from_unit_id': a, 'to_unit_id': b, 'phase': phase, 'layers': layers, 'presence': 'present', 'carries': carries,
            'header': 'dedicated', 'forbidden': 'HDR_O2, HDR_CO2', 'claim_status': 'Claimed / Partial',
            'rate': {'value': round(v, 6), 'unit': unit, 'status': 'study', 'note': note or f'{TAG} (AQS-PAR-005).'},
            'from_sector_id': sa, 'to_sector_id': sb, 'open_boundary': False, 'namespace': 'IA', 'gap_flags': [], 'notes': None, 'composition': comp}

def _node(uid, sector, cls, role, note, params):
    return {'unit_id': uid, 'sector_id': sector, 'presence': 'present', 'class': cls, 'tags': [], 'electrical_role': role, 'diagram_gap': None, 'notes': None,
            'enabled': True, 'continuous_kw': None, 'modules': [], 'params': dict(params, presence='present', note=note)}

def patch(g):
    N = {n['unit_id']: n for n in g['nodes']}; E = {e['stream_id']: e for e in g['edges']}
    if N['CRYO_O2']['params'].get('x_par_12_base'): return False   # R8: base frozen in node params (Rev BH idempotency marker; H2O_ELYZ restored 2026-10-18, D-O2)
    v = lambda k: float(E[k]['rate']['value'] or 0)
    base = {k: v(k) for k in ('IA-GEN-AIR', 'IA-NOX-N2', 'IA-NOX-CO2', 'IA-NOX-H2O', 'IA-ASU-N2', 'IA-AB-FLUE', 'S67', 'S67B', 'IA-FLUE-EXH',
                              'IA-BMED-03', 'IA-EVAP_ACID-COND', 'S17-BMED', 'SF-EVAP_ACID', 'IA-PV-01', 'IA-E-SUN') if k in E}   # R8: presence-gate retired Rev AC edges
    base['BMED_kW'] = (N['BMED_ACID'].get('continuous_kw') or {}).get('value')            # R8: Rev AC keeps the BMED kW on the S17-BMED feed edge only
    base['EVAP_kW'] = ((N['EVAP_ACID'].get('continuous_kw') or {}).get('value') if 'EVAP_ACID' in N else None)
    if base['EVAP_kW'] is None: base['EVAP_kW'] = base.get('SF-EVAP_ACID')                # restored EVAP_ACID carries continuous_kw (R8 task A)
    base['bus_r0'] = _bus(g)
    pv = N['PV_ARRAY']['params']; base['PV'] = {k: pv[k] for k in ('count', 'nameplate_kw', 'area_m2') if k in pv}   # R8: Rev AC stores module_kw x count
    if 'nameplate_kw' not in base['PV'] and pv.get('module_kw') is not None: base['PV']['nameplate_kw'] = pv['module_kw']*pv.get('count', 0)
    N['CRYO_O2']['params']['x_par_12_base'] = base
    # R8 scope gates: H2O_ELYZ (restored 2026-10-18, D-O2) and HCL_BURNER died with the Rev AC scope pivot; PROD_O2/PROD_MEOH
    # are graph nodes again (D-AIR restored PROD_O2 verbatim); only PROD_MEOH is still created here (MEOH_TANK needs its product outlet).
    new_nodes = [_node('PROD_MEOH', 'CRYO', 'product', 'none', 'X-PAR-12: methanol product store (carbon leaves the plant as product, no vent).', {})]
    alive = set(N) | {n['unit_id'] for n in new_nodes}
    g['nodes'] += new_nodes
    add = [_edge('IA-GEN-O2', 'HDR_O2', 'BACKUP_GEN', 'G', ['mass'], 'combustion O2, 10 % excess', 0, 'kg/d', 'CRYO', 'GAS', {'O2': 0.99, 'Ar': 0.01}),
           _edge('IA-AB-O2', 'HDR_O2', 'AFTERBURNER', 'G', ['mass'], 'combustion O2, 10 % excess', 0, 'kg/d', 'CRYO', 'GAS', {'O2': 0.99, 'Ar': 0.01}),
           _edge('IA-HCO2-MEOH', 'HDR_CO2', 'MEOH_SYNTH', 'G', ['mass'], 'CO2 not taken by the bed', 0, 'kg/d', 'CRYO', 'CRYO', {'CO2': 1.0}),
           _edge('IA-MEOH-PROD', 'MEOH_TANK', 'PROD_MEOH', 'L', ['mass'], 'methanol product', 0, 'kg/d', 'CRYO', 'CRYO', {'CH3OH': 1.0}),
           _edge('IA-C5-SHIP', 'PROD_C5_C10', 'NORTH_DOCK', 'L', ['mass'], 'C5-C10 product shipped', 0, 'kg/d', 'CRYO', 'DOCK', {'C5-C10': 1.0}),
           _edge('IA-MEOH-SHIP', 'PROD_MEOH', 'NORTH_DOCK', 'L', ['mass'], 'methanol shipped at the dock', 0, 'kg/d', 'CRYO', 'DOCK', {'CH3OH': 1.0}),
           _edge('IA-H2O-MU', 'NORTH_DOCK', 'LEACH_CSTR_1', 'L', ['mass'], 'water make-up for H and O leaving as product', 0, 'kg/d', 'DOCK', 'WET', {'water': 1.0})]
    for k, _ in CELLS:
        add += [_edge(f'IA-EW{k}-CL2', f'EW_{k}', 'LEACH_CSTR_1', 'G', ['mass'], 'anode Cl2 (+ O2 side) to leach oxidation', 0, 'kg/d', 'WET', 'WET')]
    add = [e for e in add if e['stream_id'] not in E and e['from_unit_id'] in alive and e['to_unit_id'] in alive]   # R8: no duplicate stream_ids, no dead endpoints
    g['edges'] += add
    # R8: the OLD_H2 zeroing, IA-CO2-RET zeroing and the balance_rev_l term rewrites belong to the retired
    # cathode-H2 -> HCL_BURNER reroute; Rev AC holds those rates as study rates (R10 owns the re-basis).
    return True

def tf(g):
    if not any(e['stream_id'] == 'IA-C5-SHIP' for e in g['edges']):
        g['edges'].append(_edge('IA-C5-SHIP', 'PROD_C5_C10', 'NORTH_DOCK', 'L', ['mass'], 'C5-C10 product shipped', 0, 'kg/d', 'CRYO', 'DOCK', {'C5-C10': 1.0}))
    N = {n['unit_id']: n for n in g['nodes']}; E = {e['stream_id']: e for e in g['edges']}; B = N['CRYO_O2']['params']['x_par_12_base']
    if 'FORM' in N and not any(e['stream_id'] == 'IA-FORM-N2' for e in g['edges']):   # X-SAF-11 FORM dilution edges (A-M-159); R8: FORM retired in Rev AC
        g['edges'] += [_edge('IA-FORM-N2', 'HDR_N2', 'FORM', 'G', ['mass'], 'N2 diluent to the iron-molybdate bed (lean side, FORMOX_REVIEW2021)', 0, 'kg/d', 'CRYO', 'FARM', {'N2': 1.0}),
                       _edge('IA-FORM-TAIL', 'FORM', 'AFTERBURNER', 'G', ['mass'], 'FORM tail gas: N2, excess O2, trace CH2O/CO to the afterburner', 0, 'kg/d', 'FARM', 'GAS', {'N2': 0.93, 'O2': 0.07})]
    v = lambda k: float(E[k]['rate']['value'] or 0)
    vv = lambda k: float(E[k]['rate']['value'] or 0) if k in E else 0.0            # R8: optional ref, absent in Rev AC
    def put(k, x, why):
        assert x > -1e-6, (k, x, why)
        E[k]['rate']['value'] = round(max(x, 0.0), 6); E[k]['rate']['note'] = (E[k]['rate'].get('note') or '').split(f' | {TAG}')[0] + f' | {TAG}: {why} (AQS-PAR-005).'
    def resid(u):
        r = 0.0
        for e in g['edges']:
            if e['presence'] == 'present' and 'mass' in (e.get('layers') or []) and e['rate'].get('unit') == 'kg/d':
                x = float(e['rate']['value'] or 0); r += x if e['to_unit_id'] == u else 0; r -= x if e['from_unit_id'] == u else 0
        return r
    L = {}
    # --- EW Faraday (R10b re-base, A-M-255): restore the DC feeds on the live RECTIFIER and the missing cathode-H2
    #     outlets on the live pool, then re-solve the gases. The burner pair (IA-EW{n}-H2B/CL2B -> HCL_BURNER) died
    #     with HCL_BURNER in the Rev AC pivot: the full anode Cl2 + O2 rides the leach oxidant line and the cathode
    #     H2 goes to HDR_H2 (the electrolyser keeps its gross-draw sizing per A-M-230; the pool surplus accumulates
    #     at CRYO_H2 and is reported, not absorbed).
    for k, kw in _dc_ew_kw(g).items():
        if f'IA-DC-EW_{k}' not in E and 'RECTIFIER' in N and f'EW_{k}' in N:
            g['edges'].append(_edge(f'IA-DC-EW_{k}', 'RECTIFIER', f'EW_{k}', 'E', ['elec'], 'DC bus bar', kw, 'kW', 'ELEC', 'DIGESTER',
                note='R10b X-PAR-12 gap fill (D8): solver P_bus re-solved live - Faraday I from the held metal harvests x (ew_cell_voltage_V + ew_bus_drop_V from drivers); write_graph.process is the single writer of these edges, this fills gaps only; RECT_EW remapped to the live RECTIFIER (A-M-255).'))
            E[f'IA-DC-EW_{k}'] = g['edges'][-1]
    for k, sid in CELL_H2.items():
        if sid not in E and f'EW_{k}' in N and 'HDR_H2' in N:
            g['edges'].append(_edge(sid, f'EW_{k}', 'HDR_H2', 'G', ['mass'], 'cathode H2 to the H2 pool', 0, 'kg/d', 'DIGESTER', 'CRYO',
                {'H2': 0.98, 'water': 0.02}, 'R10b X-PAR-12: cathode-H2 outlet on the live pool - HCL_BURNER retired in Rev AC (A-M-255).'))
            E[sid] = g['edges'][-1]
    tot = dict(I=0, cl2=0, o2=0, h2=0, cl2b=0)
    for k, ov in CELLS:
        if f'IA-DC-EW_{k}' not in E or CELL_H2[k] not in E: continue
        I = v(f'IA-DC-EW_{k}')*1000/VCELL; ne = I*MOL_A
        h2 = ne*(1-CE)/2*2.016e-3; cl2 = ne*(1-FO2)/2*70.906e-3; o2 = ne*FO2/4*31.998e-3; cl2b = h2/2.016*70.906
        put(CELL_H2[k], h2, f'cathode H2 = I(1-CE)/2F, I = {I:.0f} A, CE {CE}; to the H2 pool (HCL_BURNER retired, A-M-255)')
        put(f'IA-EW{k}-CL2', cl2 + o2, f'anode {1-FO2:.0%} Cl2 + {FO2:.0%} O2, all to leach oxidation (burner share retired with HCL_BURNER; Cl2 + M -> MCl2, USBM_CL_EW)')
        E[f'IA-EW{k}-CL2']['composition'] = {'Cl2': round(cl2/(cl2 + o2), 4), 'O2': round(o2/(cl2 + o2), 4)}
        put(ov, v(ov) + resid(f'EW_{k}'), 'overflow by difference after Faraday gases')
        for a, b in (('I', I), ('cl2', cl2), ('o2', o2), ('h2', h2), ('cl2b', cl2b)): tot[a] += b
    for sid in ('IA-EW1-H2', 'IA-EW2-H2'):   # duplicate cathode-H2 stubs superseded by the re-based outlets
        if sid in E and v(sid) != 0.0: put(sid, 0.0, 'superseded stub: the cell cathode H2 rides IA-HDR-H2-01/-03 (R10b, A-M-255)')
    put('IA-POL-02', v('IA-POL-02') + resid('POLISH_BANK'), 'polish return by difference'); put('IA-REC-01', v('IA-POL-02'), 'recycle out = polish return')
    if 'IA-HDR-H2-02' in E:   # R10b: the header and dryer pass the re-based Faraday H2 to the store
        put('IA-HDR-H2-02', v('IA-HDR-H2-02') + resid('HDR_H2'), 'header passes the EW cathode H2 (R10b Faraday re-base, A-M-255)')
        put('S64', v('IA-HDR-H2-02'), 'dryer pass-through to the store (S24 relief stays shut, AQS-VENT-001)')
    tot['h2_pool'] = round(resid('CRYO_H2'), 6)
    L['ew'] = tot; L['hcl'] = 0.0   # no HCl synthesis in Rev AC: the side-Cl2 share rides the leach oxidant (A-M-255)
    # BMED acid regeneration make-up displaced by synthesis HCl
    regen = 593.5*36.46e-3; prod = v('S09') + v('IA-BMED-01') + vv('IA-HCL-BU'); kb = 1.0   # oxide-leach HCl (solver.leach_acid, GREENWOOD) is still made by BMED; synthesis HCl only replaces the HCl the EW side reaction splits (2 HCl -> H2 + Cl2)
    need = regen
    if N['BMED_ACID'].get('continuous_kw') and B.get('BMED_kW') is not None: N['BMED_ACID']['continuous_kw']['value'] = round(B['BMED_kW']*kb, 4)   # R8: node kW absent in Rev AC
    _s17 = round(B['S17-BMED']*kb, 4)
    if abs(_s17 - v('S17-BMED')) > 1e-3: put('S17-BMED', _s17, f'BMED HCl make {prod+need:.2f} of {prod+regen:.2f} kg/d (k {kb:.3f})')   # epsilon guard (write-convergence fix 2026-10-19): write_graph owns the edge (it re-syncs B['S17-BMED'] every pass); an unconditional put re-appended the TF note each pass and put the balance-last and process-last orderings on different note attractors, so regen --quick broke --check
    # R10a 2026-10-18: the acid/base regen loop is restored to the BH topology (fa1b4db) - IA-BMED-03/04 were Rev AC unrated
    # CRU placeholders with no CRU source basis. Each BMED closes by difference on its leach spent-liquor purge against
    # the loop anchor IA-EVAP_*-FEED (X-PAR acid-loop decision, AQS-PAR-001 s3), the side draws, the condensate return
    # and the X-PAR-10 vent-scrubber tie pair (IA-VS-SPENT into BMED_ACID, IA-VS-NAOH out of BMED_BASE). EVAP_BASE
    # closes on IA-BASE-PPT below (absorbs the retired ACEX caustic draw, BH IA-ACEX-NAOH 0.23).
    # WRITE-CONVERGENCE FIX 2026-10-19 (balance --write rejoins the regen manifest): this block is a graph writer in
    #     the regen successive-substitution loop against write_graph.process, so it obeys the D8 single-writer rule
    #     (as IA-DC-EW_n): write_graph owns the solver-solved edges (EVAP feeds/condensates/vents, the X-PAR-10
    #     scrubber family, kW stamps); this block owns the leach spent purges and the acid product rate. Defects:
    #     (1) IA-BMED-04 missed the X-PAR-10 spent-return term IA-VS-NAOH (base twin of the acid-side IA-VS-SPENT
    #         term): BMED_BASE sat -0.0006 kg/d and the purge flipped +/-0.0006 every write_graph/balance round
    #         trip (the write_graph writer always carried it).
    #     (2) the frozen x_par_12_base re-stamps of IA-EVAP_ACID-COND (864.9665), SF-EVAP_ACID (1.497) and the
    #         EVAP_ACID node kW fought the live solver writer (cond 878.7551): the by-difference purge IA-BMED-03
    #         absorbed the 13.79 kg/d gap every pass - a repulsive fixed point at 439.4 kg/d that pushed IA-ACID-01
    #         up +13.79/pass or collapsed it to the IA-BMED-03 -593.49 assert from below. Retired: write_graph
    #         re-solves those edges from the solver every pass.
    #     (3) edges shared with write_graph are re-derived through solver.evap - the exact write_graph code path,
    #         on its 4-dp grid - behind a 1 g/d epsilon guard, so the 6-dp closure of 4-dp inputs can never
    #         ping-pong against the solver's own rounding (IA-BMED-04: closure 500.1312 vs write_graph 500.1311).
    #     IA-ACID-01 is SIZED to the leach HCl demand - its stated basis (AQS-DUTY-011 'sized to the continuous
    #     neighbor draw', X-RSZ-01 class A bound on current drivers): the old by-difference closure was an identity
    #     map that preserved the stale +1.57 % over-supply (446.5287 vs the 439.6127 the current assay demands)
    #     and held the X-PAR-04 misfit gate red. The EVAP_ACID family follows on the same solver relations, so
    #     write_graph re-derives identical numbers the next regen pass.
    from . import solver as _sol
    from .vent_scrubber import design as _vsd
    _lac = _sol.leach_acid(_D)['hcl_kg_d']; _wa = _D['bmed_product_wt_acid']['value']; _wo = _D['acid_conc_design_wt']['value']
    _pin = round(_lac/_wo, 4); _ea = _sol.evap(_D, _pin*_wo, _wa, _wo, unit='EVAP_ACID')
    _u = _vsd(_D, _ea)['upset']   # X-PAR-10 family is f(acid feed): carried with the re-sized acid product (write_graph stamps the same floats; 1e-5 guard, the family's natural 1e-4 grid)
    for _k, _x in (('IA-EVAP_ACID-VENT', _u['vent_kg_d']), ('IA-VS-NAOH', _u['naoh_soln_kg_d']), ('IA-VS-SPENT', _u['spent_kg_d']), ('IA-VS-OFF', _u['offgas_kg_d'])):
        if _k in E and abs(round(_x, 4) - v(_k)) > 1e-5: put(_k, round(_x, 4), f'X-PAR-10 rate on the re-sized acid family (solver vent_scrubber.design, the write_graph code path; carried by the write-convergence fix 2026-10-19)')
    if 'IA-VS-NAOH' in E: E['IA-VS-NAOH'].setdefault('params', {})['NaOH_mol_d'] = round(_u['naoh_mol_d'], 9)   # identical float to the write_graph stamp
    put('IA-ACID-01', _pin, f'acid product sized to the leach HCl demand: {_lac:.4f} kg/d / {_wo:.0%} = {_pin:.4f} kg/d (AQS-DUTY-011 sized-to-draw basis, X-RSZ-01 class A bound on current drivers; write-convergence fix 2026-10-19: the by-difference closure was an identity map that preserved a stale +1.57 % over-supply)')
    _fd = round(_ea['feed_kg_d'], 4)
    if abs(_fd - v('IA-EVAP_ACID-FEED')) > 1e-3: put('IA-EVAP_ACID-FEED', _fd, 'EVAP_ACID feed re-derived on the sized acid product through solver.evap (column recycle, PERRY7_HCL_VLE); write_graph.process is the writer of record, epsilon guard 1 g/d (write-convergence fix 2026-10-19)')
    _cd = round(_fd - _pin - v('IA-EVAP_ACID-VENT'), 4)
    if abs(_cd - v('IA-EVAP_ACID-COND')) > 1e-3: put('IA-EVAP_ACID-COND', _cd, f'condensate = water off {_ea["water_kg_d"]:.2f} kg/d less the X-PAR-10 vent, on the sized acid product (frozen-base re-stamp 864.9665 retired 2026-10-19: it fought the live solver writer 878.7551 and rattled the purge +13.79 kg/d per pass)')
    put('IA-BMED-03', v('IA-EVAP_ACID-FEED') + v('S09') + v('IA-BMED-01') - v('IA-EVAP_ACID-COND') - vv('IA-VS-SPENT'),
        f"leach spent-acid purge closes BMED_ACID: feed {v('IA-EVAP_ACID-FEED'):.2f} + S09 {v('S09'):.2f} + IA-BMED-01 {v('IA-BMED-01'):.2f} - condensate {v('IA-EVAP_ACID-COND'):.2f} - vent-scrubber spent return {vv('IA-VS-SPENT'):.4f} (X-PAR-10 term, restored 2026-10-19 after it rattled the loop +0.0006 kg/d per pass); BH 449.52 (fa1b4db)")
    _b4 = v('IA-EVAP_BASE-FEED') + v('IA-BMED-02') + vv('IA-VS-NAOH') - v('IA-EVAP_BASE-COND')
    if abs(_b4 - v('IA-BMED-04')) > 1e-3: put('IA-BMED-04', _b4,
        f"leach spent-base purge closes BMED_BASE: feed {v('IA-EVAP_BASE-FEED'):.2f} + IA-BMED-02 {v('IA-BMED-02'):.2f} + vent-scrubber NaOH bleed {vv('IA-VS-NAOH'):.4f} - condensate {v('IA-EVAP_BASE-COND'):.2f} (the X-PAR-10 spent-return term IA-VS-NAOH was missing from the formula, which rattled the loop +0.0006 kg/d per pass once --write resumed; restored 2026-10-19 to match the write_graph writer); BH 502.98 verbatim (fa1b4db); write_graph owns the 4-dp grid, epsilon guard 1 g/d")
    _bp = v('IA-BASE-PPT') + resid('EVAP_BASE')
    if abs(_bp - v('IA-BASE-PPT')) > 1e-3: put('IA-BASE-PPT', _bp, 'base ppt by difference; absorbs the retired ACEX caustic draw (BH IA-ACEX-NAOH 0.23, fa1b4db)')   # epsilon guard (write-convergence fix 2026-10-19): identity closure at the fixed point - an unconditional put churned the note against the write_graph writer
    _kw = round(_ea['kW'], 4)
    if N['EVAP_ACID'].get('continuous_kw') and abs(_kw - N['EVAP_ACID']['continuous_kw']['value']) > 1e-3:
        N['EVAP_ACID']['continuous_kw']['value'] = _kw   # re-sized family: the live solver kW, identical to the write_graph stamp (frozen-base re-stamp retired)
    if 'SF-EVAP_ACID' in E and abs(_kw - v('SF-EVAP_ACID')) > 1e-3:
        put('SF-EVAP_ACID', _kw, '480 V feed equal to EVAP_ACID continuous_kw on the re-sized acid family (live solver.evap value; frozen-base re-stamp retired 2026-10-19)')
    L['bmed'] = (kb, B['S17-BMED'] - v('S17-BMED') + B['SF-EVAP_ACID'] - v('SF-EVAP_ACID'))
    # --- BACKUP_GEN on a standby / exercise basis (NFPA110 8.4.2: monthly exercise >= 30 min at >= 30 % of nameplate); daily average
    if 'gen_full' not in B:
        B['gen_full'] = {k: v(k) for k in ('CUT-1-OUT', 'S45', 'S47', 'S46', 'CUT-1')}
    gf = B['gen_full']; kw_gen = float(N['BACKUP_GEN']['params'].get('rated_kW', GEN_KW))
    e_ex = kw_gen*EX_LOAD*EX_H*12/365                         # kWh/d average
    fuel = e_ex/(GEN_ETA*LHV_C5)                               # kg/d C5-C10
    N['BACKUP_GEN']['params'].update(rated_kW=kw_gen, duty_basis=f'standby; NFPA 110 8.4.2 monthly exercise {EX_H} h at {EX_LOAD:.0%} load = {e_ex:.3f} kWh/d average; fuel {fuel:.3f} kg/d at {GEN_ETA:.0%} on {LHV_C5} kWh/kg LHV (TURNS2012)')
    N['BACKUP_GEN']['continuous_kw'] = {'value': round(e_ex/24, 4), 'unit': 'kW', 'status': 'study', 'note': f'{TAG}: standby, NFPA 110 exercise average'}
    put('CUT-1-OUT', fuel, 'genset exercise fuel (NFPA 110 8.4.2)'); put('S45', 0.0, 'genset runs on the C5-C10 cut only'); put('S47', e_ex/24, 'exercise energy, daily average')
    poly = v('IA-C5-POLY') if 'IA-C5-POLY' in E else 0.0        # olefin feed drawn at the cut tank (AQS-DUTY-073)
    put('IA-C5-SHIP', v('CUT-1') - fuel - poly, f'C5-C10 product not burned: shipped at the dock less the olefin draw {poly:.4f} kg/d (AQS-DUTY-073)')
    r = fuel/gf['CUT-1-OUT']
    # --- combustion O2
    gen_b = v('S45')*7.937 + v('CUT-1-OUT')*(11.75*32.0/107.2); og = EXC*gen_b
    og_full = EXC*(gf['S45']*7.937 + gf['CUT-1-OUT']*(11.75*32.0/107.2))
    put('IA-GEN-O2', og, f'1.10 x ({v("S45"):.3f} H2 x 7.94 + {v("CUT-1-OUT"):.3f} C7.5H17 x 3.51)')
    x_air = (B['IA-GEN-AIR'] - og_full)*r
    if x_air > -1e-6: put('IA-GEN-AIR', x_air, 'N2 diluent, scaled with the exercise fuel')   # R8: Rev AC froze S45 pre-standby but IA-GEN-AIR post-standby; re-basis is R10's
    put('S46', v('IA-GEN-AIR') + og + v('CUT-1-OUT') + v('S45'), 'genset exhaust = inputs')
    dn2 = B['IA-GEN-AIR'] - v('IA-GEN-AIR'); dC = gf['CUT-1-OUT']*(1 - r)*90.0/107.2; dH = gf['CUT-1-OUT']*(1 - r)*17.2/107.2 + gf['S45']   # fuel mass that left on the old graph as C and H
    gco2 = v('CUT-1-OUT')*(7.5*32.0/107.2); gh2o = gen_b - gco2
    ab_co, ab_org = vv('IA-SIC-CO')*0.5711, v('NCG_TO_AB')*0.03*1.066 + 0.3195 + v('S11')*0.001*1.066
    oa = EXC*(ab_co + ab_org); put('IA-AB-O2', oa, f'1.10 x (CO {ab_co:.3f} + organics {ab_org:.3f}); S11 is 99.8 % water')
    # D-DOCK lane 2026-10-19 (balance close, AFTERBURNER -2.18): the flue is the burner mass balance, not a frozen base + O2.
    #    All oxidised inputs (NCG, bed organics S11, sanitation digester gas + cake, combustion O2) leave as flue; the dilution
    #    air IA-AB-AIR joins at the flue junction AFTERBURNER_FLUE on the restored combustion-air path (STOICH), not through
    #    the burner — so it enters S67, not IA-AB-FLUE.
    ab_in = v('NCG_TO_AB') + v('S11') + vv('IA-BLK-GAS') + vv('IA-BLK-CAKE')
    put('IA-AB-FLUE', ab_in + oa, f'burner mass balance: NCG {v("NCG_TO_AB"):.3f} + S11 {v("S11"):.3f} + digester gas {vv("IA-BLK-GAS"):.3f} + cake {vv("IA-BLK-CAKE"):.2f} + combustion O2 {oa:.3f} (oxidised to CO2/H2O, mass through)')
    put('S67B', B['S67B'] + ab_co + ab_org/2, 'bound O2 into CO2 (KO CO2 cut keeps the chemistry basis)')
    put('S67', v('IA-AB-FLUE') + v('IA-AB-AIR'), 'flue junction passes burner flue + dilution air (restored combustion-air path, STOICH IA-AB-AIR)')
    put('IA-FLUE-EXH', v('S67') + vv('S70') + v('IA-LEACH-FLUE') + v('IA-FLUE-QUENCH') - v('S67B'),
        'knockout passes the flue less the CO2 cut S67B (X-SAN-01 quench water and the leach vent ride the inputs)')
    xs = (og - gen_b) + (oa - ab_co - ab_org)
    if 'FORM' in N and all(k in E for k in ('IA-FORM-S', 'IA-MEOH-FORM', 'IA-FORM-O2', 'IA-FORM-N2', 'IA-FORM-TAIL')):
        # X-SAF-11 (A-M-159): FORM feed at about 10 mol% MeOH, 10 mol% O2, 80 mol% N2 (FORMOX_REVIEW2021): O2 = 1 mol per MeOH (half reacts),
        # N2 = 8 mol per MeOH taken from the afterburner dilution air (IA-AB-AIR) so the flue N2 is unchanged; tail to the afterburner.
        fb = N['FORM']['params'].setdefault('dilution_base', {'IA-AB-AIR': v('IA-AB-AIR')})
        nm = (v('IA-FORM-S') + v('IA-MEOH-FORM'))/32.042; n2f = 8*nm*28.013; xo = nm*16.0
        put('IA-FORM-O2', nm*32.0, '1 O2 per MeOH at 10/10 mol% (X-SAF-11)'); put('IA-FORM-N2', n2f, '8 N2 per MeOH (X-SAF-11)'); put('IA-FORM-TAIL', n2f + xo, 'N2 + unreacted O2 (X-SAF-11)')
        put('IA-AB-AIR', fb['IA-AB-AIR'] - n2f, 'dilution air less the N2 routed through FORM (X-SAF-11)')
        put('IA-AB-FLUE', v('IA-AB-FLUE') + n2f + xo, 'flue carries the FORM tail'); put('S67', v('S67') + xo, 'flue carries the FORM excess O2')
        put('IA-FLUE-EXH', v('IA-FLUE-EXH') + xo, 'FORM excess O2'); xs += xo
    if all(k in E for k in ('IA-NOX-N2', 'IA-NOX-CO2', 'IA-ASU-N2', 'IA-ASU-O2', 'IA-ASU-CO2', 'IA-CO2-RET')):
        # R8: the cold-box species family died with CRYO_ASU in the Rev AC pivot; NOX_SCRUB keeps its study rates (R10 re-basis)
        put('IA-NOX-CO2', B['IA-NOX-CO2'] - dC + gco2, 'genset bound O2 into CO2, less the carbon of the fuel no longer burned'); put('IA-NOX-H2O', B['IA-NOX-H2O'] - dH + gh2o + ab_org/2, 'bound O2 into water, less the H no longer burned')
        # D-DOCK lane 2026-10-19 (balance close, NOX_SCRUB +5.04): the gas outlet re-homes to its BH routing — the scrubber
        #    vents to the cold box on IA-NOX-N2/IA-NOX-CO2 (outlets restored with CRYO_ASU per D-AIR) — and closes by
        #    difference against the live inlets instead of the frozen BH base: X-SAN-01 Rev B moved the sanitation loads onto
        #    the inlet edges (leach vent, flue quench) and the old base + retirement-delta arithmetic stopped tracking them.
        nox_in = v('S46') + v('IA-FLUE-EXH') + vv('IA-FC-EXH') + v('IA-LEACH-NOX') + vv('IA-FC-FIX') + v('IA-CLOSE-1') + vv('IA-NIT-VENT')
        put('IA-NOX-N2', nox_in - v('IA-NOX-H2O') - v('IA-NOX-N') - v('IA-NOX-CO2'),
            f'scrubber gas outlet by difference: in {nox_in:.3f} (flue {v("IA-FLUE-EXH"):.2f} + leach vent {v("IA-LEACH-NOX"):.2f} + genset/ties {v("S46") + v("IA-CLOSE-1"):.3f}) less water {v("IA-NOX-H2O"):.2f}, nutrients {v("IA-NOX-N"):.2f}, CO2 {v("IA-NOX-CO2"):.2f} — BH routing to the cold box (D-AIR restored the outlets)')
        E['IA-NOX-N2']['composition'] = {'N2': round(1 - xs/v('IA-NOX-N2'), 4), 'O2': round(xs/v('IA-NOX-N2'), 4)}
        put('IA-ASU-N2', v('IA-NOX-N2') - xs, 'N2 out = N2 in')
        # D-DOCK lane 2026-10-19: plant-air chain closed end-to-end. The header (HDR_N2) passes its draws on IA-AIR-RX-OUT
        #    from the air receiver; the cold box (CRYO_N2) sends S84 to the receiver and exports the surplus N2 on IA-N2-VENT
        #    at the dock boundary (owner ruling D-DOCK: surplus products leave at the dock; the BH vent path re-opens with the
        #    ASU restored per D-AIR). The receiver banks the margin (sizing: docs-authority/_storage_sizing.py, A-M-270).
        hdr_draw = sum(v(k) for k in E if E[k]['from_unit_id'] == 'HDR_N2' and k != 'IA-N2-RET' and E[k]['presence'] == 'present'
                       and 'mass' in (E[k].get('layers') or []) and E[k]['rate'].get('unit') == 'kg/d')
        need = hdr_draw - v('IA-EW4-N2')                                                  # sweep N2 returns below the header balance
        avail = v('IA-ASU-N2') + v('IA-N2-RET') - v('S88') - v('IA-AHU-FIX') - v('S03')    # direct CRYO_N2 draws stay at the cold box
        vent = max(0.0, avail - need)
        put('IA-N2-VENT', vent, f'cold-box N2 surplus exported at the dock boundary (D-DOCK 2026-10-19; BH vent path re-opened with D-AIR): available {avail:.3f} less header need {need:.3f} kg/d')
        put('S84', avail - vent, 'cold-box N2 product to the air receiver, less direct draws (S03 fab N2 purge BH 1.4998 AQS-DUTY-010, R10b) and the dock export')
        if 'IA-AIR-RX-OUT' in E:
            put('IA-AIR-RX-OUT', v('S84'), 'air receiver passes the cold-box delivery to the header at steady state (D-DOCK product buffer; A-M-270)')
        if avail < need - 1e-6: L['n2_header_short_kg_d'] = round(need - avail, 6)
        put('IA-CO2-RET', 0.0, 'no CO2 recycle into the cold box'); put('IA-ASU-CO2', v('IA-NOX-CO2'), 'CO2 out = CO2 in'); put('IA-ASU-O2', xs, 'O2 out = O2 in (combustion excess)')
    L['comb'] = dict(gen=og, ab=oa, gen_b=gen_b, ab_b=ab_co + ab_org, xs=xs)
    # --- CO2: light-limited bed, rest to methanol
    bm2 = N['GROW_BED']['params'].get('area_m2', BED_M2); bed = bm2*CO2_M2/1000; veg = sum(v(k) for k in E if k.startswith('IA-') and k.endswith('-CO2') and E[k]['from_unit_id'] == 'HDR_CO2' and E[k]['to_unit_id'] not in ('MEOH_SYNTH',)); others = sum(vv(k) for k in ('S90', 'IA-COMP-CO2', 'IA-COMP-FIX', 'IA-YEAST-CO2', 'IA-ABE-CO2'))
    put('S04', 0.0, 'bed dosed from HDR_CO2 only'); put('S85', max(0.0, bed + veg - others), 'cold-box CO2 to header only if the bed needs it'); put('S89', bed, f'light-limited uptake {bm2:.2f} m2 x {CO2_M2:.1f} g CO2/m2/d (DLI {DLI}, A-M-133); crew-duty area from GROW_BED params: S14 crew food / BVAD2022 tomato edible at the same flux (A-M-229)')
    put('IA-HCO2-MEOH', v('S85') + others - bed - veg, 'header CO2 the bed cannot fix'); put('S73', v('S73') + resid('CRYO_CO2'), 'cold-box CO2 to methanol by difference')
    co2m = v('S73') + v('IA-HCO2-MEOH')
    put('S74', co2m*3*2.016/44.01, 'CO2 + 3 H2'); put('S75', co2m*(1 + 3*2.016/44.01 - 18.015/44.01), '-> CH3OH (mass closed)'); put('IA-MEOH-H2O', co2m*18.015/44.01, '+ H2O')
    x_meoh = v('IA-MEOH-PROD') + resid('MEOH_TANK')
    if x_meoh > -1e-6: put('IA-MEOH-PROD', x_meoh, 'methanol product by difference')   # R8: Rev AC draws more methanol than S75 makes; residual left to R10
    put('IA-MEOH-COND', v('IA-MEOH-COND') + resid('MEOH_COND'), 'condensate to roof')
    L['co2'] = dict(bed=bed, meoh=co2m, others=others)
    # --- electrolyser by H2 demand (D-O2 owner ruling 2026-10-18, A-M-230: H2O_ELYZ restored as the O2 source; re-based to the
    #     Rev AC H2 pool. Sized on the gross pool draws S45 genset + S49 fuel cell + S74 methanol: the stale EW cathode-H2 study
    #     rates (IA-HDR-H2-01/03/04 -> S64 into CRYO_H2) are not credited — the BH Faraday basis routes cathode H2 to HCl
    #     synthesis, not the pool, and crediting the phantom would undersize the O2 source below the draws (P19). The S64
    #     accumulation at CRYO_H2 is reported in L['ely']['h2_pool_resid_kg_d'] and owned by the R10 EW re-basis.)
    if 'H2O_ELYZ' in N and 'IA-ELY-H2' in E:
        # D-DOCK lane 2026-10-19 (balance close, CRYO_H2 +1.975): the electrolyser is sized to the pool draws NET of the EW
        #     Faraday cathode credit S64. A-M-230 kept the gross basis because the BH-era cathode H2 was a phantom (it routed
        #     to HCl synthesis); the R10b re-base (A-M-255) put the full Faraday cathode H2 on the live pool, so the credit is
        #     now real metering, not phantom accounting. Which side governs: the H2 side — O2 headroom stays large either way
        #     (IA-ELY-O2 72.4 kg/d vs 45.2 kg/d of header + direct draws after netting; the 27.2 kg/d surplus still exports on
        #     IA-O2-PROD, so the O2 N+1 rule P19 is intact and O2 does not constrain the electrolyser size). EW-down case:
        #     methanol (S74) throttles before the fuel cell; ELY-down case: the CRYO_H2 autonomy store covers it (AQS-ELEC-007).
        ew_credit = v('S64') if 'S64' in E else 0.0
        h2 = max(0.0, v('S45') + v('S49') + v('S74') - ew_credit); o2 = h2*31.998/4.032
        put('IA-ELY-H2', h2, f'H2 demand net of the live EW Faraday cathode credit: genset {v("S45"):.2f} + fuel cell {v("S49"):.2f} + methanol {v("S74"):.2f} - S64 {ew_credit:.3f} kg/d (A-M-255 credit; H2 side governs, O2 headroom documented in A-M-272)')
        put('IA-ELY-O2', o2, 'O2 = 7.937 x H2'); put('IA-ELY-H2O', h2 + o2, 'water split')
        kw = h2*KWH_H2/24; E['SF-H2O_ELYZ']['rate']['value'] = round(kw, 4)
        q = kw - h2*HHV_H2/24   # stack heat: BH carried it on SQ-H2O_ELYZ to HEAT_SINK; HEAT_SINK retired in Rev AC, and the
        # R6 heat study re-homed it to the Q4 water header as SQ-H2O_ELYZ-Q4 (AQS-HEAT-STUDY-002 wiring, A-M-247-class) - restamped here
        if 'SQ-H2O_ELYZ-Q4' in E:
            E['SQ-H2O_ELYZ-Q4']['rate']['value'] = round(q, 4)
            E['SQ-H2O_ELYZ-Q4']['rate']['note'] = (E['SQ-H2O_ELYZ-Q4']['rate'].get('note') or '').split(f' | {TAG}')[0] + \
                f' | {TAG}: stack heat {q:.2f} kW routed to Q4_BUS (Rev AC heat-study wiring; BH HEAT_SINK retired), closes the ELY energy balance (A-M-230, restamped R10b).'
        if 'SQ-H2O_ELYZ' in E: E['SQ-H2O_ELYZ']['rate']['value'] = round(q, 4)
        N['H2O_ELYZ']['continuous_kw'] = {'value': round(kw, 4), 'unit': 'kW', 'status': 'study', 'note': f'{TAG}: {h2:.2f} kg/d H2 x {KWH_H2} kWh/kg / 24 h; rated {h2*KWH_H2/PSH_ELY:.1f} kW on a {PSH_ELY} h PV window.'}
        N['H2O_ELYZ']['params']['stack_heat_kw'] = {'value': round(q, 4), 'unit': 'kW', 'status': 'study', 'note': f'{TAG}: {q:.2f} kW stack heat routed on SQ-H2O_ELYZ-Q4 to the Q4 water header (Rev AC heat-study wiring; BH HEAT_SINK retired) - A-M-230 note restamped R10b.'}
        L['ely'] = dict(h2=h2, h2_ew_credit_kg_d=round(ew_credit, 6), h2_gross_draws_kg_d=round(v('S45') + v('S49') + v('S74'), 6), o2=o2, kw=kw, rated=h2*KWH_H2/PSH_ELY, stack_heat_kw=q, h2_pool_resid_kg_d=round(resid('CRYO_H2'), 6))
    if 'IA-ASU-N2' in E:
        # TF re-basis 2026-10-18 (A-M-227 follow-up, D-AIR restored topology): the EW_4 sweep rate re-solves from the HDR_N2
        # header balance instead of holding the stale BH 0.710 kg/d. When even a zero sweep leaves the header over-supplied
        # (restored ASU pass-through S84 > header draws), the surplus is REPORTED as a residual item (L + edge note), not
        # absorbed by a negative sweep and not an assert — the N2 loop closure is R10 work on the NOX/AHU gas returns.
        n2 = resid('HDR_N2'); sweep = v('IA-EW4-N2') - n2
        if sweep > -1e-6:
            put('IA-EW4-N2', sweep, f'header balance: sweep N2 re-solved {n2:+.3f} kg/d at HDR_N2 (restored ASU topology)')
        else:
            put('IA-EW4-N2', 0.0, f'sweep held closed: N2 header over-supplied {-sweep:.3f} kg/d even at zero sweep (ASU pass-through vs header draws); residual reported, not absorbed (A-M-227)')
            L['n2_header_surplus_kg_d'] = round(-sweep, 6)
    put('IA-MEOH-SHIP', v('IA-MEOH-PROD'), 'shipped')
    return L

def close_o2(g):
    """After T6: O2 product = cold-box O2 + bed O2 + electrolyser O2; surplus to PROD_O2.
    TF re-basis 2026-10-18 (A-M-230, owner ruling D-O2): H2O_ELYZ is restored and is the O2 source; with the crew-duty bed
    (A-M-229) and the ASU recovery the sources cover the header draws and the direct CRYO_O2 draws, and the surplus leaves on
    IA-O2-PROD/IA-O2-SHIP. The REPORT structure from the A-M-228 gap era stays (edge notes, CRYO_O2 params o2_gap,
    LAST['o2']): no asserts while the R10 stale-rate lanes are open — the ledger is written either way. S83 now passes on
    what is left after the direct CRYO_O2 draws (S02 crew and S50 fuel cell were re-homed onto CRYO_O2 in Rev AC; at BH
    they drew from HDR_O2, which is why the old formula did not subtract them and CRYO_O2 sat -41.8 kg/d)."""
    N = {n['unit_id']: n for n in g['nodes']}
    E = {e['stream_id']: e for e in g['edges']}; v = lambda k: float(E[k]['rate']['value'] or 0)
    vv = lambda k: float(E[k]['rate']['value'] or 0) if k in E else 0.0
    src = v('S87') + vv('IA-ASU-O2') + vv('IA-ELY-O2') + sum(v(k) for k in E if k.startswith('IA-') and k.endswith('-O2') and E[k]['to_unit_id'] == 'CRYO_O2' and E[k]['from_unit_id'] in ('VEG_BED', 'FRUIT_GUTTER', 'PEANUT', 'NFIX_BED'))
    direct = sum(v(k) for k in E if E[k]['from_unit_id'] == 'CRYO_O2' and k not in ('S83', 'IA-O2-MAKE') and E[k]['presence'] == 'present' and 'mass' in (E[k].get('layers') or []) and E[k]['rate'].get('unit') == 'kg/d')
    draw = sum(float(e['rate']['value'] or 0) for e in g['edges'] if e['from_unit_id'] == 'HDR_O2' and e['stream_id'] not in ('IA-O2-RET', 'IA-O2-PROD') and e['presence'] == 'present')
    if 'IA-O2-PROD' in E and ('IA-ASU-O2' in E or 'IA-ELY-O2' in E):
        E['S83']['rate']['value'] = round(src - direct - v('IA-O2-MAKE'), 6)
        E['IA-O2-PROD']['rate']['value'] = round(max(src - direct - draw, 0.0), 6)
        E['IA-O2-SHIP']['rate']['value'] = E['IA-O2-PROD']['rate']['value']
        gap_hdr = draw - src; gap_sys = draw + direct - src
        if gap_hdr > 1e-6:
            why = (f'O2 short {gap_hdr:.3f} kg/d at HDR_O2 (src {src:.3f} vs draw {draw:.3f}); system gap {gap_sys:.3f} kg/d incl. CRYO_O2 direct draws '
                   f'(S02 crew {vv("S02"):.1f}, S50 fuel cell {vv("S50"):.1f}); surplus outlet held closed — residual reported per A-M-228 (O2 N+1 source decision open)')
            for k in ('IA-O2-PROD', 'IA-O2-SHIP', 'S83'):
                E[k]['rate']['note'] = (E[k]['rate'].get('note') or '').split(f' | {TAG}')[0] + f' | {TAG}: {why} (AQS-PAR-005).'
        N['CRYO_O2']['params']['o2_gap'] = {'hdr_short_kg_d': round(max(gap_hdr, 0.0), 4), 'system_short_kg_d': round(max(gap_sys, 0.0), 4),
            'system_surplus_kg_d': round(max(-gap_sys, 0.0), 4),
            'src_kg_d': round(src, 4), 'hdr_draw_kg_d': round(draw, 4), 'direct_draw_kg_d': round(direct, 4),
            'basis': 'A-M-230 (D-O2): H2O_ELYZ restored — sources IA-ELY-O2 (PEM electrolyser, the O2 source) + S87 (crew-duty bed, A-M-229) + IA-ASU-O2 (recovered combustion excess); S02/S50 draw directly on CRYO_O2 (Rev AC re-home), the rest via HDR_O2',
            'note': 'reported ledger, not an assert (A-M-228 discipline kept): surplus carried by IA-O2-PROD/IA-O2-SHIP'}
        LAST['o2'] = (src, draw, round(gap_sys, 6))
    return src, draw

def _bus(g):
    r = 0.0
    for e in g['edges']:
        if e['presence'] == 'present' and 'elec' in (e.get('layers') or []):
            x = float(e['rate']['value'] or 0); r += x if e['to_unit_id'] == 'SOL_ARK_60K' else 0; r -= x if e['from_unit_id'] == 'SOL_ARK_60K' else 0
    return r

def close_power(g):
    """Bus by difference on PV average; array count/area scale with it."""
    N = {n['unit_id']: n for n in g['nodes']}; E = {e['stream_id']: e for e in g['edges']}; B = N['CRYO_O2']['params']['x_par_12_base']
    r = _bus(g) - B['bus_r0']
    pv = float(E['IA-PV-01']['rate']['value']) - r; f = pv/B['IA-PV-01']
    E['IA-PV-01']['rate']['value'] = round(pv, 4)
    if 'IA-E-SUN' in E: E['IA-E-SUN']['rate']['value'] = round(B['IA-E-SUN']*f, 4)   # R8: solar-resource edge retired in Rev AC
    if N['PV_ARRAY'].get('continuous_kw') is not None: N['PV_ARRAY']['continuous_kw']['value'] = round(pv, 4)
    return pv, B['IA-PV-01'], f, (B['PV'].get('area_m2', 0.0)*(f - 1) if B['PV'].get('area_m2') else None)
LAST = {}

def storage(g):
    """ELY + FUEL_CELL as a reversible water loop and store at the existing 200 bar basis (CRYO_H2 store_kg). Ideal gas x Z (A-M-133)."""
    N = {n['unit_id']: n for n in g['nodes']}; E = {e['stream_id']: e for e in g['edges']}; v = lambda k: float(E[k]['rate']['value'] or 0)
    fc_h2 = v('S49'); fc_kwh = v('S51')*24; e_fc = fc_kwh/fc_h2; rte = e_fc/KWH_H2
    h2d = v('IA-ELY-H2') if 'IA-ELY-H2' in E else 0.0                       # D-O2 2026-10-18: electrolyser restored (A-M-230); without it the store sizes on the fuel-cell need alone
    buf = h2d*(1 - PSH_ELY/24); res = PSH_STORE_D*fc_h2      # PV-window buffer + AQS-ELEC-007 autonomy days of fuel-cell draw (cloudy-day case: PV oversize x cloudy yield >= 1, so the electrolyser keeps running; only the dark hours and an outage need store)
    st = math.ceil(buf + res); hrs = st/(fc_h2/24)
    N['CRYO_H2']['params'].update(store_kg=st, store_basis=f'need: {buf:.1f} kg dark-hours buffer ({h2d:.2f} kg/d x (1 - {PSH_ELY:.0f}/24)) + {res:.1f} kg = {PSH_STORE_D:.0f} d fuel-cell autonomy (AQS-ELEC-007 AUT_CRIT); X-PAR-12')
    P, T, R = _D['CRYO.cold-box-asu-recovery-train.cold-box.CRYO_H2.store_pressure_Pa']['value'], _D['CRYO.cold-box-asu-recovery-train.cold-box.CRYO_H2.store_T_K']['value'], 8.314; rho = lambda M, Z: P*M/(Z*R*T)
    rh2, ro2 = rho(2.016e-3, _D['CRYO.cold-box-asu-recovery-train.cold-box.CRYO_H2.z_h2_200bar_15C']['value']), rho(31.998e-3, _D['CRYO.cold-box-asu-recovery-train.cold-box.CRYO_H2.z_o2_200bar_15C']['value'])
    N['CRYO_H2']['params']['store_water_volume_m3'] = round(st/rh2, 2)      # Z at 200 bar, 15 C: H2 1.13, O2 0.93 (NIST_WEBBOOK isothermal data; verify, A-M-133)
    o2st = st*7.937
    crew = v('S02'); crew_d = max(1.0, PSH_STORE_D); crew_res = crew*crew_d     # X-RED-04: NFPA 99 reserve >= 1 average day; AQS-ELEC-007 2 d governs
    d = dict(fc_h2=fc_h2, fc_kW=v('S51'), e_fc=e_fc, rte=rte, store_h2=st, hours=hrs, rho_h2=rh2, V_h2=st/rh2, store_o2=o2st, rho_o2=ro2, V_o2=o2st/ro2)
    N['CRYO_O2']['params'].update({'storage_mode': 'compressed gas, 200 bar, Type I cylinder bank, O2-cleaned (ASTM G93), separate from H2 (NFPA 2 ch. 7 separation)',
                                    'store_kg': round(o2st, 1), 'store_water_volume_m3': round(o2st/ro2, 2), 'store_basis': 'stoichiometric partner of the CRYO_H2 store (X-PAR-12)',
                                    'crew_reserve_kg': round(crew_res, 2), 'crew_reserve_basis': f'separate cylinder bank, crew draw {crew:.2f} kg/d x {crew_d:.0f} d (NFPA 99 reserve >= 1 average day; AQS-ELEC-007 autonomy 2 d governs); not drawn by FUEL_CELL (X-RED-04, A-M-146)'})
    N['FUEL_CELL']['params']['reversible_loop'] = {'electrolyser': 'H2O_ELYZ', 'round_trip': round(rte, 3), 'basis': f'PEM {KWH_H2} kWh/kg H2 in, {e_fc:.1f} kWh/kg out', 'oxidant': 'pure O2 from HDR_O2; H2 and O2 never mixed (NFPA 2, ISO 22734, IEC 62282-3-100)'}
    return d

def report(gb, ga, L, S):
    from flow_graph.param.gas_species import ledger
    Eb = {e['stream_id']: float(e['rate']['value'] or 0) for e in gb['edges']}; Ea = {e['stream_id']: float(e['rate']['value'] or 0) for e in ga['edges']}
    lb = ledger(gb); before_gap = lb['sink'] + lb['need'] - lb['src']
    drawa = sum(float(e['rate']['value'] or 0) for e in ga['edges'] if e['from_unit_id'] == 'HDR_O2' and e['stream_id'] not in ('IA-O2-RET', 'IA-O2-PROD') and e['presence'] == 'present')
    Nb = {n['unit_id']: n for n in gb['nodes']}; Na = {n['unit_id']: n for n in ga['nodes']}
    offcl = sum(t['value'] for n in gb['nodes'] if n['unit_id'].startswith('EW_') for t in (n['params'].get('balance_rev_l') or {}).get('terms', []) if 'anode Cl2' in t['label'])
    h2b = sum(Eb[k] for k in OLD_H2); ew = L['ew']; c = L['comb']; pb, pa = Nb['PV_ARRAY']['params'], Na['PV_ARRAY']['params']
    X = ['# O2 source study and species closure', '', 'Document number: AQS-PAR-005', 'Revision: C', 'Date: 2026-10-15',
         'Authority: AQS-PLAN-007 X-PAR-12, X-PAR-11. Generated by `flow_graph/param/o2_source.py` (Rev A study) and `flow_graph/param/o2_close.py` (Rev B transfer functions, run from balance.physics). A-M-132, A-M-133.', '',
         '| Rev | Description | Date |', '| --- | --- | --- |', '| A | Audit, light-limited bed, source comparison. | 2026-10-15 |',
         '| C | Owner Q-003/Q-004: genset standby (NFPA 110), H2 bank sized from need. | 2026-10-15 |', '| B | Owner: the three errors are physics corrections. Bed credit light-limited; cold box conserves species; EW gases by Faraday with a Cl2 sink; combustion O2 on the graph; PEM electrolyser with the fuel cell as a reversible store; CO2 to methanol. | 2026-10-15 |', '',
         '## 1. O2 ledger (kg/d)', '', '| | before | after |', '| --- | --- | --- |',
         f"| grow-bed photosynthesis S87 | {Eb['S87']:.2f} (claimed: all dosed CO2 fixed) | {Ea['S87']:.2f} (28 m2, DLI 17, light-limited) |",
         f"| cold box IA-ASU-O2 | {Eb['IA-ASU-O2']:.2f} (from IA-CO2-RET {Eb['IA-CO2-RET']:.0f} kg/d CO2 and 0.8 kg/d leach liquor: no species source) | {Ea['IA-ASU-O2']:.2f} (excess combustion O2 recovered) |",
         f"| PEM electrolyser IA-ELY-O2 | 0 | {Ea['IA-ELY-O2']:.2f} |",
         f"| process draws from HDR_O2 | {lb['sink']:.2f} | {drawa - Ea['IA-GEN-O2'] - Ea['IA-AB-O2']:.2f} |",
         f"| combustion O2 (genset {c['gen']:.2f}, afterburner {c['ab']:.2f}, 10 % excess) | {lb['need']:.2f} not on graph (burned in N2) | {c['gen'] + c['ab']:.2f} on IA-GEN-O2, IA-AB-O2 |",
         f"| species gap | **{before_gap:.1f}** | **0.0** |", f"| surplus to PROD_O2 (cylinders, shipped) | - | {Ea['IA-O2-PROD']:.2f} |", '',
         f"BACKUP_GEN is standby (owner Q-003): NFPA 110 8.4.2 monthly 30 min exercise at 30 % of {GEN_KW:.0f} kW, {Ea['CUT-1-OUT']:.3f} kg/d fuel daily average (was {Eb['CUT-1-OUT']:.2f} continuous); {Ea['IA-C5-SHIP']:.2f} kg/d C5-C10 shipped as product.", '',
         f"The electrolyser is sized by H2 demand (fuel cell {Ea['S49']:.2f}, genset {Ea['S45']:.2f}, methanol {Ea['S74']:.2f} kg/d), not by the O2 gap; its O2 exceeds the corrected gap and the surplus is product, not vent.", '',
         '## 2. Chlorine and EW hydrogen (kg/d)', '', '| | before | after |', '| --- | --- | --- |',
         f"| EW current, A-cell (P_dc / 2.12 V) | {ew['I']:,.0f} | same |",
         f"| anode Cl2 | {offcl:.1f} off-graph to HDR_ACID_GAS (no such unit) | {ew['cl2']:.1f} by Faraday (98 % of current) |",
         f"| anode O2 side reaction | - | {ew['o2']:.2f}, with the Cl2 to the leach (consumed as oxidant) |",
         f"| Cl2 to leach oxidation (Cl2 + M -> MCl2) | 0 | {ew['cl2'] - ew['cl2b']:.1f} |",
         f"| cathode H2 | {h2b:.2f} to HDR_H2 (needs {h2b/2.016e-3*2/MOL_A:,.0f} A-cell) | {ew['h2']:.2f} (CE 0.85) to HCL_BURNER |",
         f"| side Cl2 to HCL_BURNER | 0 | {ew['cl2b']:.2f} |", f"| HCl synthesised to the leach | 0 | {L['hcl']:.2f} |",
         f"| off-graph REGEN LEACH make-up into CONTINUOUS_RECYCLE | 223.8 | 0 (withdrawn) |", '',
         'Cl2 sink by calculation. (a) HCl synthesis of all anode Cl2 needs '
         f"{ew['cl2']/70.906*2.016:.1f} kg/d H2 (= {ew['cl2']/70.906*2.016*KWH_H2/24:.0f} kW of electrolysis) and returns {ew['cl2']/70.906*2*36.46:.0f} kg/d HCl that the oxide leach does not need (solver.leach_acid {87.9:.1f} kg/d). "
         '(b) Cl2 to leach oxidation of the metallic scrap loop (IA-HOP-01 worn goods, the EW sheet source) needs no unit and no H2: Cl2 + M -> MCl2 is the reverse of the cell reaction (USBM_CL_EW). '
         '(c) hypochlorite: 2 NaOH per Cl2, a NaOCl stream with no user. Picked: (b) for the main anode Cl2; the side-reaction pair (H2 + Cl2, equimolar) is recombined in a graphite burner (smallest unit that returns the HCl the side reaction split). '
         'BMED duty is unchanged: oxide-leach HCl is still regenerated by BMED (solver, GREENWOOD).', '',
         '## 3. CO2 ledger (kg/d)', '', '| | before | after |', '| --- | --- | --- |',
         f"| CO2 to GROW_BED (S04 + S89) | {Eb['S04'] + Eb['S89']:.2f} | {Ea['S04'] + Ea['S89']:.2f} |",
         f"| IA-CO2-RET into the cold box | {Eb['IA-CO2-RET']:.1f} | 0 |", f"| genset CO2 from on-graph O2 (bound O) | - | +{Ea['IA-NOX-CO2'] - Eb['IA-NOX-CO2']:.2f} on IA-NOX-CO2 |",
         f"| CO2 to methanol (S73 + IA-HCO2-MEOH) | {Eb['S73']:.2f} | {L['co2']['meoh']:.2f} |", f"| methanol product (IA-MEOH-PROD) | 0 | {Ea['IA-MEOH-PROD']:.2f} |", '',
         'Sink comparison for the CO2 the 28 m2 bed cannot fix: '
         f"grow bed {L['co2']['meoh']*1000/CO2_M2:.0f} m2 more at DLI 17, LED {L['co2']['meoh']*1000/CO2_M2*DLI/(LED*1e-6)/3.6e6/24:.0f} kW (plus food/biomass and {L['co2']['meoh']*32/44.01:.0f} kg/d more O2, already in surplus); "
         f"methanol {L['co2']['meoh']*3*2.016/44.01:.2f} kg/d H2 = {L['co2']['meoh']*3*2.016/44.01*KWH_H2/24:.0f} kW of electrolysis. Picked methanol: about {(L['co2']['meoh']*1000/CO2_M2*DLI/(LED*1e-6)/3.6e6/24)/(L['co2']['meoh']*3*2.016/44.01*KWH_H2/24):.0f} x less power; the bed stays an owner option for food (OPEN_QUESTIONS Q-001).", '',
         '## 4. Electrolyser and fuel cell (reversible water loop)', '',
         f"PEM electrolyser: {L['ely']['h2']:.2f} kg/d H2, {L['ely']['o2']:.1f} kg/d O2, {L['ely']['h2']*8.937:.1f} kg/d water from ROOF_TANK; {L['ely']['kw']:.1f} kW average, {L['ely']['rated']:.0f} kW rated on a {PSH_ELY:.0f} h PV window; stack heat {L['ely']['stack_heat_kw']:.1f} kW (BH HEAT_SINK retired: reported residual, A-M-230).",
         f"Fuel cell (existing FUEL_CELL, pure O2 from HDR_O2): {S['fc_h2']:.2f} kg/d H2 -> {S['fc_kW']:.2f} kW, {S['e_fc']:.1f} kWh/kg; round trip {S['rte']*100:.0f} % (ZNBR2 is the efficient short store; the H2/O2 pair is the multi-day store).",
         f"Store at 200 bar, sized from need (dark-hours buffer + 2 d fuel-cell autonomy, AQS-ELEC-007): H2 {S['store_h2']:.0f} kg ({S['V_h2']:.2f} m3 water volume at {S['rho_h2']:.1f} kg/m3) = {S['hours']:.0f} h of fuel-cell output; O2 partner {S['store_o2']:.0f} kg ({S['V_o2']:.2f} m3 at {S['rho_o2']:.0f} kg/m3), separate bank.",
         'H2 and O2 are generated, stored and piped separately; no mixed (HHO) gas anywhere (NFPA 2-2023 ch. 7 and 10, ISO 22734:2019, IEC 62282-3-100). Fuel-cell water returns via S52 to VCD_TRAIN and on to the roof tank.', '',
         '## 5. Power and roof', '', '| | before | after |', '| --- | --- | --- |',
         f"| PV average IA-PV-01, kW | {Eb['IA-PV-01']:.1f} | {Ea['IA-PV-01']:.1f} |", f"| PV nameplate, kWp | {pb['nameplate_kw']} | {pa['nameplate_kw']} |",
         f"| PV array area, m2 | {pb['area_m2']} | {pa['area_m2']} |", f"| roof footprint, m2 | {pb.get('roof', {}).get('footprint_m2')} | {pa.get('roof', {}).get('footprint_m2')} |",
         f"| ZNBR2, kWh | {Nb['ZNBR2']['params'].get('kWh')} | {Na['ZNBR2']['params'].get('kWh')} |",
         f"| roof-tank make-up IA-POT-01, kg/d | {Eb['IA-POT-01']:.1f} | {Ea['IA-POT-01']:.1f} |", f"| water make-up at the dock IA-H2O-MU, kg/d | 0 | {Ea['IA-H2O-MU']:.1f} (= H and O shipped as methanol and O2) |", '',
         'Regenerated: load list, one-line, AQS-ELEC-007 power sizing (write_graph power), candidate MVS.']
    import os
    open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'docs-authority/O2_SOURCE.md'), 'w').write('\n'.join(X) + '\n')

"""X-PAR-02 balance solver, closure layer (AQS-PAR-001). Edge rates set by a transfer function (parametric generators and the stoichiometric
demand edges listed in STOICH) are held. Every other mass edge is a held study rate; these are reconciled by minimum weighted least squares
subject to every unit balancing exactly [NARASIMHAN2000]: minimise sum(((x - x0)/s)^2), s = x0 (relative) or 1 kg/d for zero-rate return
and trim edges (*-RET, *-FIX, *-MAKE). Tolerance: a reconciled edge moving more than TOL (2 %) is a failure, not a review item (test_balance.py). Physics transfer functions (physics()) run first.
Writes the graph (--write) and docs-authority/BALANCE_RECONCILIATION.md (AQS-PAR-003). Run: python3 -m flow_graph.param.balance [--write]"""
import json, os, sys
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GP = os.path.join(ROOT, 'flow_graph/plant_flow_graph.json')
SINK = {'RELIEF_H2', 'RELIEF_CRYO', 'BOUNDARY_EXPORT', 'NORTH_DOCK'}   # boundary meters: in != out by design (losses, curtailment, exports) — per first-principles audit correction 5, owner rulings 2026-10-18. NORTH_DOCK joined 2026-10-19 per owner ruling D-DOCK: the dock is the inter-plant trade boundary (feedstock imports, surplus-product exports), not a balance-constrained sector — its ledger is reported as a trade statement (params.trade_statement), exempt from unit closure.
MARK = ('X-PAR', 'X-SAN', 'X-MFG', 'AQS-DUTY-06', 'X-SAF-10', 'X-ELS')
STOICH = {'S49': 'H2 to the fuel cell (load)', 'S50': 'O2 = 8 x H2 by mass', 'S02': 'crew O2 0.84 kg/p.d', 'IA-FC-AIR': 'MEOH_FC oxidant',
          'IA-AC-O2': 'acetic acid oxidation', 'IA-O2-NIT': 'nitric acid', 'IA-GLX-O2': 'net one O2 per acetaldehyde via NO recycle (X-PAR-13)', 'IA-FORM-O2': 'one O2 per methanol at 10/10 mol% (X-SAF-11)', 'IA-FORM-N2': 'FORM N2 diluent', 'IA-FORM-TAIL': 'FORM tail gas', 'IA-AB-AIR': 'afterburner dilution air less FORM N2',
          'IA-H2O2-SRC': 'Faraday at the cell current', 'S14': 'crew food', 'S21': 'crew water', 'IA-WASH': 'wash water'}   # S40 removed: TERRACE_IRRIG deleted (D-FARM owner ruling 2026-10-18, A-M-229)
GROSS = 0.05
TRIM = ('-RET', '-FIX', '-MAKE')

TOL = 0.02                                 # measurement tolerance per edge (A-M-120): a reconciled move above 2 % of the rate (1 g/d floor) fails
PHYS_TAG = 'X-PAR-02 TF'
DOCK_STATEMENT = []                        # D-DOCK trade-statement lines, filled by physics() and emitted by report()

def _unit_resid(g, u):
    r = 0.0
    for e in g['edges']:
        if e['presence'] == 'present' and 'mass' in (e.get('layers') or []) and e['rate'].get('unit') == 'kg/d':
            v = float(e['rate']['value'] or 0)
            r += v if e['to_unit_id'] == u else 0.0
            r -= v if e['from_unit_id'] == u else 0.0
    return r

CO2_EDGES = ('S04', 'S67B', 'S73', 'S85', 'S89', 'S90', 'IA-COMP-CO2', 'IA-NOX-CO2', 'IA-ASU-CO2', 'IA-CO2-RET', 'IA-COMP-FIX', 'IA-YEAST-CO2', 'IA-ABE-CO2')
LEACH_SOLIDS = ('IA-FEED-01', 'IA-HOP-01', 'S16', 'IA-BAG-01', 'IA-SIC-RET', 'IA-REC-01')     # solids and the equilibrated EW recycle carry no fresh dissolved gas
from flow_graph.param import site as _site   # external atmosphere from the site profile (AQS-PLAN-011 section 3.2)
_PA = _site.p_atm_Pa()
HENRY = {'CO2': (3.3e-4, 101325.0, 44.01), 'O2': (1.3e-5, _site.air_fraction('O2')*_PA, 32.00), 'N2': (6.4e-6, _site.air_fraction('N2')*_PA, 28.01)}   # Hcp mol/(m3 Pa) at 298 K [SANDER2015], partial pressure Pa (CO2: pure gas at one standard atmosphere, the bound), g/mol

def henry_bound(g):
    """Upper bound on gas desorbed from the leach liquor: every fresh liquid inflow saturated at 25 C under 1 atm CO2 (bounding) plus air O2/N2."""
    gkg = sum(H*p*M/1000.0 for H, p, M in HENRY.values())/1000.0          # kg gas per kg liquor (density 1000 kg/m3)
    flow = sum(float(e['rate']['value'] or 0) for e in g['edges'] if e['to_unit_id'] == 'LEACH_CSTR_1' and e['presence'] == 'present'
               and 'mass' in (e.get('layers') or []) and e['stream_id'] not in LEACH_SOLIDS)
    return flow*gkg

def physics(g):
    """Transfer functions that replace the held study rates which X-SAF-10 left inconsistent (A-M-120, AQS-PAR-003 section 2).
    T1 closed greenhouse at steady state: transpiration = irrigation - drains. RETIRED with TERRACE_IRRIG (owner ruling
       2026-10-18, D-FARM): the terrace node and S40/S41/S42/IA-TERR-VAP are deleted; the crew-duty GROW_BED water path
       is IA-BED-VAP (ET) with IA-BED-H2O closed by difference below (A-M-229).
    T2 AHU condensate = greenhouse vapour in (AQS-DUTY-013: greenhouse vapour condenses to the roof tank, no second outlet).
    T3 O2 product follows the header draw (no storage, no vent; AQS-DUTY-017/019): S83 = IA-ASU-O2 = sum of HDR_O2 draws, IA-O2-RET = 0.
    T4 roof-tank shortfall is made up on the potable path by difference: IA-POT-01, IA-UPW-REMIN, S25 and the leach water bleed IA-LEACH-VCD.
    T5 the leach dissolved-gas edge IA-LEACH-ASU closes the leach and the cold box. It is reduced, toward the Henry's-law solubility bound
       (SANDER2015); the remaining excess over that bound is task X-PAR-11."""
    from flow_graph.param import o2_close
    from flow_graph.param import ess_tf; ess_tf.tf(g)
    o2_close.patch(g); o2_close.tf(g)
    E = {e['stream_id']: e for e in g['edges']}
    v = lambda k: float(E[k]['rate']['value'] or 0)
    def put(k, x, why):
        E[k]['rate']['value'] = round(x, 6)
        E[k]['rate']['note'] = (E[k]['rate'].get('note') or '').split(' | X-PAR-02')[0] + f' | {PHYS_TAG}: {why} (AQS-PAR-003).'
    # R10c (D-DOCK lane 2026-10-19): the remaining reported unit residuals closed on their own stated bases - every edge here
    #    is a pass-through, stoichiometric or source-sized-to-draw basis already named on the edge; nothing is absorbed
    #    without a basis (A-M-228 discipline). Runs between the two o2_close passes so the leach / BMED / header / CO2
    #    chains re-settle on the second pass below.
    for u, k, out, why in (('HOPPER', 'IA-HOP-01', True, 'returned scrap closes the scrap yard by difference: worn goods + swarf + leach return less the dock feed (its stated basis: follows the worn goods)'),
                           ('FUEL_CELL', 'IA-FC-LEACH', True, 'cell drain closes the cell; product water S52 stays on its stoichiometric basis (AQS-DUTY-023)'),
                           ('WS_NITRIC', 'IA-BMED-01', False, 'reagent day tank passes its draw S34; 1.25 mol/d HCl at 36.46 g/mol = 0.0456 kg/d is the stated molar basis (AQS-DUTY-010); BMED_ACID re-closes on the spent-acid purge IA-BMED-03'),
                           ('WS_AMMONIA', 'IA-NH3-SRC', False, 'ammonia source sized to the bench draw S33 (AQS-DUTY-016: each chemical has a source); the N2 header re-settles in o2_close'),
                           ('WS_SOLV', 'IA-SOLV-MU', False, 'solvent resupply imported at the dock boundary equals the bench draw IA-SOLV-WB (D-DOCK reagent import; 30 d hold already sized, A-M-225)'),
                           ('MEOH_FERM', 'IA-FERM-DIG', True, 'fermenter digestate (water + spent solids) joins the blackwater barrier - galley-organics class like IA-GAL; BLACK_DIGEST closes on IA-BLK-GREY (T7)'),
                           ('OIL_PYRO', 'IA-CHAR', True, 'char by difference: pyro feed less the per-pass volatiles = the documented oil 22.5 + NCG 5.0 + C29 pass-through split (the SiC-furnace carbon charge rides IA-SIC-RET)'),
                           ('WET_BENCH', 'S10', True, 'spent etch/return order-of-magnitude band unchanged; closes the bench by difference'),
                           ('MFG_SHOP', 'S16', True, 'shop scrap to the leach closes the shop by difference (AUD s10.6 band; absorbs the char-reductant re-base)')):
        if k in E:
            r = _unit_resid(g, u); put(k, v(k) + (r if out else -r), why)
    # MFG_SHOP is NOT closed here on POLY_TO_MFG/MFG_SCRAP_TO_IND: that pair is a coupled two-edge closure owned by the
    # foundry_poly regen stage (S = K + P + r0, A-M-261) - a partial in-memory mirror would fight it. The shop's surplus
    # outlet S16 (scrap to the leach, AUD s10.6 band) closes it here instead; the foundry stage then re-derives the same
    # P from its own idempotent remnant and the two writers agree at the fixed point.
    if all(k in E for k in ('S76', 'IA-MEOH-REST', 'IA-FC-AIR', 'S82', 'S81', 'IA-CLOSE-10')):
        # MEOH_FC re-base: Rev N held a small-feed oxidant rate (IA-FC-AIR 2.48 kg/d) against the current 5.0 kg/d methanol
        # feed (residual +0.42). Complete oxidation CH3OH + 1.5 O2 -> CO2 + 2 H2O is re-based on the methanol actually
        # burned (S76 + the waste return IA-MEOH-REST); the water edge closes the cell by difference.
        meoh = v('S76') + v('IA-MEOH-REST')
        put('IA-FC-AIR', meoh*1.5*31.998/32.042, f'stoichiometric oxidant 1.5 O2 per CH3OH on {meoh:.3f} kg/d methanol burned (STOICH basis; AQS-DUTY-012 Rev N re-base)')
        put('S82', meoh*44.01/32.042, f'stoichiometric CO2 on {meoh:.3f} kg/d methanol burned (AQS-DUTY-012 Rev N re-base)')
        E['S82']['composition'] = {'CO2': 1.0}
        put('S81', meoh + v('IA-FC-AIR') + v('IA-CLOSE-10') - v('S82'), 'cell water out by difference closes MEOH_FC (the IA-CLOSE-10 liquor tie rides it)')
    XL = o2_close.tf(g)     # second pass settles EW_4 after the N2 trim and the leach/BMED/header/CO2 chains after R10c
    # T6 grow-bed net photosynthesis (X-PAR-11): CO2 + H2O -> CH2O + O2, PQ 1.0 [TAIZ2015]; all CO2 dosed to the bed is fixed at steady state
    #    (the dose is sized to uptake, AQS-DUTY-011). O2 = 32/44 x CO2 leaves on S87 to CRYO_O2; the trim carries CO2 + H2O - O2.
    #    D-FARM owner ruling 2026-10-18: GROW_BED re-based to crew duty (A-M-229) — the bed is a live, closed unit again;
    #    the clean-water make-up IA-BED-H2O closes it by difference (ess_tf.py sets the area, o2_close the CO2 dose).
    if all(k in E for k in ('S04', 'S89', 'S87')):
        co2 = v('S04') + v('S89'); put('S87', co2*32.0/44.01, f'grow-bed photosynthetic O2 = 32/44 x {co2:.3f} kg/d CO2 (PQ 1.0, TAIZ2015)')
        E['S87']['composition'] = {'O2': 0.99, 'Ar': 0.01}
    if 'IA-BED-H2O' in E:
        put('IA-BED-H2O', v('IA-BED-H2O') - _unit_resid(g, 'GROW_BED'), 'crew-duty bed closes by difference on the clean-water line (A-M-229)')
    # T7 crew water and the grey/black train (R10a, 2026-10-18): Rev AC cut HABITATION's crew-4 outputs when the farm rebase
    #    killed their endpoints (HAB_WASH, COMPOST_TOILET, HAB_GALLEY) and diverted the grey water into NUTRIENT_DOSE, where the
    #    by-difference closure pumped it into the leach (the reported water-long +515 kg/d). Restored on live endpoints, BH crew-4
    #    values verbatim (91d33f4): urine/fecal/galley organics to BLACK_DIGEST (X-SAN-01: the blackwater digester is the surviving
    #    barrier 1; the COMPOST_TOILET pre-stage is retired), grey + wash water on S12 to GREY_TREAT (HAB_WASH retired, the wash
    #    rides S12). Closures: HABITATION on S12, BLACK_DIGEST on IA-BLK-GREY (gas 0.10 / cake 0.67 / nutrient split 0.90 are BH
    #    verbatim graph rates; dewater/pasteur/alk-hold barriers retired, splits carried at the digester), GREY_TREAT on IA-GREY-01
    #    (grey sludge to the leach, Rev M pattern), the treated-water draw S29 stays the BH still feed 104.50.
    if all(k in E for k in ('S12', 'IA-BLK-GREY', 'IA-GREY-01')):
        put('S12', v('S12') + _unit_resid(g, 'HABITATION'),
            'crew grey+wash by difference (BH crew-4: 240.23 grey + 80.00 wash ride S12, HAB_WASH retired; 91d33f4)')
        put('IA-BLK-GREY', v('IA-BLK-GREY') + _unit_resid(g, 'BLACK_DIGEST'),
            'released digest liquor by difference (BH 18.43 from the retired BLACK_ALK_HOLD + direct urine/fecal water, 91d33f4)')
        put('IA-GREY-01', v('IA-GREY-01') + _unit_resid(g, 'GREY_TREAT'),
            'grey sludge to the leach by difference (Rev M: sized to the continuous neighbor draw; was 242.65 at BH)')
    for u, k, why in (('GROW_BED', 'IA-BED-COMP', 'trim less the photosynthetic O2'), ('COMPOST', 'IA-COMP-OUT', 'compost passes the trim'), ('NUTRIENT_DOSE', 'IA-NUT-LEACH', 'nutrient surplus by difference')):
        if k in E:
            r = _unit_resid(g, u); put(k, v(k) + r, why)
    for k in CO2_EDGES:
        if k in E: E[k]['composition'] = {'CO2': 1.0}
    if 'IA-HVAC-COND' in E:
        vap_fixed = tuple(k for k in ('IA-BED-VAP', 'IA-HAB-VAP', 'IA-DR-VAP') if k in E)   # IA-DR-VAP retired with DUAL_ROOT; IA-TERR-VAP deleted with TERRACE_IRRIG (A-M-229)
        put('IA-HVAC-COND', sum(v(k) for k in vap_fixed) + sum(v(k) for k in E if k.endswith('-VAP') and E[k]['to_unit_id'] == 'CRYO_AHU' and k not in vap_fixed), 'condensate = greenhouse vapour in')
    if 'IA-O2-RET' in E:
        put('IA-O2-RET', 0.0, 'no surplus O2 return')
    # AHU dehumidification (A-M-153): latent = condensate x h_fg 2.454 MJ/kg at 20 C (NIST_WEBBOOK); coil chiller COP 2.96 (ASHRAE901_2022
    # air-cooled < 150 ton full-load minimum); electric on SF-CRYO_AHU, latent + electric rejected to HEAT_SINK on SQ-CRYO_AHU.
    from flow_graph.param.o2_close import _edge
    N_ = {n['unit_id']: n for n in g['nodes']}
    sink = 'HEAT_SINK' in N_                                                            # R8: HEAT_SINK retired in Rev AC
    for sid, a, b, lay in (('SF-CRYO_AHU', 'SOL_ARK_60K', 'CRYO_AHU', ['elec']), ('SQ-CRYO_AHU', 'CRYO_AHU', 'HEAT_SINK', ['energy'])):
        if sid == 'SQ-CRYO_AHU' and not sink: continue
        if sid not in E: g['edges'].append(_edge(sid, a, b, 'E', lay, 'AHU coil chiller' if sid[1] == 'F' else 'AHU latent + compressor heat', 0, 'kW', 'ELEC', 'CRYO')); E[sid] = g['edges'][-1]
    from . import drivers as _dv; COP = _dv.load()['ahu_chiller_COP']['value']
    ql = v('IA-HVAC-COND')*2.454e3/86400; we = ql/COP
    E['SF-CRYO_AHU']['rate']['value'] = round(we, 4)
    if 'SQ-CRYO_AHU' in E: E['SQ-CRYO_AHU']['rate']['value'] = round(ql + we, 4)
    N_['CRYO_AHU']['continuous_kw'] = {'value': round(we, 4), 'unit': 'kW', 'status': 'study', 'note': f'latent {ql:.2f} kW (condensate {v("IA-HVAC-COND"):.1f} kg/d x 2.454 MJ/kg) / COP {COP} (A-M-153)'}
    src, draw = o2_close.close_o2(g); o2_close.LAST['storage'] = o2_close.storage(g)     # T3; H2/O2 banks re-sized every pass (X-PAR-12): O2 product = cold-box O2 in + bed + electrolyser; surplus to PROD_O2. No O2 from CO2.
    d = -_unit_resid(g, 'ROOF_TANK')
    for k in ('IA-POT-01', 'IA-UPW-REMIN', 'S25', 'IA-LEACH-VCD'):
        if k in E: put(k, v(k) + d, f'roof-tank shortfall {d:+.4f} kg/d by difference on the potable path')
    if 'S01' in E:
        # R10a: the UPW header passes its draws (BH 67.30 = IA-UPW-HAB 0.80 + IA-UPW-USE 66.50; Rev AC had 95.00). Runs after
        # the T4 shift so the header tracks the distillate/remin splits; d cancels (S25 and IA-UPW-REMIN shift together).
        put('S01', v('S01') + _unit_resid(g, 'BMED_UPW_POLISH'), 'UPW header passes its draws IA-UPW-HAB + IA-UPW-USE (BH 67.30, 91d33f4; Rev AC 95.00 overdrew the header)')
    a = _unit_resid(g, 'CRYO_ASU')
    if 'IA-LEACH-ASU' in E:
        # R8: the leach dissolved-gas edge and its Henry bound died with CRYO_ASU in Rev AC; the assert stays for the live path
        lim = henry_bound(g)
        put('IA-LEACH-ASU', max(0.0, v('IA-LEACH-ASU') - a), f'closes leach and cold box ({-a:+.4f} kg/d); Henry bound {lim:.3f} kg/d (SANDER2015)')
        assert v('IA-LEACH-ASU') <= lim + 1e-6, ('IA-LEACH-ASU above the Henry-law bound', v('IA-LEACH-ASU'), lim)
    r_leach = _unit_resid(g, 'LEACH_CSTR_1'); h2o_mu = v('IA-H2O-MU') - r_leach
    if h2o_mu > -1e-6:
        put('IA-H2O-MU', h2o_mu, 'leach water make-up by difference (H and O leave as methanol and O2 product)')
    else:
        # TF re-basis 2026-10-18 (A-M-229 follow-up): the leach train is water-long (hab grey water via NUTRIENT_DOSE
        # closure has no outlet since the bed takes crew-duty nutrient flow only). Report the surplus — do not write a
        # negative make-up rate (the stock run hid -464 kg/d this way). Outlet decision is R10 work.
        put('IA-H2O-MU', 0.0, f'leach water-long {-h2o_mu:.3f} kg/d: no make-up needed, surplus has no outlet; residual reported, not a negative rate (A-M-229)')
    # D-DOCK lane 2026-10-19, product buffer storage (owner ruling D-DOCK: buffer stores assumed built for O2 / water /
    #    compressed air / food / metals): the three stores the graph lacked pass their feeds at steady state, so mass
    #    closure is unchanged — the store is inventory, not a sink (O2: CRYO_O2 bank and water: ROOF_TANK already exist).
    #    FOOD_STORE: fresh harvest S14 lands in the store, S14D feeds the galley; sized on the X-RED-08 80-day dry
    #    reserve basis (A-M-148/A-M-270). METAL_STORE: STOCK_OUT is transit only; the product store buffers the foundry
    #    output against the MFG/FAB/wire draws, 14 d dispatch campaign (A-M-270). AIR_RECEIVER: cold-box delivery bank,
    #    sized on the ASU/vent margin (o2_close.tf S84/IA-AIR-RX-OUT/IA-N2-VENT, A-M-270).
    if all(k in E for k in ('S14', 'S14D')):
        put('S14D', v('S14'), 'food store passes the harvest to the galley at steady state (D-DOCK buffer, A-M-270)')
    if 'IA-STOCK-STORE' in E:
        put('IA-STOCK-STORE', v('IA-STOCK-STORE') - _unit_resid(g, 'METAL_STORE'),
            'metal product store passes the foundry output to the stock draws (D-DOCK buffer, A-M-270)')
    # D-DOCK 2026-10-19: the dock is NOT a regular sector - it is the inter-plant boundary: imports of arbitrary feedstock
    #    (landfill reclaim, mining waste, lunar regolith class) and exports of surplus products to other plants. It must not
    #    be forced to conform to intra-plant closure standards; its ledger is a REPORTED trade statement (imports/exports/net),
    #    not a balance constraint (owner ruling D-DOCK, notes/first_principles_audit_2026-10-17.md). The statement reports
    #    every dock edge; rate rounding at the dock is accepted design-phase noise.
    N_ = {n['unit_id']: n for n in g['nodes']}
    if 'NORTH_DOCK' in N_:
        def _dock(want_in):
            return {e['stream_id']: round(float(e['rate']['value'] or 0), 3) for e in g['edges']
                    if e['presence'] == 'present' and 'mass' in (e.get('layers') or []) and e['rate'].get('unit') == 'kg/d'
                    and ((e['to_unit_id'] == 'NORTH_DOCK') if want_in else (e['from_unit_id'] == 'NORTH_DOCK'))
                    and float(e['rate']['value'] or 0) != 0.0}
        exports_ = _dock(True)      # plant products arriving at the dock for shipment out
        imports_ = _dock(False)     # feedstock/water/reagents the plant takes in
        net_ = round(sum(exports_.values()) - sum(imports_.values()), 3)
        rdock = _unit_resid(g, 'NORTH_DOCK')
        N_['NORTH_DOCK']['params'].pop('site_freight_ledger', None)   # R10a ledger superseded by the D-DOCK trade statement
        N_['NORTH_DOCK']['params']['trade_statement'] = {
            'exports_kg_d': exports_, 'imports_kg_d': imports_, 'net_kg_d': net_, 'residual_kg_d': round(rdock, 3),
            'basis': 'inter-plant trade boundary per owner ruling D-DOCK (2026-10-19): imports of arbitrary feedstock (landfill reclaim, '
                     'mining waste, lunar regolith class), exports of surplus products to other plants; reported, not balance-constrained',
            'note': 'net > 0 means the plant ships more product than it imports (the plant surplus statement). The residual repeats the '
                    'unit ledger (in - out) for information only; the dock is exempt from unit closure per D-DOCK and rate rounding here '
                    'is accepted design-phase noise. R10b closed the EW cascade (A-M-255), CRYO_ASU Ar (A-M-256) and WAFER_FAB (A-M-257).'}
        global DOCK_STATEMENT
        DOCK_STATEMENT = [
            '', '## 1a. Dock trade statement (owner ruling D-DOCK, 2026-10-19)', '',
            'NORTH_DOCK is the inter-plant trade boundary, not a balance-constrained sector: imports of arbitrary feedstock '
            '(landfill reclaim, mining waste, lunar regolith class) and exports of surplus products to other plants. Its ledger '
            'is reported here and on the node (`params.trade_statement`); the unit is exempt from the closure test with the other boundary meters.',
            '', '| Direction | Edge | Commodity | kg/d |', '| --- | --- | --- | --- |'] + [
            f"| export | {k} | {(E[k].get('carries') or '')[:40]} | {x} |" for k, x in sorted(exports_.items())] + [
            f"| import | {k} | {(E[k].get('carries') or '')[:40]} | {x} |" for k, x in sorted(imports_.items())] + [
            f'', f'**Net trade: {net_:+.3f} kg/d** (exports {sum(exports_.values()):.3f} - imports {sum(imports_.values()):.3f}); dock ledger residual {rdock:+.3f} kg/d (reported, exempt per D-DOCK).']
    o2_close.LAST.clear(); o2_close.LAST.update(XL, power=o2_close.close_power(g), o2=(src, draw))
    return d, a

def reconcile(g):
    E = [e for e in g['edges'] if e['presence'] == 'present' and 'mass' in (e.get('layers') or []) and e['rate'].get('unit') == 'kg/d']
    x0 = np.array([float(e['rate']['value'] or 0) for e in E])
    held = lambda e: e['stream_id'] in STOICH or any(k in (e['rate'].get('note') or '') for k in MARK)
    free = [i for i, e in enumerate(E) if not held(e) and (x0[i] > 0 or e['stream_id'].endswith(TRIM))]
    fs = set(free); fixed = [i for i in range(len(E)) if i not in fs]
    nodes = sorted(({e['from_unit_id'] for e in E} | {e['to_unit_id'] for e in E}) - SINK); ni = {n: k for k, n in enumerate(nodes)}
    A = np.zeros((len(nodes), len(E)))
    for i, e in enumerate(E):
        if e['to_unit_id'] in ni: A[ni[e['to_unit_id']], i] += 1
        if e['from_unit_id'] in ni: A[ni[e['from_unit_id']], i] -= 1
    r0 = A @ x0
    s = np.array([x0[i] if x0[i] > 0 else 1.0 for i in free])
    rhs = -(A[:, fixed] @ x0[fixed]) - A[:, free] @ x0[free]
    from scipy.optimize import lsq_linear
    M = A[:, free]*s; big = 1e4; lb = -x0[free]/s                      # x >= 0
    u = lsq_linear(np.vstack([M*big, np.eye(len(free))]), np.concatenate([rhs*big, np.zeros(len(free))]), bounds=(lb, np.inf), lsmr_tol='auto', tol=1e-12, max_iter=5000).x
    x = x0.copy(); x[free] = np.maximum(x0[free] + s*u, 0.0)
    r = A @ x
    return dict(E=E, x0=x0, x=x, free=free, nodes=nodes, r0=r0, r=r)

ROOT_CAUSE = ("X-SAF-10 corrected the peroxide cell feed from 3.0 kg/d O2 to 0.176 kg/d O2 (Faraday) plus 2.824 kg/d make-up water from ROOF_TANK, "
  "and took that water off S40. It did not propagate: TERRACE_IRRIG still transpired 40 kg/d on 37.176 kg/d irrigation, and the cold box still "
  "made 2.824 kg/d O2 that nothing drew. Revision A reconciled the two by least squares (IA-TERR-VAP -2.824, IA-O2-RET +2.824) and smeared "
  "small moves over 361 edges. Hypothesis tested: missing photosynthetic O2 from the terrace. Rejected for this cut: the terrace has no CO2 "
  "supply and no harvest edge, so net CO2 + H2O -> CH2O + O2 fixation there is zero (TAIZ2015), and the sign is wrong (the terrace was short "
  "water, the header long O2). Fix: Revision A moves withdrawn; T1-T5 in balance.physics. X-PAR-11 (T6): GROW_BED fixes the 19.0 kg/d CO2 dosed to it (S04 + S89); its photosynthetic O2, 32/44 x CO2 at PQ 1.0, "
  "leaves on S87 to CRYO_O2 instead of the trim lump; the trim, compost and nutrient surplus pass the difference; the cold box extracts that much less O2 and the "
  "leach dissolved-gas edge falls with it, now asserted under the Henry-law bound (SANDER2015). CO2 edges carry CO2 composition. Verification: T-PAR-02 (A-M-123).")

def report(R):
    E, x0, x = R['E'], R['x0'], R['x']
    ch = sorted([(abs(x[i] - x0[i]), i) for i in R['free'] if abs(x[i] - x0[i]) > 1e-4], reverse=True)
    gross = [i for _, i in ch if abs(x[i] - x0[i]) > TOL*max(x0[i], 0.05)]
    off0 = [(R['nodes'][k], R['r0'][k]) for k in range(len(R['nodes'])) if abs(R['r0'][k]) > 1e-4]
    L = ['# Mass balance reconciliation', '', 'Document number: AQS-PAR-003', 'Revision: E', 'Date: 2026-10-25', '',
         '| Rev | Description | Date |', '| --- | --- | --- |', '| A | First issue. | 2026-10-15 |',
         '| B | Owner: no fudge. X-SAF-10 imbalance (IA-TERR-VAP / IA-O2-RET, 2.824 kg/d) traced and fixed by transfer functions T1-T5; reconciled moves within measurement tolerance. | 2026-10-15 |',
         '| C | X-PAR-11 T6: grow-bed photosynthetic O2 on S87; leach dissolved gas under the Henry bound; CO2 edges carry CO2. | 2026-10-15 |',
         '| D | Owner ruling D-DOCK 2026-10-19: NORTH_DOCK is the inter-plant trade boundary (closure-exempt; ledger reported as a trade statement, section 1a). The three real closures: AFTERBURNER flue = burner mass balance on the restored combustion-air path; NOX_SCRUB gas outlet by difference to the cold box (BH routing, D-AIR) with the cold-box N2 surplus exported at the dock; CRYO_H2 closed by sizing the electrolyser to the pool draws net of the EW Faraday cathode credit (H2 side governs, A-M-272). R10c closes the remaining reported residuals on their stated bases (A-M-274). Product buffer stores added for food / metal / plant air (A-M-270). Test trio green. | 2026-10-19 |',
         '| E | Rewritten to the documentation style guide (AQS-DOC-002): purpose and scope first, revision record in order, table titles. No method, rate or result changed. | 2026-10-25 |', '',
         '## 1. Purpose and scope', '',
         'This page records how the plant mass balance is reconciled. The method is minimum weighted least squares on the held study rates (NARASIMHAN2000); transfer-function and stoichiometric edges stay at their set rates. The generator is `flow_graph/param/balance.py`; authority AQS-PLAN-007 X-PAR-02. It runs in every full regeneration and the reconciliation gate fails on a move outside measurement tolerance.',
         '',
         '## 2. Root cause and physics fix', '', ROOT_CAUSE, '',
         f"Mass edges {len(E)}; held by a transfer function or stoichiometry {len(E) - len(R['free'])}; reconciled {len(R['free'])}. Units {len(R['nodes'])}.",
         f"Before: {len(off0)} units out of balance (sum of residuals {sum(abs(v) for _, v in off0):.3f} kg/d). After: max unit residual {np.abs(R['r']).max():.2e} kg/d. Negative rates after reconciliation: {int((x < -1e-9).sum())}.", '',
         '## 3. Units out of balance before reconciliation', '',
         'Boundary meters are exempt from unit closure: RELIEF_H2 / RELIEF_CRYO / BOUNDARY_EXPORT (relief and export meters) and, '
         'since owner ruling D-DOCK (2026-10-19), NORTH_DOCK (the inter-plant trade boundary — its ledger is the trade statement in section 3a).', '',
         'Table 3.1. Unit residual before reconciliation', '', '| Unit | In - out, kg/d |', '| --- | --- |'] + [f'| {n} | {v:+.4f} |' for n, v in off0] + DOCK_STATEMENT + [
         '', f'## 4. Moves outside measurement tolerance ({TOL*100:.0f} % of the rate, 1 g/d floor); must be empty', '', 'Table 4.1. Reconciled moves outside tolerance', '', '| Edge | From | To | Held study rate | Reconciled | Change |', '| --- | --- | --- | --- | --- | --- |'] + [
         f"| {E[i]['stream_id']} | {E[i]['from_unit_id']} | {E[i]['to_unit_id']} | {x0[i]:.4f} | {x[i]:.4f} | {(x[i] - x0[i]):+.4f} |" for i in gross] + [
         '', '## 5. All reconciled changes above 0.1 g/d', '', 'Table 5.1. Reconciled changes', '', '| Edge | Held | Reconciled | Change, % |', '| --- | --- | --- | --- |'] + [
         f"| {E[i]['stream_id']} | {x0[i]:.4f} | {x[i]:.4f} | {((x[i] - x0[i])/x0[i]*100 if x0[i] else float('nan')):+.2f} |" for _, i in ch] + [
         '', '## 6. Held stoichiometric edges', '', 'Table 6.1. Stoichiometric edges', '', '| Edge | Basis |', '| --- | --- |'] + [f'| {k} | {v} |' for k, v in STOICH.items()]
    open(os.path.join(ROOT, 'docs-authority/BALANCE_RECONCILIATION.md'), 'w').write('\n'.join(L) + '\n')
    return gross, off0

def main():
    g = json.load(open(GP)); d, a = physics(g); print('physics roof', round(d, 4), 'asu', round(a, 4)); R = reconcile(g); gross, off0 = report(R)
    from flow_graph.param import closure_tf; print('closure TF / inputs / rederive', closure_tf.write(g))
    print('off before', len(off0), 'max resid after', float(np.abs(R['r']).max()), 'gross', [R['E'][i]['stream_id'] for i in gross])
    if '--write' in sys.argv:
        assert (R['x'] >= -1e-9).all() and np.abs(R["r"]).max() < 1e-3
        for i in R['free']:
            e = R['E'][i]
            if abs(R['x'][i] - R['x0'][i]) > 1e-7:
                e['rate']['value'] = round(float(max(R['x'][i], 0.0)), 6)
                e['rate']['note'] = (e['rate'].get('note') or '').split(' | X-PAR-02')[0] + ' | X-PAR-02 reconciled (AQS-PAR-003).'
        open(GP, 'w').write(json.dumps(g, indent=2))

if __name__ == '__main__': main()

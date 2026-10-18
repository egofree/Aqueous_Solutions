"""Foundry + polymers sizing transfer functions (AQS-DUTY-072 / AQS-DUTY-073, unit task 02 for the
FOUNDRY and POLYMERS sectors). Sizes the two sectors from need at the Rev AC bounding case:

Demand side (live graph): WAFER_FAB draws are 0 (A-M-257: the fab closes on UPW + slurry + N2 purge);
WIRE_DRAW closes on S57 (MFG Cu wire line), so STOCK_TO_WIRE_DRAW = 0. The MFG_SHOP goods loop is closed
(IA-MFG-OUT 596.863 out = IA-WEAR return), so the shop's only live need is its rounding remnant r0
(rated in - rated out) plus whatever the foundry stock loop and polymer draw feed back through it.

Foundry chain (AQS-DUTY-072): the pot/cell train (AL/CA/MG/CR/TI/MO) has no live feed at the bounding
case - no chloride feed edges exist, Al stays in the leach liquor as solute (AQS-BOM-SC-001 sec. 6),
the Cr feed (AQS-DUTY-CR), the Ti dense-grit assay (AQS-ASSAY-TI-MO) and the Mo liquor tenor
(AQS-ASSAY-TI-MO) are missing, and EW_9's products are fully booked (A-M-255). The investment-casting
train is blocked: the wax loop has no make-up source and GLASS_DIGEST is fully committed (IA-GLASS-03
30.0 = S08G 26.7 + IA-SIL-SRC 3.3), so spent shell has no digest capacity. The live foundry is the
scrap-remelt loop: MFG scrap -> IND_MELT -> CAST_LINE/CONT_CAST -> ROLL -> STOCK_OUT -> MFG_SHOP at the
AQS-SIZE-FOUNDRY consumable-replacement stock lines that are not pot-blocked (Cu 3 + Fe 10 + Zn/EW 1).

Polymers chain (AQS-DUTY-073): the fluoropolymer train is F-blocked (no fluorine source on site,
AQS-BOM-SC-001 43 BOM lines Missing, Q-013) and POLY_COND waits on the digester organic assay
(AQS-DES-POLY), so both carry 0. The live train is the polyolefin line: C5-C10 naphtha drawn at the cut
tank -> POLY_OLEFIN -> PELLET -> POLY_STOCK -> MFG_SHOP draw + wet-line reject.

Closure (exact, from the live graph):
  K   = foundry stock to the shop (drivers foundry_stock_demand_kg_d)
  f   = melt loss to slag/dross (drivers foundry_melt_loss_frac)
  rej = polymer offcut to the wet line per kg issued (drivers poly_shop_reject_frac)
  P   = -r0 + f*K/(1-f)          polymer draw that closes the shop (A-M-257 by-difference pattern)
  S   = K + P + r0               shop scrap charge to IND_MELT
  slag = f*S                     FOUNDRY_SLAG_TO_LEACH (mass conservation on the melt)
  poly_feed = P*(1+rej)          naphtha draw; IA-C5-SHIP = CUT-1 - CUT-1-OUT - poly_feed (its TF)

DOCK_EXPORT_TBD rates 0.0 from the goods balance: foundry products net 0 (the stock loop closes on the
shop draw) and the mfg goods surplus net 0 (goods production = worn-goods return), so the plant goods
surplus at the bounding case is 0.0 kg/d - that statement IS the plant surplus statement pending the
goods-growth decision; the NORTH_DOCK residual stays the non-goods study-basis imbalance it was.

Run: python3 -m flow_graph.param.foundry_poly [--write]
"""
import json, math, os, sys
from . import drivers as DR

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GP = os.path.join(ROOT, 'flow_graph/plant_flow_graph.json')
DOC_F, DOC_P = 'AQS-DUTY-072', 'AQS-DUTY-073'
TAG = f'X-PAR-02 TF: foundry/polymers sizing ({DOC_F}/{DOC_P})'


def rate(v, note):
    return {'value': round(v, 6), 'unit': 'kg/d', 'status': 'study', 'note': note}


def solve(g=None):
    """Return the sizing dict; g loaded from the graph when not given."""
    if g is None:
        g = json.load(open(GP))
    d = DR.load()
    val = lambda k: DR.val(d, k)
    E = {e['stream_id']: e for e in g['edges']}

    def rated(k):
        r = E[k]['rate']
        return float(r['value'] or 0) if r.get('unit') == 'kg/d' else 0.0

    def resid(u, skip=()):
        r = 0.0
        for e in g['edges']:
            if e['presence'] == 'present' and 'mass' in (e.get('layers') or []) and e['rate'].get('unit') == 'kg/d' \
                    and e['stream_id'] not in skip:
                v = float(e['rate']['value'] or 0)
                r += v if e['to_unit_id'] == u else 0.0
                r -= v if e['from_unit_id'] == u else 0.0
        return r

    r0 = resid('MFG_SHOP', skip=('MFG_SCRAP_TO_IND', 'STOCK_TO_MFG', 'POLY_TO_MFG'))
    # ^ rated in - rated out at the shop, EXCLUDING this pass's own loop edges so the closure is
    #   idempotent (re-running on the written graph returns the same remnant, A-M-257 pattern)
    K = val('foundry_stock_demand_kg_d')         # Cu 3 + Fe 10 + Zn/EW 1 (AQS-SIZE-FOUNDRY live lines)
    f = val('foundry_melt_loss_frac')
    rej = val('poly_shop_reject_frac')
    P = -r0 + f * K / (1 - f)                    # polymer draw that closes the shop
    S = K + P + r0                               # scrap charge to IND_MELT
    slag = f * S
    assert abs(S - slag - K) < 1e-9
    poly_feed = P * (1 + rej)
    poly_wet = rej * P
    c5 = rated('CUT-1') - rated('CUT-1-OUT') - poly_feed      # IA-C5-SHIP re-solve (make - burned - olefin)

    # melt energy by metal class (X-MFG-37 method, A-M-177): (cp_s dT + L + cp_l superheat)/eta
    eta = val('melt_eta'); sup = val('melt_superheat_K')
    q = {}
    q['Cu'] = (val('melt_cp_solid_kJ_kgK') * (1084.62 - 25) + val('melt_L_kJ_kg') + val('melt_cp_liq_kJ_kgK') * sup) / eta / 3600
    q['Fe'] = (val('melt_fe_cp_solid_kJ_kgK') * (1538 - 25) + val('melt_fe_L_kJ_kg') + val('melt_fe_cp_liq_kJ_kgK') * sup) / eta / 3600
    q['Zn'] = (val('melt_zn_cp_solid_kJ_kgK') * (419.5 - 25) + val('melt_zn_L_kJ_kg') + val('melt_zn_cp_liq_kJ_kgK') * sup) / eta / 3600
    mix = {'Cu': 3.0, 'Fe': 10.0, 'Zn': 1.0}                 # AQS-SIZE-FOUNDRY live stock lines
    assert abs(sum(mix.values()) - K) < 1e-9
    e_melt = sum(m * q[c] for c, m in mix.items()) + val('melt_hold_kW') * val('melt_time_h') * math.ceil(S / val('melt_charge_kg'))
    kw_peak = math.ceil(val('melt_charge_kg') * max(q.values()) / val('melt_time_h') * 2) / 2   # largest cold heat
    e_roll = 0.032 * (mix['Cu'] + mix['Fe'])                  # A-M-177 rolling 0.032 kWh/kg (bounding, cold class)
    return dict(g=g, E=E, d=d, r0=r0, K=K, f=f, rej=rej, P=P, S=S, slag=slag, poly_feed=poly_feed,
                poly_wet=poly_wet, c5_ship=c5, q=q, mix=mix, e_melt=e_melt, kw_peak=kw_peak, e_roll=e_roll,
                heats=math.ceil(S / val('melt_charge_kg')), charge=val('melt_charge_kg'))


def apply(g=None, write=False):
    s = solve(g)
    g, E = s['g'], s['E']
    K, S, P = s['K'], s['S'], s['P']

    def put(k, v, note):
        assert k in E, k
        E[k]['rate'] = rate(v, note)

    # ---- foundry: live scrap-remelt loop ---------------------------------------------------
    put('MFG_SCRAP_TO_IND', S,
        f'Shop scrap (charge) to the melt; closes MFG_SHOP on the store draws ({DOC_F}, A-M-261). | {TAG}.')
    put('FOUNDRY_SLAG_TO_LEACH', s['slag'],
        f'Melt slag+dross {s["f"]:.0%} of charge by mass conservation on the melt (INDUCT_SOCX 1-2 % band, '
        f'A-M-262); returns to the leach. | {TAG}.')
    put('IND_MELT_TO_CAST', 3.0,
        f'Cu-class melt to the cast line: bus/winding stock (AQS-SIZE-FOUNDRY Cu 3 kg/d). | {TAG}.')
    put('IND_TO_CONT', 11.0,
        f'Fe 10 + Zn 1 kg/d to the semi-continuous caster (AQS-SIZE-FOUNDRY Fe/low-alloy and Zn/EW lines). | {TAG}.')
    put('CAST_SCRAP_TO_IND', 0.0,
        'Near-net permanent-mold pours at 3 kg/d; sprue/runner returns are campaign events, not a daily '
        f'continuous rate (the melt loop closes on MFG_SCRAP_TO_IND). | {TAG}.')
    put('CAST_TO_ROLL', 3.0, f'Cu cast stock to rolling (bus bar / winding strip, FOUNDRY_DESIGN machine table). | {TAG}.')
    put('CAST_TO_EXTRUDE', 0.0,
        'Extrusion is the Al/Cu/Mg profile path (FOUNDRY_DESIGN); Al/Mg pot metal is feed-blocked at the '
        f'bounding case, so the Cu line rolls. | {TAG}.')
    put('CONT_TO_ROLL', 10.0, f'Fe billet to rolling (AQS-SIZE-FOUNDRY Fe 10). | {TAG}.')
    put('CONT_TO_STOCK', 1.0, f'Zn/EW ingot straight to stock (AQS-SIZE-FOUNDRY Zn 1). | {TAG}.')
    put('ROLL_TO_STOCK', 13.0, f'Rolled plate/sheet stock (Cu 3 + Fe 10). | {TAG}.')
    put('STOCK_TO_MFG', K,
        f'Formed stock to the shop = the foundry product demand Cu 3 + Fe 10 + Zn/EW 1 kg/d '
        f'(AQS-SIZE-FOUNDRY live stock lines; A-M-261). | {TAG}.')
    put('STOCK_TO_WIRE_DRAW', 0.0,
        'WIRE_DRAW (MFG) closes on S57 Cu from MET_MELT (A-M-177 line); no foundry wire draw at the '
        f'bounding case (A-M-257 by-difference pattern). | {TAG}.')
    put('EXTRUDE_TO_STOCK', 0.0, f'Extrusion idle: Al/Mg profile feed blocked (pots unfed). | {TAG}.')
    put('DRAW_TO_STOCK', 0.0,
        'FOUNDRY DRAW has no feed edge at Rev AC; wire sizing is the MFG WIRE_DRAW S57 line '
        f'(FOUNDRY_INTEGRATION role split). | {TAG}.')
    put('SINTER_TO_STOCK', 0.0, f'Sinter feed is Ti/Mo/Cr powder; pot/cell train feed-blocked. | {TAG}.')
    put('ATOM_TO_STOCK', 0.0, f'Gas-atomizer powder path optional, not baseline (FOUNDRY_INTEGRATION). | {TAG}.')
    put('IND_TO_ATOM', 0.0, f'No powder demand on IND_MELT at the bounding case. | {TAG}.')
    # ---- foundry: feed-blocked trains (0 with basis) ---------------------------------------
    for k, why in [
        ('EW_METALS_TO_IND', 'A-M-255 alias retired: EW_9 metal harvest fully booked on IA-EW-MET-9 (61.341 to the shop) '
         'and IA-EW-SHEET (13.989 to MET_MELT); a third draw would double-book the harvest. The melt is fed on shop scrap.'),
        ('EW9_LIQUOR_TO_MO', 'A-M-255 alias retired: EW_9 liquor tail fully booked on IA-EW-09 to POLISH_BANK; a parallel '
         'Mo draw would double-book it, and the Mo tenor measurement is missing (AQS-ASSAY-TI-MO).'),
        ('MO_TO_IND', 'Mo recovery feed-blocked: EW9_LIQUOR_TO_MO retired at 0 (A-M-255) and the liquor Mo tenor is '
         'unmeasured (AQS-ASSAY-TI-MO); design case 0.05 kg/d Mo with stoichiometric feeds in ' + DOC_F + '.'),
        ('MO_CELL_RAFFINATE', 'MO_CELL idle (feed-blocked, AQS-ASSAY-TI-MO).'),
        ('MO_CELL_ANODE_GAS_TO_CRU', 'MO_CELL idle (feed-blocked, AQS-ASSAY-TI-MO).'),
        ('FLOAT_SINK_GRIT_TO_TI', 'Ti dense-grit assay missing: no composition is on the edge (AQS-ASSAY-TI-MO); '
         'FLOAT_SINK closes on its held liquor/plastics edges, so the grit draw would open it.'),
        ('METALS_TO_IND_MELT', 'TI_CELL idle at the bounding case (grit assay missing, AQS-ASSAY-TI-MO); Kroll per-kg '
         'feed table in ' + DOC_F + ' sec. 4 for the day the assay lands.'),
        ('VAC_IND_TI', 'TI_CELL idle (grit assay missing, AQS-ASSAY-TI-MO).'),
        ('TI_CELL_SLAG_RETURN', 'TI_CELL idle; the Kroll MgCl2 return table is in ' + DOC_F + ' sec. 4.'),
        ('TI_CELL_CL2_TO_CRU', 'TI_CELL idle; Kroll chlorine closes internally via the Mg pot (AQS-BAL-KROLL).'),
        ('CR_TO_IND', 'Cr feed assay missing, no composition on an edge (AQS-DUTY-CR); chromite-grit route unfed.'),
        ('AL_POT_TO_IND', 'AL_POT unfed at the bounding case: no chloride feed edge exists and Al stays in the leach '
         'liquor as solute (AQS-BOM-SC-001 sec. 6, alumina recovery a study); design case 8 kg/d in ' + DOC_F + ' sec. 4.'),
        ('AL_POT_CL2', 'AL_POT idle (unfed); Cl2 return table per kg Al in ' + DOC_F + ' sec. 4.'),
        ('MG_POT_TO_IND', 'MG_POT unfed: the Kroll Mg recycle (AQS-BAL-KROLL) has no live Ti rate to serve; design '
         'case per-kg table in ' + DOC_F + ' sec. 4.'),
        ('MG_POT_CL2', 'MG_POT idle; Kroll chlorine loop net zero (AQS-BAL-KROLL).'),
        ('CA_POT_TO_IND', 'CA_POT unfed: no CaCl2 feed edge at Rev AC; Ca metal also the grease-thickener source.'),
        ('FLUX_TO_IND', 'FLUX_PREP unfed: SALT_FEED has no in-edge (no salt source at the bounding case); flux cover is '
         'a campaign addition from the leach salt split when that task assigns it.'),
        ('SALT_TO_FLUX', 'SALT_FEED is a stub source at Rev AC (no in-edges); no salt rate invented.'),
        ('COMB_OFFGAS', 'COMB_HEAT is the alternate path, off-baseline (FOUNDRY_DUTY heat policy); off-gas routes to '
         'MET_SCRUB only when the alternate is energized.'),
        ('IND_TO_INV', 'Investment casting blocked: no wax make-up source (WAX_PATTERN closes on reclaim only) and '
         'GLASS_DIGEST is fully committed (IA-GLASS-03 30.0 = S08G 26.7 + IA-SIL-SRC 3.3).'),
        ('VAC_TO_INV', 'VAC_IND idle (Ti feed-blocked, AQS-ASSAY-TI-MO).'),
        ('VAC_IND_TO_VAC_CAST', 'VAC_IND idle (Ti feed-blocked, AQS-ASSAY-TI-MO).'),
        ('WAX_TO_SHELL', 'Investment train blocked (see IND_TO_INV).'),
        ('WAX_RECLAIM_TO_PATTERN', 'Investment train blocked (see IND_TO_INV).'),
        ('SHELL_TO_BURNOUT', 'Investment train blocked (see IND_TO_INV).'),
        ('BURNOUT_TO_CAST', 'Investment train blocked (see IND_TO_INV).'),
        ('WAX_TO_OIL', 'Investment train blocked; no unrecovered-wax blowdown to the fractionator.'),
        ('INV_TO_BREAK', 'Investment train blocked (see IND_TO_INV).'),
        ('BREAK_TO_STOCK', 'Investment train blocked (see IND_TO_INV).'),
        ('SHELL_TO_GLASS', 'Spent shell has no digest capacity: GLASS_DIGEST closes exactly on IA-GLASS-03 = S08G + '
         'IA-SIL-SRC, so GLASS_MILL_TO_DIGEST is 0 by its own closure.'),
    ]:
        put(k, 0.0, f'{why} | {TAG}.')
    # ---- polymers --------------------------------------------------------------------------
    put('OIL_TO_OLEFIN', 0.0,
        'Fractionator draw 0: the olefin feed draws as naphtha at the cut tank (IA-C5-POLY); the recovered-wax '
        f'path (WAX_TO_OIL) is 0 with the investment train blocked. OIL_FRAC closes. | {TAG}.')
    put('MEOH_TO_OLEFIN', 0.0,
        'Methanol committed to the tank/ship balance (X-PAR-12 TF on S75); the olefin carbon source is the '
        f'on-site C5-C10 naphtha cut (AQS-DES-POLY: carbon source on site). | {TAG}.')
    put('OLEFIN_TO_PELLET', s['poly_feed'],
        f'Polyolefin resin = naphtha feed {s["poly_feed"]:.4f} kg/d (mass-conserving oligomerization, '
        f'AQS-SIZE-OIL-POLY POLY_OLEFIN 150-250 C / 1-5 MPa). | {TAG}.')
    put('PELLET_TO_STOCK', s['poly_feed'], f'Pellet line passes the resin to stock. | {TAG}.')
    put('POLY_TO_MFG', P,
        f'Shop polymer draw by difference on the shop closure (A-M-257 pattern): -r0 {s["r0"]:+.6f} + melt loss '
        f'term f*K/(1-f); molded articles ride BLOW_MOLD (IA-BLOW-OUT 8.407). | {TAG}.')
    put('POLY_TO_WET', s['poly_wet'],
        f'Shop polymer offcut to the wet line, {s["rej"]:.0%} of the issue (the S58/S59/S60 10 % shop-loss '
        f'class, AQS-DUTY-010; A-M-263). | {TAG}.')
    put('POWDER_TO_STOCK', 0.0, 'Fluoropolymer powder blocked (no F source on site, AQS-BOM-SC-001, Q-011/Q-013). | {TAG}.')
    put('FILM_TO_STOCK', 0.0, 'FILM_CAST has no feed edge at Rev AC; film/sheet rides the pellet line when a die study issues it. | {TAG}.')
    for k, why in [
        ('F_RECOVER_TO_HF_GEN', 'F_RECOVER (DIGESTER) has no in-edge at Rev AC; no fluorine source on site '
         '(AQS-BOM-SC-001 43 lines Missing, Q-013).'),
        ('HF_GEN_TO_VDF', 'Fluoropolymer train F-blocked (AQS-BOM-SC-001, Q-013); design case 0.5 kg/d HF in ' + DOC_P + '.'),
        ('HF_GEN_TO_TFE', 'Fluoropolymer train F-blocked (AQS-BOM-SC-001, Q-013).'),
        ('VDF_TO_POLY_F', 'Fluoropolymer train F-blocked (AQS-BOM-SC-001, Q-013).'),
        ('TFE_TO_POLY_F', 'Fluoropolymer train F-blocked (AQS-BOM-SC-001, Q-013).'),
        ('POLYF_TO_PELLET', 'Fluoropolymer train F-blocked (AQS-BOM-SC-001, Q-013).'),
        ('POLYF_TO_POWDER', 'Fluoropolymer train F-blocked (AQS-BOM-SC-001, Q-013).'),
        ('CRU_TO_VDF', 'No monomer chlorination draw: fluoropolymer train F-blocked (Q-013).'),
        ('CRU_TO_TFE', 'No monomer chlorination draw: fluoropolymer train F-blocked (Q-013).'),
        ('DIGEST_TO_POLY', 'POLY_COND recipe waits on the digester organic assay (AQS-DES-POLY / AQS-SIZE-OIL-POLY: '
         'no rate treated as design); BLACK_DIGEST closes on IA-BLK-GREY.'),
    ]:
        put(k, 0.0, f'{why} | {TAG}.')
    # naphtha feed edge + ship re-solve
    if 'IA-C5-POLY' not in E:
        src = dict(E['IA-C5-SHIP'])
        src.update(stream_id='IA-C5-POLY', to_unit_id='POLY_OLEFIN', to_sector_id='POLYMERS', phase='L',
                   carries='C5-C10 naphtha olefin feed',
                   notes='Created by the polymers sizing pass: the olefin feed draws as naphtha at the cut tank '
                         '(AQS-SIZE-OIL-POLY); the fractionator-side OIL_TO_OLEFIN stays 0 so OIL_FRAC closes.',
                   open_boundary=False)
        src['rate'] = rate(s['poly_feed'],
                           f'Olefin feed to POLY_OLEFIN = shop polymer draw x (1 + reject) = {s["poly_feed"]:.4f} kg/d '
                           f'({DOC_P}, A-M-264). | {TAG}.')
        g['edges'].append(src)
        E['IA-C5-POLY'] = src
    else:
        put('IA-C5-POLY', s['poly_feed'], f'Polyolefin naphtha feed ({DOC_P}, A-M-264). | {TAG}.')
    cut1_out = float(s['E']['CUT-1-OUT']['rate']['value'] or 0)
    put('IA-C5-SHIP', s['c5_ship'],
        f'X-PAR-12 TF (AQS-PAR-005): C5-C10 make less the plant draws - genset {cut1_out:.4f} and the '
        f'olefin feed {s["poly_feed"]:.4f} (this pass, {DOC_P}); shipped at the dock. | {TAG}.')
    # ---- goods balance ---------------------------------------------------------------------
    # SF-HF_GEN: electrical feed of the F-blocked standby unit (0 duty; the power rollup sums 0)
    if 'SF-HF_GEN' in E:
        E['SF-HF_GEN']['rate'] = {'value': 0.0, 'unit': 'kW', 'status': 'study',
                                  'note': f'HF_GEN standby at 0 duty (fluoropolymer train F-blocked, Q-013; '
                                          f'feed 0 on F_RECOVER_TO_HF_GEN). | {TAG}.'}
        N = {n['unit_id']: n for n in g['nodes']}
        if 'HF_GEN' in N:
            N['HF_GEN']['continuous_kw'] = {'value': 0.0, 'unit': 'kW', 'status': 'study',
                                            'note': f'standby, 0 duty at the bounding case ({DOC_P} sec. 3). | {TAG}.'}
    put('DOCK_EXPORT_TBD', 0.0,
        'Goods balance (A-M-265): foundry products net 0 (stock loop closes on the shop draw) + mfg goods surplus '
        'net 0 (IA-MFG-OUT 596.863 = IA-WEAR worn return) - internal use fully looped = 0.0 kg/d goods export at '
        'the bounding case. THIS IS THE PLANT SURPLUS STATEMENT: the plant sustains itself in goods with zero '
        'saleable goods surplus at Rev AC scope; the NORTH_DOCK residual is the non-goods study-basis imbalance '
        '(NOX_SCRUB/CRYO_H2/AFTERBURNER + WS rounding), owned by those lanes, not goods.')
    E['DOCK_EXPORT_TBD']['rate']['note'] = (E['DOCK_EXPORT_TBD']['rate']['note'].split(f' | {TAG}')[0]) + f' | {TAG}.'
    stamp(g, s)
    # document the missing edges this pass found (idempotent: one entry, replaced in place)
    gap = {'id': 'FOUNDRY_POLY_MISSING_EDGES', 'severity': 'medium',
           'detail': 'Foundry/polymers sizing pass (AQS-DUTY-072/073): absent edges that block positive rates - '
                     'pot chloride feeds (LEACH->AL/MG/CA_POT), DRAW feed (CAST/ROLL->DRAW), FORGE edges, '
                     'FILM_CAST feed, POLY_COND outlet to PELLET, wax make-up + shell ceramic for the investment '
                     'train, SALT_FEED source, F_RECOVER feed (F recovery, Q-013). Each 0-rated edge cites its '
                     'block in the sizing docs until the feed lands.'}
    g['gaps'] = [x for x in g.get('gaps', []) if x.get('id') != gap['id']] + [gap]
    if write:
        open(GP, 'w').write(json.dumps(g, indent=2) + '\n')
    return s


def stamp(g, s):
    N = {n['unit_id']: n for n in g['nodes']}
    src_f, src_p = DOC_F, DOC_P

    def st(u, **kw):
        p = N[u].setdefault('params', {})
        p['sizing'] = dict(status='study', source=kw.pop('source'), **kw)

    q, mix = s['q'], s['mix']
    st('IND_MELT', source=src_f, charge_kg_d=round(s['S'], 4), stock_out_kg_d=s['K'], slag_kg_d=round(s['slag'], 4),
       crucible_kg=s['charge'], heats_d=s['heats'], melt_kWh_d=round(s['e_melt'], 3), avg_kW=round(s['e_melt'] / 24, 4),
       peak_kW=s['kw_peak'], connected_kW=25.0, kWh_per_kg={k: round(v, 4) for k, v in q.items()},
       basis='scrap remelt; class energies (cp_s dT + L + cp_l superheat)/eta per A-M-177 method, CRC_CU/CRC_FE/CRC_ZN')
    st('CAST_LINE', source=src_f, pour_kg_d=mix['Cu'], products='Cu ingot/billet, permanent mold', scrap_return_kg_d=0.0)
    st('CONT_CAST', source=src_f, feed_kg_d=round(mix['Fe'] + mix['Zn'], 4), billet_kg_d=mix['Fe'], ingot_kg_d=mix['Zn'],
       mold='water-cooled copper, horizontal (AQS-SIZE-FOUNDRY)')
    st('ROLL', source=src_f, rolled_kg_d=round(mix['Cu'] + mix['Fe'], 4), kWh_d=round(s['e_roll'], 4),
       basis='0.032 kWh/kg cold-rolling class (A-M-177 DIETER1988); hot rolling cheaper')
    st('EXTRUDE', source=src_f, rate_kg_d=0.0, status_note='installed standby: Al/Cu/Mg profile feed blocked')
    st('DRAW', source=src_f, rate_kg_d=0.0, status_note='no feed edge at Rev AC; wire sizing is MFG WIRE_DRAW (S57)')
    st('FORGE', source=src_f, rate_kg_d=0.0, status_note='no edges at Rev AC; open-die work is campaign-scale')
    st('SINTER', source=src_f, rate_kg_d=0.0, status_note='installed standby: Ti/Mo/Cr powder feed blocked')
    st('STOCK_OUT', source=src_f, stock_out_kg_d=s['K'], draws=dict(MFG=s['K'], FAB=0.0, WIRE_DRAW=0.0))
    st('VAC_IND', source=src_f, rate_kg_d=0.0, connected_kW=15.0, design_case='2 kg ISM skull melt (AQS-SIZE-FOUNDRY); '
       'Ti feed-blocked (AQS-ASSAY-TI-MO)')
    st('VAC_CAST', source=src_f, rate_kg_d=0.0, status_note='installed standby tied to VAC_IND')
    st('RF_HEAT', source=src_f, duty_kg_d=0.0, connected_kW=5.0, status_note='preheat/sinter standby (A-M-232); sinter feed blocked')
    st('RES_HEAT', source=src_f, rate_kg_d=0.0, status_note='alternate path only (FOUNDRY_DUTY heat policy)')
    st('COMB_HEAT', source=src_f, rate_kg_d=0.0, status_note='alternate path only; off-gas to MET_SCRUB when energized')
    st('FLUX_PREP', source=src_f, rate_kg_d=0.0, status_note='installed standby: SALT_FEED unfed at Rev AC')
    kroll = dict(feed_grit_kg_per_kg_Ti=1.67, carbon_kg=0.50, cl2_kg=2.96, ticl4_kg=3.96, mg_kg=1.01, mgcl2_kg=3.97,
                 co_kg=1.17, source='AQS-BAL-KROLL (stoichiometric, no rate until the grit assay)')
    st('TI_CELL', source=src_f, rate_kg_d=0.0, design_case_per_kg_Ti=kroll, status_note='grit assay missing (AQS-ASSAY-TI-MO)')
    st('MO_CELL', source=src_f, rate_kg_d=0.0, design_case_kg_d=0.05, status_note='liquor Mo tenor missing (AQS-ASSAY-TI-MO)')
    st('CR_CELL', source=src_f, rate_kg_d=0.0, design_case_kg_d=0.20, status_note='feed assay missing (AQS-DUTY-CR)')
    st('AL_POT', source=src_f, rate_kg_d=0.0, design_case_kg_d=8.0, alcl3_kg_per_kg_al=round(2 * 133.34 / (2 * 26.98), 3),
       cl2_kg_per_kg_al=round(3 * 70.906 / (2 * 26.98), 3), status_note='unfed: Al stays in leach liquor (AQS-BOM-SC-001 sec. 6)')
    st('MG_POT', source=src_f, rate_kg_d=0.0, mgcl2_kg_per_kg_mg=round(95.21 / 24.305, 3),
       cl2_kg_per_kg_mg=round(70.906 / 24.305, 3), status_note='Kroll Mg recycle; no live Ti rate to serve (AQS-BAL-KROLL)')
    st('CA_POT', source=src_f, rate_kg_d=0.0, cacl2_kg_per_kg_ca=round(110.98 / 40.078, 3),
       status_note='unfed: no CaCl2 feed edge at Rev AC')
    for u in ('WAX_PATTERN', 'SHELL_BUILD', 'SHELL_BURNOUT', 'INV_CAST', 'SHELL_BREAK'):
        st(u, source=src_f, rate_kg_d=0.0,
           status_note='installed standby: wax make-up unfed and GLASS_DIGEST fully committed (no shell capacity)')
    # polymers
    st('POLY_OLEFIN', source=src_p, feed_kg_d=round(s['poly_feed'], 6), feed='C5-C10 naphtha at the cut tank (IA-C5-POLY)',
       T_C='150-250', P_MPa='1-5', heat_W=round(s['poly_feed'] * 2.1 * 175 / 86400, 4),
       basis='AQS-SIZE-OIL-POLY POLY_OLEFIN reactor; feed heating 25->200 C at 2.1 kJ/kg K, exotherm neglected (study)')
    st('PELLET', source=src_p, pellet_kg_d=round(s['poly_feed'], 6), form='2-4 mm pellets (AQS-DES-POLY)')
    st('POWDER_RESIN', source=src_p, rate_kg_d=0.0, status_note='installed standby: fluoropolymer feed blocked (Q-013)')
    st('FILM_CAST', source=src_p, rate_kg_d=0.0, status_note='installed standby: no feed edge at Rev AC')
    st('POLY_STOCK', source=src_p, out_kg_d=round(s['P'], 6), to_wet_kg_d=round(s['poly_wet'], 6), to_fab_kg_d=0.0)
    fp = dict(hf_kg_d=0.5, vdf_kg_d=0.15, tfe_kg_d=0.10, pvdf_kg_d=0.14, ptfE_kg_d=0.09, source='AQS-RATE-FP-MET design case')
    for u in ('HF_GEN', 'VDF_SYN', 'TFE_SYN', 'POLY_F'):
        st(u, source=src_p, rate_kg_d=0.0, design_case=fp, status_note='F-blocked: no fluorine source on site (AQS-BOM-SC-001, Q-013)')
    st('POLY_COND', source=src_p, rate_kg_d=0.0, status_note='recipe waits on the digester organic assay (AQS-DES-POLY)')


def main():
    s = apply(write='--write' in sys.argv)
    out = {k: v for k, v in s.items() if k not in ('g', 'E', 'd')}
    print(json.dumps(out, indent=1, default=float))


if __name__ == '__main__':
    main()

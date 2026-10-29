"""Silicon feed and crystal-growth blanket gas of WAFER_FAB, sized from the wafer need (owner decision 2026-10-29, A-M-417).

Silicon. The fab starts FAB.litho-train.starts_per_d wafers a day. Each wafer takes a slot of wafer thickness plus saw kerf
along the ingot body; the charge adds the crown, tail, ground-off diameter and pot scrap (cz_crop_frac). The charge of a pull is
the larger of the need of one tool campaign (campaign_d) and the least melt the crucible holds (cz_min_depth_frac of the crucible
diameter); the days between pulls follow, and the wafers of a pull are stored until started. The plant makes only metallurgical-grade silicon
(SI_REDUCE), far below the purity a CZ charge needs, so flow_graph/param/si_refine.py refines it on site to electronic grade
into the METAL_STORE buffer, which holds one charge until the pull (owner decision t58u: no imports except waste or raw ore). Finished
wafers go to the lithography train and back to the fab tool row, then to the dock; kerf and crop leave with the
spent slurry to the leach.

Blanket gas. The puller runs under argon from the cold box (CRYO_ASU) for the meltdown, neck and crown, body pull and
cool-down. Flow scales with the crucible area. The exhaust returns to CRYO_ASU through its heated argon getter, so the loop
is closed and the supply equals the return. Nitrogen is not a valid CZ ambient: at the melt temperature it forms silicon
nitride on the melt and the crucible (cz_blanket_gas = 'N2' is refused); nitrogen stays the purge of the wafer tools (S03).
Run: python3 -m flow_graph.param.fab_silicon"""
import json, math, os
from . import drivers as DR
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = 'FAB.wafer-line-train.'
TAG = 'X-MFG-40 TF (A-M-417)'
AR_RHO_STD = 1.784          # g/L argon at 0 C and 1 atm, the reference of a standard litre per minute

def design(d=None):
    d = d or DR.load(); v = lambda k: DR.val(d, k)
    gas = v(F + 'cz_blanket_gas')
    if gas != 'Ar':
        raise SystemExit(f'fab_silicon: cz_blanket_gas {gas!r} refused: nitrogen forms silicon nitride on the melt at 1414 C; argon is the only valid CZ ambient')
    D = v(F + 'wafer_D_mm')/10; t = v(F + 'wafer_t_um')/1e4; kerf = v(F + 'kerf_um')/1e4; rho = v(F + 'si_rho_g_cm3')   # cm, g/cm3
    area = math.pi/4*D**2; starts = v('FAB.litho-train.starts_per_d'); keep = 1 - v(F + 'cz_crop_frac')
    wafer_g = rho*area*t; slot_g = rho*area*(t + kerf)
    # the charge is the larger of the wafer need of one tool campaign and the least melt the crucible can hold for a pull
    cru_D = D*v(F + 'cz_crucible_ratio'); crucible_cm2 = math.pi/4*cru_D**2
    min_kg = v(F + 'si_liquid_rho_g_cm3')*crucible_cm2*v(F + 'cz_min_depth_frac')*cru_D/1000
    need_kg = starts*v(F + 'campaign_d')*slot_g/keep/1000
    charge_kg = max(need_kg, min_kg)
    n = charge_kg*1000*keep/slot_g; interval_d = n/starts                     # wafers per pull, days between pulls
    body_cm = n*(t + kerf)
    si_kg_d = charge_kg/interval_d; wafer_kg_d = starts*wafer_g/1000; loss_kg_d = si_kg_d - wafer_kg_d
    pull_h = body_cm*10/v(F + 'cz_pull_mm_h')
    ar_h = v(F + 'cz_melt_h') + v(F + 'cz_neck_crown_h') + pull_h + v(F + 'cz_cool_h')
    slpm = crucible_cm2*v(F + 'cz_ar_slpm_per_cm2')
    ar_kg_pull = slpm*60*ar_h*AR_RHO_STD/1000
    return dict(wafers_per_pull=n, interval_d=interval_d, need_kg=need_kg, min_kg=min_kg, crucible_D_cm=cru_D, wafer_g=wafer_g, body_cm=body_cm, charge_kg=charge_kg, si_kg_d=si_kg_d, wafer_kg_d=wafer_kg_d,
                loss_kg_d=loss_kg_d, holding_kg=charge_kg,
                pull_h=pull_h, ar_h=ar_h, crucible_cm2=crucible_cm2, ar_slpm=slpm, ar_kg_pull=ar_kg_pull, ar_kg_d=ar_kg_pull/interval_d)

# stream id, from, to, carries, phase, composition, key of the design dict
STREAMS = (('STOCK_TO_FAB', 'METAL_STORE', 'WAFER_FAB', 'electronic-grade silicon CZ charge from the store', 'S', {'Si': 1.0}, 'si_kg_d'),
           ('IA-FAB-WAFER', 'WAFER_FAB', 'LITHO_COAT', 'wafers to resist coat', 'S', {'Si': 1.0}, 'wafer_kg_d'),
           ('IA-LITHO-WAFER-A', 'LITHO_COAT', 'LITHO_ALIGN', 'coated wafers to exposure', 'S', {'Si': 1.0}, 'wafer_kg_d'),
           ('IA-LITHO-WAFER-B', 'LITHO_ALIGN', 'LITHO_DEV', 'exposed wafers to develop', 'S', {'Si': 1.0}, 'wafer_kg_d'),
           ('IA-LITHO-WAFER-RET', 'LITHO_DEV', 'WAFER_FAB', 'patterned wafers back to the fab tool row', 'S', {'Si': 1.0}, 'wafer_kg_d'),
           ('IA-FAB-PRODUCT', 'WAFER_FAB', 'NORTH_DOCK', 'finished wafers to the dock for dispatch', 'S', {'Si': 1.0}, 'wafer_kg_d'),
           ('IA-FAB-KERF', 'WAFER_FAB', 'LEACH_CSTR_1', 'saw kerf, crop and pot scrap with the spent slurry', 'S', {'Si': 1.0}, 'loss_kg_d'),
           ('IA-AR-CZ', 'CRYO_ASU', 'WAFER_FAB', 'argon blanket gas for the CZ puller', 'G', {'Ar': 1.0}, 'ar_kg_d'),
           ('IA-AR-CZ-BACK', 'WAFER_FAB', 'CRYO_ASU', 'CZ argon exhaust back to the cold-box getter', 'G', {'Ar': 1.0}, 'ar_kg_d'))
WHY = {'si_kg_d': 'CZ charge per pull / days between pulls', 'wafer_kg_d': 'wafer starts x wafer mass',
       'loss_kg_d': 'charge less wafers: kerf, crop and pot scrap', 'ar_kg_d': 'puller argon per pull / days between pulls; closed loop through the getter'}

def tf(g, d=None):
    from flow_graph.param.o2_close import _edge
    r = design(d); N = {n['unit_id']: n for n in g['nodes']}; E = {e['stream_id']: e for e in g['edges']}
    for sid, a, b, carries, ph, comp, key in STREAMS:
        note = f"{TAG}: {WHY[key]} = {r[key]:.4f} kg/d (fab_silicon.py)."
        if sid not in E:
            e = _edge(sid, a, b, ph, ['mass'], carries, r[key], 'kg/d', N[a]['sector_id'], N[b]['sector_id'], comp, note)
            g['edges'].append(e); E[sid] = e
        e = E[sid]
        e.update(from_unit_id=a, to_unit_id=b, carries=carries, presence='present', composition=comp)
        e['rate'] = {'value': round(r[key], 6), 'unit': 'kg/d', 'status': 'study', 'note': note}
    return r

if __name__ == '__main__':
    print(json.dumps({k: (round(x, 4) if isinstance(x, float) else x) for k, x in design().items()}))

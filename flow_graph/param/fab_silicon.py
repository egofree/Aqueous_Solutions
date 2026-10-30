"""Silicon feed and crystal-growth blanket gas of WAFER_FAB, sized from the wafer need (owner decision 2026-10-29, A-M-417).

Silicon. The fab starts FAB.litho-train.starts_per_d wafers a day. Each wafer takes a slot of wafer thickness plus saw kerf
along the ingot body; the charge adds the crown, tail, ground-off diameter and pot scrap (cz_crop_frac). The charge of a pull is
the larger of the need of one tool campaign (campaign_d) and the least melt the crucible holds (cz_min_depth_frac of the crucible
diameter); the days between pulls follow, and the wafers of a pull are stored until started. On pv_wafer_route CZ_PSQ125 the same
ingot also gives the thin solar wafers of the cell line, so the body taken a day includes them; on CAST_MC156 the cell line takes
cast multicrystalline wafers instead and the cast charge is added (flow_graph/param/pv_wafer.py, A-M-437). The plant makes only metallurgical-grade silicon
(SI_REDUCE), far below the purity a CZ charge needs, so flow_graph/param/si_refine.py refines it on site to electronic grade
into the METAL_STORE buffer, which holds one charge until the pull (owner decision t58u: no imports except waste or raw ore). Finished
wafers go to the lithography train and back to the fab tool row, then to the dock; kerf and crop leave with the
spent slurry to the leach.

Blanket gas. The puller runs under argon from the cold box (CRYO_ASU) for the meltdown, neck and crown, body pull and
cool-down. Flow scales with the crucible area. The exhaust returns to CRYO_ASU through its heated argon getter, so the loop
is closed and the supply equals the return. Nitrogen is not a valid CZ ambient: at the melt temperature it forms silicon
nitride on the melt and the crucible (cz_blanket_gas = 'N2' is refused); nitrogen stays the purge of the wafer tools (S03).

Hot zone (A-M-436). The heater duty is a heat-loss model of the hot zone, not a class value. While the melt is held and pulled the
heater makes up: conduction through the graphite felt on the sides (a cylinder, Fourier) and on the top and bottom (flat discs);
radiation from the melt through the annulus of the heat-shield opening to the cold lid (grey body, emissivity of liquid silicon);
the heat the melt gives to the crystal, which is the conduction up the crystal at the interface, k G, less the latent heat that
the growth itself releases, rho v L; and the sensible heat of the argon purge, which leaves at the heater temperature. The axial
gradient G follows from the pull rate v by the Voronkov ratio at which the crystal grows defect-lean. At each meltdown the heater
also brings the graphite susceptor and heater up to temperature. During cool-down the heater is off. Every input is a driver, and
the model is to be checked against the heater power log of the first pull; no calibration factor is applied.
Run: python3 -m flow_graph.param.fab_silicon"""
import json, math, os
from . import drivers as DR
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = 'FAB.wafer-line-train.'
TAG = 'X-MFG-40 TF (A-M-417)'
AR_RHO_STD = 1.784          # g/L argon at 0 C and 1 atm, the reference of a standard litre per minute
SIGMA = 5.670374e-8         # W/(m2 K4) Stefan-Boltzmann constant (CODATA 2018, INCROPERA7)
R_GAS, M_AR = 8.314462, 39.948   # J/(mol K), g/mol; a monatomic gas has cp = 5/2 R / M

def felt_box(d, T_in_C, r_in_m, h_in_m, open_m2=0.0):
    """Conduction loss (W) through a felt pack around a cylinder of inner radius r_in and height h_in: Fourier through the side
    cylinder and through the top and bottom discs, less any opening in the top. The outer face sits at the cold wall."""
    k = DR.val(d, F + 'hz_felt_k_W_mK'); t = DR.val(d, F + 'hz_felt_mm')/1000; dT = T_in_C - DR.val(d, F + 'hz_wall_C')
    side = 2*math.pi*k*h_in_m*dT/math.log((r_in_m + t)/r_in_m)
    ends = k*(2*math.pi*r_in_m**2 - open_m2)*dT/t
    return side, ends

def hotzone(d, cru_D_cm, ingot_D_cm, pull_mm_h, ar_slpm):
    """Heater duty (kW) of the CZ hot zone while the melt is held and pulled, by term, and the heat (kWh) to bring the graphite up (A-M-436)."""
    v = lambda k: DR.val(d, F + k)
    Th = v('hz_heater_C'); Tw = v('hz_wall_C') + 273.15; Tm = 1414.0 + 273.15      # melting point of silicon (CRC_SI)
    r_cru = cru_D_cm/200; r_in = r_cru + v('hz_gap_mm')/1000; h_in = v('hz_height_ratio')*cru_D_cm/100
    r_ing = ingot_D_cm/200; r_open = r_ing*v('hz_open_ratio'); a_open = math.pi*(r_open**2 - r_ing**2); a_ing = math.pi*r_ing**2
    side, ends = felt_box(d, Th, r_in, h_in, math.pi*r_open**2)
    rad = v('si_melt_emissivity')*SIGMA*(Tm**4 - Tw**4)*a_open
    vel = pull_mm_h/1000/3600; G = (pull_mm_h/60)/v('cz_voronkov_mm2_Kmin')*1000     # m/s; K/m from v/G = xi (mm/min over mm2/(K min) gives K/mm)
    k_g = v('si_k_solid_W_mK')*G*a_ing; latent = v('si_rho_g_cm3')*1000*vel*v('si_latent_kJ_kg')*1000*a_ing
    xtal = k_g - latent
    ar = ar_slpm/60*AR_RHO_STD/1000*2.5*R_GAS/M_AR*1000*(Th - 25)                       # kg/s x J/(kg K) x K
    t = v('hz_graphite_t_mm')/1000; area = 2*math.pi*r_cru*h_in + math.pi*r_cru**2 + 2*math.pi*(r_in - t)*h_in
    g_kg = area*t*v('graphite_rho_g_cm3')*1000
    terms = dict(felt_side=side, felt_ends=ends, melt_radiation=rad, crystal=xtal, argon=ar)
    return dict(terms_kW={k: x/1000 for k, x in terms.items()}, kW=sum(terms.values())/1000, G_K_mm=G/1000, conduction_up_crystal_kW=k_g/1000, latent_kW=latent/1000,
                graphite_kg=g_kg, graphite_kWh=g_kg*v('graphite_cp_kJ_kgK')*(Th - 25)/3600, felt_inner_D_m=2*r_in, felt_inner_h_m=h_in)

def design(d=None):
    d = d or DR.load(); v = lambda k: DR.val(d, k)
    gas = v(F + 'cz_blanket_gas')
    if gas != 'Ar':
        raise SystemExit(f'fab_silicon: cz_blanket_gas {gas!r} refused: nitrogen forms silicon nitride on the melt at 1414 C; argon is the only valid CZ ambient')
    D = v(F + 'wafer_D_mm')/10; t = v(F + 'wafer_t_um')/1e4; kerf = v(F + 'kerf_um')/1e4; rho = v(F + 'si_rho_g_cm3')   # cm, g/cm3
    area = math.pi/4*D**2; starts = v('FAB.litho-train.starts_per_d'); keep = 1 - v(F + 'cz_crop_frac')
    wafer_g = rho*area*t; slot_g = rho*area*(t + kerf)
    from . import pv_wafer
    pv = pv_wafer.need(d); on_cz = pv['route'] == 'CZ_PSQ125'                 # solar wafers from the same ingot on CZ_PSQ125 (A-M-437)
    pv_slot_g_d = pv['slot_kg_d']*1000 if on_cz else 0.0; pv_cm_d = pv['cells_per_d']*(pv['t_cm'] + pv['kerf_cm']) if on_cz else 0.0
    # the charge is the larger of the wafer need of one tool campaign and the least melt the crucible can hold for a pull
    cru_D = D*v(F + 'cz_crucible_ratio'); crucible_cm2 = math.pi/4*cru_D**2
    min_kg = v(F + 'si_liquid_rho_g_cm3')*crucible_cm2*v(F + 'cz_min_depth_frac')*cru_D/1000
    day_g = starts*slot_g + pv_slot_g_d                                          # ingot body taken a day: fab wafers and, on CZ, solar wafers
    need_kg = v(F + 'campaign_d')*day_g/keep/1000
    charge_kg = max(need_kg, min_kg)
    interval_d = charge_kg*1000*keep/day_g; n = starts*interval_d              # days between pulls, fab wafers per pull
    body_cm = interval_d*(starts*(t + kerf) + pv_cm_d)
    wafer_kg_d = starts*wafer_g/1000; pv_wafer_kg_d = pv['wafer_kg_d']
    cz_kg_d = charge_kg/interval_d; mc = None if on_cz else pv_wafer.cast(d)
    si_kg_d = cz_kg_d + (mc['si_kg_d'] if mc else 0.0); loss_kg_d = si_kg_d - wafer_kg_d - pv_wafer_kg_d
    pull_h = body_cm*10/v(F + 'cz_pull_mm_h')
    ar_h = v(F + 'cz_melt_h') + v(F + 'cz_neck_crown_h') + pull_h + v(F + 'cz_cool_h')
    slpm = crucible_cm2*v(F + 'cz_ar_slpm_per_cm2')
    ar_kg_pull = slpm*60*ar_h*AR_RHO_STD/1000
    hz = hotzone(d, cru_D, D, v(F + 'cz_pull_mm_h'), slpm)
    heat_kWh = charge_kg*(v(F + 'si_cp_kJ_kgK')*(1414.0 - 25) + v(F + 'si_latent_kJ_kg'))/3600     # charge to melt (CRC_SI)
    hot_h = v(F + 'cz_melt_h') + v(F + 'cz_neck_crown_h') + pull_h                 # heater on; off for the cool-down
    hz_kWh = hz['kW']*hot_h + hz['graphite_kWh']
    melt_peak = hz['kW'] + (heat_kWh + hz['graphite_kWh'])/v(F + 'cz_melt_h')
    return dict(pv=pv, mc=mc, pv_wafer_kg_d=pv_wafer_kg_d, cz_kg_d=cz_kg_d, pv_wafers_per_pull=pv['cells_per_d']*interval_d if on_cz else 0.0, hz=hz, charge_heat_kWh=heat_kWh, hot_h=hot_h, hz_kWh_pull=hz_kWh, melt_peak_kW=melt_peak, pull_kWh=heat_kWh + hz_kWh,
                wafers_per_pull=n, interval_d=interval_d, need_kg=need_kg, min_kg=min_kg, crucible_D_cm=cru_D, wafer_g=wafer_g, body_cm=body_cm, charge_kg=charge_kg, si_kg_d=si_kg_d, wafer_kg_d=wafer_kg_d,
                loss_kg_d=loss_kg_d, holding_kg=charge_kg,
                pull_h=pull_h, ar_h=ar_h, crucible_cm2=crucible_cm2, ar_slpm=slpm, ar_kg_pull=ar_kg_pull, ar_kg_d=ar_kg_pull/interval_d + (mc['ar_kg_d'] if mc else 0.0))

# stream id, from, to, carries, phase, composition, key of the design dict
STREAMS = (('STOCK_TO_FAB', 'METAL_STORE', 'WAFER_FAB', 'electronic-grade silicon CZ charge from the store', 'S', {'Si': 1.0}, 'si_kg_d'),
           ('IA-FAB-WAFER', 'WAFER_FAB', 'LITHO_COAT', 'wafers to resist coat', 'S', {'Si': 1.0}, 'wafer_kg_d'),
           ('IA-LITHO-WAFER-A', 'LITHO_COAT', 'LITHO_ALIGN', 'coated wafers to exposure', 'S', {'Si': 1.0}, 'wafer_kg_d'),
           ('IA-LITHO-WAFER-B', 'LITHO_ALIGN', 'LITHO_DEV', 'exposed wafers to develop', 'S', {'Si': 1.0}, 'wafer_kg_d'),
           ('IA-LITHO-WAFER-RET', 'LITHO_DEV', 'WAFER_FAB', 'patterned wafers back to the fab tool row', 'S', {'Si': 1.0}, 'wafer_kg_d'),
           ('IA-FAB-PRODUCT', 'WAFER_FAB', 'NORTH_DOCK', 'finished wafers to the dock for dispatch', 'S', {'Si': 1.0}, 'wafer_kg_d'),
           ('IA-FAB-KERF', 'WAFER_FAB', 'LEACH_CSTR_1', 'saw kerf, crop and pot scrap with the spent slurry', 'S', {'Si': 1.0}, 'loss_kg_d'),
           ('IA-PV-WAFER', 'WAFER_FAB', 'SOLAR_PV_CELL', 'solar wafers to the cell line, from the CZ ingot or the cast block by pv_wafer_route', 'S', {'Si': 1.0}, 'pv_wafer_kg_d'),
           ('IA-PV-CELL', 'SOLAR_PV_CELL', 'PV_ARRAY', 'finished cells to the replacement modules of the roof array', 'S', {'Si': 1.0}, 'pv_wafer_kg_d'),
           ('IA-AR-CZ', 'CRYO_ASU', 'WAFER_FAB', 'argon blanket gas for the CZ puller and, on CAST_MC156, the cast furnace', 'G', {'Ar': 1.0}, 'ar_kg_d'),
           ('IA-AR-CZ-BACK', 'WAFER_FAB', 'CRYO_ASU', 'CZ argon exhaust back to the cold-box getter', 'G', {'Ar': 1.0}, 'ar_kg_d'))
WHY = {'si_kg_d': 'CZ charge per pull / days between pulls, plus the cast charge on CAST_MC156', 'pv_wafer_kg_d': 'cells a day to replace the roof array x solar wafer mass (pv_wafer.py, A-M-437)', 'wafer_kg_d': 'wafer starts x wafer mass',
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

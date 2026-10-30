"""Cell need and wafer route of the solar cell line SOLAR_PV_CELL (X-RTE-PV-SI, A-M-437).

Need. The cell line makes the cells that replace the plant's own roof array (PV_ARRAY). Its rate follows from the graph: the array
nameplate times the share replaced each year, over the power of one cell. A module is replaced when its output has fallen to the
end-of-life fraction, which at the measured degradation rate gives the life; random failures add their own share. The power of a
cell is its area times its efficiency at the standard irradiance of 1000 W/m2.

Wafer route (driver pv_wafer_route). Two technologies are valid, and both are built:
- CZ_PSQ125 (default): semi-square cells 125 mm across the flats, cut from the 150 mm Czochralski ingot of the one puller in
  WAFER_FAB, sliced thin for cells. The round corners are the ingot diameter; the square-off grind and the kerf go with the fab
  kerf. It needs no second furnace and gives the higher cell efficiency, so it is the default.
- CAST_MC156: square 156 mm multicrystalline cells sawn from a block cast by directional solidification in a small cast furnace
  inside WAFER_FAB. It does not depend on the puller, so it is the second technology and the backup when the puller is down.
A larger puller for 156 mm single-crystal cells (a 210 mm ingot) is evaluated in m2_puller() and not built: it would add a second
hot zone and a much larger least melt per pull for the same cells, which the 125 mm format already gives from the existing puller.

Recovery. The retired cells of end-of-life modules return their silicon to the chlorosilane loop of SI_REFINE (si_refine.py), so
the quartz reduced in SI_REDUCE falls by that silicon. In steady state the cells retired equal the cells installed.
Run: python3 -m flow_graph.param.pv_wafer"""
import json, math, os
from . import drivers as DR
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GP = os.path.join(ROOT, 'flow_graph/plant_flow_graph.json')
F = 'FAB.wafer-line-train.'; P = 'FAB.pv-wafer-train.'
ROUTES = ('CZ_PSQ125', 'CAST_MC156')
STC_W_M2 = 1000.0           # standard test irradiance (IEC 60904-3)
DAYS_YR = 365.25

def psq_area_cm2(side_mm, D_mm):
    """Area of a square of side `side_mm` with its corners cut by a circle of diameter D_mm (a semi-square wafer)."""
    R, h = D_mm/2, side_mm/2
    if h >= R: raise SystemExit(f'pv_wafer: a {side_mm} mm square does not fit inside a {D_mm} mm ingot')
    if h*math.sqrt(2) <= R: return side_mm**2/100
    seg = R*R*math.acos(h/R) - h*math.sqrt(R*R - h*h)      # circular segment beyond each flat
    return (math.pi*R*R - 4*seg)/100

def array_kw(g=None):
    g = g or json.load(open(GP))
    return float(next(n for n in g['nodes'] if n['unit_id'] == 'PV_ARRAY')['params']['nameplate_kw'])

def need(d=None, g=None, route=None):
    d = d or DR.load(); v = lambda k: DR.val(d, k)
    route = route or v('pv_wafer_route')
    if route not in ROUTES: raise SystemExit(f'pv_wafer: pv_wafer_route {route!r} is not one of {ROUTES}')
    life = (1 - v(P + 'eol_output_frac'))/v(P + 'degradation_per_yr')
    repl = 1/life + v(P + 'failure_per_yr')
    kw = array_kw(g); W_d = kw*1000*repl/DAYS_YR
    t = v(P + 'wafer_t_um')/1e4; kerf = v(F + 'kerf_um')/1e4; rho = v(F + 'si_rho_g_cm3')
    if route == 'CZ_PSQ125':
        D = v(F + 'wafer_D_mm'); A = psq_area_cm2(v(P + 'psq_side_mm'), D); eff = v(P + 'cell_eff_CZ'); body = math.pi/4*(D/10)**2
    else:
        A = v(P + 'mc_side_mm')**2/100; eff = v(P + 'cell_eff_MC'); body = A
    cell_W = A/1e4*STC_W_M2*eff; cells = W_d/cell_W
    wafer_g = rho*A*t; slot_g = rho*body*(t + kerf)
    return dict(route=route, array_kw=kw, life_yr=life, repl_per_yr=repl, W_d=W_d, cell_area_cm2=A, cell_eff=eff, cell_W=cell_W, cells_per_d=cells,
                wafer_g=wafer_g, slot_g=slot_g, wafer_kg_d=cells*wafer_g/1000, slot_kg_d=cells*slot_g/1000, t_cm=t, kerf_cm=kerf, Si_g_per_W=slot_g/cell_W)

def box_loss_W(d, T_C, side_m, h_m):
    """Conduction through a felt box of inner side side_m and height h_m: four flat walls, top and bottom (Fourier)."""
    k = DR.val(d, F + 'hz_felt_k_W_mK'); t = DR.val(d, F + 'hz_felt_mm')/1000; dT = T_C - DR.val(d, F + 'hz_wall_C')
    return k*(4*side_m*h_m + 2*side_m**2)*dT/t

def cast(d=None, nd=None):
    """Directional-solidification furnace of CAST_MC156: one block a campaign, sized from the wafer need (A-M-437)."""
    from .fab_silicon import AR_RHO_STD, R_GAS, M_AR
    d = d or DR.load(); v = lambda k: DR.val(d, k); nd = nd or need(d, route='CAST_MC156')
    rho = v(F + 'si_rho_g_cm3'); side = v(P + 'mc_side_mm')/10; blk = side + 2*v(P + 'mc_edge_crop_mm')/10   # cm
    usable = (side/blk)**2*(1 - v(P + 'mc_tb_crop_frac'))
    camp = v(F + 'campaign_d'); charge = nd['slot_kg_d']*camp/usable
    H = charge*1000/(rho*blk**2)                                       # cm block height
    Th = v(F + 'hz_heater_C'); s_in = blk/100 + 2*v(F + 'hz_gap_mm')/1000; h_in = v(F + 'hz_height_ratio')*s_in
    loss = box_loss_W(d, Th, s_in, h_in)
    vel = v(P + 'mc_growth_mm_h')/1000/3600; a = (blk/100)**2
    xtal = v(F + 'si_k_solid_W_mK')*v(P + 'mc_G_K_cm')*100*a - rho*1000*vel*v(F + 'si_latent_kJ_kg')*1000*a
    slpm = blk**2*v(F + 'cz_ar_slpm_per_cm2'); ar = slpm/60*AR_RHO_STD/1000*2.5*R_GAS/M_AR*1000*(Th - 25)
    grow_h = H*10/v(P + 'mc_growth_mm_h'); melt_h = v(P + 'mc_melt_h'); cool_h = v(P + 'mc_cool_h')
    gt = v(F + 'hz_graphite_t_mm')/1000; g_kg = (4*s_in*h_in + s_in**2)*gt*v(F + 'graphite_rho_g_cm3')*1000
    g_kWh = g_kg*v(F + 'graphite_cp_kJ_kgK')*(Th - 25)/3600
    heat = charge*(v(F + 'si_cp_kJ_kgK')*(1414.0 - 25) + v(F + 'si_latent_kJ_kg'))/3600
    kWh = heat + g_kWh + (loss + ar)/1000*(melt_h + grow_h) + xtal/1000*grow_h
    ar_kg = slpm*60*(melt_h + grow_h + cool_h)*AR_RHO_STD/1000
    return dict(block_cm=blk, height_cm=H, usable=usable, charge_kg=charge, interval_d=camp, si_kg_d=charge/camp, loss_kg_d=charge/camp - nd['wafer_kg_d'],
                held_kW=(loss + ar)/1000, crystal_kW=xtal/1000, graphite_kg=g_kg, kWh_cast=kWh, kW_avg=kWh/camp/24, peak_kW=(loss + ar)/1000 + (heat + g_kWh)/melt_h,
                ar_kg_d=ar_kg/camp, hours=melt_h + grow_h + cool_h)

def m2_puller(d=None):
    """A second, larger puller for 156 mm single-crystal cells, evaluated against the 125 mm cells of the existing puller."""
    from .fab_silicon import hotzone
    d = d or DR.load(); v = lambda k: DR.val(d, k)
    D = v(P + 'm2_ingot_D_mm')/10; cru = D*v(F + 'cz_crucible_ratio')
    min_kg = v(F + 'si_liquid_rho_g_cm3')*math.pi/4*cru**2*v(F + 'cz_min_depth_frac')*cru/1000
    hz = hotzone(d, cru, D, v(F + 'cz_pull_mm_h'), math.pi/4*cru**2*v(F + 'cz_ar_slpm_per_cm2'))
    A = v(P + 'mc_side_mm')**2/100                                     # 156 mm full-square single-crystal cell
    return dict(ingot_D_cm=D, crucible_D_cm=cru, min_melt_kg=min_kg, held_kW=hz['kW'], graphite_kg=hz['graphite_kg'], cell_W=A/1e4*STC_W_M2*v(P + 'cell_eff_CZ'))

if __name__ == '__main__':
    print(json.dumps(dict(need=need(), cast=cast(), m2=m2_puller()), default=float, indent=1))

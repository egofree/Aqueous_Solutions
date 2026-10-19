"""Q-009 closed (owner, 2026-10-16): the building's top floors are the pumped-hydro upper reservoir (water tower); CATCH_TANK at L-2 is the
lower reservoir. Pure solver, no FreeCAD: models/freecad/params.py and ess_tf.py both call solve(). A-M-187.
Energy E = rho g eta V h_eff, with h_eff the drop between the water centroids (upper full -> lower full), less penstock friction.
Both reservoirs use the plate less the stair/lift/shaft cores. The upper reservoir is stacked in levels of at most hw_max water each (slab and
wall load per ACI 350); each level is split in at least two cells (redundancy: one cell can be drained for inspection; cell length limits
sloshing). The lower reservoir deepens CATCH_TANK below the lowest basement. Head and volume depend on each other, so iterate."""
import json, math, os
_D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'drivers.json')
WTK = 'PUMPED_HYDRO.hydro-train.HYDRO_SET.'   # U4b: sizing literals single-sourced from drivers.json (A-M-187)
def _v(d, k): return float(d[k]['value'])
def solve(E_kWh, plate_L, plate_W, z_res0, z_catch_top, d=None, V_dead=0.0):
    """V_dead: fire reserve held below the hydro outlet (X-SAF-05); no head credit, and the lower reservoir also holds it (sprinkler run-off)."""
    d = d or json.load(open(_D))
    A = plate_L*plate_W/1e6*(1 - _v(d, 'wt_core_frac')); clr = _v(d, 'wt_level_clear_mm')/1000; hw = _v(d, 'wt_water_max_m')
    eta = _v(d, 'hydro_eta_turbine')*(1 - _v(d, 'wt_penstock_loss_frac')); fb = _v(d, 'wt_freeboard_m')
    TOP = _v(d, WTK+'wt_catch_top_deduct_m')  # L-1 slab 0.3 m + 0.2 m for bund sumps recessed into it (GA rev C: EW_BUND sump had cut into the tank)
    zr, zc = z_res0/1000, z_catch_top/1000 - TOP; V = 1000.0
    for _ in range(60):
        n = max(1, math.ceil((V + V_dead)/A/hw - 1e-9)); dl = (V + V_dead)/A/n                                   # equal depth on n levels
        zu = zr + _v(d, WTK+'wt_slab_m') + (n - 1)*clr/2 + dl/2                                               # centroid of the stack (slab 0.3 m)
        dc = (V + V_dead)/A; zl = zc - fb - dc/2                                                      # lower: top fixed under the basement, freeboard
        h = zu - zl; Vn = E_kWh*3.6e6/(1000*9.81*h*eta)
        if abs(Vn - V) < 0.01: break
        V = Vn
    L = plate_L/1000; ncell = max(_v(d, WTK+'wt_cells_min'), math.ceil(L/_v(d, 'wt_cell_len_m')))
    return dict(V_m3=V, head_m=h, area_m2=A, levels=n, depth_per_level_m=dl, level_clear_m=clr, z_res0_m=zr, z_roof_m=zr + n*clr,
                catch_depth_m=dc, catch_clear_m=dc + fb + _v(d, WTK+'wt_slab_m') + TOP, z_catch_floor_m=zc - fb - dc, cells_per_level=ncell, cell_len_m=L/ncell,
                water_t=V + V_dead, V_fire_m3=V_dead, eta_net=eta, E_kWh=E_kWh)
def seismic_wind(r, plate_L, plate_W, d=None):
    """ASCE7_22 12.8 equivalent lateral force on the water mass (impulsive, rigid), 15.7.6 sloshing freeboard (convective, rectangular cell
    per ACI350_3), 26-27 wind on the added height. Site values are A-M-187 assumptions until the geotechnical report."""
    d = d or json.load(open(_D)); g = 9.81; SDS, SD1, TL = _v(d, 'wt_SDS'), _v(d, 'wt_SD1'), _v(d, 'wt_TL_s')
    R, Ie = _v(d, 'wt_R'), _v(d, 'wt_Ie'); Cs = SDS/(R/Ie); W = r['water_t']*g                    # kN
    Lc, hl = r['cell_len_m'], r['depth_per_level_m']; lam = math.sqrt(3.16*g*math.tanh(3.16*hl/Lc)); Tc = 2*math.pi/lam*math.sqrt(Lc)
    Sac = min(1.5*SD1/Tc, 1.5*SDS) if Tc <= TL else 1.5*SD1*TL/Tc**2
    slosh = 0.42*Lc*Sac*Ie                                                                      # ASCE 7 15.7.6.1.2 (D -> cell length)
    V = _v(d, 'wt_wind_ms'); H = r['z_roof_m']; Kz = 2.01*(max(H, 4.6)/274.32)**(2/9.5)        # exposure C, Table 26.10-1
    qz = 0.613*Kz*0.85*V**2/1000; Fw = qz*0.85*1.3*(plate_L/1000)*r['levels']*r['level_clear_m']  # kN on the reservoir storeys, G 0.85, Cp 0.8+0.5
    return dict(W_water_kN=W, Cs=Cs, V_seis_kN=Cs*W, M_seis_kNm=Cs*W*(r['z_res0_m'] + r['levels']*r['level_clear_m']/2), Tc_s=Tc, Sac=Sac,
                slosh_m=slosh, freeboard_ok=slosh <= r['level_clear_m'] - _v(d, WTK+'wt_slab_m') - hl, qz_kPa=qz, F_wind_kN=Fw, H_roof_m=H)

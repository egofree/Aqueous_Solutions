"""engine v2: the building-stack geometry book (the shared physics of the
ledger section H rows doc_egress_env and doc_water_tower — the reference
libraries models/freecad/params.py and flow_graph/param/water_tower.py).

Both v1 libraries read drivers.json and the site profile from disk at import
or call time (params.py loads drivers and the committed graph when imported;
water_tower.solve calls SITE.g() internally), so a v2 renderer cannot import
them without re-introducing file I/O and an environment read. This module
ports the derivation the two documents consume as pure functions over the
solve inputs: the baseline plate and level stack (the SCALE_M 1 state of
params.py), the pumped-hydro reservoir solve (water_tower.solve with the
apparent gravity as an explicit argument — A-M-187), the ASCE 7 / ACI 350.3
seismic-and-wind book (water_tower.seismic_wind), and the assembled
building_book the two documents read (the params.py HYDRO, level datums,
core and stair geometry, and the CATCH_TANK basis).

Golden equality: flow_graph/v2/test_safety_books.py compares the book field
by field against the v1 libraries under the baseline site (the tests may read
files and import the I/O-carrying v1 modules; this module may not).

Pure: no I/O, no wall-clock, no RNG, no float literals (the engine lint's
discipline; the drivers and the site profile carry the values).
"""
import math

WTK = 'PUMPED_HYDRO.hydro-train.HYDRO_SET.'                             # the HYDRO_SET driver prefix (A-M-187)


def _v(d, k):
    return float(d[k]['value'])


# ---- the baseline plate and level stack (models/freecad/params.py, SCALE_M 1) ----

BAY = 6000                                                             # the bay module, mm
BASE_BAYS_X, BASE_BAYS_Y = 4, 3                                        # the baseline bay count (SCALE_M 1)
SCALE_M = 1                                                            # params.py SCALE_M 1.0; the floor/round paths read the int
SHOP_LEVELS = max(1, int(math.floor(SCALE_M)))
BASEMENT_LEVELS = max(1, int(math.floor(SCALE_M)))
MODULE_BAYS_X = max(1, int(round(BASE_BAYS_X * SCALE_M)))
MODULE_BAYS_Y = max(1, int(round(BASE_BAYS_Y * SCALE_M)))
PLATE_L = MODULE_BAYS_X * BAY                                          # 24 x 18 m baseline plate
PLATE_W = MODULE_BAYS_Y * BAY
SLAB_THK = 300                                                         # the suspended-level slab, mm (AQS-BLD-016)
CLEAR_Lm2 = 4500                                                       # catch / sub-basement clear before the reservoir deepening
CLEAR_Lm1 = 6000                                                       # each process basement clear
CLEAR_L0 = 6000                                                        # grade clear to the first life soffit
CLEAR_L1 = 4800                                                        # each life floor clear
Z_L0 = 0
Z_Lm1 = -CLEAR_Lm1 * 1                                                 # uppermost process basement FFL (basement_z(0))
Z_L1 = SHOP_LEVELS * CLEAR_L0                                          # first life FFL above the shop levels
CORE_L, CORE_W = 8000, 6000                                            # X-BLD-05 core re-pack
CORE_X = (PLATE_L - CORE_L) // 2
CORE_Y = (PLATE_W - CORE_W) // 2
SERVICE_ENTRY_L, SERVICE_ENTRY_W, SERVICE_ENTRY_H = 3600, 2400, 2800   # north face, west strip near the dock
SERVICE_ENTRY_X = 200
SERVICE_ENTRY_Y = PLATE_W - SERVICE_ENTRY_W - 200
STAIR_BOX = 2600                                                       # X-BLD-05: two flights of 1150 mm clear (IBC 1011.2 min 1118)
STAIR_MAINT_W = 1300                                                   # single flight 1150 mm clear
STAIR_SERVICE_L, STAIR_SERVICE_W = STAIR_BOX, 3600
STAIR_SERVICE_X = SERVICE_ENTRY_X + SERVICE_ENTRY_L + 200
STAIR_SERVICE_Y = PLATE_W - STAIR_SERVICE_W - 200


def basement_z(i):
    """FFL of process basement i (0 = uppermost = classic L-1)."""
    return -CLEAR_Lm1 * (int(i) + 1)


# ---- the pumped-hydro reservoir solve (flow_graph/param/water_tower.py, A-M-187) ----

def hydro_solve(e_kwh, plate_l, plate_w, z_res0, z_catch_top, d, g, v_dead=0):
    """V = E/(rho g h eta) with h the drop between the water centroids; the
    head depends on the depth, so iterate. v_dead: the fire reserve held below
    the hydro outlet (X-SAF-05), no head credit. g: the site apparent gravity
    (the v1 SITE.g() read, explicit here)."""
    a = plate_l * plate_w / 1000000 * (1 - _v(d, 'wt_core_frac'))
    clr = _v(d, 'wt_level_clear_mm') / 1000
    hw = _v(d, 'wt_water_max_m')
    eta = _v(d, 'hydro_eta_turbine') * (1 - _v(d, 'wt_penstock_loss_frac'))
    fb = _v(d, 'wt_freeboard_m')
    top = _v(d, WTK + 'wt_catch_top_deduct_m')                         # L-1 slab + bund sump deduction
    zr, zc = z_res0 / 1000, z_catch_top / 1000 - top
    vol = float('1000.0')
    for _ in range(60):
        n = max(1, math.ceil((vol + v_dead) / a / hw - float('1e-9')))
        dl = (vol + v_dead) / a / n                                    # equal depth on n levels
        zu = zr + _v(d, WTK + 'wt_slab_m') + (n - 1) * clr / 2 + dl / 2
        dc = (vol + v_dead) / a
        zl = zc - fb - dc / 2
        h = zu - zl
        vn = e_kwh * 3600000 / (1000 * g * h * eta)
        if abs(vn - vol) < float('0.01'):
            break
        vol = vn
    length = plate_l / 1000
    ncell = max(_v(d, WTK + 'wt_cells_min'), math.ceil(length / _v(d, 'wt_cell_len_m')))
    return dict(V_m3=vol, head_m=h, area_m2=a, levels=n, depth_per_level_m=dl, level_clear_m=clr, z_res0_m=zr,
                z_roof_m=zr + n * clr, catch_depth_m=dc,
                catch_clear_m=dc + fb + _v(d, WTK + 'wt_slab_m') + top, z_catch_floor_m=zc - fb - dc,
                cells_per_level=ncell, cell_len_m=length / ncell, water_t=vol + v_dead, V_fire_m3=v_dead,
                eta_net=eta, E_kWh=e_kwh)


def seismic_wind(r, plate_l, plate_w, d, g):
    """ASCE7_22 12.8 equivalent lateral force on the water mass (impulsive,
    rigid), 15.7.6 sloshing freeboard (convective, rectangular cell per
    ACI350_3), ch. 26-27 wind on the added height. Site values are A-M-187
    assumptions until the geotechnical report."""
    sds, sd1, tl = _v(d, 'wt_SDS'), _v(d, 'wt_SD1'), _v(d, 'wt_TL_s')
    rr, ie = _v(d, 'wt_R'), _v(d, 'wt_Ie')
    cs = sds / (rr / ie)
    w = r['water_t'] * g                                               # kN
    lc, hl = r['cell_len_m'], r['depth_per_level_m']
    lam = math.sqrt(float('3.16') * g * math.tanh(float('3.16') * hl / lc))
    tc = 2 * math.pi / lam * math.sqrt(lc)
    sac = min(float('1.5') * sd1 / tc, float('1.5') * sds) if tc <= tl else float('1.5') * sd1 * tl / tc ** 2
    slosh = float('0.42') * lc * sac * ie                              # ASCE 7 15.7.6.1.2 (D -> cell length)
    vv = _v(d, 'wt_wind_ms')
    hh = r['z_roof_m']
    kz = float('2.01') * (max(hh, float('4.6')) / float('274.32')) ** (2 / float('9.5'))   # exposure C, Table 26.10-1
    qz = float('0.613') * kz * float('0.85') * vv ** 2 / 1000
    fw = qz * float('0.85') * float('1.3') * (plate_l / 1000) * r['levels'] * r['level_clear_m']  # G 0.85, Cp 0.8+0.5
    return dict(W_water_kN=w, Cs=cs, V_seis_kN=cs * w, M_seis_kNm=cs * w * (r['z_res0_m'] + r['levels'] * r['level_clear_m'] / 2),
                Tc_s=tc, Sac=sac, slosh_m=slosh,
                freeboard_ok=slosh <= r['level_clear_m'] - _v(d, WTK + 'wt_slab_m') - hl, qz_kPa=qz, F_wind_kN=fw, H_roof_m=hh)


def building_book(model, d, g):
    """The assembled book params.py exposes to the egress and water-tower
    documents, derived from the model and inputs alone: the fire reserve sets
    the reservoir dead storage (X-FIR-01), the reservoir solve sets the
    reservoir levels and the roof datum, and the deepened catch clears set
    Z_Lm2 (the params.py order of definition)."""
    from . import fire_book as _FB
    life_levels = 1 + int(round(_v(d, 'wt_life_per_shop'))) * (SHOP_LEVELS - 1)
    z_l2 = Z_L1 + life_levels * CLEAR_L1                                # roof / tank plate above the top life floor
    vf = _FB.demand(d, PLATE_L * PLATE_W / 1000000)[1]                 # the governing fire-water volume (X-SAF-05)
    e = model.field('node', 'HYDRO_SET', 'params')['backup_basis']['energy_kWh_bus']
    r = hydro_solve(e, PLATE_L, PLATE_W, z_l2 + _v(d, 'wt_level_clear_mm'), basement_z(BASEMENT_LEVELS - 1), d, g, v_dead=vf)
    clear_lm2 = max(CLEAR_Lm2, int(round(r['catch_clear_m'] * 1000)))
    z_lm2 = basement_z(BASEMENT_LEVELS - 1) - clear_lm2
    catch_w = int(round(PLATE_W * (1 - _v(d, 'wt_core_frac'))))
    catch_h = int(round((r['catch_depth_m'] + _v(d, 'wt_freeboard_m')) * 1000))
    return dict(PLATE_L=PLATE_L, PLATE_W=PLATE_W, SLAB_THK=SLAB_THK, CLEAR_L1=CLEAR_L1,
                Z_Lm1=Z_Lm1, Z_Lm2=z_lm2, Z_L1=Z_L1, Z_L2=z_l2, Z_L0=Z_L0,
                SHOP_LEVELS=SHOP_LEVELS, LIFE_LEVELS=life_levels,
                CORE_X=CORE_X, CORE_Y=CORE_Y,
                STAIR_BOX=STAIR_BOX, STAIR_MAINT_W=STAIR_MAINT_W,
                STAIR_SERVICE_L=STAIR_SERVICE_L, STAIR_SERVICE_W=STAIR_SERVICE_W,
                STAIR_SERVICE_X=STAIR_SERVICE_X, STAIR_SERVICE_Y=STAIR_SERVICE_Y,
                HYDRO_RES_Z0=int(round(r['z_res0_m'] * 1000)), HYDRO_RES_CLEAR=int(_v(d, 'wt_level_clear_mm')),
                HYDRO_RES_LEVELS=r['levels'], Z_ROOF=int(round(r['z_roof_m'] * 1000)),
                HYDRO=r,
                CATCH_TANK_L=PLATE_L, CATCH_TANK_W=catch_w, CATCH_TANK_H=catch_h,
                CATCH_TANK_X=0, CATCH_TANK_Y=max(0, (PLATE_W - catch_w) // 2), CATCH_TANK_Z=z_lm2 + SLAB_THK)

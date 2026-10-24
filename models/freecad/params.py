"""Millimetre parameters. Keep in lockstep with models/openscad/params.scad."""

WALL = 12
FLOOR = 16

CSTR_L = 2000
CSTR_W = 1200
CSTR_H = 1400
FREEBOARD = 200

WEIR_W = 450
WEIR_CREST = CSTR_H - FREEBOARD
WEIR_SLOT_H = 80
WEIR_LIP = 120

AUGER_D = 140
AUGER_SHAFT = 40
AUGER_PITCH = 110
AUGER_TROUGH_W = 180
AUGER_TROUGH_H = 110
AUGER_OFFSET_Y = 280
AUGER_INCLINE = 28

MIXER_D = 50
GAS_D = 80
DROP_X = 80
DROP_L = 400
DROP_W = 250
DROP_COAM = 80

PUMP_D = 80
PUMP_Z = 450
PUMP_Y = 900
STRAINER_L = 180
STRAINER_W = 140
STRAINER_H = 160

MEZZ_H = 2200
MEZZ_L = 1600
MEZZ_THK = 12
HOPPER_L = 700
HOPPER_W = 600
HOPPER_H = 800
SHRED_L = 500
SHRED_W = 500
SHRED_H = 450
CONV_W = 240
CONV_H = 120
CONV_PLATE = 6
CONV_FLANGE = 40
CONV_SPRING_D = 50
CONV_SPRING_H = 80
CONV_BOLT = 10
CONV_LEN = 1800
DUST_D = 150
AUGER_LIFT_L = 700

FDEW_L = 1800
FDEW_W = 450
FDEW_H = 80
FDEW_RISE = 120
SDEW_L = 1400
SDEW_W = 220
SDEW_H = 80
SPLIT_L = 600
SPLIT_W = 500
SPLIT_H = 400
STUB_L = 400
STUB_W = 300
STUB_H = 250

EW_L = 600
EW_W = 420
EW_H = 650
EW_FUNNEL_H = 220
EW_VALVE_D = 50
EW_VALVE_L = 60
EW_MEM_T = 4
EW_SLOT = 10
EW_PITCH = 750
EW_TAGS = ("EW-1", "EW-2", "EW-3", "EW-4", "EW-5", "EW-6", "EW-7", "EW-8", "EW-9")

AISLE_X0 = 200
AISLE_Y = -(EW_W + 2 * WALL) - 400
AISLE_Z = 400
BUND_H = 150
BUND_PAD = 250
SUMP_L = 400
SUMP_W = 400
SUMP_H = 300
VDF_D = 700
VDF_L = 900
PAIL_W = 180
HDR_D = 80
HDR_Z = 1400

LBL_L = 400
LBL_H = 120
LBL_T = 8
LBL_Z = 1600
SIGN_L = 500
SIGN_H = 400
SIGN_T = 12
SIGN_Z = 1500

P_TANK_L = 500
P_TANK_W = 500
P_TANK_H = 800
P_PITCH = 600
PK_PITCH = 550
PK_TAGS = ("PK-1", "PK-2", "PK-3", "PK-4", "PK-5", "PK-6", "PK-7", "PK-8", "PK-9")
EW_METALS = ("Au", "Ag", "Cu", "Pb", "Sn", "Ni", "Fe", "Cd", "Zn")

BMED_L = 2200
BMED_W = 900
BMED_H = 1400
TOTE_L = 800
TOTE_W = 800
TOTE_H = 1100

DRYER_L = 1400
DRYER_W = 700
DRYER_H = 900
PYRO_L = 2800
PYRO_D = 320
FRAC_D = 500
FRAC_H = 2800
AB_D = 400
AB_H = 2200

RINSE_L = 1200
ROTARY_L = 2400
ROTARY_D = 600
MILL_L = 800
DIGEST_L = 1400
DIGEST_W = 900
DIGEST_H = 1600

RECT_L = 1600
RECT_W = 800
RECT_H = 1800
SOLARK_L = 800
SOLARK_W = 400
SOLARK_H = 1400
ZNBR_L = 1800
ZNBR_W = 1200
ZNBR_H = 1600
PV_L = 4000
PV_W = 2000
PV_H = 80

# ---------------------------------------------------------------------------
# Building stack levels (AQS-BLD-001) + scale model (AQS-SCALE-001).
# World Z = 0 is L0 grade FFL. Wet-line FCStd remains L-1-local
# (local Z=0 = L-1 FFL); build_plant shifts the process cassette by Z_Lm1.
# Scale rules: docs-authority/SCALE_MODEL.md. Not everything scales the same way.
#
# Vertical order (top → bottom), always:
#   ROOF_TANK → discrete LIFE floors (HAB∥FARM) → L0 MFG/grade →
#   discrete process BASEMENT levels (wet + CRYO) → CATCH_TANK (deepest)
# ---------------------------------------------------------------------------
import math

BAY = 6000
BASE_BAYS_X = 4
BASE_BAYS_Y = 3
BASE_PLATE_L = BASE_BAYS_X * BAY   # 24000
BASE_PLATE_W = BASE_BAYS_Y * BAY   # 18000

# Primary drivers: set SCALE_M, or set MODULE_BAYS_X / MODULE_BAYS_Y explicitly.
# SCALE_M=1 → 24 × 18 m baseline. Explicit bay counts win when not None.
SCALE_M = 1.0
MODULE_BAYS_X_OVERRIDE = None   # e.g. 8 for M3 length without changing Y
MODULE_BAYS_Y_OVERRIDE = None

def _bays_from_scale(scale):
    return (max(1, int(round(BASE_BAYS_X * scale))),
            max(1, int(round(BASE_BAYS_Y * scale))))

if MODULE_BAYS_X_OVERRIDE is not None:
    MODULE_BAYS_X = int(MODULE_BAYS_X_OVERRIDE)
else:
    MODULE_BAYS_X = _bays_from_scale(SCALE_M)[0]
if MODULE_BAYS_Y_OVERRIDE is not None:
    MODULE_BAYS_Y = int(MODULE_BAYS_Y_OVERRIDE)
else:
    MODULE_BAYS_Y = _bays_from_scale(SCALE_M)[1]

PLATE_L = MODULE_BAYS_X * BAY
PLATE_W = MODULE_BAYS_Y * BAY
AREA_SCALE = (float(PLATE_L) * float(PLATE_W)) / (float(BASE_PLATE_L) * float(BASE_PLATE_W))
_FOOT_SCALE = math.sqrt(AREA_SCALE)  # linear dims so footprint ∝ AREA_SCALE

# Discrete cassette from X-bay length — gates L0 MFG / WAFER_FAB horizontal jumps
# M1: 4–5 bays, M2: 6–7, M3: ≥8
if MODULE_BAYS_X >= 8:
    CASSETTE_COUNT = 3
elif MODULE_BAYS_X >= 6:
    CASSETTE_COUNT = 2
else:
    CASSETTE_COUNT = 1
CASSETTE_ID = ("M1", "M2", "M3")[CASSETTE_COUNT - 1]

# Discrete stacked floors (not continuous height stretch of one plate).
# LIFE_LEVELS: HAB∥FARM pairs between roof tank and L0 MFG/grade.
# BASEMENT_LEVELS: wet + CRYO process plates underground (CATCH below all).
# Owner rule (Q-009): as the building grows, HAB/FARM levels are added at wt_life_per_shop x the rate of shop levels.
import json as _json, os as _os, sys as _sys
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
_DRV = _json.load(open(_os.path.join(_ROOT, 'flow_graph/param/drivers.json')))
SHOP_LEVELS = max(1, int(math.floor(SCALE_M + 1e-12)))
LIFE_LEVELS = 1 + int(round(_DRV['wt_life_per_shop']['value'])) * (SHOP_LEVELS - 1)
BASEMENT_LEVELS = max(1, int(math.floor(SCALE_M + 1e-12)))

SLAB_THK = 300
CLEAR_Lm2 = 4500   # catch / sub-basement clear
CLEAR_Lm1 = 6000   # each process basement clear
CLEAR_L0 = 6000    # grade clear to first life soffit
CLEAR_L1 = 4800    # each life floor clear

Z_L0 = 0


def basement_z(i):
    """FFL of process basement i (0 = uppermost = classic L-1, just below grade)."""
    return -CLEAR_Lm1 * (int(i) + 1)


Z_Lm1 = basement_z(0)  # uppermost process basement FFL
# CATCH always deepest: below the lowest process basement clear
Z_Lm2 = basement_z(BASEMENT_LEVELS - 1) - CLEAR_Lm2   # replaced below by the lower-reservoir depth
Z_L1 = SHOP_LEVELS * CLEAR_L0      # first life FFL above the shop levels
Z_L2 = Z_L1 + LIFE_LEVELS * CLEAR_L1  # roof / tank plate above top life floor
Z_PROCESS = Z_Lm1                  # primary wet cassette on uppermost basement


def life_z(i):
    """FFL of discrete life floor i (0 = first above L0). HAB∥FARM pair."""
    return Z_L1 + int(i) * CLEAR_L1


# Wet-process cassette XY nudge (L-1 local → plate bay grid). Local cassette
# overhangs west/south of leach origin; shift keeps wet line inside SLAB_Lm1.
PROCESS_DX = 5000
PROCESS_DY = 4000

SITE_LAT_DEG = 33.0                # Dallas default; ARRAY_ROOF / PV tilt = +φ (south face NH)

CORE_L, CORE_W = 8000, 6000      # X-BLD-05 core re-pack: STAIR_P 2.6x4.8, ELEV_SVC 2.7x3.2, STAIR_MAINT, 6 shafts without overlap (CAD clash check)
CORE_X = (PLATE_L - CORE_L) // 2
CORE_Y = (PLATE_W - CORE_W) // 2

# Site orientation (AQS-SITE-001 / AQS-BLD-001):
#   +Y = site north = pole-facing in the northern hemisphere.
# ARRAY_ROOF / PV_ARRAY: rotate about +X by +SITE_LAT_DEG (NH) so +Y edge
# rises → south (equator) face. Negative tilt would face north/dock — forbidden.
# ENV_WALL_N at Y = PLATE_W. Do not flip axes without updating AQS-SITE-001.
SITE_NORTH_AXIS = "+Y"

# L0 primary truck dock — north (pole-facing) edge of plate at grade.
# Origin = SW corner of dock bay on the plate. Truck doors face +Y (north).
# Discrete jump (AQS-SCALE-001 / AQS-BLD-001): ONE dock space + associated
# freight elevator (ELEV_DOCK) at baseline (M1). Add dock+elevator pairs
# as the plate grows E–W (same cassette unlock as MFG/FAB).
DOCK_COUNT = CASSETTE_COUNT          # M1→1, M2→2, M3→3
DOCK_PAIR_L = min(12000, max(BAY * 2, PLATE_L // max(1, DOCK_COUNT)))
DOCK_L = DOCK_PAIR_L                 # plan length of one dock space
DOCK_W = min(8000, PLATE_W)
DOCK_X = 0
DOCK_Y = PLATE_W - DOCK_W
DOCK_Z = Z_L0
DOCK_APRON_N = 34000         # exterior truck apron north of ENV_WALL_N: 1.5 x WB-67 length 22.4 m, X-BLD-07 / A-M-212 (was 6000)
DOCK_APRON_W = PLATE_L       # apron along the whole north face for the WB-67 turn (X-BLD-07)
DOCK_DOOR_H = 4300           # dock door clear height: WB-67 4.11 m + 0.19 m (X-BLD-07)
DOCK_DOOR_W = 3600           # north-facing door clear (massing)
# Freight elevator paired with each dock (≠ CORE ELEV_SVC)
ELEV_DOCK_L, ELEV_DOCK_W = 2700, 3200
ELEV_DOCK_H_HEAD = 500       # headroom above L0 for shaft massing start

# SERVICE_ENTRY + STAIR_SERVICE — north face, west strip near dock.
# Equipment / service access to basement AND code-credible secondary
# egress from L-1 / L-2. Does not carry hab sleeping egress (STAIR_P /
# STAIR_S*). Not STAIR_MAINT (operators-only). See AQS-SITE-001.
SERVICE_ENTRY_L, SERVICE_ENTRY_W, SERVICE_ENTRY_H = 3600, 2400, 2800
SERVICE_ENTRY_X = 200
SERVICE_ENTRY_Y = PLATE_W - SERVICE_ENTRY_W - 200
STAIR_BOX = 2600             # X-BLD-05: two flights of 1,150 mm clear (IBC 1011.2 min 1,118) + 300 mm for walls and rails
STAIR_MAINT_W = 1300         # single flight 1,150 mm clear
STAIR_SERVICE_L, STAIR_SERVICE_W = STAIR_BOX, 3600
STAIR_SERVICE_X = SERVICE_ENTRY_X + SERVICE_ENTRY_L + 200
STAIR_SERVICE_Y = PLATE_W - STAIR_SERVICE_W - 200

# Campus envelopes (mm). Origins = SW corner on the named plate.
# HAB west / FARM east — always paired on each discrete life floor.
HAB_L = PLATE_L // 2
HAB_W = PLATE_W
HAB_H = 3200
HAB_X, HAB_Y, HAB_Z = 0, 0, Z_L1

FARM_L = PLATE_L - HAB_L
FARM_W = PLATE_W
FARM_H = 4500
FARM_X, FARM_Y, FARM_Z = HAB_L, 0, Z_L1

# MFG + WAFER_FAB always at L0 (ground). Horizontal discrete jumps only.
# L0 Y redistrib (AQS-AUD-001 Rev D layout relief): MFG depth 10→8 m,
# FAB depth 8→10 m — same 18 m plate, no SCALE_M / bay-count change.
MFG_L = 12000 + (CASSETTE_COUNT - 1) * BAY
MFG_W, MFG_H = 8000, 5000
MFG_X, MFG_Y, MFG_Z = PLATE_L // 2, 0, Z_L0

FAB_L = 12000 + (CASSETTE_COUNT - 1) * BAY
FAB_W, FAB_H = 10000, 4000
FAB_X, FAB_Y, FAB_Z = PLATE_L // 2, MFG_W, Z_L0
if FAB_Y + FAB_W > PLATE_W:
    FAB_Y = max(0, PLATE_W - FAB_W)

# CRYO always underground on process basement plates (not grade).
# Vertical growth = BASEMENT_LEVELS; one cold-box bay per basement level.
# Layout relief (AQS-AUD-001 Rev D): 6×6 → 9×6 m using free east strip to
# plate edge (CRYO_X + 9000 ≤ PLATE_L at M1). Bay grid unchanged.
# Rev E (2026-10-16): W 6000 -> 8700 to hold the A-M-214 block (8.66 m) and the 1 h H2 / O2 partition.
CRYO_L, CRYO_W, CRYO_H = 9000, 8700, 4000
CRYO_X = CORE_X + CORE_L
CRYO_Y = CORE_Y
CRYO_Z = Z_Lm1  # primary (uppermost basement); replicas use basement_z(i)
if CRYO_Y + CRYO_W > PLATE_W:
    CRYO_Y = max(0, PLATE_W - CRYO_W)
if CRYO_X + CRYO_L > PLATE_L:
    CRYO_X = max(0, PLATE_L - CRYO_L)

# Continuous tanks ∝ plan area (same rate). Height fixed → V ∝ footprint.
# ROOF_TANK always top (Z_L2). CATCH_TANK always deepest (Z_Lm2).
_RT_L0, _RT_W0, _RT_H0 = 16000, 12000, 7000
_CT_L0, _CT_W0, _CT_H0 = 12000, 8000, 4000
ROOF_TANK_L = int(round(_RT_L0 * _FOOT_SCALE))
ROOF_TANK_W = int(round(_RT_W0 * _FOOT_SCALE))
ROOF_TANK_H = _RT_H0
ROOF_TANK_X = max(0, (PLATE_L - ROOF_TANK_L) // 2)
ROOF_TANK_Y = max(0, (PLATE_W - ROOF_TANK_W) // 2)
ROOF_TANK_Z = Z_L2

# Q-009 closed: water tower. Upper reservoir = HYDRO_RES levels above the ROOF_TANK storey; lower = CATCH_TANK (A-M-187).
_sys.path.insert(0, _ROOT)
from flow_graph.param import water_tower as _WT
try:
    _E = [n for n in _json.load(open(_os.path.join(_ROOT, 'flow_graph/plant_flow_graph.json')))['nodes'] if n['unit_id'] == 'HYDRO_SET'][0]['params']['backup_basis']['energy_kWh_bus']
except Exception:
    _E = 200.3
from flow_graph.param import fire as _FIRE
FIRE_RESERVE_M3 = _FIRE.demand(PLATE_L*PLATE_W/1e6)[1]
HYDRO = _WT.solve(_E, PLATE_L, PLATE_W, Z_L2 + _DRV['wt_level_clear_mm']['value'], basement_z(BASEMENT_LEVELS - 1), _DRV, V_dead=FIRE_RESERVE_M3)
HYDRO_RES_LEVELS = HYDRO['levels']
HYDRO_RES_Z0 = int(round(HYDRO['z_res0_m'] * 1000))
HYDRO_RES_CLEAR = int(_DRV['wt_level_clear_mm']['value'])
HYDRO_RES_WATER_H = int(round(HYDRO['depth_per_level_m'] * 1000))
HYDRO_HEAD_M = HYDRO['head_m']
Z_ROOF = int(round(HYDRO['z_roof_m'] * 1000))      # roof slab over the reservoir; PV array sits here
CLEAR_Lm2 = max(CLEAR_Lm2, int(round(HYDRO['catch_clear_m'] * 1000)))
Z_Lm2 = basement_z(BASEMENT_LEVELS - 1) - CLEAR_Lm2
CATCH_TANK_L = PLATE_L
CATCH_TANK_W = int(round(PLATE_W * (1 - _DRV['wt_core_frac']['value'])))
CATCH_TANK_H = int(round((HYDRO['catch_depth_m'] + _DRV['wt_freeboard_m']['value']) * 1000))
CATCH_TANK_X = 0
CATCH_TANK_Y = max(0, (PLATE_W - CATCH_TANK_W) // 2)
CATCH_TANK_Z = Z_Lm2 + SLAB_THK

# Electrical discrete jumps (AQS-SCALE-001)
# D10 (2026-10-18) — PRECEDENCE: the GRAPH wins, unconditionally. These seeds
# (50 kW base / x1.4 overprod / 70 kW PV module / 60 kW·120 kWh ZNBR) are
# OFFLINE FALLBACKS for building without a pack. When a design-tool pack
# params.json is applied (params_overlay_apply.py), the graph's
# mvs.electrical + PV_ARRAY params (written by flow_graph/param/write_graph.py
# power(): need 281.96 kW, target = 2.5 x need, 7818 x 0.5 kWp PV, ZNBR2 over
# the 55 x 60 kW hybrid-inverter block) override the derived ELEC_NEED_KW /
# ELEC_TARGET_KW / PV_COUNT / ZNBR_COUNT / RECT_COUNT / module kW in the fork
# (need base and module kW in place; target + counts as end-overrides).
# ELEC_OVERPROD is inert under a target_kw push and stays a fallback knob.
ELEC_NEED_KW_BASE = 50.0
ELEC_OVERPROD = 1.4
PV_MODULE_KW = 70.0
ZNBR_MODULE_KW = 60.0
ZNBR_MODULE_KWH = 120.0
ELEC_NEED_KW = (ELEC_NEED_KW_BASE * CASSETTE_COUNT
                * (0.6 + 0.2 * LIFE_LEVELS + 0.2 * BASEMENT_LEVELS))
ELEC_TARGET_KW = ELEC_NEED_KW * ELEC_OVERPROD
PV_COUNT = max(1, int(math.ceil(ELEC_TARGET_KW / PV_MODULE_KW)))
ZNBR_COUNT = max(
    1,
    int(math.ceil(ELEC_NEED_KW / ZNBR_MODULE_KW)),
    int(math.ceil(ELEC_NEED_KW * 2.0 / ZNBR_MODULE_KWH)),
)
RECT_COUNT = max(1, CASSETTE_COUNT)

# Life-floor terraces (balconies) — AQS-TRR-001 / AQS-BLD-001 layout lock.
# One terrace per life floor on S+E+W (NH) or N+E+W (SH), starting at the
# top life floor and stepping down/out. Each floor has a door onto its terrace.
# Grade OVERFLOW_* aprons remain the clean-tower surplus receiver (not the
# primary balcony massing).
TERRACE_SLAB_THK = 200
TERRACE_WIDTH = 3000          # plan depth of one floor terrace band
TERRACE_DOOR_W = 1200         # door clear from life floor onto terrace
TERRACE_DOOR_H = 2200
TERRACE_RAIL_H = 1100         # guardrail massing on outer edge
# Legacy grade overflow bands (irrigation / surplus path; subordinate)
TERRACE_RUN = 9000            # total plan run of grade overflow bands
TERRACE_BANDS = 3             # discrete grade bands approximating slope
TERRACE_DROP = 1800           # total top-of-slab drop, inner (grade) → outer band
TERRACE_DOWNCOMER_D = 400     # conceptual overflow riser stub OD (massing)
# Yard: keep outdoor POWER equipment west of ENV_WALL_W (no wall punch-through)
YARD_WALL_CLEAR = 500         # mm clear west of X=0 for GEN/FC east faces

# Life-header rack tiers (mm above each life FFL; world = life_z(i) + tier).
LIFE_Z_GREY = 900
LIFE_Z_UPW = 1100
LIFE_Z_ETCH = 1300
LIFE_Z_O2 = 2800
LIFE_Z_N2 = 3000
LIFE_Z_CO2 = 3200
LIFE_D_GREY = 50
LIFE_D_UPW = 40
LIFE_D_ETCH = 32
LIFE_D_GAS = 25
LIFE_D_CO2 = 40
LIFE_RACK_N_Y = PLATE_W - 1000
LIFE_RACK_S_Y = 200
LIFE_RACK_W_X = 200
LIFE_RACK_E_X = PLATE_L - 200
LIFE_RACK_X0 = 0
LIFE_RACK_X1 = PLATE_L
LIFE_RACK_Y0 = 0
LIFE_RACK_Y1 = PLATE_W

# ---------------------------------------------------------------------------
# WP-D1b / CAD-M1 — TBD massing clash envelopes (not PE nameplates / not rates).
# Aliases of existing stub / tote / digest / tank / BMED classes only.
# ---------------------------------------------------------------------------
D1B_TBD_SKID_L = BMED_L
D1B_TBD_SKID_W = BMED_W
D1B_TBD_SKID_H = BMED_H
D1B_TBD_TOTE_L = TOTE_L
D1B_TBD_TOTE_W = TOTE_W
D1B_TBD_TOTE_H = TOTE_H
D1B_TBD_DIGEST_L = DIGEST_L
D1B_TBD_DIGEST_W = DIGEST_W
D1B_TBD_DIGEST_H = DIGEST_H
D1B_TBD_TANK_L = P_TANK_L
D1B_TBD_TANK_W = P_TANK_W
D1B_TBD_TANK_H = P_TANK_H
D1B_TBD_STUB_L = STUB_L
D1B_TBD_STUB_W = STUB_W
D1B_TBD_STUB_H = STUB_H
# Reagent-tote pitch (reuse polish-bank pitch class)
D1B_WS_PITCH = PK_PITCH

# GA relocations applied after placement (build_plant.py), world mm, bbox centre in plan. Rev 2026-10-16 (GA_CHECK CAD clash fix):
# AFTERBURNER sat in the 100-200 mm-gap pyrolysis line (overlapping NaOH_DIGEST, touching PROD_C5_C10), where no 1 h room
# fits; moved to the nearest free 2 x 2 m L-1 bay (17.4-19.4 m E, 1.7-3.7 m N), about 3 m of NCG duct from the fractionator.
RELOCATE = {"AFTERBURNER": (18400, 2700)}

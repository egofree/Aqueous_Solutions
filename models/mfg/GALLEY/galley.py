"""GALLEY manufacturing model, AQS-PLAN-006 work order (X-HAB habitation room).

Graph revision AD. Study. Not a PE stamp. Reads the plant graph through the shared
reader (models/mfg/lib/graph_node.py) and rebuilds every solid through the shared
close-out builder (models/mfg/farm_closeout.py), the AQUA_TANK pattern.

Placement frame: x along the room length, y along the width, z up, origin at the room
corner. Every dimension is an authority figure or a named layout choice:

- The unit is the 12 m2 galley fitout shell per the node size basis ("12 m2 fitout
  shell at the A-M-419 room basis, 2400 ceiling (AQS-HAB-001) (X-HAB sec3)"): the
  room-form shell 4000 x 3000 x 2400 with 15 mm partition panels, a 900 x 2100 door
  opening in the -X end wall and the 20 mm deck-finish build-down (the accepted form
  class). Nothing is resized.
- The fitout duty section 3 names, drawn as study envelopes (WORK_ORDER W12): an
  SS304 galley counter along the -Y wall west of the inlet row (worktop,
  splashback, four legs - the worktops and splashbacks duty section 3 names); a
  purchased range/oven appliance envelope against the -X end wall (the baked
  crushed eggshell return of schedule row N6 is baked here); and a food-contact PP
  preparation-board set on the worktop (duty section 3). No copper-bearing alloys
  on food paths: the counter and nozzles are 304.
- Nozzles: all 8 rows of docs-authority/nozzles/GALLEY.csv drawn at tag, face and
  bore as atmospheric open-bore tube stubs flush at the envelope faces (duty section
  4; the schedule rating column Class 150 carried verbatim as text; no flange drawn,
  W4 110 % rule). N1 food issue and N7 duckweed greens on -Y at z 160; N2 prepared
  meals, N3 biowaste, N6 eggshell return and N8 grey water on +Y at z 600; N4 drain
  flush at the envelope bottom under the counter; N5 vent flush at the envelope top
  on the +Y wall line (the schedule z 800 datum predates the 2400 box - stale datum,
  hold W12).
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))            # models/mfg: lib, tracker, farm_hab
sys.path.insert(0, str(HERE.parents[2]))        # repo root: models.*

from models.mfg import farm_closeout            # noqa: E402

UNIT = "GALLEY"

# Galley counter (duty section 3 SS304 worktops and splashbacks; run along the -Y
# wall west of the -Y inlet row, WORK_ORDER W12). (xyz dxdydz)
COUNTER_TOP = (300.0, 60.0, 854.0, 1600.0, 600.0, 6.0)
COUNTER_SPLASH = (300.0, 15.0, 860.0, 1600.0, 6.0, 300.0)
COUNTER_LEGS = [(320.0, 80.0), (1840.0, 80.0), (320.0, 600.0), (1840.0, 600.0)]

# Range/oven appliance envelope (bakes the N6 crushed-eggshell return; against the
# -X end wall south of the door swing): outer and inner cut xyz dxdydz.
APPLIANCE = ((15.0, 2000.0, 0.0, 600.0, 650.0, 900.0),
             (19.0, 2004.0, 8.0, 592.0, 642.0, 892.0))

# Food-contact PP preparation boards on the worktop (duty section 3). xyz dxdydz.
PREP_BOARDS = [(400.0, 120.0, 860.0, 450.0, 450.0, 20.0),
               (1000.0, 150.0, 860.0, 450.0, 450.0, 20.0)]

DRAIN_XY = (900.0, 360.0)                       # under the counter run
VENT_XY = (2000.0, 2985.0)                      # on the +Y wall line


def _checker(P):
    """A bounds helper: every fitout envelope stays inside the room walls."""
    L, W, H = (float(v) for v in P["size_mm"])

    def check(k, x, y, z, dx, dy, dz):
        assert x >= 15.0 and x + dx <= L - 15.0, (k, "inside the end walls")
        assert y >= 15.0 and y + dy <= W - 15.0, (k, "inside the long walls")
        assert z + dz <= H - 20.0, (k, "under the ceiling line")
    return check


def _counter(P):
    from farm_closeout import box
    check = _checker(P)
    check("counter", *COUNTER_TOP)
    check("counter_splash", *COUNTER_SPLASH)
    for (lx, ly) in COUNTER_LEGS:
        check("counter_leg", lx, ly, 0.0, 40.0, 40.0, 854.0)
    run = box(*COUNTER_TOP).union(box(*COUNTER_SPLASH))
    for (lx, ly) in COUNTER_LEGS:
        run = run.union(box(lx, ly, 0.0, 40.0, 40.0, 854.0))
    return run


def _appliance(P):
    from farm_closeout import box
    outer, cut = APPLIANCE
    _checker(P)("appliance", *outer)
    return box(*outer).cut(box(*cut))


def _prep_boards(P):
    from farm_closeout import box
    check = _checker(P)
    boards = None
    for i, b in enumerate(PREP_BOARDS):
        check(f"prep_board_{i + 1}", *b)
        s = box(*b)
        boards = s if boards is None else boards.union(s)
    return boards


SPEC = {
    "unit": UNIT,
    "extras": {"counter": _counter, "appliance": _appliance,
               "prep_boards": _prep_boards},
    "rho_map": {"floor": "aluminium", "wall_long_a": "aluminium",
                "wall_long_b": "aluminium", "wall_end_solid": "aluminium",
                "wall_end_door": "aluminium", "counter": "304",
                "appliance": "steel", "prep_boards": "PP", "nozzles": "304"},
    "drop_keys": (),
    "drain_xy": DRAIN_XY,
    "vent_xy": VENT_XY,
    "cad_stl_scope": "build solid, metres (X-PAR-04 envelope registry; the room shell "
                     "fills the node box 4000 x 3000 x 2400, walls to the 2380 "
                     "ceiling line, vent flush at the 2400 top)",
    "nozzle_idiom": "atmospheric open-bore tube stubs flush at the envelope faces "
                    "(duty section 4); N1 food issue and N7 duckweed greens on -Y at "
                    "z 160; N2 prepared meals, N3 biowaste, N6 eggshell return and "
                    "N8 grey water on +Y at z 600; N4 drain flush at the envelope "
                    "bottom under the counter; N5 vent flush at the envelope top on "
                    "the +Y wall line (the schedule z 800 datum predates the 2400 "
                    "box - stale datum, WORK_ORDER W12); no flange drawn (W4 110 % "
                    "rule); the schedule rating column (Class 150) carried verbatim "
                    "as text",
    "machine": lambda P, dims, mass: {
        "type": "habitation galley fitout: aluminium room shell (12 m2, A-M-419; "
                "AQS-HAB-001, 2400 ceiling) with an SS304 counter run, a purchased "
                "range/oven appliance envelope and a PP preparation-board set "
                "(node size basis)",
        "a_farm": "the room shell is drawn at the node box per the room form class; "
                  "the counter, appliance and board envelopes and the nozzle set "
                  "are drawn",
        "counter": "SS304 worktop + splashback + four legs along the -Y wall "
                   "x 300..1900, west of the -Y inlet row (worktops and splashbacks "
                   "per duty section 3); layout choice, WORK_ORDER W12",
        "appliance": "range/oven envelope 600 x 650 x 900 against the -X end wall "
                     "south of the door swing - the baked crushed eggshell return "
                     "(schedule N6) is baked here; purchased per plan rule 6, "
                     "study sheet envelope at steel density",
        "prep_boards": "food-contact PP boards on the worktop (duty section 3); no "
                       "copper-bearing alloys on food paths (AQS-STD-002)",
        "material": P.get("material"),
        "ca_mm": 0.0,
    },
    "bom": lambda P, mass, dims: [
        ["1", "Aluminium room shell: floor + four 15 mm partition walls, 4000 x "
              "3000 x 2400 outer, 900 x 2100 door opening in the -X end wall (12 m2 "
              "fitout shell at the A-M-419 room basis, 2400 ceiling)", 1,
         "aluminium",
         round(sum(mass[k] for k in ("floor", "wall_long_a", "wall_long_b",
                                     "wall_end_solid", "wall_end_door")), 1), "make",
         "size_basis verbatim; no copper-bearing alloys on food paths (duty section "
         "3, AQS-STD-002)"],
        ["2", "SS304 galley counter: worktop + splashback + four legs, run "
              "1600 x 600 along the -Y wall x 300..1900", 1, "SS304",
         mass["counter"], "make",
         "worktops and splashbacks per duty section 3; shop sheet-metal work; no "
         "copper-bearing alloys on food paths (AQS-STD-002)"],
        ["3", "Range/oven appliance envelope (bakes the N6 crushed-eggshell "
              "return), 600 x 650 x 900 against the -X end wall", 1, "steel",
         mass["appliance"], "buy",
         "purchased appliance per plan rule 6; study sheet envelope at steel "
         "density, maker prints govern at order"],
        ["4", "PP preparation board set (food-contact), two boards on the worktop",
         2, "PP", mass["prep_boards"], "buy",
         "catalogue item; food-contact PP per duty section 3 (AQS-STD-002)"],
        ["5", "Nozzle set per docs-authority/nozzles/GALLEY.csv: 8 rows drawn as "
              "DN15 tube stubs (food issue in, prepared meals, biowaste, drain, "
              "vent, eggshell return, duckweed greens in, grey water out)", 8,
         "SS304", mass["nozzles"], "make",
         "schedule tags/faces/heights verbatim; atmospheric per duty section 4; "
         "bores are the AQS-PIP-004 line DN, not recalculated (AQS-PIP-003)"],
    ],
    "fastener_rows": lambda P: [
        [None, "M10 counter hold-down bolt", "ISO 3506 A4-70", 6,
         "counter legs and appliance envelope to the slab (study pattern)",
         "A4-70 stainless on the food-contact line (duty section 3: no "
         "copper-bearing alloys on food paths); study pattern, confirmed at "
         "fabrication"],
        [None, "M10 shell sill anchor", "ISO 898-1 8.8", 4,
         "room shell sill to the slab, 4 corners",
         "8.8 carbon steel per the plan grade rule; the anchor is not a wetted "
         "part; isolation washers at the aluminium sill at fabrication"],
    ],
    "envelope_block": lambda P, dims: {
        "size_mm": P["size_mm"],
        "basis": P.get("size_basis"),
        "wall_mm": P.get("wall_mm"),
        "measured_bbox_mm": dims,
    },
    "layout_block": lambda P: {
        "frame": "origin at the room corner; floor + four 15 mm partition walls per "
                 "the room form class, 900 x 2100 door opening in the -X end wall, "
                 "20 mm deck-finish build-down (walls to z 2380); counter run along "
                 "the -Y wall x 300..1900 (worktop at z 854, splashback to z 1160), "
                 "appliance envelope against the -X end wall y 2000..2650, boards "
                 "on the worktop",
        "supports": "shell on the slab on 4 sill anchors; counter on 4 legs bolted "
                    "to the slab; appliance bolted to the slab",
        "nozzle_spread": "the schedule gives face and height only; inlets N1 and N7 "
                         "on the -Y wall at z 160 (x 1983..2035, east of the "
                         "counter run), outlets N2/N3/N6/N8 on the +Y wall at "
                         "z 600 (x 1956..2045), N4 drain at (900, 360) under the "
                         "counter, N5 vent at (2000, 2985) on the +Y wall line "
                         "through the top face; per-tag positions in "
                         "check.nozzles_drawn",
        "hardware_idiom": "connection hardware flush at the envelope faces",
    },
}


def parts(P):
    return farm_closeout.unit_parts(P, SPEC)


if __name__ == "__main__":
    farm_closeout.build_and_export(HERE, SPEC)

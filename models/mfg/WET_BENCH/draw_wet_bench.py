"""WET_BENCH drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, bench01 (plinth + deck + frame),
baths01 (the four wet baths + heater envelopes), aux01 (connection hardware),
iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets                                       # noqa: E402

ns = runpy.run_path(HERE / "wet_bench.py")
parts, R = ns["parts"], ns["report"]
unit = "WET_BENCH"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


bench = union_all([parts["plinth"], parts["deck"], parts["frame"]])
baths = union_all([parts["baths"], parts["heaters"]])
aux = parts["nozzles"]
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
BM = R["bath_mass_kg"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm envelope - the node size_mm '
      f'({R["size_basis"] or "node size_mm"}); the duty section 2 states no '
      'envelope - the node governs (hold W12)',
      'RCA/etch wet bench per the node equipment list: SC1 and SC2 baths 10 L '
      'at 80 C with immersion heater envelopes, DHF etch bath at ambient, DIW '
      'rinse bay',
      'Wetted material per duty section 3: PVC-U per AQS-STD-002 M1/M2, no '
      'metal wetted part; above 60 C the thermoplastic is CPVC - the node '
      'equipment rows give the 80 C bath temperatures, so SC1/SC2 are CPVC',
      'The node equipment rows name PP tanks; the duty selection governs '
      '(plan rule 5; hold W12)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     [f'Bath masses from the model: SC1 {BM["sc1"]:g} kg, SC2 {BM["sc2"]:g} kg, '
      f'DHF {BM["dhf"]:g} kg, rinse {BM["rinse"]:g} kg (wall 10 study, W12)',
      'A-MACH guard: the hold-down frame pins the registry box so the build '
      'fills the node envelope (X-PAR-04); 8 slab anchors (fasteners.csv)',
      'Bath arrangement and the unstated bath sizes (DHF, rinse) are the '
      'layout choice (WORK_ORDER W12)'],
     "General arrangement, side elevation (end view). Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     ['13 schedule rows of docs-authority/nozzles/WET_BENCH.csv at tag, face '
      'and bore',
      'Inlets on -Y at z 160: N1 HCl, N2 DN25 fab UPW, N3 HF (aq), N4 H2O2, '
      'N9 NH4OH/NH3, N10 KOH, N11 HNO3, N12 H3PO4, N13 ethanol and acetone; '
      'outlets on +Y at z 600: N5 DN25 spent etch, N6 resist and solvent waste',
      'N7 drain flush at the envelope bottom (50 datum); N8 vent flush at the '
      'envelope top (800 datum is the box top)',
      'Atmospheric open-bore tube stubs drawn polymer per duty section 3 (no '
      'metal wetted part); the schedule rating column (Class 150) carried '
      'verbatim as text'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("bench01", bench, (0, 1, 0),
     ['Bench deck on the 20 mm plinth inside the four-post hold-down/guard '
       'frame (40 x 40 posts, top rails), AQS-MOD-002 dry service',
      'The frame pins the registry box so the build fills the node envelope '
      '(X-PAR-04); 8 M12 slab anchors (fasteners.csv)',
      'Carbon steel (ASTM A500); the frame is dry structure outside the wetted '
      'polymer'],
     "Fabricated part sheet: bench, plinth and hold-down frame."),
    ("baths01", baths, (1, -1, 1),
     ['SC1 and SC2: 10 L nominal (inner 250 x 250 x 160), wall 10 (study), '
       'CPVC per the duty 60 C rule at the node 80 C bath temperatures; '
       'immersion heater envelopes are the purchased units (plan rule 6)',
       'DHF etch and DIW rinse baths: drawn to their bays (no bath size stated '
       'on the node - hold W12), PVC-U per duty section 3 (AQS-STD-002 M1/M2)',
       'Thermoplastic welds per the unit route (F-MACH applied to the '
       'thermoplastic shop: DVS 2207 class practice)'],
     "Fabricated part sheet: wet baths and heater envelopes."),
    ("aux01", aux, (0, 1, 0),
     ['Connection hardware DN15/DN25 as open-bore tube stubs flush at the '
      'envelope faces, drawn polymer per duty section 3 (no metal wetted '
      'part); atmospheric per duty section 4 (no flange class)',
      'All 13 schedule rows present at tag, face, height and bore; per-tag '
      'positions in check.nozzles_drawn',
      'The stub ODs follow the DN series (the steel pipe table); the polymer '
      'tube wall is the supplier rule (hold, W12)'],
     "Fabricated part sheet: connection hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: reagents and fab UPW in on -Y, spent etch and '
      'solvent waste out on +Y; drain at the bottom, vent at the top',
      f'Graph revision {R["graph_revision"]} is the model authority for this '
      'build; STEP (export/wet_bench.step) is the solids of record',
      'Tracker --check green; acceptance A-core + A-MACH + A-SC per '
      'AQS-PLAN-006 section 5'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/wet_bench.py", f"models/mfg/{unit}/draw_wet_bench.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ["- Bench per the node equipment list: SC1/SC2 baths 10 L at 80 C with "
     "immersion heater envelopes (2.479 kWh/d each), DHF etch bath at ambient, "
     "DIW rinse bay; bath arrangement and the unstated bath sizes are the "
     "layout choice (W12)",
     "- Wetted material per duty section 3: PVC-U per AQS-STD-002 M1/M2, no "
     "metal wetted part; the 80 C baths are CPVC per the duty 60 C rule (the "
     "node equipment rows give the temperatures); the node rows name PP tanks, "
     "the duty selection governs (plan rule 5; hold W12)",
     "- A-MACH guard: the four-post hold-down frame pins the registry box so "
     "the build fills the envelope (X-PAR-04); 8 slab anchors in fasteners.csv"],
    "A-core + A-MACH + A-SC")

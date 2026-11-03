"""LITHO_DEV drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, frame01 (base + hold-down frame),
bowl01 (develop bowl + dispense point), aux01 (connection hardware), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets                                       # noqa: E402

ns = runpy.run_path(HERE / "litho_dev.py")
parts, R = ns["parts"], ns["report"]
unit = "LITHO_DEV"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


frame = union_all([parts["base"], parts["frame"]])
bowl = union_all([parts["bowl"], parts["dispense"]])
aux = parts["nozzles"]
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
B = R["machine"]["bowl"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm envelope - the node size_mm '
      f'({R["size_basis"] or "node size_mm"}, issued envelope A-M-287)',
      'Duty section 2 prose carries the seed figure 500 x 500 x 800; the node '
      'governs and the older figure is named (hold W12, the WS_SOLV precedent)',
      'Wet develop bench per the node design block and note (A-M-287): TMAH '
      '2.38 % class developer on the shared WET_BENCH chemistry fork, puddle '
      '40 mL/wafer, waste on the S38-class resist/solvent loop',
      'Wetted parts 316L per duty section 3 (developer); CA 0 mm (AQS-STD-001)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     [f'Develop bowl inner {B["inner_mm"][0]:g} x {B["inner_mm"][1]:g} x '
      f'{B["inner_mm"][2]:g} ({B["nominal_l"]:g} L nominal, wall 10 study - '
      'the bowl size is the layout choice, hold W12)',
      'Hold-down frame (40 x 40 posts + top rails) pins the registry box so '
      'the build fills the node envelope (X-PAR-04); 8 slab anchors',
      'No purchased item is named on the node or duty, so none is drawn (the '
      'WS_SOLV precedent); the guard and anchors are drawn'],
     "General arrangement, side elevation (end view). Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     ['4 schedule rows of docs-authority/nozzles/LITHO_DEV.csv at tag, face '
      'and bore',
      'N4 (resist/solvent carry in from the coat bench) at x 600 on -Y at z '
      '160; N3 (spent resist and solvent out) at x 660 on +Y at z 600 - both '
      'solids transfer rows drawn DN15, bore not calculated (plan W4)',
      'N1 drain flush at the envelope bottom (50 datum); N2 vent flush at the '
      'envelope top - its 800 datum predates the 900 box (hold W12)',
      'Atmospheric hose per duty section 4 (DN copied from the edge and not '
      'recalculated)'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("frame01", frame, (0, 1, 0),
     ['Base plate and hold-down/guard frame (40 x 40 posts, top rails), '
       'carbon steel A500 (AQS-MOD-002 dry service)',
       'The frame pins the registry box so the build fills the node envelope '
       '(X-PAR-04); 8 M10 slab anchors (fasteners.csv)',
       'Dry structure outside the wetted 316L station'],
     "Fabricated part sheet: base plate and hold-down frame."),
    ("bowl01", bowl, (1, -1, 1),
     ['Develop bowl: inner 300 x 200 x 120 (7.2 L nominal), wall 10 (study), '
       '316L per duty section 3 (CA 0 mm, AQS-STD-001)',
       'Puddle dispense point envelope above the bowl (40 mL/wafer per the '
       'node design)',
       'Thermoplastic-free wetted path: TMAH class developer on the shared '
       'WET_BENCH chemistry fork (node design)'],
     "Fabricated part sheet: develop bowl and dispense point (wetted 316L)."),
    ("aux01", aux, (0, 1, 0),
     ['Connection hardware DN15 tube stubs flush at the envelope faces; '
      'atmospheric hose per duty section 4 (no flange class)',
      'All 4 schedule rows present at tag, face, height and bore; per-tag '
      'notes in check.nozzles_drawn',
      'The schedule rating column (Class 150) carried verbatim as text'],
     "Fabricated part sheet: connection hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: the carry stream from the coat bench in on -Y, '
      'spent resist and solvent out on +Y to the S38 loop; drain at the '
      'bottom, vent at the top',
      f'Graph revision {R["graph_revision"]} is the model authority for this '
      'build; STEP (export/litho_dev.step) is the solids of record',
      'Tracker --check green; acceptance A-core + A-MACH + A-SC per '
      'AQS-PLAN-006 section 5'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/litho_dev.py", f"models/mfg/{unit}/draw_litho_dev.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ["- Wet develop bench per the node design block and note (A-M-287): "
     "develop bowl in 316L per duty section 3 with the puddle dispense point "
     "envelope (40 mL/wafer); the TMAH class developer is the shared "
     "WET_BENCH chemistry fork; waste on the S38-class loop to OIL_FRAC",
     "- Duty section 2 prose carries the seed figure 500 x 500 x 800; the node "
     "1200 x 600 x 900 governs, the older figure named (hold W12)",
     "- Hold-down frame pins the registry box so the build fills the envelope "
     "(X-PAR-04); no purchased item is named, so none is drawn (WS_SOLV "
     "precedent)"],
    "A-core + A-MACH + A-SC")

"""LITHO_COAT drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, frame01 (base + guard frame),
bowl01 (spin bowl, catch bowl, stand, chuck), aux01 (purchased envelopes +
hardware), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets                                       # noqa: E402

ns = runpy.run_path(HERE / "litho_coat.py")
parts, R = ns["parts"], ns["report"]
unit = "LITHO_COAT"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


frame = union_all([parts["base"], parts["frame"]])
bowl = union_all([parts["spin_bowl"], parts["catch_bowl"], parts["stand"],
                  parts["chuck"]])
aux = union_all([parts["motor"], parts["hotplate"], parts["nozzles"]])
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm envelope - the node size_mm '
      f'({R["size_basis"] or "node size_mm"}, issued envelope A-M-287)',
      'Duty section 2 prose carries the seed figure 600 x 500 x 800; the node '
      'governs and the older figure is named (hold W12, the WS_SOLV precedent)',
      'Spin-coater line per the node design block and note (A-M-287): spin '
      'bowl, vacuum chuck 150 mm (node chuck_mm), softbake hotplate; spin '
      '5000 rpm, dispense 2.0 mL, novolac 1 um',
      'Wetted parts 316L per duty section 3 (resist/solvent); CA 0 mm '
      '(AQS-STD-001)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Spin-chuck motor 0.75 kW peak and softbake hotplate 0.3 kW at the '
      '100 C hold are purchased envelopes per plan rule 6 (ratings from the '
      'node)',
      'Guard frame (40 x 40 posts + top rails) pins the registry box so the '
      'build fills the node envelope (X-PAR-04); 8 slab anchors',
      'The vacuum source for the chuck is not named on the node or duty - '
      'none drawn (hold W12)'],
     "General arrangement, side elevation (end view). Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     ['4 schedule rows of docs-authority/nozzles/LITHO_COAT.csv at tag, face '
      'and bore',
      'N3 (spent resist and solvent in) at x 600 on -Y at z 160; N4 '
      '(resist/solvent carry to the develop bench) at x 660 on +Y at z 600 - '
      'both solids transfer rows drawn DN15, bore not calculated (plan W4)',
      'N1 drain flush at the envelope bottom (50 datum); N2 vent flush at the '
      'envelope top - its 800 datum predates the 1400 box (hold W12)',
      'Atmospheric hose per duty section 4 (DN copied from the edge and not '
      'recalculated)'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("frame01", frame, (0, 1, 0),
     ['Base plate and guard frame (40 x 40 posts, top rails), carbon steel '
       'A500 (AQS-MOD-002 dry service)',
       'The frame pins the registry box so the build fills the node envelope '
       '(X-PAR-04); 8 M10 slab anchors (fasteners.csv)',
       'Dry structure outside the wetted 316L station'],
     "Fabricated part sheet: base plate and guard frame."),
    ("bowl01", bowl, (1, -1, 1),
     ['Spin bowl OD 360 x 200, wall 10 (study - the envelope sizes are the '
       'layout choice around the node 150 mm chuck, hold W12), rim collar, '
       'on the stand',
       'Coat catch bowl OD 480 x 60 tray - the IA-LITHO-CARRY stream names '
       'the coat catch bowl',
       'Vacuum chuck D 150 (node chuck_mm) on the spindle; 316L per duty '
       'section 3 (CA 0 mm, AQS-STD-001)'],
     "Fabricated part sheet: spin station (wetted 316L)."),
    ("aux01", aux, (0, 1, 0),
     ['Purchased envelopes per plan rule 6: spin-chuck motor 0.75 kW peak '
      '(node spin_peak_kW); softbake hotplate 0.3 kW at the 100 C hold '
      '(node softbake_kW/softbake_C)',
      'Connection hardware DN15 tube stubs flush at the envelope faces; '
      'atmospheric hose per duty section 4',
      'The schedule rating column (Class 150) carried verbatim as text'],
     "Fabricated part sheet: purchased envelopes and hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: the spin axis is vertical at (300, 400); the '
      'hotplate sits beside the bowl on the deck',
      f'Graph revision {R["graph_revision"]} is the model authority for this '
      'build; STEP (export/litho_coat.step) is the solids of record',
      'Tracker --check green; acceptance A-core + A-SC (route hold: no '
      'section 4 class row names the coater class) per AQS-PLAN-006 '
      'section 5'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/litho_coat.py", f"models/mfg/{unit}/draw_litho_coat.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ["- Spin-coater line per the node design block and note (A-M-287): spin "
     "bowl and coat catch bowl in 316L per duty section 3, the 150 mm vacuum "
     "chuck (node chuck_mm) on the spindle, and the spin-chuck motor (0.75 kW "
     "peak) and softbake hotplate (0.3 kW, 100 C hold) as purchased envelopes "
     "per plan rule 6 with the node ratings",
     "- Duty section 2 prose carries the seed figure 600 x 500 x 800; the node "
     "1200 x 800 x 1400 governs, the older figure named (hold W12)",
     "- Guard frame pins the registry box so the build fills the envelope "
     "(X-PAR-04); anchors in fasteners.csv"],
    "A-core + A-SC (route hold)")

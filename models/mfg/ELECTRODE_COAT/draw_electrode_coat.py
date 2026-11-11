"""ELECTRODE_COAT drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, frame01 (base + guard frame),
hood01 (booth hood + wetted interior), aux01 (purchased envelopes + hardware),
iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets, step_export  # noqa: E402

ns = runpy.run_path(HERE / "electrode_coat.py")
parts, R = ns["parts"], ns["report"]
unit = "ELECTRODE_COAT"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


frame = union_all([parts["base"], parts["frame"]])
hood = union_all([parts["hood"], parts["tray"], parts["racks"], parts["spray"]])
aux = union_all([parts["cure"], parts["exhaust"], parts["nozzles"]])
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm envelope - the node size_mm '
      f'({R["size_basis"] or "node size_mm"}); the duty section 2 envelope '
      'line agrees with the node',
      'Electrode coating booth per the node design block and AQS-MFG-ELC-001 '
      'Rev D (named on the node note): open-front hood, coat head, IR cure '
      'panel, exhaust fan; carbon/Ni non-precious M1 class (RuO2-IrO2 '
      'deferred)',
      'Exhaust routing per the node design line: MET_AHU -> MET_SCRUB '
      '(S71-S72), named at the vent; the afterburner is not the primary '
      'treatment (AQS-MFG-ELC-001 section 3.2)',
      'Wetted hardware 316L per duty section 3 (coating slurry); CA 0 mm '
      '(AQS-STD-001)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['ELC-CURE-01 IR cure panel 1.2 kW and ELC-EXH-01 exhaust fan 0.35 kW '
      'are purchased envelopes per plan rule 6 (ratings from the node)',
      'AQS-MFG-ELC-001: coating recipes and equipment nameplates are not '
      'designed - the coat head is an envelope, no internals invented (hold '
      'W12)',
      'Guard frame (40 x 40 posts + top rails) pins the registry box so the '
      'build fills the node envelope (X-PAR-04); 8 slab anchors'],
     "General arrangement, side elevation (end view). Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     ['4 schedule rows of docs-authority/nozzles/ELECTRODE_COAT.csv at tag, '
      'face and bore',
      'N3 (nickel sheet to the booth) at x 600 on -Y at z 160; N4 (coated '
      'anode) at x 660 on +Y at z 600 - both solids transfer rows drawn DN15, '
      'bore not calculated (plan W4)',
      'N1 tray drain flush at the envelope bottom (50 datum); N2 hood exhaust '
      'flush at the envelope top - its 800 datum predates the 1800 box (hold '
      'W12); destination MET_AHU named',
      'Atmospheric hose per duty section 4 (no flange class)'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("frame01", frame, (0, 1, 0),
     ['Base plate and guard frame (40 x 40 posts, top rails), carbon steel '
       'A500 (AQS-MOD-002 dry service)',
       'The frame pins the registry box so the build fills the node envelope '
       '(X-PAR-04); 8 M10 slab anchors + 12 M8 hood-panel bolts '
       '(fasteners.csv)',
       'Dry structure outside the wetted 316L interior'],
     "Fabricated part sheet: base plate and guard frame."),
    ("hood01", hood, (1, -1, 1),
     ['Booth hood: back, side and top sheet panels (5 study, open front on '
       '-Y), per AQS-MFG-ELC-001 section 3.2 (metal aisle, exhaust to '
       'MET_AHU)',
       'Drip tray and electrode rack rails 316L per duty section 3 (coating '
       'slurry; CA 0 mm, AQS-STD-001); substrates (316L-stainless or titanium '
       'mesh/plate) are the workpiece, not drawn',
       'Coat head envelope (ELC-SPRAY-01) wetted class; envelope + interface '
       'per plan rule 6'],
     "Fabricated part sheet: booth hood and wetted interior."),
    ("aux01", aux, (0, 1, 0),
     ['Purchased envelopes per plan rule 6: IR cure panel (ELC-CURE-01, 1.2 '
      'kW) and exhaust fan (ELC-EXH-01, 0.35 kW), ratings from the node',
      'Connection hardware DN15 tube stubs flush at the envelope faces; '
      'atmospheric hose per duty section 4',
      'The schedule rating column (Class 150) carried verbatim as text'],
     "Fabricated part sheet: purchased envelopes and hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: the open front faces -Y toward the metal aisle '
      'walkway; the exhaust rises at the hood top rear',
      f'Graph revision {R["graph_revision"]} is the model authority for this '
      'build; STEP (export/electrode_coat.step) is the solids of record',
      'Tracker --check green; acceptance A-core + A-SC (route hold: no '
      'section 4 class row names the coater class) per AQS-PLAN-006 '
      'section 5'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/electrode_coat.py", f"models/mfg/{unit}/draw_electrode_coat.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ["- Coating booth per the node design block and AQS-MFG-ELC-001 Rev D: "
     "open-front hood over a 316L drip tray, coat-head envelope (ELC-SPRAY-01), "
     "IR cure panel (ELC-CURE-01, 1.2 kW) and exhaust fan (ELC-EXH-01, "
     "0.35 kW) as purchased envelopes per plan rule 6; recipes and nameplates "
     "are not designed - no internals invented (hold W12)",
     "- Exhaust routing named at the vent: MET_AHU -> MET_SCRUB (S71-S72) per "
     "the node design line and AQS-MFG-ELC-001 section 3.2",
     "- Guard frame pins the registry box so the build fills the envelope "
     "(X-PAR-04); anchors in fasteners.csv"],
    "A-core + A-SC (route hold)")

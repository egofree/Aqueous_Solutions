"""OIL_DRYER drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, drum01 (drum + jacket), frame01
(guard frame + saddles + plinth), aux01 (connection hardware), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets                                       # noqa: E402

ns = runpy.run_path(HERE / "oil_dryer.py")
parts, R = ns["parts"], ns["report"]
unit = "OIL_DRYER"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


drum = union_all([parts["drum"], parts["jacket"]])
frame = union_all([parts["plinth"], parts["saddles"], parts["frame"]])
aux = parts["nozzles"]
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
M = R["machine"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm envelope - the node size_mm ({R["size_basis"]})',
      'Horizontal jacketed drying drum drawn to the envelope: drum OD 500 x 700, '
      'jacket annulus 20 mm (study values - holds, W12), on two saddles over the '
      '20 mm plinth',
      'A-MACH guard: four-post guard frame (40 x 40 posts, mid and top rails) pins '
      'the envelope around the drum',
      'Carbon steel (duty section 3), CA 1.5 mm (AQS-STD-001 hydrocarbon rule)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Drum axis at y 300, z 430; saddle tops pierce the drum annulus (fuse idiom); '
      'jacket end plates lap the drum over the mid-span',
      'Duty basis: float plastics 33 kg/d dried and out to OIL_PYRO; the N1/N2 '
      'jacket rows carry the HX-4 Q3 process heat (schedule service text verbatim)',
      'No purchased items named on the node or duty: no equipment row exists, so '
      'the dryer drive and vacuum hardware are not drawn (A-MACH hold, W12)'],
     "General arrangement, side elevation (end view). Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     ['7 schedule rows of docs-authority/nozzles/OIL_DRYER.csv at tag, face and bore',
      'N1/N2 DN15 (HX-4 Q3 process heat, dryer jacket) and N3 DN25 (float plastics '
      'in) on -Y at z 160; N4 DN25 (dried plastics to OIL_PYRO) and N5 DN15 (dryer '
      'reject) on +Y at z 600',
      'N6 drain flush at the envelope bottom (50 datum); N7 vent flush at the '
      'envelope top (800 datum is the box top)',
      'Atmospheric open-bore tube stubs per duty section 4 (nozzle DN15, no flange '
      'class); the schedule rating column (Class 150) carried verbatim as text'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("drum01", drum, (0, 1, 0),
     [f'Drum OD {M["drum_od_mm"]:g} x {M["length_mm"]:g}, wall {M["wall_mm"]:g} mm '
      '(study value - no authority states a drum wall, hold W12)',
      f'Jacket OD {M["drum_od_mm"] + 2 * M["jacket_mm"]:g}, annulus {M["jacket_mm"]:g} '
      'mm (study value, hold W12), end plates lap the drum; the jacket is the HX-4 '
      'Q3 heat surface (schedule N1/N2)',
      'CA 1.5 mm (AQS-STD-001 hydrocarbon rule); welds per the unit route (F-MACH)'],
     "Fabricated part sheet: drying drum + heating jacket."),
    ("frame01", frame, (0, 1, 0),
     ['Guard frame per A-MACH: four 40 x 40 posts full height, mid rails at z 300 '
      'and top rails at the envelope top',
      'Two saddles (tops pierce the drum annulus) + plinth 1000 x 600 x 20 '
      '(AQS-MOD-002 dry service)',
      '8 M12 slab anchors and 8 M12 saddle bolts (fasteners.csv); frame pins the '
      'envelope (X-PAR-04)'],
     "Fabricated part sheet: guard frame + supports."),
    ("aux01", aux, (0, 1, 0),
     ['Connection hardware DN15/DN25 as open-bore tube stubs flush at the envelope '
      'faces; atmospheric per duty section 4 (no flange class)',
      'All 7 schedule rows present at tag, face, height and bore; per-tag '
      'positions in check.nozzles_drawn',
      'The N1/N2 service text (HX-4 Q3 process heat, dryer jacket) matches the '
      'drawn jacket; the schedule rating column (Class 150) is carried verbatim as '
      'text'],
     "Fabricated part sheet: connection hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: plastics and jacket heat in on -Y, dried plastics out to '
      'OIL_PYRO and reject out on +Y; drain and vent on the run centreline',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/oil_dryer.step) is the solids of record',
      'Tracker --check green; acceptance A-core + A-MACH per AQS-PLAN-006 '
      'section 5'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/oil_dryer.py", f"models/mfg/{unit}/draw_oil_dryer.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ["- Machine: horizontal jacketed drying drum OD 500 x 700 (wall 6, study), "
     "jacket annulus 20 (study) as the HX-4 Q3 heat surface, on saddles over a "
     "20 mm plinth (holds, W12)",
     "- A-MACH: guard frame drawn (four posts, mid and top rails) and anchors in "
     "fasteners.csv; no purchased items named on the node or duty - none drawn "
     "(hold, W12)",
     "- Duty basis: float plastics 33 kg/d dried and out to OIL_PYRO; the "
     "internals row is none and the duty claims no holdup basis, so none is "
     "drawn"],
    "A-core + A-MACH")

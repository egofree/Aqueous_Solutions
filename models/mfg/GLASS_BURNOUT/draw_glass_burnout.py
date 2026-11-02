"""GLASS_BURNOUT drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, drum01 (burnout drum), stands01
(plinth + trunnion stands), aux01 (connection hardware), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets                                       # noqa: E402

ns = runpy.run_path(HERE / "glass_burnout.py")
parts, R = ns["parts"], ns["report"]
unit = "GLASS_BURNOUT"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


drum = parts["drum"]
stands = union_all([parts["plinth"], parts["stands"]])
aux = parts["nozzles"]
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
M = R["machine"]
LL = R["line_list"]
X = R["nozzles_drawn"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm envelope - the node size_mm ({R["size_basis"]})',
      'Burnout rotary drum OD 560 x 700, wall 12 mm (study - hold, W12), between two '
      'tire rings on trunnion stands (ported AQS-MFG-001 form mfg_burnout_rotary.scad)',
      f'Drum-full volume {M["v_full_m3"]:g} m3 against the duty section 2 seven-day '
      f'charge {M["charge_duty_m3"]:g} m3: reported, nothing resized (plan rule 3)',
      'Material 316L (duty section 3); CA 0 mm (AQS-STD-001 rule)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Drum axis at y 300, z 520; end-head shaft stubs run in plain housings on '
      'pedestals from the 20 mm plinth (ported UCP213 form)',
      'Rotary drive not designed: no drive is named on the node or duty (hold, W12)',
      'Tire rings OD 584 x 30 at x 170/630 are drum features (rotating wear rings)'],
     "General arrangement, side elevation (end view). Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     ['7 schedule rows of docs-authority/nozzles/GLASS_BURNOUT.csv at tag, face and bore',
      'N1 DN25 (milled cullet) and N2 DN15 (fuel) on -Y at z 160; N3/N4 DN15 (Q2 '
      'burnout, not Q4 - row quoting repaired) and N5 DN25 (burned cullet) on +Y at z 600',
      'N6 drain flush at the envelope bottom (50 datum); N7 vent flush at the envelope '
      'top (schedule datum 800 predates the 1200 box - hold, W12)',
      'Atmospheric hose barbs per duty section 4; the schedule rating column (Class '
      '150) is carried verbatim as text, no flange drawn (no process pressure stated)'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("drum01", drum, (0, 1, 0),
     [f'Burnout drum OD {M["drum_od_mm"]:g} x {M["drum_len_mm"]:g}, wall {M["wall_mm"]:g} mm '
      '(study value - no authority states a drum wall, hold W12)',
      'End heads 10 mm; trunnion shaft stubs pierce the end heads; tires OD 584 x 30',
      '316L per duty section 3; CA 0 mm (AQS-STD-001 316L rule)'],
     "Fabricated part sheet: burnout drum."),
    ("stands01", stands, (0, 1, 0),
     ['Plinth 800 x 600 x 20 (AQS-MOD-002 dry service) + two trunnion stands: '
      '130 x 70 base plate, pedestal, OD 120 plain housing at each shaft',
      'Housing bores and pedestal fit are study proportions, confirmed at fabrication '
      '(hold, W12)',
      'Carbon steel (ASTM A500); 8 M10 slab anchors and 4 M12 housing bolts '
      '(fasteners.csv)'],
     "Fabricated part sheet: plinth + trunnion stands."),
    ("aux01", aux, (0, 1, 0),
     ['Connection hardware DN15/DN25 as atmospheric hose barbs flush at the envelope '
      'faces (lib/nozzles.py); barb profile a study proportion, finished against the '
      'hose supplier print',
      'All 7 schedule rows present at tag, face, height and bore; per-tag positions in '
      'check.nozzles_drawn',
      f'The A-PIPE line list of record is line_list.csv: {LL["rows"]} rows generated '
      'from the unit edges and AQS-PIP-004; no new edge (the two Q2 heat-recovery '
      'lines ride study edges and are carried verbatim)'],
     "Fabricated part sheet: connection hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: cullet and fuel in on -Y, burned cullet and the Q2 '
      'heat-recovery takeoffs out on +Y; drain and vent on the run centreline',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/glass_burnout.step) is the solids of record',
      'Tracker --check green; acceptance A-core + A-PIPE per AQS-PLAN-006 section 5'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/glass_burnout.py", f"models/mfg/{unit}/draw_glass_burnout.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/line_list.csv", f"models/mfg/{unit}/check.json",
     f"models/mfg/{unit}/WORK_ORDER.md"],
    [f"- A-PIPE line list: line_list.csv generated from the unit's graph edges and "
     f"docs-authority/LINE_LIST.md (AQS-PIP-004): {LL['rows']} rows, "
     "tag/from/to/DN/class/service/rating; the HL-GLASS_BURNOUT-Q2-A/B rows ride "
     "study edges and carry the study note; edge coverage complete, no new edge",
     "- Machine: burnout rotary drum OD 560 x 700, wall 12 (study), on trunnion "
     "stands; drum-full 0.1579 m3 against the 0.2100 m3 duty section 2 seven-day "
     "charge - reported, nothing resized (plan rule 3)",
     "- Schedule N3/N4 rows repaired to the schedule quoting (service text carried an "
     "unquoted comma that shifted face and height); the change record is in "
     "notes/glass_oilgas_m3_2026-11-02.md"],
    "A-core + A-PIPE")

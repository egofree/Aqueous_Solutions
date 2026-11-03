"""GLASS_RINSE drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, bath01 (rinse bath), aux01
(connection hardware + plinth), iso01, and a second part sheet frame01 (plinth).

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets                                       # noqa: E402

ns = runpy.run_path(HERE / "glass_rinse.py")
parts, R = ns["parts"], ns["report"]
unit = "GLASS_RINSE"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


bath = parts["bath"]
plinth = parts["plinth"]
aux = parts["nozzles"]
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
M = R["machine"]
LL = R["line_list"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm envelope - the node size_mm ({R["size_basis"]})',
      'Open-topped rinse bath to the envelope: 316L walls 10 mm (study - hold, W12), '
      'inside 1180 x 580, on the 20 mm plinth (ported AQS-MFG-001 form mfg_rinse.scad)',
      f'Bath volume to the 100 mm freeboard {M["v_bath_m3"]:g} m3 against the duty '
      f'section 2 seven-day charge {M["charge_duty_m3"]:g} m3: reported, nothing '
      'resized (plan rule 3)',
      'Material 316L (duty section 3); CA 0 mm (AQS-STD-001 rule)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Bath walls sit on the base head; the freeboard line sits 100 mm below the rim',
      'Dewater pump not drawn: no pump is named on the node or duty (hold, W12; the '
      'legacy form carried a DN80 pump hint only)',
      'Liquor leaves to SALT FEED, not the sewer (legacy form note carried by the '
      'line list)'],
     "General arrangement, side elevation (end view). Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     ['4 schedule rows of docs-authority/nozzles/GLASS_RINSE.csv at tag, face and bore',
      'N1 DN25 (cullet in) on -Y at z 160; N2 DN25 (rinsed cullet out to the mill) '
      'on +Y at z 600',
      'N3 drain flush at the envelope bottom (50 datum); N4 vent flush at the '
      'envelope top (800 datum is the box top)',
      'Atmospheric hose barbs per duty section 4; the schedule rating column (Class '
      '150) is carried verbatim as text, no flange drawn (no process pressure stated)'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("bath01", bath, (0, 1, 0),
     [f'Rinse bath {L:g} x {W:g} x {H - 20:g}, wall {M["wall_mm"]:g} mm (study value '
      '- no authority states a tank wall, hold W12)',
      'Open top; base head 10 mm on the plinth; corners are squarebutt welds per the '
      'unit route (F-PIPE applied to machine hardware)',
      '316L per duty section 3; CA 0 mm (AQS-STD-001 316L rule)'],
     "Fabricated part sheet: rinse bath."),
    ("frame01", plinth, (0, 1, 0),
     ['Plinth 1200 x 600 x 20 (AQS-MOD-002 dry service class)',
      '8 M10 slab anchors (fasteners.csv)',
      'Carbon steel (ASTM A500)'],
     "Fabricated part sheet: plinth."),
    ("aux01", aux, (0, 1, 0),
     ['Connection hardware DN25 as atmospheric hose barbs flush at the envelope '
      'faces (lib/nozzles.py); barb profile a study proportion, finished against the '
      'hose supplier print',
      'All 4 schedule rows present at tag, face, height and bore; per-tag positions '
      'in check.nozzles_drawn',
      f'The A-PIPE line list of record is line_list.csv: {LL["rows"]} rows generated '
      'from the unit edges and AQS-PIP-004; no new edge'],
     "Fabricated part sheet: connection hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: cullet in on -Y at z 160, rinsed cullet out on +Y at z 600 '
      'to the mill; drain and vent on the run centreline',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/glass_rinse.step) is the solids of record',
      'Tracker --check green; acceptance A-core + A-PIPE per AQS-PLAN-006 section 5'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/glass_rinse.py", f"models/mfg/{unit}/draw_glass_rinse.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/line_list.csv", f"models/mfg/{unit}/check.json",
     f"models/mfg/{unit}/WORK_ORDER.md"],
    [f"- A-PIPE line list: line_list.csv generated from the unit's graph edges and "
     f"docs-authority/LINE_LIST.md (AQS-PIP-004): {LL['rows']} rows, "
     "tag/from/to/DN/class/service/rating; edge coverage complete, no new edge",
     "- Machine: open-topped rinse bath to the envelope, walls 10 (study); bath "
     "volume 0.4585 m3 to the 100 mm freeboard against the 0.2577 m3 duty section 2 "
     "seven-day charge - reported, nothing resized (plan rule 3); dewater pump not "
     "drawn (no pump named on the node or duty, hold W12)"],
    "A-core + A-PIPE")

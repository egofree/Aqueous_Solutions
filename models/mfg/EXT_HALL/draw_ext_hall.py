"""EXT_HALL drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, plan (the L-shape and the column grid), bay01 (one
6 m bay massing), roof01 (roof deck + PV interface note), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets, step_export  # noqa: E402

ns = runpy.run_path(HERE / "ext_hall.py")
parts, R = ns["parts"], ns["report"]
unit = "EXT_HALL"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


full = union_all(list(parts.values()))
frame_only = union_all([parts["slab"], parts["frame_grid"], parts["roof"]])

L, W, H = [float(v) for v in R["size_mm"]]
M = R["machine"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L/1000:g} x {W/1000:g} x {H/1000:g} m building massing envelope - '
      'the node size_mm (bounding box of the issued L-shape; EXT_HALL_E 162 x 174 m '
      '+ EXT_HALL_N 24 x 156 m, placement_seed blocks are the authority)',
      'Steel portal frames on the 6 m grid (31 x 29 bays of the size note; '
      'columns at every grid point inside the L); 6 m eave; insulated metal roof '
      'and wall panels to the IECC U-factors (A-M-104)',
      'Roof framing for LRFD 1.72 kPa (A-M-105, ASCE 7-22); the roof PV interface '
      'is the PV_ARRAY model (15 array tables, accepted separately)',
      'No process internals: the fitout programme stays the duty-sheet open item '
      '(duty section 8)'],
     "General arrangement, front elevation (south). Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['East elevation across the 174 m depth; wall panels 300 mm from slab to '
      'eave (IECC wall U 0.534 class, A-M-104)',
      'On-grade slab 150 mm (massing); the foundation design is the X-BLD lane\'s '
      '(hold, WORK_ORDER W12)',
      'NORTH_DOCK opens into EXT_HALL_N; the 6 m truck lane to the north wall is '
      'reserved (duty section 7, accepted 2026-10-15)'],
     "General arrangement, side elevation (east). Shop, not stamped."),
    ("plan", full, (0, 0, -1),
     ['Plan: the L-shape (E block x 24..186 m, N block x 0..24 m y 18..174 m) and '
      f'the column grid at the 6 m bay lines ({M["grid"]["columns"]} columns)',
      'Perimeter wall lines on the L-footprint; the E/N boundary is open between '
      'the blocks (one hall)',
      'No nozzles: duty section 4 states None (electrical feed SF-EXT_HALL, air-'
      'source heat pumps D77, GEO_GHEX not coupled)'],
     "General arrangement, plan. Tags per the issued blocks."),
    ("bay01", frame_only, (1, -1, 1),
     ['One 6 x 6 m bay of the portal-frame grid: 300 x 300 columns from slab to '
      'the roof deck at the grid points (massing sections)',
      'Section sizes are massing values - the structural design (member '
      'selection, base plates, anchors) is the X-BLD lane\'s (hold, WORK_ORDER W12)',
      'Steel sections made in-house (duty section 3, X-MFG-32); 4 M20 base bolts '
      'per column (fasteners.csv)'],
     "Fabricated part sheet: the portal-frame bay massing."),
    ("roof01", full, (0, 0, 1),
     ['Roof deck 100 mm at z 5900..6000 over the L (IECC roof U 0.199 class, '
      'A-M-104); roof framing for LRFD 1.72 kPa (A-M-105)',
      'Roof PV access per IFC 2027 1205.3 / NFPA 1 11.12: the 1829 mm perimeter '
      'pathway and the 15 array tables are the PV_ARRAY model\'s scope',
      'Roof load figures (A-M-105) are stamped on the PV node - nothing doubled '
      'here'],
     "Fabricated part sheet: roof deck + PV interface."),
    ("iso01", full, (1, -1, 1),
     ['Site orientation: E block east of the base plate, N block north of it; '
      'the west yard stays outdoor (NFPA 855, X-PAR-07)',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/ext_hall.step) is the solids of record',
      'Tracker --check green; acceptance A-core per AQS-PLAN-006 section 5 '
      '(route hold: building has no section 4 class)'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/ext_hall.py", f"models/mfg/{unit}/draw_ext_hall.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ["- Building massing per the node size_note and the placement_seed blocks "
     "(the authority): 162 x 174 m + 24 x 156 m L-shape, 6 m eave; slab 150 mm, "
     f"wall panels 300 mm, roof deck 100 mm, portal-frame column grid at every "
     f"6 m grid point inside the L ({M['grid']['columns']} columns, 31 x 29 bays)",
     "- No process internals: the fitout programme stays the duty-sheet open "
     "item; the roof PV interface is the PV_ARRAY model's scope - nothing doubled",
     "- Route hold carried by name (building class); column/wall/roof sections "
     "are massing values - the structural design is the X-BLD lane's (holds, "
     "WORK_ORDER W12)"],
    "A-core")

# no nozzle schedule exists for this unit: replace the lib's schedule line with
# the no-schedule wording the FORGE precedent carries (no dangling CSV reference)
log = HERE / "build_log.md"
s = log.read_text()
s = s.replace(
    f"- Nozzles: all {R['nozzle_count_schedule']} rows of "
    f"`docs-authority/nozzles/{unit}.csv` present at face, height and bore "
    "(per-tag notes in check.nozzles_drawn)",
    "- Nozzles: none - the duty section 4 states None (electrical feed "
    "SF-EXT_HALL, air-source heat pumps D77, GEO_GHEX not coupled); no nozzle "
    "schedule is issued and no nozzle hardware is drawn (hold, WORK_ORDER W12)")
log.write_text(s)

"""GEO_HP_CLOSED_LOOP drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the
accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, skid01 (buffer vessel + headers +
tie stubs), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets                                       # noqa: E402

ns = runpy.run_path(HERE / "geo_hp_closed_loop.py")
parts, R = ns["parts"], ns["report"]
unit = "GEO_HP_CLOSED_LOOP"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


skid = union_all([parts["buffer_vessel"], parts["headers"], parts["tie_stubs"]])
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
M = R["machine"]
LP = M["loop"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm envelope - the node size_mm (the study '
      'registry box; the seed 800 x 800 x 800 "loop vessel beside GHEX" figure '
      'predates it - the node governs, hold W12)',
      'Closed source-loop distribution skid per the node design block: the loop '
      'between the GHEX bore field and the heat-pump evaporators (GEO_HP) - '
      'DN32 HDPE supply/return header runs, the loop buffer manifold vessel '
      '(OD 220 x 300, study, W12), the circulator envelope (125.7 W, node)',
      f'Loop: {LP["fluid"]}, design case {LP["design_case_kW_th"]:g} kW th at '
      f'{LP["flow_kg_s"]:g} kg/s, dT {LP["dT_K"]:g} K, head {LP["head_m"]:g} m '
      f'(node design); the S43 class edge runs at 0 kW idle standby',
      'Route hold carried by name: the node class is blank - no section 4 class '
      '(AFTERBURNER_FLUE/REE_RECOVER precedent)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Buffer vessel at x 200 on the skid centreline; header runs x 120..620 at '
      'z 320/380 +/- 70; circulator envelope x 640..880 (study stations, W12)',
      'AQS-DUTY-076 source-loop circulator: the 125.7 W node stamp (node '
      'continuous 0.1257 kW) - purchased per plan rule 6',
      'The buried ground array is the GHEX/site lane\'s - the tie stubs are '
      'interface indications, the below-grade runs are named, not drawn (hold, '
      'W12)'],
     "General arrangement, side elevation (end view). Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     ['3 schedule rows of docs-authority/nozzles/GEO_HP_CLOSED_LOOP.csv at tag, '
      'face and bore',
      'N3 geothermal loop fluid in on -Y at z 160 - the return from the GHEX '
      'bore field',
      'N1 drain flush at the envelope bottom (50 datum); N2 vent flush at the '
      'envelope top (800 datum = box top)',
      'Atmospheric hose barbs (rows read "Bore not calculated. Rating hose, '
      'atmospheric"); no flange (W4 110 % rule)'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("skid01", skid, (0, 1, 0),
     ['Loop buffer manifold vessel OD 220 x 300 (the seed\'s "loop vessel"; '
      'study - hold W12) with DN32 HDPE supply/return header runs',
      'Tie-in stubs at x 200/480: the below-grade interface to the GHEX bore '
      'field and the skid-side tie toward GEO_HP (interface indications, hold W12)',
      'HDPE DR-11 per the node material row; skid stations are study values'],
     "Fabricated part sheet: buffer vessel + headers + tie stubs."),
    ("iso01", full, (1, -1, 1),
     ['Plant orientation: loop return in on -Y from the GHEX bore field; the '
      'supply tie runs toward GEO_HP beside the vessel',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/geo_hp_closed_loop.step) is the solids of record',
      'Tracker --check green; acceptance A-core per AQS-PLAN-006 section 5 '
      '(route hold: the node class is blank)'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/geo_hp_closed_loop.py",
     f"models/mfg/{unit}/draw_geo_hp_closed_loop.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ["- Closed source-loop distribution skid per the node design block: DN32 "
     "HDPE supply/return header runs, the loop buffer manifold vessel (study, "
     "W12), the circulator envelope (AQS-DUTY-076, 125.7 W node stamp, "
     "purchased per plan rule 6), and the tie stubs (interface indications)",
     "- Route hold carried by name: the node class is blank - no section 4 "
     "class (AFTERBURNER_FLUE/REE_RECOVER precedent); the buried ground array "
     "is the GHEX/site lane's (hold, W12)",
     "- Hose-barb nozzles per the schedule (bores not calculated, hose, "
     "atmospheric); skid stations study values (holds, WORK_ORDER W12)"],
    "A-core")

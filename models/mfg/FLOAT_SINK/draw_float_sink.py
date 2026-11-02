"""FLOAT_SINK drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, sh01 (tank shell + rim), in01 (weir +
launder), aux01 (connection hardware), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets                                       # noqa: E402

ns = runpy.run_path(HERE / "float_sink.py")
parts, R = ns["parts"], ns["report"]
unit = "FLOAT_SINK"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


shell = union_all([parts["tank"], parts["rim_frame"]])
internals = union_all([parts["weir"], parts["launder"]])
aux = parts["nozzles"]
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
T = R["tank"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm overall - the study registry envelope '
      '(node size_mm), filled exactly',
      'Open-top CPVC tank: sink zone x 0..690, weir to z 700, float zone x 700..990 '
      'with the launder at the +X wall (lip overflow z 700, channel floor z 640)',
      f'Wall {T["wall_mm"]:g} mm (study - hold, W12); CA 0 mm (AQS-STD-001 polymer rule)',
      'Atmospheric float/sink separation, feed up to 85 C from LEACH_CSTR_1 (duty 1/3)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Weir laps 5 mm into the floor; launder floor laps 5 mm into the +X wall and the '
      'lip laps through the channel floor band (every union fused)',
      'Rim frame 20 mm bar closes the envelope at the top',
      'Welded plate construction, ISO 2768-m unless noted'],
     "General arrangement, side elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("nozzle_orient", full, (0, 0, -1),
     ['6 schedule rows of docs-authority/nozzles/FLOAT_SINK.csv at tag, face and bore',
      'N1 DN50 sink solids in on -Y at z 160; N2 DN50 liquor return, N3 DN25 float '
      'plastics, N6 DN15 solids (grit, bore not calculated) on +Y at z 600',
      'N4 drain boss in the sink zone floor (50 datum); N5 vent on the +Y rim bar '
      'flush at the 800 top',
      'Ports pack centred on the face mid-length per face/height group; the zoning '
      'against the weir is the fabricator s (hold, W12); per-tag positions in '
      'check.nozzles_drawn'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("sh01", shell, (0, 1, 0),
     [f'Tank shell: floor and walls {T["wall_mm"]:g} mm CPVC, open top, rim frame 20 mm',
      'CPVC per duty section 3 (AQS-STD-002 M1/M2/M5); no metal wetted part',
      'Welds per the unit WORK_ORDER route (F-VES): sheet cut, hot-gas / extrusion '
      'welds, set-in ports, leak test of the shell',
      f'Holdup at the 720 mm working level net of internals: {R["holdup_m3"]:g} m3 '
      '(A-VES; no residence claimed - the duty claims no holdup)'],
     "Fabricated part sheet: tank shell + rim frame."),
    ("in01", internals, (0, 1, 0),
     ['Weir plate x 690..700 to z 700: sink solids settle in the x 0..690 zone, float '
      'plastics spill the weir into the launder',
      'Launder: lip plate x 920..930 (overflow z 700) over a channel floor at z 640 '
      'running to the +X wall',
      'Layout solids from the duty section 1 separation duty; the node internals row '
      'is none, so the tracker records no internal solid (hold, W12)'],
     "Fabricated part sheet: weir + float launder."),
    ("aux01", aux, (0, 1, 0),
     ['Connection hardware DN15/DN25/DN50 as atmospheric hose barbs (lib/nozzles.py); '
      'barb profile a study proportion, finished against the hose supplier print',
      'Schedule rating column (Class 150) carried verbatim as text - duty section 4 '
      'says atmospheric tube or hose, no flange class (W4 110 % rule)',
      'N6 solids row drawn at DN15 and labeled bore not calculated (AQS-PLAN-006 W4)'],
     "Fabricated part sheet: connection hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: sink solids in on -Y, liquor / plastics / grit out on +Y; '
      'weir and launder at the +X end',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/float_sink.step) is the solids of record',
      'Build fills the study registry envelope exactly; tracker --check green'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/float_sink.py", f"models/mfg/{unit}/draw_float_sink.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    [f"- A-VES: liquor holdup {R['holdup_m3']} m3 at the 720 mm working level net of "
     "the weir and launder, reported from the model; the duty claims no holdup, so no "
     "residence time is derived",
     "- Internals: weir + float launder drawn as layout solids from the duty section 1 "
     "separation duty; the node internals row is none (tracker hold, W12)"],
    "A-core + A-VES")

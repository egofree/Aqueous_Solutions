"""ROOF_TANK drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, sh01 (shell + heads + plinth),
in01 (dip pipe + stilling well + PVDF coil), aux01 (connection hardware), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets                                       # noqa: E402

ns = runpy.run_path(HERE / "roof_tank.py")
parts, R = ns["parts"], ns["report"]
unit = "ROOF_TANK"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


shell = union_all([parts["plinth"], parts["tank"], parts["rim_frame"]])
internals = union_all([parts["stilling_well"], parts["dip_pipe"], parts["coil"]])
aux = parts["nozzles"]
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
T = R["tank"]
I = T["internals"]
C = I["coil"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm overall - the node registry envelope, filled '
      'exactly (the duty sheet carries no size line; W12)',
      'Rectangular welded-plate PVC-U tank (HOPPER/FLOAT_SINK idiom): floor and '
      'walls 10 mm (study fab page - hold, W12), 20 mm rim frame closes the top',
      'Internals: dip pipe inside the stilling well (fab study page) plus the PVDF '
      'air coil of duty section 3 (sheet IN01)',
      'Roof water tank, atmospheric; the hot draw is cooled at the coil line '
      '(duty sections 2, 3 and 6)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['26 schedule rows drawn at tag, face, height and bore; the two 160/600 rows '
      'pack the full face chord, outer barbs near-tangent to the shell (hold, W12)',
      'N9 drain boss tip at the 50 datum; N10 vent flush at the top head (the 800 '
      'datum predates the box, W12)',
      'PVDF coil, 4 turns at a 300 mm mean diameter, z 80..320 (study dims, W12)'],
     "General arrangement, side elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("nozzle_orient", full, (0, 0, -1),
     ['26 schedule rows of docs-authority/nozzles/ROOF_TANK.csv at tag, face and bore',
      'N18 is a solids row drawn at DN15 and labeled bore not calculated',
      'Ports pack centred on the face mid-length per face/height group; per-tag '
      'positions in check.nozzles_drawn',
      'Atmospheric hose barbs; the schedule rating column (Class 150) carried '
      'verbatim as text - no flange drawn (duty section 4)'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("sh01", shell, (0, 1, 0),
     ['Plate walls and floor 10 mm PVC-U inside the 649 x 520 envelope, open top '
      'closed by the 20 mm rim frame, on the plinth',
      'CA does not apply to the polymer (AQS-STD-001); wall a study value (hold, W12)',
      'Welds per the unit WORK_ORDER route (F-VES): sheet/pipe cut, thermoplastic '
      'weld, set-in ports, leak test'],
     "Fabricated part sheet: tank body + rim frame + plinth."),
    ("in01", internals, (0, 1, 0),
     ['Stilling well OD 110 x wall 5, laps floor and rim; dip pipe OD 60 x wall 4 '
      'inside it, hung from the rim bars (fab study page; dims study, W12)',
      f'PVDF air coil: tube OD {C["tube_od_mm"]:g}, 4 turns at a 300 mm mean '
      f'diameter, {C["area_drawn_m2"]} m2 DRAWN (duty section 3)',
      'A-HX-style report: no authority sizes the coil and AQS-STD-002 section 10 '
      'Rev J records the trim superseded - the conflict is a named hold (W12)'],
     "Fabricated part sheet: dip pipe + stilling well + coil."),
    ("aux01", aux, (0, 1, 0),
     ['Connection hardware DN15/DN25/DN50 as atmospheric hose barbs '
      '(lib/nozzles.py); barb profile a study proportion, finished against the '
      'hose supplier print',
      'Solids row N18 at DN15, bore not calculated (plan W4 rule)',
      'Schedule rating column (Class 150) carried verbatim as text - duty section 4 '
      '(atmospheric tube or hose; W4 110 percent rule: no process pressure)'],
     "Fabricated part sheet: connection hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: water services on the -Y/+Y faces at z 160/600, drain at '
      'the base head, vent on the top head',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/roof_tank.step) is the solids of record',
      f'Build fills the node registry envelope exactly; holdup {R["holdup_m3"]} m3 '
      'reported, no residence derived (A-VES)'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/roof_tank.py", f"models/mfg/{unit}/draw_roof_tank.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    [f"- A-VES: the {R['holdup_m3']} m3 liquor volume is reported - the duty "
     "section 2 two-minute figure is not a designed volume and no residence time "
     "is derived",
     "- Coil area reported as DRAWN: no authority sizes it and the AQS-STD-002 "
     "section 10 Rev J supersession is a named conflict hold (W12)",
     "- Internals: dip pipe + stilling well per fab/ROOF_TANK.md (AQS-MFG-001); "
     "dimensions study values (W12)"],
    "A-core + A-VES")

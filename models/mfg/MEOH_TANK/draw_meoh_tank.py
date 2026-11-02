"""MEOH_TANK drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, sh01 (shell + heads + plinth),
in01 (dip pipe + stilling well), aux01 (connection hardware), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets                                       # noqa: E402

ns = runpy.run_path(HERE / "meoh_tank.py")
parts, R = ns["parts"], ns["report"]
unit = "MEOH_TANK"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


shell = union_all([parts["plinth"], parts["shell"]])
internals = union_all([parts["stilling_well"], parts["dip_pipe"]])
aux = parts["nozzles"]
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
T = R["tank"]
I = T["internals"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm overall - the node envelope (AQS-DUTY-064 '
      'box), filled exactly; the duty sheet shell line 800 x 800 x 1100 is a hold '
      '(W12)',
      f'Vertical welded 304L tank: shell OD 540, wall {T["wall_mm"]:g} mm (node '
      'design_storage booking), on a plinth with heads',
      'Internals per the AQS-MFG-001 study page: dip pipe down to z 100 inside the '
      'stilling well (sheet IN01)',
      'Methanol product storage, atmospheric (duty sections 2, 4 and 6)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['13 schedule rows drawn at tag, face, height and bore: 4 feeds in on -Y at '
      'z 160, 7 draws out on +Y at z 600; per-tag positions in check.nozzles_drawn',
      'N9 drain boss tip at the 50 datum; N10 vent flush at the top head (the 800 '
      'datum predates the box, W12)',
      'The fab study page 6 mm wall predates the node design_storage booking of '
      '3.0 mm - the node governs (W12)'],
     "General arrangement, side elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("nozzle_orient", full, (0, 0, -1),
     ['13 schedule rows of docs-authority/nozzles/MEOH_TANK.csv at tag, face and '
      'bore',
      'N1..N4 feeds in on -Y at z 160 (crude MeOH, biogenic MeOH, methane, '
      'compost condensate)',
      'N5..N8 and N11..N13 draws out on +Y at z 600 (fuel, tank draw, '
      'formaldehyde, methylamine, product, VDF and TFE carbon sources)',
      'Atmospheric hose barbs; the schedule rating column (Class 150) carried '
      'verbatim as text - no flange drawn (duty section 4)'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("sh01", shell, (0, 1, 0),
     [f'Shell OD 540 x wall {T["wall_mm"]:g} SA-240 304L, z 40..560, heads, plinth; '
      'welded construction',
      'CA 0 mm on the 304L (AQS-STD-001); wall the node design_storage booking '
      '(AQS-DUTY-064)',
      'Welds per the unit WORK_ORDER route (F-VES): plate cut, gas-tungsten-arc weld, set-in '
      'ports, hydro or leak test'],
     "Fabricated part sheet: shell + heads + plinth."),
    ("in01", internals, (0, 1, 0),
     [f'Stilling well OD {I["stilling_well"]["od_mm"]:g} x wall '
      f'{I["stilling_well"]["wall_mm"]:g}, z {I["stilling_well"]["z_mm"][0]:g}..'
      f'{I["stilling_well"]["z_mm"][1]:g}; laps floor and top head',
      f'Dip pipe OD {I["dip_pipe"]["od_mm"]:g} x wall {I["dip_pipe"]["wall_mm"]:g} '
      f'inside the well, z {I["dip_pipe"]["z_mm"][0]:g}..{I["dip_pipe"]["z_mm"][1]:g}',
      'Internals named by fab/MEOH_TANK.md (AQS-MFG-001); dimensions study values '
      '(hold, W12); node internals row none'],
     "Fabricated part sheet: dip pipe + stilling well."),
    ("aux01", aux, (0, 1, 0),
     ['Connection hardware DN15 as atmospheric hose barbs (lib/nozzles.py); barb '
      'profile a study proportion, finished against the hose supplier print',
      'Schedule rating column (Class 150) carried verbatim as text - duty section 4 '
      '(atmospheric hose; W4 110 percent rule: no process pressure)',
      '304L hardware per duty section 3; A4-70 fasteners by the plan grade rule'],
     "Fabricated part sheet: connection hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: feeds in on -Y at z 160, draws out on +Y at z 600, drain '
      'at the base head, vent on the top head',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/meoh_tank.step) is the solids of record',
      f'Build fills the node envelope exactly; holdup {R["holdup_m3"]} m3 reported, '
      'the duty working volume (0.0421 m3, 7 days) stays the booked basis (A-VES)'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/meoh_tank.py", f"models/mfg/{unit}/draw_meoh_tank.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    [f"- A-VES: the {R['holdup_m3']} m3 liquor volume is reported - the duty "
     "working volume (0.0421 m3, 7 days) stays the booked basis and no residence "
     "time is derived",
     "- Duty sheet shell line 800 x 800 x 1100 vs node AQS-DUTY-064 box: the node "
     "governs, the sheet line is a named hold (W12)"],
    "A-core + A-VES")

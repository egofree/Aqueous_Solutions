"""WS_KOH drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, tank01 (day tank + tray)aux01
(guard + purchased envelopes + connection hardware), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets                                       # noqa: E402

ns = runpy.run_path(HERE / "ws_koh.py")
parts, R = ns["parts"], ns["report"]
noz_pieces = ns["noz_pieces"]
unit = "WS_KOH"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


tank = union_all([parts["tray"], parts["tank"]])
aux = union_all([parts["guard_rail"]])
nozh = cq.Workplane(obj=cq.Compound.makeCompound([p.val() for p in noz_pieces]))
body = union_all([parts["tray"], parts["tank"], parts["guard_rail"]])
for piece in noz_pieces:                                     # piecewise, as the builder exports
    body = body.union(piece)
full = body

L, W, H = [float(v) for v in R["size_mm"]]
T = R["tank"]
M = R["a_mach"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm overall - the node storage-sizing envelope, '
      'filled exactly (the duty section 4 prose seed line 800 x 800 x 1100 is an '
      'older figure, W12)',
      'KOH make-up day-station: day tank at the back, service-zone guard rail front-right',
      'The BMED NaOH product to KOH; duty section 2: no holdup claimed (0.27 kg/d in and out)',
      'PVC-U wetted per duty section 3 rules M1 and M2'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     [f'Day tank OD {T["od_mm"]:g} x wall {T["wall_mm"]:g} (study fab page - hold, '
      'W12), base head lapping the tray, top head and vent riser within the box',
      'No purchased item is named on the node or duty sheet - none drawn (the criterion has nothing to match, W12)',
      'No internals: the node row is none and no study page issues internals for this station (W12)'],
     "General arrangement, side elevation. Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     [f'{R["nozzle_count_schedule"]} schedule rows of docs-authority/nozzles/WS_KOH.csv '
      'at tag, face and bore',
      'N1 NaOH product in on -Y at z 160; N2 KOH out on +Y (schedule datum 600 clamped down: the 350 box predates it, W12)',
      'N-drain passes through the tray floor; the vent riser stands on the tank '
      'head to the envelope top (its 800 datum predates the box, W12)',
      'Atmospheric hose makeup by the connecting line at the face; the schedule '
      'rating column (Class 150) carried verbatim as text - no flange drawn '
      '(duty section 4)'],
     "Connection orientation, top view. Tags/faces/bore per the schedule."),
    ("tank01", tank, (0, 1, 0),
     [f'Day tank OD {T["od_mm"]:g} x wall {T["wall_mm"]:g}, z {T["z_mm"][0]:g}..'
      f'{T["z_mm"][1]:g}, heads, on the bund tray',
     'Station day-tank envelope: no holdup claimed on the node or duty (duty section 8) - no volume claimed (W12)',
      'Welds per the unit WORK_ORDER route (F-MACH): sheet/pipe cut, thermoplastic '
      'weld, set-in ports, leak test'],
     "Fabricated part sheet: day tank + bund tray."),
    ("aux01", aux, (1, -0.5, 0.7),
     ['Guard rail over the front-right floor zone (A-MACH: guard drawn); anchors '
      'in fasteners.csv',
      'No purchased items named for this station - none drawn (W12)',
      'Connection hardware DN15/DN25 as open-bore tube (lib/dn Sch 40 table), '
      'flush at the envelope faces; atmospheric per duty section 4'],
     "Fabricated part sheet: guard, purchased envelopes, connection hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: NaOH product in on -Y, KOH out on +Y, drain at the tray, vent riser on the tank head',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/' + 'ws_koh' + '.step) is the solids of record',
      f'Build fills the node storage-sizing envelope exactly; the tank volume is reported for the record only (no holdup basis)'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/ws_koh.py", f"models/mfg/{unit}/draw_ws_koh.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ['- A-MACH: guard rail and slab anchors drawn; no purchased item named on the node or duty - none drawn (W12)',
    '- Tank: station day-tank envelope, no volume claimed (duty section 8: no holdup basis; W12)',
    '- Schedule datums clamped into the 350 mm box (holds, W12)'],
    "A-core + A-MACH")

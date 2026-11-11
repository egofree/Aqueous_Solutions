"""WS_NITRIC drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

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
from lib import sheets, step_export  # noqa: E402

ns = runpy.run_path(HERE / "ws_nitric.py")
parts, R = ns["parts"], ns["report"]
noz_pieces = ns["noz_pieces"]
unit = "WS_NITRIC"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


tank = union_all([parts["tray"], parts["tank"]])
aux = union_all([parts["guard_rail"], parts["pump"]])
nozh = cq.Workplane(obj=cq.Compound.makeCompound([p.val() for p in noz_pieces]))
body = union_all([parts["tray"], parts["tank"], parts["guard_rail"], parts["pump"]])
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
      'Nitric acid day-station: 25 L day tank at the back, PVDF pump envelope in the guarded floor zone',
      '2 M HNO3 at no more than 40 C; storage per X-SAF-09 (14 d at 1.17 L/d = 16.4 L net, tank 25 L nominal, own bund 30 L); AQS-DSN-OX-001 section 1',
      'PVC-U tank and piping, PVDF pumps and valves, FKM or PTFE gaskets; 304L excluded (M3) - duty section 3'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     [f'Day tank OD {T["od_mm"]:g} x wall {T["wall_mm"]:g} (study fab page - hold, '
      'W12), base head lapping the tray, top head and vent riser within the box',
      'Working levels: 25 L nominal and 16.4 L net reported from the model at the X-SAF-09 basis; the 30 L own bund is the room-side containment the station seats in (W12)',
      'Instruments (level high-high trip, temperature 40 C trip, density alarm, bund sump pH) are loop hardware, not modeled (duty section 5)'],
     "General arrangement, side elevation. Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     [f'{R["nozzle_count_schedule"]} schedule rows of docs-authority/nozzles/WS_NITRIC.csv '
      'at tag, face and bore',
      'N1/N2 in on -Y at z 160; N3/N4/N7 out on +Y and the N6 DN25 vent-to-NOX_SCRUB row drawn at the +Y band bound (no datum on the row - layout choice, W12)',
      'N-drain passes through the tray floor; the vent riser stands on the tank '
      'head to the envelope top (its 800 datum predates the box, W12)',
      'Atmospheric hose makeup by the connecting line at the face; the schedule '
      'rating column (Class 150) carried verbatim as text - no flange drawn '
      '(duty section 4)'],
     "Connection orientation, top view. Tags/faces/bore per the schedule."),
    ("tank01", tank, (0, 1, 0),
     [f'Day tank OD {T["od_mm"]:g} x wall {T["wall_mm"]:g}, z {T["z_mm"][0]:g}..'
      f'{T["z_mm"][1]:g}, heads, on the bund tray',
     'Volume per the duty section 2 X-SAF-09 basis; the vent goes on IA-NIT-VENT to NOX_SCRUB and overflow goes to the oxidizing-acid bund (duty section 6)',
      'Welds per the unit WORK_ORDER route (F-MACH): sheet/pipe cut, thermoplastic '
      'weld, set-in ports, leak test'],
     "Fabricated part sheet: day tank + bund tray."),
    ("aux01", aux, (1, -0.5, 0.7),
     ['Guard rail over the front-right floor zone (A-MACH: guard drawn); anchors '
      'in fasteners.csv',
      'PVDF pump envelope (duty section 3), drawn as its envelope and interface per plan rule 6; drive rating per the maker TDS at order (W12)',
      'Connection hardware DN15/DN25 as open-bore tube (lib/dn Sch 40 table), '
      'flush at the envelope faces; atmospheric per duty section 4'],
     "Fabricated part sheet: guard, purchased envelopes, connection hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: acid in on -Y, HNO3 and the scrubber vent out on +Y, drain at the tray, vent riser on the tank head',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/' + 'ws_nitric' + '.step) is the solids of record',
      f'Build fills the node storage-sizing envelope exactly; the 25 L nominal and 16.4 L net levels are reported at the X-SAF-09 basis'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/ws_nitric.py", f"models/mfg/{unit}/draw_ws_nitric.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ['- A-MACH: guard rail and slab anchors drawn; PVDF pump named from duty section 3 and drawn as its envelope (plan rule 6); drive rating per the maker TDS at order (W12)',
    '- Tank: 25 L nominal, 16.4 L net at the duty section 2 X-SAF-09 basis, levels reported; the 30 L own bund is the room-side containment (W12)',
    '- Schedule datums clamped into the 350 mm box; the N6 vent-to-scrubber row carries no datum and draws at the +Y band bound (holds, W12)'],
    "A-core + A-MACH")

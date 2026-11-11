"""WS_SLURRY drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, tank01 (day tank + tray), aux01
(guard + purchased envelopes + connection hardware), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets, step_export  # noqa: E402

ns = runpy.run_path(HERE / "ws_slurry.py")
parts, R = ns["parts"], ns["report"]
noz_pieces = ns["noz_pieces"]
unit = "WS_SLURRY"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else s.union(s)
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
      'Slurry day-station: day tank at the back, service-zone guard rail front-right',
      'Silicate to slurry in; colloidal silica slurry out to S37 (duty section 1)',
      'PE wetted per duty section 3 (graph node material row); CA 0 mm on the polymer (AQS-STD-001)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     [f'Day tank OD {T["od_mm"]:g} x wall {T["wall_mm"]:g} per node design_storage '
      '(AQS-DUTY-064), base head lapping the tray, top head at the box top',
      'Nominal volume 0.02 m3 at the 30-day hold basis reported for the record; '
      'duty section 2 claims no holdup and no residence time is derived (W12)',
      'No purchased item is named on the node or duty sheet - none drawn (the criterion has nothing to match, W12)'],
     "General arrangement, side elevation. Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     [f'{R["nozzle_count_schedule"]} schedule rows of docs-authority/nozzles/WS_SLURRY.csv '
      'at tag, face and bore',
      'N1 silicate to slurry in on -Y at z 160; N2 colloidal silica slurry out on '
      '+Y (schedule datum 600 clamped down: the 350 box predates it, W12)',
      'N-drain passes through the tray floor; the vent riser stands beside the tank '
      'to the envelope top (its 800 datum predates the box, W12)',
      'Atmospheric hose makeup by the connecting line at the face; the schedule '
      'rating column (Class 150) carried verbatim as text - no flange drawn'],
     "Connection orientation, top view. Tags/faces/bore per the schedule."),
    ("tank01", tank, (0, 1, 0),
     [f'Day tank OD {T["od_mm"]:g} x wall {T["wall_mm"]:g}, z {T["z_mm"][0]:g}..'
      f'{T["z_mm"][1]:g}, heads, on the bund tray; figures per node design_storage (AQS-DUTY-064)',
      'Nominal volume per design_storage V_nom_m3 at the 30-day hold basis; reported, no residence claim (W12)',
      'Welds per the unit WORK_ORDER route (F-MACH): sheet cut, thermoplastic '
      'weld, set-in ports, leak test'],
     "Fabricated part sheet: day tank + bund tray."),
    ("aux01", aux, (1, -0.5, 0.7),
     ['Guard rail over the front-right floor zone (A-MACH: guard drawn); anchors '
      'in fasteners.csv',
      'No purchased items named for this station - none drawn (W12)',
      'Connection hardware DN15 as open-bore tube (lib/dn Sch 40 table), '
      'flush at the envelope faces; atmospheric per duty section 4'],
     "Fabricated part sheet: guard, purchased envelopes, connection hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: silicate to slurry in on -Y, the colloidal silica slurry '
      'out on +Y, drain at the tray, vent riser beside the tank',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/' + 'ws_dope' + '.step) is the solids of record',
      f'Build fills the node storage-sizing envelope exactly; the nominal-volume level is reported at the design_storage basis'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/ws_slurry.py", f"models/mfg/{unit}/draw_ws_slurry.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ['- A-MACH: guard rail and slab anchors drawn; no purchased item named on the node or duty - none drawn (W12)',
     '- Tank: node design_storage D 300 x H 300, wall 4.75 (AQS-DUTY-064); the 0.02 m3 nominal volume is reported for the record, no residence claim (W12)',
     '- Schedule datums clamped into the 350 mm box (holds, W12)'],
    "A-core + A-MACH")

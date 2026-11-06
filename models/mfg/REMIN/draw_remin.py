"""REMIN drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, sh01 (day tank), skid01 (purchased
envelopes), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets                                       # noqa: E402

ns = runpy.run_path(HERE / "remin.py")
parts, R = ns["parts"], ns["report"]
noz_pieces = ns["noz_pieces"]
unit = "REMIN"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


tank = union_all([parts["tray"], parts["tank"]])
skid = union_all([parts["metering_pumps"], parts["uv_unit"]])
aux = cq.Workplane(obj=cq.Compound.makeCompound([p.val() for p in noz_pieces]))
body = union_all([parts["tray"], parts["tank"], parts["metering_pumps"], parts["uv_unit"]])
for piece in noz_pieces:                                     # piecewise, as the builder exports
    body = body.union(piece)
full = body

L, W, H = [float(v) for v in R["size_mm"]]
T = R["tank"]
PU = R["purchased"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm overall - the node storage-sizing envelope, '
      'filled exactly (the duty section 2 shell line 600 x 400 x 800 is an older '
      'figure, W12)',
      'Remineralization dosing skid: PVC-U day tank OD 460 at the back, the two '
      'metering-pump envelopes front-right and the UV lantern front-left (sheet '
      'SKID01)',
      'Atmospheric tube connections on tray risers, flush at the envelope faces '
      '(sheet AUX01)',
      'Working level set by the duty section 2 holdup basis (7 days at the 10 L/d '
      'potable tap = 0.07 m3); atmospheric, duty sections 2, 4 and 6'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     [f'Tank shell OD 460 x wall {T["wall_mm"]:g} (study fab page - hold, W12), '
      'base head lapping the tray, top head closing at z 580..600 within the box',
      'The node design block names the purchased items: 2 x metering diaphragm '
      '(Ca slurry, MgCl2) and the UV unit after the dose (potable integrity) - '
      'drawn as their envelope and interface per plan rule 6',
      'PVC-U drawn per duty section 3 rule M1; the HDPE alternative is a named '
      'hold (W12)'],
     "General arrangement, side elevation. Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     [f'{R["nozzle_count_schedule"]} schedule rows of docs-authority/nozzles/REMIN.csv at tag, face and bore',
      'N1 UPW in on -Y at z 160 (tray riser); N2 potable and N5 remineralised '
      'makeup out on +Y (schedule datums 600 clamped down so the branch and riser '
      'stay inside the box, W12)',
      'N3 drain through the tray floor (50 datum); N4 vent flush at the tank top '
      'head (its 800 datum predates the box, W12)',
      'Atmospheric hose makeup by the connecting line at the face; the schedule '
      'rating column (Class 150) carried verbatim as text - no flange drawn',
      'N6 cable power terminal: carried verbatim, not drawn'],
     "Connection orientation, top view. Tags/faces/bore per the schedule."),
    ("sh01", tank, (0, 1, 0),
     [f'Day tank OD 460 x wall {T["wall_mm"]:g} PVC-U, z 40..580, heads, on the '
      'skid tray',
      'CA does not apply to the polymer (AQS-STD-001); wall a study value (hold, W12)',
      'Welds per the unit WORK_ORDER route (F-VES): sheet/pipe cut, thermoplastic '
      'weld, set-in ports, leak test'],
     "Fabricated part sheet: day tank + tray."),
    ("skid01", skid, (1, -0.4, 0.6),
     ['Purchased envelopes per plan rule 6: two metering diaphragm pumps '
      '(110 x 90 x 130 each, front-right) and the UV lantern (OD 90 x 220 long, '
      'front-left)',
      'The node design block names them; the UV unit sits after the dose on the '
      'potable line (potable integrity)',
      'Internals of the purchased units stay with the maker - envelope and '
      'interface only (W12); hold-down bolts in fasteners.csv'],
     "Fabricated part sheet: purchased equipment envelopes."),
    ("aux01", aux, (0, 1, 0),
     ['Connection hardware DN15 as open-bore tube (lib/dn Sch 40 table), flush at '
      'the envelope faces; atmospheric per duty section 4',
      'Side connections ride tray risers; hose makeup by the connecting line at '
      'the face; the W4 110 percent rule draws no flange (no process pressure)',
      'N3 drain passes through the tray floor; N4 vent stands on the tank top head'],
     "Fabricated part sheet: connection hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: UPW in on -Y, potable out on +Y through the UV position, '
      'drain at the tray floor, vent on the tank top head',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/remin.step) is the solids of record',
      f'Build fills the node storage-sizing envelope exactly; holdup {R["holdup_m3"]} '
      'm3 reported at the duty-basis level (A-VES)'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/remin.py", f"models/mfg/{unit}/draw_remin.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    [f"- A-VES: the {R['holdup_m3']} m3 working volume at the duty-basis level is "
     "reported - the duty section 2 carries the holdup basis (7 days at the 10 L/d "
     "potable tap); no new residence-time claim",
     "- Purchased items per plan rule 6: 2 x metering diaphragm pumps (Ca slurry, "
     "MgCl2) and the UV unit after the dose, named from the node design block and "
     "drawn as their envelope and interface only; wetted parts and drive ratings "
     "per the maker TDS at order (W12)",
     "- Material conditional: PVC-U drawn per duty section 3 rule M1; the HDPE "
     "alternative is a named hold (W12)"],
    "A-core + A-VES")

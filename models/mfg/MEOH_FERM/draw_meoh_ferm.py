"""MEOH_FERM drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, vessel01 (vessel + stand), aux01
(insulation, pump envelope, loop), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets, step_export  # noqa: E402

ns = runpy.run_path(HERE / "meoh_ferm.py")
parts, R = ns["parts"], ns["report"]
noz_pieces = ns["noz_pieces"]
unit = "MEOH_FERM"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else s.union(s)
    return u


vessel = union_all([parts["plinth"], parts["legs"], parts["support_ring"],
                    parts["shell"]])
aux = union_all([parts["insulation"], parts["heater_pad"], parts["recirc_pump"],
                 parts["recirc_loop"]])
body = union_all([vessel, aux])
for piece in noz_pieces:
    body = body.union(piece)
full = body

L, W, H = [float(v) for v in R["size_mm"]]
V = R["vessel"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm overall - the node envelope (X-MFG-31 '
      'reactor_design), filled by the vent riser top (the duty section 2 prose '
      'line "Envelope 2200 x 900 x 1400" predates the node box, W12)',
      f'Fermenter vessel OD {V["od_mm"]:g} x wall 4.0 x 100 shell (node design), '
      '50 mm PIR envelope, on the stand over the plinth',
      'PVC-U wetted per duty section 3 (rules M1 and M2); the node HDPE row is '
      'superseded for the wetted parts (W12)',
      'Pump envelope (daily recirculation, node mixer row) and 0.74 W heater mat '
      'envelope (purchased, plan rule 6)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     [f'Working level: the 48 h basis V = 0.0007 m3 (duty section 2) sets the '
      f'level at z {V["working_level_mm"]:g}, reported from the model (A-VES); '
      'no new residence-time claim',
      'Agitation is by the recirculation loop (the node mixer row): pump to the '
      'top head, return from the base; no top-entry agitator named on the node - '
      'none drawn (W12)',
      'T 35 C per the node design sits inside the PVC-U class; above 60 C the '
      'thermoplastic is CPVC (duty section 3)'],
     "General arrangement, side elevation. Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     [f'{R["nozzle_count_schedule"]} schedule rows of docs-authority/nozzles/'
      'MEOH_FERM.csv at tag, face and bore',
      'N1 ferment feed in on -Y at z 160; N2 biogenic MeOH and N3 fermenter '
      'residue out on +Y (600 datums clamped to 570.7, the od + 8 rule - W12)',
      'N6 fermenter digestate carries the line-list classification solids '
      '(non-piped transfer): drawn DN15, bore not calculated (plan W4)',
      'N4 drain boss under the base (flush at the envelope bottom, 50 datum); N5 '
      'vent riser on the top head, flush at the envelope top (800 datum, W12); '
      'face hardware per the CATCH_TANK idiom'],
     "Connection orientation, top view. Tags/faces/bore per the schedule."),
    ("vessel01", vessel, (0, 1, 0),
     [f'Shell OD {V["od_mm"]:g} x wall 4.0, z 230..330, heads, on the support ring '
      'and 4 legs over the plinth - the node design figures (X-MFG-31)',
      'PVC-U per duty section 3; CA 0 mm on the polymer (AQS-STD-001); thermoplastic '
      'welds per the route (F-VES), leak test by fill',
      'The 48 h working volume is the duty section 2 basis; the level is reported, '
      'not re-derived'],
     "Fabricated part sheet: vessel + stand."),
    ("aux01", aux, (1, -0.5, 0.7),
     ['PIR insulation envelope OD 225 x 50 class with top cap (node material row); '
      'the loop penetrations pass through it',
      'Daily recirculation pump envelope (node mixer row) and 0.74 W heater mat '
      'envelope - purchased, plan rule 6; ratings read the maker sheets at order',
      'Recirculation loop DN15 PVC-U: pump to top head (inject), base tap to pump '
      '(return); the node agitation basis'],
     "Fabricated part sheet: insulation, pump envelope, recirculation loop."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: ferment feed in on -Y, biogenic MeOH and residue out on '
      '+Y, digestate solids port, drain at the base, vent at the box top',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/' + 'meoh_ferm' + '.step) is the solids of record',
      'The skid chain fuses to one solid; the face stubs stay separate until the '
      'connecting lines make their joints (check.solids_note)'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/meoh_ferm.py", f"models/mfg/{unit}/draw_meoh_ferm.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ['- A-VES: the 48 h working volume V = 0.0007 m3 (duty section 2) is an '
     'existing holdup basis - the model level (z 305.1) is set by it and reported; '
     'no new residence-time claim',
     '- Agitation per the node mixer row: daily recirculation pump (envelope, plan '
     'rule 6) with a DN15 loop; no top-entry agitator named - none drawn (W12)',
     '- PVC-U wetted per duty section 3; the node HDPE row superseded for the '
     'wetted parts (holds, W12); the 600 datums clamped to 570.7',
     '- The skid chain fuses to one solid; the face stubs stay separate until the '
     'connecting lines make their joints (check.solids_note)'],
    "A-core + A-VES")

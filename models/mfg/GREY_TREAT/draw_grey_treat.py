"""GREY_TREAT drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, sh01 (shell + heads + plinth),
aux01 (connection hardware), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets                                       # noqa: E402

ns = runpy.run_path(HERE / "grey_treat.py")
parts, R = ns["parts"], ns["report"]
noz_pieces = ns["noz_pieces"]
unit = "GREY_TREAT"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


shell = union_all([parts["plinth"], parts["shell"]])
aux = cq.Workplane(obj=cq.Compound.makeCompound([p.val() for p in noz_pieces]))
body = shell
for piece in noz_pieces:                                     # piecewise, as the builder exports
    body = body.union(piece)
full = body

L, W, H = [float(v) for v in R["size_mm"]]
T = R["tank"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm overall - the node registry envelope, filled '
      'exactly (the duty sheet seed line 800 x 800 x 1100 is an older figure, W12)',
      'Greywater treatment vessel: vertical PVC-U tank, shell OD 460, wall '
      f'{T["wall_mm"]:g} mm (study fab page - hold, W12), on a plinth with heads',
      'No internals drawn: the node internals row is none and no study page issues '
      'internals for this unit (W12)',
      'Greywater treatment, atmospheric (duty sections 2, 4 and 6)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Shell base head laps the plinth; top head closes at z 708..728 within the box',
      'Ports on the -Y face sit at z 160; the +Y outlets at z 600; drain boss tip '
      'at the 50 datum, vent flush at the top head (the 800 datum predates the '
      'box, W12)',
      'PVC-U per duty section 3 rules M1 and M2; CA does not apply to the polymer'],
     "General arrangement, side elevation. Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     ['11 schedule rows of docs-authority/nozzles/GREY_TREAT.csv at tag, face and '
      'bore',
      'N1 DN50 grey/solids in and N2/N8/N9/N10/N11 DN15 bleed and wash-water inlets '
      '(face -Y, z 160); N3 DN25 treated grey, N4 DN50 grey sludge and N7 DN15 '
      'water-cycle return out (+Y, z 600)',
      'N5 drain boss on the base head (50 datum); N6 vent flush at the top head',
      'Atmospheric hose barbs; the schedule rating column (Class 150) carried '
      'verbatim as text - no flange drawn (duty section 4)'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("sh01", shell, (0, 1, 0),
     [f'Shell OD 460 x wall {T["wall_mm"]:g} PVC-U, z 40..708, heads, plinth',
      'CA does not apply to the polymer (AQS-STD-001); wall a study value (hold, W12)',
      'Welds per the unit WORK_ORDER route (F-VES): sheet/pipe cut, thermoplastic '
      'weld, set-in ports, leak test'],
     "Fabricated part sheet: shell + heads + plinth."),
    ("aux01", aux, (0, 1, 0),
     ['Connection hardware DN15/DN25/DN50 as atmospheric hose barbs '
      '(lib/nozzles.py); barb profile a study proportion, finished against the '
      'hose supplier print',
      'Schedule rating column (Class 150) carried verbatim as text - duty section 4 '
      '(atmospheric hose; W4 110 percent rule: no process pressure)',
      'The issued schedule (11 rows) governs; the duty section 4 prose table '
      '(7 rows on the seed block) predates it (hold, W12)'],
     "Fabricated part sheet: connection hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: the grey and wash-water inlets on -Y, the treated outlets '
      'on +Y, drain at the base head, vent on the top head',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/grey_treat.step) is the solids of record',
      f'Build fills the node registry envelope exactly; holdup {R["holdup_m3"]} m3 '
      'reported, no residence derived - the duty claims no holdup (A-VES)'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/grey_treat.py", f"models/mfg/{unit}/draw_grey_treat.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    [f"- A-VES: the {R['holdup_m3']} m3 liquor volume at the study working level is "
     "reported - the duty section 2 claims no holdup and no residence time is "
     "derived",
     "- Internals: none drawn - the node internals row is none and no study page "
     "issues internals for this unit (W12)",
     "- The duty section 4 prose block (7 rows on the seed line 800 x 800 x 1100) "
     "predates the issued 11-row schedule and the node box; the node and the "
     "schedule govern (W12)"],
    "A-core + A-VES")

"""POLISH_BANK drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

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
from lib import sheets, step_export  # noqa: E402

ns = runpy.run_path(HERE / "polish_bank.py")
parts, R = ns["parts"], ns["report"]
noz_pieces = ns["noz_pieces"]
unit = "POLISH_BANK"


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
I = T["internals"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm overall - the node registry envelope, filled '
      'exactly',
      'Polish bank on the EW tail line: vertical PVC-U vessel, shell OD 540, wall '
      f'{T["wall_mm"]:g} mm (study fab page - hold, W12), on a plinth with heads',
      'The seed once carried the bank as separate columns (PK_1..PK_9 era); the '
      'present graph defines one unit - the model covers that column set as the '
      'node defines it (W12)',
      'Working level set by the duty section 2 holdup basis (0.0827 m3, 30-minute '
      'hold); atmospheric, duty sections 2, 4 and 6'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Shell base head laps the plinth; top head closes at z 780..800 within the box',
      'No internals drawn: the node internals row is none and no authority '
      'dimensions the polish media (duty section 5 names a differential-pressure '
      'instrument across the packing) - nothing invented (W12)',
      'PVC-U per duty section 3 rules M1 and M2; CA does not apply to the polymer'],
     "General arrangement, side elevation. Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     ['7 schedule rows of docs-authority/nozzles/POLISH_BANK.csv at tag, face and '
      'bore',
      'N1 DN50 EW tail in and N7 DN15 raffinate-after-Mo-cut in (face -Y, z 160); '
      'N2/N3 DN50 out and N6 DN15 liquor return out (+Y, z 600)',
      'N4 drain boss on the base head (50 datum); N5 vent flush at the top head '
      '(the 800 datum is the envelope top)',
      'Atmospheric hose barbs; the schedule rating column (Class 150) carried '
      'verbatim as text - no flange drawn (duty section 4)'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("sh01", shell, (0, 1, 0),
     [f'Shell OD 540 x wall {T["wall_mm"]:g} PVC-U, z 40..760, heads, plinth',
      'CA does not apply to the polymer (AQS-STD-001); wall a study value (hold, W12)',
      'Welds per the unit WORK_ORDER route (F-VES): sheet/pipe cut, thermoplastic '
      'weld, set-in ports, leak test'],
     "Fabricated part sheet: shell + heads + plinth."),
    ("aux01", aux, (0, 1, 0),
     ['Connection hardware DN15/DN50 as atmospheric hose barbs (lib/nozzles.py); '
      'barb profile a study proportion, finished against the hose supplier print',
      'Schedule rating column (Class 150) carried verbatim as text - duty section 4 '
      '(atmospheric hose; W4 110 percent rule: no process pressure)',
      'The duty section 4 prose bore line (6.25 mm, DN15) is not a specification '
      'and predates the issued DN50 tail rows - schedule governs (W12)'],
     "Fabricated part sheet: connection hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: EW tail in on -Y, raffinate and liquor return out on +Y, '
      'drain at the base head, vent on the top head',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/polish_bank.step) is the solids of record',
      f'Build fills the node registry envelope exactly; holdup {R["holdup_m3"]} m3 '
      'reported at the duty-basis level, no new residence claim (A-VES)'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/polish_bank.py", f"models/mfg/{unit}/draw_polish_bank.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    [f"- A-VES: the {R['holdup_m3']} m3 liquor volume at the duty-basis working "
     "level is reported - the duty section 2 figure is an existing holdup basis "
     "(30-minute hold), not a new residence claim; duty section 8: the vessel is "
     "not built, so this is not a measured volume",
     "- Internals: none drawn - the node internals row is none and no authority "
     "dimensions the polish media (W12); the PK_1..PK_9 seed history is named and "
     "the model covers the column set as the node defines it",
     "- The duty section 4 prose bore line (DN15) predates the issued DN50 tail "
     "rows; the schedule governs (W12)"],
    "A-core + A-VES")

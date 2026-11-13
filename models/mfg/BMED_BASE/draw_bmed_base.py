"""BMED_BASE drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, stack01 (the EDBM stack), aux01
(connection hardware), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets, step_export  # noqa: E402

ns = runpy.run_path(HERE / "bmed_base.py")
parts, R = ns["parts"], ns["report"]
noz_pieces = ns["noz_pieces"]
unit = "BMED_BASE"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


body = union_all([v for k, v in parts.items() if k != "nozzles"])
for piece in noz_pieces:                                     # piecewise, as the builder exports
    body = body.union(piece)
aux = cq.Workplane(obj=cq.Compound.makeCompound([p.val() for p in noz_pieces]))
full = body
stack = union_all([parts["anode_end_plate"], parts["frame_plate_a"],
                   parts["triplet_laminate"], parts["frame_plate_b"],
                   parts["cathode_end_plate"], parts["tie_rods"]])

L, W, H = [float(v) for v in R["size_mm"]]
S = R["stack"]
X = R["nozzles_drawn"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm overall - the node registry envelope, filled '
      'exactly (the study box; design sizing per the duty sheet follows, W12)',
      'BMED electrodialysis stack skid, base side: drip tray over the envelope, '
      'stack module at the -X end, hold-down beam on posts (sheet STACK01)',
      'Atmospheric tube connections on tray risers, flush at the envelope faces '
      '(sheet AUX01)',
      'PVC-U wetted per duty section 3; electrode plates are the A-M-170 hardware '
      '(Ti/MMO anode, 316L cathode per AQS-STD-002 M6, X-QA-13)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Stack cross-section 300 x 300 centred (y 150..450), frames 300 x 300 per the '
      'AQS-DUTY-068 construction, tie-rod clamped',
      f'Active window 200 x 200 (0.04 m2 per cell), {S["triplets_per_stack"]} triplets '
      f'of 1 bipolar + 2 monopolar membranes, 0.8 mm PE mesh spacers',
      'Tray floor 20 + curb 60 x 10; hold-down beam z 330..350 on four posts; '
      'frame PVC-U drawn, sizing PP named (hold, W12)'],
     "General arrangement, side elevation (stack section). Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     ['8 schedule rows of docs-authority/nozzles/BMED_BASE.csv at tag, face and bore',
      'N1 DN25 and N7 DN15 in on -Y at z 160; N2/N3/N6/N8 out on +Y (schedule '
      'datums 600 clamped down: the 350 box predates them, W12)',
      'N4 drain through the tray floor (50 datum), N5 vent flush at the top face on '
      'the beam (800 datum predates the box, W12)',
      'Per-tag positions in check.nozzles_drawn; the Class 150 rating column carried '
      'verbatim as text - no flange drawn (duty section 4)'],
     "Connection orientation, top view. Tags/faces/bore per the schedule."),
    ("stack01", stack, (0, 1, 0),
     ['EDBM stack per the AQS-DUTY-068 / A-M-170 construction: Ti/MMO anode end '
      'plate, clamp frames, triplet laminate, 316L cathode end plate (M6), tie rods (M4)',
      f'{S["triplets_per_stack"]} triplets at {S["triplet_pitch_mm"]:g} mm pitch '
      '(the A-M-171 compartment + membrane stack-up), 0.04 m2 active window per cell',
      'The sizing page books 421 triplets in 5 stacks of 85 plus 1 spare for the BMED '
      'pair; the node books no per-unit count - representative module drawn (W12)',
      'Frames PVC-U drawn per duty section 3; the construction names PP - both '
      'facts recorded (hold, W12)'],
     "Fabricated part sheet: electrodialysis stack module."),
    ("aux01", aux, (0, 1, 0),
     ['Connection hardware DN15/DN25 as open-bore tube (lib/dn Sch 40 table), '
      'flush at the envelope faces; atmospheric per duty section 4',
      'Side connections ride tray risers; hose makeup by the connecting line at the '
      'face; the W4 110 percent rule draws no flange (no process pressure stated)',
      'N4 drain passes through the tray floor; N5 vent stands 25 on the beam top'],
     "Fabricated part sheet: connection hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: the base-side regen loop and condensate return in on -Y, '
      'the NaOH product, digest draw, 2 M make-up and bleed lines out on +Y',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/bmed_base.step) is the solids of record',
      'Tracker --check green; acceptance A-core + A-CELL per AQS-PLAN-006 section 5'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/bmed_base.py", f"models/mfg/{unit}/draw_bmed_base.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    [f"- A-CELL: triplet count {S['triplets_per_stack']}, frames 300 x 300, pitch "
     f"{S['triplet_pitch_mm']:g} mm, active area 0.04 m2 per cell - the AQS-DUTY-068 "
     "/ A-M-170/171 construction reported from the model; duty section 2 carries no "
     "plate row, so the match is against the sizing construction (W12); POWER.md "
     "states no bus bar for this class",
     "- The pair's stack power is booked on BMED_ACID (this unit's duty section 9); "
     "the sizing design voltage class 1.22-1.67 V/triplet and the AQS-TST-006 "
     "acceptance band are the verification route - figures reported, not recomputed",
     "- Schedule datums clamped into the 350 mm box: the 600 outlet datums down, "
     "the 800 vent flush at the top face, the 50 drain flush through the floor "
     "(holds, W12); N3 row repaired to schedule quoting (hold 7 of HX8 precedent)"],
    "A-core + A-CELL")

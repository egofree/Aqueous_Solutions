"""P_CA drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, sh01 (PP-H vessel), in01 (agitator),
aux01 (drive + nozzles), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets                                       # noqa: E402

ns = runpy.run_path(HERE / "p_ca.py")
parts, R = ns["parts"], ns["report"]
noz_pieces = ns["noz_pieces"]
unit = "P_CA"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


vessel = union_all([parts["frame_plinth"], parts["vessel"]])
agit = union_all([parts["agitator"], parts["agitator_drive"]])
aux = cq.Workplane(obj=cq.Compound.makeCompound([p.val() for p in noz_pieces]))
body = union_all([parts["frame_plinth"], parts["vessel"], parts["agitator"],
                  parts["agitator_drive"]])
for piece in noz_pieces:                                     # piecewise, as the builder exports
    body = body.union(piece)
full = body

L, W, H = [float(v) for v in R["size_mm"]]
V = R["vessel"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm overall - the node seed envelope (the '
      'calcium-soap precipitation vessel at the 0.025 kg/d thickener draw), '
      'filled exactly',
      'Route hold: the node class precip has no AQS-PLAN-006 section 4 route '
      'class; the vessel work follows the F-VES operations as the nearest '
      'family (W10)',
      'PP-H vessel on a steel frame plinth with a PP agitator and its drive '
      '(sheets SH01, IN01, AUX01)',
      'Duty section 6: relief case study pending (unit task 07) - no set point '
      'claimed'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Vessel base head laps the frame plinth; top head closes at z 336..356; '
      'the drive envelope rides the top head to z 400',
      f'Vessel OD 250 x wall {V["wall_mm"]:g} (study - no thickness booked on the '
      'node, W12); scale is knocked down mechanically at clean-out (a design '
      'note, not an allowance)',
      'PP-H per duty section 3 (X-MAT-22); the 316L mixed-build alternative is '
      'a named hold (W12)'],
     "General arrangement, side elevation. Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     ['2 schedule rows of docs-authority/nozzles/P_CA.csv: drain and vent '
      'utilities only - no piped process connection on the graph yet (duty '
      'section 4)',
      'N1 drain, open bore through the plinth and base head, flush at the '
      'envelope bottom (50 datum)',
      'N2 vent flush at the vessel top head (the schedule 800 datum predates '
      'the 400 box, W12)',
      'PE slurry lines wait for rated graph edges - none drawn (hold, W12); '
      'the Class 150 rating column carried verbatim as text, no flange drawn'],
     "Connection orientation, top view. Tags/faces/bore per the schedule."),
    ("sh01", vessel, (0, 1, 0),
     [f'PP-H vessel OD 250 x wall {V["wall_mm"]:g}, z 18..356, heads, on the '
      'steel frame plinth',
      'CA 0 mm (AQS-STD-001 polymer rule); wall a study value (hold, W12)',
      'PP-H at the lib PP table density (910 kg/m3) for the BOM masses'],
     "Fabricated part sheet: PP-H vessel + frame plinth."),
    ("in01", agit, (0, 1, 0),
     ['PP agitator per duty section 3: shaft on the vessel axis from the base '
      'head up through the top head into the drive hub; two blades at z 80 and '
      'z 150',
      'Shaft and blade dimensions are study values (hold, W12); the node '
      'internals row is none, so the tracker records no internal solid',
      'Drive envelope is a purchased item (plan rule 6); drive rating per the '
      'maker TDS at order'],
     "Fabricated part sheet: PP agitator + drive."),
    ("aux01", aux, (0, 1, 0),
     ['Connection hardware DN15 as open-bore tube (lib/dn Sch 40 table dims, '
      'PP-H pipe); atmospheric per duty section 4',
      'Instrument loops P_CALT-01, P_CAPT-01, P_CATE-01 are loop hardware, not '
      'modeled (duty section 5)',
      'The PCA_TO_GREASE edges carry no kg/d rate yet (duty section 8) - no '
      'process nozzles are invented'],
     "Fabricated part sheet: connection hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: drain at the tray, vent at the vessel top head, '
      'agitator drive on top',
      f'Graph revision {R["graph_revision"]} is the model authority for this '
      'build; STEP (export/p_ca.step) is the solids of record',
      f'Build fills the node seed envelope exactly; working volume '
      f'{R["working_volume_m3"]} m3 reported for the record - the duty books no '
      'holdup basis, so no level or residence is derived'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/p_ca.py", f"models/mfg/{unit}/draw_p_ca.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ["- Route hold: the node class precip has no AQS-PLAN-006 section 4 route "
     "class; the tracker records the hold (A-core, route hold) and the vessel "
     "work follows the F-VES operations as the nearest family (W10)",
     "- PP-H vessel + PP agitator per duty section 3 (X-MAT-22); wall and "
     "agitator dimensions study values (holds, W12); the 316L mixed-build "
     "alternative named; the duty section 8 'material selection pending' line "
     "predates the issued X-MAT-22 selection",
     "- Relief case study pending (unit task 07): no set point claimed; "
     "instrument loops are loop hardware, not modeled"],
    "A-core (route hold)")

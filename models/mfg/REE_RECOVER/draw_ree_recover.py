"""REE_RECOVER drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, fr01 (frame + shelves), skid01
(purchased envelopes, lower shelf), skid02 (upper shelf), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets, step_export  # noqa: E402

ns = runpy.run_path(HERE / "ree_recover.py")
parts, R = ns["parts"], ns["report"]
noz_pieces = ns["noz_pieces"]
unit = "REE_RECOVER"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


fr = union_all([parts["frame"], parts["shelving"]])
skid1 = union_all([parts["demag_oven"], parts["leach_reactor"]])
skid2 = union_all([parts["vacuum_filter"], parts["calcining_muffle"]])
aux = cq.Workplane(obj=cq.Compound.makeCompound([p.val() for p in noz_pieces]))
body = union_all([parts["frame"], parts["shelving"], parts["demag_oven"],
                  parts["leach_reactor"], parts["vacuum_filter"],
                  parts["calcining_muffle"]])
for piece in noz_pieces:                                     # piecewise, as the builder exports
    body = body.union(piece)
full = body

L, W, H = [float(v) for v in R["size_mm"]]
E = R["equipment"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm overall - the bench campaign skid box, '
      'filled exactly (fume-hood class, MET_SYN row)',
      'Route hold: the node class precip has no AQS-PLAN-006 section 4 route '
      'class; the skid work follows the F-MACH frame and F-VES vessel '
      'operations as the nearest families (W10)',
      'REE_RECOVER batch campaign per A-M-433 (X-END-02): demag oven and 10 L '
      'leach reactor lower shelf, filter and muffle upper shelf',
      'Purchased envelopes per plan rule 6 - envelope and interface only, '
      'internals with the maker (sheets SKID01, SKID02)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     [f'AQS-MOD-002 frame, 80 x 5 tube, the fixed weld pattern; shelves at z 180 '
      f'and z 900; floor drip plate at the base (layout choices, W12)',
      f'316L tube frame per the wet-bench class (HCl fume service; layout choice, '
      f'W12); CA 0 mm (AQS-STD-001 rules)',
      'The vent riser stands from the upper-shelf zone to the box top - the H2 '
      'vent to the acid-scrubber header (duty section 2 sizing)'],
     "General arrangement, side elevation. Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     ['2 schedule rows of docs-authority/nozzles/REE_RECOVER.csv: drain and vent '
      'utilities only - no piped process connection on the graph yet (duty '
      'section 4)',
      'N1 drain, open bore through the floor plate, flush at the envelope '
      'bottom (50 datum)',
      'N2 vent riser flush at the envelope top (the schedule 800 datum predates '
      'the 1400 box, W12)',
      'The Class 150 rating column carried verbatim as text - no flange drawn '
      '(W4 110 percent rule: no process pressure stated)'],
     "Connection orientation, top view. Tags/faces/bore per the schedule."),
    ("fr01", fr, (0, 1, 0),
     ['Frame and shelving: the AQS-MOD-002 parameter set at the 800 x 600 bay, '
      'two shelves and the floor plate in 316L plate',
      'Frame mass per the AQS-MOD-002 section 5 table (the lib frame rule)',
      'Anchor points at the four frame feet; slab fixings in fasteners.csv'],
     "Fabricated part sheet: frame + shelves."),
    ("skid01", skid1, (0, 1, 0),
     ['Lower shelf: demag oven envelope (300 x 300 x 280; > 320 C, 5 L class) '
      'and the glass-lined leach reactor envelope (OD 240 x 380, covers the '
      '10 L charge; 55 C jacket, stirrer, H2 vent)',
      'Purchased items named with the rating from the duty section 2 sizing '
      'line (plan rule 6); envelope positions are the layout choice (W12)',
      'Wetted parts per the maker TDS at order; the row masses are envelope '
      'masses at the tabulated shell densities'],
     "Fabricated part sheet: lower-shelf purchased envelopes."),
    ("skid02", skid2, (0, 1, 0),
     ['Upper shelf: PP-H vacuum filter envelope (300 x 220 x 250) and the '
      'calcining muffle envelope (320 x 280 x 260; 900 C, 2 L, 316L shell '
      'dry oxide)',
      'PP-H filter wetted per duty section 3; the Hastelloy C-276 alternative '
      'if the campaign moves above 60 C is a named hold (W12)',
      'Purchased items per plan rule 6: envelope and interface only, internals '
      'with the maker'],
     "Fabricated part sheet: upper-shelf purchased envelopes."),
    ("aux01", aux, (0, 1, 0),
     ['Connection hardware DN15 as open-bore tube (lib/dn Sch 40 table dims, '
      '316L); atmospheric per duty section 4',
      'N1 drain passes through the floor plate; N2 rides the upper-shelf zone '
      'to the box top',
      'No instrument loop yet (unit task 08); relief case pending (unit task '
      '07) - no trip or set point specified'],
     "Fabricated part sheet: connection hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: demag + leach lower, filter + muffle upper, drain at '
      'the floor plate, H2 vent riser at the box top',
      f'Graph revision {R["graph_revision"]} is the model authority for this '
      'build; STEP (export/ree_recover.step) is the solids of record',
      f'Build fills the node skid box exactly; campaign figures '
      f'({R["campaign"]["campaign_kg"]:g} kg NdFeB, {R["campaign"]["reo_kg"]:g} kg '
      'REO per campaign) reported from the node sizing block, nothing '
      'recomputed here'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/ree_recover.py", f"models/mfg/{unit}/draw_ree_recover.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ["- Route hold: the node class precip has no AQS-PLAN-006 section 4 route "
     "class; the tracker records the hold (A-core, route hold) and the skid "
     "work follows the F-MACH frame and F-VES vessel operations as the nearest "
     "families (W10)",
     "- Purchased equipment per plan rule 6: the duty section 2 sizing line "
     "names the set (demag oven, 10 L glass-lined reactor, PP-H filter, 900 C "
     "muffle); each is drawn as its envelope and interface only; envelope "
     "positions are the layout choice (W12)",
     "- Relief case pending (unit task 07) and no instrument loop yet (unit "
     "task 08): no trip or set point specified; nozzle elevations are schedule "
     "placeholders"],
    "A-core (route hold)")

"""MEOH_FC drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, stack01 (cell stack + bus), aux01
(reformer + bed envelope), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets                                       # noqa: E402

ns = runpy.run_path(HERE / "meoh_fc.py")
parts, R = ns["parts"], ns["report"]
noz_pieces = ns["noz_pieces"]
unit = "MEOH_FC"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else s.union(s)
    return u


stack = union_all([parts["stack_stand"], parts["stack_ends"], parts["stack_pack"],
                   parts["bus_bars"], parts["bus_return"]])
aux = union_all([parts["base_plate"], parts["reformer_saddle"], parts["reformer"],
                 parts["reformer_bed"]])
body = union_all([stack, aux])
for piece in noz_pieces:
    body = body.union(piece)
full = body

L, W, H = [float(v) for v in R["size_mm"]]
AC = R["a_cell"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm overall - the node envelope (AQS-DUTY-077 '
      'methanol-train residual sizing); the duty prose 1600 skid line predates it (W12)',
      f'Direct methanol fuel-cell skid: {AC["n_cells"]}-cell stack (0.6 V at 0.3 A/cm2 '
      f'on {AC["cell_A_cm2"]:g} cm2 cells, {AC["stack_area_m2_node"]:g} m2) at the centre, '
      '316L reformer shell (Cu/ZnO class bed) at the -X end',
      'Copper bus 30 x 5 from the stack end plate to the +Y face at the N5 datum '
      '(duty section 3: conductors are copper)',
      'The MEA laminate and the catalyst bed drawn as envelopes (plan rule 6)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     [f'Stack: end plates {AC["plate_mm"]:g} x {AC["plate_mm"]:g} at {AC["pitch_mm"]:g} mm '
      f'pitch enclosing the {AC["active_mm"]:g} mm active window; count and active '
      'area per the node design block',
      'Duty section 2 carries no plate row - the A-CELL match is against the node '
      'design construction (hold, W12); POWER.md states no bus-bar section for this '
      'unit (W12)',
      'Rated 1.0 kWe at the S79 point; the methanol draw supports about 0.5 kWe '
      'continuous - part load on the dispatch schedule (node design note)'],
     "General arrangement, side elevation. Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     [f'{R["nozzle_count_schedule"]} schedule rows of docs-authority/nozzles/'
      'MEOH_FC.csv at tag, face and bore',
      'N1 MeOH fuel, N2 cell air, N3 tank draw and N4 leach condensate in on -Y at '
      'z 160; N6 heat (less than 80 C), N7 condensate, N8 CO2 return and N11 cell '
      'exhaust out on +Y at z 600 - datums draw as issued',
      'N5 (MEOH DC) is the DC conductor per duty section 4 prose: drawn as the '
      'copper bus pad at the schedule face/height; a conductor has no bore (W12)',
      'N9 drain boss under the reformer (flush at the envelope bottom, 50 datum); '
      'N10 vent riser on the reformer head, flush at the envelope top (800 datum, W12)'],
     "Connection orientation, top view. Tags/faces/bore per the schedule."),
    ("stack01", stack, (0, 1, 0),
     [f'Cell stack: end plates 316L, the {AC["n_cells"]}-cell MEA laminate envelope '
      'at its gasket clearance (buy, plan rule 6), PTFE gaskets',
      'Tie rods in fasteners.csv compress the plate pair; bus bars copper per '
      'duty section 3',
      'Assembly per the F-CELL route: plate shear and punch, bus bar cut and '
      'drill, gasket cut, stack assembly'],
     "Fabricated part sheet: cell stack + bus."),
    ("aux01", aux, (1, -0.5, 0.7),
     [f'Reformer shell OD 150 x wall 4 (study), z 40..440, heads, on the saddle; '
      'the Cu/ZnO class bed drawn as its envelope (buy, plan rule 6)',
      'Skid base plate 1800 x 800 x 20 (AQS-MOD-002 dry service class); 6 slab '
      'anchors in fasteners.csv',
      'No wetted alloy (duty section 3); CA does not apply'],
     "Fabricated part sheet: reformer + skid base."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: methanol fuel and air in on -Y, DC out on the copper bus '
      'at the +Y face, condensate and CO2 return out on +Y, drain at the base, '
      'vent at the box top',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/' + 'meoh_fc' + '.step) is the solids of record',
      'The skid chain fuses to one solid; the laminate envelope and the face stubs '
      'stay separate until assembly (check.solids_note)'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/meoh_fc.py", f"models/mfg/{unit}/draw_meoh_fc.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ['- A-CELL: 28 cells, 200 cm2 active each (0.56 m2 total per the node design), '
     'plate 160 x 160 at 6 mm pitch enclosing the 141.4 mm active window; duty '
     'section 2 carries no plate row, so the match is against the node design '
     '(hold, W12)',
     '- Bus: copper per duty section 3; POWER.md states no bus-bar section for '
     'this unit - the criterion has nothing to match (W12)',
     '- The N5 (MEOH DC) row drawn as the copper conductor pad per duty section 4 '
     'prose (holds, W12)'],
    "A-core + A-CELL")

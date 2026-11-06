"""MEOH_SYNTH drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, reactor01 (pressure part), aux01
(jacket, bed envelope, preheater), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets                                       # noqa: E402

ns = runpy.run_path(HERE / "meoh_synth.py")
parts, R = ns["parts"], ns["report"]
noz_pieces = ns["noz_pieces"]
unit = "MEOH_SYNTH"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else s.union(s)
    return u


reactor = union_all([parts["plinth"], parts["bottom_flange"], parts["tube"],
                     parts["top_flange"]])
aux = union_all([parts["jacket"], parts["bed"], parts["grid_bottom"], parts["grid_top"],
                 parts["preheater"]])
nozh = cq.Workplane(obj=cq.Compound.makeCompound([p.val() for p in noz_pieces]))
body = reactor
for k in ("jacket", "bed", "grid_bottom", "grid_top", "preheater"):
    body = body.union(parts[k])
for piece in noz_pieces:                                     # piecewise, as the builder exports
    body = body.union(piece)
full = body

L, W, H = [float(v) for v in R["size_mm"]]
RC = R["reactor"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm overall - the node envelope (X-MFG-31 '
      'reactor_design), filled by the vent riser top',
      'Fixed-bed synthesis tube DN50 (OD 60.3 x wall 3.91, L_bed 1485 + 400), '
      'DN50 Class 600 flanges pair, DN100 thermal-oil jacket to Q3',
      'Material 316L per duty section 3: synthesis 50 bar a, 250 C, API 941 '
      '(AQS-REV-H2-001 section 5); the node SA-106 B row predates it (W12)',
      'Feed preheater 0.818 kW envelope at the +X corner (purchased, plan rule 6)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     [f'Bed {RC["bed"]["length_mm"]:g} mm of Cu/ZnO/Al2O3 ({RC["bed"]["volume_L_node"]:g} L, '
      f'{RC["bed"]["cat_kg"]:g} kg) inside the tube bore at running clearance; '
      'support grids at the bed ends',
      f'Design {RC["design_pressure"]["MPa"]:g} MPa: t_req '
      f'{RC["design_pressure"]["t_req_mm"]:g} mm against t_nom '
      f'{RC["design_pressure"]["t_nom_mm"]:g} mm (node t_ok)',
      'The A-VES holdup is the bed volume, reported; no residence time is derived '
      '(duty section 2 claims no holdup; a fixed bed)'],
     "General arrangement, side elevation. Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     [f'{R["nozzle_count_schedule"]} schedule rows of docs-authority/nozzles/'
      'MEOH_SYNTH.csv at tag, face and bore',
      'N1 CO2 and N2 H2 in on -Y at z 160, N8 CO2-not-taken at the pack; N3 crude '
      'MeOH, N6 co-feed, N7 synthesis water and N9 mercaptan trace out on +Y at '
      'z 600 - datums draw as issued (both fit the 2585 box)',
      'N4 drain boss under the bottom flange (flush at the envelope bottom, 50 '
      'datum); N5 vent riser on the top flange, flush at the envelope top (the 800 '
      'datum is the placeholder elevation, W12)',
      'Side stubs pierce to the tube axis so every takeoff lands on the vessel; '
      'elevations are the schedule placeholders pending vessel design (duty '
      'section 4, W12)',
      'N10 cable power terminal: carried verbatim, not drawn'],
     "Connection orientation, top view. Tags/faces/bore per the schedule."),
    ("reactor01", reactor, (0, 1, 0),
     [f'Tube DN50 OD {RC["tube"]["od_mm"]:g} x wall {RC["tube"]["wall_mm"]:g}, '
      f'{RC["tube"]["length_mm"]:g} mm; Class 600 flange pair OD '
      f'{RC["flanges"]["od_mm"]:g} x {RC["flanges"]["t_mm"]:g} (B16.5)',
      '316L per duty section 3 (API 941); CA 0 mm (AQS-STD-001); welds GTAW per '
      'ASME IX qualified procedures; 100 % radiography of the butt welds',
      'Hydro test at 1.3 x the 5.5 MPa design (UG-99); the catalyst reduction '
      'schedule is an operating-procedure item'],
     "Fabricated part sheet: pressure part (tube + flanges) on the plinth."),
    ("aux01", aux, (1, -0.5, 0.7),
     [f'Jacket DN100 OD {RC["jacket"]["od_mm"]:g} x wall {RC["jacket"]["wall_mm"]:g}, '
      'thermal-oil service, exotherm to Q3 (node design)',
      'Catalyst bed envelope (purchased, plan rule 6) and support grids at running '
      'clearance inside the bore; they are not welded to the pressure part',
      'Feed preheater 0.818 kW envelope and interface (purchased, plan rule 6)'],
     "Fabricated part sheet: jacket, bed envelope, grids, preheater."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: CO2 and H2 in low on -Y, crude MeOH and water out at z 600 '
      'on +Y, drain at the base, vent riser at the box top',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/' + 'meoh_synth' + '.step) is the solids of record',
      'The face connection hardware is atmospheric open-bore tube (duty section 4); '
      'the pressure-part flanges carry the Class 600 rating'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/meoh_synth.py", f"models/mfg/{unit}/draw_meoh_synth.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ['- Pressure part 316L per duty section 3 (API 941, AQS-REV-H2-001 section 5); '
     'the node SA-106 B tube row superseded (hold, W12)',
     '- A-VES: the bed volume (3.213 L model against the node 3.2143 L V_work_L) is '
     'reported; no residence time derived (duty section 2 claims no holdup)',
     '- Purchased items as envelopes per plan rule 6: catalyst bed (3.54 kg '
     'Cu/ZnO/Al2O3) and feed preheater (0.818 kW)',
     '- Two solids: the vessel chain and the bed-with-grids envelope at running '
     'clearance in the bore; both closed and manifold'],
    "A-core + A-VES")

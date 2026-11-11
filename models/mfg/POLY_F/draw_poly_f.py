"""POLY_F drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, kettle01 (kettle + jacket), aux01
(agitator + drive envelope + connection hardware), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets, step_export  # noqa: E402

ns = runpy.run_path(HERE / "poly_f.py")
parts, R = ns["parts"], ns["report"]
noz_pieces = ns["noz_pieces"]
unit = "POLY_F"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else s.union(s)
    return u


kettle = union_all([parts["plinth"], parts["legs"], parts["support_ring"],
                    parts["kettle"], parts["jacket"]])
aux = union_all([parts["agitator"], parts["drive"]])
body = union_all([kettle, aux])
for piece in noz_pieces:
    body = body.union(piece)
full = body

L, W, H = [float(v) for v in R["size_mm"]]
K = R["kettle"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm envelope - the reactor-class study minimum '
      '(jacketed kettle at the 0.25 kg/d monomer duty, reclaim loop to F_RECOVER, '
      'A-M-289), filled by the vent riser top',
      'Emulsion polymerization kettle OD 150 x 225 shell (node design) with '
      'heads, jacket envelope, on the stand over the plinth',
      'Hastelloy C-276 wetted, PTFE gasketed per duty section 3 (the node row '
      'matches); VDF/TFE monomer from the gas train',
      'The build replaces the pre-plan M2 study build; the old +Y overhang is '
      'gone - hardware flush at the envelope faces'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     [f'Agitator per the node power basis (jacket loss + agitator, A-M-289): '
      'shaft and two-blade impeller drawn as solids into the purchased drive '
      'envelope (plan rule 6)',
      f'Gross shell volume {K["gross_volume_L"]:g} L reported for the record; the '
      'duty claims no holdup figure and no residence time is derived (A-VES)',
      f'Shell wall {K["wall_mm"]:g} mm is the study fab-page value; the node books '
      'no thickness (hold, W12)'],
     "General arrangement, side elevation. Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     [f'{R["nozzle_count_schedule"]} schedule rows of docs-authority/nozzles/'
      'POLY_F.csv at tag, face and bore',
      'N1 VDF and N2 TFE monomer in on -Y at z 160; N3 (PVDF/PTFE resin) and N4 '
      '(fluoropolymer powder) out on +Y at z 600 - both solids rows drawn DN15, '
      'bore not calculated (plan W4)',
      'N5 (PVDF resin to the film/sheet line) and N6 (off-spec scrap/rework) out '
      'on +Y at z 600; N7 drain boss under the base head (flush at the envelope '
      'bottom, 50 datum); N8 vent riser on the top head, flush at the envelope '
      'top (the 800 datum is the placeholder, W12)',
      'Atmospheric joints per duty section 4; Class 150 column verbatim, no '
      'flange drawn'],
     "Connection orientation, top view. Tags/faces/bore per the schedule."),
    ("kettle01", kettle, (0, 1, 0),
     [f'Kettle OD 150, shell 225, heads, z {K["z_mm"][0]:g}..{K["z_mm"][1]:g}; '
      'jacket envelope OD 184 / ID 162 (layout choice, W12)',
      'C-276 welds per the route (F-VES): plate cut, roll, GTAW per ASME IX '
      'practice, nozzle set-in, leak test; PTFE-gasketed joints per the '
      'material row',
      'Reclaim loop to F_RECOVER per the node envelope basis'],
     "Fabricated part sheet: kettle + jacket envelope + stand."),
    ("aux01", aux, (1, -0.5, 0.7),
     ['Agitator shaft and impeller (solids, the node power basis A-M-289); the '
      'drive is the purchased envelope per plan rule 6',
      'Drive rating reads the maker sheet at order; the node carries no rpm or '
      'impeller datum (study values, W12)',
      'Support ring, 4 legs and plinth in carbon steel (dry service)'],
     "Fabricated part sheet: agitator + drive envelope."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: VDF and TFE monomer in on -Y, resin, powder and '
      'reclaim out on +Y, drain at the base, vent at the box top',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/' + 'poly_f' + '.step) is the solids of record',
      'The skid chain fuses to one solid; the face stubs stay separate until the '
      'connecting lines make their joints (check.solids_note)'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/poly_f.py", f"models/mfg/{unit}/draw_poly_f.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ['- Replaces the pre-plan M2 study build: the old +Y connection overhang '
     '(bbox 630 against the 600 envelope) is gone - hardware flush at the '
     'envelope faces, the envelope itself unchanged (nothing resized)',
     '- Agitator drawn as solids per the node power basis (jacket loss + '
     'agitator, A-M-289) into the purchased drive envelope (plan rule 6)',
     '- A-VES: gross shell volume reported for the record; no holdup claimed, '
     'no residence derived (W12)'],
    "A-core + A-VES")

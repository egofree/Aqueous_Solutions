"""POLY_COND drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, kettle01 (kettle + jacket), aux01
(agitator + drive envelope + stand), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets, step_export  # noqa: E402

ns = runpy.run_path(HERE / "poly_cond.py")
parts, R = ns["parts"], ns["report"]
noz_pieces = ns["noz_pieces"]
unit = "POLY_COND"


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
      '(AQS-DUTY-073); the build sits inside it (standby unit, W12)',
      'Condensation resin kettle OD 200 x 300 shell (node design) with heads, '
      'jacket envelope (jacket_C 160), on the stand over the plinth',
      'Installed standby: the DIGEST_TO_POLY edge stays 0 until the digester '
      'organic assay issues the recipe (node design note)',
      '316L per duty section 3; the Hastelloy option is a named hold (W12)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     [f'Agitator per the node design row (0.18 kW): shaft and two-blade impeller '
      'drawn as solids into the purchased drive envelope (plan rule 6)',
      f'Gross shell volume {K["gross_volume_L"]:g} L reported for the record; the '
      'duty claims no holdup and no residence time is derived (A-VES)',
      f'Shell wall {K["wall_mm"]:g} mm is the study fab-page value; the node books '
      'no thickness (hold, W12)'],
     "General arrangement, side elevation. Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     [f'{R["nozzle_count_schedule"]} schedule rows of docs-authority/nozzles/'
      'POLY_COND.csv at tag, face and bore',
      'N1 digester organics in on -Y at z 160 (face hardware; the connecting line '
      'makes the joint at the face)',
      'N2 drain boss under the base head (flush at the envelope bottom, 50 datum); '
      'N3 vent riser on the top head flushing at the envelope top (the 800 datum is the schedule placeholder, W12)',
      'Atmospheric joints per duty section 4; the schedule rating column (Class '
      '150) carried verbatim as text - no flange drawn'],
     "Connection orientation, top view. Tags/faces/bore per the schedule."),
    ("kettle01", kettle, (0, 1, 0),
     [f'Kettle OD 200, shell 300, heads, z {K["z_mm"][0]:g}..{K["z_mm"][1]:g}; '
      'jacket envelope OD 234 / ID 212 (layout choice, W12)',
      'Welds per the route (F-VES): plate cut, roll, GTAW per ASME IX practice, '
      'nozzle set-in, leak test',
      'Standby envelope: the model covers the installed geometry the node issues'],
     "Fabricated part sheet: kettle + jacket envelope + stand."),
    ("aux01", aux, (1, -0.5, 0.7),
     ['Agitator shaft and impeller (solids, node design row); the 0.18 kW drive '
      'is the purchased envelope per plan rule 6',
      'Drive rating reads the maker sheet at order; the node carries no rpm or '
      'impeller datum (study values, W12)',
      'Support ring, 4 legs and plinth in carbon steel (dry service)'],
     "Fabricated part sheet: agitator + drive envelope."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: digester organics in on -Y when the recipe activates; '
      'drain at the base, vent riser at the 800 datum',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/' + 'poly_cond' + '.step) is the solids of record',
      'The skid chain fuses to one solid; the inlet face stub stays separate until '
      'the connecting line makes its joint (check.solids_note)'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/poly_cond.py", f"models/mfg/{unit}/draw_poly_cond.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ['- Installed standby: the node envelope state is standby and the duty flows '
     'are 0; the model covers the installed geometry (W12)',
     '- Agitator drawn as solids per the node design row (0.18 kW) into the '
     'purchased drive envelope (plan rule 6)',
     '- A-VES: gross shell volume reported for the record; no holdup claimed, no '
     'residence derived (W12)'],
    "A-core + A-VES")

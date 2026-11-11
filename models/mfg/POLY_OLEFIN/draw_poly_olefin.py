"""POLY_OLEFIN drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, vessel01 (vessel + stand), aux01
(connection hardware), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets, step_export  # noqa: E402

ns = runpy.run_path(HERE / "poly_olefin.py")
parts, R = ns["parts"], ns["report"]
noz_pieces = ns["noz_pieces"]
unit = "POLY_OLEFIN"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else s.union(s)
    return u


vessel = union_all([parts["plinth"], parts["legs"], parts["support_ring"],
                    parts["vessel"]])
aux = parts["nozzles"]
body = union_all([vessel, aux])
full = body

L, W, H = [float(v) for v in R["size_mm"]]
V = R["vessel"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm envelope - the reactor-class study minimum '
      '(node envelope basis: DN150 at 1 d hold-up of the naphtha feed at 750 '
      'kg/m3; wall by UG-27 at 5 MPa), filled by the vent riser top',
      f'Oligomerization reactor OD 150 x 225 shell (node design), wall '
      f'{V["wall_mm"]:g} mm by UG-27 at the 5 MPa design; op window 150-250 C at '
      '1-5 MPa (AQS-SIZE-OIL-POLY)',
      'SA-240 316L welded per duty section 3 (the node design row matches); '
      'CA 0 mm (AQS-STD-001)',
      'The node names no agitator and no jacket - none drawn (W12)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     [f'Gross shell volume {V["gross_volume_L"]:g} L reported; the node envelope '
      f'basis books the 1 d hold-up of the 0.2941 kg/d feed (0.39 L at 750 kg/m3) '
      '- an existing basis, no new residence time derived (A-VES)',
      'Support ring and 4 legs over the plinth (carbon steel, dry service)',
      'Vent riser on the top head flushing at the envelope top (the 800 datum is '
      'the schedule placeholder, W12)'],
     "General arrangement, side elevation. Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     [f'{R["nozzle_count_schedule"]} schedule rows of docs-authority/nozzles/'
      'POLY_OLEFIN.csv at tag, face and bore',
      'N1 light cuts, N2 methanol co-feed and N4 C5-C10 naphtha in on -Y at '
      'z 160; N3 polyolefin resin out on +Y at z 600 - datums draw as issued',
      'N3 carries the line-list classification solids (non-piped transfer): '
      'drawn DN15, bore not calculated (plan W4)',
      'N5 drain boss under the base head (flush at the envelope bottom, 50 '
      'datum); N6 vent riser on the top head; atmospheric joints per duty '
      'section 4, Class 150 column verbatim, no flange'],
     "Connection orientation, top view. Tags/faces/bore per the schedule."),
    ("vessel01", vessel, (0, 1, 0),
     [f'Vessel OD 150, wall {V["wall_mm"]:g} (UG-27 at 5 MPa), shell 225, heads, '
      f'z {V["z_mm"][0]:g}..{V["z_mm"][1]:g}; support ring and legs over the plinth',
      'SA-240 316L welded, GTAW per ASME IX practice; nozzle set-in; leak test',
      'The node names no agitator and no jacket - none drawn (W12)'],
     "Fabricated part sheet: vessel + stand."),
    ("aux01", aux, (1, -0.5, 0.7),
     ['Connection hardware DN15 as open-bore tube stubs flush at the envelope '
      'faces; atmospheric per duty section 4; Class 150 column verbatim',
      'All 6 schedule rows present at tag, face, height and bore; the N3 solids '
      'row drawn DN15, bore not calculated (plan W4)',
      'Per-tag positions in check.nozzles_drawn'],
     "Fabricated part sheet: connection hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: light cuts and naphtha in on -Y, the polyolefin resin '
      'out on +Y, drain at the base, vent at the box top',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/' + 'poly_olefin' + '.step) is the solids of record',
      'The skid chain fuses to one solid; the face stubs stay separate until the '
      'connecting lines make their joints (check.solids_note)'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/poly_olefin.py", f"models/mfg/{unit}/draw_poly_olefin.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ['- Wall 3.8 mm per the node design row (UG-27 at the 5 MPa design); '
     'SA-240 316L welded per duty section 3 (the node row matches)',
     '- A-VES: gross shell volume 3.6 L reported; the 1 d hold-up of the naphtha '
     'feed is the node envelope basis (existing), no new residence time derived',
     '- The N3 solids row drawn DN15, bore not calculated (plan W4); no agitator '
     'and no jacket named on the node - none drawn (W12)'],
    "A-core + A-VES")

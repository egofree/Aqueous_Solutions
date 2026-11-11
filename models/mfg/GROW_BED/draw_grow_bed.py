"""GROW_BED drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, bed01 (basin + ribs + sump + liner),
canopy01 (posts + rails + LED panel), bay01 (the registry bay module), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets, step_export  # noqa: E402

ns = runpy.run_path(HERE / "grow_bed.py")
parts, R = ns["parts"], ns["report"]
unit = "GROW_BED"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


bed = union_all([parts["bay_module"], parts["basin"]])
canopy = union_all([parts["canopy"], parts["led_panel"]])
full = union_all(list(parts.values()))

M = R["machine"]
AF = M["area"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     ['Keys: the full bed is the build - interior 7280 x 4000 mm = 29.12 m2 '
      '(A-M-229 crew duty), 400 high; the study box 2000 x 1000 x 400 is the '
      'bay-module registry box (check.json cad_stl_scope)',
      'A-FARM: bed area matches the node, liner and drain drawn, NOT shrunk to '
      'fit the block; the export bbox reads against size_mm as the section-7 '
      'misfit - nothing resized (plan rule 3)',
      'HDPE basin (walls/floor 15 mm) + EPDM liner 5 mm (GROWBED_A idiom); '
      'LECA media at a 250 mm study depth (hold, W12)',
      'LED canopy: panel envelope over the bed, 2.0463 kW = 29.12 m2 x 70.3 '
      'W/m2 (A-M-133/A-M-144); purchased per plan rule 6'],
     "General arrangement, front elevation (long wall). Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Cross-section: basin 400 high, media 250 study depth, canopy posts and '
      'rails to z 900 with the panel at z 840 (layout choice, hold W12)',
      'Duty section 2 circulation: 19100.9 kg/d, two-minute holdup 0.0265 m3 - '
      'reported, not a residence-time claim',
      'Duty section 8 note stands: if this node is also a reservoir, that volume '
      'is not the two-minute holdup'],
     "General arrangement, side elevation (end view). Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     ['22 schedule rows of docs-authority/nozzles/GROW_BED.csv at tag, face and bore',
      'Bed rows: N1-N4 in on -Y at z 80; N5-N8 out on +Y at z 300 (the bed water '
      'line); N13/N14/N16/N17/N19 in at z 160',
      'Canopy rows N11/N12/N15/N18/N20/N21/N22 at the schedule z 600 datum sit '
      'above the build height - drawn flush at the envelope top (hold, W12)',
      'N9 drain flush at the envelope bottom over the bay sump (50 datum); N10 '
      'vent at the envelope top; atmospheric tube per duty section 4'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("bed01", bed, (0, 1, 0),
     ['HDPE basin: walls and floor 15 mm, interior 7280 x 4000 mm = 29.12 m2 '
      '(A-M-229), with internal cross-ribs framing the nominal 2000 x 1000 bays',
      'EPDM liner 5 mm (buy roll; GROWBED_A ponded-zone idiom); LECA media at a '
      '250 mm study depth (the charge is a buy row, the envelope drawn)',
      'Drain sump 300 x 300 x 120 at the bay corner with the N9 drain above it '
      '(A-FARM: drain drawn); sump size a study value (hold, W12)'],
     "Fabricated part sheet: basin + ribs + sump + media envelope."),
    ("canopy01", canopy, (0, 1, 0),
     ['LED canopy: 4 posts and perimeter rails to z 900 (painted A500, farm '
      'frame class; the frame is not the wetted part, duty section 3)',
      'LED panel envelope over the bed: the node continuous 2.0463 kW (A-M-144) '
      '- purchased per plan rule 6; the panel mass is a table-density placeholder '
      'until the maker TDS quotes (hold, W12)',
      'Canopy height is the layout choice (hold, WORK_ORDER W12)'],
     "Fabricated part sheet: canopy + LED panel."),
    ("bay01", union_all([parts["bay_module"]]), (1, -1, 1),
     ['The registry bay module: 2000 x 1000 x 400 mm, exactly the node size_mm '
      '(the X-PAR-04 gate; the CRYO_ASU treatment)',
      'A genuine subset of the build: the corner bay of the basin with its walls, '
      'liner, media envelope and the drain sump',
      'The full bed is the export/ build and the STEP (check.json cad_stl_scope)'],
     "Fabricated part sheet: the registry bay module."),
    ("iso01", full, (1, -1, 1),
     ['Plant orientation: bed rows on the -Y/+Y walls; the canopy rows at the '
      'envelope top; drain at the bay-corner sump',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/grow_bed.step) is the solids of record',
      'Tracker --check green (misfit reported per plan rule 3); acceptance '
      'A-core + A-FARM per AQS-PLAN-006 section 5 (route F-FARM)'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/grow_bed.py", f"models/mfg/{unit}/draw_grow_bed.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ["- Crop grow bed per the node area_basis (A-M-229): HDPE basin + EPDM "
     "liner, interior 7280 x 4000 mm = 29.12 m2, LECA media envelope at a 250 "
     "mm study depth, drain sump at the bay corner (A-FARM: liner and drain "
     "drawn), LED canopy at the node 2.0463 kW stamp (A-M-144)",
     "- A-FARM: bed area matches the node, NOT shrunk to fit the study box - "
     "the full bed is the export/ build; the registry carries the 2000 x 1000 x "
     "400 bay module (the CRYO_ASU X-PAR-04 treatment) and the export bbox "
     "misfit is section-7-reported, nothing resized (plan rule 3)",
     "- 22 schedule rows verbatim; the z 600 canopy rows drawn at the envelope "
     "top (stale datum, hold W12); media depth/sump/canopy height study values "
     "(holds, WORK_ORDER W12)"],
    "A-core + A-FARM")

# no nozzle CSV gap to patch here (22 rows exist); nothing superseded to strip

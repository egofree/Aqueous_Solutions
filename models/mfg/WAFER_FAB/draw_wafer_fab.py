"""WAFER_FAB drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, bench01 (plinth + deck + frame),
stations01 (node-equipment station envelopes), purge01 (N2 purge distribution),
aux01 (connection hardware), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets, step_export  # noqa: E402

ns = runpy.run_path(HERE / "wafer_fab.py")
parts, R = ns["parts"], ns["report"]
unit = "WAFER_FAB"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


bench = union_all([parts["plinth"], parts["deck"], parts["frame"]])
stations = parts["stations"]
purge = parts["purge"]
aux = parts["nozzles"]
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm envelope - the node size_mm '
      f'({R["size_basis"] or "node size_mm"}); the duty section 2 states no '
      'envelope - the node governs (hold W12)',
      'Wafer-fab tool row: CZ puller, ingot cool/anneal, crop/grind/edge and the '
      'FAB_TOOL dry row as purchased-class station envelopes per plan rule 6, on '
      'the bench deck inside the four-post hold-down frame',
      'Node note carried as text: ISO 14644-1 Class 7 wet bench, Class 6 tool row',
      'Material per duty section 3: 316L where the stream is wet; CA 0 mm '
      '(AQS-STD-001)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Station kW are node equipment figures (the calculated connected load '
      '0.4417 kW total); the station arrangement is the layout choice '
      '(WORK_ORDER W12)',
      'N2 purge distribution header DN15 at z 720 with drop legs to the stations '
      '(node equipment row, ISO 14644 Class 6 row, 0.03 kW)',
      'A-MACH guard: the hold-down frame pins the registry box so the build '
      'fills the node envelope (X-PAR-04)'],
     "General arrangement, side elevation (end view). Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     ['14 schedule rows of docs-authority/nozzles/WAFER_FAB.csv at tag, face and '
      'bore',
      'Inlets on -Y at z 160: N1 DN15 (N2 purge), N2 DN15 (B/P/As concentrate), '
      'N3 DN15 (colloidal silica slurry), N4 DN25 (fab UPW), N11/N12/N14 DN15 '
      '(the solids transfer rows); outlets on +Y at z 600: N5/N6/N7 DN15, N8 '
      'DN25 (spent UPW), N13 DN15 (spent resist and solvent)',
      'N9 drain flush at the envelope bottom (50 datum); N10 vent flush at the '
      'envelope top (800 datum is the box top)',
      'Atmospheric open-bore tube stubs per duty section 4 (nozzle DN15, no '
      'flange class); the solids rows are non-piped transfers drawn DN15, bore '
      'not calculated (plan W4); the schedule rating column (Class 150) carried '
      'verbatim as text'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("bench01", bench, (0, 1, 0),
     ['Bench deck on the 20 mm plinth inside the four-post hold-down/guard '
       'frame (40 x 40 posts, top rails), AQS-MOD-002 dry service',
      'The frame pins the registry box so the build fills the node envelope '
      '(X-PAR-04); 8 M12 slab anchors (fasteners.csv)',
      'Carbon steel (ASTM A500); the frame is dry structure outside the wetted '
      'hardware'],
     "Fabricated part sheet: bench, plinth and hold-down frame."),
    ("stations01", stations, (1, -1, 1),
     ['Station envelopes per the node equipment list (plan rule 6: purchased '
      'items drawn as envelope and interface, named with the rating from the '
      'node; no invented internals)',
      'CZ puller 0.2317 kW; ingot cool/anneal 0.02 kW; crop/grind/edge tools '
      '0.04 kW; FAB_TOOL dry row (ox, RTA, metal, probe standby) 0.12 kW',
      'Arrangement is the layout choice (WORK_ORDER W12); vendor prints '
      'govern the internals of each purchased station'],
     "Purchased station envelopes (node equipment list)."),
    ("purge01", purge, (1, -1, 1),
     ['N2 purge distribution: DN15 Sch 40 header (x 120..880 at z 720) with '
      'four drop legs to the stations',
      'Node equipment row: N2 purge distribution (ISO 14644 Class 6 row), '
      '0.03 kW connected parasitics named on the node',
      '316L tube per duty section 3 (wet-side material rule applied to the '
      'process hardware)'],
     "Fabricated part sheet: N2 purge distribution."),
    ("aux01", aux, (0, 1, 0),
     ['Connection hardware DN15/DN25 as open-bore tube stubs flush at the '
      'envelope faces; atmospheric per duty section 4 (no flange class)',
      'All 14 schedule rows present at tag, face, height and bore; per-tag '
      'positions in check.nozzles_drawn',
      'The four solids rows are non-piped transfers drawn DN15, bore not '
      'calculated (plan W4)'],
     "Fabricated part sheet: connection hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: reagents, UPW and stock in on -Y, spent streams out '
      'on +Y; drain at the bottom, vent at the top',
      f'Graph revision {R["graph_revision"]} is the model authority for this '
      'build; STEP (export/wafer_fab.step) is the solids of record',
      'Tracker --check green; acceptance A-core + A-MACH + A-SC per '
      'AQS-PLAN-006 section 5'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/wafer_fab.py", f"models/mfg/{unit}/draw_wafer_fab.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ["- Machine per the node equipment list: CZ puller (0.2317 kW), ingot "
     "cool/anneal (0.02 kW), crop/grind/edge tools (0.04 kW), FAB_TOOL dry row "
     "(0.12 kW) as purchased-class station envelopes per plan rule 6; N2 purge "
     "distribution (0.03 kW) as the DN15 header with four drop legs; station "
     "arrangement is the layout choice (W12)",
     "- A-MACH guard: the four-post hold-down frame pins the registry box so the "
     "build fills the envelope (X-PAR-04); 8 slab anchors in fasteners.csv",
     "- Material per duty section 3: 316L where the stream is wet; CA 0 mm "
     "(AQS-STD-001); the node note (ISO 14644-1 Class 7 wet bench, Class 6 tool "
     "row) carried as text"],
    "A-core + A-MACH + A-SC")

"""SOLAR_PV_CELL drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, frame01 (base + hold-down frame),
stations01 (the seven station envelopes), emit01 (quartz tube + fibre annulus),
aux01 (heater/pump envelopes + hardware), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets                                       # noqa: E402

ns = runpy.run_path(HERE / "solar_pv_cell.py")
parts, R = ns["parts"], ns["report"]
unit = "SOLAR_PV_CELL"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


frame = union_all([parts["base"], parts["frame"]])
stations = union_all([parts["stations"], parts["tex_heater"], parts["arc_pump"]])
emit = union_all([parts["quartz_tube"], parts["fibre"]])
aux = parts["nozzles"]
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm envelope - the node size_mm '
      f'({R["size_basis"] or "node size_mm"}, issued envelope X-MFG-38 tool '
      'line); the duty section 2 envelope line agrees with the node',
      'In-house PV cell line per the node design block (X-MFG-38, A-M-178, '
      'AQS-DUTY-071): texture, POCl3 diffusion, PSG etch, PECVD SiNx, screen '
      'print, fast firing, IV - 3 cells per batch, KOH feed from WS_KOH',
      'Seven named stations drawn as envelopes with the node ratings; '
      'arrangement and unstated envelope sizes are the layout choice (W12)',
      'Wetted material per duty section 3: 316L where the stream is wet; the '
      'node station texts name PP tanks - the duty selection governs (plan '
      'rule 5; hold W12)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['PV-EMIT-01 diffusion internally resolved per its node dims: quartz '
      'tube 200 mm x 1.0 m with the 200 mm ceramic-fibre annulus taken at '
      'face value as the fibre thickness',
      'AQS-PV-001 rev C carries the older 50 mm ID x 800 mm tube figure; the '
      'node design 200 mm x 1.0 m governs (hold W12)',
      'Hold-down frame (40 x 40 posts + top rails) pins the registry box so '
      'the build fills the node envelope (X-PAR-04); 8 slab anchors'],
     "General arrangement, side elevation (end view). Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     ['4 schedule rows of docs-authority/nozzles/SOLAR_PV_CELL.csv at tag, '
      'face and bore',
      'N3 (dopant concentrate in) at x 1200 on -Y at z 160; N4 (dopant into '
      'the wafer fab) at x 1260 on +Y at z 600 - both solids transfer rows '
      'drawn DN15, bore not calculated (plan W4)',
      'N1 drain flush at the envelope bottom (50 datum); N2 vent flush at the '
      'envelope top - its 800 datum predates the 1600 box (hold W12)',
      'Atmospheric hose per duty section 4 (bore not calculated)'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("frame01", frame, (0, 1, 0),
     ['Base plate and hold-down/guard frame (40 x 40 posts, top rails), '
       'carbon steel A500 (AQS-MOD-002 dry service)',
       'The frame pins the registry box so the build fills the node envelope '
       '(X-PAR-04); 8 M12 slab anchors (fasteners.csv)',
       'Dry structure outside the wetted 316L baths'],
     "Fabricated part sheet: base plate and hold-down frame."),
    ("stations01", stations, (1, -1, 1),
     ['Station envelopes per the node design tool table (design texts and '
       'peak kW): PV-TEX-01 1.98 kW, PV-EMIT-01 3.79 kW, PV-PSG-01 ambient, '
       'PV-ARC-01 2.25 kW, PV-CON-01 0.7 kW, PV-FIRE-01 3.0 kW, PV-IV-01 '
       '0.1 kW',
       'PV-TEX-01 immersion heater and PV-ARC-01 dry vacuum pump envelopes '
       'are the purchased units per plan rule 6 (ratings from the node / '
       'A-M-178 basis)',
       'Wetted baths 316L per duty section 3 (CA 0 mm, AQS-STD-001); the '
       'node texts name PP - the duty governs (plan rule 5; hold W12)'],
     "Station envelopes (node design tool table)."),
    ("emit01", emit, (1, -1, 1),
     ['Quartz diffusion tube OD 200 x 1000, wall 5 (study - the node gives '
       'OD and length, not wall; hold W12); AQS-PV-001 section 3: tube quartz',
       'Ceramic-fibre insulation annulus 200 mm x 1000 (the node design text '
       "taken at face value); A-M-178 fibre k basis (0.035 + 0.0002 T)",
       'Tube on stands in the PV-EMIT-01 bay, x 480..1480; diffusion basis '
       'A-M-178: 20 kg heated mass to 850 C in 1.5 h'],
     "Fabricated part sheet: PV-EMIT-01 diffusion internals."),
    ("aux01", aux, (0, 1, 0),
     ['Connection hardware DN15 tube stubs flush at the envelope faces; '
      'atmospheric hose per duty section 4 (bore not calculated)',
      'All 4 schedule rows present at tag, face, height and bore; per-tag '
      'notes in check.nozzles_drawn',
      'The schedule rating column (Class 150) carried verbatim as text'],
     "Fabricated part sheet: connection hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: the tool line runs x 60..2340 in two rows on the '
      'deck; the diffusion tube runs the length of the EMIT bay',
      f'Graph revision {R["graph_revision"]} is the model authority for this '
      'build; STEP (export/solar_pv_cell.step) is the solids of record',
      'Tracker --check green; acceptance A-core + A-MACH + A-SC per '
      'AQS-PLAN-006 section 5'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/solar_pv_cell.py", f"models/mfg/{unit}/draw_solar_pv_cell.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ["- In-house PV cell line per the node design block (X-MFG-38, A-M-178, "
     "AQS-DUTY-071): seven named stations drawn as envelopes with the node "
     "ratings; PV-EMIT-01 internally resolved per its node dims (quartz tube "
     "200 x 1000 with the 200 mm ceramic-fibre annulus at face value)",
     "- Wetted material per duty section 3: 316L where the stream is wet; the "
     "node station texts name PP tanks - the duty selection governs (plan "
     "rule 5; hold W12); tube quartz and screen stainless shop-cut per "
     "AQS-PV-001 section 3",
     "- Hold-down frame pins the registry box so the build fills the envelope "
     "(X-PAR-04); anchors in fasteners.csv"],
    "A-core + A-MACH + A-SC")

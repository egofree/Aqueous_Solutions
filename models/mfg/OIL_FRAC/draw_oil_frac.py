"""OIL_FRAC drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, col01 (column shell + heads + skirt),
frame01 (hold-down frame + plinth), aux01 (connection hardware), iso01. The set
replaces the stale envelope-era sheets of the Oct-31-era M2 build.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets                                       # noqa: E402

ns = runpy.run_path(HERE / "oil_frac.py")
parts, R = ns["parts"], ns["report"]
unit = "OIL_FRAC"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


col = parts["column"]
frame = union_all([parts["plinth"], parts["frame"]])
aux = parts["nozzles"]
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
C = R["column"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm envelope - the node size_mm ({R["size_basis"]})',
      'Vertical carbon-steel fractionator column drawn to the node envelope: shell '
      'OD 480 (the duty states no diameter - drawn to the envelope, hold W12), '
      'wall 6 (study, hold W12), top and bottom heads on a skirt seat',
      'Four-post hold-down frame pins the registry box so the build fills the '
      'envelope (X-PAR-04)',
      'Carbon steel (duty section 3), CA 1.5 mm (AQS-STD-001 hydrocarbon rule)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     [f'A-COL sump report: the duty section 2 sump {C["sump_duty_m3"]:g} m3 (30 min) '
      'stands in the modeled bore as the bottom-head zone - reported, nothing '
      'resized (plan rule 3)',
      'The node internals row is none: no packing, distributor or demister is '
      'drawn; stages and HTU are not stated anywhere and stay a named hold (A-COL, '
      'W12); the cut split rides the node cut_basis pass fractions (A-M-138, '
      'SU2018_PYRO) - a flowsheet allocation, not tray design',
      'Duty basis: pyrolysis oil in, four fractionator cuts out (CUT-1..CUT-4), NCG '
      'to the header, light cuts to POLY_OLEFIN'],
     "General arrangement, side elevation (end view). Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     ['14 schedule rows of docs-authority/nozzles/OIL_FRAC.csv at tag, face and '
      'bore - the issued schedule replaces the style-builders study layout',
      'Inlets N1-N4, N12, N14 on -Y at z 160 (N14 solids row drawn DN15 bore not '
      'calculated per plan W4); outlets N5-N8 (the four CUT lines), N11 (NCG to '
      'the header) and N13 (light cuts to POLY_OLEFIN) on +Y at z 600',
      'N9 drain flush at the envelope bottom (50 datum); N10 vent flush at the '
      'envelope top (800 datum is the box top)',
      'Atmospheric open-bore tube stubs per duty section 4 (nozzle DN15, no flange '
      'class); the schedule rating column (Class 150) carried verbatim as text'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("col01", col, (0, 1, 0),
     [f'Column shell OD {C["od_mm"]:g} x wall {C["wall_mm"]:g} (study), z '
      f'{C["z_mm"][0]:g}..{C["z_mm"][1]:g}, with 8 mm heads and a skirt seat to '
      'the plinth',
      'Shell drawn to the node envelope; no column diameter or wall is stated on '
      'the node or duty (holds, W12)',
      'CA 1.5 mm (AQS-STD-001 hydrocarbon rule); welds per the unit route (F-COL)'],
     "Fabricated part sheet: column shell."),
    ("frame01", frame, (0, 1, 0),
     ['Four-post hold-down frame (40 x 40 posts, top rails) + plinth '
      f'{L:g} x {W:g} x 20 (AQS-MOD-002 dry service)',
      'The frame pins the registry box so the build fills the node envelope '
      '(X-PAR-04); 8 M12 slab anchors (fasteners.csv)',
      'Close-out note: this build replaces the Oct-31-era style-builders study '
      'export; WORK_ORDER W1-W12, make-or-buy BOM, fasteners, check record and '
      'the duty section 7 pointer are beside the model'],
     "Fabricated part sheet: hold-down frame + plinth."),
    ("aux01", aux, (0, 1, 0),
     ['Connection hardware DN15/DN25 as open-bore tube stubs flush at the envelope '
      'faces; atmospheric per duty section 4 (no flange class)',
      'All 14 schedule rows present at tag, face, height and bore; per-tag '
      'positions in check.nozzles_drawn',
      'The N14 solids row (spent resist and solvent from the fab) is a non-piped '
      'transfer: drawn DN15, bore not calculated (plan W4)'],
     "Fabricated part sheet: connection hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: pyrolysis oil and waste streams in on -Y, the four cuts '
      'and NCG out on +Y; drain at the bottom, vent at the top',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/oil_frac.step) is the solids of record',
      'Tracker --check green; acceptance A-core + A-COL per AQS-PLAN-006 '
      'section 5'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/oil_frac.py", f"models/mfg/{unit}/draw_oil_frac.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ["- M2 close-out per the HX8 close pattern: the style-builders column study "
     "verified through the current shared lib (unit-dir builder, 14-row issued "
     "schedule, tracker W2, section 5 artifacts completed); the stale "
     "envelope-era drawing set and GA.md superseded",
     "- A-COL: no packing, distributor or demister is named on the node, so none "
     "is drawn (internals none); stages and HTU are not stated anywhere and stay "
     "a named hold (W12); the cut split rides the node cut_basis fractions "
     "(A-M-138, SU2018_PYRO) - a flowsheet allocation, not tray design",
     "- Sump report: the duty section 2 sump 0.0006 m3 (30 min) stands 3.5 mm "
     "deep in the modeled bore - the sump zone is the bottom head; reported, "
     "nothing resized (plan rule 3)",
     "- The shell is drawn to the node envelope (OD 480, wall 6 study): the duty "
     "states no diameter and no wall (holds, W12); a four-post hold-down frame "
     "pins the registry box (X-PAR-04)"],
    "A-core + A-COL")

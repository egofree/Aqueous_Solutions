"""GLASS_DIGEST drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, sh01 (shell + lid + legs), in01
(agitator + coil), aux01 (connection hardware), iso01. The set replaces the
stale envelope-era sheets of the Oct-31-era M2 build.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets, step_export  # noqa: E402

ns = runpy.run_path(HERE / "glass_digest.py")
parts, R = ns["parts"], ns["report"]
unit = "GLASS_DIGEST"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


shell = union_all([parts["legs"], parts["shell"], parts["lid"]])
internals = union_all([parts["agitator"], parts["motor"], parts["coil"]])
aux = parts["nozzles"]
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
V = R["vessel"]
X = R["nozzles_drawn"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm envelope - the node size_mm ({R["size_basis"]})',
      'CPVC digestor per the X-MFG-31 design: OD 400 shell, wall 4, H 400, on 4 '
      'legs 150; bolted lid flange OD 460; top-entry agitator with 0.09 kW '
      'gearmotor envelope; Q3 PVDF DN15 coil (3 tube rings R 155)',
      f'A-VES report: model shell volume {V["v_shell_model_l"]:g} L against the node '
      f'design V_L {V["v_L_node_l"]:g} L; no new residence time derived',
      'Duty section 3 names 316L, the node design names CPVC - conflict carried as '
      'a hold (W12), nothing resized'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Shell z 150..550; lid 550..566; agitator shaft to the PBT blade at z 300; '
      'vent riser flush at the envelope top (the 800 datum is the schedule '
      'placeholder)',
      'Agitator per the node design block: D133 impeller, 358 rpm, shaft_W 14.79 W, '
      'motor_kW 0.09 (purchased envelope per plan rule 6)',
      'PVDF impeller and shaft sleeve per design.material; the coil per the design '
      'heat row (graph HL-Q3-A/B-HX6)'],
     "General arrangement, side elevation (end view). Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     ['12 schedule rows of docs-authority/nozzles/GLASS_DIGEST.csv at tag, face and '
      'bore - the issued schedule replaces the 5-row study layout of the Oct-31-era '
      'M2 build',
      'Inlets N1-N4, N12 on -Y; outlets N5-N8, N11 on +Y; the placeholder datums '
      '(160/600) draw clamped into the shell span [175, 525] (holds, W12)',
      'N9 drain boss flush at the envelope bottom; N10 vent riser on the lid flush '
      'at the envelope top; the N4 row quoting repaired (digest NaOH, 20 wt %)',
      'Atmospheric open-bore tube connections per duty section 4; the N11 solids '
      'row drawn DN15, bore not calculated (plan W4)'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("sh01", shell, (0, 1, 0),
     ['Shell OD 400 x wall 4 x H 400, CPVC to 93 C (DVS 2205 allowable 3.0 MPa at '
      '85 C), base head, lid flange ring OD 460 x 16 with 12-bolt circle',
      '4 CPVC legs 40 x 40 x 150 (layout choice carried from the issued '
      'construction - the node names no support, hold W12)',
      'CA 0 mm (AQS-STD-001 polymer rule); extrusion welds per DVS 2207-3 (route '
      'in WORK_ORDER W10)'],
     "Fabricated part sheet: shell + lid + legs."),
    ("in01", internals, (0, 1, 0),
     ['Agitator: shaft D24 with 4-blade 45 deg PBT D133 (PVDF per design.material) '
      'at 358 rpm; 0.09 kW gearmotor shown as its purchased envelope (plan rule 6)',
      'Q3 coil: PVDF DN15, 3 tube rings R 155 at 33 mm pitch per the design heat '
      'row (graph HL-Q3-A/B-HX6); the schedule N1/N2 service text says jacket - '
      'carried verbatim, the coil is the issued construction (hold, W12)',
      'The node internals row is none: the tracker records no internal solid; the '
      'agitator and coil are node-design machine features, drawn as solids'],
     "Fabricated part sheet: agitator + gearmotor envelope + Q3 coil."),
    ("aux01", aux, (0, 1, 0),
     ['Connection hardware DN15/DN25 as open-bore tube connections from the shell '
      'to the envelope faces; atmospheric per duty section 4; the schedule rating '
      'column (Class 150) is carried verbatim as text (no flange drawn - no '
      'process pressure stated)',
      'All 12 schedule rows present at tag, face, height and bore; clamped datums '
      'and per-tag positions in check.nozzles_drawn',
      'Close-out note: this build replaces the Oct-31-era M2 study export; '
      'WORK_ORDER W1-W12, make-or-buy BOM, fasteners, check record and the duty '
      'section 7 pointer are beside the model'],
     "Fabricated part sheet: connection hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: burned cullet and NaOH in on -Y, stock and liquors out on '
      '+Y; drain at the bottom, vent riser at the top',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/glass_digest.step) is the solids of record',
      'Tracker --check green; acceptance A-core + A-VES per AQS-PLAN-006 section 5'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/glass_digest.py", f"models/mfg/{unit}/draw_glass_digest.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ["- M2 close-out per the HX8 close pattern: the Oct-31-era reactors.py study "
     "build verified through the current shared lib (unit-dir builder, 12-row "
     "issued schedule, tracker W2, section 5 artifacts completed); the stale "
     "envelope-era drawing set and GA.md superseded",
     "- A-VES: model shell volume 48.3 L against the node design V_L 49.9724 L "
     "(V_work 37.4793 L, tau 22.5014 h at 85 C); reported, no residence claim "
     "added",
     "- Schedule N4 row repaired to the schedule quoting (unquoted comma in "
     "'digest NaOH, 20 wt%' shifted face and height); change record in "
     "notes/glass_oilgas_m3_2026-11-02.md"],
    "A-core + A-VES")

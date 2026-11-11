"""MET_SYN drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, column01 (reactor column + jacket +
stirrer), tanks01 (feed tanks + pumps), hood01 (bench + hood + frame), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets, step_export  # noqa: E402

ns = runpy.run_path(HERE / "met_syn.py")
parts, R = ns["parts"], ns["report"]
unit = "MET_SYN"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


column = union_all([parts["column"], parts["glass_liner"], parts["jacket"], parts["stirrer"]])
tanks = union_all([parts["feed_tanks"], parts["metering_pumps"], parts["ptfe_lines"],
                   parts["crystalliser"]])
aux = union_all([parts["plinth"], parts["deck"], parts["frame"], parts["hood"]])
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
M = R["machine"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm envelope - the node size_mm ({R["size_basis"]})',
      'Bench fume-hood synthesis train per the node sizing/design blocks and duty '
      'section 3: borosilicate glass-lined reactor column (2 L working volume), 3 '
      'SS304 reagent feed tanks, Hastelloy C crystalliser, PTFE-lined transfer lines',
      'Connected set 0.2 kW (node): heating jacket + stirrer + metering pumps; '
      'purchased-class envelopes per plan rule 6, no per-item figure invented',
      'Four-post hold-down/guard frame pins the registry box (X-PAR-04); 8 slab '
      'anchors in fasteners.csv'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Bench deck at z 800 over the 20 mm plinth; fume-hood shell over the bench '
      'z 820..1800 (wet-bench class under HCN/acrolein fume; layout choice, W12)',
      'Reactor column x 400 y 500; feed-tank row x 700 at y 300/550/800; '
      'crystalliser x 1150 y 500 - the arrangement is the layout choice (W12)',
      'Chemistry (node design block): step 1 CH3OH + H2S -> CH3SH (K2O/Al2O3, '
      '350 C); step 2 MMP addition; step 3 Strecker to DL-Met - three steps in '
      'campaign sequence through the one column'],
     "General arrangement, side elevation (end view). Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     ['6 schedule rows of docs-authority/nozzles/MET_SYN.csv at tag, face and bore',
      'N1 methanol feed, N2 H2S feed, N3 ammonia feed on -Y at z 160 (under the '
      'bench deck, where the metering pumps sit)',
      'N4 DL-Met crystals out (solids service) on +Y at z 600 at the crystalliser '
      'discharge, drawn DN15 bore not calculated (plan W4)',
      'N5 drain flush at the envelope bottom (50 datum); N6 vent flush at the '
      'envelope top - the 800 datum predates the 1800 box (hold, W12); atmospheric '
      'tube per duty section 4, no flange (W4 110 % rule)'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("column01", column, (0, 1, 0),
     ['Glass-lined reactor column OD 150 x 600 with borosilicate lining, '
      'base/top heads and heating-jacket band OD 190 x 300 (2 L working volume, '
      'node sizing; shell dimensions study, W12)',
      'Stirrer drive on the column head as a purchased-class envelope (connected '
      'set 0.2 kW from the node)',
      'CA 0 mm (AQS-STD-001); duty section 3 alternative: tantalum reactor if the '
      'HCN service shows corrosion at lining pinholes (not drawn, X-MAT-22)'],
     "Fabricated part sheet: reactor column + jacket + stirrer."),
    ("tanks01", tanks, (0, 1, 0),
     ['Reagent feed tanks OD 200 x 300, 3 off, SS304 per duty section 3 (CH3OH / '
      'H2S / NH3 per the schedule feeds)',
      'Metering pumps as purchased-class envelopes on the tank bases; PTFE-lined '
      'transfer lines: column-to-crystalliser run, pump risers, crystalliser vent stub',
      'Hastelloy C crystalliser OD 220 x 350 (duty section 3: the product-quality '
      'bottleneck, X-UI-002) - buy-row envelope, maker TDS mass governs'],
     "Fabricated part sheet: feed tanks + pumps + lines + crystalliser."),
    ("hood01", aux, (0, 1, 0),
     ['Bench deck, plinth and four-post hold-down frame (40 x 40 posts, top rails)',
      'Fume-hood shell: back/side walls and top over the bench, 316L wet-bench '
      'class (HCN/acrolein fume; REE_RECOVER idiom; layout choice, W12)',
      'All 6 schedule rows present at tag, face, height and bore (check.nozzles_drawn)'],
     "Fabricated part sheet: bench + hood + frame."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: reagent feeds in on -Y, DL-Met crystals out on +Y at the '
      'crystalliser discharge; drain and vent on the skid centreline',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/met_syn.step) is the solids of record',
      'Tracker --check green; acceptance A-core per AQS-PLAN-006 section 5 '
      '(route hold: chemical_synthesis has no section 4 class)'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/met_syn.py", f"models/mfg/{unit}/draw_met_syn.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ["- Bench fume-hood synthesis train per the node sizing/design blocks and duty "
     "section 3: borosilicate glass-lined reactor column (2 L working volume), 3 "
     "SS304 feed tanks, Hastelloy C crystalliser, PTFE-lined transfer lines",
     "- Connected set 0.2 kW (node: jacket + stirrer + metering pumps) drawn as "
     "purchased-class envelopes per plan rule 6; A-MACH practice: hold-down frame "
     "and 8 anchors; purchased items named with the node rating",
     "- Route hold carried by name: chemical_synthesis has no AQS-PLAN-006 section "
     "4 class; shell dimensions are study values (holds, WORK_ORDER W12)"],
    "A-core")

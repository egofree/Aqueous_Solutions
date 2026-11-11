"""WIRE_DRAW drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, dies01 (die stand + die set + fume
hood), block01 (bull block + shaft + guides), aux01 (frame + bench + drive +
cabinet), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets, step_export  # noqa: E402

ns = runpy.run_path(HERE / "wire_draw.py")
parts, R = ns["parts"], ns["report"]
unit = "WIRE_DRAW"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


dies = union_all([parts["die_stand"], parts["die_set"], parts["fume_hood"]])
block = union_all([parts["bull_block"], parts["block_shaft"], parts["wire_guides"]])
aux = union_all([parts["plinth"], parts["frame"], parts["bench_bed"],
                 parts["drive_group"], parts["control_cabinet"]])
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
M = R["machine"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm envelope - the node size_mm ({R["size_basis"]}); '
      'the build fills it exactly (hold-down frame + vent riser pin the box)',
      'Bull-block wire drawer per the AQS-MFG-010 tool row (Table 2.1, rev C '
      'metering split): nameplate 1.1 kW, energy basis 250 MPa x strain 3.0 / 0.55 '
      '(DIETER1988) + no-load 15 % x 1 h (A-M-177)',
      'The DRAW accepted idiom (commit 30f5abf4) scaled to the node box: bench '
      'bed x 100..700, die stand -X with the carbide die set, bull-block drum '
      'OD 300 at +X z 600, fume hood over the die zone',
      'A-MACH: die-zone/drum guard rail + hold-down frame + 8 slab anchors'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Bench centreline y 300; die stand on the -X head, bull block on the +X '
      'head with the drive bay behind it; control cabinet on the -X floor',
      'Duty: 6.839 kg/d billet in (S57), 3.939 kg/d wire out (S58), 0.44 kg/d '
      'draw scrap and 2.46 kg/d draw fume (the fume row routes to the house '
      'scrubber train)',
      'Drum and bench dimensions are study values (hold, WORK_ORDER W12); the '
      'capstan hardware carries the machine lubricant programme - no wetted stream'],
     "General arrangement, side elevation (end view). Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     ['7 schedule rows of docs-authority/nozzles/WIRE_DRAW.csv at tag, face and bore',
      'N1 billet in and N7 rod/wire stock in (solids service, drawn DN15 bore not '
      'calculated, plan W4) on -Y at z 160',
      'N2 wire product out, N3 draw scrap out and N4 draw fume out on +Y at z 600',
      'N5 drain flush at the envelope bottom (50 datum); N6 vent flush at the '
      'envelope top (800 datum = box top); atmospheric tube per duty section 4'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("dies01", dies, (0, 1, 0),
     ['Die stand on the bench head with the tungsten-carbide die set in '
      'tool-steel casings (consumable buy set; die count is a study value, '
      'hold, WORK_ORDER W12)',
      'Draw-fume extraction hood over the die zone: the N4 row routes to the '
      'house scrubber train; the hood placement is the layout choice (W12)',
      'DIETER1988 ch. 20/21 die class; CA 0 mm (AQS-STD-001)'],
     "Fabricated part sheet: die stand + die set + fume hood."),
    ("block01", block, (0, 1, 0),
     [f'Bull-block take-up drum OD {M["bull_block"]["od_mm"]:g} with shaft and '
      'wire-guide sheaves',
      'Drum size is the study value (hold, WORK_ORDER W12); the capstan hardware '
      'carries the machine lubricant programme - no wetted stream (duty section 3)',
      'Take-off at z 600 over the N2/N3/N4 out rows'],
     "Fabricated part sheet: bull block + shaft + guides."),
    ("aux01", aux, (0, 1, 0),
     [f'Four-post hold-down/guard frame pinning the {L:g} x {W:g} x {H:g} envelope '
      '(40 x 40 posts, top rails); die-zone and drum guard rail, 4 posts x 3 tiers',
      'Bench bed on 4 legs (DRAW bench idiom scaled to the node box); study '
      'sections (hold, WORK_ORDER W12)',
      'Drive group and control cabinet as purchased envelopes (nameplate 1.1 kW, '
      'node stamp; plan rule 6); cabinet mass a table-density placeholder until '
      'the maker TDS quotes (hold, W12)'],
     "Fabricated part sheet: frame + bench + drive + cabinet."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: billet/stock in on -Y, wire/scrap/fume out on +Y; die '
      'stand -X, bull block +X',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/wire_draw.step) is the solids of record',
      'Tracker --check green; acceptance A-core + A-MACH + A-SC per AQS-PLAN-006 '
      'section 5 (route F-MACH)'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/wire_draw.py", f"models/mfg/{unit}/draw_wire_draw.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ["- Bull-block wire drawer per the AQS-MFG-010 tool row (nameplate 1.1 kW; "
     "A-M-177 strain-3.0 energy basis), built on the DRAW accepted idiom (commit "
     "30f5abf4) scaled to the node box: bench bed, die stand with the carbide "
     "die set (buy consumable), bull-block drum OD 300, wire guides, fume hood "
     "over the die zone (N4 to the house scrubber train)",
     "- A-MACH: die-zone/drum guard rail + hold-down frame + 8 anchors; purchased "
     "items named with the node ratings (drive group and cabinet, plan rule 6); "
     "A-SC: shop-made hardware flagged with the AQS-BOM-SC-001 cross-reference",
     "- Dry forming machine (no wetted stream); CA 0 mm; drum/bench/die-count "
     "study values (holds, WORK_ORDER W12)"],
    "A-core + A-MACH + A-SC")

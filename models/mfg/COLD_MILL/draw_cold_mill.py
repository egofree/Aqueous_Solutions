"""COLD_MILL drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, housing01 (bedplate + housings + crown),
rolls01 (work rolls + journals + screw-downs), aux01 (frame + tables + guard +
cabinet), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets                                       # noqa: E402

ns = runpy.run_path(HERE / "cold_mill.py")
parts, R = ns["parts"], ns["report"]
unit = "COLD_MILL"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


housing = union_all([parts["bedplate"], parts["housings"], parts["crown"]])
rolls = union_all([parts["roll_lower"], parts["roll_upper"], parts["journals"],
                   parts["screw_downs"], parts["strip_tables"]])
aux = union_all([parts["plinth"], parts["frame"], parts["guard_rail"],
                 parts["gearbox"], parts["drive_motor"], parts["control_cabinet"]])
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
M = R["machine"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm envelope - the node size_mm ({R["size_basis"]}); '
      'the build fills it exactly (hold-down frame pins the box)',
      'Two-high cold rolling mill per the AQS-MFG-010 tool row (Table 2.1, rev C '
      'metering split): nameplate 2.2 kW, energy basis 250 MPa x strain 2.3 / 0.55 '
      '(DIETER1988) + no-load 15 % x 1 h (A-M-177)',
      'Work rolls OD 120 x 300 with the 5 mm strip gap; strip runs along y through '
      'the pass line z 302.5; drive train -X, control cabinet x 700..960',
      'A-MACH: hold-down frame + roll-zone guard rail + 8 slab anchors'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Housings x 230/530 on the bedplate, crown tie z 620..660, screw-downs to '
      'z 700; strip tables on the pass line both sides of the roll gap',
      'Roll centres z 240/365 (5 mm gap at the strip class) - study values '
      '(hold, WORK_ORDER W12)',
      'Duty: 3.95 kg/d strand in (IA-MELT-MILL), 3.95 kg/d sheet/strip out (S59); '
      'dry forming machine, no wetted stream on the graph'],
     "General arrangement, side elevation (end view). Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     ['4 schedule rows of docs-authority/nozzles/COLD_MILL.csv at tag, face and bore',
      'N1 strand in on -Y at z 160; N2 sheet/strip out on +Y at z 600 (schedule '
      'datum is a placeholder above the pass line - hold, W12)',
      'N3 drain flush at the envelope bottom (50 datum); N4 vent flush at the '
      'envelope top (800 datum = box top)',
      'Atmospheric tube per duty section 4, no flange (W4 110 % rule)'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("housing01", housing, (0, 1, 0),
     ['Mill bedplate 520 x 480 and two vertical housings 40 x 360 with crown tie '
      '(two-high housing idiom)',
      'Housing sections are study values sized to the strip class (hold, '
      'WORK_ORDER W12); CA 0 mm (AQS-STD-001)',
      'Frame A500 per AQS-MOD-002 dry service; anchors in fasteners.csv'],
     "Fabricated part sheet: bedplate + housings + crown."),
    ("rolls01", rolls, (0, 1, 0),
     ['Work rolls OD 120 x 300, 2 off (upper/lower, 5 mm gap), tool steel '
      '(AR400/D2 class, lib table); journals OD 40 outboard of the housings '
      '(shop lathe)',
      'Screw-down studs on the crown over the upper journal stations; layout '
      'choice (W12)',
      'Entry/exit strip tables on the pass line z 302.5 - the physical exit; the '
      'N2 schedule datum z 600 is a placeholder (hold, W12)'],
     "Fabricated part sheet: rolls + journals + screw-downs + tables."),
    ("aux01", aux, (0, 1, 0),
     [f'Four-post hold-down/guard frame pinning the {L:g} x {W:g} x {H:g} envelope '
      '(40 x 40 posts, top rails); roll-zone guard rail, 4 posts x 3 tiers',
      'Drive gearbox + motor as a purchased envelope (2.2 kW nameplate, '
      'AQS-MFG-010 Table 2.1; node stamp) - purchased per plan rule 6',
      'Control cabinet as a purchased envelope; mass a table-density placeholder '
      'until the maker TDS quotes (hold, W12)'],
     "Fabricated part sheet: frame + guard + drive + cabinet."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: strand in on -Y, sheet/strip out on +Y through the roll '
      'gap; drive train -X, cabinet +X',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/cold_mill.step) is the solids of record',
      'Tracker --check green; acceptance A-core + A-MACH + A-SC per AQS-PLAN-006 '
      'section 5 (route F-MACH)'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/cold_mill.py", f"models/mfg/{unit}/draw_cold_mill.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ["- Two-high cold rolling mill per the AQS-MFG-010 tool row (nameplate 2.2 "
     "kW; A-M-177 energy basis): bedplate, housings 40 x 360 with crown tie, "
     "work rolls OD 120 x 300 (5 mm gap) with outboard journals, screw-downs, "
     "strip tables on the pass line z 302.5",
     "- A-MACH: hold-down frame + roll-zone guard rail + 8 anchors; purchased "
     "items named with the node ratings (2.2 kW drive set, control cabinet, plan "
     "rule 6); A-SC: shop-made hardware flagged with the AQS-BOM-SC-001 "
     "cross-reference",
     "- Dry forming machine (no wetted stream on the graph); CA 0 mm; housing/"
     "roll dimensions are study values (holds, WORK_ORDER W12)"],
    "A-core + A-MACH + A-SC")

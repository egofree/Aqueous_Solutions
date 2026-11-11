"""MFG_SHOP drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, stations01 (the six machine envelopes),
bench01 (bench + frame + shop-air header), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets, step_export  # noqa: E402

ns = runpy.run_path(HERE / "mfg_shop.py")
parts, R = ns["parts"], ns["report"]
unit = "MFG_SHOP"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


stations = union_all([parts["stations"]])
bench = union_all([parts["plinth"], parts["deck"], parts["frame"], parts["shop_air"]])
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
M = R["machine"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm envelope - the node size_mm ({R["size_basis"]}); '
      'the build fills it exactly (hold-down frame pins the box)',
      'Machine-shop fitout per the node continuous note authority (AQS-MFG-010 '
      'rev C, Table 2.1): six shop machine tools as purchased-class envelopes per '
      'plan rule 6 - CNC vertical mill 7.5 kW, engine lathe 5.5 kW, band saw '
      '1.5 kW, rotary-screw air compressor 4.0 kW, TIG/MIG welder 6.0 kW, bench '
      'set 2.0 kW; connected 26.5 kW, one 8 h shift, average 2.55 kW',
      'The four metal-forming tools (melt, atomiser, mill, drawer) are metered at '
      'their own units since the rev C split - not part of this fitout',
      'A-MACH: hold-down/guard frame + 8 slab anchors; shop-air DN15 header with '
      'four drop legs'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Station envelopes on the bench deck (y 100..420), heights graded 200..520; '
      'station arrangement is the layout choice (W12)',
      'Shop-air header at y 470, z 720 with drop legs at x 150/340/520/700 '
      '(compressor service)',
      'MCC-1 framing: the connected load frames the feeder with the roster '
      '(AQS-MFG-010 section 3); coincident peak 24.5 kW'],
     "General arrangement, side elevation (end view). Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     ['33 schedule rows of docs-authority/nozzles/MFG_SHOP.csv at tag, face and bore',
      'Stock rows on -Y at z 160: DN25 metals/Si and glass/ceramic stock, DN15 '
      'cuts and issues, and the 19 solids rows (goods, scrap returns, plated '
      'sheet) drawn DN15 bore not calculated (plan W4)',
      'Out rows on +Y at z 600: scrap, metal scrap, goods in service (the DN50 '
      'row), shop scrap, manufacturing scrap return, textiles',
      'N9 drain flush at the envelope bottom (50 datum); N10 vent flush at the '
      'envelope top (800 datum = box top); atmospheric tube per duty section 4'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("stations01", stations, (0, 1, 0),
     ['Six machine station envelopes per AQS-MFG-010 Table 2.1 (nameplates on '
      'each station in check.machine.stations)',
      'Purchased per plan rule 6: envelope + interface, no invented internals; '
      'machine footprints are study values - the maker prints govern at order '
      '(hold, WORK_ORDER W12)',
      'Station masses are study envelopes at carbon-steel density apportioned by '
      'envelope volume; maker prints quote at order'],
     "Fabricated part sheet: the six machine station envelopes."),
    ("bench01", bench, (0, 1, 0),
     ['Bench deck over the plinth inside the four-post hold-down/'
      'guard frame (40 x 40 posts, top rails) pinning the registry box (X-PAR-04)',
      'Shop-air DN15 header with four drop legs (compressor service, AQS-MFG-010 '
      'air compressor row 4.0 kW)',
      '8 slab anchors in fasteners.csv; 12 machine hold-down bolts, 2 per station'],
     "Fabricated part sheet: bench + frame + shop-air header."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: stock in on -Y, goods/scrap out on +Y; the shop-air '
      'header runs the bench length',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/mfg_shop.step) is the solids of record',
      'Tracker --check green; acceptance A-core + A-MACH + A-SC per AQS-PLAN-006 '
      'section 5 (route F-MACH); the shop that makes the AQS-BOM-SC-001 make rows'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/mfg_shop.py", f"models/mfg/{unit}/draw_mfg_shop.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ["- Machine-shop fitout per AQS-MFG-010 rev C Table 2.1: six shop machine "
     "tools as purchased-class envelopes (CNC mill 7.5, lathe 5.5, band saw 1.5, "
     "compressor 4.0, welder 6.0, bench set 2.0 kW; connected 26.5 kW, average "
     "2.55 kW); shop-air DN15 header with four drops",
     "- A-MACH: hold-down/guard frame + 8 anchors; purchased items named with the "
     "tool-row nameplates (plan rule 6); A-SC: bench, frame, header and "
     "connections flagged with the AQS-BOM-SC-001 cross-reference - this is the "
     "shop that makes the plant's AQS-BOM-SC-001 make rows",
     "- The four metal-forming tools are metered at their own units (rev C "
     "split); the 19 solids rows are drawn DN15 bore not calculated (W4); machine "
     "footprints are study values (holds, WORK_ORDER W12)"],
    "A-core + A-MACH + A-SC")

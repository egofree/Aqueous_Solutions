"""GEO_GHEX drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, skid01 (headers + stubs + fill pot),
loop01 (the A-HX loop-area report sheet), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets                                       # noqa: E402

ns = runpy.run_path(HERE / "geo_ghex.py")
parts, R = ns["parts"], ns["report"]
unit = "GEO_GHEX"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


skid = union_all([parts["headers"], parts["bore_stubs"], parts["fill_pot"]])
aux = union_all([parts["plinth"], parts["frame"], parts["pump_env"]])
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
M = R["machine"]
BF = M["bore_field"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm envelope - the node size_mm (the study '
      'registry box; the seed 1200 x 800 x 800 "bore field tie, massing only" '
      'figure predates it - the node governs, hold W12)',
      'Ground heat exchanger manifold skid per the node design block '
      '(design_survey_locked, ST-ORC-01): DN32 HDPE flow/return header runs, '
      'two bore-pair tie-in stubs to below grade, the circulation-pump envelope '
      '(125.7 W, node) and the glycol fill pot',
      f'Bore field (node facts): {BF["bores"]} bores x {BF["depth_m"]:g} m at '
      f'{BF["spacing_m"]:g} m spacing, {BF["metres_installed"]:g} m installed - '
      'drilled subsurface works (site/well lane); the stubs are the interface '
      'indication',
      'A-MACH practice: hold-down/guard frame + 8 slab anchors'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Header runs x 120..700 at z 300/360 on the skid centreline +/- 80; bore '
      'stubs to the box floor at x 200 and 800; pump envelope x 720..940',
      f'Loop: {M["loop"]["fluid"]}, flow {M["loop"]["flow_kg_s"]:g} kg/s, dT '
      f'{M["loop"]["dT_K"]:g} K, DN32 HDPE DR-11 (node design)',
      f'Class figures (survey-locked): q_per_m {M["loop"]["q_per_m_W"]:g} W/m, '
      f'Q_ceiling {M["loop"]["Q_ceiling_kW_th"]:g} kW th, T_source '
      f'{M["loop"]["T_source_K"]:g} K, k_ground {M["loop"]["k_ground_W_mK"]:g} '
      'W/(m K) - the duty states no mass throughput'],
     "General arrangement, side elevation (end view). Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     ['3 schedule rows of docs-authority/nozzles/GEO_GHEX.csv at tag, face and bore',
      'N3 geothermal loop fluid out on +Y at z 600 - the loop tie to GEO_HP '
      '(the S43 class edge)',
      'N1 drain flush at the envelope bottom (50 datum); N2 vent flush at the '
      'envelope top (800 datum = box top)',
      'Atmospheric hose barbs (rows read "Bore not calculated. Rating hose, '
      'atmospheric"); no flange (W4 110 % rule)'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("skid01", skid, (0, 1, 0),
     ['DN32 HDPE flow/return header runs on the skid with the glycol fill pot '
      '(OD 140 x 220, study - hold W12)',
      'Bore-pair tie-in stubs to below grade at x 200 and 800: interface '
      'indication - the boreholes continue to the 45 m node depth at the 6 m '
      'node spacing (drilled works, hold W12)',
      'HDPE DR-11 per the node material row; header stations are study values'],
     "Fabricated part sheet: headers + stubs + fill pot."),
    ("loop01", aux, (0, 1, 0),
     [f'A-HX loop-area report: {M["a_hx_area"]["loop_m"]:g} m of DN32 (OD 42.4) '
      f'= {M["a_hx_area"]["area_m2"]:g} m2 wetted loop area, from the model skid '
      'plus the node-quoted buried run (2 bores x 2 legs x 45 m + 6 m header)',
      'NOT called a calculated duty: the duty sheet states no mass throughput; '
      'q_per_m 35 W/m and Q_ceiling 3.0 kW th are the node survey-locked class '
      'figures',
      'Circulation pump envelope (125.7 W, node design circ_pump_W) - purchased '
      'per plan rule 6; mass a table-density placeholder (hold W12)'],
     "Fabricated part sheet: pump envelope + A-HX loop-area report."),
    ("iso01", full, (1, -1, 1),
     ['Plant orientation: the loop tie out on +Y to GEO_HP (S43 class edge); '
      'the bore stubs run to the box floor and below grade',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/geo_ghex.step) is the solids of record',
      'Tracker --check green; acceptance A-core + A-HX per AQS-PLAN-006 '
      'section 5 (route F-HX)'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/geo_ghex.py", f"models/mfg/{unit}/draw_geo_ghex.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ["- Ground heat exchanger manifold skid per the node design block "
     "(design_survey_locked, ST-ORC-01): DN32 HDPE flow/return headers, two "
     "bore-pair tie-in stubs to below grade (interface indication), pump "
     "envelope (125.7 W, node) and glycol fill pot",
     "- A-HX: loop area 186 m DN32 = 24.8 m2 reported from the model plus the "
     "node-quoted buried run - not called a calculated duty (the duty states no "
     "mass throughput; q_per_m/Q_ceiling are the survey-locked class figures)",
     "- The boreholes are drilled subsurface works (site/well lane): depth/"
     "spacing named, not drawn to depth (hold W12); hose-barb nozzles per the "
     "schedule (bores not calculated, hose, atmospheric)"],
    "A-core + A-HX")

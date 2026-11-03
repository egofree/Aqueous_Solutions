"""PV_ARRAY drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, table01 (rails + feet + tilted strips),
array01 (the array facts sheet, plan of the roof layout), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, math, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets                                       # noqa: E402

ns = runpy.run_path(HERE / "pv_array.py")
parts, R = ns["parts"], ns["report"]
unit = "PV_ARRAY"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


table = union_all([parts["table_rails"], parts["ballast_feet"], parts["module_strips"]])
aux = union_all([parts["plinth"], parts["frame"], parts["roof_deck"]])
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
M = R["machine"]
AF = M["array_facts"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm envelope - the node size_mm; the build is '
      'the box-scale representative table section (WAFER_FAB room-scale precedent); '
      'the array figures are reported, not shrunk onto the box',
      f'Array per the node: 15 tables of {AF["table_mm"][0]/1000:g} x '
      f'{AF["table_mm"][1]/1000:g} m over the 210 x 138 m roof footprint, '
      f'{AF["modules"]} modules x 0.5 kW = nameplate 3026 kWp, area 26574 m2, '
      'roof only per X-PAR-07 (ground field removed)',
      'Representative table: 3 module-plane strips covering 60 % of the plane '
      '(GCR 0.6, A-M-103), tilt +10 deg about +X, +Y edge raised (equator-facing, '
      'site north = +Y heritage rule)',
      'A-MACH: hold-down frame + ballast feet (the anchor drawn, A-M-105 '
      '0.15 kPa ballast class)'],
     "General arrangement, front elevation (low edge). Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Tilt section: module plane rises toward +Y at the drawn 10 deg study tilt '
      '(A-M-103 low-tilt; the verification test is a PVWatts run at the roof '
      'tilt and azimuth - hold, W12)',
      f'Array mass {AF["mass_t"]:g} t at 17 kg/m2 modules + ballasted racking '
      '(A-M-184) over the 26574 m2 node area; roof loads service 1.11 / LRFD '
      '1.716 kPa (A-M-105)',
      'Ballast feet 80 x 80 x 240 under the table rails; the roof-ballast design '
      'is the X-BLD lane\'s (hold, W12)'],
     "General arrangement, side elevation. Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     ['4 schedule rows of docs-authority/nozzles/PV_ARRAY.csv at tag, face and bore',
      'N1 solar into the array (DN25) on -Y at z 160; N2 PV daily average (DN25) '
      'on +Y at z 600 - the electrical edges drawn as the schedule\'s tube rows '
      'with the conductor note carried (duty inline rows: "Rating conductor. Not '
      'a hose")',
      'N3 drain flush at the envelope bottom (50 datum); N4 vent flush at the '
      'envelope top (800 datum = box top)',
      'Duty section 4 verbatim: DN copied from the edge, not recalculated'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("table01", table, (0, 1, 0),
     ['Table rails on 4 ballast feet (80 x 80 x 240) with the tilted module '
      'plane: 3 strips, 60 % coverage (GCR 0.6, A-M-103)',
      'Modules are purchased envelopes per plan rule 6 (0.5 kW, STC eff 0.19); '
      'module dimensions are not stated on the node (hold, W12)',
      'Ballasted racking is the shop make (X-MFG-32 class); the roof-ballast '
      'design is the X-BLD lane\'s'],
     "Fabricated part sheet: table rails + ballast feet + module plane."),
    ("array01", aux, (0, 0, -1),
     ['Array plan facts (reported, the representative build is box-scale): 15 '
      'tables 5 x 3 inside the 1829 mm perimeter pathway (interior 1219 mm), '
      'IFC 2027 1205.3 / NFPA 1 11.12; solver roof_close segment math',
      f'Tables {AF["table_mm"][0]:g} x {AF["table_mm"][1]:g} mm; roof footprint '
      '210000 x 138000 mm; area 26574 m2; nameplate 3026 kWp (6052 x 0.5 kW); '
      'average delivered 368.99 kW (A-M-233 rebasis)',
      'Roof PV access per IFC 2027 1205.3 / NFPA 1 11.12 is stamped on the '
      'EXT_HALL duty; the roof structure is the X-BLD lane\'s'],
     "Fabricated part sheet: the array plan facts."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: solar in on -Y, PV daily average out on +Y; the tilt '
      'faces the equator (+Y edge raised, site north = +Y)',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/pv_array.step) is the solids of record',
      'Tracker --check green; acceptance A-core + A-MACH per AQS-PLAN-006 '
      'section 5 (route F-MACH)'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/pv_array.py", f"models/mfg/{unit}/draw_pv_array.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ["- Representative array-table section at the registry box (WAFER_FAB "
     "room-scale precedent): tilted module plane (3 strips, 60 % GCR coverage, "
     "A-M-103), table rails, 4 ballast feet; the array facts reported from the "
     "node - 15 tables over the 210 x 138 m roof, 6052 x 0.5 kW = 3026 kWp, "
     "26574 m2, 451.8 t at A-M-184",
     "- Tilt +10 deg about +X, +Y edge raised (equator-facing, site north = +Y "
     "heritage rule); the numeric tilt is a study value pending the PVWatts run "
     "(hold, WORK_ORDER W12)",
     "- A-MACH: hold-down frame + ballast anchors drawn; modules purchased per "
     "plan rule 6 with the node ratings"],
    "A-core + A-MACH")

"""VAC_CAST drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, chamber01 (vacuum chamber + lid),
mould01 (mould-tilt table + crucible set + pour hardware), aux01 (pump skid +
cabinet + plinth + connection hardware), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets                                       # noqa: E402

ns = runpy.run_path(HERE / "vac_cast.py")
parts, R = ns["parts"], ns["report"]
unit = "VAC_CAST"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


chamber = union_all([parts["chamber_shell"], parts["chamber_lid"]])
mould = union_all([parts["mould_table"], parts["tilt_frame"], parts["trunnion_pins"],
                   parts["pour_lip"], parts["crucible"], parts["crucible_backup"]])
aux = union_all([parts["plinth"], parts["vacuum_pump_skid"], parts["control_cabinet"]])
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
M = R["machine"]
S = R["standby"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm overall - the node N+1 rated envelope (A-M-282), filled exactly',
      'Vacuum tilt-pour casting station, N+1 standby of CAST_LINE / CONT_CAST: ' + S["state"],
      '304L vacuum chamber on the plinth, vacuum pump skid and control cabinet on the +X bay',
      'Mould-tilt table inside the chamber; graphite crucible on its alumina backup (buy set)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     [f'Chamber shell t{M["chamber"]["wall_mm"]:g} 304L (study fab-page value - hold, W12), '
      f'lid t40 with clamp studs; chamber z 60..1200 on the plinth',
      'Tilt pour about the trunnion axis at z 500; pour lip serves the melt row at z 600',
      'The 3 kg design-case melt (node design) is drawn as a process-inventory solid, not a BOM part',
      'General tolerance ISO 2768-m unless noted'],
     "General arrangement, side elevation. Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     [f'{R["nozzle_count_schedule"]} schedule rows of docs-authority/nozzles/VAC_CAST.csv '
      'at tag, face and bore',
      'N1 DN15 melt inlet +Y at z 160 flush at the envelope face (registered compass layout, '
      'params.json layout block)',
      'N2 DN15 drain through the plinth, flush at the envelope bottom (50 datum); '
      'N3 DN15 vent riser on the chamber lid, flush at the envelope top (800 datum is the '
      'schedule placeholder - hold, W12)',
      'Atmospheric hose makeup at the face (duty section 4); Class 150 schedule column '
      'carried verbatim as text'],
     "Connection orientation, top view. Tags/faces/bore per the schedule."),
    ("chamber01", chamber, (0, 1, 0),
     [f'304L vacuum chamber {M["chamber"]["od_mm"][0]:g} x {M["chamber"]["od_mm"][1]:g} '
      f'x z {M["chamber"]["z_mm"][0]:g}..{M["chamber"]["z_mm"][1]:g}, shell t6, lid t40',
      'Passes shown: drain through the floor, vent in the lid, melt inlet +Y',
      'Welds per the unit WORK_ORDER route (304L GTAW, full penetration); leak test at the '
      'study chamber duty (W10)',
      'General tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: vacuum chamber and lid."),
    ("mould01", mould, (0, 1, 0),
     [f'Steel mould-tilt table deck z 300..330 on legs (duty section 3 table hardware)',
      f'Tilt cradle and trunnions at z 500; graphite crucible OD {M["crucible"]["od_mm"]:g} '
      f'x {M["crucible"]["h_mm"]:g} on its alumina backup - consumable set, buy',
      'Pour lip serves the melt row at z 600; tilt actuator package purchased at fabrication (W12)',
      'General tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: mould-tilt table, crucible set, pour hardware."),
    ("aux01", aux, (1, -0.5, 0.7),
     ['Vacuum pump skid and control cabinet on the +X bay - purchased per plan rule 6, drawn '
      'as their envelopes; 7.5 kW connected (node design); standby unit (A-M-282)',
      'Plinth with 8 x M12 wedge anchors (fasteners.csv item 1); 12 x M10 A4-70 lid and '
      'cabinet-rail studs (item 2)',
      'Connection hardware DN15 open-bore tube (lib/dn Sch 40 table), flush at the envelope faces'],
     "Fabricated part sheet: pump skid, cabinet, plinth, connection hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: chamber at the -X end, pump and cabinet bay +X; melt enters +Y at '
      'z 160, castings leave through the chamber door at the unit-task design',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/vac_cast.step) is the solids of record',
      'Standby N+1 alternate: the machine is real, the design-day rate is zero on the '
      'graph (duty section 2)'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/vac_cast.py", f"models/mfg/{unit}/draw_vac_cast.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ['- Standby N+1 alternate drawn per the node design block (A-M-282/A-M-283): real machine, '
     'standby-zero design-day rate; named in the BOM rows and the WORK_ORDER',
     '- 304L vacuum chamber per duty section 3; graphite crucible + alumina backup as the '
     'consumable buy set; CA 0 mm (AQS-STD-001)',
     '- Purchased vacuum pump skid and control cabinet (7.5 kW connected, node design) drawn '
     'as their envelopes per plan rule 6'],
    "A-core, A-SC (route hold)")

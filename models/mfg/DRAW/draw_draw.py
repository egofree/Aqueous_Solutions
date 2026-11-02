"""DRAW drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, bench01 (bench bed + die stand + die
set), capstan01 (capstan group + drive bay + gripper), aux01 (cabinet + plinth +
guard rail), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets                                       # noqa: E402

ns = runpy.run_path(HERE / "draw.py")
parts, R = ns["parts"], ns["report"]
unit = "DRAW"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


bench = union_all([parts["bench_bed"], parts["die_stand"], parts["die_set"]])
capstan = union_all([parts["capstan_drum"], parts["capstan_shaft"], parts["gripper_carriage"],
                     parts["wire_guides"], parts["drive_group"]])
aux = union_all([parts["plinth"], parts["control_cabinet"], parts["guard_rail"]])
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
M = R["machine"]
S = R["standby"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm overall - the node N+1 rated envelope (A-M-282), filled exactly',
      'Bench wire/rod draw bench, N+1 former of ROLL: ' + S["state"],
      f'Steel bench bed {M["bench"]["basis"].split("bench_mm ")[1].split(";")[0]} (node design bench_mm) with die stand -X and capstan head +X',
      'Tungsten-carbide die set in tool-steel casings - consumable buy set (duty section 3)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     [f'Capstan drum OD {M["capstan"]["od_mm"]:g} at z 720 (study size - hold, W12); the capstan '
      'hardware carries the machine lubricant programme - no wetted stream (duty section 3)',
      'Drive group behind the capstan and control cabinet on the -X floor - purchased envelopes (plan rule 6)',
      'Die-zone and capstan guard rail, 4 posts x 3 tiers (A-MACH: guard drawn)',
      'General tolerance ISO 2768-m unless noted'],
     "General arrangement, side elevation. Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     [f'{R["nozzle_count_schedule"]} schedule rows of docs-authority/nozzles/DRAW.csv '
      'at tag, face and bore',
      'N1 solids wire out on +X at z 600 (drawn at DN15, bore not calculated, W4), riding the take-off guide',
      'N2 DN15 drain through the plinth, flush at the envelope bottom (50 datum); '
      'N3 DN15 vent riser on the capstan head, flush at the envelope top (800 datum is the '
      'schedule placeholder - hold, W12)',
      'Atmospheric hose makeup at the face (duty section 4); Class 150 schedule column '
      'carried verbatim as text; compass mapping is the registered layout (params.json layout block)'],
     "Connection orientation, top view. Tags/faces/bore per the schedule."),
    ("bench01", bench, (0, 1, 0),
     [f'Steel bench bed z {M["bench"]["z_mm"][0]:g}..{M["bench"]["z_mm"][1]:g} on 4 legs '
      '(duty section 3 steel bench)',
      f'Die stand on the -X head with {M["die_set"]["count"]} tungsten-carbide dies in '
      'tool-steel casings - consumable buy set (DIETER1988 ch. 20/21)',
      'The diamond last-pass alternative is the duty alternative row (not drawn)',
      'Welds per the unit WORK_ORDER route; general tolerance ISO 2768-m'],
     "Fabricated part sheet: bench bed, die stand, die set."),
    ("capstan01", capstan, (0, 1, 0),
     [f'Capstan drum OD {M["capstan"]["od_mm"]:g} with shaft and drive bay behind it (purchased '
      'drive per plan rule 6)',
      'Gripper carriage on the bench bed; 3 wire-guide sheave pins',
      'Lubricant programme is the capstan hardware duty (duty section 3), process note not geometry',
      'General tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: capstan group, drive bay, carriage."),
    ("aux01", aux, (1, -0.5, 0.7),
     ['Control cabinet 3 kW connected (node design) - purchased per plan rule 6, drawn as its '
      'envelope; standby unit, energized only on the ROLL outage (A-M-282)',
      'Plinth with 8 x M12 wedge anchors (fasteners.csv item 1); 10 x M12 8.8 studs on the '
      'die-stand clamp and bearing blocks (item 2)',
      'Connection hardware DN15 open-bore tube (lib/dn Sch 40 table), flush at the envelope faces'],
     "Fabricated part sheet: cabinet, plinth, guard rail."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: die stand -X, capstan head +X; wire leaves +X at z 600',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/draw.step) is the solids of record',
      'Standby N+1 alternate: the machine is real, the design-day rate is zero on the '
      'graph (duty section 2)'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/draw.py", f"models/mfg/{unit}/draw_draw.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ['- Standby N+1 alternate drawn per the node design block (A-M-282/A-M-283): real machine, '
     'standby-zero design-day rate; named in the BOM rows and the WORK_ORDER',
     '- A-MACH: die-zone and capstan guard rail and slab anchors drawn; drive group and control '
     'cabinet are the purchased items named with the node rating',
     '- Carbide die set is the purchased consumable (buy row); steel bench per duty section 3; '
     'CA 0 mm (AQS-STD-001)',
     '- The solids schedule row (N1 wire) is drawn at DN15 labeled bore not calculated (W4); '
     'A-SC make rows flagged and W11 cross-references AQS-BOM-SC-001'],
    "A-core, A-MACH, A-SC")

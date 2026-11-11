"""EXTRUDE drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, frame01 (platens + tie rods + bed +
container group), die01 (H13 die + ram + loader/chute), aux01 (HPU + pedestal +
plinth + guard rail), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets, step_export  # noqa: E402

ns = runpy.run_path(HERE / "extrude.py")
parts, R = ns["parts"], ns["report"]
unit = "EXTRUDE"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


frame = union_all([parts["rear_platen"], parts["front_platen"], parts["tie_rods"],
                   parts["bed"], parts["container"], parts["die_holder"]])
die = union_all([parts["h13_die"], parts["main_ram"], parts["ram_nut"],
                 parts["billet_loader"], parts["runout_chute"]])
aux = union_all([parts["plinth"], parts["hpu_skid"], parts["control_pedestal"],
                 parts["guard_rail"]])
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
M = R["machine"]
S = R["standby"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm overall - the node N+1 rated envelope (A-M-282), filled exactly',
      'Horizontal profile press, N+1 former of ROLL: ' + S["state"],
      'Tie-rod frame, container group on the z 600 axis, billet loader -X, run-out chute +X',
      f'Node design container_mm {M["container"]["bore_mm"]:g}; H13 die is the consumable buy set'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['CS platens and tie rods (study sections - hold, W12); tool-steel container liner (duty section 3)',
      f'Main ram from the rear platen, study OD (container bore + 20 - hold, W12); press_t {M["ram"]["press_t"]} node rating',
      'HPU skid on the -X floor bay and control pedestal - purchased envelopes (plan rule 6)',
      'General tolerance ISO 2768-m unless noted'],
     "General arrangement, side elevation. Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     [f'{R["nozzle_count_schedule"]} schedule rows of docs-authority/nozzles/EXTRUDE.csv '
      'at tag, face and bore',
      'N1 solids billet in on -X at z 160 (drawn at DN15, bore not calculated, W4); '
      'N2 solids rod/profile out on +X at z 600 (bore not calculated)',
      'N3 DN15 drain through the plinth, flush at the envelope bottom (50 datum); '
      'N4 DN15 vent riser, flush at the envelope top (800 datum is the schedule placeholder - hold, W12)',
      'Atmospheric hose makeup at the face (duty section 4); Class 150 schedule column '
      'carried verbatim as text; compass mapping is the registered layout (params.json layout block)'],
     "Connection orientation, top view. Tags/faces/bore per the schedule."),
    ("frame01", frame, (0, 1, 0),
     [f'Platens at x {M["frame"]["platen_x_mm"][0]:g}..{M["frame"]["platen_x_mm"][1]:g} on 4 tie rods',
      f'Container group: tool-steel liner bore {M["container"]["bore_mm"]:g} (node design '
      'container_mm) in its housing, die holder at the front platen',
      'Tie-rod nuts and die-holder clamp in fasteners.csv (item 2, M24)',
      'Welds and fits per the unit WORK_ORDER route; general tolerance ISO 2768-m'],
     "Fabricated part sheet: frame, container group."),
    ("die01", die, (0, 1, 0),
     ['H13 extrusion die (consumable buy row; nitrided die land where galling is measured - first-article item)',
      'Main ram with nut from the rear platen; billet loader and run-out chute furniture',
      'The hydraulic cylinder package purchases at fabrication (W12)',
      'General tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: die, ram, loader and chute."),
    ("aux01", aux, (1, -0.5, 0.7),
     ['HPU skid 15 kW connected (node design) - purchased per plan rule 6, drawn as its '
      'envelope; standby unit, energized only on the ROLL outage (A-M-282)',
      'Control pedestal - purchased envelope; die-zone guard rail on the operator side '
      '(A-MACH: guard drawn); plinth anchors in fasteners.csv item 1',
      'Connection hardware DN15 open-bore tube (lib/dn Sch 40 table), flush at the envelope faces'],
     "Fabricated part sheet: HPU, pedestal, plinth, guard."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: billet loader -X, press centre, run-out +X; HPU bay -X floor, pedestal rear-centre',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/extrude.step) is the solids of record',
      'Standby N+1 alternate: the machine is real, the design-day rate is zero on the '
      'graph (duty section 2)'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/extrude.py", f"models/mfg/{unit}/draw_extrude.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ['- Standby N+1 alternate drawn per the node design block (A-M-282/A-M-283): real machine, '
     'standby-zero design-day rate; named in the BOM rows and the WORK_ORDER',
     '- A-MACH: die-zone guard rail and slab anchors drawn; HPU skid and control pedestal are '
     'the purchased items named with the node rating',
     '- H13 die is the purchased consumable (buy row); tool-steel container liner per duty '
     'section 3; CA 0 mm (AQS-STD-001)',
     '- The 2 solids schedule rows are drawn at DN15 labeled bore not calculated (W4); '
     'A-SC make rows flagged and W11 cross-references AQS-BOM-SC-001'],
    "A-core, A-MACH, A-SC (route hold)")

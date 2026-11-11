"""HYDRO_SET drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, set01 (the machine envelopes + buffer
vessel), interface01 (penstock/tailrace pads, Q-009 facts), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets, step_export  # noqa: E402

ns = runpy.run_path(HERE / "hydro_set.py")
parts, R = ns["parts"], ns["report"]
unit = "HYDRO_SET"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


set_env = union_all([parts["turbine_env"], parts["generator_env"],
                     parts["pump_motor_env"], parts["cabinet_env"],
                     parts["buffer_vessel"]])
interface = union_all([parts["penstock_pad"], parts["tailrace_pad"],
                       parts["buffer_vessel"]])
aux = union_all([parts["plinth"], parts["frame"]])
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
M = R["machine"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm envelope - the node size_mm ({R["size_basis"]}); '
      'the build fills it exactly (hold-down frame + vent riser pin the box)',
      'Pumped-hydro powerhouse set per the node backup_basis (A-M-145 lane; '
      'Q-006/Q-009 closed): the diverse N+1 backup of ZNBR2 (third source '
      'FUEL_CELL) to NFPA 111 Level 1, Class X - 14 h at the 14.46 kW critical '
      'load = 202.4 kWh at the bus',
      'Machine envelopes per plan rule 6: turbine (14.46 kW discharge at 36.21 m '
      'head, eta 0.8), generator, pump-motor (49.6 kW recharge over the PV '
      'window, eta 0.85; round trip 0.68), electrical cabinet; buffer manifold '
      'vessel (study, W12)',
      'A-MACH: hold-down/guard frame + 8 slab anchors; no machine type invented '
      '- the maker prints govern'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Bays: turbine x 60..340, generator x 340..560, pump-motor x 560..720, '
      'cabinet x 720..960; buffer vessel at x 450 (layout choice, W12)',
      'Reservoir interface per Q-009: upper = the building top floors (3 levels '
      'x 3.06 m water over 367 m2, 2 cells/level, from +16.8 m, 2700 m3 node); '
      'lower = CATCH_TANK 9.17 m over 367 m2; eta_net_with_penstock 0.76',
      'The reservoir structures and penstock routing are building scope '
      '(AQS-BLD-014, A-M-187) - the pads here are interface indications, bores '
      'not calculated (W4)'],
     "General arrangement, side elevation (end view). Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     ['3 schedule rows of docs-authority/nozzles/HYDRO_SET.csv at tag, face and bore',
      'N1 hydro turbine-pump electrical out on +Y at z 600 - schedule service '
      'text verbatim including the "MISSING on SLD" note (the one-line update is '
      'an electrical-lane item)',
      'N2 drain flush at the envelope bottom (50 datum); N3 vent flush at the '
      'envelope top (800 datum = box top)',
      'Atmospheric tube per duty section 4, no flange (W4 110 % rule)'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("set01", set_env, (0, 1, 0),
     ['The purchased-class machine envelopes: turbine, generator, pump-motor, '
      'electrical cabinet (ratings on each in check.machine) and the buffer '
      'manifold vessel OD 160 x 300 (study, hold W12)',
      'No machine type is named on the node - the envelopes are the model; the '
      'maker prints govern at order (hold, WORK_ORDER W12)',
      '316L per duty section 3 where wet; CA 0 mm (AQS-STD-001)'],
     "Fabricated part sheet: machine envelopes + buffer vessel."),
    ("interface01", interface, (1, 0, 0),
     ['Penstock supply pad on the turbine bay top (from the upper reservoir '
      'above) and tailrace return pad at the pump bay base (to CATCH_TANK)',
      'Q-009 facts: upper reservoir = the building top floors from +16.8 m '
      '(roof PV at +34.8 m); lower = CATCH_TANK, floor -15.70 m',
      'Bores not calculated (W4); the penstock loss is the node '
      'eta_net_with_penstock 0.76 figure - no set point claimed'],
     "Fabricated part sheet: reservoir interface pads."),
    ("iso01", aux.union(full), (1, -1, 1),
     ['Plant orientation: discharge N1 out on +Y to the bus; the water loop runs '
      'up to the building reservoirs and back through CATCH_TANK',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/hydro_set.step) is the solids of record',
      'Tracker --check green; acceptance A-core + A-MACH per AQS-PLAN-006 '
      'section 5 (route F-MACH)'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/hydro_set.py", f"models/mfg/{unit}/draw_hydro_set.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ["- Pumped-hydro powerhouse set per the node backup_basis (A-M-145 lane; "
     "Q-006/Q-009 closed): N+1 backup of ZNBR2 to NFPA 111 Level 1 Class X (14 h "
     "at 14.46 kW = 202.4 kWh); turbine (14.46 kW at 36.21 m, eta 0.8), "
     "generator, pump-motor (49.6 kW recharge, eta 0.85) and cabinet envelopes "
     "per plan rule 6",
     "- Reservoir interface per the Q-009 facts: upper = building top floors "
     "(3 levels x 3.06 m over 367 m2, 2 cells/level), lower = CATCH_TANK "
     "(9.17 m over 367 m2); penstock/tailrace pads drawn, bores not calculated "
     "(W4) - the reservoirs are building scope (AQS-BLD-014, A-M-187)",
     "- A-MACH: hold-down/guard frame + 8 anchors; purchased items named with "
     "the node ratings; no machine type invented (holds, WORK_ORDER W12)"],
    "A-core + A-MACH")

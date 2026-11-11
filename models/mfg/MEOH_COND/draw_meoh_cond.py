"""MEOH_COND drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, sh01 (shell + heads + plinth),
in01 (coil), aux01 (connection hardware), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets, step_export  # noqa: E402

ns = runpy.run_path(HERE / "meoh_cond.py")
parts, R = ns["parts"], ns["report"]
unit = "MEOH_COND"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


shell = union_all([parts["plinth"], parts["shell"]])
internals = parts["coil"]
aux = parts["nozzles"]
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
K = R["ko_drum"]
C = K["coil"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm overall - the node-sized envelope '
      '(meoh_train.py, AQS-DUTY-077: D 400, H 600, drum 71.19 L nominal), filled '
      'exactly; the shell is tangent to all four faces',
      'Vertical 316L knock-out drum: shell OD 400, wall 3 mm (study - hold, W12), '
      'on a plinth with heads',
      'Coil per the node design (sheet IN01); knock-out pot + condenser on one skid',
      'Methanol-train condensate service, atmospheric (duty sections 2, 4 and 6)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Coil: 316L tube OD 10, ~2.6 turns at a 120 mm mean diameter, 1.000 m '
      'developed, z 80..185 (node design: 1 x 10 mm x 1 m coil)',
      'N2 outlet datum 600 clamped to 584.4 by the barb-radius rule; N4 vent flush '
      'at the top head (the 800 datum predates the box) - holds, W12',
      'Condensing 0.7079 kW at U 1.2 kW/m2K, LMTD 19.6 K (node design block)'],
     "General arrangement, side elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("nozzle_orient", full, (0, 0, -1),
     ['5 schedule rows of docs-authority/nozzles/MEOH_COND.csv at tag, face and bore',
      'N1/N5 condensate sources in on -Y at z 160; N2 condensate out on +Y '
      '(clamped 584.4); per-tag positions in check.nozzles_drawn',
      'N3 drain boss on the base head (50 datum); N4 vent flush at the top head',
      'Atmospheric hose barbs; the schedule rating column (Class 150) carried '
      'verbatim as text - no flange drawn (duty section 4)'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("sh01", shell, (0, 1, 0),
     ['Shell OD 400 x wall 3 316L, z 40..560, heads, plinth',
      'CA 0 mm on the 316L (AQS-STD-001); wall a study value (hold, W12)',
      'Welds per the unit WORK_ORDER route (F-VES): sheet/pipe cut, gas-tungsten-arc weld, '
      'set-in ports, leak test of shell and coil sides separately'],
     "Fabricated part sheet: shell + heads + plinth."),
    ("in01", internals, (0, 1, 0),
     [f'Coil: OD {C["tube_od_mm"]:g} x {C["developed_mm"] / 1000.0:.3f} m developed, '
      f'{C["turns"]:g} turns (node book: 1 x 10 mm x 1 m), {C["area_drawn_m2"]} m2 DRAWN',
      f'A-HX-style report: the drawn area is 0.0013 m2 over the node figure '
      f'{C["area_node_m2"]} - reported, nothing resized (hold, W12)',
      'Coil z 80..180 in the lower drum; both ends stub through the end walls'],
     "Fabricated part sheet: coil."),
    ("aux01", aux, (0, 1, 0),
     ['Connection hardware DN15 as atmospheric hose barbs (lib/nozzles.py); barb '
      'profile a study proportion, finished against the hose supplier print',
      'Schedule rating column (Class 150) carried verbatim as text - duty section 4 '
      '(atmospheric hose; W4 110 percent rule: no process pressure)',
      '316L hardware per duty section 3 (methanol/water traces)'],
     "Fabricated part sheet: connection hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: condensate sources in on -Y at z 160, out on +Y (clamped '
      '584.4), drain at the base head, vent on the top head',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/meoh_cond.step) is the solids of record',
      f'Build fills the node-sized envelope exactly; holdup {R["holdup_m3"]} m3 '
      'reported against the node drum figure, no residence derived (A-VES)'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/meoh_cond.py", f"models/mfg/{unit}/draw_meoh_cond.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    [f"- A-VES: the {R['holdup_m3']} m3 liquor volume is reported against the node "
     "drum_L 71.19 nominal figure; no residence time is derived (the duty section 2 "
     "box sentence is explicitly not a residence time)",
     "- Coil area: the drawn 0.0314 m2 is 0.0013 m2 over the node book 0.0301 "
     "(nominal figure) - reported, nothing resized (W12)"],
    "A-core + A-VES")

"""MET_HX_Q4 drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, sh01 (shell + frame + plinth),
in01 (tube bundle + sheets), aux01 (connection hardware), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets                                       # noqa: E402

ns = runpy.run_path(HERE / "met_hx_q4.py")
parts, R = ns["parts"], ns["report"]
unit = "MET_HX_Q4"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


shell = union_all([parts["plinth"], parts["frame"], parts["shell"]])
internals = union_all([parts["tube_sheets"], parts["bundle"]])
aux = parts["nozzles"]
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
X = R["hx"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm overall - the study registry envelope, filled '
      'exactly (the duty states no kilowatts and no calculated area)',
      f'Vertical 316L shell OD {X["shell_od_mm"]:g}, wall {X["wall_mm"]:g} mm (study - '
      'hold, W12), on a plinth inside a four-post hold-down frame',
      f'Straight-tube bundle: {X["tubes"]} tubes OD 12 x 525 between tube sheets at '
      f'z {X["tube_sheets_z_mm"][0]:g}/{X["tube_sheets_z_mm"][1]:g}',
      'Duty: Q4 loop heat exchange at < 80 C, atmospheric (duty sections 2 and 6)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Bundle tubes lap both tube sheets; the shell stands 30 off the envelope face, '
      'within the barb reach (flush hardware idiom)',
      'Frame posts run plinth to top bars; the shell base head laps the plinth',
      'Drawn 316L per duty section 3 s wet branch; the carbon-steel alternative (dry '
      'hydrocarbon or dry gas stream) is a named hold, W12'],
     "General arrangement, side elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("nozzle_orient", full, (0, 0, -1),
     ['3 schedule rows of docs-authority/nozzles/MET_HX_Q4.csv at tag, face and bore',
      'N1 DN15 "heat < 80 C" out on +Y at z 600 (fits the 800 box)',
      'N2 drain boss on the base head (50 datum); N3 vent flush at the top head - the '
      '800 datum IS the envelope top',
      'Atmospheric hose barbs; per-tag positions in check.nozzles_drawn'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("sh01", shell, (0, 1, 0),
     [f'Shell OD {X["shell_od_mm"]:g} x t {X["wall_mm"]:g} 316L, z 40..760, heads, '
      f'{L:g} x {W:g} plinth, four 20 mm posts and top bars',
      'CA 0 mm on the 316L (AQS-STD-001); wall a study value (hold, W12)',
      'Welds per the unit WORK_ORDER route (F-HX): sheet/pipe cut, weld, set-in ports, '
      'leak test'],
     "Fabricated part sheet: shell + frame + plinth."),
    ("in01", internals, (0, 1, 0),
     [f'Bundle: {X["tubes"]} tubes OD 12 x 525 between two 15 mm tube sheets, '
      f'{X["area_drawn_m2"]:g} m2 DRAWN',
      'A-HX: the area is reported as drawn, NOT called calculated - the node carries '
      'no heat rate (duty section 2)',
      'Tube wall 1.5 mm is a study value (hold, W12); tubes lap both sheets'],
     "Fabricated part sheet: tube bundle + sheets."),
    ("aux01", aux, (0, 1, 0),
     ['Connection hardware DN15 as an atmospheric hose barb (lib/nozzles.py); barb '
      'profile a study proportion, finished against the hose supplier print',
      'Schedule rating column (Class 150) carried verbatim as text - duty section 4: '
      'hose, atmospheric (W4 110 % rule: no process pressure)',
      'Material conditional: 316L drawn per duty section 3 s wet branch; the '
      'carbon-steel alternative holds until the stream is resolved (W12)'],
     "Fabricated part sheet: connection hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: heat out on +Y at z 600, drain at the base head, vent on the '
      'top head',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/met_hx_q4.step) is the solids of record',
      'Build fills the study registry envelope exactly; tracker --check green'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/met_hx_q4.py", f"models/mfg/{unit}/draw_met_hx_q4.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    [f"- A-HX: the {X['area_drawn_m2']} m2 bundle area is reported as DRAWN, not "
     "called calculated - the node has no heat rate (duty section 2)",
     "- Material conditional: drawn 316L per duty section 3 s wet branch; the "
     "carbon-steel alternative is a named hold (W12)"],
    "A-core + A-HX")

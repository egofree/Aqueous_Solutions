"""HX8 drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, sh01 (shell + frame + plinth),
in01 (PVDF bundle + tube sheets), aux01 (connection hardware), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets, step_export  # noqa: E402

ns = runpy.run_path(HERE / "hx8.py")
parts, R = ns["parts"], ns["report"]
unit = "HX8"


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
      'exactly (duty section 2 gives area, U and LMTD, not the box)',
      f'Vertical PVC-U shell OD {X["shell_od_mm"]:g}, wall {X["wall_mm"]:g} mm (study - '
      'hold, W12), on a plinth inside a four-post hold-down frame',
      f'PVDF straight-tube bundle: {X["tubes"]} tubes OD 10 x 360 between tube sheets at '
      f'z {X["tube_sheets_z_mm"][0]:g}/{X["tube_sheets_z_mm"][1]:g}',
      'Duty: EW reject cooling against Q4 return preheat, 4.59 kW at U 1500 W/m2K, '
      'LMTD 6 K (duty section 2)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Bundle tubes lap both tube sheets; the shell stands 30 off the envelope face, '
      'within the barb reach (flush hardware idiom)',
      'Frame posts run plinth to top bars; the shell base head laps the plinth',
      'PVDF wetted per duty section 3 (AQS-STD-002 section 4.5, owner adoption '
      '2026-10-15); PVC-U on the Q4 water side; titanium withdrawn, no graphite'],
     "General arrangement, side elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("nozzle_orient", full, (0, 0, -1),
     ['7 schedule rows of docs-authority/nozzles/HX8.csv at tag, face and bore',
      'N1 DN15 EW heat in on -Y at z 160; N2/N3 DN15 and N6/N7 DN25 out on +Y, clamped '
      'to z 581.5/584.4 (schedule datum 600 at the envelope top - hold, W12)',
      'N4 drain boss on the base head (50 datum); N5 vent flush at the top head '
      '(800 datum predates the 600 box - hold, W12)',
      'Atmospheric hose barbs; design_kPa 17.8 is the old head-plus-10 figure, not a '
      'pressure rating (duty section 4); per-tag positions in check.nozzles_drawn'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("sh01", shell, (0, 1, 0),
     [f'Shell OD {X["shell_od_mm"]:g} x t {X["wall_mm"]:g} PVC-U, z 40..560, heads, '
      f'{L:g} x {W:g} plinth, four 20 mm posts and top bars',
      'CA 0 mm (AQS-STD-001 polymer rule); PVC-U on the Q4 water side (duty section 3)',
      'Welds per the unit WORK_ORDER route (F-HX): sheet/pipe cut, thermoplastic weld, '
      'set-in ports, leak test'],
     "Fabricated part sheet: shell + frame + plinth."),
    ("in01", internals, (0, 1, 0),
     [f'PVDF bundle: {X["tubes"]} tubes OD 10 x 360 between two 15 mm tube sheets, '
      f'{X["area_model_m2"]:g} m2 tube area from the model against the {X["area_duty_m2"]:g} '
      'm2 duty figure (A-HX; nothing resized)',
      'The duty carries a heat rate (4.59 kW at U 1500, LMTD 6 K, edges 4.572 kW): the '
      'area is duty-sized, not invented here',
      'Tube wall 1.5 mm is a study value (hold, W12); tubes lap both sheets'],
     "Fabricated part sheet: PVDF bundle + tube sheets."),
    ("aux01", aux, (0, 1, 0),
     ['Connection hardware DN15/DN25 as atmospheric hose barbs (lib/nozzles.py); '
      'barb profile a study proportion, finished against the hose supplier print',
      'Schedule rating column (Class 150) carried verbatim as text - duty section 4: '
      'hose, atmospheric (W4 110 % rule: no process pressure)',
      'Two hand-era schedule rows (N2/N3) carried an unquoted comma that shifted their '
      'face and height fields; repaired to the quoting of the identical N6/N7 rows '
      '(change record, notes/tier4_feed_solids_m3_2026-11-01.md)'],
     "Fabricated part sheet: connection hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: liquor in on -Y at z 160, out on +Y at the clamped top rows; '
      'drain at the base head, vent on the top head',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/hx8.step) is the solids of record',
      'Build fills the study registry envelope exactly; tracker --check green'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/hx8.py", f"models/mfg/{unit}/draw_hx8.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    [f"- A-HX: tube area {X['area_model_m2']} m2 from the model against the "
     f"{X['area_duty_m2']} m2 duty figure (46 tubes OD 10 x 360); the duty carries the "
     "heat rate (4.59 kW at U 1500, LMTD 6 K), so the area is duty-sized and reported, "
     "not recalculated as a claim",
     "- Bundle: real PVDF tubes between two tube sheets (duty section 3; AQS-STD-002 "
     "section 4.5 owner adoption; titanium withdrawn, no graphite)"],
    "A-core + A-HX")

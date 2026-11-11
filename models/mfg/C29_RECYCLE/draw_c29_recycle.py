"""C29_RECYCLE drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient (the branch layout along the run),
spool01 (run + bend riser), aux01 (plinth, stands, drain and vent), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets, step_export  # noqa: E402

ns = runpy.run_path(HERE / "c29_recycle.py")
parts, R = ns["parts"], ns["report"]
unit = "C29_RECYCLE"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else s.union(s)
    return u


spool = union_all([parts["run"], parts["riser"], parts["out_branch"], parts["in_branch"]])
aux = union_all([parts["plinth"], parts["stands"], parts["nozzles"]])
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
S = R["spool"]
LL = R["line_list"]
X = R["nozzles_drawn"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm envelope - the node size_mm (study registry '
      'box, per its size_note; the duty section 4 prose line "Size 2000 x 60 x 60" '
      'is an older study frame, W12)',
      f'Spool {S["dn"]} OD {S["od_mm"]:g}, wall {S["wall_mm"]:g} mm (Sch 40 table; '
      'schedule not stated on the node - hold, W12), carbon steel per duty section 3',
      'X-run at the schedule inlet datum z 160; bend riser to the outlet datum z 600; '
      'trough plinth with two saddle stands; 4 slab anchors',
      f'{S["run_basis"]}'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['The run sits at depth centre y 300; the inlet branch rises... enters from the '
      '-Y face at the mid-run x 500 (the old L1/L2 mid-run frame, W12) and sets into '
      'the run; the bend riser carries the line to the +Y outlet at z 600',
      'Drain boss under the run (flush at the envelope bottom, 50 datum); vent riser '
      'off the run flush at the envelope top (800 datum = the box top)',
      'CA 1.5 mm per the AQS-STD-001 hydrocarbon rule, carried in the procurement '
      'basis; the drawn wall is the Sch 40 table value'],
     "General arrangement, side elevation (end view). Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     [f'{R["nozzle_count_schedule"]} schedule rows of docs-authority/nozzles/'
      'C29_RECYCLE.csv at tag, face and bore',
      'N1 inlet on -Y at x 500 z 160; N2 outlet is the bend-riser branch at +Y z 600; '
      'N3 drain under the run at x 300; N4 vent riser at x 700',
      'Atmospheric tube joints (duty section 4: hose, atmospheric); the schedule '
      'rating column (Class 150) carried verbatim as text - no flange drawn '
      '(no process pressure stated, W4 110 % rule)'],
     "Connection orientation, top view. Tags/faces/bore per the schedule."),
    ("spool01", spool, (0, 1, 0),
     [f'Spool {S["dn"]} OD {S["od_mm"]:g} x wall {S["wall_mm"]:g} mm: x-run {L:g} mm, '
      'inlet branch, bend riser, +Y outlet branch; bores open, joints set-in welds',
      'Material carbon steel tube (duty section 3, line class M2); the piped bore is '
      'the AQS-PIP-004 line DN (DN15 both C29 lines), not recalculated',
      'The routed run (2.4 m + 6.8 m per AQS-PIP-004) stays in the line-list route '
      'lengths; the model draws the in-envelope run'],
     "Fabricated part sheet: spool run + bend riser + branches."),
    ("aux01", aux, (1, -0.5, 0.7),
     ['Trough plinth 1000 x 60 x 20 with two saddle stands (AQS-MOD-002 dry service '
      'class); 4 M10 slab anchors in fasteners.csv',
      'Drain and vent as DN15 open-bore tube stubs off the run',
      'The line list of record is line_list.csv: 3 rows (MAIN spool + the 2 issued '
      'lines C29_RECYCLE and C29_TO_PYRO), generated from the graph edges and '
      'AQS-PIP-004; no new edge'],
     "Fabricated part sheet: supports, drain and vent hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: C29 heavy cut in on -Y, out on +Y at the outlet datum to '
      'OIL_PYRO; drain at the tray line, vent riser at the box top',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/' + 'c29_recycle' + '.step) is the solids of record',
      'Spool cut, join, support, line list - the F-PIPE operations; leak test of the '
      'assembled run'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/c29_recycle.py", f"models/mfg/{unit}/draw_c29_recycle.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/line_list.csv", f"models/mfg/{unit}/check.json",
     f"models/mfg/{unit}/WORK_ORDER.md"],
    ['- A-PIPE: line_list.csv 3 rows (MAIN spool + C29_RECYCLE + C29_TO_PYRO), '
     'tag/from/to/DN/class/service/rating; edge coverage complete; no new edge',
     '- Schedule datums draw as issued: 160 inlet and 600 outlet fit the 800 box; '
     'drain flush at the envelope bottom (50 datum); vent riser flush at the box top '
     '(800 datum) (holds, W12)',
     '- Supports: trough plinth + 2 saddle stands + 4 slab anchors (the HDR_CO2 '
     'idiom at the schedule datum height)'],
    "A-core + A-PIPE")

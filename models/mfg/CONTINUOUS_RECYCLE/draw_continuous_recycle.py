"""CONTINUOUS_RECYCLE drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient (the branch layout along the run),
spool01 (run + plinth), aux01 (branch connections), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets, step_export  # noqa: E402

ns = runpy.run_path(HERE / "continuous_recycle.py")
parts, R = ns["parts"], ns["report"]
unit = "CONTINUOUS_RECYCLE"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else s.union(s)
    return u


spool = union_all([parts["spool"], parts["plinth"]])
aux = parts["nozzles"]
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
S = R["spool"]
LL = R["line_list"]
X = R["nozzles_drawn"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm envelope - the node size_mm (study registry '
      'box, per its size_note)',
      f'Spool {S["dn"]} OD {S["od_mm"]:g}, wall {S["wall_mm"]:g} mm (Sch 40 table; '
      'schedule not stated on the node - hold, W12), PVC-U per duty section 3',
      'The run sits welded in the trough plinth to its centreline (the HDR_CO2 '
      'idiom); 6 M10 slab anchors',
      f'{S["run_basis"]}'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Cross-section: the run at the centre of the 60 mm box (y 30, z 30)',
      'The DN50 schedule rows N1/N2 seat the 60 mm cross-section at the section '
      'centre: 0.15 mm per side outside the box, inside the 1 mm house gate, '
      'reported in check.json (hold, W12)',
      'Branch stubs flush at the envelope faces; atmospheric joints (duty section 4)'],
     "General arrangement, side elevation (end view). Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     [f'{R["nozzle_count_schedule"]} schedule rows of docs-authority/nozzles/'
      'CONTINUOUS_RECYCLE.csv at tag, face and bore',
      'N1 (DN50 raffinate) in on -Y at x 400 and N5 (DN15 polish-bank return) in on '
      '-Y at x 700 (its 160 datum clamped to 48.65 in the 60 mm section); N2 (DN50 '
      'recycle liquor) out on +Y at x 1100',
      'N3 drain flush at the envelope bottom (x 1300); N4 vent flush at the top '
      '(x 200; the 800 datum is the placeholder above the section)',
      'The DN50 hand rows stand against the DN15 issued lines (AQS-PIP-004); drawn '
      'verbatim, no bore claim - bores are not recalculated (AQS-PIP-003 basis, W12)'],
     "Branch orientation, top view. Tags/faces/bore per the schedule."),
    ("spool01", spool, (0, 1, 0),
     [f'Spool {S["dn"]} OD {S["od_mm"]:g} x wall {S["wall_mm"]:g} mm, 1500 mm '
      'in-envelope run; bore open at both spool ends',
      'Material PVC-U tube (duty section 3, rules M1 and M2, no metal wetted part); '
      'CA does not apply to the polymer; above 60 C the thermoplastic is CPVC - '
      'the line temperature is not on the graph (hold, W12)',
      'Trough plinth: the spool mount, the HDR_CO2 idiom'],
     "Fabricated part sheet: spool + trough plinth."),
    ("aux01", aux, (0, 1, 0),
     ['Branch connections DN15/DN50 as open-bore tube stubs, flush at the envelope '
      'faces; atmospheric per duty section 4; the schedule rating column (Class 150) '
      'is carried verbatim as text (no flange drawn - no process pressure stated)',
      'All 5 schedule rows present at tag, face, height and bore; clamped datums and '
      'per-tag positions in check.nozzles_drawn',
      'The line list of record is line_list.csv: 3 rows (MAIN spool + the 2 issued '
      'lines IA-POL-02 and IA-REC-01), generated from the graph edges and '
      'AQS-PIP-004; no new edge'],
     "Fabricated part sheet: branch connection hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: polish-bank return in on -Y, recycle liquor out on +Y to '
      'LEACH_CSTR_1; drain and vent at the run ends',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/' + 'continuous_recycle' + '.step) is the solids of record',
      'Spool cut, join, support, line list - the F-PIPE operations; leak test of '
      'the assembled run'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/continuous_recycle.py", f"models/mfg/{unit}/draw_continuous_recycle.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/line_list.csv", f"models/mfg/{unit}/check.json",
     f"models/mfg/{unit}/WORK_ORDER.md"],
    ['- A-PIPE: line_list.csv 3 rows (MAIN spool + IA-POL-02 + IA-REC-01), '
     'tag/from/to/DN/class/service/rating; edge coverage complete; no new edge',
     '- The DN50 hand rows N1/N2 drawn verbatim against the DN15 issued lines; they '
     'seat the 60 mm cross-section with 0.15 mm per side outside the box, inside the '
     '1 mm house gate (holds, W12)',
     '- PVC-U per duty section 3; above 60 C the thermoplastic is CPVC - the line '
     'temperature is not on the graph (hold, W12)'],
    "A-core + A-PIPE")

"""HDR_H2 drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient (the branch layout along the run),
spool01 (manifold), aux01 (branch connections), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets                                       # noqa: E402

ns = runpy.run_path(HERE / "ncg_header.py")
parts, R = ns["parts"], ns["report"]
unit = "NCG_HEADER"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


spool = union_all([parts["manifold"], parts["plinth"]])
aux = parts["nozzles"]
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
S = R["spool"]
LL = R["line_list"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm envelope - the node size_mm ({R["size_basis"]}), '
      'filled exactly',
      f'Manifold spool {S["dn"]} OD {S["od_mm"]:g}, wall {S["wall_mm"]:g} mm (Sch 40 '
      'table; schedule not stated on the node - hold, W12), bore open both ends, 304L '
      'heat-traced (node design; duty section 3 carries the carbon-steel text - '
      'material basis conflict, hold W12)',
      f'{S["run_basis"]}',
      'Trough plinth 2000 x 50 x 20 (AQS-MOD-002 dry service); 8 M10 slab anchors'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Cross-section: the manifold sits at the centre of the 50 mm box and sits bonded '
      'in the trough plinth to its centreline',
      f'AQS-DUTY-075 sizing: required bore {S["id_grid_mm"]:g} mm at 8 m/s, seat minimum '
      f'{S["dn"]}; the Sch 40 bore {S["id_mm"]:g} mm seats the same DN; nothing resized',
      'Branch stubs flush at the envelope faces; duty section 4 table: atmospheric '
      'lines are hose, DN copied from the edge and not recalculated'],
     "General arrangement, side elevation (end view). Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     ['4 schedule rows of docs-authority/nozzles/NCG_HEADER.csv at tag, face and bore',
      'N1 inlet on -Y and N2 outlet on +Y, drawn at 11.3 mm (schedule datums 10 mm '
      'clamped up for the branch bore); the duty section 4 table datums (400 mm, seed '
      'block xyz) predate the issued schedule - hold W12',
      'N3 drain flush at the envelope bottom, N4 vent flush at the top',
      'The issued AQS-PIP-004 rows carry DN15 class P3 (PVDF, process vent gas); the '
      'manifold is the node 304L - the transition joint at the header face is the '
      'connection detail (hold W12)'],
     "Branch orientation, top view. Tags/faces/bore per the schedule."),
    ("spool01", spool, (0, 1, 0),
     [f'Manifold {S["dn"]} OD {S["od_mm"]:g} x wall {S["wall_mm"]:g} mm, 2000 mm '
      'representative spool of the 20 m run; bore open at both spool ends',
      'Material 304L (node design: heat-traced, tar service); CA 0 mm (AQS-STD-001 '
      'stainless rule); duty section 3 carries the carbon-steel text with a 1.5 mm '
      'allowance - material basis conflict named (hold W12); the heat tracing is a '
      'purchased cable, named in the BOM, not drawn',
      'Trough plinth: the spool mount carried from the HDR_CO2 acceptance'],
     "Fabricated part sheet: manifold + trough plinth."),
    ("aux01", aux, (0, 1, 0),
     ['Branch connections DN15 as open-bore tube stubs, flush at the envelope faces; '
      'duty section 4 table: atmospheric lines are hose; the schedule rating column '
      '(Class 150) is carried verbatim as text (no flange drawn - no process pressure '
      'stated)',
      'All 4 schedule rows present at tag, face, height and bore; clamped datums and '
      'per-tag positions in check.nozzles_drawn',
      'The line list of record is line_list.csv: 3 rows (manifold + 2 issued lines), '
      'generated from the graph edges and AQS-PIP-004; no new edge'],
     "Fabricated part sheet: branch connection hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: the fractionator NCG inlet on -Y, the afterburner feed on '
      '+Y; drain and vent at the run midpoint',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/hdr_h2.step) is the solids of record',
      'Tracker --check green on every gate except the reported DN50 cross-section '
      'misfit; acceptance A-core + A-PIPE per AQS-PLAN-006 section 5'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/ncg_header.py", f"models/mfg/{unit}/draw_ncg_header.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/line_list.csv", f"models/mfg/{unit}/check.json",
     f"models/mfg/{unit}/WORK_ORDER.md"],
    [f"- A-PIPE line list: line_list.csv generated from the unit's graph edges and "
     f"docs-authority/LINE_LIST.md (AQS-PIP-004): {LL['rows']} rows (manifold spool + "
     f"{LL['rows'] - 1} lines), tag/from/to/DN/class/service/rating; edge coverage "
     f"complete, no new edge",
     "- Spool: DN25 OD 33.7 x wall 3.38 (Sch 40 table), bore 26.9 mm inside the 4.3 "
     "mm DN-8 sizing grid seat (AQS-DUTY-075); nothing resized; 304L heat-traced "
     "(node design), the tracing a purchased cable named in the BOM",
     "- Build fills the envelope exactly; cad/stl replaced from the build",
     "- Material basis conflict named: duty section 3 carries the carbon-steel text "
     "with a 1.5 mm allowance, the node design says 304L; 304L drawn, both facts "
     "recorded (hold, W12)",
     "- Schedule datums clamped into the 50 mm cross-section: the DN15 datums 10 to "
     "11.3 mm (holds, W12); the duty table datums (400 mm) predate the schedule"],
    "A-core + A-PIPE")

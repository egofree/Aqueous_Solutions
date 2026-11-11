"""HDR_O2 drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient (the branch layout along the run),
spool01 (manifold), aux01 (branch connections), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets, step_export  # noqa: E402

ns = runpy.run_path(HERE / "hdr_o2.py")
parts, R = ns["parts"], ns["report"]
unit = "HDR_O2"


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
     [f'Keys: {L:g} x {W:g} x {H:g} mm envelope - the node size_mm ({R["size_basis"]}); '
      'the 60.3 mm cross-section is the AQS-DUTY-075 reservation (flow_graph/param/'
      'headers.py), sized to cover the DN50 branch hardware drawn at the manifold '
      'centreline (2026-11-08 reservation adoption - the assembly fits)',
      f'Manifold spool {S["dn"]} OD {S["od_mm"]:g}, wall {S["wall_mm"]:g} mm (Sch 40 '
      'table; the M1 class sheet carries the schedule at order - hold, W12), bore open '
      'both ends, 316L tube oxygen-clean per ASTM G93, socketless',
      f'{S["run_basis"]}',
      'Trough plinth 2000 x 50 x 20 (AQS-MOD-002 dry service); 8 M10 slab anchors'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Cross-section: the manifold sits at the centre of the 60.3 mm cross-section '
      'and sits welded in the trough plinth to its centreline',
      f'AQS-DUTY-075 sizing: required bore {S["id_grid_mm"]:g} mm at 8 m/s, seat minimum '
      f'{S["dn"]}; the Sch 40 bore {S["id_mm"]:g} mm seats the same DN; nothing resized',
      'The DN50 branch circle (OD 60.3) sits inside the 60.3 mm cross-section: the '
      'reservation is sized to the largest issued branch (headers.py, AQS-DUTY-075; '
      '2026-11-08 reservation adoption)'],
     "General arrangement, side elevation (end view). Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     ['12 schedule rows of docs-authority/nozzles/HDR_O2.csv at tag, face and bore',
      'N1 DN25 inlet on -Y drawn at 17.5 mm (datum 10 clamped up); N8 DN50 drawn at the '
      'manifold centreline - the OD 60.3 hardware sits inside the 60.3 mm reservation '
      'cross-section (headers.py, AQS-DUTY-075; 2026-11-08 reservation adoption)',
      'N2/N4/N5 DN15 outlets at their 37 mm datum; N3 DN25 outlet clamped down to '
      '32.4 mm; N9/N10/N12 outlets and the N11 no-bore row (DN15 drawn, bore not '
      'calculated) clamped down from the 600 mm datum',
      'N6 drain flush at the bottom, N7 vent flush at the top; oxygen-clean per '
      'ASTM G93, socketless (duty section 3)'],
     "Branch orientation, top view. Tags/faces/bore per the schedule."),
    ("spool01", spool, (0, 1, 0),
     [f'Manifold {S["dn"]} OD {S["od_mm"]:g} x wall {S["wall_mm"]:g} mm, 2000 mm '
      'representative spool of the 20 m run; bore open at both spool ends',
      'Material 316L tube (duty section 3); CA 0 mm (AQS-STD-001 rule); the M1 class '
      'sheet (AQS-PIP-003) carries the schedule at order and cleans its O2 lines per '
      'ASTM G93 (degreased and bagged; PTFE seats, no oil)',
      'Trough plinth: the spool mount carried from the HDR_CO2 acceptance'],
     "Fabricated part sheet: manifold + trough plinth."),
    ("aux01", aux, (0, 1, 0),
     ['Branch connections DN15/DN25/DN50 as open-bore tube stubs, flush at the envelope '
      'faces; atmospheric per duty section 4; the schedule rating column (Class 150) '
      'is carried verbatim as text (no flange drawn - no process pressure stated)',
      'All 12 schedule rows present at tag, face, height and bore; clamped datums, the '
      'DN50 centreline placement and per-tag positions in check.nozzles_drawn',
      'Socketless joints per duty section 3; the no-oil rule of AQS-STD-002 applies to '
      'every take-off',
      'The line list of record is line_list.csv: 9 rows (manifold + 8 issued lines), '
      'generated from the graph edges and AQS-PIP-004; no new edge'],
     "Fabricated part sheet: branch connection hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: the ASU O2 product and makeup inlets on -Y, the fuel-cell, '
      'peroxide, genset and afterburner draws on +Y; drain and vent at the run midpoint',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/hdr_o2.step) is the solids of record',
      'Tracker --check green on every gate - the reservation cross-section covers the '
      'DN50 branch hardware (headers.py, AQS-DUTY-075; 2026-11-08 reservation '
      'adoption); acceptance A-core + A-PIPE per AQS-PLAN-006 section 5'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/hdr_o2.py", f"models/mfg/{unit}/draw_o2.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/line_list.csv", f"models/mfg/{unit}/check.json",
     f"models/mfg/{unit}/WORK_ORDER.md"],
    [f"- A-PIPE line list: line_list.csv generated from the unit's graph edges and "
     f"docs-authority/LINE_LIST.md (AQS-PIP-004): {LL['rows']} rows (manifold spool + "
     f"{LL['rows'] - 1} lines), tag/from/to/DN/class/service/rating; edge coverage "
     f"complete, no new edge",
     "- Spool: DN25 OD 33.7 x wall 3.38 (Sch 40 table; the M1 class sheet carries the "
     "schedule at order), bore 26.9 mm inside the 7.1 mm DN-8 sizing grid seat "
     "(AQS-DUTY-075); nothing resized; oxygen-clean per ASTM G93, socketless",
     "- Reservation adoption (2026-11-08): headers.py (AQS-DUTY-075) sizes the "
     "reservation cross-section to the largest issued branch hardware (60.3 mm, the "
     "EN-rounded OD series); the DN50 branch row N8 draws inside it at the manifold "
     "centreline, the build reads 2000 x 60.3 x 60.3 against the same reservation, "
     "no misfit carried; oxygen-clean per ASTM G93, socketless",
     "- Schedule datums clamped into the 60.3 mm cross-section: the DN25 inlet 10 to "
     "17.5 mm, the DN25 37 mm outlet datum to 32.4 mm, the 160/600 mm placeholder "
     "datums down (holds, W12); N11 drawn DN15, bore not calculated (plan W4)"],
    "A-core + A-PIPE")

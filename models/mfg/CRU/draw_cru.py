"""CRU drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, ves01 (vessel shell), frame01
(hold-down frame + plinth), aux01 (connection hardware), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets, step_export  # noqa: E402

ns = runpy.run_path(HERE / "cru.py")
parts, R = ns["parts"], ns["report"]
unit = "CRU"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


ves = parts["vessel"]
frame = union_all([parts["plinth"], parts["frame"]])
aux = parts["nozzles"]
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
V = R["vessel"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm envelope - the node size_mm ({R["size_basis"]})',
      'Vertical PVC-U chlorate-finish vessel drawn to the node envelope: shell '
      'OD 520 (the duty states no diameter - drawn to the envelope, hold W12), '
      'wall 10 (study, hold W12), welded top and bottom, on a seat over the '
      '20 mm plinth',
      'Four-post hold-down frame pins the registry box so the build fills the '
      'envelope (X-PAR-04)',
      'Material PVC-U per duty section 3 (AQS-STD-002 rules M1 and M2; no metal '
      'wetted part); CA does not apply to the polymer'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Vessel z 40..680; the graph gives no temperature for this unit - above '
      '60 C the thermoplastic is CPVC, never metal (duty section 3, hold W12)',
      f'A-VES holdup report: the vessel holds {V["holdup_model_l"]:g} L to 100 mm '
      'below the top weld; the duty states no holdup basis for this class, so no '
      'residence time is derived',
      'Duty basis: scrub liquor in to chlorate finish, cell-gas sparges in, '
      'chlorine out to the fluoro trains (VDF_SYN/TFE_SYN), liquor returned to '
      'leach'],
     "General arrangement, side elevation (end view). Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     ['12 schedule rows of docs-authority/nozzles/CRU.csv at tag, face and bore',
      'Inlets on -Y at z 160: N1 DN25 (scrub liquor), N5-N8 DN15 (the cell-gas '
      'sparges: Ti/MO/AL/MG pot gas), N11/N12 DN15 (the fluoropolymer HCl '
      'returns); outlets on +Y at z 600: N2 DN25 (sodium chlorate liquor), N9/N10 '
      'DN15 (chlorine to VDF_SYN/TFE_SYN)',
      'N3 drain flush at the envelope bottom (50 datum); N4 vent flush at the '
      'envelope top (800 datum is the box top)',
      'Atmospheric open-bore tube stubs per duty section 4 (nozzle DN15, no '
      'flange class); the gas rows stay on their gas edges, not the room; the '
      'schedule rating column (Class 150) carried verbatim as text'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("ves01", ves, (0, 1, 0),
     [f'Vessel shell OD {V["od_mm"]:g} x wall {V["wall_mm"]:g} (study), z '
      f'{V["z_mm"][0]:g}..{V["z_mm"][1]:g}, welded top and bottom, seat to the '
      'plinth',
      'Shell drawn to the node envelope; no vessel diameter or wall is stated on '
      'the node or duty (holds, W12)',
      'PVC-U welds per the unit route (F-VES applied to the thermoplastic shop: '
      'DVS 2207 class practice); CA does not apply to the polymer'],
     "Fabricated part sheet: PVC-U vessel."),
    ("frame01", frame, (0, 1, 0),
     ['Four-post hold-down frame (40 x 40 posts, top rails) + plinth '
      f'{L:g} x {W:g} x 20 (AQS-MOD-002 dry service)',
      'The frame pins the registry box so the build fills the node envelope '
      '(X-PAR-04); 8 M12 slab anchors (fasteners.csv)',
      'Carbon steel (ASTM A500); the frame is dry structure outside the wet '
      'vessel'],
     "Fabricated part sheet: hold-down frame + plinth."),
    ("aux01", aux, (0, 1, 0),
     ['Connection hardware DN15/DN25 as open-bore tube stubs flush at the '
      'envelope faces; atmospheric per duty section 4 (no flange class)',
      'All 12 schedule rows present at tag, face, height and bore; per-tag '
      'positions in check.nozzles_drawn',
      'The six gas rows (cell gas in, chlorine out) stay on their gas edges, not '
      'the room (duty sections 5 and 6); the schedule rating column (Class 150) '
      'is carried verbatim as text'],
     "Fabricated part sheet: connection hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: liquor and gas in on -Y, chlorate liquor and chlorine '
      'out on +Y; drain at the bottom, vent at the top',
      f'Graph revision {R["graph_revision"]} is the model authority for this '
      'build; STEP (export/cru.step) is the solids of record',
      'Tracker --check green; acceptance A-core + A-VES per AQS-PLAN-006 '
      'section 5'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/cru.py", f"models/mfg/{unit}/draw_cru.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ["- Vessel: vertical PVC-U shell OD 520, wall 10 (study - the duty states no "
     "diameter and no wall: drawn to the envelope, holds W12), welded top and "
     "bottom, on a seat over a 20 mm plinth inside a four-post hold-down frame",
     "- A-VES: the vessel holds 104.1 L to 100 mm below the top weld; the duty "
     "states no holdup basis for this class, so no residence time is derived",
     "- Material per duty section 3: PVC-U wetted (AQS-STD-002 rules M1 and M2; "
     "no metal wetted part); the temperature watch is carried as a named hold "
     "(above 60 C the thermoplastic is CPVC, never metal; the graph gives no "
     "temperature for this unit)"],
    "A-core + A-VES")

"""GLASS_MILL drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, jar01 (mill jar), stands01 (plinth +
roll stands), aux01 (connection hardware), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets                                       # noqa: E402

ns = runpy.run_path(HERE / "glass_mill.py")
parts, R = ns["parts"], ns["report"]
unit = "GLASS_MILL"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


jar = parts["jar"]
stands = union_all([parts["plinth"], parts["stands"]])
aux = parts["nozzles"]
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
M = R["machine"]
LL = R["line_list"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm envelope - the node size_mm ({R["size_basis"]})',
      'Jar mill: 316L jar OD 350 x 500, wall 8 mm (study - hold, W12), on trunnion '
      'journals in two V-roll cradle stands over the 20 mm plinth (ported AQS-MFG-001 '
      'form mfg_mill.scad)',
      f'Jar-full volume {M["v_full_m3"]:g} m3 against the duty section 2 seven-day '
      f'charge {M["charge_duty_m3"]:g} m3: reported, nothing resized (plan rule 3)',
      'Material 316L (duty section 3); CA 0 mm (AQS-STD-001 rule)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Jar axis at y 300, z 430; end journals run in V-rolls on pedestal cross-beams',
      'Media charge not drawn: the node carries internals none (hold, W12); jar drive '
      'not designed - no drive named on the node or duty',
      'Carbon-steel stands and plinth (AQS-MOD-002 dry service); 8 slab anchors, '
      '4 roll-shaft bolts (fasteners.csv)'],
     "General arrangement, side elevation (end view). Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     ['6 schedule rows of docs-authority/nozzles/GLASS_MILL.csv at tag, face and bore',
      'N1 DN25 (rinsed cullet) and N6 solids (spent ceramic shell, drawn DN15 bore '
      'not calculated per plan W4) on -Y at z 160; N2 DN25 (milled cullet) and N3 '
      'DN15 (mill dust to the baghouse) on +Y at z 600',
      'N4 drain flush at the envelope bottom (50 datum); N5 vent flush at the '
      'envelope top (800 datum is the box top)',
      'Atmospheric hose barbs per duty section 4; the schedule rating column (Class '
      '150) is carried verbatim as text, no flange drawn (no process pressure stated)'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("jar01", jar, (0, 1, 0),
     [f'Mill jar OD {M["jar_od_mm"]:g} x {M["jar_len_mm"]:g}, wall {M["wall_mm"]:g} mm '
      '(study value - no authority states a jar wall, hold W12)',
      'End heads 8 mm; trunnion journals pierce the end heads at the jar axis',
      '316L per duty section 3; CA 0 mm (AQS-STD-001 316L rule)'],
     "Fabricated part sheet: mill jar."),
    ("stands01", stands, (0, 1, 0),
     ['Plinth 800 x 600 x 20 (AQS-MOD-002 dry service) + two cradle stands: '
      '180 x 160 base, cross-beam, two OD 70 V-rolls per stand',
      'Roll fit and pedestal depths are study proportions, confirmed at fabrication '
      '(hold, W12)',
      'Carbon steel (ASTM A500); fasteners per the W5 grade rule'],
     "Fabricated part sheet: plinth + roll stands."),
    ("aux01", aux, (0, 1, 0),
     ['Connection hardware DN15/DN25 as atmospheric hose barbs flush at the envelope '
      'faces (lib/nozzles.py); barb profile a study proportion, finished against the '
      'hose supplier print',
      'All 6 schedule rows present at tag, face, height and bore; per-tag positions '
      'in check.nozzles_drawn',
      f'The A-PIPE line list of record is line_list.csv: {LL["rows"]} rows generated '
      'from the unit edges and AQS-PIP-004; no new edge'],
     "Fabricated part sheet: connection hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: cullet and spent shell in on -Y, milled cullet out to the '
      'burnout and mill dust out to the baghouse on +Y; drain and vent on the run '
      'centreline',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/glass_mill.step) is the solids of record',
      'Tracker --check green; acceptance A-core + A-PIPE per AQS-PLAN-006 section 5'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/glass_mill.py", f"models/mfg/{unit}/draw_glass_mill.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/line_list.csv", f"models/mfg/{unit}/check.json",
     f"models/mfg/{unit}/WORK_ORDER.md"],
    [f"- A-PIPE line list: line_list.csv generated from the unit's graph edges and "
     f"docs-authority/LINE_LIST.md (AQS-PIP-004): {LL['rows']} rows, "
     "tag/from/to/DN/class/service/rating; edge coverage complete, no new edge",
     "- Machine: jar mill OD 350 x 500, wall 8 (study), on V-roll cradle stands; "
     "jar-full 0.0438 m3 against the 0.2577 m3 duty section 2 seven-day charge - "
     "reported, nothing resized (plan rule 3); media charge not drawn (node "
     "internals none)"],
    "A-core + A-PIPE")

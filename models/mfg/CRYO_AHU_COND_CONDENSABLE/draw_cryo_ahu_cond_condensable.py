"""CRYO_AHU_COND_CONDENSABLE drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the
accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, vessel01 (shell + heads), weir01 (weir +
launder layout solids), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets, step_export  # noqa: E402

ns = runpy.run_path(HERE / "cryo_ahu_cond_condensable.py")
parts, R = ns["parts"], ns["report"]
unit = "CRYO_AHU_COND_CONDENSABLE"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


vessel = union_all([parts["shell"], parts["plinth"]])
weir = union_all([parts["weir"], parts["launder"]])
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
M = R["machine"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm envelope - the node size_mm (the study '
      'registry box; the duty section 4 / seed 600 x 400 x 600 figures predate '
      'it - the node governs, hold W12)',
      'Condensable knock-out vessel per the duty section 3 material row (316L, '
      'condensation, no carbon steel), in the FLUE_KO weir/launder idiom '
      '(FLOAT_SINK/FLUE_KO family)',
      'Vertical 316L drum OD 540 (wall 8, study) with laps-to-plinth base head '
      'and top head; the IA-AHU-POT condensable slip (0.0521 kg/d) condenses '
      'against the cooled shell; S70 leaves above the weir',
      'Route hold carried by name: the node class is blank - no section 4 class '
      '(AFTERBURNER_FLUE/REE_RECOVER precedent)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Weir plate at the shell centreline (to z 360) divides settle from '
      'overflow; launder trough at the +X side, lip top z 360 (layout solids, '
      'study - hold W12)',
      'Sump volume below the weir lip computed from the model and reported in '
      'check.json (A-VES-style report); the duty claims no holdup - no residence '
      'time derived',
      'Duty section 8: no holdup basis - the separation duty stays unsized'],
     "General arrangement, side elevation (end view). Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     ['4 schedule rows of docs-authority/nozzles/CRYO_AHU_COND_CONDENSABLE.csv at '
      'tag, face and bore',
      'N1 condensable slip in on -Y at z 160; N2 condensables out on +Y at z 600 '
      '- atmospheric hose barbs flush at the envelope faces (rows read "Bore not '
      'calculated. Rating hose, atmospheric")',
      'N3 drain flush at the envelope bottom (50 datum); N4 vent flush at the '
      'envelope top (800 datum = box top)',
      'No flange (W4 110 % rule); the schedule rating column carried verbatim'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("vessel01", vessel, (0, 1, 0),
     ['Shell OD 540 (wall 8, study) with laps-to-plinth base head and top head',
      '316L per duty section 3 (condensation, no carbon steel); CA 0 mm '
      '(AQS-STD-001 316L rule)',
      'Shell dimensions are study values - no authority states a thickness '
      '(hold, WORK_ORDER W12)'],
     "Fabricated part sheet: shell + heads + plinth."),
    ("weir01", weir, (0, 1, 0),
     ['Weir plate at the shell centreline (x 420..430, to z 360): settle zone '
      'from the -Y side, overflow zone toward the launder',
      'Launder trough at the +X side: channel floor z 300..310, lip plates to '
      'an overflow lip top z 360 (FLUE_KO idiom; layout solids, study - hold W12)',
      'The condensables (S70) leave above the weir lip'],
     "Fabricated part sheet: weir + launder layout solids."),
    ("iso01", full, (1, -1, 1),
     ['Plant orientation: condensable slip in on -Y from the AHU, condensables '
      'out on +Y to the S70 line',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/cryo_ahu_cond_condensable.step) is the solids of record',
      'Tracker --check green; acceptance A-core per AQS-PLAN-006 section 5 '
      '(route hold: the node class is blank)'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/cryo_ahu_cond_condensable.py",
     f"models/mfg/{unit}/draw_cryo_ahu_cond_condensable.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ["- Condensable knock-out vessel per the duty section 3 row (316L, "
     "condensation, no carbon steel) in the FLUE_KO weir/launder idiom: drum OD "
     "540 (wall 8, study), weir plate to z 360, launder trough lip top z 360",
     "- Route hold carried by name: the node class is blank - no section 4 "
     "class (AFTERBURNER_FLUE/REE_RECOVER precedent); the duty/seed 600 x 400 "
     "x 600 figures predate the node study box (hold, W12)",
     "- Sump volume reported from the model (A-VES-style report, no residence "
     "time derived - duty section 8 has no holdup basis); hose-barb nozzles per "
     "the schedule (bores not calculated, hose, atmospheric)"],
    "A-core")

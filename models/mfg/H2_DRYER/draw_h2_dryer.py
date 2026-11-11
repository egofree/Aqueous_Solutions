"""H2_DRYER drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, vessel01 (dryer vessel + insulation +
heater envelope), beds01 (bed tubes + media envelopes), aux01 (KO pot + guard
frame + plinth + hardware), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets, step_export  # noqa: E402

ns = runpy.run_path(HERE / "h2_dryer.py")
parts, R = ns["parts"], ns["report"]
unit = "H2_DRYER"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


vessel = union_all([parts["vessel"], parts["insulation"], parts["heater"]])
beds = union_all([parts["beds"], parts["media"]])
aux = union_all([parts["ko_pot"], parts["frame"], parts["plinth"], parts["nozzles"]])
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
M = R["machine"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm envelope - the node size_mm ({R["size_basis"]})',
      'H2 dryer skid per the node design block: dryer vessel OD 60.3 x 628 (wall '
      '3.91, 316L annealed per M6/AQS-REV-H2-001) with 38 mm insulation; 2 deoxo '
      'DN25 x 328; 2 guard DN25 x 300; 2 TSA DN50 x 300 with sieve envelopes',
      'A-MACH guard: four-post frame (30 x 30 posts, top rail) pins the envelope; '
      '8 slab anchors in fasteners.csv',
      'Inlet knock-out pot in PVC-U per duty section 3 (wet side); the dryer '
      'vessel and dry outlet are 316L annealed (M6, dry H2)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Bed stations on the z 120 seat: KO pot x 60, deoxo x 150, guard x 220, TSA '
      'x 300, dryer vessel x 450 - the layout choice (W12); the design names '
      'components and counts, not arrangement',
      'Regeneration heater envelope at the vessel base (1.03 W, node regen_W, '
      'purchased per plan rule 6)',
      'Design duty: 1.975 kg/d H2 at the 250 C class; regeneration conditions '
      'held per the duty'],
     "General arrangement, side elevation (end view). Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     ['9 schedule rows of docs-authority/nozzles/H2_DRYER.csv at tag, face and bore',
      'N1 (process H2 in) on -Y at z 160; N2 (process H2 out), N5 (H2 relief '
      'contingency, S24), N6 (H2 normal path, S64), N7 (dried hydrogen - product '
      'gas edge, drawn DN15 bore not calculated per plan W4), N8 (sweep air) and '
      'N9 (TSA regeneration condensate) on +Y at z 600',
      'N3 drain flush at the envelope bottom (50 datum); N4 vent flush at the '
      'envelope top - the vent is S24 to RELIEF_H2 (duty section 6), destination '
      'named; the 800 datum is a placeholder under the 1028 box',
      'Atmospheric open-bore tube stubs per duty section 4 (no flange class); the '
      'schedule rating column (Class 150) carried verbatim as text'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("vessel01", vessel, (0, 1, 0),
     [f'Dryer vessel OD {M["vessel"]["od_mm"]:g} x {M["vessel"]["h_mm"]:g}, wall '
      f'{M["vessel"]["wall_mm"]:g} (the node design D_mm/H_mm/wall_mm)',
      f'Insulation {M["vessel"]["insulation_mm"]:g} mm (node insulation_mm); '
      'regeneration heater envelope at the base, 1.03 W (node regen_W, purchased '
      'per plan rule 6)',
      '316L annealed per duty section 3 (M6, dry H2, AQS-REV-H2-001); CA 0 mm '
      '(AQS-STD-001 316L rule)'],
     "Fabricated part sheet: dryer vessel + insulation + heater envelope."),
    ("beds01", beds, (0, 1, 0),
     ['Bed tubes per the design beds block: 2 deoxo DN25 x 328 (V_L 0.183 L '
      'charge, buy row, not drawn), 2 guard DN25 x 300, 2 TSA DN50 x 300',
      'Media envelopes inside: molecular sieve 0.353 kg in the TSA tubes, guard '
      'media 0.032 kg in the guard tubes (buy charges; bed envelopes drawn per '
      'plan rule 6)',
      'Tube lengths from the design L_mm; the media length is the bore between '
      '10 mm support-disc allowances (layout choice, hold W12)'],
     "Fabricated part sheet: bed tubes + media envelopes."),
    ("aux01", aux, (0, 1, 0),
     ['PVC-U inlet knock-out pot OD 60 x 120 (duty section 3: inlet knock-out '
      'PVC-U, wet)',
      'Guard frame per A-MACH: four 30 x 30 posts with top rail + plinth '
      f'{L:g} x {W:g} x 20 (AQS-MOD-002 dry service); 8 slab anchors',
      'Connection hardware DN15 as open-bore tube stubs flush at the envelope '
      'faces; all 9 schedule rows present at tag, face, height and bore '
      '(check.nozzles_drawn)'],
     "Fabricated part sheet: KO pot + guard frame + hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: wet H2 in on -Y, dried H2 and the relief contingency out '
      'on +Y (S24 to RELIEF_H2; S64 to CRYO_H2); drain and vent on the skid '
      'centreline',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/h2_dryer.step) is the solids of record',
      'Tracker --check green; acceptance A-core + A-MACH per AQS-PLAN-006 '
      'section 5'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/h2_dryer.py", f"models/mfg/{unit}/draw_h2_dryer.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ["- Skid per the node design block: dryer vessel OD 60.3 x 628, wall 3.91 "
     "(316L annealed per M6/AQS-REV-H2-001), 38 mm insulation; 2 deoxo DN25 x "
     "328, 2 guard DN25 x 300, 2 TSA DN50 x 300 bed tubes with media envelopes; "
     "PVC-U inlet KO pot (duty section 3)",
     "- A-MACH: guard frame drawn (four posts, top rail) and 8 anchors; purchased "
     "items named with the node ratings (heater 1.03 W regen_W; sieve 0.353 kg; "
     "guard media 0.032 kg; deoxo catalyst 0.183 L charges - buy rows)",
     "- The N4 vent is the S24 relief edge to RELIEF_H2 (duty section 6) with the "
     "destination named; the N7 solids row drawn DN15, bore not calculated "
     "(plan W4); bed stations are the layout choice (hold, W12)"],
    "A-core + A-MACH")

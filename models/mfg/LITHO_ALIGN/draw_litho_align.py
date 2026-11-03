"""LITHO_ALIGN drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, base01 (base plate + guard frame),
opt01 (stage, leadscrew, mask, LED head envelope), aux01 (envelope hardware),
iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets                                       # noqa: E402

ns = runpy.run_path(HERE / "litho_align.py")
parts, R = ns["parts"], ns["report"]
unit = "LITHO_ALIGN"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


base = union_all([parts["base"], parts["frame"]])
opt = union_all([parts["stage"], parts["leadscrew"], parts["mask_holder"],
                 parts["mask"], parts["led_head"]])
aux = parts["nozzles"]
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm envelope - the node size_mm '
      f'({R["size_basis"] or "node size_mm"}, AQS-LITH-001 rev C frame 6061)',
      'Duty section 2 prose carries the seed figure 500 x 500 x 800; the node '
      'governs and the older figure is named (hold W12, the WS_SOLV precedent)',
      'Contact aligner per the node design block and AQS-LITH-001 rev C: 365 '
      'nm LED array 1 W optical, 200 mJ/cm2 dose, 100 mm field; not a stepper',
      'Frame 6061 per AQS-LITH-001 section 3; duty section 3 has nothing to '
      'match (no wet stream: mass in and out are zero)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Stage aluminium; leadscrew 4140, 10 mm at 1 mm pitch, cut on the lathe '
      '(AQS-LITH-001 section 2); 10 um repeatability read by a dial, not an '
      'encoder',
      'Mask chrome on glass with the 100 um pattern, cut on the mill; the '
      'coating is not a solid',
      'Guard frame (6061, 40 x 40 posts + top rails) pins the registry box so '
      'the build fills the node envelope (X-PAR-04); 4 bench anchors'],
     "General arrangement, side elevation (end view). Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     ['2 schedule rows of docs-authority/nozzles/LITHO_ALIGN.csv: N1 drain '
      'flush at the envelope bottom (50 datum), N2 vent flush at the envelope '
      'top (800 datum is the box top)',
      "Duty section 4: 'No present edge. No nozzle.' - the two rows are the "
      'envelope hardware rows; atmospheric, hose',
      'The AQS-LITH-001 section 4 SB350 hose barb is the machine service '
      'interface, not a schedule row - named, not drawn (hold W12)'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("base01", base, (0, 1, 0),
     ['Base plate 1200 x 600 x 20 and guard frame (40 x 40 posts, top rails), '
       '6061 per AQS-LITH-001 section 3',
       'The frame pins the registry box so the build fills the node envelope '
       '(X-PAR-04); 8 M8 socket screws + 4 bench anchors (fasteners.csv)',
       'No plan grade rule covers aluminium joints: A4-70 stainless selected '
       'against galvanic action, confirmed at fabrication'],
     "Fabricated part sheet: base plate and guard frame."),
    ("opt01", opt, (1, -1, 1),
     ['Stage plate 160 x 160 x 15 (layout choice around the 100 mm field, '
       'W12); leadscrew x 140..940 at y 300; mask holder 200 x 200 x 8; '
       'mask glass 160 x 160 x 3',
       '365 nm LED array head envelope (120 x 120 x 60): purchased per plan '
       'rule 6, rating from the node design block (1 W optical)',
       'The stage, leadscrew and mask are shop-cut per AQS-LITH-001 section 2 '
       '(lathe and mill) - the make rows of the BOM'],
     "Machine parts: stage, leadscrew, mask, LED head envelope."),
    ("aux01", aux, (0, 1, 0),
     ['Envelope hardware DN15 tube stubs flush at the envelope faces; '
      'atmospheric hose per duty section 4 (no flange class)',
      'Both schedule rows present at tag, face and bore; per-tag notes in '
      'check.nozzles_drawn',
      'The schedule rating column (Class 150) carried verbatim as text'],
     "Fabricated part sheet: envelope hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: the exposure axis is vertical through mask and '
      'stage; the leadscrew drives the stage along x',
      f'Graph revision {R["graph_revision"]} is the model authority for this '
      'build; STEP (export/litho_align.step) is the solids of record',
      'Tracker --check green; acceptance A-core + A-SC (route hold: no '
      'section 4 class row names the aligner class) per AQS-PLAN-006 '
      'section 5'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/litho_align.py", f"models/mfg/{unit}/draw_litho_align.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ["- Contact aligner per the node design block and AQS-LITH-001 rev C "
     "(named on the node): 6061 frame and base, aluminium stage, 4140 "
     "leadscrew (shop lathe), chrome-on-glass mask (shop mill), and the 365 nm "
     "LED array envelope (1 W optical) as the purchased item per plan rule 6",
     "- Duty section 2 prose carries the seed figure 500 x 500 x 800; the node "
     "1200 x 600 x 800 governs, the older figure named (hold W12)",
     "- Guard frame pins the registry box so the build fills the envelope "
     "(X-PAR-04); anchors in fasteners.csv"],
    "A-core + A-SC (route hold)")

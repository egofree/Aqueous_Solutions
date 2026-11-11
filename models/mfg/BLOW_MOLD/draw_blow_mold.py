"""BLOW_MOLD drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, frame01 (base + guard frame),
melt01 (316L melt path: barrel, head, die), groups01 (drive, clamp, mold, air
envelopes), aux01 (connection hardware), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets, step_export  # noqa: E402

ns = runpy.run_path(HERE / "blow_mold.py")
parts, R = ns["parts"], ns["report"]
unit = "BLOW_MOLD"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


frame = union_all([parts["base"], parts["frame"]])
melt = union_all([parts["barrel"], parts["head_die"]])
groups = union_all([parts["drive"], parts["clamp_platens"], parts["mold"],
                    parts["air"]])
aux = parts["nozzles"]
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm envelope - the node size_mm '
      f'({R["size_basis"] or "node size_mm"}); the duty section 2 envelope '
      'line agrees with the node',
      'Continuous-extrusion blow molder per the node design block (Precious '
      'Plastic class; AQS-EQP-MFG-001; A-M-285): 316L melt path, purchased '
      'drive groups by node rating, mold tool envelope between the platens',
      'Process figures are node figures: 2.8 kg/h at 3.0 h/d on the 8.407 '
      'kg/d wax feed; products to MFG_SHOP, scrap to OIL_FRAC',
      'Melt path 316L per duty section 3 (the wax melt is the wet service); '
      'CA 0 mm (AQS-STD-001)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Purchased drive groups per plan rule 6 with the node ratings: '
      'extruder 2.2 kW (extruder_kW), clamp 0.75 kW (BLOW-CLAMP-01), air '
      '0.75 kW (BLOW-AIR-01)',
      'The article geometry is not named on the node - the mold set '
      '(BLOW-MOLD-TOOL-01) is an envelope and the mold detail is a hold '
      '(WORK_ORDER W12)',
      'Guard frame (40 x 40 posts + top rails) pins the registry box so the '
      'build fills the node envelope (X-PAR-04); 8 slab anchors'],
     "General arrangement, side elevation (end view). Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     ['4 schedule rows of docs-authority/nozzles/BLOW_MOLD.csv at tag, face '
      'and bore',
      'N3 (C11-C18 to the mold) at x 600 on -Y at z 160; N4 (blown parts) at '
      'x 660 on +Y at z 600 - both solids transfer rows drawn DN15, bore not '
      'calculated (plan W4)',
      'N1 drain flush at the envelope bottom (50 datum); N2 vent flush at the '
      'envelope top - its 800 datum predates the 1600 box (hold W12)',
      'Atmospheric hose per duty section 4 (no flange class)'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("frame01", frame, (0, 1, 0),
     ['Base plate and guard frame (40 x 40 posts, top rails), carbon steel '
       'A500 (AQS-MOD-002 dry service)',
       'The frame pins the registry box so the build fills the node envelope '
       '(X-PAR-04); 8 M12 slab anchors + 8 M10 platen bolts (fasteners.csv)',
       'Dry structure outside the wetted 316L melt path'],
     "Fabricated part sheet: base plate and guard frame."),
    ("melt01", melt, (1, -1, 1),
     ['Extruder barrel OD 60 x 700 (layout choice, W12) with the extrusion '
       'head and downward die',
       'Melt path 316L per duty section 3 (CA 0 mm, AQS-STD-001); the '
       'Precious Plastic class keeps the barrel shop-repairable',
       'Drive envelope at the barrel tail is the purchased 2.2 kW group '
       '(node extruder_kW)'],
     "Fabricated part sheet: 316L melt path."),
    ("groups01", groups, (1, -1, 1),
     ['Clamp platens (BLOW-CLAMP-01) and the mold-halves envelope '
       '(BLOW-MOLD-TOOL-01) between them; air group (BLOW-AIR-01) beside the '
       'clamp',
       'Platens and mold blank are shop work (AQS-BOM-SC-001 row: blow '
       'moulds and shoe moulds); the clamp and air drives are the purchased '
       '0.75 kW groups (node clamp_kW / air_kW)',
       'Mold detail is a hold: the article geometry is not named on the node '
       '(WORK_ORDER W12)'],
     "Fabricated part sheet: drive groups, platens and mold envelope."),
    ("aux01", aux, (0, 1, 0),
     ['Connection hardware DN15 tube stubs flush at the envelope faces; '
      'atmospheric hose per duty section 4 (no flange class)',
      'All 4 schedule rows present at tag, face, height and bore; per-tag '
      'notes in check.nozzles_drawn',
      'The schedule rating column (Class 150) carried verbatim as text'],
     "Fabricated part sheet: connection hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: the extruder runs x 80..780 with the die at the '
      'clamp end; articles leave on +Y',
      f'Graph revision {R["graph_revision"]} is the model authority for this '
      'build; STEP (export/blow_mold.step) is the solids of record',
      'Tracker --check green; acceptance A-core + A-SC (route hold: no '
      'section 4 class row names the former class) per AQS-PLAN-006 '
      'section 5'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/blow_mold.py", f"models/mfg/{unit}/draw_blow_mold.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ["- Continuous-extrusion blow molder per the node design block (Precious "
     "Plastic class; AQS-EQP-MFG-001; A-M-285): 316L melt path per duty "
     "section 3 (barrel, head, downward die), the three drive groups as "
     "purchased envelopes per plan rule 6 with the node ratings (2.2 / 0.75 / "
     "0.75 kW), and the mold tool envelope (BLOW-MOLD-TOOL-01)",
     "- The article geometry is not named on the node: the mold set is an "
     "envelope and the mold detail is a named hold (W12)",
     "- Guard frame pins the registry box so the build fills the envelope "
     "(X-PAR-04); anchors in fasteners.csv"],
    "A-core + A-SC (route hold)")

"""MET_MELT drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, furnace01 (casing + hot face + coil),
crucible01 (crucible + melt line + trunnions + pour lip), aux01 (frame + hood +
shield + cabinet), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets                                       # noqa: E402

ns = runpy.run_path(HERE / "met_melt.py")
parts, R = ns["parts"], ns["report"]
unit = "MET_MELT"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


furnace = union_all([parts["casing"], parts["hot_face"], parts["coil"]])
crucible = union_all([parts["crucible"], parts["melt_line"], parts["trunnions"],
                      parts["pour_lip"]])
aux = union_all([parts["plinth"], parts["frame"], parts["hood"],
                 parts["heat_shield"], parts["power_cabinet"]])
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
M = R["machine"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm envelope - the node size_mm ({R["size_basis"]}); '
      'the build fills it exactly (hold-down frame + hood vent riser pin the box)',
      'Coreless induction melt furnace per the duty sheet and the AQS-MFG-010 tool '
      'row (Table 2.1, rev C metering split): 10 kg Cu crucible class, nameplate '
      '7.5 kW; CS casing OD 420 with refractory hot face 40 mm and coil band',
      'Pour lip toward +Y over the three melt-out rows (billet / mill / atomizer); '
      'power cabinet as a purchased envelope; A-MACH hold-down frame + 8 anchors',
      'A-M-177 melt basis: eta 0.55, 10 kg charge, 0.5 h melt, 100 K superheat'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Furnace centre x 300 on the plinth; casing z 60..660; hood z 700..780; '
      'power cabinet x 700..960; hold-down posts at the envelope corners',
      'Duty holdup basis (duty section 2): V = (13.99/1000) x (1/24) = 0.0006 m3, '
      '1 h charge; the crucible melt line is sized to it and reported (A-VES), '
      'not used as a new rate',
      'Melt solid drawn as process inventory, not a BOM part and not an internal '
      '(IND_MELT W3 idiom)'],
     "General arrangement, side elevation (end view). Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     ['7 schedule rows of docs-authority/nozzles/MET_MELT.csv at tag, face and bore',
      'N1 cathode sheet charge in and N7 off-spec powder return (solids service, '
      'drawn DN15 bore not calculated, plan W4) on -Y at z 160',
      'N2 billet, N3 melt-to-mill and N4 melt-to-atomizer pour rows on +Y at z 600 '
      'under the pour lip',
      'N5 drain flush at the envelope bottom (50 datum); N6 vent on the hood riser '
      'flush at the envelope top (800 datum = box top); atmospheric tube per duty '
      'section 4, no flange (W4 110 % rule)'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("furnace01", furnace, (0, 1, 0),
     ['Casing OD 420 (wall 6, study) with base/top heads; refractory '
      'hot face 40 mm (liner charge, supplier TDS governs); induction coil band '
      '(copper, study section)',
      'Duty section 3: graphite or refractory on the hot face; frame A500 behind '
      'a heat shield; CA 0 mm - dry, non-hydrocarbon furnace service',
      'Shell dimensions are study values sized to the 10 kg class at the bench '
      'box (hold, WORK_ORDER W12)'],
     "Fabricated part sheet: casing + hot face + coil."),
    ("crucible01", crucible, (0, 1, 0),
     ['Clay-graphite crucible OD 110 bore 80 (buy consumable, change-out per '
      'campaign, IND_MELT W6 idiom); maker TDS mass governs at order',
      'Tilt trunnions and pour lip over the +Y melt-out rows (N2/N3/N4 at z 600); '
      'layout choice (W12)',
      'Melt-line solid is process inventory (duty section 2 holdup basis), not a '
      'BOM part'],
     "Fabricated part sheet: crucible + trunnions + pour lip."),
    ("aux01", aux, (0, 1, 0),
     [f'Four-post hold-down/guard frame pinning the {L:g} x {W:g} x {H:g} envelope '
      '(40 x 40 posts, top rails); 8 slab anchors in fasteners.csv',
      'Fume hood over the furnace with the vent riser flush at the envelope top '
      '(N6, 800 datum = box top)',
      'Power-supply cabinet as a purchased envelope: nameplate 7.5 kW (AQS-MFG-010 '
      'Table 2.1); cabinet mass a table-density placeholder until the maker TDS '
      'quotes (hold, W12)'],
     "Fabricated part sheet: frame + hood + shield + cabinet."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: charge in on -Y (sheet + powder return), melt out on +Y '
      'under the pour lip; vent on the hood riser',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/met_melt.step) is the solids of record',
      'Tracker --check green; acceptance A-core + A-VES + A-SC per AQS-PLAN-006 '
      'section 5 (route F-VES)'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/met_melt.py", f"models/mfg/{unit}/draw_met_melt.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ["- Coreless induction melt furnace per the AQS-MFG-010 tool row (10 kg Cu "
     "crucible, nameplate 7.5 kW): CS casing OD 420, refractory hot face 40 mm, "
     "coil band, clay-graphite crucible (buy consumable), tilt trunnions and pour "
     "lip toward +Y, fume hood with the vent riser at the box top",
     "- A-VES: duty section 2 holdup basis (0.0006 m3, 1 h charge); the crucible "
     "melt line is sized to it and the model figure reported, no new rate; A-SC: "
     "shop-made hardware flagged with the AQS-BOM-SC-001 cross-reference",
     "- A-MACH: hold-down frame + 8 anchors; purchased items named with the node "
     "ratings (crucible consumable; 7.5 kW power cabinet, plan rule 6)"],
    "A-core + A-VES + A-SC")

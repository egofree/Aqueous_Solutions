"""ZNBR2 drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, module01 (one bay detail), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets                                       # noqa: E402

ns = runpy.run_path(HERE / "znbr2.py")
parts, R = ns["parts"], ns["report"]
DS = ns["DS"]
unit = "ZNBR2"


def compound_of(shapes):
    """The bay/full assembly as one compound of its closed solids (the builder idiom;
    a 800-part union fuse would not converge in this session)."""
    return cq.Workplane(obj=cq.Compound.makeCompound([s.val() for s in shapes]))


# one module bay for the detail sheet: reservoir, posts, pack field, end plates, bus, lift
bay_parts = [wp for name, wp in parts
             if name != "plinth" and (name.endswith("_0") or "_0_" in name)]
bay = compound_of([wp for name, wp in parts if name == "plinth"] + bay_parts)
L, W, H = [float(v) for v in R["size_mm"]]
AC = R["a_cell"]
full = compound_of([wp for _, wp in parts])

SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm overall - the node envelope (ess_tf design, '
      'X-MFG-43), filled by the lifting beams',
      f'{AC["modules"]} module bays: bipolar plate field over its electrolyte reservoir, '
      'pump and cooler envelopes per plan rule 6',
      f'Booked cell-summed electrode area {AC["active_area_m2_booked"]} m2 at 20 mA/cm2 '
      f'(j.A = current: {AC["stack_I_A"]:g} A x {AC["stack_V_dc"]:g} V DC per module)',
      'No wetted alloy (duty section 3): carbon-plastic plates, PVC-U reservoirs, copper bus'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     [f'Electrolyte holdup {AC["modules"] * 529.4:g} L at 2 M ZnBr2 (A-M-457), one 700 x 700 '
      'x 1155 PVC-U tank per module under its stack',
      f'Plate fields as bonded pack envelopes: {AC["plates_per_module"]} plates of '
      f'{AC["plate_active_mm"][0]:g} x {AC["plate_active_mm"][1]:g} active at the 6 mm pitch',
      'Coolers at the cycling_thermal charge-window rate (A-M-455); pumps at the A-M-179 '
      'auxiliary share',
      'The placement seed block under-books this machine - floor space is the named '
      'consequence (WORK_ORDER W12(1))'],
     "General arrangement, side elevation. Shop, not stamped."),
    ("module01", bay, (1, -0.5, 0.7),
     ['One module bay, exploded view: electrolyte reservoir (PVC-U walls, open top), four '
      'support posts, bipolar plate field between its end plates, lifting beam',
      f'Stack {AC["stack_I_A"]:g} A at {AC["stack_V_dc"]:g} V DC (48 cells of the booked '
      '1.82 V in series per plate pair count - the booked cell-summed area at the 20 mA/cm2 book)',
      'Bus flats 20 x 6.3 copper at the lower end plate (AQS-BUS-001 class method; '
      'POWER.md states no ZNBR2 bus section)',
      'Tie rods M16 in the end-plate ledges; pump and cooler envelopes at the bay flank '
      '(purchased, plan rule 6)'],
     "Fabricated part sheet: one module bay (reservoir, stack, bus, purchased envelopes)."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: electrolyte make-up and charge connections low on -Y, Br2 vapour, '
      'bleed and discharge on +Y, drain at the base, vent riser at the last bay beam',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/znbr2.step) is the solids of record',
      'The face connections are atmospheric open-bore stubs (duty section 4: hose, '
      'atmospheric); the schedule elevations draw as issued'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/znbr2.py", f"models/mfg/{unit}/draw_znbr2.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    [f'- A-CELL: {AC["modules"]} modules x {AC["plates_per_module"]} plates of '
     f'{AC["plate_active_mm"][0]:g} x {AC["plate_active_mm"][1]:g} active at the 6 mm pitch '
     f'= {AC["active_area_m2_model"]} m2 against the booked {AC["active_area_m2_booked"]} m2 '
     '(purge_basis; j.A = current closes; X-MFG-43, A-M-456)',
     '- Electrolyte holdup reported (47 reservoirs, 2 M ZnBr2, A-M-457); no residence time '
     'derived (duty section 2 claims no holdup; A-VES rule)',
     '- Purchased items as envelopes per plan rule 6: pumps (A-M-179 aux share) and coolers '
     '(A-M-455 charge-window rate), one of each per module',
     '- Placement hold named: the seed block under-books the machine; floor-space reservation '
     'is the consequence (WORK_ORDER W12(1)); nothing is resized'],
    "A-core + A-CELL")

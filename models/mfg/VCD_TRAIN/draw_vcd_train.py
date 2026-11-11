"""VCD_TRAIN drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, module01 (one still module), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets, step_export  # noqa: E402

ns = runpy.run_path(HERE / "vcd_train.py")
parts, R = ns["parts"], ns["report"]
AH = R["a_hx"]
unit = "VCD_TRAIN"


def compound_of(shapes):
    return cq.Workplane(obj=cq.Compound.makeCompound([s.val() for s in shapes]))


mod0 = compound_of([wp for name, wp in parts if name == "plinth" or name.endswith("_0")])
full = compound_of([wp for _, wp in parts])
L, W, H = [float(v) for v in R["size_mm"]]

SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm overall - the issued envelope (duty sections 2/4), '
      'filled by the separator caps',
      f'Two MVC still modules, 2 x 100 % (X-RED-05, A-M-149): vessel, bundle, separator, '
      'scroll compressor envelope each',
      f'Bundle {AH["tubes_per_module"]} tubes ID {AH["tube_mm"][0]:g} x {AH["tube_mm"][2]:g} = '
      f'{AH["area_m2_drawn"]:g} m2 per module at U {AH["u_kW_m2K"]:g} x {AH["dT_drive_K"]:g} K '
      f'on the {AH["q_latent_kW"]:g} kW latent duty',
      '316L wetted, CA 0 mm (duty section 3); frame carbon steel'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     [f'Sump {R["holdup_L"]["sump_per_module_model"]:g} L per module - the duty section 2 '
      f'working volume ({R["holdup_L"]["working_volume_book_L"]:g} L, 2 h of distillate) '
      'across both modules',
      'Boiling falls inside the tubes; compressed vapour condenses on the shell - the MVC '
      'still principle at 17 kWh/m3 (A-M-149 driver basis)',
      'Separator ring and demister above the upper tubesheet; scroll compressor envelope at '
      'the bay flank (purchased, plan rule 6)',
      'Feed inlets low on -Y, distillate/brine/bottoms on +Y, drain at the base, vent riser '
      'at the bay-0 cap'],
     "General arrangement, side elevation. Shop, not stamped."),
    ("module01", mod0, (1, -0.5, 0.7),
     ['One still module, exploded view: sump, tubesheet pair with the 18-tube falling-film '
      'bundle at running clearance, separator ring, demister, top cap',
      f'The bundle carries the booked area {AH["area_m2_booked"]:g} m2 at +0.1 % (A-HX: the '
      'node latent duty is the heat rate, so the booked area is calculated)',
      'Scroll compressor envelope and interface (purchased, plan rule 6; W12(2))',
      'The evaporator class carries no section 4 route class - the fabrication route follows '
      'the F-VES practice (W12(1))'],
     "Fabricated part sheet: one MVC still module."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: feed inlets low on -Y, distillate/brine/bottoms out on +Y, drain at '
      'the base, vent riser at the bay-0 separator cap',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/vcd_train.step) is the solids of record',
      'Face connections are atmospheric open-bore stubs (duty section 4: hose, atmospheric); '
      'the schedule elevations draw as issued'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/vcd_train.py", f"models/mfg/{unit}/draw_vcd_train.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    [f'- A-HX: bundle {AH["tubes_per_module"]} tubes x {AH["area_m2_drawn"]:g} m2 drawn against '
     f'the booked {AH["area_m2_booked"]:g} m2 (latent / (U 2.8 x 5 K), PERRY9_EVAP class, on '
     'the node 8.436 kW latent duty)',
     '- Both installed modules drawn (2 x 100 %, X-RED-05); sump holdup 13.8 L equals the duty '
     'working-volume book (A-VES rule, reported)',
     '- Purchased per plan rule 6: scroll compressors as envelopes and interfaces',
     '- Route-class hold named: evaporator carries no section 4 class (W12(1))'],
    "A-core")

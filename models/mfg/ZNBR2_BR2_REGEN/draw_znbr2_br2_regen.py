"""ZNBR2_BR2_REGEN drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, a_col01 (internals stack), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets, step_export  # noqa: E402

ns = runpy.run_path(HERE / "znbr2_br2_regen.py")
parts, R = ns["parts"], ns["report"]
AC = R["a_col"]
unit = "ZNBR2_BR2_REGEN"


def compound_of(shapes):
    return cq.Workplane(obj=cq.Compound.makeCompound([s.val() for s in shapes]))


internals = compound_of([parts[k] for k in ("support", "bed", "distributor", "demister")])
full = compound_of(list(wp for _, wp in parts.items()))
L, W, H = [float(v) for v in R["size_mm"]]

SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm overall - the node envelope (ess_tf design, '
      'X-MFG-43b), filled by the vent riser',
      f'Packed Br2-recovery wash column: PVC-U DN100 Sch 80 at 1.5 m/s on the '
      f'{AC["gas_m3_h"]:g} m3/h purge (D_req {AC["D_req_mm"]:g} mm)',
      f'Bed {AC["packed_mm"]:g} mm of 25 mm PVC-U Pall rings = NTU {AC["ntu"]} x HTU '
      f'{AC["htu_m"]:g} m (duty-held figures); removal {AC["removal"] * 100:.2f} %, '
      f'{AC["y_out_ppmv"]} ppmv Br2 out',
      'Duty section 3 material: PVC-U shell/sump/packing, FKM gaskets, no metal wetted part'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     [f'Bed {AC["packed_mm"]:g} mm between the perforated support plate and the drip-pipe '
      'distributor; mesh demister above; sump on the plinth (AQS-DUTY-061 house classes)',
      'No liquor inlet is piped (duty section 2): the scrub liquor loop is the S69B return',
      'Gas in low on -Y, electrolyte return out on +Y, drain boss under the plinth, vent riser '
      'flush at the envelope top (the 2000 datum is the placeholder, W12(4))',
      'The HTU stays the duty packing figure, not a measured transfer unit (duty section 8, '
      'W12(2))'],
     "General arrangement, side elevation. Shop, not stamped."),
    ("a_col01", internals, (1, -0.5, 0.7),
     ['Internals stack (A-COL, all solids): perforated support plate (50 % open envelope), '
      'random ring bed, drip-pipe distributor, mesh demister',
      f'Packing: 25 mm PVC-U Pall rings, in-house cut tube rings (X-MFG-32 class), bed '
      f'{AC["packed_mm"]:g} mm',
      'The ring bed draws as its envelope at the bulk class; the rings are made on the '
      'jellybean line (BOM item 3)',
      'Duty section 2 rule: no sump volume is invented from the gas mass - the sump is the '
      'house class and is reported, not used (A-VES rule)'],
     "Fabricated part sheet: column internals stack."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: Br2-laden purge in low on -Y, scrubbed electrolyte out on +Y to the '
      'battery, drain at the base, vent riser at the top',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/znbr2_br2_regen.step) is the solids of record',
      f'The column sizes on the live purge ({AC["gas_m3_h"]:g} m3/h, D_req {AC["D_req_mm"]:g} mm); '
      f'the {AC["gas_duty_m3_h"]:g} m3/h duty figure and its 84 mm diameter stay the W12(1) class '
      'basis, and DN'
      f'{AC["DN_mm"]:g} carries the larger of the two diameters'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/znbr2_br2_regen.py", f"models/mfg/{unit}/draw_znbr2_br2_regen.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    [f'- A-COL: bed {AC["packed_mm"]:g} mm (NTU {AC["ntu"]} x HTU {AC["htu_m"]:g} m, duty-held), '
     'support plate, distributor and demister as solids; diameter at 1.5 m/s on the live '
     f'purge ({AC["D_req_mm"]:g} mm -> PVC-U DN{AC["DN_mm"]:g})',
     '- Sump holdup reported (house class), no residence time derived (duty section 2 rule; '
     'A-VES rule)',
     '- Duty 30 m3/h / 84 mm figures are the W12(1) class basis; the column sizes on the live '
     f'purge the charge book re-solves ({AC["D_req_mm"]:g} mm -> PVC-U DN{AC["DN_mm"]:g}) and '
     'DN100 carries the larger of the two diameters',
     '- HTU and NTU stay duty-held figures, not measured transfer units (hold, W12(2))'],
    "A-core + A-COL")

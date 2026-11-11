"""BAGHOUSE drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, bag_field01 (tubesheet + bags + hopper), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets, step_export  # noqa: E402

ns = runpy.run_path(HERE / "baghouse.py")
parts, R = ns["parts"], ns["report"]
AM = R["a_mach"]
unit = "BAGHOUSE"


def compound_of(shapes):
    return cq.Workplane(obj=cq.Compound.makeCompound([s.val() for s in shapes]))


PD = dict(parts)
field = compound_of([PD[k] for k in ("tubesheet", "bags", "hopper", "rotary_valve", "valve_guard",
                                     "pulse_header", "diaphragm_valves")])
full = compound_of([wp for _, wp in parts])
L, W, H = [float(v) for v in R["size_mm"]]

SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm overall - the design envelope (specialty_sizing, '
      'X-SPEC lane), filled by the roof',
      f'Pulse-jet baghouse: {AM["bags"]} antistatic-polyester bags D{AM["bag_mm"][0]:g} x '
      f'{AM["bag_mm"][1]:g} ({AM["cloth_m2_drawn"]:g} m2 cloth, A/C {AM["ac_drawn_m3_min_m2"]:g} '
      f'drawn against the {AM["ac_basis_m3_min_m2"]:g} m3/min/m2 basis)',
      f'Capture air {AM["capture_air_m3_h"]:g} m3/h at the 0.5 m/s hood-face class over the '
      'three draws (A-M-458)',
      'CS housing painted, bonded, grounded; deflagration vent panel on the +X wall (duty '
      'section 3)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     [f'Chain: plinth 50, 60 deg hopper to 656, bag field to 1876, tubesheet, clean plenum to '
      f'2256, roof at the envelope top',
      f'Captured dust {sum(AM["dust_kg_d"].values()):.2f} kg/d leaves via the DN200 rotary valve '
      'to IA-BAG-01 (drive guard drawn, A-MACH)',
      'The unit draws no fan of its own: duty section 1 books 0.0 kW - the baghouse dP rides '
      'the tool-extraction air mover (W12(3))',
      'Placement seed under-books the height by 0.78 m (W12(1)); nothing is resized'],
     "General arrangement, side elevation. Shop, not stamped."),
    ("bag_field01", field, (1, -0.5, 0.7),
     ['Internals and discharge (all solids): tubesheet with the 20-bag hole field, the bag '
      'field rooted into it, the 60 deg hopper, rotary valve with drive guard',
      f'Pulse-clean header DN40 with 5 diaphragm-valve envelopes (0.5 MPa compressed-air '
      'class) and the solenoid enclosure on the wall (A-MACH named ratings)',
      'Hood conveying ducts are the design DN100/DN80 set - shop spools to the hoods, not '
      'drawn (W12(5))',
      'The capture-air basis is the registered A-M-458 study basis; measured hood entries '
      'and dP replace it at the first-article duct run'],
     "Fabricated part sheet: bag field, hopper, valve, pulse header."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: three dust draws in at the inlet-plenum face (-Y), captured dust via '
      'the hopper valve on +X, clean-air vent riser at the roof top',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/baghouse.step) is the solids of record',
      'The DN15 schedule rows are the duty connection table ("0.28 mm is not a specification; '
      'nozzle is DN15" - duty section 4)',
      'Access door on the +X wall (bolted, fasteners row); anchors drawn at the plinth'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/baghouse.py", f"models/mfg/{unit}/draw_baghouse.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    [f'- A-MACH: purchased items named with the rating (rotary valve at the 7.77 kg/d dust '
     'class, pulse diaphragm valves at the 0.5 MPa class, solenoid enclosure); drive guard '
     'and plinth anchors drawn',
     f'- Cloth {AM["cloth_m2_drawn"]:g} m2 drawn ({AM["bags"]} bags) against the '
     f'{AM["cloth_m2_required"]:g} m2 basis at the {AM["ac_basis_m3_min_m2"]:g} m3/min/m2 '
     f'EPA-453 class (A-M-458); capture air {AM["capture_air_m3_h"]:g} m3/h',
     '- No fan on this unit (duty 0.0 kW): the baghouse dP rides the tool-extraction air '
     'mover - stated, not omitted (W12(3))',
     '- Placement seed under-books the height by 0.78 m (W12(1)); nothing is resized'],
    "A-core + A-MACH")

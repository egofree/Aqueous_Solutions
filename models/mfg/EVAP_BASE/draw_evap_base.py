"""EVAP_BASE drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, mvr01 (falling-film body + bundle), aux01 (separator,
blower, interchanger, relief envelopes), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets, step_export  # noqa: E402

ns = runpy.run_path(HERE / "evap_base.py")
parts, R = ns["parts"], ns["report"]
AH = R["a_hx"]
MV = R["mvr"]
unit = "EVAP_BASE"


def compound_of(shapes):
    return cq.Workplane(obj=cq.Compound.makeCompound([s.val() for s in shapes]))


PD = dict(parts)
mvr = compound_of([PD[k] for k in ("body", "bundle")])
aux = compound_of([PD[k] for k in ("separator", "blower", "interchanger",
                                   "psv_body", "psv_shell")])
full = compound_of([wp for _, wp in parts])
L, W, H = [float(v) for v in R["size_mm"]]

SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm overall - the node envelope (X-MFG-30 body, blower '
      'and interchanger frame)',
      f'MVR falling-film evaporator DN{AH["tubes"] and 350:g}: DN350 body, 20-tube nickel '
      f'bundle ({AH["A_ff_m2_drawn"]:g} m2), vapour separator, blower, interchanger',
      f'Blower ratio {MV["ratio"]:g} at {MV["comp_shaft_kW"]:g} kW shaft (X-MFG-32 line); '
      f'interchanger {MV["ix_Q_kW"]:g} kW / {MV["ix_A_m2"]:g} m2, outlets {50.6:g} C',
      'Nickel 200 wetted in hot NaOH (duty section 3); CA not applicable (AQS-STD-001)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     [f'Body chain: sump 400, tubesheet pair, tube zone 1500, head 150, separator '
      f'{MV["recirc_kg_h"] and 975:g} with the mesh pad - the design chain closes at the '
      'envelope top',
      f'Falling-film area {AH["A_ff_m2_drawn"]:g} m2 drawn against the booked '
      f'{AH["A_ff_m2_booked"]:g} m2 (latent / (U 1500 x 6 K) on the 20.95 kW duty; A-HX)',
      f'Relief per the node relief_basis: body fire valve set 100 kPa g, shell blocked-outlet '
      'valve set 350 kPa g, API 526 D orifices, vent to ACID_POLISH_SCRUB',
      'The recirculation sump (82.9 L) is hardware at the minimum-wetting-rate book; '
      'reported, no residence time claimed (A-VES rule)'],
     "General arrangement, side elevation. Shop, not stamped."),
    ("mvr01", mvr, (0.5, -1, 0.5),
     ['Falling-film body and bundle: DN350 nickel shell, tubesheet pair, 20 tubes ID 25 x '
      'OD 29 x 1500 mm at the design triangular pitch (1.25 x OD)',
      f'The bundle carries the booked area at +1.1 % (the tube count is a ceil, W12(2)); '
      'U 1500 W/(m2 K) at 6 K is the AQS-DUTY-060 class, replaced by pilot data when they '
      'exist (A-M-106)',
      'Nickel 200, CA not applicable; GTAW with nickel-qualified procedures; hydro at '
      '1.43 x design (route, W10)',
      'Evaporator class carries no section 4 route class - F-VES practice applies (W12(1))'],
     "Fabricated part sheet: falling-film body and bundle."),
    ("aux01", aux, (1, -0.5, 0.7),
     ['Vapour separator DN350 x 975 with 100 mm mesh pad above the body; blower envelope '
      '(purchased, X-MFG-32 line) and interchanger envelope at the frame flanks',
      'Recirculation pump rides the interchanger bay (988 kg/h at 4 m, node design); '
      'purchased per plan rule 6',
      'Relief-valve envelopes on the body and shell (API 526 D orifices, set points per the '
      'node relief_basis)',
      'Purchased items carry the node design ratings; maker ratings read the sheets at order '
      '(no vendor basis is a design input, W12(3))'],
     "Fabricated part sheet: separator, blower, interchanger, relief envelopes."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: NaOH feed in low on -Y, product and condensate out on +Y, drain at '
      'the base, vent riser on the separator cap flush at the envelope top',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/evap_base.step) is the solids of record',
      'The unit folder owns this builder (AQS-PLAN-006 W1): the style pass no longer '
      'clobbers the MVR build',
      'The vent schedule datum (top, 800) is the placeholder elevation (W12(4))'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/evap_base.py", f"models/mfg/{unit}/draw_evap_base.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    [f'- A-HX: bundle {AH["tubes"]} tubes, {AH["A_ff_m2_drawn"]:g} m2 drawn against the booked '
     f'{AH["A_ff_m2_booked"]:g} m2 (latent / (U 1500 x 6 K) on the node 20.95 kW duty; '
     'AQS-DUTY-060 section 1)',
     '- The X-MFG-30 MVR idiom in nickel for the NaOH service: DN350 body, separator with '
     'mesh pad, blower and interchanger envelopes (plan rule 6)',
     '- Unit-owned builder: the unit folder script replaces the evap_mvr.py EVAP_BASE '
     'expansion, so the style pass never clobbers the build',
     '- Route-class hold named: evaporator carries no section 4 class (W12(1)); pilot U and '
     'bench leach stay the open duty items (W12(6))'],
    "A-core")

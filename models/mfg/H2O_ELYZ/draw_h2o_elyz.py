"""H2O_ELYZ drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, stack01 (the PEM cell field), bop01 (separators, beds,
pump, relief), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets                                       # noqa: E402

ns = runpy.run_path(HERE / "h2o_elyz.py")
parts, R = ns["parts"], ns["report"]
SR = R["stack_report"]
unit = "H2O_ELYZ"


def compound_of(shapes):
    return cq.Workplane(obj=cq.Compound.makeCompound([s.val() for s in shapes]))


PD = dict(parts)
stack = compound_of([wp for n, wp in parts if n == "stack_frame" or n.startswith(("stack_", "cell_", "post_"))
                     or n == "power_electronics"])
bop = compound_of([wp for n, wp in parts if n.startswith(("h2_sep", "o2_sep", "bed_", "di_water_pump",
                                                          "bop_frame", "psv_h2"))])
full = compound_of([wp for _, wp in parts])
L, W, H = [float(v) for v in R["size_mm"]]

SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm overall - the A-M-279 skid allowances at the rated '
      f'kW (stack deck {R["skid_allowances"]["l_stack_mm"]:g} + gap 100 + BoP deck '
      f'{R["skid_allowances"]["l_bop_mm"]:g} at W 1050, H 2200)',
      f'PEM stack: {SR["cells"]} cells of {SR["active_mm"][0]:g} x {SR["active_mm"][1]:g} mm '
      f'active ({SR["area_m2_cell_summed"]:g} m2 cell-summed) at the 8 mm pitch',
      f'{SR["i_stack_A"]:g} A at {SR["v_stack_V"]:g} V DC ({SR["p_dc_kW"]:g} kW DC) on the '
      f'rated H2 over the {SR["window_h"]:g} h PV window (A-M-133, A-M-459)',
      'BoP deck: H2 and O2 separators DN150 x 400, deoxo and dryer beds, DI-water pump '
      '(purchased envelopes, rule 6)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Ti cell hardware and PTFE seals, Ir/Ru anode with Pt cathode (duty section 3); '
      'H2 and O2 leave on separate lines (NFPA 2, ISO 22734)',
      'Deoxo on H2: 2 beds DN80 x 345 at GHSV 5000 1/h (A-M-168 class); dryer on H2: 2 beds '
      'DN80 x 712 (4A/13X at margin 3)',
      'Design 990 kPa g; the H2 relief per the node relief_basis (A-M-196), envelope drawn',
      'The placement seed block under-books the skid (W12(1)); nothing is resized'],
     "General arrangement, side elevation. Shop, not stamped."),
    ("stack01", stack, (1, -0.5, 0.7),
     [f'The PEM cell field: {SR["cells"]} bipolar plates of 169.7 x 169.7 mm active between Ti end '
      'plates at the 8 mm pitch; the plates and lands draw, the MEAs are a BOM loading row '
      '(W12(3))',
      f'The cell-summed area {SR["area_m2_cell_summed"]:g} m2 is what the rated H2 books: '
      '26,590 Ah/kg / j (A-M-459)',
      f'Copper bus pair at the terminals (dry side; conductors are copper per duty section 3); '
      f'{SR["i_stack_A"]:g} A per terminal pair',
      'The operating point (j 1.8 A/cm2, 1.85 V/cell) is the registered study basis - the '
      'polarisation curve replaces it at the first article (W12(2))'],
     "Fabricated part sheet: PEM stack and enclosure."),
    ("bop01", bop, (1, -0.5, 0.7),
     ['H2 and O2 gas-liquid separators DN150 x 400 on legs, one per side (316L, M1 family); '
      'design 990 kPa g (node design_kPa)',
      'Deoxo on H2 (2 x DN80 x 345) and dryer on H2 (2 x DN80 x 712) - the A-M-168 purifier '
      'classes applied on the skid, duplicated beds',
      'DI-water pump envelope (purchased, rule 6) and the H2 relief-valve envelope per the '
      'node relief_basis',
      'Recorded hold: the H2_DRYER unit sizes on the HDR pool residual (2.750 kg/d) against '
      'this unit 9.358 design / 8.715 edge - the sizing hold stays open (W12(6))'],
     "Fabricated part sheet: balance-of-plant deck."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: feed water in low on -Y, H2 and O2 out on +Y (separate lines), drain '
      'at the base, vent riser at the BoP frame top',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/h2o_elyz.step) is the solids of record',
      'The power and service terminals (N6/N7) are text rows of the schedule; the piped rows '
      'draw at their placeholder datums (W12(4))',
      'The deoxo and dryer beds duplicated per the A-M-168 bed-count rule'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/h2o_elyz.py", f"models/mfg/{unit}/draw_h2o_elyz.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    [f'- Stack facts reported against A-M-459: {SR["cells"]} cells x {SR["active_mm"][0]:g} x '
     f'{SR["active_mm"][1]:g} mm = {SR["area_m2_cell_summed"]:g} m2 cell-summed, '
     f'{SR["i_stack_A"]:g} A at {SR["v_stack_V"]:g} V DC ({SR["p_dc_kW"]:g} kW DC)',
     '- The node internals row drawn in full: stack + H2/O2 separators + deoxo on H2 + dryer '
     '(A-M-168 classes on the skid beds)',
     '- Placement hold named: the seed block under-books the A-M-279 skid (W12(1)); nothing '
     'is resized',
     '- H2_DRYER chain mismatch recorded, not fixed (W12(6))'],
    "A-core")

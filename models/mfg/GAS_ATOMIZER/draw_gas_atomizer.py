"""GAS_ATOMIZER drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, tower01 (tower + powder pot + gas ring),
tundish01 (tundish + heater + stand), aux01 (frame + loop + compressor + cabinet),
iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets, step_export  # noqa: E402

ns = runpy.run_path(HERE / "gas_atomizer.py")
parts, R = ns["parts"], ns["report"]
unit = "GAS_ATOMIZER"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


tower = union_all([parts["tower"], parts["powder_pot"], parts["gas_ring"]])
tundish = union_all([parts["tundish"], parts["tundish_heater"], parts["tundish_stand"]])
aux = union_all([parts["plinth"], parts["frame"], parts["ar_loop"],
                 parts["compressor"], parts["control_cabinet"]])
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
M = R["machine"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm envelope - the node size_mm ({R["size_basis"]}); '
      'the build fills it exactly (hold-down frame pins the box)',
      'Close-coupled gas atomiser with Ar recirculation per the AQS-MFG-010 tool '
      'row (Table 2.1, rev C metering split): nameplate 5.5 kW; GMR 2.5 at 30 bar '
      '+ tundish 1 kW x 1 h (A-M-177)',
      'Atomization tower OD 300 with powder pot, close-coupled gas ring at the '
      'tower neck, heated tundish on a stand over the tower; Ar loop DN32 to the '
      'compressor bay x 700..960',
      'A-MACH: hold-down frame + 8 slab anchors; purchased items named with the '
      'node ratings (compressor 30 bar class, cabinet 5.5 kW, tundish heater 1 kW)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Tower centre x 300 on the plinth, z 60..560; tundish z 580..700; powder pot '
      'at the tower base; station arrangement is the layout choice (W12)',
      'Duty: 3.556 kg/d melt in (IA-MELT-ATOM), 3.2 kg/d powder out (S60) and '
      '0.3556 kg/d off-spec remelt back to MET_MELT; the IND_TO_ATOM standby row '
      'stays at zero on the design day',
      '30 bar Ar loop class per A-M-177: the relief case is pending (unit task 07) '
      'and no design_kPa is stated on the node - no flange drawn (W4 110 % rule)'],
     "General arrangement, side elevation (end view). Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     ['7 schedule rows of docs-authority/nozzles/GAS_ATOMIZER.csv at tag, face and bore',
      'N1 melt in and N5 standby melt row (IND_TO_ATOM study edge, "when powder '
      'required") on -Y at z 160',
      'N2 metal powder out, N6 powder stock and N7 off-spec remelt (solids rows '
      'drawn DN15, bore not calculated, plan W4) on +Y at z 600',
      'N3 drain flush at the envelope bottom (50 datum); N4 vent flush at the '
      'envelope top (800 datum = box top); atmospheric tube per duty section 4'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("tower01", tower, (0, 1, 0),
     ['Atomization tower OD 300 (wall 6, study) with base/neck heads and '
      'powder-collection pot OD 200',
      'Close-coupled gas ring R 60 with 4 gas ports at the tower neck (GMR 2.5 '
      'study basis, A-M-177); ring geometry study (hold, W12)',
      '316L per duty section 3 (melt contact); CA 0 mm - dry powder loop '
      '(AQS-STD-001)'],
     "Fabricated part sheet: tower + powder pot + gas ring."),
    ("tundish01", tundish, (0, 1, 0),
     ['Tundish OD 160 on a stand over the tower neck (z 580..700, study)',
      'Heater band at the tundish base: the 1 kW tundish duty (AQS-MFG-010 '
      'Table 2.1; A-M-177 10 min pour) - the heater set is a buy element, '
      'purchased per plan rule 6',
      'Tundish dimensions are study values sized to the 3.56 kg/d class (hold, '
      'WORK_ORDER W12)'],
     "Fabricated part sheet: tundish + heater + stand."),
    ("aux01", aux, (0, 1, 0),
     [f'Four-post hold-down/guard frame pinning the {L:g} x {W:g} x {H:g} envelope '
      '(40 x 40 posts, top rails); 8 slab anchors in fasteners.csv',
      'Ar recirculation loop DN32 tube runs to the compressor bay (30 bar class '
      'per A-M-177); loop runs are layout choice (W12)',
      'Compressor set and control cabinet as purchased envelopes (30 bar class, '
      '5.5 kW nameplate); masses table-density placeholders until the maker TDS '
      'quotes (hold, W12)'],
     "Fabricated part sheet: frame + Ar loop + compressor + cabinet."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: melt in on -Y, powder/stock/remelt out on +Y; Ar loop '
      'runs -Y to +X',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/gas_atomizer.step) is the solids of record',
      'Tracker --check green; acceptance A-core + A-MACH + A-SC per AQS-PLAN-006 '
      'section 5 (route F-MACH)'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/gas_atomizer.py", f"models/mfg/{unit}/draw_gas_atomizer.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ["- Close-coupled gas atomiser with Ar recirculation per the AQS-MFG-010 tool "
     "row (nameplate 5.5 kW; GMR 2.5 at 30 bar + tundish 1 kW, A-M-177): tower "
     "OD 300 with powder pot, gas ring at the neck, heated tundish on a stand, "
     "DN32 Ar loop to the compressor bay",
     "- A-MACH: hold-down frame + 8 anchors; purchased items named with the node "
     "ratings (compressor 30 bar class, cabinet 5.5 kW, tundish heater 1 kW, plan "
     "rule 6); A-SC: shop-made hardware flagged with the AQS-BOM-SC-001 "
     "cross-reference",
     "- No design_kPa on the node; the 30 bar loop class is the A-M-177 study "
     "basis and the relief case is pending (unit task 07) - no flange drawn (W4 "
     "110 % rule); tower/tundish dimensions are study values (holds, WORK_ORDER "
     "W12)"],
    "A-core + A-MACH + A-SC")

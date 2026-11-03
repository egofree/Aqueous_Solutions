"""AFTERBURNER drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, ch01 (chamber + refractory),
aux01 (purchased envelopes + saddles + plinth), nozz01 (connection hardware),
iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets                                       # noqa: E402

ns = runpy.run_path(HERE / "afterburner.py")
parts, R = ns["parts"], ns["report"]
unit = "AFTERBURNER"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


chamber = union_all([parts["chamber"], parts["refractory"]])
aux = union_all([parts["plinth"], parts["saddles"], parts["burner"], parts["fan"],
                 parts["damper"]])
nozz = parts["nozzles"]
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
C = R["chamber"]
PR = R["purchased"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm envelope - the node size_mm ({R["size_basis"]})',
      'Combustion chamber per duty section 8 (AQS-DUTY-063 Rev B section 6, '
      'X-SAN-01): ID 200 x 600, >= 850 C for >= 2 s (EU IED Art. 50), horizontal on '
      'two saddles over the 20 mm plinth',
      'Steel shell wall 6 and refractory lining 50 are study values - duty section '
      '8: refractory and burner detail open (holds, W12)',
      'Burner, flue ID fan and damper envelopes carry the node equipment ratings '
      '(plan rule 6)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Chamber axis at y 300, z 420; burner envelope on -X, flue ID fan envelope on '
      '+X, damper and flame monitor envelope on the chamber top',
      f'A-HX report: chamber volume {C["v_chamber_m3"]:g} m3; residence at the '
      f'AFTERBURNER_FLUE design flow {C["residence_at_flue_s"]:g} s against the '
      '>= 2 s requirement - reported, not called a calculated design (the duty '
      'claims no heat rate)',
      'Carbon steel (duty section 3), CA 1.5 mm (AQS-STD-001 hydrocarbon rule)'],
     "General arrangement, side elevation (end view). Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     ['12 schedule rows of docs-authority/nozzles/AFTERBURNER.csv at tag, face and '
      'bore',
      'Inlets N1-N3, N10-N12 on -Y at z 160 (NCG, organics, fuel, biogas, '
      'combustion O2, and the N12 digestate-cake solids row drawn DN15 bore not '
      'calculated per plan W4); outlets N4-N6, N9 on +Y at z 600 (Q1 flue rows - '
      'quoting repaired, flue to AFTERBURNER_FLUE, captured CO2/air to CRYO_CO2)',
      'N7 drain flush at the envelope bottom (50 datum); N8 vent flush at the '
      'envelope top (800 datum is the box top)',
      'Atmospheric open-bore tube stubs per duty section 4 (no duct bore, no flange '
      'class); the schedule rating column (Class 150) carried verbatim as text'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("ch01", chamber, (0, 1, 0),
     [f'Chamber ID {C["id_mm"]:g} x {C["length_mm"]:g}, steel shell wall '
      f'{C["wall_mm"]:g} (study) with two end heads',
      f'Refractory lining t {C["refractory_mm"]:g} press-fitted over the full bore '
      '(duty section 8: refractory detail open - study layer, hold W12)',
      'Duty feed basis 7.03 kg/d including sanitation cake and biogas (X-SAN-01)'],
     "Fabricated part sheet: chamber + refractory lining."),
    ("aux01", aux, (0, 1, 0),
     ['Plinth 1000 x 600 x 20 + two saddles (180 mm bases, tops pierce the shell '
      'annulus) + the three purchased envelopes',
      f'{PR["burner"].split(",")[0]} - burner detail open on the duty (hold W12); '
      'envelopes carry the node ratings, no invented internals',
      'Carbon steel (ASTM A500) structure; 8 M12 slab anchors and 8 M12 saddle '
      'bolts (fasteners.csv)'],
     "Fabricated part sheet: supports + purchased envelopes."),
    ("nozz01", nozz, (0, 1, 0),
     ['Connection hardware DN15 as open-bore tube stubs flush at the envelope '
      'faces (lib builders); atmospheric per duty section 4',
      'All 12 schedule rows present at tag, face, height and bore; per-tag '
      'positions in check.nozzles_drawn',
      'The N12 solids row is a non-piped transfer (sealed bins to incineration, '
      'barrier 2): drawn DN15, bore not calculated (plan W4)'],
     "Fabricated part sheet: connection hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: waste gas and cake in on -Y, flue out on +Y to '
      'AFTERBURNER_FLUE and the Q1 heat-recovery takeoffs; drain and vent on the '
      'run centreline',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/afterburner.step) is the solids of record',
      'Tracker --check green; acceptance A-core + A-HX per AQS-PLAN-006 section 5'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/afterburner.py", f"models/mfg/{unit}/draw_afterburner.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ["- Machine: combustion chamber ID 200 x 600 per duty section 8 (AQS-DUTY-063 "
     "Rev B section 6, X-SAN-01), >= 850 C for >= 2 s (EU IED Art. 50); steel wall "
     "6 and refractory 50 are study values (holds, W12)",
     "- A-HX: chamber volume 0.01885 m3; residence at the AFTERBURNER_FLUE node "
     "design flow 0.0018 m3/s is 10.5 s against the >= 2 s requirement - reported, "
     "not called a calculated design (the duty claims no heat rate)",
     "- Purchased envelopes per plan rule 6 from the node equipment list: burner + "
     "ignition + BMS 0.05 kW, flue ID fan 0.1332 kW, dampers + flame monitor "
     "0.01 kW; burner detail open on the duty (hold, W12)",
     "- Schedule N4/N5 rows repaired to the schedule quoting (unquoted comma in "
     "'Q1 flue, not Q4' shifted face and height); change record in "
     "notes/glass_oilgas_m3_2026-11-02.md"],
    "A-core + A-HX")

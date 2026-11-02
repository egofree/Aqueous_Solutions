"""COMB_HEAT drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, shell01 (shell + brick lining + crown),
burner01 (310S radiant tube + burner block + flue duct + hearth rail), aux01
(controls bay + plinth + connection hardware), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets                                       # noqa: E402

ns = runpy.run_path(HERE / "comb_heat.py")
parts, R = ns["parts"], ns["report"]
unit = "COMB_HEAT"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


shell = union_all([parts["furnace_shell"], parts["brick_lining"], parts["castable_crown"]])
burner = union_all([parts["burner_tube"], parts["burner_block"], parts["flue_duct"],
                    parts["hearth_rail"]])
aux = union_all([parts["plinth"], parts["controls_cabinet"]])
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
M = R["machine"]
S = R["standby"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm overall - the node N+1 rated envelope (A-M-282), filled exactly',
      'Combustion reheating furnace, tertiary N+1 standby of IND_MELT: ' + S["state"],
      'Mild-steel shell with the alumina-silica brick + castable crown hot face, 310S radiant burner tube',
      f'Dry flue path above the acid dew point; N1 off-gas takeoff to MET_SCRUB; thermal_kW {M["burner_tube"]["basis"].split("thermal_kW ")[1].split(" ")[0]} node rating'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     [f'Shell t{M["shell"]["wall_mm"]:g} mild steel (study fab-page value - hold, W12), '
      f'brick hot face t{M["lining"]["brick_mm"]:g} + castable crown (duty section 3)',
      'Radiant tube along X at z 600: combustion products stay inside the tube; '
      'fuel class is the plant C5-C10 product (duty section 1)',
      'Controls cabinet on the +X bay - purchased envelope (plan rule 6)',
      'General tolerance ISO 2768-m unless noted'],
     "General arrangement, side elevation. Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     [f'{R["nozzle_count_schedule"]} schedule rows of docs-authority/nozzles/COMB_HEAT.csv '
      'at tag, face and bore',
      'N1 DN15 combustion off-gas takeoff on +Y at z 600 (registered layout), riding the dry flue duct to MET_SCRUB',
      'N2 DN15 drain through the plinth, flush at the envelope bottom (50 datum); '
      'N3 DN15 vent riser on the shell roof, flush at the envelope top (800 datum is the '
      'schedule placeholder - hold, W12)',
      'Atmospheric hose makeup at the face (duty section 4); Class 150 schedule column '
      'carried verbatim as text'],
     "Connection orientation, top view. Tags/faces/bore per the schedule."),
    ("shell01", shell, (0, 1, 0),
     [f'Mild-steel shell {M["shell"]["od_mm"][0]:g} x {M["shell"]["od_mm"][1]:g} '
      f'x z {M["shell"]["z_mm"][0]:g}..{M["shell"]["z_mm"][1]:g}, wall t4',
      'Hot face: alumina-silica brick t115 (study fab-page value - hold, W12) with the castable crown over the chamber',
      'Burner-tube pass through the -X wall and brick; drain pass in the floor',
      'Welds per the unit WORK_ORDER route (CS fillet welds, ISO 2553); general tolerance ISO 2768-m'],
     "Fabricated part sheet: shell, brick lining, castable crown."),
    ("burner01", burner, (0, 1, 0),
     [f'310S radiant burner tube OD {M["burner_tube"]["od_mm"]:g} at z 600 with the burner block on -X',
      'Combustion products stay inside the tube (duty section 3); stoichiometry per TURNS2012',
      'Dry flue duct with the N1 takeoff on +Y; flue path dry above the acid dew point to MET_SCRUB',
      'Hearth rail on the chamber floor; burner train purchased at fabrication (W12)'],
     "Fabricated part sheet: radiant tube, burner block, flue, hearth rail."),
    ("aux01", aux, (1, -0.5, 0.7),
     ['Controls cabinet 0.05 kW connected (node design) - purchased per plan rule 6, drawn '
      'as its envelope; standby unit, energized only on the IND_MELT outage (A-M-282)',
      'Plinth with 8 x M12 wedge anchors (fasteners.csv item 1); 12 x M10 8.8 studs on the '
      'roof hatch and burner-block clamp (item 2)',
      'Connection hardware DN15 open-bore tube (lib/dn Sch 40 table), flush at the envelope faces'],
     "Fabricated part sheet: controls bay, plinth, connection hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: furnace shell at the -X end, controls bay +X; flue leaves +Y at z 600, vent riser on the roof',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/comb_heat.step) is the solids of record',
      'Standby tertiary alternate: the machine is real, the design-day rate is zero on the '
      'graph (duty section 2)'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/comb_heat.py", f"models/mfg/{unit}/draw_comb_heat.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ['- Standby tertiary N+1 alternate drawn per duty section 3 (A-M-282/A-M-283): real machine, '
     'standby-zero design-day rate; named in the BOM rows and the WORK_ORDER',
     '- Alumina-silica brick + castable crown hot face on the mild-steel shell; 310S radiant '
     'burner tube keeps combustion products off the charge (duty section 3); CA 0 mm (AQS-STD-001)',
     '- Purchased controls cabinet (0.05 kW connected, node design) drawn as its envelope per '
     'plan rule 6; burner train purchased at fabrication (W12)'],
    "A-core (route hold)")

"""VAC_IND drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, chamber01 (vacuum chamber + lid +
insulation package), melt01 (crucible + ISM coil + pour hardware), aux01 (PSU
bay + tilt hydraulics + connection hardware), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets, step_export  # noqa: E402

ns = runpy.run_path(HERE / "vac_ind.py")
parts, R = ns["parts"], ns["report"]
unit = "VAC_IND"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


chamber = union_all([parts["chamber_shell"], parts["chamber_lid"], parts["fibre_lining"]])
melt = union_all([parts["crucible_jacket"], parts["ism_coil"], parts["pour_lip"],
                  parts["trunnion_pins"]])
aux = union_all([parts["psu_cabinet"], parts["tilt_frame"], parts["plinth"]])
body = union_all(list(parts.values()))
full = body

L, W, H = [float(v) for v in R["size_mm"]]
M = R["machine"]
S = R["standby"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm overall - the node N+1 rated envelope (A-M-282), filled exactly',
      'Vacuum induction skull-melt (ISM) furnace, N+1 diverse standby of IND_MELT: '
      f'{S["basis"]}',
      '304L vacuum chamber on the plinth, PSU bay on +X, tilt hydraulics floor bay',
      'Water-cooled Cu crucible OD 120 - no wetted-refractory interface (duty section 3)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     [f'Chamber shell t{M["chamber"]["wall_mm"]:g} 304L (study fab-page value - hold, W12), '
      f'ceramic-fibre insulation t40 inside the vacuum boundary (duty section 3)',
      'Chamber z 60..1200 on the plinth; lid clamp studs in fasteners.csv; '
      f'PSU {M["psu"]["bay"]}',
      'The 2 kg design-case skull melt (node design) is drawn as a process-inventory solid, not a BOM part',
      'General tolerance ISO 2768-m unless noted'],
     "General arrangement, side elevation. Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     [f'{R["nozzle_count_schedule"]} schedule rows of docs-authority/nozzles/VAC_IND.csv '
      'at tag, face and bore',
      'N1/N3 DN15 melt rows +Y at z 600 flush at the envelope face; N2 solids charge port '
      '-Y at z 160 (drawn at DN15, bore not calculated, W4)',
      'N4 DN15 drain through the plinth, flush at the envelope bottom (50 datum); '
      'N5 DN15 vent riser on the chamber lid, flush at the envelope top (800 datum is the '
      'schedule placeholder - hold, W12)',
      'Schedule inlet/outlet faces mapped to compass by the registered layout '
      '(params.json layout block); atmospheric hose makeup at the face (duty section 4)'],
     "Connection orientation, top view. Tags/faces/bore per the schedule."),
    ("chamber01", chamber, (0, 1, 0),
     [f'304L vacuum chamber {M["chamber"]["od_mm"][0]:g} x {M["chamber"]["od_mm"][1]:g} '
      f'x z {M["chamber"]["z_mm"][0]:g}..{M["chamber"]["z_mm"][1]:g}, shell t6, lid t40',
      'Passes shown: drain through the floor, vent in the lid, charge port -Y, melt rows +Y, coil-lead +X',
      'Insulation: ceramic-fibre board t40 inside the vacuum boundary (duty section 3)',
      'Welds per the unit WORK_ORDER route; leak test at 1.3 x the study chamber duty '
      '(W10); general tolerance ISO 2768-m'],
     "Fabricated part sheet: vacuum chamber, lid and insulation package."),
    ("melt01", melt, (0, 1, 0),
     [f'Water-cooled Cu crucible OD {M["crucible"]["od_mm"]:g} x {M["crucible"]["h_mm"]:g}, '
      f'jacket wall {M["crucible"]["wall_mm"]:g} - the 2 kg ISM design case',
      f'ISM coil, {M["coil"]["turns"]} turns x OD {M["coil"]["tube_od_mm"]:g} Cu, lead exits '
      '+X through the insulation package to the PSU bay',
      'Tilt pour about the trunnion axis at z 500; pour lip serves the +Y melt rows at z 600',
      'Coil cooling-water circuit is loop hardware, not modeled (WORK_ORDER W12)'],
     "Fabricated part sheet: melt zone (crucible, coil, pour hardware)."),
    ("aux01", aux, (1, -0.5, 0.7),
     ['PSU cabinet 15 kW connected (node design) - purchased per plan rule 6, drawn as its '
      'envelope; energized only on the IND_MELT outage (A-M-282)',
      'Tilt-frame hydraulics bay; the actuator package is purchased at fabrication (W12)',
      'Plinth with 8 x M12 wedge anchors (fasteners.csv item 1); 12 x M10 A4-70 lid and '
      'cabinet-rail studs (item 2)',
      'Connection hardware DN15 open-bore tube (lib/dn Sch 40 table), flush at the envelope faces'],
     "Fabricated part sheet: PSU bay, tilt hydraulics, plinth, connection hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: chamber at the -X end, PSU bay +X; melt leaves +Y at z 600, '
      'charge enters -Y at z 160',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/vac_ind.step) is the solids of record',
      'Standby N+1 alternate: the machine is real, the design-day rate is zero on the '
      'graph (duty section 2)'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/vac_ind.py", f"models/mfg/{unit}/draw_vac_ind.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ['- Standby N+1 alternate drawn per the node design block (A-M-282/A-M-283): real machine, '
     'standby-zero design-day rate; named in the BOM rows and the WORK_ORDER',
     '- Water-cooled Cu crucible per duty section 3: no wetted-refractory interface; 304L vacuum '
     'chamber; CA 0 mm (AQS-STD-001)',
     '- Purchased PSU cabinet (15 kW connected, node design) drawn as its envelope per plan rule 6'],
    "A-core (route hold)")

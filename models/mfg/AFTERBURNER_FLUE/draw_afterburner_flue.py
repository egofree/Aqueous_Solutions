"""AFTERBURNER_FLUE drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, spool01 (duct + isolating flange),
insul01 (insulation jacket), aux01 (branch connections + trough), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets, step_export  # noqa: E402

ns = runpy.run_path(HERE / "afterburner_flue.py")
parts, R = ns["parts"], ns["report"]
unit = "AFTERBURNER_FLUE"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


spool = parts["spool"]
insul = parts["insulation"]
aux = union_all([parts["plinth"], parts["nozzles"]])
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
S = R["spool"]
LL = R["line_list"]
X = R["nozzles_drawn"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm envelope - the node size_mm ({R["size_basis"]})',
      f'Flue duct spool {S["dn"]} OD {S["od_mm"]:g}, wall {S["wall_mm"]:g} mm '
      '(ASME B36.10M Sch 40 named values - outside the lib DN15-DN50 table, hold '
      'W12), 1000 mm representative spool of the 20 m run, bore open both ends',
      'Insulation jacket 40 mm (study thickness, hold W12) over the run; dielectric '
      'isolating flange at the FLUE_KO end (AQS-STD-002 section 4.3)',
      'Material 316L per duty section 3 (issued); the node design block says CS - '
      'conflict carried as a hold (W12), nothing resized'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['The duct sits at the box centre (y 300, z 400), welded in the trough plinth '
      'to its centreline (the HDR_CO2 trough-mount idiom)',
      f'A node-design sizing: required bore {S["id_req_mm"]:g} mm at 8 m/s, DN100 '
      f'seat; the Sch 40 bore {S["id_mm"]:g} mm sits inside the seat; nothing resized',
      'Route hold: the flue_junction class has no plan section 4 route class - '
      'A-core acceptance with the hold named; the A-PIPE idiom follows the node '
      'duct design (COMB_HEAT/RES_HEAT precedent)'],
     "General arrangement, side elevation (end view). Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     ['5 schedule rows of docs-authority/nozzles/AFTERBURNER_FLUE.csv at tag, face '
      'and bore',
      'N1 DN15 (flue from the afterburner) and N2 DN25 (combustion air) on -Y at z '
      '160; N3 DN25 (flue N2/O2/CO2/NOx to FLUE_KO) on +Y at z 600',
      'N4 drain flush at the envelope bottom (50 datum); N5 vent flush at the '
      'envelope top (800 datum is the box top; duty section 4: stays on the gas '
      'edge, not the room)',
      'Atmospheric tube stubs per duty section 4; the schedule rating column '
      '(Class 150) carried verbatim as text; branch stubs stop at the insulation '
      'surface'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("spool01", spool, (0, 1, 0),
     [f'Duct {S["dn"]} OD {S["od_mm"]:g} x wall {S["wall_mm"]:g}, 1000 mm '
      'representative spool; bore open at both spool ends',
      f'{S["run_basis"]}',
      'Dielectric isolating flange OD 190 x 20 at the +X (FLUE_KO) end per '
      'AQS-STD-002 section 4.3'],
     "Fabricated part sheet: duct spool + isolating flange."),
    ("insul01", insul, (0, 1, 0),
     [f'Insulation jacket: OD {S["od_mm"] + 2 * S["insulation_mm"]:g} x {L - 20:g} '
      'over the duct run; the isolating-flange end stays bare',
      'Duty section 3: insulated to hold the wall above the acid dew point (M7; '
      'dew point held)',
      'Thickness 40 mm is a study value; AQS-THM-003 states no thickness for this '
      'line (hold, W12)'],
     "Fabricated part sheet: insulation jacket."),
    ("aux01", aux, (0, 1, 0),
     ['Trough plinth 1000 x 600 x 20 (AQS-MOD-002 dry service); 8 M10 slab anchors '
      '(fasteners.csv)',
      'Branch connections DN15/DN25 as open-bore tube stubs from the envelope face '
      'to the insulation surface; atmospheric per duty section 4',
      f'The A-PIPE line list of record is line_list.csv: {LL["rows"]} rows (MAIN '
      'spool + issued lines), generated from the graph edges and AQS-PIP-004; no '
      'new edge'],
     "Fabricated part sheet: trough + branch connections."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: flue and combustion air in on -Y, flue to the knock-out '
      'out on +Y; drain and vent on the run centreline',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/afterburner_flue.step) is the solids of record',
      'Tracker --check green; acceptance A-core (route hold) per AQS-PLAN-006 '
      'section 5'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/afterburner_flue.py", f"models/mfg/{unit}/draw_afterburner_flue.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/line_list.csv", f"models/mfg/{unit}/check.json",
     f"models/mfg/{unit}/WORK_ORDER.md"],
    [f"- A-PIPE line list: line_list.csv generated from the unit's graph edges and "
     f"docs-authority/LINE_LIST.md (AQS-PIP-004): {LL['rows']} rows (MAIN spool + "
     f"{LL['rows'] - 1} issued lines), tag/from/to/DN/class/service/rating; edge "
     "coverage complete, no new edge",
     "- Spool: DN100 OD 114.3 x wall 6.02 (ASME B36.10M Sch 40 named values), "
     "1000 mm representative spool of the 20 m node-design run; the 102.26 mm bore "
     "sits inside the DN100 seat over the 17 mm required bore; nothing resized",
     "- Route hold: no plan section 4 route class for flue_junction - A-core with "
     "the hold named; the A-PIPE idiom follows the node duct design",
     "- Material: 316L per duty section 3 (issued selection); the node design "
     "block says CS Sch 40 insulated per AQS-THM-003 - conflict carried as a hold "
     "(W12); insulation thickness 40 mm a study value (hold, W12)"],
    "A-core (route hold)")

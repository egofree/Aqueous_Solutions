"""RF_HEAT drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
No nozzle-orientation sheet: there is no piped process connection on the graph
(duty section 4, no schedule issued). Sheets: ga_front, ga_side, shell01 (casing
+ lid + fibre hot face), melt01 (crucible + pedestal + RF coil + enclosure),
aux01 (RF cabinet + plinth), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets, step_export  # noqa: E402

ns = runpy.run_path(HERE / "rf_heat.py")
parts, R = ns["parts"], ns["report"]
unit = "RF_HEAT"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


shell = union_all([parts["casing"], parts["lid"], parts["fibre_lining"]])
melt = union_all([parts["crucible"], parts["crucible_pedestal"], parts["rf_coil"],
                  parts["coil_enclosure"], parts["coil_leads"]])
aux = union_all([parts["plinth"], parts["rf_cabinet"]])
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
M = R["machine"]
S = R["standby"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm overall - the node N+1 rated envelope (A-M-282), filled exactly',
      'RF preheat/hold unit, N+1 diverse standby of IND_MELT at equal melt duty: ' + S["state"],
      'Clay-graphite crucible + ceramic-fibre hot face + CS casing (the IND_MELT lining class, duty section 3)',
      'Water-cooled Cu RF coil inside its enclosure; RF/PSU cabinet on the +X bay - purchased envelope'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     [f'Casing t{M["casing"]["wall_mm"]:g} CS (study fab-page value - hold, W12), '
      f'fibre hot face t{M["lining"]["fibre_mm"]:g} (duty section 3)',
      f'Coil: {M["coil"]["turns"]} turns x OD {M["coil"]["tube_od_mm"]:g} Cu, 100-400 kHz '
      'through-coil (node design freq_kHz); cooling-water circuit is loop hardware (W12)',
      'Crucible D110 x 165 clay-graphite - the 10 kg class consumable, buy row',
      'General tolerance ISO 2768-m unless noted'],
     "General arrangement, side elevation. Shop, not stamped."),
    ("shell01", shell, (0, 1, 0),
     [f'CS casing {M["casing"]["od_mm"][0]:g} x {M["casing"]["od_mm"][1]:g} '
      f'x z {M["casing"]["z_mm"][0]:g}..{M["casing"]["z_mm"][1]:g}, wall t4, lid t40 with clamp studs',
      'Ceramic-fibre hot face t150 (duty section 3, the IND_MELT lining class)',
      'Welds per the unit WORK_ORDER route (CS fillet welds, ISO 2553); general tolerance ISO 2768-m'],
     "Fabricated part sheet: casing, lid, fibre hot face."),
    ("melt01", melt, (0, 1, 0),
     ['Clay-graphite crucible on its pedestal - consumable, buy row (change-out at the unit task 12 work order)',
      'Water-cooled Cu RF coil in its enclosure: the enclosure keeps the coil out of the melt space (duty section 3)',
      'Coil leads exit +X through the casing to the RF cabinet bay',
      'The quartz isolation-sleeve alternative applies only under flux vapours - not drawn (hold, W12)'],
     "Fabricated part sheet: crucible, pedestal, RF coil, enclosure."),
    ("aux01", aux, (1, -0.5, 0.7),
     ['RF generator / PSU cabinet 5 kW connected (node design) - purchased per plan rule 6, '
      'drawn as its envelope; standby unit, energized only on the IND_MELT outage (A-M-282)',
      'Plinth with 8 x M12 wedge anchors (fasteners.csv item 1); 12 x M10 8.8 studs on the '
      'lid clamp and enclosure cover (item 2)',
      'No piped process connection on the graph - no nozzle hardware (duty section 4; hold, W12)'],
     "Fabricated part sheet: RF cabinet, plinth."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: furnace casing at the -X end, RF cabinet bay +X; lid opens upward',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/rf_heat.step) is the solids of record',
      'Standby N+1 alternate: the machine is real, the design-day rate is zero on the '
      'graph (duty section 2)'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))

# build log written by hand: the sheets.build_log nozzle line assumes an issued
# schedule, and this unit has none (duty section 4) - the honest line is written below.
import sys  # noqa: E402
import cadquery as cq  # noqa: E402

dims = " x ".join(f"{v:g}" for v in R["bbox_mm"])
env = " x ".join(f"{v:g}" for v in R["size_mm"])
lines = [
    f"# Build log - {unit}",
    "",
    f"Date: {sheets.deterministic_date()}. Authority: AQS-PLAN-006 section 5 (acceptance) "
    "A-core (route hold); MFG_MODEL_PLAN (AQS-PLAN-006).",
    f"Graph: `flow_graph/plant_flow_graph.json` (duty sheet "
    f"`docs-authority/duties/{unit}.md`; envelope per `models/mfg/{unit}/params.json`).",
    "",
    "## Tool versions",
    "",
    f"- CadQuery {cq.__version__} (CADQUERY_PYTHON)",
    f"- Python {sys.version.split()[0]}; build run headless via "
    f"`python3 models/mfg/{unit}/{unit.lower()}.py`",
    "",
    "## Checks",
    "",
    f"- Build bbox {dims} mm against the {env} mm envelope: "
    + ("inside (tracker check green)" if R["inside_size_mm"] else "OVER - misfit reported"),
    f"- Solid source: build export `models/mfg/{unit}/export/{unit.lower()}.step`; export STL "
    f"closed and manifold, {R['solids']} solid(s); `cad/stl/{unit}.stl` replaced from the build "
    "(ASCII, metres)",
    "- Nozzles: no piped process connection on the graph; no nozzle schedule is issued "
    "(duty section 4) - no nozzle hardware drawn (hold, WORK_ORDER W12)",
    "- Standby N+1 alternate drawn per the node design block (A-M-282/A-M-232): real machine, "
    "standby-zero design-day rate; named in the BOM rows and the WORK_ORDER",
    "- Clay-graphite crucible + ceramic-fibre hot face + CS casing per duty section 3 (the "
    "IND_MELT lining class); CA 0 mm (AQS-STD-001); the crucible is the purchased consumable",
    "- Purchased RF/PSU cabinet (5 kW connected, node design) drawn as its envelope per plan "
    "rule 6; the coil cooling-water circuit is loop hardware (W12)",
    f"- BOM `models/mfg/{unit}/bom.csv` (generated from the model: qty, material, mass, "
    "make-or-buy); fasteners and WORK_ORDER beside it",
    f"- Drawing set `models/mfg/{unit}/drawings/` (GA front/side, part sheets, iso; "
    "title blocks per AQS-DWG-002); no nozzle sheet - no schedule",
    "",
    "## Sources",
    "",
    f"- `models/mfg/{unit}/{unit.lower()}.py`",
    f"- `models/mfg/{unit}/draw_{unit.lower()}.py`",
    f"- `models/mfg/{unit}/bom.csv`",
    f"- `models/mfg/{unit}/fasteners.csv`",
    f"- `models/mfg/{unit}/check.json`",
    f"- `models/mfg/{unit}/WORK_ORDER.md`",
    f"- build export `models/mfg/{unit}/export/{unit.lower()}.step`",
    "",
    "Status: accepted per AQS-PLAN-006 section 5 A-core (route hold); holds named in "
    "WORK_ORDER W12.",
]
(HERE / "build_log.md").write_text("\n".join(lines) + "\n")
print(json.dumps({"build_log": "written (no-schedule variant)"}))

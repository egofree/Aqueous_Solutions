"""FORGE drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
No nozzle-orientation sheet: there is no piped process connection on the graph
(duty section 4, no schedule issued). Sheets: ga_front, ga_side, frame01
(housings + crown + bolster), die01 (ram group + H13 die blocks + guard rail),
aux01 (HPU skid + control pedestal + plinth), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets                                       # noqa: E402

ns = runpy.run_path(HERE / "forge.py")
parts, R = ns["parts"], ns["report"]
unit = "FORGE"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


frame = union_all([parts["housing_a"], parts["housing_b"], parts["crown"], parts["bolster"]])
die = union_all([parts["ram_cylinder"], parts["ram_platen"], parts["die_top"],
                 parts["die_bottom"], parts["guard_rail"]])
aux = union_all([parts["plinth"], parts["hpu_skid"], parts["control_pedestal"]])
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
M = R["machine"]
S = R["standby"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm overall - the node N+1 rated envelope (A-M-282), filled exactly',
      'Open-die hydraulic press, N+1 former of ROLL: ' + S["state"],
      'Twin-housing frame with crown, bolster bed mid-height, ram group between the housings',
      'Node design ram and press_t rating; H13 die blocks are the consumable buy set'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Cast-steel housings and platens (duty section 3, DIETER1988); study sections (hold, W12)',
      'HPU skid on the +X bay and control pedestal on the -X floor - purchased envelopes (plan rule 6)',
      'Die-zone guard rail between the bays (A-MACH: guard drawn)',
      'General tolerance ISO 2768-m unless noted'],
     "General arrangement, side elevation. Shop, not stamped."),
    ("frame01", frame, (0, 1, 0),
     [f'Housing plates at x {M["frame"]["housing_x_mm"][0]:g} and x {M["frame"]["housing_x_mm"][3]:g}, '
      f'crown beam z {M["frame"]["crown_z_mm"][0]:g}..{M["frame"]["crown_z_mm"][1]:g}',
      f'Bolster bed z {M["bolster"]["z_mm"][0]:g}..{M["bolster"]["z_mm"][1]:g} between the housings',
      'Crown-to-housing ties and bolster hold-downs in fasteners.csv (item 2, M24)',
      'Welds and fits per the unit WORK_ORDER route; general tolerance ISO 2768-m'],
     "Fabricated part sheet: housings, crown, bolster."),
    ("die01", die, (0, 1, 0),
     [f'Ram group: cylinder to node design ram_mm {M["ram"]["dia_mm"]:g} with platen',
      'H13 die block pair t120 (open-die flat dies) - consumable buy set (duty section 3, ASM_V1)',
      'Die-zone guard rail on 4 posts x 2 tiers (A-MACH: guard drawn)',
      'The re-cuttable cast alternative is the duty alternative row (not drawn)'],
     "Fabricated part sheet: ram group, die blocks, guard rail."),
    ("aux01", aux, (1, -0.5, 0.7),
     ['Hydraulic power unit skid 11 kW connected (node design) - purchased per plan rule 6, '
      'drawn as its envelope; standby unit, energized only on the ROLL outage (A-M-282)',
      'Control pedestal - purchased envelope; plinth with 8 x M16 wedge anchors (fasteners.csv '
      'item 1) and 8 x M24 studs (item 2)',
      'No piped process connection on the graph - no nozzle hardware (duty section 4; hold, W12)'],
     "Fabricated part sheet: HPU skid, control pedestal, plinth."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: control pedestal -X, press frame centre, HPU bay +X; die zone between the housings',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/forge.step) is the solids of record',
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
    "A-core, A-SC (route hold); MFG_MODEL_PLAN (AQS-PLAN-006).",
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
    "- Standby N+1 alternate drawn per the node design block (A-M-282/A-M-283): real machine, "
    "standby-zero design-day rate; named in the BOM rows and the WORK_ORDER",
    "- A-MACH: die-zone guard rail and slab anchors drawn; HPU skid and control pedestal are "
    "the purchased items named with the node rating",
    "- H13 die pair is the purchased consumable (buy row); cast-steel frame per duty section 3; "
    "CA 0 mm (AQS-STD-001)",
    "- A-SC: the press forges the bar stock the shop uses; make rows flagged and W11 "
    "cross-references AQS-BOM-SC-001",
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
    "Status: accepted per AQS-PLAN-006 section 5 A-core, A-SC (route hold); holds named in "
    "WORK_ORDER W12.",
]
(HERE / "build_log.md").write_text("\n".join(lines) + "\n")
print(json.dumps({"build_log": "written (no-schedule variant)"}))

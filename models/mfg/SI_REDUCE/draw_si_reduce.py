"""SI_REDUCE drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, retort01 (casing + brick + hot face + hearth), top01
(lid + hopper + clamp ring), band01 (heater band + plinth), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets, step_export  # noqa: E402

ns = runpy.run_path(HERE / "si_reduce.py")
parts, R = ns["parts"], ns["report"]
unit = "SI_REDUCE"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


retort = union_all([parts["casing"], parts["brick_backup"], parts["hot_face"],
                    parts["bore"], parts["clamp_ring"]])
top = union_all([parts["hopper"], parts["clamp_ring"], parts["casing"]])
band = union_all([parts["heater_band"], parts["plinth"]])
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
M = R["machine"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm envelope - the node size_mm ({R["size_basis"]}); '
      'the retort under-fills the box by design (the batch class sets it)',
      'Carbothermic silicon reduction retort per the duty section 3 lining stack '
      '(X-MAT-22; SCHACHT2004 ch. 8; CRC_SI benchmark): mild-steel casing OD 700 '
      'with alumina brick backup 60 mm and graphite hot face 40 mm (dry, M7)',
      'Kroll-class retort idiom shared with the AQS-DUTY-072 pot-cell lineage '
      '(TI_CELL train); charge hopper on the lid (dry char + silica feed, duty '
      'section 3)',
      'Heater band envelope, node continuous 5.0 kW (X-SPEC carbothermic study '
      'class); purchased per plan rule 6'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Retort on the plinth centre (x 600, y 500); casing z 0..1260, lid + clamp '
      'ring + hopper to z 1540; heater band box around the lower shaft',
      'Duty (node design block): si_kgd 1.8, sio2_kgd 3.85, char_kgd 1.924 - '
      'carbothermic silicon for the PV cell line (SOLAR_PV_CELL draw)',
      'No nozzles: duty section 4 states no piped process connection and no '
      'schedule issued; the CHAR_TO_SI feed is a solids edge with no rate',
      'Route hold carried by name: furnace has no AQS-PLAN-006 section 4 class'],
     "General arrangement, side elevation (end view). Shop, not stamped."),
    ("retort01", retort, (0, 1, 0),
     ['Lining stack section: casing wall 6 mm (study), alumina brick backup 60 mm '
      '(buy-row charge, supplier TDS governs), graphite hot face 40 mm (dry, M7)',
      f'Hearth bore {M["lining"]["bore_mm"]:g} mm, hearth floor disc at the base '
      'head; shell radii are study values (hold, WORK_ORDER W12)',
      'CA 0 mm - dry, non-hydrocarbon furnace service (AQS-STD-001); the '
      'silicon-carbide hot-face alternative is the duty alternative row (not drawn)'],
     "Fabricated part sheet: casing + brick backup + hot face."),
    ("top01", top, (0, 0, -1),
     ['Lid plate with clamp ring (8 M12 clamp studs, fasteners.csv)',
      'Charge hopper cone on the lid with hatch box: duty section 3 dry char and '
      'silica-class feed handling (sio2_kgd 3.85 + char_kgd 1.924 per si_kgd 1.8)',
      'Hopper size is a study value (hold, WORK_ORDER W12)'],
     "Fabricated part sheet: lid + hopper + clamp ring, top view."),
    ("band01", band, (0, 1, 0),
     ['Heater band envelope around the heating zone: node continuous_kw 5.0 kW '
      '(X-SPEC carbothermic study class); purchased per plan rule 6',
      'Heater-band envelope mass is a table-density placeholder until the maker '
      'TDS quotes (hold, WORK_ORDER W12)',
      f'Plinth {L:g} x {W:g} x 20 with 8 slab anchors (AQS-MOD-002 dry service)'],
     "Fabricated part sheet: heater band + plinth."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: charge in at the lid hopper; no piped connections on the '
      'graph (duty section 4); product tap not named on the node or duty - none '
      'drawn (hold, WORK_ORDER W12)',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/si_reduce.step) is the solids of record',
      'Tracker --check green; acceptance A-core per AQS-PLAN-006 section 5 '
      '(route hold: furnace has no section 4 class)'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/si_reduce.py", f"models/mfg/{unit}/draw_si_reduce.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ["- Carbothermic reduction retort per the duty section 3 lining stack "
     "(X-MAT-22; SCHACHT2004 ch. 8): mild-steel casing OD 700, alumina brick "
     "backup 60 mm, graphite hot face 40 mm (dry, M7); Kroll-class retort idiom "
     "(AQS-DUTY-072 lineage)",
     "- Charge hopper on the lid (dry char + silica feed handling, duty section "
     "3); heater band envelope at the node 5.0 kW continuous rating, purchased "
     "per plan rule 6",
     "- No nozzles: duty section 4 states no piped process connection and no "
     "schedule issued; route hold carried by name (furnace class); shell radii "
     "are study values (holds, WORK_ORDER W12)"],
    "A-core")

# no nozzle schedule exists for this unit: replace the lib's schedule line with
# the no-schedule wording the FORGE precedent carries (no dangling CSV reference)
log = HERE / "build_log.md"
s = log.read_text()
s = s.replace(
    f"- Nozzles: all {R['nozzle_count_schedule']} rows of "
    f"`docs-authority/nozzles/{unit}.csv` present at face, height and bore "
    "(per-tag notes in check.nozzles_drawn)",
    "- Nozzles: no piped process connection on the graph; no nozzle schedule is "
    "issued (duty section 4) - no nozzle hardware drawn (hold, WORK_ORDER W12)")
log.write_text(s)

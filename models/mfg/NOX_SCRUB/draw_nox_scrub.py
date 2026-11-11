"""NOX_SCRUB drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, sh01 (column shell + skirt + plinth),
in01 (packed internals), aux01 (connection hardware), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets, step_export  # noqa: E402

ns = runpy.run_path(HERE / "nox_scrub.py")
parts, R = ns["parts"], ns["report"]
unit = "NOX_SCRUB"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


shell = union_all([parts["plinth"], parts["skirt"], parts["shell"]])
internals = union_all([parts["support"], parts["packing"], parts["distributor"],
                       parts["demister"]])
aux = parts["nozzles"]
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
C = R["column"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm overall - the X-PAR-03 envelope, filled exactly',
      f'CPVC column OD {C["D_mm"]:g}, wall {C["wall_mm"]:g} mm (study - hold, W12), '
      f'shell z {C["shell_z_mm"][0]:g}..{C["shell_z_mm"][1]:g}, top head, skirt, 600 x 600 plinth',
      f'Packed height {C["packed_mm"]:g} mm (node design) in two beds with a '
      'redistribution disc; distributor above, demister below the top head',
      'Duty: flue, leach off-gas and nitric vents, atmospheric (duty sections 4 and 6)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Internals at layout elevations: support grid z 700, beds z 715..1866.5 / 1881.5..3033, '
      'distributor z 3060, demister z 4043 (check.column)',
      'Connection barbs flush at the envelope faces on extension spools that cross the '
      'air gap and the shell wall (ray-set lengths)',
      'CPVC shell per duty section 3; packing and demister PP; node design block names '
      'PP-H - duty section 3 governs wetted materials (hold, W12)'],
     "General arrangement, side elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("nozzle_orient", full, (0, 0, -1),
     [f'{R["nozzle_count_schedule"]} schedule rows of docs-authority/nozzles/NOX_SCRUB.csv at tag, face and bore',
      'Inlets -Y: N1-N4 at z 400, N13-N15 at z 160, N11/N12 (nitric vents, no schedule '
      'datum) drawn at z 3400 in the gas space - hold, W12',
      'Outlets +Y at z 1500: N5 DN50, N6 DN15, N7 DN25, N8 DN50; N9 drain boss lapping '
      'the skirt ring; N10 vent riser on the top head to the 4103 top (2000 datum '
      'predates the sized column - hold, W12)',
      'The z 400 row packs the full DN 200 chord: the outer nozzles are near-tangent '
      '(set-on fillets are the fabricator s; a distribution manifold is the '
      'detail-design alternative - hold, W12)',
      'N16 cable power terminal: carried verbatim, not drawn'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("sh01", shell, (0, 1, 0),
     [f'Column shell OD {C["D_mm"]:g} x t {C["wall_mm"]:g}, z {C["shell_z_mm"][0]:g}..'
      f'{C["shell_z_mm"][1]:g}, flat top head 20, skirt with 2 mm laps, plinth 20',
      'CPVC per duty section 3 (AQS-STD-002 M1/M2/M5, 85 C leach off-gas); CA 0 mm '
      '(AQS-STD-001 polymer rule)',
      'Welds per the unit WORK_ORDER route (F-COL): sheet/pipe cut, thermoplastic weld, '
      'set-in ports, leak test',
      f'dP 1171 Pa across the packing is the node design figure (X-PAR-03)'],
     "Fabricated part sheet: column shell + skirt + plinth."),
    ("in01", internals, (0, 1, 0),
     ['A-COL internals as envelope solids: support grid, two packed beds (2303 mm total '
      'PP pall rings, in-house cut per the duty), redistribution disc, liquid '
      'distributor, PP mesh demister',
      'Ring count and mesh not modelled piece-wise; the node internals row is none, so '
      'the tracker records no internal solid (hold, W12)',
      'Bed elevations are the layout choice - the node design gives packed height only; '
      'no stage or HTU count is claimed anywhere (A-COL)'],
     "Fabricated part sheet: packed internals."),
    ("aux01", aux, (0, 1, 0),
     ['Connection hardware DN15/DN25/DN50 as atmospheric hose barbs (lib/nozzles.py); '
      'barb profile a study proportion, finished against the hose supplier print',
      'Schedule rating column (Class 150 / hose) carried verbatim as text - duty '
      'section 4: atmospheric tube or hose (W4 110 % rule: no process pressure)',
      'Extension spools cross from the envelope face to the shell along each port s '
      'own ray; per-tag positions in check.nozzles_drawn'],
     "Fabricated part sheet: connection hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: inlets -Y (z 160/400 rows and the gas-space nitric vents), '
      'outlets +Y at z 1500, drain at the skirt base, vent riser on the top head',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/nox_scrub.step) is the solids of record',
      'Build fills the X-PAR-03 envelope exactly; tracker --check green'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/nox_scrub.py", f"models/mfg/{unit}/draw_nox_scrub.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ["- A-COL: packing height (2303 mm in two beds), support grid, redistribution disc, "
     "liquid distributor and PP mesh demister are solids (envelope solids; ring count "
     "not modelled); no stage or HTU count is claimed anywhere",
     "- Internals basis: node design block (D 200, packed 2303, H 3803) and duty "
     "section 3 materials; bed elevations are the layout choice (hold, W12)"],
    "A-core + A-COL")

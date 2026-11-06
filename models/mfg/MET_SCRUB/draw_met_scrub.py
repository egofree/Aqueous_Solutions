"""MET_SCRUB drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, sh01 (column shell + skirt + plinth),
in01 (packed internals), aux01 (connection hardware), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets                                       # noqa: E402

ns = runpy.run_path(HERE / "met_scrub.py")
parts, R = ns["parts"], ns["report"]
unit = "MET_SCRUB"


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
      f'PVC-U column OD {C["D_mm"]:g}, wall {C["wall_mm"]:g} mm (study - hold, W12), '
      f'shell z {C["shell_z_mm"][0]:g}..{C["shell_z_mm"][1]:g}, top head, skirt, plinth',
      f'Packed height {C["packed_mm"]:g} mm (node design) in two beds with a '
      'redistribution disc; distributor above, demister below the top head',
      'Duty: metal-aisle fume and mist, 2520 m3/h at 1.5 m/s (duty section 2), '
      'atmospheric (duty sections 4 and 6)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Internals at layout elevations: support grid z 700, beds z 715..1866.5 / '
      '1881.5..3033, distributor z 3060, demister z 4043 (check.column)',
      'Connection barbs flush at the envelope faces on ray-set spools crossing the air '
      'gap and the shell wall; the DN300 air return is a plain stub spool',
      'PVC-U shell per duty section 3; the graph gives no gas temperature - above 60 C '
      'it would be CPVC (hold, W12)'],
     "General arrangement, side elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("nozzle_orient", full, (0, 0, -1),
     [f'{R["nozzle_count_schedule"]} schedule rows of docs-authority/nozzles/MET_SCRUB.csv at tag, face and bore',
      'Inlets -Y: N1 DN50, N2 DN50, N3 DN15 at z 400; N8 DN15 at z 160',
      'Outlets +Y at z 1500: N4 DN15, N5 DN15; N9 DN300 air return at z 600 (house OD '
      '323.9 stub, outside the lib hardware table - hold, W12)',
      'N6 drain boss lapping the skirt ring; N7 vent riser on the top head to the 4103 '
      'top (2000 datum predates the sized column - hold, W12)',
      'N10 cable power terminal: carried verbatim, not drawn'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("sh01", shell, (0, 1, 0),
     [f'Column shell OD {C["D_mm"]:g} x t {C["wall_mm"]:g}, z {C["shell_z_mm"][0]:g}..'
      f'{C["shell_z_mm"][1]:g}, flat top head 20, skirt with laps, plinth 20',
      'PVC-U per duty section 3 (AQS-STD-002 M1/M2); CA 0 mm (AQS-STD-001 polymer rule)',
      'Welds per the unit WORK_ORDER route (F-COL): sheet/pipe cut, thermoplastic weld, '
      'set-in ports, leak test',
      'dP 1171 Pa across the packing is the node design figure (X-PAR-03)'],
     "Fabricated part sheet: column shell + skirt + plinth."),
    ("in01", internals, (0, 1, 0),
     ['A-COL internals as envelope solids: support grid, two packed beds (2303 mm total '
      'PP pall rings, in-house cut per the node design), redistribution disc, liquid '
      'distributor, PP mesh demister',
      'Ring count and mesh not modelled piece-wise; the node internals row is none, so '
      'the tracker records no internal solid (hold, W12)',
      'Bed elevations are the layout choice - the node design gives packed height only; '
      'no stage or HTU count is claimed anywhere (A-COL)'],
     "Fabricated part sheet: packed internals."),
    ("aux01", aux, (0, 1, 0),
     ['Connection hardware DN15/DN50 as atmospheric hose barbs (lib/nozzles.py); '
      'barb profile a study proportion, finished against the hose supplier print',
      'Schedule rating column (Class 150) carried verbatim as text - duty section 4: '
      'atmospheric tube or hose (W4 110 % rule: no process pressure)',
      'Spools run from each port s own ray to 10 mm past the inner wall; per-tag '
      'positions in check.nozzles_drawn'],
     "Fabricated part sheet: connection hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: fume inlets -Y (z 160/400), outlets +Y (z 600 DN300 air '
      'return, z 1500 liquors), drain at the skirt base, vent riser on the top head',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/met_scrub.step) is the solids of record',
      'Build fills the X-PAR-03 envelope exactly; tracker --check green'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/met_scrub.py", f"models/mfg/{unit}/draw_met_scrub.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ["- A-COL: packing height (2303 mm in two beds), support grid, redistribution disc, "
     "liquid distributor and PP mesh demister are solids (envelope solids; ring count "
     "not modelled); no stage or HTU count is claimed anywhere",
     "- Internals basis: node design block (D 800, packed 2303, H 3803) and duty "
     "section 3 materials; bed elevations are the layout choice (hold, W12)"],
    "A-core + A-COL")

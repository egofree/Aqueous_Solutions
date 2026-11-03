"""BMED_UPW_POLISH drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, bench01 (plinth + deck + frame),
internals01 (RO/EDI/UV/pump envelopes + bypass run), aux01 (connection
hardware), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets                                       # noqa: E402

ns = runpy.run_path(HERE / "bmed_upw_polish.py")
parts, R = ns["parts"], ns["report"]
unit = "BMED_UPW_POLISH"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


bench = union_all([parts["plinth"], parts["deck"], parts["frame"]])
internals = union_all([parts["ro_modules"], parts["edi_stacks"], parts["uv_lamp"],
                       parts["ro_pump"], parts["bypass"]])
aux = parts["nozzles"]
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm envelope - the node size_mm '
      f'({R["size_basis"] or "node size_mm"}); the duty section 2 states no '
      'envelope - the node governs (hold W12)',
      'UPW polish skid per the node internals row and design block (X-MFG-34, '
      'A-M-176, AQS-DUTY-070): 2 flat-sheet TFC RO modules, 2 EDI stacks, the '
      'UV-TOC lamp, the RO pump, and the potable bypass run',
      'Every named internal is a solid envelope per plan rule 6; the module '
      'internals are the X-MFG-34 in-house design task, not invented (hold '
      'W12)',
      'Wetted hardware 316L per duty section 3 (UPW service); CA 0 mm '
      '(AQS-STD-001)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Node design figures carried: membrane_m2 0.2652 at the 6.859 bar feed, '
      'recovery 0.9547, EDI 0.39 W, UV 15 W, bypass 206.77 kg/d; A-M-176 '
      'basis 0.27 m2/module at 6.9 bar, 10 cell pairs at 4 V, 2 x 100% '
      'trains',
      'A-M-072 (RO 3.0 / EDI 0.5 kWh/m3) is the vendor-class energy basis, '
      'replaced by the X-MFG-34 in-house design and bench test - named hold '
      '(W12)',
      'Hold-down frame (40 x 40 posts + top rails) on the 20 mm plinth pins '
      'the registry box (X-PAR-04); 8 slab anchors'],
     "General arrangement, side elevation (end view). Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     ['7 schedule rows of docs-authority/nozzles/BMED_UPW_POLISH.csv at tag, '
      'face and bore',
      'N1 DN50 VCD distillate in on -Y at z 160; outlets on +Y at z 600: N2 '
      'DN25 UPW, N3 DN25 fab UPW, N4 DN15 remineralizer, N5 DN15 polish '
      'reject',
      'N6 drain flush at the envelope bottom (50 datum); N7 vent flush at '
      'the envelope top (800 datum is the box top)',
      'Atmospheric open-bore tube stubs per duty section 4 (atmospheric '
      'joints are hose, bore not calculated)'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("bench01", bench, (0, 1, 0),
     ['Skid deck on the 20 mm plinth inside the hold-down/guard frame (40 x '
       '40 posts, top rails), AQS-MOD-002 dry service',
       'The frame pins the registry box so the build fills the node envelope '
       '(X-PAR-04); 8 M10 slab anchors (fasteners.csv)',
       'Carbon steel (ASTM A500); dry structure outside the wetted 316L '
       'hardware'],
     "Fabricated part sheet: plinth, deck and hold-down frame."),
    ("internals01", internals, (1, -1, 1),
     ['Purchased-module envelopes per plan rule 6: 2 RO modules (120 dia x '
       '500, one per train), 2 EDI stacks (150 x 150 x 400), UV-TOC lamp '
       '(30 dia x 400), RO pump (120 x 120 x 150)',
       'Potable bypass run DN25 Sch 40 at y 470, z 260 with risers - the '
       'potable share bypasses RO/EDI (node internals row; bypass_kg_d '
       '206.77)',
       'Module and pump envelope sizes and the piping layout are the layout '
       'choice (WORK_ORDER W12); the 316L wetted hardware per duty section 3'],
     "Internals: RO/EDI/UV/pump envelopes and the bypass run."),
    ("aux01", aux, (0, 1, 0),
     ['Connection hardware DN15/DN25/DN50 as open-bore tube stubs flush at '
      'the envelope faces; atmospheric hose per duty section 4',
      'All 7 schedule rows present at tag, face, height and bore; per-tag '
      'positions in check.nozzles_drawn',
      'The schedule rating column (Class 150) carried verbatim as text'],
     "Fabricated part sheet: connection hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: distillate in on -Y, UPW/fab UPW/remin and reject '
      'out on +Y; drain at the bottom, vent at the top',
      f'Graph revision {R["graph_revision"]} is the model authority for this '
      'build; STEP (export/bmed_upw_polish.step) is the solids of record',
      'Tracker --check green; acceptance A-core + A-MACH per AQS-PLAN-006 '
      'section 5'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/bmed_upw_polish.py", f"models/mfg/{unit}/draw_bmed_upw_polish.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    ["- Skid per the node internals row and design block (X-MFG-34, A-M-176, "
     "AQS-DUTY-070): 2 flat-sheet TFC RO module envelopes (membrane_m2 "
     "0.2652, feed 6.859 bar, recovery 0.9547), 2 EDI stack envelopes "
     "(EDI_A 0.00973 A / 0.39 W), the UV-TOC lamp envelope (15 W), the RO "
     "pump envelope (2.6 W), and the potable bypass run (206.77 kg/d, 2 x "
     "100% trains per A-M-176)",
     "- A-M-072 vendor-class energy bases (RO 3.0 / EDI 0.5 kWh/m3) carried "
     "as a named hold pending the X-MFG-34 bench test; module internals are "
     "the X-MFG-34 design task, not invented (plan rule 6)",
     "- Hold-down frame pins the registry box so the build fills the envelope "
     "(X-PAR-04); anchors in fasteners.csv"],
    "A-core + A-MACH")

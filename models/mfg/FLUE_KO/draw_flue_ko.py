"""FLUE_KO drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, sh01 (shell + heads + plinth),
in01 (spool + mesh pad + weir + launder), aux01 (connection hardware), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets                                       # noqa: E402

ns = runpy.run_path(HERE / "flue_ko.py")
parts, R = ns["parts"], ns["report"]
unit = "FLUE_KO"


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


shell = union_all([parts["plinth"], parts["shell"]])
internals = union_all([parts["inlet_spool"], parts["mesh_pad"], parts["weir"],
                       parts["launder"]])
aux = parts["nozzles"]
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
K = R["ko_drum"]
I = K["internals"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm overall - the node registry envelope, filled '
      'exactly (the duty sheet unit-task-04 line 600 x 700 x 1100 is a hold, W12)',
      'Vertical FRP knock-out drum: shell OD 540, wall 8 mm (study - hold, W12), on '
      'a plinth with heads',
      'Internals per duty section 3: borosilicate inlet spool at z 300, PVDF mesh '
      'pad at z 620 on its support ring; weir and launder layout solids (sheet IN01)',
      'Flue knock-out to the NOx scrubber, atmospheric (duty sections 1, 3 and 6)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['S67 at 300 C enters the glass spool and is quenched by N8 (24.31 kg/d, '
      'X-SAF-07); the gas leaves below the FRP limit (duty section 3)',
      'Weir plate x 420..430 to z 360 divides settle from overflow; the launder '
      'trough lip overflows at z 360 into the sump (layout solids, W12)',
      'FRP vinyl ester with C-veil liner (AQS-STD-002 section 8 audit row); CA does '
      'not apply'],
     "General arrangement, side elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("nozzle_orient", full, (0, 0, -1),
     ['8 schedule rows of docs-authority/nozzles/FLUE_KO.csv at tag, face and bore',
      'N1/N2/N3/N8 flue and quench services in on -Y at z 160; N4/N5 gas out on +Y '
      'at z 600; per-tag positions in check.nozzles_drawn',
      'N6 drain boss on the base head (50 datum); N7 vent flush at the top head - '
      'the 800 datum IS the envelope top, drawn exact',
      'Atmospheric hose barbs; the schedule rating column (Class 150) carried '
      'verbatim as text - no flange drawn (duty section 4)'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("sh01", shell, (0, 1, 0),
     ['Shell OD 540 x wall 8 FRP vinyl ester with C-veil liner, z 40..760, heads, '
      'plinth',
      'Wall a study value - no authority states an FRP thickness (hold, W12)',
      'Fabrication per the unit WORK_ORDER route (F-VES): contact-moulded FRP over '
      'the liner, set-in ports, leak test'],
     "Fabricated part sheet: shell + heads + plinth."),
    ("in01", internals, (0, 1, 0),
     ['Borosilicate glass 3.3 inlet spool OD 110 x wall 3 at z 300, reach 300 mm '
      '(duty section 3; dims study, W12)',
      'PVDF mesh pad OD 508 x 16 at z 620 on a support ring OD 532 x ID 488 '
      '(duty section 3; dims study, W12)',
      'Weir to z 360 and launder trough (floor z 300, overflow lip z 360): layout '
      'solids from the separation duty, unsized (duty section 8, hold W12)'],
     "Fabricated part sheet: spool + mesh pad + weir + launder."),
    ("aux01", aux, (0, 1, 0),
     ['Connection hardware DN15/DN25/DN50 as atmospheric hose barbs '
      '(lib/nozzles.py); barb profile a study proportion, finished against the '
      'hose supplier print',
      'Schedule rating column (Class 150) carried verbatim as text - duty section 4 '
      '(atmospheric hose; W4 110 percent rule: no process pressure)',
      'Hardware PVDF per the all-polymer wetted basis (duty section 3: no metal '
      'wetted part)'],
     "Fabricated part sheet: connection hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: flue in on -Y at z 160 (quenched in the spool), gas out on '
      '+Y at z 600, drain at the base head, vent on the top head',
      f'Graph revision {R["graph_revision"]} is the model authority for this build; '
      'STEP (export/flue_ko.step) is the solids of record',
      f'Build fills the node registry envelope exactly; sump {R["holdup_m3"]} m3 '
      'reported, no residence derived (A-VES)'],
     "Isometric orientation sheet."),
]

print(json.dumps(sheets.export_sheets(unit, parts, R, SHEETS, HERE)))
sheets.build_log(
    unit, HERE, R,
    [f"models/mfg/{unit}/flue_ko.py", f"models/mfg/{unit}/draw_flue_ko.py",
     f"models/mfg/{unit}/bom.csv", f"models/mfg/{unit}/fasteners.csv",
     f"models/mfg/{unit}/check.json", f"models/mfg/{unit}/WORK_ORDER.md"],
    [f"- A-VES: the {R['holdup_m3']} m3 sump volume is reported - the duty claims "
     "no holdup for this class (section 8) and no residence time is derived",
     "- Materials per duty section 3: FRP vinyl ester + C-veil liner, borosilicate "
     "glass 3.3 spool, PVDF pad and hardware; no metal wetted part",
     "- Internals: the weir/launder separation layout is unsized (duty section 8) "
     "- named hold (W12)"],
    "A-core + A-VES")

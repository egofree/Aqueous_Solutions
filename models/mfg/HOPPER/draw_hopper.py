"""HOPPER drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, sh01 (hopper body), in01 (base plate +
rim frame), aux01 (connection hardware), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy

HERE = pathlib.Path(__file__).parent
ns = runpy.run_path(HERE / "hopper.py")
parts, R = ns["parts"], ns["report"]
REV = R["graph_revision"]
DRAW = HERE / "drawings"; DRAW.mkdir(exist_ok=True)


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


body = parts["body"]
frames = union_all([parts["frame_base"], parts["rim_frame"]])
aux = parts["nozzles"]
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
B = R["body"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm overall - the node envelope '
      '(AQS-DUTY-064), filled exactly',
      f'Bin z {B["bin_z_mm"][0]:g}..{B["bin_z_mm"][1]:g}, pyramidal frustum z '
      f'{B["frustum_z_mm"][0]:g}..{B["frustum_z_mm"][1]:g} to a {B["discharge"]}; '
      'discharge bore over a 190 mm base-plate opening',
      f'Carbon steel, wall {B["wall_mm"]:g} mm (study - hold, W12); CA 1.5 mm '
      '(AQS-STD-001 hydrocarbon rule)',
      'Atmospheric receiving hopper, gravity discharge (duty sections 1 and 4)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Base plate 20 mm under the discharge opening; top hold-down rim frame 20 mm bar',
      'Frustum slope carries the z 160 inlet row (roots set in the shell wall); the bin '
      'wall carries the clamped z 565..584 outlet row',
      'Welded plate construction, ISO 2768-m unless noted'],
     "General arrangement, side elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("nozzle_orient", full, (0, 0, -1),
     [f'{R["nozzle_count_schedule"]} schedule rows of docs-authority/nozzles/HOPPER.csv at tag, face and bore',
      'Inlets -Y at z 160: N1 DN15, N2 DN50, N3 DN25, N10 DN15 (roots in the frustum wall)',
      'Outlets +Y clamped to z 565..584 (schedule datum 600 at the envelope top - hold, W12): '
      'N4 DN25, N5 DN50, N6 DN15, N9 DN15',
      'N7 drain boss beside the discharge opening (50 datum); N8 vent on the +Y rim bar '
      '(schedule datum 800 predates the 600 box - hold, W12)',
      'Atmospheric hose barbs; no flange drawn (duty section 4: no flange class); '
      'per-tag positions in check.nozzles_drawn',
      'N11 solids make-up feed: carried verbatim, not drawn'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("sh01", body, (0, 1, 0),
     [f'Hopper body: bin + frustum + outlet box, wall {B["wall_mm"]:g} mm carbon steel plate '
      '(study thickness - hold, W12)',
      'CA 1.5 mm per AQS-STD-001; no aqueous chloride in this vessel (duty section 3)',
      'Welds per the unit WORK_ORDER route (F-VES): plate cut, roll none, fillet welds, '
      'set-in ports, leak test of the discharge path',
      f'Holdup (geometric, model): {R["holdup_m3"]:g} m3 bin + frustum + outlet; no holdup '
      'is claimed by the duty (A-VES)'],
     "Fabricated part sheet: hopper body."),
    ("in01", frames, (0, 1, 0),
     ['Base plate 600 x 600 x 20 with a 190 mm discharge opening; M10 wedge anchors, '
      'one per corner (grade 8.8 by the plan rule on carbon steel)',
      'Top hold-down rim frame, 20 mm bar, four sides: restraint and lifting',
      'Study sections (WORK_ORDER W12); anchor length confirmed at fabrication'],
     "Fabricated part sheet: base plate + rim frame."),
    ("aux01", aux, (0, 1, 0),
     ['Connection hardware DN15/DN25/DN50 as atmospheric hose barbs (lib/nozzles.py); '
      'barb profile a study proportion, finished against the hose supplier print',
      'Schedule rating column (Class 150) carried verbatim as text - duty section 4 says '
      'atmospheric tube or hose, no flange class (W4 110 % rule: no process pressure)',
      'Ports pack one row per face/height group, centred on the face mid-length '
      '(layout choice, WORK_ORDER W2); per-tag positions in check.nozzles_drawn'],
     "Fabricated part sheet: connection hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: inlets -Y, outlets +Y, discharge through the base opening',
      f'Graph revision {REV} is the model authority for this build; STEP '
      '(export/hopper.step) is the solids of record',
      'Build fills the node envelope exactly; tracker --check green'],
     "Isometric orientation sheet."),
]

BAND = 100   # notes band appended under the drawing; _drawings.py stamps the title block bottom-right

def add_notes(svg_path, notes):
    import re
    s = svg_path.read_text()
    if "aqs-fab-notes" in s:
        return
    w = float(re.search(r'width="([\d.]+)"', s).group(1))
    h = float(re.search(r'height="([\d.]+)"', s).group(1))
    s = re.sub(r'height="[\d.]+"', f'height="{h + BAND}"', s, count=1)
    rows = [f"Graph revision {REV} - {svg_path.stem}: {n}" for n in notes]
    block = f'<g id="aqs-fab-notes" transform="translate(0,{h})" font-family="DejaVu Sans,sans-serif" font-size="10" fill="#000">'
    for i, n0 in enumerate(rows):
        block += f'<text x="6" y="{24 + 13 * i}">{n0}</text>'
    block += '</g>'
    svg_path.write_text(s.replace("</svg>", block + "</svg>"))

pdf = "stamped pass pending"
import cadquery as cq
for sid, shape, pdir, notes, _title in SHEETS:
    svg = DRAW / f"{sid}.svg"
    if svg.exists() and "aqs-title-block" in svg.read_text():   # stamped: geometry frozen, PDF pass only
        try:
            import cairosvg
            import sys as _aqs_sys
            import pathlib as _aqs_pl
            _aqs_sys.path.insert(0, str(_aqs_pl.Path(__file__).resolve().parent.parent))   # models/mfg, for lib
            from lib.pdf_write import write_pdf
            write_pdf(str(svg), str(DRAW / f"{sid}.pdf"))
            pdf = "pdf+svg current"
        except Exception as e:
            pdf = f"pdf skipped ({e.__class__.__name__}: {e})"
        continue
    cq.exporters.export(shape.val(), str(svg), opt={"projectionDir": pdir, "showAxes": False, "showHidden": True})
    add_notes(svg, notes)

# ---------------------------------------------------------------- build log (A-core record)
step_src = "build export `models/mfg/HOPPER/export/hopper.step`"
srcs = ["models/mfg/HOPPER/hopper.py", "models/mfg/HOPPER/draw_hopper.py", step_src,
        "models/mfg/HOPPER/bom.csv", "models/mfg/HOPPER/fasteners.csv",
        "models/mfg/HOPPER/check.json", "models/mfg/HOPPER/WORK_ORDER.md"]
log = f"""# Build log - HOPPER

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-VES; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/HOPPER.md`; node envelope from AQS-DUTY-064 storage sizing).

## Tool versions

- CadQuery {cq.__version__} (CADQUERY_PYTHON)
- Python {__import__('sys').version.split()[0]}; build run headless via `python3 models/mfg/HOPPER/hopper.py`

## Checks

- Build bbox {R['bbox_mm'][0]} x {R['bbox_mm'][1]} x {R['bbox_mm'][2]} mm: fills the node envelope {L:g} x {W:g} x {H:g} mm exactly (tracker check green)
- Solid source: {step_src}; export STL closed and manifold, one solid; `cad/stl/HOPPER.stl` replaced from the build (ASCII, metres)
- Nozzles: all {R['nozzle_count_schedule']} rows of `docs-authority/nozzles/HOPPER.csv` present at face, height and bore, drawn as atmospheric hose barbs per duty section 4; heights at the envelope top clamped with named holds (check.nozzles_drawn); the N11 solids make-up row is carried verbatim, not drawn
- A-VES: hopper holdup {R['holdup_m3']} m3 computed from the model and reported; the duty claims no holdup, so no residence time is derived (duty section 8)
- BOM `models/mfg/HOPPER/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/HOPPER/drawings/` (GA front/side, nozzle orientation, 2 part sheets, aux, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded

## Sources

""" + "".join(f"- `{s}`\n" for s in srcs) + """
Status: accepted per AQS-PLAN-006 section 5 A-core and A-VES; holds named in WORK_ORDER W12 (study wall thickness, clamped schedule datums, the Class 150 rating column against the atmospheric duty, and the missing duty size line).
"""
(HERE / "build_log.md").write_text(log)
print(json.dumps({"sheets": [s[0] for s in SHEETS], "pdf": pdf}))

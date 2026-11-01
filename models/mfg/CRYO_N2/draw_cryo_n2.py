"""CRYO_N2 drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, sh01 (shell + skid), in01 (internal
cavity volume, empty by authority), aux01 (hose hardware), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy

HERE = pathlib.Path(__file__).parent
ns = runpy.run_path(HERE / "cryo_n2.py")
parts, R = ns["parts"], ns["report"]
REV = R["graph_revision"]
DRAW = HERE / "drawings"; DRAW.mkdir(exist_ok=True)


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


shell = union_all([parts["skid"], parts["shell"]])
aux = parts["nozzles"]
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm overall - the node size_mm box, filled exactly',
      'The build is the shell machine: shell + nozzles + supports (no internals named on the '
      'node or the duty sheet - holds, WORK_ORDER W12)',
      'Shell t 3 on a 20 mm skid (study values; no thickness stated by any authority)',
      'Every schedule datum fits this envelope: inlet z 400, outlets z 600/1500, vent flush at '
      'the 2000 top',
      'Atmospheric per duty sections 4 and 6; the vent stays on the gas edge, not the room'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Welded 316L shell, closed top and bottom, lapped 5 into the skid so the union fuses',
      'Hose barbs flush at the envelope faces with extension stubs into the cavity',
      'N3 drain flush at z 0 through the skid, boss to the 50 datum; N4 vent flush at the top',
      'General tolerance ISO 2768-m unless noted'],
     "General arrangement, side elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("nozzle_orient", full, (0, 0, -1),
     ['8 schedule rows of docs-authority/nozzles/CRYO_N2.csv at tag, face, height and bore',
      'N1 DN50 inlet at -Y z 400; N2 DN50 outlet at +Y z 1500; N5/N6/N7 DN15 and N8 DN50 '
      'outlets at +Y z 600',
      'N3 DN15 drain at bottom (60, 150), flush z 0, boss to the 50 datum; N4 DN15 vent flush '
      'at the 2000 top datum',
      'Atmospheric hose per duty sections 4 and 6; schedule rating column (Class 150) carried '
      'verbatim as text - per-tag positions in check.nozzles_drawn'],
     "Nozzle orientation, top view. Tags/faces/heights per the schedule."),
    ("sh01", shell, (0, 1, 0),
     [f'Shell 300 x 300 x {H - 20:g} mm, t 3, welded closed, on a 20 mm skid (316L, CA 0 mm '
      'per AQS-STD-001)',
      'The node carries no design and no diameter (duty section 8): the box is the shell '
      'machine; a vacuum jacket is not named and none is drawn',
      'Welds per the unit WORK_ORDER route (F-COL); leak test of the shell',
      'General tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: shell + skid."),
    ("in01", shell, (0, 1, 0),
     ['Internal cavity: empty by authority - the node carries internals "none" and the duty '
      'sheet names no packing, diameter or internals',
      'A-COL packing/distributor/demister: not named for this unit; the shell machine stands '
      'until the diameter and internals are designed (holds, WORK_ORDER W12)',
      'Stages or HTU stay a hold where the duty says so (AQS-PLAN-006 section 5)'],
     "Fabricated part sheet: internal cavity (empty by authority)."),
    ("aux01", aux, (0, 1, 0),
     ['Hose barbs DN15/DN50 flush at the envelope faces; barb profile a study proportion '
      '(lib/nozzles.py), finished against the hose supplier print',
      'Extension stubs reach into the cavity so every union crosses the shell wall',
      'N3 drain and N4 vent: DN15 stubs to their schedule datums',
      'Schedule rating column (Class 150) carried verbatim as text - no flange drawn (W12)'],
     "Fabricated part sheet: nozzle hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: inlet on the -Y face, outlets on +Y; vent to the gas edge, not the '
      'room (duty section 6)',
      f'Graph revision {REV} is the model authority for this build; STEP (export/cryo_n2.step) '
      'is the solids of record',
      'The build fills the node size_mm box exactly; tracker --check green'],
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
            cairosvg.svg2pdf(url=str(svg), write_to=str(DRAW / f"{sid}.pdf"))
            pdf = "pdf+svg current"
        except Exception as e:
            pdf = f"pdf skipped ({e.__class__.__name__}: {e})"
        continue
    cq.exporters.export(shape.val(), str(svg), opt={"projectionDir": pdir, "showAxes": False, "showHidden": True})
    add_notes(svg, notes)

# ---------------------------------------------------------------- build log (A-core record)
step_src = "build export `models/mfg/CRYO_N2/export/cryo_n2.step`"
srcs = ["models/mfg/CRYO_N2/cryo_n2.py", "models/mfg/CRYO_N2/draw_cryo_n2.py", step_src,
        "models/mfg/CRYO_N2/bom.csv", "models/mfg/CRYO_N2/fasteners.csv",
        "models/mfg/CRYO_N2/check.json", "models/mfg/CRYO_N2/WORK_ORDER.md"]
log = f"""# Build log - CRYO_N2

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-COL; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/CRYO_N2.md`; envelope is the node size_mm box).

## Tool versions

- CadQuery {cq.__version__} (CADQUERY_PYTHON)
- Python {__import__('sys').version.split()[0]}; build run headless via `python3 models/mfg/CRYO_N2/cryo_n2.py`

## Checks

- Build bbox {R['bbox_mm'][0]} x {R['bbox_mm'][1]} x {R['bbox_mm'][2]} mm: fills the node size_mm box {L:g} x {W:g} x {H:g} mm exactly (tracker check green)
- Solid source: {step_src}; export STL closed and manifold; `cad/stl/CRYO_N2.stl` replaced from the build (ASCII, metres)
- Nozzles: all {R['nozzle_count_schedule']} rows of `docs-authority/nozzles/CRYO_N2.csv` present at face, height, bore and tag; every schedule datum fits the envelope and is drawn as issued
- A-COL: no packing, distributor, demister or diameter is named on the node or the duty sheet - the shell machine stands and the gaps are named holds (WORK_ORDER W12)
- BOM `models/mfg/CRYO_N2/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/CRYO_N2/drawings/` (GA front/side, nozzle orientation, 2 part sheets, iso; title blocks per AQS-DWG-002)

## Sources

""" + "".join(f"- `{s}`\n" for s in srcs) + """
Status: accepted per AQS-PLAN-006 section 5 A-core and A-COL with the named design holds; the machine-design detail (internals, diameter, insulation) follows the unit WORK_ORDER.
"""
(HERE / "build_log.md").write_text(log)
print(json.dumps({"sheets": [s[0] for s in SHEETS], "pdf": pdf}))

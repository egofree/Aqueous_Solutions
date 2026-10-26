"""SHELL_BUILD drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

Run twice around _drawings.py:
    <cq python> draw_shell_build.py             # SVG source from the build
    python3 docs-authority/_drawings.py  # title block + register rows
    <cq python> draw_shell_build.py             # PDF pass (now from stamped SVGs)
"""
import json, pathlib, re
import cadquery as cq

HERE = pathlib.Path(__file__).parent
ns = __import__("runpy").run_path(HERE / "shell_build.py")
parts = ns["parts"]
inv = ns.get("inv", {{}})
REV = ns["P"]["graph_revision"]
DRAW = HERE / "drawings"; DRAW.mkdir(exist_ok=True)

def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u

shell = union_all([parts[k] for k in ("booth_frame", "dip_deck")])
hood = union_all([parts[k] for k in ("slurry_tank", "stucco_station", "manipulator")])
electrode = union_all([parts[k] for k in ("pattern_chute", "green_shell_out", "silica_inlets")])
aux = union_all([parts[k] for k in ("drain_well", "vent_stub")])
full = union_all(list(parts.values()) + list(inv.values()))

SHEETS = [
    ("ga_front", union_all([shell, hood, electrode, aux]), (0, 1, 0),
     ['Keys: 1500 x 800 booth, 1500 height; slurry tank 40 L at z 360..700; rainfall stucco station above the +X end',
      '6-dip manipulator mast over the drip deck; back-wall cladding on the -Y face',
      'N1 pattern chute -X z 160; N3/N4 silica inlets -X z 160; N2 green shell +X z 600; N5 drain z 50; N6 vent roof',
      'Slurry inventory drawn in place - process inventory, not a BOM part'],,
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", union_all([shell, hood, electrode, aux]), (1, 0, 0),
     ['General tolerance ISO 2768-m unless noted'],
     "General arrangement, side elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("nozzle_orient", full, (0, 0, -1),
     ['N1 -X face z 160: wax pattern in (from WAX_PATTERN N1; solids, bore not calculated)',
      'N3/N4 -X face z 160: foundry silica make-up and reclaimed stucco/flour (solids)',
      'N2 +X face z 600: green shell out to SHELL_BURNOUT N1 (solids)',
      'N5 bottom (400,400): DN15 drain, flush at z 0; N6 top (400,400) at the roof datum',
      'Heights/bore/rating per docs-authority/nozzles/SHELL_BUILD.csv; compass faces are the registered layout choice (params.json layout_note)'],,
     "Nozzle orientation, top view. Heights per the task-04 schedule."),
    ("sh01", shell, (0, 1, 0),
     ['Structure per the duty sheet; 6 mm fillet welds (ISO 2553 a6) at the plate seams',
      'General tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: primary structure."),
    ("hd01", hood, (0, 1, 0),
     ['Unit hardware per the duty sheet and the task-04 schedule',
      'General tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: process hardware."),
    ("el01", electrode, (0, 1, 0),
     ['Service connections per the task-04 schedule',
      'General tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: service connections."),
    ("aux01", aux, (0, 1, 0),
     ['N-drain sump flush at z 0; N-vent per the schedule datum',
      'General tolerance ISO 2768-m'],
     "Fabricated part sheet: drain + vent."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: +X face, y along depth, z up',
      'Graph revision AC is the model authority for this build; STEP (export/shell_build.step) is the solids of record',
      'Process inventory drawn in place - not a BOM part'],
     "Isometric orientation sheet."),
]

BAND = 100

def add_notes(svg_path, notes):
    s = svg_path.read_text()
    w = float(re.search(r'width="([\d.]+)"', s).group(1))
    h = float(re.search(r'height="([\d.]+)"', s).group(1))
    s = re.sub(r'height="[\d.]+"', f'height="{{h + BAND}}"', s, count=1)
    rows = [f"Graph revision {{REV}} - {{svg_path.stem}}: {{n}}" for n in notes]
    block = f'<g id="aqs-fab-notes" transform="translate(0,{{h}})" font-family="DejaVu Sans,sans-serif" font-size="10" fill="#000">'
    for i, n0 in enumerate(rows):
        block += f'<text x="6" y="{{24 + 13 * i}}">{{n0}}</text>'
    block += '</g>'
    svg_path.write_text(s.replace("</svg>", block + "</svg>"))

pdf = "stamped pass pending"
for sid, shape, pdir, notes, _title in SHEETS:
    svg = DRAW / f"{{sid}}.svg"
    if not svg.exists():
        pass
    elif "aqs-title-block" in svg.read_text():
        try:
            import cairosvg
            cairosvg.svg2pdf(url=str(svg), write_to=str(DRAW / f"{{sid}}.pdf"))
            pdf = "pdf+svg current"
        except Exception as e:
            pdf = f"pdf skipped ({{e.__class__.__name__}})"
        continue
    cq.exporters.export(shape.val(), str(svg), opt={{"projectionDir": pdir, "showAxes": False, "showHidden": True}})
    add_notes(svg, notes)
print(json.dumps({{"sheets": [s[0] for s in SHEETS], "pdf": pdf}}))

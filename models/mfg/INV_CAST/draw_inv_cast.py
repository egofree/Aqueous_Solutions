"""INV_CAST drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

Run twice around _drawings.py:
    <cq python> draw_inv_cast.py             # SVG source from the build
    python3 docs-authority/_drawings.py  # title block + register rows
    <cq python> draw_inv_cast.py             # PDF pass (now from stamped SVGs)
"""
import json, pathlib, re
import cadquery as cq

HERE = pathlib.Path(__file__).parent
ns = __import__("runpy").run_path(HERE / "inv_cast.py")
parts = ns["parts"]
inv = ns.get("inv", {})
REV = ns["P"]["graph_revision"]
DRAW = HERE / "drawings"; DRAW.mkdir(exist_ok=True)

def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u

shell = union_all([parts[k] for k in ("frame", "mould_clamp", "pour_station", "cast_out_bed")])
hood = union_all([parts[k] for k in ("melt_stubs", "vent_stub")])
electrode = union_all([parts[k] for k in ("cast_out_stop",)])
aux = union_all([parts[k] for k in ("shell_inlet", "drain_well")])
full = union_all(list(parts.values()) + list(inv.values()))

SHEETS = [
    ("ga_front", union_all([shell, hood, electrode, aux]), (0, 1, 0),
     ['Keys: 1500 x 800 frame, 1500 height with the mould-change gantry z 1460..1500; shell-mould clamp and tilt-pour station on the deck',
      'N1 fired shell in -X z 160; N2/N3 melt DN15 stubs -Y z 160 (from IND_MELT N14); N4 cast+shell +X z 600 on the roller bed',
      'N5 drain z 50; N6 vent z 800; campaign of 8 moulds (design row)',
      'Shell-mould inventory drawn in place - process inventory, not a BOM part'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", union_all([shell, hood, electrode, aux]), (1, 0, 0),
     ['General tolerance ISO 2768-m unless noted'],
     "General arrangement, side elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("nozzle_orient", full, (0, 0, -1),
     ['N1 -X face z 160: fired shell in (solids, bore not calculated)',
      'N2/N3 -X face z 160: DN15 melt for investment pour (from IND_MELT N14)',
      'N4 +X face z 600: cast + shell out to SHELL_BREAK N1 (solids)',
      'N5 bottom: DN15 drain, flush at z 0; N6 top: vent at the frame datum',
      'Heights/bore/rating per docs-authority/nozzles/INV_CAST.csv; compass faces are the registered layout choice (params.json layout_note)'],
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
      'Graph revision AC is the model authority for this build; STEP (export/inv_cast.step) is the solids of record',
      'Process inventory drawn in place - not a BOM part'],
     "Isometric orientation sheet."),
]

BAND = 100

def add_notes(svg_path, notes):
    s = svg_path.read_text()
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
for sid, shape, pdir, notes, _title in SHEETS:
    svg = DRAW / f"{sid}.svg"
    if not svg.exists():
        pass
    elif "aqs-title-block" in svg.read_text():
        try:
            import cairosvg
            cairosvg.svg2pdf(url=str(svg), write_to=str(DRAW / f"{sid}.pdf"))
            pdf = "pdf+svg current"
        except Exception as e:
            pdf = f"pdf skipped ({e.__class__.__name__})"
        continue
    cq.exporters.export(shape.val(), str(svg), opt={"projectionDir": pdir, "showAxes": False, "showHidden": True})
    add_notes(svg, notes)
print(json.dumps({"sheets": [s[0] for s in SHEETS], "pdf": pdf}))

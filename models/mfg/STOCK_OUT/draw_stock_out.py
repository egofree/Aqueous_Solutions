"""STOCK_OUT drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
(content-hash revision per ISO_7200/ASME_Y14_35) and the DRAWING_REGISTER.md rows
are applied by docs-authority/_drawings.py (AQS-DWG-002), which stamps every
model/mfg/*/drawings/*.svg. Geometry and notes:

  ga_front     general arrangement, front elevation (-Y): three-tier rack
  ga_side      general arrangement, side elevation (-X)
  nozzle_orient  nozzle orientation, top view (faces per the task-04 schedule)
  sh01         casing + lining + head plate (weld + tolerance notes)
  hd01         top group: vent stub, upright tops
  el01         tiers: decks, back guard, issue-face stops
  aux01        service group: issue sill, drain, vent
  iso01        isometric orientation sheet

Run twice around _drawings.py:
    <cq python> draw_stock_out.py         # SVG source from the build
    python3 docs-authority/_drawings.py   # title block + register rows
    <cq python> draw_stock_out.py         # PDF pass (now from stamped SVGs)
"""
import json, pathlib, re
import cadquery as cq

HERE = pathlib.Path(__file__).parent
ns = __import__("runpy").run_path(HERE / "stock_out.py")
parts, inv, P = ns["parts"], ns["inv"], ns["P"]
REV = P["graph_revision"]
DRAW = HERE / "drawings"; DRAW.mkdir(exist_ok=True)

def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u

shell = union_all([parts[k] for k in ("uprights", "tier_decks", "back_guard")])
hood = union_all([parts[k] for k in ("vent_stub",)])
electrode = union_all([parts[k] for k in ("edge_stops",)])
aux = union_all([parts[k] for k in ("issue_sill", "drain_well")])
full = union_all(list(parts.values()) + list(inv.values()))

SHEETS = [
    ("ga_front", union_all([shell, hood, electrode, aux]), (0, 1, 0),
     ['Keys: 1200 x 800 rack, 1500 overall height; three tier decks at z 160 / 600 / 1000',
      'The seven stock-inlet rows land on the tier decks (task-04 schedule N1..N7)',
      'N8 formed product issues at the +X face at z 600; N9 floor drain z 50; N10 vent top z 1500 datum',
      'Stock inventory drawn as solids - process inventory, not a BOM part'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", union_all([shell, hood, electrode, aux]), (1, 0, 0),
     ['Keys: six 60 x 60 uprights; back guard plate on the -Y... +Y face; issue-face stops at +X',
      'Tier loading 1.0 d hold (AQS-DUTY-072); general tolerance ISO 2768-m unless noted'],
     "General arrangement, side elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("nozzle_orient", full, (0, 0, -1),
     ['N1..N7 stock inlets: the rows land on the tier decks at z 160 (registered layout choice)',
      'N8 +X face z 600: formed metal product to the store (solids, bore not calculated)',
      'N9 bottom (400,400): DN15 nominal floor drain, flush at z 0',
      'N10 top (600,400): DN15 vent at the z 1500 datum',
      'Heights/bore/rating per docs-authority/nozzles/STOCK_OUT.csv'],
     "Nozzle orientation, top view. Heights per the task-04 schedule."),
    ("sh01", shell, (0, 1, 0),
     ['Uprights 60 x 60 with tier decks 1200 x 800 x 30; back guard plate 1200 x 20',
      '6 mm fillet welds (ISO 2553 a6) at the upright/deck seams; general tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: uprights, decks, back guard. Welds per ISO 2553."),
    ("hd01", hood, (0, 1, 0),
     ['N10 vent stub DN15 at (600,400) to the z 1500 datum',
      'General tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: vent stub."),
    ("el01", electrode, (0, 1, 0),
     ['Issue-face edge stops at +X on each tier, 20 x 720 x 120',
      'General tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: issue-face edge stops."),
    ("aux01", aux, (0, 1, 0),
     ['N8 issue sill +X z 600 (formed metal product to the store; bore not calculated)',
      'N9 drain sump OD 60, DN15 bore, flush at z 0',
      'General tolerance ISO 2768-m'],
     "Fabricated part sheet: issue sill + drain."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: +X face, y along depth, z up; three-tier rack with staged stock',
      'Graph revision AC is the model authority for this build; STEP (export/stock_out.step) is the solids of record',
      'Stock inventory shown in place - not a BOM part'],
     "Isometric orientation sheet."),
]

BAND = 100   # notes band appended under the drawing; _drawings.py stamps the title block bottom-right

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
        pass   # fresh write below
    elif "aqs-title-block" in svg.read_text():   # already stamped by _drawings.py: geometry frozen, PDF pass only
        try:
            import cairosvg
            cairosvg.svg2pdf(url=str(svg), write_to=str(DRAW / f"{sid}.pdf"))
            pdf = "pdf+svg current"
        except Exception as e:
            pdf = f"pdf skipped ({e.__class__.__name__}: {e})"
        continue
    cq.exporters.export(shape.val(), str(svg), opt={"projectionDir": pdir, "showAxes": False, "showHidden": True})
    add_notes(svg, notes)          # notes only; the title block + register rows happen in _drawings.py
print(json.dumps({"sheets": [s[0] for s in SHEETS], "pdf": pdf}))

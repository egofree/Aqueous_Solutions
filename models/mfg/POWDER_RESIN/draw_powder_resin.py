"""POWDER_RESIN drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
(content-hash revision per ISO_7200/ASME_Y14_35) and the DRAWING_REGISTER.md rows
are applied by docs-authority/_drawings.py (AQS-DWG-002), which stamps every
model/mfg/*/drawings/*.svg. Geometry and notes:

  ga_front     general arrangement, front elevation (-Y): mill, cyclone, collector, frame
  ga_side      general arrangement, side elevation (-X)
  nozzle_orient  nozzle orientation, top view (faces per the task-04 schedule)
  sh01         casing + lining + head plate (weld + tolerance notes)
  hd01         top group: cyclone, vent riser to the z 1200 datum
  el01         powder path: pin mill, ducts, collector
  aux01        service group: inlet chute, powder outlet, drain
  iso01        isometric orientation sheet

Run twice around _drawings.py:
    <cq python> draw_powder_resin.py            # SVG source from the build
    python3 docs-authority/_drawings.py   # title block + register rows
    <cq python> draw_powder_resin.py            # PDF pass (now from stamped SVGs)
"""
import json, pathlib, re
import cadquery as cq

HERE = pathlib.Path(__file__).parent
ns = __import__("runpy").run_path(HERE / "powder_resin.py")
parts, inv, P = ns["parts"], ns["inv"], ns["P"]
REV = P["graph_revision"]
DRAW = HERE / "drawings"; DRAW.mkdir(exist_ok=True)

def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u

shell = union_all([parts[k] for k in ("frame", "mill", "mill_motor", "cyclone", "collector")])
hood = union_all([parts[k] for k in ("vent_stub", "duct_mill_cyc", "duct_cyc_col")])
electrode = union_all([parts[k] for k in ("powder_inlet", "powder_out")])
aux = union_all([parts[k] for k in ("drain_well",)])
full = union_all(list(parts.values()) + list(inv.values()))

SHEETS = [
    ("ga_front", union_all([shell, hood, electrode, aux]), (0, 1, 0),
     ['Keys: 1500 x 800 frame, 1500 height with the top rail; pin mill OD 220 x 240 at -X',
      'Cyclone classifier OD 220 x 520 + cone; PE-lined collector 340 x 300 x 460 at +X',
      'N1 powder inlet chute -X z 160 (from POLY_F N4); N2 powder stock +X at the collector',
      'N3 nominal drain (400,400) z 50; N4 vent on the cyclone to the z 1200 datum',
      'Powder inventory drawn in the collector - process inventory, not a BOM part'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", union_all([shell, hood, electrode, aux]), (1, 0, 0),
     ['Keys: 316L mill; PE-lined collector per duty section 3',
      'General tolerance ISO 2768-m unless noted'],
     "General arrangement, side elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("nozzle_orient", full, (0, 0, -1),
     ['N1 -X face z 160: fluoropolymer powder in from POLY_F N4 (solids, bore not calculated)',
      'N2 +X face at the collector: powder stock out to STOCK_OUT N6 (solids)',
      'N3 bottom (400,400): DN15 nominal drain, flush at z 0',
      'N4 top on the cyclone: DN15 vent to the z 1200 datum',
      'Heights/bore/rating per docs-authority/nozzles/POWDER_RESIN.csv; compass faces are the registered layout choice (params.json layout_note)'],
     "Nozzle orientation, top view. Heights per the task-04 schedule."),
    ("sh01", shell, (0, 1, 0),
     ['Frame: base 1500 x 800 x 40, four 60 x 60 posts to the z 1480 datum, top rail z 1460..1500',
      '6 mm fillet welds (ISO 2553 a6) at the post/base seams; general tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: frame + mill + cyclone + collector. Welds per ISO 2553."),
    ("hd01", hood, (0, 1, 0),
     ['Ducts OD 80: mill -> cyclone, cyclone -> collector; N4 vent DN15 on the cyclone to z 1200',
      'General tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: ducts + vent."),
    ("el01", electrode, (0, 1, 0),
     ['N1 powder inlet chute -X z 160 (from POLY_F N4)',
      'N2 powder stock out at the collector (to STOCK_OUT N6)',
      'General tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: inlet + outlet."),
    ("aux01", aux, (0, 1, 0),
     ['N3 nominal drain flush at z 0',
      'General tolerance ISO 2768-m'],
     "Fabricated part sheet: drain."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: +X face, y along depth, z up; mill, cyclone and collector on the frame',
      'Graph revision AC is the model authority for this build; STEP (export/powder_resin.step) is the solids of record',
      'Powder inventory shown in the collector - not a BOM part'],
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

"""FILM_CAST drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
(content-hash revision per ISO_7200/ASME_Y14_35) and the DRAWING_REGISTER.md rows
are applied by docs-authority/_drawings.py (AQS-DWG-002), which stamps every
model/mfg/*/drawings/*.svg. Geometry and notes:

  ga_front     general arrangement, front elevation (-Y): extruder, die, chill roll, winder
  ga_side      general arrangement, side elevation (-X)
  nozzle_orient  nozzle orientation, top view (faces per the task-04 schedule)
  sh01         casing + lining + head plate (weld + tolerance notes)
  hd01         top group: hoist beam, vent riser
  el01         web path: barrel, die, chill roll, pressure roll, draw rolls, winder
  aux01        service group: resin inlet, film stop, drain
  iso01        isometric orientation sheet

Run twice around _drawings.py:
    <cq python> draw_film_cast.py         # SVG source from the build
    python3 docs-authority/_drawings.py   # title block + register rows
    <cq python> draw_film_cast.py         # PDF pass (now from stamped SVGs)
"""
import json, pathlib, re
import cadquery as cq

HERE = pathlib.Path(__file__).parent
ns = __import__("runpy").run_path(HERE / "film_cast.py")
parts, inv, P = ns["parts"], ns["inv"], ns["P"]
REV = P["graph_revision"]
DRAW = HERE / "drawings"; DRAW.mkdir(exist_ok=True)

def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u

shell = union_all([parts[k] for k in ("frame",)])
hood = union_all([parts[k] for k in ("vent_stub",)])
electrode = union_all([parts[k] for k in ("extruder_barrel", "extruder_hopper", "extruder_drive", "die", "chill_roll", "pressure_roll", "draw_rolls", "winder")])
aux = union_all([parts[k] for k in ("resin_inlet", "film_stop", "drain_well")])
full = union_all(list(parts.values()) + list(inv.values()))

SHEETS = [
    ("ga_front", union_all([shell, hood, electrode, aux]), (0, 1, 0),
     ['Keys: 1500 x 800 line frame, 1500 height with the roll-change gantry z 1460..1500',
      'Extruder D25 x 480 with hopper and drive at -X; Hastelloy die 200 mm at z 910..1030',
      'Chill roll OD 150 and pressure roll at z 915..1065; draw rolls x 980/1100/1220; winder +X',
      'N2 PVDF resin DN15 inlet -X z 160; N1 film stock +X z 600..760; N3 drain z 50; N4 vent to z 1200',
      'Film web inventory drawn as a solid - process inventory, not a BOM part'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", union_all([shell, hood, electrode, aux]), (1, 0, 0),
     ['Keys: melt 220 C class (316L barrel, Hastelloy die per duty section 3)',
      'General tolerance ISO 2768-m unless noted'],
     "General arrangement, side elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("nozzle_orient", full, (0, 0, -1),
     ['N2 -X face z 160: DN15 PVDF resin inlet from POLY_F N5',
      'N1 +X face z 600: film stock out at the winder (solids, bore not calculated)',
      'N3 bottom (400,400): DN15 drain, flush at z 0',
      'N4 top (300,80): DN15 vent to the z 1200 datum',
      'Heights/bore/rating per docs-authority/nozzles/FILM_CAST.csv; compass faces are the registered layout choice (params.json layout_note)'],
     "Nozzle orientation, top view. Heights per the task-04 schedule."),
    ("sh01", shell, (0, 1, 0),
     ['Frame: base 1500 x 800 x 40, four 60 x 60 posts, line bed z 830..860',
      'Gantry legs 60 wide and the hoist beam z 1460..1500 for the roll change-out',
      '6 mm fillet welds (ISO 2553 a6) at the post/bed seams; general tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: frame. Welds per ISO 2553."),
    ("hd01", hood, (0, 1, 0),
     ['N4 vent DN15 riser at (300,80) to the z 1200 datum',
      'General tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: vent."),
    ("el01", electrode, (0, 1, 0),
     ['Extruder D25 x 480, 316L barrel; Hastelloy die 200 mm at z 910..1030',
      'Chill roll OD 150 x 300 and pressure roll OD 90; draw rolls OD 80 x 3; winder OD 180 x 260',
      'General tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: web path (barrel, die, rolls, winder)."),
    ("aux01", aux, (0, 1, 0),
     ['N2 PVDF resin DN15 inlet -X z 160 (from POLY_F N5)',
      'N1 film stock stop +X (solids, bore not calculated)',
      'N3 drain sump OD 60, DN15 bore, flush at z 0; general tolerance ISO 2768-m'],
     "Fabricated part sheet: service group (inlet, stop, drain)."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: +X face, y along depth, z up; extruder, die, chill roll and winder on the frame',
      'Graph revision AC is the model authority for this build; STEP (export/film_cast.step) is the solids of record',
      'Film web inventory shown in place - not a BOM part'],
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

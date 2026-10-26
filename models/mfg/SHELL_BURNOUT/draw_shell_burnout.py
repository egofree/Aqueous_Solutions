"""SHELL_BURNOUT drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
(content-hash revision per ISO_7200/ASME_Y14_35) and the DRAWING_REGISTER.md rows
are applied by docs-authority/_drawings.py (AQS-DWG-002), which stamps every
model/mfg/*/drawings/*.svg. Geometry and notes:

  ga_front     general arrangement, front elevation (-Y): furnace, door, condensate pan
  ga_side      general arrangement, side elevation (-X)
  nozzle_orient  nozzle orientation, top view (faces per the task-04 schedule)
  sh01         casing + lining + head plate (weld + tolerance notes)
  hd01         top group: N7 vent, N3/N4 wax stubs, N5 off-gas collector
  el01         furnace interior: hot face, hearth, shell racks
  aux01        service group: N1 inlet, N2 outlet, door, drain
  iso01        isometric orientation sheet

Run twice around _drawings.py:
    <cq python> draw_shell_burnout.py     # SVG source from the build
    python3 docs-authority/_drawings.py   # title block + register rows
    <cq python> draw_shell_burnout.py     # PDF pass (now from stamped SVGs)
"""
import json, pathlib, re
import cadquery as cq

HERE = pathlib.Path(__file__).parent
ns = __import__("runpy").run_path(HERE / "shell_burnout.py")
parts, inv, P = ns["parts"], ns["inv"], ns["P"]
REV = P["graph_revision"]
DRAW = HERE / "drawings"; DRAW.mkdir(exist_ok=True)

def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u

shell = union_all([parts[k] for k in ("casing", "hot_face", "hearth_plate", "door")])
hood = union_all([parts[k] for k in ("condensate_stub", "wax_stub", "offgas_stub", "vent_stub", "condenser_pan", "offgas_collector")])
electrode = union_all([parts[k] for k in ("shell_inlet", "fired_out")])
aux = union_all([parts[k] for k in ("drain_well",)])
full = union_all(list(parts.values()) + list(inv.values()))

SHEETS = [
    ("ga_front", union_all([shell, hood, electrode, aux]), (0, 1, 0),
     ['Keys: 1000 x 1000 casing, 1500 overall height; front door -X; t hot-face lining',
      'N1 green-shell inlet -X z 160; N2 fired-shell out +X z 600 (to INV_CAST N1)',
      'N3/N4 condensate + unrecovered-wax DN15 stubs +Y z 600; N5 off-gas -Y z 600',
      'N6 drain bottom (400,400) flush at z 0; N7 vent top (400,400) z 800',
      'Shell-rack inventory drawn in place - process inventory, not a BOM part'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", union_all([shell, hood, electrode, aux]), (1, 0, 0),
     ['Keys: dewax + fire furnace at 900 C (0.25 kW dewax heaters per the design row)',
      'Condensate pan under the shell racks routes reclaim to WAX_PATTERN N2',
      'General tolerance ISO 2768-m unless noted'],
     "General arrangement, side elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("nozzle_orient", full, (0, 0, -1),
     ['N1 -X face z 160: green shell in from SHELL_BUILD N2 (solids, bore not calculated)',
      'N2 +X face z 600: fired shell out to INV_CAST N1 (solids)',
      'N3 +Y face, x 600, z 600: DN15 wax condensate reclaim to WAX_PATTERN N2',
      'N4 +Y face, x 700, z 600: DN15 unrecovered wax to the oil line',
      'N5 -Y face, x 700, z 600: DN15 dewax/burnout off-gas (burned wax + steam)',
      'N6 bottom (400,400): DN15 drain, flush at z 0; N7 top (400,400): DN15 vent at z 800',
      'Heights/bore/rating per docs-authority/nozzles/SHELL_BURNOUT.csv; compass faces are the registered layout choice (params.json layout_note)'],
     "Nozzle orientation, top view. Heights per the task-04 schedule."),
    ("sh01", shell, (0, 1, 0),
     ['Casing CS t4 with the front door slab (6 x M10 hinges, fasteners.csv item 1); hot-face lining with the door throat recess',
      '6 mm fillet welds (ISO 2553 a6) at the wall/roof seams; general tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: casing + hot face + hearth + door. Welds per ISO 2553."),
    ("hd01", hood, (0, 1, 0),
     ['N3/N4 DN15 stubs +Y z 600; N5 off-gas collector hood -Y z 480..640',
      'N7 vent DN15 at (400,400) to the z 800 datum',
      'Gasket faces per AQS-PIP-003 practice (AQS-STD-002 section 14); general tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: gas group (pan, collector, stubs, vent)."),
    ("el01", electrode, (0, 1, 0),
     ['N1 green-shell inlet -X z 160, full height to the base',
      'N2 fired-shell outlet +X z 600 (to INV_CAST N1)',
      'General tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: shell pass-throughs."),
    ("aux01", aux, (0, 1, 0),
     ['N6 drain sump OD 60, DN15 bore, flush at z 0',
      'Hearth plate z 160..220; general tolerance ISO 2768-m'],
     "Fabricated part sheet: drain + hearth."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: +X face, y along depth, z up; furnace with the door and condensate pan',
      'Graph revision AC is the model authority for this build; STEP (export/shell_burnout.step) is the solids of record',
      'Shell-rack inventory shown in place - not a BOM part'],
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

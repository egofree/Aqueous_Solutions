"""CR_CELL drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
(content-hash revision per ISO_7200/ASME_Y14_35) and the DRAWING_REGISTER.md rows
are applied by docs-authority/_drawings.py (AQS-DWG-002), which stamps every
model/mfg/*/drawings/*.svg. Geometry and notes:

  ga_front     general arrangement, front elevation (-Y)
  ga_side      general arrangement, side elevation (-X)
  nozzle_orient  nozzle orientation, top view (faces per the task-04 schedule)
  sh01         casing + lining + head plate (weld + tolerance notes)
  hd01         hood group: hot plate, plate, rim, DN50 riser, dip leg, N1/N3/N7 stubs, vent
  el01         electrode bank: 3 anodes + clamps, 2 cathodes, bus rails/straps
  aux01        service group: N1 tap, N2/N3 chutes, N4 CO stub, N5 drain
  iso01        isometric orientation sheet

Run twice around _drawings.py:
    <cq python> draw_cr_cell.py           # SVG source from the build
    python3 docs-authority/_drawings.py   # title block + register rows
    <cq python> draw_cr_cell.py           # PDF pass (now from stamped SVGs)
"""
import json, pathlib, re
import cadquery as cq

HERE = pathlib.Path(__file__).parent
ns = __import__("runpy").run_path(HERE / "cr_cell.py")
parts, inv, P = ns["parts"], ns["inv"], ns["P"]
REV = P["graph_revision"]
DRAW = HERE / "drawings"; DRAW.mkdir(exist_ok=True)

def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u

shell = union_all([parts[k] for k in ("casing", "fibre_lining", "ram_lining", "head_plate")])
hood = union_all([parts[k] for k in ("hood_hot_plate", "hood", "offtake_riser", "riser_flange", "dip_leg", "vent_stub", "co_stub")])
electrode = union_all([parts[k] for k in ("anodes", "anode_clamps", "cathodes", "bus_rails", "bus_straps", "ceramic_pads")])
aux = union_all([parts[k] for k in ("cr_tap_group", "feed_chutes", "drain_well")])
full = union_all(list(parts.values()) + list(inv.values()))
BATH = P["design"]["bath_top_mm"]

SHEETS = [
    ("ga_front", union_all([shell, hood, electrode, aux]), (0, 1, 0),
     ['Keys: 800 overall width (shell); 1600 overall height, roof datum z 1594..1600',
      f'Bath top z {BATH:.0f} (hood hot plate at {BATH-10:.0f}..{BATH:.0f}); head plate deck 1154..1160; bus rails 1196..1201',
      'N1 Cr-metal tap lip +X z 600; N2/N3 chutes -X z 160; N4 CO stub +Y z 600; N5 drain bottom z 50; N6 vent on the riser at z 800',
      'Connection hardware protrudes no more than 50 mm outside the shell faces (task-04 schedule; reported in check.json, nothing resized)',
      'Bath inventory (salt + metal layer) drawn as solids - process inventory, not a BOM part'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", union_all([shell, hood, electrode, aux]), (1, 0, 0),
     ['Keys: 800 overall depth (-Y face); casing t6 + fibre lining t24 + graphite ram t40; wetted cavity 660 square',
      '1600 overall height; riser DN50 OD 60.3 t 2.0 at (+150,+150) from the shell centre, top 1594',
      'Return dip leg DN15 inside the riser annulus, bottom z 250; N3 Cl2 stub +Y z 600 - dry 700 C headspace above the hood',
      'N2 lance z 160 sub-surface; general tolerance ISO 2768-m unless noted'],
     "General arrangement, side elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("nozzle_orient", full, (0, 0, -1),
     ['N1 +X face z 600: Ca-metal tap well, crest and discharge lip (open launder, solids - bore not calculated)',
      'N2 -X face, y 400, z 160: DN15 Class 150, CaCl2 brine concentrate inlet, lance into the bath',
      'N3 +Y face, x 598, z 600: DN15 Class 150, chlorine byproduct export (water-treatment class)',
      'N4 bottom face, (256,160): DN15 drain well, sump face z 50, flush at z 0',
      'N5 top, DN15 on the DN50 riser at z 800',
      'Heights/bore/rating per docs-authority/nozzles/CA_POT.csv; compass faces are the registered layout choice (params.json layout_note)'],
     "Nozzle orientation, top view. Heights per the task-04 schedule."),
    ("sh01", union_all([shell, parts["hood_hot_plate"]]), (0, 1, 0),
     ['Casing t6 CS: 6 mm fillet welds (ISO 2553 a6) along wall/wall and wall/roof seams; head plate 1154..1160 bolted to casing frames (M10, fasteners.csv item 1)',
      'Lining package: casing t6 + ceramic fibre t24 + graphite ram t40; the ram carries the N2 lance and N4 drain passes as drawn',
      'General tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: casing + lining + head plate. Welds per ISO 2553; general tolerance ISO 2768-m."),
    ("hd01", hood, (0, 1, 0),
     ['Hood plate CS t6 + rim lip 60 wide x 46; graphite hot plate t10 (expendable wetted face)',
      'DN50 riser OD 60.3 t 2.0: full-penetration butt welds to the plate (ISO 2553); N6 DN15 vent stub on the riser at z 800; N4 DN15 CO stub at +Y z 600',
      'Return dip leg DN15 inside the riser annulus, bottom z 250',
      'Gasket faces per AQS-PIP-003 class practice (AQS-STD-002 section 14); general tolerance ISO 2768-m'],
     "Fabricated part sheet: hood group (hot plate, plate + rim, riser, dip leg, vent)."),
    ("el01", electrode, (0, 1, 0),
     ['3 anodes D50 x 1064 at x 165, 400, 635 (y 400); immersion 250 mm, tips z 100; clamp bars 90 x 40 x 24 (6 x M10 studs, fasteners.csv item 1)',
      '2 cathode plates 110 x 12 x 300 on the -Y ram face, z 90..390 (duty section 2 graph design row)',
      'Cu rails 2 x 5 x 5 (25 mm2 class) on ceramic pads, z 1196..1201; straps 6 x 20 Cu, 3 mm fillet at the clamp welds (ISO 2553)',
      'Bus hardware frame-isolated per AQS-STD-002 section 11; general tolerance ISO 2768-m'],
     "Fabricated part sheet: electrode bank + busbar ladder."),
    ("aux01", aux, (0, 1, 0),
     ['N1 Cr-metal tap: carbon well DN80-class, crest 605..615, discharge lip +X z 600 (WO step 6 tap procedure)',
      'N2/N3 feed chutes: box 35 x 160 x 90 each (Cr2O3 chromite concentrate, carbon reductant)',
      'N5 drain: carbon sump OD 60, DN15 bore through the base stack, flush at z 0 (frozen-salt drain pig)',
      'General tolerance ISO 2768-m'],
     "Fabricated part sheet: service group (tap, chutes, drain)."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: +X face, y along depth, z up; hood + head plate + bus in place over the 800 x 800 x 1600 lined cell',
      'Graph revision AC is the model authority for this build; STEP (export/ca_pot.step) is the solids of record',
      'Bath inventory (salt + metal layer) shown in place - not a BOM part'],
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

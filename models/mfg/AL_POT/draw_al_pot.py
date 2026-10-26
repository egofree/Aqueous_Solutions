"""AL_POT drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
(content-hash revision per ISO_7200/ASME_Y14_35) and the DRAWING_REGISTER.md rows
are applied by docs-authority/_drawings.py (AQS-DWG-002), which stamps every
model/mfg/*/drawings/*.svg. Geometry and notes:

  ga_front     general arrangement, front elevation (-Y)
  ga_side      general arrangement, side elevation (-X)
  nozzle_orient  nozzle orientation, top view (faces per the task-04 schedule)
  sh01         casing + lining + head plate (weld + tolerance notes)
  hd01         hood group: hot plate, plate, rim, DN150 riser, dip leg, vent
  el01         electrode bank: 5 anodes + clamps, 5 cathodes, bus rails/straps
  aux01        service group: N1 siphon, N3 chute/lance, N5 drain, sleeves, stubs
  iso01        isometric orientation sheet

Run twice around _drawings.py:
    <cq python> draw_al_pot.py            # SVG source from the build
    python3 docs-authority/_drawings.py   # title block + register rows
    <cq python> draw_al_pot.py            # PDF pass (now from stamped SVGs)
"""
import json, pathlib, re
import cadquery as cq

HERE = pathlib.Path(__file__).parent
ns = __import__("runpy").run_path(HERE / "al_pot.py")
parts, inv, P = ns["parts"], ns["inv"], ns["P"]
REV = P["graph_revision"]
DRAW = HERE / "drawings"; DRAW.mkdir(exist_ok=True)

def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u

shell = union_all([parts[k] for k in ("casing", "fibre_lining", "ram_lining", "head_plate")])
hood = union_all([parts[k] for k in ("hood_hot_plate", "hood", "offtake_riser", "riser_flange", "dip_leg", "vent_stub")])
electrode = union_all([parts[k] for k in ("anodes", "anode_clamps", "cathodes", "bus_rails", "bus_straps", "ceramic_pads")])
aux = union_all([parts[k] for k in ("metal_siphon", "feed_chute_group", "drain_well", "ceramic_sleeves", "DN15_stubs")])
full = union_all(list(parts.values()) + list(inv.values()))

SHEETS = [
    ("ga_front", union_all([shell, hood, electrode, aux]), (0, 1, 0),
     ['Keys: 800 overall width (shell); 1600 overall height, roof datum z0 = 1594..1600',
      'Melt level z 500 (hood hot plate at 490..500); head plate deck 1154..1160; bus rails 1196..1227',
      'N1 siphon lip +X z 600; N2/N4 DN15 at z 600; N3 chute z 160; N6 vent on the riser at z 800',
      'Connection hardware protrudes no more than 50 mm outside the shell faces (task-04 schedule; reported in check.json, nothing resized)',
      'Melt inventory (salt + metal layer) drawn as solids - process inventory, not a BOM part'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", union_all([shell, hood, electrode, aux]), (1, 0, 0),
     ['Keys: 800 overall depth (-Y face); casing t6 + fibre lining t24 + graphite ram t40; wetted cavity 660 square',
      '1600 overall height; riser DN150 OD 168.3 t 4.0 at (+90,+90) from hood centre, top 1594',
      'Dip leg DN50 OD 60.3 Hastelloy C-276 inside the riser annulus, bottom z 250 (250 mm submerged)',
      'N2/N4 stub faces z 600 above the hood plate - dry 700 C headspace (M7); N3 lance z 160 sub-surface',
      'General tolerance ISO 2768-m unless noted'],
     "General arrangement, side elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("nozzle_orient", full, (0, 0, -1),
     ['N1 +X face z 600: metal siphon discharge lip (open launder, solids - bore not calculated)',
      'N2 -Y face, x 202, z 600: DN15 Class 150, Cl2 return, alumina sleeve through the ram',
      'N3 -X face, y 400, z 160: solids inlet, chute + rotary seal + DN100 lance into the melt',
      'N4 +Y face, x 598, z 600: DN15 Class 150, chlorine export to the CRU (A-M-280 ruling)',
      'N5 bottom face, (256,160): DN15 drain well, sump face z 50, flush at z 0',
      'N6 top, DN150 riser z 800 (+Y side): DN15 Class 150 vent',
      'Heights/bore/rating per docs-authority/nozzles/AL_POT.csv; compass faces are the registered layout choice (params.json layout_note)'],
     "Nozzle orientation, top view. Heights per the task-04 schedule."),
    ("sh01", union_all([shell, parts["hood_hot_plate"]]), (0, 1, 0),
     ['Casing t6 CS: 6 mm fillet welds (ISO 2553 a6) along wall/wall and wall/roof seams; head plate 1154..1160 bolted to casing frames (M12, fasteners.csv item 1)',
      'Lining package: casing t6 + ceramic fibre t24 + graphite ram t40 - the duty section 3 10 mm wetted design allowance is inside the ram',
      'Drain sump recess and nozzle passes cut into the ram as drawn (N3/N5/crest channel)',
      'General tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: casing + lining + head plate. Welds per ISO 2553; general tolerance ISO 2768-m."),
    ("hd01", hood, (0, 1, 0),
     ['Hood plate CS t6 + rim lip 60 wide x 46; graphite hot plate t10 (expendable wetted face = the 10 mm allowance)',
      'DN150 riser OD 168.3 t 4.0 (sch 10): full-penetration butt welds to the plate (ISO 2553); DN15 vent stub at z 800',
      'Dip leg DN50 OD 60.3 Hastelloy C-276, annulus liquid seal, bottom z 250',
      'Gasket faces per AQS-PIP-003 class practice (AQS-STD-002 section 14); general tolerance ISO 2768-m'],
     "Fabricated part sheet: hood group (hot plate, plate + rim, riser, dip leg, vent)."),
    ("el01", electrode, (0, 1, 0),
     ['5 anodes D75 x 1064 at x 170..698 step 132 (y 400); immersion 400 mm, tips z 100; clamp bars 110 x 40 x 24 (10 x M12 studs, fasteners.csv item 1)',
      '5 cathode plates 110 x 12 x 440 at x 136..664 step 132 on the -Y ram face, z 90..530 (duty section 2 graph design row)',
      'Cu rails 2 x 32 x 31 (975 mm2 class) on ceramic pads, z 1196..1227; straps 8 x 20 Cu, 3 mm fillet at the clamp welds (ISO 2553)',
      'Bus hardware frame-isolated per AQS-STD-002 section 11; general tolerance ISO 2768-m'],
     "Fabricated part sheet: electrode bank + busbar ladder."),
    ("aux01", aux, (0, 1, 0),
     ['N1 siphon: carbon well DN80 OD 88.9, crest 655..665, discharge lip +X z 600 (heat traced; WO step 6 tap procedure)',
      'N3 chute: box 35 x 160 x 140 + hopper + rotary-seal flange; DN100 lance OD 114.3 t 4.0 into the melt at z 160',
      'N5 drain: carbon sump OD 60, DN15 bore through the base stack, flush at z 0 (frozen-salt drain pig)',
      'N2/N4 alumina sleeves OD 32 for the ram passes; general tolerance ISO 2768-m'],
     "Fabricated part sheet: service group (siphon, chute, drain, sleeves)."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: +X face, y along depth, z up; hood + head plate + bus in place over the 800 x 800 x 1000 lined pot zone',
      'Graph revision AC is the model authority for this build; STEP (export/al_pot.step) is the solids of record',
      'Process inventory (melt salt + metal layer) shown in place - not a BOM part'],
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

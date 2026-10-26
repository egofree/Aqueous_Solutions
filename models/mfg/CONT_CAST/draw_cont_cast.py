"""CONT_CAST drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
(content-hash revision per ISO_7200/ASME_Y14_35) and the DRAWING_REGISTER.md rows
are applied by docs-authority/_drawings.py (AQS-DWG-002), which stamps every
model/mfg/*/drawings/*.svg. Geometry and notes:

  ga_front     general arrangement, front elevation (-Y): mould, run-out, gantry
  ga_side      general arrangement, side elevation (-X)
  nozzle_orient  nozzle orientation, top view (faces per the task-04 schedule)
  sh01         casing + lining + head plate (weld + tolerance notes)
  hd01         top group: hoist beam, vent riser, mould water manifold
  el01         strand path: mould cavities, withdrawal rolls, run-out rollers
  aux01        service group: melt inlet, stock stubs, billet bed, drain
  iso01        isometric orientation sheet

Run twice around _drawings.py:
    <cq python> draw_cont_cast.py         # SVG source from the build
    python3 docs-authority/_drawings.py   # title block + register rows
    <cq python> draw_cont_cast.py         # PDF pass (now from stamped SVGs)
"""
import json, pathlib, re
import cadquery as cq

HERE = pathlib.Path(__file__).parent
ns = __import__("runpy").run_path(HERE / "cont_cast.py")
parts, inv, P = ns["parts"], ns["inv"], ns["P"]
REV = P["graph_revision"]
DRAW = HERE / "drawings"; DRAW.mkdir(exist_ok=True)

def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u

shell = union_all([parts[k] for k in ("frame", "billet_bed")])
hood = union_all([parts[k] for k in ("vent_stub", "stock_stubs", "water_manifold")])
electrode = union_all([parts[k] for k in ("mould", "mould_jacket", "withdrawal_rolls", "runout_rollers")])
aux = union_all([parts[k] for k in ("melt_inlet", "billet_stop", "drain_well")])
full = union_all(list(parts.values()) + list(inv.values()))

SHEETS = [
    ("ga_front", union_all([shell, hood, electrode, aux]), (0, 1, 0),
     ['Keys: 1500 x 800 frame; table deck z 580..610; mould housing -X z 600..800',
      'Two strand centrelines y 280 / 520; withdrawal rolls z 636; run-out rollers to x 1400; billet bed +X',
      'Gantry legs and hoist beam z 1460..1500 for the mould change-out',
      'N1 melt inlet -X z 160; N2 billet stop +X; N3 stock stubs +Y z 600; N4 drain z 50; N5 vent z 800',
      'Strand inventory drawn as solids - process inventory, not a BOM part'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", union_all([shell, hood, electrode, aux]), (1, 0, 0),
     ['Keys: mould housing 220 x 400 x 200 with copper cavities; water jacket plate on the +Z face',
      'Withdrawal rolls OD 90 at x 340 / 520; run-out rollers OD 60 at 90 mm pitch',
      'N1 melt inlet -X z 160 into the mould; general tolerance ISO 2768-m unless noted'],
     "General arrangement, side elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("nozzle_orient", full, (0, 0, -1),
     ['N1 -X face, y 400, z 160: DN15 melt inlet from IND_MELT N8',
      'N2 +X face z 600: billet/slab stop (solids, bore not calculated)',
      'N3 +Y face, x 400 / 640, z 600: DN15 as-cast stock stubs',
      'N4 bottom (400,400): DN15 drain well, flush at z 0',
      'N5 top, DN15 riser at (750,400) to the z 800 datum',
      'Heights/bore/rating per docs-authority/nozzles/CONT_CAST.csv; compass faces are the registered layout choice (params.json layout_note)'],
     "Nozzle orientation, top view. Heights per the task-04 schedule."),
    ("sh01", shell, (0, 1, 0),
     ['Frame: base 1500 x 800 x 40, four 40 x 40 posts, table deck z 580..610; gantry legs 60 wide with the hoist beam z 1460..1500',
      'Billet bed +X overlaps the deck; 6 mm fillet welds (ISO 2553 a6) at the post/deck seams',
      'General tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: frame + billet bed. Welds per ISO 2553; general tolerance ISO 2768-m."),
    ("hd01", hood, (0, 1, 0),
     ['N5 vent riser DN15 from the deck to the z 800 datum; N3 as-cast stock DN15 stubs +Y z 600',
      'Mould water manifold DN36 class along the -Y side; gasket faces per AQS-PIP-003 practice (AQS-STD-002 section 14)',
      'General tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: top group (vent, stock stubs, water manifold)."),
    ("el01", electrode, (0, 1, 0),
     ['Mould housing 220 x 400 x 200 with two copper strand cavities (AQS-SIZE-FOUNDRY); water jacket plate on the +Z face',
      'Withdrawal rolls OD 90 with drive quills at x 340 / 520; run-out rollers OD 60 at 90 mm pitch, 2 mm into the deck',
      'General tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: strand path (mould, withdrawal, run-out)."),
    ("aux01", aux, (0, 1, 0),
     ['N1 melt inlet DN15 -X z 160 into the mould (from IND_MELT N8)',
      'N2 billet stop +X 30 x 400 x 120 on the bed (solids, bore not calculated)',
      'N4 drain sump OD 60, DN15 bore, flush at z 0',
      'General tolerance ISO 2768-m'],
     "Fabricated part sheet: service group (melt inlet, stop, drain)."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: +X face, y along depth, z up; mould, run-out and gantry on the frame',
      'Graph revision AC is the model authority for this build; STEP (export/cont_cast.step) is the solids of record',
      'Strand inventory shown in place - not a BOM part'],
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

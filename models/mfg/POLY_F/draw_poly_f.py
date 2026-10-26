"""POLY_F drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
(content-hash revision per ISO_7200/ASME_Y14_35) and the DRAWING_REGISTER.md rows
are applied by docs-authority/_drawings.py (AQS-DWG-002), which stamps every
model/mfg/*/drawings/*.svg. Geometry and notes:

  ga_front     general arrangement, front elevation (-Y): kettle, jacket, agitator, frame
  ga_side      general arrangement, side elevation (-X)
  nozzle_orient  nozzle orientation, top view (faces per the task-04 schedule)
  sh01         casing + lining + head plate (weld + tolerance notes)
  hd01         top group: dished top, drive, monomer stubs, vent
  el01         discharge: chutes, liquor stubs, drain
  aux01        service group: drain
  iso01        isometric orientation sheet

Run twice around _drawings.py:
    <cq python> draw_poly_f.py            # SVG source from the build
    python3 docs-authority/_drawings.py   # title block + register rows
    <cq python> draw_poly_f.py            # PDF pass (now from stamped SVGs)
"""
import json, pathlib, re
import cadquery as cq

HERE = pathlib.Path(__file__).parent
ns = __import__("runpy").run_path(HERE / "poly_f.py")
parts, inv, P = ns["parts"], ns["inv"], ns["P"]
REV = P["graph_revision"]
DRAW = HERE / "drawings"; DRAW.mkdir(exist_ok=True)

def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u

shell = union_all([parts[k] for k in ("base", "support_skirt", "support_frame", "kettle", "jacket", "dished_top")])
hood = union_all([parts[k] for k in ("vdf_inlet", "tfe_inlet", "vent_stub")])
electrode = union_all([parts[k] for k in ("agitator_shaft", "impeller", "motor", "resin_chute", "powder_chute")])
aux = union_all([parts[k] for k in ("pvdf_stub", "scrap_stub", "drain_well")])
full = union_all(list(parts.values()) + list(inv.values()))

SHEETS = [
    ("ga_front", union_all([shell, hood, electrode, aux]), (0, 1, 0),
     ['Keys: 600 x 600 frame, 1200 envelope datum; kettle OD 150 x 225 at z 500..725, dished top',
      'Agitator shaft + 2 impellers; 0.1 kW drive z 860..960; monomer rail z 1160..1200',
      'N1/N2 monomer DN15 stubs -Y z 160; N3/N4 discharge chutes +X z 600; N5/N6 liquor stubs z 560',
      'N7 drain through the skirt flush at z 0; N8 vent at (300,360) top',
      'Emulsion inventory drawn in place - process inventory, not a BOM part'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", union_all([shell, hood, electrode, aux]), (1, 0, 0),
     ['Keys: jacket OD +28 x 195; Hastelloy C-276 wetted, PTFE gasketed (duty section 3)',
      '60 C duty, 0.0449 kW; general tolerance ISO 2768-m unless noted'],
     "General arrangement, side elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("nozzle_orient", full, (0, 0, -1),
     ['N1 -Y face, x 240, z 160: DN15 VDF monomer inlet', 'N2 -Y face, x 360, z 160: DN15 TFE monomer inlet',
      'N3 +X face z 600: PVDF/PTFE resin chute (solids, bore not calculated)',
      'N4 +X face z 600: fluoropolymer powder chute (solids)',
      'N5 +X face z 560: DN15 PVDF resin to the film/sheet line',
      'N6 -X face z 560: DN15 off-spec scrap/rework',
      'N7 bottom (300,300): DN15 drain through the skirt, flush at z 0; N8 top (300,360) at the z 1200 datum',
      'Heights/bore/rating per docs-authority/nozzles/POLY_F.csv; compass faces are the registered layout choice (params.json layout_note)'],
     "Nozzle orientation, top view. Heights per the task-04 schedule."),
    ("sh01", shell, (0, 1, 0),
     ['Kettle OD 150 x 225 with the jacket and dished top; support skirt on the base plate',
      'Four-post frame to the z 1200 datum with the monomer rail z 1160..1200',
      '6 mm fillet welds (ISO 2553 a6) at the post/base seams; general tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: frame + kettle + jacket. Welds per ISO 2553."),
    ("hd01", hood, (0, 1, 0),
     ['N1/N2 monomer DN15 stubs -Y z 160; N8 vent DN15 at (300,360) top',
      'General tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: monomer + vent."),
    ("el01", electrode, (0, 1, 0),
     ['N3/N4 discharge chutes +X z 600 (PVDF/PTFE resin; fluoropolymer powder)',
      '0.1 kW agitator drive above the dished top; general tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: discharge + drive."),
    ("aux01", aux, (0, 1, 0),
     ['N5 PVDF DN15 stub +X z 560 (to FILM_CAST N2); N6 scrap DN15 stub -X z 560',
      'N7 drain sump through the skirt, flush at z 0; general tolerance ISO 2768-m'],
     "Fabricated part sheet: liquor stubs + drain."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: +X face, y along depth, z up; kettle, jacket, agitator and frame',
      'Graph revision AC is the model authority for this build; STEP (export/poly_f.step) is the solids of record',
      'Emulsion inventory shown in place - not a BOM part'],
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

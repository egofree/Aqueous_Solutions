"""TI_CELL drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
(content-hash revision per ISO_7200/ASME_Y14_35) and the DRAWING_REGISTER.md rows
are applied by docs-authority/_drawings.py (AQS-DWG-002), which stamps every
model/mfg/*/drawings/*.svg. Geometry and notes:

  ga_front     general arrangement, front elevation (-Y): chlorinator, condenser, reduction retort
  ga_side      general arrangement, side elevation (-X)
  nozzle_orient  nozzle orientation, top view (faces per the task-04 schedule)
  sh01         casing + lining + head plate (weld + tolerance notes)
  hd01         gas group: charge hoppers, offtake interconnects, vent riser and stub
  el01         vessels: heater and water bands, furnace box, retort pedestals
  aux01        service group: N1/N5 taps, chutes, stubs, harvest ports, drain
  iso01        isometric orientation sheet

Run twice around _drawings.py:
    <cq python> draw_ti_cell.py           # SVG source from the build
    python3 docs-authority/_drawings.py   # title block + register rows
    <cq python> draw_ti_cell.py           # PDF pass (now from stamped SVGs)
"""
import json, pathlib, re
import cadquery as cq

HERE = pathlib.Path(__file__).parent
ns = __import__("runpy").run_path(HERE / "ti_cell.py")
parts, inv, P = ns["parts"], ns["inv"], ns["P"]
REV = P["graph_revision"]
DRAW = HERE / "drawings"; DRAW.mkdir(exist_ok=True)

def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u

shell = union_all([parts[k] for k in ("chlorinator", "condenser", "reduction_retort", "furnace_box", "skid_frame")])
hood = union_all([parts[k] for k in ("chlorinator_band", "condenser_band", "mg_hopper", "x_chlor_cond", "x_cond_retort", "vent_riser", "vent_stub")])
electrode = union_all([parts[k] for k in ("cl2_stubs", "co_stub", "mgcl2_stubs")])
aux = union_all([parts[k] for k in ("charge_chutes", "mg_chute", "slag_spout", "harvest_ports", "mgcl2_trough", "drain_well")])
full = union_all(list(parts.values()) + list(inv.values()))

SHEETS = [
    ("ga_front", union_all([shell, hood, electrode, aux]), (0, 1, 0),
     ['Keys: 800 x 800 frame, 1600 overall height with the retort lift beam z 1560..1600',
      'Chlorinator z 240..880 at (170,560); condenser z 240..660 at (400,560); reduction retort z 200..720 at (660,520)',
      'N2/N10/N11 charge chutes -X z 160; N3/N9 Cl2 stubs -Y z 160; N12 CO and N1 slag +Y z 600; N4/N5 harvest ports +X z 600; N6/N7 MgCl2 stubs retort +Y z 600; N13 drain z 50; N14 vent z 800',
      'Interconnects OD 24 t 2 slope chlorinator -> condenser -> retort',
      'Ti sponge inventory in the retort drawn as a solid - process inventory, not a BOM part'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", union_all([shell, hood, electrode, aux]), (1, 0, 0),
     ['Keys: chlorinator 800 C with the heater band; condenser with the water band; reduction retort 900 C in the furnace box',
      'Interconnects OD 24 t 2 slope chlorinator -> condenser -> retort; retort lift beam z 1560..1600 for the batch change-out',
      'The chlorine loop closes with MG_POT: N9 feed and N3 return per the A-M-280 ruling; general tolerance ISO 2768-m unless noted'],
     "General arrangement, side elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("nozzle_orient", full, (0, 0, -1),
     ['N2/N10/N11 charge chutes -X z 160 on the chlorinator (grit, rutile concentrate, carbon reductant)',
      'N3/N9 Cl2 stubs -Y z 160 on the chlorinator (loop with MG_POT)',
      'N12 CO export +Y z 600 and N1 slag spout +Y z 600 on the chlorinator',
      'N4/N5 harvest ports +X z 600 and N8 Mg chute -X z 160 on the reduction retort',
      'N6/N7 MgCl2 stubs +Y z 600 on the retort (return to MG_POT; drag-out to flux)',
      'N13 drain bottom (170,560); N14 vent on the condenser top riser at z 800',
      'Heights/bore/rating per docs-authority/nozzles/TI_CELL.csv; compass faces are the registered layout choice (params.json layout_note)'],
     "Nozzle orientation, top view. Heights per the task-04 schedule."),
    ("sh01", shell, (0, 1, 0),
     ['Vessels: chlorinator retort OD 180, condenser OD 140, reduction retort OD 200 - shell seams full-penetration butt welds (ISO 2553)',
      'Skid frame: base plate 800 x 800 x 60, four 40 x 40 posts, retort lift beam z 1560..1600; vessel pedestals carry the interconnect heights',
      'General tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: vessels + skid frame. Welds per ISO 2553; general tolerance ISO 2768-m."),
    ("hd01", hood, (0, 1, 0),
     ['Chlorinator heater band and condenser water band, OD +30 shells, element pockets per the duty sheet',
      'Mg charge hopper cone on the retort; interconnect stubs OD 24 t 2 with full-penetration butt welds (ISO 2553)',
      'N14 vent riser DN15 from the condenser top to the z 800 datum',
      'General tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: gas group (bands, hopper, interconnects, vent)."),
    ("el01", electrode, (0, 1, 0),
     ['N3/N9 chlorine DN15 stubs on the chlorinator -Y shell at z 160 (loop with MG_POT, A-M-280 ruling)',
      'N12 CO export DN15 and N1 slag spout on the +Y shell at z 600',
      'N6/N7 MgCl2 DN15 stubs on the retort +Y shell at z 600 (return to MG_POT; drag-out to flux)',
      'General tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: chlorine and salt connections."),
    ("aux01", aux, (0, 1, 0),
     ['N2/N10/N11 charge chutes on the chlorinator -X face at z 160 (grit, rutile concentrate, carbon reductant)',
      'N4/N5 harvest ports +X z 600 and N8 Mg reductant chute -X z 160 on the reduction retort',
      'N1 slag spout +Y z 600; MgCl2 drag-out trough 640 x 110 x 90 under the frame; N13 drain sump OD 60 flush at z 0',
      'General tolerance ISO 2768-m'],
     "Fabricated part sheet: service group (chutes, harvest, trough, drain)."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: +X face, y along depth, z up; chlorinator, condenser and reduction retort on the skid frame',
      'Graph revision AC is the model authority for this build; STEP (export/ti_cell.step) is the solids of record',
      'Ti sponge inventory in the retort shown in place - not a BOM part'],
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

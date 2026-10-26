"""SHELL_BUILD drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
(content-hash revision per ISO_7200/ASME_Y14_35) and the DRAWING_REGISTER.md rows
are applied by docs-authority/_drawings.py (AQS-DWG-002), which stamps every
model/mfg/*/drawings/*.svg. Geometry and notes:

  ga_front     general arrangement, front elevation (-Y): booth, tank, manipulator
  ga_side      general arrangement, side elevation (-X)
  nozzle_orient  nozzle orientation, top view (faces per the task-04 schedule)
  sh01         casing + lining + head plate (weld + tolerance notes)
  hd01         top group: manipulator mast and arm, rainfall head, vent
  el01         process: slurry tank, drip deck, stucco station
  aux01        service group: chutes, green-shell out, drain
  iso01        isometric orientation sheet

Run twice around _drawings.py:
    <cq python> draw_shell_build.py       # SVG source from the build
    python3 docs-authority/_drawings.py   # title block + register rows
    <cq python> draw_shell_build.py       # PDF pass (now from stamped SVGs)
"""
import json, pathlib, re
import cadquery as cq

HERE = pathlib.Path(__file__).parent
ns = __import__("runpy").run_path(HERE / "shell_build.py")
parts, inv, P = ns["parts"], ns["inv"], ns["P"]
REV = P["graph_revision"]
DRAW = HERE / "drawings"; DRAW.mkdir(exist_ok=True)

def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u

shell = union_all([parts[k] for k in ("booth_frame", "back_guard" if "back_guard" in parts else "dip_deck")])
hood = union_all([parts[k] for k in ("manipulator", "stucco_station", "vent_stub")])
electrode = union_all([parts[k] for k in ("slurry_tank", "dip_deck")])
aux = union_all([parts[k] for k in ("pattern_chute", "green_shell_out", "silica_inlets", "drain_well")])
full = union_all(list(parts.values()) + list(inv.values()))

SHEETS = [
    ("ga_front", union_all([shell, hood, electrode, aux]), (0, 1, 0),
     ['Keys: 1500 x 800 booth, 1500 height; slurry tank 40 L at z 360..700; rainfall stucco station +X end',
      '6-dip manipulator mast over the drip deck; back-wall cladding -Y',
      'N1 pattern chute -X z 160 (from WAX_PATTERN N1); N3/N4 silica inlets -X z 160; N2 green shell +X z 600',
      'N5 drain z 50; N6 vent roof z 1500 datum',
      'Slurry inventory drawn in place - process inventory, not a BOM part'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", union_all([shell, hood, electrode, aux]), (1, 0, 0),
     ['Keys: dip cycle 6 positions (design row); rainfall head above the drip deck',
      'General tolerance ISO 2768-m unless noted'],
     "General arrangement, side elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("nozzle_orient", full, (0, 0, -1),
     ['N1 -X face z 160: wax pattern in from WAX_PATTERN N1 (solids, bore not calculated)',
      'N3/N4 -X face z 160: foundry silica make-up and reclaimed stucco/flour (solids)',
      'N2 +X face z 600: green shell out to SHELL_BURNOUT N1 (solids)',
      'N5 bottom (400,400): DN15 drain, flush at z 0; N6 top (400,400) at the roof datum',
      'Heights/bore/rating per docs-authority/nozzles/SHELL_BUILD.csv; compass faces are the registered layout choice (params.json layout_note)'],
     "Nozzle orientation, top view. Heights per the task-04 schedule."),
    ("sh01", shell, (0, 1, 0),
     ['Booth frame 60 x 60 posts with back-wall cladding; drip deck over the slurry tank',
      '6 mm fillet welds (ISO 2553 a6) at the post/deck seams; general tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: booth frame + drip deck. Welds per ISO 2553."),
    ("hd01", hood, (0, 1, 0),
     ['6-dip manipulator: mast, cross arm, grip hoist',
      'Rainfall stucco station with reclaim pan; N6 vent stub at the roof datum',
      'General tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: manipulator + stucco station + vent."),
    ("el01", electrode, (0, 1, 0),
     ['Slurry tank 40 L (design row); agitated per the duty sheet',
      'General tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: slurry tank."),
    ("aux01", aux, (0, 1, 0),
     ['N1 pattern chute -X z 160; N3/N4 silica inlet chutes -X z 160',
      'N2 green-shell out +X z 600; N5 drain sump OD 60, DN15 bore, flush at z 0',
      'General tolerance ISO 2768-m'],
     "Fabricated part sheet: service group (chutes, outlets, drain)."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: +X face, y along depth, z up; booth, tank, stucco station and manipulator',
      'Graph revision AC is the model authority for this build; STEP (export/shell_build.step) is the solids of record',
      'Slurry inventory shown in place - not a BOM part'],
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

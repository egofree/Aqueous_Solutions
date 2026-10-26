"""SHELL_BREAK drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
(content-hash revision per ISO_7200/ASME_Y14_35) and the DRAWING_REGISTER.md rows
are applied by docs-authority/_drawings.py (AQS-DWG-002), which stamps every
model/mfg/*/drawings/*.svg. Geometry and notes:

  ga_front     general arrangement, front elevation (-Y): table, sieve, enclosure, mast
  ga_side      general arrangement, side elevation (-X)
  nozzle_orient  nozzle orientation, top view (faces per the task-04 schedule)
  sh01         casing + lining + head plate (weld + tolerance notes)
  hd01         top group: sieve rails, enclosure hood, vent mast
  el01         knock-out path: vibratory table, drive, reclaim pan
  aux01        service group: inlets, outlets, drain
  iso01        isometric orientation sheet

Run twice around _drawings.py:
    <cq python> draw_shell_break.py       # SVG source from the build
    python3 docs-authority/_drawings.py   # title block + register rows
    <cq python> draw_shell_break.py       # PDF pass (now from stamped SVGs)
"""
import json, pathlib, re
import cadquery as cq

HERE = pathlib.Path(__file__).parent
ns = __import__("runpy").run_path(HERE / "shell_break.py")
parts, inv, P = ns["parts"], ns["inv"], ns["P"]
REV = P["graph_revision"]
DRAW = HERE / "drawings"; DRAW.mkdir(exist_ok=True)

def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u

shell = union_all([parts[k] for k in ("frame", "vib_table", "vib_drive", "sieve", "reclaim_pan", "enclosure")])
hood = union_all([parts[k] for k in ("vent_stub",)])
electrode = union_all([parts[k] for k in ("cast_inlet", "casting_out", "spent_out", "reclaim_out", "silica_out")])
aux = union_all([parts[k] for k in ("drain_well",)])
full = union_all(list(parts.values()) + list(inv.values()))

SHEETS = [
    ("ga_front", union_all([shell, hood, electrode, aux]), (0, 1, 0),
     ['Keys: 1500 x 800 frame, 1500 height with the service mast; feed deck -X, vibratory table z 610..670',
      'Reclaim sieve (open-top mesh bars) at z 700..730 over the reclaim pan; enclosure hood z 670..950',
      'N1 cast-tree inlet -X z 160; N2 castings +X z 600; N3 spent silica +X z 600; N4/N5 reclaim + return +Y z 600',
      'N6 drain bottom (400,400) flush at z 0; N7 vent on the mast at the z 1500 datum',
      'Cast-tree inventory drawn on the table - process inventory, not a BOM part'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", union_all([shell, hood, electrode, aux]), (1, 0, 0),
     ['Keys: vibratory table with the 0.4 kW drive under the deck; sieve at the stated slope',
      'Enclosure hood over the table for dust control; general tolerance ISO 2768-m unless noted'],
     "General arrangement, side elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("nozzle_orient", full, (0, 0, -1),
     ['N1 -X face z 160: cast + shell in from INV_CAST N4 (solids, bore not calculated)',
      'N2 +X face z 600: investment castings out (solids)',
      'N3 +X face z 600: spent ceramic shell to the solids line (solids)',
      'N4 +Y face z 600: reclaimed stucco/flour (solids); N5 +Y face z 600: spent silica return (solids)',
      'N6 bottom (400,400): DN15 drain, flush at z 0; N7 top on the mast at the z 1500 datum',
      'Heights/bore/rating per docs-authority/nozzles/SHELL_BREAK.csv; compass faces are the registered layout choice (params.json layout_note)'],
     "Nozzle orientation, top view. Heights per the task-04 schedule."),
    ("sh01", shell, (0, 1, 0),
     ['Frame: base 1500 x 800 x 40, four 60 x 60 posts, feed deck inset from the mast corner',
      'Service mast 60 x 60 to the z 1500 datum; 6 mm fillet welds (ISO 2553 a6) at the seams',
      'General tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: frame + table + sieve. Welds per ISO 2553."),
    ("hd01", hood, (0, 1, 0),
     ['N7 vent stub DN15 on the service mast at the z 1500 datum',
      'General tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: vent stub."),
    ("el01", electrode, (0, 1, 0),
     ['N2 investment castings +X z 600; N3 spent silica +X z 600 (solids, bore not calculated)',
      'N4 reclaim +Y z 600 and N5 silica return +Y z 600 (solids)',
      'General tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: product and reclaim outlets."),
    ("aux01", aux, (0, 1, 0),
     ['N1 cast-tree inlet -X z 160, full height to the base',
      'N6 drain sump OD 60, DN15 bore, flush at z 0',
      'General tolerance ISO 2768-m'],
     "Fabricated part sheet: inlet + drain."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: +X face, y along depth, z up; vibratory table, sieve and enclosure on the frame',
      'Graph revision AC is the model authority for this build; STEP (export/shell_break.step) is the solids of record',
      'Cast-tree inventory shown on the table - not a BOM part'],
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

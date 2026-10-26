"""ROLL drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
(content-hash revision per ISO_7200/ASME_Y14_35) and the DRAWING_REGISTER.md rows
are applied by docs-authority/_drawings.py (AQS-DWG-002), which stamps every
model/mfg/*/drawings/*.svg. Geometry and notes:

  ga_front     general arrangement, front elevation (-Y): stand, rolls, roller tables
  ga_side      general arrangement, side elevation (-X)
  nozzle_orient  nozzle orientation, top view (faces per the task-04 schedule)
  sh01         casing + lining + head plate (weld + tolerance notes)
  hd01         top group: screw-down, chocks, vent riser
  el01         pass line: bottom and top rolls, roll window
  aux01        service group: entry/sheet guides, roller tables, drain
  iso01        isometric orientation sheet

Run twice around _drawings.py:
    <cq python> draw_roll.py              # SVG source from the build
    python3 docs-authority/_drawings.py   # title block + register rows
    <cq python> draw_roll.py              # PDF pass (now from stamped SVGs)
"""
import json, pathlib, re
import cadquery as cq

HERE = pathlib.Path(__file__).parent
ns = __import__("runpy").run_path(HERE / "roll.py")
D = ns["D"]
ROLL_Z = ns["ROLL_Z"]
parts, inv, P = ns["parts"], ns["inv"], ns["P"]
REV = P["graph_revision"]
DRAW = HERE / "drawings"; DRAW.mkdir(exist_ok=True)

def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u

shell = union_all([parts[k] for k in ("base", "stand")])
hood = union_all([parts[k] for k in ("screw_down", "roll_chocks", "vent_stub")])
electrode = union_all([parts[k] for k in ("bottom_roll", "top_roll")])
aux = union_all([parts[k] for k in ("table_rollers", "billet_stop", "sheet_guide", "drain_well")])
full = union_all(list(parts.values()) + list(inv.values()))

SHEETS = [
    ("ga_front", union_all([shell, hood, electrode, aux]), (0, 1, 0),
     ['Keys: 1500 x 800 base, 1500 overall height; two-high stand window 300 wide x 260 high at z 880..1140',
      f"Rolls OD {D['rolls_D_mm']} x {D['roll_L_mm']} across the full width; pass line at the bottom-roll centre z {ROLL_Z:.0f}",
      'N1/N3 entry guide -X and N2 sheet guide +X at the pass line; N4 drain z 50; N5 vent to z 800',
      'Roller tables with pedestals tie the entry and exit rollers to the base and the stand',
      'Strip inventory drawn as a solid - process inventory, not a BOM part'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", union_all([shell, hood, electrode, aux]), (1, 0, 0),
     ['Keys: stand housings y 280..520; screw-down z 1150..1500 from the top roll',
      'Roll chocks cross the stand +X face (no coplanar seam); bearing caps per the duty sheet',
      'General tolerance ISO 2768-m unless noted'],
     "General arrangement, side elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("nozzle_orient", full, (0, 0, -1),
     ['N1/N3 billet entry -X at the pass line (solids, bore not calculated)',
      'N2 plate/sheet out +X at the pass line',
      'N4 drain bottom (400,400) flush at z 0; N5 vent riser at (750,400) to the z 800 datum',
      'Heights/bore/rating per docs-authority/nozzles/ROLL.csv; compass faces are the registered layout choice (params.json layout_note)'],
     "Nozzle orientation, top view. Heights per the task-04 schedule."),
    ("sh01", shell, (0, 1, 0),
     ['Base 1500 x 800 x 60 with four 60 x 60 posts; stand housings y 280..520, full-width roll window slot z 880..1140',
      '6 mm fillet welds (ISO 2553 a6) at the post/base seams; general tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: base + stand. Welds per ISO 2553; general tolerance ISO 2768-m."),
    ("hd01", hood, (0, 1, 0),
     ['Screw-down OD 50, z 1150..1500, from the top-roll chock to the frame datum',
      'Roll chocks cross the stand +X face by 20 mm (no coplanar seam); N5 vent riser DN15 to z 800',
      'General tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: top group (screw-down, chocks, vent)."),
    ("el01", electrode, (0, 1, 0),
     ['Bottom roll at z 800..1100 (centre ' + str(ROLL_Z) + '), top roll at z 1100..1400 (screw-adjust gap)',
      'Rolls span the full 800 mm width; driven per the drive side layout',
      'General tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: pass line (bottom and top rolls)."),
    ("aux01", aux, (0, 1, 0),
     ['N1/N3 entry guide -X and N2 sheet guide +X, full height to the base',
      'Roller tables: OD 80 rollers at 100 mm pitch on pedestals tied to the base and the stand',
      'N4 drain sump OD 60, DN15 bore, flush at z 0',
      'General tolerance ISO 2768-m'],
     "Fabricated part sheet: service group (guides, tables, drain)."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: +X face, y along depth, z up; stand, rolls and roller tables on the base',
      'Graph revision AC is the model authority for this build; STEP (export/roll.step) is the solids of record',
      'Strip inventory shown in place - not a BOM part'],
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

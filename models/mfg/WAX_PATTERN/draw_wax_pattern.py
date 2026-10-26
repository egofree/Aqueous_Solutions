"""WAX_PATTERN drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

Run twice around _drawings.py:
    <cq python> draw_wax_pattern.py             # SVG source from the build
    python3 docs-authority/_drawings.py  # title block + register rows
    <cq python> draw_wax_pattern.py             # PDF pass (now from stamped SVGs)
"""
import json, pathlib, re
import cadquery as cq

HERE = pathlib.Path(__file__).parent
import sys
sys.path.insert(0, str(HERE.parents[2]))
from models.mfg import bench_prep
UNIT = "WAX_PATTERN"
report = bench_prep.build_and_export(UNIT)
parts = bench_prep._LAST_PARTS
REV = bench_prep.P["graph_revision"]
DRAW = HERE / "drawings"; DRAW.mkdir(exist_ok=True)

def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u

shell = union_all([parts[k] for k in ("bench_frame", "work_top", "extraction_hood")])
hood = union_all([parts[k] for k in ("wax_pot", "injector_head", "pattern_table")])
electrode = union_all([parts[k] for k in ("pattern_chute",)])
aux = union_all([parts[k] for k in ("condensate_trap", "makeup_hopper", "drain_well", "vent_stub")])
full = union_all(list(parts.values()))
_LAST_PARTS = parts

SHEETS = [
    ("ga_front", union_all([shell, hood, electrode, aux]), (0, 1, 0),
     ['Keys: bench 800 x 600, work top z 850..900; wax pot 10 L and 0.5 kW injector head at z 700..1060',
      'Extraction hood z 900..1080 with the N5 vent to the z 1200 datum',
      'N1 pattern discharge chute +X z 600..900; N2/N3 inlets -X z 160',
      'N4 drain bottom (400,300) flush at z 0',
      'Wax inventory drawn where applicable - process inventory, not a BOM part'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", union_all([shell, hood, electrode, aux]), (1, 0, 0),
     ['Keys: bench 800 x 600, work top z 850..900; extraction hood above; vent to the z 1200 datum',
      'General tolerance ISO 2768-m unless noted'],
     "General arrangement, side elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("nozzle_orient", full, (0, 0, -1),
     ['N1 +X face z 600: pattern discharge chute (solids, bore not calculated)',
      'N2 -X face z 160: wax condensate reclaim (DN15)',
      'N3 -X face z 160: pattern wax make-up, petro-wax class import (solids; A-M-284)',
      'N4 bottom (400,300): DN15 drain, flush at z 0; N5 top: vent at the z 1200 datum',
      'Heights/bore/rating per docs-authority/nozzles/WAX_PATTERN.csv; compass faces are the registered layout choice (params.json layout_note)'],
     "Nozzle orientation, top view. Heights per the task-04 schedule."),
    ("sh01", shell, (0, 1, 0),
     ['Bench frame: four 50 x 50 legs, work top 800 x 600 x 50; hood plenum z 900..1050 and canopy z 1050..1080',
      '6 mm fillet welds (ISO 2553 a6) at the leg/top seams; general tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: bench frame + work top + hood. Welds per ISO 2553."),
    ("hd01", hood, (0, 1, 0),
     ['Wax pot 10 L with the 0.5 kW injector head and the pattern table',
      'General tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: wax pot + injector + pattern table."),
    ("el01", electrode, (0, 1, 0),
     ['Service hardware detail per the unit task-04 schedule',
      'General tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: hardware detail."),
    ("aux01", aux, (0, 1, 0),
     ['N-drain sump OD 60, DN15 bore, flush at z 0; N-vent stub to the z 1200 datum',
      'General tolerance ISO 2768-m'],
     "Fabricated part sheet: drain + vent."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: +X face, y along depth, z up; bench, hood and unit hardware',
      'Graph revision AC is the model authority for this build; STEP (export/wax_pattern.step) is the solids of record'],
     "Isometric orientation sheet."),
]

BAND = 100

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
        pass
    elif "aqs-title-block" in svg.read_text():
        try:
            import cairosvg
            cairosvg.svg2pdf(url=str(svg), write_to=str(DRAW / f"{sid}.pdf"))
            pdf = "pdf+svg current"
        except Exception as e:
            pdf = f"pdf skipped ({e.__class__.__name__})"
        continue
    cq.exporters.export(shape.val(), str(svg), opt={"projectionDir": pdir, "showAxes": False, "showHidden": True})
    add_notes(svg, notes)
print(json.dumps({"sheets": [s[0] for s in SHEETS], "pdf": pdf}))

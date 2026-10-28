# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""FARM / HAB / POLY drawing sets (X-FARM / X-HAB / X-POLY M3 follow-on pass).

Eight sheets per unit from the accepted build: GA front/side/plan, isometric, and
four part/detail sheets drawn from the form class's own parts. Rebuilds the parts
from params.json (the same arithmetic the check.json verified) - reads nothing
else. SVG + notes bands first; `docs-authority/_drawings.py` stamps the title
blocks and writes the register rows; a second pass emits the PDFs (cairosvg).

Run: $CADQUERY_PYTHON models/mfg/farm_hab_draw.py UNIT [UNIT ...]
"""
import json, pathlib, re, sys
import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1]))
from models.mfg import farm_hab

BAND = 100
TOL = 'General tolerance ISO 2768-m unless noted.'


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


def add_notes(svg_path, unit, notes):
    s = svg_path.read_text()
    w = float(re.search(r'width="([\d.]+)"', s).group(1))
    h = float(re.search(r'height="([\d.]+)"', s).group(1))
    s = re.sub(r'height="[\d.]+"', f'height="{h + BAND}"', s, count=1)
    rows = [f'{unit} - {svg_path.stem}: {n}' for n in notes]
    block = f'<g id="aqs-fab-notes" transform="translate(0,{h})" font-family="DejaVu Sans,sans-serif" font-size="10" fill="#000">'
    for i, n0 in enumerate(rows):
        block += f'<text x="6" y="{24 + 13 * i}">{n0}</text>'
    block += '</g>'
    svg_path.write_text(s.replace('</svg>', block + '</svg>'))


def sheets_for(P, parts):
    """Eight (sid, shape, projection_dir, notes, title) per the form class."""
    L, W, H = P['size_mm']
    mat = P.get('material_class', 'HDPE')
    note = P.get('size_note', '')
    full = union_all(list(parts.values()))
    base = [
        ('ga_front', full, (0, 1, 0), [note, f'Shell class {mat}.', TOL],
         'General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7).'),
        ('ga_side', full, (1, 0, 0), [note, TOL],
         'General arrangement, side elevation. Shop, not stamped (AQS-STD-001 section 7).'),
        ('plan', full, (0, 0, -1), [note, TOL], 'Plan view.'),
        ('iso01', full, (1, -1, 1),
         ['Shop orientation: +X face, y along depth, z up.',
          f'STEP (export/{P["unit"].lower()}.step) is the solids of record; the graph Rev AC node is the model authority.'],
         'Isometric orientation sheet.'),
    ]
    out = list(base)
    # four part/detail sheets from the form's own parts
    detail_parts = [(k, v) for k, v in parts.items() if k not in
                    tuple(f'{x}_{y}' for x in ('baffle', 'stub') for y in
                          ('1', '2', '3', '4'))]
    while len(detail_parts) < 4:   # pad with derived views of the full body
        detail_parts.append((f'detail_{len(detail_parts) + 1}', full))
    for i, (k, v) in enumerate(detail_parts[:4]):
        pdir = [(0, 1, 0), (1, 0, 0), (0, 0, -1), (1, -1, 1)][i % 4]
        out.append((f'pt{i + 1}_{k[:18]}', v, pdir,
                    [f'{k}: sheet-metal / shell part per params.json; class {mat}.', TOL],
                    f'Fabricated part sheet: {k.replace("_", " ")}.'))
    return out[:8]


def draw(unit):
    H = HERE / unit
    P = json.loads((H / 'params.json').read_text())
    parts = farm_hab.FORMS[P['form']](P)
    DRAW = H / 'drawings'
    DRAW.mkdir(exist_ok=True)
    pdf = 'svg current (stamped pass pending)'
    for sid, shape, pdir, notes, _title in sheets_for(P, parts):
        svg = DRAW / f'{sid}.svg'
        if svg.exists():
            content = svg.read_text()
            if 'aqs-title-block' in content:
                try:
                    import cairosvg
                    cairosvg.svg2pdf(url=str(svg), write_to=str(DRAW / f'{sid}.pdf'))
                    pdf = 'pdf+svg current'
                except Exception as e:
                    pdf = f'pdf skipped ({e.__class__.__name__})'
                continue
        cq.exporters.export(shape.val(), str(svg),
                            opt={'projectionDir': pdir, 'showAxes': False, 'showHidden': True})
        add_notes(svg, unit, notes)
    print(json.dumps({'unit': unit, 'form': P['form'], 'sheets': 8, 'pdf': pdf}))


if __name__ == '__main__':
    for u in (sys.argv[1:] or []):
        draw(u)

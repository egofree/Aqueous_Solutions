# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""X-3D-SITE: per-site 3D plant model from the placement model (AQS-3D-BUILD-001 Rev M).

Builds a site's plant model from real, sourced data only:
- flow_graph/placement_seed.json (Rev M+): blocks, level datums, per-unit centres and
  sizes - every solid traces to a cited placement entry;
- the site's scaling plan (flow_graph/param/sites/<sid>.json): eliminated units leave
  the built model and ride a separate labelled ghost layer (never silent);
- the site's replacement placements ride at their placement-model sizing.

Units without a seed placement mass at their block centre, tagged `block-centre
massing, placement pending`, and are named in the manifest. Units with neither a
placement nor a block are named `unplaced` and carry no solid. Nothing is invented:
massing boxes at sourced centres, not detailed CAD.

Outputs under media/3d/:
- site_model.glb          glTF binary; one named box mesh per unit (+ ghosts); Z-up, mm
- SITE_AXO.svg            labelled axonometric sheet (blocks, units, ghosts, datums)
- LEVEL_<name>.svg        labelled plan per level
- MODEL_MANIFEST.json     per-unit state, coverage, eliminated and unplaced lists

Run: AQS_SITE=<sid> python3 -m flow_graph.param.site_3d [OUT_DIR]   (default media/3d)
"""
import json
import math
import os
import sys

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if R not in sys.path:
    sys.path.insert(0, R)

SEED = os.path.join(R, 'flow_graph', 'placement_seed.json')
GRAPH = os.path.join(R, 'flow_graph', 'plant_flow_graph.json')
SITES = os.path.join(R, 'flow_graph', 'param', 'sites')

SECTOR_COLORS = {
    'ELEC': '#2c6fbb', 'HAB': '#c0392b', 'FARM': '#1e8449', 'WTR': '#2471a3',
    'DIGESTER': '#7d6608', 'MFG': '#6c3483', 'FOUNDRY': '#935116', 'FAB': '#117864',
    'GAS': '#b03a2e', 'GEO': '#5d6d7e', 'GLASS': '#a04000', 'HEAT': '#d68910',
    'MEOH': '#117a65', 'NUT': '#884ea0', 'OIL': '#7b241c', 'POLYMERS': '#1f618d',
    'PUMPED_HYDRO': '#2874a6', 'CRYO': '#5499c7', 'DOCK': '#85929e',
}


def _color(sector):
    return SECTOR_COLORS.get(sector, '#666666')


def collect(site_id=None):
    """Per-unit 3D state for a site: placement, status, sector, block, label data."""
    seed = json.load(open(SEED))
    g = json.load(open(GRAPH))
    D = seed['datums_mm']
    present = {n['unit_id']: n for n in g['nodes'] if n.get('presence') in ('present', 'placeholder')}
    seeded = {u['unit_id']: u for u in seed['units']}
    block_of, block_geom = {}, {}
    for b in seed['blocks']:
        block_geom[b['block_id']] = b
        for u in b.get('unit_ids', []):
            block_of.setdefault(u, b['block_id'])

    # the site's scaling plan
    plan, errors = {}, []
    if site_id and site_id != 'baseline':
        from flow_graph.param import scaling as SC
        prof_path = os.path.join(SITES, f'{site_id}.json')
        prof = json.load(open(prof_path))
        plan, errors = SC.resolve(prof, present)

    out = []
    for uid, node in sorted(present.items()):
        st = plan.get(uid, {})
        status = st.get('status', 'kept')
        replaced_by = st.get('replacement')
        sector = node.get('sector_id', '')
        s = seeded.get(uid)
        if s:
            level = s['level']
            origin = list(s['origin_mm']) + [0] * (3 - len(s['origin_mm']))
            origin[2] = origin[2] + D.get(level, 0)      # the seed Z is relative to the level datum
            size = list(s['size_mm']) + [1500] * (3 - len(s['size_mm']))   # nominal height when unissued
            basis = s.get('source', 'placement seed')
            geom = 'placement'
        else:
            blk = block_of.get(uid)
            if blk:
                bg = block_geom[blk]
                level = bg.get('level', 'L0')
                origin = list(bg['origin_mm']) + [0] * (3 - len(bg['origin_mm']))
                origin[2] = D.get(level, 0)
                size = list(bg['size_mm']) + [1500] * (3 - len(bg['size_mm']))
                basis = f'block-centre massing of {blk} (placement pending)'
                geom = 'block-massing'
            else:
                out.append(dict(unit_id=uid, sector_id=sector, status='unplaced',
                                replaced_by=replaced_by or None))
                continue
        out.append(dict(unit_id=uid, sector_id=sector, level=level,
                        origin_mm=origin, size_mm=size, basis=basis,
                        status=('eliminated' if status == 'eliminated' else 'built'),
                        replaced_by=replaced_by or None,
                        geom=geom))
    return out, D, seed, errors


def _box_faces(origin, size):
    """Axonometric faces of a box: top + the two viewer-facing sides (Z-up mm)."""
    x, y, z = origin
    sx, sy, sz = size
    c = [(x, y, z), (x + sx, y, z), (x + sx, y + sy, z), (x, y + sy, z),
         (x, y, z + sz), (x + sx, y, z + sz), (x + sx, y + sy, z + sz), (x, y + sy, z + sz)]

    def iso(p):
        px, py, pz = p
        return ((px - py) * math.cos(math.pi / 6), -(pz + (px + py) * math.sin(math.pi / 6)))

    pts = [iso(p) for p in c]
    top = [pts[4], pts[5], pts[6], pts[7]]
    left = [pts[0], pts[1], pts[5], pts[4]]     # -Y face
    right = [pts[1], pts[2], pts[6], pts[5]]    # +X face
    depth = sum((x + y + z) for x, y, z in c)
    return {'top': top, 'left': left, 'right': right, 'depth': depth,
            'centre_iso': iso((x + sx / 2, y + sy / 2, z + sz / 2))}


def _svg_poly(pts, fill, stroke, dashed=False, opacity=1.0):
    dash = ' stroke-dasharray="18 10"' if dashed else ''
    pp = ' '.join(f'{x:.0f},{y:.0f}' for x, y in pts)
    return (f'<polygon points="{pp}" fill="{fill}" fill-opacity="{opacity}" '
            f'stroke="{stroke}" stroke-width="2"{dash}/>')


def axo_svg(units3d, D, site_label):
    """Labelled axonometric sheet: blocks, built units, eliminated ghosts, datums."""
    xs, ys = [], []
    geoms = []
    for u in units3d:
        if 'origin_mm' not in u:
            continue
        f = _box_faces(u['origin_mm'], u['size_mm'])
        geoms.append((u, f))
        for p in f['top'] + f['left'] + f['right']:
            xs.append(p[0]); ys.append(p[1])
    if not xs:
        return '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="120"><text x="10" y="60">no placed units</text></svg>'
    pad = 60
    x0, y0 = min(xs) - pad, min(ys) - pad
    w, h = max(xs) - x0 + 2 * pad, max(ys) - y0 + 2 * pad + 40
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h:.0f}" '
         f'font-family="DejaVu Sans,sans-serif" font-size="13">',
         f'<rect x="0" y="0" width="{w:.0f}" height="{h:.0f}" fill="white"/>',
         f'<text x="16" y="28" font-size="17" font-weight="bold">{site_label} plant - placement-model axonometric (schematic: positions carry no dimension beyond the placement model)</text>',
         f'<text x="16" y="48" font-size="12" fill="#555">Z-up, mm. Solid = built at this site. Dashed = eliminated by the scaling plan (function moved to the labelled replacement). Grey = block-centre massing, placement pending.</text>']
    geoms.sort(key=lambda g: g[1]['depth'])          # painter: far first
    for u, f in geoms:
        elim = u['status'] == 'eliminated'
        col = _color(u['sector_id'])
        cx, cy = f['centre_iso']
        o.append(_svg_poly(f['top'], col if not elim else 'none', col, dashed=elim, opacity=0.92))
        o.append(_svg_poly(f['left'], '#00000022' if not elim else 'none', col, dashed=elim))
        o.append(_svg_poly(f['right'], '#00000044' if not elim else 'none', col, dashed=elim))
        if not elim:
            o.append(f'<text x="{cx:.0f}" y="{cy:.0f}" textAnchor="middle" fontSize="12" '
                     f'fill="#111">{u["unit_id"]}</text>')
        elif u.get('replaced_by'):
            o.append(f'<text x="{cx:.0f}" y="{cy:.0f}" textAnchor="middle" fontSize="11" '
                     f'fill="#c0392b">{u["unit_id"]} -> {u["replaced_by"]}</text>')
    o.append(f'<text x="{w - 340:.0f}" y="{h - 30:.0f}" fontSize="11" fill="#555">levels (mm): '
             + ', '.join(f'{k} {v}' for k, v in sorted(D.items(), key=lambda kv: kv[1])) + '</text>')
    o.append(f'<text x="{w - 340:.0f}" y="{h - 12:.0f}" fontSize="11" fill="#555">+X right-down, +Y left-down, +Z up. Source: placement_seed Rev M+.</text>')
    o.append('</svg>')
    return '\n'.join(o)


def plan_svg(units3d, level, D, site_label):
    """Labelled plan per level: X-Y rectangles at the level datum."""
    rows, xs, ys = [], [], []
    for u in units3d:
        if 'origin_mm' not in u or u['level'] != level:
            continue
        x, y = u['origin_mm'][0], u['origin_mm'][1]
        sx, sy = u['size_mm'][0], u['size_mm'][1]
        xs += [x, x + sx]; ys += [y, y + sy]
        rows.append((u, x, y, sx, sy))
    if not rows:
        return None
    pad = 80
    x0, y0 = min(xs) - pad, min(ys) - pad
    w, h = max(xs) - x0 + 2 * pad, max(ys) - y0 + 2 * pad + 46
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h:.0f}" '
         f'font-family="DejaVu Sans,sans-serif" font-size="12">',
         f'<rect x="0" y="0" width="{w:.0f}" height="{h:.0f}" fill="white"/>',
         f'<text x="16" y="26" font-size="15" font-weight="bold">{site_label} - level {level} plan (mm, +X right, +Y up)</text>',
         f'<text x="16" y="44" font-size="11" fill="#555">datum Z {D.get(level, 0)} mm. Dashed = eliminated by the scaling plan.</text>']
    for u, x, y, sx, sy in rows:
        elim = u['status'] == 'eliminated'
        col = _color(u['sector_id'])
        o.append(f'<rect x="{x - x0:.0f}" y="{y - y0:.0f}" width="{sx:.0f}" height="{sy:.0f}" '
                 f'fill="{col}22" stroke="{col}" stroke-width="2" '
                 f'stroke-dasharray="10 6" fill-opacity="0.85"/>' if elim else
                 f'<rect x="{x - x0:.0f}" y="{y - y0:.0f}" width="{sx:.0f}" height="{sy:.0f}" '
                 f'fill="{col}33" stroke="{col}" stroke-width="2"/>')
        o.append(f'<text x="{x - x0 + 6:.0f}" y="{y - y0 + 16:.0f}" fontSize="11">{u["unit_id"]}</text>')
    o.append('</svg>')
    return '\n'.join(o)


def glb(units3d, out_path):
    """glTF binary: one named box per unit; ghosts in a separate 'eliminated' node set."""
    import trimesh
    import numpy as np
    scene = trimesh.Scene()
    for u in units3d:
        if 'origin_mm' not in u:
            continue
        sx, sy, sz = u['size_mm']
        cx = u['origin_mm'][0] + sx / 2
        cy = u['origin_mm'][1] + sy / 2
        cz = u['origin_mm'][2] + sz / 2
        m = trimesh.creation.box(extents=[sx, sy, sz])
        m.apply_translation([cx, cy, cz])
        m.metadata.update({'sector': u['sector_id'], 'status': u['status'],
                           'level': u['level'], 'basis': u.get('basis', '')})
        name = u['unit_id'] + (' [eliminated]' if u['status'] == 'eliminated' else '')
        scene.add_geometry(m, node_name=name, geom_name=name)
    scene.export(out_path)
    return len(scene.geometry)


def build(site_id=None, out_dir=None):
    """Build the site's 3D artifacts. Returns the manifest dict."""
    site_id = site_id or os.environ.get('AQS_SITE') or 'baseline'
    out_dir = out_dir or os.path.join(R, 'media', '3d')
    os.makedirs(out_dir, exist_ok=True)
    units3d, D, seed, errors = collect(site_id)
    label = (site_id + ' ' if site_id != 'baseline' else 'Baseline ') + 'site'

    # the glTF binary
    n_geom = 0
    try:
        n_geom = glb(units3d, os.path.join(out_dir, 'site_model.glb'))
    except Exception as exc:
        errors.append(f'glb export failed: {exc}')

    # the axonometric + per-level plans
    open(os.path.join(out_dir, 'SITE_AXO.svg'), 'w').write(axo_svg(units3d, D, label))
    levels = sorted({u['level'] for u in units3d if 'origin_mm' in u},
                    key=lambda lv: D.get(lv, 0))
    plans = {}
    for lv in levels:
        svg = plan_svg(units3d, lv, D, label)
        if svg:
            open(os.path.join(out_dir, f'LEVEL_{lv.replace("-", "m")}.svg'), 'w').write(svg)
            plans[lv] = f'LEVEL_{lv.replace("-", "m")}.svg'

    built = [u for u in units3d if u['status'] == 'built' and 'origin_mm' in u]
    ghosts = [u for u in units3d if u['status'] == 'eliminated' and 'origin_mm' in u]
    massing = [u for u in units3d if u.get('geom') == 'block-massing']
    unplaced = [u['unit_id'] for u in units3d if u['status'] == 'unplaced']
    manifest = {
        'site_id': site_id,
        'placement_seed_revision': seed.get('revision'),
        'units_total': len(units3d),
        'built': len(built), 'ghosts_eliminated': len(ghosts),
        'block_centre_massing': len(massing), 'unplaced': unplaced,
        'routed_note': ('3D geometry is placement-model massing at sourced centres; '
                        'detailed CAD remains models/freecad + models/mfg.'),
        'levels': levels, 'plans': plans,
        'glb_units': n_geom, 'errors': errors,
        'units': [{k: u.get(k) for k in ('unit_id', 'sector_id', 'level', 'status',
                                         'replaced_by', 'basis') if u.get(k) is not None}
                  for u in units3d],
    }
    json.dump(manifest, open(os.path.join(out_dir, 'MODEL_MANIFEST.json'), 'w'), indent=1)
    return manifest


if __name__ == '__main__':
    sid = os.environ.get('AQS_SITE') or 'baseline'
    out = sys.argv[1] if len(sys.argv) > 1 else None
    m = build(sid, out)
    print(f"site_3d[{m['site_id']}]: built {m['built']}, ghosts {m['ghosts_eliminated']}, "
          f"massing {m['block_centre_massing']}, unplaced {len(m['unplaced'])}")

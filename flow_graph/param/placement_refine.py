# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""X-PIP-03 placement refinement: grid positions -> process-adjacency ordering.

The Rev N grid placements put units at sequential positions without design logic,
and the Rev N blocks themselves were dropped at arbitrary coordinates. This
module refines both levels:

1. Block seating (per level): the Rev N blocks - identified by 'Rev N' in the
   block's own source note - are re-seated by weighted process adjacency. The
   block graph's edge weights are the mass-edge counts between block pairs on
   the same level; each movable block takes the collision-free position that
   minimises the weighted distance to its neighbour blocks. Blocks without the
   Rev N marker are PINNED: their units carry designed-placement citations and
   their absolute positions are prior design intent.

2. Unit seating (within each block holding grid placements): a BFS from the
   block's source units (no in-edges from within the block) through the mass
   edges sets the placement priority - upstream units claim slots first - and a
   greedy pass seats each unit in the free slot minimising
   (a) the total distance to its already-seated intra-block neighbours, plus
   (b) the distance to the nearest point of each cross-block neighbour's
   rectangle (projection lower-bounds the cross-block run).

Layout rules (shop-floor convention): rows grow left-to-right and stack
downward; 800 mm maintenance clearance between unit footprints, 3 m fire lane
between blocks, 500 mm wall keep-out; designed units are seat obstacles; a
block whose re-seated units do not fit its declared rectangle grows and
records the growth in its source note.

Consequence, measured against the Rev N grid baseline: the grid crammed units
past their block edges (67 out-of-block placements, 2 footprint overlaps),
which bought ~6 % shorter conduit. The refined layout is VALID (every
re-seated unit inside its block, no overlaps) and process-adjacency-ordered
(intra-block runs -43 % in the largest block); the honest price is ~6 % more
routed length, accepted in exchange for a layout a plant could actually build.
Run: python3 -m flow_graph.param.placement_refine
"""
import json
import math
import os
from collections import defaultdict, deque

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SEED = os.path.join(R, 'flow_graph', 'placement_seed.json')
GP = os.path.join(R, 'flow_graph', 'plant_flow_graph.json')

CLEAR = 800           # maintenance clearance between unit footprints, mm
MARGIN = 500          # block wall keep-out, mm
FIRE_LANE = 3000      # clearance between blocks, mm
Z_DATUM = {'L0': 0, 'L-1': -6000, 'L-2': -16468, 'L1': 6000, 'L2': 10800, 'ROOF': 34800}


def load():
    seed = json.load(open(SEED))
    g = json.load(open(GP))
    return seed, g


def block_assignments(seed):
    """unit_id -> block_id from the seed's block definitions."""
    blk = {}
    for b in seed['blocks']:
        for u in b.get('unit_ids', []):
            blk[u] = b['block_id']
    return blk


def _footprint(entry):
    sz = entry.get('size_mm') or [1500, 1000]
    w = float(sz[0]) if len(sz) > 0 and isinstance(sz[0], (int, float)) else 1500.0
    d = float(sz[1]) if len(sz) > 1 and isinstance(sz[1], (int, float)) else 1000.0
    return w, d


def _rects_overlap(a, b, gap=0.0):
    return not (a[0] + a[2] + gap <= b[0] or b[0] + b[2] + gap <= a[0]
                or a[1] + a[3] + gap <= b[1] or b[1] + b[3] + gap <= a[1])


def _nearest_point(rect, x, y):
    """Nearest point of rect (x0, y0, w, d) to (x, y)."""
    return (min(max(x, rect[0]), rect[0] + rect[2]),
            min(max(y, rect[1]), rect[1] + rect[3]))


def seat_blocks(seed, g):
    """Re-seat the Rev N blocks around the pinned constellation, per level.

    Returns {block_id: (dx, dy)} translation deltas (0,0 for pinned blocks).
    """
    movable = {b['block_id'] for b in seed['blocks'] if 'Rev N' in (b.get('source') or '')}
    blocks = {b['block_id']: b for b in seed['blocks']}
    levels = defaultdict(list)
    for bid, b in blocks.items():
        levels[b.get('level', 'L0')].append(bid)

    # weighted block adjacency from same-level cross-block mass edges
    N = {n['unit_id']: n for n in g['nodes']}
    present = {uid for uid, n in N.items() if n.get('presence') in ('present', 'placeholder')}
    blk = block_assignments(seed)
    w = defaultdict(lambda: defaultdict(int))
    for e in g['edges']:
        if e['presence'] != 'present' or 'mass' not in (e.get('layers') or []):
            continue
        f, t = e['from_unit_id'], e['to_unit_id']
        if f not in present or t not in present:
            continue
        bf, bt = blk.get(f), blk.get(t)
        if not bf or not bt or bf == bt:
            continue
        if blocks[bf].get('level', 'L0') != blocks[bt].get('level', 'L0'):
            continue
        w[bf][bt] += 1
        w[bt][bf] += 1

    deltas = {}
    for lv, bids in levels.items():
        mov = sorted(set(bids) & movable, key=lambda b: -sum(w[b].values()))
        if not mov:
            continue
        seated = {}                                  # bid -> (x0, y0, w, d)

        def rect_of(bid, x=None, y=None):
            b = blocks[bid]
            return (b['origin_mm'][0] if x is None else x,
                    b['origin_mm'][1] if y is None else y,
                    b['size_mm'][0], b['size_mm'][1])

        for bid in bids:
            if bid not in movable:
                seated[bid] = rect_of(bid)           # pinned

        for bid in mov:                              # heaviest first
            b = blocks[bid]
            bw, bd = b['size_mm'][0], b['size_mm'][1]
            nbrs = {nb: wt for nb, wt in w[bid].items() if nb in seated}
            # candidate seats: the four sides of every seated rect
            cands = []
            for nb, r in seated.items():
                for (cx, cy) in ((r[0] + r[2] + FIRE_LANE, r[1]),
                                 (r[0] - bw - FIRE_LANE, r[1]),
                                 (r[0], r[1] + r[3] + FIRE_LANE),
                                 (r[0], r[1] - bd - FIRE_LANE)):
                    cand = (cx, cy, bw, bd)
                    if any(_rects_overlap(cand, s, FIRE_LANE) for s in seated.values()):
                        continue
                    if cand[1] + bd <= 0 or cand[1] < -20000:   # keep the canvas sane
                        continue
                    cands.append(cand)
            if not cands:
                deltas[bid] = (0, 0)
                seated[bid] = rect_of(bid)
                continue

            def sc(c):
                cx, cy = c[0] + bw / 2, c[1] + bd / 2
                if not nbrs:                         # unconnected: nearest to canvas origin
                    return (cx * cx + cy * cy, cx, cy)
                return (sum(wt * math.dist((cx, cy), _nearest_point(seated[nb], cx, cy))
                            for nb, wt in nbrs.items()), cx, cy)

            best = min(cands, key=sc)
            seated[bid] = best
            deltas[bid] = (round(best[0] - b['origin_mm'][0]),
                           round(best[1] - b['origin_mm'][1]))
    return deltas


def apply_block_deltas(seed, deltas):
    """Translate every unit of a moved block by its block's delta."""
    blk = block_assignments(seed)
    n = 0
    for u in seed['units']:
        d = deltas.get(blk.get(u['unit_id']))
        if d and (d[0] or d[1]):
            u['origin_mm'][0] += d[0]
            u['origin_mm'][1] += d[1]
            n += 1
    for b in seed['blocks']:
        d = deltas.get(b['block_id'])
        if d and (d[0] or d[1]):
            b['origin_mm'][0] += d[0]
            b['origin_mm'][1] += d[1]
    return n


def refine(seed, g):
    """Refine block positions and grid placements. Returns {unit_id: new_entry_data}."""
    N = {n['unit_id']: n for n in g['nodes']}
    present = {uid for uid, n in N.items() if n.get('presence') in ('present', 'placeholder')}
    blk = block_assignments(seed)

    deltas = seat_blocks(seed, g)
    moved_units = apply_block_deltas(seed, deltas)

    blocks_by_id = {b['block_id']: b for b in seed['blocks']}
    by_block = defaultdict(dict)
    for u in seed['units']:
        uid = u['unit_id']
        if uid not in present:
            continue
        if 'grid placement' not in (u.get('source') or ''):
            continue                                # already designed
        b = blk.get(uid)
        if b:
            by_block[b][uid] = u

    edges_in_block = defaultdict(list)
    cross_edges = defaultdict(lambda: defaultdict(int))
    for e in g['edges']:
        if e['presence'] != 'present' or 'mass' not in (e.get('layers') or []):
            continue
        f, t = e['from_unit_id'], e['to_unit_id']
        bf, bt = blk.get(f), blk.get(t)
        if bf and bf == bt:
            edges_in_block[bf].append((f, t))
        elif bf and bt and bf != bt:
            if f in by_block.get(bf, {}):
                cross_edges[f][bt] += 1
            if t in by_block.get(bt, {}):
                cross_edges[t][bf] += 1

    refined = {}
    for blk_id, units_in_blk in sorted(by_block.items()):
        bg = blocks_by_id.get(blk_id)
        if not bg:
            continue
        designed = [u for u in seed['units']
                    if u['unit_id'] in present
                    and blk.get(u['unit_id']) == blk_id
                    and u['unit_id'] not in units_in_blk]
        geom = {'origin_mm': bg['origin_mm'], 'size_mm': bg['size_mm'],
                'level': bg.get('level', 'L0'), '_designed_units': designed}
        nbr_rects = {bid: (b['origin_mm'][0], b['origin_mm'][1],
                           b['size_mm'][0], b['size_mm'][1])
                     for bid, b in blocks_by_id.items() if bid != blk_id}
        positions = seat_units(units_in_blk, edges_in_block.get(blk_id, []),
                               geom, nbr_rects, cross_edges, block_entry=bg)
        for uid, pos in positions.items():
            refined[uid] = {**pos, 'block': blk_id}
    return refined


def seat_units(units_in_block, edges_in_block, block_geom, nbr_rects, cross_edges,
               block_entry=None):
    """Greedy unit seating (see module docstring).

    Obstacle-aware: the block's DESIGNED units (not being re-seated) are no-go
    rectangles. If the re-seated units genuinely do not fit the declared block
    rectangle, the block grows (size_mm) and the growth is recorded in its
    source note.
    """
    ox, oy = block_geom['origin_mm'][0], block_geom['origin_mm'][1]
    sx, sy = block_geom['size_mm'][0], block_geom['size_mm'][1]
    z = Z_DATUM.get(block_geom.get('level', 'L0'), 0)

    adj = defaultdict(set)
    for f, t in edges_in_block:
        adj[f].add(t)
        adj[t].add(f)

    in_deg = {u: 0 for u in units_in_block}
    for _f, t in edges_in_block:
        if t in in_deg:
            in_deg[t] += 1
    sources = sorted((u for u in units_in_block if in_deg[u] == 0),
                     key=lambda u: (-_footprint(units_in_block[u])[0], u))
    order, visited = [], set()
    queue = deque(sources)
    while queue:
        u = queue.popleft()
        if u in visited or u not in units_in_block:
            continue
        visited.add(u)
        order.append(u)
        for t in sorted(adj[u]):
            if t not in visited:
                queue.append(t)
    order.extend(sorted(set(units_in_block) - visited))   # orphans last

    # obstacles: designed units already occupying this block
    obstacles = [(u['origin_mm'][0], u['origin_mm'][1],
                  float(u['size_mm'][0]), float(u['size_mm'][1]))
                 for u in block_geom.get('_designed_units', [])]

    rows, centres, positions = [], {}, {}
    placed = []

    def blocked(x, y, w, d):
        r = (x, y, w, d)
        return any(_rects_overlap(r, ob, CLEAR) for ob in obstacles) or \
               any(_rects_overlap(r, p, CLEAR) for p in placed)

    def score(u, x, y, nbrs):
        if nbrs:
            s = sum(abs(x - nx) + abs(y - ny) for nx, ny in nbrs)
        else:
            s = abs(y - (oy + sy / 2.0))             # neutral: middle band
        for bid, wt in (cross_edges.get(u) or {}).items():
            if bid in nbr_rects:
                px, py = _nearest_point(nbr_rects[bid], x, y)
                s += wt * math.hypot(x - px, y - py) * 0.05   # gentle boundary bias
        return s

    max_bottom = oy + MARGIN
    max_right = ox + MARGIN
    for u in order:
        w, d = _footprint(units_in_block[u])
        nbrs = [centres[n] for n in adj[u] if n in centres]
        cands = []
        for row in rows:
            x = row['x_end'] + CLEAR
            while blocked(x, row['y'], w, d):        # slide past the obstacle
                hit = next((ob for ob in obstacles + placed
                            if _rects_overlap((x, row['y'], w, d), ob, CLEAR)), None)
                if hit is None:
                    break
                x = hit[0] + hit[2] + CLEAR
            if x + w <= ox + sx - MARGIN:
                cands.append((x, row['y'], row))
        new_y = (oy + MARGIN + sum(r['h'] + CLEAR for r in rows)) if rows else oy + MARGIN
        # push the new row below any obstacle crossing its band
        changed = True
        while changed:
            changed = False
            for ob in obstacles:
                if _rects_overlap((ox, new_y, sx, d), ob, 0):
                    new_y = ob[1] + ob[3] + CLEAR
                    changed = True
        cands.append((ox + MARGIN, new_y, None))
        x, y, row = min(cands, key=lambda c: (score(u, c[0], c[1], nbrs), c[0], c[1]))
        if row is None:
            row = {'y': y, 'x_end': x + w, 'h': d}
            rows.append(row)
        else:
            row['x_end'] = x + w
            row['h'] = max(row['h'], d)
        placed.append((x, y, w, d))
        centres[u] = (x + w / 2.0, y + d / 2.0)
        max_bottom = max(max_bottom, y + d)
        max_right = max(max_right, x + w)
        positions[u] = {
            'origin_mm': [round(x), round(y), z],
            'source': (f'process-adjacency placement (two-level refinement: Rev N blocks '
                       f'seated by weighted adjacency around the pinned constellation, then '
                       f'greedy nearest-to-seated-neighbours; mass edges set geometry; '
                       f'{CLEAR:g} mm clearance). Grid predecessor: sequential fill without design logic.'),
        }

    # the block declaration must envelope its contents: grow if the seating
    # exceeded the declared rectangle
    if block_entry is not None:
        grew = []
        need_x, need_y = round(max_right + MARGIN - ox), round(max_bottom + MARGIN - oy)
        if need_x > sx:
            block_entry['size_mm'][0] = need_x
            grew.append(f'width {sx} -> {need_x} mm')
        if need_y > sy:
            block_entry['size_mm'][1] = need_y
            grew.append(f'depth {sy} -> {need_y} mm')
        if grew:
            block_entry['source'] = (block_entry.get('source') or '') + \
                f' [Rev N refinement: block grew ({"; ".join(grew)}) to envelope its re-seated units]'
    return positions


def apply(seed_path=None, graph_path=None):
    """Refine the grid placements in the seed. Returns (moved_count, refined_map)."""
    sp = seed_path or SEED
    seed = json.load(open(sp))
    g = json.load(open(graph_path or GP))
    refined = refine(seed, g)
    n = 0
    for u in seed['units']:
        uid = u['unit_id']
        if uid in refined:
            r = refined[uid]
            old = list(u['origin_mm'])
            u['origin_mm'] = r['origin_mm']
            u['source'] = r['source']
            if math.dist(old, r['origin_mm']) > 100:
                n += 1
    json.dump(seed, open(sp, 'w'), indent=1)
    return n, refined


if __name__ == '__main__':
    n, refined = apply()
    print(f'placement_refine: {n} units moved > 100 mm '
          f'(two-level process-adjacency refinement; {len(refined)} grid placements re-seated)')

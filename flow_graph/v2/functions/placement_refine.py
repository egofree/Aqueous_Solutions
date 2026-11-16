"""The placement refinement family (family migration; reference writer
flow_graph/param/placement_refine.py, ledger row `placement_refine`, section
F, PHYSICS - the layout solver, migrate-as-function).

X-PIP-03 Rev O: the Rev N grid placements re-seated by process adjacency - the
Rev N blocks (identified by 'Rev N' in the block's own source note) seated by
weighted mass-edge adjacency around the pinned constellation (blocks without
the Rev N marker are PINNED: designed-placement citations), heaviest block
first, each taking the collision-free position that minimises the weighted
distance to its neighbour blocks; then each unit carrying a 'grid placement'
source greedily seated in the free slot minimising (a) the total distance to
its already-seated intra-block neighbours - the BFS from the block's source
units (no in-edges from within the block) through the mass edges sets the
priority - plus (b) the distance to the nearest point of each cross-block
neighbour's rectangle. Layout rules: rows grow left-to-right and stack
downward, 800 mm maintenance clearance between footprints, 3 m fire lane
between blocks, 500 mm wall keep-out, designed units are seat obstacles, and a
block whose re-seated units do not fit its declared rectangle grows and
records the growth in its source note.

This module ports the pure kernels (block_assignments, seat_blocks,
apply_block_deltas, refine, seat_units) exactly; the writer half (the v1
apply(), which json-dumps the seed file) stays outside - file writing is the
declared I/O boundary of engine v2, and the seed is a hybrid hand+generated
file that later stages amend.

Golden (test_placement_refine.py): the committed flow_graph/placement_seed.json
is the run's own output at the idempotence fixpoint - every Rev N block and
every re-seated unit carries the run's source stamps, so refine() over the
committed seed is a no-op and the seed bytes are unchanged (golden 1). The
solver's behaviour beyond the fixpoint is proven by reference equivalence:
this port and flow_graph.param.placement_refine return identical refined maps
and identical mutated seeds on the committed seed and on deterministic
un-stamped variants of it (golden 2) - the reference implementation is the
oracle. Plus the layout validity invariants (re-seated units inside their
grown blocks; no footprint overlaps at the clearance) and determinism. The
first-run reconstruction (the pre-Rev-O seed) is not reconstructable from the
committed tree - the run's stamps overwrote the predecessor source texts - so
no first-move golden exists; recorded as the row's deviation.

Float doctrine: the seating score is a float-replica chain (math.dist/hypot
weighted sums) over integer grid coordinates; the boundary bias 0.05 enters
as the decimal string of the v1 literal. No float literals (the lint holds
this). Pure: no I/O, no wall-clock, no RNG.
"""
import math
from collections import defaultdict, deque

CLEAR = 800           # maintenance clearance between unit footprints, mm
MARGIN = 500          # block wall keep-out, mm
FIRE_LANE = 3000      # clearance between blocks, mm
Z_DATUM = {'L0': 0, 'L-1': -6000, 'L-2': -16468, 'L1': 6000, 'L2': 10800, 'ROOF': 34800}


def block_assignments(seed):
    """unit_id -> block_id from the seed's block definitions."""
    blk = {}
    for b in seed['blocks']:
        for u in b.get('unit_ids', []):
            blk[u] = b['block_id']
    return blk


def _footprint(entry):
    sz = entry.get('size_mm') or [1500, 1000]
    w = float(sz[0]) if len(sz) > 0 and isinstance(sz[0], (int, float)) else float('1500')
    d = float(sz[1]) if len(sz) > 1 and isinstance(sz[1], (int, float)) else float('1000')
    return w, d


def _rects_overlap(a, b, gap=0):
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
            if 'X-PIP-03 refinement' in (b.get('source') or ''):
                deltas[bid] = (0, 0)                 # already seated: idempotence stamp
                seated[bid] = rect_of(bid)
                continue
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
            b['source'] = (b.get('source') or '') + \
                ' [X-PIP-03 refinement: seated by weighted adjacency]'
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
    """Refine block positions and grid placements. Returns {unit_id: new_entry_data}.
    Mutates the seed in place (the v1 contract: block sources gain their stamps,
    blocks grow their size_mm); the caller owns the seed copy."""
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
            s = abs(y - (oy + sy / 2))               # neutral: middle band
        for bid, wt in (cross_edges.get(u) or {}).items():
            if bid in nbr_rects:
                px, py = _nearest_point(nbr_rects[bid], x, y)
                s += wt * math.hypot(x - px, y - py) * float('0.05')   # gentle boundary bias
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
        centres[u] = (x + w / 2, y + d / 2)
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

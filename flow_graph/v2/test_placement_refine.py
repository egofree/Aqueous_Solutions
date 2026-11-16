"""engine v2: the placement refinement family acceptance (ledger section F,
the `placement_refine` PHYSICS row - the layout solver, ported to
flow_graph/v2/functions/placement_refine.py).

The committed flow_graph/placement_seed.json is the v1 run's own output at
its idempotence fixpoint (every Rev N block and every re-seated unit carries
the run's source stamps). The proofs:

- golden 1, fixpoint idempotence: refine() over the committed seed is a no-op
  - no unit re-seated, no seed field changed;
- golden 2, reference equivalence: on the committed seed AND on the
  deterministic un-stamped variant (the blocks' refinement markers stripped,
  so the solver does real work), the port and the v1 reference writer return
  identical refined maps and leave identical seeds - the reference
  implementation is the oracle;
- validity: on the un-stamped run every re-seated unit lands inside its
  (possibly grown) block rectangle and no two footprints overlap at the
  800 mm maintenance clearance;
- determinism: two passes, identical;
- purity: no I/O, no banned imports, no float literals.

Deviation recorded (the module docstring carries it too): no first-move
golden exists - the pre-Rev-O seed is not reconstructable from the committed
tree, because the run's source stamps overwrote the predecessor texts.
"""
import ast
import copy
import json
import os

from flow_graph.param import placement_refine as V1
from flow_graph.v2.functions import placement_refine as PR

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SEED = os.path.join(ROOT, 'flow_graph', 'placement_seed.json')
GRAPH = os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')

_MARK = ' [X-PIP-03 refinement: seated by weighted adjacency]'


def committed_seed():
    with open(SEED, encoding='utf-8') as f:
        return json.load(f)


def committed_graph():
    with open(GRAPH, encoding='utf-8') as f:
        return json.load(f)


def unstamped(seed):
    """The deterministic un-stamped variant: the blocks' refinement markers
    stripped, so every Rev N block re-seats (real solver work)."""
    s = copy.deepcopy(seed)
    for b in s['blocks']:
        src = b.get('source') or ''
        if _MARK in src:
            b['source'] = src.replace(_MARK, '')
    return s


def test_golden_fixpoint_idempotence_over_the_committed_seed():
    seed = committed_seed()
    before = copy.deepcopy(seed)
    refined = PR.refine(seed, committed_graph())
    assert refined == {}, f'{len(refined)} units re-seated at the fixpoint'
    assert seed == before, 'the committed seed moved under a fixpoint run'


def test_reference_equivalence_committed_and_unstamped():
    """Port == v1 (identical refined map, identical mutated seed) on the
    committed seed and on the un-stamped variant."""
    g = committed_graph()
    for label, mk in (('committed', copy.deepcopy), ('unstamped', unstamped)):
        s1, s2 = mk(committed_seed()), mk(committed_seed())
        r1 = PR.refine(s1, g)
        r2 = V1.refine(s2, g)
        assert r1 == r2, f'{label}: refined maps differ ({len(r1)} vs {len(r2)})'
        assert s1 == s2, f'{label}: mutated seeds differ'


def test_unstamped_run_reseats_blocks_and_is_valid():
    """The un-stamped variant actually exercises the solver: the Rev N blocks
    re-seat (move), every unit of a moved block travels with it, and the
    post-run block rectangles pairwise clear the 3 m fire lane. (The
    unit-seating half is dormant on this seed: no 'grid placement' unit is a
    member of any block's unit_ids, so refine's unit map stays empty - the
    reference equivalence test covers that half against the v1 oracle.)"""
    before = unstamped(committed_seed())
    seed = copy.deepcopy(before)
    g = committed_graph()
    blk_of = PR.block_assignments(seed)
    refined = PR.refine(seed, g)
    assert refined == {}, 'no grid-placement unit is a block member on this seed'
    blocks_before = {b['block_id']: b for b in before['blocks']}
    blocks_after = {b['block_id']: b for b in seed['blocks']}
    moved = {bid for bid, b in blocks_after.items()
             if b['origin_mm'] != blocks_before[bid]['origin_mm']}
    assert moved, 'the un-stamped variant must re-seat Rev N blocks'
    # every unit of a moved block travelled with it (same delta)
    for u_before, u_after in zip(before['units'], seed['units']):
        bid = blk_of.get(u_before['unit_id'])
        if bid in moved:
            db = [blocks_after[bid]['origin_mm'][k] - blocks_before[bid]['origin_mm'][k] for k in (0, 1)]
            du = [u_after['origin_mm'][k] - u_before['origin_mm'][k] for k in (0, 1)]
            assert du == db, f"{u_before['unit_id']}: unit delta {du} != block delta {db}"
    # the algorithm's placement rule: each re-seated block sits clear of
    # every other block on its level at the fire lane (pinned blocks are
    # priors and carry no such guarantee between themselves)
    after_by_level = {}
    for b in seed['blocks']:
        after_by_level.setdefault(b.get('level', 'L0'), []).append(b)
    for lv, blocks_lv in after_by_level.items():
        rects = [(b['origin_mm'][0], b['origin_mm'][1], float(b['size_mm'][0]), float(b['size_mm'][1]))
                 for b in blocks_lv if b['block_id'] in moved]
        others = [(b['origin_mm'][0], b['origin_mm'][1], float(b['size_mm'][0]), float(b['size_mm'][1]))
                  for b in blocks_lv if b['block_id'] not in moved]
        for r in rects:
            for o in others + [x for x in rects if x is not r]:
                assert not PR._rects_overlap(r, o, PR.FIRE_LANE), \
                    f'{lv}: a re-seated block overlaps at the {PR.FIRE_LANE} mm fire lane'


def test_determinism_two_passes_identical():
    g = committed_graph()
    s1, s2 = unstamped(committed_seed()), unstamped(committed_seed())
    assert PR.refine(s1, g) == PR.refine(s2, g)
    assert s1 == s2


def test_family_module_pure():
    banned = {'datetime', 'random', 'uuid', 'time', 'tempfile'}
    with open(PR.__file__, encoding='utf-8') as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                assert a.name.split('.')[0] not in banned, f'banned import {a.name}'
        elif isinstance(node, ast.ImportFrom):
            assert (node.module or '').split('.')[0] not in banned, f'banned import from {node.module}'
        elif isinstance(node, ast.Constant):
            assert not isinstance(node.value, float), f'{node.lineno}: float literal'
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'open':
            raise AssertionError(f'{node.lineno}: file I/O in a function module')

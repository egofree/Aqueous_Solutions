"""engine v2: the foundry-family acceptance (the golden-value proof).

Reference writer: flow_graph/param/foundry_poly.py (+ its salt_recovery.py TF
call), ledger row `foundry_poly`, section C, MIXED - split solve -> function,
topology -> composer. The committed graph carries every field the family
stamps; the proofs:

- exact change set: the family's overlay equals the hand-enumerated
  specification, and a strict whole-model walk proves nothing else moved
  (the fluoro-owned F-block, the solvent streams, the balance-owned IA-C5-SHIP
  note and the composer-owned topology stay byte-faithful);
- golden equality: every changed field equals the committed golden, numbers
  exact at the golden's decimals - except the five rates the balance family
  re-reconciles after this stage every pass (AQS-PAR-003) and one si_route
  remap residue: each delta asserted exactly, with its owner;
- grid spot-checks on the integer books: the aluminium line's
  chlorinator/hydroxide chain (X-QA-19), the Kroll Mg book (AQS-BAL-KROLL),
  the brine crystallizer's 2.0 kg/d draw split (A-M-503) and the melt-shop
  stock ledger closure;
- determinism: two runs, byte-identical; the no-drivers bridge contract
  records nothing; grid purity: no float literals, no I/O in the module.
"""
import ast
import inspect
import json
import os
from decimal import Decimal

from flow_graph.v2.functions import foundry as FD
from flow_graph.v2.graph_io import bytes as render, load

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF_GRAPH = os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')
DRIVERS = os.path.join(ROOT, 'flow_graph', 'param', 'drivers.json')
INPUTS = {'drivers': json.load(open(DRIVERS))}

# ---- the change-set specification (hand-enumerated) ------------------------
SIZING_NODES = ['IND_MELT', 'CAST_LINE', 'CONT_CAST', 'ROLL', 'STOCK_OUT', 'AL_POT', 'MG_POT',
                'CA_POT', 'TI_CELL', 'MO_CELL', 'CR_CELL', 'FLUX_PREP', 'WAX_PATTERN', 'SHELL_BUILD',
                'SHELL_BURNOUT', 'INV_CAST', 'SHELL_BREAK', 'VAC_IND', 'VAC_CAST', 'RF_HEAT',
                'RES_HEAT', 'COMB_HEAT', 'SINTER', 'FORGE', 'EXTRUDE', 'DRAW', 'POLY_OLEFIN',
                'PELLET', 'POLY_COND']
DESIGN_NODES = ['IND_MELT', 'CAST_LINE', 'CONT_CAST', 'ROLL', 'STOCK_OUT', 'TI_CELL', 'WAX_PATTERN',
                'SHELL_BUILD', 'SHELL_BURNOUT', 'INV_CAST', 'SHELL_BREAK', 'FLUX_PREP', 'VAC_IND',
                'VAC_CAST', 'RF_HEAT', 'RES_HEAT', 'COMB_HEAT', 'SINTER', 'FORGE', 'EXTRUDE',
                'DRAW', 'POLY_OLEFIN', 'PELLET', 'POLY_STOCK']
POTS = ['AL_POT', 'MG_POT', 'CA_POT', 'MO_CELL', 'CR_CELL']
POT_DESIGN_KEYS = {'AL_POT': ['service', 'chemistry', 'feed_kg_d', 'metal_kg_d', 'cl2_kg_d', 'I_A',
                              'cell_V', 'dc_kW', 'hold_kW', 'connected_kW', 'bath_T_C', 'anode_D_mm',
                              'anode_imm_mm', 'cathodes', 'busbar_mm2'],
                   'MG_POT': ['service', 'chemistry', 'feed_kg_d', 'metal_kg_d', 'cl2_kg_d', 'I_A',
                              'cell_V', 'dc_kW', 'hold_kW', 'connected_kW', 'bath_T_C', 'anode_D_mm',
                              'anode_imm_mm', 'cathodes', 'busbar_mm2'],
                   'CA_POT': ['service', 'chemistry', 'feed_kg_d', 'metal_kg_d', 'cl2_kg_d', 'I_A',
                              'cell_V', 'dc_kW', 'hold_kW', 'connected_kW', 'bath_T_C', 'anode_D_mm',
                              'anode_imm_mm', 'cathodes', 'busbar_mm2'],
                   'MO_CELL': ['service', 'chemistry', 'feed_kg_d', 'metal_kg_d', 'co2_kg_d', 'I_A',
                               'cell_V', 'dc_kW', 'hold_kW', 'connected_kW', 'bath_T_C', 'anode_D_mm',
                               'anode_imm_mm', 'cathodes', 'busbar_mm2'],
                   'CR_CELL': ['service', 'chemistry', 'feed_kg_d', 'metal_kg_d', 'co_kg_d', 'I_A',
                               'cell_V', 'dc_kW', 'hold_kW', 'connected_kW', 'bath_T_C', 'anode_D_mm',
                               'anode_imm_mm', 'cathodes', 'busbar_mm2']}
KW_NODES = ['AL_POT', 'MG_POT', 'CA_POT', 'TI_CELL', 'MO_CELL', 'CR_CELL', 'FLUX_PREP',
            'WAX_PATTERN', 'SHELL_BUILD', 'SHELL_BURNOUT', 'INV_CAST', 'SHELL_BREAK', 'VAC_CAST',
            'RES_HEAT', 'SINTER', 'FORGE', 'EXTRUDE', 'DRAW', 'COMB_HEAT', 'BRINE_CRYS']
RATE_EDGES = [
    # the scrap-remelt melt loop
    'MFG_SCRAP_TO_IND', 'FOUNDRY_SLAG_TO_LEACH', 'IND_MELT_TO_CAST', 'IND_TO_CONT',
    'CAST_SCRAP_TO_IND', 'CAST_TO_ROLL', 'CAST_TO_EXTRUDE', 'CONT_TO_ROLL', 'CONT_TO_STOCK',
    'ROLL_TO_STOCK', 'STOCK_TO_MFG', 'STOCK_TO_WIRE_DRAW', 'EXTRUDE_TO_STOCK', 'DRAW_TO_STOCK',
    'SINTER_TO_STOCK', 'ATOM_TO_STOCK', 'IND_TO_ATOM',
    # the recovery-sized aluminium line (X-QA-19)
    'IA-ALCL3-MU', 'IA-AL-CAKE', 'CHAR_TO_AL', 'IA-AL-CO', 'IA-AL-H2O', 'AL_POT_TO_IND',
    'IA-CL2-SHIP',
    # the Mg/Ca pot feeds and the Kroll book
    'IA-MGCL2-KROLL', 'IA-KROLL-FLUX', 'IA-MGCL2-MU', 'IA-MG-TI', 'IA-CL2-MG-TI',
    'MG_POT_TO_IND', 'MG_POT_CL2', 'IA-CACL2-MU', 'CA_POT_TO_IND', 'IA-CA-CL2-SHIP',
    # the on-site brine recovery (A-M-503)
    'IA-BRINE-SRC', 'IA-BRINE-CACL2', 'IA-BRINE-MGCL2', 'IA-BRINE-ML', 'SF-BRINE_CRYS',
    # the Kroll / Mo / Cr carbochlorination cells (IA-KROLL-CO is not stamped:
    # the solvent family re-rates it with its CO draw, A-M-479)
    'IA-TIO2-MU', 'CHAR_TO_TI', 'IA-C-TI', 'METALS_TO_IND_MELT', 'TI_CELL_SLAG_RETURN',
    'TI_CELL_CL2_TO_CRU', 'VAC_IND_TI', 'VAC_IND_TO_VAC_CAST', 'IA-MOO3-MU',
    'CHAR_TO_MO', 'IA-C-MO', 'MO_TO_IND', 'MO_CELL_RAFFINATE', 'MO_CELL_ANODE_GAS_TO_CRU',
    'EW9_LIQUOR_TO_MO', 'EW_METALS_TO_IND', 'IA-MO-VENT', 'IA-CR2O3-MU', 'CHAR_TO_CR',
    'IA-C-CR', 'CR_TO_IND', 'FLOAT_SINK_GRIT_TO_TI', 'IA-CR-VENT',
    # the investment train (A-M-286/498) and the sink-circuit cake transfer
    'IA-WAX-MU', 'IA-WAX-CUT', 'IA-SILICA-MU', 'IA-SIL-SHOP', 'WAX_TO_SHELL', 'SHELL_TO_BURNOUT',
    'WAX_RECLAIM_TO_PATTERN', 'WAX_TO_OIL', 'IA-BURNOUT-VENT', 'BURNOUT_TO_CAST', 'IND_TO_INV',
    'VAC_TO_INV', 'INV_TO_BREAK', 'BREAK_TO_STOCK', 'IA-SHELL-RECLAIM', 'IA-SHELL-SHOP',
    'IA-SHELL-EXPORT', 'IA-SINK-01', 'IA-WET-FLOAT-01', 'SHELL_TO_GLASS', 'COMB_OFFGAS',
    'FLUX_TO_IND', 'SALT_TO_FLUX',
    # the polyolefin line and the dock statements
    'OIL_TO_OLEFIN', 'MEOH_TO_OLEFIN', 'OLEFIN_TO_PELLET', 'PELLET_TO_STOCK', 'POLY_TO_MFG',
    'POLY_TO_WET', 'DIGEST_TO_POLY', 'IA-C5-POLY',
    'IA-C5-SHIP', 'IA-METAL-SHIP', 'DOCK_EXPORT_TBD',
    # the crew textile line (A-M-429/502) and the retired finish
    'STOCK_TO_FIBER', 'IA-FR-P', 'IA-FR-NH3', 'FIBER_SCRAP', 'FLEECE_TO_MFG', 'TEXTILE_HAB',
    'S34B', 'FR_FINISH',
    # the SF electrical feeds
    'SF-AL_POT', 'SF-MG_POT', 'SF-CA_POT', 'SF-TI_CELL', 'SF-MO_CELL', 'SF-CR_CELL',
]
EXPECTED_FIELDS = (
    [(uid, 'params.sizing') for uid in SIZING_NODES]
    + [(uid, 'params.design') for uid in DESIGN_NODES]
    + [(uid, 'params.envelope') for uid in DESIGN_NODES]
    + [(uid, 'params.envelope') for uid in POTS]
    + [(uid, 'params.design.' + k) for uid in POTS for k in sorted(POT_DESIGN_KEYS[uid])]
    + [('BRINE_CRYS', 'params.design')]
    + [(uid, 'continuous_kw') for uid in KW_NODES]
    + [(uid, 'params.recovery') for uid in ('SHELL_BUILD', 'TI_CELL', 'MO_CELL', 'CR_CELL', 'HOPPER')]
)
EXPECTED_EDGE_FIELDS = [('IA-CL2-SHIP', 'params.base_kg_d'), ('IA-CL2-SHIP', 'params.al_chlor_cl2_kg_d'),
                        ('IA-CA-CL2-SHIP', 'params.si_cl2_kg_d'), ('IA-WAX-CUT', 'composition'),
                        ('IA-SHELL-EXPORT', 'composition')]

# Downstream families re-solve these five rates after this stage every pass;
# the committed tree carries their residue. Owners: the balance family
# (AQS-PAR-003) re-reconciles the three brine-loop rates; the fluoro
# photoresist netting (A-M-482, 0.001824 kg/d to RESIST_SYN) re-rates
# IA-CA-CL2-SHIP, after si_refine's make-up netting (A-M-484); the solvent
# family (A-M-479) re-rates IA-KROLL-CO with its CO draw. This family stamps
# the exact design book (the closing values the consumers need); each delta
# is asserted exactly, in kg/d, with its owner.
DEVIATIONS = {
    ('IA-BRINE-SRC', 'rate.value'): (2.000047, 2.0),
    ('IA-BRINE-CACL2', 'rate.value'): (0.116201, 0.116115),
    ('IA-BRINE-ML', 'rate.value'): (1.844063, 1.844103),
    ('IA-CA-CL2-SHIP', 'rate.value'): (0.063248, 0.065072),
}
# the balance family re-reconciles these four after this stage; the solvent
# family (A-M-479) owns IA-KROLL-CO and the IA-SOLV-* streams outright
NOT_STAMPED = ('IA-KROLL-CO',) + tuple(k for k, _v in DEVIATIONS)

# ---- topology mutation inventory (the composer lane's work; the seed proof) -
# Every graph-structure mutation the v1 --write pass performs, with its
# condition. The composer lane's module is landed (flow_graph/v2/functions/
# topology.py, imported FIRST in solve.py - the shape precedes the values; the
# both-directions proof is flow_graph/v2/test_topology.py). The committed seed
# already carries all of it; the asserts pin it.
TOPOLOGY_INVENTORY = {
    'created_edges': {
        'IA-ALCL3-MU': ('NORTH_DOCK', 'AL_POT'), 'IA-AL-CAKE': ('LEACH_CSTR_1', 'AL_POT'),
        'CHAR_TO_AL': ('OIL_PYRO', 'AL_POT'), 'IA-AL-CO': ('AL_POT', 'NORTH_DOCK'),
        'IA-AL-H2O': ('AL_POT', 'ATMOS'), 'IA-MGCL2-KROLL': ('TI_CELL', 'MG_POT'),
        'IA-KROLL-FLUX': ('TI_CELL', 'FLUX_PREP'), 'IA-MGCL2-MU': ('NORTH_DOCK', 'MG_POT'),
        'IA-MG-TI': ('MG_POT', 'TI_CELL'), 'IA-CL2-MG-TI': ('MG_POT', 'TI_CELL'),
        'IA-CACL2-MU': ('NORTH_DOCK', 'CA_POT'), 'IA-CA-CL2-SHIP': ('CA_POT', 'NORTH_DOCK'),
        'IA-TIO2-MU': ('NORTH_DOCK', 'TI_CELL'), 'CHAR_TO_TI': ('OIL_PYRO', 'TI_CELL'),
        'IA-KROLL-CO': ('TI_CELL', 'NORTH_DOCK'),      # re-rated by the solvent family (A-M-479)
        'IA-MOO3-MU': ('NORTH_DOCK', 'MO_CELL'), 'CHAR_TO_MO': ('OIL_PYRO', 'MO_CELL'),
        'IA-MO-VENT': ('MO_CELL', 'NORTH_DOCK'), 'IA-CR2O3-MU': ('NORTH_DOCK', 'CR_CELL'),
        'CHAR_TO_CR': ('OIL_PYRO', 'CR_CELL'), 'IA-CR-VENT': ('CR_CELL', 'NORTH_DOCK'),
        'IA-WAX-MU': ('NORTH_DOCK', 'WAX_PATTERN'), 'IA-WAX-CUT': ('PROD_C19_C28', 'WAX_PATTERN'),
        'IA-SILICA-MU': ('NORTH_DOCK', 'SHELL_BUILD'), 'IA-SIL-SHOP': ('MFG_SHOP', 'SHELL_BUILD'),
        'IA-BURNOUT-VENT': ('SHELL_BURNOUT', 'NORTH_DOCK'),
        'IA-SHELL-RECLAIM': ('SHELL_BREAK', 'SHELL_BUILD'), 'IA-SHELL-SHOP': ('SHELL_BREAK', 'MFG_SHOP'),
        'IA-SHELL-EXPORT': ('SHELL_BREAK', 'NORTH_DOCK'),
        'IA-C5-POLY': ('PROD_C5_C10', 'POLY_OLEFIN'), 'IA-METAL-SHIP': ('METAL_STORE', 'NORTH_DOCK'),
        'SF-AL_POT': ('SOL_ARK_60K', 'AL_POT'), 'SF-MG_POT': ('SOL_ARK_60K', 'MG_POT'),
        'SF-CA_POT': ('SOL_ARK_60K', 'CA_POT'), 'SF-TI_CELL': ('SOL_ARK_60K', 'TI_CELL'),
        'SF-MO_CELL': ('SOL_ARK_60K', 'MO_CELL'), 'SF-CR_CELL': ('SOL_ARK_60K', 'CR_CELL'),
    },
    'created_by_salt_recovery': {
        'IA-BRINE-SRC': ('LEACH_CSTR_1', 'BRINE_CRYS'), 'IA-BRINE-CACL2': ('BRINE_CRYS', 'CA_POT'),
        'IA-BRINE-MGCL2': ('BRINE_CRYS', 'MG_POT'), 'IA-BRINE-ML': ('BRINE_CRYS', 'LEACH_CSTR_1'),
        'SF-BRINE_CRYS': ('SOL_ARK_60K', 'BRINE_CRYS'),
    },
    'created_nodes': ['BRINE_CRYS'],
    'created_edge_conditional': {'STOCK_TO_FIBER': ('POLY_STOCK', 'POLY_FIBER'),
                                 'IA-FR-P': ('WS_PHOS', 'POLY_FIBER'),
                                 'IA-FR-NH3': ('WS_AMMONIA', 'POLY_FIBER'),
                                 'FIBER_SCRAP': ('POLY_FIBER', 'LEACH_CSTR_1'),
                                 'FLEECE_TO_MFG': ('POLY_FIBER', 'MFG_SHOP'),
                                 'TEXTILE_HAB': ('MFG_SHOP', 'HABITATION')},
    'retired_edges': ['IA-ALCL3-MU', 'IA-CL2-SHIP', 'IA-MGCL2-MU', 'IA-CACL2-MU', 'IA-WAX-MU',
                      'IA-SILICA-MU', 'IA-SHELL-EXPORT', 'IA-C-TI', 'IA-C-MO', 'IA-C-CR',
                      'FR_FINISH'],
    'retired_by_salt_recovery': ['IA-CACL2-MU', 'IA-MGCL2-MU'],   # a second retirement on the same edges
    'deleted_edges': ['IA-CA-TO-PCA'],
    'repointed': {'IA-WAX-CUT': 'from_sector_id -> OIL'},
    'gaps_entry': 'FOUNDRY_POLY_MISSING_EDGES (replaced in place)',
    # param-side mutations: field seeds this family's compute reads back (the
    # first run creates them; the baseline seed carries them - pinned in
    # test_topo_composer_lane_inventory)
    'seeded_edge_params': {
        'IA-CL2-SHIP.params.base_kg_d': 0.0,
        'IA-CL2-SHIP.params.al_chlor_cl2_kg_d': 'the on-site chlorination draw (A-M-495)',
        'IA-CA-CL2-SHIP.params.si_cl2_kg_d': 'the silicon-loop make-up book (A-M-472, A-M-484)',
        'IA-SINK-01.params.pre_al_cake_kg_d': 'seeded once from the rate, if al_cake > 0 (F-20261110-07)',
        'IA-WET-FLOAT-01.params.pre_al_cake_kg_d': 'seeded once from the rate, if al_cake > 0 (F-20261110-07)',
        'S34B.params.pre_fr_kg_d': 'seeded once from the rate, textile line live (A-M-502)',
    },
    # everything else the v1 pass mutates that is neither edge creation nor a
    # rate/kw/design stamp: the composer lane's residue classes
    'other_mutations': (
        'IA-CL2-SHIP.params.si_cl2_kg_d popped (the netting moved to IA-CA-CL2-SHIP, A-M-484)',
        'dock_class + dock_pending_task popped on the retired imports IA-MGCL2-MU / IA-CACL2-MU / IA-WAX-MU and FR_FINISH',
        'carries rewritten on the retired imports (X-QA-11 / F-20261110-06 / F-20261110-07 wording)',
        'brine STREAMS composition + carries re-stamped every pass; SF-BRINE_CRYS header = tray; BRINE_CRYS class = precip',
        'created edges copy templates: IA-SOLV-MU (mass layer), IA-C5-SHIP, IA-O2-SHIP, SF-HF_GEN (kw), '
        'STOCK_TO_FIBER else PELLET_TO_STOCK (textile); IA-CA-CL2-SHIP carries layers=[mass, energy]; '
        'IA-C5-POLY sets open_boundary=False on creation',
        'SF-HF_GEN rate + HF_GEN continuous_kw conditionally re-rated to 0 (re-owned by fluoro_train)',
        "DOCK_EXPORT_TBD note re-TAGged in place (idempotent)",
        'solve() seeds IA-GOODS-SHIP in memory and restores it (closed-shop read; never persisted)',
    ),
}


def run():
    b = load(REF_GRAPH)
    FD.foundry_poly(b, INPUTS)
    return b


def _committed():
    with open(REF_GRAPH, encoding='utf-8') as f:
        return json.load(f)


def _num_eq(gold, got):
    return Decimal(str(gold)).normalize() == Decimal(str(got)).normalize()


def _eq(gold, got):
    if isinstance(gold, dict):
        return isinstance(got, dict) and set(gold) == set(got) and all(_eq(v, got[k]) for k, v in gold.items())
    if isinstance(gold, list):
        return isinstance(got, list) and len(gold) == len(got) and all(_eq(a, b) for a, b in zip(gold, got))
    if isinstance(gold, (int, float)) and not isinstance(gold, bool):
        return isinstance(got, (int, float)) and not isinstance(got, bool) and _num_eq(gold, got)
    return gold == got


def _dig(obj, path):
    cur = obj
    for part in path.split('.'):
        cur = cur[part]
    return cur


def _strict_diffs(c_obj, r_obj, prefix, out, expected, deltas):
    """Paths where the rendered model differs from the committed graph beyond
    the expected change set: strict (same JSON types) everywhere except the
    enumerated fields (numeric equality at the golden's decimals) and the
    documented deviation pairs. Provenance rows are excluded."""
    for k in sorted((set(c_obj) | set(r_obj)) - {'provenance'}):
        p = prefix + '.' + k if prefix else k
        if k not in c_obj or k not in r_obj:
            out.add(p)
        elif p in deltas:
            if (c_obj[k], r_obj[k]) != deltas[p]:
                out.add(p + ' (deviation pair moved)')
        elif p in expected:
            if not _eq(c_obj[k], r_obj[k]):
                out.add(p)
        elif isinstance(c_obj[k], dict) and isinstance(r_obj[k], dict):
            _strict_diffs(c_obj[k], r_obj[k], p, out, expected, deltas)
        elif isinstance(c_obj[k], list) and isinstance(r_obj[k], list) and len(c_obj[k]) == len(r_obj[k]):
            if any(type(a) is not type(b) or a != b for a, b in zip(c_obj[k], r_obj[k])):
                out.add(p)
        elif type(c_obj[k]) is not type(r_obj[k]) or c_obj[k] != r_obj[k]:
            out.add(p)


def test_exact_change_set_and_golden_equality():
    committed = _committed()
    c_nodes = {n['unit_id']: n for n in committed['nodes']}
    c_edges = {e['stream_id']: e for e in committed['edges']}
    b = run()
    out = json.loads(render(b))
    r_nodes = {n['unit_id']: n for n in out['nodes']}
    r_edges = {e['stream_id']: e for e in out['edges']}

    got_nodes = sorted((uid, path) for (kind, uid, path) in b.computed if kind == 'node')
    got_edges = sorted((sid, path) for (kind, sid, path) in b.computed if kind == 'edge')
    assert got_nodes == sorted(EXPECTED_FIELDS), (
        sorted(set(got_nodes) - set(EXPECTED_FIELDS)), sorted(set(EXPECTED_FIELDS) - set(got_nodes)))
    expected_edges = sorted([(sid, 'rate') for sid in RATE_EDGES] + EXPECTED_EDGE_FIELDS)
    assert got_edges == expected_edges, (
        sorted(set(got_edges) - set(expected_edges)),
        sorted(set(expected_edges) - set(got_edges)))

    for uid, path in EXPECTED_FIELDS:
        assert _eq(_dig(c_nodes[uid], path), _dig(r_nodes[uid], path)), (uid, path)
    for sid, path in expected_edges:
        if any(sid == d_sid for d_sid, _p in DEVIATIONS):
            continue                     # the reconciled residues: asserted below
        assert _eq(_dig(c_edges[sid], path), _dig(r_edges[sid], path)), (sid, path)

    # nothing else moves: a strict walk of every node and edge finds no drift
    # beyond the enumerated fields and the five documented deviations
    dev_sids = {sid for sid, _p in DEVIATIONS}
    expected_node_paths = {uid + '.' + path for uid, path in EXPECTED_FIELDS}
    diffs = set()
    for uid in sorted(set(c_nodes) | set(r_nodes)):
        _strict_diffs(c_nodes[uid], r_nodes[uid], uid, diffs, expected_node_paths, {})
    assert diffs == set(), sorted(diffs)
    expected_edge_paths = {sid + '.' + path for sid, path in expected_edges if sid not in dev_sids}
    edge_deltas = {sid + '.' + path: pair for (sid, path), pair in DEVIATIONS.items()}
    edge_diffs = set()
    for sid in sorted(set(c_edges) | set(r_edges)):
        _strict_diffs(c_edges[sid], r_edges[sid], sid, edge_diffs, expected_edge_paths, edge_deltas)
    assert edge_diffs == set(), sorted(edge_diffs)


def test_deviation_owners():
    """The five reconciled deltas, each exactly, with the downstream owner."""
    committed = _committed()
    c_edges = {e['stream_id']: e for e in committed['edges']}
    b = run()
    got = {sid: b.computed[('edge', sid, 'rate')][0]['value'] for (sid, _p) in DEVIATIONS}
    assert got == {sid: pair[1] for (sid, _p), pair in DEVIATIONS.items()}
    for (sid, path), (gold, _got) in DEVIATIONS.items():
        assert c_edges[sid]['rate']['value'] == gold, (sid, 'committed residue moved')


def test_brine_crystallizer_book():
    """A-M-503: the 2.0 kg/d draw splits exactly into 0.116115 CaCl2 +
    0.039782 MgCl2 + 1.844103 mother liquor, on integer mg books."""
    s = FD._core(load(REF_GRAPH), INPUTS)
    assert s['brine_feed'] == 2
    assert s['cacl2_br'] == 116115 and s['mgcl2_br'] == 39782 and s['brine_ml'] == 1844103
    assert s['cacl2_br'] + s['mgcl2_br'] + s['brine_ml'] == 2000000
    # the Mg book closes on the retort stoichiometry: the make-up is exactly
    # the drag-out (gross less the returned salt)
    assert s['mgcl2_br'] == FD.book(s['mg_ti'], 6, '') + FD.book(s['cl2_ti'], 6, '') \
        - FD.book(s['mgcl2_ret'], 6, '')
    # the crystallizer node book and its feed edge carry the same split
    b = run()
    design = b.computed[('node', 'BRINE_CRYS', 'params.design')][0]
    assert design == {'cacl2_kg_d': 0.116115, 'mgcl2_kg_d': 0.039782, 'feed_kg_d': 2.0,
                      'ml_kg_d': 1.844103, 'kw': 0.07}
    assert b.computed[('edge', 'IA-BRINE-MGCL2', 'rate')][0]['value'] == 0.039782


def test_aluminium_line_chain():
    """X-QA-19 grid spot-checks: the recoverable-Al basis, the hydroxide
    cake, the carbochlorination chain and the retired make-up."""
    s = FD._core(load(REF_GRAPH), INPUTS)
    M = FD.MM
    assert s['al'] == FD.rat('4.1072') * 5 / 4 and s['al_rec'] == s['al']
    assert s['alcl3_mu'] == 0, 'the AlCl3 import is retired: the cake must cover the whole feed'
    assert s['al_cake'] == s['al_rec'] * (M['Al'] + 3 * (M['O'] + M['H'])) / M['Al']
    assert FD.book(s['al_cake'], 6, '') == 14842429          # 14.842429 kg/d, mg book
    assert FD.book(s['alcl3_rec'], 6, '') == 25371834
    assert FD.book(s['al_chlor_cl2'], 6, '') == 20237834
    assert FD.book(s['char_al'], 6, '') == 3428153
    assert FD.book(s['al_co'], 6, '') == 7994666
    assert FD.book(s['al_h2o'], 6, '') == 5141916
    # the chlorination chlorine equals the cell's byproduct per kg Al: the
    # pot closes exactly (A-M-290/X-QA-19)
    assert s['al_chlor_cl2'] == s['al_rec'] * 3 * M['Cl'] / M['Al']
    assert s['al_cl2'] == s['al'] * 3 * M['Cl'] / M['Al']
    b = run()
    assert b.computed[('edge', 'IA-AL-CAKE', 'rate')][0]['value'] == 14.842429
    assert b.computed[('edge', 'IA-CL2-SHIP', 'rate')][0]['value'] == 0.0
    assert b.computed[('edge', 'IA-CL2-SHIP', 'params.al_chlor_cl2_kg_d')][0] == s['al_chlor_f']


def test_kroll_mg_book():
    """The Ti cell book on integer mg counts (AQS-BAL-KROLL)."""
    s = FD._core(load(REF_GRAPH), INPUTS)
    M = FD.MM
    assert s['ti'] == FD.rat('0.4') * 5 / 4
    assert FD.book(s['tio2'], 6, '') == 834247
    assert FD.book(s['c_ti'], 6, '') == 250924
    assert FD.book(s['cl2_ti'], 6, '') == 1481313
    assert FD.book(s['mg_ti'], 6, '') == 507761
    assert FD.book(s['mgcl2_g'], 6, '') == 1989074
    assert FD.book(s['kroll_flux'], 6, '') == 39781
    assert FD.book(s['mgcl2_ret'], 6, '') == 1949292
    assert FD.book(s['co_ti'], 6, '') == 585171
    # the retort closes on the write grid: gross = returned salt + make-up
    # (each term at its own R6 rounding, exactly as salt_recovery.design books it)
    assert FD.book(s['mgcl2_ret'], 6, '') + s['mgcl2_br'] == FD.book(s['mgcl2_g'], 6, '')
    # the gross chlorinator CO books on the R6 grid to 0.585172; the solvent CO
    # draw (A-M-479) re-rates the edge afterwards - this family stamps none of it
    gross_co = (FD.book(s['tio2'], 6, '') + FD.book(s['c_ti'], 6, '') + FD.book(s['cl2_ti'], 6, '')
                + FD.book(s['mg_ti'], 6, '') - FD.book(s['ti'], 6, '')
                - FD.book(s['mgcl2_ret'], 6, '') - FD.book(s['kroll_flux'], 6, ''))
    assert gross_co == 585172 and gross_co - 126101 == 459071
    b = run()
    assert b.computed[('edge', 'METALS_TO_IND_MELT', 'rate')][0]['value'] == 0.5
    assert ('edge', 'IA-KROLL-CO', 'rate') not in b.computed


def test_melt_shop_ledger():
    """The melt-shop closure on exact books: S from the rounded P, the stock
    ledger, the melt mix and the class energies."""
    s = FD._core(load(REF_GRAPH), INPUTS)
    assert s['r0'] == FD.Fraction(Decimal('-0.016065'))
    assert s['K'] == FD.rat('22.0072') and s['f'] == FD.Fraction(1, 100)
    assert s['P'] == -s['r0'] + s['f'] * s['K'] / (1 - s['f'])
    assert s['sP'] == 238360 and s['sS'] == 22229495 and s['spotm'] == 5946500
    assert s['sca'] == 41931 and s['sflux'] == 39781 and s['sslag'] == 304007
    ind_to_cont = s['sS'] + s['spotm'] + s['sca'] + s['sflux'] - 5000000 - s['sslag']
    assert ind_to_cont == 22953700
    assert s['stock_in'] == s['K'] + s['potm']
    assert s['heats'] == 3 and s['kw_peak'] == 15
    assert FD.book(s['e_melt'], 3, '') == 15763
    assert FD.book(s['e_roll'], 4, '') == 4160
    assert sum(s['mix'].values()) == s['S_exact'] - s['P'] + s['potm']
    b = run()
    assert b.computed[('edge', 'MFG_SCRAP_TO_IND', 'rate')][0]['value'] == 22.229495
    assert b.computed[('edge', 'IND_TO_CONT', 'rate')][0]['value'] == 22.9537
    assert b.computed[('edge', 'CONT_TO_STOCK', 'rate')][0]['value'] == 12.9537
    assert b.computed[('edge', 'STOCK_TO_MFG', 'rate')][0]['value'] == 22.0072
    sizing = b.computed[('node', 'IND_MELT', 'params.sizing')][0]
    assert sizing['charge_kg_d'] == 28.2158 and sizing['heats_d'] == 3
    assert sizing['melt_kWh_d'] == 15.763 and sizing['peak_kW'] == 15.0


def test_pot_electrical_book():
    """The Faraday book at the writer's 96485 C/mol constant, 2/4-dp."""
    s = FD._core(load(REF_GRAPH), INPUTS)
    pe = s['pot_e']
    assert pe['AL_POT']['I_A'] == 749.96 and pe['AL_POT']['V'] == 3.8
    assert pe['AL_POT']['dc_kW'] == 2.8498 and pe['AL_POT']['hold_kW'] == 0.1069
    assert pe['AL_POT']['kW'] == 2.9567
    assert pe['MG_POT']['I_A'] == 54.89 and pe['MG_POT']['kW'] == 0.3375
    assert pe['CA_POT']['I_A'] == 2.75 and pe['CA_POT']['kW'] == 0.1184
    assert pe['MO_CELL']['kW'] == 0.1141 and pe['CR_CELL']['kW'] == 0.16
    assert pe['TI_CELL'] == {'I_A': 0.0, 'V': 0.0, 'dc_kW': 0.0, 'hold_kW': 0.5, 'kW': 0.5}


def test_topo_composer_lane_inventory():
    """The topology inventory is pinned against the committed seed: the
    composer lane's work exists, the function stamped none of it."""
    committed = _committed()
    c_edges = {e['stream_id']: e for e in committed['edges']}
    inv = TOPOLOGY_INVENTORY
    for sid, (a, zb) in inv['created_edges'].items():
        e = c_edges[sid]
        assert (e['from_unit_id'], e['to_unit_id']) == (a, zb), sid
    for sid, (a, zb) in inv['created_by_salt_recovery'].items():
        e = c_edges[sid]
        assert (e['from_unit_id'], e['to_unit_id']) == (a, zb), sid
    for uid in inv['created_nodes']:
        assert uid in {n['unit_id'] for n in committed['nodes']}, uid
    for sid in set(inv['retired_edges']):
        assert c_edges[sid].get('presence') == 'retired', sid
    for sid, (a, zb) in inv['created_edge_conditional'].items():
        e = c_edges[sid]
        assert (e['from_unit_id'], e['to_unit_id']) == (a, zb), sid
    for sid in inv['deleted_edges']:
        assert sid not in c_edges, sid
    assert c_edges['IA-WAX-CUT']['from_sector_id'] == 'OIL'
    # the param-side seeds the compute reads back (the composer lane creates
    # them on the first run; the baseline seed must carry them)
    assert c_edges['IA-SINK-01']['params']['pre_al_cake_kg_d'] == 376.1
    assert c_edges['IA-WET-FLOAT-01']['params']['pre_al_cake_kg_d'] == 343.1
    assert c_edges['S34B']['params']['pre_fr_kg_d'] == 0.61
    assert c_edges['IA-CL2-SHIP']['params']['base_kg_d'] == 0.0
    assert 'si_cl2_kg_d' not in c_edges['IA-CL2-SHIP']['params'], 'the A-M-484 pop is seed topology'
    assert inv['other_mutations'] and inv['seeded_edge_params'], 'the residue classes are documented'
    # the brine-route locale gate (AQS-SITE-010): hosts present at the baseline
    b = run()
    assert b.computed, 'the family stamped (the hosts are present at the baseline)'


def test_no_drivers_records_nothing():
    b = load(REF_GRAPH)
    FD.foundry_poly(b, {})
    assert b.computed == {}


def test_determinism_two_runs_byte_identical():
    assert render(run()) == render(run())


def test_provenance_rows():
    b = run()
    for (_kind, _uid, _path), (value, prov) in b.computed.items():
        assert prov.stage == 'foundry_poly' and prov.basis
    assert b.computed[('node', 'BRINE_CRYS', 'params.design')][1].basis.startswith('X-RTE TF')
    assert b.computed[('node', 'AL_POT', 'params.sizing')][1].basis.startswith('the recovery-sized')


def test_function_module_grid_purity():
    """The engine module holds no float literals and no I/O (the lint's rule)."""
    tree = ast.parse(inspect.getsource(FD))
    floats = [n.lineno for n in ast.walk(tree)
              if isinstance(n, ast.Constant) and isinstance(n.value, float)]
    opens = [n.lineno for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'open']
    assert floats == [] and opens == []

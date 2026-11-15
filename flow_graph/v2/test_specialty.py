"""engine v2: the specialty-sizing family acceptance (the golden-value proof).

Reference writer: flow_graph/param/specialty_sizing.py (X-SPEC lane). The
committed graph carries every field the stage writes; the proofs:

- exact change set: the function's overlay equals the enumerated specification,
  and a full walk of the rendered model shows nothing else moved (edges and
  untouched nodes byte-faithful; only the enumerated fields differ, plus the
  structured provenance rows the serializer adds on touched nodes);
- golden equality: every changed field equals the committed golden, numbers
  quantised to the golden's decimals (exact equality, zero enumerated drift);
- the GROW_BED area assert holds on integer mm2 and fires when the framing
  no longer carries the A-M-229 area;
- the DRY_COOLER seed read and its 12.0 kW fallback;
- determinism: two runs, byte-identical;
- grid purity: no float literals and no I/O in the function module.
"""
import ast
import inspect
import json
import os
from decimal import Decimal

import pytest

from flow_graph.v2.functions import specialty as SP
from flow_graph.v2.graph_io import bytes as render, load

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF_GRAPH = os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')
DRIVERS = os.path.join(ROOT, 'flow_graph', 'param', 'drivers.json')
INPUTS = {'drivers': json.load(open(DRIVERS))}

# The change-set specification: every (unit, field path) the function writes.
BOXES = ('AFTERBURNER', 'AFTERBURNER_FLUE', 'BMED_UPW_POLISH', 'COLD_MILL', 'CRU',
         'CRYO_AHU_COND_CONDENSABLE', 'GAS_ATOMIZER', 'GEO_GHEX', 'GEO_HP_CLOSED_LOOP', 'HYDRO_SET',
         'MET_MELT', 'MFG_SHOP', 'OIL_DRYER', 'PV_ARRAY', 'WAFER_FAB', 'WET_BENCH', 'WIRE_DRAW')
ENVELOPE = ('params.size_mm', 'params.size_note')
KW = ('continuous_kw.value', 'continuous_kw.note')
EXPECTED_FIELDS = [
    ('GREASE_CA', 'params.design.duty'), ('GREASE_CA', 'params.design.batch_kgd'),
    ('GREASE_CA', 'params.design.heat_class'), ('GREASE_CA', 'params.sizing.batch_kgd'),
    ('GREASE_CA', 'params.size_mm'), ('GREASE_CA', 'params.size_note'),
    ('GREASE_CA', 'params.size_basis'), ('GREASE_CA', 'continuous_kw.value'),
    ('GREASE_CA', 'continuous_kw.note'),
    ('GREASE_LI', 'params.design.duty'), ('GREASE_LI', 'params.design.batch_kgd'),
    ('GREASE_LI', 'params.sizing.batch_kgd'), ('GREASE_LI', 'params.size_mm'),
    ('GREASE_LI', 'params.size_note'), ('GREASE_LI', 'params.size_basis'),
    ('GREASE_LI', 'continuous_kw.value'), ('GREASE_LI', 'continuous_kw.note'),
    ('P_CA', 'params.design.duty'), ('P_CA', 'params.design.thickener_kgd'),
    ('P_CA', 'params.sizing.thickener_kgd'), ('P_CA', 'params.size_mm'),
    ('P_CA', 'params.size_note'), ('P_CA', 'params.size_basis'),
    ('P_CA', 'continuous_kw.value'), ('P_CA', 'continuous_kw.note'),
    ('LI_RECOVER', 'params.design.duty'), ('LI_RECOVER', 'params.design.slipstream_kgd'),
    ('LI_RECOVER', 'params.sizing.slipstream_kgd'), ('LI_RECOVER', 'params.size_mm'),
    ('LI_RECOVER', 'params.size_note'), ('LI_RECOVER', 'params.size_basis'),
    ('LI_RECOVER', 'continuous_kw.value'), ('LI_RECOVER', 'continuous_kw.note'),
    ('ADS_CHILL', 'params.design.duty'), ('ADS_CHILL', 'params.design.chilled_kw'),
    ('ADS_CHILL', 'params.design.cop_thermal'), ('ADS_CHILL', 'params.sizing.chilled_kw'),
    ('ADS_CHILL', 'params.sizing.cop_thermal'), ('ADS_CHILL', 'params.size_mm'),
    ('ADS_CHILL', 'params.size_note'), ('ADS_CHILL', 'params.size_basis'),
    ('DRY_COOLER', 'params.design.duty'), ('DRY_COOLER', 'params.design.airflow_m3_s'),
    ('DRY_COOLER', 'params.design.fan_kw'), ('DRY_COOLER', 'params.sizing.airflow_m3_s'),
    ('DRY_COOLER', 'params.size_mm'), ('DRY_COOLER', 'params.size_note'),
    ('DRY_COOLER', 'params.size_basis'), ('DRY_COOLER', 'continuous_kw.value'),
    ('DRY_COOLER', 'continuous_kw.note'),
    ('GW_INTAKE', 'params.design.duty'), ('GW_INTAKE', 'params.design.pump_kw'),
    ('GW_INTAKE', 'params.sizing.pump_kw'), ('GW_INTAKE', 'params.size_mm'),
    ('GW_INTAKE', 'params.size_note'), ('GW_INTAKE', 'params.size_basis'),
    ('GW_INTAKE', 'continuous_kw.value'), ('GW_INTAKE', 'continuous_kw.note'),
    ('H2O_ELYZ', 'params.design.duty'), ('H2O_ELYZ', 'params.design.kwh_per_kg_h2'),
    ('H2O_ELYZ', 'params.design.machine'), ('H2O_ELYZ', 'params.design.rated_kw'),
    ('H2O_ELYZ', 'params.design.window_h'), ('H2O_ELYZ', 'params.design.h2_rate_kg_h'),
    ('H2O_ELYZ', 'params.design.stack'), ('H2O_ELYZ', 'params.design.separators'),
    ('H2O_ELYZ', 'params.design.deoxo'), ('H2O_ELYZ', 'params.design.dryer'),
    ('H2O_ELYZ', 'params.design.skid'), ('H2O_ELYZ', 'params.design.computed_by'),
    ('H2O_ELYZ', 'params.sizing.kwh_per_kg_h2'), ('H2O_ELYZ', 'params.sizing.rated_kw'),
    ('H2O_ELYZ', 'params.size_mm'), ('H2O_ELYZ', 'params.size_note'),
    ('BAGHOUSE', 'params.design.machine'), ('BAGHOUSE', 'params.design.dust_kg_d'),
    ('BAGHOUSE', 'params.design.hoods_m2'), ('BAGHOUSE', 'params.design.hood_face_velocity_m_s'),
    ('BAGHOUSE', 'params.design.capture_air_m3_h'), ('BAGHOUSE', 'params.design.ac_basis_m3_min_m2'),
    ('BAGHOUSE', 'params.design.cloth_req_m2'), ('BAGHOUSE', 'params.design.bags'),
    ('BAGHOUSE', 'params.design.bag_mm'), ('BAGHOUSE', 'params.design.bag_pitch_mm'),
    ('BAGHOUSE', 'params.design.cloth_drawn_m2'), ('BAGHOUSE', 'params.design.ac_drawn_m3_min_m2'),
    ('BAGHOUSE', 'params.design.ducts'), ('BAGHOUSE', 'params.design.housing_inner_mm'),
    ('BAGHOUSE', 'params.design.wall_mm'), ('BAGHOUSE', 'params.design.hopper_h_mm'),
    ('BAGHOUSE', 'params.design.valve_outlet_mm'), ('BAGHOUSE', 'params.design.z_chain'),
    ('BAGHOUSE', 'params.design.material'), ('BAGHOUSE', 'params.design.basis'),
    ('BAGHOUSE', 'params.design.computed_by'), ('BAGHOUSE', 'params.sizing.capture_air_m3_h'),
    ('BAGHOUSE', 'params.sizing.cloth_m2'), ('BAGHOUSE', 'params.size_mm'),
    ('BAGHOUSE', 'params.size_note'),
    ('MAU_HX', 'params.design.duty'), ('MAU_HX', 'params.sizing.duty_kw'),
    ('MAU_HX', 'params.size_mm'), ('MAU_HX', 'params.size_note'), ('MAU_HX', 'params.size_basis'),
    ('FEED_PREP', 'params.sizing.load_basis'), ('FEED_PREP', 'continuous_kw.value'),
    ('FEED_PREP', 'continuous_kw.note'),
    ('POLY_FIBER', 'params.sizing.load_basis'), ('POLY_FIBER', 'continuous_kw.value'),
    ('POLY_FIBER', 'continuous_kw.note'),
    ('AQUA_UV', 'params.sizing.load_basis'), ('AQUA_UV', 'continuous_kw.value'),
    ('AQUA_UV', 'continuous_kw.note'),
    ('EXT_HALL', 'params.size_mm'), ('EXT_HALL', 'params.size_note'),
    ('SI_REDUCE', 'params.size_mm'), ('SI_REDUCE', 'params.size_note'),
] + [(uid, p) for uid in BOXES for p in ENVELOPE] + [
    ('GROW_BED', 'params.size_mm'), ('GROW_BED', 'params.size_note'),
    ('BLACK_DIGEST', 'params.design.D_mm'), ('BLACK_DIGEST', 'params.design.H_mm'),
    ('BLACK_DIGEST', 'params.design.wall_mm'), ('BLACK_DIGEST', 'params.design.V_L'),
    ('BLACK_DIGEST', 'params.design.material'), ('BLACK_DIGEST', 'params.design.insulation'),
    ('BLACK_DIGEST', 'params.design.heat_W'), ('BLACK_DIGEST', 'params.design.T_C'),
    ('BLACK_DIGEST', 'params.design.SRT_d'), ('BLACK_DIGEST', 'params.design.biogas_g_d'),
    ('BLACK_DIGEST', 'params.size_mm'), ('BLACK_DIGEST', 'params.size_note'),
    ('MET_SYN', 'params.size_mm'), ('MET_SYN', 'params.size_note'),
]


def run():
    b = load(REF_GRAPH)
    SP.specialty_sizing(b, INPUTS)
    return b


def _num_eq(gold, got):
    """Equal quantised to the golden's decimals: exact numeric equality."""
    return Decimal(str(gold)).normalize() == Decimal(str(got)).normalize()


def _eq(gold, got):
    if isinstance(gold, dict):
        return isinstance(got, dict) and set(gold) == set(got) and all(_eq(v, got[k]) for k, v in gold.items())
    if isinstance(gold, list):
        return isinstance(got, list) and len(gold) == len(got) and all(_eq(a, b) for a, b in zip(gold, got))
    if isinstance(gold, (int, float)) and not isinstance(gold, bool):
        return isinstance(got, (int, float)) and not isinstance(got, bool) and _num_eq(gold, got)
    return gold == got


def _dig(node, path):
    cur = node
    for part in path.split('.'):
        cur = cur[part]
    return cur


def _strict_diffs(c_node, r_node, prefix, out, expected):
    """Paths where rendered differs from committed beyond the expected change
    set: strict (same JSON types) everywhere except the enumerated fields,
    where numeric equality suffices (e.g. 7310 against 7310.0). Provenance
    rows, added by the serializer on touched nodes, are excluded."""
    for k in sorted((set(c_node) | set(r_node)) - {'provenance'}):
        p = prefix + '.' + k if prefix else k
        if k not in c_node or k not in r_node:
            out.add(p)
        elif p in expected:
            if not _eq(c_node[k], r_node[k]):
                out.add(p)
        elif isinstance(c_node[k], dict) and isinstance(r_node[k], dict):
            _strict_diffs(c_node[k], r_node[k], p, out, expected)
        elif isinstance(c_node[k], list) and isinstance(r_node[k], list) and len(c_node[k]) == len(r_node[k]):
            if any(type(a) is not type(b) or a != b for a, b in zip(c_node[k], r_node[k])):
                out.add(p)
        elif type(c_node[k]) is not type(r_node[k]) or c_node[k] != r_node[k]:
            out.add(p)


def test_exact_change_set_and_golden_equality():
    with open(REF_GRAPH, encoding='utf-8') as f:
        committed = json.load(f)
    c_nodes = {n['unit_id']: n for n in committed['nodes']}
    c_edges = {e['stream_id']: e for e in committed['edges']}
    b = run()
    out = json.loads(render(b))
    r_nodes = {n['unit_id']: n for n in out['nodes']}
    r_edges = {e['stream_id']: e for e in out['edges']}

    # the overlay is exactly the enumerated specification
    got = {(uid, path) for (kind, uid, path) in b.computed}
    assert got == set(EXPECTED_FIELDS)

    # every changed field equals the committed golden (quantised to its decimals)
    for uid, path in EXPECTED_FIELDS:
        assert _eq(_dig(c_nodes[uid], path), _dig(r_nodes[uid], path)), (uid, path)

    # nothing else moves: a strict walk (same JSON types) finds no drift beyond
    # the enumerated fields; int-vs-float representation on the written fields
    # (e.g. 7310 against the committed 7310.0) is tolerated there, numerically.
    expected_paths = {uid + '.' + path for uid, path in EXPECTED_FIELDS}
    diffs = set()
    for uid in sorted(set(c_nodes) | set(r_nodes)):
        _strict_diffs(c_nodes[uid], r_nodes[uid], uid, diffs, expected_paths)
    assert diffs == set(), sorted(diffs)

    # no edge moves at all (the function reads the IA-* loss edges, writes none)
    for sid in c_edges:
        assert c_edges[sid] == r_edges[sid], sid


def test_changed_values_spot_checks():
    b = run()
    out = json.loads(render(b))
    n = {x['unit_id']: x for x in out['nodes']}
    assert n['ADS_CHILL']['params']['design']['chilled_kw'] == 2.25
    assert n['ADS_CHILL']['params']['design']['cop_thermal'] == 0.45
    assert n['DRY_COOLER']['params']['design']['airflow_m3_s'] == 10.37
    assert n['DRY_COOLER']['params']['design']['fan_kw'] == 7.7
    assert n['DRY_COOLER']['continuous_kw']['value'] == 7.7
    assert n['DRY_COOLER']['continuous_kw']['note'] == (
        'the fan at the 0.05 kW_fan/kW_th class on the rated duty 154 kW (A-M-244 restated); '
        'fan-assisted at the window bounding case (X-SPEC sizing, calculated)')
    elyz = n['H2O_ELYZ']['params']['design']
    assert elyz['kwh_per_kg_h2'] == 55.0 and elyz['rated_kw'] == 85.8
    assert elyz['h2_rate_kg_h'] == 1.5597
    assert elyz['stack']['active_per_cell_cm2'] == 288.0
    assert elyz['stack']['active_mm'] == [169.7, 169.7]
    assert elyz['stack']['i_stack_A'] == 518.4
    assert elyz['stack']['v_stack_V'] == 148.0
    assert elyz['stack']['p_dc_kW'] == 76.72
    assert elyz['stack']['area_m2_total'] == 2.304
    assert elyz['deoxo']['tube'] == 'DN80 x 345 mm 316L'
    assert elyz['dryer']['tube'] == 'DN80 x 712 mm 316L'
    assert elyz['dryer']['sieve_kg'] == 5.01 and elyz['dryer']['water_kg_d'] == 0.167
    assert elyz['skid']['l_stack_mm'] == 2042 and elyz['skid']['l_bop_mm'] == 1225
    assert n['H2O_ELYZ']['params']['size_mm'] == [3367, 1050, 2200]
    bh = n['BAGHOUSE']['params']['design']
    assert bh['dust_kg_d'] == {'IA-MILL-LOSS': 6.82, 'IA-FAB-LOSS': 0.0, 'IA-WIRE-LOSS': 0.358}
    assert bh['capture_air_m3_h'] == 756.0
    assert bh['cloth_req_m2'] == 10.5 and bh['cloth_drawn_m2'] == 11.31
    assert bh['ac_drawn_m3_min_m2'] == 1.114
    assert bh['hopper_h_mm'] == 606 and bh['z_chain']['bags'] == [676, 1876]
    assert bh['z_chain']['plenum'] == [1896, 2256]
    assert n['BAGHOUSE']['params']['size_mm'] == [1250, 1000, 2276]


def test_grid_qty_fields():
    """Grid-dimensioned fields carry Qty provenance on the declared dimension."""
    b = run()
    for uid in ('GREASE_CA', 'GREASE_LI', 'P_CA', 'LI_RECOVER'):
        v, _p = b.computed[('node', uid, 'params.design.' +
                            ('batch_kgd' if uid.startswith('GREASE') else
                             ('thickener_kgd' if uid == 'P_CA' else 'slipstream_kgd')))]
        assert v.dim == 'mass_flow' and isinstance(v.count, int)
    for uid in ('GREASE_CA', 'GREASE_LI', 'P_CA', 'LI_RECOVER', 'DRY_COOLER', 'GW_INTAKE',
                'FEED_PREP', 'POLY_FIBER', 'AQUA_UV'):
        v, _p = b.computed[('node', uid, 'continuous_kw.value')]
        assert v.dim == 'power' and isinstance(v.count, int)
    assert b.computed[('node', 'GW_INTAKE', 'continuous_kw.value')][0].count == 370
    assert b.computed[('node', 'AQUA_UV', 'continuous_kw.value')][0].count == 40


def test_grow_bed_integer_mm2_and_assert():
    b = run()
    size = b.computed[('node', 'GROW_BED', 'params.size_mm')][0]
    assert size == [7310, 4030, 911] and all(isinstance(x, int) for x in size)
    assert 4 * 1820 * (2 * 2000) == 29120000                # the framing carries the A-M-229 area
    b2 = load(REF_GRAPH)
    b2.nodes['GROW_BED']['params']['area_m2'] = 29.13       # tamper: the framing no longer fits
    with pytest.raises(AssertionError, match='the bay framing must carry the A-M-229 area exactly'):
        SP.specialty_sizing(b2, INPUTS)


def test_dry_cooler_seed_read_and_fallback():
    b = load(REF_GRAPH)
    del b.nodes['DRY_COOLER']['params']['rated_kW']          # a seed without the heat lane's rating
    SP.specialty_sizing(b, INPUTS)
    out = json.loads(render(b))
    n = next(x for x in out['nodes'] if x['unit_id'] == 'DRY_COOLER')
    assert n['params']['design']['fan_kw'] == 0.6            # 0.05 x the 12.0 kW fallback
    assert n['params']['sizing']['airflow_m3_s'] == 0.81     # 0.61 m3/s per 7.25 kW on the 9.6 kW duty
    assert n['continuous_kw']['note'].startswith(
        'the fan at the 0.05 kW_fan/kW_th class on the rated duty 12 kW')


def test_no_declared_inputs_records_nothing():
    """The bridge solve / check carry no driver payload: the stage records
    nothing and the seed stands (the test_core bridge contract)."""
    b = load(REF_GRAPH)
    SP.specialty_sizing(b, {})
    assert b.computed == {}


def test_determinism_two_runs_byte_identical():
    assert render(run()) == render(run())


def test_provenance_rows():
    b = run()
    for (kind, uid, path), (value, prov) in b.computed.items():
        assert kind == 'node' and prov.stage == 'specialty_sizing' and prov.basis
    assert b.computed[('node', 'GROW_BED', 'params.size_note')][1].ref == 'A-M-469'
    assert b.computed[('node', 'H2O_ELYZ', 'params.design.stack')][1].ref == 'A-M-459'
    assert b.computed[('node', 'BAGHOUSE', 'params.design.capture_air_m3_h')][1].ref == 'A-M-458'
    assert b.computed[('node', 'EXT_HALL', 'params.size_note')][1].ref == 'A-M-104'


def test_function_module_grid_purity():
    """The engine module holds no float literals and no I/O (the lint's rule,
    enforced here because the lint's scan of functions/ is not recursive)."""
    tree = ast.parse(inspect.getsource(SP))
    floats = [n.lineno for n in ast.walk(tree)
              if isinstance(n, ast.Constant) and isinstance(n.value, float)]
    opens = [n.lineno for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'open']
    assert floats == [] and opens == []

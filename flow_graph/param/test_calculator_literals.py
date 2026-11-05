"""X-QA-06 gate (AQS-PAR-001): design numbers in the study calculators come from drivers.json.

The four calculators - docs-authority/_rect_ew_sizing.py, docs-authority/_ew_sizing.py,
flow_graph/param/specialty_sizing.py and flow_graph/param/stub_activation.py - must read every
named design constant through flow_graph.param.drivers.val (or flow_graph.param.constants for
physical data). A bare numeric assignment is a design constant that has not been moved; this test
fails while one remains. Expressions that compute (sums, products, divisions) are not bare
assignments and are not flagged: a unit conversion such as ``* 1000`` or a loop variable is
arithmetic, not an input. The allow-list covers the structural literals 0 and 1 (identity and
zero), which carry no design content. Text-bonded records (a tuple holding a number next to its
basis note, an envelope list inside a design record) are not bare assignments; their basis travels
in the adjacent string and is gated by the citation checks.

The second test pins the step-2 move: each driver below holds the calculator's previous value, so
the generated numbers stay identical to the pre-move calculation.
"""
import ast
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CALCULATORS = [
    'docs-authority/_rect_ew_sizing.py',
    'docs-authority/_ew_sizing.py',
    'flow_graph/param/specialty_sizing.py',
    'flow_graph/param/stub_activation.py',
]
ALLOW = {0, 1, 0.0, 1.0}


def _bare_numeric(node):
    """True when a value node is a bare number or a list/tuple of bare numbers."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
        return node.value not in ALLOW
    if isinstance(node, (ast.List, ast.Tuple)):
        if not node.elts:
            return False
        return all(
            isinstance(e, ast.Constant) and isinstance(e.value, (int, float)) and not isinstance(e.value, bool) and e.value not in ALLOW
            for e in node.elts
        )
    return False


def _assignments(path):
    tree = ast.parse(open(path).read(), filename=path)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            value = node.value
        elif isinstance(node, ast.AnnAssign):
            value = node.value
        elif isinstance(node, ast.NamedExpr):
            value = node.value
        else:
            continue
        if value is not None and _bare_numeric(value):
            yield node.lineno, ast.unparse(node)[:120]


def test_no_bare_numeric_design_constants():
    found = {}
    for rel in CALCULATORS:
        path = os.path.join(ROOT, rel)
        bad = list(_assignments(path))
        if bad:
            found[rel] = bad
    assert not found, found


def test_moved_drivers_hold_calculator_values():
    from flow_graph.param import drivers as DR
    d = DR.load()
    expect = {
        'rect_channel_frame_sizes_A': [250, 500, 1000, 1500, 2000, 2500, 3000, 4000],
        'rect_channel_margin': 1.1,
        'rect_channel_rated_V': 6.0,
        'rect_busbar_J_A_cm2': 200.0,
        'ew_sheet_collection_cell': 9,
        'si_kgd': 1.8,
        'ely_window_h': 6.0,
        'pem_stack_j_A_cm2': 1.8,
        'pem_stack_v_cell_V': 1.85,
        'pem_stack_cells': 80,
        'elyz_h2_design_kg_d': 9.358,
        'elyz_bed_radius_m': 0.04,
        'baghouse_hood_face_velocity_m_s': 0.5,
        'baghouse_ac_basis_m3_min_m2': 1.2,
        'baghouse_bag_count': 20,
        'baghouse_hood_mill_m2': 0.2,
        'baghouse_hood_kerf_m2': 0.12,
        'baghouse_hood_wire_m2': 0.1,
        'litho_dev_kW': 0.008,
        'blow_mold_rate_kg_h': 2.8,
        'blow_mold_extruder_kW': 2.2,
        'blow_mold_clamp_kW': 0.75,
        'blow_mold_air_kW': 0.75,
        'electrode_coat_exhaust_kW': 0.35,
        'electrode_coat_cure_kW': 1.2,
        'lio_bat_energy_kWh': 2517,
        'geo_orc_feed_pump_kW': 0.05,
        'GEO.orc-train.q_sink_kW': 12.0,
    }
    for key, value in expect.items():
        assert key in d, f'{key}: driver missing'
        assert DR.val(d, key) == value, f'{key}: {DR.val(d, key)!r} != {value!r}'

"""X-PAR-04 gate (AQS-PAR-001 section 1 item 5). Fails when a solved unit does not close or a
graph value compared by solver.check() deviates from the solver by more than solver.MISFIT_TOL."""
from flow_graph.param import solver

def test_solved_units_close():
    errs, _, _, _ = solver.check()
    assert not errs, errs

def test_graph_within_misfit_tolerance():
    _, mis, _, _ = solver.check()
    bad = [f'{m[0]}: graph {m[1]:.3f}, solved {m[2]:.3f}, {m[3]*100:+.2f} %' for m in mis if abs(m[3]) > solver.MISFIT_TOL]
    assert not bad, bad

def test_acid_loop_below_azeotrope():
    d, _, _ = solver.solve()
    assert d['acid_conc_design_wt']['value'] < d['hcl_azeotrope_wt']['value']

def test_roof_carries_pv():
    """X-PAR-07: PV is roof-only; the converged roof carries the nameplate."""
    _, g, s = solver.solve()
    pv = next(n for n in g['nodes'] if n['unit_id'] == 'PV_ARRAY')['params']
    assert pv['nameplate_kw'] <= s['roof']['pv_roof_kWp'] and pv['nameplate_kw'] >= s['roof']['pv_need_kWp']

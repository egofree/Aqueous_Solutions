"""X-PAR-02 gate: every unit closes on the mass edges (AQS-PAR-003); fails on imbalance."""
import json
import numpy as np
from flow_graph.param import balance as B
def test_mass_closes():
    g = json.load(open(B.GP)); R = B.reconcile(g)
    bad = [(R['nodes'][k], float(R['r0'][k])) for k in range(len(R['nodes'])) if abs(R['r0'][k]) > 1e-3]
    assert not bad, bad

def test_reconciliation_within_tolerance():
    """Owner rule: reconciliation is not a fudge. Every reconciled move lies inside the measurement tolerance B.TOL (A-M-120)."""
    g = json.load(open(B.GP)); B.physics(g); R = B.reconcile(g)
    out = [(R['E'][i]['stream_id'], float(R['x0'][i]), float(R['x'][i])) for i in R['free'] if abs(R['x'][i] - R['x0'][i]) > B.TOL*max(R['x0'][i], 0.05)]
    assert not out, out

def test_closure_transfer_functions():
    """X-PAR-02: every study edge is a closure TF or a design input; closures re-derive from the inputs within 0.1 g/d."""
    from flow_graph.param import closure_tf as T
    g = json.load(open(B.GP)); B.physics(g); R, role, order = T.assign(g)
    assert len(role) == len(R['free'])
    assert T.rederive(g, R, role, order) < 1e-4

"""X-PAR-02 gate: every unit closes on the mass edges (AQS-PAR-003); fails on imbalance."""
import json
import numpy as np
from flow_graph.param import balance as B
def test_mass_closes():
    g = json.load(open(B.GP)); R = B.reconcile(g)
    bad = [(R['nodes'][k], float(R['r0'][k])) for k in range(len(R['nodes'])) if abs(R['r0'][k]) > 1e-3]
    assert not bad, bad

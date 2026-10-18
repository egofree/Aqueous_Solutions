"""X-STD-01 gate: every check document carries its code-basis block with each governing clause."""
import os
from flow_graph.param import code_basis as CB
def test_code_basis_present():
    for k, p in CB.PATHS.items():
        s = open(os.path.join(CB.ROOT, p)).read()
        assert CB.MARK in s, f'{p}: no code basis block'
        for a, b in CB.B[k]:
            assert b in s, f'{p}: missing {b}'

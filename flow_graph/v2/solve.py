"""engine v2: the solve — pure functions composed in one declared order.

A solve function takes (builder, inputs) and records computed fields with their
provenance. No I/O, no wall-clock, no RNG, no float arithmetic (the lint holds
this). The composition order is the import list below: one place, explicit, no
hidden dependencies. Physics migrates family by family from the reference
writers (each migration carries its golden-value proof).
"""
from . import functions as _fns                    # noqa: F401  (import = registration)
from .graph_io import load
from .model import Builder
from .registry import fn, FNS                      # noqa: F401

GRAPH_PATH = 'flow_graph/plant_flow_graph.json'


def solve(inputs, graph_path=None):
    """The one deterministic solve: load the model seed, apply the declared
    functions in order, freeze. Same inputs -> byte-identical serialization,
    always. inputs: dict of input payloads (drivers, refs, ...); the seed is the
    serialized graph at graph_path (the strangler bridge until construction
    itself migrates into the solve)."""
    b = load(graph_path or GRAPH_PATH)
    for f in FNS:
        f(b, inputs)
    return b.build()

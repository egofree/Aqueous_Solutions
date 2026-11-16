"""engine v2: the solve — pure functions composed in one declared order.

A solve function takes (builder, inputs) and records computed fields with their
provenance. No I/O, no wall-clock, no RNG, no float arithmetic (the lint holds
this). The composition order is the import list below: one place, explicit, no
hidden dependencies. Physics migrates family by family from the reference
writers (each migration carries its golden-value proof).
"""
from . import functions as _fns                    # noqa: F401  (import = registration)
from .functions import process                     # noqa: F401
from .functions import power                       # noqa: F401
from .functions import heat                        # noqa: F401
from .functions import relief_vent                 # noqa: F401
from .functions import foundry                     # noqa: F401
from .functions import farm_balance                # noqa: F401
from .functions import materials3                  # noqa: F401
from .functions import pot_cells                   # noqa: F401
from .functions import specialty                   # noqa: F401
from .functions import si_route                    # noqa: F401
from .functions import sites                       # noqa: F401
from .functions import meoh_train                  # noqa: F401
from .functions import storage_sizing              # noqa: F401
from .functions import pv_cell_line                # noqa: F401
from .functions import dock_class                  # noqa: F401
from .functions import h2_purifier                 # noqa: F401
from .functions import house_scrubbers             # noqa: F401
from .functions import upw_polish                  # noqa: F401
from .functions import geo_loop                    # noqa: F401
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

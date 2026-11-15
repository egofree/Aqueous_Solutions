"""engine v2: the solve — pure functions composed in one declared order.

A solve function takes (builder, inputs) and records computed fields with their
provenance. No I/O, no wall-clock, no RNG, no float arithmetic (the lint holds
this). FNS is the declared composition order; solve() applies it and freezes.

The list starts empty by design: physics migrates family by family from the
reference writers (each migration carries its golden-value proof), and the
composition order is data here — one place, explicit, no hidden dependencies.
"""
from .graph_io import load
from .model import Builder

GRAPH_PATH = 'flow_graph/plant_flow_graph.json'

FNS = []


def fn(name, basis):
    """Register a solve function under a name and its engineering basis citation."""
    def deco(f):
        f.stage_name, f.stage_basis = name, basis
        FNS.append(f)
        return f
    return deco




def fn(name, basis):
    """Register a solve function under a name and its engineering basis citation."""
    def deco(f):
        f.stage_name, f.stage_basis = name, basis
        FNS.append(f)
        return f
    return deco


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


@fn('pot_cell_bath_top', 'the pot builders geometry: bath top z = immersion + tips (A-M-496)')
def pot_cell_bath_top(b, inputs):
    """Exemplar migration (the reference writer flow_graph/param/pot_cells.py): the bath
    top sits anode-immersion + 100 mm tip elevation, on the length grid."""
    for uid in ('CA_POT', 'CR_CELL', 'MG_POT', 'MO_CELL'):
        node = b.nodes.get(uid)
        if node is None or node.get('presence') != 'present':
            continue
        imm = node.get('params', {}).get('design', {}).get('anode_imm_mm')
        if imm is None:
            continue
        tips = inputs.get('pot_tips_mm', 100)
        from .grid import Qty
        b.set_node_field(uid, 'design.bath_top_mm',
                         Qty(int(round(float(imm))) + int(tips), 'length'),
                         {'stage': 'pot_cell_bath_top', 'basis': 'bath top = immersion + tips',
                          'ref': 'A-M-496'})

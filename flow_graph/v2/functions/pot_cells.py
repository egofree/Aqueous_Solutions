"""The pot-cell bath-top geometry (exemplar migration; reference writer
flow_graph/param/pot_cells.py). The bath surface sits at immersion + tip
elevation — one line of arithmetic the builders consume.
"""
from flow_graph.v2.grid import Qty
from flow_graph.v2.registry import fn


@fn('pot_cell_bath_top', 'the pot builders geometry: bath top z = immersion + tips (A-M-496)')
def pot_cell_bath_top(b, inputs):
    for uid in ('CA_POT', 'CR_CELL', 'MG_POT', 'MO_CELL'):
        node = b.nodes.get(uid)
        if node is None or node.get('presence') != 'present':
            continue
        imm = node.get('params', {}).get('design', {}).get('anode_imm_mm')
        if imm is None:
            continue
        tips = inputs.get('pot_tips_mm', 100)
        b.set_node_field(uid, 'design.bath_top_mm',
                         Qty(int(round(float(imm))) + int(tips), 'length'),
                         {'stage': 'pot_cell_bath_top', 'basis': 'bath top = immersion + tips',
                          'ref': 'A-M-496'})

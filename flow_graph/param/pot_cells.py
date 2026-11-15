"""Pot-cell bath-top geometry stamp (X-QA-18 step 3, A-M-496).

The manufacturing builders of the four pot cells (CA_POT, CR_CELL, MG_POT,
MO_CELL) read ``design.bath_top_mm`` - the z of the bath surface, which sets
the tap-well crest, the hood lintel and the lining run-out on their drawing
sheets. The key is derived geometry, not a fresh size: the bath surface sits
at the anode tip elevation plus the immersion (the builders' stated
arithmetic: "bath top z 350 = 250 mm immersion + tips z 100"), so this stage
computes it from the unit's own ``design.anode_imm_mm`` (the foundry_poly
Faraday sizing) plus the A-M-496 tip elevation and stamps it into the design
block the builders read through the plant graph. Nothing here is hand-held
beyond the registered A-M-496 tip elevation.

Run: python3 -m flow_graph.param.pot_cells  (writes_graph: graph stage of
regen_manifest.json, after foundry_poly)
"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
GP = os.path.join(os.path.dirname(HERE), 'plant_flow_graph.json')

# A-M-496: the anode rods hang with their tips 100 mm above the cell floor
# (rod column z 100..1164), so bath top z = anode_imm_mm + 100.
TIP_Z_MM = 100.0
UNITS = ('CA_POT', 'CR_CELL', 'MG_POT', 'MO_CELL')


def main():
    g = json.load(open(GP))
    N = {n['unit_id']: n for n in g['nodes']}
    missing = [u for u in UNITS if u not in N]
    assert not missing, f'{missing}: pot cells absent from the graph'
    wrote = []
    for u in UNITS:
        design = N[u].setdefault('params', {}).get('design') or {}
        assert design.get('anode_imm_mm'), f'{u}: no design.anode_imm_mm to derive the bath top from'
        top = round(design['anode_imm_mm'] + TIP_Z_MM, 1)
        if design.get('bath_top_mm') != top:
            design['bath_top_mm'] = top
            wrote.append(u)
    json.dump(g, open(GP, 'w'), indent=2)
    print(f'pot_cells: bath_top_mm = anode_imm_mm + {TIP_Z_MM:g} (A-M-496) on '
          f'{len(UNITS)} pot cells, {", ".join(wrote) if wrote else "none"} changed')


if __name__ == '__main__':
    main()

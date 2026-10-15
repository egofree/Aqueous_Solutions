"""X-PAR-07 layout: writes the extension blocks and the roof PV_ARRAY row from the converged roof (graph PV_ARRAY params.roof).
EXT_HALL_E east of the base plate, EXT_HALL_N north of it; the west yard stays outdoor (NFPA 855 ESS, NFPA 2 hydrogen)."""
import json
g = json.load(open('flow_graph/plant_flow_graph.json')); pv = next(n for n in g['nodes'] if n['unit_id'] == 'PV_ARRAY')['params']; rf = pv['roof']
W, D = rf['footprint_mm']; p = rf['perimeter_pathway_mm']
P = 'flow_graph/placement_seed.json'; s = json.load(open(P)); z = s['datums_mm'].setdefault('ROOF', 14400)
r = next(r for r in s['units'] if r['unit_id'] == 'PV_ARRAY')
r.update(level='ROOF', origin_mm=[p, p, z], size_mm=[W-2*p, D-2*p, 300])
r['source'] = (f"X-PAR-07 roof-only PV (ground field removed). Envelope of {rf['arrays']} arrays inside the IFC 2021 1205.3 {p} mm perimeter pathway "
               f"of the {W/1000:.0f} x {D/1000:.0f} m roof (solver.roof_close); 1219 mm interior pathways; array area {pv['area_m2']} m2. ROOF datum {z} mm is a study value (A-M-103).")
s['blocks'] = [b for b in s['blocks'] if not b['block_id'].startswith('EXT_HALL')] + [
    dict(block_id='EXT_HALL_E', level='L0', origin_mm=[24000, 0], size_mm=[W-24000, D, 6000], unit_ids=['EXT_HALL'],
         source='X-PAR-07 single-storey conditioned extension carrying the roof PV (owner decision 2026-10-15, A-M-104). East of the base plate; west yard stays outdoor (NFPA 855, NFPA 2).'),
    dict(block_id='EXT_HALL_N', level='L0', origin_mm=[0, 18000], size_mm=[24000, D-18000, 6000], unit_ids=['EXT_HALL'],
         source='X-PAR-07 extension north of the base plate. NORTH_DOCK opens into it; a 6 m truck lane to the north wall is reserved (accepted 2026-10-15).')]
s['notes_rev_l'] = (f"2026-10-15, X-PAR-07: building grown to {W/1000:.0f} x {D/1000:.0f} m ({rf['bays'][0]} x {rf['bays'][1]} bays of 6 m, conditioned extension) so the roof carries "
                    f"the full PV array; EXT_HALL_E/N blocks; PV_ARRAY on ROOF; ground field removed. Base-plate rows not moved: no sizing driver warrants it.")
s['revision'] = 'L'
json.dump(s, open(P, 'w'), indent=2, ensure_ascii=True); print(W, D, rf['arrays'])

"""X-BLD-04. Lays out the PV ground field as one study envelope west of the yard: area = PV_ARRAY nameplate
x pv_ground_m2_per_kWp (drivers.json, A-M-078), rectangle of aspect pv_field_aspect (E-W long, rows facing the
equator), east edge maint_clear_mm west of the westmost other L0 row, south edge on the yard's south line.
Owner site area is pending (X-BAS-03); this is a study placement. --write updates the PV_ARRAY seed row."""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flow_graph.param import drivers as DR
d = DR.load(); SEED = 'flow_graph/placement_seed.json'; seed = json.load(open(SEED))
g = json.load(open('flow_graph/plant_flow_graph.json')); kwp = next(n for n in g['nodes'] if n['unit_id']=='PV_ARRAY')['params']['nameplate_kw']
A = kwp*DR.val(d,'pv_ground_m2_per_kWp'); asp = DR.val(d,'pv_field_aspect')
dy = math.ceil(math.sqrt(A/asp)*10)*100; dx = math.ceil(A*1e6/dy/100)*100    # mm, 100 mm grid
L0 = [r for r in seed['units'] if r.get('level')=='L0' and r['unit_id']!='PV_ARRAY']
x_e = min(r['origin_mm'][0] for r in L0) - seed['rules']['maint_clear_mm']; y_s = min(r['origin_mm'][1] for r in L0)
row = dict(origin_mm=[x_e-dx, y_s, 0], size_mm=[dx, dy, 2500])
print(f'{kwp} kWp, {A:.0f} m2, field {dx/1000:.1f} x {dy/1000:.1f} m at ({x_e-dx}, {y_s})')
if '--write' in sys.argv:
    r = next(r for r in seed['units'] if r['unit_id']=='PV_ARRAY'); r.update(row)
    r['source'] = (f'X-BLD-04 study PV ground field (flow_graph/place_pv_field.py): {kwp} kWp x {DR.val(d,"pv_ground_m2_per_kWp")} m2/kWp = {A:.0f} m2, '
                   f'{dx/1000:.1f} x {dy/1000:.1f} m, 2.5 m mount height (study), {seed["rules"]["maint_clear_mm"]} mm west of the yard. Site area pending owner (X-BAS-03); A-M-078, A-M-098.')
    json.dump(seed, open(SEED,'w'), indent=2, ensure_ascii=True)

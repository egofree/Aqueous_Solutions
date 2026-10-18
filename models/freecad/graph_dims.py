"""Parametric unit dims from the graph (AQS-BLD-010 rev E, A-M-226). Runs in build_plant.py before resolve_overlaps.
Every unit whose graph node carries params.design_storage (AQS-DUTY-064, docs-authority/_storage_sizing.py) is rebuilt as
an upright cylinder D x H at its placed plan centre and floor level, so the GA follows the sizing calculation.
Labels move with the unit's top. Logs to ../../docs-authority/inventory/CAD_GRAPH_DIMS.json."""
import json
import FreeCAD as App
import Part
def apply(doc, graph, log):
    g = json.load(open(graph)); out = []
    for n in g['nodes']:
        ds = (n.get('params') or {}).get('design_storage')
        if not ds: continue
        objs = [o for o in doc.Objects if o.Label == n['unit_id'] and o.TypeId.startswith('Part::') and hasattr(o, 'Shape') and not o.Shape.isNull()]
        if not objs: out.append(dict(unit=n['unit_id'], applied=False, note='no Part object with this label')); continue
        o = objs[0]; b = o.Shape.BoundBox; D, H = float(ds['D_mm']), float(ds['H_mm'])
        old = [round(b.XLength), round(b.YLength), round(b.ZLength)]
        s = Part.makeCylinder(D / 2, H, App.Vector(b.Center.x, b.Center.y, b.ZMin))
        if o.TypeId == 'Part::Feature':
            o.Placement = App.Placement(); o.Shape = s
        else:
            nf = doc.addObject('Part::Feature', o.Name + '_g'); nf.Shape = s
            lab = o.Label; doc.removeObject(o.Name); nf.Label = lab
        out.append(dict(unit=n['unit_id'], applied=True, old_mm=old, D_mm=D, H_mm=H, material=ds.get('material')))
    json.dump(out, open(log, 'w'), indent=1)
    print("  graph dims: %d units resized from the graph" % sum(1 for x in out if x['applied']))

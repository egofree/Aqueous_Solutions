"""X-BAS-02. Held rates recalculated at the bounding feed cases of AQS-ASSAY-001 Rev C.
Method: class mass at each case = 102.68 kg/d x class fraction. The increment over the
reference point is added to the edge that carries that class (incremental), except the
organic line, which scales with the organic ratio. Prints a markdown table."""
import json
F=102.68
C={'A':dict(water=0,silicate_oxide=0.99,organic=0,unassigned=0,other_inorganic=0.005),
   'B':dict(water=0.03,silicate_oxide=0.30,organic=0.25,unassigned=0.09905,other_inorganic=0),
   'MSW':dict(water=0.25,silicate_oxide=0.05,organic=0.30,unassigned=0.341,other_inorganic=0),
   'ref':dict(water=0.05,silicate_oxide=0.18,organic=0.22,unassigned=0.14975,other_inorganic=0)}
g=json.load(open('flow_graph/plant_flow_graph.json'))
R={e['stream_id']:e['rate']['value'] for e in g['edges']}
rows=[]
def inc(cls,unit,sid,note):
    out=[]
    for k in ('A','B','MSW'):
        d=F*(C[k][cls]-C['ref'][cls]); out.append(R[sid]+d)
    rows.append((cls,unit,sid,R[sid],*out,note))
inc('silicate_oxide','FLOAT_SINK','IA-SINK-01','increment on sink solids; regolith silicate assumed to report to sink, not to the glass train')
inc('water','LEACH_CSTR_1','IA-EW-04','feed water joins the liquor')
for cls,u,sid in (('organic','OIL_DRYER','IA-PLAST-01'),('organic','OIL_PYRO','IA-OIL-01')):
    out=[R[sid]*C[k][cls]/C['ref'][cls] for k in ('A','B','MSW')]
    rows.append((cls,u,sid,R[sid],*out,'scales with organic fraction'))
# acid demand, case A oxides fully leached (Lunar Sourcebook mid-range, assumption)
ox={'Al2O3':(0.19,6,101.96),'CaO':(0.125,2,56.08),'MgO':(0.09,2,40.30),'FeO':(0.13,2,71.84)}
hcl=sum(F*C['A']['silicate_oxide']*f*n*36.46/M for f,n,M in ox.values())
acid=R['IA-ACID-01']*0.20
print('| Class | Unit | Edge | Graph kg/d | Case A | Case B | MSW | Method |\n| --- | --- | --- | --- | --- | --- | --- | --- |')
for r in rows: print(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]:.2f} | {r[4]:.2f} | {r[5]:.2f} | {r[6]:.2f} | {r[7]} |")
print(f"\nAcid. IA-ACID-01 carries {R['IA-ACID-01']:.2f} kg/d of 20 wt% HCl = {acid:.2f} kg/d HCl. Case A with Al2O3 0.19, CaO 0.125, MgO 0.09, FeO 0.13 of the silicate fully leached needs {hcl:.1f} kg/d HCl, {hcl/acid:.1f} times the edge. TiO2 and SiO2 are taken as not leached.")
json.dump({'rows':rows,'hcl_A':hcl,'hcl_edge':acid},open('/tmp/bc.json','w'))

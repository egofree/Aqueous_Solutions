"""X-MAT-19. Coolers on hot LEACH_CSTR_1 draws: duty and passive air-cooled PVDF pipe length.
Study values; register A-M entries."""
import json, math
g=json.load(open('flow_graph/plant_flow_graph.json')); R={e['stream_id']:e for e in g['edges']}
D={'IA-BMED-03':(3.0,35.0,'BMED_ACID membrane inlet 35 C'),'IA-BMED-04':(3.6,35.0,'BMED_BASE membrane inlet 35 C')}
Tin=85.0; Tair=37.8; U=7.0; OD=0.032   # W/m2K natural convection outside, PVDF DN25 OD 32 mm
rows=[]
for s,(cp,Tout,why) in D.items():
    m=R[s]['rate']['value']; Q=m*cp*(Tin-Tout)/86400*1000   # W
    lm=((Tin-Tair)-(Tout-Tair))/math.log((Tin-Tair)/(Tout-Tair)) if Tout>Tair else None
    A=Q/(U*lm) if lm else None; L=A/(math.pi*OD) if A else None
    rows.append(dict(edge=s,m=m,cp=cp,Tout=Tout,Q_W=Q,LMTD=lm,A_m2=A,L_m=L,why=why))
if __name__=='__main__': print(json.dumps(rows,indent=1))

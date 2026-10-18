"""X-MAT-19. Coolers on hot LEACH_CSTR_1 draws: duty and passive air-cooled PVDF pipe length.
Study values; register A-M entries."""
import json, math, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flow_graph.param import drivers as DR
from flow_graph.param.sizing import heat as HT
_d=DR.load()
g=json.load(open('flow_graph/plant_flow_graph.json')); R={e['stream_id']:e for e in g['edges']}
FEED_T=DR.val(_d,'evap_feed_T_C')   # BMED feed 35 C (A-M-106), the cooler target at the membrane inlets
D={'IA-BMED-03':(DR.val(_d,'cp_hcl20_kJ_kgK'),FEED_T,'BMED_ACID membrane inlet 35 C'),'IA-BMED-04':(DR.val(_d,'cp_naoh20_kJ_kgK'),FEED_T,'BMED_BASE membrane inlet 35 C')}
Tin=DR.val(_d,'DIGESTER.metals-leach-train.brine-loop.LEACH_CSTR_1.hot_draw_T_C'); Tair=DR.val(_d,'site_design_dry_bulb_C'); U=DR.val(_d,'U_free_convection_W_m2K'); OD=DR.val(_d,'DIGESTER.metals-leach-train.acid-base-regen.cooler_pipe_od_m')   # W/m2K natural convection outside, PVDF DN25 OD 32 mm
rows=[]
for s,(cp,Tout,why) in D.items():
    m=R[s]['rate']['value']; Q=HT.sensible_W(m,cp,Tin-Tout)   # W, INCROPERA7
    lm=HT.lmtd(Tin-Tair,Tout-Tair)
    A=HT.area_m2(Q,U,lm); L=A/(math.pi*OD) if A else None
    rows.append(dict(edge=s,m=m,cp=cp,Tout=Tout,Q_W=Q,LMTD=lm,A_m2=A,L_m=L,why=why))
if __name__=='__main__': print(json.dumps(rows,indent=1))

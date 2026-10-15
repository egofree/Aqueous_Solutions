"""AQS-ELEC-005 grounding grid resistance (IEEE Std 80-2013, Sverak equation 52). Study values.
Rev B (D75): the grid follows the converged building (graph PV_ARRAY params.roof) plus the 10 m west yard;
mesh conductors on every second 6 m column line (12 m mesh), rods at about 10 m on the ring (A-M-110)."""
import math, json
rho=50.0                 # ohm m, soil resistivity, assumption (clay, AQS-SITE-002 soil assumption)
g=json.load(open('flow_graph/plant_flow_graph.json')); rf=next(n for n in g['nodes'] if n['unit_id']=='PV_ARRAY')['params']['roof']
X=rf['footprint_mm'][0]/1000+10.0; Y=rf['footprint_mm'][1]/1000   # m, building plus west yard
h=0.75; mesh=12.0        # m burial depth; mesh spacing
Lr=2*(X+Y); rods=math.ceil(Lr/10); rod_L=3.0
Lm=(math.floor(X/mesh)-1)*Y+(math.floor(Y/mesh)-1)*X
A=X*Y; LT=Lr+Lm+rods*rod_L
Rg=rho*(1/LT+1/math.sqrt(20*A)*(1+1/(1+h*math.sqrt(20/A))))
print(json.dumps(dict(rho=rho,A_m2=A,ring_m=Lr,mesh_m=Lm,rods=rods,LT_m=LT,Rg_ohm=round(Rg,3),target_ohm=5.0)))

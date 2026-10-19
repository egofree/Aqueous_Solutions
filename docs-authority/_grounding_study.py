"""AQS-ELEC-005 grounding grid resistance (IEEE Std 80-2013, Sverak equation 52). Study values.
Rev B (D75): the grid follows the converged building (graph PV_ARRAY params.roof) plus the 10 m west yard;
mesh conductors on every second 6 m column line (12 m mesh), rods at about 10 m on the ring (A-M-110)."""
import math, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # U4b: sizing literals single-sourced from drivers.json (A-M-110)
from flow_graph.param import drivers as DR
_d = DR.load(); v = lambda k: DR.val(_d, k)
rho=v('ELEC.distribution-train.gnd_soil_rho_ohm_m')    # ohm m, soil resistivity, assumption (clay, AQS-SITE-002 soil assumption)
g=json.load(open('flow_graph/plant_flow_graph.json')); rf=next(n for n in g['nodes'] if n['unit_id']=='PV_ARRAY')['params']['roof']
X=rf['footprint_mm'][0]/1000+v('ELEC.distribution-train.gnd_west_yard_m'); Y=rf['footprint_mm'][1]/1000   # m, building plus west yard
h=v('ELEC.distribution-train.gnd_depth_m'); mesh=v('ELEC.distribution-train.gnd_mesh_spacing_m')        # m burial depth; mesh spacing
Lr=2*(X+Y); rods=math.ceil(Lr/v('ELEC.distribution-train.gnd_rod_pitch_m')); rod_L=v('ELEC.distribution-train.gnd_rod_L_m')
Lm=(math.floor(X/mesh)-1)*Y+(math.floor(Y/mesh)-1)*X
A=X*Y; LT=Lr+Lm+rods*rod_L
Rg=rho*(1/LT+1/math.sqrt(20*A)*(1+1/(1+h*math.sqrt(20/A))))
print(json.dumps(dict(rho=rho,A_m2=A,ring_m=Lr,mesh_m=Lm,rods=rods,LT_m=LT,Rg_ohm=round(Rg,3),target_ohm=v('ELEC.distribution-train.gnd_target_ohm'))))

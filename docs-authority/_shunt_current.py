"""X-MAT-07. Shunt (stray) current through the liquor between EW cells. Study values."""
import json, math
import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flow_graph.param.drivers import load as _dl; _D=_dl()
sigma=_D['DIGESTER.ew-cascade-train.liquor_conductivity_S_m']['value']  # S/m, chloride liquor about 1.4 M HCl with metal chlorides (A-M-269)
ID=_D['DIGESTER.ew-cascade-train.intercell_bore_m']['value']            # m, 2 in Sch 80 bore (AQS-PIP-003 P1/P2, A-M-036)
A=math.pi/4*ID**2
dV=_D['DIGESTER.ew-cascade-train.max_shunt_dV_V']['value']    # V, worst difference if two floating channels are both earthed at opposite poles (A-M-269)
Imax=_D['DIGESTER.ew-cascade-train.stray_current_limit_A']['value']   # A, stray-current limit (A-M-269)
Rreq=dV/Imax; Lreq=Rreq*sigma*A
L_pitch=0.75; R_pitch=L_pitch/(sigma*A); I_pitch=dV/R_pitch
print(json.dumps(dict(sigma=sigma,A_m2=A,R_req_ohm=Rreq,L_req_m=Lreq,R_at_pitch_ohm=R_pitch,I_at_pitch_A=I_pitch)))

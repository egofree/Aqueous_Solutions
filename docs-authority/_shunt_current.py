"""X-MAT-07. Shunt (stray) current through the liquor between EW cells. Study values."""
import json, math
sigma=30.0                      # S/m, chloride liquor about 1.4 M HCl with metal chlorides, assumption
ID=0.0493                       # m, 2 in Sch 80 bore (AQS-PIP-003 P1/P2)
A=math.pi/4*ID**2
dV=6.0                          # V, worst difference if two floating channels are both earthed at opposite poles
Imax=0.1                        # A, stray-current limit, assumption
Rreq=dV/Imax; Lreq=Rreq*sigma*A
L_pitch=0.75; R_pitch=L_pitch/(sigma*A); I_pitch=dV/R_pitch
print(json.dumps(dict(sigma=sigma,A_m2=A,R_req_ohm=Rreq,L_req_m=Lreq,R_at_pitch_ohm=R_pitch,I_at_pitch_A=I_pitch)))

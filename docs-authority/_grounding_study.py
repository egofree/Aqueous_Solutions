"""AQS-ELEC-005 grounding grid resistance (IEEE Std 80-2013, Sverak equation 52). Study values."""
import math, json
rho=50.0                 # ohm m, soil resistivity, assumption (clay, AQS-SITE-002 soil assumption)
X,Y=35.0,20.0            # m, ring around the placement extents, assumption
h=0.75                   # m burial depth
rods=12; rod_L=3.0       # rods at about 10 m on the ring
A=X*Y; Lr=2*(X+Y); LT=Lr+rods*rod_L
Rg=rho*(1/LT+1/math.sqrt(20*A)*(1+1/(1+h*math.sqrt(20/A))))
print(json.dumps(dict(rho=rho,A_m2=A,ring_m=Lr,LT_m=LT,Rg_ohm=round(Rg,2),target_ohm=5.0)))

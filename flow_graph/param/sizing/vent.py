"""Normal venting of atmospheric tanks [API2000_2020] 3.3.2, SI form; open-vent bore by the orifice equation [PERRY9].
V_out = k_vol V_pf + Y V_tk^0.9 R_i ; V_in = V_pe + C V_tk^0.7 R_i (Nm3/h air). Y, C from drivers (latitude band not fixed until X-BAS-03:
the largest band, below 42 deg, is used). Open vent: Q = Cd A sqrt(2 dP / rho_air)."""
import math
from ..refs import cite
REF = (cite('API2000_2020'), cite('PERRY9'))
def out_breathing_Nm3_h(V_tk, V_pf, Y=0.32, Ri=1.0, k_vol=2.0): return k_vol*V_pf + Y*V_tk**0.9*Ri
def in_breathing_Nm3_h(V_tk, V_pe, C=6.5, Ri=1.0): return V_pe + C*V_tk**0.7*Ri
def open_vent_bore_mm(Q_Nm3_h, dP_Pa, Cd=0.61, rho=1.293):
    A = Q_Nm3_h/3600/(Cd*math.sqrt(2*dP_Pa/rho)); return math.sqrt(4*A/math.pi)*1000

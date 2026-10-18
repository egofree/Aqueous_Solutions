"""Relief device sizing [API520] Part I, US customary units as published; helpers convert to mm.
Coefficients (Kd, Kw, Kc, Kv, Kb) are inputs: take them from the valve vendor or API 520 defaults."""
import math
from ..refs import cite
REF = cite('API520')
IN2_TO_MM2 = 645.16
def liquid_area_in2(Q_gpm, G, p1_psig, p2_psig, Kd=0.65, Kw=1.0, Kc=1.0, Kv=1.0):
    """A = Q/(38 Kd Kw Kc Kv) sqrt(G/(p1-p2)) [API520 eq. 32]; Kd 0.65 is the API 520 preliminary value for liquid."""
    return Q_gpm/(38*Kd*Kw*Kc*Kv)*math.sqrt(G/(p1_psig-p2_psig))
def gas_C(k): return 520*math.sqrt(k*(2/(k+1))**((k+1)/(k-1)))
def gas_area_in2(W_lb_h, k, P1_psia, T_R, Z, M, Kd=0.975, Kb=1.0, Kc=1.0):
    """Critical flow A = W/(C Kd P1 Kb Kc) sqrt(T Z/M) [API520 eq. 3]; Kd 0.975 is the API 520 preliminary value for gas."""
    return W_lb_h/(gas_C(k)*Kd*P1_psia*Kb*Kc)*math.sqrt(T_R*Z/M)
def equiv_bore_mm(A_in2): return math.sqrt(4*A_in2*IN2_TO_MM2/math.pi)

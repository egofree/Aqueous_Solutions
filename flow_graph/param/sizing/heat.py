"""Heat-transfer sizing [INCROPERA7]: Q = m cp dT; LMTD = (dT1 - dT2)/ln(dT1/dT2); A = Q/(U LMTD)."""
import math
from ..refs import cite
REF = cite('INCROPERA7')
def sensible_W(m_kg_d, cp_kJ_kgK, dT_K): return m_kg_d*cp_kJ_kgK*dT_K/86400*1000
def lmtd(dT1, dT2):
    if dT1<=0 or dT2<=0: return None
    return dT1 if abs(dT1-dT2)<1e-9 else (dT1-dT2)/math.log(dT1/dT2)
def area_m2(Q_W, U, LMTD): return Q_W/(U*LMTD) if LMTD else None
def dittus_boelter_h(Re, Pr, k, d):
    """Turbulent tube flow, heating of the fluid: Nu = 0.023 Re^0.8 Pr^0.4 [INCROPERA7 eq. 8.60]."""
    return 0.023*Re**0.8*Pr**0.4*k/d
def U_series(h_in, h_out, wall_m, k_wall, R_foul=0.0):
    """Overall coefficient, thin wall: 1/U = 1/h_in + t/k + 1/h_out + R_f [INCROPERA7 sec. 11.2]."""
    return 1/(1/h_in + wall_m/k_wall + 1/h_out + R_foul)

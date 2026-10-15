"""Heat-transfer sizing [INCROPERA7]: Q = m cp dT; LMTD = (dT1 - dT2)/ln(dT1/dT2); A = Q/(U LMTD)."""
import math
from ..refs import cite
REF = cite('INCROPERA7')
def sensible_W(m_kg_d, cp_kJ_kgK, dT_K): return m_kg_d*cp_kJ_kgK*dT_K/86400*1000
def lmtd(dT1, dT2):
    if dT1<=0 or dT2<=0: return None
    return dT1 if abs(dT1-dT2)<1e-9 else (dT1-dT2)/math.log(dT1/dT2)
def area_m2(Q_W, U, LMTD): return Q_W/(U*LMTD) if LMTD else None

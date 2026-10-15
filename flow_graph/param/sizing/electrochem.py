"""Electrochemical sizing. Faraday's law: I = m z F / (M t CE)  [CODATA2018 for F; SCHLESINGER2011 for EW practice]."""
import math
from ..constants import F, F_ref
from ..refs import cite
REF = (F_ref, cite('SCHLESINGER2011'))
def faraday_current_A(m_kg_d, M_g_mol, z, ce):
    """Current to deposit m_kg_d of a metal of molar mass M with z electrons at current efficiency ce."""
    return m_kg_d*1000/M_g_mol*z*F/86400/ce
def cathode_count(I_A, j_A_m2, plate_area_both_faces_m2):
    return max(1, math.ceil(I_A/(j_A_m2*plate_area_both_faces_m2)))
def dc_power_kW(I_A, V): return I_A*V/1000

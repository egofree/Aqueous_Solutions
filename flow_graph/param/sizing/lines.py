"""Line sizing by velocity [PERRY9 sec. 6]: d = sqrt(4 Q / (pi v)); smallest standard DN with ID >= d."""
import math
from ..refs import cite
REF = cite('PERRY9')
def min_id_mm(m_kg_s, rho_kg_m3, v_m_s): return math.sqrt(4*m_kg_s/rho_kg_m3/(math.pi*v_m_s))*1000
def pick_dn(id_req_mm, dn_list, id_of, dn_min=15):
    return next(d for d in dn_list if id_of[d]>=id_req_mm and d>=dn_min)

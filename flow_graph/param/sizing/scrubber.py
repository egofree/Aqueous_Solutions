"""Packed scrubber sizing [PERRY9_ABS]. C_s (capacity factor) and HTU are packing inputs: take them from
the packing vendor; the functions do not supply defaults."""
import math
from ..refs import cite
REF = cite('PERRY9_ABS')
def flood_velocity_m_s(Cs_m_s, rho_L, rho_G): return Cs_m_s*math.sqrt((rho_L-rho_G)/rho_G)
def diameter_m(Q_gas_m3_s, u_flood_m_s, frac_flood):
    """D = sqrt(4 Q / (pi f u_f)); f is the design fraction of flood [PERRY9_ABS 0.7-0.8]."""
    return math.sqrt(4*Q_gas_m3_s/(math.pi*frac_flood*u_flood_m_s))
def ntu_irreversible(y_in, y_out): return math.log(y_in/y_out)
def packed_height_m(HTU_m, y_in, y_out): return HTU_m*ntu_irreversible(y_in, y_out)

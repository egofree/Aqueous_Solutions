"""Tank, agitator and pump sizing. Plates and beams [ROARK8]; agitator power [PERRY9_MIX]; pump power [PERRY9_PUMP]."""
import math
from ..refs import cite
from .. import site as SITE
REF = (cite('ROARK8'), cite('PERRY9_MIX'), cite('PERRY9_PUMP'))
G = SITE.g()   # apparent gravity from the site profile
def hydrostatic_MPa(rho, depth_mm): return rho*G*depth_mm*1e-9
def volume_m3(L_mm, W_mm, h_mm): return L_mm*W_mm*h_mm*1e-9
def residence_h(V_m3, Q_m3_d): return V_m3/Q_m3_d*24
def agitator_power_W(Np, rho, N_rps, D_m):
    """Turbulent regime P = Np rho N^3 D^5 [PERRY9_MIX]."""
    return Np*rho*N_rps**3*D_m**5
def long_plate_stress_MPa(q_MPa, b_mm, t_mm, beta=0.75):
    """Long rectangular plate, uniform load, simply supported, a/b > 3: sigma = beta q b^2 / t^2 [ROARK8 table 11.4]."""
    return beta*q_MPa*b_mm**2/t_mm**2
def long_plate_defl_mm(q_MPa, b_mm, t_mm, E_MPa, alpha=0.142):
    """Same plate: y = alpha q b^4 / (E t^3) [ROARK8 table 11.4]."""
    return alpha*q_MPa*b_mm**4/(E_MPa*t_mm**3)
def channel_I_mm4(h, b, tw):
    """Thin channel: web plus two flanges about the strong axis."""
    return tw*h**3/12 + 2*((b-tw)*tw)*(h/2-tw/2)**2
def ss_beam_udl(w_N_mm, L_mm, E_MPa, I_mm4, c_mm):
    """Simply supported, uniform load: M = w L^2/8, sigma = M c / I, y = 5 w L^4 / (384 E I) [ROARK8 table 8.1]."""
    M = w_N_mm*L_mm**2/8
    return dict(M_Nmm=M, sigma_MPa=M*c_mm/I_mm4, defl_mm=5*w_N_mm*L_mm**4/(384*E_MPa*I_mm4))
def pump_shaft_W(rho, Q_m3_s, H_m, eff):
    """P = rho g Q H / eff [PERRY9_PUMP]."""
    return rho*G*Q_m3_s*H_m/eff

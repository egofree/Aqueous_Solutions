"""Packed scrubber sizing [PERRY9_ABS]. C_s (capacity factor) and HTU are packing inputs: take them from
the packing vendor; the functions do not supply defaults."""
import math
from ..refs import cite
from .. import site as SITE
REF = cite('PERRY9_ABS')
def flood_velocity_m_s(Cs_m_s, rho_L, rho_G): return Cs_m_s*math.sqrt((rho_L-rho_G)/rho_G)
def diameter_m(Q_gas_m3_s, u_flood_m_s, frac_flood):
    """D = sqrt(4 Q / (pi f u_f)); f is the design fraction of flood [PERRY9_ABS 0.7-0.8]."""
    return math.sqrt(4*Q_gas_m3_s/(math.pi*frac_flood*u_flood_m_s))
def ntu_irreversible(y_in, y_out): return math.log(y_in/y_out)
def packed_height_m(HTU_m, y_in, y_out): return HTU_m*ntu_irreversible(y_in, y_out)

def min_liquid_m3_h(D_m, a_m2_m3, mwr_m3_m_h):
    """Minimum wetting rate [PERRY9_ABS]: L >= MWR x a x column area (Morris and Jackson rule, 0.08 m3/(m h) for packings below 75 mm)."""
    return mwr_m3_m_h*a_m2_m3*math.pi*D_m**2/4

def fuller_D_m2_s(T_K, P_kPa, MA, MB, VA, VB):
    """Gas diffusivity, Fuller-Schettler-Giddings [PERRY9_DIFF]: D[cm2/s] = 1e-3 T^1.75 sqrt(1/MA+1/MB) / (P[atm] (VA^1/3+VB^1/3)^2)."""
    return 1e-3*T_K**1.75*math.sqrt(1/MA+1/MB)/((P_kPa/101.325)*(VA**(1/3)+VB**(1/3))**2)/1e4

def htu_film_m(G_mol_m2_s, c_mol_m3, D_m2_s, film_m, a_m2_m3):
    """Gas-film HTU at very low gas loading: k_y = c D / film (Fick, stagnant film [TREYBAL3]); HTU = G / (k_y a).
    Used when the gas mass velocity is far below the range of the packed-bed k_G a correlations [PERRY9_ABS]."""
    return G_mol_m2_s/(c_mol_m3*D_m2_s/film_m*a_m2_m3)

def vent_scrubber(feed_kg_d, air_mg_kg, T_vent_C, p_hcl_kPa, psat_vent_kPa, y_out_ppm, htu_m, margin, dp_mm, d_over_dp, a_m2_m3, mwr, excess, naoh_wt):
    """X-PAR-10 vent scrubber on the EVAP_ACID column vent. Non-condensables = air dissolved in the feed [WEISS1970], released in the body and
    vented from the condensing side through a vent condenser at T_vent. The vent leaves saturated with water at T_vent and with HCl at the
    equilibrium partial pressure over the condensate [PERRY7_HCL_VLE]. NaOH absorbs HCl irreversibly, NTU = ln(y_in/y_out) [PERRY9_ABS].
    Diameter from the column-to-packing ratio (wall channelling) [PERRY9_ABS]; liquid recirculation from the minimum wetting rate;
    NaOH bleed = HCl absorbed x excess, as the BMED 2 M base."""
    P = SITE.p_process_kPa(); air_mol = feed_kg_d*air_mg_kg/1e6/28.96*1000          # mol/d; total pressure is the process space (shell interior where the profile states one)
    n_dry = air_mol; y_w = psat_vent_kPa/P; y_h = p_hcl_kPa/P
    n_tot = n_dry/(1 - y_w - y_h); hcl_mol = n_tot*y_h; w_mol = n_tot*y_w
    vent_kg_d = (air_mol*28.96 + w_mol*18.015 + hcl_mol*36.461)/1000
    y_in = y_h*1e6; ntu = ntu_irreversible(y_in, y_out_ppm) if y_in > y_out_ppm else 0.0
    D = dp_mm*d_over_dp/1000
    if htu_m is None:   # film model: HCl in air, Fuller volumes H 2.31 + Cl 21.0, air 19.7 [PERRY9_DIFF]; film = half the packing size
        T = T_vent_C + 273.15; Dg = fuller_D_m2_s(T, P, 36.461, 28.96, 23.31, 19.7)
        htu_m = htu_film_m(n_tot/86400/(math.pi*D**2/4), P*1000/(8.314*T), Dg, dp_mm/2000, a_m2_m3)
    Z = max(htu_m*ntu*margin, 0.5)                                        # 0.5 m minimum bed (one distributor and support stage)
    Lmin = min_liquid_m3_h(D, a_m2_m3, mwr)
    naoh_mol = hcl_mol*excess; naoh_kg_d = naoh_mol*40.0/1000/naoh_wt     # as 2 M base solution
    Q_m3_h = n_tot/24*0.0224*(273.15+T_vent_C)/273.15
    return dict(htu_m=htu_m, air_mol_d=air_mol, vent_mol_d=n_tot, vent_kg_d=vent_kg_d, hcl_in_mol_d=hcl_mol, hcl_in_kg_d=hcl_mol*36.461/1000, y_in_ppm=y_in,
                y_out_ppm=y_out_ppm, ntu=ntu, packed_m=Z, D_m=D, gas_m3_h=Q_m3_h, u_gas_m_s=Q_m3_h/3600/(math.pi*D**2/4), recirc_m3_h=Lmin,
                naoh_mol_d=naoh_mol, naoh_soln_kg_d=naoh_kg_d, spent_kg_d=naoh_kg_d + hcl_mol*36.461/1000,
                offgas_kg_d=vent_kg_d - hcl_mol*36.461/1000 + hcl_mol*y_out_ppm/y_in*36.461/1000 if y_in else vent_kg_d)

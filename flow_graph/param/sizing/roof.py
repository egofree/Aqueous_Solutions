"""Roof PV and building-extension loads (X-PAR-07).
Roof PV layout: perimeter pathway 1219 mm when both building axes <= 76.2 m (250 ft), else 1829 mm; arrays no larger than
45.72 m (150 ft) in either axis with 1219 mm pathways between them [IFC2027_1205, NFPA1_2027_11_12].
Array power = array area x module STC efficiency x 1 kW/m2 x ground-cover ratio [NREL_PVWATTS8].
Extension loads on the added floor area (single-storey extension):
  lighting  = LPD x area x lit fraction (occupant-sensor control, IECC 2021 C405.2.1) [IECC2021_C405]
  ventilation = Ra x area x rho cp x dT_mean / COP + Ra x area x SFP [ASHRAE621_2019, ISO16798_3]
  envelope  = (U_roof x added roof + U_wall x full new perimeter wall, bounding) x dT_mean / COP [IECC2021_C402]; slab and internal gains not counted
Roof structural load = PV dead + max(roof live, snow) with ASCE 7-22 LRFD 1.2D + 1.6(Lr or S) [ASCE7_22]."""
import math
from ..refs import cite
REF = tuple(cite(k) for k in ('IFC2027_1205','NFPA1_2027_11_12','NREL_PVWATTS8','IECC2021_C405','ASHRAE621_2019','ISO16798_3','IECC2021_C402','ASCE7_22'))
def _segments(L_mm, max_mm, path_mm):
    """Split a clear length into arrays no longer than max_mm separated by path_mm; returns array length total."""
    n = max(1, math.ceil((L_mm + path_mm)/(max_mm + path_mm)))
    return L_mm - (n-1)*path_mm, n
def array_area_m2(W_mm, D_mm, perim_small, perim_large, axis_limit, arr_max, path):
    p = perim_small if max(W_mm, D_mm) <= axis_limit else perim_large
    lx, nx = _segments(W_mm - 2*p, arr_max, path); ly, ny = _segments(D_mm - 2*p, arr_max, path)
    return max(0, lx)*max(0, ly)/1e6, dict(perimeter_mm=p, arrays=nx*ny, arrays_x=nx, arrays_y=ny)
def roof_kWp(area_m2, eff, gcr): return area_m2*eff*gcr
def extension_kW(A_add_m2, lpd_W_m2, light_frac, Ra_L_s_m2, dT_K, cop, sfp_W_per_L_s, U_roof, conditioned=1.0, A_wall_m2=0.0, U_wall=0.0):
    """conditioned 0: unconditioned hall (mechanical ventilation fans only, no heating or cooling of the air or envelope)."""
    vent_L_s = Ra_L_s_m2*A_add_m2
    light = lpd_W_m2*A_add_m2*light_frac/1000
    vent = (conditioned*vent_L_s/1000*1.2*1006*dT_K/cop + vent_L_s*sfp_W_per_L_s)/1000
    env = conditioned*(U_roof*A_add_m2 + U_wall*A_wall_m2)*dT_K/cop/1000
    return dict(light_kW=light, vent_kW=vent, envelope_kW=env, total_kW=light+vent+env, vent_L_s=vent_L_s)
def roof_load_kPa(pv_dead, Lr, S):
    return dict(service_kPa=pv_dead+max(Lr, S), lrfd_kPa=1.2*pv_dead+1.6*max(Lr, S))

def extension_kW_v2(A_add_m2, lpd_W_m2, light_frac, Ra_L_s_m2, dTh_K, dTc_K, cop_h, cop_c, sfp_W_per_L_s, U_roof, A_wall_m2, U_wall,
                    F_slab_W_mK, P_slab_m, pump_W_per_kWt=0.0, conditioned=1.0):
    """X-PAR-08. Heating and cooling split by degree days [NOAA_NORMALS_DFW]: mean heating dT = HDD/365, cooling dT = CDD/365 (K).
    Conduction UA = roof + walls [IECC2021_C402]; slab-on-grade edge loss F x perimeter [IECC2021_C402 Table C402.1.4, F-factor] in the
    heating season only (no cooling credit, conservative). Outdoor air rho cp V [ASHRAE621_2019]. Internal gains = lighting and fan power
    (all ends as heat); they offset heating and add to cooling in proportion to the heating and cooling dT shares (balance-point study
    method, ASHRAE_FUND_2021 ch. 18). Electric = Q_h/COP_h + Q_c/COP_c (+ ground-loop pumping per kW thermal) + fans + lighting.
    Occupant and process gains are not counted (hall programme open)."""
    vent_L_s = Ra_L_s_m2*A_add_m2; UAv = vent_L_s/1000*1.2*1006
    UAe = U_roof*A_add_m2 + U_wall*A_wall_m2; UAs = F_slab_W_mK*P_slab_m
    light = lpd_W_m2*A_add_m2*light_frac; fan = vent_L_s*sfp_W_per_L_s; G = light + fan
    fh = dTh_K/(dTh_K+dTc_K); fc = 1 - fh
    Qh = max(0.0, (UAe+UAv+UAs)*dTh_K - G*fh)*conditioned; Qc = ((UAe+UAv)*dTc_K + G*fc)*conditioned
    pump = pump_W_per_kWt*(Qh+Qc)/1000
    hvac = Qh/cop_h + Qc/cop_c + pump
    return dict(light_kW=light/1000, vent_kW=(fan + UAv*(dTh_K/cop_h + dTc_K/cop_c)*conditioned)/1000, envelope_kW=(hvac - UAv*(dTh_K/cop_h + dTc_K/cop_c)*conditioned)/1000,
                total_kW=(light+fan+hvac)/1000, vent_L_s=vent_L_s, Qh_kW=Qh/1000, Qc_kW=Qc/1000, slab_kW=UAs*dTh_K/1000, gains_kW=G/1000, pump_kW=pump/1000)

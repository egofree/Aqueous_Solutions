"""Roof PV and building-extension loads (X-PAR-07).
Roof PV layout: perimeter pathway 1219 mm when both building axes <= 76.2 m (250 ft), else 1829 mm; arrays no larger than
45.72 m (150 ft) in either axis with 1219 mm pathways between them [IFC2021_1205, NFPA1_2021_11_12].
Array power = array area x module STC efficiency x 1 kW/m2 x ground-cover ratio [NREL_PVWATTS8].
Extension loads on the added floor area (single-storey extension):
  lighting  = LPD x area x lit fraction (occupant-sensor control, IECC 2021 C405.2.1) [IECC2021_C405]
  ventilation = Ra x area x rho cp x dT_mean / COP + Ra x area x SFP [ASHRAE621_2019, ISO16798_3]
  envelope  = U_roof x roof area x dT_mean / COP [IECC2021_C402]
Roof structural load = PV dead + max(roof live, snow) with ASCE 7-22 LRFD 1.2D + 1.6(Lr or S) [ASCE7_22]."""
import math
from ..refs import cite
REF = tuple(cite(k) for k in ('IFC2021_1205','NFPA1_2021_11_12','NREL_PVWATTS8','IECC2021_C405','ASHRAE621_2019','ISO16798_3','IECC2021_C402','ASCE7_22'))
def _segments(L_mm, max_mm, path_mm):
    """Split a clear length into arrays no longer than max_mm separated by path_mm; returns array length total."""
    n = max(1, math.ceil((L_mm + path_mm)/(max_mm + path_mm)))
    return L_mm - (n-1)*path_mm, n
def array_area_m2(W_mm, D_mm, perim_small, perim_large, axis_limit, arr_max, path):
    p = perim_small if max(W_mm, D_mm) <= axis_limit else perim_large
    lx, nx = _segments(W_mm - 2*p, arr_max, path); ly, ny = _segments(D_mm - 2*p, arr_max, path)
    return max(0, lx)*max(0, ly)/1e6, dict(perimeter_mm=p, arrays=nx*ny, arrays_x=nx, arrays_y=ny)
def roof_kWp(area_m2, eff, gcr): return area_m2*eff*gcr
def extension_kW(A_add_m2, lpd_W_m2, light_frac, Ra_L_s_m2, dT_K, cop, sfp_W_per_L_s, U_roof, conditioned=1.0):
    """conditioned 0: unconditioned hall (mechanical ventilation fans only, no heating or cooling of the air or envelope)."""
    vent_L_s = Ra_L_s_m2*A_add_m2
    light = lpd_W_m2*A_add_m2*light_frac/1000
    vent = (conditioned*vent_L_s/1000*1.2*1006*dT_K/cop + vent_L_s*sfp_W_per_L_s)/1000
    env = conditioned*U_roof*A_add_m2*dT_K/cop/1000
    return dict(light_kW=light, vent_kW=vent, envelope_kW=env, total_kW=light+vent+env, vent_L_s=vent_L_s)
def roof_load_kPa(pv_dead, Lr, S):
    return dict(service_kPa=pv_dead+max(Lr, S), lrfd_kPa=1.2*pv_dead+1.6*max(Lr, S))

"""PV and storage sizing. PV kWp = (E_day_direct + E_night/eta_rt) / (yield x derate) [NREL_PVWATTS for yield].
Overcurrent devices at 125 % of continuous current [NEC2023]."""
import math
from ..refs import cite
REF = (cite('NREL_PVWATTS'), cite('NEC2023'))
def pv_kWp(P_kW, night_h, eta_rt, yield_kWh_kWp_d, derate):
    return (P_kW*(24-night_h)+P_kW*night_h/eta_rt)/(yield_kWh_kWp_d*derate)
def amps_3ph(kW, V, pf): return kW*1000/(math.sqrt(3)*V*pf)
def breaker(a, std, factor=1.25): return next(b for b in std if b>=factor*a)
def rectifier_channel(I_A, V_cell, V_drop, eff, frames, margin, V_rated):
    """DC rectifier channel: P_dc = I (V_cell + V_drop); P_ac = P_dc / eff; frame = smallest standard >= margin x I.
    Cell voltage and current efficiency basis USBM_CL_EW (chloride EW)."""
    need = I_A*margin; rate = next(s for s in frames if s >= need)
    Pdc = I_A*(V_cell+V_drop)/1000
    return dict(need_A=need, rated_A=rate, rated_kW=rate*V_rated/1000, Pdc_kW=Pdc, Pac_kW=Pdc/eff)

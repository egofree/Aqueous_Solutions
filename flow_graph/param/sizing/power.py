"""PV and storage sizing. PV kWp = (E_day_direct + E_night/eta_rt) / (yield x derate) [NREL_PVWATTS for yield].
Overcurrent devices at 125 % of continuous current [NEC2023]."""
import math
from ..refs import cite
REF = (cite('NREL_PVWATTS'), cite('NEC2023'))
def pv_kWp(P_kW, night_h, eta_rt, yield_kWh_kWp_d, derate):
    return (P_kW*(24-night_h)+P_kW*night_h/eta_rt)/(yield_kWh_kWp_d*derate)
def amps_3ph(kW, V, pf): return kW*1000/(math.sqrt(3)*V*pf)
def breaker(a, std, factor=1.25): return next(b for b in std if b>=factor*a)

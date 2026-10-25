"""PV and storage sizing. PV kWp = (E_day_direct + E_night/eta_rt) / (yield x derate) [NREL_PVWATTS for yield].
Overcurrent devices at 125 % of continuous current [NEC2026]."""
import math
from ..refs import cite
REF = (cite('NREL_PVWATTS'), cite('NEC2026'))
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
def oversized(P_kW, night_h, eta_rt, yield_kWh_kWp_d, derate, factor, dc_ac, inv_unit_kW):
    """D75 (owner, 2026-10-15): PV at `factor` x the nameplate that closes the daily balance (pv_kWp).
    Design cloudy day: daily yield = mean / factor. On that day the array delivers exactly the energy of the
    un-oversized array, so the storage still fills (night energy / round trip).
    Charge rate: PV peak on the cloudy day (PVWatts hourly model scales with plane-of-array irradiance, NREL_PVWATTS8)
    less the direct load: kWp x derate / factor - P. Discharge rate: P. Storage energy: P x night_h.
    Inverter AC: kWp / dc_ac (PVWatts default ratio) and not less than P. Clear-day export at noon: inverter AC - P
    when storage is full. Clear-day surplus energy exported: (factor - 1) x the balancing energy."""
    base = pv_kWp(P_kW, night_h, eta_rt, yield_kWh_kWp_d, derate); kwp = factor*base
    charge = max(kwp*derate/factor - P_kW, 0.0)
    inv_ac = max(kwp/dc_ac, P_kW); n = math.ceil(inv_ac/inv_unit_kW)
    E_bal = base*yield_kWh_kWp_d*derate
    return dict(pv_base_kWp=base, pv_kWp=kwp, store_kWh=P_kW*night_h, discharge_kW=P_kW, charge_kW=charge,
                store_kW=max(P_kW, charge), store_in_kWh=P_kW*night_h/eta_rt, inverters=n, inv_kW=n*inv_unit_kW,
                export_peak_kW=n*inv_unit_kW - P_kW, export_kWh_d_clear=(factor-1)*E_bal, cloudy_yield_frac=1/factor)

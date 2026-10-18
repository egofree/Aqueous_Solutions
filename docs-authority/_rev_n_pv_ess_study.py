"""AQS-DUTY-012 Rev A, WP-PV-ESS part 1: hourly PV DC output from a typical meteorological year.

Inputs : data/pvgis_tmy_33.0_-96.8.csv (PVGIS 5.2 TMY, radiation PVGIS-NSRDB 2005-2015, meteo ERA5;
         https://re.jrc.ec.europa.eu/api/v5_2/tmy?lat=33.0&lon=-96.8&outputformat=json, retrieved 2026-10-08).
Site   : SITE_LAT 33.0 (params.py sandbox, "Dallas-class"); longitude -96.8 taken for the Dallas-class theme.
Model  : pvlib-python (Holmgren et al. 2018, https://doi.org/10.21105/joss.00884).
         Perez transposition, fixed tilt = latitude (33 deg), azimuth 180 deg (SITE_ACCESS: roof tilt latitude, equator face),
         albedo 0.20; SAPM cell temperature, open rack glass/polymer; PVWatts DC model, gamma_pdc -0.0037 /K and
         system losses 14.08 % (PVWatts default; Dobos 2014, NREL/TP-6A20-62641, https://docs.nrel.gov/docs/fy14osti/62641.pdf).
         Inverter loss is not applied here: the Sol-Ark conversion loss is booked on the bus (AQS-DUTY-011).
Output : data/pv_hourly_tmy_33.0_-96.8.csv (per hour: month, day, local standard hour, P_dc kW for the 70 kWp array)
         data/pv_tmy_summary.json (monthly mean daily kWh, annual yield, worst month).
Requires pvlib and pandas; the closure script (_rev_n_corrections_study.py) reads only the CSV/JSON outputs.
Run    : python3 _rev_n_pv_ess_study.py
"""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
LAT, LON, ALT = 33.0, -96.8, 204.0
TILT, AZ, ALBEDO = 33.0, 180.0, 0.20
P_KWP = 70.0
GAMMA = -0.0037
LOSSES = 0.1408
TMY = os.path.join(HERE, "data", "pvgis_tmy_33.0_-96.8.csv")
OUT_CSV = os.path.join(HERE, "data", "pv_hourly_tmy_33.0_-96.8.csv")
OUT_JSON = os.path.join(HERE, "data", "pv_tmy_summary.json")
UTC_OFFSET_H = -6           # local standard time (CST)


def main():
    import pandas as pd
    import pvlib
    df = pd.read_csv(TMY)
    # TMY months come from different years; re-stamp on a non-leap nominal year, keeping month/day/hour (UTC)
    t = pd.to_datetime("2019" + df["time_utc"].str[4:], format="%Y%m%d:%H%M", utc=True)
    df.index = t
    df = df.sort_index()
    loc = pvlib.location.Location(LAT, LON, altitude=ALT, tz="UTC")
    # irradiance values are hourly averages stamped at the start of the hour: evaluate the sun at mid-hour
    tm = df.index + pd.Timedelta(minutes=30)
    sp = loc.get_solarposition(tm)
    sp.index = df.index
    dni_extra = pvlib.irradiance.get_extra_radiation(df.index)
    am = pvlib.atmosphere.get_relative_airmass(sp["apparent_zenith"])
    poa = pvlib.irradiance.get_total_irradiance(TILT, AZ, sp["apparent_zenith"], sp["azimuth"], df["DNI_W_m2"], df["GHI_W_m2"], df["DHI_W_m2"],
                                                dni_extra=dni_extra, airmass=am, albedo=ALBEDO, model="perez")
    poa_g = poa["poa_global"].fillna(0.0).clip(lower=0.0)
    prm = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS["sapm"]["open_rack_glass_polymer"]
    tc = pvlib.temperature.sapm_cell(poa_g, df["T2m_C"], df["WS10m_m_s"], **prm)
    pdc = pvlib.pvsystem.pvwatts_dc(poa_g, tc, P_KWP, GAMMA) * (1 - LOSSES)
    pdc = pdc.clip(lower=0.0)
    loc_t = df.index + pd.Timedelta(hours=UTC_OFFSET_H)
    rows = []
    for ts, lt, p in zip(df.index, loc_t, pdc.values):
        rows.append((lt.month, lt.day, lt.hour, round(float(p), 4)))
    rows.sort()
    with open(OUT_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["month_local", "day_local", "hour_local_standard", "p_dc_kw"])
        w.writerows(rows)
    mon = {}
    for m, d, h, p in rows:
        mon.setdefault(m, {}).setdefault(d, 0.0)
        mon[m][d] += p
    monthly = {m: dict(days=len(v), mean_daily_kwh=round(sum(v.values()) / len(v), 2), mean_kw=round(sum(v.values()) / len(v) / 24, 3),
                       min_daily_kwh=round(min(v.values()), 2)) for m, v in sorted(mon.items())}
    annual = sum(p for *_, p in rows)
    worst = min(monthly, key=lambda m: monthly[m]["mean_daily_kwh"])
    poa_m = {}
    for ts, g in zip(loc_t, poa_g.values):
        poa_m.setdefault(ts.month, 0.0)
        poa_m[ts.month] += g / 1000.0
    summ = dict(doc="AQS-DUTY-012 WP-PV-ESS", site=dict(lat=LAT, lon=LON, alt_m=ALT), array=dict(kwp=P_KWP, tilt=TILT, azimuth=AZ, albedo=ALBEDO),
                model="pvlib %s: Perez, SAPM open_rack_glass_polymer, PVWatts DC gamma %.4f, losses %.2f %%" % (pvlib.__version__, GAMMA, LOSSES * 100),
                annual_kwh=round(annual, 0), annual_kwh_per_kwp=round(annual / P_KWP, 1), annual_mean_kw=round(annual / 8760, 3),
                monthly=monthly, worst_month=worst, worst_month_mean_kw=monthly[worst]["mean_kw"],
                poa_kwh_m2_month={m: round(v, 1) for m, v in sorted(poa_m.items())}, peak_dc_kw=round(max(p for *_, p in rows), 2))
    json.dump(summ, open(OUT_JSON, "w"), indent=1)
    return summ


if __name__ == "__main__":
    s = main()
    print(json.dumps({k: s[k] for k in ("annual_kwh", "annual_kwh_per_kwp", "annual_mean_kw", "worst_month", "worst_month_mean_kw", "peak_dc_kw")}, indent=1))
    for m, v in s["monthly"].items():
        print(m, v)

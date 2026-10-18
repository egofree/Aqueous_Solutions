#!/usr/bin/env python3
# SPDX-License-Identifier: CERN-OHL-S-2.0
"""AQS-DUTY-008 heat-ladder edge study (HL-* and S67B).

First-principles duties, media, temperatures, flows and line sizes for the
21 edges that carried presence "study" through Rev H. Inputs are graph values
and issued envelopes; every other number is an assumption stated in A_* below.
Rev J (AQS-DUTY-008 Rev B) adds main_j(): HX-8 on Q4, Q3 draws HX-4/5/6, re-rated Q3/Q4.
Rev K (AQS-DUTY-008 Rev C) adds main_k(): thermosyphon static head vs loop pressure drop at the
placed store elevations, stepped store elevations for the downhill steps, pumped cross-ties.
Run: python3 _hl_edges_study.py [--json out.json] [--rev-j | --rev-k]
"""
from __future__ import annotations
import json, math, sys

# ---------------------------------------------------------------- inputs (graph / docs)
CO2_AB_KG_D = 15.0          # afterburner flue CO2 (S67 basis since Rev J; was S18), AQS-AUD-001 mid of 12-22.5 kg/d
CULLET_KG_D = 30.0          # S08G silicate + grit, AQS-AUD-001 s4.1, reference feed at 150 kg/d wet, AQS-ASSAY-001
BURNOUT_KW_E = 1.0          # GLASS_BURNOUT issued duty (electric)
T_AMB = 25.0

# ---------------------------------------------------------------- assumptions
# NCG mass mix, polyolefin pyrolysis gas class (C1-C4). LHV MJ/kg, carbon mass fraction.
NCG = {"CH4": (0.25, 50.0, 12/16), "C2H4": (0.25, 47.2, 24/28), "C2H6": (0.10, 47.5, 24/30),
       "C3H6": (0.25, 45.8, 36/42), "C3H8": (0.15, 46.4, 36/44)}
A_AB_SHELL = 0.05           # afterburner casing loss, fraction of release
A_T_AB = 850.0              # oxidizer exit, 850 C / 2 s class
A_T_HX7 = 650.0             # flue leaving HX-7 burnout jacket (burnout 450-550 C, 100 K approach)
A_T_Q1X = 300.0             # flue leaving Q1 exchanger (Q1 store 250 C + 50 K gas-side approach)
A_CP_FLUE = 1.13            # kJ/kg K, lean flue 25-850 C
A_CP_GLASS = 0.95           # kJ/kg K, soda-lime 25-500 C
A_T_BURN = 500.0            # burnout bed, mid of 450-550 C
A_T_CULLET_OUT = 170.0      # cullet cooler exit, Q2 oil return 150 C + 20 K
A_ROT_AREA = 1.10           # m2, rotary tube + ends behind the Q2 jacket
A_ROT_INS = (0.050, 0.08)   # m, W/m K mineral wool between process wall and Q2 oil jacket
A_T_Q2_JACKET = 140.0       # mean Q2 jacket oil
A_BURN_OFFGAS_KW = 0.03     # sweep + volatiles sensible to the oil-vapor header
A_BURN_END_KW = 0.05        # trunnion and end-plate loss to room
A_MARGIN = 1.25             # rated / governing duty
A_HP_LOSS = 0.03            # loop thermosyphon line loss, fraction of transferred duty
A_H_OUT = 10.0              # W/m2 K outer film, still air
A_V_LIQ = 1.0               # m/s velocity basis, pumped liquid
A_V_VAP = 10.0              # m/s velocity basis, thermosyphon vapor
A_DN_MIN = 15               # mechanical minimum line
A_L_DOWN = 6.0              # m equivalent length, tier to tier
A_L_X = 25.0                # m equivalent length, ladder A to ladder B across the core
A_RISE = 0.8                # m, evaporator (low in source store) to condenser (high in sink store)
A_CAPTURE_REC = 0.85        # VSA 13X CO2 recovery at FLUE_KO
A_CAPTURE_PUR = 0.90        # mol CO2 in the cut
A_P_CUT = 1.30e5            # Pa abs, VSA product
A_T_CUT = 30.0
A_V_GAS = 10.0

PIPE_ID_MM = {15: 15.80, 20: 20.93, 25: 26.64, 32: 35.05, 40: 40.89, 50: 52.50, 65: 62.71, 80: 77.93}

# Battery geometry (store volume from graph; envelope 800 x 800 x 1200 issued)
# (vol_m3, T_nom, inner dims (shape, a, b, h), side insulation t, k)
STORES = {
    "Q1": (0.30, 250.0, ("cyl", 0.62, 0.62, 1.00), 0.090, 0.025, "microporous"),
    "Q2": (0.30, 150.0, ("cyl", 0.62, 0.62, 1.00), 0.090, 0.025, "microporous"),
    "Q3": (0.40, 100.0, ("box", 0.68, 0.68, 0.88), 0.060, 0.035, "mineral wool"),
    "Q4": (0.60, 70.0, ("box", 0.74, 0.74, 1.10), 0.030, 0.025, "PIR"),
}
ENVELOPE = (0.80, 0.80, 1.20)

# Fluids. Liquid: rho, cp. Two-phase: T_sat, P_sat (Pa), h_fg (kJ/kg), rho_l, rho_v, mu_v (Pa s), mu_l
OIL_Q1 = dict(name="synthetic thermal oil, hydrogenated terphenyl class", rho=870.0, cp=2.30, mu=0.6e-3, beta=8.5e-4)
OIL_Q2 = dict(name="synthetic thermal oil, hydrogenated terphenyl class", rho=930.0, cp=2.00, mu=1.5e-3, beta=8.0e-4)
WATER_Q4 = dict(name="treated water (Q4 water header)", rho=985.0, cp=4.18, mu=0.5e-3, beta=5.0e-4)
TP = {
    "DA_200": dict(name="biphenyl/diphenyl-oxide eutectic (Dowtherm A class)", T=200.0, P=0.25e5, hfg=310.0, rl=910.0, M=0.166, mu_v=1.0e-5, mu_l=0.45e-3),
    "DA_245": dict(name="biphenyl/diphenyl-oxide eutectic (Dowtherm A class)", T=245.0, P=0.78e5, hfg=290.0, rl=870.0, M=0.166, mu_v=1.1e-5, mu_l=0.33e-3),
    "W_145": dict(name="water (deaerated, steel loop)", T=145.0, P=4.15e5, hfg=2133.0, rl=922.0, M=0.018, mu_v=1.4e-5, mu_l=0.19e-3),
    "W_125": dict(name="water (deaerated, steel loop)", T=125.0, P=2.32e5, hfg=2188.0, rl=939.0, M=0.018, mu_v=1.3e-5, mu_l=0.22e-3),
    "W_95": dict(name="water (deaerated, copper loop)", T=95.0, P=0.845e5, hfg=2270.0, rl=962.0, M=0.018, mu_v=1.2e-5, mu_l=0.30e-3),
    "W_85": dict(name="water (deaerated, copper loop)", T=85.0, P=0.578e5, hfg=2296.0, rl=968.0, M=0.018, mu_v=1.15e-5, mu_l=0.33e-3),
    "W_65": dict(name="water (deaerated, copper loop)", T=65.0, P=0.250e5, hfg=2346.0, rl=980.0, M=0.018, mu_v=1.1e-5, mu_l=0.43e-3),
}
R = 8.314
# Saturation pressure at the source store's maximum (nominal + 10 %): sealed-loop design pressure basis
PSAT_MAX = {"DA_200": (275.0, 1.45), "DA_245": (275.0, 1.45), "W_145": (165.0, 7.0), "W_125": (165.0, 7.0),
            "W_95": (110.0, 1.43), "W_85": (110.0, 1.43), "W_65": (77.0, 0.42)}


def kw(x):
    return round(x, 3)


def area_id(dn):
    return math.pi * (PIPE_ID_MM[dn] / 1000) ** 2 / 4


def pick_dn(q_m3s, v):
    for dn in sorted(PIPE_ID_MM):
        if dn < A_DN_MIN:
            continue
        if q_m3s / area_id(dn) <= v:
            return dn
    raise SystemExit("line out of table")


def dp_darcy(m, rho, mu, dn, L):
    d = PIPE_ID_MM[dn] / 1000
    v = m / rho / area_id(dn)
    Re = rho * v * d / mu
    f = 64 / Re if Re < 2300 else 0.316 * Re ** -0.25
    return f * L / d * rho * v * v / 2, v, Re


def store_loss(tier):
    vol, T, (shape, a, b, h), t, k, mat = STORES[tier]
    if shape == "cyl":
        vin = math.pi * a * a / 4 * h
        a_in = math.pi * a * h + 2 * math.pi * a * a / 4
        do, ho = a + 2 * t, min(ENVELOPE[2], h + 2 * 0.10)
        a_out = math.pi * do * ho + 2 * math.pi * do * do / 4
    else:
        vin = a * b * h
        a_in = 2 * (a * b + a * h + b * h)
        ao, bo, ho = a + 2 * t, b + 2 * t, ENVELOPE[2]
        a_out = 2 * (ao * bo + ao * ho + bo * ho)
    fits = (a + 2 * t) <= ENVELOPE[0] + 1e-9
    U = 1 / (t / k + 1 / A_H_OUT)
    Am = (a_in + a_out) / 2
    return dict(tier=tier, vol_m3=round(vin, 3), vol_issued_m3=vol, T_C=T, insulation=mat, t_mm=t * 1000, k=k,
                U=round(U, 3), A_m2=round(Am, 2), loss_kw=kw(U * Am * (T - T_AMB) / 1000), fits_envelope=fits)


# ---------------------------------------------------------------- sources
def ncg():
    lhv = sum(w * l for w, l, c in NCG.values())
    co2 = sum(w * c * 44 / 12 for w, l, c in NCG.values())
    return lhv, co2, lhv / co2


def sources():
    lhv, co2_per_kg, e_co2 = ncg()
    fuel_kg_d = CO2_AB_KG_D / co2_per_kg
    q_rel = CO2_AB_KG_D * e_co2 * 1000 / 86400          # kW
    q_shell = A_AB_SHELL * q_rel
    m_flue = (q_rel - q_shell) / (A_CP_FLUE * (A_T_AB - T_AMB))   # kg/s
    C = m_flue * A_CP_FLUE                                 # kW/K
    q_hx7 = C * (A_T_AB - A_T_HX7)
    q_q1 = C * (A_T_HX7 - A_T_Q1X)
    q_ko = C * (A_T_Q1X - T_AMB)
    ab = dict(lhv_MJ_kg=round(lhv, 2), co2_kg_per_kg_fuel=round(co2_per_kg, 3), e_MJ_per_kg_co2=round(e_co2, 2),
              fuel_kg_d=round(fuel_kg_d, 2), q_release_kw=kw(q_rel), q_shell_kw=kw(q_shell),
              m_flue_kg_h=round(m_flue * 3600, 2), q_hx7_kw=kw(q_hx7), q_q1_kw=kw(q_q1), q_flue_to_ko_kw=kw(q_ko),
              closure_kw=kw(q_rel - q_shell - q_hx7 - q_q1 - q_ko))
    mc = CULLET_KG_D / 86400
    q_cullet_heat = mc * A_CP_GLASS * (A_T_BURN - T_AMB)
    q_cullet_rec = mc * A_CP_GLASS * (A_T_BURN - A_T_CULLET_OUT)
    q_jacket = A_ROT_AREA * A_ROT_INS[1] / A_ROT_INS[0] * (A_T_BURN - A_T_Q2_JACKET) / 1000
    q_q2 = q_cullet_rec + q_jacket
    need = q_cullet_heat + q_jacket + A_BURN_OFFGAS_KW + A_BURN_END_KW
    trim = need - q_hx7
    bo = dict(cullet_kg_d=CULLET_KG_D, q_cullet_heat_kw=kw(q_cullet_heat), q_cullet_recovered_kw=kw(q_cullet_rec),
              q_jacket_kw=kw(q_jacket), q_to_q2_kw=kw(q_q2), q_offgas_kw=A_BURN_OFFGAS_KW, q_end_kw=A_BURN_END_KW,
              q_hx7_in_kw=kw(q_hx7), q_trim_electric_kw=kw(trim), q_cullet_residual_kw=kw(q_cullet_heat - q_cullet_rec),
              electric_within_issued=trim <= BURNOUT_KW_E)
    return ab, bo, q_q1, q_q2


# ---------------------------------------------------------------- ladder balance
def ladder(q1_src, q2_src, losses, split):
    """split = fractions of each source to (A, B); returns per-ladder tier flows."""
    out = {}
    for i, lad in enumerate("AB"):
        f = split[i]
        if f == 0:
            out[lad] = None
            continue
        r = {}
        q_in1 = q1_src * f
        d1 = (q_in1 - losses["Q1"])
        r["Q1"] = dict(src=q_in1, from_above=0.0, loss=losses["Q1"], down=d1)
        d1n = d1 * (1 - A_HP_LOSS)
        q_in2 = d1n + q2_src * f
        d2 = q_in2 - losses["Q2"]
        r["Q2"] = dict(src=q2_src * f, from_above=d1n, hp_loss=d1 - d1n, loss=losses["Q2"], down=d2)
        d2n = d2 * (1 - A_HP_LOSS)
        q_in3 = d2n  # HX-8 contributes 0 at the Q3 set point (see study)
        d3 = q_in3 - losses["Q3"]
        r["Q3"] = dict(src=0.0, from_above=d2n, hp_loss=d2 - d2n, loss=losses["Q3"], down=d3)
        d3n = d3 * (1 - A_HP_LOSS)
        bus = d3n - losses["Q4"]
        r["Q4"] = dict(src=0.0, from_above=d3n, hp_loss=d3 - d3n, loss=losses["Q4"], down=bus)
        out[lad] = r
    return out


def closure(q1_src, q2_src, res, losses, idle_losses=0.0):
    src = q1_src + q2_src
    sinks = 0.0
    for lad, r in res.items():
        if r is None:
            continue
        sinks += r["Q4"]["down"]
        sinks += sum(r[t]["loss"] for t in r) + sum(r[t].get("hp_loss", 0.0) for t in r)
    return src, sinks, src - sinks


# ---------------------------------------------------------------- edges
def pumped(q_kw, fl, t_sup, t_ret):
    dT = abs(t_ret - t_sup)
    m = q_kw / (fl["cp"] * dT)
    qv = m / fl["rho"]
    dn = pick_dn(qv, A_V_LIQ)
    v = qv / area_id(dn)
    relief = fl["beta"] * q_kw * 1000 / (fl["rho"] * fl["cp"] * 1000)  # m3/s blocked-in expansion
    return dict(kind="pumped loop", medium=fl["name"], supply_C=t_sup, return_C=t_ret, dT_K=dT,
                m_kg_s=round(m, 5), flow_L_min=round(qv * 60000, 2), line_DN=dn,
                line_id_mm=PIPE_ID_MM[dn], velocity_m_s=round(v, 3), velocity_basis_m_s=A_V_LIQ,
                thermal_relief_L_h=round(relief * 3.6e6, 4))


def twophase(q_kw, key, L):
    f = TP[key]
    rho_v = f["P"] * f["M"] / (R * (f["T"] + 273.15))
    m = q_kw / f["hfg"]
    qv = m / rho_v
    head = f["rl"] * 9.81 * A_RISE
    dpl, vl, Rel = dp_darcy(m, f["rl"], f["mu_l"], 15, L)
    dn = pick_dn(qv, A_V_VAP)
    while True:
        dpv, vv, Rev = dp_darcy(m, rho_v, f["mu_v"], dn, L)
        if dpv + dpl < 0.5 * head:
            break
        dn = min(d for d in PIPE_ID_MM if d > dn)
    return dict(kind="loop thermosyphon (vapor riser + condensate return with check)", medium=f["name"],
                supply_C=f["T"], return_C=f["T"] - 5.0, P_sat_bar_a=round(f["P"] / 1e5, 3), h_fg_kJ_kg=f["hfg"],
                m_kg_s=round(m, 6), vapor_m3_h=round(qv * 3600, 3), line_DN=dn, line_id_mm=PIPE_ID_MM[dn],
                velocity_m_s=round(vv, 2), velocity_basis_m_s=A_V_VAP, return_DN=15, L_eq_m=L,
                dp_vapor_Pa=round(dpv, 1), dp_liquid_Pa=round(dpl, 2), head_Pa=round(head, 0),
                dp_ok=(dpv + dpl) < 0.5 * head, T_blocked_C=PSAT_MAX[key][0], P_blocked_bar_a=PSAT_MAX[key][1])


def main():
    ab, bo, q1_src, q2_src = sources()
    stores = {t: store_loss(t) for t in STORES}
    losses = {t: stores[t]["loss_kw"] for t in STORES}
    normal = ladder(q1_src, q2_src, losses, (0.5, 0.5))
    single = ladder(q1_src, q2_src, losses, (1.0, 0.0))
    cN = closure(q1_src, q2_src, normal, losses)
    cS = closure(q1_src, q2_src, single, losses)
    S = single["A"]
    N = normal["A"]
    rated = {
        "SRC_Q1": q1_src * A_MARGIN,
        "SRC_Q2": q2_src * A_MARGIN,
        "DOWN_Q1": S["Q1"]["down"] * A_MARGIN,
        "DOWN_Q2": S["Q2"]["down"] * A_MARGIN,
        "DOWN_Q3": S["Q3"]["down"] * A_MARGIN,
        "BUS_Q4": S["Q4"]["down"] * A_MARGIN,
    }
    rated["X_Q1"] = q1_src * A_MARGIN
    rated["X_Q2"] = (S["Q2"]["from_above"] + q2_src) * A_MARGIN
    rated["X_Q3"] = S["Q3"]["from_above"] * A_MARGIN
    rated["X_Q4"] = S["Q4"]["from_above"] * A_MARGIN
    edges = {}
    for lad in "AB":
        o = "B" if lad == "A" else "A"
        edges[f"HL-AFTERBURNER-Q1-{lad}"] = dict(src="AFTERBURNER", dst=f"Q1_{lad}", rated=rated["SRC_Q1"],
            normal=N["Q1"]["src"], **pumped(rated["SRC_Q1"], OIL_Q1, 220.0, 250.0),
            hot_side=f"afterburner flue {A_T_HX7:.0f} -> {A_T_Q1X:.0f} C after HX-7, {ab['m_flue_kg_h']} kg/h")
        edges[f"HL-GLASS_BURNOUT-Q2-{lad}"] = dict(src="GLASS_BURNOUT", dst=f"Q2_{lad}", rated=rated["SRC_Q2"],
            normal=N["Q2"]["src"], **pumped(rated["SRC_Q2"], OIL_Q2, 120.0, 150.0),
            hot_side=f"rotary Q2 jacket behind insulation + cullet cooler {A_T_BURN:.0f} -> {A_T_CULLET_OUT:.0f} C")
        edges[f"HL-Q1-{lad}-DOWN"] = dict(src=f"Q1_{lad}", dst=f"Q2_{lad}", rated=rated["DOWN_Q1"], normal=N["Q1"]["down"],
                                          **twophase(rated["DOWN_Q1"], "DA_200", A_L_DOWN))
        edges[f"HL-Q2-{lad}-DOWN"] = dict(src=f"Q2_{lad}", dst=f"Q3_{lad}", rated=rated["DOWN_Q2"], normal=N["Q2"]["down"],
                                          **twophase(rated["DOWN_Q2"], "W_125", A_L_DOWN))
        edges[f"HL-Q3-{lad}-DOWN"] = dict(src=f"Q3_{lad}", dst=f"Q4_{lad}", rated=rated["DOWN_Q3"], normal=N["Q3"]["down"],
                                          **twophase(rated["DOWN_Q3"], "W_85", A_L_DOWN))
        edges[f"HL-Q4-{lad}-BUS"] = dict(src=f"Q4_{lad}", dst="Q4_BUS", rated=rated["BUS_Q4"], normal=N["Q4"]["down"],
                                         **pumped(rated["BUS_Q4"], WATER_Q4, 65.0, 45.0))
    xkeys = {"Q1": "DA_245", "Q2": "W_145", "Q3": "W_95", "Q4": "W_65"}
    for t, key in xkeys.items():
        edges[f"{'HL-'+t}-X"] = dict(src=f"{t}_A", dst=f"{t}_B", rated=rated["X_" + t], normal=0.0,
                                     **twophase(rated["X_" + t], key, A_L_X))
        edges[f"{'HL-'+t}-X-BA"] = dict(src=f"{t}_B", dst=f"{t}_A", rated=rated["X_" + t], normal=0.0,
                                        **twophase(rated["X_" + t], key, A_L_X))
    # S67B
    co2_cut = CO2_AB_KG_D * A_CAPTURE_REC
    y = A_CAPTURE_PUR
    wco2 = y * 44 / (y * 44 + (1 - y) * 28.9)
    tot = co2_cut / wco2
    rho = A_P_CUT * (y * 0.044 + (1 - y) * 0.0289) / (R * (A_T_CUT + 273.15))
    qv = tot / 86400 / rho
    dn = pick_dn(qv, A_V_GAS)
    q_cold = co2_cut / 86400 * (0.85 * (A_T_CUT + 20.0) + 282.0)
    edges["S67B"] = dict(src="FLUE_KO", dst="CRYO_CO2", rated=co2_cut, normal=co2_cut, kind="gas line",
                         medium=f"dry CO2-rich cut, >= {y*100:.0f} mol% CO2, balance N2/O2, dew point <= -40 C",
                         supply_C=A_T_CUT, return_C=None, P_bar_a=A_P_CUT / 1e5, co2_kg_d=round(co2_cut, 2),
                         total_kg_d=round(tot, 2), rho_kg_m3=round(rho, 3), flow_Nm3_h=round(tot / 24 / (1.01325e5 * (y * 0.044 + (1 - y) * 0.0289) / (R * 273.15)), 4),
                         line_DN=dn, line_id_mm=PIPE_ID_MM[dn], velocity_m_s=round(qv / area_id(dn), 3),
                         velocity_basis_m_s=A_V_GAS, sink_duty_kw=round(q_cold, 4),
                         rejected_co2_kg_d=round(CO2_AB_KG_D - co2_cut, 2))
    for k, e in edges.items():
        e["rated"] = round(e["rated"], 3)
        e["normal"] = round(e["normal"], 3)
    res = dict(afterburner=ab, burnout=bo, stores=stores, q1_src=kw(q1_src), q2_src=kw(q2_src),
               normal=normal, single=single, closure_normal=[kw(x) for x in cN], closure_single=[kw(x) for x in cS],
               rated={k: kw(v) for k, v in rated.items()}, edges=edges)
    return res



# ================================================================ Rev J (AQS-DUTY-008 Rev B)
# HX-8 on Q4, Q3 process draws HX-4/5/6, re-rated Q3/Q4. Inputs from repo docs; A_J_* are decisions.
F = 96485.0
DHF = {"Fe2+": -89.1, "Cu2+": 64.8, "Zn2+": -153.9, "Al3+": -531.0, "Cl-": -167.2, "ClO3-": -104.0, "H2O": -285.8}  # kJ/mol, aq, 25 C
EW_KW = 6.0                 # EW_1 continuous_kw (RECT-EW class share), graph
EW_SHARE = {"Fe": 790.0, "Cu": 137.0, "Zn": 80.0}   # kWh/t reference point, ELECTRICAL.md (Ni+Zn+Sn+Pb blend taken at Zn)
EW_CELL = {"Fe": (3.1, 0.80), "Cu": (2.2, 0.85), "Zn": (3.4, 0.80)}  # V_cell, CE, ELECTRICAL.md
EW_N, EW_L, EW_W, EW_H = 9, 0.600, 0.420, 0.650     # params.py EW_*; 9 cells
EW_WALL = (0.012, 0.16)     # m, W/m K CPVC wall
CONC_M3_H = 0.17            # concentrate to EW-1, AQS-DUTY-007
RHO_LIQ, CP_LIQ = 1050.0, 3.7   # chloride liquor
FEED_KG_D = 150.0           # plant rate, wet
# leach metals per wet t (ELECTRICAL.md reference-point build-up), leach fraction
LEACH_METALS = {"Fe": (250.0, 0.85, 55.85), "Cu": (70.0, 0.90, 63.55), "Zn": (30.0, 0.85, 65.38), "Al": (50.0, 0.85, 26.98)}
DRYER_KWH_KG = (0.70, 0.85)  # ELECTRICAL.md, per kg water evaporated
MOIST_FRAC = 0.05           # reference-point moisture, ELECTRICAL.md assay
GLASS_FRAC = (0.72, 0.13)   # soda-lime SiO2, Na2O mass fractions
CSTR = (2.000, 1.200, 1.400)   # params.py CSTR_L/W/H
DIGEST = (1.400, 0.900, 1.600)  # params.py DIGEST_L/W/H
DIGEST_CLASS_KW = 1.5       # GLASS_DIGEST continuous_kw (study class)
# decisions
A_J_T_EW = 55.0             # EW aisle liquor, inside the 40-60 C band (FAN_STACK)
A_J_EW_INS = (0.025, 0.040) # 25 mm closed-cell lagging on cell walls (fits the 150 mm gap at 750 pitch)
A_J_V_HOOD = 0.3            # m/s air over the liquor under the anode hoods
A_J_BALL = 0.80             # evaporation cut by a PP ball blanket
A_J_T_LEACH = 77.5          # mid of 70-85 C (GLOSSARY Leach / Salria)
A_J_T_REGEN = 35.0          # REGEN LEACH return after BMED (bipolar membranes held <= 40 C)
A_J_T_DIGEST = 85.0         # mid of 80-90 C
A_J_T_CAUSTIC = 35.0        # BMED caustic to the digest
A_J_NAOH_M = 2.0            # mol/L BMED caustic
A_J_LAG = (0.050, 0.035)    # 50 mm mineral wool on CSTR and digest
A_J_PURGE_M3_H = 5.0        # lid purge per vessel (CSTR N3, digest to HDR_CAUSTIC), damper-set
A_J_T_PURGE = 60.0          # purge leaves saturated at 60 C (lid reflux)
A_J_CP_SHRED = 1.0
A_J_Q4_RET = 45.0           # Q4 return
A_J_HX8_WOUT = 49.0         # HX-8 water out
A_J_HX8_LOUT = 51.0         # HX-8 liquor out
A_J_U_PLATE = 1500.0        # W/m2 K, Ti plate liquor/water
A_J_U_COIL = {"Q1": 150.0, "Q2": 150.0, "Q3": 400.0, "Q4": 400.0}   # natural convection, Appendix B basis
A_J_COIL_DT = 5.0


def xsat(T):
    p = 0.61094 * math.exp(17.625 * T / (T + 243.04)) * 1000      # Pa, Magnus
    return 0.622 * p / (101325 - p)


def hfg_w(T):
    return 2501.0 - 2.37 * T


def lagged(dims, t_k, T):
    L, W, H = dims
    A = 2 * (L * W + L * H + W * H)
    U = 1 / (t_k[0] / t_k[1] + 1 / A_H_OUT)
    return A, U, U * A * (T - T_AMB) / 1000


def purge_evap(m3_h, T_out):
    m_air = m3_h / 3600 * 1.18
    w = m_air * (xsat(T_out) - 0.010)
    return w, w * hfg_w(T_out)


def vtn_metal(m):
    # M2+ + 2Cl- -> M + Cl2 (chloride EW, Cl2 to CRU)
    return -(DHF[m + "2+"] + 2 * DHF["Cl-"]) / (2 * F) * 1000


def hx8():
    v_side = -(2 * DHF["Cl-"]) / (2 * F) * 1000          # 2H+ + 2Cl- -> H2 + Cl2
    tot = sum(EW_SHARE.values())
    rows, q_ohm = [], 0.0
    for m, e in EW_SHARE.items():
        V, CE = EW_CELL[m]
        vt = vtn_metal(m)
        frac = 1 - (CE * vt + (1 - CE) * v_side) / V
        p = EW_KW * e / tot
        q_ohm += p * frac
        rows.append(dict(metal=m, V_cell=V, CE=CE, V_tn=round(vt, 3), heat_fraction=round(frac, 3), P_kw=kw(p), heat_kw=kw(p * frac)))
    a_wall = EW_N * (2 * (EW_L + EW_W) * EW_H + EW_L * EW_W)
    U = 1 / (EW_WALL[0] / EW_WALL[1] + A_J_EW_INS[0] / A_J_EW_INS[1] + 1 / A_H_OUT)
    q_wall = U * a_wall * (A_J_T_EW - T_AMB) / 1000
    a_surf = EW_N * EW_L * EW_W
    evap_kg_h = (25 + 19 * A_J_V_HOOD) * a_surf * (xsat(A_J_T_EW) - 0.010)
    q_evap_bare = evap_kg_h / 3600 * hfg_w(A_J_T_EW)
    q_evap = q_evap_bare * (1 - A_J_BALL)
    mcp = CONC_M3_H / 3600 * RHO_LIQ * CP_LIQ
    q_feed = mcp * (A_J_T_LEACH - A_J_T_EW)
    q = q_ohm + q_feed - q_wall - q_evap
    m_w = q / (WATER_Q4["cp"] * (A_J_HX8_WOUT - A_J_Q4_RET))
    m_l = q / (CP_LIQ * (A_J_T_EW - A_J_HX8_LOUT))
    dt1, dt2 = A_J_T_EW - A_J_HX8_WOUT, A_J_HX8_LOUT - A_J_Q4_RET
    lmtd = dt1 if abs(dt1 - dt2) < 1e-9 else (dt1 - dt2) / math.log(dt1 / dt2)
    return dict(metals=rows, V_side=round(v_side, 3), q_ohmic_kw=kw(q_ohm), wall_area_m2=round(a_wall, 2), wall_U=round(U, 3),
                q_wall_kw=kw(q_wall), surf_area_m2=round(a_surf, 3), evap_bare_kg_h=round(evap_kg_h, 2),
                q_evap_bare_kw=kw(q_evap_bare), q_evap_kw=kw(q_evap), conc_mcp_kw_K=round(mcp, 4), q_feed_kw=kw(q_feed),
                duty_kw=kw(q), water_in_C=A_J_Q4_RET, water_out_C=A_J_HX8_WOUT, liquor_in_C=A_J_T_EW,
                liquor_out_C=A_J_HX8_LOUT, approach_hot_K=dt1, approach_cold_K=dt2, lmtd_K=round(lmtd, 2),
                area_m2=round(q * 1000 / (A_J_U_PLATE * lmtd), 2), water_kg_h=round(m_w * 3600, 1),
                liquor_kg_h=round(m_l * 3600, 1), sens_kw_per_K_feed=round(mcp, 4))


def draws():
    # HX-4 dryer: ELECTRICAL.md 0.70-0.85 kWh/kg water x reference-point moisture
    w_kg_d = FEED_KG_D * MOIST_FRAC
    q4 = w_kg_d * sum(DRYER_KWH_KG) / 2 / 24
    dryer = dict(water_kg_d=w_kg_d, kWh_per_kg=sum(DRYER_KWH_KG) / 2, duty_kw=kw(q4),
                 check_kWh_t=round(q4 * 24 / FEED_KG_D * 1000, 1), basis="ELECTRICAL.md dryer 0.70-0.85 kWh/kg water; table 40 kWh/t")
    # HX-5 leach
    mcp = CONC_M3_H / 3600 * RHO_LIQ * CP_LIQ
    q_regen = mcp * (A_J_T_LEACH - A_J_T_REGEN)
    A, U, q_shell = lagged(CSTR, A_J_LAG, A_J_T_LEACH)
    q_shred = FEED_KG_D / 86400 * A_J_CP_SHRED * (A_J_T_LEACH - T_AMB)
    w, q_purge = purge_evap(A_J_PURGE_M3_H, A_J_T_PURGE)
    rx = []
    dh = {"Fe": DHF["Fe2+"], "Zn": DHF["Zn2+"], "Al": DHF["Al3+"],
          "Cu": DHF["Cu2+"] + DHF["Cl-"] / 3 + DHF["H2O"] - DHF["ClO3-"] / 3}
    q_rx = 0.0
    for m, (kg_t, f, M) in LEACH_METALS.items():
        mol_d = kg_t * f * FEED_KG_D / 1000 * 1000 / M
        q = mol_d * -dh[m] / 86400
        q_rx += q
        rx.append(dict(metal=m, kg_d=round(kg_t * f * FEED_KG_D / 1000, 2), mol_d=round(mol_d, 1), dH_kJ_mol=round(dh[m], 1),
                       oxidant="ClO3-" if m == "Cu" else "H+ (lowest credit)", q_kw=kw(q)))
    q5 = q_regen + q_shell + q_shred + q_purge - q_rx
    leach = dict(T_C=A_J_T_LEACH, q_regen_kw=kw(q_regen), regen_in_C=A_J_T_REGEN, mcp_kw_K=round(mcp, 4),
                 shell_area_m2=round(A, 2), shell_U=round(U, 3), q_shell_kw=kw(q_shell), q_shred_kw=kw(q_shred),
                 purge_water_kg_d=round(w * 86400, 1), q_purge_kw=kw(q_purge), reactions=rx, q_exotherm_kw=kw(q_rx),
                 duty_kw=kw(q5))
    # HX-6 digest
    g = CULLET_KG_D
    sio2 = g * GLASS_FRAC[0] / 60.08 * 1000
    na_in = 2 * g * GLASS_FRAC[1] / 61.98 * 1000
    naoh = max(2 * sio2 - na_in, 0)
    v_l_d = naoh / A_J_NAOH_M
    m_liq = v_l_d / 1000 * 1080.0
    q_liq = m_liq / 86400 * 3.8 * (A_J_T_DIGEST - A_J_T_CAUSTIC)
    q_glass = g / 86400 * 0.84 * (A_J_T_DIGEST - T_AMB)
    Ad, Ud, q_dshell = lagged(DIGEST, A_J_LAG, A_J_T_DIGEST)
    wd, q_dpurge = purge_evap(A_J_PURGE_M3_H, A_J_T_PURGE)
    q6 = q_liq + q_glass + q_dshell + q_dpurge
    digest = dict(T_C=A_J_T_DIGEST, glass_kg_d=g, naoh_mol_d=round(naoh, 0), naoh_kg_d=round(naoh * 0.040, 1),
                  caustic_L_d=round(v_l_d, 0), q_liquor_kw=kw(q_liq), q_glass_kw=kw(q_glass), shell_area_m2=round(Ad, 2),
                  q_shell_kw=kw(q_dshell), purge_water_kg_d=round(wd * 86400, 1), q_purge_kw=kw(q_dpurge), duty_kw=kw(q6),
                  class_kw=DIGEST_CLASS_KW)
    return dryer, leach, digest


def ladder_j(q1_src, q2_src, losses, split, q_hx8, draw_list):
    """Rev J ladder: HX-8 into Q4, Q3 serves the process draws in list order; shortfall is electric trim."""
    out = {}
    for i, lad in enumerate("AB"):
        f = split[i]
        if f == 0:
            out[lad] = None
            continue
        r = {}
        q_in1 = q1_src * f
        d1 = q_in1 - losses["Q1"]
        r["Q1"] = dict(src=q_in1, from_above=0.0, loss=losses["Q1"], down=d1)
        d1n = d1 * (1 - A_HP_LOSS)
        d2 = d1n + q2_src * f - losses["Q2"]
        r["Q2"] = dict(src=q2_src * f, from_above=d1n, hp_loss=d1 - d1n, loss=losses["Q2"], down=d2)
        d2n = d2 * (1 - A_HP_LOSS)
        avail = d2n - losses["Q3"]
        served, short = {}, {}
        for name, q in draw_list:
            need = q * f
            s = min(need, max(avail, 0.0))
            served[name], short[name] = s, need - s
            avail -= s
        d3 = max(avail, 0.0)
        r["Q3"] = dict(src=0.0, from_above=d2n, hp_loss=d2 - d2n, loss=losses["Q3"], draws=sum(served.values()), down=d3)
        r["draws_served"] = served
        r["trim"] = short
        d3n = d3 * (1 - A_HP_LOSS)
        q8 = q_hx8 * f
        bus = d3n + q8 - losses["Q4"]
        r["Q4"] = dict(src=q8, from_above=d3n, hp_loss=d3 - d3n, loss=losses["Q4"], down=bus)
        out[lad] = r
    return out


def closure_j(q1_src, q2_src, q_hx8, res):
    src = q1_src + q2_src + q_hx8
    sinks = 0.0
    for r in res.values():
        if r is None:
            continue
        sinks += r["Q4"]["down"] + sum(r["draws_served"].values())
        sinks += sum(r[t]["loss"] for t in ("Q1", "Q2", "Q3", "Q4")) + sum(r[t].get("hp_loss", 0.0) for t in ("Q1", "Q2", "Q3", "Q4"))
    return src, sinks, src - sinks


def coil(q_kw, tier):
    return q_kw * 1000 / (A_J_U_COIL[tier] * A_J_COIL_DT)


A_J_LOWFIN = (2.5, 0.90)     # integral low-fin tube: outside area ratio, fin efficiency (used only if bare does not fit)


def coil_fit(area, tier, dn=25, clear=0.06):
    """Helical coil, pitch 2 OD, concentric rows (max 3) until one coil fits in 0.45 of the store height
    (evaporator low, condenser high: two cross-tie coils per store). Falls back to low-fin tube."""
    od = {15: 0.0213, 20: 0.0269, 25: 0.0337}[dn]
    vol, T, (shape, a, b, h), t, k, mat = STORES[tier]
    d0 = (a if shape == "cyl" else min(a, b)) - 2 * clear - od
    for tube, mult in (("bare", 1.0), ("integral low-fin", A_J_LOWFIN[0] * A_J_LOWFIN[1])):
        L = area / (math.pi * od * mult)
        for rows in range(1, 4):
            ds = [d0 - 4 * od * i for i in range(rows)]
            turns = L / (math.pi * sum(ds))
            height = turns * 2 * od
            if height <= 0.45 * h:
                break
        if 2 * height <= 0.9 * h:
            break
    return dict(tube=f"DN{dn} OD {od*1000:.1f} mm, {tube}", tube_m=round(L, 1), rows=rows,
                helix_d_m=[round(d, 3) for d in ds], turns_per_row=round(turns, 1), height_m=round(height, 3),
                store_inner_h_m=h, fits_two=2 * height <= 0.9 * h)


def r1_variant(h8, leach):
    """Sensitivity, not adopted: liquor recuperator between the concentrate (leach -> EW-1) and the REGEN LEACH
    return, sized so that HX-8 is 0 (EW self-balanced)."""
    mcp = h8["conc_mcp_kw_K"]
    net_ew = h8["q_ohmic_kw"] - h8["q_wall_kw"] - h8["q_evap_kw"]
    t_feed = A_J_T_EW - net_ew / mcp
    q_r1 = mcp * (A_J_T_LEACH - t_feed)
    t_ret = A_J_T_REGEN + q_r1 / mcp
    q5 = leach["duty_kw"] - q_r1
    return dict(ew_feed_C=round(t_feed, 1), r1_duty_kw=kw(q_r1), regen_after_r1_C=round(t_ret, 1),
                approach_K=round(min(A_J_T_LEACH - t_ret, t_feed - A_J_T_REGEN), 1), hx5_kw=kw(q5), hx8_kw=0.0)


def main_j():
    base = main()
    ab, bo, q1_src, q2_src = sources()
    losses = {t: base["stores"][t]["loss_kw"] for t in STORES}
    h8 = hx8()
    dryer, leach, digest = draws()
    order = [("HX-4", dryer["duty_kw"]), ("HX-6", digest["duty_kw"]), ("HX-5", leach["duty_kw"])]
    tot_draw = sum(q for _, q in order)
    run_n = ladder_j(q1_src, q2_src, losses, (0.5, 0.5), h8["duty_kw"], order)
    run_s = ladder_j(q1_src, q2_src, losses, (1.0, 0.0), h8["duty_kw"], order)
    cN, cS = closure_j(q1_src, q2_src, h8["duty_kw"], run_n), closure_j(q1_src, q2_src, h8["duty_kw"], run_s)
    idle_s = base["single"]["A"]
    S = run_s["A"]
    rated = dict(base["rated"])
    rated["DOWN_Q3"] = max(idle_s["Q3"]["down"], S["Q3"]["down"]) * A_MARGIN
    rated["BUS_Q4"] = max(idle_s["Q4"]["down"], S["Q4"]["down"]) * A_MARGIN
    # HX-8 has its own edge to each Q4 battery, so the Q4 cross-tie never carries HX-8 heat: X_Q4 keeps the ladder basis.
    rated["X_Q4"] = max(idle_s["Q4"]["from_above"], S["Q4"]["from_above"]) * A_MARGIN
    rated["HX8"] = h8["duty_kw"] * A_MARGIN
    for k, q in order:
        rated[k] = q * A_MARGIN
    trim = {lad: (sum(r["trim"].values()) if r else 0.0) for lad, r in run_n.items()}
    trim_n = {k: sum(run_n[l]["trim"][k] for l in "AB") for k, _ in order}
    trim_s = {k: run_s["A"]["trim"][k] for k, _ in order}
    edges = {}
    N = run_n["A"]
    for lad in "AB":
        edges[f"HL-Q3-{lad}-DOWN"] = dict(src=f"Q3_{lad}", dst=f"Q4_{lad}", rated=rated["DOWN_Q3"], normal=N["Q3"]["down"],
                                          normal_idle=base["normal"]["A"]["Q3"]["down"], **twophase(rated["DOWN_Q3"], "W_85", A_L_DOWN))
        edges[f"HL-Q4-{lad}-BUS"] = dict(src=f"Q4_{lad}", dst="Q4_BUS", rated=rated["BUS_Q4"], normal=N["Q4"]["down"],
                                         **pumped(rated["BUS_Q4"], WATER_Q4, 65.0, 45.0))
        p = pumped(rated["HX8"], WATER_Q4, A_J_Q4_RET, A_J_HX8_WOUT)
        p.update(kind="pumped loop (Q4 return preheat)", supply_C=A_J_HX8_WOUT, return_C=A_J_Q4_RET)
        edges[f"HL-HX8-Q4-{lad}"] = dict(src="HX8", dst=f"Q4_{lad}", rated=rated["HX8"], normal=h8["duty_kw"] / 2, **p,
                                         approach_K=min(h8["approach_hot_K"], h8["approach_cold_K"]),
                                         hot_side=f"EW liquor {A_J_T_EW:.0f} -> {A_J_HX8_LOUT:.0f} C")
        for k, dst, tsup, tret in (("HX-4", "OIL_DRYER", 95.0, 85.0), ("HX-5", "LEACH_CSTR_1", 95.0, 85.0), ("HX-6", "GLASS_DIGEST", 95.0, 90.0)):
            p = pumped(rated[k], WATER_Q4 | dict(name="treated water (Q3 jacket loop, pressurized)", rho=962.0, cp=4.21), tsup, tret)
            edges[f"HL-Q3-{lad}-{k.replace('-', '')}"] = dict(src=f"Q3_{lad}", dst=dst, rated=rated[k], normal=N["draws_served"][k], **p,
                                                              exchanger=k, trim_normal_kw=trim_n[k] / 2, trim_single_kw=trim_s[k])
    for t, key in (("Q4", "W_65"),):
        for sfx, a, b in (("X", "A", "B"), ("X-BA", "B", "A")):
            edges[f"HL-{t}-{sfx}"] = dict(src=f"{t}_{a}", dst=f"{t}_{b}", rated=rated["X_Q4"], normal=0.0, **twophase(rated["X_Q4"], key, A_L_X))
    for e in edges.values():
        e["rated"], e["normal"] = round(e["rated"], 3), round(e["normal"], 3)
    coils = {}
    for t in ("Q1", "Q2", "Q3", "Q4"):
        a = coil(rated["X_" + t], t)
        coils[t] = dict(rated_kw=kw(rated["X_" + t]), area_m2=round(a, 2), **coil_fit(a, t))
    return dict(base=base, hx8=h8, dryer=dryer, leach=leach, digest=digest, draw_order=[k for k, _ in order], draw_total_kw=kw(tot_draw),
                run_normal=run_n, run_single=run_s, closure_run_normal=[kw(x) for x in cN], closure_run_single=[kw(x) for x in cS],
                trim_normal=({k: kw(v) for k, v in trim_n.items()}), trim_single=({k: kw(v) for k, v in trim_s.items()}),
                rated_j={k: kw(v) for k, v in rated.items()}, edges_j=edges, coils=coils,
                r1=r1_variant(h8, leach), q4_bus_running_normal_kw=kw(2 * N["Q4"]["down"]),
                q4_bus_running_single_kw=kw(S["Q4"]["down"]), q4_life_kw=3.0)


# ================================================================ Rev K (AQS-DUTY-008 Rev C)
# Thermosyphon rise. Inputs: Rev J rated duties, Rev G store origins (z -6000 both ladders, 1500 mm pitch),
# issued envelope 800 x 800 x 1200. A_K_* are decisions.
A_K_Z0 = -6000.0             # mm, Rev G origin z of every store (L-1 FFL)
A_K_PITCH = 1.5              # m, store centre-to-centre along the ladder row (Rev G)
A_K_COIL_CLEAR = 0.06        # m, coil to inner top / bottom (same as coil_fit radial clearance)
A_K_DP_CHECK = 500.0         # Pa, cracking pressure of the low-cracking swing check on the condensate return
A_K_H_MIN = 0.30             # m, minimum condensate leg above the evaporator (level swing + check + drain-down)
A_K_ROUND = 0.05             # m, store elevation step rounded up to 50 mm
A_K_ELBOW_LD = 30.0          # L/D per long-radius elbow
A_K_SLAB_SOFFIT = -300.0     # mm, underside of the L0 slab over L-1 (SLAB_L0 on the placed copy)
A_K_HEADROOM = 600.0         # mm, maint_clear_mm above the highest store
A_K_PUMP_ETA = 0.15          # wire-to-water, small canned / mag-drive circulator
A_K_COIL_HELIX = 1.3         # friction multiplier for helical coil vs straight tube
A_K_K_MINOR = 12.0           # sum of minor losses per cross-tie loop (2 isolation, 1 check, 4 tees, entries)
A_K_X_DT = 5.0               # K, cross-tie loop supply - return
OIL_Q1X = dict(name="synthetic thermal oil, hydrogenated terphenyl class", rho=860.0, cp=2.48, mu=0.60e-3, beta=9.0e-4)
OIL_Q2X = OIL_Q2
WATER_Q3X = dict(name="treated water (Q3 cross-tie loop, pressurized 2.5 bar a)", rho=962.0, cp=4.21, mu=0.30e-3, beta=7.0e-4)
WATER_Q4X = dict(name="treated water (Q4 cross-tie loop)", rho=980.0, cp=4.18, mu=0.43e-3, beta=5.5e-4)
STEP_KEYS = (("Q1", "Q2", "DA_200", "DOWN_Q1"), ("Q2", "Q3", "W_125", "DOWN_Q2"), ("Q3", "Q4", "W_85", "DOWN_Q3"))
X_KEY = {"Q1": "DA_245", "Q2": "W_145", "Q3": "W_95", "Q4": "W_65"}   # Rev J two-phase keys; give the blocked store temperature
X_DESIGN_P = {"Q1": 1.0, "Q2": 1.0, "Q3": 2.5, "Q4": 1.0}               # bar a, closed loop with expansion tank (Q3 pressurized)
X_FLUID = {"Q1": (OIL_Q1X, 245.0, 240.0), "Q2": (OIL_Q2X, 145.0, 140.0), "Q3": (WATER_Q3X, 95.0, 90.0), "Q4": (WATER_Q4X, 65.0, 60.0)}


def store_geom(tier):
    vol, T, (shape, a, b, h), t, k, mat = STORES[tier]
    base = (ENVELOPE[2] - h) / 2      # inner base above the store origin (symmetric bottom / top build-up)
    return base, h


def coil_height(area, tier, lowfin, dn=25, clear=0.06):
    od = {15: 0.0213, 20: 0.0269, 25: 0.0337}[dn]
    vol, T, (shape, a, b, h), t, k, mat = STORES[tier]
    d0 = (a if shape == "cyl" else min(a, b)) - 2 * clear - od
    mult = A_J_LOWFIN[0] * A_J_LOWFIN[1] if lowfin else 1.0
    L = area / (math.pi * od * mult)
    for rows in range(1, 4):
        ds = [d0 - 4 * od * i for i in range(rows)]
        turns = L / (math.pi * sum(ds))
        height = turns * 2 * od
        if height <= 0.45 * h:
            break
    return dict(tube="bare" if not lowfin else "integral low-fin", tube_m=round(L, 1), rows=rows, height_m=round(height, 3))


def pack_store(tier, coils):
    """coils: list of (name, area). All bare first; switch the tallest bare coil to low-fin until the stack fits 0.9 h."""
    base, h = store_geom(tier)
    lowfin = {n: False for n, _ in coils}
    while True:
        res = {n: coil_height(a, tier, lowfin[n]) for n, a in coils}
        tot = sum(r["height_m"] for r in res.values())
        if tot <= 0.9 * h or all(lowfin.values()):
            break
        tall = max((n for n in lowfin if not lowfin[n]), key=lambda n: res[n]["height_m"])
        lowfin[tall] = True
    for n, a in coils:
        res[n]["area_m2"] = round(a, 2)
    return dict(coils=res, stack_m=round(tot, 3), inner_h_m=h, fits=tot <= 0.9 * h)


def pumped_loop_dp(fl, m, dn, L, coil_m):
    d = PIPE_ID_MM[dn] / 1000
    dpp, v, Re = dp_darcy(m, fl["rho"], fl["mu"], dn, L)
    dpc, vc, Rec = dp_darcy(m, fl["rho"], fl["mu"], 25, 2 * coil_m)
    dpm = A_K_K_MINOR * fl["rho"] * v * v / 2
    return dpp + dpc * A_K_COIL_HELIX + dpm


def main_k():
    J = main_j()
    rated = dict(J["base"]["rated"])
    rated.update(J["rated_j"])
    # coil areas: downhill evaporator (source tier U) / condenser (sink tier U); one bidirectional cross-tie coil per store
    areas = {}
    for s, k, key, rk in STEP_KEYS:
        areas[(s, "evap")] = coil(rated[rk], s)
        areas[(k, "cond")] = coil(rated[rk], k)
    packs = {}
    for t in ("Q1", "Q2", "Q3", "Q4"):
        lst = []
        if (t, "cond") in areas:
            lst.append(("down_condenser (low)", areas[(t, "cond")]))
        lst.append(("cross_tie (mid)", coil(rated["X_" + t], t)))
        if (t, "evap") in areas:
            lst.append(("down_evaporator (high)", areas[(t, "evap")]))
        packs[t] = pack_store(t, lst)
    steps, z = {}, {"Q1": A_K_Z0 / 1000}
    for s, k, key, rk in STEP_KEYS:
        f = TP[key]
        bs, hs = store_geom(s)
        bk, hk = store_geom(k)
        he = packs[s]["coils"]["down_evaporator (high)"]["height_m"]
        hc = packs[k]["coils"]["down_condenser (low)"]["height_m"]
        evap_c = bs + hs - A_K_COIL_CLEAR - he / 2       # above the source origin
        cond_c = bk + A_K_COIL_CLEAR + hc / 2            # above the sink origin
        # Rev B layout at equal elevation: evaporator low in the source, condenser high in the sink
        rise_revb = (bk + hk - A_K_COIL_CLEAR - hc / 2) - (bs + A_K_COIL_CLEAR + he / 2)
        # stratification-correct layout (extract at the top of the hot store, inject at the bottom of the cold store)
        rise_flat = cond_c - evap_c
        tp0 = twophase(rated[rk], key, A_L_DOWN)
        dn = tp0["line_DN"]
        # route: in-store legs + level change + pitch, plus 4 long-radius elbows on the vapor line
        def route(H):
            straight = 0.4 + 0.4 + abs(H) + A_K_PITCH
            return straight + 4 * A_K_ELBOW_LD * PIPE_ID_MM[dn] / 1000
        rho_v = f["P"] * f["M"] / (R * (f["T"] + 273.15))
        m = rated[rk] / f["hfg"]
        H = A_K_H_MIN
        for _ in range(20):
            L = max(A_L_DOWN, route(H))
            dpv, vv, _r = dp_darcy(m, rho_v, f["mu_v"], dn, L)
            dpl, vl, _r2 = dp_darcy(m, f["rl"], f["mu_l"], 15, L)
            dpt = dpv + dpl + A_K_DP_CHECK
            Hn = max(A_K_H_MIN, 2 * dpt / (f["rl"] * 9.81))
            if abs(Hn - H) < 1e-4:
                break
            H = Hn
        dz = math.ceil((evap_c - cond_c + H) / A_K_ROUND - 1e-9) * A_K_ROUND
        H_act = dz - (evap_c - cond_c)
        head = (f["rl"] - rho_v) * 9.81 * H_act
        z[k] = z[s] + dz
        steps[rk] = dict(src=s, dst=k, fluid=key, medium=f["name"], rated_kw=kw(rated[rk]), line_DN=dn, L_eq_m=round(L, 2),
                         m_kg_s=round(m, 6), dp_vapor_Pa=round(dpv, 1), dp_liquid_Pa=round(dpl, 2), dp_check_Pa=A_K_DP_CHECK,
                         dp_total_Pa=round(dpt, 1), H_req_m=round(H, 3),
                         same_elev_revB_rise_m=round(rise_revb, 3), same_elev_revB_head_Pa=round(f["rl"] * 9.81 * rise_revb, 0),
                         same_elev_correct_rise_m=round(rise_flat, 3),
                         evap_centre_m=round(evap_c, 3), cond_centre_m=round(cond_c, 3), dz_store_m=round(dz, 3),
                         rise_m=round(H_act, 3), head_Pa=round(head, 0), dp_over_head=round(dpt / head, 3), gravity_ok=dpt < 0.5 * head)
    top = (z["Q4"] * 1000 + ENVELOPE[2] * 1000)
    elev = dict(z_mm={t: round(v * 1000) for t, v in z.items()}, q4_top_mm=round(top),
                headroom_mm=round(A_K_SLAB_SOFFIT - top), headroom_ok=(A_K_SLAB_SOFFIT - top) >= A_K_HEADROOM)
    xties = {}
    for t, (fl, ts, tr) in X_FLUID.items():
        p = pumped(rated["X_" + t], fl, ts, tr)
        mm = p["m_kg_s"]
        xc = packs[t]["coils"]["cross_tie (mid)"]
        coil_m = xc["tube_m"]
        dpl = pumped_loop_dp(fl, mm, p["line_DN"], 2 * A_L_X, coil_m)   # supply + return, 25 m each way
        qv = mm / fl["rho"]
        hyd = qv * dpl
        xties[t] = dict(rated_kw=kw(rated["X_" + t]), **p, L_eq_m=2 * A_L_X, coil_area_m2_each=xc["area_m2"],
                        coil_tube=xc["tube"], coil_tube_m_each=coil_m, loop_dp_kPa=round(dpl / 1000, 2), pump_head_m=round(dpl / (fl["rho"] * 9.81), 2),
                        pump_hydraulic_W=round(hyd, 2), pump_electric_W=round(hyd / A_K_PUMP_ETA, 1),
                        store_dT_at_rated_K=2 * A_J_COIL_DT + A_K_X_DT, T_max_C=PSAT_MAX[X_KEY[t]][0],
                        P_loop_bar_a=X_DESIGN_P[t])
    return dict(J=J, packs=packs, steps=steps, elevations=elev, xties=xties)


if __name__ == "__main__":
    if "--rev-k" in sys.argv:
        r = main_k()
        if "--json" in sys.argv:
            json.dump({k: v for k, v in r.items() if k != "J"}, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1, default=float)
        for t, pk in r["packs"].items():
            print("pack", t, json.dumps(pk))
        for k, st in r["steps"].items():
            print("step", k, json.dumps(st))
        print("elev", json.dumps(r["elevations"]))
        for t, x in r["xties"].items():
            print("xtie", t, json.dumps(x))
        sys.exit(0)
    if "--rev-j" in sys.argv:
        r = main_j()
        if "--json" in sys.argv:
            json.dump(r, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1, default=float)
        for k in ("hx8", "dryer", "leach", "digest"):
            print(k, json.dumps(r[k]))
        print("draw_total", r["draw_total_kw"], "trim_normal", r["trim_normal"], "trim_single", r["trim_single"])
        print("closure_run_normal", r["closure_run_normal"], "closure_run_single", r["closure_run_single"])
        for c in ("run_normal", "run_single"):
            for L, t in r[c].items():
                if t:
                    print(c, L, {q: ({a: round(b, 3) for a, b in v.items()} if isinstance(v, dict) else v) for q, v in t.items()})
        print("rated_j", r["rated_j"])
        for k, e in r["edges_j"].items():
            print(k, e["rated"], e["normal"], e.get("supply_C"), e.get("return_C"), e.get("m_kg_s"), e.get("line_DN"), e.get("velocity_m_s"), e.get("dp_ok"))
        print("r1", r["r1"], "bus", r["q4_bus_running_normal_kw"], r["q4_bus_running_single_kw"])
        for k, c in r["coils"].items():
            print("coil", k, c)
        sys.exit(0)

    r = main()
    if "--json" in sys.argv:
        json.dump(r, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1, default=float)
    print(json.dumps({k: r[k] for k in ("afterburner", "burnout", "q1_src", "q2_src", "closure_normal", "closure_single", "rated")}, indent=1))
    for k, s in r["stores"].items():
        print(k, s)
    for lad in ("normal", "single"):
        for L, t in r[lad].items():
            if t:
                print(lad, L, {q: {a: round(b, 3) for a, b in v.items()} for q, v in t.items()})
    for k, e in r["edges"].items():
        print(k, e["rated"], e["normal"], e["medium"][:30], e.get("supply_C"), e.get("return_C"), e.get("m_kg_s"), e.get("line_DN"), e.get("velocity_m_s"), e.get("dp_ok"))

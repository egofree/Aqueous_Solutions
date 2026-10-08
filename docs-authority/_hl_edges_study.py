#!/usr/bin/env python3
# SPDX-License-Identifier: CERN-OHL-S-2.0
"""AQS-DUTY-008 heat-ladder edge study (HL-* and S67B).

First-principles duties, media, temperatures, flows and line sizes for the
21 edges that carried presence "study" through Rev H. Inputs are graph values
and issued envelopes; every other number is an assumption stated in A_* below.
Run: python3 _hl_edges_study.py [--json out.json]
"""
from __future__ import annotations
import json, math, sys

# ---------------------------------------------------------------- inputs (graph / docs)
CO2_AB_KG_D = 15.0          # S18 study rate, AQS-AUD-001 mid of 12-22.5 kg/d
CULLET_KG_D = 30.0          # S08G silicate + grit, AQS-AUD-001 s4.1, mixed WEEE at 150 kg/d wet
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


if __name__ == "__main__":
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

"""AQS-DUTY-012 Rev A. Rev N model corrections (graph Rev M -> Rev N).

Applies the AQS-STUDY-SSE-001 Rev A work packages to the Rev M closure model (AQS-DUTY-011). The Rev M pipeline is
re-run from the Rev L graph (commit c4e1818, or --base FILE) with these replacements:
  WP-EC-REDOX  leach ORP stated vs SHE; Fe leaves the leach as Fe(III), Cu as Cu(II); oxidation states carried through
               the electron balance (returning Fe(II)/Cu(I) re-oxidised in the leach).
  WP-EC-CE     per-cell current partition: deposition + Fe(III) reduction + Cu(II) reduction + H2 evolution, with the
               redox shuttle limited by mass transfer (X = 1 - exp(-k_m A / Q)); CE is a result. V_cell, n and the
               HER-only CE are read from the ELECTRICAL.md conventions table (single source of truth).
  WP-EC-CE     anode Cl2 above the leach oxidant demand bypasses the sparge to ALK_SCRUBBER; its hypochlorite is
               decomposed in the CRU (2 NaOCl -> 2 NaCl + O2, vented). O2 sparge make-up only when demand exceeds supply.
  WP-BMED-SEC  BMED DC = pairs x F x V_ru / CE.
  WP-CRYO-DUTY cold-head electric = cold duty / (0.16 x Carnot COP at 90 K / 300 K).
  WP-PV-ESS    S93 = worst-month mean of a pvlib TMY run (data/pv_hourly_tmy_33.0_-96.8.csv, from _rev_n_pv_ess_study.py);
               ZnBr2 flows from an hourly SOC simulation.
  WP-BAL-SPECIES element balances (Fe, Cu, Zn, Al, Na, Cl, Si, Au, Ag) with absolute tolerances; by-difference audit.
  WP-HL-OPS    NCG management provision on the two-phase thermosyphons (graph params).
A_RN_* are Rev N study decisions, each stated in REV_N_MODEL_CORRECTIONS_DUTY.md.
Run: python3 _rev_n_corrections_study.py [--base revL.json] [--revm revM.json] [--json report.json] [--write out.json]
     [--ce-fe 0.80]  (sensitivity: overrides the ELECTRICAL.md Fe CE; never used with --write)
Never edits plant.FCStd. Keeps loops_closed and every *_on_site flag as found.
"""
import copy
import csv
import json
import math
import os
import subprocess
import tempfile
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _edge_rating_study as er  # noqa: E402
import _hl_edges_study as hl  # noqa: E402
import _co2_header_study as co2  # noqa: E402
import _rev_m_closure_study as rm  # noqa: E402
from _rev_m_closure_study import (A_RM_CE, A_RM_H2_CATCH, A_RM_ENTRAIN, A_RM_RINSE_VOL, A_RM_CL2_SPARGE, A_RM_O2_UTIL,  # noqa: E402,F401
                                  A_RM_RAFF_H_M, A_RM_T_RAFF, A_RM_T_HCL, A_RM_T_CRU, A_RM_T_FLOAT, A_RM_T_S28, A_RM_T_PRE,
                                  A_RM_CAKE_SOLIDS, A_RM_RECT_ETA, A_RM_INV_LOSS, A_RM_HYDRO_PUMP_ETA, A_RM_FC_ETA,
                                  A_RM_STANDBY_H, A_RM_ZNBR2_AW, A_RM_ZNBR2_APPROACH, A_RM_GREY_SLUDGE, A_RM_DOSE_KG_D,
                                  A_RM_VCD_KWH_M3, A_RM_PK_KW, A_RM_GLASS_INSOL, A_RM_S11_LHV, A_RM_RECYCLE_DN,
                                  CP_L, DHE, RevM, ceil_step, h2o_sat_per_kg_gas)

REPO = os.path.abspath(os.path.join(HERE, ".."))
REVM_REF = "fa9ac07"          # Rev M commit (local, share main)
M = er.M
N_E = er.N_E
EW_METALS = er.EW_METALS
F = 96485.0
R_GAS = 8.314462
M_AL = 26.98

# ---- Rev N study decisions (A_RN_*); each is stated in REV_N_MODEL_CORRECTIONS_DUTY.md
A_RN_ORP_SHE = 1.05            # V vs SHE, leach ORP setpoint (range below)
A_RN_ORP_RANGE = (1.00, 1.10)
A_RN_AGCL_SAT = 0.197          # V vs SHE, Ag/AgCl in saturated KCl, 25 C (deBethune 1959)
A_RN_E0 = {"Fe3/Fe2": 0.771, "Cu2/CuCl": 0.54, "Cu2/Cu1": 0.159, "AuCl4/Au": 0.93, "Cl2/Cl": 1.36, "ClO3/Cl2": 1.47}   # V vs SHE, 25 C
A_RN_AU_E0_CASCADE = 1.00      # Electrochem-Cascade.md value (data page gives 0.93)
A_RN_KM = 2.2e-5               # m/s, mid of the FM01-LC range (Griffiths et al. 2005)
A_RN_KM_RANGE = (1.1e-5, 3.3e-5)
A_RN_CATH_AREA = 7 * 2 * 0.35 * 0.45   # m2 per cell: 7 cathodes, 2 faces, 0.35 x 0.45 m immersed, inside 600 x 420 x 650 mm
A_RN_J_FE = 300.0              # A/m2, Fe EW design current density (Liu et al. 30 mA/cm2 basis)
A_RN_LEACH_N = dict(Au=3, Ag=1, Cu=2, Pb=2, Sn=2, Ni=2, Fe=3, Cd=2, Zn=2)   # oxidation state leaving the leach at A_RN_ORP_SHE
A_RN_DHF = {"Fe2+": -89.1, "Fe3+": -48.5}   # kJ/mol, NBS (Wagman et al. 1982); Parker & Khodakovskii 1995: -90.0, -49.0
A_RN_BMED_V_RU = 2.0           # V per repeating unit (ELECTRICAL 1.8-2.2 V, mid)
A_RN_BMED_CE = 0.65            # Cassaro et al. 2023 feed-and-bleed 63-67 % (1 M product)
A_RN_CRYO_ETA = 0.16           # fraction of Carnot (basis stated with the Rev L 4.0 kW figure)
A_RN_CRYO_TC, A_RN_CRYO_TH = 90.0, 300.0
A_RN_ESS_USABLE = 105.0        # kWh usable (FLOW_BATTERY 100-110 kWh after cutoff and strip reserve)
A_RN_ESS_P = 60.0              # kW
A_RN_ESS_RTE = 0.75            # DC-DC incl. pumps (FLOW_BATTERY 70-80 %); split as sqrt each way
A_RN_ESS_SD = 0.03             # fraction of SOC per day (FLOW_BATTERY "a few percent per day")
A_RN_LED_HOURS = (6, 22)       # local standard time, photoperiod 16 h (co2.A_PHOTO_H)
A_RN_PV_KWP = 70.0
PV_HOURLY = os.path.join(HERE, "data", "pv_hourly_tmy_33.0_-96.8.csv")
PV_SUMMARY = os.path.join(HERE, "data", "pv_tmy_summary.json")
TOL_EL_FRAC = 0.01             # element tolerance = 1 % of the smallest stream of that element at the node
TOL_EL_FLOOR = 1e-6            # mol/d


def electrical_table():
    """n, V_cell and HER-only CE per metal from the ELECTRICAL.md conventions table."""
    for p in (os.path.join(HERE, "ELECTRICAL.md"), os.path.join(HERE, "..", "ELECTRICAL.md")):
        if os.path.exists(p):
            break
    else:
        raise FileNotFoundError("ELECTRICAL.md not found next to the script or one level up")
    out = {}
    for line in open(p, encoding="utf-8"):
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) == 6 and c[0] in EW_METALS:
            out[c[0]] = dict(n=int(c[1]), V=float(c[3]), CE=float(c[4]))
    missing = [m for m in EW_METALS if m not in out]
    if missing:
        raise ValueError(f"ELECTRICAL.md table missing {missing}")
    return out, os.path.relpath(p, HERE)


def vtn(m):
    """Thermoneutral voltage per electron for M(n+) + n Cl- -> M + n/2 Cl2. DUTY-008 convention: Pb/Sn/Ni/Cd at Zn, Au/Ag at Cu."""
    k = {"Fe": "Fe", "Cu": "Cu", "Zn": "Zn"}.get(m, "Zn" if m in ("Pb", "Sn", "Ni", "Cd") else "Cu")
    return hl.vtn_metal(k)


V_TN_FE3 = (A_RN_DHF["Fe2+"] - A_RN_DHF["Fe3+"] - hl.DHF["Cl-"]) / F * 1000   # Fe3+ + Cl- -> Fe2+ + 1/2 Cl2
V_SIDE = -(2 * hl.DHF["Cl-"]) / (2 * F) * 1000                                # 2 HCl -> H2 + Cl2


def leach_redox(cl=1.85, au=1.1e-5):
    """Speciation at the leach outlet for the ORP setpoint (Nernst, 77.5 C, activities as concentrations)."""
    T = hl.A_J_T_LEACH + 273.15
    s = R_GAS * T / F * math.log(10)
    r_fe = 10 ** ((A_RN_ORP_SHE - A_RN_E0["Fe3/Fe2"]) / s)
    r_cu = 10 ** ((A_RN_ORP_SHE - A_RN_E0["Cu2/CuCl"]) / s)
    e_au = A_RN_E0["AuCl4/Au"] + s / 3 * math.log10(au / cl ** 4)
    e_au_c = A_RN_AU_E0_CASCADE + s / 3 * math.log10(au / cl ** 4)
    e_cl2 = A_RN_E0["Cl2/Cl"] - s * math.log10(cl)
    return dict(orp_V_SHE=A_RN_ORP_SHE, range_V_SHE=list(A_RN_ORP_RANGE), orp_V_AgAgCl_sat_25C=round(A_RN_ORP_SHE - A_RN_AGCL_SAT, 3),
                T_C=hl.A_J_T_LEACH, nernst_slope_V_dec=round(s, 4), cl_M=cl, au_M=au, fe3_fe2_ratio=r_fe, fe2_fraction=1 / (1 + r_fe),
                cu2_cu1_ratio=r_cu, au_dissolution_E_V=round(e_au, 3), au_dissolution_E_V_cascade_E0=round(e_au_c, 3),
                cl2_cl_E_V=round(e_cl2, 3), margin_to_cl2_V=round(e_cl2 - A_RN_ORP_SHE, 3), rev_m_glossary="ORP > 1.5 V, no reference stated")


def ew_model(X, q_ew_kg, raff_kg, bleed_kg, entr_kg, na_cru, ce_fe=None, km=A_RN_KM, area=A_RN_CATH_AREA, cl_M=1.85, au_M=1.1e-5):
    """Per-cell current partition for the series EW cascade. Returns cells, raffinate species and loop compositions (mol/d)."""
    tab, src = electrical_table()
    if ce_fe is not None:
        tab["Fe"] = dict(tab["Fe"], CE=ce_fe)
    rho = hl.RHO_LIQ
    Q = q_ew_kg / rho                       # m3/d through the cascade
    b = bleed_kg / raff_kg                  # fraction of raffinate leaving on IA-BMED-05
    e_frac = entr_kg / raff_kg              # entrained electrolyte at raffinate composition (to MFG rinse, back on S16)
    diss, f = X["diss"], X["f_plate"]
    rx = leach_redox(cl_M, au_M)
    nin, dep, R = {}, {}, {}
    for m in EW_METALS:
        d = diss[m] * 1000 / M[m]
        dep[m] = d * f
        R[m] = (d - dep[m]) / b             # raffinate metal, mol/d (bleed carries the undeposited metal)
        nin[m] = R[m] + dep[m] + R[m] * e_frac
    al = X["al"] * 1000 / M_AL
    pool = dict(Fe3=nin["Fe"] * (1 - rx["fe2_fraction"]), Fe2=nin["Fe"] * rx["fe2_fraction"], Cu2=nin["Cu"], Cu1=0.0)
    pool.update({m: nin[m] for m in EW_METALS if m not in ("Fe", "Cu")})
    feed_species = dict(pool)
    xs = 1 - math.exp(-km * area * 86400 / Q)
    cells, tot = [], dict(ne_dep=0.0, r_fe=0.0, r_cu=0.0, ne_h2=0.0, n_tot=0.0, p_kw=0.0, q_heat_kw=0.0)
    for i, m in enumerate(EW_METALS):
        cell = f"EW_{i + 1}"
        V, ce = tab[m]["V"], tab[m]["CE"]
        r_fe = pool["Fe3"] if m == "Fe" else pool["Fe3"] * xs
        pool["Fe3"] -= r_fe
        pool["Fe2"] += r_fe
        r_cu = pool["Cu2"] * xs
        pool["Cu2"] -= r_cu
        pool["Cu1"] += r_cu
        if m == "Cu":
            m_in = pool["Cu1"] + pool["Cu2"]
            d1 = min(dep[m], pool["Cu1"])
            d2 = dep[m] - d1
            pool["Cu1"] -= d1
            pool["Cu2"] -= d2
            ne = d1 + 2 * d2
        elif m == "Fe":
            m_in = pool["Fe2"]
            pool["Fe2"] -= dep[m]
            ne = 2 * dep[m]
        else:
            m_in = pool[m]
            pool[m] -= dep[m]
            ne = dep[m] * tab[m]["n"]
        nh = ne * (1 - ce) / ce
        nt = ne + r_fe + r_cu + nh
        I = nt * F / 86400
        p = I * V / 1000
        heat = p - (ne * vtn(m) + r_fe * V_TN_FE3 + r_cu * vtn("Cu") + nh * V_SIDE) * F / 86.4e6
        x_need = dep[m] / m_in if m_in > 0 else 0.0
        a_req = {f"{k:.1e}": round(-math.log(max(1 - x_need, 1e-12)) * Q / (k * 86400), 2) for k in (A_RN_KM_RANGE[0], km, A_RN_KM_RANGE[1])}
        c_in = m_in / Q                       # mol/m3 of the depositing metal at the cell inlet
        n_dep = tab[m]["n"] if m != "Cu" else (ne / dep[m] if dep[m] else 2)
        i_lim = n_dep * F * km * c_in
        j = I / area
        a_fe = (I / A_RN_J_FE) if m == "Fe" else None
        cells.append(dict(cell=cell, metal=m, V_cell=V, ce_her_only=ce, ne_dep=ne, r_fe3=r_fe, r_cu2=r_cu, ne_h2=nh, n_total=nt,
                          ce_derived=ne / nt if nt else 0.0, I_A=I, p_kw=p, heat_kw=heat, j_A_m2=j, area_m2=area, x_shuttle=xs,
                          x_needed=x_need, area_required_m2=a_req, c_in_mol_m3=c_in, i_lim_A_m2=i_lim, dep_mol=dep[m],
                          dep_kg=dep[m] * M[m] / 1000, area_at_j_fe_m2=a_fe,
                          recovery_at_envelope=xs * Q / (xs * Q + (1 - xs) * bleed_kg / rho)))
        for k, v in (("ne_dep", ne), ("r_fe", r_fe), ("r_cu", r_cu), ("ne_h2", nh), ("n_tot", nt), ("p_kw", p), ("q_heat_kw", heat)):
            tot[k] += v
    raff = dict(pool)
    # pool after the cascade still contains the entrained share; remove it to get the raffinate leaving EW_9
    raff_out = {k: v / (1 + e_frac) for k, v in raff.items()}
    entr = {k: raff[k] - raff_out[k] for k in raff}
    ret = (raff_out["Fe2"] + raff_out["Cu1"]) * (1 - b) + entr["Fe2"] + entr["Cu1"]
    dem_fresh = sum(diss[m] * 1000 / M[m] * A_RN_LEACH_N[m] for m in EW_METALS)
    al_e = 3 * al
    u_eq = sum(b * raff_out[k] * z for k, z in (("Fe2", 2), ("Fe3", 3), ("Cu1", 1), ("Cu2", 2))) + \
        sum(b * raff_out[m] * N_E[m] for m in EW_METALS if m not in ("Fe", "Cu"))
    vol = dict(Q_m3_d=Q, raff_m3_d=raff_kg / rho, bleed_m3_d=bleed_kg / rho, b=b)
    conc = {k: v / (raff_kg / rho) for k, v in raff_out.items()}
    conc_in = {k: v / Q for k, v in feed_species.items()}
    na_c = na_cru / b / (raff_kg / rho)
    al_c = al / b / (raff_kg / rho)
    cl_c = A_RM_RAFF_H_M * 1000 + na_c + 3 * al_c + 2 * conc["Fe2"] + 3 * conc["Fe3"] + conc["Cu1"] + 2 * conc["Cu2"] + \
        sum(conc[m] * N_E[m] for m in EW_METALS if m not in ("Fe", "Cu"))
    q_feed = 2 * feed_species["Fe2"] + 3 * feed_species["Fe3"] + feed_species["Cu1"] + 2 * feed_species["Cu2"] + \
        sum(feed_species[m] * N_E[m] for m in EW_METALS if m not in ("Fe", "Cu"))
    cl_feed = (A_RM_RAFF_H_M * 1000 * raff_kg / rho * (1 + e_frac) + tot["ne_h2"] + (na_cru + 3 * al) / b * (1 + e_frac) + q_feed) / Q
    ret_fe2 = raff_out["Fe2"] * (1 - b) + entr["Fe2"]
    ret_cu1 = raff_out["Cu1"] * (1 - b) + entr["Cu1"]
    summ = dict(cl_feed_M=cl_feed / 1000, au_feed_M=feed_species["Au"] / Q / 1000, fe_third_e=diss["Fe"] * 1000 / M["Fe"], returned_fe2=ret_fe2, returned_cu1=ret_cu1, source_table=src, km_m_s=km, area_m2_per_cell=area, x_shuttle=xs, ce_fe=tab["Fe"]["CE"], tot=tot, dem_fresh=dem_fresh,
                al_mol=al, al_e=al_e, returned_reduced=ret, demand=dem_fresh + al_e + ret, u_eq=u_eq, vol=vol, raff_mM=conc, feed_mM=conc_in,
                na_mM=na_c, al_mM=al_c, cl_raff_M=cl_c / 1000, leach=rx, ce_ew_overall=tot["ne_dep"] / tot["n_tot"])
    return dict(cells=cells, summary=summ, feed=feed_species, raff=raff_out, entr=entr, nin=nin, dep=dep, b=b, tab=tab)


def hx8_patch(ewm):
    """HX-8 with the cell ohmic heat from the per-cell partition (replaces the DUTY-008 6.0 kW share basis)."""
    orig = hl.hx8

    def hx8_n():
        h = orig()
        q_new = ewm["summary"]["tot"]["q_heat_kw"]
        k = (h["duty_kw"] - h["q_ohmic_kw"] + q_new) / h["duty_kw"]
        h = dict(h, rev_m_q_ohmic_kw=h["q_ohmic_kw"], rev_m_duty_kw=h["duty_kw"], q_ohmic_kw=hl.kw(q_new), duty_kw=hl.kw(h["duty_kw"] * k),
                 area_m2=round(h["area_m2"] * k, 2), water_kg_h=round(h["water_kg_h"] * k, 1), liquor_kg_h=round(h["liquor_kg_h"] * k, 1),
                 metals=[dict(cell=c["cell"], metal=c["metal"], P_kw=round(c["p_kw"], 3), heat_kw=round(c["heat_kw"], 3)) for c in ewm["cells"]],
                 basis="AQS-DUTY-012 per-cell partition: heat = I V - sum(partial current x V_tn)")
        return h
    hx8_n.orig = orig
    return hx8_n


def pv_load():
    rows = []
    with open(PV_HOURLY) as fh:
        for r in csv.DictReader(fh):
            rows.append((int(r["month_local"]), int(r["day_local"]), int(r["hour_local_standard"]), float(r["p_dc_kw"])))
    summ = json.load(open(PV_SUMMARY))
    return rows, summ


def ess_sim(rows, ac_flat_no_led, led_avg, dc_const, ac_const):
    """Hourly bus with ZnBr2 SOC. AC demand x (1 + inverter loss); PV + DMFC (DC) + hydro (AC) constant supplies; grid by difference."""
    eta = math.sqrt(A_RN_ESS_RTE)
    h0, h1 = A_RN_LED_HOURS
    led_on = led_avg * 24 / (h1 - h0)
    soc = 0.0
    out = None
    for _pass in range(2):                   # first pass sets the initial SOC (31 Dec carry-over)
        mon = {}
        for m, d, h, pv in rows:
            ac = ac_flat_no_led + (led_on if h0 <= h < h1 else 0.0)
            need = ac * (1 + A_RM_INV_LOSS)
            net = pv + dc_const + ac_const - need
            chg = dis = grid = exp = 0.0
            if net > 0:
                chg = min(net, A_RN_ESS_P, max(A_RN_ESS_USABLE - soc, 0) / eta)
                exp = net - chg
            else:
                dis = min(-net, A_RN_ESS_P, soc * eta)
                grid = -net - dis
            s0 = soc
            sd = soc * A_RN_ESS_SD / 24
            soc = soc + chg * eta - dis / eta - sd
            k = mon.setdefault(m, dict(h=0, pv=0.0, chg=0.0, dis=0.0, grid=0.0, exp=0.0, sd=0.0, conv=0.0, soc0=s0, soc1=0.0, need=0.0, soc_max=0.0))
            k["h"] += 1
            for kk, vv in (("pv", pv), ("chg", chg), ("dis", dis), ("grid", grid), ("exp", exp), ("sd", sd), ("need", need)):
                k[kk] += vv
            k["conv"] += chg * (1 - eta) + dis * (1 / eta - 1)
            k["soc1"] = soc
            k["soc_max"] = max(k["soc_max"], soc)
        out = mon
    res = {}
    for m, k in sorted(out.items()):
        hh = k["h"]
        res[m] = {x: k[x] / hh for x in ("pv", "chg", "dis", "grid", "exp", "sd", "conv", "need")}
        res[m]["dsoc_kw"] = (k["soc1"] - k["soc0"]) / hh
        res[m]["soc_max_kwh"] = k["soc_max"]
        res[m]["cycles_per_day"] = k["dis"] / A_RN_ESS_USABLE / (hh / 24)
    hrs = sum(out[m]["h"] for m in out)
    ann = {x: sum(out[m][x] for m in out) / hrs for x in ("pv", "chg", "dis", "grid", "exp", "sd", "conv", "need")}
    return dict(monthly=res, annual=ann, led_on_kw=led_on, eta_each_way=eta)


def rate_n(g, R, X, ctx):
    S = RevM(g, R, X)
    D = S.decisions
    feed = hl.FEED_KG_D
    # ================================================================ 1. EW Faraday basis
    diss, f_plate = X["diss"], X["f_plate"]
    q_ew = S.v("IA-EW-04")
    h8 = hl.hx8()
    evap_cell = h8["evap_bare_kg_h"] * (1 - hl.A_J_BALL) * 24.0 / hl.EW_N
    chain = ["IA-EW-01", "IA-EW-02", "IA-EW-03", "IA-EW-10", "IA-EW-05", "IA-EW-06", "IA-EW-07", "IA-EW-08", "IA-EW-09"]
    w_h2 = h2o_sat_per_kg_gas(hl.A_J_T_EW, M["H2"])
    flow = q_ew
    ew = []
    ewm = ctx["ewm"]
    tot = dict(dep=0.0, ne_dep=0.0, ne_side=0.0, ne_fe=0.0, ne_cu=0.0, ne_h2=0.0, cl2=0.0, h2=0.0, h2_caught=0.0, vap=0.0, entr=0.0, p_kw=0.0, h2_hood=0.0)
    for i, m in enumerate(EW_METALS):
        cell = f"EW_{i + 1}"
        cm = ewm["cells"][i]
        S.drop(cell, "mass")
        dep = diss[m] * f_plate
        ne = cm["ne_dep"]
        ns = cm["r_fe3"] + cm["r_cu2"] + cm["ne_h2"]
        h2 = cm["ne_h2"] / 2 * M["H2"] / 1000
        cl2 = cm["n_total"] / 2 * M["Cl2"] / 1000
        entr = dep * A_RM_ENTRAIN
        caught = cell in A_RM_H2_CATCH
        vap = h2 * w_h2 if caught else 0.0
        out = flow - dep - cl2 - h2 - entr - evap_cell - vap
        p_kw = cm["p_kw"]
        S.set(chain[i], out, "kg/d",
              f"{cell} in {flow:.1f} - {m} deposit {dep:.3f} - anode Cl2 {cl2:.3f} - H2 {h2:.4f} - harvest entrainment {entr:.3f} - evaporation {evap_cell:.2f}"
              + (f" - H2 saturation water {vap:.3f}" if caught else ""),
              "AQS-DUTY-012 per-cell current partition (deposition, Fe3+ and Cu2+ reduction, H2); CE derived", "chloride electrolyte overflow",
              f"{hl.A_J_T_EW} C, atm", deposit_kg_d=round(dep, 4), anode_cl2_kg_d=round(cl2, 4), h2_kg_d=round(h2, 5), ce=round(cm["ce_derived"], 4),
              current_A=round(cm["I_A"], 1), fe3_reduced_mol_d=round(cm["r_fe3"], 2), cu2_reduced_mol_d=round(cm["r_cu2"], 2))
        S.off(cell, "mass", "out", f"{m} cathode harvest (reported on S08)", dep, "S08 split by leach build-up")
        S.off(cell, "mass", "out", "anode Cl2 to the Cl2 header (leach sparge; surplus to ALK_SCRUBBER)", cl2, "Faraday: total cell current / 2F")
        S.off(cell, "mass", "out", "evaporation to EW hood (ball blanket)", evap_cell, "DUTY-008 HX-8")
        S.off(cell, "mass", "out", "electrolyte entrained on harvest (to MFG rinse, returns on S16)", entr, f"{A_RM_ENTRAIN} kg/kg deposit")
        if caught:
            sid = A_RM_H2_CATCH[cell]
            S.set(sid, h2 + vap, "kg/d", f"{cell} {m}: HER {cm['ne_h2']:.1f} mol e-/d (HER-only CE {cm['ce_her_only']} per ELECTRICAL.md); H2 {h2:.4f} kg/d + saturation water {vap:.4f} at {hl.A_J_T_EW} C",
                  "AQS-DUTY-012 per-cell current partition", "H2, water-saturated", f"{hl.A_J_T_EW} C, cathode hood", h2_kg_d=round(h2, 5), water_kg_d=round(vap, 5))
            tot["h2_caught"] += h2
            tot["vap"] += vap
        else:
            S.off(cell, "mass", "out", "cathode H2 to hood sweep (vented, < 1 % LFL)", h2, "minor cell; not collected")
            tot["h2_hood"] += h2
        ew.append(dict(cell=cell, metal=m, in_kg_d=round(flow, 2), deposit=round(dep, 4), n_e_dep=round(ne, 2), n_e_side=round(ns, 2),
                       n_e_fe3=round(cm["r_fe3"], 2), n_e_cu2=round(cm["r_cu2"], 2), n_e_h2=round(cm["ne_h2"], 2), ce_derived=round(cm["ce_derived"], 4),
                       I_A=round(cm["I_A"], 1), j_A_m2=round(cm["j_A_m2"], 1), V_cell=cm["V_cell"],
                       cl2=round(cl2, 4), h2=round(h2, 5), caught=caught, entrained=round(entr, 3), out=round(out, 2), p_kw=round(p_kw, 3)))
        for k, val in (("dep", dep), ("ne_dep", ne), ("ne_side", ns), ("ne_fe", cm["r_fe3"]), ("ne_cu", cm["r_cu2"]), ("ne_h2", cm["ne_h2"]),
                       ("cl2", cl2), ("h2", h2), ("entr", entr), ("p_kw", p_kw)):
            tot[k] += val
        flow = out
    raff = flow
    S.off("EW_9", "mass", "in", "H2 dryer condensate return", tot["vap"], "H2_DRYER knock-out drained to the EW_9 sump")
    S.set("IA-HDR-H2-02", tot["h2_caught"] + tot["vap"], "kg/d", "sum of IA-HDR-H2-01/03/04", "AQS-DUTY-011", "H2, water-saturated", "header")
    S.set("S64", tot["h2_caught"], "kg/d", f"dried H2 = collected H2 {tot['h2_caught']:.4f} kg/d (Fe, Cu, Zn cells)", "AQS-DUTY-012 per-cell partition", "H2, dry", "dryer out")
    S.drop("H2_DRYER")
    S.off("H2_DRYER", "mass", "out", "knock-out condensate to EW_9 sump", tot["vap"], "saturation water at 55 C")
    S.log.append(f"Rev N H2 {tot['h2']:.3f} kg/d total, {tot['h2_caught']:.3f} kg/d collected; EW DC {tot['p_kw']:.3f} kW")
    D["ew"] = dict(h2_total=tot["h2"], h2_caught=tot["h2_caught"], h2_hood=tot["h2_hood"], cl2_total=tot["cl2"], ne_dep=tot["ne_dep"],
                   ne_side=tot["ne_side"], p_ew_kw=tot["p_kw"], entrained=tot["entr"], dep=tot["dep"], cells=ew, raff=raff)
    D["ew"].update(ne_fe=tot["ne_fe"], ne_cu=tot["ne_cu"], ne_h2=tot["ne_h2"], model=ewm["summary"])
    # ================================================================ 2. CRYO_H2 dispatch, FC / GEN standby, MeOH
    h2 = tot["h2_caught"]
    S.set("S74", h2, "kg/d", "all dried H2 to MeOH synthesis on the design day (standby FC/GEN inventory held full)", "AQS-DUTY-011 dispatch", "H2", "~30 bar")
    fc_lhv = 4.0 / A_RM_FC_ETA
    h2_fc = fc_lhv * 86.4 / er.LHV_H2
    inv = h2_fc / 24 * A_RM_STANDBY_H
    o2_fc = h2_fc * M["O2"] / 2 / M["H2"]
    st_rows = (("S49", "FC H2", round(h2_fc, 3)), ("S45", "GEN H2", S.v("S45")), ("S50", "FC O2 (stoichiometric)", round(o2_fc, 3)),
               ("S52", "PEM product water", round(h2_fc * M["H2O"] / M["H2"], 3)), ("S46", "GEN exhaust", S.v("S46")))
    for sid, txt, st in st_rows:
        S.set(sid, 0.0, "kg/d", f"standby: 0 on the design day; {txt} {st} kg/d while running", "AQS-DUTY-011 dispatch (H2 make cannot carry a continuous 4 kW FC)",
              (S.E[sid].get("params") or {}).get("medium", txt), "standby", standby_kg_d=st)
    s53_st = round((fc_lhv - 4.0) * (er.A_RL_FC_T_C - hl.A_J_Q4_RET) / (er.A_RL_FC_T_C - 25.0), 3)
    for sid, st in (("S51", 4.0), ("S47", S.v("S47")), ("S53", s53_st)):
        S.set(sid, 0.0, "kW", f"standby: 0 on the design day; {st} kW while running", "AQS-DUTY-011 dispatch", (S.E[sid].get("params") or {}).get("medium", "power"),
              "standby", standby_kw=st)
    for u in ("FUEL_CELL", "BACKUP_GEN"):
        S.drop(u)
    D["standby"] = dict(fc_lhv_kw=fc_lhv, fc_h2_kg_d=h2_fc, fc_h2_kg_h=h2_fc / 24, inventory_kg=inv, fill_days=inv / h2 if h2 else None,
                        fc_o2_stoich_kg_d=o2_fc, fc_water_kg_d=h2_fc * M["H2O"] / M["H2"], fc_heat_kw=fc_lhv - 4.0, s53_standby_kw=s53_st)
    s75 = h2 * M["MeOH"] / (3 * M["H2"])
    s73 = s75 * M["CO2"] / M["MeOH"]
    S.set("S75", s75, "kg/d", f"CO2 + 3 H2 -> CH3OH + H2O on S74 {h2:.4f} kg/d H2", "stoichiometry", "crude MeOH", "ambient")
    S.set("S73", s73, "kg/d", f"stoichiometric CO2 for S75 {s75:.3f} kg/d", "stoichiometry", "CO2 feedstock", "~30 bar")
    s77 = S.v("S77")
    s76 = s75 + s77
    S.set("S76", s76, "kg/d", f"S75 {s75:.3f} + S77 {s77}", "MEOH_TANK level", "MeOH fuel", "ambient")
    n_meoh = s76 * 1000 / M["MeOH"]
    S.set("S81", n_meoh * 2 * M["H2O"] / 1000, "kg/d", f"CH3OH + 1.5 O2 -> CO2 + 2 H2O on S76 {s76:.3f}", "stoichiometry", "MeOH FC product water", "~60 C")
    s82 = s76 * M["CO2"] / M["MeOH"]
    S.set("S82", s82, "kg/d", f"S76 {s76:.3f} x 44.01/32.04", "stoichiometry", "CO2 return", "ambient")
    eta = 3600 / (er.A_RL_DMFC_L_KWH * er.A_RL_RHO_MEOH * er.LHV_MEOH * 1000)
    q_meoh = s76 * er.LHV_MEOH / 86.4
    s79 = q_meoh * eta
    f_fc = (er.A_RL_FC_T_C - hl.A_J_Q4_RET) / (er.A_RL_FC_T_C - 25.0)
    s80 = (q_meoh - s79) * f_fc
    S.set("S79", s79, "kW", f"DMFC eta {eta:.4f} x S76 LHV {q_meoh:.3f} kW", "EFOY-class fuel use", "DC power", "24 V DC bus")
    S.set("S80", s80, "kW", f"DMFC heat {q_meoh - s79:.3f} kW x {f_fc:.4f} above Q4 return", "MeOH LHV", "Q4 water", "45 C return")
    for u in ("MEOH_FC", "MEOH_SYNTH"):
        S.drop(u)
    S.off("MEOH_FC", "mass", "in", "air O2", n_meoh * 1.5 * M["O2"] / 1000, "stoichiometric")
    S.off("MEOH_FC", "energy", "in", "MeOH LHV (S76)", q_meoh, "19.93 MJ/kg")
    S.off("MEOH_FC", "energy", "out", "low-grade heat", q_meoh - s79 - s80, "below Q4 return")
    S.off("MEOH_SYNTH", "mass", "out", "synthesis water", s75 * M["H2O"] / M["MeOH"], "CO2 + 3 H2 -> CH3OH + H2O")
    # ================================================================ 3. afterburner CO2 (S11 carbon folded in)
    s11 = S.v("S11")
    s11_co2 = X["s11_co2"]
    co2_ab = hl.CO2_AB_KG_D + s11_co2
    m_flue = X["m_flue"] + s11
    s11_dm = s11 * er.A_RL_S11_DM
    s11_w = s11 - s11_dm + s11_dm * 0.06 * M["H2O"] / M["H2"]
    q_s11 = s11_dm * A_RM_S11_LHV / 86.4
    S.set("S67", m_flue, "kg/d", f"DUTY-008 flue {X['m_flue']:.2f} + S11 trim {s11} (burned within the excess air)", "AQS-DUTY-008 + AQS-DUTY-011",
          "flue N2/O2/CO2/H2O", "300 C", co2_kg_d=round(co2_ab, 3))
    s67b = hl.A_CAPTURE_REC * co2_ab
    S.set("S67B", s67b, "kg/d", f"VSA recovery {hl.A_CAPTURE_REC} x CO2 {co2_ab:.3f} (NCG 15.0 + S11 {s11_co2:.3f})", "AQS-DUTY-008 capture basis", "dry CO2-rich cut",
          "30 C, 1.3 bar a", co2_kg_d=round(s67b, 3), total_kg_d=round(s67b / 12.75 * 13.68, 2))
    for u in ("AFTERBURNER", "AFTERBURNER_FLUE"):
        S.drop(u, "mass")
    air = X["m_flue"] - hl.sources()[0]["fuel_kg_d"]
    S.off("AFTERBURNER", "mass", "in", "combustion air", air, "DUTY-008 flue less fuel")
    S.off("AFTERBURNER", "mass", "out", "flue to AFTERBURNER_FLUE", m_flue, "DUTY-008 + S11")
    S.off("AFTERBURNER_FLUE", "mass", "in", "flue from AFTERBURNER", m_flue, "")
    ko = X["ko_cond"] + s11_w
    s70 = R.rates["S70"]["value"]
    S.drop("FLUE_KO", "mass")
    S.off("FLUE_KO", "mass", "out", "KO condensate", ko, "flue water less saturation at 30 C (+ S11 water)")
    S.off("FLUE_KO", "mass", "out", "VSA tail gas to stack", m_flue + s70 - s67b - ko, "flue + S70 less captured CO2 and condensate")
    D["co2"] = dict(co2_ab=co2_ab, s11_co2=s11_co2, q_s11_kw=q_s11)
    s04 = S.v("S04")
    s85 = s67b + s82 - s04 - s73 - s70
    S.set("S85", s85, "kg/d", f"CRYO_CO2 remainder: S67B {s67b:.3f} + S82 {s82:.3f} - S04 {s04} - S73 {s73:.3f} - S70 {s70:.4f}", "AQS-DUTY-011 CRYO_CO2 balance",
          "CO2 product", "3.0 bar a", kind="by_difference")
    s90 = S.v("S90")
    S.set("S89", s85 + s90, "kg/d", f"S85 {s85:.3f} + S90 {s90}", "AQS-DUTY-009 Rev B method", "CO2 gas", "3.0 bar a, 20 C")
    # ================================================================ 4. hab / grey / nutrient
    s21, s26, s14, s02, s78 = S.v("S21"), S.v("S26"), S.v("S14"), S.v("S02"), S.v("S78")
    black = 4 * sum(er.A_RL_BLACK_L_P_D)
    s12 = s21 + s26 + s14 + s02 - s78 - s90 - black
    S.set("S12", s12, "kg/d", f"HAB balance: S21 {s21} + S26 {s26} + S14 {s14} + S02 {s02} - S78 {s78} - S90 {s90} - black {black:.2f} (grey + AHU condensate)",
          "AQS-DUTY-011 HAB balance; AUD s11 grey 100-120 L/d check", "grey water + AHU condensate", "ambient", kind="by_difference")
    S.drop("HABITATION", "mass")
    S.off("HABITATION", "mass", "out", "black water to BLACK_DIGEST", black, "BVAD urine/feces/flush")
    s29 = (1 - A_RM_GREY_SLUDGE) * s12
    sludge = A_RM_GREY_SLUDGE * s12
    S.set("S29", s29, "kg/d", f"grey treat recovery {1 - A_RM_GREY_SLUDGE:.0%} of S12", "grey-water practice", "treated grey", "ambient")
    S.drop("GREY_TREAT")
    S.off("GREY_TREAT", "mass", "out", "sludge / backwash to BLACK_DIGEST", sludge, f"{A_RM_GREY_SLUDGE:.0%} of S12")
    s30 = black + sludge - er.A_RL_BLACK_GAS
    S.set("S30", s30, "kg/d", f"black {black:.2f} + grey sludge {sludge:.3f} - digester gas {er.A_RL_BLACK_GAS}", "BVAD class", "digest liquor / nutrients", "ambient")
    S.drop("BLACK_DIGEST")
    S.off("BLACK_DIGEST", "mass", "in", "black water", black, "HABITATION")
    S.off("BLACK_DIGEST", "mass", "in", "grey sludge", sludge, "GREY_TREAT")
    S.off("BLACK_DIGEST", "mass", "out", "digester gas", er.A_RL_BLACK_GAS, "VS destruction")
    S.set("S07", s30 + A_RM_DOSE_KG_D, "kg/d", f"S30 {s30:.3f} + micronutrient salts {A_RM_DOSE_KG_D}", "AQS-DUTY-011 nutrient basis (black-water N and K cover crop uptake)",
          "nutrient solution", "ambient")
    S.drop("NUTRIENT_DOSE")
    S.off("NUTRIENT_DOSE", "mass", "in", "micronutrient salts (Fe chelate, Ca/Mg, trace)", A_RM_DOSE_KG_D, "dose skid")
    # ================================================================ 5. MFG / S16 / glass residue
    entr = tot["entr"]
    rinse = entr * A_RM_RINSE_VOL
    S.set("S16", entr + rinse, "kg/d", f"harvest rinse return: entrained electrolyte {entr:.3f} ({A_RM_ENTRAIN} kg/kg on {tot['dep']:.1f} kg/d) + {A_RM_RINSE_VOL:.0f} rinse volumes {rinse:.3f}",
          "AQS-DUTY-011 S16 composition", "chloride rinse liquor (Fe/Cu/Zn chlorides, HCl trace); no solid metal", "ambient")
    cu_dep = diss["Cu"] * f_plate
    blend_dep = sum(diss[k] for k in ("Pb", "Sn", "Ni", "Cd", "Zn")) * f_plate
    goods = S.v("S08") + S.v("S58") + S.v("S59") + S.v("S60") - cu_dep - blend_dep
    S.drop("MFG_SHOP")
    sw = S.v("S61")
    S.off("MFG_SHOP", "mass", "in", "scrap bin returns", sw, "draw/mill/atomizer")
    S.off("MFG_SHOP", "mass", "in", "electrolyte entrained on harvest", entr, "EW cells")
    S.off("MFG_SHOP", "mass", "in", "harvest rinse water (tower water)", rinse, "ROOF_TANK inventory")
    S.off("MFG_SHOP", "mass", "out", "charges to MET_MELT, COLD_MILL, GAS_ATOMIZER", cu_dep + blend_dep, "S08 Cu + blend")
    S.off("MFG_SHOP", "mass", "out", "finished goods to NORTH_DOCK", goods, "shop product = all not returned", kind="by_difference")
    S.set("DOCK_EXPORT_TBD", goods, "kg/d", "MFG_SHOP finished goods (Fe plate, wire, sheet, powder): S08 + formed products - charges", "AQS-DUTY-011 MFG balance",
          "metal goods (solid)", "palletized", kind="by_difference")
    S.drop("NORTH_DOCK")
    S.off("NORTH_DOCK", "mass", "in", "finished goods from MFG_SHOP", goods, "MFG_SHOP balance")
    S.drop("ROOF_TANK", "mass")
    S.off("ROOF_TANK", "mass", "in", "inventory draw (dry design day, no rain)", s21 + rinse, "S21 + MFG rinse met from storage")
    S.off("ROOF_TANK", "mass", "out", "MFG harvest rinse water", rinse, "S16 basis")
    gl = [t for t in R.off.get("GLASS_RINSE", []) if t["label"].startswith("sink residue")][0]["value"]
    S.set("S96", gl, "kg/d", f"sink residue {X['residue']:.2f} kg/d dry (unleached metal, fillers, unassigned assay) + drained moisture", "AQS-DUTY-010 sink balance",
          "inert reject (characterize: TCLP)", "ambient", dry_kg_d=round(X["residue"], 2))
    R.off["GLASS_RINSE"] = [t for t in R.off["GLASS_RINSE"] if not t["label"].startswith("sink residue")]
    return S, dict(tot=tot, raff=raff, s04=s04, s11=s11, s02=s02, s29=s29, s91=None, q_s11=q_s11, s11_dm=s11_dm, s80=s80, s79=s79, s70=s70)


def rate_n2(S, c, ctx):
    R, X, D, g = S.R, S.X, S.decisions, S.g
    tot, raff = c["tot"], c["raff"]
    diss, f_plate = X["diss"], X["f_plate"]
    feed = hl.FEED_KG_D
    h8 = hl.hx8()
    q_ew = S.v("IA-EW-04")
    # ================================================================ 6. electrons: Cl2 sparge, chlorate, O2 (Rev N: oxidation states carried)
    ewm = ctx["ewm"]
    es = ewm["summary"]
    u_e = es["u_eq"]
    al_mol = X["al"] * 1000 / M_AL
    al_e = 3 * al_mol
    dem = es["demand"]
    fe_ox_mol = es["fe_third_e"] + es["returned_fe2"]
    c_mol = tot["cl2"] * 1000 / M["Cl2"]
    a = A_RM_CL2_SPARGE
    if 2 * c_mol >= dem:
        c_sp, c_x, o2_e = dem / 2, c_mol - dem / 2, 0.0
    else:
        c_sp, c_x, o2_e = c_mol, 0.0, dem - 2 * c_mol
    c_a_in = (1 - a) * c_sp + c_x
    slip = er.A_RL_SLIP * c_a_in
    c_a = c_a_in - slip
    na_alk, na_pol = 2 * c_a, 2 * slip
    na_cru = na_alk + na_pol
    e_cl2, e_cru = 2 * a * c_sp, 2 * (1 - a) * c_sp
    delta = o2_e
    o2_dec = c_x / 2
    o2_dec_kg = o2_dec * M["O2"] / 1000
    o2_mol = delta / 4 / A_RM_O2_UTIL
    s95 = o2_mol * M["O2"] / 1000
    o2_vent = s95 * (1 - A_RM_O2_UTIL)
    if c_x > 0:
        S.set("S95", s95, "kg/d", f"0: anode Cl2 {2 * c_mol:.1f} mol e-/d exceeds the leach oxidant demand {dem:.1f} (fresh metal {es['dem_fresh']:.1f} + Al {al_e:.1f} + returning Fe(II)/Cu(I) {es['returned_reduced']:.1f}); "
              f"sparge share {c_sp:.1f} mol/d Cl2, surplus {c_x:.1f} mol/d to ALK_SCRUBBER", "AQS-DUTY-012 leach electron balance", "O2 gas (cold box product)", "~2 bar g sparge (standby)", mol_d=0.0)
    else:
        S.set("S95", s95, "kg/d", f"oxidant deficit {delta:.1f} mol e-/d (demand {dem:.1f} - Cl2 sparge {e_cl2:.1f} - chlorate {e_cru:.1f}) / 4 / utilization {A_RM_O2_UTIL}",
              "AQS-DUTY-012 leach electron balance", "O2 gas (cold box product)", "~2 bar g sparge", mol_d=round(o2_mol, 1))
    S.set("S83", s95, "kg/d", "= S95 (HDR_O2 pass-through to the leach sparge)", "AQS-DUTY-011", "O2 gas", "header 3 bar g")
    S.set("S84", 0.0, "kg/d", "HDR_N2 has no consumer edge (S88 retired; RS-HAB-N2 open)", "graph topology", "N2 gas", "header pressurized, no draw")
    D["electrons"] = dict(n_e_dep=tot["ne_dep"], u_e=u_e, al_e=al_e, al_mol=al_mol, demand=dem, dem_fresh=es["dem_fresh"], returned_reduced=es["returned_reduced"],
                          cl2_mol=c_mol, cl2_sparge_mol=c_sp, cl2_surplus_mol=c_x, e_cl2=e_cl2, e_cru=e_cru, o2_e=delta, o2_mol=o2_mol, o2_decomp_mol=o2_dec,
                          na_alk=na_alk, na_pol=na_pol, na_cru=na_cru, c_a_in=c_a_in, slip_mol=slip, n_e_side=tot["ne_side"], n_e_h2=tot["ne_h2"],
                          n_e_fe3=tot["ne_fe"], n_e_cu2=tot["ne_cu"], fe_ox_mol=fe_ox_mol, cathodic_total=2 * c_mol)
    naoh_alk_kg = na_alk / er.A_RL_M_REAGENT * er.A_RL_RHO_2M["NaOH"]
    S.set("IA-BMED-07", naoh_alk_kg, "kg/d", f"2 x Cl2 absorbed {c_a:.2f} mol/d (unabsorbed sparge {(1 - a) * c_sp:.2f} + surplus bypass {c_x:.2f}, less slip) = {na_alk:.1f} mol/d NaOH as 2 M",
          "Cl2 + 2 NaOH -> NaCl + NaOCl + H2O", "NaOH 2 M", "ambient", mol_d=round(na_alk, 1))
    cl2_abs_kg = c_a * M["Cl2"] / 1000
    alk_liq = naoh_alk_kg + cl2_abs_kg
    S.set("IA-BMED-08", alk_liq, "kg/d", f"IA-BMED-07 {naoh_alk_kg:.3f} + absorbed Cl2 {cl2_abs_kg:.4f}", "mass", "NaCl/NaOCl scrub liquor", "~40 C")
    slip_kg = slip * M["Cl2"] / 1000
    salt = slip * (M["NaCl"] + M["NaOCl"]) / 1000
    s66 = salt / er.A_RL_POL_SALT_WT
    S.set("S66", s66, "kg/d", f"Cl2 slip {er.A_RL_SLIP:.0%} of ALK inlet {c_a_in * M['Cl2'] / 1000:.3f} kg/d -> NaCl + NaOCl {salt:.4f} kg/d at {er.A_RL_POL_SALT_WT:.0%} salts",
          "VENT_SCRUB_EQUIPMENT 2.1", "hypochlorite/chloride scrub liquor", "ambient")
    S.drop("ACID_POLISH_SCRUB")
    S.off("ACID_POLISH_SCRUB", "mass", "in", "make-up water + NaOH", s66 - slip_kg, "level control")
    S.off("ACID_POLISH_SCRUB", "mass", "out", "polished air to stack", S.v("S65") * 24 - slip_kg, "S65 less absorbed Cl2")
    cru = alk_liq + s66 - o2_dec_kg
    S.set("IA-BMED-09", cru, "kg/d", f"IA-BMED-08 {alk_liq:.3f} + S66 {s66:.4f} - O2 {o2_dec_kg:.3f} from decomposing the surplus hypochlorite (2 NaOCl -> 2 NaCl + O2); "
          f"chlorate {e_cru / 6:.1f} mol/d from the sparge share (3 NaOCl -> NaClO3 + 2 NaCl)", "AQS-DUTY-012 CRU split", "NaClO3 / NaCl liquor", f"{A_RM_T_CRU} C",
          na_mol_d=round(na_cru, 1), chlorate_mol_d=round(e_cru / 6, 1), o2_vent_kg_d=round(o2_dec_kg, 3))
    S.drop("ALK_SCRUBBER")
    S.drop("CRU")
    S.off("ALK_SCRUBBER", "mass", "in", "acid-gas air (EW hood sweep + leach lid purge) incl. unabsorbed sparge Cl2 and the surplus anode Cl2 bypass", S.v("S65") * 24 + cl2_abs_kg,
          "S65 basis + Cl2 absorbed (scrubber water evaporation within the S65 saturation basis)")
    if o2_dec_kg > 0:
        S.off("CRU", "mass", "out", "O2 from hypochlorite decomposition (surplus anode Cl2) to the CRU vent", o2_dec_kg, "2 NaOCl -> 2 NaCl + O2 (catalytic); AQS-DUTY-012")
    # ================================================================ 7. digest, cake
    dg = hl.draws()[2]
    naoh_dig = dg["naoh_mol_d"]
    s91 = dg["caustic_L_d"] * er.A_RL_RHO_2M["NaOH"]
    S.set("S91", s91, "kg/d", f"DUTY-008 digest NaOH {naoh_dig:.0f} mol/d as 2 M ({dg['caustic_L_d']:.0f} L/d x 1.080)", "AQS-DUTY-008 digest", "NaOH 2 M",
          "35 C (55 C after HX-10)", mol_d=naoh_dig)
    glass = hl.CULLET_KG_D
    sio2_mol = glass * hl.GLASS_FRAC[0] / 60.08 * 1000
    na_glass = 2 * glass * hl.GLASS_FRAC[1] / 61.98 * 1000
    insol = glass * A_RM_GLASS_INSOL
    purge_d = dg["purge_water_kg_d"]
    s92 = s91 + glass - insol - purge_d
    S.set("S92", s92, "kg/d", f"S91 {s91:.2f} + dissolved cullet {glass - insol:.2f} (SiO2 + Na2O) - lid purge water {purge_d}", "AQS-DUTY-011 digest balance",
          "sodium silicate liquor", "~80 C", sio2_mol_d=round(sio2_mol, 1), na_mol_d=round(naoh_dig + na_glass, 1))
    S.set("S08G", insol, "kg/d", f"insoluble cullet fraction {A_RM_GLASS_INSOL:.2f} x {glass} (CaO/MgO/Al2O3 residue, dried)", "AQS-DUTY-011 digest balance; soda-lime composition",
          "digest residue (glass-ceramic filler grade)", "dried")
    S.drop("GLASS_DIGEST", "mass")
    S.off("GLASS_DIGEST", "mass", "out", "lid purge vapor to HDR_CAUSTIC", purge_d, "DUTY-008 digest purge")
    u_hyd = sum(diss[m] * (1 - f_plate) * (M[m] + N_E[m] * 17.007) / M[m] for m in EW_METALS)
    dsp = min(na_glass, al_mol)
    cake_dry = (sio2_mol - dsp) * 60.08 / 1000 + dsp * 142.05 / 1000 + (al_mol - dsp) * 78.0 / 1000 + u_hyd
    s97 = cake_dry / A_RM_CAKE_SOLIDS
    S.set("S97", s97, "kg/d", f"cake dry {cake_dry:.2f} kg/d (SiO2 {(sio2_mol - dsp) * 0.06008:.2f}, NaAlSiO4 {dsp * 0.14205:.2f}, Al(OH)3 {(al_mol - dsp) * 0.078:.2f}, M(OH)n {u_hyd:.2f}) at {A_RM_CAKE_SOLIDS:.0%} solids",
          "AQS-DUTY-011 pH-shift stoichiometry", "filter cake", "ambient", dry_kg_d=round(cake_dry, 2), na_retained_mol_d=round(dsp, 1))
    D["salt"] = dict(sio2_mol=sio2_mol, na_glass=na_glass, al_mol=al_mol, dsp_mol=dsp, cake_dry=cake_dry, u_hyd=u_hyd, insol=insol)
    h09 = S.v("S09") / er.A_RL_RHO_2M["HCl"] * er.A_RL_M_REAGENT
    h01 = S.v("IA-BMED-01") / er.A_RL_RHO_2M["HCl"] * er.A_RL_M_REAGENT
    n02 = S.v("IA-BMED-02") / er.A_RL_RHO_2M["NaOH"] * er.A_RL_M_REAGENT
    D["fab"] = dict(h09=h09, h01=h01, n02=n02)
    # ================================================================ 8. ZnBr2, farm, UPW
    S.drop("ZNBR2", "mass")
    S.drop("ZNBR2_BR2_REGEN", "mass")
    dry = er.A_RL_BR2_PURGE_M3_H * er.rho_air(25.0) / (1 + er.A_RL_W_AMB) * 24
    vap_in = dry * er.A_RL_W_AMB
    w_eq = A_RM_ZNBR2_AW * er.w_sat(25.0)
    evap = dry * (w_eq - er.A_RL_W_AMB) * A_RM_ZNBR2_APPROACH
    br2 = er.A_RL_BR2_PURGE_M3_H * er.A_RL_BR2_PPMV * 1e-6 * (M["Br2"] / 24.465) * 24
    naoh_kg = br2 / M["Br2"] * 2 / er.A_RL_M_REAGENT * er.A_RL_RHO_2M["NaOH"]
    S.set("S69", dry + vap_in + evap + br2, "kg/d",
          f"purge {er.A_RL_BR2_PURGE_M3_H} m3/h: dry air {dry:.1f} + ambient water {vap_in:.2f} + electrolyte evaporation {evap:.3f} (aw {A_RM_ZNBR2_AW}, {A_RM_ZNBR2_APPROACH:.0%} approach) + Br2 {br2:.4f}",
          "hub VENT_SCRUB_EQUIPMENT 2.2; AQS-DUTY-011", "moist air + Br2 vapor", "25 C, atm", br2_kg_d=round(br2, 4), evap_kg_d=round(evap, 3))
    S.set("S69B", br2 + naoh_kg, "kg/d", f"Br2 {br2:.4f} + NaOH make-up {naoh_kg:.4f}; purge humidity not condensed (scrub at ambient, outlet below saturation)",
          "Br2 + 2 NaOH -> NaBr + NaOBr + H2O", "NaBr/NaOBr liquor", "ambient")
    mk = evap - naoh_kg
    S.off("ZNBR2", "mass", "in", "purge air (dry)", dry, "headspace purge")
    S.off("ZNBR2", "mass", "in", "purge air ambient humidity", vap_in, "w 0.010")
    S.off("ZNBR2", "mass", "in", "UPW electrolyte make-up (HDR_UPW)", mk, "evaporation less S69B water")
    S.off("ZNBR2_BR2_REGEN", "mass", "in", "2 M NaOH make-up", naoh_kg, "stoichiometric")
    S.off("ZNBR2_BR2_REGEN", "mass", "out", "scrubbed moist air to stack", dry + vap_in + evap, "")
    D["znbr2"] = dict(evap=evap, makeup=mk, dry=dry)
    gtmp = copy.deepcopy(g)
    Et = {e["stream_id"]: e for e in gtmp["edges"]}
    for sid in ("S85", "S89", "S90", "S73", "S74", "S49", "S45", "S64"):
        Et[sid]["rate"] = dict(Et[sid]["rate"], value=S.v(sid))
    tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    json.dump(gtmp, tmp)
    tmp.close()
    cc = co2.main(tmp.name)
    os.unlink(tmp.name)
    oa, oa_min = cc["farm"]["oa_required_m3_h"], cc["farm"]["oa_min_m3_h"]
    ps = er.psat_kpa(er.A_RL_FARM_T_C) * er.A_RL_FARM_RH
    w_farm = 0.622 * ps / (101.325 - ps)
    rho_d = er.rho_air(25.0) / (1 + er.A_RL_W_AMB)
    vapf = (oa * co2.A_PHOTO_H + oa_min * (24 - co2.A_PHOTO_H)) * rho_d * (w_farm - er.A_RL_W_AMB)
    et = er.A_RL_ET_L_M2_D * co2.A_CANOPY_M2
    s13 = et - vapf
    S.set("S13", s13, "kg/d", f"ET {et:.1f} - farm exhaust vapor {vapf:.1f} (OA {oa} m3/h light, {oa_min} dark)", "AQS-DUTY-009 OA; ET class", "farm sump + AHU condensate",
          "~15 C", oa_m3_h=oa)
    s04, s11, s02 = c["s04"], c["s11"], c["s02"]
    o2p = s04 * M["O2"] / M["CO2"]
    s89 = S.v("S89")
    gb_out = s13 + S.v("S14") + S.v("S14X") + s11 + s89 + vapf + o2p
    farm_mk = gb_out - (S.v("S07") + s04 + s89)
    s01 = farm_mk + mk
    S.set("S01", s01, "kg/d", f"farm make-up {farm_mk:.2f} (GROW_BED balance) + ZnBr2 electrolyte make-up {mk:.3f}", "AQS-DUTY-011 GROW_BED balance", "UPW", "ambient",
          kind="by_difference")
    S.drop("GROW_BED", "mass")
    S.off("GROW_BED", "mass", "in", "UPW make-up from HDR_UPW", farm_mk, "S01 less ZnBr2 make-up", kind="by_difference")
    S.off("GROW_BED", "mass", "out", "CO2 to farm exhaust", s89, "AQS-DUTY-009 fate")
    S.off("GROW_BED", "mass", "out", "water vapor to farm exhaust", vapf, "OA x humidity rise")
    S.off("GROW_BED", "mass", "out", "photosynthetic O2 to farm exhaust", o2p, "S04 stoichiometry")
    S.drop("HDR_UPW")
    S.off("HDR_UPW", "mass", "out", "farm make-up to GROW_BED", farm_mk, "S01")
    S.off("HDR_UPW", "mass", "out", "ZnBr2 electrolyte make-up", mk, "S01")
    s27, s26 = S.v("S27"), S.v("S26")
    s25 = (s01 + s27 + s26) / (1 - er.A_RL_UPW_REJECT)
    S.set("S25", s25, "kg/d", f"UPW polish demand (S01 {s01:.2f} + S27 {s27} + S26 {s26}) / (1 - reject {er.A_RL_UPW_REJECT})", "AQS-DUTY-011", "distillate", "~40 C")
    S.drop("BMED_UPW_POLISH")
    S.off("BMED_UPW_POLISH", "mass", "out", "fab UPW to FAB_UPW_TANK (S27)", s27, "S27")
    S.off("BMED_UPW_POLISH", "mass", "out", "potable to REMIN (S26)", s26, "S26")
    S.off("BMED_UPW_POLISH", "mass", "out", "polish reject", s25 * er.A_RL_UPW_REJECT, "EDI/RO polish")
    D["farm"] = dict(oa=oa, oa_min=oa_min, vap=vapf, et=et, farm_makeup=farm_mk, o2_photo=o2p, s13=s13)
    # ================================================================ 9. leach loop + salt loop fixed point
    purge = hl.draws()[1]["purge_water_kg_d"]
    slurry = X["undissolved"] + X["liquor"]
    s08 = S.v("S08")
    s29 = c["s29"]
    fixed_in = sum(S.v(s) for s in ("S10", "S16", "S19", "S39", "S68", "S72", "IA-WET-FLOAT-01"))
    rho_l = hl.RHO_LIQ / 1000.0
    s28 = S.v("S28")
    cl2_kg = tot["cl2"]
    cl2_sp_kg = c_sp * M["Cl2"] / 1000
    for it in range(500):
        ins = fixed_in + s28 + feed + tot["dep"] + s95 + cl2_sp_kg
        outs = q_ew + s08 + slurry + purge + (1 - a) * cl2_sp_kg + o2_vent
        rec = outs - ins
        acid = 0.0
        for _ in range(200):
            pol2 = rec - acid - cru
            bleed = raff - pol2
            f_h = bleed / rho_l * A_RM_RAFF_H_M
            cl_bleed = f_h + na_cru + al_e + u_e
            L = cl_bleed - h09
            acid_new = L / er.A_RL_M_REAGENT * er.A_RL_RHO_2M["HCl"]
            if abs(acid_new - acid) < 1e-10:
                break
            acid = acid_new
        pairs = L + h09 + h01
        n_top = pairs - naoh_dig - na_alk - n02
        n_top_req = f_h + al_e + u_e - naoh_dig
        top_kg = n_top / er.A_RL_M_REAGENT * er.A_RL_RHO_2M["NaOH"]
        acid_tr = pairs / er.A_RL_M_REAGENT * er.A_RL_RHO_2M["HCl"]
        base_tr = pairs / er.A_RL_M_REAGENT * er.A_RL_RHO_2M["NaOH"]
        dil = bleed + s92 + top_kg - acid_tr - base_tr - s97
        vcd_feed = s13 + s29 + dil
        s28_new = vcd_feed * (1 - er.A_RL_VCD_REC)
        if abs(s28_new - s28) < 1e-10:
            break
        s28 = s28_new
    S.set("S28", s28, "kg/d", f"VCD brine {1 - er.A_RL_VCD_REC:.0%} of feed {vcd_feed:.1f} (S13 + S29 + S98)", "VCD practice", "VCD brine (NaCl)", "~40 C")
    S.set("IA-REC-01", rec, "kg/d", f"leach balance: recycle = IA-POL-02 {pol2:.1f} + BMED HCl {acid:.1f} + CRU liquor {cru:.2f}",
          "AQS-DUTY-011 leach loop", "regenerated leach liquor", "mixed, see HX-5", line_DN=A_RM_RECYCLE_DN)
    S.set("IA-POL-02", pol2, "kg/d", f"raffinate {raff:.1f} less bleed {bleed:.1f}", "AQS-DUTY-011 leach loop", "raffinate", f"~{A_RM_T_RAFF:.0f} C")
    S.set("IA-BMED-05", bleed, "kg/d", f"POLISH_BANK level: raffinate {raff:.1f} - IA-POL-02 {pol2:.1f}; free HCl {A_RM_RAFF_H_M} M, Al {al_mol:.0f} mol/d, undeposited metal {u_e:.0f} eq/d",
          "AQS-DUTY-011 leach loop", "raffinate brine bleed", f"~{A_RM_T_RAFF:.0f} C", kind="by_difference", cl_mol_d=round(cl_bleed, 1))
    S.set("IA-BMED-06", acid, "kg/d", f"HCl {L:.1f} mol/d = Cl in bleed {cl_bleed:.1f} - fab HCl returning on S10 {h09:.1f}, as 2 M", "AQS-DUTY-011 chloride balance",
          "HCl 2 M", f"{A_RM_T_HCL} C", mol_d=round(L, 1))
    S.set("IA-BMED-10", top_kg, "kg/d", f"BMED pairs {pairs:.1f} - digest {naoh_dig:.0f} - ALK {na_alk:.1f} - fab {n02:.2f} = {n_top:.1f} mol/d NaOH as 2 M (alkalinity need {n_top_req:.1f})",
          "AQS-DUTY-011 salt-loop alkalinity", "NaOH 2 M", "ambient", mol_d=round(n_top, 1))
    S.set("IA-BMED-03", acid_tr, "kg/d", f"acid compartment: {pairs:.1f} mol/d HCl as 2 M (IA-BMED-06 + S09 + IA-BMED-01)", "AQS-DUTY-011 BMED pair balance",
          "salt-loop transfer (Cl- + product water)", "<= 40 C", mol_d=round(pairs, 1))
    S.set("IA-BMED-04", base_tr, "kg/d", f"base compartment: {pairs:.1f} mol/d NaOH as 2 M (S91 + IA-BMED-07 + IA-BMED-10 + IA-BMED-02)", "AQS-DUTY-011 BMED pair balance",
          "salt-loop transfer (Na+ + product water)", "<= 40 C", mol_d=round(pairs, 1))
    S.set("S98", dil, "kg/d", f"salt loop level: bleed {bleed:.1f} + S92 {s92:.1f} + IA-BMED-10 {top_kg:.1f} - transfers {acid_tr + base_tr:.1f} - cake {s97:.2f}",
          "AQS-DUTY-011 salt-loop balance", "diluate (dilute NaCl)", "~35 C", kind="by_difference")
    s99 = vcd_feed - s25 - s28
    S.set("S99", s99, "kg/d", f"VCD feed {vcd_feed:.1f} - S25 {s25:.1f} - S28 {s28:.2f}", "AQS-DUTY-011 VCD balance", "distillate (clean water)", "ambient", kind="by_difference")
    bmed_kg = pairs * (M["HCl"] + M["NaOH"]) / 1000
    p_bmed = pairs * F * A_RN_BMED_V_RU / A_RN_BMED_CE / 86.4e6
    p_bmed_rev_m = bmed_kg * er.A_RL_BMED_KWH_KG / 24
    bmed_kwh_kg_naoh = p_bmed * 24 / (pairs * M["NaOH"] / 1000)
    D["loop"] = dict(rec=rec, pol2=pol2, bleed=bleed, f_h=f_h, cl_bleed=cl_bleed, L=L, pairs=pairs, n_top=n_top, n_top_req=n_top_req, dil=dil,
                     vcd_feed=vcd_feed, s28=s28, s99=s99, s25=s25, bmed_kg_d=bmed_kg, p_bmed_kw=p_bmed, p_bmed_rev_m_basis_kw=p_bmed_rev_m, bmed_kwh_kg_naoh=bmed_kwh_kg_naoh, raff=raff, iterations=it, o2_vent=o2_vent, acid=acid, cru=cru)
    for u in ("POLISH_BANK", "CONTINUOUS_RECYCLE", "SALT_FEED", "BMED_ACID", "BMED_BASE", "VCD_TRAIN"):
        S.drop(u, "mass") if u in R.off else None
    S.drop("LEACH_CSTR_1", "mass")
    S.off("LEACH_CSTR_1", "mass", "in", "fresh shredded feed", feed, "plant basis 150 kg/d wet")
    S.off("LEACH_CSTR_1", "mass", "in", "EW cathode harvest booked onto S08", tot["dep"], "= S08")
    S.off("LEACH_CSTR_1", "mass", "in", "anode Cl2 sparge (share of the EW Cl2 header set by the oxidant demand)", cl2_sp_kg, "AQS-DUTY-012 electron balance")
    S.off("LEACH_CSTR_1", "mass", "out", "slurry to FLOAT_SINK", slurry, "undissolved + 20 wt % liquor")
    S.off("LEACH_CSTR_1", "mass", "out", "purge vapor", purge, "DUTY-008 HX-5 purge")
    S.off("LEACH_CSTR_1", "mass", "out", "unabsorbed Cl2 to lid purge -> ALK_SCRUBBER", (1 - a) * cl2_sp_kg, f"1 - sparge absorption {a}")
    S.off("LEACH_CSTR_1", "mass", "out", "unused O2 to lid purge", o2_vent, f"1 - utilization {A_RM_O2_UTIL}")
    # ================================================================ 10. heat: HX-5, HX-6, Q4 sinks, ladder
    T5 = hl.A_J_T_LEACH
    t_rec = (pol2 * A_RM_T_RAFF + acid * A_RM_T_HCL + cru * A_RM_T_CRU) / rec
    cold = [("S68", S.v("S68"), 4.18, er.A_RL_COIL_T_C), ("S10", S.v("S10"), 4.0, 25.0), ("S16", S.v("S16"), 4.0, 25.0),
            ("S39", S.v("S39"), 4.0, 25.0), ("S72", S.v("S72"), 4.18, 25.0), ("S28", s28, 4.0, A_RM_T_S28)]
    warm = [("IA-REC-01", rec, CP_L, t_rec), ("IA-WET-FLOAT-01", S.v("IA-WET-FLOAT-01"), CP_L, A_RM_T_FLOAT), ("S19", S.v("S19"), 0.8, 25.0)]
    q_hx9 = sum(mm * cp * (A_RM_T_PRE - t) for _, mm, cp, t in cold) / 86400
    q_cold_raw = sum(mm * cp * (T5 - t) for _, mm, cp, t in cold) / 86400
    q_warm = sum(mm * cp * (T5 - t) for _, mm, cp, t in warm) / 86400
    lch = hl.draws()[1]
    q_fix = lch["q_shell_kw"] + lch["q_shred_kw"] + lch["q_purge_kw"]
    q_rx_low = lch["q_exotherm_kw"]
    cu_e = [r for r in lch["reactions"] if r["metal"] == "Cu"][0]["mol_d"] * 2
    q_ox_tot = (e_cl2 * DHE["Cl2"] + e_cru * DHE["ClO3"] + delta * DHE["O2"] - fe_ox_mol * (A_RN_DHF["Fe3+"] - A_RN_DHF["Fe2+"])) / 86400
    q_ox_extra = q_ox_tot - cu_e * DHE["ClO3"] / 86400
    q5_rate = q_warm + q_cold_raw + q_fix - q_rx_low
    q5_norm = q_warm + q_cold_raw - q_hx9 + q_fix - q_rx_low - q_ox_extra
    hx5_rating = ceil_step(q5_rate * hl.A_MARGIN)
    hx9_full = q_hx9
    hx9_trim = 0.0
    if q5_norm < 0:
        hx9_trim = min(-q5_norm, q_hx9)
        q_hx9 -= hx9_trim
        q5_norm += hx9_trim
    q_hx10 = s91 * 3.8 * (A_RM_T_PRE - hl.A_J_T_CAUSTIC) / 86400
    q6_norm = dg["duty_kw"] - q_hx10
    q6_rate = dg["duty_kw"]
    hx6_rating = ceil_step(q6_rate * hl.A_MARGIN)
    base = hl.main()
    _, _, q1_src, q2_src = hl.sources()
    losses = {t: base["stores"][t]["loss_kw"] for t in hl.STORES}
    q4dry = hl.draws()[0]["duty_kw"]
    order_n = [("HX-4", q4dry), ("HX-6", q6_norm), ("HX-5", max(q5_norm, 0.0))]
    run_n = hl.ladder_j(q1_src, q2_src, losses, (0.5, 0.5), h8["duty_kw"], order_n)
    run_s = hl.ladder_j(q1_src, q2_src, losses, (1.0, 0.0), h8["duty_kw"], order_n)
    served = {k: sum(run_n[l]["draws_served"][k] for l in "AB") for k, _ in order_n}
    trim = {k: sum(run_n[l]["trim"][k] for l in "AB") for k, _ in order_n}
    trim_s = {k: run_s["A"]["trim"][k] for k, _ in order_n}
    bus_n = 2 * run_n["A"]["Q4"]["down"]
    q3_down = 2 * run_n["A"]["Q3"]["down"]
    D["heat"] = dict(t_rec=t_rec, q_hx9=q_hx9, q_cold_raw=q_cold_raw, q_warm=q_warm, q_fix=q_fix, q_rx_low=q_rx_low, q_ox_tot=q_ox_tot, q_ox_extra=q_ox_extra,
                     q5_rate=q5_rate, q5_norm=q5_norm, hx5_rating=hx5_rating, q_hx10=q_hx10, q6_norm=q6_norm, q6_rate=q6_rate, hx6_rating=hx6_rating,
                     served=served, trim=trim, trim_single=trim_s, bus_n=bus_n, q3_down=q3_down, cold=[(s, round(mm, 2), t) for s, mm, _, t in cold],
                     warm=[(s, round(mm, 2), round(t, 1)) for s, mm, _, t in warm], rev_l_hx5=lch["duty_kw"], rev_l_hx6=dg["duty_kw"], hx9_full=hx9_full, hx9_trim=hx9_trim)
    o2_out = s02 + s95
    asu = o2_out / (er.A_RL_Y_O2 * er.A_RL_ASU_REC)
    stg = er.A_RL_ASU_P ** 0.5
    t2 = 298.15 + 298.15 * (stg ** (0.4 / 1.4) - 1) / er.A_RL_ETA_IS
    w_shaft = 2 * (asu / 86400) * 1.006 * (t2 - 298.15)
    f_q4 = (t2 - 273.15 - hl.A_J_Q4_RET) / (t2 - 273.15 - 25.0)
    sieve = 2 * asu * er.A_RL_W_AMB * 2.5e3 / 86400 * er.A_RL_SIEVE_RECOV
    s54 = w_shaft * f_q4 + sieve
    S.set("S54", s54, "kW", f"ASU air {asu:.1f} kg/d for O2 {o2_out:.2f} kg/d (S02 + S83): shaft {w_shaft:.4f} kW x {f_q4:.3f} + sieve TSA {sieve:.4f}",
          "CRYO_COLD_BOX", "Q4 water", "45 C return / 60 C supply", asu_air_kg_d=round(asu, 1))
    n2 = S.v("S03")
    qc = (o2_out * (0.918 * 208 + 213) + n2 * (1.04 * 221 + 199)) / 86400 * (1 + er.A_RL_COLD_LEAK)
    q_co2 = 0.048
    cop = A_RN_CRYO_ETA * A_RN_CRYO_TC / (A_RN_CRYO_TH - A_RN_CRYO_TC)
    p_cryo = (qc + q_co2) / cop
    cryo = dict(qc_o2_n2_kw=qc, q_co2_kw=q_co2, cop=cop, p_kw=p_cryo, rev_m_kw=er.A_RL_STIRLING_KW, o2_out_kg_d=o2_out, n2_kg_d=n2,
                p_kw_co2_at_253K=qc / cop + q_co2 / (A_RN_CRYO_ETA * 253.15 / (A_RN_CRYO_TH - 253.15)))
    S.set("S55", p_cryo + qc + q_co2, "kW", f"cold-head reject = electric {p_cryo:.4f} + lift {qc + q_co2:.4f} kW (O2/N2 {qc:.4f} + CO2 condensing {q_co2}); "
          f"electric = lift / ({A_RN_CRYO_ETA} x Carnot COP {A_RN_CRYO_TC:.0f}/{A_RN_CRYO_TH - A_RN_CRYO_TC:.0f} K)", "AQS-DUTY-012 WP-CRYO-DUTY; CRYO_COLD_BOX; HEAT_LADDER_DUTIES 9",
          "glycol 30 %", "dT 5 K", electric_kw=round(p_cryo, 4), lift_kw=round(qc + q_co2, 4), vendor_no_load_floor="RS-CRYO-VENDOR")
    S.drop("CRYO_O2")
    S.off("CRYO_O2", "mass", "in", "liquid O2 from the cold box", o2_out, "ASU recovery basis")
    if "CRYO_N2" in R.off:
        S.drop("CRYO_N2")
    S.off("CRYO_N2", "mass", "in", "N2 from the cold box", n2, "= S03")
    s80 = c["s80"]
    q4_in = bus_n + s54 + S.v("S63") + s80
    life = 3.0
    s102 = q4_in - life - q_hx9 - q_hx10
    S.set("S100", q_hx9, "kW", f"HX-9: make-up {', '.join(s for s, *_ in cold)} to {A_RM_T_PRE} C", "AQS-DUTY-011", "Q4 water", "60 C supply / 45 C return",
          duty_normal_kw=round(q_hx9, 4), duty_rated_kw=round(hx9_full * hl.A_MARGIN, 3), hx9_trim_kw=round(hx9_trim, 4),
          trim_note="HX-9 preheat reduced by the leach heat surplus (exotherm + oxidant credit above the HX-5 demand); leach temperature held by the make-up preheat" if hx9_trim > 0 else "")
    S.set("S101", q_hx10, "kW", f"HX-10: S91 {s91:.1f} kg/d x 3.8 x ({A_RM_T_PRE} - {hl.A_J_T_CAUSTIC}) C", "AQS-DUTY-011", "Q4 water", "60 C supply / 45 C return",
          duty_normal_kw=round(q_hx10, 4), duty_rated_kw=round(q_hx10 * hl.A_MARGIN, 3))
    S.set("S102", s102, "kW", f"Q4 bus in {q4_in:.3f} - life {life} - HX-9 {q_hx9:.3f} - HX-10 {q_hx10:.3f}", "AQS-DUTY-011 Q4 balance", "Q4 water -> GHEX glycol",
          "60 C supply", kind="by_difference", duty_normal_kw=round(s102, 4), duty_rated_kw=round(max(s102, 0) * hl.A_MARGIN, 3))
    D["q4"] = dict(bus_n=bus_n, s54=s54, s63=S.v("S63"), s80=s80, q4_in=q4_in, life=life, s100=q_hx9, s101=q_hx10, s102=s102, rev_l_surplus=3.3167)
    # ================================================================ 11. electrical
    pv_rows, pv_sum = pv_load()
    pvm = int(pv_sum["worst_month"])
    dec = [p for mo, _, _, p in pv_rows if mo == pvm]
    s93 = sum(dec) / len(dec)
    S.set("S93", s93, "kW", f"worst-month (month {pvm}) mean of the hourly TMY run: {s93 * 24:.1f} kWh/d DC from 70 kWp; annual mean {pv_sum['annual_mean_kw']:.3f} kW "
          f"({pv_sum['annual_kwh_per_kwp']:.0f} kWh/kWp.yr)", "AQS-DUTY-012 WP-PV-ESS; pvlib + PVGIS 5.2 TMY (33.0 N, 96.8 W)", "DC", "PV input",
          peak_kw=70.0, design_month=pvm, annual_mean_kw=pv_sum["annual_mean_kw"], annual_kwh_per_kwp=pv_sum["annual_kwh_per_kwp"],
          monthly_mean_kw={str(k): v["mean_kw"] for k, v in pv_sum["monthly"].items()}, peak_dc_kw_tmy=pv_sum["peak_dc_kw"])
    p_ew = tot["p_kw"]
    rect_dc = p_ew + p_bmed + A_RM_PK_KW
    s17 = rect_dc / A_RM_RECT_ETA
    bmed_rating = math.ceil(p_bmed * hl.A_MARGIN)
    S.set("S17", s17, "kW", f"(EW {p_ew:.3f} + BMED {p_bmed:.3f} + PK {A_RM_PK_KW}) / {A_RM_RECT_ETA}", "AQS-DUTY-012 per-cell partition + BMED V_ru basis", "AC to rectifiers", "480 V",
          rect_ew_kw=round(p_ew, 3), rect_bmed_kw=round(p_bmed, 3), rect_bmed_rating_kw=bmed_rating)
    S.set("S20", 5.0, "kW", "GROW_BED LED canopy share (graph continuous_kw 5.0)", "graph GROW_BED continuous_kw", "AC load", "bus")
    gb_trim = hl.sources()[1]["q_trim_electric_kw"]
    loads = [
        ("MFG_SHOP", 12.0), ("HABITATION", 3.0), ("CRYO cold head (duty / 0.16 Carnot)", p_cryo), ("LEACH_CSTR_1 parasitics", 2.0),
        ("WAFER_FAB", 2.0), ("WET_BENCH", 1.0), ("AFTERBURNER", 0.5), ("ALK_SCRUBBER", 0.4), ("H2_DRYER", 0.3), ("MEOH_SYNTH", 0.5),
        ("NUTRIENT_DOSE", 0.1), ("GLASS_RINSE", 0.2), ("GLASS_MILL", 0.8), ("GLASS_BURNOUT electric trim", gb_trim), ("LITHO_STUB", 0.1),
        ("ELECTRODE_COAT", 0.3), ("BLOW_MOLD", 0.5), ("SOLAR_PV_CELL", 1.0), ("UPW polish (EDI)", 0.1),
        ("VCD_TRAIN", vcd_feed / 1000 * A_RM_VCD_KWH_M3 / 24), ("ASU compressor", w_shaft / 0.9), ("hydro pump", S.v("S23") / A_RM_HYDRO_PUMP_ETA),
        ("HX-4 trim", trim["HX-4"]), ("HX-5 trim", trim["HX-5"]), ("HX-6 trim", trim["HX-6"]), ("GEO_HP (idle)", 0.0),
    ]
    s94 = sum(x for _, x in loads)
    S.set("S94", s94, "kW", "sum of itemized daily-average AC loads (LOAD_AGG balance terms)", "graph node continuous_kw + AQS-DUTY-011 trims", "AC", "bus")
    if "LOAD_AGG" in R.off:
        S.drop("LOAD_AGG")
    for lab, x in loads:
        S.off("LOAD_AGG", "energy", "out", lab, x, "daily average")
    if "RECTIFIER" in R.off:
        S.drop("RECTIFIER")
    S.off("RECTIFIER", "energy", "out", "RECT-EW DC to EW cells", p_ew, "sum of cell current x V_cell (AQS-DUTY-012)")
    S.off("RECTIFIER", "energy", "out", "RECT-BMED DC to BMED stack", p_bmed, f"{pairs:.1f} pairs/d x F x {A_RN_BMED_V_RU} V / CE {A_RN_BMED_CE}")
    S.off("RECTIFIER", "energy", "out", "RECT-PK DC", A_RM_PK_KW, "ELECTRICAL < 0.5 kW")
    S.off("RECTIFIER", "energy", "out", "conversion loss", s17 - rect_dc, f"1 - {A_RM_RECT_ETA}")
    ac = s17 + s94 + 5.0
    inv = ac * A_RM_INV_LOSS
    led = S.v("S20")
    ess = ess_sim(pv_rows, ac - led, led, c["s79"], S.v("IA-ESS-HYDRO-ELEC"))
    em = ess["monthly"][pvm]
    S.set("IA-ESS-ZNBR2-CHG", em["chg"], "kW", f"hourly SOC simulation, month {pvm} mean: charge only from PV above the bus load; {em['cycles_per_day']:.3f} equivalent cycles/d",
          "AQS-DUTY-012 WP-PV-ESS; FLOW_BATTERY (105 kWh usable, 60 kW, RTE 0.75, self-discharge 3 %/d)", "DC", "bus", peak_kw=60.0,
          annual_mean_kw=round(ess["annual"]["chg"], 4), soc_max_kwh=round(em["soc_max_kwh"], 2))
    S.set("IA-ESS-ZNBR2-DIS", em["dis"], "kW", f"hourly SOC simulation, month {pvm} mean discharge to the bus", "AQS-DUTY-012 WP-PV-ESS; FLOW_BATTERY", "DC", "bus",
          peak_kw=60.0, annual_mean_kw=round(ess["annual"]["dis"], 4))
    S.drop("ZNBR2", "energy")
    S.off("ZNBR2", "energy", "out", "conversion loss (sqrt(RTE) each way)", em["conv"], "FLOW_BATTERY 70-80 % DC-DC")
    S.off("ZNBR2", "energy", "out", "self-discharge", em["sd"], f"{A_RN_ESS_SD:.0%} of SOC per day (FLOW_BATTERY 'a few percent per day')")
    if abs(em["dsoc_kw"]) > 1e-9:
        S.off("ZNBR2", "energy", "out" if em["dsoc_kw"] > 0 else "in", "state-of-charge change over the month", abs(em["dsoc_kw"]), "hourly simulation", kind="accumulation")
    sup = s93 + S.v("IA-ESS-ZNBR2-DIS") + S.v("IA-ESS-HYDRO-ELEC") + c["s79"]
    pv_exp = em["exp"]
    dem_e = ac + S.v("IA-ESS-ZNBR2-CHG") + inv + pv_exp
    grid = dem_e - sup
    if "SOL_ARK_60K" in R.off:
        S.drop("SOL_ARK_60K")
    S.off("SOL_ARK_60K", "energy", "out", "inverter / charger conversion loss", inv, f"{A_RM_INV_LOSS:.0%} of AC delivered")
    if pv_exp > 0:
        S.off("SOL_ARK_60K", "energy", "out", "PV surplus not stored (export at the GRID port or curtailment)", pv_exp, "hourly simulation, design month")
    S.off("SOL_ARK_60K", "energy", "in", "utility import at the GRID port (ELECTRICAL AQS-ELC-001 Rev B)", grid, "bus balance", kind="by_difference")
    if "GEO_GHEX" in R.off:
        S.drop("GEO_GHEX")
    S.off("GEO_GHEX", "energy", "out", "heat to ground (borefield recharge)", s102, "S102")
    D["elec"] = dict(pv=s93, p_ew=p_ew, p_bmed=p_bmed, bmed_rating_kw=bmed_rating, s17=s17, s94=s94, loads=loads, inv=inv, grid=grid, supply=sup, demand=dem_e,
                     grid_kwh_d=grid * 24, ew_issued_kw=6.0, w_shaft=w_shaft, p_cryo=p_cryo, cryo=cryo, ess=ess, pv_month=pvm, ac=ac, pv_export=pv_exp)
    for u in ("LEACH_CSTR_1", "GLASS_DIGEST", "Q4_BUS", "OIL_DRYER", "AFTERBURNER"):
        if u in R.off:
            S.drop(u, "energy")
    S.off("OIL_DRYER", "energy", "out", "dryer duty (evaporation)", q4dry, "DUTY-008")
    S.off("OIL_DRYER", "energy", "in", "electric trim", trim["HX-4"], "AQS-DUTY-011 ladder run")
    S.off("LEACH_CSTR_1", "energy", "in", "electric trim (ladder short)", trim["HX-5"], "AQS-DUTY-011 ladder run")
    S.off("LEACH_CSTR_1", "energy", "out", "HX-5 duty, normal (streams + shell + shred + purge - exotherm incl. Cl2/O2 oxidant credit)", max(q5_norm, 0.0), "AQS-DUTY-011")
    S.off("LEACH_CSTR_1", "energy", "out", "HX-9 make-up preheat duty", q_hx9, "S100")
    S.off("GLASS_DIGEST", "energy", "in", "electric trim", trim["HX-6"], "AQS-DUTY-011 ladder run")
    S.off("GLASS_DIGEST", "energy", "out", "HX-6 duty after HX-10 caustic preheat", q6_norm, "AQS-DUTY-011")
    S.off("GLASS_DIGEST", "energy", "out", "HX-10 caustic preheat duty", q_hx10, "S101")
    S.off("Q4_BUS", "energy", "out", "life load (hab + farm)", life, "DUTY-008 q4_life_kw")
    s = hl.sources()[0]
    S.off("AFTERBURNER", "energy", "in", "NCG heat release", s["q_release_kw"], "DUTY-008")
    S.off("AFTERBURNER", "energy", "in", "S11 trim heat release", c["q_s11"], f"{c['s11_dm']:.3f} kg/d DM x {A_RM_S11_LHV} MJ/kg")
    S.off("AFTERBURNER", "energy", "out", "shell loss", s["q_shell_kw"], "DUTY-008")
    S.off("AFTERBURNER", "energy", "out", "HX-7 to burnout", s["q_hx7_kw"], "DUTY-008")
    S.off("AFTERBURNER", "energy", "out", "flue sensible to KO (+ S11 heat)", s["q_flue_to_ko_kw"] + c["q_s11"], "DUTY-008 + S11")
    for lad in "AB":
        for k, tsup, tret, rated in (("HX-5", 95.0, 85.0, q5_rate * hl.A_MARGIN), ("HX-6", 95.0, 90.0, q6_rate * hl.A_MARGIN), ("HX-4", 95.0, 85.0, q4dry * hl.A_MARGIN)):
            sid = f"HL-Q3-{lad}-{k.replace('-', '')}"
            p = hl.pumped(rated, hl.WATER_Q4 | dict(name="treated water (Q3 jacket loop, pressurized)", rho=962.0, cp=4.21), tsup, tret)
            nrm = run_n[lad]["draws_served"][k]
            S.rates[sid] = dict(value=round(rated, 3), unit="kW", note=f"rated {rated:.3f} kW = {k} rating-case duty x {hl.A_MARGIN}; normal {nrm:.3f} kW (AQS-DUTY-011 ladder run)",
                                params=dict(p, duty_rated_kw=round(rated, 3), duty_normal_kw=round(nrm, 3), exchanger=k,
                                            trim_normal_kw_per_ladder=round(run_n[lad]["trim"][k], 3), trim_single_kw=round(trim_s[k], 3)))
    return S


def element_balances(g, S, ctx):
    """WP-BAL-SPECIES: element balances (mol/d) on the chloride loop with absolute tolerances."""
    D = S.decisions
    ewm = ctx["ewm"]
    es, el, lp = ewm["summary"], D["electrons"], D["loop"]
    b = lp["bleed"] / lp["raff"]
    e_frac = D["ew"]["entrained"] / lp["raff"]
    raff_v = lp["raff"] / hl.RHO_LIQ
    X = S.X
    diss, f = X["diss"], X["f_plate"]
    metals = [m for m in EW_METALS]

    def base_species(pool, scale=1.0):
        d = {m: 0.0 for m in metals}
        d["Fe"] = (pool.get("Fe2", 0) + pool.get("Fe3", 0)) * scale
        d["Cu"] = (pool.get("Cu1", 0) + pool.get("Cu2", 0)) * scale
        for m in metals:
            if m not in ("Fe", "Cu"):
                d[m] = pool.get(m, 0.0) * scale
        return d

    def charge(pool, scale=1.0):
        q = 2 * pool.get("Fe2", 0) + 3 * pool.get("Fe3", 0) + pool.get("Cu1", 0) + 2 * pool.get("Cu2", 0)
        q += sum(pool.get(m, 0.0) * N_E[m] for m in metals if m not in ("Fe", "Cu"))
        return q * scale

    R_al, R_na = es["al_mol"] / es["vol"]["b"], el["na_cru"] / es["vol"]["b"]
    H_R = A_RM_RAFF_H_M * 1000 * raff_v
    raff = ewm["raff"]
    sp_raff = base_species(raff)
    sp_raff.update(Al=R_al, Na=R_na, Cl=H_R + R_na + 3 * R_al + charge(raff))
    sp_entr = {k: v * e_frac for k, v in sp_raff.items()}
    feed = ewm["feed"]
    sp_feed = base_species(feed)
    H_in = H_R * (1 + e_frac) + el["n_e_h2"]
    sp_feed.update(Al=R_al * (1 + e_frac), Na=R_na * (1 + e_frac), Cl=H_in + R_na * (1 + e_frac) + 3 * R_al * (1 + e_frac) + charge(feed))
    dep = {m: ewm["dep"][m] for m in metals}
    cl2_cl = 2 * el["cl2_mol"]
    pol_frac = lp["pol2"] / lp["raff"]
    sp_pol2 = {k: v * pol_frac for k, v in sp_raff.items()}
    u = {m: diss[m] * (1 - f) * 1000 / M[m] for m in metals}
    sp_bleed = dict(u, Al=es["al_mol"], Na=el["na_cru"], Cl=lp["cl_bleed"])
    dis = {m: diss[m] * 1000 / M[m] for m in metals}
    out = {}

    def chk(name, elem, ins, outs, note=""):
        vals = [v for v in list(ins.values()) + list(outs.values()) if abs(v) > 1e-12]
        tol = max(TOL_EL_FLOOR, TOL_EL_FRAC * min(abs(v) for v in vals)) if vals else TOL_EL_FLOOR
        a, c = sum(ins.values()), sum(outs.values())
        out[f"{name}/{elem}"] = dict(element=elem, in_total=round(a, 6), out_total=round(c, 6), residual=round(a - c, 6), tol_abs=round(tol, 6),
                                     status="closed" if abs(a - c) <= tol else "OPEN", ins={k: round(v, 6) for k, v in ins.items()},
                                     outs={k: round(v, 6) for k, v in outs.items()}, note=note)
    for elem in ("Fe", "Cu", "Zn", "Au", "Ag", "Al", "Na", "Cl"):
        ins = {"IA-EW-04": sp_feed[elem]}
        outs = {"IA-EW-09 raffinate": sp_raff[elem], "harvest entrainment (S16)": sp_entr[elem]}
        if elem in dep:
            outs["cathode deposit (S08)"] = dep[elem]
        if elem == "Cl":
            outs["anode Cl2"] = cl2_cl
        chk("EW_TRAIN", elem, ins, outs, "EW_1..EW_9 lumped; feed Cl by charge balance (H+ in = raffinate H+ + HER H+)")
    for elem in ("Fe", "Cu", "Zn", "Al", "Na", "Cl"):
        chk("POLISH_BANK", elem, {"IA-EW-09": sp_raff[elem]}, {"IA-POL-02": sp_pol2[elem], "IA-BMED-05 bleed": sp_bleed[elem]},
            "bleed composition from the leach-loop definitions (undeposited metal, Al, CRU Na, Cl by charge); IA-POL-02 at raffinate composition")
    for elem in ("Fe", "Cu", "Zn", "Al", "Na", "Cl"):
        ins = {"IA-POL-02": sp_pol2[elem], "S16 entrained electrolyte": sp_entr[elem]}
        if elem in dis:
            ins["metal dissolved (off-graph)"] = dis[elem]
        if elem == "Al":
            ins["Al dissolved (off-graph)"] = es["al_mol"]
        if elem == "Na":
            ins["IA-BMED-09 CRU liquor"] = el["na_cru"]
        if elem == "Cl":
            ins["IA-BMED-06 HCl"] = lp["L"]
            ins["S10 fab HCl"] = D["fab"]["h09"]
            ins["IA-BMED-09 CRU liquor (NaCl + NaClO3)"] = el["na_cru"]
            ins["anode Cl2 absorbed (sparge)"] = 2 * A_RM_CL2_SPARGE * el["cl2_sparge_mol"]
            outs = {"IA-EW-04": sp_feed[elem]}
        else:
            outs = {"IA-EW-04": sp_feed[elem]}
        chk("LEACH_CSTR_1", elem, ins, outs, "IA-REC-01 composition = IA-POL-02 + IA-BMED-06 + IA-BMED-09 (CONTINUOUS_RECYCLE mixing, not separately checked); "
            "slurry liquor to FLOAT_SINK returns on IA-WET-FLOAT-01 at leach composition (assumed); S28/S98 salt content not modelled (assumed nil)")
    sd = D["salt"]
    for elem in ("Fe", "Cu", "Zn", "Al", "Si"):
        if elem == "Si":
            ins, outs = {"S92 dissolved silica": sd["sio2_mol"]}, {"S97 cake SiO2 + NaAlSiO4": (sd["sio2_mol"] - sd["dsp_mol"]) + sd["dsp_mol"]}
        elif elem == "Al":
            ins, outs = {"IA-BMED-05": sp_bleed["Al"]}, {"S97 cake Al(OH)3 + NaAlSiO4": (sd["al_mol"] - sd["dsp_mol"]) + sd["dsp_mol"]}
        else:
            ins = {"IA-BMED-05": b * sp_raff[elem]}
            outs = {"S97 cake M(OH)n": u[elem]}
        chk("SALT_FEED", elem, ins, outs, "bleed metal at raffinate composition x bleed fraction; cake hydroxide from the undeposited metal")
    chk("ALK_CRU", "Cl", {"Cl2 to ALK (unabsorbed sparge + surplus)": 2 * el["c_a_in"]}, {"IA-BMED-09 (NaCl + NaClO3)": el["na_cru"]},
        "Cl2 + 2 NaOH; slip via ACID_POLISH_SCRUB and S66 to CRU")
    chk("ALK_CRU", "Na", {"IA-BMED-07": el["na_alk"], "polish scrub NaOH (S66)": el["na_pol"]}, {"IA-BMED-09": el["na_cru"]}, "")
    return out, dict(feed=sp_feed, raff=sp_raff, bleed=sp_bleed, pol2=sp_pol2, entr=sp_entr)


def species_n(g, S, ctx):
    out = rm.species(g, S)
    D = S.decisions
    el, lp = D["electrons"], D["loop"]
    sup = el["e_cl2"] + el["e_cru"] + el["o2_e"]
    out["LEACH/electrons"] = dict(in_total=round(sup, 1), out_total=round(el["demand"], 1), residual=round(sup - el["demand"], 3),
                                  status="closed" if abs(sup - el["demand"]) <= 0.01 else "OPEN",
                                  note="oxidant e- (Cl2 sparge share + chlorate + O2) = fresh metal e- (Fe as Fe(III)) + Al + returning Fe(II)/Cu(I)")
    cath = el["cathodic_total"]
    leach_ox = el["demand"]
    lhs = cath
    rhs = leach_ox - el["u_e"] - el["al_e"] + el["n_e_h2"]
    out["EW/electrons"] = dict(in_total=round(lhs, 2), out_total=round(rhs, 2), residual=round(lhs - rhs, 4),
                               status="closed" if abs(lhs - rhs) <= max(0.01, 1e-4 * lhs) else "OPEN",
                               note="cathodic e- = leach oxidation - bleed metal charge - Al + HER e- (steady state, oxidation states carried)")
    cl_in = lp["L"] + el["na_cru"] + D["fab"]["h09"] + 2 * A_RM_CL2_SPARGE * el["cl2_sparge_mol"]
    cl_out = 2 * el["cl2_mol"] + lp["cl_bleed"]
    out["LEACH_LOOP/Cl"] = dict(in_total=round(cl_in, 1), out_total=round(cl_out, 1), residual=round(cl_in - cl_out, 3),
                                status="closed" if abs(cl_in - cl_out) <= 0.01 * cl_in else "OPEN",
                                note="Cl in: BMED HCl + CRU (NaCl + NaClO3) + fab HCl on S10 + absorbed sparge Cl2; out: all anode Cl2 + bleed")
    return out


NCG = dict(requirement="non-condensable gas management (AQS-DUTY-012 WP-HL-OPS)",
           vent_point="purge connection with isolation valve at the condenser high point (condenser coil in the receiving store); NCG accumulator volume above the condenser",
           detection="condenser vapour-inlet vs condensate-outlet temperature difference logged; rising difference indicates NCG blanketing",
           leak_rate_spec="helium leak test of the sealed loop before charge; acceptance rate from the vendor / RS-HL-NCG",
           fluid_sampling="eutectic loops: sampling interval and low-boiler limit per fluid vendor (RS-HL-NCG); water loops: deaerated charge, dissolved O2 check at charge",
           reference="Reay, Kew & McGlen, Heat Pipes, 6th ed. (2014)")


def node_updates_n(g, S, ctx):
    rm.node_updates(g, S)
    N = {n["unit_id"]: n for n in g["nodes"]}
    pv = N["VCD_TRAIN"]["params"]
    if pv.get("feed_m3_d_rated", 0) < 0.40:
        # P8: the issued VCD rating (Rev M, 0.40 m3/d) is held; the Rev N feed is within it.
        pv.update(feed_m3_d_rated=0.40, rating_note_rev_n=f"Rev N feed {pv['feed_m3_d']} m3/d is within the Rev M issued rating 0.40 m3/d; rating held (P8, AQS-DUTY-012)")
    E = {e["stream_id"]: e for e in g["edges"]}
    D = S.decisions
    ewm = ctx["ewm"]
    el = D["elec"]
    ck = N["RECTIFIER"].get("continuous_kw")
    if isinstance(ck, dict):
        ck.update(value=round(el["s17"], 2), note=f"Rev N: (EW {el['p_ew']:.2f} + BMED {el['p_bmed']:.2f} + PK 0.5 kW DC) / 0.95 (AQS-DUTY-012)")
    cells = ewm["cells"]
    i7 = next(c for c in cells if c["cell"] == "EW_7")
    others = [c for c in cells if c["cell"] != "EW_7"]
    N["RECTIFIER"]["params"]["ratings_rev_n"] = dict(
        doc="AQS-DUTY-012",
        RECT_EW=dict(dc_kw=round(el["p_ew"], 2), rating_kw=math.ceil(1.25 * el["p_ew"]), rev_m_issued_kw=el["ew_issued_kw"],
                     cell_current_A={c["cell"]: round(c["I_A"], 1) for c in cells},
                     topology=(f"cell currents differ by two orders of magnitude ({min(c['I_A'] for c in others):.0f}-{max(c['I_A'] for c in others):.0f} A on EW_1-6/8/9, "
                               f"{i7['I_A']:.0f} A on EW_7), so the single series string (0-36 V, 0-250 A) is replaced by per-cell current-controlled channels; "
                               f"EW_7 needs a dedicated {i7['I_A']:.0f} A / {i7['V_cell']} V ({i7['p_kw']:.1f} kW) channel unless the Fe route changes (RS-EW-SELECT)")),
        RECT_BMED=dict(dc_kw=round(el["p_bmed"], 2), rating_kw=el["bmed_rating_kw"]),
        RECT_PK=dict(dc_kw=0.5))
    ck = N["BMED_UPW_POLISH"].get("continuous_kw")
    if isinstance(ck, dict):
        ck["note"] = f"Rev N: BMED stack is carried on RECTIFIER (RECT-BMED {el['p_bmed']:.2f} kW DC, rating {el['bmed_rating_kw']} kW; AQS-DUTY-012); UPW polish EDI ~0.1 kW"
    ck = N["CRYO_H2"].get("continuous_kw")
    if isinstance(ck, dict):
        ck.update(value=round(el["p_cryo"], 2), note=f"Rev N: cold-head electric = lift {el['cryo']['qc_o2_n2_kw'] + el['cryo']['q_co2_kw']:.3f} kW / (0.16 x Carnot COP at 90 K) "
                  f"= {el['p_cryo']:.2f} kW (AQS-DUTY-012); vendor no-load floor RS-CRYO-VENDOR; was 4.0 kW study band")
    for c in ewm["cells"]:
        p = N[c["cell"]].setdefault("params", {})
        p["rev_n_cell"] = dict(doc="AQS-DUTY-012", metal=c["metal"], V_cell=c["V_cell"], ce_her_only=c["ce_her_only"], ce_derived=round(c["ce_derived"], 4),
                               current_A=round(c["I_A"], 1), dc_kw=round(c["p_kw"], 3), heat_kw=round(c["heat_kw"], 3),
                               partition_mol_e_d=dict(deposit=round(c["ne_dep"], 2), fe3_reduction=round(c["r_fe3"], 2), cu2_reduction=round(c["r_cu2"], 2), h2=round(c["ne_h2"], 2)),
                               cathode_area_m2=round(c["area_m2"], 3), area_basis="A_RN_CATH_AREA: 7 cathodes x 2 faces x 0.35 x 0.45 m inside 600 x 420 x 650 mm (assumption; RS-EW-AREA)",
                               j_A_m2=round(c["j_A_m2"], 1), shuttle_conversion=round(c["x_shuttle"], 4), deposit_single_pass_fraction=round(c["x_needed"], 4),
                               recovery_at_envelope_mass_transfer_limit=round(c["recovery_at_envelope"], 3), recovery_basis_f_plate=round(S.X["f_plate"], 4),
                               area_required_m2_by_km=c["area_required_m2"], i_lim_deposit_A_m2=round(c["i_lim_A_m2"], 1),
                               envelope_adequate=bool(min(c["area_required_m2"].values()) <= c["area_m2"] and (c["metal"] != "Fe" or c["area_at_j_fe_m2"] <= c["area_m2"])))
    p = N["EW_7"]["params"]
    c7 = ewm["cells"][6]
    p["fe_ew_basis"] = dict(doc="AQS-DUTY-012", catholyte="process liquor, pH ~1 (0.10 M free HCl), ~%.1f M Cl-" % ewm["summary"]["cl_raff_M"],
                            separator="membrane-divided (cation exchange membrane) required to keep anode Cl2 and Fe3+ off the cathode; RS-EW-CE",
                            anode="Cl2 evolution on Ti/RuO2-TiO2 (DSA) or graphite (WP-ELC-MAT; Ni excluded)", cathode="Ti blank (Liu et al. 2025)",
                            V_cell=c7["V_cell"], ce_her_only=c7["ce_her_only"], ce_source="Liu et al. 2025, case B2 (0.3 M FeCl3 + 1 M NaCl, 80 C, 30 mA/cm2): FE 41.5 %",
                            kwh_per_kg=round(c7["p_kw"] * 24 / c7["dep_kg"], 2), design_j_A_m2=A_RN_J_FE, area_at_design_j_m2=round(c7["area_at_j_fe_m2"], 2),
                            envelope_area_m2=round(c7["area_m2"], 3), cascade_concept="AEM-divided, pH 2-3, 3.5-4.6 kWh/kg (Badenhorst 2019; Liu 2025 B1); not adopted: needs neutralisation and an anion-rich catholyte (RS-EW-CE)")
    p = N["LEACH_CSTR_1"]["params"]
    p["orp_basis"] = dict(ewm["summary"]["leach"], doc="AQS-DUTY-012", reference_electrode="Ag/AgCl, saturated KCl (+0.197 V vs SHE at 25 C); probe temperature correction RS-ORP-PROBE",
                          speciation_check="PHREEQC 3.7.3 llnl.dat screening (_rev_n_thermo_study.py); Pitzer database lacks Fe(III)/Cu/Au species (RS-THERMO-PITZER)")
    for t in ("Q1", "Q2", "Q3"):
        for lad in "AB":
            e = E[f"HL-{t}-{lad}-DOWN"]
            e["params"]["ncg_management"] = dict(NCG, p_sat_bar_a=e["params"].get("P_sat_bar_a"), medium=e["params"].get("medium"))
    pv = N["PV_ARRAY"].setdefault("params", {})
    pvs = json.load(open(PV_SUMMARY))
    pv["pv_tmy_rev_n"] = dict(doc="AQS-DUTY-012", model=pvs["model"], site=pvs["site"], annual_kwh=pvs["annual_kwh"], annual_kwh_per_kwp=pvs["annual_kwh_per_kwp"],
                              annual_mean_kw=pvs["annual_mean_kw"], worst_month=pvs["worst_month"], worst_month_mean_kw=pvs["worst_month_mean_kw"],
                              monthly_mean_kw={k: v["mean_kw"] for k, v in pvs["monthly"].items()}, data="docs-authority/data/pv_hourly_tmy_33.0_-96.8.csv")
    z = N["ZNBR2"].setdefault("params", {})
    ess = el["ess"]
    z["ess_sim_rev_n"] = dict(doc="AQS-DUTY-012", usable_kwh=A_RN_ESS_USABLE, p_kw=A_RN_ESS_P, rte=A_RN_ESS_RTE, self_discharge_per_d=A_RN_ESS_SD,
                              monthly={str(m): {k: round(v, 3) for k, v in r.items()} for m, r in ess["monthly"].items()},
                              annual={k: round(v, 3) for k, v in ess["annual"].items()})


def hx8_update(g):
    """HX-8 duty from the per-cell ohmic heat: HX8 node, IA-HX8 and HL-HX8-Q4-A/B (envelope unchanged; plate count re-stated)."""
    N = {n["unit_id"]: n for n in g["nodes"]}
    E = {e["stream_id"]: e for e in g["edges"]}
    hx = hl.hx8()
    p = N["HX8"]["params"]
    p.update(duty_kw=hx["duty_kw"], q_ohmic_kw=hx["q_ohmic_kw"], area_m2=hx["area_m2"], doc_rev_n="AQS-DUTY-012 (cell ohmic heat from the per-cell partition)",
             rev_m_duty_kw=hx["rev_m_duty_kw"], rev_m_q_ohmic_kw=hx["rev_m_q_ohmic_kw"])
    J = hl.main_j()["edges_j"]
    for sid in ("HL-HX8-Q4-A", "HL-HX8-Q4-B", "HL-Q4-A-BUS", "HL-Q4-B-BUS"):
        e, ej = E[sid], J[sid]
        pr = e["params"]
        old = e["rate"]["value"]
        if abs(old - ej["rated"]) < 1e-9:
            continue
        upd = {k: ej[k] for k in ("m_kg_s", "flow_L_min", "line_DN", "line_id_mm", "velocity_m_s", "thermal_relief_L_h") if k in ej and k in pr}
        pr.update(upd, rev_m_value=old, duty_rated_kw=ej["rated"], doc="AQS-DUTY-012")
        if sid.startswith("HL-HX8"):
            pr["duty_normal_kw"] = round(hx["duty_kw"] / 2, 3)
            note = (f"AQS-DUTY-012: rated = HX-8 duty {hx['duty_kw']:.3f} kW x {hl.A_MARGIN} (single ladder takes all). Normal {hx['duty_kw'] / 2:.3f} kW per ladder. "
                    f"Cell ohmic heat {hx['q_ohmic_kw']:.3f} kW from the per-cell partition.")
        else:
            note = f"AQS-DUTY-012: rated = single-ladder bus feed with HX-8 ({hx['duty_kw']:.3f} kW) x {hl.A_MARGIN}. Normal per the Rev N ladder run."
        e["rate"] = dict(value=ej["rated"], unit="kW", status="study", note=note)
    e = E["IA-HX8"]
    old = e["rate"]["value"]
    e["rate"] = dict(value=hx["duty_kw"], unit="kW", status="study",
                     note=f"AQS-DUTY-012: EW ohmic heat {hx['q_ohmic_kw']:.3f} kW (per-cell partition) + concentrate sensible {hx['q_feed_kw']:.3f} - wall loss {hx['q_wall_kw']:.3f} - evaporation {hx['q_evap_kw']:.3f}.")
    e["params"].update(duty_kw=hx["duty_kw"], liquor_kg_h=hx["liquor_kg_h"], doc="AQS-DUTY-012", rev_m_value=old)
    plates = math.ceil(hx["area_m2"] / 0.032)
    N["HX8"]["params"].update(plates_count_rev_n=plates, size_check_rev_n=f"{plates} plates x 0.032 m2 = {plates * 0.032:.2f} m2 in the same M3-class frame (600 mm carrying bar); envelope [600, 400, 600] unchanged")
    return hx


def gaps_update_n(g, cons, spc, elb):
    exc = sorted(set(v["node"] for v in cons.values() if v["status"].startswith("OPEN")) | {k.split("/")[0] for k, v in spc.items() if v["status"] == "OPEN"}
                 | {k.split("/")[0] for k, v in elb.items() if v["status"] == "OPEN"})
    det = ("AQS-DUTY-012 node conservation (+-1 %, daily average) and element balances (absolute tolerance): " +
           (("open at " + ", ".join(exc)) if exc else "no open node or element balances") + ". See REV_N_MODEL_CORRECTIONS_DUTY.md.")
    g["gaps"] = [x for x in g.get("gaps", []) if x["id"] not in ("REV_M_CONSERVATION", "REV_N_CONSERVATION", "REV_N_REQUIRED_STUDIES")]
    g["gaps"].append(dict(id="REV_N_CONSERVATION", severity="high" if exc else "low", detail=det))
    req = [
        "RS-EW-CE: Fe EW current efficiency in the process liquor (bench, divided cell); basis 0.415 (Liu et al. 2025 B2) is a low bound; anion-rich catholyte or pH 2-3 alternative.",
        "RS-EW-AREA: cathode area and k_m per cell (flow regime, 3-D cathodes for Au/Ag); EW_7 area at 300 A/m2 and the Au/Ag recovery at the issued envelope.",
        "RS-EW-SELECT: co-deposition and selectivity along the cascade (Cu(I) at the Au/Ag cells, Cu carry-over to EW_4..EW_9).",
        "RS-ORP-PROBE: leach ORP probe (Ag/AgCl) temperature correction and calibration at 77.5 C.",
        "RS-THERMO-PITZER: speciation of Fe(III)/Cu(I)/Au chloro-complexes at I ~ 3 mol/kg with a validated activity model (Pitzer parameters or commercial electrolyte model).",
        "RS-CRU-DECOMP: catalytic hypochlorite decomposition in the CRU for the surplus anode Cl2 (catalyst, residence time, O2 vent).",
        "RS-BMED-CE: BMED CE and V_ru at 2 M products (vendor stack data); basis 0.65 / 2.0 V.",
        "RS-CRYO-VENDOR: cold-head no-load power and part-load curve.",
        "RS-LOAD-PROFILE: hourly AC load profile (Rev N uses flat loads plus a 16 h LED photoperiod).",
        "RS-ESS-SD: ZnBr2 self-discharge and standby pump power vs SOC.",
        "RS-HL-NCG: thermosyphon leak-rate acceptance, eutectic sampling interval and low-boiler limit (vendor).",
        "RS-ELC-MAT: electrode service matrix (EW anodes/cathodes, BMED end electrodes, ZnBr2); Ni excluded as a Cl2 anode.",
        "RS-MAT-CPVC: CPVC derating at 77.5-80 C for LEACH/EW/CRU; PVDF or FRP alternative (ASME_CLASS_SHEETS Rev N design temperatures).",
        "Carried from Rev M: RS-LEACH-H2, RS-HAB-N2, RS-RESIDUE-TCLP, RS-DSP, RS-CL2-SPARGE, RS-GHEX-RECHARGE.",
    ]
    g["gaps"].append(dict(id="REV_N_REQUIRED_STUDIES", severity="medium", detail=" | ".join(req)))
    for x in g["gaps"]:
        if x["id"] == "REV_M_REQUIRED_STUDIES":
            x["detail"] = x["detail"] + " | Rev N: carried into REV_N_REQUIRED_STUDIES."
    return exc


def notes_n(S, ctx):
    D = S.decisions
    e, el, lp = D["ew"], D["elec"], D["loop"]
    es = ctx["ewm"]["summary"]
    return ("AQS-DUTY-012 Rev A model corrections on Rev M. Leach ORP {:.2f} V vs SHE (Ag/AgCl sat. KCl {:.2f} V at 25 C): Fe leaves as Fe(III), Cu as Cu(II). "
            "EW per-cell current partition (k_m {:.1e} m/s, {:.2f} m2/cell): EW DC {:.2f} kW, overall CE {:.3f}, H2 {:.3f} kg/d ({:.3f} collected), anode Cl2 {:.1f} mol/d; "
            "Fe CE {:.3f} (ELECTRICAL.md). Surplus anode Cl2 {:.1f} mol/d to ALK_SCRUBBER, hypochlorite decomposed in the CRU; O2 sparge S95 {:.2f} kg/d. "
            "BMED {:.0f} pairs/d, {:.2f} kW DC (V_ru 2.0 V, CE 0.65). Cold head {:.2f} kW (0.16 Carnot). PV design month {} mean {:.2f} kW (TMY, pvlib); "
            "ZnBr2 by hourly SOC simulation. Grid import {:.2f} kW on the design day. NCG management on the two-phase thermosyphons. "
            "loops_closed and every *_on_site flag unchanged (false).").format(
        A_RN_ORP_SHE, A_RN_ORP_SHE - A_RN_AGCL_SAT, es["km_m_s"], es["area_m2_per_cell"], e["p_ew_kw"], es["ce_ew_overall"], e["h2_total"], e["h2_caught"],
        D["electrons"]["cl2_mol"], es["ce_fe"], D["electrons"]["cl2_surplus_mol"], S.v("S95"), lp["pairs"], el["p_bmed"], el["p_cryo"], el["pv_month"], el["pv"], el["grid"])


def merge_rev_m(gn, gm):
    """Unchanged edges keep their Rev M rate and params; changed edges get the AQS-DUTY-012 note and rev_m_value."""
    Em = {e["stream_id"]: e for e in gm["edges"]}
    changed, out = [], []
    for e in gn["edges"]:
        m = Em.get(e["stream_id"])
        if m is None:
            out.append(e)
            continue
        vn, vm = (e.get("rate") or {}).get("value"), (m.get("rate") or {}).get("value")
        if vn == vm and (e.get("params") or {}).get("doc") != "AQS-DUTY-012":
            new = copy.deepcopy(m)
            pn, pm = e.get("params") or {}, m.get("params") or {}
            extra = {k: v for k, v in pn.items() if pm.get(k) != v and k in ("duty_normal_kw", "ncg_management")}
            if extra:
                new.setdefault("params", {}).update(extra)
                if "duty_normal_kw" in extra:
                    new["params"]["rev_m_duty_normal_kw"] = pm.get("duty_normal_kw")
                    new["params"]["doc_rev_n"] = "AQS-DUTY-012 ladder run"
                changed.append((e["stream_id"], "params", sorted(extra)))
            out.append(new)
            continue
        new = copy.deepcopy(m)
        note = (e.get("rate") or {}).get("note") or ""
        if note.startswith("AQS-DUTY-011: "):
            note = "AQS-DUTY-012: " + note[len("AQS-DUTY-011: "):]
        new["rate"] = dict(e["rate"], note=note[:400])
        pr = dict(m.get("params") or {})
        pr.update({k: v for k, v in (e.get("params") or {}).items() if k not in ("rev_l_value",)})
        pr["doc"] = "AQS-DUTY-012"
        pr["rev_m_value"] = vm
        new["params"] = pr
        changed.append((e["stream_id"], vm, vn))
        out.append(new)
    gn["edges"] = out
    return changed


def revm_graph(path=None):
    if path:
        return json.load(open(path))
    txt = subprocess.check_output(["git", "-C", REPO, "show", f"{REVM_REF}:flow_graph/plant_flow_graph.json"])
    return json.loads(txt)


def run_once(base, ctx_in, ce_fe=None):
    g0 = rm.base_graph(base)
    g, R, X, _ = er.build(g0)
    ewm = ew_model(X, ctx_in["q_ew"], ctx_in["raff"], ctx_in["bleed"], ctx_in["entr"], ctx_in["na_cru"], ce_fe=ce_fe, cl_M=ctx_in["cl_M"], au_M=ctx_in["au_M"])
    orig = getattr(hl.hx8, "orig", hl.hx8)
    hl.hx8 = orig
    hl.hx8 = hx8_patch(ewm)
    er.hl_offgraph(R)
    retired = rm.topology(g)
    ctx = dict(ewm=ewm)
    S, c = rate_n(g, R, X, ctx)
    S = rate_n2(S, c, ctx)
    lp, el = S.decisions["loop"], S.decisions["electrons"]
    nxt = dict(q_ew=S.v("IA-EW-04"), raff=lp["raff"], bleed=lp["bleed"], entr=S.decisions["ew"]["entrained"], na_cru=el["na_cru"],
               cl_M=ewm["summary"]["cl_feed_M"], au_M=ewm["summary"]["au_feed_M"])
    return g, R, X, S, c, ctx, retired, nxt


def main(base=None, write=None, revm=None, ce_fe=None):
    ctx_in = dict(q_ew=4284.0, raff=3925.0, bleed=782.0, entr=4.0, na_cru=140.0, cl_M=1.85, au_M=1.1e-5)
    hist = []
    for it in range(60):
        g, R, X, S, c, ctx, retired, nxt = run_once(base, ctx_in, ce_fe)
        d = max(abs(nxt[k] - ctx_in[k]) for k in nxt)
        hist.append(dict(it=it, bleed=round(nxt["bleed"], 4), na_cru=round(nxt["na_cru"], 3), delta=d))
        ctx_in = nxt
        if d < 1e-6:
            break
    rm.apply(g, S)
    base_hl = hl.main()
    _, _, q1_src, q2_src = hl.sources()
    losses = {t: base_hl["stores"][t]["loss_kw"] for t in hl.STORES}
    h = S.decisions["heat"]
    order_n = [("HX-4", hl.draws()[0]["duty_kw"]), ("HX-6", h["q6_norm"]), ("HX-5", max(h["q5_norm"], 0.0))]
    run_n = hl.ladder_j(q1_src, q2_src, losses, (0.5, 0.5), hl.hx8()["duty_kw"], order_n)
    rm.ladder_terms(S, run_n)
    hx8_update(g)
    cons = rm.conserve(g, R)
    spc = species_n(g, S, ctx)
    elb, comp = element_balances(g, S, ctx)
    N = {n["unit_id"]: n for n in g["nodes"]}
    for n in g["nodes"]:
        (n.get("params") or {}).pop("balance_rev_l", None)
        (n.get("params") or {}).pop("balance_rev_m", None)
    for u, terms in R.off.items():
        if u in N:
            p = N[u].get("params") or {}
            p["balance_rev_n"] = dict(doc="AQS-DUTY-012", basis="daily-average design day; off-graph terms", terms=terms)
            N[u]["params"] = p
    node_updates_n(g, S, ctx)
    rm.gaps_update(g, cons, spc)
    exc = gaps_update_n(g, cons, spc, elb)
    byd_edges = sorted(sid for sid, rr in S.rates.items() if rr["params"].get("rate_kind") == "by_difference")
    unrated = [e["stream_id"] for e in g["edges"] if e["presence"] == "present" and (e.get("rate") or {}).get("value") is None]
    opened = {k: v for k, v in cons.items() if v["status"].startswith("OPEN")}
    rep = dict(counts=dict(nodes=len(g["nodes"]), edges=len(g["edges"]), present=sum(e["presence"] == "present" for e in g["edges"]), unrated_present=unrated),
               conservation=dict(checked=len(cons), closed=sum(v["status"] == "closed" for v in cons.values()),
                                 closed_by_difference_unverified=sum(v["status"].startswith("closed (") for v in cons.values()), open=sorted(opened),
                                 species_open=sorted(k for k, v in spc.items() if v["status"] == "OPEN"),
                                 elements_checked=len(elb), elements_closed=sum(v["status"] == "closed" for v in elb.values()),
                                 elements_open=sorted(k for k, v in elb.items() if v["status"] == "OPEN"), by_difference_edges=byd_edges, open_nodes=exc),
               nodes=cons, species=spc, elements=elb, compositions=comp, decisions=S.decisions, log=S.log, fixed_point=hist,
               ew_cells=ctx["ewm"]["cells"], ew_summary=ctx["ewm"]["summary"], hx8=hl.hx8(),
               rates={k: dict(value=v["value"], unit=v["unit"], basis=v["note"]) for k, v in S.rates.items()})
    if write:
        gm = revm_graph(revm)
        changed = merge_rev_m(g, gm)
        rep["changed_vs_rev_m"] = changed
        Nm = {n["unit_id"]: n for n in gm["nodes"]}
        for k in ("loops_closed",):
            if k in gm:
                g[k] = gm[k]
        for k in list(gm.keys()):
            if k.startswith("notes_rev_") or k in ("notes", "date"):
                g[k] = gm[k]
        g["revision"] = "N"
        g["date"] = "2026-10-08"
        g["notes_rev_n"] = notes_n(S, ctx)
        flips = [n["unit_id"] for n in g["nodes"] for k, v in n.items() if k.endswith("_on_site") and Nm.get(n["unit_id"], {}).get(k) != v]
        rep["on_site_flips"] = flips
        open(write, "w").write(json.dumps(g, indent=2))
    return rep, g


if __name__ == "__main__":
    b = sys.argv[sys.argv.index("--base") + 1] if "--base" in sys.argv else None
    wr = sys.argv[sys.argv.index("--write") + 1] if "--write" in sys.argv else None
    rv = sys.argv[sys.argv.index("--revm") + 1] if "--revm" in sys.argv else None
    ce = float(sys.argv[sys.argv.index("--ce-fe") + 1]) if "--ce-fe" in sys.argv else None
    if ce is not None and wr:
        sys.exit("--ce-fe is a sensitivity run; do not combine with --write")
    rep, g = main(b, wr, rv, ce)
    if "--json" in sys.argv:
        json.dump(rep, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1, default=float)
    print(json.dumps(dict(counts=rep["counts"], conservation=rep["conservation"]), indent=1, default=float))

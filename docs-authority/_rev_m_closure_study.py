"""AQS-DUTY-011 Rev A. Rev M closure study (graph Rev L -> Rev M).

Starts from the Rev L graph (commit c4e1818, or --base FILE), reproduces the AQS-DUTY-010 rating pass, then applies
the Rev M changes: Faraday H2 basis, alias retirements, CRYO_H2 dispatch, grey/nutrient routing, the BMED / CRU /
chloride loop, leach and digest heater ratings, Q4 surplus sinks, electrical bus closure and the S87/S88 outcome.
Daily-average design day as AQS-DUTY-010. A_RM_* are Rev M study decisions, each stated in REV_M_CLOSURE_DUTY.md.
Run: python3 _rev_m_closure_study.py [--base revL.json] [--json report.json] [--write out.json]
Never edits plant.FCStd. Keeps loops_closed and every *_on_site flag as found.
"""
import copy
import json
import math
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _edge_rating_study as er  # noqa: E402
import _hl_edges_study as hl  # noqa: E402
import _co2_header_study as co2  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, ".."))
BASE_REF = "c4e1818"          # Rev L commit on main
M = er.M
N_E = er.N_E
EW_METALS = er.EW_METALS
TOL = er.TOL
F = 96485.0
M_AL = 26.98

# ---- Rev M study decisions (A_RM_*); each is stated in REV_M_CLOSURE_DUTY.md
A_RM_CE = dict(Au=0.90, Ag=0.90, Cu=0.85, Pb=0.85, Sn=0.85, Ni=0.80, Fe=0.80, Cd=0.85, Zn=0.80)   # ELECTRICAL CE table
A_RM_V_CELL = dict(Au=2.2, Ag=2.2, Cu=2.2, Pb=3.4, Sn=3.4, Ni=3.4, Fe=3.1, Cd=3.4, Zn=3.4)       # ELECTRICAL V_cell (blend at Zn)
A_RM_H2_CATCH = {"EW_7": "IA-HDR-H2-01", "EW_3": "IA-HDR-H2-03", "EW_9": "IA-HDR-H2-04"}         # Fe, Cu, Zn cells
A_RM_ENTRAIN = 0.10           # kg electrolyte per kg harvested deposit, drained
A_RM_RINSE_VOL = 2.0          # displacement rinse volumes on the harvest
A_RM_CL2_SPARGE = 0.95        # anode Cl2 absorbed in the LEACH_CSTR_1 sparge
A_RM_O2_UTIL = 0.90           # O2 sparge utilization
A_RM_RAFF_H_M = 0.10          # free HCl in raffinate and bleed, mol/L (chloride EW pH ~1)
A_RM_T_RAFF = hl.A_J_T_EW - 5.0
A_RM_T_HCL = 35.0             # BMED acid product (stack <= 40 C)
A_RM_T_CRU = 40.0             # CRU liquor
A_RM_T_FLOAT = 60.0           # float/sink liquor return
A_RM_T_S28 = 40.0
A_RM_T_PRE = 55.0             # HX-9 / HX-10 Q4 preheat outlet (Q4 supply 60 C, 5 K approach)
A_RM_HEATER_STEP = 0.5        # kW rating step
A_RM_CAKE_SOLIDS = 0.50       # filter cake, wt solids
A_RM_PV_YIELD = 1550.0        # kWh/kWp.yr, fixed tilt, SITE_LAT 33 design sandbox
A_RM_RECT_ETA = 0.95
A_RM_INV_LOSS = 0.03          # Sol-Ark conversion loss on AC delivered
A_RM_HYDRO_PUMP_ETA = 0.75
A_RM_FC_ETA = 0.52            # PEM system LHV efficiency at rated 4.0 kW
A_RM_STANDBY_H = 8.0          # FC standby inventory, hours at rated
A_RM_ZNBR2_AW = 0.78          # ZnBr2 electrolyte water activity
A_RM_ZNBR2_APPROACH = 0.5     # purge outlet approach to electrolyte equilibrium humidity
A_RM_GREY_SLUDGE = 0.05
A_RM_DOSE_KG_D = 0.02         # micronutrient salts at NUTRIENT_DOSE
A_RM_VCD_KWH_M3 = 17.0        # VCD SEC mid of 14-20
A_RM_PK_KW = 0.5              # RECT-PK
A_RM_GLASS_INSOL = 1.0 - hl.GLASS_FRAC[0] - hl.GLASS_FRAC[1]   # CaO/MgO/Al2O3 share of soda-lime cullet
A_RM_S11_LHV = 17.5           # MJ/kg dry biomass
A_RM_RECYCLE_DN = 15

CP_L = hl.CP_LIQ
DHE = dict(Cl2=167.2, ClO3=153.43, O2=142.9)   # kJ per mol e-, reduction enthalpy released (aq, 25 C)

NEW_EDGES = [
    # sid, from, to, phase, layers, carries, header, forbidden, notes
    ("IA-BMED-05", "POLISH_BANK", "SALT_FEED", "L", ["mass"], "raffinate brine bleed (loop level control)", "process",
     "HDR_UPW, UPW polish", "Rev M. Bleed to the AEM bank / salt loop (notes/aem_bank.md). Replaces the Rev L off-graph bleed."),
    ("IA-BMED-06", "BMED_ACID", "CONTINUOUS_RECYCLE", "L", ["mass"], "BMED HCl 2 M (REGEN LEACH acid make-up)", "process",
     "UPW polish, HDR_UPW", "Rev M. Acid make-up joins the raffinate in CONTINUOUS_RECYCLE (to LEACH_CSTR_1 only)."),
    ("IA-BMED-07", "BMED_BASE", "ALK_SCRUBBER", "L", ["mass"], "BMED NaOH 2 M to the alkaline Cl2 scrubber", "process",
     "UPW polish, HDR_UPW", "Rev M. Stoichiometric NaOH for the unabsorbed anode Cl2 (Cl2 + 2 NaOH)."),
    ("IA-BMED-08", "ALK_SCRUBBER", "CRU", "L", ["mass"], "hypochlorite / chloride scrub liquor", "process",
     "HDR_UPW, hab", "Rev M. Pregnant scrub liquor to the chlorate unit."),
    ("IA-BMED-09", "CRU", "CONTINUOUS_RECYCLE", "L", ["mass"], "chlorate / chloride liquor (REGEN LEACH oxidant)", "process",
     "UPW polish, HDR_UPW", "Rev M. NaClO3 + NaCl returned with the BMED HCl (GLOSSARY REGEN LEACH)."),
    ("IA-BMED-10", "BMED_BASE", "SALT_FEED", "L", ["mass"], "BMED NaOH 2 M for the pH-shift (metal hydroxide / silica drop)", "process",
     "UPW polish, HDR_UPW", "Rev M. Alkalinity make-up for the bleed neutralization to pH 9 (aem_bank.md)."),
    ("S91", "BMED_BASE", "GLASS_DIGEST", "L", ["mass"], "BMED NaOH 2 M digest caustic", "HDR_CAUSTIC",
     "UPW polish, leach", "Rev M. Was off-graph in Rev L (DUTY-008 593 mol/d)."),
    ("S92", "GLASS_DIGEST", "SALT_FEED", "L", ["mass"], "spent digest liquor (sodium silicate)", "process",
     "HDR_UPW, farm", "Rev M. Joins the bleed before the silica drop (aem_bank.md)."),
    ("S93", "PV_ARRAY", "SOL_ARK_60K", "E", ["elec"], "PV DC (daily average)", "tray", "none",
     "Rev M. 70 kWp array to the Sol-Ark PV input; daily-average yield."),
    ("S94", "SOL_ARK_60K", "LOAD_AGG", "E", ["elec"], "AC loads aggregate (daily average)", "tray", "none",
     "Rev M. LOAD_AGG is an accounting boundary: itemized loads in its balance terms."),
    ("S95", "HDR_O2", "LEACH_CSTR_1", "G", ["mass"], "O2 sparge (leach oxidant make-up)", "HDR_O2",
     "hab air, BOUNDARY_EXPORT", "Rev M. Process O2 from HDR_O2 only; no tee to hab air. Supplies the oxidant the anode Cl2 and chlorate do not."),
    ("S96", "GLASS_RINSE", "BOUNDARY_EXPORT", "S", ["mass"], "sink residue reject (inert, unleached metal and fillers)", "dock",
     "farm, leach", "Rev M. TCLP / leachate characterization required before disposal or sale (REV_M_CLOSURE_DUTY.md)."),
    ("S97", "SALT_FEED", "BOUNDARY_EXPORT", "S", ["mass"], "pH-shift cake: precipitated silica, Al(OH)3, sodium aluminosilicate, metal hydroxides", "dock",
     "farm, leach", "Rev M. Filter cake from the silica / hydroxide drop at pH 9."),
    ("S98", "SALT_FEED", "VCD_TRAIN", "L", ["mass"], "BMED salt-loop diluate bleed", "process",
     "HDR_UPW direct, farm", "Rev M. Water exit of the chloride loop; VCD distils it, brine returns on S28."),
    ("S99", "VCD_TRAIN", "BOUNDARY_EXPORT", "L", ["mass"], "distillate surplus (clean water export)", "dock",
     "process headers", "Rev M. Distillate above the UPW polish demand (AQS-SUR-001 clean water)."),
    ("S100", "Q4_BUS", "LEACH_CSTR_1", "E", ["thermal"], "Q4 water to HX-9 leach make-up preheater", "Q4",
     "HL-* ladder, CONTINUOUS_RECYCLE", "Rev M. HX-9 heats the cold make-up streams (S68, S10, S16, S39, S72, S28) to 55 C. Not on CONTINUOUS_RECYCLE."),
    ("S101", "Q4_BUS", "GLASS_DIGEST", "E", ["thermal"], "Q4 water to HX-10 digest caustic preheater", "Q4",
     "HL-* ladder", "Rev M. HX-10 heats S91 caustic 35 -> 55 C ahead of the HX-6 jacket."),
    ("S102", "Q4_BUS", "GEO_GHEX", "E", ["thermal"], "Q4 surplus to borefield recharge", "Q4",
     "GEO_ORC (reserved, 0 kW)", "Rev M. Remaining Q4 surplus to the GHEX loop (seasonal ground store). ORC pad stays empty."),
]

RETIRE_M = {
    "S05": "alias of S64 (both H2_DRYER -> CRYO_H2 carrying the same H2 pool). S64 kept.",
    "S86": "alias of S56 (both CRYO_AHU -> RELIEF_CRYO contingency relief, 0 on the design day). S56 kept as the relief path.",
    "S87": "flow does not exist: photosynthetic O2 (0.806 kg/d) is a 0.003 % enrichment of the farm exhaust air; recovering it is air separation, which the cold box already does on intake air. Any endpoint sends farm air into a process header.",
    "S88": "flow does not exist: GROW_BED has no N2 demand (outdoor-air ventilated at the DUTY-009 OA rate). The only candidate N2 consumer is HAB cabin leakage make-up via HDR_N2, which needs the hab envelope leak rate (required study RS-HAB-N2).",
}

RETARGET = {
    "S12": dict(to_unit_id="GREY_TREAT", carries="grey water + hab AHU condensate", header="HDR_GREY",
                notes="Rev M: retargeted from NUTRIENT_DOSE. Grey and AHU condensate go to grey treat -> VCD (S29); solids and nutrients reach the farm via BLACK_DIGEST (S30)."),
    "S20": dict(from_unit_id="SOL_ARK_60K", to_unit_id="GROW_BED", carries="LED canopy load", forbidden="none",
                notes="Rev M: direction corrected; GROW_BED is a load (LED canopy), not a source."),
    "IA-BMED-03": dict(from_unit_id="SALT_FEED", carries="salt-loop transfer to the BMED acid compartment (Cl- + product water)",
                       notes="Rev M: source corrected from CRU (CRU makes chlorate, not acid or base). Salt feed -> BMED acid side."),
    "IA-BMED-04": dict(from_unit_id="SALT_FEED", carries="salt-loop transfer to the BMED base compartment (Na+ + product water)",
                       notes="Rev M: source corrected from CRU. Salt feed -> BMED base side."),
    "IA-HDR-H2-01": dict(from_unit_id="EW_7", carries="cathode-hood H2, water-saturated (Fe cell)",
                         notes="Rev M: moved from EW_1 (Au, negligible H2) to EW_7 (Fe), the largest H2 source at CE 0.80."),
    "IA-HDR-H2-03": dict(from_unit_id="EW_3", carries="cathode-hood H2, water-saturated (Cu cell)",
                         notes="Rev M: moved from EW_2 (Ag) to EW_3 (Cu)."),
    "IA-HDR-H2-04": dict(carries="cathode-hood H2, water-saturated (Zn cell)", notes="Rev M: kept on EW_9 (Zn)."),
    "S68": dict(carries="CRYO AHU coil condensate (acid trace, flue-cap zone)",
                notes="Rev M: text corrected. Coil condensate from the cryo room AHU; may carry acid trace from the flue-cap zone, so it stays process (to leach). Not flue condensate (flue condensate is the FLUE_KO knockout)."),
}


def psat_kpa(t):
    return er.psat_kpa(t)


def ceil_step(x, step=A_RM_HEATER_STEP):
    return math.ceil(x / step - 1e-9) * step


def base_graph(path=None):
    if path:
        return json.load(open(path))
    txt = subprocess.check_output(["git", "-C", REPO, "show", f"{BASE_REF}:flow_graph/plant_flow_graph.json"])
    return json.loads(txt)


class RevM:
    def __init__(self, g, R, X):
        self.g, self.R, self.X = g, R, X
        self.E = {e["stream_id"]: e for e in g["edges"]}
        self.N = {n["unit_id"]: n for n in g["nodes"]}
        self.rates = {}
        self.log = []
        self.decisions = {}

    def v(self, sid):
        if sid in self.rates:
            return self.rates[sid]["value"]
        return (self.E[sid].get("rate") or {}).get("value")

    def set(self, sid, value, unit, basis, source, medium, cond, kind="derived", **params):
        val = round(value, 4) if abs(value) < 100 else round(value, 2)
        self.rates[sid] = dict(value=val, unit=unit, note=basis,
                               params=dict(rate_basis=basis, rate_source=source, medium=medium, conditions=cond, rate_kind=kind, **params))

    def drop(self, node, layer=None):
        self.R.off[node] = [t for t in self.R.off.get(node, []) if layer is not None and t["layer"] != layer]
        if not self.R.off[node]:
            self.R.off.pop(node)

    def off(self, node, layer, direction, label, value, basis, kind="derived"):
        self.R.offg(node, layer, direction, label, value, basis, kind)


def topology(g):
    E = {e["stream_id"]: e for e in g["edges"]}
    N = {n["unit_id"]: n for n in g["nodes"]}
    retired = []
    for sid, why in RETIRE_M.items():
        if sid in E:
            retired.append(dict(reason=why, edge=E[sid]))
    g["edges"] = [e for e in g["edges"] if e["stream_id"] not in RETIRE_M]
    E = {e["stream_id"]: e for e in g["edges"]}
    for sid, ch in RETARGET.items():
        e = E[sid]
        e["params"] = dict(e.get("params") or {})
        if "from_unit_id" in ch and ch["from_unit_id"] != e["from_unit_id"]:
            e["params"]["rev_l_from"] = e["from_unit_id"]
        if "to_unit_id" in ch and ch["to_unit_id"] != e["to_unit_id"]:
            e["params"]["rev_l_to"] = e["to_unit_id"]
        for k, val in ch.items():
            e[k] = val
        e["from_sector_id"] = N[e["from_unit_id"]].get("sector_id")
        e["to_sector_id"] = N[e["to_unit_id"]].get("sector_id")
    for sid, frm, to, phase, layers, carries, header, forbidden, notes in NEW_EDGES:
        if sid in E:
            continue
        e = dict(stream_id=sid, from_unit_id=frm, to_unit_id=to, phase=phase, layers=layers, presence="present",
                 carries=carries, header=header, forbidden=forbidden, claim_status="Closed",
                 rate=dict(value=None, unit=None, status="study", note=None),
                 from_sector_id=N[frm].get("sector_id"), to_sector_id=N[to].get("sector_id"), open_boundary=False,
                 namespace="IA" if sid.startswith("IA-") else "S", gap_flags=[], notes=notes,
                 params=dict(doc="AQS-DUTY-011", rev_m_new=True))
        g["edges"].append(e)
    return retired


def h2o_sat_per_kg_gas(t_c, m_gas):
    ps = psat_kpa(t_c)
    return ps / (101.325 - ps) * M["H2O"] / m_gas


def rate_m(g, R, X):
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
    tot = dict(dep=0.0, ne_dep=0.0, ne_side=0.0, cl2=0.0, h2=0.0, h2_caught=0.0, vap=0.0, entr=0.0, p_kw=0.0, h2_hood=0.0)
    for i, m in enumerate(EW_METALS):
        cell = f"EW_{i + 1}"
        S.drop(cell, "mass")
        dep = diss[m] * f_plate
        ne = dep * 1000 / M[m] * N_E[m]
        ns = ne * (1 - A_RM_CE[m]) / A_RM_CE[m]
        h2 = ns / 2 * M["H2"] / 1000
        cl2 = (ne + ns) / 2 * M["Cl2"] / 1000
        entr = dep * A_RM_ENTRAIN
        caught = cell in A_RM_H2_CATCH
        vap = h2 * w_h2 if caught else 0.0
        out = flow - dep - cl2 - h2 - entr - evap_cell - vap
        p_kw = (ne + ns) * F * A_RM_V_CELL[m] / 86.4e6
        S.set(chain[i], out, "kg/d",
              f"{cell} in {flow:.1f} - {m} deposit {dep:.3f} - anode Cl2 {cl2:.3f} - H2 {h2:.4f} - harvest entrainment {entr:.3f} - evaporation {evap_cell:.2f}"
              + (f" - H2 saturation water {vap:.3f}" if caught else ""),
              "AQS-DUTY-011 EW step; CE per ELECTRICAL table (all inefficiency booked as cathode H2, upper bound)", "chloride electrolyte overflow",
              f"{hl.A_J_T_EW} C, atm", deposit_kg_d=round(dep, 4), anode_cl2_kg_d=round(cl2, 4), h2_kg_d=round(h2, 5), ce=A_RM_CE[m])
        S.off(cell, "mass", "out", f"{m} cathode harvest (reported on S08)", dep, "S08 split by leach build-up")
        S.off(cell, "mass", "out", "anode Cl2 to the leach sparge header", cl2, "Faraday: (n_dep + n_side)/2 Cl2")
        S.off(cell, "mass", "out", "evaporation to EW hood (ball blanket)", evap_cell, "DUTY-008 HX-8")
        S.off(cell, "mass", "out", "electrolyte entrained on harvest (to MFG rinse, returns on S16)", entr, f"{A_RM_ENTRAIN} kg/kg deposit")
        if caught:
            sid = A_RM_H2_CATCH[cell]
            S.set(sid, h2 + vap, "kg/d", f"{cell} {m}: n_side = n_dep x (1 - CE)/CE, CE {A_RM_CE[m]}; H2 {h2:.4f} kg/d + saturation water {vap:.4f} at {hl.A_J_T_EW} C",
                  "AQS-DUTY-011 Faraday; ELECTRICAL CE table", "H2, water-saturated", f"{hl.A_J_T_EW} C, cathode hood", h2_kg_d=round(h2, 5), water_kg_d=round(vap, 5))
            tot["h2_caught"] += h2
            tot["vap"] += vap
        else:
            S.off(cell, "mass", "out", "cathode H2 to hood sweep (vented, < 1 % LFL)", h2, "minor cell; not collected")
            tot["h2_hood"] += h2
        ew.append(dict(cell=cell, metal=m, in_kg_d=round(flow, 2), deposit=round(dep, 4), n_e_dep=round(ne, 2), n_e_side=round(ns, 2),
                       cl2=round(cl2, 4), h2=round(h2, 5), caught=caught, entrained=round(entr, 3), out=round(out, 2), p_kw=round(p_kw, 3)))
        for k, val in (("dep", dep), ("ne_dep", ne), ("ne_side", ns), ("cl2", cl2), ("h2", h2), ("entr", entr), ("p_kw", p_kw)):
            tot[k] += val
        flow = out
    raff = flow
    S.off("EW_9", "mass", "in", "H2 dryer condensate return", tot["vap"], "H2_DRYER knock-out drained to the EW_9 sump")
    S.set("IA-HDR-H2-02", tot["h2_caught"] + tot["vap"], "kg/d", "sum of IA-HDR-H2-01/03/04", "AQS-DUTY-011", "H2, water-saturated", "header")
    S.set("S64", tot["h2_caught"], "kg/d", f"dried H2 = collected H2 {tot['h2_caught']:.4f} kg/d (Fe, Cu, Zn cells)", "AQS-DUTY-011 Faraday", "H2, dry", "dryer out")
    S.drop("H2_DRYER")
    S.off("H2_DRYER", "mass", "out", "knock-out condensate to EW_9 sump", tot["vap"], "saturation water at 55 C")
    S.log.append(f"Faraday H2 4.8 -> {tot['h2']:.3f} kg/d total, {tot['h2_caught']:.3f} kg/d collected")
    D["ew"] = dict(h2_total=tot["h2"], h2_caught=tot["h2_caught"], h2_hood=tot["h2_hood"], cl2_total=tot["cl2"], ne_dep=tot["ne_dep"],
                   ne_side=tot["ne_side"], p_ew_kw=tot["p_kw"], entrained=tot["entr"], dep=tot["dep"], cells=ew, raff=raff)
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


def rate_m2(S, c):
    R, X, D, g = S.R, S.X, S.decisions, S.g
    tot, raff = c["tot"], c["raff"]
    diss, f_plate = X["diss"], X["f_plate"]
    feed = hl.FEED_KG_D
    h8 = hl.hx8()
    q_ew = S.v("IA-EW-04")
    # ================================================================ 6. electrons: Cl2 sparge, chlorate, O2
    u_e = sum(diss[m] * (1 - f_plate) * 1000 / M[m] * N_E[m] for m in EW_METALS)
    al_mol = X["al"] * 1000 / M_AL
    al_e = 3 * al_mol
    dem = tot["ne_dep"] + u_e + al_e
    c_mol = tot["cl2"] * 1000 / M["Cl2"]
    a = A_RM_CL2_SPARGE
    c_a_in = (1 - a) * c_mol
    slip = er.A_RL_SLIP * c_a_in
    c_a = c_a_in - slip
    na_alk, na_pol = 2 * c_a, 2 * slip
    na_cru = na_alk + na_pol
    e_cl2, e_cru = 2 * a * c_mol, na_cru
    delta = dem - e_cl2 - e_cru
    o2_mol = delta / 4 / A_RM_O2_UTIL
    s95 = o2_mol * M["O2"] / 1000
    o2_vent = s95 * (1 - A_RM_O2_UTIL)
    S.set("S95", s95, "kg/d", f"oxidant deficit {delta:.1f} mol e-/d (demand {dem:.1f} - Cl2 sparge {e_cl2:.1f} - chlorate {e_cru:.1f}) / 4 / utilization {A_RM_O2_UTIL}",
          "AQS-DUTY-011 leach electron balance", "O2 gas (cold box product)", "~2 bar g sparge", mol_d=round(o2_mol, 1))
    S.set("S83", s95, "kg/d", "= S95 (HDR_O2 pass-through to the leach sparge)", "AQS-DUTY-011", "O2 gas", "header 3 bar g")
    S.set("S84", 0.0, "kg/d", "HDR_N2 has no consumer edge (S88 retired; RS-HAB-N2 open)", "graph topology", "N2 gas", "header pressurized, no draw")
    D["electrons"] = dict(n_e_dep=tot["ne_dep"], u_e=u_e, al_e=al_e, al_mol=al_mol, demand=dem, cl2_mol=c_mol, e_cl2=e_cl2, e_cru=e_cru, o2_e=delta,
                          o2_mol=o2_mol, na_alk=na_alk, na_pol=na_pol, na_cru=na_cru, c_a_in=c_a_in, slip_mol=slip, n_e_side=tot["ne_side"])
    naoh_alk_kg = na_alk / er.A_RL_M_REAGENT * er.A_RL_RHO_2M["NaOH"]
    S.set("IA-BMED-07", naoh_alk_kg, "kg/d", f"2 x Cl2 absorbed {c_a:.2f} mol/d = {na_alk:.1f} mol/d NaOH as 2 M", "Cl2 + 2 NaOH -> NaCl + NaOCl + H2O",
          "NaOH 2 M", "ambient", mol_d=round(na_alk, 1))
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
    cru = alk_liq + s66
    S.set("IA-BMED-09", cru, "kg/d", f"IA-BMED-08 {alk_liq:.3f} + S66 {s66:.4f}; 3 NaOCl -> NaClO3 + 2 NaCl in the CRU tank", "mass; hypochlorite disproportionation",
          "NaClO3 / NaCl liquor", f"{A_RM_T_CRU} C", na_mol_d=round(na_cru, 1), chlorate_mol_d=round(na_cru / 6, 1))
    S.drop("ALK_SCRUBBER")
    S.drop("CRU")
    S.off("ALK_SCRUBBER", "mass", "in", "acid-gas air (EW hood sweep + leach lid purge) incl. unabsorbed Cl2", S.v("S65") * 24 + cl2_abs_kg,
          "S65 basis + Cl2 absorbed (scrubber water evaporation within the S65 saturation basis)")
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
    for it in range(500):
        ins = fixed_in + s28 + feed + tot["dep"] + s95 + cl2_kg
        outs = q_ew + s08 + slurry + purge + (1 - a) * cl2_kg + o2_vent
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
    p_bmed = bmed_kg * er.A_RL_BMED_KWH_KG / 24
    D["loop"] = dict(rec=rec, pol2=pol2, bleed=bleed, f_h=f_h, cl_bleed=cl_bleed, L=L, pairs=pairs, n_top=n_top, n_top_req=n_top_req, dil=dil,
                     vcd_feed=vcd_feed, s28=s28, s99=s99, s25=s25, bmed_kg_d=bmed_kg, p_bmed_kw=p_bmed, raff=raff, iterations=it, o2_vent=o2_vent, acid=acid, cru=cru)
    for u in ("POLISH_BANK", "CONTINUOUS_RECYCLE", "SALT_FEED", "BMED_ACID", "BMED_BASE", "VCD_TRAIN"):
        S.drop(u, "mass") if u in R.off else None
    S.drop("LEACH_CSTR_1", "mass")
    S.off("LEACH_CSTR_1", "mass", "in", "fresh shredded feed", feed, "plant basis 150 kg/d wet")
    S.off("LEACH_CSTR_1", "mass", "in", "EW cathode harvest booked onto S08", tot["dep"], "= S08")
    S.off("LEACH_CSTR_1", "mass", "in", "anode Cl2 sparge (all EW cells)", cl2_kg, "AQS-DUTY-011 Faraday")
    S.off("LEACH_CSTR_1", "mass", "out", "slurry to FLOAT_SINK", slurry, "undissolved + 20 wt % liquor")
    S.off("LEACH_CSTR_1", "mass", "out", "purge vapor", purge, "DUTY-008 HX-5 purge")
    S.off("LEACH_CSTR_1", "mass", "out", "unabsorbed Cl2 to lid purge -> ALK_SCRUBBER", (1 - a) * cl2_kg, f"1 - sparge absorption {a}")
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
    q_ox_tot = (e_cl2 * DHE["Cl2"] + e_cru * DHE["ClO3"] + delta * DHE["O2"]) / 86400
    q_ox_extra = q_ox_tot - cu_e * DHE["ClO3"] / 86400
    q5_rate = q_warm + q_cold_raw + q_fix - q_rx_low
    q5_norm = q_warm + q_cold_raw - q_hx9 + q_fix - q_rx_low - q_ox_extra
    hx5_rating = ceil_step(q5_rate * hl.A_MARGIN)
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
                     warm=[(s, round(mm, 2), round(t, 1)) for s, mm, _, t in warm], rev_l_hx5=lch["duty_kw"], rev_l_hx6=dg["duty_kw"])
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
    S.set("S55", er.A_RL_STIRLING_KW + qc, "kW", f"Stirling reject = electric {er.A_RL_STIRLING_KW} + lift {qc:.4f} kW", "CRYO_COLD_BOX", "glycol 30 %", "dT 5 K")
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
          duty_normal_kw=round(q_hx9, 4), duty_rated_kw=round(q_hx9 * hl.A_MARGIN, 3))
    S.set("S101", q_hx10, "kW", f"HX-10: S91 {s91:.1f} kg/d x 3.8 x ({A_RM_T_PRE} - {hl.A_J_T_CAUSTIC}) C", "AQS-DUTY-011", "Q4 water", "60 C supply / 45 C return",
          duty_normal_kw=round(q_hx10, 4), duty_rated_kw=round(q_hx10 * hl.A_MARGIN, 3))
    S.set("S102", s102, "kW", f"Q4 bus in {q4_in:.3f} - life {life} - HX-9 {q_hx9:.3f} - HX-10 {q_hx10:.3f}", "AQS-DUTY-011 Q4 balance", "Q4 water -> GHEX glycol",
          "60 C supply", kind="by_difference", duty_normal_kw=round(s102, 4), duty_rated_kw=round(max(s102, 0) * hl.A_MARGIN, 3))
    D["q4"] = dict(bus_n=bus_n, s54=s54, s63=S.v("S63"), s80=s80, q4_in=q4_in, life=life, s100=q_hx9, s101=q_hx10, s102=s102, rev_l_surplus=3.3167)
    # ================================================================ 11. electrical
    s93 = 70.0 * A_RM_PV_YIELD / 8760.0
    S.set("S93", s93, "kW", f"70 kWp x {A_RM_PV_YIELD:.0f} kWh/kWp.yr / 8760 h", "PV yield class SITE_LAT 33 (fixed tilt)", "DC", "PV input", peak_kw=70.0)
    p_ew = tot["p_kw"]
    rect_dc = p_ew + p_bmed + A_RM_PK_KW
    s17 = rect_dc / A_RM_RECT_ETA
    bmed_rating = math.ceil(p_bmed * hl.A_MARGIN)
    S.set("S17", s17, "kW", f"(EW {p_ew:.3f} + BMED {p_bmed:.3f} + PK {A_RM_PK_KW}) / {A_RM_RECT_ETA}", "AQS-DUTY-011 Faraday + BMED pair basis", "AC to rectifiers", "480 V",
          rect_ew_kw=round(p_ew, 3), rect_bmed_kw=round(p_bmed, 3), rect_bmed_rating_kw=bmed_rating)
    S.set("S20", 5.0, "kW", "GROW_BED LED canopy share (graph continuous_kw 5.0)", "graph GROW_BED continuous_kw", "AC load", "bus")
    gb_trim = hl.sources()[1]["q_trim_electric_kw"]
    loads = [
        ("MFG_SHOP", 12.0), ("HABITATION", 3.0), ("CRYO cold head (CRYO_H2 node 4.0 kW)", er.A_RL_STIRLING_KW), ("LEACH_CSTR_1 parasitics", 2.0),
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
    S.off("RECTIFIER", "energy", "out", "RECT-EW DC to EW cells", p_ew, "Faraday x V_cell")
    S.off("RECTIFIER", "energy", "out", "RECT-BMED DC to BMED stack", p_bmed, f"{bmed_kg:.1f} kg/d pair x {er.A_RL_BMED_KWH_KG} kWh/kg")
    S.off("RECTIFIER", "energy", "out", "RECT-PK DC", A_RM_PK_KW, "ELECTRICAL < 0.5 kW")
    S.off("RECTIFIER", "energy", "out", "conversion loss", s17 - rect_dc, f"1 - {A_RM_RECT_ETA}")
    ac = s17 + s94 + 5.0
    inv = ac * A_RM_INV_LOSS
    sup = s93 + S.v("IA-ESS-ZNBR2-DIS") + S.v("IA-ESS-HYDRO-ELEC") + c["s79"]
    dem_e = ac + S.v("IA-ESS-ZNBR2-CHG") + inv
    grid = dem_e - sup
    if "SOL_ARK_60K" in R.off:
        S.drop("SOL_ARK_60K")
    S.off("SOL_ARK_60K", "energy", "out", "inverter / charger conversion loss", inv, f"{A_RM_INV_LOSS:.0%} of AC delivered")
    S.off("SOL_ARK_60K", "energy", "in", "utility import at the GRID port (ELECTRICAL AQS-ELC-001 Rev B)", grid, "bus balance", kind="by_difference")
    if "GEO_GHEX" in R.off:
        S.drop("GEO_GHEX")
    S.off("GEO_GHEX", "energy", "out", "heat to ground (borefield recharge)", s102, "S102")
    D["elec"] = dict(pv=s93, p_ew=p_ew, p_bmed=p_bmed, bmed_rating_kw=bmed_rating, s17=s17, s94=s94, loads=loads, inv=inv, grid=grid, supply=sup, demand=dem_e,
                     grid_kwh_d=grid * 24, ew_issued_kw=6.0, w_shaft=w_shaft)
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


def ladder_terms(S, run_n):
    E = S.E
    for lad in "AB":
        run = run_n[lad]
        for t in ("Q1", "Q2", "Q3", "Q4"):
            q = f"{t}_{lad}"
            S.drop(q, "energy")
            S.off(q, "energy", "out", "store standing loss", run[t]["loss"], "DUTY-008 store loss")
            if run[t].get("hp_loss"):
                S.off(q, "energy", "out", "thermosyphon line loss on arrival", run[t]["hp_loss"], "DUTY-008 A_HP_LOSS")
        for sid, val in ((f"HL-Q3-{lad}-DOWN", run["Q3"]["down"]), (f"HL-Q4-{lad}-BUS", run["Q4"]["down"]),
                         (f"HL-Q2-{lad}-DOWN", run["Q2"]["down"]), (f"HL-Q1-{lad}-DOWN", run["Q1"]["down"])):
            e = E[sid]
            old = (e.get("params") or {}).get("duty_normal_kw")
            if old is None or abs(old - round(val, 3)) > 1e-9:
                e.setdefault("params", {})["duty_normal_kw"] = round(val, 3)
                e["params"]["doc_rev_m"] = "AQS-DUTY-011 ladder run"
                if old is not None:
                    e["params"]["rev_l_duty_normal_kw"] = old


def apply(g, S):
    E = {e["stream_id"]: e for e in g["edges"]}
    for sid, rr in S.rates.items():
        if sid not in E:
            continue
        e = E[sid]
        old = (e.get("rate") or {}).get("value")
        e["rate"] = dict(value=rr["value"], unit=rr["unit"], status="study", note=("AQS-DUTY-011: " + rr["note"])[:400])
        pr = dict(e.get("params") or {})
        pr.update(rr["params"])
        pr["doc"] = "AQS-DUTY-011"
        if old is not None and abs(old - rr["value"]) > 1e-9:
            pr["rev_l_value"] = old
        e["params"] = pr
        e["presence"] = "present"


ENERGY_NODES = er.ENERGY_NODES + ["LOAD_AGG", "RECTIFIER", "GEO_GHEX"]


def conserve(g, R):
    save = er.ENERGY_NODES[:]
    er.ENERGY_NODES[:] = ENERGY_NODES
    try:
        return er.conserve(g, R)
    finally:
        er.ENERGY_NODES[:] = save


def species(g, S):
    E = {e["stream_id"]: e for e in g["edges"]}
    v = lambda s: E[s]["rate"]["value"]  # noqa: E731
    D = S.decisions
    out = {}
    a = hl.CO2_AB_KG_D + D["co2"]["s11_co2"]
    b = E["S67"]["params"]["co2_kg_d"]
    out["AFTERBURNER/CO2"] = dict(in_total=round(a, 3), out_total=b, residual=round(a - b, 4), status="closed" if abs(a - b) <= TOL * a else "OPEN",
                                  note="S11 trim carbon folded into the S67 CO2 basis (Rev M)")
    a = v("S18") + v("S67B") + v("S82")
    b = v("S04") + v("S73") + v("S85") + v("S70")
    out["CRYO_CO2/CO2"] = dict(in_total=round(a, 3), out_total=round(b, 3), residual=round(a - b, 4),
                               status="closed (one term by difference)" if abs(a - b) <= TOL * a else "OPEN")
    a, b = v("S85") + v("S90"), v("S89")
    out["HDR_CO2/CO2"] = dict(in_total=round(a, 3), out_total=b, residual=round(a - b, 4), status="closed" if abs(a - b) <= 1e-3 else "OPEN")
    a = D["ew"]["h2_caught"]
    b = v("S64") + v("S24")
    out["H2_DRYER/H2"] = dict(in_total=round(a, 4), out_total=round(b, 4), residual=round(a - b, 5), status="closed" if abs(a - b) <= 1e-3 else "OPEN")
    b = v("S74") + v("S45") + v("S49")
    out["CRYO_H2/H2"] = dict(in_total=round(v("S64"), 4), out_total=round(b, 4), residual=round(v("S64") - b, 5), status="closed" if abs(v("S64") - b) <= 1e-3 else "OPEN")
    el = D["electrons"]
    sup = el["e_cl2"] + el["e_cru"] + el["o2_e"]
    out["LEACH/electrons"] = dict(in_total=round(sup, 1), out_total=round(el["demand"], 1), residual=round(sup - el["demand"], 3), status="closed",
                                  note="oxidant e- (Cl2 sparge + chlorate + O2) = metal e- dissolved (deposited + undeposited + Al)")
    lp = D["loop"]
    cl_in = lp["L"] + el["na_cru"] + D["fab"]["h09"] + 2 * A_RM_CL2_SPARGE * el["cl2_mol"]
    cl_out = 2 * el["cl2_mol"] + lp["cl_bleed"]
    out["LEACH_LOOP/Cl"] = dict(in_total=round(cl_in, 1), out_total=round(cl_out, 1), residual=round(cl_in - cl_out, 3),
                                status="closed" if abs(cl_in - cl_out) <= TOL * cl_in else "OPEN",
                                note="Cl in: BMED HCl + CRU (NaCl + NaClO3) + fab HCl on S10 + absorbed anode Cl2; out: anode Cl2 + bleed")
    na_in = el["na_cru"] + 593.0 + D["salt"]["na_glass"] + lp["n_top"]
    na_out = lp["cl_bleed"] + D["salt"]["dsp_mol"]
    out["SALT_FEED/Na"] = dict(in_total=round(na_in, 1), out_total=round(na_out, 1), residual=round(na_in - na_out, 2),
                               status="closed" if abs(na_in - na_out) <= TOL * na_in else "OPEN",
                               note="Na in: bleed (CRU Na) + digest NaOH + glass Na + IA-BMED-10; out: NaCl to BMED (= Cl in bleed) + Na retained in the cake")
    pairs = lp["pairs"]
    naoh_use = 593.0 + el["na_alk"] + lp["n_top"] + D["fab"]["n02"]
    out["BMED/pairs"] = dict(in_total=round(pairs, 1), out_total=round(naoh_use, 1), residual=round(pairs - naoh_use, 3), status="closed",
                             note="HCl made = NaOH made; NaOH uses: S91 + IA-BMED-07 + IA-BMED-10 + IA-BMED-02")
    return out


def node_updates(g, S):
    N = {n["unit_id"]: n for n in g["nodes"]}
    D = S.decisions
    h = D["heat"]
    lp = D["loop"]
    p = N["LEACH_CSTR_1"].setdefault("params", {})
    p.update(heater_rating_kw=h["hx5_rating"],
             heater_rating_basis=f"HX-5 rating case {h['q5_rate']:.3f} kW (Q3, Q4 and Cl2 sparge unavailable; DUTY-008 lowest exotherm credit) x {hl.A_MARGIN}, rounded up to 0.5 kW",
             hx5_normal_kw=round(h["q5_norm"], 3), hx9_kw=round(h["q_hx9"], 3), doc_rev_m="AQS-DUTY-011")
    p = N["GLASS_DIGEST"].setdefault("params", {})
    p.update(heater_rating_kw=h["hx6_rating"],
             heater_rating_basis=f"HX-6 rating case {h['q6_rate']:.3f} kW (Q3 and Q4 unavailable) x {hl.A_MARGIN}, rounded up to 0.5 kW; replaces the 1.5 kW study class",
             hx6_normal_kw=round(h["q6_norm"], 3), hx10_kw=round(h["q_hx10"], 3), doc_rev_m="AQS-DUTY-011")
    ck = N["GLASS_DIGEST"].get("continuous_kw")
    if isinstance(ck, dict):
        ck["note"] = f"Rev M: heater rating {h['hx6_rating']} kW (AQS-DUTY-011); 1.5 kW study class retired"
    p = N["CONTINUOUS_RECYCLE"].setdefault("params", {})
    q = lp["rec"] / hl.RHO_LIQ / 86400
    idm = hl.PIPE_ID_MM[A_RM_RECYCLE_DN] / 1000
    vel = q / (math.pi / 4 * idm ** 2)
    D["recycle_line"] = dict(dn=A_RM_RECYCLE_DN, velocity_m_s=vel, flow_m3_d=lp["rec"] / hl.RHO_LIQ, rev_l_velocity_m_s=0.02)
    p.update(line_DN=A_RM_RECYCLE_DN, line_material="CPVC", velocity_m_s=round(vel, 3), flow_m3_d=round(lp["rec"] / hl.RHO_LIQ, 3),
             size_note="L x W x H mm, study envelope: DN15 CPVC line on clear liquor (25 um filter at the POLISH_BANK outlet) plus support allowance; Rev M (AQS-DUTY-011)",
             size_doc="MVS_EQUIPMENT Rev M")
    p = N["VCD_TRAIN"].setdefault("params", {})
    feed = lp["vcd_feed"] / 1000
    rated = math.ceil(feed * hl.A_MARGIN * 20) / 20
    D["vcd"] = dict(feed_m3_d=feed, rated_m3_d=rated, avg_kw=feed * A_RM_VCD_KWH_M3 / 24, rev_l_issued=0.11)
    p.update(feed_m3_d=round(feed, 3), feed_m3_d_rated=rated, avg_kw=round(feed * A_RM_VCD_KWH_M3 / 24, 3), duty_doc="AQS-DUTY-011 Rev M (was 0.11 m3/d issued)")
    ck = N["RECTIFIER"].get("continuous_kw")
    if isinstance(ck, dict):
        ck.update(value=round(D["elec"]["s17"], 2), note=f"Rev M: (EW {D['elec']['p_ew']:.2f} + BMED {D['elec']['p_bmed']:.2f} + PK 0.5 kW DC) / 0.95 (AQS-DUTY-011)")
    ck = N["BMED_UPW_POLISH"].get("continuous_kw")
    if isinstance(ck, dict):
        ck["note"] = f"Rev M: BMED stack is carried on RECTIFIER (RECT-BMED {D['elec']['p_bmed']:.2f} kW DC, rating {D['elec']['bmed_rating_kw']} kW); UPW polish EDI ~0.1 kW"
    gb = N["GROW_BED"]["params"]
    gb.update(co2_in_kg_d={"S04": S.v("S04"), "S89": S.v("S89")}, co2_to_exhaust_kg_d=S.v("S89"), farm_oa_m3_h=D["farm"]["oa"])
    p = N["GEO_GHEX"]["params"]
    p.update(Q_recharge_kW_th=round(D["q4"]["s102"], 3), recharge_note="Rev M: Q4 surplus to borefield (S102); ORC pad reserved, P_ORC 0")


def gaps_update(g, cons, spc):
    exc = sorted(set(v["node"] for v in cons.values() if v["status"].startswith("OPEN")) | {k.split("/")[0] for k, v in spc.items() if v["status"] == "OPEN"})
    det = ("AQS-DUTY-011 node conservation (+-1 %, daily average): " + (("open at " + ", ".join(exc)) if exc else "no open node balances") +
           ". See REV_M_CLOSURE_DUTY.md.")
    g["gaps"] = [x for x in g.get("gaps", []) if x["id"] not in ("REV_L_CONSERVATION_EXCEPTIONS", "REV_M_CONSERVATION", "REV_M_REQUIRED_STUDIES")]
    g["gaps"].append(dict(id="REV_M_CONSERVATION", severity="high" if exc else "low", detail=det))
    for x in g["gaps"]:
        if x["id"] == "WP_TRUE_CLOSURE_RESIDUALS":
            x["detail"] = "Rev M: S87 and S88 retired (no physical flow; AQS-DUTY-011). Required studies in REV_M_REQUIRED_STUDIES. loops_closed false."
    req = [
        "RS-LEACH-H2: leach lid H2 under oxidant upset (Cl2 sparge or O2 off): purge dilution to < 25 % LFL and interlock.",
        "RS-HAB-N2: hab envelope leak rate at operating pressure; sets HDR_N2 -> HABITATION make-up (the only N2 consumer candidate).",
        "RS-RESIDUE-TCLP: S96 sink residue and S97 cake leachate characterization before disposal or sale.",
        "RS-DSP: bench confirmation that glass Na leaves in the pH-9 cake as sodium aluminosilicate (Na <= Al).",
        "RS-CL2-SPARGE: anode Cl2 absorption in LEACH_CSTR_1 (0.95 basis) and the Fe3+ effect on EW CE.",
        "RS-GHEX-RECHARGE: borefield temperature drift under S102 continuous recharge (field bore data external, design_survey_locked).",
    ]
    g["gaps"].append(dict(id="REV_M_REQUIRED_STUDIES", severity="medium", detail=" | ".join(req)))
    return exc


def notes(S):
    D = S.decisions
    return ("AQS-DUTY-011 Rev A closure. Faraday H2 on the ELECTRICAL CE table ({:.3f} kg/d, {:.3f} collected at EW_7/EW_3/EW_9); S05, S86 retired as aliases; "
            "S87, S88 retired (no physical flow). CRYO_H2: all H2 to MeOH, FC and GEN on standby. S12 -> GREY_TREAT, S20 reversed, IA-BMED-03/04 from SALT_FEED. "
            "Chloride loop: anode Cl2 sparged in LEACH_CSTR_1 (0.95), remainder ALK -> CRU -> CONTINUOUS_RECYCLE; BMED HCl {:.0f} mol/d to CONTINUOUS_RECYCLE; "
            "O2 sparge S95 {:.2f} kg/d; bleed IA-BMED-05 to SALT_FEED; BMED {:.0f} pairs/d ({:.2f} kW DC). Heaters: HX-5 rating {} kW, HX-6 rating {} kW. "
            "Q4 surplus to HX-9, HX-10 and borefield (S102 {:.3f} kW). Electrical bus closed with utility import by difference. "
            "loops_closed and every *_on_site flag unchanged (false).").format(
        D["ew"]["h2_total"], D["ew"]["h2_caught"], D["loop"]["L"], S.v("S95"), D["loop"]["pairs"], D["elec"]["p_bmed"], D["heat"]["hx5_rating"],
        D["heat"]["hx6_rating"], D["q4"]["s102"])


def main(base=None, write=None):
    g0 = base_graph(base)
    g, R, X, _ = er.build(g0)
    er.hl_offgraph(R)
    retired = topology(g)
    S, c = rate_m(g, R, X)
    S = rate_m2(S, c)
    apply(g, S)
    base = hl.main()
    _, _, q1_src, q2_src = hl.sources()
    losses = {t: base["stores"][t]["loss_kw"] for t in hl.STORES}
    h = S.decisions["heat"]
    order_n = [("HX-4", hl.draws()[0]["duty_kw"]), ("HX-6", h["q6_norm"]), ("HX-5", max(h["q5_norm"], 0.0))]
    run_n = hl.ladder_j(q1_src, q2_src, losses, (0.5, 0.5), hl.hx8()["duty_kw"], order_n)
    ladder_terms(S, run_n)
    cons = conserve(g, R)
    spc = species(g, S)
    N = {n["unit_id"]: n for n in g["nodes"]}
    for n in g["nodes"]:
        (n.get("params") or {}).pop("balance_rev_l", None)
    for u, terms in R.off.items():
        if u in N:
            p = N[u].get("params") or {}
            p["balance_rev_m"] = dict(doc="AQS-DUTY-011", basis="daily-average design day; off-graph terms", terms=terms)
            N[u]["params"] = p
    node_updates(g, S)
    unrated = [e["stream_id"] for e in g["edges"] if e["presence"] == "present" and (e.get("rate") or {}).get("value") is None]
    ph = [e["stream_id"] for e in g["edges"] if e["presence"] == "placeholder"]
    opened = {k: v for k, v in cons.items() if v["status"].startswith("OPEN")}
    exc = gaps_update(g, cons, spc)
    rep = dict(counts=dict(nodes=len(g["nodes"]), edges=len(g["edges"]), present=sum(e["presence"] == "present" for e in g["edges"]), unrated_present=unrated,
                           placeholders=ph, retired=[r["edge"]["stream_id"] for r in retired], new=[x[0] for x in NEW_EDGES], retargeted=sorted(RETARGET)),
               conservation=dict(checked=len(cons), closed=sum(v["status"] == "closed" for v in cons.values()),
                                 closed_by_difference=sum(v["status"].startswith("closed (") for v in cons.values()), open=sorted(opened),
                                 species_open=sorted(k for k, v in spc.items() if v["status"] == "OPEN")),
               nodes=cons, species=spc, decisions=S.decisions, log=S.log,
               rates={k: dict(value=v["value"], unit=v["unit"], basis=v["note"]) for k, v in S.rates.items()})
    if write:
        g["revision"] = "M"
        g["date"] = "2026-10-08"
        g["notes_rev_m"] = notes(S)
        g["notes_rev_m_retired"] = json.dumps([dict(reason=r["reason"], edge=r["edge"]) for r in retired], ensure_ascii=True)
        open(write, "w").write(json.dumps(g, indent=2))
    return rep, g


if __name__ == "__main__":
    b = sys.argv[sys.argv.index("--base") + 1] if "--base" in sys.argv else None
    wr = sys.argv[sys.argv.index("--write") + 1] if "--write" in sys.argv else None
    rep, g = main(b, wr)
    if "--json" in sys.argv:
        json.dump(rep, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1, default=float)
    print(json.dumps(dict(counts=rep["counts"], conservation=rep["conservation"]), indent=1))

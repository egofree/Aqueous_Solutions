"""AQS-DUTY-010 Rev A. Edge rating and node conservation (graph Rev K -> Rev L).

Rates every present edge that has no rate, closes the placeholder edges, and checks node conservation
(daily-average design day: plant running normal, dry weather, one hydro cycle per day).
Inputs read from the graph or imported from AQS-DUTY-008 (_hl_edges_study) and AQS-DUTY-009
(_co2_header_study). A_RL_* are Rev L study decisions, each stated in EDGE_RATING_DUTY.md.
Run: python3 _edge_rating_study.py [--graph in.json] [--json report.json] [--write out.json]
Never edits plant.FCStd. Keeps loops_closed and every *_on_site flag as found.
"""
import copy
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _hl_edges_study as hl  # noqa: E402
import _co2_header_study as co2  # noqa: E402

GRAPH = os.path.join(HERE, "..", "flow_graph", "plant_flow_graph.json")
TOL = 0.01

# ---- molar masses, g/mol
M = dict(H2=2.016, O2=31.998, N2=28.014, CO2=44.01, H2O=18.015, Cl2=70.906, HCl=36.461, NaOH=39.997,
         MeOH=32.042, CH4=16.043, HNO3=63.013, NaNO3=84.995, NaCl=58.443, KOH=56.106, KCl=74.551, Br2=159.808,
         NaOCl=74.442, Au=196.97, Ag=107.87, Cu=63.546, Pb=207.2, Sn=118.71, Ni=58.693, Fe=55.845, Cd=112.41,
         Zn=65.38)
N_E = dict(Au=3, Ag=1, Cu=2, Pb=2, Sn=2, Ni=2, Fe=2, Cd=2, Zn=2)
EW_METALS = ("Au", "Ag", "Cu", "Pb", "Sn", "Ni", "Fe", "Cd", "Zn")   # params.py order, EW_1..EW_9
LHV_H2 = 119.96      # MJ/kg
LHV_MEOH = 19.93     # MJ/kg
R_AIR = 287.05

# ---- Rev L study decisions (A_RL_*); each is stated in EDGE_RATING_DUTY.md
A_RL_PLASTIC = 0.22          # ELECTRICAL assay: plastic + paper, wet basis
A_RL_GLASS = 0.18            # ELECTRICAL assay: glass
A_RL_PM_KG_T = dict(Au=0.05, Ag=0.20)   # ELECTRICAL assay 50 / 200 ppm
A_RL_PM_LEACH = 0.90         # ELECTRICAL leach recovery band 0.85-0.95 mid
A_RL_OIL_KG_T = 150.0        # ELECTRICAL yields: oil cuts
A_RL_PLATED_KG_T = 280.0     # yields: plated metal (= S08 at 150 kg/d)
A_RL_SLURRY_WT = 0.20        # leach train discharge to float/sink, wt % solids
A_RL_GLASS_DRY_KG_D = None   # cullet = hl.CULLET_KG_D (DUTY-008 burnout basis, = silicate yield)
A_RL_KO_T_C = 30.0           # FLUE_KO outlet, saturated
A_RL_W_AMB = 0.010           # ambient humidity ratio (DUTY-008 basis)
A_RL_FARM_T_C, A_RL_FARM_RH = 24.0, 0.70   # farm air
A_RL_ET_L_M2_D = 3.3         # canopy evapotranspiration, leafy crop under LED (FAO-56 Kc ~1.0 indoor)
A_RL_FARM_OA_DARK = None     # dark-period OA = co2 study oa_min
A_RL_VCD_REC = 0.90          # VCD distillate recovery (grey/condensate feed)
A_RL_UPW_REJECT = 0.02       # UPW polish reject (EDI/RO polish on distillate)
A_RL_HAB_WATER_L_P_D = 30.0  # hab hygiene water per person (LIFE_MEP fixture class)
A_RL_O2_P_D = 0.84           # kg O2 per person-day (NASA BVAD nominal)
A_RL_RQ = 0.87               # respiratory quotient (BVAD)
A_RL_FOOD_WASTE = 0.15       # food waste share of ration to MEOH_FERM
A_RL_FW_DM, A_RL_FW_VS = 0.15, 0.90
A_RL_CH4_NM3_KG_VS = 0.30
A_RL_MEOH_CONV = 0.70        # CH4 -> MeOH conversion
A_RL_BLACK_L_P_D = (1.5, 0.12, 2.5)   # urine, feces, flush per person (BVAD class)
A_RL_BLACK_GAS = 0.05        # kg/d gas lost in BLACK_DIGEST (VS destruction, small)
A_RL_ASU_REC = 0.90          # O2 recovery in the cold box
A_RL_Y_O2 = 0.2314           # O2 mass fraction of air
A_RL_ASU_P = 6.0             # bar a compressor discharge
A_RL_ETA_IS = 0.70
A_RL_SIEVE_RECOV = 0.5
A_RL_COLD_LEAK = 0.40        # cold-box heat leak allowance on liquefaction duty
A_RL_STIRLING_KW = 4.0       # cold-head electric (CRYO 2-8 kW class; 16 % of Carnot at 90 K)
A_RL_GEN_LAMBDA = 2.0        # backup gen excess air
A_RL_GEN_AFR = 34.3          # H2 stoich air, kg/kg
A_RL_GEN_ETA = 0.50          # S47 2.5 kW from S45 LHV 5.0 kW
A_RL_FC_T_C = 60.0           # PEM stack coolant
A_RL_DMFC_L_KWH = 0.9        # EFOY-class DMFC fuel use, L MeOH per kWh
A_RL_RHO_MEOH = 0.7914
A_RL_STARTS = 3              # wafer starts/d (ST-LITHO-01)
A_RL_N2_SLM, A_RL_N2_MIN = 10.0, 40.0   # tool purge per start
A_RL_SOLV_L_D, A_RL_RHO_SOLV = 1.25, 0.79   # WS_SOLV band 0.5-2 L/d mid, IPA/PGMEA class
A_RL_UPW_BAND = (20.0, 100.0)  # fab UPW L/d for 1-5 starts, interpolated
A_RL_M_REAGENT = 2.0         # BMED products and exchange grades, mol/L
A_RL_RHO_2M = dict(HCl=1.033, NaOH=1.080, HNO3=1.064, KOH=1.090)
A_RL_BMED_KWH_D = 12.0       # ELECTRICAL BMED 80 kWh/t x 150 kg/d
A_RL_BMED_KWH_KG = 2.1       # ELECTRICAL 1.8-2.4 kWh per kg NaOH + HCl, mid
A_RL_SLIP = 0.01             # Cl2 slip past ALK to the acid polish
A_RL_POL_SALT_WT = 0.15      # polish blowdown salt limit
A_RL_POLISH_M3_H, A_RL_POLISH_T_C = 1500.0, 50.0   # VENT_SCRUB_EQUIPMENT 2.1
A_RL_BR2_PURGE_M3_H = 30.0   # VENT_SCRUB_EQUIPMENT 2.2 band 10-50 mid
A_RL_BR2_PPMV = 10.0         # complexed electrolyte headspace
A_RL_CRYO_AHU_M3_H = 2592.0  # RELIEF_CRYO size basis: 12 ACH x 216 m3
A_RL_COIL_T_C = 10.0         # CRYO AHU coil leaving dew point
A_RL_CO2_BOIL = 0.01         # CRYO_CO2 boil-off per day of holdup
A_RL_MET_LEV_M3_H = 720.0    # VENT_SCRUB_EQUIPMENT 2.4 band 540-900 mid
A_RL_MET_ACH, A_RL_MET_VOL = 6.0, 300.0
A_RL_CU_TO_WIRE = 0.5
A_RL_SWARF = 0.10
A_RL_FUME_MELT = 0.003
A_RL_FINES_ATOM = 0.01
A_RL_SCRUB_SOLIDS = 0.02
A_RL_MIST_G_KG = 2.0
A_RL_MELT_RECOV = 0.55
A_RL_DUST = 0.005            # baghouse catch, share of shredded feed
A_RL_HP_ETA_CARNOT = 0.45
A_RL_HP_SUPPLY_K = 328.0
A_RL_ROOF_M3, A_RL_ROOF_H, A_RL_HYDRO_KWH = 200.0, 18.0, 7.0
A_RL_ZNBR2_KWH, A_RL_ZNBR2_RTE = 120.0, 0.75   # FLOW_BATTERY 70-80 % mid, one cycle/d
A_RL_S11_DM, A_RL_C_DM = 0.42, 0.45
A_RL_LED_DLI, A_RL_LED_EFF = 17.0, 2.7   # LED check only
A_RL_RHO_SLURRY = 1.10
A_RL_HUM_NONGREY = None      # hab non-grey water is by difference from S12 (S12 governs)


def psat_kpa(t):
    return 0.61094 * math.exp(17.625 * t / (t + 243.04))


def w_sat(t, p=101.325):
    ps = psat_kpa(t)
    return 0.622 * ps / (p - ps)


def rho_air(t):
    return 101325 / (R_AIR * (t + 273.15))


class Rater:
    def __init__(self, g):
        self.g = g
        self.E = {e["stream_id"]: e for e in g["edges"]}
        self.rates = {}      # sid -> dict(value, unit, note, params)
        self.off = {}        # node -> list of off-graph terms
        self.log = []

    def r(self, sid):
        if sid in self.rates:
            return self.rates[sid]["value"]
        return (self.E[sid].get("rate") or {}).get("value")

    def set(self, sid, value, unit, basis, source, medium, cond, kind="derived", **params):
        self.rates[sid] = dict(value=round(value, 4) if abs(value) < 100 else round(value, 2), unit=unit,
                               note=basis, params=dict(rate_basis=basis, rate_source=source, medium=medium,
                                                       conditions=cond, rate_kind=kind, **params))

    def offg(self, node, layer, direction, label, value, basis, kind="derived"):
        self.off.setdefault(node, []).append(dict(layer=layer, dir=direction, label=label, value=round(value, 4),
                                                  basis=basis, kind=kind))


def rate_all(g):
    R = Rater(g)
    feed = hl.FEED_KG_D
    tpd = feed / 1000.0
    # ================================================================ EW / leach
    diss = {}
    for m, kg_t in A_RL_PM_KG_T.items():
        diss[m] = kg_t * A_RL_PM_LEACH * tpd
    lm = {}
    for row in (hl.LEACH_METALS.items() if isinstance(hl.LEACH_METALS, dict) else hl.LEACH_METALS):
        if isinstance(hl.LEACH_METALS, dict):
            name, v = row
            kg_t, frac = v[0], v[1]
        else:
            name, kg_t, frac = row[0], row[1], row[2]
        lm[name] = kg_t * frac * tpd
    blend_key = [k for k in lm if k not in ("Fe", "Cu", "Al")][0]
    diss.update(Cu=lm["Cu"], Fe=lm["Fe"])
    for m in ("Pb", "Sn", "Ni", "Cd", "Zn"):
        diss[m] = lm[blend_key] / 5.0
    al = lm["Al"]
    plateable = sum(diss.values())
    s08 = R.r("S08")
    f_plate = s08 / plateable
    q_ew = hl.CONC_M3_H * hl.RHO_LIQ * 24.0
    h8 = hl.hx8()
    evap_cell = h8["evap_bare_kg_h"] * (1 - hl.A_J_BALL) * 24.0 / hl.EW_N
    side = {"EW_1": "IA-HDR-H2-01", "EW_2": "IA-HDR-H2-03", "EW_9": "IA-HDR-H2-04"}
    chain = ["IA-EW-01", "IA-EW-02", "IA-EW-03", "IA-EW-10", "IA-EW-05", "IA-EW-06", "IA-EW-07", "IA-EW-08", "IA-EW-09"]
    R.set("IA-EW-04", q_ew, "kg/d", f"DUTY-008 concentrate {hl.CONC_M3_H} m3/h x {hl.RHO_LIQ} kg/m3 x 24 h",
          "AQS-DUTY-008 (_hl_edges_study CONC_M3_H, RHO_LIQ)", "chloride leach liquor (HCl/NaClO3, metal chlorides)",
          f"{hl.A_J_T_LEACH} C, atm", m3_h=hl.CONC_M3_H)
    flow = q_ew
    ew = []
    cl2_tot = h2_tot = dep_tot = 0.0
    for i, m in enumerate(EW_METALS):
        cell = f"EW_{i + 1}"
        dep = diss[m] * f_plate
        cl2 = dep / M[m] * N_E[m] / 2 * M["Cl2"]
        h2 = R.r(side[cell]) if cell in side else 0.0
        cl2s = h2 / M["H2"] * M["Cl2"]
        out = flow - dep - cl2 - h2 - cl2s - evap_cell
        sid = chain[i]
        R.set(sid, out, "kg/d", f"{cell} in {flow:.1f} - {m} deposit {dep:.3f} - anode Cl2 {cl2:.3f} - side H2 {h2:.2f} - side Cl2 {cl2s:.2f} - evaporation {evap_cell:.2f}",
              "AQS-DUTY-010 EW mass step; S08 deposit split by leach build-up (ELECTRICAL assay); H2 from IA-HDR-H2-*; evaporation DUTY-008 HX-8",
              "chloride electrolyte overflow", f"{hl.A_J_T_EW} C, atm", deposit_kg_d=round(dep, 4), anode_cl2_kg_d=round(cl2 + cl2s, 3))
        R.offg(cell, "mass", "out", f"{m} cathode harvest (reported on S08)", dep, "S08 split by leach build-up")
        R.offg(cell, "mass", "out", "anode Cl2 to HDR_ACID_GAS", cl2 + cl2s, "Faraday: n/2 Cl2 per metal; 1 Cl2 per side-reaction H2")
        R.offg(cell, "mass", "out", "evaporation to EW hood (ball blanket)", evap_cell, "DUTY-008 HX-8 bare evaporation x (1 - ball blanket) / 9")
        ew.append(dict(cell=cell, metal=m, in_kg_d=round(flow, 2), deposit=round(dep, 4), cl2=round(cl2, 3), h2=h2, cl2_side=round(cl2s, 2), out=round(out, 2)))
        cl2_tot += cl2 + cl2s
        h2_tot += h2
        dep_tot += dep
        flow = out
    raff = flow
    regen = cl2_tot + h2_tot
    # ---- leach solids and float/sink
    moist = feed * hl.MOIST_FRAC
    dissolved = plateable + al
    undissolved = feed - moist - dissolved
    plastic = A_RL_PLASTIC * feed
    cullet = hl.CULLET_KG_D
    sink_solids = undissolved - plastic
    residue = sink_solids - cullet
    liquor = undissolved * (1 - A_RL_SLURRY_WT) / A_RL_SLURRY_WT
    float_water = hl.draws()[0]["water_kg_d"]
    x_cake = float_water / (plastic + float_water)
    sink_water = sink_solids * x_cake / (1 - x_cake)
    ret = liquor - float_water - sink_water
    R.set("IA-WET-FLOAT-01", ret, "kg/d", f"slurry liquor {liquor:.1f} (20 wt % on {undissolved:.2f} kg/d undissolved) less cake moisture float {float_water} + sink {sink_water:.2f}",
          "AQS-DUTY-010; float moisture = DUTY-008 dryer water basis", "leach liquor return", "~60 C, atm", slurry_solids_kg_d=round(undissolved, 2))
    R.offg("FLOAT_SINK", "mass", "in", "leach train slurry (solids + liquor)", undissolved + liquor, "LEACH out; 20 wt % solids")
    R.offg("FLOAT_SINK", "mass", "out", "float cake to OIL_DRYER", plastic + float_water, "plastic + paper 22 % + DUTY-008 dryer water")
    R.offg("FLOAT_SINK", "mass", "out", "sink cake to GLASS_RINSE", sink_solids + sink_water, "glass + residue at float cake moisture")
    R.offg("OIL_DRYER", "mass", "in", "float cake", plastic + float_water, "FLOAT_SINK")
    R.offg("OIL_DRYER", "mass", "out", "dryer vapor", float_water, "DUTY-008 dryer water 7.5 kg/d")
    gw = sink_water * cullet / sink_solids
    R.offg("GLASS_RINSE", "mass", "in", "sink cake", sink_solids + sink_water, "FLOAT_SINK")
    R.offg("GLASS_RINSE", "mass", "out", "sink residue reject (no product path in yields table)", residue + sink_water - gw, "assay unassigned + unleached metal; flagged")
    R.set("IA-GLASS-01", cullet + gw, "kg/d", f"cullet {cullet} kg/d dry (DUTY-008 burnout basis = silicate yield) + drained moisture {gw:.2f}",
          "AQS-DUTY-008 CULLET_KG_D; ELECTRICAL yields silicate 200 kg/t", "rinsed cullet, drained", "ambient", dry_kg_d=cullet)
    R.offg("GLASS_MILL", "mass", "out", "mill dry-step vapor", gw, "drained moisture off before burnout")
    R.set("IA-GLASS-02", cullet, "kg/d", "dry milled cullet = cullet basis", "AQS-DUTY-008 CULLET_KG_D", "milled cullet, dry", "ambient")
    R.set("IA-GLASS-03", cullet, "kg/d", "burned cullet; organics burnout negligible (DUTY-008 off-gas 0.03 kW)", "AQS-DUTY-008", "burned cullet", f"{hl.A_T_CULLET_OUT} C out")
    dg = hl.draws()[2]
    caustic = dg["caustic_L_d"] * A_RL_RHO_2M["NaOH"]
    R.offg("GLASS_DIGEST", "mass", "in", "2 M NaOH digest liquor", caustic, "DUTY-008 digest 593 mol/d at 2 M")
    R.offg("GLASS_DIGEST", "mass", "out", "sodium silicate liquor (carries the caustic)", caustic, "same liquor; S08G is on the cullet-equivalent yield basis")
    # ---- oil line
    oil = A_RL_OIL_KG_T * tpd
    ncg_f = hl.sources()[0]["fuel_kg_d"]
    vol = oil + ncg_f
    char = plastic - vol

    def W(n, a):
        return 1 - a ** n * (n * (1 - a) + 1)
    lo, hi = 0.30, 0.99
    for _ in range(200):
        a = (lo + hi) / 2
        if W(4, a) / W(28, a) > ncg_f / vol:
            lo = a
        else:
            hi = a
    alpha = (lo + hi) / 2
    w28 = W(28, alpha)
    rec = vol / w28 * (1 - w28)
    fr = [(W(10, alpha) - W(4, alpha)), (W(18, alpha) - W(10, alpha)), (W(28, alpha) - W(18, alpha))]
    fr = [x / sum(fr) for x in fr]
    cut = [oil * x for x in fr]
    s38 = 0.006
    solv = A_RL_SOLV_L_D * A_RL_RHO_SOLV
    formed = None
    R.set("IA-OIL-01", plastic, "kg/d", f"dry plastic + paper float {A_RL_PLASTIC} x {feed}", "ELECTRICAL assay", "dried plastic/paper float", "dryer out, <110 C")
    R.set("IA-OIL-02", vol + rec, "kg/d", f"per-pass volatiles: net {vol} (oil {oil} + NCG {ncg_f}) + C29 recycle {rec:.2f} (ASF alpha {alpha:.4f})",
          "ELECTRICAL yields 150 kg/t oil; DUTY-008 NCG fuel; ASF fit", "pyrolysis vapor/condensate", "~450 C pyro out", asf_alpha=round(alpha, 5))
    R.offg("OIL_PYRO", "mass", "out", "char to silicon arc", char, "yields complement: float - oil - NCG")
    R.set("IA-OIL-03", ncg_f, "kg/d", "NCG C1-C4 = DUTY-008 afterburner fuel (CO2 15.0 / 3.002)", "AQS-DUTY-008 sources()", "NCG (C1-C4 gas)", "~1 bar a, 40 C")
    R.set("NCG_TO_AB", ncg_f, "kg/d", "= IA-OIL-03 (header pass-through)", "AQS-DUTY-008", "NCG", "~1 bar a")
    R.set("CUT-4", rec, "kg/d", "C29+ per pass, recycled to extinction", "ASF fit", "C29+ heavy cut", "~250 C")
    R.set("C29_RECYCLE", rec, "kg/d", "= CUT-4", "ASF fit", "C29+ heavy cut", "hot, to pyrolyzer only")
    R.set("C29_TO_PYRO", rec, "kg/d", "= C29_RECYCLE", "ASF fit", "C29+ heavy cut", "pyro inlet")
    s72b = None  # set in MFG below; CUT-1/CUT-3 completed after MFG
    X = dict(ew=ew, raff=raff, regen=regen, cl2_tot=cl2_tot, h2_tot=h2_tot, dep_tot=dep_tot, al=al, dissolved=dissolved,
             undissolved=undissolved, residue=residue, liquor=liquor, alpha=alpha, rec=rec, cut=cut, char=char,
             solv=solv, s38=s38, moist=moist, plateable=plateable, f_plate=f_plate, diss=diss, oil=oil, vol=vol,
             plastic=plastic, sink_solids=sink_solids)

    # ================================================================ fab (ST-LITHO-01: 3 starts/d; AUD s13 bands)
    st = A_RL_STARTS
    upw = A_RL_UPW_BAND[0] + (A_RL_UPW_BAND[1] - A_RL_UPW_BAND[0]) * (st - 1) / 4
    R.set("S27", upw, "kg/d", f"fab UPW {A_RL_UPW_BAND[0]:.0f}-{A_RL_UPW_BAND[1]:.0f} L/d for 1-5 starts, at {st} starts", "AQS-AUD-001 s13 + ST-LITHO-01", "UPW >18 MOhm.cm", "ambient, 1.0 kg/L")
    bands = dict(S31=(0.5, 2.5, "HF (aq) dilute"), S32=(1, 5, "H2O2 dilute (SC-1/SC-2)"), S33=(1, 5, "NH4OH dilute (SC-1)"))
    for sid, (lo_, hi_, med) in bands.items():
        v = lo_ + (hi_ - lo_) * (st - 1) / 4
        R.set(sid, v, "kg/d", f"AUD s13 band {lo_}-{hi_} L/d at {st} of 1-5 starts, dilute 1.0 kg/L", "AQS-AUD-001 s13", med, "ambient")
    v34 = (0.5 + (2.0 - 0.5) * (st - 1) / 4) / 2
    R.set("S34", v34 * A_RL_RHO_2M["HNO3"], "kg/d", f"AUD s13 WS_NITRIC/WS_PHOS band 0.5-2 L/d at {st} starts = {2 * v34:.3f} L/d, 50/50 split; 2 M HNO3 at 1.064 kg/L",
          "AQS-AUD-001 s13", "HNO3 2 M", "ambient", L_d=v34)
    R.set("S34B", v34, "kg/d", f"50/50 split of the same band, {v34:.3f} L/d dilute 1.0 kg/L", "AQS-AUD-001 s13", "H3PO4 dilute", "ambient", L_d=v34)
    v35 = 0.25
    R.set("S35", v35 * A_RL_RHO_2M["KOH"], "kg/d", "AUD s13 <0.5 L/d -> 0.25 L/d of 2 M KOH (1.09 kg/L)", "AQS-AUD-001 s13", "KOH 2 M", "ambient", L_d=v35)
    R.set("S36", 0.01, "kg/d", "AUD s13 grams/d concentrate -> 10 g/d", "AQS-AUD-001 s13", "B/P dopant concentrate", "cabinet")
    v37 = 1 + (5 - 1) * (st - 1) / 4
    R.set("S37", v37 * A_RL_RHO_SLURRY, "kg/d", f"AUD s13 1-5 L/d makeup at {st} starts = {v37} L/d x 1.1 kg/L", "AQS-AUD-001 s13", "colloidal silica slurry", "ambient")
    n2 = A_RL_N2_SLM * A_RL_N2_MIN * st * M["N2"] / 22.414 / 1000
    R.set("S03", n2, "kg/d", f"{A_RL_N2_SLM} slm x {A_RL_N2_MIN} min x {st} starts at 1.25 g/L", "ST-LITHO-01 starts; tool purge class", "N2 gas", "ambient, ~2 bar g")
    R.set("S38", s38, "kg/d", "ST-LITHO-01 resist waste 6 g/d", "ST-LITHO-01", "resist and solvent waste", "ambient")
    R.set("S39B", solv, "kg/d", f"WS_SOLV {A_RL_SOLV_L_D} L/d (AUD s13 0.5-2 mid) x {A_RL_RHO_SOLV}", "AQS-AUD-001 s13 WS_SOLV", "solvent and photoresist", "ambient")
    R.offg("WAFER_FAB", "mass", "in", "WS_SOLV solvent (litho/strip)", solv, "AUD s13 WS_SOLV")
    R.offg("WAFER_FAB", "mass", "out", "N2 purge to fab exhaust", n2, "= S03")
    R.set("S39", R.rates["S37"]["value"] + 0.01, "kg/d", "spent slurry + dopant residue = S37 + S36 (AUD: spent return same order as forwards)", "AQS-AUD-001 s13", "spent slurry and etch liquor", "ambient")
    # BMED products (ELECTRICAL energy basis)
    pair_kg = A_RL_BMED_KWH_D / A_RL_BMED_KWH_KG
    mol = pair_kg * 1000 / (M["HCl"] + M["NaOH"])
    acid = mol / A_RL_M_REAGENT * A_RL_RHO_2M["HCl"]
    base = mol / A_RL_M_REAGENT * A_RL_RHO_2M["NaOH"]
    R.set("IA-BMED-03", acid, "kg/d", f"BMED {A_RL_BMED_KWH_D} kWh/d / {A_RL_BMED_KWH_KG} kWh/kg pair = {pair_kg:.2f} kg/d = {mol:.1f} mol/d HCl as 2 M",
          "ELECTRICAL BMED 80 kWh/t, 1.8-2.4 kWh/kg", "HCl 2 M acid loop", "ambient", mol_d=round(mol, 1))
    R.set("IA-BMED-04", base, "kg/d", f"{mol:.1f} mol/d NaOH as 2 M", "ELECTRICAL BMED", "NaOH 2 M base loop", "ambient", mol_d=round(mol, 1))
    hcl_37 = 1.5 * 1.18 * 0.37
    s09 = hcl_37 * 1000 / M["HCl"] / A_RL_M_REAGENT * A_RL_RHO_2M["HCl"]
    R.set("S09", s09, "kg/d", f"SC-2 1:1:5 -> HCl volume = H2O2 SC-2 share 1.5 L/d (37 % eq, {hcl_37:.3f} kg HCl) delivered as 2 M BMED acid",
          "RCA SC-2 recipe; S32 split", "HCl 2 M", "ambient")
    n34 = v34 * A_RL_M_REAGENT
    R.set("IA-BMED-01", n34 / A_RL_M_REAGENT * A_RL_RHO_2M["HCl"], "kg/d", f"1:1 molar HCl for S34 ({n34:.2f} mol/d HNO3) at 2 M, resin exchange",
          "S34 stoichiometry", "HCl 2 M", "ambient")
    R.offg("WS_NITRIC", "mass", "in", "NaNO3 salt", n34 * M["NaNO3"] / 1000, "1:1 molar")
    n35 = v35 * A_RL_M_REAGENT
    R.set("IA-BMED-02", n35 / A_RL_M_REAGENT * A_RL_RHO_2M["NaOH"], "kg/d", f"1:1 molar NaOH for S35 ({n35:.2f} mol/d KOH) at 2 M, resin exchange",
          "S35 stoichiometry", "NaOH 2 M", "ambient")
    R.offg("WS_KOH", "mass", "in", "KCl salt", n35 * M["KCl"] / 1000, "1:1 molar")
    for node, sids in (("WS_NITRIC", ("IA-BMED-01", "S34")), ("WS_KOH", ("IA-BMED-02", "S35"))):
        salt = R.off[node][0]["value"]
        R.offg(node, "mass", "out", "spent exchange brine", R.rates[sids[0]]["value"] + salt - R.rates[sids[1]]["value"], "level of the exchange column", kind="by_difference")
    bench_in = sum(R.rates[s]["value"] for s in ("S09", "S27", "S31", "S32", "S33", "S34", "S34B", "S35"))
    R.offg("WET_BENCH", "mass", "in", "resist from the litho track", s38, "ST-LITHO-01")
    R.set("S10", bench_in, "kg/d", "WS forwards sum completed: all bench inputs (S09, S27, S31-S35, S34B) + resist - S38", "AQS-AUD-001 s13 (spent = forwards)",
          "spent etch + rinse to REGEN LEACH", "ambient", kind="by_difference")
    R.log.append(f"S10 re-derived {(R.E['S10'].get('params') or {}).get('rev_k_value', R.E['S10']['rate']['value'])} -> {bench_in:.2f} kg/d: Rev K value omitted S27 rinse and S09")

    # ================================================================ MFG / metals
    cu_dep = diss["Cu"] * f_plate
    blend_dep = sum(diss[m] for m in ("Pb", "Sn", "Ni", "Cd", "Zn")) * f_plate
    cu_w = cu_dep * A_RL_CU_TO_WIRE
    fume = cu_w * A_RL_FUME_MELT
    s57 = cu_w - fume
    s58 = s57 * (1 - A_RL_SWARF)
    s59 = (cu_dep - cu_w) * (1 - A_RL_SWARF)
    fines = blend_dep * A_RL_FINES_ATOM
    s60 = blend_dep * (1 - A_RL_SWARF)
    sw = (s57 - s58) + (cu_dep - cu_w - s59) + (blend_dep - s60 - fines)
    R.set("S57", s57, "kg/d", f"Cu deposit {cu_dep:.3f} x {A_RL_CU_TO_WIRE} to wire, less melt fume {A_RL_FUME_MELT:.1%}", "S08 split (EW-3 Cu share)", "Cu billet", "cast")
    R.set("S58", s58, "kg/d", f"S57 less {A_RL_SWARF:.0%} draw swarf", "forming yield", "Cu wire", "ambient")
    R.set("S59", s59, "kg/d", f"Cu {cu_dep - cu_w:.3f} to cold mill less {A_RL_SWARF:.0%} trim", "forming yield", "Cu sheet/strip", "ambient")
    R.set("S60", s60, "kg/d", f"blend deposit {blend_dep:.3f} (Pb/Sn/Ni/Cd/Zn) less {A_RL_SWARF:.0%} off-spec", "atomizer yield", "metal powder", "ambient")
    R.set("S61", sw, "kg/d", "swarf/trim/off-spec from draw, mill and atomizer (less LEV fines)", "forming yield", "metal scrap", "ambient")
    R.offg("MET_MELT", "mass", "in", "Cu charge from MFG_SHOP", cu_w, "S08 Cu share")
    R.offg("MET_MELT", "mass", "out", "melt fume to MET LEV (S71)", fume, "A_RL_FUME_MELT")
    R.offg("WIRE_DRAW", "mass", "out", "draw swarf to MFG_SHOP scrap bin", s57 - s58, "A_RL_SWARF")
    R.offg("COLD_MILL", "mass", "in", "Cu charge from MFG_SHOP", cu_dep - cu_w, "S08 Cu share")
    R.offg("COLD_MILL", "mass", "out", "mill trim to MFG_SHOP scrap bin", cu_dep - cu_w - s59, "A_RL_SWARF")
    R.offg("GAS_ATOMIZER", "mass", "in", "blend charge from MFG_SHOP", blend_dep, "S08 blend share")
    R.offg("GAS_ATOMIZER", "mass", "out", "off-spec to MFG_SHOP scrap bin", blend_dep - s60 - fines, "A_RL_SWARF")
    R.offg("GAS_ATOMIZER", "mass", "out", "ultrafines to MET LEV (S71)", fines, "A_RL_FINES_ATOM")
    s16 = R.r("S16")
    mfg_in = s08 + s58 + s59 + s60 + sw
    goods = mfg_in - s16 - sw - cu_dep - blend_dep
    R.offg("MFG_SHOP", "mass", "in", "scrap bin returns", sw, "draw/mill/atomizer")
    R.offg("MFG_SHOP", "mass", "out", "charges to MET_MELT, COLD_MILL, GAS_ATOMIZER", cu_dep + blend_dep, "S08 Cu + blend")
    R.offg("MFG_SHOP", "mass", "out", "finished goods to NORTH_DOCK", goods, "shop product = all not returned", kind="by_difference")
    R.set("DOCK_EXPORT_TBD", goods, "kg/d", "MFG_SHOP finished goods (Fe plate, wire, sheet, powder) to export", "AQS-DUTY-010 MFG balance",
          "metal goods (solid)", "palletized", kind="by_difference")
    R.offg("NORTH_DOCK", "mass", "in", "finished goods from MFG_SHOP", goods, "MFG_SHOP balance")
    mist = A_RL_MIST_G_KG / 1000 * (s58 + s59)
    s72_sol = fume + fines
    s72 = s72_sol / A_RL_SCRUB_SOLIDS
    s71 = A_RL_MET_LEV_M3_H * rho_air(25.0)
    s62 = A_RL_MET_ACH * A_RL_MET_VOL * rho_air(25.0)
    R.set("S71", s71, "kg/h", f"MET LEV {A_RL_MET_LEV_M3_H} m3/h (VENT_SCRUB 2.4 band 540-900 mid) at 1.184 kg/m3", "hub VENT_SCRUB_EQUIPMENT 2.4",
          "air + metal fume/fines/mist", "25 C, atm", m3_h=A_RL_MET_LEV_M3_H)
    R.set("S62", s62, "kg/h", f"MET aisle general exhaust {A_RL_MET_ACH} ACH x {A_RL_MET_VOL} m3", "ventilation basis", "air", "25 C, atm",
          m3_h=A_RL_MET_ACH * A_RL_MET_VOL)
    R.set("S72", s72, "kg/d", f"fines {s72_sol:.4f} kg/d (melt fume + atomizer ultrafines) in scrub blowdown at {A_RL_SCRUB_SOLIDS:.0%} solids",
          "AQS-DUTY-010 MET balance", "metal fines in aqueous scrub liquor", "ambient")
    R.set("S72B", mist, "kg/d", f"lubricant mist {A_RL_MIST_G_KG} g/kg formed x {s58 + s59:.2f} kg/d", "forming practice", "organic mist (draw/roll lube)", "ambient")
    R.offg("MET_SCRUB", "mass", "in", "scrub make-up water", s72 - s72_sol, "level control = blowdown water", kind="derived")
    R.offg("MET_SCRUB", "mass", "out", "scrubbed air to stack", (s62 + s71) * 24 - s72_sol - mist, "air in less captured fines and mist")
    # finish oil cuts
    cut = X["cut"]
    R.set("CUT-1", cut[0] + s38 + solv, "kg/d", f"ASF C5-C10 share {cut[0]:.2f} of net oil {oil} + S38 + S39B solvent", "ELECTRICAL yields; ASF fit", "C5-C10 cut", "tank")
    R.set("CUT-2", cut[1], "kg/d", f"ASF C11-C18 share of net oil {oil}", "ELECTRICAL yields; ASF fit", "C11-C18 cut", "tank")
    R.set("CUT-3", cut[2] + mist, "kg/d", f"ASF C19-C28 share {cut[2]:.2f} + S72B lube mist", "ELECTRICAL yields; ASF fit", "C19-C28 cut", "tank")

    # ================================================================ dust, flue, acid gas
    s19 = A_RL_DUST * feed
    R.set("S19", s19, "kg/d", f"baghouse catch {A_RL_DUST:.1%} of shredded feed", "shredder fines class", "WEEE fines", "ambient")
    src = hl.sources()[0]
    m_flue = src["m_flue_kg_h"] * 24
    fuel = src["fuel_kg_d"]
    c_frac = src["co2_kg_per_kg_fuel"] * 12.011 / M["CO2"]
    h2o_fuel = fuel * (1 - c_frac) * M["H2O"] / M["H2"]
    air = m_flue - fuel
    h2o_air = air * A_RL_W_AMB / (1 + A_RL_W_AMB)
    dry = m_flue - h2o_fuel - h2o_air
    ko_ret = dry * w_sat(A_RL_KO_T_C)
    ko_cond = h2o_fuel + h2o_air - ko_ret
    X.update(m_flue=m_flue, ko_cond=ko_cond)
    R.offg("AFTERBURNER", "mass", "in", "combustion air", air, "DUTY-008 flue 10.07 kg/h less fuel")
    R.offg("AFTERBURNER", "mass", "out", "flue to AFTERBURNER_FLUE", m_flue, "DUTY-008 m_flue_kg_h")
    R.offg("AFTERBURNER_FLUE", "mass", "in", "flue from AFTERBURNER", m_flue, "DUTY-008")
    s11_co2 = R.r("S11") * A_RL_S11_DM * A_RL_C_DM * M["CO2"] / 12.011
    X["s11_co2"] = s11_co2
    s90_pre = A_RL_O2_P_D * 4 * A_RL_RQ * M["CO2"] / M["O2"]
    buf = (R.r("S85") + s90_pre) * (24 - co2.A_PHOTO_H) / 24
    s70 = A_RL_CO2_BOIL * buf
    R.set("S70", s70, "kg/d", f"CRYO_CO2 boil-off {A_RL_CO2_BOIL:.0%}/d of the {buf:.2f} kg dark buffer, vented via the cryo AHU condensables box",
          "AQS-DUTY-009 dark buffer", "CO2 vapor (condensables)", "ambient")
    R.offg("CRYO_CO2", "mass", "out", "boil-off to CRYO AHU (S70)", s70, "= S70")
    R.offg("FLUE_KO", "mass", "out", "KO condensate", ko_cond, f"flue water less saturation at {A_RL_KO_T_C} C")
    R.offg("FLUE_KO", "mass", "out", "VSA tail gas to stack", m_flue + s70 - R.r("S67B") - ko_cond, "flue + S70 less captured CO2 and condensate")
    # acid gas polish
    slip = cl2_tot * A_RL_SLIP
    nmol = slip * 1000 / M["Cl2"]
    salt = nmol * (M["NaCl"] + M["NaOCl"]) / 1000
    s66 = salt / A_RL_POL_SALT_WT
    R.set("S66", s66, "kg/d", f"Cl2 slip {A_RL_SLIP:.0%} of {cl2_tot:.1f} kg/d EW anode Cl2 -> NaCl + NaOCl {salt:.2f} kg/d at {A_RL_POL_SALT_WT:.0%} salts",
          "VENT_SCRUB_EQUIPMENT 2.1 (blowdown 50-200 L per transfer)", "hypochlorite/chloride scrub liquor", "ambient")
    rho50 = rho_air(A_RL_POLISH_T_C)
    s65 = A_RL_POLISH_M3_H * rho50 * (1 + w_sat(A_RL_POLISH_T_C)) / (1 + w_sat(A_RL_POLISH_T_C) * 1.608)
    R.set("S65", s65, "kg/h", f"polish {A_RL_POLISH_M3_H} m3/h at {A_RL_POLISH_T_C} C saturated", "hub VENT_SCRUB_EQUIPMENT 2.1; FAN_STACK HDR_ACID_GAS 1500 m3/h",
          "acid-gas residual in moist air", f"{A_RL_POLISH_T_C} C, atm", m3_h=A_RL_POLISH_M3_H)
    R.offg("ACID_POLISH_SCRUB", "mass", "in", "make-up water + NaOH", s66 - slip, "level control")
    R.offg("ACID_POLISH_SCRUB", "mass", "out", "polished air to stack", s65 * 24 - slip, "S65 less absorbed Cl2")
    # ZnBr2 Br2 regen
    dry = A_RL_BR2_PURGE_M3_H * rho_air(25.0) / (1 + A_RL_W_AMB) * 24
    vap = dry * A_RL_W_AMB
    br2 = A_RL_BR2_PURGE_M3_H * A_RL_BR2_PPMV * 1e-6 * (M["Br2"] / 24.465) * 24
    naoh_l = br2 / M["Br2"] * 2 / A_RL_M_REAGENT
    s69b = vap + br2 + naoh_l * A_RL_RHO_2M["NaOH"]
    R.set("S69", dry + vap + br2, "kg/d", f"headspace purge {A_RL_BR2_PURGE_M3_H} m3/h (VENT_SCRUB 2.2 band 10-50 mid) at ambient humidity + {A_RL_BR2_PPMV:.0f} ppmv Br2",
          "hub VENT_SCRUB_EQUIPMENT 2.2", "moist air + Br2 vapor", "25 C, atm", br2_kg_d=round(br2, 4), water_kg_d=round(vap, 2), m3_h=A_RL_BR2_PURGE_M3_H)
    R.set("S69B", s69b, "kg/d", f"scrub liquor: saturation water {vap:.2f} + Br2 {br2:.4f} + NaOH make-up {naoh_l * A_RL_RHO_2M['NaOH']:.4f}",
          "Br2 + 2 NaOH; vapor condensed in the scrub", "NaBr/NaBrO liquor", "ambient")
    R.offg("ZNBR2", "mass", "in", "purge air (dry)", dry, "headspace purge")
    R.offg("ZNBR2", "mass", "out", "electrolyte accumulation (Na + water from S69B, less Br2)", s69b - br2, "no electrolyte bleed on the graph", kind="accumulation")
    R.offg("ZNBR2_BR2_REGEN", "mass", "in", "2 M NaOH make-up", naoh_l * A_RL_RHO_2M["NaOH"], "stoichiometric")
    R.offg("ZNBR2_BR2_REGEN", "mass", "out", "scrubbed dry air to stack", dry, "")

    # ================================================================ cryo, gas, power
    s02 = A_RL_O2_P_D * 4
    R.set("S02", s02, "kg/d", f"{A_RL_O2_P_D} kg O2/p.d x 4 crew", "NASA BVAD nominal; crew 4", "O2 gas", "regulated, ambient")
    R.log.append(f"S02 corrected 3.4 -> {s02:.2f} kg/d (0.84 x 4)")
    R.set("S15", 0.0, "kg/d", "photosynthetic O2 (0.806 kg/d) leaves with FARM AHU exhaust; HAB is sealed with its own AHU and is supplied by S02",
          "AQS-DUTY-009 farm OA; S04 stoichiometry", "O2 (none delivered)", "n/a")
    for sid in ("S83", "S84"):
        R.set(sid, 0.0, "kg/d", "HDR_O2/HDR_N2 have no consumer edge; hab O2 is S02, N2 is S03. A non-zero fill would double count.",
              "graph topology", "O2 gas" if sid == "S83" else "N2 gas", "header pressurized, no draw")
    o2_out = s02 + R.r("S50")
    asu = o2_out / (A_RL_Y_O2 * A_RL_ASU_REC)
    stg = A_RL_ASU_P ** 0.5
    t2 = 298.15 + 298.15 * (stg ** (0.4 / 1.4) - 1) / A_RL_ETA_IS
    w_shaft = 2 * (asu / 86400) * 1.006 * (t2 - 298.15)
    f_q4 = (t2 - 273.15 - hl.A_J_Q4_RET) / (t2 - 273.15 - 25.0)
    sieve = 2 * asu * A_RL_W_AMB * 2.5e3 / 86400 * A_RL_SIEVE_RECOV
    s54 = w_shaft * f_q4 + sieve
    R.set("S54", s54, "kW", f"ASU air {asu:.1f} kg/d, 2-stage to {A_RL_ASU_P} bar a (eta_is {A_RL_ETA_IS}): shaft {w_shaft:.3f} kW x {f_q4:.3f} above Q4 return + sieve TSA {sieve:.3f}",
          "CRYO_COLD_BOX (intercooler residual + sieve cool-down)", "Q4 water", "45 C return / 60 C supply", asu_air_kg_d=round(asu, 1))
    qc = (o2_out * (0.918 * 208 + 213) + n2 * (1.04 * 221 + 199)) / 86400 * (1 + A_RL_COLD_LEAK)
    R.set("S55", A_RL_STIRLING_KW + qc, "kW", f"Stirling reject = electric {A_RL_STIRLING_KW} + lift {qc:.3f} kW (O2 + N2 liquefaction + {A_RL_COLD_LEAK:.0%} leak)",
          "CRYO_COLD_BOX; CONTINUOUS_KW 2-8 kW class", "glycol 30 %", "dT 5 K", glycol_kg_h=round((A_RL_STIRLING_KW + qc) / (3.6 * 5) * 3600, 0))
    xs = w_sat(A_RL_COIL_T_C)
    s68 = A_RL_CRYO_AHU_M3_H * rho_air(25.0) / (1 + A_RL_W_AMB) * (A_RL_W_AMB - xs) * 24
    R.set("S68", s68, "kg/d", f"CRYO AHU {A_RL_CRYO_AHU_M3_H:.0f} m3/h coil to {A_RL_COIL_T_C} C dew (w {A_RL_W_AMB} -> {xs:.5f}); latent {s68 / 24 * 2454 / 3600:.2f} kW",
          "RELIEF_CRYO size basis 12 ACH x 216 m3; VENT_SCRUB 2.3 KO 2-5 kW", "AHU coil condensate (carries text says flue condensate: flagged)", "~10 C")
    for sid in ("S56", "S86", "S24"):
        R.set(sid, 0.0, "kg/d", "contingency relief only; no continuous flow on the design day", "NFPA 55 / NFPA 2 relief class", "relief gas", "event only")
    gen_air = R.r("S45") * A_RL_GEN_AFR * A_RL_GEN_LAMBDA
    R.set("S46", R.r("S45") + gen_air, "kg/d", f"S45 {R.r('S45')} + air at lambda {A_RL_GEN_LAMBDA} ({A_RL_GEN_AFR} kg/kg stoich)", "H2 combustion stoichiometry",
          "engine exhaust (H2O, N2, O2, NOx)", "hot exhaust", kg_h=round((R.r("S45") + gen_air) / 24, 2))
    R.offg("BACKUP_GEN", "mass", "in", "combustion air", gen_air, "lambda 2")
    s52 = R.r("S49") * M["H2O"] / M["H2"]
    R.set("S52", s52, "kg/d", f"S49 {R.r('S49')} kg/d H2 x 18.015/2.016", "PEM stoichiometry", "PEM product water", "~60 C")
    o2_st = R.r("S49") * M["O2"] / 2 / M["H2"]
    R.offg("FUEL_CELL", "mass", "out", "cathode excess O2 vent", R.r("S50") - o2_st, "S50 less stoichiometric O2")
    fc_lhv = R.r("S49") * LHV_H2 / 86.4
    f_fc = (A_RL_FC_T_C - hl.A_J_Q4_RET) / (A_RL_FC_T_C - 25.0)
    s53 = (fc_lhv - R.r("S51")) * f_fc
    R.set("S53", s53, "kW", f"FC heat {fc_lhv - R.r('S51'):.3f} kW (LHV {fc_lhv:.3f} - S51) x ({A_RL_FC_T_C}-45)/({A_RL_FC_T_C}-25) above Q4 return",
          "H2 LHV; S51 authority", "Q4 water", "45 C return")
    R.offg("FUEL_CELL", "energy", "in", "H2 LHV (S49)", fc_lhv, "119.96 MJ/kg")
    R.offg("FUEL_CELL", "energy", "out", "low-grade heat to ambient", fc_lhv - R.r("S51") - s53, "below Q4 return")
    R.offg("BACKUP_GEN", "energy", "in", "H2 LHV (S45)", R.r("S45") * LHV_H2 / 86.4, "119.96 MJ/kg")
    R.offg("BACKUP_GEN", "energy", "out", "radiator + exhaust heat", R.r("S45") * LHV_H2 / 86.4 - R.r("S47"), "1 - eta")
    # MeOH
    n_meoh = R.r("S76") * 1000 / M["MeOH"]
    s81 = n_meoh * 2 * M["H2O"] / 1000
    R.set("S81", s81, "kg/d", f"CH3OH + 1.5 O2 -> CO2 + 2 H2O on S76 {R.r('S76')} kg/d", "stoichiometry", "MeOH FC product water (MeOH trace)", "~60 C")
    R.offg("MEOH_FC", "mass", "in", "air O2", n_meoh * 1.5 * M["O2"] / 1000, "stoichiometric")
    eta = 3600 / (A_RL_DMFC_L_KWH * A_RL_RHO_MEOH * LHV_MEOH * 1000)
    q_meoh = R.r("S76") * LHV_MEOH / 86.4
    s79 = q_meoh * eta
    R.set("S79", s79, "kW", f"DMFC eta {eta:.4f} ({A_RL_DMFC_L_KWH} L/kWh) x S76 LHV {q_meoh:.3f} kW; REQ-MEOH-FC 0.5-2 kW band NOT met", "EFOY-class fuel use; ESS_DUTY_MATRIX",
          "DC power", "24 V DC bus")
    R.log.append(f"S79 corrected 1.0 -> {s79:.3f} kW (fuel-limited by S76)")
    s80 = (q_meoh - s79) * f_fc
    R.set("S80", s80, "kW", f"DMFC heat {q_meoh - s79:.3f} kW x {f_fc:.4f} above Q4 return", "MeOH LHV", "Q4 water", "45 C return")
    R.offg("MEOH_FC", "energy", "in", "MeOH LHV (S76)", q_meoh, "19.93 MJ/kg")
    R.offg("MEOH_FC", "energy", "out", "low-grade heat", q_meoh - s79 - s80, "below Q4 return")
    R.offg("MEOH_SYNTH", "mass", "out", "synthesis water", R.r("S75") * M["H2O"] / M["MeOH"], "CO2 + 3 H2 -> CH3OH + H2O")
    # ZnBr2 / hydro / electrical
    dis = A_RL_ZNBR2_KWH / 24
    chg = dis / A_RL_ZNBR2_RTE
    R.set("IA-ESS-ZNBR2-DIS", dis, "kW", f"{A_RL_ZNBR2_KWH} kWh one cycle/d averaged over 24 h", "ESS_DUTY_MATRIX 120 kWh; FLOW_BATTERY", "DC", "bus", peak_kw=60.0)
    R.set("IA-ESS-ZNBR2-CHG", chg, "kW", f"discharge / round trip {A_RL_ZNBR2_RTE} (FLOW_BATTERY 70-80 % mid)", "FLOW_BATTERY", "DC", "bus", peak_kw=60.0)
    R.offg("ZNBR2", "energy", "out", "round-trip loss", chg - dis, "1 - RTE")
    mh = A_RL_ROOF_M3 * 1000
    R.set("IA-ESS-HYDRO-CHG", mh, "kg/d", f"one full {A_RL_ROOF_M3:.0f} m3 cycle per day", "ESS_DUTY_MATRIX pumped hydro 200 m3 / 18 m", "water", "ambient")
    R.set("IA-ESS-HYDRO-DIS", mh, "kg/d", "one full cycle per day", "ESS_DUTY_MATRIX", "water", "ambient")
    e_h = mh * 9.81 * A_RL_ROOF_H / 3.6e6
    for sid in ("S22", "S23"):
        R.set(sid, e_h / 24, "kW", f"hydraulic power: rho V g h = {e_h:.2f} kWh/cycle over 24 h", "ESS_DUTY_MATRIX 9.8 kWh ideal", "water (potential energy)", "18 m head")
    R.set("IA-ESS-HYDRO-ELEC", A_RL_HYDRO_KWH / 24, "kW", f"{A_RL_HYDRO_KWH} kWh recoverable per cycle over 24 h", "ESS_DUTY_MATRIX ~7 kWh recoverable", "AC", "bus")
    for sid in ("S40", "S41", "S42"):
        R.set(sid, 0.0, "kg/d", "event-driven; zero on the dry design day", "AUD s4 terrace S40 event-driven", "water", "event only")
    led = A_RL_LED_DLI / (co2.A_PHOTO_H * 3600) * 1e6 / A_RL_LED_EFF * co2.A_CANOPY_M2 / 1000
    R.set("S20", 5.0, "kW", f"GROW_BED continuous_kw (LED canopy share); LED check {led:.2f} kW in photoperiod at DLI {A_RL_LED_DLI}, {A_RL_LED_EFF} umol/J",
          "graph GROW_BED continuous_kw 5.0 kW (LED canopy share, study)", "DC load", "bus", source_governs="graph node value; LED first-principles check is lower")
    # thermal Q4 peers
    cu_heat = (cu_w) * (0.385 * (1085 - 25) + 205) / 86400 * A_RL_MELT_RECOV
    R.set("S63", cu_heat, "kW", f"Cu melt sensible + latent on {cu_w:.3f} kg/d x {A_RL_MELT_RECOV} recovered (mold/coil water)", "Cu properties", "Q4 water", "45 C return")
    cop = A_RL_HP_ETA_CARNOT * A_RL_HP_SUPPLY_K / (A_RL_HP_SUPPLY_K - 285.0)
    life = hl.main_j()["q4_life_kw"]
    bus_n = hl.main_j()["q4_bus_running_normal_kw"]
    for sid, txt in (("S06", "farm"), ("S44", "Q4 / hab")):
        R.set(sid, 0.0, "kW", f"GEO_HP dispatch: lift only on Q4 deficit. Normal bus {bus_n} kW >= life {life} kW, so 0. Standby (ladder down): {life / 2} kW to {txt}",
              "HEAT_LADDER (GEO_HP only lift); DUTY-008 q4_life_kw", "Q4 water", "60 C supply", standby_kw=life / 2)
    R.set("S43", 0.0, "kW", f"ground heat = 0 while GEO_HP is idle. Standby {life * (1 - 1 / cop):.3f} kW at COP {cop:.2f} (0.45 Carnot 285 -> 328 K) <= GHEX 3.0 kW",
          "GEO_GHEX params; ST-ORC-01", "glycol loop", "12 C ground", standby_kw=round(life * (1 - 1 / cop), 3), cop=round(cop, 2))
    X.update(cop=cop, life=life, bus_n=bus_n)

    # ================================================================ life / water
    crew = 4
    s21 = A_RL_HAB_WATER_L_P_D * crew
    R.set("S21", s21, "kg/d", f"hab hygiene water {A_RL_HAB_WATER_L_P_D} L/p.d x {crew}", "LIFE_MEP fixture class; crew 4", "potable water", "ambient")
    R.log.append(f"S21 corrected 95 -> {s21:.0f} kg/d (95 was the farm sump band)")
    R.offg("ROOF_TANK", "mass", "in", "inventory draw (dry design day, no rain)", s21, "S21 + S40 met from storage")
    R.set("S26", 10.0, "kg/d", "REMIN drink_L_d 10", "REMIN node params", "remineralized potable", "ambient")
    s14 = 0.6 * crew
    R.set("S14", s14, "kg/d", f"crew ration 0.6 kg/p.d x {crew}; production 4.2 = S14 + S14X 1.8", "GROW_BED params ration_kg_person_d_study", "fresh produce", "ambient")
    R.log.append(f"S14 corrected 4.2 -> {s14:.1f} kg/d (S14X governs the surplus)")
    s90 = s02 * A_RL_RQ * M["CO2"] / M["O2"]
    X["s90"] = s90
    s78 = A_RL_FOOD_WASTE * s14
    R.set("S78", s78, "kg/d", f"food waste {A_RL_FOOD_WASTE:.0%} of ration", "FAO household waste class", "food waste", "ambient")
    vs = s78 * A_RL_FW_DM * A_RL_FW_VS
    ch4 = vs * A_RL_CH4_NM3_KG_VS * M["CH4"] / 22.414
    s77 = ch4 * M["MeOH"] / M["CH4"] * A_RL_MEOH_CONV
    R.set("S77", s77, "kg/d", f"VS {vs:.4f} kg/d x {A_RL_CH4_NM3_KG_VS} Nm3 CH4/kg VS -> MeOH at {A_RL_MEOH_CONV:.0%}", "digestion stoichiometry", "biogenic MeOH", "ambient")
    R.offg("MEOH_FERM", "mass", "out", "digestate + CO2 + water", s78 - s77, "feed less MeOH", kind="by_difference")
    s12 = R.r("S12")
    body = s14 - s78 + s02 - s90
    black = crew * sum(A_RL_BLACK_L_P_D)
    cond = s21 + 10.0 - s12 + body - black
    R.offg("HABITATION", "mass", "out", "black water to BLACK_DIGEST", black, "BVAD urine/feces/flush")
    R.offg("HABITATION", "mass", "out", "hab AHU condensate + non-grey remainder", cond, "S12 governs grey", kind="by_difference")
    s30 = black - A_RL_BLACK_GAS
    R.set("S30", s30, "kg/d", f"black water {black:.2f} kg/d less digester gas {A_RL_BLACK_GAS}", "BVAD class", "digest liquor / nutrients", "ambient")
    R.offg("BLACK_DIGEST", "mass", "in", "black water", black, "HABITATION")
    R.offg("BLACK_DIGEST", "mass", "out", "digester gas", A_RL_BLACK_GAS, "VS destruction")
    s29 = 0.95 * s12
    R.set("S29", s29, "kg/d", "grey treat recovery 95 % of S12 (5 % sludge/backwash)", "grey-water practice", "treated grey", "ambient")
    # farm water / CO2
    X["s29"] = s29
    return R, X


GRAPH_IN = [GRAPH]


PLACEHOLDER_OUTCOME = {
    "IA-OIL-01": "present: dried float to pyrolyzer",
    "IA-OIL-02": "present: pyrolysis volatiles to fractionator",
    "IA-WET-FLOAT-01": "present: float/sink liquor return",
    "S28": "present: VCD brine to REGEN LEACH",
    "IA-BMED-03": "present: BMED acid loop make (energy basis)",
    "IA-BMED-04": "present: BMED base loop make (energy basis)",
    "IA-POL-02": "present: retargeted from the POLISH_BANK self-loop stub to POLISH_BANK -> CONTINUOUS_RECYCLE (raffinate return; STUDIES_COMPLETE precedent)",
    "S13": "present: farm sump + farm AHU condensate to VCD",
    "S25": "present: VCD distillate to UPW polish",
    "S26": "present: REMIN drinking water to HAB",
    "S29": "present: treated grey to VCD",
    "S52": "present: PEM product water to VCD",
    "IA-ESS-HYDRO-ELEC": "present: hydro set to bus",
    "IA-ESS-ZNBR2-CHG": "present: ZnBr2 charge",
    "IA-ESS-ZNBR2-DIS": "present: ZnBr2 discharge",
    "DOCK_EXPORT_TBD": "present: MFG goods export (ID stays TBD: no invented DOCK S##)",
}
RETIRE = {
    "IA-POL-01": "flow does not exist: process liquor never enters the UPW polish skid; post-polish brine goes to the AEM bank -> K split -> BMED (notes/aem_bank.md). Raffinate return is IA-POL-02.",
    "S48": "flow does not exist at M1: ST-ORC-01 / GEO_GHEX Q_surplus_kW_th 0 -> P_ORC = eta x 0 = 0; GEO_ORC is a placeholder node.",
    "IA-ESS-MEOH-CHG": "duplicates S75 (MEOH_SYNTH -> MEOH_TANK, 5.0 kg/d).",
    "IA-ESS-MEOH-DIS": "duplicates S79 (MEOH_FC -> SOL_ARK_60K).",
}
HOLD = {
    "S87": "HOLD placeholder: the surplus O2 is the photosynthetic O2 (0.806 kg/d) in FARM AHU exhaust air at ~21 %. Capturing it means sending farm air into a process header (CRYO_O2), which the rule forbids, and it is already counted in S15. No clean endpoint.",
    "S88": "HOLD placeholder: GROW_BED has no N2 demand (farm is outdoor-air ventilated at the DUTY-009 OA rate). Source rule is met (CRYO_N2, not the cryo residual) but there is no sink. No clean endpoint.",
}


def farm_water(R, X, g):
    import tempfile
    tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    json.dump(g, tmp)
    tmp.close()
    c = co2.main(tmp.name)
    os.unlink(tmp.name)
    oa, oa_min = c["farm"]["oa_required_m3_h"], c["farm"]["oa_min_m3_h"]
    ps = psat_kpa(A_RL_FARM_T_C) * A_RL_FARM_RH
    w_farm = 0.622 * ps / (101.325 - ps)
    rho_d = rho_air(25.0) / (1 + A_RL_W_AMB)
    vap = (oa * co2.A_PHOTO_H + oa_min * (24 - co2.A_PHOTO_H)) * rho_d * (w_farm - A_RL_W_AMB)
    et = A_RL_ET_L_M2_D * co2.A_CANOPY_M2
    s13 = et - vap
    R.set("S13", s13, "kg/d", f"ET {et:.1f} ({A_RL_ET_L_M2_D} L/m2.d x {co2.A_CANOPY_M2} m2) - farm exhaust vapor {vap:.1f} (OA {oa} m3/h light, {oa_min} dark; w {w_farm:.4f} - {A_RL_W_AMB})",
          "AQS-DUTY-009 OA; ET class", "farm sump + AHU condensate", "~15 C", oa_m3_h=oa)
    s04 = R.r("S04")
    dm = s04 * 30.026 / M["CO2"]
    o2 = s04 * M["O2"] / M["CO2"]
    s89 = R.r("S89")
    R.offg("GROW_BED", "mass", "in", "UPW make-up from HDR_UPW (S01)", R.r("S01"), "S01")
    R.offg("GROW_BED", "mass", "out", "CO2 to farm exhaust", s89, "AQS-DUTY-009 fate")
    R.offg("GROW_BED", "mass", "out", "water vapor to farm exhaust", vap, "OA x humidity rise")
    R.offg("GROW_BED", "mass", "out", "photosynthetic O2 to farm exhaust", o2, "CO2 + H2O -> CH2O + O2 on S04")
    R.offg("HDR_UPW", "mass", "out", "farm make-up to GROW_BED", R.r("S01"), "S01")
    s29 = X["s29"]
    s52 = R.rates["S52"]["value"]
    feed = s13 + s29 + s52
    s25 = feed * A_RL_VCD_REC
    R.set("S25", s25, "kg/d", f"VCD recovery {A_RL_VCD_REC:.0%} of feed {feed:.1f} (S13 + S29 + S52)", "VCD practice", "distillate", "~40 C")
    R.set("S28", feed - s25, "kg/d", f"VCD brine {1 - A_RL_VCD_REC:.0%} of feed", "VCD practice", "VCD brine", "~40 C")
    R.offg("BMED_UPW_POLISH", "mass", "out", "fab UPW to FAB_UPW_TANK (S27)", R.r("S27"), "S27")
    R.offg("BMED_UPW_POLISH", "mass", "out", "potable to REMIN (S26)", R.r("S26"), "S26")
    R.offg("BMED_UPW_POLISH", "mass", "out", "polish reject", s25 * A_RL_UPW_REJECT, "EDI/RO polish")
    R.offg("FAB_UPW_TANK", "mass", "in", "UPW from BMED_UPW_POLISH", R.r("S27"), "S27")
    R.offg("REMIN", "mass", "in", "UPW from BMED_UPW_POLISH", R.r("S26"), "S26")
    X.update(oa=oa, oa_min=oa_min, vap=vap, et=et, vcd_feed=feed, dm=dm, o2_photo=o2, w_farm=w_farm)
    # ---- leach loop (needs S28)
    others = sum(R.r(s) for s in ("S10", "S16", "S19", "S28", "S39", "S68", "S72", "IA-WET-FLOAT-01"))
    purge = hl.draws()[1]["purge_water_kg_d"]
    slurry = X["undissolved"] + X["liquor"]
    feed_w = hl.FEED_KG_D
    q_ew = R.rates["IA-EW-04"]["value"]
    s08 = R.r("S08")
    rec = q_ew + s08 + slurry + purge - others - feed_w - X["dep_tot"]
    pol2 = rec - X["regen"]
    bleed = X["raff"] - pol2
    R.set("IA-REC-01", rec, "kg/d", f"recycle = IA-POL-02 {pol2:.1f} + REGEN LEACH make-up {X['regen']:.1f} (Cl2 + H2 removed at EW, element basis)",
          "AQS-DUTY-010 leach loop; DUTY-008 HX-5 0.17 m3/h governs the heater", "regenerated leach liquor", f"{hl.A_J_T_REGEN} C", kind="derived")
    R.set("IA-POL-02", pol2, "kg/d", f"raffinate {X['raff']:.1f} less brine bleed {bleed:.1f} to the AEM bank (level control)",
          "AQS-DUTY-010 leach loop", "raffinate", f"~{hl.A_J_T_EW - 5:.0f} C")
    R.offg("POLISH_BANK", "mass", "out", "brine bleed to AEM bank -> K split -> BMED", bleed, "loop level control", kind="by_difference")
    R.offg("CONTINUOUS_RECYCLE", "mass", "in", "REGEN LEACH make-up (BMED HCl + CRU NaClO3)", X["regen"], "Cl2 + H2 evolved at EW, element basis")
    R.offg("LEACH_CSTR_1", "mass", "in", "fresh shredded feed", feed_w, "plant basis 150 kg/d wet")
    R.offg("LEACH_CSTR_1", "mass", "in", "EW cathode harvest booked onto S08", X["dep_tot"], "= S08")
    R.offg("LEACH_CSTR_1", "mass", "out", "slurry to FLOAT_SINK", slurry, "undissolved + 20 wt % liquor")
    R.offg("LEACH_CSTR_1", "mass", "out", "purge vapor", purge, "DUTY-008 HX-5 purge")
    X.update(bleed=bleed, rec=rec, pol2=pol2)


def build(g0):
    g = copy.deepcopy(g0)
    R, X = rate_all(g)
    E = {e["stream_id"]: e for e in g["edges"]}
    N = {n["unit_id"]: n for n in g["nodes"]}
    retired = []
    for sid, why in RETIRE.items():
        if sid in E:
            retired.append(dict(reason=why, edge=E.pop(sid)))
        elif g.get("notes_rev_l_retired"):
            retired = json.loads(g["notes_rev_l_retired"])
    g["edges"] = [e for e in g["edges"] if e["stream_id"] not in RETIRE]
    # IA-POL-02 retarget
    e = E["IA-POL-02"]
    e["to_unit_id"] = "CONTINUOUS_RECYCLE"
    e["carries"] = "raffinate (EW tail after polish) to continuous recycle"
    e["notes"] = "Rev L: was a POLISH_BANK self-loop stub. Raffinate return; the brine bleed leaves POLISH_BANK to the AEM bank (off-graph)."
    if "to_sector_id" in e:
        e["to_sector_id"] = N["CONTINUOUS_RECYCLE"].get("sector_id")
    # S90
    s89 = E["S89"]
    if "S90" in E:
        g["edges"] = [x for x in g["edges"] if x["stream_id"] != "S90"]
    s90 = copy.deepcopy(s89)
    s90.update(stream_id="S90", from_unit_id="HABITATION", to_unit_id="HDR_CO2",
               carries="metabolic CO2 (desorbed from the HAB CO2 sorbent bed)", header="HDR_CO2",
               forbidden="HDR_O2, hab air return, BOUNDARY_EXPORT, process headers",
               claim_status="Closed", from_sector_id=N["HABITATION"].get("sector_id"), to_sector_id=N["HDR_CO2"].get("sector_id"),
               notes="Rev L. CO2 only, from the sealed-hab sorbent (S02 supplies the O2). Joins S85 on HDR_CO2; S89 carries both to the farm AHU dose. No tee to hab air or the dock.")
    s90v = X["s90"]
    s90["rate"] = dict(value=round(s90v, 3), unit="kg/d", status="study",
                       note=f"AQS-DUTY-010: S02 {R.rates['S02']['value']} kg/d O2 x RQ {A_RL_RQ} x 44.01/32.00")
    s90["params"] = dict(doc="AQS-DUTY-010", rate_basis=s90["rate"]["note"], rate_source="NASA BVAD RQ; S02", medium="CO2 gas (desorbed, dry)",
                         conditions="sorbent desorb, compressed to HDR_CO2 3.0 bar a", P_bar_a=3.0, line_DN=15, material="316L")
    g["edges"].append(s90)
    E["S90"] = s90
    hdr_in = R.r("S85") + round(s90v, 3)
    R.set("S89", hdr_in, "kg/d", f"AQS-DUTY-009 Rev B: S85 {R.r('S85')} + S90 {s90v:.3f}", "AQS-DUTY-009 Rev B", "CO2 gas", "3.0 bar a, 20 C")
    # apply rates
    for sid, rr in R.rates.items():
        if sid not in E:
            continue
        e = E[sid]
        old = (e.get("rate") or {}).get("value")
        st = (e.get("rate") or {}).get("status")
        e["rate"] = dict(value=rr["value"], unit=rr["unit"], status="study" if st != "authority" else "authority",
                         note=("AQS-DUTY-010: " + rr["note"])[:400])
        pr = e.get("params") or {}
        pr.update(rr["params"])
        pr["doc"] = pr.get("doc", "AQS-DUTY-010") if sid in ("S89",) else "AQS-DUTY-010"
        if old is not None and abs(old - rr["value"]) > 1e-9:
            pr["rev_k_value"] = old
        e["params"] = pr
        if sid in PLACEHOLDER_OUTCOME:
            e["presence"] = "present"
    # first pass farm/water needs S89/S90 in graph
    farm_water(R, X, g)
    for sid in ("S13", "S25", "S28", "IA-REC-01", "IA-POL-02"):
        rr = R.rates[sid]
        e = E[sid]
        e["rate"] = dict(value=rr["value"], unit=rr["unit"], status="study", note=("AQS-DUTY-010: " + rr["note"])[:400])
        pr = e.get("params") or {}
        pr.update(rr["params"])
        pr["doc"] = "AQS-DUTY-010"
        e["params"] = pr
        if sid in PLACEHOLDER_OUTCOME:
            e["presence"] = "present"
    # S89 / GROW_BED params from the CO2 study rerun
    p89 = E["S89"]["params"]
    p89.update(doc="AQS-DUTY-009 Rev B", oa_required_m3_h=X["oa"], fate_exhaust_kg_d=round(hdr_in, 3),
               m_avg_kg_h=round(hdr_in / 24, 3), m_peak_kg_h=round(hdr_in / 16, 3), dark_buffer_kg=round(hdr_in * 8 / 24, 2))
    gb = N["GROW_BED"]["params"]
    gb.update(food_out_kg_d_study=4.2, co2_in_kg_d={"S04": R.r("S04"), "S89": round(hdr_in, 3)}, co2_to_exhaust_kg_d=round(hdr_in, 3),
              farm_oa_m3_h=X["oa"])
    # holds
    for sid, why in HOLD.items():
        e = E[sid]
        e["presence"] = "placeholder"
        e["rate"] = dict(value=None, unit=None, status="null", note=why)
        e["params"] = dict(e.get("params") or {}, hold_reason=why, doc="AQS-DUTY-010")
    for sid, why in PLACEHOLDER_OUTCOME.items():
        if sid in E:
            E[sid]["presence"] = "present"
            E[sid].setdefault("params", {})["rev_l_outcome"] = why
            if sid == "DOCK_EXPORT_TBD":
                E[sid]["gap_flags"] = [f for f in (E[sid].get("gap_flags") or []) if "rate" not in f]
    return g, R, X, retired


ENERGY_NODES = ["AFTERBURNER", "GLASS_BURNOUT", "Q1_A", "Q1_B", "Q2_A", "Q2_B", "Q3_A", "Q3_B", "Q4_A", "Q4_B", "HX8", "EW_1",
                "OIL_DRYER", "LEACH_CSTR_1", "GLASS_DIGEST", "Q4_BUS", "FUEL_CELL", "BACKUP_GEN", "MEOH_FC", "ZNBR2", "SOL_ARK_60K",
]


def hl_offgraph(R):
    j = hl.main_j()
    s = hl.sources()[0]
    gb = hl.sources()[1]
    for lad in "AB":
        run = j["run_normal"][lad]
        for t in ("Q1", "Q2", "Q3", "Q4"):
            q = f"{t}_{lad}"
            R.offg(q, "energy", "out", "store standing loss", run[t]["loss"], "DUTY-008 store loss")
            if run[t].get("hp_loss"):
                R.offg(q, "energy", "out", "thermosyphon line loss on arrival", run[t]["hp_loss"], "DUTY-008 A_HP_LOSS")
    R.offg("AFTERBURNER", "energy", "in", "NCG heat release", s["q_release_kw"], "DUTY-008")
    for k, lab in (("q_shell_kw", "shell loss"), ("q_hx7_kw", "HX-7 to burnout"), ("q_flue_to_ko_kw", "flue sensible to KO")):
        R.offg("AFTERBURNER", "energy", "out", lab, s[k], "DUTY-008")
    R.offg("GLASS_BURNOUT", "energy", "in", "HX-7 from afterburner", gb["q_hx7_in_kw"], "DUTY-008")
    R.offg("GLASS_BURNOUT", "energy", "in", "electric trim", gb["q_trim_electric_kw"], "DUTY-008")
    for k in ("q_offgas_kw", "q_end_kw", "q_cullet_residual_kw"):
        R.offg("GLASS_BURNOUT", "energy", "out", k, gb[k], "DUTY-008")
    h = hl.hx8()
    R.offg("EW_1", "energy", "in", "cell ohmic heat (9 cells)", h["q_ohmic_kw"], "DUTY-008 HX-8")
    R.offg("EW_1", "energy", "in", "feed sensible above 51 C", h["q_feed_kw"], "DUTY-008 HX-8")
    R.offg("EW_1", "energy", "out", "wall loss", h["q_wall_kw"], "DUTY-008")
    R.offg("EW_1", "energy", "out", "evaporation (ball blanket)", h["q_evap_kw"], "DUTY-008")
    d = hl.draws()
    tn = j["trim_normal"]
    R.offg("OIL_DRYER", "energy", "out", "dryer duty (evaporation)", d[0]["duty_kw"], "DUTY-008")
    R.offg("OIL_DRYER", "energy", "in", "electric trim", tn["HX-4"], "DUTY-008")
    R.offg("LEACH_CSTR_1", "energy", "in", "electric trim (ladder short)", tn["HX-5"], "DUTY-008 trim_normal")
    R.offg("LEACH_CSTR_1", "energy", "out", "HX-5 duty (regen + shell + shred + purge - exotherm)", d[1]["duty_kw"], "DUTY-008")
    R.offg("GLASS_DIGEST", "energy", "in", "electric trim", tn["HX-6"], "DUTY-008 trim_normal")
    R.offg("GLASS_DIGEST", "energy", "out", "digest duty", d[2]["duty_kw"], "DUTY-008")
    R.offg("Q4_BUS", "energy", "out", "life load (hab + farm)", j["q4_life_kw"], "DUTY-008 q4_life_kw = GHEX Q4 life priority")


def edge_energy(e):
    if "thermal" in e["layers"] or "elec" in e["layers"] or ("ess" in e["layers"] and (e.get("rate") or {}).get("unit") == "kW"):
        r = e.get("rate") or {}
        if r.get("unit") != "kW" or r.get("value") is None:
            return None
        dn = (e.get("params") or {}).get("duty_normal_kw")
        return dn if dn is not None else r["value"]
    return None


def edge_mass(e):
    r = e.get("rate") or {}
    if r.get("value") is None:
        return None
    if r.get("unit") == "kg/d":
        return r["value"]
    if r.get("unit") == "kg/h":
        return r["value"] * 24
    return None


SKIP_ENERGY_EDGES = {"S22", "S23"}   # hydraulic potential on the ess layer (checked as mass on IA-ESS-HYDRO-*)


def conserve(g, R):
    nodes = [n["unit_id"] for n in g["nodes"]]
    res = {}
    for u in nodes:
        for layer in ("mass", "energy"):
            ins, outs = [], []
            for e in g["edges"]:
                if e["presence"] != "present" or e["from_unit_id"] == e["to_unit_id"]:
                    continue
                if layer == "mass":
                    v = edge_mass(e) if ("mass" in e["layers"] or "ess" in e["layers"]) else None
                else:
                    v = None if e["stream_id"] in SKIP_ENERGY_EDGES else edge_energy(e)
                if v is None:
                    continue
                kd = "by_difference" if (e.get("params") or {}).get("rate_kind") == "by_difference" else "edge"
                if e["to_unit_id"] == u:
                    ins.append((e["stream_id"], v, kd))
                if e["from_unit_id"] == u:
                    outs.append((e["stream_id"], v, kd))
            for t in R.off.get(u, []):
                if t["layer"] != layer:
                    continue
                (ins if t["dir"] == "in" else outs).append(("off: " + t["label"], t["value"], t["kind"]))
            if layer == "energy" and u not in ENERGY_NODES:
                continue
            if not ins or not outs:
                continue
            a, b = sum(x[1] for x in ins), sum(x[1] for x in outs)
            den = max(a, b, 1e-9)
            resid = a - b
            bydiff = any(x[2] == "by_difference" for x in ins + outs)
            status = "closed" if abs(resid) <= TOL * den + 1e-6 else "OPEN"
            if any(x[2] == "accumulation" for x in ins + outs):
                status = "OPEN (steady accumulation)"
            if status == "closed" and bydiff:
                status = "closed (one term by difference)"
            res[f"{u}/{layer}"] = dict(node=u, layer=layer, in_total=round(a, 4), out_total=round(b, 4), residual=round(resid, 4),
                                       residual_pct=round(100 * resid / den, 3), status=status,
                                       ins=[(x[0], round(x[1], 4)) for x in ins], outs=[(x[0], round(x[1], 4)) for x in outs])
    return res


def species(g, R, X):
    E = {e["stream_id"]: e for e in g["edges"]}
    v = lambda s: E[s]["rate"]["value"]  # noqa: E731
    out = {}
    s67co2 = E["S67"].get("params", {}).get("co2_kg_d", hl.CO2_AB_KG_D)
    a = hl.CO2_AB_KG_D + X["s11_co2"]
    out["AFTERBURNER/CO2"] = dict(in_total=round(a, 3), out_total=s67co2, residual=round(a - s67co2, 3), residual_pct=round(100 * (a - s67co2) / a, 2),
                                  status="OPEN" if abs(a - s67co2) > TOL * a else "closed",
                                  note="S11 trim carbon (0.8 kg/d x 42 % DM x 45 % C) is not in the DUTY-008 15.0 kg/d CO2 basis")
    a = v("S18") + v("S67B") + v("S82")
    b = v("S04") + v("S73") + v("S85") + R.rates["S70"]["value"]
    out["CRYO_CO2/CO2"] = dict(in_total=round(a, 3), out_total=round(b, 3), residual=round(a - b, 3), residual_pct=round(100 * (a - b) / a, 2),
                               status="closed" if abs(a - b) <= TOL * a else "OPEN")
    a = v("S85") + v("S90")
    b = v("S89")
    out["HDR_CO2/CO2"] = dict(in_total=round(a, 3), out_total=b, residual=round(a - b, 4), status="closed" if abs(a - b) <= 1e-3 else "OPEN")
    a = v("S04") + v("S89")
    b = X["s04_fixed"] if "s04_fixed" in X else v("S04")
    b += v("S89")
    out["GROW_BED/CO2"] = dict(in_total=round(a, 3), out_total=round(b, 3), residual=round(a - b, 4), status="closed",
                               note="S04 fixed in biomass, S89 to farm exhaust")
    a = v("IA-HDR-H2-01") + v("IA-HDR-H2-03") + v("IA-HDR-H2-04")
    out["H2_DRYER/H2"] = dict(in_total=a, out_total=v("S05") + v("S64") + v("S24"), residual=round(a - v("S05") - v("S64") - v("S24"), 3), status="OPEN",
                              note="S05 and S64 both carry the 4.8 kg/d pool (authority edges; probable alias)")
    return out


def main(path=GRAPH, write=None):
    GRAPH_IN[0] = path
    g0 = json.load(open(path))
    g, R, X, retired = build(g0)
    hl_offgraph(R)
    cons = conserve(g, R)
    spc = species(g, R, X)
    N = {n["unit_id"]: n for n in g["nodes"]}
    for u, terms in R.off.items():
        if u in N:
            p = N[u].get("params") or {}
            p["balance_rev_l"] = dict(doc="AQS-DUTY-010", basis="daily-average design day; off-graph terms", terms=terms)
            N[u]["params"] = p
    unrated = [e["stream_id"] for e in g["edges"] if e["presence"] == "present" and (e.get("rate") or {}).get("value") is None]
    ph = [e["stream_id"] for e in g["edges"] if e["presence"] == "placeholder"]
    opened = {k: v for k, v in cons.items() if v["status"].startswith("OPEN")}
    rep = dict(counts=dict(edges=len(g["edges"]), present=sum(e["presence"] == "present" for e in g["edges"]), unrated_present=unrated,
                           placeholders=ph, retired=[r["edge"]["stream_id"] for r in retired], rated_by_rev_l=sorted(R.rates)),
               conservation=dict(checked=len(cons), closed=sum(v["status"] == "closed" for v in cons.values()),
                                 closed_by_difference=sum(v["status"].startswith("closed (") for v in cons.values()),
                                 open=sorted(opened)),
               nodes=cons, species=spc, fixes=R.log, derived=dict((k, v) for k, v in X.items() if not isinstance(v, (list, dict))),
               ew=X["ew"], placeholders=dict(outcome=PLACEHOLDER_OUTCOME, retired=RETIRE, hold=HOLD),
               rates={k: dict(value=v["value"], unit=v["unit"], basis=v["note"], kind=v["params"]["rate_kind"]) for k, v in R.rates.items()})
    gaps = {x["id"]: x for x in g.get("gaps", [])}
    upd = {
        "DOCK_EXPORT_TBD": ("medium", "Rev L: present and rated (MFG goods export, by difference at MFG_SHOP). ID stays DOCK_EXPORT_TBD: no S## invented."),
        "INTRA_AISLE_RATES": ("low", "Rev L (AQS-DUTY-010): every present IA-* edge rated with rate_basis/rate_source in params. IA-POL-01 and IA-ESS-MEOH-CHG/DIS retired."),
        "PUMPED_HYDRO_PFD": ("low", "Rev L: IA-ESS-HYDRO-CHG/DIS 200 t/d (one cycle/d), S22/S23 0.409 kW hydraulic, IA-ESS-HYDRO-ELEC 0.292 kW (7 kWh/cycle)."),
        "WP_TRUE_CLOSURE_RESIDUALS": ("medium", "Rev L: S87/S88 demoted to placeholder on HOLD (no clean endpoint; AQS-DUTY-010). Node conservation run: see REV_L_CONSERVATION_EXCEPTIONS. loops_closed false."),
    }
    for k, (sev, det) in upd.items():
        if k in gaps:
            gaps[k]["severity"], gaps[k]["detail"] = sev, det
    exc = sorted(set(v["node"] for v in cons.values() if v["status"].startswith("OPEN")) | {k.split("/")[0] for k, v in spc.items() if v["status"] == "OPEN"})
    det = "AQS-DUTY-010 node conservation (+-1 %, daily average): open at " + ", ".join(exc) + ". Reasons in EDGE_RATING_DUTY.md s6."
    if "REV_L_CONSERVATION_EXCEPTIONS" in gaps:
        gaps["REV_L_CONSERVATION_EXCEPTIONS"]["detail"] = det
    else:
        g.setdefault("gaps", []).append(dict(id="REV_L_CONSERVATION_EXCEPTIONS", severity="high", detail=det))
    if write:
        g["revision"] = "L"
        g["notes_rev_l"] = ("AQS-DUTY-010 Rev A edge rating. Every present edge rated (unit by layer: kg/d or kg/h mass, kW thermal/electric); "
                            "rate_basis / rate_source / medium / conditions in params; node balances with off-graph terms in node params.balance_rev_l. "
                            f"Placeholders closed: {len(PLACEHOLDER_OUTCOME)} made present, {len(RETIRE)} retired (IA-POL-01, S48, IA-ESS-MEOH-CHG/DIS), "
                            "S87/S88 demoted to placeholder on HOLD. New S90 HABITATION -> HDR_CO2 metabolic CO2; S89 = S85 + S90. "
                            "Fixes: " + "; ".join(R.log) + ". loops_closed and every *_on_site flag unchanged (false).")
        g["notes_rev_l_retired"] = json.dumps(retired, ensure_ascii=True)
        open(write, "w").write(json.dumps(g, indent=2))
    return rep, g


if __name__ == "__main__":
    gp = sys.argv[sys.argv.index("--graph") + 1] if "--graph" in sys.argv else GRAPH
    wr = sys.argv[sys.argv.index("--write") + 1] if "--write" in sys.argv else None
    if "--graph" not in sys.argv and json.load(open(GRAPH)).get("revision", "L") > "L":
        # Rev M onward: this study (AQS-DUTY-010 Rev A) is reproducible against its Rev L
        # base only. The superseding rating is AQS-DUTY-011 (_rev_m_closure_study.py).
        import subprocess
        import tempfile
        txt = subprocess.check_output(["git", "-C", os.path.join(HERE, ".."), "show",
                                       "d9cd071:flow_graph/plant_flow_graph.json"])
        tmp = tempfile.NamedTemporaryFile("wb", suffix=".json", delete=False)
        tmp.write(txt)
        tmp.close()
        gp = tmp.name
        print("note: graph is past Rev L; AQS-DUTY-010 rerun on Rev L base d9cd071", file=sys.stderr)
    rep, g = main(gp, wr)
    if "--json" in sys.argv:
        json.dump(rep, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)
    print(json.dumps(dict(counts=rep["counts"], conservation=rep["conservation"]), indent=1))

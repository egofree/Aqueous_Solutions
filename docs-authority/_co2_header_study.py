"""AQS-DUTY-009 Rev A. HDR_CO2 consumer study (graph Rev K).

Reads the Rev J graph rates, tests each candidate CO2 sink, and sizes the chosen branch S89 HDR_CO2 -> GROW_BED.
Inputs from the graph are read, not typed. A_* are study decisions, each stated in CO2_HEADER_DUTY.md.
Run: python3 _co2_header_study.py [--json out.json] [--graph path]
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GRAPH = os.path.join(HERE, "..", "flow_graph", "plant_flow_graph.json")

R = 8.314
M_CO2 = 44.01e-3
M_H2 = 2.016e-3
M_MEOH = 32.04e-3
A_PPM_AMB = 420.0          # ambient CO2, ppm (2026 global mean ~ 425; 420 conservative for dilution)
A_PPM_SET = 1000.0         # farm enrichment setpoint, ppm (common greenhouse 800-1200; keeps occupied space <= 1000)
A_PPM_CROP_MAX = 1500.0    # above this, stomatal / leaf-injury risk in leafy crops; never a setpoint
A_T_FARM_C = 24.0
A_PHOTO_H = 16.0           # photoperiod, h/d (LED canopy); dose only in light
A_FARM_LWH = (12.0, 18.0, 4.5)  # m, FARM envelope (WAFER/FARM block on the placed copy)
A_CANOPY_M2 = 28.0         # GROW_BED canopy (S14 yield basis, AQS-AUD-001 s12)
A_CREW_IN_FARM = 2         # persons for the outdoor-air minimum
A_OA_PERSON_L_S = 2.5      # ASHRAE 62.1-type Rp (L/s per person)
A_OA_AREA_L_S_M2 = 0.3     # Ra (L/s per m2); plant-growth area, conservative
A_HDR_P_BAR_A = 3.0        # HDR_CO2 operating pressure (2 bar g), regulated off the CRYO_CO2 vaporizer
A_HDR_T_C = 20.0
A_Z_CO2 = 0.985            # compressibility of CO2 at 3 bar a, 20 C
A_BRANCH_DN = 15
A_BRANCH_ID_MM = 15.8      # DN15 Sch40 bore (same table as AQS-DUTY-008)
A_FARM_DUCT_MM = (500, 300)  # LIFE_MEP FARM AHU duct
A_DT_OA_K = 10.0           # outdoor to farm temperature difference for the load estimate
A_DARK_H = 24.0 - A_PHOTO_H
A_LIQ_RHO = 1030.0         # liquid CO2 at about -20 C / 20 bar, kg/m3 (CRYO_CO2 inventory)
A_REMIN_CA_MG_L = 25.0     # REMIN issued params (only used to show the lime + CO2 route is negligible)


def rate(g, sid):
    for e in g["edges"]:
        if e["stream_id"] == sid:
            return (e.get("rate") or {}).get("value")
    raise KeyError(sid)


def node(g, uid):
    for n in g["nodes"]:
        if n["unit_id"] == uid:
            return n
    raise KeyError(uid)


def main(path=GRAPH):
    g = json.load(open(path))
    s85 = rate(g, "S85")
    s04 = rate(g, "S04")
    h2_pool = rate(g, "S05")
    s73 = rate(g, "S73")
    s74 = rate(g, "S74")
    s49 = rate(g, "S49")
    s45 = rate(g, "S45")
    out = {"inputs": dict(S85=s85, S04=s04, S05_H2_pool=h2_pool, S73=s73, S74=s74, S49=s49, S45=s45)}

    # --- candidate 1: MEOH_SYNTH (CO2 + 3 H2 -> CH3OH + H2O)
    h2_per_co2 = 3 * M_H2 / M_CO2
    h2_need = s85 * h2_per_co2
    meoh = s85 * M_MEOH / M_CO2
    h2_free_fc_on = h2_pool - s49 - s74        # FC running: S49 takes the full pool
    h2_free_gen_on = h2_pool - s45 - s74       # GEN running
    out["meoh"] = dict(h2_kg_per_kg_co2=round(h2_per_co2, 4), h2_needed_kg_d=round(h2_need, 3), meoh_kg_d=round(meoh, 2),
                       h2_free_fc_case_kg_d=round(h2_free_fc_on, 3), h2_free_gen_case_kg_d=round(h2_free_gen_on, 3),
                       feasible=h2_free_fc_on >= h2_need and h2_free_gen_on >= h2_need,
                       note="MeOH is burned in MEOH_FC and returns its carbon on S82: a carrier loop, not a sink.")

    # --- candidate 2: REMIN (lime + CO2 bicarbonate route; issued design is hydroxide only)
    rem = node(g, "REMIN")["params"]
    ca_mmol = A_REMIN_CA_MG_L / 40.08
    co2_remin = rem["drink_L_d"] * 2 * ca_mmol * 44.01 / 1e6
    out["remin"] = dict(co2_kg_d=round(co2_remin, 5), share=round(co2_remin / s85, 6),
                        note="2 CO2 per Ca as bicarbonate; negligible and REMIN is issued as hydroxide dose.")

    # --- candidate 3: GROW_BED enrichment via FARM AHU
    T = A_T_FARM_C + 273.15
    rho_co2_room = 101325 * M_CO2 / (R * T)                       # kg/m3 pure CO2 at farm conditions
    dC = (A_PPM_SET - A_PPM_AMB) * 1e-6 * rho_co2_room            # kg/m3 excess over ambient
    vol = A_FARM_LWH[0] * A_FARM_LWH[1] * A_FARM_LWH[2]
    area = A_FARM_LWH[0] * A_FARM_LWH[1]
    oa_min = (A_CREW_IN_FARM * A_OA_PERSON_L_S + A_OA_AREA_L_S_M2 * area) * 3.6   # m3/h
    uptake = s04                                                  # net fixation, Rev J S04 basis
    uptake_umol = uptake / (A_PHOTO_H * 3600) / A_CANOPY_M2 / M_CO2 * 1e6
    loss_min = oa_min * A_PHOTO_H * dC                            # kg/d lost at minimum OA, light hours
    dose_min = uptake + loss_min
    # all of S85 + S04 is dosed in the photoperiod; S04 is fixed, S85 leaves with exhaust
    exhaust = s85
    oa_req = exhaust / (A_PHOTO_H * dC)
    ppm_at_min_oa = A_PPM_AMB + exhaust / (A_PHOTO_H * oa_min) / rho_co2_room * 1e6
    duct_v = oa_req / 3600 / (A_FARM_DUCT_MM[0] * A_FARM_DUCT_MM[1] * 1e-6)
    load_kw = (oa_req - oa_min) * 1.2 / 3600 * 1.006 * A_DT_OA_K
    out["farm"] = dict(volume_m3=vol, floor_m2=area, rho_co2_kg_m3=round(rho_co2_room, 4), dC_g_m3=round(dC * 1000, 4),
                       oa_min_m3_h=round(oa_min, 1), oa_min_ach=round(oa_min / vol, 3),
                       uptake_kg_d=uptake, canopy_uptake_umol_m2_s=round(uptake_umol, 1),
                       loss_at_min_oa_kg_d=round(loss_min, 3), dose_to_hold_setpoint_at_min_oa_kg_d=round(dose_min, 3),
                       ppm_if_all_s85_at_min_oa=round(ppm_at_min_oa, 0), crop_max_ppm=A_PPM_CROP_MAX,
                       oa_required_m3_h=round(oa_req, 1), oa_required_ach=round(oa_req / vol, 3),
                       oa_ok=oa_req >= oa_min, duct_velocity_all_oa_m_s=round(duct_v, 2),
                       extra_oa_sensible_kw_at_10K=round(load_kw, 2),
                       fate=dict(fixed_in_biomass_S04_kg_d=s04, leaves_with_farm_exhaust_kg_d=round(exhaust, 3),
                                 note="Not sequestration. The S85 carbon is used once for growth enrichment and then vented with farm exhaust air."))

    # --- branch line S89
    rho = A_HDR_P_BAR_A * 1e5 * M_CO2 / (A_Z_CO2 * R * (A_HDR_T_C + 273.15))
    m_avg = s85 / 24.0
    m_peak = s85 / A_PHOTO_H
    q_peak = m_peak / rho
    a = math.pi / 4 * (A_BRANCH_ID_MM / 1000) ** 2
    v_peak = q_peak / 3600 / a
    buffer = s85 * A_DARK_H / 24.0
    out["branch"] = dict(stream_id="S89", from_unit_id="HDR_CO2", to_unit_id="GROW_BED", rate_kg_d=s85,
                         P_bar_a=A_HDR_P_BAR_A, T_C=A_HDR_T_C, rho_kg_m3=round(rho, 3), m_avg_kg_h=round(m_avg, 3),
                         m_peak_kg_h=round(m_peak, 3), q_peak_m3_h=round(q_peak, 4), line_DN=A_BRANCH_DN,
                         line_id_mm=A_BRANCH_ID_MM, velocity_peak_m_s=round(v_peak, 3), material="316L",
                         dark_buffer_kg=round(buffer, 2), dark_buffer_liquid_L=round(buffer / A_LIQ_RHO * 1000, 2))
    out["balance"] = dict(HDR_CO2_in_S85=s85, HDR_CO2_out_S89=s85, residual=round(s85 - s85, 6),
                          GROW_BED_in=round(s04 + s85, 3), GROW_BED_fixed=s04, GROW_BED_exhaust=round(exhaust, 3))
    out["decision"] = "GROW_BED via FARM AHU CO2 dose (S89). MEOH_SYNTH rejected (H2-limited, carrier loop). REMIN negligible."
    return out


if __name__ == "__main__":
    gp = sys.argv[sys.argv.index("--graph") + 1] if "--graph" in sys.argv else GRAPH
    r = main(gp)
    if "--json" in sys.argv:
        json.dump(r, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)
    print(json.dumps(r, indent=1))

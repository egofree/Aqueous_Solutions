#!/usr/bin/env python3
# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Build plant_flow_graph.json sole authority seed from CAD + prior graph.

WP-Ap1: preserves ``mvs`` block and node continuous_kw/modules/params/enabled
from an existing plant_flow_graph.json when present. Falls back once to the
generated projection candidate_mvs.json only if mvs is missing (bootstrap).
After rebuild, run export_candidate_mvs.py to refresh the projection.

Does NOT invent routes, rates, or nameplates. Placeholder study stubs get
rate=null (lock present_plus_placeholders). Gaps stay flagged.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HUB = ROOT.parent
CAD = HUB / "cad"
CAND = HUB / "design_tool" / "aqs_design_tool" / "data" / "candidate_mvs.json"
OUT = ROOT / "plant_flow_graph.json"


def _load_prior_mvs_and_enrichment():
    """Preserve WP-Ap1 mvs + node enrichment across topology rebuilds."""
    mvs = None
    enrich = {}
    if OUT.is_file():
        prior = json.loads(OUT.read_text(encoding="utf-8"))
        if isinstance(prior.get("mvs"), dict):
            mvs = prior["mvs"]
        for n in prior.get("nodes") or []:
            enrich[n["unit_id"]] = {
                k: n.get(k)
                for k in ("enabled", "continuous_kw", "modules", "params")
                if k in n
            }
    if mvs is None and CAND.is_file():
        # Bootstrap only — not a competing write authority after WP-Ap1
        c = json.loads(CAND.read_text(encoding="utf-8"))
        mvs = {
            "schema_version": c.get("schema_version", "aqs-mvs-0.3"),
            "doc_id": c.get("doc_id", "AQS-MVS-001"),
            "revision": c.get("revision", "E-candidate"),
            "licence": c.get("licence", "CERN-OHL-S-2.0"),
            "scale_m": c.get("scale_m", 1.0),
            "status": c.get("status", "candidate"),
            "mvs_criteria": c.get("mvs_criteria") or {},
            "site": c.get("site") or {},
            "sectors": c.get("sectors") or [],
            "electrical": c.get("electrical") or {},
            "scale_rules": c.get("scale_rules") or {},
            "ui": c.get("ui") or {},
            "notes": c.get("notes"),
            "write_path": (
                "plant_flow_graph.json#mvs + nodes/edges; "
                "candidate_mvs.json is generated projection only"
            ),
        }
        for u in c.get("units") or []:
            enrich.setdefault(u["unit_id"], {})
            enrich[u["unit_id"]].update(
                {
                    "enabled": u.get("enabled", True),
                    "continuous_kw": u.get("continuous_kw"),
                    "modules": u.get("modules") or [],
                    "params": u.get("params") or {},
                }
            )
    return mvs, enrich


# Study stubs → placeholder nodes; their exclusive edges get null rates.
PLACEHOLDER_UNITS = {
    "VCD_TRAIN",
    "REMIN",
    "GEO_ORC",
    "LITHO_STUB",
    "BLOW_MOLD",
    "ELECTRODE_COAT",
    "SOLAR_PV_CELL",  # study_stub class; architecture_promoted but not Present
}

# Units known missing dedicated PFD (audit §2) — present but diagram_gap.
DIAGRAM_GAP_UNITS = {
    "HYDRO_SET": "Dedicated hydro_dock_pfd.png (graph-bridged); campus water_cycle still shows inventory narrative",
    "NORTH_DOCK": "Dedicated hydro_dock_pfd.png (graph-bridged); campus/ground_floor still show footprint",
    "BOUNDARY_EXPORT": "DOCK export boundary — no inter-block S## for goods freight (use DOCK_EXPORT_TBD)",
}

# Map STREAM_REGISTER From/To prose fragments → unit_id (best-effort; no new routes).
# Prefer candidate_mvs endpoints when stream already seeded there.
NAME_TO_UNIT = {
    "BMED / UPW POLISH": "BMED_UPW_POLISH",
    "BMED_UPW_POLISH": "BMED_UPW_POLISH",
    "UPW POLISH": "BMED_UPW_POLISH",
    "FARM": "GROW_BED",
    "GROW BED": "GROW_BED",
    "GROW_BED": "GROW_BED",
    "WAFER FAB": "WAFER_FAB",
    "WAFER_FAB": "WAFER_FAB",
    "HABITATION": "HABITATION",
    "HAB": "HABITATION",
    "CRYO O2": "CRYO_O2",
    "CRYO_O2": "CRYO_O2",
    "CRYO N2": "CRYO_N2",
    "CRYO_N2": "CRYO_N2",
    "CRYO CO2": "CRYO_CO2",
    "CRYO_CO2": "CRYO_CO2",
    "CRYO H2": "CRYO_H2",
    "CRYO_H2": "CRYO_H2",
    "H2_DRYER": "H2_DRYER",
    "Q4 / HVAC": "Q4_BUS",
    "Q4": "Q4_BUS",
    "NUTRIENT DOSE": "NUTRIENT_DOSE",
    "NUTRIENT_DOSE": "NUTRIENT_DOSE",
    "METALS / ELEMENTS + SILICATE": "LEACH_CSTR_1",
    "FAB PREP": "WAFER_FAB",
    "MFG SHOP": "MFG_SHOP",
    "MFG_SHOP": "MFG_SHOP",
    "HCl PRODUCT / NaOH PRODUCT": "BMED_UPW_POLISH",
    "WET BENCH": "WET_BENCH",
    "WET_BENCH": "WET_BENCH",
    "REGEN LEACH": "LEACH_CSTR_1",
    "LEACH CSTR 1": "LEACH_CSTR_1",
    "LEACH_CSTR_1": "LEACH_CSTR_1",
    "CSTR 1": "LEACH_CSTR_1",
    "GALLEY": "HABITATION",
    "HOPPER": "HOPPER",
    "OIL LINE": "AFTERBURNER",
    "HAB WASTE": "HABITATION",
    "SALT FEED": "SALT_FEED",
    "FARM SUMP + HVAC": "GROW_BED",
    "FARM SUMP": "GROW_BED",
    "SOL_ARK / ZNBR2 / RECTIFIER": "SOL_ARK_60K",
    "SOL_ARK": "SOL_ARK_60K",
    "SOL_ARK_60K": "SOL_ARK_60K",
    "AFTERBURNER / air": "AFTERBURNER",
    "AFTERBURNER": "AFTERBURNER",
    "CRYO": "CRYO_CO2",
    "BAGHOUSE fines": "BAGHOUSE",
    "BAGHOUSE": "BAGHOUSE",
    "LED CANOPY, FAB TOOL, HAB AIR": "LOAD_AGG",
    "ROOF TANK": "ROOF_TANK",
    "ROOF_TANK": "ROOF_TANK",
    "HAB WATER": "HABITATION",
    "CATCH TANK": "CATCH_TANK",
    "CATCH_TANK": "CATCH_TANK",
    "HYDRO SET": "HYDRO_SET",
    "HYDRO_SET": "HYDRO_SET",
    "VCD_COND": "VCD_TRAIN",
    "VCD_EVAP": "VCD_TRAIN",
    "VCD_FEED": "VCD_TRAIN",
    "VCD_TRAIN": "VCD_TRAIN",
    "REMIN / POTABLE_TANK": "REMIN",
    "REMIN": "REMIN",
    "FAB_UPW_TANK": "FAB_UPW_TANK",
    "GREY_TREAT": "GREY_TREAT",
    "BLACK_DIGEST": "BLACK_DIGEST",
    "WS_HF_ED": "WS_HF_ED",
    "WS_PEROX": "WS_PEROX",
    "WS_AMMONIA": "WS_AMMONIA",
    "WS_NITRIC / WS_PHOS": "WS_NITRIC",
    "WS_KOH": "WS_KOH",
    "WS_DOPE / CRU polish": "WS_DOPE",
    "WS_SLURRY": "WS_SLURRY",
    "WS_SOLV": "WS_SOLV",
    "LAP_CMP / FAB_PREP": "WAFER_FAB",
    "LAP_CMP": "WAFER_FAB",
    "FAB_TOOL dopant cabinets": "WAFER_FAB",
    "FAB_TOOL litho / strip": "LITHO_STUB",
    "FAB_TOOL": "WAFER_FAB",
    "OVERFLOW_SPILL_ROOF / ROOF TANK surplus": "ROOF_TANK",
    "TERRACE irrig headers": "TERRACE_IRRIG",
    "TERRACE_IRRIG": "TERRACE_IRRIG",
    "TERRACE underdrain / apron (clean)": "TERRACE_IRRIG",
    "Enclosed terrace / GH fertigated drain": "TERRACE_IRRIG",
    "GEO_GHEX": "GEO_GHEX",
    "GEO_HP": "GEO_HP",
    "GEO_ORC (stub)": "GEO_ORC",
    "GEO_ORC": "GEO_ORC",
    "BACKUP_GEN": "BACKUP_GEN",
    "BACKUP_GEN exhaust": "BACKUP_GEN",
    "FUEL_CELL": "FUEL_CELL",
    "FUEL_CELL / FC_DCDC": "FUEL_CELL",
    "FC_HX_Q4": "FUEL_CELL",
    "CRYO_HX_Q4": "CRYO_HX_Q4",
    "CRYO_DED_COOL (loop)": "CRYO_DED_COOL",
    "CRYO_DED_COOL": "CRYO_DED_COOL",
    "CRYO_AHU / CRYO_AHU_COND residual": "CRYO_AHU",
    "CRYO_AHU": "CRYO_AHU",
    "CRYO_AHU_COND": "CRYO_AHU",
    "PROD_METALS / MET_MELT": "MET_MELT",
    "MET_MELT": "MET_MELT",
    "WIRE_DRAW": "WIRE_DRAW",
    "COLD_MILL": "COLD_MILL",
    "GAS_ATOMIZER": "GAS_ATOMIZER",
    "MET_WIRE_BIN / ELECTRODE_FAB / MFG_CRIB": "MFG_SHOP",
    "MET_SHEET_BIN / MFG_CRIB": "MFG_SHOP",
    "MET_POWDER_CRIB / FAB / RepRap": "MFG_SHOP",
    "Forming swarf / trim": "MFG_SHOP",
    "MET_AHU": "MET_AHU",
    "MET_SCRUB / baghouse (S71)": "MET_SCRUB",
    "MET_SCRUB / baghouse": "MET_SCRUB",
    "MET_SCRUB": "MET_SCRUB",
    "MET_HX_Q4": "MET_HX_Q4",
    "ALK_SCRUBBER residual": "ALK_SCRUBBER",
    "ALK_SCRUBBER": "ALK_SCRUBBER",
    "ACID_POLISH_SCRUB": "ACID_POLISH_SCRUB",
    "ACID_POLISH / ALK blowdown": "ACID_POLISH_SCRUB",
    "CRU": "CRU",
    "FLUE_CAP / CRYO": "CRYO_CO2",
    "FLUE_CAP / CRYO_AHU_COND": "CRYO_AHU",
    "ZNBR2_BR2_REGEN": "ZNBR2",
    "ZnBr2 positive tank": "ZNBR2",
    "ZNBR2": "ZNBR2",
    "COLD_BOX / CRYO condensate return": "CRYO_H2",
    "MET_SCRUB / baghouse": "MET_SCRUB",
    "CSTR 1 / OIL / HDR_ORG": "LEACH_CSTR_1",
    "MEOH_DAC_OR_CO2 / MEOH_SYNTH / MEOH_IEM_CELL": "MEOH_SYNTH",
    "MEOH_SYNTH / MEOH_IEM_CELL": "MEOH_SYNTH",
    "MEOH_SYNTH": "MEOH_SYNTH",
    "MEOH_COND / MEOH_DIST": "MEOH_TANK",
    "MEOH_TANK / MEOH_DAY_TANK": "MEOH_TANK",
    "MEOH_TANK": "MEOH_TANK",
    "MEOH_FC": "MEOH_FC",
    "MEOH_FC / MEOH_DCDC": "MEOH_FC",
    "MEOH_FERM_STILL": "MEOH_FERM",
    "MEOH_FERM_DIG": "MEOH_FERM",
    "MEOH_FERM": "MEOH_FERM",
    "Farm/hab organics (S12/S30 class)": "HABITATION",
    "MEOH_HX_Q4": "MEOH_FC",
    "MEOH_FC / MEOH_COND": "MEOH_FC",
    "MEOH_FC / MEOH_VENT_KO": "MEOH_FC",
    "CRYO_CO2 / FARM (Claimed)": "CRYO_CO2",
    "CRYO_CO2 / S67 / air": "CRYO_CO2",
    "Sol-Ark AC couple": "SOL_ARK_60K",
    "Sol-Ark BATT DC": "SOL_ARK_60K",
    "Sol-Ark GEN port": "SOL_ARK_60K",
    "all blocks": "LOAD_AGG",
    "condensate / scrubber": "GREY_TREAT",
    "condensate / S13 class": "GREY_TREAT",
    "safe vent contingency": "BOUNDARY_EXPORT",
    "roof contingency (SHAFT_H2)": "BOUNDARY_EXPORT",
    "DRAIN_SEC": "CATCH_TANK",
    "CATCH TANK / DRAIN_SEC": "CATCH_TANK",
    "HAB taps (HAB_WATER)": "HABITATION",
    "WET_BENCH / solar texture stub": "WET_BENCH",
    "GREY treat / VCD_FEED / SALT": "GREY_TREAT",
    "NUTRIENT DOSE / SALT FEED": "NUTRIENT_DOSE",
    "UPW POLISH / HAB_ED_POLISH": "BMED_UPW_POLISH",
    "UPW POLISH / SALT FEED / VCD_FEED": "VCD_TRAIN",
    "REGEN LEACH / SALT FEED": "LEACH_CSTR_1",
    "REGEN LEACH / OIL / HDR_ORG": "LEACH_CSTR_1",
    "SALT FEED / NUTRIENT DOSE / HOPPER": "NUTRIENT_DOSE",
    "HOPPER or OIL LINE": "HOPPER",
    "FARM, WAFER FAB, HABITATION": "HDR_UPW",
    "WAFER FAB, FARM": "WAFER_FAB",
    "FARM, HABITATION": "GROW_BED",
    "HABITATION and FARM": "GROW_BED",
    "Q4 / FARM / HAB": "Q4_BUS",
    "HDR_O2": "HDR_O2",
    "HDR_UPW": "HDR_UPW",
    "RECTIFIER": "RECTIFIER",
    "PV_ARRAY": "PV_ARRAY",
    "EW_1": "EW_1",
    "GLASS_DIGEST": "GLASS_DIGEST",
    "NORTH_DOCK": "NORTH_DOCK",
    "BOUNDARY_EXPORT": "BOUNDARY_EXPORT",
    "HAB_ED_POLISH": "BMED_UPW_POLISH",
    "POTABLE_TANK": "REMIN",
}

# Extra structural units needed as endpoints (not inventing process — register names).
EXTRA_UNITS = [
    ("CRYO_N2", "CRYO", "present", "cold_box", None, "Register S03 endpoint; not yet in candidate_mvs units[]"),
    ("Q4_BUS", "HAB", "present", "header", None, "Thermal Q4 collector bus (S06/S44/S53/S54/S63/S80)"),
    ("HOPPER", "OIL", "present", "hopper", None, "Organic/scrap hopper (S11/S16/S61)"),
    ("SALT_FEED", "WET", "present", "feed", None, "Salt feed (S12/S13/S28/S29/S30)"),
    ("BAGHOUSE", "GAS", "present", "baghouse", None, "Dust baghouse (S19)"),
    ("LOAD_AGG", "ELEC", "present", "load_agg", "S17/S20 undrawn aggregation", "Electrical load aggregation for S17/S20"),
    ("FAB_UPW_TANK", "FAB", "present", "tank", None, "Fab UPW tank (S27)"),
    ("GREY_TREAT", "WTR", "present", "treat", None, "Grey treatment (S29)"),
    ("BLACK_DIGEST", "WTR", "present", "digest", None, "Black digest (S30)"),
    ("WS_HF_ED", "FAB", "present", "reagent", None, "Fab reagent fork (S31)"),
    ("WS_PEROX", "FAB", "present", "reagent", None, "Fab reagent fork (S32)"),
    ("WS_AMMONIA", "FAB", "present", "reagent", None, "Fab reagent fork (S33)"),
    ("WS_NITRIC", "FAB", "present", "reagent", None, "Fab reagent fork (S34)"),
    ("WS_KOH", "FAB", "present", "reagent", None, "Fab reagent fork (S35)"),
    ("WS_DOPE", "FAB", "present", "reagent", None, "Fab reagent fork (S36)"),
    ("WS_SLURRY", "FAB", "present", "reagent", None, "Fab reagent fork (S37)"),
    ("WS_SOLV", "FAB", "present", "reagent", None, "Fab reagent fork (S38) — litho path also via LITHO_STUB"),
    ("GEO_GHEX", "GEO", "present", "ghex", None, "Geothermal GHEX (S43)"),
    ("CRYO_HX_Q4", "CRYO", "present", "hx", None, "CRYO warm reject HX (S54)"),
    ("CRYO_DED_COOL", "CRYO", "present", "cool", None, "Dedicated cryo cool loop (S55)"),
    ("CRYO_AHU", "CRYO", "present", "ahu", None, "CRYO AHU (S56/S70)"),
    ("MET_MELT", "MFG", "present", "melt", None, "Metal melt (S57)"),
    ("WIRE_DRAW", "MFG", "present", "forming", None, "Wire draw (S58)"),
    ("COLD_MILL", "MFG", "present", "forming", None, "Cold mill (S59)"),
    ("GAS_ATOMIZER", "MFG", "present", "forming", None, "Gas atomizer (S60)"),
    ("MET_AHU", "MFG", "present", "ahu", None, "Metal aisle AHU (S62/S71)"),
    ("MET_SCRUB", "MFG", "present", "scrubber", None, "MET scrub/baghouse (S71/S72)"),
    ("MET_HX_Q4", "MFG", "present", "hx", None, "MET HX → Q4 (S63)"),
    ("ACID_POLISH_SCRUB", "GAS", "present", "scrubber", None, "Acid polish scrub (S65)"),
    ("CRU", "WET", "present", "cru", None, "Chlorate finish / CRU (S66)"),
    ("MEOH_FERM", "MEOH", "present", "ferment", None, "MeOH ferment (S77/S78)"),
    ("HDR_O2", "GAS", "present", "header", None, "O2 header (S15/S02)"),
    ("GLASS_RINSE", "GLASS", "placeholder", "intra", "glass_ceramic_pfd unlabeled", "Intra-aisle glass rinse (IA-*)"),
    ("GLASS_BURNOUT", "GLASS", "placeholder", "intra", "glass_ceramic_pfd unlabeled", "Intra-aisle glass burnout (IA-*)"),
    ("GLASS_MILL", "GLASS", "placeholder", "intra", "glass_ceramic_pfd unlabeled", "Intra-aisle glass mill (IA-*)"),
    ("EW_2", "WET", "present", "ew_cell", None, "EW cascade stage (intra)"),
    ("EW_9", "WET", "present", "ew_cell", None, "EW cascade last stage proxy (intra)"),
    ("FLOAT_SINK", "WET", "present", "separator", None, "Float/sink (intra)"),
    ("C29_RECYCLE", "WET", "placeholder", "recycle", "intra-aisle ID was TBD", "C29-class recycle node"),
    ("BMED_ACID", "WET", "present", "bmed", None, "BMED acid loop node"),
    ("BMED_BASE", "WET", "present", "bmed", None, "BMED base loop node"),
    ("POLISH_BANK", "WET", "present", "polish", None, "Polish bank series"),
    ("OIL_DRYER", "OIL", "present", "dryer", None, "Oil dryer (intra)"),
    ("OIL_PYRO", "OIL", "present", "pyro", None, "Oil pyro (intra)"),
    ("OIL_FRAC", "OIL", "present", "frac", None, "Oil frac (intra)"),
    ("CONTINUOUS_RECYCLE", "WET", "placeholder", "recycle", "continuous_recycling_pfd unlabeled", "Continuous recycle heat ladder node"),
]

# Intra-aisle edges called out in audit §3.3 / §7.2 — stable IA-* IDs, placeholder rates.
INTRA_AISLE = [
    # EW cascade
    ("IA-EW-01", "EW_1", "EW_2", "L", "EW stage overflow/advance", ["mass"], "ew_cascade undrawn S##"),
    ("IA-EW-02", "EW_2", "EW_9", "L", "EW cascade mid→last (proxy; stages 3–8 not exploded)", ["mass"], "ew_cascade undrawn S##"),
    ("IA-EW-03", "EW_9", "POLISH_BANK", "L", "EW → polish / precip", ["mass"], "ew_cascade undrawn S##"),
    ("IA-EW-04", "LEACH_CSTR_1", "EW_1", "L", "CSTR → EW-1 feed", ["mass"], "ew_cascade undrawn S##"),
    # Float / C29
    ("IA-WET-FLOAT-01", "FLOAT_SINK", "LEACH_CSTR_1", "L", "Float/sink liquor return", ["mass"], "STR scope-out; ID was TBD"),
    ("IA-WET-C29-01", "C29_RECYCLE", "LEACH_CSTR_1", "L", "C29-class recycle", ["mass"], "STR scope-out; ID was TBD"),
    # Continuous recycle
    ("IA-REC-01", "CONTINUOUS_RECYCLE", "LEACH_CSTR_1", "L", "Continuous recycle liquor", ["mass"], "continuous_recycling_pfd"),
    ("IA-REC-Q3", "CONTINUOUS_RECYCLE", "Q4_BUS", "E", "Heat ladder Q3 residual (ghost to Q4 bus for EFD-thermal)", ["thermal"], "heat ladder unlabeled"),
    # BMED
    ("IA-BMED-01", "BMED_ACID", "BMED_UPW_POLISH", "L", "BMED acid product internal", ["mass"], "bmed_regen unlabeled"),
    ("IA-BMED-02", "BMED_BASE", "BMED_UPW_POLISH", "L", "BMED base product internal", ["mass"], "bmed_regen unlabeled"),
    ("IA-BMED-03", "CRU", "BMED_ACID", "L", "CRU → BMED acid regen loop", ["mass"], "bmed_regen unlabeled"),
    ("IA-BMED-04", "CRU", "BMED_BASE", "L", "CRU → BMED base regen loop", ["mass"], "bmed_regen unlabeled"),
    # Polish
    ("IA-POL-01", "POLISH_BANK", "BMED_UPW_POLISH", "L", "Polish bank → UPW polish", ["mass"], "polish_bank unlabeled"),
    ("IA-POL-02", "POLISH_BANK", "POLISH_BANK", "L", "Polish series internals (self-loop stub)", ["mass"], "polish_bank unlabeled"),
    # Glass
    ("IA-GLASS-01", "GLASS_RINSE", "GLASS_BURNOUT", "L", "Glass rinse → burnout", ["mass"], "glass_ceramic_pfd no S##"),
    ("IA-GLASS-02", "GLASS_BURNOUT", "GLASS_MILL", "S", "Glass burnout → mill", ["mass"], "glass_ceramic_pfd no S##"),
    ("IA-GLASS-03", "GLASS_MILL", "GLASS_DIGEST", "S", "Glass mill → digest", ["mass"], "glass_ceramic_pfd no S##"),
    ("IA-GLASS-Q2", "GLASS_BURNOUT", "Q4_BUS", "E", "Q2 burnout heat (study path; not rate)", ["thermal"], "glass heat unlabeled"),
    # Oil internals
    ("IA-OIL-01", "OIL_DRYER", "OIL_PYRO", "S", "Dryer → pyro", ["mass"], "oil_line internals"),
    ("IA-OIL-02", "OIL_PYRO", "OIL_FRAC", "L", "Pyro → frac", ["mass"], "oil_line internals"),
    ("IA-OIL-03", "OIL_FRAC", "AFTERBURNER", "G", "Frac cut / vapor → afterburner", ["mass"], "oil_line internals"),
    ("IA-OIL-Q1", "AFTERBURNER", "Q4_BUS", "E", "Q1 afterburner heat (not into hab air)", ["thermal"], "Q1≠Q4 rule"),
]

# ESS charge/discharge typed edges (layer ess) — architecture from ESS/SLD; rates null if unknown.
ESS_EDGES = [
    ("IA-ESS-ZNBR2-CHG", "SOL_ARK_60K", "ZNBR2", "E", "ZnBr2 charge (PV/RECT surplus)", ["elec", "ess"], True),
    ("IA-ESS-ZNBR2-DIS", "ZNBR2", "SOL_ARK_60K", "E", "ZnBr2 discharge to bus", ["elec", "ess"], True),
    ("IA-ESS-MEOH-CHG", "MEOH_SYNTH", "MEOH_TANK", "L", "MeOH synth inventory = charge-analogue", ["mass", "ess"], True),
    ("IA-ESS-MEOH-DIS", "MEOH_FC", "SOL_ARK_60K", "E", "MeOH FC discharge (peers S79)", ["elec", "ess"], False),  # S79 is Present electric
    ("IA-ESS-HYDRO-CHG", "CATCH_TANK", "ROOF_TANK", "L", "Pumped hydro charge (pump up; peers S23)", ["mass", "ess"], False),
    ("IA-ESS-HYDRO-DIS", "ROOF_TANK", "CATCH_TANK", "L", "Pumped hydro discharge (penstock; peers S22)", ["mass", "ess"], False),
    ("IA-ESS-HYDRO-ELEC", "HYDRO_SET", "SOL_ARK_60K", "E", "Hydro turbine-pump electrical (MISSING on SLD)", ["elec", "ess"], True),
]


def phase_layers(phase: str, stream_id: str) -> list[str]:
    layers = []
    p = phase.upper()
    if "E" in p and stream_id in {
        "S06", "S44", "S53", "S54", "S63", "S80",
    }:
        layers.append("thermal")
    if "E" in p and stream_id in {
        "S17", "S20", "S47", "S48", "S51", "S79",
    }:
        layers.append("elec")
    if stream_id in {"S22", "S23", "S69", "S76", "S79"}:
        layers.append("ess")
    if not layers:
        if p == "E":
            # default electric heat vs power by ID already handled; leftover E → thermal+elec ambiguity
            layers.append("elec")
        else:
            layers.append("mass")
    # S43 geothermal loop is thermal+mass
    if stream_id == "S43":
        layers = ["mass", "thermal"]
    if stream_id == "S55":
        layers = ["mass", "thermal"]
    return layers


def parse_stream_register() -> list[dict]:
    text = (CAD / "STREAM_REGISTER.md").read_text()
    rows = []
    for line in text.splitlines():
        if not line.startswith("| S"):
            continue
        parts = [c.strip() for c in line.strip("|").split("|")]
        if len(parts) < 6:
            continue
        sid, frm, to, ph, carries, header = parts[:6]
        forbidden = parts[6] if len(parts) > 6 else ""
        if not re.match(r"^S\d{2}$", sid):
            continue
        rows.append(
            {
                "stream_id": sid,
                "from_raw": frm,
                "to_raw": to,
                "phase": ph,
                "carries": carries,
                "header": header,
                "forbidden": forbidden,
            }
        )
    return rows


def parse_mass_flow_claims() -> dict[str, str]:
    text = (CAD / "MASS_FLOW.md").read_text()
    claims = {}
    for line in text.splitlines():
        if not line.startswith("| S"):
            continue
        parts = [c.strip() for c in line.strip("|").split("|")]
        if len(parts) < 3:
            continue
        sid = parts[0]
        if re.match(r"^S\d{2}$", sid):
            claims[sid] = parts[2]
    # MeOH section may not have per-ID rows for all; leave missing
    return claims


def resolve_unit(raw: str) -> str:
    raw = raw.strip()
    if raw in NAME_TO_UNIT:
        return NAME_TO_UNIT[raw]
    # try first segment before comma
    first = raw.split(",")[0].strip()
    if first in NAME_TO_UNIT:
        return NAME_TO_UNIT[first]
    # try before /
    first = raw.split("/")[0].strip()
    if first in NAME_TO_UNIT:
        return NAME_TO_UNIT[first]
    # slug
    slug = re.sub(r"[^A-Za-z0-9]+", "_", raw).strip("_").upper()[:48]
    return slug or "UNKNOWN"


def sector_for(unit_id: str, cand_units: dict) -> str:
    if unit_id in cand_units:
        return cand_units[unit_id]["sector_id"]
    for uid, sec, *_ in EXTRA_UNITS:
        if uid == unit_id:
            return sec
    # guess from prefix
    prefixes = {
        "CRYO": "CRYO",
        "MEOH": "MEOH",
        "MET_": "MFG",
        "WS_": "FAB",
        "GEO": "GEO",
        "EW_": "WET",
        "OIL_": "OIL",
        "GLASS": "GLASS",
        "BMED": "WET",
        "POLISH": "WET",
        "HDR_": "WTR",
        "FAB_": "FAB",
        "Q4": "HAB",
    }
    for p, s in prefixes.items():
        if unit_id.startswith(p):
            return s
    return "WET"


def main() -> None:
    cand = json.loads(CAND.read_text())
    cand_units = {u["unit_id"]: u for u in cand["units"]}
    cand_streams = {s["stream_id"]: s for s in cand["streams"]}
    claims = parse_mass_flow_claims()
    register = parse_stream_register()

    nodes: dict[str, dict] = {}

    def ensure_node(uid: str, *, presence=None, sector=None, cls=None, diagram_gap=None, notes=None, tags=None):
        if uid in nodes:
            return
        cu = cand_units.get(uid)
        if cu:
            is_ph = uid in PLACEHOLDER_UNITS or cu.get("class") == "study_stub"
            nodes[uid] = {
                "unit_id": uid,
                "sector_id": cu["sector_id"],
                "presence": "placeholder" if is_ph else "present",
                "class": cu.get("class"),
                "tags": list(cu.get("tags") or []),
                "electrical_role": cu.get("electrical_role"),
                "diagram_gap": DIAGRAM_GAP_UNITS.get(uid),
                "notes": notes,
            }
            if is_ph and "study_stub" not in nodes[uid]["tags"]:
                nodes[uid]["tags"].append("study_stub")
            return
        nodes[uid] = {
            "unit_id": uid,
            "sector_id": sector or sector_for(uid, cand_units),
            "presence": presence or "present",
            "class": cls,
            "tags": tags or [],
            "electrical_role": None,
            "diagram_gap": diagram_gap or DIAGRAM_GAP_UNITS.get(uid),
            "notes": notes,
        }

    # Seed from candidate units
    for uid, u in cand_units.items():
        ensure_node(uid)

    # Extra structural
    for uid, sec, presence, cls, dgap, notes in EXTRA_UNITS:
        ensure_node(uid, presence=presence, sector=sec, cls=cls, diagram_gap=dgap, notes=notes)

    edges = []
    seen = set()

    def add_edge(e: dict):
        sid = e["stream_id"]
        if sid in seen:
            return
        seen.add(sid)
        ensure_node(e["from_unit_id"])
        ensure_node(e["to_unit_id"])
        # Placeholder rate rule
        from_ph = nodes[e["from_unit_id"]]["presence"] == "placeholder"
        to_ph = nodes[e["to_unit_id"]]["presence"] == "placeholder"
        if e.get("presence") == "placeholder" or from_ph or to_ph:
            e["presence"] = "placeholder"
            e["rate"] = {"value": None, "unit": None, "status": "null", "note": "placeholder — no invented rate (lock present_plus_placeholders)"}
        edges.append(e)

    # Inter-block from register
    for row in register:
        sid = row["stream_id"]
        cs = cand_streams.get(sid)
        if cs:
            frm = cs["from_unit_id"]
            to = cs["to_unit_id"]
            phase = cs.get("phase") or row["phase"]
            carries = cs.get("carries") or row["carries"]
            rate = cs.get("rate")
            from_sec = cs.get("from_sector_id")
            to_sec = cs.get("to_sector_id")
            open_b = bool(cs.get("open_boundary"))
        else:
            frm = resolve_unit(row["from_raw"])
            to = resolve_unit(row["to_raw"])
            # Multi-destination: register lists several — keep primary resolve; flag
            phase = row["phase"]
            carries = row["carries"]
            rate = None
            from_sec = None
            to_sec = None
            open_b = False

        layers = phase_layers(phase, sid)
        gap_flags = []
        # S17 + MeOH S73–S82 now on graph-bridged electrical_sld.png / mass_flow_pfd.png
        # (WP-A10 matplotlib bridge tranche). Do not re-flag as undrawn/missing.
        if sid == "S48":
            gap_flags.append("orc_stub_kw_tbd")
        if sid not in cand_streams:
            gap_flags.append("absent_from_candidate_mvs")

        # Presence: if endpoints placeholder → placeholder; S48 GEO_ORC placeholder
        presence = "present"
        ensure_node(frm)
        ensure_node(to)
        if nodes[frm]["presence"] == "placeholder" or nodes[to]["presence"] == "placeholder":
            presence = "placeholder"

        rate_obj = None
        if presence == "placeholder":
            rate_obj = {"value": None, "unit": None, "status": "null", "note": "placeholder — no invented rate (lock present_plus_placeholders)"}
        elif rate:
            rate_obj = {
                "value": rate.get("value"),
                "unit": rate.get("unit"),
                "status": rate.get("status") or "study",
                "note": rate.get("note"),
            }
        else:
            rate_obj = {"value": None, "unit": None, "status": "null", "note": "no rate in candidate_mvs / authority numeric — not invented"}

        add_edge(
            {
                "stream_id": sid,
                "from_unit_id": frm,
                "to_unit_id": to,
                "phase": phase,
                "layers": layers,
                "presence": presence,
                "carries": carries,
                "header": row["header"],
                "forbidden": row["forbidden"],
                "claim_status": claims.get(sid),
                "rate": rate_obj,
                "from_sector_id": from_sec or nodes[frm]["sector_id"],
                "to_sector_id": to_sec or nodes[to]["sector_id"],
                "open_boundary": open_b,
                "namespace": "S",
                "gap_flags": gap_flags,
                "notes": f"From register: {row['from_raw']} → {row['to_raw']}" if not cs else None,
            }
        )

    # Sandbox extras S08G / S14X — keep flagged, do not promote to register
    for sid in ("S08G", "S14X"):
        cs = cand_streams[sid]
        ensure_node(cs["from_unit_id"])
        ensure_node(cs["to_unit_id"])
        rate = cs.get("rate") or {}
        add_edge(
            {
                "stream_id": sid,
                "from_unit_id": cs["from_unit_id"],
                "to_unit_id": cs["to_unit_id"],
                "phase": cs["phase"],
                "layers": ["mass"],
                "presence": "present",
                "carries": cs.get("carries"),
                "header": None,
                "forbidden": None,
                "claim_status": None,
                "rate": {
                    "value": rate.get("value"),
                    "unit": rate.get("unit"),
                    "status": rate.get("status") or "study",
                    "note": rate.get("note"),
                },
                "from_sector_id": cs.get("from_sector_id"),
                "to_sector_id": cs.get("to_sector_id"),
                "open_boundary": bool(cs.get("open_boundary")),
                "namespace": "SANDBOX",
                "gap_flags": ["sandbox_extra_not_in_STREAM_REGISTER", "reconcile_or_keep_sandbox"],
                "notes": "candidate_mvs extension — do not invent new register ID",
            }
        )

    # DOCK export — no S##; placeholder edge without inventing ID
    add_edge(
        {
            "stream_id": "DOCK_EXPORT_TBD",
            "from_unit_id": "NORTH_DOCK",
            "to_unit_id": "BOUNDARY_EXPORT",
            "phase": "S",
            "layers": ["mass"],
            "presence": "placeholder",
            "carries": "goods / cassettes / surplus freight (ID TBD)",
            "header": None,
            "forbidden": None,
            "claim_status": None,
            "rate": {"value": None, "unit": None, "status": "null", "note": "placeholder — do not invent S## or rate"},
            "from_sector_id": "DOCK",
            "to_sector_id": "DOCK",
            "open_boundary": True,
            "namespace": "TBD",
            "gap_flags": ["no_S_id", "do_not_invent_route_or_rate", "high_severity_audit"],
            "notes": "Audit §7.1 DOCK export — sector required; no inter-block stream ID issued",
        }
    )

    # Intra-aisle
    for sid, frm, to, phase, carries, layers, note in INTRA_AISLE:
        add_edge(
            {
                "stream_id": sid,
                "from_unit_id": frm,
                "to_unit_id": to,
                "phase": phase,
                "layers": layers,
                "presence": "placeholder",
                "carries": carries,
                "header": None,
                "forbidden": None,
                "claim_status": None,
                "rate": {"value": None, "unit": None, "status": "null", "note": "intra-aisle placeholder — rate unknown"},
                "from_sector_id": sector_for(frm, cand_units),
                "to_sector_id": sector_for(to, cand_units),
                "open_boundary": False,
                "namespace": "IA",
                "gap_flags": ["intra_aisle", "full_depth_now", note],
                "notes": note,
            }
        )

    # ESS layer edges
    for sid, frm, to, phase, carries, layers, as_ph in ESS_EDGES:
        # MEOH DIS duplicates S79 conceptually — mark gap if S79 exists
        gap = ["ess_layer"]
        if sid == "IA-ESS-MEOH-DIS":
            gap.append("overlaps_S79_architecture")
        if sid == "IA-ESS-HYDRO-ELEC":
            gap.append("missing_on_sld")
        add_edge(
            {
                "stream_id": sid,
                "from_unit_id": frm,
                "to_unit_id": to,
                "phase": phase,
                "layers": layers,
                "presence": "placeholder" if as_ph else "present",
                "carries": carries,
                "header": None,
                "forbidden": None,
                "claim_status": None,
                "rate": (
                    {"value": None, "unit": None, "status": "null", "note": "ESS typed edge — rate not invented"}
                    if as_ph
                    else None
                ),
                "from_sector_id": sector_for(frm, cand_units),
                "to_sector_id": sector_for(to, cand_units),
                "open_boundary": False,
                "namespace": "IA",
                "gap_flags": gap,
                "notes": "EFD chemical-storage / charge-discharge typing",
            }
        )
        # Fix present ESS hydro mass peers — attach rates from S22/S23 if we want; keep null inventory_cycle
        if not as_ph and sid in ("IA-ESS-HYDRO-CHG", "IA-ESS-HYDRO-DIS"):
            edges[-1]["rate"] = {
                "value": None,
                "unit": "kg/d",
                "status": "null",
                "note": "inventory_cycle — peers S22/S23; no invented continuous rate",
            }
            edges[-1]["presence"] = "present"
        if not as_ph and sid == "IA-ESS-MEOH-DIS":
            # Use S79 rate by reference note; edge itself is architectural duplicate — keep as placeholder to avoid double-count
            edges[-1]["presence"] = "placeholder"
            edges[-1]["rate"] = {
                "value": None,
                "unit": None,
                "status": "null",
                "note": "use S79 for rate; this edge is ESS-layer view alias",
            }

    view_presets = [
        {
            "preset_id": "VIEW-PFD-LINE",
            "view_mode": "PFD",
            "layer_filter": ["mass", "elec", "thermal"],
            "include_intra_aisle": True,
            "include_placeholders": True,
            "description": "Line PFD full_depth_now (inter-block + IA-*)",
        },
        {
            "preset_id": "VIEW-MFD-CAMPUS",
            "view_mode": "MFD",
            "layer_filter": ["mass"],
            "include_intra_aisle": False,
            "include_placeholders": True,
            "description": "Inter-block mass edges; claim_status attributes",
        },
        {
            "preset_id": "VIEW-EFD-ELEC",
            "view_mode": "EFD",
            "layer_filter": ["elec"],
            "include_intra_aisle": True,
            "include_placeholders": True,
            "description": "EFD layer A — electrical",
        },
        {
            "preset_id": "VIEW-EFD-THERMAL",
            "view_mode": "EFD",
            "layer_filter": ["thermal"],
            "include_intra_aisle": True,
            "include_placeholders": True,
            "description": "EFD layer B — thermal Q1–Q4",
        },
        {
            "preset_id": "VIEW-EFD-ESS",
            "view_mode": "EFD",
            "layer_filter": ["ess"],
            "include_intra_aisle": True,
            "include_placeholders": True,
            "description": "EFD layer C — chemical-storage charge/discharge",
        },
    ]

    gaps = [
        {"id": "S17_bridged", "severity": "low", "detail": "S17 labeled on graph-bridged electrical_sld.png; still sparse on line PFDs"},
        {"id": "DOCK_EXPORT_TBD", "severity": "high", "detail": "Placeholder edge; no S## invented; shown as TBD on mass_flow_pfd"},
        {"id": "MEOH_MF_SLD_BRIDGED", "severity": "low", "detail": "S73–S82 on graph-bridged mass_flow_pfd + S79 on electrical_sld; MF claim_status rows still end S72"},
        {"id": "PUMPED_HYDRO_PFD", "severity": "medium", "detail": "Dedicated hydro_dock_pfd graph-bridged; HYDRO elec still rate null / placeholder on SLD"},
        {"id": "DOCK_PFD", "severity": "medium", "detail": "Dedicated hydro_dock_pfd graph-bridged; DOCK_EXPORT_TBD remains TBD (no S##)"},
        {"id": "INTRA_AISLE_RATES", "severity": "medium", "detail": "IA-* IDs assigned; rates null until measured/issued"},
        {"id": "SANDBOX_S08G_S14X", "severity": "medium", "detail": "Keep sandbox or promote — do not invent third ID"},
        {"id": "GENERATOR_MIGRATION", "severity": "medium", "detail": "Other matplotlib pfd_scripts/* still legacy bootstrap; electrical_sld + mass_flow_pfd graph-bridged"},
    ]

    notes = [
        "Sole typed topology authority per typed_graph_sole. UI + diagrams shall render/solve from this graph.",
        "STREAM_REGISTER / MASS_FLOW are derived or bi-synced via export_authority_md.py — not competing masters after migration.",
        "present_plus_placeholders: study stubs VCD/LITHO/ORC/BLOW/REMIN/ELECTRODE_COAT/SOLAR_PV_CELL/GEO_ORC have presence=placeholder and rate=null.",
        "Do not invent stream routes, rates, or nameplates. Gaps remain flagged.",
        "Licence: CERN-OHL-S-2.0.",
    ]

    # WP-Ap1: preserve mvs + unit enrichment; never silent dual-write
    prior_mvs, enrich = _load_prior_mvs_and_enrichment()
    for uid, n in nodes.items():
        e = enrich.get(uid) or {}
        n.setdefault("enabled", e.get("enabled", True))
        if "continuous_kw" in e:
            n["continuous_kw"] = e["continuous_kw"]
        else:
            n.setdefault("continuous_kw", None)
        n.setdefault("modules", list(e.get("modules") or []))
        params = dict(e.get("params") or {})
        params.update(n.get("params") or {})
        n["params"] = params

    if prior_mvs is not None:
        notes.insert(
            0,
            "WP-Ap1: mvs block + node enrichment preserved across build_seed; "
            "candidate_mvs.json is generated via export_candidate_mvs.py only.",
        )

    graph = {
        "schema_version": "aqs-flow-graph-0.1",
        "doc_id": "AQS-FLOW-GRAPH-001",
        "revision": "B",
        "licence": "CERN-OHL-S-2.0",
        "date": "2026-10-01",
        "sole_authority": True,
        "locks": [
            "layered_views",
            "full_depth_now",
            "efd_three_layers",
            "typed_graph_sole",
            "present_plus_placeholders",
        ],
        "nodes": sorted(nodes.values(), key=lambda n: n["unit_id"]),
        "edges": edges,
        "view_presets": view_presets,
        "gaps": gaps,
        "notes": notes,
        "mvs": prior_mvs,
    }

    OUT.write_text(json.dumps(graph, indent=2) + "\n")
    print("WP-Ap1 mvs block:", "present" if prior_mvs else "MISSING — fold required")
    print("Next: python3 export_candidate_mvs.py  # refresh projection")
    n_present = sum(1 for n in graph["nodes"] if n["presence"] == "present")
    n_ph = sum(1 for n in graph["nodes"] if n["presence"] == "placeholder")
    e_present = sum(1 for e in edges if e["presence"] == "present")
    e_ph = sum(1 for e in edges if e["presence"] == "placeholder")
    print(f"Wrote {OUT}")
    print(f"nodes: {len(graph['nodes'])} (present={n_present}, placeholder={n_ph})")
    print(f"edges: {len(edges)} (present={e_present}, placeholder={e_ph})")
    print(f"S##: {sum(1 for e in edges if e['namespace']=='S')}")
    print(f"IA: {sum(1 for e in edges if e['namespace']=='IA')}")
    print(f"TBD: {sum(1 for e in edges if e['namespace']=='TBD')}")
    print(f"SANDBOX: {sum(1 for e in edges if e['namespace']=='SANDBOX')}")


if __name__ == "__main__":
    main()

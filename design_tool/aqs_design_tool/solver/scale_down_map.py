# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Scale-down → unreclaimed-resource map (AQS-SCALE-UR-001 Rev C).

When sandbox disables a required sector / ESS peer, or derates SCALE_M
below M1 closure rules, the solver emits ``unreclaimed_resource`` gaps
tied to ``stream_id`` / ``sector_id``. Does **not** invent mass closure.

Canonical prose: ``cad/SCALE_DOWN_UNRECLAIMED.md`` (Rev C unit-level).
"""

from __future__ import annotations

from typing import TypedDict


class UnreclaimedEntry(TypedDict):
    stream_ids: list[str]
    sector_definition: str | None
    detail: str


# sector_id → streams / Sector Definition reopened as unreclaimed when off
SECTOR_OFF_UNRECLAIMED: dict[str, UnreclaimedEntry] = {
    "ZNBR2": {
        "stream_ids": ["S69", "S17"],
        "sector_definition": "Energy Storage System (Electrochemical)",
        "detail": "ZnBr2 ESS peer off — Br2 regen / DC storage path unreclaimed",
    },
    "MEOH": {
        "stream_ids": ["S73", "S74", "S76", "S79"],
        "sector_definition": "Energy Storage System (Electrochemical)",
        "detail": "MeOH ESS peer off — CO2/H2 synth, fuel, and MEOH_FC DC unreclaimed",
    },
    "PUMPED_HYDRO": {
        "stream_ids": ["S22", "S23"],
        "sector_definition": "Energy Storage System (Gravity)",
        "detail": "Pumped-hydro ESS peer off — roof↔catch penstock unreclaimed",
    },
    "WET": {
        "stream_ids": ["S08", "S05", "S64"],
        "sector_definition": "Process (Mass transform)",
        "detail": "WET off — metals crib + Faraday H2 generation unreclaimed",
    },
    "OIL": {
        "stream_ids": ["S11", "S18", "S67", "S67B"],
        "sector_definition": "Process (Mass transform)",
        "detail": "OIL off — organics / afterburner→CRYO CO2 path unreclaimed (carbon on S67/S67B since graph Rev J; S18 is the claim id)",
    },
    "GLASS": {
        "stream_ids": ["S08G"],
        "sector_definition": "Process (Mass transform)",
        "detail": "GLASS off — silicate/ceramic goods export unreclaimed",
    },
    "GAS": {
        "stream_ids": ["S05", "S64", "S65", "S24"],
        "sector_definition": "Process (Mass transform)",
        "detail": "GAS off — H2 dryer / acid-gas polish / vent-closure paths unreclaimed",
    },
    "FAB": {
        "stream_ids": ["S03", "S09", "S10"],
        "sector_definition": "Process (Mass transform)",
        "detail": "FAB off — wafer/UPW/etch returns unreclaimed (goods surplus gap)",
    },
    "MFG": {
        "stream_ids": ["S08", "S16"],
        "sector_definition": "Process (Mass transform)",
        "detail": "MFG off — metals crib / scrap return unreclaimed (goods surplus gap)",
    },
    "NUT": {
        "stream_ids": ["S07", "S12"],
        "sector_definition": "Process (Mass transform)",
        "detail": "NUT off — nutrient dose / grey→dose unreclaimed",
    },
    "FARM": {
        "stream_ids": ["S14", "S14X", "S15", "S11"],
        "sector_definition": "Life support / habitat",
        "detail": "FARM off — food / O2 / organics unreclaimed",
    },
    "HAB": {
        "stream_ids": ["S02", "S12", "S21"],
        "sector_definition": "Life support / habitat",
        "detail": "HAB off — life O2 / grey / potable draw unreclaimed",
    },
    "CRYO": {
        "stream_ids": ["S02", "S03", "S04", "S64", "S45", "S49", "S50", "S73", "S74"],
        "sector_definition": "Utility / header",
        "detail": "CRYO off — product gases + H2/CO2 consumers unreclaimed",
    },
    "WTR": {
        "stream_ids": ["S01", "S21", "S22", "S23", "S40"],
        "sector_definition": "Utility / header",
        "detail": "WTR off — UPW / roof–catch / terrace overflow unreclaimed",
    },
    "ELEC": {
        "stream_ids": ["S17", "S47", "S51", "S79"],
        "sector_definition": "Utility / header",
        "detail": "ELEC hub off — DC/AC bus injectors unreclaimed",
    },
    "ELEC_PV": {
        "stream_ids": ["S17", "S20"],
        "sector_definition": "Energy Production (Electrical)",
        "detail": "ELEC_PV off — PV generation / load bus unreclaimed",
    },
    "DOCK": {
        "stream_ids": ["S14X", "S08G"],
        "sector_definition": "Export / dock",
        "detail": "DOCK off — surplus export boundaries unreclaimed",
    },
    "TRR": {
        "stream_ids": ["S40"],
        "sector_definition": "Utility / header",
        "detail": "TRR off — clean terrace overflow path unreclaimed (optional sector)",
    },
    "BACKUP_GEN": {
        "stream_ids": ["S45", "S47"],
        "sector_definition": "Energy Production (Combustion Engine)",
        "detail": "BACKUP_GEN off — H2→GEN AC path unreclaimed (optional)",
    },
    "FUEL_CELL": {
        "stream_ids": ["S49", "S50", "S51"],
        "sector_definition": "Energy Production (Electrochemical)",
        "detail": "FUEL_CELL off — PEM H2/O2→BATT DC unreclaimed (optional)",
    },
    "GEO": {
        "stream_ids": ["S06"],
        "sector_definition": "Utility / header",
        "detail": "GEO off — Q4 heat path unreclaimed (optional / ORC TBD)",
    },
}


# SCALE_M / discrete derates that break M1 closure rules (AQS-SCALE-001)
# When sandbox scale_m falls below these floors, emit unreclaimed tied to streams.
SCALE_DERATE_RULES: list[dict] = [
    {
        "id": "below_m1_scale",
        "min_scale_m": 1.0,
        "stream_ids": ["S08", "S05", "S64", "S14", "S21"],
        "sector_ids": ["WET", "FARM", "WTR"],
        "detail": (
            "SCALE_M below M1 baseline (1.0) — cassette/wet-feed 150 kg/d, "
            "life plate, and water inventory rules no longer close without "
            "flagging unreclaimed resources (AQS-SCALE-001 / AQS-SCALE-UR-001)"
        ),
    },
    {
        "id": "life_levels_collapse",
        "min_scale_m": 1.0,  # floor(SCALE_M) < 1 impossible at ≥1; flag same band
        "stream_ids": ["S14", "S02", "S12"],
        "sector_ids": ["FARM", "HAB"],
        "detail": (
            "Life-floor discrete rule LIFE_LEVELS=max(1,floor(SCALE_M)) — "
            "sandbox derate below M1 leaves HAB∥FARM capacity unreclaimed"
        ),
    },
]



# unit_id → streams reopened when unit disabled while parent sector may stay on
# (AQS-SCALE-UR-001 Rev C / WP-A7). P0/P1 consume-ready.
UNIT_OFF_UNRECLAIMED: dict[str, UnreclaimedEntry] = {
    "VCD_TRAIN": {
        "stream_ids": ["S25", "S28", "S29"],
        "sector_definition": "Utility / header",
        "detail": "VCD_TRAIN off — open study ST-VCD-01 queued (potable Present blocked; not accepted unreclaimed endpoint)",
    },
    "REMIN": {
        "stream_ids": ["S26"],
        "sector_definition": "Utility / header",
        "detail": "REMIN off — open study ST-REMIN-01 queued (potable export Present blocked)",
    },
    "GEO_ORC": {
        "stream_ids": ["S48"],
        "sector_definition": "Utility / header",
        "detail": "GEO_ORC off — open study ST-ORC-01 queued (GHEX survey before kW_e freeze)",
    },
    "LITHO_STUB": {
        "stream_ids": ["S38"],
        "sector_definition": "Process (Mass transform)",
        "detail": "LITHO_STUB off — open study ST-LITHO-01 queued (electronic self-copy Incomplete; not accepted omission)",
    },
    "SOLAR_PV_CELL": {
        "stream_ids": ["S03", "S10"],
        "sector_definition": "Process (Mass transform)",
        "detail": "SOLAR_PV_CELL off — open study ST-SOLAR-01 queued (nameplates/offtake Incomplete)",
    },
    "HYDRO_SET": {
        "stream_ids": ["S22", "S23"],
        "sector_definition": "Energy Storage System (Gravity)",
        "detail": "HYDRO_SET off — penstock inventory cycle unreclaimed (ESS peer incomplete)",
    },
    "ZNBR2": {
        "stream_ids": ["S69", "S17"],
        "sector_definition": "Energy Storage System (Electrochemical)",
        "detail": "ZNBR2 unit off — Br2 regen / DC storage unreclaimed",
    },
    "MEOH_FC": {
        "stream_ids": ["S79"],
        "sector_definition": "Energy Storage System (Electrochemical)",
        "detail": "MEOH_FC off — MeOH DC inject unreclaimed",
    },
    "MEOH_SYNTH": {
        "stream_ids": ["S73", "S74", "S76"],
        "sector_definition": "Energy Storage System (Electrochemical)",
        "detail": "MEOH_SYNTH off — CO2/H2→MeOH synth unreclaimed",
    },
    "MEOH_TANK": {
        "stream_ids": ["S76"],
        "sector_definition": "Energy Storage System (Electrochemical)",
        "detail": "MEOH_TANK off — MeOH inventory unreclaimed",
    },
    "GROW_BED": {
        "stream_ids": ["S14", "S14X", "S15"],
        "sector_definition": "Life support / habitat",
        "detail": "GROW_BED off — food / O2 farm path unreclaimed",
    },
    "ROOF_TANK": {
        "stream_ids": ["S21", "S22", "S40"],
        "sector_definition": "Utility / header",
        "detail": "ROOF_TANK off — tower inventory / penstock / overflow unreclaimed",
    },
    "CATCH_TANK": {
        "stream_ids": ["S21", "S23"],
        "sector_definition": "Utility / header",
        "detail": "CATCH_TANK off — catch inventory / return unreclaimed",
    },
    "H2_DRYER": {
        "stream_ids": ["S64", "S24"],
        "sector_definition": "Process (Mass transform)",
        "detail": "H2_DRYER off — dryer path + contingency unreclaimed",
    },
    "ALK_SCRUBBER": {
        "stream_ids": ["S65"],
        "sector_definition": "Process (Mass transform)",
        "detail": "ALK_SCRUBBER off — acid-gas polish unreclaimed",
    },
    "WAFER_FAB": {
        "stream_ids": ["S03", "S09", "S10", "S38"],
        "sector_definition": "Process (Mass transform)",
        "detail": "WAFER_FAB off — wafer gases/etch/litho unreclaimed",
    },
    "MFG_SHOP": {
        "stream_ids": ["S08", "S16"],
        "sector_definition": "Process (Mass transform)",
        "detail": "MFG_SHOP off — metals crib / scrap unreclaimed",
    },
    "BLOW_MOLD": {
        "stream_ids": ["S16"],
        "sector_definition": "Process (Mass transform)",
        "detail": "BLOW_MOLD off — open study ST-BLOW-01 queued (required for MVS; not accepted unreclaimed endpoint)",
    },
    "ELECTRODE_COAT": {
        "stream_ids": ["S71", "S72"],
        "sector_definition": "Process (Mass transform)",
        "detail": "ELECTRODE_COAT off — open study ST-ELC-01 queued (required for MVS; exhaust path incomplete)",
    },
}


def streams_for_unit_off(unit_id: str) -> UnreclaimedEntry | None:
    return UNIT_OFF_UNRECLAIMED.get(unit_id)

def streams_for_sector_off(sector_id: str) -> UnreclaimedEntry | None:
    return SECTOR_OFF_UNRECLAIMED.get(sector_id)


def derate_hits(scale_m: float) -> list[dict]:
    """Return SCALE_DERATE_RULES that fire for this scale_m."""
    hits = []
    for rule in SCALE_DERATE_RULES:
        if scale_m < float(rule["min_scale_m"]) - 1e-12:
            hits.append(rule)
    return hits

# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Scale-down → unreclaimed-resource map (AQS-SCALE-UR-001 Rev C).

When sandbox disables a required sector / ESS peer, or derates SCALE_M
below M1 closure rules, the solver emits ``unreclaimed_resource`` gaps
tied to ``stream_id`` / ``sector_id``. Does **not** invent mass closure.

Canonical prose: ``cad/SCALE_DOWN_UNRECLAIMED.md`` (Rev C unit-level).

2026-10-18 re-key (first-principles audit §sector definitions, Rev AC
ontology): ``SECTOR_OFF_UNRECLAIMED`` keys now match the 19-sector
``SECTOR_CATALOGUE`` exactly. WET→DIGESTER rename; FOUNDRY / POLYMERS /
HEAT rows added; the six deleted-sector rows (ZNBR2 / WET / ELEC_PV /
TRR / BACKUP_GEN / FUEL_CELL) removed, with their still-relevant content
moved to ``UNIT_OFF_UNRECLAIMED`` (PV_ARRAY / ZNBR2 / FUEL_CELL /
BACKUP_GEN are units in ELEC since the Rev AC pivot). Stream ids
refreshed to the live graph: S05 / S14X / S40 / S06 are retired.
"""

from __future__ import annotations

from typing import TypedDict


class UnreclaimedEntry(TypedDict):
    stream_ids: list[str]
    sector_definition: str | None
    detail: str


# sector_id → streams / Sector Definition reopened as unreclaimed when off.
# Keyed 1:1 to SECTOR_CATALOGUE (19 sectors, AQS-SEC-001 Rev E + Rev AC
# sector refresh). Stream ids verified against plant_flow_graph.json Rev AC.
SECTOR_OFF_UNRECLAIMED: dict[str, UnreclaimedEntry] = {
    "DIGESTER": {
        # Renamed from WET at the Rev AC sector pivot (graph Rev AC, 6e25619).
        "stream_ids": [
            "S08",            # leach → MFG metals/Si crib (42 kg/d)
            "S16",            # MFG scrap return (12 kg/d)
            "S10",            # WET_BENCH spent etch return (79.12 kg/d)
            "IA-FEED-01",     # HOPPER plant feedstock into leach CSTR-1
            "IA-DC-EW_9",     # RECTIFIER DC bus bar to EW-9 (7.54 kW)
            "IA-HDR-H2-04",   # EW-9 cathode H2 to the H2 pool (Faraday)
        ],
        "sector_definition": "Process (Mass transform)",
        "detail": (
            "DIGESTER off (was WET) — leach/EW/BMED train, metals crib and "
            "Faraday H2 generation unreclaimed"
        ),
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
    "POLYMERS": {
        # Rev AC scope (fluoropolymer + polyolefin train).
        "stream_ids": [
            "IA-C5-POLY",     # PROD_C5_C10 naphtha olefin feed (0.41 kg/d)
            "POLY_TO_MFG",    # polymer feedstock to manufacturing (0.38 kg/d)
            "POLY_TO_FAB",    # polymer feedstock to the wafer fab
            "POLY_TO_WET",    # lining/gasket stock return to leach
            "CRU_TO_VDF",     # chlorate-route chlorine to VDF synthesis
            "CRU_TO_TFE",     # chlorate-route chlorine to TFE synthesis
        ],
        "sector_definition": "Process (Mass transform)",
        "detail": (
            "POLYMERS off — fluoropolymer / polyolefin train "
            "(naphtha→pellet→MFG/FAB) unreclaimed"
        ),
    },
    "GAS": {
        # S05 retired with the old Faraday single-stream view; S64 is the
        # H2_DRYER normal path that carries the same pool now.
        "stream_ids": ["S64", "S65", "S24"],
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
    "FOUNDRY": {
        # Rev AC scope: smelting pots moved in from MFG (100% of pot edges to
        # FOUNDRY/DIGESTER); goods-surplus train with MFG/FAB (A2 lineage).
        "stream_ids": [
            "MFG_SCRAP_TO_IND",    # MFG scrap return to induction melt (14.14 kg/d)
            "STOCK_TO_MFG",        # cast/rolled stock to manufacturing (14.0 kg/d)
            "FOUNDRY_SLAG_TO_LEACH",  # slag return to leach (0.14 kg/d)
            "SF-IND_MELT",         # SOL_ARK AC feed, 25 kW wired load
            "SF-RF_HEAT",          # SOL_ARK AC feed, 5 kW wired load
            "SF-VAC_IND",          # SOL_ARK AC feed, 15 kW wired load
        ],
        "sector_definition": "Process (Mass transform)",
        "detail": (
            "FOUNDRY off — melt/cast/roll goods train + wired AC feeds "
            "(SF-*) unreclaimed"
        ),
    },
    "NUT": {
        "stream_ids": ["S07", "S12"],
        "sector_definition": "Process (Mass transform)",
        "detail": "NUT off — nutrient dose / grey→dose unreclaimed",
    },
    "FARM": {
        # S14X retired at Rev AC; food export is booked on the goods balance.
        "stream_ids": ["S14", "S15", "S11"],
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
        # S40 terrace overflow retired with TERRACE_IRRIG (A-M-229).
        "stream_ids": ["S01", "S21", "S22", "S23"],
        "sector_definition": "Utility / header",
        "detail": "WTR off — UPW / roof–catch penstock / clean tower unreclaimed",
    },
    "ELEC": {
        # PV / ZNBR2 / FC / genset units live here as units since the Rev AC
        # pivot; their individual offs are mapped in UNIT_OFF_UNRECLAIMED.
        "stream_ids": ["S17", "S47", "S51", "S79"],
        "sector_definition": "Utility / header",
        "detail": "ELEC hub off — DC/AC bus injectors unreclaimed",
    },
    "HEAT": {
        # Rev AC scope: heat-ladder batteries Q1-Q4 + Q4_BUS branches.
        "stream_ids": [
            "S44",   # GEO_HP → Q4_BUS
            "S53",   # FUEL_CELL → Q4_BUS
            "S80",   # MEOH_FC → Q4_BUS
            "S100",  # Q4_BUS → leach HX-9 preheat
            "S101",  # Q4_BUS → GLASS_DIGEST HX-10 preheat
        ],
        "sector_definition": "Utility / header",
        "detail": "HEAT off — heat ladder stores + Q4_BUS branches unreclaimed (AQS-HEAT-LADDER-001; optional sector)",
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
    "GEO": {
        # S06 (Q4 heat path) retired; GEO_HP→Q4_BUS (S44) and the ORC study
        # edge (S48) are the current ties.
        "stream_ids": ["S44", "S48"],
        "sector_definition": "Utility / header",
        "detail": "GEO off — GEO_HP Q4 feed / ORC study path unreclaimed (optional / ORC TBD)",
    },
    "DOCK": {
        # S14X retired; surplus export is energy/O2/MeOH/oil-cuts, not metal
        # goods (A-M-265: DOCK_EXPORT_TBD = 0.0 from the goods balance).
        "stream_ids": ["S08G", "IA-O2-SHIP", "IA-MEOH-SHIP", "IA-C5-SHIP", "DOCK_EXPORT_TBD"],
        "sector_definition": "Export / dock",
        "detail": "DOCK off — surplus export boundaries unreclaimed (O2/MeOH/oil-cut shipments)",
    },
}


# SCALE_M / discrete derates that break M1 closure rules (AQS-SCALE-001)
# When sandbox scale_m falls below these floors, emit unreclaimed tied to streams.
SCALE_DERATE_RULES: list[dict] = [
    {
        "id": "below_m1_scale",
        "min_scale_m": 1.0,
        # S05 retired; IA-HDR-H2-04 is the EW-9 cathode H2 Faraday path.
        "stream_ids": ["S08", "IA-HDR-H2-04", "S64", "S14", "S21"],
        "sector_ids": ["DIGESTER", "FARM", "WTR"],
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
# 2026-10-18: PV_ARRAY / FUEL_CELL / BACKUP_GEN rows moved in from the deleted
# ELEC_PV / FUEL_CELL / BACKUP_GEN sector rows (Rev AC: units in ELEC); ZNBR2
# row refreshed to its current graph edges; GROW_BED / ROOF_TANK dropped their
# retired S14X / S40 ties.
UNIT_OFF_UNRECLAIMED: dict[str, UnreclaimedEntry] = {
    "PV_ARRAY": {
        "stream_ids": ["IA-PV-01", "IA-ESS-ZNBR2-SRC"],
        "sector_definition": "Energy Production (Electrical)",
        "detail": (
            "PV_ARRAY unit off — PV generation to the bus / ZnBr2 charge "
            "share unreclaimed (ELEC_PV sector deleted at Rev AC; PV is a "
            "unit in ELEC)"
        ),
    },
    "FUEL_CELL": {
        "stream_ids": ["S49", "S50", "S51", "S53"],
        "sector_definition": "Energy Production (Electrochemical)",
        "detail": (
            "FUEL_CELL unit off — PEM H2/O2→BATT DC + Q4 heat unreclaimed "
            "(FUEL_CELL sector deleted at Rev AC; AQS-FC-001 lineage)"
        ),
    },
    "BACKUP_GEN": {
        "stream_ids": ["S45", "S47"],
        "sector_definition": "Energy Production (Combustion Engine)",
        "detail": (
            "BACKUP_GEN unit off — standby H2→GEN AC path unreclaimed "
            "(BACKUP_GEN sector deleted at Rev AC; optional)"
        ),
    },
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
        # ZNBR2 sector deleted at Rev AC; the flow battery is a unit in ELEC
        # and the third ESS peer at unit level (ESS_PEER_UNIT_IDS).
        "stream_ids": [
            "IA-ESS-ZNBR2-CHG",  # SOL_ARK charge (PV/RECT surplus, 6.67 kW)
            "IA-ESS-ZNBR2-DIS",  # discharge to bus (5.0 kW)
            "S69",               # Br2 vapor to regen loop
            "IA-ZNBR-MU",        # electrolyte water make-up from leach
        ],
        "sector_definition": "Energy Storage System (Electrochemical)",
        "detail": "ZNBR2 unit off — bus charge/discharge / Br2 regen / electrolyte make-up unreclaimed",
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
        # S14X retired; S20 is the bed's SOL_ARK AC feed.
        "stream_ids": ["S14", "S15", "S11", "S20"],
        "sector_definition": "Life support / habitat",
        "detail": "GROW_BED off — food / O2 farm path unreclaimed",
    },
    "ROOF_TANK": {
        # S40 terrace overflow retired with TERRACE_IRRIG (A-M-229).
        "stream_ids": ["S21", "S22", "S23"],
        "sector_definition": "Utility / header",
        "detail": "ROOF_TANK off — tower inventory / penstock unreclaimed",
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

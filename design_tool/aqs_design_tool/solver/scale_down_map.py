# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Scale-down and switched-off map for the design tool (AQS-SCALE-UR-001).

When a design switches off a sector or a unit, or sets the scale factor below a rule's limit, the solver
reports ``unreclaimed_resource`` gaps tied to stream ids. It does not invent mass closure.

The sector entries and the heat store scale rules come from ``data/scale_down.json``, which
``flow_graph/param/scale_down.py`` computes from the plant graph by a balance on each sector. The unit entries
and the plant-wide scale rules below are kept by hand. The page ``docs-authority/SCALE_DOWN_UNRECLAIMED.md`` is
generated from both.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TypedDict


class UnreclaimedEntry(TypedDict):
    stream_ids: list[str]
    sector_definition: str | None
    detail: str


_DATA = json.loads((Path(__file__).resolve().parent.parent / "data" / "scale_down.json").read_text(encoding="utf-8"))


def _sector_entry(sector_id: str, rows: dict) -> UnreclaimedEntry:
    sink = [r["stream_id"] for r in rows["no_sink"]]
    source = [r["stream_id"] for r in rows["no_source"]]
    return {
        "stream_ids": sink + source,
        "sector_definition": _DATA["definitions"].get(sector_id),
        "detail": (
            f"{sector_id} off: {len(sink)} incoming stream(s) left without a sink, "
            f"{len(source)} outgoing stream(s) left without a source (AQS-SCALE-UR-001 section 3.2)"
        ),
    }


# sector_id → streams left unreclaimed or unsupplied when the sector is off; computed from the graph.
SECTOR_OFF_UNRECLAIMED: dict[str, UnreclaimedEntry] = {
    sid: _sector_entry(sid, rows) for sid, rows in _DATA["sector_off"].items()
}


# SCALE_M / discrete derates that break M1 closure rules (AQS-SCALE-001)
# When the design scale falls below these floors, emit unreclaimed tied to streams.
HAND_DERATE_RULES: list[dict] = [
    {
        "id": "below_m1_scale",
        "min_scale_m": 1.0,
        # S05 retired; IA-HDR-H2-04 is the EW-9 cathode H2 Faraday path.
        "stream_ids": ["S08", "IA-HDR-H2-04", "S64", "S14", "S21"],
        "sector_ids": ["DIGESTER", "FARM", "WTR"],
        "detail": "Below the baseline scale the 150 kg/d digester feed, the farm's minimum planting and the water inventory no longer balance, so their streams are flagged",
    },
    {
        "id": "life_levels_collapse",
        "min_scale_m": 1.0,  # whole levels: any scale below the baseline leaves part of a level unused
        "stream_ids": ["S14", "S02", "S12"],
        "sector_ids": ["FARM", "HAB"],
        "detail": "Habitat and farm are built in whole levels (at least one), so a smaller plant leaves part of a level unused",
    },
]



# Plant-wide rules above, plus one rule per heat store from the graph (AQS-SCALE-UR-001 Table 4.1).
SCALE_DERATE_RULES: list[dict] = HAND_DERATE_RULES + _DATA["derate_rules"]


# unit_id → streams reopened when unit disabled while parent sector may stay on
# (AQS-SCALE-UR-001 Rev C / WP-A7). P0/P1 consume-ready.
UNIT_OFF_UNRECLAIMED: dict[str, UnreclaimedEntry] = {
    "PV_ARRAY": {
        "stream_ids": ["IA-PV-01", "IA-ESS-ZNBR2-SRC"],
        "sector_definition": "Energy Production (Electrical)",
        "detail": "Solar array off: its generation to the electrical bus and its share of zinc-bromine battery charging are lost",
    },
    "FUEL_CELL": {
        "stream_ids": ["S49", "S50", "S51", "S53"],
        "sector_definition": "Energy Production (Electrochemical)",
        "detail": "Fuel cell off: its DC output to the battery and its heat to the Q4 store are lost; the hydrogen and oxygen it would use stay in storage",
    },
    "BACKUP_GEN": {
        "stream_ids": ["S45", "S47"],
        "sector_definition": "Energy Production (Combustion Engine)",
        "detail": "Standby generator off: the standby hydrogen-to-AC path is unavailable (the generator is optional)",
    },
    "VCD_TRAIN": {
        "stream_ids": ["S25", "S28", "S29"],
        "sector_definition": "Utility / header",
        "detail": "Vapour-compression distiller off: no potable water is produced; this is not an accepted end state, see study ST-VCD-01",
    },
    "REMIN": {
        "stream_ids": ["S26"],
        "sector_definition": "Utility / header",
        "detail": "Remineralizer off: distilled water cannot be exported as potable water; see study ST-REMIN-01",
    },
    "GEO_ORC": {
        "stream_ids": ["S48"],
        "sector_definition": "Utility / header",
        "detail": "Geothermal ORC off: no geothermal electricity; its rating waits on the ground heat exchanger survey, see study ST-ORC-01",
    },
    "LITHO_STUB": {
        "stream_ids": ["S38"],
        "sector_definition": "Process (Mass transform)",
        "detail": "Lithography stub off: the plant cannot make its own electronics; this is not an accepted omission, see study ST-LITHO-01",
    },
    "SOLAR_PV_CELL": {
        "stream_ids": ["S03", "S10"],
        "sector_definition": "Process (Mass transform)",
        "detail": "Solar cell line off: no replacement solar cells are made; ratings are not yet set, see study ST-SOLAR-01",
    },
    "HYDRO_SET": {
        "stream_ids": ["S22", "S23"],
        "sector_definition": "Energy Storage System (Gravity)",
        "detail": "Hydro turbine off: water lifted to the roof tank is not turned back into electricity",
    },
    "ZNBR2": {
        # The zinc-bromine flow battery is a unit in ELEC
        # and the third ESS peer at unit level (ESS_PEER_UNIT_IDS).
        "stream_ids": [
            "IA-ESS-ZNBR2-CHG",  # SOL_ARK charge (PV/RECT surplus, 6.67 kW)
            "IA-ESS-ZNBR2-DIS",  # discharge to bus (5.0 kW)
            "S69",               # Br2 vapor to regen loop
            "IA-ZNBR-MU",        # electrolyte water make-up from leach
        ],
        "sector_definition": "Energy Storage System (Electrochemical)",
        "detail": "Zinc-bromine battery off: bus charge and discharge, bromine regeneration and electrolyte make-up water are lost",
    },
    "MEOH_FC": {
        "stream_ids": ["S79"],
        "sector_definition": "Energy Storage System (Electrochemical)",
        "detail": "Methanol fuel cell off: methanol is not turned back into DC power",
    },
    "MEOH_SYNTH": {
        "stream_ids": ["S73", "S74", "S76"],
        "sector_definition": "Energy Storage System (Electrochemical)",
        "detail": "Methanol synthesis off: carbon dioxide and hydrogen are not made into methanol",
    },
    "MEOH_TANK": {
        "stream_ids": ["S76"],
        "sector_definition": "Energy Storage System (Electrochemical)",
        "detail": "Methanol tank off: methanol cannot be stored",
    },
    "GROW_BED": {
        # S14X retired; S20 is the bed's SOL_ARK AC feed.
        "stream_ids": ["S14", "S15", "S11", "S20"],
        "sector_definition": "Life support / habitat",
        "detail": "Grow bed off: food and oxygen from the farm are lost",
    },
    "ROOF_TANK": {
        # S40 terrace overflow retired with TERRACE_IRRIG (A-M-229).
        "stream_ids": ["S21", "S22", "S23"],
        "sector_definition": "Utility / header",
        "detail": "Roof tank off: the water inventory on the tower and the flow to the hydro turbine are lost",
    },
    "CATCH_TANK": {
        "stream_ids": ["S21", "S23"],
        "sector_definition": "Utility / header",
        "detail": "Catch tank off: the lower water inventory and the return flow are lost",
    },
    "H2_DRYER": {
        "stream_ids": ["S64", "S24"],
        "sector_definition": "Process (Mass transform)",
        "detail": "Hydrogen dryer off: dried hydrogen and its contingency path are lost",
    },
    "ALK_SCRUBBER": {
        "stream_ids": ["S65"],
        "sector_definition": "Process (Mass transform)",
        "detail": "Alkaline scrubber off: acid gases are not polished out of the vent",
    },
    "WAFER_FAB": {
        "stream_ids": ["S03", "S09", "S10", "S38"],
        "sector_definition": "Process (Mass transform)",
        "detail": "Wafer fab off: process gases, etch and lithography streams are unused",
    },
    "MFG_SHOP": {
        "stream_ids": ["S08", "S16"],
        "sector_definition": "Process (Mass transform)",
        "detail": "Machine shop off: metal stock is not drawn and scrap is not returned",
    },
    "BLOW_MOLD": {
        "stream_ids": ["S16"],
        "sector_definition": "Process (Mass transform)",
        "detail": "Blow moulder off: no bottles or containers are made; required for the minimum viable system, see study ST-BLOW-01",
    },
    "ELECTRODE_COAT": {
        "stream_ids": ["S71", "S72"],
        "sector_definition": "Process (Mass transform)",
        "detail": "Electrode coater off: no electrodes are coated and the exhaust path is incomplete; required for the minimum viable system, see study ST-ELC-01",
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

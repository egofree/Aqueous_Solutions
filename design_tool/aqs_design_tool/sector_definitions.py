# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Sector Definition taxonomy — AQS-UI-001 Rev C §3.1 + AQS-SEC-001 catalogue.

The graph's ``mvs.sectors`` is the authority for sector ids. This module mirrors
it for the design tool (``flow_graph/test_doc_consistency.py`` fails on drift)
and holds the retired and alias names. ``docs-authority/SECTOR_DEFINITIONS.md``
(AQS-SEC-001) is generated from both by ``docs-authority/_sector_definitions.py``.
Class list remains owned by AQS-UI-001 §3.1.

Project locks (2026-10-01):
- FAB and MFG ``required_for_mvs_closure=true`` for goods surplus (A2 closed).
- ESS peers ZNBR2 / MEOH / PUMPED_HYDRO: **all three**
  ``required_for_mvs_closure=true`` in MVS (A3 reframed Rev D). Redundancy
  is a core tenet; MeOH also feeds other processes. Sandbox may disable →
  solver emits ``unreclaimed_resource`` per missing ESS (incomplete
  closure — not accepted emissions). Do not invent new Sector Definition
  classes.
"""

from __future__ import annotations

from enum import Enum
from typing import Literal, TypedDict


class SectorDefinition(str, Enum):
    """Role types orthogonal to physical bay layout (AQS-UI-001 §3.1)."""

    ESS_GRAVITY = "Energy Storage System (Gravity)"
    ESS_ELECTROCHEMICAL = "Energy Storage System (Electrochemical)"
    ENERGY_PRODUCTION_ELECTRICAL = "Energy Production (Electrical)"
    ENERGY_PRODUCTION_COMBUSTION = "Energy Production (Combustion Engine)"
    ENERGY_PRODUCTION_ELECTROCHEMICAL = "Energy Production (Electrochemical)"
    PROCESS_MASS_TRANSFORM = "Process (Mass transform)"
    LIFE_SUPPORT_HABITAT = "Life support / habitat"
    UTILITY_HEADER = "Utility / header"
    EXPORT_DOCK = "Export / dock"


# Aliases rejected as sector_id (AQS-SEC-001 §4.1)
NON_SECTOR_ALIASES = {
    "POWER": "composite → ELEC (PV / ZNBR2 / FC / genset units) + GEO, MEOH",
    "LIFE": "composite → FARM + HAB (+ WTR)",
    "OIL_GLASS": "FreeCAD group → OIL + GLASS",
    "FRM": "alias → FARM",
    "CRY": "alias → CRYO",
    "MET": "folded under MFG",
    "SLINGSHOT": "non-sector interface",
    "CORE": "building shafts — not a sector toggle",
    "WATER": "legacy seed id → WTR (AQS-SEC-001)",
}

# Sector ids that existed in earlier graph revisions and are no longer sectors.
# ``now`` lists the current sector(s) holding their units (empty when retired outright).
RETIRED_SECTOR_IDS = {
    "WET": {"now": ["DIGESTER"], "when": "graph Rev AC (2026-10-17)",
            "note": "renamed; the same leach / EW / BMED / polish line"},
    "ELEC_PV": {"now": ["ELEC"], "when": "graph Rev AC (2026-10-17)",
                "note": "PV_ARRAY is a unit in ELEC"},
    "ZNBR2": {"now": ["ELEC"], "when": "graph Rev AC (2026-10-17)",
              "note": "the flow battery is a unit in ELEC; still an ESS peer by unit (ESS_PEER_UNIT_IDS)"},
    "BACKUP_GEN": {"now": ["ELEC"], "when": "graph Rev AC (2026-10-17)",
                   "note": "the standby H2 genset is a unit in ELEC"},
    "FUEL_CELL": {"now": ["ELEC"], "when": "graph Rev AC (2026-10-17)",
                  "note": "the PEM fuel cell is a unit in ELEC"},
    "TRR": {"now": [], "when": "2026-10-18",
            "note": "terrace irrigation retired with the TERRACE_IRRIG unit"},
}


class SectorCatalogueRow(TypedDict):
    sector_id: str
    sector_definition: str
    required_for_mvs_closure: bool
    enabled_default: bool
    notes: str
    aqs_sec_required: str  # true | false | study from AQS-SEC-001


# Reconciled to AQS-SEC-001 Rev E §4. FAB/MFG required (A2); all three ESS required (A3).
SECTOR_CATALOGUE: list[SectorCatalogueRow] = [
    {
        # Renamed from WET at the Rev AC sector pivot (graph Rev AC, 6e25619);
        # refreshed 2026-10-18 per notes/first_principles_audit_2026-10-17.md
        # §sector definitions (stale-row cleanup, D lane).
        "sector_id": "DIGESTER",
        "sector_definition": SectorDefinition.PROCESS_MASS_TRANSFORM.value,
        "required_for_mvs_closure": True,
        "enabled_default": True,
        "aqs_sec_required": "true",
        "notes": (
            "Leach / EW / BMED / polish; renamed from WET at the Rev AC sector "
            "pivot. 150 kg/d wet feed (AQS-SEC-001 lineage)."
        ),
    },
    {
        "sector_id": "OIL",
        "sector_definition": SectorDefinition.PROCESS_MASS_TRANSFORM.value,
        "required_for_mvs_closure": True,
        "enabled_default": True,
        "aqs_sec_required": "true",
        "notes": "Organics / oil loop; AFTERBURNER → CRYO",
    },
    {
        "sector_id": "GLASS",
        "sector_definition": SectorDefinition.PROCESS_MASS_TRANSFORM.value,
        "required_for_mvs_closure": True,
        "enabled_default": True,
        "aqs_sec_required": "true",
        "notes": "Silicate / ceramic; materials surplus path (AQS-SEC-001)",
    },
    {
        # Rev AC scope (fluoropolymer train: HF_GEN/VDF_SYN/TFE_SYN/POLY_F/...).
        "sector_id": "POLYMERS",
        "sector_definition": SectorDefinition.PROCESS_MASS_TRANSFORM.value,
        "required_for_mvs_closure": True,
        "enabled_default": True,
        "aqs_sec_required": "study",
        "notes": "Fluoropolymer synthesis, film, resins",
    },
    {
        "sector_id": "GAS",
        "sector_definition": SectorDefinition.PROCESS_MASS_TRANSFORM.value,
        "required_for_mvs_closure": True,
        "enabled_default": True,
        "aqs_sec_required": "true",
        "notes": "Scrub / vent closure (AQS-VENT-001); secondary Utility",
    },
    {
        "sector_id": "FAB",
        "sector_definition": SectorDefinition.PROCESS_MASS_TRANSFORM.value,
        "required_for_mvs_closure": True,  # AQS-SEC-001 Rev B+ A2 closed
        "enabled_default": True,
        "aqs_sec_required": "true",
        "notes": (
            "Wafer / solar-cell fab. Required for MVS goods surplus "
            "(Project decision 2026-10-01 / AQS-SEC-001 A2)."
        ),
    },
    {
        "sector_id": "MFG",
        "sector_definition": SectorDefinition.PROCESS_MASS_TRANSFORM.value,
        "required_for_mvs_closure": True,  # AQS-SEC-001 Rev B+ A2 closed
        "enabled_default": True,
        "aqs_sec_required": "true",
        "notes": (
            "Shop + metal forming (MET folded). Required for MVS goods surplus "
            "(Project decision 2026-10-01 / AQS-SEC-001 A2)."
        ),
    },
    {
        # Rev AC scope (smelting pots moved in from MFG 2026-10-18 per the
        # first-principles audit placement findings: 100 % of pot edges go to
        # FOUNDRY/DIGESTER).
        "sector_id": "FOUNDRY",
        "sector_definition": SectorDefinition.PROCESS_MASS_TRANSFORM.value,
        "required_for_mvs_closure": True,
        "enabled_default": True,
        "aqs_sec_required": "study",
        "notes": (
            "Smelting pots, casting, forging, rolling — notes/FOUNDRY_SIZING.md; "
            "goods-surplus train with MFG/FAB (A2 lineage)."
        ),
    },
    {
        "sector_id": "NUT",
        "sector_definition": SectorDefinition.PROCESS_MASS_TRANSFORM.value,
        "required_for_mvs_closure": True,
        "enabled_default": True,
        "aqs_sec_required": "true",
        "notes": "Nutrient dose; [catalogue-proposed] sector (AQS-SEC-001)",
    },
    {
        "sector_id": "FARM",
        "sector_definition": SectorDefinition.LIFE_SUPPORT_HABITAT.value,
        "required_for_mvs_closure": True,
        "enabled_default": True,
        "aqs_sec_required": "true",
        "notes": "Grow beds; food surplus (CAD name FARM not FRM)",
    },
    {
        "sector_id": "HAB",
        "sector_definition": SectorDefinition.LIFE_SUPPORT_HABITAT.value,
        "required_for_mvs_closure": True,
        "enabled_default": True,
        "aqs_sec_required": "true",
        "notes": "Habitation / life support",
    },
    {
        "sector_id": "CRYO",
        "sector_definition": SectorDefinition.UTILITY_HEADER.value,
        "required_for_mvs_closure": True,
        "enabled_default": True,
        "aqs_sec_required": "true",
        "notes": "Cold-box O2/N2/CO2/H2; not a generation class",
    },
    {
        "sector_id": "WTR",
        "sector_definition": SectorDefinition.UTILITY_HEADER.value,
        "required_for_mvs_closure": True,
        "enabled_default": True,
        "aqs_sec_required": "true",
        "notes": "Roof/catch/VCD/UPW (AQS-WTR-001); was WATER in early seed",
    },
    # TRR deleted 2026-10-18: terrace irrigation retired with TERRACE_IRRIG
    # (D-FARM owner ruling 2026-10-18, A-M-229) — no units, stale row.
    {
        "sector_id": "ELEC",
        "sector_definition": SectorDefinition.UTILITY_HEADER.value,
        "required_for_mvs_closure": True,
        "enabled_default": True,
        "aqs_sec_required": "true",
        "notes": (
            "Sol-Ark / ATS / RECT / MCC hub — PV, storage and FC units live here "
            "as units since the Rev AC pivot (ELEC_PV/ZNBR2/BACKUP_GEN/FUEL_CELL "
            "sector rows deleted 2026-10-18: unit-level, not sector toggles)"
        ),
    },
    {
        # Rev AC scope: heat-ladder batteries Q1-Q4 + Q4_BUS and its branches
        # (AQS-HEAT-LADDER-001; AQS-HEAT-STUDY-002 Q4 expansion).
        "sector_id": "HEAT",
        "sector_definition": SectorDefinition.UTILITY_HEADER.value,
        "required_for_mvs_closure": False,
        "enabled_default": True,
        "aqs_sec_required": "study",
        "notes": "Heat ladder batteries Q1-Q4 (AQS-HEAT-LADDER-001)",
    },
    # ELEC_PV deleted 2026-10-18: PV_ARRAY is a unit in ELEC since the Rev AC
    # pivot; the discrete PV count is carried in PV_ARRAY.params, not a sector.
    # ZNBR2 deleted 2026-10-18: the flow battery is a unit in ELEC (ESS peer at
    # unit level, see ESS_PEER_UNIT_IDS), not a sector toggle.
    {
        "sector_id": "MEOH",
        "sector_definition": SectorDefinition.ESS_ELECTROCHEMICAL.value,
        "required_for_mvs_closure": True,  # AQS-SEC-001 Rev E / A3
        "enabled_default": True,
        "aqs_sec_required": "true",
        "notes": (
            "MeOH — required ESS peer in MVS; also feeds other processes "
            "(AQS-SEC-001 A1 secondary). Sandbox off → unreclaimed_resource."
        ),
    },
    {
        "sector_id": "PUMPED_HYDRO",
        "sector_definition": SectorDefinition.ESS_GRAVITY.value,
        "required_for_mvs_closure": True,  # AQS-SEC-001 Rev E / A3
        "enabled_default": True,
        "aqs_sec_required": "true",
        "notes": (
            "Roof–catch penstock — required ESS peer in MVS (redundancy). "
            "Sandbox off → unreclaimed_resource gap (AQS-SEC-001 Rev E)."
        ),
    },
    # BACKUP_GEN deleted 2026-10-18: standby H2 genset is a unit (ELEC), not a
    # sector — no BACKUP_GEN sector units since the Rev AC pivot.
    # FUEL_CELL deleted 2026-10-18: PEM FC is a unit in ELEC (AQS-FC-001
    # lineage), not a sector toggle.
    {
        "sector_id": "GEO",
        "sector_definition": SectorDefinition.UTILITY_HEADER.value,
        "required_for_mvs_closure": False,  # AQS-SEC-001=study → treat as optional until ORC
        "enabled_default": True,
        "aqs_sec_required": "study",
        "notes": "GEO HP→Q4; ORC TBD — required left false pending study freeze",
    },
    {
        "sector_id": "DOCK",
        "sector_definition": SectorDefinition.EXPORT_DOCK.value,
        "required_for_mvs_closure": True,
        "enabled_default": True,
        "aqs_sec_required": "true",
        "notes": "North dock / freight; surplus export boundary",
    },
]

# Back-compat alias used by earlier P0 drafts
PLACEHOLDER_SECTOR_CATALOGUE = SECTOR_CATALOGUE

# MVS ESS peer set (AQS-SEC-001 Rev E / A3): redundancy is a core tenet.
# 2026-10-18 sector refresh (first-principles audit §sector definitions):
# ZNBR2 is no longer a sector — the flow battery is a unit in ELEC, so the
# sector-level peer set keeps the two ESS sectors (MEOH, PUMPED_HYDRO) and the
# third peer is tracked at unit level below. Sandbox may disable any peer;
# the solver flags each with unreclaimed_resource.
ESS_PEER_SECTOR_IDS = frozenset({"MEOH", "PUMPED_HYDRO"})
# Unit-level ESS peers living inside non-ESS sectors after the Rev AC pivot
# (ZNBR2 in ELEC). Kept alongside the sector set so redundancy checks can find
# all three peers; consumers key off ESS_PEER_SECTOR_IDS for sector toggles.
ESS_PEER_UNIT_IDS = frozenset({"ZNBR2"})
UNRECLAIMED_RESOURCE_REASON = "unreclaimed_resource"
# Deprecated (Rev C A3): kept as alias name only for export-pack archaeology.
ESS_PEER_SET_GAP_REASON = "ess_peer_set_all_disabled"


def catalogue_as_sector_rows() -> list[dict]:
    """Rows suitable for MVS ``sectors`` array."""
    out = []
    for row in SECTOR_CATALOGUE:
        out.append(
            {
                "sector_id": row["sector_id"],
                "sector_definition": row["sector_definition"],
                "enabled": row["enabled_default"],
                "required_for_mvs_closure": row["required_for_mvs_closure"],
                "notes": row["notes"],
            }
        )
    return out

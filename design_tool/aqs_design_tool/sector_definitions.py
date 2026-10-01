# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Sector Definition taxonomy — AQS-UI-001 Rev C §3.1 + AQS-SEC-001 catalogue.

Authoritative plant ``sector_id`` map: ``cad/SECTOR_DEFINITIONS.md``
(**AQS-SEC-001** Rev E). Class list remains owned by AQS-UI-001 §3.1.

Mike locks (2026-10-01):
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
    "POWER": "composite → ELEC, ELEC_PV, ZNBR2, BACKUP_GEN, FUEL_CELL, GEO, MEOH",
    "LIFE": "composite → FARM + HAB (+ WTR/TRR)",
    "OIL_GLASS": "FreeCAD group → OIL + GLASS",
    "FRM": "alias → FARM",
    "CRY": "alias → CRYO",
    "MET": "folded under MFG",
    "SLINGSHOT": "non-sector interface",
    "CORE": "building shafts — not a sector toggle",
    "WATER": "legacy seed id → WTR (AQS-SEC-001)",
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
        "sector_id": "WET",
        "sector_definition": SectorDefinition.PROCESS_MASS_TRANSFORM.value,
        "required_for_mvs_closure": True,
        "enabled_default": True,
        "aqs_sec_required": "true",
        "notes": "L-1 leach / EW / BMED; 150 kg/d wet feed (AQS-SEC-001)",
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
            "(Mike 2026-10-01 / AQS-SEC-001 A2)."
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
            "(Mike 2026-10-01 / AQS-SEC-001 A2)."
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
    {
        "sector_id": "TRR",
        "sector_definition": SectorDefinition.UTILITY_HEADER.value,
        "required_for_mvs_closure": False,
        "enabled_default": True,
        "aqs_sec_required": "false",
        "notes": "Terrace overflow / irrigation (AQS-TRR-001)",
    },
    {
        "sector_id": "ELEC",
        "sector_definition": SectorDefinition.UTILITY_HEADER.value,
        "required_for_mvs_closure": True,
        "enabled_default": True,
        "aqs_sec_required": "true",
        "notes": "Sol-Ark / ATS / RECT / MCC hub — distinct from ELEC_PV",
    },
    {
        "sector_id": "ELEC_PV",
        "sector_definition": SectorDefinition.ENERGY_PRODUCTION_ELECTRICAL.value,
        "required_for_mvs_closure": True,
        "enabled_default": True,
        "aqs_sec_required": "true",
        "notes": "PV modules; discrete PV_COUNT",
    },
    {
        "sector_id": "ZNBR2",
        "sector_definition": SectorDefinition.ESS_ELECTROCHEMICAL.value,
        "required_for_mvs_closure": True,  # AQS-SEC-001 Rev E / A3
        "enabled_default": True,
        "aqs_sec_required": "true",
        "notes": (
            "ZnBr2 flow battery — required ESS peer in MVS (redundancy). "
            "Sandbox off → unreclaimed_resource gap (AQS-SEC-001 Rev E)."
        ),
    },
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
    {
        "sector_id": "BACKUP_GEN",
        "sector_definition": SectorDefinition.ENERGY_PRODUCTION_COMBUSTION.value,
        "required_for_mvs_closure": False,
        "enabled_default": True,
        "aqs_sec_required": "false",
        "notes": "H2 genset; REQ-GEN-CONT study 2.5 kW_e",
    },
    {
        "sector_id": "FUEL_CELL",
        "sector_definition": SectorDefinition.ENERGY_PRODUCTION_ELECTROCHEMICAL.value,
        "required_for_mvs_closure": False,
        "enabled_default": True,
        "aqs_sec_required": "false",
        "notes": "PEM FC; own sector_id (AQS-FC-001 / AQS-SEC-001)",
    },
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

# MVS ESS peer set (AQS-SEC-001 Rev E / A3): all three required_for_mvs_closure.
# Sandbox may disable any; solver flags each with unreclaimed_resource.
ESS_PEER_SECTOR_IDS = frozenset({"ZNBR2", "MEOH", "PUMPED_HYDRO"})
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

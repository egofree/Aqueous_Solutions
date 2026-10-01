#!/usr/bin/env python3
# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Thin bridge: plant_flow_graph.json → legacy matplotlib PFD/SLD scripts.

Sole topology authority remains ``plant_flow_graph.json``. Scripts may read
edges/nodes here; they must not invent rates, stream IDs, or nameplates.
Null rates and TBD namespaces stay visible.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Iterable, Optional

PACKAGE_DIR = Path(__file__).resolve().parent
if str(PACKAGE_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGE_DIR.parent))

from flow_graph import GRAPH_PATH, load_graph, load_graph_dict  # noqa: E402
from flow_graph.models import FlowEdge, FlowNode, LayerTag, PlantFlowGraph  # noqa: E402


def graph_path() -> Path:
    return GRAPH_PATH


def load() -> PlantFlowGraph:
    return load_graph()


def load_raw() -> dict[str, Any]:
    return load_graph_dict()


def edges_on_layers(
    graph: Optional[PlantFlowGraph] = None,
    layers: Iterable[str] = ("elec",),
    *,
    include_intra_aisle: bool = True,
    include_placeholders: bool = True,
) -> list[FlowEdge]:
    g = graph or load()
    tags = [LayerTag(x) if not isinstance(x, LayerTag) else x for x in layers]
    return g.filter_edges(
        layers=tags,
        include_intra_aisle=include_intra_aisle,
        include_placeholders=include_placeholders,
    )


def edge_by_id(stream_id: str, graph: Optional[PlantFlowGraph] = None) -> Optional[FlowEdge]:
    g = graph or load()
    for e in g.edges:
        if e.stream_id == stream_id:
            return e
    return None


def edges_by_ids(
    stream_ids: Iterable[str], graph: Optional[PlantFlowGraph] = None
) -> list[FlowEdge]:
    wanted = set(stream_ids)
    g = graph or load()
    return [e for e in g.edges if e.stream_id in wanted]


def node_by_id(unit_id: str, graph: Optional[PlantFlowGraph] = None) -> Optional[FlowNode]:
    g = graph or load()
    return g.node_map().get(unit_id)


def format_rate(edge: FlowEdge) -> str:
    """Human rate label; never invents a value when rate is null."""
    r = edge.rate
    if r is None or r.value is None:
        unit = (r.unit if r else None) or ""
        return f"rate null{(' ' + unit) if unit else ''}".strip()
    unit = r.unit or ""
    status = r.status.value if hasattr(r.status, "value") else str(r.status)
    return f"{r.value} {unit}".strip() + (f" ({status})" if status and status != "authority" else "")


def claim_label(edge: FlowEdge) -> str:
    if edge.claim_status:
        return edge.claim_status
    if edge.namespace == "TBD":
        return "TBD — no S##"
    if edge.presence.value == "placeholder" if hasattr(edge.presence, "value") else edge.presence == "placeholder":
        return "placeholder"
    return "—"  # honest: MF table / graph has no claim_status


def meoh_mass_claim_edges(graph: Optional[PlantFlowGraph] = None) -> list[FlowEdge]:
    """S73–S82 from graph (all layers); caller filters display groups."""
    ids = [f"S{i:02d}" for i in range(73, 83)]
    return edges_by_ids(ids, graph)


def dock_export_edge(graph: Optional[PlantFlowGraph] = None) -> Optional[FlowEdge]:
    return edge_by_id("DOCK_EXPORT_TBD", graph)


def elec_ess_bridge_edges(graph: Optional[PlantFlowGraph] = None) -> dict[str, FlowEdge]:
    """Named elec/ess peers the SLD must surface (S17 + ESS peers).

    Keys are stable draw handles, not invented stream IDs.
    """
    g = graph or load()
    out: dict[str, FlowEdge] = {}
    for sid, key in (
        ("S17", "S17"),
        ("S79", "S79_MEOH_FC"),
        ("S47", "S47_GEN"),
        ("S51", "S51_FC"),
        ("S48", "S48_GEO_ORC"),
        ("IA-ESS-HYDRO-ELEC", "HYDRO_ELEC"),
        ("IA-ESS-ZNBR2-CHG", "ZNBR2_CHG"),
        ("IA-ESS-ZNBR2-DIS", "ZNBR2_DIS"),
        ("IA-ESS-MEOH-DIS", "MEOH_ESS_DIS"),
    ):
        e = edge_by_id(sid, g)
        if e is not None:
            out[key] = e
    return out


# --- Intra-aisle / hydro-dock helpers (tranche: line PFD bridge) ---

_IA_PREFIXES = {
    "ew": ("IA-EW-",),
    "rec": ("IA-REC-", "IA-WET-"),
    "glass": ("IA-GLASS-",),
    "bmed": ("IA-BMED-",),
    "polish": ("IA-POL-",),
    "oil": ("IA-OIL-",),
    "ess_znbr2": ("IA-ESS-ZNBR2-",),
    "ess_meoh": ("IA-ESS-MEOH-",),
    "ess_hydro": ("IA-ESS-HYDRO-",),
}


def ia_edges(
    aisle: str,
    graph: Optional[PlantFlowGraph] = None,
) -> list[FlowEdge]:
    """IA-* edges for a named aisle key (ew, rec, glass, bmed, polish, oil, ess_*)."""
    prefixes = _IA_PREFIXES.get(aisle)
    if not prefixes:
        raise ValueError(f"unknown aisle {aisle!r}; known: {sorted(_IA_PREFIXES)}")
    g = graph or load()
    out: list[FlowEdge] = []
    for e in g.edges:
        if any(e.stream_id.startswith(p) for p in prefixes):
            out.append(e)
    out.sort(key=lambda e: e.stream_id)
    return out


def ia_edges_by_ids(
    stream_ids: Iterable[str], graph: Optional[PlantFlowGraph] = None
) -> list[FlowEdge]:
    return edges_by_ids(stream_ids, graph)


def edge_callout(edge: FlowEdge, *, with_carries: bool = False) -> str:
    """Short overlay label: stream_id · rate; never invents values."""
    parts = [edge.stream_id, format_rate(edge)]
    if with_carries and edge.carries:
        parts.append(str(edge.carries))
    return "  ·  ".join(parts)


def ia_register_lines(
    edges: Iterable[FlowEdge], *, with_route: bool = True
) -> list[str]:
    """One line per edge for a legend box on a matplotlib sheet."""
    lines: list[str] = []
    for e in edges:
        route = f"{e.from_unit_id} → {e.to_unit_id}" if with_route else ""
        claim = claim_label(e)
        bit = f"{e.stream_id}  {route}  ·  {format_rate(e)}"
        if claim and claim not in ("—",):
            bit += f"  ·  {claim}"
        if e.carries:
            bit += f"  ·  {e.carries}"
        lines.append(bit)
    return lines


def hydro_dock_bridge_edges(
    graph: Optional[PlantFlowGraph] = None,
) -> dict[str, FlowEdge]:
    """PUMPED_HYDRO + DOCK edges for dedicated hydro_dock_pfd.

    Keys are draw handles. Rates only when graph supplies them.
    """
    g = graph or load()
    out: dict[str, FlowEdge] = {}
    for sid, key in (
        ("S21", "S21_ROOF_HAB"),
        ("S22", "S22_PENSTOCK"),
        ("S23", "S23_PUMP"),
        ("IA-ESS-HYDRO-CHG", "HYDRO_CHG"),
        ("IA-ESS-HYDRO-DIS", "HYDRO_DIS"),
        ("IA-ESS-HYDRO-ELEC", "HYDRO_ELEC"),
        ("DOCK_EXPORT_TBD", "DOCK_EXPORT"),
    ):
        e = edge_by_id(sid, g)
        if e is not None:
            out[key] = e
    return out


def znbr2_ess_bridge_edges(
    graph: Optional[PlantFlowGraph] = None,
) -> dict[str, FlowEdge]:
    g = graph or load()
    out: dict[str, FlowEdge] = {}
    for sid, key in (
        ("IA-ESS-ZNBR2-CHG", "ZNBR2_CHG"),
        ("IA-ESS-ZNBR2-DIS", "ZNBR2_DIS"),
        ("S69", "S69_BR2"),
    ):
        e = edge_by_id(sid, g)
        if e is not None:
            out[key] = e
    return out


def meoh_ess_bridge_edges(
    graph: Optional[PlantFlowGraph] = None,
) -> dict[str, FlowEdge]:
    g = graph or load()
    out: dict[str, FlowEdge] = {}
    for sid, key in (
        ("IA-ESS-MEOH-CHG", "MEOH_CHG"),
        ("IA-ESS-MEOH-DIS", "MEOH_DIS"),
        ("S79", "S79_MEOH_FC"),
    ):
        e = edge_by_id(sid, g)
        if e is not None:
            out[key] = e
    # mass claim train also available via meoh_mass_claim_edges
    return out



# --- Sector S## / IA sets for remaining line PFDs (tranche F) ---
# Only IDs that exist in plant_flow_graph.json. Never invent rates or S##.

SECTOR_EDGE_IDS: dict[str, tuple[str, ...]] = {
    "oil": (
        "IA-OIL-01", "IA-OIL-02", "IA-OIL-03", "IA-OIL-Q1", "S67", "S11",
    ),
    "wet": (
        "IA-WET-C29-01", "IA-WET-FLOAT-01", "IA-REC-01",
        "S09", "S10", "S31", "S32", "S33", "S34", "S35", "S38", "S65", "S66",
    ),
    "metal_forming": (
        "S57", "S58", "S59", "S60", "S61", "S62", "S63", "S71", "S72",
    ),
    "mfg_shop": (
        "S08", "S16", "S58", "S59", "S60", "S61",
    ),
    "hab_water": (
        "S01", "S21", "S25", "S26", "S28", "S29", "S12",
    ),
    "habitation": (
        "S02", "S12", "S14", "S15", "S21", "S26", "S78",
    ),
    "fab_upw": (
        "S01", "S09", "S27",
    ),
    "terrace": (
        "S40", "S41", "S42",
    ),
    "fuel_cell": (
        "S49", "S50", "S51", "S52", "S53",
    ),
    "backup_gen": (
        "S45", "S46", "S47",
    ),
    "geothermal": (
        "S06", "S43", "S44", "S48",
    ),
    "wafer_fab": (
        "S03", "S36", "S37", "S38", "S39",
    ),
    "fab_reagent": (
        "S31", "S32", "S33", "S34", "S35", "S36", "S37",
    ),
    "solar_cell": (
        # SOLAR_PV_CELL node is placeholder with no dedicated edges yet;
        # sheet uses shared fab UPW / KOH / etch-return peers from graph.
        "S10", "S27", "S35",
    ),
    "farm": (
        "S04", "S06", "S07", "S11", "S13", "S14", "S14X", "S15", "S20",
    ),
    "nutrient": (
        "S07", "S12", "S30",
    ),
    "cryo": (
        "S02", "S03", "S04", "S05", "S18", "S54", "S55", "S56",
        "S64", "S67", "S68", "S70",
    ),
    "vent": (
        "S19", "S56", "S62", "S65", "S66", "S71",
    ),
    # Layout / campus sheets — cross-link overlay only (not full process PFDs)
    "campus_cross": (
        "S01", "S02", "S12", "S21", "S40", "S41", "DOCK_EXPORT_TBD",
        "IA-ESS-HYDRO-ELEC",
    ),
    "building_cross": (
        "S01", "S17", "S21", "S43", "S44", "DOCK_EXPORT_TBD",
    ),
    "container_cross": (
        "S65", "S66", "S19", "IA-OIL-03", "IA-EW-04",
    ),
}


def sector_edges(
    sector: str,
    graph: Optional[PlantFlowGraph] = None,
) -> list[FlowEdge]:
    """Edges for a named process/layout sector key; missing IDs skipped."""
    ids = SECTOR_EDGE_IDS.get(sector)
    if not ids:
        raise ValueError(f"unknown sector {sector!r}; known: {sorted(SECTOR_EDGE_IDS)}")
    return edges_by_ids(ids, graph)


def sector_edge_map(
    sector: str,
    graph: Optional[PlantFlowGraph] = None,
) -> dict[str, FlowEdge]:
    return {e.stream_id: e for e in sector_edges(sector, graph)}


__all__ = [
    "GRAPH_PATH",
    "claim_label",
    "dock_export_edge",
    "edge_by_id",
    "edge_callout",
    "edges_by_ids",
    "edges_on_layers",
    "elec_ess_bridge_edges",
    "format_rate",
    "graph_path",
    "hydro_dock_bridge_edges",
    "ia_edges",
    "ia_edges_by_ids",
    "ia_register_lines",
    "load",
    "load_raw",
    "meoh_ess_bridge_edges",
    "meoh_mass_claim_edges",
    "node_by_id",
    "znbr2_ess_bridge_edges",
    "SECTOR_EDGE_IDS",
    "sector_edge_map",
    "sector_edges",
]

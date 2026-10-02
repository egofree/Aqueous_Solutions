# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Pydantic models for Aqueous plant flow graph (AQS-FLOW-GRAPH-001).

Sole typed topology authority per Mike locks:
  layered_views, full_depth_now, efd_three_layers, typed_graph_sole,
  present_plus_placeholders.
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class Presence(str, Enum):
    PRESENT = "present"
    PLACEHOLDER = "placeholder"


class LayerTag(str, Enum):
    MASS = "mass"
    ELEC = "elec"
    THERMAL = "thermal"
    ESS = "ess"


class Phase(str, Enum):
    S = "S"
    L = "L"
    G = "G"
    E = "E"
    S_L = "S/L"
    L_S = "L/S"
    G_L = "G/L"
    L_E = "L/E"
    G_E = "G/E"


class RateStatus(str, Enum):
    AUTHORITY = "authority"
    STUDY = "study"
    NULL = "null"


class Quantity(BaseModel):
    value: Optional[float] = None
    unit: Optional[str] = None
    status: RateStatus = RateStatus.NULL
    note: Optional[str] = None


class FlowNode(BaseModel):
    unit_id: str
    sector_id: str
    presence: Presence = Presence.PRESENT
    class_name: Optional[str] = Field(default=None, alias="class")
    tags: list[str] = Field(default_factory=list)
    electrical_role: Optional[str] = None
    diagram_gap: Optional[str] = None
    notes: Optional[str] = None
    # WP-Ap1 — MVS unit fields live on the graph (not a second master)
    enabled: bool = True
    continuous_kw: Optional[Quantity] = None
    modules: list[dict[str, Any]] = Field(default_factory=list)
    params: dict[str, Any] = Field(default_factory=dict)

    model_config = {"populate_by_name": True}


class FlowEdge(BaseModel):
    stream_id: str
    from_unit_id: str
    to_unit_id: str
    phase: str
    layers: list[LayerTag] = Field(default_factory=lambda: [LayerTag.MASS])
    presence: Presence = Presence.PRESENT
    carries: Optional[str] = None
    header: Optional[str] = None
    forbidden: Optional[str] = None
    claim_status: Optional[str] = None
    rate: Optional[Quantity] = None
    from_sector_id: Optional[str] = None
    to_sector_id: Optional[str] = None
    open_boundary: bool = False
    namespace: Literal["S", "IA", "TBD", "SANDBOX"] = "S"
    gap_flags: list[str] = Field(default_factory=list)
    notes: Optional[str] = None


class ViewPreset(BaseModel):
    preset_id: str
    view_mode: Literal["PFD", "MFD", "EFD"]
    layer_filter: list[LayerTag] = Field(default_factory=list)
    include_intra_aisle: bool = True
    include_placeholders: bool = True
    description: Optional[str] = None


class MvsBlock(BaseModel):
    """MVS sector/site/criteria/electrical fields living on the graph (WP-Ap1).

    ``schema_version`` here is the *projected* aqs-mvs-* version for legacy
    consumers; the graph itself keeps ``aqs-flow-graph-*`` at the root.
    """

    schema_version: str = "aqs-mvs-0.3"
    doc_id: str = "AQS-MVS-001"
    revision: str = "E-candidate"
    licence: str = "CERN-OHL-S-2.0"
    scale_m: float = 1.0
    status: str = "candidate"
    mvs_criteria: dict[str, Any] = Field(default_factory=dict)
    site: dict[str, Any] = Field(default_factory=dict)
    sectors: list[dict[str, Any]] = Field(default_factory=list)
    electrical: dict[str, Any] = Field(default_factory=dict)
    scale_rules: dict[str, Any] = Field(default_factory=dict)
    ui: dict[str, Any] = Field(default_factory=dict)
    notes: Optional[str] = None
    write_path: Optional[str] = None


class PlantFlowGraph(BaseModel):
    schema_version: str = "aqs-flow-graph-0.1"
    doc_id: str = "AQS-FLOW-GRAPH-001"
    revision: str = "B"
    licence: str = "CERN-OHL-S-2.0"
    date: str = "2026-10-01"
    sole_authority: bool = True
    locks: list[str] = Field(
        default_factory=lambda: [
            "layered_views",
            "full_depth_now",
            "efd_three_layers",
            "typed_graph_sole",
            "present_plus_placeholders",
        ]
    )
    nodes: list[FlowNode] = Field(default_factory=list)
    edges: list[FlowEdge] = Field(default_factory=list)
    view_presets: list[ViewPreset] = Field(default_factory=list)
    gaps: list[dict[str, Any]] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    # WP-Ap1 — sectors / crew / SITE_LAT / surplus flags / electrical
    mvs: Optional[MvsBlock] = None

    def node_map(self) -> dict[str, FlowNode]:
        return {n.unit_id: n for n in self.nodes}

    def filter_edges(
        self,
        *,
        layers: Optional[list[LayerTag]] = None,
        include_intra_aisle: bool = True,
        include_placeholders: bool = True,
        namespace: Optional[str] = None,
    ) -> list[FlowEdge]:
        out: list[FlowEdge] = []
        for e in self.edges:
            if not include_placeholders and e.presence == Presence.PLACEHOLDER:
                continue
            if not include_intra_aisle and e.namespace == "IA":
                continue
            if namespace and e.namespace != namespace:
                continue
            if layers is not None:
                elayers = set(e.layers)
                if not elayers.intersection(layers):
                    continue
            out.append(e)
        return out

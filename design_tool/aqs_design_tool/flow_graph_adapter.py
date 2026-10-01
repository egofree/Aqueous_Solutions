# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Adapter: plant_flow_graph.json → MVS model (WP-Ap1 sole authority).

``flow_graph/plant_flow_graph.json`` is the **single
write path** for topology (nodes/edges) and MVS fields (``mvs`` block +
node continuous_kw/modules/params/enabled).

``candidate_mvs.json`` is a **generated projection** only
(``flow_graph/export_candidate_mvs.py``) — never a competing write authority.

Preserves known gaps — never sets ``mvs_equivalent`` true from topology alone.
Placeholder / TBD rates stay null (``present_plus_placeholders``).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Optional

from .models import (
    GapModel,
    MvsModel,
    Quantity,
    RateStatus,
    StreamModel,
    UnitModel,
)
from .paths import FLOW_GRAPH_JSON, FLOW_GRAPH_PACKAGE

_DIAGRAMS = FLOW_GRAPH_PACKAGE.parent
if str(_DIAGRAMS) not in sys.path:
    sys.path.insert(0, str(_DIAGRAMS))


def load_plant_flow_graph_dict(path: Path | None = None) -> dict[str, Any]:
    p = path or FLOW_GRAPH_JSON
    if not p.is_file():
        raise FileNotFoundError(f"Plant flow graph not found: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def load_plant_flow_graph(path: Path | None = None):
    """Return validated PlantFlowGraph (lazy import of flow_graph.models)."""
    from flow_graph.models import PlantFlowGraph  # type: ignore[import-not-found]

    p = path or FLOW_GRAPH_JSON
    return PlantFlowGraph.model_validate_json(p.read_text(encoding="utf-8"))


def _map_rate_status(raw: Optional[str]) -> RateStatus:
    if raw is None or raw == "null":
        return RateStatus.TBD
    try:
        return RateStatus(raw)
    except ValueError:
        return RateStatus.STUDY


def _null_rate_kind(edge: dict[str, Any]) -> Optional[str]:
    """Label null rates explicitly — do not invent continuous dump."""
    rate = edge.get("rate") or {}
    if rate.get("value") is not None:
        return None
    if edge.get("open_boundary") or edge.get("namespace") == "TBD":
        return "open_boundary"
    if edge.get("presence") == "placeholder":
        return "study_deferred"
    if edge.get("namespace") == "IA":
        return "inventory_cycle"
    flags = edge.get("gap_flags") or []
    if any("tbd" in f.lower() or "absent" in f.lower() for f in flags):
        return "unknown"
    return "unknown"


def graph_edge_to_stream(edge: dict[str, Any]) -> StreamModel:
    rate_raw = edge.get("rate")
    rate: Optional[Quantity] = None
    if isinstance(rate_raw, dict):
        rate = Quantity(
            value=rate_raw.get("value"),
            unit=rate_raw.get("unit") or "",
            status=_map_rate_status(rate_raw.get("status")),
            note=rate_raw.get("note"),
        )
    note_parts: list[str] = []
    if edge.get("notes"):
        note_parts.append(str(edge["notes"]))
    if edge.get("gap_flags"):
        note_parts.append("gap_flags=" + ",".join(edge["gap_flags"]))
    if edge.get("presence") == "placeholder":
        note_parts.append("presence=placeholder")
    if edge.get("namespace") and edge["namespace"] != "S":
        note_parts.append(f"namespace={edge['namespace']}")
    layers = edge.get("layers") or []
    if layers:
        note_parts.append("layers=" + ",".join(layers))
    return StreamModel(
        stream_id=edge["stream_id"],
        from_unit_id=edge["from_unit_id"],
        to_unit_id=edge["to_unit_id"],
        phase=edge.get("phase") or "L",
        carries=edge.get("carries"),
        rate=rate,
        from_sector_id=edge.get("from_sector_id"),
        to_sector_id=edge.get("to_sector_id"),
        open_boundary=bool(edge.get("open_boundary", False)),
        null_rate_kind=_null_rate_kind(edge),  # type: ignore[arg-type]
        note="; ".join(note_parts) if note_parts else None,
    )


def graph_node_to_unit(node: dict[str, Any]) -> UnitModel:
    """Map graph node → UnitModel (kw/params live on the graph after WP-Ap1)."""
    params: dict[str, Any] = dict(node.get("params") or {})
    if node.get("diagram_gap"):
        params.setdefault("diagram_gap", node["diagram_gap"])
    if node.get("presence"):
        params.setdefault("presence", node["presence"])
    if node.get("notes"):
        params.setdefault("graph_notes", node["notes"])
    cw_raw = node.get("continuous_kw")
    continuous_kw: Optional[Quantity] = None
    if isinstance(cw_raw, dict):
        continuous_kw = Quantity(
            value=cw_raw.get("value"),
            unit=cw_raw.get("unit") or "kW",
            status=_map_rate_status(cw_raw.get("status")),
            note=cw_raw.get("note"),
        )
    return UnitModel(
        unit_id=node["unit_id"],
        sector_id=node["sector_id"],
        enabled=bool(node.get("enabled", True)),
        class_name=node.get("class"),
        tags=list(node.get("tags") or []),
        params=params,
        modules=list(node.get("modules") or []),
        electrical_role=node.get("electrical_role"),
        continuous_kw=continuous_kw,
    )


def topology_from_graph(
    graph: dict[str, Any] | None = None,
    *,
    include_placeholders: bool = True,
    include_intra_aisle: bool = True,
) -> tuple[list[UnitModel], list[StreamModel], list[GapModel]]:
    g = graph or load_plant_flow_graph_dict()
    units: list[UnitModel] = []
    for n in g.get("nodes", []):
        if not include_placeholders and n.get("presence") == "placeholder":
            continue
        units.append(graph_node_to_unit(n))
    streams: list[StreamModel] = []
    gaps: list[GapModel] = []
    for e in g.get("edges", []):
        if not include_placeholders and e.get("presence") == "placeholder":
            continue
        if not include_intra_aisle and e.get("namespace") == "IA":
            continue
        streams.append(graph_edge_to_stream(e))
        for flag in e.get("gap_flags") or []:
            gaps.append(
                GapModel(
                    sector_id=e.get("from_sector_id") or e.get("to_sector_id"),
                    stream_id=e["stream_id"],
                    reason="flow_graph_gap",
                    detail=flag,
                )
            )
    for gitem in g.get("gaps") or []:
        if isinstance(gitem, dict):
            gaps.append(
                GapModel(
                    sector_id=gitem.get("sector_id"),
                    stream_id=gitem.get("stream_id"),
                    reason=str(gitem.get("reason") or "flow_graph_gap"),
                    detail=gitem.get("detail") or gitem.get("notes"),
                )
            )
    return units, streams, gaps


def mvs_from_graph(
    graph: dict[str, Any] | None = None,
    *,
    include_placeholders: bool = True,
    include_intra_aisle: bool = True,
) -> MvsModel:
    """Build full MvsModel from plant_flow_graph (sole authority).

    Reads ``mvs`` block (sectors, site/crew/SITE_LAT, surplus flags,
    electrical, scale_rules, ui, schema_version) and nodes/edges.
    Does **not** set loops_closed / mvs_equivalent true.
    """
    g = graph or load_plant_flow_graph_dict()
    mvs = g.get("mvs")
    if not isinstance(mvs, dict):
        raise ValueError(
            "plant_flow_graph.json missing mvs{} — WP-Ap1 fold incomplete"
        )

    units, streams, graph_gaps = topology_from_graph(
        g,
        include_placeholders=include_placeholders,
        include_intra_aisle=include_intra_aisle,
    )

    data: dict[str, Any] = {
        "schema_version": mvs.get("schema_version", "aqs-mvs-0.3"),
        "doc_id": mvs.get("doc_id", "AQS-MVS-001"),
        "revision": mvs.get("revision", "E-candidate"),
        "licence": mvs.get("licence", g.get("licence", "CERN-OHL-S-2.0")),
        "scale_m": mvs.get("scale_m", 1.0),
        "status": mvs.get("status", "candidate"),
        "mvs_criteria": mvs.get("mvs_criteria") or {},
        "site": mvs.get("site") or {},
        "sectors": mvs.get("sectors") or [],
        "units": [u.model_dump(by_alias=True, mode="json") for u in units],
        "streams": [s.model_dump(mode="json") for s in streams],
        "electrical": mvs.get("electrical") or {},
        "scale_rules": mvs.get("scale_rules") or {},
        "ui": mvs.get("ui") or {},
        "gaps": [g.model_dump(mode="json") for g in graph_gaps],
        "unclosed_streams": [],
    }
    # Criteria locks (gap preservation)
    crit = data["mvs_criteria"]
    if isinstance(crit, dict):
        crit["loops_closed"] = False

    note = mvs.get("notes") or ""
    marker = (
        f"Loaded from AQS-FLOW-GRAPH-001 "
        f"({g.get('doc_id')} rev {g.get('revision')}; "
        f"{len(units)} units / {len(streams)} streams). "
        "Sole write path = plant_flow_graph.json (nodes/edges + mvs). "
        "candidate_mvs.json is generated projection only. "
        "Never mvs_equivalent from topology alone."
    )
    data["notes"] = f"{note}\n{marker}".strip() if note else marker
    return MvsModel.model_validate(data)


def merge_mvs_with_flow_graph(
    mvs: MvsModel | None = None,
    graph: dict[str, Any] | None = None,
    *,
    include_placeholders: bool = True,
    include_intra_aisle: bool = True,
) -> MvsModel:
    """Compatibility alias → ``mvs_from_graph`` (graph sole authority).

    ``mvs`` argument is ignored when graph has an ``mvs`` block (WP-Ap1).
    Kept so older call sites keep working without dual-write.
    """
    del mvs  # graph is authority; do not merge divergent masters
    return mvs_from_graph(
        graph,
        include_placeholders=include_placeholders,
        include_intra_aisle=include_intra_aisle,
    )


def flow_graph_meta() -> dict[str, Any]:
    g = load_plant_flow_graph_dict()
    mvs = g.get("mvs") if isinstance(g.get("mvs"), dict) else {}
    site = mvs.get("site") or {}
    return {
        "doc_id": g.get("doc_id"),
        "revision": g.get("revision"),
        "schema_version": g.get("schema_version"),
        "sole_authority": g.get("sole_authority", True),
        "locks": g.get("locks") or [],
        "path": str(FLOW_GRAPH_JSON),
        "package": str(FLOW_GRAPH_PACKAGE),
        "node_count": len(g.get("nodes") or []),
        "edge_count": len(g.get("edges") or []),
        "gap_count": len(g.get("gaps") or []),
        "mvs_block_present": bool(mvs),
        "mvs_schema_version": mvs.get("schema_version"),
        "mvs_revision": mvs.get("revision"),
        "crew": site.get("crew"),
        "site_lat_deg": site.get("site_lat_deg"),
        "sector_count": len(mvs.get("sectors") or []),
        "loops_closed": (mvs.get("mvs_criteria") or {}).get("loops_closed", False),
        "candidate_mvs_role": "generated_projection",
        "write_path": "flow_graph/plant_flow_graph.json",
        "projection_export": "flow_graph/export_candidate_mvs.py",
        "mvs_equivalent_from_topology": False,
        "projection_contract": projection_contract_status(),
        "note": (
            "Sole typed plant graph authority (WP-Ap1/Ap2). "
            "Solve/mvs/sandbox load from graph; candidate_mvs.json is export-only. "
            "Drift vs projection fails authority contract. "
            "Never claim mvs_equivalent from this adapter alone."
        ),
    }


def projection_contract_status() -> dict[str, Any]:
    """WP-Ap2: topology identity + on-disk candidate regen-check (warn payload)."""
    import sys

    pkg = FLOW_GRAPH_PACKAGE
    if str(pkg) not in sys.path:
        sys.path.insert(0, str(pkg))
    try:
        from authority_contract import check_authority_contract  # type: ignore
    except ImportError as exc:
        return {
            "ok": False,
            "error": f"authority_contract import failed: {exc}",
            "candidate_mvs_role": "generated_projection",
        }
    report = check_authority_contract(require_candidate_file=True)
    d = report.as_dict()
    # Compact for API meta
    return {
        "ok": d["ok"],
        "candidate_matches_projection": d["candidate_matches_projection"],
        "candidate_file_present": d["candidate_file_present"],
        "graph_unit_count": d["graph_unit_count"],
        "graph_stream_count": d["graph_stream_count"],
        "candidate_unit_count": d["candidate_unit_count"],
        "candidate_stream_count": d["candidate_stream_count"],
        "graph_units_hash": d["graph_units_hash"],
        "graph_streams_hash": d["graph_streams_hash"],
        "issues": d["issues"],
        "warnings": d["warnings"],
        "write_path": d["write_path"],
        "candidate_mvs_role": d["candidate_mvs_role"],
        "mvs_equivalent_from_topology": False,
    }


def assert_projection_in_sync(*, fail: bool = True) -> dict[str, Any]:
    """Raise RuntimeError if on-disk candidate_mvs drifts from graph projection."""
    status = projection_contract_status()
    if not status.get("ok"):
        issues = status.get("issues") or [{"detail": status.get("error")}]
        detail = "; ".join(
            (i.get("detail") if isinstance(i, dict) else str(i)) for i in issues
        )
        msg = f"candidate_mvs projection drift / dual master: {detail}"
        if fail:
            raise RuntimeError(msg)
    return status

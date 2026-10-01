# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""WP-Ap2 — graph sole-authority contract helpers.

Topology identity: unit_id / stream_id sets (and stream endpoints) must match
between plant_flow_graph.json and the generated candidate_mvs projection.
Hand-edited candidate_mvs drift is detectable via regen-check / hash.

Does not invent rates, streams, or nameplates. Never claims mvs_equivalent.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
HUB = ROOT.parent
GRAPH_PATH = ROOT / "plant_flow_graph.json"
CANDIDATE_PATH = (
    HUB / "design_tool" / "aqs_design_tool" / "data" / "candidate_mvs.json"
)


@dataclass
class ContractIssue:
    code: str
    detail: str


@dataclass
class ContractReport:
    ok: bool
    graph_path: str
    candidate_path: str
    graph_unit_count: int = 0
    graph_stream_count: int = 0
    candidate_unit_count: int = 0
    candidate_stream_count: int = 0
    projection_unit_count: int = 0
    projection_stream_count: int = 0
    graph_units_hash: str = ""
    graph_streams_hash: str = ""
    candidate_units_hash: str = ""
    candidate_streams_hash: str = ""
    projection_units_hash: str = ""
    projection_streams_hash: str = ""
    candidate_matches_projection: bool = False
    candidate_file_present: bool = False
    issues: list[ContractIssue] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "graph_path": self.graph_path,
            "candidate_path": self.candidate_path,
            "graph_unit_count": self.graph_unit_count,
            "graph_stream_count": self.graph_stream_count,
            "candidate_unit_count": self.candidate_unit_count,
            "candidate_stream_count": self.candidate_stream_count,
            "projection_unit_count": self.projection_unit_count,
            "projection_stream_count": self.projection_stream_count,
            "graph_units_hash": self.graph_units_hash,
            "graph_streams_hash": self.graph_streams_hash,
            "candidate_units_hash": self.candidate_units_hash,
            "candidate_streams_hash": self.candidate_streams_hash,
            "projection_units_hash": self.projection_units_hash,
            "projection_streams_hash": self.projection_streams_hash,
            "candidate_matches_projection": self.candidate_matches_projection,
            "candidate_file_present": self.candidate_file_present,
            "issues": [{"code": i.code, "detail": i.detail} for i in self.issues],
            "warnings": list(self.warnings),
            "write_path": "flow_graph/plant_flow_graph.json",
            "candidate_mvs_role": "generated_projection",
            "mvs_equivalent_from_topology": False,
        }


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _unit_id_set(nodes_or_units: list[dict[str, Any]]) -> set[str]:
    return {str(n["unit_id"]) for n in nodes_or_units if "unit_id" in n}


def _stream_endpoint_map(edges_or_streams: list[dict[str, Any]]) -> dict[str, tuple[str, str]]:
    out: dict[str, tuple[str, str]] = {}
    for e in edges_or_streams:
        sid = str(e["stream_id"])
        out[sid] = (str(e["from_unit_id"]), str(e["to_unit_id"]))
    return out


def _hash_sorted_ids(ids: set[str]) -> str:
    return _sha256_text("\n".join(sorted(ids)))


def _hash_endpoints(endpoints: dict[str, tuple[str, str]]) -> str:
    lines = [f"{sid}|{fr}|{to}" for sid, (fr, to) in sorted(endpoints.items())]
    return _sha256_text("\n".join(lines))


def topology_identity(
    graph: dict[str, Any],
    candidate: dict[str, Any],
    *,
    label: str = "candidate",
) -> list[ContractIssue]:
    """Require matching unit_id / stream_id sets and stream endpoints."""
    issues: list[ContractIssue] = []
    g_units = _unit_id_set(graph.get("nodes") or [])
    c_units = _unit_id_set(candidate.get("units") or [])
    only_g = sorted(g_units - c_units)
    only_c = sorted(c_units - g_units)
    if only_g or only_c:
        issues.append(
            ContractIssue(
                "unit_id_set_mismatch",
                f"{label} unit_id diverge vs graph: "
                f"only_in_graph={only_g[:20]} only_in_{label}={only_c[:20]} "
                f"(counts graph={len(g_units)} {label}={len(c_units)})",
            )
        )

    g_eps = _stream_endpoint_map(graph.get("edges") or [])
    c_eps = _stream_endpoint_map(candidate.get("streams") or [])
    g_sids = set(g_eps)
    c_sids = set(c_eps)
    only_gs = sorted(g_sids - c_sids)
    only_cs = sorted(c_sids - g_sids)
    if only_gs or only_cs:
        issues.append(
            ContractIssue(
                "stream_id_set_mismatch",
                f"{label} stream_id diverge vs graph: "
                f"only_in_graph={only_gs[:20]} only_in_{label}={only_cs[:20]} "
                f"(counts graph={len(g_sids)} {label}={len(c_sids)})",
            )
        )
    shared = g_sids & c_sids
    endpoint_mismatches: list[str] = []
    for sid in sorted(shared):
        if g_eps[sid] != c_eps[sid]:
            endpoint_mismatches.append(
                f"{sid}: graph={g_eps[sid]} {label}={c_eps[sid]}"
            )
            if len(endpoint_mismatches) >= 20:
                break
    if endpoint_mismatches:
        issues.append(
            ContractIssue(
                "stream_endpoint_mismatch",
                f"{label} stream endpoints diverge vs graph: {endpoint_mismatches}",
            )
        )
    return issues


def check_authority_contract(
    *,
    graph_path: Path | None = None,
    candidate_path: Path | None = None,
    require_candidate_file: bool = True,
) -> ContractReport:
    """Full WP-Ap2 check: graph ↔ live projection ↔ on-disk candidate_mvs."""
    from export_candidate_mvs import project_candidate_mvs  # local sibling

    gp = graph_path or GRAPH_PATH
    cp = candidate_path or CANDIDATE_PATH
    report = ContractReport(
        ok=True,
        graph_path=str(gp),
        candidate_path=str(cp),
    )

    if not gp.is_file():
        report.ok = False
        report.issues.append(
            ContractIssue("graph_missing", f"plant_flow_graph missing: {gp}")
        )
        return report

    graph = json.loads(gp.read_text(encoding="utf-8"))
    if not isinstance(graph.get("mvs"), dict):
        report.ok = False
        report.issues.append(
            ContractIssue(
                "mvs_block_missing",
                "plant_flow_graph.json missing mvs{} — WP-Ap1 incomplete",
            )
        )
        return report

    g_units = _unit_id_set(graph.get("nodes") or [])
    g_eps = _stream_endpoint_map(graph.get("edges") or [])
    report.graph_unit_count = len(g_units)
    report.graph_stream_count = len(g_eps)
    report.graph_units_hash = _hash_sorted_ids(g_units)
    report.graph_streams_hash = _hash_endpoints(g_eps)

    projection = project_candidate_mvs(graph)
    p_units = _unit_id_set(projection.get("units") or [])
    p_eps = _stream_endpoint_map(projection.get("streams") or [])
    report.projection_unit_count = len(p_units)
    report.projection_stream_count = len(p_eps)
    report.projection_units_hash = _hash_sorted_ids(p_units)
    report.projection_streams_hash = _hash_endpoints(p_eps)

    for issue in topology_identity(graph, projection, label="live_projection"):
        report.issues.append(issue)

    report.candidate_file_present = cp.is_file()
    if not cp.is_file():
        msg = f"candidate_mvs.json missing: {cp} — run export_candidate_mvs.py"
        if require_candidate_file:
            report.issues.append(ContractIssue("candidate_missing", msg))
        else:
            report.warnings.append(msg)
    else:
        candidate = json.loads(cp.read_text(encoding="utf-8"))
        c_units = _unit_id_set(candidate.get("units") or [])
        c_eps = _stream_endpoint_map(candidate.get("streams") or [])
        report.candidate_unit_count = len(c_units)
        report.candidate_stream_count = len(c_eps)
        report.candidate_units_hash = _hash_sorted_ids(c_units)
        report.candidate_streams_hash = _hash_endpoints(c_eps)

        for issue in topology_identity(graph, candidate, label="on_disk_candidate"):
            report.issues.append(issue)

        # Regen-check: on-disk must match fresh projection topology hashes
        match = (
            report.candidate_units_hash == report.projection_units_hash
            and report.candidate_streams_hash == report.projection_streams_hash
        )
        report.candidate_matches_projection = match
        if not match:
            report.issues.append(
                ContractIssue(
                    "projection_drift",
                    "on-disk candidate_mvs.json topology hashes diverge from "
                    "fresh export_candidate_mvs projection — hand-edit or stale "
                    "file; regenerate via flow_graph/export_candidate_mvs.py "
                    f"(units {report.candidate_units_hash[:12]}… vs "
                    f"{report.projection_units_hash[:12]}…; streams "
                    f"{report.candidate_streams_hash[:12]}… vs "
                    f"{report.projection_streams_hash[:12]}…)",
                )
            )

    # Projection must never flip mvs_equivalent true
    crit = (projection.get("mvs_criteria") or {}).get("self_copy") or {}
    if crit.get("mvs_equivalent") is True:
        report.issues.append(
            ContractIssue(
                "mvs_equivalent_true",
                "projection claims mvs_equivalent=true — forbidden while incomplete",
            )
        )

    report.ok = len(report.issues) == 0
    return report


def assert_authority_contract(**kwargs: Any) -> ContractReport:
    report = check_authority_contract(**kwargs)
    if not report.ok:
        details = "; ".join(f"{i.code}: {i.detail}" for i in report.issues)
        raise AssertionError(f"authority contract failed: {details}")
    return report

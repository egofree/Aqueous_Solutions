# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""WP-Ap2 regression: topology identity graph ↔ candidate_mvs projection.

Runnable:
  cd Diagrams/aqueous_diagrams/flow_graph
  python3 -m pytest test_authority_contract.py -q
  python3 check_authority_contract.py
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from authority_contract import (  # noqa: E402
    CANDIDATE_PATH,
    GRAPH_PATH,
    assert_authority_contract,
    check_authority_contract,
    topology_identity,
)
from export_candidate_mvs import project_candidate_mvs  # noqa: E402


@pytest.fixture(scope="module")
def graph() -> dict:
    assert GRAPH_PATH.is_file(), f"missing {GRAPH_PATH}"
    return json.loads(GRAPH_PATH.read_text(encoding="utf-8"))


def test_graph_has_mvs_block(graph: dict) -> None:
    assert isinstance(graph.get("mvs"), dict)
    assert graph["mvs"].get("schema_version")


def test_live_projection_topology_matches_graph(graph: dict) -> None:
    projection = project_candidate_mvs(graph)
    issues = topology_identity(graph, projection, label="live_projection")
    assert issues == [], [i.detail for i in issues]
    assert len(projection["units"]) == len(graph["nodes"])
    assert len(projection["streams"]) == len(graph["edges"])


def test_on_disk_candidate_matches_graph_and_projection(graph: dict) -> None:
    report = check_authority_contract()
    assert report.ok, [i.detail for i in report.issues]
    assert report.candidate_matches_projection
    assert report.graph_unit_count == report.candidate_unit_count
    assert report.graph_stream_count == report.candidate_stream_count
    assert report.graph_units_hash == report.candidate_units_hash
    assert report.graph_streams_hash == report.candidate_streams_hash


def test_assert_authority_contract_green() -> None:
    report = assert_authority_contract()
    assert report.ok


def test_divergent_master_detected(graph: dict, tmp_path: Path) -> None:
    """Hand-edited candidate with extra unit must fail contract."""
    projection = project_candidate_mvs(graph)
    drifted = copy.deepcopy(projection)
    drifted["units"].append(
        {
            "unit_id": "FAKE_DIVERGENT_UNIT",
            "sector_id": "WET",
            "enabled": True,
            "class": None,
            "tags": [],
            "params": {},
            "modules": [],
            "electrical_role": None,
            "continuous_kw": None,
        }
    )
    bad = tmp_path / "candidate_mvs.json"
    bad.write_text(json.dumps(drifted, indent=2) + "\n", encoding="utf-8")
    report = check_authority_contract(candidate_path=bad)
    assert not report.ok
    codes = {i.code for i in report.issues}
    assert "unit_id_set_mismatch" in codes or "projection_drift" in codes


def test_projection_never_sets_mvs_equivalent_true(graph: dict) -> None:
    projection = project_candidate_mvs(graph)
    crit = projection.get("mvs_criteria") or {}
    sc = crit.get("self_copy") or {}
    assert crit.get("loops_closed") is not True
    assert sc.get("mvs_equivalent") is not True


def test_candidate_path_expected() -> None:
    assert CANDIDATE_PATH.name == "candidate_mvs.json"
    assert "design_tool" in str(CANDIDATE_PATH)

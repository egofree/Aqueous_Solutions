# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Aqueous typed plant flow graph — sole topology authority (AQS-FLOW-GRAPH-001)."""
from __future__ import annotations

import json
from pathlib import Path

from .models import PlantFlowGraph

PACKAGE_DIR = Path(__file__).resolve().parent
GRAPH_PATH = PACKAGE_DIR / "plant_flow_graph.json"


def load_graph(path: Path | None = None) -> PlantFlowGraph:
    p = path or GRAPH_PATH
    return PlantFlowGraph.model_validate_json(p.read_text())


def load_graph_dict(path: Path | None = None) -> dict:
    p = path or GRAPH_PATH
    return json.loads(p.read_text())

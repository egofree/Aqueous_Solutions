# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Filesystem paths for the design-tool package (sandbox-only mutations)."""

from __future__ import annotations

from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent
TOOL_ROOT = PACKAGE_ROOT.parent
DATA_DIR = PACKAGE_ROOT / "data"
SCHEMA_DIR = PACKAGE_ROOT / "schema"
EXPORTS_DIR = TOOL_ROOT / "exports"
CANDIDATE_MVS_PATH = DATA_DIR / "candidate_mvs.json"
SCHEMA_PATH = SCHEMA_DIR / "mvs.schema.json"

# In-memory / on-disk sandbox store (never under locked cad/ MVS docs)
SANDBOX_STORE_DIR = TOOL_ROOT / ".sandbox_store"

# Typed plant flow graph (AQS-FLOW-GRAPH-001) — sole topology authority
FLOW_GRAPH_PACKAGE = TOOL_ROOT.parent / "flow_graph"
FLOW_GRAPH_JSON = FLOW_GRAPH_PACKAGE / "plant_flow_graph.json"
FLOW_GRAPH_VIEWS = FLOW_GRAPH_PACKAGE / "views"

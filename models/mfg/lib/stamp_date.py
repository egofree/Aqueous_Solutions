# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Deterministic stamp dates for the manufacturing-model outputs.

A generated output must not carry the wall-clock day of the run: regenerating
the same inputs on a different day then changes the tracked file, which
breaks regen idempotency and the day-independence of the check suite. The
stamp is the plant graph's own date field (``flow_graph/plant_flow_graph.json``
``date``), which changes only when the graph itself is deliberately
re-stamped by its owner writer. A latest-commit-date rule was rejected: the
stamp commit itself touches the models tree and would move the stamp on its
own commit, failing idempotency on the first run after every stamp change.
When the graph file is unavailable, the latest commit date of the
section-7 inputs is the fallback; it is fixed by the inputs either way, so
two runs over the same tree produce identical bytes on any day.
"""
import json
import os
import subprocess

_LIB = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_LIB)))
_GRAPH = os.path.join(ROOT, "flow_graph", "plant_flow_graph.json")

_INPUTS = [
    "flow_graph/plant_flow_graph.json",
    "flow_graph/placement_seed.json",
    "models/mfg/tracker.py",
    "docs-authority/duties",
    "docs-authority/nozzles",
    "models/mfg",
    "cad/stl",
]


def deterministic_date():
    """The YYYY-MM-DD stamp of the current inputs (no wall clock)."""
    try:
        day = str(json.load(open(_GRAPH)).get("date") or "")
        if day:
            return day
    except Exception:
        pass
    try:
        out = subprocess.run(
            ["git", "-C", ROOT, "log", "-1", "--format=%cs", "--", *_INPUTS],
            capture_output=True, text=True, timeout=120, check=True)
        day = out.stdout.strip()
        if day:
            return day
    except Exception:
        pass
    return "1970-01-01"

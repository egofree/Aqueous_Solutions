# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Deterministic stamp dates for the manufacturing-model outputs.

A generated output must not carry the wall-clock day of the run: regenerating
the same inputs on a different day then changes the tracked file, which
breaks regen idempotency and the day-independence of the check suite. The
stamp is instead the date of the inputs' own state: the latest commit date
among the section-7 generation inputs (the plant graph, the placement seed,
the tracker, the duty pages, the nozzle schedules, the models tree and the
cad/stl registry), read with ``git log -1 --format=%cs``. When git is not
available (an exported tree), the plant graph's own ``date`` field is used.
Both are fixed by the inputs, so two runs over the same tree produce identical
bytes on any day.
"""
import json
import os
import subprocess

_LIB = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_LIB)))  # models/mfg/lib -> repo
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
        out = subprocess.run(
            ["git", "-C", ROOT, "log", "-1", "--format=%cs", "--", *_INPUTS],
            capture_output=True, text=True, timeout=120, check=True)
        day = out.stdout.strip()
        if day:
            return day
    except Exception:
        pass
    try:
        return str(json.load(open(_GRAPH)).get("date") or "1970-01-01")
    except Exception:
        return "1970-01-01"

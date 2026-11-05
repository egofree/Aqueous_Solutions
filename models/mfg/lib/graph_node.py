# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Shared graph-node reader for the manufacturing-model builders.

The plant graph (``flow_graph/plant_flow_graph.json``) is the sole topology
authority. A builder takes its envelope, revision, nozzle schedule and
design block from the graph node instead of the ``models/mfg/<UNIT>/params.json``
copy, which the tracker writes as a build report. ``as_params()`` returns a
dict with the W2 keys the builders already read (``unit_id``, ``graph_revision``,
``size_mm``, ``nozzles``, ``design``, ``size_basis``), so the converted read is
a drop-in for ``P = json.loads((HERE / "params.json").read_text())``. Params.json
is not written through this reader: builders that persist builder-owned blocks
keep their own params.json write-back; builders that draw only from the graph
write their build report through the tracker.
"""
import csv
import json
import os

_LIB = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_LIB)))
_GRAPH = os.path.join(ROOT, "flow_graph", "plant_flow_graph.json")


def _load_graph():
    return json.load(open(_GRAPH))


def _node_size(params):
    """The claimed envelope of a node, in the precedence the tracker uses."""
    env = params.get("envelope") or {}
    sizing = params.get("sizing") or {}
    return env.get("size_mm") or sizing.get("size_mm") or params.get("size_mm")


def _size_basis(params):
    env = params.get("envelope") or {}
    sizing = params.get("sizing") or {}
    return env.get("basis") or params.get("size_note") or sizing.get("basis")


def _nozzle_rows(unit):
    """The duty section 4 nozzle schedule rows for a unit, or None when absent."""
    path = os.path.join(ROOT, "docs-authority", "nozzles", unit + ".csv")
    if not os.path.exists(path):
        return None
    with open(path) as fh:
        rows = []
        for r in csv.DictReader(fh):
            try:
                height = float(r["height_mm"])
                height = int(height) if height == int(height) else height
            except (KeyError, TypeError, ValueError):
                height = None
            rows.append({"tag": r.get("tag"), "size": r.get("size"),
                         "rating": r.get("rating"), "service": r.get("service"),
                         "face": r.get("face"), "height_mm": height})
        return rows


class GraphNode:
    """One plant-graph node's manufacturing-model facts."""

    def __init__(self, unit, node, graph):
        self.unit = unit
        self.node = node
        self.graph_revision = graph.get("revision")
        self.params = node.get("params") or {}
        self.size_mm = _node_size(self.params)
        self.size_basis = _size_basis(self.params)
        self.nozzles = _nozzle_rows(unit)
        self.design = self.params.get("design") or {}
        self.class_ = node.get("class")
        self.sector = node.get("sector_id")
        self.compressor_design = self.params.get("compressor_design")
        self.design_kPa = self.params.get("design_kPa")
        self.relief_mm = self.params.get("relief_mm")
        self.internals = node.get("internals") or self.params.get("internals") or "none"
        sec3 = (self.params.get("sec3_material") or {}).get("mat")
        self.material = sec3

    def as_params(self):
        """A dict with the W2 keys the builders read from params.json."""
        return {
            "unit_id": self.unit,
            "graph_revision": self.graph_revision,
            "size_mm": self.size_mm,
            "size_basis": self.size_basis,
            "class": self.class_,
            "sector": self.sector,
            "design_kPa": self.design_kPa,
            "relief_mm": self.relief_mm,
            "compressor_design": self.compressor_design,
            "nozzles": self.nozzles or [],
            "material": self.material,
            "internals": self.internals,
            "design": self.design,
        }


def graph_node(unit):
    """The graph node for a unit id (present or placeholder)."""
    g = _load_graph()
    node = next((n for n in g["nodes"] if n["unit_id"] == unit), None)
    if node is None:
        raise KeyError(f"{unit}: no graph node")
    return GraphNode(unit, node, g)

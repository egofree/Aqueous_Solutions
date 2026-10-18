# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Nested system tree (U4a tree-of-trees) over AQS-FLOW-GRAPH-001.

Structure (owner-confirmed decomposition, 2026-10-18):

    sector root (the 19 mvs.sectors ids)
      -> train (level 1, ``*-train``)
        -> subsystem (level 2, only where a real sub-train exists)
          -> unit leaf (carries ``unit_id``; a leaf's id ends in its unit_id)

TechTree patterns kept: dotted ids derived from the path, single-parent
containment, and cross-cutting concerns OUTSIDE the tree — headers,
junctions, and heat/electrical edges live inside the sector that owns
them and join the train they serve; they are never shared children.

The leaf set is the graph unit set exactly, in both directions.  The
graph stays the sole authority: the tree only partitions it.  U4a drift
guard: ``pytest flow_graph/param/test_system_tree.py`` fails when a
graph node is added/removed without a matching tree edit.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Optional

from pydantic import BaseModel, Field

try:  # package import (flow_graph.system_tree)
    from . import load_graph_dict as _load_graph_dict
except ImportError:  # pragma: no cover - flat import (flow_graph/ on sys.path)
    from flow_graph import load_graph_dict as _load_graph_dict  # type: ignore

SCHEMA_VERSION = "aqs-system-tree-0.1"
DOC_ID = "AQS-SYS-TREE-001"
TREE_PATH = Path(__file__).resolve().parent / "system_tree.yaml"

# Aggregate "worst presence" ranking, least real first: a retired unit
# (traceability only, no rate) is worse than a placeholder (future unit),
# which is worse than study depth, which is worse than present.
PRESENCE_RANK: dict[str, int] = {"retired": 0, "placeholder": 1, "study": 2, "present": 3}


class TreeValidationError(ValueError):
    """Raised when the tree is structurally broken or drifts from the graph."""

    def __init__(self, issues: list[str]) -> None:
        self.issues = list(issues)
        super().__init__("system tree invalid: " + "; ".join(self.issues))


class TreeNode(BaseModel):
    """One node of the containment tree.

    ``level`` and ``children`` are derived (never hand-authored): level is
    the parent-chain depth, children the declared child ids in file order.
    """

    id: str
    parent: Optional[str] = None
    level: int = 0
    children: list[str] = Field(default_factory=list)
    unit_id: Optional[str] = None
    description: Optional[str] = None


def _graph_payload(
    graph: dict[str, Any] | str | Path | None,
) -> tuple[list[dict[str, Any]], list[str]]:
    """Return (nodes, sector_ids) from a graph dict/path (None=live graph)."""
    g: dict[str, Any]
    if graph is None:
        g = _load_graph_dict()
    elif isinstance(graph, dict):
        g = graph
    else:
        g = json.loads(Path(graph).read_text(encoding="utf-8"))
    sectors = [
        s.get("sector_id")
        for s in ((g.get("mvs") or {}).get("sectors") or [])
        if s.get("sector_id")
    ]
    return list(g.get("nodes") or []), sectors


class SystemTree(BaseModel):
    schema_version: str = SCHEMA_VERSION
    doc_id: str = DOC_ID
    revision: str = "A"
    date: str = "2026-10-18"
    licence: str = "CERN-OHL-S-2.0"
    notes: Optional[str] = None
    # unit_id -> legacy graph sector_id allowed to sit under a different
    # root (WET is the pre-rename DIGESTER, graph Rev X sector pivot).
    sector_exceptions: dict[str, str] = Field(default_factory=dict)
    nodes: list[TreeNode] = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        self._by_id: dict[str, TreeNode] = {}
        self.reindex()

    # ------------------------------------------------------------------
    # indexing / structural integrity
    # ------------------------------------------------------------------

    def reindex(self) -> list[str]:
        """Rebuild levels + children; return structural issues (empty=ok)."""
        issues: list[str] = []
        by_id: dict[str, TreeNode] = {}
        for n in self.nodes:
            if n.id in by_id:
                issues.append(f"duplicate node id '{n.id}'")
            by_id[n.id] = n

        for n in self.nodes:
            if n.parent is not None and n.parent not in by_id:
                issues.append(f"node '{n.id}' references unknown parent '{n.parent}'")
            if n.parent == n.id:
                issues.append(f"node '{n.id}' parents itself")

        for n in self.nodes:
            n.children = []
        if not issues:
            for n in self.nodes:
                if n.parent is not None:
                    by_id[n.parent].children.append(n.id)

        # levels via parent-chain walk with cycle detection
        for n in self.nodes:
            seen: set[str] = set()
            cur = n
            level = 0
            while cur.parent is not None:
                if cur.id in seen:
                    issues.append(f"cycle detected at '{cur.id}'")
                    break
                seen.add(cur.id)
                nxt = by_id.get(cur.parent)
                if nxt is None:
                    break
                cur = nxt
                level += 1
            n.level = level

        # dotted-id derivation + leaf purity
        for n in self.nodes:
            if n.parent is None:
                if "." in n.id:
                    issues.append(
                        f"root id '{n.id}' must be a bare sector id (no dots)"
                    )
                continue
            prefix, _, last = n.id.rpartition(".")
            if not last or prefix != n.parent:
                issues.append(
                    f"node id '{n.id}' does not derive from parent '{n.parent}'"
                )
            if n.unit_id is not None:
                if last != n.unit_id:
                    issues.append(
                        f"leaf '{n.id}' must end in its unit_id '{n.unit_id}'"
                    )
                if n.children:
                    issues.append(f"unit leaf '{n.id}' must not carry children")

        self._by_id = by_id
        return issues

    def node(self, node_id: str) -> TreeNode:
        try:
            return self._by_id[node_id]
        except KeyError:
            raise KeyError(f"unknown tree node '{node_id}'") from None

    # ------------------------------------------------------------------
    # loading
    # ------------------------------------------------------------------

    @classmethod
    def from_nodes(
        cls, nodes: list[TreeNode] | list[dict[str, Any]], **meta: Any
    ) -> "SystemTree":
        """Build without raising; call reindex()/validate() for issues."""
        typed = [n if isinstance(n, TreeNode) else TreeNode(**n) for n in nodes]
        return cls(nodes=typed, **meta)

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> "SystemTree":
        meta = {
            k: raw[k]
            for k in (
                "schema_version",
                "doc_id",
                "revision",
                "date",
                "licence",
                "notes",
                "sector_exceptions",
            )
            if k in raw
        }
        return cls.from_nodes(raw.get("nodes") or [], **meta)

    # ------------------------------------------------------------------
    # validation against the graph (drift guard)
    # ------------------------------------------------------------------

    def _graph_issues(
        self, graph: dict[str, Any] | str | Path | None
    ) -> list[str]:
        issues: list[str] = []
        gnodes, sector_ids = _graph_payload(graph)
        graph_units = {n["unit_id"] for n in gnodes}
        sector_of = {n["unit_id"]: n.get("sector_id") for n in gnodes}

        leaves = [n for n in self.nodes if n.unit_id is not None]
        tree_units = {n.unit_id for n in leaves}
        placed: dict[str, str] = {}
        for n in leaves:
            assert n.unit_id is not None
            if n.unit_id in placed:
                issues.append(
                    f"unit '{n.unit_id}' assigned at two leaves "
                    f"('{placed[n.unit_id]}' and '{n.id}')"
                )
            placed[n.unit_id] = n.id

        missing = sorted(graph_units - tree_units)
        extra = sorted(tree_units - graph_units)
        if missing:
            issues.append(
                f"graph units missing from tree ({len(missing)}): "
                + ", ".join(missing)
            )
        if extra:
            issues.append(
                f"tree leaves not in graph ({len(extra)}): " + ", ".join(extra)
            )

        roots = [n.id for n in self.nodes if n.parent is None]
        bad_roots = sorted(r for r in roots if r not in sector_ids)
        if bad_roots:
            issues.append(
                f"roots that are not mvs sector ids: {', '.join(bad_roots)}"
            )
        no_root = sorted(set(sector_ids) - set(roots))
        if no_root:
            issues.append(f"sectors with no tree root: {', '.join(no_root)}")

        # sector containment: a unit sits under its graph sector's root,
        # except where sector_exceptions records a pre-rename legacy sector.
        for n in leaves:
            assert n.unit_id is not None
            sec = sector_of.get(n.unit_id)
            if sec is None:
                continue  # already reported as a leaf not in graph
            root = n.id.split(".", 1)[0]
            if root != sec and self.sector_exceptions.get(n.unit_id) != sec:
                issues.append(
                    f"unit '{n.unit_id}' (graph sector {sec}) placed under "
                    f"root '{root}' without a sector_exceptions entry"
                )
        return issues

    def validate(
        self, graph: dict[str, Any] | str | Path | None = None
    ) -> dict[str, Any]:
        """Validate structure + graph agreement; raise or return a report.

        Checks: (a) leaf set == graph unit set exactly, both directions;
        (b) every root is an mvs sector id (and every sector has a root);
        (c) parents resolve and chains are cycle-free; (d) dotted ids
        derive from the path; plus unit-leaf purity and single assignment,
        and sector-root containment with recorded exceptions.
        """
        issues = self.reindex() + self._graph_issues(graph)
        if issues:
            raise TreeValidationError(issues)
        gnodes, sector_ids = _graph_payload(graph)
        leaves = [n for n in self.nodes if n.unit_id is not None]
        return {
            "ok": True,
            "doc_id": self.doc_id,
            "revision": self.revision,
            "nodes": len(self.nodes),
            "leaves": len(leaves),
            "graph_units": len({n["unit_id"] for n in gnodes}),
            "roots": len([n for n in self.nodes if n.parent is None]),
            "sector_count": len(sector_ids),
            "stats": self.stats(),
        }

    # ------------------------------------------------------------------
    # queries
    # ------------------------------------------------------------------

    def resolve_units(self, node_id: str) -> set[str]:
        """Unit ids under ``node_id`` (inclusive). KeyError on unknown node."""
        self.node(node_id)  # KeyError check
        out: set[str] = set()
        stack = [node_id]
        while stack:
            n = self.node(stack.pop())
            if n.unit_id is not None:
                out.add(n.unit_id)
            stack.extend(n.children)
        return out

    def unit_leaf_map(self) -> dict[str, str]:
        """unit_id -> leaf node id."""
        return {n.unit_id: n.id for n in self.nodes if n.unit_id is not None}

    def aggregate(
        self,
        unit_ids: Iterable[str],
        graph: dict[str, Any] | str | Path | None = None,
    ) -> dict[str, Any]:
        """Aggregate a unit set: count, kW sum from continuous_kw, worst presence.

        ``kw_sum`` adds every continuous_kw value whose unit is blank or kW;
        ``presence`` is the least-mature presence in the set (retired <
        placeholder < study < present); None for an empty set.
        """
        gnodes, _ = _graph_payload(graph)
        node_by_unit = {n["unit_id"]: n for n in gnodes}
        ids = set(unit_ids)
        kw_sum = 0.0
        kw_count = 0
        worst: Optional[str] = None
        missing: list[str] = []
        for uid in sorted(ids):
            n = node_by_unit.get(uid)
            if n is None:
                missing.append(uid)
                continue
            cw = n.get("continuous_kw")
            val: Optional[float] = None
            unit: Optional[str] = "kW"
            if isinstance(cw, dict):
                val = cw.get("value")
                unit = cw.get("unit") or "kW"
            elif isinstance(cw, (int, float)) and not isinstance(cw, bool):
                val = float(cw)  # Rev AC graph shorthand: bare number = kW study
            if val is not None and (unit or "kW") == "kW":
                kw_sum += float(val)
                kw_count += 1
            presence = str(n.get("presence") or "present")
            if worst is None or PRESENCE_RANK.get(
                presence, 3
            ) < PRESENCE_RANK.get(worst, 3):
                worst = presence
        return {
            "count": len(ids),
            "kw_sum": round(kw_sum, 6),
            "kw_count": kw_count,
            "presence": worst,
            "unknown_unit_ids": missing,
        }

    def stats(self) -> dict[str, Any]:
        """Tree shape summary: nodes per level, trains, subsystems, leaves."""
        by_level: dict[int, int] = {}
        for n in self.nodes:
            by_level[n.level] = by_level.get(n.level, 0) + 1
        leaves = [n for n in self.nodes if n.unit_id is not None]
        subsystems = [n for n in self.nodes if n.unit_id is None and n.level >= 2]
        units_per_root: dict[str, int] = {}
        for n in leaves:
            root = n.id.split(".", 1)[0]
            units_per_root[root] = units_per_root.get(root, 0) + 1
        return {
            "nodes": len(self.nodes),
            "by_level": dict(sorted(by_level.items())),
            "roots": by_level.get(0, 0),
            "trains": by_level.get(1, 0),
            "subsystems": len(subsystems),
            "leaves": len(leaves),
            "units_per_root": dict(sorted(units_per_root.items())),
        }


def load(path: Path | str | None = None) -> SystemTree:
    """Load system_tree.yaml; raise TreeValidationError on broken structure."""
    import yaml

    p = Path(path) if path is not None else TREE_PATH
    raw = yaml.safe_load(p.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or not raw.get("nodes"):
        raise TreeValidationError([f"{p}: no nodes found"])
    tree = SystemTree.from_raw(raw)
    issues = tree.reindex()
    if issues:
        raise TreeValidationError(issues)
    return tree

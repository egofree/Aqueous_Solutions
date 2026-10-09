#!/usr/bin/env python3
"""Loop partition and closure test.

Tarjan finds the strongly connected components. A component of one unit is not a loop.
Johnson lists the elementary cycles inside a component. The closure test is a balance
on the cut around each component: mass or energy entering equals mass or energy leaving,
and every unit inside balances. loops_closed stays false unless every component passes.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GRAPH = ROOT / "plant_flow_graph.json"


def tarjan(nodes: list[str], edges: list[tuple[str, str]]) -> list[list[str]]:
    adj: dict[str, list[str]] = defaultdict(list)
    for a, b in edges:
        adj[a].append(b)
    index: dict[str, int] = {}
    low: dict[str, int] = {}
    stack: list[str] = []
    on: set[str] = set()
    comps: list[list[str]] = []
    i = 0

    def strong(v: str) -> None:
        nonlocal i
        index[v] = low[v] = i
        i += 1
        stack.append(v)
        on.add(v)
        for w in adj[v]:
            if w not in index:
                strong(w)
                low[v] = min(low[v], low[w])
            elif w in on:
                low[v] = min(low[v], index[w])
        if low[v] == index[v]:
            comp = []
            while True:
                w = stack.pop()
                on.remove(w)
                comp.append(w)
                if w == v:
                    break
            comps.append(comp)

    for v in nodes:
        if v not in index:
            strong(v)
    return comps


def johnson(nodes: list[str], edges: list[tuple[str, str, str]], limit: int) -> list[list[str]]:
    """Elementary cycles, blocked after use. Stops at limit."""
    adj: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for a, b, s in edges:
        adj[a].append((b, s))
    order = {n: i for i, n in enumerate(sorted(nodes))}
    cycles: list[list[str]] = []

    def walk(start: str, v: str, path: list[str], seen: set[str]) -> None:
        if len(cycles) >= limit:
            return
        for w, sid in adj[v]:
            if len(cycles) >= limit:
                return
            if w == start and path:
                cycles.append(path + [sid])
            elif w not in seen and order.get(w, -1) > order[start]:
                seen.add(w)
                walk(start, w, path + [sid], seen)
                seen.remove(w)

    for n in sorted(nodes, key=lambda x: order[x]):
        if len(cycles) >= limit:
            break
        walk(n, n, [], {n})
    return cycles


def load():
    g = json.loads(GRAPH.read_text())
    by = defaultdict(list)
    for e in g["edges"]:
        if e["presence"] != "present":
            continue
        for layer in e.get("layers") or ["none"]:
            by[layer].append(e)
    return g, by


def node_gap(edges, uid, unit):
    inn = out = 0.0
    for e in edges:
        if e["rate"]["unit"] != unit:
            continue
        if e["to_unit_id"] == uid:
            inn += e["rate"]["value"]
        if e["from_unit_id"] == uid:
            out += e["rate"]["value"]
    return inn, out


def component_cut(edges, members, unit):
    inside = set(members)
    enter = leave = 0.0
    for e in edges:
        if e["rate"]["unit"] != unit:
            continue
        a, b = e["from_unit_id"], e["to_unit_id"]
        if a not in inside and b in inside:
            enter += e["rate"]["value"]
        elif a in inside and b not in inside:
            leave += e["rate"]["value"]
    return enter, leave


def report(limit: int = 20) -> str:
    g, by = load()
    lines = [
        f"Graph {g['revision']}. Closure is the cut around each Tarjan component.",
        "A component passes when every unit balances and the cut balances, per rate unit.",
        "",
    ]
    any_fail = False
    for layer in ("mass", "thermal", "elec", "ess"):
        edges = by.get(layer, [])
        nodes = sorted({e["from_unit_id"] for e in edges} | {e["to_unit_id"] for e in edges})
        pairs = [(e["from_unit_id"], e["to_unit_id"]) for e in edges]
        comps = [c for c in tarjan(nodes, pairs) if len(c) > 1]
        lines.append(f"## {layer}: {len(edges)} edges, {len(comps)} loops")
        for comp in sorted(comps, key=len, reverse=True):
            units = sorted({e["rate"]["unit"] for e in edges
                            if e["from_unit_id"] in comp or e["to_unit_id"] in comp})
            named = johnson(comp, [(e["from_unit_id"], e["to_unit_id"], e["stream_id"]) for e in edges], limit)
            lines.append(f"- {len(comp)} units. Circuits listed: {len(named)} (cap {limit}).")
            lines.append("  " + ", ".join(sorted(comp)[:14]) + (" ..." if len(comp) > 14 else ""))
            if named:
                lines.append("  one circuit: " + " -> ".join(named[0][:8]))
            for unit in units:
                bad = []
                for uid in comp:
                    inn, out = node_gap(edges, uid, unit)
                    if inn == 0 and out == 0:
                        continue
                    if abs(inn - out) / max(inn, out, 1e-9) > 0.01:
                        bad.append(uid)
                enter, leave = component_cut(edges, comp, unit)
                cut = abs(enter - leave) / max(enter, leave, 1e-9) > 0.01
                status = "fail" if bad or cut else "pass"
                if status == "fail":
                    any_fail = True
                lines.append(
                    f"  {unit}: nodes off {len(bad)}, cut in {enter:.2f} out {leave:.2f} {status}"
                )
        lines.append("")
    lines.append("loops_closed: false" if any_fail else "loops_closed: true")
    return "\n".join(lines)


def main() -> None:
    text = report()
    out = ROOT / "derived" / "LOOP_CLOSURE.md"
    out.write_text(text + "\n")
    print(text)
    print("wrote", out)


if __name__ == "__main__":
    main()

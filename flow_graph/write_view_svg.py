#!/usr/bin/env python3
"""SVG from the view JSON. Ranked sweep. Graphviz is not on this machine."""
import json
from pathlib import Path

VIEWS = Path("/tmp/Aqueous_Solutions/flow_graph/views")


def svg_for(name):
    data = json.loads((VIEWS / f"{name}.json").read_text())
    nodes = [n["unit_id"] for n in data["nodes"]]
    edges = [(e["from_unit_id"], e["to_unit_id"], e["stream_id"]) for e in data["edges"]
             if e["from_unit_id"] in nodes and e["to_unit_id"] in nodes]
    rank = {n: 0 for n in nodes}
    for _ in range(len(nodes)):
        changed = False
        for a, b, _ in edges:
            if rank[b] < rank[a] + 1:
                rank[b] = rank[a] + 1
                changed = True
        if not changed:
            break
    cols = {}
    for n, r in rank.items():
        cols.setdefault(r, []).append(n)
    for r in cols:
        cols[r].sort()
    pos = {}
    for r, col in cols.items():
        for i, n in enumerate(col):
            pos[n] = (40 + i * 150, 40 + r * 70)
    w = 40 + max(len(c) for c in cols.values()) * 150
    h = 80 + (max(rank.values()) + 1) * 70
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
             '<rect width="100%" height="100%" fill="#f3efe6"/>',
             f'<text x="20" y="24" font-size="16" font-family="sans-serif">{name} rev {data.get("source_revision")}</text>']
    for a, b, sid in edges:
        x1, y1 = pos[a]
        x2, y2 = pos[b]
        parts.append(f'<line x1="{x1+60}" y1="{y1+18}" x2="{x2+60}" y2="{y2}" stroke="#444" stroke-width="1.2"/>')
    for n, (x, y) in pos.items():
        parts.append(f'<rect x="{x}" y="{y}" width="120" height="28" rx="3" fill="#fff" stroke="#222"/>')
        parts.append(f'<text x="{x+6}" y="{y+18}" font-size="10" font-family="sans-serif">{n}</text>')
    parts.append("</svg>")
    (VIEWS / f"{name}.svg").write_text("\n".join(parts))
    print(name, "nodes", len(nodes), "edges", len(edges))


for name in ("pfd", "mfd", "efd-elec", "efd-thermal", "efd-ess"):
    svg_for(name)

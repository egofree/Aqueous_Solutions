#!/usr/bin/env python3
# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Filter plant_flow_graph.json into PFD / MFD / EFD-* views (JSON + DOT + SVG).

Emits usable Graphviz SVG under views/ (requires ``dot`` on PATH).
Does not invent rates or stream routes — topology only from the graph.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GRAPH = ROOT / "plant_flow_graph.json"
VIEWS = ROOT / "views"

# Campus footprint sectors always shown on MFD even without mass edges
# (HYDRO electrical/ESS edges live on EFD; DOCK mass edge is TBD namespace).
MFD_FORCE_SECTORS = frozenset({"DOCK", "PUMPED_HYDRO"})

PRESETS = {
    "pfd": {
        "preset_id": "VIEW-PFD-LINE",
        "view_mode": "PFD",
        "layers": None,  # all
        "include_intra_aisle": True,
        "include_placeholders": True,
        "force_sectors": frozenset(),
        "engine": "dot",
    },
    "mfd": {
        "preset_id": "VIEW-MFD-CAMPUS",
        "view_mode": "MFD",
        "layers": ["mass"],
        "include_intra_aisle": False,
        "include_placeholders": True,
        "namespaces": ["S", "SANDBOX", "TBD"],
        "force_sectors": MFD_FORCE_SECTORS,
        "engine": "fdp",
    },
    "efd-elec": {
        "preset_id": "VIEW-EFD-ELEC",
        "view_mode": "EFD",
        "layers": ["elec"],
        "include_intra_aisle": True,
        "include_placeholders": True,
        "force_sectors": frozenset(),
        "engine": "dot",
    },
    "efd-thermal": {
        "preset_id": "VIEW-EFD-THERMAL",
        "view_mode": "EFD",
        "layers": ["thermal"],
        "include_intra_aisle": True,
        "include_placeholders": True,
        "force_sectors": frozenset(),
        "engine": "dot",
    },
    "efd-ess": {
        "preset_id": "VIEW-EFD-ESS",
        "view_mode": "EFD",
        "layers": ["ess"],
        "include_intra_aisle": True,
        "include_placeholders": True,
        "force_sectors": frozenset(),
        "engine": "dot",
    },
}

LAYER_EDGE_COLOR = {
    "mass": "#1b5e20",
    "elec": "#1e3a8a",
    "thermal": "#b45309",
    "ess": "#6d28d9",
}

HIGHLIGHT_STREAMS = frozenset(
    {
        "S17",
        "S73",
        "S74",
        "S75",
        "S76",
        "S77",
        "S78",
        "S79",
        "S80",
        "S81",
        "S82",
        "DOCK_EXPORT_TBD",
    }
)


def filter_view(g: dict, cfg: dict) -> dict:
    layers = cfg.get("layers")
    ns_allow = cfg.get("namespaces")
    force_sectors = cfg.get("force_sectors") or frozenset()
    edges = []
    used_nodes = set()
    for e in g["edges"]:
        if not cfg.get("include_placeholders", True) and e["presence"] == "placeholder":
            continue
        if not cfg.get("include_intra_aisle", True) and e["namespace"] == "IA":
            continue
        if ns_allow and e["namespace"] not in ns_allow:
            continue
        if layers is not None:
            if not set(e.get("layers") or []).intersection(layers):
                continue
        edges.append(e)
        used_nodes.add(e["from_unit_id"])
        used_nodes.add(e["to_unit_id"])

    # Campus placeholders (DOCK / PUMPED_HYDRO) on MFD even without mass edges
    for n in g["nodes"]:
        if n["sector_id"] in force_sectors:
            used_nodes.add(n["unit_id"])

    nodes = [n for n in g["nodes"] if n["unit_id"] in used_nodes]
    orphan_campus = [
        n["unit_id"]
        for n in nodes
        if n["sector_id"] in force_sectors
        and n["unit_id"] not in {e["from_unit_id"] for e in edges}
        | {e["to_unit_id"] for e in edges}
    ]
    return {
        "preset_id": cfg["preset_id"],
        "view_mode": cfg["view_mode"],
        "source_doc": g.get("doc_id"),
        "source_revision": g.get("revision"),
        "node_count": len(nodes),
        "edge_count": len(edges),
        "orphan_campus_units": orphan_campus,
        "nodes": nodes,
        "edges": edges,
        "render_note": (
            "JSON + Graphviz DOT/SVG from plant_flow_graph.json — "
            "no invented rates; placeholders dashed"
        ),
    }


def _escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def to_dot(view: dict, *, title: str) -> str:
    """Clustered Graphviz DOT suitable for SVG emit."""
    lines = [
        "digraph G {",
        "  graph [rankdir=LR, fontname=\"Helvetica\", fontsize=11, "
        f'label="{_escape(title)}\\n{_escape(view.get("preset_id", ""))}  ·  '
        f'{view.get("source_doc", "")} rev {view.get("source_revision", "")}", '
        "labelloc=t, pad=0.3, nodesep=0.35, ranksep=0.55];",
        '  node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=9];',
        '  edge [fontname="Helvetica", fontsize=8];',
    ]

    by_sector: dict[str, list] = defaultdict(list)
    for n in view["nodes"]:
        by_sector[n["sector_id"]].append(n)

    for sector, nodes in sorted(by_sector.items()):
        lines.append(f'  subgraph "cluster_{_escape(sector)}" {{')
        lines.append(f'    label="{_escape(sector)}";')
        lines.append('    style=rounded; color="#94a3b8";')
        for n in nodes:
            presence = n.get("presence", "present")
            fill = "#e2e8f0" if presence == "placeholder" else "#ffffff"
            if n["sector_id"] in MFD_FORCE_SECTORS:
                fill = "#fef3c7" if presence == "placeholder" else "#fde68a"
            gap = n.get("diagram_gap") or ""
            label = f"{n['unit_id']}"
            if presence == "placeholder":
                label += "\\n(placeholder)"
            if gap and n["sector_id"] in MFD_FORCE_SECTORS:
                # short campus note
                short = gap[:48] + ("…" if len(gap) > 48 else "")
                label += f"\\n{_escape(short)}"
            lines.append(
                f'    "{_escape(n["unit_id"])}" '
                f'[fillcolor="{fill}", label="{label}"];'
            )
        lines.append("  }")

    for e in view["edges"]:
        style = "dashed" if e.get("presence") == "placeholder" else "solid"
        layers = e.get("layers") or ["mass"]
        color = LAYER_EDGE_COLOR.get(layers[0], "#334155")
        sid = e["stream_id"]
        penwidth = "2.2" if sid in HIGHLIGHT_STREAMS else "1.2"
        rate = e.get("rate") or {}
        rate_bits = ""
        if rate.get("value") is not None:
            rate_bits = f"\\n{rate['value']} {rate.get('unit') or ''}".rstrip()
        elif e.get("namespace") == "TBD":
            rate_bits = "\\nTBD (no S##)"
        label = f"{sid}{rate_bits}"
        if e.get("gap_flags"):
            style = "dashed"
        lines.append(
            f'  "{_escape(e["from_unit_id"])}" -> "{_escape(e["to_unit_id"])}" '
            f'[label="{_escape(label)}", style={style}, color="{color}", '
            f'fontcolor="{color}", penwidth={penwidth}];'
        )

    # Orphan campus units already in clusters; add invisible note edge? skip.
    lines.append("}")
    return "\n".join(lines) + "\n"


def render_svg(dot_path: Path, svg_path: Path, engine: str = "dot") -> bool:
    exe = shutil.which(engine) or shutil.which("dot")
    if not exe:
        print(f"  WARN: graphviz '{engine}' not on PATH — skip SVG {svg_path.name}")
        return False
    try:
        subprocess.run(
            [exe, "-Tsvg", "-o", str(svg_path), str(dot_path)],
            check=True,
            capture_output=True,
            text=True,
        )
        return True
    except subprocess.CalledProcessError as exc:
        print(f"  WARN: {engine} failed for {dot_path.name}: {exc.stderr[:200]}")
        # fallback to dot
        if engine != "dot" and shutil.which("dot"):
            try:
                subprocess.run(
                    ["dot", "-Tsvg", "-o", str(svg_path), str(dot_path)],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                return True
            except subprocess.CalledProcessError as exc2:
                print(f"  WARN: dot fallback failed: {exc2.stderr[:200]}")
        return False


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--graph", type=Path, default=GRAPH)
    ap.add_argument("--out-dir", type=Path, default=VIEWS)
    ap.add_argument(
        "--only",
        choices=list(PRESETS.keys()) + ["all"],
        default="all",
    )
    ap.add_argument(
        "--dot",
        action="store_true",
        default=True,
        help="Write Graphviz DOT (default on)",
    )
    ap.add_argument("--no-dot", action="store_true", help="Skip DOT files")
    ap.add_argument(
        "--svg",
        action="store_true",
        default=True,
        help="Emit SVG via graphviz (default on)",
    )
    ap.add_argument("--no-svg", action="store_true", help="Skip SVG emit")
    args = ap.parse_args()
    write_dot = args.dot and not args.no_dot
    write_svg = args.svg and not args.no_svg

    g = json.loads(args.graph.read_text())
    args.out_dir.mkdir(parents=True, exist_ok=True)
    keys = list(PRESETS.keys()) if args.only == "all" else [args.only]
    for key in keys:
        cfg = PRESETS[key]
        view = filter_view(g, cfg)
        out = args.out_dir / f"{key}.json"
        out.write_text(json.dumps(view, indent=2) + "\n")
        print(
            f"{key}: nodes={view['node_count']} edges={view['edge_count']} "
            f"orphans={view.get('orphan_campus_units')} → {out.name}"
        )
        if write_dot or write_svg:
            title = {
                "pfd": "PFD line view (all layers)",
                "mfd": "MFD campus / mass view",
                "efd-elec": "EFD electrical layer (S17 + peers)",
                "efd-thermal": "EFD thermal layer",
                "efd-ess": "EFD ESS charge/discharge layer",
            }.get(key, key)
            dot_text = to_dot(view, title=title)
            dot_path = args.out_dir / f"{key}.dot"
            if write_dot:
                dot_path.write_text(dot_text)
            if write_svg:
                # always need a dot file for render
                if not write_dot:
                    dot_path.write_text(dot_text)
                svg_path = args.out_dir / f"{key}.svg"
                ok = render_svg(dot_path, svg_path, engine=cfg.get("engine", "dot"))
                if ok:
                    print(f"  SVG → {svg_path.name}")


if __name__ == "__main__":
    main()

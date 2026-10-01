#!/usr/bin/env python3
"""Stub: flow graph / export pack → 3D recipe (NO geometry solver).

Honest Phase D interface. Today geometry still comes from params.py +
build_plant.py. This script only inventories the graph and optionally
triggers the *baseline* FreeCAD rebuild (params-driven).

    python3 graph_geometry_bridge.py --graph ../../flow_graph/plant_flow_graph.json
    python3 graph_geometry_bridge.py --graph /path/to/flow_graph_snapshot.json \\
        --params /path/to/params.json --out /tmp/3d_recipe.json
    python3 graph_geometry_bridge.py --graph ../../flow_graph/plant_flow_graph.json \\
        --rebuild-baseline

CERN-OHL-S-2.0. See docs-authority/BUILD_3D_FROM_FLOW.md.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHARE = HERE.parents[1]  # .../aqueous-solutions
DEFAULT_GRAPH = SHARE / "flow_graph" / "plant_flow_graph.json"


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def node_enabled(n: dict) -> bool:
    if "enabled" in n:
        return bool(n["enabled"])
    # presence style
    p = n.get("presence") or (n.get("params") or {}).get("presence")
    if p is None:
        return True
    return str(p).lower() not in ("absent", "false", "0", "disabled")


def inventory(graph: dict) -> dict:
    nodes = graph.get("nodes") or []
    edges = graph.get("edges") or []
    by_sector: Counter = Counter()
    enabled_c = 0
    units = []
    for n in nodes:
        sector = n.get("sector_id") or "UNKNOWN"
        en = node_enabled(n)
        by_sector[sector] += 1
        if en:
            enabled_c += 1
        units.append(
            {
                "unit_id": n.get("unit_id"),
                "sector_id": sector,
                "enabled": en,
                "class": n.get("class"),
                "params": n.get("params") or {},
            }
        )
    return {
        "doc_id": graph.get("doc_id"),
        "revision": graph.get("revision"),
        "node_count": len(nodes),
        "edge_count": len(edges),
        "enabled_nodes": enabled_c,
        "nodes_by_sector": dict(sorted(by_sector.items())),
        "units": units,
    }


def read_scale_m_params_py() -> float | None:
    p = HERE / "params.py"
    if not p.is_file():
        return None
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("SCALE_M"):
            # SCALE_M = 1.0
            try:
                return float(line.split("=", 1)[1].strip().split()[0])
            except (IndexError, ValueError):
                return None
    return None


def build_recipe(graph: dict, params_overlay: dict | None) -> dict:
    inv = inventory(graph)
    disk_scale = read_scale_m_params_py()
    overlay_scale = None
    if params_overlay:
        overlay_scale = params_overlay.get("scale_m")
    return {
        "schema": "aqs-3d-recipe-0.1-stub",
        "status": "stub_not_wired",
        "licence": "CERN-OHL-S-2.0",
        "honest_note": (
            "No FreeCAD Feature is created from this recipe. "
            "Baseline solids remain params.py + build_plant.py. "
            "Phase D WPs: unit_id map, safe SCALE_M apply, presence filter, pack 3d/."
        ),
        "topology_authority": graph.get("doc_id") or "AQS-FLOW-GRAPH-001",
        "graph_inventory": {
            k: inv[k]
            for k in (
                "doc_id",
                "revision",
                "node_count",
                "edge_count",
                "enabled_nodes",
                "nodes_by_sector",
            )
        },
        "scale": {
            "params_py_SCALE_M": disk_scale,
            "overlay_scale_m": overlay_scale,
            "overlay_rewrites_params_py": False,
            "overlay_note": (params_overlay or {}).get("note"),
        },
        "freecad": {
            "binary": "/usr/bin/freecadcmd",
            "entry": "build_plant.py",
            "protocol": "docs-authority/FREECAD_PROTOCOL.md",
            "consumes_graph": False,
        },
        "future_hooks": [
            "WP-D1 unit_id ↔ FreeCAD object name map",
            "WP-D2 safe apply of overlay scale_m / module counts to a params copy",
            "WP-D3 export pack module 3d/ (recipe + rebuild pointer + optional STEP)",
            "WP-D4 presence filter from enabled=false",
            "WP-D5 optional placement_mm (schema)",
        ],
        "units_sample": inv["units"][:20],
        "units_full_count": len(inv["units"]),
    }


def rebuild_baseline() -> int:
    """Params-driven plant rebuild. Does not interpret the graph."""
    cmd = ["/usr/bin/freecadcmd", str(HERE / "build_plant.py")]
    print("rebuild-baseline (params only):", " ".join(cmd))
    if not Path("/usr/bin/freecadcmd").is_file():
        print("ERROR: /usr/bin/freecadcmd missing", file=sys.stderr)
        return 2
    return subprocess.call(cmd, cwd=str(HERE))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument(
        "--graph",
        type=Path,
        default=DEFAULT_GRAPH if DEFAULT_GRAPH.is_file() else None,
        help="plant_flow_graph.json or flow_graph_snapshot.json",
    )
    ap.add_argument(
        "--params",
        type=Path,
        default=None,
        help="optional export pack params.json overlay",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=None,
        help="write recipe JSON (default: print summary only)",
    )
    ap.add_argument(
        "--rebuild-baseline",
        action="store_true",
        help="after inventory, run freecadcmd build_plant.py (ignores graph for geometry)",
    )
    args = ap.parse_args(argv)

    if args.graph is None or not args.graph.is_file():
        print("ERROR: --graph path required and must exist", file=sys.stderr)
        return 2

    graph = load_json(args.graph)
    overlay = load_json(args.params) if args.params else None
    recipe = build_recipe(graph, overlay)

    gi = recipe["graph_inventory"]
    print("graph:", args.graph)
    print(
        "  rev=%s nodes=%s edges=%s enabled=%s"
        % (gi.get("revision"), gi["node_count"], gi["edge_count"], gi["enabled_nodes"])
    )
    print("  sectors:", gi["nodes_by_sector"])
    print(
        "  SCALE_M params.py=%s overlay=%s (overlay does NOT rewrite params.py)"
        % (recipe["scale"]["params_py_SCALE_M"], recipe["scale"]["overlay_scale_m"])
    )
    print("  status:", recipe["status"])

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        # full unit list in file
        full = dict(recipe)
        full["units"] = inventory(graph)["units"]
        full.pop("units_sample", None)
        args.out.write_text(json.dumps(full, indent=2) + "\n", encoding="utf-8")
        print("wrote", args.out)

    if args.rebuild_baseline:
        # Ensure share path shims if materials/stl missing (best-effort)
        models = HERE.parent
        tables_csv = SHARE / "tables" / "materials.csv"
        if tables_csv.is_file() and not (models / "materials.csv").exists():
            try:
                (models / "materials.csv").symlink_to(Path("../tables/materials.csv"))
            except OSError:
                pass
        detail = models / "detail"
        detail.mkdir(exist_ok=True)
        export_detail = models / "export" / "detail"
        stl_link = detail / "stl"
        if export_detail.is_dir() and not stl_link.exists():
            try:
                stl_link.symlink_to(Path("../export/detail"))
            except OSError:
                pass
        return rebuild_baseline()
    return 0


if __name__ == "__main__":
    sys.exit(main())

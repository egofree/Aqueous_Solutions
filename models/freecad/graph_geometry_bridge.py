#!/usr/bin/env python3
"""Flow graph / export pack → 3D recipe (NO geometry solver).

Inventories the graph, loads WP-D1 unit↔FreeCAD name map coverage,
optionally applies WP-D2 safe overlay → params_overlay.py (never gold
params.py), and optionally triggers the *baseline* FreeCAD rebuild.

    python3 graph_geometry_bridge.py --graph ../../flow_graph/plant_flow_graph.json
    python3 graph_geometry_bridge.py --graph /path/to/flow_graph_snapshot.json \\
        --params /path/to/params.json --out /tmp/3d_recipe.json
    python3 graph_geometry_bridge.py --graph ../../flow_graph/plant_flow_graph.json \\
        --map unit_freecad_map.json --coverage
    python3 graph_geometry_bridge.py --params /path/to/params.json --apply-overlay
    python3 graph_geometry_bridge.py --graph ../../flow_graph/plant_flow_graph.json \\
        --rebuild-baseline

CERN-OHL-S-2.0. See docs-authority/BUILD_3D_FROM_FLOW.md;
planning/GRAPH_TO_3D_IMPLEMENTATION_PLAN.md (AQS-PLAN-3D-001 WP-D1/D2).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Share layout: .../aqueous-solutions/models/freecad → parents[1]=aqueous-solutions
# Hub layout: .../cad/freecad → parents[1]=cad; graph lives at hub/flow_graph
SHARE_CANDIDATE = HERE.parents[1]
DEFAULT_MAP = HERE / "unit_freecad_map.json"
DEFAULT_OVERLAY_OUT = HERE / "params_overlay.py"


def _load_overlay_apply():
    """Import params_overlay_apply from the same directory (hub or share)."""
    import importlib.util

    mod_path = HERE / "params_overlay_apply.py"
    if not mod_path.is_file():
        raise ImportError(f"params_overlay_apply.py missing beside bridge: {mod_path}")
    spec = importlib.util.spec_from_file_location("params_overlay_apply", mod_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {mod_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod



def _default_graph() -> Path | None:
    candidates = [
        SHARE_CANDIDATE / "flow_graph" / "plant_flow_graph.json",
        HERE.parents[1].parent / "flow_graph" / "plant_flow_graph.json",  # hub cad/ → aqueous_diagrams
        HERE.parents[2] / "flow_graph" / "plant_flow_graph.json",
    ]
    for c in candidates:
        if c.is_file():
            return c
    return None


DEFAULT_GRAPH = _default_graph()


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def node_enabled(n: dict) -> bool:
    if "enabled" in n:
        return bool(n["enabled"])
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
                "presence": n.get("presence"),
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


def load_unit_map(path: Path | None) -> dict | None:
    """Load aqs-unit-freecad-map-1.0 JSON; return None if missing."""
    if path is None:
        path = DEFAULT_MAP
    if not path.is_file():
        return None
    return load_json(path)


def map_coverage(graph: dict, unit_map: dict) -> dict:
    """Join graph unit_ids to map entries; report coverage % (WP-D1)."""
    nodes = graph.get("nodes") or []
    entries = unit_map.get("entries") or []
    by_id = {e.get("unit_id"): e for e in entries if e.get("unit_id")}
    graph_ids = [n.get("unit_id") for n in nodes if n.get("unit_id")]
    missing_rows = [uid for uid in graph_ids if uid not in by_id]
    extra_rows = sorted(set(by_id) - set(graph_ids))
    status_c: Counter = Counter()
    joined = []
    for uid in graph_ids:
        e = by_id.get(uid)
        if e is None:
            status_c["missing_map_row"] += 1
            joined.append({"unit_id": uid, "status": "missing_map_row"})
            continue
        st = e.get("status") or "unknown"
        status_c[st] += 1
        joined.append(
            {
                "unit_id": uid,
                "status": st,
                "freecad_names": e.get("freecad_names") or [],
                "builder": e.get("builder"),
                "group_path": e.get("group_path") or [],
            }
        )
    n = len(graph_ids) or 1
    classified = n - len(missing_rows)
    present_ids = [
        n.get("unit_id")
        for n in nodes
        if n.get("unit_id") and n.get("presence") == "present"
    ]
    present_ok = [
        uid
        for uid in present_ids
        if (by_id.get(uid) or {}).get("status") in ("mapped", "massing_only")
    ]
    return {
        "schema": unit_map.get("schema"),
        "map_revision": unit_map.get("revision"),
        "map_path": None,  # filled by caller
        "graph_nodes": len(graph_ids),
        "map_entries": len(entries),
        "rows_classified": classified,
        "rows_classified_pct": round(100.0 * classified / n, 1),
        "by_status": dict(sorted(status_c.items())),
        "missing_map_rows": missing_rows,
        "extra_map_rows": extra_rows,
        "present_nodes": len(present_ids),
        "present_mapped_or_massing": len(present_ok),
        "present_coverage_pct": round(
            100.0 * len(present_ok) / (len(present_ids) or 1), 1
        ),
        "gaps": {
            "unmapped": [j["unit_id"] for j in joined if j["status"] == "unmapped"],
            "placeholder_skip": [
                j["unit_id"] for j in joined if j["status"] == "placeholder_skip"
            ],
            "missing_map_row": missing_rows,
        },
        "units": joined,
    }


def read_scale_m_params_py() -> float | None:
    p = HERE / "params.py"
    if not p.is_file():
        return None
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("SCALE_M"):
            try:
                return float(line.split("=", 1)[1].strip().split()[0])
            except (IndexError, ValueError):
                return None
    return None


def build_recipe(
    graph: dict,
    params_overlay: dict | None,
    unit_map: dict | None = None,
    map_path: Path | None = None,
    overlay_apply_result: dict | None = None,
) -> dict:
    inv = inventory(graph)
    disk_scale = read_scale_m_params_py()
    overlay_scale = None
    if params_overlay:
        overlay_scale = params_overlay.get("scale_m")

    coverage = None
    if unit_map is not None:
        coverage = map_coverage(graph, unit_map)
        if map_path is not None:
            coverage["map_path"] = str(map_path)

    status = "stub_not_wired"
    if coverage and coverage["rows_classified_pct"] == 100.0:
        status = "name_map_loaded_wp_d1"
    if overlay_apply_result and overlay_apply_result.get("ok"):
        status = "overlay_fork_applied_wp_d2"

    recipe = {
        "schema": "aqs-3d-recipe-0.1-stub",
        "status": status,
        "licence": "CERN-OHL-S-2.0",
        "honest_note": (
            "No FreeCAD Feature is created from this recipe yet. "
            "Baseline solids remain params.py + build_plant.py unless a session "
            "imports params_overlay.py. WP-D1 name map + WP-D2 safe overlay "
            "applicator are wired; WP-D3..D4 add pack 3d/ + presence filter."
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
        "name_map_coverage": (
            {
                k: coverage[k]
                for k in (
                    "schema",
                    "map_revision",
                    "map_path",
                    "graph_nodes",
                    "map_entries",
                    "rows_classified",
                    "rows_classified_pct",
                    "by_status",
                    "present_nodes",
                    "present_mapped_or_massing",
                    "present_coverage_pct",
                    "gaps",
                )
            }
            if coverage
            else None
        ),
        "scale": {
            "params_py_SCALE_M": disk_scale,
            "overlay_scale_m": overlay_scale,
            "applied_to": (
                (overlay_apply_result or {}).get("out_path")
                if overlay_apply_result
                else None
            ),
            "applied_keys": (
                (overlay_apply_result or {}).get("applied_keys")
                if overlay_apply_result
                else None
            ),
            "overlay_rewrites_params_py": False,
            "overlay_note": (params_overlay or {}).get("note"),
            "allow_list_ref": "params_overlay_apply.py",
        },
        "freecad": {
            "binary": "/usr/bin/freecadcmd",
            "entry": "build_plant.py",
            "protocol": "docs-authority/FREECAD_PROTOCOL.md",
            "consumes_graph": False,
            "name_map_ref": "unit_freecad_map.json",
        },
        "future_hooks": [
            "WP-D3 export pack module 3d/ (recipe + rebuild pointer + optional STEP)",
            "WP-D4 presence filter from enabled=false / placeholder policy",
            "WP-D5 optional placement_mm (schema study)",
        ],
        "units_sample": inv["units"][:20],
        "units_full_count": len(inv["units"]),
    }
    if coverage:
        recipe["_name_map_units"] = coverage["units"]
    try:
        oa = _load_overlay_apply()
        recipe["overlay_allow_list"] = oa.allow_list_report()["apply"]
    except ImportError:
        recipe["overlay_allow_list"] = None
    if overlay_apply_result:
        recipe["overlay_apply"] = {
            "ok": overlay_apply_result.get("ok"),
            "out_path": overlay_apply_result.get("out_path"),
            "applied_keys": overlay_apply_result.get("applied_keys"),
            "overlay_rewrites_params_py": False,
        }
    return recipe


def rebuild_baseline() -> int:
    """Params-driven plant rebuild. Does not interpret the graph."""
    cmd = ["/usr/bin/freecadcmd", str(HERE / "build_plant.py")]
    print("rebuild-baseline (params only):", " ".join(cmd))
    if not Path("/usr/bin/freecadcmd").is_file():
        print("ERROR: /usr/bin/freecadcmd missing", file=sys.stderr)
        return 2
    return subprocess.call(cmd, cwd=str(HERE))


def print_coverage(cov: dict) -> None:
    print("name map coverage:")
    print(
        "  classified=%s/%s (%.1f%%)  present_mapped_or_massing=%s/%s (%.1f%%)"
        % (
            cov["rows_classified"],
            cov["graph_nodes"],
            cov["rows_classified_pct"],
            cov["present_mapped_or_massing"],
            cov["present_nodes"],
            cov["present_coverage_pct"],
        )
    )
    print("  by_status:", cov["by_status"])
    gaps = cov.get("gaps") or {}
    if gaps.get("unmapped"):
        print("  gaps.unmapped (%d):" % len(gaps["unmapped"]), ", ".join(gaps["unmapped"][:12]),
              ("..." if len(gaps["unmapped"]) > 12 else ""))
    if gaps.get("placeholder_skip"):
        print(
            "  gaps.placeholder_skip (%d):" % len(gaps["placeholder_skip"]),
            ", ".join(gaps["placeholder_skip"]),
        )
    if gaps.get("missing_map_row"):
        print("  ERROR missing_map_row:", gaps["missing_map_row"])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument(
        "--graph",
        type=Path,
        default=DEFAULT_GRAPH,
        help="plant_flow_graph.json or flow_graph_snapshot.json",
    )
    ap.add_argument(
        "--params",
        type=Path,
        default=None,
        help="optional export pack params.json overlay",
    )
    ap.add_argument(
        "--map",
        type=Path,
        default=DEFAULT_MAP if DEFAULT_MAP.is_file() else None,
        help="unit_freecad_map.json (WP-D1); default beside this script",
    )
    ap.add_argument(
        "--coverage",
        action="store_true",
        help="print name-map coverage %% and exit 0 if 100%% rows classified",
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
    ap.add_argument(
        "--apply-overlay",
        action="store_true",
        help="WP-D2: apply --params allow-list → params_overlay.py (never gold params.py)",
    )
    ap.add_argument(
        "--overlay-out",
        type=Path,
        default=None,
        help="fork path for --apply-overlay (default: params_overlay.py beside bridge)",
    )
    ap.add_argument(
        "--allow-list",
        action="store_true",
        help="print WP-D2 overlay allow-list JSON and exit",
    )
    args = ap.parse_args(argv)

    if args.allow_list:
        oa = _load_overlay_apply()
        print(json.dumps(oa.allow_list_report(), indent=2))
        return 0

    apply_result = None
    if args.apply_overlay:
        if not args.params or not args.params.is_file():
            print("ERROR: --apply-overlay requires existing --params", file=sys.stderr)
            return 2
        oa = _load_overlay_apply()
        overlay_doc = load_json(args.params)
        out = args.overlay_out or DEFAULT_OVERLAY_OUT
        try:
            apply_result = oa.write_overlay_fork(overlay_doc, out_path=out)
        except ValueError as exc:
            print(f"ERROR: overlay refuse: {exc}", file=sys.stderr)
            return 1
        print("overlay applied →", apply_result["out_path"])
        print("applied_keys:", json.dumps(apply_result["applied_keys"], sort_keys=True))
        print("gold untouched; overlay_rewrites_params_py=false")
        if args.graph is None and not args.out and not args.coverage and not args.rebuild_baseline:
            return 0

    if args.graph is None or not args.graph.is_file():
        print("ERROR: --graph path required and must exist", file=sys.stderr)
        return 2

    graph = load_json(args.graph)
    overlay = load_json(args.params) if args.params else None
    unit_map = load_unit_map(args.map) if args.map else load_unit_map(DEFAULT_MAP)
    map_path = args.map if args.map and args.map.is_file() else (
        DEFAULT_MAP if DEFAULT_MAP.is_file() else None
    )

    if args.coverage:
        if unit_map is None:
            print("ERROR: --coverage requires unit_freecad_map.json", file=sys.stderr)
            return 2
        cov = map_coverage(graph, unit_map)
        cov["map_path"] = str(map_path) if map_path else None
        print("graph:", args.graph)
        print_coverage(cov)
        return 0 if cov["rows_classified_pct"] == 100.0 and not cov["missing_map_rows"] else 1

    recipe = build_recipe(
        graph,
        overlay,
        unit_map=unit_map,
        map_path=map_path,
        overlay_apply_result=apply_result,
    )

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
    if recipe["scale"].get("applied_keys") is not None:
        print("  overlay applied_to:", recipe["scale"].get("applied_to"))
        print("  overlay applied_keys:", recipe["scale"].get("applied_keys"))
    print("  status:", recipe["status"])
    if recipe.get("name_map_coverage"):
        print_coverage(recipe["name_map_coverage"])
    elif map_path is None:
        print("  name map: (not found — place unit_freecad_map.json beside bridge)")

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        full = dict(recipe)
        full["units"] = inventory(graph)["units"]
        if "_name_map_units" in full:
            full["name_map_units"] = full.pop("_name_map_units")
        full.pop("units_sample", None)
        args.out.write_text(json.dumps(full, indent=2) + "\n", encoding="utf-8")
        print("wrote", args.out)

    if args.rebuild_baseline:
        models = HERE.parent
        share_root = SHARE_CANDIDATE
        tables_csv = share_root / "tables" / "materials.csv"
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

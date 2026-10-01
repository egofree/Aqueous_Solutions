#!/usr/bin/env python3
"""Flow graph / export pack → 3D recipe (no geometry solver).

Inventories the graph, loads unit↔FreeCAD name-map coverage, optionally
applies allow-listed overlay → params_overlay.py (never gold params.py),
applies presence filter (skip/tag disabled & placeholder), emits pack-ready
recipe, and optionally triggers baseline rebuild.

    python3 graph_geometry_bridge.py --graph ../../flow_graph/plant_flow_graph.json
    python3 graph_geometry_bridge.py --graph /path/to/flow_graph_snapshot.json \
        --params /path/to/params.json --out /tmp/3d_recipe.json
    python3 graph_geometry_bridge.py --graph ../../flow_graph/plant_flow_graph.json \
        --map unit_freecad_map.json --coverage
    python3 graph_geometry_bridge.py --params /path/to/params.json --apply-overlay
    python3 graph_geometry_bridge.py --graph ../../flow_graph/plant_flow_graph.json \
        --presence-report
    python3 graph_geometry_bridge.py --graph snapshot.json --apply-presence \
        --fcstd plant.FCStd --fcstd-out /tmp/plant_filtered.FCStd
    python3 graph_geometry_bridge.py --self-test
    python3 graph_geometry_bridge.py --graph ../../flow_graph/plant_flow_graph.json \
        --rebuild-baseline

CERN-OHL-S-2.0. See docs-authority/BUILD_3D_FROM_FLOW.md;
planning/GRAPH_TO_3D_IMPLEMENTATION_PLAN.md (AQS-PLAN-3D-001).
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
        HERE.parents[1].parent / "flow_graph" / "plant_flow_graph.json",  # share: models/ → repo root
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
    """Join graph unit_ids to map entries; report coverage %."""
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


PRESENCE_POLICY = "skip_disabled_and_placeholder_unless_mapped_massing"


def node_presence(n: dict) -> str:
    """Return graph presence string (default present)."""
    p = n.get("presence")
    if p is None:
        p = (n.get("params") or {}).get("presence")
    if p is None:
        return "present"
    return str(p).lower()


def emit_decision(node: dict, map_entry: dict | None) -> dict:
    """Presence + name-map emit decision. Does not create Features.

    Semantics (AQS-PLAN-3D-001 §8):
      enabled=false → skip
      presence=placeholder → skip unless map status=massing_only (opt-in)
      presence=present + enabled → emit per map (mapped/massing_only/structural)
      unmapped / missing map row / placeholder_skip → skip (gap recorded)
    """
    uid = node.get("unit_id")
    enabled = node_enabled(node)
    presence = node_presence(node)
    st = (map_entry or {}).get("status")
    names = list((map_entry or {}).get("freecad_names") or [])
    base = {
        "unit_id": uid,
        "sector_id": node.get("sector_id"),
        "enabled": enabled,
        "presence": node.get("presence") if node.get("presence") is not None else presence,
        "map_status": st,
        "freecad_names": names,
        "builder": (map_entry or {}).get("builder"),
    }

    if not enabled:
        return {**base, "action": "skip_disabled", "emit": False}

    if presence in ("absent", "disabled", "false", "0"):
        return {**base, "action": "skip_absent", "emit": False}

    if presence == "placeholder":
        if st == "massing_only" and names:
            return {**base, "action": "emit_massing_placeholder_opt_in", "emit": True}
        return {**base, "action": "skip_placeholder", "emit": False}

    if map_entry is None:
        return {**base, "action": "gap_missing_map_row", "emit": False}

    if st == "unmapped":
        return {**base, "action": "skip_unmapped", "emit": False}
    if st == "placeholder_skip":
        return {**base, "action": "skip_placeholder", "emit": False}
    if st in ("mapped", "massing_only", "structural"):
        if not names and st != "structural":
            return {**base, "action": "emit_mapped_no_names", "emit": False}
        return {**base, "action": "emit", "emit": True}

    return {**base, "action": f"skip_unknown_status_{st}", "emit": False}


def presence_filter(graph: dict, unit_map: dict | None) -> dict:
    """Join graph nodes to map; return emit/skip decisions + Feature name sets."""
    entries = (unit_map or {}).get("entries") or []
    by_id = {e.get("unit_id"): e for e in entries if e.get("unit_id")}
    decisions = []
    for n in graph.get("nodes") or []:
        if not isinstance(n, dict) or not n.get("unit_id"):
            continue
        decisions.append(emit_decision(n, by_id.get(n["unit_id"])))

    emit_u = [d for d in decisions if d["emit"]]
    skip_u = [d for d in decisions if not d["emit"]]
    action_c: Counter = Counter(d["action"] for d in decisions)
    names_emit: list[str] = []
    names_omit: list[str] = []
    for d in decisions:
        for name in d["freecad_names"]:
            if d["emit"]:
                names_emit.append(name)
            else:
                names_omit.append(name)
    return {
        "policy": PRESENCE_POLICY,
        "units_total": len(decisions),
        "emit_count": len(emit_u),
        "skip_count": len(skip_u),
        "by_action": dict(sorted(action_c.items())),
        "freecad_names_emit": sorted(set(names_emit)),
        "freecad_names_omit": sorted(set(names_omit)),
        "emit_unit_ids": [d["unit_id"] for d in emit_u],
        "skip_unit_ids": [d["unit_id"] for d in skip_u],
        "decisions": decisions,
        "note": (
            "Structural envelope Features not listed on skipped process units "
            "are left in place. Logical unmapped stay skip (no invented boxes)."
        ),
    }


def file_sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    import hashlib

    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()



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



def apply_presence_to_fcstd(
    fcstd_in: Path,
    fcstd_out: Path,
    filt: dict,
    mode: str = "omit",
) -> dict:
    """Post-pass: omit or tag Features listed in filt['freecad_names_omit'].

    Runs under /usr/bin/freecadcmd. Never invents geometry. Input is copied
    to fcstd_out before mutation when paths differ.
    """
    if mode not in ("omit", "tag"):
        raise ValueError(f"mode must be omit|tag, got {mode!r}")
    if not Path("/usr/bin/freecadcmd").is_file():
        raise FileNotFoundError("/usr/bin/freecadcmd missing")
    if not fcstd_in.is_file():
        raise FileNotFoundError(f"FCStd not found: {fcstd_in}")

    omit_names = list(filt.get("freecad_names_omit") or [])
    script = HERE / "_presence_filter_once.py"
    report_path = HERE / "_presence_filter_report.json"
    lines = [
        "# SPDX-License-Identifier: CERN-OHL-S-2.0",
        "# Ephemeral FreeCAD script from graph_geometry_bridge.apply_presence_to_fcstd.",
        "import json, shutil",
        "import FreeCAD as App",
        f"src = {str(fcstd_in.resolve())!r}",
        f"dst = {str(fcstd_out.resolve())!r}",
        f"mode = {mode!r}",
        f"omit = {omit_names!r}",
        f"report_path = {str(report_path.resolve())!r}",
        "if src != dst:",
        "    shutil.copy2(src, dst)",
        "doc = App.openDocument(dst)",
        "before = len(doc.Objects)",
        "before_parts = sum(1 for o in doc.Objects if o.TypeId == 'Part::Feature')",
        "removed = []",
        "tagged = []",
        "missing = []",
        "for name in omit:",
        "    obj = doc.getObject(name)",
        "    if obj is None:",
        "        missing.append(name)",
        "        continue",
        "    if mode == 'omit':",
        "        doc.removeObject(name)",
        "        removed.append(name)",
        "    else:",
        "        try:",
        "            obj.Visibility = False",
        "        except Exception:",
        "            pass",
        "        try:",
        "            lbl = obj.Label or name",
        "            if not str(lbl).startswith('DISABLED_'):",
        "                obj.Label = 'DISABLED_' + str(lbl)",
        "        except Exception:",
        "            pass",
        "        tagged.append(name)",
        "doc.recompute()",
        "doc.save()",
        "App.closeDocument(doc.Name)",
        "after_doc = App.openDocument(dst)",
        "after = len(after_doc.Objects)",
        "after_parts = sum(1 for o in after_doc.Objects if o.TypeId == 'Part::Feature')",
        "App.closeDocument(after_doc.Name)",
        "rep = {",
        "  'ok': True,",
        "  'mode': mode,",
        "  'fcstd_in': src,",
        "  'fcstd_out': dst,",
        "  'objects_before': before,",
        "  'objects_after': after,",
        "  'parts_before': before_parts,",
        "  'parts_after': after_parts,",
        "  'removed': removed,",
        "  'tagged': tagged,",
        "  'missing_names': missing,",
        "  'omit_requested': omit,",
        "}",
        "open(report_path, 'w', encoding='utf-8').write(json.dumps(rep, indent=2) + '\\n')",
        "keys = ('mode','objects_before','objects_after','parts_before','parts_after',"
        "        'removed','tagged','missing_names')",
        "print('presence-filter:', json.dumps({k: rep[k] for k in keys}))",
    ]
    script.write_text("\n".join(lines) + "\n", encoding="utf-8")
    try:
        rc = subprocess.call(
            ["/usr/bin/freecadcmd", str(script)],
            cwd=str(HERE),
        )
        if rc != 0:
            raise RuntimeError(f"freecadcmd presence filter exited {rc}")
        if not report_path.is_file():
            raise RuntimeError("presence filter report missing")
        return json.loads(report_path.read_text(encoding="utf-8"))
    finally:
        script.unlink(missing_ok=True)
        report_path.unlink(missing_ok=True)


def presence_self_test(graph: dict, unit_map: dict) -> int:
    """T6-style presence filter tests (no invented geometry). Return 0 on pass."""
    failures: list[str] = []
    filt = presence_filter(graph, unit_map)
    if filt["policy"] != PRESENCE_POLICY:
        failures.append("policy mismatch")

    if filt["by_action"].get("skip_disabled"):
        failures.append(
            f"gold graph unexpected skip_disabled: {filt['by_action']['skip_disabled']}"
        )

    unmapped = [
        d for d in filt["decisions"] if d.get("map_status") == "unmapped"
    ]
    if not unmapped:
        failures.append("expected >=1 unmapped logical unit in Rev B map")
    for d in unmapped:
        if d["emit"] or d["action"] != "skip_unmapped":
            failures.append(f"unmapped must skip: {d['unit_id']} -> {d}")

    for d in filt["decisions"]:
        if (
            str(d.get("presence")).lower() == "placeholder"
            and d["map_status"] != "massing_only"
            and d["emit"]
        ):
            failures.append(f"placeholder must skip: {d['unit_id']}")

    nodes = [dict(n) for n in (graph.get("nodes") or []) if isinstance(n, dict)]
    target = None
    by_id = {
        e["unit_id"]: e
        for e in (unit_map.get("entries") or [])
        if e.get("unit_id")
    }
    for n in nodes:
        e = by_id.get(n.get("unit_id") or "")
        if e and e.get("status") == "mapped" and e.get("freecad_names"):
            target = n.get("unit_id")
            break
    if not target:
        failures.append("no mapped unit with freecad_names for T6")
    else:
        mut = {
            "nodes": [],
            "edges": graph.get("edges") or [],
            "doc_id": graph.get("doc_id"),
            "revision": graph.get("revision"),
        }
        for n in nodes:
            nn = dict(n)
            if nn.get("unit_id") == target:
                nn["enabled"] = False
            mut["nodes"].append(nn)
        filt2 = presence_filter(mut, unit_map)
        d2 = next(x for x in filt2["decisions"] if x["unit_id"] == target)
        if d2["action"] != "skip_disabled" or d2["emit"]:
            failures.append(f"T6 enabled=false: {d2}")
        names = by_id[target]["freecad_names"]
        for nm in names:
            if nm not in filt2["freecad_names_omit"]:
                failures.append(f"T6 omit set missing {nm}")
            if nm in filt2["freecad_names_emit"]:
                failures.append(f"T6 emit set still has {nm}")
        extra = set(filt2["freecad_names_omit"]) - set(filt["freecad_names_omit"])
        if set(names) - extra:
            failures.append(f"T6 omit delta missing names: {set(names) - extra}")
        print(f"PASS T6 logic: {target} enabled=false -> omit {names}")

    leach = next(
        (d for d in filt["decisions"] if d["unit_id"] == "LEACH_CSTR_1"), None
    )
    if leach is None:
        failures.append("LEACH_CSTR_1 missing from decisions")
    elif not leach["emit"] or leach["action"] != "emit":
        failures.append(f"LEACH_CSTR_1 should emit: {leach}")
    else:
        print("PASS: LEACH_CSTR_1 emit")

    blow = next(
        (d for d in filt["decisions"] if d["unit_id"] == "BLOW_MOLD"), None
    )
    if blow is None:
        print("NOTE: BLOW_MOLD not in graph — skip placeholder named check")
    elif blow["emit"] or blow["action"] != "skip_placeholder":
        failures.append(f"BLOW_MOLD should skip_placeholder: {blow}")
    else:
        print("PASS: BLOW_MOLD skip_placeholder")

    print(
        "presence baseline: emit=%s skip=%s by_action=%s omit_names=%s"
        % (
            filt["emit_count"],
            filt["skip_count"],
            filt["by_action"],
            len(filt["freecad_names_omit"]),
        )
    )
    if filt["freecad_names_omit"]:
        print(
            "NOTE: baseline freecad_names_omit non-empty:",
            filt["freecad_names_omit"][:12],
        )
    else:
        print(
            "PASS baseline omit empty: all-present/enabled catalogue "
            "Feature set unchanged by filter"
        )

    if failures:
        for f in failures:
            print("FAIL:", f)
        return 1
    print("self-test: presence filter passed")
    return 0



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

    filt = presence_filter(graph, unit_map) if unit_map is not None else None

    status = "stub_not_wired"
    if coverage and coverage["rows_classified_pct"] == 100.0:
        status = "name_map_loaded_wp_d1"
    if overlay_apply_result and overlay_apply_result.get("ok"):
        status = "overlay_fork_applied_wp_d2"
    if filt is not None and coverage and coverage["rows_classified_pct"] == 100.0:
        status = "wired_presence_and_overlay" if (
            overlay_apply_result and overlay_apply_result.get("ok")
        ) else "wired_presence_name_map"

    plant_fcstd = HERE / "plant.FCStd"
    plant_step = HERE / "plant.step"
    sha = {}
    h1 = file_sha256(plant_fcstd)
    if h1:
        sha["plant.FCStd"] = h1
    h2 = file_sha256(plant_step)
    if h2:
        sha["plant.step"] = h2

    recipe = {
        "schema": "aqs-3d-recipe-1.0",
        "status": status,
        "licence": "CERN-OHL-S-2.0",
        "honest_note": (
            "Recipe inventories the graph, name-map coverage, presence filter, "
            "and optional overlay fork. Solids still come from params.py + "
            "build_plant.py (or params_overlay.py fork). Presence post-pass "
            "omits/tags mapped Feature Names for disabled/placeholder units — "
            "dims and rates are not derived from the graph. Logical unmapped stay skip."
        ),
        "topology_authority": graph.get("doc_id") or "AQS-FLOW-GRAPH-001",
        "graph_ref": None,  # pack emitter fills relative path
        "params_overlay_ref": None,
        "name_map_ref": "unit_freecad_map.json",
        "presence_policy": PRESENCE_POLICY,
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
            "rebuild_sh": "models/REBUILD.sh",
            "protocol": "docs-authority/FREECAD_PROTOCOL.md",
            "consumes_graph": True,
            "name_map_ref": "unit_freecad_map.json",
            "presence_post_pass": (
                "graph_geometry_bridge.py --apply-presence "
                "--fcstd plant.FCStd --fcstd-out plant_filtered.FCStd"
            ),
        },
        "outputs": {
            "fcstd": "plant.FCStd",
            "step_optional": "plant.step" if plant_step.is_file() else None,
            "sha256": sha,
        },
        "presence_filter": (
            {
                k: filt[k]
                for k in (
                    "policy",
                    "units_total",
                    "emit_count",
                    "skip_count",
                    "by_action",
                    "freecad_names_omit",
                    "skip_unit_ids",
                    "note",
                )
            }
            if filt
            else None
        ),
        "future_hooks": [
            "optional placement_mm (schema study; applicator deferred)",
            "Auto layout solver (post-Phase-D study)",
        ],
        "units_sample": inv["units"][:20],
        "units_full_count": len(inv["units"]),
    }
    if coverage:
        recipe["_name_map_units"] = coverage["units"]
    if filt:
        recipe["_presence_decisions"] = filt["decisions"]
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
        help="unit_freecad_map.json; default beside this script",
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
        help="apply --params allow-list → params_overlay.py (never gold params.py)",
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
        help="print overlay allow-list JSON and exit",
    )
    ap.add_argument(
        "--presence-report",
        action="store_true",
        help="print presence filter summary JSON and exit",
    )
    ap.add_argument(
        "--apply-presence",
        action="store_true",
        help="omit/tag Features for skipped units on an FCStd copy",
    )
    ap.add_argument(
        "--fcstd",
        type=Path,
        default=None,
        help="input plant.FCStd for --apply-presence (default: plant.FCStd beside bridge)",
    )
    ap.add_argument(
        "--fcstd-out",
        type=Path,
        default=None,
        help="output FCStd for --apply-presence (default: plant_filtered.FCStd)",
    )
    ap.add_argument(
        "--presence-mode",
        choices=("omit", "tag"),
        default="omit",
        help="omit=remove Features; tag=hide + DISABLED_ Label prefix",
    )
    ap.add_argument(
        "--self-test",
        action="store_true",
        help="run WP-D4 presence filter tests (no invented geometry)",
    )
    args = ap.parse_args(argv)

    if args.allow_list:
        oa = _load_overlay_apply()
        print(json.dumps(oa.allow_list_report(), indent=2))
        return 0

    if args.self_test:
        gpath = args.graph if args.graph and args.graph.is_file() else DEFAULT_GRAPH
        if gpath is None or not Path(gpath).is_file():
            print("ERROR: --self-test needs --graph / default plant_flow_graph.json", file=sys.stderr)
            return 2
        umap = load_unit_map(args.map) if args.map else load_unit_map(DEFAULT_MAP)
        if umap is None:
            print("ERROR: --self-test requires unit_freecad_map.json", file=sys.stderr)
            return 2
        return presence_self_test(load_json(Path(gpath)), umap)

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

    if args.presence_report or args.apply_presence:
        if unit_map is None:
            print("ERROR: presence filter requires unit_freecad_map.json", file=sys.stderr)
            return 2
        filt = presence_filter(graph, unit_map)
        summary = {
            k: filt[k]
            for k in (
                "policy",
                "units_total",
                "emit_count",
                "skip_count",
                "by_action",
                "freecad_names_omit",
                "skip_unit_ids",
                "note",
            )
        }
        print(json.dumps(summary, indent=2))
        if args.apply_presence:
            fc_in = args.fcstd or (HERE / "plant.FCStd")
            fc_out = args.fcstd_out or (HERE / "plant_filtered.FCStd")
            try:
                rep = apply_presence_to_fcstd(
                    fc_in, fc_out, filt, mode=args.presence_mode
                )
            except (FileNotFoundError, RuntimeError, ValueError) as exc:
                print(f"ERROR: presence apply: {exc}", file=sys.stderr)
                return 2
            print("presence applied →", rep.get("fcstd_out"))
            print(
                "objects %s→%s parts %s→%s removed=%s tagged=%s missing=%s"
                % (
                    rep.get("objects_before"),
                    rep.get("objects_after"),
                    rep.get("parts_before"),
                    rep.get("parts_after"),
                    len(rep.get("removed") or []),
                    len(rep.get("tagged") or []),
                    len(rep.get("missing_names") or []),
                )
            )
        return 0

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
    if recipe.get("presence_filter"):
        pf = recipe["presence_filter"]
        print(
            "  presence: emit=%s skip=%s omit_names=%s policy=%s"
            % (
                pf.get("emit_count"),
                pf.get("skip_count"),
                len(pf.get("freecad_names_omit") or []),
                pf.get("policy"),
            )
        )
        print("  presence by_action:", pf.get("by_action"))

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        full = dict(recipe)
        full["units"] = inventory(graph)["units"]
        if "_name_map_units" in full:
            full["name_map_units"] = full.pop("_name_map_units")
        if "_presence_decisions" in full:
            if full.get("presence_filter") is not None:
                full["presence_filter"] = dict(full["presence_filter"])
                full["presence_filter"]["decisions"] = full.pop("_presence_decisions")
            else:
                full.pop("_presence_decisions", None)
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

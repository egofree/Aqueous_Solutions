#!/usr/bin/env python3
# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Emit STREAM_REGISTER / MASS_FLOW *excerpts* derived from plant_flow_graph.json.

WP-Ap3: regenerate derived STREAM_REGISTER / MASS_FLOW excerpts into
flow_graph/derived/. CAD docs remain human+derived hybrid sync targets
(prefer derived/ as generated; pointers in cad/).
Do not invent rates or DOCK S##. Placeholders export as null / — .
"""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GRAPH = ROOT / "plant_flow_graph.json"
DERIVED = ROOT / "derived"


def load_graph() -> dict:
    return json.loads(GRAPH.read_text())


def emit_stream_register(g: dict) -> str:
    lines = [
        "# Stream register excerpt — DERIVED from flow_graph",
        "",
        "Document number: AQS-STR-001-DERIVED",
        f"Source: AQS-FLOW-GRAPH-001 Rev {g.get('revision')} (`plant_flow_graph.json`)",
        f"Generated: {date.today().isoformat()}",
        "Licence: CERN-OHL-S-2.0",
        "",
        "**Not** the legacy master while migration is incomplete — compare to `cad/STREAM_REGISTER.md`.",
        "Intra-aisle (IA-*) and TBD namespaces included for full_depth_now visibility.",
        "",
        "| ID | From | To | Ph | Layers | Presence | Carries | Rate | Gap flags |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for e in g["edges"]:
        rate = e.get("rate") or {}
        rv = rate.get("value")
        ru = rate.get("unit") or ""
        rate_s = "—" if rv is None else f"{rv} {ru}".strip()
        gaps = ",".join(e.get("gap_flags") or []) or "—"
        layers = ",".join(e.get("layers") or [])
        lines.append(
            f"| {e['stream_id']} | {e['from_unit_id']} | {e['to_unit_id']} | {e['phase']} | "
            f"{layers} | {e['presence']} | {e.get('carries') or '—'} | {rate_s} | {gaps} |"
        )
    lines.append("")
    return "\n".join(lines)


def emit_mass_flow(g: dict) -> str:
    lines = [
        "# Mass-flow claim excerpt — DERIVED from flow_graph",
        "",
        "Document number: AQS-MF-001-DERIVED",
        f"Source: AQS-FLOW-GRAPH-001 Rev {g.get('revision')} (`plant_flow_graph.json`)",
        f"Generated: {date.today().isoformat()}",
        "Licence: CERN-OHL-S-2.0",
        "",
        "**Not** the legacy master while migration is incomplete — compare to `cad/MASS_FLOW.md`.",
        "Only namespace=S and SANDBOX mass-layer edges listed (MFD campus view).",
        "",
        "| ID | Route | Claim status | Presence | Rate | Notes |",
        "|---|---|---|---|---|---|",
    ]
    for e in g["edges"]:
        if e.get("namespace") not in ("S", "SANDBOX", "TBD"):
            continue
        if "mass" not in (e.get("layers") or []) and e.get("namespace") != "TBD":
            # still show TBD dock
            if e.get("namespace") != "TBD":
                continue
        rate = e.get("rate") or {}
        rv = rate.get("value")
        rate_s = "—" if rv is None else f"{rv} {rate.get('unit') or ''}".strip()
        lines.append(
            f"| {e['stream_id']} | {e['from_unit_id']}→{e['to_unit_id']} | "
            f"{e.get('claim_status') or '—'} | {e['presence']} | {rate_s} | "
            f"{e.get('notes') or '—'} |"
        )
    lines.append("")
    return "\n".join(lines)


def emit_census(g: dict) -> str:
    nodes = g["nodes"]
    edges = g["edges"]
    np = sum(1 for n in nodes if n["presence"] == "present")
    nph = sum(1 for n in nodes if n["presence"] == "placeholder")
    ep = sum(1 for e in edges if e["presence"] == "present")
    eph = sum(1 for e in edges if e["presence"] == "placeholder")
    by_ns = {}
    for e in edges:
        by_ns[e["namespace"]] = by_ns.get(e["namespace"], 0) + 1
    lines = [
        "# Flow graph census — DERIVED",
        "",
        f"Source: AQS-FLOW-GRAPH-001 Rev {g.get('revision')}",
        f"Generated: {date.today().isoformat()}",
        "",
        f"- nodes: **{len(nodes)}** (present={np}, placeholder={nph})",
        f"- edges: **{len(edges)}** (present={ep}, placeholder={eph})",
        f"- by namespace: {by_ns}",
        f"- locks: {', '.join(g.get('locks') or [])}",
        "",
        "## Gaps",
        "",
    ]
    for gap in g.get("gaps") or []:
        lines.append(f"- **{gap.get('id')}** ({gap.get('severity')}): {gap.get('detail')}")
    lines.append("")
    return "\n".join(lines)


def emit_sync_pointer(g: dict) -> str:
    """Document hybrid: derived/ is generated; cad/STREAM+MASS remain sync targets."""
    return "\n".join(
        [
            "# Derived STREAM / MASS sync pointer — WP-Ap3",
            "",
            f"Source graph: AQS-FLOW-GRAPH-001 Rev {g.get('revision')} (`plant_flow_graph.json`)",
            f"Generated: {date.today().isoformat()}",
            "Licence: CERN-OHL-S-2.0",
            "",
            "## Generated (this directory)",
            "",
            "| File | Role |",
            "|---|---|",
            "| `STREAM_REGISTER_DERIVED.md` | Full stream table from graph edges (incl. IA-* / TBD) |",
            "| `MASS_FLOW_DERIVED.md` | Mass-layer S / SANDBOX / TBD claim excerpt |",
            "| `CENSUS.md` | Node/edge counts + gap list |",
            "",
            "## Human + derived hybrid (do not overwrite wholesale)",
            "",
            "| CAD doc | Role after WP-Ap3 |",
            "|---|---|",
            "| `cad/STREAM_REGISTER.md` (AQS-STR-001) | **Sync target** — human narrative + inter-block S## table; compare to derived |",
            "| `cad/MASS_FLOW.md` (AQS-MF-001) | **Sync target** — claim-status narrative; compare to derived |",
            "",
            "Prefer editing the graph, then:",
            "",
            "```bash",
            "cd Diagrams/aqueous_diagrams/flow_graph",
            "python3 export_authority_md.py",
            "python3 render_layer_views.py   # layer stubs still graph-driven",
            "```",
            "",
            "Do **not** invent DOCK S## or fill null placeholder rates.",
            "DOCK_EXPORT_TBD stays TBD. Layer views: `render_layer_views.py` → `views/`.",
            "",
        ]
    )


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--graph", type=Path, default=GRAPH)
    ap.add_argument("--out-dir", type=Path, default=DERIVED)
    args = ap.parse_args()
    g = json.loads(args.graph.read_text())
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "STREAM_REGISTER_DERIVED.md").write_text(emit_stream_register(g))
    (args.out_dir / "MASS_FLOW_DERIVED.md").write_text(emit_mass_flow(g))
    (args.out_dir / "CENSUS.md").write_text(emit_census(g))
    (args.out_dir / "SYNC_POINTER.md").write_text(emit_sync_pointer(g))
    print(f"Wrote derived excerpts under {args.out_dir}")


if __name__ == "__main__":
    main()

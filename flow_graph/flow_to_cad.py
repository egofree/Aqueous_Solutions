#!/usr/bin/env python3
"""Flow graph → FreeCAD placement script. Does not invent millimetres.

Reads the typed plant graph, the unit↔Feature name map, and an explicit
placement table. Emits a FreeCAD console script that sets Placement on
named Features. Edges are not routed. Rates are not sizes. Gold params.py
is not rewritten.

A unit is placed only when the table has origin_mm and level for that
unit_id, or for a block_id the unit is explicitly assigned to. Missing
rows are gaps, not boxes.

    python3 flow_to_cad.py --graph plant_flow_graph.json \\
        --map unit_freecad_map.json --placements placement_seed.json \\
        --out /tmp/apply_placement.py --report /tmp/placement_report.json

CERN-OHL-S-2.0. Aligns with AQS-3D-BUILD-001 Rev G: applicator was
deferred; this is that applicator, still without an edge auto-router.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

SCHEMA = "aqs-placement-apply-1.0"

# Level tag → world Z of that plate's FFL, mm. Only values locked in
# AQS-AUTH-001 / AQS-BLD-001. Other levels must come from params.py
# or the placement file "datums_mm". Do not infer slab thickness here.
LOCKED_DATUMS_MM = {
    "L0": 0.0,
    "L-1": -6000.0,
}


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


def issued_size(n: dict) -> list | None:
    """Graph size_mm when the node carries an issued L×W×H envelope, else None."""
    p = n.get("params") or {}
    size = p.get("size_mm")
    note = str(p.get("size_note") or "").lower()
    if isinstance(size, list) and len(size) == 3 and "issued envelope" in note:
        return [float(v) for v in size]
    return None


def index_placements(table: dict) -> tuple[dict, dict, dict]:
    """Return (by unit_id, by block_id, datums_mm)."""
    by_unit = {}
    by_block = {}
    for row in table.get("units") or []:
        uid = row.get("unit_id")
        if uid:
            by_unit[uid] = row
    for row in table.get("blocks") or []:
        bid = row.get("block_id")
        if bid:
            by_block[bid] = row
    datums = dict(LOCKED_DATUMS_MM)
    datums.update({k: float(v) for k, v in (table.get("datums_mm") or {}).items()})
    return by_unit, by_block, datums


def resolve_row(unit_id: str, by_unit: dict, by_block: dict) -> dict | None:
    if unit_id in by_unit:
        return by_unit[unit_id]
    for block in by_block.values():
        members = block.get("unit_ids") or []
        if unit_id in members:
            return block
    return None


def origin_world_mm(row: dict, datums: dict) -> tuple[float, float, float] | None:
    origin = row.get("origin_mm")
    if not (isinstance(origin, list) and len(origin) >= 2):
        return None
    level = row.get("level")
    if level not in datums and len(origin) < 3:
        return None
    z = float(origin[2]) if len(origin) >= 3 else float(datums[level])
    return float(origin[0]), float(origin[1]), z


def plan(graph: dict, unit_map: dict, table: dict, issued_envelopes: bool = True,
         create_issued: bool = False) -> dict:
    by_unit, by_block, datums = index_placements(table)
    entries = {e["unit_id"]: e for e in (unit_map.get("entries") or []) if e.get("unit_id")}
    moves = []
    gaps = []
    skipped = []
    creates = []
    size_conflicts = []
    for n in graph.get("nodes") or []:
        uid = n.get("unit_id")
        if not uid:
            continue
        if not node_enabled(n):
            skipped.append({"unit_id": uid, "reason": "disabled"})
            continue
        entry = entries.get(uid)
        names = list((entry or {}).get("freecad_names") or [])
        status = (entry or {}).get("status")
        placeholder = str(n.get("presence") or "present").lower() == "placeholder"
        row = resolve_row(uid, by_unit, by_block)
        if row is not None:
            origin = origin_world_mm(row, datums)
            if origin is None:
                gaps.append({
                    "unit_id": uid,
                    "freecad_names": names,
                    "reason": "origin_or_datum_missing",
                    "level": row.get("level"),
                })
                continue
            size = row.get("size_mm")
            explicit = "unit_id" in row and row.get("block_id") is None
            issued = issued_size(n) if (issued_envelopes and explicit) else None
            if issued is not None and isinstance(size, list) and [float(v) for v in size] != issued:
                size_conflicts.append({"unit_id": uid, "seed_size_mm": size, "issued_size_mm": issued})
                issued = None
            if create_issued and issued is not None and not names:
                # Issued envelope, explicit seed row, no Feature on the model: the
                # copy gets one envelope box named after the unit. Not a nameplate.
                creates.append({
                    "unit_id": uid,
                    "feature_name": uid,
                    "level": row.get("level"),
                    "origin_mm": list(origin),
                    "size_mm": issued,
                    "frame": "plate_world",
                })
            moves.append({
                "unit_id": uid,
                "freecad_names": names,
                "level": row.get("level"),
                "origin_mm": list(origin),
                "size_mm": size if isinstance(size, list) else None,
                "source": row.get("block_id") or uid,
                "source_doc": row.get("source"),
                "issued_size_mm": issued,
                "apply": explicit and bool(names),
                "study": placeholder,
                "frame": "plate_world",
            })
            continue
        if placeholder or status in ("unmapped", "placeholder_skip") or not names:
            skipped.append({"unit_id": uid, "reason": status or "no_feature_name_no_study_row"})
            continue
        gaps.append({"unit_id": uid, "freecad_names": names, "reason": "no_placement_row"})
    apply_moves = [m for m in moves if m["apply"]]
    seen = set()
    deduped = []
    for m in apply_moves:
        names = [n for n in m["freecad_names"] if n not in seen]
        seen.update(names)
        if names:
            deduped.append({**m, "freecad_names": names})
    return {
        "schema": SCHEMA,
        "graph_doc": graph.get("doc_id"),
        "graph_revision": graph.get("revision"),
        "map_revision": unit_map.get("revision"),
        "placement_doc": table.get("doc_id"),
        "datums_mm": datums,
        "move_count": len(moves),
        "apply_count": len(deduped),
        "gap_count": len(gaps),
        "skip_count": len(skipped),
        "by_gap": dict(Counter(g["reason"] for g in gaps)),
        "issued_envelopes": issued_envelopes,
        "resize_count": sum(1 for m in deduped if m.get("issued_size_mm")),
        "create_issued": create_issued,
        "create_count": len(creates),
        "process_nudge_mm": {"PROCESS_DX": 5000, "PROCESS_DY": 4000, "Z_Lm1": -6000},
        "nudge_rule": (
            "Seed origins are plate-world. build_plant already applies PROCESS_DX/DY "
            "to the wet cassette. Apply script sets Placement only for explicit unit "
            "rows (yard, fab wet, MeOH, shop/cryo nozzles, water stubs). Block rows "
            "are not written, so the aisle is not restacked."
        ),
        "moves": moves,
        "apply_moves": deduped,
        "create_moves": creates,
        "size_conflicts": size_conflicts,
        "gaps": gaps,
        "skipped": skipped,
        "refused": [
            "edge_auto_router",
            "size_from_rate",
            "rewrite_gold_params",
        ],
    }


def emit_freecad(report: dict, fcstd: str, out_fcstd: str) -> str:
    payload = json.dumps(report["apply_moves"])
    creates = json.dumps(report.get("create_moves") or [])
    return f'''# SPDX-License-Identifier: CERN-OHL-S-2.0
# Generated by flow_to_cad.py. Absolute plate-world Placement.
# Explicit pitch rows only. Does not restack the wet cassette.
# Rows with an issued envelope get a box of that L×W×H on the copy.
import json
import FreeCAD as App
import Part

src = {fcstd!r}
dst = {out_fcstd!r}
moves = json.loads({payload!r})
creates = json.loads({creates!r})

if src == dst:
    raise SystemExit("refusing to write the source model; dst must be a copy")
import shutil
shutil.copy2(src, dst)
doc = App.openDocument(dst)
applied = []
resized = []
created = []
missing = []
for row in moves:
    x, y, z = row["origin_mm"]
    issued = row.get("issued_size_mm")
    for i, name in enumerate(row["freecad_names"]):
        obj = doc.getObject(name)
        if obj is None:
            missing.append(name)
            continue
        if issued and i == 0:
            obj.Shape = Part.makeBox(*issued)
            resized.append(name)
        obj.Placement = App.Placement(App.Vector(x, y, z), App.Rotation())
        applied.append(name)
if creates:
    grp = doc.getObject("ISSUED_ENVELOPES") or doc.addObject("App::DocumentObjectGroup", "ISSUED_ENVELOPES")
    for row in creates:
        name = row["feature_name"]
        if doc.getObject(name) is not None:
            missing.append("exists:" + name)
            continue
        x, y, z = row["origin_mm"]
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = Part.makeBox(*row["size_mm"])
        obj.Placement = App.Placement(App.Vector(x, y, z), App.Rotation())
        grp.addObject(obj)
        created.append(name)
doc.recompute()
doc.save()
App.closeDocument(doc.Name)
print(json.dumps({{"applied": applied, "resized": resized, "created": created, "missing": missing}}))
'''


def main() -> int:
    ap = argparse.ArgumentParser(description="Graph + explicit placement table → FreeCAD placement script")
    ap.add_argument("--graph", type=Path, required=True)
    ap.add_argument("--map", type=Path, required=True)
    ap.add_argument("--placements", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True, help="FreeCAD script path")
    ap.add_argument("--report", type=Path, required=True)
    ap.add_argument("--fcstd", default="plant.FCStd")
    ap.add_argument("--fcstd-out", default="plant_placed.FCStd")
    ap.add_argument("--no-issued-envelopes", action="store_true",
                    help="Placement only; do not resize mapped Features to the issued envelope")
    ap.add_argument("--create-issued", action="store_true",
                    help="Also add an envelope box for issued units that have a seed row but no "
                         "Feature. Off by default: seed origins for those rows are not yet "
                         "reconciled with the plant model.")
    args = ap.parse_args()
    if args.fcstd == args.fcstd_out:
        ap.error("--fcstd-out must differ from --fcstd; the applicator writes a copy only")

    report = plan(load_json(args.graph), load_json(args.map), load_json(args.placements),
                  issued_envelopes=not args.no_issued_envelopes,
                  create_issued=args.create_issued)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    args.out.write_text(
        emit_freecad(report, args.fcstd, args.fcstd_out),
        encoding="utf-8",
    )
    print(
        f"moves {report['move_count']}  apply {report['apply_count']}  "
        f"resize {report['resize_count']}  create {report['create_count']}  "
        f"size_conflicts {len(report['size_conflicts'])}  "
        f"gaps {report['gap_count']}  skipped {report['skip_count']}  script {args.out}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""The views/exports/layout renderer wave (ledger section F). Reference
writers: flow_graph/export_authority_md.py (derived_excerpts),
flow_graph/loop_closure.py (loop_closure), flow_graph/export_candidate_mvs.py
(candidate_mvs), flow_graph/regen_derived.py -> flow_graph/render_layer_views.py
(regen_derived), docs-authority/_sector_definitions.py (sector_definitions),
flow_graph/param/scale_down.py (scale_down, the doc+json half; the analysis
half is flow_graph/v2/functions/scale_down.py),
flow_graph/param/placement_refine.py (placement_refine - the layout solver,
functions/placement_refine.py), docs-authority/_placement_routes.py
(placement_routes), flow_graph/param/site_3d.py (site_3d),
models/openscad/foam_ew/generate.py (foam_ew_cut_list),
docs-authority/_drawings.py (drawings), docs-authority/_pid_sheets.py
(pid_sheets). The ported render functions reproduce the v1 doc templates
exactly (same headers, document numbers, table shapes, number formats and
basis texts); the acceptance is byte-exact reproduction of the committed files
(flow_graph/v2/test_render_views.py).

Read model: the plain committed-graph structure (the seed, verbatim - the
file every section-F stage read), built once per render by _graph(). These
rows WRITE NO GRAPH STATE, and the v1 stages read the committed graph FILE;
the seed is that file. The computed overlay is deliberately NOT composed into
the books the views embed: the views are topology documents committed against
that file, and composing re-derived physics books here would couple document
bytes to physics-lane drift instead of catching it on the graph (where the
staleness gates live). Recorded drifts found at port time (family-lane
findings, recorded for those lanes): the foundry family re-derives edge
IA-CA-CL2-SHIP at 0.065072 kg/d where the committed book and v1
foundry_poly.solve() both carry 0.063248 kg/d; the farm/hab families'
grid-exact size_mm stamps emit integers where the committed books carry the
v1 floats (7310 vs 7310.0). The views ride the committed books until those
lanes reconcile.

Input payloads (the v1 stage file reads, read at the caller's I/O boundary
and passed in inputs; a caller that omits one gets loud stub bytes, never a
wrong document):
- inputs['system_tree']: flow_graph/system_tree.yaml, parsed
  (sector_definitions row);
- inputs['doc_numbers']: {'DESIGN_TOOL_ARCHITECTURE.md': number,
  'GLOSSARY.md': number} - the two front-matter numbers the v1 docnum() read
  from those pages (sector_definitions row, section 7 table);
- inputs['placement_seed']: flow_graph/placement_seed.json, parsed (site_3d
  row; the hybrid hand+generated seed placement_refine owns and
  doc_egress_hall/doc_water_tower amend).

REMAINING (rows and outputs NOT ported here, each with its reason):
- regen_derived SVGs (flow_graph/views/*.svg): rendered by the external
  graphviz binary (dot/fdp) under the committed keep-when-dot-unchanged guard
  (the init_rank flake) - an external-tool layout with file side state, not a
  pure function of the model. The JSON view and the DOT text (that render's
  exact inputs) are ported and byte-exact. media/_generated.json is the
  pattern manifest (bookkeeping; dies per the ledger).
- placement_routes (docs-authority/ISO_ROUTES.md/.json, iso/ISO_SHEETS.csv,
  ISO_SHEETS.md): executes the line-list stage namespace (runpy
  docs-authority/_line_list.py -> rows, C) for the piped rows and unit
  centres - the line_list family (section E) has not landed, so the routed
  table cannot be composed. The A-M-074 rack routing arithmetic ports as the
  renderer's pure kernel when that family lands.
- site_3d GLB (media/3d/site_model.glb): binary CAD asset (trimesh glTF
  export), outside the document registry; the SVG sheets and the coverage
  manifest are ported. Non-baseline locales have no committed golden (locale
  runs are worktree runs); the renderer renders the committed baseline
  reference model.
- foam_ew PNGs (models/openscad/foam_ew/*.png): matplotlib raster exports,
  library-version-dependent bytes; the cut list page and CSV are ported.
- drawings (docs-authority/DRAWING_REGISTER.md + the title-block stamps):
  stamps SVGs owned by OTHER stages (the graphviz views SVGs above; motor-FA
  SVGs - doc_motor_fa not landed; mfg drawing SVGs - the CAD lane) and
  composes the pid_sheets rows. Composition recorded for the composer lane:
  per drawing, the stamp is stripped (the `aqs-title-block` group regex),
  the revision is the first 8 hex of SHA-256 of the stripped content, the
  ISO_7200 block re-stamps lower right, and the register rows join the
  pid-series rows kept from the previous register (FOREIGN_ROWS keep rule),
  so the register is identical whichever of the two writers ran last.
- pid_sheets (docs-authority/pid/*.svg + _register.csv): reads the line list
  (line_list, not landed), INSTRUMENT_INDEX.csv (doc_instr_index),
  OTHER_INVENTORY.csv (inventory_other), CAUSE_EFFECT.md (doc_sif) and the
  hand+generated nozzle CSVs (nozzle_sched, none landed). The DRAWING_REGISTER
  append is the doc-on-doc write-back recorded above (idempotent foreign-row
  keep under the count line). pid/_generated.json is bookkeeping (dies).
- placement_refine (flow_graph/placement_seed.json): the solver is ported
  (functions/placement_refine.py); the seed file is the hybrid payload above.
  Golden: idempotence at the committed fixpoint + reference equivalence with
  the v1 module (see that module's docstring).

Pure: no I/O here - the registry returns bytes and file writing stays
outside.
"""
import collections
import csv
import importlib.util
import io
import json
import math
import os
from copy import deepcopy

from flow_graph.v2.functions import scale_down as _SD          # the analysis kernel

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def _graph(m):
    """The plain committed-graph structure the v1 section-F stages read: the
    seed, verbatim (load() parsed it from that file; serialization reproduces
    its bytes). Read-only.

    The computed overlay is deliberately NOT composed here. These rows write
    no graph state, and the documents committed are projections of the
    committed file itself; composing re-derived physics books would couple
    document bytes to physics-lane drift instead of catching it on the graph
    (where the staleness gates live). Drifts observed at port time, both
    family-lane findings against their own committed books, recorded for
    those lanes: the foundry family re-derives edge IA-CA-CL2-SHIP at
    0.065072 kg/d where the committed book and v1 foundry_poly.solve() both
    carry 0.063248 kg/d; and the farm/hab families' grid-exact size_mm stamps
    emit integers (7310) where the committed books carry the v1 floats
    (7310.0). The views ride the committed books until those lanes
    reconcile."""
    return deepcopy(m.data)


def _stub(path, key):
    """The loud bytes a caller gets when it does not carry the payload the
    renderer reads. render() over a partial payload set (a sibling wave's
    whole-registry pass) stays bytes-valued; the acceptance path is
    render_one with the full payload set."""
    return (f'# {path}: pending render - input payload {key!r} not provided by this caller '
            f'(the v1 stage read it as a file; the acceptance caller passes it in inputs)\n').encode('utf-8')


# ---- derived_excerpts (flow_graph/export_authority_md.py, WP-Ap3) --------------

def render_stream_register(m, inputs):
    """flow_graph/derived/STREAM_REGISTER_DERIVED.md (AQS-STR-001-DERIVED)."""
    g = _graph(m)
    lines = [
        "# Stream register excerpt — DERIVED from flow_graph",
        "",
        "Document number: AQS-STR-001-DERIVED",
        f"Source: AQS-FLOW-GRAPH-001 Rev {g.get('revision')} (`plant_flow_graph.json`)",
        f"Graph date: {g.get('date')} (output is a pure function of the graph; no run date, so regen is idempotent)",
        "Licence: CERN-OHL-S-2.0",
        "",
        "**Not** the legacy master while migration is incomplete — compare to `docs-authority/STREAM_REGISTER.md`.",
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
            f"{layers} | {e.get('presence') or ''} | {e.get('carries') or '—'} | {rate_s} | {gaps} |"
        )
    lines.append("")
    return "\n".join(lines).encode("utf-8")


def render_mass_flow(m, inputs):
    """flow_graph/derived/MASS_FLOW_DERIVED.md (AQS-MF-001-DERIVED)."""
    g = _graph(m)
    lines = [
        "# Mass-flow claim excerpt — DERIVED from flow_graph",
        "",
        "Document number: AQS-MF-001-DERIVED",
        f"Source: AQS-FLOW-GRAPH-001 Rev {g.get('revision')} (`plant_flow_graph.json`)",
        f"Graph date: {g.get('date')} (output is a pure function of the graph; no run date, so regen is idempotent)",
        "Licence: CERN-OHL-S-2.0",
        "",
        "**Not** the legacy master while migration is incomplete — compare to `docs-authority/MASS_FLOW.md`.",
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
            f"{e.get('claim_status') or '—'} | {e.get('presence') or ''} | {rate_s} | "
            f"{e.get('notes') or '—'} |"
        )
    lines.append("")
    return "\n".join(lines).encode("utf-8")


def render_census(m, inputs):
    """flow_graph/derived/CENSUS.md."""
    g = _graph(m)
    nodes = g["nodes"]
    edges = g["edges"]
    np = sum(1 for n in nodes if n.get("presence") == "present")
    nph = sum(1 for n in nodes if n.get("presence") == "placeholder")
    ep = sum(1 for e in edges if e.get("presence") == "present")
    eph = sum(1 for e in edges if e.get("presence") == "placeholder")
    by_ns = {}
    for e in edges:
        ns = e.get("namespace")
        if ns is None:
            sid = e.get("stream_id") or ""
            if sid.startswith("IA-"):
                ns = "IA"
            elif sid.startswith("SANDBOX"):
                ns = "SANDBOX"
            elif sid.startswith("TBD") or "TBD" in sid:
                ns = "TBD"
            elif sid.startswith("S") and len(sid) > 1 and sid[1].isdigit():
                ns = "S"
            else:
                ns = "unknown"
        by_ns[ns] = by_ns.get(ns, 0) + 1
    lines = [
        "# Flow graph census — DERIVED",
        "",
        f"Source: AQS-FLOW-GRAPH-001 Rev {g.get('revision')}",
        f"Graph date: {g.get('date')} (output is a pure function of the graph; no run date, so regen is idempotent)",
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
    return "\n".join(lines).encode("utf-8")


def render_sync_pointer(m, inputs):
    """flow_graph/derived/SYNC_POINTER.md (WP-Ap3)."""
    g = _graph(m)
    text = "\n".join(
        [
            "# Derived STREAM / MASS sync pointer — WP-Ap3",
            "",
            f"Source graph: AQS-FLOW-GRAPH-001 Rev {g.get('revision')} (`plant_flow_graph.json`)",
            f"Graph date: {g.get('date')} (output is a pure function of the graph; no run date, so regen is idempotent)",
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
            "| `docs-authority/STREAM_REGISTER.md` (AQS-STR-001) | **Sync target** — human narrative + inter-block S## table; compare to derived |",
            "| `docs-authority/MASS_FLOW.md` (AQS-MF-001) | **Sync target** — claim-status narrative; compare to derived |",
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
    return text.encode("utf-8")


# ---- loop_closure (flow_graph/loop_closure.py; stays a check) ------------------

_LC_EPS = float('1e-9')     # the balance floor of the v1 cut test
_LC_TOL = float('0.01')     # the 1 % cut/unit tolerance


def _tarjan(nodes, edges):
    adj = collections.defaultdict(list)
    for a, b in edges:
        adj[a].append(b)
    index = {}
    low = {}
    stack = []
    on = set()
    comps = []
    counter = [0]

    def strong(v):
        i = counter[0]
        index[v] = low[v] = i
        counter[0] += 1
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


def _johnson(nodes, edges, limit, visit_cap=20000):
    """Elementary cycles. Stops at limit or visit_cap. Returns (cycles, stopped_early)."""
    adj = collections.defaultdict(list)
    for a, b, s in edges:
        adj[a].append((b, s))
    order = {n: i for i, n in enumerate(sorted(nodes))}
    cycles = []
    visits = [0]
    stopped = [False]

    def walk(start, v, path, seen):
        if stopped[0] or len(cycles) >= limit:
            return
        visits[0] += 1
        if visits[0] > visit_cap:
            stopped[0] = True
            return
        for w, sid in adj[v]:
            if stopped[0] or len(cycles) >= limit:
                return
            if w == start and path:
                cycles.append(path + [sid])
            elif w not in seen and order.get(w, -1) > order[start]:
                seen.add(w)
                walk(start, w, path + [sid], seen)
                seen.remove(w)

    for n in sorted(nodes, key=lambda x: order[x]):
        if stopped[0] or len(cycles) >= limit:
            break
        walk(n, n, [], {n})
    return cycles, stopped[0]


def _one_circuit(nodes, edges):
    """One directed circuit, if the component has one. Not a census."""
    adj = collections.defaultdict(list)
    for a, b, s in edges:
        adj[a].append((b, s))
    seen = set()
    stack = []
    on = set()

    def walk(v):
        seen.add(v)
        on.add(v)
        stack.append(v)
        for w, _sid in adj[v]:
            if w not in seen:
                found = walk(w)
                if found:
                    return found
            elif w in on:
                path = stack[stack.index(w):] + [w]
                sids = []
                for a, b in zip(path, path[1:]):
                    sids.append(next(s for x, s in adj[a] if x == b))
                return sids
        stack.pop()
        on.remove(v)
        return None

    for n in nodes:
        if n not in seen:
            found = walk(n)
            if found:
                return found
    return None


def _lc_node_gap(edges, uid, unit):
    inn = out = 0
    for e in edges:
        r = e.get("rate") or {}
        if r.get("unit") != unit:
            continue
        if e["to_unit_id"] == uid:
            inn += r.get("value") or 0
        if e["from_unit_id"] == uid:
            out += r.get("value") or 0
    return inn, out


def _lc_component_cut(edges, members, unit):
    inside = set(members)
    enter = leave = 0
    for e in edges:
        r = e.get("rate") or {}
        if r.get("unit") != unit:
            continue
        a, b = e["from_unit_id"], e["to_unit_id"]
        if a not in inside and b in inside:
            enter += r.get("value") or 0
        elif a in inside and b not in inside:
            leave += r.get("value") or 0
    return enter, leave


def _lc_report(g, limit=20):
    by = collections.defaultdict(list)
    for e in g["edges"]:
        if e.get("presence") != "present":
            continue
        for layer in e.get("layers") or ["none"]:
            by[layer].append(e)
    lines = [
        f"Graph Rev {g['revision']}. Closure is the cut around each Tarjan component.",
        "A component passes when every unit balances and the cut balances, per rate unit, within 1%.",
        "Pass is on the present edges in this file. It is not on-site evidence.",
        "This result is not the MVS flag. mvs.mvs_criteria.loops_closed is not set here.",
        "",
    ]
    any_fail = False
    for layer in ("mass", "thermal", "elec", "ess"):
        edges = by.get(layer, [])
        nodes = sorted({e["from_unit_id"] for e in edges} | {e["to_unit_id"] for e in edges})
        pairs = [(e["from_unit_id"], e["to_unit_id"]) for e in edges]
        comps = [c for c in _tarjan(nodes, pairs) if len(c) > 1]
        lines.append(f"## {layer}: {len(edges)} edges, {len(comps)} loops")
        for comp in sorted(comps, key=len, reverse=True):
            units = sorted({(e.get("rate") or {}).get("unit") for e in edges   # R11 Rev AC regen: 80 present edges carry null rates (unit/value None); they carry no balance and are skipped below by the unit test
                            if (e["from_unit_id"] in comp or e["to_unit_id"] in comp)
                            and (e.get("rate") or {}).get("unit") is not None})
            triple = [(e["from_unit_id"], e["to_unit_id"], e["stream_id"]) for e in edges]
            named, stopped = _johnson(comp, triple, limit)
            witness = _one_circuit(comp, triple)
            if stopped:
                lines.append(
                    f"- {len(comp)} units. Circuits listed: {len(named)} (cap {limit}). "
                    "Elementary search stopped at the visit cap. Closure is the cut, not the circuit list."
                )
            else:
                lines.append(f"- {len(comp)} units. Circuits listed: {len(named)} (cap {limit}).")
            lines.append("  " + ", ".join(sorted(comp)[:14]) + (" ..." if len(comp) > 14 else ""))
            shown = named[0][:8] if named else (witness[:8] if witness else None)
            if shown:
                lines.append("  one circuit: " + " -> ".join(shown))
            for unit in units:
                bad = []
                for uid in comp:
                    inn, out = _lc_node_gap(edges, uid, unit)
                    if inn == 0 and out == 0:
                        continue
                    if abs(inn - out) / max(inn, out, _LC_EPS) > _LC_TOL:
                        bad.append(uid)
                enter, leave = _lc_component_cut(edges, comp, unit)
                cut = abs(enter - leave) / max(enter, leave, _LC_EPS) > _LC_TOL
                status = "fail" if bad or cut else "pass"
                if status == "fail":
                    any_fail = True
                lines.append(
                    f"  {unit}: nodes off {len(bad)}, cut in {enter:.2f} out {leave:.2f} {status}"
                )
        lines.append("")
    lines.append("loops_closed: false" if any_fail else "loops_closed: true")
    lines.append("This result is the cut test. It is not the MVS flag.")
    return "\n".join(lines)


def render_loop_closure(m, inputs):
    """flow_graph/derived/LOOP_CLOSURE.md (the cut-balance report; the check
    itself is the test lane's to run on these bytes)."""
    return (_lc_report(_graph(m)) + "\n").encode("utf-8")


# ---- candidate_mvs (flow_graph/export_candidate_mvs.py, WP-Ap1) ----------------

def _mvs_stream(edge):
    rate_raw = edge.get("rate")
    rate = None
    if isinstance(rate_raw, dict):
        # Graph uses status "null"; MVS projection uses RateStatus "tbd"
        st = rate_raw.get("status") or "tbd"
        if st in ("null", "None"):
            st = "tbd"
        rate = {
            "value": rate_raw.get("value"),
            "unit": rate_raw.get("unit") or "",
            "status": st,
            "note": rate_raw.get("note"),
        }
    stream = {
        "stream_id": edge["stream_id"],
        "from_unit_id": edge["from_unit_id"],
        "to_unit_id": edge["to_unit_id"],
        "phase": edge.get("phase") or "L",
        "carries": edge.get("carries"),
        "rate": rate,
        "from_sector_id": edge.get("from_sector_id"),
        "to_sector_id": edge.get("to_sector_id"),
        "open_boundary": bool(edge.get("open_boundary", False)),
    }
    # Honest null-rate labels for projection consumers (WP-A1)
    if rate is None or rate.get("value") is None:
        if edge.get("open_boundary") or edge.get("namespace") == "TBD":
            stream["null_rate_kind"] = "open_boundary"
        elif edge.get("presence") == "placeholder":
            stream["null_rate_kind"] = "study_deferred"
        elif edge.get("namespace") == "IA":
            stream["null_rate_kind"] = "inventory_cycle"
        else:
            stream["null_rate_kind"] = "unknown"
    note_parts = []
    if edge.get("notes"):
        note_parts.append(str(edge["notes"]))
    if edge.get("gap_flags"):
        note_parts.append("gap_flags=" + ",".join(edge["gap_flags"]))
    if edge.get("presence") == "placeholder":
        note_parts.append("presence=placeholder")
    if edge.get("namespace") and edge["namespace"] != "S":
        note_parts.append(f"namespace={edge['namespace']}")
    layers = edge.get("layers") or []
    if layers:
        note_parts.append("layers=" + ",".join(layers))
    if note_parts:
        stream["note"] = "; ".join(note_parts)
    return stream


def _mvs_unit(node):
    return {
        "unit_id": node["unit_id"],
        "sector_id": node["sector_id"],
        "enabled": bool(node.get("enabled", True)),
        "class": node.get("class"),
        "tags": list(node.get("tags") or []),
        "params": dict(node.get("params") or {}),
        "modules": list(node.get("modules") or []),
        "electrical_role": node.get("electrical_role"),
        "continuous_kw": node.get("continuous_kw"),
    }


def render_candidate_mvs(m, inputs):
    """design_tool/aqs_design_tool/data/candidate_mvs.json (the design-tool
    projection; the single write path from the graph)."""
    g = _graph(m)
    mvs = g.get("mvs")
    if not isinstance(mvs, dict):
        raise ValueError("plant_flow_graph.json missing mvs{} block - run fold / seed with WP-Ap1 fields first")
    units = [_mvs_unit(n) for n in g.get("nodes") or []]
    streams = [_mvs_stream(e) for e in g.get("edges") or []]
    marker = (
        "GENERATED projection of AQS-FLOW-GRAPH-001 rev "
        f"{g.get('revision')} (plant_flow_graph.json). Single write path = "
        "plant_flow_graph.json (nodes/edges + mvs). Do not edit this file; "
        "regenerate via flow_graph/export_candidate_mvs.py. Never "
        "mvs_equivalent from topology alone."
    )
    base_notes = mvs.get("notes") or ""
    notes = f"{base_notes}\n{marker}".strip() if base_notes else marker
    out = {
        "schema_version": mvs.get("schema_version", "aqs-mvs-0.3"),
        "doc_id": mvs.get("doc_id", "AQS-MVS-001"),
        "revision": mvs.get("revision", "E-candidate"),
        "licence": mvs.get("licence", g.get("licence", "CERN-OHL-S-2.0")),
        "scale_m": mvs.get("scale_m", float('1.0')),
        "status": mvs.get("status", "candidate"),
        "mvs_criteria": mvs.get("mvs_criteria") or {},
        "site": mvs.get("site") or {},
        "sectors": mvs.get("sectors") or [],
        "units": units,
        "streams": streams,
        "electrical": mvs.get("electrical") or {},
        "scale_rules": mvs.get("scale_rules") or {},
        "ui": mvs.get("ui") or {},
        "gaps": [],
        "unclosed_streams": [],
        "notes": notes,
    }
    # Honesty: never claim closed loops from projection
    crit = out["mvs_criteria"]
    if isinstance(crit, dict):
        crit.setdefault("loops_closed", False)
        sc = crit.get("self_copy")
        if isinstance(sc, dict) and "mvs_equivalent" in sc:
            sc["mvs_equivalent"] = False
    return (json.dumps(out, indent=2) + "\n").encode("utf-8")


# ---- regen_derived (flow_graph/render_layer_views.py; the JSON + DOT half) -----

# Campus footprint sectors always shown on MFD even without mass edges
# (HYDRO electrical/ESS edges live on EFD; DOCK mass edge is TBD namespace).
_MFD_FORCE_SECTORS = frozenset({"DOCK", "PUMPED_HYDRO"})

_PRESETS = {
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
        "force_sectors": _MFD_FORCE_SECTORS,
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

_LAYER_EDGE_COLOR = {
    "mass": "#1b5e20",
    "elec": "#1e3a8a",
    "thermal": "#b45309",
    "ess": "#6d28d9",
}

_HIGHLIGHT_STREAMS = frozenset(
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

_VIEW_TITLES = {
    "pfd": "PFD line view (all layers)",
    "mfd": "MFD campus / mass view",
    "efd-elec": "EFD electrical layer (S17 + peers)",
    "efd-thermal": "EFD thermal layer",
    "efd-ess": "EFD ESS charge/discharge layer",
}


def _escape(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


def _filter_view(g, cfg):
    layers = cfg.get("layers")
    ns_allow = cfg.get("namespaces")
    force_sectors = cfg.get("force_sectors") or frozenset()
    edges = []
    used_nodes = set()
    for e in g["edges"]:
        if not cfg.get("include_placeholders", True) and e.get("presence") == "placeholder":
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


def _to_dot(view, title):
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

    by_sector = collections.defaultdict(list)
    for n in view["nodes"]:
        by_sector[n["sector_id"]].append(n)

    for sector, nodes in sorted(by_sector.items()):
        lines.append(f'  subgraph "cluster_{_escape(sector)}" {{')
        lines.append(f'    label="{_escape(sector)}";')
        lines.append('    style=rounded; color="#94a3b8";')
        for n in nodes:
            presence = n.get("presence", "present")
            fill = "#e2e8f0" if presence == "placeholder" else "#ffffff"
            if n["sector_id"] in _MFD_FORCE_SECTORS:
                fill = "#fef3c7" if presence == "placeholder" else "#fde68a"
            gap = n.get("diagram_gap") or ""
            label = f"{n['unit_id']}"
            if presence == "placeholder":
                label += "\\n(placeholder)"
            if gap and n["sector_id"] in _MFD_FORCE_SECTORS:
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
        color = _LAYER_EDGE_COLOR.get(layers[0], "#334155")
        sid = e["stream_id"]
        penwidth = "2.2" if sid in _HIGHLIGHT_STREAMS else "1.2"
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


def _view_renderer(key, kind):
    """The JSON or DOT bytes of one layer view (the two renderer-side halves of
    the v1 regen_derived pass; the graphviz SVG render stays outside)."""
    def f(m, inputs):
        view = _filter_view(_graph(m), _PRESETS[key])
        if kind == 'json':
            return (json.dumps(view, indent=2) + "\n").encode("utf-8")
        return _to_dot(view, _VIEW_TITLES[key]).encode("utf-8")
    f.__name__ = f'render_view_{key.replace("-", "_")}_{kind}'
    f.__doc__ = f'flow_graph/views/{key}.{kind}: the {kind.upper()} half of the {key} layer view.'
    return f


# ---- sector_definitions (docs-authority/_sector_definitions.py, AQS-SEC-001) ---

_REVISION, _REV_DATE = 'I', '2026-10-25'     # bump when this generator's structure changes


def _sdt_cell(x):
    return str(x).replace('|', '/').replace('\n', ' ').strip()


def render_sector_definitions(m, inputs):
    """docs-authority/SECTOR_DEFINITIONS.md (AQS-SEC-001): sectors from
    mvs.sectors, units from the graph nodes, trains from the system tree
    (payload), classes/ESS peers/retired ids/aliases from the design-tool
    catalogue module. Payloads: inputs['system_tree'] (parsed YAML),
    inputs['doc_numbers'] (the DESIGN_TOOL_ARCHITECTURE/GLOSSARY front-matter
    numbers the v1 docnum() read)."""
    tree = inputs.get('system_tree')
    doc_numbers = inputs.get('doc_numbers') or {}
    if tree is None:
        return _stub('docs-authority/SECTOR_DEFINITIONS.md', 'system_tree')
    if 'DESIGN_TOOL_ARCHITECTURE.md' not in doc_numbers or 'GLOSSARY.md' not in doc_numbers:
        return _stub('docs-authority/SECTOR_DEFINITIONS.md', 'doc_numbers')
    from design_tool.aqs_design_tool import sector_definitions as _mod   # the catalogue classes/peers/aliases
    g = _graph(m)
    sectors = g['mvs']['sectors']
    units = collections.defaultdict(list)
    for n in g['nodes']:
        units[n['sector_id']].append(n['unit_id'])
    trains = collections.defaultdict(list)
    desc = {}
    for n in tree['nodes']:
        if not n.get('parent'):
            desc[n['id']] = ' '.join(str(n.get('description', '')).split())
        elif '.' not in n['parent'] and not n.get('unit_id'):
            trains[n['parent']].append(n['id'].split('.', 1)[1])

    L = ['# Sector definitions', '',
         'Document number: AQS-SEC-001  ', f'Revision: {_REVISION}  ', f'Date: {_REV_DATE}  ',
         'Generated by `docs-authority/_sector_definitions.py` from the sector list `mvs.sectors` in the plant flow '
         f'graph (AQS-FLOW-GRAPH-001, graph Rev {g["revision"]}, {g["date"]}) and from the system tree '
         '(AQS-SYS-TREE-001). Do not edit this page by hand. Change the graph, the system tree or '
         '`design_tool/aqs_design_tool/sector_definitions.py`, then run the pipeline. Not a PE stamp.', '',
         '| Rev | Description | Date |', '|---|---|---|',
         '| A–G | Catalogue written by hand, with its rulings on ambiguous names (A1 to A9). The text is in the git history. | 2026-10-01 |',
         '| H | Generated from the graph after the sectors were reorganised at graph revision AC: WET renamed DIGESTER; '
         'ELEC_PV, ZNBR2, BACKUP_GEN and FUEL_CELL became units in ELEC; TRR retired; FOUNDRY, POLYMERS and HEAT added. | 2026-10-24 |',
         f'| I | Purpose and scope added; generator text rewritten to the documentation style guide (AQS-DOC-002); the catalogue split into three tables. | {_REV_DATE} |', '',
         'Licence: CERN-OHL-S-2.0.', '',
         '## 1. Purpose and scope', '',
         'The plant is divided into sectors. A sector is a group of units that together perform one function, such as '
         'metal recovery, water treatment or power distribution. Each sector has an identifier, its `sector_id`, '
         'which the plant flow graph, the solver, the design tool and the documents all use.', '',
         'This page lists every sector in the graph and assigns each one to exactly one sector definition class, '
         'which states the kind of function it performs. It also states whether the sector is needed to close the '
         'loops of the minimum viable system (MVS), the smallest set of sectors that closes every mass, energy and '
         'life-support loop. The page then lists the energy storage systems (ESS) that the MVS needs, the sector '
         'identifiers that are no longer used, and the names that look like sector identifiers but are not.', '',
         'The graph holds the sector list; this page only presents it. The test `flow_graph/test_doc_consistency.py` '
         'fails if the design-tool catalogue or the sector table in the repository README no longer matches the '
         'graph.', '',
         '## 2. Sector definition classes', '',
         'The class list is set by AQS-UI-001, section 3.1. A new class needs a project decision. Table 2.1 lists '
         'the classes and the sectors that currently belong to each.', '',
         'Table 2.1. Sector definition classes', '',
         '| Class | Sectors in the class |', '|---|---|']
    by_def = collections.defaultdict(list)
    for s in sectors:
        by_def[s['sector_definition']].append(s['sector_id'])
    for c in _mod.SectorDefinition:
        L.append(f'| {c.value} | {", ".join(by_def.get(c.value, [])) or "—"} |')
    unknown = sorted(set(by_def) - {c.value for c in _mod.SectorDefinition})
    if unknown:
        raise ValueError(f'graph uses Sector Definitions outside AQS-UI-001 §3.1: {unknown}')

    L += ['', '## 3. Catalogue', '',
          'Table 3.1 gives one row per sector, in the order of the graph. The column "MVS" is the graph flag '
          '`required_for_mvs_closure`: true means the sector is needed to close the MVS loops. The column "Enabled" is '
          'false when a sector is switched off in the model. The unit count is taken from the graph nodes. A train is '
          'a group of units inside a sector, taken from the first level below the sector in the system tree.', '',
          'Table 3.1. Sectors', '',
          '| sector_id | Sector definition | MVS | Enabled | Units | Trains |',
          '|---|---|---|---|---|---|']
    for s in sectors:
        sid = s['sector_id']
        L.append(f'| {sid} | {s["sector_definition"]} | {str(s["required_for_mvs_closure"]).lower()} | '
                 f'{str(s.get("enabled", True)).lower()} | {len(units.get(sid, []))} | '
                 f'{", ".join(sorted(trains.get(sid, []))) or "—"} |')
    L += ['', 'Table 3.2 gives the description of each sector held in the system tree.', '',
          'Table 3.2. Sector descriptions from the system tree (AQS-SYS-TREE-001)', '',
          '| sector_id | Description |', '|---|---|']
    for s in sectors:
        L.append(f'| {s["sector_id"]} | {_sdt_cell(desc.get(s["sector_id"], "—"))} |')
    L += ['', 'Table 3.3 gives the note held against each sector in the graph. The notes record the origin of the '
          'sector and the documents that set its scope.', '',
          'Table 3.3. Sector notes from the graph', '',
          '| sector_id | Note |', '|---|---|']
    for s in sectors:
        L.append(f'| {s["sector_id"]} | {_sdt_cell(s.get("notes", "")) or "—"} |')

    L += ['', '## 4. Energy storage peers', '',
          'The MVS needs every one of its energy storage peers: the energy storage systems that back each other up. '
          'The peers that are whole sectors are '
          + ', '.join(sorted(_mod.ESS_PEER_SECTOR_IDS)) + '. The peers that are units inside a sector are '
          + ', '.join(f'{u} ({next((n["sector_id"] for n in g["nodes"] if n["unit_id"] == u), "not in graph")})'
                      for u in sorted(_mod.ESS_PEER_UNIT_IDS))
          + '. A design study in the design tool may switch a peer off. The solver then reports `'
          + _mod.UNRECLAIMED_RESOURCE_REASON + '` for that peer and does not report the loops as closed.', '',
          '## 5. Retired sector identifiers', '',
          'Older documents and dated notes may use the identifiers in Table 5.1. Read each one as the current sector '
          'shown in the same row.', '',
          'Table 5.1. Retired sector identifiers', '',
          '| Former id | Now | Since | Note |', '|---|---|---|---|']
    for old, r in sorted(_mod.RETIRED_SECTOR_IDS.items()):
        L.append(f'| {old} | {", ".join(r["now"]) or "retired"} | {r["when"]} | {_sdt_cell(r["note"])} |')
    L += ['', '## 6. Aliases and non-sector names', '',
          'The names in Table 6.1 appear in older documents, drawings or CAD groups but are not sector identifiers. '
          'Do not use them as a `sector_id`; read each one as shown.', '',
          'Table 6.1. Names that are not sector identifiers', '', '| Name | Meaning |', '|---|---|']
    for k, v in sorted(_mod.NON_SECTOR_ALIASES.items()):
        L.append(f'| `{k}` | {_sdt_cell(v)} |')
    L += ['', '## 7. Related documents', '',
          'Table 7.1. Related documents', '',
          '| Document | Number | Role |', '|---|---|---|',
          '| `flow_graph/plant_flow_graph.json` | AQS-FLOW-GRAPH-001 | The single source of plant topology; `mvs.sectors` is the sector list |',
          '| `flow_graph/system_tree.yaml` | AQS-SYS-TREE-001 | Breaks each sector down into trains and units |',
          f'| [DESIGN_TOOL_ARCHITECTURE.md](DESIGN_TOOL_ARCHITECTURE.md) | {doc_numbers["DESIGN_TOOL_ARCHITECTURE.md"]} | Sets the sector definition class list (section 3.1) |',
          f'| [GLOSSARY.md](GLOSSARY.md) | {doc_numbers["GLOSSARY.md"]} | Sector and unit terms |', '']
    return '\n'.join(L).encode('utf-8')


# ---- scale_down (flow_graph/param/scale_down.py; doc+json half) -----------------

_SCALE_REVISION, _SCALE_DATE = 'F', '2026-10-29'


def _sd_table(head, rows):
    return ['| ' + ' | '.join(head) + ' |', '|' + '---|' * len(head)] + ['| ' + ' | '.join(map(str, r)) + ' |' for r in rows]


def _sd_page(a, units_off, hand_rules):
    L = []
    w = L.append
    w('# What goes unreclaimed when the plant is made smaller or a sector is switched off')
    w('')
    w('Document number: AQS-SCALE-UR-001  ')
    w(f'Revision: {_SCALE_REVISION}  ')
    w(f'Date: {_SCALE_DATE}  ')
    w('Generated by `flow_graph/param/scale_down.py` from the plant graph; do not edit by hand.  ')
    w('Not a PE stamp.')
    w('')
    L += _sd_table(['Rev', 'Description', 'Date'], [
        ['A', 'First map from switched-off sectors to the streams left unreclaimed', '2026-10-01'],
        ['B', 'Methanol and pumped-hydro scale notes; study-unit streams', '2026-10-01'],
        ['C', 'Unit-level map for units switched off inside a running sector', '2026-10-01'],
        ['D', 'Sector names brought to the current sector list', '2026-10-24'],
        ['E', 'Rewritten in plain language. Sector lists now computed from the graph by a balance on each sector, which '
              'closes the open FOUNDRY, POLYMERS and HEAT rows. Scale-down limits derived for those three sectors.', '2026-10-24'],
        ['F', 'Summary renamed purpose and scope; the revision history removed from the summary; the terms table captioned.', _SCALE_DATE]])
    w('')
    w('## 1. Purpose and scope')
    w('')
    w('The design tool lets a user plan a smaller plant, or switch parts of it off. The plant is designed so that every '
      'material and heat stream is used again somewhere: scrap is remelted, chlorine goes back to the leach, waste heat '
      'is stored and reused. When a part is missing, the streams it used to take in have nowhere to go, and the streams '
      'it used to send out stop arriving. This page lists those streams so the design tool reports them as unreclaimed '
      'resources, open problems to solve, instead of treating the plant as still closed.')
    w('')
    w('Two questions are answered here:')
    w('')
    w('1. If a sector is switched off, which streams are left unreclaimed? (Section 3.)')
    w('2. If the plant is built smaller, how small can each sector go before it stops working, and what does a '
      'smaller size cost? (Section 4.)')
    w('')
    w('Every list on this page is computed from the plant graph by a balance on each sector, and the size limits of '
      'section 4 come from the mass and energy balances of the sectors concerned.')
    w('')
    w('## 2. Terms')
    w('')
    w('Table 2.1 defines the terms used on this page.')
    w('')
    w('Table 2.1. Terms')
    w('')
    L += (_sd_table(['Term', 'Meaning'], [
        ['Sector', 'A group of units that does one job, such as FOUNDRY (metal production). The sector list is the plant graph\'s, AQS-SEC-001.'],
        ['Stream', 'A flow of material, heat or electricity between two units, named by its stream id in the plant graph.'],
        ['Unreclaimed resource', 'A stream that the full plant reuses but that has no destination (or no source) in the configuration being studied.'],
        ['Scale factor, s', 'The plant size relative to the baseline design (SCALE_M in AQS-SCALE-001). s = 0.5 is a plant with half the throughput.'],
        ['Campaign', 'Running a unit at its normal rate for part of the time, and storing feed between runs, instead of running it slowly all the time.'],
        ['Standing loss', 'Heat that leaks out of a hot vessel through its insulation whether or not it is in use.'],
    ]))
    w('')
    w('## 3. Switching a sector off')
    w('')
    w('### 3.1 Method')
    w('')
    w('Draw a boundary round the sector and list every stream that crosses it (a mass and energy balance on a control '
      'volume). When the sector is off, each of those streams loses one end:')
    w('')
    w('- A stream coming in from another sector loses its sink. The material or heat is left unreclaimed in the sector that makes it.')
    w('- A stream going out to another sector loses its source. That sector goes short of something it needs.')
    w('- Electrical feeds, including electric heaters that top up a heat store, and purchased imports stop. Exports and vents through the dock stop with the sector. Neither is a closure gap.')
    w('- A stream whose rate is zero in the current design carries nothing today. It is listed for completeness only.')
    w('')
    w('The generator recomputes these lists from the plant graph on every regeneration, so they follow design changes. The '
      'design tool reads the same data (`design_tool/aqs_design_tool/data/scale_down.json`).')
    w('')
    w('### 3.2 Results')
    w('')
    w('Tables 3.1 to 3.%d give, for each sector, the streams that cross its boundary and what happens to each when that '
      'sector is off. Rates are design rates from the plant graph; streams that carry nothing in the current design are '
      'left out.' % len(a['sector_off']))
    w('')
    what = {'no_sink': 'left without a sink: unreclaimed', 'no_source': 'left without a source: consumer goes short', 'stops': 'stops with the sector'}
    for k, (sid, r) in enumerate(a['sector_off'].items(), 1):
        w(f"Table 3.{k}. {sid} off. Sector type: {a['definitions'].get(sid) or 'not defined'}.")
        w('')
        rows = [[x['stream_id'], f"{x['from']} to {x['to']}", x['other_sector'], _SD.fmt(x['rate'], x['unit'] or ''), what[role]]
                for role in ('no_sink', 'no_source', 'stops') for x in r[role]]
        if rows:
            L.extend(_sd_table(['Stream', 'From and to', 'Other sector', 'Design rate', 'When the sector is off'], rows))
        else:
            w('No stream crosses this sector\'s boundary in the current design.')
        w('')
    w('### 3.3 Units switched off inside a running sector')
    w('')
    U = len(a['sector_off']) + 1
    w('Some units can be switched off while the rest of their sector runs. Table 3.%d lists those that have their own entry ' % U +
      'in the design tool (`UNIT_OFF_UNRECLAIMED` in `design_tool/aqs_design_tool/solver/scale_down_map.py`).')
    w('')
    w(f'Table 3.{U}. Streams left unreclaimed when a single unit is off')
    w('')
    L += _sd_table(['Unit off', 'Streams', 'Effect'], [[u, ', '.join(e['stream_ids']) or 'none', e['detail']] for u, e in units_off.items()])
    w('')
    w('## 4. Building the plant smaller')
    w('')
    w('### 4.1 Method')
    w('')
    w('Throughput is taken as proportional to the scale factor s (assumption A-M-329; AQS-SCALE-001 gives the baseline feed of '
      '150 kg/d at s = 1). Equipment does not shrink smoothly: a crucible, an electrolysis cell or a heat store has a '
      'smallest practical size, and some losses do not fall with throughput. For each unit type the question is therefore '
      'what stops working, or what gets worse, as s falls. Batch and campaign operation are the usual answer at small '
      'production rates [2]. Values used below come from the plant graph; values not yet confirmed by test are in the '
      'assumptions register with the test that will confirm them.')
    w('')
    lim = a['limits']
    w('### 4.2 HEAT: heat stores')
    w('')
    w('A heat store recovers waste heat from other sectors and gives it back later. Its recovered heat in is the waste heat it receives from other sectors plus the heat passed down from the store one tier hotter. Exchanges between the A and B twins of a tier cancel and are not counted, and purchased electric trim heat is not recovered heat. Its standing loss depends on its '
      'surface area, insulation and temperature, not on how much heat passes through it [3, 4]. If the store keeps its '
      'size while the plant shrinks, the recovered heat falls in proportion to s but the loss does not. The store stops '
      'delivering any useful heat when')
    w('')
    w('    s x (recovered heat in) = standing loss,   that is   s_min = standing loss / recovered heat in.')
    w('')
    w('Where an input is not yet rated it is counted as zero, so the limit shown is on the safe (high) side. '
      'Below s_min the store needs purchased heat just to stay warm, so it should be switched off and its recovered heat '
      'inputs are unreclaimed. If the store is instead made smaller with the plant, its loss falls with its surface area '
      '(volume to the power 2/3) and the limit drops to (standing loss / recovered heat in) cubed. Table 4.1 gives both. '
      'The design tool applies the first, more cautious limit.')
    w('')
    w('Table 4.1. Heat store limits')
    w('')
    L += _sd_table(['Store', 'Tier', 'Standing loss (kW)', 'Recovered heat in (kW)', 'Hold time at standing loss (h)', 's_min, store kept at size', 's_min, store shrunk with plant'],
                   [[h['unit_id'], h['tier'], _SD.fmt(h['loss_kW']),
                     _SD.fmt(h['recovered_in_kW']) + (f" plus unrated {', '.join(h['unrated_inputs'])}" if h['unrated_inputs'] else ''), _SD.fmt(h['hold_hours']),
                     _SD.fmt(h['s_min']) if h['s_min'] else 'open: input not yet rated', _SD.fmt(h['s_min_if_store_shrinks']) if h['s_min'] else 'open'] for h in lim['HEAT']['stores']])
    w('')
    w('### 4.3 FOUNDRY: metal production')
    w('')
    w('Molten-salt electrolysis cells need their bath kept molten. The heat to do that (hold power) is set by the cell size '
      'and insulation, while the electrolysis power scales with metal output [5]. Letting a cell freeze between runs and '
      'remelting it cycles the lining through large temperature changes, which cracks refractory [6], so the cells are '
      'held hot (assumption A-M-330). At scale s the energy per kilogram of metal rises by the factor (s x D + H) / '
      '(s x (D + H)), where D is electrolysis power and H is hold power. Table 4.2 gives that factor. A cell whose hold '
      'power is already most of its total is a candidate for campaign operation with a shared hot-holding furnace; that '
      'is a design decision, not an automatic consequence.')
    w('')
    w('Table 4.2. Molten-salt cells: energy per kilogram relative to full scale')
    w('')
    L += _sd_table(['Cell', 'Hold power H (kW)', 'Electrolysis power D (kW)', 'Hold share at s = 1'] + [f's = {x}' for x in _SD.SCALES],
                   [[c['unit_id'], _SD.fmt(c['hold_kW']), _SD.fmt(c['dc_kW']), _SD.fmt(c['hold_share'])] + [_SD.fmt(c['energy_factor'][str(x)]) for x in _SD.SCALES] for c in lim['FOUNDRY']['cells']])
    w('')
    w('The induction melter works in heats of one full crucible. Each heat starts from a cold charge, so the energy per '
      'kilogram does not change with the number of heats [7]. A smaller plant runs fewer heats. Below the scale '
      'at which a day\'s scrap fills one crucible, the melter runs in campaigns and the scrap waits in a buffer of one '
      'crucible. Nothing is left unreclaimed.')
    w('')
    w('Table 4.3. Batch melter: days between heats')
    w('')
    L += _sd_table(['Melter', 'Crucible (kg)', 'Charge at s = 1 (kg/d)', 'Campaigns below s'] + [f's = {x}' for x in _SD.SCALES],
                   [[mm['unit_id'], _SD.fmt(mm['crucible_kg']), _SD.fmt(mm['charge_kg_d']), _SD.fmt(mm['s_campaign'])] + [_SD.fmt(mm['days_between_heats'][str(x)]) for x in _SD.SCALES] for mm in lim['FOUNDRY']['batch_melters']])
    w('')
    w('FOUNDRY has no scale below which a stream is left unreclaimed. The cost of a smaller plant is the extra energy in '
      'Table 4.2 and the scrap buffer in Table 4.3.')
    w('')
    w('### 4.4 POLYMERS: plastics')
    w('')
    w('The polymer train makes grams to a few hundred grams a day, far below the smallest continuous equipment, so it '
      'already runs in campaigns of one polymerization kettle batch [1, 2]. A smaller plant lengthens the interval '
      'between campaigns. The feeds that arrive between campaigns are held in buffers whose size is one batch\'s worth, '
      'so the buffer size does not depend on s. Chlorine is not stored: it stays in the digester chlorine loop until a '
      'campaign draws it, so gas feeds have no buffer. The batch size uses assumption A-M-331.')
    w('')
    w('Table 4.4. Polymer kettle: days between campaigns and buffer per campaign')
    w('')
    rows = []
    for k in lim['POLYMERS']['kettles']:
        rows.append([k['unit_id'], _SD.fmt(k['volume_L']), _SD.fmt(k['batch_kg']), _SD.fmt(k['product_kg_d'])] +
                    [_SD.fmt(k['days_between_batches'][str(x)]) if k['days_between_batches'] else 'n/a' for x in _SD.SCALES] +
                    ['; '.join(f"{b['stream_id']} {_SD.fmt(b['kg_per_campaign'], 'kg')}" for b in k['buffers']) or 'none'])
    L += _sd_table(['Kettle', 'Volume (L)', 'Batch (kg)', 'Product at s = 1 (kg/d)'] + [f's = {x}' for x in _SD.SCALES] + ['Feed buffers per campaign'], rows)
    w('')
    w('POLYMERS has no scale below which a stream is left unreclaimed, provided the buffers in Table 4.4 are fitted.')
    w('')
    w('### 4.5 Plant-wide rules')
    w('')
    w('Table 4.5 lists every scale rule the design tool applies: the plant-wide rules carried from earlier revisions and '
      'the heat store rules from Table 4.1.')
    w('')
    w('Table 4.5. Scale rules applied by the design tool')
    w('')
    L += _sd_table(['Rule', 'Applies below s', 'Streams flagged', 'Reason'],
                   [[r['id'], _SD.fmt(r['min_scale_m']), ', '.join(r['stream_ids']), r['detail']] for r in hand_rules + a['derate_rules']])
    w('')
    w('## 5. How the design tool uses this page')
    w('')
    w(f'1. For each switched-off sector it reports the streams marked unreclaimed or short in Tables 3.1 to 3.{U - 1}.')
    w(f'2. For each switched-off unit it reports the streams in Table 3.{U}.')
    w('3. For a scale factor below a rule\'s limit in Table 4.5 it reports that rule\'s streams.')
    w('4. A plant with any of these reports is not counted as closed.')
    w('')
    w('## 6. Assumptions')
    w('')
    L += (_sd_table(['Id', 'Assumption', 'Test that confirms it'], [
        ['A-M-329', 'Throughput is proportional to the scale factor below the baseline (s < 1)', 'Size one sub-baseline layout with the scale model and compare its feed with s x 150 kg/d'],
        ['A-M-330', 'Molten-salt cells are held molten between runs rather than frozen and remelted', 'Lining inspection after a planned freeze-thaw trial on one cell'],
        ['A-M-331', f'Polymer kettle batch = volume x {_SD.BATCH_FILL} fill x {_SD.LATEX_DENSITY_KG_L} kg/L x {_SD.LATEX_SOLIDS} solids', 'Weigh the dried polymer from the first kettle batch'],
    ]))
    w('')
    w('## 7. References')
    w('')
    w('1. Ullmann\'s Encyclopedia of Industrial Chemistry, Wiley-VCH, Fluoropolymers chapter (ULLMANN_FLUOROPOLY).')
    w('2. Towler G., Sinnott R., Chemical Engineering Design, 2nd ed., Butterworth-Heinemann (2013): choice of batch or continuous operation (TOWLER2013).')
    w('3. Bergman T.L., Lavine A.S., Incropera F.P., DeWitt D.P., Fundamentals of Heat and Mass Transfer, 7th ed., Wiley (2011): conduction through insulation (INCROPERA7).')
    w('4. ASTM C680-24, Standard Practice for Estimate of the Heat Gain or Loss and the Surface Temperatures of Insulated Flat, Cylindrical, and Spherical Systems (ASTM_C680).')
    w('5. Grjotheim K., Welch B.J., Aluminium Smelter Technology, 2nd ed., Aluminium-Verlag (1988): heat balance of electrolysis cells (GRJOTHEIM1988).')
    w('6. Schacht C.A. (ed.), Refractories Handbook, CRC Press (2004), ch. 13 thermomechanical lining design (SCHACHT2004).')
    w('7. Small coreless induction furnace practice: melt energy from cold charge (INDUCT_SOCX).')
    w('')
    w('## 8. Related documents')
    w('')
    L += (_sd_table(['Document', 'Role'], [
        ['`docs-authority/SCALE_MODEL.md` (AQS-SCALE-001)', 'How the building grows with the scale factor'],
        ['`docs-authority/SECTOR_DEFINITIONS.md` (AQS-SEC-001)', 'The sector list'],
        ['`docs-authority/STREAM_REGISTER.md` (AQS-STR-001)', 'Stream ids'],
        ['`docs-authority/HEAT_LADDER.md`', 'The heat stores and their tiers'],
    ]))
    w('')
    return '\n'.join(L)


def render_scale_down_json(m, inputs):
    """design_tool/aqs_design_tool/data/scale_down.json: the analysis book of
    the scale_down family (functions/scale_down.py), serialized as the v1
    writer wrote it (json, indent 1, non-ascii kept, one trailing newline)."""
    a = _SD.analyse(_graph(m))
    return (json.dumps(a, indent=1, ensure_ascii=False) + '\n').encode('utf-8')


def render_scale_down_page(m, inputs):
    """docs-authority/SCALE_DOWN_UNRECLAIMED.md (AQS-SCALE-UR-001): the page
    over the analysis book, with the design-tool hand data (the unit-off map
    and the hand derate rules) from the solver's data module."""
    from design_tool.aqs_design_tool.solver import scale_down_map as _SDM   # UNIT_OFF_UNRECLAIMED, HAND_DERATE_RULES
    a = _SD.analyse(_graph(m))
    return _sd_page(a, _SDM.UNIT_OFF_UNRECLAIMED, _SDM.HAND_DERATE_RULES).encode('utf-8')


# ---- foam_ew_cut_list (models/openscad/foam_ew/generate.py; the list half) -----

_FOAM_P = None


def _foam_params():
    """The foam cascade's own parameters (models/openscad/foam_ew/params.py -
    the row's read set is its own params, no graph input)."""
    global _FOAM_P
    if _FOAM_P is None:
        spec = importlib.util.spec_from_file_location(
            'aqs_foam_ew_params', os.path.join(_ROOT, 'models', 'openscad', 'foam_ew', 'params.py'))
        _FOAM_P = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_FOAM_P)
    return _FOAM_P


def _foam_slant(top, bot, drop, P):
    return math.hypot((top - bot) / 2, drop)


def _foam_parts(P):
    """Return list of (name, w, h, qty_note) for one cell. Tabs included."""
    sx = _foam_slant(P.OD_L, P.THROAT + 2 * P.T, P.FUNNEL_H, P)
    sy = _foam_slant(P.OD_W, P.THROAT + 2 * P.T, P.FUNNEL_H, P)
    return [
        ("BOTTOM", P.OD_L, P.OD_W, "open to funnel; 16 mm hole later"),
        ("WALL_Y+", P.OD_L, P.ID_H, "anode long wall; sits on 212-edge"),
        ("WALL_Y-", P.OD_L, P.ID_H, "cathode long wall; sits on 212-edge"),
        ("WALL_X+", P.ID_W, P.ID_H, "overflow end; notch after glue-up"),
        ("WALL_X-", P.ID_W, P.ID_H, "inlet end; sits between longs"),
        ("FUNNEL_X", P.OD_L + 2 * P.TAB, sx + P.TAB, "qty 2; side tabs"),
        ("FUNNEL_Y", P.OD_W + 2 * P.TAB, sy + P.TAB, "qty 2; side tabs"),
        ("THROAT", P.THROAT + 4 * P.T, P.THROAT + 4 * P.T, "16 mm hole at centre"),
        ("CEM_RIB", P.RIB_L, P.RIB_H, "qty 2"),
        ("WEIR", 50, 30, "glued on +X after notch"),
    ]


def _foam_bom(P):
    rows = []
    for name, w, h, note in _foam_parts(P):
        qty = 2 if name in ("FUNNEL_X", "FUNNEL_Y", "CEM_RIB") else 1
        qty *= P.N_CELLS
        rows.append(dict(name=name, w=w, h=h, qty=qty, note=note, group="cell"))
    # bund — one deck may exceed one sheet width; split into 2 planks
    plank_w = P.AISLE_W + 2 * P.T
    plank_l = P.AISLE_LEN + 2 * P.T
    if plank_l > P.SHEET_L - 2 * P.MARGIN:
        raise ValueError("bund deck longer than 8 ft — drop scale")
    rows.append(dict(name="BUND_DECK", w=plank_l, h=plank_w, qty=1,
                     note="cells sit on this", group="bund"))
    rows.append(dict(name="BUND_LONG", w=plank_l, h=P.BUND_H, qty=2,
                     note="sits on deck", group="bund"))
    rows.append(dict(name="BUND_END", w=plank_w, h=P.BUND_H, qty=2,
                     note="inside longs", group="bund"))
    rows.append(dict(name="LABEL", w=80, h=28, qty=P.N_CELLS,
                     note="EW-n + metal", group="misc"))
    return rows


def _foam_instances(rows):
    inst = []
    for r in rows:
        for i in range(int(r["qty"])):
            inst.append(dict(name=r["name"], w=float(r["w"]), h=float(r["h"]),
                             i=i, group=r["group"]))
    return inst


def _foam_pack(inst, P):
    """Shelf pack onto 4x8 sheets. Rotate if the other orientation fits a gap better."""
    items = sorted(inst, key=lambda p: max(p["w"], p["h"]), reverse=True)
    sheets = []  # list of {used: [(x,y,w,h,name,i)], shelves: [(y, height, xcursor)]}

    def new_sheet():
        return dict(used=[], y=P.MARGIN, row_h=0, x=P.MARGIN)

    sheets.append(new_sheet())

    usable_w = P.SHEET_W - 2 * P.MARGIN
    usable_l = P.SHEET_L - 2 * P.MARGIN

    for p in items:
        cands = [(p["w"], p["h"], False), (p["h"], p["w"], True)]
        cands = [c for c in cands if c[0] <= usable_l and c[1] <= usable_w]
        if not cands:
            raise ValueError("part %s %.0fx%.0f does not fit a 4x8" % (
                p["name"], p["w"], p["h"]))
        placed = False
        for s in sheets:
            for w, h, rot in sorted(cands, key=lambda c: c[1]):
                if s["x"] + w <= P.SHEET_L - P.MARGIN and (
                        s["row_h"] == 0 or h <= s["row_h"] or
                        s["x"] == P.MARGIN):
                    if s["row_h"] == 0:
                        s["row_h"] = h
                    if h > s["row_h"] and s["x"] == P.MARGIN:
                        s["row_h"] = h
                    if s["x"] + w <= P.SHEET_L - P.MARGIN and h <= max(s["row_h"], h):
                        if h <= s["row_h"] or s["x"] == P.MARGIN:
                            s["used"].append((s["x"], s["y"], w, h, p["name"], p["i"], rot))
                            s["x"] += w + P.KERF
                            s["row_h"] = max(s["row_h"], h)
                            placed = True
                            break
            if placed:
                break
            # new row on this sheet
            for w, h, rot in sorted(cands, key=lambda c: c[1]):
                ny = s["y"] + s["row_h"] + P.KERF
                if ny + h <= P.SHEET_W - P.MARGIN and w <= usable_l:
                    s["y"] = ny
                    s["x"] = P.MARGIN
                    s["row_h"] = h
                    s["used"].append((s["x"], s["y"], w, h, p["name"], p["i"], rot))
                    s["x"] += w + P.KERF
                    placed = True
                    break
            if placed:
                break
        if not placed:
            s = new_sheet()
            w, h, rot = min(cands, key=lambda c: c[1])
            s["row_h"] = h
            s["used"].append((s["x"], s["y"], w, h, p["name"], p["i"], rot))
            s["x"] += w + P.KERF
            sheets.append(s)
    return sheets


def render_foam_cut_list_md(m, inputs):
    """models/openscad/foam_ew/CUT_LIST.md (AQS-FOAM-001; own params, no graph
    input). The PNG nests are matplotlib rasters - not ported (see REMAINING)."""
    P = _foam_params()
    rows = _foam_bom(P)
    n_sheets = len(_foam_pack(_foam_instances(rows), P))
    lines = [
        "# Foam EW cascade — cut list",
        "",
        "Document number: AQS-FOAM-001  ",
        "Revision: A  ",
        "Date: 2026-09-27",
        "",
        "Scale 1:3. Sheet 4×8 ft (1219 × 2438 mm). Thickness 6 mm expanded PVC.",
        "Duty: wet Salria coupon at bench temperature. Not the 70–85 °C plant wall.",
        "Kerf allowance in the nest: %d mm. Walls sit on BOTTOM." % P.KERF,
        "",
        "| Part | Qty | Blank mm | Notes |",
        "|---|---|---|---|",
    ]
    for r in rows:
        lines.append("| %s | %d | %.0f × %.0f | %s |" % (
            r["name"], r["qty"], r["w"], r["h"], r["note"]))
    cell_area = sum(r["w"] * r["h"] * r["qty"] for r in rows)
    sheet_area = P.SHEET_L * P.SHEET_W
    lines += [
        "",
        "## Buy",
        "",
        "- Expanded PVC foam board 6 mm, 4×8 ft × **%d** (plus one spare if the first sheet chips)." % n_sheets,
        "- PVC solvent for foam (Weld-On 4052 / equivalent) + 6 mm acrylic/PVC square as CEM stand-in.",
        "- PVC or CPVC tube OD ~16 mm for nine drain stubs (same family as the board).",
        "- Fine marker + straightedge + snap-off knife + sanding block.",
        "",
        "## Glue order (one cell)",
        "",
        "1. Square BOTTOM. Mark the inside of the four walls.",
        "2. Glue WALL_Y− and WALL_Y+ on the 212 mm edges of BOTTOM.",
        "3. Drop WALL_X− / WALL_X+ between them. Fillet every inside corner.",
        "4. Cut the overflow notch in WALL_X+ only after the box is square.",
        "5. Glue FUNNEL_X / FUNNEL_Y tabs to the underside of BOTTOM. Cap with THROAT.",
        "6. CEM ribs last, 6 mm gap on the mid-plane, blue toward cathode (−Y).",
        "7. Set the nine cells on BUND_DECK at 250 mm centres. Overflow points +X.",
        "8. Solvent-cure fully. Fillet both faces of every seam before Salria fill.",
        "",
        "Blank area %.2f m². %d sheets × %.2f m² = %.2f m². "
        "Nest figure is the buy count." % (
            cell_area / float('1e6'), n_sheets, sheet_area / float('1e6'),
            n_sheets * sheet_area / float('1e6')),
        "",
        "Foam-core PVC at bench T. Plant wet wall remains solid CPVC at 70–85 °C.",
    ]
    return ("\n".join(lines) + "\n").encode("utf-8")


def render_foam_cut_list_csv(m, inputs):
    """models/openscad/foam_ew/cut_list.csv (the csv module's CRLF dialect, as
    the v1 writer produced with newline='')."""
    P = _foam_params()
    rows = _foam_bom(P)
    sio = io.StringIO(newline='')
    w = csv.DictWriter(sio, fieldnames=["name", "qty", "w_mm", "h_mm", "group", "note"])
    w.writeheader()
    for r in rows:
        w.writerow(dict(name=r["name"], qty=r["qty"], w_mm="%.1f" % r["w"],
                        h_mm="%.1f" % r["h"], group=r["group"], note=r["note"]))
    return sio.getvalue().encode("utf-8")


# ---- site_3d (flow_graph/param/site_3d.py; X-3D-SITE, the SVG + manifest half) --

_SECTOR_COLORS = {
    'ELEC': '#2c6fbb', 'HAB': '#c0392b', 'FARM': '#1e8449', 'WTR': '#2471a3',
    'DIGESTER': '#7d6608', 'MFG': '#6c3483', 'FOUNDRY': '#935116', 'FAB': '#117864',
    'GAS': '#b03a2e', 'GEO': '#5d6d7e', 'GLASS': '#a04000', 'HEAT': '#d68910',
    'MEOH': '#117a65', 'NUT': '#884ea0', 'OIL': '#7b241c', 'POLYMERS': '#1f618d',
    'PUMPED_HYDRO': '#2874a6', 'CRYO': '#5499c7', 'DOCK': '#85929e',
}

_SITE_LABEL = 'Baseline site'   # the committed reference model (locale runs are worktree runs)


def _site3d_color(sector):
    return _SECTOR_COLORS.get(sector, '#666666')


def _site3d_collect(g, seed):
    """Per-unit 3D state for the baseline site: placement, status, sector,
    block, label data (the v1 collect() at site_id='baseline': no scaling
    plan). Reads the seed payload; every solid traces to a cited entry."""
    D = seed['datums_mm']
    present = {n['unit_id']: n for n in g['nodes'] if n.get('presence') in ('present', 'placeholder')}
    seeded = {u['unit_id']: u for u in seed['units']}
    block_of, block_geom = {}, {}
    for b in seed['blocks']:
        block_geom[b['block_id']] = b
        for u in b.get('unit_ids', []):
            block_of.setdefault(u, b['block_id'])

    out = []
    for uid, node in sorted(present.items()):
        sector = node.get('sector_id', '')
        s = seeded.get(uid)
        if s:
            level = s['level']
            origin = list(s['origin_mm']) + [0] * (3 - len(s['origin_mm']))
            origin[2] = origin[2] + D.get(level, 0)      # the seed Z is relative to the level datum
            size = list(s['size_mm']) + [1500] * (3 - len(s['size_mm']))   # nominal height when unissued
            basis = s.get('source', 'placement seed')
            geom = 'placement'
        else:
            blk = block_of.get(uid)
            if blk:
                bg = block_geom[blk]
                level = bg.get('level', 'L0')
                origin = list(bg['origin_mm']) + [0] * (3 - len(bg['origin_mm']))
                origin[2] = D.get(level, 0)
                size = list(bg['size_mm']) + [1500] * (3 - len(bg['size_mm']))
                basis = f'block-centre massing of {blk} (placement pending)'
                geom = 'block-massing'
            else:
                out.append(dict(unit_id=uid, sector_id=sector, status='unplaced',
                                replaced_by=None))
                continue
        out.append(dict(unit_id=uid, sector_id=sector, level=level,
                        origin_mm=origin, size_mm=size, basis=basis,
                        status='built',
                        replaced_by=None,
                        geom=geom))
    return out, D, seed


def _site3d_box_faces(origin, size):
    """Axonometric faces of a box: top + the two viewer-facing sides (Z-up mm)."""
    x, y, z = origin
    sx, sy, sz = size
    c = [(x, y, z), (x + sx, y, z), (x + sx, y + sy, z), (x, y + sy, z),
         (x, y, z + sz), (x + sx, y, z + sz), (x + sx, y + sy, z + sz), (x, y + sy, z + sz)]

    def iso(p):
        px, py, pz = p
        return ((px - py) * math.cos(math.pi / 6), -(pz + (px + py) * math.sin(math.pi / 6)))

    pts = [iso(p) for p in c]
    top = [pts[4], pts[5], pts[6], pts[7]]
    left = [pts[0], pts[1], pts[5], pts[4]]     # -Y face
    right = [pts[1], pts[2], pts[6], pts[5]]    # +X face
    depth = sum((x + y + z) for x, y, z in c)
    return {'top': top, 'left': left, 'right': right, 'depth': depth,
            'centre_iso': iso((x + sx / 2, y + sy / 2, z + sz / 2))}


def _site3d_svg_poly(pts, fill, stroke, dashed=False, opacity=float('1')):
    dash = ' stroke-dasharray="18 10"' if dashed else ''
    pp = ' '.join(f'{x:.0f},{y:.0f}' for x, y in pts)
    return (f'<polygon points="{pp}" fill="{fill}" fill-opacity="{opacity}" '
            f'stroke="{stroke}" stroke-width="2"{dash}/>')


def _site3d_axo(units3d, D, site_label):
    """Labelled axonometric sheet: blocks, built units, eliminated ghosts, datums."""
    xs, ys = [], []
    geoms = []
    for u in units3d:
        if 'origin_mm' not in u:
            continue
        f = _site3d_box_faces(u['origin_mm'], u['size_mm'])
        geoms.append((u, f))
        for p in f['top'] + f['left'] + f['right']:
            xs.append(p[0])
            ys.append(p[1])
    if not xs:
        return '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="120"><text x="10" y="60">no placed units</text></svg>'
    pad = 60
    x0, y0 = min(xs) - pad, min(ys) - pad
    w, h = max(xs) - x0 + 2 * pad, max(ys) - y0 + 2 * pad + 40
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h:.0f}" '
         f'font-family="DejaVu Sans,sans-serif" font-size="13">',
         f'<rect x="0" y="0" width="{w:.0f}" height="{h:.0f}" fill="white"/>',
         f'<text x="16" y="28" font-size="17" font-weight="bold">{site_label} plant - placement-model axonometric (schematic: positions carry no dimension beyond the placement model)</text>',
         f'<text x="16" y="48" font-size="12" fill="#555">Z-up, mm. Solid = built at this site. Dashed = eliminated by the scaling plan (function moved to the labelled replacement). Grey = block-centre massing, placement pending.</text>']
    geoms.sort(key=lambda g: g[1]['depth'])          # painter: far first
    for u, f in geoms:
        elim = u['status'] == 'eliminated'
        col = _site3d_color(u['sector_id'])
        cx, cy = f['centre_iso']
        o.append(_site3d_svg_poly(f['top'], col if not elim else 'none', col, dashed=elim, opacity=float('0.92')))
        o.append(_site3d_svg_poly(f['left'], '#00000022' if not elim else 'none', col, dashed=elim))
        o.append(_site3d_svg_poly(f['right'], '#00000044' if not elim else 'none', col, dashed=elim))
        if not elim:
            o.append(f'<text x="{cx:.0f}" y="{cy:.0f}" textAnchor="middle" fontSize="12" '
                     f'fill="#111">{u["unit_id"]}</text>')
        elif u.get('replaced_by'):
            o.append(f'<text x="{cx:.0f}" y="{cy:.0f}" textAnchor="middle" fontSize="11" '
                     f'fill="#c0392b">{u["unit_id"]} -> {u["replaced_by"]}</text>')
    o.append(f'<text x="{w - 340:.0f}" y="{h - 30:.0f}" fontSize="11" fill="#555">levels (mm): '
             + ', '.join(f'{k} {v}' for k, v in sorted(D.items(), key=lambda kv: kv[1])) + '</text>')
    o.append(f'<text x="{w - 340:.0f}" y="{h - 12:.0f}" fontSize="11" fill="#555">+X right-down, +Y left-down, +Z up. Source: placement_seed Rev M+.</text>')
    o.append('</svg>')
    return '\n'.join(o)


def _site3d_plan(units3d, level, D, site_label):
    """Labelled plan per level: X-Y rectangles at the level datum."""
    rows, xs, ys = [], [], []
    for u in units3d:
        if 'origin_mm' not in u or u['level'] != level:
            continue
        x, y = u['origin_mm'][0], u['origin_mm'][1]
        sx, sy = u['size_mm'][0], u['size_mm'][1]
        xs += [x, x + sx]
        ys += [y, y + sy]
        rows.append((u, x, y, sx, sy))
    if not rows:
        return None
    pad = 80
    x0, y0 = min(xs) - pad, min(ys) - pad
    w, h = max(xs) - x0 + 2 * pad, max(ys) - y0 + 2 * pad + 46
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h:.0f}" '
         f'font-family="DejaVu Sans,sans-serif" font-size="12">',
         f'<rect x="0" y="0" width="{w:.0f}" height="{h:.0f}" fill="white"/>',
         f'<text x="16" y="26" font-size="15" font-weight="bold">{site_label} - level {level} plan (mm, +X right, +Y up)</text>',
         f'<text x="16" y="44" font-size="11" fill="#555">datum Z {D.get(level, 0)} mm. Dashed = eliminated by the scaling plan.</text>']
    for u, x, y, sx, sy in rows:
        elim = u['status'] == 'eliminated'
        col = _site3d_color(u['sector_id'])
        o.append(f'<rect x="{x - x0:.0f}" y="{y - y0:.0f}" width="{sx:.0f}" height="{sy:.0f}" '
                 f'fill="{col}22" stroke="{col}" stroke-width="2" '
                 f'stroke-dasharray="10 6" fill-opacity="0.85"/>' if elim else
                 f'<rect x="{x - x0:.0f}" y="{y - y0:.0f}" width="{sx:.0f}" height="{sy:.0f}" '
                 f'fill="{col}33" stroke="{col}" stroke-width="2"/>')
        o.append(f'<text x="{x - x0 + 6:.0f}" y="{y - y0 + 16:.0f}" fontSize="11">{u["unit_id"]}</text>')
    o.append('</svg>')
    return '\n'.join(o)


def _site3d_state(m, inputs):
    seed = inputs.get('placement_seed')
    if seed is None:
        return None
    return _site3d_collect(_graph(m), seed)


def render_site_axo(m, inputs):
    """media/3d/SITE_AXO.svg (the baseline reference model; payload:
    placement_seed)."""
    st = _site3d_state(m, inputs)
    if st is None:
        return _stub('media/3d/SITE_AXO.svg', 'placement_seed')
    units3d, D, _seed = st
    return _site3d_axo(units3d, D, _SITE_LABEL).encode('utf-8')


def _site_plan_renderer(level):
    def f(m, inputs):
        name = 'media/3d/LEVEL_%s.svg' % level.replace('-', 'm')
        st = _site3d_state(m, inputs)
        if st is None:
            return _stub(name, 'placement_seed')
        units3d, D, _seed = st
        svg = _site3d_plan(units3d, level, D, _SITE_LABEL)
        if svg is None:
            return _stub(name, f'a placed unit on level {level!r}')
        return svg.encode('utf-8')
    f.__name__ = f'render_site_plan_{level.replace("-", "m")}'
    f.__doc__ = f'media/3d/LEVEL_{level.replace("-", "m")}.svg: the {level} level plan.'
    return f


def render_site_manifest(m, inputs):
    """media/3d/MODEL_MANIFEST.json (coverage manifest; glb_units is the box
    count the glTF export packs - every placed unit, built and ghost alike,
    which the binary lane reproduces; errors is the export's error list,
    empty on the committed reference)."""
    st = _site3d_state(m, inputs)
    if st is None:
        return _stub('media/3d/MODEL_MANIFEST.json', 'placement_seed')
    units3d, D, seed = st
    levels = sorted({u['level'] for u in units3d if 'origin_mm' in u},
                    key=lambda lv: D.get(lv, 0))
    plans = {}
    for lv in levels:
        svg = _site3d_plan(units3d, lv, D, _SITE_LABEL)
        if svg:
            plans[lv] = f'LEVEL_{lv.replace("-", "m")}.svg'
    built = [u for u in units3d if u['status'] == 'built' and 'origin_mm' in u]
    ghosts = [u for u in units3d if u['status'] == 'eliminated' and 'origin_mm' in u]
    massing = [u for u in units3d if u.get('geom') == 'block-massing']
    unplaced = [u['unit_id'] for u in units3d if u['status'] == 'unplaced']
    manifest = {
        'site_id': 'baseline',
        'placement_seed_revision': seed.get('revision'),
        'units_total': len(units3d),
        'built': len(built), 'ghosts_eliminated': len(ghosts),
        'block_centre_massing': len(massing), 'unplaced': unplaced,
        'routed_note': ('3D geometry is placement-model massing at sourced centres; '
                        'detailed CAD remains models/freecad + models/mfg.'),
        'levels': levels, 'plans': plans,
        'glb_units': sum(1 for u in units3d if 'origin_mm' in u), 'errors': [],
        'units': [{k: u.get(k) for k in ('unit_id', 'sector_id', 'level', 'status',
                                         'replaced_by', 'basis') if u.get(k) is not None}
                  for u in units3d],
    }
    return json.dumps(manifest, indent=1).encode('utf-8')


# ---- the declared registry block (census order, section F) ----------------------

DOCS = [
    # derived_excerpts (flow_graph/export_authority_md.py)
    ('flow_graph/derived/STREAM_REGISTER_DERIVED.md', render_stream_register),
    ('flow_graph/derived/MASS_FLOW_DERIVED.md', render_mass_flow),
    ('flow_graph/derived/CENSUS.md', render_census),
    ('flow_graph/derived/SYNC_POINTER.md', render_sync_pointer),
    # loop_closure (flow_graph/loop_closure.py)
    ('flow_graph/derived/LOOP_CLOSURE.md', render_loop_closure),
    # candidate_mvs (flow_graph/export_candidate_mvs.py)
    ('design_tool/aqs_design_tool/data/candidate_mvs.json', render_candidate_mvs),
    # regen_derived (flow_graph/render_layer_views.py; JSON + DOT; SVGs external)
    ('flow_graph/views/pfd.json', _view_renderer('pfd', 'json')),
    ('flow_graph/views/mfd.json', _view_renderer('mfd', 'json')),
    ('flow_graph/views/efd-elec.json', _view_renderer('efd-elec', 'json')),
    ('flow_graph/views/efd-thermal.json', _view_renderer('efd-thermal', 'json')),
    ('flow_graph/views/efd-ess.json', _view_renderer('efd-ess', 'json')),
    ('flow_graph/views/pfd.dot', _view_renderer('pfd', 'dot')),
    ('flow_graph/views/mfd.dot', _view_renderer('mfd', 'dot')),
    ('flow_graph/views/efd-elec.dot', _view_renderer('efd-elec', 'dot')),
    ('flow_graph/views/efd-thermal.dot', _view_renderer('efd-thermal', 'dot')),
    ('flow_graph/views/efd-ess.dot', _view_renderer('efd-ess', 'dot')),
    # sector_definitions (docs-authority/_sector_definitions.py)
    ('docs-authority/SECTOR_DEFINITIONS.md', render_sector_definitions),
    # scale_down (flow_graph/param/scale_down.py; analysis = functions/scale_down.py)
    ('design_tool/aqs_design_tool/data/scale_down.json', render_scale_down_json),
    ('docs-authority/SCALE_DOWN_UNRECLAIMED.md', render_scale_down_page),
    # foam_ew_cut_list (models/openscad/foam_ew/generate.py; PNGs external)
    ('models/openscad/foam_ew/CUT_LIST.md', render_foam_cut_list_md),
    ('models/openscad/foam_ew/cut_list.csv', render_foam_cut_list_csv),
    # site_3d (flow_graph/param/site_3d.py; GLB external; baseline reference model)
    ('media/3d/SITE_AXO.svg', render_site_axo),
    ('media/3d/LEVEL_Lm2.svg', _site_plan_renderer('L-2')),
    ('media/3d/LEVEL_Lm1.svg', _site_plan_renderer('L-1')),
    ('media/3d/LEVEL_L0.svg', _site_plan_renderer('L0')),
    ('media/3d/LEVEL_L1.svg', _site_plan_renderer('L1')),
    ('media/3d/LEVEL_L2.svg', _site_plan_renderer('L2')),
    ('media/3d/LEVEL_ROOF.svg', _site_plan_renderer('ROOF')),
    ('media/3d/MODEL_MANIFEST.json', render_site_manifest),
]

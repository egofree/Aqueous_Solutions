# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""FastAPI surface for Aqueous design-tool P0 (AQS-UI-001 §7).

Locked / candidate MVS is read-only via GET /api/v1/mvs.
All mutations are sandbox-scoped.
"""

from __future__ import annotations

import ast
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from typing import Optional
import importlib

SP = importlib.import_module("aqs_design_tool.site_profiles")
SC = importlib.import_module("flow_graph.param.scaling")
SITE_PROF = importlib.import_module("flow_graph.param.site")
PIPE = importlib.import_module("aqs_design_tool.solver.pipeline")

from pydantic import BaseModel, ConfigDict
from fastapi import FastAPI, HTTPException

SP = importlib.import_module("aqs_design_tool.site_profiles")
SC = importlib.import_module("flow_graph.param.scaling")
SITE_PROF = importlib.import_module("flow_graph.param.site")
PIPE = importlib.import_module("aqs_design_tool.solver.pipeline")
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .. import SCHEMA_VERSION, __version__
from ..export.pack import export_pack
from ..models import (
    ResidualItem, GapModel, SandboxOverrides, SolveResponse, SolveRequest,
    ExportRequest,
    ExportResponse,
    FlagsResponse,
    MvsModel,
    SandboxCreateRequest,
    SandboxPatchRequest,
    SolveRequest,
    SolveResponse,
)
from ..solver.stub import solve
from .store import STORE, load_mvs_from_graph

app = FastAPI(
    title="Aqueous Design Tool API",
    version=__version__,
    description=(
        "P0/P1 + WP-Ap1 graph sole authority (AQS-UI-001 / unify_then_reshape). "
        "Write path = plant_flow_graph.json; candidate_mvs is generated projection; "
        "sandboxes overlay graph; CERN-OHL-S-2.0."
    ),
)

# Local P1 Vite (5173) + common alt ports — loopback only.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:5174",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    contract: dict = {"ok": None, "error": "unchecked"}
    try:
        from ..flow_graph_adapter import projection_contract_status

        contract = projection_contract_status()
    except Exception as exc:  # noqa: BLE001
        contract = {"ok": False, "error": str(exc)}
    return {
        "status": "ok",
        "schema_version": SCHEMA_VERSION,
        "package_version": __version__,
        "note": "P0 stub — no claim of full plant balance closure.",
        "topology_authority": "AQS-FLOW-GRAPH-001",
        "write_path": "flow_graph/plant_flow_graph.json",
        "candidate_mvs_role": "generated_projection",
        "mvs_equivalent": False,
        "projection_contract_ok": contract.get("ok"),
        "projection_contract": contract,
    }


@app.get("/api/v1/mvs", response_model=MvsModel)
def get_mvs() -> MvsModel:
    """Return MVS model from plant_flow_graph (sole authority; read-only).

    ``candidate_mvs.json`` is a generated projection of the same graph.
    """
    try:
        return load_mvs_from_graph()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"MVS load failed: {exc}") from exc


@app.get("/api/v1/mvs/from-graph", response_model=MvsModel)
def get_mvs_from_graph() -> MvsModel:
    """Alias of GET /mvs — graph is sole authority (WP-Ap1).

    Known gaps preserved. Never claims mvs_equivalent from topology alone.
    Sandboxes created via POST /sandbox use this same load by default.
    """
    try:
        return load_mvs_from_graph()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=500, detail=f"MVS+flow-graph load failed: {exc}"
        ) from exc


@app.get("/api/v1/mvs/projection-check")
def projection_check() -> dict:
    """WP-Ap2: fail (HTTP 409) if on-disk candidate_mvs drifts from graph.

    Solve/mvs/sandbox always load the graph; this endpoint makes dual-master
    drift visible to contributors and operators.
    """
    try:
        from ..flow_graph_adapter import projection_contract_status

        status = projection_contract_status()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=500, detail=f"projection check failed: {exc}"
        ) from exc
    if not status.get("ok"):
        raise HTTPException(status_code=409, detail=status)
    return status


@app.get("/api/v1/flow-graph")
def get_flow_graph_meta() -> dict:
    """Metadata for sole topology authority (AQS-FLOW-GRAPH-001)."""
    try:
        from ..flow_graph_adapter import flow_graph_meta

        return flow_graph_meta()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=500, detail=f"flow-graph load failed: {exc}"
        ) from exc


@app.get("/api/v1/flow-graph/topology")
def get_flow_graph_topology(
    include_placeholders: bool = True,
    include_intra_aisle: bool = True,
) -> dict:
    """Units/streams mapped from plant_flow_graph.json (no MVS fields)."""
    try:
        from ..flow_graph_adapter import topology_from_graph

        units, streams, gaps = topology_from_graph(
            include_placeholders=include_placeholders,
            include_intra_aisle=include_intra_aisle,
        )
        return {
            "source": "AQS-FLOW-GRAPH-001",
            "mvs_equivalent": False,
            "unit_count": len(units),
            "stream_count": len(streams),
            "gap_count": len(gaps),
            "units": [u.model_dump(by_alias=True, mode="json") for u in units],
            "streams": [s.model_dump(mode="json") for s in streams],
            "gaps": [g.model_dump(mode="json") for g in gaps],
        }
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=500, detail=f"flow-graph topology failed: {exc}"
        ) from exc


@app.get("/api/v1/flow-graph/views/{view_name}")
def get_flow_graph_view(view_name: str) -> JSONResponse:
    """Layer view JSON (pfd|mfd|efd-elec|efd-thermal|efd-ess)."""
    from ..paths import FLOW_GRAPH_VIEWS

    allowed = {"pfd", "mfd", "efd-elec", "efd-thermal", "efd-ess"}
    if view_name not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown view '{view_name}'; allowed={sorted(allowed)}",
        )
    path = FLOW_GRAPH_VIEWS / f"{view_name}.json"
    if not path.is_file():
        raise HTTPException(
            status_code=404,
            detail=f"View not generated yet: {path}. Run flow_graph/render_layer_views.py",
        )
    import json

    return JSONResponse(json.loads(path.read_text(encoding="utf-8")))


@app.post("/api/v1/sandbox")
@app.get("/api/v1/sites")
def list_sites() -> dict:
    """The locale scaling profiles a site sandbox can start from (X-UI-002 Phase 1)."""
    out = []
    for sid in SP.available_sites():
        try:
            prof = SITE_PROF.load_profile(sid)
            acts = SC.actions(prof)
            out.append({'site_id': sid, 'actions': len(acts),
                        'eliminations': sum(1 for a in acts if a.get('action') == 'eliminate')})
        except Exception as exc:  # a broken profile is listed with its error, not hidden
            out.append({'site_id': sid, 'error': str(exc)[:120]})
    return {'sites': out}


class SiteSandboxRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    site_id: str
    label: Optional[str] = None


SiteSandboxRequest.model_rebuild()


@app.post("/api/v1/sandbox/from-site")
def create_sandbox_from_site(body: SiteSandboxRequest) -> dict:
    """A scaling profile becomes a sandbox: the engine's own resolved plan as overrides,
    the profile's replacement placements stamped with their site sizing."""
    try:
        sp = SP.site_overrides(body.site_id)
        place_units = SP.site_placement_units(body.site_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"site profile {body.site_id}: {exc}") from exc
    if sp['errors']:
        raise HTTPException(status_code=422, detail={'site_id': body.site_id, 'errors': sp['errors']})
    overrides = SandboxOverrides(**sp['overrides'])
    base = load_mvs_from_graph()
    # fold in the placement units (sizing + provenance from the placement model);
    # units already carried by the graph get their site sizing stamped instead
    by_id = {u.unit_id: u for u in base.units}
    for pu in place_units:
        if pu['unit_id'] in by_id:
            u = by_id[pu['unit_id']]
            u.params = {**(u.params or {}), **pu['params']}
        else:
            base.units.append(UnitModel(**pu))
    rec = STORE.create(overrides=overrides, label=body.label or f"site:{body.site_id}",
                       base=base, site_profile=body.site_id)
    return {
        "sandbox_id": rec.sandbox_id,
        "label": rec.label,
        "site_id": body.site_id,
        "applied": sp['applied'],
        "unapplied": sp['unapplied'],
        "replacement_of": sp['replacement_of'],
        "placement_units": [p['unit_id'] for p in place_units],
        "parent_mvs_revision": rec.parent_mvs_revision,
        "model": rec.model.model_dump(by_alias=True, mode="json"),
    }


@app.post("/api/v1/sandbox/{sandbox_id}/solve-pipeline", response_model=SolveResponse)
def solve_sandbox_pipeline(sandbox_id: str) -> SolveResponse:
    """The REAL X-PAR-02 balance on the sandbox fold: true residuals, never smoothed."""
    try:
        rec = STORE.get(sandbox_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown sandbox {sandbox_id}") from exc
    units = [u.model_dump(by_alias=True) for u in rec.model.units]
    res = PIPE.solve_mass(units, sandbox_id=sandbox_id)
    elec, egaps = {}, []
    if rec.site_profile:
        try:
            er = PIPE.solve_electrical(rec.model.electrical.model_dump(by_alias=True),
                                       units, rec.site_profile,
                                       disabled={u['unit_id'] for u in units
                                                 if not u.get('enabled', True)})
            elec = er['electrical_match']
            egaps = [GapModel(sector_definition='site electrical', reason=gap) for gap in er['gaps']]
        except Exception as exc:  # a broken profile section is a named error, not a silent one
            egaps = [GapModel(sector_definition='site electrical',
                              reason=f'electrical match failed: {exc}')]
    result = SolveResponse(
        status=res['status'],
        sandbox_id=sandbox_id,
        residuals={'mass': [ResidualItem(**r) for r in res['residuals']['mass']]},
        electrical_match=elec,
        gaps=[GapModel(sector_definition='pipeline solve', reason=res['note'])] + egaps,
    )
    STORE.set_solve(sandbox_id, result)
    return result


def create_sandbox(body: SandboxCreateRequest | None = None) -> dict:
    body = body or SandboxCreateRequest()
    rec = STORE.create(overrides=body.overrides, label=body.label)
    return {
        "sandbox_id": rec.sandbox_id,
        "label": rec.label,
        "created_at": rec.created_at,
        "parent_mvs_revision": rec.parent_mvs_revision,
        "model": rec.model.model_dump(by_alias=True, mode="json"),
    }


@app.get("/api/v1/sandbox/{sandbox_id}")
def get_sandbox(sandbox_id: str) -> dict:
    try:
        rec = STORE.get(sandbox_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown sandbox {sandbox_id}") from exc
    return {
        "sandbox_id": rec.sandbox_id,
        "label": rec.label,
        "created_at": rec.created_at,
        "updated_at": rec.updated_at,
        "parent_mvs_revision": rec.parent_mvs_revision,
        "model": rec.model.model_dump(by_alias=True, mode="json"),
        "last_solve": (
            rec.last_solve.model_dump(mode="json") if rec.last_solve else None
        ),
    }


@app.patch("/api/v1/sandbox/{sandbox_id}")
def patch_sandbox(sandbox_id: str, body: SandboxPatchRequest) -> dict:
    try:
        rec = STORE.patch(sandbox_id, body.overrides, label=body.label)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown sandbox {sandbox_id}") from exc
    return {
        "sandbox_id": rec.sandbox_id,
        "label": rec.label,
        "updated_at": rec.updated_at,
        "model": rec.model.model_dump(by_alias=True, mode="json"),
    }


@app.post("/api/v1/sandbox/{sandbox_id}/solve", response_model=SolveResponse)
def solve_sandbox(
    sandbox_id: str, body: SolveRequest | None = None
) -> SolveResponse:
    try:
        rec = STORE.get(sandbox_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown sandbox {sandbox_id}") from exc
    result = solve(rec.model, body or SolveRequest(), sandbox_id=sandbox_id)
    STORE.set_solve(sandbox_id, result)
    return result


@app.get("/api/v1/sandbox/{sandbox_id}/flags", response_model=FlagsResponse)
def get_flags(sandbox_id: str) -> FlagsResponse:
    try:
        rec = STORE.get(sandbox_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown sandbox {sandbox_id}") from exc
    if rec.last_solve is None:
        # Run a lightweight solve to populate flags
        result = solve(rec.model, SolveRequest(), sandbox_id=sandbox_id)
        STORE.set_solve(sandbox_id, result)
        rec = STORE.get(sandbox_id)
    assert rec.last_solve is not None
    ls = rec.last_solve
    return FlagsResponse(
        sandbox_id=sandbox_id,
        gaps=ls.gaps,
        unclosed_streams=ls.unclosed_streams,
        bottlenecks=ls.bottlenecks,
        redundant_paths=ls.redundant_paths,
        code_flags=ls.code_flags,
        last_solve_status=ls.status,
    )


@app.post("/api/v1/sandbox/{sandbox_id}/export", response_model=ExportResponse)
def export_sandbox(
    sandbox_id: str, body: ExportRequest | None = None
) -> ExportResponse:
    try:
        rec = STORE.get(sandbox_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown sandbox {sandbox_id}") from exc
    try:
        return export_pack(rec, body or ExportRequest())
    except ValueError as exc:  # QA R1: bad pack_name (traversal/shape)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except FileExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.get("/api/v1/sector-definitions")
def list_sector_definitions() -> JSONResponse:
    """Placeholder catalogue until AQS-SEC-001 lands."""
    from ..sector_definitions import PLACEHOLDER_SECTOR_CATALOGUE, SectorDefinition

    return JSONResponse(
        {
            "source": "AQS-SEC-001 Rev C + AQS-UI-001 §3.1",
            "todo": "ESS ≥1 peer set (A3): gap ess_peer_set_all_disabled when ZNBR2/MEOH/PUMPED_HYDRO all off",
            "definitions": [e.value for e in SectorDefinition],
            "catalogue": PLACEHOLDER_SECTOR_CATALOGUE,
        }
    )


def create_app() -> FastAPI:
    return app


# ----------------------------------------------------------------------
# U6 design UI — read-only views over the unified engine
# (flow_graph.system_tree / param/drivers.json / param.regen). None of
# these mutate anything: the write path stays edit → regen (AGENTS loop).
# ----------------------------------------------------------------------


def _last_run_passes(receipt_path):
    """Graph-loop pass count of the last full regen, from the untracked run log beside the
    receipt (the tracked receipt is deterministic and carries no run details). None if absent."""
    try:
        run = json.loads((receipt_path.parent / "_regen_run.json").read_text(encoding="utf-8"))
        return run.get("passes")
    except Exception:
        return None


def _repo_paths() -> tuple:
    """(repo_root, drivers.json, regen receipt, rev_stamp checker)."""
    from ..paths import FLOW_GRAPH_PACKAGE

    root = FLOW_GRAPH_PACKAGE.parent
    return (
        root,
        FLOW_GRAPH_PACKAGE / "param" / "drivers.json",
        FLOW_GRAPH_PACKAGE / "derived" / "_regen_receipt.json",
        root / "docs-authority" / "_rev_stamp.py",
    )


def _flow_graph_on_path() -> None:
    """Make the flow_graph package importable (repo root on sys.path)."""
    from ..paths import FLOW_GRAPH_PACKAGE

    root = str(FLOW_GRAPH_PACKAGE.parent)
    if root not in sys.path:
        sys.path.insert(0, root)


def _load_system_tree():
    """Import flow_graph.system_tree with the flow_graph package importable."""
    _flow_graph_on_path()
    from flow_graph.system_tree import load as load_tree

    return load_tree()


@app.get("/api/v1/system-tree")
def get_system_tree(include_unit_ids: bool = True) -> dict:
    """U4a containment tree (AQS-SYS-TREE-001), served read-only.

    Every node carries its resolved unit set and an aggregate (count,
    ``kw_sum`` from graph ``continuous_kw``, worst presence) rolled up
    from the graph — the tree only partitions the graph (sole
    authority). Sandbox toggles PATCH ``system_enabled`` /
    ``subsystem_enabled`` / ``unit_enabled`` with these node ids;
    most-specific wins server-side.
    """
    from ..flow_graph_adapter import load_plant_flow_graph_dict

    _flow_graph_on_path()
    from flow_graph.system_tree import TreeValidationError

    try:
        tree = _load_system_tree()
        graph = load_plant_flow_graph_dict()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except TreeValidationError as exc:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "system tree structurally invalid",
                "issues": exc.issues,
            },
        ) from exc

    nodes = []
    for n in tree.nodes:
        units = sorted(tree.resolve_units(n.id))
        nodes.append(
            {
                "id": n.id,
                "parent": n.parent,
                "level": n.level,
                "children": list(n.children),
                "unit_id": n.unit_id,
                "description": n.description,
                "unit_ids": units if include_unit_ids else None,
                "aggregate": tree.aggregate(units, graph=graph),
            }
        )
    return {
        "source": "AQS-SYS-TREE-001 (flow_graph/system_tree.yaml)",
        "graph_authority": "AQS-FLOW-GRAPH-001",
        "read_only": True,
        "schema_version": tree.schema_version,
        "doc_id": tree.doc_id,
        "revision": tree.revision,
        "date": tree.date,
        "sector_exceptions": tree.sector_exceptions,
        "stats": tree.stats(),
        "node_count": len(nodes),
        "nodes": nodes,
    }


@app.get("/api/v1/params")
def get_params() -> dict:
    """Design drivers listing — READ-ONLY projection of drivers.json.

    Values live in ``flow_graph/param/drivers.json`` (X-PAR-01: every
    independent input with a published reference / register id / owner
    basis). The write path is edit drivers.json + regen, never this API.
    """
    _, drivers_path, _, _ = _repo_paths()
    if not drivers_path.is_file():
        raise HTTPException(
            status_code=404, detail=f"drivers.json not found: {drivers_path}"
        )
    raw = drivers_path.read_bytes()
    _flow_graph_on_path()
    from flow_graph.param import drivers as _drivers

    data = _drivers.load()  # drivers.json with the selected site profile applied
    rows = []
    for key in sorted(data):
        e = data[key] if isinstance(data[key], dict) else {"value": data[key]}
        rows.append(
            {
                "key": key,
                "value": e.get("value"),
                "units": e.get("units"),
                "ref": e.get("ref"),
                "owner": e.get("owner"),
                "register": e.get("register"),
                "needs_verification": bool(e.get("needs_verification")),
                "verification_test": e.get("verification_test"),
            }
        )
    return {
        "source": "flow_graph/param/drivers.json (X-PAR-01)",
        "read_only": True,
        "note": "Values live in drivers.json; edit + regen is the write path.",
        "count": len(rows),
        "needs_verification_count": sum(
            1 for r in rows if r["needs_verification"]
        ),
        "drivers_sha256": hashlib.sha256(raw).hexdigest(),
        "params": rows,
    }


@app.get("/api/v1/regen-status")
def get_regen_status() -> dict:
    """Staleness of derived artefacts vs the graph — read-only check.

    ``python3 -m flow_graph.param.regen --check`` delegates to
    ``docs-authority/_rev_stamp.py`` but *rewrites*
    ``docs-authority/DERIVED_REVISIONS.md``; ``--check-only`` runs the
    same evaluator and writes nothing, so this GET stays side-effect
    free. Exit 1 ⇔ gated stale files exist.
    """
    import re

    root, _, receipt_path, rev_stamp = _repo_paths()
    checked_at = datetime.now(timezone.utc).isoformat()
    out: dict = {
        "ok": False,
        "stale_count": None,
        "gated_stale": [],
        "files_checked": None,
        "last_receipt": None,
        "checked_at": checked_at,
        "command": f"python3 {rev_stamp.relative_to(root)} --check-only",
    }
    try:
        r = subprocess.run(
            [sys.executable, str(rev_stamp), "--check-only"],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=15,
        )
    except subprocess.TimeoutExpired:
        return {**out, "error": "rev_stamp --check-only timed out after 15 s"}
    except OSError as exc:  # noqa: BLE001 — surface as status, not a 500
        return {**out, "error": f"failed to run rev_stamp: {exc}"}

    m = re.search(
        r"^(\d+) files (\d+) stale gated stale: \[(.*)\]\s*$",
        r.stdout,
        re.MULTILINE,
    )
    if m is None:
        tail = "\n".join((r.stdout + r.stderr).strip().splitlines()[-5:])
        return {
            **out,
            "error": f"could not parse rev_stamp output (rc={r.returncode}): {tail}",
        }
    files_checked = int(m.group(1))
    stale_count = int(m.group(2))
    gated: list[str] = []
    if m.group(3).strip():
        try:
            parsed = ast.literal_eval(f"[{m.group(3)}]")
            gated = [str(x) for x in parsed]
        except (ValueError, SyntaxError):
            gated = []
    status = {
        **out,
        "ok": r.returncode == 0 and stale_count == 0,
        "stale_count": stale_count,
        "gated_stale": gated,
        "files_checked": files_checked,
        "returncode": r.returncode,
    }
    # Last full-regen provenance receipt (best effort; never a 500).
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        status["last_receipt"] = {
            "graph_sha256": receipt.get("graph_sha256"),
            "passes": _last_run_passes(receipt_path),
            "converged": receipt.get("converged"),
            "vouched_count": len(receipt.get("vouched_patterns") or []),
            "failed": receipt.get("failed") or [],
            "generated_by": receipt.get("generated_by"),
        }
    except FileNotFoundError:
        status["receipt_error"] = f"no regen receipt at {receipt_path}"
    except (json.JSONDecodeError, OSError) as exc:
        status["receipt_error"] = f"unreadable regen receipt: {exc}"
    return status

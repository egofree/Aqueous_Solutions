# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""FastAPI surface for Aqueous design-tool P0 (AQS-UI-001 §7).

Locked / candidate MVS is read-only via GET /api/v1/mvs.
All mutations are sandbox-scoped.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .. import SCHEMA_VERSION, __version__
from ..export.pack import export_pack
from ..models import (
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

    Honest gaps preserved. Never claims mvs_equivalent from topology alone.
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
    drift visible to CI and operators.
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

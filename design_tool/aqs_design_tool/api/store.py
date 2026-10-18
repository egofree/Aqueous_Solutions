# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Sandbox store — mutations never touch locked graph / projection files."""

from __future__ import annotations

import copy
import json
import os
import threading
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from pydantic import ValidationError

from ..models import (
    MvsModel,
    SandboxOverrides,
    SolveResponse,
)
from ..paths import CANDIDATE_MVS_PATH, SANDBOX_STORE_DIR


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_mvs_from_graph(path: Path | None = None) -> MvsModel:
    """Sole authority load: plant_flow_graph.json → MvsModel (WP-Ap1)."""
    from ..flow_graph_adapter import load_plant_flow_graph_dict, mvs_from_graph

    if path is not None:
        return mvs_from_graph(load_plant_flow_graph_dict(path))
    return mvs_from_graph()


def load_candidate_mvs(path: Path | None = None) -> MvsModel:
    """Load MVS model — graph sole authority (WP-Ap2).

    Always prefers ``mvs_from_graph``. On-disk ``candidate_mvs.json`` is a
    generated projection only; if it drifts from the graph, a warning is
    recorded but the **graph** is still returned (never a divergent master).
    Fallback to the JSON file only if the graph itself is missing.
    """
    from ..flow_graph_adapter import (
        load_plant_flow_graph_dict,
        mvs_from_graph,
        projection_contract_status,
    )

    try:
        g = load_plant_flow_graph_dict()
        if isinstance(g.get("mvs"), dict):
            # Regen-check: warn on drift but do not load the drifted file
            try:
                status = projection_contract_status()
                if not status.get("ok"):
                    import warnings

                    warnings.warn(
                        "candidate_mvs.json drifts from plant_flow_graph "
                        f"projection: {status.get('issues')}. "
                        "Using graph authority; regenerate via "
                        "flow_graph/export_candidate_mvs.py",
                        UserWarning,
                        stacklevel=2,
                    )
            except Exception:  # noqa: BLE001 — contract check must not block solve
                pass
            return mvs_from_graph(g)
    except FileNotFoundError:
        pass

    p = path or CANDIDATE_MVS_PATH
    data = json.loads(p.read_text(encoding="utf-8"))
    data.pop("_projection", None)
    return MvsModel.model_validate(data)


def load_mvs_with_flow_graph(path: Path | None = None) -> MvsModel:
    """Alias for ``load_mvs_from_graph`` (graph sole authority)."""
    return load_mvs_from_graph(path)


def apply_overrides(model: MvsModel, overrides: SandboxOverrides) -> MvsModel:
    data = model.model_dump(by_alias=True, mode="json")
    if overrides.scale_m is not None:
        data["scale_m"] = overrides.scale_m
    if overrides.crew is not None:
        data["site"]["crew"] = overrides.crew
    if overrides.site_lat_deg is not None:
        data["site"]["site_lat_deg"] = overrides.site_lat_deg
    # Least specific first: sector rows (graph mvs.sectors), then tree
    # nodes (U4a). Tree keys are dotted ids in system_tree.yaml; a sector
    # id is also a valid tree node (root), so system_enabled{'ELEC'} acts
    # on units only while sector_enabled also flips the sector row.
    for sec in data.get("sectors", []):
        sid = sec["sector_id"]
        if sid in overrides.sector_enabled:
            sec["enabled"] = bool(overrides.sector_enabled[sid])
    if overrides.system_enabled or overrides.subsystem_enabled:
        from ..flow_graph_adapter import tree_override_unit_sets

        # subsystem entries merge after system entries, so a subsystem
        # flag outranks a train flag on overlap; unit_enabled below
        # outranks both (most-specific wins).
        merged: dict[str, bool] = {}
        for node_id, flag in {
            **overrides.system_enabled,
            **overrides.subsystem_enabled,
        }.items():
            try:
                unit_set = tree_override_unit_sets([node_id])[node_id]
            except KeyError as exc:
                raise KeyError(
                    f"override node '{node_id}' is not in "
                    f"flow_graph/system_tree.yaml: {exc}"
                ) from None
            for uid in unit_set:
                merged[uid] = bool(flag)
        for unit in data.get("units", []):
            if unit["unit_id"] in merged:
                unit["enabled"] = merged[unit["unit_id"]]
    if overrides.unit_enabled:
        for unit in data.get("units", []):
            uid = unit["unit_id"]
            if uid in overrides.unit_enabled:
                unit["enabled"] = bool(overrides.unit_enabled[uid])
    if overrides.unit_param_overrides:
        for unit in data.get("units", []):
            uid = unit["unit_id"]
            if uid in overrides.unit_param_overrides:
                unit.setdefault("params", {}).update(
                    overrides.unit_param_overrides[uid]
                )
    data["status"] = "sandbox"
    data["gaps"] = []
    data["unclosed_streams"] = []
    return MvsModel.model_validate(data)


@dataclass
class SandboxRecord:
    sandbox_id: str
    label: str
    model: MvsModel
    created_at: str
    updated_at: str
    last_solve: Optional[SolveResponse] = None
    parent_mvs_revision: str = "E-candidate"


class SandboxStore:
    """In-memory store with optional JSON mirror under .sandbox_store/."""

    def __init__(self, persist: bool = True) -> None:
        self._items: dict[str, SandboxRecord] = {}
        self._persist = persist
        # QA R2: FastAPI serves endpoints on a threadpool, so mirror
        # read-modify-writes need a lock to stay atomic per sandbox file.
        self._lock = threading.Lock()
        if persist:
            SANDBOX_STORE_DIR.mkdir(parents=True, exist_ok=True)

    def create(
        self,
        overrides: SandboxOverrides | None = None,
        label: str | None = None,
        base: MvsModel | None = None,
    ) -> SandboxRecord:
        with self._lock:
            # Default base: graph sole authority (WP-Ap1)
            base = base or load_mvs_from_graph()
            base_copy = MvsModel.model_validate(
                copy.deepcopy(base.model_dump(by_alias=True, mode="json"))
            )
            model = apply_overrides(base_copy, overrides or SandboxOverrides())
            sid = f"sbx_{uuid.uuid4().hex[:12]}"
            now = _now()
            rec = SandboxRecord(
                sandbox_id=sid,
                label=label or sid,
                model=model,
                created_at=now,
                updated_at=now,
                parent_mvs_revision=base.revision,
            )
            self._items[sid] = rec
            self._mirror(rec)
            return rec

    def _get_locked(self, sandbox_id: str) -> SandboxRecord:
        """Lookup + lazy mirror load. Caller must hold ``self._lock``."""
        if sandbox_id not in self._items:
            path = SANDBOX_STORE_DIR / f"{sandbox_id}.json"
            if path.is_file():
                # QA R2: a truncated / corrupt mirror must surface as
                # KeyError(sandbox_id) — the API maps that to 404 instead of
                # leaking JSONDecodeError / ValidationError as a 500.
                try:
                    raw = json.loads(path.read_text(encoding="utf-8"))
                    rec = SandboxRecord(
                        sandbox_id=raw["sandbox_id"],
                        label=raw.get("label", sandbox_id),
                        model=MvsModel.model_validate(raw["model"]),
                        created_at=raw["created_at"],
                        updated_at=raw["updated_at"],
                        last_solve=(
                            SolveResponse.model_validate(raw["last_solve"])
                            if raw.get("last_solve")
                            else None
                        ),
                        parent_mvs_revision=raw.get(
                            "parent_mvs_revision", "E-candidate"
                        ),
                    )
                except (
                    json.JSONDecodeError,
                    ValidationError,
                    KeyError,
                ) as exc:
                    raise KeyError(sandbox_id) from exc
                self._items[sandbox_id] = rec
                return rec
            raise KeyError(sandbox_id)
        return self._items[sandbox_id]

    def get(self, sandbox_id: str) -> SandboxRecord:
        with self._lock:
            return self._get_locked(sandbox_id)

    def patch(
        self,
        sandbox_id: str,
        overrides: SandboxOverrides,
        label: str | None = None,
    ) -> SandboxRecord:
        with self._lock:
            rec = self._get_locked(sandbox_id)
            rec.model = apply_overrides(rec.model, overrides)
            if label is not None:
                rec.label = label
            rec.updated_at = _now()
            rec.last_solve = None
            self._mirror(rec)
            return rec

    def set_solve(self, sandbox_id: str, result: SolveResponse) -> SandboxRecord:
        with self._lock:
            rec = self._get_locked(sandbox_id)
            rec.last_solve = result
            rec.updated_at = _now()
            dump = rec.model.model_dump(by_alias=True, mode="json")
            dump["gaps"] = [g.model_dump(mode="json") for g in result.gaps]
            dump["unclosed_streams"] = [
                u.model_dump(mode="json") for u in result.unclosed_streams
            ]
            rec.model = MvsModel.model_validate(dump)
            self._mirror(rec)
            return rec

    def _mirror(self, rec: SandboxRecord) -> None:
        if not self._persist:
            return
        path = SANDBOX_STORE_DIR / f"{rec.sandbox_id}.json"
        payload: dict[str, Any] = {
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
        # QA R2: write-then-rename so readers never see a half-written mirror.
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, path)


STORE = SandboxStore(persist=True)

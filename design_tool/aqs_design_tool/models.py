# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Pydantic models for Aqueous MVS (schema_version aqs-mvs-0.3+).

Aligned to AQS-UI-001 Rev C §6; surplus thresholds AQS-SUR-001. Study / stand-in numeric fields must
carry ``status: study`` until issued nameplates exist.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .sector_definitions import SectorDefinition


class RateStatus(str, Enum):
    STUDY = "study"
    AUTHORITY = "authority"
    ISSUED = "issued"
    TBD = "tbd"
    UNKNOWN = "unknown"


class Phase(str, Enum):
    S = "S"
    L = "L"
    G = "G"
    E = "E"
    SL = "S/L"
    LG = "L/G"
    GL = "G/L"
    LS = "L/S"


class Quantity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    value: Optional[float] = None
    unit: str = ""
    status: RateStatus = RateStatus.STUDY
    note: Optional[str] = None


class SiteModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    site_id: str = "AQS_SITE_M1"
    site_lat_deg: Optional[float] = None
    crew: Optional[int] = None
    jurisdiction_theme: str = "USA_Dallas_class"
    # WP C4/GHEX 2026-10-02: design_survey_locked is not a field measurement
    site_survey_status: Optional[str] = None
    site_survey_note: Optional[str] = None


class SectorModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sector_id: str
    sector_definition: SectorDefinition | str
    enabled: bool = True
    required_for_mvs_closure: bool = False
    notes: Optional[str] = None


class EquipmentModule(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    module_id: str
    class_name: Optional[str] = Field(default=None, alias="class")
    count: int = 1
    params: dict[str, Any] = Field(default_factory=dict)


class UnitModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    unit_id: str
    sector_id: str
    enabled: bool = True
    class_name: Optional[str] = Field(default=None, alias="class")
    tags: list[str] = Field(default_factory=list)
    params: dict[str, Any] = Field(default_factory=dict)
    modules: list[dict[str, Any] | str] = Field(default_factory=list)
    electrical_role: Optional[
        Literal["generation", "storage", "load", "bus", "none"]
    ] = None
    continuous_kw: Optional[Quantity] = None

    @field_validator("continuous_kw", mode="before")
    @classmethod
    def _coerce_kw(cls, v: object) -> object:
        # Rev AC graph shorthand: bare number means {value: n, unit: kW, status: study}
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            return {"value": float(v), "unit": "kW", "status": "study"}
        return v


class StreamModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stream_id: str
    from_unit_id: str
    to_unit_id: str
    phase: str
    carries: Optional[str] = None
    rate: Optional[Quantity] = None
    from_sector_id: Optional[str] = None
    to_sector_id: Optional[str] = None
    open_boundary: bool = False
    # When rate.value is null: explicit label (AQS-PLAN-UI-001 WP-A1). Not continuous-dump filler.
    null_rate_kind: Optional[
        Literal[
            "open_boundary",
            "inventory_cycle",
            "event",
            "unknown",
            "campaign_tbd",
            "study_deferred",
        ]
    ] = None
    note: Optional[str] = None


class ElectricalModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    bus_nodes: list[str] = Field(default_factory=list)
    storage_options: list[str] = Field(default_factory=list)
    need_kw: Optional[Quantity] = None
    target_kw: Optional[Quantity] = None
    pv_module_kw: Optional[float] = None
    pv_count: Optional[int] = None
    znbr_module_kw: Optional[float] = None
    znbr_count: Optional[int] = None
    rect_count: Optional[int] = None
    notes: Optional[str] = (
        "Study values from cad/freecad/params.py and AQS-REQ-KW-001; "
        "not vendor nameplates."
    )


class ScaleRulesModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tanks: Literal["continuous"] = "continuous"
    mfg_cryo: Literal["discrete"] = "discrete"
    pv_znbr2: Literal["module"] = "module"
    dock: Literal["by_cassette"] = "by_cassette"


class UiModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cycle_views: list[str] = Field(
        default_factory=lambda: ["C", "O", "H2O", "H2", "N", "heat"]
    )
    sector_toggles: bool = True
    gap_panel: bool = True
    export_modules: list[str] = Field(
        default_factory=lambda: [
            "params",
            "streams",
            "sld",
            "pfd",
            "bom",
            "compliance_flags",
            "3d",
        ]
    )



class SurplusThresholdsModel(BaseModel):
    """Study pass thresholds (AQS-SUR-001) — not freeze gold."""

    model_config = ConfigDict(extra="forbid")

    food_kg_d_min: Optional[float] = None
    clean_water_L_d_min: Optional[float] = None
    materials_or_goods_kg_d_min: Optional[float] = None
    energy_kWh_d_min: Optional[float] = None
    status: RateStatus = RateStatus.STUDY
    note: Optional[str] = None


class SelfCopyFlagsModel(BaseModel):
    """Self-copy checklist flags (AQS-BOM-SC-001) — Partial until complete."""

    model_config = ConfigDict(extra="forbid")

    critical_path_documented: bool = False
    reprap_bom_complete: bool = False
    lithography_on_site: bool = False
    lithography_in_mvs: bool = False
    blow_mold_in_mvs: bool = False
    vcd_remin_on_site: bool = False
    electrode_coating_on_site: bool = False
    bom_doc: Optional[str] = None
    note: Optional[str] = None
    # WP C4 2026-10-02: C3 Present criteria reminder (does not set *_on_site)
    present_criteria_note: Optional[str] = None


class MvsCriteriaModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    loops_closed: bool = False
    surplus_export: list[str] = Field(
        default_factory=lambda: [
            "food",
            "clean_water",
            "materials_or_goods",
            "energy",
        ]
    )
    note: str = (
        "Candidate MVS only until AQS-MVS-001 freeze; loops_closed must "
        "not be claimed true without solver evidence."
    )
    surplus_thresholds_doc: Optional[str] = None
    surplus_thresholds: Optional[SurplusThresholdsModel] = None
    self_copy: Optional[SelfCopyFlagsModel] = None


class GapModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sector_definition: Optional[str] = None
    sector_id: Optional[str] = None
    stream_id: Optional[str] = None
    reason: str
    detail: Optional[str] = None


class UnclosedStreamModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stream_id: str
    reason: str
    from_unit_id: Optional[str] = None
    to_unit_id: Optional[str] = None


class MvsModel(BaseModel):
    """Full typed MVS / sandbox design model."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str = "aqs-mvs-0.3"
    doc_id: str = "AQS-MVS-001"
    revision: str = "A-candidate"
    licence: str = "CERN-OHL-S-2.0"
    scale_m: float = 1.0
    status: Literal["candidate", "frozen", "sandbox"] = "candidate"
    mvs_criteria: MvsCriteriaModel = Field(default_factory=MvsCriteriaModel)
    site: SiteModel = Field(default_factory=SiteModel)
    sectors: list[SectorModel] = Field(default_factory=list)
    units: list[UnitModel] = Field(default_factory=list)
    streams: list[StreamModel] = Field(default_factory=list)
    electrical: ElectricalModel = Field(default_factory=ElectricalModel)
    scale_rules: ScaleRulesModel = Field(default_factory=ScaleRulesModel)
    ui: UiModel = Field(default_factory=UiModel)
    gaps: list[GapModel] = Field(default_factory=list)
    unclosed_streams: list[UnclosedStreamModel] = Field(default_factory=list)
    notes: Optional[str] = None


class SandboxOverrides(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sector_enabled: dict[str, bool] = Field(default_factory=dict)
    unit_enabled: dict[str, bool] = Field(default_factory=dict)
    scale_m: Optional[float] = None
    crew: Optional[int] = None
    site_lat_deg: Optional[float] = None
    unit_param_overrides: dict[str, dict[str, Any]] = Field(default_factory=dict)


class SandboxCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: Optional[str] = None
    overrides: SandboxOverrides = Field(default_factory=SandboxOverrides)


class SandboxPatchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    overrides: SandboxOverrides = Field(default_factory=SandboxOverrides)
    label: Optional[str] = None


class SolveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    objectives: list[str] = Field(
        default_factory=lambda: [
            "close_mass",
            "close_energy",
            "match_electrical",
            "report_surplus",
            "report_gaps",
        ]
    )
    tolerances: dict[str, float] = Field(
        default_factory=lambda: {"mass_rel": 1e-3, "power_kW": 0.5}
    )


class SurplusItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    value: Optional[float] = None
    unit: str
    status: RateStatus = RateStatus.STUDY
    note: Optional[str] = None
    pass_study: Optional[bool] = None
    threshold: Optional[float] = None


class ResidualItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    kind: str
    residual: Optional[float] = None
    unit: Optional[str] = None
    status: str = "incomplete"
    detail: Optional[str] = None


class BottleneckModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stream_id: Optional[str] = None
    unit_id: Optional[str] = None
    reason: str


class RedundantPathModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ids: list[str]
    reason: str


class CodeFlagModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    theme: str
    controlling: str = "most_restrictive"
    refs: list[str] = Field(default_factory=list)


class SolveResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["ok", "partial", "infeasible"] = "partial"
    mvs_equivalent: bool = False
    sandbox_id: Optional[str] = None
    residuals: dict[str, list[ResidualItem]] = Field(
        default_factory=lambda: {"mass": [], "energy": [], "electrical": []}
    )
    surplus: dict[str, SurplusItem] = Field(default_factory=dict)
    gaps: list[GapModel] = Field(default_factory=list)
    unclosed_streams: list[UnclosedStreamModel] = Field(default_factory=list)
    bottlenecks: list[BottleneckModel] = Field(default_factory=list)
    redundant_paths: list[RedundantPathModel] = Field(default_factory=list)
    code_flags: list[CodeFlagModel] = Field(default_factory=list)
    electrical_match: dict[str, Any] = Field(default_factory=dict)
    notes: list[str] = Field(default_factory=list)
    solved_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class ExportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    export_modules: list[str] = Field(
        default_factory=lambda: ["params", "streams", "compliance_flags"]
    )
    pack_name: Optional[str] = None


class ExportResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pack_dir: str
    files: list[str]
    notes: list[str] = Field(default_factory=list)


class FlagsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sandbox_id: str
    gaps: list[GapModel] = Field(default_factory=list)
    unclosed_streams: list[UnclosedStreamModel] = Field(default_factory=list)
    bottlenecks: list[BottleneckModel] = Field(default_factory=list)
    redundant_paths: list[RedundantPathModel] = Field(default_factory=list)
    code_flags: list[CodeFlagModel] = Field(default_factory=list)
    last_solve_status: Optional[str] = None

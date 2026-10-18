# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Mass-energy / electrical match / surplus / gaps solver stub (P0).

Does **not** invent false loop closure. Incomplete balances return
``status=partial`` with residuals and gaps populated. Study surplus
values may be null.

Scale-down / sector-off → unreclaimed_resource gaps per
``scale_down_map`` (AQS-SCALE-UR-001).
"""

from __future__ import annotations

from typing import Any

from ..models import (
    BottleneckModel,
    CodeFlagModel,
    GapModel,
    MvsModel,
    RateStatus,
    RedundantPathModel,
    ResidualItem,
    SolveRequest,
    SolveResponse,
    SurplusItem,
    UnclosedStreamModel,
)
from ..sector_definitions import (
    ESS_PEER_SECTOR_IDS,
    SECTOR_CATALOGUE,
    UNRECLAIMED_RESOURCE_REASON,
)
from .scale_down_map import (
    SECTOR_OFF_UNRECLAIMED,
    UNIT_OFF_UNRECLAIMED,
    derate_hits,
    streams_for_sector_off,
    streams_for_unit_off,
)


# Known contended / parallel paths from AQS-STR-001 / AQS-REQ-KW-001 study notes
_H2_POOL_STREAMS = {"S05", "S45", "S49", "S64", "S74"}
_PARALLEL_H2_CONSUMERS = ["S45", "S49", "S74"]


def _enabled_sector_ids(model: MvsModel) -> set[str]:
    return {s.sector_id for s in model.sectors if s.enabled}


def _disabled_sectors(model: MvsModel) -> list:
    return [s for s in model.sectors if not s.enabled]


def _unit_sector_map(model: MvsModel) -> dict[str, str]:
    return {u.unit_id: u.sector_id for u in model.units}


def _emit_unreclaimed_for_sector(
    gaps: list[GapModel],
    *,
    sector_id: str,
    sector_definition: str | None,
    required: bool,
) -> None:
    """Emit unreclaimed_resource gaps tied to stream_id per AQS-SCALE-UR-001."""
    entry = streams_for_sector_off(sector_id)
    base_detail = (
        entry["detail"]
        if entry
        else (
            f"Required sector '{sector_id}' disabled — incomplete closure / "
            "incomplete closure — open study queued (not accepted emissions/sub-MVS endpoint)."
            if required
            else f"Sector '{sector_id}' disabled."
        )
    )
    sec_def = (
        (entry["sector_definition"] if entry else None)
        or sector_definition
    )
    stream_ids = list(entry["stream_ids"]) if entry else []

    if stream_ids:
        for sid in stream_ids:
            gaps.append(
                GapModel(
                    sector_definition=sec_def,
                    sector_id=sector_id,
                    stream_id=sid,
                    reason=UNRECLAIMED_RESOURCE_REASON,
                    detail=f"{base_detail} [stream {sid}]",
                )
            )
    else:
        gaps.append(
            GapModel(
                sector_definition=sec_def,
                sector_id=sector_id,
                stream_id=None,
                reason=UNRECLAIMED_RESOURCE_REASON,
                detail=base_detail,
            )
        )


def _report_gaps(model: MvsModel) -> list[GapModel]:
    gaps: list[GapModel] = []
    for s in model.sectors:
        if s.required_for_mvs_closure and not s.enabled:
            # AQS-UI-001 Rev C / AQS-SCALE-UR-001: required sector or ESS off
            # → unreclaimed_resource (incomplete closure), with stream ties.
            _emit_unreclaimed_for_sector(
                gaps,
                sector_id=s.sector_id,
                sector_definition=str(s.sector_definition),
                required=True,
            )
            if s.sector_id in ESS_PEER_SECTOR_IDS:
                # Keep a sector-level summary gap for ESS peers (redundancy note)
                gaps.append(
                    GapModel(
                        sector_definition=str(s.sector_definition),
                        sector_id=s.sector_id,
                        stream_id=None,
                        reason=UNRECLAIMED_RESOURCE_REASON,
                        detail=(
                            f"Required ESS peer '{s.sector_id}' disabled — "
                            "framed as unreclaimed resource / incomplete "
                            "closure (not accepted pollution or emissions). "
                            "MVS requires all three ESS peers "
                            f"({', '.join(sorted(ESS_PEER_SECTOR_IDS))}); "
                            "redundancy is a core tenet."
                        ),
                    )
                )
            else:
                gaps.append(
                    GapModel(
                        sector_definition=str(s.sector_definition),
                        sector_id=s.sector_id,
                        stream_id=None,
                        reason="required_sector_disabled",
                        detail=(
                            "Sector required_for_mvs_closure is off; "
                            "sandbox is not MVS-equivalent "
                            "(incomplete closure). Stream-tied "
                            f"{UNRECLAIMED_RESOURCE_REASON} gaps also emitted."
                        ),
                    )
                )
        elif not s.enabled:
            # Optional sector off — still map streams as unreclaimed if listed
            if s.sector_id in SECTOR_OFF_UNRECLAIMED:
                _emit_unreclaimed_for_sector(
                    gaps,
                    sector_id=s.sector_id,
                    sector_definition=str(s.sector_definition),
                    required=False,
                )
            gaps.append(
                GapModel(
                    sector_definition=str(s.sector_definition),
                    sector_id=s.sector_id,
                    stream_id=None,
                    reason="sector_disabled",
                    detail="Optional sector disabled in sandbox.",
                )
            )


    # Unit-level offs (AQS-SCALE-UR-001 Rev C / WP-A7) — consume-ready
    for u in model.units:
        if getattr(u, "enabled", True):
            continue
        entry = streams_for_unit_off(u.unit_id)
        if not entry:
            gaps.append(
                GapModel(
                    sector_definition=None,
                    sector_id=u.sector_id,
                    stream_id=None,
                    reason=UNRECLAIMED_RESOURCE_REASON,
                    detail=(
                        f"Unit '{u.unit_id}' disabled — unreclaimed (no unit map row; "
                        "parent sector may still be on)."
                    ),
                )
            )
            continue
        base_detail = entry["detail"]
        sec_def = entry.get("sector_definition")
        stream_ids = list(entry["stream_ids"] or [])
        if stream_ids:
            for sid in stream_ids:
                gaps.append(
                    GapModel(
                        sector_definition=sec_def,
                        sector_id=u.sector_id,
                        stream_id=sid,
                        reason=UNRECLAIMED_RESOURCE_REASON,
                        detail=f"{base_detail} [unit {u.unit_id}; stream {sid}]",
                    )
                )
        else:
            gaps.append(
                GapModel(
                    sector_definition=sec_def,
                    sector_id=u.sector_id,
                    stream_id=None,
                    reason=UNRECLAIMED_RESOURCE_REASON,
                    detail=f"{base_detail} [unit {u.unit_id}]",
                )
            )

    # SCALE_M derate below M1 closure rules
    for rule in derate_hits(float(model.scale_m)):
        for sid in rule["stream_ids"]:
            gaps.append(
                GapModel(
                    sector_definition=None,
                    sector_id=None,
                    stream_id=sid,
                    reason=UNRECLAIMED_RESOURCE_REASON,
                    detail=f"{rule['detail']} [rule={rule['id']}; stream {sid}]",
                )
            )
        for sec in rule.get("sector_ids", []):
            gaps.append(
                GapModel(
                    sector_definition=None,
                    sector_id=sec,
                    stream_id=None,
                    reason=UNRECLAIMED_RESOURCE_REASON,
                    detail=f"{rule['detail']} [rule={rule['id']}; sector {sec}]",
                )
            )

    # Missing Sector Definition classes that the enabled graph may still need.
    # Re-derived from SECTOR_CATALOGUE (AQS-SEC-001 Rev E + Rev AC sector
    # refresh, 2026-10-18): every definition carried by a required sector
    # must be present on some enabled sector. The former hardcoded list kept
    # demanding 'Energy Production (Electrical)' after its only sector
    # (ELEC_PV) became the PV_ARRAY unit in ELEC, leaving the all-on
    # baseline permanently infeasible via missing_sector_definition.
    present_defs = {
        str(s.sector_definition) for s in model.sectors if s.enabled
    }
    required_defs = {
        row["sector_definition"]
        for row in SECTOR_CATALOGUE
        if row["required_for_mvs_closure"]
    }
    for needed in sorted(required_defs - present_defs):
        gaps.append(
            GapModel(
                sector_definition=needed,
                sector_id=None,
                stream_id=None,
                reason="missing_sector_definition",
                detail=f"No enabled sector carries definition '{needed}'.",
            )
        )

    # Orphan stream endpoints
    unit_ids = {u.unit_id for u in model.units}
    unit_map = _unit_sector_map(model)
    for st in model.streams:
        for end, uid in (("from", st.from_unit_id), ("to", st.to_unit_id)):
            if uid in unit_ids:
                continue
            if st.open_boundary or uid.startswith("HDR_") or uid.startswith("BOUNDARY_"):
                continue
            gaps.append(
                GapModel(
                    sector_definition=None,
                    sector_id=unit_map.get(uid),
                    stream_id=st.stream_id,
                    reason="orphan_unit_reference",
                    detail=f"Stream {st.stream_id} {end}_unit_id '{uid}' not in units table.",
                )
            )

    return gaps


def _report_unclosed(model: MvsModel) -> list[UnclosedStreamModel]:
    enabled = _enabled_sector_ids(model)
    unit_map = _unit_sector_map(model)
    # Unit-endpoint awareness (Rev AC unit toggles): a stream touching a
    # disabled unit is open at that endpoint even while both parent sectors
    # stay enabled. Sector-level checks above are unchanged.
    disabled_units = {
        u.unit_id for u in model.units if not getattr(u, "enabled", True)
    }
    out: list[UnclosedStreamModel] = []
    for st in model.streams:
        if st.open_boundary:
            out.append(
                UnclosedStreamModel(
                    stream_id=st.stream_id,
                    reason="open_boundary",
                    from_unit_id=st.from_unit_id,
                    to_unit_id=st.to_unit_id,
                )
            )
            continue
        from_sec = st.from_sector_id or unit_map.get(st.from_unit_id)
        to_sec = st.to_sector_id or unit_map.get(st.to_unit_id)
        if from_sec and from_sec not in enabled:
            out.append(
                UnclosedStreamModel(
                    stream_id=st.stream_id,
                    reason="upstream_sector_off",
                    from_unit_id=st.from_unit_id,
                    to_unit_id=st.to_unit_id,
                )
            )
        elif to_sec and to_sec not in enabled:
            out.append(
                UnclosedStreamModel(
                    stream_id=st.stream_id,
                    reason="downstream_sector_off",
                    from_unit_id=st.from_unit_id,
                    to_unit_id=st.to_unit_id,
                )
            )
        elif st.from_unit_id in disabled_units:
            out.append(
                UnclosedStreamModel(
                    stream_id=st.stream_id,
                    reason="upstream_unit_off",
                    from_unit_id=st.from_unit_id,
                    to_unit_id=st.to_unit_id,
                )
            )
        elif st.to_unit_id in disabled_units:
            out.append(
                UnclosedStreamModel(
                    stream_id=st.stream_id,
                    reason="downstream_unit_off",
                    from_unit_id=st.from_unit_id,
                    to_unit_id=st.to_unit_id,
                )
            )
        elif st.rate is None or st.rate.value is None:
            kind = getattr(st, "null_rate_kind", None)
            if kind == "inventory_cycle":
                reason = "null_inventory_cycle"
            elif kind == "event":
                reason = "null_event"
            elif kind == "open_boundary":
                reason = "null_open_boundary"
            elif kind in ("unknown", "campaign_tbd", "study_deferred"):
                reason = f"null_{kind}"
            else:
                reason = "rate_incomplete_study"
            out.append(
                UnclosedStreamModel(
                    stream_id=st.stream_id,
                    reason=reason,
                    from_unit_id=st.from_unit_id,
                    to_unit_id=st.to_unit_id,
                )
            )
    return out


def _electrical_match(model: MvsModel) -> tuple[dict[str, Any], list[ResidualItem]]:
    """Hook electrical generation / storage / load against study envelopes."""
    residuals: list[ResidualItem] = []
    enabled = _enabled_sector_ids(model)
    # Unit-level toggles (Rev AC): PV_ARRAY / FUEL_CELL / BACKUP_GEN / ZNBR2
    # are units in ELEC, so their kW follows the unit's own enabled flag —
    # a disabled unit leaves the envelope even while ELEC stays on.
    unit_on = {u.unit_id: bool(getattr(u, "enabled", True)) for u in model.units}
    elec = model.electrical

    gen_kw = 0.0
    storage_kw = 0.0
    load_kw = 0.0
    gen_sources: list[str] = []
    load_sources: list[str] = []

    for u in model.units:
        if u.sector_id not in enabled:
            continue
        if not unit_on.get(u.unit_id, True):
            # Disabled unit — its kW leaves the envelope.
            continue
        ck = u.continuous_kw
        val = ck.value if ck and ck.value is not None else None
        role = u.electrical_role
        if role == "generation" and val is not None:
            gen_kw += val
            gen_sources.append(u.unit_id)
        elif role == "storage" and val is not None:
            storage_kw += val
        elif role == "load" and val is not None:
            load_kw += val
            load_sources.append(u.unit_id)

    pv_kw = None
    if elec.pv_count is not None and elec.pv_module_kw is not None:
        pv_kw = elec.pv_count * elec.pv_module_kw
        # PV is counted only when its unit is on (ELEC_PV sector deleted at
        # the Rev AC pivot; PV_ARRAY is a generation-role unit in ELEC). A
        # model without a PV_ARRAY unit row has nothing to disable, so the
        # module product stands. Double-count guard kept: when PV_ARRAY
        # already books its nameplate as a generation-role unit, the
        # electrical-block product is the same plant — count it once.
        if unit_on.get("PV_ARRAY", True) and "PV_ARRAY" not in gen_sources:
            gen_kw += pv_kw
            gen_sources.append("PV_ARRAY_modules")

    need = elec.need_kw.value if elec.need_kw and elec.need_kw.value is not None else None
    target = (
        elec.target_kw.value if elec.target_kw and elec.target_kw.value is not None else None
    )

    match: dict[str, Any] = {
        "generation_kw_study": gen_kw if gen_sources else None,
        "storage_power_kw_study": storage_kw if storage_kw else None,
        "load_kw_study": load_kw if load_sources else None,
        "need_kw": need,
        "target_kw": target,
        "pv_nameplate_kw_study": pv_kw,
        "enabled_storage_options": [
            # Options named as units (ZNBR2 since Rev AC) follow the unit's
            # enabled flag; options named as sectors (MEOH, PUMPED_HYDRO)
            # follow the sector toggle.
            s
            for s in elec.storage_options
            if (unit_on.get(s, True) if s in unit_on else s in enabled)
        ],
        "status": "incomplete",
        "note": (
            "Electrical match is a study hook only (AQS-REQ-KW-001 / params.py). "
            "Does not claim plant balance closure. "
            "PUMPED_HYDRO continuous_kw incomplete at M1; energy ≪ ZnBr2 (AQS-ESS-001)."
        ),
    }

    if need is not None and gen_kw:
        residual = gen_kw - need
        residuals.append(
            ResidualItem(
                id="elec_gen_minus_need",
                kind="electrical",
                residual=residual,
                unit="kW",
                status="study",
                detail="Generation envelope minus ELEC_NEED_KW (study).",
            )
        )
        if residual < -0.5:
            match["status"] = "shortfall_study"
        else:
            match["status"] = "envelope_ok_study"
    else:
        residuals.append(
            ResidualItem(
                id="elec_match",
                kind="electrical",
                residual=None,
                unit="kW",
                status="incomplete",
                detail="Insufficient issued rates for full electrical match.",
            )
        )

    return match, residuals


def _surplus_stub(model: MvsModel) -> dict[str, SurplusItem]:
    """Surplus from FARM/WTR/DIGESTER·MFG·FAB/PV_ARRAY vs AQS-SUR-001 study thresholds.

    Energy gate is the PV_ARRAY unit (ELEC_PV sector deleted at the Rev AC
    pivot; PV is a unit in ELEC).
    """
    enabled = _enabled_sector_ids(model)
    thr = model.mvs_criteria.surplus_thresholds
    food_thr = thr.food_kg_d_min if thr and thr.food_kg_d_min is not None else 0.5
    water_thr = thr.clean_water_L_d_min if thr and thr.clean_water_L_d_min is not None else 50.0
    goods_thr = (
        thr.materials_or_goods_kg_d_min
        if thr and thr.materials_or_goods_kg_d_min is not None
        else 5.0
    )
    energy_thr = thr.energy_kWh_d_min if thr and thr.energy_kWh_d_min is not None else 20.0

    crew = model.site.crew if model.site.crew is not None else 4
    ration = 0.6  # study kg/person·d (AQS-SUR-001)

    rates = {s.stream_id: (s.rate.value if s.rate else None) for s in model.streams}

    # Food: S14 − crew ration
    food_val = None
    food_pass = None
    food_note = "FARM disabled — food surplus gap."
    if "FARM" in enabled:
        s14 = rates.get("S14")
        if s14 is not None:
            food_val = max(0.0, float(s14) - float(crew) * ration)
            food_pass = food_val >= food_thr
            food_note = (
                f"Study surplus food={food_val:.2f} kg/d (S14−crew×{ration}); "
                f"threshold {food_thr} kg/d (AQS-SUR-001); pass_study={food_pass}."
            )
        else:
            food_note = "FARM enabled; S14 rate null — food surplus unknown."

    # Clean water: inventory ≫ daily use → study export capability when WTR on (AQS-SUR-001)
    water_val = None
    water_pass = None
    water_note = "WTR sector off — clean-water surplus gap."
    if "WTR" in enabled:
        s01 = rates.get("S01")
        s21 = rates.get("S21")
        demand = 285.0  # potable+farm+fab study (AQS-SUR-001)
        if s01 is not None or s21 is not None:
            water_val = 50.0  # study export capability — roof inventory ≫ daily
            water_pass = water_val >= water_thr
            water_note = (
                f"WTR on; study clean-water export capability={water_val:.0f} L/d "
                f"(inventory ≫ demand ~{demand:.0f} L/d; AQS-AUD-001 §11 / AQS-SUR-001); "
                f"pass_study={water_pass}. Potable export blocked until VCD/remin Present "
                "(ST-VCD-01/ST-REMIN-01 open studies; vcd_remin_on_site=false)."
            )
        else:
            water_note = "WTR on but S01/S21 rates null — water surplus unknown."

    # Goods: study exportable from metals/polymer when DIGESTER·MFG(+FAB)
    # (WET renamed DIGESTER at the Rev AC sector pivot; the WET test is
    # kept for legacy sandboxes)
    goods_val = None
    goods_pass = None
    goods_note = "DIGESTER/MFG off — materials gap."
    if "WET" in enabled or "MFG" in enabled:
        s08 = rates.get("S08")
        if s08 is not None:
            goods_val = 0.25 * float(s08) + (12.0 if "MFG" in enabled else 0.0)
            if "FAB" not in enabled:
                goods_note = (
                    f"Study goods envelope={goods_val:.1f} kg/d but FAB off — "
                    "incomplete (A2 requires FAB+MFG)."
                )
                goods_pass = False
            else:
                goods_pass = goods_val >= goods_thr
                goods_note = (
                    f"Study goods surplus={goods_val:.1f} kg/d (0.25×S08 + MFG scrap study); "
                    f"threshold {goods_thr} kg/d; pass_study={goods_pass}."
                )
        else:
            goods_note = "DIGESTER/MFG on; S08 null — goods surplus unknown."

    # Energy: (target−need)×study_sun_h — gated on the PV_ARRAY unit
    # (ELEC_PV sector deleted at Rev AC; PV_ARRAY is a unit in ELEC).
    pv_unit_on = next(
        (
            bool(getattr(u, "enabled", True))
            for u in model.units
            if u.unit_id == "PV_ARRAY"
        ),
        True,
    )
    energy_val = None
    energy_pass = None
    energy_note = "PV_ARRAY unit off — energy surplus gap."
    if pv_unit_on:
        need = model.electrical.need_kw.value if model.electrical.need_kw else None
        target = model.electrical.target_kw.value if model.electrical.target_kw else None
        sun_h = 4.0  # AQS-SUR-001 placeholder until SITE_LAT
        if need is not None and target is not None:
            energy_val = max(0.0, (float(target) - float(need)) * sun_h)
            energy_pass = energy_val >= energy_thr
            lat = model.site.site_lat_deg
            energy_note = (
                f"Study energy headroom={energy_val:.0f} kWh/d ((target−need)×{sun_h} h); "
                f"threshold {energy_thr}; pass_study={energy_pass}. "
                f"SITE_LAT={'null — insolation unknown' if lat is None else lat}."
            )
        else:
            energy_note = "PV_ARRAY on; need/target incomplete — energy surplus unknown."

    return {
        "food": SurplusItem(
            value=food_val, unit="kg/d", status=RateStatus.STUDY,
            note=food_note, pass_study=food_pass, threshold=food_thr,
        ),
        "clean_water": SurplusItem(
            value=water_val, unit="L/d", status=RateStatus.STUDY,
            note=water_note, pass_study=water_pass, threshold=water_thr,
        ),
        "materials_or_goods": SurplusItem(
            value=goods_val, unit="kg/d", status=RateStatus.STUDY,
            note=goods_note, pass_study=goods_pass, threshold=goods_thr,
        ),
        "energy": SurplusItem(
            value=energy_val, unit="kWh/d", status=RateStatus.STUDY,
            note=energy_note, pass_study=energy_pass, threshold=energy_thr,
        ),
    }



def _bottlenecks(model: MvsModel) -> list[BottleneckModel]:
    enabled = _enabled_sector_ids(model)
    out: list[BottleneckModel] = []
    present = {st.stream_id for st in model.streams}
    consumers_on = []
    for st in model.streams:
        if st.stream_id in _PARALLEL_H2_CONSUMERS:
            to_sec = st.to_sector_id
            if to_sec is None or to_sec in enabled:
                consumers_on.append(st.stream_id)
    if len(consumers_on) > 1:
        out.append(
            BottleneckModel(
                stream_id="S05",
                reason="H2_pool_contended",
            )
        )
    if "CRYO" in enabled and "S64" in present:
        pass
    return out


def _redundant(model: MvsModel) -> list[RedundantPathModel]:
    present = {st.stream_id for st in model.streams}
    out: list[RedundantPathModel] = []
    if "S45" in present and "S49" in present:
        out.append(
            RedundantPathModel(
                ids=["S45", "S49"],
                reason="parallel_H2_consumers",
            )
        )
    if "S51" in present and "S79" in present:
        out.append(
            RedundantPathModel(
                ids=["S51", "S79"],
                reason="parallel_BATT_DC_injectors",
            )
        )
    return out


def _mass_residuals_polish(model: MvsModel, unclosed: list[UnclosedStreamModel]) -> list[ResidualItem]:
    """Per-pool study residuals from filled rates — never invents closure (WP-A8)."""
    enabled = _enabled_sector_ids(model)
    rates = {
        s.stream_id: (s.rate.value if s.rate and s.rate.value is not None else None)
        for s in model.streams
    }
    out: list[ResidualItem] = []

    # H2 pool: generation S05/S64 vs consumers S45+S49+S74 (study; contended)
    gen_h2 = 0.0
    cons_h2 = 0.0
    h2_known = False
    for sid, sign in (("S05", "gen"), ("S64", "gen"), ("S45", "cons"), ("S49", "cons"), ("S74", "cons")):
        v = rates.get(sid)
        if v is None:
            continue
        h2_known = True
        if sign == "gen":
            # S05 and S64 are alternate views of same Faraday pool — take max not sum
            gen_h2 = max(gen_h2, float(v)) if sid in ("S05", "S64") else gen_h2 + float(v)
        else:
            cons_h2 += float(v)
    if h2_known:
        # Prefer S05 as Faraday source if present else S64
        src = rates.get("S05")
        if src is None:
            src = rates.get("S64")
        gen_use = float(src) if src is not None else gen_h2
        residual = gen_use - cons_h2
        out.append(
            ResidualItem(
                id="h2_pool_gen_minus_consumers",
                kind="mass",
                residual=residual,
                unit="kg/d",
                status="study",
                detail=(
                    f"Study H2: source={gen_use:.2f} vs sum(S45/S49/S74)={cons_h2:.2f} kg/d. "
                    "Negative ⇒ contended / schedule incomplete (AQS-ESS-001); "
                    "not invented simultaneous full-duty closure."
                ),
            )
        )

    # Food: S14 − crew ration − S14X (export should match surplus)
    s14 = rates.get("S14")
    s14x = rates.get("S14X")
    if "FARM" in enabled and s14 is not None:
        crew = model.site.crew if model.site.crew is not None else 4
        ration = 0.6
        expected_export = max(0.0, float(s14) - float(crew) * ration)
        if s14x is not None:
            food_resid = round(expected_export - float(s14x), 6)
            out.append(
                ResidualItem(
                    id="food_export_vs_s14x",
                    kind="mass",
                    residual=food_resid,
                    unit="kg/d",
                    status="study",
                    detail=(
                        f"S14={s14} − crew×{ration} → expected export {expected_export:.2f}; "
                        f"S14X={s14x}; residual={food_resid:.2f} (study)."
                    ),
                )
            )
        else:
            out.append(
                ResidualItem(
                    id="food_export_vs_s14x",
                    kind="mass",
                    residual=None,
                    unit="kg/d",
                    status="incomplete",
                    detail="S14 present but S14X null — food export residual incomplete.",
                )
            )

    # Water inventory: S01 vs S21 study couples (roof makeup)
    s01 = rates.get("S01")
    s21 = rates.get("S21")
    if "WTR" in enabled and s01 is not None and s21 is not None:
        out.append(
            ResidualItem(
                id="water_s01_minus_s21",
                kind="mass",
                residual=float(s01) - float(s21),
                unit="kg/d",
                status="study",
                detail=(
                    f"Study UPW S01={s01} vs clean tower S21={s21} kg/d. "
                    "S22/S23 inventory_cycle nulls excluded (not continuous)."
                ),
            )
        )

    n_labeled_null = sum(
        1
        for u in unclosed
        if u.reason.startswith("null_") or u.reason == "rate_incomplete_study"
    )
    out.append(
        ResidualItem(
            id="mass_balance_plant",
            kind="mass",
            residual=None,
            unit="kg/d",
            status="incomplete",
            detail=(
                "Full multi-species plant balance not claimed. "
                f"{n_labeled_null} null-labeled / rate-incomplete streams remain. "
                "Scale-down unreclaimed per AQS-SCALE-UR-001 Rev C — no invented mass closure. "
                "loops_closed must stay false."
            ),
        )
    )
    return out


def _energy_residuals_polish(model: MvsModel, elec_match: dict[str, Any]) -> list[ResidualItem]:
    """Energy residuals: electrical hook + hydro vs ZnBr2 asymmetry note (WP-A4/A8)."""
    out: list[ResidualItem] = [
        ResidualItem(
            id="energy_balance_plant",
            kind="energy",
            residual=None,
            unit="kWh/d",
            status="incomplete",
            detail=(
                "Plant energy balance deferred; electrical match hook only. "
                f"elec_match.status={elec_match.get('status')}."
            ),
        )
    ]
    znbr = next((u for u in model.units if u.unit_id == "ZNBR2"), None)
    hydro = next((u for u in model.units if u.unit_id == "HYDRO_SET"), None)
    if znbr is not None and hydro is not None:
        znbr_kwh = None
        if znbr.params and znbr.params.get("kWh") is not None:
            znbr_kwh = float(znbr.params["kWh"])
        hydro_kwh = None
        if hydro.params and hydro.params.get("energy_kwh_ideal_study") is not None:
            hydro_kwh = float(hydro.params["energy_kwh_ideal_study"])
        if znbr_kwh is not None and hydro_kwh is not None:
            out.append(
                ResidualItem(
                    id="hydro_vs_znbr2_energy_asymmetry",
                    kind="energy",
                    residual=hydro_kwh - znbr_kwh,
                    unit="kWh",
                    status="study",
                    detail=(
                        f"M1 hydro ideal {hydro_kwh} kWh ≪ ZnBr2 {znbr_kwh} kWh "
                        f"(~{100.0 * hydro_kwh / znbr_kwh:.0f}%). Documented asymmetry "
                        "(AQS-ESS-001); continuous hydro kW incomplete; not silent loss."
                    ),
                )
            )
    return out



def solve(model: MvsModel, request: SolveRequest | None = None, sandbox_id: str | None = None) -> SolveResponse:
    """Run P0 stub solve. Never sets loops_closed / mvs_equivalent true without evidence."""
    request = request or SolveRequest()
    gaps = _report_gaps(model)
    unclosed = _report_unclosed(model)
    elec_match, elec_residuals = _electrical_match(model)
    surplus = _surplus_stub(model)
    bottlenecks = _bottlenecks(model)
    redundant = _redundant(model)

    mass_residuals = _mass_residuals_polish(model, unclosed)
    energy_residuals = _energy_residuals_polish(model, elec_match)

    required_off = any(g.reason == "required_sector_disabled" for g in gaps)
    missing_def = any(g.reason == "missing_sector_definition" for g in gaps)
    unreclaimed = any(g.reason == UNRECLAIMED_RESOURCE_REASON for g in gaps)
    rate_incomplete = any(
        u.reason == "rate_incomplete_study" or u.reason.startswith("null_")
        for u in unclosed
    )
    sector_route_breaks = any(
        u.reason in ("upstream_sector_off", "downstream_sector_off") for u in unclosed
    )

    notes = [
        "P0 solver stub — residuals/gaps/surplus structure only.",
        "Does not claim full plant balance closure.",
        "Study / stand-in / authority-doc rates labeled; not PE-stamped nameplates.",
        "Scale-down map: AQS-SCALE-UR-001 (cad/SCALE_DOWN_UNRECLAIMED.md).",
    ]

    mvs_equivalent = False  # WP-A8: never true while incomplete / Partial self-copy
    hard_incomplete = required_off or missing_def or unreclaimed
    if hard_incomplete or sector_route_breaks:
        status: str = "infeasible" if hard_incomplete else "partial"
        if required_off:
            notes.append(
                "Required MVS-closure sector(s) disabled → not MVS-equivalent "
                "(incomplete closure)."
            )
        if unreclaimed:
            missing_ess = sorted(
                {
                    g.sector_id
                    for g in gaps
                    if g.reason == UNRECLAIMED_RESOURCE_REASON
                    and g.sector_id
                    and g.sector_id in ESS_PEER_SECTOR_IDS
                }
            )
            ur_streams = sorted(
                {
                    g.stream_id
                    for g in gaps
                    if g.reason == UNRECLAIMED_RESOURCE_REASON and g.stream_id
                }
            )
            notes.append(
                f"Unreclaimed-resource gaps emitted ({UNRECLAIMED_RESOURCE_REASON}); "
                "incomplete closure (not accepted emissions); not MVS-equivalent "
                "(no invented storage/mass closure)."
            )
            if missing_ess:
                notes.append(
                    "Required ESS peer(s) disabled: " + ", ".join(missing_ess) + "."
                )
            if ur_streams:
                notes.append(
                    "Stream-tied unreclaimed ids (sample): "
                    + ", ".join(ur_streams[:12])
                    + ("…" if len(ur_streams) > 12 else "")
                    + "."
                )
    else:
        status = "partial"
        notes.append(
            "All required sectors enabled, but mass/energy rates incomplete — "
            "status remains partial (no false loop closure)."
        )

    sc = model.mvs_criteria.self_copy
    if sc and not sc.reprap_bom_complete:
        notes.append(
            "Self-copy BOM Partial (AQS-BOM-SC-001 Rev G) — reprap_bom_complete=false; "
            "ST-LITHO/BLOW/ELC/VCD/REMIN/ORC/SOLAR physics issued; Present/survey external TBD "
            "(not accepted gaps; sandbox tracks MVS)."
        )
    if rate_incomplete:
        n_null = sum(
            1
            for u in unclosed
            if u.reason == "rate_incomplete_study" or u.reason.startswith("null_")
        )
        notes.append(
            f"{n_null} streams lack numeric rates (null_rate_kind / study labels; "
            "no invented continuous dump)."
        )
    food_item = surplus.get("food")
    if food_item is not None and food_item.pass_study is True:
        notes.append(
            "Food surplus pass_study=true vs AQS-SUR-001 (upper-band FARM path study)."
        )
    elif food_item is not None and food_item.pass_study is False:
        notes.append("Food surplus below AQS-SUR-001 study bar (pass_study=false).")
    hydro = next((u for u in model.units if u.unit_id == "HYDRO_SET"), None)
    if hydro is not None:
        notes.append(
            "PUMPED_HYDRO M1 energy ≪ ZnBr2 (AQS-ESS-001); continuous_kw incomplete — "
            "symbolic redundancy at M1; scale-up V×h path in unit params."
        )

    code_flags = [
        CodeFlagModel(
            theme="IBC_height_or_NFPA_footprint",
            controlling="most_restrictive",
            refs=["AQS-CMP-001", "AQS-EGR-001"],
        )
    ]

    return SolveResponse(
        status=status,  # type: ignore[arg-type]
        mvs_equivalent=mvs_equivalent,
        sandbox_id=sandbox_id,
        residuals={
            "mass": mass_residuals,
            "energy": energy_residuals,
            "electrical": elec_residuals,
        },
        surplus=surplus,
        gaps=gaps,
        unclosed_streams=unclosed,
        bottlenecks=bottlenecks,
        redundant_paths=redundant,
        code_flags=code_flags,
        electrical_match=elec_match,
        notes=notes,
    )

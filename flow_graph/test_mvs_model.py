# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Schema regression: the projected candidate_mvs.json validates against MvsModel.

Covers the site survey fields (site_survey_status, site_survey_note) carried on
mvs.site since WP C4 2026-10-02, and confirms that loops_closed and every
*_on_site flag remain false in the projection.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
DESIGN_TOOL = ROOT.parent / "design_tool"
for p in (ROOT, DESIGN_TOOL):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

pydantic = pytest.importorskip("pydantic")

from aqs_design_tool.models import MvsModel, SiteModel  # noqa: E402
from authority_contract import CANDIDATE_PATH, GRAPH_PATH  # noqa: E402
from export_candidate_mvs import project_candidate_mvs  # noqa: E402


def test_site_model_accepts_survey_fields() -> None:
    site = SiteModel.model_validate(
        {
            "site_id": "AQS_SITE_M1",
            "site_lat_deg": 33.0,
            "crew": 4,
            "site_survey_status": "design_survey_locked",
            "site_survey_note": "design basis; field measurement external",
        }
    )
    assert site.site_survey_status == "design_survey_locked"
    assert site.site_survey_note


def test_site_model_still_forbids_unknown_fields() -> None:
    with pytest.raises(pydantic.ValidationError):
        SiteModel.model_validate({"site_id": "X", "not_a_field": 1})


def test_candidate_on_disk_validates() -> None:
    data = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    model = MvsModel.model_validate(data)
    assert model.site.site_survey_status == data["site"].get("site_survey_status")


def test_projection_validates_and_flags_stay_false() -> None:
    graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
    model = MvsModel.model_validate(project_candidate_mvs(graph))
    crit = model.mvs_criteria
    assert crit.loops_closed is False
    assert crit.self_copy is not None
    on_site = {k: v for k, v in crit.self_copy.model_dump().items() if k.endswith("_on_site")}
    assert on_site, "expected *_on_site flags on mvs_criteria.self_copy"
    for name, value in on_site.items():
        assert value is False, name

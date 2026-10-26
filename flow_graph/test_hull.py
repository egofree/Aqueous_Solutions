# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""X-LOC-11 hull gate: the floating-island hull carries the plant with stability and freeboard
margin on the stated dimensions (AQS-SITE-012)."""
import pytest
from flow_graph.param import drivers as DR, hull


@pytest.fixture(scope='module')
def result():
    return hull.design(DR.load())


def test_hull_carries_the_plant_with_margin(result):
    assert result['ok'] and not result['errors']


def test_draft_leaves_freeboard(result):
    assert 0 < result['draft_m'] < result['D_m']
    assert result['freeboard_m'] >= result['freeboard_min_m']


def test_stability_is_positive_with_margin(result):
    assert result['GM_m'] >= result['gm_min_m']
    assert result['KB_m'] > 0 and result['BM_m'] > 0 and result['KG_m'] > 0


def test_operating_mass_sums(result):
    assert result['operating_mass_t'] == pytest.approx(result['plant_mass_t'] + result['lightweight_t'], rel=1e-6)
    assert result['plant_mass_t'] > 0


def test_roll_period_is_physical(result):
    # a box pontoon rolls in seconds, not minutes; the study bound keeps the driver honest
    assert 3.0 <= result['roll_period_s'] <= 30.0


def test_document_renders():
    txt = hull.render(hull.design(DR.load()))
    assert 'Document number: AQS-SITE-012' in txt and 'Check passes' in txt

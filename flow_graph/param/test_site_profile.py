# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Site profile checks (AQS-PLAN-011 sections 4 and 13): the baseline profile reproduces drivers.json
exactly, a missing value is an error, and every script reads the drivers through the loader."""
import copy, json, os, re, subprocess
import pytest
from flow_graph.param import drivers as DR, site as S

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def base():
    return json.load(open(S.path(S.BASELINE)))


def test_baseline_resolves_to_drivers_json(monkeypatch):
    monkeypatch.delenv(S.ENV, raising=False)
    raw, res = DR.raw(), DR.load()
    assert list(raw) == list(res)
    for k in raw:
        assert json.dumps(raw[k]) == json.dumps(res[k]), k


def test_every_profile_validates():
    for sid in S.available():
        assert S.validate(json.load(open(S.path(sid))), sid) == []
        S.apply(DR.raw(), sid)


def test_bindings_exist_with_matching_units(base):
    raw = DR.raw()
    for dk, (pk, e) in S.bindings(base).items():
        assert dk in raw, pk
        assert raw[dk]['units'] == e['units'], pk


def test_missing_group_is_an_error(base):
    for gk in S.groups_spec():
        p = copy.deepcopy(base); del p['groups'][gk]
        assert any(f'group {gk} missing' in e for e in S.validate(p)), gk


def test_missing_entry_is_an_error(base):
    for gk, gs in S.groups_spec().items():
        if 'entries' not in base['groups'][gk]: continue
        for ek in gs['entries']:
            p = copy.deepcopy(base); del p['groups'][gk]['entries'][ek]
            assert any(f'{gk}.{ek} missing' in e for e in S.validate(p)), (gk, ek)


def test_entry_without_value_or_basis_is_an_error(base):
    p = copy.deepcopy(base); e = p['groups']['thermal']['entries']['heating_dry_bulb_C']
    del e['value']
    assert any('value/units missing' in x for x in S.validate(p))
    p = copy.deepcopy(base); e = p['groups']['thermal']['entries']['heating_dry_bulb_C']
    e.pop('register', None); e.pop('ref', None); e.pop('owner', None)
    assert any('no ref, register id or owner basis' in x for x in S.validate(p))
    p = copy.deepcopy(base); p['groups']['thermal']['entries']['heating_dry_bulb_C']['ref'] = 'NO_SUCH_REF'
    assert any('unknown ref' in x for x in S.validate(p))


def test_group_without_entries_needs_reason_or_task(base):
    always = [g for g, s in S.groups_spec().items() if s['always']]
    optional = [g for g, s in S.groups_spec().items() if not s['always']]
    p = copy.deepcopy(base); p['groups'][always[0]] = {'not_applicable': 'x'}
    assert any('required at every site' in x for x in S.validate(p))
    p = copy.deepcopy(base); p['groups'][optional[0]] = {}
    assert any('no not_applicable reason' in x for x in S.validate(p))
    p = copy.deepcopy(base); p['groups'][optional[0]] = {'pending': 'later'}
    assert any('no not_applicable reason' in x for x in S.validate(p))


def test_unknown_site_fails(monkeypatch):
    monkeypatch.setenv(S.ENV, 'no_such_site')
    with pytest.raises(SystemExit, match='not found'):
        DR.load()


def test_units_mismatch_fails(tmp_path, monkeypatch, base):
    p = copy.deepcopy(base)
    p['groups']['wind']['entries']['basic_wind_speed_m_s']['units'] = 'mph'
    monkeypatch.setattr(S, 'SITES', str(tmp_path)); p['site_id'] = 'bad'
    (tmp_path / 'bad.json').write_text(json.dumps(p))
    with pytest.raises(SystemExit, match='differ from driver'):
        DR.load('bad')


def test_bound_value_reaches_the_drivers(tmp_path, monkeypatch, base):
    p = copy.deepcopy(base); p['site_id'] = 'hot'
    p['groups']['thermal']['entries']['cooling_dry_bulb_C']['value'] = 46.0
    monkeypatch.setattr(S, 'SITES', str(tmp_path))
    (tmp_path / 'hot.json').write_text(json.dumps(p))
    assert DR.load('hot')['site_design_dry_bulb_C']['value'] == 46.0


def test_no_direct_drivers_json_reads():
    """Only drivers.py opens drivers.json; every other script goes through drivers.load()."""
    files = subprocess.run(['git', 'ls-files', '*.py'], cwd=ROOT, capture_output=True, text=True).stdout.split()
    pat = re.compile(r'(open|read_text|read_bytes|json\.load)\([^)\n]*drivers\.json')
    bad = [f for f in files if f != 'flow_graph/param/drivers.py' and pat.search(open(os.path.join(ROOT, f), errors='replace').read())]
    assert bad == []

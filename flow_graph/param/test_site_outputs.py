# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Locale outputs (AQS-PLAN-011 section 4.4): a locale run never writes a baseline file."""
import json, os, subprocess
import pytest
from flow_graph.param import regen, site_outputs as SO


def test_baseline_has_no_site_folder():
    with pytest.raises(SystemExit):
        SO.site_dir('baseline')


@pytest.mark.parametrize('rel', ['../../docs-authority/HVAC.md', '/etc/passwd', '../venus/x.md', 'a/../../../x'])
def test_target_cannot_leave_the_site_folder(tmp_path, rel):
    with pytest.raises(SystemExit, match='must stay under'):
        SO.target('mars', rel, str(tmp_path))


def test_target_mirrors_the_repository_path(tmp_path):
    assert SO.target('mars', 'docs-authority/HVAC.md', str(tmp_path)) == os.path.realpath(str(tmp_path / 'sites/mars/docs-authority/HVAC.md'))


def test_document_number_takes_the_site_code_once():
    t = '# HVAC\n\nDocument number: AQS-THM-002\nRevision: B\n\nText AQS-THM-002.\n'
    once = SO.suffix_numbers(t, 'MARS')
    assert 'Document number: AQS-THM-002/MARS\n' in once and 'Text AQS-THM-002.' in once
    assert SO.suffix_numbers(once, 'MARS') == once


def test_in_place_locale_run_is_refused(monkeypatch):
    monkeypatch.setenv('AQS_SITE', 'mars'); monkeypatch.delenv(SO.ENV_WT, raising=False)
    with pytest.raises(SystemExit, match='temporary worktree'):
        regen.main(['--quick'])


def test_unknown_site_is_refused():
    with pytest.raises(SystemExit, match='not found'):
        regen.main(['--site', 'no_such_site'])


def test_collect_and_write_stay_in_the_site_folder(tmp_path, monkeypatch):
    wt = tmp_path / 'wt'; root = tmp_path / 'root'; wt.mkdir(); root.mkdir()
    g = lambda *a: subprocess.run(['git', *a], cwd=wt, check=True, capture_output=True)
    g('init', '-q'); (wt / 'gen').mkdir(); (wt / 'docs-authority').mkdir()
    (wt / 'gen/A.md').write_text('# A\n\nDocument number: AQS-THM-002\n\nv 1\n')
    (wt / 'gen/B.md').write_text('same\n')
    (wt / 'docs-authority/DERIVED_REVISIONS.md').write_text('c1\n')
    g('add', '-A'); g('-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-qm', 'base')
    (wt / 'gen/A.md').write_text('# A\n\nDocument number: AQS-THM-002\n\nv 2\n')
    (wt / 'docs-authority/DERIVED_REVISIONS.md').write_text('c2\n')
    (wt / 'gen/new.json').write_text('{}\n')
    monkeypatch.setattr(SO.S, 'load_profile', lambda sid=None: {'site_id': 'mars', 'site_code': 'MARS'})
    monkeypatch.setattr(SO, 'profile_hash', lambda sid, root=None: 'h')
    files = SO.collect('mars', str(wt))
    assert sorted(files) == ['gen/A.md', 'gen/new.json']
    assert b'AQS-THM-002/MARS' in files['gen/A.md']
    man = SO.write('mars', files, [], str(root))
    written = sorted(os.path.relpath(os.path.join(d, f), root) for d, _, fs in os.walk(root) for f in fs)
    assert written == ['sites/mars/SITE_OUTPUTS.json', 'sites/mars/gen/A.md', 'sites/mars/gen/new.json']
    assert json.load(open(root / 'sites/mars/SITE_OUTPUTS.json'))['outputs'] == man['outputs']

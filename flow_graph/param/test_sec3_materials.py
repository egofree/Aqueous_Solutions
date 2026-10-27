"""X-MAT-22 lane gates (AQS-STD-006, A-M-318..328): the 38 held units each carry an issued duty
section 3 material selection; the X-FARM/X-HAB lane (materials3.SEL_FARM, A-M-415..425) extends
the same gate to the FARM/HAB build-out units. The roster section 3 sweep is clean, the internals
task-09 hold is gone, the brine family of AQS-STD-002 section 12.2 is issued, and the
new refs.py sources of the lane exist."""
import csv, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

def _sel():
    g = json.load(open(f'{ROOT}/flow_graph/plant_flow_graph.json'))
    return {n['unit_id']: n.get('params', {}).get('sec3_material')
            for n in g['nodes'] if (n.get('params') or {}).get('sec3_material')}

def test_sec3_selections_issued_and_rendered():
    sel = _sel()
    # the selections are derived from the issued lanes, not pinned (2026-10-26 parametric pass):
    # the graph carries exactly what flow_graph/param/materials3.py issues (stale-writer guard),
    # and the closed X-MAT-22 task-09 batch keeps its audited 38-unit roster
    from flow_graph.param import materials3
    assert set(sel) == set(materials3.SEL) | set(materials3.SEL_FARM)
    assert len(materials3.SEL) == 38
    for u, s in sel.items():
        assert all(s.get(k) for k in ('mat', 'basis', 'alt', 'note', 'task')), u
        d = open(f'{ROOT}/docs-authority/duties/{u}.md').read()
        m3 = re.search(r'^3\. Material\..*$', d, re.M)
        assert m3, f'no duty section 3 on {u}'
        t = m3.group(0)
        assert 'Selection pending' not in t and 'Not chosen' not in t, u
        assert 'Basis:' in t and 'Alternative:' in t and f"({s['task']})" in t, u

def test_std002_122_brine_family_issued():
    s = open(f'{ROOT}/docs-authority/MATERIALS_STD.md').read()
    sec = s.split('### 12.2', 1)[1].split('### 12.3', 1)[0]
    n = 0
    for ln in sec.splitlines():
        if ln.startswith('|') and '---' not in ln and '| Family' not in ln:
            c = [x.strip() for x in ln.split('|')]
            n += 1
            assert 'pending' not in c[3].lower() and 'task 09' not in c[3].lower(), ln
    assert n >= 5, n   # 3 original '—' families + the 2 issued brine rows

def test_unit_materials_roster_clean():
    um = json.load(open(f'{ROOT}/docs-authority/inventory/UNIT_MATERIALS.json'))
    assert um.get('open') == {}, um.get('open')

def test_internals_task09_hold_gone():
    i = open(f'{ROOT}/docs-authority/INTERNALS.md').read()
    assert 'same hold as task 09' not in i

def test_eol_no_duty3_unclassed_holds():
    held = []
    for r in csv.DictReader(open(f'{ROOT}/docs-authority/inventory/EOL_RETURN.csv')):
        if r.get('hold', '').startswith('held - duty sheet section 3'):
            held.append(r)
    assert not held, (held[0] if held else None, len(held))

def test_lane_refs_registered():
    from flow_graph.param.refs import REFS
    for k in ('DING2018_CL_REVIEW', 'DING2021_ENG', 'KRUIZENGA2012', 'KROLL1940',
              'ULLMANN_MAGNESIUM', 'ULLMANN_TITANIUM', 'ULLMANN_WAX', 'MANG2007',
              'WANG2006_ADS', 'SCHACHT2004', 'ASM_V1', 'ASM_V7'):
        assert k in REFS and len(REFS[k]) > 100 and '.py' not in REFS[k], k

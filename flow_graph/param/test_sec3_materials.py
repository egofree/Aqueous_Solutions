"""X-MAT-22 lane gates (AQS-STD-006, A-M-318..328): the 38 held units each carry an issued duty
section 3 material selection; the X-FARM/X-HAB lane (materials3.SEL_FARM, A-M-415..425) extends
the same gate to the FARM/HAB build-out units, and the X-QA-13 lane (materials3.SEL_QA13) extends
it to the acid and base regeneration line (BMED_ACID, BMED_BASE, EVAP_ACID). The roster
section 3 sweep is clean, the internals task-09 hold is gone, the brine family of AQS-STD-002
section 12.2 is issued, and the new refs.py sources of the lane exist."""
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
    # and the closed lanes keep their audited rosters (X-MAT-22 task-09 batch, X-FARM/X-HAB,
    # X-QA-13 acid and base regeneration line)
    from flow_graph.param import materials3
    roster = set(materials3.SEL) | set(materials3.SEL_FARM) | set(materials3.SEL_QA13)
    assert set(sel) == roster
    # Invariant, not a count (F-20261110-09): every lane entry is a live stamped unit on the
    # graph, so a roster entry cannot outlive its unit and a new unit joins only through the
    # lane writer. The membership set equality above pins the roster itself.
    units = {n['unit_id'] for n in json.load(open(f'{ROOT}/flow_graph/plant_flow_graph.json'))['nodes']
             if n.get('presence') != 'retired'}
    assert roster <= units, sorted(roster - units)
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


def test_xqa13_regen_line_wetted_metal_gated_and_consistent():
    """X-QA-13 gate: in the chlor-alkali and acid-regeneration units every wetted part is PVC or
    another polymer selected by chemical compatibility (AQS-STD-002 M2/M3/M5), the electrodes
    are metal by electrochemical compatibility (M6), and metal outside the wetted and vapour
    zone is allowed by M4. A metal-bearing mfg-BOM row in these units without one of those rule
    tags or a lining class fails here, and the reselected parts state one selection in every
    generated writer (mfg BOM, sizing page, internals register, duty sheets)."""
    import csv
    metal = re.compile(r'316|304|stainless|titanium|nickel|carbon steel|monel|hastelloy|'
                       r'copper|brass|\bTi\b|Ti/MMO|Ti G', re.I)
    clear = ('AQS-STD-002 M6', 'AQS-STD-002 M4', 'AQS-STD-002 M5',
             'PTFE-lined', 'PVDF', 'steam side', 'graphite', 'glass')
    for u in ('BMED_ACID', 'BMED_BASE', 'EVAP_ACID'):
        with open(f'{ROOT}/models/mfg/{u}/bom.csv') as fh:
            for r in csv.DictReader(fh):
                row = ' '.join(r.values())
                if metal.search(row) and not any(c in row for c in clear):
                    raise AssertionError(
                        f'{u} bom item {r["item"]}: bare wetted metal without an AQS-STD-002 '
                        f'M-rule or lining class: {r["description"]}')
    # the reselected parts carry the same selection in every writer
    for u in ('BMED_ACID', 'BMED_BASE'):
        bom = open(f'{ROOT}/models/mfg/{u}/bom.csv').read()
        assert '316L/Ni' not in bom, u
        rows = list(csv.DictReader(open(f'{ROOT}/models/mfg/{u}/bom.csv')))
        cath = next(r for r in rows if 'Cathode end plate' in r['description'])
        assert cath['material'] == '316L' and 'AQS-STD-002 M6' in cath['basis'], (u, cath)
        rods = next(r for r in rows if 'Tie rods' in r['description'])
        assert rods['material'].startswith('316L') and 'AQS-STD-002 M4' in rods['basis'], (u, rods)
    evap = list(csv.DictReader(open(f'{ROOT}/models/mfg/EVAP_ACID/bom.csv')))
    assert '316L/Ni' not in open(f'{ROOT}/models/mfg/EVAP_ACID/bom.csv').read()
    shell = next(r for r in evap if r['description'].startswith('Shell'))
    assert 'carbon steel' in shell['material'] and 'PTFE-lined' in shell['material'], shell
    for f in ('docs-authority/sizing/BMED_STACK.md', 'docs-authority/INTERNALS.md',
              'docs-authority/duties/BMED_ACID.md', 'docs-authority/duties/BMED_BASE.md'):
        assert '316L/Ni' not in open(f'{ROOT}/{f}').read(), f

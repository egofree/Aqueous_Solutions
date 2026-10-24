"""X-CTL-04 gate: the control-program source (AQS-CTL-004) matches the instrument index,
the refreshed AQS-CTL-002 module table, and the scan simulation passes."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flow_graph.control.plc_programs import (  # noqa: E402
    load_loops, plc_table, scan_budget, simulate, _span, ST_DIR,
)


def _loops():
    return load_loops()


def test_classification_counts():
    loops = _loops()
    counts = {}
    for r in loops:
        counts[r['cls']] = counts.get(r['cls'], 0) + 1
    assert set(counts) == {'CONTROL', 'INDICATION', 'SIF'}
    ## every independent SIF element of the instrument index (tag numbers 90 and up) is a SIF loop, and nothing else is
    sif_tags = [r for r in loops if int(r['loop'].split('-')[-1]) >= 90]
    assert counts['SIF'] == len(sif_tags)


def test_setpoints_from_the_graph():
    sp = {r['loop']: r['sp'] for r in _loops() if r['cls'] == 'CONTROL'}
    assert sp['CRYO_ASUPT-01'] == 17.5          # design 17.5 kPa g from the graph
    assert sp['POLY_OLEFINPT-01'] == 5000.0     # design P_MPa 5.0 (A-M-283 poly wave)
    assert sp['CRYO_CO2TE-01'] == 25.0          # design T 25 C
    zero = [r for r in _loops() if r['cls'] == 'CONTROL' and r['sp'] == 0]
    for r in zero:
        assert r['pv_hi'] == 0.0 and r['pv_lo'] is None   # expected-zero: any positive PV alarms


def test_span_parse_coverage():
    ## only the 2 rupture-disc PSH discretes carry no engineering span
    unparsed = [r['loop'] for r in _loops() if _span(r)[0] is None]
    assert len(unparsed) == 2


def test_st_files_match_the_architecture_table():
    plcs = plc_table()
    ## one program per PLC in the architecture table, and no program for a PLC that has left it
    assert sorted(f[:-3] for f in os.listdir(ST_DIR) if f.endswith('.st')) == sorted(plcs)
    assert {r['plc'] for r in _loops()} <= set(plcs)
    for plc in plcs:
        path = os.path.join(ST_DIR, f'{plc}.st')
        assert os.path.isfile(path), path
        src = open(path).read()
        assert src.startswith('(* AQS-CTL-004 X-CTL-04')
        assert f'PROGRAM {plc.replace("-", "_")}_CTRL' in src
        ## SIF watch inputs are declared but never acted on in the basic program
        if 'SIF' in src:
            for line in src.splitlines():
                assert 'SIF' not in line or 'watch' in line or 'safety CPU pair' in line


def test_scan_simulation_zero_fails():
    loops = _loops()
    res, fails = simulate(loops, None)
    assert fails == [], fails[:5]
    assert res['CONTROL'][0] > 0 and res['INDICATION'][0] > 0 and res['SIF'][0] == sum(1 for r in loops if r['cls'] == 'SIF')


def test_ai_cross_check_against_control_arch():
    sanity = scan_budget(_loops(), plc_table())
    assert all(d['diff'] == 0 for d in sanity.values())

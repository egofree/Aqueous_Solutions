"""X-QA-07 / Q-040: the standby generator rating on the graph is the live computation, not a
stored nameplate. backup_fuel.rating_kw() derives it from critical_list() at 125 percent rounded
up in the commercial 5 kW step (AQS-ELEC-007 / AQS-RED-001, owner ruling Q-040, 2026-11-05);
write_graph.power stamps the result on BACKUP_GEN. This test re-derives the rating from the
committed graph and drivers and requires the stamped value to match, rule for rule."""
import json, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from flow_graph.param import drivers as DR
from flow_graph.param import backup_fuel as BF


def test_backup_gen_rating_is_the_live_computation():
    g = json.load(open(ROOT + '/flow_graph/plant_flow_graph.json'))
    d = DR.load()
    gc = {n['unit_id']: n for n in g['nodes']}
    gen = BF.rating_kw(gc, d)
    stamped = gc['BACKUP_GEN']['params']['rated_kW']
    assert stamped == gen['rated_kW'], (
        f'BACKUP_GEN rated_kW {stamped} != the live critical-list computation {gen["rated_kW"]}')
    crit = sum(float(v) for v in BF.critical_list(gc, d).values())
    margin = DR.val(d, BF.K + 'crit_margin')
    step = DR.val(d, BF.K + 'rating_step_kw')
    expect = -(-crit * margin // step) * step   # ceil to the commercial step, the rating_kw rule
    assert gen['rated_kW'] == expect, (
        f'rating {gen["rated_kW"]} != {margin:g} x the critical list {crit:.2f} kW rounded up in {step:g} kW steps')

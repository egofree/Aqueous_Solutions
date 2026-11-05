"""Parametric-provenance gate (AGENTS.md Sizing): everything in the model is parametric.
Every size is computed from demand and supply through the drivers and the transfer
functions, so every present unit must trace to the registered sizing machinery: an entry
in docs-authority/inventory/SIZING_COVERAGE.json (the evidence registry, whose build
asserts the cited sizing document names the unit) or a registered study/interim basis in
docs-authority/assumptions_manual.json (an entry whose where/files field names the unit).
A unit with neither is an unregistered size; the test fails listing them. Extend coverage
through flow_graph/param/sizing_coverage.py or register an assumption - never weaken
this test, and never carry a size on a plug value."""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _load():
    g = json.load(open(os.path.join(ROOT, 'flow_graph/plant_flow_graph.json')))
    cov = json.load(open(os.path.join(ROOT, 'docs-authority/inventory/SIZING_COVERAGE.json')))
    am = json.load(open(os.path.join(ROOT, 'docs-authority/assumptions_manual.json')))
    # where (where used) and files are the register's designated usage fields (AGENTS.md Assumptions)
    texts = [' '.join([str(a.get('where', '')), ' '.join(a.get('files', []))]) for a in am]
    return g, cov, texts


def _assumption_naming(u, texts):
    return re.search(r'\b' + re.escape(u) + r'\b', ' \n '.join(texts))


def test_sized_unit_traces_to_registered_sizing():
    """Every present, non-boundary unit with a params.design block (a sized unit) is covered
    by the sizing evidence registry or by a registered assumption. A design block with
    neither is the unregistered plug-value pattern the sizing audits exist to stop."""
    g, cov, texts = _load()
    bad = [n['unit_id'] for n in g['nodes']
           if n.get('presence') == 'present' and n.get('class') != 'boundary'
           and n.get('params', {}).get('design')
           and n['unit_id'] not in cov and not _assumption_naming(n['unit_id'], texts)]
    assert not bad, 'sized units with no SIZING_COVERAGE.json entry and no registered assumption basis: %s' % bad


def test_every_present_unit_has_registered_sizing_basis():
    """No present, non-boundary unit exists outside the sizing evidence registry and the
    assumptions register: a unit with neither has no sizing calculation anywhere.
    Fix coverage through flow_graph/param/sizing_coverage.py (or a registered assumption),
    not by exempting the unit here."""
    g, cov, texts = _load()
    bad = [n['unit_id'] for n in g['nodes']
           if n.get('presence') == 'present' and n.get('class') != 'boundary'
           and n['unit_id'] not in cov and not _assumption_naming(n['unit_id'], texts)]
    assert not bad, ('present units with neither a SIZING_COVERAGE.json entry nor a registered '
                     'assumption basis (extend flow_graph/param/sizing_coverage.py or register an '
                     'assumption - never a plug value): %s' % bad)

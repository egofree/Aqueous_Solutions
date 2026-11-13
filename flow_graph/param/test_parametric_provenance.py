"""Parametric-provenance gate (AGENTS.md Sizing): everything in the model is parametric.
Every size is computed from demand and supply through the drivers and the transfer
functions, so every present unit must trace to the registered sizing machinery: an entry
in docs-authority/inventory/SIZING_COVERAGE.json (the evidence registry, whose build
asserts the cited sizing document names the unit) or a registered study/interim basis in
docs-authority/assumptions_manual.json (an entry whose where/files field names the unit).
A unit with neither is an unregistered size; the test fails listing them. Extend coverage
through flow_graph/param/sizing_coverage.py or register an assumption - never weaken
this test, and never carry a size on a plug value.

The gate also compares values, not only identifiers (X-QA-09): for the sizing families
whose calculation is a pure design(d, g) function, the test recomputes each family in
memory from drivers.json and the committed graph and requires every value the node's
params.design block states to equal that recomputation (at the writer's 4-decimal
rounding), with the block carrying nothing the basis does not compute and nothing
computed left unwritten. Boundary of the value check, so a green tree stays green:
reactor_design reads edge rates at its own DAG position (S75/S74/S73 and the unit
inflows move after the stage runs), so it verifies only inside the pipeline - the regen
receipt owns it until the stage reads its inputs at the final state (X-QA-18). The
evaporators, the BMED stack, the EW cascade and the PV nameplate already value-compare
through solver.check() (test_param_misfit, the 1 % gate). The per-unit sweep documents (AQS-SIZE-*) are re-rendered from the graph by every
unit_sizing_sweep stage run (docs-authority/_unit_sizing_sweep.py render_body; F-20261112-02
retired the -02-close freeze), and test_sweep_sizing_docs_match_the_graph below holds every
sweep-owned doc to that render - a frozen snapshot fails there naming the unit."""
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


# --- X-QA-09: the sizing basis must hold the values the model carries --------------------
#
# Ten sizing families compute their unit design blocks in a pure design(d, g) function and
# write the result verbatim into the node's params.design (floats at the writer's 4-decimal
# convention). The recomputation needs only drivers.json and the committed graph, so the
# check below re-runs it in memory and compares values - read-only, no stage runs.

# (module, the family evidence doc the coverage build cites for these units, result getter).
# The unit list comes from each design() result - it is not repeated here.
_FAMILY_BASIS = [
    ('geo_loop', 'docs-authority/sizing/GEO_LOOP.md', lambda m, d, g: m.design(d, g)),
    ('house_scrubbers', 'docs-authority/sizing/HOUSE_SCRUBBERS.md', lambda m, d, g: m.design(d, g)),
    ('receivers', 'docs-authority/sizing/GAS_RECEIVERS.md', lambda m, d, g: m.design(d, g)),
    ('heat_battery', 'docs-authority/sizing/HEAT_BATTERY.md', lambda m, d, g: m.design(d, g)),
    ('headers', 'docs-authority/sizing/HEADERS.md', lambda m, d, g: m.design(d, g)),
    ('meoh_train', 'docs-authority/sizing/MEOH_TRAIN.md', lambda m, d, g: m.design(d, g)),
    ('cold_box', 'docs-authority/sizing/COLD_BOX.md', lambda m, d, g: {'CRYO_ASU': m.design(d, g)}),
    ('h2_purifier', 'docs-authority/sizing/H2_PURIFIER_BEDS.md', lambda m, d, g: {'H2_DRYER': m.design(d, g)}),
    ('pv_cell_line', 'docs-authority/sizing/PV_CELL_LINE.md', lambda m, d, g: {'SOLAR_PV_CELL': m.design(d)}),
    ('upw_polish', 'docs-authority/sizing/UPW_POLISH.md', lambda m, d, g: {'BMED_UPW_POLISH': m.design(d, g)}),
]

# Design-block keys a writer adds as its own integer round of a computed value, not values
# the basis states under the same name: cold_box.write stores H_mm/D_mm = round(bed_L_mm /
# bed_D_mm). Any key added here needs the writer line that derives it, cited beside it.
_WRITER_DERIVED_KEYS = {
    ('CRYO_ASU', '.D_mm'): 'flow_graph/param/cold_box.py write(): round(r["bed_D_mm"])',
    ('CRYO_ASU', '.H_mm'): 'flow_graph/param/cold_box.py write(): round(r["bed_L_mm"])',
}


def _flatten(x, pre=''):
    out = {}
    if isinstance(x, dict):
        for k, v in x.items():
            out.update(_flatten(v, pre + '.' + str(k)))
    elif isinstance(x, list):
        for i, v in enumerate(x):
            out.update(_flatten(v, '%s[%d]' % (pre, i)))
    else:
        out[pre] = x
    return out


def _value_agrees(committed, computed):
    """The stage writers store computed floats rounded to 4 decimals; accept that convention
    (half-ulp of the last written digit, plus a float slack at the rounding boundary)."""
    if isinstance(committed, bool) or isinstance(computed, bool):
        return committed == computed
    if isinstance(committed, (int, float)) and isinstance(computed, (int, float)):
        return abs(committed - computed) <= 5.05e-5 + 1e-9 * abs(computed)
    return committed == computed


def _design_value_mismatches(g, d, cov):
    """Recompute every family design in memory and compare it with the committed params.design
    blocks. Returns failure strings naming the unit, the key and both values."""
    from flow_graph.param import drivers as DR
    import importlib
    N = {n['unit_id']: n for n in g['nodes']}
    bad = []
    for mod_name, doc, get in _FAMILY_BASIS:
        R = get(importlib.import_module('flow_graph.param.' + mod_name), DR.load() if d is None else d, g)
        for u in sorted(R):
            entry = cov.get(u)
            if entry is None:
                bad.append('%s: recomputed by flow_graph/param/%s.py design() but has no '
                           'SIZING_COVERAGE.json entry' % (u, mod_name))
                continue
            if entry.get('doc') != doc:
                bad.append('%s: the registry cites %s but the %s family build cites %s'
                           % (u, entry.get('doc'), mod_name, doc))
                continue
            committed = (N.get(u) or {}).get('params', {}).get('design')
            if not isinstance(committed, dict) or not committed:
                bad.append('%s: %s.design() computes a sizing basis but the graph carries no '
                           'params.design block' % (u, mod_name))
                continue
            have, want = _flatten(committed), _flatten(R[u])
            for k in sorted(set(want) - set(have)):
                bad.append('%s%s: computed by %s.design() as %r but never written to the graph'
                           % (u, k, mod_name, want[k]))
            for k in sorted(set(have) - set(want)):
                if (u, k) not in _WRITER_DERIVED_KEYS:
                    bad.append('%s%s: design-block value %r that the %s family basis does not '
                               'compute (a size without its calculation)'
                               % (u, k, have[k], mod_name))
                elif not isinstance(have[k], (int, float)) or isinstance(have[k], bool):
                    bad.append('%s%s: listed writer-derived but is not numeric: %r' % (u, k, have[k]))
            for k in sorted(set(have) & set(want)):
                if not _value_agrees(have[k], want[k]):
                    bad.append('%s%s: graph %r != %s.design() recomputation %r '
                               '(drivers.json at the committed graph)'
                               % (u, k, have[k], mod_name, want[k]))
            if not (set(have) & set(want)):
                bad.append('%s: the graph design block and the %s.design() recomputation share '
                           'no key - nothing was actually compared' % (u, mod_name))
    return sorted(bad)


def test_design_block_values_match_the_family_sizing_basis():
    """X-QA-09 (values, not only identifiers): for every pure-function sizing family, each value
    the node's params.design block states equals the family design() recomputation from
    drivers.json at the committed graph, the block states nothing the basis does not compute,
    and nothing computed is left unwritten. A hand-edited size or a drifted writer fails here
    naming the unit, the key and both values. See the module docstring for what stays outside
    this check and why."""
    g, cov, _texts = _load()
    bad = _design_value_mismatches(g, None, cov)
    assert not bad, ('sized values disagreeing with their recomputed sizing basis: %s' % bad)


# --- F-20261112-02: the per-unit sweep documents must mirror the graph --------------------
#
# The unit_sizing_sweep stage re-renders every present unit's template-owned AQS-SIZE doc
# from the committed graph on every run; ownership follows the template, so a doc another
# writer rewrote into its own shape stays out of scope here (its values are covered by the
# family checks above instead). The check imports the generator's render_body and holds each
# committed doc to that render byte for byte: the basis line (duty / params.design /
# params.sizing / design_storage / envelope / state) and the vessel geometry are pure
# functions of the graph, so a stale frozen snapshot fails naming the unit and the line.

def _sweep_module():
    import importlib.util
    path = os.path.join(ROOT, 'docs-authority/_unit_sizing_sweep.py')
    spec = importlib.util.spec_from_file_location('aqs_unit_sizing_sweep', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _first_diff(want, got):
    for wl, gl in zip(want.splitlines(), got.splitlines()):
        if wl != gl:
            return 'doc states %r, the graph render states %r' % (gl, wl)
    return 'doc carries %d lines, the graph render %d' % (len(got.splitlines()), len(want.splitlines()))


def test_sweep_sizing_docs_match_the_graph():
    """Every present unit whose sizing doc carries the unit_sizing_sweep template matches the
    stage render from the committed graph exactly - a later writer that supersedes a node's
    sizing basis cannot leave a stale snapshot behind it. Run the unit_sizing_sweep stage to
    refresh; never hand-edit the doc to pass."""
    sweep = _sweep_module()
    stale = []
    for uid in sorted(sweep.N):
        u = sweep.N[uid]
        if u.get('presence') != 'present' or not sweep.sweep_owned(uid):
            continue
        want = sweep.render_body(uid)
        got = open(os.path.join(ROOT, 'docs-authority/sizing/%s.md' % uid),
                   encoding='utf-8', errors='replace').read()
        if want != got:
            stale.append('%s: %s' % (uid, _first_diff(want, got)))
    assert not stale, ('per-unit sweep documents stale against the graph (the '
                       'unit_sizing_sweep stage owns them; refresh, do not hand-edit): %s' % stale)

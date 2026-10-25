# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Site profiles (AQS-PLAN-011 section 4). One file per locale in flow_graph/param/sites/<site_id>.json
carries every environmental input in the form of a driver. The groups and the entries each group must
carry are listed once, in flow_graph/schema/site_profile.schema.json ("x-groups"). An entry with
"binds" supplies that drivers.json key; drivers.load() applies it through apply(). The profile is
chosen by the AQS_SITE environment variable; without it the baseline profile is used."""
import json, os, re
from .refs import REFS

HERE = os.path.dirname(os.path.abspath(__file__))
SITES = os.path.join(HERE, 'sites')
SCHEMA = os.path.join(os.path.dirname(HERE), 'schema', 'site_profile.schema.json')
BASELINE = 'baseline'
ENV = 'AQS_SITE'
_META = ('binds',)


def site_id():
    """The selected site id: AQS_SITE, else the baseline."""
    return os.environ.get(ENV) or BASELINE


def path(sid=None):
    return os.path.join(SITES, f'{sid or site_id()}.json')


def available():
    return sorted(f[:-5] for f in os.listdir(SITES) if f.endswith('.json'))


def groups_spec():
    return json.load(open(SCHEMA))['x-groups']


def validate(prof, name='profile'):
    """Return a list of errors: a missing group, a missing required entry, an entry without units or
    a basis, an unknown reference key, or a pending group without a task id."""
    err, spec = [], groups_spec()
    if not re.match(r'^[a-z][a-z0-9_]*$', str(prof.get('site_id', ''))): err.append(f'{name}: site_id missing or malformed')
    g = prof.get('groups')
    if not isinstance(g, dict): return err + [f'{name}: groups missing']
    for gk in g:
        if gk not in spec: err.append(f'{name}: unknown group {gk}')
    for gk, gs in spec.items():
        grp = g.get(gk)
        if grp is None: err.append(f'{name}: group {gk} missing'); continue
        if 'entries' not in grp:
            if gs['always']: err.append(f'{name}: group {gk} is required at every site and must carry entries')
            elif grp.get('not_applicable'): pass
            elif not re.match(r'^X-[A-Z]+-[0-9]+$', str(grp.get('pending', ''))): err.append(f'{name}: group {gk} has no entries, no not_applicable reason and no pending task id')
            continue
        ents = grp['entries']
        for ek in gs['entries']:
            if ek not in ents: err.append(f'{name}: {gk}.{ek} missing')
        for ek, e in ents.items():
            k = f'{name}: {gk}.{ek}'
            if not isinstance(e, dict) or 'value' not in e or 'units' not in e: err.append(f'{k}: value/units missing'); continue
            if not (e.get('ref') or e.get('register') or e.get('owner')): err.append(f'{k}: no ref, register id or owner basis')
            if e.get('ref') and e['ref'] not in REFS: err.append(f'{k}: unknown ref {e["ref"]}')
            if e.get('needs_verification') and not e.get('verification_test'): err.append(f'{k}: needs_verification without verification_test')
    return err


def load_profile(sid=None):
    sid = sid or site_id()
    p = path(sid)
    if not os.path.exists(p):
        raise SystemExit(f'site profile {sid!r} not found ({ENV}); available: {", ".join(available())}')
    prof = json.load(open(p))
    err = validate(prof, os.path.relpath(p, os.path.dirname(os.path.dirname(HERE))))
    if prof.get('site_id') != sid: err.append(f'{sid}: site_id {prof.get("site_id")!r} does not match the file name')
    if err: raise SystemExit('site profile: ' + '; '.join(err))
    return prof


def entries(prof):
    """Every entry as ('group.entry', entry dict)."""
    for gk, grp in prof['groups'].items():
        for ek, e in (grp.get('entries') or {}).items():
            yield f'{gk}.{ek}', e


def bindings(prof):
    return {e['binds']: (k, e) for k, e in entries(prof) if e.get('binds')}


def apply(drivers, sid=None):
    """Replace every bound driver with the profile entry that supplies it. The units must match."""
    prof = load_profile(sid); err = []
    for dk, (pk, e) in bindings(prof).items():
        if dk not in drivers: err.append(f'{pk}: binds unknown driver {dk}'); continue
        if drivers[dk].get('units') != e['units']: err.append(f'{pk}: units {e["units"]!r} differ from driver {dk} {drivers[dk].get("units")!r}')
        drivers[dk] = {f: x for f, x in e.items() if f not in _META}
    if err: raise SystemExit('site profile: ' + '; '.join(err))
    return drivers


def val(key, sid=None):
    """Value of a profile entry by 'group.entry'."""
    gk, ek = key.split('.', 1)
    grp = load_profile(sid)['groups'][gk]
    if 'entries' not in grp: raise SystemExit(f'site profile: {gk} is {"not applicable" if grp.get("not_applicable") else "pending " + grp.get("pending", "")} at this site; {key} has no value')
    return grp['entries'][ek]['value']

"""Independent inputs. drivers.json holds each value with units, a reference key (refs.REFS)
or a register id, and needs_verification / verification_test when no published value fixes it."""
import json, os
from .refs import REFS
P = os.path.join(os.path.dirname(__file__), 'drivers.json')
def load():
    d = json.load(open(P)); err = []
    for k, v in d.items():
        if 'value' not in v or 'units' not in v: err.append(f'{k}: value/units missing')
        if not (v.get('ref') or v.get('register') or v.get('owner')): err.append(f'{k}: no ref, register id or owner basis')
        if v.get('ref') and v['ref'] not in REFS: err.append(f'{k}: unknown ref {v["ref"]}')
        if v.get('needs_verification') and not v.get('verification_test'): err.append(f'{k}: needs_verification without verification_test')
    if err: raise SystemExit('drivers.json: ' + '; '.join(err))
    return d
def val(d, k): return d[k]['value']

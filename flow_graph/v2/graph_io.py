"""engine v2: serialization — the single write.

load(): parse the serialized graph into a Builder (passthrough values verbatim).
bytes(): render the model to the serialized bytes. A builder with an empty
computed overlay reproduces the input bytes exactly (the strangler bridge:
untouched fields round-trip; migrated fields emit grid-exact decimals derived
from their integer counts — never floats computed at render time).
write(): atomic (tmp + os.replace). This module is the engine's only writer of
the graph file.
"""
import json, os
from copy import deepcopy
from decimal import Decimal

from .grid import Grid, Qty, _default_grid
from .model import Builder, Model, Prov

INDENT = 2


def load(path, grid=None):
    with open(path, encoding='utf-8') as f:
        return Builder(json.load(f))


def _numeric(qty, grid):
    """The exact numeric value of a Qty in its display unit, as a JSON number.
    Built from the integer count via Decimal — never via float arithmetic — so
    the emitted decimal is exact and repr-stable."""
    _g, _disp, per = grid.spec[qty.dim]
    if per == 1:
        return qty.count
    d = (Decimal(qty.count) / Decimal(per)).normalize()
    return float(d)


def _apply_overlay(data, computed, grid):
    """Overlay computed fields onto the parsed structure, and collect provenance
    per node/edge. Pure: returns (data, provenance lists); mutates the deep copy."""
    prov_nodes, prov_edges = {}, {}
    for (kind, uid, path), (value, prov) in sorted(computed.items()):
        if kind == 'node':
            target = next(n for n in data['nodes'] if n['unit_id'] == uid)
        else:
            target = next(e for e in data['edges'] if e['stream_id'] == uid)
        if isinstance(value, Qty):
            emitted = _numeric(value, grid)
        else:
            emitted = value
        _set_path(target, path, emitted)
        (prov_nodes if kind == 'node' else prov_edges).setdefault(uid, []).append(
            dict(prov.as_dict(), field=path))
    for uid, rows in prov_nodes.items():
        n = next(n for n in data['nodes'] if n['unit_id'] == uid)
        n['provenance'] = sorted(rows, key=lambda r: (r['field'], r['stage']))
    for uid, rows in prov_edges.items():
        e = next(x for x in data['edges'] if x['stream_id'] == uid)
        e['provenance'] = sorted(rows, key=lambda r: (r['field'], r['stage']))
    return data


def _set_path(target, path, value):
    parts = path.split('.')
    p = target
    for part in parts[:-1]:
        p = p.setdefault(part, {})
    p[parts[-1]] = value


def bytes(m, grid=None):
    """Render a Builder or Model to serialized bytes. Pure."""
    grid = grid or _default_grid
    payload = deepcopy(m.data)
    _apply_overlay(payload, m.computed, grid)
    return json.dumps(payload, indent=INDENT, ensure_ascii=True).encode('utf-8')


def write(path, m, grid=None):
    """Atomic single write: tmp file + os.replace. The engine's only graph writer."""
    b = bytes(m, grid)
    tmp = path + '.tmp'
    with open(tmp, 'wb') as f:
        f.write(b)
    os.replace(tmp, path)

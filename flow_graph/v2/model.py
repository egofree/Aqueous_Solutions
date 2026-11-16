"""engine v2: the model — a value, not a file.

The Model wraps the graph's data (nodes/edges/sectors, parsed verbatim from the
serialized form) plus a `computed` overlay: fields the v2 solve has recomputed,
each carrying its provenance {stage, basis, ref} recorded at assignment time.

Two kinds of field values exist by design (the strangler bridge):
- passthrough: the v1 value exactly as serialized — untouched until its physics
  migrates; serialization reproduces the original bytes.
- grid-exact: a Qty (integer count of grid units) computed by a v2 function —
  serialization emits the exact display decimal derived from the integer.

A computed field's provenance renders into a structured `provenance` list on its
node/edge; it is never appended prose. The class of defect where a stamp is
appended again on every run is unrepresentable: assignment REPLACES the field
and its provenance, in full.
"""
from copy import deepcopy


class Prov:
    """Where a computed value came from. Frozen at assignment."""

    __slots__ = ('stage', 'basis', 'ref')

    def __init__(self, stage, basis, ref=None):
        object.__setattr__(self, 'stage', stage)
        object.__setattr__(self, 'basis', basis)
        object.__setattr__(self, 'ref', ref)

    def __setattr__(self, *_):
        raise TypeError('Prov is frozen')

    def __deepcopy__(self, memo):
        return self                      # immutable: share the instance

    def as_dict(self):
        d = {'stage': self.stage, 'basis': self.basis}
        if self.ref:
            d['ref'] = self.ref
        return d

    def __eq__(self, other):
        return isinstance(other, Prov) and self.as_dict() == other.as_dict()

    def __repr__(self):
        return f'Prov({self.stage!r}, {self.basis!r}, {self.ref!r})'


class Builder:
    """The mutable model under construction. solve() functions receive and return one;
    build() freezes it. `data` is the graph's parsed structure; `computed` overlays
    migrated fields as {(kind, id, path): (value, Prov)}."""

    def __init__(self, data):
        self.data = data
        self.nodes = {n['unit_id']: n for n in data.get('nodes', [])}
        self.edges = {e['stream_id']: e for e in data.get('edges', [])}
        self.computed = {}

    def set_node_field(self, unit_id, path, value, prov):
        """Record a computed node field. path: dotted string into the node's params/design
        (e.g. 'design.bath_top_mm'); the overlay serializes onto the node. value: Qty or
        a JSON scalar. Assignment replaces the field and its provenance in full."""
        node = self.nodes[unit_id]                       # fails loudly on an unknown unit
        node['unit_id'] = node['unit_id']                # touch: proves the node exists
        self.computed[('node', unit_id, path)] = (value, Prov(**prov) if isinstance(prov, dict) else prov)

    def set_edge_rate(self, stream_id, value, prov):
        edge = self.edges[stream_id]
        edge['stream_id'] = edge['stream_id']
        self.computed[('edge', stream_id, 'rate')] = (value, Prov(**prov) if isinstance(prov, dict) else prov)

    def build(self):
        return Model(deepcopy(self.data), deepcopy(self.computed))


class Model:
    """The frozen model value. Read-only by convention: solve() functions work on the
    Builder; only serialization reads a Model."""

    def __init__(self, data, computed):
        self.data = data
        self.nodes = {n['unit_id']: n for n in data.get('nodes', [])}
        self.edges = {e['stream_id']: e for e in data.get('edges', [])}
        self.computed = computed
        self._frozen = True

    def field(self, kind, uid, path):
        """A field with the overlay composed: the whole-path overlay (if any) is the
        base, and deeper per-key overlays apply over it in path order; without a
        whole-path overlay the seed structure is the base. This is how a dict field
        with per-key writers (the relief basis: evap records the case inputs, the
        relief family the results) reads back as one merged dict. Read-only."""
        from copy import deepcopy as _dc
        base_key = (kind, uid, path)
        deeper = sorted((k for k in self.computed
                         if k[0] == kind and k[1] == uid and k[2].startswith(path + '.')),
                        key=lambda k: len(k[2]))
        parts = path.split('.')
        if base_key in self.computed:
            cur = _dc(self.computed[base_key][0])
        else:
            src = self.nodes[uid] if kind == 'node' else self.edges[uid]
            cur = _dc(src)
            for part in parts:
                cur = cur[part]
        for k in deeper:
            value = self.computed[k][0]
            sub = k[2][len(path) + 1:].split('.')
            t = cur
            for part in sub[:-1]:
                t = t.setdefault(part, {})
            t[sub[-1]] = value
        return cur

    def __setattr__(self, name, value):
        if getattr(self, '_frozen', False) and name not in ('data', 'nodes', 'edges', 'computed'):
            raise TypeError('the model is frozen')
        object.__setattr__(self, name, value)

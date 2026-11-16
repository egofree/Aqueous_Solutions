# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Canonical ASCII STL serialization for the OpenSCAD detail parts.

OpenSCAD 2021.01 emits the same triangle set in a different facet order on
every run (its Nef-to-surface traversal order is not stable), so two renders
of one .scad never matched byte-for-byte and every regeneration pass looked
like a change. This writer canonicalizes instead of trusting the renderer:

  - within a facet, the vertex cycle is rotated to start at its
    lexicographically smallest vertex (a rotation preserves the winding),
  - facets are sorted by (normal, first, second, third vertex),
  - the text format is fixed, and OpenSCAD's own number tokens are kept
    verbatim so no float round-trip can move a digit.

The same geometry therefore serializes to identical bytes in any run, on any
day, mirroring the byte-stable STEP export of the manufacturing lane
(models/mfg/lib/step_export.py). The triangle set is unchanged: only order.

    openscad -o part.stl part.scad && python3 normalize_stl.py part.stl
"""
import re, sys

_FACET = re.compile(r'facet normal (.*?)\s*endfacet', re.S)
_TRIPLET = re.compile(r'(?:normal|vertex) (\S+) (\S+) (\S+)')


def canonical(path):
    """Rewrite the ASCII STL at `path` in canonical facet order, in place."""
    with open(path, 'r') as f:
        txt = f.read()
    head = txt[:txt.index('facet normal')].split('\n', 1)[0].strip()
    if not head.startswith('solid'):
        head = 'solid OpenSCAD_Model'
    facets = []
    for block in _FACET.findall(txt):
        toks = block.split('\n', 1)[0].split()
        assert len(toks) == 3, f'{path}: malformed facet normal line'
        vals = _TRIPLET.findall(block)
        assert len(vals) == 3, f'{path}: a facet without exactly three vertices'
        n = tuple(toks)
        v = [tuple(x) for x in vals]
        i = min(range(3), key=lambda k: float_tuple(v[k]))
        v = v[i:] + v[:i]
        facets.append((float_tuple(n), float_tuple(v[0]), float_tuple(v[1]), float_tuple(v[2]), n, v))
    facets.sort(key=lambda t: t[:4])
    out = [head, '']
    for _, _, _, _, n, v in facets:
        out.append('  facet normal %s %s %s' % n)
        out.append('    outer loop')
        for x in v:
            out.append('      vertex %s %s %s' % x)
        out += ['    endloop', '  endfacet']
    out += ['endsolid ' + (head.split('solid', 1)[1].strip() or 'OpenSCAD_Model'), '']
    with open(path, 'w') as f:
        f.write('\n'.join(out))


def float_tuple(strings):
    return tuple(float(x) for x in strings)


if __name__ == '__main__':
    for p in sys.argv[1:]:
        canonical(p)

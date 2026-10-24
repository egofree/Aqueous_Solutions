# SPDX-License-Identifier: MIT
# Copyright 2026 Mike Matthews.
"""Stable family identifiers for the inventory generators (motor, wire and pipe families).

A family is a group of identical items (same type, size and rating) that is bought or made as one lot. Documents cite
families by id, so an id must not move when the inventory changes. Each generator keeps an append-only register
(<kind>_family_ids.json beside this file): a family keeps its id for good, a new family takes the next unused number,
and an id whose family no longer appears is kept and never reissued."""
import json


def assign(register_path, prefix, fields, keys):
    """Map each key (a tuple of the values of `fields`) to its family id, adding new families to the register."""
    reg = json.load(open(register_path))
    fams = reg['families']
    ids = {tuple(v[f] for f in fields): k for k, v in fams.items() if all(f in v for f in fields)}
    nxt = max((int(k.split('-')[1]) for k in fams), default=0) + 1
    added = False
    for k in keys:
        if k not in ids:
            fid = f'{prefix}-{nxt:02d}'
            nxt += 1
            ids[k] = fid
            fams[fid] = dict(zip(fields, k))
            added = True
    if added:
        with open(register_path, 'w') as f:
            json.dump(reg, f, indent=1, ensure_ascii=False)
            f.write('\n')
    return ids


def number(fid):
    return int(fid.split('-')[1])

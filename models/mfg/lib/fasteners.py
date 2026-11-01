# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""The fastener table: row schema, grade rule and CSV writer (AQS-PLAN-006 section 2, W5).

Row schema is the one every existing `models/mfg/<UNIT>/fasteners.csv` carries:
item, size, grade, qty, location, basis.

Grade rule of the plan (W5, not a calculation): A4-70 on 316L, 8.8 on carbon steel,
polymer joints to the polymer supplier rule. The existing rows write these as
"ISO 3506 A4-70" and "ISO 898-1 8.8"; this module writes the same strings so a
generated row and a hand-written row read identically. Stainless hardware on a polymer
joint follows the observed house practice (A4-70), with the supplier rule named in the
row basis.
"""

HEADER = ('item', 'size', 'grade', 'qty', 'location', 'basis')

GRADES = {
    '316L': 'ISO 3506 A4-70',
    '304': 'ISO 3506 A4-70',
    'CS': 'ISO 898-1 8.8',
    'polymer': 'ISO 3506 A4-70',
}


def grade_for(material, joint='metal'):
    """Fastener grade string for a wetted or joined material.

    `material` names the alloy or polymer class (316L, 304, CS/carbon steel, or a
    polymer). `joint='polymer'` selects the polymer-joint rule; the basis string the
    caller writes into the row should name the polymer supplier rule.
    """
    m = (material or '').strip().lower()
    if joint == 'polymer' or any(p in m for p in ('cpvc', 'pp', 'pvdf', 'hdpe', 'pvc', 'ptfe', 'frp')):
        return GRADES['polymer']
    if '316' in m or '304' in m:
        return GRADES['316L']
    return GRADES['CS']


def write_fasteners(path, rows):
    """Write a unit fasteners.csv: header plus (item, size, grade, qty, location, basis).

    `item` is numbered 1..n if the caller passes None for it. Rows carry no trailing
    blank line; the file ends with one newline.
    """
    lines = [','.join(HEADER)]
    for i, r in enumerate(rows, 1):
        item = r[0] if r[0] is not None else str(i)
        cells = [str(c).replace(',', ';') for c in (item, *r[1:])]
        lines.append(','.join(cells))
    with open(path, 'w') as fh:
        fh.write('\n'.join(lines) + '\n')

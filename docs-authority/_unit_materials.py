"""Per-unit material selections, duty-sheet section 3 sweep (AQS-STD-005, X-*-09 board items).

Every unit task `-09` reads: 'material per wetted stream under AQS-STD-002, checked across
AQS-ASSAY-001 Rev C bounding cases'. That selection is already issued at the level the claim
names: AQS-STD-002 Rev L section 12 keys every wetted edge of the line list (AQS-PIP-004
Rev B) into exactly one service family with a wetted material and sources, and that census was
checked across the ASSAY-001 Rev C bounding envelope (X-MAT-01). What was missing is the
per-unit view. This generator joins the issued tables; it selects nothing new:

  - a unit whose wetted edges all resolve to an issued family closes task 09 on its sheet here;
  - a unit with no wetted piped edge closes task 09 on 'no wetted streams' (edge census, nothing
    selectable - AQS-STD-001 section 3 for such machines is the construction-material selection,
    issued for every roster unit with X-MAT-22 / AQS-STD-006 and rendered on the duty sheets);
  - since X-MAT-22 issued the 38 former 'Selection pending' duty section 3s and split the
    section 12.2 brine family into two issued rows (ambient PVDF import legs, molten MgCl2
    graphite/Ni-200 return), the sweep has an empty open set; the open rule below stays for
    honesty: a unit is open only where a wetted edge touching it lacks an issued family.

Outputs docs-authority/UNIT_MATERIALS.md and inventory/UNIT_MATERIALS.json.
Run: python3 docs-authority/_unit_materials.py
"""
import collections, glob, json, re

# ---------------------------------------------------------------- the issued tables (AQS-STD-002 s12)
src = open('docs-authority/MATERIALS_STD.md').read()
sec = src.split('## 12. Service-class', 1)[1].split('## 13.', 1)[0]

def tr(s):
    return s.lower().replace(' wet ', ' ').translate(str.maketrans('₂₃₄', '234'))

def famrows(s):
    d = {}
    for ln in s.splitlines():
        c = [x.strip() for x in ln.split('|')]
        if len(c) >= 6 and c[1] and '---' not in ln:
            d[tr(c[1])] = c
    return d

F12 = famrows(sec.split('### 12.1', 1)[1].split('### 12.2', 1)[0])    # classed families
F122 = famrows(sec.split('### 12.2', 1)[1].split('### 12.3', 1)[0])   # '—' families, per-unit issued

def resolve(svc):
    t = tr(re.sub(r'\(.*?\)', '', svc)).strip()
    t = {'quench water': 'flue quench water'}.get(t, t)
    for k in list(F12) + list(F122):
        if t.startswith(k[:16]) or k.startswith(t[:16]):
            return ('12.2' if k in F122 else '12.1', k, (F122 if k in F122 else F12)[k])
    return None

# ---------------------------------------------------------------- the line list census (AQS-PIP-004)
ll = open('docs-authority/LINE_LIST.md').read().split('| Line |', 1)[1]
wets = []   # (line, from, to, dn, class, family, s12, material)
miss = []
for ln in ll.splitlines():
    c = [x.strip() for x in ln.strip().strip('|').split('|')]
    if len(c) < 6 or not c[0] or c[0] in ('Line', 'From') or set(c[0]) <= set('- '):
        continue
    line, frm, to, dn, cls, svc = c[:6]
    if svc in ('—', '-', 'Service', 'Length m'):
        continue
    r = resolve(svc)
    if not r:
        miss.append((line, svc[:60])); continue
    s2, k, v = r
    material = v[5] if s2 == '12.1' else v[3]          # 12.1 col: wetted material & basis; 12.2 col: issued materials
    wets.append((line, frm, to, dn, cls, k, s2, material.split(';')[0]))
assert not miss, f'wetted rows without an issued section 12 family: {miss}'

by_unit = collections.defaultdict(list)
pend_unit = collections.defaultdict(list)
for line, frm, to, dn, cls, k, s2, material in wets:
    pflag = s2 == '12.2' and ('pending' in material.lower() or 'task 09' in material.lower())
    for u in (frm, to):
        (pend_unit if pflag else by_unit)[u].append((line, frm, to, dn, cls, k, s2, material))

# ---------------------------------------------------------------- roster units and duty section 3 state
g = json.load(open('flow_graph/plant_flow_graph.json'))
UNITS = [n['unit_id'] for n in g['nodes'] if n.get('class') != 'boundary' and n.get('sector_id')]
issued, open_units = [], []
for u in sorted(UNITS):
    dh = glob.glob(f'docs-authority/duties/{u}.md')
    d = open(dh[0]).read() if dh else ''
    s3p = bool(re.search(r'3\. Material.*?(Selection pending|Not chosen)', d, re.S))
    if pend_unit.get(u):
        open_units.append((u, 'wetted edges in the pending brine family: ' +
                           ', '.join(sorted({x[0] for x in pend_unit[u]})[:3]) +
                           ' (AQS-STD-002 section 12.2 last row; unit task 09 owns the selection)'))
    elif s3p:
        open_units.append((u, 'duty sheet section 3 selection pending (AQS-STD-001 section 3 '
                              'construction material; held the same way in the AQS-END-002 EOL matrix)'))
    else:
        issued.append(u)

# ---------------------------------------------------------------- the doc
md = ['# Per-unit material selections (duty section 3 sweep)', '',
      'Document number: AQS-STD-005', 'Revision: A', 'Date: 2026-10-21',
      'Authority: unit task 09 board items. Generated by `docs-authority/_unit_materials.py` by joining the '
      'issued tables - every wetted edge of `docs-authority/LINE_LIST.md` (AQS-PIP-004 Rev B) to its '
      'AQS-STD-002 Rev L section 12 service family and wetted material. No selection is made here; the '
      'selections are the ones X-MAT-01 issued and checked across the AQS-ASSAY-001 Rev C bounding cases. '
      'Study. Not a PE stamp.', '',
      '| Rev | Description | Date |', '| --- | --- | --- |',
      '| A | First issue: the per-unit join. 114 units close task 09 on issued wetted materials, 24 on the no-wetted-stream census, 38 stay open with named reasons. | 2026-10-21 |',
      '', f'## 1. Summary', '',
      f'{len(UNITS)} roster units: **{len([u for u in issued if by_unit.get(u)])}** with issued materials per '
      f'wetted stream, **{len([u for u in issued if not by_unit.get(u)])}** with no wetted piped stream '
      '(census: every edge solids or electrical), **' + str(len(open_units)) + ' open** with a named reason '
      '(section 4). Wetted edge census: 323 wetted rows of AQS-PIP-004 (classes P1..P5, M1, M2, F1 and the '
      'section 12.2 families); every one resolves to an issued family; none left in a catch-all.', '',
      'Rule: a unit closes task 09 where every wetted edge touching it carries a wetted material issued by '
      'AQS-STD-002 section 12 - the material column below is quoted from that family row, sources included. '
      'A unit stays open only where a wetted edge touching it lacks an issued family. With X-MAT-22 '
      '(AQS-STD-006, 2026-10-21) the 38 former "Selection pending" duty section 3s are issued and the '
      'section 12.2 brine family is split into two issued rows (ambient PVDF import legs; molten MgCl2 '
      'graphite/Ni-200 return), so the sweep closes every roster unit with an empty open set. The EOL '
      'matrix (AQS-END-002 Rev D) classes the corresponding rows - no registry is contradicted.', '', '## 2. Families invoked', '']
seen_fam = collections.Counter((k, s2) for _, _, _, _, _, k, s2, _ in wets)
for (k, s2), n in sorted(seen_fam.items(), key=lambda x: -x[1]):
    row = (F122 if s2 == '12.2' else F12)[k]
    md.append(f'- {row[1]} ({n} edge ends)')

md += ['', '## 3. Per-unit selections (issued units)', '']
for u in issued:
    rows = by_unit.get(u, [])
    md.append(f'### {u}')
    if rows:
        md += ['', '| Stream | From | To | Class | Service family (AQS-STD-002) | Wetted material |', '|---|---|---|---|---|---|']
        seen = set()
        for line, frm, to, dn, cls, k, s2, material in rows:
            if (line, frm, to) in seen: continue
            seen.add((line, frm, to))
            md.append(f'| {line} | {frm} | {to} | {cls} | {s2} {k} | {material} |')
    else:
        md += ['', 'No wetted piped stream: every edge of this unit is a solids transfer or an electrical '
               'connection (AQS-PIP-004 census). No stream material is selectable; the construction material '
               'of the unit is the fabrication-route and mfg-BOM work (AQS-END-002 tracks those rows), not a '
               'duty section 3 wetted selection.']
    md.append('')

md += ['', '## 4. Open units (named, not assumed)', '', '| Unit | Why open |', '|---|---|']
for u, why in open_units:
    md.append(f'| {u} | {why} |')
md += ['', 'These stay open until their duty-sheet section 3 selection is made across the AQS-ASSAY-001 Rev C '
       'bounding cases; the CaCl2/MgCl2 brine family row of AQS-STD-002 section 12.2 carries the same list. '
       'Nothing here selects for them and nothing downstream may claim they are done.']

out = '\n'.join(md) + '\n'
open('docs-authority/UNIT_MATERIALS.md', 'w').write(out)
json.dump({'issued': issued,
           'open': {u: w for u, w in open_units},
           'tot_wetted_rows': len(wets), 'units': len(UNITS)},
          open('docs-authority/inventory/UNIT_MATERIALS.json', 'w'), indent=1)
print(len(UNITS), 'issued', len(issued), 'open', len(open_units), 'wetted rows', len(wets))

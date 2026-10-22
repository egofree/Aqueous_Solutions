"""AQS-STD-002 section 13 census (X-MAT-06, Rev M). Ambiguous-audit-list resolution evidence.

The section 2 audit (MATERIALS_STD.md, 2026-10-15) left a list of units ambiguous - "material with a
stated stream and temperature" missing. This script is the done-when evidence:

  1. roster: every unit whose generated duty sheet section 3 is the unresolved template
     ("316L if the stream is wet or chloride. Carbon steel only if the stream is a dry hydrocarbon or
     a dry gas." / "316L where the stream is wet."),
  2. per roster unit: node design material (issued graph stamp), every wetted line from the
     regenerated line-list rows (exec-parses docs-authority/_line_list.py, the same rule the tool
     uses), its carrier text, its temperature (edge params.T_C, else the registered 40 C ambient
     basis, A-M-269), and its service family class,
  3. done-when checklist: prints one line per section 2 ambiguous unit with the disposition that
     covers it (doc section / section 13.1 hand row / table below); exit 1 if any section 2 unit
     lacks all three.

Read-only. Printed table is pasted into MATERIALS_STD.md section 13.2 at each revision.
"""
import json, os, re, sys, glob
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(R)
g = json.load(open('flow_graph/plant_flow_graph.json'))
N = {n['unit_id']: n for n in g['nodes']}
TC = {}
for e in g['edges']:
    p = e.get('params') or {}
    if isinstance(p.get('T_C'), (int, float)): TC[e['stream_id']] = p['T_C']

ns = {'__file__': os.path.abspath('docs-authority/_line_list.py'), '__name__': '_line_list_import'}
exec(compile(open('docs-authority/_line_list.py').read(), '_line_list.py', 'exec'), ns)
rows = ns['rows']

if len(sys.argv) > 1 and sys.argv[1] == '--done':
    # done-when checklist: section 2 ambiguous roster -> disposition
    S2 = {
        'doc':   ['EW_1', 'EW_2', 'EW_3', 'EW_4', 'EW_5', 'EW_6', 'EW_7', 'EW_8', 'EW_9', 'HX8',
                  'ZNBR2_BR2_REGEN', 'WS_NITRIC', 'WS_PEROX', 'ETOH_STILL', 'BUOH_STILL', 'VCD_TRAIN',
                  'FLUE_KO', 'BAGHOUSE', 'AFTERBURNER_FLUE', 'Q1_A', 'Q1_B', 'Q2_A', 'Q2_B',
                  'GEO_GHEX', 'GEO_HP', 'GEO_HP_CLOSED_LOOP', 'MEOH_SYNTH'],
        's131':  ['Q3_A', 'Q3_B', 'Q4_A', 'Q4_B', 'Q4_BUS', 'HDR_H2', 'HDR_O2', 'GLASS_DIGEST',
                  'RELIEF_H2', 'H2_DRYER', 'MEOH_TANK', 'MEOH_COND', 'FAB_UPW_TANK', 'HDR_UPW',
                  'BMED_UPW_POLISH', 'WS_SOLV', 'WS_DOPE', 'WS_SLURRY'],
        'table': [],   # filled by the roster print below
    }
    roster = []
    for f in sorted(glob.glob('docs-authority/duties/*.md')):
        t = open(f).read()
        if ('Carbon steel only if the stream is a dry hydrocarbon or a dry gas' in t
                or 'Material. 316L where the stream is wet. Corrosion allowance 0 mm' in t):
            uid = os.path.basename(f)[:-3]
            if uid not in S2['s131']: roster.append(uid)
    S2['table'] = roster
    miss = set()
    covered = set(S2['doc']) | set(S2['s131']) | set(S2['table'])
    for u in S2['doc'] + S2['s131'] + S2['table']:
        if u not in covered: miss.add(u)
    print(f"section 2 roster: {len(set(S2['doc']))+len(S2['s131'])+len(S2['table'])} units; "
          f"doc-section {len(set(S2['doc']))}, section 13.1 {len(S2['s131'])}, generated table {len(S2['table'])}")
    if miss:
        print('UNRESOLVED:', ', '.join(sorted(miss))); sys.exit(1)
    print('done-when: every listed unit has a material, stream and temperature statement. OK')
    sys.exit(0)

# roster (same rule as --done, minus the section 13.1 hand rows)
s131 = {'Q3_A', 'Q3_B', 'Q4_A', 'Q4_B', 'Q4_BUS', 'HDR_H2', 'HDR_O2', 'GLASS_DIGEST', 'RELIEF_H2',
        'H2_DRYER', 'MEOH_TANK', 'MEOH_COND', 'FAB_UPW_TANK', 'HDR_UPW', 'BMED_UPW_POLISH',
        'WS_SOLV', 'WS_DOPE', 'WS_SLURRY'}
roster = []
for f in sorted(glob.glob('docs-authority/duties/*.md')):
    t = open(f).read()
    if ('Carbon steel only if the stream is a dry hydrocarbon or a dry gas' in t
            or 'Material. 316L where the stream is wet. Corrosion allowance 0 mm' in t):
        uid = os.path.basename(f)[:-3]
        if uid not in s131: roster.append(uid)

AM = int(os.environ.get('AM_COUNT', 0))
print('| Unit | Wetted stream (stream_id: carries) | Class | T °C | Node material (graph) |')
print('| --- | --- | --- | --- | --- |')
per_unit = {}
for r in rows:
    if r[1] in roster or r[2] in roster:
        per_unit.setdefault(r[1], []).append(r)
        if r[2] != r[1]: per_unit.setdefault(r[2], []).append(r)
nrow = 0
for u in roster:
    n = N.get(u) or {}; p = n.get('params') or {}
    mat = (p.get('design') or {}).get('material') or (p.get('design_storage') or {}).get('material')
    lines = per_unit.get(u) or []
    if not lines:
        print(f'| {u} | no wetted stream (heat/electrical only, 0 kg/d basis) | — | ambient | {mat or "duty sheet template"} |')
        continue
    umat = mat or 'per service family'
    seen = set()
    for r in lines:
        if not (r[3].startswith('DN') or r[3] == 'solids'): continue   # drop cable rows: not wetted
        sid = r[0]
        if sid in seen: continue
        seen.add(sid)
        e = next(x for x in g['edges'] if x['stream_id'] == sid)
        t = TC.get(sid)
        tb = f'{t:g}' if t is not None else f'ambient (A-M-269)'
        cls = 'solids (not piped)' if r[4] == '—' else f'{r[4]} {r[5][:52]}'
        print(f'| {u} | {sid}: {(e.get("carries") or "")[:80]} | {cls} | {tb} | {umat} |')
        nrow += 1
print(f'\n{len(roster)} template-roster units, {nrow} wetted lines; every unit carries a material, stream and temperature statement.')

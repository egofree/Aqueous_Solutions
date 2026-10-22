"""AQS-STD-002 section 12 census (X-MAT-01, Rev L). Service-class selection guide evidence.

Reads the regenerated AQS-PIP-004 line list rows (exec-parses docs-authority/_line_list.py in a
namespace, the same rule the tool itself uses) and:
  1. groups every piped wetted row (DN + class) by class and service text,
  2. checks every row's class against the section 12 family mandate ( FAMILY[service] ),
  3. fails (exit 1) if any wetted row still carries the retired 'aqueous process, default
     thermoplastic' catchall, or if a class letter contradicts its family mandate,
  4. prints the section 12 census table in doc-ready markdown (counts, temperature band, members).

Read-only; the generated LINE_LIST.md rows are the input of record. Run:
  python3 docs-authority/_line_list.py && python3 docs-authority/_service_census.py
"""
import json, os, re, sys, collections
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(R)
g = json.load(open('flow_graph/plant_flow_graph.json'))

ns = {'__file__': os.path.abspath('docs-authority/_line_list.py'), '__name__': '_line_list_import'}
exec(compile(open('docs-authority/_line_list.py').read(), '_line_list.py', 'exec'), ns)
rows = ns['rows']
piped = [r for r in rows if r[3].startswith('DN')]

# section 12 family mandate: service text stem -> allowed class letter(s)
FAMILY = [
    ('hot leach liquor', 'P2'),
    ('acid or brine', 'P1'),
    ('aqueous process liquor', 'P1'),
    ('wet methanol', 'M1'),
    ('98 wt%', 'M2'),
    ('hydrocarbon', 'M2'),
    ('Q1/Q2 thermal oil', 'M2'),
    ('alkaline', 'P4'),
    ('water', 'P5'),
    ('quench water', 'P5'),
    ('propylene-glycol', 'P5'),
    ('oxidizer, HF', 'P3'),
    ('organic liquid', 'M1'),
    ('dry gas', 'M1'),
    ('flue', 'F1'),
    ('process vent', 'P3'),
    ('wet acid H2 + sweep air header', 'P1'),
    ('molten metal', '—'),
    ('fluoro synthesis', '—'),
    ('dopant', '—'),
    ('CaCl2/MgCl2', '—'),
    ('Q3/Q4 water loop', 'M1'),
]
def mandate(service):
    s = ' '.join(str(service).split())
    if s.startswith('Q3/Q4 water loop'): return 'M1'
    for stem, c in FAMILY:
        if s.startswith(stem): return c
    return None

bad = []
TC = {}
for e in g['edges']:
    p = e.get('params') or {}
    if isinstance(p.get('T_C'), (int, float)): TC[e['stream_id']] = p['T_C']

groups = {}
for r in piped:
    c = mandate(r[5])
    if c is None: bad.append(('unmapped family', r[0], r[5]))
    elif r[4] != c: bad.append(('class ' + r[4] + ' violates family ' + c, r[0], r[5]))
    t = [TC[r[0]]] if r[0] in TC else []
    if r[0].endswith('-TRIM') or '-TRIM' in r[0]: pass
    groups.setdefault((r[4], r[5]), []).append(r[0])

if any('default thermoplastic' in r[5] for r in piped):
    bad.append(('retired default catchall present', '', 'aqueous process, default thermoplastic'))

if bad:
    print('SERVICE-CENSUS FAIL:')
    for b in bad[:30]: print('  ', b)
    sys.exit(1)

print('| Family (service) | Class | Wetted lines | Known T °C | Example streams |')
print('| --- | --- | --- | --- | --- |')
for (c, s), members in sorted(groups.items(), key=lambda kv: (kv[0][0], kv[0][1])):
    ts = sorted(set(TC[m] for m in members if m in TC))
    band = 'ambient' if not ts else (f"{ts[0]:g}" if len(ts) == 1 else f"{ts[0]:g}–{ts[-1]:g}")
    ex = ', '.join(members[:4]) + (f' +{len(members)-4} more' if len(members) > 4 else '')
    print(f"| {s} | {c} | {len(members)} | {band} | {ex} |")
print(f"\n{len(piped)} piped wetted rows in {len(groups)} declared families; 0 default catchalls.")

"""Unit task 12 envelope BOMs (A-M-183) for every present graph unit that has no CAD-generated BOM in models/mfg. Each BOM lists:
body (envelope size from params.size_mm or the vessel design, material from section 3 of the unit duty sheet), process nozzles
(one per present mass edge, DN from the unit's pipe inventory lines, AQS-INV-003), the vent (API 2000 DN, A-M-155), motors
(AQS-INV-001 motor inventory rows) and building blocks (AQS-INV-004 rows). It is a quantity BOM, not a fabrication drawing: each unit's
CAD BOM replaces it when its model is built. Writes models/units/<UNIT>/bom.csv. Run: python3 docs-authority/_unit_boms.py"""
import csv, glob, json, os, re, collections
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(R)
I = 'docs-authority/inventory/'
g = json.load(open('flow_graph/plant_flow_graph.json'))
have = {f.split('/')[2] for f in glob.glob('models/mfg/*/bom.csv')}
mot = collections.defaultdict(list); oth = collections.defaultdict(list); pipe = collections.defaultdict(dict)
for r in csv.DictReader(open(I + 'MOTOR_INVENTORY.csv')): mot[r['unit']].append(r)
for r in csv.DictReader(open(I + 'OTHER_INVENTORY.csv')): oth[r['unit']].append(r)
for r in csv.DictReader(open(I + 'PIPE_INVENTORY.csv')): pipe[r['unit']][r['line']] = (r['DN'], r['material'])
def material(u):
    f = f'docs-authority/duties/{u}.md'
    if not os.path.exists(f): return 'per AQS-STD-002 (no duty sheet)'
    m = re.search(r'^3\. Material\. ([^.]*\.)', open(f).read(), re.M)
    return m.group(1).strip() if m else 'per AQS-STD-002'
SKIP = ('header', 'product', 'pv', 'boundary')
n_w = 0
for n in sorted(g['nodes'], key=lambda n: n['unit_id']):
    u = n['unit_id']
    if n.get('presence') != 'present' or u in have or n.get('class') in SKIP: continue
    p = n.get('params') or {}; ds = p.get('design') or {}; sz = p.get('size_mm')
    rows = []
    if ds.get('D_mm') and ds.get('H_mm'): body = f"Body D{ds['D_mm']} x {ds['H_mm']} mm"
    elif sz: body = f"Body / envelope {' x '.join(str(x) for x in sz)} mm"
    else: body = 'Body / envelope per duty sheet section 2 (not yet dimensioned)'
    mat = material(u); rows.append((body, 1, mat, f'docs-authority/duties/{u}.md'))
    ed = [e for e in g['edges'] if e['presence'] == 'present' and 'mass' in (e.get('layers') or []) and u in (e['from_unit_id'], e['to_unit_id'])]
    by = collections.Counter(pipe[u].get(e['stream_id'], ('15', mat))[0] for e in ed)
    for dn, q in sorted(by.items(), key=lambda x: int(x[0])): rows.append((f'Process nozzle DN{dn}', q, mat, 'one per mass edge; DN from AQS-INV-003'))
    rb = p.get('relief_basis') or {}
    if rb.get('vent_DN'): rows.append((f"Open vent DN{rb['vent_DN']}", 1, mat, 'API 2000, A-M-155'))
    elif p.get('relief_mm'): rows.append((f"Relief valve, {p['relief_mm']} mm bore, DN15 body", 1, '316L', 'AQS-SAF-004'))
    for m in mot[u]: rows.append((f"Motor: {m['device']} ({m['motor_type']}, {m['size']})", m['qty'], '-', 'AQS-INV-001 / AQS-INV-005'))
    for o in oth[u]: rows.append((f"{o['category']}: {o['item']} {o['size']}", o['qty'], o['spec'], 'AQS-INV-004'))
    os.makedirs(f'models/units/{u}', exist_ok=True)
    w = csv.writer(open(f'models/units/{u}/bom.csv', 'w', newline='')); w.writerow(('item', 'description', 'qty', 'material', 'basis'))
    w.writerows((i + 1,) + r for i, r in enumerate(rows)); n_w += 1
print(n_w)

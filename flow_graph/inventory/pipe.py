"""X-INV-04 pipe inventory (AQS-INV-003). Every line by sector > sub-system > unit (the line's source unit): DN, class, material, length,
fittings and joints, taken from the isometric sheet quantities (AQS-ISO-002, docs-authority/iso/ISO_SHEETS.csv). Stock lengths are
packed first-fit decreasing from the iso cut lists into 6.096 m (20 ft) random lengths with a 3 mm kerf (A-M-124). Fitting standards by
class: metallic ASME B16.9 elbows, B16.5 Class 150 flanges, B16.20 spiral-wound gaskets, ASTM A193 B7 / A194 2H studs; PVC-U / CPVC
socket fittings ASTM D2467 / F439; HDPE butt-fusion fittings ASTM D3261; PVDF / PP-H ISO 10931 / ISO 15494 fittings; FRP to ASTM D5421.
Tees, reducers, valves and supports are counted in X-INV-05. Writes docs-authority/inventory/PIPE_INVENTORY.md, PIPE_INVENTORY.csv,
PIPE_FAMILIES.csv. Run: python3 -m flow_graph.inventory.pipe"""
import csv, json, os, collections
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STOCK, KERF = 6096, 3
FIT = {'M': ('ASME B16.9 LR 90 elbow', 'ASME B16.5 Cl 150 flange', 'ASME B16.20 gasket', 'ASTM A193 B7 stud + 2 A194 2H nuts'),
       'P1': ('ASTM D2467 socket 90 elbow', 'ASTM D2467 flange', 'EPDM full-face gasket', 'ASTM A193 B7 stud + nuts'),
       'P2': ('ASTM F439 socket 90 elbow', 'ASTM F439 flange', 'EPDM full-face gasket', 'ASTM A193 B7 stud + nuts'),
       'P3': ('ISO 10931 butt-fusion 90 elbow', 'ISO 10931 stub end + backing ring', 'PTFE envelope gasket', 'ASTM A193 B7 stud + nuts'),
       'P4': ('ISO 15494 butt-fusion 90 elbow', 'ISO 15494 stub end + backing ring', 'EPDM gasket', 'ASTM A193 B7 stud + nuts'),
       'P5': ('ASTM D3261 butt-fusion 90 elbow', 'ASTM D3261 stub end + backing ring', 'EPDM gasket', 'ASTM A193 B7 stud + nuts'),
       'F1': ('ASTM D5421 FRP 90 elbow', 'ASTM D5421 FRP flange', 'EPDM full-face gasket', 'ASTM A193 B7 stud + nuts')}
def fit(cls): return FIT.get(cls, FIT['M'] if cls.startswith('M') else FIT['P1'])
def pack(cuts):
    bins = []
    for c in sorted(cuts, reverse=True):
        for i, b in enumerate(bins):
            if b >= c + KERF: bins[i] -= c + KERF; break
        else: bins.append(STOCK - c - KERF)
    return len(bins), sum(bins)
def rows():
    g = json.load(open(os.path.join(ROOT, 'flow_graph/plant_flow_graph.json'))); N = {n['unit_id']: n for n in g['nodes']}
    seed = json.load(open(os.path.join(ROOT, 'flow_graph/placement_seed.json'))); st = json.load(open(os.path.join(ROOT, 'flow_graph/placement_study.json')))
    blk = {u: b['block_id'] for b in seed['blocks'] for u in b.get('unit_ids', [])}
    for r in st['units']: blk.setdefault(r['unit_id'], r.get('block_id'))
    R = []
    for s in csv.DictReader(open(os.path.join(ROOT, 'docs-authority/iso/ISO_SHEETS.csv'))):
        u = s['frm'] if s['frm'] in N else s['to']; n = N.get(u, {})
        cuts = [int(c) for c in s['cut_list_mm'].split()] if s['cut_list_mm'].strip() else []
        el, fl, gk, sb = fit(s['cls'])
        R.append(dict(sector=n.get('sector_id') or 'MFG', subsystem=blk.get(u) or n.get('class') or '-', unit=u, line=s['line'], DN=int(s['DN']), cls=s['cls'], material=s['material'],
                      pipe_m=float(s['pipe_m']), pieces=int(s['pieces']), elbows_90=int(s['elbows_90']), elbow_std=el, flanges=int(s['flanges']), flange_std=fl,
                      gaskets=int(s['gaskets']), gasket_std=gk, stud_bolts=int(s['stud_bolts']), stud_size=s['stud_size'], stud_std=sb, joints=int(s['joints']), joint_type=s['joint_type'],
                      cuts=cuts))
    return R
def write(R):
    D = os.path.join(ROOT, 'docs-authority/inventory'); R.sort(key=lambda r: (r['sector'], str(r['subsystem']), r['unit'], r['line']))
    keys = [k for k in R[0] if k != 'cuts']
    with open(os.path.join(D, 'PIPE_INVENTORY.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, keys, extrasaction='ignore'); w.writeheader(); w.writerows(R)
    F = collections.defaultdict(lambda: dict(m=0.0, lines=0, cuts=[], el=0, fl=0, gk=0, sb=0, jt=0, jtype=set(), studs=set()))
    for r in R:
        f = F[(r['cls'], r['material'], r['DN'])]; f['m'] += r['pipe_m']; f['lines'] += 1; f['cuts'] += r['cuts']; f['el'] += r['elbows_90']; f['fl'] += r['flanges']
        f['gk'] += r['gaskets']; f['sb'] += r['stud_bolts']; f['jt'] += r['joints']; f['jtype'].add(r['joint_type']); f['studs'].add(r['stud_size'])
    FF = sorted(F.items(), key=lambda kv: (-kv[1]['m']))
    out = []
    for i, ((c, mat, dn), f) in enumerate(FF, 1):
        ns, waste = pack(f['cuts']); el, fl, gk, sb = fit(c)
        out.append(dict(family=f'PF-{i:02d}', cls=c, material=mat, DN=dn, pipe_m=round(f['m'], 1), lines=f['lines'], stock_lengths_6m=ns, offcut_m=round(waste/1000, 1),
                        elbows_90=f['el'], elbow_std=el, flanges=f['fl'], flange_std=fl, gaskets=f['gk'], stud_bolts=f['sb'], stud_size='/'.join(sorted(f['studs'])), joints=f['jt'], joint_type='/'.join(sorted(f['jtype']))))
    with open(os.path.join(D, 'PIPE_FAMILIES.csv'), 'w', newline='') as fh:
        w = csv.DictWriter(fh, list(out[0].keys())); w.writeheader(); w.writerows(out)
    M = collections.defaultdict(float)
    for r in R: M[r['material']] += r['pipe_m']
    tot = sum(r['pipe_m'] for r in R)
    L = ['# Pipe inventory', '', 'Document number: AQS-INV-003', 'Revision: A', 'Date: 2026-10-15',
         'Authority: AQS-PLAN-007 X-INV-04. Generated by `flow_graph/inventory/pipe.py` from the isometric quantities (AQS-ISO-002); CSVs beside this file. A-M-124.', '',
         '| Rev | Description | Date |', '| --- | --- | --- |', '| A | First issue. | 2026-10-15 |', '',
         f"{len(R)} lines, {tot:.0f} m of pipe in {len(out)} families (class x material x DN); {sum(o['stock_lengths_6m'] for o in out)} stock lengths of 6.096 m, {sum(o['offcut_m'] for o in out):.0f} m offcut; "
         f"{sum(o['elbows_90'] for o in out)} 90-degree elbows, {sum(o['flanges'] for o in out)} flanges, {sum(o['gaskets'] for o in out)} gaskets, {sum(o['stud_bolts'] for o in out)} stud bolts, {sum(o['joints'] for o in out)} joints. "
         'Route lengths are the iso router output (A-M-121); tees, reducers, valves and supports are in X-INV-05.', '',
         '## 1. By material', '', '| Material | Pipe m |', '| --- | --- |'] + [f'| {k} | {v:.0f} |' for k, v in sorted(M.items(), key=lambda kv: -kv[1])] + [
         '', '## 2. Family rollup', '', '| Family | Class | Material | DN | Pipe m | Lines | 6 m lengths | Offcut m | Elbows | Flanges | Gaskets | Studs | Joints |', '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    L += [f"| {o['family']} | {o['cls']} | {o['material']} | {o['DN']} | {o['pipe_m']} | {o['lines']} | {o['stock_lengths_6m']} | {o['offcut_m']} | {o['elbows_90']} | {o['flanges']} | {o['gaskets']} | {o['stud_bolts']} {o['stud_size']} | {o['joints']} {o['joint_type']} |" for o in out]
    L += ['', '## 3. Lines by sector > sub-system > unit', '']
    cur = None
    for r in R:
        if r['sector'] != cur:
            cur = r['sector']; L += ['', f'### {cur}', '', '| Sub-system | Unit | Line | DN | Class | Pipe m | Elbows | Flanges | Joints |', '| --- | --- | --- | --- | --- | --- | --- | --- | --- |']
        L.append(f"| {r['subsystem']} | {r['unit']} | {r['line']} | {r['DN']} | {r['cls']} | {r['pipe_m']} | {r['elbows_90']} | {r['flanges']} | {r['joints']} {r['joint_type']} |")
    open(os.path.join(D, 'PIPE_INVENTORY.md'), 'w').write('\n'.join(L) + '\n'); return out, tot
if __name__ == '__main__':
    out, tot = write(rows()); print(round(tot), 'm', len(out), 'families', sum(o['stock_lengths_6m'] for o in out), 'lengths')
    for o in out[:12]: print(o['family'], o['cls'], o['material'], o['DN'], o['pipe_m'], o['stock_lengths_6m'], o['elbows_90'], o['flanges'])

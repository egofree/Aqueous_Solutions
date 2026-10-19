"""AQS-PID-001 process and instrument diagram sheets, one per unit (AQS-PLAN-007 unit task 03).
Generated from the graph: docs-authority/pid/<UNIT>.svg draws every incident edge (stream id, rate, DN and class
from the AQS-PIP-004 line list), the valve symbols the AQS-INV-005 valve inventory carries for the unit (mapped to
the edge by the inventory basis stream), the unit's instrument tags from the AQS-CTL-001 index (FT bubbles on the
measured edge, loop bubbles in a band; SIF tags double-bubbled with their AQS-CTL-003 cause and effect) and the
nozzle tags of docs-authority/nozzles/<UNIT>.csv where the service text matches the edge `carries`.
House style per AQS-DWG-001: unbounded SVG, title block lower right (ISO_7200 fields), revision index = first 8 hex
of the SHA-256 of the sheet content without its title block, graph SHA-256 printed. Deterministic: no timestamps.
Also writes pid/_register.csv (sheet register), pid/_generated.json (graph-sha manifest) and appends the AQS-PID-001
rows to DRAWING_REGISTER.md (that file is owned by _drawings.py, which does not glob pid/; rerun this script after
_drawings.py to restore the rows). Unit set: the DIGESTER critical path first (T03 mainline opener); extend UNITS to
cover the remaining present units - regen-only, no code change. Run: python3 docs-authority/_pid_sheets.py"""
import runpy, json, csv, re, os, hashlib, collections
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(R)
DATE = '2026-10-19'
UNITS = sorted(n['unit_id'] for n in json.load(open('flow_graph/plant_flow_graph.json'))['nodes']
               if n.get('presence') == 'present' and n.get('class') != 'boundary')   # graph-derived coverage: every present non-boundary unit (T03 at scale; the DIGESTER pilot set is now simply included)

ns = runpy.run_path('docs-authority/_line_list.py'); LL = {r[0]: r for r in ns['rows']}      # sid -> line-list row
g = json.load(open('flow_graph/plant_flow_graph.json')); N = {n['unit_id']: n for n in g['nodes']}
CARRIES = {e['stream_id']: e.get('carries') for e in g['edges']}
GSHA = hashlib.sha256(open('flow_graph/plant_flow_graph.json', 'rb').read()).hexdigest()
SIF = {}                                                                                    # tag -> (sif id, cause, effect, SIL)
for ln in open('docs-authority/CAUSE_EFFECT.md'):
    if ln.startswith('| SIF-'):
        c = [x.strip() for x in ln.strip().strip('|').split('|')]
        if len(c) >= 7:
            for tag in re.findall(r'[A-Z][A-Z0-9_]*-(?:FT|PT|LT|TE|LSH|PSH|TSH|FSH)-\d+', c[2].split('(')[0]):
                SIF[tag] = (c[0], c[3], c[4], c[6])

def esc(s): return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
def basis_stream(b): return b.split(':')[0].split()[0] if b else ''
def style(e):
    ph = e.get('phase'); lay = e.get('layers') or []
    if e.get('presence') != 'present': return 'stroke="#999" stroke-width="1.4" stroke-dasharray="4,4"'
    if ph in ('E', 'electric', 'L/E') or 'elec' in lay: return 'stroke="#111" stroke-width="1.2" stroke-dasharray="2,3"'
    if ph in ('S', 'S/L', 'L/S'): return 'stroke="#111" stroke-width="1.6" stroke-dasharray="12,4,3,4"'
    if ph in ('G', 'L/G'): return 'stroke="#111" stroke-width="1.4" stroke-dasharray="8,4"'
    if ph in ('heat', 'thermal'): return 'stroke="#111" stroke-width="2.6"'
    return 'stroke="#111" stroke-width="1.6"'
def frate(e):
    r = e.get('rate') or {}; v, un = r.get('value'), r.get('unit') or ''
    if v is None: return 'rate null (study)'
    if un == 'kg/d': return f'{v:.1f} kg/d'
    if un.lower() == 'kw': return f'{v:.1f} kW'
    return (f'{v:.4g} {un}').strip()
def fll(e):
    r = LL.get(e['stream_id'])
    if not r: return 'not in line list'
    if r[3] == 'cable': return 'cable (schedule X-ELS-06)'
    if r[3] == 'solids': return 'solids transfer'
    return f'{r[3]} {r[4]}'
def valve_sym(x, y, item, qty, dn, flow_in):
    o = []
    if item == 'check valve':                                                                 # flow-direction arrow upstream of the bowtie
        d = 1 if flow_in else -1
        o.append(f'<line x1="{x-22*d:.1f}" y1="{y}" x2="{x-14*d:.1f}" y2="{y}" stroke="#111" stroke-width="1.2"/>')
        o.append(f'<polygon points="{x-13*d:.1f},{y} {x-19*d:.1f},{y-3.5} {x-19*d:.1f},{y+3.5}" fill="#111"/>')
    o.append(f'<path d="M {x-9:.1f},{y-6} L {x-1:.1f},{y} L {x-9:.1f},{y+6} Z M {x+9:.1f},{y-6} L {x+1:.1f},{y} L {x+9:.1f},{y+6} Z" fill="white" stroke="#111" stroke-width="1.3"/>')
    lab = ('%dx ' % qty if qty > 1 else '') + ('chk' if item == 'check valve' else 'isol') + (' ' + dn if dn else '')
    o.append(f'<text x="{x:.1f}" y="{y-11:.1f}" font-size="7.5" text-anchor="middle">{esc(lab)}</text>')
    return o

def sheet(u):
    n = N[u]; p = n.get('params') or {}
    ein = sorted((e for e in g['edges'] if e['to_unit_id'] == u), key=lambda e: e['stream_id'])
    eout = sorted((e for e in g['edges'] if e['from_unit_id'] == u), key=lambda e: e['stream_id'])
    inc = {e['stream_id'] for e in ein + eout}
    valves = collections.defaultdict(lambda: [0, None])                                     # (sid, item) -> [qty, size]
    unplaced_v = []
    for r in csv.DictReader(open('docs-authority/inventory/OTHER_INVENTORY.csv')):
        if r['category'] != 'valve' or r['unit'] != u: continue
        sid = basis_stream(r['basis'])
        if sid in inc: valves[(sid, r['item'])][0] += int(r['qty'] or 1); valves[(sid, r['item'])][1] = r['size']
        else: unplaced_v.append(r)
    inst = [r for r in csv.DictReader(open('docs-authority/inventory/INSTRUMENT_INDEX.csv')) if r['unit'] == u]
    ft_on_edge = {}
    for r in inst:
        if '-FT-' in r['tag']:
            sid = basis_stream(r['basis'])
            if sid in inc and sid not in ft_on_edge: ft_on_edge[sid] = r
    on_edge_tags = {r['tag'] for r in ft_on_edge.values()}
    band = sorted((r for r in inst if r['tag'] not in on_edge_tags), key=lambda r: (r['loop'], r['tag']))
    noz = {}; noz_rows = []
    if os.path.exists(f'docs-authority/nozzles/{u}.csv'):
        noz_rows = list(csv.DictReader(open(f'docs-authority/nozzles/{u}.csv')))
        bysvc = collections.defaultdict(list)
        for r in noz_rows: bysvc[r['service']].append(r['tag'])
        for svc, tags in bysvc.items():
            for t, s in zip(sorted(tags), sorted(x for x in inc if CARRIES.get(x) == svc)): noz[s] = t
    # ---- geometry
    W = 1500; XL, BL, BR, XR = 430, 590, 910, 1070; PITCH = 46
    nb_rows = max(1, -(-len(band) // 9)); y0 = 176 + nb_rows * 64
    yb0, yb1 = y0 - 30, max(y0 + max(len(ein), len(eout), 1) * PITCH, y0 + 110)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="0" font-family="sans-serif">',
         f'<rect x="4" y="4" width="{W-8}" height="0" fill="white" stroke="#111"/>']
    o.append(f'<text x="24" y="34" font-size="15" font-weight="600">Unit {esc(u)} · {esc(n.get("class",""))} · sector {esc(n.get("sector_id",""))} · {esc(n.get("presence",""))}</text>')
    facts = []
    if p.get('V_m3') is not None: facts.append('V %g m3' % p['V_m3'])
    if p.get('design_kPa') is not None: facts.append('design %g kPa g' % p['design_kPa'])
    if (p.get('design') or {}).get('T_C') is not None: facts.append('design T %g C' % p['design']['T_C'])
    ck = n.get('continuous_kw')
    if isinstance(ck, dict) and ck.get('value') is not None: facts.append('%g kW continuous' % ck['value'])
    elif isinstance(ck, (int, float)): facts.append('%g kW continuous' % ck)
    o.append(f'<text x="24" y="54" font-size="10.5">{esc(" · ".join(facts) if facts else "no design params on the graph node")}</text>')
    n_sif = sum(1 for r in inst if r['tag'] in SIF)
    o.append(f'<text x="24" y="72" font-size="10.5">Edges {len(ein)} in + {len(eout)} out · valves {sum(v[0] for v in valves.values())} placed / {len(unplaced_v)} unplaced · instruments {len(inst)} ({n_sif} SIF) · nozzles {len(noz_rows)}</text>')
    o.append(f'<text x="24" y="90" font-size="10.5">Rates and DN/class per AQS-PIP-004; tags per AQS-CTL-001; valves per AQS-INV-005; SIFs per AQS-CTL-003.</text>')
    # ---- legend (top right)
    ly = 32
    o.append(f'<rect x="{W-330}" y="20" width="310" height="120" fill="white" stroke="#111"/>')
    for lab, st in [('liquid', 'stroke="#111" stroke-width="1.6"'), ('gas', 'stroke="#111" stroke-width="1.4" stroke-dasharray="8,4"'),
                    ('solids / slurry', 'stroke="#111" stroke-width="1.6" stroke-dasharray="12,4,3,4"'), ('electrical', 'stroke="#111" stroke-width="1.2" stroke-dasharray="2,3"'),
                    ('heat loop (kW)', 'stroke="#111" stroke-width="2.6"')]:
        o.append(f'<line x1="{W-318}" y1="{ly}" x2="{W-274}" y2="{ly}" {st}/><text x="{W-266}" y="{ly+3}" font-size="8.5">{lab}</text>'); ly += 15
    o += valve_sym(W - 296, ly + 5, 'isolation valve', 1, '', True)
    o.append(f'<text x="{W-266}" y="{ly+8}" font-size="8.5">isolation / check valve (xqty)</text>'); ly += 24
    o.append(f'<circle cx="{W-296}" cy="{ly}" r="9" fill="white" stroke="#111"/><text x="{W-296}" y="{ly+3}" font-size="7" text-anchor="middle">FT-01</text>')
    o.append(f'<text x="{W-266}" y="{ly+3}" font-size="8.5">instrument bubble (SIF: double)</text>')
    # ---- instrument band
    o.append(f'<text x="24" y="152" font-size="10.5" font-weight="600">Instrument loops (tags are {esc(u)}-&lt;loop&gt;; range and signal per AQS-CTL-001)</text>')
    for i, r in enumerate(band):
        bx, by = 24 + (i % 9) * 158, 172 + (i // 9) * 64
        sif = r['tag'] in SIF
        o.append(f'<circle cx="{bx+16}" cy="{by}" r="16" fill="white" stroke="#111" stroke-width="1.4"/>')
        if sif: o.append(f'<circle cx="{bx+16}" cy="{by}" r="11.5" fill="none" stroke="#111" stroke-width="0.9"/>')
        o.append(f'<text x="{bx+16}" y="{by+3.5}" font-size="7.5" text-anchor="middle">{esc(r["tag"].split("-",1)[1])}</text>')
        s = SIF.get(r['tag'])
        l1 = f'{s[0]} · SIL {s[3]}' if sif and s else r['range']
        l2 = (s[1] + ' -> ' + s[2])[:44] if sif and s else r['signal'][:44]
        o.append(f'<text x="{bx+38}" y="{by-2}" font-size="7">{esc(l1[:34])}</text>')
        o.append(f'<text x="{bx+38}" y="{by+8}" font-size="6.5" fill="#555">{esc(l2)}</text>')
    # ---- unit box
    o.append(f'<rect x="{BL}" y="{yb0}" width="{BR-BL}" height="{yb1-yb0}" rx="10" fill="#f6f6f6" stroke="#111" stroke-width="2"/>')
    o.append(f'<text x="{(BL+BR)/2}" y="{yb0+26}" font-size="15" font-weight="700" text-anchor="middle">{esc(u)}</text>')
    o.append(f'<text x="{(BL+BR)/2}" y="{yb0+42}" font-size="9.5" text-anchor="middle">{esc(n.get("class",""))} · {esc(n.get("sector_id",""))} sector</text>')
    # ---- edges
    def draw_edge(e, y, inp):
        xa, xb = (XL, BL - 4) if inp else (BR + 4, XR)
        o.append(f'<line x1="{xa}" y1="{y}" x2="{xb-9}" y2="{y}" {style(e)} class="{"edge-in" if inp else "edge-out"}"/>')
        o.append(f'<polygon points="{xb},{y} {xb-9},{y-4} {xb-9},{y+4}" fill="{"#999" if e.get("presence") != "present" else "#111"}"/>')
        lx = 24 if inp else W - 24; an = 'start' if inp else 'end'
        other = e['from_unit_id'] if inp else e['to_unit_id']
        rate = frate(e) + ' · ' + fll(e) + ('' if e.get('presence') == 'present' else ' · absent')
        o.append(f'<text x="{lx}" y="{y-19}" font-size="9" fill="#666" text-anchor="{an}">{esc(other)}</text>')
        o.append(f'<text x="{lx}" y="{y-5}" font-size="11" font-weight="600" text-anchor="{an}">{esc(e["stream_id"])}</text>')
        o.append(f'<text x="{lx}" y="{y+13}" font-size="10" text-anchor="{an}">{esc(rate)}</text>')
        if noz.get(e['stream_id']):
            o.append(f'<text x="{BL+8 if inp else BR-8}" y="{y+4}" font-size="8" font-style="italic" fill="#555" text-anchor="{"start" if inp else "end"}">{esc(noz[e["stream_id"]])}</text>')
        seg = xb - xa
        for (sid, item), (qty, size) in sorted(valves.items()):
            if sid != e['stream_id']: continue
            o.extend(valve_sym(xa + seg * (0.28 if item == 'check valve' else 0.76), y, item, qty, size, inp))
        r = ft_on_edge.get(e['stream_id'])
        if r:
            fx = xa + seg * 0.52
            o.append(f'<circle cx="{fx}" cy="{y}" r="12" fill="white" stroke="#111" stroke-width="1.3"/>')
            o.append(f'<text x="{fx}" y="{y+3}" font-size="7" text-anchor="middle">{esc(r["tag"].split("-",1)[1])}</text>')
    for i, e in enumerate(ein): draw_edge(e, y0 + i * PITCH, True)
    for i, e in enumerate(eout): draw_edge(e, y0 + i * PITCH, False)
    # ---- notes + title block
    notes = [f'Every incident graph edge is drawn: {len(ein)} in, {len(eout)} out. Cables and solids transfers carry no DN (line list rows cable/solids).',
             'Sources: AQS-PIP-004 line list; AQS-CTL-001 instrument index; AQS-INV-005 valve inventory; AQS-CTL-003 cause and effect'
             + (f'; nozzles/{u}.csv.' if noz_rows else f'; no nozzle schedule for {u} yet (unit task 04).')]
    if unplaced_v:
        notes.append('Valves not on a unit edge (inventory basis names no incident stream): ' + '; '.join(
            f'{v["item"]} {v["size"]} ({v["basis"]})' for v in unplaced_v[:6]) + (' ...' if len(unplaced_v) > 6 else ''))
    if noz_rows:
        miss_n = [f'{r["tag"]} {r["service"]}' for r in noz_rows if r['tag'] not in noz.values()]
        if miss_n: notes.append('Nozzles with no matching graph edge (service text): ' + '; '.join(miss_n[:8]) + (' ...' if len(miss_n) > 8 else ''))
    notes.append('Study. Not a PE stamp. Symbols per ISA-5.1-2022 and ISO 10628-2 intent; sheet format per AQS-DWG-001.')
    H = max(yb1 + 40, 176 + nb_rows * 64 + 40) + len(notes) * 15 + 160
    o[0] = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="sans-serif">'
    o[1] = f'<rect x="4" y="4" width="{W-8}" height="{H-8}" fill="white" stroke="#111"/>'
    ny = H - 140 - len(notes) * 15
    o.append(f'<text x="24" y="{ny-10}" font-size="10" font-weight="600">Notes</text>')
    o += [f'<text x="24" y="{ny + 15*i}" font-size="9">{esc(t)}</text>' for i, t in enumerate(notes)]
    rev = hashlib.sha256('\n'.join(o).encode()).hexdigest()[:8]
    tb = [f'Aqueous Solutions (owner)   AQS-PID-001-{u}', f'P&amp;ID {esc(u)} ({esc(n.get("class",""))}, {esc(n.get("sector_id",""))} sector)',
          f'Type: P&amp;ID (ISO_10628_2)   Rev {rev}   Issued {DATE}', 'Created: flow graph pipeline   Approved: not approved (study)',
          f'Graph SHA-256 {GSHA[:16]}   Sheet 1 of 1   AQS-DWG-001']
    x, y, w, h = W - 384, H - 118, 360, 96
    tbg = [f'<g id="aqs-title-block"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="white" stroke="black" stroke-width="1"/>']
    tbg += [f'<text x="{x+8}" y="{y+17+17*i}" font-size="9">{t}</text>' for i, t in enumerate(tb)]
    tbg.append('</g>')
    open(f'docs-authority/pid/{u}.svg', 'w').write('\n'.join(o) + '\n' + '\n'.join(tbg) + '</svg>\n')
    return dict(unit=u, drawing=f'AQS-PID-001-{u}', rev=rev, file=f'docs-authority/pid/{u}.svg', sector=n.get('sector_id', ''),
                unit_class=n.get('class', ''), edges_in=len(ein), edges_out=len(eout),
                valves_placed=sum(v[0] for v in valves.values()), valves_unplaced=len(unplaced_v),
                instruments=len(inst), sifs=n_sif, nozzles=len(noz_rows))

os.makedirs('docs-authority/pid', exist_ok=True)
import glob as _glob
for _f in _glob.glob('docs-authority/pid/*.svg'):                                        # orphan hygiene: sheets of units no longer drawn
    if os.path.basename(_f)[:-4] not in UNITS: os.remove(_f)
recs = [sheet(u) for u in UNITS]
with open('docs-authority/pid/_register.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(recs[0].keys())); w.writeheader(); w.writerows(recs)
json.dump({'generated_by': 'docs-authority/_pid_sheets.py', 'graph_sha256': GSHA, 'patterns': ['docs-authority/pid/*'],
           'sheets': [r['unit'] for r in recs]}, open('docs-authority/pid/_generated.json', 'w'), indent=1)
open('docs-authority/pid/_generated.json', 'a').write('\n')
# ---- DRAWING_REGISTER.md: append this series idempotently (owner _drawings.py does not glob pid/)
lines = [l for l in open('docs-authority/DRAWING_REGISTER.md').read().splitlines() if not l.startswith('| AQS-PID-')]
base = sum(1 for l in lines if l.startswith('| AQS-'))
lines = [re.sub(r'^\d+ drawings\.', f'{base + len(recs)} drawings.', l) for l in lines]
prov = 'The AQS-PID-001 series (unit P&amp;IDs) is appended by `docs-authority/_pid_sheets.py`, provenance `docs-authority/pid/_generated.json`; rerun it after `_drawings.py`.'
if prov not in lines: lines.insert(next(i for i, l in enumerate(lines) if l.startswith('| Number |')) - 1, prov)
lines += [f"| {r['drawing']} | P&amp;ID {r['unit']} | P&amp;ID (ISO_10628_2) | {r['rev']} | {r['file']} |" for r in recs]
open('docs-authority/DRAWING_REGISTER.md', 'w').write('\n'.join(lines) + '\n')
print(f"{len(recs)} P&ID sheets; edges {sum(r['edges_in'] + r['edges_out'] for r in recs)}; valves {sum(r['valves_placed'] for r in recs)} placed / {sum(r['valves_unplaced'] for r in recs)} unplaced; instruments {sum(r['instruments'] for r in recs)}")

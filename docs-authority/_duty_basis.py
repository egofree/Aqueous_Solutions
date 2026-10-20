"""X-PAR-04 regenerated duty basis: section 1 (mass in/out, electrical duty, streams) and the section 2 hold-up sentence of every duty sheet,
and the node params.duty string, from the current graph. A present unit with no sheet gets one AUTHORED here on the house AQS-STD-001
8-section standard: section 1 from the graph closure, sections 2-8 quoting what the graph node carries (design / envelope / sizing /
design_storage / relief params, instrument loops of AQS-CTL-001) and honest 'study/pending' statements where no deep study exists - no
invented content. Also emits duties/_origins.json (U2a): the unit -> origin/size edges extracted from the same sheets, read by
_line_list.py instead of the markdown."""
import csv as _csv, glob, hashlib, json, os, re, sys, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); GP = os.path.join(ROOT, 'flow_graph/plant_flow_graph.json'); D = os.path.join(ROOT, 'docs-authority/duties')
f4 = lambda x: f'{x:.4g}'
def lst(es):
    s = '; '.join(f"{e['stream_id']} {f4(e['rate']['value'] or 0)} kg/d ({e.get('carries') or e['stream_id']})" for e in es[:4])
    return s + (f'; {len(es) - 4} more' if len(es) > 4 else '') if es else 'none'
_LOOPS = collections.defaultdict(set)
for _r in _csv.DictReader(open(os.path.join(ROOT, 'docs-authority/inventory/INSTRUMENT_INDEX.csv'))): _LOOPS[_r['unit']].add(_r['loop'])
_VESSEL_ZERO = ('kettle', 'precip', 'separator', 'store')   # utilities-only nozzle file where nothing is piped (kept in step with _nozzle_sched.py)
def _scalars(d, skip=()):
    out = []
    for k, v in (d or {}).items():
        if k in skip or isinstance(v, (dict, list)): continue
        out.append(f'{k} {v if isinstance(v, (str, bool, int)) else f4(v)}')
    return '; '.join(out)
def _dot(s):
    while s.endswith('..'): s = s[:-1]
    return s if s.endswith('.') else s + '.'
def author(n, g, ins, outs, mi, mo, kw):
    """Full AQS-STD-001 sheet for a present unit whose sheet does not exist yet: graph facts quoted, gaps stated as pending."""
    u = n['unit_id']; p = n.get('params') or {}; env = p.get('envelope') or {}; ds = p.get('design') or {}; sz = p.get('sizing') or {}
    sto = p.get('design_storage') or {}; edges = [e for e in g['edges'] if u in (e['from_unit_id'], e['to_unit_id'])]
    conns = [e for e in edges if e.get('presence') == 'present' and (('mass' in (e.get('layers') or []) and (e.get('rate') or {}).get('unit') == 'kg/d') or ((e.get('rate') or {}).get('unit') == 'kW' and (e['stream_id'].startswith('HL-') or 'thermal' in (e.get('layers') or [])) and e.get('phase') not in ('E', 'electric') and 'elec' not in (e.get('layers') or [])))]
    vents = [e for e in edges if e.get('presence') == 'present' and 'vent' in (e['stream_id'] + ' ' + str(e.get('carries') or '')).lower()]
    unrate = [e['stream_id'] for e in edges if e.get('presence') == 'present' and 'mass' in (e.get('layers') or []) and (e.get('rate') or {}).get('unit') != 'kg/d']
    loops = sorted(_LOOPS.get(u, ()))
    o = [f'# {u}', '', f"Standard: AQS-STD-001 Rev A. Graph Rev {g.get('revision')}. Study. Not a PE stamp.", '',
         f'1. Basis. Mass in {f4(mi)} kg/d. Mass out {f4(mo)} kg/d. Electrical duty {kw:.4f} kW. In: {lst(ins)}. Out: {lst(outs)}.', '', '2. Size.']
    s2 = []
    esz = env.get('size_mm') or p.get('size_mm')
    if esz:
        L, W, H = esz; V = L * W * H / 1e9
        s2.append(f'- Envelope {L}×{W}×{H} mm, {f4(V)} m³.' + (f' That box over this flow would be {V*1000/mi*24:.1f} h if it were full. It is not a residence time.' if mi > 0 else ''))
        if env.get('basis'): s2.append(_dot(f'- Envelope basis (graph node): {env["basis"]}'))
        elif p.get('size_note'): s2.append(_dot(f'- Envelope: {p["size_note"]}'))
    if sto: s2.append(_dot(f'- Storage sizing (AQS-DUTY-064, graph design_storage): {_scalars(sto, skip=("material",))}'))
    if sz: s2.append(_dot(f'- Sizing study {sz.get("source", "pending")} ({sz.get("status", "study")}): {_scalars(sz, skip=("status", "source", "status_note"))}'))
    if ds: s2.append(_dot(f'- Graph design (AQS-PAR-001 sizing): {_scalars(ds, skip=("material",))}'))
    flat = _scalars({k: v for k, v in p.items() if k not in ('design', 'envelope', 'sizing', 'design_storage', 'size_mm', 'size_note', 'note', 'internals', 'presence', 'design_kPa', 'relief_mm', 'relief_basis', 'basis') and not isinstance(v, dict)})
    if flat: s2.append(_dot(f'- Node params (AQS-PAR-001): {flat}'))
    if p.get('note'): s2.append(_dot(f'- Node note: {p["note"]}'))
    if p.get('internals'): s2.append(_dot(f'- Internals (graph node): {p["internals"]}'))
    if p.get('basis'): s2.append(_dot(f'- Basis (graph node): {p["basis"]}'))
    if not (esz or sz or ds or sto or flat): s2.append('- Sizing calculation pending (unit task 02). The graph node carries no design and no envelope.')
    o += s2
    o += ['']
    mat = ds.get('material') or sto.get('material')
    o.append('3. Material. ' + (f'{mat} (graph node material). Corrosion allowance per the AQS-STD-001 shop rule; no measured pit rate.' if mat else 'Selection pending (unit task 09, AQS-STD-002 across the AQS-ASSAY-001 Rev C bounding cases). Not chosen on this page.'))
    if conns:
        n4 = f'4. Nozzles. Schedule at `nozzles/{u}.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`.'
    elif n.get('class') in _VESSEL_ZERO:
        n4 = f'4. Nozzles. No piped process connection on the graph yet (no kg/d rated edge); `nozzles/{u}.csv` carries only the drain and vent utilities.'
    else:
        n4 = '4. Nozzles. No piped process connection on the graph (un-rated or non-mass edges only); no nozzle schedule is issued yet. Nothing to size a bore against.'
    if conns or n.get('class') in _VESSEL_ZERO:
        n4 += ' Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).'
    o += ['', n4, '']
    o.append('5. Instruments. ' + (f"Loops {', '.join(loops)} in AQS-CTL-001. What trips is stated on the loop." if loops else 'No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.'))
    o += ['']
    if p.get('relief_basis'):
        rb = p['relief_basis']; rbc = rb.get('case') if isinstance(rb, dict) else rb
        o.append(_dot('6. Relief. ' + f'Node relief basis: {rbc}' + (f'. Bore {p["relief_mm"]} mm.' if p.get('relief_mm') else '') + (f' Design {f4(p["design_kPa"])} kPa g (node design_kPa).' if p.get('design_kPa') else '')) + ' Not to the room.')
    elif vents:
        o.append('6. Relief. ' + f"Vent edge {' and '.join(e['stream_id'] for e in vents)} on the graph (to {' and '.join(sorted(set(e['to_unit_id'] for e in vents)))}). Atmospheric operation is not claimed beyond this edge. Not to the room.")
    else:
        o.append('6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.')
    stl = f' The envelope is `cad/stl/{u}.stl`.' if os.path.exists(os.path.join(ROOT, f'cad/stl/{u}.stl')) else ' No CAD envelope issued yet.'
    o += ['', f'7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule).{stl}', '']
    oi = []
    if not (sz or sto): oi.append('Sizing calculation pending (unit task 02).')
    if not mat: oi.append('Material selection pending (unit task 09).')
    if not loops: oi.append('No instrument loop yet (unit task 08).')
    if not (p.get('relief_basis') or vents): oi.append('Relief case pending (unit task 07).')
    if unrate: oi.append(f"Edges {', '.join(unrate)} carry no kg/d rate yet; section 1 reads zero flow until the parametric model rates them.")
    if conns or n.get('class') in _VESSEL_ZERO: oi.append('Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).')
    o.append('8. Open items. ' + ' '.join(oi))
    return '\n'.join(o) + '\n'
def main():
    g = json.load(open(GP)); ch = 0; au = 0
    for n in g['nodes']:
        u = n['unit_id']; p = os.path.join(D, f'{u}.md')
        ins = [e for e in g['edges'] if e['to_unit_id'] == u and e['presence'] == 'present' and 'mass' in (e.get('layers') or []) and e['rate'].get('unit') == 'kg/d']
        outs = [e for e in g['edges'] if e['from_unit_id'] == u and e['presence'] == 'present' and 'mass' in (e.get('layers') or []) and e['rate'].get('unit') == 'kg/d']
        mi = sum(e['rate']['value'] or 0 for e in ins); mo = sum(e['rate']['value'] or 0 for e in outs)
        kw = ((n.get('continuous_kw') or {}).get('value') or 0) if isinstance(n.get('continuous_kw'), dict) else 0
        prm = n.setdefault('params', {})
        if 'duty' in prm: prm['duty'] = re.sub(r'^In [\d.]+ kg/d, out [\d.]+ kg/d, [\d.]+ kW\.', f'In {mi:.3f} kg/d, out {mo:.3f} kg/d, {kw:.3f} kW.', prm['duty'])
        if not os.path.exists(p):
            if n.get('presence') != 'present': continue   # standby units keep no sheet until they go present
            open(p, 'w').write(author(n, g, ins, outs, mi, mo, kw)); au += 1; continue
        s = open(p).read(); s0 = s
        s = re.sub(r'^1\. Basis\..*$', f'1. Basis. Mass in {f4(mi)} kg/d. Mass out {f4(mo)} kg/d. Electrical duty {kw:.4f} kW. In: {lst(ins)}. Out: {lst(outs)}.', s, count=1, flags=re.M)
        m = re.search(r'Envelope [\d×]+ mm, ([\d.]+) m³\. That box over this flow would be [\d.]+ h if it were full\.', s)
        if m and mi > 0: s = s.replace(m.group(0), re.sub(r'would be [\d.]+ h', f'would be {float(m.group(1))*1000/mi*24:.1f} h', m.group(0)))
        if s != s0: open(p, 'w').write(s); ch += 1
    # R11 Rev AC regen: the graph is closed this lane, so params.duty is refreshed in memory only
    # (CRYO_ASU duty text trails its balanced rates; a graph-write lane picks it up). The manifest
    # below hashes the on-disk graph, which this script no longer rewrites.
    gsha = hashlib.sha256(open(GP, 'rb').read()).hexdigest()   # manifest: every sheet was checked against this exact graph (read by _rev_stamp.py)
    json.dump({'graph_sha256': gsha, 'sheets': len(os.listdir(D)), 'patterns': ['docs-authority/duties/*.md']}, open(os.path.join(D, '_generated.json'), 'w'), indent=1)
    # U2a sidecar: unit -> origin/size for every sheet in the directory (the same glob and regex
    # _line_list.py used on the markdown), so _line_list reads origins from here instead of the md.
    origins = {}
    for f in glob.glob(os.path.join(D, '*.md')):
        s = open(f).read().replace('\u2212', '-')
        m = re.search(r'[Oo]rigin (-?\d+), (-?\d+), (-?\d+) mm\. Size (\d+) [×x] (\d+) [×x] (\d+)', s)
        if m: origins[os.path.basename(f)[:-3]] = {'origin_mm': [int(x) for x in m.groups()[:3]], 'size_mm': [int(x) for x in m.groups()[3:]]}
    json.dump({'_generated_from': {'graph_sha256': gsha, 'generator': 'docs-authority/_duty_basis.py'}, 'origins': origins},
              open(os.path.join(D, '_origins.json'), 'w'), indent=1)
    print('duty sheets refreshed', ch, '| authored', au, '| origins', len(origins))
if __name__ == '__main__': main()

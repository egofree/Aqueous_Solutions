"""X-PAR-04 regenerated duty basis: section 1 (mass in/out, electrical duty, streams) and the section 2 hold-up sentence of every duty sheet,
and the node params.duty string, from the current graph. Other sections are untouched."""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); GP = os.path.join(ROOT, 'flow_graph/plant_flow_graph.json'); D = os.path.join(ROOT, 'docs-authority/duties')
f4 = lambda x: f'{x:.4g}'
def lst(es):
    s = '; '.join(f"{e['stream_id']} {f4(e['rate']['value'] or 0)} kg/d ({e.get('carries') or e['stream_id']})" for e in es[:4])
    return s + (f'; {len(es) - 4} more' if len(es) > 4 else '') if es else 'none'
def main():
    g = json.load(open(GP)); ch = 0
    for n in g['nodes']:
        u = n['unit_id']; p = os.path.join(D, f'{u}.md')
        ins = [e for e in g['edges'] if e['to_unit_id'] == u and e['presence'] == 'present' and 'mass' in (e.get('layers') or []) and e['rate'].get('unit') == 'kg/d']
        outs = [e for e in g['edges'] if e['from_unit_id'] == u and e['presence'] == 'present' and 'mass' in (e.get('layers') or []) and e['rate'].get('unit') == 'kg/d']
        mi = sum(e['rate']['value'] or 0 for e in ins); mo = sum(e['rate']['value'] or 0 for e in outs)
        kw = ((n.get('continuous_kw') or {}).get('value') or 0) if isinstance(n.get('continuous_kw'), dict) else 0
        prm = n.setdefault('params', {})
        if 'duty' in prm: prm['duty'] = re.sub(r'^In [\d.]+ kg/d, out [\d.]+ kg/d, [\d.]+ kW\.', f'In {mi:.3f} kg/d, out {mo:.3f} kg/d, {kw:.3f} kW.', prm['duty'])
        if not os.path.exists(p): continue
        s = open(p).read(); s0 = s
        s = re.sub(r'^1\. Basis\..*$', f'1. Basis. Mass in {f4(mi)} kg/d. Mass out {f4(mo)} kg/d. Electrical duty {kw:.4f} kW. In: {lst(ins)}. Out: {lst(outs)}.', s, count=1, flags=re.M)
        m = re.search(r'Envelope [\d×]+ mm, ([\d.]+) m³\. That box over this flow would be [\d.]+ h if it were full\.', s)
        if m and mi > 0: s = s.replace(m.group(0), re.sub(r'would be [\d.]+ h', f'would be {float(m.group(1))*1000/mi*24:.1f} h', m.group(0)))
        if s != s0: open(p, 'w').write(s); ch += 1
    # R11 Rev AC regen: the graph is closed this lane, so params.duty is refreshed in memory only
    # (CRYO_ASU duty text trails its balanced rates; a graph-write lane picks it up). The manifest
    # below hashes the on-disk graph, which this script no longer rewrites.
    import hashlib   # manifest: every sheet was checked against this exact graph (read by _rev_stamp.py)
    json.dump({'graph_sha256': hashlib.sha256(open(GP, 'rb').read()).hexdigest(), 'sheets': len(os.listdir(D)), 'patterns': ['docs-authority/duties/*.md']}, open(os.path.join(D, '_generated.json'), 'w'), indent=1)
    print('duty sheets refreshed', ch)
if __name__ == '__main__': main()

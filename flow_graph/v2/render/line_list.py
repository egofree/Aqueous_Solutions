"""The line-list pipeline chain renderer wave (the document lane of the
ledger rows line_list [E], placement_routes [F], nozzle_sched [E],
pid_sheets [F] and drawings [F]; the compute halves live in
flow_graph/v2/functions/line_list.py - the C-dict namespace and row kernel
the other stages execute - functions/routes.py - the A-M-074 rack routing
kernel - and functions/nozzles.py - the coverage-merge kernel). Reference
writers: docs-authority/_line_list.py, _placement_routes.py,
_nozzle_sched.py, _pid_sheets.py, _drawings.py. The ported render functions
reproduce the v1 document templates exactly (same headers, document numbers,
table shapes, number formats and basis texts); the acceptance is byte-exact
reproduction of the committed files (flow_graph/v2/test_render_line_list.py,
test_render_pid_drawings.py).

Input payloads (the v1 stage file reads, read at the caller's I/O boundary
and passed in inputs; a caller that omits one gets loud stub bytes, never a
wrong document):
- inputs['line_positions']: the unit-centre namespace C (the line-list
  family's payload; the inventory wave declares the same key);
- inputs['placement_seed']: flow_graph/placement_seed.json, parsed (the
  views-wave payload key; the routing datums and the sidecar revision);
- inputs['graph_sha256']: the committed graph file's SHA-256 (the
  ISO_ROUTES.json provenance block; the v1 hashlib read of the file);
- inputs['instrument_index'] / inputs['other_inventory']: the committed
  inventory CSV rows (doc_instr_index / inventory_other products; explicit
  renderer-input edges - inventory_other is byte-exact in render/inventory.py
  and can compose in memory, doc_instr_index is still REMAINING there);
- inputs['cause_effect']: the docs-authority/CAUSE_EFFECT.md '| SIF-' column
  rows (doc_sif product, REMAINING in the controls wave);
- inputs['nozzle_schedules']: the merged schedule state
  {unit: rows-or-None} (the nozzle_sched product; the nozzles family proves
  it is the merge fixpoint of the hand rows, so the committed files are the
  declared payload);
- inputs['drawing_svgs'] / inputs['drawing_steps']: the drawing inventory the
  drawings stage stamps (the graphviz views SVGs - an external-binary render,
  REMAINING per the views wave; the motor-FA and mfg drawing SVGs - lanes
  outside this chain) and the STEP models. The title-block STAMP composition
  over them is ported here (stamp()) and is byte-verified at the committed
  fixpoint: strip the stamp, re-stamp, and the committed bytes come back.

Composition rules ported (the views-wave docstring's recording, now
implemented):
- pid_sheets' DRAWING_REGISTER append is the idempotent foreign-row keep:
  compose_pid_register() strips any previous AQS-PID rows, recounts the
  drawings count line, re-inserts the provenance note under the count line
  and appends the rows - identical output whichever of the two writers ran
  last;
- drawings' register is the same composition from the other side:
  render_drawings_register() renders the drawings-series rows and keeps the
  pid rows (render_pid_register_rows) - the committed register is that
  two-writer fixpoint, and the test proves both orders produce it.

REMAINING (outputs of these rows NOT ported here, each with its reason):
- the graphviz views SVGs (flow_graph/views/*.svg): external-binary dot/fdp
  renders (the views wave's REMAINING entry); the stamp over them is ported
  and byte-verified against the committed files via the drawing_svgs payload;
- pid/_generated.json: the graph-sha pattern manifest (bookkeeping; dies per
  the ledger);
- pid orphan hygiene (removing sheets of units no longer drawn): file-tree
  maintenance outside the registry; the census test holds DOCS equal to the
  graph census instead;
- the v1 stdout ledgers (the BIG oversized-line warnings, the nozzle append
  tallies): session output, not documents;
- non-basement payload variants (locale runs): no committed golden.

Pure: no I/O here - the registry returns bytes and file writing stays
outside.
"""
import csv
import hashlib
import io
import json
import re
from copy import deepcopy

from flow_graph.v2.functions import line_list as _LL
from flow_graph.v2.functions import nozzles as _NZ
from flow_graph.v2.functions import routes as _RT
_PID_DATE = '2026-10-19'                                       # the v1 sheet issue date
_DWG_DATE = '2026-10-15'                                       # the register date
_ARROW_H = float('3.5')            # the check-valve arrowhead half-height, mm
_BUBBLE_TEXT_DY = float('3.5')     # the bubble tag baseline offset, mm
_CHK_POS = float('0.28')           # check-valve position, fraction of the edge run
_ISOL_POS = float('0.76')          # isolation-valve position, fraction of the edge run
_FT_POS = float('0.52')            # FT bubble position, fraction of the edge run
_TB = re.compile(r'\n?<g id="aqs-title-block".*?</g>\n?', re.S)
_FOREIGN_ROWS = ('| AQS-PID-',)                                # register rows appended by pid_sheets
_FOREIGN_NOTES = ('The AQS-PID-001 series',)                   # their provenance note, kept with them
_PID_PROV = ('The AQS-PID-001 series (unit P&amp;IDs) is appended by '
             '`docs-authority/_pid_sheets.py`, provenance `docs-authority/pid/_generated.json`; '
             '`_drawings.py` keeps these rows.')


def _graph(m):
    """The plain committed-graph structure the chain stages read: the seed,
    verbatim. Read-only. (The line list, the P&ID sheets and the drawing
    register are committed against the graph file; the computed overlay is
    deliberately not composed here - the views-wave ruling: composing
    re-derived physics books would couple document bytes to physics-lane
    drift instead of catching it on the graph, where the staleness gates
    live.)"""
    return deepcopy(m.data)


def _stub(path, key):
    """The loud bytes a caller gets when it does not carry the payload the
    renderer reads."""
    return (f'# {path}: pending render - input payload {key!r} not provided by this caller '
            f'(the v1 stage read it as a file; the acceptance caller passes it in inputs)\n').encode('utf-8')


def _csv_bytes(matrix):
    """The v1 csv.writer face (CRLF rows, QUOTE_MINIMAL) as bytes - the
    serialization face the reference writers used."""
    s = io.StringIO()
    csv.writer(s).writerows(matrix)
    return s.getvalue().encode('utf-8')


def _csv_dict_bytes(rows, keys):
    """The v1 csv.DictWriter face (CRLF rows, header row) as bytes."""
    s = io.StringIO()
    w = csv.DictWriter(s, keys)
    w.writeheader()
    w.writerows(rows)
    return s.getvalue().encode('utf-8')


def _rows(m, inputs):
    """The line-list namespace over the seed (the payload the chain shares)."""
    return _LL.rows(_graph(m), inputs.get('line_positions'), inputs.get('drivers') or {})


# ---- AQS-PIP-004: the plant line list ------------------------------------------

def render_line_list_md(m, inputs):
    """docs-authority/LINE_LIST.md: the v1 _line_list.py __main__ template."""
    if 'line_positions' not in inputs:
        return _stub('docs-authority/LINE_LIST.md', 'line_positions')
    if 'drivers' not in inputs:
        return _stub('docs-authority/LINE_LIST.md', 'drivers')
    rows = _rows(m, inputs)
    C = inputs['line_positions']
    piped = [r for r in rows if r[3].startswith('DN')]
    miss = [r for r in piped if r[6] is None]
    hdr = f"""# Plant line list

Document number: AQS-PIP-004
Revision: C
Date: 2026-10-21
Authority: graph state 2026-10-21; AQS-PLAN-007 X-PIP-02; class rules keyed to the AQS-STD-002 Rev L section 12 service families (X-MAT-01), verify with `docs-authority/_service_census.py`. Generated by `docs-authority/_line_list.py`. Classes per AQS-PIP-003 Rev A; the fluoro synthesis train, dopant concentrates, molten-metal laundering, and pot-brine concentrates carry per-duty-sheet materials and are pending a PIP-003 Rev B class. Study. Not a PE stamp. Rules (study, AQS-REG-002 A-M-065 to A-M-067): DN from edge `line_DN`, else velocity 1 m/s liquid, 10 m/s gas, minimum DN15, DN50 for slurries; length is the orthogonal distance between unit centres × 1.2; class by the rules in the script.

| Rev | Description | Date |
| --- | --- | --- |
| C | HDR_H2 adjudicated wet acid + sweep air (PVC-U, M3) per X-MAT-06: the 13 wetted header lines move from the dry-gas M1 and assorted P1/P2 families to the new P1 wet-acid-header family; census 23 families. | 2026-10-21 |
| B | Class rules keyed to the AQS-STD-002 Rev L section 12 families (X-MAT-01): the "aqueous process, default thermoplastic" catchall retired; hydrocarbon/fuel/wax cuts to M2 (carbon steel, dry), wet methanol and solvents to M1 (316L), melt pours to "—" launder rows, and the fluoro synthesis train, dopant and pot-brine concentrates to "—" pending PIP-003 Rev B. Run `_service_census.py` as the gate. | 2026-10-21 |
| A | First issue. | 2026-10-15 |

{len(rows)} edges: {len(piped)} piped, {sum(r[3] == 'solids' for r in rows)} solids transfers, {sum(r[3] == 'cable' for r in rows)} electrical. Piped edges without a length (unit position missing): {len(miss)}.

| Line | From | To | DN | Class | Service | Length m | Route | DN basis |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |"""
    out = [hdr] + ['| ' + ' | '.join('' if x is None else str(x) for x in r) + ' |' for r in rows]
    nopos = sorted({x for r in piped if r[6] is None for x in (r[1], r[2]) if x not in C})
    out.insert(1, f"Units with no position anywhere in the repo (no duty origin, no placement row): "
                  f"{len(nopos)}: {', '.join(nopos)}. Their lines carry DN and class; length and route wait "
                  f"for X-BLD placement.\n")
    return ('\n'.join(out) + '\n').encode('utf-8')


# ---- AQS-ISO-001/002: the placement routes -------------------------------------

def _routed(m, inputs):
    """The routed set over the seed: (recs, jrows, miss, D) or None without
    the payloads."""
    seed = inputs.get('placement_seed')
    if seed is None or 'line_positions' not in inputs or 'drivers' not in inputs:
        return None
    D = seed['datums_mm']
    recs, jrows, miss = _RT.route_all(_rows(m, inputs), inputs['line_positions'], D)
    return recs, jrows, miss, D


def render_iso_routes_md(m, inputs):
    """docs-authority/ISO_ROUTES.md: the v1 _placement_routes.py template."""
    got = _routed(m, inputs)
    if got is None:
        return _stub('docs-authority/ISO_ROUTES.md', 'placement_seed')
    recs, _jrows, miss, _D = got
    tab = ['| Line | DN | Class | From | To | dZ up | dX | dY | dZ down | Length m | Elbows |',
           '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    tot = float('0')
    for rec, r in zip(recs, [r for r in _rows(m, inputs) if r[3].startswith('DN')
                             and inputs['line_positions'].get(r[1]) and inputs['line_positions'].get(r[2])]):
        ca, cb = inputs['line_positions'].get(r[1]), inputs['line_positions'].get(r[2])
        (x1, y1, z1), (x2, y2, z2) = ca[0], cb[0]
        zr = _RT.rack_z(inputs['placement_seed']['datums_mm'], z1, z2)
        legs = [round(zr - z1), round(x2 - x1), round(y2 - y1), round(z2 - zr)]
        L = sum(abs(v) for v in legs) / 1000
        el = max(sum(1 for v in legs if abs(v) > 1) - 1, 0)
        tab.append(f'| {rec["line"]} | {rec["DN"]} | {rec["cls"]} | {r[1]} | {r[2]} | '
                   f'{legs[0]} | {legs[1]} | {legs[2]} | {legs[3]} | {L:.1f} | {el} |')
        tot += L
    out = ['''# Placement routes

Document number: AQS-ISO-001
Revision: B
Date: 2026-10-28
Authority: the placement model (flow_graph/placement_seed.json Rev M, AQS-BLD-001 block plan); the A-M-074 rack rule. Generated by `docs-authority/_placement_routes.py`. Study routes. Not a stamped shop pack. Supersedes the retired auto-router output (AQS-3D-BUILD-001 Rev G rejected auto-routing; this table routes only lines whose BOTH ends carry a sourced placement - no invented mm).

Route rule: up to the source-level rack (datum + 3200 mm, AQS-PIP-002), X run, Y run, then vertical to the target centre. Legs in mm, signed. Elbows = non-zero legs - 1. Risers are at least 300 mm above the higher end so every route keeps a flexible leg (X-PIP-04). Unit centres are the placement-model centres; nozzle lateral offsets refine at detail design (the nozzle schedules carry face + height). Supports and stress: AQS-PIP-005.
''',
           f'Status. {len(recs)} positioned piped lines routed, {tot:.0f} m total. {len(miss)} piped lines wait on '
           'unit placements (the named gap: X-BLD-09 / X-RSZ-05).', '']
    out += tab + ['']
    out += ['Waiting on placements:'] + [f'- {x}' for x in miss] if miss else ['All piped lines routed.']
    return ('\n'.join(out) + '\n').encode('utf-8')


def render_iso_routes_json(m, inputs):
    """docs-authority/ISO_ROUTES.json: the v1 supports sidecar (X-PIP-05);
    the _generated_from provenance block reproduces the committed face - the
    v2 provenance lives in the engine manifest."""
    got = _routed(m, inputs)
    if got is None:
        return _stub('docs-authority/ISO_ROUTES.json', 'placement_seed')
    recs, jrows, miss, _D = got
    tot = sum(sum(abs(v) for v in r['legs_mm']) / 1000 for r in jrows)
    seed = inputs['placement_seed']
    gsha = inputs.get('graph_sha256')
    if gsha is None:
        return _stub('docs-authority/ISO_ROUTES.json', 'graph_sha256')
    doc = {'_generated_from': {'graph_sha256': gsha,
                               'generator': 'docs-authority/_placement_routes.py',
                               'placement_seed_revision': seed.get('revision')},
           'rows': jrows,
           'summary': {'routed': len(recs), 'missing_position': len(miss), 'total_m': round(tot)}}
    return json.dumps(doc, indent=1).encode('utf-8')


def render_iso_sheets_csv(m, inputs):
    """docs-authority/iso/ISO_SHEETS.csv: the insulation + fittings sidecar
    (X-INV-003/004). The empty-routed branch keeps the v1 fixed header for
    totality (never taken at the committed state)."""
    got = _routed(m, inputs)
    if got is None:
        return _stub('docs-authority/iso/ISO_SHEETS.csv', 'placement_seed')
    recs, _jrows, _miss, _D = got
    if recs:
        return _csv_dict_bytes(recs, list(recs[0].keys()))
    return _csv_dict_bytes([], ['line', 'DN', 'cls', 'material', 'frm', 'to', 'route_m',
                                'pipe_m', 'pieces', 'cut_list_mm', 'elbows_90', 'flanges',
                                'gaskets', 'stud_bolts', 'stud_size', 'joints', 'joint_type'])


def render_iso_sheets_md(m, inputs):
    """docs-authority/ISO_SHEETS.md: the X-INV-003/004 sheet page."""
    got = _routed(m, inputs)
    if got is None:
        return _stub('docs-authority/ISO_SHEETS.md', 'placement_seed')
    recs, _jrows, miss, _D = got
    seed = inputs['placement_seed']
    L = ['# Isometric sheet data (no SVG: the isometric presentation retired 2026-10-27)', '',
         'Document number: AQS-ISO-002',
         f'Status. {len(recs)} routed lines; waiting on placements {len(miss)}. '
         f'Pipe {_RT.total_m(recs):.0f} m, elbows {sum(x["elbows_90"] for x in recs)}, '
         f'flanges {sum(x["flanges"] for x in recs)}, joints {sum(x["joints"] for x in recs)}.', '',
         'Basis: the AQS-ISO-001 Rev B route rule over the placement model (Rev ' + str(seed.get("revision")) + '); '
         'elbow take-off ASME B16.9 long-radius (metal) or 0.5 x OD (thermoplastic, A-M-121); 6 m random '
         'lengths; flanges at both nozzles; ASME B16.5 Class 150 bolting; OD ASME B36.10M. Not checked '
         'here: clashes with structure and other lines along the rack (X-PIP-04 with supports and stress).', '',
         '## Lines', '', '| Line | From | To | DN | Class | Pipe m | Elbows |',
         '| --- | --- | --- | --- | --- | --- | --- |']
    L += [f"| {x['line']} | {x['frm']} | {x['to']} | {x['DN']} | {x['cls']} | {x['pipe_m']} | "
          f"{x['elbows_90']} |" for x in recs]
    if miss:
        L += ['', 'Waiting on placements:'] + [f'- {x}' for x in miss]
    return ('\n'.join(L) + '\n').encode('utf-8')


# ---- unit task 04: the nozzle schedules -----------------------------------------

def render_nozzle_csv(u):
    """docs-authority/nozzles/<u>.csv: the merged schedule state serialized.
    The payload carries the committed file bytes per unit (the nozzles family
    proves the committed tree is the merge's fixpoint, so the committed rows
    re-merge to themselves). Where the merge appends nothing the v1 wrote
    nothing - the committed bytes come back verbatim (the hand-era files keep
    their LF face; the generator-written files their CRLF face). Where it
    appends, the write goes through the v1 csv.writer face (CRLF)."""
    def f(m, inputs):
        sched = inputs.get('nozzle_schedules')
        if sched is None:
            return _stub(f'docs-authority/nozzles/{u}.csv', 'nozzle_schedules')
        raw = sched.get(u)
        if raw is None:
            return _stub(f'docs-authority/nozzles/{u}.csv', f'the {u} schedule')
        rows = list(csv.reader(io.StringIO(raw.decode('utf-8'))))
        g = _graph(m)
        dn = _LL.dn_map(_LL.rows(g, inputs.get('line_positions'), inputs.get('drivers') or {}))
        got = _NZ.schedule_rows(g, dn, {u: rows}, units=frozenset((u,))).get(u)
        if got == rows:
            return raw                                    # the v1 no-write branch
        return _csv_bytes(got)                            # the v1 write face
    f.__name__ = f'render_nozzle_csv_{u}'
    f.__doc__ = f'docs-authority/nozzles/{u}.csv: the merged nozzle schedule.'
    return f


# ---- AQS-PID-001: the P&ID sheets ------------------------------------------------

def _esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def _basis_stream(b):
    return b.split(':')[0].split()[0] if b else ''


def _style(e):
    ph = e.get('phase')
    lay = e.get('layers') or []
    if e.get('presence') != 'present':
        return 'stroke="#999" stroke-width="1.4" stroke-dasharray="4,4"'
    if ph in ('E', 'electric', 'L/E') or 'elec' in lay:
        return 'stroke="#111" stroke-width="1.2" stroke-dasharray="2,3"'
    if ph in ('S', 'S/L', 'L/S'):
        return 'stroke="#111" stroke-width="1.6" stroke-dasharray="12,4,3,4"'
    if ph in ('G', 'L/G'):
        return 'stroke="#111" stroke-width="1.4" stroke-dasharray="8,4"'
    if ph in ('heat', 'thermal'):
        return 'stroke="#111" stroke-width="2.6"'
    return 'stroke="#111" stroke-width="1.6"'


def _frate(e):
    r = e.get('rate') or {}
    v, un = r.get('value'), r.get('unit') or ''
    if v is None:
        return 'rate null (study)'
    if un == 'kg/d':
        return f'{v:.1f} kg/d'
    if un.lower() == 'kw':
        return f'{v:.1f} kW'
    return (f'{v:.4g} {un}').strip()


def _fll(e, ll):
    r = ll.get(e['stream_id'])
    if not r:
        return 'not in line list'
    if r[3] == 'cable':
        return 'cable (schedule X-ELS-06)'
    if r[3] == 'solids':
        return 'solids transfer'
    return f'{r[3]} {r[4]}'


def _valve_sym(x, y, item, qty, dn, flow_in):
    o = []
    if item == 'check valve':                      # flow-direction arrow upstream of the bowtie
        d = 1 if flow_in else -1
        o.append(f'<line x1="{x - 22 * d:.1f}" y1="{y}" x2="{x - 14 * d:.1f}" y2="{y}" '
                 f'stroke="#111" stroke-width="1.2"/>')
        o.append(f'<polygon points="{x - 13 * d:.1f},{y} {x - 19 * d:.1f},{y - _ARROW_H} '
                 f'{x - 19 * d:.1f},{y + _ARROW_H}" fill="#111"/>')
    o.append(f'<path d="M {x - 9:.1f},{y - 6} L {x - 1:.1f},{y} L {x - 9:.1f},{y + 6} Z '
             f'M {x + 9:.1f},{y - 6} L {x + 1:.1f},{y} L {x + 9:.1f},{y + 6} Z" fill="white" '
             f'stroke="#111" stroke-width="1.3"/>')
    lab = ('%dx ' % qty if qty > 1 else '') + ('chk' if item == 'check valve' else 'isol') + \
        (' ' + dn if dn else '')
    o.append(f'<text x="{x:.1f}" y="{y - 11:.1f}" font-size="7.5" text-anchor="middle">{_esc(lab)}</text>')
    return o


def _sif_map(cause_effect):
    """tag -> (sif id, cause, effect, SIL) from the CAUSE_EFFECT '| SIF-'
    rows (the payload carries the column lists; the tag extraction is the
    pid module's)."""
    SIF = {}
    for c in cause_effect or ():
        if len(c) >= 7:
            for tag in re.findall(r'[A-Z][A-Z0-9_]*-(?:FT|PT|LT|TE|LSH|PSH|TSH|FSH)-\d+',
                                  c[2].split('(')[0]):
                SIF[tag] = (c[0], c[3], c[4], c[6])
    return SIF


def _pid_state(m, inputs):
    """The shared pid context, or (None, payload-key) naming the first
    missing payload: the seed graph, the line-list namespace, the instrument
    and valve inventories, the SIF map and the merged nozzle schedules."""
    for key in ('instrument_index', 'other_inventory', 'cause_effect', 'nozzle_schedules'):
        if inputs.get(key) is None:
            return None, key
    g = _graph(m)
    ll = {r[0]: r for r in _LL.rows(g, inputs.get('line_positions'), inputs.get('drivers') or {})}
    return dict(g=g, ll=ll, CARRIES={e['stream_id']: e.get('carries') for e in g['edges']},
                GREV=g['revision'], SIF=_sif_map(inputs['cause_effect']),
                inst_rows=inputs['instrument_index'], inv_rows=inputs['other_inventory'],
                sched=inputs['nozzle_schedules']), None


def _sheet(ctx, u):
    """One P&ID sheet: (svg text, register row) - the v1 sheet(), verbatim."""
    g, ll, CARRIES, GREV, SIF = ctx['g'], ctx['ll'], ctx['CARRIES'], ctx['GREV'], ctx['SIF']
    N = {n['unit_id']: n for n in g['nodes']}
    n = N[u]
    p = n.get('params') or {}
    ein = sorted((e for e in g['edges'] if e['to_unit_id'] == u), key=lambda e: e['stream_id'])
    eout = sorted((e for e in g['edges'] if e['from_unit_id'] == u), key=lambda e: e['stream_id'])
    inc = {e['stream_id'] for e in ein + eout}
    valves = {}
    unplaced_v = []
    for r in ctx['inv_rows']:
        if r['category'] != 'valve' or r['unit'] != u:
            continue
        sid = _basis_stream(r['basis'])
        if sid in inc:
            valves.setdefault((sid, r['item']), [0, None])[0] += int(r['qty'] or 1)
            valves[(sid, r['item'])][1] = r['size']
        else:
            unplaced_v.append(r)
    inst = [r for r in ctx['inst_rows'] if r['unit'] == u]
    ft_on_edge = {}
    for r in inst:
        if '-FT-' in r['tag']:
            sid = _basis_stream(r['basis'])
            if sid in inc and sid not in ft_on_edge:
                ft_on_edge[sid] = r
    on_edge_tags = {r['tag'] for r in ft_on_edge.values()}
    band = sorted((r for r in inst if r['tag'] not in on_edge_tags), key=lambda r: (r['loop'], r['tag']))
    noz = {}
    noz_rows = []
    raw = ctx['sched'].get(u)
    if raw is not None:
        rows = list(csv.reader(io.StringIO(raw.decode('utf-8'))))
        hdr = rows[0]
        noz_rows = [dict(zip(hdr, r)) for r in rows[1:] if r and r[0].strip()]
        bysvc = {}
        for r in noz_rows:
            bysvc.setdefault(r['service'], []).append(r['tag'])
        for svc, tags in bysvc.items():
            for t, s in zip(sorted(tags), sorted(x for x in inc if CARRIES.get(x) == svc)):
                noz[s] = t
    # ---- geometry
    W = 1500
    XL, BL, BR, XR = 430, 590, 910, 1070
    PITCH = 46
    nb_rows = max(1, -(-len(band) // 9))
    y0 = 176 + nb_rows * 64
    yb0, yb1 = y0 - 30, max(y0 + max(len(ein), len(eout), 1) * PITCH, y0 + 110)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="0" font-family="sans-serif">',
         f'<rect x="4" y="4" width="{W - 8}" height="0" fill="white" stroke="#111"/>']
    o.append(f'<text x="24" y="34" font-size="15" font-weight="600">Unit {_esc(u)} · '
             f'{_esc(n.get("class", ""))} · sector {_esc(n.get("sector_id", ""))} · '
             f'{_esc(n.get("presence", ""))}</text>')
    facts = []
    if p.get('V_m3') is not None:
        facts.append('V %g m3' % p['V_m3'])
    if p.get('design_kPa') is not None:
        facts.append('design %g kPa g' % p['design_kPa'])
    if (p.get('design') or {}).get('T_C') is not None:
        facts.append('design T %g C' % p['design']['T_C'])
    ck = n.get('continuous_kw')
    if isinstance(ck, dict) and ck.get('value') is not None:
        facts.append('%g kW continuous' % ck['value'])
    elif isinstance(ck, (int, float)):
        facts.append('%g kW continuous' % ck)
    o.append(f'<text x="24" y="54" font-size="10.5">'
             f'{_esc(" · ".join(facts) if facts else "no design params on the graph node")}</text>')
    n_sif = sum(1 for r in inst if r['tag'] in SIF)
    o.append(f'<text x="24" y="72" font-size="10.5">Edges {len(ein)} in + {len(eout)} out · valves '
             f'{sum(v[0] for v in valves.values())} placed / {len(unplaced_v)} unplaced · instruments '
             f'{len(inst)} ({n_sif} SIF) · nozzles {len(noz_rows)}</text>')
    o.append(f'<text x="24" y="90" font-size="10.5">Rates and DN/class per AQS-PIP-004; tags per '
             'AQS-CTL-001; valves per AQS-INV-005; SIFs per AQS-CTL-003.</text>')
    # ---- legend (top right)
    ly = 32
    o.append(f'<rect x="{W - 330}" y="20" width="310" height="120" fill="white" stroke="#111"/>')
    for lab, st in [('liquid', 'stroke="#111" stroke-width="1.6"'),
                    ('gas', 'stroke="#111" stroke-width="1.4" stroke-dasharray="8,4"'),
                    ('solids / slurry', 'stroke="#111" stroke-width="1.6" stroke-dasharray="12,4,3,4"'),
                    ('electrical', 'stroke="#111" stroke-width="1.2" stroke-dasharray="2,3"'),
                    ('heat loop (kW)', 'stroke="#111" stroke-width="2.6"')]:
        o.append(f'<line x1="{W - 318}" y1="{ly}" x2="{W - 274}" y2="{ly}" {st}/>'
                 f'<text x="{W - 266}" y="{ly + 3}" font-size="8.5">{lab}</text>')
        ly += 15
    o += _valve_sym(W - 296, ly + 5, 'isolation valve', 1, '', True)
    o.append(f'<text x="{W - 266}" y="{ly + 8}" font-size="8.5">isolation / check valve (xqty)</text>')
    ly += 24
    o.append(f'<circle cx="{W - 296}" cy="{ly}" r="9" fill="white" stroke="#111"/>'
             f'<text x="{W - 296}" y="{ly + 3}" font-size="7" text-anchor="middle">FT-01</text>')
    o.append(f'<text x="{W - 266}" y="{ly + 3}" font-size="8.5">instrument bubble (SIF: double)</text>')
    # ---- instrument band
    o.append(f'<text x="24" y="152" font-size="10.5" font-weight="600">Instrument loops (tags are '
             f'{_esc(u)}-&lt;loop&gt;; range and signal per AQS-CTL-001)</text>')
    for i, r in enumerate(band):
        bx, by = 24 + (i % 9) * 158, 172 + (i // 9) * 64
        sif = r['tag'] in SIF
        o.append(f'<circle cx="{bx + 16}" cy="{by}" r="16" fill="white" stroke="#111" stroke-width="1.4"/>')
        if sif:
            o.append(f'<circle cx="{bx + 16}" cy="{by}" r="11.5" fill="none" stroke="#111" stroke-width="0.9"/>')
        o.append(f'<text x="{bx + 16}" y="{by + _BUBBLE_TEXT_DY}" font-size="7.5" text-anchor="middle">'
                 f'{_esc(r["tag"].split("-", 1)[1])}</text>')
        s = SIF.get(r['tag'])
        l1 = f'{s[0]} · SIL {s[3]}' if sif and s else r['range']
        l2 = (s[1] + ' -> ' + s[2])[:44] if sif and s else r['signal'][:44]
        o.append(f'<text x="{bx + 38}" y="{by - 2}" font-size="7">{_esc(l1[:34])}</text>')
        o.append(f'<text x="{bx + 38}" y="{by + 8}" font-size="6.5" fill="#555">{_esc(l2)}</text>')
    # ---- unit box
    o.append(f'<rect x="{BL}" y="{yb0}" width="{BR - BL}" height="{yb1 - yb0}" rx="10" fill="#f6f6f6" '
             'stroke="#111" stroke-width="2"/>')
    o.append(f'<text x="{(BL + BR) / 2}" y="{yb0 + 26}" font-size="15" font-weight="700" '
             f'text-anchor="middle">{_esc(u)}</text>')
    o.append(f'<text x="{(BL + BR) / 2}" y="{yb0 + 42}" font-size="9.5" text-anchor="middle">'
             f'{_esc(n.get("class", ""))} · {_esc(n.get("sector_id", ""))} sector</text>')

    # ---- edges
    def draw_edge(e, y, inp):
        xa, xb = (XL, BL - 4) if inp else (BR + 4, XR)
        o.append(f'<line x1="{xa}" y1="{y}" x2="{xb - 9}" y2="{y}" {_style(e)} '
                 f'class="{"edge-in" if inp else "edge-out"}"/>')
        o.append(f'<polygon points="{xb},{y} {xb - 9},{y - 4} {xb - 9},{y + 4}" '
                 f'fill="{"#999" if e.get("presence") != "present" else "#111"}"/>')
        lx = 24 if inp else W - 24
        an = 'start' if inp else 'end'
        other = e['from_unit_id'] if inp else e['to_unit_id']
        rate = _frate(e) + ' · ' + _fll(e, ll) + ('' if e.get('presence') == 'present' else ' · absent')
        o.append(f'<text x="{lx}" y="{y - 19}" font-size="9" fill="#666" text-anchor="{an}">{_esc(other)}</text>')
        o.append(f'<text x="{lx}" y="{y - 5}" font-size="11" font-weight="600" text-anchor="{an}">'
                 f'{_esc(e["stream_id"])}</text>')
        o.append(f'<text x="{lx}" y="{y + 13}" font-size="10" text-anchor="{an}">{_esc(rate)}</text>')
        if noz.get(e['stream_id']):
            o.append(f'<text x="{BL + 8 if inp else BR - 8}" y="{y + 4}" font-size="8" font-style="italic" '
                     f'fill="#555" text-anchor="{"start" if inp else "end"}">{_esc(noz[e["stream_id"]])}</text>')
        seg = xb - xa
        for (sid, item), (qty, size) in sorted(valves.items()):
            if sid != e['stream_id']:
                continue
            o.extend(_valve_sym(xa + seg * (_CHK_POS if item == 'check valve' else _ISOL_POS),
                                y, item, qty, size, inp))
        r = ft_on_edge.get(e['stream_id'])
        if r:
            fx = xa + seg * _FT_POS
            o.append(f'<circle cx="{fx}" cy="{y}" r="12" fill="white" stroke="#111" stroke-width="1.3"/>')
            o.append(f'<text x="{fx}" y="{y + 3}" font-size="7" text-anchor="middle">'
                     f'{_esc(r["tag"].split("-", 1)[1])}</text>')

    for i, e in enumerate(ein):
        draw_edge(e, y0 + i * PITCH, True)
    for i, e in enumerate(eout):
        draw_edge(e, y0 + i * PITCH, False)
    # ---- notes + title block
    notes = [f'Every incident graph edge is drawn: {len(ein)} in, {len(eout)} out. Cables and solids '
             'transfers carry no DN (line list rows cable/solids).',
             'Sources: AQS-PIP-004 line list; AQS-CTL-001 instrument index; AQS-INV-005 valve inventory; '
             'AQS-CTL-003 cause and effect'
             + (f'; nozzles/{u}.csv.' if noz_rows else f'; no nozzle schedule for {u} yet (unit task 04).')]
    if unplaced_v:
        notes.append('Valves not on a unit edge (inventory basis names no incident stream): ' + '; '.join(
            f'{v["item"]} {v["size"]} ({v["basis"]})' for v in unplaced_v[:6])
            + (' ...' if len(unplaced_v) > 6 else ''))
    if noz_rows:
        miss_n = [f'{r["tag"]} {r["service"]}' for r in noz_rows if r['tag'] not in noz.values()]
        if miss_n:
            notes.append('Nozzles with no matching graph edge (service text): '
                         + '; '.join(miss_n[:8]) + (' ...' if len(miss_n) > 8 else ''))
    notes.append('Study. Not a PE stamp. Symbols per ISA-5.1-2022 and ISO 10628-2 intent; sheet format '
                 'per AQS-DWG-001.')
    H = max(yb1 + 40, 176 + nb_rows * 64 + 40) + len(notes) * 15 + 160
    o[0] = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="sans-serif">'
    o[1] = f'<rect x="4" y="4" width="{W - 8}" height="{H - 8}" fill="white" stroke="#111"/>'
    ny = H - 140 - len(notes) * 15
    o.append(f'<text x="24" y="{ny - 10}" font-size="10" font-weight="600">Notes</text>')
    o += [f'<text x="24" y="{ny + 15 * i}" font-size="9">{_esc(t)}</text>' for i, t in enumerate(notes)]
    rev = hashlib.sha256('\n'.join(o).encode()).hexdigest()[:8]
    tb = [f'Aqueous Solutions (owner)   AQS-PID-001-{u}',
          f'P&amp;ID {_esc(u)} ({_esc(n.get("class", ""))}, {_esc(n.get("sector_id", ""))} sector)',
          f'Type: P&amp;ID (ISO_10628_2)   Rev {rev}   Issued {_PID_DATE}',
          'Created: flow graph pipeline   Approved: not approved (study)',
          f'Graph Rev {GREV}   Sheet 1 of 1   AQS-DWG-001']
    x, y, w, h = W - 384, H - 118, 360, 96
    tbg = [f'<g id="aqs-title-block"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="white" '
           'stroke="black" stroke-width="1"/>']
    tbg += [f'<text x="{x + 8}" y="{y + 17 + 17 * i}" font-size="9">{t}</text>' for i, t in enumerate(tb)]
    tbg.append('</g>')
    svg = '\n'.join(o) + '\n' + '\n'.join(tbg) + '</svg>\n'
    row = dict(unit=u, drawing=f'AQS-PID-001-{u}', rev=rev, file=f'docs-authority/pid/{u}.svg',
               sector=n.get('sector_id', ''), unit_class=n.get('class', ''),
               edges_in=len(ein), edges_out=len(eout),
               valves_placed=sum(v[0] for v in valves.values()), valves_unplaced=len(unplaced_v),
               instruments=len(inst), sifs=n_sif, nozzles=len(noz_rows))
    return svg, row


def pid_units(m):
    """The P&ID census: every present non-boundary unit, unit_id-sorted (the
    v1 UNITS set; graph-derived coverage)."""
    return sorted(n['unit_id'] for n in m.data.get('nodes', [])
                  if n.get('presence') == 'present' and n.get('class') != 'boundary')


def render_pid_sheet(u):
    """docs-authority/pid/<u>.svg: one unit P&ID sheet."""
    def f(m, inputs):
        ctx, missing = _pid_state(m, inputs)
        if ctx is None:
            return _stub(f'docs-authority/pid/{u}.svg', missing)
        if u not in {n['unit_id'] for n in ctx['g']['nodes']}:
            return _stub(f'docs-authority/pid/{u}.svg', f'the {u} node')
        svg, _row = _sheet(ctx, u)
        return svg.encode('utf-8')
    f.__name__ = f'render_pid_sheet_{u}'
    f.__doc__ = f'docs-authority/pid/{u}.svg: the unit P&ID sheet (AQS-PID-001).'
    return f


def render_pid_register_rows(m, inputs):
    """The AQS-PID-001 register rows, in the sheet census order - the rows
    the pid append keeps in DRAWING_REGISTER.md and the pid register CSV
    serializes. Not a registry entry: the composers consume it."""
    ctx, _missing = _pid_state(m, inputs)
    if ctx is None:
        return None
    return [_sheet(ctx, u)[1] for u in pid_units(m)]


def render_pid_register_csv(m, inputs):
    """docs-authority/pid/_register.csv: the sheet register (the v1
    DictWriter face over the row dicts, in the census order)."""
    recs = render_pid_register_rows(m, inputs)
    if recs is None:
        return _stub('docs-authority/pid/_register.csv', 'instrument_index')
    return _csv_dict_bytes(recs, list(recs[0].keys()))


def compose_pid_register(lines, rows):
    """The idempotent foreign-row keep (the v1 pid append into
    DRAWING_REGISTER.md, owned by drawings): strip any previous AQS-PID rows,
    recount the count line over the drawings rows, re-insert the provenance
    note under the count line, append the rows. Whichever of the two writers
    ran last, the register reads the same."""
    out = [l for l in lines if not l.startswith('| AQS-PID-')]
    base = sum(1 for l in out if l.startswith('| AQS-'))
    out = [re.sub(r'^\d+ drawings\.', f'{base + len(rows)} drawings.', l) for l in out]
    out = [l for l in out if not l.startswith('The AQS-PID-001 series')]
    if _PID_PROV not in out:
        out.insert(next(i for i, l in enumerate(out) if l.startswith('| Number |')) - 1, _PID_PROV)
    out += [f"| {r['drawing']} | P&amp;ID {r['unit']} | P&amp;ID (ISO_10628_2) | {r['rev']} | "
            f"{r['file']} |" for r in rows]
    return out


# ---- AQS-DWG-002: the drawing register and the title-block stamp ------------------

def stamp(svg, number, title, kind, graph_sha=None):
    """The title-block stamp composer (the v1 _drawings.py stamp()): strip
    any existing `aqs-title-block` group, take the revision as the first 8
    hex of the SHA-256 of the stripped content, re-stamp the ISO_7200 block
    lower right, inserted before the closing tag. The views drawings carry
    the graph SHA (X-DWG-03). Pure text in, text out."""
    stripped = _TB.sub('', svg)
    rev = hashlib.sha256(stripped.encode()).hexdigest()[:8]
    m = re.search(r'viewBox="([-0-9.]+)[ ,]+([-0-9.]+)[ ,]+([-0-9.]+)[ ,]+([-0-9.]+)"', svg)
    if m:
        x0, y0, W, H = (float(x) for x in m.groups())
    else:
        w = re.search(r'<svg[^>]*width="([0-9.]+)', svg)
        h = re.search(r'<svg[^>]*height="([0-9.]+)', svg)
        x0, y0 = float('0'), float('0')
        W = float(w.group(1)) if w else float('800')
        H = float(h.group(1)) if h else float('600')
    s = max(float('0.6'), min(W, H) / 900)
    w, h = 360 * s, 96 * s
    x, y = x0 + W - w - 4 * s, y0 + H - h - 4 * s
    f = 9 * s
    rows = [f'Aqueous Solutions (owner)   {number}', title[:60],
            f'Type: {kind}   Rev {rev}   Issued {_DWG_DATE}',
            'Created: flow graph pipeline   Approved: not approved (study)',
            (f'Graph SHA-256 {graph_sha[:16]}   ' if graph_sha else '') + 'Sheet 1 of 1   AQS-DWG-001']
    t = ''.join(f'<text x="{x + 6 * s:.1f}" y="{y + (16 + 17 * i) * s:.1f}" '
                f'font-family="sans-serif" font-size="{f:.1f}">'
                f'{r.replace("&", "&amp;").replace("<", "&lt;")}</text>' for i, r in enumerate(rows))
    g = (f'\n<g id="aqs-title-block"><rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
         f'fill="white" stroke="black" stroke-width="{s:.2f}"/>{t}</g>\n')
    i = stripped.rfind('</svg>')
    return stripped[:i] + g + stripped[i:]


def _drawing_inventory(m, inputs):
    """The stamped-drawing inventory (the v1 files() over the payload): rows
    of (number, title, kind, file, from_graph) in the v1 glob order -
    `from_graph` marks the flow diagrams, whose title block carries the graph
    SHA (X-DWG-03). Revisions are not carried: they are the SHA-256[:8] of
    the payload SVG content without its title block, taken at render time."""
    svgs = inputs.get('drawing_svgs')
    steps = inputs.get('drawing_steps')
    if svgs is None or steps is None:
        return None
    reg = []
    _VIEW_TITLES = {'pfd': 'Process flow diagram', 'mfd': 'Mass flow diagram',
                    'efd-elec': 'Electrical flow diagram', 'efd-ess': 'Energy storage flow diagram',
                    'efd-thermal': 'Thermal flow diagram'}
    for f in sorted(k for k in svgs if k.startswith('flow_graph/views/')):
        b = f.split('/')[-1][:-4]
        reg.append((f'AQS-DWG-PFD-{b.upper()}', _VIEW_TITLES.get(b, b),
                    'flow diagram (ISO_10628_2)', f, True))
    for f in sorted(k for k in svgs if k.startswith('models/motors/')):
        mf = f.split('/')[-3]
        reg.append((f'AQS-INV-005-{mf}', f'Motor family {mf} assembly', 'assembly drawing', f, False))
    # AQS-PLAN-006 W7 fabrication drawing sets. The title carries the graph
    # revision - the model source (models/mfg/<unit>/params.json) is the
    # authority, so from_graph stays False (the content-hash revision governs
    # per ASME_Y14_35).
    grev = m.data.get('revision')
    for f in sorted(k for k in svgs if k.startswith('models/mfg/')):
        parts = f.split('/')
        mf = parts[-3]
        b = f.split('/')[-1][:-4].upper()
        reg.append((f'AQS-MFG-{mf}-{b}',
                    f'{mf} fabrication drawing {b} (AQS-PLAN-006 M3; graph Rev {grev})',
                    'fabrication drawing (GA / nozzle orientation / part sheet)', f, False))
    for f in sorted(steps):
        u = f.split('/')[-3]
        reg.append((f'AQS-MFG-{u}', f'{u} fabrication model (STEP, model-based definition)',
                    '3D model', f, False))
    return reg


def render_drawings_register(m, inputs):
    """docs-authority/DRAWING_REGISTER.md (AQS-DWG-002): the drawings-series
    rows over the payload inventory, with the AQS-PID rows kept (the
    foreign-row keep rule - the register is identical whichever of the two
    writers ran last; render_pid_register_rows supplies the kept rows and
    compose_pid_register is the same composition from the pid side)."""
    reg = _drawing_inventory(m, inputs)
    if reg is None:
        return _stub('docs-authority/DRAWING_REGISTER.md', 'drawing_svgs')
    svgs = inputs['drawing_svgs']
    md = ['# Drawing register', '', 'Document number: AQS-DWG-002', 'Revision: A',
          f'Date: {_DWG_DATE}',
          'Authority: AQS-PLAN-007 X-DWG-02 under the drawing standard AQS-DWG-001. Generated by '
          '`docs-authority/_drawings.py`. Study.', '',
          f'{len(reg)} drawings. Revision for SVG drawings is the content hash in the title block '
          '(AQS-DWG-001 section 4); "git" is the file history; "graph" is the graph manifest '
          '(media/_generated.json).', '',
          '| Number | Title | Type | Revision | File |', '|---|---|---|---|---|']
    for num, title, kind, path, _fg in reg:
        rev = 'git' if kind == '3D model' else \
            hashlib.sha256(_TB.sub('', svgs[path]).encode()).hexdigest()[:8]
        md.append(f'| {num} | {title} | {kind} | {rev} | {path} |')
    # Rows of series owned by other generators (P&ID sheets) are kept as they
    # are, so the register is the same whichever of the two generators ran last.
    pid_rows = render_pid_register_rows(m, inputs)
    if pid_rows is None:
        return _stub('docs-authority/DRAWING_REGISTER.md', 'instrument_index')
    md = [re.sub(r'^\d+ drawings\.', f'{len(reg) + len(pid_rows)} drawings.', l) for l in md]
    notes = [_PID_PROV]
    i = md.index('| Number | Title | Type | Revision | File |')
    md = md[:i - 1] + notes + md[i - 1:]           # same place _pid_sheets.py puts it
    return ('\n'.join(md + [f"| {r['drawing']} | P&amp;ID {r['unit']} | P&amp;ID (ISO_10628_2) | "
                            f"{r['rev']} | {r['file']} |" for r in pid_rows]) + '\n').encode('utf-8')


# ---- the declared registry block (chain order: line list -> routes -> nozzles
#      -> pid -> drawings; the views wave stays the registry tail) --------------

_NOZZLE_UNITS = (
    'ABE', 'ACETOX', 'ACEX', 'ACID_PLANT', 'ACID_POLISH_SCRUB', 'AFTERBURNER',
    'AFTERBURNER_FLUE', 'AIR_RECEIVER', 'ALD', 'ALK_SCRUBBER', 'AL_POT', 'AMF', 'ANIMAL_PEN',
    'AQUA_TANK', 'AQUA_UV', 'ASH', 'ATMOS', 'AZOLLA', 'AZOLLA_BED', 'BACKUP_GEN', 'BAGHOUSE',
    'BEES', 'BEE_HIVE', 'BIOFILTER', 'BLACK_DIGEST', 'BLOW', 'BLOW_MOLD', 'BMED_ACID',
    'BMED_BASE', 'BMED_UPW_POLISH', 'BOARD_MILL', 'BOUNDARY_EXPORT', 'BRINE_CRYS', 'BSFL',
    'BSFL_BIN', 'BUCL', 'BUOH_STILL', 'C29_RECYCLE', 'CAST_LINE', 'CATCH_TANK', 'CA_POT',
    'CHICKENS', 'CHICKEN_COOP', 'CLARIFIER', 'CLOVER', 'COLD_MILL', 'COMB_HEAT', 'COMPOST',
    'COMPOST_MYC', 'COMPOST_TOILET', 'CONTINUOUS_RECYCLE', 'CONT_CAST', 'CRAYFISH',
    'CROP_ALLIUM', 'CROP_BASIL', 'CROP_CUCUMBER', 'CROP_KALE', 'CROP_LETTUCE', 'CROP_PEPPER',
    'CROP_ROSEMARY', 'CROP_SPINACH', 'CROP_TOMATO', 'CRU', 'CRYO_AHU',
    'CRYO_AHU_COND_CONDENSABLE', 'CRYO_AR', 'CRYO_ASU', 'CRYO_CO2', 'CRYO_DED_COOL',
    'CRYO_H2', 'CRYO_HE', 'CRYO_HX_Q4', 'CRYO_KR', 'CRYO_N2', 'CRYO_NE', 'CRYO_O2', 'CRYO_XE',
    'CR_CELL', 'CURTAIL', 'DIGESTER', 'DRAW', 'DRY_COOLER', 'DUAL_ROOT', 'DUCKWEED',
    'DUCK_PEN', 'ELCOAT', 'ELECTRODE_COAT', 'EMETH', 'ETOH_STILL', 'EVAP_ACID',
    'EVAP_ACID_VS', 'EVAP_BASE', 'EW_1', 'EW_2', 'EW_3', 'EW_4', 'EW_5', 'EW_6', 'EW_7',
    'EW_8', 'EW_9', 'EXPANDER', 'EXTRUDE', 'FAB_UPW_TANK', 'FEED_PREP', 'FILM_CAST', 'FISH',
    'FISH_SUMP', 'FLOAT_SINK', 'FLUE_KO', 'FLUX_PREP', 'FOOD_STORE', 'FORM', 'FORM_RX',
    'FRUIT_GUTTER', 'FUEL_CELL', 'F_RECOVER', 'GALLEY', 'GAS_ATOMIZER', 'GEO_GHEX', 'GEO_HP',
    'GEO_HP_CLOSED_LOOP', 'GEO_ORC', 'GLASS_BURNOUT', 'GLASS_DIGEST', 'GLASS_MILL',
    'GLASS_RINSE', 'GLYOXAL', 'GOATS', 'GREASE_CA', 'GREASE_LI', 'GREY_TREAT', 'GROWBED_A',
    'GROWBED_B', 'GROW_BED', 'GW_INTAKE', 'H2O_ELYZ', 'H2_DRYER', 'HABITATION', 'HAB_GALLEY',
    'HAB_MED', 'HAB_SLEEP', 'HAB_WASH', 'HDR_CO2', 'HDR_H2', 'HDR_N2', 'HDR_O2', 'HDR_UPW',
    'HEAT_SINK', 'HF_GEN', 'HNO3', 'HOPPER', 'HTC', 'HX8', 'HYDRO_SET', 'IMID', 'IND_MELT',
    'INV_CAST', 'IODIDE', 'LEACH_CSTR_1', 'LIGNO_PRE', 'LITHO', 'LITHO_ALIGN', 'LITHO_COAT',
    'LITHO_DEV', 'LITHO_STUB', 'LI_RECOVER', 'LOAD_AGG', 'MEAM', 'MEOH_COND', 'MEOH_FC',
    'MEOH_FERM', 'MEOH_SYNTH', 'MEOH_TANK', 'METAL_STORE', 'MET_AHU', 'MET_HX_Q4', 'MET_MELT',
    'MET_SCRUB', 'MET_SYN', 'MFG_SHOP', 'MG_POT', 'MISTER', 'MO_CELL', 'MUSHROOM',
    'MUSH_BLOCK', 'MUSH_STRAW', 'NAOH_PLANT', 'NCG_HEADER', 'NFIX_BED', 'NFT', 'NORTH_DOCK',
    'NOX_SCRUB', 'NUTRIENT_DOSE', 'NUT_AN', 'OIL_DRYER', 'OIL_FRAC', 'OIL_PYRO', 'PEANUT',
    'PELLET', 'POLISH_BANK', 'POLY_COND', 'POLY_F', 'POLY_FIBER', 'POLY_OLEFIN', 'POLY_STOCK',
    'POWDER_RESIN', 'PROD_C11_C18', 'PROD_C19_C28', 'PROD_C29', 'PROD_C5_C10', 'PROD_MEOH',
    'PROD_O2', 'PV_ARRAY', 'PV_CELL', 'P_CA', 'Q1_A', 'Q1_B', 'Q2_A', 'Q2_B', 'Q3_A', 'Q3_B',
    'Q4_A', 'Q4_B', 'Q4_BUS', 'QUAIL_CAGE', 'QUAT', 'RABBIT_HUTCH', 'RECTIFIER',
    'REE_RECOVER', 'RELIEF_CRYO', 'RELIEF_H2', 'REMIN', 'RESIST_SYN', 'ROLL', 'ROOF_TANK',
    'S13_CLASS_TREAT', 'SALT_FEED', 'SEED_BANK', 'SHELL_BREAK', 'SHELL_BUILD',
    'SHELL_BURNOUT', 'SIC_FURNACE', 'SINTER', 'SI_REDUCE', 'SI_REFINE', 'SOLAR_PV_CELL',
    'SOLV_PLANT', 'SOL_ARK_60K', 'STOCK_OUT', 'STRUVITE', 'SUNFLOWER', 'TERRACE_IRRIG',
    'TFE_SYN', 'TI_CELL', 'VAC_CAST', 'VAC_IND', 'VCD_TRAIN', 'VDF_SYN', 'VEG_BED',
    'VERMI_BIN', 'WAFER_FAB', 'WASHROOM', 'WAX_PATTERN', 'WET_BENCH', 'WIRE_DRAW', 'WORMS',
    'WS_AMMONIA', 'WS_DOPE', 'WS_HF_ED', 'WS_KOH', 'WS_NITRIC', 'WS_PEROX', 'WS_PHOS',
    'WS_SLURRY', 'WS_SOLV', 'YEAST', 'ZNBR2', 'ZNBR2_BR2_REGEN')

_PID_UNIT_LIST = (
    'ACID_PLANT', 'ACID_POLISH_SCRUB', 'ADS_CHILL', 'AFTERBURNER', 'AFTERBURNER_FLUE',
    'AIR_RECEIVER', 'ALK_SCRUBBER', 'AL_POT', 'AQUA_TANK', 'AQUA_UV', 'BACKUP_GEN',
    'BAGHOUSE', 'BEE_HIVE', 'BIOFILTER', 'BLACK_DIGEST', 'BLOW_MOLD', 'BMED_ACID',
    'BMED_BASE', 'BMED_UPW_POLISH', 'BRINE_CRYS', 'BSFL_BIN', 'C29_RECYCLE', 'CAST_LINE',
    'CATCH_TANK', 'CA_POT', 'CHICKEN_COOP', 'COLD_MILL', 'COMB_HEAT', 'COMMON_AREA',
    'CONTINUOUS_RECYCLE', 'CONT_CAST', 'CRU', 'CRYO_AHU', 'CRYO_AHU_COND_CONDENSABLE',
    'CRYO_ASU', 'CRYO_CO2', 'CRYO_DED_COOL', 'CRYO_H2', 'CRYO_HX_Q4', 'CRYO_N2', 'CRYO_O2',
    'CR_CELL', 'DRAW', 'DRY_COOLER', 'DUCKWEED', 'DUCK_PEN', 'ELECTRODE_COAT', 'EVAP_ACID',
    'EVAP_ACID_VS', 'EVAP_BASE', 'EW_1', 'EW_2', 'EW_3', 'EW_4', 'EW_5', 'EW_6', 'EW_7',
    'EW_8', 'EW_9', 'EXTRUDE', 'EXT_HALL', 'FAB_UPW_TANK', 'FEED_PREP', 'FILM_CAST',
    'FLOAT_SINK', 'FLUE_KO', 'FLUX_PREP', 'FOOD_STORE', 'FORGE', 'FUEL_CELL', 'F_RECOVER',
    'GALLEY', 'GAS_ATOMIZER', 'GEO_GHEX', 'GEO_HP', 'GEO_HP_CLOSED_LOOP', 'GLASS_BURNOUT',
    'GLASS_DIGEST', 'GLASS_MILL', 'GLASS_RINSE', 'GREASE_CA', 'GREASE_LI', 'GREY_TREAT',
    'GROWBED_A', 'GROWBED_B', 'GROW_BED', 'GW_INTAKE', 'H2O_ELYZ', 'H2_DRYER', 'HABITATION',
    'HDR_CO2', 'HDR_H2', 'HDR_N2', 'HDR_O2', 'HDR_UPW', 'HF_GEN', 'HOPPER', 'HX8',
    'HYDRO_SET', 'IND_MELT', 'INV_CAST', 'LEACH_CSTR_1', 'LITHO_ALIGN', 'LITHO_COAT',
    'LITHO_DEV', 'LI_RECOVER', 'LOAD_AGG', 'MAU_HX', 'MEDICAL', 'MEOH_COND', 'MEOH_FC',
    'MEOH_FERM', 'MEOH_SYNTH', 'MEOH_TANK', 'METAL_STORE', 'MET_AHU', 'MET_HX_Q4', 'MET_MELT',
    'MET_SCRUB', 'MET_SYN', 'MFG_SHOP', 'MG_POT', 'MO_CELL', 'NAOH_PLANT', 'NCG_HEADER',
    'NOX_SCRUB', 'NUTRIENT_DOSE', 'NUT_AN', 'OIL_DRYER', 'OIL_FRAC', 'OIL_PYRO', 'PELLET',
    'POLISH_BANK', 'POLY_COND', 'POLY_F', 'POLY_FIBER', 'POLY_OLEFIN', 'POLY_STOCK',
    'POWDER_RESIN', 'PROD_C11_C18', 'PROD_C19_C28', 'PROD_C29', 'PROD_C5_C10', 'PROD_MEOH',
    'PROD_O2', 'PV_ARRAY', 'P_CA', 'Q1_A', 'Q1_B', 'Q2_A', 'Q2_B', 'Q3_A', 'Q3_B', 'Q4_A',
    'Q4_B', 'Q4_BUS', 'QUAIL_CAGE', 'RABBIT_HUTCH', 'RECTIFIER', 'REC_DAYROOM', 'REE_RECOVER',
    'RELIEF_CRYO', 'RELIEF_H2', 'REMIN', 'RESIST_SYN', 'RES_HEAT', 'RF_HEAT', 'ROLL',
    'ROOF_TANK', 'SALT_FEED', 'SHELL_BREAK', 'SHELL_BUILD', 'SHELL_BURNOUT', 'SINTER',
    'SI_REDUCE', 'SI_REFINE', 'SLEEP_QUARTERS', 'SOLAR_PV_CELL', 'SOLV_PLANT', 'SOL_ARK_60K',
    'STOCK_OUT', 'TFE_SYN', 'TI_CELL', 'VAC_CAST', 'VAC_IND', 'VCD_TRAIN', 'VDF_SYN',
    'VERMI_BIN', 'WAFER_FAB', 'WASHROOM', 'WAX_PATTERN', 'WET_BENCH', 'WIRE_DRAW',
    'WS_AMMONIA', 'WS_DOPE', 'WS_HF_ED', 'WS_KOH', 'WS_NITRIC', 'WS_PEROX', 'WS_PHOS',
    'WS_SLURRY', 'WS_SOLV', 'ZNBR2', 'ZNBR2_BR2_REGEN')


DOCS = (
    # line_list (docs-authority/_line_list.py)
    [('docs-authority/LINE_LIST.md', render_line_list_md)]
    # placement_routes (docs-authority/_placement_routes.py)
    + [('docs-authority/ISO_ROUTES.md', render_iso_routes_md),
       ('docs-authority/ISO_ROUTES.json', render_iso_routes_json),
       ('docs-authority/iso/ISO_SHEETS.csv', render_iso_sheets_csv),
       ('docs-authority/ISO_SHEETS.md', render_iso_sheets_md)]
    # nozzle_sched (docs-authority/_nozzle_sched.py)
    + [(f'docs-authority/nozzles/{u}.csv', render_nozzle_csv(u)) for u in _NOZZLE_UNITS]
    # pid_sheets (docs-authority/_pid_sheets.py)
    + [(f'docs-authority/pid/{u}.svg', render_pid_sheet(u)) for u in _PID_UNIT_LIST]
    + [('docs-authority/pid/_register.csv', render_pid_register_csv)]
    # drawings (docs-authority/_drawings.py; the pid rows kept)
    + [('docs-authority/DRAWING_REGISTER.md', render_drawings_register)]
)

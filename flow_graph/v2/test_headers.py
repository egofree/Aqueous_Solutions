"""engine v2: the headers-family acceptance (the golden-value proof).

Reference writer: flow_graph/param/headers.py `--write` (ledger row
`sizing_headers`, section B - the AQS-DUTY-075 header-class units, bore from
the velocity limit). The committed graph carries every field the family
stamps; the proofs:

- exact change set: the family's overlay equals the hand-enumerated
  specification (8 params.design books, 3 reservation fields on each of the
  7 reserved headers: size_note, size_mm, size_basis - 29 node fields, no
  edge stamps: no rates change), and a strict whole-model walk (nodes and
  edges, same JSON types) proves nothing else moved;
- golden equality: every changed field equals the committed golden, numbers
  quantised to the golden's decimals (exact repr equality, zero enumerated
  drift) - including the raw-float design books the family ported as v1
  float books (the foundry precedent);
- the velocity-limit bore audit re-derived on exact Decimal arithmetic: the
  concurrent flow census, Q4_BUS winter duty book, d = sqrt(4Q/(pi v)),
  the DN ladder pick and the bore-x-length volume/holdup identities, per
  unit against the hand-enumerated golden books;
- grid spot-checks: the DN-minus-8 clearance table, the first-fitting-rung
  property, the reservation cross-section (manifold OD vs largest branch OD),
  the layout-length passthrough;
- the driver-tamper table: the velocity limits, the flue service minimum and
  the loop-swing driver move the books through the registered function as
  the exact chain predicts;
- the payload branches: iso_sheets rows set the manifold run (max per line,
  junk rows skipped); the nozzles payload sets the reservation cross-section
  (absent unit -> the v1 absent-file branch);
- the bridge contracts: no driver payload or no site profile records
  nothing; a seed without size_mm takes the 2000 mm default; the
  AFTERBURNER_FLUE envelope note is not this family's field;
- determinism: two runs, byte-identical;
- purity: no float literals and no I/O in the family module.
"""
import ast
import csv
import inspect
import json
import os
from decimal import Decimal, ROUND_HALF_EVEN

from flow_graph.v2.functions import headers as HD
from flow_graph.v2.graph_io import bytes as render, load

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF_GRAPH = os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')
DRIVERS = os.path.join(ROOT, 'flow_graph', 'param', 'drivers.json')
PROFILE = os.path.join(ROOT, 'flow_graph', 'param', 'sites', 'baseline.json')
NOZZLE_DIR = os.path.join(ROOT, 'docs-authority', 'nozzles')

_D = json.load(open(DRIVERS))
_P = json.load(open(PROFILE))
_N = {}
for _u in HD.RESERVATION:
    with open(os.path.join(NOZZLE_DIR, _u + '.csv')) as _f:
        _N[_u] = [r['size'] for r in csv.DictReader(_f)]


def _iso_sheets():
    with open(os.path.join(ROOT, 'docs-authority/iso/ISO_SHEETS.csv'), newline='', encoding='utf-8') as _f:
        return list(csv.DictReader(_f))
INPUTS = {'drivers': _D, 'site_profile': _P, 'nozzles': _N,
          # the ISO_SHEETS sidecar rows: the committed routing lengths the
          # header length book derives from (the canonical declared payload
          # carries them; without them the family books the fallback length)
          'iso_sheets': _iso_sheets()}

PI = Decimal('3141592653589793') / Decimal(10) ** 15
R_GAS = Decimal('8.314462618')
K0 = Decimal('273.15')
BUS_DRAWS = ('HABITATION', 'LEACH_CSTR_1', 'GLASS_DIGEST', 'GEO_GHEX', 'MAU_HX')
HDK = 'HDR.headers-train.'

# The change-set specification: every (unit, field path) the family writes.
DESIGN_UNITS = ['HDR_H2', 'HDR_N2', 'HDR_O2', 'HDR_CO2', 'HDR_UPW', 'Q4_BUS',
                'NCG_HEADER', 'AFTERBURNER_FLUE']
EXPECTED_FIELDS = [(u, 'params.design') for u in DESIGN_UNITS] + [
    (u, 'params.' + f) for u in HD.RESERVATION for f in ('size_note', 'size_mm', 'size_basis')]
EXPECTED_EDGES = []                                            # no rates change on the graph

# The hand-enumerated golden design books (from the committed graph; the
# length and volume books moved with the ISO_SHEETS routing rows at the P4
# payload completion, and the reservation cross-sections with the nozzle
# payload).
GOLDEN = {
    'HDR_H2':  dict(DN=25, id_req='4.9', flow='0.0', Q='0.0002', vol='0.0054', hold='0.0',
                    conn=18, rho='0.084', vel='8.0', duty=None),
    'HDR_O2':  dict(DN=25, id_req='8.1', flow='0.0005', Q='0.0004', vol='0.0083', hold='0.01',
                    conn=8, rho='1.2041', vel='8.0', duty=None),
    'HDR_N2':  dict(DN=32, id_req='17.3', flow='0.0023', Q='0.0019', vol='0.0202', hold='0.02',
                    conn=8, rho='1.2041', vel='8.0', duty=None),
    'HDR_CO2': dict(DN=25, id_req='2.0', flow='0.0', Q='0.0', vol='0.0066', hold='0.01',
                    conn=5, rho='1.84', vel='8.0', duty=None),
    'HDR_UPW': dict(DN=25, id_req='0.8', flow='0.0008', Q='0.0', vol='0.0074', hold='7.24',
                    conn=3, rho='983', vel='1.5', duty=None),
    'Q4_BUS':  dict(DN=32, id_req='18.1', flow='0.3778', Q='0.0004', vol='0.0168', hold='16.48',
                    conn=17, rho='983', vel='1.5', duty='15.8144'),
    'NCG_HEADER': dict(DN=25, id_req='4.3', flow='0.0001', Q='0.0001', vol='0.006', hold='0.0',
                       conn=2, rho='0.5', vel='8.0', duty=None),
    'AFTERBURNER_FLUE': dict(DN=100, id_req='18.3', flow='0.0016', Q='0.0021', vol='0.2971',
                             hold='0.22', conn=3, rho='0.75', vel='8.0', duty=None),
}
SIZE_GOLDEN = {'HDR_H2': (2000, '60.3'), 'HDR_N2': (2000, '60.3'), 'HDR_O2': (2000, '60.3'),
               'HDR_CO2': (2000, '33.7'), 'HDR_UPW': (2000, '33.7'), 'Q4_BUS': (2000, '42.4'),
               'NCG_HEADER': (2000, '33.7')}
# The routed layout lengths (the ISO_SHEETS route metres the family books;
# landed by the P4 payload completion).
LEN_GOLDEN = {'HDR_H2': Decimal('23.6'), 'HDR_O2': Decimal('36.4'), 'HDR_N2': Decimal('44.7'),
              'HDR_CO2': Decimal('29.2'), 'HDR_UPW': Decimal('32.5'), 'Q4_BUS': Decimal('37.1'),
              'NCG_HEADER': Decimal('26.4'), 'AFTERBURNER_FLUE': Decimal('44.7')}


def run(inputs=None):
    b = load(REF_GRAPH)
    HD.headers_bore(b, inputs if inputs is not None else INPUTS)
    return b


def committed():
    with open(REF_GRAPH, encoding='utf-8') as f:
        return json.load(f)


def dex(x):
    return Decimal(str(x))


def dv(drv, key):
    return dex(drv[HDK + key]['value'])


def qe(x, dp):
    """Half-even quantise of an exact value at dp decimals (the audit's quantise)."""
    return Decimal(x).quantize(Decimal(1).scaleb(-dp), rounding=ROUND_HALF_EVEN)


def _num_eq(gold, got):
    return Decimal(str(gold)).normalize() == Decimal(str(got)).normalize()


def _eq(gold, got):
    if isinstance(gold, dict):
        return isinstance(got, dict) and set(gold) == set(got) and all(_eq(v, got[k]) for k, v in gold.items())
    if isinstance(gold, list):
        return isinstance(got, list) and len(gold) == len(got) and all(_eq(a, x) for a, x in zip(gold, got))
    if isinstance(gold, (int, float)) and not isinstance(gold, bool):
        return isinstance(got, (int, float)) and not isinstance(got, bool) and _num_eq(gold, got)
    return gold == got


def _dig(obj, path):
    cur = obj
    for part in path.split('.'):
        cur = cur[part]
    return cur


def _strict_diffs(c_obj, r_obj, prefix, out, expected):
    """Paths where the rendered model differs from the committed graph beyond
    the expected change set: strict (same JSON types) everywhere except the
    enumerated fields, where equality at the golden's decimals holds.
    Provenance rows, added by the serializer on touched objects, are excluded."""
    for k in sorted((set(c_obj) | set(r_obj)) - {'provenance'}):
        p = prefix + '.' + k if prefix else k
        if k not in c_obj or k not in r_obj:
            out.add(p)
        elif p in expected:
            if not _eq(c_obj[k], r_obj[k]):
                out.add(p)
        elif isinstance(c_obj[k], dict) and isinstance(r_obj[k], dict):
            _strict_diffs(c_obj[k], r_obj[k], p, out, expected)
        elif isinstance(c_obj[k], list) and isinstance(r_obj[k], list) and len(c_obj[k]) == len(r_obj[k]):
            if any(type(a) is not type(x) or a != x for a, x in zip(c_obj[k], r_obj[k])):
                out.add(p)
        elif type(c_obj[k]) is not type(r_obj[k]) or c_obj[k] != r_obj[k]:
            out.add(p)


def exact_flow(g, u):
    """The concurrent kg/d census as an exact Decimal sum (edge-list order)."""
    tot_in = tot_out = Decimal(0)
    for e in g['edges']:
        r = e.get('rate') or {}
        if e.get('presence') == 'present' and r.get('unit') == 'kg/d' \
                and u in (e['from_unit_id'], e['to_unit_id']):
            v = dex(r.get('value') or 0)
            if e['from_unit_id'] == u:
                tot_out += v
            else:
                tot_in += v
    return max(tot_in, tot_out)


def exact_duty(g):
    """The Q4_BUS winter concurrent branch sum as an exact Decimal."""
    d = Decimal(0)
    for e in g['edges']:
        r = e.get('rate') or {}
        if e.get('presence') == 'present' and r.get('unit') in ('kg/d', 'kW') \
                and e['from_unit_id'] == 'Q4_BUS' and e['to_unit_id'] in BUS_DRAWS:
            d += dex(r.get('value') or 0)
    return d


def exact_air_rho(drv, prof):
    """The air-class density as an exact Decimal chain (open-air branch)."""
    atm = prof['groups']['atmosphere']['entries']
    return dex(atm['pressure_Pa']['value']) * dex(atm['molar_mass_kg_kmol']['value']) / 1000 \
        / (R_GAS * (dv(drv, 'hdr_air_T_C') + K0))


def exact_books(u, drv=None, g=None):
    """The independent exact-Decimal chain for one unit: the concurrent flow,
    d = sqrt(4Q/(pi v)), the DN ladder pick and bore-x-length volume/holdup,
    quantised at the v1 schema points (flow/Q 6 dp, bore 1 dp, volume 4 dp,
    holdup 2 dp, then the blanket 4 dp store on floats)."""
    drv = drv if drv is not None else INPUTS['drivers']
    g = g if g is not None else committed()
    _svc, kind, mink, velk, rhok, _mat, mode = HD.SPEC[u]
    duty = None
    if kind == 'liquid' and mode == 'Q4_BUS':
        duty = exact_duty(g)
        m = duty * 1000 / (dv(drv, 'hdr_cp_water_kJ_kgK') * 1000 * dex(drv['heat_loop_dT_K']['value']))
    else:
        m = exact_flow(g, u) / 86400
    rho = exact_air_rho(drv, INPUTS['site_profile']) if rhok == 'hdr_rho_air' else dv(drv, rhok)
    Q = m / rho
    vel = dv(drv, velk)
    id_req = (4 * Q / (PI * vel)).sqrt() * 1000
    min_dn = int(dv(drv, mink))
    dn = next(d for d in HD.DN_LIST if HD.ID_OF[d] >= id_req and d >= min_dn)
    # the routed layout length: the ISO_SHEETS route metres (the family's raw
    # input, not its rounded length book); the hdr_run_default_m driver is the
    # no-line fallback
    iso = {r['line']: r for r in INPUTS['iso_sheets']}
    runs = [float(iso[e['stream_id']]['route_m']) for e in g['edges']
            if e.get('presence') == 'present' and u in (e['from_unit_id'], e['to_unit_id'])
            and e['stream_id'] in iso and (e.get('rate') or {}).get('unit') in ('kg/d', 'kW')]
    L = Decimal(str(max(runs))) if runs else dv(drv, 'hdr_run_default_m')
    vol = PI * (Decimal(HD.ID_OF[dn]) / 1000) ** 2 / 4 * L
    return dict(m=m, Q=Q, rho=rho, vel=vel, duty=duty, id_req=id_req, dn=dn, L=L, vol=vol,
                hold=vol * rho,
                flow_6=qe(m, 6), Q_6=qe(Q, 6), id_1=qe(id_req, 1), vol_4=qe(vol, 4), hold_2=qe(vol * rho, 2),
                flow_4=qe(qe(m, 6), 4), Q_4=qe(qe(Q, 6), 4))


def books(b):
    """The stored design books of a run: {unit: design dict}."""
    return {u: b.computed[('node', u, 'params.design')][0] for u in DESIGN_UNITS}


def test_exact_change_set_and_golden_equality():
    c = committed()
    c_nodes = {n['unit_id']: n for n in c['nodes']}
    c_edges = {e['stream_id']: e for e in c['edges']}
    b = run()
    out = json.loads(render(b))
    r_nodes = {n['unit_id']: n for n in out['nodes']}
    r_edges = {e['stream_id']: e for e in out['edges']}

    got_nodes = sorted((uid, path) for (kind, uid, path) in b.computed if kind == 'node')
    got_edges = sorted((sid, path) for (kind, sid, path) in b.computed if kind == 'edge')
    assert got_nodes == sorted(EXPECTED_FIELDS), (
        sorted(set(got_nodes) - set(EXPECTED_FIELDS)), sorted(set(EXPECTED_FIELDS) - set(got_nodes)))
    assert got_edges == sorted(EXPECTED_EDGES)

    for uid, path in EXPECTED_FIELDS:
        assert _eq(_dig(c_nodes[uid], path), _dig(r_nodes[uid], path)), (uid, path)
    for sid, path in EXPECTED_EDGES:
        assert _eq(_dig(c_edges[sid], path), _dig(r_edges[sid], path)), (sid, path)

    expected_paths = {uid + '.' + path for uid, path in EXPECTED_FIELDS} \
        | {sid + '.' + path for sid, path in EXPECTED_EDGES}
    diffs = set()
    for uid in sorted(set(c_nodes) | set(r_nodes)):
        _strict_diffs(c_nodes[uid], r_nodes[uid], uid, diffs, expected_paths)
    assert diffs == set(), sorted(diffs)
    for sid in sorted(set(c_edges) | set(r_edges)):
        _strict_diffs(c_edges[sid], r_edges[sid], sid, diffs, expected_paths)
    assert diffs == set(), sorted(diffs)


def test_golden_books_hand_enumerated():
    """The stored books equal the hand-enumerated golden, field by field."""
    bk = books(run())
    for u, gold in GOLDEN.items():
        row = bk[u]
        assert row['DN'] == gold['DN'] and row['connections'] == gold['conn'], u
        assert dex(row['id_req_mm']) == Decimal(gold['id_req']), u
        assert dex(row['flow_kg_s']) == Decimal(gold['flow']), u
        assert dex(row['Q_m3_s']) == Decimal(gold['Q']), u
        assert dex(row['volume_m3']) == Decimal(gold['vol']), u
        assert dex(row['hold_kg']) == Decimal(gold['hold']), u
        assert dex(row['rho_kg_m3']) == Decimal(gold['rho']), u
        assert dex(row['v_m_s']) == Decimal(gold['vel']), u
        assert dex(row['length_m']) == LEN_GOLDEN[u], u
        if gold['duty'] is None:
            assert row['duty_kW'] is None, u
        else:
            assert dex(row['duty_kW']) == Decimal(gold['duty']), u
        assert row['service'] == HD.SPEC[u][0] and row['material'] == HD.SPEC[u][5] \
            and row['kind'] == HD.SPEC[u][1], u


def test_integer_books_keep_their_json_types():
    """The integer books stay JSON integers (the v1 passthrough semantics):
    DN and the connections census stay integers; the routed layout length is
    a float book (the ISO_SHEETS route metres, one decimal); the reservation
    carries float OD crosses; the water density driver book stays an
    integer."""
    b = run()
    out = json.loads(render(b))
    nodes = {n['unit_id']: n for n in out['nodes']}
    for u, row in books(b).items():
        assert type(row['DN']) is int and type(row['connections']) is int and type(row['length_m']) is float, u
    for u in ('HDR_UPW', 'Q4_BUS'):
        assert type(nodes[u]['params']['design']['rho_kg_m3']) is int
    assert type(nodes['Q4_BUS']['params']['design']['duty_kW']) is float
    for u, (length_mm, cross) in SIZE_GOLDEN.items():
        mm = nodes[u]['params']['size_mm']
        assert type(mm[0]) is int and mm[0] == length_mm, u
        assert type(mm[1]) is float and dex(mm[1]) == Decimal(cross), u
        assert mm[1] == mm[2], u


def test_velocity_limit_bore_audit_on_exact_decimal():
    """The bore chain re-derived exactly: the concurrent flow census, the
    Q4_BUS duty book over the loop swing, d = sqrt(4Q/(pi v)), the first
    fitting DN rung and the bore-x-length volume/holdup identities - each
    against the hand-enumerated golden and the stored book."""
    bk = books(run())
    for u, gold in GOLDEN.items():
        eb = exact_books(u)
        assert eb['dn'] == gold['DN'], u                        # the ladder pick
        assert eb['id_1'] == Decimal(gold['id_req']), u
        assert eb['flow_4'] == dex(bk[u]['flow_kg_s']), u
        assert eb['Q_4'] == dex(bk[u]['Q_m3_s']), u
        assert eb['vol_4'] == dex(bk[u]['volume_m3']), u
        # the family books hold from its float product; at a .xx5 boundary the
        # exact Decimal chain rounds the other way (the routed lengths moved
        # HDR_UPW onto one), so the identity holds within the last cent
        assert abs(eb['hold_2'] - dex(bk[u]['hold_kg'])) <= Decimal('0.01'), u
        if eb['duty'] is not None:
            assert eb['duty'] == dex(bk[u]['duty_kW']), u
        # the first-fitting-rung property: no earlier rung carries the required bore
        min_dn = int(dv(INPUTS['drivers'], HD.SPEC[u][2]))
        for d in (d for d in HD.DN_LIST if d < eb['dn'] and d >= min_dn):
            assert HD.ID_OF[d] < eb['id_req'], (u, d)
    # the DN-minus-8 clearance table holds over the whole ladder
    for d in HD.DN_LIST:
        assert HD.ID_OF[d] == d - 8
    # Q4_BUS: duty / (cp x swing) closes on the stored flow
    eb = exact_books('Q4_BUS')
    assert eb['duty'] == Decimal('15.8144')                     # life + HX-9 + HX-10 + GHEX + MAU
    assert eb['m'] == eb['duty'] * 1000 / (Decimal('4.186') * 1000 * Decimal('10.0'))
    # the reservation cross-section: manifold OD vs the largest branch OD
    nozz = INPUTS['nozzles']
    for u, (_length, cross) in SIZE_GOLDEN.items():
        branch = max([dex(HD.DN_OD[s]) for s in nozz[u] if s in HD.DN_OD] or [Decimal(0)])
        od = dex(HD.DN_OD['DN' + str(bk[u]['DN'])])
        assert dex(cross) == max(od, branch), u


def test_grid_spot_checks():
    """The reservation books: the layout length is carried through, the note
    and basis strings match the v1 literals, and the flue junction - not a
    reserved header - carries no reservation at all."""
    b = run()
    for u, (length_mm, cross) in SIZE_GOLDEN.items():
        note = b.computed[('node', u, 'params.size_note')][0]
        basis = b.computed[('node', u, 'params.size_basis')][0]
        dn = books(b)[u]['DN']
        vol = books(b)[u]['volume_m3']
        run_m = round(LEN_GOLDEN[u])                       # the note's rounded run (half-even)
        assert note == f'DN{dn} manifold x {run_m} m run ({vol:.3f} m3), {HD.TAG}', u
        assert basis == (f'{HD.TAG}: manifold DN{dn} segment (modelled length {length_mm} mm, layout) with '
                         f'the cross-section covering the largest issued branch hardware ({cross} mm, '
                         'EN-rounded OD series, AQS-PIP-004)'), u
    got = sorted((uid, path) for (kind, uid, path) in b.computed if kind == 'node'
                 and uid == 'AFTERBURNER_FLUE')
    assert got == [('AFTERBURNER_FLUE', 'params.design')]       # design only: the envelope note is not ours


def with_driver(key, val):
    """The drivers with one value overridden (the key may be flat or prefixed)."""
    drv = json.loads(json.dumps(INPUTS['drivers']))
    drv[key if key.startswith('heat_') else HDK + key]['value'] = val
    return drv


def test_driver_tamper_table():
    """The velocity limits, the flue service minimum and the loop swing move
    the books through the registered function as the exact chain predicts -
    expected books from the exact chain, never scaled from the stored floats."""
    def run_drv(drv):
        bb = run({'drivers': drv, 'site_profile': INPUTS['site_profile'], 'nozzles': INPUTS['nozzles']})
        return bb, books(bb)

    # the gas velocity halved: every gas bore requirement grows by sqrt(2)
    drv = with_driver('hdr_v_gas_m_s', 4.0)
    _bb, bk = run_drv(drv)
    eb = exact_books('HDR_N2', drv=drv)
    assert bk['HDR_N2']['DN'] == eb['dn'] == 40                 # 17.3 x sqrt(2) clears the DN32 rung (ID 24)
    assert dex(bk['HDR_N2']['id_req_mm']) == eb['id_1']
    assert bk['HDR_CO2']['DN'] == 25                            # the service minimum still governs
    assert dex(bk['HDR_CO2']['id_req_mm']) == exact_books('HDR_CO2', drv=drv)['id_1']
    # the flue service minimum raised to DN125: the velocity book stays, the ladder moves
    _bb, bk = run_drv(with_driver('hdr_min_DN_flue', 125))
    assert bk['AFTERBURNER_FLUE']['DN'] == 125
    assert dex(bk['AFTERBURNER_FLUE']['id_req_mm']) == Decimal('18.3')   # the velocity book is untouched
    # the loop swing doubled: the Q4 duty book stands, the flow halves, the bore drops a rung
    drv = with_driver('heat_loop_dT_K', 20.0)
    _bb, bk = run_drv(drv)
    eb = exact_books('Q4_BUS', drv=drv)
    assert bk['Q4_BUS']['DN'] == eb['dn'] == 25                 # 12.8 mm fits the DN25 rung (ID 17)
    assert dex(bk['Q4_BUS']['flow_kg_s']) == eb['flow_4'] == Decimal('0.1889')
    assert dex(bk['Q4_BUS']['duty_kW']) == Decimal('15.8144')   # the winter branch sum, not a dT book


def test_iso_payload_branch():
    """The ISO_SHEETS.csv rows set the manifold run: max route per line over
    the header's present kg/d|kW lines, junk rows skipped; a header without
    routed lines keeps the A-M-306 default run."""
    inp = dict(INPUTS)
    inp['iso_sheets'] = [
        {'line': 'S89', 'route_m': 35.0}, {'line': 'S85', 'route_m': 2.0},
        {'line': 'S90', 'route_m': 40.0},                        # S90 is HDR_CO2's longest line
        {'line': 'S89', 'route_m': 10.0},                        # a second sheet row: max stays 35
        {'line': 'JUNK', 'route_m': 'n/a'},                      # the v1 ValueError pass
        {'route_m': 5.0},                                        # no line id: skipped
        {'line': 'S100', 'route_m': 3.0},                        # a kW branch of Q4_BUS, not HDR_CO2
    ]
    b = run(inp)
    row = b.computed[('node', 'HDR_CO2', 'params.design')][0]
    assert row['length_m'] == 40.0 and dex(row['volume_m3']) == Decimal('0.0091')
    assert b.computed[('node', 'HDR_CO2', 'params.size_note')][0] == \
        'DN25 manifold x 40 m run (0.009 m3), ' + HD.TAG
    assert b.computed[('node', 'HDR_H2', 'params.design')][0]['length_m'] == 20   # no routed lines
    q4 = b.computed[('node', 'Q4_BUS', 'params.design')][0]
    assert q4['length_m'] == 3.0                                 # S100 (Q4_BUS -> LEACH_CSTR_1) routes Q4_BUS alone


def test_nozzles_payload_and_absent_branch():
    """The branch-hardware payload sets the reservation cross-section; a unit
    absent from the payload takes the v1 absent-file branch (manifold OD
    alone); a schedule size outside the OD series books zero (the v1 .get
    default)."""
    inp = dict(INPUTS)
    inp['nozzles'] = {}
    b = run(inp)
    assert b.computed[('node', 'HDR_H2', 'params.size_mm')][0][1] == 33.7   # DN25 manifold OD
    assert b.computed[('node', 'Q4_BUS', 'params.size_mm')][0][1] == 42.4   # DN32 manifold OD
    inp = dict(INPUTS)
    inp['nozzles'] = {'HDR_H2': ['DN50', 'DN15', 'solids']}
    b = run(inp)
    assert b.computed[('node', 'HDR_H2', 'params.size_mm')][0][1] == 60.3   # the DN50 branch governs
    assert b.computed[('node', 'HDR_CO2', 'params.size_mm')][0][1] == 33.7  # absent: the manifold OD alone
    assert 'largest issued branch hardware (60.3 mm' in b.computed[('node', 'HDR_H2', 'params.size_basis')][0]


def test_seed_layout_length_passthrough():
    """size_mm[0] is layout state: carried through from the seed (the basis
    text names it); a seed without size_mm takes the v1 2000 mm default."""
    b = load(REF_GRAPH)
    b.nodes['HDR_H2']['params']['size_mm'] = [1500, 60.3, 60.3]
    HD.headers_bore(b, INPUTS)
    assert b.computed[('node', 'HDR_H2', 'params.size_mm')][0] == [1500, 60.3, 60.3]
    assert '(modelled length 1500 mm, layout)' in b.computed[('node', 'HDR_H2', 'params.size_basis')][0]
    b = load(REF_GRAPH)
    del b.nodes['NCG_HEADER']['params']['size_mm']
    HD.headers_bore(b, INPUTS)
    assert b.computed[('node', 'NCG_HEADER', 'params.size_mm')][0] == [2000, 33.7, 33.7]


def test_bridge_no_payload_records_nothing():
    """The bridge solve / check carry no payloads: the family records nothing
    and the seed stands. Drivers without the profile and the profile without
    drivers each abstain."""
    b = run({})
    assert b.computed == {}
    b = run({'drivers': INPUTS['drivers']})
    assert b.computed == {}
    b = run({'site_profile': INPUTS['site_profile'], 'nozzles': INPUTS['nozzles']})
    assert b.computed == {}


def test_seed_guard_fails_loudly():
    """A seed missing a header-class unit fails loudly instead of writing a
    partial family."""
    b = load(REF_GRAPH)
    b.data['nodes'] = [n for n in b.data['nodes'] if n['unit_id'] != 'HDR_CO2']
    b.nodes.pop('HDR_CO2')
    try:
        HD.headers_bore(b, INPUTS)
    except AssertionError:
        pass
    else:
        raise SystemExit('the missing-unit assert did not fire')


def test_determinism_two_runs_byte_identical():
    assert render(run()) == render(run())


def test_provenance_rows():
    b = run()
    for (kind, uid, path), (value, prov) in b.computed.items():
        assert prov.stage == 'sizing_headers' and prov.basis
        assert prov.ref in ('PERRY9', 'AQS-PIP-004')
        if path == 'params.design':
            assert prov.ref == 'PERRY9'
        else:
            assert prov.ref == 'AQS-PIP-004'


def test_function_module_grid_purity():
    """The engine module holds no float literals and no I/O (the lint's rule)."""
    tree = ast.parse(inspect.getsource(HD))
    floats = [n.lineno for n in ast.walk(tree)
              if isinstance(n, ast.Constant) and isinstance(n.value, float)]
    opens = [n.lineno for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'open']
    assert floats == [] and opens == []

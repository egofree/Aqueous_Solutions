"""The placement-routes family (family migration; reference writer
docs-authority/_placement_routes.py, ledger row `placement_routes`, section F,
RENDER "becomes-renderer (routing calc pure fn)" - the A-M-074 rack routing
kernel ports here; the four documents render in the renderer lane).

X-PIP-03 close-out: every piped line whose both ends carry a sourced
placement routes by the A-M-074 rack rule - rise to the source-level rack
(the level datum + 3200 mm, AQS-PIP-002), X run, Y run, then vertical to the
target centre; risers keep a flexible leg at least 300 mm above the higher
end (X-PIP-06, A-M-127). Fittings: elbow take-off ASME B16.9 long-radius for
metal classes or 0.5 x OD for thermoplastics (A-M-121), 6 m random lengths,
flanges at both nozzles, ASME B16.5 Class 150 bolting, OD per ASME B36.10M.
Lines with an unplaced end are named in the coverage line - a named gap,
never an invented length.

The kernel executes on the line-list namespace
(flow_graph.v2.functions.line_list.rows: the piped rows and their DN/class)
over the placement datums - the v1 stage ran the line-list module via runpy
and read its `C` and `rows`; the centres arrive as the declared
inputs['line_positions'] payload and the datums as inputs['placement_seed']
['datums_mm'] (the views-wave payload key).

Level selection ports the v1 lvl(): the datum whose level is at or below the
centre elevation and closest to it (the odd 1e9 sentinel for levels above the
centre becomes an exact-integer sentinel; same ordering, no float literal).

Float doctrine: the reference writer solves in float space (round(L, 2)
metres, '{:.1f}' cells, f'{c:.0f}' cut lists), so this is a float replica of
that chain over the same books; the constants port as integers (the 3200 mm
rack height, the 300 mm flexible leg, the 6000 mm random length, the OD and
take-off tables as the decimal strings of the v1 literals). Pure: no I/O, no
wall-clock, no RNG.

Golden (test_render_line_list.py): the committed docs-authority/ISO_ROUTES.md,
ISO_ROUTES.json, docs-authority/iso/ISO_SHEETS.csv and ISO_SHEETS.md - byte-exact through the
render lane.
"""
RACK = 3200                                   # datum + rack height, mm (AQS-PIP-002)
MINRISE = 300                                 # X-PIP-06 flexible leg, mm (A-M-127)
RANDOM_M = 6000                               # 6 m random lengths, mm
OD = {15: float('21.3'), 20: float('26.7'), 25: float('33.4'), 32: float('42.2'),
      40: float('48.3'), 50: float('60.3'), 65: float('73.0'), 80: float('88.9'),
      100: float('114.3'), 150: float('168.3'), 200: float('219.1'), 250: float('273.1'),
      300: float('323.9')}                    # ASME B36.10M, mm
B169 = {15: 38, 20: 29, 25: 38, 32: 48, 40: 57, 50: 76, 65: 95, 80: 114, 100: 152,
        150: 229, 200: 305, 250: 381, 300: 457}          # ASME B16.9 LR 90 take-off, mm
BOLT = {15: (4, '1/2'), 20: (4, '1/2'), 25: (4, '1/2'), 32: (4, '1/2'), 40: (4, '1/2'),
        50: (4, '5/8'), 65: (4, '5/8'), 80: (4, '5/8'), 100: (8, '5/8'), 150: (8, '3/4'),
        200: (8, '3/4'), 250: (12, '7/8'), 300: (12, '7/8')}   # ASME B16.5 Cl 150
MAT = {'P1': 'PVC-U Sch 80 ASTM D1785', 'P2': 'CPVC Sch 80 ASTM F441',
       'P3': 'PVDF SDR 21 ISO 10931', 'P4': 'PP-H ISO 15494',
       'P5': 'HDPE PE4710 DR 11 (ASTM D3035)', 'M1': '316L ASTM A312',
       'M2': 'CS ASTM A106 Gr B', 'F1': 'FRP vinyl ester', 'G1': 'borosilicate 3.3'}
JOINT = {'P1': 'solvent', 'P2': 'solvent', 'P3': 'fusion', 'P4': 'fusion', 'P5': 'fusion',
         'M1': 'butt weld', 'M2': 'butt weld', 'F1': 'butt-and-strap', 'G1': 'coupling'}

_ABOVE = 10 ** 9                    # the lvl sentinel: no datum at or below z
HALF_OD = float('0.5')              # thermoplastic elbow take-off, x OD (A-M-121)
LR_FALLBACK = float('1.5')          # off-table DN elbow take-off, x DN (metal)


def lvl(D, z):
    """The routing level of an elevation: the datum at or below z closest to
    it (the v1 lvl(), integer sentinel)."""
    return min(D, key=lambda k: abs(z - D[k]) if z >= D[k] else _ABOVE)


def rack_z(D, z1, z2):
    """The rack elevation of a route: the source-level rack, at least
    MINRISE above the higher end (X-PIP-06)."""
    return max(D[lvl(D, z1)] + RACK, max(z1, z2) + MINRISE)


def route_line(row, ca, cb, D):
    """One piped line routed. Returns (rec, legs_mm): the ISO_SHEETS record
    dict (the v1 rec, its key order the CSV field order) and the signed leg
    list the ISO_ROUTES table prints. `row` is a line-list row (the piped
    rows of the line-list namespace); ca/cb the placed centres."""
    (x1, y1, z1), (x2, y2, z2) = ca[0], cb[0]
    zr = rack_z(D, z1, z2)
    legs = [zr - z1, x2 - x1, y2 - y1, z2 - zr]
    nz = [v for v in legs if abs(v) > 1]
    dn = int(row[3][2:])
    cl = row[4]
    el = max(len(nz) - 1, 0)
    to = B169.get(dn, LR_FALLBACK * dn) if cl.startswith('M') else HALF_OD * OD.get(dn, dn)
    cuts = []
    for i, v in enumerate(nz):
        L = abs(v) - to * ((1 if i > 0 else 0) + (1 if i < len(nz) - 1 else 0))
        while L > RANDOM_M:
            cuts.append(RANDOM_M)
            L -= RANDOM_M
        cuts.append(max(L, 0))
    pipe_m = sum(cuts) / 1000
    nb, bs = BOLT.get(dn, (8, '3/4'))
    joints = 2 * el + (len(cuts) - len(nz)) + 2
    rec = dict(line=row[0], DN=dn, cls=cl, material=MAT.get(cl, cl), frm=row[1], to=row[2],
               route_m=round(sum(abs(v) for v in nz) / 1000, 2), pipe_m=round(pipe_m, 2),
               pieces=len(cuts), cut_list_mm=' '.join(f'{c:.0f}' for c in cuts),
               elbows_90=el, flanges=2, gaskets=2, stud_bolts=2 * nb,
               stud_size=f'{bs} in', joints=joints, joint_type=JOINT.get(cl, '-'))
    return rec, legs


def route_all(rows_, line_positions, D):
    """The whole routed set over the line-list namespace. Returns
    (recs, jrows, miss): the ISO_SHEETS records, the ISO_ROUTES.json rows
    (legs rounded to whole mm, the v1 jrow), and the named coverage gaps.
    Pure."""
    recs, jrows, miss = [], [], []
    for r in rows_:
        if not r[3].startswith('DN'):
            continue
        ca, cb = line_positions.get(r[1]), line_positions.get(r[2])
        if not ca or not cb:
            miss.append(f"{r[0]} ({r[1] if not ca else r[2]} unplaced)")
            continue
        rec, legs = route_line(r, ca, cb, D)
        recs.append(rec)
        (x1, y1, z1), (x2, y2, z2) = ca[0], cb[0]
        zr = rack_z(D, z1, z2)
        mlegs = [round(zr - z1), round(x2 - x1), round(y2 - y1), round(z2 - zr)]
        L = sum(abs(v) for v in mlegs) / 1000
        el = max(sum(1 for v in mlegs if abs(v) > 1) - 1, 0)
        jrows.append({'line': rec['line'], 'dn': rec['DN'], 'class': rec['cls'],
                      'from': r[1], 'to': r[2], 'legs_mm': mlegs, 'length_m': round(L, 1),
                      'elbows': el})
    return recs, jrows, miss


def total_m(recs):
    """The pipe total of a routed set, m (the ISO_SHEETS.md status line)."""
    return sum(x['pipe_m'] for x in recs)

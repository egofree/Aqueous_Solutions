"""The write_graph heat family (family migration; reference writer
flow_graph/param/write_graph.py, command `heat`, ledger row `write_graph_heat`,
PHYSICS). The X-THM-01 store-ledger re-solve (R10b, A-M-259): the heat-ladder
transit by difference (down-only, HEAT_LADDER.md; cross-tie pairs cancel;
standing losses held; Q3 supply-limited so its draws run pro-rata on the rated
profile and the Q3 -> Q4 step carries 0), the Q4 bus close with the GEO_HP
dispatch (AQS-DUTY-010: lift only on deficit), the ZNBR2 cycling heat and its
charge-window book (X-THM-01 F-4, A-M-455), the fuel-cell full-stack heat
credit (X-THM-01 F-11, A-M-383), the dry-cooler terminal closure (F-3,
A-M-454) and the dry-cooler rating from the calculated bounding duty
(F-4, A-M-244 restated, A-M-455). The committed graph carries every field this
family stamps; that committed state is the golden this module reproduces.

Grid doctrine (owner ruling 2026-11-15): driver and seed values arrive as v1
floats and are converted at this boundary by dec() (exact Decimal of the
decimal repr); arithmetic is exact rational/Decimal; schema fields are
quantised half-even (Python round()'s tie rule) at the decimals the v1 schema
stores - 4 dp on every kW rate book, 2 dp for the fan kW and the window books,
1 dp for the daily-energy books. The scale is named at each call.
Dimensionless constants port as integer scaled pairs with the scale in the
name: the AQS-DUTY-008 section 3 rating margin 1.25 -> 125/100, the fan class
0.05 kW_fan/kW_th -> 5/100, the 24 h day, and the v1 float-dust epsilon
1e-6 kW -> 1/1000000. No float literals.

Disposition of the chains around this family (the strangler bridge):
- The ZNBR2 STORE BOOK (store_kWh = P x night, store_in_kWh = store/RT) is
  write_graph_power-family state: v1 re-derived it by calling the grease
  route's pure solve and passing the result to docs-authority/_power_sizing.py
  as an in-memory continuous_kw override (F-20261110-08), because between
  passes the graph carries specialty_sizing's commercial-class grease stamps.
  The power chain (demand census, EW rectifier input, roof close with the
  EXT_HALL extension heat, the roof-fit fixed point) is that family's ledger
  row, so v2 reads the committed book from the seed - ZNBR2 params
  .cycling_thermal, the same read-back v1 itself performs when it sizes the
  dry cooler - and re-derives the window book from the night_hours and
  round-trip drivers. A seed without the book records nothing.
- The EXT_HALL extension heat belongs to the power() command (the roof_close
  chain and the EXT_HALL node stamps), not to the heat command; it enters the
  ZNBR book only through the power family's P above. No heat stamp carries it.
- The dry-cooler fan electrical stamp (continuous_kw) and the airside design
  stay with specialty_sizing, which reads params.rated_kW from the seed
  (X-SPEC lane); this family writes only the rating params it owns.
- Edge topology (creating IA-DC-REJ when the seed lacks it) is builder work:
  the committed graph carries the edge, so the terminal closure asserts the
  seed topology instead of writing it.
- The layer repair (kW-unit ladder edges carry layer thermal) and the Q3
  rated-draw profile seed port as repairs that record only when the seed
  needs them; on the committed seed both are already satisfied and record
  nothing.

The v1 machinery (disk write-back, subprocess spawn, the print ledger check)
does not migrate: assignment replaces the field and its provenance in full,
and the note re-stamp idiom (`split(' | {TAG}')[0]` append, one tag per
writer) ports verbatim as the deterministic string book it is. A solve
without the driver payload records nothing, so the bridge solve and the check
stay byte-faithful to the seed.
"""
import math
from decimal import Decimal, ROUND_HALF_EVEN

from flow_graph.v2.registry import fn

STAGES = 'heat'                                                # family tag in provenance rows
D0, D1 = Decimal(0), Decimal(1)
DAY = Decimal(24)                                              # h, the design-day book
MARGIN = Decimal(125) / Decimal(100)                           # 1.25 rating margin, AQS-DUTY-008 section 3
FAN_CLASS = Decimal(5) / Decimal(100)                          # 0.05 kW_fan/kW_th class (A-M-244 restated)
EPS = Decimal(1) / Decimal(1000000)                            # the v1 float-dust guard on the bus deficit, kW
TAGH = 'X-THM-01 R10b'
TAGZ = 'X-THM-01 F-4'
TAGF = 'X-THM-01 F-11'
R10B = '(A-M-259).'
# F-25 convention made explicit: the A/B pair is N+1 (HEAT_LADDER.md section 3,
# A-M-453). rate.value books the design-day NORMAL state; the single-ladder
# case sizes the hardware and the dry-cooler upset.
F25 = ('N+1 pair (HEAT_LADDER.md section 3, A-M-453): each ladder is full-capacity and either carries the plant '
       'alone. The rate books the design-day normal flow with both ladders on line (HX-8 50/50 split + store trim '
       'per ladder). The single-ladder case (one ladder isolated, all source heat on the other, AQS-DUTY-008 '
       'section 3) sizes the hardware and the dry-cooler upset; it is not a simultaneous flow.')
STALE_DC = 'The DRY_COOLER unit is rated 12 kW to pass the 10.16 kW case with all seasonal branches down.'
RATED_DC = ('The DRY_COOLER unit is rated for the calculated bounding terminal duty (DRY_COOLER params.rated_kW; '
            'A-M-244 restated, A-M-455).')
# the kW-unit ladder edges the ledger counts (thermal + kW; 'mass' on a kW edge is the mislabel)
FAM = ('HL-AFTERBURNER-Q1-A', 'HL-AFTERBURNER-Q1-B', 'HL-GLASS_BURNOUT-Q2-A', 'HL-GLASS_BURNOUT-Q2-B',
       'HL-Q1-A-DOWN', 'HL-Q1-B-DOWN', 'HL-Q2-A-DOWN', 'HL-Q2-B-DOWN', 'HL-Q3-A-DOWN', 'HL-Q3-B-DOWN',
       'HL-Q1-X', 'HL-Q1-X-BA', 'HL-Q2-X', 'HL-Q2-X-BA', 'HL-Q3-X', 'HL-Q3-X-BA', 'HL-Q4-X', 'HL-Q4-X-BA',
       'HL-Q4-A-BUS', 'HL-Q4-B-BUS', 'IA-HX8')
STORE_LINKS = ('HL-Q4-A-BUS', 'HL-Q4-B-BUS')
DRAWS = ('HX4', 'HX5', 'HX6')


def dec(value):
    """A v1 float/int/str -> exact Decimal at the boundary (decimal repr)."""
    return Decimal(str(value))


def q(x, dp):
    """Quantise an exact value to `dp` decimals, half-even - Python round()'s
    documented tie rule, the rounding the v1 writer used; scale named at the
    call. Returns the JSON float the schema stores."""
    f = float(Decimal(x).quantize(D1.scaleb(-dp), rounding=ROUND_HALF_EVEN))
    return float(0) if f == 0 else f                           # no signed zeros in the book


def fmt(x, dp):
    """The f'{x:.dpf}' text of an exact value (half-even at dp)."""
    return f'{Decimal(x).quantize(D1.scaleb(-dp), rounding=ROUND_HALF_EVEN):f}'


def _prov(basis, ref=None):
    from flow_graph.v2.model import Prov
    return Prov(STAGES, basis, ref)


def _set(b, uid, path, value, basis, ref=None):
    b.set_node_field(uid, path, value, _prov(basis, ref))


def _rate(b, sid, value, note, basis, ref=None):
    """The kW rate book on a ladder/bus edge: {value, unit, status, note} in
    the serialized order the committed graph carries."""
    b.set_edge_rate(sid, {'value': value, 'unit': 'kW', 'status': 'study', 'note': note},
                    _prov(basis, ref))


def _edge_field(b, sid, path, value, basis, ref=None):
    """An edge field beyond 'rate' (params.*, layers): the overlay the builder
    records non-rate fields through."""
    b.computed[('edge', sid, path)] = (value, _prov(basis, ref))


def _kw(b, sid):
    """The current kW book of an edge: the family overlay first (the fresh
    stamps of this same pass), the seed rate otherwise; None books 0 (the v1
    `value or 0`)."""
    got = b.computed.get(('edge', sid, 'rate'))
    if got is not None:
        return dec(got[0]['value'])
    val = (b.edges[sid].get('rate') or {}).get('value')
    return dec(val) if isinstance(val, (int, float)) else D0


def _put(b, sid, x, why, basis, ref=None):
    """The v1 put(): the rate value at 4 dp and the note re-stamp - the old
    note up to this writer's tag, then one fresh ` | {TAGH}: why (A-M-259).`
    segment (idempotent, one tag per writer; Cross-stage map 3)."""
    old = (b.edges[sid]['rate'].get('note') or '')
    note = old.split(f' | {TAGH}')[0] + f' | {TAGH}: {why} {R10B}'
    _rate(b, sid, q(x, 4), note, basis, ref)


def _thermal_census(b, side, unit, drop=()):
    """Sum of the thermal kW books at a unit on one side, retired edges
    excluded, `drop` stream ids excluded (the v1 Q4-bus close census)."""
    total = D0
    for e in b.data['edges']:
        sid = e['stream_id']
        if e.get(side) != unit or sid in drop:
            continue
        if e.get('presence') == 'retired' or 'thermal' not in (e.get('layers') or []):
            continue
        if (e.get('rate') or {}).get('unit') != 'kW':
            continue
        total += _kw(b, sid)
    return total


def transit_down(source_kw, loss_kw):
    """One down-transit step: tier source less the standing line loss (kW)."""
    return source_kw - loss_kw


def pro_rata(supply_kw, rated_kw, rated_sum_kw):
    """A supply-limited Q3 draw: the Q3 supply spread pro-rata on the rated
    duty profile (HEAT_LADDER.md Duties; AQS-DUTY-008 Rev B)."""
    return supply_kw * rated_kw / rated_sum_kw


def window_book(kwh_out, kwh_in, night_h, rt):
    """The ZNBR2 charge-window book (X-THM-01 F-4, A-M-455). The charge
    window is the hours the charging source runs: 24 - night_hours at a
    solar-primary portfolio (daylight charging), the full 24 h when the site's
    diverse source charges around the clock - the polar-night profile carries
    night_hours 24 and clamps to the full day (a zero window is never a real
    book). The derivation is field-driven off the night_hours driver; no
    locale name enters it. All values exact (kWh, h, kW)."""
    win = DAY - night_h
    if win <= 0:
        win = DAY
    loss = kwh_in - kwh_out                                    # electrolyte heat, kWh/d
    avg = loss / DAY                                           # kW, the ledger's 24 h average
    win_kw = loss / win                                        # kW, the bounding window rate
    chg = kwh_in / win                                         # kW, the charge electrical rate
    return dict(win_h=win, loss=loss, avg=avg, win_kw=win_kw, chg=chg, rt=rt)


def cooler_rating(dc_in_kw, znbr_avg_kw, znbr_win_kw):
    """The dry-cooler rating case (X-THM-01 F-4, A-M-244 restated, A-M-455):
    the design-day terminal book with the ZNBR2 cycling heat at its
    charge-window rate instead of its average, hardware at the AQS-DUTY-008
    section 3 margin, the fan at the 0.05 kW_fan/kW_th class."""
    bound = dc_in_kw - znbr_avg_kw + znbr_win_kw
    rated = math.ceil(MARGIN * bound)
    fan = FAN_CLASS * rated
    return dict(bound=bound, rated=rated, fan=fan)


@fn('charge_window', 'X-THM-01 F-4: ZNBR2 cycling heat and the charge-window book (A-M-455; round trip '
    'A-M-062/179); store book from the write_graph power family via the seed (F-20261110-08)')
def charge_window(b, inputs):
    drv = inputs.get('drivers')
    if drv is None:
        return
    book = b.nodes.get('ZNBR2', {}).get('params', {}).get('cycling_thermal')
    e = b.edges.get('IA-ZNBR-HEAT')
    if book is None or e is None:
        # the store book is the power family's committed output (P x night at
        # the heat-lane grease override); without it on the seed this family
        # cannot invent the book, so it records nothing
        return
    basis = ('X-THM-01 F-4 ZNBR2 cycling heat (A-M-455; round trip A-M-062/179); store book read from the '
             'write_graph power family via the seed (F-20261110-08)')
    e_out, e_in = dec(book['kwh_d_out']), dec(book['kwh_d_in'])
    wk = window_book(e_out, e_in, dec(drv['night_hours']['value']), dec(drv['storage_round_trip']['value']))
    win, loss, avg = wk['win_h'], wk['loss'], wk['avg']
    rt = str(wk['rt'])
    note = (e['rate'].get('note') or '').split(f' | {TAGZ}')[0] + (
        f' | {TAGZ}: cycling heat from the booked store - {fmt(e_out, 0)} kWh/d out at round trip {rt} '
        f'(A-M-062/179) = {fmt(e_in, 0)} kWh/d charge, loss {fmt(loss, 0)} kWh/d = {fmt(avg, 1)} kW average '
        f'thermal; window thermal rate {fmt(wk["win_kw"], 1)} kW (bounding sizing case: all the daily loss in '
        f'the {fmt(win, 0)} h charge window) against a {fmt(wk["chg"], 1)} kW charge rate over the same window '
        f'(electrolyte thermal-management sizing case; A-M-455). Was the stale 1.67 kW Rev-N 120 kWh-class seed.')
    _rate(b, 'IA-ZNBR-HEAT', q(avg, 4), note, basis, 'A-M-455')
    _set(b, 'ZNBR2', 'params.cycling_thermal', {
        'kwh_d_in': q(e_in, 1), 'kwh_d_out': q(e_out, 1), 'round_trip': float(wk['rt']),
        'loss_kwh_d': q(loss, 1), 'avg_kW': q(avg, 2), 'window_h': float(win),
        'window_kW': q(wk['win_kw'], 2), 'charge_kW_window': q(wk['chg'], 2),
        'basis': (f'store {fmt(e_out, 0)} kWh/d (AQS-ELEC-007 P x night) at round trip {rt} (A-M-062/179): the '
                  f'round-trip difference is electrolyte heat; window_kW is the bounding heat rate with all the '
                  f'daily loss in the {fmt(win, 0)} h charge window; charge_kW_window {fmt(wk["chg"], 1)} kW is '
                  f'the charge electrical rate over the same window; rejected to the Q4 bus on IA-ZNBR-HEAT and '
                  f'the terminal (A-M-455)')}, basis, 'A-M-455')


@fn('fuel_cell_heat', 'X-THM-01 F-11: the fuel-cell heat credit is the physical stack heat - H2 LHV in less '
    'the electric draw (A-M-383 LHV)')
def fuel_cell_heat(b, inputs):
    drv = inputs.get('drivers')
    if drv is None:
        return
    if not all(s in b.edges for s in ('S53', 'S49', 'S51')):
        return
    basis = 'X-THM-01 F-11 full stack heat on the bus (A-M-383 H2 LHV; AQS-DUTY-010)'
    lhv = dec(drv['ELEC.generation-train.BACKUP_GEN.h2_lhv_kWh_kg']['value'])   # kWh/kg, A-M-383
    s49, s51 = _kw(b, 'S49'), _kw(b, 'S51')
    fc_lhv = s49 * lhv / DAY                                   # kW, the H2 feed as LHV heat
    fc_heat = fc_lhv - s51                                     # kW, the physical stack heat
    note = (b.edges['S53']['rate'].get('note') or '').split(f' | {TAGF}')[0] + (
        f' | {TAGF}: full stack heat on the bus - S49 {fmt(s49, 1)} kg/d H2 x {lhv} kWh/kg LHV (A-M-383) / 24 h '
        f'= {fmt(fc_lhv, 3)} kW less the {fmt(s51, 1)} kW electric draw (S51) = {fmt(fc_heat, 3)} kW. '
        f'The previous book credited only the portion above the 45 C Q4 return (x 15/35, 1.1419 kW) and dropped '
        f'the rest of the physical heat; the bus ledger takes the full credit.')
    _rate(b, 'S53', q(fc_heat, 4), note, basis, 'A-M-383')


@fn('heat_ledger', 'X-THM-01 R10b heat-ladder transit by difference, Q3 supply-limited draws, the F-25 N+1 '
    'store-bus book (HEAT_LADDER.md; A-M-259, A-M-453) and the Q4 bus close with the GEO_HP dispatch '
    '(AQS-DUTY-010)')
def heat_ledger(b, inputs):
    drv = inputs.get('drivers')
    if drv is None:
        return
    basis = 'X-THM-01 R10b ladder transit by difference (A-M-259; HEAT_LADDER.md); AQS-DUTY-008 section 3 rates'
    for s in FAM:   # kW-unit ladder edges carry layer thermal; 'mass' on a kW edge is the mislabel
        e = b.edges.get(s)
        if e is not None and 'thermal' not in (e.get('layers') or []):
            fixed = ['thermal'] + [l for l in (e.get('layers') or []) if l != 'mass']
            _edge_field(b, s, 'layers', fixed,
                        'X-THM-01 R10b layer repair (A-M-259): kW-unit ladder edges carry layer thermal', 'A-M-259')
    for a in ('A', 'B'):
        _put(b, f'HL-Q1-{a}-DOWN', transit_down(_kw(b, f'HL-AFTERBURNER-Q1-{a}'), _kw(b, f'IA-Q1{a}-LOSS')),
             'down transit = tier source less the standing loss', basis, 'A-M-259')
        q1d = _kw(b, f'HL-Q1-{a}-DOWN')
        _put(b, f'HL-Q2-{a}-DOWN',
             transit_down(q1d + _kw(b, f'HL-GLASS_BURNOUT-Q2-{a}'), _kw(b, f'IA-Q2{a}-LOSS')),
             'down transit = Q1 down + burnout source less the standing loss', basis, 'A-M-259')
        # Q3 supply-limited (HEAT_LADDER.md Duties: draws running, Q3 -> Q4 carries 0)
        uid = f'Q3_{a}'
        draws = {f'HL-Q3-{a}-{h}': dec(_kw(b, f'HL-Q3-{a}-{h}')) for h in DRAWS}
        if 'x_thm_rated_draws' not in b.nodes[uid]['params']:
            _set(b, uid, 'params.x_thm_rated_draws', {k: float(v) for k, v in draws.items()},
                 'X-THM-01 R10b rated-draw profile seed (Q3 supply-limited draws, AQS-DUTY-008 Rev B)', 'AQS-DUTY-008')
        else:
            draws = {k: dec(x) for k, x in b.nodes[uid]['params']['x_thm_rated_draws'].items()}
        r3 = sum(draws.values(), D0)
        s3 = _kw(b, f'HL-Q2-{a}-DOWN')
        for k, rated in draws.items():
            _put(b, k, pro_rata(s3, rated, r3),
                 f'supply-limited draw: {fmt(s3, 3)} kW Q3 supply pro-rata on the rated profile {fmt(r3, 3)} kW',
                 basis, 'A-M-259')
        _put(b, f'HL-Q3-{a}-DOWN', D0,
             'Q3 fully drawn; the Q3 -> Q4 step carries 0 (HEAT_LADDER.md Duties)', basis, 'A-M-259')
        # Q4 batteries pass what they receive (HX-8 split + trim) to the header bus
        _put(b, f'HL-Q4-{a}-BUS',
             _kw(b, f'HL-HX8-Q4-{a}') + _kw(b, f'IA-Q4{a}-TRIM') + _kw(b, f'HL-Q3-{a}-DOWN'),
             'store-bus link = HX-8 split + rectifier trim + Q3 down (store closes)', basis, 'A-M-259')
    close_basis = basis + '; F-25 N+1 store-bus book (HEAT_LADDER.md section 3, A-M-453); Q4 bus close, ' \
        'GEO_HP dispatch (AQS-DUTY-010)'
    for s in STORE_LINKS:
        if s in b.edges:
            rest = (b.edges[s]['rate'].get('note') or '').split(' | X-THM-01')
            note = F25 + ''.join(' | X-THM-01' + seg for seg in rest[1:])
            _rate(b, s, q(_kw(b, s), 4), note, close_basis, 'A-M-453')
            _edge_field(b, s, 'params.duty_normal_kw', float(q(_kw(b, s), 4)), close_basis, 'A-M-453')
    fixed_in = _thermal_census(b, 'to_unit_id', 'Q4_BUS', drop=('S44',) + STORE_LINKS)
    stores = sum((_kw(b, s) for s in STORE_LINKS if s in b.edges), D0)
    fixed_out = _thermal_census(b, 'from_unit_id', 'Q4_BUS', drop=('HL-Q4-REJ',))
    need = fixed_out - (fixed_in + stores)
    if need > EPS:
        _put(b, 'S44', need,
             f'GEO_HP lifts the Q4 bus deficit {fmt(need, 3)} kW (AQS-DUTY-010 dispatch: lift only on deficit)',
             close_basis, 'A-M-259')
        _put(b, 'HL-Q4-REJ', D0,
             'terminal idle on the design day: the study branches absorb the bus; dry cooler stays rated for '
             'the upset case', close_basis, 'A-M-259')
    else:
        _put(b, 'S44', D0, 'GEO_HP idle: bus sources cover the branches (AQS-DUTY-010)', close_basis, 'A-M-259')
        _put(b, 'HL-Q4-REJ', -need,
             f'terminal by difference {fmt(-need, 3)} kW; dry cooler rated for the upset case (A-M-244)',
             close_basis, 'A-M-259')


@fn('dry_cooler', 'X-THM-01 R10b terminal closure (F-3, A-M-454) and the dry-cooler rating from the calculated '
    'bounding duty (F-4, A-M-244 restated, A-M-455; AQS-DUTY-008 section 3 margin, 0.05 kW_fan/kW_th class)')
def dry_cooler(b, inputs):
    drv = inputs.get('drivers')
    if drv is None:
        return
    term_basis = 'X-THM-01 R10b terminal closure (F-3, A-M-454): the cooler passes the duty it receives to ambient air'
    assert 'IA-DC-REJ' in b.edges, 'dry_cooler: the seed lacks the terminal rejection edge (builder topology)'
    dc_in = _thermal_census(b, 'to_unit_id', 'DRY_COOLER')
    note = (f'X-THM-01 R10b terminal closure (F-3, A-M-454): equals every thermal kW edge into DRY_COOLER '
            f'({fmt(dc_in, 3)} kW on this pass); the node ledger closes: in = out to ambient air.')
    _rate(b, 'IA-DC-REJ', q(dc_in, 4), note, term_basis, 'A-M-454')
    book = b.computed.get(('node', 'ZNBR2', 'params.cycling_thermal'))
    book = book[0] if book is not None else b.nodes.get('ZNBR2', {}).get('params', {}).get('cycling_thermal')
    if b.nodes.get('DRY_COOLER') is None or book is None:
        return                                                 # the v1 rating guard: no book, no rating
    rating_basis = ('X-THM-01 F-4 dry-cooler rating (A-M-244 restated, A-M-455); AQS-DUTY-008 section 3 margin, '
                    '0.05 kW_fan/kW_th class')
    znbr_avg = _kw(b, 'IA-ZNBR-HEAT')
    znbr_win = dec(book['window_kW'])
    r = cooler_rating(dc_in, znbr_avg, znbr_win)
    rated, fan = r['rated'], r['fan']
    rej = b.computed.get(('edge', 'HL-Q4-REJ', 'rate'))
    rate = rej[0] if rej is not None else b.edges['HL-Q4-REJ']['rate']
    if STALE_DC in (rate.get('note') or ''):
        _rate(b, 'HL-Q4-REJ', q(rate['value'], 4), rate['note'].replace(STALE_DC, RATED_DC), rating_basis)
    _set(b, 'DRY_COOLER', 'params.rated_kW', float(rated), rating_basis, 'A-M-455')
    _set(b, 'DRY_COOLER', 'params.fan_kW', q(fan, 2), rating_basis, 'A-M-455')
    _set(b, 'DRY_COOLER', 'params.basis',
         (f'X-THM-01 F-4 (A-M-244 restated, A-M-455): rated {rated} kW = 1.25 x the calculated bounding duty '
          f'{fmt(r["bound"], 1)} kW (design-day terminal book {fmt(dc_in, 1)} kW with the ZNBR2 cycling heat at '
          f'its {fmt(znbr_win, 1)} kW charge-window rate; AQS-DUTY-008 section 3 margin); fan {q(fan, 2)} kW at '
          f'the 0.05 kW_fan/kW_th class. Was the 12 kW class sized to the 10.16 kW no-preheat upset.'),
         rating_basis, 'A-M-455')

"""The sizing_receivers family (family migration; reference writer
flow_graph/param/receivers.py --write, ledger row `sizing_receivers`, section B,
MIXED: split sizing -> this function, doc -> the renderer wave). High-pressure
gas receivers CRYO_H2 and CRYO_O2 (A-M-167, AQS-DUTY-065) and the liquid CO2
store CRYO_CO2 at 20 bar, -20 C (A-M-181: 2 d of inflow at 1032 kg/m3, 90 %
fill): banks of seamless SA-312 TP316L DN100 Sch 160 tubes (ASME B36.10M OD
114.3, t 13.49 mm). 316L serves both gases: austenitic (hydrogen), and stainless
in oxygen (CGA_S1_1 relief, O2 cleaning ASTM G93 per the graph). Wall per B31.3
304.1.2 / UG-27 outside-radius form t = P D/(2(S E + P Y)) with Y 0.4, S from
ASME_II_D, E 1, 12.5 % mill tolerance. ID 87 mm is below the 152 mm Section
VIII limit (ASME_VIII1_U1), so the tubes are piping components (ASME_B31_3).
Water volume from the graph store; tubes in two manifolded halves so one
leaking tube or half is isolated with the rest in service (redundancy rule).
The committed graph carries every field the stage stamps; that committed state
is the golden this function reproduces.

Grid doctrine (owner ruling 2026-11-15): driver and seed values convert at this
boundary by dec() (the exact Decimal of the decimal repr); the v1 quantise
points emit through book()/unbook() - the integer count of 10^-dp units,
half-even, with the dimension and scale cited at every call. Tube counts, rows,
halves and every rack millimetre run as native integers on the driver grid (the
pitch, allowance and per-row drivers are whole-mm integers). Dimensionless
constants port as integer scaled pairs with the scale in the name (the Y 0.4
B31.3 form as 2/5, the two manifolded halves, the 2 d hold driver read at the
boundary). No float literals; the lint holds this.

The books that stay v1 float books by necessity, documented here: the bank
water volumes the stage does not round. The main bank volume is the seed store
book (CRYO_H2/CRYO_O2 from the storage family, CRYO_CO2 freshly rounded at 4 dp
by this stage); the CRYO_O2 crew-reserve bank volume is the raw float product
store_water_volume_m3 x crew_reserve_kg / store_kg the v1 stage carried
unrounded onto the stamp - it reproduces the committed repr through a float
replica of the v1 expression over the same quantised inputs (no literals; the
floats come from the exact books by flo()). The per-tube water area carries pi
(the v1 float book; the tube-count ceilings sit far enough from an integer
boundary that the float book is the faithful one). The t_req wall, steel mass
and store books quantise at the stage's own points (the design dict floats at
4 dp, the CO2 store mass at 3 dp, the store volume at 4 dp) through
book()/unbook(), whose float path converts through the exact binary value
(Fraction), so it is Python round()'s own tie rule.

Seed reads (prior-family fields, recorded): the store books
params.store_water_volume_m3 of CRYO_H2 and CRYO_O2 (the storage family's
books, read as-is), CRYO_O2 params.crew_reserve_kg (the X-RED-04 crew book),
params.design_kPa (the R11 Rev AC module basis where a node lost the stamp:
A-M-167 22 MPa / A-M-180 2200 kPa g driver fallback), and the CRYO_CO2 inflow
sum (every present kg/d edge into CRYO_CO2, in edge-list order - the process
and capture families' books).

Disposition of the chains around this family (the strangler bridge):
- docs-authority/sizing/GAS_RECEIVERS.md (AQS-DUTY-065) is the renderer wave's:
  the doc consumed per unit P_design_MPa, t_req_mm, t_min_mm, t_ok, tube_m,
  ID_mm, the bank list (bank name and V_m3), tubes, steel_kg and rack_mm, plus
  the fixed 316L/Sch 160 wall sentence.
- params.relief_mm / params.relief_basis / params.design_kPa on these nodes are
  NOT this stage's: the v1 receivers writer stamps none of them - the relief
  cases belong to the write_graph relief family (API 520 on pressurised nodes)
  and the fire case to its X-SAF-05 receiver block; this function leaves the
  committed relief books untouched (one writer per field).
- The CO2 store books land first and feed the same pass's bank arithmetic: the
  v1 stage wrote params.store_kg / params.store_water_volume_m3 on CRYO_CO2 and
  read the rounded volume straight into the main bank book; this function does
  the same (fresh book, then the rounded read).

The v1 machinery (disk write-back, the doc render, the stdout dump) does not
migrate: assignment replaces the field and its provenance in full. A solve
without the driver payload records nothing, so the bridge solve and the check
stay byte-faithful to the seed.
"""
import math
from decimal import Decimal, ROUND_HALF_EVEN
from fractions import Fraction

from flow_graph.v2.registry import fn

STAGE = 'receivers'                                            # ledger row sizing_receivers, provenance stage
RCVK = 'CRYO.cold-box-asu-recovery-train.cold-box.'            # U4b: sizing literals single-sourced from drivers.json
TAG = 'A-M-167'
F0 = Decimal('0.0')                                            # the v1 zero book (float lane)
Y_FORM = Fraction(2, 5)                                        # the B31.3 Y 0.4 outside-radius form
MM_PER_M = Fraction(1000)                                      # the mm/m ladder
MATERIAL = ('SA-312 TP316L seamless DN100 Sch 160, B16.11 Class 9000 fittings / autoclave cone-and-thread, '
            'O2 bank cleaned to ASTM G93')
SIZE_NOTE = 'L x W x H mm tube rack, set by flow_graph/param/receivers.py (A-M-167)'
UNITS = ('CRYO_H2', 'CRYO_O2', 'CRYO_CO2')


def dec(value):
    """A v1 float/int/str -> exact Decimal at the boundary (decimal repr)."""
    return Decimal(str(value))


def book(x, dp, cite):
    """The integer book: exact value -> count of 10^-dp units, half-even.
    A float input converts through its exact binary value, so this is Python
    round()'s own tie rule - the rounding the v1 writer used at this point.
    `cite` names the dimension and the schema scale at the call site."""
    if isinstance(x, (float, Decimal)):
        x = Fraction(x)
    m = 10 ** dp
    a, b = x.numerator * m, x.denominator
    sign = -1 if a < 0 else 1
    q, r = divmod(abs(a), b)
    if 2 * r > b or (2 * r == b and q % 2 == 1):
        q += 1
    return sign * q


def unbook(cnt, dp):
    """Render an integer book count as the exact JSON number of its decimal
    (no signed zeros - the v1 rate book carries none)."""
    f = float(Decimal(cnt) / (Decimal(10) ** dp))
    return float(0) if f == 0 else f


def flo(value):
    """The documented float-lane conversion: the float of an exact book or
    decimal - identical bits to the JSON literal it came from."""
    if isinstance(value, Fraction):
        return value.numerator / value.denominator
    return float(str(value))


def _prov(basis, ref=None):
    from flow_graph.v2.model import Prov
    return Prov(STAGE, basis, ref)


def _set(b, uid, path, value, basis, ref=None):
    b.set_node_field(uid, path, value, _prov(basis, ref))


def _dv(drv, key):
    """A driver value -> exact Decimal. drivers.json keys are flat dotted
    strings (DR.val); a bare suffix also walks the receiver prefix."""
    if key in drv:
        return dec(drv[key]['value'])
    return dec(drv[RCVK + key]['value'])


def co2_inflow_kg_d(b):
    """The committed kg/d books into CRYO_CO2: every present kg/d edge, summed
    in edge-list order (the process and capture families' rates)."""
    total = flo(F0)
    for e in b.data['edges']:
        if e['to_unit_id'] == 'CRYO_CO2' and e.get('presence') == 'present' \
                and (e.get('rate') or {}).get('unit') == 'kg/d':
            val = e['rate'].get('value')
            total += val if isinstance(val, (int, float)) else flo(F0)
    return total


def design(b, drv):
    """The v1 receivers.design() port on the recorded boundary. Returns
    ({unit: design dict}, (store_kg, store_volume)) with the dicts in the v1
    key order."""
    s = flo(_dv(drv, 's_316L_38C_MPa'))                    # MPa, ASME_II_D SA-312 TP316L to 38 C
    length = flo(_dv(drv, 'rcv_tube_len_m'))
    od = flo(_dv(drv, 'rcv_tube_OD_mm'))
    wall = flo(_dv(drv, 'rcv_tube_wall_mm'))
    mill = flo(_dv(drv, 'rcv_wall_mill_factor'))
    halves_i = int(_dv(drv, 'rcv_manifold_halves'))
    per_row = int(_dv(drv, 'rcv_tubes_per_row'))
    pitch = int(_dv(drv, 'rcv_row_pitch_mm'))
    rack_allow = int(_dv(drv, 'rcv_rack_allow_mm'))
    rack_len_allow = int(_dv(drv, 'rcv_rack_len_allow_mm'))
    t_amb = int(_dv(drv, 'rcv_T_amb_C'))
    kg_m = flo(_dv(drv, 'rcv_tube_kg_m'))
    id_mm = od - 2 * wall
    area = math.pi * (id_mm / float(MM_PER_M)) ** 2 / 4
    out = {}
    co2_books = None
    for u in UNITS:
        p = b.nodes[u].get('params') or {}
        if u == 'CRYO_CO2':
            # A-M-181: 2 d of inflow at the liquid density, 90 % fill; the
            # store books land on the node and feed the bank book below
            store_kg = unbook(book(flo(_dv(drv, 'co2_store_hold_d')) * co2_inflow_kg_d(b), 3,
                                   'mass kg: the CO2 store mass book at 3 dp (A-M-181)'), 3)
            vol = unbook(book(flo(dec(store_kg)) / flo(_dv(drv, 'co2_liq_rho_kg_m3'))
                              / flo(_dv(drv, 'co2_fill')), 4,
                              'volume m3: the CO2 store water volume book at 4 dp (A-M-181)'), 4)
            co2_books = (store_kg, vol)
            store_vol = vol
        else:
            store_vol = p['store_water_volume_m3']         # the storage family's seed book
        p_design = flo(dec(p['design_kPa'])) / float(MM_PER_M) \
            if isinstance(p.get('design_kPa'), (int, float)) \
            else flo(_dv(drv, 'rcv_design_kPa_co2' if u == 'CRYO_CO2' else 'rcv_design_kPa_hp')) / float(MM_PER_M)
        # R11 Rev AC regen: params.design_kPa dropped from the graph in Rev AC;
        # module basis A-M-167 (22 MPa) / A-M-180 (2200 kPa g)
        t_req = p_design * od / (2 * (s + p_design * float(Y_FORM)))
        t_min = wall * mill
        banks = [('main', store_vol)]
        if u == 'CRYO_O2' and p.get('crew_reserve_kg'):
            banks.append(('crew reserve', store_vol * flo(dec(p['crew_reserve_kg']))
                          / flo(dec(p['store_kg']))))      # the raw float bank book (see docstring)
        bk = []
        for name, vol in banks:
            n = max(halves_i, math.ceil(vol / (area * length)))
            n += n % halves_i                               # whole manifolded halves
            bk.append(dict(bank=name, V_m3=vol, tubes=n, halves=halves_i))
        nt = sum(bank['tubes'] for bank in bk)
        rows = math.ceil(nt / flo(per_row))
        rack = [book(length * float(MM_PER_M), 0, 'length mm: the rack length book, whole mm') + rack_len_allow,
                per_row * pitch + rack_allow, rows * pitch + rack_allow]
        out[u] = dict(P_design_MPa=p_design, S_MPa=s, t_req_mm=t_req, t_min_mm=t_min, t_ok=t_min >= t_req,
                      OD_mm=od, ID_mm=id_mm, tube_m=length, banks=bk, tubes=nt,
                      steel_kg=nt * length * kg_m, D_mm=book(od, 0, 'length mm: the tube OD book, whole mm'),
                      wall_mm=wall, H_mm=rows * pitch + rack_allow, T_C=t_amb, rack_mm=rack,
                      material=MATERIAL)
    return out, co2_books


@fn('gas_receivers', 'High-pressure gas receivers CRYO_H2 / CRYO_O2 and the liquid CO2 store CRYO_CO2 '
    '(A-M-167, A-M-180, A-M-181; AQS-DUTY-065): SA-312 TP316L DN100 Sch 160 tube banks, the B31.3 304.1.2 '
    'outside-radius wall with Y 0.4 and 12.5 % mill tolerance, two manifolded halves per bank (redundancy '
    'rule); the CO2 store at 2 d of inflow, 90 % fill')
def gas_receivers(b, inputs):
    drv = inputs.get('drivers')
    if drv is None or not all(u in b.nodes for u in UNITS):
        return                                             # bridge contract: no drivers, no stamps
    result, co2_books = design(b, drv)
    basis = ('AQS-DUTY-065 receiver tube banks (A-M-167 HP gas, A-M-180 2200 kPa g O2/H2 basis, A-M-181 CO2 '
             'store): SA-312 TP316L DN100 Sch 160, B31.3 304.1.2 wall with Y 0.4, 12.5 % mill tolerance, '
             'whole manifolded halves per bank')
    if co2_books is not None:
        _set(b, 'CRYO_CO2', 'params.store_kg', co2_books[0], basis, 'A-M-181')
        _set(b, 'CRYO_CO2', 'params.store_water_volume_m3', co2_books[1], basis, 'A-M-181')
    for u, r in result.items():
        design_book = {k: (unbook(book(x, 4, 'the design book at 4 dp (MPa, mm, m, kg scale)'), 4)
                           if isinstance(x, float) else x) for k, x in r.items()}
        _set(b, u, 'params.design', design_book, basis, TAG)
        _set(b, u, 'params.size_mm', r['rack_mm'], basis, TAG)
        _set(b, u, 'params.size_note', SIZE_NOTE, basis, TAG)

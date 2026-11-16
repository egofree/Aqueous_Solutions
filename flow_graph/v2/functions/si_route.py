"""The silicon-route family (family migration; reference writer
flow_graph/param/si_refine.py `--write` with its fab_silicon.tf call, ledger
row `si_route`, section B, PHYSICS - migrate-as-function).

X-MFG-40 / X-RTE-SI family-4 stage (A-M-471/472/484): the wafer/CZ/litho/PV
streams of the fab silicon chain (A-M-471, fab_silicon.tf) and the SI_REDUCE
carbothermic reduction + SI_REFINE electronic-grade route (A-M-472,
si_refine.tf), run after specialty_sizing and before write_graph_power so the
roof re-solve sees the SF-SI_REDUCE / SF-SI_REFINE feeds. The committed graph
carries every field the stage stamps; that committed state is the golden this
module reproduces.

Grid doctrine (owner ruling 2026-11-15): the solve is exact. The fab and
chlorosilane-chain books run on Fractions over the driver decimals; the two
transcendentals of the chain (pi and the semi-square corner angle) evaluate in
Decimal at 60 digits - pi as the integer scaled pair 3141592653589793/10^15,
the corner angle by the atan half-angle identity 2*atan(sqrt((1-x)/(1+x))) in
an 80-digit context (Decimal carries no acos; the series is the function
`_acos`). Driver and seed values convert at the boundary by rat() (the exact
Fraction of the decimal repr). Quantisation happens only at the v1 writers'
own points, as integer books on the sub-grid of the declared dimension:
book(x, dp, cite) returns the exact integer count of 10^-dp units - the mg
book of the kg/d rate schema (10^-6 kg/d), the 0.1 mW book of the kW schema
(10^-4 kW), the 0.1 g book of the 4 dp design schema and the mg book of the
mass-fraction schema - with the dimension and scale cited at every call;
unbook() renders the exact decimal. Dimensionless constants port as integer
scaled pairs with the scale named: the CIAAW2021 molar-mass table on a
1e-3 g/mol scale (constants.py M, exactly the entries the reference writer's
stoichiometry reads), pi on a 1e-15 scale, the argon reference density
1784/1000 g/L and the Julian year 36525/100 d. No float literals; the lint
holds this.

The books that stay v1 float books by necessity, documented here: the
recovery-record masses (params.recovery need/recovered/unrecovered kg_d, raw
float products and sums of the chain values in v1), the IA-SI-PURGE bleed
composition (float divisions of the registered impurity-blend weights, A-M-489),
the round-6 carbon loss inside the char recovery record, and the A-M-484
netting comparison against the committed si_cl2 draw book. All reproduce the
committed reprs exactly through a float replica of the v1 expression over the
same leaves (no literals; the floats come from the driver/seed decimals and
the v1 pi/acos area book by _flo), per the foundry-family precedent for the
raw-float books.

Disposition of the chains around this family (the strangler bridge):
- TOPOLOGY does not migrate: this stage is a create-or-rate writer (edges are
  CREATED when a graph predates the route, else re-rated). The committed seed
  carries the whole topology - the SI_REFINE node (created by v1 only when
  missing, with its creation-time class/notes/params.presence seed), the 13
  fab streams and 11 route streams, the SF-SI_REDUCE / SF-SI_REFINE feeds
  (created only when missing, header tray on creation) - so this function
  asserts the seed topology, records each creation condition in the
  provenance of the fields it does stamp, and stamps only fields. The full
  mutation inventory for the composer lane is asserted as structured data in
  test_si_route.py.
- The rate-driven PRESENCE of the route streams is this stage's book (the
  recovery-first retire stamps): presence books 'retired' exactly when the
  stamped rate books zero, back to 'present' when a driver move revives the
  stream. IA-QUARTZ-MU carries the F-20261110-06 retirement note in that
  state. The fab streams never book zero, so their presence is seed topology
  (asserted, not stamped).
- The A-M-484 stamp semantics: the CA_POT chlorine export IA-CA-CL2-SHIP is
  NET of this loop's make-up. foundry_poly seeds the export with the make-up
  book in params.si_cl2_kg_d; this stage moves the export by the delta dl =
  seed book - recomputed make-up, and re-books the make-up, ONLY when dl is
  non-zero (successive substitution; the AL_POT chlorine closed on the cake
  chlorination, X-QA-19, so the CA_POT share carries the dock export). Under
  the F-20261110-09 single-writer rule (A-M-472 context) the si_cl2 draw book
  is this family's field: at the committed seed the recomputed make-up equals
  the book, so dl is 0.0 and the family stamps nothing on the edge - asserted
  in the test.
- DOWNSTREAM-OWNED fields are not stamped (one writer per field): the fab
  hot-zone model (A-M-483) stamps no field in this stage's window - the
  WAFER_FAB load basis is the X-ELS-02 block of the process family and the
  SOLAR_PV_CELL tool line is the sizing_pv_cell_line family (X-MFG-38, whose
  params.design.need seed is pv_wafer.need); SI_REDUCE's sec3_material is the
  materials3 family's selection (X-MAT-22); SI_REDUCE's size_note is the
  placement seed's; tcs_circ_kg_d (the TCS circulation, A-M-489) is computed
  by the reference writer but stamped by no stage - reported, not stamped.
  The m2_puller study (pv_wafer.py) writes nothing anywhere.
- The pv_wafer route dispatch: CZ_PSQ125 ports in full (the committed route).
  The CAST_MC156 cast-furnace branch (pv_wafer.cast) is deferred - the route
  driver is CZ_PSQ125, and the function records nothing if that ever changes
  (the process-family caustic precedent). SILANE_FBR ports in full: the route
  driver selects the yield and kWh drivers and the note route name, and the
  unstamped tcs_circ term is TCS-only.

The v1 machinery that does not migrate: the json file write, the note-freeze
idempotence (assignment replaces the field and its provenance in full), and
the o2_close _edge/_node template spawning (composer lane). A solve without
the driver payload records nothing, so the bridge solve and the check stay
byte-faithful to the seed.
"""
import math
from decimal import Decimal, getcontext
from fractions import Fraction

from flow_graph.v2.registry import fn

STAGE = 'si_route'                                             # ledger row, section B
D = Decimal
TAG_FAB = 'X-MFG-40 TF (A-M-471)'                              # fab_silicon.py TAG
TAG_SR = 'X-MFG-40 TF, on-site silicon (A-M-472)'              # si_refine.py TAG
PI = Decimal(3141592653589793) / Decimal(10) ** 15             # pi (scale 1e-15)
DAYS_YR = Fraction(36525, 100)                                 # Julian year, d
AR_RHO_STD = Fraction(1784, 1000)                              # g/L argon at 0 C and 1 atm (scale 1e-3)
ROUTES = ('TCS_SIEMENS', 'SILANE_FBR')                         # si_refine_route dispatch
PV_ROUTES = ('CZ_PSQ125', 'CAST_MC156')                        # pv_wafer_route dispatch

# CIAAW2021 molar masses on a 1e-3 g/mol scale (flow_graph/param/constants.py
# M, exactly the entries the reference writer's stoichiometry reads)
M = {'H': Fraction(1008, 1000), 'C': Fraction(12011, 1000), 'O': Fraction(15999, 1000),
     'Al': Fraction(26982, 1000), 'Si': Fraction(28085, 1000), 'Cl': Fraction(35450, 1000),
     'Ca': Fraction(40078, 1000), 'Fe': Fraction(55845, 1000)}
M_O2, M_CO, M_CO2 = 2 * M['O'], M['C'] + M['O'], M['C'] + 2 * M['O']
M_SIO2 = M['Si'] + 2 * M['O']
# the recovery AW table this family consumes for its recovery-first records
# (flow_graph/param/recovery.py AW): exact decimals, floated only inside
# _aw_frac (the documented v1 float book)
AW = {'Si': '28.085', 'O': '15.999'}

# fab streams (fab_silicon.py STREAMS): stream id, from, to, composition
# element, design key. The endpoints and the static compositions are
# composer-lane seed (asserted); the rate books are this stage's.
STREAMS_FAB = (('STOCK_TO_FAB', 'METAL_STORE', 'WAFER_FAB', 'Si', 'si_kg_d'),
               ('IA-FAB-WAFER', 'WAFER_FAB', 'LITHO_COAT', 'Si', 'wafer_kg_d'),
               ('IA-LITHO-WAFER-A', 'LITHO_COAT', 'LITHO_ALIGN', 'Si', 'wafer_kg_d'),
               ('IA-LITHO-WAFER-B', 'LITHO_ALIGN', 'LITHO_DEV', 'Si', 'wafer_kg_d'),
               ('IA-LITHO-WAFER-RET', 'LITHO_DEV', 'WAFER_FAB', 'Si', 'wafer_kg_d'),
               ('IA-FAB-PRODUCT', 'WAFER_FAB', 'NORTH_DOCK', 'Si', 'wafer_kg_d'),
               ('IA-FAB-KERF', 'WAFER_FAB', 'LEACH_CSTR_1', 'Si', 'kerf_leach_kg_d'),
               ('IA-FAB-KERF-REC', 'WAFER_FAB', 'SI_REFINE', 'Si', 'kerf_rec_kg_d'),
               ('IA-FAB-SCRAP', 'WAFER_FAB', 'METAL_STORE', 'Si', 'scrap_rec_kg_d'),
               ('IA-PV-WAFER', 'WAFER_FAB', 'SOLAR_PV_CELL', 'Si', 'pv_wafer_kg_d'),
               ('IA-PV-CELL', 'SOLAR_PV_CELL', 'PV_ARRAY', 'Si', 'pv_wafer_kg_d'),
               ('IA-AR-CZ', 'CRYO_ASU', 'WAFER_FAB', 'Ar', 'ar_kg_d'),
               ('IA-AR-CZ-BACK', 'WAFER_FAB', 'CRYO_ASU', 'Ar', 'ar_kg_d'))
WHY_FAB = {'si_kg_d': 'CZ charge per pull / days between pulls, plus the cast charge on CAST_MC156',
           'pv_wafer_kg_d': 'cells a day to replace the roof array x solar wafer mass (pv_wafer.py, A-M-484)',
           'wafer_kg_d': 'wafer starts x wafer mass',
           'kerf_leach_kg_d': 'saw kerf x (1 - si_kerf_recycle_frac): the slurry-fine fraction that stays with the '
                              'spent slurry to the leach',
           'kerf_rec_kg_d': 'saw kerf x si_kerf_recycle_frac: reclaimed to the chlorosilane loop '
                            '(recovery-first, A-M-486)',
           'scrap_rec_kg_d': 'crop, square-off and pot scrap x si_scrap_recycle_frac, returned to the store for the '
                             'next charge (A-M-487)',
           'ar_kg_d': 'puller argon per pull / days between pulls; closed loop through the getter'}
# route streams (si_refine.py STREAMS); IA-SI-PURGE carries the computed bleed
# composition, the others the static template
STREAMS_SI = (('IA-QUARTZ-MU', 'NORTH_DOCK', 'SI_REDUCE', 'SiO2', 'quartz_kg_d'),
              ('IA-SI-BRIQ', 'MFG_SHOP', 'SI_REDUCE', 'SiO2', 'briq_kg_d'),
              ('CHAR_TO_SI', 'OIL_PYRO', 'SI_REDUCE', 'C', 'char_kg_d'),
              ('IA-SI-HOOD-O2', 'ATMOS', 'SI_REDUCE', 'O2', 'o2_hood_kg_d'),
              ('IA-SI-CO2', 'SI_REDUCE', 'ATMOS', 'CO2', 'co2_kg_d'),
              ('IA-SI-FUME', 'SI_REDUCE', 'LEACH_CSTR_1', 'SiO2', 'fume_leach_kg_d'),
              ('IA-SI-MG', 'SI_REDUCE', 'SI_REFINE', 'Si', 'mg_kg_d'),
              ('IA-CL2-SIREF', 'CA_POT', 'SI_REFINE', 'Cl2', 'cl2_kg_d'),
              ('IA-SI-PURGE', 'SI_REFINE', 'LEACH_CSTR_1', None, 'purge_kg_d'),
              ('IA-PV-EOL', 'PV_ARRAY', 'SI_REFINE', 'Si', 'eol_in_kg_d'),
              ('IA-SI-EG', 'SI_REFINE', 'METAL_STORE', 'Si', 'eg_kg_d'))
WHY_SI = {'quartz_kg_d': 'the burden shortfall left after the recovered crib silicate (recovery-first, A-M-472)',
          'briq_kg_d': 'the crib silicate of the leach feed (A-M-490) briquetted as furnace burden, short of the '
                       'burden need',
          'char_kg_d': '2 C per Si reduced', 'o2_hood_kg_d': 'half an O2 per CO burned',
          'co2_kg_d': 'one CO2 per CO burned',
          'fume_leach_kg_d': 'gross fume x (1 - si_fume_burden_frac): the baghouse catch returns to the burden '
                             '(A-M-488)',
          'mg_kg_d': '(charge - returned scrap - eol - kerf credits) / purity',
          'cl2_kg_d': 'chlorine leaving with the impurity chlorides',
          'purge_kg_d': 'impurity chlorides from the impurity balance at the registered blend, plus the eol '
                        'separation residue',
          'eg_kg_d': 'the CZ charge less the returned crop and pot scrap (fab_silicon.py, A-M-487)',
          'eol_in_kg_d': 'cells retired a day, equal in steady state to the cells installed (pv_wafer.py, A-M-484); '
                         'ye lands in the loop (A-M-485)'}
QUARTZ_RETIRED_NOTE = ('Retired by recovery-first silicon (F-20261110-06): the briquetted crib silicate of the leach '
                       'feed covers the whole furnace burden, so no dock quartz is drawn. The edge returns if a '
                       'driver change leaves a shortfall (si_refine.py).')
CREATE_OR_RATE = ('create-or-rate edge: the composer lane creates it when the graph predates the route '
                  '(o2_close _edge template); the seed carries the creation')
# the registered iron-rich impurity blend of A-M-472's 2.2 kg Cl/kg
# (FeCl3 1.90, AlCl3 3.94, CaCl2 1.77): 0.75/0.15/0.10 by metal mass gives
# 2.20 kg Cl per kg of metal (A-M-489); weights as integer scaled pairs on a
# 1e-2 scale, formulas as (element, count) pairs over the M table
IMP_BLEND_W = (('FeCl3', Fraction(75, 100), (('Fe', 1), ('Cl', 3))),
               ('AlCl3', Fraction(15, 100), (('Al', 1), ('Cl', 3))),
               ('CaCl2', Fraction(10, 100), (('Ca', 1), ('Cl', 2))))


def rat(value):
    """A v1 driver/seed value -> its exact Fraction (the decimal the JSON carried)."""
    return Fraction(Decimal(str(value)))


def _flo(value):
    """The exact float of a v1 decimal (for the documented float-replica
    books): identical bits to the JSON literal it came from."""
    if isinstance(value, Fraction):
        return value.numerator / value.denominator if value.denominator != 1 else float(value.numerator)
    return float(str(value))


def _round_half_even(x, dp):
    """An exact value -> integer count of 10^-dp units, half-even (Python
    round()'s documented tie rule - the reference writer's rounding)."""
    if isinstance(x, Decimal):
        x = Fraction(x)
    m = 10 ** dp
    a, b = x.numerator * m, x.denominator
    sign = -1 if a < 0 else 1
    q, r = divmod(abs(a), b)
    if 2 * r > b or (2 * r == b and q % 2 == 1):
        q += 1
    return sign * q


def book(x, dp, cite):
    """The integer book: exact value -> count of 10^-dp units, half-even.
    `cite` names the dimension and the schema scale at the call site."""
    return _round_half_even(x, dp)


def unbook(cnt, dp):
    """Render an integer book count as the exact JSON number of its decimal
    (no signed zeros - the v1 rate book carries none)."""
    f = float(D(cnt) / (D(10) ** dp))
    return float(0) if f == 0 else f


def fbook(v, dp, cite):
    """The integer book of a documented v1 float-book value: the exact value
    of the double, quantised half-even (Python round(float, dp) semantics)."""
    return _round_half_even(Fraction(_flo(v)), dp)


def fmt(x, dp):
    """The f'{v:.dpf}' text of an exact value (half-even at dp)."""
    cnt = _round_half_even(x, dp)
    sign = '-' if cnt < 0 else ''
    cnt = abs(cnt)
    if dp == 0:
        return f'{sign}{cnt}'
    return f'{sign}{cnt // 10 ** dp}.{cnt % 10 ** dp:0{dp}d}'


def _acos(x):
    """acos on Decimal - Decimal carries none; the half-angle identity
    2*atan(sqrt((1-x)/(1+x))) with the alternating atan series, 80-digit
    context (exact to far beyond every quantisation this family stamps)."""
    getcontext().prec = 80
    if x == 1:
        return D(0)
    y = ((1 - x) / (1 + x)).sqrt()
    y2 = -y * y
    s, term, n = D(0), y, D(1)
    for _ in range(1, 200):
        s += term / n
        term = term * y2
        n = n + 2
        if abs(term) < D(10) ** -75:
            break
    res = 2 * s
    getcontext().prec = 60
    return +res


def _prov(basis, ref=None):
    from flow_graph.v2.model import Prov
    return Prov(STAGE, basis, ref)


def _set(b, uid, path, value, basis, ref=None):
    b.set_node_field(uid, path, value, _prov(basis, ref))


def _rate(b, sid, value, note, basis, ref=None):
    """The v1 rate() book on an edge: {value, unit, status, note} in kg/d."""
    b.set_edge_rate(sid, {'value': value, 'unit': 'kg/d', 'status': 'study', 'note': note},
                    _prov(basis, ref))


def _kw_rate(b, sid, value, note, basis, ref=None):
    """The v1 SF feed book on an edge: {value, unit, status, note} in kW."""
    b.set_edge_rate(sid, {'value': value, 'unit': 'kW', 'status': 'study', 'note': note},
                    _prov(basis, ref))


def _edge_field(b, sid, path, value, basis, ref=None):
    """An edge field beyond 'rate' (presence, composition): the same overlay."""
    b.computed[('edge', sid, path)] = (value, _prov(basis, ref))


def _kw_dict(b, uid, value, note, basis, ref=None):
    """The v1 continuous_kw stamp: whole dict, key order preserved."""
    _set(b, uid, 'continuous_kw', {'value': value, 'unit': 'kW', 'status': 'study', 'note': note},
         basis, ref)


def _seed_param(b, uid, dotted):
    """A seed value another family owns (the strangler read)."""
    cur = b.nodes[uid]['params']
    for part in dotted.split('.'):
        cur = cur[part]
    return cur


def _seed_edge_param(edge, dotted):
    """A seed value carried on an edge's params (the strangler read)."""
    cur = edge['params']
    for part in dotted.split('.'):
        cur = cur[part]
    return cur


def _aw_frac(formula, el):
    """recovery.frac for the ore minerals - the v1 float book over the AW
    table (see module docstring): float ops in the v1 order over the same
    inputs."""
    m = {'Si': 1 * _flo(AW['Si']), 'O': 2 * _flo(AW['O'])} if formula == 'SiO2' else {}
    t = sum(m.values())
    return m.get(el, _flo('0')) / t if t else _flo('0')


def _psq_area_cm2_x(side_mm, d_mm):
    """pv_wafer.psq_area_cm2 on exact books: the area of a square of side
    side_mm with its corners cut by a circle of diameter d_mm (a semi-square
    wafer), cm2."""
    r, h = D(d_mm) / 2, D(side_mm) / 2
    if h * D(2).sqrt() <= r:
        return Fraction(side_mm ** 2, 100)
    seg = r * r * _acos(h / r) - h * (r * r - h * h).sqrt()
    return Fraction((PI * r * r - 4 * seg) / 100)


def _core(b, inputs):
    """The silicon-route solve: the port of pv_wafer.need + fab_silicon.design
    + si_refine.design on exact rational arithmetic (with the two
    transcendental evaluations in Decimal), plus the documented v1 float
    replica for the raw-float books. Returns the chain values, or None without
    the drivers (the bridge contract)."""
    drv = inputs.get('drivers')
    if drv is None:
        return None

    def dv(k):
        return rat(drv[k]['value'])

    Fw, Pp = 'FAB.wafer-line-train.', 'FAB.pv-wafer-train.'
    route = drv['si_refine_route']['value']
    if route not in ROUTES:
        raise ValueError(f'si_refine_route {route!r} is not one of {ROUTES}')
    pv_route = drv['pv_wafer_route']['value']
    if pv_route not in PV_ROUTES:
        raise ValueError(f'pv_wafer_route {pv_route!r} is not one of {PV_ROUTES}')
    if pv_route != 'CZ_PSQ125':
        return None              # the CAST_MC156 cast-furnace branch is deferred (see module docstring)
    gas = drv[Fw + 'cz_blanket_gas']['value']
    if gas != 'Ar':
        raise ValueError(f'cz_blanket_gas {gas!r} refused: nitrogen forms silicon nitride on the melt at 1414 C; '
                         'argon is the only valid CZ ambient')

    # ---- pv_wafer.need: the cell need of the roof array (A-M-484) ----------
    life = (1 - dv(Pp + 'eol_output_frac')) / dv(Pp + 'degradation_per_yr')
    repl = 1 / life + dv(Pp + 'failure_per_yr')
    kw_np = rat(_seed_param(b, 'PV_ARRAY', 'nameplate_kw'))      # the array the cell line replaces
    w_d = kw_np * 1000 * repl / DAYS_YR                          # W of array replaced a day, STC 1000 W/m2
    t_pv = dv(Pp + 'wafer_t_um') / 10 ** 4
    kerf = dv(Fw + 'kerf_um') / 10 ** 4
    rho = dv(Fw + 'si_rho_g_cm3')
    a_pv = _psq_area_cm2_x(int(dv(Pp + 'psq_side_mm')), int(dv(Fw + 'wafer_D_mm')))
    eff_pv = dv(Pp + 'cell_eff_CZ')
    pv_body = Fraction(PI) * (dv(Fw + 'wafer_D_mm') / 10 / 2) ** 2
    cell_w = a_pv / 10 ** 4 * 1000 * eff_pv
    cells = w_d / cell_w
    wafer_g_pv = rho * a_pv * t_pv
    slot_g_pv = rho * pv_body * (t_pv + kerf)
    pv_wafer_kg_d = cells * wafer_g_pv / 1000
    pv_slot_g_d = cells * slot_g_pv / 1000
    pv_cm_d = cells * (t_pv + kerf)

    # ---- fab_silicon.design: the CZ charge (A-M-471) -----------------------
    starts = dv('FAB.litho-train.starts_per_d')
    keep = 1 - dv(Fw + 'cz_crop_frac')
    d_cm = dv(Fw + 'wafer_D_mm') / 10
    t_fab = dv(Fw + 'wafer_t_um') / 10 ** 4
    area = Fraction(PI) / 4 * d_cm * d_cm
    wafer_g = rho * area * t_fab
    slot_g = rho * area * (t_fab + kerf)
    cru_d = d_cm * dv(Fw + 'cz_crucible_ratio')
    crucible_cm2 = Fraction(PI) / 4 * cru_d * cru_d
    min_kg = dv(Fw + 'si_liquid_rho_g_cm3') * crucible_cm2 * dv(Fw + 'cz_min_depth_frac') * cru_d / 1000
    day_g = starts * slot_g + pv_slot_g_d * 1000
    need_kg = dv(Fw + 'campaign_d') * day_g / keep / 1000
    charge_kg = max(need_kg, min_kg)     # the crucible least melt governs at the bounding case
    interval_d = charge_kg * 1000 * keep / day_g
    body_cm = interval_d * (starts * (t_fab + kerf) + pv_cm_d)
    wafer_kg_d = starts * wafer_g / 1000
    cz_kg_d = charge_kg / interval_d
    si_kg_d = cz_kg_d                    # CZ_PSQ125: no cast charge
    loss_kg_d = si_kg_d - wafer_kg_d - pv_wafer_kg_d
    kerf_kg_d = starts * rho * area * kerf / 1000 + cells * rho * area * kerf / 1000
    scrap_kg_d = loss_kg_d - kerf_kg_d
    pull_h = body_cm * 10 / dv(Fw + 'cz_pull_mm_h')
    ar_h = dv(Fw + 'cz_melt_h') + dv(Fw + 'cz_neck_crown_h') + pull_h + dv(Fw + 'cz_cool_h')
    slpm = crucible_cm2 * dv(Fw + 'cz_ar_slpm_per_cm2')
    ar_kg_pull = slpm * 60 * ar_h * AR_RHO_STD / 1000
    yk = dv('si_kerf_recycle_frac')
    fs = dv('si_scrap_recycle_frac')
    kerf_leach = kerf_kg_d * (1 - yk)
    kerf_rec = kerf_kg_d * yk
    scrap_rec = scrap_kg_d * fs
    ar_kg_d = ar_kg_pull / interval_d

    # ---- si_refine.design: the chlorosilane loop (A-M-472/485..490) --------
    eg = si_kg_d - scrap_rec             # electronic-grade silicon the loop must make
    eol_in = pv_wafer_kg_d               # retired cells into the loop (A-M-485)
    ye = dv('si_eol_yield')
    eol = eol_in * ye
    eol_res = eol_in - eol               # glass/encapsulant separation residue
    si_in = eg - eol - kerf_rec          # silicon the furnace must reduce (loop net)
    assert si_in > 0, ('the recovered silicon exceeds the loop need; '
                       'lower si_eol_yield or si_kerf_recycle_frac')
    mg = si_in / dv('si_mg_purity')
    imp = mg - si_in                     # Fe/Al/Ca of the burden and the char ash
    y = dv(f'si_refine_yield_{route}')
    cl_imp = imp * dv('si_imp_cl_kg_kg')
    cl2 = cl_imp                         # chlorine leaves only with the impurity chlorides
    purge = imp + cl_imp + eol_res       # the bleed
    stc_rec = eg * (1 - y) / y           # SiCl4-Si hydrogenated back to TCS (A-M-489)
    h2 = stc_rec * dv('si_h2_stc_kg_kg')
    sio2_r = si_in * M_SIO2 / M['Si']
    r_saf = dv('si_saf_recovery')
    fume = sio2_r * (1 - r_saf) / r_saf  # gross fume to the baghouse
    bf = dv('si_fume_burden_frac')
    fume_leach = fume * (1 - bf)
    burden_need = sio2_r + imp + fume_leach      # SiO2-equivalent the furnace takes in
    feed = b.edges['IA-FEED-01']
    sil = rat(_seed_edge_param(feed, 'assay_envelope.cases.reference_point.silicate_oxide'))
    crib = rat(feed['rate']['value']) * sil * dv('s08_silicate_carry_frac')   # the A-M-490 crib pool
    briq = min(crib, burden_need)        # recovery-first burden (A-M-472)
    quartz = burden_need - briq          # dock quartz is the shortfall only
    c = 2 * M['C'] * si_in / M['Si']
    co = 2 * M_CO * si_in / M['Si']
    o2_hood = co * M_O2 / 2 / M_CO       # CO + 1/2 O2 -> CO2 in the hood
    co2 = co * M_CO2 / M_CO
    kw_reduce = mg * dv('si_saf_kWh_kg') / 24
    kw_refine = eg * dv(f'si_refine_kWh_kg_{route}') / 24
    # the loop and burden closures (the v1 1e-9 float asserts, exact here)
    assert briq + quartz + c + o2_hood == mg + co2 + fume_leach, 'the furnace burden must close'
    assert mg + eol_in + kerf_rec + cl2 == eg + purge, 'the loop must close: mg + credits + chlorine = rods + bleed'

    # ---- the documented v1 float-replica books (see module docstring) ------
    fb = _float_books(drv, feed, _seed_param(b, 'PV_ARRAY', 'nameplate_kw'))

    return dict(drv=drv, route=route, eg=eg, si_kg_d=si_kg_d, wafer_kg_d=wafer_kg_d,
                pv_wafer_kg_d=pv_wafer_kg_d, kerf_leach=kerf_leach, kerf_rec=kerf_rec,
                scrap_rec=scrap_rec, ar_kg_d=ar_kg_d, a_pv=a_pv, charge_kg=charge_kg,
                min_kg=min_kg, need_kg=need_kg, interval_d=interval_d, pull_h=pull_h,
                eol_in=eol_in, eol=eol, eol_res=eol_res, si_in=si_in, mg=mg, imp=imp,
                cl2=cl2, purge=purge, stc_rec=stc_rec, h2=h2, sio2_r=sio2_r, fume_leach=fume_leach,
                burden_need=burden_need, crib=crib, briq=briq, quartz=quartz, c=c, co=co,
                o2_hood=o2_hood, co2=co2, kw_reduce=kw_reduce, kw_refine=kw_refine, fb=fb)


def _float_books(drv, feed, nameplate):
    """The documented v1 float-replica books (see module docstring): the
    recovery-record masses, the IA-SI-PURGE bleed composition inputs and the
    A-M-484 netting comparison, reproducing the committed doubles exactly
    through the v1 expressions over the same leaves (the driver/seed decimals
    and the v1 pi/acos area book; no literals)."""
    Fw, Pp = 'FAB.wafer-line-train.', 'FAB.pv-wafer-train.'

    def f(k):
        return _flo(drv[k]['value'])

    def psq_area_cm2_f(side_mm, d_mm):
        r, h = d_mm / 2, side_mm / 2
        seg = r * r * math.acos(h / r) - h * math.sqrt(r * r - h * h)
        return (math.pi * r * r - 4 * seg) / 100

    # pv_wafer.need, v1 float book
    life_f = (1 - f(Pp + 'eol_output_frac')) / f(Pp + 'degradation_per_yr')
    repl_f = 1 / life_f + f(Pp + 'failure_per_yr')
    w_d_f = _flo(nameplate) * 1000 * repl_f / _flo(DAYS_YR)
    t_pv_f = f(Pp + 'wafer_t_um') / 10 ** 4
    kerf_f = f(Fw + 'kerf_um') / 10 ** 4
    rho_f = f(Fw + 'si_rho_g_cm3')
    a_pv_f = psq_area_cm2_f(f(Pp + 'psq_side_mm'), f(Fw + 'wafer_D_mm'))
    cell_w_f = a_pv_f / 10 ** 4 * 1000 * f(Pp + 'cell_eff_CZ')
    cells_f = w_d_f / cell_w_f
    pv_wafer_kg_d_f = cells_f * rho_f * a_pv_f * t_pv_f / 1000
    pv_body_f = math.pi / 4 * (f(Fw + 'wafer_D_mm') / 10) ** 2
    pv_slot_g_d_f = cells_f * rho_f * pv_body_f * (t_pv_f + kerf_f) / 1000
    pv_cm_d_f = cells_f * (t_pv_f + kerf_f)
    # fab_silicon.design, v1 float book
    starts_f = f('FAB.litho-train.starts_per_d')
    keep_f = 1 - f(Fw + 'cz_crop_frac')
    d_cm_f = f(Fw + 'wafer_D_mm') / 10
    t_fab_f = f(Fw + 'wafer_t_um') / 10 ** 4
    area_f = math.pi / 4 * d_cm_f ** 2
    slot_g_f = rho_f * area_f * (t_fab_f + kerf_f)
    cru_d_f = d_cm_f * f(Fw + 'cz_crucible_ratio')
    crucible_cm2_f = math.pi / 4 * cru_d_f ** 2
    min_kg_f = f(Fw + 'si_liquid_rho_g_cm3') * crucible_cm2_f * f(Fw + 'cz_min_depth_frac') * cru_d_f / 1000
    day_g_f = starts_f * slot_g_f + pv_slot_g_d_f * 1000
    need_kg_f = f(Fw + 'campaign_d') * day_g_f / keep_f / 1000
    charge_kg_f = max(need_kg_f, min_kg_f)
    interval_f = charge_kg_f * 1000 * keep_f / day_g_f
    si_kg_d_f = charge_kg_f / interval_f
    wafer_kg_d_f = starts_f * rho_f * area_f * t_fab_f / 1000
    kerf_kg_d_f = starts_f * rho_f * area_f * kerf_f / 1000 + cells_f * rho_f * area_f * kerf_f / 1000
    kerf_leach_f = kerf_kg_d_f * (1 - f('si_kerf_recycle_frac'))
    kerf_rec_f = kerf_kg_d_f * f('si_kerf_recycle_frac')
    scrap_rec_f = (si_kg_d_f - wafer_kg_d_f - pv_wafer_kg_d_f - kerf_kg_d_f) * f('si_scrap_recycle_frac')
    # si_refine.design, v1 float book
    mc = {k: _flo(v) for k, v in M.items()}
    m_co_f, m_co2_f = mc['C'] + mc['O'], mc['C'] + 2 * mc['O']
    m_sio2_f = mc['Si'] + 2 * mc['O']
    eg_f = si_kg_d_f - scrap_rec_f
    eol_f = pv_wafer_kg_d_f * f('si_eol_yield')
    eol_res_f = pv_wafer_kg_d_f - eol_f
    si_in_f = eg_f - eol_f - kerf_rec_f
    mg_f = si_in_f / f('si_mg_purity')
    imp_f = mg_f - si_in_f
    cl2_f = imp_f * f('si_imp_cl_kg_kg')
    purge_f = imp_f + cl2_f + eol_res_f
    sio2_r_f = si_in_f * m_sio2_f / mc['Si']
    fume_f = sio2_r_f * (1 - f('si_saf_recovery')) / f('si_saf_recovery')
    fume_leach_f = fume_f * (1 - f('si_fume_burden_frac'))
    crib_f = _flo(feed['rate']['value']) \
        * _flo(_seed_edge_param(feed, 'assay_envelope.cases.reference_point.silicate_oxide')) \
        * f('s08_silicate_carry_frac')
    briq_f = min(crib_f, sio2_r_f + imp_f + fume_leach_f)
    c_f = 2 * mc['C'] * si_in_f / mc['Si']
    co2_f = (2 * m_co_f * si_in_f / mc['Si']) * m_co2_f / m_co_f
    co2_loss_f = co2_f * mc['C'] / m_co2_f       # the C inside the hood CO2, v1 op order
    return dict(eg_f=eg_f, eol_f=eol_f, eol_res_f=eol_res_f, kerf_leach_f=kerf_leach_f,
                kerf_rec_f=kerf_rec_f, briq_f=briq_f, c_f=c_f, co2_f=co2_f, co2_loss_f=co2_loss_f,
                cl2_f=cl2_f, purge_f=purge_f, sio2_r_f=sio2_r_f, fume_leach_f=fume_leach_f,
                imp_f=imp_f, frac_sio2_si=_aw_frac('SiO2', 'Si'))


def _assert_seed_topology(b):
    """The composer lane owns the topology; the seed must carry it. Fail
    loudly on drift (the process-family seed-contract pattern)."""
    for sid, a, zb, _comp, _key in STREAMS_FAB:
        e = b.edges[sid]
        assert (e['from_unit_id'], e['to_unit_id']) == (a, zb), f'{sid} names another stream'
        assert e.get('presence') == 'present', f'{sid} presence drifted (the fab rates never book zero)'
    for sid, a, zb, _comp, _key in STREAMS_SI:
        e = b.edges[sid]
        assert (e['from_unit_id'], e['to_unit_id']) == (a, zb), f'{sid} names another stream'
    # the SI_REFINE node exists: created by v1 only on a graph that predates
    # the route; the seed carries it with its creation-time notes/presence
    for uid in ('SI_REDUCE', 'SI_REFINE', 'WAFER_FAB', 'SOLAR_PV_CELL', 'METAL_STORE', 'PV_ARRAY'):
        assert uid in b.nodes, f'the {uid} node is composer-authored seed'
    # the SF feeds exist: created only when missing, header tray on creation
    for sid in ('SF-SI_REDUCE', 'SF-SI_REFINE'):
        assert sid in b.edges and b.edges[sid].get('header') == 'tray', f'{sid} is composer-authored seed'
    # the dock silicon import IA-SI-IMPORT: v1 retires it when present and not
    # retired; the committed graph has it deleted outright (composer lane)
    assert all(e.get('stream_id') != 'IA-SI-IMPORT' for e in b.data['edges']), \
        'IA-SI-IMPORT stays deleted (the owner-decision t58u retirement is seed topology)'
    # the static compositions of the fab and route streams are templates
    one = unbook(10 ** 6, 6)                  # the template value 1.0 on the mg book
    for sid, _a, _zb, comp, _key in STREAMS_FAB:
        assert b.edges[sid].get('composition') == {comp: one}, f'{sid} composition template drifted'
    for sid, _a, _zb, comp, _key in STREAMS_SI:
        if comp is not None:
            assert b.edges[sid].get('composition') == {comp: one}, f'{sid} composition template drifted'


def _purge_composition(fb):
    """The IA-SI-PURGE bleed composition (the documented v1 float book): the
    registered impurity-blend weights over their sum, the separation-residue
    share, then the renormalisation - float divisions and the float re-sum in
    the v1 order, each share booked on the mg book of the mass-fraction schema
    (10^-6)."""
    blend = {}
    for name, w, formula in IMP_BLEND_W:
        mw_f = sum(n * _flo(M[el]) for el, n in formula)
        blend[name] = _flo(w) * mw_f / _flo(M[formula[0][0]])
    s = sum(blend.values())
    comp = {k: unbook(fbook(v / s, 6, 'mass fraction on the mg book (10^-6)'), 6) for k, v in blend.items()}
    comp['separation residue'] = unbook(fbook(fb['eol_res_f'] / fb['purge_f'], 6,
                                              'mass fraction on the mg book (10^-6)'), 6) if fb['purge_f'] else float(0)
    tot = sum(comp.values())
    return {k: unbook(fbook(v / tot, 6, 'mass fraction on the mg book (10^-6)'), 6) for k, v in comp.items()}


# ---- the family function -------------------------------------------------------

@fn('si_route', 'X-MFG-40 / X-RTE-SI family-4 stage (A-M-471/472/484): the wafer/CZ/litho/PV streams of the fab '
    'silicon chain (A-M-471, fab_silicon.tf), the SI_REDUCE carbothermic burden and hood books and the SI_REFINE '
    'chlorosilane loop (A-M-472, A-M-485..490), the recovery-first retire stamps (F-20261110-06) on create-or-rate '
    'edges, and the A-M-484 chlorine make-up netting on IA-CA-CL2-SHIP under the F-20261110-09 single-writer rule')
def si_route(b, inputs):
    s = _core(b, inputs)
    if s is None:
        return                                    # bridge contract: no drivers, no stamps
    _assert_seed_topology(b)
    fb = s['fb']
    route = s['route']

    def rv(x):
        """kg/d on the mg book: 10^-6 kg/d (the v1 round(x, 6) rate schema)."""
        return unbook(book(x, 6, 'kg/d on the mg book (10^-6 kg/d)'), 6)

    def kv(x):
        """kW on the 0.1 mW book: 10^-4 kW (the v1 round(x, 4) kW schema)."""
        return unbook(book(x, 4, 'kW on the 0.1 mW book (10^-4 kW)'), 4)

    def dv4(x):
        """kg/d on the 0.1 g book: 10^-4 kg/d (the v1 round(x, 4) design schema)."""
        return unbook(book(x, 4, 'kg/d on the 0.1 g design book (10^-4 kg/d)'), 4)

    # ---- the fab silicon chain (A-M-471, fab_silicon.tf) ----------------------
    basis_fab = ('the fab silicon chain (X-MFG-40 TF, A-M-471): the wafer starts through the CZ charge, the '
                 'recovery-first kerf split (A-M-486/487) and the closed argon loop; create-or-rate edges, the '
                 'composer lane creates the streams when the graph predates the chain and the seed carries them')
    fab_vals = {'si_kg_d': s['si_kg_d'], 'wafer_kg_d': s['wafer_kg_d'],
                'kerf_leach_kg_d': s['kerf_leach'], 'kerf_rec_kg_d': s['kerf_rec'],
                'scrap_rec_kg_d': s['scrap_rec'], 'pv_wafer_kg_d': s['pv_wafer_kg_d'],
                'ar_kg_d': s['ar_kg_d']}
    for sid, _a, _zb, _comp, key in STREAMS_FAB:
        note = f'{TAG_FAB}: {WHY_FAB[key]} = {fmt(fab_vals[key], 4)} kg/d (fab_silicon.py).'
        _rate(b, sid, rv(fab_vals[key]), note, basis_fab)

    # ---- the carbothermic + EG route (A-M-472, si_refine.tf) ------------------
    basis_si = ('the on-site silicon route (X-MFG-40 TF, on-site silicon, A-M-472): the carbothermic burden '
                '(A-M-490 crib silicate, A-M-488 fume return, F-20261110-06 recovery-first quartz retirement), '
                'the hood burn and the chlorosilane loop (A-M-485..489)')
    si_vals = {'quartz_kg_d': s['quartz'], 'briq_kg_d': s['briq'], 'char_kg_d': s['c'],
               'o2_hood_kg_d': s['o2_hood'], 'co2_kg_d': s['co2'], 'fume_leach_kg_d': s['fume_leach'],
               'mg_kg_d': s['mg'], 'cl2_kg_d': s['cl2'], 'purge_kg_d': s['purge'],
               'eol_in_kg_d': s['eol_in'], 'eg_kg_d': s['eg']}
    for sid, _a, _zb, comp, key in STREAMS_SI:
        note = f'{TAG_SR}: {WHY_SI[key]} = {fmt(si_vals[key], 4)} kg/d (si_refine.py, route {route}).'
        if sid == 'IA-QUARTZ-MU' and si_vals[key] == 0:
            note = QUARTZ_RETIRED_NOTE            # the recovery-first retire note
        _rate(b, sid, rv(si_vals[key]), note, basis_si, CREATE_OR_RATE)
        # the recovery-first retire stamp: presence books retired exactly when
        # the rate books zero, back to present when a driver move revives it
        _edge_field(b, sid, 'presence', 'present' if si_vals[key] != 0 else 'retired',
                    basis_si + '; the recovery-first retire stamp (F-20261110-06): presence follows the rate book, '
                    'returning to present when a driver move revives the stream')
        if sid == 'IA-SI-PURGE':
            _edge_field(b, sid, 'composition', _purge_composition(fb),
                        basis_si + '; the bleed composition from the impurity balance at the registered blend '
                        '(A-M-489; the documented v1 float book)')

    # ---- the continuous loads and their SF feeds (A-M-472) --------------------
    basis_kw = f'{TAG_SR}: the submerged-arc furnace and the refining-route loads'
    _kw_dict(b, 'SI_REDUCE', kv(s['kw_reduce']),
             f'{TAG_SR}: {fmt(s["mg"], 4)} kg/d metallurgical silicon x si_saf_kWh_kg / 24 h (si_refine.py).',
             basis_kw, 'the F-20261110-09 single-writer rule (A-M-472 context)')
    _kw_dict(b, 'SI_REFINE', kv(s['kw_refine']),
             f'{TAG_SR}: {fmt(s["eg"], 4)} kg/d electronic-grade silicon x si_refine_kWh_kg_{route} / 24 h '
             f'(si_refine.py).', basis_kw, 'the F-20261110-09 single-writer rule (A-M-472 context)')
    for u, val in (('SI_REDUCE', s['kw_reduce']), ('SI_REFINE', s['kw_refine'])):
        _kw_rate(b, f'SF-{u}', kv(val), f'{TAG_SR}: feed equal to {u} continuous_kw.', basis_kw,
                 'create-or-rate edge: the composer lane creates the feed when missing (header tray on creation); '
                 'the seed carries it')

    # ---- the recovery-first records (F-20261110-06) ---------------------------
    basis_rec = ('the recovery-first records of the silicon route (F-20261110-06; A-M-485..490); the record masses '
                 'are the documented v1 float book (module docstring)')
    _set(b, 'SI_REDUCE', 'params.recovery', [
        {'element': 'Si', 'use': 'silicon furnace burden',
         'need_kg_d': (fb['sio2_r_f'] + fb['fume_leach_f'] + fb['imp_f']) * fb['frac_sio2_si'],
         'recovered_kg_d': fb['briq_f'] * fb['frac_sio2_si'], 'recovered_from': ['IA-SI-BRIQ'],
         'ore_streams': ['IA-QUARTZ-MU'], 'unrecovered': [],
         'note': ('recovery-first: the crib silicate recovered from the leach feed (A-M-490) is briquetted as the '
                  'whole furnace burden; the baghouse fume returns to the burden at si_fume_burden_frac (A-M-488) '
                  f'and dock quartz is drawn for the shortfall only ({fmt(s["quartz"], 4)} kg/d). The spent foundry '
                  'shell silica stays in the foundry loop (SHELL_BREAK to SHELL_BUILD), retiring the shell-silica '
                  'export and import pair')},
        {'element': 'C', 'use': 'furnace char reductant', 'need_kg_d': fb['c_f'], 'recovered_kg_d': float(0),
         'recovered_from': [], 'ore_streams': [],
         'unrecovered': [{'stream': 'IA-SI-CO2',
                          'kg_d': unbook(fbook(fb['co2_loss_f'], 6, 'kg/d on the mg book (10^-6 kg/d)'), 6),
                          'recoverable': False,
                          'basis': 'the furnace carbon monoxide burns to carbon dioxide in the hood with plant air; '
                                   'stack gas of the small submerged-arc class (A-M-472)'}],
         'note': 'the pyrolysis char carbon reduces the silica and leaves as hood CO2; the element mass balance '
                 'closes (F-20261110-07 loss check)'}], basis_rec)
    _set(b, 'SI_REFINE', 'params.recovery', [
        {'element': 'Si', 'use': 'electronic-grade silicon for the CZ charge', 'need_kg_d': fb['eg_f'],
         'recovered_kg_d': fb['eol_f'] + fb['kerf_rec_f'], 'recovered_from': ['IA-PV-EOL', 'IA-FAB-KERF-REC'],
         'ore_streams': [],
         'unrecovered': [{'stream': 'IA-SI-PURGE', 'kg_d': fb['eol_res_f'], 'recoverable': False,
                          'basis': 'end-of-life glass and encapsulant separation residue at si_eol_yield (A-M-485); '
                                   'leaves with the impurity-chloride bleed to the leach'},
                         {'stream': 'IA-FAB-KERF', 'kg_d': fb['kerf_leach_f'], 'recoverable': False,
                          'basis': 'slurry-fine kerf fraction not reclaimed (1 - si_kerf_recycle_frac, A-M-486); '
                                   'stays with the spent slurry'}],
         'note': ('the chlorosilane loop recovers the retired-cell silicon (A-M-485) and the reclaimed kerf '
                  '(A-M-486) first and hydrogenates the recycled SiCl4 back to trichlorosilane (A-M-489), so only '
                  'the impurity chlorides bleed; the crop and pot scrap return to the charge in METAL_STORE '
                  '(A-M-487)')}], basis_rec)

    # ---- the SI_REDUCE design book (F-20261110-09 single-writer rule) ---------
    basis_dsn = ('the F-20261110-09 single-writer rule (A-M-472 context): this stage is the only writer of the '
                 'SI_REDUCE design values - the retired X-QA-06 study class (A-M-466 replaced_by) no longer puts '
                 'anything on the unit; this stage supersedes it (A-M-471/472)')
    _set(b, 'SI_REDUCE', 'params.design',
         {'duty': 'carbothermic silicon reduction: the briquetted crib-silicate burden and the pyrolysis char '
                  '-> metallurgical-grade silicon for the CZ charge (route si_refine.py, A-M-472)',
          'si_kgd': dv4(s['si_in']), 'sio2_kgd': dv4(s['sio2_r']), 'char_kgd': dv4(s['c'])}, basis_dsn)
    _set(b, 'SI_REDUCE', 'params.sizing', {'si_kgd': dv4(s['si_in'])}, basis_dsn)
    _set(b, 'SI_REDUCE', 'params.size_mm', [1200, 1000, 1600],
         basis_dsn + '; the graphite hot-face furnace envelope (the issued sec3 selection)')
    _set(b, 'SI_REDUCE', 'params.size_basis',
         'graphite hot-face furnace (the issued sec3 selection) at the batch class', basis_dsn)

    # ---- the A-M-484 make-up netting on the CA_POT export ---------------------
    # foundry_poly seeds IA-CA-CL2-SHIP with the make-up book in
    # params.si_cl2_kg_d; this stage moves the export by the delta only when
    # the need moved after foundry_poly ran (successive substitution). The
    # si_cl2 draw book is this family's field (F-20261110-09 single-writer
    # rule, A-M-472 context). At the committed seed the recomputed make-up
    # equals the book, so dl is 0 and the family stamps nothing - asserted in
    # the test.
    sh = b.edges.get('IA-CA-CL2-SHIP')
    if sh is not None and (sh.get('params') or {}).get('si_cl2_kg_d') is not None:
        dl = sh['params']['si_cl2_kg_d'] - fb['cl2_f']
        if dl:
            seed = dict(sh['rate'])
            seed['value'] = unbook(fbook(_flo(sh['rate']['value']) + dl, 6,
                                         'kg/d on the mg book (10^-6 kg/d)'), 6)
            b.set_edge_rate('IA-CA-CL2-SHIP', seed,
                            _prov('the A-M-484 make-up netting: the CA_POT export moves by the silicon-loop '
                                  'make-up delta dl = book - recomputed need (A-M-484; foundry_poly seeds the '
                                  'export, this stage keeps it net; the AL_POT chlorine closed on the cake '
                                  'chlorination, X-QA-19)'))
            _edge_field(b, 'IA-CA-CL2-SHIP', 'params.si_cl2_kg_d', fb['cl2_f'],
                        'the A-M-484 make-up book: the si_cl2 draw this export is net of '
                        '(the F-20261110-09 single-writer rule, A-M-472 context)')
    return s

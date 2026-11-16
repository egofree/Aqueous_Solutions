"""The foundry + polymers sizing family (family migration; reference writer
flow_graph/param/foundry_poly.py with its salt_recovery.py TF call, ledger row
`foundry_poly`, section C, MIXED: split solve -> this function, topology ->
the builder/composer lane).

AQS-DUTY-072 / AQS-DUTY-073 (X-PAR-02 TF), unit task 02 for the FOUNDRY and
POLYMERS sectors, at the Rev AC bounding case with the X-QA-19 recovery-sized
aluminium line (A-M-495), the X-QA-11 on-site routes (A-M-496 brine, A-M-498
wax, A-M-499 raw-feed class, A-M-502 phosphate-FR finish) and the D-DOCK
feedstock program (A-M-284). The committed graph carries every field the
family stamps; that committed state is the golden this module reproduces.

Grid doctrine (owner ruling 2026-11-15): the solve is exact — the mass and
electrical books run on Fractions over the driver decimals, the vessel
geometry on Decimal at 60 digits (pi as the integer scaled pair
3141592653589793/10^15, cube roots as Decimal powers). Driver and seed values
convert at the boundary by rat() (the exact Fraction of the decimal repr).
Quantisation happens only at the v1 writers' own points, as integer books on
the sub-grid of the declared dimension: book(x, dp, cite) returns the exact
integer count of 10^-dp units (the milli-book that makes the committed
decimal schema exactly representable; the dimension and scale are cited at
every call), unbook() renders the exact decimal. The Faraday constant ports
as the integer pair 96485/1 C/mol — the reference writer's own book (its
F = 96485.0, not CODATA2018). Dimensionless constants port as integer scaled
pairs: the GREENWOOD element-mass table and the recovery AW table as exact
decimals, the stoichiometric ratios as integer pairs. No float literals; the
lint holds this.

The books that stay v1 float books by necessity, documented here: the
recovery-record masses (params.recovery need/recovered, a raw float product
of quantised rates and the AW table in v1), the retired IA-CL2-SHIP
params.al_chlor_cl2_kg_d, and the raw-float metal books the v1 solve dict
carries unrounded onto the stamps (the AL/TI/MO/CR metal *_kg_d entries in
params.sizing and the pot-design metal_kg_d, and CONT_CAST billet_kg_d - the
float melt mix including the float-arithmetic shop remnant r0_f). All
reproduce the committed repr exactly through a float replica of the v1
expression over the same quantised inputs (no literals; the floats come
from the exact books by _flo).

Disposition of the chains around this family (the strangler bridge):
- TOPOLOGY does not migrate: stream creation (mk()), retirements, presence
  flips, re-points (IA-WAX-CUT from_sector OIL) and the g['gaps'] entry are
  composer-lane work. The committed seed already carries that topology, so
  this function asserts it (the endpoints of created edges, the presence of
  retired edges, the absence of the interim IA-CA-TO-PCA) and stamps only
  fields. The full mutation inventory for the composer lane is asserted as
  structured data in test_foundry.py.
- DOWNSTREAM-OWNED fields are not stamped (one writer per field): the
  fluoro_train family re-owns the F-block unit blocks and the fluoropolymer
  edges incl. POWDER_TO_STOCK / FILM_TO_STOCK (A-M-289, A-M-482); the
  solvent family (A-M-479) owns the IA-SOLV-* streams and re-rates
  IA-KROLL-CO with its CO draw; the balance family (AQS-PAR-003)
  re-reconciles the brine-loop rates (IA-BRINE-SRC / IA-BRINE-CACL2 /
  IA-BRINE-ML - IA-BRINE-MGCL2 sits exactly at the closure) and co-authors
  the IA-C5-SHIP note; the fluoro photoresist netting (A-M-482) re-rates
  IA-CA-CL2-SHIP after si_refine's make-up netting (A-M-484). This function
  stamps the exact design book for those five rates - the closing values
  their downstream consumers need - and the test enumerates the committed
  residue per field with its owner.
- si_cl2 (the silicon-loop chlorine make-up, A-M-472) is owned by the
  si_route family: read from the committed IA-CA-CL2-SHIP params.si_cl2_kg_d
  seed (the A-M-484 remap book), never recomputed here.
- The melt-shop remnant r0 reads the shop through the committed graph with
  v1's closed-shop seed semantics (IA-GOODS-SHIP seeded in memory when the
  shop nets positive pre-goods, restored after the read; this function is
  read-only — the seed write stays with its own families).

The v1 note-freeze idempotence, the dock-class pops on retirement and the
FOUNDRY_POLY_MISSING_EDGES gap bookkeeping do not migrate: assignment
replaces the field and its provenance in full, retirement is seed topology,
and the gap list is a composer artifact. A solve without the driver payload
records nothing, so the bridge solve and the check stay byte-faithful to
the seed.
"""
from decimal import Decimal, ROUND_CEILING, ROUND_HALF_EVEN, localcontext
from fractions import Fraction

from flow_graph.v2.registry import fn

STAGE = 'foundry_poly'                                        # ledger row, section C
D = Decimal
D0, D1 = Decimal(0), Decimal(1)
DOC_F, DOC_P = 'AQS-DUTY-072', 'AQS-DUTY-073'
TAG = f'X-PAR-02 TF: foundry/polymers sizing ({DOC_F}/{DOC_P})'
TAG_SR = 'X-RTE TF: on-site Kroll brine recovery (X-QA-11, A-M-496)'
F_COULOMB = Fraction(96485)                                   # C/mol: the reference writer's book
PI = Decimal(3141592653589793) / Decimal(10) ** 15            # pi (scale 1e-15)

# GREENWOOD element-mass table exactly as the reference writer carries it
# (foundry_poly.py MM): exact decimals as integer scaled pairs.
MM = {'Al': Fraction(269815, 10000), 'Cl': Fraction(35453, 1000),
      'Mg': Fraction(24305, 1000), 'Ca': Fraction(40078, 1000),
      'Ti': Fraction(47867, 1000), 'O': Fraction(159994, 10000),
      'C': Fraction(12011, 1000), 'Mo': Fraction(95948, 1000),
      'Cr': Fraction(519962, 10000), 'H': Fraction(1008, 1000)}
# the recovery AW table this family consumes for its recovery-first records
# (flow_graph/param/recovery.py AW): exact decimals, floated only inside
# _aw_frac (the documented v1 float book).
AW = {'Si': '28.085', 'O': '15.999', 'Ti': '47.867', 'Mo': '95.95', 'Cr': '51.996'}
# element fractions of the dock concentrates (recovery.ORE mineral formulas)
ORE_FORMULA = {'TiO2': (('Ti', 1), ('O', 2)), 'MoO3': (('Mo', 1), ('O', 3)),
               'Cr2O3': (('Cr', 2), ('O', 3)), 'SiO2': (('Si', 1), ('O', 2))}
# the (NH4)2HPO4 finish book (A-M-502): H3PO4 and 2 NH3 per compound
M_H3PO4, M_NH3_X2, M_NH4_2HPO4 = Fraction(97994, 1000), Fraction(34062, 1000), Fraction(132056, 1000)

BRINE_HOSTS = ('LEACH_CSTR_1', 'CA_POT', 'MG_POT')            # A-M-496 locale hosts
BRINE_STREAMS = (('IA-BRINE-SRC', 'LEACH_CSTR_1', 'BRINE_CRYS'), ('IA-BRINE-CACL2', 'BRINE_CRYS', 'CA_POT'),
                 ('IA-BRINE-MGCL2', 'BRINE_CRYS', 'MG_POT'), ('IA-BRINE-ML', 'BRINE_CRYS', 'LEACH_CSTR_1'))
# the v1 stoichiometric coefficient book (foundry_poly melt classes)
MELT_CLASSES = (('Cu', '1084.62', 'melt_cp_solid_kJ_kgK', 'melt_L_kJ_kg', 'melt_cp_liq_kJ_kgK'),
                ('Fe', '1538', 'melt_fe_cp_solid_kJ_kgK', 'melt_fe_L_kJ_kg', 'melt_fe_cp_liq_kJ_kgK'),
                ('Zn', '419.5', 'melt_zn_cp_solid_kJ_kgK', 'melt_zn_L_kJ_kg', 'melt_zn_cp_liq_kJ_kgK'),
                ('Al', '660.3', 'melt_al_cp_solid_kJ_kgK', 'melt_al_L_kJ_kg', 'melt_al_cp_liq_kJ_kgK'),
                ('Ti', '1668', 'melt_ti_cp_solid_kJ_kgK', 'melt_ti_L_kJ_kg', 'melt_ti_cp_liq_kJ_kgK'))
POT_ROWS = (('AL_POT', 'al', 'Al', 3), ('MG_POT', 'mg', 'Mg', 2), ('CA_POT', 'ca', 'Ca', 2),
            ('MO_CELL', 'mo', 'Mo', 3), ('CR_CELL', 'cr', 'Cr', 3))


def rat(value):
    """A v1 driver/seed value -> its exact Fraction (the decimal the JSON carried)."""
    return Fraction(Decimal(str(value)))


def _round_half_even(x, dp):
    """An exact value -> integer count of 10^-dp units, half-even (Python
    round()'s documented tie rule — the reference writer's rounding)."""
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
    (no signed zeros — the v1 rate book carries none)."""
    f = float(D(cnt) / (D(10) ** dp))
    return float(0) if f == 0 else f


def fq(x, dp):
    """book + render in one step: the exact value at `dp` decimals."""
    return unbook(_round_half_even(x, dp), dp)


def qi(x):
    """round(x) as v1 wrote it: half-even to an integer."""
    return _round_half_even(x, 0)


def ceil_f(x):
    """math.ceil of an exact value."""
    if isinstance(x, Decimal):
        x = Fraction(x)
    return -((-x.numerator) // x.denominator)


def fmt(x, dp):
    """The f'{v:.dpf}' text of an exact value (half-even at dp)."""
    cnt = _round_half_even(x, dp)
    sign = '-' if cnt < 0 else ''
    cnt = abs(cnt)
    if dp == 0:
        return f'{sign}{cnt}'
    return f'{sign}{cnt // 10 ** dp}.{cnt % 10 ** dp:0{dp}d}'


def fmt_signed(x, dp):
    """The f'{v:+.dpf}' text of an exact value (sign always shown)."""
    cnt = _round_half_even(x, dp)
    sign = '-' if cnt < 0 else '+'
    return sign + fmt(D(abs(cnt)) / D(10) ** dp, dp)


def pct(x, dp):
    """The f'{v:.dp%}' text of an exact value."""
    return fmt(x * 100, dp) + '%'


def _flo(value):
    """The exact float of a v1 decimal (for the documented float-replica
    books): identical bits to the JSON literal it came from."""
    if isinstance(value, Fraction):
        value = value.numerator / value.denominator if value.denominator != 1 else value.numerator
        return float(value)
    return float(str(value))


def ffmt(v, dp):
    # the f'{v:.dpf}' of a stored v1 float book value (the double's
    # correctly-rounded decimal - the reference writer formats the doubles)
    return f'{v:.{dp}f}'


def dstr(x):
    """The exact decimal string of an exact value (Fraction denominators
    terminate on the driver decimals)."""
    if isinstance(x, Fraction):
        with localcontext() as ctx:
            ctx.prec = 60
            return str(D(x.numerator) / D(x.denominator))
    return str(x)


def _aw_frac(formula, el):
    """recovery.frac for the ORE minerals — the v1 float book over the AW
    table (see docstring): float ops in the v1 order over the same inputs."""
    m = {e: k * _flo(AW[e]) for e, k in ORE_FORMULA[formula]}
    t = sum(m.values())
    return m.get(el, _flo('0')) / t if t else _flo('0')


def _hold_kw():
    """The pot bath-hold loss (foundry_poly.hold_kW at the pot class): the
    DN150-floor vessel governs for every pot at the Rev AC rates, so the
    value is one constant — Decimal at 60 digits, 4 dp at stamp."""
    with localcontext() as ctx:
        ctx.prec = 60
        v = D('0.15') ** 2 * PI / 4 * D('0.225')
        d_c = (4 * v / (PI * D('1.5'))) ** (D(1) / 3)
        area = (PI * d_c * D('1.5') * d_c + 2 * PI * d_c * d_c / 4) * D('1.4')
        return D('0.8') * area * 675 / 1000


def _d_hold(kg, rho, tau, hd):
    """foundry_poly.D_hold: hold-up diameter in mm (Decimal at 60 digits)."""
    with localcontext() as ctx:
        ctx.prec = 60
        v = D(kg.numerator) / D(kg.denominator) * D(tau.numerator) / D(tau.denominator) \
            / (D(rho.numerator) / D(rho.denominator))
        if v <= 0:
            return D0
        return (4 * v / (PI * (D(hd.numerator) / D(hd.denominator)))) ** (D(1) / 3) * 1000


def _round10(xd):
    """int(round(x, -1)) as v1 wrote it: nearest 10 mm, half-even, as int."""
    return int(xd.quantize(D('1E+1'), rounding=ROUND_HALF_EVEN))


def _ebox(mn, d_mm, hd):
    """foundry_poly.ebox: the hold-up box grown at the class minimum
    (+300 mm plan access, +500 mm head at atm_HD), on the 10 mm grid."""
    d = D(d_mm)
    h = D(hd.numerator) / D(hd.denominator)
    return [_round10(max(D(mn[0]), d + 300)), _round10(max(D(mn[1]), d + 300)),
            _round10(max(D(mn[2]), d * h + 500))]


def _hoop(p_mpa, d_mm):
    """ASME VIII-1 UG-27 class wall (AQS-DUTY-064 method), 1 dp."""
    with localcontext() as ctx:
        ctx.prec = 60
        p, d_mm = D(p_mpa), D(d_mm)
        t = p * (d_mm / 2) / (115 - D('0.6') * p)
        v = max(D(3), t) + D('0.49')
        return float(v.quantize(D('0.1'), rounding=ROUND_HALF_EVEN))


def _faraday(m_kg_d, m_g_mol, z, ce):
    """Cell current at kg/d metal [foundry_poly.faraday_A]: the writer's
    96485 C/mol book, exact Fraction."""
    return m_kg_d * 1000 / m_g_mol * z * F_COULOMB / 86400 / ce


def _seed_param(b, uid, dotted):
    """A seed value another family owns (the strangler read)."""
    cur = b.nodes[uid]['params']
    for part in dotted.split('.'):
        cur = cur[part]
    return cur


def _seed_edge_param(b, sid, dotted):
    """A seed value carried on an edge's params (the strangler read)."""
    cur = b.edges[sid]['params']
    for part in dotted.split('.'):
        cur = cur[part]
    return cur


def _prov(basis, ref=None):
    from flow_graph.v2.model import Prov
    return Prov(STAGE, basis, ref)


def _set(b, uid, path, value, basis, ref=None):
    b.set_node_field(uid, path, value, _prov(basis, ref))


def _rate(b, sid, value, note, basis, ref=None):
    """The v1 rate() book on an edge: {value, unit, status, note}."""
    b.set_edge_rate(sid, {'value': value, 'unit': 'kg/d', 'status': 'study', 'note': note},
                    _prov(basis, ref))


def _kw_rate(b, sid, value, note, basis, ref=None):
    """The v1 kw()/SF feed book on an edge: {value, unit, status, note} in kW."""
    b.set_edge_rate(sid, {'value': value, 'unit': 'kW', 'status': 'study', 'note': note},
                    _prov(basis, ref))


def _edge_field(b, sid, path, value, basis, ref=None):
    """An edge field beyond 'rate' (params.*): the same overlay."""
    b.computed[('edge', sid, path)] = (value, _prov(basis, ref))


def _kw_dict(b, uid, value, note, basis, ref=None):
    """The v1 kw() continuous_kw stamp: whole dict, key order preserved."""
    _set(b, uid, 'continuous_kw', {'value': value, 'unit': 'kW', 'status': 'study', 'note': note},
         basis, ref)


def _r0(b):
    """The shop rounding remnant (A-M-265): rated in - rated out at MFG_SHOP,
    excluding this pass's own loop edges, with v1's closed-shop seed
    semantics (IA-GOODS-SHIP seeded in memory when the shop nets positive
    pre-goods; this read never writes). Exact Decimal over the seed rates.
    Pass 1 seeds the shop the way the reference writer does; pass 2 is the
    residual the solve consumes."""
    ins_all, out_ng, mfg_out, goods = D0, D0, D0, D0
    loop = ('MFG_SCRAP_TO_IND', 'STOCK_TO_MFG', 'POLY_TO_MFG')
    r = D0
    for e in b.data['edges']:
        if e['presence'] != 'present' or 'mass' not in (e.get('layers') or []) \
                or (e.get('rate') or {}).get('unit') != 'kg/d':
            continue
        val = e['rate'].get('value')
        if not isinstance(val, (int, float)):
            continue
        sid = e['stream_id']
        if sid == 'IA-GOODS-SHIP':
            goods = D(str(val))
            continue
        v = D(str(val))
        if e['to_unit_id'] == 'MFG_SHOP':
            ins_all += v
            if sid not in loop:
                r += v
        elif e['from_unit_id'] == 'MFG_SHOP':
            if sid == 'IA-MFG-OUT':
                mfg_out = v
            else:
                out_ng += v
                if sid not in loop:
                    r -= v
    seed = _round_half_even(ins_all - out_ng, 6)
    seed_kg = D(seed) / D(10) ** 6
    goods_eff = seed_kg if (seed > 0 and abs(goods - seed_kg) > D('1e-9')) else goods
    return r - goods_eff


def _core(b, inputs):
    """The foundry solve: the port of foundry_poly.solve() on exact rational
    arithmetic. Returns the chain values, or None without the drivers (the
    bridge contract)."""
    drv = inputs.get('drivers')
    if drv is None:
        return None

    def dv(k):
        return rat(drv[k]['value'])

    E = b.edges
    r0 = Fraction(_r0(b))
    # shop closure (A-M-257 by-difference pattern)
    K = dv('foundry_stock_demand_kg_d')            # full AQS-SIZE-FOUNDRY table (A-M-261 rev)
    f = dv('foundry_melt_loss_frac')
    rej = dv('poly_shop_reject_frac')
    P = -r0 + f * K / (1 - f)                      # polymer draw that closes the shop

    # pot / Kroll / investment algebra (A-M-280..284.283.286)
    xf = dv('foundry_pot_export_frac')
    al_i, ti_i = dv('foundry_al_line_kg_d'), dv('foundry_ti_line_kg_d')
    mo_i, cr_i = dv('foundry_mo_add_kg_d'), dv('foundry_cr_add_kg_d')
    al, ti = al_i * (1 + xf), ti_i * (1 + xf)      # line + export margin (A-M-285)
    mo, cr = mo_i * (1 + xf), cr_i * (1 + xf)
    potm = al + ti + mo + cr                       # total pot-metal throughput
    ca = dv('foundry_ca_add_frac') * (K + potm)    # deoxidizer Ca on the melt charge
    alcl3 = al * (MM['Al'] + 3 * MM['Cl']) / MM['Al']
    al_cl2 = al * 3 * MM['Cl'] / MM['Al']
    # X-QA-19 owner ruling (A-M-495): the aluminium line is sized to the
    # recoverable aluminium — AL_POT makes its whole AlCl3 feed on site from
    # the leach reactive-Al hydroxide cake, calcined and carbochlorinated
    # with the pot chlorine; the dock AlCl3 import is retired.
    feed_rate = Fraction(Decimal(str(E['IA-FEED-01']['rate']['value'])))
    al_frac = Fraction(Decimal(str(_seed_edge_param(b, 'IA-FEED-01',
                                                    'assay_envelope.reference_point_elements.Al'))))
    al_rec = min(al, feed_rate * al_frac)
    al_cake = al_rec * (MM['Al'] + 3 * (MM['O'] + MM['H'])) / MM['Al']
    alcl3_rec = al_rec * (MM['Al'] + 3 * MM['Cl']) / MM['Al']
    alcl3_mu = alcl3 - alcl3_rec                   # 0 at the recovery basis
    al_chlor_cl2 = al_rec * 3 * MM['Cl'] / MM['Al']
    char_al = al_rec * 3 * MM['C'] / (2 * MM['Al'])
    al_co = al_rec * 3 * (MM['C'] + MM['O']) / (2 * MM['Al'])
    al_h2o = al_rec * 3 * (2 * MM['H'] + MM['O']) / (2 * MM['Al'])
    cacl2 = ca * (MM['Ca'] + 2 * MM['Cl']) / MM['Ca']
    ca_cl2 = ca * 2 * MM['Cl'] / MM['Ca']
    tio2 = ti * (MM['Ti'] + 2 * MM['O']) / MM['Ti']
    c_ti = ti * 2 * MM['C'] / MM['Ti']
    cl2_ti = ti * 4 * MM['Cl'] / MM['Ti']
    mg_ti = ti * 2 * MM['Mg'] / MM['Ti']
    mgcl2_g = ti * 2 * (MM['Mg'] + 2 * MM['Cl']) / MM['Ti']
    co_ti = ti * 2 * (MM['C'] + MM['O']) / MM['Ti']
    kd = dv('foundry_kroll_dragout_frac')
    kroll_flux = kd * mgcl2_g                      # salt drag-out to FLUX_PREP
    mgcl2_ret = mgcl2_g - kroll_flux               # arrives at MG_POT
    mgcl2_mu = mg_ti + cl2_ti - mgcl2_ret          # brine make-up (= the drag-out exactly)
    moo3 = mo * (MM['Mo'] + 3 * MM['O']) / MM['Mo']
    c_mo = mo * Fraction(3, 2) * MM['C'] / MM['Mo']
    co2_mo = mo * Fraction(3, 2) * (MM['C'] + 2 * MM['O']) / MM['Mo']
    cr2o3 = cr * (2 * MM['Cr'] + 3 * MM['O']) / (2 * MM['Cr'])
    c_cr = cr * 3 * MM['C'] / (2 * MM['Cr'])
    co_cr = cr * 3 * (MM['C'] + MM['O']) / (2 * MM['Cr'])
    flux = kroll_flux
    S_exact = K + P + r0
    slag = f * S_exact + flux + ca                 # dross + flux pass-through + deoxidizer Ca
    inv = dv('foundry_inv_line_kg_d')
    cont = S_exact + potm + ca + flux - 3 - inv - slag        # IND_TO_CONT by difference
    cont_roll, cont_stock = Fraction(10), cont - 10
    stock_in = 13 + cont_stock + inv
    assert stock_in == K + potm, 'the foundry stock ledger must close on K + pot metal'
    # investment loop (A-M-286)
    sh = dv('foundry_inv_shell_kg_per_kg') * inv
    shr = dv('foundry_inv_shell_reclaim_frac')
    sh_mu, sh_recl = sh * (1 - shr), sh * shr
    wx = dv('foundry_inv_wax_kg_per_kg') * inv
    wr = dv('foundry_inv_wax_reclaim_frac')
    wx_mu, wx_recl, wx_burn = wx * (1 - wr), wx * wr, wx * (1 - wr)

    # electrical: Faraday at the pots/cells (A-M-282); hold at the DN150 floor
    Vc = {k: rat(v) for k, v in drv['foundry_pot_voltage_V']['value'].items()}
    ce = dv('foundry_pot_ce')
    hold_r = _round_half_even(_hold_kw(), 4)
    pot_e = {}
    for u, vk, el, z in POT_ROWS:
        m = {'AL_POT': al, 'MG_POT': mg_ti, 'CA_POT': ca, 'MO_CELL': mo, 'CR_CELL': cr}[u]
        i = _faraday(m, MM[el], z, ce)
        i_r = _round_half_even(i, 2)
        dc_r = _round_half_even(i * Vc[vk] / 1000, 4)
        kw_r = dc_r + hold_r                       # exact count arithmetic on the 4-dp book
        pot_e[u] = {'I_A': unbook(i_r, 2), 'V': fq(Vc[vk], 2), 'dc_kW': unbook(dc_r, 4),
                    'hold_kW': unbook(hold_r, 4), 'kW': unbook(kw_r, 4)}
    pot_e['TI_CELL'] = {'I_A': float(0), 'V': float(0), 'dc_kW': float(0), 'hold_kW': float('0.5'),
                        'kW': float('0.5')}        # thermochemical Kroll retort/chlorinator hold

    # melt energy by metal class (X-MFG-37 method, A-M-177)
    eta, sup = dv('melt_eta'), dv('melt_superheat_K')
    q = {c: (dv(cps) * (rat(t_c) - 25) + dv(l_kg) + dv(cpl) * sup) / eta / 3600
         for c, t_c, cps, l_kg, cpl in MELT_CLASSES}
    # melt charge by class: recycled table return + fresh pot metal; the
    # castings ride Fe, the stainless Cr/Mo ride Ti (reactive), r0 rides Fe
    mix = {'Cu': Fraction(3),
           'Fe': 10 + (dv('foundry_ss_line_kg_d') - mo_i - cr_i) + inv + r0, 'Zn': Fraction(1),
           'Al': al + al_i, 'Ti': (ti + mo + cr) + (ti_i + mo_i + cr_i)}
    assert sum(mix.values()) == S_exact - P + potm, 'the melt class mix must equal the charge'
    charge, time_h = dv('melt_charge_kg'), dv('melt_time_h')
    heats = ceil_f((S_exact + potm + flux) / charge)
    e_melt = sum((m * q[c] for c, m in mix.items()), Fraction(0)) + dv('melt_hold_kW') * time_h * heats
    kw_peak = D(ceil_f(charge * max(q.values()) / time_h * 2)) / 2     # largest cold heat
    e_roll = Fraction(32, 1000) * (mix['Cu'] + 10)                     # A-M-177 rolling class

    # crew textile line (A-M-429) and the C5 book — every R6 point takes a kg
    # Fraction and returns an integer mg count; counts re-enter as /10^6
    pp_c = _round_half_even(
        dv('POLYMERS.textile.textile_kg_person_yr') * dv('san_crew') / 365
        / ((1 + dv('POLYMERS.textile.fr_pickup_frac')) * dv('POLYMERS.textile.spin_yield')), 6)
    pp_in = Fraction(pp_c) / 10 ** 6
    sP = _round_half_even(P, 6)
    sP_kg = Fraction(sP) / 10 ** 6
    sS = _round_half_even(K + sP_kg + r0, 6)
    spotm = _round_half_even(potm, 6)
    sca = _round_half_even(ca, 6)
    sflux = _round_half_even(flux, 6)
    sslag = _round_half_even(f * Fraction(sS) / 10 ** 6, 6) + sflux + sca
    spf = _round_half_even(sP_kg * (1 + rej) + pp_in, 6)
    c5 = _round_half_even(Fraction(Decimal(str(E['CUT-1']['rate']['value']))), 6) \
        - _round_half_even(Fraction(Decimal(str(E['CUT-1-OUT']['rate']['value']))), 6) - spf
    # textile FR finish (X-QA-11, A-M-502): live where the P and NH3 lines run
    fr_live = (b.nodes.get('WS_PHOS', {}).get('presence') == 'present'
               and b.nodes.get('WS_AMMONIA', {}).get('presence') == 'present')
    fr_pickup = _round_half_even(dv('POLYMERS.textile.fr_pickup_frac') * pp_in
                                 * dv('POLYMERS.textile.spin_yield'), 6)
    fr_p = _round_half_even(Fraction(fr_pickup) / 10 ** 6 * M_H3PO4 / M_NH4_2HPO4, 6) if fr_live else 0
    fr_nh3 = _round_half_even(Fraction(fr_pickup) / 10 ** 6 * M_NH3_X2 / M_NH4_2HPO4, 6) if fr_live else 0
    textile = _round_half_even(dv('POLYMERS.textile.spin_yield') * pp_in
                               + (Fraction(fr_pickup) / 10 ** 6 if fr_live else 0), 6)
    scrap = _round_half_even(pp_in * (1 - dv('POLYMERS.textile.spin_yield')), 6)

    # on-site brine recovery (X-QA-11, A-M-496; A-M-503 pot feeds): the
    # salt_recovery design book on the foundry write grid
    cacl2_br = sca + _round_half_even(ca_cl2, 6)
    mgcl2_br = _round_half_even(mg_ti, 6) + _round_half_even(cl2_ti, 6) - _round_half_even(mgcl2_ret, 6)
    brine_feed = dv('brine_crys_feed_kg_d')
    brine_feed_mg = _round_half_even(brine_feed, 6)
    assert brine_feed_mg >= cacl2_br + mgcl2_br, 'the brine draw must carry the pot feeds'
    brine_ml = brine_feed_mg - cacl2_br - mgcl2_br
    assert brine_feed_mg == cacl2_br + mgcl2_br + brine_ml, 'the crystallizer draw must split exactly'
    brine_kw = dv('brine_crys_kW')

    # the silicon-loop chlorine make-up (A-M-472): si_route family's book,
    # read from the committed A-M-484 remap param (the strangler seed)
    si_cl2_f = (b.edges['IA-CA-CL2-SHIP'].get('params') or {}).get('si_cl2_kg_d')
    si_cl2 = Fraction(Decimal(str(si_cl2_f))) if si_cl2_f is not None else Fraction(0)

    # the documented v1 float-replica books (see module docstring)
    al_f = _flo(drv['foundry_al_line_kg_d']['value']) * _flo(Fraction(5, 4))
    ti_f = _flo(drv['foundry_ti_line_kg_d']['value']) * _flo(Fraction(5, 4))
    mo_f = _flo(drv['foundry_mo_add_kg_d']['value']) * _flo(Fraction(5, 4))
    cr_f = _flo(drv['foundry_cr_add_kg_d']['value']) * _flo(Fraction(5, 4))
    al_rec_f = min(al_f, _flo(E['IA-FEED-01']['rate']['value']) * _flo(al_frac))
    al_chlor_f = al_rec_f * 3 * _flo('35.453') / _flo('26.9815')
    # the v1 float r0 (the float-arithmetic shop residual) and its raw mix
    # consumer: CONT_CAST cad billet_kg_d = mix['Fe'] stores the raw float
    _r, _gi, _go = _flo('0'), _flo('0'), _flo('0')
    _goods_f = _flo('0')
    for e in b.data['edges']:
        if e['presence'] != 'present' or 'mass' not in (e.get('layers') or []) \
                or (e.get('rate') or {}).get('unit') != 'kg/d':
            continue
        val = e['rate'].get('value')
        if not isinstance(val, (int, float)):
            continue
        sid = e['stream_id']
        v = float(val or 0)
        if sid == 'IA-GOODS-SHIP':
            _goods_f = v
            continue
        if e['to_unit_id'] == 'MFG_SHOP':
            _gi += v
        if e['from_unit_id'] == 'MFG_SHOP' and sid != 'IA-MFG-OUT':
            _go += v
    _seed_f = round(_gi - _go, 6)
    _goods_eff = _seed_f if (_seed_f > 0 and abs(_goods_f - _seed_f) > _flo('1e-9')) else _goods_f
    for e in b.data['edges']:
        if e['presence'] != 'present' or 'mass' not in (e.get('layers') or []) \
                or (e.get('rate') or {}).get('unit') != 'kg/d':
            continue
        sid = e['stream_id']
        if sid in ('MFG_SCRAP_TO_IND', 'STOCK_TO_MFG', 'POLY_TO_MFG'):
            continue
        val = e['rate'].get('value')
        if not isinstance(val, (int, float)):
            continue
        v = float(val or 0)
        if e['to_unit_id'] == 'MFG_SHOP':
            _r += v
        elif e['from_unit_id'] == 'MFG_SHOP':
            _r -= _goods_eff if sid == 'IA-GOODS-SHIP' else v
    r0_f = _r
    fe_f = _flo('10.0') + (_flo('1.5') - _flo('0.05') - _flo('0.2')) + _flo('2.0') + r0_f

    return dict(drv=drv, r0=r0, K=K, f=f, rej=rej, P=P, S_exact=S_exact, sP=sP, sS=sS,
                xf=xf, al_i=al_i, ti_i=ti_i, mo_i=mo_i, cr_i=cr_i, al=al, ti=ti, mo=mo, cr=cr,
                potm=potm, spotm=spotm, ca=ca, sca=sca, alcl3=alcl3, al_cl2=al_cl2,
                al_frac=al_frac, al_rec=al_rec, al_cake=al_cake, alcl3_rec=alcl3_rec,
                alcl3_mu=alcl3_mu, al_chlor_cl2=al_chlor_cl2, char_al=char_al, al_co=al_co,
                al_h2o=al_h2o, cacl2=cacl2, ca_cl2=ca_cl2, tio2=tio2, c_ti=c_ti, cl2_ti=cl2_ti,
                mg_ti=mg_ti, mgcl2_g=mgcl2_g, mgcl2_ret=mgcl2_ret, mgcl2_mu=mgcl2_mu, co_ti=co_ti,
                kroll_flux=kroll_flux, flux=flux, sflux=sflux, sslag=sslag, moo3=moo3, c_mo=c_mo,
                co2_mo=co2_mo, cr2o3=cr2o3, c_cr=c_cr, co_cr=co_cr, sh=sh, sh_mu=sh_mu,
                sh_recl=sh_recl, wx=wx, wx_mu=wx_mu, wx_recl=wx_recl, wx_burn=wx_burn,
                inv=inv, cont=cont, cont_roll=cont_roll, cont_stock=cont_stock,
                stock_in=stock_in, pot_e=pot_e, q=q, mix=mix, e_melt=e_melt,
                kw_peak=kw_peak, e_roll=e_roll, heats=heats, charge=charge, time_h=time_h,
                pp_in=pp_in, spf=spf, c5=c5, fr_live=fr_live, fr_pickup=fr_pickup,
                fr_p=fr_p, fr_nh3=fr_nh3, textile=textile, scrap=scrap,
                cacl2_br=cacl2_br, mgcl2_br=mgcl2_br, brine_feed=brine_feed,
                brine_ml=brine_ml, brine_kw=brine_kw, si_cl2=si_cl2, si_cl2_f=si_cl2_f, ce=ce,
                al_f=al_f, ti_f=ti_f, mo_f=mo_f, cr_f=cr_f, al_chlor_f=al_chlor_f,
                r0_f=r0_f, fe_f=fe_f)


def _assert_seed_topology(b):
    """The composer lane owns the topology; the seed must carry it. Fail
    loudly on drift (the process-family seed-contract pattern)."""
    endpoints = {'IA-AL-CAKE': ('LEACH_CSTR_1', 'AL_POT'), 'CHAR_TO_AL': ('OIL_PYRO', 'AL_POT'),
                 'IA-AL-CO': ('AL_POT', 'NORTH_DOCK'), 'IA-AL-H2O': ('AL_POT', 'ATMOS'),
                 'IA-MGCL2-KROLL': ('TI_CELL', 'MG_POT'), 'IA-KROLL-FLUX': ('TI_CELL', 'FLUX_PREP'),
                 'IA-MG-TI': ('MG_POT', 'TI_CELL'), 'IA-CL2-MG-TI': ('MG_POT', 'TI_CELL'),
                 'IA-CA-CL2-SHIP': ('CA_POT', 'NORTH_DOCK'), 'IA-TIO2-MU': ('NORTH_DOCK', 'TI_CELL'),
                 'CHAR_TO_TI': ('OIL_PYRO', 'TI_CELL'), 'IA-MOO3-MU': ('NORTH_DOCK', 'MO_CELL'),
                 'CHAR_TO_MO': ('OIL_PYRO', 'MO_CELL'), 'IA-MO-VENT': ('MO_CELL', 'NORTH_DOCK'),
                 'IA-CR2O3-MU': ('NORTH_DOCK', 'CR_CELL'), 'CHAR_TO_CR': ('OIL_PYRO', 'CR_CELL'),
                 'IA-CR-VENT': ('CR_CELL', 'NORTH_DOCK'), 'IA-WAX-CUT': ('PROD_C19_C28', 'WAX_PATTERN'),
                 'IA-SIL-SHOP': ('MFG_SHOP', 'SHELL_BUILD'), 'IA-BURNOUT-VENT': ('SHELL_BURNOUT', 'NORTH_DOCK'),
                 'IA-SHELL-RECLAIM': ('SHELL_BREAK', 'SHELL_BUILD'), 'IA-SHELL-SHOP': ('SHELL_BREAK', 'MFG_SHOP'),
                 'IA-C5-POLY': ('PROD_C5_C10', 'POLY_OLEFIN'), 'IA-METAL-SHIP': ('METAL_STORE', 'NORTH_DOCK')}
    for sid, (a, zb) in endpoints.items():
        e = b.edges[sid]
        assert (e['from_unit_id'], e['to_unit_id']) == (a, zb), f'{sid} names another stream'
    retired = ('IA-ALCL3-MU', 'IA-CL2-SHIP', 'IA-MGCL2-MU', 'IA-CACL2-MU', 'IA-WAX-MU',
               'IA-SILICA-MU', 'IA-SHELL-EXPORT', 'IA-C-TI', 'IA-C-MO', 'IA-C-CR', 'FR_FINISH')
    for sid in retired:
        assert b.edges[sid].get('presence') == 'retired', f'{sid} presence drifted from retired'
    assert b.edges['IA-WAX-CUT'].get('from_sector_id') == 'OIL', 'IA-WAX-CUT sector re-point missing'
    assert all(e.get('stream_id') != 'IA-CA-TO-PCA' for e in b.data['edges']), \
        'the interim IA-CA-TO-PCA edge is retired by the composer lane, not present'
    for u in BRINE_HOSTS:
        assert (b.nodes.get(u) or {}).get('presence') == 'present', \
            'the brine route lands only where the leach and the pots run (A-M-496)'
        assert 'BRINE_CRYS' in b.nodes, 'the BRINE_CRYS node is composer-authored seed'
    for sid, a, zb in BRINE_STREAMS:
        e = b.edges[sid]
        assert (e['from_unit_id'], e['to_unit_id']) == (a, zb), f'{sid} names another stream'
        assert e.get('presence') == 'present', f'{sid} presence drifted'


# ---- the family function -------------------------------------------------------

@fn('foundry_poly', 'AQS-DUTY-072/073 foundry + polymers sizing (X-PAR-02 TF): the recovery-sized '
    'aluminium line (X-QA-19, A-M-495), the pot/Kroll books (A-M-280..284, A-M-290), the on-site brine '
    'recovery (X-QA-11, A-M-496, A-M-503), the investment train (A-M-286, A-M-498), the melt-shop '
    'closure (A-M-257, A-M-261 rev), the recovery-first records (A-M-499) and the crew textile line '
    '(A-M-429, A-M-502)')
def foundry_poly(b, inputs):
    s = _core(b, inputs)
    if s is None:
        return                                    # bridge contract: no drivers, no stamps
    _assert_seed_topology(b)
    ce_str = dstr(s['ce'])

    def rv(x):
        return unbook(_round_half_even(x, 6), 6)

    def rv_c(c):
        return unbook(int(c), 6)                  # an integer mg count -> exact decimal

    def kv(x):
        return unbook(_round_half_even(x, 4), 4)

    def tv(x):
        return unbook(_round_half_even(x, 2), 2)

    # ---- foundry: live scrap-remelt loop + pot/cell/Kroll metal ---------------
    basis = f'the scrap-remelt melt loop and pot-metal ledger ({DOC_F}; A-M-261 rev, A-M-257, A-M-262, A-M-285)'
    _rate(b, 'MFG_SCRAP_TO_IND', rv_c(s['sS']),
          f'Shop scrap (charge) to the melt; closes MFG_SHOP on the store draws ({DOC_F}, A-M-261 rev). | {TAG}.',
          basis)
    _rate(b, 'FOUNDRY_SLAG_TO_LEACH', rv_c(s['sslag']),
          f'Melt slag+dross {pct(s["f"], 0)} of charge plus the {fmt(s["flux"], 4)} kg/d salt-flux pass-through by mass '
          f'conservation on the melt (INDUCT_SOCX 1-2 % band, A-M-262); returns to the leach. | {TAG}.', basis)
    _rate(b, 'IND_MELT_TO_CAST', float(3),
          f'Cu-class melt to the cast line: bus/winding stock (AQS-SIZE-FOUNDRY Cu 3 kg/d). | {TAG}.', basis)
    ind_to_cont = (s['sS'] + s['spotm'] + s['sca'] + s['sflux'] - 3000000
                   - s['inv'] * 1000000 - s['sslag'])
    _rate(b, 'IND_TO_CONT', rv_c(ind_to_cont),
          f'Melt to the semi-continuous caster by difference on the melt: Fe 11.5 (10 low-alloy + 1.5 stainless base) '
          f'+ Zn 1 + pot metal {fmt(s["potm"], 4)} (Al {fmt(s["al"], 1)} / Ti {fmt(s["ti"], 2)} / Mo {fmt(s["mo"], 4)} / '
          f'Cr {fmt(s["cr"], 2)}, A-M-261 rev table). | {TAG}.', basis)
    _rate(b, 'CAST_SCRAP_TO_IND', float(0),
          'Near-net permanent-mold pours at 3 kg/d; sprue/runner returns are campaign events, not a daily '
          f'continuous rate (the melt loop closes on MFG_SCRAP_TO_IND). | {TAG}.', basis)
    _rate(b, 'CAST_TO_ROLL', float(3),
          f'Cu cast stock to rolling (bus bar / winding strip, FOUNDRY_DESIGN machine table). | {TAG}.', basis)
    _rate(b, 'CAST_TO_EXTRUDE', float(0),
          'EXTRUDE is ROLL\'s N+1 alternate (A-M-283): standby-zero on the design day; the Cu line rolls. | {TAG}.',
          basis)
    _rate(b, 'CONT_TO_ROLL', float(10), f'Fe billet to rolling (AQS-SIZE-FOUNDRY Fe 10). | {TAG}.', basis)
    _rate(b, 'CONT_TO_STOCK', rv_c(ind_to_cont - 10000000),
          f'As-cast stock by difference: Zn 1 + stainless base 1.5 + pot metal {fmt(s["potm"], 4)} ingot to stock. | '
          f'{TAG}.', basis)
    _rate(b, 'ROLL_TO_STOCK', float(13), f'Rolled plate/sheet stock (Cu 3 + Fe 10). | {TAG}.', basis)
    _rate(b, 'STOCK_TO_MFG', rv(s['K']),
          f'Formed stock to the shop = the foundry product demand: the full AQS-SIZE-FOUNDRY consumable-replacement '
          f'table Cu 3 + Fe 10 + Zn/EW 1 + Al {fmt(s["al_i"], 4)} + stainless 1.5 + Ti 0.40 + investment castings 2 = '
          f'{fmt(s["K"], 1)} kg/d (A-M-261 rev: the Al line is sized to the recoverable aluminium, X-QA-19, A-M-495). | '
          f'{TAG}.', basis)
    _rate(b, 'STOCK_TO_WIRE_DRAW', float(0),
          'WIRE_DRAW (MFG) closes on S57 Cu from MET_MELT (A-M-177 line); no foundry wire draw at the '
          f'bounding case (A-M-257 by-difference pattern). | {TAG}.', basis)
    for sid, why in (('EXTRUDE_TO_STOCK', 'EXTRUDE standby-zero: ROLL N+1 alternate (A-M-283), energized on a '
                      'roll-stand outage'),
                     ('DRAW_TO_STOCK', 'DRAW standby-zero: ROLL N+1 alternate (A-M-283); wire sizing is MFG '
                      'WIRE_DRAW S57'),
                     ('SINTER_TO_STOCK', 'SINTER standby-zero: consolidation N+1 alternate (A-M-283); powder path '
                      'optional'),
                     ('ATOM_TO_STOCK', 'Gas-atomizer powder path optional, not baseline (FOUNDRY_INTEGRATION)'),
                     ('IND_TO_ATOM', 'No powder demand on IND_MELT at the bounding case')):
        _rate(b, sid, float(0), f'{why}. | {TAG}.', basis)

    # ---- pot cells: the recovery-sized aluminium line (X-QA-19, A-M-495) ------
    basis_al = 'the recovery-sized aluminium line (X-QA-19 owner ruling, A-M-495; A-M-282 Faraday, A-M-285 margin)'
    _rate(b, 'IA-ALCL3-MU', float(0),
          f'Retired by the recovery-sized aluminium line (X-QA-19 owner ruling, A-M-495): the chlorinator makes the whole '
          f'AlCl3 feed on site from the recovered hydroxide cake ({fmt(s["alcl3_rec"], 4)} kg/d on IA-AL-CAKE, calcined and '
          f'carbochlorinated with the pot chlorine {fmt(s["al_chlor_cl2"], 4)} kg/d on the internal cell loop) and the Al stock '
          f'line is sized to the recoverable aluminium ({fmt(s["al_i"], 4)} kg/d at the A-M-285 margin, driver '
          f'foundry_al_line_kg_d), so there is no shortfall to import. Was the anhydrous AlCl3 make-up of the '
          f'demand-sized Al line (process-chemical import, pending class; A-M-261 table before the X-QA-19 resize). | {TAG}.',
          basis_al)
    _rate(b, 'IA-AL-CAKE', rv(s['al_cake']),
          f'The reference feed carries {fmt(s["al_frac"], 3)} Al (AQS-ASSAY-001 section 3) = {fmt(s["al_rec"], 4)} kg/d Al, '
          f'precipitated with the 20 wt% NaOH dose (IA-BASE-PPT basis); drawn as the hydroxide cake at '
          f'{fmt((MM["Al"] + 3 * (MM["O"] + MM["H"])) / MM["Al"], 3)} kg/kg Al and netted off the sink-circuit solids '
          f'(IA-SINK-01 / IA-WET-FLOAT-01 each less the same mass). | {TAG}.', basis_al)
    _rate(b, 'CHAR_TO_AL', rv(s['char_al']),
          f'Al2O3 + 3 C + 3 Cl2 -> 2 AlCl3 + 3 CO (GREENWOOD carbochlorination class): '
          f'{fmt(3 * MM["C"] / (2 * MM["Al"]), 3)} kg C per kg Al on the recovered cake; from the pyrolysis char pool '
          f'(IA-CHAR by difference). | {TAG}.', basis_al)
    _rate(b, 'IA-AL-CO', rv(s['al_co']),
          f'{fmt(3 * (MM["C"] + MM["O"]) / (2 * MM["Al"]), 3)} kg CO per kg Al chlorinated on the recovered cake; dock '
          f'fuel-gas class (IA-KROLL-CO precedent). | {TAG}.', basis_al)
    _rate(b, 'IA-AL-H2O', rv(s['al_h2o']),
          f'2 Al(OH)3 -> Al2O3 + 3 H2O before the chlorination (GREENWOOD): '
          f'{fmt(3 * (2 * MM["H"] + MM["O"]) / (2 * MM["Al"]), 3)} kg/d water per kg/d Al in the cake. | {TAG}.', basis_al)
    _rate(b, 'AL_POT_TO_IND', rv(s['al']),
          f'Al metal to the melt: molten AlCl3-(NaCl-KCl) electrolysis 2AlCl3 -> 2Al + 3Cl2 at 700 C, '
          f'{ffmt(s["pot_e"]["AL_POT"]["I_A"], 0)} A at CE {ce_str} (A-M-282); '
          f'{fmt(s["al_i"], 0)} kg/d line + {fmt(s["al"] - s["al_i"], 1)} export surplus (A-M-285). | {TAG}.', basis_al)
    _rate(b, 'IA-CL2-SHIP', float(0),
          'Retired by the recovery-sized aluminium line (X-QA-19, A-M-495): the pot Cl2 byproduct closes exactly on the '
          'cake chlorination (the same 3.942 kg/kg Al produced on the cell and drawn on the internal chlorination loop), so '
          'AL_POT has no chlorine surplus to export; the dock chlorine product is the CA_POT share on IA-CA-CL2-SHIP, net of '
          'the silicon-loop make-up (A-M-472) and the photoresist draw (A-M-482). Was the pot Cl2 export net of the '
          f'silicon-loop make-up and the {fmt(s["al_chlor_cl2"], 4)} kg/d cake chlorination (F-20261110-07; A-M-290 chlorine '
          f'ruling). | {TAG}.', basis_al)
    _edge_field(b, 'IA-CL2-SHIP', 'params.base_kg_d', float(0),
                basis_al + '; the fluoro pass reads this base every pass (A-M-481 HCL_OX branch)')
    _edge_field(b, 'IA-CL2-SHIP', 'params.al_chlor_cl2_kg_d', s['al_chlor_f'],
                basis_al + '; the on-site AlCl3 chlorination draw at the v1 float book (A-M-495)')

    # ---- the Mg/Ca pot feeds and the on-site brine recovery (A-M-496/503) -----
    basis_mg = 'the Kroll Mg recycle book (AQS-BAL-KROLL closure; A-M-284, A-M-290; A-M-282 Faraday)'
    _rate(b, 'IA-MGCL2-KROLL', rv(s['mgcl2_ret']),
          f'AQS-BAL-KROLL closure: {fmt(2 * (MM["Mg"] + 2 * MM["Cl"]) / MM["Ti"], 3)} kg/kg Ti gross less the '
          f'{fmt(s["kroll_flux"], 4)} kg/d drag-out to FLUX_PREP (A-M-284). | {TAG}.', basis_mg)
    _rate(b, 'IA-KROLL-FLUX', rv(s['kroll_flux']),
          f'{pct(s["drv"]["foundry_kroll_dragout_frac"]["value"] and rat(s["drv"]["foundry_kroll_dragout_frac"]["value"]), 0)} '
          f'of the Kroll MgCl2 gross: the salt-flux cover for the Al-charged melt (A-M-284); unblocks FLUX_PREP from the '
          f'SALT_FEED stub. | {TAG}.', basis_mg)
    _rate(b, 'IA-MGCL2-MU', float(0),
          f'Retired by the on-site brine recovery (X-QA-11, A-M-496): the make-up was the Kroll drag-out, '
          f'{fmt(s["mgcl2_mu"], 4)} kg/d MgCl2-equivalent cycling flux -> melt -> slag -> leach; BRINE_CRYS crystallizes it '
          f'back out of the leach chlorides and feeds the pot at the same rate on IA-BRINE-MGCL2, so MG_POT still '
          f'delivers the retort Mg exactly. Was the dock process-chemical import (A-M-284, pending class). | {TAG}.',
          basis_mg)
    _rate(b, 'IA-MG-TI', rv(s['mg_ti']),
          f'{fmt(2 * MM["Mg"] / MM["Ti"], 3)} kg Mg per kg Ti (AQS-BAL-KROLL); MG_POT electrolysis of the returned MgCl2 at '
          f'{ffmt(s["pot_e"]["MG_POT"]["I_A"], 0)} A (A-M-282). | {TAG}.', basis_mg)
    _rate(b, 'IA-CL2-MG-TI', rv(s['cl2_ti']),
          f'Chlorine closes internally (AQS-BAL-KROLL): MG_POT returns exactly the {fmt(4 * MM["Cl"] / MM["Ti"], 3)} kg/kg Ti '
          f'the chlorination draws; the EW anode gas stays booked to the leach (Faraday balance, A-M-255 pattern; '
          f'A-M-284 ruling - it is the initial loop charge only). | {TAG}.', basis_mg)
    _rate(b, 'MG_POT_TO_IND', float(0),
          'MG_POT serves only the Kroll recycle at steady state (all Mg to the retort on IA-MG-TI); no Mg stock line '
          f'at the table. | {TAG}.', basis_mg)
    _rate(b, 'MG_POT_CL2', float(0),
          f'MG_POT Cl2 fully serves the chlorinator (IA-CL2-MG-TI); no CRU surplus. | {TAG}.', basis_mg)
    basis_ca = 'the Ca deoxidizer pot and its chlorine export (A-M-284, A-M-290, A-M-472, A-M-495, A-M-496)'
    _rate(b, 'IA-CACL2-MU', float(0),
          f'Retired by the on-site brine recovery (X-QA-11, A-M-496): the pot feed carried the Ca deoxidizer addition '
          f'{fmt(s["ca"], 4)} kg/d at {pct(rat(s["drv"]["foundry_ca_add_frac"]["value"]), 2)} of the melt charge; the Ca reports to the '
          f'dross and leach liquor as CaCl2 (the pot chlorine leaves separately as the IA-CA-CL2-SHIP product export), '
          f'and BRINE_CRYS crystallizes the make-up back out of the leach chlorides on IA-BRINE-CACL2 at the same rate. '
          f'Was the dock process-chemical import (A-M-284, pending class). | {TAG}.', basis_ca)
    _rate(b, 'CA_POT_TO_IND', rv(s['ca']),
          'Ca deoxidizer/desulfurizer addition to the melt (steelmaking practice class); sized at '
          f'{pct(rat(s["drv"]["foundry_ca_add_frac"]["value"]), 2)} of the melt charge - the same Ca line serves the grease-thickener '
          f'Ca(OH)2 draw (AQS-DUTY-GREASE) when the P_CA param pass rates the cake. | {TAG}.', basis_ca)
    ca_cl2_ship = s['ca_cl2'] - s['si_cl2']
    _ca_ship = dict(b.edges['IA-CA-CL2-SHIP']['rate'])
    _ca_ship['value'] = rv(ca_cl2_ship)
    b.set_edge_rate('IA-CA-CL2-SHIP', _ca_ship,
                    _prov(basis_ca + '; value-only update (the photoresist netting co-authors the note, A-M-482)'))
    _edge_field(b, 'IA-CA-CL2-SHIP', 'params.si_cl2_kg_d', s['si_cl2_f'],
                basis_ca + '; si_refine.tf moves the export by any later change of this make-up (A-M-484); '
                'the si_route book, passed through verbatim')
    # the crystallizer book (salt_recovery.design, A-M-503 pot feeds on the foundry write grid)
    basis_br = f'{TAG_SR}: the crystallizer balance and pot-feed rates (A-M-496 draw drivers, A-M-503 pot feeds)'
    br_book = {'feed_kg_d': _round_half_even(s['brine_feed'], 6), 'cacl2_kg_d': s['cacl2_br'],
               'mgcl2_kg_d': s['mgcl2_br'], 'ml_kg_d': s['brine_ml']}
    for sid, a, zb in BRINE_STREAMS:
        key = {sid: k for sid, _a, _z, k in
               (('IA-BRINE-SRC', 0, 0, 'feed_kg_d'), ('IA-BRINE-CACL2', 0, 0, 'cacl2_kg_d'),
                ('IA-BRINE-MGCL2', 0, 0, 'mgcl2_kg_d'), ('IA-BRINE-ML', 0, 0, 'ml_kg_d'))}[sid]
        note = f"{TAG_SR}: {key.replace('_kg_d', '')} = {fmt(Fraction(br_book[key]) / 10 ** 6, 6)} kg/d " \
               f"(salt_recovery.py)."
        if sid == 'IA-BRINE-MGCL2':
            _rate(b, sid, rv_c(br_book[key]), note, basis_br)
        else:
            # value-only: the balance reconciler re-solves these three and
            # appends its AQS-PAR-003 marker to the salt_recovery note
            _e = dict(b.edges[sid]['rate'])
            _e['value'] = rv_c(br_book[key])
            b.set_edge_rate(sid, _e, _prov(basis_br + '; value-only update (the balance reconciler owns the note)'))
    _kw_dict(b, 'BRINE_CRYS', kv(s['brine_kw']),
             f'{TAG_SR}: crystallizer jacket and vacuum ejector at the {fmt(s["brine_feed"], 2)} kg/d side-stream '
             f'(brine_crys_kW, A-M-496).', basis_br)
    _kw_rate(b, 'SF-BRINE_CRYS', kv(s['brine_kw']),
             f'{TAG_SR}: feed equal to BRINE_CRYS continuous_kw.', basis_br)
    _set(b, 'BRINE_CRYS', 'params.design',
         {k: rv_c(v) for k, v in (('cacl2_kg_d', br_book['cacl2_kg_d']), ('mgcl2_kg_d', br_book['mgcl2_kg_d']),
                                  ('feed_kg_d', br_book['feed_kg_d']),
                                  ('ml_kg_d', br_book['ml_kg_d']), ('kw', _round_half_even(s['brine_kw'], 6)))},
         basis_br)

    # ---- Kroll cells: dock oxide concentrates + carbon, internal chlorine ----
    basis_kr = 'the Kroll and Mo/Cr carbochlorination cells (AQS-BAL-KROLL; A-M-284, A-M-290, F-20261110-07)'
    _rate(b, 'IA-TIO2-MU', rv(s['tio2']),
          f'D-DOCK feedstock import (A-M-284): {fmt((MM["Ti"] + 2 * MM["O"]) / MM["Ti"], 3)} kg/kg Ti on the oxide-equivalent '
          f'basis (AQS-BAL-KROLL); concentrate grade envelope TiO2 90-97 wt%, design point 94 % (A-M-284 '
          f'needs_verification: XRF assay of the accepted lot). | {TAG}.', basis_kr)
    _rate(b, 'CHAR_TO_TI', rv(s['c_ti']),
          '2 C per TiO2 chlorinated (AQS-BAL-KROLL); the Kroll carbon re-points to the plant char pool '
          f'(F-20261110-07: plant pyrolysis char is a recovered stream, so no carbon imports while the pool holds). | '
          f'{TAG}.', basis_kr)
    _rate(b, 'IA-C-TI', float(0),
          'Retired by recovery-first carbon (F-20261110-07): the Kroll reductant is plant pyrolysis char on '
          'CHAR_TO_TI; the dock carbon import does not return unless the char pool runs short.', basis_kr)
    _rate(b, 'METALS_TO_IND_MELT', rv(s['ti']),
          f'Ti sponge to the melt under salt flux: {fmt(s["ti"], 2)} kg/d = 0.40 line + export margin (A-M-285); the vacuum '
          f'consolidation path (VAC_IND_TI) is the N+1 quality route, standby-zero (A-M-283). | {TAG}.', basis_kr)
    _rate(b, 'TI_CELL_SLAG_RETURN', float(0),
          'Oxide-equivalent feed leaves no grit slag on the design basis; the gangue/Fe terms are the assay-day task '
          f'(A-M-284 envelope: the real concentrate assay re-points the feed to FLOAT_SINK grit when it lands). | {TAG}.',
          basis_kr)
    _rate(b, 'TI_CELL_CL2_TO_CRU', float(0),
          f'Kroll chlorine closes on the Mg pot loop (IA-CL2-MG-TI); the CRU tap is purge-only. | {TAG}.', basis_kr)
    _rate(b, 'VAC_IND_TI', float(0),
          f'VAC_IND is the N+1 diverse melt path (A-M-283): standby-zero on the design day. | {TAG}.', basis_kr)
    _rate(b, 'VAC_IND_TO_VAC_CAST', float(0),
          f'VAC_CAST rides VAC_IND (N+1 pair, A-M-283): standby-zero. | {TAG}.', basis_kr)
    _rate(b, 'IA-MOO3-MU', rv(s['moo3']),
          f'D-DOCK feedstock import (A-M-284): {fmt((MM["Mo"] + 3 * MM["O"]) / MM["Mo"], 3)} kg/kg Mo oxide-equivalent; '
          f'tech-oxide grade envelope 95-99 wt% MoO3, design 98 % (A-M-284 assay-verification task). | {TAG}.', basis_kr)
    _rate(b, 'CHAR_TO_MO', rv(s['c_mo']),
          f'1.5 C per MoO3 on the Mo(III) chloride route (A-M-284); plant pyrolysis char pool '
          f'(F-20261110-07, as CHAR_TO_TI). | {TAG}.', basis_kr)
    _rate(b, 'IA-C-MO', float(0),
          'Retired by recovery-first carbon (F-20261110-07), as IA-C-TI: the molybdenum chlorinator '
          'reductant is plant pyrolysis char on CHAR_TO_MO.', basis_kr)
    _rate(b, 'MO_TO_IND', rv(s['mo']),
          'Mo metal to the melt: carbochlorination to MoCl3 then molten-salt electrolysis MoCl3 -> Mo + 1.5Cl2 with the '
          f'anode gas recycled to the chlorination (internal chlorine loop, A-M-290); {fmt(s["mo_i"], 2)} kg/d 316-class '
          f'addition + export margin. | {TAG}.', basis_kr)
    _rate(b, 'MO_CELL_RAFFINATE', float(0),
          'Oxide feed has no liquor raffinate; the EW_9 stub stays retired (A-M-255). | {TAG}.', basis_kr)
    _rate(b, 'MO_CELL_ANODE_GAS_TO_CRU', float(0),
          f'Anode gas recycles to the cell chlorination step (A-M-290); CRU tap purge-only. | {TAG}.', basis_kr)
    _rate(b, 'EW9_LIQUOR_TO_MO', float(0),
          'A-M-255 alias retired: EW_9 liquor tail fully booked on IA-EW-09 to POLISH_BANK; the Mo feed is the dock '
          f'oxide import (IA-MOO3-MU, A-M-284). | {TAG}.', basis_kr)
    _rate(b, 'EW_METALS_TO_IND', float(0),
          'A-M-255 alias retired: EW_9 metal harvest fully booked on IA-EW-MET-9 and IA-EW-SHEET; the melt is fed on '
          f'shop scrap + pot metal. | {TAG}.', basis_kr)
    _rate(b, 'IA-MO-VENT', rv_c(_round_half_even(s['moo3'], 6) + _round_half_even(s['c_mo'], 6)
                                - _round_half_even(s['mo'], 6)),
          f'1.5 CO2 per Mo on the carbochlorination net (A-M-284); dock vent class. | {TAG}.', basis_kr)
    _rate(b, 'IA-CR2O3-MU', rv(s['cr2o3']),
          f'D-DOCK feedstock import (A-M-284): {fmt((2 * MM["Cr"] + 3 * MM["O"]) / (2 * MM["Cr"]), 3)} kg/kg Cr '
          f'oxide-equivalent; chromite class envelope 40-52 wt% Cr2O3, design 46 % (A-M-284 assay-verification task; the '
          f'Fe/Mg/Al gangue balance is the assay-day follow-up). | {TAG}.', basis_kr)
    _rate(b, 'CHAR_TO_CR', rv(s['c_cr']),
          f'3 C per Cr2O3 on the Cr(III) chloride route (A-M-284); plant pyrolysis char pool '
          f'(F-20261110-07, as CHAR_TO_TI). | {TAG}.', basis_kr)
    _rate(b, 'IA-C-CR', float(0),
          'Retired by recovery-first carbon (F-20261110-07), as IA-C-TI: the chromium chlorinator '
          'reductant is plant pyrolysis char on CHAR_TO_CR.', basis_kr)
    _rate(b, 'CR_TO_IND', rv(s['cr']),
          'Cr metal to the melt: carbochlorination to CrCl3 then molten-salt electrolysis 2CrCl3 -> 2Cr + 3Cl2 with the '
          f'anode gas recycled internally (A-M-284); {fmt(s["cr_i"], 2)} kg/d stainless addition + export margin. | {TAG}.',
          basis_kr)
    _rate(b, 'FLOAT_SINK_GRIT_TO_TI', float(0),
          'Internal dense-grit feed superseded by the dock rutile class at the design point; the assay-day task can '
          f're-point the feed to the grit when AQS-ASSAY-TI-MO lands (A-M-284). | {TAG}.', basis_kr)
    _rate(b, 'IA-CR-VENT', rv_c(_round_half_even(s['cr2o3'], 6) + _round_half_even(s['c_cr'], 6)
                                - _round_half_even(s['cr'], 6)),
          f'3 CO per 2 Cr on the carbochlorination net (A-M-284); dock fuel-gas class. | {TAG}.', basis_kr)

    # ---- investment casting: wax cut blend + foundry silica (A-M-286/498) -----
    basis_inv = 'the investment casting train (A-M-286; the C19-C28 wax blend A-M-498; recovery-first silica F-20261110-06)'
    _rate(b, 'IA-WAX-MU', float(0),
          f'Retired by the on-site wax blend (X-QA-11, A-M-498): the make-up {fmt(s["wx_mu"], 4)} kg/d draws from the '
          f'plant C19-C28 cut tank on IA-WAX-CUT (the same paraffin cut the wax chain runs on), blended with the '
          f'dewax reclaim {fmt(s["wx_recl"], 1)} kg/d to the pattern-wax spec. Was the dock petro-wax import '
          f'(A-M-284, pending class). | {TAG}.', basis_inv)
    _rate(b, 'IA-WAX-CUT', rv(s['wx_mu']),
          f'Pattern-room make-up {fmt(s["wx_mu"], 4)} kg/d ({pct(1 - rat(s["drv"]["foundry_inv_wax_reclaim_frac"]["value"]), 0)} of the '
          f'{fmt(s["wx"], 1)} kg/d pattern wax; the dewax reclaim {fmt(s["wx_recl"], 1)} covers the rest, A-M-286): drawn from '
          f'the C19-C28 cut tank (the plant paraffin cut, A-M-498), netted off IA-C19-SHIP in ess_tf. | {TAG}.', basis_inv)
    _edge_field(b, 'IA-WAX-CUT', 'composition', {'C19-C28': float(1)},
                basis_inv + '; the stream is the plant paraffin cut')
    _rate(b, 'IA-SILICA-MU', float(0),
          f'Retired by recovery-first silica (F-20261110-06): the shell make-up {fmt(s["sh_mu"], 4)} kg/d is the recovered crib '
          f'and spent-shell silica pool on IA-SIL-SHOP (the plant silica surplus after the silicon furnace burden); the dock '
          f'import does not return while the pool holds. Was the '
          f'{pct(1 - rat(s["drv"]["foundry_inv_shell_reclaim_frac"]["value"]), 1)} make-up of the {fmt(s["sh"], 1)} kg/d green shell '
          f'(AQS-SIZE-FOUNDRY 0.5 kg/kg-casting line, A-M-286). | {TAG}.', basis_inv)
    _rate(b, 'IA-SIL-SHOP', rv(s['sh_mu']),
          'Recovery-first silica make-up (F-20261110-06): the shop recovered-silica pool (the S08 crib silicate, A-M-490, '
          f'plus the spent-shell surplus on IA-SHELL-SHOP) covers the shell make-up {fmt(s["sh_mu"], 4)} kg/d that imported; '
          f'GLASS_DIGEST stays fully committed (IA-GLASS-03 30.0 = S08G 26.7 + IA-SIL-SRC 3.3). | {TAG}.', basis_inv)
    _rate(b, 'WAX_TO_SHELL', rv(s['wx']),
          f'{fmt(s["wx"], 1)} kg/d wax patterns at 1 kg/kg castings (A-M-286). | {TAG}.', basis_inv)
    _rate(b, 'SHELL_TO_BURNOUT', rv(s['sh'] + s['wx']),
          f'Green shell {fmt(s["sh"], 1)} kg/d (6-dip class, 4 kg/kg castings) + patterns {fmt(s["wx"], 1)} (A-M-286). | {TAG}.',
          basis_inv)
    _rate(b, 'WAX_RECLAIM_TO_PATTERN', rv(s['wx_recl']),
          f'Dewax condensate reclaim {pct(rat(s["drv"]["foundry_inv_wax_reclaim_frac"]["value"]), 0)} of the pattern wax (A-M-286). | {TAG}.',
          basis_inv)
    _rate(b, 'WAX_TO_OIL', float(0),
          f'Unrecovered wax ({fmt(s["wx_burn"], 2)} kg/d) burns in the flash-dewax firebox (A-M-286); no oil-line draw. | {TAG}.',
          basis_inv)
    _rate(b, 'IA-BURNOUT-VENT', rv(s['wx_burn']),
          f'Balance of the pattern wax at the burnout firebox (A-M-286); dock vent class. | {TAG}.', basis_inv)
    _rate(b, 'BURNOUT_TO_CAST', rv(s['sh']),
          f'Fired shell {fmt(s["sh"], 1)} kg/d to the pour station (A-M-286). | {TAG}.', basis_inv)
    _rate(b, 'IND_TO_INV', rv(s['inv']),
          f'Melt to the investment pour: the live melt output at the {fmt(s["inv"], 1)} kg/d castings line '
          f'(AQS-SIZE-FOUNDRY; A-M-286). | {TAG}.', basis_inv)
    _rate(b, 'VAC_TO_INV', float(0),
          f'VAC_IND N+1 pour path (A-M-283): standby-zero on the design day. | {TAG}.', basis_inv)
    _rate(b, 'INV_TO_BREAK', rv(s['sh'] + s['inv']),
          f'Castings in shell to knock-out (A-M-286). | {TAG}.', basis_inv)
    _rate(b, 'BREAK_TO_STOCK', rv(s['inv']),
          f'Investment castings {fmt(s["inv"], 1)} kg/d to stock (A-M-286). | {TAG}.', basis_inv)
    _rate(b, 'IA-SHELL-RECLAIM', rv(s['sh_recl']),
          f'{pct(rat(s["drv"]["foundry_inv_shell_reclaim_frac"]["value"]), 1)} of spent shell reclaimed to the backup '
          f'coats (A-M-286). | {TAG}.', basis_inv)
    _rate(b, 'IA-SHELL-SHOP', rv(s['sh_mu']),
          'The spent-shell balance beyond the reclaim (the 0.5 kg/kg-casting line, AQS-SIZE-FOUNDRY; A-M-286) joins the '
          'shop recovered-silica pool instead of exporting: the shell make-up draws from the pool on IA-SIL-SHOP and the '
          'silicon furnace takes its burden shortfall from the pool on IA-SI-BRIQ, so the export-plus-import pair is '
          f'retired (F-20261110-06). | {TAG}.', basis_inv)
    _rate(b, 'IA-SHELL-EXPORT', float(0),
          'Retired by recovery-first silica (F-20261110-06): the spent shell beyond the reclaim goes to the shop '
          f'recovered-silica pool on IA-SHELL-SHOP ({fmt(s["sh_mu"], 4)} kg/d), which feeds the shell make-up (IA-SIL-SHOP) and '
          'the silicon furnace burden (IA-SI-BRIQ of si_refine.py). Was the spent-shell balance export '
          f'(AQS-SIZE-FOUNDRY registered waste line; A-M-286); GLASS_MILL has no digest capacity (A-M-267). | {TAG}.',
          basis_inv)
    _edge_field(b, 'IA-SHELL-EXPORT', 'composition', {'SiO2': float(1)},
                basis_inv + '; the spent-shell class is silica (the recovery record reads it)')
    # the reactive-Al hydroxide cake leaves the sink-circuit solids loop at the
    # leach (F-20261110-07): both circulating bulk edges give up the same mass
    # from the pre-cake base stamped once in params (the idempotent transfer)
    basis_cake = 'the reactive-Al hydroxide cake transfer out of the sink circuit (F-20261110-07; AQS-PAR-003)'
    cake_mg = _round_half_even(s['al_cake'], 6)
    for sid, tmpl in (('IA-SINK-01',
                       'Sink solids less the {cake} kg/d reactive-Al hydroxide cake drawn to the aluminium '
                       'line on IA-AL-CAKE (recovery-first, F-20261110-07); the sink-circuit bulk edges give up '
                       'the same mass from the pre-cake base {base} kg/d. | X-PAR-02 reconciled (AQS-PAR-003).'),
                      ('IA-WET-FLOAT-01',
                       'Liquor return less the cake mass now drawn at the leach (the IA-SINK-01 twin of the '
                       'same transfer, F-20261110-07), from the pre-cake base {base} kg/d. '
                       '| X-PAR-02 reconciled (AQS-PAR-003).')):
        base = Fraction(Decimal(str(_seed_edge_param(b, sid, 'pre_al_cake_kg_d'))))
        _rate(b, sid, fq(base - Fraction(cake_mg) / 10 ** 6, 6),
              tmpl.format(cake=fmt(s['al_cake'], 4), base=fmt(base, 4)) + f' | {TAG}.', basis_cake)
    _rate(b, 'SHELL_TO_GLASS', float(0),
          'Spent shell reclaims internally (IA-SHELL-RECLAIM) and sends the balance to the shop recovered-silica pool '
          '(IA-SHELL-SHOP): GLASS_DIGEST is fully committed (A-M-267) so the solids line has no digest capacity for it. '
          f'| {TAG}.', basis_inv)
    _rate(b, 'COMB_OFFGAS', float(0),
          'COMB_HEAT is the fuel-fired N+1 alternate (A-M-283): standby-zero; off-gas routes to '
          f'MET_SCRUB only when the alternate is energized. | {TAG}.', basis)
    _rate(b, 'FLUX_TO_IND', rv(s['kroll_flux']),
          f'Salt-flux cover to the melt = the Kroll MgCl2-class drag-out (A-M-284); closes FLUX_PREP on '
          f'IA-KROLL-FLUX. | {TAG}.', basis)
    _rate(b, 'SALT_TO_FLUX', float(0),
          'SALT_FEED stays a stub source: the flux feed is the Kroll drag-out (A-M-284). | {TAG}.', basis)

    # ---- node continuous_kw + SF feeds (A-M-282 Faraday, A-M-286 study) ------
    basis_kw = f'{DOC_F} pot-cell Faraday and bench/line load stamps (A-M-282, A-M-286, A-M-283 N+1 alternates)'
    pe = s['pot_e']
    _kw_dict(b, 'AL_POT', kv(D(str(pe['AL_POT']['kW']))),
             f'{DOC_F} pot cell: Faraday {ffmt(pe["AL_POT"]["I_A"], 0)} A x {ffmt(pe["AL_POT"]["V"], 1)} V at CE '
             f'{ce_str} = {ffmt(pe["AL_POT"]["dc_kW"], 2)} kW DC + bath hold '
             f'{ffmt(pe["AL_POT"]["hold_kW"], 2)} kW (150 mm fibre, study; A-M-282).', basis_kw)
    _kw_dict(b, 'MG_POT', kv(D(str(pe['MG_POT']['kW']))),
             f'{DOC_F} Kroll Mg recycle: {ffmt(pe["MG_POT"]["I_A"], 1)} A x {ffmt(pe["MG_POT"]["V"], 1)} V = '
             f'{ffmt(pe["MG_POT"]["dc_kW"], 3)} kW + hold {ffmt(pe["MG_POT"]["hold_kW"], 2)} kW (A-M-282).', basis_kw)
    _kw_dict(b, 'CA_POT', kv(D(str(pe['CA_POT']['kW']))),
             f'{DOC_F} grease-Ca pot: {ffmt(pe["CA_POT"]["I_A"], 2)} A x {ffmt(pe["CA_POT"]["V"], 1)} V = '
             f'{ffmt(pe["CA_POT"]["dc_kW"], 3)} kW + hold {ffmt(pe["CA_POT"]["hold_kW"], 2)} kW (A-M-282).', basis_kw)
    _kw_dict(b, 'TI_CELL', kv(D(str(pe['TI_CELL']['kW']))),
             f'{DOC_F} Kroll retort + chlorinator hold at 900/800 C under Ar (thermochemical reduction, no electrolysis; '
             f'A-M-284 study hold).', basis_kw)
    _kw_dict(b, 'MO_CELL', kv(D(str(pe['MO_CELL']['kW']))),
             f'{DOC_F} Mo(III) molten-salt cell: {ffmt(pe["MO_CELL"]["I_A"], 2)} A x {ffmt(pe["MO_CELL"]["V"], 1)} V = '
             f'{ffmt(pe["MO_CELL"]["dc_kW"], 3)} kW + hold {ffmt(pe["MO_CELL"]["hold_kW"], 2)} kW (A-M-282).', basis_kw)
    _kw_dict(b, 'CR_CELL', kv(D(str(pe['CR_CELL']['kW']))),
             f'{DOC_F} Cr(III) molten-salt cell: {ffmt(pe["CR_CELL"]["I_A"], 2)} A x {ffmt(pe["CR_CELL"]["V"], 1)} V = '
             f'{ffmt(pe["CR_CELL"]["dc_kW"], 3)} kW + hold {ffmt(pe["CR_CELL"]["hold_kW"], 2)} kW (A-M-282).', basis_kw)
    for u, w, note in (('FLUX_PREP', '0.1', f'{DOC_F} flux bench agitator/mixer at the {fmt(s["kroll_flux"], 3)} kg/d salt duty (study).'),
                       ('WAX_PATTERN', '0.5', f'{DOC_F} pattern injector + wax conditioning pot at {fmt(s["wx"], 1)} kg/d patterns (A-M-286 study).'),
                       ('SHELL_BUILD', '0.3', f'{DOC_F} slurry mixer + stucco rainfall at {fmt(s["sh"], 1)} kg/d shell (A-M-286 study).'),
                       ('SHELL_BURNOUT', '0.25', f'{DOC_F} dewax/firebox at 900 C: shell sensible {fmt(s["sh"], 1)} kg/d offset by the '
                        f'{fmt(s["wx_burn"], 2)} kg/d wax fire credit; 0.25 kW hold class (A-M-286 study).'),
                       ('INV_CAST', '0.15', f'{DOC_F} tilt-pour station at {fmt(s["inv"], 1)} kg/d castings (study).'),
                       ('SHELL_BREAK', '0.4', f'{DOC_F} vibratory knock-out table at {fmt(s["sh"], 1)} kg/d spent shell (study).')):
        _kw_dict(b, u, float(w), note, basis_kw)
    for u, why in (('VAC_CAST', 'N+1 of CAST_LINE/CONT_CAST (vacuum tilt-pour, A-M-283)'),
                   ('RES_HEAT', 'N+1 diverse heat of SHELL_BURNOUT/SINTER (resistance radiant, A-M-283)'),
                   ('SINTER', 'N+1 consolidation of ROLL (press-and-sinter P/M route, A-M-283)'),
                   ('FORGE', 'N+1 former of ROLL (open-die press, A-M-283)'),
                   ('EXTRUDE', 'N+1 former of ROLL (profile press, A-M-283)'),
                   ('DRAW', 'N+1 former of ROLL (wire/rod bench, A-M-283)')):
        _kw_dict(b, u, float(0), f'standby-zero on the design day: {why}; connected rating in params.design.', basis_kw)
    _kw_dict(b, 'COMB_HEAT', float('0.05'),
             'standby-zero on the design day: N+1 fuel-fired heat of IND_MELT (A-M-283); 0.05 kW controls/blower '
             'parasitic, fuel on the C5-C10 class when energized.', basis_kw)
    for u in ('AL_POT', 'MG_POT', 'CA_POT', 'TI_CELL', 'MO_CELL', 'CR_CELL'):
        _kw_rate(b, f'SF-{u}', kv(D(str(pe[u]['kW']))), f'Equals {u} continuous_kw ({DOC_F}).', basis_kw)

    # ---- polymers: the polyolefin line (AQS-DUTY-073, A-M-264) ---------------
    basis_po = f'the polyolefin line ({DOC_P}; A-M-264, A-M-257 by-difference closure, A-M-263 shop-loss class)'
    spf = s['spf']
    _rate(b, 'OIL_TO_OLEFIN', float(0),
          'Fractionator draw 0: the olefin feed draws as naphtha at the cut tank (IA-C5-POLY); the recovered-wax '
          f'path (WAX_TO_OIL) is 0 with the wax loop closing on reclaim (A-M-286). OIL_FRAC closes. | {TAG}.', basis_po)
    _rate(b, 'MEOH_TO_OLEFIN', float(0),
          'Methanol committed to the tank/ship balance (X-PAR-12 TF on S75); the olefin carbon source is the '
          f'on-site C5-C10 naphtha cut (AQS-DES-POLY: carbon source on site). | {TAG}.', basis_po)
    _rate(b, 'OLEFIN_TO_PELLET', rv_c(s['spf']),
          f'Polyolefin resin = naphtha feed {fmt(Fraction(s['spf']) / 10 ** 6, 4)} kg/d (mass-conserving oligomerization, '
          f'AQS-SIZE-OIL-POLY POLY_OLEFIN 150-250 C / 1-5 MPa). | {TAG}.', basis_po)
    _rate(b, 'PELLET_TO_STOCK', rv_c(s['spf']), f'Pellet line passes the resin to stock. | {TAG}.', basis_po)
    _rate(b, 'POLY_TO_MFG', rv_c(s['sP']),
          f'Shop polymer draw by difference on the shop closure (A-M-257 pattern): -r0 {fmt_signed(-(-s["r0"]), 6)} + melt loss '
          f'term f*K/(1-f); molded articles ride BLOW_MOLD (IA-BLOW-OUT 8.407). | {TAG}.', basis_po)
    _rate(b, 'POLY_TO_WET', rv_c(_round_half_even(s['rej'] * Fraction(s['sP']) / 10 ** 6, 6)),
          f'Shop polymer offcut to the wet line, {pct(s["rej"], 0)} of the issue (the S58/S59/S60 10 % shop-loss '
          f'class, AQS-DUTY-010; A-M-263). | {TAG}.', basis_po)
    for sid, why in (('DIGEST_TO_POLY', 'POLY_COND recipe waits on the digester organic assay (AQS-DES-POLY / '
                      'AQS-SIZE-OIL-POLY: no rate treated as design); BLACK_DIGEST closes on IA-BLK-GREY'),):
        _rate(b, sid, float(0), f'{why}. | {TAG}.', basis_po)
    _rate(b, 'IA-C5-POLY', rv_c(s['spf']), f'Polyolefin naphtha feed ({DOC_P}, A-M-264). | {TAG}.', basis_po)
    # value-only update: the note is co-authored downstream (the fab photoresist
    # netting A-M-482 and the balance ess_tf closure both extend it)
    cut1_out = Decimal(str(b.edges['CUT-1-OUT']['rate']['value']))
    seed = dict(b.edges['IA-C5-SHIP']['rate'])
    seed['value'] = rv_c(s['c5'])
    b.set_edge_rate('IA-C5-SHIP', seed, _prov(basis_po + '; the IA-C5-SHIP note is co-authored downstream '
                     '(A-M-482 photoresist netting, ess_tf dock closure) - value-only update'))
    _rate(b, 'IA-METAL-SHIP', rv(s['potm']),
          f'Pot-line metal export {fmt(s["potm"], 4)} kg/d (Al {fmt(s["al"], 1)} + Ti {fmt(s["ti"], 2)} + Mo {fmt(s["mo"], 4)} + Cr '
          f'{fmt(s["cr"], 2)}): the stock loop is the only net inlet, so the loop passes it to the METAL_STORE dispatch '
          f'(A-M-270 buffer) and the dock exports it (D-DOCK outlet; A-M-285). | {TAG}.', basis)
    _rate(b, 'DOCK_EXPORT_TBD', float(0),
          'Goods balance (A-M-265 rev, restated A-M-460): the accounting placeholder stays 0.0 - the real surplus exports '
          f'ride their own dock edges: foundry pot metal IA-METAL-SHIP {fmt(s["potm"], 4)} kg/d + pot chlorine '
          f'IA-CA-CL2-SHIP {fmt(s["ca_cl2"] - s["si_cl2"], 3)} kg/d net of the silicon-loop make-up (A-M-285; the AL_POT chlorine '
          'closes on the cake chlorination, X-QA-19, A-M-495) and the shop finished-goods surplus '
          'IA-GOODS-SHIP on top of the shipped products (O2, MeOH, oil cuts). THIS IS THE PLANT SURPLUS STATEMENT: the plant '
          'is a net exporter of metal, chlorine and finished goods through the dock (Q-038 rebasis 2026-11-04: the wear-goods '
          'plug pair IA-MFG-OUT/IA-WEAR is retired; wear rides the A-M-429 roster line).'
          f' | {TAG}.', basis)

    # ---- the crew textile line (A-M-429, A-M-502) -----------------------------
    basis_tx = f'the crew textile line (A-M-429; the phosphate-FR finish X-QA-11, A-M-502)'
    if 'POLY_FIBER' in b.nodes:
        _rate(b, 'STOCK_TO_FIBER', rv(s['pp_in']),
              f'PP feed at the {pct(rat(s["drv"]["POLYMERS.textile.spin_yield"]["value"]), 0)} spin yield (A-M-429). | {TAG}.',
              basis_tx)
        if s['fr_live']:
            _rate(b, 'IA-FR-P', rv_c(s['fr_p']),
                  f'H3PO4 + 2 NH3 -> (NH4)2HPO4 on the finish pick-up {fmt(Fraction(s["fr_pickup"]) / 10 ** 6, 4)} kg/d at 2 % of fibre '
                  f'(A-M-225 basis; A-M-502): {fmt(Fraction(s["fr_p"]) / 10 ** 6, 6)} kg/d acid, on site (X-QA-11). | {TAG}.', basis_tx)
            _rate(b, 'IA-FR-NH3', rv_c(s['fr_nh3']),
                  f'the neutralizer half of the (NH4)2HPO4 finish, {fmt(Fraction(s["fr_nh3"]) / 10 ** 6, 6)} kg/d '
                  f'(A-M-502; the ammonia line re-solves on IA-NH3-SRC in balance.physics). | {TAG}.', basis_tx)
        _rate(b, 'FIBER_SCRAP', rv_c(s['scrap']),
              f'spin waste, PP leach-inert (the POLY_TO_WET class). | {TAG}.', basis_tx)
        _rate(b, 'FLEECE_TO_MFG', rv_c(s['textile']),
              f'fleece incl. FR: cutting/sewing/knitting into the crew textile issue (A-M-429). | {TAG}.', basis_tx)
        _rate(b, 'TEXTILE_HAB', rv_c(s['textile']),
              f'the worn goods return on IA-WEAR (A-M-429). | {TAG}.', basis_tx)
        if s['fr_p'] > 0:
            base = Fraction(Decimal(str(_seed_edge_param(b, 'S34B', 'pre_fr_kg_d'))))
            _rate(b, 'S34B', fq(base - Fraction(s['fr_p']) / 10 ** 6, 6),
                  f'{TAG}: the WS_PHOS H3PO4 product splits to the bench {fmt(base, 4)} less the '
                  f'FR finish draw {fmt(Fraction(s["fr_p"]) / 10 ** 6, 6)} kg/d on IA-FR-P (X-QA-11, A-M-502).', basis_tx)
    _rate(b, 'FR_FINISH', float(0),
          'Retired by the on-site phosphate-FR finish (X-QA-11, A-M-502): the '
          '(NH4)2HPO4 compound forms in-bath on IA-FR-P (fab H3PO4) and IA-FR-NH3 '
          '(ammonia line) where the spin line runs; where a locale eliminates the line '
          'the demand retires with it. Was the D-DOCK reagent import (A-M-225).', basis_tx)

    # ---- recovery-first records (flow_graph/param/recovery.py tables) --------
    basis_rec = 'the recovery-first records of this family\'s ore and recovered streams (A-M-499, F-20261110-06/-07, A-M-284)'
    _set(b, 'SHELL_BUILD', 'params.recovery', [_si_record(b, s)], basis_rec)
    _set(b, 'TI_CELL', 'params.recovery', [_ore_record(b, 'IA-TIO2-MU', 'TI_CELL', 'Ti', 'TiO2')], basis_rec)
    _set(b, 'MO_CELL', 'params.recovery', [_ore_record(b, 'IA-MOO3-MU', 'MO_CELL', 'Mo', 'MoO3')], basis_rec)
    _set(b, 'CR_CELL', 'params.recovery', [_ore_record(b, 'IA-CR2O3-MU', 'CR_CELL', 'Cr', 'Cr2O3')], basis_rec)
    _set(b, 'HOPPER', 'params.recovery', [_fe_record(b, s)], basis_rec)

    _stamp_sizing(b, s)
    return s


def _si_record(b, s):
    """The SHELL_BUILD silica record (F-20261110-06): the v1 float book over
    the quantised rates and the AW table (see module docstring)."""
    v = lambda sid: _flo(b.edges[sid]['rate']['value'] or 0)
    si = _aw_frac('SiO2', 'Si')
    need = (v('IA-SHELL-RECLAIM') + _flo(fq(s['sh_mu'], 6))) * si
    rec = (v('IA-SHELL-RECLAIM') + v('IA-SIL-SHOP')) * si
    return {'element': 'Si', 'use': 'investment shell silica', 'need_kg_d': need,
            'recovered_kg_d': rec, 'recovered_from': ['IA-SHELL-RECLAIM', 'IA-SIL-SHOP'],
            'ore_streams': [], 'unrecovered': [],
            'note': ('recovery-first silica (F-20261110-06): the reclaimed backup-coat shell plus the shop recovered-silica '
                     'pool (the S08 crib silicate of A-M-490 and the spent-shell surplus on IA-SHELL-SHOP) cover the whole '
                     'shell make-up; the dock import IA-SILICA-MU and the spent-shell export IA-SHELL-EXPORT are both retired')}


def _ore_record(b, sid, uid, el, formula):
    """The dock-concentrate records (A-M-284): the v1 float book."""
    return {'element': el, 'use': f'{uid} metal', 'need_kg_d': _flo(b.edges[sid]['rate']['value'] or 0) * _aw_frac(formula, el),
            'recovered_kg_d': _flo('0'), 'recovered_from': [], 'ore_streams': [sid], 'unrecovered': [],
            'note': ('the dock concentrate is the only source at this scope (D-DOCK feedstock ruling, A-M-284); the '
                     'float-sink dense grit is the first source as far as its assay supports it (assay task '
                     'AQS-ASSAY-TI-MO), and this record re-opens on that route when the assay lands')}


def _fe_record(b, s):
    """The HOPPER raw-feed record (A-M-499): the v1 float book over the
    quantised seed rates and the feed assay driver."""
    d = s['drv']
    fe = _flo(d['feed_fe_assay_frac']['value'])
    v = lambda sid: _flo(b.edges[sid]['rate']['value'] or 0)
    receipts = sum(v(k) for k in ('IA-WEAR', 'S61', 'FRASS', 'IA-LEACH-HOP') if k in b.edges)
    fe_ins = [e['stream_id'] for e in b.data['edges'] if e['presence'] == 'present'
              and e['to_unit_id'] in ('LEACH_CSTR_1', 'NORTH_DOCK', 'ATMOS')
              and 'Fe' in (e.get('composition') or {}) and float(e['rate']['value'] or 0) > 0]
    return {'element': 'Fe', 'use': 'design feed metal (scrap yard)',
            'need_kg_d': v('IA-FEED-01') * fe, 'recovered_kg_d': receipts * fe,
            'recovered_from': ['IA-WEAR', 'S61', 'FRASS', 'IA-LEACH-HOP'] + sorted(set(fe_ins) | {'IA-BRINE-ML'}),
            'ore_streams': ['IA-FEED-MU'], 'unrecovered': [],
            'note': ('the characterized-lot make-up is the raw feed class (AQS-ASSAY-001 section 7, A-M-499): the loop '
                     'receipts return their metal to the scrap yard and the listed leach-loop liquor inflows recirculate '
                     'the dissolved feed metals - the EW cascade plates them at recovery 1.0 (A-M-460); they are loop '
                     'returns the recovery runs on, not terminal losses')}


def _stamp_sizing(b, s):
    """The params.sizing / params.design / params.envelope books (X-MFG-30
    CadQuery pattern; A-M-199 envelopes): stamp() and cad() of the reference
    writer. The pot-cell design blocks are leaf-stamped so the pot_cells
    family's bath_top_mm field stays passthrough. Downstream-owned blocks
    (the fluoro_train F-block units and POLY_STOCK sizing) are not stamped."""
    drv = s['drv']
    hd = rat(drv['atm_HD']['value'])
    pe = s['pot_e']
    eng = fq                                          # exact value at dp

    def st(uid, fields, basis, ref=None):
        _set(b, uid, 'params.sizing', dict(status='study', **fields), basis, ref)

    def cad(uid, design, size_mm, style, state, why, leaf_design=False):
        basis = f'X-MFG-30 CAD stamp ({DOC_F}/{DOC_P}): {why}'
        if leaf_design:
            for k in design:
                _set(b, uid, 'params.design.' + k, design[k], basis)
        else:
            _set(b, uid, 'params.design', dict(design), basis)
        _set(b, uid, 'params.envelope', dict(size_mm=size_mm, style=style, state=state, basis=why), basis)
        if ('node', uid, 'params.sizing') in b.computed:   # fluoro_train re-owns POLY_STOCK sizing
            b.computed[('node', uid, 'params.sizing')][0]['size_mm'] = size_mm

    def dh(kg, rho, tau=Fraction(1)):
        return _d_hold(kg, rho, tau, hd)

    def f3(v):
        return _flo(v)                                # a v1 driver/book float, verbatim

    def hd_mul(xd):
        return qi(D(xd) * D(hd.numerator) / D(hd.denominator))

    CELL_ENV_BASIS = ('cell-class study minimum; live on the pot feeds - the dock oxide concentrates and the recovered '
                      'brine (A-M-284, A-M-496); bath 0.5 d hold at 1800 kg/m3, electrodes and busbar from the Faraday '
                      'current (A-M-282)')

    # melt/forming/store train
    charge = s['charge']
    dc_ind = _round10(dh(charge, 7000))
    st('IND_MELT', {
        'source': DOC_F, 'charge_kg_d': eng(Fraction(s['sS']) / 10 ** 6 + s['potm'] + s['kroll_flux'], 4),
        'stock_out_kg_d': f3(drv['foundry_stock_demand_kg_d']['value']),
        'slag_kg_d': eng(Fraction(s['sslag']) / 10 ** 6, 4), 'crucible_kg': f3(drv['melt_charge_kg']['value']),
        'heats_d': s['heats'], 'melt_kWh_d': eng(s['e_melt'], 3),
        'avg_kW': eng(s['e_melt'] / 24, 4), 'peak_kW': float(s['kw_peak']), 'connected_kW': float(25),
        'kWh_per_kg': {c: eng(s['q'][c], 4) for c in ('Cu', 'Fe', 'Zn', 'Al', 'Ti')},
        'basis': 'scrap remelt + pot metal; class energies (cp_s dT + L + cp_l superheat)/eta per A-M-177 method, '
                 'CRC_CU/CRC_FE/CRC_ZN/CRC_AL/CRC_TI (reactive/addition class bounding at Ti)'},
        'the melt-shop ledger and class energies (A-M-177, A-M-261 rev)')
    cad('IND_MELT',
        dict(service='Cu/Fe/Zn/Al scrap + pot-metal remelt; medium-frequency coreless induction, tilt pour',
             crucible_kg=f3(drv['melt_charge_kg']['value']), crucible_D_mm=float(dc_ind),
             crucible_H_mm=hd_mul(dc_ind), heats_d=s['heats'], connected_kW=float(25),
             peak_kW=float(s['kw_peak']), melt_kWh_d=eng(s['e_melt'], 3),
             lining='ceramic-fibre hot face 150 mm + 4 mm CS casing (study)'),
        _ebox((1000, 1000, 1500), float(dc_ind), hd), 'box_furnace', 'live',
        'A-M-199 melt class: crucible melt_charge_kg at 7000 kg/m3, H/D atm_HD, +300/+500 allowances; box furnace at '
        'the connected load')
    st('CAST_LINE', {'source': DOC_F, 'pour_kg_d': f3('3.0'), 'products': 'Cu ingot/billet, permanent mold',
                     'scrap_return_kg_d': float(0)},
       'the Cu cast line (A-M-261 rev)')
    cad('CAST_LINE', dict(machine='permanent-mould cast line', pour_kg_d=f3('3.0'), moulds=2, table_L_mm=700),
        _ebox((1500, 800, 1500), float(dh(Fraction(3), 7000, Fraction(1, 24))), hd), 'line_machine', 'live',
        'A-M-199 forming class; 1 h hold-up of the Cu pour is below the class minimum')
    cont4 = eng(s['cont'], 4)
    st('CONT_CAST', {'source': DOC_F, 'feed_kg_d': cont4, 'billet_kg_d': float(10),
                     'ingot_kg_d': eng(s['cont_stock'], 4),
                     'mold': 'water-cooled copper, horizontal (AQS-SIZE-FOUNDRY)',
                     'basis': 'pot metal + Zn + stainless base to the ingot line; Fe 10 rolled'},
       'the semi-continuous caster (A-M-261 rev, A-M-285)')
    cad('CONT_CAST', dict(machine='two-strand horizontal semi-continuous caster', feed_kg_d=cont4,
                          billet_kg_d=s['fe_f'], ingot_kg_d=eng(s['cont_stock'], 4), strands=2,
                          mould='water-cooled copper (AQS-SIZE-FOUNDRY)'),
        _ebox((1500, 800, 1500), float(dh(s['cont'], 7000, Fraction(1, 24))), hd), 'line_machine', 'live',
        'A-M-199 forming class; hold-up of the cont feed is below the class minimum')
    st('ROLL', {'source': DOC_F, 'rolled_kg_d': eng(s['mix']['Cu'] + 10, 4), 'kWh_d': eng(s['e_roll'], 4),
                'basis': '0.032 kWh/kg cold-rolling class (A-M-177 DIETER1988); hot rolling cheaper'},
       'the rolling bench (A-M-177)')
    cad('ROLL', dict(machine='two-high bench rolling mill', rolled_kg_d=eng(s['mix']['Cu'] + 10, 4),
                     rolls_D_mm=300, roll_L_mm=640, kWh_d=eng(s['e_roll'], 4)),
        _ebox((1500, 800, 1500), float(dh(s['mix']['Cu'] + 10, 7000, Fraction(1, 24))), hd), 'line_machine', 'live',
        'A-M-199 forming class; hold-up of the 13 kg/d charge is below the class minimum')
    st('STOCK_OUT', {'source': DOC_F, 'stock_out_kg_d': eng(s['stock_in'], 4),
                     'draws': dict(MFG=f3(drv['foundry_stock_demand_kg_d']['value']), FAB=float(0),
                                   WIRE_DRAW=float(0)),
                     'export_kg_d': eng(s['potm'], 4)},
       'the stock ledger (A-M-261 rev, A-M-285 export)')
    cad('STOCK_OUT', dict(rack='three-tier bar/plate/ingot staging rack',
                          issue_kg_d=f3(drv['foundry_stock_demand_kg_d']['value']),
                          export_kg_d=eng(s['potm'], 4), hold_d=f3('1.0')),
        _ebox((1200, 800, 1500), float(dh(s['stock_in'], 2000)), hd), 'store_rack', 'live',
        '1 d shop issue K at the 2000 kg/m3 staged-metal density (AQS-DUTY-064 METAL_STORE row; A-M-261 loop)')

    # pot cells: per-unit sizing books, design leaf-stamped (bath_top_mm is
    # the pot_cells family's field)
    st('AL_POT', {'source': DOC_F, 'al_kg_d': s['al_f'], 'line_kg_d': f3(drv['foundry_al_line_kg_d']['value']),
                  'export_kg_d': eng(s['al'] - s['al_i'], 4), 'alcl3_kg_d': eng(s['alcl3'], 4),
                  'alcl3_recovered_kg_d': eng(s['alcl3_rec'], 4), 'alcl3_makeup_kg_d': eng(s['alcl3_mu'], 4),
                  'al_cake_kg_d': eng(s['al_cake'], 4), 'cl2_kg_d': eng(s['al_cl2'], 4),
                  'cl2_chlorination_kg_d': eng(s['al_chlor_cl2'], 4), 'char_kg_d': eng(s['char_al'], 4),
                  'chemistry': '2 AlCl3 -> 2 Al + 3 Cl2 electrolysis at 700 C NaCl-KCl-AlCl3 bath; cake calcination + '
                  'Al2O3 + 3 C + 3 Cl2 -> 2 AlCl3 + 3 CO chlorination of the recovered hydroxide (GREENWOOD stoichiometry)',
                  'I_A': pe['AL_POT']['I_A'], 'V': pe['AL_POT']['V'], 'dc_kW': pe['AL_POT']['dc_kW'],
                  'hold_kW': pe['AL_POT']['hold_kW'], 'kW': pe['AL_POT']['kW'],
                  'basis': 'recovery-sized aluminium (X-QA-19 owner ruling, A-M-495): the line is sized to the recoverable '
                  'aluminium - the leach reactive-Al hydroxide cake is calcined and carbochlorinated on site with the cell '
                  'chlorine, making the whole AlCl3 feed; the anhydrous AlCl3 dock import is retired; Faraday at CE '
                  '0.85 (A-M-282)'},
       'the recovery-sized aluminium pot (X-QA-19, A-M-495; A-M-282 Faraday)')
    st('MG_POT', {'source': DOC_F, 'mg_kg_d': eng(s['mg_ti'], 4), 'mgcl2_return_kg_d': eng(s['mgcl2_ret'], 4),
                  'mgcl2_makeup_kg_d': eng(s['mgcl2_mu'], 4), 'cl2_kg_d': eng(s['cl2_ti'], 4),
                  'chemistry': 'MgCl2 -> Mg + Cl2, 700 C (AQS-BAL-KROLL closure)',
                  'I_A': pe['MG_POT']['I_A'], 'V': pe['MG_POT']['V'], 'dc_kW': pe['MG_POT']['dc_kW'],
                  'hold_kW': pe['MG_POT']['hold_kW'], 'kW': pe['MG_POT']['kW'],
                  'basis': 'Kroll Mg recycle at the 0.50 kg/d Ti line; the brine-recovery crystallizer BRINE_CRYS covers '
                  'the drag-out (X-QA-11, A-M-496)'},
       'the Kroll Mg recycle pot (AQS-BAL-KROLL; A-M-496)')
    st('CA_POT', {'source': DOC_F, 'ca_kg_d': eng(s['ca'], 6), 'cacl2_kg_d': eng(s['cacl2'], 6),
                  'cl2_kg_d': eng(s['ca_cl2'], 6), 'chemistry': 'CaCl2 -> Ca + Cl2, 700 C',
                  'I_A': pe['CA_POT']['I_A'], 'V': pe['CA_POT']['V'], 'dc_kW': pe['CA_POT']['dc_kW'],
                  'hold_kW': pe['CA_POT']['hold_kW'], 'kW': pe['CA_POT']['kW'],
                  'basis': 'grease-thickener Ca line (AQS-DUTY-GREASE 0.1 kg/d Ca(OH)2); brine recovered on site by '
                  'BRINE_CRYS (X-QA-11, A-M-496)'},
       'the grease-Ca pot (AQS-DUTY-GREASE; A-M-496)')
    st('TI_CELL', {'source': DOC_F, 'ti_kg_d': s['ti_f'], 'tio2_kg_d': eng(s['tio2'], 4),
                   'c_kg_d': eng(s['c_ti'], 4), 'cl2_kg_d': eng(s['cl2_ti'], 4), 'mg_kg_d': eng(s['mg_ti'], 4),
                   'mgcl2_gross_kg_d': eng(s['mgcl2_g'], 4), 'co_kg_d': eng(s['co_ti'], 4),
                   'chemistry': 'TiO2 + 2C + 2Cl2 -> TiCl4 + 2CO; TiCl4 + 2Mg -> Ti + 2MgCl2 (AQS-BAL-KROLL)',
                   'I_A': pe['TI_CELL']['I_A'], 'V': pe['TI_CELL']['V'], 'dc_kW': pe['TI_CELL']['dc_kW'],
                   'hold_kW': pe['TI_CELL']['hold_kW'], 'kW': pe['TI_CELL']['kW'],
                   'basis': 'dock rutile-equivalent + carbon + Mg-pot loop; A-M-284 (assay envelope on the concentrate)'},
       'the Kroll retort train (AQS-BAL-KROLL; A-M-284)')
    st('MO_CELL', {'source': DOC_F, 'mo_kg_d': s['mo_f'], 'moo3_kg_d': eng(s['moo3'], 4),
                   'c_kg_d': eng(s['c_mo'], 4), 'co2_kg_d': eng(s['co2_mo'], 4),
                   'chemistry': 'MoO3 + 1.5C + 1.5Cl2 -> MoCl3 + 1.5CO2; MoCl3 -> Mo + 1.5Cl2 (anode gas recycled)',
                   'I_A': pe['MO_CELL']['I_A'], 'V': pe['MO_CELL']['V'], 'dc_kW': pe['MO_CELL']['dc_kW'],
                   'hold_kW': pe['MO_CELL']['hold_kW'], 'kW': pe['MO_CELL']['kW'],
                   'basis': 'dock tech-oxide import; internal chlorine loop; A-M-290 (grade envelope 95-99 % MoO3)'},
       'the Mo(III) cell (A-M-290, A-M-284)')
    st('CR_CELL', {'source': DOC_F, 'cr_kg_d': s['cr_f'], 'cr2o3_kg_d': eng(s['cr2o3'], 4),
                   'c_kg_d': eng(s['c_cr'], 4), 'co_kg_d': eng(s['co_cr'], 4),
                   'chemistry': 'Cr2O3 + 3C + 3Cl2 -> 2CrCl3 + 3CO; 2CrCl3 -> 2Cr + 3Cl2 (anode gas recycled)',
                   'I_A': pe['CR_CELL']['I_A'], 'V': pe['CR_CELL']['V'], 'dc_kW': pe['CR_CELL']['dc_kW'],
                   'hold_kW': pe['CR_CELL']['hold_kW'], 'kW': pe['CR_CELL']['kW'],
                   'basis': 'dock chromite-equivalent import; internal chlorine loop; A-M-290 (grade envelope 40-52 % Cr2O3)'},
       'the Cr(III) cell (A-M-290, A-M-284)')
    for uid, feed in (('AL_POT', eng(s['alcl3'], 4)), ('MG_POT', eng(s['mgcl2_ret'] + s['mgcl2_mu'], 4)),
                      ('CA_POT', eng(s['cacl2'], 4)), ('MO_CELL', eng(s['moo3'] + s['c_mo'], 4)),
                      ('CR_CELL', eng(s['cr2o3'] + s['c_cr'], 4))):
        d_cell = dh(Fraction(Decimal(str(feed))), 1800, Fraction(1, 2))
        i_a = pe[uid]['I_A']
        bus = ceil_f(Fraction(Decimal(str(i_a))) / Fraction(3, 2) / 25) * 25   # 1.5 A/mm2 class, 25 mm2 grid
        conn = ceil_f(Fraction(Decimal(str(pe[uid]['kW']))) + Fraction(1, 2))
        design = dict(feed_kg_d=feed, metal_kg_d={'AL_POT': s['al_f'], 'MG_POT': eng(s['mg_ti'], 4),
                                                  'CA_POT': eng(s['ca'], 4), 'MO_CELL': s['mo_f'],
                                                  'CR_CELL': s['cr_f']}[uid],
                      I_A=i_a, cell_V=pe[uid]['V'], dc_kW=pe[uid]['dc_kW'], hold_kW=pe[uid]['hold_kW'],
                      connected_kW=conn, busbar_mm2=bus)
        if uid == 'AL_POT':
            design.update(service='molten AlCl3-(NaCl-KCl) electrolysis cell, 700 C',
                          chemistry='2 AlCl3 -> 2 Al + 3 Cl2', cl2_kg_d=eng(s['al_cl2'], 4),
                          bath_T_C=float(700), anode_D_mm=75, anode_imm_mm=400, cathodes=5)
        elif uid == 'MG_POT':
            design.update(service='molten MgCl2 electrolysis cell (Kroll Mg recycle), 700 C',
                          chemistry='MgCl2 -> Mg + Cl2', cl2_kg_d=eng(s['cl2_ti'], 4),
                          bath_T_C=float(700), anode_D_mm=50, anode_imm_mm=300, cathodes=4)
        elif uid == 'CA_POT':
            design.update(service='molten CaCl2 electrolysis cell, 700 C', chemistry='CaCl2 -> Ca + Cl2',
                          cl2_kg_d=eng(s['ca_cl2'], 4), bath_T_C=float(700), anode_D_mm=50,
                          anode_imm_mm=250, cathodes=3)
        elif uid == 'MO_CELL':
            design.update(service='Mo(III) molten-salt electrolysis cell with carbochlorination loop, 650 C',
                          chemistry='MoO3 + 1.5C + 1.5Cl2 -> MoCl3 + 1.5CO2; MoCl3 -> Mo + 1.5Cl2',
                          co2_kg_d=eng(s['co2_mo'], 4), bath_T_C=float(650), anode_D_mm=50,
                          anode_imm_mm=250, cathodes=3)
        else:
            design.update(service='Cr(III) molten-salt electrolysis cell with carbochlorination loop, 700 C',
                          chemistry='Cr2O3 + 3C + 3Cl2 -> 2CrCl3 + 3CO; 2CrCl3 -> 2Cr + 3Cl2',
                          co_kg_d=eng(s['co_cr'], 4), bath_T_C=float(700), anode_D_mm=50,
                          anode_imm_mm=250, cathodes=3)
        cad(uid, design, _ebox((800, 800, 1600), float(d_cell), hd), 'pot_cell', 'live',
            CELL_ENV_BASIS, leaf_design=True)
    # Kroll train
    d_ti = dh(s['tio2'] + s['c_ti'], 1800)
    cad('TI_CELL',
        dict(service='Kroll chlorinator + Mg-reduction retort train',
             chemistry='TiO2 + 2C + 2Cl2 -> TiCl4 + 2CO; TiCl4 + 2Mg -> Ti + 2MgCl2 (AQS-BAL-KROLL)',
             tio2_kg_d=eng(s['tio2'], 4), c_kg_d=eng(s['c_ti'], 4), ti_kg_d=s['ti_f'],
             mg_kg_d=eng(s['mg_ti'], 4), cl2_kg_d=eng(s['cl2_ti'], 4),
             mgcl2_gross_kg_d=eng(s['mgcl2_g'], 4), co_kg_d=eng(s['co_ti'], 4), retort_T_C=float(900),
             chlorinator_T_C=float(800), hold_kW=pe['TI_CELL']['hold_kW'], batch_kg=f3('1.0'),
             basis='batch retort campaigns at the 0.5 kg/d Ti scale'),
        _ebox((800, 800, 1600), float(d_ti), hd), 'kroll_train', 'live',
        'cell-class study minimum; live on the D-DOCK rutile + carbon imports with the Mg-pot loop (A-M-284)')
    st('FLUX_PREP', {'source': DOC_F, 'salt_kg_d': eng(s['kroll_flux'], 4),
                     'basis': 'Kroll MgCl2-class drag-out (A-M-284); salt-flux cover for the Al-charged melt'},
       'the salt-flux bench (A-M-284)')
    cad('FLUX_PREP', dict(bench='salt flux cover preparation bench', salt_kg_d=eng(s['kroll_flux'], 4),
                          hopper_L=20, mixer_kW=f3('0.1')),
        _ebox((800, 600, 1200), float(dh(s['kroll_flux'], 1800, Fraction(2))), hd), 'bench_prep', 'live',
        'prep-class study minimum; live on the Kroll drag-out (A-M-284)')
    # investment train
    st('WAX_PATTERN', {'source': DOC_F, 'wax_kg_d': eng(s['wx'], 4), 'makeup_kg_d': eng(s['wx_mu'], 4),
                       'reclaim_kg_d': eng(s['wx_recl'], 4),
                       'basis': '1 kg wax per kg castings, 90 % reclaim; make-up is the C19-C28 cut blend '
                       '(A-M-286, A-M-498)'},
       'the pattern wax book (A-M-286, A-M-498)')
    cad('WAX_PATTERN', dict(bench='wax pattern injection bench', wax_kg_d=eng(s['wx'], 4),
                            makeup_kg_d=eng(s['wx_mu'], 4), reclaim_kg_d=eng(s['wx_recl'], 4),
                            injector_kW=f3('0.5'), pot_L=10),
        _ebox((800, 600, 1200), float(dh(s['wx'], 1000)), hd), 'bench_prep', 'live',
        'prep-class study minimum; live on the C19-C28 cut blend make-up + 90 % reclaim (A-M-286, A-M-498)')
    st('SHELL_BUILD', {'source': DOC_F, 'shell_kg_d': eng(s['sh'], 4), 'silica_makeup_kg_d': eng(s['sh_mu'], 4),
                       'reclaim_kg_d': eng(s['sh_recl'], 4),
                       'basis': '6-dip shell 4 kg/kg castings, 87.5 % reclaim (A-M-286)'},
       'the shell-building booth (A-M-286)')
    cad('SHELL_BUILD', dict(machine='dip-coat + stucco rainfall shell-building booth', shell_kg_d=eng(s['sh'], 4),
                            silica_makeup_kg_d=eng(s['sh_mu'], 4), reclaim_kg_d=eng(s['sh_recl'], 4), dips=6,
                            slurry_L=40),
        _ebox((1500, 800, 1500), float(dh(s['sh'], 1600)), hd), 'line_machine', 'live',
        'A-M-199 forming class at the 4 kg/kg shell duty (A-M-286); 1 d slurry/flour staging at 1600 kg/m3')
    st('SHELL_BURNOUT', {'source': DOC_F, 'shell_kg_d': eng(s['sh'], 4), 'wax_reclaim_kg_d': eng(s['wx_recl'], 4),
                         'burned_wax_kg_d': eng(s['wx_burn'], 4), 'T_C': float(900),
                         'basis': 'flash dewax + fire at 900 C (A-M-286)'},
       'the dewax/firebox (A-M-286)')
    cad('SHELL_BURNOUT', dict(service='flash-dewax + shell fire furnace, 900 C', shell_kg_d=eng(s['sh'], 4),
                              wax_reclaim_kg_d=eng(s['wx_recl'], 4), burned_wax_kg_d=eng(s['wx_burn'], 4),
                              T_C=float(900), kW=f3('0.25'), condenser='wax condensate to WAX_PATTERN'),
        _ebox((1000, 1000, 1500), float(dh(s['sh'], 2500)), hd), 'box_furnace', 'live',
        'A-M-199 melt class at the fired-shell duty (A-M-286)')
    st('INV_CAST', {'source': DOC_F, 'pour_kg_d': f3(drv['foundry_inv_line_kg_d']['value']),
                    'shell_kg_d': eng(s['sh'], 4),
                    'basis': 'live melt output 2 kg/d through the fired shell (A-M-286)'},
       'the investment pour station (A-M-286)')
    cad('INV_CAST', dict(machine='investment casting tilt-pour station',
                         pour_kg_d=f3(drv['foundry_inv_line_kg_d']['value']), shell_kg_d=eng(s['sh'], 4),
                         molds_per_campaign=8),
        _ebox((1500, 800, 1500), float(dh(s['inv'], 7000, Fraction(1, 24))), hd), 'line_machine', 'live',
        'A-M-199 forming class; live on IND_TO_INV (A-M-286)')
    st('SHELL_BREAK', {'source': DOC_F, 'castings_kg_d': f3(drv['foundry_inv_line_kg_d']['value']),
                       'spent_shell_kg_d': eng(s['sh'], 4), 'reclaim_kg_d': eng(s['sh_recl'], 4),
                       'export_kg_d': eng(s['sh_mu'], 4), 'basis': 'A-M-286 knock-out split'},
       'the knock-out station (A-M-286)')
    cad('SHELL_BREAK', dict(machine='vibratory shell knock-out station with reclaim sieve',
                            spent_shell_kg_d=eng(s['sh'], 4), reclaim_kg_d=eng(s['sh_recl'], 4),
                            export_kg_d=eng(s['sh_mu'], 4), table_kW=f3('0.4')),
        _ebox((1500, 800, 1500), float(dh(s['sh'], 1600)), hd), 'line_machine', 'live',
        'A-M-199 forming class at the spent-shell duty (A-M-286)')
    # N+1 alternates: real equipment, standby-zero design-day rate (A-M-283)
    st('VAC_IND', {'source': DOC_F, 'rate_kg_d': float(0), 'connected_kW': float(15),
                   'backup_of': 'IND_MELT (diverse: vacuum induction skull melt)',
                   'outage_basis': 'IND_MELT relining/repair outage 2 d (crucible life 20-50 heats, AQS-SIZE-FOUNDRY '
                   'sec. Crucibles; AGENTS.md redundancy rule)',
                   'design_case': '2 kg ISM skull melt (AQS-SIZE-FOUNDRY)'},
       'the N+1 alternates, rated standby (A-M-283)')
    cad('VAC_IND', dict(service='vacuum induction skull melt (ISM), N+1 diverse of IND_MELT', design_case_kg=f3('2.0'),
                        connected_kW=float(15), backup_of='IND_MELT', outage_d=f3('2.0'),
                        duty_note='equal-duty backup of the 25 kW melt at the 2 kg ISM batch class (A-M-283)'),
        _ebox((1000, 1000, 1500), float(_round10(dh(Fraction(2), 7000))), hd), 'box_furnace', 'standby_rated',
        'A-M-199 melt class; N+1 rated envelope (A-M-283): real machine, standby-zero design-day rate')
    st('VAC_CAST', {'source': DOC_F, 'rate_kg_d': float(0), 'connected_kW': float('7.5'),
                    'backup_of': 'CAST_LINE / CONT_CAST (vacuum tilt-pour)',
                    'outage_basis': 'cast-line stoppage during the VAC_IND outage window (A-M-282)'},
       'the N+1 alternates, rated standby (A-M-283)')
    cad('VAC_CAST', dict(machine='vacuum tilt-pour casting station, N+1 of CAST_LINE', connected_kW=float('7.5'),
                         backup_of='CAST_LINE', outage_d=f3('2.0'), design_case_kg_d=f3('3.0')),
        _ebox((1500, 800, 1500), float(dh(Fraction(3), 7000, Fraction(1, 24))), hd), 'line_machine', 'standby_rated',
        'A-M-199 forming class; N+1 rated envelope (A-M-283)')
    st('RF_HEAT', {'source': DOC_F, 'duty_kg_d': float(0), 'connected_kW': float(5),
                   'backup_of': 'IND_MELT (N+1 at equal melt duty)',
                   'outage_basis': 'IND_MELT coil/PSU outage; 100-400 kHz through-coil at the 10 kg crucible class '
                   '(A-M-232 rating held; A-M-283 N+1 envelope)'},
       'the N+1 alternates, rated standby (A-M-283)')
    cad('RF_HEAT', dict(service='RF preheat/hold unit, N+1 at equal melt duty of IND_MELT', connected_kW=float(5),
                        backup_of='IND_MELT', outage_d=f3('2.0'),
                        crucible_kg=f3(drv['melt_charge_kg']['value']), freq_kHz='100-400',
                        duty_note='equal-duty backup of the 10 kg crucible class (A-M-283; A-M-232 rating held)'),
        _ebox((1000, 1000, 1500), float(_round10(dh(charge, 7000))), hd), 'box_furnace', 'standby_rated',
        'A-M-199 melt class; N+1 rated envelope (A-M-283)')
    st('RES_HEAT', {'source': DOC_F, 'rate_kg_d': float(0), 'connected_kW': float(12),
                    'backup_of': 'SHELL_BURNOUT / SINTER heating duty (resistance radiant)',
                    'outage_basis': 'burnout-element outage during a shell campaign (A-M-282)'},
       'the N+1 alternates, rated standby (A-M-283)')
    cad('RES_HEAT', dict(service='resistance radiant reheating furnace, N+1 of SHELL_BURNOUT/SINTER heating',
                         connected_kW=float(12), backup_of='SHELL_BURNOUT/SINTER', outage_d=f3('2.0'), T_C=float(900)),
        _ebox((1000, 1000, 1500), float(dh(s['sh'] + 1, 2500)), hd), 'box_furnace', 'standby_rated',
        'A-M-199 melt class; N+1 rated envelope (A-M-283)')
    st('COMB_HEAT', {'source': DOC_F, 'rate_kg_d': float(0), 'connected_kW': float(30),
                     'backup_of': 'IND_MELT (tertiary, fuel-fired C5-C10 class)',
                     'outage_basis': 'long IND_MELT outage with both electric alternates unavailable (A-M-282); '
                     'off-gas to MET_SCRUB when energized'},
       'the N+1 alternates, rated standby (A-M-283)')
    cad('COMB_HEAT', dict(service='combustion reheating furnace (C5-C10 fuel class), tertiary N+1 of IND_MELT',
                          connected_kW=f3('0.05'), thermal_kW=float(30), backup_of='IND_MELT', outage_d=f3('2.0'),
                          offgas='to MET_SCRUB when energized (COMB_OFFGAS)'),
        _ebox((1000, 1000, 1500), float(_round10(dh(charge, 7000))), hd), 'box_furnace', 'standby_rated',
        'A-M-199 melt class; N+1 rated envelope (A-M-283)')
    st('SINTER', {'source': DOC_F, 'rate_kg_d': float(0), 'connected_kW': float(8),
                  'backup_of': 'ROLL consolidation (press-and-sinter P/M route at the 0.5 kg/d powder class)',
                  'outage_basis': 'roll-stand outage at the powder-class lots (A-M-282)'},
       'the N+1 alternates, rated standby (A-M-283)')
    cad('SINTER', dict(service='Ti/Mo/Cr powder sinter furnace, N+1 consolidation of ROLL', connected_kW=float(8),
                       backup_of='ROLL', outage_d=f3('2.0'), design_case_kg_d=f3('0.5'), T_C=float(1300)),
        _ebox((1000, 1000, 1500), float(_round10(dh(Fraction(1, 2), 3000))), hd), 'box_furnace', 'standby_rated',
        'A-M-199 melt class at the powder-bulk density 3000 kg/m3 (study); N+1 rated envelope (A-M-283)')
    st('FORGE', {'source': DOC_F, 'rate_kg_d': float(0), 'connected_kW': float(11), 'backup_of': 'ROLL (open-die press)',
                 'outage_basis': 'roll-stand outage at the 10 kg/d bar class (A-M-282)'},
       'the N+1 alternates, rated standby (A-M-283)')
    cad('FORGE', dict(machine='open-die hydraulic press, N+1 former of ROLL', connected_kW=float(11),
                      backup_of='ROLL', outage_d=f3('2.0'), press_t=25, ram_mm=200),
        _ebox((1500, 800, 1500), float(D0), hd), 'line_machine', 'standby_rated',
        'A-M-199 forming class; N+1 rated envelope (A-M-283)')
    st('EXTRUDE', {'source': DOC_F, 'rate_kg_d': float(0), 'connected_kW': float(15),
                   'backup_of': 'ROLL (profile press at the Al/Cu profile class)',
                   'outage_basis': 'roll-stand outage on profile-class lots (A-M-282)'},
       'the N+1 alternates, rated standby (A-M-283)')
    cad('EXTRUDE', dict(machine='horizontal profile press, N+1 former of ROLL', connected_kW=float(15),
                        backup_of='ROLL', outage_d=f3('2.0'), press_t=50, container_mm=60),
        _ebox((1500, 800, 1500), float(D0), hd), 'line_machine', 'standby_rated',
        'A-M-199 forming class; N+1 rated envelope (A-M-283)')
    st('DRAW', {'source': DOC_F, 'rate_kg_d': float(0), 'connected_kW': float(3),
                'backup_of': 'ROLL (wire/rod bench at the 3 kg/d class)',
                'outage_basis': 'roll-stand outage on wire-class lots; wire sizing stays MFG WIRE_DRAW S57 (A-M-282)'},
       'the N+1 alternates, rated standby (A-M-283)')
    cad('DRAW', dict(machine='bench wire/rod draw bench, N+1 former of ROLL', connected_kW=float(3),
                     backup_of='ROLL', outage_d=f3('2.0'), bench_mm=1200, dies=6),
        _ebox((1500, 800, 1500), float(D0), hd), 'line_machine', 'standby_rated',
        'A-M-199 forming class; N+1 rated envelope (A-M-283)')
    # polymers: the live polyolefin line
    poly_feed = s['P'] * (1 + s['rej'])
    heat_w = eng(poly_feed * Fraction(21, 10) * 175 / 86400, 4)
    feed6 = eng(poly_feed, 6)
    st('POLY_OLEFIN', {'source': DOC_P, 'feed_kg_d': feed6, 'feed': 'C5-C10 naphtha at the cut tank (IA-C5-POLY)',
                       'T_C': '150-250', 'P_MPa': '1-5', 'heat_W': heat_w,
                       'basis': 'AQS-SIZE-OIL-POLY POLY_OLEFIN reactor; feed heating 25->200 C at 2.1 kJ/kg K, '
                       'exotherm neglected (study)'},
       'the polyolefin reactor (AQS-SIZE-OIL-POLY, A-M-264)')
    d_poly = dh(poly_feed, 750)
    dp = max(D(150), D(str(float(d_poly))))
    cad('POLY_OLEFIN', dict(vessel='vertical cylindrical oligomerization reactor', D_mm=150, H_mm=hd_mul(D(150)),
                            wall_mm=_hoop(5, 150), T_C=float(250), P_MPa=float(5),
                            op_window='150-250 C at 1-5 MPa (AQS-SIZE-OIL-POLY)', feed_kg_d=feed6, heat_W=heat_w,
                            material='SA-240 316L, welded (ASME IX)'),
        _ebox((600, 600, 1200), float(dp), hd), 'reactor', 'live',
        'reactor-class study minimum; DN150 at 1 d hold-up of the naphtha feed at 750 kg/m3 melt density; wall by '
        'ASME VIII-1 UG-27 at 5 MPa')
    st('PELLET', {'source': DOC_P, 'pellet_kg_d': feed6, 'form': '2-4 mm pellets (AQS-DES-POLY)'},
       'the pellet line (AQS-DES-POLY)')
    cad('PELLET', dict(machine='underwater die-face pelletizer', rate_kg_d=feed6, pellet_mm='2-4'),
        _ebox((1500, 800, 1500), float(dh(poly_feed, 500, Fraction(1, 24))), hd), 'line_machine', 'live',
        'A-M-199 forming class; hold-up of the resin stream is below the class minimum')
    cad('POLY_STOCK', dict(bin='pellet tote bin', issue_kg_d=eng(s['P'], 6), to_wet_kg_d=eng(s['rej'] * s['P'], 6),
                           hold_d=f3('1.0')),
        _ebox((600, 400, 800), float(dh(poly_feed, 500)), hd), 'store_bin', 'live',
        '1 d shop issue + reject staging at the 500 kg/m3 pellet bulk density (study; A-M-264)')
    st('POLY_COND', {'source': DOC_P, 'rate_kg_d': float(0),
                     'status_note': 'recipe waits on the digester organic assay (AQS-DES-POLY)'},
       'the condensation resin kettle, standby recipe hold (AQS-DES-POLY)')
    # the POLY_COND sizing block keeps the foundry-authored envelope size (the
    # fluoro family re-stamps its design/envelope, not its sizing)
    b.computed[('node', 'POLY_COND', 'params.sizing')][0]['size_mm'] = _ebox((600, 600, 1200), _flo('150.0'), hd)
    return s

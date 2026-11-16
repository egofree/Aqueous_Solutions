"""The methanol-train residual sizing family (family migration; reference writer
flow_graph/param/meoh_train.py, ledger row `sizing_meoh_train`, section B, MIXED:
split sizing -> this function, the MEOH_TRAIN.md page -> the renderer wave).

AQS-DUTY-077, unit task (MEOH)-02: MEOH_COND (the water-recovery condenser and
knock-out pot on IA-MEOH-H2O + S81 to ROOF_TANK) and MEOH_FC (the indirect
methanol fuel cell, installed 1.0 kW_e stack, continuous book 0.5 kW_e per the
Q-039 owner ruling 2026-11-13). The reference writer changes no rates; it
stamps the two units' params.design and params.size_note only, and the
committed graph carries exactly those fields. That committed state is the
golden this module reproduces.

Grid doctrine (owner ruling 2026-11-15): the solve is exact. Driver and seed
values convert at the boundary by rat() (the exact Fraction of the decimal
repr); the arithmetic is Fraction over the driver decimals. Quantisation
happens only at the reference writer's own rounding points, as integer books on
the sub-grid of the declared dimension: book(x, dp, cite) returns the exact
integer count of 10^-dp units, the dimension and scale named at every call
(the 4 dp design book, the 1 dp LMTD book, the 2 dp drum book, the 3 dp
methanol-energy book), unbook() renders the exact decimal. The transcendental
pieces port as fixed-precision Decimals: the log-mean temperature difference
from the natural log at 60 digits, the knock-out pot diameter from the cube
root at 60 digits (pi as the integer scaled pair 3141592653589793/10^15). The
50 mm vessel grid and the 10 mm coil divisor are integer scales. No float
literals; the lint holds this. The three driver passthroughs the design dict
carries verbatim (U_kW_m2K, cell_V, j_A_cm2, cell_A_cm2, meoh LHV into the
basis text) stay the reference writer's own raw values, documented here.

DISPOSITION: the graph stamps (the two design dicts and the size notes) land
here; docs-authority/sizing/MEOH_TRAIN.md is renderer-wave work (doc_meoh_train
row). The size_mm envelopes and the MEOH_FC continuous_kw dict are other
writers' fields and stay passthrough. A solve without the drivers records
nothing (the bridge contract).
"""
from decimal import Decimal, localcontext
from fractions import Fraction

from flow_graph.v2.registry import fn

STAGE = 'sizing_meoh_train'                                   # ledger row, section B
DOC = 'AQS-DUTY-077'
TAG = f'methanol train residual sizing (flow_graph/param/meoh_train.py, {DOC})'
MK = 'MEOH.synthesis-train.'                                  # the driver prefix (U4b single-sourcing)
PI = Decimal(3141592653589793) / Decimal(10) ** 15            # pi (scale 1e-15)
RHO_VAP = Fraction(13, 100)                                   # 0.13 kg/m3 water vapour at 50 C class
DRUM_MIN_M3 = Fraction(2, 1000)                               # the 2 L knock-out floor
COIL_M2 = Fraction(1, 10)                                     # 0.10 m2 per 10 mm x 1 m coil tube
CONDENSING = (('IA-MEOH-H2O', 'synthesis loop'), ('S81', 'fuel cell'))   # the water sources, in note order


def rat(value):
    """A v1 driver/seed value -> its exact Fraction (the decimal the JSON carried)."""
    return Fraction(Decimal(str(value)))


def _round_half_even(x, dp):
    """An exact value -> integer count of 10^-dp units, half-even (Python
    round()'s documented tie rule - the reference writer's rounding)."""
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
    """Render an integer book count as the exact JSON number of its decimal."""
    from decimal import Decimal as D
    f = float(D(cnt) / (D(10) ** dp))
    return float(0) if f == 0 else f


def fq(x, dp, cite):
    """book + render in one step: the exact value at `dp` decimals."""
    return unbook(book(x, dp, cite), dp)


def ceil_f(x):
    """math.ceil of an exact value."""
    return -((-x.numerator) // x.denominator)


def _ln_ratio(a, b):
    """ln(a/b) as a 60-digit Decimal (the LMTD log)."""
    with localcontext() as ctx:
        ctx.prec = 60
        return (Decimal(a) / Decimal(b)).ln()


def _cbrt(x):
    """The cube root of a positive exact value as a 60-digit Decimal."""
    with localcontext() as ctx:
        ctx.prec = 60
        xd = Decimal(x.numerator) / Decimal(x.denominator)
        return xd ** (Decimal(1) / Decimal(3))


def _ceil_grid_mm(x_mm, grid):
    """math.ceil(x/grid)*grid on an exact mm length: the vessel grid rule."""
    return int(ceil_f(x_mm / grid) * grid)


def _prov(basis, ref=None):
    from flow_graph.v2.model import Prov
    return Prov(STAGE, basis, ref)


def _set(b, uid, path, value, basis, ref=None):
    b.set_node_field(uid, path, value, _prov(basis, ref))


def _edge_rate_value(b, sid):
    """A seed rate value (0 where the edge or its rate is absent, the
    reference writer's `or 0`)."""
    e = b.edges.get(sid) or {}
    v = (e.get('rate') or {}).get('value')
    return rat(v) if isinstance(v, (int, float)) else Fraction(0)


def _core(b, inputs):
    """The sizing chain: the port of meoh_train.design() on exact rational
    arithmetic. Returns the two design dicts, or None without the drivers
    (the bridge contract)."""
    drv = inputs.get('drivers')
    if drv is None:
        return None

    def dv(k):
        return drv[k]['value']                                 # the raw driver value, as v1 carried it

    def v(k):
        return rat(dv(k))

    # ---- MEOH_COND: condense IA-MEOH-H2O + S81 at the loop dew point --------
    m_h2o = _edge_rate_value(b, 'IA-MEOH-H2O') + _edge_rate_value(b, 'S81')   # kg/d water to recover
    m_s = m_h2o / 86400                                        # kg/s
    lat = v(MK + 'MEOH_COND.latent_kJ_kg')                     # kJ/kg (IAPWS_IF97 class)
    dT_sh = v(MK + 'MEOH_COND.subcool_K')                      # K
    q = m_s * (v(MK + 'MEOH_COND.cp_vap_kJ_kgK') * dT_sh + lat) * 1000   # W, sensible + latent
    lmtd = Fraction(10) / Fraction(_ln_ratio(25, 15))          # (60-35)-(40-25) over ln((60-35)/(40-25))
    area = q / 1000 / (v(MK + 'MEOH_COND.U_kW_m2K') * lmtd)    # m2 at the water-on-water U
    qv = m_s / RHO_VAP                                         # m3/s vapour
    vdrum = max(qv * 30, m_h2o / 1000, DRUM_MIN_M3)            # 30 s residence or the daily condensate, >= 2 L
    d_mm = _ceil_grid_mm(Fraction(_cbrt(4 * vdrum / (Fraction(PI) * v(MK + 'MEOH_COND.drum_HD')))) * 1000,
                         Fraction(50))                          # bore on the 50 mm vessel grid
    h_mm = _ceil_grid_mm(vdrum / (Fraction(PI) * (Fraction(d_mm, 1000) ** 2) / 4) * 1000,
                         Fraction(50))                          # height on the same grid
    cond = dict(water_kg_d=fq(m_h2o, 4, 'recovered water, kg/d, 4 dp design book'),
                sources='IA-MEOH-H2O (synthesis loop) + S81 (fuel cell)',
                condensing_kW=fq(q / 1000, 4, 'condensing duty, kW, 4 dp design book'),
                U_kW_m2K=dv(MK + 'MEOH_COND.U_kW_m2K'),        # driver passthrough (documented)
                LMTD_K=fq(lmtd, 1, 'log-mean temperature difference, K, 1 dp design book'),
                area_m2=fq(area, 4, 'condenser area, m2, 4 dp design book'),
                tube=f'{ceil_f(area / COIL_M2)} x 10 mm x 1 m coil',
                drum_L=fq(vdrum * 1000, 2, 'knock-out pot volume, L, 2 dp design book'),
                D_mm=d_mm, H_mm=h_mm,
                to='condensate to ROOF_TANK (IA-MEOH-COND)',
                material='316L shell and coil (methanol/water traces)',
                note='knock-out pot + condenser on the same skid')

    # ---- MEOH_FC: the installed 1.0 kW_e stack, the continuous book on S79 --
    # Q-039 owner ruling (2026-11-13): the continuous book rides S79 at the
    # fuel-supported class; the installed 1.0 kW / 28-cell hardware rating is
    # standby capability (2 x 0.5 kW SI-DMFC-01 bank modules, AQS-REQ-KW-001).
    p_cont = _edge_rate_value(b, 'S79')                        # kW_e continuous book, fuel-supported class
    installed_kWe = 1                                          # installed hardware class (owner lock, Q-039)
    cell_point = v(MK + 'MEOH_FC.cell_V') * v(MK + 'MEOH_FC.cell_A_cm2') * v(MK + 'MEOH_FC.j_A_cm2')
    n_cells = ceil_f(installed_kWe * 1000 / cell_point)        # cells of the installed rating
    a_stack = v(MK + 'MEOH_FC.cell_A_cm2') / 10000             # one cell's active area, m2
    meoh = _edge_rate_value(b, 'S76')                          # kg/d methanol draw
    lhv = dv(MK + 'MEOH_FC.meoh_LHV_MJ_kg')                    # MJ/kg (PERRY9), passthrough in the basis text
    fc = dict(rated_kWe=fq(Fraction(installed_kWe), 4, 'installed rating, kW_e, 4 dp design book'),
              continuous_kW=fq(p_cont, 4, 'continuous book, kW_e, 4 dp design book'),
              methanol_kg_d=fq(meoh, 4, 'methanol draw, kg/d, 4 dp design book'),
              air_O2_kg_d=fq(_edge_rate_value(b, 'IA-FC-AIR'), 4, 'air O2 draw, kg/d, 4 dp design book'),
              water_kg_d=fq(_edge_rate_value(b, 'S81'), 4, 'water draw, kg/d, 4 dp design book'),
              CO2_kg_d=fq(_edge_rate_value(b, 'S82'), 4, 'CO2 return, kg/d, 4 dp design book'),
              heat_kW=fq(_edge_rate_value(b, 'S80'), 4, 'rejected heat, kW, 4 dp design book'),
              n_cells=n_cells, cell_V=dv(MK + 'MEOH_FC.cell_V'), j_A_cm2=dv(MK + 'MEOH_FC.j_A_cm2'),
              cell_A_cm2=dv(MK + 'MEOH_FC.cell_A_cm2'),
              stack_area_m2=fq(n_cells * a_stack, 4, 'stack active area, m2, 4 dp design book'),
              methanol_energy_kW=fq(meoh * rat(lhv) / Fraction(Decimal('86.4')), 3,
                                    'methanol LHV power, kW, 3 dp design book'),
              basis=(f'installed stack 1.0 kW (SI-DMFC-01 bank, 2 x 0.5 kW modules, standby per the '
                     f'Q-039 owner ruling 2026-11-13); cell point {dv(MK + "MEOH_FC.cell_V")} V at '
                     f'{dv(MK + "MEOH_FC.j_A_cm2")} A/cm2, {dv(MK + "MEOH_FC.cell_A_cm2")} cm2 cells '
                     f'(IEC62282_3_100 module class); methanol LHV {lhv} MJ/kg (PERRY9)'),
              material='PEM stack, 316L reformer shell (Cu/ZnO class catalyst), PTFE gaskets',
              note='skid at the issued 1800 x 800 x 1600 mm envelope; the continuous book is 0.5 kW_e on S79 '
                   '(Q-039 owner ruling 2026-11-13, fuel-limited at the settled S76 feed) and the installed 1.0 kW rating '
                   'is standby capability, so the skid runs at part load on the dispatch schedule; '
                   'the species edges (O2, CO2, water) close on the graph')
    return cond, fc


@fn('sizing_meoh_train', 'AQS-DUTY-077 methanol-train residual sizing (unit task (MEOH)-02): the MEOH_COND '
    'water-recovery condenser and knock-out pot (IAPWS_IF97 latent class, PERRY9 sec. 11 U, 50 mm vessel grid) '
    'and the MEOH_FC installed 1.0 kW_e stack with the 0.5 kW_e continuous book on S79 (Q-039 owner ruling '
    '2026-11-13, SI-DMFC-01 bank, IEC62282_3_100 cell point)')
def meoh_train(b, inputs):
    s = _core(b, inputs)
    if s is None:
        return                                                 # bridge contract: no drivers, no stamps
    cond, fc = s
    basis = (f'the methanol-train residual sizing ({DOC}): MEOH_COND dew-point duty on the seed water streams '
             'IA-MEOH-H2O + S81, MEOH_FC from the installed rating at the IEC62282_3_100 cell point; the '
             'continuous book rides S79 per the Q-039 owner ruling 2026-11-13')
    _set(b, 'MEOH_COND', 'params.design', cond, basis)
    _set(b, 'MEOH_COND', 'params.size_note', f'sized from the issued graph duties, {TAG}', basis)
    _set(b, 'MEOH_FC', 'params.design', fc, basis)
    _set(b, 'MEOH_FC', 'params.size_note', f'sized from the issued graph duties, {TAG}', basis)

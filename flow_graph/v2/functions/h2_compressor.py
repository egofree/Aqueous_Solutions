"""The sizing_h2_compressor family (family migration; reference writer
flow_graph/param/h2_compressor.py --write, ledger row `sizing_h2_compressor`,
section B, MIXED: split sizing -> this function, doc -> the renderer wave).
X-MFG-36 in-house multi-stage diaphragm H2 compressor for CRYO_H2 (A-M-169,
AQS-DUTY-067): equal pressure ratio per stage, intercooled to the suction
temperature; stage work W = k/(k-1) R T1/M (r^((k-1)/k) - 1)/eta_ad (ideal gas,
Perry's sec. 10 [DOE_H2_COMP], k from NIST_WEBBOOK); swept volume per stroke
from the suction flow, speed and volumetric efficiency; diaphragm diameter from
a shallow spherical-cap cavity, V about pi D^2 h / 8. Stage count: the fewest
equal-ratio stages whose predicted discharge stays at or below 135 C [API618].
Average power on the energy balance; sized at the peak rate (run hours). Two
compressors (one standby) per the redundancy rule. The committed graph carries
every field the stage stamps; that committed state is the golden this function
reproduces. The power family's critical list reads this stage's
params.compressor_design.P_peak_kW (the CRYO_H2 outage slice, AQS-ELEC-007 /
AQS-DUTY-067) and this function's continuous_kw book feeds the same census -
the downstream read the composition has to order after this family.

Grid doctrine (owner ruling 2026-11-15): driver and seed values convert at this
boundary by dec() (the exact Decimal of the decimal repr); the v1 quantise
points emit through book()/unbook() - the integer count of 10^-dp units,
half-even, with the dimension and scale cited at every call - and every stage
number, count and the unit driver run as native integers. Dimensionless
constants port as integer scaled pairs with the scale in the name (the 86400 s
day, the 3600 s hour, the 1000 W/kW ladder, the 3.6e6 J/kWh book, the stage
loop). No float literals; the lint holds this.

The books that stay v1 float books by necessity, documented here: the whole
params.compressor_design block. The reference writer stores its solve dict
UNROUNDED (json round-trip of raw doubles) and the chains behind it are
transcendental in float space (the stage search on R**(1/n), the r**x isentropic
work, the cube-root-free but transcendental diaphragm diameter on pi, the
universal gas constant quotient Rm = 8.314/0.002016). Those books reproduce the
committed repr exactly through a float replica of the v1 expression over the
same inputs (no literals; the floats come from the exact boundary books by
flo(), and the float-lane constants enter as the decimal strings of the v1
literals). The continuous kW book and the SF feed value quantise at 4 dp
through book()/unbook(), whose float path converts through the exact binary
value (Fraction), so it is Python round()'s own tie rule.

Seed reads (prior-family fields, recorded): H2_kg_d is the sum of the committed
mass books of every edge into CRYO_H2 (the storage/electrolysis families'
rates; the v1 sum runs over the graph's edge-list order).

Disposition of the chains around this family (the strangler bridge):
- docs-authority/sizing/H2_COMPRESSOR.md (AQS-DUTY-067) is the renderer wave's:
  the doc consumed H2_kg_d, n_stages, ratio_per_stage, T_limit_C, kWh_per_kg,
  P_avg_kW, P_peak_kW, the per-stage books (P_in_bar, P_out_bar, T_out_C,
  intercooler_W, swept_cm3, diaphragm_D_mm), the units driver and the material
  string, plus the h2c_P1_bar/h2c_P2_bar drivers and the suction temperature in
  C, and the units>1 sentence rule.
- SF-CRYO_H2 is a value-only update (SQ-CRYO_H2 died with Rev AC; the guard
  covers a seed that carries it): the seed rate dict passes through with only
  the value replaced.

The v1 machinery (disk write-back, the doc render, the stdout dump) does not
migrate: assignment replaces the field and its provenance in full. A solve
without the driver payload records nothing, so the bridge solve and the check
stay byte-faithful to the seed.
"""
import math
from decimal import Decimal, ROUND_HALF_EVEN
from fractions import Fraction

from flow_graph.v2.registry import fn

STAGE = 'h2_compressor'                                        # ledger row sizing_h2_compressor, provenance stage
TAG = 'X-MFG-36 (A-M-169)'
CB = 'CRYO.cold-box-asu-recovery-train.cold-box.CRYO_H2.'      # U4b: sizing literals single-sourced from drivers.json
DAY_S = Fraction(86400)                                        # s, the transport book's day
HOUR_S = Fraction(3600)                                        # s, the run-hour book
K_W = Fraction(1000)                                           # W per kW
J_KWH = Decimal('3600000')                                     # J per kWh (3.6e6)
M_H2 = Decimal('0.002016')                                     # kg/mol, the v1 Rm denominator book
F0 = Decimal('0.0')                                            # the v1 zero book (float lane)
MATERIAL = ('head and plates 17-4PH H1150 / 316L (hydrogen service), triple-layer 301 SS diaphragm with '
            'leak detection between layers')


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


def _edge_value(b, sid, value, basis, ref=None):
    """Value-only update on an existing rate (the feed edges carry other
    writers' notes)."""
    seed = dict(b.edges[sid]['rate'])
    seed['value'] = value
    b.set_edge_rate(sid, seed, _prov(basis, ref))


def h2_mass_kg_d(b):
    """The committed mass books into CRYO_H2, summed over the graph's edge-list
    order (the v1 sum; the storage and electrolysis families own the rates)."""
    total = flo(F0)
    for e in b.data['edges']:
        if e['to_unit_id'] == 'CRYO_H2' and 'mass' in (e.get('layers') or []):
            total += e['rate']['value']
    return total


def design(b, drv):
    """The v1 h2_compressor.design() port on the recorded boundary. Returns
    the design dict in the v1 key order."""
    def v(k):
        return drv[k]['value'] if k in drv else drv[CB + k]['value']

    m_d = h2_mass_kg_d(b)
    k = flo(dec(v('h2c_k')))
    t1 = flo(dec(v(CB + 'h2c_T_suction_K')))
    rm = flo('8.314') / flo(dec(M_H2))                # J/kg K, the universal gas constant quotient
    x = (k - 1) / k
    ratio = flo(dec(v('h2c_P2_bar'))) / flo(dec(v('h2c_P1_bar')))
    eta_ad = flo(dec(v('h2c_eta_ad')))
    t_out_max = flo(dec(v('h2c_T_out_max_C')))

    def tout(r):
        return t1 * (1 + (r ** x - 1) / eta_ad)

    n = 1                                                  # the fewest equal-ratio stages within the
    while tout(ratio ** (1 / n)) - flo('273.15') > t_out_max:
        n += 1                                             # API618 135 C discharge limit
    r = ratio ** (1 / n)
    w = n * k / (k - 1) * rm * t1 * (r ** x - 1) / eta_ad  # J/kg, n stages
    run_h = flo(dec(v('h2c_run_h')))
    m_pk = m_d / run_h / float(HOUR_S)
    eta_motor = flo(dec(v('h2c_eta_motor')))
    p_avg = m_d / float(DAY_S) * w / eta_motor / float(K_W)
    p_pk = m_pk * w / eta_motor / float(K_W)
    stages = []
    rpm = flo(dec(v('h2c_rpm')))
    eta_v = flo(dec(v('h2c_eta_v')))
    h = flo(dec(v('h2c_cavity_h_mm'))) / float(Fraction(1000))
    cp = flo(dec(v('h2c_cp_kJ_kgK')))
    for i, p_s in enumerate([flo(dec(v('h2c_P1_bar'))) * r ** j for j in range(n)]):
        rho = p_s * flo('1e5') / (rm * t1)
        vs = m_pk / rho / (rpm / 60 * eta_v)
        stages.append(dict(stage=i + 1, P_in_bar=p_s, P_out_bar=p_s * r, T_out_C=tout(r) - flo('273.15'),
                           intercooler_W=m_pk * cp * float(Fraction(1000)) * (tout(r) - t1),
                           swept_cm3=vs * float(Fraction(1000000)),
                           diaphragm_D_mm=math.sqrt(8 * vs / (math.pi * h)) * float(Fraction(1000))))
    units = v(CB + 'h2c_units')
    return dict(H2_kg_d=m_d, n_stages=n, T_limit_C=t_out_max, ratio_per_stage=r,
                kWh_per_kg=w / float(J_KWH) / eta_motor, P_avg_kW=p_avg, P_peak_kW=p_pk,
                stages=stages, units=units, material=MATERIAL)


@fn('h2_compressor', 'X-MFG-36 in-house multi-stage diaphragm H2 compressor for CRYO_H2 (A-M-169, '
    'AQS-DUTY-067): equal-ratio staging to the API618 135 C discharge limit [DOE_H2_COMP, NIST_WEBBOOK], '
    'intercooled per stage, sized at the peak rate over the run hours; two units, one standby, per the '
    'redundancy rule')
def h2_compressor(b, inputs):
    drv = inputs.get('drivers')
    if drv is None or 'CRYO_H2' not in b.nodes:
        return                                             # bridge contract: no drivers, no stamps
    r = design(b, drv)
    basis = ('X-MFG-36 in-house diaphragm H2 compressor (A-M-169, AQS-DUTY-067): equal-ratio staging to the '
             'API618 135 C discharge limit, intercooled per stage, average power on the energy balance, peak '
             'rate over the run hours; two units, one standby (redundancy rule)')
    v1, v2 = flo(dec(drv['h2c_P1_bar']['value'])), flo(dec(drv['h2c_P2_bar']['value']))
    _set(b, 'CRYO_H2', 'params.compressor_design', dict(r), basis, 'A-M-169')
    _set(b, 'CRYO_H2', 'params.compressor',
         f"in-house {r['n_stages']}-stage diaphragm, {v1:g} to {v2:g} bar, intercooled, {r['units']:g} x 100 % (X-MFG-36)",
         basis, 'A-M-169')
    kw = unbook(book(r['P_avg_kW'], 4, 'power kW: the continuous book at 4 dp'), 4)
    _set(b, 'CRYO_H2', 'continuous_kw', {
        'value': kw, 'unit': 'kW', 'status': 'study',
        'note': (f"{TAG}: {r['H2_kg_d']:.2f} kg/d x {r['kWh_per_kg']:.2f} kWh/kg; peak {r['P_peak_kW']:.2f} kW "
                 'over the run hours.')}, basis, 'A-M-169')
    for sid in ('SF-CRYO_H2', 'SQ-CRYO_H2'):
        if sid in b.edges:                                 # R11 Rev AC regen: SQ-* heat edges died with HEAT_SINK
            _edge_value(b, sid, kw, basis, 'A-M-169')

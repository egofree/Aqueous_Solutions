"""The X-MFG-34 RO/EDI polish family (family migration; reference writer
flow_graph/param/upw_polish.py `--write`, ledger row `sizing_upw_polish`,
section B, MIXED: split sizing -> this function, the sizing doc -> the renderer
lane). The BMED_UPW_POLISH train: the potable share bypasses to REMIN; only
the UPW products (IA-UPW-FAB to the fab, S01 to HDR_UPW) pass reverse osmosis
then electrodeionisation. RO: solution-diffusion J = A (dP - dpi) with
dpi = 2 c R T [BAKER2012], area = permeate / design flux, feed pressure from
the permeance; EDI: I = F n / CE for the salt left in the RO permeate, cell
pairs x cell voltage [ALVARADO2014]; the UV-TOC lamp at its driver rating.
The committed graph carries every field the v1 stage stamps; that committed
state is the golden this module reproduces.

Grid doctrine (owner ruling 2026-11-15): driver and seed values cross the
boundary through dec() (the exact Decimal of the decimal repr). Physical
constants port as integer scaled pairs or exact decimal strings: the Faraday
book 96485 C/mol (the reference writer's own constant, not CODATA2018), R
8.314 J/(mol K), NaCl 58.44 g/mol, the Pa-per-bar book 1/100000, the ppm/L
conversions /1000 and /86400 s. Schema fields quantise half-even at the
decimals the v1 schema stores: the kW books at 4 dp (Python round()'s tie
rule). No float literals.

THE RAW-FLOAT DESIGN BOOKS. v1 stored params.design as the unrounded float
chain (a json round-trip, no blanket rounding), and the v1 writer's own
rounding (the continuous_kw book at 4 dp) ran on that chain. An exact-Decimal
book floats a ulp away from the committed repr (the RO feed itself, 127.300395
+ 6.045005, carries the v1 float dust 133.34539999999998 on the graph), so -
the foundry-family precedent (flow_graph/v2/functions/foundry.py, module
docstring) - the stored design numerics stay v1 float books: float replicas of
the reference writer's expressions over the same boundary inputs, constants
entering as floats of their exact decimals by fl(). The exact-Decimal audit
books (recovery, osmotic pressure, the EDI current) live in the family test as
independent re-derivations.

Disposition of the chains around this family (the strangler bridge):
- The sizing doc (docs-authority/sizing/UPW_POLISH.md, AQS-DUTY-070) is
  renderer-lane work. It consumes, from the fields this function stamps:
  ro_feed_TDS_mg_L (driver), bypass_kg_d, UPW_kg_d, RO_feed_kg_d, recovery,
  membrane_m2, modules, osmotic_bar, feed_bar, EDI_A, EDI_kW, UV_kW,
  total_kW, kWh_per_m3 and kWh_per_m3_RO_EDI, plus the ro_*/edi_* driver
  texts.
- params.internals is the machine text, ported verbatim as data.
- The SQ-BMED_UPW_POLISH heat edge died with HEAT_SINK in Rev AC; the v1
  guard updates what exists, so on the committed seed it is absent - this
  function asserts that and stamps nothing on it (builder lane). The
  SF-BMED_UPW_POLISH book is re-rated value-only, the seed note preserved.
A solve without the driver payload records nothing, so the bridge solve and
the check stay byte-faithful to the seed.
"""
from decimal import Decimal

from flow_graph.v2.registry import fn

STAGES = 'sizing_upw_polish'                                   # ledger row, section B
TAG = 'X-MFG-34 (A-M-176, AQS-DUTY-070)'
REF = 'A-M-176'
UPW_UNIT = 'BMED_UPW_POLISH'
RO_PREFIX = 'WTR.potable-upw-train.BMED_UPW_POLISH.'           # the UPW driver prefix (A-M-176)
F_COULOMB = 96485                                              # C/mol, the reference writer's Faraday book
R_GAS = '8.314'                                                # J/(mol K), the reference writer's book
M_NACL = '58.44'                                               # g/mol NaCl, the reference writer's book
BAR = Decimal(10) ** 5                                         # Pa per bar
INTERNALS = 'potable bypass; 2 x flat-sheet RO module, 2 x EDI stack, UV-TOC lamp'


def dec(value):
    """A v1 float/int/str -> exact Decimal at the boundary (decimal repr)."""
    return Decimal(str(value))


def fl(value):
    """The v1 float of an exact decimal (for the documented raw-float books):
    identical bits to the JSON literal the reference writer carried."""
    return float(dec(value))


def q(x, dp):
    """Quantise to `dp` decimals, half-even - Python round()'s documented tie
    rule, the rounding the v1 writer used; scale named at the call."""
    return round(fl(x), dp)


def _prov(basis, ref=None):
    from flow_graph.v2.model import Prov
    return Prov(STAGES, basis, ref)


def _set(b, uid, path, value, basis, ref=None):
    b.set_node_field(uid, path, value, _prov(basis, ref))


def osmotic_bar(c_feed, recovery, rejection, t_k):
    """The exact mean feed-side osmotic pressure (audit book, bar): the
    concentrate c_conc = c (1 - (1 - rejection) recovery) / (1 - recovery) at
    the graph recovery, dpi = 2 c R T [BAKER2012] at the mean of feed and
    concentrate, over the Pa-per-bar book."""
    c = c_feed
    c_conc = c * (1 - (1 - rejection) * recovery) / (1 - recovery)
    return 2 * (c + c_conc) / 2 * dec(R_GAS) * t_k / BAR


@fn('upw_polish', 'X-MFG-34 RO/EDI polish (A-M-176, AQS-DUTY-070): solution-diffusion RO J = A (dP - dpi) '
    '[BAKER2012] at the graph recovery, EDI I = F n / CE [ALVARADO2014] on the salt left in the permeate, '
    'UV-TOC at the driver rating; potable share bypasses')
def upw_polish(b, inputs):
    drv = inputs.get('drivers')
    if drv is None:
        return                                                  # the bridge contract: no payload, no stamps
    if UPW_UNIT not in b.nodes:
        return
    need = ('IA-UPW-FAB', 'S01', 'IA-UPW-REJ', 'IA-UPW-REMIN')
    if not all(sid in b.edges for sid in need):
        return                                                  # the graph duty is incomplete: record nothing
    assert 'SQ-' + UPW_UNIT not in b.edges, \
        'upw_polish: the seed carries an SQ heat edge the Rev AC graph retired (builder topology)'

    def rate_f(sid):
        return fl(b.edges[sid]['rate']['value'] or 0)           # the v1 r() read

    def dv(k):
        return fl(drv[k]['value'])

    upw = rate_f('IA-UPW-FAB') + rate_f('S01')                  # kg/d, the UPW products
    rej = rate_f('IA-UPW-REJ')
    feed = upw + rej                                            # kg/d, the RO feed
    rec = upw / feed                                            # the graph recovery
    c = dv('ro_feed_TDS_mg_L') / fl(M_NACL)                     # mol/m3 NaCl
    rejection = dv('ro_rejection')
    t_k = fl(drv[RO_PREFIX + 'ro_eval_T_K']['value'])
    dpi = 2 * (c + c * (1 - (1 - rejection) * rec) / (1 - rec)) / 2 * fl(R_GAS) * t_k / fl(BAR)  # bar
    d_p = dv('ro_flux_LMH') / dv('ro_A_LMH_bar') + dpi          # bar, the RO feed pressure
    area = upw / 24 / dv('ro_flux_LMH')                         # m2 (kg/d ~ L/d)
    qf = feed / 1000 / 86400                                    # m3/s
    p_ro = qf * d_p * fl(BAR) / dv('ro_pump_eta') / 1000        # kW
    c_perm = c * (1 - rejection)                                # mol/m3 in the permeate
    n_mol = upw / 1000 / 86400 * c_perm                         # mol/s
    i_edi = F_COULOMB * n_mol / dv('edi_CE')                    # A
    p_edi = i_edi * dv('edi_V_cell') * fl(drv['edi_cells']['value']) / 1000   # kW
    p_uv = dv('upw_uv_W') / 1000                                # kW
    total = p_ro + p_edi + p_uv
    basis = ('X-MFG-34 RO/EDI polish (A-M-176, AQS-DUTY-070) from the graph duty: IA-UPW-FAB + S01 products, '
             'IA-UPW-REJ reject; ro_*/edi_* drivers (flow_graph/param/upw_polish.py port)')
    per_m3 = total * 24 / (feed / 1000)
    per_m3_ro_edi = (p_ro + p_edi) * 24 / (feed / 1000)
    stamps = (
        ('UPW_kg_d', upw, 'the UPW products at the seed rates'),
        ('bypass_kg_d', rate_f('IA-UPW-REMIN'), 'the potable share, which bypasses the train'),
        ('RO_feed_kg_d', feed, 'products + reject'),
        ('recovery', rec, 'products / feed on the graph rates'),
        ('osmotic_bar', dpi, '2 c R T at the mean feed-side concentration [BAKER2012]'),
        ('feed_bar', d_p, 'flux / permeance + osmotic (solution-diffusion, BAKER2012)'),
        ('membrane_m2', area, 'permeate / 24 h / driver ro_flux_LMH'),
        ('modules', drv[RO_PREFIX + 'ro_modules']['value'], 'driver ro_modules (one standby; the int book stays int)'),
        ('RO_kW', p_ro, 'Q dP / ro_pump_eta'),
        ('EDI_A', i_edi, 'F n / edi_CE on the salt left in the RO permeate [ALVARADO2014]'),
        ('EDI_kW', p_edi, 'I x edi_V_cell x edi_cells / 1000'),
        ('UV_kW', p_uv, 'driver upw_uv_W'),
        ('total_kW', total, 'RO + EDI + UV'),
        ('kWh_per_m3', per_m3, 'total x 24 h per m3 of RO feed'),
        ('kWh_per_m3_RO_EDI', per_m3_ro_edi, 'RO + EDI only'),
    )
    for key, val, cite in stamps:
        _set(b, UPW_UNIT, 'params.design.' + key, val, basis + '; ' + cite, REF)
    _set(b, UPW_UNIT, 'params.internals', INTERNALS, 'the machine text (design decision, verbatim)', REF)
    kw = q(total, 4)
    _set(b, UPW_UNIT, 'continuous_kw.value', kw, basis, REF)
    _set(b, UPW_UNIT, 'continuous_kw.note',
         f'{TAG}: RO pump {p_ro * 1000:.1f} W + EDI {p_edi * 1000:.2f} W + UV {p_uv * 1000:.0f} W; '
         'potable share bypasses.', basis, REF)
    seed_ckw = b.nodes[UPW_UNIT].get('continuous_kw') or {}
    if 'status' not in seed_ckw:
        _set(b, UPW_UNIT, 'continuous_kw.status', 'study', basis, REF)
    if 'unit' not in seed_ckw:
        _set(b, UPW_UNIT, 'continuous_kw.unit', 'kW', basis, REF)
    if 'SF-' + UPW_UNIT in b.edges:
        book = dict(b.edges['SF-' + UPW_UNIT]['rate'])
        book['value'] = kw
        b.set_edge_rate('SF-' + UPW_UNIT, book,
                        _prov(basis + '; the feed edge re-rated to the node book (the seed note stands)', REF))

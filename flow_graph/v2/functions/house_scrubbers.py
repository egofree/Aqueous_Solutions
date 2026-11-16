"""The X-PAR-03 house scrubber family (family migration; reference writer
flow_graph/param/house_scrubbers.py `--write`, ledger row `sizing_house_scrubbers`,
section B, MIXED: split sizing -> this function, the sizing doc -> the renderer
lane). The packed-column scrubber sizing applied to ALK_SCRUBBER,
ACID_POLISH_SCRUB, NOX_SCRUB and MET_SCRUB (A-M-164): gas volume from the graph
mass inflow at the 1.2 kg/m3 book, diameter from flooding at the design
fraction (sizing.scrubber [PERRY9_ABS]) and not below 8 packing diameters, bed
= HTU x ln(1/(1 - removal)) for the irreversible-absorption target with the
0.5 m minimum, liquid from the minimum wetting rate, fan on the bed plus the
250 Pa fixed losses, pump on head at the site gravity. The committed graph
carries every field the v1 stage stamps; that committed state is the golden
this module reproduces.

Grid doctrine (owner ruling 2026-11-15): driver, seed and site-profile values
cross the boundary through dec() (the exact Decimal of the decimal repr);
arithmetic is exact Decimal. Dimensionless constants port as integer scaled
pairs with the scale in the name: the liquid density 1000 kg/m3, the 3600 s
hour, the 86400 s day, the 50 mm vessel-diameter grid, pi as
3141592653589793/10^15. Schema fields quantise half-even at the decimals the
v1 schema stores: the design books at 4 dp (Python round()'s tie rule), the
vessel height and diameter as integer mm books (the diameter on the 50 mm
envelope grid by ceiling). No float literals.

Disposition of the chains around this family (the strangler bridge):
- The sizing doc (docs-authority/sizing/HOUSE_SCRUBBERS.md, AQS-DUTY-079) is
  renderer-lane work. It consumes, per unit, from the fields this function
  stamps: duty, gas_kg_d, Q_m3_s, u_flood_m_s, D_mm, packed_mm, H_mm,
  recirc_m3_h, dP_Pa, fan_W, pump_W, kW, plus the packing driver texts
  (hs_Cs_flood_m_s, hs_frac_flood, vs_d_over_dp, hs_removal, vs_mwr, hs_dp_mm,
  hs_htu_m, hs_dP_Pa_m, hs_a_m2_m3, hs_gas_rho_kg_m3).
- The SQ-* heat edges died with HEAT_SINK in Rev AC; v1 created them only when
  both endpoints existed, so on the committed seed they are absent - this
  function asserts that and stamps nothing on them (builder lane).
- The SF-* feed edges exist for all four units; v1 re-rated value and note and
  preserved unit/status - ported as the seed-book copy it is.
- Site profile: this function reads gravity.g_m_s2 (the pump-head arithmetic;
  v1's SITE.g()) from inputs['site_profile']. A solve without the driver
  payload or the profile records nothing, so the bridge solve and the check
  stay byte-faithful to the seed.
"""
from decimal import Decimal, ROUND_CEILING, ROUND_HALF_EVEN

from flow_graph.v2.registry import fn

STAGES = 'sizing_house_scrubbers'                              # ledger row, section B
TAG = 'X-PAR-03 house scrubber (flow_graph/param/house_scrubbers.py, A-M-164)'
REF = 'A-M-164'
HSK = 'GAS.scrubbing-headers-train.scrubbing.'                 # the scrubbing sizing driver prefix (A-M-164)
UNITS = {'ALK_SCRUBBER': 'NaOH scrub of the house acid-gas header',
         'ACID_POLISH_SCRUB': 'acid polish of the same air (liquor to CRU)',
         'NOX_SCRUB': 'flue, leach off-gas and nitric vents',
         'MET_SCRUB': 'metal-aisle fume and mist (wet scrubber ahead of the baghouse filter)'}
MATERIAL = 'PP-H shell and in-house cut PP rings; PP mesh demister'
SIZE_NOTE = 'L x W x H mm, set by flow_graph/param/house_scrubbers.py (X-PAR-03)'
RHO_L = Decimal(1000)                                          # kg/m3, the liquid book (water)
HOUR_S, DAY_S = Decimal(3600), Decimal(86400)                  # s
DIA_GRID = 50                                                  # mm, the vessel-diameter envelope grid
PI = Decimal(3141592653589793) / Decimal(10) ** 15             # pi (scale 1e-15)
SIZE_NOTE_BASIS = 'the vessel envelope on the 50 mm diameter grid (design decision, verbatim text)'
D1 = Decimal(1)


def dec(value):
    """A v1 float/int/str -> exact Decimal at the boundary (decimal repr)."""
    return Decimal(str(value))


def q(x, dp):
    """Quantise an exact value to `dp` decimals, half-even - Python round()'s
    documented tie rule, the rounding the v1 writer used; scale named at the
    call. Returns the JSON float the schema stores."""
    f = float(Decimal(x).quantize(D1.scaleb(-dp), rounding=ROUND_HALF_EVEN))
    return float(0) if f == 0 else f                           # no signed zeros in the book


def qi(x):
    """round(x) as v1 wrote it: half-even to an integer (the length book)."""
    return int(Decimal(x).quantize(D1, rounding=ROUND_HALF_EVEN))


def ceil_int(x):
    """math.ceil of an exact value."""
    return int(Decimal(x).to_integral_value(rounding=ROUND_CEILING))


def _prov(basis, ref=None):
    from flow_graph.v2.model import Prov
    return Prov(STAGES, basis, ref)


def _set(b, uid, path, value, basis, ref=None):
    b.set_node_field(uid, path, value, _prov(basis, ref))


def flood_velocity(cs, rho_l, rho_g):
    """sizing.scrubber.flood_velocity_m_s [PERRY9_ABS]: u_f = C_s sqrt((rho_L - rho_G)/rho_G)."""
    return cs * ((rho_l - rho_g) / rho_g).sqrt()


def diameter(q_gas, u_flood, frac):
    """sizing.scrubber.diameter_m [PERRY9_ABS]: D = sqrt(4 Q / (pi f u_f))."""
    return (4 * q_gas / (PI * frac * u_flood)).sqrt()


def packed_height(htu, removal):
    """sizing.scrubber.packed_height_m [PERRY9_ABS]: HTU x ln(1/(1 - removal))."""
    return htu * (1 / (1 - removal)).ln()


def min_liquid(d_m, a_m2_m3, mwr):
    """sizing.scrubber.min_liquid_m3_h [PERRY9_ABS]: L >= MWR x a x column area."""
    return mwr * a_m2_m3 * PI * d_m * d_m / 4


@fn('house_scrubbers', 'X-PAR-03 packed-column sizing on the house scrubbers (A-M-164, PERRY9_ABS): diameter from '
    'flooding at the design fraction and not below 8 packing diameters, bed = HTU x ln(1/(1-removal)), liquid from '
    'the minimum wetting rate, fan on bed + fixed losses, pump on head')
def house_scrubbers(b, inputs):
    drv = inputs.get('drivers')
    prof = inputs.get('site_profile')
    if drv is None or prof is None:
        return                                                  # the bridge contract: no payload, no stamps

    def dv(k):
        return drv[k]['value']                                  # the driver as written

    g_m_s2 = dec(prof['groups']['gravity']['entries']['g_m_s2']['value'])   # site gravity (v1 SITE.g())
    rho_g = dec(dv(HSK + 'hs_gas_rho_kg_m3'))
    cs, frac = dec(dv('hs_Cs_flood_m_s')), dec(dv('hs_frac_flood'))
    dp_mm, d_over_dp = dec(dv('hs_dp_mm')), dec(dv('vs_d_over_dp'))
    htu, removal = dec(dv('hs_htu_m')), dec(dv('hs_removal'))
    a_m2_m3, mwr = dec(dv('hs_a_m2_m3')), dec(dv('vs_mwr'))
    dpa_m, fixed_dp = dec(dv('hs_dP_Pa_m')), dec(dv(HSK + 'hs_fixed_dP_Pa'))
    fan_eff = dec(dv('hs_fan_eff'))
    head_m, pump_eff = dec(dv('hs_pump_head_m')), dec(dv('hs_pump_eff'))
    bed_min, allow = dec(dv(HSK + 'hs_bed_min_m')), int(dv(HSK + 'hs_vessel_allow_mm'))
    side, top = int(dv(HSK + 'hs_envelope_side_mm')), int(dv(HSK + 'hs_envelope_top_mm'))
    uf = flood_velocity(cs, RHO_L, rho_g)                       # m/s, the flood velocity book
    for u, duty in UNITS.items():
        if u not in b.nodes:
            continue
        gas = sum((dec(e['rate']['value'] or 0) for e in b.data['edges']
                   if e['to_unit_id'] == u and 'mass' in (e.get('layers') or [])
                   and e['phase'].startswith(('G', 'L/G'))), Decimal(0))   # kg/d, the graph gas inflow
        q_gas = gas / rho_g / DAY_S                             # m3/s
        d_m = max(diameter(q_gas, uf, frac), dp_mm * d_over_dp / 1000)     # m, not below 8 packing diameters
        z_m = max(bed_min, packed_height(htu, removal))         # m, the packed bed
        liq = min_liquid(d_m, a_m2_m3, mwr)                     # m3/h, the minimum wetting rate
        d_p = dpa_m * z_m + fixed_dp                            # Pa
        fan_w = q_gas * d_p / fan_eff
        pump_w = liq / HOUR_S * 1000 * g_m_s2 * head_m / pump_eff
        d_mm = ceil_int(d_m * 1000 / DIA_GRID) * DIA_GRID       # the 50 mm envelope grid
        h_mm = qi(z_m * 1000) + allow                           # sump, distributor and demister allowance
        kw = q((fan_w + pump_w) / 1000, 4)
        basis = (f'X-PAR-03 packed-column sizing (A-M-164, PERRY9_ABS) on the {u} graph gas inflow; packing drivers '
                 'hs_*/vs_* (flow_graph/param/house_scrubbers.py port)')
        for key, val, cite in (
                ('gas_kg_d', q(gas, 4), 'the graph mass inflow, G and L/G phase edges'),
                ('Q_m3_s', q(q_gas, 4), 'gas / 1.2 kg/m3 book / 86400 s'),
                ('u_flood_m_s', q(uf, 4), 'C_s sqrt((rho_L - rho_G)/rho_G), PERRY9_ABS'),
                ('D_mm', d_mm, 'flooding at driver hs_frac_flood, not below 8 packing diameters (vs_d_over_dp); '
                 '50 mm envelope grid'),
                ('packed_mm', qi(z_m * 1000), 'HTU x ln(1/(1 - hs_removal)), 0.5 m minimum'),
                ('H_mm', h_mm, 'packed bed + the vessel allowance (sump, distributor, demister)'),
                ('recirc_m3_h', q(liq, 4), 'the minimum wetting rate vs_mwr x a x column area'),
                ('dP_Pa', q(d_p, 4), 'hs_dP_Pa_m x bed + the 250 Pa fixed losses'),
                ('fan_W', q(fan_w, 4), 'Q dP / hs_fan_eff'),
                ('pump_W', q(pump_w, 4), 'L / 3600 s x 1000 g/L x site gravity x head / hs_pump_eff'),
                ('kW', kw, '(fan + pump) / 1000, 4 dp book')):
            _set(b, u, 'params.design.' + key, val, basis + '; ' + cite, REF)
        _set(b, u, 'params.design.duty', duty, 'the unit duty text (design decision, verbatim)', REF)
        _set(b, u, 'params.design.material', MATERIAL, 'the material text (design decision, verbatim)', REF)
        _set(b, u, 'params.size_mm', [d_mm + side, d_mm + side, h_mm + top], SIZE_NOTE_BASIS, REF)
        _set(b, u, 'params.size_note', SIZE_NOTE, SIZE_NOTE_BASIS, REF)
        _set(b, u, 'continuous_kw.value', kw, basis, REF)
        _set(b, u, 'continuous_kw.note',
             f'{TAG}. Fan {q(fan_w, 4):.0f} W, pump {q(pump_w, 4):.0f} W.', basis, REF)
        seed_ckw = b.nodes[u].get('continuous_kw') or {}
        if 'status' not in seed_ckw:
            _set(b, u, 'continuous_kw.status', 'study', basis, REF)
        if 'unit' not in seed_ckw:
            _set(b, u, 'continuous_kw.unit', 'kW', basis, REF)
        if 'SF-' + u in b.edges:
            book = dict(b.edges['SF-' + u]['rate'])
            book['value'], book['note'] = kw, TAG + '.'
            b.set_edge_rate('SF-' + u, book, _prov(basis + '; the feed edge re-rated to the node book', REF))
        assert 'SQ-' + u not in b.edges, \
            f'house_scrubbers: the seed carries an SQ-{u} edge the Rev AC graph retired (builder topology)'

"""The sizing_cold_box family (family migration; reference writer
flow_graph/param/cold_box.py --write, ledger row `sizing_cold_box`, section B,
MIXED: split sizing -> this function, doc -> the renderer wave). X-MFG-33
in-house CRYO_ASU separation train (AQS-DUTY-069, A-M-175): sized from the duty
on the graph, not from an air plant. The cold box has no air intake (IA-AIR-IN
0): its feed is the scrubbed flue from NOX_SCRUB, nitrogen with a little O2 and
CO2. Nitrogen already meets its 99 % product purity once the CO2 is out, so no
cryogenic column is needed. The design: 13X temperature-swing beds take out the
CO2 (three beds, one adsorbing, one regenerating at 204 C [NASA_CDRA2015], one
standby); the desorbed CO2 goes to an intercooled compressor staged so the
discharge stays within 150 C [API618], to the 20 bar store and is condensed at
-20 C [NIST_WEBBOOK]; the Ar return passes a heated getter; He, Ne, Kr and Xe
are closed inventories that pass through with no separation duty. The committed
graph carries every field the stage stamps; that committed state is the golden
this function reproduces.

Grid doctrine (owner ruling 2026-11-15): driver and seed values convert at this
boundary by dec() (the exact Decimal of the decimal repr); the v1 quantise
points emit through book()/unbook() - the integer count of 10^-dp units,
half-even, with the dimension and scale cited at every call - and every count,
stage number and rack figure runs as a native integer. Dimensionless constants
port as integer scaled pairs with the scale in the name (the 24 h day, the
86400 s day, the 1000 W/kW ladder, the +100 mm bed pitch margin, the three-bed
train). No float literals; the lint holds this.

The books that stay v1 float books by necessity, documented here: the whole
params.design block. The reference writer stores its solve dict UNROUNDED
(json round-trip of raw doubles) and the chains behind it are transcendental in
float space (the API618 stage search on rr**x, the isentropic works, the
reverse-Brayton expander book, the cube-root bed diameter on pi). Those books
reproduce the committed repr exactly through a float replica of the v1
expression over the same inputs (no literals; the floats come from the exact
boundary books by flo(), and the float-lane constants enter as the decimal
strings of the v1 literals). Quantisation at the stage's own points - the
continuous kW book at 4 dp, the SF feed value, the skid extents at 1 dp, the
whole-mm vessel books - goes through book()/unbook(), whose float path converts
through the exact binary value (Fraction), so it is Python round()'s own tie
rule and reproduces the v1 round() book for book.

Seed reads (prior-family fields, recorded): the feed rates on IA-NOX-CO2 and
IA-NOX-N2 are the NOX_SCRUB family's committed books (read `value or 0`, the
v1 guard); the process-space pressure is the site profile's atmosphere group
(shell interior where the profile states one, else the external atmosphere -
A-M-401, the v1 SITE.p_process_Pa read).

Disposition of the chains around this family (the strangler bridge):
- docs-authority/sizing/COLD_BOX.md (AQS-DUTY-069) is the renderer wave's:
  the doc consumed the design books feed_N2_kg_d, feed_CO2_kg_d, x_CO2,
  sorbent_kg_per_bed, bed_D_mm, bed_L_mm, regen_kW, blower_kW, co2_comp_kW,
  co2_chill_kW, getter_kW, total_kW, comp_stages, comp_ratio_per_stage,
  comp_T_out_C and expander_backup (cold_kW, T_out_C, loop_kg_d, shaft_kW,
  net_kW, COP, chiller_kW), plus the cb_cycle_h driver read fresh from
  drivers.json, and the DN round of bed_D_mm at its table row.
- The EXPANDER idle bookkeeping (node continuous_kw 0, SF/SQ feed values 0, the
  IA-EXP-IN/IA-EXP-OUT loop-edge zero rates and notes) applies only where the
  stage's objects exist: EXPANDER left the graph (Q-010 closed by the owner -
  the redundancy rule moved into params.design.expander_backup, A-M-186) and
  the loop edges and SQ-CRYO_ASU died with Rev AC. The committed seed carries
  none of them, so the guards record nothing; a seed that carries one gets the
  v1 book.
- SF-CRYO_ASU is a value-only update: the R11 Rev AC feed note belongs to the
  RSZ/restoration writers, so the seed rate dict passes through with only the
  value replaced.

The v1 machinery (disk write-back, the doc render, the stdout dump) does not
migrate: assignment replaces the field and its provenance in full. A solve
without the driver payload records nothing, so the bridge solve and the check
stay byte-faithful to the seed.
"""
import math
from decimal import Decimal, ROUND_HALF_EVEN
from fractions import Fraction

from flow_graph.v2.registry import fn

STAGE = 'cold_box'                                             # ledger row sizing_cold_box, provenance stage
TAG = 'X-MFG-33 (A-M-175, AQS-DUTY-069)'
CB = 'CRYO.cold-box-asu-recovery-train.cold-box.CRYO_ASU.'     # U4b: sizing literals single-sourced from drivers.json (A-M-175/186)
DAY_S = Fraction(86400)                                        # s, the transport book's day
DAY_H = Fraction(24)                                           # h, the cycle book's day
K_W = Fraction(1000)                                           # W per kW
MGG = Fraction(1000)                                           # mg per g (the kmol book)
BEDS = 3                                                       # one adsorbing, one regenerating, one standby
PITCH_MARGIN_MM = Fraction(100)                                # +100 mm bed pitch margin (the layout book)
MACH_X0_MM = Decimal('1700.0')                                 # purchased machinery row x0 (W12 layout)
MACH_LEN_MM = Decimal('740.0')                                 # purchased machinery row length
SKID_W_MM = Decimal('560.0')                                   # skid width
HOSE_LAP_MM = Decimal('32.0')                                  # -Y hose-makeup lap
SKID_MARGIN_MM = Decimal('20.0')                               # skid margin
TOP_DATUM_MM = Decimal('2000.0')                               # issued z vent datum, the assembly top
F0 = Decimal('0.0')                                            # the v1 zero book (float lane)


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
    """Value-only update on an existing rate (the note-owner books: the SF
    feeds carry other writers' notes)."""
    seed = dict(b.edges[sid]['rate'])
    seed['value'] = value
    b.set_edge_rate(sid, seed, _prov(basis, ref))


def _edge_field(b, sid, path, value, basis, ref=None):
    """An edge field beyond 'rate' (params.*, rate.note): the same overlay."""
    b.computed[('edge', sid, path)] = (value, _prov(basis, ref))


def _p_process_pa(inputs):
    """SITE.p_process_Pa (A-M-401): the shell interior where the profile states
    one, else the external atmosphere. Pure read of the site-profile payload."""
    prof = inputs.get('site_profile')
    atm = ((prof or {}).get('groups') or {}).get('atmosphere', {}).get('entries') or {}
    shell = atm.get('shell_pressure_kPa')
    if isinstance(shell, dict) and 'value' in shell:
        return float(dec(shell['value']) * 1000)
    ext = atm.get('pressure_Pa')
    if isinstance(ext, dict) and 'value' in ext:
        return float(dec(ext['value']))
    return float(dec('101325'))                            # the baseline standard atmosphere


def _seed_rate(b, sid):
    """The committed kg/d book of a feed edge, `value or 0` (the v1 guard)."""
    val = (b.edges[sid]['rate'] or {}).get('value')
    return flo(dec(val)) if isinstance(val, (int, float)) else flo(F0)


def design(b, drv, inputs):
    """The v1 cold_box.design() port on the recorded boundary: the exact
    Decimal boundary for the drivers and seed books, the documented float
    replica for the v1 transcendental chains, integers for every count and
    rack figure. Returns the design dict in the v1 key order."""
    def v(k):
        return drv[k]['value'] if k in drv else drv[CB + k]['value']

    co2 = _seed_rate(b, 'IA-NOX-CO2')
    n2 = _seed_rate(b, 'IA-NOX-N2')
    n = co2 / flo('44.01')                                 # kmol/d CO2
    x_co2 = n / (n + n2 / flo('28.013'))
    per_cycle = n * flo(dec(v('cb_cycle_h'))) / float(DAY_H) * float(MGG)
    m_sorb = per_cycle / flo(dec(v('cb_13x_CO2_mol_kg')))  # kg per bed
    d_t = flo(dec(v('cb_regen_C'))) - flo(dec(v(CB + 'tsa_regen_start_C')))
    cyc = float(DAY_H) / flo(dec(v('cb_cycle_h')))
    q_cyc = m_sorb * (1 + flo(dec(v('cb_steel_to_sorbent'))) * flo(dec(v(CB + 'steel_cp_kJ_kgK')))
                      / flo(dec(v('cb_cp_sorbent_kJ_kgK')))) * flo(dec(v('cb_cp_sorbent_kJ_kgK'))) * d_t \
        + per_cycle * flo(dec(v('cb_dH_ads_kJ_mol')))      # kJ; steel cp driver
    p_regen = q_cyc * cyc / float(DAY_S) * (1 + flo(dec(v('cb_regen_loss_frac'))))
    p_pa = _p_process_pa(inputs)
    q = (n + n2 / flo('28.013')) * float(MGG) / float(DAY_S) * flo('8.314') \
        * flo(dec(v(CB + 'feed_T_K'))) / p_pa              # m3/s feed at 35 C in the process space (A-M-401)
    p_blow = q * flo(dec(v('cb_bed_dP_kPa'))) * float(K_W) / flo(dec(v(CB + 'blower_eta'))) / float(K_W)
    k = flo(dec(v(CB + 'co2_k')))
    x = (k - 1) / k                                        # the API618 stage search: fewest equal-ratio
    ns = 1                                                 # stages within the 150 C discharge limit
    while flo(dec(v(CB + 'feed_T_K'))) * (1 + ((flo(dec(v('cb_co2_store_bar'))) / flo('1.0')) ** (x / ns) - 1)
                                          / flo(dec(v(CB + 'comp_eta')))) - flo('273.15') > flo(dec(v('cb_T_out_max_C'))):
        ns += 1
    rr = (flo(dec(v('cb_co2_store_bar'))) / flo('1.0')) ** (1 / ns)
    w = ns / x * flo('8.314') / flo('0.04401') * flo(dec(v(CB + 'feed_T_K'))) * (rr ** x - 1) / flo(dec(v(CB + 'comp_eta')))
    t_st = flo(dec(v(CB + 'feed_T_K'))) * (1 + (rr ** x - 1) / flo(dec(v(CB + 'comp_eta')))) - flo('273.15')
    p_comp = co2 / float(DAY_S) * w / flo(dec(v(CB + 'motor_eta'))) / float(K_W)
    q_cond = flo(dec(v(CB + 'co2_liq_cp_kJ_kgK'))) * flo(dec(v(CB + 'co2_subcool_K'))) + flo(dec(v('cb_co2_latent_kJ_kg')))
    p_chill = co2 / float(DAY_S) * q_cond / flo(dec(v('cb_chiller_COP')))
    p_get = flo(dec(v('cb_getter_W'))) / float(K_W)
    rho_b = flo(dec(v(CB + 'sorbent_bulk_rho_kg_m3')))
    v_b = m_sorb / rho_b
    d_bed = (4 * v_b / (math.pi * flo(dec(v(CB + 'bed_LD'))))) ** (1 / 3)
    # bed L/D driver, 13X bulk 650 kg/m3 (A-M-175); the cube root as the
    # integer pair 1/3 in float space
    k2 = flo(dec(v(CB + 'exp_n2_k')))
    xe = (k2 - 1) / k2
    t_in = flo(dec(v('exp_T_in_K')))
    t_out = t_in * (1 - flo(dec(v('exp_eta_s'))) * (1 - flo(dec(v('exp_pr'))) ** -xe))
    q_cold = co2 / float(DAY_S) * q_cond
    dq = flo(dec(v(CB + 'exp_n2_cp_kJ_kgK'))) * (flo(dec(v(CB + 'exp_warm_T_K'))) - t_out)
    m_loop = q_cold / dq                                   # kg/s, warms to -25 C at the condenser
    w_c = flo(dec(v(CB + 'exp_n2_cp_kJ_kgK'))) * t_in * (flo(dec(v('exp_pr'))) ** xe - 1) / flo(dec(v('exp_eta_comp')))
    w_e = flo(dec(v(CB + 'exp_n2_cp_kJ_kgK'))) * (t_in - t_out)
    p_loop = m_loop * (w_c - w_e)
    exp_bk = dict(cold_kW=q_cold, T_out_C=t_out - flo('273.15'), loop_kg_d=m_loop * float(DAY_S),
                  shaft_kW=m_loop * w_e, net_kW=p_loop, COP=q_cold / p_loop,
                  chiller_kW=q_cold / flo(dec(v('cb_chiller_COP'))))
    tot = p_regen + p_blow + p_comp + p_chill + p_get
    bed_d = d_bed * float(K_W)
    r = dict(feed_N2_kg_d=n2, feed_CO2_kg_d=co2, x_CO2=x_co2, CO2_mol_per_cycle=per_cycle,
             sorbent_kg_per_bed=m_sorb, beds=BEDS, bed_D_mm=bed_d,
             bed_L_mm=flo(dec(v(CB + 'bed_LD'))) * d_bed * float(K_W),
             regen_kW=p_regen, blower_kW=p_blow, co2_comp_kW=p_comp, co2_chill_kW=p_chill, getter_kW=p_get,
             total_kW=tot, comp_stages=ns, comp_ratio_per_stage=rr, comp_T_out_C=t_st, expander_backup=exp_bk)
    # The modelled skid extents (2026-11-08 reservation adoption, registered
    # study layout, W12): the beds zone (one pitch per bed from the first axis
    # at half pitch) beside the purchased machinery row, with the 20 mm skid
    # margin; the basin width plus the -Y hose-makeup lap; the issued z 2000
    # vent datum as the assembly top. These are the constants the builder lays
    # out to.
    bed_pitch = bed_d + float(PITCH_MARGIN_MM)
    bed_x_end = bed_pitch / 2 + (BEDS - 1) * bed_pitch + bed_d / 2
    mach_x0, mach_len = float(MACH_X0_MM), float(MACH_LEN_MM)
    skid_w, hose_lap = float(SKID_W_MM), float(HOSE_LAP_MM)
    skid_l = unbook(book(max(bed_x_end, mach_x0 + mach_len) + float(SKID_MARGIN_MM), 1,
                         'length mm: the skid length book at 1 dp (W12 layout)'), 1)
    r.update(bed_pitch_mm=unbook(book(bed_pitch, 1, 'length mm: the bed pitch book at 1 dp'), 1),
             machinery_row_x0_mm=mach_x0, machinery_row_len_mm=mach_len, skid_w_mm=skid_w,
             hose_lap_mm=hose_lap, skid_l_mm=skid_l, top_datum_mm=float(TOP_DATUM_MM),
             size_mm=[skid_l, unbook(book(skid_w + hose_lap, 1, 'length mm: the skid width book at 1 dp'), 1),
                      float(TOP_DATUM_MM)])
    return r


@fn('cold_box_asu', 'X-MFG-33 in-house CRYO_ASU separation train (AQS-DUTY-069; A-M-175, A-M-186): 13X TSA '
    'beds [NASA_CDRA2015], the CO2 compressor staged to the API618 150 C discharge limit (found by '
    'AQS-SAF-004), the -20 C condenser [NIST_WEBBOOK] and the reverse-Brayton expander backup (Q-010 closed)')
def cold_box_asu(b, inputs):
    drv = inputs.get('drivers')
    if drv is None or 'CRYO_ASU' not in b.nodes:
        return                                             # bridge contract: no drivers, no stamps
    r = design(b, drv, inputs)
    basis = ('X-MFG-33 CRYO_ASU separation train sized from the graph duty (AQS-DUTY-069; A-M-175; expander '
             'backup A-M-186, Q-010): 13X TSA regeneration, staged CO2 compressor to the API618 discharge '
             'limit, condenser chiller, Ar getter; no cryogenic column (no air intake)')
    note = (f"{TAG}: 13X TSA regeneration {r['regen_kW']:.2f} + blower {r['blower_kW']:.3f} + CO2 compressor "
            f"{r['co2_comp_kW']:.3f} + condenser chiller {r['co2_chill_kW']:.3f} + Ar getter {r['getter_kW']:.2f} kW; "
            'no cryogenic column (no air intake).')
    _set(b, 'CRYO_ASU', 'continuous_kw', {
        'value': unbook(book(r['total_kW'], 4, 'power kW: the continuous book at 4 dp'), 4),
        'unit': 'kW', 'status': 'study', 'note': note}, basis, 'A-M-175')
    _set(b, 'CRYO_ASU', 'internals',
         '3 x 13X TSA beds, CO2 two-stage compressor and condenser, heated Ar getter; noble-gas inventories pass through',
         basis, 'A-M-175')
    _set(b, 'CRYO_ASU', 'params.internals',
         '3 x 13X TSA beds, CO2 two-stage compressor and condenser, heated Ar getter; noble-gas inventories pass through',
         basis, 'A-M-175')
    design_book = dict(r)
    design_book['H_mm'] = book(r['bed_L_mm'], 0, 'length mm: the vessel height book, whole mm')
    design_book['D_mm'] = book(r['bed_D_mm'], 0, 'length mm: the vessel diameter book, whole mm')
    _set(b, 'CRYO_ASU', 'params.design', design_book, basis, 'A-M-175')
    _set(b, 'CRYO_ASU', 'params.size_mm', r['size_mm'], basis, 'A-M-175')
    _set(b, 'CRYO_ASU', 'params.size_basis',
         f'{TAG} skid extents: the beds zone plus the purchased '
         'machinery row with the 20 mm skid margin; the width '
         'carries the -Y hose-makeup lap; the z top is the issued '
         'vent datum (registered study layout, W12)', basis, 'A-M-175')
    if 'SF-CRYO_ASU' in b.edges:                           # R11 Rev AC regen: SQ-* heat edges died with HEAT_SINK
        _edge_value(b, 'SF-CRYO_ASU',
                    unbook(book(r['total_kW'], 4, 'power kW: the feed book at 4 dp'), 4), basis, 'A-M-175')
    for sid in ('IA-EXP-IN', 'IA-EXP-OUT'):                # R11 Rev AC regen: loop edges may be absent
        if sid in b.edges:
            _edge_value(b, sid, flo(F0), basis, 'A-M-186')
            _edge_field(b, sid, 'rate.note',
                        f'{TAG}: no refrigeration duty; loop idle in normal operation; standby backup (Q-010 closed)',
                        basis, 'A-M-186')
    if 'EXPANDER' in b.nodes:                              # R11 Rev AC regen: EXPANDER left the graph (Q-010)
        _set(b, 'EXPANDER', 'continuous_kw.value', flo(F0), basis, 'A-M-186')
        _set(b, 'EXPANDER', 'continuous_kw.note',
             f'{TAG}: idle, no duty; retirement is Q-010', basis, 'A-M-186')
        for sid in ('SF-EXPANDER', 'SQ-EXPANDER'):
            if sid in b.edges:
                _edge_value(b, sid, flo(F0), basis, 'A-M-186')

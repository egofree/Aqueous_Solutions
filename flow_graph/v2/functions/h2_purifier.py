"""The X-MFG-39 H2 purifier bed sizing family (family migration; reference
writer flow_graph/param/h2_purifier.py `--write`, ledger row `sizing_h2_purifier`,
section B, MIXED: split sizing -> this function, the sizing doc -> the renderer
lane). The H2_DRYER bed train: the deoxo bed (2 H2 + O2 -> 2 H2O over Pd/Al2O3,
volume from the space velocity), the chloride guard (promoted alumina, charged
for the change-out interval) and the two-bed TSA dryer (4A/13X working capacity
x the cycle load x the margin), each bed duplicated so one is on line while the
other regenerates or is changed; regeneration heat = sieve + steel sensible +
water desorption per cycle averaged over the cycle, plus the ASTM_C680
insulated-cylinder loss while hot; electric load at the heater efficiency
(A-M-168). The committed graph carries every field the v1 stage stamps; that
committed state is the golden this module reproduces.

Grid doctrine (owner ruling 2026-11-15): driver and seed values cross the
boundary through dec() (the exact Decimal of the decimal repr); the integer
books (bed lengths, counts, the envelope mm) are half-even integer books on
the declared length grid, and the kW books quantise half-even at 4 dp - the
decimals the v1 schema stores, Python round()'s tie rule. Dimensionless and
physical constants port as integer scaled pairs or exact decimal strings:
the molar mass 2.016 g/mol H2, the molar volume 0.022414 Nm3/mol, water 18.015,
HCl 36.461, the ppm book 1/1000000. No float literals.

THE RAW-FLOAT DESIGN BOOKS. v1 stored params.design as the unrounded float
chain (a json round-trip, no blanket rounding), and the v1 writers' own
rounding (kW at 4 dp, L_mm to the integer mm) ran on that chain. An
exact-Decimal book floats a ulp away from the committed repr and would read as
an edit on every raw field, so - the foundry-family precedent
(flow_graph/v2/functions/foundry.py, module docstring) - the stored design
numerics stay v1 float books: float replicas of the reference writer's
expressions over the same boundary inputs, constants entering as floats of
their exact decimals by fl(). The exact-Decimal audit books of the same chain
(the mol book, the water and sieve loads, the regeneration energy) live in the
family test as independent re-derivations.

Disposition of the chains around this family (the strangler bridge):
- The sizing doc (docs-authority/sizing/H2_PURIFIER_BEDS.md, AQS-DUTY-066) is
  renderer-lane work. It consumes, from the fields this function stamps:
  H2_kg_d, Nm3_h, O2_mol_d, water_kg_d, HCl_kg_d, guard_kg, sieve_kg, the
  per-bed beds rows (V_L, tube, L_mm, count), regen_W, T_C, insulation_mm,
  loss_W and kW.
- Topology is builder work and the committed seed carries it, so this function
  asserts instead of writes: the IA-H2P-H2O condensate edge (created by v1 with
  composition {'water': 1.0}, sectors GAS -> WTR) exists with to_unit_id
  VCD_TRAIN; SQ-H2_DRYER and S49P do not exist on the committed seed - the v1
  guards skip the SQ re-rate and the S49P/S52 fuel-cell water rebookkeeping is
  dead code there (recorded, not ported).
- The IA-H2P-H2O rate book (feed-water mass, X-PAR-15) is a graph stamp: the
  feed water is the seed S49 rate times its water composition, which the
  committed seed does not carry, so the book is 0.0 kg/d (the v1 read-back).
- The v1 note literal '0.7' (the heater efficiency in the continuous_kw note)
  now reads the h2p_regen_heater_eta driver - the same bytes on the committed
  drivers, and the note no longer goes stale on a driver change.
A solve without the driver payload records nothing, so the bridge solve and the
check stay byte-faithful to the seed.
"""
import math
from decimal import Decimal

from flow_graph.v2.registry import fn

STAGES = 'sizing_h2_purifier'                                  # ledger row, section B
TAG = 'X-MFG-39 (A-M-168)'
REF = 'A-M-168'
HP = 'GAS.scrubbing-headers-train.gas-headers.H2_DRYER.'       # the H2 dryer sizing driver prefix (A-M-168)
M_H2, M_H2O, M_HCL = '2.016', '18.015', '36.461'               # g/mol, exact decimals
NM3_PER_MOL = '0.022414'                                       # Nm3/mol at 0 C (A-M-168 book)
THK = (13, 25, 38, 50, 65, 75, 100, 125, 150, 200)             # the ASTM_C680 mineral-wool ladder, mm
DN_SMALL, DN_LARGE = 25, 50                                    # the tube DN pair of the v1 bed geometry


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


def qi(x):
    """round(x) as v1 wrote it: half-even to an integer (the length book)."""
    return int(round(fl(x)))


def _prov(basis, ref=None):
    from flow_graph.v2.model import Prov
    return Prov(STAGES, basis, ref)


def _set(b, uid, path, value, basis, ref=None):
    b.set_node_field(uid, path, value, _prov(basis, ref))


def _re_rate(b, sid, mutate, basis, ref=None):
    """Re-rate a seed edge book in place (the v1 `E[sid]['rate'][...] = ...`
    writes): the seed book copied, the named fields replaced - the seed note,
    unit and status the v1 writer preserved stay."""
    book = dict(b.edges[sid]['rate'])
    mutate(book)
    b.set_edge_rate(sid, book, _prov(basis, ref))


def insulated_cylinder(T_C, D_mm, L_m, thk=THK):
    """sizing/heat.py insulated_cylinder [ASTM_C680, ASTM_C1055, A-M-158]: the
    smallest standard thickness with the surface at or under 50 C; k =
    0.037 + 0.00017 T_mean, ambient 25 C, h 10 W/m2K, heads and nozzles at
    1.3 (the reference writer's own float book). Returns (thk_mm, loss_W)."""
    r1 = D_mm / 2000
    for t in thk:
        r2 = r1 + t / 1000
        k = fl('0.037') + fl('0.00017') * (T_C + 50) / 2
        loss_flux = (T_C - 25) / (math.log(r2 / r1) / (2 * math.pi * k) + 1 / (2 * math.pi * r2 * 10))
        surface = 25 + loss_flux / (2 * math.pi * r2 * 10)
        if surface <= 50:
            break
    return t, loss_flux * L_m * fl('1.3')


def mol_book(h2_kg_d):
    """The exact mol book of the feed (audit): kg/d H2 over 2.016 g/mol x 1000
    mol/d - the integer-scaled-pair form of the v1 float chain."""
    return dec(h2_kg_d) / dec(M_H2) * 1000


@fn('h2_purifier_beds', 'X-MFG-39 H2 purifier beds (A-M-168): deoxo from the GHSV driver, chloride guard on the '
    'change-out interval, two-bed TSA at the working capacity x cycle x margin, regeneration heat + ASTM_C680 loss; '
    'every bed duplicated (redundancy rule)')
def h2_purifier_beds(b, inputs):
    drv = inputs.get('drivers')
    if drv is None:
        return                                                  # the bridge contract: no payload, no stamps
    feed_sid = 'IA-HDR-H2-02' if 'IA-HDR-H2-02' in b.edges else 'S49'
    if feed_sid not in b.edges:
        return                                                  # no feed on the seed: the train cannot be sized
    U = 'H2_DRYER' if 'H2_DRYER' in b.nodes else 'H2_PURIFIER'  # the R11 Rev AC node rename
    if U not in b.nodes:
        return
    assert 'IA-H2P-H2O' in b.edges and b.edges['IA-H2P-H2O']['to_unit_id'] == 'VCD_TRAIN', \
        'h2_purifier_beds: the seed lacks the X-PAR-15 condensate edge to VCD_TRAIN (builder topology)'
    assert 'SQ-' + U not in b.edges and 'S49P' not in b.edges, \
        'h2_purifier_beds: the seed carries topology the committed graph retired (SQ-*/S49P)'

    def dv_(k):
        return fl(drv[HP + k]['value'])                         # the driver as the v1 float

    def dvr(k):
        return drv[HP + k]['value']                             # the driver as written (int books stay int)

    feed = b.edges[feed_sid]
    comp = feed.get('composition') or {}
    rate_f = fl(feed['rate']['value'])
    h2 = rate_f * fl(comp.get('H2', 1))                         # kg/d H2 at the seed composition
    n = h2 / fl(M_H2) * 1000                                    # mol/d, the mol book
    Nm3_h = n * fl(NM3_PER_MOL) / 24                            # Nm3/h
    ppm = fl(dec(1).scaleb(-6))                                 # the ppm book 1/1000000
    o2 = n * fl(drv['h2p_o2_ppmv']['value']) * ppm              # mol/d O2 at the inlet spec
    w_deoxo = 2 * o2 * fl(M_H2O) / 1000                         # kg/d, 2 H2O per O2
    V_deoxo = Nm3_h / fl(drv['h2p_deoxo_ghsv_h']['value']) * 1000   # L at the space velocity
    hcl = n * fl(drv['h2p_hcl_ppmv']['value']) * ppm * fl(M_HCL) / 1000   # kg/d HCl at the inlet spec
    m_guard = hcl * fl(drv['h2p_guard_days']['value']) / fl(drv['h2p_guard_cap']['value'])  # kg media
    w = rate_f * fl(comp.get('water', 0)) + w_deoxo             # kg/d water: feed share + deoxo water
    cycle_h = fl(drv['h2p_cycle_h']['value'])
    m_sieve = w * cycle_h / 24 / fl(drv['h2p_sieve_work_cap']['value']) * fl(drv['h2p_bed_margin']['value'])
    V_sieve = m_sieve / dv_('h2p_sieve_bulk_kg_L')              # L at 0.7 kg/L bulk
    beds_in = {'deoxo': V_deoxo, 'guard': m_guard / dv_('h2p_guard_bulk_kg_L'), 'TSA': V_sieve}
    geo = {}
    for bed, V_book in beds_in.items():
        V = max(V_book, dv_('h2p_bed_min_L'))
        small = V < dv_('h2p_tube_vol_switch_L')
        D = dv_('h2p_tube_OD_small_mm') if small else dv_('h2p_tube_OD_large_mm')
        t_wall = dv_('h2p_wall_small_mm') if D < 40 else dv_('h2p_wall_large_mm')
        idm = D - 2 * t_wall                                    # mm, inside diameter
        L = max(dvr('h2p_bed_min_L_mm'), V / 1000 / (math.pi * (idm / 1000) ** 2 / 4) * 1000)
        geo[bed] = dict(V_L=V, tube=f'DN{DN_SMALL if D < 40 else DN_LARGE} Sch 40 316L',
                        L_mm=qi(L), count=dvr('h2p_bed_count'))
    Lt = geo['TSA']['L_mm'] / 1000                              # m, the TSA bed length book
    od_tsa = dv_('h2p_tube_OD_large_mm') if 'DN50' in geo['TSA']['tube'] else dv_('h2p_tube_OD_small_mm')
    steel = math.pi * od_tsa / 1000 * Lt * dv_('h2p_steel_wall_m') * dvr('h2p_steel_rho_kg_m3')  # kg
    T_regen, ref_T = fl(drv['h2p_regen_T_C']['value']), dvr('h2p_sensible_ref_T_C')
    q_kJ = (m_sieve * dv_('h2p_sieve_cp_kJ_kgK') * (T_regen - ref_T)
            + steel * dv_('h2p_steel_cp_kJ_kgK') * (T_regen - ref_T)) / 1000 \
        + w * cycle_h / 24 * dvr('h2p_water_desorb_kJ_kg')      # kJ per regeneration
    regen_W = q_kJ * 1000 / 86400 * (24 / cycle_h)              # W average over the cycle
    ins_mm, loss_W = insulated_cylinder(T_regen, dv_('h2p_tube_OD_large_mm'), Lt)
    eta, hot_frac = dv_('h2p_regen_heater_eta'), dv_('h2p_loss_hot_frac')
    kw = q((regen_W / eta + loss_W * hot_frac) / 1000, 4)       # the kW book, 4 dp
    basis = f'X-MFG-39 H2 purifier bed train (A-M-168); feed {feed_sid} on the seed; sizing drivers h2p_* and ' \
            f'{HP}* (flow_graph/param/h2_purifier.py port)'
    bed_basis = 'bed duplicated, one on line (redundancy rule); DN by the 0.25 L tube switch, length on the ' \
                '300 mm minimum (A-M-168)'
    _set(b, U, 'params.design.H2_kg_d', h2, basis + '; H2 at the seed composition', REF)
    _set(b, U, 'params.design.Nm3_h', Nm3_h, basis + '; the mol book over the 0.022414 Nm3/mol volume', REF)
    _set(b, U, 'params.design.O2_mol_d', o2, basis + '; O2 at driver h2p_o2_ppmv', REF)
    _set(b, U, 'params.design.water_kg_d', w, basis + '; 2 H2O per O2 plus the seed feed-water share (nil on the '
         'committed seed composition)', REF)
    _set(b, U, 'params.design.HCl_kg_d', hcl, basis + '; HCl at driver h2p_hcl_ppmv', REF)
    _set(b, U, 'params.design.guard_kg', m_guard, basis + '; h2p_guard_days / h2p_guard_cap charge', REF)
    _set(b, U, 'params.design.sieve_kg', m_sieve, basis + '; h2p_cycle_h/24 / h2p_sieve_work_cap x h2p_bed_margin', REF)
    _set(b, U, 'params.design.beds', geo, basis + '; ' + bed_basis, REF)
    _set(b, U, 'params.design.regen_W', regen_W, basis + '; sieve + steel sensible + water desorption per cycle, '
         'averaged over the cycle', REF)
    _set(b, U, 'params.design.loss_W', loss_W, basis + '; ASTM_C680 insulated cylinder (A-M-158) while hot', REF)
    _set(b, U, 'params.design.insulation_mm', ins_mm, basis + '; smallest standard thickness, surface at or under '
         '50 C (ASTM_C1055)', REF)
    _set(b, U, 'params.design.kW', kw, basis + '; (regen / h2p_regen_heater_eta + half the insulated loss) / 1000, '
         '4 dp book', REF)
    _set(b, U, 'params.design.D_mm', dvr('h2p_envelope_D_mm'), basis + '; envelope driver', REF)
    _set(b, U, 'params.design.H_mm', max(g['L_mm'] for g in geo.values()) + dvr('h2p_envelope_top_mm'),
         basis + '; tallest bed + the envelope top allowance', REF)
    _set(b, U, 'params.design.T_C', T_regen, basis + '; regeneration temperature driver h2p_regen_T_C', REF)
    _set(b, U, 'params.design.wall_mm', dv_('h2p_wall_large_mm'), basis + '; DN50 Sch 40 wall driver', REF)
    _set(b, U, 'continuous_kw.value', kw, basis, REF)
    _set(b, U, 'continuous_kw.note',
         f'{TAG}: TSA regeneration {regen_W:.1f} W / {eta:g} + half the insulated loss.', basis, REF)
    seed_ckw = b.nodes[U].get('continuous_kw') or {}
    if 'status' not in seed_ckw:
        _set(b, U, 'continuous_kw.status', 'study', basis, REF)
    if 'unit' not in seed_ckw:
        _set(b, U, 'continuous_kw.unit', 'kW', basis, REF)
    _set(b, U, 'params.size_mm',
         [dvr('h2p_envelope_L_mm'), dvr('h2p_envelope_W_mm'),
          max(g['L_mm'] for g in geo.values()) + dvr('h2p_envelope_top_mm') + dvr('h2p_envelope_head_mm')],
         basis + '; envelope L x W x H, integer mm on the declared length grid', REF)
    if 'SF-' + U in b.edges:
        _re_rate(b, 'SF-' + U, lambda book: book.update(value=kw),
                 basis + '; the feed edge re-rated to the node book (the seed note stands)', REF)
    wf = fl(dec(b.edges['S49']['rate']['value'] or 0)
            * dec((b.edges['S49'].get('composition') or {}).get('water', 0))) \
        if 'S49' in b.edges else fl(0)
    _re_rate(b, 'IA-H2P-H2O', lambda book: book.update(value=q(wf, 6), note=(
        'X-PAR-15: feed water (S49 composition) removed by the TSA, condensed from the regeneration purge '
        '(A-M-168).')), basis + '; X-PAR-15: the feed water leaves on the TSA regeneration purge (A-M-168)', REF)

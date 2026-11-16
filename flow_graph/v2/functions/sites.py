"""The site/locale writer family (family migration; reference writers
flow_graph/param/scaling.py, flow_graph/param/portfolio.py,
flow_graph/param/site_units.py and flow_graph/param/lake_boehmer.py; ledger
rows `site_scaling`, `site_power`, `doc_site_units` (the placement/sizing
half; the SITE_UNITS.md render is the renderer half) and `lake_boehmer_design`).

Three chains port here:

- `site_scale` resolves the profile's scaling actions against the seed into
  the per-unit plan book (status, factor, count, replacement, import_path)
  the locale solve applies - the v1 `scaling.resolve()` half. In v1 the plan
  is consumed by the redundancy census (source count x the duplicate count)
  and by validation; no v1 writer multiplies a rate by the size factor, so
  the factor lands in the book (scale_rate() is the exact application any
  design consumer performs), and nothing is invented.
- `site_power_placement` collects the placeholder units the locale's scaling
  replacements and the portfolio's primary/backup sources name, and stamps
  `params.site_placement` with the sizing the profile produces - the v1
  `site_units.placements()/apply()` half. The sizer dispatch is a registry
  keyed by the unit id the profile names (FSP_40K, MMRTG, RAD_PANEL, LIO_BAT,
  generic design record): the portfolio source names decide, never a locale
  id. The fission and RTG counts are ceil rules on the portfolio worst-stretch
  balance and the backup-fuel critical list (F-20261113-01, the Q-024 revision:
  designed sources carry their completed study record,
  `power_portfolio.dust_stretch_design`).
- `lake_ed_train` sizes the lake-restoration electrodialysis train: the
  Faraday specific-energy rule per stage, the module counts (duty ceil + the
  N+1 spare), the container counts, the D-PV rule nameplate and the battery
  store. The audit's locale-name guard promotion lives here: v1 gated its
  write on the selected site id (`if sid != 'lake_boehmer'`); the v2 function
  is data-conditioned - it fires only when the seed carries the ED train
  units and the driver payload carries the design set. No locale id appears
  in this module (test_sites.py holds that with an AST check).

Golden provenance (enumerated in test_sites.py):
- the RAD_PANEL sizing book equals the committed locale stamp in
  sites/mars/flow_graph/plant_flow_graph.json (params.site_placement);
- the LIO_BAT stretch book rule equals the committed locale stamp in
  sites/leo/flow_graph/plant_flow_graph.json (the stamp's own recorded
  demand base; that locale file's need_kw has since moved - deviation
  enumerated in the test);
- the RTG count and carry reproduce the committed study record in the mars
  profile `power_portfolio.dust_stretch_design` (19 units on the 2.0 kW
  controls trickle, 2.09 kW_e carried) and the fission counts reproduce the
  ceil rule on the recorded demand books (the study's 2+1 at the PV-only
  balance, the finding's landed 7+1 on the locale demand base);
- the lake ED train books reproduce AQS-SITE-015 (SITE_BASIS_LAKE_BOEHMER.md,
  tables 5.1/5.2) and the reference writer's own pure compute() on the
  committed drivers. The baseline seed carries no lb_design stamps (the v1
  stage writes only inside its locale worktree and sites/lake_boehmer/ is
  not committed), so the documented books are the golden.

Grid doctrine (owner ruling 2026-11-15): driver and seed values arrive as v1
floats and are converted at this boundary by dec() (exact Decimal of the
decimal repr); arithmetic is exact Decimal; record fields are quantised
half-even (Python round()'s tie rule) at the decimals the v1 schema stores -
2 dp on the kW/kWh books, 3 dp on the radiator per-kW area, 1 dp on areas,
stage books and carries, 4 dp on the salt closure. Scale named at each call.
Physical constants port as exact Decimals: the CODATA2018 Faraday, the
Stefan-Boltzmann constant as an integer scaled pair, the kWh in joules, the
NaCl equivalent molar mass, the 24 h day and the 86400 s day. No float
literals. A solve without the profile or driver payload records nothing, so
the bridge solve and the check stay byte-faithful to the seed.
"""
from decimal import Decimal, ROUND_HALF_EVEN

from flow_graph.v2.registry import fn

STAGES = 'site'                                                # family tag in provenance rows
D0, D1 = Decimal(0), Decimal(1)
DAY = Decimal(24)                                              # h, the design-day book
SEC_DAY = Decimal(86400)                                       # s, the transport book's day
W_PER_KW = Decimal(1000)                                       # W per kW
MG_PER_G = Decimal(1000)                                       # mg per g
J_PER_KWH = Decimal('3600000')                                 # J per kWh (3.6e6)
DEC2, DEC1000 = Decimal(2), Decimal(1000)
F_FARADAY = Decimal('96485.33212')                             # C/mol, CODATA2018
NACL = Decimal('58.44')                                        # g/mol equivalent salt, NaCl basis (CRC)
SIGMA = Decimal(5670374419) / Decimal(10 ** 17)                # W/(m2 K4), CODATA2018 Stefan-Boltzmann
ACTIONS = ('size', 'duplicate', 'replace', 'eliminate')
REGISTER = 'AQS-SITE-013 (SITE_UNITS.md)'
LB_UNITS = ('LB_INTAKE', 'LB_DEGAS', 'LB_DEGAS_SCRUB', 'LB_SOFTEN', 'LB_ED1', 'LB_ED2',
            'LB_PROD_TANK', 'LB_PROD_OUTLET', 'LB_BRINE_RETURN', 'LB_CHEM_STORE')
LB = 'WTR.lake-boehmer.'
LB_KEYS = (LB + 'feed_m3_d', LB + 'feed_tds_g_L', LB + 'ed_recovery',
           LB + 'ed_stage1_product_tds_g_L', LB + 'product_tds_mg_L',
           LB + 'ed_cellpair_voltage_V', LB + 'ed_current_efficiency',
           LB + 'ed_current_density_A_m2', LB + 'ed_membrane_area_m2',
           LB + 'ed_spare_modules_per_stage', LB + 'ed_modules_per_container',
           LB + 'aux_intake_kWh_m3', LB + 'aux_degasser_kWh_m3',
           LB + 'aux_softening_kWh_m3', LB + 'aux_dosing_cip_kWh_m3',
           LB + 'battery_contingency_days', LB + 'bess_container_kWh',
           LB + 'utility_containers')
LB_POWER_KEYS = ('storage_round_trip', 'night_hours', 'pv_yield_kWh_kWp_d',
                 'pv_system_derate', 'pv_oversize_factor')
CRIT_K = 'ELEC.generation-train.BACKUP_GEN.'
SEC_BASIS = ('flow_graph/param/lake_boehmer.py module docstring (CODATA2018 F; '
             'STRATHMANN2004 U_cp, A-M-438; CAMPIONE2018 CE and j, A-M-439/440)')
NET_SALT = ('product and concentrate both return to the lake '
            '(owner decision, OPEN_QUESTIONS.md Q-037); only the scrubbed sulfide '
            'and the softening sludge leave, so the net lake salt removal is about zero')


def dec(value):
    """A v1 float/int/str -> exact Decimal at the boundary (decimal repr)."""
    return Decimal(str(value))


def q(x, dp):
    """Quantise an exact value to `dp` decimals, half-even - Python round()'s
    documented tie rule, the rounding the v1 writer used; scale named at the
    call. Returns the JSON float the schema stores."""
    f = float(Decimal(x).quantize(D1.scaleb(-dp), rounding=ROUND_HALF_EVEN))
    return float(0) if f == 0 else f                           # no signed zeros in the book


def ceil_ratio(a, b):
    """ceil(a / b) on exact positive Decimals: the v1 math.ceil of the
    quotient, integer-exact (no float quotient to wobble at a boundary)."""
    whole, rest = divmod(a, b)
    return int(whole + (1 if rest else 0))


def scale_rate(value, factor):
    """The size-factor application on a rate or design value: the exact
    product, quantised half-even at 4 dp (the kW rate book's decimals)."""
    return q(dec(value) * dec(factor), 4)


def _prov(basis, ref=None):
    from flow_graph.v2.model import Prov
    return Prov(STAGES, basis, ref)


# --- profile plumbing (the site.apply binding, pure data) -------------------

def bind_drivers(drivers, profile):
    """Replace every driver a profile entry binds with that entry (the v1
    site.apply port). A bind naming an unknown driver, or carrying units that
    differ from the driver's, fails loudly."""
    out = dict(drivers)
    for grp in (profile.get('groups') or {}).values():
        for e in (grp.get('entries') or {}).values():
            k = e.get('binds')
            if not k:
                continue
            if k not in out or out[k].get('units') != e.get('units'):
                raise ValueError(f'profile binds {k}: unknown driver or units differ')
            out[k] = {f: x for f, x in e.items() if f != 'binds'}
    return out


def entry_value(profile, key):
    """The value of a profile entry by 'group.entry' (the v1 site.val port)."""
    gk, ek = key.split('.', 1)
    grp = (profile.get('groups') or {}).get(gk) or {}
    ents = grp.get('entries') or {}
    if ek not in ents:
        raise KeyError(f'{key}: not a profile entry')
    return ents[ek]['value']


def site_drivers(inputs):
    """The site-bound driver view: the committed drivers overlaid with the
    profile bindings. None when either payload is absent (the bridge
    contract: a solve without the site payloads records nothing)."""
    drv, prof = inputs.get('drivers'), inputs.get('profile')
    if not isinstance(drv, dict) or not isinstance(prof, dict):
        return None
    return bind_drivers(drv, prof)


# --- the portfolio worst-stretch balance (the v1 portfolio.py physics) ------

def portfolio_of(profile):
    """The power_portfolio group's entry values by entry key."""
    ents = ((profile.get('groups') or {}).get('power_portfolio') or {}).get('entries') or {}
    return {k: e['value'] for k, e in ents.items()}


def stretch_hours(profile, pf):
    """The worst stretch h, from the hours entry the portfolio names."""
    return dec(entry_value(profile, pf['worst_stretch']['hours_entry']))


def phi(pf):
    """The share-weighted stretch output fraction of the primary sources."""
    total = D0
    for s in pf['sources']:
        if s['role'] == 'primary':
            total += dec(s['share']) * dec(s.get('stretch_output_frac', 0))
    return total


def mean_generation_per_kw(profile, eta):
    """G / P: mean primary generation per kW of average demand that closes the
    day through the worst stretch (storage round trip eta)."""
    pf = portfolio_of(profile)
    h, f = stretch_hours(profile, pf), phi(pf)
    return ((DAY - h) + h / eta) / (DAY - f * h + f * h / eta)


def pv_factor(profile, eta):
    """Multiplier on the reference PV balance: PV share times the worst-stretch
    correction. Exactly 1 for PV alone with no output in the stretch."""
    pf = portfolio_of(profile)
    pv = [s for s in pf['sources'] if s['role'] == 'primary' and s.get('kind') == 'pv']
    if not pv:
        return D0
    h, f = stretch_hours(profile, pf), phi(pf)
    return dec(pv[0]['share']) * (DAY / (DAY - f * h + f * h / eta))


def pv_kwp(p_kw, night_h, eta_rt, yield_kwh_kwp_d, derate):
    """The reference PV balance (sizing.power.pv_kWp): kWp = (direct + night
    energy over the round trip) / (yield x derate)."""
    return (p_kw * (DAY - night_h) + p_kw * night_h / eta_rt) / (yield_kwh_kwp_d * derate)


# --- seed reads (recorded where they enter a stamp) -------------------------

def need_kw(b):
    """The graph's converged electrical demand, mvs.electrical.need_kw (kW)."""
    v = ((b.data.get('mvs') or {}).get('electrical') or {}).get('need_kw') or {}
    x = v.get('value')
    return dec(x) if isinstance(x, (int, float)) else None


def demand_at_base_plate(b):
    """The demand a locale whose portfolio closes on a non-roof source books:
    the converged need minus the EXT_HALL roof extension, which exists to
    carry the roof PV (write_graph power generic path books the base plate,
    A-M-231/A-M-234)."""
    need = need_kw(b)
    if need is None:
        return None
    ext = b.nodes.get('EXT_HALL') or {}
    book = ext.get('continuous_kw')
    x = book.get('value') if isinstance(book, dict) else book
    if isinstance(x, (int, float)):
        need = need - dec(x)
    return need


def critical_list(b, drv):
    """The critical loads (kW) an outage carries, from the drivers and the
    seed (backup_fuel.critical_list port, AQS-ELEC-007)."""
    def r2(x):
        return dec(q(dec(x), 2))
    comp = ((b.nodes.get('CRYO_H2') or {}).get('params') or {}).get('compressor_design') or {}
    crit = {'HABITATION': dec(drv[CRIT_K + 'crit_HABITATION_kW']['value']),
            'CRYO_H2': r2(comp.get('P_peak_kW', dec('4.0')))}      # CRYO_H2 peak (AQS-DUTY-067)
    if 'CRYO_ASU' in b.nodes:
        crit['CRYO_ASU'] = r2(b.nodes['CRYO_ASU']['continuous_kw']['value'])   # AQS-DUTY-069 (A-M-238)
    if 'GROW_BED' in b.nodes:
        crit['GROW_BED'] = dec(drv[CRIT_K + 'crit_GROW_BED_kW']['value'])
    crit['controls and instruments'] = dec(drv[CRIT_K + 'crit_controls_kW']['value'])
    return crit


def dust_record(profile):
    """The profile's dust-stretch design record (the F-20261113-01 study the
    portfolio's designed sources cite)."""
    ents = ((profile.get('groups') or {}).get('power_portfolio') or {}).get('entries') or {}
    return ents.get('dust_stretch_design', {}).get('value') or {}


# --- the sizer registry (the v1 site_units SIZERS, keyed by unit id) --------

def _pv_source(pf):
    """(share, stretch_output_frac) of the primary PV entry; zeros when none."""
    share, frac = D0, D0
    for s in pf['sources']:
        if s['role'] == 'primary' and s.get('kind') == 'pv':
            share = dec(s['share'])
            frac = dec(s.get('stretch_output_frac', 0))
    return share, frac


def sizer_fsp_40k(b, drv, prof):
    """Dust-season fission sizing (F-20261113-01): through the dust stretch the
    PV share delivers only its stretch fraction of its mean rate, and the
    deficit is carried in NASA FSP 40 kW_e units with one installed spare
    (N+1). Inputs: the profile's worst-stretch balance and its dust-stretch
    design record; the unit rating is the node's published rating. No count
    is hard-coded."""
    node = b.nodes.get('FSP_40K') or {}
    unit_kw = (node.get('params') or {}).get('unit_kW_e')
    demand = demand_at_base_plate(b)
    if demand is None or unit_kw is None or drv is None:
        return {}
    pf = portfolio_of(prof)
    rec = dust_record(prof)
    frac = rec.get('pv_stretch_output_frac')
    if frac is None:                                   # fall back to the portfolio's PV entry
        _share, frac = _pv_source(pf)
        frac = dec(frac)
    share_pv, _f = _pv_source(pf)
    eta = dec(drv['storage_round_trip']['value'])
    mean_kw = mean_generation_per_kw(prof, eta) * demand
    pv_dust = dec(frac) * share_pv * mean_kw
    deficit = demand - pv_dust
    duty = ceil_ratio(deficit, dec(unit_kw)) if deficit > D0 else 0
    return {'demand_kW': q(demand, 2), 'mean_generation_kW': q(mean_kw, 2),
            'pv_share': float(share_pv), 'dust_pv_output_frac': float(dec(frac)),
            'pv_dust_output_kW': q(pv_dust, 2), 'dust_deficit_kW': q(deficit, 2),
            'unit_kW_e': float(dec(unit_kw)), 'count_duty': duty,
            'count_installed_n_plus_1': duty + 1,
            'installed_kW_e': q(dec(duty + 1) * dec(unit_kw), 1),
            'basis': 'AQS-PLAN-011 section 5.5 worst-stretch balance at the portfolio shares; dust fraction '
                     'from power_portfolio.dust_stretch_design (F-20261113-01); unit rating NASA_FSP; '
                     'one installed spare per the N+1 rule'}


def sizer_mmrtg(b, drv, prof):
    """RTG trickle sizing (F-20261113-01): the controls-and-instruments slice
    of the critical list (backup_fuel.critical_list, the single source) carried
    in NASA MMRTG 110 W_e units. The kW-class criticals stay on the fission
    base and the fuel cell; no count is hard-coded."""
    node = b.nodes.get('MMRTG') or {}
    unit_w = (node.get('params') or {}).get('unit_W_e')
    if unit_w is None or drv is None:
        return {}
    crit = critical_list(b, drv)
    trickle = crit.get('controls and instruments')
    if trickle is None:
        return {}
    count = ceil_ratio(trickle * W_PER_KW, dec(unit_w))
    return {'critical_list_kW': q(sum(crit.values(), D0), 2), 'controls_trickle_kW': q(trickle, 2),
            'unit_W_e': float(dec(unit_w)), 'count': count,
            'carries_W_e': q(dec(count) * dec(unit_w), 1),
            'basis': 'backup_fuel.critical_list controls slice (AQS-ELEC-007); unit rating NASA_RTG; '
                     'the kW-class criticals stay on the fission base and the fuel cell (F-20261113-01)'}


def sizer_rad_panel(b, drv, prof):
    """Radiator sizing from the profile's heat-rejection level for the unit:
    Stefan-Boltzmann area per kW at the level's radiator temperature against
    the profile's radiative sink and emissivity (A-M-396/397), at the unit's
    rated duty."""
    node = b.nodes.get('RAD_PANEL') or {}
    grp = ((prof.get('groups') or {}).get('heat_rejection') or {}).get('entries') or {}
    lv = None
    for row in (grp.get('levels') or {}).get('value') or []:
        if row.get('unit') == 'RAD_PANEL':
            lv = row
    if lv is None:
        return {}
    rad_k, sink = lv.get('radiator_K'), (grp.get('radiative_sink_K') or {}).get('value')
    eps = (grp.get('radiator_emissivity') or {}).get('value')
    duty = (node.get('params') or {}).get('rated_kW')
    out = {'radiator_K': float(dec(rad_k)), 'sink_K': float(dec(sink)),
           'emissivity': float(dec(eps)), 'duty_kW': float(dec(duty))}
    if rad_k and sink and eps and duty:
        area = W_PER_KW / (dec(eps) * SIGMA * (dec(rad_k) ** 4 - dec(sink) ** 4))
        out['area_m2_per_kW'] = q(area, 3)
        out['area_m2'] = q(area * dec(duty), 1)
        out['basis'] = 'A-M-396 (sink), A-M-397 (emissivity); Stefan-Boltzmann'
    return out


def sizer_lio_bat(b, drv, prof):
    """Worst-stretch storage sizing: the energy the stretch draws from storage
    at the plant demand, charged over the round trip (AQS-PLAN-011 section
    5.5; A-M-402 interim)."""
    demand = need_kw(b)
    if demand is None or drv is None:
        return {}
    eta = dec(drv['storage_round_trip']['value'])
    pf = portfolio_of(prof)
    h, f = stretch_hours(prof, pf), phi(pf)
    mean_per_kw = mean_generation_per_kw(prof, eta)
    delivered = (D1 - f * mean_per_kw) * h * demand
    return {'stretch_h': float(h), 'demand_kW': float(demand),
            'storage_delivered_kWh': q(delivered, 1),
            'storage_charged_kWh': q(delivered / eta, 1),
            'basis': 'AQS-PLAN-011 section 5.5 worst-stretch balance; A-M-402 interim'}


def sizer_generic(b, drv, prof):
    """No profile-based size: the placement carries the design record and
    sizes at the locale design pass (the v1 generic fallback)."""
    return {}


SIZERS = {'RAD_PANEL': sizer_rad_panel, 'LIO_BAT': sizer_lio_bat,
          'FSP_40K': sizer_fsp_40k, 'MMRTG': sizer_mmrtg}


# --- the scaling plan (the v1 scaling.resolve plan rows) ---------------------

def scaling_actions(profile):
    """The profile's scaling group's action list."""
    grp = (profile.get('groups') or {}).get('scaling') or {}
    return ((grp.get('entries') or {}).get('actions') or {}).get('value') or []


def targets(t, nodes):
    """The units a scaling action targets: a sector prefix sweeps the sector's
    units (sorted), a bare id names one unit. An id not in the graph fails
    loudly (the v1 resolve treats it as an error)."""
    if t.startswith('sector:'):
        return sorted(u for u in nodes if nodes[u].get('sector_id') == t[7:])
    if t not in nodes:
        raise ValueError(f'scaling target {t!r} is not a unit or a sector in the graph')
    return [t]


def _row(b, uid):
    """The plan row so far this pass (the overlay first), else the v1 default
    kept row: actions apply in profile order onto the same row."""
    got = b.computed.get(('node', uid, 'params.site_scaling'))
    if got is not None:
        return dict(got[0])
    return {'status': 'kept', 'factor': float(D1), 'count': 1,
            'replacement': None, 'import_path': None}


@fn('site_scale', 'site scaling plan per locale (AQS-PLAN-011 section 5, X-LOC-05): the profile scaling '
    'actions resolve to the per-unit plan book the locale solve applies; the duplicate count multiplies the '
    'redundancy source counts and the size factor applies through scale_rate')
def site_scale(b, inputs):
    prof = inputs.get('profile')
    if not isinstance(prof, dict):
        return
    for a in scaling_actions(prof):
        act = a.get('action')
        if act not in ACTIONS:
            raise ValueError(f'scaling action {act!r} is not one of {", ".join(ACTIONS)}')
        cite = a.get('ref') or a.get('register') or a.get('owner')
        for uid in targets(str(a.get('target', '')), b.nodes):
            if b.nodes[uid].get('presence') != 'present':
                continue                      # the plan covers present units (the v1 resolve)
            row = _row(b, uid)
            if act == 'size':
                row['factor'] = float(dec(a.get('factor', D1)))
            elif act == 'duplicate':
                row['count'] = int(a.get('count', 1))
            else:
                row['status'] = 'replaced' if act == 'replace' else 'eliminated'
                row['replacement'] = a.get('replacement')
                row['import_path'] = a.get('import_path')
            basis = f'site scaling action ({cite}): {act} on {uid} (AQS-PLAN-011 section 5, X-LOC-05)'
            b.set_node_field(uid, 'params.site_scaling', row, _prov(basis))


@fn('site_power_placement', 'per-locale placement and sizing of the placeholder units the scaling '
    'replacements and the portfolio sources name (AQS-SITE-013; AQS-PLAN-011 section 5.5; F-20261113-01 '
    'designed sources under the Q-024 revision): sizer dispatch keyed by the unit id the profile names, '
    'never a locale id')
def site_power_placement(b, inputs):
    prof = inputs.get('profile')
    if not isinstance(prof, dict):
        return
    sid = prof.get('site_id')
    if not sid:
        raise ValueError('profile lacks site_id')
    drv = site_drivers(inputs)
    placed = {}
    for a in scaling_actions(prof):
        rep = a.get('replacement')
        node = b.nodes.get(rep) if rep else None
        if node is None or node.get('presence') != 'placeholder':
            continue                       # kept reference units are not placements
        e = placed.setdefault(rep, [])
        if a.get('target') not in e:
            e.append(a.get('target'))
    pf = portfolio_of(prof)
    for s in pf.get('sources', []):
        # a designed source the portfolio names (role primary or backup): placed and sized per
        # locale; flagged options (role option) stay studies, not placements
        node = b.nodes.get(s.get('unit'))
        if node is None or node.get('presence') != 'placeholder' or s.get('role') not in ('primary', 'backup'):
            continue
        placed.setdefault(s['unit'], [])
    for uid in sorted(placed):
        sizer = SIZERS.get(uid, sizer_generic)
        sizing = sizer(b, drv, prof)
        basis = f'site placement per locale ({REGISTER}): {uid}'
        b.set_node_field(uid, 'params.site_placement',
                         {'site': sid, 'replaces': placed[uid], 'sizing': sizing, 'register': REGISTER},
                         _prov(basis))


# --- the lake ED train (the v1 lake_boehmer compute/stamp, promoted) ---------

def ed_train(drv, prof):
    """The lake-site ED train sizing from the site-bound drivers and profile.
    Transfer functions, per unit volume of dilute: SEC = F dC_eq U / (CE x the
    kWh in joules); dC_eq = 2 (C_in - C_out) / NaCl x 1000 mol_eq/m3; the
    salt transport a module carries R = j A CE / F x the seconds in a day;
    the duty divides by R, rounds up, one spare module per stage (A-M-451).
    Power follows the D-PV rule: the balancing nameplate at the site-bound
    drivers times the bound oversize factor; the battery usable store carries
    the night energy plus the contingency days (A-M-443). Pure; every value
    exact until the record quantises."""
    def val(k):
        return dec(drv[k]['value'])
    feed = val(LB + 'feed_m3_d')
    tds_in = val(LB + 'feed_tds_g_L')
    rec = val(LB + 'ed_recovery')
    tds_mid = val(LB + 'ed_stage1_product_tds_g_L')
    tds_out = val(LB + 'product_tds_mg_L') / MG_PER_G
    volt = val(LB + 'ed_cellpair_voltage_V')
    ce = val(LB + 'ed_current_efficiency')
    j = val(LB + 'ed_current_density_A_m2')
    area = val(LB + 'ed_membrane_area_m2')
    spare = int(val(LB + 'ed_spare_modules_per_stage'))
    per_cont = val(LB + 'ed_modules_per_container')
    dilute = feed * rec                                   # product path, m3/d
    conc = feed - dilute                                  # concentrate path, m3/d
    stages = []
    for name, t0, t1 in (('LB_ED1', tds_in, tds_mid), ('LB_ED2', tds_mid, tds_out)):
        dc_eq = DEC2 * (t0 - t1) / NACL * DEC1000         # mol_eq per m3 of dilute
        duty = dc_eq * dilute                             # mol_eq/d
        sec = F_FARADAY * dc_eq * volt / (ce * J_PER_KWH)  # kWh/m3 of dilute
        r_mod = j * area * ce / F_FARADAY * SEC_DAY       # mol_eq/d per module
        n_duty = ceil_ratio(duty, r_mod)
        n_inst = n_duty + spare
        stages.append(dict(unit=name, dilute_m3_d=float(dilute),
                           tds_in_g_L=drv[LB + 'feed_tds_g_L']['value'] if name == 'LB_ED1' else float(t0),
                           tds_out_g_L=float(t1),
                           delta_eq_m3=q(dc_eq, 2), duty_eq_d=q(duty, 1),
                           sec_kwh_m3=q(sec, 3), energy_kwh_d=q(sec * dilute, 1),
                           eq_per_module_d=q(r_mod, 1), modules_duty=n_duty,
                           modules_installed=n_inst,
                           rectifier_capacity_kw=q(dec(n_inst) * j * area * volt / W_PER_KW, 1)))
    ed_kwh = q(sum(dec(s['energy_kwh_d']) for s in stages), 1)
    aux_keys = (LB + 'aux_intake_kWh_m3', LB + 'aux_degasser_kWh_m3',
                LB + 'aux_softening_kWh_m3', LB + 'aux_dosing_cip_kWh_m3')
    aux = dec(q(sum(val(k) for k in aux_keys), 2))
    aux_kwh = q(aux * feed, 1)
    demand = dec(q((dec(ed_kwh) + dec(aux_kwh)) / DAY, 2))
    eta, night = val('storage_round_trip'), val('night_hours')
    yld, der, ov = val('pv_yield_kWh_kWp_d'), val('pv_system_derate'), val('pv_oversize_factor')
    balance = pv_kwp(demand, night, eta, yld, der) * pv_factor(prof, eta)
    nameplate = ceil_ratio(balance * ov, D1)
    cont = int(val(LB + 'battery_contingency_days'))
    usable = demand * night + demand * DAY * dec(cont)
    charged = usable / eta
    bess = ceil_ratio(charged, val(LB + 'bess_container_kWh'))
    ed_cont = sum(ceil_ratio(dec(s['modules_installed']), per_cont) for s in stages)
    util = drv[LB + 'utility_containers']['value']
    salt_in = feed * tds_in
    salt_prod = dilute * tds_out
    salt_removed = dilute * (tds_in - tds_out)
    tds_conc = tds_in + salt_removed / conc
    salt_conc = conc * tds_conc
    closure = salt_in - (salt_prod + salt_conc)
    return dict(
        flows=dict(feed_m3_d=drv[LB + 'feed_m3_d']['value'], product_m3_d=float(dilute),
                   concentrate_m3_d=float(conc), feed_tds_g_L=drv[LB + 'feed_tds_g_L']['value'],
                   product_tds_g_L=float(tds_out), concentrate_tds_g_L=q(tds_conc, 1),
                   salt_feed_kg_d=q(salt_in, 1), salt_product_kg_d=q(salt_prod, 1),
                   salt_concentrate_kg_d=q(salt_conc, 1), salt_closure_kg_d=q(closure, 4),
                   salt_removed_from_dilute_kg_d=q(salt_removed, 1)),
        stages=stages,
        ed=dict(energy_kwh_d=ed_kwh, aux_kwh_m3_feed=float(aux), aux_kwh_d=aux_kwh,
                demand_kw=float(demand), ed_containers=ed_cont,
                utility_containers=util, utility_container_total=sum(util.values())),
        power=dict(demand_kw=float(demand), pv_balance_kWp=q(balance, 1),
                   pv_nameplate_kWp=nameplate, pv_yield_kWh_kWp_d=float(yld),
                   pv_system_derate=float(der), pv_oversize_factor=float(ov),
                   night_hours=float(night), storage_round_trip=float(eta),
                   battery_usable_kwh=q(usable, 1), battery_charged_kwh=q(charged, 1),
                   battery_contingency_days=cont, battery_containers=bess),
        containers_total=ed_cont + sum(util.values()) + bess)


def ed_designs(c):
    """The params.lb_design blocks the design pass stamps (the v1 stamp
    designs dict, verbatim)."""
    st = {s['unit']: s for s in c['stages']}
    fl, ed, pw = c['flows'], c['ed'], c['power']
    designs = {
        'LB_INTAKE': dict(feed_m3_d=fl['feed_m3_d'], feed_tds_g_L=fl['feed_tds_g_L'],
                          feed_so4_mg_L=7500, site_safety_h2s_ppm=110,
                          basis='drivers WTR.lake-boehmer.* (A-M-434/435/436); AQS-SITE-015'),
        'LB_DEGAS': dict(air_water_ratio_vol=60, h2s_removal_target=float(dec('0.95')),
                         basis='Henry coefficients WTR.lake-boehmer.henry_* (SANDER2015, A-M-450); '
                               'ratio and removal pending the packed-tower design pass'),
        'LB_DEGAS_SCRUB': dict(site_safety_h2s_ppm=110, osha_ceiling_ppm=10,
                               design_load='pending the dissolved-sulfide assay (A-M-436)',
                               basis='A-M-436; lethal-site controls at the units and the vent'),
        'LB_SOFTEN': dict(ed_recovery_basis='concentrate gypsum at most 2 x Ksp with softening (A-M-437)',
                          feed_calcium='unmeasured (A-M-447); chemistry sizes on the assayed feed'),
        'LB_PROD_TANK': dict(product_m3_d=fl['product_m3_d'],
                             hold='locale design pass (A-M-225 basis)'),
        'LB_PROD_OUTLET': dict(product_m3_d=fl['product_m3_d'], concentrate_m3_d=fl['concentrate_m3_d'],
                               net_lake_salt_removal_kg_d=q(D0, 1), statement=NET_SALT,
                               basis='owner decision Q-037; AQS-SITE-015'),
        'LB_BRINE_RETURN': dict(concentrate_m3_d=fl['concentrate_m3_d'],
                                concentrate_tds_g_L=fl['concentrate_tds_g_L'],
                                basis='A-M-437; carries the removed salt back to the lake (Q-037)'),
        'LB_CHEM_STORE': dict(services=['lime', 'soda ash', 'scrubber caustic', 'clean-in-place acid'],
                              basis='A-M-225 hold-time basis; resupply by road (AQS-SITE-015 logistics)'),
    }
    designs['LB_ED1'] = dict(st['LB_ED1'], basis=SEC_BASIS)
    designs['LB_ED2'] = dict(st['LB_ED2'], basis=SEC_BASIS)
    designs['LIO_BAT'] = dict(battery_usable_kwh=pw['battery_usable_kwh'],
                              battery_charged_kwh=pw['battery_charged_kwh'],
                              battery_contingency_days=pw['battery_contingency_days'],
                              night_hours=pw['night_hours'], demand_kw=pw['demand_kw'],
                              pv_nameplate_kWp=pw['pv_nameplate_kWp'],
                              battery_containers=pw['battery_containers'],
                              basis='Lake Boehmer locale design pass (AQS-SITE-015); supersedes the '
                                    'A-M-402 interim carry at this locale')
    return designs


@fn('lake_ed_train', 'lake Boehmer site design pass (AQS-SITE-015, X-LOC-05): the lake-restoration ED train, '
    'its auxiliaries, the D-PV rule nameplate and the battery store, from the site profile and the drivers '
    '(F CODATA2018; STRATHMANN2004 cell-pair voltage A-M-438; CAMPIONE2018 CE and j A-M-439/440; membrane '
    'area A-M-441; recovery A-M-437; auxiliaries A-M-442; contingency A-M-443; containers A-M-444/445/446; '
    'stage split A-M-449; degasser A-M-450; the N+1 spare per stage A-M-451). The v1 locale-id guard is '
    'promoted to a data condition: the train fires only when the seed carries its units and the drivers '
    'carry the design set')
def lake_ed_train(b, inputs):
    drv = inputs.get('drivers')
    prof = inputs.get('profile')
    if not isinstance(drv, dict) or not isinstance(prof, dict):
        return
    if not all(u in b.nodes for u in LB_UNITS):
        return                                          # no ED train units on this seed
    d = site_drivers(inputs)
    if d is None or not all(k in d for k in LB_KEYS) or not all(k in d for k in LB_POWER_KEYS):
        return                                          # the design driver set is absent
    basis = ('lake Boehmer locale design pass (AQS-SITE-015; X-LOC-05): the ED train sizing from the site '
             'profile and drivers; stamped on the train units and the storage replacement')
    for uid, design in ed_designs(ed_train(d, prof)).items():
        b.set_node_field(uid, 'params.lb_design', design, _prov(basis))

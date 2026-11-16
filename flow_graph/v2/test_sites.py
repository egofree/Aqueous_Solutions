"""engine v2: the site/locale family acceptance (the golden-value proof).

Reference writers: flow_graph/param/scaling.py, flow_graph/param/portfolio.py,
flow_graph/param/site_units.py, flow_graph/param/lake_boehmer.py (ledger rows
`site_scaling`, `site_power`, `doc_site_units` placement half,
`lake_boehmer_design`). The proofs:

- no locale name in the engine module: an AST check holds the audit's guard
  promotion - every dispatch and design condition is data (the seed's units,
  the profile's entries, the driver set), never a locale id;
- golden equality: the RAD_PANEL sizing book equals the committed locale stamp
  in sites/mars/flow_graph/plant_flow_graph.json, the LIO_BAT stretch book
  equals the committed locale stamp in sites/leo/... on the stamp's own
  recorded demand base, and the lake ED train books equal the reference
  writer's pure compute() on the committed drivers - the books AQS-SITE-015
  publishes (the baseline seed carries no lb_design stamps, because the v1
  stage writes only inside its locale worktree and no sites/lake_boehmer/
  tree is committed, so the documented books are the golden);
- the placement dispatch table: dust deficit -> fission duty count (ceil) plus
  the N+1 spare, controls trickle -> RTG count - data rows through the
  registered function, including tampered drivers, a tampered dust fraction
  and the study demand base (the finding's landed counts);
- the scaling table: factor -> application results as data rows, and the plan
  book through the registered function (size, duplicate, replace, eliminate);
- the portfolio worst-stretch balance re-derived on exact Decimal books;
- the bridge contracts: no site payload records nothing; a seed without the
  ED train units or a driver payload without the design set records nothing
  (the promoted guard);
- determinism: two runs, byte-identical;
- grid purity: no float literals, no I/O, and no locale-id literal in the
  family module.
"""
import ast
import copy
import inspect
import json
import os
from decimal import Decimal

from flow_graph.v2.functions import sites as ST
from flow_graph.v2.graph_io import bytes as render, load

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF_GRAPH = os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')
DRIVERS = os.path.join(ROOT, 'flow_graph', 'param', 'drivers.json')
SITES = os.path.join(ROOT, 'flow_graph', 'param', 'sites')
MARS_GRAPH = os.path.join(ROOT, 'sites', 'mars', 'flow_graph', 'plant_flow_graph.json')
LEO_GRAPH = os.path.join(ROOT, 'sites', 'leo', 'flow_graph', 'plant_flow_graph.json')

DRIVERS_JSON = json.load(open(DRIVERS))
MARS = json.load(open(os.path.join(SITES, 'mars.json')))
LEO = json.load(open(os.path.join(SITES, 'leo.json')))
LAKE = json.load(open(os.path.join(SITES, 'lake_boehmer.json')))
INPUTS_MARS = {'drivers': DRIVERS_JSON, 'profile': MARS}
INPUTS_LAKE = {'drivers': DRIVERS_JSON, 'profile': LAKE}
LOCALE_IDS = sorted(f[:-5] for f in os.listdir(SITES) if f.endswith('.json'))

ETA = Decimal('0.7')                                   # driver storage_round_trip
MARS_H = Decimal('12.33')                              # the mars worst stretch, solar.night_hours
MARS_F = Decimal('0.755')                              # 0.65 x 1.0 + 0.35 x 0.3


def dig(obj, path):
    for part in path.split('.'):
        obj = obj[part]
    return obj


def num_eq(gold, got):
    return Decimal(str(gold)).normalize() == Decimal(str(got)).normalize()


def eq(gold, got):
    if isinstance(gold, dict):
        return isinstance(got, dict) and set(gold) == set(got) and all(eq(v, got[k]) for k, v in gold.items())
    if isinstance(gold, list):
        return isinstance(got, list) and len(gold) == len(got) and all(eq(a, b) for a, b in zip(gold, got))
    if isinstance(gold, (int, float)) and not isinstance(gold, bool):
        return isinstance(got, (int, float)) and not isinstance(got, bool) and num_eq(gold, got)
    return gold == got


def place(b, inputs=None):
    ST.site_power_placement(b, inputs if inputs is not None else INPUTS_MARS)
    return b


def test_no_locale_name_literals():
    """The audit's guard promotion, held syntactically: no string literal in
    the family module equals a locale id."""
    tree = ast.parse(inspect.getsource(ST))
    literals = [n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    assert LOCALE_IDS                                    # the check fails empty
    assert sorted(set(LOCALE_IDS)) == ['antarctic', 'baseline', 'cocoa_fl', 'death_valley',
                                       'floating_island', 'lake_boehmer', 'leo', 'mars']
    hit = sorted({x for x in literals if x in LOCALE_IDS})
    assert hit == [], hit


def test_scaling_table_factor_rows():
    """The size-factor application on rates/design values, as data rows."""
    rows = [                                             # (factor, value, product) exact
        ('0.5', '88.0192', '44.0096'),
        ('2.0', '1.25', '2.5'),
        ('1', '191.36', '191.36'),
        ('0.25', '12', '3'),
        ('1.5', '2', '3'),
    ]
    for factor, value, product in rows:
        assert ST.scale_rate(value, factor) == float(Decimal(product)), (factor, value)


def test_scaling_plan_book_through_the_registered_function():
    """The plan book the profile actions resolve to, per unit (the v1
    resolve rows): size, duplicate, replace, eliminate."""
    prof = copy.deepcopy(MARS)
    prof['groups']['scaling']['entries']['actions']['value'] = [
        {'target': 'sector:FOUNDRY', 'action': 'size', 'factor': 0.5, 'register': 'test'},
        {'target': 'FUEL_CELL', 'action': 'duplicate', 'count': 2, 'register': 'test'},
        {'target': 'DRY_COOLER', 'action': 'replace', 'replacement': 'RAD_PANEL', 'register': 'test'},
        {'target': 'FAB_UPW_TANK', 'action': 'eliminate', 'import_path': 'closed pressurised tank',
         'register': 'test'},
    ]
    b = load(REF_GRAPH)
    ST.site_scale(b, {'drivers': DRIVERS_JSON, 'profile': prof})
    foundry = {u: v[0] for (kind, u, p), v in b.computed.items()
               if kind == 'node' and p == 'params.site_scaling'
               and b.nodes[u].get('sector_id') == 'FOUNDRY'}
    assert foundry and all(row['factor'] == 0.5 and row['status'] == 'kept' for row in foundry.values())
    fc = b.computed[('node', 'FUEL_CELL', 'params.site_scaling')][0]
    assert fc['count'] == 2 and fc['factor'] == 1.0 and fc['status'] == 'kept'
    dc = b.computed[('node', 'DRY_COOLER', 'params.site_scaling')][0]
    assert dc['status'] == 'replaced' and dc['replacement'] == 'RAD_PANEL'
    upw = b.computed[('node', 'FAB_UPW_TANK', 'params.site_scaling')][0]
    assert upw['status'] == 'eliminated' and upw['import_path'] == 'closed pressurised tank'
    # two size actions on one unit merge onto one row, in profile order
    prof['groups']['scaling']['entries']['actions']['value'] = [
        {'target': 'FUEL_CELL', 'action': 'size', 'factor': 2, 'register': 'test'},
        {'target': 'FUEL_CELL', 'action': 'duplicate', 'count': 3, 'register': 'test'},
    ]
    b2 = load(REF_GRAPH)
    ST.site_scale(b2, {'drivers': DRIVERS_JSON, 'profile': prof})
    row = b2.computed[('node', 'FUEL_CELL', 'params.site_scaling')][0]
    assert row == {'status': 'kept', 'factor': 2.0, 'count': 3, 'replacement': None, 'import_path': None}
    # a bad action verb or an unknown target fails loudly (the v1 resolve errors)
    for bad in ({'target': 'HX8', 'action': 'shrink', 'factor': 2, 'register': 't'},
                {'target': 'NO_UNIT', 'action': 'size', 'factor': 2, 'register': 't'}):
        bb = load(REF_GRAPH)
        try:
            ST.site_scale(bb, {'drivers': DRIVERS_JSON, 'profile':
                               dict(prof, groups={'scaling': {'entries': {'actions': {'value': [bad]}}}})})
            raise AssertionError('bad action accepted')
        except ValueError:
            pass


def test_mars_scaling_golden():
    """The committed mars profile resolves on the baseline seed to its
    elimination plan: every action target carries its replacement or import
    path, as the locale solve would record it."""
    b = load(REF_GRAPH)
    ST.site_scale(b, INPUTS_MARS)
    acts = MARS['groups']['scaling']['entries']['actions']['value']
    stamped = {(u, v[0]['status']) for (kind, u, p), v in b.computed.items()
               if kind == 'node' and p == 'params.site_scaling'}
    assert len(stamped) == len({a['target'] for a in acts}) == 17
    hs = b.computed[('node', 'HYDRO_SET', 'params.site_scaling')][0]
    assert hs == {'status': 'eliminated', 'factor': 1.0, 'count': 1,
                  'replacement': 'ZNBR2', 'import_path': None}
    upw = b.computed[('node', 'FAB_UPW_TANK', 'params.site_scaling')][0]
    assert upw['replacement'] is None and upw['import_path'].startswith('closed pressurised UPW tank')


def test_placement_golden_mars_rad_panel():
    """The RAD_PANEL sizing book equals the committed locale stamp in
    sites/mars (the Stefan-Boltzmann book, quantised at the stamp's
    decimals)."""
    b = place(load(REF_GRAPH))
    got = b.computed[('node', 'RAD_PANEL', 'params.site_placement')][0]
    committed = dig({n['unit_id']: n for n in json.load(open(MARS_GRAPH))['nodes']},
                    'RAD_PANEL.params.site_placement'.split('.')[0])['params']['site_placement']
    assert eq(committed, got)
    assert got['site'] == 'mars' and got['replaces'] == ['DRY_COOLER']
    assert got['sizing']['area_m2_per_kW'] == 1.862 and got['sizing']['area_m2'] == 22.3
    # the exact book re-derived: 1000 / (eps sigma (Tr^4 - Ts^4))
    area = Decimal(1000) / (Decimal('0.9') * ST.SIGMA * (Decimal(328) ** 4 - Decimal(180) ** 4))
    assert area.quantize(Decimal('0.001')) == Decimal('1.862')
    assert (area * Decimal(12)).quantize(Decimal('0.1')) == Decimal('22.3')


def test_placement_set_and_no_locale_conditionals():
    """The placement set follows from the profile data alone: the mars
    replacements that are placeholders, plus the portfolio's designed
    sources. The same function with the lake profile names a different set -
    the profile decides, never a locale id in code."""
    b = place(load(REF_GRAPH))
    got = {u for (kind, u, p) in b.computed if kind == 'node' and p == 'params.site_placement'}
    assert got == {'RAD_PANEL', 'TANK_BLD', 'REC_HDR', 'CAT_OX', 'E_HEAT', 'FSP_40K', 'MMRTG'}
    for uid in got:                                    # every placement the profile names
        srcs = [s['unit'] for s in MARS['groups']['power_portfolio']['entries']['sources']['value']]
        reps = [a.get('replacement') for a in MARS['groups']['scaling']['entries']['actions']['value']]
        assert uid in srcs or uid in reps
    bl = place(load(REF_GRAPH), {'drivers': DRIVERS_JSON, 'profile': LEO})
    leo_set = {u for (kind, u, p) in bl.computed if kind == 'node' and p == 'params.site_placement'}
    assert 'FSP_40K' not in leo_set and 'MMRTG' not in leo_set and 'LIO_BAT' in leo_set


def test_placement_golden_leo_lio_bat():
    """The LIO_BAT stretch book equals the committed locale stamp in sites/leo
    on the stamp's own recorded demand base. Deviation enumerated: the
    committed leo file's need_kw has since moved to 144.53, so a fresh locale
    run would book a different demand; the rule and the stretch book are the
    golden, the demand is the stamp's recorded input."""
    committed = {n['unit_id']: n for n in json.load(open(LEO_GRAPH))['nodes']}
    gold = committed['LIO_BAT']['params']['site_placement']
    b = load(REF_GRAPH)
    b.data['mvs']['electrical']['need_kw']['value'] = gold['sizing']['demand_kW']   # the recorded base
    place(b, {'drivers': DRIVERS_JSON, 'profile': LEO})
    got = b.computed[('node', 'LIO_BAT', 'params.site_placement')][0]
    assert got['replaces'] == gold['replaces'] == ['ZNBR2', 'ZNBR2_BR2_REGEN', 'HYDRO_SET']
    assert eq(gold['sizing'], got['sizing'])
    assert got['sizing']['storage_delivered_kWh'] == 101.2      # h P = 0.56 x 180.75
    assert got['sizing']['storage_charged_kWh'] == 144.6        # delivered / eta
    # the rule rows on the current committed locale demand: delivered = h P, charged = delivered / eta
    for demand, delivered, charged in (('144.53', '80.9', '115.6'), ('191.36', '107.2', '153.1')):
        bb = load(REF_GRAPH)
        bb.data['mvs']['electrical']['need_kw']['value'] = float(Decimal(demand))
        place(bb, {'drivers': DRIVERS_JSON, 'profile': LEO})
        book = bb.computed[('node', 'LIO_BAT', 'params.site_placement')][0]['sizing']
        assert book['storage_delivered_kWh'] == float(Decimal(delivered)), (demand, book)
        assert book['storage_charged_kWh'] == float(Decimal(charged)), (demand, book)


def mars_mean_generation():
    return ((Decimal(24) - MARS_H) + MARS_H / ETA) / (Decimal(24) - MARS_F * MARS_H + MARS_F * MARS_H / ETA)


def fission_book(b, need):
    """Run the placement dispatch on a seed whose converged demand is `need`
    (kW): the FSP_40K sizing book (the demand-base is the study's recorded
    input, as in the leo proof)."""
    b.data['mvs']['electrical']['need_kw']['value'] = need
    place(b)
    return b.computed[('node', 'FSP_40K', 'params.site_placement')][0]['sizing']


def test_placement_dispatch_fission_rows():
    """Dust deficit -> fission duty count (ceil) + the N+1 spare, as data rows
    through the registered function. The counts follow the demand base:
    - the committed baseline demand book (need 191.36 less the 88.0192 kW roof
      extension) -> 3 duty + 1 spare, the same counts the study's recorded
      103.2 kW demand book and its 91.9 kW deficit produce;
    - the study demand base the finding recorded (the mars locale demand
      390.31 less the baseline roof extension) -> 7 duty + 1 spare
      (F-20261113-01: 'surface fission 7 duty + 1 spare x 40 kW_e');
    - a tampered dust fraction 1.0 moves the deficit and the count."""
    base = fission_book(load(REF_GRAPH), 191.36)
    assert base['demand_kW'] == 103.34 and base['dust_deficit_kW'] == 91.99
    assert base['count_duty'] == 3 and base['count_installed_n_plus_1'] == 4
    assert base['installed_kW_e'] == 160.0
    rec = MARS['groups']['power_portfolio']['entries']['dust_stretch_design']['value']
    assert ST.ceil_ratio(Decimal(str(rec['load_book']['plant_demand_kW'])), Decimal('40')) == 3
    assert rec['dust_season_store']['with_fission_base'].startswith(
        'the night bank stays as built')                      # the 91.9 kW deficit book, study provenance
    study = fission_book(load(REF_GRAPH), 390.31)             # the finding's demand base
    assert study['demand_kW'] == 302.29 and study['dust_deficit_kW'] == 269.08
    assert study['count_duty'] == 7 and study['count_installed_n_plus_1'] == 8
    assert study['installed_kW_e'] == 320.0
    assert study['basis'].startswith('AQS-PLAN-011 section 5.5')
    # tampered dust fraction: PV delivers its full mean rate through the stretch
    prof = copy.deepcopy(MARS)
    prof['groups']['power_portfolio']['entries']['dust_stretch_design']['value'] = dict(
        rec, pv_stretch_output_frac=1.0)
    bb = load(REF_GRAPH)
    place(bb, {'drivers': DRIVERS_JSON, 'profile': prof})
    book = bb.computed[('node', 'FSP_40K', 'params.site_placement')][0]['sizing']
    assert book['dust_pv_output_frac'] == 1.0 and book['dust_deficit_kW'] == 65.5
    assert book['count_duty'] == 2 and book['count_installed_n_plus_1'] == 3
    assert book['installed_kW_e'] == 120.0
    # a deficit fully covered by PV books no duty units
    prof['groups']['power_portfolio']['entries']['dust_stretch_design']['value'] = dict(
        rec, pv_stretch_output_frac=20.0)
    bb = load(REF_GRAPH)
    place(bb, {'drivers': DRIVERS_JSON, 'profile': prof})
    book = bb.computed[('node', 'FSP_40K', 'params.site_placement')][0]['sizing']
    assert book['count_duty'] == 0 and book['count_installed_n_plus_1'] == 1


def test_placement_dispatch_rtg_rows():
    """Controls trickle -> RTG count, through the registered function: the
    committed trickle (2.0 kW) gives the study's 19 units and 2.09 kW_e
    carried; a tampered trickle moves the count by the same ceil rule."""
    b = place(load(REF_GRAPH))
    book = b.computed[('node', 'MMRTG', 'params.site_placement')][0]['sizing']
    rec = MARS['groups']['power_portfolio']['entries']['dust_stretch_design']['value']
    assert book['controls_trickle_kW'] == rec['load_book']['controls_trickle_kW'] == 2.0
    assert book['count'] == rec['rtg']['controls_trickle_units'] == 19
    assert book['carries_W_e'] == rec['rtg']['carries_kW_e'] * 1000 == 2090.0
    assert book['critical_list_kW'] == 14.58                  # HAB 3.0 + H2 2.83 + ASU 1.75 + grow 5.0 + controls 2.0
    assert ST.ceil_ratio(Decimal('2000'), Decimal('110')) == 19
    drv = copy.deepcopy(DRIVERS_JSON)
    drv['ELEC.generation-train.BACKUP_GEN.crit_controls_kW']['value'] = 1.05
    bb = place(load(REF_GRAPH), {'drivers': drv, 'profile': MARS})
    book = bb.computed[('node', 'MMRTG', 'params.site_placement')][0]['sizing']
    assert book['controls_trickle_kW'] == 1.05 and book['count'] == 10
    assert book['carries_W_e'] == 1100.0
    assert ST.ceil_ratio(Decimal('1050'), Decimal('110')) == 10


def test_portfolio_balance_exact_books():
    """The worst-stretch balance re-derived on exact Decimal books: G/P, phi,
    the stretch hours and the PV factor."""
    assert ST.phi(ST.portfolio_of(MARS)) == MARS_F == Decimal('0.755')
    assert ST.stretch_hours(MARS, ST.portfolio_of(MARS)) == MARS_H
    assert ST.mean_generation_per_kw(MARS, ETA) == mars_mean_generation()
    assert mars_mean_generation().quantize(Decimal('0.000001')) == Decimal('1.046255')
    # PV alone with no stretch output is exactly the reference balance
    assert ST.pv_factor(LAKE, ETA) == Decimal(1)
    assert ST.pv_factor(MARS, ETA) == Decimal('0.35') * (Decimal(24) / (
        Decimal(24) - MARS_F * MARS_H + MARS_F * MARS_H / ETA))
    # the reference PV balance itself: (P (24 - h) + P h / eta) / (yield x derate)
    p = Decimal('2594.63')
    bal = ST.pv_kwp(p, Decimal('13.5'), ETA, Decimal('5.8'), Decimal('0.8'))
    assert bal.quantize(Decimal('0.1')) == Decimal('16655.8')
    assert bal.quantize(Decimal('0.01')) == Decimal('16655.80')


def test_lake_ed_train_golden_books():
    """The lake ED train books equal the reference writer's pure compute() on
    the committed drivers - the books AQS-SITE-015 publishes (tables 5.1/5.2:
    14/15 and 7/8 modules, 1800 + 960 kW rectifiers, about 2595 kW demand,
    16656 and 33312 kWp, 97299 and 139000 kWh, 35 battery containers,
    12 + 14 + 35 containers)."""
    b = load(REF_GRAPH)
    ST.lake_ed_train(b, INPUTS_LAKE)
    got = {(u, p) for (kind, u, p) in b.computed if kind == 'node'}
    assert got == {(u, 'params.lb_design') for u in ST.LB_UNITS} | {('LIO_BAT', 'params.lb_design')}
    ed1 = b.computed[('node', 'LB_ED1', 'params.lb_design')][0]
    ed2 = b.computed[('node', 'LB_ED2', 'params.lb_design')][0]
    # stage books (the transfer functions, quantised at the v1 record decimals)
    for book, dc, duty, sec, energy, nduty in ((ed1, 2053.39, 1026694.0, 77.695, 38847.4, 14),
                                               (ed2, 1026.69, 513347.0, 38.847, 19423.7, 7)):
        assert book['delta_eq_m3'] == dc and book['duty_eq_d'] == duty
        assert book['sec_kwh_m3'] == sec and book['energy_kwh_d'] == energy
        assert book['modules_duty'] == nduty and book['modules_installed'] == nduty + 1   # the N+1 spare
        assert book['eq_per_module_d'] == 76115.2
    assert ed1['rectifier_capacity_kw'] == 1800.0 and ed2['rectifier_capacity_kw'] == 960.0
    assert ed1['dilute_m3_d'] == 500.0 and ed1['tds_in_g_L'] == 105 and ed1['tds_out_g_L'] == 45.0
    assert ed2['tds_in_g_L'] == 45.0 and ed2['tds_out_g_L'] == 15.0
    # AQS-SITE-015 table 5.1 rows, as data (the doc rounds to the stated precision)
    assert Decimal(str(ed1['duty_eq_d'])).quantize(Decimal('1E3')) == Decimal('1.027E+6')   # "about 1,027,000 eq/d"
    assert Decimal(str(ed2['duty_eq_d'])).quantize(Decimal('1E3')) == Decimal('5.13E+5')    # "about 513,000 eq/d"
    assert ST.q(Decimal(str(ed1['sec_kwh_m3'])), 1) == 77.7                          # "77.7 kWh/m3"
    # the salt ledger closes: feed = product + concentrate, closure 0
    lio = b.computed[('node', 'LIO_BAT', 'params.lb_design')][0]
    intake = b.computed[('node', 'LB_INTAKE', 'params.lb_design')][0]
    outlet = b.computed[('node', 'LB_PROD_OUTLET', 'params.lb_design')][0]
    brine = b.computed[('node', 'LB_BRINE_RETURN', 'params.lb_design')][0]
    assert intake['feed_m3_d'] == 1000 and intake['feed_tds_g_L'] == 105
    assert outlet['product_m3_d'] == 500.0 and brine['concentrate_m3_d'] == 500.0
    assert brine['concentrate_tds_g_L'] == 195.0
    assert outlet['net_lake_salt_removal_kg_d'] == 0.0
    assert Decimal(str(ed1['duty_eq_d'])) / Decimal(str(ed2['duty_eq_d'])) == Decimal('2')
    # power and storage: the D-PV rule nameplate, the night-plus-contingency store
    assert lio['demand_kw'] == 2594.63 and lio['pv_nameplate_kWp'] == 33312
    assert lio['battery_usable_kwh'] == 97298.6 and lio['battery_charged_kwh'] == 138998.0
    assert lio['battery_containers'] == 35 and lio['battery_contingency_days'] == 1
    assert lio['night_hours'] == 13.5
    # AQS-SITE-015 table 5.2 rows, as data: "about 16,656 / 33,312 kWp", "about 97,299 / 139,000 kWh"
    assert ST.q(Decimal('16655.8'), 0) == 16656.0 and ST.q(Decimal('97298.6'), 0) == 97299.0
    assert Decimal('138998.0').quantize(Decimal('1E3')) == Decimal('1.39E+5')                # "about 139,000 kWh"
    assert ST.ceil_ratio(Decimal('138998.0'), Decimal('4000')) == 35


def test_lake_ed_train_exact_transfer_functions():
    """The transfer functions re-checked on exact Decimal books, independent
    of the stamping: the specific-energy rule, the module transport rate, the
    container ceils."""
    F, nacl, j_kwh = ST.F_FARADAY, ST.NACL, ST.J_PER_KWH
    dc1 = Decimal(2) * (Decimal('105') - Decimal('45')) / nacl * Decimal(1000)
    assert dc1.quantize(Decimal('0.01')) == Decimal('2053.39')
    sec = F * dc1 * Decimal('1.2') / (Decimal('0.85') * j_kwh)
    assert sec.quantize(Decimal('0.001')) == Decimal('77.695')
    r_mod = Decimal('100') * Decimal('1000') * Decimal('0.85') / F * ST.SEC_DAY
    assert r_mod.quantize(Decimal('0.1')) == Decimal('76115.2')
    duty = dc1 * Decimal('500.0')
    assert ST.ceil_ratio(duty, r_mod) == 14 and ST.ceil_ratio(duty / 2, r_mod) == 7
    assert ST.ceil_ratio(Decimal(15), Decimal(2)) + ST.ceil_ratio(Decimal(8), Decimal(2)) == 12
    # the exact function against the quantised books
    c = ST.ed_train(ST.site_drivers(INPUTS_LAKE), LAKE)
    assert c['ed']['energy_kwh_d'] == 58271.1 and c['ed']['aux_kwh_m3_feed'] == 4.0
    assert c['ed']['aux_kwh_d'] == 4000.0 and c['ed']['demand_kw'] == 2594.63
    assert c['ed']['ed_containers'] == 12 and c['ed']['utility_container_total'] == 14
    assert c['power']['pv_balance_kWp'] == 16655.8 and c['power']['pv_nameplate_kWp'] == 33312
    assert c['flows']['salt_closure_kg_d'] == 0.0 and c['flows']['salt_feed_kg_d'] == 105000.0
    assert c['containers_total'] == 61


def test_lake_design_blocks_verbatim():
    """The stamped design blocks are the v1 stamp dicts verbatim."""
    b = load(REF_GRAPH)
    ST.lake_ed_train(b, INPUTS_LAKE)
    degas = b.computed[('node', 'LB_DEGAS', 'params.lb_design')][0]
    assert degas == {'air_water_ratio_vol': 60, 'h2s_removal_target': 0.95,
                     'basis': 'Henry coefficients WTR.lake-boehmer.henry_* (SANDER2015, A-M-450); '
                              'ratio and removal pending the packed-tower design pass'}
    scrub = b.computed[('node', 'LB_DEGAS_SCRUB', 'params.lb_design')][0]
    assert scrub['osha_ceiling_ppm'] == 10 and scrub['site_safety_h2s_ppm'] == 110
    assert scrub['design_load'] == 'pending the dissolved-sulfide assay (A-M-436)'
    chem = b.computed[('node', 'LB_CHEM_STORE', 'params.lb_design')][0]
    assert chem['services'] == ['lime', 'soda ash', 'scrubber caustic', 'clean-in-place acid']
    lio = b.computed[('node', 'LIO_BAT', 'params.lb_design')][0]
    assert lio['basis'] == ('Lake Boehmer locale design pass (AQS-SITE-015); supersedes the '
                            'A-M-402 interim carry at this locale')


def test_driver_binding_is_data():
    """The profile overlays its bound drivers; a bind naming an unknown driver
    or carrying different units fails loudly."""
    d = ST.bind_drivers(DRIVERS_JSON, MARS)
    assert d['night_hours']['value'] == 12.33 and d['pv_yield_kWh_kWp_d']['value'] == 2.5
    assert d['pv_oversize_factor']['value'] == 2.0
    assert DRIVERS_JSON['night_hours']['value'] == 14.0       # the committed drivers are untouched
    prof = copy.deepcopy(MARS)
    prof['groups']['solar']['entries']['night_hours']['units'] = 'fortnights'
    for bad in (prof, copy.deepcopy(MARS) | {'groups': {'solar': {'entries': {
            'night_hours': {'value': 1, 'units': 'h', 'binds': 'not_a_driver'}}}}}):
        try:
            ST.bind_drivers(DRIVERS_JSON, bad)
            raise AssertionError('bad bind accepted')
        except ValueError:
            pass


def test_bridge_contract_no_payloads_records_nothing():
    """The bridge solve / check carry no site payloads: without the profile
    the scaling and placement chains record nothing; without drivers and
    profile the lake train records nothing - the seed stands."""
    for inputs in ({}, {'drivers': DRIVERS_JSON}):
        b = load(REF_GRAPH)
        ST.site_scale(b, inputs)
        ST.site_power_placement(b, inputs)
        ST.lake_ed_train(b, inputs)
        assert b.computed == {}, inputs
    for prof in (MARS, LEO, LAKE):                             # profile only: no lake books
        b = load(REF_GRAPH)
        ST.lake_ed_train(b, {'profile': prof})
        assert not any(p == 'params.lb_design' for (_, _, p) in b.computed)


def test_lake_guard_is_the_data_condition():
    """The promoted guard: without the ED train units on the seed, or without
    the design driver set in the payload, the train records nothing - the
    condition is data, never a locale id."""
    b = load(REF_GRAPH)
    b.nodes.pop('LB_ED2')
    ST.lake_ed_train(b, INPUTS_LAKE)
    assert b.computed == {}
    drv = {k: v for k, v in DRIVERS_JSON.items() if not k.startswith(ST.LB)}
    b = load(REF_GRAPH)
    ST.lake_ed_train(b, {'drivers': drv, 'profile': LAKE})
    assert b.computed == {}
    drv = copy.deepcopy(DRIVERS_JSON)
    del drv['pv_system_derate']
    b = load(REF_GRAPH)
    ST.lake_ed_train(b, {'drivers': drv, 'profile': LAKE})
    assert b.computed == {}


def test_determinism_two_runs_byte_identical():
    outs = []
    for _ in range(2):
        b = load(REF_GRAPH)
        ST.site_scale(b, INPUTS_MARS)
        place(b)
        ST.lake_ed_train(b, INPUTS_LAKE)
        outs.append(render(b))
    assert len(set(outs)) == 1


def test_provenance_rows():
    b = load(REF_GRAPH)
    ST.site_scale(b, INPUTS_MARS)
    place(b)
    ST.lake_ed_train(b, INPUTS_LAKE)
    for (kind, uid, path), (value, prov) in b.computed.items():
        assert prov.stage == 'site' and prov.basis
    assert 'AQS-PLAN-011 section 5' in b.computed[('node', 'HYDRO_SET', 'params.site_scaling')][1].basis
    assert 'FSP_40K' in b.computed[('node', 'FSP_40K', 'params.site_placement')][1].basis
    assert 'AQS-SITE-015' in b.computed[('node', 'LB_ED1', 'params.lb_design')][1].basis


def test_function_module_grid_purity():
    """The engine module holds no float literals and no I/O (the lint's rule)."""
    tree = ast.parse(inspect.getsource(ST))
    floats = [n.lineno for n in ast.walk(tree)
              if isinstance(n, ast.Constant) and isinstance(n.value, float)]
    opens = [n.lineno for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'open']
    assert floats == [] and opens == []

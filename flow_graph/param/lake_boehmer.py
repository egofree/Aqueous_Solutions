# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Lake Boehmer site design pass (AQS-SITE-015, task X-LOC-05).

Sizes the lake-restoration electrodialysis train at the lake_boehmer locale from the site
profile and the drivers. Transfer functions, per unit volume of dilute:

    SEC [kWh/m3] = F * dC_eq * U_cp / (CE * 3.6e6)
    dC_eq [mol_eq/m3] = 2 * (C_in - C_out) / 58.44 * 1000

with F = 96485.33212 C/mol [CODATA2018], 58.44 g/mol the molar mass of equivalent salt
(NaCl basis: one Na+ and one Cl- transported per mole of salt removed, one equivalent
each), U_cp the cell-pair voltage [STRATHMANN2004 practice range, A-M-438] and CE the
current efficiency [CAMPIONE2018, A-M-439]. The salt transport a module carries is

    R = j * A * CE / F  [mol_eq/s]

with j the current density [CAMPIONE2018, A-M-440] and A the membrane area per module
[A-M-441]; the duty divides by R, rounds up, and carries one spare module per stage
(A-M-451, the redundancy rule). Container counts are parametric: the electrodialysis
containers are ceil(installed modules / ed_modules_per_container) per stage, the utility
containers come from the driver table, and the battery containers are the charged store
per bess_container_kWh.

Power follows the repo D-PV rule: the balancing nameplate is sizing.power.pv_kWp at the
site-bound drivers, times the bound pv_oversize_factor. The battery usable store carries
the night energy plus the contingency days (A-M-443); charged = usable / round trip.

Everything reports what the drivers produce; nothing is hand-tuned. Values live in the
stamped params.lb_design and in AQS-SITE-015, never in prose.

    python3 -m flow_graph.param.lake_boehmer            # validate + print the sizing JSON
    python3 -m flow_graph.param.lake_boehmer --write    # stamp params.lb_design (lake_boehmer locale context only)
"""
import json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
GP = os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')
LB_UNITS = ('LB_INTAKE', 'LB_DEGAS', 'LB_DEGAS_SCRUB', 'LB_SOFTEN', 'LB_ED1', 'LB_ED2',
            'LB_PROD_TANK', 'LB_PROD_OUTLET', 'LB_BRINE_RETURN', 'LB_CHEM_STORE')
NACL = 58.44   # g/mol equivalent salt [CRC_COND class]


def v(d, k):
    return d[k]['value']


def compute(d, prof):
    """The site sizing from the loaded drivers and profile. Pure function of the inputs."""
    from . import portfolio as PF
    from .constants import F
    from .sizing.power import pv_kWp
    feed = v(d, 'WTR.lake-boehmer.feed_m3_d')
    tds_in = v(d, 'WTR.lake-boehmer.feed_tds_g_L')
    rec = v(d, 'WTR.lake-boehmer.ed_recovery')
    tds_mid = v(d, 'WTR.lake-boehmer.ed_stage1_product_tds_g_L')
    tds_out = v(d, 'WTR.lake-boehmer.product_tds_mg_L') / 1000.0
    U = v(d, 'WTR.lake-boehmer.ed_cellpair_voltage_V')
    ce = v(d, 'WTR.lake-boehmer.ed_current_efficiency')
    j = v(d, 'WTR.lake-boehmer.ed_current_density_A_m2')
    area = v(d, 'WTR.lake-boehmer.ed_membrane_area_m2')
    spare = int(v(d, 'WTR.lake-boehmer.ed_spare_modules_per_stage'))
    per_cont = v(d, 'WTR.lake-boehmer.ed_modules_per_container')
    dilute = feed * rec                    # product path, m3/d
    conc = feed - dilute                   # concentrate path, m3/d
    stages = []
    for name, t0, t1 in (('LB_ED1', tds_in, tds_mid), ('LB_ED2', tds_mid, tds_out)):
        dc_eq = 2.0 * (t0 - t1) / NACL * 1000.0          # mol_eq per m3 of dilute
        duty = dc_eq * dilute                            # mol_eq/d
        sec = F * dc_eq * U / (ce * 3.6e6)               # kWh/m3 of dilute
        r_mod = j * area * ce / F * 86400.0              # mol_eq/d per module
        n_duty = math.ceil(duty / r_mod)
        n_inst = n_duty + spare
        stages.append(dict(unit=name, dilute_m3_d=dilute, tds_in_g_L=t0, tds_out_g_L=t1,
                           delta_eq_m3=round(dc_eq, 2), duty_eq_d=round(duty, 1),
                           sec_kwh_m3=round(sec, 3), energy_kwh_d=round(sec * dilute, 1),
                           eq_per_module_d=round(r_mod, 1), modules_duty=n_duty,
                           modules_installed=n_inst,
                           rectifier_capacity_kw=round(n_inst * j * area * U / 1000.0, 1)))
    ed_kwh_d = round(sum(s['energy_kwh_d'] for s in stages), 1)
    aux_keys = ('WTR.lake-boehmer.aux_intake_kWh_m3', 'WTR.lake-boehmer.aux_degasser_kWh_m3',
                'WTR.lake-boehmer.aux_softening_kWh_m3', 'WTR.lake-boehmer.aux_dosing_cip_kWh_m3')
    aux = round(sum(v(d, k) for k in aux_keys), 2)
    aux_kwh_d = round(aux * feed, 1)
    p_kw = round((ed_kwh_d + aux_kwh_d) / 24.0, 2)
    eta = v(d, 'storage_round_trip')
    night = v(d, 'night_hours')
    y = v(d, 'pv_yield_kWh_kWp_d')
    der = v(d, 'pv_system_derate')
    ov = v(d, 'pv_oversize_factor')
    bal = pv_kWp(p_kw, night, eta, y, der) * PF.pv_factor(prof, eta)
    nameplate = math.ceil(bal * ov)
    cont = v(d, 'WTR.lake-boehmer.battery_contingency_days')
    usable = p_kw * night + p_kw * 24.0 * cont
    charged = usable / eta
    bess = math.ceil(charged / v(d, 'WTR.lake-boehmer.bess_container_kWh'))
    ed_cont = sum(math.ceil(s['modules_installed'] / per_cont) for s in stages)
    util = v(d, 'WTR.lake-boehmer.utility_containers')
    salt_in = feed * tds_in                                  # kg/d
    salt_prod = dilute * tds_out                             # kg/d
    salt_removed = dilute * (tds_in - tds_out)               # kg/d into the concentrate
    tds_conc = tds_in + salt_removed / conc                  # g/L concentrate
    salt_conc = conc * tds_conc                              # kg/d
    closure = salt_in - (salt_prod + salt_conc)              # kg/d, want 0
    return dict(
        site='lake_boehmer',
        flows=dict(feed_m3_d=feed, product_m3_d=dilute, concentrate_m3_d=conc,
                   feed_tds_g_L=tds_in, product_tds_g_L=tds_out, concentrate_tds_g_L=round(tds_conc, 1),
                   salt_feed_kg_d=round(salt_in, 1), salt_product_kg_d=round(salt_prod, 1),
                   salt_concentrate_kg_d=round(salt_conc, 1), salt_closure_kg_d=round(closure, 4),
                   salt_removed_from_dilute_kg_d=round(salt_removed, 1)),
        stages=stages,
        ed=dict(energy_kwh_d=ed_kwh_d, aux_kwh_m3_feed=aux, aux_kwh_d=aux_kwh_d,
                demand_kw=p_kw, ed_containers=ed_cont,
                utility_containers=util, utility_container_total=sum(util.values())),
        power=dict(demand_kw=p_kw, pv_balance_kWp=round(bal, 1), pv_nameplate_kWp=nameplate,
                   pv_yield_kWh_kWp_d=y, pv_system_derate=der, pv_oversize_factor=ov,
                   pv_winter_yield_kWh_kWp_d=v(d, 'WTR.lake-boehmer.pv_winter_yield_kWh_kWp_d'),
                   night_hours=night, storage_round_trip=eta,
                   battery_usable_kwh=round(usable, 1), battery_charged_kwh=round(charged, 1),
                   battery_contingency_days=cont, battery_containers=bess),
        containers_total=ed_cont + sum(util.values()) + bess,
        net_lake_salt_removal=dict(kg_d=0.0,
                                   statement='product and concentrate both return to the lake '
                                             '(owner decision, OPEN_QUESTIONS.md Q-037); only the scrubbed sulfide '
                                             'and the softening sludge leave, so the net lake salt removal is about zero'),
        basis=dict(sec='flow_graph/param/lake_boehmer.py module docstring (CODATA2018 F; '
                       'STRATHMANN2004 U_cp, A-M-438; CAMPIONE2018 CE and j, A-M-439/440)',
                   modules='R = j * A * CE / F; duty / R rounded up, one spare module per stage (A-M-451)',
                   pv='D-PV rule: pv_kWp at the site drivers times the bound pv_oversize_factor',
                   battery='night energy plus the contingency days (A-M-443) over storage_round_trip',
                   containers='ISO 668 1CC envelope (A-M-444); utility counts driver A-M-445; '
                              'battery store per container driver A-M-446'))


def _stage_nodes(c):
    return {s['unit']: s for s in c['stages']}


def stamp(g, c):
    """Stamp params.lb_design on the LB_* units and LIO_BAT. Idempotent; returns the count."""
    units = {n['unit_id']: n for n in g['nodes']}
    st = _stage_nodes(c)
    fl, ed, pw = c['flows'], c['ed'], c['power']
    designs = {
        'LB_INTAKE': dict(feed_m3_d=fl['feed_m3_d'], feed_tds_g_L=fl['feed_tds_g_L'],
                          feed_so4_mg_L=7500, site_safety_h2s_ppm=110,
                          basis='drivers WTR.lake-boehmer.* (A-M-434/435/436); AQS-SITE-015'),
        'LB_DEGAS': dict(air_water_ratio_vol=60, h2s_removal_target=0.95,
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
                               net_lake_salt_removal_kg_d=0.0, statement=c['net_lake_salt_removal']['statement'],
                               basis='owner decision Q-037; AQS-SITE-015'),
        'LB_BRINE_RETURN': dict(concentrate_m3_d=fl['concentrate_m3_d'],
                                concentrate_tds_g_L=fl['concentrate_tds_g_L'],
                                basis='A-M-437; carries the removed salt back to the lake (Q-037)'),
        'LB_CHEM_STORE': dict(services=['lime', 'soda ash', 'scrubber caustic', 'clean-in-place acid'],
                              basis='A-M-225 hold-time basis; resupply by road (AQS-SITE-015 logistics)'),
    }
    designs['LB_ED1'] = dict(st['LB_ED1'], basis=c['basis']['sec'])
    designs['LB_ED2'] = dict(st['LB_ED2'], basis=c['basis']['sec'])
    n = 0
    for u, design in designs.items():
        node = units.get(u)
        if node is None:
            raise SystemExit(f'lake_boehmer: node {u} not in the graph')
        p = node.setdefault('params', {})
        if p.get('lb_design') == design:
            continue
        p['lb_design'] = design
        n += 1
    lio = units.get('LIO_BAT')
    if lio is not None:
        d = dict(battery_usable_kwh=pw['battery_usable_kwh'], battery_charged_kwh=pw['battery_charged_kwh'],
                 battery_contingency_days=pw['battery_contingency_days'], night_hours=pw['night_hours'],
                 demand_kw=pw['demand_kw'], pv_nameplate_kWp=pw['pv_nameplate_kWp'],
                 battery_containers=pw['battery_containers'],
                 basis='Lake Boehmer locale design pass (AQS-SITE-015); supersedes the A-M-402 '
                       'interim carry at this locale')
        p = lio.setdefault('params', {})
        if p.get('lb_design') != d:
            p['lb_design'] = d
            n += 1
    return n


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    from . import site as S, drivers as DR, site_outputs as SO
    sid = S.site_id()
    d = DR.load(sid)
    prof = S.load_profile(sid)
    c = compute(d, prof)
    print(json.dumps(c, indent=1, sort_keys=True))
    if '--write' in argv:
        if sid != 'lake_boehmer':
            print('lake_boehmer: not the selected site; nothing written')
            return 0
        if not SO.in_locale_worktree(ROOT):
            raise SystemExit(f'AQS_SITE={sid}: the design pass writes only inside the locale worktree; '
                             f'run "python3 -m flow_graph.param.regen --site {sid}"')
        g = json.load(open(GP))
        n = stamp(g, c)
        if n:
            txt = json.dumps(g, indent=2)
            if open(GP, 'rb').read().endswith(b'\n'):
                txt += '\n'
            open(GP, 'w').write(txt)
        print(f'lake_boehmer: {n} node design stamp(s) written')
    return 0


if __name__ == '__main__':
    sys.exit(main())

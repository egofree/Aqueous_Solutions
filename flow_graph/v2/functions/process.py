"""The write_graph process family (family migration; reference writer
flow_graph/param/write_graph.py, command `process`, ledger row
`write_graph_process`, PHYSICS - the v2 solve kernel).

X-PAR-04 acid loop and EW cascade: the leach acid demand, the BMED stack
energy at the concentration-honest 2 M SEC (physics audit F-5, A-M-171), the
NaOH balance and the on-site caustic TF (A-M-475, route CHLOR_ALKALI), the two
MVR evaporator mass balances, the X-PAR-10 vent scrubber on the EVAP_ACID
column vent (AQS-DUTY-061), the Q-038 element-rate booking of the EW cascade
and its forming chain (AQS-ASSAY-001 sections 4 and 5; A-M-460), the EW cell
bounding currents, cell stamps and DC channel edges (AQS-DUTY-051,
AQS-ELEC-004), the EW rectifier stamps, and the SOL_ARK bus close on IA-PV-01.
The committed graph carries every field this family stamps; that committed
state is the golden this module reproduces.

Grid doctrine (owner ruling 2026-11-15): driver and seed values arrive as v1
floats and are converted at this boundary by dec() (exact Decimal of the
decimal repr); arithmetic is exact rational/Decimal; schema fields are
quantised half-even (Python round()'s tie rule) at the decimals the v1 schema
stores - 4 dp for the rate() book, 6 dp where v1 said so (IA-DC channels,
caustic streams, IA-FEED-MU), 3 dp for liquor volumes. The scale is named at
each call. Dimensionless physics constants port as integer scaled pairs with
the scale in the basis: Faraday 9648533212/100000 C/mol (CODATA2018), the
CIAAW2021 molar masses on a 1e-3 mol-g scale, the Perry 2-9/2-10 fit rows on a
1e-5 log scale, mmHg->kPa 133322/1000000, the site profile baseline constants
980665/100000 m/s2 and 101325/1000 kPa (flow_graph/param/site.py baseline),
pi on a 1e-15 scale. No float literals.

Disposition of the chains around this family (the strangler bridge):
- MVR evaporator DESIGN (blower/pump/trim kW, kWh/t, the column equilibrium):
  owned by the sizing_evap_design family (ledger row, depends_on this stage);
  this family reads the committed params.design block as its seed input.
- EW plate GEOMETRY and rectifier CHANNEL arithmetic: no separate ledger owner
  (their only graph stamps land in this stage's window), so the arithmetic of
  docs-authority/_ew_sizing.py and _rect_ew_sizing.py (AQS-DUTY-051 /
  AQS-ELEC-004 through sizing.electrochem and sizing.power.rectifier_channel)
  is ported here as pure functions.
- The on-site caustic TF (flow_graph/param/caustic.py) CHLOR_ALKALI route is
  ported; the CAUSTICIZE branch (it pulls the fluoro/sulfuric families) is
  deferred - the route driver is CHLOR_ALKALI, and the function records
  nothing if that ever changes.
- The X-ELS-02 load-basis block (shop tools, foundry duty cycle, habitation
  and fab tool lists, afterburner blower, dosing skid, GEO source-loop
  circulator) is deferred: its calculators belong to the doc_mfg_tools,
  foundry_poly, sizing_heat and geo_loop families per the ledger.
- Edge topology (from_unit_id re-points of the product edges, S17 presence)
  is builder/composer work: the committed graph already carries it, so this
  family asserts the seed topology instead of writing it.

The v1 machinery (subprocess spawning, note-freeze idempotence, pass loop,
bus re-stamp guards) does not migrate: assignment replaces the field and its
provenance in full, and the IA-BAG-01 note-owner protocol (F-20261110-08) is
ported as the value-only update it is. A solve without the driver payload
records nothing, so the bridge solve and the check stay byte-faithful to the
seed.
"""
import math
from decimal import Decimal, ROUND_HALF_EVEN

from flow_graph.v2.registry import fn

STAGES = 'process'                                            # family tag in provenance rows
D = Decimal
D0, D1 = Decimal(0), Decimal(1)
F = Decimal(9648533212) / Decimal(100000)                     # C/mol, CODATA2018 (scale 1e-5)
G_SITE = Decimal(980665) / Decimal(100000)                    # m/s2, site profile baseline
P_SITE_KPA = Decimal(101325) / Decimal(1000)                  # kPa, site profile baseline process space
PI = Decimal(3141592653589793) / Decimal(10) ** 15            # pi (scale 1e-15)
MHCL, MH2O, MNAOH = Decimal('36.461'), Decimal('18.015'), Decimal('39.997')
M_NACL = Decimal('58.443')                                    # caustic.py NaCl book (CIAAW2021)
TAG = 'X-PAR acid-loop decision (AQS-PAR-001 §3)'
NT = TAG + '; NaOH balance (owner decision 2026-10-15)'
VT = TAG + '; X-PAR-10 vent scrubber (AQS-DUTY-061)'
MET = 'X-PAR-02 Q-038 element-rate rebasis (AQS-ASSAY-001 sections 4 and 5; A-M-460)'
TAG24 = 'X-PAR F-24'
CATAG = 'X-PAR-06 TF: on-site sodium hydroxide (A-M-475)'
ELEC_IN = ('S17-BMED', 'S17-EW', 'SF-EVAP_ACID', 'SF-EVAP_BASE', 'SF-EVAP_ACID_VS',
           'SF-GEO_HP_CLOSED_LOOP')
# The cell-to-element booking map (flow_graph/param/ew_cells.py, AQS-ASSAY-001
# table 4.1; Q-038 owner ruling 2026-11-05). Element molar masses CIAAW2021,
# 1e-3 g/mol scale; valences per USBM_CL_EW chloride EW.
EW_CELLS = {1: ('Au', 3), 2: ('Ag', 1), 3: ('Cu', 2), 4: ('Pb', 2), 5: ('Sn', 2),
            6: ('Ni', 2), 7: ('Fe', 2), 8: ('Cd', 2), 9: ('Zn', 2)}
M_EL = {'Au': Decimal('196.97'), 'Ag': Decimal('107.87'), 'Cu': Decimal('63.546'),
        'Pb': Decimal('207.2'), 'Sn': Decimal('118.71'), 'Ni': Decimal('58.693'),
        'Fe': Decimal('55.845'), 'Cd': Decimal('112.41'), 'Zn': Decimal('65.38')}
# Perry's 7th ed. tables 2-9 (water) and 2-10 (HCl) over aqueous HCl:
# log10 p[mmHg] = A - B/T per wt% row, linear in log p between rows
# [PERRY7_HCL_VLE]. A on a 1e-5 scale, B integer kelvin.
VLE_W = {6: (899156, 2282), 10: (899864, 2295), 14: (897075, 2300), 18: (898014, 2323),
         20: (897877, 2334), 22: (902708, 2363), 24: (896022, 2356)}
VLE_H = {2: (1180370, 4736), 4: (1164000, 4471), 6: (1121440, 4202), 8: (1104060, 4042),
         10: (1093110, 3908), 12: (1079000, 3765), 14: (1069540, 3636), 16: (1062610, 3516),
         18: (1049570, 3376), 20: (1038330, 3245), 22: (1031720, 3125), 24: (1021850, 2995)}
MMHG_KPA = Decimal(133322) / Decimal(1000000)                 # Torr -> kPa (scale 1e-6)


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
    """round(x) as v1 wrote it: half-even to an integer."""
    return int(Decimal(x).quantize(D1, rounding=ROUND_HALF_EVEN))


def fmt(x, dp):
    """The f'{x:.dpf}' text of an exact value (half-even at dp)."""
    return f'{Decimal(x).quantize(D1.scaleb(-dp), rounding=ROUND_HALF_EVEN):f}'


def _prov(basis, ref=None):
    from flow_graph.v2.model import Prov
    return Prov(STAGES, basis, ref)


def _set(b, uid, path, value, basis, ref=None):
    b.set_node_field(uid, path, value, _prov(basis, ref))


def _rate(b, sid, value, unit, note, basis, ref=None):
    """The v1 rate() book on an edge: {value, unit, status, note} in that key
    order (the serialized order the committed graph carries)."""
    b.set_edge_rate(sid, {'value': value, 'unit': unit, 'status': 'study', 'note': note},
                    _prov(basis, ref))


def _edge_field(b, sid, path, value, basis, ref=None):
    """An edge field beyond 'rate' (params.*, rate.note): the same overlay the
    builder records rates through; model.Builder exposes only the rate path, so
    this writes the overlay directly."""
    b.computed[('edge', sid, path)] = (value, _prov(basis, ref))


def _edge_value(b, sid, value, basis, ref=None):
    """Value-only update on an existing rate (the note-owner/seed-note books:
    IA-FEED-MU, IA-BAG-01, IA-GOODS-SHIP band, IA-PV-01)."""
    seed = dict(b.edges[sid]['rate'])
    seed['value'] = value
    b.set_edge_rate(sid, seed, _prov(basis, ref))


def _lp(tab, w, t):
    """One Perry fit row interpolation (integer scaled pairs; exact rational)."""
    ks = sorted(tab)
    if w <= ks[0]:
        a, bb = tab[ks[0]]
        return Decimal(a) / D1.scaleb(5) - bb / t
    for i in range(len(ks) - 1):
        if ks[i] <= w <= ks[i + 1]:
            a1, b1 = tab[ks[i]]
            a2, b2 = tab[ks[i + 1]]
            l1 = Decimal(a1) / D1.scaleb(5) - b1 / t
            l2 = Decimal(a2) / D1.scaleb(5) - b2 / t
            f = (w - ks[i]) / (ks[i + 1] - ks[i])
            return l1 + f * (l2 - l1)
    a, bb = tab[ks[-1]]
    return Decimal(a) / D1.scaleb(5) - bb / t


def _faraday_current(m_kg_d, m_g_mol, z, ce):
    """I = m z F / (M t CE) [CODATA2018, SCHLESINGER2011]."""
    return m_kg_d * 1000 / m_g_mol * z * F / 86400 / ce


def _dc_power_kw(i_a, v):
    return i_a * v / 1000


def _cathode_count(i_a, j_a_m2, plate_m2):
    return max(1, math.ceil(i_a / (j_a_m2 * plate_m2)))


def _rectifier_channel(i_a, v_cell, v_drop, eff, frames, margin, v_rated):
    """sizing.power.rectifier_channel [USBM_CL_EW]: frame = smallest standard
    >= margin x I; P_dc = I (V_cell + V_drop); P_ac = P_dc / eff."""
    need = i_a * margin
    rated = next(f for f in frames if f >= need)
    p_dc = i_a * (v_cell + v_drop) / 1000
    return {'need_A': need, 'rated_A': rated, 'rated_kW': rated * v_rated / 1000,
            'Pdc_kW': p_dc, 'Pac_kW': p_dc / eff}


def _vent_case(feed_kg_d, w_cond_pct, d):
    """The X-PAR-10 vent-scrubber case (sizing.scrubber.vent_scrubber
    [PERRY9_ABS, PERRY9_DIFF, PERRY7_HCL_VLE, WEISS1970]; A-M-111 drivers).
    Pure: the Perry log fits, the gas book and the absorption masses."""
    v = lambda k: dec(d[k]['value'])
    t_c = v('vs_T_C')
    tk = t_c + Decimal('273.15')
    ph = (D(10) ** _lp(VLE_H, w_cond_pct, tk)) * MMHG_KPA
    pw = (D(10) ** _lp(VLE_W, w_cond_pct, tk)) * MMHG_KPA if w_cond_pct >= 6 else None
    # (the sub-6 wt% branch takes the IAPWS psat - the upset design case this
    # family stamps always carries a column condensate >= 6 wt%; the normal
    # case and its psat belong to the vent-scrubber doc family)
    p = P_SITE_KPA
    air = feed_kg_d * v('vs_air_mg_kg') / D(10) ** 6 / Decimal('28.96') * 1000   # mol/d [WEISS1970]
    y_w = pw / p
    y_h = ph / p
    n_tot = air / (1 - y_w - y_h)
    hcl_mol = n_tot * y_h
    w_mol = n_tot * y_w
    vent = (air * Decimal('28.96') + w_mol * MH2O + hcl_mol * MHCL) / 1000
    y_in = y_h * D(10) ** 6
    ntu = (y_in / v('vs_y_out_ppm')).ln() if y_in > v('vs_y_out_ppm') else D0
    dp_mm = v('vs_dp_mm')
    d_col = dp_mm * v('vs_d_over_dp') / 1000
    # gas-film HTU at this loading: Fuller-Schettler-Giddings diffusivity
    # (T^1.75 and the cube-root volumes through exact Decimal powers), Fick
    # film at half the packing size [TREYBAL3]
    dg = D(10) ** -3 * (tk ** Decimal('1.75')) * (
        (1 / MHCL + 1 / Decimal('28.96')).sqrt()) / (
        (p / Decimal('101.325')) * (Decimal('23.31') ** (D1 / 3) + Decimal('19.7') ** (D1 / 3)) ** 2) / D(10) ** 4
    g_flux = n_tot / 86400 / (PI * d_col * d_col / 4)
    c_mol = p * 1000 / (Decimal('8.314') * tk)
    htu = g_flux / (c_mol * dg / (dp_mm / 2000) * v('vs_a_m2_m3'))
    z_bed = max(htu * ntu * v('vs_margin'), Decimal('0.5'))    # 0.5 m minimum bed
    packed_mm = math.ceil(z_bed * 1000 / 100) * 100
    l_min = v('vs_mwr') * v('vs_a_m2_m3') * PI * d_col * d_col / 4   # m3/h wetting
    naoh_wt = v('bmed_product_wt_base')
    naoh_mol = hcl_mol * v('vs_naoh_excess')
    naoh_soln = naoh_mol * Decimal(40) / 1000 / naoh_wt        # 40.0: the scrubber NaOH book
    hcl_kg = hcl_mol * MHCL / 1000
    offgas = vent - hcl_kg + hcl_mol * (v('vs_y_out_ppm') / y_in) * MHCL / 1000
    pump = l_min / 3600 * 1000 * G_SITE * dec(d['DIGESTER.metals-leach-train.acid-base-regen.EVAP_ACID_VS.vs_pump_head_m']['value']) \
        / dec(d['DIGESTER.metals-leach-train.acid-base-regen.EVAP_ACID_VS.vs_pump_eta']['value']) / 1000
    dn = next(x for x in d['DIGESTER.metals-leach-train.acid-base-regen.EVAP_ACID_VS.vs_DN_ladder_mm']['value']
              if x >= d_col * 1000)
    sump_l = dec(d['DIGESTER.metals-leach-train.acid-base-regen.EVAP_ACID_VS.vs_sump_L']['value'])
    return dict(vent_kg_d=vent, y_in_ppm=y_in, naoh_mol_d=naoh_mol, naoh_soln_kg_d=naoh_soln, sump_L=sump_l,
                spent_kg_d=naoh_soln + hcl_kg, offgas_kg_d=offgas, recirc_m3_h=l_min,
                pump_kW=pump, DN=dn, packed_mm=packed_mm,
                height_mm=packed_mm + dec(d['DIGESTER.metals-leach-train.acid-base-regen.EVAP_ACID_VS.vs_head_allowance_mm']['value']))


def _core(b, inputs):
    """The process solve kernel: the port of solver.solve() minus the roof
    spawn (the power family's input), on exact Decimal arithmetic. Returns the
    chain values, or None without the driver payload (the bridge contract)."""
    drv = inputs.get('drivers')
    if drv is None:
        return None
    v = lambda k: dec(drv[k]['value'])
    dvs = lambda k: str(dec(drv[k]['value']))
    R = {sid: dec(e['rate']['value']) for sid, e in b.edges.items()
         if isinstance((e.get('rate') or {}).get('value'), (int, float))}

    # leach acid demand: oxide + n HCl -> chloride + water [GREENWOOD, LUNAR_SOURCEBOOK]
    m_ox = {'Al2O3': Decimal('101.961'), 'CaO': Decimal('56.077'),
            'MgO': Decimal('40.304'), 'FeO': Decimal('71.844')}      # CIAAW2021, 1e-3 scale
    n_hcl = {k: dec(x) for k, x in drv['hcl_stoich']['value'].items()}
    feed_ox = v('feed_rate_kg_d') * v('feed_case_A_silicate_oxide')
    mol_ox = {o: feed_ox * dec(f) * v('case_A_leach_extent') * 1000 / m_ox[o]
              for o, f in drv['case_A_oxide_fractions']['value'].items()}
    hcl_mol = sum((mol_ox[o] * n_hcl[o] for o in mol_ox), D0)
    assert v('acid_conc_design_wt') < v('hcl_azeotrope_wt'), 'acid loop above the HCl azeotrope'

    # BMED stack: salt split 1:1, energy at the concentration-honest 2 M SEC
    # (F-5, A-M-171 restated); the in-house triplet voltage [STRATHMANN2004,
    # CRC_COND] stays note data at its own seawater-brine concentration
    base_kg = hcl_mol * MNAOH / 1000
    j = v('bmed_j_A_m2') / D(10000)
    gap = v('bmed_spacer_mm') / 10
    kappas = drv['bmed_kappa_S_cm']['value']
    sol = v('bmed_spacer_shadow') * gap * sum((1 / dec(x) for x in
        (kappas['salt'], kappas['base'], kappas['acid'])), D0)
    v_mem = 2 * j * v('bmed_R_mono_ohm_cm2')
    v_end = v('bmed_V_end_per_stack_V') / v('bmed_cells_per_stack_max')
    v_model = v('bmed_V_bpm_V') + v_mem + sol * j + v_end
    v_pilot = v('bmed_sec_pilot_kWh_kg') * Decimal(3600000) * MNAOH / 1000 * v('bmed_CE') / Decimal('96485.33212')
    v_design = max(v_model, v_pilot)
    sec = v('bmed_sec_kWh_per_kg_base')
    kw_bmed = sec * base_kg / 24

    # evaporator mass balances (solver.evap); MVR kW from the sizing_evap_design
    # family's committed design block (the strangler seed, ledger row sizing_evap_design)
    def evap_mass(solute, w_in, w_out, added=D0, added_water=D0, acid=False):
        assert w_out > w_in
        c = v('evap_cond_hcl_wt') if acid else D0
        prod = (solute + added) / w_out
        feed = prod * (w_out - c) / (w_in - c) if c else solute / w_in
        water = feed + added + added_water - prod
        return dict(solute=solute, added=added, added_water=added_water, feed=feed,
                    product=prod, water=water)

    ea = evap_mass(R['IA-ACID-01'] * v('acid_conc_design_wt'),
                   v('bmed_product_wt_acid'), v('acid_conc_design_wt'), acid=True)
    up = _vent_case(ea['feed'], dec(_seed_param(b, 'EVAP_ACID', 'design.column.y_eq_body_pct')), drv)
    nb_ppt = hcl_mol * v('ppt_naoh_per_cl')
    sio2 = max(D0, R['IA-GLASS-03'] - R['S08G']) * 1000 / Decimal('60.083')
    nb_dig = sio2 * v('digest_naoh_per_sio2')
    nb_acex = R.get('IA-BMIM', D0) * 1000 / Decimal('174.67')   # X-PAR-14, A-M-162
    nb_mk = max(D0, nb_ppt + nb_dig + up['naoh_mol_d'] + nb_acex - hcl_mol)
    # on-site caustic make-up (flow_graph/param/caustic.py, A-M-475): recovery
    # first; the CHLOR_ALKALI route books the halite top-up and the purge bleed
    route = drv['naoh_route']['value']
    wc = v('ca_catholyte_wt')
    pw_liq = 1 / (v('na_purge_recycle_frac') / wc + (1 - v('na_purge_recycle_frac')) / wc)
    makeup_kg = nb_mk * MNAOH / 1000 / pw_liq
    ca = None
    if route == 'CHLOR_ALKALI':
        n_kmol = nb_mk / 1000
        rec, top = n_kmol * v('na_purge_recycle_frac'), n_kmol * (1 - v('na_purge_recycle_frac'))
        naoh_kg = n_kmol * MNAOH
        hal = top * M_NACL
        halite = hal / v('halite_ore_purity')
        liquor = naoh_kg / wc
        dc_kwh_kg = v('ca_cell_V') * F / (MNAOH / 1000 * v('ca_CE')) / Decimal(3600000)
        kw_cell = n_kmol * MNAOH * dc_kwh_kg / 24 / v('rect_efficiency')
        ca = dict(recycle=rec * M_NACL, bleed=top * M_NACL, halite_ore=halite,
                  residue=halite - hal, liquor=liquor, naoh=naoh_kg,
                  cl2=n_kmol * Decimal('35.453'), h2=n_kmol * Decimal('1.008'),
                  h2o=liquor + n_kmol * Decimal('35.453') + n_kmol * Decimal('1.008')
                      + (halite - hal) - halite - rec * M_NACL,   # well water closes the unit
                  kw_cell=kw_cell, product_wt=pw_liq, route=route)
    eb = evap_mass(base_kg - up['naoh_mol_d'] * MNAOH / 1000,
                   v('bmed_product_wt_base'), v('base_conc_design_wt'),
                   added=makeup_kg * pw_liq, added_water=makeup_kg * (1 - pw_liq))

    # EW cascade: bounding currents at the element envelope (Q-038; Q-041
    # arrangement driver) and the Q-038 booked rates (solver.ew_products)
    ce = v('ew_current_efficiency_design')
    v_cell, v_drop = v('ew_cell_voltage_V'), v('ew_bus_drop_V')
    arr = drv['ew_minor_metal_arrangement']['value']
    assert arr in ('selective', 'merged'), arr
    minor = tuple(int(x) for x in drv['ew_minor_metal_cells']['value'])
    els = _seed_edge(b, 'IA-FEED-01')['params']['assay_envelope']['element_envelope']['elements']
    rec_leach = v('ew_leach_recovery_design')
    feed_env = R['IA-FEED-01']
    m_blend = min(M_EL[EW_CELLS[m][0]] for m in minor)          # nickel basis (A-M-494)
    ew = {}
    for n in range(1, 10):
        el, z = EW_CELLS[n]
        env_key = el if el in ('Fe', 'Cu', 'Au', 'Ag') else 'other_plateable'
        dep = feed_env * dec(els[env_key]['fraction']) * rec_leach
        host = arr == 'merged' and n == minor[0]
        idle = arr == 'merged' and n in minor and not host
        i_a = D0 if idle else _faraday_current(dep, m_blend if host else M_EL[el], z, ce)
        ew[n] = dict(metal=el, I=i_a, P=_dc_power_kw(i_a, v_cell),
                     P_bus=_dc_power_kw(i_a, v_cell + v_drop))
    dc_total = sum((ew[n]['P_bus'] for n in ew), D0)
    rect = dict(I=sum((ew[n]['I'] for n in ew), D0), P_dc=dc_total,
                P_ac=dc_total / v('rect_efficiency'))

    # Q-038 booked deposit rows (X-QA-04, A-M-470 even minor split)
    ref_els = _seed_edge(b, 'IA-FEED-01')['params']['assay_envelope']['reference_point_elements']
    r6 = lambda x: dec(x).quantize(D1.scaleb(-6), rounding=ROUND_HALF_EVEN)
    dep_ref = {n: r6(feed_env * dec(ref_els[EW_CELLS[n][0] if n not in minor else 'other_plateable']) * rec_leach)
               for n in EW_CELLS}
    for n in minor:
        dep_ref[n] = r6(feed_env * dec(ref_els['other_plateable']) * rec_leach / len(minor))
    cu = dec(dep_ref[3]).quantize(D1.scaleb(-4), rounding=ROUND_HALF_EVEN)
    blend = sum((dep_ref[n] for n in minor), D0)
    s57 = dec(cu / 2).quantize(D1.scaleb(-4), rounding=ROUND_HALF_EVEN)
    mill = s57
    atom = dec(blend).quantize(D1.scaleb(-4), rounding=ROUND_HALF_EVEN)
    remelt = dec(blend * D(10) / 100).quantize(D1.scaleb(-4), rounding=ROUND_HALF_EVEN)
    sheet = dec(s57 + mill + atom - remelt).quantize(D1.scaleb(-4), rounding=ROUND_HALF_EVEN)
    fume = dec(s57 * v('wire_melt_fume_frac')).quantize(D1.scaleb(-4), rounding=ROUND_HALF_EVEN)
    s58 = dec((s57 - fume) * D(9) / 10).quantize(D1.scaleb(-4), rounding=ROUND_HALF_EVEN)
    wloss = dec((s57 - fume) / 10).quantize(D1.scaleb(-4), rounding=ROUND_HALF_EVEN)
    s60 = dec(blend * D(9) / 10).quantize(D1.scaleb(-4), rounding=ROUND_HALF_EVEN)
    wear = v('POLYMERS.textile.textile_kg_person_yr') * v('san_crew') / 365
    wear_r = dec(wear).quantize(D1.scaleb(-4), rounding=ROUND_HALF_EVEN)
    hopper_in = R['S61'] + R['FRASS'] + R['IA-LEACH-HOP'] + wear_r
    feed_mu = (R['IA-FEED-01'] - hopper_in).quantize(D1.scaleb(-6), rounding=ROUND_HALF_EVEN)
    assert feed_mu > 0, 'hopper make-up negative: loop receipts exceed the design feed'

    return dict(v=v, dvs=dvs, R=R, drv=drv, hcl_mol=hcl_mol, base_kg=base_kg,
                v_design=v_design, sec=sec, kw_bmed=kw_bmed, ea=ea, eb=eb, up=up,
                nb=dict(ppt=nb_ppt, dig=nb_dig, acex=nb_acex, makeup=nb_mk,
                        makeup_kg=makeup_kg),
                ca=ca, pw_liq=pw_liq, ew=ew, rect=rect, dc_total=dc_total,
                minor=minor, dep_ref=dep_ref, cu=cu, blend=blend, sheet=sheet,
                s57=s57, s58=s58, s59=mill, s60=s60, fume=fume, wloss=wloss,
                wear=wear_r, feed_mu=feed_mu, ce=ce, v_cell=v_cell, v_drop=v_drop,
                arr=arr)


def _seed_param(b, uid, dotted):
    """A seed value another family owns (the strangler read)."""
    cur = b.nodes[uid]['params']
    for part in dotted.split('.'):
        cur = cur[part]
    return cur


def _seed_edge(b, sid):
    return b.edges[sid]


def _seed_rate(b, sid):
    return dec(b.edges[sid]['rate']['value'])


@fn('process_acid_loop', 'X-PAR-04 acid loop and NaOH balance: leach acid demand [GREENWOOD], BMED '
    'stack at the 2 M SEC (F-5, A-M-171), NaOH make-up demand, AQS-PAR-001')
def process_acid_loop(b, inputs):
    s = _core(b, inputs)
    if s is None:
        return
    v, dvs = s['v'], s['dvs']
    basis = 'BMED energy at the 2 M SEC (F-5, A-M-171); NaOH balance (owner decision 2026-10-15); AQS-PAR-001'
    kw = q(s['kw_bmed'], 4)
    note = (f"{TAG}. BMED stack: {fmt(s['base_kg'], 2)} kg/d NaOH x {fmt(s['sec'], 1)} kWh/kg at the 2 M product "
            f"(EDBM_WHEY_2021 quotes 6.7 kWh/kg at 2 M; the design basis is the product's own concentration, "
            f"physics audit F-5, A-M-171) / 24 h. The in-house triplet voltage {fmt(s['v_design'], 2)} V at CE "
            f"{dvs('bmed_CE')} (STRATHMANN2004, CRC_COND, EDBM_PILOT_2023; AQS-DUTY-068) is model data at its own "
            f"seawater-brine concentration. Solver flow_graph/param/solver.py bmed().")
    _set(b, 'BMED_ACID', 'continuous_kw.value', kw, basis)
    _set(b, 'BMED_ACID', 'continuous_kw.note', note, basis)
    _rate(b, 'S17-BMED', kw, 'kW', f'{TAG}. 480 V feed equal to BMED_ACID continuous_kw.', basis)
    x12 = b.nodes['CRYO_O2']['params'].get('x_par_12_base')
    if x12:
        _set(b, 'CRYO_O2', 'params.x_par_12_base.BMED_kW', kw, basis + '; X-PAR-12 rescaling base follows the BMED energy')
        _set(b, 'CRYO_O2', 'params.x_par_12_base.S17-BMED', kw, basis + '; X-PAR-12 rescaling base follows the BMED energy')
    wb = v('base_conc_design_wt')
    wtxt = fmt(wb * 100, 0)
    nb = s['nb']
    _rate(b, 'IA-BASE-PPT', q(nb['ppt'] * MNAOH / 1000 / wb, 4), 'kg/d',
          f"{NT}. {fmt(nb['ppt'], 0)} mol/d NaOH, one per leached chloride (GREENWOOD), as {wtxt} wt%.", basis)
    _rate(b, 'IA-BASE-01', q(nb['dig'] * MNAOH / 1000 / wb, 4), 'kg/d',
          f"{NT}. {fmt(nb['dig'], 1)} mol/d NaOH = 2 x SiO2 dissolved (IA-GLASS-03 less S08G, all as SiO2, "
          f"bounding; GREENWOOD), as {wtxt} wt%.", basis)
    if 'IA-ACEX-NAOH' in b.edges:
        _rate(b, 'IA-ACEX-NAOH', q(nb['acex'] * MNAOH / 1000 / wb, 4), 'kg/d',
              f"{NT}. {fmt(nb['acex'], 2)} mol/d NaOH, one per [Bmim]Cl, OH-form resin regeneration "
              f"(X-PAR-14, A-M-162), as {wtxt} wt%.", basis)
    _rate(b, 'IA-DIG-LIQ', q(nb['dig'] * MNAOH / 1000 / wb, 4), 'kg/d',
          f'{NT}. Silicate liquor equal to the digest NaOH draw (digest closes on IA-GLASS-03, S08G, '
          f'IA-SIL-SRC, IA-SIC-IN).', basis)


@fn('process_caustic_tf', 'X-PAR-06 TF: on-site sodium hydroxide (A-M-475), flow_graph/param/caustic.py, '
    'recovery first (owner decisions t59u/t61u), route CHLOR_ALKALI (Q-035, A-M-478)')
def process_caustic_tf(b, inputs):
    s = _core(b, inputs)
    if s is None or s['ca'] is None:
        return                                   # CAUSTICIZE branch: deferred to its route families
    ca = s['ca']
    route = ca['route']
    streams = (('IA-HALITE-MU', 'NORTH_DOCK', 'NAOH_PLANT', 'halite_ore', ca['halite_ore']),
               ('IA-NA-RECYCLE', 'LEACH_CSTR_1', 'NAOH_PLANT', 'recycle', ca['recycle']),
               ('IA-NAOH-CL2-SHIP', 'NAOH_PLANT', 'NORTH_DOCK', 'cl2', ca['cl2']),
               ('IA-NAOH-H2', 'NAOH_PLANT', 'HDR_H2', 'h2', ca['h2']),
               ('IA-NAOH-H2O', 'GW_INTAKE', 'NAOH_PLANT', 'h2o', ca['h2o']),
               ('IA-NAOH-RESIDUE', 'NAOH_PLANT', 'NORTH_DOCK', 'residue', ca['residue']),
               ('IA-NAOH-LIQ', 'NAOH_PLANT', 'EVAP_BASE', 'liquor', ca['liquor']))
    basis = 'on-site NaOH make-up, membrane chlor-alkali (A-M-475, A-M-478; ULLMANN_NAOH), route ' + route
    for sid, a, zb, key, val in streams:
        e = b.edges[sid]
        assert (e['from_unit_id'], e['to_unit_id']) == (a, zb), f'caustic: {sid} names another stream'
        assert e.get('presence') == 'present', f'caustic: {sid} presence drifted'
        note = f'{CATAG}: {key} = {fmt(val, 4)} kg/d (caustic.py, route {route}).'
        _rate(b, sid, q(val, 6), 'kg/d', note, basis)
    _edge_field(b, 'IA-NAOH-LIQ', 'params.NaOH_kg_d', q(ca['naoh'], 6), basis)
    _edge_field(b, 'IA-NAOH-LIQ', 'params.NaOH_wt', q(ca['product_wt'], 6), basis)
    _rate(b, 'IA-NA-PURGE', q(ca['bleed'], 6), 'kg/d',
          f'{CATAG}: the make-up sodium leaves the leach as sodium chloride, one NaCl per NaOH; the fraction '
          f'na_purge_recycle_frac is recovered to NAOH_PLANT on IA-NA-RECYCLE and the rest is bled here '
          f'(recovery first, t61u; route {route}).', basis)
    if 'IA-NAOH-MU' in b.edges:
        _rate(b, 'IA-NAOH-MU', float(0), 'kg/d',
              'Retired 2026-10-29 (owner decision t59u: no imports except waste or raw ore). The make-up is '
              'made on site by NAOH_PLANT (A-M-475).', basis)
    why = f'membrane cells {fmt(ca["kw_cell"], 4)} kW (ca_cell_V x F / (M x ca_CE) through the rectifier)'
    _set(b, 'NAOH_PLANT', 'continuous_kw.value', q(ca['kw_cell'], 4), basis)
    _set(b, 'NAOH_PLANT', 'continuous_kw.note', f'{CATAG}: {why} (caustic.py, route {route}).', basis)
    _rate(b, 'SF-NAOH_PLANT', q(ca['kw_cell'], 4), 'kW', f'{CATAG}: feed equal to NAOH_PLANT continuous_kw.', basis)


def _evap_seed_design(b, uid):
    """The MVR design numbers of the sizing_evap_design family (the strangler
    seed): specific energy, blower/recirculation/trim kW, total kW."""
    dsg = b.nodes[uid]['params']['design']
    return dsg['kWh_per_t'], dsg['comp_elec_kW'], dsg['pump_kW'], dsg['trim_kW'], dsg['total_kW']


@fn('process_evaporators', 'X-MFG-30 MVR evaporator mass balances (X-PAR-04); the MVR design kW from the '
    'sizing_evap_design family (AQS-DUTY-060, A-M-106); IA-BMED-04 brine closure')
def process_evaporators(b, inputs):
    s = _core(b, inputs)
    if s is None:
        return
    v, dvs = s['v'], s['dvs']
    basis = 'MVR evaporator mass balance (solver.evap); in-house MVR design X-MFG-30 (AQS-DUTY-060); AQS-PAR-001'
    for side, key, src, sa in (('ACID', 'ea', 'BMED_ACID', 'HCl'), ('BASE', 'eb', 'BMED_BASE', 'NaOH')):
        e = s[key]
        w_in, w_out = v('bmed_product_wt_' + side.lower()), v('acid_conc_design_wt' if side == 'ACID'
                                                              else 'base_conc_design_wt')
        kwh_t, comp, pump, trim, kw = (dec(x) for x in _evap_seed_design(b, 'EVAP_' + side))
        note = (f'{TAG}. MVR evaporator, {sa} from 2 M ({fmt(w_in * 100, 2)} wt%) to {fmt(w_out * 100, 0)} wt%'
                + (f' (below the HCl azeotrope {fmt(v("hcl_azeotrope_wt") * 100, 1)} wt%, PERRY9_HCL)'
                   if side == 'ACID' else '')
                + f'; water off {fmt(e["water"], 1)} kg/d x {str(dec(kwh_t))} kWh/t (in-house MVR design X-MFG-30, '
                + f'AQS-DUTY-060: blower {fmt(comp, 3)} kW, recirculation {fmt(pump, 3)} kW, trim {fmt(trim, 3)} kW) '
                + f'= {fmt(kw, 2)} kW. Study.')
        uid = 'EVAP_' + side
        nb_note = (f'{sa} concentrator after {src} ({TAG}). Wetted parts per ULLMANN_HCL (impregnated graphite or '
                   f'fluoropolymer-lined; study).' if side == 'ACID'
                   else f'{sa} concentrator after {src} ({TAG}). Nickel or fluoropolymer-lined wetted parts (study).')
        _set(b, uid, 'notes', nb_note, basis)
        _set(b, uid, 'continuous_kw.value', q(kw, 4), basis)
        _set(b, uid, 'continuous_kw.note', note, basis)
        _set(b, uid, 'params.presence', 'present', basis)
        _set(b, uid, 'params.water_off_kg_d', q(e['water'], 2), basis)
        _set(b, uid, 'params.feed_wt', float(dec(w_in)), basis)
        _set(b, uid, 'params.product_wt', float(dec(w_out)), basis)
        _set(b, uid, 'params.mvr_kWh_per_t', float(dec(kwh_t)), basis)
        _rate(b, f'IA-{uid}-FEED', q(e['feed'], 4), 'kg/d',
              f'{TAG}. {fmt(e["solute"], 2)} kg/d {sa} / {dvs("bmed_product_wt_" + side.lower())}.', basis)
        _rate(b, f'SF-{uid}', q(kw, 4), 'kW', f'{TAG}. 480 V feed equal to {uid} continuous_kw.', basis)
        _rate(b, f'SQ-{uid}', q(kw, 4), 'kW',
              f'{TAG}. Compressor work leaves as heat (A-M-086); to the Q4 loop (HEAT_SINK retired at Rev AC; '
              f'gap audit 2026-10-31). Layer thermal (F-3 fix, A-M-454): the MVR compressor heat is heat, not a '
              f'mixed energy stream, so the X-THM-01 Q4 ledger counts it.', basis)
        assert b.edges[f'IA-{uid}-COND']['from_unit_id'] == uid
        assert all(b.edges[p]['from_unit_id'] == uid for p in
                   (('IA-ACID-01',) if side == 'ACID' else ('IA-BASE-01', 'IA-BASE-PPT')))
    _rate(b, 'IA-EVAP_BASE-COND', q(s['eb']['water'], 4), 'kg/d',
          f'{TAG}. Water evaporated, condensed and returned to BMED_BASE.', basis)
    # BMED_BASE closes on its brine feed: out = IA-BMED-04 + condensate
    _rate(b, 'IA-BMED-04',
          q(s['eb']['feed'] + _seed_rate(b, 'IA-BMED-02') + s['up']['naoh_soln_kg_d'] - s['eb']['water'], 4),
          'kg/d', f'{TAG}. Brine to BMED_BASE closing the stack balance with the condensate return.', basis)


@fn('process_vent_scrubber', 'X-PAR-10 vent scrubber EVAP_ACID_VS on the EVAP_ACID column vent '
    '(AQS-DUTY-061, A-M-111): Perry 2-9/2-10 vent equilibrium, packed-bed absorption, NaOH bleed')
def process_vent_scrubber(b, inputs):
    s = _core(b, inputs)
    if s is None:
        return
    up = s['up']
    basis = 'X-PAR-10 vent scrubber (AQS-DUTY-061, A-M-111; PERRY9_ABS, PERRY7_HCL_VLE, WEISS1970); AQS-PAR-001'
    uid = 'EVAP_ACID_VS'
    _set(b, uid, 'notes',
         'Packed PVC alkali scrubber on the EVAP_ACID column vent; NaOH bleed from BMED_BASE; spent liquor to '
         'BMED_ACID. Duty sheet docs-authority/duties/EVAP_ACID_VS.md.', basis)
    _set(b, uid, 'continuous_kw.value', q(up['pump_kW'], 4), basis)
    _set(b, uid, 'continuous_kw.note',
         f'{VT}. Sump recirculation pump {fmt(up["recirc_m3_h"] * 1000, 0)} L/h at the minimum wetting rate '
         f'(PERRY9_ABS), 10 m head, 40 % efficiency (study).', basis)
    _set(b, uid, 'params.presence', 'present', basis)
    _set(b, uid, 'params.DN', int(up['DN']), basis)
    _set(b, uid, 'params.packed_mm', int(up['packed_mm']), basis)
    _set(b, uid, 'params.height_mm', int(up['height_mm']), basis)
    _set(b, uid, 'params.sump_L', float(dec(up['sump_L'])), basis)
    _set(b, uid, 'params.material',
         'PVC-U pipe and fittings (ASTM D1785 Sch 80), in-house cut PVC tube rings, PVC mesh demister '
         '(PERRY9_MAT: PVC to 60 C in HCl and NaOH)', basis)
    _set(b, uid, 'params.y_in_ppm_design', q(up['y_in_ppm'], 1), basis)
    _set(b, uid, 'params.y_out_ppm', float(s['dvs']('vs_y_out_ppm')), basis)
    _set(b, uid, 'params.design_case', 'upset: column bypassed (A-M-111)', basis)
    _set(b, uid, 'params.size_mm', [400, 400, int(up['height_mm'])], 'length-mm counts on the declared grid')
    _set(b, uid, 'params.size_note', 'L x W x H mm, set by flow_graph/param/vent_scrubber.py (X-PAR-10)', basis)
    _rate(b, 'IA-EVAP_ACID-VENT', q(up['vent_kg_d'], 4), 'kg/d',
          f'{VT}. Air from the feed (WEISS1970) saturated at the vent condenser; design case '
          f'{fmt(up["y_in_ppm"], 0)} ppmv HCl.', basis)
    _rate(b, 'IA-VS-NAOH', q(up['naoh_soln_kg_d'], 4), 'kg/d',
          f'{VT}. {fmt(up["naoh_mol_d"] * 1000, 3)} mmol/d = {s["dvs"]("vs_naoh_excess")} x HCl absorbed.', basis)
    _edge_field(b, 'IA-VS-NAOH', 'params.NaOH_mol_d', q(up['naoh_mol_d'], 9), basis)
    _rate(b, 'IA-VS-SPENT', q(up['spent_kg_d'], 4), 'kg/d', f'{VT}. Bleed plus HCl absorbed.', basis)
    _rate(b, 'IA-VS-OFF', q(up['offgas_kg_d'], 4), 'kg/d', f'{VT}. {s["dvs"]("vs_y_out_ppm")} ppmv HCl.', basis)
    _rate(b, 'SF-EVAP_ACID_VS', q(up['pump_kW'], 4), 'kW', f'{VT}. Feed equal to continuous_kw.', basis)
    _rate(b, 'SQ-EVAP_ACID_VS', q(up['pump_kW'], 4), 'kW',
          f'{VT}. Pump work leaves as heat. Layer thermal (F-3 fix, A-M-454): the X-THM-01 Q4 ledger counts it.',
          basis)
    _rate(b, 'IA-EVAP_ACID-COND', q(s['ea']['water'] - up['vent_kg_d'], 4), 'kg/d',
          f'{TAG}. Water evaporated, condensed and returned to BMED_ACID, less the vent (X-PAR-10).', basis)


@fn('process_ew_cascade', 'Q-038 element-rate booking of the EW cascade and its forming chain '
    '(AQS-ASSAY-001 sections 4 and 5; A-M-460, A-M-470, A-M-429; AQS-DUTY-010), bounding cell currents '
    '(AQS-DUTY-051, USBM_CL_EW, CODATA2018), Q-041 arrangement driver')
def process_ew_cascade(b, inputs):
    s = _core(b, inputs)
    if s is None:
        return
    v = s['v']
    basis = ('EW cascade bounding currents and Q-038 booked rates (AQS-ASSAY-001 sections 4 and 5; A-M-460; '
             'AQS-DUTY-051; USBM_CL_EW; Q-038 owner ruling 2026-11-05)')
    # booked product edges: noble and iron harvests on their cell edges, the
    # forming share (Cu + blend) on IA-EW-SHEET at the EW_9 collection point
    for n in range(1, 10):
        val = s['dep_ref'][n] if n in (1, 2, 7) else D0
        val = dec(val).quantize(D1.scaleb(-4), rounding=ROUND_HALF_EVEN)
        rider = ("; this cell's harvest rides IA-EW-SHEET (the forming routes take the Cu and blend deposits, "
                 "AQS-DUTY-010)." if val == 0 else ".")
        _rate(b, f'IA-EW-MET-{n}', q(val, 4), 'kg/d',
              f'{MET}. Cell EW_{n} plated product, element deposit mass at leach recovery 1.0{rider}', basis)
    _rate(b, 'IA-EW-SHEET', q(s['sheet'], 4), 'kg/d',
          f'{MET}. The forming feed booked at the EW_9 collection point: Cu deposit half to wire and half to mill, '
          f'the Pb/Sn/Ni/Cd/Zn blend deposits to powder (AQS-DUTY-010 bases on S57/S59/S60), less the atomizer '
          f'off-spec return {fmt(_remelt(s), 4)} kg/d. Element mass at recovery 1.0; the wear-goods '
          f'copper-equivalent convention is retired (Q-038 owner ruling 2026-11-04).', basis)
    form = [('S57', 'wire billet: half the Cu deposit'),
            ('S58', 'wire product: billet less melt fume at 10 % draw swarf'),
            ('S59', 'mill sheet (the mill closes at its feed)'),
            ('S60', 'powder: blend deposits at 10 % off-spec'),
            ('IA-WIRE-LOSS', 'draw swarf to the baghouse (10 % of the billet net of fume)'),
            ('IA-DRAW-FUME', 'melt fume at the AQS-DUTY-010 0.3 % of billet')]
    vals = {'S57': s['s57'], 'S58': s['s58'], 'S59': s['s59'], 'S60': s['s60'],
            'IA-WIRE-LOSS': s['wloss'], 'IA-DRAW-FUME': s['fume']}
    for sid, why in form:
        _rate(b, sid, q(vals[sid], 4), 'kg/d',
              f'{MET}. {why}; derived from the feed-assay deposit rows through solver.ew_products() (X-QA-04).',
              basis)
    # IA-BAG-01: the note belongs to fab_resist when the on-site photoresist
    # route owns it (F-20261110-08); this family re-derives the value only
    bag_old = (b.edges['IA-BAG-01']['rate'].get('note') or '')
    bag_owned = (b.edges['IA-BAG-01'].get('params') or {}).get('note_owner') == 'fab_resist' \
        or bag_old.startswith('X-RTE TF: fab photoresist')
    bag_val = q(s['wloss'] + _seed_rate(b, 'IA-MILL-LOSS') + _seed_rate(b, 'IA-FAB-LOSS'), 4)
    if bag_owned:
        _edge_value(b, 'IA-BAG-01', bag_val, basis + '; note owner fab_resist (F-20261110-08)')
    else:
        _rate(b, 'IA-BAG-01', bag_val, 'kg/d',
              f'{MET}. baghouse collected fines to the leach: mill loss + fab loss + draw swarf', basis)
    # aisle air book: make-up replaces the scrub blowdown loss less the draw fume
    blow = _seed_rate(b, 'S72') + _seed_rate(b, 'S72B')
    _rate(b, 'IA-MET-AIR-MU', q(blow - s['fume'], 4), 'kg/d',
          f'{MET}. MET_AHU make-up = MET_SCRUB blowdown {fmt(blow, 4)} less the wire-draw fume {fmt(s["fume"], 4)}.',
          basis)
    _rate(b, 'IA-MET-AIR-RET',
          q(_seed_rate(b, 'S62') + _seed_rate(b, 'S71') + s['fume'] - blow, 4), 'kg/d',
          f'{MET}. Closed aisle return: S62 + S71 + draw fume - scrub blowdown.', basis)
    _rate(b, 'IA-WEAR', q(s['wear'], 4), 'kg/d',
          f'{MET}. Worn-goods return at the roster line: the crew finished-textile issue (TEXTILE_HAB, '
          f'{fmt(s["wear"], 4)} kg/d, A-M-429) worn out at steady state. The 596.86 kg/d closing-by-difference '
          f'plug (A-M-265, 149 kg/person/d) is retired.', basis)
    _rate(b, 'IA-MFG-OUT', float(0), 'kg/d',
          f'{MET}. Retired plug: the crew goods issue is the roster textile line on TEXTILE_HAB (A-M-429); the '
          f'shop finished-goods surplus exports on IA-GOODS-SHIP (self-sustaining plant rule).', basis)
    _edge_value(b, 'IA-FEED-MU', float(s['feed_mu']),
                basis + '; dock make-up feedstock value (note owned by the first-creation book, A-M-460)')
    _shop_sums(b, s)
    _edge_field(b, 'S16', 'rate.note',
                'Study MFG scrap continuous-equiv mid of polymer/metal band (AQS-AUD-001 s10.6): 29.3 % of the '
                f'S08 solids. {MET}: the shop closes on the goods export IA-GOODS-SHIP; this line holds its band '
                'basis.', basis + '; S16 band-basis note of AQS-AUD-001 s10.6')
    # cell DC stamps and channels
    for n in range(1, 10):
        uid = f'EW_{n}'
        e = s['ew'][n]
        cell = b.nodes[uid]
        if isinstance(cell.get('continuous_kw'), dict):
            note = (f"{TAG}. Cell DC at the electrode: {fmt(e['I'], 0)} A (Faraday at the AQS-ASSAY-001 element "
                    f"envelope, table 4.1, recovery 1.0; Q-038 owner ruling 2026-11-05) x {s['dvs']('ew_cell_voltage_V')} "
                    f"V (USBM_CL_EW chloride EW).")
            _set(b, uid, 'continuous_kw.value', q(e['P'], 4), basis)
            _set(b, uid, 'continuous_kw.note', note, basis)
        if 'cell_voltage_V' in cell['params']:
            _set(b, uid, 'params.cell_current_A', qi(e['I']), basis)
            _set(b, uid, 'params.cell_voltage_V', float(s['v_cell']), basis)
        # plate geometry from the harvest book (docs-authority/_ew_sizing.py
        # arithmetic, AQS-EW-MOD-001 drivers; A-M-029/036..040): the graph
        # params.sizing are outputs of that book, never inputs back into it
        ph = v('DIGESTER.ew-cascade-train.ew_plate_height_m')
        pwid = v('DIGESTER.ew-cascade-train.ew_plate_width_m')
        ap = 2 * ph * pwid
        jj = v('ew_current_density_A_m2')
        pitch = v('DIGESTER.ew-cascade-train.ew_cathode_pitch_m')
        wall = v('DIGESTER.ew-cascade-train.ew_tank_wall_m')
        endm = v('DIGESTER.ew-cascade-train.ew_tank_end_margin_m')
        sidem = v('DIGESTER.ew-cascade-train.ew_tank_side_margin_m')
        sump = v('DIGESTER.ew-cascade-train.ew_tank_sump_m')
        top = v('DIGESTER.ew-cascade-train.ew_tank_cover_m')
        fb = v('DIGESTER.ew-cascade-train.ew_tank_freeboard_m')
        nc = _cathode_count(e['I'], jj, ap)
        li, wi = nc * pitch + 2 * endm, pwid + 2 * sidem
        hi = sump + ph + top + fb
        sz = {'size_mm': [qi((li + 2 * wall) * 1000), qi((wi + 2 * wall) * 1000), qi((hi + wall) * 1000)],
              'I_bounding_A': qi(e['I']), 'cathodes': nc, 'anodes': nc + 1,
              'j_A_m2': qi(e['I'] / (nc * ap)),
              'V_liq_m3': q(li * wi * (sump + ph + top), 3), 'P_dc_kW': q(e['P'], 2),
              'status': 'study', 'source': 'AQS-DUTY-051'}
        _set(b, uid, 'params.sizing', sz, basis + '; AQS-EW-MOD-001 plate/tank drivers (A-M-029, A-M-036..040)')
        if f'IA-DC-{uid}' in b.edges:
            _rate(b, f'IA-DC-{uid}', q(e['P_bus'], 6), 'kW',
                  f"{TAG}. Channel DC at {s['dvs']('ew_cell_voltage_V')} V cell + {s['dvs']('ew_bus_drop_V')} V bus "
                  f"drop, bounding current at the AQS-ASSAY-001 element envelope (Q-038 owner ruling 2026-11-05); "
                  f"6 dp so the sub-watt cells carry no rounding misfit.", basis)


def _remelt(s):
    """The atomizer off-spec return: 10 percent of the blend deposits."""
    return s['blend'] * D(10) / 100


def _shop_sums(b, s):
    """IA-GOODS-SHIP seed: shop throughput less the crew issue and returns,
    seeded only outside the reconciliation band (A-M-491; R10c pairing with
    balance.physics, 2026-11-10 Round D2/D4)."""
    g = b.data
    ins = sum((dec(e['rate']['value']) for e in g['edges'] if e['presence'] == 'present'
               and e['to_unit_id'] == 'MFG_SHOP' and 'mass' in (e.get('layers') or [])
               and e['rate'].get('unit') == 'kg/d' and isinstance(e['rate'].get('value'), (int, float))), D0)
    outs = sum((dec(e['rate']['value']) for e in g['edges'] if e['presence'] == 'present'
                and e['from_unit_id'] == 'MFG_SHOP' and 'mass' in (e.get('layers') or [])
                and e['rate'].get('unit') == 'kg/d' and isinstance(e['rate'].get('value'), (int, float))
                and e['stream_id'] not in ('IA-GOODS-SHIP', 'IA-MFG-OUT')), D0)
    goods = (ins - outs).quantize(D1.scaleb(-6), rounding=ROUND_HALF_EVEN)
    assert goods > 0, ('shop goods surplus negative: the shop consumes more than it takes in', str(goods))
    band = s['v']('balance_residual_band_kg_d')
    seed = dec(b.edges['IA-GOODS-SHIP']['rate']['value'] or 0)
    if abs(seed - goods) > band:
        _edge_value(b, 'IA-GOODS-SHIP', float(goods),
                    'shop finished-goods surplus seed (AQS-PAR-003 R10c band, A-M-491; self-sustaining plant rule)')


@fn('process_rectifier', 'nine-channel EW rectifier channels and stamps (AQS-ELEC-004, A-M-044, A-M-255; '
    'R10b remap, F-24 re-basis; USBM_CL_EW)')
def process_rectifier(b, inputs):
    s = _core(b, inputs)
    if s is None:
        return
    v = s['v']
    uid = 'RECTIFIER'
    if uid not in b.nodes:
        return
    basis = 'EW rectifier channels (AQS-ELEC-004; A-M-044 frames; A-M-255; USBM_CL_EW)'
    drv = s['drv']
    frames = [dec(x) for x in drv['rect_channel_frame_sizes_A']['value']]
    margin, v_rated = v('rect_channel_margin'), v('rect_channel_rated_V')
    eff = v('rect_efficiency')
    rated_sum = sum((_rectifier_channel(s['ew'][n]['I'], s['v_cell'], s['v_drop'], eff, frames, margin, v_rated)['rated_A']
                     for n in range(1, 10)), D0)
    rated_kw = rated_sum * v_rated / 1000
    r = s['rect']
    p_ac, p_dc, loss = r['P_ac'], r['P_dc'], r['P_ac'] - r['P_dc']
    _set(b, uid, 'params.rated_A', int(rated_sum), basis)
    _set(b, uid, 'params.nameplate_kw_dc', float(q(rated_kw, 6)), basis)
    _set(b, uid, 'params.rect_ac_input_kW', q(p_ac, 3), basis)
    _set(b, uid, 'params.rect_loss_kW', q(loss, 3), basis)
    _set(b, uid, 'params.rect_basis',
         f'{TAG}/R10b: nine-channel EW rectifier {fmt(rated_sum, 0)} A, {fmt(rated_kw, 0)} kW DC nameplate at '
         f'6 V; bounding AC input {fmt(p_ac, 2)} kW (AQS-ELEC-004), counted once '
         f'in _power_sizing (A-M-255). F-24: the 12 kW node load stamp (A-M-231 \'48 V rail\' basis) is removed as '
         f'a double count - its cited basis (\'DC to cells and induction\', POWER_DUTIES.md) is booked in the '
         f'AQS-ELEC-004 row, the induction units carry their own stamps, and no 48 V rail load table exists '
         f'(CRITICAL_PATH says 20 kW; the per-motor 48 V driver loads live in the unit stamps). S17 is retired.',
         basis, 'A-M-255')
    _set(b, uid, 'notes',
         f'{TAG}; AQS-ELEC-004. Nine-channel EW rectifier, {fmt(rated_sum, 0)} A, {fmt(rated_kw, 0)} kW DC '
         f'nameplate at 6 V (Rev AC node RECTIFIER; RECT_EW remapped R10b).', basis)
    _set(b, uid, 'continuous_kw.value', float(0), basis + '; F-24: no independent 48 V rail load basis')
    if isinstance(b.nodes[uid].get('continuous_kw'), dict):
        _set(b, uid, 'continuous_kw.note',
             f'A-M-231 (AQS-NOTE-PV-REBASE Rev A section 8): 12 kW 48 V rail and auxiliary basis (AQS-PWR-001). '
             f'The nine-channel EW DC load is counted once behind the AQS-ELEC-004 bounding AC row in _power_sizing '
             f'(params.rect_ac_input_kW {fmt(p_ac, 2)} kW; A-M-255); S17 equals this node value.', basis, 'A-M-231')
    if 'S17' in b.edges:
        _rate(b, 'S17', float(0), 'kW',
              f'{TAG24} (A-M-231 restated): retired - the 12 kW RECTIFIER supply double-counted the EW rectifier '
              f'AC feed now booked behind the AQS-ELEC-004 bounding row (A-M-255); the \'48 V rail\' re-branding '
              f'has no load table. Live path: the EW rectifier AC input is counted in _power_sizing '
              f'(params.rect_ac_input_kW).', basis)
        assert b.edges['S17']['presence'] == 'retired'
    if 'IA-RECT-Q4' in b.edges:
        _rate(b, 'IA-RECT-Q4', q(loss, 4), 'kW',
              f'{TAG24} (A-M-246 restated): the rectifier reject is the calculated conversion loss at the bounding '
              f'duty - AC input {fmt(p_ac, 3)} kW less DC out {fmt(p_dc, 3)} kW at eff 0.80 '
              f'= {fmt(loss, 3)} kW to the Q4 recovery loop. Was the 1.0 kW bound of the removed 12 kW basis '
              f'(12 kW at 92-96 percent efficiency, POWER_DUTIES.md).', basis)


@fn('process_bus_delta', 'SOL_ARK 480 V bus close on IA-PV-01 (X-PAR-04): the PV average carries the change '
    'the acid-loop feeds introduce (AQS-PAR-001; A-M-233 re-basis owns the absolute value)')
def process_bus_delta(b, inputs):
    if inputs.get('drivers') is None:
        return
    basis = 'SOL_ARK bus close (X-PAR-04; AQS-PAR-001): the PV average carries the delta of the acid-loop feeds'
    def bus_val(sid):
        got = b.computed.get(('edge', sid, 'rate'))
        if got is not None:
            return dec(got[0]['value'])
        return dec(b.edges[sid]['rate']['value'])
    before = sum((dec(b.edges[sid]['rate']['value']) for sid in ELEC_IN if sid in b.edges), D0)
    after = sum((bus_val(sid) for sid in ELEC_IN if sid in b.edges), D0)
    delta = after - before
    pv = (dec(b.edges['IA-PV-01']['rate']['value']) + delta).quantize(D1.scaleb(-4), rounding=ROUND_HALF_EVEN)
    _edge_value(b, 'IA-PV-01', float(pv), basis)
    if isinstance(b.nodes['PV_ARRAY'].get('continuous_kw'), dict):
        _set(b, 'PV_ARRAY', 'continuous_kw.value', float(pv), basis)

"""The write_graph power family (family migration; reference writers
flow_graph/param/write_graph.py command `power` and docs-authority/_power_sizing.py,
ledger rows `write_graph_power` (MIXED: solve -> here, collection bus -> renderer)
and `doc_site_units` (MIXED: designed-source sizing -> here, placement doc ->
renderer)). The AQS-ELEC-007 demand census and roof close, the D75 PV dispatch,
the ZNBR2 store book, the Q-040 critical-list rating with the NFPA 110 exercise
average, the F-20261110-08 grease re-solve arithmetic, and the locale
designed-source dispatch (F-20261113-01). The committed graph carries every
field this family stamps; that committed state is the golden this module
reproduces.

Grid doctrine (owner ruling 2026-11-15): driver and seed values arrive as v1
floats and are converted at this boundary by dec() (exact Decimal of the
decimal repr); arithmetic is exact rational/Decimal; schema fields are
quantised half-even (Python round()'s tie rule) at the decimals the v1 schema
stores - 4 dp on the kW books, 2 dp on the store and bus books, 3 dp on the
hvac and roof-load books, 1 dp on the interconnection peak, integers on every
count and nameplate. The scale is named at each call. Dimensionless constants
port as integer scaled pairs with the scale in the name: the air book
1.2 kg/m3 x 1006 J/kgK -> 12/10 x 1006, the daily-average conversions /24 h and
/86.4, the SKF per-point gram rule 0.005 -> 5/1000, the monthly->daily average
12/365, pi on a 1e-15 scale. No float literals.

THE ROOF CLOSE AS A PURE DERIVATION. v1's solver.roof_close swept the bay-grid
growth range (base bays .. base+59 bays per axis) in float arithmetic and kept
the smallest-footprint fit whose roof carries the quantised PV need (ties on
the aspect ratio nearest 4/3). The sweep is already bounded integer
combinatorics - no convergence loop - so v2 ports it as exact Decimal
evaluation over the same declared range with the same fit rule; the aspect tie
is the algebraically identical integer cross-product |3nx-4ny|/ny (no float
division at all). Same inputs -> same fit, always; the fit is exact on the
grid (whole bays, whole kWp need, have >= need asserted).

DISPOSITION OF THE CHAINS AROUND THIS FAMILY (the strangler bridge):
- Composition order. The heat family reads this family's store book
  (ZNBR2 params.cycling_thermal, the vehicle dict the v1 heat stage wrote from
  the power sizing), so THIS FAMILY REGISTERS BEFORE HEAT: the required solve
  order is process -> power -> heat (the census reads process's fresh acid-loop
  and rectifier books overlay-first; heat then re-derives the charge-window
  book from the fresh store book). With the heat family as landed, its
  charge_window read-back is seed-only; it becomes the fresh computation the
  moment its read gains the overlay-first idiom its own dry_cooler already
  uses (one line, heat lane). The GEO_HP book runs the other way: this family
  reads the heat family's Q4-bus lift S44 overlay-first, seed fallback - with
  power before heat that read is the committed fixed point (a changed lift
  lands on the next solve, the pass-lag the v1 fixed-point loop hid).
- The ZNBR2 STORE BOOK P (the roof-close fixed point: demand census + EW
  rectifier AC + EXT_HALL extension heat + roof fit) lands here: store_kWh =
  P x night, store_in_kWh = store / round trip. The family stamps the store
  book into the vehicle dict ZNBR2 params.cycling_thermal in the committed
  schema shape. The committed dict embeds the v1 heat-lane census (grease
  route override plus the mid-pass demand books, 2658.8 kWh/d out); the v2
  single census books 2679.0 kWh/d out - the enumerated deviation the
  composition eliminates, not a physics change. The ZNBR2 kW/kWh/charge/
  discharge/continuous_kw/distribution books reproduce the committed golden
  exactly (they were always this writer's, at this census).
- The F-20261110-08 grease machinery: v1's heat stage re-solved the grease
  route (A-M-480 SKF relubrication) in memory and passed the duty to
  _power_sizing.py as an in-memory continuous_kw override, because between
  passes the graph carries specialty_sizing's commercial-class kettle stamps.
  In v2 the store book is single-sourced in this census (which reads the seed
  stamps, exactly like v1's own power() call did - that call is what the
  committed golden embeds), so the override plumbing dies. The arithmetic
  survives as the registered pure derivation `grease_route` (the SKF need
  chain, the route stoichiometry, the ASTM_C680 kettle), first in this family's
  order, recording nothing: the GREASE_* stamps belong to the specialty and
  fluoro lanes.
- mvs.electrical is derived, not stamped: the v1 writer wrote the whole graph
  -level block, and the v2 overlay has no graph-level lane yet (nodes and
  edges only). `mvs_book()` is the pure derivation, pinned to the committed
  block in the tests; writing it to the graph is builder/composer work, the
  same split the collection bus takes.
- Edge and node topology (creating EXT_HALL, SF-EXT_HALL, the GEO_GHEX hall
  field removal) is builder work: the committed graph carries them, so this
  family asserts the seed topology instead of writing it.
- The FUEL_CELL standby-replacement exercise book (locale plan eliminates the
  genset) is the balance family's lane (o2_close); this family ports the
  genset-present book only and records nothing when the seed lacks BACKUP_GEN.
- The X-ELS-02 shop-tool and source-loop-circulator load books belong to their
  calculators per the ledger (doc_mfg_tools, geo_loop); this family keeps only
  the GEO_HP re-solve of the S44 lift current.

The v1 machinery (subprocess spawn, the print ledger, disk write-back) does
not migrate: assignment replaces the field and its provenance in full. A solve
without the driver or site-profile payload records nothing, so the bridge
solve and the check stay byte-faithful to the seed.
"""
from decimal import Decimal, ROUND_CEILING, ROUND_HALF_EVEN

from flow_graph.v2.registry import fn

STAGES = 'power'                                               # family tag in provenance rows
D0, D1 = Decimal(0), Decimal(1)
DAY = Decimal(24)                                              # h, the design-day book
PI = Decimal(3141592653589793) / Decimal(10) ** 15            # pi (scale 1e-15)
F = Decimal(9648533212) / Decimal(100000)                      # C/mol, CODATA2018 (scale 1e-5)
AIR = Decimal(12) / Decimal(10)                                # 1.2 kg/m3 air density book
AIR_CP = Decimal(1006)                                         # J/kgK, the ventilation UA book
BAY_RANGE = 60                                                 # the declared bay-grid growth range (+0..+59 bays per axis)
ASPECT_A, ASPECT_B = 3, 4                                      # the 4/3 aspect tie as the integer metric |3nx-4ny|/ny
M_EL = {'Au': Decimal('196.97'), 'Ag': Decimal('107.87'), 'Cu': Decimal('63.546'),
        'Pb': Decimal('207.2'), 'Sn': Decimal('118.71'), 'Ni': Decimal('58.693'),
        'Fe': Decimal('55.845'), 'Cd': Decimal('112.41'), 'Zn': Decimal('65.38')}
EW_CELLS = {1: ('Au', 3), 2: ('Ag', 1), 3: ('Cu', 2), 4: ('Pb', 2), 5: ('Sn', 2),
            6: ('Ni', 2), 7: ('Fe', 2), 8: ('Cd', 2), 9: ('Zn', 2)}
NOT_DEMAND = {'SOL_ARK_60K', 'PV_ARRAY', 'ZNBR2', 'FUEL_CELL', 'MEOH_FC', 'BACKUP_GEN',
              'BOUNDARY_EXPORT', 'EXT_HALL'}                   # storage/generation/export: never demand (A-M-231)
KGEN = 'ELEC.generation-train.BACKUP_GEN.'                     # the generator driver prefix (AQS-ELEC-007)
# grease route (A-M-480): stearic-acid equivalent C18H36O2 and the route atoms (CIAAW2021-class book)
M_ACID = Decimal('284.48')
M_H, M_O, M_CA, M_LI = Decimal('1.008'), Decimal('15.999'), Decimal('40.078'), Decimal('6.941')
M_H2O = 2 * M_H + M_O
M_CAO = M_CA + M_O
M_CAOH2 = M_CA + 2 * (M_O + M_H)
M_LIOH = M_LI + M_O + M_H
M_CASOAP = 2 * (M_ACID - Decimal('1.008')) + M_CA
M_LISOAP = (M_ACID - Decimal('1.008')) + M_LI
INSUL_THK = (13, 25, 38, 50, 65, 75, 100, 125, 150, 200)       # the ASTM_C680 mineral-wool ladder, mm
NONROT = {'rectifier', 'inverter', 'pv', 'flow_battery', 'pem_fc', 'iem_fc', 'pem_electrolyser', 'genset',
          'hydro', 'farm', 'hab', 'shop', 'dock', 'heat_battery', 'digest'}
FLAG_ONLY = ('fission', 'other')                               # designed sources need their completed study (Q-024)


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
    """int(round(x)) as v1 wrote it: half-even to an integer."""
    return int(Decimal(x).quantize(D1, rounding=ROUND_HALF_EVEN))


def qd(x, dp):
    """The exact quantised book (half-even at dp), kept as a Decimal for
    downstream exact arithmetic."""
    return Decimal(x).quantize(D1.scaleb(-dp), rounding=ROUND_HALF_EVEN)


def ceil(x):
    """math.ceil on the exact book (the v1 nameplate/counts rule)."""
    return int(Decimal(x).to_integral_value(rounding=ROUND_CEILING))


def fmt(x, dp):
    """The f'{x:.dpf}' text of an exact value (half-even at dp)."""
    return f'{Decimal(x).quantize(D1.scaleb(-dp), rounding=ROUND_HALF_EVEN):f}'


def gfmt(x):
    """The f'{x:g}' text of an exact value (the v1 step/peak conventions):
    the decimal repr with trailing zeros stripped."""
    return f'{Decimal(x).normalize():f}'


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


def _dv(drv, key):
    """A driver value -> exact Decimal. drivers.json keys are flat dotted
    strings (DR.val); a compound path also walks into dict-valued entries
    (maint_rotating.lube_mo), unwrapping the 'value' envelope at each step."""
    if key in drv:
        return dec(drv[key]['value'])
    cur = drv
    for part in key.split('.'):
        if isinstance(cur, dict) and 'value' in cur and part not in cur:
            cur = cur['value']
        cur = cur[part]
    if isinstance(cur, dict) and 'value' in cur:
        cur = cur['value']
    return dec(cur)


def _dvs(drv, key):
    """A driver value as the text the v1 f-string interpolation printed (a
    string driver passes through; a numeric one as its decimal repr)."""
    raw = drv[key]['value'] if key in drv else None
    if raw is None:
        cur = drv
        for part in key.split('.'):
            cur = cur[part]
        raw = cur['value'] if isinstance(cur, dict) and 'value' in cur else cur
    return raw if isinstance(raw, str) else str(dec(raw))


def _node_val(b, uid, path):
    """A seed node field (dotted path)."""
    cur = b.nodes[uid]
    for part in path.split('.'):
        cur = cur[part]
    return cur


def _fresh_node(b, uid, path):
    """A node field this pass may already have re-stamped: the family overlay
    first, the seed otherwise (the dry_cooler read idiom)."""
    got = b.computed.get(('node', uid, path))
    if got is not None:
        return got[0]
    return _node_val(b, uid, path)


def _fresh_rate(b, sid):
    """An edge rate this pass may already have re-stamped: overlay first."""
    got = b.computed.get(('edge', sid, 'rate'))
    if got is not None:
        return got[0]['value']
    return b.edges[sid]['rate']['value']


def _kw(b, uid):
    """The continuous kW book of a unit, overlay first, seed otherwise; None
    or a missing field books 0 (the v1 `value or 0`)."""
    if uid not in b.nodes:
        return D0
    got = b.computed.get(('node', uid, 'continuous_kw'))
    qk = got[0] if got is not None else b.nodes[uid].get('continuous_kw')
    v = qk.get('value') if isinstance(qk, dict) else qk
    return dec(v) if isinstance(v, (int, float)) else D0


def _pv_kwp(p_kw, night_h, eta_rt, yld, derate):
    """sizing.power.pv_kWp [NREL_PVWATTS]: the balancing nameplate."""
    return (p_kw * (DAY - night_h) + p_kw * night_h / eta_rt) / (yld * derate)


def _oversized(p_kw, night_h, eta_rt, yld, derate, factor, dc_ac, inv_unit_kw):
    """sizing.power.oversized [NREL_PVWATTS8, D75]: PV at `factor` x the
    balancing nameplate; cloudy-day yield mean/factor; charge = PV peak on the
    cloudy day less direct load; inverter AC = kWp/dc_ac and not less than P."""
    base = _pv_kwp(p_kw, night_h, eta_rt, yld, derate)
    kwp = factor * base
    charge = max(kwp * derate / factor - p_kw, D0)
    inv_ac = max(kwp / dc_ac, p_kw)
    n = ceil(inv_ac / inv_unit_kw)
    e_bal = base * yld * derate
    return dict(pv_base_kWp=base, pv_kWp=kwp, store_kWh=p_kw * night_h, discharge_kW=p_kw,
                charge_kW=charge, store_kW=max(p_kw, charge), store_in_kWh=p_kw * night_h / eta_rt,
                inverters=n, inv_kW=n * inv_unit_kw, export_peak_kW=n * inv_unit_kw - p_kw,
                export_kWh_d_clear=(factor - D1) * e_bal, cloudy_yield_frac=D1 / factor)


def _storage_book(p_kw, night_h, eta_rt):
    """docs-authority/_power_sizing.py _storage (X-LOC-13 worst-stretch model):
    the store carries P x night out and store/RT in; the charge rate is the
    store-in over the charge window. THE ZNBR2 STORE BOOK P."""
    store = p_kw * night_h
    store_in = store / eta_rt
    win = DAY - night_h if night_h < DAY else DAY
    return dict(store_kWh=store, store_in_kWh=store_in, discharge_kW=p_kw,
                charge_kW=store_in / win, store_kW=max(p_kw, store_in / night_h if night_h > D0 else p_kw))


def _segments(length_mm, max_mm, path_mm):
    """sizing.roof._segments [IFC2027 1205.3, NFPA1 11.12]: arrays no longer
    than max_mm separated by path_mm; the array length total and the count."""
    n = max(1, ceil((length_mm + path_mm) / (max_mm + path_mm)))
    return length_mm - (n - 1) * path_mm, n


def _array_area(w_mm, d_mm, perim_small, perim_large, axis_limit, arr_max, path):
    """sizing.roof.array_area_m2: the usable roof inside the perimeter pathway
    and the array count (the m2 on a 1e-6 mm2->m2 scale, exact)."""
    p = perim_small if max(w_mm, d_mm) <= axis_limit else perim_large
    lx, nx = _segments(w_mm - 2 * p, arr_max, path)
    ly, ny = _segments(d_mm - 2 * p, arr_max, path)
    return max(D0, lx) * max(D0, ly) / Decimal(10) ** 6, dict(perimeter_mm=p, arrays=nx * ny,
                                                              arrays_x=nx, arrays_y=ny)


def _roof_kwp(area_m2, eff, gcr):
    """sizing.roof.roof_kWp [NREL_PVWATTS8]: area x STC efficiency x GCR."""
    return area_m2 * eff * gcr


def _extension(drv, a_add, w_mm, d_mm, mode):
    """sizing.roof.extension_kW_v2 (X-PAR-08) on exact books: lighting (IECC
    2021 C405, 10 % lit), ventilation (ASHRAE 62.1-2025 air, ISO 16798-3 fans),
    heat-pump HVAC split by degree days (ASHRAE 90.1-2025 Table 6.8.1-2,
    NOAA_NORMALS_DFW means), slab edge F-factor (IECC 2021 C402), internal
    gains = lighting + fans. The ground mode adds the bore field under the
    footprint (KAVANAUGH2014 bore length per kW peak block load)."""
    v = lambda k: _dv(drv, k)
    a_add = dec(a_add)
    w_m, d_m = dec(w_mm) / 1000, dec(d_mm) / 1000
    aw = 2 * (w_m + d_m) * v('ext_wall_h_mm') / 1000            # perimeter wall area, m2
    perim = 2 * (w_m + d_m)
    conditioned = v('ext_conditioned')
    vent_ls = v('ext_Ra_L_s_m2') * a_add
    uav = vent_ls / 1000 * AIR * AIR_CP
    uae = v('ext_U_roof') * a_add + v('ext_U_wall') * aw
    uas = v('ext_F_slab') * perim
    light = v('ext_lpd_W_m2') * a_add * v('ext_light_frac')
    fan = vent_ls * v('ext_sfp_W_per_L_s')
    g = light + fan
    dth, dtc = v('ext_dTh_K'), v('ext_dTc_K')
    fh = dth / (dth + dtc)
    fc = D1 - fh
    cop_h = v('gsh_cop_h' if mode == 'ground' else 'ash_cop_h')
    cop_c = v('gsh_cop_c' if mode == 'ground' else 'ash_cop_c')
    pump_w = v('gsh_pump_W_per_kWt') if mode == 'ground' else D0
    qh = max(D0, (uae + uav + uas) * dth - g * fh) * conditioned
    qc = ((uae + uav) * dtc + g * fc) * conditioned
    pump = pump_w * (qh + qc) / 1000
    hvac = qh / cop_h + qc / cop_c + pump
    r = dict(light_kW=light / 1000, vent_kW=(fan + uav * (dth / cop_h + dtc / cop_c) * conditioned) / 1000,
             envelope_kW=(hvac - uav * (dth / cop_h + dtc / cop_c) * conditioned) / 1000,
             total_kW=(light + fan + hvac) / 1000, vent_L_s=vent_ls,
             Qh_kW=qh / 1000, Qc_kW=qc / 1000, slab_kW=uas * dth / 1000, gains_kW=g / 1000,
             pump_kW=pump / 1000)
    pk_h = (uae + uav + uas) * (v('ext_T_in_C') - v('ext_T_design_h_C')) / 1000
    pk_c = (uae + uav) * (v('ext_T_design_c_C') - v('ext_T_in_C')) / 1000 + r['gains_kW']
    r.update(mode=mode, peak_h_kW=pk_h, peak_c_kW=pk_c)
    if mode == 'ground':
        bore_l = v('gsh_bore_m_per_kWt') * max(pk_h, pk_c)
        bores = ceil(bore_l / v('gsh_bore_depth_m'))
        r.update(bore_m=bore_l, bores=bores,
                 bore_field_m2=dec(bores) * v('gsh_bore_spacing_m') ** 2,
                 fits_under_building=dec(bores) * v('gsh_bore_spacing_m') ** 2 <= w_m * d_m)
    return r


def _roof_load(drv):
    """sizing.roof.roof_load_kPa [ASCE 7-22]: PV dead + max(live, snow),
    service and LRFD 1.2D + 1.6(Lr or S)."""
    dead = _dv(drv, 'roof_pv_dead_kPa')
    live = max(_dv(drv, 'roof_live_kPa'), _dv(drv, 'roof_snow_kPa'))
    return dict(service_kPa=q(dead + live, 3), lrfd_kPa=q(dead * Decimal(12) / Decimal(10) + live * Decimal(16) / Decimal(10), 3))


def _roof_close(drv, p_base_kw, pvf, mode=None):
    """solver.roof_close (X-PAR-07/X-PAR-08) as a pure derivation: exact
    evaluation of the declared bay-grid growth range (base..base+59 bays per
    axis), smallest footprint whose roof carries the quantised PV need
    (ceil to the whole kWp the nameplate books), ties on the aspect ratio
    nearest 4/3 as the integer cross-product. Deterministic; no convergence
    loop; the fit is exact on the grid."""
    mode = mode or _dvs(drv, 'ext_hvac')
    if mode == 'best':
        fits = {m: _roof_close(drv, p_base_kw, pvf, m) for m in ('air', 'ground')}
        best = min(fits.values(), key=lambda r: (r['footprint_m2'], r['P_kW']))
        best = dict(best)
        best['compare'] = {m: dict(footprint_m2=r['footprint_m2'], bays=[r['bays_x'], r['bays_y']],
                                   ext_kW=q(r['ext']['total_kW'], 2), pv_kWp=r['pv_need_kWp'])
                           for m, r in fits.items()}
        return best
    bay = _dv(drv, 'bay_mm')
    bx0, by0 = int(_dv(drv, 'base_bays_x')), int(_dv(drv, 'base_bays_y'))
    a0 = dec(bx0) * dec(by0) * bay * bay / Decimal(10) ** 6
    eta = _dv(drv, 'storage_round_trip')
    yld = _dv(drv, 'pv_yield_kWh_kWp_d') * _dv(drv, 'pv_roof_yield_factor')
    derate, factor = _dv(drv, 'pv_system_derate'), _dv(drv, 'pv_oversize_factor')
    best = None
    for nx in range(bx0, bx0 + BAY_RANGE):
        for ny in range(by0, by0 + BAY_RANGE):
            w_mm, d_mm = dec(nx) * bay, dec(ny) * bay
            area = w_mm * d_mm / Decimal(10) ** 6
            ext = _extension(drv, area - a0, w_mm, d_mm, mode)
            p = dec(p_base_kw) + ext['total_kW']
            need = ceil(_pv_kwp(p, _dv(drv, 'night_hours'), eta, yld, derate) * factor * pvf)
            arr, lay = _array_area(w_mm, d_mm, _dv(drv, 'ifc_perim_small_mm'), _dv(drv, 'ifc_perim_large_mm'),
                                   _dv(drv, 'ifc_axis_limit_mm'), _dv(drv, 'ifc_array_max_mm'), _dv(drv, 'ifc_path_mm'))
            have = _roof_kwp(arr, _dv(drv, 'pv_module_eff'), _dv(drv, 'pv_roof_gcr'))
            if have < need:
                continue
            if best is not None:
                if area > best['footprint_m2']:
                    continue
                if area == best['footprint_m2']:
                    # |nx/ny - 4/3| < |bx/by - 4/3|  <=>  |3nx-4ny|*by < |3bx-4by|*ny
                    if abs(ASPECT_A * nx - ASPECT_B * ny) * best['bays_y'] \
                            >= abs(ASPECT_A * best['bays_x'] - ASPECT_B * best['bays_y']) * ny:
                        continue
            best = dict(bays_x=nx, bays_y=ny, W_mm=w_mm, D_mm=d_mm, footprint_m2=area,
                        added_m2=area - a0, ext=ext, P_kW=p, pv_need_kWp=need, hvac=mode,
                        array_m2=arr, layout=lay, pv_roof_kWp=have, load=_roof_load(drv))
    return best


def _ew_currents(b, drv):
    """The EW cascade bounding currents at the element envelope (Q-038,
    AQS-DUTY-051, CODATA2018 Faraday; the same arithmetic as the process
    family) and the EW rectifier AC input the census counts (A-M-255: counted
    once, behind the AQS-ELEC-004 bounding row)."""
    feed = dec(_fresh_rate(b, 'IA-FEED-01'))
    els = b.edges['IA-FEED-01']['params']['assay_envelope']['element_envelope']['elements']
    rec = _dv(drv, 'ew_leach_recovery_design')
    ce = _dv(drv, 'ew_current_efficiency_design')
    arr = drv['ew_minor_metal_arrangement']['value']
    assert arr in ('selective', 'merged'), arr
    minor = tuple(int(x) for x in drv['ew_minor_metal_cells']['value'])
    m_blend = min(M_EL[EW_CELLS[m][0]] for m in minor)          # nickel basis (A-M-494)
    v_cell, v_drop = _dv(drv, 'ew_cell_voltage_V'), _dv(drv, 'ew_bus_drop_V')
    i_total, p_ac = D0, D0
    for n in range(1, 10):
        el, z = EW_CELLS[n]
        env_key = el if el in ('Fe', 'Cu', 'Au', 'Ag') else 'other_plateable'
        dep = feed * dec(els[env_key]['fraction']) * rec
        host = arr == 'merged' and n == minor[0]
        idle = arr == 'merged' and n in minor and not host
        i_a = D0 if idle else dep * 1000 / (m_blend if host else M_EL[el]) * z * F / 86400 / ce
        i_total += i_a
        p_ac += i_a * (v_cell + v_drop) / 1000
    return i_total, p_ac / _dv(drv, 'rect_efficiency')


def _census(b):
    """The A-M-231 demand census (docs-authority/_power_sizing.py): every
    present unit's continuous kW outside the storage/generation/export set and
    the EW cells, each raised to the SOL_ARK feed where a feed books more."""
    books = {}
    for n in b.data['nodes']:
        uid = n['unit_id']
        if n.get('presence') == 'retired' or uid in NOT_DEMAND:
            continue
        if uid.startswith('EW_') and uid[3:].isdigit():
            continue
        kw = _kw(b, uid)
        if kw:
            books[uid] = kw
    for e in b.data['edges']:
        if e.get('from_unit_id') != 'SOL_ARK_60K' or 'elec' not in (e.get('layers') or []):
            continue
        uid = e['to_unit_id']
        if uid in NOT_DEMAND or e.get('presence') == 'retired':
            continue
        r = e.get('rate') or {}
        if r.get('unit') == 'kW' and isinstance(r.get('value'), (int, float)):
            books[uid] = max(books.get(uid, D0), dec(r['value']))
    return books


def _critical_list(b, drv):
    """backup_fuel.critical_list (AQS-ELEC-007): the loads the generator
    carries in an outage, from drivers and the graph."""
    crit = [('HABITATION', float(_dv(drv, KGEN + 'crit_HABITATION_kW')))]
    if 'CRYO_H2' in b.nodes:
        peak = dec(_fresh_node(b, 'CRYO_H2', 'params.compressor_design.P_peak_kW'))
        crit.append(('CRYO_H2', q(peak, 2)))                    # AQS-DUTY-067 peak
    if 'CRYO_ASU' in b.nodes:
        crit.append(('CRYO_ASU', q(_kw(b, 'CRYO_ASU'), 2)))     # AQS-DUTY-069 (A-M-238)
    if 'GROW_BED' in b.nodes:
        crit.append(('GROW_BED', float(_dv(drv, KGEN + 'crit_GROW_BED_kW'))))
    crit.append(('controls and instruments', float(_dv(drv, KGEN + 'crit_controls_kW'))))
    return crit


def _rating(b, drv):
    """backup_fuel.rating_kw (owner ruling Q-040, 2026-11-05; AQS-ELEC-007 /
    AQS-RED-001): 125 % of the live critical list, rounded up in the commercial
    5 kW step."""
    crit = _critical_list(b, drv)
    margin, step = _dv(drv, KGEN + 'crit_margin'), _dv(drv, KGEN + 'rating_step_kw')
    s = sum((dec(v) for _, v in crit), D0)
    rated = ceil(s * margin / step) * step
    basis = (f"125 % of the live critical list {fmt(s, 2)} kW, rounded up in {gfmt(step)} kW steps "
             '(AQS-ELEC-007 / AQS-RED-001, NFPA 110 standby basis; owner ruling Q-040 2026-11-05); '
             "list: " + ', '.join(f'{k} {fmt(v, 2)}' for k, v in crit))
    return dict(crit=crit, crit_kW=s, rated=rated, basis=basis)


def _exercise_avg(rated, drv):
    """The NFPA 110 8.4.2 monthly exercise as a daily average (X-PAR-12 TF,
    A-M-350): rated x exercise load x exercise h x 12 months/365 d, over 24 h."""
    e_ex = dec(rated) * _dv(drv, KGEN + 'exercise_load_frac') * _dv(drv, KGEN + 'exercise_h') \
        * Decimal(12) / Decimal(365)
    return e_ex, e_ex / DAY


def _portfolio(prof):
    ents = prof['groups']['power_portfolio']['entries']
    return {k: ents[k]['value'] for k in ents}


def _entry(prof, key):
    grp, e = key.split('.', 1)
    return (prof['groups'].get(grp, {}).get('entries') or {}).get(e)


CF_DEFAULT = Decimal(35) / Decimal(100)                        # the generic-source default capacity factor (X-LOC-08)


def _phi(prof):
    return sum((dec(s['share']) * dec(s.get('stretch_output_frac', 0))
                for s in _portfolio(prof)['sources'] if s['role'] == 'primary'), D0)


def _mean_gen_per_kw(prof, eta):
    """portfolio.mean_generation_per_kW (AQS-PLAN-011 section 5.5): mean
    primary generation per kW of average demand through the worst stretch."""
    h, f = dec(_entry(prof, _portfolio(prof)['worst_stretch']['hours_entry'])['value']), _phi(prof)
    return ((DAY - h) + h / eta) / (DAY - f * h + f * h / eta)


def _pv_factor(drv, prof, eta):
    """portfolio.pv_factor: PV share x the worst-stretch correction, 1 for PV
    alone with no output in the stretch. prof None reads the reference
    portfolio convention through the driver book (share 1, no stretch output):
    the baseline profile binds it to 1 and the factor is profile data."""
    if prof is None:
        return D1
    pf = _portfolio(prof)
    pv = [s for s in pf['sources'] if s['role'] == 'primary' and s['kind'] == 'pv']
    if not pv:
        return D0
    h = dec(_entry(prof, pf['worst_stretch']['hours_entry'])['value'])
    f = _phi(prof)
    return dec(pv[0]['share']) * (DAY / (DAY - f * h + f * h / eta))


def _study_ok(prof, s):
    """portfolio._study (Q-024 revision, 2026-11-15): a flagged-only kind
    enters the balance as a designed source only with its completed study - a
    study id and the profile record it closes, carrying the dust fraction."""
    st = s.get('study')
    if not isinstance(st, dict) or not str(st.get('id', '')).strip():
        return False
    rec = _entry(prof, str(st.get('record', '')))
    return isinstance(rec, dict) and isinstance(rec.get('value'), dict) \
        and 'pv_stretch_output_frac' in rec['value']


def _grease_route(b, drv):
    """The A-M-480 shop-grease route re-solve (flow_graph/param/grease.py
    design(); F-20261110-08): the SKF relubrication need of every powered
    rotating unit, the soap stoichiometry on the selected thickener route, and
    the campaign kettle duty (feed heat + ASTM_C680 shell loss over the heater
    efficiency). Exact books; the route duty the v1 heat lane fed the power
    sizing as an in-memory override. Records nothing: the GREASE_* stamps
    belong to the specialty and fluoro lanes."""
    route = drv['grease_thickener']['value']
    assert route in ('CA', 'LI'), route
    units = []
    for n in b.data['nodes']:
        p = n.get('params') or {}
        cls = n.get('class') or ''
        if not p or p.get('presence') == 'absent' or cls in ('boundary', 'building') \
                or n.get('presence') == 'retired':
            continue
        qk = _kw(b, n['unit_id'])
        if qk > D0 and cls not in NONROT:
            units.append(n['unit_id'])
    gp = Decimal(5) / Decimal(1000) * _dv(drv, 'grease_bearing_D_mm') * _dv(drv, 'grease_bearing_B_mm')
    interval = _dv(drv, 'maint_rotating.lube_mo') * Decimal('365.25') / Decimal(12)
    grease = dec(len(units)) * _dv(drv, 'grease_points_per_unit') * gp / interval / 1000
    soap = grease * _dv(drv, 'grease_soap_frac')
    base = grease - soap
    msoap, nacid = (M_CASOAP, 2) if route == 'CA' else (M_LISOAP, 1)
    n_soap = soap / msoap                                       # kmol/d
    acid = n_soap * nacid * M_ACID
    thick = n_soap * (M_CAOH2 if route == 'CA' else M_LIOH)
    water_sap = n_soap * nacid * M_H2O
    wax_ox = acid / _dv(drv, 'grease_wax_ox_acid_yield')
    o2 = wax_ox * _dv(drv, 'grease_wax_ox_o2')
    vent = wax_ox + o2 - acid + water_sap
    wax = base + wax_ox
    z = dict(route=route, units=len(units), gp_g=gp, interval_d=interval, grease_kg_d=grease,
             soap_kg_d=soap, base_oil_kg_d=base, wax_kg_d=wax, wax_ox_kg_d=wax_ox, acid_kg_d=acid,
             o2_kg_d=o2, vent_kg_d=vent, thickener_kg_d=thick,
             caoh2_kg_d=thick if route == 'CA' else D0, lioh_kg_d=thick if route == 'LI' else D0,
             lime_draw_kg_d=D0, slake_h2o_kg_d=D0, reject_kg_d=D0)
    if route == 'CA':
        comp = (b.edges.get('IA-LIME-SHIP') or {}).get('composition') or {}
        f = dec(comp.get('CaO', 0))
        assert f > 0, 'grease: the ACID_PLANT residue carries no CaO on this acid route'
        cao = n_soap * M_CAO
        z['lime_draw_kg_d'] = cao / f
        z['slake_h2o_kg_d'] = n_soap * M_H2O
        z['reject_kg_d'] = z['lime_draw_kg_d'] - cao
    residual = wax + o2 + thick - grease - vent                 # the route identity (exact algebra; the
    assert abs(residual) <= grease / Decimal(10) ** 12          # 28-digit soap division leaves only dust)
    t_c = _dv(drv, 'grease_kettle_T_C_' + route.lower())
    camp, run_h = _dv(drv, 'grease_campaign_d'), _dv(drv, 'grease_run_h')
    vol = grease * camp / _dv(drv, 'grease_rho_kg_m3') / _dv(drv, 'grease_fill')
    d_m = max(_dv(drv, 'grease_min_kettle_D_m'), (Decimal(4) * vol / PI) ** (D1 / 3))
    # ASTM_C680 insulated cylinder [ASTM_C547, A-M-158]: smallest standard
    # thickness with the surface at or under 50 C; k = k_a + k_b T_mean
    r1 = d_m * 1000 / 2000
    thk_mm, loss_w = INSUL_THK[-1], D0
    for t in INSUL_THK:
        r2 = r1 + dec(t) / 1000
        k = Decimal('0.037') + Decimal('0.00017') * (t_c + Decimal(50)) / 2
        qq = (t_c - Decimal(25)) / ((r2 / r1).ln() / (2 * PI * k) + D1 / (2 * PI * r2 * Decimal(10)))
        ts = Decimal(25) + qq / (2 * PI * r2 * Decimal(10))
        thk_mm, loss_w = t, qq
        if ts <= Decimal(50):
            break
    loss = loss_w * d_m * Decimal('1.3')                        # heads and nozzles factor
    q_feed = (wax + thick) * _dv(drv, 'grease_cp_kJ_kgK') * (t_c - Decimal(25)) / Decimal('86.4')
    kw = (q_feed + loss * run_h / (camp * DAY)) / _dv(drv, 'grease_heater_eff') / 1000
    z.update(kettle_L=vol * 1000, kettle_D_mm=d_m * 1000, insul_mm=thk_mm, loss_W=loss, kw=kw,
             kettle_T_C=t_c, campaign_d=camp)
    return z


def _chain(b, inputs):
    """The power solve kernel: the port of docs-authority/_power_sizing.py
    plus the write_graph power() write half, on exact Decimal books. Returns
    the chain values, or None without the driver and site-profile payloads
    (the bridge contract)."""
    drv = inputs.get('drivers')
    prof = inputs.get('site_profile')
    if drv is None or prof is None:
        return None
    i_total, rect_ac = _ew_currents(b, drv)
    books = _census(b)
    census_sum = sum(books.values(), D0)
    p_bounding = qd(census_sum + rect_ac, 2)
    ref_rect = i_total * _dv(drv, 'ELEC.distribution-train.RECTIFIER.ref_case_cell_V') \
        / _dv(drv, 'ELEC.distribution-train.RECTIFIER.ref_case_CE') / 1000
    p_reference = qd(census_sum + ref_rect, 2)
    eta = _dv(drv, 'storage_round_trip')
    night = _dv(drv, 'night_hours')
    pf = _portfolio(prof)
    primary = next((s for s in pf['sources'] if s['role'] == 'primary'), None)
    kind = primary['kind'] if primary else 'pv'
    primary_unit = primary.get('unit', 'PV_ARRAY') if primary else 'PV_ARRAY'
    pvf = _pv_factor(drv, prof, eta)
    roof = None
    pv = {}
    if kind == 'pv':
        roof = _roof_close(drv, p_bounding, pvf)
        if roof is None:
            raise SystemExit('no roof fit - the array need at this profile exceeds the roof over the '
                             'whole bay-grid growth range (the site power study; AQS-PLAN-011, Q-024)')
        yld = _dv(drv, 'pv_yield_kWh_kWp_d') * _dv(drv, 'pv_roof_yield_factor') / pvf
        for k, p in (('bounding', p_bounding + roof['ext']['total_kW']),
                     ('reference', p_reference + roof['ext']['total_kW'])):
            pv[k] = dict(P_kW=p, **_oversized(p, night, eta, yld, _dv(drv, 'pv_system_derate'),
                                              _dv(drv, 'pv_oversize_factor'), _dv(drv, 'pv_dc_ac_ratio'), _inv_unit(b)))
    else:
        cf = dec(primary.get('capacity_factor', CF_DEFAULT))
        assert D0 < cf <= D1, f'{kind} capacity_factor {cf} must be above 0 and at most 1'
        share = dec(primary.get('share', 0))                    # F-20261113-01: the share restored
        for k, p in (('bounding', p_bounding), ('reference', p_reference)):
            st = _storage_book(p, night, eta)
            nameplate = qd(share * p / cf, 1)
            pv[k] = dict(P_kW=p, **st, nameplate_kWp=nameplate, nameplate_kw=nameplate, area_m2=0,
                         kind=kind, capacity_factor=cf, cloudy_yield_frac=cf, inverters=1,
                         inv_kW=p, export_peak_kW=D0, export_kWh_d_clear=D0, pv_base_kWp=nameplate)
    gen = _rating(b, drv)
    e_ex, e_avg = _exercise_avg(gen['rated'], drv)
    return dict(drv=drv, prof=prof, pf=pf, kind=kind, primary_unit=primary_unit,
                books=books, census_sum=census_sum, rect_ac=rect_ac, ref_rect=ref_rect,
                p_bounding=p_bounding, p_reference=p_reference, eta=eta, night=night,
                roof=roof, pv=pv, bounding=pv['bounding'], gen=gen, e_ex=e_ex, e_avg=e_avg,
                grease=_grease_route(b, drv))


def _inv_unit(b):
    """The per-inverter kW the SOL_ARK block books (the hybrid-inverter unit
    the store and the array distribute over)."""
    sp = _fresh_node(b, 'SOL_ARK_60K', 'params')
    return dec(sp['kW']) / dec(max(int(sp.get('count', 1)), 1))


@fn('backup_criticals', 'Q-040 (2026-11-05) BACKUP_GEN rating from the live critical list at 125 % in the '
    'commercial 5 kW step (AQS-ELEC-007/AQS-RED-001, NFPA 110 standby basis; backup_fuel.rating_kw); the '
    'X-PAR-12 NFPA 110 8.4.2 monthly exercise as a daily average (A-M-350)')
def backup_criticals(b, inputs):
    s = _chain(b, inputs)
    if s is None or 'BACKUP_GEN' not in b.nodes:
        return                                                  # the fuel-cell replacement lane is the balance family's
    drv = s['drv']
    gen = s['gen']
    basis = ('Q-040 live critical-list rating (AQS-ELEC-007/AQS-RED-001, NFPA 110 standby basis; '
             'backup_fuel.rating_kw) and the NFPA 110 8.4.2 exercise average (X-PAR-12 TF, A-M-350)')
    _set(b, 'BACKUP_GEN', 'params.rated_kW', float(gen['rated']), basis, 'Q-040')
    _set(b, 'BACKUP_GEN', 'params.rated_kW_basis',
         'flow_graph/param/backup_fuel.py rating_kw (single computation, owner ruling Q-040 2026-11-05): '
         + gen['basis'] + '; written by write_graph power(), read by docs-authority/_power_sizing.py and o2_close.py.',
         basis, 'Q-040')
    if isinstance(_fresh_node(b, 'BACKUP_GEN', 'continuous_kw'), dict):
        _set(b, 'BACKUP_GEN', 'continuous_kw.value', q(s['e_avg'], 4), basis, 'A-M-350')
        _set(b, 'BACKUP_GEN', 'continuous_kw.note',
             'X-PAR-12 TF: standby, NFPA 110 exercise average', basis, 'A-M-350')


@fn('grease_route', 'A-M-480 shop grease from the wax cut: the SKF relubrication need, the route '
    'stoichiometry and the campaign kettle (F-20261110-08 arithmetic). Records nothing: the GREASE_* '
    'stamps belong to the specialty and fluoro lanes; the v1 in-memory override dies with the '
    'single-sourced store book')
def grease_route(b, inputs):
    _chain(b, inputs)                                           # the derivation runs; the graph stays seed-faithful


@fn('power_ledger', 'X-PAR-07/X-PAR-08 roof close and extension hall on the A-M-231 demand census '
    '(AQS-ELEC-007, docs-authority/_power_sizing.py); X-ELS-02 load-basis (A-M-275) for the GEO_HP '
    're-solve of the heat family Q4 lift')
def power_ledger(b, inputs):
    s = _chain(b, inputs)
    if s is None or s['kind'] != 'pv':
        return                                                  # the generic path books no roof extension
    drv = s['drv']
    rf = s['roof']
    x = rf['ext']
    kw = qd(x['total_kW'], 4)
    basis = ('X-PAR-07 solver.roof_close extension hall on the A-M-231 demand census (AQS-ELEC-007); '
             'X-PAR-08 hvac (ASHRAE 90.1-2025 Table 6.8.1-2, IECC 2021 C402/C405, ASHRAE 62.1-2025, '
             'ISO 16798-3, NOAA_NORMALS_DFW)')
    assert 'EXT_HALL' in b.nodes and 'SF-EXT_HALL' in b.edges, \
        'power_ledger: the seed lacks the extension hall node/feed (builder topology)'
    cond = 'conditioned' if _dv(drv, 'ext_conditioned') else 'unconditioned'
    note = (f"X-PAR-07 solver.roof_close: {cond} extension {fmt(rf['added_m2'], 0)} m2; "
            f"lighting {fmt(x['light_kW'], 2)} kW (IECC 2021 C405, 10 % lit), "
            f"ventilation {fmt(x['vent_kW'], 2)} kW (ASHRAE 62.1-2025 air at COP per ASHRAE 90.1-2025 Table 6.8.1-2, "
            f"ISO 16798-3 fans), envelope {fmt(x['envelope_kW'], 2)} kW (IECC 2021 C402 roof and walls; envelope deltas "
            f"from the bounding station normals, AQS-SITE-002 Rev C).")
    if x.get('mode'):
        compare = rf.get('compare', {})
        note += (f" X-PAR-08: {x['mode']}-source heat pumps (ASHRAE 90.1-2025 Table 6.8.1-2), heating "
                 f"{fmt(x['Qh_kW'], 1)} kW and cooling {fmt(x['Qc_kW'], 1)} kW thermal average after internal gains "
                 f"{fmt(x['gains_kW'], 1)} kW and slab edge {fmt(x['slab_kW'], 2)} kW (IECC F-factor); loop pumping "
                 f"{fmt(x['pump_kW'], 2)} kW. Comparison: "
                 + '; '.join(f"{m} {fmt(c['footprint_m2'], 0)} m2, {fmt(c['ext_kW'], 2)} kW" for m, c in compare.items())
                 + '.')
        hv = {}
        for k, v in x.items():
            hv[k] = q(v, 3) if isinstance(v, Decimal) else v
        _set(b, 'EXT_HALL', 'params.hvac', hv, basis, 'X-PAR-08')
        if not x.get('bores'):
            assert 'hall_field' not in (b.nodes['GEO_GHEX'].get('params') or {}), \
                'power_ledger: the seed carries a hall bore field the air-source mode retires (builder topology)'
        if x.get('bores'):
            _set(b, 'GEO_GHEX', 'params.hall_field',
                 {'bores': int(x['bores']), 'depth_m': float(_dv(drv, 'gsh_bore_depth_m')),
                  'bore_m': qi(x['bore_m']), 'area_m2': q(x['bore_field_m2'], 0) if isinstance(x['bore_field_m2'], Decimal) else x['bore_field_m2'],
                  'location': 'under the EXT_HALL slab',
                  'basis': 'KAVANAUGH2014 bore length per kW peak block load; X-PAR-08, A-M-112'},
                 basis, 'A-M-112')
    _set(b, 'EXT_HALL', 'continuous_kw.value', q(kw, 4), basis, 'X-PAR-07')
    _set(b, 'EXT_HALL', 'continuous_kw.note', note, basis, 'X-PAR-07')
    _set(b, 'EXT_HALL', 'params.footprint_m2', float(rf['added_m2']), basis, 'X-PAR-07')
    _set(b, 'EXT_HALL', 'params.conditioned', bool(_dv(drv, 'ext_conditioned')), basis, 'X-PAR-07')
    _set(b, 'EXT_HALL', 'params.blocks', ['EXT_HALL_E', 'EXT_HALL_N'], basis, 'X-PAR-07')
    _set(b, 'EXT_HALL', 'params.duty',
         f"In 0.000 kg/d, out 0.000 kg/d, {fmt(kw, 3)} kW. Sheet docs-authority/duties/EXT_HALL.md.",
         basis, 'X-PAR-07')
    _rate(b, 'SF-EXT_HALL', q(kw, 4), 'kW', 'Equals EXT_HALL continuous_kw (X-PAR-07).', basis, 'X-PAR-07')
    # IA-PV-01 carries the extension delta (X-PAR-07): the fresh extension
    # less the seed feed the bus already carries. The note keeps one X-PAR-07
    # segment (the idempotence guard, ported as the string book it is).
    old = dec(b.edges['SF-EXT_HALL']['rate']['value']) if ('SF-EXT_HALL' in b.edges) else D0
    pv1 = dict(b.edges['IA-PV-01']['rate'])
    pv1['value'] = q(dec(pv1['value']) + kw - old, 4)
    if 'X-PAR-07' not in (pv1.get('note') or ''):
        pv1['note'] = (pv1.get('note') or '') + f' X-PAR-07 extension hall: +{fmt(kw, 2)} kW.'
    b.set_edge_rate('IA-PV-01', pv1, _prov(basis + '; the PV average carries the extension delta', 'X-PAR-07'))
    # X-ELS-02 (A-M-275): GEO_HP electrical = the re-solved Q4-bus lift S44
    # over the ground-source heating COP. S44 is the heat family's stamp: with
    # power before heat this reads the committed fixed point (overlay first,
    # seed fallback); a moved lift lands on the next solve.
    if 'S44' in b.edges and isinstance(_fresh_rate(b, 'S44'), (int, float)):
        s44 = dec(_fresh_rate(b, 'S44'))
        gkw = s44 / _dv(drv, 'gsh_cop_h')
        gb = ('X-ELS-02 load-basis (A-M-275): the GEO_HP electrical book re-solved from the heat family '
              'Q4-bus lift over the ground-source heating COP (drivers gsh_cop_h, ASHRAE 90.1-2025 class)')
        if b.nodes.get('GEO_HP') is not None:
            note = (f"X-ELS-02: Q4-bus lift S44 {fmt(s44, 4)} kW (write_graph heat re-solve, AQS-DUTY-010 dispatch: "
                    f"lift only on deficit) / ground-source heating COP {_dvs(drv, 'gsh_cop_h')} (drivers gsh_cop_h, "
                    f"ASHRAE 90.1-2025 class) = {fmt(gkw, 4)} kW; 2 x 100 % units (X-RED-07). Source-loop circulator "
                    f"sized by AQS-DUTY-076 (pump stamped on GEO_HP_CLOSED_LOOP, counted on the same bounding winter "
                    f"case, A-M-317).")
            _set(b, 'GEO_HP', 'continuous_kw.value', q(gkw, 4), gb, 'A-M-275')
            _set(b, 'GEO_HP', 'continuous_kw.note', note, gb, 'A-M-275')
            if 'SF-GEO_HP' in b.edges:
                _rate(b, 'SF-GEO_HP', q(gkw, 4), 'kW',
                      'X-ELS-02 load-basis (A-M-275). Feed equal to GEO_HP continuous_kw.', gb, 'A-M-275')


@fn('pv_dispatch', 'D75 (owner 2026-10-15): PV at pv_oversize_factor x the balancing nameplate '
    '(sizing.power.oversized, NREL_PVWATTS8; A-M-109); SOL_ARK hybrid-inverter block and the D75 '
    'interconnection (IEEE 1547-2018 Cat. B/III, UL 1741 SB, NEC 2026 705.11/705.20, ANSI C12.20); '
    'portfolio dispatch, PV primary or the generic share/capacity-factor source (X-LOC-08, F-20261113-01)')
def pv_dispatch(b, inputs):
    s = _chain(b, inputs)
    if s is None:
        return
    drv = s['drv']
    basis = ('D75 PV dispatch at pv_oversize_factor x the balancing nameplate (A-M-109, NREL_PVWATTS8, '
             'X-PAR-07 roof close); portfolio dispatch (X-LOC-08)')
    p = s['bounding']
    if s['kind'] != 'pv':
        # generic primary: nameplate = share x demand / capacity factor, from
        # the profile; storage books for every storage unit the portfolio names
        unit = s['primary_unit']
        if unit in b.nodes:
            gb = basis + '; generic primary sized by _power_sizing.py (demand / capacity factor)'
            _set(b, unit, 'params.nameplate_kw', float(p['nameplate_kw']), gb, 'X-LOC-08')
            _set(b, unit, 'params.capacity_factor', float(p['capacity_factor']), gb, 'X-LOC-08')
            _set(b, unit, 'params.kind', s['kind'], gb, 'X-LOC-08')
            _set(b, unit, 'params.basis',
                 f"{s['kind']} primary source sized by _power_sizing.py (demand / capacity factor)", gb, 'X-LOC-08')
            if isinstance(_fresh_node(b, unit, 'continuous_kw'), dict):
                _set(b, unit, 'continuous_kw.value', q(p['P_kW'], 4), gb, 'X-LOC-08')
                _set(b, unit, 'continuous_kw.note',
                     f"{s['kind']} primary: {fmt(p['P_kW'], 2)} kW demand / capacity factor "
                     f"{p['capacity_factor']} = {p['nameplate_kw']} nameplate.", gb, 'X-LOC-08')
        for sto in s['pf'].get('storage', []):
            su = sto.get('unit', '')
            if su in b.nodes and su != 'HYDRO_SET':
                _set(b, su, 'params.kW', ceil(p['store_kW']), basis, 'X-LOC-13')
                _set(b, su, 'params.kWh', ceil(p['store_kWh']), basis, 'X-LOC-13')
                _set(b, su, 'params.charge_kW', ceil(p['charge_kW']), basis, 'X-LOC-13')
                _set(b, su, 'params.discharge_kW', ceil(p['discharge_kW']), basis, 'X-LOC-13')
                _set(b, su, 'params.basis', 'worst-stretch storage sizing (X-LOC-13 model)', basis, 'X-LOC-13')
        return
    if 'PV_ARRAY' not in b.nodes or 'SOL_ARK_60K' not in b.nodes:
        return
    rf = s['roof']
    kwp = ceil(p['pv_kWp'])
    count = ceil(dec(kwp) / dec(_fresh_node(b, 'PV_ARRAY', 'params.module_kw')))
    pb = basis + '; PV_ARRAY roof block (IFC 2027 1205.3, NFPA 1 11.12, IECC 2021, ASHRAE 62.1, ISO 16798-3, ASCE 7-22)'
    _set(b, 'PV_ARRAY', 'params.nameplate_kw', kwp, basis, 'A-M-109')
    _set(b, 'PV_ARRAY', 'params.count', count, basis, 'A-M-109')
    _set(b, 'PV_ARRAY', 'params.area_m2', qi(rf['array_m2']), basis, 'A-M-235')
    _set(b, 'PV_ARRAY', 'params.mounting', 'roof only (X-PAR-07); ground field removed', basis, 'X-PAR-07')
    _set(b, 'PV_ARRAY', 'params.roof', {
        'footprint_mm': [int(rf['W_mm']), int(rf['D_mm'])], 'bays': [rf['bays_x'], rf['bays_y']],
        'footprint_m2': float(rf['footprint_m2']), 'extension_m2': float(rf['added_m2']),
        'roof_capacity_kWp': q(rf['pv_roof_kWp'], 1),
        'perimeter_pathway_mm': int(rf['layout']['perimeter_mm']), 'arrays': int(rf['layout']['arrays']),
        'extension_load_kW': q(rf['ext']['total_kW'], 2), 'roof_load_kPa': rf['load'],
        'basis': 'flow_graph/param/solver.py roof_close (IFC 2027 1205.3, NFPA 1 11.12, IECC 2021, '
                 'ASHRAE 62.1, ISO 16798-3, ASCE 7-22)'}, pb, 'X-PAR-07')
    _set(b, 'PV_ARRAY', 'params.oversize_factor', float(_dv(drv, 'pv_oversize_factor')), basis, 'A-M-109')
    _set(b, 'PV_ARRAY', 'params.balance_kWp', ceil(p['pv_base_kWp']), basis, 'A-M-234')
    _set(b, 'ZNBR2', 'params.charge_basis',
         f"D75 cloudy-day case: yield {fmt(p['cloudy_yield_frac'], 2)} x mean (NREL_PVWATTS8 hourly scaling; "
         'NREL_NSRDB distribution to verify, A-M-109); charge = PV peak on that day less direct load',
         basis, 'A-M-109')
    _set(b, 'SOL_ARK_60K', 'params.count', int(p['inverters']), basis, 'A-M-231')
    _set(b, 'SOL_ARK_60K', 'params.kW', float(p['inv_kW']), basis, 'A-M-231')
    _set(b, 'SOL_ARK_60K', 'params.dc_ac_ratio', float(_dv(drv, 'pv_dc_ac_ratio')), basis, 'A-M-231')
    _set(b, 'SOL_ARK_60K', 'params.interconnection', {
        'export_peak_kW': q(p['export_peak_kW'], 1), 'export_kWh_d_clear': qi(p['export_kWh_d_clear']),
        'standards': 'IEEE 1547-2018 Cat. B / III, UL 1741 SB listed; NEC 2026 705.11 supply-side connection, '
                     '705.20 disconnect; ANSI C12.20 class 0.2 bidirectional meter', 'decision': 'D75'},
        basis + '; SOL_ARK interconnection (IEEE 1547-2018 Cat. B / III, UL 1741 SB, NEC 2026 705.11/705.20, '
                'ANSI C12.20 class 0.2)', 'A-M-237')


@fn('znbr2_store_book', 'AQS-ELEC-007 store book P x night (A-M-062/179 round trip; D75 chain through the '
    'roof-close fixed point); the heat family read-back vehicle (F-20261110-08); AQS-ELEC-008 inverter '
    'distribution')
def znbr2_store_book(b, inputs):
    s = _chain(b, inputs)
    if s is None or s['kind'] != 'pv' or 'ZNBR2' not in b.nodes:
        return
    drv = s['drv']
    p = s['bounding']
    eta, night = s['eta'], s['night']
    store, store_in = p['store_kWh'], p['store_in_kWh']
    basis = ('AQS-ELEC-007 store book P x night at the round-trip driver (A-M-062/179); store P from the '
             'roof-close fixed point (A-M-231 census + EW rectifier AC + EXT_HALL extension heat + roof fit, '
             'docs-authority/_power_sizing.py); AQS-ELEC-008 inverter distribution')
    _set(b, 'ZNBR2', 'params.kW', ceil(p['store_kW']), basis, 'AQS-ELEC-007')
    _set(b, 'ZNBR2', 'params.kWh', ceil(store), basis, 'AQS-ELEC-007')
    _set(b, 'ZNBR2', 'params.charge_kW', ceil(p['charge_kW']), basis, 'AQS-ELEC-007')
    _set(b, 'ZNBR2', 'params.discharge_kW', ceil(p['discharge_kW']), basis, 'AQS-ELEC-007')
    _set(b, 'ZNBR2', 'params.distribution',
         f"distributed over the {int(p['inverters'])} hybrid inverters, {fmt(store / p['inverters'], 1)} kWh and "
         f"{fmt(p['charge_kW'] / p['inverters'], 1)} kW charge each (AQS-ELEC-008)", basis, 'AQS-ELEC-008')
    if isinstance(_fresh_node(b, 'ZNBR2', 'continuous_kw'), dict):
        _set(b, 'ZNBR2', 'continuous_kw.value', q(p['discharge_kW'], 4), basis, 'AQS-ELEC-007')
        _set(b, 'ZNBR2', 'continuous_kw.note',
             'X-ELS-02: solved continuous discharge rating from docs-authority/_power_sizing.py (AQS-ELEC-007, D75 '
             'chain; single writer write_graph power()): '
             f"discharge {fmt(p['discharge_kW'], 1)} kW, charge {fmt(p['charge_kW'], 1)} kW, {fmt(store, 0)} kWh over "
             f"{int(p['inverters'])} hybrid inverters (AQS-ELEC-008). Neither path is demand (storage); the charge draw "
             'rides IA-ESS-ZNBR2-CHG. Was the stale 60 kW study value.', basis, 'AQS-ELEC-007')
    # the store book vehicle the heat family reads back (X-THM-01 F-4). The
    # committed dict embeds the v1 heat-lane census; this fresh book is this
    # family's own census (the composition single source). Window arithmetic
    # identical to the heat family's window_book.
    win = DAY - night
    if win <= 0:
        win = DAY                                               # a zero window is never a real book
    loss = store_in - store
    avg, win_kw, chg = loss / DAY, loss / win, store_in / win
    _set(b, 'ZNBR2', 'params.cycling_thermal', {
        'kwh_d_in': q(store_in, 1), 'kwh_d_out': q(store, 1), 'round_trip': float(eta),
        'loss_kwh_d': q(loss, 1), 'avg_kW': q(avg, 2), 'window_h': float(win),
        'window_kW': q(win_kw, 2), 'charge_kW_window': q(chg, 2),
        'basis': (f'store {fmt(store, 0)} kWh/d (AQS-ELEC-007 P x night) at round trip {fmt(eta, 1)} '
                  f'(A-M-062/179): the round-trip difference is electrolyte heat; window_kW is the bounding heat '
                  f'rate with all the daily loss in the {fmt(win, 0)} h charge window; charge_kW_window '
                  f"{fmt(chg, 1)} kW is the charge electrical rate over the same window; rejected to the Q4 bus on "
                  'IA-ZNBR-HEAT and the terminal (A-M-455)')},
        basis + '; X-THM-01 F-4 store book (A-M-455)', 'A-M-455')


@fn('designed_sources', 'AQS-PLAN-011 section 5.5 worst-stretch balance at the portfolio shares; the '
    'profile dust-stretch design record (F-20261113-01); NASA Fission Surface Power 40 kW_e unit count '
    '= ceil(dust deficit / unit) + 1 spare (N+1), NASA MMRTG 110 W_e count = ceil(controls trickle / unit) '
    '(AQS-ELEC-007 critical list; Q-024 designed sources)')
def designed_sources(b, inputs):
    """The locale designed-source dispatch, field-driven off the profile's
    portfolio and its dust-stretch design record - no locale name anywhere.
    Stamps params.site_placement on placeholder units a designed source names
    (the locale worktree lane; the reference seed names none and records
    nothing). The scaling-replacement sizers (RAD_PANEL, LIO_BAT) stay with
    the site-scaling family per the ledger split."""
    drv = inputs.get('drivers')
    prof = inputs.get('site_profile')
    if drv is None or prof is None:
        return
    eta = _dv(drv, 'storage_round_trip')
    pf = _portfolio(prof)
    g_per_kw = _mean_gen_per_kw(prof, eta)
    rec = ((prof.get('groups', {}).get('power_portfolio', {}).get('entries', {})
            .get('dust_stretch_design', {}) or {}).get('value') or {})
    # the demand a non-roof locale books: the converged need less the EXT_HALL
    # roof extension, which exists to carry the roof PV (A-M-231/A-M-234)
    need = (b.data.get('mvs', {}).get('electrical', {}).get('need_kw', {}) or {}).get('value')
    need = dec(need) if isinstance(need, (int, float)) else D0
    ext_q = _kw(b, 'EXT_HALL')
    demand = need - ext_q
    basis = ('AQS-PLAN-011 section 5.5 worst-stretch balance at the portfolio shares; dust fraction from '
             'power_portfolio.dust_stretch_design (F-20261113-01); AQS-SITE-013 placement register')
    pv_share = D0
    for s in pf['sources']:
        if s['role'] == 'primary' and s.get('kind') == 'pv':
            pv_share = dec(s['share'])
    for s in pf['sources']:
        unit = s.get('unit', '')
        if unit not in b.nodes or b.nodes[unit].get('presence') != 'placeholder':
            continue
        if s.get('role') not in ('primary', 'backup') or not _study_ok(prof, s):
            continue
        if s['kind'] in FLAG_ONLY and s['kind'] == 'fission':
            unit_kw = dec(_fresh_node(b, unit, 'params.unit_kW_e'))
            if not demand or not unit_kw:
                continue
            frac = rec.get('pv_stretch_output_frac')
            frac = dec(frac) if frac is not None else D0
            g = g_per_kw * demand
            pv_dust = frac * pv_share * g
            deficit = demand - pv_dust
            duty = ceil(deficit / unit_kw)
            book = {'demand_kW': q(demand, 2), 'mean_generation_kW': q(g, 2), 'pv_share': float(pv_share),
                    'dust_pv_output_frac': float(frac), 'pv_dust_output_kW': q(pv_dust, 2),
                    'dust_deficit_kW': q(deficit, 2), 'unit_kW_e': float(unit_kw), 'count_duty': duty,
                    'count_installed_n_plus_1': duty + 1, 'installed_kW_e': q(dec(duty + 1) * unit_kw, 1),
                    'basis': 'AQS-PLAN-011 section 5.5 worst-stretch balance at the portfolio shares; dust fraction '
                             'from power_portfolio.dust_stretch_design (F-20261113-01); unit rating NASA_FSP; '
                             'one installed spare per the N+1 rule'}
        elif s['kind'] in FLAG_ONLY:
            crit = _critical_list(b, drv)
            trickle = next((dec(v) for k, v in crit if k == 'controls and instruments'), D0)
            unit_w = dec(_fresh_node(b, unit, 'params.unit_W_e'))
            if not trickle or not unit_w:
                continue
            count = ceil(trickle * 1000 / unit_w)
            book = {'critical_list_kW': q(sum((dec(v) for _, v in crit), D0), 2),
                    'controls_trickle_kW': q(trickle, 2), 'unit_W_e': float(unit_w), 'count': count,
                    'carries_W_e': q(dec(count) * unit_w, 1),
                    'basis': 'backup_fuel.critical_list controls slice (AQS-ELEC-007); unit rating NASA_RTG; '
                             'the kW-class criticals stay on the fission base and the fuel cell (F-20261113-01)'}
        else:
            continue                                            # non-designed kinds: not this lane
        _set(b, unit, 'params.site_placement',
             {'site': prof['site_id'], 'replaces': [], 'sizing': book,
              'register': 'AQS-SITE-013 (SITE_UNITS.md)'}, basis, 'F-20261113-01')


def mvs_book(b, inputs):
    """The mvs.electrical book, derived (D1/D2): need = the converged bounding
    demand incl. the extension; target = the mean-day average generation of
    the installed array = pv_oversize_factor x balancing energy / 24 (A-M-234).
    Pure: the v2 overlay has no graph-level lane yet, so the builder carries
    the committed block and the tests pin this derivation to it."""
    s = _chain(b, inputs)
    if s is None or s['kind'] != 'pv':
        return None
    drv = s['drv']
    p, rf = s['bounding'], s['roof']
    old = b.data.get('mvs', {}).get('electrical') or {}
    kwp = ceil(p['pv_kWp'])
    count = ceil(dec(kwp) / dec(_fresh_node(b, 'PV_ARRAY', 'params.module_kw')))
    target = p['pv_kWp'] * _dv(drv, 'pv_yield_kWh_kWp_d') * _dv(drv, 'pv_roof_yield_factor') \
        * _dv(drv, 'pv_system_derate') / DAY
    return {
        'bus_nodes': old.get('bus_nodes', ['SOL_ARK_60K', 'ZNBR2', 'RECTIFIER']),
        'storage_options': old.get('storage_options', ['ZNBR2', 'MEOH', 'PUMPED_HYDRO']),
        'need_kw': {'value': q(p['P_kW'], 2), 'unit': 'kW', 'status': 'study',
                    'note': f"write_graph power() live derivation (A-M-234 replaced_by; A-M-258): converged bounding "
                            f"demand incl. the EXT_HALL extension (roof_close {rf['bays_x']}x{rf['bays_y']} bays, ext "
                            f"{fmt(rf['ext']['total_kW'], 2)} kW)."},
        'target_kw': {'value': q(target, 2), 'unit': 'kW', 'status': 'study',
                      'note': 'write_graph power() live derivation: mean-day average generation of the installed array '
                              '= pv_oversize_factor x balancing energy / 24 (= 2.5 x need at the drivers basis; '
                              'A-M-234 formula, D75).'},
        'pv_module_kw': float(dec(_fresh_node(b, 'PV_ARRAY', 'params.module_kw'))), 'pv_count': count,
        'znbr_module_kw': q(p['inv_kW'] / p['inverters'], 6), 'znbr_count': int(p['inverters']),
        'rect_count': 1,
        'notes': ('write_graph power() (single writer, D1/D2/D4): need/target/PV/storage chain derived again per '
                  'A-M-234 replaced_by / A-M-258 from docs-authority/_power_sizing.py (demand = max(node continuous_kw, '
                  'SOL_ARK feed) + RECT-EW bounding AC, A-M-231) and solver.roof_close; pv_module_kw x pv_count = '
                  'PV_ARRAY.params.nameplate_kw; znbr_* = the SOL_ARK hybrid-inverter block the ZNBR2 store is '
                  'distributed over; rect_count = the single nine-channel RECTIFIER (Rev AC; RECT_EW remap, A-M-255).')}

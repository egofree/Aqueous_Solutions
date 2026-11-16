"""The GEO loop sizing family (family migration; reference writer
flow_graph/param/geo_loop.py `--write`, ledger row `sizing_geo_loop`, section B,
MIXED: split sizing -> this function, the sizing doc -> the renderer lane).
Unit task 02 for the GEO units (AQS-DUTY-076): GEO_GHEX (the shallow closed
bore field), GEO_HP (the only ladder lift, 2 x 100 % per X-RED-07) and
GEO_HP_CLOSED_LOOP (the source circulation). Design case = the survey-locked
GHEX ceiling (graph params, ST-ORC-01 survey hold: k_ground 1.5 W/m K,
T_source 285 K) and the issued winter lift duty on the graph. Bore metres from
the cited per-metre sustained capacity band [KAVANAUGH2014: 30-50 W/m; the
registered 35 W/m driver], the U-tube count and even bore split at 5 m
rounding, bore spacing and the 25 % propylene-glycol loop flow at dT 3 K
(registered), the DN ladder from the velocity limit, circulation on head at
the site gravity; heat pump at the graph COP basis (S44 lift / SF-GEO_HP
electric; the study COP 3.43 at 285 K, AQS-HEAT-STUDY-002 sec. 6); brazed-plate
source and condenser areas at U 2.0 kW/m2 K [PERRY9] and the 5 K approach. No
rates change on the graph. The committed graph carries every field the v1
stage stamps; that committed state is the golden this module reproduces.

Grid doctrine (owner ruling 2026-11-15): driver, seed and site-profile values
cross the boundary through dec() (the exact Decimal of the decimal repr);
arithmetic is exact Decimal. Dimensionless constants port as integer scaled
pairs with the scale in the name: the 1000 W/kW and 1000 mm/m books, the 5 m
bore-split grid, the 5, 25, 32, 40, 50, 65, 80 DN ladder, the DN-minus-8
clearance rule, pi as 3141592653589793/10^15. Schema fields quantise half-even
at the decimals the v1 schema stores: COP at 2 dp, areas at 3 dp, bore metres
required / header / circulation at 1 dp, flows and lifts at 4 dp (Python
round()'s tie rule); every count, bore depth and DN an integer, and driver int
books (q_per_m_W, spacing, dT, head) stay int through the blanket 4 dp store
the v1 writer applied to floats only. No float literals.

Disposition of the chains around this family (the strangler bridge):
- The sizing doc (docs-authority/sizing/GEO_LOOP.md, AQS-DUTY-076) is
  renderer-lane work. It consumes, from the fields this function stamps:
  GEO_GHEX design (Q_ceiling_kW_th, k_ground_W_mK, T_source_K, q_per_m_W,
  bores, bore_depth_m, bore_metres_installed, bore_metres_req,
  bore_spacing_m, loop_DN, loop_flow_kg_s, loop_fluid, loop_dT_K,
  circ_pump_W, header_m), the GEO_HP design (lift_kW_th, cop, modules,
  module_kW_th, source_area_m2, condenser_area_m2, hx_class, cop_basis) and
  the GEO_HP_CLOSED_LOOP design (design_case_kW_th, flow_kg_s, DN, dT_K,
  head_m, pump_W, duty).
- SEED READS, recorded: S44 (the Q4-bus lift) and SF-GEO_HP are the write_graph
  heat family's fields - read from the seed, not the overlay, exactly the
  committed fixed point v1 consumed at its stage point (a moved lift lands on
  the seed after the next committed pass; the pass-lag the v1 fixed-point loop
  hid). GEO_GHEX params (Q_GHEX_avail_kW_th, k_ground_W_mK, T_source_K) carry
  the survey lock; the v1 defaults (3.0 kW, 1.5 W/m K, 285 K) stand for a seed
  without them.
- SITE PROFILE: this function reads gravity.g_m_s2 (the pump-head arithmetic;
  v1's SITE.g()) from inputs['site_profile'].
- The X-ELS-02 (A-M-317) circulation-pump continuous_kw DEMAND stamp is the
  write_graph power family's book (already landed there, reading these params):
  this function stamps no kW.
- params.size_note: the v1 writer wrote it on all three units, but the
  specialty lane (X-SPEC) re-stamps the study envelope notes on GEO_GHEX and
  GEO_HP_CLOSED_LOOP later in the same regen pass, and the committed graph
  carries those - one writer per field: the GEO_HP note (which the specialty
  lane does not touch) is this family's; the other two notes are the specialty
  lane's and are not stamped here.
A solve without the driver payload or the profile records nothing, so the
bridge solve and the check stay byte-faithful to the seed.
"""
from decimal import Decimal, ROUND_CEILING, ROUND_HALF_EVEN

from flow_graph.v2.registry import fn

STAGES = 'sizing_geo_loop'                                     # ledger row, section B
GL = 'GEO.geo-loop.'                                           # the GEO sizing driver prefix (AQS-DUTY-076)
TAG = 'GEO loop sizing (flow_graph/param/geo_loop.py, AQS-DUTY-076)'
REF = 'AQS-DUTY-076'
DIA_GRID, BORE_SPLIT = 5, 5                                    # m, the even-split rounding grid (x 5 m)
DN_LADDER = (25, 32, 40, 50, 65, 80)                           # the pipe DN ladder
DN_CLEARANCE = 8                                               # DN minus 8 mm >= the velocity diameter
W_PER_KW, MM_PER_M = 1000, 1000                                # the unit-scaled books
PI = Decimal(3141592653589793) / Decimal(10) ** 15             # pi (scale 1e-15)
GH_STATUS = 'design_survey_locked (ST-ORC-01)'
GH_MATERIAL = 'HDPE DR-11 U-tubes, 1 in bore + horizontal runs; borehole grout thermal'
HP_REDUNDANCY = '2 x 100 % (X-RED-07)'
HP_MATERIAL = '316L plates, R410A-class refrigerant, propylene-glycol brine source'
CL_DUTY = ('source loop between the bore field and the heat-pump evaporators; S43 carries it on the graph '
           '(0 kW idle standby)')
CL_MATERIAL = 'HDPE DR-11 buried; 25 % propylene glycol (freeze protection to -10 C)'
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


def ceil_int(x):
    """math.ceil of an exact value."""
    return int(Decimal(x).to_integral_value(rounding=ROUND_CEILING))


def _prov(basis, ref=None):
    from flow_graph.v2.model import Prov
    return Prov(STAGES, basis, ref)


def _set(b, uid, path, value, basis, ref=None):
    b.set_node_field(uid, path, value, _prov(basis, ref))


def edge_kw(b, sid):
    """The seed rate book of an edge as an exact kW book, None/absent -> 0 (the
    v1 `value or 0`). Seed-only: S44/SF-GEO_HP are the heat family's fields and
    the committed graph is the fixed point this family sizes at."""
    e = b.edges.get(sid)
    val = (e or {}).get('rate', {}).get('value')
    return dec(val) if isinstance(val, (int, float)) else Decimal(0)


def bore_field(q_ceiling, q_per_m, depth_m):
    """The bore-field books: required metres at the per-metre capacity, the
    bore count (not below 2) and the even 5 m-rounded split."""
    bore_m = q_ceiling * W_PER_KW / q_per_m
    n_bore = max(2, ceil_int(bore_m / depth_m))
    depth = ceil_int(bore_m / n_bore / BORE_SPLIT) * BORE_SPLIT
    return bore_m, n_bore, depth


def loop_books(q_ceiling, cp, d_t, rho, v_limit):
    """The source-loop books at the ceiling: glycol mass flow, volume flow,
    the velocity-required inside diameter (mm) and the DN ladder pick."""
    m_loop = q_ceiling * W_PER_KW / (cp * W_PER_KW * d_t)       # kg/s
    q_loop = m_loop / rho                                       # m3/s
    id_req = (4 * q_loop / (PI * v_limit)).sqrt() * MM_PER_M    # mm
    dn = next(x for x in DN_LADDER if x - DN_CLEARANCE >= id_req)
    return m_loop, q_loop, id_req, dn


@fn('geo_loop', 'AQS-DUTY-076 unit task 02 (GEO)-02: GHEX bore field at the survey-locked ceiling (ST-ORC-01) '
    '[KAVANAUGH2014 35 W/m registered], the GEO_HP 2 x 100 % lift at the graph COP basis (X-RED-07, '
    'AQS-HEAT-STUDY-002 sec. 6) and the source circulation [PERRY9 plate class]; no rates change on the graph')
def geo_loop(b, inputs):
    drv = inputs.get('drivers')
    prof = inputs.get('site_profile')
    if drv is None or prof is None:
        return                                                  # the bridge contract: no payload, no stamps
    if not all(u in b.nodes for u in ('GEO_GHEX', 'GEO_HP', 'GEO_HP_CLOSED_LOOP')):
        return

    def dv(k):
        return drv[GL + k]['value']                             # the driver as written

    ghx = b.nodes['GEO_GHEX'].get('params') or {}
    q_ghex = dec(ghx.get('Q_GHEX_avail_kW_th', '3.0'))          # the survey-locked ceiling, graph (ST-ORC-01)
    k_ground = dec(ghx.get('k_ground_W_mK', '1.5'))
    t_source = dec(ghx.get('T_source_K', '285.0'))
    q_lift, p_el = edge_kw(b, 'S44'), edge_kw(b, 'SF-GEO_HP')   # the heat family's issued winter duty (seed reads)
    if not p_el:
        p_el = q_lift / dec(dv('geo_hp_cop_design'))
    cop = q_lift / p_el if p_el else dec(dv('geo_hp_cop_design'))
    g_m_s2 = dec(prof['groups']['gravity']['entries']['g_m_s2']['value'])   # site gravity (v1 SITE.g())
    # ---- GEO_GHEX: shallow closed bore field at the survey-locked ceiling ----
    bore_m, n_bore, depth = bore_field(q_ghex, dec(dv('ghex_q_per_m_W')), dec(dv('ghex_bore_depth_m')))
    m_total = n_bore * depth
    hdr_m = (n_bore - 1) * dv('ghex_bore_spacing_m')            # int book: driver spacing stays int
    m_loop, q_loop, id_req, dn = loop_books(q_ghex, dec(dv('glycol_cp_kJ_kgK')), dec(dv('glycol_dT_K')),
                                            dec(dv('glycol_rho_kg_m3')), dec(dv('glycol_v_m_s')))
    pump_w = dec(dv('glycol_rho_kg_m3')) * g_m_s2 * q_loop * dec(dv('loop_head_m')) / dec(dv('loop_pump_eff'))
    ghex_basis = (f'AQS-DUTY-076 GEO_GHEX at the survey-locked ceiling (graph params, ST-ORC-01; '
                  f'k_ground {q(k_ground, 4)} W/m K, T_source {q(t_source, 4)} K) and the per-metre capacity '
                  'driver ghex_q_per_m_W [KAVANAUGH2014 30-50 W/m band, registered]')
    for key, val, cite in (
            ('Q_ceiling_kW_th', q(q_ghex, 4), 'the graph ceiling param'),
            ('k_ground_W_mK', q(k_ground, 4), 'the graph survey param'),
            ('T_source_K', q(t_source, 4), 'the graph survey param'),
            ('q_per_m_W', dv('ghex_q_per_m_W'), 'the registered per-metre capacity driver'),
            ('bore_metres_req', q(bore_m, 1), 'ceiling x 1000 W/kW / per-metre W'),
            ('bores', n_bore, 'not below 2 bores (design-output at the locked survey values)'),
            ('bore_depth_m', depth, 'the even split at the 5 m rounding grid'),
            ('bore_metres_installed', m_total, 'bores x split depth'),
            ('bore_spacing_m', dv('ghex_bore_spacing_m'), 'the registered spacing driver'),
            ('header_m', q(hdr_m, 1) if isinstance(hdr_m, float) else hdr_m,
             '(bores - 1) x spacing on the header run'),
            ('loop_DN', dn, 'the DN ladder against the velocity diameter + 8 mm clearance'),
            ('loop_flow_kg_s', q(m_loop, 4), 'ceiling / (glycol cp x dT)'),
            ('loop_dT_K', dv('glycol_dT_K'), 'the registered loop rise driver'),
            ('loop_fluid', f"{dv('glycol_vol_pct')} % propylene glycol", 'the registered loop fluid driver'),
            ('circ_pump_W', q(pump_w, 1), 'rho g Q head / efficiency at the site gravity'),
            ('status', GH_STATUS, 'the survey-lock status text (design decision, verbatim)'),
            ('material', GH_MATERIAL, 'the material text (design decision, verbatim)')):
        _set(b, 'GEO_GHEX', 'params.design.' + key, val, ghex_basis, REF)
    # ---- GEO_HP: 2 x 100 % lift at the issued winter duty ----
    q_mod = max(q_lift, dec(dv('geo_hp_module_min_kW')))
    u_plate, d_t_plate = dec(dv('bp_ux_U_kW_m2K')), dec(dv('bp_ux_dT_K'))
    a_src = q_mod / (u_plate * d_t_plate)
    a_cond = (q_mod + p_el) / (u_plate * d_t_plate)             # the condenser rejects Q + W
    hp_basis = ('AQS-DUTY-076 GEO_HP at the issued winter duty: the seed Q4-bus lift S44 over the seed SF-GEO_HP '
                'book (graph COP basis; study COP 3.43 at 285 K, AQS-HEAT-STUDY-002 sec. 6), 2 x 100 % '
                '(X-RED-07), brazed plate at U 2.0 kW/m2 K and the 5 K approach [PERRY9]')
    for key, val, cite in (
            ('lift_kW_th', q(q_lift, 4), 'the seed S44 book'),
            ('electric_kW', q(p_el, 4), 'the seed SF-GEO_HP book (or lift / cop_design when unfed)'),
            ('cop', q(cop, 2), 'lift / electric at the graph books'),
            ('modules', 2, '2 x 100 % (X-RED-07)'),
            ('redundancy', HP_REDUNDANCY, 'the redundancy text (design decision, verbatim)'),
            ('module_kW_th', q(q_mod, 3), 'the lift, not below the module minimum driver'),
            ('source_area_m2', q(a_src, 3), 'module duty / (U x approach)'),
            ('condenser_area_m2', q(a_cond, 3), 'module duty + electrical / (U x approach)'),
            ('hx_class', f"brazed plate, U {dv('bp_ux_U_kW_m2K')} kW/m2 K at {dv('bp_ux_dT_K')} K approach (PERRY9)",
             'the plate-class text over the drivers (design decision)'),
            ('cop_basis', 'graph S44/SF-GEO_HP; study COP 3.43 at 285 K (AQS-HEAT-STUDY-002 sec. 6, KAVANAUGH2014)',
             'the COP basis text (design decision, verbatim)'),
            ('material', HP_MATERIAL, 'the material text (design decision, verbatim)')):
        _set(b, 'GEO_HP', 'params.design.' + key, val, hp_basis, REF)
    _set(b, 'GEO_HP', 'params.size_note', f'sized at the survey-locked design case, {TAG}',
         'the envelope note (design decision, verbatim; the GEO_GHEX and GEO_HP_CLOSED_LOOP notes are the '
         'specialty lane study boxes, one writer per field)', REF)
    # ---- GEO_HP_CLOSED_LOOP: the source circulation between GHEX and GEO_HP ----
    cl_basis = ('AQS-DUTY-076 GEO_HP_CLOSED_LOOP: the source circulation sized at the survey-locked ceiling '
                '(S43 carries it on the graph, 0 kW idle standby; X-ELS-02 A-M-317 keeps the demand stamp with '
                'the write_graph power family)')
    for key, val, cite in (
            ('design_case_kW_th', q(q_ghex, 4), 'the survey-locked ceiling'),
            ('flow_kg_s', q(m_loop, 4), 'the source-loop mass flow'),
            ('DN', dn, 'the DN ladder pick'),
            ('dT_K', dv('glycol_dT_K'), 'the registered loop rise driver'),
            ('head_m', dv('loop_head_m'), 'the head driver (int book stays int)'),
            ('pump_W', q(pump_w, 1), 'rho g Q head / efficiency at the site gravity'),
            ('duty', CL_DUTY, 'the duty text (design decision, verbatim)'),
            ('material', CL_MATERIAL, 'the material text (design decision, verbatim)')):
        _set(b, 'GEO_HP_CLOSED_LOOP', 'params.design.' + key, val, cl_basis, REF)

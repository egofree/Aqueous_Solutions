"""The sizing_evap_design family (family migration; reference writer
flow_graph/param/evap_design.py --write, ledger row `sizing_evap_design`,
section B, MIXED: split sizing -> this function, doc -> the renderer wave).
X-MFG-30 in-house MVR falling-film evaporators EVAP_ACID and EVAP_BASE, no
bought skid (owner decision 2026-10-15; AQS-DUTY-060, A-M-106/107/108). Each
unit: single-effect falling-film body at the driver body pressure, mechanical
vapour recompression at an IAPWS-IF97 driving difference, isentropic blower
[PERRY9_PUMP], minimum-wetting recirculation, counter-current feed/product/
condensate interchanger [INCROPERA7], trim heat only where the compressor work
does not cover the sensible deficit, triangular-pitch shell on the 50 mm grid,
and (acid only) the counter-current HCl column on the body from the Perry
vapour-liquid equilibrium [PERRY7_HCL_VLE], with the API 520 Part I relief
cases (fire on the body per ISO 23251 / API 521 at 21 % overpressure; blocked
outlet on the shell at 120 % flow and 10 % overpressure). The committed graph
carries every field the stage stamps; the committed params.design blocks are
the golden this function reproduces. The process family seed-reads this
family's MVR design block (its strangler input), so the composition order is
process -> evap_design; this function reads the process family's mass books
through the same bridge in return.

Grid doctrine (owner ruling 2026-11-15): driver and seed values convert at this
boundary by dec() (the exact Decimal of the decimal repr); the v1 quantise
points emit through rb() - book()/unbook(), the integer count of 10^-dp units,
half-even, with the dimension and scale cited at every call. Tube count, shell
diameter (50 mm grid), column DN, packed height and the whole-mm heights run as
native integers; the frame drivers are whole-mm integers and the size_mm sums
stay on that integer grid. Dimensionless constants port as integer scaled pairs
with the scale in the name (the mm/m and W/kW ladders, the 100 % overpressure
point, the 21 % / 10 % / 120 % relief fractions as 121/100, 11/10, 12/10, the
DN ladder, the 50 mm pitch grid). No float literals; the lint holds this.

The books that stay v1 float books by necessity, documented here: the design
and relief dicts. The reference writer quantises its solve dict in float space
(round() on doubles) and the chains behind it are transcendental in float space
(region-4 saturation [IAPWS_IF97] with sqrt, the isentropic works with powers,
the LMTD log, the API 520 gas area, the tsat and Perry-VLE bisections). Those
books reproduce the committed repr exactly through a float replica of the v1
expression over the same inputs (no literals; the floats come from the exact
boundary books by flo(), and the float-lane constants enter as the decimal
strings of the v1 literals). rb()'s float path converts through the exact
binary value (Fraction), so it is Python round()'s own tie rule and reproduces
the v1 round() book for book.

Mass books are prior-family fields (recorded): water, product, feed+added per
unit come from the process family's canonical evap mass books (the solver.evap
port in flow_graph/v2/functions/process.py, ledger row write_graph_process -
the v1 evap stage re-solved the same chain itself through solver.solve()), read
here through that family's pure _core kernel on the seed rates IA-ACID-01,
IA-GLASS-03, S08G and IA-BMIM, the leach/BMED drivers, the EVAP_ACID column
y_eq_body_pct seed read (inside the X-PAR-10 vent case) and the caustic route
drivers. The condensate HCl fraction is the evap_cond_hcl_wt driver; the
recycle book is water x fraction (the v1 float chain).

Disposition of the chains around this family (the strangler bridge):
- docs-authority/sizing/EVAP_DESIGN.md (AQS-DUTY-060) is the renderer wave's:
  the doc consumed the per-unit design tables (T_boil_C .. T_out_C), the two
  relief rows (W_kg_h, P1_kPa_abs, A_req_mm2, adequate), the trim sentence off
  trim_kW, the column books (stages, packed_mm, DN, height_mm, placement,
  cond_hcl_wt_pct, recycle_hcl_kg_d, y_eq_*), the HCl-options comparison (the
  v1 options() study helper - doc-only, renderer lane) and the solver feed/
  water books for its section 8 text; then appended the code-basis block
  (X-STD-01, the composer lane).
- params.relief_basis / params.relief_mm are CO-AUTHORED: this stage writes the
  case dict and the study figure, and the write_graph relief family re-solves
  the body area, bore and computed_by in place after this stage every pass
  (AQS-PAR-001 relief pass), leaving bore_req_mm appended. The committed tree
  carries that residue; the test enumerates the delta per field with the
  owner. The case inputs the relief family reads (P1_kPa_abs, T_K, M, k,
  W_kg_h) are this stage's books and land fresh.
- EVAP continuous_kw / SF-EVAP_* feed books are the process family's (the MVR
  kW stamps cite its X-PAR decision note); this function stamps none of them.
- The edge T stamps run value-and-basis on the outlet lines the v1 writer
  named: the condensate lines (IA-EVAP_*-COND), the acid product line
  (IA-ACID-01) and the base liquor/product lines (IA-BASE-PPT, IA-BASE-01),
  plus the acid condensate composition (HCl_wt, HCl_kg_d, composition_basis on
  IA-EVAP_ACID-COND).

The v1 machinery (disk write-back, the doc render, the stdout dump) does not
migrate: assignment replaces the field and its provenance in full. A solve
without the driver payload records nothing, so the bridge solve and the check
stay byte-faithful to the seed.
"""
import math
from decimal import Decimal, ROUND_HALF_EVEN
from fractions import Fraction

from flow_graph.v2.functions import process as PR             # the prior family's pure mass kernel
from flow_graph.v2.registry import fn

STAGE = 'evap_design'                                          # ledger row sizing_evap_design, provenance stage
EVK = 'DIGESTER.metals-leach-train.acid-base-regen.'           # U4b: sizing literals single-sourced from drivers.json (A-M-106/107/108)
TAG = 'X-MFG-30'
DUTY = 'AQS-DUTY-060'
T_BASIS = 'X-MFG-30 interchanger outlet (AQS-DUTY-060)'
SIZE_NOTE = 'L x W x H mm: body plus interchanger and compressor frame, in-house design X-MFG-30 (AQS-DUTY-060)'
COMPUTED_BY = 'flow_graph/param/evap_design.py (ISO23251; API520)'   # the v1 refs.cite keys, inlined
ORIFICE = 'API 526 D (71 mm2)'
CASE_BODY = 'fire, ISO 23251 / API 521 adequate drainage'
CASE_SHELL = 'blocked outlet, compressor at 120 % design flow'
COL_MATERIAL = 'borosilicate glass 3.3 sections (ISO 3585), PTFE Pall rings, PTFE-lined flanges (PERRY9_MAT)'
COL_PLACEMENT = ('free-standing beside the body on the same frame (L-1 headroom 6 m); vapour duct from the '
                 'separator to the column bottom, column bottoms back to the body')
DN_LADDER_MM = (50, 80, 100, 150, 200, 250, 300)               # the DN ladder (integers)
PITCH_GRID_MM = 50                                             # the shell diameter grid
F0 = Decimal('0.0')                                            # the v1 zero book (float lane)
DAY_S = Fraction(86400)                                        # s, the transport book's day
M_H2O = Decimal('18.02')                                       # kg/kmol, the relief and column M book
PSI_PER_KPA = Decimal('6.894757')                              # kPa per psi, the API 520 US-unit bridge
LB_PER_KG = Decimal('2.20462')                                 # lb per kg, the API 520 US-unit bridge
R_KJ = Decimal('8.314')                                        # kJ/(kmol K), the ideal-gas book
R_J = Decimal('461.5')                                         # J/(kg K), the steam R book (PERRY9)
ORIFICE_D_IN2 = Decimal('71.0')                                # in2, the API 526 D orifice area
OVER_FIRE = Decimal('121') / Decimal(100)                      # 21 % overpressure (ISO 23251)
OVER_SHELL = Decimal('11') / Decimal(10)                       # 10 % overpressure
FLOW_BLOCK = Decimal('12') / Decimal(10)                       # 120 % design flow (blocked outlet)
MM_PER_M = Fraction(1000)                                      # the mm/m ladder
S_PER_H = Fraction(3600)                                       # s/h
IN2_MM2 = Decimal('645.16')                                    # mm2 per in2 (API 520 conversion)
FIRE_F = Decimal('21000')                                      # Btu/h, the ISO 23251 fire input
SQFT_PER_M2 = Decimal('10.7639')                               # the fire-area bridge
BTU_KJ = Decimal('0.29307107')                                 # kJ per Btu
# region 4 of IAPWS-IF97 [IAPWS_IF97], the reference writer's own coefficient
# book: integer scaled pairs on a 1e-7 x 1e0 .. 1e-17 mixed scale
IAPWS_N = tuple(Decimal(x) for x in (
    '0.11670521452767e4', '-0.72421316703206e6', '-0.17073846940092e2', '0.12020824702470e5',
    '-0.32325550322333e7', '0.14915108613530e2', '-0.48232657361591e4', '0.40511340542057e6',
    '-0.23855557567849', '0.65017534844798e3'))
# Perry's 7th ed. tables 2-9 (water) and 2-10 (HCl) over aqueous HCl:
# log10 p[mmHg] = A - B/T per wt% row, linear in log p between rows
# [PERRY7_HCL_VLE]. A as exact decimals, B integer kelvin.
VLE_W = {6: (Decimal('8.99156'), 2282), 10: (Decimal('8.99864'), 2295), 14: (Decimal('8.97075'), 2300),
         18: (Decimal('8.98014'), 2323), 20: (Decimal('8.97877'), 2334), 22: (Decimal('9.02708'), 2363),
         24: (Decimal('8.96022'), 2356)}
VLE_H = {2: (Decimal('11.8037'), 4736), 4: (Decimal('11.6400'), 4471), 6: (Decimal('11.2144'), 4202),
         8: (Decimal('11.0406'), 4042), 10: (Decimal('10.9311'), 3908), 12: (Decimal('10.7900'), 3765),
         14: (Decimal('10.6954'), 3636), 16: (Decimal('10.6261'), 3516), 18: (Decimal('10.4957'), 3376),
         20: (Decimal('10.3833'), 3245), 22: (Decimal('10.3172'), 3125), 24: (Decimal('10.2185'), 2995)}
M_HCL = Decimal('36.461')                                      # kg/kmol HCl, the VLE mass book
M_WAT = Decimal('18.015')                                      # kg/kmol water, the VLE mass book


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


def rb(x, dp, cite):
    """The v1 round() book: quantise to `dp` decimals and render (scale named
    at the call). At 0 dp the integer book itself is the JSON number, as the
    v1 round() wrote it."""
    cnt = book(x, dp, cite)
    return cnt if dp == 0 else unbook(cnt, dp)


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


def _edge_field(b, sid, path, value, basis, ref=None):
    """An edge field beyond 'rate' (params.*): the same overlay."""
    b.computed[('edge', sid, path)] = (value, _prov(basis, ref))


def _dv(drv, key):
    """A driver value -> exact Decimal. drivers.json keys are flat dotted
    strings; a bare suffix also walks the acid-base-regen prefix."""
    if key in drv:
        return dec(drv[key]['value'])
    return dec(drv[EVK + key]['value'])


def _g(inputs):
    """SITE.g: apparent gravity from the site profile (m/s2)."""
    prof = inputs.get('site_profile')
    grp = ((prof or {}).get('groups') or {}).get('gravity', {}).get('entries') or {}
    if isinstance(grp.get('g_m_s2'), dict):
        return flo(dec(grp['g_m_s2']['value']))
    return flo(dec('9.80665'))                             # the baseline standard gravity


def _p_process_kpa(inputs):
    """SITE.p_process_kPa (A-M-401): the shell interior where the profile
    states one, else the external atmosphere."""
    prof = inputs.get('site_profile')
    atm = ((prof or {}).get('groups') or {}).get('atmosphere', {}).get('entries') or {}
    shell = atm.get('shell_pressure_kPa')
    if isinstance(shell, dict) and 'value' in shell:
        return flo(dec(shell['value']))                    # already kPa
    ext = atm.get('pressure_Pa')
    if isinstance(ext, dict) and 'value' in ext:
        return flo(dec(ext['value'])) / 1000
    return flo(dec('101325')) / 1000                       # the baseline standard atmosphere


# ---- the reference writer's sizing helpers (sizing/evaporator.py,
# ---- sizing/relief.py, sizing/hcl_vle.py), float replica lane ---------------

def psat_kpa(t_c):
    """Region-4 saturation pressure [IAPWS_IF97], kPa."""
    t = t_c + flo('273.15')
    th = t + flo(IAPWS_N[8]) / (t - flo(IAPWS_N[9]))
    a = th * th + flo(IAPWS_N[0]) * th + flo(IAPWS_N[1])
    bb = flo(IAPWS_N[2]) * th * th + flo(IAPWS_N[3]) * th + flo(IAPWS_N[4])
    c = flo(IAPWS_N[5]) * th * th + flo(IAPWS_N[6]) * th + flo(IAPWS_N[7])
    return (2 * c / (-bb + math.sqrt(bb * bb - 4 * a * c))) ** 4 * float(Fraction(1000))


def tsat_c(p_kpa):
    """Region-4 saturation temperature by the reference writer's 80-step
    bisection on [0, 370] C, C."""
    lo, hi = flo(F0), flo(Decimal('370.0'))
    for _ in range(80):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if psat_kpa(m) < p_kpa else (lo, m)
    return (lo + hi) / 2


def compressor_kw(m_kg_s, t1_c, p1_kpa, p2_kpa, k, eta):
    """Ideal-gas isentropic work with the steam R book [PERRY9_PUMP]:
    returns (shaft kW, kJ/kg)."""
    w = k / (k - 1) * flo(R_J) * (t1_c + flo('273.15')) * ((p2_kpa / p1_kpa) ** ((k - 1) / k) - 1)
    return m_kg_s * w / eta / float(Fraction(1000)), w / float(Fraction(1000))


def interchanger(f_kg_s, cp_f, t_f, v_kg_s, cp_v, t_v, p_kg_s, cp_p, t_p, approach):
    """Feed heated by condensate and product, hot outlets set to the cold-end
    approach, feed outlet capped so the hot-end approach also holds
    [INCROPERA7]."""
    to = t_f + approach
    q = v_kg_s * cp_v * (t_v - to) + p_kg_s * cp_p * (t_p - to)
    t_fo = t_f + q / (f_kg_s * cp_f)
    cap = min(t_v, t_p) - approach
    if t_fo > cap:
        t_fo = cap
        q = f_kg_s * cp_f * (t_fo - t_f)
        to = (v_kg_s * cp_v * t_v + p_kg_s * cp_p * t_p - q) / (v_kg_s * cp_v + p_kg_s * cp_p)
    lm = ((min(t_v, t_p) - t_fo) - (to - t_f)) / math.log((min(t_v, t_p) - t_fo) / (to - t_f)) \
        if abs((min(t_v, t_p) - t_fo) - (to - t_f)) > flo('1e-9') else (to - t_f)
    return dict(Q_kW=q, T_feed_out_C=t_fo, T_hot_out_C=to, LMTD_K=lm)


def fire_relief_kg_h(a_w_m2, latent_kj_kg):
    """Q = 21000 F A_w^0.82 Btu/h (adequate drainage) [ISO23251]; relieving
    vapour W = Q / latent: returns (kg/h, kW)."""
    q_btu_h = float(FIRE_F) * flo('1.0') * (a_w_m2 * flo(SQFT_PER_M2)) ** flo(Decimal('0.82'))
    return q_btu_h * flo(BTU_KJ) / float(Fraction(1000)) * float(S_PER_H) / latent_kj_kg, \
        q_btu_h * flo(BTU_KJ) / float(Fraction(1000))


def gas_c(k):
    """The API 520 gas-flow factor C = 520 sqrt(k (2/(k+1))^((k+1)/(k-1)))."""
    return 520 * math.sqrt(k * (2 / (k + 1)) ** ((k + 1) / (k - 1)))


def gas_area_in2(w_lb_h, k, p1_psia, t_r, z, m, kd=flo(Decimal('0.975'))):
    """Critical flow A = W/(C Kd P1 Kb Kc) sqrt(T Z/M) [API520 eq. 3]; Kd
    0.975 is the API 520 preliminary value for gas; Kb = Kc = 1."""
    return w_lb_h / (gas_c(k) * kd * p1_psia) * math.sqrt(t_r * z / m)


def _lp(tab, w, t):
    """One Perry fit row interpolation (log10 p[mmHg] = A - B/T), linear in
    log p between rows."""
    ks = sorted(tab)
    if w <= ks[0]:
        a, b = tab[ks[0]]
        return flo(a) - b / t
    for i in range(len(ks) - 1):
        if ks[i] <= w <= ks[i + 1]:
            f = (w - ks[i]) / (ks[i + 1] - ks[i])
            l1 = flo(tab[ks[i]][0]) - tab[ks[i]][1] / t
            l2 = flo(tab[ks[i + 1]][0]) - tab[ks[i + 1]][1] / t
            return l1 + f * (l2 - l1)
    a, b = tab[ks[-1]]
    return flo(a) - b / t


def bubble(w_pct, p_mmhg=flo(Decimal('760.0'))):
    """Liquid wt% HCl -> (T_C, vapour wt% HCl) at P, by the reference writer's
    80-step bisection on [330, 420] K."""
    lo, hi = flo(Decimal('330.0')), flo(Decimal('420.0'))
    for _ in range(80):
        t = (lo + hi) / 2
        s = 10 ** _lp(VLE_W, w_pct, t) + 10 ** _lp(VLE_H, w_pct, t)
        lo, hi = (t, hi) if s < p_mmhg else (lo, t)
    ph = 10 ** _lp(VLE_H, w_pct, t)
    pw = 10 ** _lp(VLE_W, w_pct, t)
    y = ph / (ph + pw)
    return t - flo('273.15'), 100 * y * flo(M_HCL) / (y * flo(M_HCL) + (1 - y) * flo(M_WAT))


def x_from_y(y_pct):
    """Liquid wt% in equilibrium with a vapour wt%, by bisection on [0, 20]."""
    lo, hi = flo(F0), flo(Decimal('20.0'))
    for _ in range(80):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if bubble(m)[1] < y_pct else (lo, m)
    return (lo + hi) / 2


def strip_stages(f_kg_s, x_f, b_kg_s, x_b, v_kg_s, y_top, nmax=60):
    """Counter-current column above the MVR body: feed liquid enters the top,
    product leaves the body, vapour goes to the blower. Stage-by-stage from the
    top on a mass basis (equimass overflow, study): x_n from equilibrium with
    y_n; y_{n+1} = (L x_n - B xB)/V. Returns ideal stages to reach xB."""
    liq = f_kg_s
    y = y_top
    n = 0
    while n < nmax:
        n += 1
        x = x_from_y(y)
        if x >= x_b:
            return n
        y = (liq * x - b_kg_s * x_b) / v_kg_s
        if y <= 0:
            return n
    return None


# ---- the design chain --------------------------------------------------------

def design(drv, inputs, mass, unit):
    """The v1 evap_design.design() port. mass: the process family's evap mass
    book (water/product/feed/added, exact Decimals). Returns the design dict
    in the v1 key order, relief dicts included."""
    acid = unit == 'EVAP_ACID'

    def v(k):
        return flo(_dv(drv, k))

    t_b = v('evap_bp_acid_C') if acid else v('evap_bp_base_C')
    p1 = v('evap_body_kPa')
    t_c = t_b + v('evap_dT_drive_K')
    p2 = psat_kpa(t_c)
    water = flo(dec(mass['water']))
    product = flo(dec(mass['product']))
    feed = flo(dec(mass['feed']))
    added = flo(dec(mass['added']))
    big_v = water / float(DAY_S)
    big_p = product / float(DAY_S)
    big_f = (feed + added) / float(DAY_S)
    comp_kw, w = compressor_kw(big_v, t_b, p1, p2, v('evap_k_steam'), v('evap_comp_eta'))
    comp_e = comp_kw / v('evap_motor_eta')
    lat = flo(_dv(drv, EVK + 'evap_latent_kJ_kg'))
    q = big_v * lat
    area = q * float(Fraction(1000)) / (v('evap_U_ff') * v('evap_dT_drive_K'))
    di = v('evap_tube_id_mm') / float(MM_PER_M)
    length = v('evap_tube_L_mm') / float(MM_PER_M)
    tubes = math.ceil(area / (math.pi * di * length))
    rec = v('evap_wet_min') * tubes * math.pi * di
    rho = flo(_dv(drv, EVK + 'evap_liquor_rho_kg_m3'))
    pump_kw = rec / rho * _g(inputs) * flo(_dv(drv, EVK + 'evap_pump_head_m')) * rho \
        / flo(_dv(drv, EVK + 'evap_pump_eta')) / float(Fraction(1000))
    cp_p = v('evap_cp_acid_prod') if acid else v('evap_cp_base_prod')
    ix = interchanger(big_f, v('evap_cp_feed'), v('evap_feed_T_C'), big_v,
                      flo(_dv(drv, EVK + 'evap_cond_cp_kJ_kgK')), t_c, big_p, cp_p, t_b, v('evap_approach_K'))
    a_ix = ix['Q_kW'] * float(Fraction(1000)) / (v('evap_U_ix') * ix['LMTD_K'])
    trim = big_f * v('evap_cp_feed') * (t_b - ix['T_feed_out_C']) - comp_kw
    trim_kw = max(flo(F0), trim)
    pitch = flo(_dv(drv, EVK + 'evap_tube_pitch_ratio')) * (di * float(MM_PER_M)
                                                            + 2 * flo(_dv(drv, EVK + 'evap_tube_wall_mm')))
    d_sh = math.ceil((flo(_dv(drv, EVK + 'evap_bundle_margin')) * pitch
                      * math.sqrt(tubes / flo(Decimal('0.907')))
                      + flo(_dv(drv, EVK + 'evap_shell_pitch_allowance')) * pitch) / PITCH_GRID_MM) * PITCH_GRID_MM
    height = length * float(MM_PER_M) + v('evap_sump_h_mm') + flo(_dv(drv, EVK + 'evap_head_h_mm')) \
        + flo(_dv(drv, EVK + 'evap_separator_h_mm'))
    # fire case on the body (ISO 23251 / API 521), set at body design, 21 % overpressure
    a_w = math.pi * d_sh / float(MM_PER_M) * v('evap_sump_h_mm') / float(MM_PER_M) \
        + math.pi * (d_sh / float(MM_PER_M)) ** 2 / 4
    w_f, q_f = fire_relief_kg_h(a_w, lat)
    p_site = _p_process_kpa(inputs)
    p1f = flo(OVER_FIRE) * v('evap_body_design_kPag') + p_site
    t_f = tsat_c(p1f) + (t_b - 100)
    a_f = gas_area_in2(w_f * flo(LB_PER_KG), v('evap_k_steam'), p1f / flo(PSI_PER_KPA),
                       (t_f + flo('273.15')) * flo(Decimal('1.8')), flo('1.0'), flo(M_H2O))
    # shell side blocked outlet: compressor at 120 % of design flow, 10 % overpressure
    w_b = flo(FLOW_BLOCK) * big_v * float(S_PER_H)
    p1b = flo(OVER_SHELL) * v('evap_shell_design_kPag') + p_site
    t_bk = tsat_c(p1b)
    a_b = gas_area_in2(w_b * flo(LB_PER_KG), v('evap_k_steam'), p1b / flo(PSI_PER_KPA),
                       (t_bk + flo('273.15')) * flo(Decimal('1.8')), flo('1.0'), flo(M_H2O))
    d_letter = flo(_dv(drv, EVK + 'evap_psv_orifice_D_in2'))  # in2, API 526 orifice D (smallest letter)
    k_steam = v('evap_k_steam')
    col = None
    if acid:   # counter-current column on the body, feed at the top (X-MFG-30 option d, AQS-DUTY-060 section 7)
        c_pct = flo(dec(drv['evap_cond_hcl_wt']['value'])) * 100
        ns = strip_stages(big_f, v('bmed_product_wt_acid') * 100, big_p, v('acid_conc_design_wt') * 100, big_v, c_pct)
        rho_v = p1 * flo(M_H2O) / (flo(R_KJ) * (t_b + flo('273.15')))
        d_col = math.sqrt(4 * big_v / rho_v / v('evap_col_u_m_s') / math.pi) * float(MM_PER_M)
        dn = next(x for x in DN_LADDER_MM if x >= d_col)
        recycle = water * flo(dec(drv['evap_cond_hcl_wt']['value']))   # the v1 water x fraction book
        col = dict(ideal_stages_incl_body=ns, column_stages=ns - 1, cond_hcl_wt_pct=c_pct,
                   y_eq_feed_pct=rb(bubble(v('bmed_product_wt_acid') * 100)[1], 3,
                                    'fraction wt%: the Perry VLE book at 3 dp'),
                   y_eq_body_pct=rb(bubble(v('acid_conc_design_wt') * 100)[1], 2,
                                    'fraction wt%: the Perry VLE book at 2 dp'),
                   packed_mm=rb((ns - 1) * v('evap_col_hetp_mm') * v('evap_col_margin'), 0,
                                'length mm: the packed bed book, whole mm'),
                   D_req_mm=rb(d_col, 1, 'length mm: the column diameter book at 1 dp'),
                   DN=dn, recycle_hcl_kg_d=rb(recycle, 2, 'mass_flow kg/d: the HCl recycle book at 2 dp'),
                   material=COL_MATERIAL)
        col['height_mm'] = col['packed_mm'] + int(_dv(drv, EVK + 'evap_col_skirt_mm'))
        col['placement'] = COL_PLACEMENT
        height = max(height, col['height_mm'])
    relief_body = dict(case=CASE_BODY, A_wetted_m2=rb(a_w, 3, 'area m2: the wetted area book at 3 dp'),
                       Q_kW=rb(q_f, 2, 'power kW: the fire duty book at 2 dp'),
                       W_kg_h=rb(w_f, 2, 'mass_flow kg/h: the relieving flow book at 2 dp'),
                       P1_kPa_abs=rb(p1f, 1, 'pressure kPa: the relieving pressure book at 1 dp'),
                       T_K=rb(t_f + flo('273.15'), 1, 'temperature K: the relieving temperature book at 1 dp'),
                       M_kg_kmol=flo(M_H2O), k=k_steam,
                       A_req_mm2=rb(a_f * flo(IN2_MM2), 2, 'area mm2: the required orifice book at 2 dp'),
                       orifice=ORIFICE, adequate=bool(a_f <= d_letter))
    relief_shell = dict(case=CASE_SHELL,
                        W_kg_h=rb(w_b, 2, 'mass_flow kg/h: the blocked-outlet flow book at 2 dp'),
                        P1_kPa_abs=rb(p1b, 1, 'pressure kPa: the relieving pressure book at 1 dp'),
                        T_K=rb(t_bk + flo('273.15'), 1, 'temperature K: the relieving temperature book at 1 dp'),
                        M_kg_kmol=flo(M_H2O), k=k_steam,
                        A_req_mm2=rb(a_b * flo(IN2_MM2), 3, 'area mm2: the required orifice book at 3 dp'),
                        orifice=ORIFICE, adequate=bool(a_b <= d_letter))
    return dict(unit=unit, T_boil_C=t_b, T_cond_C=rb(t_c, 2, 'temperature C: the condensing book at 2 dp'),
                p_body_kPa=p1, p_shell_kPa=rb(p2, 2, 'pressure kPa: the shell book at 2 dp'),
                ratio=rb(p2 / p1, 3, 'ratio: the compression ratio book at 3 dp'),
                water_kg_h=rb(big_v * float(S_PER_H), 3, 'mass_flow kg/h: the evaporation book at 3 dp'),
                duty_kW=rb(q, 2, 'power kW: the evaporation duty book at 2 dp'),
                comp_shaft_kW=rb(comp_kw, 3, 'power kW: the blower shaft book at 3 dp'),
                comp_elec_kW=rb(comp_e, 3, 'power kW: the blower electrical book at 3 dp'),
                w_kJ_kg=rb(w, 1, 'energy kJ/kg: the compressor work book at 1 dp'),
                kWh_per_t=rb((comp_e + pump_kw + trim_kw) / (big_v * flo(Decimal('3.6'))), 1,
                             'energy kWh/t: the specific energy book at 1 dp'),
                A_ff_m2=rb(area, 2, 'area m2: the falling-film book at 2 dp'),
                tubes=tubes, tube_id_mm=di * float(MM_PER_M), tube_L_mm=length * float(MM_PER_M),
                recirc_kg_h=rb(rec * float(S_PER_H), 1, 'mass_flow kg/h: the recirculation book at 1 dp'),
                pump_kW=rb(pump_kw, 3, 'power kW: the recirculation pump book at 3 dp'),
                shell_D_mm=d_sh, height_mm=rb(height, 0, 'length mm: the assembly height book, whole mm'),
                ix_Q_kW=rb(ix['Q_kW'], 2, 'power kW: the interchanger duty book at 2 dp'),
                ix_A_m2=rb(a_ix, 3, 'area m2: the interchanger area book at 3 dp'),
                T_feed_preheat_C=rb(ix['T_feed_out_C'], 1, 'temperature C: the feed preheat book at 1 dp'),
                T_out_C=rb(ix['T_hot_out_C'], 1, 'temperature C: the outlet book at 1 dp'),
                trim_kW=rb(trim_kw, 3, 'power kW: the trim heater book at 3 dp'),
                total_kW=rb(comp_e + pump_kw + trim_kw, 3, 'power kW: the total electrical book at 3 dp'),
                column=col, relief_body=relief_body, relief_shell=relief_shell)


def _masses(b, inputs):
    """The process family's evap mass books (prior-family fields, recorded):
    None without the driver payload (the bridge contract)."""
    s = PR._core(b, inputs)
    if s is None:
        return None
    return s['ea'], s['eb']


@fn('evap_design', 'X-MFG-30 in-house MVR falling-film evaporators EVAP_ACID and EVAP_BASE (AQS-DUTY-060; '
    'A-M-106/107/108): IAPWS-IF97 compression ratio, isentropic blower, minimum-wetting recirculation, '
    'counter-current interchanger, trim heat, 50 mm shell grid; the acid unit carries the counter-current HCl '
    'column [PERRY7_HCL_VLE] and the ISO 23251 / API 520 relief cases')
def evap_design(b, inputs):
    drv = inputs.get('drivers')
    if drv is None or not all(u in b.nodes for u in ('EVAP_ACID', 'EVAP_BASE')):
        return                                             # bridge contract: no drivers, no stamps
    masses = _masses(b, inputs)
    if masses is None:
        return
    basis = ('X-MFG-30 in-house MVR evaporator design (AQS-DUTY-060; A-M-106/107/108): falling-film body, '
             'mechanical vapour recompression, interchanger, in-house relief cases and the acid HCl column; '
             'mass books from the process family (solver.evap port, the strangler seed read)')
    relief_basis_note = ('; the write_graph relief family re-solves the body area, bore and computed_by in '
                         'place after this stage every pass (AQS-PAR-001 relief pass)')
    for unit, mass in (('EVAP_ACID', masses[0]), ('EVAP_BASE', masses[1])):
        r = design(drv, inputs, mass, unit)
        _set(b, unit, 'params.design', {k: v for k, v in r.items() if not k.startswith('relief')},
             basis, 'A-M-106')
        # size: body plus interchanger and compressor frame; the EVAP_ACID frame
        # also carries the column (X-PAR-10 frame share)
        frame_len = int(_dv(drv, EVK + 'evap_frame_len_mm'))
        frame_col = int(_dv(drv, EVK + 'evap_frame_col_mm'))
        frame_min_w = int(_dv(drv, EVK + 'evap_frame_min_w_mm'))
        frame_wid = int(_dv(drv, EVK + 'evap_frame_wid_margin_mm'))
        frame_acid = int(_dv(drv, EVK + 'evap_frame_acid_w_mm'))
        length_mm = r['shell_D_mm'] + frame_len + (r['column']['DN'] + frame_col if r.get('column') else 0)
        width_mm = max(frame_min_w, r['shell_D_mm'] + frame_wid) + (frame_acid if unit == 'EVAP_ACID' else 0)
        _set(b, unit, 'params.size_mm', [length_mm, width_mm, r['height_mm']], basis, 'A-M-106')
        _set(b, unit, 'params.size_note', SIZE_NOTE, basis, 'A-M-106')
        _set(b, unit, 'params.relief_mm',
             rb(math.sqrt(4 * flo(ORIFICE_D_IN2) / math.pi), 2,
                'length mm: the relief bore book at 2 dp'), basis, 'A-M-107')
        # One writer per field: evap records the CASE INPUTS of the relief basis;
        # the results (W book, area, bore, adequacy, computed_by) belong to the
        # write_graph relief family, which re-solves them in place after this
        # stage in the declared composition (AQS-PAR-001 relief pass).
        case_inputs = {k: v for k, v in r['relief_body'].items()
                       if k not in ('W_kg_h', 'A_req_mm2', 'bore_req_mm', 'computed_by', 'adequate')}
        case_inputs['shell_side'] = r['relief_shell']
        _set(b, unit, 'params.relief_basis', case_inputs, basis + relief_basis_note, 'A-M-107')
        _set(b, unit, 'params.design_kPa', flo(_dv(drv, 'evap_body_design_kPag')), basis, 'A-M-107')
        for sid in ([f'IA-{unit}-COND'] + (['IA-ACID-01'] if unit == 'EVAP_ACID'
                                           else ['IA-BASE-PPT', 'IA-BASE-01'])):
            if sid in b.edges:
                _edge_field(b, sid, 'params.T_C', r['T_out_C'], basis, 'A-M-106')
                _edge_field(b, sid, 'params.T_basis', T_BASIS, basis, 'A-M-106')
        if unit == 'EVAP_ACID' and 'IA-EVAP_ACID-COND' in b.edges:
            c = r['column']
            _edge_field(b, 'IA-EVAP_ACID-COND', 'params.HCl_wt', c['cond_hcl_wt_pct'] / 100, basis, 'A-M-108')
            _edge_field(b, 'IA-EVAP_ACID-COND', 'params.HCl_kg_d', c['recycle_hcl_kg_d'], basis, 'A-M-108')
            _edge_field(b, 'IA-EVAP_ACID-COND', 'params.composition_basis',
                        'column top vapour, PERRY7_HCL_VLE (AQS-DUTY-060 section 7)', basis, 'A-M-108')

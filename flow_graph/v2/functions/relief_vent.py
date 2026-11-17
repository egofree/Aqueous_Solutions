"""The write_graph relief and vent family (family migration; reference writer
flow_graph/param/write_graph.py, commands `relief` and `vent`, ledger rows
`write_graph_relief` and `write_graph_vent`, PHYSICS; vent depends_on relief
in the reference manifest, and this module keeps that order).

The `relief` command: pressurised nodes (params.relief_mm present, design_kPa
above the atmospheric study band) are sized by API 520 Part I critical-flow gas
orifice area (flow_graph/param/sizing/relief.py); the case inputs are read from
params.relief_basis, and the results (required area, bore, adequacy) are
written back into the same book. The three gas receiver banks take the X-SAF-05
API 521 fire case per half bank (flow_graph/param/fire.py receiver_fire,
A-M-188), which governs relief_mm. Nodes without an API 520 case are marked
atmospheric. The `vent` command: API 2000 normal venting for every atmospheric
node (X-PAR-03, A-M-155) - pump-in/out breathing from the node's daily liquid
movement in the transfer window, thermal breathing on the sized envelope
volume, the open-vent bore at min(driver vent_dP_Pa, 25 % of design) [PERRY9
orifice], DN 25 minimum - and the A-M-174 design pressure from the actual
cases: vapour space at 4 x vent dP plus the full-height hydrostatic head, with
the A-M-182 hold-up head where the unit has no sized height. The committed
graph carries every field this family stamps; that committed state is the
golden this module reproduces.

Grid doctrine (owner ruling 2026-11-15): seed case inputs (P1_kPa_abs, T_K,
M_kg_kmol, k, Z, W_kg_h), design fields (design_kPa, relief_mm, size_mm,
H_mm, OD_mm, tube_m, banks V_m3) and drivers arrive as v1 floats and are
converted at this boundary by dec() (exact Decimal of the decimal repr); the
dimension of each seed read is named at the call. Arithmetic is exact
rational/Decimal; schema fields are quantised half-even (Python round()'s tie
rule) at the decimals the v1 writer stored - 2 dp on A_req_mm2 and
bore_req_mm, 3 dp on the fire-case book, 3 dp on the vent volumes and
breathing rates, 4 dp on the pump terms, 1 dp on vent_bore_req_mm, integral
vent_dP_Pa, vent_DN and the whole-mm relief_mm ceiling. The scale is named at
each call. Dimensionless constants port as integer scaled pairs with the scale
in the name: 645.16 mm2/in2 -> 64516/100, 2.20462 lb/kg -> 220462/100000,
6.894757 kPa/psi -> 6894757/1000000 (the relief caller's conversion),
0.145038 psi/kPa -> 145038/1000000 (the fire caller's own conversion, kept as
published), 1.8 deg R/K -> 9/5, Kd 0.975 -> 975/1000, the fire constants
0.1406 -> 1406/10000, Tw 1559.67 R -> 155967/100, F' floor 0.01 -> 1/100,
exponents 1.25 -> 5/4, 0.6625 -> 53/80, 0.82 -> 41/50, 10.7639 ft2/m2 ->
107639/10000, 0.29307107 kJ/Btu -> 29307107/100000000, R 8314
J/(kmol K), set 1.21 -> 121/100, depressuring 900 s and 3600 s/h, latent
282 kJ/kg; API 2000 volume factor 2.0 -> 2, Cd 0.61 -> 61/100, air 1.293
kg/m3 -> 1293/1000, 3600 s/h; vent fractions 0.25 -> 1/4 and 4 x vent dP; the
site baseline gravity and process pressure read from flow_graph/param/site.py's
baseline profile (as process.py ports them); pi on a
1e-15 scale. No float literals.

Seed reads from prior families (recorded dependencies, the strangler bridge):
- relief_basis case inputs: cold_box (CRYO_H2/O2/CO2 receivers), evap_design
  (EVAP_ACID/EVAP_BASE fire and shell-side cases), the H2-compressor chain per
  A-M-196 (H2O_ELYZ blocked outlet). This family computes FROM them, never
  re-derives them.
- vent reads params.sizing.size_mm / params.size_mm and design.H_mm (the
  sizing families' geometry), node class, the liquid kg/d edge census, and the
  design_kPa seed (the vent dP cap reads the committed design pressure).
- The site profile constants enter only through the baseline pair above.

Disposition of the chains around this family:
- The relief REGISTER (docs-authority/RELIEF_REGISTER.md, ledger row
  doc_relief_register) is a renderer over these stamps; it does not migrate
  here.
- The compressor interstage recalculation lives in the register renderer, not
  in the v1 relief command; nothing of it stamps the graph.
- sizing/relief.py liquid_area_in2 has no caller in either command; it is not
  ported. The gas chain (gas_C, gas_area_in2, equiv_bore_mm), the open-vent
  orifice and the fire case are ported in full.
- The hold-up head branch (A-M-182) ports in full as holdup_head_m; on the
  committed seed every atmospheric node has a sized height, so the branch is
  exercised only through the pure function (spot-checked in the tests).

The v1 machinery (disk write-back, the stdout census) does not migrate:
assignment replaces the field and its provenance in full. The relief command's
atmospheric mark replaces the relief_basis book in full - exactly as v1 does
before vent re-sizes it - so the relief -> vent pair reproduces the committed
book and key order. A solve without the driver payload records nothing, so the
bridge solve and the check stay byte-faithful to the seed.
"""
from decimal import Decimal, ROUND_CEILING, ROUND_HALF_EVEN

from flow_graph.param import site as SITE          # the baseline Earth constants (X-LOC-03)

from flow_graph.v2.registry import fn

STAGE_R = 'relief'                                             # provenance stage, relief command
STAGE_V = 'vent'                                               # provenance stage, vent command
D = Decimal
D0, D1 = Decimal(0), Decimal(1)
PI = Decimal(3141592653589793) / D(10) ** 15                   # pi (scale 1e-15)
# API 520 Part I (sizing/relief.py), US customary as published
IN2_MM2 = Decimal(64516) / Decimal(100)                        # mm2 per in2
LB_PER_KG = Decimal(220462) / D(10) ** 5                       # 2.20462 lb/kg
KPA_TO_PSI = Decimal(6894757) / D(10) ** 6                     # 6.894757 kPa/psi (relief caller)
PSI_PER_KPA = Decimal(145038) / D(10) ** 6                     # 0.145038 psi/kPa (fire caller)
R_F = D(9) / D(5)                                              # deg Rankine per kelvin
KD_GAS = Decimal(975) / Decimal(1000)                          # API 520 preliminary gas Kd
K_DEFAULT = D(7) / D(5)                                        # isentropic k fallback 1.4
# API 521 fire case (fire.py receiver_fire; X-SAF-05, A-M-188)
F_PRIME = Decimal(1406) / D(10) ** 4                           # 0.1406 environmental factor numerator
TW_R = Decimal(155967) / Decimal(100)                          # 1100 F + 459.67 = 1559.67 R wall
F_PRIME_MIN = D(1) / Decimal(100)                              # F' floor 0.01
EXP_125 = D(5) / D(4)                                          # (Tw - T1)^1.25
EXP_06625 = D(53) / D(80)                                      # T1^0.6625
EXP_082 = D(41) / D(50)                                        # A^0.82 (API 521 liquid)
FT2_M2 = Decimal(107639) / D(10) ** 4                          # 10.7639 ft2/m2
BTU_KJ = Decimal(29307107) / D(10) ** 8                        # 0.29307107 kJ/Btu
R_UNIV = D(8314)                                               # J/(kmol K), fire.py rho book
FIRE_SET = D(121) / Decimal(100)                               # 121 % of design gauge
DEPRESS_S = D(900)                                             # 15 min depressuring (API 521 5.20)
S_PER_H = D(3600)                                              # s per h
LATENT_KJ_KG = D(282)                                          # CO2 latent heat (NIST_WEBBOOK)
M_LIQUID = D(40)                                               # kg/kmol, the fire.py liquid test
T_LIQUID = D(273)                                              # K, the fire.py liquid test
GAS_FIRE = ('CRYO_H2', 'CRYO_O2', 'CRYO_CO2')                  # fire.py GAS_FIRE receiver banks
FIRE_METHOD = 'API 521 7th ed. 4.4.13.2.4 (API521_2020)'
COMPUTED_BY = 'flow_graph/param/sizing/relief.py gas_area_in2 (API520)'
RELIEF_MM_BASIS = 'governing of blocked outlet and fire case per half bank, rounded up to whole mm'
# API 2000 normal venting (sizing/vent.py, [API2000_2020] 3.3.2 SI + [PERRY9] orifice)
K_VOL = D(2)                                                   # out-breathing volume factor 2.0
CD = D(61) / Decimal(100)                                      # orifice discharge coefficient 0.61
RHO_AIR = Decimal(1293) / Decimal(1000)                        # 1.293 kg/m3 vent air
VENT_DP_FRAC = D(1) / D(4)                                     # vent dP held to 25 % of design
DESIGN_DEFAULT_KPA = D(2)                                      # the `design_kPa or 2` fallback, kPa
VENT_DP_MULT = D(4)                                            # vapour case at 4 x vent dP
PA_PER_KPA = D(1000)                                           # Pa per kPa
MM3_PER_M3 = D(10) ** 9                                        # mm3 per m3
DNS = (25, 32, 40, 50, 65, 80, 100, 125, 150, 200, 250, 300)   # DN ladder, mm, 25 minimum
# site profile baseline (flow_graph/param/site.py; as process.py ports them)
G_SITE = Decimal(str(SITE.g(SITE.BASELINE)))                   # m/s2 apparent gravity
P_PROC_KPA = Decimal(str(SITE.p_atm_Pa(SITE.BASELINE))) / D(10) ** 3   # kPa process-space absolute pressure
ATM_METHOD = 'API 2000 normal venting (API2000_2020), flow_graph/param/sizing/vent.py, A-M-155'
ATM_MARK = {'case': 'atmospheric',
            'method': 'not an API 520 case; tank venting per API Std 2000 at unit task 07',
            'relief_mm_status': 'atmospheric; design pressure set by the vent stage (A-M-174)'}


def dec(value):
    """A v1 float/int/str -> exact Decimal at the boundary (decimal repr)."""
    return Decimal(str(value))


def q(x, dp):
    """Quantise an exact value to `dp` decimals, half-even - Python round()'s
    documented tie rule, the rounding the v1 writer used; scale named at the
    call. Returns the JSON float the schema stores."""
    f = float(D(x).quantize(D1.scaleb(-dp), rounding=ROUND_HALF_EVEN))
    return float(0) if f == 0 else f                           # no signed zeros in the book


def qi(x):
    """round(x) as v1 wrote it: half-even to an integer."""
    return int(D(x).quantize(D1, rounding=ROUND_HALF_EVEN))


def qceil(x):
    """math.ceil on an exact book (whole-mm / half-kPa ceilings)."""
    return int(D(x).to_integral_value(rounding=ROUND_CEILING))


def fmt(x, dp):
    """The f'{x:.dpf}' text of an exact value (half-even at dp)."""
    return f'{D(x).quantize(D1.scaleb(-dp), rounding=ROUND_HALF_EVEN):f}'


def _prov(stage, basis, ref=None):
    from flow_graph.v2.model import Prov
    return Prov(stage, basis, ref)


def _set(b, uid, path, value, stage, basis, ref=None):
    b.set_node_field(uid, path, value, _prov(stage, basis, ref))


def gas_C(k):
    """API 520 Part I flow factor C(k) = 520 sqrt(k (2/(k+1))^((k+1)/(k-1))),
    dimensionless; exact on Decimal books (the fractional power is exact-order
    Decimal exponentiation, as process.py's Perry fits use)."""
    return D(520) * (k * (D(2) / (k + D1)) ** ((k + D1) / (k - D1))).sqrt()


def gas_area_in2(w_lb_h, k, p1_psia, t_r, z, m, kd=KD_GAS, kb=D1, kc=D1):
    """API 520 Part I eq. 3 critical gas orifice area, in2:
    A = W / (C Kd P1 Kb Kc) sqrt(T Z / M) [API520]."""
    return w_lb_h / (gas_C(k) * kd * p1_psia * kb * kc) * (t_r * z / m).sqrt()


def equiv_bore_mm(a_in2):
    """The equivalent bore of an orifice area: d = sqrt(4 A 645.16 / pi), mm."""
    return (D(4) * a_in2 * IN2_MM2 / PI).sqrt()


def fire_relief_kg_h(a_wetted_m2, latent_kj_kg, f=D1):
    """API 521 liquid fire relief: Q = 21000 F A^0.82 Btu/h on the wetted area,
    relieved as vapour at the latent heat -> (kg/h, kW) [API521_2020]."""
    q_btu_h = D(21000) * f * (a_wetted_m2 * FT2_M2) ** EXP_082
    kj_h = q_btu_h * BTU_KJ                                    # kJ/h through 0.29307107 kJ/Btu
    return kj_h / 1000 * S_PER_H / latent_kj_kg, kj_h / 1000


def receiver_fire(design, rb, design_kpa, p_proc_kpa=P_PROC_KPA):
    """API 521 fire case on a receiver tube bank - the port of
    flow_graph/param/fire.py receiver_fire (X-SAF-05, A-M-188). One relief
    valve per manifolded half; each half sized for its own tubes. Gas-filled:
    A = F' A' / sqrt(P1), F' = 0.1406/(C Kd) (Tw - T1)^1.25 / T1^0.6625 (USC),
    Tw 1559.67 R, F' floor 0.01. Liquid CO2: 21000 F A^0.82 Btu/h relieved as
    vapour at the 282 kJ/kg latent heat. P1 = 121 % of design gauge + process
    pressure. Depressuring (API 521 5.20): to 50 % design in 900 s. `design`
    and `rb` are the seed param books (tubes, OD_mm, tube_m, banks V_m3;
    M_kg_kmol, k, Z, T_K, P1_kPa_abs), all exact at the boundary."""
    m_kg_kmol = dec(rb['M_kg_kmol'])                           # kg/kmol
    kappa = dec(rb['k'])                                       # isentropic exponent
    z = dec(rb['Z'])                                           # compressibility
    t_n = dec(rb['T_K'])                                       # K, normal relief temperature
    tubes = int(design['tubes'])                               # tubes per bank set
    od_m = dec(design['OD_mm']) / 1000                         # m, tube outside diameter
    tube_m_len = dec(design['tube_m'])                         # m, exposed tube length
    a = tubes * PI * od_m * tube_m_len                         # m2 exposed
    ah = a / D(2)                                              # m2 per manifolded half
    p1 = FIRE_SET * design_kpa + p_proc_kpa                    # kPa abs at the fire case
    p_set = design_kpa + p_proc_kpa                            # kPa abs at set
    liquid = m_kg_kmol > M_LIQUID and t_n < T_LIQUID           # the fire.py liquid-CO2 test
    if not liquid:
        t1 = t_n * p1 / dec(rb['P1_kPa_abs'])                  # K, gas at relieving
        t1_r = t1 * R_F                                        # deg R
        f_prime = max(F_PRIME_MIN, F_PRIME / (gas_C(kappa) * KD_GAS)
                      * (TW_R - t1_r) ** EXP_125 / t1_r ** EXP_06625)
        a_in2 = f_prime * ah * FT2_M2 / (p1 * PSI_PER_KPA).sqrt()
    else:
        w_fire, _kw = fire_relief_kg_h(ah, LATENT_KJ_KG)
        t1 = t_n + D(30)                                       # K, the fire.py liquid T1
        a_in2 = gas_area_in2(w_fire * LB_PER_KG, kappa, p1 * PSI_PER_KPA, t1 * R_F, z, m_kg_kmol)
    v = sum((dec(bank['V_m3']) for bank in design['banks']), D0)   # m3 bank volume
    rho = lambda p_kpa: p_kpa * PA_PER_KPA * m_kg_kmol / (R_UNIV * z * t_n)   # kg/m3 ideal gas
    m_depress = D0 if liquid else v * (rho(p_set) - rho(D(1) / D(2) * design_kpa + p_proc_kpa))
    w_depress = D(2) * m_depress / DEPRESS_S * S_PER_H         # kg/h to 50 % design in 900 s
    a_depress = gas_area_in2(w_depress * LB_PER_KG, kappa, p_set * PSI_PER_KPA, t_n * R_F, z,
                             m_kg_kmol) if m_depress else D0
    return dict(exposed_m2=a, per_half_m2=ah, P1_kPa_abs=p1, T1_K=t1,
                A_req_mm2_per_half=a_in2 * IN2_MM2, bore_req_mm_per_half=equiv_bore_mm(a_in2),
                valves=2, depress_kg=m_depress,
                depress_bore_mm=equiv_bore_mm(a_depress) if m_depress else D0,
                liquid=liquid, method=FIRE_METHOD)


@fn('relief_devices', 'API 520 Part I critical-flow relief sizing on the pressurised nodes (API520; '
    'sizing/relief.py), case inputs from params.relief_basis; X-SAF-05 API 521 fire case on the gas '
    'receiver banks (A-M-188)')
def relief_devices(b, inputs):
    """The relief command. Per node carrying params.relief_mm: an API 520 case
    book (P1_kPa_abs present) gets its required area, bore and adequacy
    re-derived from its own case inputs; GAS_FIRE receivers with a sized design
    take the governing fire case per half bank, which sets relief_mm on the
    whole-mm grid. Nodes without a case are marked atmospheric (the vent
    command's input). Records nothing without the driver payload (the bridge
    contract)."""
    if inputs.get('drivers') is None:
        return
    gas_basis = ('API 520 Part I critical-flow gas sizing (API520; sizing/relief.py); case inputs read from '
                 'params.relief_basis')
    fire_basis = 'X-SAF-05 API 521 fire case per manifolded half bank (A-M-188; API521_2020)'
    atm_basis = 'not an API 520 case; tank venting per API Std 2000 at unit task 07'
    for node in b.data['nodes']:
        uid = node['unit_id']
        params = node.get('params') or {}
        if 'relief_mm' not in params:
            continue
        rb = params.get('relief_basis')
        if isinstance(rb, dict) and 'P1_kPa_abs' in rb:
            w = rb.get('W_kg_h')                               # kg/h relief load, or from the case text
            if not w:
                w = float(dec(str(rb['case']).split('= ')[-1].split(' kg/h')[0]))
            a_in2 = gas_area_in2(
                dec(w) * LB_PER_KG,
                dec(rb['k']) if 'k' in rb else K_DEFAULT,
                dec(rb['P1_kPa_abs']) / KPA_TO_PSI,            # kPa abs -> psi abs
                dec(rb['T_K']) * R_F,                          # K -> deg R
                dec(rb['Z']) if 'Z' in rb else D1,
                dec(rb['M_kg_kmol']),                          # kg/kmol
                kd=dec(rb['Kd']) if 'Kd' in rb else KD_GAS,
                kb=dec(rb['Kb']) if 'Kb' in rb else D1,
                kc=dec(rb['Kc']) if 'Kc' in rb else D1)
            bore = equiv_bore_mm(a_in2)                        # mm
            book = dict(rb)                                    # seed order preserved; outputs re-stamped
            book['W_kg_h'] = float(dec(w))
            book['A_req_mm2'] = q(a_in2 * IN2_MM2, 2)          # mm2
            book['bore_req_mm'] = q(bore, 2)                   # mm
            book['computed_by'] = COMPUTED_BY
            book['adequate'] = bool(dec(params['relief_mm']) >= bore)   # mm vs mm
            _set(b, uid, 'params.relief_basis', book, STAGE_R, gas_basis, 'API520')
            if uid in GAS_FIRE and params.get('design'):
                fire = receiver_fire(params['design'], rb, dec(params['design_kPa']))   # kPa gauge seed
                book['fire_case'] = {k: (q(v, 3) if isinstance(v, D) else v) for k, v in fire.items()}
                book['relief_mm_basis'] = RELIEF_MM_BASIS
                governing = max(dec(book['bore_req_mm']), fire['bore_req_mm_per_half'])
                relief_mm = float(qceil(governing))            # whole mm, v1 p['relief_mm'] re-stamp
                book['adequate'] = bool(dec(relief_mm) >= governing)
                _set(b, uid, 'params.relief_basis', book, STAGE_R, gas_basis + '; ' + fire_basis, 'A-M-188')
                _set(b, uid, 'params.relief_mm', relief_mm, STAGE_R,
                     fire_basis + '; governing of blocked outlet and fire case per half bank', 'A-M-188')
        else:
            _set(b, uid, 'params.relief_basis', dict(ATM_MARK), STAGE_R, atm_basis)


def out_breathing(v_tk_m3, v_pf_m3_h, y):
    """API 2000 out-breathing (expiry), Nm3/h air: V = 2 V_pf + Y V_tk^0.9
    ([API2000_2020] 3.3.2 SI; Y from the drivers, latitude band not fixed
    until X-BAS-03 - the largest band, below 42 deg, is used)."""
    return K_VOL * v_pf_m3_h + y * v_tk_m3 ** (D(9) / D(10))


def in_breathing(v_tk_m3, v_pe_m3_h, c):
    """API 2000 in-breathing (contraction), Nm3/h air: V = V_pe + C V_tk^0.7."""
    return v_pe_m3_h + c * v_tk_m3 ** (D(7) / D(10))


def open_vent_bore(q_nm3_h, dp_pa):
    """Open-vent bore [PERRY9] orifice: Q = Cd A sqrt(2 dP / rho_air) at
    0.61 / 1.293 kg/m3, mm."""
    a_m2 = q_nm3_h / S_PER_H / (CD * (D(2) * dp_pa / RHO_AIR).sqrt())
    return (D(4) * a_m2 / PI).sqrt() * 1000                    # mm


def holdup_head_m(q_in_m3_h, transfer_h, unit_class, unit_id, drivers):
    """The A-M-182 liquid head where the unit has no sized height: header and
    recycle pipes hold no standing liquid; farm and habitation units take the
    bed or fixture depth; everything else takes a store or process hold-up
    volume at the driver hold days, as an equivalent cylinder at the driver
    H/D. Returns (head m, hold text)."""
    if unit_class in ('header', 'recycle_pipe'):
        return D0, 'pipe only, no standing liquid'
    if unit_class in ('farm', 'hab') or unit_id.startswith('HAB_'):
        h = dec(drivers['atm_bed_depth_m']['value'])           # m
        return h, f'bed or fixture depth {h} m'
    kind = 'store' if (unit_class in ('tank', 'product', 'reagent', 'cut_tank', 'dock')
                       or unit_id in ('ROOF_TANK', 'FAB_UPW_TANK')) else 'process'
    hold_d = dec(drivers['atm_hold_d']['value'][kind])         # d of hold-up
    v_hold = q_in_m3_h * transfer_h * hold_d                   # m3
    h_over_d = dec(drivers['atm_HD']['value'])                 # H/D
    d_equiv = (D(4) * v_hold / (PI * h_over_d)) ** (D1 / D(3))  # m
    return h_over_d * d_equiv, f'{kind} hold-up {fmt(hold_d, 0)} d = {fmt(v_hold, 3)} m3, H/D {h_over_d}'


@fn('atm_venting', 'X-PAR-03 API 2000 normal venting for every atmospheric node (A-M-155; API2000_2020 '
    '3.3.2 SI; PERRY9 open-vent orifice); A-M-174 design pressure from the actual cases, A-M-182 hold-up head')
def atm_venting(b, inputs):
    """The vent command. Per atmospheric node: the pump terms from the liquid
    kg/d edge census in the transfer window, thermal breathing on the sized
    envelope volume, the open-vent bore at min(driver dP, 25 % of the seed
    design pressure), the DN ladder, and the A-M-174 design pressure: vapour
    at 4 x vent dP plus the full-height hydrostatic head (A-M-182 hold-up head
    where no height is sized), on the half-kPa ceiling grid. Records nothing
    without the driver payload (the bridge contract)."""
    drv = inputs.get('drivers')
    if drv is None:
        return
    y = dec(drv['api2000_Y']['value'])                         # Nm3/h per m3^0.9 band factor
    c = dec(drv['api2000_C']['value'])                         # Nm3/h per m3^0.7 band factor
    transfer_h = dec(drv['vent_transfer_h']['value'])          # h, the pump-term window
    dp_cap = dec(drv['vent_dP_Pa']['value'])                   # Pa, the open-vent dP cap
    sg = dec(drv['atm_design_sg']['value'])                    # specific gravity, hydrostatic book
    basis = ('X-PAR-03 API 2000 normal venting (A-M-155; API2000_2020; sizing/vent.py; PERRY9 bore); '
             'A-M-174 design pressure from the cases')
    def liquid(e):
        return e['presence'] == 'present' and e.get('phase') == 'L' \
            and (e.get('rate') or {}).get('unit') == 'kg/d'
    for node in b.data['nodes']:
        uid = node['unit_id']
        params = node.get('params') or {}
        rb = params.get('relief_basis')
        if not (isinstance(rb, dict) and rb.get('case') == 'atmospheric'):
            continue
        sz = (params.get('sizing') or {}).get('size_mm') or params.get('size_mm')   # mm
        v = dec(sz[0]) * dec(sz[1]) * dec(sz[2]) / MM3_PER_M3 if sz and len(sz) >= 3 else D0   # m3
        q_in = sum((dec(e['rate']['value']) if e['rate'].get('value') else D0
                    for e in b.data['edges'] if e['to_unit_id'] == uid and liquid(e)), D0) \
            / 1000 / transfer_h                                # m3/h in
        q_out = sum((dec(e['rate']['value']) if e['rate'].get('value') else D0
                     for e in b.data['edges'] if e['from_unit_id'] == uid and liquid(e)), D0) \
            / 1000 / transfer_h                                # m3/h out
        v_out = out_breathing(v, q_in, y)                      # Nm3/h
        v_in = in_breathing(v, q_out, c)                       # Nm3/h
        dp = min(dp_cap, VENT_DP_FRAC * (dec(params['design_kPa']) if params.get('design_kPa')
                                         else DESIGN_DEFAULT_KPA) * PA_PER_KPA)   # Pa
        bore = open_vent_bore(max(v_out, v_in), dp)            # mm
        book = dict(rb)                                        # the relief mark, then the vent book
        book['method'] = ATM_METHOD
        book['V_tk_m3'] = q(v, 3)                              # m3
        book['pump_in_m3_h'] = q(q_in, 4)                      # m3/h
        book['pump_out_m3_h'] = q(q_out, 4)                    # m3/h
        book['out_breathing_Nm3_h'] = q(v_out, 3)              # Nm3/h
        book['in_breathing_Nm3_h'] = q(v_in, 3)                # Nm3/h
        book['vent_dP_Pa'] = qi(dp)                            # Pa
        book['vent_bore_req_mm'] = q(bore, 1)                  # mm
        book['vent_DN'] = next(d for d in DNS if d >= bore)    # DN ladder, 25 minimum
        book['thermal_term'] = 'envelope volume' if v else 'no sized volume: pump terms only'
        design = params.get('design') or {}
        h_mm = design.get('H_mm') or (sz[2] if sz and len(sz) >= 3 else 0)   # mm
        h = dec(h_mm) / 1000                                   # m
        hold = ''
        if not h and q_in > 0:                                 # A-M-182: head from the hold-up volume
            h, hold = holdup_head_m(q_in, transfer_h, node.get('class') or '', uid, drv)
        p_vap = VENT_DP_MULT * dp / PA_PER_KPA                 # kPa, 4 x vent dP
        p_liq = sg * G_SITE * h                                # kPa, SG x g x head
        design_kpa = qceil((p_vap + p_liq) * D(2)) / 2         # kPa g, half-kPa ceiling grid (v1 /2)
        book['relief_mm_status'] = 'atmospheric; no relief orifice, open vent per API 2000'
        if h:
            book['design_case'] = (f'vapour {fmt(p_vap, 1)} kPa (4 x vent dP) + hydrostatic {fmt(p_liq, 1)} kPa '
                                   f'({fmt(h, 2)} m full at SG {sg}'
                                   + (f'; {hold}, A-M-182' if hold else '')
                                   + f') = {design_kpa} kPa g (A-M-174)')
        else:
            book['design_case'] = (f'vapour {fmt(p_vap, 1)} kPa (4 x vent dP) = {design_kpa} kPa g; '
                                   f"{hold or 'no liquid inflow, no hydrostatic case'} (A-M-174)")
        _set(b, uid, 'params.relief_basis', book, STAGE_V, basis, 'A-M-155')
        _set(b, uid, 'params.design_kPa', float(design_kpa), STAGE_V,
             basis + '; design >= 4 x vent dP plus the full-height hydrostatic head', 'A-M-174')

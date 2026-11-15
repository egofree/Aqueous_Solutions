"""The X-SPEC specialty sizing lane (family migration; reference writer
flow_graph/param/specialty_sizing.py, ledger row `specialty_sizing`, PHYSICS).

X-LOC-SPEC / unit task 02 close-out (AQS-PLAN-007): the grease/lithium kettles,
the adsorption chiller, the dry cooler, the well head, the PEM electrolyser skid,
the baghouse, the make-up-air coil, the three flagged load stamps, the hall and
study-envelope boxes, the grow-bed bay framing, the black-water digester and the
methionine hood train. Every field this stage writes exists on the committed
graph (flow_graph/plant_flow_graph.json); that committed state is the golden
this function reproduces.

Grid doctrine (owner ruling 2026-11-15): quantities live on the declared grid as
integer Qty counts; driver and seed values arrive as v1 floats and are converted
at this boundary by grid_int() (Decimal, half-up at the grid, per-display scale
read from the grid.json data, dimension cited at the call site). Physics
constants port as integer scaled pairs - the Faraday book (2*96485*1000000) /
(2016*3600) -> 26589 Ah per kg H2, sqrt(3) -> 1732/1000, pi -> 3141593/1000000,
the 11.127 Nm3/kg H2 molar-volume class -> 11127/1000. No float literals.
Schema fields whose unit is not a declared grid dimension (m3/s air, m2 cloth,
A/cm2, kWh/kg, ...) are computed by scaled(): integer numerator over integer
denominator, quantised half-up to the decimals the v1 schema stores. Where v1
quantised an intermediate before reuse (the 55.0 kWh/kg book, the 0.167 kg/d
water book, the 7.16 L dryer volume, the 288.0 cm2 cell area, the 2-dp cloth
book) this port quantises at the same points.

Machine texts, duct schedules and the z_chain are design decisions: ported
verbatim as data. The v1 note-freeze idempotence (write the stamp note once) is
unrepresentable here: assignment replaces the field and its provenance in full,
and the same inputs rebuild the same note. The function declares its inputs
(the v1 drivers.json payload); a solve without them records nothing, so the
bridge solve and the check stay byte-faithful to the seed.
"""
import math
from decimal import Decimal, ROUND_HALF_UP

from flow_graph.v2.grid import Grid, Qty
from flow_graph.v2.registry import fn

GRID = Grid.load()
STAGE = 'specialty_sizing'


def grid_int(value, per):
    """A v1 float -> an integer count of grid units: Decimal, half-up at the
    grid boundary. `per` is the count-per-display-unit of the value's dimension
    (GRID.spec[dim][2] for a declared dimension); cite the dimension at the
    call site."""
    return int((Decimal(str(value)) * per).quantize(Decimal(1), rounding=ROUND_HALF_UP))


def scaled(num, den, dp):
    """Integer numerator / integer denominator, half-up at `dp` decimals.
    For schema fields whose unit is not a declared grid dimension; the scale is
    named in the call."""
    return float((Decimal(num) / Decimal(den)).quantize(Decimal(1).scaleb(-dp), rounding=ROUND_HALF_UP))


def half_up(num, den):
    """Integer division, half-up - the grid division rule where v1 quantised an
    intermediate value before reuse."""
    return int((Decimal(num) / Decimal(den)).quantize(Decimal(1), rounding=ROUND_HALF_UP))


def decq(value, dp):
    """Quantise an exact Decimal-derived value to `dp` decimals, half-up."""
    return float(Decimal(str(value)).quantize(Decimal(1).scaleb(-dp), rounding=ROUND_HALF_UP))


def _set(b, uid, path, value, basis, ref=None):
    prov = {'stage': STAGE, 'basis': basis}
    if ref:
        prov['ref'] = ref
    b.set_node_field(uid, path, value, prov)


def _kw(b, uid, w_count, note, basis, ref=None):
    """The continuous_kw stamp: value as a power-grid Qty (the schema stores kW
    floats; the grid is W, serialization emits the exact kW decimal), the human
    note text verbatim (downstream doc stages parse it), and status/unit
    defaulted only when the seed lacks them."""
    _set(b, uid, 'continuous_kw.value', Qty(w_count, 'power'), basis, ref)
    _set(b, uid, 'continuous_kw.note', note, basis, ref)
    seed = (b.nodes.get(uid, {}).get('continuous_kw') or {})
    if 'status' not in seed:
        _set(b, uid, 'continuous_kw.status', 'study', basis, ref)
    if 'unit' not in seed:
        _set(b, uid, 'continuous_kw.unit', 'kW', basis, ref)


@fn('specialty_sizing', 'X-LOC-SPEC / unit task 02 close-out (AQS-PLAN-007): the specialty machines, the '
    'flagged load stamps, the envelope boxes and the grow-bed framing, every number on its cited basis')
def specialty_sizing(b, inputs):
    drv = inputs.get('drivers')
    if drv is None:
        # The declared inputs are absent (a bridge solve or a check pass carries no
        # driver payload until the write_graph family wires inputs): the stage
        # cannot invent its drivers, so it records nothing and the seed stands.
        return

    def dv(name):
        return drv[name]['value']

    # --- the grease/lithium kettles (X-ASM-02 lubrication class) -------------------
    # Study classes on the mass_flow grid. The edge rates this lane once wrote are
    # superseded by the grease route lane (A-M-480); the kettles keep the designs
    # and the envelopes.
    ca_g = 200                                               # 0.2 kg/d Ca grease, g/d on the mass_flow grid (X-ASM-02 audit)
    li_g = 100                                               # 0.1 kg/d Li grease
    thick_g = 25                                             # 0.025 kg/d Ca-soap thickener (~12 % class)
    slip_g = 500                                             # 0.5 kg/d POLISH_BANK LiOH slipstream
    _set(b, 'GREASE_CA', 'params.design.duty',
         'calcium grease kettle: the C19-C28 wax base + the P_CA thickener -> the general lubrication grease',
         'the kettle duty text (design decision, verbatim)')
    _set(b, 'GREASE_CA', 'params.design.batch_kgd', Qty(ca_g, 'mass_flow'),
         'X-ASM-02 study class: the general lubrication draw (verification: X-ASM-02 greasing audit)')
    _set(b, 'GREASE_CA', 'params.design.heat_class', 'soap precipitation, jacket heated',
         'the kettle heat class (design decision, verbatim)')
    _set(b, 'GREASE_CA', 'params.sizing.batch_kgd', Qty(ca_g, 'mass_flow'),
         'X-ASM-02 study class: the general lubrication draw (verification: X-ASM-02 greasing audit)')
    _set(b, 'GREASE_CA', 'params.size_mm', [500, 400, 600], 'length-mm counts on the declared grid')
    _set(b, 'GREASE_CA', 'params.size_note', None, 'no note: the study envelope box stands alone')
    _set(b, 'GREASE_CA', 'params.size_basis', 'the 0.2 kg/d batch kettle: heated soap-precipitation class',
         'the kettle envelope basis')
    _kw(b, 'GREASE_CA', 200, 'jacket heater at the 0.2 kg/d batch class (X-SPEC sizing, calculated)',
        'jacket heater at the 0.2 kg/d batch class')

    _set(b, 'GREASE_LI', 'params.design.duty',
         'lithium grease kettle: the wax base + the LI_RECOVER carbonated thickener -> the motor-bearing grease',
         'the kettle duty text (design decision, verbatim)')
    _set(b, 'GREASE_LI', 'params.design.batch_kgd', Qty(li_g, 'mass_flow'),
         'X-ASM-02 study class: the motor-bearing grease draw')
    _set(b, 'GREASE_LI', 'params.sizing.batch_kgd', Qty(li_g, 'mass_flow'),
         'X-ASM-02 study class: the motor-bearing grease draw')
    _set(b, 'GREASE_LI', 'params.size_mm', [500, 400, 600], 'length-mm counts on the declared grid')
    _set(b, 'GREASE_LI', 'params.size_note', None, 'no note: the study envelope box stands alone')
    _set(b, 'GREASE_LI', 'params.size_basis', 'the 0.1 kg/d batch kettle (emulsification class)',
         'the kettle envelope basis')
    _kw(b, 'GREASE_LI', 200, 'jacket heater at the 0.1 kg/d batch class (X-SPEC sizing, calculated)',
        'jacket heater at the 0.1 kg/d batch class')

    _set(b, 'P_CA', 'params.design.duty',
         'calcium-soap precipitation: wax + lime -> the grease thickener (feeds GREASE_CA)',
         'the vessel duty text (design decision, verbatim)')
    _set(b, 'P_CA', 'params.design.thickener_kgd', Qty(thick_g, 'mass_flow'),
         'the calcium-soap thickener at ~12 % of the Ca grease (grease chemistry class)')
    _set(b, 'P_CA', 'params.sizing.thickener_kgd', Qty(thick_g, 'mass_flow'),
         'the calcium-soap thickener at ~12 % of the Ca grease (grease chemistry class)')
    _set(b, 'P_CA', 'params.size_mm', [300, 300, 400], 'length-mm counts on the declared grid')
    _set(b, 'P_CA', 'params.size_note', None, 'no note: the study envelope box stands alone')
    _set(b, 'P_CA', 'params.size_basis', 'the calcium-soap precipitation vessel at the 0.025 kg/d thickener draw',
         'the vessel envelope basis')
    _kw(b, 'P_CA', 50, 'agitator at the precipitation batch class (X-SPEC sizing, calculated)',
        'agitator at the precipitation batch class')

    _set(b, 'LI_RECOVER', 'params.design.duty',
         'carbonate the POLISH_BANK LiOH slipstream -> the lithium thickener (feeds GREASE_LI)',
         'the vessel duty text (design decision, verbatim)')
    _set(b, 'LI_RECOVER', 'params.design.slipstream_kgd', Qty(slip_g, 'mass_flow'),
         'the POLISH_BANK liquor slipstream at the ~1.5 wt% LiOH class')
    _set(b, 'LI_RECOVER', 'params.sizing.slipstream_kgd', Qty(slip_g, 'mass_flow'),
         'the POLISH_BANK liquor slipstream at the ~1.5 wt% LiOH class')
    _set(b, 'LI_RECOVER', 'params.size_mm', [200, 200, 800], 'length-mm counts on the declared grid')
    _set(b, 'LI_RECOVER', 'params.size_note', None, 'no note: the study envelope box stands alone')
    _set(b, 'LI_RECOVER', 'params.size_basis', 'the carbonation contactor at the 0.5 kg/d slipstream',
         'the vessel envelope basis')
    _kw(b, 'LI_RECOVER', 50, 'contactor agitator + CO2 metering at the batch class (X-SPEC sizing, calculated)',
        'contactor agitator + CO2 metering at the batch class')

    # --- ADS_CHILL: 2.25 kW chilled = 5 kW drive x the 0.45 thermal COP class ------
    _set(b, 'ADS_CHILL', 'params.design.duty',
         'silica gel-water adsorption chiller: 5 kW drive at 65 C -> 2.25 kW chilled at 12 C, 7.25 kW rejected',
         'the chiller duty text (design decision, verbatim)')
    _set(b, 'ADS_CHILL', 'params.design.chilled_kw', Qty(2250, 'power'),
         '2.25 kW chilled = 5.0 kW drive x the 0.45 thermal COP class (A-M-239/240; AQS-DUTY-013 class)',
         'A-M-239')
    _set(b, 'ADS_CHILL', 'params.design.cop_thermal', scaled(45, 100, 2),
         'the 0.45 thermal COP class (A-M-239/240; WANG2006_ADS)', 'A-M-239')
    _set(b, 'ADS_CHILL', 'params.sizing.chilled_kw', Qty(2250, 'power'),
         '2.25 kW chilled = 5.0 kW drive x the 0.45 thermal COP class (A-M-239/240; AQS-DUTY-013 class)',
         'A-M-239')
    _set(b, 'ADS_CHILL', 'params.sizing.cop_thermal', scaled(45, 100, 2),
         'the 0.45 thermal COP class (A-M-239/240; WANG2006_ADS)', 'A-M-239')
    _set(b, 'ADS_CHILL', 'params.size_mm', [700, 500, 1200], 'length-mm counts on the declared grid')
    _set(b, 'ADS_CHILL', 'params.size_note', None, 'no note: the study envelope box stands alone')
    _set(b, 'ADS_CHILL', 'params.size_basis',
         'the 2.25 kW-class silica gel-water adsorption chiller: drive 65 C, chilled 12 C, thermal COP ~0.45 '
         '(A-M-239/240; WANG2006_ADS); 304L shells per the issued sec3', 'the chiller envelope basis', 'A-M-239')

    # --- DRY_COOLER: fan electrical + airside read the rating the heat lane wrote ---
    # rated_kW is a prior stage's output: read it from the builder seed, keep the
    # 12.0 kW v1 fallback for a seed without it.
    _dc_raw = (b.nodes.get('DRY_COOLER', {}).get('params') or {}).get('rated_kW')
    rated_w = grid_int(_dc_raw, GRID.spec['power'][2]) if _dc_raw else 12 * 1000   # fallback 12.0 kW
    rated_kw_txt = str(grid_int(_dc_raw, 1)) if _dc_raw else '12'                  # the note's :.0f duty text
    duty_w = (rated_w * 4) // 5                                    # the rated / 1.25 bounding duty
    # airflow: 0.61 m3/s per 7.25 kW class -> 610 L/s per 7250 W, on the duty
    air_l_s = half_up(610 * duty_w * 1000, 7250 * 1000)            # L/s count
    airflow = decq(scaled(air_l_s, 1000, 2), 2)
    # fan: 0.05 kW_fan/kW_th -> 5 W per 100 W thermal, on the power grid
    fan_w = half_up(rated_w * 5, 100)
    fan_note = ('the fan at the 0.05 kW_fan/kW_th class on the rated duty ' + rated_kw_txt +
                ' kW (A-M-244 restated); fan-assisted at the window bounding case (X-SPEC sizing, calculated)')
    _set(b, 'DRY_COOLER', 'params.design.duty',
         'dry rejection of the ADS_CHILL 7.25 kW + the Q4 dry share + the ZNBR2 cycling heat',
         'the duty text (design decision, verbatim)')
    _set(b, 'DRY_COOLER', 'params.design.airflow_m3_s', airflow,
         'air 25->38 C at 1.06 kg/m3: Q/(rho cp dT) at 0.61 m3/s per 7.25 kW class (AQS-BLD class approach)',
         'A-M-244')
    _set(b, 'DRY_COOLER', 'params.design.fan_kw', Qty(fan_w, 'power'),
         'the fan at the 0.05 kW_fan/kW_th class (A-M-244 restated)', 'A-M-244')
    _set(b, 'DRY_COOLER', 'params.sizing.airflow_m3_s', airflow,
         'air 25->38 C at 1.06 kg/m3: Q/(rho cp dT) at 0.61 m3/s per 7.25 kW class (AQS-BLD class approach)',
         'A-M-244')
    _set(b, 'DRY_COOLER', 'params.size_mm', [1200, 600, 1200], 'length-mm counts on the declared grid')
    _set(b, 'DRY_COOLER', 'params.size_note', None, 'no note: the study envelope box stands alone')
    _set(b, 'DRY_COOLER', 'params.size_basis',
         'the dry coil + fan at the calculated rejection duty (study envelope box; design sizing per the duty '
         'sheet follows)', 'the envelope basis')
    _kw(b, 'DRY_COOLER', fan_w, fan_note, 'the fan at the 0.05 kW_fan/kW_th class (A-M-244 restated)', 'A-M-244')

    # --- GW_INTAKE: standby well head ----------------------------------------------
    _set(b, 'GW_INTAKE', 'params.design.duty', 'standby well head: the make-up on loss of atmospheric harvest',
         'the duty text (design decision, verbatim)')
    _set(b, 'GW_INTAKE', 'params.design.pump_kw', Qty(370, 'power'),
         'the submersible at the make-up class (the T4 shortfall bound ~30 m3/d worst case: 0.37 kW lifts '
         '30 m3 x 30 m)')
    _set(b, 'GW_INTAKE', 'params.sizing.pump_kw', Qty(370, 'power'),
         'the submersible at the make-up class (the T4 shortfall bound ~30 m3/d worst case: 0.37 kW lifts '
         '30 m3 x 30 m)')
    _set(b, 'GW_INTAKE', 'params.size_mm', [800, 800, 600], 'length-mm counts on the declared grid')
    _set(b, 'GW_INTAKE', 'params.size_note', None, 'no note: the study envelope box stands alone')
    _set(b, 'GW_INTAKE', 'params.size_basis',
         'the wellhead hatch + pump discharge set (X-LOC-13 well head); the pump is downhole, not plant-side',
         'the envelope basis', 'X-LOC-13')
    _kw(b, 'GW_INTAKE', 370,
        'the submersible at the make-up class (the T4 shortfall bound ~30 m3/d worst case: 0.37 kW lifts '
        '30 m3 x 30 m) (standby-zero at the baseline: standby-zero at the baseline: the atmospheric harvest '
        'covers the water cycle (the T4 by-design ruling). The pump rate is the loss-of-harvest make-up class.) '
        '(X-SPEC sizing, calculated)',
        'the loss-of-harvest make-up class; standby-zero at the baseline (the T4 by-design ruling)')

    # --- H2O_ELYZ: the PEM skid machine design (A-M-459 stack; A-M-133 window;
    # A-M-168 bed classes; A-M-279 skid allowances) ---------------------------------
    h2_gd = grid_int(dv('elyz_h2_design_kg_d'), GRID.spec['mass_flow'][2])     # design-block H2, g/d
    win_mh = grid_int(dv('ely_window_h'), 1000)                                # the window, milli-h (A-M-133)
    # Faraday: 2 x 96485 C/mol over 2.016 g/mol -> Ah per kg H2, integer scaled pair
    ah_kg = half_up(2 * 96485 * 1000000, 2016 * 3600)                          # 26589 Ah/kg (v1 float 26588.68)
    j_mA = grid_int(dv('pem_stack_j_A_cm2'), 1000)                             # A/cm2 -> mA/cm2
    vc_mV = grid_int(dv('pem_stack_v_cell_V'), 1000)                           # V/cell -> mV/cell
    cells = int(dv('pem_stack_cells'))
    # specific consumption: the rated-edge book 21.445 kW x 24 h over 9.358 kg
    kwh_mwhg = half_up(21445 * 24 * 1000, h2_gd)                               # 54997 milli-Wh/g = Wh/kg
    kwh = decq(scaled(kwh_mwhg, 1000, 1), 1)                                   # 55.0 at the stored decimal
    kwh_book = half_up(kwh_mwhg, 100) * 100                                    # the stored 55.0 book v1 reuses
    rated_w = half_up(h2_gd * kwh_book, win_mh)                                # system draw at the window, W
    rated_kw = decq(scaled(rated_w, 1000, 1), 1)                               # 85.8 at the stored decimal
    h2_rate = scaled(h2_gd, win_mh, 4)                                         # kg/h at the rated point
    i_mA = half_up(h2_gd * ah_kg * 1000, win_mh)                               # cell-summed current, mA
    a_sum_mcm2 = half_up(i_mA * 1000, j_mA)                                    # cell-summed area, milli-cm2
    a_cell_mcm2 = half_up(a_sum_mcm2 * 1000, cells * 1000)                     # per cell, milli-cm2
    a_cell = decq(scaled(a_cell_mcm2, 1000, 1), 1)                             # 288.0 at the stored decimal
    edge_hm = math.isqrt(a_cell_mcm2 * 1000)                                   # sqrt by integer isqrt, hm
    active_mm = decq(scaled(edge_hm, 100, 1), 1)                               # 169.7
    i_stack = decq(scaled(a_cell_mcm2 * j_mA, 1000 * 1000, 1), 1)              # A at the drawn point
    v_stack = decq(scaled(cells * vc_mV, 1000, 1), 1)                          # V
    p_dc = decq(scaled(i_mA * vc_mV, 1000 * 1000 * 1000, 2), 2)                # kW DC
    area_m2 = decq(scaled(a_sum_mcm2, 1000 * 10000, 3), 3)                     # total active area, m2
    # A-M-279 deck allowances: 0.025 + 0.015 m2/kW at W 1050, H 2200 -> mm of deck
    l_stack = (rated_w * 25) // 1050
    l_bop = (rated_w * 15) // 1050
    l_skid = l_stack + 100 + l_bop                                             # 100 mm gap between the decks
    nm3_mlh = half_up(h2_gd * 11127 * 1000, win_mh)                            # 11.127 Nm3/kg -> mL/h at the point
    nm3_txt = decq(scaled(nm3_mlh, 1000000, 1), 1)                             # 17.4 at the note decimal
    bed_r_mm = grid_int(dv('elyz_bed_radius_m'), 1000)                         # DN80 Sch 40 bore, mm
    bed_area_mm2 = half_up(3141593 * bed_r_mm * bed_r_mm, 1000000)             # pi -> 3141593/1000000
    deoxo_ml = half_up(nm3_mlh, 5000)                                          # GHSV 5000 1/h (A-M-168 class)
    deoxo_bed_mm = (deoxo_ml * 1000 // 2) // bed_area_mm2                      # two beds, mm each
    # dryer: water book scaled off the H2_DRYER saturation figure (0.0492/2.750 per kg H2)
    water_gd = half_up(h2_gd * 492, 27500)                                     # 167 g/d at the stored 3-dp book
    sieve_g = water_gd * 30                                                    # 0.10 kg/kg working, margin 3
    dryer_ml = half_up(sieve_g * 1000, 700)                                    # 0.7 kg/L sieve bulk (A-M-168)
    dryer_ml_book = half_up(dryer_ml + 5, 10) * 10                             # the 7.16 L 2-dp book v1 reuses
    dryer_bed_mm = (dryer_ml_book * 1000 // 2) // bed_area_mm2
    _set(b, 'H2O_ELYZ', 'params.design.duty',
         'PEM electrolysis: 83.62 kg/d water -> 9.358 kg/d H2 + 74.263 kg/d O2 at 21.445 kW',
         'the duty text (design decision, verbatim)')
    _set(b, 'H2O_ELYZ', 'params.design.kwh_per_kg_h2', kwh,
         'PEM specific consumption at the stored decimal; grid-exact book ' + str(kwh_mwhg) +
         ' Wh/kg (21.445 kW x 24 h / 9.358 kg, the rated edges self-consistent)')
    _set(b, 'H2O_ELYZ', 'params.design.machine',
         'PEM stack skid + balance-of-plant deck (H2/O2 gas-liquid separators, deoxo on H2, dryer on H2 '
         'per params.internals)', 'the machine text (design decision, verbatim)')
    _set(b, 'H2O_ELYZ', 'params.design.rated_kw', rated_kw,
         'the system draw at the window: the ' + str(kwh) + ' kWh/kg book over the ' +
         str(dv('ely_window_h')) + ' h window (A-M-133)', 'A-M-133')
    _set(b, 'H2O_ELYZ', 'params.design.window_h', float(Decimal(str(dv('ely_window_h')))),
         'the PV window driver ely_window_h (A-M-133)', 'A-M-133')
    _set(b, 'H2O_ELYZ', 'params.design.h2_rate_kg_h', h2_rate,
         'the design-block H2 over the window, kg/h at the rated point (A-M-459)', 'A-M-459')
    _set(b, 'H2O_ELYZ', 'params.design.stack', {
        'j_A_cm2': float(Decimal(str(dv('pem_stack_j_A_cm2')))),
        'v_cell': float(Decimal(str(dv('pem_stack_v_cell_V')))),
        'cells': cells,
        'active_per_cell_cm2': a_cell,
        'active_mm': [active_mm, active_mm],
        'i_stack_A': i_stack,
        'v_stack_V': v_stack,
        'p_dc_kW': p_dc,
        'area_m2_total': area_m2,
        'basis': 'the cell-summed area the rated H2 books: m_dot x 26,590 Ah/kg / j (A-M-459); stack DC at '
                 'V_cell x cells; the system draw adds BoP and power electronics to the 55 kWh/kg book (A-M-133)',
    }, 'the stack point: m_dot x Ah/kg / j at the driver current density and cell voltage (A-M-459)', 'A-M-459')
    _set(b, 'H2O_ELYZ', 'params.design.separators',
         'H2 and O2 gas-liquid separators DN150 x 400, one per side, 316L (duty section 3 M1 family)',
         'the separator text (design decision, verbatim)')
    _set(b, 'H2O_ELYZ', 'params.design.deoxo', {
        'beds': 2,
        'tube': 'DN80 x %d mm 316L' % deoxo_bed_mm,
        'basis': 'GHSV 5000 1/h on the rated %s Nm3/h H2 (A-M-168 driver class)' % nm3_txt,
    }, 'GHSV 5000 1/h on the rated H2 (A-M-168 driver class)', 'A-M-168')
    _set(b, 'H2O_ELYZ', 'params.design.dryer', {
        'beds': 2,
        'tube': 'DN80 x %d mm 316L' % dryer_bed_mm,
        'sieve_kg': decq(scaled(sieve_g, 1000, 2), 2),
        'water_kg_d': decq(scaled(water_gd, 1000, 3), 3),
        'basis': '4A/13X 0.10 kg/kg at margin 3, regenerated at 250 C (A-M-168 class); water book scaled off '
                 'the H2_DRYER saturation figure',
    }, '4A/13X at 0.10 kg/kg working capacity, margin 3 (A-M-168 class)', 'A-M-168')
    _set(b, 'H2O_ELYZ', 'params.design.skid', {
        'w_mm': 1050,
        'h_mm': 2200,
        'l_stack_mm': l_stack,
        'l_bop_mm': l_bop,
        'basis': 'the A-M-279 allowances at the rated kW (stack 0.025 + BoP 0.015 m2/kW at W 1050, H 2200)',
    }, 'the A-M-279 plan allowances at the rated kW', 'A-M-279')
    _set(b, 'H2O_ELYZ', 'params.design.computed_by',
         'flow_graph/param/specialty_sizing.py (X-SPEC lane, CAD-representation audit item 8)',
         'the computed_by text, ported verbatim (the structured provenance names the v2 stage)')
    _set(b, 'H2O_ELYZ', 'params.sizing.kwh_per_kg_h2', kwh,
         'PEM specific consumption at the stored decimal (the rated edges self-consistent)')
    _set(b, 'H2O_ELYZ', 'params.sizing.rated_kw', rated_kw,
         'the system draw at the window (A-M-133)', 'A-M-133')
    _set(b, 'H2O_ELYZ', 'params.size_mm', [l_skid, 1050, 2200], 'length-mm counts on the declared grid')
    _set(b, 'H2O_ELYZ', 'params.size_note',
         'L x W x H mm, set by flow_graph/param/specialty_sizing.py: the A-M-279 skid allowances at the rated '
         'kW (stack deck %d + gap 100 + BoP deck %d at W 1050, H 2200); the placement seed block '
         '(1800 x 800 x 1600) under-books it - the named consequence (H2O_ELYZ WORK_ORDER W12)'
         % (l_stack, l_bop), 'the skid envelope note (design decision, verbatim)', 'A-M-279')

    # --- BAGHOUSE: capture air, cloth field, hopper and z-chain (A-M-458) -----------
    _bh_dust = {k: decq(((b.edges.get(k, {}).get('rate') or {}).get('value')) or 0, 3)
                for k in ('IA-MILL-LOSS', 'IA-FAB-LOSS', 'IA-WIRE-LOSS')}
    hoods = {'IA-MILL-LOSS': float(Decimal(str(dv('baghouse_hood_mill_m2')))),
             'IA-FAB-LOSS': float(Decimal(str(dv('baghouse_hood_kerf_m2')))),
             'IA-WIRE-LOSS': float(Decimal(str(dv('baghouse_hood_wire_m2'))))}       # m2 hood faces (A-M-458)
    u_mms = grid_int(dv('baghouse_hood_face_velocity_m_s'), 1000)                    # m/s -> mm/s
    hood_mm2 = sum(grid_int(x, 1000000) for x in hoods.values())                     # m2 -> mm2
    capture_m3h = half_up(u_mms * hood_mm2 * 3600, 1000 * 1000000)                   # mm3/h -> m3/h
    acb_100 = grid_int(dv('baghouse_ac_basis_m3_min_m2'), 100)                       # m3/min/m2, 2-dp (EPA-453)
    cloth_req = decq(scaled(capture_m3h * 100, 60 * acb_100, 2), 2)                  # 10.5 m2 required
    bags = int(dv('baghouse_bag_count'))                                             # D150 x 1200, 5 x 4 field
    bag_area_e4 = half_up(3141593 * 150 * 1200, 100000000)                           # pi -> 3141593/1000000
    bag_area = decq(scaled(bag_area_e4, 10000, 4), 4)                                # 0.5655 m2 per bag
    cloth_e2 = bag_area_e4 * bags // 100                                             # the 2-dp cloth book
    cloth = decq(scaled(cloth_e2, 100, 2), 2)                                        # 11.31 m2 drawn
    ac_drawn = decq(scaled(capture_m3h * 100, 60 * cloth_e2, 3), 3)                  # 1.114 m3/min/m2 drawn
    hopper_h = (900 - 200) // 2 * 1732 // 1000                                       # 60 deg: sqrt 3 -> 1732/1000
    bh_h = 50 + hopper_h + 20 + 1200 + 20 + 360 + 20                                 # plinth to roof chain
    _set(b, 'BAGHOUSE', 'params.design.machine',
         'pulse-jet dust baghouse: CS housing, tubesheet, 20-bag antistatic-polyester field, 60 deg dust '
         'hopper with rotary valve to IA-BAG-01, pulse-clean header and solenoid/diaphragm envelopes',
         'the machine text (design decision, verbatim)')
    _set(b, 'BAGHOUSE', 'params.design.dust_kg_d', _bh_dust,
         'the capture-book dust rates, read from the seed edges at the 3-dp book')
    _set(b, 'BAGHOUSE', 'params.design.hoods_m2', hoods, 'the hood faces (A-M-458)', 'A-M-458')
    _set(b, 'BAGHOUSE', 'params.design.hood_face_velocity_m_s',
         float(Decimal(str(dv('baghouse_hood_face_velocity_m_s')))),
         'the hood face velocity (ACGIH class, driver baghouse_hood_face_velocity_m_s)', 'A-M-458')
    _set(b, 'BAGHOUSE', 'params.design.capture_air_m3_h',
         float(Decimal(capture_m3h).quantize(Decimal('0.1'))),
         'capture air = hood face velocity x hood faces (A-M-458, ACGIH class)', 'A-M-458')
    _set(b, 'BAGHOUSE', 'params.design.ac_basis_m3_min_m2', float(Decimal(str(dv('baghouse_ac_basis_m3_min_m2')))),
         'the air-to-cloth basis (EPA-453 practice, driver baghouse_ac_basis_m3_min_m2)', 'A-M-458')
    _set(b, 'BAGHOUSE', 'params.design.cloth_req_m2', cloth_req,
         'cloth = air / 1.2 m3/min/m2 (EPA-453 practice)', 'A-M-458')
    _set(b, 'BAGHOUSE', 'params.design.bags', bags, 'the drawn bag count (driver baghouse_bag_count)', 'A-M-458')
    _set(b, 'BAGHOUSE', 'params.design.bag_mm', [150, 1200], 'length-mm counts on the declared grid')
    _set(b, 'BAGHOUSE', 'params.design.bag_pitch_mm', 180, 'length-mm count on the declared grid')
    _set(b, 'BAGHOUSE', 'params.design.cloth_drawn_m2', cloth,
         'the drawn field area at the 180 mm pitch', 'A-M-458')
    _set(b, 'BAGHOUSE', 'params.design.ac_drawn_m3_min_m2', ac_drawn,
         'the drawn air-to-cloth ratio (the +8 % field over the requirement)', 'A-M-458')
    _set(b, 'BAGHOUSE', 'params.design.ducts',
         'hood ducts DN100 (mill, 360 m3/h) and DN80 x 2 (fab 216, wire 180 m3/h) at the 18-20 m/s duct class; '
         'the schedule DN15 rows stay the duty connection table (WORK_ORDER W12)',
         'the duct schedule text (design decision, verbatim)')
    _set(b, 'BAGHOUSE', 'params.design.housing_inner_mm', [900, 700], 'length-mm counts on the declared grid')
    _set(b, 'BAGHOUSE', 'params.design.wall_mm', scaled(30, 10, 1), 'the 3.0 mm CS wall (design decision)')
    _set(b, 'BAGHOUSE', 'params.design.hopper_h_mm', hopper_h,
         '60 deg hopper over the 200 mm valve outlet (sqrt 3 -> 1732/1000)', 'A-M-458')
    _set(b, 'BAGHOUSE', 'params.design.valve_outlet_mm', 200, 'length-mm count on the declared grid')
    _set(b, 'BAGHOUSE', 'params.design.z_chain', {
        'plinth': 50,
        'hopper_top': 50 + hopper_h,
        'bags': [50 + hopper_h + 20, 50 + hopper_h + 20 + 1200],
        'tubesheet': 50 + hopper_h + 20 + 1200,
        'plenum': [50 + hopper_h + 20 + 1200 + 20, 50 + hopper_h + 20 + 1200 + 20 + 360],
    }, 'the z-chain elevations, integer mm on the declared grid', 'A-M-458')
    _set(b, 'BAGHOUSE', 'params.design.material',
         'carbon steel housing, painted, bonded and grounded; antistatic polyester bags (duty section 3); '
         'deflagration vent per the combustible-dust class',
         'the material text (design decision, verbatim)')
    _set(b, 'BAGHOUSE', 'params.design.basis',
         'capture air = hood face velocity x hood faces (A-M-458, ACGIH class); cloth = air / 1.2 m3/min/m2 '
         '(EPA-453 practice); drawn field carries it at +8 %',
         'the sizing basis text (design decision, verbatim)', 'A-M-458')
    _set(b, 'BAGHOUSE', 'params.design.computed_by',
         'flow_graph/param/specialty_sizing.py (X-SPEC lane, CAD-representation audit item 5)',
         'the computed_by text, ported verbatim (the structured provenance names the v2 stage)')
    _set(b, 'BAGHOUSE', 'params.sizing.capture_air_m3_h',
         float(Decimal(capture_m3h).quantize(Decimal('0.1'))),
         'capture air = hood face velocity x hood faces (A-M-458, ACGIH class)', 'A-M-458')
    _set(b, 'BAGHOUSE', 'params.sizing.cloth_m2', cloth, 'the drawn cloth field', 'A-M-458')
    _set(b, 'BAGHOUSE', 'params.size_mm', [1250, 1000, bh_h], 'length-mm counts on the declared grid')
    _set(b, 'BAGHOUSE', 'params.size_note',
         'L x W x H mm, set by flow_graph/param/specialty_sizing.py (X-SPEC): housing, inlet plenum, bag field '
         'and 60 deg hopper; the placement seed block (1500 x 1000 x 1500) under-books the height by 0.78 m - '
         'the named consequence (BAGHOUSE WORK_ORDER W12)', 'the envelope note (design decision, verbatim)')

    # --- MAU_HX: the 12 kW water-to-air coil ----------------------------------------
    _set(b, 'MAU_HX', 'params.design.duty', 'the 12 kW water-to-air coil on the hab make-up air (Q4 -> MAU)',
         'the duty text (design decision, verbatim)')
    _set(b, 'MAU_HX', 'params.sizing.duty_kw', Qty(12000, 'power'), 'the 12 kW coil duty (A-M-241)', 'A-M-241')
    _set(b, 'MAU_HX', 'params.size_mm', [600, 400, 400], 'length-mm counts on the declared grid')
    _set(b, 'MAU_HX', 'params.size_note', None, 'no note: the study envelope box stands alone')
    _set(b, 'MAU_HX', 'params.size_basis', 'the 12 kW water-to-air coil at the MAU duty (Q4 -> hab make-up air)',
         'the envelope basis', 'A-M-241')

    # --- the three flagged load stamps ----------------------------------------------
    _set(b, 'FEED_PREP', 'params.sizing.load_basis',
         'mixer 0.1 + grinder 0.15 + HP drier 0.35 (9.5 kg/d water x ~0.9 kWh/kg at the HP COP class); '
         'arithmetic per A-M-426', 'the load arithmetic note (A-M-426)', 'A-M-426')
    _kw(b, 'FEED_PREP', 600,
        'mixer 0.1 + grinder 0.15 + HP drier 0.35 (9.5 kg/d water x ~0.9 kWh/kg at the HP COP class); '
        'arithmetic per A-M-426 (X-SPEC calculated) (X-SPEC sizing, calculated)',
        'the load arithmetic (A-M-426; the A-M-275/A-M-301 calculated discipline)', 'A-M-426')
    _set(b, 'POLY_FIBER', 'params.sizing.load_basis',
         'extruder heater 0.2 (0.09 kg/d PP melt + standby) + spindle/winder 0.1; arithmetic per A-M-429',
         'the load arithmetic note (A-M-429)', 'A-M-429')
    _kw(b, 'POLY_FIBER', 300,
        'extruder heater 0.2 (0.09 kg/d PP melt + standby) + spindle/winder 0.1; arithmetic per A-M-429 '
        '(X-SPEC calculated) (X-SPEC sizing, calculated)',
        'the load arithmetic (A-M-429; the A-M-275/A-M-301 calculated discipline)', 'A-M-429')
    _set(b, 'AQUA_UV', 'params.sizing.load_basis',
         'the 254 nm lamp class at the 30-100 mJ/cm2 dose and the 40 kg/d loop flow (A-M-428)',
         'the load arithmetic note (A-M-428)', 'A-M-428')
    _kw(b, 'AQUA_UV', 40,
        'the 254 nm lamp class at the 30-100 mJ/cm2 dose and the 40 kg/d loop flow (A-M-428) (X-SPEC '
        'calculated) (X-SPEC sizing, calculated)',
        'the load arithmetic (A-M-428; the A-M-275/A-M-301 calculated discipline)', 'A-M-428')

    # --- EXT_HALL: the building massing envelope -------------------------------------
    _set(b, 'EXT_HALL', 'params.size_mm', [186000, 174000, 6000], 'length-mm counts on the declared grid')
    _set(b, 'EXT_HALL', 'params.size_note',
         'building massing envelope (bounding box of the issued L-shape): EXT_HALL_E 162 x 174 m east extension '
         '+ EXT_HALL_N 24 x 156 m north extension, 6 m eave, portal frames on the 6 m grid (31 x 29 bays, '
         'X-PAR-07, A-M-104; placement_seed blocks EXT_HALL_E/N are the authority). Conditioned footprint per '
         'params.footprint_m2; the fitout programme stays the duty-sheet open item.',
         'the massing envelope note (X-PAR-07, A-M-104)', 'A-M-104')

    # --- SI_REDUCE + the study-envelope boxes ----------------------------------------
    # (SI_REDUCE design values are owned by the silicon route lane, A-M-472; this lane
    # writes the envelope box only.)
    _set(b, 'SI_REDUCE', 'params.size_mm', [1200, 1000, 1600], 'length-mm counts on the declared grid')
    _set(b, 'SI_REDUCE', 'params.size_note', 'envelope from the placement seed (AQS-PLACE-SEED-001); sized by need',
         'the envelope note (AQS-PLACE-SEED-001)')
    for uid in ('AFTERBURNER', 'AFTERBURNER_FLUE', 'BMED_UPW_POLISH', 'COLD_MILL', 'CRU',
                'CRYO_AHU_COND_CONDENSABLE', 'GAS_ATOMIZER', 'GEO_GHEX', 'GEO_HP_CLOSED_LOOP', 'HYDRO_SET',
                'MET_MELT', 'MFG_SHOP', 'OIL_DRYER', 'PV_ARRAY', 'WAFER_FAB', 'WET_BENCH', 'WIRE_DRAW'):
        _set(b, uid, 'params.size_mm', [1000, 600, 800], 'length-mm counts on the declared grid')
        _set(b, uid, 'params.size_note',
             'study default envelope box, read back from the cad/stl registry (M0 study envelope; design sizing '
             'per the duty sheet follows)', 'the study envelope note (M0)')

    # --- GROW_BED: the bay framing (A-M-469 over the A-M-229 area) --------------------
    # Integer mm2: the 4 x 2 framing must carry the A-M-229 area exactly.
    area_mm2 = grid_int(b.nodes['GROW_BED']['params']['area_m2'], 1000000)     # m2 -> mm2
    gb_ix, gb_iy = 4 * 1820, 2 * 2000
    assert gb_ix * gb_iy == area_mm2, \
        'GROW_BED: the bay framing must carry the A-M-229 area exactly'
    _set(b, 'GROW_BED', 'params.size_mm', [gb_ix + 2 * 15, gb_iy + 2 * 15, 911],
         'length-mm counts on the declared grid: 4 x 2 nominal 2000 x 1000 bays, 15 mm basin walls, canopy z 900')
    _set(b, 'GROW_BED', 'params.size_note',
         'crew-duty growing area (A-M-229 29.12 m2) framed 4 x 2 nominal 2000 x 1000 bays, 15 mm basin walls, '
         'LED canopy top z 900 with the rail frame to z 910.6 (A-M-469; the canopy top is the registered study '
         'layout, W12)', 'the bay framing note (A-M-469 over the A-M-229 area)', 'A-M-469')

    # --- BLACK_DIGEST: the digester design (AQS-DUTY-063 book, restored verbatim) -----
    bd = {'D_mm': 800, 'H_mm': 760, 'wall_mm': scaled(50, 10, 1), 'V_L': 378,
          'material': 'PP-H sheet, extrusion-welded (DVS 2207-11)',
          'insulation': 'PIR 50 mm, PE cladding', 'heat_W': 85, 'T_C': 55, 'SRT_d': 15, 'biogas_g_d': 99}
    for key in sorted(bd):
        _set(b, 'BLACK_DIGEST', 'params.design.' + key, bd[key],
             'the AQS-DUTY-063 digester design, restored from the governing sizing doc (AQS-DUTY-063)',
             'AQS-DUTY-063')
    _set(b, 'BLACK_DIGEST', 'params.size_mm', [1100, 1100, 1260], 'length-mm counts on the declared grid')
    _set(b, 'BLACK_DIGEST', 'params.size_note',
         'DN800 x 760 mm thermophilic anaerobic digester + 300 mm envelope margin, per AQS-DUTY-063 '
         '(sizing/SANITATION.md section 2 row 1: 378 L, PP-H 5.0 mm, 50 mm PIR, 85 W, 55 C SRT 15 d METCALF5); '
         'graph-side design restored from the governing sizing doc because the X-SAN-01 writer is R11-blocked '
         '(owner lane)', 'the digester envelope note (AQS-DUTY-063)', 'AQS-DUTY-063')

    # --- MET_SYN: the hood train envelope --------------------------------------------
    _set(b, 'MET_SYN', 'params.size_mm', [1500, 1000, 1800], 'length-mm counts on the declared grid')
    _set(b, 'MET_SYN', 'params.size_note',
         'bench fume-hood train: glass-lined reactor column (2 L working volume), reagent feed tanks, '
         'Hastelloy C crystalliser; the 9 g/d DL-Met duty sets nothing larger (A-M-416 route A; X-UI-002)',
         'the hood train envelope note (A-M-416 route A)', 'A-M-416')

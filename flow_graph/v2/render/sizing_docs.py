"""The sizing-document renderer wave (the doc half of the ledger section B
MIXED rows). Reference writers: flow_graph/param/cold_box.py, evap_design.py,
receivers.py, h2_compressor.py, h2_purifier.py, house_scrubbers.py,
upw_polish.py, geo_loop.py -- the doc-render section of each --write module;
the physics lanes did not port it. Eight pure functions Model -> document
bytes, one per sizing document, porting the v1 doc-template code exactly (the
same headers, document numbers, revision lines, table shapes, number formats
and basis texts). The acceptance is byte-exact reproduction of the committed
file (flow_graph/v2/test_render_sizing.py).

What each function reads (the doc-consumption notes recorded in the landed
family modules' docstrings):
- render_cold_box: the CRYO_ASU params.design books (feed_N2_kg_d,
  feed_CO2_kg_d, x_CO2, sorbent_kg_per_bed, bed_D_mm, bed_L_mm, regen_kW,
  blower_kW, comp_stages, comp_ratio_per_stage, comp_T_out_C, co2_comp_kW,
  co2_chill_kW, getter_kW, total_kW, expander_backup), plus the cb_cycle_h
  driver read fresh (the v1 DR.load() read).
- render_evap_design: the EVAP_ACID / EVAP_BASE params.design blocks (the
  per-unit design tables, trim, column books), the params.relief_basis case
  dicts (the body case and the nested shell_side), the process family's evap
  mass books for section 8 and the options study table (the v1 options()
  doc-only helper - the renderer lane; the VLE chain is the evap_design
  family's float-lane bubble() port), and the evap_* basis drivers.
- render_gas_receivers: the CRYO_H2 / CRYO_O2 / CRYO_CO2 params.design books
  (P_design_MPa, t_req_mm, t_min_mm, t_ok, tube_m, ID_mm, banks, tubes,
  steel_kg, rack_mm); the fixed 316L/Sch 160 wall sentence is template text.
- render_h2_compressor: the CRYO_H2 params.compressor_design books (H2_kg_d,
  n_stages, ratio_per_stage, T_limit_C, kWh_per_kg, P_avg_kW, P_peak_kW, the
  per-stage rows, units, material) plus the h2c_P1_bar / h2c_P2_bar /
  h2c_eta_ad drivers and the suction temperature in C.
- render_h2_purifier_beds: the H2_DRYER params.design books (H2_kg_d, Nm3_h,
  O2_mol_d, water_kg_d, HCl_kg_d, guard_kg, sieve_kg, the beds rows, regen_W,
  T_C, insulation_mm, loss_W, kW).
- render_house_scrubbers: the four scrubbers' params.design books (duty,
  gas_kg_d, Q_m3_s, u_flood_m_s, D_mm, packed_mm, H_mm, recirc_m3_h, dP_Pa,
  fan_W, pump_W, kW) plus the packing driver texts.
- render_upw_polish: the BMED_UPW_POLISH params.design books (bypass_kg_d,
  UPW_kg_d, RO_feed_kg_d, recovery, membrane_m2, modules, osmotic_bar,
  feed_bar, RO_kW, EDI_A, EDI_kW, UV_kW, total_kW, kWh_per_m3,
  kWh_per_m3_RO_EDI) plus the ro_*/edi_* driver texts.
- render_geo_loop: the GEO_GHEX / GEO_HP / GEO_HP_CLOSED_LOOP params.design
  books plus the glycol velocity and head drivers.

The model fields carry the raw v1 float books verbatim (the physics families
stamp the committed books; where the reference writer stored its solve dict
unrounded, the model holds those same floats), so every field formats with
the v1 format string and the bytes match. Pure: no I/O here - the registry
returns bytes and file writing stays outside.
"""
import math
import re

from flow_graph.param.code_basis import MARK as _CODE_MARK          # X-STD-01 block, single source
from flow_graph.param.code_basis import block as _code_block
from flow_graph.v2.functions import evap_design as _EVD             # the VLE float-lane chain
from flow_graph.v2.functions import house_scrubbers as _HS         # the unit order (the doc's row order)
from flow_graph.v2.functions import process as _PR                 # the evap mass books' pure kernel
from flow_graph.v2.functions import receivers as _RCV              # the unit order (the doc's row order)

T0_C = float('273.15')                                             # K -> C offset (the v1 literal)
UPW_PREFIX = 'WTR.potable-upw-train.BMED_UPW_POLISH.'              # the UPW driver prefix (A-M-176)
GL = 'GEO.geo-loop.'                                               # the GEO driver prefix (AQS-DUTY-076)
HSK = 'GAS.scrubbing-headers-train.scrubbing.'                     # the scrubbing driver prefix (A-M-164)
EVK = 'DIGESTER.metals-leach-train.acid-base-regen.'               # the acid-base-regen driver prefix (A-M-106)


def _fld(m, uid, path):
    """A model field: the physics overlay first (at any dotted depth), then
    the committed seed book. Read-only; loud on a missing field."""
    rest = path.split('.')
    cur = None
    for i in range(len(rest), 0, -1):
        key = ('node', uid, '.'.join(rest[:i]))
        if key in m.computed:
            cur = m.computed[key][0]
            rest = rest[i:]
            break
    else:
        cur = m.nodes[uid]
    for part in rest:
        cur = cur[part]
    return cur


def _drv(inputs, key):
    """A driver value, verbatim (the v1 DR.val read over the same payload)."""
    return inputs['drivers'][key]['value']


def _scrub_liquid_raw(m, u, inputs):
    """The raw minimum-wetting liquid book the v1 doc printed (m3/h; the .3f
    cell). The model carries the 4 dp store book, and at the half-thousandth
    the cell double-rounds (NOX_SCRUB: the raw 0.47752208 prints '0.478', the
    0.4775 book prints '0.477'), so the float replica of the reference
    writer's chain runs over the same boundary inputs: the v1 float read of
    the seed gas books and the packing drivers (sizing/scrubber.py)."""
    def v(k):
        return float(str(_drv(inputs, k)))
    rho_g = v(HSK + 'hs_gas_rho_kg_m3')
    gas = sum(float(e['rate']['value'] or 0) for e in m.data['edges']
              if e['to_unit_id'] == u and 'mass' in (e.get('layers') or [])
              and e['phase'].startswith(('G', 'L/G')))
    q_gas = gas / rho_g / 86400                                       # m3/s at the 1.2 kg/m3 book
    uf = v('hs_Cs_flood_m_s') * math.sqrt((1000 - rho_g) / rho_g)     # the flood velocity
    d_m = max(math.sqrt(4 * q_gas / (math.pi * v('hs_frac_flood') * uf)),
              v('hs_dp_mm') * v('vs_d_over_dp') / 1000)               # flood, not below 8 packing diameters
    return v('vs_mwr') * v('hs_a_m2_m3') * math.pi * d_m ** 2 / 4     # the minimum wetting rate


# ---- AQS-DUTY-069: the CRYO_ASU separation train (X-MFG-33) -------------------

def render_cold_box(m, inputs):
    """docs-authority/sizing/COLD_BOX.md: the v1 cold_box.py doc template."""
    r = _fld(m, 'CRYO_ASU', 'params.design')
    ex = r['expander_backup']
    cycle_h = _drv(inputs, 'cb_cycle_h')                            # the v1 DR.load() read, fresh
    md = ['# CRYO_ASU separation train', '', 'Document number: AQS-DUTY-069', 'Revision: C', 'Date: 2026-10-16',
          'Authority: AQS-PLAN-007 X-MFG-33 (rev C: EXPANDER kept as chiller backup, Q-010; rev B: CO2 compressor '
          'staged to the API618 discharge limit, found by AQS-SAF-004). Generated by `flow_graph/param/cold_box.py`. '
          'Study. A-M-175.', '',
          f"Feed (graph): N2 {r['feed_N2_kg_d']:.2f} kg/d (99.92 % N2, rest O2) and CO2 {r['feed_CO2_kg_d']:.2f} kg/d "
          f"from NOX_SCRUB; no intake air (IA-AIR-IN 0). CO2 {r['x_CO2'] * 100:.1f} mol %. Nitrogen meets its 99 % "
          'product purity once the CO2 is removed, so the train has no cryogenic column.', '',
          '| Item | Design | kW |', '|---|---|---|',
          f"| CO2 TSA | 3 x 13X beds (1 adsorbing, 1 regenerating at 204 C per NASA_CDRA2015, 1 standby), "
          f"{r['sorbent_kg_per_bed']:.0f} kg each at 1.5 mol/kg working capacity, {cycle_h:.0f} h half-cycle; "
          f"DN{round(r['bed_D_mm'], -1):.0f} x {r['bed_L_mm']:.0f} mm 316L | {r['regen_kW']:.2f} |",
          f"| Feed blower | 10 kPa rise | {r['blower_kW']:.3f} |",
          f"| CO2 compressor | {r['comp_stages']} stages, ratio {r['comp_ratio_per_stage']:.2f}, intercooled, to 20 bar; "
          f"discharge {r['comp_T_out_C']:.0f} C within the API618 150 C limit | {r['co2_comp_kW']:.3f} |",
          f"| CO2 condenser | -20 C, latent 282 kJ/kg (NIST_WEBBOOK), chiller COP 2.5 | {r['co2_chill_kW']:.3f} |",
          f"| Ar getter | heated getter on the WAFER_FAB return | {r['getter_kW']:.2f} |",
          f"| Total | | {r['total_kW']:.2f} |", '',
          'He, Ne, Kr and Xe are closed inventories that return from their stores and pass through; no separation duty. '
          + f"The EXPANDER is kept as the diverse backup for the condenser chiller (owner decision Q-010, redundancy "
          f"rule): N2 reverse-Brayton loop, pressure ratio 5, outlet {ex['T_out_C']:.0f} C, {ex['loop_kg_d']:.0f} kg/d "
          f"N2 for {ex['cold_kW']:.3f} kW cold at -25 C, {ex['net_kW']:.3f} kW net (COP {ex['COP']:.2f} against the "
          "chiller's 2.5). It is idle in normal operation; a chiller failure starts it. A-M-186.",
          '',
          'The regeneration heat is electric in this revision. Taking it from the Q2 ladder (200-250 C) is the first '
          'saving to study. Sorbent capacity, heat of adsorption and the chiller COP are assumptions until the bed '
          'breakthrough test (A-M-175).']
    return ('\n'.join(md) + '\n').encode('utf-8')


# ---- AQS-DUTY-060: the MVR evaporators (X-MFG-30) -----------------------------

def _evap_options(inputs, mass):
    """The v1 evap_design.options() study helper (doc-only, renderer lane):
    HCl-in-condensate options on the acid unit, compared on vapour (blower
    power scales with it) and added equipment. mass: the process family's
    evap mass book (exact Decimals); the float chain is the v1 solver's."""
    def v(k):
        return _drv(inputs, k)
    xF = v('bmed_product_wt_acid') * 100
    xB = v('acid_conc_design_wt') * 100
    product = float(str(mass['product']))                           # the v1 e['product_kg_d'] book
    water = float(str(mass['water']))
    cond = v('evap_cond_hcl_wt')                                    # the v1 e['cond_hcl_wt']
    recycle = water * cond                                          # the v1 e['recycle_hcl_kg_d']
    V0 = product * xB / xF - product                                # vapour with no HCl recycle
    yB = _EVD.bubble(xB)[1]
    yF = _EVD.bubble(xF)[1]
    xD = cond * 100
    LV = (yB - xD) / (xB - xD)
    Rmin = LV / (1 - LV)
    y14 = _EVD.bubble(14)[1]
    w = float('16.0')
    y16 = _EVD.bubble(w)[1]
    P16 = product * xB / w
    F16 = P16 * (w - y16) / (xF - y16)
    V16 = F16 - P16
    return [dict(option='a', name='rectifier with reflux on the vapour line (feed to the body)',
                 vapour_factor=round(1 + Rmin, 2),
                 note=f'minimum reflux {Rmin:.1f} (pinch at the body vapour {yB:.1f} wt%); blower power at least x{1 + Rmin:.1f}'),
            dict(option='b', name='two stages, final stage once-through', vapour_factor=None,
                 note=f'final-stage vapour runs {y14:.1f} to {yB:.1f} wt% HCl, above the {xF:.2f} wt% feed; still needs a column to return HCl'),
            dict(option='c', name='lower product strength, 16 wt%', vapour_factor=round(V16 / V0, 2),
                 note=f'body vapour {y16:.1f} wt% HCl; recycle makes the feed {F16:.0f} kg/d and the vapour x{V16 / V0:.1f}; leach takes 25 % more liquor'),
            dict(option='d', name='counter-current column on the body, feed at the top (adopted)',
                 vapour_factor=round(water / V0, 3),
                 note=f'no reflux; top vapour {xD:.2f} wt% HCl against {yF:.2f} wt% equilibrium over the feed; '
                      f'recycle {recycle:.2f} kg/d HCl to BMED_ACID')]


_EVAP_LAB = (('T_boil_C', 'Boiling temperature, °C'), ('T_cond_C', 'Condensing temperature, °C'),
             ('p_body_kPa', 'Body pressure, kPa abs'), ('p_shell_kPa', 'Shell pressure, kPa abs'),
             ('ratio', 'Compression ratio'), ('water_kg_h', 'Water evaporated, kg/h'),
             ('duty_kW', 'Evaporation duty, kW'), ('w_kJ_kg', 'Compressor work, kJ/kg'),
             ('comp_shaft_kW', 'Compressor shaft power, kW'), ('comp_elec_kW', 'Compressor electrical power, kW'),
             ('pump_kW', 'Recirculation pump, kW'), ('trim_kW', 'Trim heater, kW'),
             ('total_kW', 'Total electrical power, kW'), ('kWh_per_t', 'Specific energy, kWh per tonne of water'),
             ('A_ff_m2', 'Falling-film area, m²'), ('tubes', 'Tubes'),
             ('tube_id_mm', 'Tube inside diameter, mm'), ('tube_L_mm', 'Tube length, mm'),
             ('recirc_kg_h', 'Recirculation, kg/h'), ('shell_D_mm', 'Shell diameter, mm'),
             ('height_mm', 'Height, mm'), ('ix_Q_kW', 'Interchanger duty, kW'),
             ('ix_A_m2', 'Interchanger area, m²'), ('T_feed_preheat_C', 'Feed after the interchanger, °C'),
             ('T_out_C', 'Product and condensate outlet, °C'))


def render_evap_design(m, inputs):
    """docs-authority/sizing/EVAP_DESIGN.md: the v1 evap_design.py doc
    template, closed with the X-STD-01 code-basis block (the v1 write_doc
    append, composed here in memory)."""
    def v(k):
        return _drv(inputs, k)
    a = _fld(m, 'EVAP_ACID', 'params.design')
    b = _fld(m, 'EVAP_BASE', 'params.design')
    c = a['column']
    relief = (('EVAP_ACID', _fld(m, 'EVAP_ACID', 'params.relief_basis')),
              ('EVAP_BASE', _fld(m, 'EVAP_BASE', 'params.relief_basis')))
    s = _PR._core(m, inputs)                                        # the masses' strangler kernel (seed reads)
    assert s is not None, 'evap doc: the mass books need the driver payload'
    ea = s['ea']                                                    # the v1 s['evap_acid'] mass books
    feed = float(str(ea['feed']))
    water = float(str(ea['water']))
    options = _evap_options(inputs, ea)
    lat = v(EVK + 'evap_latent_kJ_kg')
    t = '\n'.join(f'| {l} | {a[k]} | {b[k]} |' for k, l in _EVAP_LAB)
    rl = '\n'.join(f"| {cs} | {u} | {case['W_kg_h']} | {case['P1_kPa_abs']} | {case['A_req_mm2']} | "
                   f"API 526 D (71 mm²), {'adequate' if case['adequate'] else 'not adequate'} |"
                   for u, basis in relief
                   for cs, case in (('Body fire', basis), ('Shell blocked outlet', basis['shell_side'])))
    op = '\n'.join(f"| {o['option']} | {o['name']} | {o['vapour_factor'] if o['vapour_factor'] else '—'} | {o['note']} |"
                   for o in options)
    trim = max(a['trim_kW'], b['trim_kW'])
    trim_txt = ('The compressor work covers the heat needed to bring the feed to the boil, so neither evaporator '
                'needs a continuous trim heater.' if trim == 0 else
                f'The compressor work does not cover all the heat needed to bring the feed to the boil, so a trim '
                f'heater supplies the rest ({a["trim_kW"]} kW on EVAP_ACID and {b["trim_kW"]} kW on EVAP_BASE).')
    md = f"""# In-house mechanical vapour recompression evaporators EVAP_ACID and EVAP_BASE

Document number: AQS-DUTY-060
Revision: C
Date: 2026-10-29
Generated by `flow_graph/param/evap_design.py` from the plant graph and `flow_graph/param/drivers.json`. Do not edit by hand; change the generator or its inputs and run `python3 -m flow_graph.param.regen`.
Authority: task X-MFG-30; owner decision of 2026-10-15 that the evaporators are designed and built in house to an open design, with no bought skid. Study. Not a PE stamp.

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue: falling-film design with mechanical vapour recompression, interchanger and in-house relief. | 2026-10-15 |
| B | HCl in the acid vapour quantified from Perry's Tables 2-9 and 2-10; counter-current column added on EVAP_ACID (option d); condensate at 0.5 wt% HCl recycles to BMED_ACID. | 2026-10-15 |
| C | Document number, revision and purpose and scope added; the basis written as sentences with the driver values; tables numbered and labelled with units; the comparison with an earlier upper bound removed | 2026-10-29 |

## 1. Purpose and scope

This page designs the two evaporators that concentrate the products of the bipolar membrane stacks: EVAP_ACID for hydrochloric acid and EVAP_BASE for sodium hydroxide. It gives the method, the size and power of each evaporator, the relief valves, the outlet temperatures, the materials, and the column that keeps HCl out of the acid condensate. The water to be evaporated comes from the plant solver.

## 2. Basis

Each evaporator is a single-effect falling-film evaporator with mechanical vapour recompression (MVR). The liquor runs down the inside of vertical tubes, the compressed vapour condenses on the shell side, and the body is at {v('evap_body_kPa'):g} kPa. The {v('acid_conc_design_wt') * 100:g} wt% HCl boils at its azeotrope temperature, {v('evap_bp_acid_C'):g} °C [PERRY9_HCL], which is the bounding case; the {v('base_conc_design_wt') * 100:g} wt% NaOH boils at {v('evap_bp_base_C'):g} °C, a boiling-point elevation of {v('evap_bp_base_C') - 100:g} K [MCCABE7_DUHRING].

Saturation pressures come from region 4 of IAPWS-IF97, and the latent heat is {lat:g} kJ/kg [IAPWS_IF97]. The compressor raises the vapour to the saturation pressure {v('evap_dT_drive_K'):g} K above the boiling point. Its work is the ideal-gas isentropic work with k = {v('evap_k_steam'):g}, divided by an efficiency of {v('evap_comp_eta'):g} [PERRY9_PUMP] and a motor efficiency of {v('evap_motor_eta'):g} (A-M-106).

The falling-film coefficient is {v('evap_U_ff'):g} W/(m² K) at that driving difference [PERRY9_EVAP] (A-M-106). The minimum wetting rate of {v('evap_wet_min'):g} kg/(m s) sets the recirculation [PERRY9_EVAP]. The feed enters at {v('evap_feed_T_C'):g} °C and is preheated in a counter-current interchanger against the condensate and the product, with a {v('evap_approach_K'):g} K approach and a coefficient of {v('evap_U_ix'):g} W/(m² K) [PERRY9_EVAP] [INCROPERA7]. The HCl and water equilibrium uses fits to Perry's 7th edition Tables 2-9 and 2-10 [PERRY7_HCL_VLE] in `flow_graph/param/sizing/hcl_vle.py`.

## 3. Results

Table 3.1 gives the design of each evaporator.

Table 3.1. Evaporator design

| Quantity | EVAP_ACID | EVAP_BASE |
| --- | --- | --- |
{t}

{trim_txt}

## 4. Relief

The body relief case is fire, with Q = 21000 F A^0.82 Btu/h and 21 % overpressure (ISO 23251 and API 521). The shell relief case is a blocked outlet with the compressor at 120 % of its design flow and 10 % overpressure. Both valves are sized as gas to API 520 Part I and built to ISO 4126-1. The body is designed for {v('evap_body_design_kPag'):g} kPa g and full vacuum, and the shell for {v('evap_shell_design_kPag'):g} kPa g (A-M-107). Table 4.1 gives the result for each case.

Table 4.1. Relief cases

| Case | Unit | Flow, kg/h | Relieving pressure, kPa abs | Area required, mm² | Valve |
| --- | --- | --- | --- | --- | --- |
{rl}

## 5. Outlet temperatures (X-MAT-20)

The product and the condensate leave the interchanger at {a['T_out_C']} °C on the acid unit and {b['T_out_C']} °C on the base unit, below the 60 °C limit of line class P1 (AQS-STD-002). The condensate lines therefore stay in class P1, and IA-ACID-01 stays in class P2 for hot leach service. The parameter `T_C` of each outlet stream on the graph carries these values.

## 6. Materials

The acid unit has impregnated graphite tubes, tube sheets and interchanger, a PTFE-lined steel shell and separator, a column of borosilicate glass 3.3 with PTFE packing, and PVDF piping [PERRY9_MAT] [ULLMANN_HCL]. The base unit is nickel 200 [PERRY9_MAT]. Fasteners outside the wetted zone are ISO 3506 A4-70 on the acid unit and ISO 898-1 class 8.8 on the base unit.

## 7. Manufacturing

The model `models/mfg/evap_mvr.py` (CadQuery) reads `params.design` from the graph and exports `models/mfg/EVAP_*/export/*.step` and `*.stl`. Each unit folder holds its bill of materials `bom.csv`, its fasteners `fasteners.csv` and its work order `WO.md`. The fabrication routes are in `docs-authority/fab/EVAP_*.md`.

## 8. HCl in the acid vapour

From the Perry tables, the vapour over the {v('acid_conc_design_wt') * 100:g} wt% body liquid at {v('evap_body_kPa'):g} kPa carries {c['y_eq_body_pct']} wt% HCl, more than the {v('bmed_product_wt_acid') * 100:.2f} wt% feed, so a well-mixed body cannot send its condensate back to BMED_ACID. The vapour over the feed carries {c['y_eq_feed_pct']} wt%. Table 8.1 compares the ways to keep the HCl out of the condensate.

Table 8.1. Options for the HCl in the acid vapour

| Option | Description | Vapour against the base case | Finding |
| --- | --- | --- | --- |
{op}

Option d is adopted, as the smallest complete system. The feed enters the top of a packed column on the body frame, and the liquid runs down against the body vapour and reaches the body at {v('acid_conc_design_wt') * 100:g} wt%. No reflux is drawn, so the compressor duty rises only by the recycled water. The column has {c['column_stages']} ideal stages above the body, from the Perry equilibrium, packed to {c['packed_mm']} mm at a height per stage of {v('evap_col_hetp_mm'):g} mm times {v('evap_col_margin'):g} [PERRY9_ABS] (A-M-108). It is DN{c['DN']} at {v('evap_col_u_m_s'):g} m/s vapour and {c['height_mm']} mm high, {c['placement']}.

The condensate carries {c['cond_hcl_wt_pct']} wt% HCl ({c['recycle_hcl_kg_d']} kg/d). It returns to BMED_ACID with the make-up water and comes back in the feed, which rises to {feed:.1f} kg/d, with {water:.1f} kg/d of water evaporated. The BMED current does not change, because the recycled HCl is not generated again. The owner may choose another option, for example option a if a condensate with almost no HCl is wanted.
"""
    # the v1 write_doc composition: strip any code-basis block, then append the
    # EVAP_DESIGN rows (X-STD-01, the composer lane)
    body = re.sub(r'\n' + re.escape(_CODE_MARK) + r'.*?(?=\n## |\Z)', '', md, flags=re.S).rstrip('\n') \
        + '\n\n' + _code_block('EVAP_DESIGN')
    return body.encode('utf-8')


# ---- AQS-DUTY-065: the high-pressure gas receivers ----------------------------

def render_gas_receivers(m, inputs):
    """docs-authority/sizing/GAS_RECEIVERS.md: the v1 receivers.py doc template."""
    md = ['# High-pressure gas receivers', '', 'Document number: AQS-DUTY-065', 'Revision: B', 'Date: 2026-10-16',
          'Revision B 2026-10-16 adds CRYO_CO2 (A-M-181). Authority: X-MFG-40 follow-on (CRYO_H2, CRYO_O2, CRYO_CO2 '
          'were Section VIII-1 awaiting size). Generated by `flow_graph/param/receivers.py`. Study. A-M-167.', '',
          '| Unit | Design MPa | t req / min, mm | Tube | Banks | Tubes | Steel, kg | Rack L x W x H, mm |',
          '|---|---|---|---|---|---|---|---|']
    for u in _RCV.UNITS:
        r = _fld(m, u, 'params.design')
        # the v1 doc printed the raw wall book; the model carries the 4 dp
        # store book, whose .2f cell double-rounds (CRYO_CO2: raw 1.0850052
        # prints '1.09', the 1.085 book prints '1.08'), so the raw float
        # replica runs on the model's own exact books (B31.3 304.1.2, Y 0.4)
        t_req = r['P_design_MPa'] * r['OD_mm'] / (2 * (r['S_MPa'] + r['P_design_MPa'] * float('0.4')))
        md.append(
            f"| {u} | {r['P_design_MPa']:.1f} | {t_req:.2f} / {r['t_min_mm']:.2f} "
            f"{'ok' if r['t_ok'] else 'NOT OK'} | DN100 Sch 160 316L x {r['tube_m']} m (ID {r['ID_mm']:.1f}) | "
            + '; '.join(f"{b['bank']} {b['V_m3']:.3f} m3" for b in r['banks'])
            + f" | {r['tubes']} | {r['steel_kg']:.0f} | {' x '.join(str(x) for x in r['rack_mm'])} |")
    md += ['', 'Wall per ASME_B31_3 304.1.2 (outside-diameter form, Y 0.4) with S 115 MPa (ASME_II_D, SA-312 TP316L '
            'to 38 C), E 1, no corrosion allowance (dry gas), Sch 160 less 12.5 % mill tolerance. ID 87.3 mm is under '
            'the 152 mm Section VIII-1 size limit (ASME_VIII1_U1), so each tube is a piping component. Each bank is '
            'two manifolded halves with isolation and its own relief (pressure_nodes.py blocked-outlet case), so a '
            'leaking tube takes out at most half a bank. Fatigue from daily cycling and hydrogen-assisted fatigue of '
            '316L are checked at the first-article cycle test (A-M-167).']
    return ('\n'.join(md) + '\n').encode('utf-8')


# ---- AQS-DUTY-067: the hydrogen compressor (X-MFG-36) -------------------------

def render_h2_compressor(m, inputs):
    """docs-authority/sizing/H2_COMPRESSOR.md: the v1 h2_compressor.py doc template."""
    def v(k):
        return _drv(inputs, k)
    r = _fld(m, 'CRYO_H2', 'params.compressor_design')
    T1C = v('CRYO.cold-box-asu-recovery-train.cold-box.CRYO_H2.h2c_T_suction_K') - T0_C
    units = r['units']
    md = ['# Hydrogen compressor', '', 'Document number: AQS-DUTY-067', 'Revision: C', 'Date: 2026-10-29',
          'Generated by `flow_graph/param/h2_compressor.py` from the plant graph and `flow_graph/param/drivers.json`. '
          'Do not edit by hand; change the generator or its inputs and run `python3 -m flow_graph.param.regen`.',
          'Authority: task X-MFG-36 of AQS-PLAN-007; assumption A-M-169. Study. Not a PE stamp.', '',
          '| Rev | Description | Date |', '| --- | --- | --- |',
          '| A | First issue: an in-house diaphragm compressor for the hydrogen store | 2026-10-16 |',
          '| B | Stage count set by the discharge temperature limit; the two-stage layout of Rev A ran too hot | 2026-10-16 |',
          '| C | Record of revisions, purpose and scope added; the design written as sentences; the suction temperature '
          'and pressures taken from the drivers in the text | 2026-10-29 |', '',
          '## 1. Purpose and scope', '',
          'This page sizes the in-house multi-stage diaphragm compressor that fills the hydrogen store `CRYO_H2`. It '
          'gives the number of stages, the pressures and discharge temperature of each stage, the intercooler duty, '
          'the swept volume and diaphragm diameter, and the power. The hydrogen flow is the sum of the mass streams '
          'into `CRYO_H2` on the plant graph.', '',
          '## 2. Design', '',
          f"The compressor takes {r['H2_kg_d']:.2f} kg/d of hydrogen from {v('h2c_P1_bar'):g} bar to "
          f"{v('h2c_P2_bar'):g} bar in {r['n_stages']} stages of equal pressure ratio {r['ratio_per_stage']:.3f}, with "
          f"an intercooler after each stage that returns the gas to {T1C:.0f} °C. "
          'The number of stages is the smallest for which the predicted discharge temperature, at an adiabatic '
          f"efficiency of {v('h2c_eta_ad')}, stays at or below {r['T_limit_C']:.0f} °C, the limit for hydrogen-rich "
          'service in [API618]. '
          f"The specific energy is {r['kWh_per_kg']:.2f} kWh/kg, the average power {r['P_avg_kW']:.3f} kW and the peak "
          f"power over the run hours {r['P_peak_kW']:.3f} kW. "
          + (f"{units:g} compressors are fitted, one of them standby."
             if isinstance(units, (int, float)) and units > 1 else 'One compressor is fitted.'), '',
          'Table 2.1 gives the stages.', '', 'Table 2.1. Compressor stages', '',
          '| Stage | In bar | Out bar | Discharge °C | Intercooler W (peak) | Swept cm3/stroke | Diaphragm D mm |',
          '|---|---|---|---|---|---|---|']
    md += [f"| {s['stage']} | {s['P_in_bar']:.1f} | {s['P_out_bar']:.1f} | {s['T_out_C']:.0f} | "
           f"{s['intercooler_W']:.0f} | {s['swept_cm3']:.1f} | {s['diaphragm_D_mm']:.0f} |" for s in r['stages']]
    md += ['', '## 3. Construction', '',
           'The materials are as follows: ' + r['material'] + '. The intercoolers are 316L tube-in-tube exchangers on '
           'the cooling water loop. The efficiencies, the speed and the cavity depth are assumptions until the first '
           'article has been run on the bench (A-M-169).']
    return ('\n'.join(md) + '\n').encode('utf-8')


# ---- AQS-DUTY-066: the H2 purifier beds (X-MFG-39) ----------------------------

_PURIFIER_FIELDS = ('H2_kg_d', 'Nm3_h', 'O2_mol_d', 'water_kg_d', 'HCl_kg_d', 'guard_kg', 'sieve_kg', 'beds',
              'regen_W', 'loss_W', 'insulation_mm', 'kW', 'T_C')


def render_h2_purifier_beds(m, inputs):
    """docs-authority/sizing/H2_PURIFIER_BEDS.md: the v1 h2_purifier.py doc template."""
    u = 'H2_DRYER' if 'H2_DRYER' in m.nodes else 'H2_PURIFIER'      # the R11 Rev AC node rename
    r = {k: _fld(m, u, 'params.design.' + k) for k in _PURIFIER_FIELDS}
    md = ['# H2_PURIFIER beds', '', 'Document number: AQS-DUTY-066', 'Revision: A', 'Date: 2026-10-15',
          'Authority: AQS-PLAN-007 X-MFG-39. Generated by `flow_graph/param/h2_purifier.py`. Study. A-M-168.', '',
          'Unit task 02 for H2_DRYER (the Rev AC node name of this purifier train).', '',
          f"Feed {r['H2_kg_d']:.2f} kg/d H2 ({r['Nm3_h']:.2f} Nm3/h). O2 {r['O2_mol_d']:.2f} mol/d, water "
          f"{r['water_kg_d'] * 1000:.1f} g/d, HCl {r['HCl_kg_d'] * 1000:.3f} g/d. Product to ISO_14687 Grade D (water "
          'and O2 at or below 5 umol/mol, halogenates 0.05 umol/mol).', '',
          '| Bed | Volume, L | Tube | Length, mm | Count |', '|---|---|---|---|---|']
    md += [f"| {b} | {x['V_L']:.3f} | {x['tube']} | {x['L_mm']} | {x['count']} |" for b, x in r['beds'].items()]
    md += ['', f"Guard charge {r['guard_kg'] * 1000:.0f} g; sieve {r['sieve_kg'] * 1000:.0f} g per TSA bed. "
           f"Regeneration {r['regen_W']:.1f} W average at {r['T_C']} C, insulation {r['insulation_mm']} mm "
           f"(loss {r['loss_W']:.0f} W while hot); electric load {r['kW'] * 1000:.0f} W. Every bed is duplicated (one "
           'on line). All capacities and the space velocity are assumptions (A-M-168) until the bed tests.',
           '',
           'X-PAR-15: the feed water now leaves on IA-H2P-H2O to VCD_TRAIN (with the fuel-cell water S52, which falls '
           'by the same mass) and S49P is dry H2 to Grade D. Deoxo water is formed from O2 that the graph does not '
           'yet carry on S49 (1000 ppm v assumed here); it is inside the TSA load above.']
    return ('\n'.join(md) + '\n').encode('utf-8')


# ---- AQS-DUTY-079: the house scrubbers (X-PAR-03) -----------------------------

_HS_FIELDS = ('duty', 'gas_kg_d', 'Q_m3_s', 'u_flood_m_s', 'D_mm', 'packed_mm', 'H_mm', 'recirc_m3_h',
              'dP_Pa', 'fan_W', 'pump_W', 'kW')


def render_house_scrubbers(m, inputs):
    """docs-authority/sizing/HOUSE_SCRUBBERS.md: the v1 house_scrubbers.py doc template."""
    def v(k):
        return _drv(inputs, k)
    md = """# House scrubbers

Document number: AQS-DUTY-079  
Former number: AQS-DUTY-064 (shared with sizing/STORAGE_HOLDUP.md until 2026-10-24; that page keeps it)
Revision: A
Date: 2026-10-15
Authority: AQS-PLAN-007 X-PAR-03 (scrubber function applied). Generated by `flow_graph/param/house_scrubbers.py`. Study. A-M-164.

| Unit | Duty | Gas, kg/d | Gas, m3/s | Flood velocity, m/s | Diameter, mm | Bed, mm | Height, mm | Liquid, m3/h | dP, Pa | Fan, W | Pump, W | kW |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
"""
    for u in _HS.UNITS:
        r = {k: _fld(m, u, 'params.design.' + k) for k in _HS_FIELDS}
        recirc = _scrub_liquid_raw(m, u, inputs)                    # the v1 raw liquid book (see the helper)
        md += f"| {u} | {r['duty']} | {r['gas_kg_d']:.1f} | {r['Q_m3_s']:.4f} | {r['u_flood_m_s']:.2f} | {r['D_mm']} | {r['packed_mm']} | {r['H_mm']} | {recirc:.3f} | {r['dP_Pa']:.0f} | {r['fan_W']:.1f} | {r['pump_W']:.1f} | {r['kW']} |\n"
    md += f"""
Basis: flooding u_f = C_s sqrt((rho_L - rho_G)/rho_G), D at {v('hs_frac_flood')} of flood (PERRY9_ABS), not below {v('vs_d_over_dp'):.0f} packing diameters; bed = HTU x ln(1/(1 - {v('hs_removal')})) with a 0.5 m minimum; minimum wetting rate {v('vs_mwr')} m3/(m h) (PERRY9_ABS). Packing is the in-house {v('hs_dp_mm'):.0f} mm cut PP ring: C_s {v('hs_Cs_flood_m_s')} m/s, HTU {v('hs_htu_m')} m, {v('hs_dP_Pa_m'):.0f} Pa/m and a = {v('hs_a_m2_m3'):.0f} m2/m3 are assumptions (A-M-164) until the column flooding and absorption tests on the in-house packing are run. Gas density {v(HSK + 'hs_gas_rho_kg_m3')} kg/m3. The scrub chemistry is AQS SCRUBBER_CHEMISTRY.md; EVAP_ACID_VS stays on its own design (X-PAR-10).
"""
    return md.encode('utf-8')


# ---- AQS-DUTY-070: the ultrapure water polish (X-MFG-34) ----------------------

_UPW_FIELDS = ('UPW_kg_d', 'bypass_kg_d', 'RO_feed_kg_d', 'recovery', 'osmotic_bar', 'feed_bar', 'membrane_m2',
               'modules', 'RO_kW', 'EDI_A', 'EDI_kW', 'UV_kW', 'total_kW', 'kWh_per_m3', 'kWh_per_m3_RO_EDI')


def render_upw_polish(m, inputs):
    """docs-authority/sizing/UPW_POLISH.md: the v1 upw_polish.py doc template."""
    def v(k):
        return _drv(inputs, k)
    r = {k: _fld(m, 'BMED_UPW_POLISH', 'params.design.' + k) for k in _UPW_FIELDS}
    mods = v(UPW_PREFIX + 'ro_modules')
    md = ['# Ultrapure water polish (RO and EDI)', '', 'Document number: AQS-DUTY-070', 'Revision: B',
          'Date: 2026-10-29',
          'Generated by `flow_graph/param/upw_polish.py` from the plant graph and `flow_graph/param/drivers.json`. '
          'Do not edit by hand; change the generator or its inputs and run `python3 -m flow_graph.param.regen`.',
          'Authority: task X-MFG-34 of AQS-PLAN-007; assumption A-M-176. Study. Not a PE stamp.', '',
          '| Rev | Description | Date |', '| --- | --- | --- |',
          '| A | First issue: reverse osmosis and electrodeionisation sized from the graph duty; the potable share '
          'bypasses the train | 2026-10-16 |',
          '| B | Record of revisions, purpose and scope added; the design written as sentences with the driver values; '
          'tables numbered | 2026-10-29 |', '',
          '## 1. Purpose and scope', '',
          'This page sizes the ultrapure water (UPW) polish `BMED_UPW_POLISH`: a reverse osmosis (RO) stage, an '
          'electrodeionisation (EDI) stage and an ultraviolet lamp that destroys total organic carbon (UV-TOC). The '
          'flows come from the plant graph.', '',
          '## 2. Flows', '',
          f"The feed, stream S25, is distillate from the vapour compression distiller, with about "
          f"{v('ro_feed_TDS_mg_L'):.0f} mg/L of dissolved solids (A-M-176). "
          f"The potable share of {r['bypass_kg_d']:.1f} kg/d goes to remineralisation `REMIN` and bypasses the polish. "
          f"The ultrapure water product of {r['UPW_kg_d']:.1f} kg/d, for the fab and the header `HDR_UPW`, passes "
          'through the RO stage and then the EDI stage. '
          f"The RO feed is {r['RO_feed_kg_d']:.1f} kg/d at a recovery of {r['recovery'] * 100:.1f} %; the reject "
          'leaves by stream IA-UPW-REJ.', '',
          '## 3. Design', '',
          'The RO flux follows the solution-diffusion model J = A (ΔP − Δπ) [BAKER2012], with a permeance A of '
          f"{v('ro_A_LMH_bar'):g} L/(m2 h bar) and a design flux of {v('ro_flux_LMH'):g} L/(m2 h). "
          f"This gives {r['membrane_m2']:.2f} m2 of flat-sheet thin-film composite membrane per module; {mods:g} "
          'modules are fitted, one of them standby. The mean osmotic pressure is '
          f"{r['osmotic_bar'] * 1000:.0f} mbar and the feed pressure {r['feed_bar']:.1f} bar.",
          'The EDI current carries the salt left in the RO permeate at a current efficiency of '
          f"{v('edi_CE'):g}, through {v('edi_cells'):g} cell pairs at {v('edi_V_cell'):g} V each [ALVARADO2014]. "
          'Two stacks are fitted, one of them standby.',
          f"The UV-TOC lamp, at 185 nm and 254 nm on the ultrapure water loop, is rated {r['UV_kW'] * 1000:.0f} W "
          '(driver `upw_uv_W`).', '',
          'Table 3.1 gives the power of each stage.', '', 'Table 3.1. Power', '',
          '| Stage | Current or flow | Power (W) |', '|---|---|---|',
          f"| RO pump | {r['RO_feed_kg_d']:.1f} kg/d at {r['feed_bar']:.1f} bar | {r['RO_kW'] * 1000:.1f} |",
          f"| EDI | {r['EDI_A'] * 1000:.0f} mA | {r['EDI_kW'] * 1000:.2f} |",
          f"| UV-TOC | | {r['UV_kW'] * 1000:.0f} |",
          f"| Total | | {r['total_kW'] * 1000:.1f} |", '',
          f"The RO and EDI stages use {r['kWh_per_m3_RO_EDI']:.2f} kWh per cubic metre of RO feed, at the low end of "
          'the 0.5 to 3 kWh/m3 range for brackish water RO [GREENLEE2009], because distillate needs little pressure. '
          f"With the UV lamp the figure is {r['kWh_per_m3']:.2f} kWh/m3.",
          'The permeance, the feed dissolved solids and the EDI current efficiency are assumptions until the modules '
          'are tested on the bench (A-M-176).']
    return ('\n'.join(md) + '\n').encode('utf-8')


# ---- AQS-DUTY-076: the GEO loop -----------------------------------------------

_GH_FIELDS = ('Q_ceiling_kW_th', 'k_ground_W_mK', 'T_source_K', 'q_per_m_W', 'bore_metres_req', 'bores',
              'bore_depth_m', 'bore_metres_installed', 'bore_spacing_m', 'header_m', 'loop_DN',
              'loop_flow_kg_s', 'loop_fluid', 'loop_dT_K', 'circ_pump_W', 'material')
_GEO_HP_FIELDS = ('lift_kW_th', 'cop', 'modules', 'module_kW_th', 'source_area_m2', 'condenser_area_m2',
                  'cop_basis', 'material')
_CL_FIELDS = ('design_case_kW_th', 'flow_kg_s', 'DN', 'dT_K', 'head_m', 'pump_W', 'duty', 'material')


def render_geo_loop(m, inputs):
    """docs-authority/sizing/GEO_LOOP.md: the v1 geo_loop.py doc template."""
    def v(k):
        return _drv(inputs, GL + k)
    gh = {k: _fld(m, 'GEO_GHEX', 'params.design.' + k) for k in _GH_FIELDS}
    hp = {k: _fld(m, 'GEO_HP', 'params.design.' + k) for k in _GEO_HP_FIELDS}
    cl = {k: _fld(m, 'GEO_HP_CLOSED_LOOP', 'params.design.' + k) for k in _CL_FIELDS}
    md = ['# GEO loop sizing', '', 'Document number: AQS-DUTY-076', 'Revision: A', 'Date: 2026-10-20',
          'Authority: AQS-PLAN-007 unit tasks (GEO)-02; AQS-HEAT-STUDY-002 (AQS-HEAT-STUDY-002 sec. 6 GHEX ceiling; '
          'D-GEO_ORC keeps GEO_ORC at 0 kW_e). '
          'Generated by `flow_graph/param/geo_loop.py`. Study. Not a PE stamp. Survey values stay locked (ST-ORC-01).',
          '',
          'Unit task 02 for the three GEO units. Design case: the survey-locked GHEX ceiling '
          f'{gh["Q_ceiling_kW_th"]} kW_th (k_ground {gh["k_ground_W_mK"]} W/m K, T_source {gh["T_source_K"]} K, graph '
          f'params) and the issued winter lift {hp["lift_kW_th"]} kW_th on S44. Bore metres = ceiling / '
          f'{gh["q_per_m_W"]} W per metre sustained capacity '
          '(KAVANAUGH2014 small closed-loop band 30-50 W/m; 35 W/m used, registered), split '
          f'{gh["bores"]} x {gh["bore_depth_m"]} m bores at '
          f'{gh["bore_spacing_m"]} m spacing; loop flow {gh["loop_flow_kg_s"]} kg/s of {gh["loop_fluid"]} at a '
          f'{gh["loop_dT_K"]} K rise (registered), DN{gh["loop_DN"]} at {v("glycol_v_m_s")} m/s, circulation '
          f'{gh["circ_pump_W"]} W at {gh["header_m"]:.0f} m header + bore circuit head {v("loop_head_m")} m. Heat pump '
          f'{hp["modules"]} x 100 % (X-RED-07) at COP {hp["cop"]} (graph S44 / SF-GEO_HP; study 3.43 at 285 K), '
          f'brazed-plate areas {hp["source_area_m2"]} m2 source / {hp["condenser_area_m2"]} m2 condenser.', '',
          '| Unit | Design case | Sized result | Material | Notes |', '|---|---|---|---|---|',
          f"| GEO_GHEX | {gh['Q_ceiling_kW_th']} kW_th ceiling, survey-locked | {gh['bores']} bores x "
          f"{gh['bore_depth_m']} m = {gh['bore_metres_installed']} m "
          f"({gh['bore_metres_req']} m required), DN{gh['loop_DN']} loop, {gh['circ_pump_W']} W circulation | "
          f"{gh['material']} | recharge branch 0.7 kW normal, "
          '3.0 kW hard ceiling (AQS-HEAT-STUDY-002 sec. 10.7) |',
          f"| GEO_HP | {hp['lift_kW_th']} kW_th winter lift at COP {hp['cop']} | {hp['modules']} x 100 % modules at "
          f"{hp['module_kW_th']} kW_th; plates {hp['source_area_m2']} + {hp['condenser_area_m2']} m2 | "
          f"{hp['material']} | {hp['cop_basis']} |",
          f"| GEO_HP_CLOSED_LOOP | {cl['design_case_kW_th']} kW_th source loop | {cl['flow_kg_s']} kg/s, DN{cl['DN']}, "
          f"{cl['dT_K']} K rise, {cl['pump_W']} W at {cl['head_m']} m | {cl['material']} | {cl['duty']} |", '',
          'The bore count is a design-output at the locked survey values; the thermal response test (ST-ORC-01 '
          'blockers) can raise the per-metre capacity and cut metres - that is the registered sensitivity. Winter '
          'extraction and summer recharge stay inside the ceiling so the field does not warm into the GEO_HP source '
          'degradation case (AQS-HEAT-STUDY-002 sec. 6). Open: none for task 02 at the survey-locked basis; '
          'the survey confirmation is the registered replacing test.']
    return ('\n'.join(md) + '\n').encode('utf-8')

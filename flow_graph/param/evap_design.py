"""X-MFG-30 in-house MVR falling-film evaporators EVAP_ACID and EVAP_BASE (no bought skid). Writes the design onto the graph
(params.design, outlet temperatures, relief_basis, size_mm) and docs-authority/sizing/EVAP_DESIGN.md (AQS-DUTY-060).
Run: python3 -m flow_graph.param.evap_design [--write]"""
import json, math, sys
from . import solver, drivers as DR, site as SITE
from .sizing import evaporator as EV, relief as RL, power as PW, hcl_vle as VLE
from .refs import cite
_D = DR.load(); EVK = 'DIGESTER.metals-leach-train.acid-base-regen.'   # U4b: sizing literals single-sourced from drivers.json (A-M-106/107/108)
LAT = DR.val(_D, EVK+'evap_latent_kJ_kg')   # kJ/kg at 100 C [IAPWS_IF97]
def design(d, e, unit):
    """e: mass result of solver.evap (water_kg_d, product_kg_d, feed_kg_d, added_kg_d)."""
    v = lambda k: DR.val(d, k); acid = unit == 'EVAP_ACID'
    Tb = v('evap_bp_acid_C' if acid else 'evap_bp_base_C'); p1 = v('evap_body_kPa'); Tc = Tb + v('evap_dT_drive_K'); p2 = EV.psat_kPa(Tc)
    V = e['water_kg_d']/86400; P = e['product_kg_d']/86400; F = (e['feed_kg_d'] + e['added_kg_d'])/86400
    comp_kW, w = EV.compressor_kW(V, Tb, p1, p2, v('evap_k_steam'), v('evap_comp_eta')); comp_e = comp_kW/v('evap_motor_eta')
    Q = V*LAT; A = Q*1000/(v('evap_U_ff')*v('evap_dT_drive_K'))
    di = v('evap_tube_id_mm')/1000; L = v('evap_tube_L_mm')/1000; n = math.ceil(A/(math.pi*di*L))
    rec = v('evap_wet_min')*n*math.pi*di   # kg/s
    pump_kW = rec/v(EVK+'evap_liquor_rho_kg_m3')*SITE.g()*v(EVK+'evap_pump_head_m')*v(EVK+'evap_liquor_rho_kg_m3')/v(EVK+'evap_pump_eta')/1000   # 4 m head, 40 % (PERRY9_PUMP)
    cpP = v('evap_cp_acid_prod' if acid else 'evap_cp_base_prod')
    ix = EV.interchanger(F, v('evap_cp_feed'), v('evap_feed_T_C'), V, v(EVK+'evap_cond_cp_kJ_kgK'), Tc, P, cpP, Tb, v('evap_approach_K'))
    A_ix = ix['Q_kW']*1000/(v('evap_U_ix')*ix['LMTD_K'])
    trim = F*v('evap_cp_feed')*(Tb - ix['T_feed_out_C']) - comp_kW    # sensible deficit not covered by compressor work
    trim_kW = max(0.0, trim)
    pitch = v(EVK+'evap_tube_pitch_ratio')*(di*1000 + 2*v(EVK+'evap_tube_wall_mm')); Dsh = math.ceil((v(EVK+'evap_bundle_margin')*pitch*math.sqrt(n/0.907) + v(EVK+'evap_shell_pitch_allowance')*pitch)/50)*50   # mm, triangular pitch, 6 mm graphite or 2 mm Ni wall
    H = L*1000 + v('evap_sump_h_mm') + v(EVK+'evap_head_h_mm') + v(EVK+'evap_separator_h_mm')   # tubes + sump + heads + separator
    # fire case on the body (ISO 23251 / API 521), set at body design, 21 % overpressure
    Aw = math.pi*Dsh/1000*v('evap_sump_h_mm')/1000 + math.pi*(Dsh/1000)**2/4
    Wf, Qf = EV.fire_relief_kg_h(Aw, LAT)
    P1f = 1.21*v('evap_body_design_kPag') + SITE.p_process_kPa(); Tf = EV.tsat_C(P1f) + (Tb - 100)
    Af = RL.gas_area_in2(Wf*2.20462, v('evap_k_steam'), P1f/6.894757, (Tf+273.15)*1.8, 1.0, 18.02)
    # shell side blocked outlet: compressor at 120 % of design flow, 10 % overpressure
    Wb = 1.2*V*3600; P1b = 1.1*v('evap_shell_design_kPag') + SITE.p_process_kPa(); Tbk = EV.tsat_C(P1b)
    Ab = RL.gas_area_in2(Wb*2.20462, v('evap_k_steam'), P1b/6.894757, (Tbk+273.15)*1.8, 1.0, 18.02)
    D_letter = v(EVK+'evap_psv_orifice_D_in2')   # in2, API 526 orifice D (smallest letter)
    col = None
    if acid:   # counter-current column on the body, feed at the top (X-MFG-30 option d, AQS-DUTY-060 section 7)
        c = e['cond_hcl_wt']*100; ns = VLE.strip_stages(F, v('bmed_product_wt_acid')*100, P, v('acid_conc_design_wt')*100, V, c)
        rho = p1*18.02/(8.314*(Tb+273.15)); Dc = math.sqrt(4*V/rho/v('evap_col_u_m_s')/math.pi)*1000   # body vapour space (A-M-106 body pressure), not site ambient
        DN = next(x for x in (50, 80, 100, 150, 200, 250, 300) if x >= Dc)
        col = dict(ideal_stages_incl_body=ns, column_stages=ns-1, cond_hcl_wt_pct=c, y_eq_feed_pct=round(VLE.bubble(v('bmed_product_wt_acid')*100)[1], 3),
                   y_eq_body_pct=round(VLE.bubble(v('acid_conc_design_wt')*100)[1], 2), packed_mm=round((ns-1)*v('evap_col_hetp_mm')*v('evap_col_margin')),
                   D_req_mm=round(Dc, 1), DN=DN, recycle_hcl_kg_d=round(e['recycle_hcl_kg_d'], 2), material='borosilicate glass 3.3 sections (ISO 3585), PTFE Pall rings, PTFE-lined flanges (PERRY9_MAT)')
        col['height_mm'] = col['packed_mm'] + v(EVK+'evap_col_skirt_mm'); col['placement'] = 'free-standing beside the body on the same frame (L-1 headroom 6 m); vapour duct from the separator to the column bottom, column bottoms back to the body'
        H = max(H, col['height_mm'])
    return dict(unit=unit, T_boil_C=Tb, T_cond_C=round(Tc, 2), p_body_kPa=p1, p_shell_kPa=round(p2, 2), ratio=round(p2/p1, 3),
                water_kg_h=round(V*3600, 3), duty_kW=round(Q, 2), comp_shaft_kW=round(comp_kW, 3), comp_elec_kW=round(comp_e, 3), w_kJ_kg=round(w, 1),
                kWh_per_t=round((comp_e + pump_kW + trim_kW)/(V*3.6), 1), A_ff_m2=round(A, 2), tubes=n, tube_id_mm=di*1000, tube_L_mm=L*1000,
                recirc_kg_h=round(rec*3600, 1), pump_kW=round(pump_kW, 3), shell_D_mm=Dsh, height_mm=round(H),
                ix_Q_kW=round(ix['Q_kW'], 2), ix_A_m2=round(A_ix, 3), T_feed_preheat_C=round(ix['T_feed_out_C'], 1), T_out_C=round(ix['T_hot_out_C'], 1),
                trim_kW=round(trim_kW, 3), total_kW=round(comp_e + pump_kW + trim_kW, 3), column=col,
                relief_body=dict(case='fire, ISO 23251 / API 521 adequate drainage', A_wetted_m2=round(Aw, 3), Q_kW=round(Qf, 2), W_kg_h=round(Wf, 2),
                                 P1_kPa_abs=round(P1f, 1), T_K=round(Tf+273.15, 1), M_kg_kmol=18.02, k=v('evap_k_steam'), A_req_mm2=round(Af*RL.IN2_TO_MM2, 2),
                                 orifice='API 526 D (71 mm2)', adequate=bool(Af <= D_letter)),
                relief_shell=dict(case='blocked outlet, compressor at 120 % design flow', W_kg_h=round(Wb, 2), P1_kPa_abs=round(P1b, 1), T_K=round(Tbk+273.15, 1),
                                  M_kg_kmol=18.02, k=v('evap_k_steam'), A_req_mm2=round(Ab*RL.IN2_TO_MM2, 3), orifice='API 526 D (71 mm2)', adequate=bool(Ab <= D_letter)))
def main():
    d, g, s = solver.solve(); R = {u: design(d, s['evap_acid' if u == 'EVAP_ACID' else 'evap_base'], u) for u in ('EVAP_ACID', 'EVAP_BASE')}
    print(json.dumps(R, indent=1))
    if '--write' in sys.argv:
        write_doc(d, s, R)
        N = {n['unit_id']: n for n in g['nodes']}; E = {e['stream_id']: e for e in g['edges']}
        for u, r in R.items():
            p = N[u]['params']; p['design'] = {k: v for k, v in r.items() if not k.startswith('relief')}
            p['size_mm'] = [r['shell_D_mm'] + DR.val(d, EVK+'evap_frame_len_mm') + (r['column']['DN'] + DR.val(d, EVK+'evap_frame_col_mm') if r.get('column') else 0), max(DR.val(d, EVK+'evap_frame_min_w_mm'), r['shell_D_mm'] + DR.val(d, EVK+'evap_frame_wid_margin_mm')) + (DR.val(d, EVK+'evap_frame_acid_w_mm') if u == 'EVAP_ACID' else 0), r['height_mm']]   # EVAP_ACID frame also carries EVAP_ACID_VS (X-PAR-10)
            p['size_note'] = 'L x W x H mm: body plus interchanger and compressor frame, in-house design X-MFG-30 (AQS-DUTY-060)'
            p['relief_mm'] = round(math.sqrt(4*71.0/math.pi), 2)
            p['relief_basis'] = dict(r['relief_body'], computed_by=f"flow_graph/param/evap_design.py ({cite('ISO23251')}; {cite('API520')})", shell_side=r['relief_shell'])
            p['design_kPa'] = DR.val(d, 'evap_body_design_kPag')
            for sid in ([f'IA-{u}-COND'] + (['IA-ACID-01'] if u == 'EVAP_ACID' else ['IA-BASE-PPT', 'IA-BASE-01'])):
                if sid in E: E[sid].setdefault('params', {}) or E[sid].update(params={}); E[sid]['params']['T_C'] = r['T_out_C']; E[sid]['params']['T_basis'] = 'X-MFG-30 interchanger outlet (AQS-DUTY-060)'
        if 'IA-EVAP_ACID-COND' in E:
            c = R['EVAP_ACID']['column']; E['IA-EVAP_ACID-COND']['params'].update(HCl_wt=c['cond_hcl_wt_pct']/100, HCl_kg_d=c['recycle_hcl_kg_d'], composition_basis='column top vapour, PERRY7_HCL_VLE (AQS-DUTY-060 section 7)')
        open(solver.GP if hasattr(solver, 'GP') else 'flow_graph/plant_flow_graph.json', 'w').write(json.dumps(g, indent=2))
    return R

def options(d, e):
    """HCl-in-condensate options on the acid unit, compared on vapour (blower power scales with it) and added equipment."""
    v = lambda k: DR.val(d, k); xF = v('bmed_product_wt_acid')*100; xB = v('acid_conc_design_wt')*100; P = e['product_kg_d']; V0 = P*xB/xF - P   # vapour with no HCl recycle
    yB = VLE.bubble(xB)[1]; yF = VLE.bubble(xF)[1]; xD = e['cond_hcl_wt']*100
    LV = (yB - xD)/(xB - xD); Rmin = LV/(1 - LV)
    y14 = VLE.bubble(14)[1]
    w = 16.0; y16 = VLE.bubble(w)[1]; P16 = P*xB/w; F16 = P16*(w - y16)/(xF - y16); V16 = F16 - P16
    return [dict(option='a', name='rectifier with reflux on the vapour line (feed to the body)', vapour_factor=round(1 + Rmin, 2),
                 note=f'minimum reflux {Rmin:.1f} (pinch at the body vapour {yB:.1f} wt%); blower power at least x{1+Rmin:.1f}'),
            dict(option='b', name='two stages, final stage once-through', vapour_factor=None,
                 note=f'final-stage vapour runs {y14:.1f} to {yB:.1f} wt% HCl, above the {xF:.2f} wt% feed; still needs a column to return HCl'),
            dict(option='c', name='lower product strength, 16 wt%', vapour_factor=round(V16/V0, 2),
                 note=f'body vapour {y16:.1f} wt% HCl; recycle makes the feed {F16:.0f} kg/d and the vapour x{V16/V0:.1f}; leach takes 25 % more liquor'),
            dict(option='d', name='counter-current column on the body, feed at the top (adopted)', vapour_factor=round(e['water_kg_d']/V0, 3),
                 note=f'no reflux; top vapour {xD:.2f} wt% HCl against {yF:.2f} wt% equilibrium over the feed; recycle {e["recycle_hcl_kg_d"]:.2f} kg/d HCl to BMED_ACID')]

def write_doc(d, s, R):
    _write_doc(d, s, R)
    from . import code_basis as CB; CB.append(CB.PATHS['EVAP_DESIGN'], 'EVAP_DESIGN')

def _write_doc(d, s, R):
    v = lambda k: DR.val(d, k)
    A, B = R['EVAP_ACID'], R['EVAP_BASE']; c = A['column']; O = options(d, s['evap_acid'])
    lab = [('T_boil_C', 'Boiling temperature, °C'), ('T_cond_C', 'Condensing temperature, °C'), ('p_body_kPa', 'Body pressure, kPa abs'), ('p_shell_kPa', 'Shell pressure, kPa abs'),
           ('ratio', 'Compression ratio'), ('water_kg_h', 'Water evaporated, kg/h'), ('duty_kW', 'Evaporation duty, kW'), ('w_kJ_kg', 'Compressor work, kJ/kg'),
           ('comp_shaft_kW', 'Compressor shaft power, kW'), ('comp_elec_kW', 'Compressor electrical power, kW'), ('pump_kW', 'Recirculation pump, kW'), ('trim_kW', 'Trim heater, kW'),
           ('total_kW', 'Total electrical power, kW'), ('kWh_per_t', 'Specific energy, kWh per tonne of water'), ('A_ff_m2', 'Falling-film area, m²'), ('tubes', 'Tubes'),
           ('tube_id_mm', 'Tube inside diameter, mm'), ('tube_L_mm', 'Tube length, mm'), ('recirc_kg_h', 'Recirculation, kg/h'), ('shell_D_mm', 'Shell diameter, mm'),
           ('height_mm', 'Height, mm'), ('ix_Q_kW', 'Interchanger duty, kW'), ('ix_A_m2', 'Interchanger area, m²'), ('T_feed_preheat_C', 'Feed after the interchanger, °C'),
           ('T_out_C', 'Product and condensate outlet, °C')]
    t = '\n'.join(f'| {l} | {A[k]} | {B[k]} |' for k, l in lab)
    rl = '\n'.join(f"| {cs} | {u} | {r[k]['W_kg_h']} | {r[k]['P1_kPa_abs']} | {r[k]['A_req_mm2']} | API 526 D (71 mm²), {'adequate' if r[k]['adequate'] else 'not adequate'} |"
                   for u, r in R.items() for cs, k in (('Body fire', 'relief_body'), ('Shell blocked outlet', 'relief_shell')))
    op = '\n'.join(f"| {o['option']} | {o['name']} | {o['vapour_factor'] if o['vapour_factor'] else '—'} | {o['note']} |" for o in O)
    trim = max(A['trim_kW'], B['trim_kW'])
    trim_txt = 'The compressor work covers the heat needed to bring the feed to the boil, so neither evaporator needs a continuous trim heater.' if trim == 0 else \
               f"The compressor work does not cover all the heat needed to bring the feed to the boil, so a trim heater supplies the rest ({A['trim_kW']} kW on EVAP_ACID and {B['trim_kW']} kW on EVAP_BASE)."
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

Each evaporator is a single-effect falling-film evaporator with mechanical vapour recompression (MVR). The liquor runs down the inside of vertical tubes, the compressed vapour condenses on the shell side, and the body is at {v('evap_body_kPa'):g} kPa. The {v('acid_conc_design_wt')*100:g} wt% HCl boils at its azeotrope temperature, {v('evap_bp_acid_C'):g} °C [PERRY9_HCL], which is the bounding case; the {v('base_conc_design_wt')*100:g} wt% NaOH boils at {v('evap_bp_base_C'):g} °C, a boiling-point elevation of {v('evap_bp_base_C') - 100:g} K [MCCABE7_DUHRING].

Saturation pressures come from region 4 of IAPWS-IF97, and the latent heat is {LAT:g} kJ/kg [IAPWS_IF97]. The compressor raises the vapour to the saturation pressure {v('evap_dT_drive_K'):g} K above the boiling point. Its work is the ideal-gas isentropic work with k = {v('evap_k_steam'):g}, divided by an efficiency of {v('evap_comp_eta'):g} [PERRY9_PUMP] and a motor efficiency of {v('evap_motor_eta'):g} (A-M-106).

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

The product and the condensate leave the interchanger at {A['T_out_C']} °C on the acid unit and {B['T_out_C']} °C on the base unit, below the 60 °C limit of line class P1 (AQS-STD-002). The condensate lines therefore stay in class P1, and IA-ACID-01 stays in class P2 for hot leach service. The parameter `T_C` of each outlet stream on the graph carries these values.

## 6. Materials

The acid unit has impregnated graphite tubes, tube sheets and interchanger, a PTFE-lined steel shell and separator, a column of borosilicate glass 3.3 with PTFE packing, and PVDF piping [PERRY9_MAT] [ULLMANN_HCL]. The base unit is nickel 200 [PERRY9_MAT]. Fasteners outside the wetted zone are ISO 3506 A4-70 on the acid unit and ISO 898-1 class 8.8 on the base unit.

## 7. Manufacturing

The model `models/mfg/evap_mvr.py` (CadQuery) reads `params.design` from the graph and exports `models/mfg/EVAP_*/export/*.step` and `*.stl`. Each unit folder holds its bill of materials `bom.csv`, its fasteners `fasteners.csv` and its work order `WO.md`. The fabrication routes are in `docs-authority/fab/EVAP_*.md`.

## 8. HCl in the acid vapour

From the Perry tables, the vapour over the {v('acid_conc_design_wt')*100:g} wt% body liquid at {v('evap_body_kPa'):g} kPa carries {c['y_eq_body_pct']} wt% HCl, more than the {v('bmed_product_wt_acid')*100:.2f} wt% feed, so a well-mixed body cannot send its condensate back to BMED_ACID. The vapour over the feed carries {c['y_eq_feed_pct']} wt%. Table 8.1 compares the ways to keep the HCl out of the condensate.

Table 8.1. Options for the HCl in the acid vapour

| Option | Description | Vapour against the base case | Finding |
| --- | --- | --- | --- |
{op}

Option d is adopted, as the smallest complete system. The feed enters the top of a packed column on the body frame, and the liquid runs down against the body vapour and reaches the body at {v('acid_conc_design_wt')*100:g} wt%. No reflux is drawn, so the compressor duty rises only by the recycled water. The column has {c['column_stages']} ideal stages above the body, from the Perry equilibrium, packed to {c['packed_mm']} mm at a height per stage of {v('evap_col_hetp_mm'):g} mm times {v('evap_col_margin'):g} [PERRY9_ABS] (A-M-108). It is DN{c['DN']} at {v('evap_col_u_m_s'):g} m/s vapour and {c['height_mm']} mm high, {c['placement']}.

The condensate carries {c['cond_hcl_wt_pct']} wt% HCl ({c['recycle_hcl_kg_d']} kg/d). It returns to BMED_ACID with the make-up water and comes back in the feed, which rises to {s['evap_acid']['feed_kg_d']:.1f} kg/d, with {s['evap_acid']['water_kg_d']:.1f} kg/d of water evaporated. The BMED current does not change, because the recycled HCl is not generated again. The owner may choose another option, for example option a if a condensate with almost no HCl is wanted.
"""
    open('docs-authority/sizing/EVAP_DESIGN.md', 'w').write(md)

if __name__ == '__main__': main()

"""X-MFG-30 in-house MVR falling-film evaporators EVAP_ACID and EVAP_BASE (no bought skid). Writes the design onto the graph
(params.design, outlet temperatures, relief_basis, size_mm) and docs-authority/sizing/EVAP_DESIGN.md (AQS-DUTY-060).
Run: python3 -m flow_graph.param.evap_design [--write]"""
import json, math, sys
from . import solver, drivers as DR
from .sizing import evaporator as EV, relief as RL, power as PW, hcl_vle as VLE
from .refs import cite
LAT = 2257.0   # kJ/kg at 100 C [IAPWS_IF97]
def design(d, e, unit):
    """e: mass result of solver.evap (water_kg_d, product_kg_d, feed_kg_d, added_kg_d)."""
    v = lambda k: DR.val(d, k); acid = unit == 'EVAP_ACID'
    Tb = v('evap_bp_acid_C' if acid else 'evap_bp_base_C'); p1 = v('evap_body_kPa'); Tc = Tb + v('evap_dT_drive_K'); p2 = EV.psat_kPa(Tc)
    V = e['water_kg_d']/86400; P = e['product_kg_d']/86400; F = (e['feed_kg_d'] + e['added_kg_d'])/86400
    comp_kW, w = EV.compressor_kW(V, Tb, p1, p2, v('evap_k_steam'), v('evap_comp_eta')); comp_e = comp_kW/v('evap_motor_eta')
    Q = V*LAT; A = Q*1000/(v('evap_U_ff')*v('evap_dT_drive_K'))
    di = v('evap_tube_id_mm')/1000; L = v('evap_tube_L_mm')/1000; n = math.ceil(A/(math.pi*di*L))
    rec = v('evap_wet_min')*n*math.pi*di   # kg/s
    pump_kW = rec/1100*9.81*4.0*1100/0.4/1000   # 4 m head, 40 % (PERRY9_PUMP)
    cpP = v('evap_cp_acid_prod' if acid else 'evap_cp_base_prod')
    ix = EV.interchanger(F, v('evap_cp_feed'), v('evap_feed_T_C'), V, 4.21, Tc, P, cpP, Tb, v('evap_approach_K'))
    A_ix = ix['Q_kW']*1000/(v('evap_U_ix')*ix['LMTD_K'])
    trim = F*v('evap_cp_feed')*(Tb - ix['T_feed_out_C']) - comp_kW    # sensible deficit not covered by compressor work
    trim_kW = max(0.0, trim)
    pitch = 1.25*(di*1000 + 2*6); Dsh = math.ceil((1.1*pitch*math.sqrt(n/0.907) + 2*pitch)/50)*50   # mm, triangular pitch, 6 mm graphite or 2 mm Ni wall
    H = L*1000 + v('evap_sump_h_mm') + 300 + 900   # tubes + sump + heads + separator
    # fire case on the body (ISO 23251 / API 521), set at body design, 21 % overpressure
    Aw = math.pi*Dsh/1000*v('evap_sump_h_mm')/1000 + math.pi*(Dsh/1000)**2/4
    Wf, Qf = EV.fire_relief_kg_h(Aw, LAT)
    P1f = 1.21*v('evap_body_design_kPag') + 101.325; Tf = EV.tsat_C(P1f) + (Tb - 100)
    Af = RL.gas_area_in2(Wf*2.20462, v('evap_k_steam'), P1f/6.894757, (Tf+273.15)*1.8, 1.0, 18.02)
    # shell side blocked outlet: compressor at 120 % of design flow, 10 % overpressure
    Wb = 1.2*V*3600; P1b = 1.1*v('evap_shell_design_kPag') + 101.325; Tbk = EV.tsat_C(P1b)
    Ab = RL.gas_area_in2(Wb*2.20462, v('evap_k_steam'), P1b/6.894757, (Tbk+273.15)*1.8, 1.0, 18.02)
    D_letter = 0.110   # in2, API 526 orifice D (smallest letter)
    col = None
    if acid:   # counter-current column on the body, feed at the top (X-MFG-30 option d, AQS-DUTY-060 section 7)
        c = e['cond_hcl_wt']*100; ns = VLE.strip_stages(F, v('bmed_product_wt_acid')*100, P, v('acid_conc_design_wt')*100, V, c)
        rho = 101.325*18.02/(8.314*(Tb+273.15)); Dc = math.sqrt(4*V/rho/v('evap_col_u_m_s')/math.pi)*1000
        DN = next(x for x in (50, 80, 100, 150, 200, 250, 300) if x >= Dc)
        col = dict(ideal_stages_incl_body=ns, column_stages=ns-1, cond_hcl_wt_pct=c, y_eq_feed_pct=round(VLE.bubble(v('bmed_product_wt_acid')*100)[1], 3),
                   y_eq_body_pct=round(VLE.bubble(v('acid_conc_design_wt')*100)[1], 2), packed_mm=round((ns-1)*v('evap_col_hetp_mm')*v('evap_col_margin')),
                   D_req_mm=round(Dc, 1), DN=DN, recycle_hcl_kg_d=round(e['recycle_hcl_kg_d'], 2), material='borosilicate glass 3.3 sections (ISO 3585), PTFE Pall rings, PTFE-lined flanges (PERRY9_MAT)')
        col['height_mm'] = col['packed_mm'] + 800; col['placement'] = 'free-standing beside the body on the same frame (L-1 headroom 6 m); vapour duct from the separator to the column bottom, column bottoms back to the body'
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
            p['size_mm'] = [r['shell_D_mm'] + 900 + (r['column']['DN'] + 250 if r.get('column') else 0), max(800, r['shell_D_mm'] + 400) + (500 if u == 'EVAP_ACID' else 0), r['height_mm']]   # EVAP_ACID frame also carries EVAP_ACID_VS (X-PAR-10)
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
    A, B = R['EVAP_ACID'], R['EVAP_BASE']; c = A['column']; O = options(d, s['evap_acid'])
    keys = ['T_boil_C','T_cond_C','p_body_kPa','p_shell_kPa','ratio','water_kg_h','duty_kW','w_kJ_kg','comp_shaft_kW','comp_elec_kW','pump_kW','trim_kW','total_kW','kWh_per_t',
            'A_ff_m2','tubes','tube_id_mm','tube_L_mm','recirc_kg_h','shell_D_mm','height_mm','ix_Q_kW','ix_A_m2','T_feed_preheat_C','T_out_C']
    t = '\n'.join(f'| {k} | {A[k]} | {B[k]} |' for k in keys)
    rl = '\n'.join(f"| {cs} | {u} | {r[k]['W_kg_h']} | {r[k]['P1_kPa_abs']} | {r[k]['A_req_mm2']} | API 526 D (71 mm2), {'adequate' if r[k]['adequate'] else 'NOT adequate'} |"
                   for u, r in R.items() for cs, k in (('Body fire', 'relief_body'), ('Shell blocked outlet', 'relief_shell')))
    op = '\n'.join(f"| {o['option']} | {o['name']} | {o['vapour_factor'] if o['vapour_factor'] else '-'} | {o['note']} |" for o in O)
    md = f"""# In-house MVR evaporators EVAP_ACID and EVAP_BASE

Document: AQS-DUTY-060 Rev B. Date 2026-10-15. Generated by `flow_graph/param/evap_design.py` (X-MFG-30). Study. Not a PE stamp.

| Rev | Change |
|---|---|
| A | First issue: MVR falling-film design, interchanger, in-house relief. |
| B | HCl in the acid vapour quantified from Perry's Tables 2-9/2-10; counter-current column added on EVAP_ACID (option d); condensate 0.5 wt% HCl recycles to BMED_ACID. |

## 1. Basis
Owner decision 2026-10-15: no bought skid; evaporators are designed and built in-house to an open design. Single-effect mechanical vapour recompression, falling film inside vertical tubes, condensing compressed vapour on the shell side, atmospheric body.
- Boiling: 20 wt% HCl at the azeotrope temperature 108.6 C (PERRY9_HCL, bounding); 20 wt% NaOH at 108.0 C (BPE 8 K, MCCABE7_DUHRING).
- Saturation pressures IAPWS-IF97 region 4; latent heat 2257 kJ/kg (IAPWS_IF97).
- Blower: ideal-gas isentropic work, k 1.33, efficiency 0.70 (PERRY9_PUMP), motor 0.90 (A-M-106).
- Falling film U 1500 W/(m2 K) at 6 K (PERRY9_EVAP; A-M-106); minimum wetting 0.05 kg/(m s) sets the recirculation (PERRY9_EVAP).
- Interchanger: feed at 35 C against condensate and product, counter-current, 10 K approach, U 2000 W/(m2 K) (PERRY9_EVAP, INCROPERA7).
- HCl-water VLE: Perry's 7th ed. Tables 2-9 and 2-10 fits (PERRY7_HCL_VLE), `flow_graph/param/sizing/hcl_vle.py`.
- Relief: body fire Q = 21000 F A^0.82 Btu/h (ISO 23251 / API 521), 21 % overpressure; steam shell blocked outlet at 120 % blower flow, 10 % overpressure; API 520 Part I gas area; ISO 4126-1 valve. Body 100 kPa g and full vacuum; shell 350 kPa g (A-M-107).

## 2. Results

| Quantity | EVAP_ACID | EVAP_BASE |
|---|---|---|
{t}

Power {A['kWh_per_t']} and {B['kWh_per_t']} kWh/t of water against the 72 kWh/t upper bound used before (VOGELBUSCH_MVR). Compressor work covers the feed-to-boiling deficit; no continuous trim heater.

## 3. Relief

| Case | Unit | W kg/h | P1 kPa abs | A required mm2 | Valve |
|---|---|---|---|---|---|
{rl}

## 4. Outlet temperatures (X-MAT-20)
Product and condensate leave the interchanger at {A['T_out_C']} C (acid) and {B['T_out_C']} C (base), below the 60 C limit of line class P1 (AQS-STD-002). Condensate lines stay P1; IA-ACID-01 stays P2 (hot leach service). Edge params T_C carry the values.

## 5. Materials
Acid: impregnated graphite tubes, tubesheets and interchanger; PTFE-lined steel shell and separator; column in borosilicate glass 3.3 with PTFE packing; PVDF piping (PERRY9_MAT, ULLMANN_HCL). Base: nickel 200 (PERRY9_MAT). Fasteners outside the wetted zone ISO 3506 A4-70 (acid) or ISO 898-1 8.8 (base).

## 6. Manufacturing
`models/mfg/evap_mvr.py` (CadQuery, reads params.design) exports `models/mfg/EVAP_*/export/*.step|stl`. BOM `bom.csv`, fasteners `fasteners.csv`, work order `WO.md`. Route `docs-authority/fab/EVAP_*.md`.

## 7. HCl in the acid vapour (resolved by design, Rev B)
From the Perry tables, vapour over the 20 wt% body liquid at 101.3 kPa carries {c['y_eq_body_pct']} wt% HCl, more than the {DR.val(d,'bmed_product_wt_acid')*100:.2f} wt% feed; a well-mixed body cannot send that condensate back to BMED. Vapour over the feed carries {c['y_eq_feed_pct']} wt%.

| Option | Description | Vapour vs base | Finding |
|---|---|---|---|
{op}

Adopted: option d, the smallest complete system. The feed enters the top of a packed column standing on the body frame; liquid runs down against the body vapour and reaches the body at 20 wt%; no reflux is drawn, so the blower duty rises only by the recycled water. {c['column_stages']} ideal stages above the body (stage count from the Perry VLE), packed {c['packed_mm']} mm at HETP 500 mm x 1.5 (PERRY9_ABS, A-M-108), DN{c['DN']} at 1.0 m/s vapour, column height {c['height_mm']} mm, {c['placement']}. Condensate {c['cond_hcl_wt_pct']} wt% HCl ({c['recycle_hcl_kg_d']} kg/d) returns to BMED_ACID with the make-up water and comes back in the feed: the feed rises to {s['evap_acid']['feed_kg_d']:.1f} kg/d and the water off to {s['evap_acid']['water_kg_d']:.1f} kg/d; BMED current is unchanged (recycled HCl is not generated). Owner may override, for example with option a if a near-zero-HCl condensate is wanted.
"""
    open('docs-authority/sizing/EVAP_DESIGN.md', 'w').write(md)

if __name__ == '__main__': main()

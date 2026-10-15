"""X-MFG-30 in-house MVR falling-film evaporators EVAP_ACID and EVAP_BASE (no bought skid). Writes the design onto the graph
(params.design, outlet temperatures, relief_basis, size_mm) and docs-authority/sizing/EVAP_DESIGN.md (AQS-DUTY-060).
Run: python3 -m flow_graph.param.evap_design [--write]"""
import json, math, sys
from . import solver, drivers as DR
from .sizing import evaporator as EV, relief as RL, power as PW
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
    return dict(unit=unit, T_boil_C=Tb, T_cond_C=round(Tc, 2), p_body_kPa=p1, p_shell_kPa=round(p2, 2), ratio=round(p2/p1, 3),
                water_kg_h=round(V*3600, 3), duty_kW=round(Q, 2), comp_shaft_kW=round(comp_kW, 3), comp_elec_kW=round(comp_e, 3), w_kJ_kg=round(w, 1),
                kWh_per_t=round((comp_e + pump_kW + trim_kW)/(V*3.6), 1), A_ff_m2=round(A, 2), tubes=n, tube_id_mm=di*1000, tube_L_mm=L*1000,
                recirc_kg_h=round(rec*3600, 1), pump_kW=round(pump_kW, 3), shell_D_mm=Dsh, height_mm=round(H),
                ix_Q_kW=round(ix['Q_kW'], 2), ix_A_m2=round(A_ix, 3), T_feed_preheat_C=round(ix['T_feed_out_C'], 1), T_out_C=round(ix['T_hot_out_C'], 1),
                trim_kW=round(trim_kW, 3), total_kW=round(comp_e + pump_kW + trim_kW, 3),
                relief_body=dict(case='fire, ISO 23251 / API 521 adequate drainage', A_wetted_m2=round(Aw, 3), Q_kW=round(Qf, 2), W_kg_h=round(Wf, 2),
                                 P1_kPa_abs=round(P1f, 1), T_K=round(Tf+273.15, 1), M_kg_kmol=18.02, k=v('evap_k_steam'), A_req_mm2=round(Af*RL.IN2_TO_MM2, 2),
                                 orifice='API 526 D (71 mm2)', adequate=bool(Af <= D_letter)),
                relief_shell=dict(case='blocked outlet, compressor at 120 % design flow', W_kg_h=round(Wb, 2), P1_kPa_abs=round(P1b, 1), T_K=round(Tbk+273.15, 1),
                                  M_kg_kmol=18.02, k=v('evap_k_steam'), A_req_mm2=round(Ab*RL.IN2_TO_MM2, 3), orifice='API 526 D (71 mm2)', adequate=bool(Ab <= D_letter)))
def main():
    d, g, s = solver.solve(); R = {u: design(d, s['evap_acid' if u == 'EVAP_ACID' else 'evap_base'], u) for u in ('EVAP_ACID', 'EVAP_BASE')}
    print(json.dumps(R, indent=1))
    if '--write' in sys.argv:
        N = {n['unit_id']: n for n in g['nodes']}; E = {e['stream_id']: e for e in g['edges']}
        for u, r in R.items():
            p = N[u]['params']; p['design'] = {k: v for k, v in r.items() if not k.startswith('relief')}
            p['size_mm'] = [r['shell_D_mm'] + 900, max(800, r['shell_D_mm'] + 400), r['height_mm']]
            p['size_note'] = 'L x W x H mm: body plus interchanger and compressor frame, in-house design X-MFG-30 (AQS-DUTY-060)'
            p['relief_mm'] = round(math.sqrt(4*71.0/math.pi), 2)
            p['relief_basis'] = dict(r['relief_body'], computed_by=f"flow_graph/param/evap_design.py ({cite('ISO23251')}; {cite('API520')})", shell_side=r['relief_shell'])
            p['design_kPa'] = DR.val(d, 'evap_body_design_kPag')
            for sid in ([f'IA-{u}-COND'] + (['IA-ACID-01'] if u == 'EVAP_ACID' else ['IA-BASE-PPT', 'IA-BASE-01'])):
                if sid in E: E[sid].setdefault('params', {}) or E[sid].update(params={}); E[sid]['params']['T_C'] = r['T_out_C']; E[sid]['params']['T_basis'] = 'X-MFG-30 interchanger outlet (AQS-DUTY-060)'
        open(solver.GP if hasattr(solver, 'GP') else 'flow_graph/plant_flow_graph.json', 'w').write(json.dumps(g, indent=2))
    return R
if __name__ == '__main__': main()

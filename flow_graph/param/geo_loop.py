"""Unit task 02 for the GEO loop (AQS-DUTY-076): GEO_GHEX (shallow closed ground loop),
GEO_HP (the only ladder lift, 2 x 100 % per X-RED-07) and GEO_HP_CLOSED_LOOP (the source
circulation). Design case = the survey-locked GHEX ceiling (3.0 kW_th at k_ground 1.5 W/m K,
T_source 285 K - graph params, ST-ORC-01 survey hold) and the issued winter lift duty on the
graph (S44 to Q4_BUS). Bore metres from the cited per-metre sustained capacity band
(KAVANAUGH2014: 30-50 W/m for small closed loops; 35 W/m used, registered); U-tube count,
bore spacing (6 m, registered) and 25 % propylene-glycol loop flow at dT 3 K (registered);
heat pump at the plant COP basis (graph S44 2.1952 kW_th / SF-GEO_HP 0.686 kW_e = COP 3.2;
study COP 3.43 at 285 K, AQS-HEAT-STUDY-002 sec. 6); brazed-plate source and condenser areas
at U 2.0 kW/m2 K (PERRY9 sec. 11 plate class) and 5 K approach. No rates change on the graph.
Run: python3 -m flow_graph.param.geo_loop [--write]"""
import json, math, os, sys
from . import drivers as DR
from .refs import cite

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GP = os.path.join(ROOT, 'flow_graph/plant_flow_graph.json')
DOC = 'AQS-DUTY-076'
TAG = f'GEO loop sizing (flow_graph/param/geo_loop.py, {DOC})'
GL = 'GEO.geo-loop.'                 # U4b: sizing literals single-sourced from drivers.json


def design(d, g):
    v = lambda k: DR.val(d, k)
    N = {n['unit_id']: n for n in g['nodes']}; E = {e['stream_id']: e for e in g['edges']}
    ev = lambda sid: float((E.get(sid) or {}).get('rate', {}).get('value') or 0)
    q_ghex = (N['GEO_GHEX'].get('params') or {}).get('Q_GHEX_avail_kW_th', 3.0)     # survey-locked ceiling, graph
    q_lift, p_el = ev('S44'), ev('SF-GEO_HP')                                       # issued winter duty, graph
    if not p_el: p_el = q_lift / v(GL + 'geo_hp_cop_design')
    cop = q_lift / p_el if p_el else v(GL + 'geo_hp_cop_design')
    # ---- GEO_GHEX: shallow closed bore field at the survey-locked ceiling ---------------------
    qm_w_m = v(GL + 'ghex_q_per_m_W')                                               # sustained per-metre capacity (registered)
    bore_m = q_ghex * 1000.0 / qm_w_m
    n_bore = max(2, math.ceil(bore_m / v(GL + 'ghex_bore_depth_m')))
    depth = math.ceil(bore_m / n_bore / 5.0) * 5                                    # even split, 5 m rounding
    m_total = n_bore * depth
    hdr_m = (n_bore - 1) * v(GL + 'ghex_bore_spacing_m')
    cp_g = v(GL + 'glycol_cp_kJ_kgK') * 1000.0; rho_g = v(GL + 'glycol_rho_kg_m3')
    m_loop = q_ghex * 1000.0 / (cp_g * v(GL + 'glycol_dT_K'))                       # kg/s at the ceiling
    Q_loop = m_loop / rho_g
    id_req = math.sqrt(4 * Q_loop / (math.pi * v(GL + 'glycol_v_m_s'))) * 1000
    dn = next(dn for dn in (25, 32, 40, 50, 65, 80) if dn - 8 >= id_req)
    pump_w = rho_g * 9.81 * Q_loop * v(GL + 'loop_head_m') / v(GL + 'loop_pump_eff')
    ghex = dict(Q_ceiling_kW_th=q_ghex, k_ground_W_mK=(N['GEO_GHEX'].get('params') or {}).get('k_ground_W_mK', 1.5),
                T_source_K=(N['GEO_GHEX'].get('params') or {}).get('T_source_K', 285.0), q_per_m_W=qm_w_m,
                bore_metres_req=round(bore_m, 1), bores=n_bore, bore_depth_m=depth, bore_metres_installed=m_total,
                bore_spacing_m=v(GL + 'ghex_bore_spacing_m'), header_m=round(hdr_m, 1),
                loop_DN=dn, loop_flow_kg_s=round(m_loop, 4), loop_dT_K=v(GL + 'glycol_dT_K'),
                loop_fluid=f"{v(GL+'glycol_vol_pct')} % propylene glycol",
                circ_pump_W=round(pump_w, 1), status='design_survey_locked (ST-ORC-01)',
                material='HDPE DR-11 U-tubes, 1 in bore + horizontal runs; borehole grout thermal')
    # ---- GEO_HP: 2 x 100 % lift at the issued winter duty ------------------------------------
    q_mod = max(q_lift, v(GL + 'geo_hp_module_min_kW'))
    a_src = q_mod / (v(GL + 'bp_ux_U_kW_m2K') * v(GL + 'bp_ux_dT_K'))
    a_cond = (q_mod + p_el) / (v(GL + 'bp_ux_U_kW_m2K') * v(GL + 'bp_ux_dT_K'))     # condenser rejects Q + W
    hp = dict(lift_kW_th=round(q_lift, 4), electric_kW=round(p_el, 4), cop=round(cop, 2),
              modules=2, redundancy='2 x 100 % (X-RED-07)', module_kW_th=round(q_mod, 3),
              source_area_m2=round(a_src, 3), condenser_area_m2=round(a_cond, 3),
              hx_class=f'brazed plate, U {v(GL+"bp_ux_U_kW_m2K")} kW/m2 K at {v(GL+"bp_ux_dT_K")} K approach ({cite("PERRY9")})',
              cop_basis=f'graph S44/SF-GEO_HP; study COP 3.43 at 285 K (AQS-HEAT-STUDY-002 sec. 6, {cite("KAVANAUGH2014")})',
              material='316L plates, R410A-class refrigerant, propylene-glycol brine source')
    # ---- GEO_HP_CLOSED_LOOP: the source circulation between GHEX and GEO_HP ------------------
    closed = dict(design_case_kW_th=q_ghex, flow_kg_s=round(m_loop, 4), DN=dn, dT_K=v(GL + 'glycol_dT_K'),
                  head_m=v(GL + 'loop_head_m'), pump_W=round(pump_w, 1),
                  duty='source loop between the bore field and the heat-pump evaporators; S43 carries it on the graph (0 kW idle standby)',
                  material='HDPE DR-11 buried; 25 % propylene glycol (freeze protection to -10 C)')
    return {'GEO_GHEX': ghex, 'GEO_HP': hp, 'GEO_HP_CLOSED_LOOP': closed}


def write(g, R):
    N = {n['unit_id']: n for n in g['nodes']}
    for u, r in R.items():
        p = N[u].setdefault('params', {})
        p['design'] = {k: (round(x, 4) if isinstance(x, float) else x) for k, x in r.items()}
        p['size_note'] = f'sized at the survey-locked design case, {TAG}'
    open(GP, 'w').write(json.dumps(g, indent=2))


def write_doc(d, R):
    v = lambda k: DR.val(d, k)
    gh, hp, cl = R['GEO_GHEX'], R['GEO_HP'], R['GEO_HP_CLOSED_LOOP']
    md = ['# GEO loop sizing', '', f'Document number: {DOC}', 'Revision: A', 'Date: 2026-10-20',
          'Authority: AQS-PLAN-007 unit tasks (GEO)-02; AQS-HEAT-STUDY-002 (AQS-HEAT-STUDY-002 sec. 6 GHEX ceiling; D-GEO_ORC keeps GEO_ORC at 0 kW_e). '
          'Generated by `flow_graph/param/geo_loop.py`. Study. Not a PE stamp. Survey values stay locked (ST-ORC-01).', '',
          'Unit task 02 for the three GEO units. Design case: the survey-locked GHEX ceiling '
          f'{gh["Q_ceiling_kW_th"]} kW_th (k_ground {gh["k_ground_W_mK"]} W/m K, T_source {gh["T_source_K"]} K, graph params) and the issued winter '
          f'lift {hp["lift_kW_th"]} kW_th on S44. Bore metres = ceiling / {gh["q_per_m_W"]} W per metre sustained capacity '
          f'({cite("KAVANAUGH2014")} small closed-loop band 30-50 W/m; 35 W/m used, registered), split {gh["bores"]} x {gh["bore_depth_m"]} m bores at '
          f'{gh["bore_spacing_m"]} m spacing; loop flow {gh["loop_flow_kg_s"]} kg/s of {gh["loop_fluid"]} at a {gh["loop_dT_K"]} K rise (registered), '
          f'DN{gh["loop_DN"]} at {v(GL+"glycol_v_m_s")} m/s, circulation {gh["circ_pump_W"]} W at {gh["header_m"]:.0f} m header + bore circuit head '
          f'{v(GL+"loop_head_m")} m. Heat pump {hp["modules"]} x 100 % (X-RED-07) at COP {hp["cop"]} (graph S44 / SF-GEO_HP; study 3.43 at 285 K), '
          f'brazed-plate areas {hp["source_area_m2"]} m2 source / {hp["condenser_area_m2"]} m2 condenser.', '',
          '| Unit | Design case | Sized result | Material | Notes |', '|---|---|---|---|---|',
          f"| GEO_GHEX | {gh['Q_ceiling_kW_th']} kW_th ceiling, survey-locked | {gh['bores']} bores x {gh['bore_depth_m']} m = {gh['bore_metres_installed']} m "
          f"({gh['bore_metres_req']} m required), DN{gh['loop_DN']} loop, {gh['circ_pump_W']} W circulation | {gh['material']} | recharge branch 0.7 kW normal, "
          f"3.0 kW hard ceiling (AQS-HEAT-STUDY-002 sec. 10.7) |",
          f"| GEO_HP | {hp['lift_kW_th']} kW_th winter lift at COP {hp['cop']} | {hp['modules']} x 100 % modules at {hp['module_kW_th']} kW_th; plates "
          f"{hp['source_area_m2']} + {hp['condenser_area_m2']} m2 | {hp['material']} | {hp['cop_basis']} |",
          f"| GEO_HP_CLOSED_LOOP | {cl['design_case_kW_th']} kW_th source loop | {cl['flow_kg_s']} kg/s, DN{cl['DN']}, {cl['dT_K']} K rise, "
          f"{cl['pump_W']} W at {cl['head_m']} m | {cl['material']} | {cl['duty']} |", '',
          f'The bore count is a design-output at the locked survey values; the thermal response test (ST-ORC-01 blockers) can raise the per-metre '
          f'capacity and cut metres - that is the registered sensitivity. Winter extraction and summer recharge stay inside the ceiling so the field '
          f'does not warm into the GEO_HP source degradation case (AQS-HEAT-STUDY-002 sec. 6). Open: none for task 02 at the survey-locked basis; '
          f'the survey confirmation is the registered replacing test.']
    open(os.path.join(ROOT, 'docs-authority/sizing/GEO_LOOP.md'), 'w').write('\n'.join(md) + '\n')


def main():
    d = DR.load(); g = json.load(open(GP)); R = design(d, g)
    for u, r in R.items(): print(u, json.dumps(r)[:200])
    if '--write' in sys.argv: write(g, R); write_doc(d, R)


if __name__ == '__main__':
    main()

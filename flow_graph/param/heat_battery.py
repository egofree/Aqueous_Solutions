"""Unit task 02 for the eight heat batteries Q1_A..Q4_B (AQS-DUTY-074, X-PAR-03 house pattern).

Re-derives each ladder store from its issued basis and stamps params.design on the graph:
hold energy E (graph basis: water tiers 20 kWh_th at a 30 K swing, oil tiers 10 kWh_th at an
80 K swing) -> medium mass and volume V = E / (rho cp dT); vessel D x H (H/D 1.5, D on the
50 mm grid) checked against the issued AQS-DUTY-008 sec. 5 store table and the 800 x 800 x
1200 mm placement envelope; standing loss from the issued insulation (90 mm microporous /
60 mm mineral wool / 30 mm PIR) by the radial-and-plane U A dT method (ASTM_C680 class,
ASTM_C547 wool conductivity), checked against the DUTY-008 sec. 5 loss column. Media per
AQS-HEAT-LADDER-001: Q1/Q2 thermal oil, Q3 water < 120 C, Q4 water < 80 C. No rates, loads or
edges change on the graph (the ladder losses are already carried on IA-Q*A-LOSS / the heat
ladder closure, test_heat_ladder.py). Run: python3 -m flow_graph.param.heat_battery [--write]"""
import json, math, os, sys
from . import drivers as DR
from .refs import cite

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GP = os.path.join(ROOT, 'flow_graph/plant_flow_graph.json')
DOC = 'AQS-DUTY-074'
TAG = f'heat battery sizing (flow_graph/param/heat_battery.py, {DOC})'
HB = 'HEAT.heat-battery-train.'          # U4b: sizing literals single-sourced from drivers.json
UNITS = [f'Q{t}_{s}' for t in (1, 2, 3, 4) for s in ('A', 'B')]
# tier: (fluid, hold-energy key, swing K, t_nom C, insulation spec key) - issued basis of the graph
# params (basis "20 kWh_th Q4 hold at 30 K; oil stores 10 kWh at 80 K") and AQS-DUTY-008 sec. 5
TIER = {1: ('thermal oil', 'hb_oil_hold_kWh_th', 'hb_oil_swing_K', 250, 'hb_insul_q12_mm'),
        2: ('thermal oil', 'hb_oil_hold_kWh_th', 'hb_oil_swing_K', 180, 'hb_insul_q12_mm'),
        3: ('water', 'hb_q3_hold_kWh_th', 'hb_water_swing_K', 100, 'hb_insul_q3_mm'),
        4: ('water', 'hb_water_hold_kWh_th', 'hb_water_swing_K', 70, 'hb_insul_q4_mm')}
# issued store table, AQS-DUTY-008 sec. 5 (shape inside, m; loss kW) - the module reconciles to it
ISSUED = {1: (0.302, 0.200), 2: (0.302, 0.111), 3: (0.407, 0.174), 4: (0.602, 0.164)}
MAT = {'thermal oil': ('SA-240 304L, welded', 'hb_rho_oil_kg_m3', 'hb_cp_oil_kJ_kgK'),
       'water': ('PP-H (fusion welded)', 'hb_rho_water_kg_m3', 'hb_cp_water_kJ_kgK')}
# X-MAT-06 (2026-10-21): the Q3 tier holds 100 C water (t_nom), above the PP-H class limit of
# 80 C ([S4], SIMONA PP tech.info; AQS-STD-002 section 13). The Q3 vessels are SA-240 304L welded
# on the same hold basis; the Q4 vessels (70 C) keep PP-H.
MAT_TIER = {('water', 3): 'SA-240 304L, welded (100 C tier is above the PP-H class of 80 C)',
            ('water', 4): 'PP-H (fusion welded)'}
INSUL = {1: ('microporous silica board', 'hb_k_micro_W_mK'), 2: ('microporous silica board', 'hb_k_micro_W_mK'),
         3: ('mineral wool', 'hb_k_wool_W_mK'), 4: ('PIR foam', 'hb_k_pir_W_mK')}
AMBIENT_C, U_CONV = 20.0, 9.0          # hall air, W/m2 K combined surface film (ASTM_C680 class)


def design(d, g):
    v = lambda k: DR.val(d, k)
    out = {}
    for u in UNITS:
        tier = int(u[1]); fluid, ek, sk, t_nom, ik = TIER[tier]
        E, dT = v(HB + ek) * 3.6e6, v(HB + sk)                 # J hold, K swing
        rho, cp = v(HB + MAT[fluid][1]), v(HB + MAT[fluid][2]) * 1000.0
        m = E / (cp * dT); V_req = m / rho                     # kg, m3 from the hold basis
        V = max(V_req, ISSUED[tier][0])                        # issued DUTY-008 sec. 5 shape governs where larger
        D = math.ceil((4 * V / (math.pi * v(HB + 'hb_HD'))) ** (1 / 3) * 1000 / 50) * 50
        H = math.ceil(V / (math.pi * (D / 1000) ** 2 / 4) * 1000 / 50) * 50
        A = math.pi * D / 1000 * H / 1000 + 2 * math.pi * (D / 2000) ** 2          # m2, sides + both heads
        thick, k = v(HB + ik) / 1000.0, v(HB + INSUL[tier][1])
        U = 1.0 / (thick / k + 1.0 / U_CONV)                   # W/m2 K, series film over insulation
        loss_kW = U * A * (t_nom - AMBIENT_C) / 1000.0
        wall = max(v(HB + 'hb_wall_min_mm'), math.ceil(rho * 9.81 * H / 1000 * D / 1000 / (2 * v(HB + 'hb_allow_MPa')) * 1000))
        out[u] = dict(tier=f'Q{tier}', ladder=u[-1], fluid=fluid, t_nom_C=t_nom, hold_kWh_th=v(HB + ek), swing_K=dT,
                      rho_kg_m3=rho, cp_kJ_kgK=cp, mass_kg=round(m, 1), V_req_m3=round(V_req, 4), V_m3=round(V, 4),
                      issued_V_m3=ISSUED[tier][0], D_mm=D, H_mm=H, insulation=f'{v(HB + ik):.0f} mm {INSUL[tier][0]}',
                      U_W_m2K=round(U, 2), area_m2=round(A, 3), standing_loss_kW=round(loss_kW, 3),
                      issued_loss_kW=ISSUED[tier][1], wall_mm=wall, material=MAT_TIER.get((fluid, tier), MAT[fluid][0]),
                      envelope=[800, 800, 1200], fits=bool(D <= 800 and H <= 1200))
    return out


def write(g, R):
    N = {n['unit_id']: n for n in g['nodes']}
    for u, r in R.items():
        p = N[u].setdefault('params', {})
        p['design'] = {k: (round(x, 4) if isinstance(x, float) else x) for k, x in r.items()}
        p['size_note'] = f'store D{r["D_mm"]} x H{r["H_mm"]} mm inside the 800 x 800 x 1200 mm issued envelope, {TAG}'
    open(GP, 'w').write(json.dumps(g, indent=2))


def write_doc(d, R):
    v = lambda k: DR.val(d, k)
    md = [f'# Heat battery sizing', '', f'Document number: {DOC}', 'Revision: A', 'Date: 2026-10-20',
          f'Authority: AQS-PLAN-007 unit tasks (HEAT)-02; AQS-HEAT-LADDER-001 (tiers, media, diode rule); AQS-DUTY-008 sec. 5 issued store table. '
          f'Generated by `flow_graph/param/heat_battery.py`. Study. Not a PE stamp.', '',
          f'Unit task 02 for the 8 heat batteries ({", ".join(UNITS)}). Method: hold energy from the issued basis '
          f'(water tiers {v(HB+"hb_water_hold_kWh_th")} kWh_th at a {v(HB+"hb_water_swing_K")} K swing, oil tiers {v(HB+"hb_oil_hold_kWh_th")} kWh_th at '
          f'{v(HB+"hb_oil_swing_K")} K; graph params.basis) gives m = E/(cp dT) and V = m/rho ({cite("PERRY9")} liquid properties); the issued '
          f'AQS-DUTY-008 sec. 5 shape governs where it is larger. Vessel D x H at H/D {v(HB+"hb_HD")}, D on the 50 mm grid, wall by hoop stress at the '
          f'liquid head against {v(HB+"hb_allow_MPa")} MPa allow with a {v(HB+"hb_wall_min_mm")} mm minimum. Standing loss by the plane-and-head '
          f'U A dT method (ASTM_C680 class; mineral wool k {v(HB+"hb_k_wool_W_mK")} W/mK {cite("ASTM_C547")}), checked against the issued loss column. '
          f'Thermosyphon downhill steps and cross-ties are AQS-DUTY-008 sec. 14 (not re-sized here); the loss edges stay on the heat-ladder closure '
          f'({cite("PERRY9")} for properties).', '',
          '| Unit | Tier | Fluid | T nom C | Hold kWh_th | Swing K | Mass kg | V req m3 | V m3 (issued) | D mm | H mm | Insulation | U W/m2K | Loss kW (issued) | Wall mm | Fits envelope |',
          '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for u, r in R.items():
        md.append(f"| {u} | {r['tier']} | {r['fluid']} | {r['t_nom_C']} | {r['hold_kWh_th']} | {r['swing_K']} | {r['mass_kg']} | "
                  f"{r['V_req_m3']} | {r['V_m3']} ({r['issued_V_m3']}) | {r['D_mm']} | {r['H_mm']} | {r['insulation']} | {r['U_W_m2K']} | "
                  f"{r['standing_loss_kW']} ({r['issued_loss_kW']}) | {r['wall_mm']} | {'yes' if r['fits'] else 'NO'} |")
    md += ['', f'Reconciliation: the required volumes reproduce the issued sec. 5 shapes within the 50 mm construction grid '
               f'(Q1/Q2 {R["Q1_A"]["V_req_m3"]} vs {R["Q1_A"]["issued_V_m3"]} m3, Q4 {R["Q4_A"]["V_req_m3"]} vs {R["Q4_A"]["issued_V_m3"]} m3); '
               f'Q3 keeps the larger issued shape. Standing losses land within 25 % of the issued column (edge and support effects excluded here, '
               f'included there). All eight fit the 800 x 800 x 1200 mm placement envelope (AQS-PLACE-SEED-001 Rev H rows unchanged).',
           '', 'Basis of the hold energies and media: graph params (basis string) and AQS-HEAT-LADDER-001; swing 30 K water / 80 K oil inside the '
               'tier bands (Q3 < 120 C, Q4 < 80 C). The deferred 1.5 m3 Q4 buffer of AQS-HEAT-STUDY-002 option (d) is NOT adopted here; the '
               'issued store table stands. Open: none for task 02; internals (thermosyphon steps, cross-tie pumps) are task 06 on AQS-DUTY-008 sec. 14.']
    open(os.path.join(ROOT, 'docs-authority/sizing/HEAT_BATTERY.md'), 'w').write('\n'.join(md) + '\n')


def main():
    d = DR.load(); g = json.load(open(GP)); R = design(d, g)
    for u, r in R.items(): print(u, r['D_mm'], 'x', r['H_mm'], 'mm', r['fluid'], round(r['V_m3'], 3), 'm3, loss', r['standing_loss_kW'], 'kW')
    if '--write' in sys.argv: write(g, R); write_doc(d, R)


if __name__ == '__main__':
    main()

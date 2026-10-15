"""AQS-DUTY-049 polymer exchanger sizing for HX-5 and HX8. Graph values; assumptions labeled."""
import json, math
g = json.load(open('flow_graph/plant_flow_graph.json'))
E = {e['stream_id']: e for e in g['edges']}; N = {n['unit_id']: n for n in g['nodes']}
K_PVDF = 0.17      # W/mK, low end of Kynar 740 TDS 0.17-0.19 (ASTM D433)
K_GLASS = 1.2      # W/mK, borosilicate 3.3 (ISO 3585 typical) -- published typical value
R_FOUL = 0.0002    # m2K/W per side total, assumption
def water(T):      # saturated liquid water, steam-table values (assumption: liquor and treated water taken as water)
    tab = {50:(988.0,5.47e-4,0.644,3.55),55:(985.7,5.04e-4,0.649,3.25),90:(965.3,3.15e-4,0.675,1.96)}
    return tab[min(tab, key=lambda t: abs(t-T))]
def h_tube(m, n, di, T):
    rho, mu, k, Pr = water(T); A = n*math.pi*di**2/4; v = m/(rho*A); Re = rho*v*di/mu
    return 0.023*Re**0.8*Pr**0.4*k/di, v, Re
def lmtd(a, b): return (a-b)/math.log(a/b) if abs(a-b) > 1e-9 else a
out = {}
# HX-5: Q3 water in coil, leach liquor outside
e = E['HL-Q3-A-HX5']['params']; Q = E['HL-Q3-A-HX5']['rate']['value']*1e3
TL = N['LEACH_CSTR_1']['params']['liquor_T_C']['value']
dT = lmtd(e['supply_C']-TL, e['return_C']-TL)
do, t = 0.025, 0.0019          # PVDF tube 25 x 1.9 mm, assumption
hi, v, Re = h_tube(e['m_kg_s'], 1, do-2*t, 90)
for ho_lbl, ho in (('natural convection 300 (assumption)', 300.0), ('agitated 1000 (assumption)', 1000.0)):
    for mat, k, tw in (('PVDF', K_PVDF, t), ('borosilicate 3.3, 3 mm wall', K_GLASS, 0.003)):
        U = 1/(1/hi + tw/k + 1/ho + R_FOUL); A = Q/(U*dT)
        out[f'HX-5 {mat}, outside {ho_lbl}'] = dict(Q_W=Q, LMTD_K=round(dT,2), h_in=round(hi), U=round(U,1), A_m2=round(A,2), tube_m=round(A/(math.pi*do),1))
# HX8: liquor in PVDF tubes, Q4 water on shell
p = N['HX8']['params']; Q8 = p['duty_kw']*1e3; m = E['IA-HX8']['params']['liquor_kg_h']/3600
dT8 = lmtd(p['liquor_in_C']-p['water_out_C'], p['liquor_out_C']-p['water_in_C'])
do8, t8, n8 = 0.016, 0.0015, 3  # PVDF 16 x 1.5 mm, 3 tubes per pass, assumption
hi8, v8, Re8 = h_tube(m, n8, do8-2*t8, 53)
ho8 = 1500.0                    # shell-side treated water, assumption
for mat, k, tw in (('PVDF', K_PVDF, t8), ('impregnated graphite (k ~ 100, assumption)', 100.0, 0.005)):
    U = 1/(1/hi8 + tw/k + 1/ho8 + R_FOUL); A = Q8/(U*dT8)
    out[f'HX8 {mat}'] = dict(Q_W=Q8, LMTD_K=round(dT8,2), v_m_s=round(v8,2), Re=round(Re8), h_in=round(hi8), U=round(U,1), A_m2=round(A,2), graph_area_m2=p.get('area_m2'))
print(json.dumps(out, indent=1))

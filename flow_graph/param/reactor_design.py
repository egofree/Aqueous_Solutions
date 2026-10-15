"""X-MFG-31 in-house reaction chambers (no bought skid): GLASS_DIGEST, DIGESTER, OIL_PYRO. LEACH_CSTR_1 is designed in AQS-DUTY-050
(models/mfg/LEACH_CSTR_1). Standard agitated cylinder H = T, impeller T/3 [PERRY9_MIX]; working volume = feed/rho x residence; vessel =
working / fill. Residence: GLASS_DIGEST from the zero-order alkaline dissolution rate [JMS2017_GLASSFIBRE] with the shrinking-sphere
conversion of the dissolved fraction, floored at a practical minimum; DIGESTER from the mesophilic SRT [METCALF5]; OIL_PYRO from the slow
pyrolysis residence at temperature [ANUAR2016]. Walls: thermoplastic hoop stress from hydrostatic head [DVS2205]; steel minimum
thickness UG-16(b) plus corrosion allowance [ASME_VIII1_UG16]. Heat: OIL_PYRO sensible + heat of pyrolysis [GAO2010] / heater efficiency.
Writes params.design and size_mm on the graph, continuous_kw for OIL_PYRO and the agitator duties, and docs-authority/sizing/REACTOR_DESIGN.md
(AQS-DUTY-062). Run: python3 -m flow_graph.param.reactor_design [--write]"""
import json, math, os, sys
from . import drivers as DR
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GP = os.path.join(ROOT, 'flow_graph/plant_flow_graph.json')
DN = (25, 32, 40, 50, 65, 80, 100, 125, 150, 200, 250, 300, 350, 400, 450, 500, 600, 700, 800, 900, 1000, 1200)

def vessel(V_work, fill, rho, sigma_MPa=None, t_min=3.0, CA=0.0, steel=False):
    V = V_work/fill; T = (4*V/math.pi)**(1/3); H = T
    Dn = next((x for x in DN if x/1000 >= T), DN[-1]); T = Dn/1000; H = 4*V/(math.pi*T**2); H = max(H, T*0.8)
    if steel: t = max(t_min, 1.5) + CA
    else: t = max(t_min, rho*9.81*H*fill*T/(2*sigma_MPa*1e6)*1000)
    return dict(V_work_L=V_work*1000, V_L=V*1000, D_mm=Dn, H_mm=math.ceil(H*1000/10)*10, wall_mm=math.ceil(t*2)/2)

def agitator(D_tank_m, rho, tip, Np):
    Di = D_tank_m/3; N = tip/(math.pi*Di); P = Np*rho*N**3*Di**5
    return dict(D_imp_mm=round(Di*1000), rpm=round(N*60), shaft_W=P, motor_kW=next(x for x in (0.09, 0.12, 0.18, 0.25, 0.37, 0.55, 0.75, 1.1) if x*1000 >= P/0.6))

def design(d, g):
    v = lambda k: DR.val(d, k); E = {e['stream_id']: e for e in g['edges']}
    R = lambda sid: E[sid]['rate']['value'] if sid in E else 0.0
    inflow = lambda u: sum(e['rate']['value'] for e in g['edges'] if e['to_unit_id'] == u and e['rate'].get('unit') == 'kg/d')
    out = {}
    # GLASS_DIGEST: dissolved fraction X of the cullet; shrinking sphere 1-(1-delta/r)^3 = X; recession rate k/rho_glass
    m_in = R('IA-GLASS-03'); X = max(0.0, (m_in - R('S08G'))/m_in) if m_in else 0.0
    r0 = v('rx_glass_d_um')/2e6; delta = r0*(1 - (1 - X)**(1/3))
    k = v('rx_glass_k0_g_m2_s')*(DR.val(d, 'bmed_product_molarity')/3.0)**0.31     # 2 M basis, order 0.31; 20 wt% NaOH is about 6 M (bounding low)
    t_kin_h = delta/(k/1000/2500)/3600; tau = max(3*t_kin_h, v('rx_glass_tau_min_h'))
    rho = 1300.0; Vw = inflow('GLASS_DIGEST')/rho*tau/24
    ves = vessel(Vw, v('rx_fill'), rho, sigma_MPa=3.0, t_min=4.0); ag = agitator(ves['D_mm']/1000, rho, v('rx_tip_m_s'), v('rx_Np_pbt'))
    out['GLASS_DIGEST'] = dict(X=X, delta_um=delta*1e6, t_kin_h=t_kin_h, tau_h=tau, **ves, agitator=ag, T_C=85, material='CPVC (to 93 C; DVS 2205 allowable 3.0 MPa at 85 C); PVDF impeller and shaft sleeve',
                               heat='Q3 coil HX-6 (graph HL-Q3-A/B-HX6)', kW=ag['motor_kW'])
    # DIGESTER: mesophilic SRT on the whole wet feed
    Vw = inflow('DIGESTER')/1000*v('rx_digester_srt_d')
    ves = vessel(Vw, 0.8, 1000.0, sigma_MPa=5.0, t_min=4.0)
    A = math.pi*ves['D_mm']/1000*ves['H_mm']/1000 + math.pi*(ves['D_mm']/1000)**2/2
    loss_W = 0.5*A*15.0; feed_W = inflow('DIGESTER')*4.18*15/86.4
    out['DIGESTER'] = dict(srt_d=v('rx_digester_srt_d'), **ves, T_C=35, heat_W=loss_W + feed_W, mixer='biogas recirculation through the base (no shaft seal)',
                           material='HDPE (PE100) shell, 50 mm PIR insulation (U about 0.5 W/(m2 K))', kW=round((loss_W + feed_W)/1000 + 0.02, 3))
    # OIL_PYRO: retort at temperature; heat
    m = inflow('OIL_PYRO'); Vw = m/850.0*v('rx_pyro_tau_h')/24
    ves = vessel(Vw, 0.5, 850.0, t_min=3.0, CA=1.5, steel=True)     # half full: foaming and char
    Q_kW = m*(v('rx_pyro_cp_kJ_kgK')*(v('rx_pyro_T_C') - 25)/1000 + v('rx_pyro_dH_MJ_kg'))/86.4
    out['OIL_PYRO'] = dict(T_C=v('rx_pyro_T_C'), tau_h=v('rx_pyro_tau_h'), **ves, Q_process_kW=Q_kW, kW=Q_kW/v('rx_pyro_heater_eff'),
                           material='ASME SA-240 304H (carbon steel limited to 425 C, ASME II-D); ceramic-fibre insulation; band heaters', relief='vapour line to OIL_FRAC open; bursting disc on the retort lid to the flare header (study)')
    # MEOH_SYNTH (A-M-156): cooled fixed-bed tube(s) of Cu/ZnO/Al2O3; catalyst from the CO2-only weight-time yield [CTC2020_CZA] / margin;
    # shell UG-27 [ASME_VIII1_UG27] on SA-106 B [ASME_II_D] + 1.5 mm CA; exotherm 49.5 kJ/mol to the jacket; feed preheat on the bus.
    E_ = lambda sid: E[sid]['rate']['value'] if sid in E else 0.0
    m_me = E_('S75')/24; cat = m_me/(v('meoh_wty_kg_kgcat_h')/v('meoh_wty_margin')); Vb = cat/v('meoh_cat_bulk_kg_L')/1000
    ID, OD, t_nom = 52.5, 60.3, 3.91                      # DN50 Sch 40 (ASME B36.10M)
    A = math.pi*(ID/1000)**2/4; L1 = 2.0; ntube = max(1, math.ceil(Vb/A/L1)); L = Vb/A/ntube
    Pd = 50.0*v('press_design_margin')/10                  # MPa
    t_req = Pd*(OD/2)/(v('meoh_S_MPa')*1.0 + 0.4*Pd) + 1.5   # UG-27 in outside-radius form (Appendix 1-1) + CA
    q_kW = m_me/32.042*1000*v('meoh_dH_kJ_mol')/3.6e6*1000
    pre_kW = (E_('S74')*14.3 + E_('S73')*0.95)*(250 - 40)/86400/0.7
    out['MEOH_SYNTH'] = dict(T_C=250, P_bar=50.0, design_MPa=Pd, MeOH_kg_h=m_me, cat_kg=cat, V_bed_L=Vb*1000, tubes=ntube, tube='DN50 Sch 40 SA-106 B', L_bed_mm=round(L*1000),
                             t_req_mm=t_req, t_nom_mm=t_nom, t_ok=bool(t_nom*0.875 >= t_req), exotherm_kW=q_kW, preheat_kW=pre_kW,
                             D_mm=114, H_mm=round(L*1000) + 600, wall_mm=t_nom, V_work_L=Vb*1000, V_L=Vb*1000,
                             material='SA-106 B tube in a DN100 thermal-oil jacket (exotherm to Q3); Cu/ZnO/Al2O3 pellets', kW=pre_kW)
    return out

def write(d, g, R):
    N = {n['unit_id']: n for n in g['nodes']}; E = {e['stream_id']: e for e in g['edges']}
    TAG = 'X-MFG-31 in-house reactor design (AQS-DUTY-062)'
    for u, r in R.items():
        n = N[u]; p = n.setdefault('params', {})
        p['design'] = {k: (round(x, 4) if isinstance(x, float) else x) for k, x in r.items()}
        p['size_mm'] = [r['D_mm'] + 300, r['D_mm'] + 300, r['H_mm'] + 500]; p['size_note'] = 'L x W x H mm, set by flow_graph/param/reactor_design.py (X-MFG-31)'
        n['continuous_kw'] = {'value': round(r['kW'], 4), 'unit': 'kW', 'status': 'study', 'note': f"{TAG}. " + ('agitator motor' if u == 'GLASS_DIGEST' else 'heating and mixing' if u == 'DIGESTER' else f"feed preheat {r['kW']:.3f} kW (no interchanger credit), exotherm {r['exotherm_kW']:.3f} kW to the jacket" if u == 'MEOH_SYNTH' else f"retort heat {r['Q_process_kW']:.3f} kW / heater efficiency")}
        for sid, a, b in ((f'SF-{u}', 'SOL_ARK_60K', u), (f'SQ-{u}', u, 'HEAT_SINK')):
            if sid in E: E[sid]['rate']['value'] = round(r['kW'], 4); E[sid]['rate']['note'] = f'{TAG}.'
            else:
                e = {'stream_id': sid, 'from_unit_id': a, 'to_unit_id': b, 'phase': 'E', 'layers': ['elec'] if sid.startswith('SF') else ['energy'], 'presence': 'present',
                     'carries': '480 V AC' if sid.startswith('SF') else 'electrical input leaving as heat', 'header': 'tray', 'forbidden': 'HDR_O2, HDR_CO2', 'claim_status': 'Claimed / Partial',
                     'rate': {'value': round(r['kW'], 4), 'unit': 'kW', 'status': 'study', 'note': f'{TAG}.'}, 'from_sector_id': N[a].get('sector_id'), 'to_sector_id': N[b].get('sector_id'),
                     'open_boundary': False, 'namespace': 'S', 'gap_flags': [], 'notes': None}
                g['edges'].append(e)
    open(GP, 'w').write(json.dumps(g, indent=2))

def write_doc(d, R):
    G, Dg, P, M = R['GLASS_DIGEST'], R['DIGESTER'], R['OIL_PYRO'], R['MEOH_SYNTH']
    md = f"""# In-house reaction chambers

Document number: AQS-DUTY-062
Revision: A
Date: 2026-10-15
Authority: AQS-PLAN-007 X-MFG-31 (owner decision 2026-10-15: no bought skids). Generated by `flow_graph/param/reactor_design.py`. Study. Not a PE stamp. A-M-116.

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue. GLASS_DIGEST, DIGESTER, OIL_PYRO sized from cited residence times; LEACH_CSTR_1 stays on AQS-DUTY-050. | 2026-10-15 |

## 1. Results

| Quantity | GLASS_DIGEST | DIGESTER | OIL_PYRO |
| --- | --- | --- | --- |
| Duty | alkaline digest of milled cullet | mesophilic anaerobic | slow pyrolysis retort |
| Temperature, C | {G['T_C']} | {Dg['T_C']} | {P['T_C']:.0f} |
| Residence | {G['tau_h']:.2f} h | {Dg['srt_d']:.0f} d | {P['tau_h']:.1f} h |
| Working / vessel volume, L | {G['V_work_L']:.1f} / {G['V_L']:.1f} | {Dg['V_work_L']:.1f} / {Dg['V_L']:.1f} | {P['V_work_L']:.2f} / {P['V_L']:.2f} |
| Shell DN x height, mm | {G['D_mm']} x {G['H_mm']} | {Dg['D_mm']} x {Dg['H_mm']} | {P['D_mm']} x {P['H_mm']} |
| Wall, mm | {G['wall_mm']} | {Dg['wall_mm']} | {P['wall_mm']} |
| Mixing | PBT D{G['agitator']['D_imp_mm']} at {G['agitator']['rpm']} rpm, {G['agitator']['shaft_W']:.1f} W shaft, {G['agitator']['motor_kW']} kW motor | {Dg['mixer']} | none (static retort) |
| Heat | {G['heat']} | {Dg['heat_W']:.1f} W losses and feed | {P['Q_process_kW']:.3f} kW process, {P['kW']:.3f} kW electric |
| Electrical, kW | {G['kW']} | {Dg['kW']} | {P['kW']:.3f} |
| Material | {G['material']} | {Dg['material']} | {P['material']} |

## 2. Basis

- GLASS_DIGEST. {G['X']*100:.1f} % of the cullet dissolves (IA-GLASS-03 less S08G). For {DR.val(d,'rx_glass_d_um'):.0f} um fines the shrinking-sphere recession to that conversion is {G['delta_um']:.2f} um. At the zero-order rate of JMS2017_GLASSFIBRE (2.0e-4 g/(m2 s) at 80 C in 3 M NaOH, order 0.31, corrected to 2 M; glass 2500 kg/m3) that takes {G['t_kin_h']*3600:.0f} s. Residence is 3 x kinetic, floored at {DR.val(d,'rx_glass_tau_min_h')} h for mixing, heat-up and level control. The rate is for glass fibre; soda-lime cullet is checked at the bench (MARAGHECHI2016 reports constant-rate soda-lime dissolution in 1 M NaOH at 20-80 C).
- DIGESTER. SRT {Dg['srt_d']:.0f} d on the whole wet feed (METCALF5, high-rate mesophilic 15-20 d at 35 C); 80 % fill, gas headspace above.
- OIL_PYRO. 500 C and 1 h (ANUAR2016: 400-550 C, 30-90 min). Heat = feed x (cp x dT + heat of pyrolysis 1.3 MJ/kg, GAO2010) / heater efficiency 0.7. Half-full retort for foam and char. The graph carried 0 kW for this unit before this issue; the bus takes the {P['kW']:.3f} kW.
- Walls. Thermoplastic hoop stress from the hydrostatic head with a 3-4 mm practical minimum (DVS2205). Steel UG-16(b) 1.5 mm + 1.5 mm corrosion allowance (ASME_VIII1_UG16).

## 3. Not designed here

- LEACH_CSTR_1: AQS-DUTY-050, models/mfg/LEACH_CSTR_1 (in-house, CPVC).
- BLACK_DIGEST: designed in AQS-DUTY-063 (X-SAN-01 multi-barrier sanitation train, owner decision 2026-10-15).
- MEOH_FERM: deferred.

## 4. MEOH_SYNTH (A-M-156)

- Product {M['V_bed_L']:.2f} L of Cu/ZnO/Al2O3 ({M['cat_kg']:.2f} kg): methanol {M['MeOH_kg_h']:.3f} kg/h at a weight-time yield of {DR.val(d,'meoh_wty_kg_kgcat_h')} kg/(kg h) (CTC2020_CZA, CO2-only feed, 60 bar, 523 K) / margin {DR.val(d,'meoh_wty_margin')} for 50 bar and ageing.
- {M['tubes']} x {M['tube']}, bed {M['L_bed_mm']} mm, in a DN100 thermal-oil jacket. 250 C, 50 bar operating, {M['design_MPa']:.2f} MPa design (A-M-156).
- Wall: UG-27 (ASME_VIII1_UG27) with S = {DR.val(d,'meoh_S_MPa')} MPa (ASME_II_D, SA-106 B at 260 C), E = 1, CA 1.5 mm: required {M['t_req_mm']:.2f} mm; Sch 40 nominal {M['t_nom_mm']} mm less 12.5 % mill tolerance = {M['t_nom_mm']*0.875:.2f} mm: {'adequate' if M['t_ok'] else 'NOT adequate'}.
- Heat: exotherm {M['exotherm_kW']:.3f} kW (49.5 kJ/mol, PONTZEN2011) to the jacket; feed preheat {M['preheat_kW']:.3f} kW electric, no feed/effluent interchanger credit.
- Relief: API 520 gas, blocked outlet at the full feed (flow_graph/param/pressure_nodes.py).
"""
    open(os.path.join(ROOT, 'docs-authority/sizing/REACTOR_DESIGN.md'), 'w').write(md)

def main():
    d = DR.load(); g = json.load(open(GP)); R = design(d, g)
    for u, r in R.items(): print(u, {k: (round(x, 3) if isinstance(x, float) else x) for k, x in r.items()})
    if '--write' in sys.argv: write(d, g, R); write_doc(d, R)

if __name__ == '__main__': main()

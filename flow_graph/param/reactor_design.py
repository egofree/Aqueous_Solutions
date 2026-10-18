"""X-MFG-31 in-house reaction chambers (no bought skid): GLASS_DIGEST, DIGESTER, OIL_PYRO. LEACH_CSTR_1 is designed in AQS-DUTY-050
(models/mfg/LEACH_CSTR_1). Standard agitated cylinder H = T, impeller T/3 [PERRY9_MIX]; working volume = feed/rho x residence; vessel =
working / fill. Residence: GLASS_DIGEST from the zero-order alkaline dissolution rate [JMS2017_GLASSFIBRE] with the shrinking-sphere
conversion of the dissolved fraction, floored at a practical minimum; DIGESTER from the mesophilic SRT [METCALF5]; OIL_PYRO from the slow
pyrolysis residence at temperature [ANUAR2016]. Walls: thermoplastic hoop stress from hydrostatic head [DVS2205]; steel minimum
thickness UG-16(b) plus corrosion allowance [ASME_VIII1_UG16]. Heat: OIL_PYRO sensible + heat of pyrolysis [GAO2010] / heater efficiency.
Writes params.design and size_mm on the graph, continuous_kw for OIL_PYRO and the agitator duties, and docs-authority/sizing/REACTOR_DESIGN.md
(AQS-DUTY-062) plus sizing/REACTOR_DESIGN._generated.json (staleness manifest read by docs-authority/_rev_stamp.py: the doc regenerates
byte-identical from an unchanged graph, which cannot clear commit-based staleness on its own).
Run: python3 -m flow_graph.param.reactor_design [--write | --doc-only]   (--doc-only: doc + manifest, no graph write)"""
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
    from .sizing.heat import insulated_cylinder
    ins_p, loss_p = insulated_cylinder(v('rx_pyro_T_C'), ves['D_mm'], ves['H_mm']/1000)
    out['OIL_PYRO'] = dict(T_C=v('rx_pyro_T_C'), tau_h=v('rx_pyro_tau_h'), **ves, Q_process_kW=Q_kW, insulation_mm=ins_p, loss_W=loss_p, kW=Q_kW/v('rx_pyro_heater_eff') + loss_p/1000,
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
    from .sizing.heat import insulated_cylinder
    ins_m, loss_m = insulated_cylinder(250, 114.3, (L + 0.6))
    pre_kW = (E_('S74')*14.3 + E_('S73')*0.95)*(250 - 40)/86400/0.7 + loss_m/1000
    out['MEOH_SYNTH'] = dict(T_C=250, P_bar=50.0, design_MPa=Pd, MeOH_kg_h=m_me, cat_kg=cat, V_bed_L=Vb*1000, tubes=ntube, tube='DN50 Sch 40 SA-106 B', L_bed_mm=round(L*1000),
                             t_req_mm=t_req, t_nom_mm=t_nom, t_ok=bool(t_nom*0.875 >= t_req), exotherm_kW=q_kW, preheat_kW=pre_kW,
                             D_mm=114, H_mm=round(L*1000) + 600, wall_mm=t_nom, V_work_L=Vb*1000, V_L=Vb*1000,
                             material='SA-106 B tube in a DN100 thermal-oil jacket (exotherm to Q3); Cu/ZnO/Al2O3 pellets', kW=pre_kW)
    SM = {'YEAST': dict(tau='rx_yeast_tau_h', T='rx_yeast_T_C', mat='HDPE (PE100), 50 mm PIR', mix='CO2 evolution; daily recirculation pump', fill=0.75),
          'ABE': dict(tau='rx_abe_tau_h', T='rx_abe_T_C', mat='HDPE (PE100), 50 mm PIR, N2-blanketed (anaerobic)', mix='gas recirculation (no shaft seal)', fill=0.75),
          'ACETOX': dict(tau='rx_acetox_tau_h', T='rx_acetox_T_C', mat='PP, 50 mm PIR; O2 sparger PVDF', mix='O2 sparge from HDR_O2', fill=0.7),
          'HTC': dict(tau='rx_htc_tau_h', T='rx_htc_T_C', mat='SA-240 316L, 50 mm mineral wool', mix='static autoclave, batch', fill=0.8),
          'MEOH_FERM': dict(tau='rx_meohferm_tau_h', T='rx_meohferm_T_C', mat='HDPE (PE100), 50 mm PIR', mix='daily recirculation pump', fill=0.75),
          'GLYOXAL': dict(tau='rx_glyoxal_tau_h', T='rx_glyoxal_T_C', mat='SA-240 304L (nitric service, ULLMANN_NITRIC); NO off-gas to HNO3', mix='recirculation pump, nitrite-initiated (HOTANAHALLI1972)', fill=0.7),
          'IMID': dict(tau='rx_imid_tau_h', T='rx_imid_T_C', mat='SA-240 316L, 50 mm mineral wool', mix='recirculation pump', fill=0.7),
          'BUCL': dict(tau='rx_bucl_tau_h', T='rx_bucl_T_C', mat='glass-lined steel (HCl/ZnCl2 at reflux), reflux condenser to Q1', mix='boiling at reflux', fill=0.6)}
    # Biological and hydrothermal reactors (X-MFG-31 batch 2): working volume = feed / rho x residence [BAI2008, JONES1986, GULLO2014, LIBRA2011];
    # heat = insulated losses (U 0.5 W/(m2 K)) + feed sensible heat from 20 C; HTC is a pressure vessel at water saturation (UG-27, 316L).
    for u, c in SM.items():
        tau = v(c['tau']); T = v(c['T']); m = inflow(u); Vw = m/1000*tau/24
        if u == 'HTC':
            Pd = v('psat_water_200C_MPa')*v('press_design_margin'); ves = vessel(Vw, c['fill'], 1000.0, steel=True, t_min=3.0, CA=1.5)
            t_req = Pd*(ves['D_mm']/2)/(v('sa240_316L_S_MPa_200C') - 0.6*Pd) + 1.5; ves['wall_mm'] = max(3.0, math.ceil(t_req*2)/2)
            extra = dict(design_MPa=Pd, t_req_mm=t_req)
        else: ves = vessel(Vw, c['fill'], 1000.0, sigma_MPa=5.0, t_min=4.0); extra = {}
        A = math.pi*ves['D_mm']/1000*ves['H_mm']/1000 + math.pi*(ves['D_mm']/1000)**2/2
        if T > 50:
            from .sizing.heat import insulated_cylinder
            W = insulated_cylinder(T, ves['D_mm'], ves['H_mm']/1000)[1] + m*4.18*(T - 20)/86.4
        else: W = 0.5*A*(T - 20) + m*4.18*(T - 20)/86.4
        out[u] = dict(T_C=T, tau_h=tau, **ves, **extra, heat_W=W, mixer=c['mix'], material=c['mat'], kW=round(W/1000 + (0.02 if u != 'HTC' else 0), 4))
    # Catalytic tube reactors (X-MFG-31 batch 3, A-M-157): catalyst from the cited space velocity; bed in DN15/DN25 Sch 40 tube, >= 300 mm;
    # heater = feed sensible (cp 2.5 kJ/(kg K)) + vaporisation [NIST_WEBBOOK] + endotherm, / 0.7; exotherms not credited.
    TUBES = ((15, 21.3, 2.77), (25, 33.4, 3.38), (50, 60.3, 3.91))
    def tube_bed(V_L):
        for dn, od, t in TUBES:
            idm = od - 2*t; L = V_L/1000/(math.pi*(idm/1000)**2/4)*1000
            if L <= 1500: return dict(tube=f'DN{dn} Sch 40', OD_mm=od, t_nom_mm=t, L_bed_mm=max(300, round(L)))
        return dict(tube='DN50 Sch 40', OD_mm=60.3, t_nom_mm=3.91, L_bed_mm=round(L))
    etoh = R('IA-ETOH'); meoh_f = R('IA-FORM-S') + R('IA-MEOH-FORM'); meoh_a = R('IA-MEOH-MEAM'); nh3 = R('IA-NH3-MEAM')
    cat = {'ALD': etoh/24/v('rx_ald_whsv_h'),
           'FORM': meoh_f/32.042*1000/24*v('rx_form_space_time_g_h_mol')/1000,
           'MEAM': (meoh_a/32.042 + nh3/17.031)*1000/24*0.022414/v('rx_meam_ghsv_h')*1000*v('rx_cat_bulk_kg_L')}
    heat = {'ALD': etoh*(2.5*(v('rx_ald_T_C') - 20)/1000 + v('hvap_ethanol_MJ_kg')) + etoh/46.069*1000*v('rx_ald_dH_kJ_mol')/1000,
            'FORM': meoh_f*(2.5*(150 - 20)/1000 + v('hvap_methanol_MJ_kg')),          # feed to 150 C; the bed runs on its exotherm (FORMOX_REVIEW2021)
            'MEAM': meoh_a*(2.5*(v('rx_meam_T_C') - 20)/1000 + v('hvap_methanol_MJ_kg')) + nh3*(2.5*(v('rx_meam_T_C') - 20)/1000 + v('hvap_ammonia_MJ_kg'))}
    note = {'ALD': 'Cu/SiO2 pellets, 250 C, atmospheric (CUSIO2_ALD2023)',
            'FORM': 'iron molybdate, 350 C bed, atmospheric; feed must be diluted to about 10 mol% MeOH and 10 mol% O2 in N2 (FORMOX_REVIEW2021): the graph feeds pure O2 from HDR_O2, a N2 diluent loop is required (X-SAF-02)',
            'MEAM': 'amorphous silica-alumina, 400 C, 20.7 bar (EP0064380, US1875746)'}
    for u in ('ALD', 'FORM', 'MEAM'):
        Vb = cat[u]/v('rx_cat_bulk_kg_L'); tb = tube_bed(Vb)
        from .sizing.heat import insulated_cylinder
        T_ = v({'ALD': 'rx_ald_T_C', 'FORM': 'rx_form_T_C', 'MEAM': 'rx_meam_T_C'}[u]); ins_t, loss = insulated_cylinder(T_, tb['OD_mm'], (tb['L_bed_mm'] + 300)/1000)
        kw = heat[u]/86.4/0.7 + loss/1000
        r = dict(T_C=T_, cat_kg=cat[u], V_bed_L=Vb, **tb, heat_W=kw*1000, insulation_mm=ins_t, loss_W=loss,
                 material='SA-312 TP316L tube in a band heater and mineral wool', basis=note[u], D_mm=round(tb['OD_mm']), H_mm=tb['L_bed_mm'] + 300, wall_mm=tb['t_nom_mm'],
                 V_work_L=Vb, V_L=Vb, kW=round(kw, 4))
        if u == 'MEAM':
            Pd = v('rx_meam_P_bar')*v('press_design_margin')/10; r.update(design_MPa=Pd, t_req_mm=Pd*(tb['OD_mm']/2)/(v('s_316L_400C_MPa_lower_bound') + 0.4*Pd) + 1.5)
        out[u] = r
    # ACEX (X-PAR-14, A-M-162): two OH-form strong-base anion columns, one on line and one regenerating (redundant pair) [PERRY9_IX]
    eq = R('IA-BMIM')*1000/174.67*v('ix_cycle_h')/24; Vb = eq/(v('ix_sba_cap_eq_L')*v('ix_util'))
    tb = tube_bed(Vb)
    out['ACEX'] = dict(T_C=25, eq_per_cycle=eq, V_bed_L=Vb, columns=2, **tb, D_mm=round(tb['OD_mm']), H_mm=tb['L_bed_mm'] + 300, wall_mm=tb['t_nom_mm'], V_work_L=Vb, V_L=Vb*1.5,
                   heat_W=0.0, material='PP-H column (Sch 40 PP pipe), resin strong-base type I gel, OH form; acetic acid neutraliser vessel', kW=0.02,
                   basis=f'[Bmim]Cl over OH-form resin, neutralised with AcOH; NaOH 20 wt% regenerant (PERRY9_IX); capacity {v("ix_sba_cap_eq_L")} eq/L x {v("ix_util")} utilisation')
    # HNO3 (X-MFG-31 batch 4, A-M-161): Ostwald [ULLMANN_NITRIC]: Pt-Rh gauze burner in a DN25 tube held at temperature (losses on the bus,
    # feed preheat to 250 C; the oxidation exotherm holds the gauze at plant scale but not at this rate), then a stainless absorber of liquid hold-up tau.
    nh3n = R('IA-NH3-NIT'); o2n = R('IA-O2-NIT'); Tg = v('rx_hno3_gauze_T_C')
    from .sizing.heat import insulated_cylinder
    ins_g, loss_g = insulated_cylinder(Tg, 33.4, 0.3)
    pre = (nh3n*2.2 + o2n*0.95)*(250 - 20)/86.4/0.7
    Vw = R('IA-HNO3')/1400*v('rx_hno3_absorber_tau_h')/24; ves = vessel(Vw, 0.5, 1400.0, steel=True, t_min=2.0)
    kw = (pre + loss_g)/1000 + 0.02
    out['HNO3'] = dict(T_C=Tg, gauze='Pt-Rh gauze in DN25 Sch 40 SA-312 310S, 300 mm', insulation_mm=ins_g, loss_W=loss_g, heat_W=kw*1000, tau_h=v('rx_hno3_absorber_tau_h'),
                       **ves, material='burner 310S tube; absorber SA-240 304L packed column', kW=round(kw, 4))
    live = {n['unit_id'] for n in g['nodes'] if n.get('presence', 'present') == 'present'}   # R11 Rev AC regen: DIGESTER, YEAST, ABE, ACETOX, HTC, GLYOXAL, IMID, BUCL, HNO3, ACEX, ALD, FORM, MEAM left the graph; only live units are sized
    return {u: r for u, r in out.items() if u in live}

def write(d, g, R):
    N = {n['unit_id']: n for n in g['nodes']}; E = {e['stream_id']: e for e in g['edges']}
    TAG = 'X-MFG-31 in-house reactor design (AQS-DUTY-062)'
    for u, r in R.items():
        if u not in N: continue   # R11 Rev AC regen: unit absent from the graph (removed in a later revision)
        n = N[u]; p = n.setdefault('params', {})
        p['design'] = {k: (round(x, 4) if isinstance(x, float) else x) for k, x in r.items()}
        p['size_mm'] = [r['D_mm'] + 300, r['D_mm'] + 300, r['H_mm'] + 500]; p['size_note'] = 'L x W x H mm, set by flow_graph/param/reactor_design.py (X-MFG-31)'
        n['continuous_kw'] = {'value': round(r['kW'], 4), 'unit': 'kW', 'status': 'study', 'note': f"{TAG}. " + ('agitator motor' if u == 'GLASS_DIGEST' else 'heating and mixing' if u == 'DIGESTER' else f"feed preheat {r['kW']:.3f} kW (no interchanger credit), exotherm {r['exotherm_kW']:.3f} kW to the jacket" if u == 'MEOH_SYNTH' else f"losses and feed heat {r['heat_W']:.1f} W" if u in ('YEAST', 'ABE', 'ACETOX', 'HTC', 'GLYOXAL', 'IMID', 'BUCL', 'HNO3', 'ACEX', 'MEOH_FERM') else f"feed vaporisation and preheat {r['heat_W']:.1f} W" if u in ('ALD', 'FORM', 'MEAM') else f"retort heat {r['Q_process_kW']:.3f} kW / heater efficiency")}
        for sid, a, b in ((f'SF-{u}', 'SOL_ARK_60K', u), (f'SQ-{u}', u, 'HEAT_SINK')):
            if sid in E: E[sid]['rate']['value'] = round(r['kW'], 4); E[sid]['rate']['note'] = f'{TAG}.'
            elif a in N and b in N:   # R11 Rev AC regen: HEAT_SINK and the SQ-* heat edges died in Rev AC; only create edges whose endpoints exist
                e = {'stream_id': sid, 'from_unit_id': a, 'to_unit_id': b, 'phase': 'E', 'layers': ['elec'] if sid.startswith('SF') else ['energy'], 'presence': 'present',
                     'carries': '480 V AC' if sid.startswith('SF') else 'electrical input leaving as heat', 'header': 'tray', 'forbidden': 'HDR_O2, HDR_CO2', 'claim_status': 'Claimed / Partial',
                     'rate': {'value': round(r['kW'], 4), 'unit': 'kW', 'status': 'study', 'note': f'{TAG}.'}, 'from_sector_id': N[a].get('sector_id'), 'to_sector_id': N[b].get('sector_id'),
                     'open_boundary': False, 'namespace': 'S', 'gap_flags': [], 'notes': None}
                g['edges'].append(e)
    open(GP, 'w').write(json.dumps(g, indent=2))

def write_doc(d, R):
    # R11 Rev AC regen: units that left the graph (DIGESTER and the bio/chem set below) are sized only when present; sections drop their rows.
    GONE = [u for u in ('DIGESTER', 'YEAST', 'ABE', 'ACETOX', 'HTC', 'GLYOXAL', 'IMID', 'BUCL', 'HNO3', 'ACEX', 'ALD', 'FORM', 'MEAM') if u not in R]
    G, P, M = R['GLASS_DIGEST'], R['OIL_PYRO'], R['MEOH_SYNTH']
    md = f"""# In-house reaction chambers

Document number: AQS-DUTY-062
Revision: B
Date: 2026-10-18
Authority: AQS-PLAN-007 X-MFG-31 (owner decision 2026-10-15: no bought skids). Generated by `flow_graph/param/reactor_design.py`. Study. Not a PE stamp. A-M-116.

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue. GLASS_DIGEST, DIGESTER, OIL_PYRO sized from cited residence times; LEACH_CSTR_1 stays on AQS-DUTY-050. | 2026-10-15 |
| B | Rev AC regeneration: units removed from the graph are dropped ({', '.join(GONE) if GONE else 'none'}); remaining units resized from the current rates. | 2026-10-18 |

## 1. Results

| Quantity | GLASS_DIGEST | OIL_PYRO |
| --- | --- | --- |
| Duty | alkaline digest of milled cullet | slow pyrolysis retort |
| Temperature, C | {G['T_C']} | {P['T_C']:.0f} |
| Residence | {G['tau_h']:.2f} h | {P['tau_h']:.1f} h |
| Working / vessel volume, L | {G['V_work_L']:.1f} / {G['V_L']:.1f} | {P['V_work_L']:.2f} / {P['V_L']:.2f} |
| Shell DN x height, mm | {G['D_mm']} x {G['H_mm']} | {P['D_mm']} x {P['H_mm']} |
| Wall, mm | {G['wall_mm']} | {P['wall_mm']} |
| Mixing | PBT D{G['agitator']['D_imp_mm']} at {G['agitator']['rpm']} rpm, {G['agitator']['shaft_W']:.1f} W shaft, {G['agitator']['motor_kW']} kW motor | none (static retort) |
| Heat | {G['heat']} | {P['Q_process_kW']:.3f} kW process, {P['kW']:.3f} kW electric |
| Electrical, kW | {G['kW']} | {P['kW']:.3f} |
| Material | {G['material']} | {P['material']} |

## 2. Basis

- GLASS_DIGEST. {G['X']*100:.1f} % of the cullet dissolves (IA-GLASS-03 less S08G). For {DR.val(d,'rx_glass_d_um'):.0f} um fines the shrinking-sphere recession to that conversion is {G['delta_um']:.2f} um. At the zero-order rate of JMS2017_GLASSFIBRE (2.0e-4 g/(m2 s) at 80 C in 3 M NaOH, order 0.31, corrected to 2 M; glass 2500 kg/m3) that takes {G['t_kin_h']*3600:.0f} s. Residence is 3 x kinetic, floored at {DR.val(d,'rx_glass_tau_min_h')} h for mixing, heat-up and level control. The rate is for glass fibre; soda-lime cullet is checked at the bench (MARAGHECHI2016 reports constant-rate soda-lime dissolution in 1 M NaOH at 20-80 C).
- OIL_PYRO. 500 C and 1 h (ANUAR2016: 400-550 C, 30-90 min). Heat = feed x (cp x dT + heat of pyrolysis 1.3 MJ/kg, GAO2010) / heater efficiency 0.7, plus the insulated shell loss {P['loss_W']:.0f} W at {P['insulation_mm']} mm mineral wool (AQS-THM-003). Half-full retort for foam and char. The graph carried 0 kW for this unit before this issue; the bus takes the {P['kW']:.3f} kW.
- Walls. Thermoplastic hoop stress from the hydrostatic head with a 3-4 mm practical minimum (DVS2205). Steel UG-16(b) 1.5 mm + 1.5 mm corrosion allowance (ASME_VIII1_UG16).

## 3. Not designed here

- LEACH_CSTR_1: AQS-DUTY-050, models/mfg/LEACH_CSTR_1 (in-house, CPVC).
- BLACK_DIGEST: designed in AQS-DUTY-063 (X-SAN-01 multi-barrier sanitation train, owner decision 2026-10-15).
- MEOH_FERM: section 5 (A-M-163).

## 4. MEOH_SYNTH (A-M-156)

- Product {M['V_bed_L']:.2f} L of Cu/ZnO/Al2O3 ({M['cat_kg']:.2f} kg): methanol {M['MeOH_kg_h']:.3f} kg/h at a weight-time yield of {DR.val(d,'meoh_wty_kg_kgcat_h')} kg/(kg h) (CTC2020_CZA, CO2-only feed, 60 bar, 523 K) / margin {DR.val(d,'meoh_wty_margin')} for 50 bar and ageing.
- {M['tubes']} x {M['tube']}, bed {M['L_bed_mm']} mm, in a DN100 thermal-oil jacket. 250 C, 50 bar operating, {M['design_MPa']:.2f} MPa design (A-M-156).
- Wall: UG-27 (ASME_VIII1_UG27) with S = {DR.val(d,'meoh_S_MPa')} MPa (ASME_II_D, SA-106 B at 260 C), E = 1, CA 1.5 mm: required {M['t_req_mm']:.2f} mm; Sch 40 nominal {M['t_nom_mm']} mm less 12.5 % mill tolerance = {M['t_nom_mm']*0.875:.2f} mm: {'adequate' if M['t_ok'] else 'NOT adequate'}.
- Heat: exotherm {M['exotherm_kW']:.3f} kW (49.5 kJ/mol, PONTZEN2011) to the jacket; feed preheat {M['preheat_kW']:.3f} kW electric, no feed/effluent interchanger credit.
- Relief: API 520 gas, blocked outlet at the full feed (flow_graph/param/pressure_nodes.py).
"""
    bio = (('YEAST', 'BAI2008'), ('ABE', 'JONES1986'), ('ACETOX', 'GULLO2014'), ('HTC', 'LIBRA2011'), ('GLYOXAL', 'HOTANAHALLI1972, A-M-161'), ('IMID', 'A-M-161'), ('BUCL', 'A-M-161'), ('MEOH_FERM', 'A-M-163'))
    md += '\n## 5. Biological and hydrothermal reactors\n\n| Unit | T, C | Residence, h | Working / vessel, L | DN x H, mm | Wall, mm | Heat, W | Material | Source |\n| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n'
    for u, src in bio:
        if u not in R: continue
        r = R[u]; md += f"| {u} | {r['T_C']} | {r['tau_h']} | {r['V_work_L']:.1f} / {r['V_L']:.1f} | {r['D_mm']} x {r['H_mm']} | {r['wall_mm']} | {r['heat_W']:.1f} | {r['material']} | {src} |\n"
    if 'HTC' in R: md += f"\nHTC is a pressure vessel: water saturation 1.555 MPa at 200 C (NIST_WEBBOOK) x 1.10 = {R['HTC']['design_MPa']:.2f} MPa design; UG-27 (ASME_VIII1_UG27) with S 99 MPa (316L at 200 C, ASME_II_D) + 1.5 mm CA: {R['HTC']['t_req_mm']:.2f} mm required.\n"
    md += '\n## 6. Catalytic tube reactors (A-M-157)\n\n| Unit | T, C | Catalyst, g | Bed, mL | Tube | Bed length, mm | Heater, W | Basis |\n| --- | --- | --- | --- | --- | --- | --- | --- |\n'
    for u in ('ALD', 'FORM', 'MEAM'):
        if u not in R: continue
        r = R[u]; md += f"| {u} | {r['T_C']} | {r['cat_kg']*1000:.1f} | {r['V_bed_L']*1000:.1f} | {r['tube']} | {r['L_bed_mm']} | {r['heat_W']:.1f} | {r['basis']} |\n"
    if 'MEAM' in R: md += f"\nMEAM is pressure equipment: 20.7 bar x 1.10 = {R['MEAM']['design_MPa']:.2f} MPa design; UG-27 316L at 400 C (S 80 MPa lower bound, A-M-157) {R['MEAM']['t_req_mm']:.2f} mm required against {R['MEAM']['t_nom_mm']*0.875:.2f} mm minimum of {R['MEAM']['tube']}.\n"
    if 'HNO3' in R:
        H = R['HNO3']
        md += f"\n## 7. Nitric acid (A-M-161)\n\nOstwald route (ULLMANN_NITRIC): {H['gauze']} at {H['T_C']:.0f} C, {H['insulation_mm']} mm insulation, loss {H['loss_W']:.0f} W; absorber {H['D_mm']} x {H['H_mm']} mm, {H['V_work_L']:.2f} L hold-up ({H['tau_h']} h). Heater {H['heat_W']:.0f} W. At this rate the burner does not run autothermally; the bus holds the gauze.\n"
    if 'GLYOXAL' in R or 'ACEX' in R: md += '\nGLYOXAL runs on the HNO3 route (X-PAR-13, A-M-160). ACEX (X-PAR-14, A-M-162): the direct exchange [Bmim]Cl + AcOH -> [Bmim]OAc + HCl is not driven (HCl the stronger acid); the route is an OH-form strong-base anion resin then acetic acid neutralisation, resin regenerated with 20 wt% NaOH from EVAP_BASE (PERRY9_IX).\n'
    if 'ACEX' in R:
        A_ = R['ACEX']; md += f"ACEX columns: {A_['columns']} x {A_['tube']} PP, bed {A_['V_bed_L']:.2f} L ({A_['L_bed_mm']} mm), {A_['eq_per_cycle']:.2f} eq per {DR.val(d,'ix_cycle_h')} h cycle; one on line, one regenerating.\n"
    open(os.path.join(ROOT, 'docs-authority/sizing/REACTOR_DESIGN.md'), 'w').write(md)
    # U2a staleness manifest (read by docs-authority/_rev_stamp.py): records (file, graph_sha256) so a
    # byte-identical regeneration still proves the doc was derived from this exact graph.
    import hashlib
    sha = hashlib.sha256(open(GP, 'rb').read()).hexdigest()
    json.dump({'_generated_from': {'graph_sha256': sha, 'generator': 'flow_graph/param/reactor_design.py'},
               'files': {'docs-authority/sizing/REACTOR_DESIGN.md': sha}},
              open(os.path.join(ROOT, 'docs-authority/sizing/REACTOR_DESIGN._generated.json'), 'w'), indent=1)

def main():
    d = DR.load(); g = json.load(open(GP)); R = design(d, g)
    for u, r in R.items(): print(u, {k: (round(x, 3) if isinstance(x, float) else x) for k, x in r.items()})
    if '--write' in sys.argv: write(d, g, R); write_doc(d, R)
    elif '--doc-only' in sys.argv: write_doc(d, R)   # doc + manifest only; the graph is left untouched

if __name__ == '__main__': main()

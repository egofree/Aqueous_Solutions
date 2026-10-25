"""X-INV-02 motor family designs (AQS-INV-005). One open design basis and manufacturing plan per family in MOTOR_FAMILIES.csv.
Induction (IEC frames, hermetic): output equation S = C D^2 L n_s with C = (pi^2/sqrt 2) k_w B_delta A [PYRHONEN2014 eq. 6.1-6.3], aspect
chi = L/D = (pi/4p) sqrt(p) [PYRHONEN2014 eq. 6.2], turns from E = 4.44 f k_w N Phi, conductor at J = 5 A/mm2 (TEFC range 3-8 A/mm2,
PYRHONEN2014 table 6.4); IEC 60072-1 frame dimensions; IE3 minimum efficiency IEC 60034-30-1:2025 60 Hz table (2-pole hermetic, 4-pole IEC frames). PM BLDC: T = (pi/2) D^2 L A B [HENDERSHOT2010 ch. 2]. Hybrid steppers NEMA ICS 16 flanges. Solenoids: coil
resistance R = V^2/P. Quarter-turn actuator: ISO 5211 flange torque limit. Coefficients chosen inside the published ranges are A-M-126.
Writes docs-authority/inventory/MOTOR_DESIGNS.md, MOTOR_DESIGNS.csv and motor_families/MF-nn.md. Run: python3 -m flow_graph.inventory.motor_designs"""
import csv, math, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
D = os.path.join(ROOT, 'docs-authority/inventory')
IEC72 = {'63': (63, 11, 23, 100, 80, 7), '71': (71, 14, 30, 112, 90, 7), '80': (80, 19, 40, 125, 100, 10), '90S': (90, 24, 50, 140, 100, 10), '90L': (90, 24, 50, 140, 125, 10),
         '100L': (100, 28, 60, 160, 140, 12), '112M': (112, 28, 60, 190, 140, 12), '132M': (132, 38, 80, 216, 178, 12), '180M': (180, 48, 110, 279, 241, 15)}   # H, D, E, A, B, K mm
IE3_60 = {   # IEC 60034-30-1:2025 Table for 60 Hz IE3 (kW: 2-pole, 4-pole) [IEC60034_30_1]; intermediate ratings interpolated linearly (A-M-126; the standard's 5.4.7 formula to be applied on the type test)
    0.12: (62.0, 66.0), 0.18: (65.6, 69.5), 0.25: (69.5, 73.4), 0.37: (73.4, 78.2), 0.55: (76.8, 81.1), 0.75: (77.0, 83.5), 1.1: (84.0, 86.5), 1.5: (85.5, 86.5),
    2.2: (86.5, 89.5), 3.7: (88.5, 89.5), 5.5: (89.5, 91.7), 7.5: (90.2, 91.7), 11: (91.0, 92.4), 15: (91.0, 93.0), 18.5: (91.7, 93.6), 22: (91.7, 93.6)}
def ie3(kw, p):
    k = sorted(IE3_60); c = 0 if p == 1 else 1
    if kw in IE3_60: return IE3_60[kw][c]
    lo = max(x for x in k if x <= kw); hi = min(x for x in k if x >= kw)
    return IE3_60[lo][c] + (IE3_60[hi][c] - IE3_60[lo][c])*(kw - lo)/(hi - lo)
AWG = [(n, 0.012668*92**((36 - n)/19.5)**2) for n in range(8, 41)]   # mm^2, ASTM B258
BRG = {'63': '6201-2Z', '71': '6202-2Z', '80': '6204-2Z', '90S': '6205-2Z', '90L': '6205-2Z', '100L': '6206-2Z', '112M': '6306-2Z', '132M': '6308-2Z', '180M': '6310-2Z'}
B_D, KW, J, F = 0.75, 0.92, 5.0, 60.0
def awg(a): return next((f'{n} AWG ({s:.3f} mm2)' for n, s in reversed(AWG) if s >= a), f'{a:.2f} mm2 (parallel strands)')
def induction(kw, V, p, frame=None):
    eta = ie3(kw, p)/100; pf = 0.80 if kw < 4 else 0.84
    A = 20e3 if kw < 1 else 30e3 if kw < 10 else 40e3
    ns = F/p; S = kw*1e3/(eta*pf); C = math.pi**2/math.sqrt(2)*KW*B_D*A
    chi = math.pi/(4*p)*math.sqrt(p); sp = 0.55 if p == 2 else 0.5; Dg = (S/(C*ns*chi))**(1/3); Dout = Dg/sp; held = False
    if frame in IEC72 and Dout > 0.85*2*IEC72[frame][0]/1e3:                 # frame holds the lamination OD; the core lengthens instead
        Dout = 0.85*2*IEC72[frame][0]/1e3; Dg = sp*Dout; held = True
    L = S/(C*ns*Dg**2)
    tau = math.pi*Dg/(2*p); Phi = 2/math.pi*B_D*tau*L; Vph = V/math.sqrt(3); N = 0.95*Vph/(4.44*F*KW*Phi)
    I = S/(math.sqrt(3)*V); a = I/J; Qs = 24 if (frame or '90')[:2] in ('63', '71', '80') else 36; Qr = 22 if Qs == 24 else 28
    # Rev B (X-INV-02B, A-M-218): the slots and yoke must fit inside Dout. Slot area from the winding (fill 0.40, enamel 15 %),
    # parallel tooth at 1.6 T, yoke at 1.5 T; if Dg + 2 (h_slot + h_yoke) > 1.02 Dout the core lengthens (N and slot area fall as 1/L).
    lengthened = 1.0
    for _ in range(60):
        Phi = 2/math.pi*B_D*tau*L; N = 0.95*Vph/(4.44*F*KW*Phi)
        aw = next((sz for n_, sz in reversed(AWG) if sz >= a), a)
        As = 2*3*N/Qs*aw*1.15/0.40; ts = math.pi*Dg*1e3/Qs; bt = B_D*ts/(0.97*1.6); b1 = ts - bt; k = 2*math.pi/Qs
        hs = (-b1 + math.sqrt(b1**2 + 2*k*As))/k; hy = Phi/(2*0.97*L*1.5)*1e3
        gap = 0.18 + 0.006*(kw*1e3)**0.4 if p > 1 else 0.2 + 0.01*(kw*1e3)**0.4
        if Dg*1e3 + gap + 2*(hs + hy) <= Dout*1e3: break
        L *= 1.02; lengthened *= 1.02
    m_fe = math.pi/4*(Dout**2 - (Dg*0.33)**2)*L*0.97*7650*0.7; m_cu = 3*N*2*(L + 1.2*tau)*a*1e-6*8960
    out = dict(eta=eta, pf=pf, A=A, Dg=Dg*1e3, L=L*1e3, Dout=Dout*1e3, N=round(N), I=I, cond=awg(a), Qs=Qs, Qr=Qr, m_fe=m_fe, m_cu=m_cu, rpm=round(120*F/(2*p)))
    out['held'] = held; out['LD'] = L/Dg; out['slot_fit_L_factor'] = round(lengthened, 3)
    if frame in IEC72: out['fits'] = L/Dg <= 2.5
    return out
def pm(kw, rpm, Dmax):
    T = kw*1e3/(rpm*2*math.pi/60); A, B = 15e3, 0.8; DL = T/(math.pi/2*A*B)
    Dg = min(Dmax*0.5, (DL/1.0)**(1/3)); L = DL/Dg**2
    return dict(T=T, Dg=Dg*1e3, L=L*1e3, A=A, B=B)
PLAN = {'induction': ['The stator and rotor laminations are laser-cut, and later stamped, from M400-50A electrical steel (EN 10106) 0.5 mm thick, then stacked and welded or cleated',
                      'The stator is wound with Grade 2 enamelled copper round wire (IEC 60317-13, class 200) from the plant wire line, as a single-layer concentric winding with a class F insulation system (IEC 60085) and NMN slot liners (Nomex–Mylar–Nomex laminate)',
                      'The wound stator is vacuum-pressure impregnated (VPI) with polyester resin and cured',
                      'The rotor cage is die-cast in aluminium from the in-house melt and skewed by one slot pitch',
                      'The shaft is turned and ground from C45 steel (EN 10083-2), with a keyway to IEC 60072-1',
                      'The frame is cast aluminium (A356), or cast iron above frame IEC 132, and is machined and fitted with end shields. It gives IP55 protection (IEC 60034-5) and IC 411 fan cooling (IEC 60034-6)',
                      'Bearings are taken from the bearing families of task X-INV-05, and the rotor is balanced to grade G2.5 of ISO 21940-11',
                      'Each motor receives the routine tests of IEC 60034-1: winding resistance, no-load, locked rotor, and a high-voltage (hipot) test at 2U + 1000 V. The first article is also type-tested for efficiency (IEC 60034-2-1) and noise (IEC 60034-9)'],
        'hermetic': ['The stator and rotor are made as in the induction plan, without frame, shaft or fan, as a 2-pole motor. The winding varnish and lead insulation are compatible with the refrigerant and with POE (polyol ester) oil (UL 60335-2-34 and IEC 60335-2-34 Annex AA)',
                     'The motor is shrink-fitted into the compressor shell on the scroll compressor line (task X-MFG-35)',
                     'After the shell is welded, the motor receives a high-voltage test and an insulation resistance test, and a locked-rotor and thermal protector test to IEC 60335-2-34'],
        'BLDC': ['The stator uses 0.35 mm NO20 or M270-35A laminations (EN 10106) with 12 slots and concentrated coils on each tooth',
                 'The rotor has 8 poles of surface magnets. NdFeB magnets need a supply of rare earths, which is a review item; bonded ferrite is the alternative, at about 0.4 of the torque density',
                 'Commutation uses Hall sensors or sensorless back-EMF detection, with a driver from the BLDC driver family of task X-INV-05',
                 'The flange follows NEMA ICS 16, and the housing is extruded aluminium',
                 'Each motor is tested for back-EMF constant, no-load current and torque-speed curve, with a high-voltage test at 500 V + 2U'],
        'stepper': ['The motor is a 2-phase hybrid stepper with 1.8 degree steps: an 8-pole stator and a 50-tooth rotor with an axially magnetised NdFeB ring between two toothed caps',
                    'The laminations are 0.35 mm thick (EN 10106), and the bifilar or unipolar windings are wound from the plant wire line',
                    'The flange follows NEMA ICS 16',
                    'Each motor is tested for holding torque, step accuracy (within 5 %), resistance and inductance'],
        'solenoid': ['The coil is wound with class H enamelled wire (IEC 60317-13) on a bobbin of glass-filled polyamide (PA66-GF), with the 22 mm interface of ISO 15218',
                     'The plunger and frame are ferritic stainless steel 430F',
                     'The coil is encapsulated in epoxy and fitted with a DIN EN 175301-803 connector',
                     'Each solenoid is tested for coil resistance, pull-in at 85 % of rated voltage, and insulation at 1000 V'],
        'ec_fan': ['The fan and its EC motor are taken from the nameplate or datasheet of the selected heat-pump condenser fan (A-M-332). An in-house motor design is deferred until the fan is selected',
                   'Each fan is tested for input power, speed range and response to the speed command at rated airflow, against the datasheet'],
        'actuator': ['A BLDC motor of family MF-01 drives a worm gear with a bronze wheel and a steel worm',
                     'The output is the square drive of ISO 5211 F03, with end stops and position switches',
                     'The housing is glass-filled polyamide (PA66-GF) or aluminium, with IP67 protection',
                     'Each actuator is tested for breakaway torque at the ISO 5211 F03 rating and for travel time, and a sample is tested for cycle life']}
MAG = {'NdFeB': dict(Br=1.30, Hc=1000, rho=7500, lm=3.0, grade='sintered N42, Br 1.29-1.32 T, Hcj >= 955 kA/m', RE=0.31),
       'ferrite': dict(Br=0.27, Hc=190, rho=3600, lm=6.0, grade='anisotropic polymer-bonded Sr-ferrite, Br 0.25-0.29 T, HcB 180-200 kA/m', RE=0.0)}   # COEY2010 table 11.4; IEC 60404-8-1
GAP, MUR, LEAK, BSAT, PFE = 0.5, 1.05, 0.9, 0.8, 0.05
def bg(m): M = MAG[m]; return min(BSAT, LEAK*M['Br']*M['lm']/(M['lm'] + MUR*GAP))    # air-gap flux, magnet circuit (HENDERSHOT2010 ch. 4); tooth-limited at BSAT
def pm_variant(kw, rpm, flange, mag, A=15e3, J=5.0):
    T = kw*1e3/(rpm*2*math.pi/60); B = bg(mag); DL = T/(math.pi/2*A*B)
    Dg = min(flange*0.5e-3, (DL/1.0)**(1/3)); L = DL/Dg**2
    lt = 2*(L + 1.2*math.pi*Dg/8)                                  # turn length, 8 poles
    Pcu = 1.72e-8*(J*1e6)*A*math.pi*Dg*lt/2                          # rho J A (pi D) (l_turn/2), W
    eta = kw*1e3/(kw*1e3*(1 + PFE) + Pcu)
    mm = math.pi*Dg*MAG[mag]['lm']*1e-3*L*MAG[mag]['rho']
    nxt = 'fits' if L*1e3 <= 2.5*flange else ('next flange (NEMA 23)' if flange < 57 else 'next flange (NEMA 34)' if flange < 86 else 'longer than 2.5 x flange: review')
    return dict(T=T*1e3, B=B, D=Dg*1e3, L=L*1e3, eta=eta, mag_g=mm*1e3, RE_g=mm*1e3*MAG[mag]['RE'], frame=nxt)
ROUTE = {'NdFeB': 'Nd/Pr from feedstock magnets (IA-FEED-01 scrap): hydrogen decrepitation and re-sintering of recovered NdFeB (WALTON2015), or full RE separation by solvent extraction + NdF3 molten-salt electrolysis (not on the graph); strip cast, jet mill, field press, sinter 1080 C, Ni coat',
         'ferrite': 'Fe2O3 from the leach iron (hematite) + SrCO3 (Sr not in the plant feed: celestite import or Sr from feedstock ceramics); calcine 1250 C, mill, compound in PA12, injection-mould in an orienting field; no sintering line'}
def magnets(fam):
    out = []
    for f in fam:
        if f['family'] not in ('MF-01', 'MF-02', 'MF-03', 'MF-22', 'MF-23'): continue
        n = int(f['count']); per = float(f['installed_shaft_kW'])/n
        if f['family'] == 'MF-03': per, fl, rpm = float([x for x in fam if x['family'] == 'MF-01'][0]['installed_shaft_kW'])/int([x for x in fam if x['family'] == 'MF-01'][0]['count']), 42, 3000
        else: fl = 42 if '42' in f['size'] else 57 if '57' in f['size'] else 86; rpm = 3000 if f['motor_type'].startswith('BLDC') else 600
        for m in ('NdFeB', 'ferrite'):
            d = pm_variant(per, rpm, fl, m); out.append(dict(family=f['family'], magnet=m, count=n, torque_mNm=round(d['T'], 1), Bg_T=round(d['B'], 2), D_mm=round(d['D'], 1), L_mm=round(d['L'], 1),
                                                           frame=d['frame'], eta=round(d['eta']*100, 1), magnet_g=round(d['mag_g'], 1), RE_g=round(d['RE_g'], 1), fleet_magnet_kg=round(d['mag_g']*n/1000, 2), fleet_RE_kg=round(d['RE_g']*n/1000, 2)))
    return out
def main():
    fam = list(csv.DictReader(open(os.path.join(D, 'MOTOR_FAMILIES.csv')))); rows = []
    for f in fam:
        t, sz, V = f['motor_type'], f['size'], f['voltage']; fid = f['family']; L = [f'# Motor family {fid}: {t}, {sz}, {V}', '', f'Document: AQS-INV-005 sheet {fid}', 'Revision: B', 'Date: 2026-10-25',
                                                                               'Authority: AQS-PLAN-007 task X-INV-02; assumption A-M-126. Generated by `flow_graph/inventory/motor_designs.py`; do not edit this page by hand. This is a study design basis; the design has not been type-tested.', '',
                                                                               '| Rev | Description | Date |', '| --- | --- | --- |', '| A | First issue | 2026-10-15 |',
                                                                               '| B | Purpose and scope added; text rewritten to the documentation style guide (AQS-DOC-002). No design value changed. | 2026-10-25 |', '',
                                                                               '## Purpose and scope', '',
                                                                               f'The plant makes its own motors, and motors of similar design are grouped into families. This sheet gives the design basis of family {fid}, the steps by which it is made in-house, and the work still open before it can be built. The family covers {f["count"]} motors in {f["units"]} units, with {f["installed_shaft_kW"]} kW of installed shaft power in total (motor inventory AQS-INV-001).', '',
                                                                               '## 1. Electromagnetic design basis', '', 'Table 1.1 gives the design quantities and the basis of each.', '', f'Table 1.1. Design basis of {fid}', '']
        Vn = float(re.match(r'(\d+)', V).group(1))
        if t.startswith('induction') or t.startswith('hermetic'):
            m = re.search(r'([\d.]+) kW', sz); kw = float(m.group(1)); fr = re.search(r'IEC (\d+[SLM]?)', sz); fr = fr.group(1) if fr else None
            p = 2 if t.startswith('induction') else 1; d = induction(kw, Vn, p, fr); kind = 'induction' if p == 2 else 'hermetic'
            L += ['| Quantity | Value | Basis |', '| --- | --- | --- |', f'| Rating | {kw} kW, {Vn:.0f} V 3-ph 60 Hz, {2*p} poles, {d["rpm"]} rpm sync | AQS-INV-001 |',
                  f'| Efficiency target | {d["eta"]*100:.1f} % (IE3, 60 Hz, {2*p}-pole) | IEC 60034-30-1:2025 60 Hz table |', f'| Power factor | {d["pf"]:.2f} | assumed (A-M-126) |',
                  f'| Air-gap flux density | {B_D} T | PYRHONEN2014 table 6.3, 0.7-0.9 T |', f'| Linear current density | {d["A"]/1e3:.0f} kA/m | PYRHONEN2014 table 6.3 |',
                  f'| Air-gap diameter x core length | {d["Dg"]:.0f} x {d["L"]:.0f} mm | output equation |', f'| Stator outer diameter | {d["Dout"]:.0f} mm | split ratio 0.55 (4-pole) / 0.50 (2-pole) |',
                  f'| Slots stator / rotor | {d["Qs"]} / {d["Qr"]} | PYRHONEN2014 slot-combination rules |', f'| Turns per phase | {d["N"]} | E = 4.44 f k_w N Phi, E = 0.95 V_ph |',
                  f'| Line current | {d["I"]:.2f} A | S / (sqrt3 V) |', f'| Conductor | {d["cond"]} | J = {J} A/mm2 |',
                  f'| Active mass, steel / copper | {d["m_fe"]:.1f} / {d["m_cu"]:.2f} kg | geometry estimate |']
            if fr in IEC72:
                H, Ds, E, A_, B_, K = IEC72[fr]; L += [f'| Frame | IEC {fr}: H {H}, shaft D {Ds} x E {E}, feet A {A_} x B {B_}, holes K {K} mm | IEC 60072-1 |', f'| Bearings | 2 x {BRG[fr]} | ISO 15 (assumed size) |',
                                                     f'| Lamination OD held by the frame | {"yes, core lengthened" if d["held"] else "no"} (OD <= 0.85 x 2H, A-M-126) | IEC 60072-1 |', f'| Core length / bore | {d["LD"]:.2f} ({"ok" if d.get("fits") else "above 2.5: review"}) | practical limit, A-M-126 |', f'| Slot fit | {"core lengthened x %.2f so slots and yoke fit the OD (rev B)" % d["slot_fit_L_factor"] if d["slot_fit_L_factor"] > 1 else "fits"} | fill 0.40, tooth 1.6 T, yoke 1.5 T (AQS-INV-008) |']
            rows.append(dict(family=fid, type=t, rating=sz, Dg_mm=round(d['Dg']), L_mm=round(d['L']), Dout_mm=round(d['Dout']), turns=d['N'], current_A=round(d['I'], 2), conductor=d['cond'], steel_kg=round(d['m_fe'], 1), copper_kg=round(d['m_cu'], 2), fits=d.get('fits', '-')))
        elif t.startswith('BLDC') and 'actuator' not in t:
            per = float(f['installed_shaft_kW'])/int(f['count']); fl = 42 if '42' in sz else 57; d = pm(per, 3000, fl/1000); kind = 'BLDC'
            L += ['| Quantity | Value | Basis |', '| --- | --- | --- |', f'| Rating | {per*1e3:.0f} W mean, {Vn:.0f} V DC, 3000 rpm | AQS-INV-001 (mean of the family) |', f'| Torque | {d["T"]*1e3:.0f} mN m | P / omega |',
                  f'| Rotor diameter x length | {d["Dg"]:.1f} x {d["L"]:.1f} mm | T = (pi/2) D^2 L A B, A {d["A"]/1e3:.0f} kA/m, B {d["B"]} T (HENDERSHOT2010) |', f'| Flange | {fl} mm | NEMA ICS 16 |']
            rows.append(dict(family=fid, type=t, rating=sz, Dg_mm=round(d['Dg'], 1), L_mm=round(d['L'], 1), Dout_mm=fl, turns='-', current_A=round(per/Vn/0.8, 3), conductor='-', steel_kg='-', copper_kg='-', fits=d['L'] < 3*fl))
        elif t.startswith('stepper'):
            fl = 57 if '57' in sz else 86; kind = 'stepper'; per = float(f['installed_shaft_kW'])/int(f['count'])
            L += ['| Quantity | Value | Basis |', '| --- | --- | --- |', f'| Rating | {per*1e3:.0f} W, {Vn:.0f} V DC chopper drive | AQS-INV-001 |', '| Step | 1.8 deg, 200 full steps | hybrid stepper |', f'| Flange | {fl} mm | NEMA ICS 16 |']
            rows.append(dict(family=fid, type=t, rating=sz, Dg_mm='-', L_mm='-', Dout_mm=fl, turns='-', current_A='-', conductor='-', steel_kg='-', copper_kg='-', fits='-'))
        elif t.startswith('EC '):   # electronically commutated fan motor: permanent-magnet with integrated electronics (A-M-332)
            kind = 'ec_fan'; kw = float(re.search(r'([\d.]+) kW', sz).group(1))
            L += ['| Quantity | Value | Basis |', '| --- | --- | --- |', f'| Rating | {kw:g} kW, {V} | AQS-INV-001 (next rating >= 1.15 x shaft, A-M-117) |', '| Motor | Permanent-magnet motor with integrated commutation and speed-control electronics | A-M-332 |',
                  '| Efficiency class | Not stated: the IEC 60034-30-1 efficiency classes cover line-start induction motors | IEC 60034-30-1 |', '| Electromagnetic design | Not sized here; taken from the selected fan nameplate or datasheet | A-M-332 |']
            rows.append(dict(family=fid, type=t, rating=sz, Dg_mm='-', L_mm='-', Dout_mm='-', turns='-', current_A='-', conductor='-', steel_kg='-', copper_kg='-', fits='-'))
        elif t.startswith('solenoid'):
            per = float(f['installed_shaft_kW'])*1e3/int(f['count']); R = Vn**2/per; kind = 'solenoid'
            L += ['| Quantity | Value | Basis |', '| --- | --- | --- |', f'| Coil power | {per:.1f} W at {Vn:.0f} V DC | AQS-INV-001 |', f'| Coil resistance | {R:.0f} ohm at 20 C | R = V^2 / P |', f'| Current | {per/Vn:.2f} A | P / V |', '| Interface | 22 mm coil, ISO 15218 | ISO 15218 |']
            rows.append(dict(family=fid, type=t, rating=sz, Dg_mm='-', L_mm='-', Dout_mm=22, turns='-', current_A=round(per/Vn, 2), conductor='-', steel_kg='-', copper_kg='-', fits='-'))
        else:
            kind = 'actuator'
            L += ['| Quantity | Value | Basis |', '| --- | --- | --- |', '| Output | quarter turn, ISO 5211 F03, flange torque limit 32 N m | ISO 5211 |', '| Drive | MF-01 BLDC + worm gear | this sheet |']
            rows.append(dict(family=fid, type=t, rating=sz, Dg_mm='-', L_mm='-', Dout_mm='-', turns='-', current_A='-', conductor='-', steel_kg='-', copper_kg='-', fits='-'))
        L += ['', '## 2. Manufacturing plan', '', 'The motor is made in-house in the following steps.', ''] + [f'{i}. {_s.rstrip(".")}.' for i, _s in enumerate(PLAN[kind], 1)] + ['', '## 3. Open items', '', 'Three items remain open. A first article must be built and type-tested (task X-INV-02B). The drawings, the CadQuery model and the bill of materials must be produced (task X-INV-02C). The coefficients that are now taken from within published ranges (A-M-126) are then replaced by the type-test results.']
        open(os.path.join(D, 'motor_families', f'{fid}.md'), 'w').write('\n'.join(L) + '\n')
    with open(os.path.join(D, 'MOTOR_DESIGNS.csv'), 'w', newline='') as fh: w = csv.DictWriter(fh, list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    bad = [r['family'] for r in rows if r['fits'] is False]
    M = ['# Motor family designs', '', 'Document number: AQS-INV-005', 'Revision: A', 'Date: 2026-10-15', 'Authority: AQS-PLAN-007 X-INV-02. Generated by `flow_graph/inventory/motor_designs.py`; one sheet per family in `motor_families/`. A-M-126.', '',
         '| Rev | Description | Date |', '| --- | --- | --- |', '| A | First issue. | 2026-10-15 |', '',
         f'{len(rows)} families. Induction and hermetic: output-equation sizing (PYRHONEN2014), IEC 60072-1 frames, IE3 targets from the IEC 60034-30-1 60 Hz table. BLDC: torque equation (HENDERSHOT2010). Families with core length/bore above 2.5 in their IEC frame: {", ".join(bad) or "none"}.', '',
         '| Family | Type | Rating | Bore mm | Core L mm | OD / flange mm | Turns/ph | I A | Conductor | Steel kg | Cu kg | Fits |', '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    M += [f"| [{r['family']}](motor_families/{r['family']}.md) | {r['type']} | {r['rating']} | {r['Dg_mm']} | {r['L_mm']} | {r['Dout_mm']} | {r['turns']} | {r['current_A']} | {r['conductor']} | {r['steel_kg']} | {r['copper_kg']} | {r['fits']} |" for r in rows]
    C = magnets(fam)
    with open(os.path.join(D, 'MAGNET_COMPARISON.csv'), 'w', newline='') as fh: w = csv.DictWriter(fh, list(C[0].keys())); w.writeheader(); w.writerows(C)
    M += ['', '## Magnet comparison, NdFeB vs bonded ferrite (X-INV-02D, owner 2026-10-15; basis held at NdFeB until Mike decides)', '',
          f"Properties: NdFeB {MAG['NdFeB']['grade']}; ferrite {MAG['ferrite']['grade']} (COEY2010, IEC 60404-8-1). Air gap {GAP} mm, magnet thickness {MAG['NdFeB']['lm']} / {MAG['ferrite']['lm']} mm, leakage {LEAK}, tooth limit {BSAT} T, electric loading 15 kA/m, J 5 A/mm2, iron loss {PFE*100:.0f} % (A-M-130).", '',
          '| Family | Magnet | Count | Torque mN m | B gap T | Rotor D x L mm | Frame | Efficiency % | Magnet g/unit | Rare earth g/unit | Fleet magnet kg | Fleet RE kg |', '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    M += [f"| {c['family']} | {c['magnet']} | {c['count']} | {c['torque_mNm']} | {c['Bg_T']} | {c['D_mm']} x {c['L_mm']} | {c['frame']} | {c['eta']} | {c['magnet_g']} | {c['RE_g']} | {c['fleet_magnet_kg']} | {c['fleet_RE_kg']} |" for c in C]
    M += ['', '| Item | NdFeB | Bonded ferrite |', '| --- | --- | --- |', f"| Material route | {ROUTE['NdFeB']} | {ROUTE['ferrite']} |",
          '| Production line | magnet line with sintering furnace (vacuum/argon), field press, coating; rotor bonding | injection moulding press with orienting fixture; magnets moulded onto the rotor hub, no coating |',
          '| Imported element | none if feedstock magnets suffice; otherwise Nd/Pr and Dy | Sr (or Ba) |',
          '| Motor consequence | smallest frames, highest efficiency | longer rotors or next flange; lower efficiency at equal electric loading |']
    open(os.path.join(D, 'MOTOR_DESIGNS.md'), 'w').write('\n'.join(M) + '\n'); return rows, bad
if __name__ == '__main__':
    rows, bad = main(); print(len(rows), 'families; not fitting', bad)
    for r in rows: print(r)

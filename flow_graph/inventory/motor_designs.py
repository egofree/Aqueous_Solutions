"""X-INV-02 motor family designs (AQS-INV-005). One open design basis and manufacturing plan per family in MOTOR_FAMILIES.csv.
Induction (IEC frames, hermetic): output equation S = C D^2 L n_s with C = (pi^2/sqrt 2) k_w B_delta A [PYRHONEN2014 eq. 6.1-6.3], aspect
chi = L/D = (pi/4p) sqrt(p) [PYRHONEN2014 eq. 6.2], turns from E = 4.44 f k_w N Phi, conductor at J = 5 A/mm2 (TEFC range 3-8 A/mm2,
PYRHONEN2014 table 6.4); IEC 60072-1 frame dimensions; IE3 minimum efficiency IEC 60034-30-1 (50 Hz 4-pole table; 60 Hz table to be
checked on the type test). PM BLDC: T = (pi/2) D^2 L A B [HENDERSHOT2010 ch. 2]. Hybrid steppers NEMA ICS 16 flanges. Solenoids: coil
resistance R = V^2/P. Quarter-turn actuator: ISO 5211 flange torque limit. Coefficients chosen inside the published ranges are A-M-126.
Writes docs-authority/inventory/MOTOR_DESIGNS.md, MOTOR_DESIGNS.csv and motor_families/MF-nn.md. Run: python3 -m flow_graph.inventory.motor_designs"""
import csv, math, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
D = os.path.join(ROOT, 'docs-authority/inventory')
IEC72 = {'63': (63, 11, 23, 100, 80, 7), '71': (71, 14, 30, 112, 90, 7), '80': (80, 19, 40, 125, 100, 10), '90S': (90, 24, 50, 140, 100, 10), '90L': (90, 24, 50, 140, 125, 10),
         '100L': (100, 28, 60, 160, 140, 12), '112M': (112, 28, 60, 190, 140, 12), '132M': (132, 38, 80, 216, 178, 12), '180M': (180, 48, 110, 279, 241, 15)}   # H, D, E, A, B, K mm
IE3 = [(0.12, 60.8), (0.18, 65.9), (0.25, 69.7), (0.37, 73.9), (0.55, 77.1), (0.75, 82.5), (1.1, 84.1), (1.5, 85.3), (2.2, 86.7), (3, 87.7), (4, 88.6), (5.5, 89.6), (7.5, 90.4), (11, 91.4), (15, 92.1), (18.5, 92.6), (22, 93.0)]
AWG = [(n, 0.012668*92**((36 - n)/19.5)**2) for n in range(8, 41)]   # mm^2, ASTM B258
BRG = {'63': '6201-2Z', '71': '6202-2Z', '80': '6204-2Z', '90S': '6205-2Z', '90L': '6205-2Z', '100L': '6206-2Z', '112M': '6306-2Z', '132M': '6308-2Z', '180M': '6310-2Z'}
B_D, KW, J, F = 0.75, 0.92, 5.0, 60.0
def awg(a): return next((f'{n} AWG ({s:.3f} mm2)' for n, s in reversed(AWG) if s >= a), f'{a:.2f} mm2 (parallel strands)')
def induction(kw, V, p, frame=None):
    eta = next((e for k, e in IE3 if k >= kw - 1e-9), 93.0)/100; pf = 0.80 if kw < 4 else 0.84
    A = 20e3 if kw < 1 else 30e3 if kw < 10 else 40e3
    ns = F/p; S = kw*1e3/(eta*pf); C = math.pi**2/math.sqrt(2)*KW*B_D*A
    chi = math.pi/(4*p)*math.sqrt(p); sp = 0.55 if p == 2 else 0.5; Dg = (S/(C*ns*chi))**(1/3); Dout = Dg/sp; held = False
    if frame in IEC72 and Dout > 0.85*2*IEC72[frame][0]/1e3:                 # frame holds the lamination OD; the core lengthens instead
        Dout = 0.85*2*IEC72[frame][0]/1e3; Dg = sp*Dout; held = True
    L = S/(C*ns*Dg**2)
    tau = math.pi*Dg/(2*p); Phi = 2/math.pi*B_D*tau*L; Vph = V/math.sqrt(3); N = 0.95*Vph/(4.44*F*KW*Phi)
    I = S/(math.sqrt(3)*V); a = I/J; Qs = 24 if (frame or '90')[:2] in ('63', '71', '80') else 36; Qr = 22 if Qs == 24 else 28
    m_fe = math.pi/4*(Dout**2 - (Dg*0.33)**2)*L*0.97*7650*0.7; m_cu = 3*N*2*(L + 1.2*tau)*a*1e-6*8960
    out = dict(eta=eta, pf=pf, A=A, Dg=Dg*1e3, L=L*1e3, Dout=Dout*1e3, N=round(N), I=I, cond=awg(a), Qs=Qs, Qr=Qr, m_fe=m_fe, m_cu=m_cu, rpm=round(120*F/(2*p)))
    out['held'] = held; out['LD'] = L/Dg
    if frame in IEC72: out['fits'] = L/Dg <= 2.5
    return out
def pm(kw, rpm, Dmax):
    T = kw*1e3/(rpm*2*math.pi/60); A, B = 15e3, 0.8; DL = T/(math.pi/2*A*B)
    Dg = min(Dmax*0.5, (DL/1.0)**(1/3)); L = DL/Dg**2
    return dict(T=T, Dg=Dg*1e3, L=L*1e3, A=A, B=B)
PLAN = {'induction': ['Laminations: laser-cut then stamped M400-50A (EN 10106) 0.5 mm, stacked and welded/cleated', 'Stator winding: Grade 2 enamelled Cu round wire (IEC 60317-13, class 200) from the wire line; single-layer concentric, class F insulation system (IEC 60085), slot liner NMN', 'VPI in polyester resin, cure', 'Rotor: die-cast aluminium cage (in-house melt), skewed one slot pitch', 'Shaft: C45 (EN 10083-2) turned and ground; keyway to IEC 60072-1', 'Frame: cast aluminium (A356) or cast iron above IEC 132, machined; end shields; IP55 (IEC 60034-5); IC 411 fan cooling (IEC 60034-6)', 'Bearings from the X-INV-05 bearing families; balance to ISO 21940-11 G2.5', 'Routine test IEC 60034-1: winding resistance, no-load, locked-rotor, hipot 2U + 1000 V; first-article type test IEC 60034-2-1 (efficiency) and IEC 60034-9 (noise)'],
        'hermetic': ['Stator and rotor as the induction plan, without frame, shaft and fan; 2-pole; winding varnish and lead insulation compatible with the refrigerant and POE oil (UL 60335-2-34 / IEC 60335-2-34 Annex AA)', 'Shrink-fit into the compressor shell (scroll line X-MFG-35)', 'Hipot and insulation resistance after shell welding; locked-rotor and thermal protector test per IEC 60335-2-34'],
        'BLDC': ['Stator: 0.35 mm NO20 or M270-35A laminations (EN 10106), 12 slots, concentrated tooth coils', 'Rotor: 8-pole surface magnets; NdFeB requires rare-earth supply (review item), bonded ferrite alternative at about 0.4 of the torque density', 'Hall sensors or sensorless back-EMF commutation; driver from the X-INV-05 BLDC driver family', 'Flange to NEMA ICS 16; housing extruded aluminium', 'Test: back-EMF constant, no-load current, torque-speed curve, hipot 500 V + 2U'],
        'stepper': ['Hybrid 2-phase 1.8 deg: 8-pole stator, 50-tooth rotor, axially magnetised NdFeB ring between two toothed caps', 'Laminations 0.35 mm (EN 10106); bifilar or unipolar windings from the wire line', 'Flange to NEMA ICS 16', 'Test: holding torque, step accuracy (+/- 5 %), resistance and inductance'],
        'solenoid': ['Coil: class H enamelled wire (IEC 60317-13) on a PA66-GF bobbin, 22 mm ISO 15218 interface', 'Plunger and frame: ferritic stainless 430F', 'Encapsulation in epoxy; DIN EN 175301-803 connector', 'Test: coil resistance, pull-in voltage at 85 % rated, insulation 1000 V'],
        'actuator': ['BLDC motor of family MF-01 driving a worm gear (bronze wheel, steel worm)', 'Output to ISO 5211 F03 square, end stops and position switches', 'Housing PA66-GF or Al, IP67', 'Test: breakaway torque at the ISO 5211 F03 rating, travel time, cycle life sample']}
def main():
    fam = list(csv.DictReader(open(os.path.join(D, 'MOTOR_FAMILIES.csv')))); rows = []
    for f in fam:
        t, sz, V = f['motor_type'], f['size'], f['voltage']; fid = f['family']; L = [f'# Motor family {fid}: {t}, {sz}, {V}', '', f'Document: AQS-INV-005 sheet {fid}. Generated by `flow_graph/inventory/motor_designs.py`. Study design basis, not a type-tested design. A-M-126.', '',
                                                                               f"Population: {f['count']} items in {f['units']} units, {f['installed_shaft_kW']} kW installed shaft power (AQS-INV-001).", '', '## 1. Electromagnetic design basis', '']
        Vn = float(re.match(r'(\d+)', V).group(1))
        if t.startswith('induction') or t.startswith('hermetic'):
            m = re.search(r'([\d.]+) kW', sz); kw = float(m.group(1)); fr = re.search(r'IEC (\d+[SLM]?)', sz); fr = fr.group(1) if fr else None
            p = 2 if t.startswith('induction') else 1; d = induction(kw, Vn, p, fr); kind = 'induction' if p == 2 else 'hermetic'
            L += ['| Quantity | Value | Basis |', '| --- | --- | --- |', f'| Rating | {kw} kW, {Vn:.0f} V 3-ph 60 Hz, {2*p} poles, {d["rpm"]} rpm sync | AQS-INV-001 |',
                  f'| Efficiency target | {d["eta"]*100:.1f} % (IE3) | IEC 60034-30-1 |', f'| Power factor | {d["pf"]:.2f} | assumed (A-M-126) |',
                  f'| Air-gap flux density | {B_D} T | PYRHONEN2014 table 6.3, 0.7-0.9 T |', f'| Linear current density | {d["A"]/1e3:.0f} kA/m | PYRHONEN2014 table 6.3 |',
                  f'| Air-gap diameter x core length | {d["Dg"]:.0f} x {d["L"]:.0f} mm | output equation |', f'| Stator outer diameter | {d["Dout"]:.0f} mm | split ratio 0.55 (4-pole) / 0.50 (2-pole) |',
                  f'| Slots stator / rotor | {d["Qs"]} / {d["Qr"]} | PYRHONEN2014 slot-combination rules |', f'| Turns per phase | {d["N"]} | E = 4.44 f k_w N Phi, E = 0.95 V_ph |',
                  f'| Line current | {d["I"]:.2f} A | S / (sqrt3 V) |', f'| Conductor | {d["cond"]} | J = {J} A/mm2 |',
                  f'| Active mass, steel / copper | {d["m_fe"]:.1f} / {d["m_cu"]:.2f} kg | geometry estimate |']
            if fr in IEC72:
                H, Ds, E, A_, B_, K = IEC72[fr]; L += [f'| Frame | IEC {fr}: H {H}, shaft D {Ds} x E {E}, feet A {A_} x B {B_}, holes K {K} mm | IEC 60072-1 |', f'| Bearings | 2 x {BRG[fr]} | ISO 15 (assumed size) |',
                                                     f'| Lamination OD held by the frame | {"yes, core lengthened" if d["held"] else "no"} (OD <= 0.85 x 2H, A-M-126) | IEC 60072-1 |', f'| Core length / bore | {d["LD"]:.2f} ({"ok" if d.get("fits") else "above 2.5: review"}) | practical limit, A-M-126 |']
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
        elif t.startswith('solenoid'):
            per = float(f['installed_shaft_kW'])*1e3/int(f['count']); R = Vn**2/per; kind = 'solenoid'
            L += ['| Quantity | Value | Basis |', '| --- | --- | --- |', f'| Coil power | {per:.1f} W at {Vn:.0f} V DC | AQS-INV-001 |', f'| Coil resistance | {R:.0f} ohm at 20 C | R = V^2 / P |', f'| Current | {per/Vn:.2f} A | P / V |', '| Interface | 22 mm coil, ISO 15218 | ISO 15218 |']
            rows.append(dict(family=fid, type=t, rating=sz, Dg_mm='-', L_mm='-', Dout_mm=22, turns='-', current_A=round(per/Vn, 2), conductor='-', steel_kg='-', copper_kg='-', fits='-'))
        else:
            kind = 'actuator'
            L += ['| Quantity | Value | Basis |', '| --- | --- | --- |', '| Output | quarter turn, ISO 5211 F03, flange torque limit 32 N m | ISO 5211 |', '| Drive | MF-01 BLDC + worm gear | this sheet |']
            rows.append(dict(family=fid, type=t, rating=sz, Dg_mm='-', L_mm='-', Dout_mm='-', turns='-', current_A='-', conductor='-', steel_kg='-', copper_kg='-', fits='-'))
        L += ['', '## 2. Manufacturing plan (in-house)', ''] + [f'{i}. {s}' for i, s in enumerate(PLAN[kind], 1)] + ['', '## 3. Open items', '', '- First-article build and type test (X-INV-02B).', '- Drawings, CadQuery model and BOM (X-INV-02C).\n- Coefficients inside the published ranges (A-M-126) are replaced by the type-test result.']
        open(os.path.join(D, 'motor_families', f'{fid}.md'), 'w').write('\n'.join(L) + '\n')
    with open(os.path.join(D, 'MOTOR_DESIGNS.csv'), 'w', newline='') as fh: w = csv.DictWriter(fh, list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    bad = [r['family'] for r in rows if r['fits'] is False]
    M = ['# Motor family designs', '', 'Document number: AQS-INV-005', 'Revision: A', 'Date: 2026-10-15', 'Authority: AQS-PLAN-007 X-INV-02. Generated by `flow_graph/inventory/motor_designs.py`; one sheet per family in `motor_families/`. A-M-126.', '',
         '| Rev | Description | Date |', '| --- | --- | --- |', '| A | First issue. | 2026-10-15 |', '',
         f'{len(rows)} families. Induction and hermetic: output-equation sizing (PYRHONEN2014), IEC 60072-1 frames, IE3 targets (IEC 60034-30-1). BLDC: torque equation (HENDERSHOT2010). Families with core length/bore above 2.5 in their IEC frame: {", ".join(bad) or "none"}.', '',
         '| Family | Type | Rating | Bore mm | Core L mm | OD / flange mm | Turns/ph | I A | Conductor | Steel kg | Cu kg | Fits |', '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    M += [f"| [{r['family']}](motor_families/{r['family']}.md) | {r['type']} | {r['rating']} | {r['Dg_mm']} | {r['L_mm']} | {r['Dout_mm']} | {r['turns']} | {r['current_A']} | {r['conductor']} | {r['steel_kg']} | {r['copper_kg']} | {r['fits']} |" for r in rows]
    open(os.path.join(D, 'MOTOR_DESIGNS.md'), 'w').write('\n'.join(M) + '\n'); return rows, bad
if __name__ == '__main__':
    rows, bad = main(); print(len(rows), 'families; not fitting', bad)
    for r in rows: print(r)

"""X-INV-02B desk package: first-article drawings, build traveller and type-test rig for each X-INV-02 motor family
(AQS-INV-008, A-M-218). Induction families (MF-04..MF-20): stator and rotor lamination drawing from the AQS-INV-005 design
(air gap PYRHONEN2014 ch. 6, slot area from the winding at fill 0.40, tooth and yoke at 1.6 / 1.5 T), frame outline to
IEC60072_1_1991 where the sheet gives the frame. Writes docs-authority/drawings/motor_fa/MF-nn.svg, MOTOR_FIRST_ARTICLE.md and
inventory/MOTOR_FA.json. The builds and type tests (IEC60034_1_2022, IEC60034_2_1_2014) remain open."""
import csv, json, math, os, re, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(R); sys.path.insert(0, R)
from flow_graph.param import drivers as DR   # U4b: design literals single-sourced from drivers.json (A-M-218)
_d = DR.load(); v = lambda k: DR.val(_d, k)
D = list(csv.DictReader(open('docs-authority/inventory/MOTOR_DESIGNS.csv'))); os.makedirs('docs-authority/drawings/motor_fa', exist_ok=True)
FILL, BT, BY, KFE = v('MFG.tools-metal-forming-train.mfa_slot_fill'), v('MFG.tools-metal-forming-train.mfa_tooth_T'), v('MFG.tools-metal-forming-train.mfa_yoke_T'), v('MFG.tools-metal-forming-train.mfa_stacking_factor')
def sheet(fam):
    t = open(f'docs-authority/inventory/motor_families/{fam}.md').read(); g = lambda k: (re.search(r'\| ' + k + r' \| ([^|]+) \|', t) or [None, ''])[1].strip()
    return t, g
out = []
for d in D:
    fam = d['family']; t, g = sheet(fam); rat = g('Rating'); pop = (re.search(r'Population: (\d+) items', t) or [0, '0'])[1]
    r = dict(family=fam, type=d['type'], rating=d['rating'], items=int(pop))
    if 'induction' in d['type']:
        P = float(re.search(r'([\d.]+) kW', rat).group(1))*1000; poles = int(re.search(r'(\d+) poles', rat).group(1)); p = poles//2
        Dg, L, Do = float(d['Dg_mm']), float(d['L_mm']), float(d['Dout_mm']); N = int(d['turns']); I = float(d['current_A'])
        Qs, Qr = [int(x) for x in g('Slots stator / rotor').split('/')]; Bd = float(g('Air-gap flux density').split()[0]); pf = float(g('Power factor') or v('MFG.tools-metal-forming-train.mfa_pf_default'))
        ac = float(re.search(r'\(([\d.]+) mm2\)', d['conductor']).group(1))
        dl = 0.18 + 0.006*P**0.4 if p > 1 else 0.2 + 0.01*P**0.4                       # mm, PYRHONEN2014 ch. 6
        zQ = 2*3*N/Qs; As = zQ*ac*v('MFG.tools-metal-forming-train.mfa_enamel_margin')/FILL                                               # mm2 per slot, enamel 15 %
        tau_s = math.pi*Dg/Qs; bt = Bd*tau_s/(KFE*BT); tau_p = math.pi*Dg/poles
        Phi = 2/math.pi*Bd*tau_p*L*1e-6; hy = Phi/(2*KFE*L*1e-3*BY)*1000
        # parallel-tooth slot: width grows with radius; solve depth hs from area
        b1 = tau_s - bt; k = 2*math.pi/Qs; hs = (-b1 + math.sqrt(b1**2 + 2*k*As))/k
        Do_calc = Dg + dl + 2*(hs + hy)
        fL = 1.0
        if Do_calc > Do*v('MFG.tools-metal-forming-train.mfa_od_tol'):  # longer core: N and slot area fall as 1/L at the same E and B; yoke depth unchanged
            lo, hi = 1.0, 4.0
            for _ in range(40):
                fL = (lo + hi)/2; A2 = As/fL; h2 = (-b1 + math.sqrt(b1**2 + 2*k*A2))/k
                lo, hi = (fL, hi) if Dg + dl + 2*(h2 + hy) > Do*v('MFG.tools-metal-forming-train.mfa_od_tol') else (lo, fL)
            fL = hi
        Ibar = 2*3*N*v('MFG.tools-metal-forming-train.mfa_bar_current_factor')*I*pf/Qr; Abar = Ibar/v('MFG.tools-metal-forming-train.mfa_bar_J_A_mm2')                                        # A, mm2 at 5 A/mm2 die-cast Al
        fr = g('Frame'); fm = re.search(r'H (\d+), shaft D (\d+) x E (\d+), feet A (\d+) x B (\d+), holes K (\d+)', fr)
        r.update(P_kW=P/1000, poles=poles, Dg=Dg, L=L, Dout=Do, airgap_mm=round(dl, 3), Dbore=round(Dg + dl, 2), Qs=Qs, Qr=Qr, slot_area_mm2=round(As, 1), tooth_mm=round(bt, 2),
                 slot_depth_mm=round(hs, 2), yoke_mm=round(hy, 2), Dout_check_mm=round(Do_calc, 1), od_ok=Do_calc <= Do*v('MFG.tools-metal-forming-train.mfa_od_tol'), L_req_mm=round(L*fL), N_req=round(N/fL), bar_mm2=round(Abar, 1), ring_mm2=round(Abar*Qr/(2*math.pi*p)*0.5, 1),
                 frame=fr, T_Nm=round(P/(2*math.pi*(2*v('MFG.tools-metal-forming-train.mfa_line_hz')*60/poles)*v('MFG.tools-metal-forming-train.mfa_rated_speed_frac')/60), 1))
        H, Ds, E, A, B, K = [int(x) for x in fm.groups()] if fm else [None]*6
        sc = 150/Do; cx, cy = 170, 180
        svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="760" height="380" font-family="sans-serif" font-size="10">',
               f'<text x="10" y="16" font-weight="bold">{fam} first article: stator / rotor lamination (M400-50A, 0.5 mm) and {fr.split(":")[0] if fr else "frame"} outline. AQS-INV-008 rev A, A-M-218. Not to scale outside the dimensions shown.</text>',
               f'<circle cx="{cx}" cy="{cy}" r="{Do/2*sc:.1f}" fill="#ccc" stroke="#000"/>', f'<circle cx="{cx}" cy="{cy}" r="{(Dg/2 + dl/2 + hs)*sc:.1f}" fill="none" stroke="#666" stroke-dasharray="3,2"/>']
        for i in range(Qs):
            a = 2*math.pi*i/Qs; r0 = (Dg + dl)/2; r1 = r0 + hs
            svg.append(f'<line x1="{cx + r0*sc*math.cos(a):.1f}" y1="{cy + r0*sc*math.sin(a):.1f}" x2="{cx + r1*sc*math.cos(a):.1f}" y2="{cy + r1*sc*math.sin(a):.1f}" stroke="#fff" stroke-width="{max(1, (tau_s - bt)*sc):.1f}"/>')
        svg += [f'<circle cx="{cx}" cy="{cy}" r="{(Dg + dl)/2*sc:.1f}" fill="#fff" stroke="#000"/>', f'<circle cx="{cx}" cy="{cy}" r="{(Dg - dl)/2*sc:.1f}" fill="#bbb" stroke="#000"/>']
        for i in range(Qr):
            a = 2*math.pi*(i + 0.5)/Qr; rb = (Dg - dl)/2 - math.sqrt(Abar)/2 - 0.5
            svg.append(f'<circle cx="{cx + rb*sc*math.cos(a):.1f}" cy="{cy + rb*sc*math.sin(a):.1f}" r="{max(1, math.sqrt(Abar/math.pi)*sc):.1f}" fill="#999"/>')
        if Ds: svg.append(f'<circle cx="{cx}" cy="{cy}" r="{Ds/2*sc:.1f}" fill="#555"/>')
        lines = [f'Stator OD {Do:.0f} mm (check {Do_calc:.1f} mm from slot + yoke: {"fits" if Do_calc <= Do*v("MFG.tools-metal-forming-train.mfa_od_tol") else "EXCEEDS, lengthen core"})', f'Bore {Dg + dl:.2f} mm; rotor OD {Dg - dl:.2f} mm; air gap {dl:.2f} mm',
                 f'Core length {L:.0f} mm, stacking factor {KFE}', f'Stator {Qs} slots: area {As:.0f} mm2 at fill {FILL}, depth {hs:.1f} mm, parallel tooth {bt:.2f} mm ({BT} T)', f'Yoke {hy:.1f} mm ({BY} T)',
                 f'Winding {N} turns/phase, {zQ:.0f} conductors/slot, {d["conductor"]} class 200 enamel', f'Rotor {Qr} die-cast Al bars {Abar:.0f} mm2, end ring {r["ring_mm2"]:.0f} mm2, skew 1 slot',
                 (f'Frame IEC H {H}, feet A {A} x B {B}, holes K {K}, shaft D {Ds} k6 x E {E}' if H else f'Frame: {fr}'), f'Rated torque {r["T_Nm"]} N m; bearings {g("Bearings") or "per sheet"}']
        for j, s in enumerate(lines): svg.append(f'<text x="360" y="{50 + 16*j}">{s}</text>')
        if H:  # side outline
            ox, oy, s2 = 360, 360, 0.6
            svg += [f'<rect x="{ox}" y="{oy - (H + Do/2)*s2:.1f}" width="{(L + 120)*s2:.1f}" height="{Do*s2:.1f}" fill="none" stroke="#000"/>', f'<rect x="{ox + (L + 120)*s2:.1f}" y="{oy - (H + Ds/2)*s2:.1f}" width="{E*s2:.1f}" height="{Ds*s2:.1f}" fill="#555"/>',
                    f'<line x1="{ox - 20}" y1="{oy}" x2="{ox + (L + 200)*s2:.1f}" y2="{oy}" stroke="#000"/>', f'<text x="{ox + (L + 120 + E)*s2 + 6:.1f}" y="{oy - H*s2:.1f}">shaft centre H {H}</text>']
        svg.append('</svg>'); open(f'docs-authority/drawings/motor_fa/{fam}.svg', 'w').write('\n'.join(svg))
    out.append(r)
IND = [r for r in out if 'P_kW' in r]; Tmax = max(r['T_Nm'] for r in IND); Pmax = max(r['P_kW'] for r in IND)
json.dump(out, open('docs-authority/inventory/MOTOR_FA.json', 'w'), indent=1)
md = ['# Motor first articles: drawings, traveller and type-test rig', '', 'Document number: AQS-INV-008', 'Revision: A', 'Date: 2026-10-16',
      'Authority: AQS-PLAN-007 X-INV-02B. Generated by `docs-authority/_motor_fa.py` from AQS-INV-005 (`inventory/MOTOR_DESIGNS.csv`, `inventory/motor_families/`). A-M-218. Desk package; the builds and type tests are the open part of X-INV-02B.', '',
      f'{len(out)} families; {len(IND)} induction families with lamination and frame drawings in `docs-authority/drawings/motor_fa/`. Slot, tooth and yoke are derived again here from the winding (fill {FILL}, tooth {BT} T, yoke {BY} T, stacking {KFE}); a family whose derived again OD exceeds its sheet OD by more than 2 % is flagged for a longer core before laminations are cut.', '',
      '## 1. Induction first-article dimensions', '', '| Family | kW | Poles | Bore mm | Gap mm | Core mm | Qs/Qr | Slot mm2 | Slot depth mm | Tooth mm | Yoke mm | OD sheet / check mm | Bar mm2 | T N m | Items |', '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
for r in IND:
    md.append(f"| {r['family']} | {r['P_kW']} | {r['poles']} | {r['Dbore']} | {r['airgap_mm']} | {r['L']:.0f} | {r['Qs']}/{r['Qr']} | {r['slot_area_mm2']} | {r['slot_depth_mm']} | {r['tooth_mm']} | {r['yoke_mm']} | {r['Dout']:.0f} / {r['Dout_check_mm']}{'' if r['od_ok'] else ' FLAG'} | {r['bar_mm2']} | {r['T_Nm']} | {r['items']} |")
fl = [r['family'] for r in IND if not r['od_ok']]
md += ['', f"Flagged (OD check over sheet OD): {', '.join(fl) if fl else 'none'}. For a flagged family the first article keeps the sheet OD and bore and lengthens the core: at the same back-EMF and flux density the turns, and so the slot area, fall as 1/L. Required core and turns: " + ', '.join(f"{r['family']} {r['L']:.0f} -> {r['L_req_mm']} mm, {r['N_req']} turns" for r in IND if not r['od_ok']) + ". The AQS-INV-005 sheet is revised to these before laminations are cut.", '',
       '## 2. Other families', '', '| Family | Type | Rating | Items | First article |', '|---|---|---|---|---|']
for r in out:
    if 'P_kW' in r: continue
    fa = {'BLDC': 'stator stack + bonded NdFeB rotor, hall board; back-EMF constant and torque constant on the rig', 'BLDC actuator': 'BLDC + harmonic or spur gearhead to ISO 5211 F03 flange; stall torque and cycle life 10,000 strokes',
          'solenoid': 'bobbin coil, plunger and frame; pull-in and drop-out voltage, coil temperature rise at 110 % V', 'stepper': 'hybrid stepper stack, 1.8 deg; holding torque and pull-out torque curve'}.get(r['type'], 'per sheet')
    md.append(f"| {r['family']} | {r['type']} | {r['rating']} | {r['items']} | {fa} |")
md += ['', '## 3. Build traveller (each induction family, one first article)', '',
       '| Step | Operation | Inspection / hold point | Acceptance |', '|---|---|---|---|',
       '| 1 | Laminations laser-cut from M400-50A 0.5 mm to the drawing (a progressive die only after the first article passes) | first-off dimensional | bore and OD within 0.05 mm, burr < 0.03 mm |',
       '| 2 | Stack, press and weld / cleat stator; skew and stack rotor | stack length and squareness | stacking factor >= 0.96 |',
       '| 3 | Die-cast rotor cage in in-house Al | X-ray or sectioned sample bar | porosity < 2 % by area |',
       '| 4 | Slot liners, insert winding, connect, lace | turns count, resistance balance | phase resistance within 2 % |',
       '| 5 | VPI and cure | surge comparison and hipot before VPI and after | IEC 60034-1 withstand 1000 V + 2 U, 1 min |',
       '| 6 | Machine shaft (C45), press rotor, balance | runout, balance | G2.5 (ISO 21940-11) |',
       '| 7 | Frame, end shields, bearings, fan, terminal box | air gap at 4 points | gap within 10 % of nominal |',
       '| 8 | Routine tests (IEC60034_1_2022) | winding resistance, no-load, locked rotor, hipot | per IEC 60034-1 |',
       '| 9 | Type test (IEC60034_2_1_2014 method 2-1-1B) on the rig below | efficiency, temperature rise, noise (IEC 60034-9) | efficiency >= sheet IE3 target; class B rise |', '',
       '## 4. Type-test rig (one rig for all families)', '',
       f"- Load machine: an in-house MF-18 (18.5 kW, IEC 180M) run as a regenerating load on a back-to-back VFD pair with common DC bus, so only the losses are drawn from the grid; the largest family (MF-04, {Pmax:.0f} kW hermetic) is tested at 85 % of rating on this load or with a second MF-18 coupled in tandem.",
       f"- Torque transducer: in-line, 200 N m range (largest family rated torque {Tmax} N m), class 0.2 %; speed encoder 1024 ppr.",
       '- Power analyser: 3-phase, class 0.1 %, harmonics to the 50th, with the temperature-rise thermocouples (6 per winding) and resistance-after-shutdown timer.',
       '- Bed: cast or welded steel T-slot bed, adjustable centre-height adapter plates for IEC 63 to 180, jaw couplings sized for the transducer, guard to ISO 14120.',
       '- Supply: 480 V 3-ph adjustable through the VFD for the no-load voltage sweep (IEC 60034-2-1 no-load test at 110 % to 30 % voltage); DC supply for the winding resistance.', '',
       'Output: measured efficiency, power factor, slip and temperature rise per family replace the A-M-126 coefficients (power factor, Bd, A) through `flow_graph/inventory/motor_designs.py`.']
open('docs-authority/MOTOR_FIRST_ARTICLE.md', 'w').write('\n'.join(md) + '\n')
print(len(out), len(IND), fl, Tmax)

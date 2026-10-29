"""X-INV-03-WF-01..26 open wire specifications and production plans (AQS-INV-007, A-M-217). One sheet per family in
inventory/WIRE_FAMILIES.csv: conductor (ASTM B3 soft Cu, ASTM B8 class B stranding), insulation and jacket to the listed
standard, finished diameter, copper and compound mass for the inventory length, the drawing schedule on WIRE_DRAW from 8 mm
ASTM B49 rod, and the routine and type tests. Cross-section drawings to docs-authority/drawings/wire/WF-nn.svg.
Desk package for the build; the production runs and type tests remain open (the X-INV-03-WF tasks stay unticked)."""
import csv, math, os, re, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(R); sys.path.insert(0, R)
from flow_graph.param import drivers as DR   # U4b: process literals single-sourced from drivers.json (A-M-217)
_d = DR.load(); v = lambda k: DR.val(_d, k)
FAM = list(csv.DictReader(open('docs-authority/inventory/WIRE_FAMILIES.csv')))
RHO = v('MFG.tools-metal-forming-train.metal-forming.WIRE_DRAW.ws_cu_rho_ohm_mm2_m'); CU = v('MFG.tools-metal-forming-train.metal-forming.WIRE_DRAW.ws_cu_density_g_cm3'); ROD_D = v('MFG.tools-metal-forming-train.metal-forming.WIRE_DRAW.ws_rod_D_mm'); RED = v('MFG.tools-metal-forming-train.metal-forming.WIRE_DRAW.ws_pass_reduction')  # ohm mm2/m (ASTM_B3_2013); g/cm3; mm rod (ASTM_B49_2020); area reduction per pass (A-M-217)
def area(sz):
    m = re.match(r'([\d/]+)\s*(AWG|kcmil)', sz); v, u = m.groups()
    if u == 'kcmil': return float(v)*0.506707
    n = -(int(v.split('/')[0]) - 1) if '/' in v else int(v)
    return math.pi/4*(0.127*92**((36 - n)/39))**2
def strands(sz, a, kind):
    if 'kcmil' in sz: return 37 if a <= 253.4 else 37 if a <= 506.7 else 61
    if a >= 42.4: return 19          # 1 AWG to 4/0 (ASTM_B8_2023 class B)
    return 7                          # 14 to 2 AWG; 16 and 18 AWG made 7-wire for flex (ASTM_B8_2023)
def insulation(f, a):
    t = f['insulation']; sz = f['size']
    if 'bare' in t: return [], 'bare, no covering', 'ASTM_B3_2013 / ASTM_B8_2023'
    if 'MV-105' in t: return [('conductor shield, semiconducting', 0.38), ('EPR insulation, 15 kV 133 %', 5.59), ('insulation shield, semiconducting', 0.76), ('Cu tape shield 0.127 mm, 25 % overlap', 0.25), ('PVC jacket', 2.03)], 'MV-105', 'UL1072_2006'
    if 'PV Wire' in t: return [('XLPE insulation, 2 kV (UL 4703 1000/2000 V wall for 14-10 AWG, 75 mil; confirmed 2026-10-16)', 1.91)], 'PV Wire 2 kV', 'UL4703_2014'
    if 'THHN' in t:
        tt = 0.38 if a < 5 else 0.51 if a < 8 else 0.76 if a < 20 else 1.02
        return [('PVC insulation', tt), ('nylon jacket', 0.10 if a < 8 else 0.13)], 'THHN/THWN-2', 'UL83_2017'
    if 'TFFN' in t or ('shielded pair' in t):
        return [('PVC insulation', 0.38), ('nylon jacket', 0.10)] if 'TFFN' in t else [('PVC insulation', 0.38)], 'TFFN' if 'TFFN' in t else 'PLTC shielded pair', 'UL66_2015' if 'TFFN' in t else 'UL1581_2019'
    tx = 0.76 if a < 6 else 1.14 if a < 40 else 1.40 if a < 110 else 1.65
    return [('XLPE insulation (XHHW-2)' + (', green' if 'green' in t else ''), tx)], 'XHHW-2', 'UL44_2018'
def cable(f):
    t = f['insulation'] + ' ' + f['type']
    if 'TC-ER' in t and '2-cond' in t: return 2, 'TC-ER 2-conductor'
    if 'TC-ER' in t: return 4, 'TC-ER 3 + green ground'
    if '3-pair' in t: return 6, '3 twisted pairs, overall Al/PET foil and 7-wire drain, PVC jacket'
    if 'pair' in t: return 2, 'twisted pair, Al/PET foil and drain, PVC jacket'
    return 1, 'single conductor'
def jacket(D):  # TC-ER and control-cable jackets, UL1277_2019 table (minimum average by diameter under jacket; confirmed 2026-10-16)
    return 1.14 if D <= 10.80 else 1.52 if D <= 17.78 else 2.03 if D <= 38.10 else 2.79 if D <= 63.50 else 3.56
os.makedirs('docs-authority/drawings/wire', exist_ok=True)
rows = []; sheets = []
for f in FAM:
    a = area(f['size']); n = strands(f['size'], a, f['type']); ds = math.sqrt(4*a/n/math.pi)
    k = 1.0 if n == 1 else 1.02 if n <= 19 else 1.03
    Dc = ds*(3 if n == 7 else 5 if n == 19 else 7 if n == 37 else 9)
    lay, ins, std = insulation(f, a); D = Dc + 2*sum(t for _, t in lay)
    nc, form = cable(f); Dj = None
    if nc > 1:
        lay_d = D*(1 if nc == 1 else 2 if nc == 2 else 2.414 if nc == 4 else 3.0 if nc == 6 else 2)  # circle-packing lay factors (4 cores 1 + sqrt2)
        Dj = lay_d + 2*jacket(lay_d)
    L = float(f['conductor_m']); cu_kg = a*L*CU/1000*k
    ins_kg = sum(math.pi*((Dc/2 + sum(t for _, t in lay[:i + 1]))**2 - (Dc/2 + sum(t for _, t in lay[:i]))**2)*L*(1.40 if 'PVC' in nm else 1.15 if 'nylon' in nm else 0.95 if ('XLPE' in nm or 'EPR' in nm) else 1.2)/1000 for i, (nm, _) in enumerate(lay))
    passes = max(0, math.ceil(math.log((math.pi/4*ROD_D**2)/(math.pi/4*ds**2))/-math.log(1 - RED)))
    R20 = RHO/a*1000*k
    rows.append(dict(fam=f['family'], size=f['size'], a=a, n=n, ds=ds, Dc=Dc, D=D, Dj=Dj, nc=nc, form=form, ins=ins, std=std, L=L, cu=cu_kg, ik=ins_kg, passes=passes, R20=R20, lay=lay, f=f))
    # cross-section drawing
    sc = 120/max(Dj or D, 1); cx = cy = 80
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="420" height="170" font-family="sans-serif" font-size="10">',
           f'<text x="170" y="20" font-weight="bold">{f["family"]} {f["size"]} {ins}</text>']
    r = (Dj or D)/2*sc
    if Dj: svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r:.1f}" fill="#ddd" stroke="#000"/>')
    rr = Dc/2 + sum(t for _, t in lay)
    for i in range(len(lay), -1, -1):
        rad = (Dc/2 + sum(t for _, t in lay[:i]))*sc*(0.45 if Dj else 1)
        svg.append(f'<circle cx="{cx}" cy="{cy}" r="{rad:.1f}" fill="{"#c87533" if i == 0 else ["#2c7", "#555", "#333", "#b80", "#222"][(i - 1) % 5]}" stroke="#000"/>')
    yy = 40
    for line in [f'conductor {a:.3f} mm2, {n} x {ds:.3f} mm soft Cu, ASTM B8 class B' if n > 1 else f'conductor {a:.3f} mm2 solid'] + [f'{nm} {t:.2f} mm' for nm, t in lay] + \
                [f'core OD {D:.2f} mm'] + ([f'{form}, jacket OD {Dj:.1f} mm'] if Dj else []) + [f'R20 {R20:.3f} ohm/km; {std}']:
        svg.append(f'<text x="170" y="{yy}">{line}</text>'); yy += 14
    svg.append('</svg>'); open(f'docs-authority/drawings/wire/{f["family"]}.svg', 'w').write('\n'.join(svg))
tot_cu = sum(r['cu'] for r in rows); tot_i = sum(r['ik'] for r in rows)
md = ['# Wire family specifications and production plans', '', 'Document number: AQS-INV-007', 'Revision: D', 'Date: 2026-10-29',
      'Generated by `docs-authority/_wire_specs.py` from `inventory/WIRE_FAMILIES.csv` (AQS-INV-002), with a JSON twin `docs-authority/inventory/WIRE_SPECS.json` and one cross-section drawing per family. Do not edit by hand; change the generator or its inputs and run `python3 -m flow_graph.param.regen`.',
      'Authority: tasks X-INV-03-WF of AQS-PLAN-007; drawing rule A-M-217. Study. Not a PE stamp.', '',
      '| Rev | Description | Date |', '| --- | --- | --- |',
      '| A | First issue: one specification and production plan for each wire family, with a cross-section drawing of each | 2026-10-16 |',
      '| B | Checked values: the PV Wire 2 kV 10 AWG wall confirmed to the UL 4703 figure of 75 mil; the TC-ER and control-cable jacket walls confirmed to the UL 1277 table | 2026-10-16 |',
      '| C | Evidence issue for the family tasks; the task range label corrected after a family was retired. Production runs and type tests stay open. | 2026-10-21 |',
      '| D | Purpose and scope added; the production steps and family sheets written as sentences; tables numbered | 2026-10-29 |', '',
      '## 1. Purpose and scope', '',
      'This page gives the specification and production plan of each wire family in the wire inventory AQS-INV-002. A wire family is the wire or cable of one type, size and covering. For each family the page gives the conductor, the covering layers, the cable make-up, the quantities and the standard. The production runs and type tests are the open part of each family task.', '',
      '## 2. Summary', '',
      f'The inventory has {len(rows)} families with {sum(r["L"] for r in rows)/1000:.1f} km of conductor, {tot_cu:,.0f} kg of copper and {tot_i:,.0f} kg of insulation and jacket compound; cable jackets are not included in the compound mass. The conductor is soft annealed copper of 100 % IACS conductivity to [ASTM_B3_2013], with class B concentric stranding to [ASTM_B8_2023]. It is drawn on WIRE_DRAW from 8 mm redraw rod to [ASTM_B49_2020], with an area reduction of {RED:.0%} per pass. The cross-section drawings are `docs-authority/drawings/wire/WF-nn.svg`.', '',
      'Table 2.1 lists the families.', '', 'Table 2.1. Wire families', '',
      '| Family | Size | mm2 | Strands | Wire mm | Passes | Covering | Core OD mm | Cable | Cable OD mm | Length m | Cu kg | Compound kg | R20 ohm/km | Standard |', '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
for r in rows:
    md.append(f"| {r['fam']} | {r['size']} | {r['a']:.3f} | {r['n']} | {r['ds']:.3f} | {r['passes']} | {r['ins']} | {r['D']:.2f} | {r['form']} | {'' if not r['Dj'] else f'{r[chr(68)+chr(106)]:.1f}'} | {r['L']:,.0f} | {r['cu']:,.1f} | {r['ik']:,.1f} | {r['R20']:.3f} | {r['std']} |")
md += ['', '## 3. Production plan', '',
       'Two values were checked in Rev B. The insulation of PV Wire 2 kV at 10 AWG is 75 mil (1.91 mm), which is the UL 4703 wall for 1000 V and 2000 V at 14 to 10 AWG; it had been carried as 1.52 mm. The minimum average TC-ER jacket thicknesses of 1.14, 1.52, 2.03, 2.79 and 3.56 mm, for diameters under the jacket of up to 10.80, 17.78, 38.10 and 63.50 mm and above, agree with the UL 1277 table. Both checks were made against published data sheets that restate the tables of the standards; a purchased copy of each standard is still to be checked before the type tests.', '',
       'The production steps are the same for every family.', '',
       '1. Rod. The 8 mm redraw rod to ASTM B49 is cast continuously from the copper cathode of the electrowinning line. Every coil is checked for 100 % IACS conductivity by a four-wire resistance measurement to ASTM B193.',
       f'2. Drawing. WIRE_DRAW is a multi-die line with diamond or polycrystalline diamond dies, lubricated with emulsion. The number of passes in Table 2.1 takes the rod to the strand wire at {RED:.0%} reduction per pass, with a fixed die series for each strand size.',
       '3. Annealing. An in-line resistance annealer, shrouded in inert gas or steam, brings the wire to soft temper as defined by the elongation limits of ASTM B3.',
       '4. Stranding. A rigid or tubular strander lays class B concentric strand within the lay-length limits of ASTM B8. The 16 and 18 AWG sizes are 7-wire strand for flexibility.',
       '5. Insulation. A single-screw extruder with a crosshead applies the thickness in the family sheet. Cross-linked polyethylene (for XHHW-2 and PV Wire) and ethylene propylene rubber (for MV-105) are cured in a continuous vulcanising tube or by moisture-cured silane. PVC with a nylon sheath (for THHN and TFFN) is applied by tandem extrusion.',
       '6. In-line test. Every metre is spark tested at the voltage that UL 1581 gives for the insulation thickness, and a diameter gauge feeds back to the extruder.',
       '7. Cabling. TC-ER cables and pairs are twisted or cabled; shielded pairs get a foil and drain wire; then the jacket is extruded, the legend printed and the cable coiled or reeled.',
       '8. Tests. Each reel is tested for conductor resistance against R20 in Table 2.1 and the limits of NEC Chapter 9 Table 8, for AC dielectric strength and insulation resistance in water to UL 1581, and for dimensions. Each family is type tested once to its listed standard: the VW-1 or vertical tray flame test, cold bend, sunlight resistance for PV Wire, crush and impact for TC-ER, and partial discharge for MV-105.', '',
       '## 4. Family sheets', '', 'Each subsection gives the specification of one family.', '']
for r in rows:
    f = r['f']
    lay = '; '.join(f"{nm} {t:.2f} mm" for nm, t in r['lay'])
    cab = (f" It is made up as {r['form']}, with a jacket of {jacket(r['Dj'] - 2*jacket(r['Dj']) if r['Dj'] else 0):.2f} mm from the UL 1277 table [UL1277_2019] and a cable outside diameter of {r['Dj']:.1f} mm." if r['Dj'] else '')
    md += [f"### {r['fam']}: {f['type']} {f['size']}, {f['insulation']}", '',
           f"The family serves {f['circuits']} circuits with {r['L']:,.0f} m of conductor" + (f" at voltage class {f['voltage_class']}" if f['voltage_class'].strip() not in ('', '-') else ', with no voltage class because the conductor is bare') + " (AQS-INV-002). "
 f"Its drawing is `docs-authority/drawings/wire/{r['fam']}.svg`.",
           f"The conductor is {r['a']:.3f} mm2 of soft copper, {r['n']} wires of {r['ds']:.3f} mm, with a stranded diameter of {r['Dc']:.2f} mm and a resistance at 20 °C of {r['R20']:.3f} ohm/km including the stranding factor; it uses {r['cu']:,.1f} kg of copper. "
           + (f"The covering layers are: {lay}. " if lay else 'The conductor is bare. ')
           + f"The core diameter is {r['D']:.2f} mm.{cab}",
           f"The strand wire is drawn in {r['passes']} passes from 8 mm rod. The family is made to {r['std']} and uses {r['ik']:,.1f} kg of compound.", '']
open('docs-authority/WIRE_SPECS.md', 'w').write('\n'.join(md) + '\n')
import json; json.dump([{k: v for k, v in r.items() if k not in ('f', 'lay')} for r in rows], open('docs-authority/inventory/WIRE_SPECS.json', 'w'), indent=1)
print(len(rows), round(tot_cu), round(tot_i))

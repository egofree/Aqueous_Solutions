"""X-PAR-12 O2 source study (AQS-PAR-005). Step 1 audits every O2-evolving process on the graph with Faraday/stoichiometry; step 2 sizes the
grow bed on a light basis; step 3 compares the remaining-gap sources. Writes docs-authority/O2_SOURCE_AUDIT.md (Rev A study, frozen pre-X-PAR-12
graph) and docs-authority/O2_SOURCE.md (Rev D duty summary from the live graph, D-O2/A-M-230). Run: python3 -m flow_graph.param.o2_source
Faraday: kg O2/d per A = 86400/(4 F) x 0.032 = 7.164e-3 (O2 needs 4 e-); Cl2 needs 2 e-. F = 96485 C/mol."""
import json, os
from flow_graph.param.gas_species import ledger
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = 96485.0; O2_PER_A = 86400/(4*F)*0.032; H2_PER_A = 86400/(2*F)*0.002016
QY, ABS, LED = 0.045, 0.90, 2.8     # net canopy quantum yield mol CO2/mol absorbed at elevated CO2; canopy absorptance; LED umol/J (KUSUMA2020)
def study(g):
    E = {e['stream_id']: e for e in g['edges']}; N = {n['unit_id']: n for n in g['nodes']}; v = lambda k: float(E[k]['rate']['value'] or 0) if k in E else 0.0
    L = ledger(g)
    ew_kw = sum(v(f'IA-DC-EW_{i}') for i in range(1, 10)); V = float(N['EW_1']['params'].get('cell_voltage_V', 2.12)); I = ew_kw*1000/V
    ew_h2 = sum(v(k) for k in E if (k.startswith('IA-EW') and k.endswith('-H2')) or k in ('IA-HDR-H2-01', 'IA-HDR-H2-03', 'IA-HDR-H2-04')) * 0.98
    audit = [('BMED_ACID/BASE bipolar membranes', 'H2O -> H+ + OH- inside the bipolar junction; no gas. Only the end-electrode pair evolves gas: anode 2 H2O -> O2 + 4 H+ + 4 e-', 'end electrodes only: one pair per stack; stack current not on the graph (credit 0 until the stack sheet gives it, < 0.1 kg/d per 10 A)', 0.0),
             ('EW_1..9, Ti/PbO2 anodes, HCl chloride electrolyte (H2_EMBRITTLEMENT_REVIEW, USBM_CL_EW)', '2 Cl- -> Cl2 + 2 e-; O2 side reaction 2 H2O -> O2 + 4 H+ + 4 e- at 1-3 % of anode current in chloride (O_BRIEN2005)',
              f'{ew_kw:.1f} kW DC / {V} V = {I:,.0f} A-cell; 2 % O2 = {0.02*I*O2_PER_A:.2f} kg/d, dissolved in the anolyte and stripped to HDR_ACID_GAS hoods, not captured', 0.0),
             ('Chlor-alkali', 'none on the graph (BMED makes the NaOH/HCl)', '-', 0.0),
             ('WS_PEROX', 'O2 + H2 -> H2O2 then 2 H2O2 -> 2 H2O + O2 at the bench: net O2 sink of half the draw', f'{v("IA-H2O2-SRC"):.3f} kg/d drawn, {v("IA-H2O2-SRC")/2:.3f} back to bench air (not captured)', 0.0),
             ('Hypochlorite (alkali scrubber)', '2 NaOCl -> 2 NaCl + O2 (catalysed); scrubber Cl2 loading ~ 0 on the graph', '0', 0.0),
             ('HNO3, nitrate reduction', 'NH3 + 2 O2 -> HNO3 + H2O consumes O2; denitrification gives N2, O to H2O/CO2', 'sink, already in ledger', 0.0),
             ('SIC_FURNACE carbothermal', 'SiO2 + 3 C -> SiC + 2 CO; regolith O leaves as CO, burnt with O2 in the afterburner: net sink', f'{v("IA-SIC-CO"):.3f} kg/d CO', 0.0),
             ('Molten-salt / FFC regolith reduction (SCHWANDT2012, LOMAX2020)', 'MO2 + 4 e- -> M + 2 O2-; inert anode 2 O2- -> O2 + 4 e-; ~ 40 wt% of lunar regolith is O', 'no such unit on the graph (candidate, see section 3)', 0.0),
             ('DIGESTER, BLACK_DIGEST', 'anaerobic: CH2O -> 1/2 CH4 + 1/2 CO2, no O2; no aerobic stage on either node', '0', 0.0),
             ('GROW_BED photosynthesis', 'CO2 + H2O -> CH2O + O2, PQ 1.0 (TAIZ2015)', 'see section 2: light-limited, not CO2-limited', None)]
    area = 28.0; dli = 17.0
    co2_m2 = dli*ABS*QY*44.01; o2_m2 = co2_m2*32/44.01; kwh_m2 = dli/(LED*1e-6)/3.6e6
    co2_bed = v('S04') + v('S89'); A_need = co2_bed*1000/co2_m2
    sweep = [(a, a*o2_m2/1000, a*kwh_m2/24, a*kwh_m2/(o2_m2/1000)/a if a else 0) for a in (28, 100, 250, 500, A_need)]
    src = [('PEM electrolysis', 55/7.94, 1.126, 'water 1.13 kg/kg O2; by-product H2 0.126 kg/kg', 'IEA_GHR2023; DOE HFTO 50-55 kWh/kg H2 system'),
           ('Alkaline electrolysis', 52/7.94, 1.126, 'same; KOH 30 wt% loop', 'IEA_GHR2023 50-55'),
           ('LED grow bed', kwh_m2/(o2_m2/1000), 0.56, f'{1000/o2_m2:.0f} m2 per kg/d O2; fixes C as biomass', 'QY x LED efficacy (this study)'),
           ('Chlorate candle + chlorate cell', 2.22*5.5, 0, 'NaClO3 -> NaCl + 1.5 O2 (0.451 kg O2/kg); NaCl back to a chlorate cell at 5.5 kWh/kg NaClO3; Fe fuel 5 %', 'ULLMANN chlorates'),
           ('KO2', 3.0*9.0, 0, '0.338 kg O2/kg; K metal by melt electrolysis; K2CO3 waste', 'ULLMANN potassium'),
           ('Air intake (retired IA-AIR-IN)', 0.2, 0, 'needs 3.3 kg N2 vented per kg O2: breaks the no-vent rule (AQS-DUTY-019)', 'boundary')]
    return dict(L=L, audit=audit, I=I, ew_kw=ew_kw, ew_h2=ew_h2, co2_m2=co2_m2, o2_m2=o2_m2, kwh_m2=kwh_m2, co2_bed=co2_bed, A_need=A_need, sweep=sweep, src=src, area=area, dli=dli,
                bed_real=area*o2_m2/1000, ret=v('IA-CO2-RET'), asu_o2=v('IA-ASU-O2'), ew_h2_A=ew_h2/H2_PER_A)
def write(d):
    L = d['L']; before = L['sink'] + L['need'] - L['src']
    after = L['sink'] + L['need'] - d['bed_real']
    X = ['# O2 source study', '', 'Document number: AQS-PAR-005A', 'Revision: A', 'Date: 2026-10-15', 'Authority: AQS-PLAN-007 X-PAR-12. Generated by `flow_graph/param/o2_source.py`. A-M-132.', '',
         '## 1. Audit of O2-evolving processes', '', '| Process | Stoichiometry | Rate on the graph | O2 credited kg/d |', '| --- | --- | --- | --- |'] + [
         f'| {a} | {b} | {c} | {"-" if x is None else f"{x:.2f}"} |' for a, b, c, x in d['audit']] + ['',
         f"Finding 1.1: the EW cathode H2 on the graph ({d['ew_h2']:.1f} kg/d) needs {d['ew_h2_A']:,.0f} A-cell by Faraday at 100 % to H2, leaving nothing for the metal; the DC bus delivers {d['I']:,.0f} A-cell. The anode product of that current (Cl2, {d['I']*86400/(2*F)*0.0709:.0f} kg/d at 100 %) is not on the graph. Owner review: the EW anode and cathode edges need a Faraday transfer function before any O2 credit is taken.", '',
         '## 2. Grow bed on a light basis', '', f"Net canopy quantum yield {QY} mol CO2/mol absorbed, absorptance {ABS} (elevated CO2, WHEELER1996 BPC), LED {LED} umol/J (KUSUMA2020).",
         f"At DLI {d['dli']} mol/m2/d: {d['co2_m2']:.1f} g CO2 and {d['o2_m2']:.1f} g O2 per m2 per day, {d['kwh_m2']:.2f} kWh/m2/d of LED electricity.", '',
         f"Finding 2.1: T6 (balance.py) credits all {d['co2_bed']:.2f} kg/d CO2 dosed to the bed as fixed. The issued 28 m2 at DLI 17 fixes {28*d['co2_m2']/1000:.2f} kg/d; fixing the full dose needs {d['A_need']:.0f} m2. "
         'The remainder is the CO2 the duty sheet already sends to the farm exhaust (GROW_BED params co2_to_exhaust_kg_d). S87 is over-credited.', '',
         '| Bed m2 | O2 kg/d | LED kW | kWh per kg O2 |', '| --- | --- | --- | --- |'] + [f'| {a:.0f} | {o:.2f} | {k:.1f} | {e:.0f} |' for a, o, k, e in d['sweep']] + ['',
         '## 3. Remaining-gap sources', '', '| Source | kWh per kg O2 | water kg/kg | Notes | Basis |', '| --- | --- | --- | --- | --- |'] + [f'| {a} | {b:.1f} | {c} | {n} | {r} |' for a, b, c, n, r in d['src']] + ['',
         'Smallest complete system: PEM electrolysis, about 7 kWh per kg O2 against about 77 for LED photosynthesis and 12 or more for chemical oxygen; one unit, no consumable, and its H2 has a sink on the graph. Air intake is excluded by the no-vent rule.', '',
         f"Finding 3.1: the cold box sends {d['asu_o2']:.2f} kg/d O2 (IA-ASU-O2) while its only O-bearing feeds are CO2 and dissolved gas; IA-CO2-RET ({d['ret']:.1f} kg/d CO2 in, no CO2 out) is the mass that becomes that O2. That is not a separation.", '',
         '## 4. O2 ledger', '', '| | consumed | combustion | regenerated | gap kg/d |', '| --- | --- | --- | --- | --- |',
         f"| before (AQS-PAR-004 A) | {L['sink']:.2f} | {L['need']:.2f} | {L['src']:.2f} | {before:.1f} |",
         f"| after audit, light-limited bed 28 m2 | {L['sink']:.2f} | {L['need']:.2f} | {d['bed_real']:.2f} | {after:.1f} |", '',
         'Superseded for the graph by AQS-PAR-005 Rev B (O2_SOURCE.md).']
    open(os.path.join(ROOT, 'docs-authority/O2_SOURCE_AUDIT.md'), 'w').write('\n'.join(X) + '\n'); return before, after
def duty(g):
    """AQS-PAR-005 Rev D: O2 duty summary from the live graph (owner ruling D-O2 2026-10-18, A-M-230). Mirrors the o2_close.close_o2
    ledger (same source/draw definitions) so this sheet always states what the graph states. Writes docs-authority/O2_SOURCE.md."""
    E = {e['stream_id']: e for e in g['edges']}; N = {n['unit_id']: n for n in g['nodes']}
    v = lambda k: float(E[k]['rate']['value'] or 0) if k in E else 0.0
    beds = ('VEG_BED', 'FRUIT_GUTTER', 'PEANUT', 'NFIX_BED')
    src_rows = [('PEM electrolyser H2O_ELYZ (the plant O2 source, A-M-230)', 'IA-ELY-O2', v('IA-ELY-O2')),
                ('grow bed GROW_BED, crew duty (A-M-229)', 'S87', v('S87')),
                ('cold box CRYO_ASU, recovered combustion excess (not a source: species recovery)', 'IA-ASU-O2', v('IA-ASU-O2'))] + \
               [(f'grow bed {E[k]["from_unit_id"]}', k, v(k)) for k in sorted(E) if k.startswith('IA-') and k.endswith('-O2')
                and E[k]['to_unit_id'] == 'CRYO_O2' and E[k]['from_unit_id'] in beds and v(k) > 0]
    hdr_rows = [(k, E[k]['to_unit_id'], v(k)) for k in sorted(E) if E[k]['from_unit_id'] == 'HDR_O2' and k not in ('IA-O2-RET', 'IA-O2-PROD')
                and E[k]['presence'] == 'present' and 'mass' in (E[k].get('layers') or []) and E[k]['rate'].get('unit') == 'kg/d']
    dir_rows = [(k, E[k]['to_unit_id'], v(k)) for k in sorted(E) if E[k]['from_unit_id'] == 'CRYO_O2' and k not in ('S83', 'IA-O2-MAKE')
                and E[k]['presence'] == 'present' and 'mass' in (E[k].get('layers') or []) and E[k]['rate'].get('unit') == 'kg/d']
    src = sum(r[2] for r in src_rows); hdr = sum(r[2] for r in hdr_rows); direct = sum(r[2] for r in dir_rows)
    s83 = v('S83'); ship = v('IA-O2-SHIP'); og = N['CRYO_O2']['params'].get('o2_gap', {})
    st = N['CRYO_O2']['params']; e_h2 = v('IA-ELY-H2'); e_kw = v('SF-H2O_ELYZ')
    X = ['# O2 source duty summary', '', 'Document number: AQS-PAR-005', 'Revision: D', 'Date: 2026-10-18',
         'Authority: AQS-PLAN-007 X-PAR-12, X-PAR-11. Generated by `flow_graph/param/o2_source.py` (Rev A study, Rev D duty summary from the live graph; the Rev B/C closure narrative is written by `flow_graph/param/o2_close.py` report() from balance.physics). A-M-132, A-M-133, A-M-230.', '',
         '| Rev | Description | Date |', '| --- | --- | --- |',
         '| A | Audit, light-limited bed, source comparison. | 2026-10-15 |',
         '| B | Owner: the three errors are physics corrections. Bed credit light-limited; cold box conserves species; EW gases by Faraday with a Cl2 sink; combustion O2 on the graph; PEM electrolyser with the fuel cell as a reversible store; CO2 to methanol. | 2026-10-15 |',
         '| C | Owner Q-003/Q-004: genset standby (NFPA 110), H2 bank sized from need. | 2026-10-15 |',
         '| D | Duty summary regenerated from the live graph (D-O2 restore, A-M-230): sources, draws, surplus shipped, N+1 pair stated. Supersedes the Rev C tables; they regenerate from `o2_close.py` at the next balance run. | 2026-10-18 |', '',
         '## 1. O2 duty ledger (kg/d)', '',
         '| Source into CRYO_O2 | Edge | kg/d |', '| --- | --- | --- |']
    X += [f'| {a} | `{b}` | {c:.2f} |' for a, b, c in src_rows]
    X += [f'| **sources** | | **{src:.2f}** |', '', '| Draw | Edge | To | kg/d |', '| --- | --- | --- | --- |']
    X += [f'| header (via HDR_O2, passed on S83) | `{k}` | {u} | {x:.2f} |' for k, u, x in hdr_rows]
    X += [f'| direct on CRYO_O2 | `{k}` | {u} | {x:.2f} |' for k, u, x in dir_rows]
    X += [f'| **draws** | | | **{hdr + direct:.2f}** |', f'| surplus shipped (IA-O2-PROD = IA-O2-SHIP, cylinders at NORTH_DOCK) | `IA-O2-SHIP` | PROD_O2 | **{ship:.2f}** |', '',
          f'Balance: sources {src:.2f} - direct CRYO_O2 draws {direct:.2f} = {s83:.2f} passed to the header on S83; S83 {s83:.2f} - header draws {hdr:.2f} = {ship:.2f} shipped. '
          f"CRYO_O2 params o2_gap (A-M-230): src {og.get('src_kg_d')}, header draw {og.get('hdr_draw_kg_d')}, direct draw {og.get('direct_draw_kg_d')}, system short {og.get('system_short_kg_d')}, surplus {og.get('system_surplus_kg_d')}. The surplus is product, not a vent (no-vent rule, AQS-DUTY-019).", '',
          '## 2. N+1 (owner ruling D-O2, 2026-10-18, recorded 9b742c4; A-M-230)', '',
          'The PEM electrolyser is the plant O2 source. The cold box is a species-recovery box, not a source: it has no air intake, and IA-ASU-O2 is recovered combustion excess only. With the crew-duty grow bed (A-M-229) the electrolyser restores the diverse N+1 O2 pair (P19): electric + biological. Air intake stays excluded (it breaks the no-vent rule, AQS-DUTY-019). The backup that looks surplus to the daily balance is intentional (redundancy rule, X-RED).', '',
          f"Store redundancy: 200 bar cylinder bank, {st.get('store_kg')} kg O2 ({st.get('store_water_volume_m3')} m³ water volume), stoichiometric partner of the CRYO_H2 store, separate from H2 (NFPA 2 ch. 7). Separate crew reserve bank {st.get('crew_reserve_kg')} kg = crew draw {v('S02'):.2f} kg/d × 2 d (NFPA 99 reserve ≥ 1 average day; AQS-ELEC-007 2-d autonomy governs; not drawn by FUEL_CELL; X-RED-04, A-M-146).", '',
          '## 3. Basis', '',
          f"Electrolyser sized by H2 demand, not by the O2 gap (Rev B decision): IA-ELY-H2 {e_h2:.2f} kg/d = gross pool draws (genset S45 {v('S45'):.2f} at NFPA 110 standby, fuel cell S49 {v('S49'):.2f}, methanol S74 {v('S74'):.2f}); O2 = 7.937 × H2, 55 kWh/kg H2 (IEA_GHR2023); {e_kw:.1f} kW average on SF-H2O_ELYZ, rated {e_h2*55/6:.1f} kW on a 6 h PV window (H2O_ELYZ continuous_kw). H2 and O2 are generated, stored and piped separately; no mixed (HHO) gas anywhere (NFPA 2 ch. 7 and 10, ISO 22734:2019, IEC 62282-3-100).", '',
          'Superseded Rev C sections 2-5 (Cl2 and CO2 ledgers, electrolyser/fuel-cell detail, power and roof) regenerate from `flow_graph/param/o2_close.py` report() at the next balance-pipeline run; the frozen pre-X-PAR-12 audit remains in O2_SOURCE_AUDIT.md.']
    open(os.path.join(ROOT, 'docs-authority/O2_SOURCE.md'), 'w').write('\n'.join(X) + '\n')
    return src, hdr + direct, ship
if __name__ == '__main__':
    import subprocess; g = json.loads(subprocess.run(['git', 'show', '6537017:flow_graph/plant_flow_graph.json'], cwd=ROOT, capture_output=True, text=True, check=True).stdout); d = study(g); b, a = write(d)   # Rev A: frozen pre-X-PAR-12 graph
    live = json.load(open(os.path.join(ROOT, 'flow_graph/plant_flow_graph.json'))); s = duty(live)   # Rev D: duty summary from the live graph (D-O2, A-M-230)
    print('before', round(b, 1), 'after', round(a, 1), 'A_need', round(d['A_need']), 'I', round(d['I']), 'ewh2A', round(d['ew_h2_A']), 'o2/m2', round(d['o2_m2'], 1), 'kwh/m2', round(d['kwh_m2'], 2))
    print('duty src', round(s[0], 2), 'draw', round(s[1], 2), 'surplus', round(s[2], 2))

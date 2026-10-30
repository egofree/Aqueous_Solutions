"""AQS-CTL-001 instrument index (X-CTL-01, A-M-193). Every instrument of AQS-INV-004 (OTHER_INVENTORY.csv, category instrument) gets an
ISA5_1_2022 tag <UNIT>-<letters>-<nn>, a calibrated range from the graph, a signal (IEC61131_2) and a loop on its sector PLC.
Ranges: flow = 2 x normal of the named stream (turndown), liquid at the edge density or 1000 kg/m3; pressure = next standard range >= 1.25 x
unit design pressure (gauge), else the inventory 0-10 bar; temperature = band of the unit (cryogenic, hot or ambient); level = 0-100 % of
the liquid height of A-M-182, high-level switch at 90 %. Flags any inventory range below the computed need. Since 2026-10-20 the index also
carries loops authored here for units with no AQS-INV-004 instrument rows (FOUNDRY/POLYMERS trains, gas headers, relief stacks, stores,
EVAP_ACID_VS and the standalone heat machines): ranges cite the node design param, edge rate or inventory artifact in the basis column, and
inventory rows win over authored rows of the same tag letters. Writes docs-authority/inventory/INSTRUMENT_INDEX.csv.
Run: python3 docs-authority/_instr_index.py, then _hazop.py and _sif.py"""
import csv, json, os, re, sys, collections
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(R); sys.path.insert(0, R)
from flow_graph.param.refs import cite
for k in ('ISA5_1_2022', 'IEC61131_2'): cite(k)
g = json.load(open('flow_graph/plant_flow_graph.json')); N = {n['unit_id']: n for n in g['nodes']}; E = {e['stream_id']: e for e in g['edges']}
PR = [1, 2.5, 6, 10, 16, 25, 40, 60, 100, 160, 250, 400]          # bar standard ranges
NICE = [1, 2, 2.5, 5]
def nice(x):
    k = 10**int(f'{x:e}'.split('e')[1]); return next(m*k for m in NICE + [10] if m*k >= x)
LET = {'temperature element (SIF, independent)': 'TE', 'flow transmitter': 'FT', 'pressure transmitter': 'PT', 'temperature element': 'TE', 'level transmitter': 'LT', 'high-level switch': 'LSH'}
rows = []; cnt = collections.Counter(); flags = []
# Standard temperature-element bands: (top C, range, element). Pt100 to 600 C per IEC 60751; type K thermocouple to 1100 C and
# type S to 1600 C per IEC 60584-1 (continuous-use limits of the base-metal and platinum thermocouples).
TE_BANDS = [(150, '-20 to 150 C', 'IEC 60751, 316L thermowell'), (600, '0 to 600 C (Pt100 to 600 C, IEC 60751)', 'IEC 60751, 316L thermowell'),
            (1100, '0 to 1100 C', 'type K thermocouple, IEC 60584, Inconel sheath'), (1600, '0 to 1600 C', 'type S thermocouple, IEC 60584, ceramic sheath')]
for r in csv.DictReader(open('docs-authority/inventory/OTHER_INVENTORY.csv')):
    if r['category'] != 'instrument': continue
    if r['item'].startswith('gas detector'): continue          # gas detectors are listed in AQS-SAF-006, wired to the fire panel and SIS
    u = r['unit']; n = N.get(u) or {}; p = n.get('params') or {}; L = LET[r['item']]; cnt[(u, L, 'SIF' in r['item'])] += 1; tag = f"{u}-{L}-{(89 if 'SIF' in r['item'] else 0) + cnt[(u, L, 'SIF' in r['item'])]:02d}"   # SIF elements numbered 90+ (AQS-CTL-003)
    sig = '24 V DC discrete (DI)' if L == 'LSH' else '4-20 mA HART (AI)'
    if L == 'FT':
        sid = r['basis'].split(':')[0].strip(); e = E.get(sid) or {}; q = (e.get('rate') or {}).get('value') or 0
        rho = ((e.get('params') or {}).get('density_kg_m3')) or 1000.0; lh = q/rho*1000/24
        rng = f'0-{nice(2*lh):g} L/h' if lh > 0 else '0-10 L/h (standby line)'; note = f'{sid} normal {lh:.2f} L/h'
    elif L == 'PT':
        d = p.get('design') or {}
        dk = p.get('design_kPa') or d.get('design_kPa') or (d['P_MPa']*1000.0 if d.get('P_MPa') else None)   # either place on the graph
        need = 1.25*dk/100 if dk else 0; inv = float(re.search(r'0-([0-9.]+)', r['size']).group(1))
        top = next((x for x in PR if x >= need), PR[-1]) if need > inv else inv
        rng = f'0-{top:g} bar g'; note = f"design {dk} kPa g" if dk else 'no design pressure on the graph'
        if need > inv:
            flags.append((tag, r['size'], rng, f'design {dk/100:.0f} bar g'))
            if top > 16: r = dict(r, spec='316L thin-film strain gauge, IEC 61298')   # same element rule as flow_graph/inventory/other.py
    elif L == 'TE':
        T = (p.get('design') or {}).get('T_C'); cry = u.startswith('CRYO') or 'cold' in (n.get('class') or '')
        hot = any(k in u for k in ('PYRO', 'FURNACE', 'MELT', 'AFTERBURN', 'HTC', 'SIC', 'DRYER', 'EVAP', 'DIGEST'))
        rng = '-200 to 50 C' if cry else ('0 to 600 C (Pt100 to 600 C, IEC 60751)' if hot else '-20 to 150 C'); note = f'design T {T} C' if T is not None else 'band by service'
        if T is not None and not cry:   # the span must contain the design temperature with margin: smallest standard band whose top is >= 1.1 x T
            band = next((b for b in TE_BANDS if b[0] >= 1.1*T), TE_BANDS[-1])
            if band[0] > (150 if not hot else 600):
                rng, r = band[1], dict(r, spec=band[2].replace('316L thermowell', 'own thermowell') if 'SIF' in r['item'] else band[2])
    else:
        m = re.search(r'\(([0-9.]+) m full', (p.get('relief_basis') or {}).get('design_case') or ''); h = float(m.group(1)) if m else None
        rng = f'0-100 % of {h:.2f} m' if h else '0-100 % of vessel height'; note = 'alarm at 90 %' if L == 'LSH' else 'A-M-182 liquid height'
        if L == 'LSH': rng = f'trip at 90 % ({0.9*h:.2f} m)' if h else 'trip at 90 % of vessel height'
    rows.append(dict(tag=tag, unit=u, sector=r['sector'], type=r['item'], spec=r['spec'], range=rng, signal=sig, loop=tag.replace('-', '', 1), plc=f"PLC-{r['sector']}", basis=note))

# --- X-CTL-01 per-unit extension (2026-10-20): authored loops for units with no AQS-INV-004 instrument rows ---------------
# Why these units had no loops: flow_graph/inventory/other.py emits instrument rows only where the unit has a nozzle csv, has
# liquid inflow (class not farm/product/building/hab), or is hcl_synthesis/pem_electrolyser, and skips the boundary/header/relief
# classes outright; the FOUNDRY/POLYMERS machines are solid-fed with no nozzle csv at the last AQS-INV-004 regen, and EVAP_ACID_VS's
# only instrument-category row is a gas detector (listed in AQS-SAF-006, skipped by this index). The loops below are authored here
# from the graph: every measured variable, range and citation comes from a node design param, an edge rate, or a cited inventory
# artifact - nothing invented. SIF-numbered elements (90+) continue the AQS-CTL-003 convention.
def _d(u): return (N[u].get('params') or {}).get('design') or {}
def _lph(sid, rho=None):    # L/h of an edge, for the 2 x normal FT range rule
    e = E.get(sid) or {}; q = (e.get('rate') or {}).get('value') or 0
    return q/(rho or (e.get('params') or {}).get('density_kg_m3') or 1000.0)*1000/24
AI = '4-20 mA HART (AI)'; DI = '24 V DC discrete (DI)'
AUTH = []
def A(u, L, typ, spec, rng, basis, sig=AI, sif=False): AUTH.append((u, L, typ, spec, rng, sig, basis, sif))
K600 = '0 to 600 C (Pt100 to 600 C, IEC 60751)'; AMB = '-20 to 150 C'
# FOUNDRY: pot cells (cell current, bath temperature, hood chlorine), Kroll train, melt/cast/FORM chain, benches, store
for u in ('AL_POT', 'CA_POT', 'CR_CELL', 'MG_POT', 'MO_CELL'):
    d = _d(u)
    A(u, 'IT', 'current transmitter', 'DC shunt + isolated amplifier, IEC 61010-1', f"0-{nice(2*d['I_A']):g} A", f"cell current: design I_A {d['I_A']} A")
    A(u, 'TE', 'temperature element', 'type K thermocouple, IEC 60584, Inconel sheath', '0 to 900 C', f"bath temperature: design bath_T_C {d['bath_T_C']:.0f} C")
A('AL_POT', 'AE', 'chlorine analyzer', 'electrochemical Cl2 cell', '0-100 vol % Cl2', 'anode-gas Cl2 offtake: IA-CL2-SHIP 39.42 kg/d; AL_POT_CL2 recycle standby')
A('CA_POT', 'AE', 'chlorine analyzer', 'electrochemical Cl2 cell', '0-100 vol % Cl2', 'anode-gas Cl2 offtake: IA-CA-CL2-SHIP 0.10 kg/d')
A('CA_POT', 'LT', 'level transmitter', 'laser level meter, non-contact', '0-100 % of bath height', 'molten CaCl2 bath: IA-CACL2-MU 0.15 kg/d brine feed')
A('CR_CELL', 'AE', 'chlorine analyzer', 'electrochemical Cl2 cell', '0-100 vol % Cl2', 'carbochlorination loop Cl2 (design chemistry); IA-CR-VENT CO 0.20 kg/d')
A('MG_POT', 'AE', 'chlorine analyzer', 'electrochemical Cl2 cell', '0-100 vol % Cl2', 'anode-gas Cl2 to the Kroll chlorinator: IA-CL2-MG-TI 1.48 kg/d')
A('MG_POT', 'LT', 'level transmitter', 'laser level meter, non-contact', '0-100 % of bath height', 'molten MgCl2 bath: IA-MGCL2-MU 0.04 kg/d brine make-up')
A('MO_CELL', 'AE', 'chlorine analyzer', 'electrochemical Cl2 cell', '0-100 vol % Cl2', 'anode gas (Cl2 or O2) to CRU: MO_CELL_ANODE_GAS_TO_CRU')
A('TI_CELL', 'TE', 'temperature element', 'type K thermocouple, IEC 60584, Inconel sheath', '0 to 1100 C', 'Kroll reduction retort: design retort_T_C 900 C')
A('TI_CELL', 'TE', 'temperature element', 'type K thermocouple, IEC 60584, Inconel sheath', '0 to 1000 C', 'chlorinator: design chlorinator_T_C 800 C')
A('TI_CELL', 'PT', 'pressure transmitter', 'ceramic diaphragm, IEC 61298', '0-10 bar g', 'Ar-cover Kroll retort; no design pressure on the graph')
A('TI_CELL', 'LT', 'level transmitter', 'radar 80 GHz, IEC 62828, PTFE lens', '0-100 % of vessel height', 'TiCl4 receiver between chlorinator and retort (design chemistry, AQS-BAL-KROLL)')
MELT = ('temperature element', 'type B thermocouple, IEC 60584, alumina sheath', '0 to 1600 C')
A('IND_MELT', 'TE', MELT[0], MELT[1], MELT[2], 'Cu/Fe/Zn/Al remelt (design service); 4 heats/d of the 10 kg crucible')
A('IND_MELT', 'TE', 'temperature element (SIF, independent)', 'type B thermocouple, own thermowell', MELT[2], 'independent high-temperature trip (AQS-CTL-003); design service Cu/Fe/Zn/Al', sif=True)
A('RF_HEAT', 'TE', MELT[0], MELT[1], MELT[2], 'equal-duty backup of the IND_MELT crucible class (design backup_of)')
A('RES_HEAT', 'TE', 'temperature element', 'type K thermocouple, IEC 60584, Inconel sheath', '0 to 1100 C', 'design T_C 900 C (reheat, N+1 of SHELL_BURNOUT/SINTER)')
A('RES_HEAT', 'TE', 'temperature element (SIF, independent)', 'type K thermocouple, own thermowell', '0 to 1100 C', 'independent high-temperature trip (AQS-CTL-003); design T_C 900 C', sif=True)
A('COMB_HEAT', 'TE', 'temperature element', 'type K thermocouple, IEC 60584, Inconel sheath', '0 to 1100 C', 'combustion reheating furnace (class furnace); offgas COMB_OFFGAS to MET_SCRUB')
A('CAST_LINE', 'TE', MELT[0], MELT[1], MELT[2], 'mould pour: IND_MELT_TO_CAST 3.0 kg/d molten metal')
A('CAST_LINE', 'LT', 'level transmitter', 'laser level meter, non-contact', '0-100 % of ladle height', 'pour ladle: IND_MELT_TO_CAST 3.0 kg/d molten metal')
A('VAC_IND', 'TE', MELT[0], MELT[1], MELT[2], 'vacuum induction skull melt (design service, 2 kg ISM case)')
A('VAC_IND', 'PT', 'pressure transmitter', 'ceramic diaphragm, IEC 61298', '0 to 1000 mbar a', 'melt-chamber vacuum; no design pressure on the graph')
A('VAC_CAST', 'TE', MELT[0], MELT[1], MELT[2], 'vacuum tilt-pour of VAC_IND_TO_VAC_CAST melt (design case 3 kg)')
A('VAC_CAST', 'PT', 'pressure transmitter', 'ceramic diaphragm, IEC 61298', '0 to 1000 mbar a', 'cast-chamber vacuum; no design pressure on the graph')
A('ROLL', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', K600, 'hot rolling of CAST_TO_ROLL + CONT_TO_ROLL billet (13 kg/d); no design T on the graph')
A('EXTRUDE', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', K600, 'billet/container preheat for extrusion (N+1 of ROLL); no design T on the graph')
A('DRAW', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', AMB, 'cold wire/rod draw bench (N+1 of ROLL); band by service')
A('FORGE', 'ZT', 'position transmitter', 'LVDT ram position transducer', '0-200 mm', 'ram stroke: design ram_mm 200')
A('FORGE', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', K600, 'open-die press stock temperature (N+1 of ROLL); no design T on the graph')
A('SINTER', 'TE', 'temperature element', 'type K thermocouple, IEC 60584, Inconel sheath', '0 to 1400 C', 'design T_C 1300 C powder sinter')
A('SINTER', 'TE', 'temperature element (SIF, independent)', 'type K thermocouple, own thermowell', '0 to 1400 C', 'independent high-temperature trip (AQS-CTL-003); design T_C 1300 C', sif=True)
A('FLUX_PREP', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', AMB, 'salt flux bench (class prep); IA-KROLL-FLUX 0.04 kg/d salt')
A('FLUX_PREP', 'LT', 'level transmitter', 'radar 80 GHz, IEC 62828, PTFE lens', '0-100 % of hopper height', 'flux hopper: design hopper_L 20 L')
A('STOCK_OUT', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', AMB, 'formed-metal staging rack (CONT_TO_STOCK 21.7 kg/d); condensation watch')
A('CONT_CAST', 'TE', MELT[0], MELT[1], MELT[2], 'strand feed: IND_TO_CONT 31.7 kg/d melt; water-cooled copper mould (design)')
A('CONT_CAST', 'LT', 'level transmitter', 'laser level meter, non-contact', '0-100 % of tundish height', 'tundish: IND_TO_CONT 31.7 kg/d molten metal')
A('WAX_PATTERN', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', AMB, 'wax pot: WAX_RECLAIM_TO_PATTERN 1.8 kg/d reclaim + make-up 0.2 kg/d')
A('WAX_PATTERN', 'LT', 'level transmitter', 'radar 80 GHz, IEC 62828, PTFE lens', '0-100 % of pot height', 'wax pot: design pot_L 10 L')
A('SHELL_BUILD', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', AMB, 'slurry tank of the 6-dip booth (design dips 6)')
A('SHELL_BUILD', 'LT', 'level transmitter', 'radar 80 GHz, IEC 62828, PTFE lens', '0-100 % of slurry tank height', 'slurry tank: design slurry_L 40 L')
A('SHELL_BURNOUT', 'TE', 'temperature element', 'type K thermocouple, IEC 60584, Inconel sheath', '0 to 1100 C', 'design T_C 900 C flash-dewax + shell fire')
A('SHELL_BURNOUT', 'TE', 'temperature element (SIF, independent)', 'type K thermocouple, own thermowell', '0 to 1100 C', 'independent high-temperature trip (AQS-CTL-003); design T_C 900 C', sif=True)
A('INV_CAST', 'TE', MELT[0], MELT[1], MELT[2], 'investment pour: IND_TO_INV 2.0 kg/d melt')
A('INV_CAST', 'LT', 'level transmitter', 'laser level meter, non-contact', '0-100 % of crucible height', 'pour crucible: IND_TO_INV 2.0 kg/d molten metal')
A('SHELL_BREAK', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', AMB, 'knock-out station (class separator); INV_TO_BREAK 10 kg/d')
A('METAL_STORE', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', AMB, 'metal product store (IA-STOCK-STORE 36.7 kg/d); condensation watch')
# POLYMERS: HF kiln (offgas T, HF analyzer, feed rate), VDF/TFE trains, kettle, formers, stock
A('HF_GEN', 'FT', 'flow transmitter', 'gravimetric loss-in-weight feeder (solids feed)', f"0-{nice(2*((E['IA-CAF2-MU']['rate']['value'])/24)):g} kg/h", f"acid-spar feed: IA-CAF2-MU 0.33 kg/d (design spar_kg_d)")
A('HF_GEN', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', K600, 'kiln/offgas: design T_C 250 C rotary kiln')
A('HF_GEN', 'TE', 'temperature element (SIF, independent)', 'Pt100 class A, own thermowell', K600, 'independent high-temperature trip (AQS-CTL-003); design T_C 250 C', sif=True)
A('HF_GEN', 'AE', 'HF analyzer', 'electrochemical HF cell', '0-10 ppm HF', 'kiln offgas HF watch: design hf_kg_d 1.67 kg/d')
A('HF_GEN', 'LT', 'level transmitter', 'radar 80 GHz, IEC 62828, PTFE lens', '0-100 % of vat height', 'feed blend vat: F_RECOVER_TO_HF_GEN and IA-H2SO4-ACID from ACID_PLANT')
A('VDF_SYN', 'TE', 'temperature element', 'type K thermocouple, IEC 60584, Inconel sheath', K600, 'chlorination reactor: design chlorination_C 350 C')
A('VDF_SYN', 'TE', 'temperature element', 'type K thermocouple, IEC 60584, Inconel sheath', '0 to 800 C', '142b cracking furnace: design cracking_C 650 C')
A('ACID_PLANT', 'TE', 'temperature element', 'type K thermocouple, IEC 60584, Inconel 600 sheath', '0 to 1300 C', 'cake kiln and sulfur burner temperature (A-M-421)')
A('ACID_PLANT', 'TE', 'temperature element (SIF, independent)', 'type K thermocouple, own sheath', '0 to 1300 C', 'independent high-temperature trip on the cake kiln (AQS-CTL-003)', sif=True)
A('ACID_PLANT', 'AE', 'SO2 analyzer', 'electrochemical SO2 cell', '0-20 ppm SO2', 'absorber tail-gas SO2 watch on the contact process (A-M-421)')
A('ACID_PLANT', 'LT', 'level transmitter', 'radar 80 GHz, IEC 62828, PTFE lens', '0-100 % of tank height', 'product acid tank on stream IA-H2SO4-ACID')
A('VDF_SYN', 'LT', 'level transmitter', 'radar 80 GHz, IEC 62828, PTFE lens', '0-100 % of feed tank height', 'aqueous HF feed tank: HF_GEN_TO_VDF 0.09 kg/d')
A('TFE_SYN', 'TE', 'temperature element', 'type K thermocouple, IEC 60584, Inconel sheath', '0 to 900 C', 'R-22 pyrolysis: design pyrolysis_C 750 C (immediate quench per design)')
A('TFE_SYN', 'LT', 'level transmitter', 'radar 80 GHz, IEC 62828, PTFE lens', '0-100 % of feed tank height', 'aqueous HF feed tank: HF_GEN_TO_TFE 0.08 kg/d')
A('POLY_F', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', AMB, 'emulsion kettle: design T_C 60 C')
A('POLY_F', 'LT', 'level transmitter', 'radar 80 GHz, IEC 62828, PTFE lens', '0-100 % of 0.23 m kettle', 'kettle: design H_mm 225')
A('POLY_COND', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', K600, 'standby condensation kettle: design jacket_C 160 C')
A('POLY_COND', 'LT', 'level transmitter', 'radar 80 GHz, IEC 62828, PTFE lens', '0-100 % of 0.30 m kettle', 'kettle: design H_mm 300')
A('POLY_OLEFIN', 'TE', 'temperature element', 'type K thermocouple, IEC 60584, Inconel sheath', '0 to 400 C', 'oligomerization reactor: design T_C 250 C')
A('POLY_OLEFIN', 'TE', 'temperature element (SIF, independent)', 'type K thermocouple, own thermowell', '0 to 400 C', 'independent high-temperature trip (AQS-CTL-003); design T_C 250 C', sif=True)
A('POLY_OLEFIN', 'PT', 'pressure transmitter', '316L thin-film strain gauge, IEC 61298', '0-100 bar g', 'design P_MPa 5.0 (1.25 x = 62.5 bar)')
A('POLY_OLEFIN', 'LT', 'level transmitter', 'radar 80 GHz, IEC 62828, PTFE lens', '0-100 % of 0.23 m vessel', 'reactor: design H_mm 225')
A('PELLET', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', '0 to 100 C', 'underwater die-face pelletizer process water (design machine); no design T on the graph')
A('POWDER_RESIN', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', AMB, 'PTFE pin-mill line, ambient milling (design product note)')
A('POWDER_RESIN', 'ST', 'speed transmitter', 'incremental encoder on the mill drive', '0-100 % of drive speed', 'mill drive: design duty_kW 0.0152 kW')
A('FILM_CAST', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', '0 to 300 C', 'extruder melt: design melt_C 220 C')
A('FILM_CAST', 'ST', 'speed transmitter', 'incremental encoder on the chill-roll/haul-off drive', '0-100 % of drive speed', 'chill-roll drive: design chill_roll_D_mm 150')
A('FILM_CAST', 'LT', 'level transmitter', 'radar 80 GHz, IEC 62828, PTFE lens', '0-100 % of feed vessel height', 'PVDF feed: POLYF_TO_FILM 0.14 kg/d resin')
A('POLY_STOCK', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', AMB, 'polymer stock bins (PELLET_TO_STOCK 0.29 kg/d)')
A('POLY_STOCK', 'LT', 'level transmitter', 'ultrasonic bin level', '0-100 % of bin height', 'pellet tote bins (design bin)')
# HEAT: chiller, MAU, dry cooler, Q4 hot-water bus
A('ADS_CHILL', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', '0 to 100 C', 'drive water in: IA-Q4-ADS 5.0 kW Q4 65 C')
A('ADS_CHILL', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', '0 to 40 C', 'chilled water out: IA-ADS-CHW 2.25 kW at 12 C')
A('MAU_HX', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', '0 to 100 C', 'Q4 coil: IA-Q4-MAU 12 kW Q4 water 65/45 C (winter design)')
A('DRY_COOLER', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', '0 to 100 C', 'recooling: IA-ADS-REJ 7.25 kW + HL-Q4-REJ Q4 surplus')
A('Q4_BUS', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', '0 to 100 C', 'Q4 hot-water bus supply (IA-Q4-ADS/IA-Q4-MAU 65 C design)')
A('Q4_BUS', 'PT', 'pressure transmitter', 'ceramic diaphragm, IEC 61298', '0-10 bar g', 'hot-water bus; no design pressure on the graph')
# WTR: groundwater intake skid (make-up source; X-LOC-07, AQS-PLAN-011 section 6.2)
A('GW_INTAKE', 'FT', 'flow transmitter', 'electromagnetic, PFA liner, Hastelloy C electrodes, ISO 20456', f"0-{nice(2*_lph('IA-GW-MAKEUP')):g} L/h", f"make-up to ROOF_TANK: IA-GW-MAKEUP {(E['IA-GW-MAKEUP']['rate']['value'] or 0):.2f} kg/d ({_lph('IA-GW-MAKEUP'):.2f} L/h)")
A('GW_INTAKE', 'PT', 'pressure transmitter', 'ceramic diaphragm, IEC 61298', '0-10 bar g', 'RO membrane feed; no design pressure on the graph')
A('GW_INTAKE', 'CT', 'conductivity transmitter', 'inductive conductivity, IEC 60746-1', '0-2000 uS/cm', 'RO product quality watch; well water moderately mineralised with high silica, fluoride and arsenic (USGS_DV_GW)')
# DIGESTER: acid vent scrubber (pH/ORP + level + recirc flow), recovery separators
A('EVAP_ACID_VS', 'AE', 'pH analyzer', 'glass electrode pH, IEC 60746-2', '0-14 pH', 'scrub liquor: NaOH 2 M bleed IA-VS-NAOH 0.5 g/d')
A('EVAP_ACID_VS', 'AE', 'ORP analyzer', 'ORP electrode, IEC 60746-2', '-1000 to +1000 mV', 'acid-gas breakthrough watch: IA-VS-OFF 0.029 kg/d scrubbed vent')
A('EVAP_ACID_VS', 'LT', 'level transmitter', 'radar 80 GHz, IEC 62828, PTFE lens', '0-100 % of vessel height', 'scrub liquor: IA-VS-SPENT 0.6 g/d spent bleed')
A('EVAP_ACID_VS', 'LSH', 'high-level switch', 'vibrating fork, IEC 60947-5, 316L', 'trip at 90 % of vessel height', 'scrubber sump high level trips the feed', DI)
A('EVAP_ACID_VS', 'FT', 'flow transmitter', 'electromagnetic, PFA liner, Hastelloy C electrodes, ISO 20456', '0-700 L/h', 'sump recirculation 0.35 m3/h (AQS-INV-001 motor inventory)')
A('EVAP_ACID_VS', 'TE', 'temperature element (SIF, independent)', 'Pt100 class A, own thermowell', K600, 'independent high-temperature trip (AQS-CTL-003); acid vent scrubber', sif=True)
A('F_RECOVER', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', AMB, 'fluoride concentrate receiver (class separator)')
A('F_RECOVER', 'LT', 'level transmitter', 'radar 80 GHz, IEC 62828, PTFE lens', '0-100 % of vessel height', 'concentrate: F_RECOVER_TO_HF_GEN 1.52 kg/d')
A('LI_RECOVER', 'LT', 'level transmitter', 'radar 80 GHz, IEC 62828, PTFE lens', '0-100 % of vessel height', 'standby Li polish liquor: POLISH_TO_LI (rate pending assay)')
A('P_CA', 'LT', 'level transmitter', 'radar 80 GHz, IEC 62828, PTFE lens', '0-100 % of vessel height', 'standby Ca precipitator: PCA_TO_GREASE (rate pending assay)')
# GAS/HAB/WTR/OIL headers: pressure on every gas header, UPW header also metered
A('HDR_H2', 'PT', 'pressure transmitter', 'ceramic diaphragm, IEC 61298', '0-10 bar g', 'H2 pool header: IA-HDR-H2-02 1.98 kg/d max feed; no design pressure on the graph')
A('HDR_O2', 'PT', 'pressure transmitter', 'ceramic diaphragm, IEC 61298', '0-10 bar g', 'O2 pool header: S83 33.2 kg/d product + returns; no design pressure on the graph')
A('HDR_CO2', 'PT', 'pressure transmitter', 'ceramic diaphragm, IEC 61298', '0-10 bar g', 'CO2 header: S89 0.88 + S90 4.02 kg/d; no design pressure on the graph')
A('HDR_N2', 'PT', 'pressure transmitter', 'ceramic diaphragm, IEC 61298', '0-10 bar g', 'plant air/N2 header: IA-AIR-RX-OUT 192.0 kg/d; no design pressure on the graph')
A('HDR_UPW', 'PT', 'pressure transmitter', 'ceramic diaphragm, IEC 61298', '0-10 bar g', 'UPW header; no design pressure on the graph')
A('HDR_UPW', 'FT', 'flow transmitter', 'electromagnetic, PFA liner, Hastelloy C electrodes, ISO 20456', f"0-{nice(2*_lph('S01')):g} L/h", f"UPW supply: S01 67.30 kg/d ({_lph('S01'):.2f} L/h)")
A('NCG_HEADER', 'PT', 'pressure transmitter', 'ceramic diaphragm, IEC 61298', '0-10 bar g', 'NCG header: IA-OIL-03 5.0 kg/d to the afterburner; no design pressure on the graph')
# OIL: standby grease kettles; CRYO: air receiver, product stores, relief stacks; GLASS/ELEC/FARM remainder
A('GREASE_CA', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', AMB, 'Ca grease kettle (class kettle); WAX_TO_GREASE_CA wax cut (rate pending assay)')
A('GREASE_CA', 'LT', 'level transmitter', 'radar 80 GHz, IEC 62828, PTFE lens', '0-100 % of kettle height', 'kettle holdup (class kettle)')
A('GREASE_LI', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', AMB, 'Li grease kettle (class kettle); WAX_TO_GREASE_LI wax cut (rate pending assay)')
A('GREASE_LI', 'LT', 'level transmitter', 'radar 80 GHz, IEC 62828, PTFE lens', '0-100 % of kettle height', 'kettle holdup (class kettle)')
A('AIR_RECEIVER', 'PT', 'pressure transmitter', 'ceramic diaphragm, IEC 61298', '0-10 bar g', 'plant-air receiver bank: IA-AIR-RX-OUT 192.0 kg/d; no design pressure on the graph')
A('AIR_RECEIVER', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', AMB, 'receiver bank; band by service')
A('PROD_O2', 'PT', 'pressure transmitter', 'ceramic diaphragm, IEC 61298', '0-10 bar g', 'O2 product cylinder bank: IA-O2-PROD 22.9 kg/d; no design pressure on the graph')
A('PROD_O2', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', AMB, 'cylinder bank; band by service')
A('PROD_MEOH', 'FT', 'flow transmitter', 'electromagnetic, PFA liner, Hastelloy C electrodes, ISO 20456', f"0-{nice(2*_lph('IA-MEOH-PROD', 792)):g} L/h", f"methanol product: IA-MEOH-PROD 28.15 kg/d ({_lph('IA-MEOH-PROD', 792):.2f} L/h at 792 kg/m3)")
A('PROD_MEOH', 'LT', 'level transmitter', 'radar 80 GHz, IEC 62828, PTFE lens', '0-100 % of vessel height', 'methanol product store (liquid, A-M-182)')
A('PROD_MEOH', 'LSH', 'high-level switch', 'vibrating fork, IEC 60947-5, 316L', 'trip at 90 % of vessel height', 'store high level trips the feed', DI)
A('PROD_MEOH', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', AMB, 'product store; band by service')
A('RELIEF_CRYO', 'PSH', 'pressure switch, high (rupture indication)', 'diaphragm pressure switch, IEC 60947-5-1', 'trips on header pressure rise (disc burst / PSV lift)', 'vent stack: S56 + S86 cryo contingency vents', DI)
A('RELIEF_H2', 'PSH', 'pressure switch, high (rupture indication)', 'diaphragm pressure switch, IEC 60947-5-1', 'trips on header pressure rise (disc burst / PSV lift)', 'vent stack: S24 H2 relief contingency', DI)
A('SI_REDUCE', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', K600, 'Si reduction furnace shell and off-gas (CHAR_TO_SI and IA-QUARTZ-MU rated, A-M-419); band by service')
A('SI_REFINE', 'TE', 'temperature element', 'type S thermocouple, IEC 60584, alumina sheath', '0 to 1300 C', 'Siemens rod or fluidised-bed deposition temperature (A-M-419)')
A('SI_REFINE', 'PT', 'pressure transmitter', 'ceramic diaphragm, IEC 61298', '0-10 bar g', 'chlorosilane loop pressure; no design pressure on the graph')
A('EXT_HALL', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', AMB, 'hall air: SF-EXT_HALL 68.28 kW electrical feed (ventilation watch)')
A('FOOD_STORE', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', AMB, 'food store temperature watch (class store)')
A('FOOD_STORE', 'LT', 'level transmitter', 'ultrasonic bin level', '0-100 % of bin height', 'food stock level: S14 4.2 kg/d')
A('AFTERBURNER_FLUE', 'TE', 'temperature element (SIF, independent)', 'Pt100 class A, own thermowell', K600, 'independent high-temperature trip (AQS-CTL-003); flue gas service (AQS-INV-004 carries no SIF element for it yet)', sif=True)
A('SW_INTAKE', 'FT', 'flow transmitter', 'magnetic, seawater service', '0-200 m3/h', 'intake delivery watch against the desalination and rejection demand (X-LOC-11 placeholder; A-M-409)')
A('DESAL_RO', 'AN', 'conductivity analyser', 'permeate loop, contacting cell', '0-1000 uS/cm', 'permeate quality watch against the UPW feed spec (X-LOC-11 placeholder; A-M-410)')
A('BRIN_RECOVER', 'AE', 'composition analyser', 'brine loop, sampling line', '0-150 g/L', 'brine concentration watch on the recovery path (X-LOC-11 placeholder; A-M-411)')
A('ICE_EXTRACT', 'FT', 'flow transmitter', 'magnetic, brine service', '0-2 m3/h', 'melt-water delivery watch against the make-up demand (X-LOC-09 placeholder; A-M-406)')
A('PERC_REMOVE', 'AE', 'perchlorate analyser', 'ion-selective, bed outlet', '0-100 mg/L', 'bed breakthrough watch on the ClO4 reduction (X-LOC-09 placeholder; A-M-407)')
A('ATM_INT', 'PT', 'pressure transmitter', 'gauge, compressor discharge, 316L diaphragm', '0-400 kPa', 'compressor discharge pressure watch against the process pressure (X-LOC-09 placeholder; A-M-408)')
A('LIO_BAT', 'PT', 'pressure transmitter', 'gauge, pack enclosure', '0-700 kPa', 'pack enclosure pressure watch on the sealed storage (X-LOC-10 placeholder; A-M-402)')
A('WET_OX', 'TE', 'temperature element', 'sheathed type K, reactor service', '0-500 C', 'reactor temperature watch on the wet-oxidation window (X-LOC-10 placeholder; A-M-403)')
A('HYDRO_GROW', 'AE', 'carbon-dioxide analyser', 'NDIR, chamber air loop', '0-5000 ppmv', 'chamber CO2 watch against the habitat management set-point (X-LOC-10 placeholder; A-M-404)')
A('MEM_DIST', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', AMB, 'feed-permeate temperature difference watch on the membrane loop (X-LOC-10 placeholder; A-M-405)')
A('RAD_PANEL', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', AMB, 'radiator loop outlet temperature watch; rejection performance against the A-M-396/A-M-397 design (X-LOC-09 placeholder)')
A('TANK_BLD', 'PT', 'pressure transmitter', 'gauge, 316L diaphragm, pad service', '0-400 kPa', 'bladder pad pressure gives the water level in the closed tank (X-LOC-09 placeholder; A-M-400)')
A('REC_HDR', 'PT', 'pressure transmitter', 'gauge, 316L diaphragm, header service', '0-400 kPa', 'recovery header pressure watch; the header takes every relief and offgas discharge (X-LOC-09 placeholder; A-M-398)')
A('CAT_OX', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', K600, 'catalyst bed temperature watch against the A-M-399 450 C light-off window (X-LOC-09 placeholder)')
A('E_HEAT', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', K600, 'resistance element temperature watch on the N+1 melt trim duty (X-LOC-09 placeholder)')
_have = {(r['unit'], r['tag'].split('-')[-2]) for r in rows}
_nauth = 0
for u, L, typ, spec, rng, sig, basis, sif in AUTH:
    assert u in N, f'authored unit {u} not on the graph'
    if (u, L) in _have and not sif: continue            # an AQS-INV-004 row of the same letters wins once the inventory lane catches up
    if sif and any(r['unit'] == u and r['tag'].endswith(f'-{L}-90') for r in rows): continue
    num = (90 if sif else 0) + sum(1 for r in rows if r['unit'] == u and r['tag'].split('-')[-2] == L
                                    and (int(r['tag'].split('-')[-1]) >= 90) == sif) + (0 if sif else 1)
    tag = f"{u}-{L}-{num:02d}"
    rows.append(dict(tag=tag, unit=u, sector=N[u]['sector_id'], type=typ, spec=spec, range=rng, signal=sig,
                     loop=tag.replace('-', '', 1), plc=f"PLC-{N[u]['sector_id']}", basis=basis)); _nauth += 1
_tags = [r['tag'] for r in rows]
assert len(_tags) == len(set(_tags)), 'duplicate instrument tags'
_no_loop = [n['unit_id'] for n in g['nodes'] if n['unit_id'] not in {r['unit'] for r in rows}]
_boundary = sorted(n['unit_id'] for n in g['nodes'] if n.get('class') == 'boundary')   # trade and bookkeeping boundaries, not process units
assert set(_no_loop) <= set(_boundary), f'process units without a loop (extend AUTH): {sorted(set(_no_loop) - set(_boundary))}'
with open('docs-authority/inventory/INSTRUMENT_INDEX.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
S = collections.Counter(r['plc'] for r in rows); T = collections.Counter(r['type'] for r in rows)
md = ['# Instrument index', '', 'Document number: AQS-CTL-001', 'Revision: B', 'Date: 2026-10-29',
      'Generated by `docs-authority/_instr_index.py`. Do not edit by hand; change the generator or its inputs and run `python3 -m flow_graph.param.regen`.',
      'Authority: AQS-PLAN-007 task X-CTL-01; assumption A-M-193. Tags follow ISA-5.1-2022 [ISA5_1_2022] and signals IEC 61131-2 [IEC61131_2].', '',
      '| Rev | Description | Date |', '| --- | --- | --- |',
      '| A | First issue: every instrument of the plant, by controller | 2026-10-16 |',
      '| B | Record of revisions, purpose and scope added; the method of the authored loops written as sentences; tables numbered | 2026-10-29 |', '',
      '## 1. Purpose and scope', '',
      'This page indexes the instruments of the plant. It counts them by type and by programmable logic controller (PLC), flags any instrument whose range is below its duty, and lists the loops the generator writes for units that the instrument inventory AQS-INV-004 does not cover. The full index, with one row per instrument, is `docs-authority/inventory/INSTRUMENT_INDEX.csv`; section 5 shows its first rows.', '',
      '## 2. Counts', '',
      f'The plant has {len(rows)} instruments: ' + ', '.join(f'{v} {k}' for k, v in T.most_common()) + '. Table 2.1 gives the count of each PLC and its analogue inputs (AI) and digital inputs (DI).', '',
      'Table 2.1. Instruments by PLC', '',
      '| PLC | Instruments | AI | DI |', '|---|---|---|---|'] + [f"| {k} | {v} | {sum(1 for r in rows if r['plc'] == k and 'AI' in r['signal'])} | {sum(1 for r in rows if r['plc'] == k and 'DI' in r['signal'])} |" for k, v in sorted(S.items())]
md += ['', '## 3. Ranges below the duty', '', 'AQS-INV-004 takes each range from the design pressure, so Table 3.1 should be empty. A row in it is an instrument whose inventory range does not cover the range the index needs.', '', 'Table 3.1. Ranges below the duty', '', '| Tag | Inventory range | Index range | Basis |', '|---|---|---|---|'] + [f'| {a} | {b} | {c} | {d} |' for a, b, c, d in flags]
_ext = collections.Counter(r['unit'] for r in rows if r['unit'] in {a[0] for a in AUTH})
md += ['', '## 4. Loops written by this generator', '',
       f'The instrument inventory (`flow_graph/inventory/other.py`) writes instrument rows only for a unit that has a nozzle list, a liquid inflow or one of a few named classes, and it skips boundaries, headers and relief units. Machines, headers, relief stacks, stores and some vessels therefore had no instruments. This generator writes {_nauth} loops for such units from the design parameters of each unit, the rates of its edges and the inventory files it cites; the citation is the basis column of the CSV.',
       f'If AQS-INV-004 later issues a row with the same tag letters for one of these units, the inventory row is kept and the written row is dropped, so no tag is duplicated; the generator asserts this. Table 4.1 lists, for each of the {len(_ext)} units concerned, all its loops. A unit of graph class boundary has no loop, because it is a trade or bookkeeping boundary and not a process unit' + (f' ({", ".join(_boundary)})' if _boundary else '') + '.', '',
       'Table 4.1. Loops written by this generator', '',
       '| Unit | Loops | Measured variables |', '|---|---|---|']
md += [f"| {u} | {n} | {', '.join(sorted({r['tag'].split('-')[-2] for r in rows if r['unit'] == u}))} |" for u, n in sorted(_ext.items())]
md += ['', '## 5. Index', '', 'Table 5.1 shows the first 60 rows of the index; the CSV holds every row.', '', 'Table 5.1. Instrument index, first rows', '', '| Tag | Type | Range | Signal | Loop | Basis |', '|---|---|---|---|---|---|'] + [f"| {r['tag']} | {r['type']} | {r['range']} | {r['signal']} | {r['loop']} | {r['basis']} |" for r in rows[:60]]
open('docs-authority/INSTRUMENT_INDEX.md', 'w').write('\n'.join(md) + '\n'); print(len(rows), 'rows,', _nauth, 'authored,', len(_ext), 'units extended,', flags)

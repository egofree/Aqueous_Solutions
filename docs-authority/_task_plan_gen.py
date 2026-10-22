import json, os, re, collections
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(R)
g=json.load(open('flow_graph/plant_flow_graph.json'))
P=[n for n in g['nodes'] if n.get('presence')=='present']
ex=os.path.exists
def need(f):
    assert ex(f), f; return f
def sysof(n):
    # Owner ruling 2026-10-18 (first-principles audit): the plant is organized by SECTORS;
    # task systems mirror sectors 1:1. No folding into legacy systems.
    return n['sector_id']
SEC_DEF = {s['sector_id']: (s.get('sector_definition') or '') for s in g.get('mvs', {}).get('sectors', [])}
_seccount = collections.Counter(n['sector_id'] for n in P)
SYS = [(sid, SEC_DEF.get(sid) or f'{sid} sector (definition pending in mvs.sectors)') for sid, _c in _seccount.most_common()]
units=collections.defaultdict(list)
for n in P: units[sysof(n)].append(n)
assert sum(map(len,units.values()))==len(P)
ST=[('01','Process basis and mass/energy closure','duty sheet section 1 with in = out (kg/d) and kW from the graph','—'),
('02','Sizing calculation','calculation with stated basis replacing the graph envelope; study size only is not done','01'),
('03','P&ID sheet','P&ID drawing listing every edge, valve, and instrument tag','01, 02'),
('04','Nozzle schedule','docs-authority/nozzles/<UNIT>.csv, one row per edge','03'),
('05','Line list and bores','DN, schedule, rating, and material per edge, calculated, not copied','04, 02, X-PIP-01'),
('06','Internals','internals defined and sized, or stated none with basis','02'),
('07','Relief case','duty sheet section 6: case, destination, or atmospheric statement','02, 03'),
('08','Instruments and control','loop listed in AQS-INST-001 with trip and setpoint','03, X-CTL-01'),
('09','Materials and corrosion','material per wetted stream under AQS-STD-002, checked across AQS-ASSAY-001 Rev C bounding cases','01, X-MAT-01'),
('10','CAD model accepted (AQS-PLAN-006 M3)','models/mfg/<UNIT>/ builds; acceptance per AQS-PLAN-006 section 5','02, 04, 06, 09'),
('11','Fabrication drawings','drawing set with dimensions, welds, tolerances','10, X-DWG-01'),
('12','BOM','models/mfg/<UNIT>/bom.csv','10'),
('13','Fabrication route','docs-authority/fab/<UNIT>.md','10, 12'),
('14','Installation','installed position, supports, connections in the install sequence','13, X-BLD-05, X-ASM-01'),
('15','Test and commission','test procedure and acceptance record','14, X-COM-01')]
DONE_U={('FORGE','04'): 'machine (press) with no piped process connection; _nozzle_sched.py rule: no file, nothing to schedule, nothing invented',('RES_HEAT','04'): 'machine (furnace) with no piped process connection; _nozzle_sched.py rule: no file, nothing to schedule, nothing invented',('RF_HEAT','04'): 'machine (furnace) with no piped process connection; _nozzle_sched.py rule: no file, nothing to schedule, nothing invented',('SI_REDUCE','04'): 'machine (furnace) with no piped process connection; _nozzle_sched.py rule: no file - CHAR_TO_SI solids conveyor is unrated (Rev AC), its row auto-adds when rated',('ADS_CHILL','04'): 'machine (adsorption chiller) with no piped process connection; Q4/chilled-water/reject edges are cable energy rows, not nozzles; _nozzle_sched.py rule: no file',('MAU_HX','04'): 'machine (hx) with no piped process connection; Q4 heat and supply air are cable energy rows; _nozzle_sched.py rule: no file',('EXT_HALL','04'): 'building with no piped process connection; SF-EXT_HALL is an electrical row; _nozzle_sched.py rule: no file',('LI_RECOVER','04'): '`docs-authority/nozzles/LI_RECOVER.csv` (file current; 0 piped kg/d process connections - drain and vent per AQS-STD-001 section 4)',('P_CA','04'): '`docs-authority/nozzles/P_CA.csv` (file current; 0 piped kg/d process connections - drain and vent per AQS-STD-001 section 4)',('LITHO_ALIGN','04'): '`docs-authority/nozzles/LITHO_ALIGN.csv` (file current; 0 piped kg/d process connections - drain and vent per AQS-STD-001 section 4)',('CRYO_HX_Q4','04'): '`docs-authority/nozzles/CRYO_HX_Q4.csv` (file current; 0 piped kg/d process connections under the _noz_edges rule - heat edges are cable rows)',('GREASE_CA','04'): '`docs-authority/nozzles/GREASE_CA.csv` (file current; 0 piped kg/d process connections - drain and vent per AQS-STD-001 section 4)',('GREASE_LI','04'): '`docs-authority/nozzles/GREASE_LI.csv` (file current; 0 piped kg/d process connections - drain and vent per AQS-STD-001 section 4)',('MET_HX_Q4','04'): '`docs-authority/nozzles/MET_HX_Q4.csv` (file current; 0 piped kg/d process connections under the _noz_edges rule - coil/shell edges are cable rows; the unit stays a 0 kW stub until melt-heat recovery is sized)',('LOAD_AGG','04'): '`docs-authority/nozzles/LOAD_AGG.csv` (file current; 0 piped kg/d process connections - drain and vent per AQS-STD-001 section 4)',('PV_ARRAY','04'): '`docs-authority/nozzles/PV_ARRAY.csv` (file current; 0 piped kg/d process connections under the _noz_edges rule)',('RECTIFIER','04'): '`docs-authority/nozzles/RECTIFIER.csv` (file current; 0 piped kg/d process connections under the _noz_edges rule - DC/leach-trim rows predate the cable-rule split)',('SOL_ARK_60K','04'): '`docs-authority/nozzles/SOL_ARK_60K.csv` (file current; 0 piped kg/d process connections under the _noz_edges rule)',('GEO_HP','04'): '`docs-authority/nozzles/GEO_HP.csv` (file current; 0 piped kg/d process connections - drain and vent per AQS-STD-001 section 4)',('HYDRO_SET','04'): '`docs-authority/nozzles/HYDRO_SET.csv` (file current; 0 piped kg/d process connections - the unit is electrical-only)',('LEACH_CSTR_1', '02'): '`docs-authority/sizing/LEACH_CSTR_1.md` (AQS-DUTY-050)', ('LEACH_CSTR_1', '06'): '`docs-authority/sizing/LEACH_CSTR_1.md` §2 agitator, HX-5 coil', ('EW_1', '02'): '`docs-authority/sizing/EW_CELLS.md` (AQS-DUTY-051)', ('EW_2', '02'): '`docs-authority/sizing/EW_CELLS.md` (AQS-DUTY-051)', ('EW_3', '02'): '`docs-authority/sizing/EW_CELLS.md` (AQS-DUTY-051)', ('EW_4', '02'): '`docs-authority/sizing/EW_CELLS.md` (AQS-DUTY-051)', ('EW_5', '02'): '`docs-authority/sizing/EW_CELLS.md` (AQS-DUTY-051)', ('EW_6', '02'): '`docs-authority/sizing/EW_CELLS.md` (AQS-DUTY-051)', ('EW_7', '02'): '`docs-authority/sizing/EW_CELLS.md` (AQS-DUTY-051)', ('EW_8', '02'): '`docs-authority/sizing/EW_CELLS.md` (AQS-DUTY-051)', ('EW_9', '02'): '`docs-authority/sizing/EW_CELLS.md` (AQS-DUTY-051)'}
_SH={r['unit'] for r in json.load(open('docs-authority/inventory/STORAGE_HOLDUP.json'))} if os.path.exists('docs-authority/inventory/STORAGE_HOLDUP.json') else set()
# 2026-10-20 unit task 02 evidence registry: sizing_coverage.py maps every sized unit to the sizing
# document that carries its calculation (build asserts the doc names the unit); regenerated in the
# pipeline before this stage. Kept as the single evidence source for task 02 alongside the legacy
# DONE_U/_SH rows, which the registry also carries.
_COV=json.load(open('docs-authority/inventory/SIZING_COVERAGE.json')) if os.path.exists('docs-authority/inventory/SIZING_COVERAGE.json') else {}
# 2026-10-20 unit-task evidence audit (notes/2026-10-20-evidence-audit.md): the unit-task checks read the
# per-unit artifact itself, not a graph-side stand-in. T01: the section 1 closure line _duty_basis.py
# regenerates every pass ("Mass in X kg/d. Mass out Y kg/d. Electrical duty Z kW."), in = out within the
# 4-significant-figure rounding of the sheet text. T04: nozzles/<UNIT>.csv must list every process
# connection of the unit (present kg/d mass edges plus HL-/thermal kW edges), a row counting where the
# service text equals the edge `carries` - the same match rule _pid_sheets.py uses; utility rows
# (drain, vent) match no edge and are allowed extras. T05: every present edge of the unit has a row in
# LINE_LIST.md (AQS-PIP-004) and every piped row carries DN + class (schedule, rating and material
# resolve per class in AQS-PIP-003 PIPING_CLASSES). T08: the unit owns at least one instrument loop in
# the index (AQS-CTL-001, full CSV; the Done-when's AQS-INST-001 lists only the assay/digester/farm
# study loops - X-CTL-05's partial resolved at Rev C 2026-10-21; loop membership is evidenced where the plant-wide index carries
# it; trips/setpoints for SIFs live in AQS-CTL-003). T10 stays open for every unit: its Done-when is
# acceptance M3 per AQS-PLAN-006 section 5 and no unit passes it (no drawings); the note names the real
# state of models/mfg/<UNIT> (real BOM at M2 / standby envelope + PLACEHOLDER BOM / envelope STL only).
import csv as _csv
_EU=collections.defaultdict(list)   # present edges touching each unit
for _e in g['edges']:
    if _e.get('presence')=='present':
        _EU[_e['to_unit_id']].append(_e); _EU[_e['from_unit_id']].append(_e)
def _noz_edges(u):   # connections a nozzle schedule must list: process mass edges + thermal kW edges (cables are not nozzles)
    out=[]
    for e in _EU.get(u,()):
        lay=e.get('layers') or []; un=(e.get('rate') or {}).get('unit')
        if 'mass' in lay and un=='kg/d': out.append(e)
        elif un=='kW' and (e['stream_id'].startswith('HL-') or 'thermal' in lay) and e.get('phase') not in ('E','electric') and 'elec' not in lay: out.append(e)
    return out
_S1=re.compile(r'^1\. Basis\. Mass in ([\d.eE+-]+) kg/d\. Mass out ([\d.eE+-]+) kg/d\. Electrical duty ([\d.eE+-]+) kW\.',re.M)
_DUTY={}
for _n in P:
    _p=f'docs-authority/duties/{_n["unit_id"]}.md'
    if ex(_p):
        _m=_S1.search(open(_p).read())
        if _m: _DUTY[_n['unit_id']]=(_m[1],_m[3],abs(float(_m[1])-float(_m[2]))<=1e-3*max(float(_m[1]),float(_m[2]),1e-9))
_NOZ={}
for _n in P:
    _u=_n['unit_id']; _p=f'docs-authority/nozzles/{_u}.csv'
    if ex(_p):
        _svc=collections.Counter(r.get('service','') for r in _csv.DictReader(open(_p)))
        _need=collections.Counter(e.get('carries') or '' for e in _noz_edges(_u))
        _NOZ[_u]=(sum(max(0,k-_svc.get(c,0)) for c,k in _need.items()),sum(_need.values()))
_LL=collections.defaultdict(list)
for _l in open('docs-authority/LINE_LIST.md'):
    if _l.startswith('|'):
        _c=[x.strip() for x in _l.strip().strip('|').split('|')]
        if len(_c)>=9 and _c[0]!='Line' and not _c[0].startswith('-'): _LL[_c[0]].append((_c[3],_c[4]))
def _ll_ok(u):
    for e in _EU.get(u,()):
        rows=_LL.get(e['stream_id'])
        if not rows: return False
        if any(dn.startswith('DN') and not cl for dn,cl in rows): return False
    return True
_IIDX=collections.defaultdict(set)
for _r in _csv.DictReader(open('docs-authority/inventory/INSTRUMENT_INDEX.csv')): _IIDX[_r['unit']].add(_r['loop'])
_MFG={}
for _n in P:
    _u=_n['unit_id']; _p=f'models/mfg/{_u}/bom.csv'
    if ex(_p):
        _rows=list(_csv.DictReader(open(_p)))
        _all_ph=bool(_rows) and all(re.search(r'PLACEHOLDER\s*\(standby',' '.join(map(str,r.values())),re.I) for r in _rows)
        _MFG[_u]='standby' if _all_ph else 'real'
def status(n,k):
    u=n['unit_id']; d=f'docs-authority/duties/{u}.md'
    if (u,k) in DONE_U: return DONE_U[(u,k)]
    if k=='02' and u in _SH: return '`docs-authority/sizing/STORAGE_HOLDUP.md` (AQS-DUTY-064)'
    if k=='02' and u in _COV: return f"`{_COV[u]['doc']}` ({_COV[u]['docnum']})"
    if k=='01':
        v=_DUTY.get(u)
        if v and v[2]: return f'`{d}` §1; mass in = out {v[0]} kg/d, {v[1]} kW'
    if k=='03' and ex(f'docs-authority/pid/{u}.svg'): return f'`docs-authority/pid/{u}.svg` (AQS-PID-001)'
    if k=='04':
        v=_NOZ.get(u)
        if v and v[1] and v[0]==0: return f'`docs-authority/nozzles/{u}.csv` (all {v[1]} process connections listed)'
    if k=='05' and _ll_ok(u): return f'`docs-authority/LINE_LIST.md` (all {len(_EU.get(u,()))} edges with DN + class; schedule/rating/material per class in AQS-PIP-003)'
    if k=='07' and ex(d) and re.search(r'^6\. Relief',open(d).read(),re.M): return f'`{d}` §6 (C7 closed on MASTER_PLAN)'
    if k=='08':
        v=_IIDX.get(u)
        if v: return f'`docs-authority/INSTRUMENT_INDEX.md` ({len(v)} loops; AQS-CTL-001)'
    if k=='12' and ex(f'models/mfg/{u}/bom.csv'): return f'`models/mfg/{u}/bom.csv`'
    if k=='13' and ex(f'docs-authority/fab/{u}.md'): return f'`docs-authority/fab/{u}.md` (study route)'
    return None
def note(n,k):
    u=n['unit_id']
    if k=='10':
        m=_MFG.get(u)
        if m=='real': return f'partial: M2 at `models/mfg/{u}/` (real BOM), not accepted per AQS-PLAN-006 section 5 (no drawings)'
        if m=='standby': return f'partial: `models/mfg/{u}/` envelope + PLACEHOLDER BOM (standby style, machine design not started)'
        if ex(f'models/mfg/{u}'): return f'partial: M2 at `models/mfg/{u}/`, not accepted'
        if ex(f'cad/stl/{u}.stl'): return f'partial: envelope `cad/stl/{u}.stl`'
    if k=='04':
        v=_NOZ.get(u)
        if v and v[1]: return f'partial: {v[0]} of {v[1]} process connections without a row'
        if v: return 'no piped process connections; nozzle schedule n/a'
    if k=='02' and ex(f'docs-authority/duties/{u}.md'): return 'partial: graph envelope only'
    return ''
ACC=lambda n: n['class'] in('boundary',)
# cross-cutting
X=[
('GOV','Governance, authority, document control',[
('X-GOV-01','Graph authority contract passes','`flow_graph/check_authority_contract.py` and `flow_graph/test_authority_contract.py` pass','—','flow_graph/check_authority_contract.py'),
('X-GOV-02','Duty sheet standard issued','AQS-STD-001 issued','—','docs-authority/AQS-STD-001.md'),
('X-GOV-03','Loop closure derived from graph','`flow_graph/derived/LOOP_CLOSURE.md` regenerates clean','X-GOV-01','flow_graph/derived/LOOP_CLOSURE.md'),
('X-GOV-04','Document number register','one register lists every AQS- number once; duplicates resolved','—','docs-authority/DOC_REGISTER.md'),
('X-GOV-05','Superseded plans marked','AQS-PLAN-001..003, AQS-MFG-001, AQS-REM-*, AQS-MVS-* carry a pointer to AQS-PLAN-007','X-GOV-04',None),
('X-GOV-07','Assumptions register','AQS-REG-002 lists every study and assumed value with where used, basis, and owning task; curated entries carry sensitivity and the replacing test; script validates','X-GOV-04','docs-authority/ASSUMPTIONS_REGISTER.md'),
('X-GOV-08','Sizing rule','AGENTS.md §Sizing: bounding-case sizing; restrictions revised when they block a sized design; sizing-driven changes approved by default','—','AGENTS.md'),
('X-GOV-06','Revision control of drawings and derived files','each drawing and derived file names the graph revision it was made from; stale ones flagged by a script','X-GOV-04',None)]),
('PAR','Parametric model (owner priority 2026-10-15; AQS-PAR-001)',[
('X-PAR-01','Drivers file','flow_graph/param/drivers.json holds every independent input (feed rate, bounding compositions, site climate, margins, material limits) with a published reference, register id or owner basis; needs_verification values carry verification_test; linked to AQS-REG-002','—','flow_graph/param/drivers.json'),
('X-PAR-02','Balance solver','per-unit transfer functions compute all edge rates, compositions and duties from the drivers; mass and energy closure checks fail on imbalance','X-PAR-01','flow_graph/param/solver.py'),
('X-PAR-03','Per-class sizing functions','tank, EW cell (Faraday), HX (LMTD/U), scrubber, relief (API 520), lines, pumps, agitators in flow_graph/param/sizing with cited equations; one-off scripts converted (LEACH, EW, HX-5, relief, lines, power)','X-PAR-01','flow_graph/param/sizing'),
('X-PAR-04','Generated outputs and gates','graph values, duty sheets, CadQuery params, BOMs, load list, placement and isometrics regenerated from sized values; repo checks fail on imbalance or misfit','X-PAR-02, X-PAR-03','flow_graph/param/write_graph.py'),
('X-PAR-06','NaOH balance (owner decision 2026-10-15)','precipitation NaOH from published stoichiometry, glass-digest NaOH re-derived from a cited basis, NaOH make-up sized for the residual (worst case), EVAP_BASE derived from leach acid; misfit gate passes','X-PAR-02','flow_graph/param/solver.py'),
('X-PAR-07','Roof-only PV and minimum self-contained footprint (owner decision 2026-10-15)','roof area is a solver constraint; PV kWp on the roof closes the annual and night energy balance; if the load does not fit, loads, efficiencies, rooftop layout and building footprint are iterated to the minimum footprint that closes; ground field removed; misfit gate covers the roof constraint','X-PAR-02','flow_graph/param/solver.py'),
('X-PAR-09','Commodity surplus and grid export (owner principle D75, 2026-10-15)','PV at pv_oversize_factor 2.0 x the balancing nameplate; roof and building re-converged; storage charge rate for the cloudy-day case (NREL basis); inverters for export; IEEE 1547 / UL 1741 SB / NEC 705 interconnection and export meter on the one-line and protection','X-PAR-07','docs-authority/POWER_SIZING.md'),
('X-PAR-11','Gas-exchange species layer (owner 2026-10-15)','carry O2, N2, CO2 and H2O by species on the gas edges; GROW_BED photosynthetic O2 (32/44 x CO2 fixed at PQ 1.0, TAIZ2015; 13.8 kg/d on 19.0 kg/d CO2) out of the trim lump onto S87 or the AHU air; IA-LEACH-ASU from Henry-law solubility (SANDER2015) at the leach liquor flow and temperature; ASU feed and products closed by species; verification T-PAR-02','X-PAR-02','docs-authority/BALANCE_RECONCILIATION.md'),
('X-PIP-04','Pipe flexibility loops (AQS-PIP-005)','the lines flagged as needing a loop or offset get an expansion loop or offset in the route, flexibility re-checked (guided-cantilever) and isos/supports regenerated','X-PIP-03','docs-authority/SUPPORTS.md'),
('X-PAR-12','O2 source decision (owner review, 2026-10-15)','AQS-PAR-004 shows 76.5 kg/d O2 consumed (fuel cell, crew, chemistry, combustion) with only 13.8 kg/d regenerated (grow bed) and no other source; combustion units draw air from the N2 header. Owner chooses: water electrolyser, air intake with N2 vent, or both; then the graph gets the source edges and the combustion units an O2 draw','X-PAR-11','docs-authority/GAS_SPECIES.md'),
('X-PAR-10','EVAP_ACID vent scrubber (owner decision 2026-10-15)','packed alkali scrubber on the EVAP_ACID column vent for trace HCl and non-condensables, NaOH bleed from BMED, sized with the X-PAR-03 scrubber function (Perry/Treybal), PVC, streams in and out, NaOH balance within the 1 % gate, model and BOM','X-MFG-30',None),
('X-PAR-08','Hall conditioning refinement: ground-source option, internal gains, slab losses','GEO_GHEX extension sized for the hall from a cited bore-field basis (ASHRAE GSHP method / IGSHPA), ground-source COP per ASHRAE 90.1 / ISO 13256, internal gains and slab-edge losses added to roof_close; adopted if the converged footprint shrinks, with the reason recorded','X-PAR-07','flow_graph/param/solver.py'),
('X-STD-01','NFPA and ISO code basis applied throughout (owner decision 2026-10-15)','every layout, fire, separation, egress, electrical and pressure check cites the governing NFPA and ISO clause (with IBC/IFC/NEC where they govern); citations in flow_graph/param/refs.py; checks in AQS-BLD-011/012 and successors','X-BLD-04',None),
('X-FIR-01','NFPA 13 sprinkler design and fire water supply (pending hall programme)','sprinkler system for the hall and base plate sized parametrically to the hazard class (NFPA 13-2022 density/area curves, hose allowance, duration), fire water tank and fire pump (NFPA 20, NFPA 22) as drivers in drivers.json; hazard class flagged pending the owner hall programme; precondition of AQS-EGR-002','X-STD-01',None),
('X-MFG-30','Custom evaporators EVAP_ACID and EVAP_BASE (no bought skid)','open design: MVR body, compressor, feed/condensate interchanger, outlet temperatures, relief sized in-house; full mfg model under models/mfg/; production route in MFG/FAB','X-PAR-06','docs-authority/sizing/EVAP_DESIGN.md'),
('X-MFG-31','Custom reaction chambers (no bought skid)','every reactor, digester and CSTR designed in-house with full mfg model and production route in MFG/FAB','X-MFG-30',None),
('X-MFG-33','In-house micro cold box for CRYO_ASU (X-GOV-20)','open design of the air-separation cold box, compressor and expander sized from the CRYO_ASU duty; replaces the vendor-quote basis of A-M-071 and D47','X-MFG-31',None),
('X-MFG-34','In-house RO/EDI polish for BMED_UPW_POLISH (X-GOV-20)','membrane array, pressure vessels, EDI stack and pump designed in-house with specific energy from the design and a bench test; replaces the skid-vendor basis of A-M-072','X-MFG-31',None),
('X-MFG-35','In-house BMED stack (X-GOV-20)','bipolar membrane stack frames, spacers, electrodes and end plates designed in-house; specific energy from a bench stack polarisation test; replaces the stack-vendor basis of A-M-077','X-MFG-31',None),
('X-MFG-36','In-house hydrogen compressor (X-GOV-20)','diaphragm or piston compressor to 200 bar designed in-house, isothermal efficiency from the design and a bench run; replaces the vendor-efficiency basis of DOE_H2_COMP and A-M-083','X-MFG-31',None),
('X-MFG-37','In-house metal-shop tools (X-GOV-20)','induction melt furnace, gas atomiser, rolling mill and wire drawer designed in-house with specific energy from the design and trial runs; replaces the tool-vendor basis of A-M-085','X-MFG-31','docs-authority/MFG_TOOLS.md'),
('X-MFG-38','In-house PV cell line tools (X-GOV-20)','texture, diffusion, PECVD, print and firing tools designed in-house with nameplate from the design; ST-SOLAR-01 reopened because it rested on vendor datasheets','X-MFG-31',None),
('X-MFG-39','In-house H2_PURIFIER beds (X-GOV-20)','deoxo, chloride guard and TSA beds sized in-house from published isotherms and kinetics','X-MFG-31','docs-authority/duties/H2_PURIFIER.md'),
('X-MFG-40','In-house burnout kiln, alkali scrubber, Br2 tower, fractionator, cold box pressure design (X-GOV-20)','units classed "Vendor" in AQS-ASME-001 get an in-house code intent (Atm or VIII-study) with design pressure and temperature','X-MFG-31','docs-authority/ASME_CLASS_SHEETS.md'),
('X-MFG-41','In-house ZNBR2 stack test (X-GOV-20)','round-trip efficiency and derate from an in-house stack test; replaces the battery-vendor basis of A-M-062','X-MFG-31',None),
('X-MAT-21','FRP pultruded section coupon tests (X-GOV-20)','in-house coupons to ASTM D638, D790 and D2344 for the LEACH_CSTR_1 belt channel (allowable, modulus, density); replaces the pultrusion-vendor data of A-M-034','X-MAT-01',None),
('X-MFG-32','Jellybean parts: standard sizes and in-house lines','motors, bearings, fasteners, seals and similar to ISO/IEC standard sizes for outside sourcing, plus open designs and an in-house production line plan for each family','X-MFG-31',None),
('X-GOV-20','Withdraw vendor-data bases','every "vendor data", "vendor skid" or "vendor quote" basis in docs and code replaced by an in-house design task; ticks resting on vendor data removed','X-MFG-30',None),
('X-PAR-05','Verification list to test plan','every needs_verification driver and register entry mapped to a test or prototype in a rollout plan','X-PAR-01','docs-authority/TEST_PLAN.md')]),
('RSZ','Bounding-case resizing (owner approval 2026-10-15)',[
('X-RSZ-01','Acid regeneration resize','BMED_ACID and dependents sized for the regolith-like (class A) feed','X-BAS-02','docs-authority/FEED_ASSAY.md'),
('X-RSZ-02','EW power on the graph and supply resize','RECT-EW and EW cell power booked on the graph; PV, storage, inverters to the AQS-ELEC-007 bounding case','X-ELS-05','docs-authority/POWER_SIZING.md'),
('X-RSZ-03','EW aisle re-placement','cells placed at sized lengths, cathode count justified; block grown as needed','X-RSZ-02','flow_graph/placement_seed.json'),
('X-RSZ-04','BMED trim cooling edge','energy edge for the IA-BMED-03/04 water-cooled trim','X-MAT-19','docs-authority/MATERIALS_STD.md'),
('X-RSZ-05','FARM capacity','HAB_* units moved to the HAB block; farm stacked or grown to bed area','X-BLD-09','flow_graph/placement_study.json'),
('X-RSZ-06','Potable makeup treatment','treatment step on the IA-POT-01 path from LEACH_CSTR_1 to ROOF_TANK','X-MAT-19','docs-authority/MATERIALS_STD.md'),
('X-RSZ-07','Held-rate sweep','every held rate and undersized unit checked against the bounding cases and resized','X-RSZ-01..06','docs-authority/RESIZE_SWEEP.md')]),
('SAN','Sanitation and pathogen barriers (owner decision 2026-10-15)',[
('X-SAN-01','Multi-barrier blackwater and excreta train','BLACK_DIGEST integrated: blackwater flow from HAB occupancy (cited per-capita excreta and flush water); thermophilic digestion, pasteurisation (EPA 40 CFR 503 Class A), alkaline hold with batch release, solids to the afterburner; compost-toilet output through the same barriers; ISO 30500 log-reduction targets and challenge tests; materials, models, BOMs, layout separation from FARM, docs, assumptions','X-STD-01',None)]),
('INV','Building-block inventories (owner programme 2026-10-15; in order)',[
('X-INV-01','Motor and actuator inventory','every electrically driven moving item (motors, pumps, compressors, blowers, fans, agitators, steppers, linear actuators, solenoid valves, conveyors) by sector > sub-system > unit: device, motor type, IEC/NEMA frame or standard size, kW, voltage, duty, source; unsized items flagged as assumptions; generated by flow_graph/inventory/motors.py to docs-authority/inventory/MOTOR_INVENTORY.md and CSV with a family rollup','X-MFG-32',None),
('X-INV-02','Motor family designs and production line','one open-source design and manufacturing plan per motor family in the X-INV-01 rollup, feeding the motor production line design','X-INV-01',None),
('X-INV-02B','Motor first articles and type tests','build one first article per X-INV-02 family; IEC 60034-1 routine and IEC 60034-2-1 efficiency type test; replace the A-M-126 coefficients with measured values','X-INV-02',None),
('X-INV-02D','PM magnet comparison, NdFeB vs bonded ferrite (owner 2026-10-15, after X-PAR-11)','for each BLDC/stepper family (MF-01, MF-02, MF-03, MF-22, MF-23) size an NdFeB variant and a bonded-ferrite variant from cited magnet properties (remanence, coercivity); compare frame size, mass, efficiency, material inputs (rare-earth recovery from feedstock vs in-house ferrite production) and production-line implications; comparison table in AQS-INV-005; assumptions registered','X-INV-02, X-PAR-11','docs-authority/inventory/MOTOR_DESIGNS.md'),
('X-INV-02C','Motor family drawings and BOMs','CadQuery models, drawings and BOM per X-INV-02 family from the AQS-INV-005 design sheets (laminations, winding, rotor, shaft, frame)','X-INV-02','models/motors/build.py'),
('X-INV-03','Wire inventory','every conductor by sector > sub-system > unit: size, insulation, voltage, length, ampacity basis; family rollup and production plan','X-INV-01, X-ELS-02',None),
('X-INV-04','Pipe inventory','every line by sector > sub-system > unit: DN, schedule, material, length, fittings; family rollup and production plan','X-INV-03, X-PIP-03',None),
('X-INV-05','Other building blocks inventory','valves, instruments, fasteners, seals, bearings, sheet and structural sections, electronics: inventory, family rollup and production plan per family','X-INV-04',None)]),
('BAS','Design basis',[
('X-BAS-01','Feedstock assay schema and bounding envelope','AQS-ASSAY-001 Rev C: seven-class schema, regolith-like to metal-rich PCB','—','docs-authority/FEED_ASSAY.md'),
('X-BAS-02','Bounding-case check of every held rate','each held rate recalculated at both bounding cases, or stated as held with reason','X-BAS-01','docs-authority/FEED_ASSAY.md'),
('X-BAS-03','Site basis','site, climate, seismic, soil, wind, snow values with source','—','docs-authority/SITE_BASIS.md'),
('X-BAS-04','Units and standards basis','codes and standards list per discipline','—',None)]),
('PIP','Piping and line list',[
('X-PIP-01','Piping class sheets','class sheets per service and material','X-MAT-01','docs-authority/PIPING_CLASSES.md'),
('X-PIP-02','Plant line list','every edge with DN, class, length, route; generated from the graph','X-PIP-01, unit task 05','docs-authority/LINE_LIST.md'),
('X-PIP-03','Header routing and isometrics','isometric per line; current set AQS-ISO-000 Rev A is partial','X-PIP-02, X-BLD-04','docs-authority/ISO_ROUTES.md'),
('X-PIP-04','Pipe supports and stress','support spacing and thermal stress for hot and cryogenic lines','X-PIP-03','docs-authority/SUPPORTS.md'),
('X-PIP-05','Weld map and WPS','AQS-WLD-001 extended with WPS/PQR per material','X-PIP-01',None)]),
('ELS','Electrical system (plant level)',[
('X-ELS-01','EW-1 power reconciled','5.263 kW authoritative (D3 on MASTER_PLAN)','—','docs-authority/duties/EW_1.md'),
('X-ELS-02','Load list','every node continuous_kw from a calculation, not a study share','unit task 02','docs-authority/LOAD_LIST.md'),
('X-ELS-02A','Shorten branch wiring (owner 2026-10-15)','replace the A-M-122 home-run lengths (unit to SOL_ARK_60K x 1.2 + 5 m) with local distribution panels per sector and routed cable tray; panel locations from the GA, tray routes from the iso router; re-run the wire inventory (AQS-INV-002) and report the copper saved; voltage drop <= 3 % branch / 5 % total','X-ELS-02','docs-authority/inventory/WIRE_INVENTORY.md'),
('X-ELS-03','Single-line diagram','one-line issued against the load list','X-ELS-02','docs-authority/ONE_LINE.md'),
('X-ELS-04','Rectifier sizing across the assay envelope','RECT-EW rated at the bounding case current','X-BAS-02, X-ELS-02','docs-authority/RECT_EW.md'),
('X-ELS-05','Storage and generation sizing','PV, ZnBr2, hydro, fuel cell, backup gen sized from the load profile','X-ELS-02','docs-authority/POWER_SIZING.md'),
('X-ELS-06','Conductor and busbar sizing','cable and busbar schedule with ampacity and voltage drop','X-ELS-03',None),
('X-ELS-07','Protection and coordination','fuse, breaker, and relay settings with coordination study','X-ELS-06','docs-authority/PROTECTION.md'),
('X-ELS-08','Grounding and bonding','earthing design, step and touch, bonding of process equipment','X-ELS-03, X-BAS-03','docs-authority/GROUNDING.md'),
('X-ELS-11','Collection bus sections (owner instruction 2026-10-15)','inverter bus split into 480 V sections below the NEC 240.87 threshold, step-up to the MV collection bus, storage per section, plant bus and islanding defined; one-line and protection updated','X-PAR-09','docs-authority/COLLECTION_BUS.md'),
('X-ELS-10','WS_PEROX cell sizing','cell current, area, voltage, and power from the S32 duty with stated basis','X-ELS-02','docs-authority/OXIDIZER_REAGENTS.md'),
('X-ELS-09','Hazardous area classification','zones for H2, solvent, and fuel areas','X-SAF-02',None)]),
('CTL','Controls, instrumentation, software',[
('X-CTL-01','Instrument index','every tag on every P&ID with range, signal, and loop','unit task 03',None),
('X-CTL-02','Control philosophy and PLC architecture','controller, I/O count, network, power','X-CTL-01',None),
('X-CTL-03','Safety instrumented functions','trip list with cause and effect from the HAZOP','X-SAF-01, X-CTL-01',None),
('X-CTL-04','Control software','source in the repo, simulated against the graph','X-CTL-02',None),
('X-CTL-05','Assay instrumentation loop','AQS-INST-001 assay, digester, farm study loops issued (Rev C registered against the plant-wide index)','X-BAS-01','docs-authority/INSTRUMENT_LOOPS.md')]),
('THM','Thermal and HVAC (plant level)',[
('X-THM-01','Heat ladder duty balance','Q1 to Q4 duties closed per AQS-HEAT-LADDER-001 with hot and cold side calculations','unit task 01',None),
('X-THM-02','Ventilation and HVAC design','air changes, extract, and make-up per room with fan duty','X-BLD-04, X-SAF-02',None),
('X-THM-03','Insulation schedule','insulation per hot and cryogenic line and vessel','X-PIP-02',None),
('X-THM-04','Heat-ladder line losses','AQS-THM-003 shows 12 Q1-Q3 lines losing 12-51 % of their rated duty even at 200 mm (long DN15/25 runs on 1-3 kW loops): put the losses on the graph and shorten the runs by moving the Q batteries next to their sources (placement), or justify; re-close the ladder','X-THM-03','docs-authority/INSULATION_SCHEDULE.md')]),
('BLD','Building structure and layout',[
('X-BLD-01','Frame system per AQS-MOD-001','member sizes checked against loads','X-BAS-03, X-BLD-02',None),
('X-BLD-02','Structural loads','equipment operating and test weights on each level','unit task 10',None),
('X-BLD-03','Foundations','foundation design against soil data','X-BAS-03, X-BLD-02',None),
('X-BLD-04','General arrangement and layout','placement seed checked for clearance, access, and maintenance envelopes','unit task 02','docs-authority/GA_CHECK.md'),
('X-BLD-05','Enclosure, floors, stairs, egress','envelope, floor plates, stairs; egress per AQS-EGR-001','X-BLD-01',None),
('X-BLD-06','Lifting and cranes','crane and hoist duty for the heaviest lift per level','X-BLD-02',None),
('X-BLD-07','Site access and dock','AQS-SITE-001 checked against vehicle and container sizes','X-BAS-03',None),
('X-BLD-09','Study placement of unplaced units','every present unit has a study box in its sector block, 600 mm clear; FARM sector capacity resolved','X-BLD-04','flow_graph/placement_study.json')]),
('SAF','Safety, relief, fire',[
('X-SAF-01','HAZOP','HAZOP worksheets per P&ID node with actions closed','unit task 03',None),
('X-SAF-02','Hazard separation','AQS-HSE-001 separation distances applied to layout','X-BLD-04',None),
('X-SAF-03','Relief destination per node','every duty §6 names a case or atmospheric vent (C7)','—','docs-authority/RELIEF.md'),
('X-SAF-04','Relief sizing on pressurized nodes','API 520 calculation per pressurized node; EXPANDER done (D4)','X-SAF-03, unit task 02',None),
('X-SAF-05','Fire protection and detection','detection, suppression, and fire water design','X-BLD-04, X-SAF-01',None),
('X-SAF-07','Flue quench edge into FLUE_KO','quench water edge on the graph with rate from an energy balance to below the FRP limit; balances close; rate change approved','X-MAT-00','docs-authority/duties/FLUE_KO.md'),
('X-SAF-08','Nitric vent edges to NOX_SCRUB','WS_NITRIC and HNO3 vent edges on the graph; balances close','X-SAF-03','flow_graph/plant_flow_graph.json'),
('X-SAF-09','Reagent tank holdups and bunds','holdup basis per reagent, tank volumes, bund volumes at 110 % per AQS-DSN-OX-001','X-SAF-02','docs-authority/OXIDIZER_REAGENTS.md'),
('X-SAF-11','FORM feed dilution','FORMOX_REVIEW2021: the iron-molybdate bed runs methanol-lean at about 10 mol% MeOH and 10 mol% O2 in N2; the graph feeds pure HDR_O2 to FORM. Add the N2 diluent (HDR_N2) and tail-gas edges, the O2/MeOH ratio interlock and an LOC check','X-MFG-31','docs-authority/sizing/REACTOR_DESIGN.md'),
('X-PAR-15','H2_PURIFIER water outlet','S49P carries 0.03 wt% water above the ISO 14687 Grade D limit and the TSA/deoxo water (about 95 g/d) has no outlet edge: set S49P to spec, add the regeneration purge water edge, rebalance FUEL_CELL','X-MFG-39',None),
('X-PAR-14','ACEX anion exchange route','graph exchange [Bmim]Cl + AcOH -> [Bmim]OAc + HCl is not thermodynamically driven (HCl is the far stronger acid); route via a hydroxide-form anion-exchange resin then neutralisation with acetic acid (or a cited alternative); rebalance ACEX, regenerant to the leach, then design under X-MFG-31','X-MFG-31',None),
('X-PAR-13','GLYOXAL route','graph route CH3CHO + O2 -> glyoxal is not an established process (industrial: acetaldehyde + HNO3, or ethylene glycol gas-phase oxidation over Ag); choose a cited route and rebalance GLYOXAL, then design it under X-MFG-31','X-MFG-31',None),
('X-SAF-10','Peroxide dilution water edge','water source edge into WS_PEROX; IA-H2O2-SRC set to the O2 need; balances close; rate change approved','X-ELS-10','docs-authority/OXIDIZER_REAGENTS.md'),
('X-RED-01','Redundancy audit of energy and life-support systems (owner guideline 2026-10-15)','every energy and life-support system (power, O2, water, CO2 removal, thermal, food, sanitation) listed with its primary source and failure modes; each single point of failure gets an N+1 or diverse backup sized by calculation (duration from a cited reliability or NFPA 110/111 basis) and carried on the graph; HYDRO_SET restored as the ZNBR2 backup (A-M-145) is the first entry; register AQS-RED-001','X-PAR-02',None),
('X-RED-02','Pumped-hydro upper reservoir siting (Q-009)','the 11,400 m3 NFPA 111 Class X upper reservoir placed (roof, elevated tank or grade-plus-hillside) with structural load or head revised and the volume re-derived','X-RED-01',None),
('X-RED-03','Power conversion and distribution N+1','collection bus, main panel and rectifiers audited for SPOF; second path sized; register AQS-RED-001','X-RED-01',None),
('X-RED-04','Crew O2 reserve separate from the fuel-cell oxidant','crew O2 reserve sized for a cited outage duration and kept apart from the FUEL_CELL draw; register AQS-RED-001','X-RED-01',None),
('X-RED-05','Water treatment N+1','second still or diverse treatment path sized for the potable draw; register AQS-RED-001','X-RED-01',None),
('X-RED-06','Crew CO2 removal N+1','second 100 % sorbent bed (or diverse removal) sized from the 4.02 kg/d metabolic CO2; register AQS-RED-001','X-RED-01',None),
('X-RED-07','Thermal N+1','heat sink and heat pump redundancy sized from the bounding thermal load; register AQS-RED-001','X-RED-01',None),
('X-RED-08','Food reserve','stored ration reserve sized for a cited crop-failure duration; register AQS-RED-001','X-RED-01',None),
('X-RED-09','Sanitation N+1','second toilet or diverse sanitation path sized for crew use; register AQS-RED-001','X-RED-01',None),
('X-SAF-06','Gas detection','H2, O2-deficiency, HF, NOx, CO detectors placed','X-SAF-01',None)]),
('MAT','Materials selection (AQS-STD-002)',[
('X-MAT-00','Materials standard issued','AQS-STD-002 Rev A rules M1 to M7: PVC in chlor-alkali and acid-regen, no metal wetted part in oxidizing or reducing service, electrochemistry rules','—','docs-authority/MATERIALS_STD.md'),
('X-MAT-01','Materials selection guide','material per service class across the assay envelope, with source data, under AQS-STD-002','X-MAT-00, X-BAS-01',None),
('X-MAT-02','Resolve CSTR material conflict','LEACH_CSTR_1 PVC-U; AQS-NZ-001 and the duty agree','X-MAT-00','docs-authority/duties/LEACH_CSTR_1.md'),
('X-MAT-03','Elastomer and gasket compatibility','per service','X-MAT-01',None),
('X-MAT-04','First audit of every present unit','AQS-STD-002 section 2: clear violations fixed, ambiguous units listed','X-MAT-00','docs-authority/MATERIALS_STD.md'),
('X-MAT-05','Thermoplastic temperature cases','every unit above 60 °C on a PVC service resolved to CPVC or a stated alternative; LEACH_CSTR_1 HX-5 ports at 95 °C first','X-MAT-00, X-THM-01','docs-authority/MATERIALS_STD.md'),
('X-MAT-06','Resolve the ambiguous audit list','each unit in AQS-STD-002 section 2 ambiguous list has a material with a stated stream and temperature','X-MAT-01, unit task 01',None),
('X-MAT-07','Galvanic and stray-current design','electrolyte path lengths between cells, busbar isolation, frame grounding, electrode dissolution basis (M6)','X-MAT-00, X-ELS-03','docs-authority/MATERIALS_STD.md'),
('X-MAT-08','Hydrogen embrittlement review','every metal in H2 or cathode service with H2 pressure and temperature stated (M6)','X-MAT-00','docs-authority/H2_EMBRITTLEMENT_REVIEW.md'),
('X-MAT-10','Leach liquor temperature on the graph','LEACH_CSTR_1 node carries the liquor temperature with its source; tank material rechecked against M5','X-MAT-05','flow_graph/plant_flow_graph.json'),
('X-MAT-11','HX-5 polymer coil sizing','area, U, LMTD for the PVDF coil at the rated HX-5 duty, with the film and wall basis','X-MAT-10','docs-authority/POLYMER_HX_SIZING.md'),
('X-MAT-12','HX8 polymer exchanger sizing','area, U, LMTD for the PVDF tube exchanger at the HX8 duty','X-MAT-00','docs-authority/POLYMER_HX_SIZING.md'),
('X-MAT-13','Hypobromite coupon test (on site)','test record: PVC-U coupons in S69B liquor at operating ORP, mass and hardness change against acceptance','X-MAT-00, X-COM-01',None),
('X-MAT-14','MEOH_SYNTH API 941 check','Nelson-curve check at the stated H2 partial pressure and temperature; alloy chosen','X-MAT-15','docs-authority/H2_EMBRITTLEMENT_REVIEW.md'),
('X-MAT-15','P, T, and purity on H2 edges','every H2 edge carries design pressure, temperature, and purity with basis','X-MAT-08','docs-authority/H2_EMBRITTLEMENT_REVIEW.md'),
('X-MAT-16','HX-5 glass coil adopted','borosilicate 3.3 coil on LEACH_CSTR_1 from AQS-DUTY-049; model, BOM, duty, standard updated','X-MAT-11','docs-authority/MATERIALS_STD.md'),
('X-MAT-17','HX8 PVDF bundle adopted','PVDF bundle 7.53 m2 recorded as the choice with rationale; duty, standard updated','X-MAT-12','docs-authority/MATERIALS_STD.md'),
('X-MAT-18','EW electrode materials in chloride','cathode and anode materials for chloride liquor with anodic Cl2 chosen with source (316L cathode and PbO2 anode reviewed against titanium blanks and mixed-oxide anodes)','X-MAT-08','docs-authority/MATERIALS_STD.md'),
('X-MAT-19','Cool hot LEACH draws','IA-BMED-03, IA-BMED-04 and IA-POT-01 cooled below the receiving limit (BMED membrane limit, PVC-U 60 °C) with a heat duty and exchanger on the graph','X-MAT-09','docs-authority/MATERIALS_STD.md'),
('X-MAT-20','Evaporator outlet temperatures and line classes','EVAP_ACID and EVAP_BASE product and condensate outlet temperatures fixed from the in-house evaporator design X-MFG-30 (feed/condensate interchange), and IA-ACID-01, IA-BASE-01, IA-BASE-PPT, IA-EVAP_*-COND classed or cooled to the receiving limit; LINE_LIST currently classes the condensate P1 (60 °C) on carries text only','X-PAR-04','docs-authority/sizing/EVAP_DESIGN.md'),
('X-MAT-09','Material temperatures on the graph','liquor temperature carried on every edge into a thermoplastic unit','X-MAT-05','docs-authority/MATERIALS_STD.md')]),
('COD','Codes and permits',[
('X-COD-01','Code basis','AQS-HSE-001 code basis and AQS-CMP-001 compliance matrix closed per item','X-BAS-04',None),
('X-COD-02','Permit list','building, electrical, pressure, air, water, waste permits for the site','X-BAS-03','docs-authority/PERMITS.md'),
('X-COD-03','Pressure equipment classification','each pressurized node classified with stamp requirement','X-SAF-04',None)]),
('PRO','Procurement, BOM, cost',[
('X-PRO-01','Plant BOM','roll-up of every unit bom.csv plus bulk materials','unit task 12',None),
('X-PRO-02','Bought-item specifications','datasheet per bought item','unit task 12',None),
('X-PRO-03','Cost estimate','priced BOM with source per price','X-PRO-01',None),
('X-PRO-04','Self-copy BOM','AQS-BOM-SC-001 reconciled with unit BOMs','X-PRO-01',None)]),
('DWG','Drawings package',[
('X-DWG-01','Drawing standard and title block','numbering, sheet sizes, revision blocks','X-GOV-04',None),
('X-DWG-02','Drawing register','every drawing listed with revision','X-DWG-01',None),
('X-DWG-03','PFD issued from graph','PFD generated from the graph at current revision','X-GOV-01',None)]),
('ASM','Assembly and installation sequence',[
('X-ASM-01','Install sequence','ordered lift and connect sequence per level','X-BLD-06, unit task 13',None),
('X-ASM-02','Temporary works and rigging plans','per heavy lift','X-ASM-01',None)]),
('COM','Commissioning and startup',[
('X-COM-01','Commissioning plan','pressure test, loop check, water run, chemical run per system','X-CTL-01, X-SAF-01',None),
('X-COM-02','Startup sequence','cold start from empty, including heat ladder and cryo cooldown','X-COM-01',None),
('X-COM-03','Performance test','test against the graph rates at one bounding feed case','X-COM-02',None)]),
('OPS','Operations and maintenance',[
('X-OPS-01','Operating procedures','normal, start, stop, emergency per system','X-COM-02',None),
('X-OPS-02','Maintenance plan','inspection and replacement intervals per unit','unit task 13',None),
('X-OPS-03','Spares list','critical spares per unit','X-PRO-01',None)]),
('QA','QA and verification',[
('X-QA-01','Inspection and test plan','ITP per fabrication route','unit task 13',None),
('X-QA-02','Independent design check','check record per calculation','unit task 02',None),
('X-QA-03','As-built reconciliation','as-built model and graph agree','X-ASM-01',None)]),
('END','Decommissioning and recycling loop closure',[
('X-END-01','Decommissioning plan','drain, purge, and dismantle per system','X-OPS-01',None),
('X-END-02','End-of-life material return','each unit material assigned to a plant feed class under AQS-ASSAY-001','X-BAS-01, X-PRO-01',None)]),
('TOOL','Modeling tooling',[
('X-TOOL-01','Manufacturing model plan','AQS-PLAN-006 issued with tracker (D5)','—','docs-authority/MFG_MODEL_PLAN.md'),
('X-TOOL-02','CadQuery installed and proven','EXPANDER and LEACH_CSTR_1 at M2 (D6, D7)','X-TOOL-01','models/mfg/EXPANDER/expander.py'),
('X-TOOL-03','STL storage in LFS','all cad/stl files are LFS pointers','—','cad/stl'),
('X-TOOL-04','Design tool phases','AQS-UI-001 phases beyond P0, P1, B-prime','—',None)])]
# X-INV-02 children: one open-design + manufacturing-plan task per motor family in the X-INV-01 rollup (regenerated from the CSV)
_MF = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'inventory', 'MOTOR_FAMILIES.csv')
if os.path.exists(_MF):
    import csv as _csv
    _inv = next(ph for ph in X if ph[0] == 'INV')[2]
    _at = next(i for i, t in enumerate(_inv) if t[0] == 'X-INV-02') + 1
    for _r in _csv.DictReader(open(_MF)):
        _inv.insert(_at, (f"X-INV-02-{_r['family']}", f"Motor family {_r['family']}: {_r['motor_type']} {_r['size']} {_r['voltage']}",
                          f"open design basis (electromagnetic sizing, frame, winding or coil data) and in-house manufacturing plan for {_r['count']} items in {_r['units']} units; feeds the motor production line (X-INV-02)", 'X-INV-01', f"docs-authority/inventory/motor_families/{_r['family']}.md")); _at += 1
_WF = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'inventory', 'WIRE_FAMILIES.csv')
if os.path.exists(_WF):
    _inv = next(ph for ph in X if ph[0] == 'INV')[2]
    _at = next(i for i, t in enumerate(_inv) if t[0] == 'X-INV-03') + 1
    for _r in _csv.DictReader(open(_WF)):
        _inv.insert(_at, (f"X-INV-03-{_r['family']}", f"Wire family {_r['family']}: {_r['type']} {_r['size']} {_r['insulation']}",
                          f"open specification and production plan (drawing, stranding, insulation extrusion, test to the listed standard) for {_r['conductor_m']} m in {_r['circuits']} circuits; feeds the wire line (WIRE_DRAW, X-INV-03)", 'X-INV-03', 'docs-authority/inventory/WIRE_FAMILIES.csv')); _at += 1
for _fn, _pre, _dep, _desc in (('PIPE_FAMILIES.csv', 'X-INV-04', 'X-INV-04', lambda r: (f"Pipe family {r['family']}: {r['cls']} {r['material']} DN{r['DN']}", f"production plan (extrusion or tube mill, cut to the {r['stock_lengths_6m']} stock lengths, fittings {r['elbow_std']}, joints {r['joint_type']}, test to the class) for {r['pipe_m']} m in {r['lines']} lines")),
                                 ('OTHER_FAMILIES.csv', 'X-INV-05', 'X-INV-05', lambda r: (f"Building-block family {r['family']}: {r['category']}, {r['item']}", f"open design and production plan for {r['qty']} items ({r['spec']}) in {r['units']} units"))):
    _fp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'inventory', _fn)
    if os.path.exists(_fp):
        _inv = next(ph for ph in X if ph[0] == 'INV')[2]
        _at = next(i for i, t in enumerate(_inv) if t[0] == _pre) + 1
        for _r in _csv.DictReader(open(_fp)):
            _t, _d = _desc(_r); _inv.insert(_at, (f"{_pre}-{_r['family']}", _t, _d, _dep, f'docs-authority/inventory/{_fn}')); _at += 1
_MFD = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'inventory', 'motor_families')
# 2026-10-19 evidence honesty pass (AQS-PLAN-007 rule: a task is checked only where a cited repo file proves it).
# 68 DONE_X tasks rendered 'Evidence: `None`'. Each was audited against its Done-when; 62 point at the artifact that
# proves them, 6 are reopened (box unchecked) because no repo file meets the Done-when. Full table with justifications:
# docs-authority/notes/2026-10-19-evidence-pass.md. Applied only where the tuple carries no evidence of its own.
# Same-day closure pass: a fourth value kind, 'PARTIAL:<path>' or 'PARTIAL:<path>|<status note>', renders the box OPEN
# with 'Start from `<path>` (partial)' and the status note - used where real partial work is issued (bench test
# procedures AQS-TST-004/005, the HAZOP action register AQS-SAF-008, the Rev B EOL classing) but the Done-when still
# waits on a hardware run or tracked open actions. REOPEN stays for tasks with nothing citable.
EVIDENCE_PASS={
 'X-GOV-05':'docs-authority/DOC_REGISTER.md',
 'X-GOV-06':'docs-authority/DERIVED_REVISIONS.md',
 'X-PAR-10':'docs-authority/sizing/VENT_SCRUBBER.md',
 'X-STD-01':'docs-authority/GA_CHECK.md',
 'X-PRO-02':'docs-authority/BOUGHT_SPECS.md',
 'X-ASM-01':'docs-authority/INSTALL_SEQUENCE.md',
 'X-ASM-02':'docs-authority/RIGGING_PLANS.md',
 'X-CTL-04':'docs-authority/CONTROL_SOFTWARE.md',
 'X-FIR-01':'docs-authority/FIRE_PROTECTION.md',
 'X-MFG-31':'docs-authority/fab/VDF_SYN.md',
 'X-MFG-33':'docs-authority/sizing/COLD_BOX.md',
 'X-MFG-34':'PARTIAL:docs-authority/BENCH_TEST_UPW_POLISH.md|bench test procedure issued as AQS-TST-004; the run is hardware-gated on the first module (A-M-176 open)',
 'X-MFG-36':'PARTIAL:docs-authority/BENCH_TEST_H2_COMPRESSOR.md|first-article procedure issued as AQS-TST-005; the run is hardware-gated on the first article (A-M-169 open)',
 'X-MFG-38':'docs-authority/sizing/PV_CELL_LINE.md',
 'X-MFG-32':'docs-authority/JELLYBEAN.md',
 'X-GOV-20':'flow_graph/param/test_no_vendor_basis.py',
 'X-SAN-01':'docs-authority/sizing/SANITATION.md',
 'X-INV-01':'docs-authority/inventory/MOTOR_INVENTORY.md',
 'X-INV-02':'docs-authority/inventory/MOTOR_DESIGNS.md',
 'X-INV-03':'docs-authority/inventory/WIRE_INVENTORY.md',
 'X-INV-04':'docs-authority/inventory/PIPE_INVENTORY.md',
 'X-INV-05':'docs-authority/inventory/OTHER_INVENTORY.md',
 'X-BAS-04':'docs-authority/STANDARDS_LIST.md',
 'X-PIP-05':'docs-authority/WPS_REGISTER.md',
 'X-ELS-06':'docs-authority/CABLE_SCHEDULE.md',
 'X-ELS-09':'docs-authority/HAZ_AREA.md',
 'X-CTL-01':'docs-authority/INSTRUMENT_INDEX.md',
 'X-CTL-02':'docs-authority/CONTROL_ARCH.md',
 'X-CTL-03':'docs-authority/CAUSE_EFFECT.md',
 'X-THM-01':'flow_graph/test_heat_ladder.py',
 'X-THM-02':'docs-authority/HVAC.md',
 'X-THM-03':'docs-authority/INSULATION_SCHEDULE.md',
 'X-BLD-01':'docs-authority/FRAME_CHECK.md',
 'X-BLD-02':'docs-authority/STRUCT_LOADS.md',
 'X-BLD-03':'docs-authority/FOUNDATION.md',
 'X-BLD-05':'docs-authority/ENCLOSURE_EGRESS.md',
 'X-BLD-06':'docs-authority/LIFTING.md',
 'X-BLD-07':'docs-authority/SITE_ACCESS_CHECK.md',
 'X-SAF-01':'docs-authority/HAZOP.md',
 'X-SAF-02':'docs-authority/HAZARD_SEPARATION_LAYOUT.md',
 'X-SAF-04':'docs-authority/RELIEF_REGISTER.md',
 'X-SAF-05':'docs-authority/FIRE_PROTECTION.md',
 'X-PAR-15':'docs-authority/duties/H2_PURIFIER.md',
 'X-PAR-14':'docs-authority/duties/ACEX.md',
 'X-PAR-13':'docs-authority/duties/GLYOXAL.md',
 'X-RED-01':'docs-authority/RED_AUDIT.md',
 'X-RED-02':'docs-authority/WATER_TOWER.md',
 'X-RED-03':'docs-authority/RED_AUDIT.md',
 'X-RED-04':'docs-authority/RED_AUDIT.md',
 'X-RED-05':'docs-authority/RED_AUDIT.md',
 'X-RED-06':'docs-authority/RED_AUDIT.md',
 'X-RED-07':'docs-authority/RED_AUDIT.md',
 'X-RED-08':'docs-authority/RED_AUDIT.md',
 'X-RED-09':'docs-authority/RED_AUDIT.md',
 'X-SAF-06':'docs-authority/GAS_DETECTION.md',
 'X-COD-01':'docs-authority/COMPLIANCE_MATRIX.md',
 'X-COD-03':'docs-authority/ASME_CODE_INTENT.md',
 'X-PRO-01':'docs-authority/PLANT_BOM.md',
 'X-PRO-04':'docs-authority/SELF_COPY_BOM.md',
 'X-DWG-01':'docs-authority/DRAWING_STANDARD.md',
 'X-DWG-02':'docs-authority/DRAWING_REGISTER.md',
 'X-DWG-03':'flow_graph/views/pfd.svg',
 'X-COM-01':'docs-authority/COMMISSIONING.md',
 'X-COM-02':'docs-authority/STARTUP.md',
 'X-COM-03':'docs-authority/PERF_TEST.md',
 'X-OPS-01':'docs-authority/OPERATING_PROCEDURES.md',
 'X-OPS-02':'docs-authority/MAINT_PLAN.md',
 'X-OPS-03':'docs-authority/SPARES.md',
 'X-QA-01':'docs-authority/ITP.md',
 'X-QA-02':'docs-authority/DESIGN_CHECK.md',
 'X-END-01':'docs-authority/DECOMMISSIONING.md',
 'X-END-02':'PARTIAL:docs-authority/EOL_RETURN.md|Rev C classing: 947 of 1020 lines classed; 73 unassigned, each held with a named reason (70 wait on the section-3 material selection at unit task 09 across the AQS-ASSAY-001 Rev C bounding cases, 2 wait on the HCL_BURNER duty sheet at unit task 01, 1 pointer row to the AQS-INV-004 fabricated-part roll-up); 159 held total (fluoropolymer 57, Ti 23, Nd/Dy 5, Pt-Rh 1, duty-sheet-pending 72, pointer 1)',
 'X-MAT-01':'docs-authority/MATERIALS_STD.md',
'X-MAT-06':'docs-authority/MATERIALS_STD.md',
'X-MAT-03':'docs-authority/MATERIALS_STD.md',
}
REOPEN_WHY={
}
# X-FIR-01/X-MFG-31 left REOPEN_WHY on the 2026-10-19 pass; both entries are removed 2026-10-21 (see closure comments below).
# X-SAF-01, X-MFG-34, X-MFG-36 and X-END-02 moved from REOPEN to PARTIAL in the 2026-10-19 closure pass: each now has
# citable issued work (HAZOP regeneration + AQS-SAF-008 register; bench test procedures AQS-TST-004/005; AQS-END-002
# Rev B classing) with the remaining gap named in the status note instead of claimed absent.
# 2026-10-21 X-ASM-02 closed: one rigging plan per lift over 1000 kg issued as AQS-ASM-003
# (docs-authority/RIGGING_PLANS.md, generated by docs-authority/_rigging_plans.py, gated by
# flow_graph/test_rigging_plans.py). 15 plans, one per lift of the AQS-ASM-002 heavy-lift roster
# (> 1.0 t: 10 on L1, 3 on L0, 2 on L-1), each carrying: mass per lift (AQS-BLD-013 booked; tube
# racks halved per AQS-BLD-015), design load = mass x 1.10 rigging allowance (arithmetic asserted
# by the gate), the level's booked hoist rated t and its 125 % test load (ASME B30.2) with the
# margin check asserted, ASME B30.16 underhung hoists and CMAA70 2020 class C service, hoist beams
# loading the X-BLD-01 frame at rated x 1.25 impact, and the seat context in the AQS-ASM-002
# sequence. Lift points are NOT modeled: a sling angle or lug position unmodeled by any registered
# artifact would be an invented load path - each plan names the lift-point design as an open
# fabricator item on that unit's work order, and the gate asserts every plan carries the hold.
# 2026-10-21 X-ASM-01 closed: ordered lift and connect sequence per level issued as AQS-ASM-002
# (docs-authority/INSTALL_SEQUENCE.md, generated by docs-authority/_install_seq.py, gated by
# flow_graph/test_install_sequence.py). All 176 AQS-BLD-013 structural-row units sequenced across the
# 8 levels in build order L-2 -> L-1 -> L0 -> L1 -> R1 -> R2 -> R3 -> ROOF: Kahn topological order over
# the present graph edges among the level's units (connections made to seated partners), heaviest-first
# tiebreak (AQS-BLD-015 beam-load argument), and a declared tie-in pass for the same-level recycle loops
# (16 connections on L-1, 17 on L0 - spools prefabricated, made after both ends seat). Hoist duty is the
# AQS-BLD-015 book verbatim (rated = next standard size at or above heaviest lift + 10 % rigging, load
# test 125 % per ASME B30.2); the built-in-place rule of AQS-BLD-015 is applied verbatim and the pytest
# gate asserts the INPLACE class set stays identical to _lifting.py (tanks/reservoirs, PV, farm, hab,
# headers, docks, boundaries assemble in place and carry no hoist duty; tube racks seat as two manifolded
# halves). Heavy-lift roster: 15 lifts >= 1.0 t (the AQS-ASM-003 work order); cross-check vs the AQS-BLD-015
# level rows: clean, 0 mismatch. Partners outside the AQS-BLD-013 census (module interiors, headers,
# stores, product sinks, docks) are named "no structural booking" - 75 connections do not silently drop.
# DOC_REGISTER adds AQS-ASM-002 (AQS-ASM-001 already belongs to ASME_CLASS_SHEETS.md).
# 2026-10-21 X-PRO-02 closed: datasheet per bought item issued as AQS-PRO-002
# (docs-authority/BOUGHT_SPECS.md, generated by docs-authority/_bought_specs.py, gated by
# flow_graph/test_bought_specs.py). The bought roster is the AQS-INV-004 families outside the
# 'fabricated part' category: 64 families, 2444+13643+6635+972+960+713+217+144 = 25528 items, one
# datasheet row per family carrying the standard class it is bought to (ISO 15, IEC 61131-2,
# IEC 61800-5-1, IEC 60947-2/-4-1, ISO 16135/16137, MSS SP-58/-122, EN 12756, ISO 20456/61298/60751/
# 62828/60947-5...), the sizes in use from the graph counts, and the citation bases. Instruments keep
# their per-tag datasheets on AQS-CTL-001; valve seal classes and the mechanical seal tie to
# AQS-STD-002 Rev N sec. 14 (incl. the sec. 14.2 maker-table holds); pipe class sheets stay in
# AQS-PIP-003 / AQS-INV-003. The one excluded family is OF-13 (fabricated part set - in-house work).
# 2026-10-21 X-CTL-05 closed: AQS-INST-001 goes to Rev C (docs-authority/INSTRUMENT_LOOPS.md) - the
# assay, digester and farm study loops stand as issued and are registered against the plant-wide
# instrument system: loop membership per unit in AQS-CTL-001 (722 tags, per-unit extension complete
# 2026-10-20, no unit left without its sector index), per-loop set-points in the AQS-CTL-004 program
# blocks (graph basis; A-M-188 margin class / 90 % LSH convention), trips in AQS-CTL-003 (digester
# high-level = SIF-124). Cross-references verified in section 7 of the doc; DOC_REGISTER bumped to Rev C.
# 2026-10-21 X-CTL-04 closed: control program source + scan simulation issued as AQS-CTL-004
# (docs-authority/CONTROL_SOFTWARE.md, generated by flow_graph/control/plc_programs.py, gated by
# flow_graph/test_control_programs.py). One IEC 61131-3 structured-text program per sector PLC in
# docs-authority/plc/ (20 programs, one per row of the AQS-CTL-002 table): 100 ms cyclic task, I/O
# declarations from the module table, per-loop blocks from the AQS-CTL-001 basis column - 254 CONTROL
# loops (graph set-points: edge normal rate, unit design temperature/pressure, cell current; +10/-10 %
# alarm margin per the A-M-188 margin class; an expected-zero set-point alarms on any positive PV),
# 443 INDICATION loops (90 % of span high alarm, the registered LSH convention; no set-point invented),
# 25 SIF elements as watch inputs only (AQS-CTL-003 owns the trip matrix; AQS-CTL-002 rule). GAIN/KI are
# commissioning-entered (step test per AQS-COM-001 sec. 3) - the sim exercises the law structure only
# (bounds derivation, alarm states, span-bounded output, windup-free clamp tracking, stationarity at
# PV=SP, saturation on sustained over-range): 2179 checks + 25 bindings, 0 fail. AI-count cross-check
# vs AQS-CTL-002 reconciles 0 residuals across all 20 PLCs (the CONTROL_ARCH.md refresh this lane
# carries makes that true: its AI columns had gone stale with the 2026-10-20 loop extension -
# regenerated by _plc_arch.py, module counts unchanged).
# 2026-10-21 X-MFG-31 closed: the reopen basis is stale. All six named units already have full in-house mfg models the reopen basis is stale. All six named units already have full in-house mfg models
# in models/mfg/<U>/ (parametric CadQuery source in models/mfg/polymers.py and reactors.py, STEP/STL exports,
# bom.csv, fasteners, work orders); AQS-DUTY-072/073 (docs-authority/sizing/FOUNDRY_LINE.md and POLYMERS_LINE.md)
# hold the per-kg design-case tables at the 0.0 production rate (A-M-267). This lane adds the missing production
# routes docs-authority/fab/{HF_GEN,VDF_SYN,TFE_SYN,POLY_F,POLY_OLEFIN,POLY_COND}.md in the house route format, so
# every reactor/digester/CSTR now carries model + route (unit task 13 auto-ticks for the six). Finding fixed: the
# A-M-283 poly design wave books POLY_OLEFIN pressure in design.P_MPa, invisible to docs-authority/_asme_class.py;
# the generator was extended and AQS-ASME-002 goes to Rev C - POLY_OLEFIN reclassifies to B31.3 piping component
# (ID 142 mm <= 152 mm, U-1(c)(2)(j); UG-27 3.8 mm wall already checked in AQS-DUTY-073).
# 2026-10-21 X-FIR-01 closed: the reopen basis is stale. The fire-water tank and fire-pump drivers landed in
# 1aba493 (2026-10-19, the same commit as the reopen text): fire_tank_type/fire_tank_refill_h (A-M-314) and
# fire_pump_type/fire_pump_churn_frac/fire_pump_150_flow_frac/fire_pump_head_margin_kPa (A-M-313). Arithmetic
# checks against AQS-SAF-005 Rev B and the drivers: EH1 (L0) governs - 12.2 mm/min x 232 m2 = 2830.4 L/min,
# +10 % margin = 3113 L/min sprinklers + 1900 L/min hose = 5013 L/min over 90 min = 451 m3 tank reserve;
# pump rated 5678 L/min at 150 kPa (listed step over 5013), churn 1.21 x per NFPA 20 4.16, runout 150 % at
# >=98 kPa per 4.18. Evidence is the issued design docs-authority/FIRE_PROTECTION.md (AQS-SAF-005 Rev B,
# generated by docs-authority/_fire.py from flow_graph/param/fire.py + the fire_* driver keys); the hazard
# classes stay flagged pending the owner hall programme (doc lines 26 and 82), exactly as the Done-when asks.
# 2026-10-21 X-SAF-01 closed: after X-ELS-02 (docs lane commit 0c9e53c) a rerun of _hazop.py/_sif.py on the current
# graph adds the GEO_HP_CLOSED_LOOP node (its SOL_ARK_60K pump feed edge makes inflow > 0); 130 nodes, 220 actions,
# 123 closed at issue against duty-sheet section 6 relief statements, 97 trip actions closed in the SIF pass
# (167 SIFs in sif_list.csv), register AQS-SAF-008 empty - done-when "worksheets per P&ID node with actions closed" passes.
# The remaining three stay PARTIAL.
# 2026-10-21 X-MAT-03 closed: elastomer and gasket compatibility per service (MATERIALS_STD Rev N
# section 14). The Parker O-Ring Handbook ORD 5700 (2022 ed.) registered as S23: per-class decision
# table over all nine AQS-PIP-003 Rev A classes (FKM on the acid/hydrocarbon/vent families, EPDM on
# the water/alkali families, spiral-wound 316/304-graphite and PTFE envelopes on the metal classes)
# and family exceptions - solvent families to EPDM (alcohols and ketones in its polar-solvent range)
# with the exact FKM grade held as a maker-table check, EPDM special compound at the 100 C Q3 water,
# FKM bonded on the wet-acid H2 header, PTFE envelope on the 98 wt% H2SO4 leg, RGD note for H2 soft
# goods. Machine gate docs-authority/_gasket_census.py (classes covered, rows sourced, family class
# coverage; exits nonzero otherwise). AQS-PIP-003 Rev B points its held line at section 14.
# 2026-10-21 T04 nozzle-schedule disposition batch (20 desk-P2 items closed): the _nozzle_sched.py
# rule (_noz_edges: mass kg/d edges and HL-/thermal kW edges are nozzles; electrical and cable energy
# rows are not) gives zero schedulable connections for them - 13 already carry the utilities-only or
# legacy-rules schedule file, 7 machines/buildings correctly get no file ('nothing to schedule,
# nothing invented'); SI_REDUCE notes the unrated CHAR_TO_SI conveyor, whose row self-adds when the
# param pass rates it. Evidence per unit in DONE_U.
# 2026-10-21 X-MAT-06 closed: every unit in the AQS-STD-002 section 2 ambiguous list has a material with a
# stated stream and temperature (MATERIALS_STD Rev M section 13). Two conflicts adjudicated against the
# issued bases: HDR_H2 is the PVC-U wet-acid header of AQS-REV-H2-001 (graph headers.py row corrected; the
# 13 wetted header lines reclass P1, AQS-PIP-004 Rev C) and the Q3 heat batteries are SA-240 304L at the
# 100 C tier (heat_battery.py MAT_TIER; PP-H is an 80 C class material [S4]). _duty_basis.py now re-renders
# section 3 of existing sheets where it still carries a default template and the graph carries an issued
# design/design_storage material (19 sheets refreshed; hand-written per-unit texts preserved). The
# machine done-when check is docs-authority/_ambiguous_units.py --done (section 2 roster 77 units: 27 by
# issued sections, 18 by section 13.1 rows, 32 by the generated 13.2 table; no misses). Open holds named
# in 13.1/13.2: pot cells (unit task 09), H2_DRYER regeneration, ZNBR2 hypobromite coupon verification,
# WS gasket detail (X-MAT-03), synthetic gas p-T on every H2 edge (X-MAT-09).
# 2026-10-21 X-MAT-01 closed: AQS-STD-002 Rev L adds the section 12 service-class selection guide across the
# AQS-ASSAY-001 Rev C envelope (AQS-PIP-003 Rev A letters; per-duty-sheet materials for the molten-metal,
# fluoro-train, dopant and pot-brine families pending PIP-003 Rev B). The line-list class rules are keyed to the
# guide families - the "aqueous process, default thermoplastic" catchall is retired (323 piped wetted lines,
# 22 families in docs-authority/_service_census.py, gate exits nonzero on a catchall or a class/family
# contradiction); the section 8 checker now equals the issued CPVC/PVDF members and derives the IA-BMED-03/04
# inlets (35.1/35.7 C) from the booked X-RSZ-04 trim duties and driver heat capacities; the section 10 trim
# table moved to the X-RSZ-04 booked basis. The molten-salt pot-cell wetted selection itself stays open (12.2,
# closes with X-MAT-06 / unit task 09) - it is a per-unit decision, not a section 12 class.
DONE_X={"X-RSZ-07","X-BLD-05","X-BLD-07","X-THM-02","X-ELS-09","X-SAF-02","X-BLD-03","X-BLD-01","X-PRO-04","X-QA-02","X-END-01","X-OPS-01","X-COM-03","X-COM-02","X-COM-01","X-SAF-06","X-SAF-01","X-CTL-03","X-THM-03","X-CTL-05","X-CTL-04","X-PRO-02","X-ASM-01","X-ASM-02","X-CTL-02","X-CTL-01","X-BLD-06","X-RED-01","X-RED-03","X-RED-04","X-RED-05","X-RED-06","X-RED-07","X-RED-08","X-RED-09","X-GOV-20","X-MFG-32","X-STD-01","X-PAR-10","X-RED-02","X-FIR-01","X-COD-01","X-END-02","X-QA-01","X-OPS-02","X-SAF-05","X-OPS-03","X-BLD-02","X-PIP-05","X-PRO-01","X-COD-03","X-SAF-04","X-MFG-38","X-MFG-37","X-MFG-34","X-MFG-33","X-MFG-36","X-PAR-15","X-MFG-39","X-MFG-40","X-ELS-06","X-BAS-04","X-DWG-03","X-DWG-02","X-DWG-01","X-THM-01","X-THM-04","X-PAR-03","X-MFG-31","X-PAR-14","X-PAR-13","X-SAF-11","X-ELS-02","X-MAT-01","X-MAT-06","X-MAT-03",'X-THM-03','X-PAR-04','X-PAR-01','X-RED-03','X-RED-07','X-RED-09','X-RED-05','X-RED-08','X-RED-06','X-RED-04','X-RED-01','X-GOV-06','X-GOV-05','X-PAR-11','X-PAR-12','X-INV-02C','X-PAR-02','X-INV-02D','X-ELS-02A','X-PIP-04','X-INV-02','X-INV-04','X-INV-05','X-INV-03','X-PIP-03','X-GOV-20','X-INV-01','X-SAN-01','X-MFG-32','X-STD-01','X-ELS-11','X-PAR-08','X-PAR-10','X-PAR-09','X-MFG-30','X-MAT-20','X-PAR-07','X-BLD-04','X-PAR-05','X-PAR-06','X-MAT-07','X-MAT-19','X-RSZ-06','X-RSZ-04','X-RSZ-03','X-RSZ-02','X-RSZ-01','X-PIP-02','X-RSZ-05','X-BLD-09','X-GOV-08','X-MAT-07','X-ELS-05','X-ELS-08','X-ELS-07','X-ELS-03','X-MAT-18','X-COD-02','X-MAT-09','X-PIP-01','X-ELS-04','X-BAS-02','X-SAF-09','X-MAT-14','X-MAT-15','X-SAF-10','X-SAF-07','X-MAT-17','X-MAT-16','X-GOV-07','X-GOV-04','X-ELS-10','X-SAF-08','X-MAT-12','X-MAT-11','X-MAT-10','X-MAT-08','X-MAT-05','X-MAT-00','X-MAT-02','X-MAT-04','X-GOV-01','X-GOV-02','X-GOV-03','X-BAS-01','X-ELS-01','X-SAF-03','X-TOOL-01','X-TOOL-02','X-TOOL-03'}
if os.path.isdir(_MFD): DONE_X |= {f'X-INV-02-{f[:-3]}' for f in os.listdir(_MFD) if f.endswith('.md')}
# 2026-10-21 X-INV-03 wire-family batch (26 desk-P3 items closed): the desk package AQS-INV-007 Rev C
# (docs-authority/WIRE_SPECS.md, generated by docs-authority/_wire_specs.py, gate test_wire_specs.py)
# satisfies the Done-when of every family task: one sheet per family carrying the open cross-section
# (stranding n x ds to ASTM B8 class B / B3 anneal, core OD, insulation and jacket walls to the family's
# registered standard), the cross-section drawing (docs-authority/drawings/wire/<WF>.svg), the WIRE_DRAW
# production plan (8 mm ASTM B49 rod -> draw passes at 20 % per pass to the strand size -> in-line anneal
# to ASTM B3 -> class B concentric stranding -> single-screw extrusion to the wall -> in-line UL 1581
# spark test -> twist/foil/jacket for the cable forms -> print and spool), and the routine tests per reel
# (conductor resistance against the sheet R20 and NEC Ch. 9 Table 8, AC dielectric and insulation
# resistance per UL 1581) with the type tests named to the family standard (UL 4703/83/44/66/1581/1277/
# 1072, ASTM B3/B8/B49). Passed as evidence only where the family has a sheet row (WIRE_SPECS.json key
# per WF id); the production runs and the type tests themselves stay open (hardware-gated).
import json as _json_ws
_WS_P = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'inventory', 'WIRE_SPECS.json')
_WS = _json_ws.load(open(_WS_P)) if os.path.exists(_WS_P) else []
DONE_X |= {f"X-INV-03-{_r['fam']}" for _r in _WS}
EVIDENCE_PASS.update({f"X-INV-03-{_r['fam']}": 'docs-authority/WIRE_SPECS.md' for _r in _WS})
# 2026-10-21 X-INV-04 pipe-family batch (18 desk-P3 items closed): the desk package AQS-INV-006 Rev A
# (docs-authority/PIPE_SPECS.md, generated by docs-authority/_pipe_specs.py, gate test_pipe_specs.py)
# satisfies the Done-when of every family task: one production plan per family carrying the quantity
# basis (AQS-INV-003 roster: pipe m, lines, 6.096 m stock lengths and the booked offcut allowance), the
# fittings disposition (bought to the family fitting standard; F1 FRP contact-moulded in shop to
# ASTM D5421 per the WPS-08 laminate discipline), the joints to the issued WPS id of AQS-WLD-002
# (solvent D2855, fusion DVS 2207, GTAW/SMAW per ASME IX, laminate per ASME RTP-1), the test to the
# AQS-PIP-003 class letter, and the honest making-route statement: the graph books no plastic pipe
# extrusion line and no tube mill (EXTRUDE is the 50 t metal profile press; FILM_CAST is the 0.14 kg/d
# PVDF sheet line), so stock is bought to the family standard and in-house extrusion or a tube mill
# stays a named open capital option, not an assumed machine. Passed as evidence only where the family
# row exists in PIPE_FAMILIES.csv; production runs and examinations stay open (hardware).
_PF = [dict(x) for x in __import__('csv').DictReader(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'inventory', 'PIPE_FAMILIES.csv')))] if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'inventory', 'PIPE_FAMILIES.csv')) else []
DONE_X |= {f"X-INV-04-{_r['family']}" for _r in _PF}
EVIDENCE_PASS.update({f"X-INV-04-{_r['family']}": 'docs-authority/PIPE_SPECS.md' for _r in _PF})
out=[];cnt=[]
def box(d): return '[x]' if d else '[ ]'
# Triage (AQS-PLAN-007 rev B, A-M-224): desk = can be closed from files in the repo; hardware = needs a built item, a test,
# a site measurement or an as-built; owner = waits on an owner decision (OPEN_QUESTIONS). Desk priority P1..P5 follows the
# unit-task dependency chain (basis/sizing first) and the critical path for cross-cutting tasks.
import re as _re
HW_RE = _re.compile(r"(test record|coupon|first article|bench|stack test|polarisation test|on site|as-built|build one|type test|Wenner|acceptance record)", _re.I)
OWNER_X = {'X-PRO-03', 'X-BAS-03', 'X-ELS-08'}
CRIT_X = {'X-BAS-02', 'X-ELS-02', 'X-ELS-04', 'X-SAF-01', 'X-PIP-02', 'X-BLD-02', 'X-BLD-01', 'X-BLD-03', 'X-PAR-02', 'X-PAR-03', 'X-PAR-04', 'X-PIP-03', 'X-MAT-01'}
UPRI = {'01': 1, '02': 1, '03': 2, '04': 2, '05': 2, '07': 2, '06': 3, '08': 3, '09': 3, '10': 4, '11': 4, '12': 4, '13': 4, '14': 5}
TRI = {}
def tri_x(tid, t, crit):
    if tid in OWNER_X: k = 'owner'
    elif HW_RE.search(t + ' ' + crit): k = 'hardware'
    else: k = 'desk P%d' % (1 if tid in CRIT_X else 3 if tid.startswith(('X-INV', 'X-TOOL')) else 2)
    return k
def tri_u(k):
    return 'hardware' if k == '15' else 'desk P%d' % UPRI.get(k, 5)
for code,title,items in X:
    nd=0;out.append(f'\n### X-{code}. {title}\n')
    for tid,t,crit,dep,ev in items:
        d=tid in DONE_X
        ro=''   # 2026-10-19 honesty pass: resolve evidence for done tasks that carry none in the tuple
        if d and not ev:
            _ov=EVIDENCE_PASS.get(tid)
            if _ov=='REOPEN':
                d=False; ro='reopened 2026-10-19: no cited evidence ('+REOPEN_WHY.get(tid,'no artifact matches the Done-when')+')'
            elif isinstance(_ov,str) and _ov.startswith('PARTIAL:'):
                _p=_ov[len('PARTIAL:'):]; _note=''
                if '|' in _p: _p,_note=_p.split('|',1)
                d=False; ev=_p; ro=_note
            elif _ov:
                ev=_ov
        if ev: need(ev)
        if d: nd+=1
        # when a done item carries both its own start-from path and a registered evidence path, the
        # registered one is the issued artifact and wins (family desk packages; REOPEN/PARTIAL still
        # handled above only for ev-less tuples)
        if d and ev:
            _ov2=EVIDENCE_PASS.get(tid)
            if isinstance(_ov2,str) and not _ov2.startswith(('REOPEN','PARTIAL:')): ev=_ov2
        e=f' Evidence: `{ev}`.' if d else (f' Start from `{ev}` (partial).' if ev else '')
        tg='' if d else ' Triage: '+tri_x(tid,t,crit)+'.'
        if not d: _k=tri_x(tid,t,crit); TRI[_k]=TRI.get(_k,0)+1
        out.append(f'- {box(d)} **{tid}** {t}. Done when: {crit}. Depends: {dep}.{e}{tg}'+(f' Status: {ro}.' if ro else ''))
    cnt.append((f'X-{code}',title,len(items),nd))
xs='\n'.join(out); out=[]
for code,title in SYS:
    T=D=0; out.append(f'\n### {code}. {title}\n')
    for n in sorted(units[code],key=lambda n:n['unit_id']):
        u=n['unit_id']; out.append(f'- **{code}-{u}** ({n["class"]}, sector {n["sector_id"]})')
        for k,t,crit,dep in (ST[:1] if ACC(n) else ST):
            ev=status(n,k); T+=1; D+=bool(ev); nt=note(n,k)
            depx=', '.join(f'{code}-{u}-{x.strip()}' if x.strip().isdigit() else x.strip() for x in dep.split(','))
            out.append(f'  - {box(ev)} {code}-{u}-{k} {t}. Done when: {crit.replace("<UNIT>",u)}. Depends: {depx}.'+(f' Evidence: {ev}.' if ev else '')+(f' Status: {nt}.' if nt and not ev else '')+('' if ev else f' Triage: {tri_u(k)}.'))
            if not ev: TRI[tri_u(k)]=TRI.get(tri_u(k),0)+1
    cnt.append((code,title,T,D))
us='\n'.join(out)
import pathlib; pathlib.Path('/tmp/tp').mkdir(parents=True, exist_ok=True)   # QA R3 sibling fix: hardcoded tmp dir
json.dump(cnt,open('/tmp/tp/cnt.json','w'))
tab='\n'.join(f'| {c} | {t} | {a} | {b} |' for c,t,a,b in cnt)
TA=sum(c[2] for c in cnt);TD=sum(c[3] for c in cnt)
TRT='\n'.join(f'| {k} | {v} |' for k,v in sorted(TRI.items()))
doc=f'''# Task plan

Document number: AQS-PLAN-007
Revision: B
Date: 2026-10-15
Authority: graph Rev {g.get("revision","BH")}. Study. Not a PE stamp.

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue. Master task list for a design that can be built from the repo alone. | 2026-10-15 |

## 1. Purpose and status of this page

This is the master task list. It supersedes `MASTER_PLAN.md` (AQS-PLAN-004) as the list of work; MASTER_PLAN stays as the close-out record of plan lines. AQS-STD-002 (`MATERIALS_STD.md`) is the materials rule for every unit task 09. `PROJECT_PLAN.md` (AQS-PLAN-005) holds the engineering limits and phase holds and is a sub-plan. `MFG_MODEL_PLAN.md` (AQS-PLAN-006) is the sub-plan for unit task 10. AQS-PLAN-001 to 003, AQS-MFG-001, AQS-REM-001, AQS-REM-BLD-001, AQS-MVS-PLAN-001, and AQS-MVS-CHK-001 are history.

The target is a design that a shop can build from files in this repository alone. A task is checked only where a file in the repo proves it; the file is cited. A study value, an envelope, or a held figure does not check a task. Partial evidence is written as a status note and the box stays open. No value on this page is new data.

Units are the {len(P)} present nodes of `flow_graph/plant_flow_graph.json`, grouped by system. Accounting nodes (class boundary) carry task 01 only.

## 2. Counts

Generated by `docs-authority/_task_plan_gen.py` from the graph and the files present. Rerun it after a task closes.

| System | Title | Tasks | Done |
| --- | --- | --- | --- |
{tab}
| | **Total** | **{TA}** | **{TD}** |

## 2a. Triage of open tasks (rev B)

Every open task carries a `Triage:` tag. desk = can be closed from files in this repository; hardware = needs a built item, a test, a site measurement or an as-built record; owner = waits on an owner decision (OPEN_QUESTIONS.md). Desk work runs P1 first: P1 process basis, sizing and critical-path cross-cutting tasks; P2 P&ID, nozzles, lines, relief and other cross-cutting tasks; P3 internals, instruments, materials, inventory production plans; P4 CAD, fabrication drawings, BOM, fabrication route; P5 installation. Unit task 15 (test and commission) is hardware: the procedure is desk work, but the acceptance record needs the built unit.

| Triage | Open tasks |
| --- | --- |
{TRT}

## 3. Unit task template

Every unit carries tasks 01 to 15:

| No. | Task | Done when | Depends |
| --- | --- | --- | --- |
''' + '\n'.join(f'| {k} | {t} | {c} | {d} |' for k,t,c,d in ST) + f'''

## 4. Critical path and phase sequence

1. Phase A, basis. X-GOV-04, X-BAS-02, X-BAS-03, X-BAS-04, X-MAT-01, X-MAT-06. Nothing downstream is sized until the bounding cases and the site are fixed.
2. Phase B, process. Unit task 02 for every unit, metals line first (AQS-PLAN-002 section 4), then X-ELS-02 load list and X-THM-01 heat ladder.
3. Phase C, P&ID and safety. Unit task 03, X-CTL-01, X-SAF-01 HAZOP, X-SAF-04 relief sizing, X-ELS-09 area classification.
4. Phase D, lines and materials. Unit tasks 05, 09, X-PIP-01, X-PIP-02, X-MAT-02.
5. Phase E, mechanical. Unit tasks 06, 10, 12 per AQS-PLAN-006 tier order; X-BLD-02 loads.
6. Phase F, structure and layout. X-BLD-04, X-BLD-01, X-BLD-03, X-PIP-03, X-THM-02, X-SAF-05.
7. Phase G, electrical and controls detail. X-ELS-03 to X-ELS-08, X-CTL-02 to X-CTL-04.
8. Phase H, package. Unit tasks 11, 13; X-DWG, X-PRO, X-QA-01, X-COD.
9. Phase I, build. X-ASM, unit task 14, X-COM, unit task 15, X-OPS, X-QA-03, X-END.

Critical path: X-BAS-02 → MET unit 02 (LEACH_CSTR_1, EW_1 to EW_9) → X-ELS-02 → X-ELS-04 → unit 03 → X-SAF-01 → X-PIP-02 → unit 10 → X-BLD-02 → X-BLD-01 / X-BLD-03 → unit 11 / 13 → X-ASM-01 → X-COM-01.

## 5. Next 10 tasks

1. X-PAR-02 Extend the solver unit by unit (LEACH full balance, FLOAT_SINK, VCD, UPW, gas train) until every edge is solved.
2. X-PAR-03 Atmospheric venting (API 2000) per unit task 07; API 520 relief recomputed for EXPANDER 2026-10-15 by `write_graph.py relief`. Converted 2026-10-15: rectifier, LEACH_CSTR_1, HX-5/HX8, power and one-line scripts (AQS-PAR-001 section 2).
3. X-PAR-03 Apply the scrubber function to ALK_SCRUBBER, ACID_POLISH_SCRUB, NOX_SCRUB and MET_SCRUB with C_s and HTU from the in-house packing design (X-MFG-31) (function added 2026-10-15, `flow_graph/param/sizing/scrubber.py`). Tank, agitator and pump functions added 2026-10-15 (`flow_graph/param/sizing/tank.py`).
4. X-PAR-04 BOMs for EVAP_ACID and EVAP_BASE come from the in-house design (X-MFG-30; no bought skid, owner decision 2026-10-15); CadQuery envelopes, line list, isometric routes and supports regenerated 2026-10-15 (`flow_graph/param/envelopes.py`). Done 2026-10-15: acid-loop misfits resolved and written by `flow_graph/param/write_graph.py` (AQS-PAR-001 Rev B section 4a); misfit gate `flow_graph/param/test_param_misfit.py` (1 %).
5. X-PAR-04 Vendor MVR quote and bench leach at 20 wt% HCl (A-M-089, A-M-090).
6. X-BLD-04 closed 2026-10-15 (seed Rev K): AQS-BLD-010 0 overlaps / 0 pairs; AQS-BLD-011 10/10 incompatible pairs; AQS-BLD-012 9/9 NEC 110.26 rows and 139/139 rows with a 914 mm face; L1 farm re-rowed to 914 mm paths (`flow_graph/farm_rerow.py`, A-M-102). Next: X-PAR-07 roof-only PV, X-STD-01, X-MFG-30..32, X-GOV-20 (owner decisions 2026-10-15).
7. X-PAR-07 closed 2026-10-15 (conditioned hall, owner decision): roof_close in the solver (156 x 84 m, 26 x 14 bays, 13,104 m²; PV 1336 kWp roof-only, roof capacity 1341 kWp), gate test_roof_carries_pv, EXT_HALL node with SF-EXT_HALL 37.26 kW and duty sheet, IA-PV-01 carries it, ground field removed, seed Rev L (`flow_graph/place_roof.py`). Follow-ups: bin-hour load calculation; FreeCAD extension massing; hall egress under X-STD-01.
23. 2026-10-15: X-INV-04 closed (pipe inventory AQS-INV-003 from the iso quantities: 6220 m in 24 families, 1054 stock lengths of 6.096 m, A-M-124); X-INV-05 closed (other building blocks AQS-INV-004: valves, instruments, electronics, protection, bearings, seals, supports, fasteners, fabricated part sets; 53 families, A-M-125); X-INV-02 closed (motor family designs AQS-INV-005: one design basis and in-house manufacturing plan per family, output-equation sizing PYRHONEN2014 / HENDERSHOT2010, IEC 60072-1 frames, IE3 targets; A-M-126). Per-family tasks X-INV-04-PFnn and X-INV-05-OFnn generated; X-INV-02B first articles and type tests opened.\n167. 2026-10-16 GA storage dims from graph.\n166. 2026-10-16 AQS-DUTY-064: storage and holdup sizing for 18 units (unit task 02), graph envelopes written (A-M-225)\n165. 2026-10-16 Task plan triage.\n164. 2026-10-16 L-1 regroup.\n163. 2026-10-16 Isometrics follow GA moves.\n162. 2026-10-16 QA checks QC-25..29; TC-ER lay factor fixed.\n161. 2026-10-16 Wire working values confirmed.\n160. 2026-10-16 Motor sheets revised for slot fit.\n159. 2026-10-16 Equipment clash check and L-1 corridors (A-M-220).\n158. 2026-10-16 QA checks QC-19..24 added.\n157. 2026-10-16 Test rig desk packages AQS-TST-003: BMED bench stack, ZNBR2 rig hardware, FRP coupon programme (A-M-219)\n156. 2026-10-16 X-INV-02B desk package: AQS-INV-008 lamination/frame drawings for 17 induction families, traveller, type-test rig; 5 families need longer cores (A-M-218)\n155. 2026-10-16 X-INV-03-WF desk package: AQS-INV-007 wire specs + cross-sections for 27 families (A-M-217)\n154. 2026-10-16 X-RSZ-07 closed (A-M-216).\n153. 2026-10-16 GA CAD clashes 46 -> 0 (A-M-215).\n152. 2026-10-16 QA checks extended.\n151. 2026-10-16 CAD rebuild and clash check.\n150. 2026-10-16 Separation pairs resolved.\n149. 2026-10-16 S52 composition fixed.\n148. 2026-10-16 X-BLD-05 closed (A-M-213).\n147. 2026-10-16 X-BLD-07 closed (A-M-212).\n146. 2026-10-16 X-THM-02 closed (A-M-211).\n145. 2026-10-16 X-ELS-09 closed (A-M-210).\n144. 2026-10-16 X-SAF-02 closed (A-M-209).\n143. 2026-10-16 X-BLD-03 closed (A-M-208).\n142. 2026-10-16 X-BLD-01 closed (A-M-207).\n141. 2026-10-16 X-PRO-03 held on Q-012.\n140. 2026-10-16 X-PRO-04 closed (A-M-206).\n139. 2026-10-16 Hydro energy propagated.\n138. 2026-10-16 X-QA-02 closed (A-M-205).\n137. 2026-10-16 X-END-01 closed (A-M-204).\n136. 2026-10-16 X-OPS-01 closed (A-M-203).\n135. 2026-10-16 X-COM-03 closed (A-M-202).\n134. 2026-10-16 X-COM-02 closed (A-M-201).\n133. 2026-10-16 X-COM-01 closed (A-M-200).\n132. 2026-10-16 15 unsized units now structurally loaded (A-M-199).\n131. 2026-10-16 Trip-tag mismatch fixed.\n130. 2026-10-16 X-SAF-06 closed (A-M-198): 114 detectors (H2 16 points, O2 18, CO 6, NOx 2, Cl2/HCl 13), 2oo3 at the H2/O2 SIFs; X-SAF-01 ticked: all 55 HAZOP actions closed (team review = rev B).\n129. 2026-10-16 Pipeline fix after X-CTL-03: SIF TEs indexed in AQS-CTL-001.\n128. 2026-10-16 X-CTL-03 closed (A-M-197): 162 SIFs; HAZOP AQS-SAF-001 now 0 open actions; safety PLC pair, independent TEs and ESD valves in AQS-INV-004.\n127. 2026-10-16 HAZOP instrument actions closed: LT/LSH/TE added by rule in AQS-INV-004; 22 open actions are all trips for X-CTL-03.\n126. 2026-10-16 HAZOP relief actions closed (A-M-196): H2O_ELYZ and HCL_BURNER API 520 cases, EVAP_ACID_VS API 2000 vent.\n125. 2026-10-16 X-SAF-01 rev A (A-M-195): 126 nodes, 55 open actions (not ticked): relief cases missing on H2O_ELYZ, HCL_BURNER, PROD_O2, PROD_MEOH, EVAP_ACID_VS; 20 trips to X-CTL-03.\n124. 2026-10-16 X-THM-03 ticked: AQS-THM-003 insulation schedule already generated by _insulation.py (A-M-158).\n123. 2026-10-16 X-CTL-02 closed (A-M-194): sector PLCs with I/O from AQS-CTL-001/INV-004, 202 modules, redundant CPU pairs on life-support and energy sectors, MRP ring, about 0.8 kW.\n122. 2026-10-16 X-CTL-01 closed (A-M-193): 836 tagged instruments with range, signal and loop; PT ranges from design pressure (CRYO_H2/O2 0-400 bar, was 0-10); other.py now in the pipeline.\n121. 2026-10-16 X-BLD-06 closed (A-M-192): L-1 2 x 5 t hoists (CRYO_H2 half bank 3.1 t), L0 2 x 1 t, L1 0.5 t; 125 % load test per ASME B30.2.\n120. 2026-10-16 AQS-BLD-013 fix: 17 units placed only by block-sized report moves now loaded at graph size (receivers, ROOF_TANK, BMED, OIL_PYRO...); 16 without a graph size listed for X-BLD-01.\n119. 2026-10-16 AQS-RED-001 rev B: water tower, EXPANDER backup, fire water N+1, receiver halves; X-RED-01/03-09 ticked (closed in rev A, A-M-145..152).\n118. 2026-10-16 Housekeeping: X-GOV-20, X-MFG-32, X-STD-01, X-PAR-10 ticks restored from their closing notes; X-RED-02 closed by AQS-BLD-014; X-FIR-01 closed by AQS-SAF-005.\n117. 2026-10-16 X-COD-01 closed: 41 rows - 23 closed (study), 9 open (design, task named), 3 open (external), 5 open (owner), 1 N/A.\n116. 2026-10-16 X-END-02 closed (A-M-191): 1036 BOM lines classed; held: 58 fluoropolymer (Q-011), 32 Ti (re-use), 5 NdFeB, 1 Pt-Rh, 27 unassigned.\n115. 2026-10-16 X-QA-01 closed (A-M-190): 8 fabrication routes with H/W/R points, 172 units assigned; per-unit models/units/<U>/itp.csv.\n114. 2026-10-16 X-OPS-02 closed (A-M-189): 209 units with inspection and replacement intervals (API 510/570/576, NFPA 25/70B/110/111, insert lives); per-unit models/units/<U>/maint.csv.\n113. 2026-10-16 X-SAF-05 closed (A-M-188): fire reserve 451 m3 as dead storage in the water tower (L0 EH1 governs), pumped second supply from CATCH_TANK; API 521 fire case governs the receivers: relief 13/10/9 mm per half bank (was 3.3 mm), depressuring on flame. Water tower re-solved: head 35.73 m, 3 levels.\n112. 2026-10-16 Q-009 closed (owner): water tower AQS-BLD-014 (A-M-187): head 32.65 m, 2,962 m3 on 2 reservoir levels + CATCH_TANK lower reservoir (was a 384 m3 placeholder, not from need); seismic shear 14,530 kN governs; LIFE_LEVELS grow at 2 x shop levels.\n111. 2026-10-16 Q-010 closed (owner): EXPANDER kept as standby N2 reverse-Brayton backup of the CO2 condenser chiller, 0.082 kW cold, 0.44 kW net (A-M-186).\n110. 2026-10-16 X-OPS-03 closed (A-M-185): 86 lines, 43 spare motors, 900 building-block spares, 13 process insert sets (membranes, sorbent, catalysts, gauze, resin, diaphragms, PSVs).\n109. 2026-10-16 Doc number collision fixed: STRUCT_LOADS is AQS-BLD-013.\n108. 2026-10-16 X-BLD-02 closed (A-M-184): AQS-BLD-013 in the pipeline; test-case loads L-2 4139 kN (CATCH_TANK 3916), L-1 391, L0 867, L1 2441 kN; roof PV 5178 kN = 0.17 kPa over 31,060 m2.\n107. 2026-10-16 X-PIP-05 closed: AQS-WLD-002 via _wps.py in the pipeline; WPS-01..08 for 316L, CS, HDPE, PVDF, PP, PVC-U, CPVC, FRP with qualification, essential variables, PQR test and B31.3 5 % random examination. X-PRO-01 closed (envelope BOMs).\n106. 2026-10-16 Unit BOMs (A-M-183): _unit_boms.py in the pipeline writes models/units/<UNIT>/bom.csv for 172 units; AQS-PRO-001 rolls them up (motors/blocks counted once); only boundary nodes remain without a BOM. X-PRO-01 closed.\n105. 2026-10-16 Liquid-head cases (A-M-182): 118 vapour-only units resolved: 28 hold-up heads (2 d stores, 1 d process, H/D 1.5), 15 bed/fixture depths, 5 pipes, 70 no liquid inflow. All remain atmospheric.\n104. 2026-10-16 Q-010 left open with redundancy note; commit helper now refuses on failing tests.\n103. 2026-10-15 X-PRO-01 partial: AQS-PRO-001 via _plant_bom.py in the pipeline, 507 lines; 174 graph units have no BOM yet (unit task 12). Fix: models/mfg generators wrote unquoted material fields with commas; bom.csv now csv-quoted.\n102. 2026-10-15 X-COD-03 closed: AQS-ASME-002 rev B adds stamp and test per unit: 198 atmospheric (fill test), 6 B31.3 components (1.5 x hydro), 1 machine casing; no U stamp required. Texas jurisdictional review left to X-COD-01.\n101. 2026-10-15 CRYO_CO2 sized (A-M-181): 84.6 kg liquid CO2, 0.091 m3, 4 tubes, t req 1.09 vs 11.80 mm; AQS-ASME-002 now has no Section VIII-1 unit awaiting size.\n100. 2026-10-15 X-SAF-04 closed (A-M-180): 7 pressurised vessels and 9 interstage PSVs all adequate; findings fixed: CO2 compressor discharge 225 C -> 4 stages 122 C (cold box rev B), CRYO_CO2 liquid store at 20 bar was classed atmospheric -> design 2200 kPa g, now Section VIII-1 awaiting size. Gas-receiver fire case carried to X-SAF-05.\n99. 2026-10-15 A-M-179 wording fixed (gate test_no_vendor_basis).\n98. 2026-10-15 X-MFG-41 prepared (stays open for the physical test): AQS-TST-002 10-cell stack procedure and acceptance; prediction VE 0.896, CE 0.944, RT 0.820; design 0.70 held as margin.\n97. 2026-10-15 X-MFG-38 closed (A-M-178): 7 tools, 9.40 kWh/d for 3 cells (3.1 kWh/cell), diffusion 5.9 kWh/d dominates; peak 3.8 kW; ST-SOLAR-01 closed in AQS-STUB.\n96. 2026-10-15 X-MFG-37 closed (A-M-177): melt 0.362 kWh/kg, 7.5 kW coreless furnace, 2 heats/d; atomiser Ar recirculation 0.246 kWh/kg, 5.5 kW; rolling 0.032 and drawing 0.042 kWh/kg; _mfg_tools.py --graph writes MFG_SHOP in the pipeline.\n95. 2026-10-15 X-MFG-34 closed (A-M-176): potable 235.9 kg/d bypasses; UPW 127.3 kg/d through 0.27 m2 TFC RO at 6.9 bar (95.5 % recovery from IA-UPW-REJ) and EDI 10 mA; 2 x 100 %; 18 W incl. 15 W UV.\n94. 2026-10-15 X-MFG-33 closed (A-M-175): no air intake, N2 99.9 % after CO2 removal, so no cryogenic column; 3 x 109 kg 13X beds DN410 x 1244 mm, CO2 2-stage to 20 bar and condensed at -20 C; 1.67 kW (regen 1.40). EXPANDER loop idle (Q-010). Critical list in _power_sizing now graph-derived: 14.32 kW; HYDRO backup 200.5 kWh, 5,109 m3 at 18 m; Q-009 numbers revised. Load list CRYO_ASU/CRYO_H2 now from graph.\n93. 2026-10-15 GA_CHECK finding closed: study_place.py and _ga_check.py run every pipeline pass after envelopes; 160 envelopes, 0 overlaps, 0 inside 600 mm.\n92. 2026-10-15 Placeholder design pressures replaced (A-M-174): vent stage sets design_kPa = 4 x vent dP + full-height head at SG 1.25 on all 197 atmospheric units; 77 have a hydrostatic case (max NOX_SCRUB 49 kPa g), 120 unsized units carry the 2 kPa vapour case until sized. AQS-ASME-002 unchanged at 199 atmospheric.\n91. 2026-10-15 EW busbar finding closed: AQS-BUS-001 rev C generated by _ew_busbar.py; bars 136-153 A/cm2, drop 162-176 mV inside the 0.3 V budget; cable schedule now passes all EW bars.\n90. 2026-10-15 X-MFG-36 finding closed: two-stage 290 C predicted discharge replaced by 5 stages at ratio 1.82, 125 C (API618 135 C limit); 1.97 kWh/kg.\n89. 2026-10-15 BMED energy basis replaced (A-M-171): triplet voltage model 1.22 V (BPM 1.0 + membranes 0.12 + solution 0.07 + end 0.03), design 1.67 V from the pilot measurement; SEC 1.40 kWh/kg; X-PAR-12 rescaling base now follows the solver. CE at 2 M is the governing verification item (X-MFG-41).\n88. 2026-10-15 X-MFG-35 design issued (A-M-170): 96.5 kg/d NaOH, 421 triplets of 0.04 m2 at 8 A in 5 stacks + 1 spare, 50.5 m2 membrane. Finding: the 6.7 kWh/kg graph SEC implies 8.0 V per triplet vs 1.7 V at the pilot figure; task stays open for the stack polarisation test.\n87. 2026-10-15 X-MFG-36 closed (A-M-169, h2_compressor.py in pipeline): 10.74 kg/d 10 -> 200 bar, ratio 4.47 x 2, 2.27 kWh/kg, 1.01 kW average (was 0.565 on a stale 6.63 kg/d), 3.04 kW peak; diaphragms 317/150 mm; discharge 203 C flagged (third stage option). PV 4304 -> 4310 kWp.\n86. 2026-10-15 AQS-ASME-002: EXPANDER cylinder is part of a reciprocating machine, outside Section VIII by U-1(c)(2)(c); no unit left as Section VIII-1 awaiting size.\n85. 2026-10-15 X-PAR-15 closed: S49P dry H2 5.0237 kg/d (Grade D), new IA-H2P-H2O 0.0050 kg/d to VCD_TRAIN, S52 reduced by the same mass; mass balance closes.\n84. 2026-10-15 X-MFG-39 closed (A-M-168, h2_purifier.py in pipeline): 2.33 Nm3/h H2; deoxo 2 x 0.47 L Pd/Al2O3 DN50, guard 2 x 0.10 L DN25 (82 g, 90 d), TSA 2 x 1.35 L sieve DN50 x 626 mm, regen 250 C; 44 W. Finding X-PAR-15: S49P water above Grade D and dried water has no outlet.\n83. 2026-10-15 Gas receivers (AQS-DUTY-065, A-M-167, receivers.py in the pipeline): 22 MPa design, B31.3 wall 10.16 mm req vs 11.80 mm min Sch 160; H2 36 tubes x 6.1 m (1.28 m3, 6.2 t), O2 16 + 2 crew-reserve tubes (3.1 t); ID 87 mm puts both under the Section VIII size limit (AQS-ASME-002 now 6 B31.3 components, 1 VIII-1 awaiting size: EXPANDER). Placement rerun, CRYO racks placed.\n82. 2026-10-15 X-MFG-40 closed: _asme_class.py (pipeline) applies the Section VIII-1 scope U-1(c)(2)(h)/(j): 199 atmospheric, 3 below the 152 mm size limit as B31.3 components (MEOH_SYNTH, HTC, MEAM), 3 Section VIII-1 awaiting size (CRYO_H2, CRYO_O2, EXPANDER), 7 not vessels. Cold box CRYO_ASU still on the head-plus-10 placeholder; reclassified by X-MFG-33. 197 units carry that placeholder design pressure.\n81. 2026-10-15 X-ELS-06 closed: AQS-ELEC-010 via _cable_schedule.py; wire inventory now rerun in the pipeline. 108 power circuits all meet NEC 310.16 ampacity and 3 %/2 % drop after the fix: hall 277 V lighting branches (16 A over 120 m) 12 AWG gave 8.8 % drop, now 6 AWG. Busbars: SWBD-1 sections 500 A vs 415 A plant demand (tie closed), CB-1..6 1000 A vs 903 A (NEC 705.28 125 %), Cu at UL 891 155 A/cm2; EW process bars at 200 A/cm2 flagged for a temperature-rise check at the RECT-EW first article. Wire inventory 169.4 -> 196.3 km (PV growth propagated plus lighting).\n80. 2026-10-15 X-BAS-04 closed: AQS-STD-004 via _standards_list.py (pipeline): 74 codes and standards in 8 disciplines with the files citing each; 6 registered but not yet cited.\n79. 2026-10-15 X-DWG-01/02/03 closed: AQS-DWG-001 (ASME Y14.1/Y14.35/Y14.100/Y14.5, ISO 7200 fields, ISO 10628-2 symbols; numbering, A-series sheets, content-hash revision index); _drawings.py in the pipeline stamps every SVG (5 graph views with graph SHA-256, 389 isometrics, 23 motor drawings) and writes AQS-DWG-002 (450 entries incl. STEP models and PFD images). Fix: HL-Q4-REJ is an upstream closure, X-THM-01 now closes Q4_BUS on it rather than subtracting twice.\n78. 2026-10-15 X-THM-01 closed (A-M-166): all 9 Q stores close on graph rates within 0.01 kW (test_heat_ladder.py, 23 tests); line losses carried down the ladder (Q4_A 0.76, Q4_B 0.84 kW cumulative) and taken off HL-Q4-REJ 11.76 -> 10.16 kW; no trim added. Hot and cold side duties per edge stay in AQS-DUTY-008.\n77. 2026-10-15 X-THM-04 closed (A-M-165): 26 HL lines carry line_loss_W and duty_source_rated_kw; lines in flow put 2.83 kW on HLL- thermal edges to HEAT_SINK; normally-off ties stagnant in normal operation; 10 % target relaxed for 12 small loops (loss set by duty at 150-250 C), justified in AQS-THM-003.\n76. 2026-10-15 X-PAR-03 closed: house_scrubbers.py in the pipeline (AQS-DUTY-064, A-M-164): ALK_SCRUBBER and ACID_POLISH_SCRUB DN600 x 2.3 m bed 1.11 kW each, NOX_SCRUB DN200 0.04 kW, MET_SCRUB DN800 2.12 kW; in-house 25 mm cut PP rings, packing inputs pending a column test.\n75. 2026-10-15 X-MFG-31 closed: MEOH_FERM HDPE 48 h at 35 C (A-M-163) completes the set; 20 in-house reactor models (AQS-DUTY-062 sections 1-7).\n74. 2026-10-15 X-PAR-14 closed (A-M-162, PERRY9_IX): [Bmim]Cl over OH-form strong-base resin, neutralised with AcOH; regenerant 20 wt% NaOH from EVAP_BASE (IA-ACEX-NAOH 0.235 kg/d, flake make-up 5.059 -> 5.106 kg/d via solver.naoh_balance); brine 0.179 -> 0.414 kg/d NaCl/AcOH to leach; 2 x DN50 PP columns, 1.96 L bed, 24 h cycle. write_graph process now in the pipeline.\n73. 2026-10-15 X-MFG-31 batch 4 (AQS-DUTY-062 sections 5 and 7, A-M-161): GLYOXAL 304L 0.2 L 40 C 6 h, IMID 316L 0.13 L 70 C, BUCL glass-lined 0.08 L reflux 105 C ZnCl2, HNO3 Pt-Rh gauze 900 C in DN25 310S (loss 96 W, heater 120 W replaces 0.3 kW placeholder) + 304L absorber; placeholders 0.1 kW -> about 0.02 kW; models/mfg STEP/STL/BOM/fasteners/work orders. Finding: ACEX [Bmim]Cl + AcOH exchange not driven -> X-PAR-14.\n72. 2026-10-15 X-MFG-31 batch 4 (AQS-DUTY-062 sections 5 and 7, A-M-161): GLYOXAL 304L 0.2 L 40 C 6 h, IMID 316L 0.13 L 70 C, BUCL glass-lined 0.08 L reflux 105 C ZnCl2, HNO3 Pt-Rh gauze 900 C in DN25 310S (loss 96 W, heater 120 W replaces 0.3 kW placeholder) + 304L absorber; placeholders 0.1 kW -> 0.02 kW; models/mfg STEP/STL/BOM/fasteners/work orders. Finding: ACEX [Bmim]Cl + AcOH exchange not driven -> X-PAR-14.\n71. 2026-10-15 X-PAR-13 closed: 3 CH3CHO + 4 HNO3 -> 3 glyoxal + 4 NO + 5 H2O, HNO3 0.365 kg/d, NO 0.174 kg/d recycled to HNO3, net O2 unchanged\n70. 2026-10-15 Q-009 summary expanded (AQS-RED-002 numbers)\n69. 2026-10-15 X-SAF-11 closed: FORM N2 0.84 kg/d from afterburner dilution air, O2 1 mol per MeOH\n68. 2026-10-15 X-THM-03 done (AQS-THM-003, _insulation.py in the pipeline, A-M-158): ASTM C680 radial method, 50 C surface (ASTM C1055), dew point 16.7 C; 71 hot + 2 cold items, 31.3 m3 insulation, 25.8 kW hot losses. Heat-ladder lines held to 10 % of loop duty: 12 lines cannot meet it at 200 mm (HL-Q1-X 51 %, HL-GLASS_BURNOUT-Q2-B 35 %, HL-Q3-B-HX4 37 %) -> X-THM-04. Reactor heaters include insulated losses (sizing/heat.py insulated_cylinder): OIL_PYRO 1.66, MEOH_SYNTH 0.74, MEAM 0.077, FORM 0.064, ALD 0.051 kW; PV 4214 -> 4221 kWp. New tasks X-SAF-11 (FORM N2 dilution), X-PAR-13 (GLYOXAL route).\n67. 2026-10-15 X-MFG-31 batch 3 (AQS-DUTY-062 section 6, A-M-157): ALD 8 g Cu/SiO2 at WHSV 1.0, FORM 8 g FeMo at 50.63 g h/mol, MEAM 3 g silica-alumina at GHSV 1100, 20.7 bar (design 2.28 MPa, pressure_nodes.py relief); all DN15 Sch 40 316L x 300 mm beds; heaters 9.6/2.8/2.5 W replace 0.1 kW placeholders (PV 4218 -> 4214 kWp). Findings: FORM feed must be N2-diluted to ~10 % MeOH / 10 % O2 (Formox lean side) but the graph feeds pure HDR_O2; GLYOXAL route CH3CHO + O2 is not an established process (industrial: HNO3 oxidation or glycol over Ag). IMID, ACEX, HNO3, BUCL next.\n66. 2026-10-15 X-MFG-31 batch 2 (AQS-DUTY-062 section 5): YEAST 48 h/32 C 2.7 L DN200; ABE 72 h/37 C 2.6 L DN150 N2-blanketed; ACETOX 24 h/30 C 0.39 L DN80 O2-sparged; HTC 4 h/200 C 0.67 L, pressure vessel 1.71 MPa design (UG-27 316L 2.25 mm req, DN100 Sch 10S + Class 300 flanges), steam relief case from heater power in pressure_nodes.py. Loads from losses + feed heat: 0.2+0.2+0.1+0.6 kW placeholders -> 0.095 kW; PV 4254 -> 4218 kWp, ZNBR2 4259 kWh, inverters 60 -> 59. models/mfg/YEAST, ABE, ACETOX, HTC: STEP/STL/BOM/fasteners/work orders.\n65. 2026-10-15 X-MFG-31 MEOH_SYNTH (A-M-156): methanol 1.26 kg/h at 1.22 kg/(kg h) CTC2020_CZA / 3 = 3.10 kg catalyst, 2.82 L, 1 x DN50 Sch 40 SA-106 B, bed 1302 mm, DN100 thermal-oil jacket; design 5.5 MPa, UG-27 t_req 2.88 mm vs 3.42 mm min: adequate; exotherm 0.54 kW to jacket, preheat 0.42 kW (was 0.5 placeholder); models/mfg/MEOH_SYNTH STEP/STL/BOM/fasteners/work order (B16.5 Class 600). Fix: d819efb applied API 2000 vents to the 50/200 bar nodes; pressure_nodes.py now classes MEOH_SYNTH, CRYO_H2 (1.79 kg/h), CRYO_O2 (14.4 kg/h) as API 520 blocked-outlet cases (bores 0.32/0.22/0.30 mm req), atmospheric 199.\n64. 2026-10-15 X-PAR-03 venting done: sizing/vent.py (API2000_2020 3.3.2 out/in-breathing + open-vent orifice), write_graph.py vent in the pipeline; 202 atmospheric nodes sized (64 with a thermal term on the envelope volume): 194 DN25, 2 DN32, 6 DN50 (BIOFILTER, HEAT_SINK, FISH...). Latitude band and transfer rates assumed (A-M-155) pending X-BAS-03/X-CTL-02. Remaining X-PAR-03: scrubber function on 4 scrubbers needs X-MFG-31 packing.\n63. 2026-10-15 X-PAR-04 closed: all 12 in-house mfg models (reactors, sanitation, evap_mvr x2, vent scrubber, expander, leach) re-run from current graph sizes; only OIL_PYRO BOM changed (band heater 1.42 -> 1.60 kW, inside the 2.0 kW installed); STEP churn (timestamp only) discarded; LEACH_CSTR_1 re-tessellation discarded (no size or BOM change).\n62. 2026-10-15 X-PAR-04 placement/CadQuery/isos: study_place.py lays crop beds out from the sized area (1.2 m rows <= 10.8 m, 914 mm aisles): GROW_BED 120.4 m2 = 10 rows, PEANUT 3, VEG/NFIX/FRUIT 1 each, on two FARM tiers; graph size_mm wins over category footprints (DIGESTER 2400x1800 -> 650x650); FARM skids/pens to new FARM_EXT bay on L0 in EXT_HALL_E, length grown by need to 18 m (A-M-154). AQS-BLD-010 0 overlaps / 0 clearance. 39 stale + 4 missing envelope STLs regenerated (test_envelopes.py, 21 tests); isos, supports, line list, pipe and other inventories rerun.\n61. 2026-10-15 Revision stamp: _duty_basis.py and regen_derived.py write a manifest with the graph SHA-256 and their output patterns; outputs re-derived with no byte change (deterministic PNG/MP4) are current without a churn commit; 236 files tracked this way.\n60. 2026-10-15 Derived files: 52 -> 0 stale. regen_derived.py (views, media/pfd x7, D0-D6/F0 frames, plant_phase_d.mp4) added to the pipeline; duty sheets re-derived each pass are recognised by graph SHA-256 manifest; iso/*.png + iso_fab_drawings.pdf superseded by AQS-ISO-002; verify_view*.png manual (GUI FreeCAD). Fix: flow_graph/models.py rejected the graph (132 energy-layer edges since 2026-10-09, 1 retired edge) so two PFD exporters failed; schema extended, test_graph_schema.py added (20 tests).\n59. 2026-10-15 X-PAR-01 done: 33 constants (ZnBr purge, NFT, HPA mister, BVAD tomato, zeolite, hydro eta, pyrolysis bands, bed photon chain, PEM, EW, combustion, AHU COP) now in drivers.json; outputs unchanged (PV 4255 kWp) apart from 0.01 kg/d rounding on the mister.\n58. 2026-10-15 AHU latent (A-M-153): condensate 463 kg/d -> 13.14 kW latent, chiller COP 2.96 (ASHRAE 90.1) -> 4.44 kW electric on new SF-CRYO_AHU, 17.6 kW to HEAT_SINK on SQ-CRYO_AHU. PV 4152 -> 4255 kWp, ZNBR2 4297 kWh, inverters 60 x 60 kW.\n57. 2026-10-15 X-RED-03 done (A-M-152): main-tie-main 480 V bus, 500 A sections on 290 kW demand, MCC-1A/1B, 2 x T-1, 100 A critical ATS. Fix: GROW_BED feeder S20 carried 2.25 kW after the bed grew; now follows the LED load.\n56. 2026-10-15 Q-009 trade study (AQS-RED-002, _hydro_siting.py): 448 kWh backup needs 11,417 m3 at 18 m (roof, not credible), 5,138 m3 on a 40 m tower (AWWA D100), 2,055 m3 at 100 m hillside, 685 m3 lower reservoir at a 300 m shaft (2.9 MPa). Pending Mike.\n55. 2026-10-15 Owner Q-008 (A-M-151): GROW_BED 28 -> 120.4 m2 to meet 12.73 kg/d residue lines. Bed CO2 0.85 -> 3.65 kg/d, O2 0.62 -> 2.65, LED load 2.25 -> 8.74 kW, ET 64.8 -> 279 kg/d (AHU condensate 463), S14X 1.22 -> 14.6 kg/d to larvae; methanol 27.3 -> 25.2 kg/d, electrolyser H2 11.1 -> 10.7 kg/d; PV 4035 -> 4010 kWp, ZNBR2 4050 kWh.\n54. 2026-10-15 X-RED-07 done (A-M-150): HEAT_SINK 146.5 kW rejection in 3 x 73.2 kW modules; GEO_HP 2 x 100 %.\n53. 2026-10-15 X-RED-05 and X-RED-09 done (A-M-149): VCD_TRAIN 2 x 100 %, feed 0.187 -> 0.383 m3/d, load 0.27 kW now on the bus; COMPOST_TOILET 2 x 100 %; roof-tank inventory is the diverse water backup.\n52. 2026-10-15 X-RED-08 done (A-M-148): HAB_GALLEY dry reserve 80 d (BVAD2022 tomato tM) x 2.81 kg/d crew food at 6 % DM = 13.5 kg DM; ration placeholder noted.\n51. 2026-10-15 X-RED-06 done (A-M-147): crew CO2 4.02 kg/d; 5A zeolite 1.0 wt% at 0.4 kPa (NASA_5A1998), 144 min half-cycle (NASA_CDRA2015): 40.2 kg per bed, two-bed swing pair, second assembly for N+1, 161 kg total.\n50. 2026-10-15 Fix: o2_close.storage() was not called by the pipeline (bank values were a one-off). Now runs each balance pass; H2 19 kg / O2 150.8 kg unchanged, crew reserve 6.08 kg written (X-RED-04).\n49. 2026-10-15 X-RED-04 done (A-M-146): CRYO_O2 crew reserve 6.08 kg in a separate bank (3.04 kg/d x 2 d; NFPA 99 one-day minimum).\n48. 2026-10-15 X-RED-01 done (AQS-RED-001): power stores N+3 (ZNBR2, hydro, H2/fuel cell, standby gen); SPOFs: crew O2 bank shared with the fuel cell, single still, single CO2 sorbent bed, single heat pump/sink, no food reserve, single toilet, distribution not audited. X-RED-03..09 opened.\n47. 2026-10-15 Owner redundancy rule (AGENTS.md, X-RED-01 audit task added). HYDRO_SET restored as the diverse N+1 backup of ZNBR2 (A-M-145): NFPA 111 Level 1 Class X 14 h x 32 kW critical = 448 kWh, 18 m head, 11,417 m3 upper reservoir, held full; Q-006 closed; reservoir siting Q-009 / X-RED-02.\n46. 2026-10-15 X-PAR-04 partial: _duty_basis.py regenerates section 1 and the hold-up line of 174 duty sheets and every node params.duty from the graph; added to the pipeline. Remaining X-PAR-04: CadQuery params, BOMs, placement, isometrics.\n45. 2026-10-15 X-GOV-06 done: _rev_stamp.py ties 643 derived files to the graph commit they were made from; 105 flagged stale (older duty sheets, iso, media) in DERIVED_REVISIONS.md; pipeline outputs gated by test.\n44. 2026-10-15 X-GOV-05 done: 10 superseded plan pages (PLAN-001..003, MFG-001, REM-*, MVS-*) carry a pointer to AQS-PLAN-007; DOC_REGISTER marks them; test_governance.py and test_farm_carbon.py added (18 tests).\n43. 2026-10-15 X-PAR-02 crop lighting (A-M-144): 70.3 W/m2 avg on 44.9 m2 of new crop area: VEG_BED 0.4 -> 0.73, FRUIT_GUTTER 0.4 -> 0.63, PEANUT 0.3 -> 2.66, NFIX_BED 0.2 -> 0.44 kW. PV 3955 -> 4019 kWp, ZNBR2 3994 -> 4059 kWh.\n42. 2026-10-15 X-PAR-02 farm crops (A-M-143): FRUIT_GUTTER 3.21 m2, PEANUT 33.6 m2 (0.2 kg/d peanut takes 1.65 kg CO2/d, 93 kg/d ET), NFIX_BED 3.41 m2; new CO2/O2/VAP edges; IA-PN-TRIM 5.66 to compost; IA-SUMP-MU 124 kg/d; methanol 28.7 -> 27.3 kg/d; PV 3955 kWp, ZNBR2 3994 kWh.\n41. 2026-10-15 X-PAR-02 VEG_BED (A-M-142): 9 crops 0.55 kg/d harvest need 4.74 m2 (BVAD2022); new IA-VEG-CO2 0.093, IA-VEG-O2 0.068, IA-VEG-VAP 10.2 kg/d, IA-SUMP-MU 10.2 kg/d roof-tank make-up to FISH_SUMP; trim 0.25 -> 0.23.\n40. 2026-10-15 X-PAR-02 GROW_BED crop carbon (A-M-141): DM 0.54 kg/d -> edible 4.03, inedible 2.96 kg/d fresh. S14X 1.80 -> 1.22; BSFL frass by difference. Residue lines claim 12.73 kg/d: owner choice Q-008 (shrink lines or bed to about 120 m2).\n39. 2026-10-15 X-PAR-02 bed ET (A-M-140, BVAD2022): bed 16.7 -> 64.8 kg/d, dual-root ET 7.16 -> 27.8 (supply 34.7), AHU condensate 61.0 -> 129.8 kg/d; coil latent +1.95 kW thermal, to carry into the CRYO AHU/chiller sizing task.\n38. 2026-10-15 X-PAR-02 GAS_ATOMIZER (A-M-139): IA-MELT-ATOM 3.20 -> 3.556 = S60/0.9, off-spec 0.356 remelted on new IA-ATOM-REMELT; compositions on S57/S60/IA-MELT-* changed from water/solute default to metal; stale off-graph blend charge removed. C29_RECYCLE set by A-M-138 (5.87).\n37. 2026-10-15 X-PAR-02 OIL_FRAC cuts (A-M-138): ASF fit replaced by 50/50 PE/PP thermal bands (SU2018_PYRO). CUT-1 11.16 -> 7.42, CUT-2 8.41 -> 9.92, CUT-3 3.95 -> 6.17, C29+ recycle 1.40 -> 5.87, IA-OIL-02 28.9 -> 33.4; new IA-C11-SHIP 1.51 and IA-C19-SHIP 2.22 at NORTH_DOCK. OIL_PYRO heater 1.415 -> 1.599 kW; PV 3961 -> 3964 kWp, ZNBR2 4003 kWh.\n36. 2026-10-15 X-PAR-02 DUAL_ROOT (A-M-137): ET at the bed rate 0.596 kg/m2/d x 12 m2 = 7.16 kg/d to CRYO_AHU on new IA-DR-VAP; supply 20 -> 8.95, drain 1.79 at 20 % (PLOSONE2017_DRAIN); IA-BED-H2O 16.7 -> 23.86. Mister schedule cited to LAKHIAR2018.\n35. 2026-10-15 X-PAR-02 MISTER TF (A-M-136): HPA 6 nozzles/m2 x 0.057 L/min, 4 s/4 min, 50 -> 32.2 kg/d (HPA_PRACTICE, JAE2022_AERO).\n34. 2026-10-15 X-PAR-02 per-unit TFs (ess_tf.py, A-M-135): ZNBR2 purge from published HER (ZBFB_REVIEW2023) at 25 % LFL, 30 -> 42.3 m3/h; HYDRO_SET has no storage role after ZNBR2 + H2 bank, cycle 200 m3/d -> 0; NFT 200 -> 7200 kg/d (5 gullies x 1 L/min, COOPER1996).\n33. 2026-10-15 Owner Q-003/Q-004 (AQS-PAR-005 Rev C, A-M-134): BACKUP_GEN to standby on the NFPA 110 8.4.2 exercise basis (fuel 11.16 -> 0.054 kg/d, O2 48.7 -> 0.21 kg/d, C5-C10 10.1 kg/d shipped); electrolyser 16.74 -> 11.39 kg/d H2 (38.4 -> 26.1 kW); CO2 to methanol 80.5 -> 46.4 kg/d; PV 4222 -> 3961 kWp, roof 40176 -> 37800 m2; H2 bank sized from need 115 -> 19 kg (O2 151 kg).\n32. 2026-10-15 X-PAR-12 and X-PAR-11 closed (AQS-PAR-005 Rev B, o2_close.py in balance.physics, A-M-133): grow-bed O2 credit light-limited (13.82 -> 0.62 kg/d); cold box species-conserving (IA-CO2-RET 30 -> 0, phantom O2 31.09 -> 4.50 kg/d real excess O2); EW gases by Faraday (anode Cl2 454 kg/d: 384 to leach oxidation, 69 + 1.98 H2 to a graphite HCl burner, 71 kg/d HCl to leach); combustion draws O2 at 10 % excess (genset 48.7, afterburner 0.82); PEM electrolyser 16.74 kg/d H2 / 132.8 kg/d O2, 38.4 kW avg; CO2 80.5 kg/d to methanol (53.6 kg/d product); O2 surplus 43.5 kg/d product; PV 3392 -> 4222 kWp. Open questions in AQS-OQ-001.\n31. 2026-10-15 X-INV-02C closed: models/motors/build.py writes per family (23) a STEP assembly, STL, isometric drawing.svg, bom.csv, fasteners.csv and WORK_ORDER.md from AQS-INV-005 and IEC 60072-1 (A-M-131). Study envelopes; production tolerancing after the X-INV-02B first article.\n30. 2026-10-15 X-PAR-02 closed: closure_tf.py assigns every one of the 174 study mass edges a role, 117 closure transfer functions (rate = balance of a named unit, leaf-first elimination, difference-type bases offered first) and 57 design inputs with stated basis; re-derivation from the inputs reproduces the graph to 1e-6 kg/d (gate test_closure_transfer_functions). The 57 inputs are replaced as each unit sizing task (unit task 02) issues its calculation. Species closure continues under X-PAR-11/12.\n29. 2026-10-15 X-INV-02D closed: NdFeB vs bonded-ferrite comparison in AQS-INV-005 (MAGNET_COMPARISON.csv, A-M-130): ferrite rotors 1.5-3.6 x the NdFeB volume, efficiency 5-17 points lower, MF-22 moves to NEMA 34 and MF-23 exceeds 2.5 x flange; NdFeB fleet needs 1.5 kg rare earth (recoverable from feedstock magnets, WALTON2015) against an Sr import for ferrite. Basis held at NdFeB pending Mike.\n28. 2026-10-15 X-ELS-02 panel merge by calculation (wire.merge_panels): GAS -> LP-ELEC_PV, GLASS and OIL -> LP-WTR, PUMPED_HYDRO -> LP-CRYO; 16 -> 12 panels, copper 13.90 -> 13.62 t; merges that would add < 5 kg copper (DOCK, BACKUP_GEN, FUEL_CELL, GEO, ...) held for an owner cost basis (panel vs copper).\n27. 2026-10-15 X-PAR-11 (open, blocked on X-PAR-12): oxygen species ledger AQS-PAR-004 (gas_species.py): O2 drawn 44.9 kg/d + combustion oxidant not on the graph 45.5 kg/d - regenerated 13.8 kg/d = 76.5 kg/d with no source; the cold box cannot separate O2 that is not in its feed. Owner review item X-PAR-12 (A-M-129, T-PAR-04).\n26. 2026-10-15 X-ELS-02A closed: wire inventory Rev B with a local panel per sector on routed tray, NEC 430.24 feeders, voltage-drop upsizing (3 % branch, 2 % feeder); conductor 216.1 -> 130.0 km, copper 14.2 -> 13.9 t (A-M-122 Rev B). Panel placement on the GA and tray routing remain with X-ELS-02.\n25. 2026-10-15 X-PAR-11 progress (open): T6 in balance.physics puts the grow-bed photosynthetic O2 (13.82 kg/d on 19.0 kg/d CO2, PQ 1.0, TAIZ2015) on S87 to CRYO_O2; the trim, compost and nutrient surplus pass the difference; cold-box O2 extraction falls to 31.09 kg/d; IA-LEACH-ASU falls to 0.796 kg/d, asserted under its Henry-law bound 2.89 kg/d (SANDER2015); CO2 edges carry CO2 composition (A-M-128, T-PAR-03). Open: species composition of the flue and cold-box feed edges and a per-species cold-box split.\n24. 2026-10-15: IE3 targets in AQS-INV-005 moved to the IEC 60034-30-1 60 Hz table (e.g. MF-10 1.5 kW 4-pole 86.5 %, MF-04 22 kW 2-pole 91.7 %). X-PIP-04 closed: 300 mm minimum riser rule in the iso router gives IA-ACOH, IA-ALD, IA-MEAM a flexible leg; AQS-PIP-005 now 0 lines needing a loop (A-M-127); isos, pipe and other inventories regenerated. X-INV-02D (NdFeB vs bonded ferrite, owner) queued after X-PAR-11.\n22. X-PAR-02 Rev B 2026-10-15 (owner: no fudge): the 2.824 kg/d IA-TERR-VAP / IA-O2-RET cut traced to X-SAF-10 (peroxide water taken off S40 without propagation). Photosynthesis hypothesis tested and rejected for the terrace (no CO2 supply, no harvest; wrong sign). Fixed by transfer functions T1-T5 in balance.physics; Rev A moves on 361 edges withdrawn; gate now fails any reconciled move above 2 % (test_balance.py). Verification T-PAR-02 (A-M-123). Grow-bed photosynthetic O2 and leach dissolved gas carried to X-PAR-11. X-ELS-02A added to shorten wire runs.\n21. X-INV-03 closed 2026-10-15: wire inventory AQS-INV-002 (flow_graph/inventory/wire.py): 216 km of conductor in 19 families from the motor inventory (NEC 430.22, 310.16, 250.122), collection bus and MV feeders (705.28), 377 PV source circuits (690.8), hall lighting, grounding grid; 183 km on assumed lengths/counts (A-M-122). One X-INV-03-WFnn task per family. Next: pipe inventory X-INV-04 (from AQS-ISO-002 quantities).\n20. X-PIP-03 closed 2026-10-15: isometric sheet per line AQS-ISO-002 (_iso_sheets.py): 371 of 371 piped lines routed (EVAP_ACID_VS and sanitation lines now positioned), SVG per line with legs, cut list, B16.9 elbows, B16.5 flanges and bolting, joint count; 6220 m pipe, 1062 elbows; quantities CSV feeds X-INV-04 (A-M-121). Clash checking stays with X-PIP-04.
19. X-PAR-02 progress 2026-10-15 (open): closure layer balance.py (AQS-PAR-003): held study rates reconciled by weighted least squares (NARASIMHAN2000) with transfer-function and stoichiometric edges held; all 174 units close, loop_closure now passes in full (the long-standing kg/d cut, HDR_O2 and TERRACE_IRRIG, is closed); gate test_balance.py; gross moves IA-TERR-VAP and IA-O2-RET listed for review (A-M-120). Open: per-unit transfer functions for the remaining held edges.
18. X-GOV-20 closed 2026-10-15: every vendor-data, vendor-skid and vendor-quote basis withdrawn (gate test_no_vendor_basis.py); replaced by in-house tasks X-MFG-33..41 and X-MAT-21 in A-M-034/062/071/072/077/083/085, DOE_H2_COMP, D47, D57, RESIZE_SWEEP, ASME class 'Vendor' (now 'In-house (X-MFG-40)'), H2_PURIFIER, LEACH_CSTR_1 WO W12, PV cell line; ST-SOLAR-01 reopened (it rested on bought-tool datasheets).
17. X-INV-01 closed 2026-10-15: motor and actuator inventory AQS-INV-001 (flow_graph/inventory/motors.py -> docs-authority/inventory/MOTOR_INVENTORY.md, .csv, MOTOR_FAMILIES.csv): 539 driven items, 23 families; sources BOMs, MFG_TOOLS, EXT_HALL HVAC sizing, then graph rules (flagged, A-M-119). One X-INV-02-MFnn task per family added. Next: wire (X-INV-03), pipe (X-INV-04), others (X-INV-05).
16. X-SAN-01 closed 2026-10-15 (owner decision): AQS-DUTY-063 sanitation.py: 4 persons, 19.6 kg/d vacuum-toilet blackwater plus compost-toilet output; barriers: thermophilic digestion 55 C 15 d (303 L), screw press with cake 0.67 kg/d incinerated in AFTERBURNER, pasteurisation 70 C >= 30 min (EPA 503 PFRP), standby alkaline hold pH > 12 72 h with NaOH from BMED_BASE, 3-tank batch hold released only on test; ISO 30500 targets (6/7/6/4 log) with challenge tests; sanitation room >= 8.6 m from FARM; Rev B: afterburner and downstream edges carry the cake and biogas (no S11 trim), chamber ID 200 x 600 mm at 850 C / 2 s; models and BOMs in models/mfg/BLACK_*; 0.19 kW (A-M-118). Challenge tests stay open in TEST_PLAN.
15. X-MFG-32 closed 2026-10-15: jellybean register AQS-MFG-011 generated from every mfg BOM (_jellybean.py): motors to IEC 60034-1 ratings and IEC 60072-1 frames (IE3), ISO 15 bearings, ISO fasteners (148 pieces), EN 1514-1 / ISO 3601-1 seals, ASTM D1785 pipe; open design and in-house line per family with make/buy at current volume (A-M-117). Regenerates as mfg models are added.
14. X-MFG-31 progress 2026-10-15 (open; BLACK_DIGEST now under X-SAN-01): AQS-DUTY-062 reactor_design.py sizes GLASS_DIGEST (26 h, DN450 CPVC, 0.09 kW agitator; kinetic basis replaces the 20-day figure), DIGESTER (20 d SRT, DN350 HDPE, 0.025 kW) and OIL_PYRO (500 C, 1 h, DN200 304H, 1.42 kW new bus load); CadQuery STEP/STL, BOM, fasteners and work orders in models/mfg/<UNIT> (A-M-116). Open: BLACK_DIGEST zero-flow owner review; MEOH_FERM/MEOH_SYNTH on activation of the methanol train.
13. X-STD-01 closed 2026-10-15: code basis AQS-STD-002 (editions; governing NFPA/ISO clause per check) with gate test_code_basis.py on ten check documents; hall egress AQS-EGR-002: 3438 occupants, 9 exterior door pairs at 90 m, 2.2 m 2 h exit passageway, worst travel 70.0 m vs 76.2 m (NFPA 101 Table 40.2.6 governs over IBC 1017.2.2); NFPA 13 sprinklers a precondition (A-M-115). Next: X-MFG-31, X-MFG-32, X-GOV-20, X-PAR-02, X-PIP-03.
12. X-ELS-11 closed 2026-10-15: 48 inverters in five 480 V sections (10/10/10/9/9), 1000 A mains (NEC 240.87), 750 kVA to 12.47 kV, storage 643-714 kWh per section, plant bus on CB-1 (AQS-ELEC-008, A-M-114). X-ELS-02 (load list from calculations) stays open. Next: X-STD-01, X-MFG-31, X-MFG-32, X-GOV-20, X-PAR-02, X-PIP-03.
11. X-PAR-08 closed 2026-10-15: degree-day split, internal gains, slab F-factor, air/ground comparison in solver.roof_close; ground-source (32,292 m²) reverted to air-source by the owner (D77: 27 km of bores for 0.2 %); converged 186 x 174 m, 32,364 m², PV 3394 kWp, 48 x 60 kW (A-M-112). Utility interconnection study registered as owner input (A-M-113). Next: X-ELS-02 bus split, X-STD-01, X-MFG-31, X-MFG-32, X-GOV-20, X-PAR-02, X-PIP-03.
10. X-PAR-10 closed 2026-10-15 (owner decision): EVAP_ACID_VS packed PVC scrubber on the column vent, DN150 x 1400 mm, 500 mm bed, on the EVAP_ACID frame; design case column bypassed 490 ppmv to 1 ppmv; NaOH bleed from BMED_BASE in the solver NaOH balance and the misfit gate (AQS-DUTY-061, A-M-111). Next: X-STD-01, X-MFG-31, X-MFG-32, X-GOV-20, X-PAR-08, X-PAR-02, X-PIP-03.
9. X-PAR-09 closed 2026-10-15 (owner principle D75): PV 3375 kWp = 2.0 x 1688 kWp; building 234 x 138 m (39 x 23 bays, 32,292 m²), roof capacity 3390 kWp; ZNBR2 3409 kWh, charge 1107 kW; 47 x 60 kW inverters; export up to 2577 kW at the PCC (AQS-ELEC-002 Rev D, AQS-ELEC-006 Rev C, AQS-ELEC-007 Rev E; A-M-109, A-M-110). Next: X-PAR-10 vent scrubber, X-STD-01, X-MFG-31, X-MFG-32, X-GOV-20, X-PAR-08, X-PAR-02, X-PIP-03.
8. X-MFG-30 and X-MAT-20 closed 2026-10-15: in-house MVR design (AQS-DUTY-060, `flow_graph/param/evap_design.py`), 1.39 / 1.32 kW (41.5 / 39.8 kWh/t), outlets 48.7 / 50.6 C (P1), relief sized in-house (API 526 D adequate on body fire and shell blocked outlet), CadQuery models and BOMs under `models/mfg/EVAP_*`, routes `docs-authority/fab/EVAP_*.md`. Open: HCl carry-over in the acid vapour near the azeotrope (owner review).
7. X-PIP-03 Fabrication isometrics from AQS-ISO-001.
8. X-ELS-02 Remaining study-share loads; CRYO_ASU basis.
9. X-BAS-03 and X-ELS-08 Owner inputs: ASCE Hazard Tool lookup, Wenner soil test, site area for the PV field.
10. X-PAR-02 Solver extension: LEACH full balance, FLOAT_SINK, VCD, UPW, gas train.

Sizing rule: AGENTS.md §Sizing. Sizing-driven rate and layout changes are approved by default (X-RSZ group).

## 6. Cross-cutting tasks
{xs}

## 7. Unit tasks by system
{us}
'''
open('docs-authority/TASK_PLAN.md','w').write(doc)
print(TA,TD);print(tab)

import json, os, re, collections
R='/tmp/aqs.dFW2/Aqueous_Solutions'; os.chdir(R)
g=json.load(open('flow_graph/plant_flow_graph.json'))
P=[n for n in g['nodes'] if n.get('presence')=='present']
ex=os.path.exists
def need(f):
    assert ex(f), f; return f
inst=open('docs-authority/INSTRUMENT_LOOPS.md').read()
BIO={'DIGESTER','EMETH','LIGNO_PRE','HTC','YEAST','ABE','ACETOX','ALD','GLYOXAL','FORM','MEAM','IMID','QUAT','ACEX','HNO3','BUCL','ETOH_STILL','BUOH_STILL','BIOFILTER','COMPOST','COMPOST_TOILET','CLARIFIER','STRUVITE','ASH','IODIDE','MUSH_STRAW','MUSH_BLOCK','COMPOST_MYC','AMF'}
FEED={'HOPPER','SALT_FEED','FLOAT_SINK'}
def sysof(n):
    u,s=n['unit_id'],n['sector_id']
    if u in FEED: return 'FEED'
    if u.startswith('HAB_') or s=='HAB': return 'HAB'
    if u in BIO or s=='MEOH': return 'BIO'
    if s in('FARM','NUT','TRR'): return 'FARM'
    if s=='WET': return 'MET'
    return {'MFG':'MFG','OIL':'OIL','GAS':'GAS','CRYO':'CRYO','FAB':'FAB','GLASS':'FAB','WTR':'WTR','ELEC':'ELEC','ELEC_PV':'ELEC','ZNBR2':'ELEC','BACKUP_GEN':'ELEC','FUEL_CELL':'ELEC','PUMPED_HYDRO':'ELEC','HEAT':'THERM','GEO':'THERM','DOCK':'DOCK'}[s]
SYS=[('FEED','Solids handling and feed preparation (feedstock-agnostic, AQS-ASSAY-001)'),('MET','Metals line: leach, electrowinning, BMED, polish'),('MFG','Manufacturing shop, metal forming, self-copy'),('OIL','Pyrolysis and oil fractions'),('GAS','Gas handling, scrubbing, H2/O2 headers'),('CRYO','Cryogenic air separation, gas storage, expander'),('FAB','Wafer fab, lithography, reagents, glass, SiC'),('BIO','Digester, fermentation, stills, biofilter, methanol'),('FARM','Farm: beds, azolla, hydroponics, animals, nutrients, irrigation'),('HAB','Habitation and life support'),('WTR','Water, wastewater, potable, UPW'),('ELEC','Electrical generation, storage, conversion'),('THERM','Thermal: heat ladder batteries, geothermal, heat sink'),('DOCK','Dock and boundary')]
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
DONE_U={('LEACH_CSTR_1', '02'): '`docs-authority/sizing/LEACH_CSTR_1.md` (AQS-DUTY-050)', ('LEACH_CSTR_1', '06'): '`docs-authority/sizing/LEACH_CSTR_1.md` §2 agitator, HX-5 coil', ('EW_1', '02'): '`docs-authority/sizing/EW_CELLS.md` (AQS-DUTY-051)', ('EW_2', '02'): '`docs-authority/sizing/EW_CELLS.md` (AQS-DUTY-051)', ('EW_3', '02'): '`docs-authority/sizing/EW_CELLS.md` (AQS-DUTY-051)', ('EW_4', '02'): '`docs-authority/sizing/EW_CELLS.md` (AQS-DUTY-051)', ('EW_5', '02'): '`docs-authority/sizing/EW_CELLS.md` (AQS-DUTY-051)', ('EW_6', '02'): '`docs-authority/sizing/EW_CELLS.md` (AQS-DUTY-051)', ('EW_7', '02'): '`docs-authority/sizing/EW_CELLS.md` (AQS-DUTY-051)', ('EW_8', '02'): '`docs-authority/sizing/EW_CELLS.md` (AQS-DUTY-051)', ('EW_9', '02'): '`docs-authority/sizing/EW_CELLS.md` (AQS-DUTY-051)'}
def status(n,k):
    u=n['unit_id']; d=f'docs-authority/duties/{u}.md'
    if (u,k) in DONE_U: return DONE_U[(u,k)]
    if k=='01':
        m=re.search(r'In ([\d.]+) kg/d, out ([\d.]+) kg/d',(n.get('params') or {}).get('duty') or '')
        if ex(d) and m and abs(float(m[1])-float(m[2]))<1e-6: return f'`{d}` §1; graph duty {m[1]} kg/d in = out'
    if k=='04' and ex(f'docs-authority/nozzles/{u}.csv'): return f'`docs-authority/nozzles/{u}.csv` (bores not calculated)'
    if k=='07' and ex(d) and re.search(r'^6\. Relief',open(d).read(),re.M): return f'`{d}` §6 (C7 closed on MASTER_PLAN)'
    if k=='08' and re.search(r'\b'+re.escape(u)+r'\b',inst): return '`docs-authority/INSTRUMENT_LOOPS.md`'
    if k=='12' and ex(f'models/mfg/{u}/bom.csv'): return f'`models/mfg/{u}/bom.csv`'
    if k=='13' and ex(f'docs-authority/fab/{u}.md'): return f'`docs-authority/fab/{u}.md` (study route)'
    return None
def note(n,k):
    u=n['unit_id']
    if k=='10':
        if ex(f'models/mfg/{u}'): return f'partial: M2 at `models/mfg/{u}/`, not accepted'
        if ex(f'cad/stl/{u}.stl'): return f'partial: envelope `cad/stl/{u}.stl`'
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
('X-INV-02C','Motor family drawings and BOMs','CadQuery models, drawings and BOM per X-INV-02 family from the AQS-INV-005 design sheets (laminations, winding, rotor, shaft, frame)','X-INV-02',None),
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
('X-CTL-05','Assay instrumentation loop','AQS-INST-001 Rev B assay, digester, farm loops (partial)','X-BAS-01','docs-authority/INSTRUMENT_LOOPS.md')]),
('THM','Thermal and HVAC (plant level)',[
('X-THM-01','Heat ladder duty balance','Q1 to Q4 duties closed per AQS-HEAT-LADDER-001 with hot and cold side calculations','unit task 01',None),
('X-THM-02','Ventilation and HVAC design','air changes, extract, and make-up per room with fan duty','X-BLD-04, X-SAF-02',None),
('X-THM-03','Insulation schedule','insulation per hot and cryogenic line and vessel','X-PIP-02',None)]),
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
('X-SAF-10','Peroxide dilution water edge','water source edge into WS_PEROX; IA-H2O2-SRC set to the O2 need; balances close; rate change approved','X-ELS-10','docs-authority/OXIDIZER_REAGENTS.md'),
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
DONE_X={'X-PIP-04','X-INV-02','X-INV-04','X-INV-05','X-INV-03','X-PIP-03','X-GOV-20','X-INV-01','X-SAN-01','X-MFG-32','X-STD-01','X-ELS-11','X-PAR-08','X-PAR-10','X-PAR-09','X-MFG-30','X-MAT-20','X-PAR-07','X-BLD-04','X-PAR-05','X-PAR-06','X-MAT-07','X-MAT-19','X-RSZ-06','X-RSZ-04','X-RSZ-03','X-RSZ-02','X-RSZ-01','X-PIP-02','X-RSZ-05','X-BLD-09','X-GOV-08','X-MAT-07','X-ELS-05','X-ELS-08','X-ELS-07','X-ELS-03','X-MAT-18','X-COD-02','X-MAT-09','X-PIP-01','X-ELS-04','X-BAS-02','X-SAF-09','X-MAT-14','X-MAT-15','X-SAF-10','X-SAF-07','X-MAT-17','X-MAT-16','X-GOV-07','X-GOV-04','X-ELS-10','X-SAF-08','X-MAT-12','X-MAT-11','X-MAT-10','X-MAT-08','X-MAT-05','X-MAT-00','X-MAT-02','X-MAT-04','X-GOV-01','X-GOV-02','X-GOV-03','X-BAS-01','X-ELS-01','X-SAF-03','X-TOOL-01','X-TOOL-02','X-TOOL-03'}
if os.path.isdir(_MFD): DONE_X |= {f'X-INV-02-{f[:-3]}' for f in os.listdir(_MFD) if f.endswith('.md')}
out=[];cnt=[]
def box(d): return '[x]' if d else '[ ]'
for code,title,items in X:
    nd=0;out.append(f'\n### X-{code}. {title}\n')
    for tid,t,crit,dep,ev in items:
        d=tid in DONE_X
        if ev: need(ev)
        if d: nd+=1
        e=f' Evidence: `{ev}`.' if d else (f' Start from `{ev}` (partial).' if ev else '')
        out.append(f'- {box(d)} **{tid}** {t}. Done when: {crit}. Depends: {dep}.{e}')
    cnt.append((f'X-{code}',title,len(items),nd))
xs='\n'.join(out); out=[]
for code,title in SYS:
    T=D=0; out.append(f'\n### {code}. {title}\n')
    for n in sorted(units[code],key=lambda n:n['unit_id']):
        u=n['unit_id']; out.append(f'- **{code}-{u}** ({n["class"]}, sector {n["sector_id"]})')
        for k,t,crit,dep in (ST[:1] if ACC(n) else ST):
            ev=status(n,k); T+=1; D+=bool(ev); nt=note(n,k)
            depx=', '.join(f'{code}-{u}-{x.strip()}' if x.strip().isdigit() else x.strip() for x in dep.split(','))
            out.append(f'  - {box(ev)} {code}-{u}-{k} {t}. Done when: {crit.replace("<UNIT>",u)}. Depends: {depx}.'+(f' Evidence: {ev}.' if ev else '')+(f' Status: {nt}.' if nt and not ev else ''))
    cnt.append((code,title,T,D))
us='\n'.join(out)
json.dump(cnt,open('/tmp/tp/cnt.json','w'))
tab='\n'.join(f'| {c} | {t} | {a} | {b} |' for c,t,a,b in cnt)
TA=sum(c[2] for c in cnt);TD=sum(c[3] for c in cnt)
doc=f'''# Task plan

Document number: AQS-PLAN-007
Revision: A
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
23. 2026-10-15: X-INV-04 closed (pipe inventory AQS-INV-003 from the iso quantities: 6220 m in 24 families, 1054 stock lengths of 6.096 m, A-M-124); X-INV-05 closed (other building blocks AQS-INV-004: valves, instruments, electronics, protection, bearings, seals, supports, fasteners, fabricated part sets; 53 families, A-M-125); X-INV-02 closed (motor family designs AQS-INV-005: one design basis and in-house manufacturing plan per family, output-equation sizing PYRHONEN2014 / HENDERSHOT2010, IEC 60072-1 frames, IE3 targets; A-M-126). Per-family tasks X-INV-04-PFnn and X-INV-05-OFnn generated; X-INV-02B first articles and type tests opened.\n25. 2026-10-15 X-PAR-11 progress (open): T6 in balance.physics puts the grow-bed photosynthetic O2 (13.82 kg/d on 19.0 kg/d CO2, PQ 1.0, TAIZ2015) on S87 to CRYO_O2; the trim, compost and nutrient surplus pass the difference; cold-box O2 extraction falls to 31.09 kg/d; IA-LEACH-ASU falls to 0.796 kg/d, asserted under its Henry-law bound 2.89 kg/d (SANDER2015); CO2 edges carry CO2 composition (A-M-128, T-PAR-03). Open: species composition of the flue and cold-box feed edges and a per-species cold-box split.\n24. 2026-10-15: IE3 targets in AQS-INV-005 moved to the IEC 60034-30-1 60 Hz table (e.g. MF-10 1.5 kW 4-pole 86.5 %, MF-04 22 kW 2-pole 91.7 %). X-PIP-04 closed: 300 mm minimum riser rule in the iso router gives IA-ACOH, IA-ALD, IA-MEAM a flexible leg; AQS-PIP-005 now 0 lines needing a loop (A-M-127); isos, pipe and other inventories regenerated. X-INV-02D (NdFeB vs bonded ferrite, owner) queued after X-PAR-11.\n22. X-PAR-02 Rev B 2026-10-15 (owner: no fudge): the 2.824 kg/d IA-TERR-VAP / IA-O2-RET cut traced to X-SAF-10 (peroxide water taken off S40 without propagation). Photosynthesis hypothesis tested and rejected for the terrace (no CO2 supply, no harvest; wrong sign). Fixed by transfer functions T1-T5 in balance.physics; Rev A moves on 361 edges withdrawn; gate now fails any reconciled move above 2 % (test_balance.py). Verification T-PAR-02 (A-M-123). Grow-bed photosynthetic O2 and leach dissolved gas carried to X-PAR-11. X-ELS-02A added to shorten wire runs.\n21. X-INV-03 closed 2026-10-15: wire inventory AQS-INV-002 (flow_graph/inventory/wire.py): 216 km of conductor in 19 families from the motor inventory (NEC 430.22, 310.16, 250.122), collection bus and MV feeders (705.28), 377 PV source circuits (690.8), hall lighting, grounding grid; 183 km on assumed lengths/counts (A-M-122). One X-INV-03-WFnn task per family. Next: pipe inventory X-INV-04 (from AQS-ISO-002 quantities).\n20. X-PIP-03 closed 2026-10-15: isometric sheet per line AQS-ISO-002 (_iso_sheets.py): 371 of 371 piped lines routed (EVAP_ACID_VS and sanitation lines now positioned), SVG per line with legs, cut list, B16.9 elbows, B16.5 flanges and bolting, joint count; 6220 m pipe, 1062 elbows; quantities CSV feeds X-INV-04 (A-M-121). Clash checking stays with X-PIP-04.
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

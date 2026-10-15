"""X-PAR-04 graph writer. Writes solver values into flow_graph/plant_flow_graph.json:
acid-loop decision (BMED at 2 M, EVAP_ACID and EVAP_BASE to 20 wt%), BMED energy, EW cell and
DC bus power, RECT_EW, and the SOL_ARK bus balance on IA-PV-01. Idempotent.
Stage 'power' (after the load list, one line and AQS-ELEC-007 are regenerated) writes PV, storage
and inverter sizes from docs-authority/_power_sizing.py.
Run: python3 -m flow_graph.param.write_graph [process|power]"""
import json, math, os, subprocess, sys
from . import solver, drivers as DR
ROOT = solver.ROOT; GP = os.path.join(ROOT,'flow_graph/plant_flow_graph.json')
TAG = 'X-PAR acid-loop decision (AQS-PAR-001 \u00a73)'
ELEC_IN = ('S17-BMED','S17-EW','SF-EVAP_ACID','SF-EVAP_BASE','SF-EVAP_ACID_VS')

def rate(v, unit, note): return {'value': round(v,4), 'unit': unit, 'status': 'study', 'note': note}

def edge(sid, a, b, phase, layers, carries, r, sa, sb, header='dedicated'):
    return {'stream_id': sid, 'from_unit_id': a, 'to_unit_id': b, 'phase': phase, 'layers': layers, 'presence': 'present',
            'carries': carries, 'header': header, 'forbidden': 'HDR_O2, HDR_CO2', 'claim_status': 'Claimed / Partial', 'rate': r,
            'from_sector_id': sa, 'to_sector_id': sb, 'open_boundary': False, 'namespace': 'IA' if sid.startswith('IA') else 'S',
            'gap_flags': [], 'notes': None}

def bus_load(g):
    return sum(e['rate']['value'] for e in g['edges'] if e['stream_id'] in ELEC_IN)

def process():
    d, g, s = solver.solve()
    N = {n['unit_id']: n for n in g['nodes']}; E = {e['stream_id']: e for e in g['edges']}
    before = bus_load(g)
    # BMED energy from published SEC at 2 M
    kw = s['bmed']['kW_published']
    N['BMED_ACID']['continuous_kw'] = rate(kw,'kW',f"{TAG}. BMED stack: {s['bmed']['base_kg_d']:.2f} kg/d NaOH x {s['bmed']['sec_kWh_kg']:.2f} kWh/kg from triplet voltage {s['bmed']['voltage']['V_design']:.2f} V at CE {DR.val(d,'bmed_CE')} (STRATHMANN2004, CRC_COND, EDBM_PILOT_2023; AQS-DUTY-068) / 24 h. Solver flow_graph/param/solver.py bmed().")
    E['S17-BMED']['rate'] = rate(kw,'kW',f'{TAG}. 480 V feed equal to BMED_ACID continuous_kw.')
    B12 = N['CRYO_O2']['params'].get('x_par_12_base')
    if B12: B12['BMED_kW'] = round(kw,4); B12['S17-BMED'] = round(kw,4)   # X-PAR-12 rescaling base follows the solver BMED energy
    # NaOH balance (owner decision 2026-10-15): stoichiometric draws, make-up from the dock, sodium purge
    nb = s['naoh']; wb = DR.val(d,'base_conc_design_wt'); NT = f'{TAG}; NaOH balance (owner decision 2026-10-15)'
    E['IA-BASE-PPT']['rate'] = rate(nb['ppt_kg_d']/wb,'kg/d',f"{NT}. {nb['ppt_mol']:.0f} mol/d NaOH, one per leached chloride (GREENWOOD), as {wb*100:.0f} wt%.")
    E['IA-BASE-01']['rate'] = rate(nb['digest_kg_d']/wb,'kg/d',f"{NT}. {nb['digest_mol']:.1f} mol/d NaOH = 2 x SiO2 dissolved (IA-GLASS-03 less S08G, all as SiO2, bounding; GREENWOOD), as {wb*100:.0f} wt%.")
    if 'IA-ACEX-NAOH' in E: E['IA-ACEX-NAOH']['rate'] = rate(nb['acex_kg_d']/wb,'kg/d',f"{NT}. {nb['acex_mol']:.2f} mol/d NaOH, one per [Bmim]Cl, OH-form resin regeneration (X-PAR-14, A-M-162), as {wb*100:.0f} wt%.")
    E['IA-DIG-LIQ']['rate'] = rate(E['IA-BASE-01']['rate']['value'],'kg/d',f'{NT}. Silicate liquor equal to the digest NaOH draw (digest closes on IA-GLASS-03, S08G, IA-SIL-SRC, IA-SIC-IN).')
    for t in (N['GLASS_DIGEST']['params'].get('balance_rev_l') or {}).get('terms', []):
        if t['layer']=='mass' and ('digest liquor' in t['label'] or 'silicate liquor' in t['label']):
            t['value'] = round(nb['digest_mol']/DR.val(d,'bmed_product_molarity')*1.081, 3); t['basis'] = f"{nb['digest_mol']:.1f} mol/d at 2 M, 1.081 kg/L (PERRY9_HCL); {NT}"
    mk = [edge('IA-NAOH-MU','NORTH_DOCK','EVAP_BASE','S',['mass'],'purchased NaOH flake make-up',rate(nb['makeup_kg_d'],'kg/d',f"{NT}. Demand {nb['ppt_mol']+nb['digest_mol']:.0f} mol/d less BMED {nb['bmed_mol']:.0f} mol/d; worst case, no credit for sodium returned in the silicate liquor."),'DOCK','WET'),
          edge('IA-NA-PURGE','LEACH_CSTR_1','NORTH_DOCK','L',['mass'],'sodium salt purge equal to the make-up mass',rate(nb['makeup_kg_d'],'kg/d',f'{NT}. Sodium brought in on IA-NAOH-MU leaves the loop as salt; mass equal to the make-up (study).'),'WET','DOCK')]
    for e in mk:
        if e['stream_id'] in E: E[e['stream_id']]['rate'] = e['rate']
        else: g['edges'].append(e); E[e['stream_id']] = e
    # evaporators
    for side, key, src, prods, sa in (('ACID','evap_acid','BMED_ACID',('IA-ACID-01',),'HCl'),('BASE','evap_base','BMED_BASE',solver.BASE_DEMAND,'NaOH')):
        u = f'EVAP_{side}'; v = s[key]; w = DR.val(d,'acid_conc_design_wt' if side=='ACID' else 'base_conc_design_wt')
        note = (f"{TAG}. MVR evaporator, {sa} from 2 M ({DR.val(d,'bmed_product_wt_'+side.lower())*100:.2f} wt%) to {w*100:.0f} wt%"
                + (f" (below the HCl azeotrope {DR.val(d,'hcl_azeotrope_wt')*100:.1f} wt%, PERRY9_HCL)" if side=='ACID' else '')
                + f"; water off {v['water_kg_d']:.1f} kg/d x {v['design']['kWh_per_t']} kWh/t (in-house MVR design X-MFG-30, AQS-DUTY-060: blower {v['design']['comp_elec_kW']:.3f} kW, recirculation {v['design']['pump_kW']:.3f} kW, trim {v['design']['trim_kW']:.3f} kW) = {v['kW']:.2f} kW. Study.")
        node = N.get(u) or {'unit_id': u, 'sector_id': 'WET', 'presence': 'present', 'class': 'evaporator', 'tags': [], 'electrical_role': 'load',
                            'diagram_gap': None, 'enabled': True, 'modules': [], 'params': {}}
        node['notes'] = f'{sa} concentrator after {src} ({TAG}). Wetted parts per ULLMANN_HCL (impregnated graphite or fluoropolymer-lined; study).' if side=='ACID' else f'{sa} concentrator after {src} ({TAG}). Nickel or fluoropolymer-lined wetted parts (study).'
        node['continuous_kw'] = rate(v['kW'],'kW',note)
        node['params'].update({'presence':'present','water_off_kg_d':round(v['water_kg_d'],2),'feed_wt':DR.val(d,'bmed_product_wt_'+side.lower()),'product_wt':w,
                               'mvr_kWh_per_t':v['design']['kWh_per_t'],'size_mm':node['params'].get('size_mm',[1200,900,2000]),'doc':'AQS-PAR-001, AQS-DUTY-060'})
        node['params'].setdefault('size_note','L x W x H mm, set by flow_graph/param/evap_design.py (X-MFG-30)')
        if u not in N: g['nodes'].append(node); N[u] = node
        new = [edge(f'IA-{u}-FEED', src, u, 'L', ['mass'], f'{sa} 2 M from BMED', rate(v['feed_kg_d'],'kg/d',f'{TAG}. {v["solute_kg_d"]:.2f} kg/d {sa} / {DR.val(d,"bmed_product_wt_"+side.lower())}.'),'WET','WET'),
               edge(f'IA-{u}-COND', u, src, 'L', ['mass'], 'evaporator condensate return (BMED water make-up)', rate(v['water_kg_d'],'kg/d',f'{TAG}. Water evaporated, condensed and returned to {src}.'),'WET','WET'),
               edge(f'SF-{u}', 'SOL_ARK_60K', u, 'E', ['elec'], '480 V AC', rate(v['kW'],'kW',f'{TAG}. 480 V feed equal to {u} continuous_kw.'),'ELEC','WET','tray'),
               edge(f'SQ-{u}', u, 'HEAT_SINK', 'E', ['energy'], 'electrical input leaving as heat', rate(v['kW'],'kW',f'{TAG}. Compressor work leaves as heat (A-M-086).'),'WET','GEO','tray')]
        for e in new:
            if e['stream_id'] in E: E[e['stream_id']].update({k: e[k] for k in ('rate','from_unit_id','to_unit_id','carries')})
            else: g['edges'].append(e); E[e['stream_id']] = e
        for p in prods:
            E[p]['from_unit_id'] = u; E[p]['from_sector_id'] = 'WET'
    # X-PAR-10 vent scrubber on the EVAP_ACID column vent (owner decision 2026-10-15; AQS-DUTY-061)
    vs = s['vs']; up = vs['upset']; VT = f'{TAG}; X-PAR-10 vent scrubber (AQS-DUTY-061)'
    nd = N.get('EVAP_ACID_VS') or {'unit_id': 'EVAP_ACID_VS', 'sector_id': 'WET', 'presence': 'present', 'class': 'scrubber', 'tags': [], 'electrical_role': 'load',
                                    'diagram_gap': None, 'enabled': True, 'modules': [], 'params': {}}
    nd['notes'] = 'Packed PVC alkali scrubber on the EVAP_ACID column vent; NaOH bleed from BMED_BASE; spent liquor to BMED_ACID. Duty sheet docs-authority/duties/EVAP_ACID_VS.md.'
    nd['continuous_kw'] = rate(vs['pump_kW'],'kW',f"{VT}. Sump recirculation pump {up['recirc_m3_h']*1000:.0f} L/h at the minimum wetting rate (PERRY9_ABS), 10 m head, 40 % efficiency (study).")
    nd['params'].update({'presence':'present','DN':vs['DN'],'packed_mm':vs['packed_mm'],'height_mm':vs['height_mm'],'sump_L':vs['sump_L'],'material':vs['material'],
                         'y_in_ppm_design':round(up['y_in_ppm'],1),'y_out_ppm':up['y_out_ppm'],'design_case':'upset: column bypassed (A-M-111)',
                         'size_mm':[400, 400, vs['height_mm']],'size_note':'L x W x H mm, set by flow_graph/param/vent_scrubber.py (X-PAR-10)','doc':'AQS-DUTY-061'})
    if 'EVAP_ACID_VS' not in N: g['nodes'].append(nd); N['EVAP_ACID_VS'] = nd
    vn = [edge('IA-EVAP_ACID-VENT','EVAP_ACID','EVAP_ACID_VS','G',['mass'],'column vent: non-condensables, water vapour, trace HCl',rate(up['vent_kg_d'],'kg/d',f"{VT}. Air from the feed (WEISS1970) saturated at the vent condenser; design case {up['y_in_ppm']:.0f} ppmv HCl."),'WET','WET'),
          edge('IA-VS-NAOH','BMED_BASE','EVAP_ACID_VS','L',['mass'],'NaOH 2 M bleed',rate(up['naoh_soln_kg_d'],'kg/d',f"{VT}. {vs['upset']['naoh_mol_d']*1000:.3f} mmol/d = {DR.val(d,'vs_naoh_excess')} x HCl absorbed."),'WET','WET'),
          edge('IA-VS-SPENT','EVAP_ACID_VS','BMED_ACID','L',['mass'],'spent scrub liquor (NaCl in NaOH) to the BMED brine',rate(up['spent_kg_d'],'kg/d',f'{VT}. Bleed plus HCl absorbed.'),'WET','WET'),
          edge('IA-VS-OFF','EVAP_ACID_VS','ALK_SCRUBBER','G',['mass'],'scrubbed vent to the house acid-gas header',rate(up['offgas_kg_d'],'kg/d',f"{VT}. {up['y_out_ppm']} ppmv HCl."),'WET','GAS'),
          edge('SF-EVAP_ACID_VS','SOL_ARK_60K','EVAP_ACID_VS','E',['elec'],'480 V AC',rate(vs['pump_kW'],'kW',f'{VT}. Feed equal to continuous_kw.'),'ELEC','WET','tray'),
          edge('SQ-EVAP_ACID_VS','EVAP_ACID_VS','HEAT_SINK','E',['energy'],'electrical input leaving as heat',rate(vs['pump_kW'],'kW',f'{VT}. Pump work leaves as heat.'),'WET','GEO','tray')]
    vn[1]['params'] = {'NaOH_mol_d': round(up['naoh_mol_d'], 9)}
    for e in vn:
        if e['stream_id'] in E: E[e['stream_id']].update({k: e[k] for k in ('rate','from_unit_id','to_unit_id','carries')}); E[e['stream_id']].setdefault('params',{}).update(e.get('params') or {})
        else: g['edges'].append(e); E[e['stream_id']] = e
    E['IA-EVAP_ACID-COND']['rate'] = rate(s['evap_acid']['water_kg_d'] - up['vent_kg_d'],'kg/d',f'{TAG}. Water evaporated, condensed and returned to BMED_ACID, less the vent (X-PAR-10).')
    # BMED_BASE closes on its brine feed: out (EVAP_BASE feed + IA-BMED-02) = IA-BMED-04 + condensate
    E['IA-BMED-04']['rate'] = rate(s['evap_base']['feed_kg_d'] + E['IA-BMED-02']['rate']['value'] + up['naoh_soln_kg_d'] - s['evap_base']['water_kg_d'],'kg/d',f'{TAG}. Brine to BMED_BASE closing the stack balance with the condensate return.')
    # EW cells and rectifier
    rows = {r['cell']: r for r in json.loads(subprocess.run([sys.executable,'docs-authority/_ew_sizing.py'],cwd=ROOT,capture_output=True,text=True,check=True).stdout)['rows']}
    rect = json.loads(subprocess.run([sys.executable,'docs-authority/_rect_ew_sizing.py'],cwd=ROOT,capture_output=True,text=True,check=True).stdout)['total']
    V = DR.val(d,'ew_cell_voltage_V'); CE = DR.val(d,'ew_current_efficiency_design'); VD = DR.val(d,'ew_bus_drop_V')
    for c, v in s['ew'].items():
        if c == 'RECT_EW': continue
        n = N[c]; r = rows[c]
        if isinstance(n.get('continuous_kw'), dict): n['continuous_kw'] = rate(v['P_kW'],'kW',f"{TAG}. Cell DC at the electrode: {v['I_A']:.0f} A (Faraday, copper-equivalent, CE {CE}) x {V} V (USBM_CL_EW chloride EW).")
        if 'cell_voltage_V' in n['params']: n['params']['cell_current_A'] = round(v['I_A']); n['params']['cell_voltage_V'] = V
        sz = n['params'].get('sizing', {})
        sz.update({'size_mm': r['size_mm'], 'I_bounding_A': round(v['I_A']), 'cathodes': r['cathodes'], 'anodes': r['anodes'], 'j_A_m2': round(r['j_A_m2']),
                   'V_liq_m3': round(r['V_liq_m3'],3), 'P_dc_kW': round(v['P_kW'],2), 'status': 'study', 'source': 'AQS-DUTY-051'})
        n['params']['sizing'] = sz
        E[f'IA-DC-{c}']['rate'] = rate(v['P_bus_kW'],'kW',f'{TAG}. Channel DC at {V} V cell + {VD} V bus drop, bounding current.')
        E[f'IA-EWQ-{c}']['rate'] = rate(v['P_bus_kW']-sum(e['rate']['value'] for e in g['edges'] if e['from_unit_id']==c and 'thermal' in (e.get('layers') or [])),'kW',f'{TAG}. DC input less the HX-8 thermal draw.')
    R = s['ew']['RECT_EW']
    N['RECT_EW']['continuous_kw'] = rate(R['P_ac_kW'],'kW',f"{TAG}. AC input at the bounding current; DC {R['P_dc_kW']:.2f} kW to cells, {R['loss_kW']:.2f} kW conversion loss at efficiency {DR.val(d,'rect_efficiency')}.")
    N['RECT_EW']['params'].update({'rated_A': rect['rated_A'], 'nameplate_kw_dc': rect['rated_kW']})
    N['RECT_EW']['notes'] = f"{TAG}; AQS-ELEC-004. Nine-channel EW rectifier, {rect['rated_A']} A, {rect['rated_kW']:.0f} kW DC nameplate at 6 V."
    E['S17-EW']['rate'] = rate(R['P_ac_kW'],'kW',f'{TAG}. RECT-EW AC input.')
    E['IA-RECT-EW-LOSS']['rate'] = rate(R['loss_kW'],'kW',f'{TAG}. Rectifier conversion loss.')
    # SOL_ARK bus: PV average carries the change
    delta = bus_load(g) - before
    pv = E['IA-PV-01']['rate']['value'] + delta
    E['IA-PV-01']['rate']['value'] = round(pv,4)
    N['PV_ARRAY']['continuous_kw']['value'] = round(pv,4)
    open(GP,'w').write(json.dumps(g, indent=2))
    print(f'bus load change {delta:+.3f} kW; IA-PV-01 {pv:.3f} kW')

def power():
    g = json.load(open(GP)); N = {n['unit_id']: n for n in g['nodes']}
    o = json.loads(subprocess.run([sys.executable,'docs-authority/_power_sizing.py'],cwd=ROOT,capture_output=True,text=True,check=True).stdout); p = o['bounding']; rf = o['roof']
    pv = N['PV_ARRAY']['params']; kwp = math.ceil(p['pv_kWp'])
    pv.update({'nameplate_kw': kwp, 'count': math.ceil(kwp/pv['module_kw']), 'area_m2': round(rf['array_m2']),
               'mounting': 'roof only (X-PAR-07); ground field removed',
               'roof': {'footprint_mm': [rf['W_mm'], rf['D_mm']], 'bays': [rf['bays_x'], rf['bays_y']], 'footprint_m2': rf['footprint_m2'],
                        'extension_m2': rf['added_m2'], 'roof_capacity_kWp': round(rf['pv_roof_kWp'], 1), 'perimeter_pathway_mm': rf['layout']['perimeter_mm'],
                        'arrays': rf['layout']['arrays'], 'extension_load_kW': round(rf['ext']['total_kW'], 2),
                        'roof_load_kPa': {k: round(v, 3) for k, v in rf['load'].items()},
                        'basis': 'flow_graph/param/solver.py roof_close (IFC 2021 1205.3, NFPA 1 11.12, IECC 2021, ASHRAE 62.1, ISO 16798-3, ASCE 7-22)'}})
    N['ZNBR2']['params'].update({'kW': math.ceil(p['store_kW']), 'kWh': math.ceil(p['store_kWh']), 'charge_kW': math.ceil(p['charge_kW']), 'discharge_kW': math.ceil(p['discharge_kW']),
        'charge_basis': f"D75 cloudy-day case: yield {p['cloudy_yield_frac']:.2f} x mean (NREL_PVWATTS8 hourly scaling; NREL_NSRDB distribution to verify, A-M-109); charge = PV peak on that day less direct load"})
    N['SOL_ARK_60K']['params'].update({'count': p['inverters'], 'kW': p['inv_kW'], 'dc_ac_ratio': DR.val(DR.load(), 'pv_dc_ac_ratio'),
        'interconnection': {'export_peak_kW': round(p['export_peak_kW'], 1), 'export_kWh_d_clear': round(p['export_kWh_d_clear']),
            'standards': 'IEEE 1547-2018 Cat. B / III, UL 1741 SB listed; NEC 2023 705.11 supply-side connection, 705.20 disconnect; ANSI C12.20 class 0.2 bidirectional meter', 'decision': 'D75'}})
    pv['oversize_factor'] = DR.val(DR.load(), 'pv_oversize_factor'); pv['balance_kWp'] = math.ceil(p['pv_base_kWp'])
    # X-PAR-07: extension hall load on the graph (unconditioned until the owner decides; A-M-104)
    kw = round(rf['ext']['total_kW'], 4); E = {x['stream_id']: x for x in g['edges']}
    cond = "conditioned" if DR.val(DR.load(), "ext_conditioned") else "unconditioned"
    note = (f"X-PAR-07 solver.roof_close: {cond} extension {rf['added_m2']:.0f} m2; lighting {rf['ext']['light_kW']:.2f} kW (IECC 2021 C405, 10 % lit), "
            f"ventilation {rf['ext']['vent_kW']:.2f} kW (ASHRAE 62.1-2019 air at COP per ASHRAE 90.1-2019 Table 6.8.1-2, ISO 16798-3 fans), envelope {rf['ext']['envelope_kW']:.2f} kW (IECC 2021 C402 roof and walls, NOAA DFW degree days).")
    if 'EXT_HALL' not in N:
        n = dict(unit_id='EXT_HALL', sector_id='ELEC_PV', presence='present', class_='building', tags=[], electrical_role='load', diagram_gap=None,
                 notes='Single-storey extension carrying the roof PV (X-PAR-07). Duty sheet docs-authority/duties/EXT_HALL.md.', enabled=True, modules=[], params={}, continuous_kw=None)
        n['class'] = n.pop('class_'); g['nodes'].append(n); N['EXT_HALL'] = n
    x = rf['ext']
    if x.get('mode'):
        note += (f" X-PAR-08: {x['mode']}-source heat pumps (ASHRAE 90.1-2019 Table 6.8.1-2), heating {x['Qh_kW']:.1f} kW and cooling {x['Qc_kW']:.1f} kW thermal average after"
                 f" internal gains {x['gains_kW']:.1f} kW and slab edge {x['slab_kW']:.2f} kW (IECC F-factor); loop pumping {x['pump_kW']:.2f} kW. Comparison: "
                 + '; '.join(f"{m} {c['footprint_m2']:.0f} m2, {c['ext_kW']:.2f} kW" for m, c in rf.get('compare', {}).items()) + '.')
        N['EXT_HALL'].setdefault('params', {})['hvac'] = {k: (round(v, 3) if isinstance(v, float) else v) for k, v in x.items()}
        if not x.get('bores'): N['GEO_GHEX'].get('params', {}).pop('hall_field', None)
        if x.get('bores'):
            N['GEO_GHEX'].setdefault('params', {})['hall_field'] = {'bores': x['bores'], 'depth_m': DR.val(DR.load(), 'gsh_bore_depth_m'), 'bore_m': round(x['bore_m']),
                'area_m2': x['bore_field_m2'], 'location': 'under the EXT_HALL slab', 'basis': 'KAVANAUGH2014 bore length per kW peak block load; X-PAR-08, A-M-112'}
    N['EXT_HALL']['continuous_kw'] = {'value': kw, 'unit': 'kW', 'status': 'study', 'note': note}
    N['EXT_HALL']['params'].update({'footprint_m2': rf['added_m2'], 'conditioned': bool(DR.val(DR.load(), 'ext_conditioned')), 'blocks': ['EXT_HALL_E', 'EXT_HALL_N'],
        'duty': f"In 0.000 kg/d, out 0.000 kg/d, {kw:.3f} kW. Sheet docs-authority/duties/EXT_HALL.md."})
    old = E['SF-EXT_HALL']['rate']['value'] if 'SF-EXT_HALL' in E else 0.0
    if 'SF-EXT_HALL' not in E:
        e = json.loads(json.dumps(E['SF-MFG_SHOP'])); e.update(stream_id='SF-EXT_HALL', to_unit_id='EXT_HALL', to_sector_id='ELEC_PV', notes='X-PAR-07 extension hall feed')
        g['edges'].append(e); E['SF-EXT_HALL'] = e
    E['SF-EXT_HALL']['rate'] = {'value': kw, 'unit': 'kW', 'status': 'study', 'note': 'Equals EXT_HALL continuous_kw (X-PAR-07).'}
    pv1 = E['IA-PV-01']['rate']; pv1['value'] = round(pv1['value'] + kw - old, 4)
    if 'X-PAR-07' not in pv1.get('note', ''): pv1['note'] = pv1.get('note', '') + f' X-PAR-07 extension hall: +{kw:.2f} kW.'
    open(GP,'w').write(json.dumps(g, indent=2))
    subprocess.run([sys.executable,'docs-authority/_collection_bus.py'],cwd=ROOT,capture_output=True,text=True,check=True)   # X-ELS-11 sections
    print(f"PV {kwp} kWp, storage {math.ceil(p['store_kW'])} kW / {math.ceil(p['store_kWh'])} kWh, inverters {p['inverters']} x 60 kW")

def relief():
    """Relief: pressurised nodes (design_kPa above the atmospheric study band) are sized by API 520
    (sizing.relief); the case inputs are read from params.relief_basis. Atmospheric nodes are marked:
    relief_mm is the older study figure and venting is an API 2000 case at unit task 07."""
    from .sizing import relief as RL
    from .refs import cite
    g = json.load(open(GP)); n_api = n_atm = 0
    for n in g['nodes']:
        p = n.get('params') or {}
        if 'relief_mm' not in p: continue
        rb = p.get('relief_basis')
        if isinstance(rb, dict) and 'P1_kPa_abs' in rb:
            W = rb.get('W_kg_h') or float(rb['case'].split('= ')[-1].split(' kg/h')[0])
            A = RL.gas_area_in2(W*2.20462, rb.get('k', 1.4), rb['P1_kPa_abs']/6.894757, rb['T_K']*1.8, rb.get('Z', 1.0), rb['M_kg_kmol'],
                                Kd=rb.get('Kd', 0.975), Kb=rb.get('Kb', 1.0), Kc=rb.get('Kc', 1.0))
            rb.update(W_kg_h=W, A_req_mm2=round(A*RL.IN2_TO_MM2, 2), bore_req_mm=round(RL.equiv_bore_mm(A), 2),
                      computed_by=f"flow_graph/param/sizing/relief.py gas_area_in2 ({cite('API520')})",
                      adequate=bool(p['relief_mm'] >= RL.equiv_bore_mm(A)))
            n_api += 1
        else:
            p['relief_basis'] = {'case': 'atmospheric', 'method': 'not an API 520 case; tank venting per API Std 2000 at unit task 07',
                                 'relief_mm_status': 'atmospheric; design pressure set by the vent stage (A-M-174)'}
            n_atm += 1
    open(GP, 'w').write(json.dumps(g, indent=2))
    print(f'API 520 sized {n_api}; atmospheric marked {n_atm}')

def vent():
    """X-PAR-03: API 2000 normal venting for every atmospheric node (relief_basis case 'atmospheric'), A-M-155. Pump-in/out = the node's
    daily liquid in/out volume moved in a TRANSFER_H window; thermal term on the envelope volume where one is sized; vent bore at the
    allowed open-vent dP = min(VENT_DP_PA, 25 % of design_kPa); DN 25 minimum."""
    from .sizing import vent as VT
    from .refs import cite
    from . import drivers as DV
    D = DV.load(); Y, C, TH, DPA = (D[k]['value'] for k in ('api2000_Y', 'api2000_C', 'vent_transfer_h', 'vent_dP_Pa'))
    DNS = (25, 32, 40, 50, 65, 80, 100, 125, 150, 200, 250, 300)
    g = json.load(open(GP)); n = 0; nv = 0; nh = 0; SG = D['atm_design_sg']['value']
    liq = lambda e: e['presence'] == 'present' and e.get('phase') == 'L' and (e['rate'] or {}).get('unit') == 'kg/d'
    for u in g['nodes']:
        p = u.get('params') or {}; rb = p.get('relief_basis')
        if not (isinstance(rb, dict) and rb.get('case') == 'atmospheric'): continue
        sz = (p.get('sizing') or {}).get('size_mm') or p.get('size_mm')
        V = sz[0]*sz[1]*sz[2]*1e-9 if sz and len(sz) >= 3 else 0.0; nv += bool(V)
        qi = sum(e['rate']['value'] or 0 for e in g['edges'] if e['to_unit_id'] == u['unit_id'] and liq(e))/1000/TH
        qo = sum(e['rate']['value'] or 0 for e in g['edges'] if e['from_unit_id'] == u['unit_id'] and liq(e))/1000/TH
        vo = VT.out_breathing_Nm3_h(V, qi, Y); vi = VT.in_breathing_Nm3_h(V, qo, C)
        dp = min(DPA, 0.25*(p.get('design_kPa') or 2)*1000); bore = VT.open_vent_bore_mm(max(vo, vi), dp)
        rb.update(method=f"API 2000 normal venting ({cite('API2000_2020')}), flow_graph/param/sizing/vent.py, A-M-155",
                  V_tk_m3=round(V, 3), pump_in_m3_h=round(qi, 4), pump_out_m3_h=round(qo, 4), out_breathing_Nm3_h=round(vo, 3),
                  in_breathing_Nm3_h=round(vi, 3), vent_dP_Pa=round(dp), vent_bore_req_mm=round(bore, 1), vent_DN=next(d for d in DNS if d >= bore),
                  thermal_term='envelope volume' if V else 'no sized volume: pump terms only')
        # A-M-174: design pressure from the actual cases, replacing the head-plus-10 study figure. Vapour space: the open-vent dP
        # is held to 25 % of design, so design >= 4 x vent dP; bottom of shell adds the full-height hydrostatic head at SG atm_design_sg.
        H = ((p.get('design') or {}).get('H_mm') or (sz[2] if sz and len(sz) >= 3 else 0))/1000
        P_vap = 4*dp/1000; P_liq = SG*1000*9.80665*H/1000
        p['design_kPa'] = math.ceil((P_vap + P_liq)*2)/2
        rb['relief_mm_status'] = 'atmospheric; no relief orifice, open vent per API 2000'
        rb['design_case'] = (f"vapour {P_vap:.1f} kPa (4 x vent dP) + hydrostatic {P_liq:.1f} kPa ({H:.2f} m full at SG {SG}) = {p['design_kPa']} kPa g (A-M-174)" if H else
                             f"vapour {P_vap:.1f} kPa (4 x vent dP) only = {p['design_kPa']} kPa g; hydrostatic case added when the unit is sized (A-M-174)")
        nh += bool(H)
        n += 1
    open(GP, 'w').write(json.dumps(g, indent=2))
    print(f'API 2000 vents sized {n} ({nv} with a volume); design pressure from cases on {n} ({nh} with a hydrostatic case)')

if __name__ == '__main__':
    {'process': process, 'power': power, 'relief': relief, 'vent': vent}[sys.argv[1] if len(sys.argv) > 1 else 'process']()

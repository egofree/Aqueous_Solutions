"""X-PAR-04 graph writer. Writes solver values into flow_graph/plant_flow_graph.json:
acid-loop decision (BMED at 2 M, EVAP_ACID and EVAP_BASE to 20 wt%), BMED energy, EW cell and
DC bus power, RECT_EW, and the SOL_ARK bus balance on IA-PV-01. Idempotent.
Stage 'power' (after the load list, one line and AQS-ELEC-007 are regenerated) writes PV, storage
and inverter sizes from docs-authority/_power_sizing.py.
Run: python3 -m flow_graph.param.write_graph [process|power]"""
import json, math, os, subprocess, sys
from . import solver, drivers as DR, site as SITE
ROOT = solver.ROOT; GP = os.path.join(ROOT,'flow_graph/plant_flow_graph.json')
TAG = 'X-PAR acid-loop decision (AQS-PAR-001 \u00a73)'
ELEC_IN = ('S17-BMED','S17-EW','SF-EVAP_ACID','SF-EVAP_BASE','SF-EVAP_ACID_VS','SF-GEO_HP_CLOSED_LOOP')

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
    mk = [edge('IA-NAOH-MU','NORTH_DOCK','EVAP_BASE','S',['mass'],'purchased NaOH flake make-up',rate(nb['makeup_kg_d'],'kg/d',f"{NT}. Demand {nb['ppt_mol']+nb['digest_mol']:.0f} mol/d less BMED {nb['bmed_mol']:.0f} mol/d; worst case, no credit for sodium returned in the silicate liquor."),'DOCK','DIGESTER'),
          edge('IA-NA-PURGE','LEACH_CSTR_1','NORTH_DOCK','L',['mass'],'sodium salt purge equal to the make-up mass',rate(nb['makeup_kg_d'],'kg/d',f'{NT}. Sodium brought in on IA-NAOH-MU leaves the loop as salt; mass equal to the make-up (study).'),'DIGESTER','DOCK')]
    for e in mk:
        if e['stream_id'] in E: E[e['stream_id']]['rate'] = e['rate']
        else: g['edges'].append(e); E[e['stream_id']] = e
    # evaporators
    for side, key, src, prods, sa in (('ACID','evap_acid','BMED_ACID',('IA-ACID-01',),'HCl'),('BASE','evap_base','BMED_BASE',solver.BASE_DEMAND,'NaOH')):
        u = f'EVAP_{side}'; v = s[key]; w = DR.val(d,'acid_conc_design_wt' if side=='ACID' else 'base_conc_design_wt')
        note = (f"{TAG}. MVR evaporator, {sa} from 2 M ({DR.val(d,'bmed_product_wt_'+side.lower())*100:.2f} wt%) to {w*100:.0f} wt%"
                + (f" (below the HCl azeotrope {DR.val(d,'hcl_azeotrope_wt')*100:.1f} wt%, PERRY9_HCL)" if side=='ACID' else '')
                + f"; water off {v['water_kg_d']:.1f} kg/d x {v['design']['kWh_per_t']} kWh/t (in-house MVR design X-MFG-30, AQS-DUTY-060: blower {v['design']['comp_elec_kW']:.3f} kW, recirculation {v['design']['pump_kW']:.3f} kW, trim {v['design']['trim_kW']:.3f} kW) = {v['kW']:.2f} kW. Study.")
        node = N.get(u) or {'unit_id': u, 'sector_id': 'DIGESTER', 'presence': 'present', 'class': 'evaporator', 'tags': [], 'electrical_role': 'load',
                            'diagram_gap': None, 'enabled': True, 'modules': [], 'params': {}}
        node['notes'] = f'{sa} concentrator after {src} ({TAG}). Wetted parts per ULLMANN_HCL (impregnated graphite or fluoropolymer-lined; study).' if side=='ACID' else f'{sa} concentrator after {src} ({TAG}). Nickel or fluoropolymer-lined wetted parts (study).'
        node['continuous_kw'] = rate(v['kW'],'kW',note)
        node['params'].update({'presence':'present','water_off_kg_d':round(v['water_kg_d'],2),'feed_wt':DR.val(d,'bmed_product_wt_'+side.lower()),'product_wt':w,
                               'mvr_kWh_per_t':v['design']['kWh_per_t'],'size_mm':node['params'].get('size_mm',[1200,900,2000]),'doc':'AQS-PAR-001, AQS-DUTY-060'})
        node['params'].setdefault('size_note','L x W x H mm, set by flow_graph/param/evap_design.py (X-MFG-30)')
        if u not in N: g['nodes'].append(node); N[u] = node
        new = [edge(f'IA-{u}-FEED', src, u, 'L', ['mass'], f'{sa} 2 M from BMED', rate(v['feed_kg_d'],'kg/d',f'{TAG}. {v["solute_kg_d"]:.2f} kg/d {sa} / {DR.val(d,"bmed_product_wt_"+side.lower())}.'),'DIGESTER','DIGESTER'),
               edge(f'IA-{u}-COND', u, src, 'L', ['mass'], 'evaporator condensate return (BMED water make-up)', rate(v['water_kg_d'],'kg/d',f'{TAG}. Water evaporated, condensed and returned to {src}.'),'DIGESTER','DIGESTER'),
               edge(f'SF-{u}', 'SOL_ARK_60K', u, 'E', ['elec'], '480 V AC', rate(v['kW'],'kW',f'{TAG}. 480 V feed equal to {u} continuous_kw.'),'ELEC','DIGESTER','tray'),
               edge(f'SQ-{u}', u, 'HEAT_SINK', 'E', ['energy'], 'electrical input leaving as heat', rate(v['kW'],'kW',f'{TAG}. Compressor work leaves as heat (A-M-086).'),'DIGESTER','GEO','tray')]
        for e in new:
            if e['stream_id'] in E: E[e['stream_id']].update({k: e[k] for k in ('rate','from_unit_id','to_unit_id','carries')})
            else: g['edges'].append(e); E[e['stream_id']] = e
        for p in prods:
            # R8-style presence gate: IA-ACEX-NAOH was retired with the ACEX train re-homes; only re-point
            # product edges that exist (the graph no longer carries every BASE_DEMAND member).
            if p in E: E[p]['from_unit_id'] = u; E[p]['from_sector_id'] = 'DIGESTER'
    # X-PAR-10 vent scrubber on the EVAP_ACID column vent (owner decision 2026-10-15; AQS-DUTY-061)
    vs = s['vs']; up = vs['upset']; VT = f'{TAG}; X-PAR-10 vent scrubber (AQS-DUTY-061)'
    nd = N.get('EVAP_ACID_VS') or {'unit_id': 'EVAP_ACID_VS', 'sector_id': 'DIGESTER', 'presence': 'present', 'class': 'scrubber', 'tags': [], 'electrical_role': 'load',
                                    'diagram_gap': None, 'enabled': True, 'modules': [], 'params': {}}
    nd['notes'] = 'Packed PVC alkali scrubber on the EVAP_ACID column vent; NaOH bleed from BMED_BASE; spent liquor to BMED_ACID. Duty sheet docs-authority/duties/EVAP_ACID_VS.md.'
    nd['continuous_kw'] = rate(vs['pump_kW'],'kW',f"{VT}. Sump recirculation pump {up['recirc_m3_h']*1000:.0f} L/h at the minimum wetting rate (PERRY9_ABS), 10 m head, 40 % efficiency (study).")
    nd['params'].update({'presence':'present','DN':vs['DN'],'packed_mm':vs['packed_mm'],'height_mm':vs['height_mm'],'sump_L':vs['sump_L'],'material':vs['material'],
                         'y_in_ppm_design':round(up['y_in_ppm'],1),'y_out_ppm':up['y_out_ppm'],'design_case':'upset: column bypassed (A-M-111)',
                         'size_mm':[400, 400, vs['height_mm']],'size_note':'L x W x H mm, set by flow_graph/param/vent_scrubber.py (X-PAR-10)','doc':'AQS-DUTY-061'})
    if 'EVAP_ACID_VS' not in N: g['nodes'].append(nd); N['EVAP_ACID_VS'] = nd
    vn = [edge('IA-EVAP_ACID-VENT','EVAP_ACID','EVAP_ACID_VS','G',['mass'],'column vent: non-condensables, water vapour, trace HCl',rate(up['vent_kg_d'],'kg/d',f"{VT}. Air from the feed (WEISS1970) saturated at the vent condenser; design case {up['y_in_ppm']:.0f} ppmv HCl."),'DIGESTER','DIGESTER'),
          edge('IA-VS-NAOH','BMED_BASE','EVAP_ACID_VS','L',['mass'],'NaOH 2 M bleed',rate(up['naoh_soln_kg_d'],'kg/d',f"{VT}. {vs['upset']['naoh_mol_d']*1000:.3f} mmol/d = {DR.val(d,'vs_naoh_excess')} x HCl absorbed."),'DIGESTER','DIGESTER'),
          edge('IA-VS-SPENT','EVAP_ACID_VS','BMED_ACID','L',['mass'],'spent scrub liquor (NaCl in NaOH) to the BMED brine',rate(up['spent_kg_d'],'kg/d',f'{VT}. Bleed plus HCl absorbed.'),'DIGESTER','DIGESTER'),
          edge('IA-VS-OFF','EVAP_ACID_VS','ALK_SCRUBBER','G',['mass'],'scrubbed vent to the house acid-gas header',rate(up['offgas_kg_d'],'kg/d',f"{VT}. {up['y_out_ppm']} ppmv HCl."),'DIGESTER','GAS'),
          edge('SF-EVAP_ACID_VS','SOL_ARK_60K','EVAP_ACID_VS','E',['elec'],'480 V AC',rate(vs['pump_kW'],'kW',f'{VT}. Feed equal to continuous_kw.'),'ELEC','DIGESTER','tray'),
          edge('SQ-EVAP_ACID_VS','EVAP_ACID_VS','HEAT_SINK','E',['energy'],'electrical input leaving as heat',rate(vs['pump_kW'],'kW',f'{VT}. Pump work leaves as heat.'),'DIGESTER','GEO','tray')]
    vn[1]['params'] = {'NaOH_mol_d': round(up['naoh_mol_d'], 9)}
    for e in vn:
        if e['stream_id'] in E: E[e['stream_id']].update({k: e[k] for k in ('rate','from_unit_id','to_unit_id','carries')}); E[e['stream_id']].setdefault('params',{}).update(e.get('params') or {})
        else: g['edges'].append(e); E[e['stream_id']] = e
    E['IA-EVAP_ACID-COND']['rate'] = rate(s['evap_acid']['water_kg_d'] - up['vent_kg_d'],'kg/d',f'{TAG}. Water evaporated, condensed and returned to BMED_ACID, less the vent (X-PAR-10).')
    # BMED_BASE closes on its brine feed: out (EVAP_BASE feed + IA-BMED-02) = IA-BMED-04 + condensate
    E['IA-BMED-04']['rate'] = rate(s['evap_base']['feed_kg_d'] + E['IA-BMED-02']['rate']['value'] + up['naoh_soln_kg_d'] - s['evap_base']['water_kg_d'],'kg/d',f'{TAG}. Brine to BMED_BASE closing the stack balance with the condensate return.')
    # EW cells and rectifier (R10b: RECT_EW remapped to the live RECTIFIER; the DC feeds IA-DC-EW_n are restored on it
    # by o2_close.tf, A-M-255; the IA-EWQ-* cell-heat and IA-RECT-EW-LOSS edges died with HEAT_SINK in Rev AC and are
    # guarded; the node continuous_kw stays the 12 kW A-M-231 basis so the EW DC load is counted once, behind the
    # AQS-ELEC-004 bounding AC row in _power_sizing)
    rows = {r['cell']: r for r in json.loads(subprocess.run([sys.executable,'docs-authority/_ew_sizing.py'],cwd=ROOT,capture_output=True,text=True,check=True).stdout)['rows']}
    rect = json.loads(subprocess.run([sys.executable,'docs-authority/_rect_ew_sizing.py'],cwd=ROOT,capture_output=True,text=True,check=True).stdout)['total']
    V = DR.val(d,'ew_cell_voltage_V'); CE = DR.val(d,'ew_current_efficiency_design'); VD = DR.val(d,'ew_bus_drop_V')
    for c, v in s['ew'].items():
        if c == 'RECT_EW': continue
        n = N[c]; r = rows[c]
        if isinstance(n.get('continuous_kw'), dict): n['continuous_kw'] = rate(v['P_kW'],'kW',f"{TAG}. Cell DC at the electrode: {v['I_A']:.0f} A (Faraday, copper-equivalent, CE {CE}) x {V} V (USBM_CL_EW chloride EW).")
        if 'cell_voltage_V' in n['params']: n['params']['cell_current_A'] = round(v['I_A']); n['params']['cell_voltage_V'] = V
        # D9 ownership rule (documented, no change): the EW plate GEOMETRY calculator (docs-authority/_ew_sizing.py, AQS-EW-MOD-001
        # constants) owns the geometry; it reads only the harvest edges from the graph. The params.sizing stamped here (size_mm,
        # cathodes, anodes, j, V_liq, P_dc) are OUTPUTS of that calculator onto the graph - never inputs back into it - so the
        # graph -> calculator -> graph round trip cannot self-feed. write_graph.process is the single writer of IA-DC-EW_n;
        # o2_close.tf only fills gaps with the same live solver values.
        sz = n['params'].get('sizing', {})
        sz.update({'size_mm': r['size_mm'], 'I_bounding_A': round(v['I_A']), 'cathodes': r['cathodes'], 'anodes': r['anodes'], 'j_A_m2': round(r['j_A_m2']),
                   'V_liq_m3': round(r['V_liq_m3'],3), 'P_dc_kW': round(v['P_kW'],2), 'status': 'study', 'source': 'AQS-DUTY-051'})
        n['params']['sizing'] = sz
        if f'IA-DC-{c}' in E: E[f'IA-DC-{c}']['rate'] = rate(v['P_bus_kW'],'kW',f'{TAG}. Channel DC at {V} V cell + {VD} V bus drop, bounding current.')
        if f'IA-EWQ-{c}' in E: E[f'IA-EWQ-{c}']['rate'] = rate(v['P_bus_kW']-sum(e['rate']['value'] for e in g['edges'] if e['from_unit_id']==c and 'thermal' in (e.get('layers') or [])),'kW',f'{TAG}. DC input less the HX-8 thermal draw.')
    R = s['ew']['RECT_EW']; n_rect = N.get('RECT_EW') or N.get('RECTIFIER')   # Rev AC renamed the EW rectifier RECTIFIER
    if n_rect is not None:
        n_rect['params'].update({'rated_A': rect['rated_A'], 'nameplate_kw_dc': rect['rated_kW'], 'rect_ac_input_kW': round(R['P_ac_kW'], 3), 'rect_loss_kW': round(R['loss_kW'], 3),
            'rect_basis': f"{TAG}/R10b: nine-channel EW rectifier {rect['rated_A']} A, {rect['rated_kW']:.0f} kW DC nameplate at 6 V; bounding AC input {R['P_ac_kW']:.2f} kW (AQS-ELEC-004). "
                          "Node continuous_kw stays the 12 kW A-M-231 basis and S17 equals it: the EW DC load is counted once, behind the AQS-ELEC-004 bounding AC row in _power_sizing (A-M-255)."})
        n_rect['notes'] = f"{TAG}; AQS-ELEC-004. Nine-channel EW rectifier, {rect['rated_A']} A, {rect['rated_kW']:.0f} kW DC nameplate at 6 V (Rev AC node RECTIFIER; RECT_EW remapped R10b)."
    if 'S17-EW' in E: E['S17-EW']['rate'] = rate(R['P_ac_kW'],'kW',f'{TAG}. RECT-EW AC input.')
    if 'IA-RECT-EW-LOSS' in E: E['IA-RECT-EW-LOSS']['rate'] = rate(R['loss_kW'],'kW',f'{TAG}. Rectifier conversion loss.')
    # X-ELS-02 load-basis provenance (A-M-275): every node continuous_kw either cites its calculation or is
    # listed as an explicit study share in the load list. This block aligns node stamps to the owning
    # calculation: driver-keyed nameplates, the calculated SF-* feeds (X-MFG-31 reactor design, X-SAN-01
    # sanitation, X-MFG-37 shop tool list) and the AQS-DUTY-050 agitator. Node kW changes only where the
    # calculation says so (MFG_SHOP 12 -> shop machine-tool average with the four metal tools split to their
    # own stamps (AQS-MFG-010 rev C), LEACH_CSTR_1 2 -> motor, GLASS_DIGEST 1.5 ->
    # agitator, MEOH_SYNTH 0.5 -> feed preheat); feed edges follow their nodes so the bus balance rides along.
    LTAG = 'X-ELS-02 load-basis (A-M-275)'
    def _stamp(u, kw, note, feed=True):
        n = N.get(u)
        if n is None: return
        n['continuous_kw'] = rate(kw,'kW',note)
        if feed and f'SF-{u}' in E: E[f'SF-{u}']['rate'] = rate(kw,'kW',f'{LTAG}. Feed equal to {u} continuous_kw.')
    mf = json.loads(subprocess.run([sys.executable,'docs-authority/_mfg_tools.py'],cwd=ROOT,capture_output=True,text=True,check=True).stdout)
    _stamp('MFG_SHOP', round(mf['shop_avg'],4),
           f"X-MFG-37 (A-M-177): AQS-MFG-010 rev C shop machine-tool list, one 8 h shift; {mf['shop_avg']*24:.1f} kWh/d / 24 h; "
           f"shop connected {mf['shop_connected']:.1f} kW (roster connected {mf['connected']:.1f} kW, coincident peak {mf['peak']} kW frames MCC-1); "
           f"rev C metering split moves the four metal tools to their own stamps (X-ELS-02: node was the 12 kW REQ-MFG-TOTAL-CONT study share).")
    for mt in mf['metal']:   # X-ELS-02 rev C: per-tool stamps at the AQS-MFG-010 physics rows
        u, a, kwh, npk = mt['unit'], mt['avg_kw'], mt['kwh_d'], mt['nameplate_kw']
        nt = N.get(u)
        if nt is not None: nt['electrical_role'] = nt.get('electrical_role') or 'load'
        _stamp(u, round(a,4),
               f"X-MFG-37 (A-M-177): AQS-MFG-010 rev C per-tool stamp, in-house physics from graph throughputs; {kwh:.1f} kWh/d / 24 h; "
               f"batch nameplate {npk:.1f} kW (rev B metered this tool inside the MFG_SHOP aggregate; total roster demand unchanged).")
        sid = f'SF-{u}'
        if sid not in E:
            e = json.loads(json.dumps(E['SF-MFG_SHOP']))
            e.update(stream_id=sid, to_unit_id=u, to_sector_id=(N.get(u) or {}).get('sector_id') or 'MFG',
                     notes='X-ELS-02 rev C: per-tool feeder for the AQS-MFG-010 rev C metering split')
            g['edges'].append(e); E[sid] = e
        E[sid]['rate'] = rate(round(a,4),'kW',f'{LTAG}. Feed equal to {u} continuous_kw.')
    lc = 'DIGESTER.metals-leach-train.brine-loop.LEACH_CSTR_1.'
    _shaft = DR.val(d,lc+'imp_Np')*DR.val(d,lc+'liquor_rho_kg_m3')*(DR.val(d,lc+'imp_N_rpm')/60)**3*DR.val(d,lc+'imp_D_m')**5
    _stamp('LEACH_CSTR_1', DR.val(d,lc+'motor_kW'),
           f"X-ELS-02: agitator PBT D{DR.val(d,lc+'imp_D_m')*1000:.0f} at {DR.val(d,lc+'imp_N_rpm')} rpm, {_shaft:.0f} W shaft "
           f"(Np x rho x N^3 x D^5) -> {DR.val(d,lc+'motor_kW')} kW motor (drivers key motor_kW; AQS-DUTY-050 Rev B); "
           f"leach heat is Q3 via HX-5, not electric (was the 2 kW AC parasitics share).")
    for u, mod in (('GLASS_DIGEST','agitator motor'), ('MEOH_SYNTH','feed preheat, no interchanger credit'), ('OIL_PYRO','retort heat / heater efficiency'), ('MEOH_FERM','losses and feed heat')):
        f = E.get(f'SF-{u}')
        if f is not None and isinstance(f['rate'].get('value'),(int,float)):
            _stamp(u, f['rate']['value'],
                   f"X-ELS-02: node aligned to its calculated SF-{u} feed ({mod}); sizing module flow_graph/param/reactor_design.py (X-MFG-31, AQS-DUTY-062). Feed basis: {f['rate'].get('note') or 'X-MFG-31'}.")
    f = E.get('SF-BLACK_DIGEST')
    if f is not None and isinstance(f['rate'].get('value'),(int,float)):
        _stamp('BLACK_DIGEST', f['rate']['value'],
               f"X-ELS-02: node aligned to its calculated SF-BLACK_DIGEST feed; sizing module flow_graph/param/sanitation.py (X-SAN-01, AQS-DUTY-063). Feed basis: {f['rate'].get('note') or 'X-SAN-01'}.")
    _stamp('WS_PEROX', round(12.31*2.5/1000,4),
           'X-ELS-10 (AQS-DSN-OX-001): peroxide electrolytic cell 12.31 A x 2.5 V = 0.0308 kW from the S32 duty; DC behind the RECTIFIER AC sum.',
           feed=False)
    if n_rect is not None and isinstance(n_rect.get('continuous_kw'), dict):
        n_rect['continuous_kw']['note'] = (f"A-M-231 (AQS-NOTE-PV-REBASE Rev A section 8): 12 kW 48 V rail and auxiliary basis (AQS-PWR-001). The nine-channel EW DC load is counted once "
                                           f"behind the AQS-ELEC-004 bounding AC row in _power_sizing (params.rect_ac_input_kW {R['P_ac_kW']:.2f} kW; A-M-255); S17 equals this node value.")
    for u in ('IND_MELT','RF_HEAT','VAC_IND'):   # R11 foundry bare ints -> rated dicts, value per A-M-232 (face value, unchanged)
        n = N.get(u)
        if n is not None and not isinstance(n.get('continuous_kw'), dict):
            n['continuous_kw'] = rate(float(n['continuous_kw']),'kW',
                f"study share - basis pending: AQS-SIZE-FOUNDRY batch nameplate carried flat at face value (A-M-232); calculated duty-cycle averages in docs-authority/sizing/FOUNDRY_LINE.md "
                f"(IND_MELT 0.298 kW avg) are held for the logged batch schedule (X-MFG-37 trial class). X-ELS-02.")
    x_els_residuals(g, N, E, d)   # X-ELS-02 rev C: the 13 load-list residuals get calculated/cited bases (A-M-301)
    # X-ELS-02 (A-M-317): the source-loop circulator is an electric load at its AQS-DUTY-076 pump draw,
    # stamped here (read from sizing_geo_loop's params.design, which the graph already carries) so the bus
    # rebalance below absorbs it; it rides the S44 lift dispatch (AQS-DUTY-010: lift only on the Q4 deficit)
    # and is counted on the same bounding winter case as the GEO_HP lift itself (A-M-231 demand rule).
    p_cl = N.get('GEO_HP_CLOSED_LOOP')
    pw = ((p_cl.get('params') or {}).get('design') or {}).get('pump_W') if p_cl else None
    if p_cl is not None and isinstance(pw,(int,float)) and pw > 0:
        p_cl['electrical_role'] = p_cl.get('electrical_role') or 'load'
        p_cl['continuous_kw'] = rate(pw/1000.0, 'kW',
            f"AQS-DUTY-076 source-loop circulator: {pw:.1f} W pump work (rho x g x Q x H / eta) at the GHEX-ceiling loop flow "
            f"against {((p_cl.get('params') or {}).get('design') or {}).get('head_m')} m head (sizing_geo_loop design block; drivers "
            f"GEO.geo-loop loop_head_m / pump eff, registered); runs with the S44 lift dispatch and is counted on the bounding "
            f"winter case with it (AQS-DUTY-010, A-M-231, A-M-317).")
        if 'SF-GEO_HP_CLOSED_LOOP' not in E:   # bus-fed like the EVAP_ACID_VS sump pump (same writer pattern)
            se = edge('SF-GEO_HP_CLOSED_LOOP','SOL_ARK_60K','GEO_HP_CLOSED_LOOP','E',['elec'],'480 V AC',
                      rate(pw/1000.0,'kW',f'{LTAG}. Feed equal to GEO_HP_CLOSED_LOOP continuous_kw (A-M-317).'),
                      'ELEC','GEO','tray')
            g['edges'].append(se); E['SF-GEO_HP_CLOSED_LOOP'] = se
        E['SF-GEO_HP_CLOSED_LOOP']['rate']['value'] = round(pw/1000.0, 4)
    # SOL_ARK bus: PV average carries the change
    delta = bus_load(g) - before
    pv = E['IA-PV-01']['rate']['value'] + delta
    E['IA-PV-01']['rate']['value'] = round(pv,4)
    N['PV_ARRAY']['continuous_kw']['value'] = round(pv,4)
    open(GP,'w').write(json.dumps(g, indent=2))
    print(f'bus load change {delta:+.3f} kW; IA-PV-01 {pv:.3f} kW')

def x_els_residuals(g, N, E, d):
    """X-ELS-02 rev C (A-M-301): the load-list residual rows get calculated or cited bases so the load list
    carries no 'basis pending' row beyond the owner requirement locks (FUEL_CELL, MEOH_FC). Single writer of
    these node stamps; the load list classifies from the note tokens."""
    v = lambda k: DR.val(d, k)
    RT = 'X-ELS-02 load-basis (A-M-301)'

    def _st(u, kw, note, design=None):
        n = N.get(u)
        if n is None:
            return
        n['continuous_kw'] = rate(kw, 'kW', f'{note} | {RT}.')
        if design is not None:
            n['params']['equipment'] = design
        f = E.get(f'SF-{u}')
        if f is not None and 'elec' in (f.get('layers') or []):
            f['rate'] = rate(kw, 'kW', f'Feed equal to {u} continuous_kw. | {RT}.')

    # 1) foundry duty-cycle wiring at the X-MFG-37 trial basis (A-M-177 method): the flat A-M-232 nameplates
    #    become the calculated duty-cycle averages; the connected kW ride in params (batch schedule unchanged)
    from . import foundry_poly as FX
    s = FX.solve(g)
    n = N['IND_MELT']
    n['continuous_kw'] = rate(round(s['e_melt'] / 24, 4), 'kW',
        f"X-MFG-37 trial basis (A-M-177 melt energies, AQS-DUTY-072): {s['e_melt']:.2f} kWh/d over 24 h at "
        f"{s['heats']} heats/d of the {s['charge']:.0f} kg crucible; peak {s['kw_peak']:.1f} kW, connected 25 kW "
        f"(A-M-232 face value kept as installed capacity; the load list carries the duty-cycle average). X-ELS-02.")
    n['params']['duty_cycle'] = dict(avg_kW=round(s['e_melt'] / 24, 4), peak_kW=s['kw_peak'], connected_kW=25.0,
                                     kWh_d=round(s['e_melt'], 3), heats_d=s['heats'], basis='X-MFG-37 logged batch schedule class')
    if 'SF-IND_MELT' in E:
        E['SF-IND_MELT']['rate'] = rate(round(s['e_melt'] / 24, 4), 'kW', 'Feed equal to IND_MELT continuous_kw. | X-ELS-02.')
    for u, conn, why in (('VAC_IND', 15.0, 'N+1 diverse melt path: standby-zero on the design day (A-M-283); Ti Kroll train '
                                              'feed now dock-supplied, duty-cycle wiring at the X-MFG-37 trial class'),
                         ('RF_HEAT', 5.0, 'preheat/sinter N+1 alternate: standby-zero on the design day (A-M-283); duty-cycle '
                                          'wiring at the X-MFG-37 trial class')):
        n = N.get(u)
        if n is not None:
            n['continuous_kw'] = rate(0.0, 'kW', f'X-MFG-37 trial basis (AQS-DUTY-072): {why}. X-ELS-02.')
            n['params']['duty_cycle'] = dict(avg_kW=0.0, connected_kW=conn,
                                             basis='X-MFG-37 logged batch schedule class; standby-zero per A-M-283')
            f = E.get(f'SF-{u}')
            if f is not None and 'elec' in (f.get('layers') or []):
                f['rate'] = rate(0.0, 'kW', f'Feed equal to {u} continuous_kw (standby-zero). | X-ELS-02.')

    # 2) HABITATION: the 3 kW study share decomposed per AQS-HAB-002 (calculated equipment list); the driver
    #    crit_HABITATION_kW stays the NFPA 110 critical-capacity lock, separate from the connected load
    hab = [CDRA_CO2, VENT, LIGHT, PUMPS, GALLEY, FRIDGE, MEDICAL, ELEC_COMM, HOTW] = [
        ('CDRA CO2 removal: 5A zeolite bed regen heaters + valves (X-RED-06, NASA_CDRA2015 class)', 0.75),
        ('ventilation fans: 22 L/s at SFP 750 W/(m3/s) (ASHRAE621_2019 rates, ISO16798_3 SFP3)', 0.017),
        ('lighting: 40 m2 x 8.8 W/m2 x 10 % lit (IECC2021_C405 allowance)', 0.035),
        ('water pressure + grey lift pumps (shower 6 L/min at 2 bar class, AQS-HAB-001)', 0.03),
        ('galley: induction 2 kW x 0.5 h/d + microwave + kettle = 1.4 kWh/d', 0.058),
        ('medical fridge/freezer + pharmacy (AQS-HAB-001 medical room)', 0.08),
        ('medical equipment duty share', 0.05),
        ('comms, electronics, controls at the hab panels', 0.05),
        ('wash-water heating: 60 kg/d x 30 K x 4.18 kJ/kg K', 0.087)]
    hab_kw = round(sum(x[1] for x in hab), 4)
    _st('HABITATION', hab_kw,
        f"AQS-HAB-002 equipment list: {len(hab)} line items sum {hab_kw:.3f} kW calculated (CDRA 0.75 kW dominates, "
        f"NASA_CDRA2015; ventilation ASHRAE621_2019/ISO16798_3; lighting IECC2021_C405; fixtures AQS-HAB-001 rev B). "
        f"Separately, the driver key ELEC.generation-train.BACKUP_GEN.crit_HABITATION_kW {v('ELEC.generation-train.BACKUP_GEN.crit_HABITATION_kW'):.1f} kW stays the "
        f"NFPA 110 critical-capacity lock for the backup sizing - not this connected load.",
        design=[dict(item=i, kW=round(w, 4)) for i, w in hab] + [
            dict(item='total connected (calculated)', kW=hab_kw),
            dict(item='critical-capacity lock (drivers, NFPA 110)', kW=v('ELEC.generation-train.BACKUP_GEN.crit_HABITATION_kW'))])

    # 3) WAFER_FAB + WET_BENCH: tool lists from AQS-EQP-FAB-001 (litho now on its own real tools, A-M-287)
    cp_si, L_si, T_melt = 0.9, 1790.0, 1414.0                      # kJ/kg K, kJ/kg (CRC_SI)
    cz = v('FAB.wafer-line-train.cz_charge_kg') * (cp_si * (T_melt - 25) + L_si) / 3600   # kWh per pull
    camp = v('FAB.wafer-line-train.campaign_d')
    fab = [('CZ puller: charge heat-up over the 7 d campaign + 4 h hot hold', (cz + 0.3 * 4) / camp),
           ('ingot cool/anneal station: N2 circulator duty share', 0.02),
           ('crop/grind/edge tools at 5 starts/d', 0.04),
           ('FAB_TOOL dry row parasitics (ox, RTA, metal, probe standby)', 0.12),
           ('N2 purge distribution (ISO 14644 Class 6 row)', 0.03)]
    fab_kw = round(sum(x[1] for x in fab), 4)
    _st('WAFER_FAB', fab_kw,
        f"AQS-EQP-FAB-001 sec.3 tool train (CZ class) at {v('FAB.litho-train.starts_per_d')} wafer starts/d: CZ charge "
        f"{cz:.2f} kWh/pull (CRC_SI cp/L) over a {camp:.0f} d campaign + tool-row parasitics; litho moved to the real "
        f"LITHO_* tools (A-M-287); was the 2 kW PECVD+belt study share.",
        design=[dict(item=i, kW=round(w, 4)) for i, w in fab] + [dict(item='total connected (calculated)', kW=fab_kw)])
    from .sizing import heat as HT
    bath_L, bath_C, n_b = v('FAB.wet-bench-train.bath_L'), v('FAB.wet-bench-train.bath_C'), int(v('FAB.wet-bench-train.heated_baths'))
    _, b_loss = HT.insulated_cylinder(bath_C, 300.0, 0.4)
    b_kWh = (bath_L * 4.18 * (bath_C - 25) / 3600 + b_loss * 24 / 1000) * n_b    # daily heat-up + hold, both baths
    _st('WET_BENCH', round(b_kWh / 24, 4),
        f"RCA/etch bench list (AQS-EQP-FAB-001 sec.1): {n_b} heated baths {bath_L:.0f} L at {bath_C:.0f} C "
        f"(SC1/SC2) - heat-up once daily + insulated hold (ASTM_C680 method, X-MFG-38 pattern); DHF at ambient; "
        f"{b_kWh:.2f} kWh/d.",
        design=[dict(item='SC1 bath 10 L PP tank, 80 C immersion heater', kWh_d=round(b_kWh / n_b, 3)),
                dict(item='SC2 bath 10 L PP tank, 80 C immersion heater', kWh_d=round(b_kWh / n_b, 3)),
                dict(item='DHF etch bath, ambient', kWh_d=0.0),
                dict(item='DIW rinse + N2 guns', kWh_d=0.05),
                dict(item='total', kWh_d=round(b_kWh + 0.05, 3))])

    # 4) AFTERBURNER: ID blower from the flue duty (AQS-SAN-01 850 C chamber, cooled exit duct 300 C class)
    flue = float(E['IA-AB-FLUE']['rate']['value'] or 0)
    V = flue / 29.0 * 8314.0 * (273.15 + 300.0) / SITE.p_atm_Pa() / 86400.0    # m3/s wet flue at MW 29, 300 C
    ab_kw = V * 1000.0 * v('OIL.afterburner-train.flue_fan_dP_Pa') / v('OIL.afterburner-train.flue_fan_eta') / 1000.0
    _st('AFTERBURNER', round(ab_kw, 4),
        f"ID blower on the {flue:.3f} kg/d flue (IA-AB-FLUE): {V * 1000:.1f} L/s at the 300 C exit duct class "
        f"(850 C chamber per X-SAN-01, cooled exit), {v('OIL.afterburner-train.flue_fan_dP_Pa'):.0f} Pa at eta "
        f"{v('OIL.afterburner-train.flue_fan_eta')} - the ignition transformer and burner management ride the "
        f"combustion panel at < 50 W.",
        design=[dict(item='flue ID fan (variable-speed, high-temp class)', kW=round(ab_kw, 4)),
                dict(item='ignition transformer + BMS panel', kW=0.05),
                dict(item='dampers and flame monitor', kW=0.01)])

    # 5) NUTRIENT_DOSE: metering pumps from the liquor duties (AQS-EQP-NUT-001)
    bd = float(E['IA-LEACH-BD']['rate']['value'] or 0)
    q_t = bd / 1000.0 / 7200.0                                        # bleed transfer over a 2 h window, m3/s
    p_t = 1000.0 * SITE.g() * q_t * v('NUT.nutrient-train.dose_head_m') / v('NUT.nutrient-train.pump_eta')
    nut_kw = (p_t / 1000.0) * (2.0 / 24.0) + 3 * 8 / 1000.0           # transfer window + 3 x 8 W metering pumps
    _st('NUTRIENT_DOSE', round(nut_kw, 4),
        f"Dosing-skid pumps (AQS-EQP-NUT-001): bleed transfer {bd:.1f} kg/d over a 2 h window at "
        f"{v('NUT.nutrient-train.dose_head_m'):.0f} m head, eta {v('NUT.nutrient-train.pump_eta')} "
        f"({p_t:.1f} W) + 3 x 8 W metering pumps on the bed/fish splits.",
        design=[dict(item='bleed transfer pump (diaphragm)', W=round(p_t, 1)),
                dict(item='metering pumps x3 (beds, fish, terrace)', W=24.0),
                dict(item='total average', kW=round(nut_kw, 4))])


def power():
    g = json.load(open(GP)); N = {n['unit_id']: n for n in g['nodes']}
    o = json.loads(subprocess.run([sys.executable,'docs-authority/_power_sizing.py'],cwd=ROOT,capture_output=True,text=True,check=True).stdout); p = o['bounding']; rf = o['roof']
    d = DR.load()
    pv = N['PV_ARRAY']['params']; kwp = math.ceil(p['pv_kWp']); count = math.ceil(kwp/pv['module_kw'])
    pv.update({'nameplate_kw': kwp, 'count': count, 'area_m2': round(rf['array_m2']),
               'mounting': 'roof only (X-PAR-07); ground field removed',
               'roof': {'footprint_mm': [rf['W_mm'], rf['D_mm']], 'bays': [rf['bays_x'], rf['bays_y']], 'footprint_m2': rf['footprint_m2'],
                        'extension_m2': rf['added_m2'], 'roof_capacity_kWp': round(rf['pv_roof_kWp'], 1), 'perimeter_pathway_mm': rf['layout']['perimeter_mm'],
                        'arrays': rf['layout']['arrays'], 'extension_load_kW': round(rf['ext']['total_kW'], 2),
                        'roof_load_kPa': {k: round(v, 3) for k, v in rf['load'].items()},
                        'basis': 'flow_graph/param/solver.py roof_close (IFC 2027 1205.3, NFPA 1 11.12, IECC 2021, ASHRAE 62.1, ISO 16798-3, ASCE 7-22)'}})
    N['ZNBR2']['params'].update({'kW': math.ceil(p['store_kW']), 'kWh': math.ceil(p['store_kWh']), 'charge_kW': math.ceil(p['charge_kW']), 'discharge_kW': math.ceil(p['discharge_kW']),
        'charge_basis': f"D75 cloudy-day case: yield {p['cloudy_yield_frac']:.2f} x mean (NREL_PVWATTS8 hourly scaling; NREL_NSRDB distribution to verify, A-M-109); charge = PV peak on that day less direct load"})
    N['SOL_ARK_60K']['params'].update({'count': p['inverters'], 'kW': p['inv_kW'], 'dc_ac_ratio': DR.val(DR.load(), 'pv_dc_ac_ratio'),
        'interconnection': {'export_peak_kW': round(p['export_peak_kW'], 1), 'export_kWh_d_clear': round(p['export_kWh_d_clear']),
            'standards': 'IEEE 1547-2018 Cat. B / III, UL 1741 SB listed; NEC 2026 705.11 supply-side connection, 705.20 disconnect; ANSI C12.20 class 0.2 bidirectional meter', 'decision': 'D75'}})
    pv['oversize_factor'] = DR.val(DR.load(), 'pv_oversize_factor'); pv['balance_kWp'] = math.ceil(p['pv_base_kWp'])
    # X-PAR-07: extension hall load on the graph (unconditioned until the owner decides; A-M-104)
    kw = round(rf['ext']['total_kW'], 4); E = {x['stream_id']: x for x in g['edges']}
    cond = "conditioned" if DR.val(DR.load(), "ext_conditioned") else "unconditioned"
    note = (f"X-PAR-07 solver.roof_close: {cond} extension {rf['added_m2']:.0f} m2; lighting {rf['ext']['light_kW']:.2f} kW (IECC 2021 C405, 10 % lit), "
            f"ventilation {rf['ext']['vent_kW']:.2f} kW (ASHRAE 62.1-2025 air at COP per ASHRAE 90.1-2025 Table 6.8.1-2, ISO 16798-3 fans), envelope {rf['ext']['envelope_kW']:.2f} kW (IECC 2021 C402 roof and walls, NOAA DFW degree days).")
    if 'EXT_HALL' not in N:
        n = dict(unit_id='EXT_HALL', sector_id='ELEC', presence='present', class_='building', tags=[], electrical_role='load', diagram_gap=None,
                 notes='Single-storey extension carrying the roof PV (X-PAR-07). Duty sheet docs-authority/duties/EXT_HALL.md.', enabled=True, modules=[], params={}, continuous_kw=None)
        n['class'] = n.pop('class_'); g['nodes'].append(n); N['EXT_HALL'] = n
    x = rf['ext']
    if x.get('mode'):
        note += (f" X-PAR-08: {x['mode']}-source heat pumps (ASHRAE 90.1-2025 Table 6.8.1-2), heating {x['Qh_kW']:.1f} kW and cooling {x['Qc_kW']:.1f} kW thermal average after"
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
        e = json.loads(json.dumps(E['SF-MFG_SHOP'])); e.update(stream_id='SF-EXT_HALL', to_unit_id='EXT_HALL', to_sector_id='ELEC', notes='X-PAR-07 extension hall feed')
        g['edges'].append(e); E['SF-EXT_HALL'] = e
    E['SF-EXT_HALL']['rate'] = {'value': kw, 'unit': 'kW', 'status': 'study', 'note': 'Equals EXT_HALL continuous_kw (X-PAR-07).'}
    pv1 = E['IA-PV-01']['rate']; pv1['value'] = round(pv1['value'] + kw - old, 4)
    if 'X-PAR-07' not in pv1.get('note', ''): pv1['note'] = pv1.get('note', '') + f' X-PAR-07 extension hall: +{kw:.2f} kW.'
    # D3 (2026-10-18): BACKUP_GEN rated kW stamped on the graph by this writer from the single governed source
    # drivers.json backup_gen_rated_kW (AQS-ELEC-007/AQS-RED-001 NFPA 110 rule); o2_close and _power_sizing read the same key.
    gen_kw = DR.val(d, 'backup_gen_rated_kW')
    N['BACKUP_GEN']['params'].update(rated_kW=gen_kw,
        rated_kW_basis='drivers.json backup_gen_rated_kW: single governed source (D3). Standby genset at 125 % of the critical list in 5 kW steps '
                        '(AQS-ELEC-007 / AQS-RED-001, NFPA 110 standby basis); written by write_graph power(), read by docs-authority/_power_sizing.py and o2_close.py.')
    # D4 companion: keep the ZNBR2 per-inverter distribution live with the section count (AQS-ELEC-008)
    N['ZNBR2']['params']['distribution'] = (f"distributed over the {p['inverters']} hybrid inverters, {p['store_kWh']/p['inverters']:.1f} kWh and "
                                            f"{p['charge_kW']/p['inverters']:.1f} kW charge each (AQS-ELEC-008)")
    # X-ELS-02 load-basis (A-M-275), power-chain-owned rows: ZNBR2 continuous_kw is the solved discharge
    # rating (was the stale 60 kW study value with no note); GEO_HP electrical = the re-solved Q4-bus lift
    # S44 (write_graph heat, AQS-DUTY-010 dispatch) over the ground-source heating COP (drivers gsh_cop_h).
    N['ZNBR2']['continuous_kw'] = {'value': round(p['discharge_kW'],4), 'unit': 'kW', 'status': 'study',
        'note': (f"X-ELS-02: solved continuous discharge rating from docs-authority/_power_sizing.py (AQS-ELEC-007, D75 chain; single writer write_graph power()): "
                 f"discharge {p['discharge_kW']:.1f} kW, charge {p['charge_kW']:.1f} kW, {p['store_kWh']:.0f} kWh over {p['inverters']} hybrid inverters (AQS-ELEC-008). "
                 f"Neither path is demand (storage); the charge draw rides IA-ESS-ZNBR2-CHG. Was the stale 60 kW study value.")}
    if 'S44' in E and isinstance(E['S44'].get('rate',{}).get('value'),(int,float)):
        s44 = float(E['S44']['rate']['value']); gkw = s44/DR.val(d,'gsh_cop_h')
        if N.get('GEO_HP') is not None:
            N['GEO_HP']['continuous_kw'] = rate(gkw,'kW',
                f"X-ELS-02: Q4-bus lift S44 {s44:.4f} kW (write_graph heat re-solve, AQS-DUTY-010 dispatch: lift only on deficit) / ground-source heating COP "
                f"{DR.val(d,'gsh_cop_h')} (drivers gsh_cop_h, ASHRAE 90.1-2025 class) = {gkw:.4f} kW; 2 x 100 % units (X-RED-07). "
                f"Source-loop circulator sized by AQS-DUTY-076 (pump stamped on GEO_HP_CLOSED_LOOP, counted on the same bounding winter case, A-M-317).")
            if 'SF-GEO_HP' in E: E['SF-GEO_HP']['rate'] = rate(gkw,'kW','X-ELS-02 load-basis (A-M-275). Feed equal to GEO_HP continuous_kw.')
    # X-ELS-02 (A-M-317): the source-loop circulator stamp is written by the process writer (the stage
    # that owns the SOL_ARK bus rebalance), reading sizing_geo_loop's params.design; this writer only
    # keeps the GEO_HP re-solve above current.
    # D1/D2 (2026-10-18): mvs.electrical is WRITTEN here from the live power-chain derivation (A-M-234 replaced_by; A-M-258
    # chain) instead of being a seed block that drifts from PV_ARRAY/ZNBR2/SOL_ARK params. Schema keys only
    # (design_tool ElectricalModel, extra=forbid). need = converged bounding demand incl. the EXT_HALL extension;
    # target = mean-day average generation of the installed array = pv_oversize_factor x balancing energy / 24
    # (= 2.5 x need at the drivers basis: 2.0 D75 oversize / 0.70 round trip); pv_* mirror PV_ARRAY.params;
    # znbr_* mirror the SOL_ARK hybrid-inverter block the ZNBR2 store is distributed over; rect = the one nine-channel RECTIFIER.
    target = p['pv_kWp']*DR.val(d,'pv_yield_kWh_kWp_d')*DR.val(d,'pv_roof_yield_factor')*DR.val(d,'pv_system_derate')/24.0
    mvs = g.setdefault('mvs', {})
    old_el = mvs.get('electrical') or {}
    mvs['electrical'] = {
        'bus_nodes': old_el.get('bus_nodes', ['SOL_ARK_60K', 'ZNBR2', 'RECTIFIER']),
        'storage_options': old_el.get('storage_options', ['ZNBR2', 'MEOH', 'PUMPED_HYDRO']),
        'need_kw': {'value': round(p['P_kW'], 2), 'unit': 'kW', 'status': 'study',
                    'note': f"write_graph power() live derivation (A-M-234 replaced_by; A-M-258): converged bounding demand incl. the EXT_HALL extension (roof_close {rf['bays_x']}x{rf['bays_y']} bays, ext {rf['ext']['total_kW']:.2f} kW)."},
        'target_kw': {'value': round(target, 2), 'unit': 'kW', 'status': 'study',
                      'note': 'write_graph power() live derivation: mean-day average generation of the installed array = pv_oversize_factor x balancing energy / 24 (= 2.5 x need at the drivers basis; A-M-234 formula, D75).'},
        'pv_module_kw': pv['module_kw'], 'pv_count': count,
        'znbr_module_kw': round(p['inv_kW']/p['inverters'], 6), 'znbr_count': p['inverters'],
        'rect_count': 1,
        'notes': ('write_graph power() (single writer, D1/D2/D4): need/target/PV/storage chain derived again per A-M-234 replaced_by / A-M-258 from '
                  'docs-authority/_power_sizing.py (demand = max(node continuous_kw, SOL_ARK feed) + RECT-EW bounding AC, A-M-231) and solver.roof_close; '
                  'pv_module_kw x pv_count = PV_ARRAY.params.nameplate_kw; znbr_* = the SOL_ARK hybrid-inverter block the ZNBR2 store is distributed over; '
                  'rect_count = the single nine-channel RECTIFIER (Rev AC; RECT_EW remap, A-M-255).')}
    open(GP,'w').write(json.dumps(g, indent=2))
    subprocess.run([sys.executable,'docs-authority/_collection_bus.py'],cwd=ROOT,capture_output=True,text=True,check=True)   # X-ELS-11 sections
    print(f"PV {kwp} kWp, storage {math.ceil(p['store_kW'])} kW / {math.ceil(p['store_kWh'])} kWh, inverters {p['inverters']} x 60 kW; "
          f"mvs.electrical need {round(p['P_kW'],2)} kW / target {round(target,2)} kW; BACKUP_GEN {gen_kw:.0f} kW")

def heat():
    """X-THM-01 store-ledger re-solve (R10b, A-M-259). Two Rev AC defects: (1) the kW-unit ladder-family edges
    (Q4 bus links, Q1/Q2 source feeds, the down and cross-tie steps, the HX-8 duty feed) carry layer 'mass', so the
    X-THM-01 ledger missed them; (2) the R6 heat-study branches (HX-9/HX-10, adsorption chiller, MAU coil, ELY stack
    heat, rectifier reject) were added without re-solving the transit, leaving Q3_A/B -10.3 and Q4_BUS -18.1 kW.
    This stage fixes the layers, then re-solves the transit by difference down the ladder (down-only, HEAT_LADDER.md;
    cross-tie pairs cancel; standing losses and duty-sheet sources/draws are held; Q3 is supply-limited so its draws
    run pro-rata on the rated profile and the Q3->Q4 step carries 0), then sets the GEO_HP lift S44 to the Q4 bus
    deficit (its AQS-DUTY-010 dispatch rule) and the dry-cooler rejection by difference. Idempotent."""
    import json as _j
    g = _j.load(open(GP)); N = {n['unit_id']: n for n in g['nodes']}; E = {e['stream_id']: e for e in g['edges']}
    TAGH = 'X-THM-01 R10b'
    kw = lambda sid: float(E[sid]['rate']['value'] or 0)
    def put(sid, x, why):
        E[sid]['rate']['value'] = round(x, 4)
        E[sid]['rate']['note'] = (E[sid]['rate'].get('note') or '').split(f' | {TAGH}')[0] + f' | {TAGH}: {why} (A-M-259).'
    fam = ('HL-AFTERBURNER-Q1-A', 'HL-AFTERBURNER-Q1-B', 'HL-GLASS_BURNOUT-Q2-A', 'HL-GLASS_BURNOUT-Q2-B',
           'HL-Q1-A-DOWN', 'HL-Q1-B-DOWN', 'HL-Q2-A-DOWN', 'HL-Q2-B-DOWN', 'HL-Q3-A-DOWN', 'HL-Q3-B-DOWN',
           'HL-Q1-X', 'HL-Q1-X-BA', 'HL-Q2-X', 'HL-Q2-X-BA', 'HL-Q3-X', 'HL-Q3-X-BA', 'HL-Q4-X', 'HL-Q4-X-BA',
           'HL-Q4-A-BUS', 'HL-Q4-B-BUS', 'IA-HX8')
    for s in fam:   # kW-unit ladder edges carry layer thermal (the ledger counts thermal + kW; 'mass' on a kW edge is the mislabel)
        if s in E and 'thermal' not in (E[s].get('layers') or []):
            E[s]['layers'] = ['thermal'] + [l for l in (E[s].get('layers') or []) if l != 'mass']
    # Q1 -> Q2 -> Q3 transit by difference (cross-tie pairs cancel; standing losses held at the duty-sheet rates)
    for A in ('A', 'B'):
        put(f'HL-Q1-{A}-DOWN', kw(f'HL-AFTERBURNER-Q1-{A}') - kw(f'IA-Q1{A}-LOSS'), 'down transit = tier source less the standing loss')
        put(f'HL-Q2-{A}-DOWN', kw(f'HL-Q1-{A}-DOWN') + kw(f'HL-GLASS_BURNOUT-Q2-{A}') - kw(f'IA-Q2{A}-LOSS'), 'down transit = Q1 down + burnout source less the standing loss')
        # Q3 supply-limited (HEAT_LADDER.md Duties: draws running, Q3 -> Q4 carries 0): draws pro-rata on the rated profile
        p3 = N[f'Q3_{A}']['params'].setdefault('x_thm_rated_draws', {k: kw(k) for k in (f'HL-Q3-{A}-HX4', f'HL-Q3-{A}-HX5', f'HL-Q3-{A}-HX6')})
        r3 = sum(p3.values()); s3 = kw(f'HL-Q2-{A}-DOWN')
        for k, rated in p3.items(): put(k, s3*rated/r3, f'supply-limited draw: {s3:.3f} kW Q3 supply pro-rata on the rated profile {r3:.3f} kW')
        put(f'HL-Q3-{A}-DOWN', 0.0, 'Q3 fully drawn; the Q3 -> Q4 step carries 0 (HEAT_LADDER.md Duties)')
        # Q4 batteries pass what they receive (HX-8 split + trim) to the header bus
        put(f'HL-Q4-{A}-BUS', kw(f'HL-HX8-Q4-{A}') + kw(f'IA-Q4{A}-TRIM') + kw(f'HL-Q3-{A}-DOWN'),
            'store-bus link = HX-8 split + rectifier trim + Q3 down (store closes)')
    fixed_in = sum(kw(s) for s in ('S53', 'S54', 'S63', 'S80', 'IA-ZNBR-HEAT', 'IA-RECT-Q4', 'SQ-H2O_ELYZ-Q4') if s in E)
    stores = kw('HL-Q4-A-BUS') + kw('HL-Q4-B-BUS')
    fixed_out = sum(kw(s) for s in ('IA-Q4-LIFE', 'S100', 'S101', 'IA-Q4-ADS', 'IA-Q4-MAU') if s in E)
    need = fixed_out - (fixed_in + stores)
    if need > 1e-6:
        put('S44', need, f'GEO_HP lifts the Q4 bus deficit {need:.3f} kW (AQS-DUTY-010 dispatch: lift only on deficit)')
        put('HL-Q4-REJ', 0.0, 'terminal idle on the design day: the study branches absorb the bus; dry cooler stays rated 12 kW for the upset case')
    else:
        put('S44', 0.0, 'GEO_HP idle: bus sources cover the branches (AQS-DUTY-010)')
        put('HL-Q4-REJ', -(need), f'terminal by difference {-(need):.3f} kW; dry cooler rated 12 kW for the upset case (A-M-244)')
    # ledger check on the stores (X-THM-01 tolerance 0.01 kW)
    import collections
    b = collections.Counter()
    for e in g['edges']:
        if 'thermal' in (e.get('layers') or []) and e.get('presence') != 'retired' and (e['rate'] or {}).get('unit') == 'kW':
            x = float(e['rate']['value'] or 0); b[e['from_unit_id']] -= x; b[e['to_unit_id']] += x
    bad = {u: round(v, 4) for u, v in b.items() if u[:3] in ('Q1_', 'Q2_', 'Q3_', 'Q4_') and abs(v) > 0.01}
    open(GP, 'w').write(_j.dumps(g, indent=2))
    print(f"heat ladder re-solved: stores {'CLOSE' if not bad else bad}; GEO_HP lift {kw('S44'):.3f} kW, dry-cooler rejection {kw('HL-Q4-REJ'):.3f} kW")

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
            from . import fire as FI                                                      # X-SAF-05: API 521 fire case on the receivers (A-M-188)
            if n['unit_id'] in FI.GAS_FIRE and p.get('design'):
                fc = FI.receiver_fire(p); rb['fire_case'] = {k: (round(v, 3) if isinstance(v, float) else v) for k, v in fc.items()}
                p['relief_mm'] = float(math.ceil(max(rb['bore_req_mm'], fc['bore_req_mm_per_half']))); rb['relief_mm_basis'] = 'governing of blocked outlet and fire case per half bank, rounded up to whole mm'
                rb['adequate'] = bool(p['relief_mm'] >= max(rb['bore_req_mm'], fc['bore_req_mm_per_half']))
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
        hold = ''
        if not H and qi > 0:   # A-M-182: liquid head from a hold-up volume where the unit has no sized height
            cl = u.get('class') or ''
            if cl in ('header', 'recycle_pipe'): hold = 'pipe only, no standing liquid'
            elif cl in ('farm', 'hab') or u['unit_id'].startswith('HAB_'): H = DV.val(D, 'atm_bed_depth_m'); hold = f'bed or fixture depth {H} m'
            else:
                kind = 'store' if (cl in ('tank', 'product', 'reagent', 'cut_tank', 'dock') or u['unit_id'] in ('ROOF_TANK', 'FAB_UPW_TANK')) else 'process'
                Vh = qi*TH*DV.val(D, 'atm_hold_d')[kind]; HD = DV.val(D, 'atm_HD'); Dh = (4*Vh/(math.pi*HD))**(1/3); H = HD*Dh
                hold = f'{kind} hold-up {DV.val(D, "atm_hold_d")[kind]:.0f} d = {Vh:.3f} m3, H/D {HD}'
        P_vap = 4*dp/1000; P_liq = SG*1000*SITE.g()*H/1000
        p['design_kPa'] = math.ceil((P_vap + P_liq)*2)/2
        rb['relief_mm_status'] = 'atmospheric; no relief orifice, open vent per API 2000'
        rb['design_case'] = (f"vapour {P_vap:.1f} kPa (4 x vent dP) + hydrostatic {P_liq:.1f} kPa ({H:.2f} m full at SG {SG}{'; ' + hold + ', A-M-182' if hold else ''}) = {p['design_kPa']} kPa g (A-M-174)" if H else
                             f"vapour {P_vap:.1f} kPa (4 x vent dP) = {p['design_kPa']} kPa g; {hold or 'no liquid inflow, no hydrostatic case'} (A-M-174)")
        nh += bool(H)
        n += 1
    open(GP, 'w').write(json.dumps(g, indent=2))
    print(f'API 2000 vents sized {n} ({nv} with a volume); design pressure from cases on {n} ({nh} with a hydrostatic case)')

if __name__ == '__main__':
    {'process': process, 'power': power, 'heat': heat, 'relief': relief, 'vent': vent}[sys.argv[1] if len(sys.argv) > 1 else 'process']()

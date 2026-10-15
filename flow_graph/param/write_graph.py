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
ELEC_IN = ('S17-BMED','S17-EW','SF-EVAP_ACID','SF-EVAP_BASE')

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
    N['BMED_ACID']['continuous_kw'] = rate(kw,'kW',f"{TAG}. BMED stack at 2 M product: {s['bmed']['base_kg_d']:.2f} kg/d NaOH x {DR.val(d,'bmed_sec_kWh_per_kg_base')} kWh/kg (EDBM_WHEY_2021) / 24 h. Solver flow_graph/param/solver.py bmed().")
    E['S17-BMED']['rate'] = rate(kw,'kW',f'{TAG}. 480 V feed equal to BMED_ACID continuous_kw.')
    # evaporators
    for side, key, src, prods, sa in (('ACID','evap_acid','BMED_ACID',('IA-ACID-01',),'HCl'),('BASE','evap_base','BMED_BASE',solver.BASE_DEMAND,'NaOH')):
        u = f'EVAP_{side}'; v = s[key]; w = DR.val(d,'acid_conc_design_wt' if side=='ACID' else 'base_conc_design_wt')
        note = (f"{TAG}. MVR evaporator, {sa} from 2 M ({DR.val(d,'bmed_product_wt_'+side.lower())*100:.2f} wt%) to {w*100:.0f} wt%"
                + (f" (below the HCl azeotrope {DR.val(d,'hcl_azeotrope_wt')*100:.1f} wt%, PERRY9_HCL)" if side=='ACID' else '')
                + f"; water off {v['water_kg_d']:.1f} kg/d x {DR.val(d,'mvr_kWh_per_t')} kWh/t (VOGELBUSCH_MVR upper bound) = {v['kW']:.2f} kW. Study.")
        node = N.get(u) or {'unit_id': u, 'sector_id': 'WET', 'presence': 'present', 'class': 'evaporator', 'tags': [], 'electrical_role': 'load',
                            'diagram_gap': None, 'enabled': True, 'modules': [], 'params': {}}
        node['notes'] = f'{sa} concentrator after {src} ({TAG}). Wetted parts per ULLMANN_HCL (impregnated graphite or fluoropolymer-lined; study).' if side=='ACID' else f'{sa} concentrator after {src} ({TAG}). Nickel or fluoropolymer-lined wetted parts (study).'
        node['continuous_kw'] = rate(v['kW'],'kW',note)
        node['params'].update({'presence':'present','water_off_kg_d':round(v['water_kg_d'],2),'feed_wt':DR.val(d,'bmed_product_wt_'+side.lower()),'product_wt':w,
                               'mvr_kWh_per_t':DR.val(d,'mvr_kWh_per_t'),'size_mm':node['params'].get('size_mm',[1200,900,2000]),'size_note':'L x W x H mm, study envelope pending vendor MVR quote','doc':'AQS-PAR-001'})
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
    p = json.loads(subprocess.run([sys.executable,'docs-authority/_power_sizing.py'],cwd=ROOT,capture_output=True,text=True,check=True).stdout)['bounding']
    pv = N['PV_ARRAY']['params']; kwp = math.ceil(p['pv_kWp'])
    pv.update({'nameplate_kw': kwp, 'count': math.ceil(kwp/pv['module_kw']), 'area_m2': round(kwp*5)})
    N['ZNBR2']['params'].update({'kW': math.ceil(p['store_kW']), 'kWh': math.ceil(p['store_kWh'])})
    N['SOL_ARK_60K']['params'].update({'count': p['inverters'], 'kW': p['inv_kW']})
    open(GP,'w').write(json.dumps(g, indent=2))
    print(f"PV {kwp} kWp, storage {math.ceil(p['store_kW'])} kW / {math.ceil(p['store_kWh'])} kWh, inverters {p['inverters']} x 60 kW")

if __name__ == '__main__':
    {'process': process, 'power': power}[sys.argv[1] if len(sys.argv) > 1 else 'process']()

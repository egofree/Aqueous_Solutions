"""X-INV-01 motor and actuator inventory (AQS-INV-001). Every item that moves under electrical power, by sector > sub-system > unit.
Sources, in priority: (1) models/mfg/<UNIT>/bom.csv (sized in-house designs); (2) docs-authority/MFG_TOOLS.md tool list; (3) graph
sizing params (EXT_HALL hvac, design dicts); (4) rules on the graph edges and node class, every one flagged 'assumed' in the
'basis' column and registered as A-M-119. Rating: next IEC 60034-1 preferred rating >= 1.15 x shaft (A-M-117); < 60 W shaft is a
24 V DC BLDC in a standard flange size; solenoids and valve actuators 24 V DC. Writes docs-authority/inventory/MOTOR_INVENTORY.md,
MOTOR_INVENTORY.csv and MOTOR_FAMILIES.csv. Run: python3 -m flow_graph.inventory.motors"""
import csv, glob, json, math, os, re, collections
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
IEC = [(0.09, '56'), (0.12, '63'), (0.18, '63'), (0.25, '71'), (0.37, '71'), (0.55, '80'), (0.75, '80'), (1.1, '90S'), (1.5, '90L'), (2.2, '100L'),
       (3.0, '100L'), (4.0, '112M'), (5.5, '132S'), (7.5, '132M'), (11.0, '160M'), (15.0, '160L'), (18.5, '180M'), (22.0, '180L'), (30.0, '200L'), (37.0, '225S')]
H_PUMP, ETA_PUMP, DP_FAN, ETA_FAN, RHO_G = 10.0, 0.4, 1000.0, 0.5, 1.2        # A-M-119 study defaults for unsized items
NO_PUMP = {'header', 'boundary', 'intra', 'recycle_pipe', 'relief', 'hx', 'heat_battery', 'pv', 'inverter', 'rectifier', 'ghex', 'hab', 'building', 'dock'}
FAN_CLS = {'scrubber', 'dryer', 'baghouse', 'ahu', 'thermal', 'wet_bench', 'fab'}

def size(kw, kind):
    if kind == 'solenoid': return 'solenoid', 'ISO 15218 coil, 22 mm', '24 V DC'
    if kind == 'actuator': return 'BLDC actuator', 'ISO 5211 F03 mount', '24 V DC'
    if kind == 'hermetic': return 'hermetic induction (scroll)', f'{next(r for r, f in IEC if r >= kw*1.15):g} kW hermetic', '480 V 3-ph'
    if kind == 'stepper': return 'stepper', 'NEMA 23 (57 mm)' if kw <= 0.1 else 'NEMA 34 (86 mm)', '48 V DC'
    if kw < 0.06: return 'BLDC', '42 mm (NEMA 17 flange)' if kw <= 0.015 else '57 mm (NEMA 23 flange)', '24 V DC'
    r, f = next((r, f) for r, f in IEC if r >= kw*1.15)
    return 'induction IE3', f'IEC {f} / {r:g} kW', '480 V 3-ph' if r >= 0.37 else '208 V 3-ph'

def build():
    g = json.load(open(os.path.join(ROOT, 'flow_graph/plant_flow_graph.json'))); N = {n['unit_id']: n for n in g['nodes']}
    seed = json.load(open(os.path.join(ROOT, 'flow_graph/placement_seed.json'))); st = json.load(open(os.path.join(ROOT, 'flow_graph/placement_study.json')))
    blk = {}
    for b in seed['blocks']:
        for u in b.get('unit_ids', []): blk[u] = b['block_id']
    for r in st['units']: blk.setdefault(r['unit_id'], r.get('block_id'))
    rows = []
    def add(u, dev, kind, kw, duty, basis, qty=1):
        n = N.get(u, {}); mt, sz, V = size(kw, kind)
        rows.append(dict(sector=n.get('sector_id') or 'MFG', subsystem=blk.get(u) or n.get('class') or '-', unit=u, device=dev, motor_type=mt, size=sz,
                         shaft_kW=round(kw, 4), voltage=V, duty=duty, qty=qty, basis=basis))
    bomu = set()
    for b in sorted(glob.glob(os.path.join(ROOT, 'models/mfg/*/bom.csv'))):
        u = b.split('/')[-2]
        for r in csv.reader(open(b)):
            t = ' '.join(r); d = r[1] if len(r) > 1 else t
            m = re.search(r'([\d.]+) kW (?:motor|shaft)', t) or re.search(r'[Gg]earmotor ([\d.]+) kW', t)
            q = int(r[2]) if len(r) > 2 and r[2].isdigit() else 1
            if 'heater' in t.lower(): continue
            if m: add(u, d[:60], 'motor', float(m.group(1)), 'S1', 'BOM (sized)', q); bomu.add(u)
            elif re.search(r'\bpump\b', t, re.I):
                add(u, d[:60], 'solenoid' if 'solenoid' in t.lower() else 'motor', 0.03 if 'dosing' in t.lower() else 0.12, 'S3' if 'dosing' in t.lower() else 'S1', 'BOM; shaft assumed (A-M-119)', q); bomu.add(u)
            elif re.search(r'blower', t, re.I): add(u, d[:60], 'motor', 0.02, 'S1', 'BOM; shaft assumed (A-M-119)', q); bomu.add(u)
            elif re.search(r'actuated|release valve', t, re.I): add(u, d[:60], 'actuator', 0.01, 'S2', 'BOM', q)
    # MFG tool list
    for line in open(os.path.join(ROOT, 'docs-authority/MFG_TOOLS.md')):
        c = [x.strip() for x in line.split('|')[1:-1]]
        if len(c) >= 3 and re.match(r'^[\d.]+$', c[2]):
            name, u, kw = c[0], (c[1] if c[1] in N else 'MFG_SHOP'), float(c[2])
            if re.search(r'furnace|welder|atomizer', name, re.I):
                if 'atomizer' in name.lower(): add(u, 'atomizer gas recirculation blower', 'motor', 1.5, 'S1', 'MFG_TOOLS; shaft assumed (A-M-119)')
                add(u, f'{name}: cooling-water pump', 'motor', 0.37, 'S1', 'MFG_TOOLS; assumed (A-M-119)'); continue
            if 'hand tools' in name: add(u, 'drill press spindle', 'motor', 0.55, 'S3', 'MFG_TOOLS; assumed'); add(u, 'bench grinder', 'motor', 0.37, 'S3', 'MFG_TOOLS; assumed'); continue
            add(u, f'{name}: main drive', 'motor', kw/1.15, 'S1' if 'compressor' in name.lower() else 'S3', 'MFG_TOOLS nameplate')
            if 'CNC' in name: add(u, f'{name}: axis drive', 'stepper', 0.4, 'S3', 'assumed closed-loop stepper per axis (A-M-119)', 3)
    # graph-sized and class rules
    E = collections.defaultdict(list)
    for e in g['edges']:
        if e.get('presence') == 'present' and e['rate'].get('unit') == 'kg/d' and (e['rate'].get('value') or 0) > 0: E[e['from_unit_id']].append(e)
    for u, n in N.items():
        c = n.get('class'); p = n.get('params') or {}; ck = (n.get('continuous_kw') or {}).get('value') or 0
        if u in bomu or c in ('boundary',) or n.get('presence') == 'absent': continue
        if u == 'EXT_HALL':
            h = p['hvac']; mods = 8
            add(u, 'air-source heat pump compressor', 'hermetic', h['peak_c_kW']/3.22/mods, 'S1 (VFD)', f"peak cooling {h['peak_c_kW']:.0f} kW / COP 3.22 / {mods} modules (module count assumed, A-M-119)", mods)
            add(u, 'heat pump condenser fan', 'motor', 0.75, 'S1 (EC)', 'assumed 2 per module (A-M-119)', 2*mods)
            q = h['vent_L_s']/1000/mods
            for k in ('supply', 'exhaust'): add(u, f'AHU {k} fan', 'motor', q*500/0.6/1000, 'S1 (VFD)', f"{h['vent_L_s']:.0f} L/s (ASHRAE 62.1) / {mods} AHUs at 500 Pa, fan eff 0.6 (assumed)", mods)
            add(u, 'AHU damper actuator', 'actuator', 0.005, 'S2', 'assumed 3 per AHU', 3*mods); continue
        if c == 'cold_box' and ck >= 1: add(u, 'air compressor (cold box feed)', 'motor', ck*0.85, 'S1', 'graph continuous_kw x 0.85 (assumed)'); add(u, 'expander brake / generator', 'motor', ck*0.05, 'S1', 'assumed')
        elif c == 'cold_box' and ck > 0: add(u, 'cryocooler compressor', 'hermetic', ck, 'S1', 'graph continuous_kw (assumed all compressor)')
        if c == 'heat_pump': add(u, 'heat pump compressor', 'hermetic', ck*0.9, 'S1', 'graph continuous_kw x 0.9 (assumed)'); add(u, 'ground-loop circulator', 'motor', 0.1, 'S1', 'assumed')
        if c == 'hydro': add(u, 'pump-turbine motor-generator', 'motor', 9.8/6, 'S2', 'AQS-ESS-001 9.8 kWh over 6 h (assumed)')
        if c in ('pem_fc', 'iem_fc'): add(u, 'cathode air blower', 'motor', ck*0.05, 'S1', 'assumed 5 % parasitic'); add(u, 'coolant pump', 'motor', ck*0.01, 'S1', 'assumed 1 %')
        if c == 'flow_battery': add(u, 'electrolyte pump (anolyte, catholyte) per stack string', 'motor', 0.25, 'S1', 'assumed 0.25 kW per string, 2 per string, 48 strings (A-M-119)', 96)
        if c == 'genset': add(u, 'starter motor', 'motor', 1.0, 'S2', 'assumed'); add(u, 'radiator fan', 'motor', 0.25, 'S1', 'assumed')
        if c in ('rectifier', 'inverter'): add(u, 'cooling fan', 'motor', 0.05, 'S1', 'assumed per cabinet', 48 if c == 'inverter' else 4)
        if c == 'dock': add(u, 'overhead door operator', 'motor', 0.75, 'S2', 'assumed', 2); add(u, 'dock leveller hydraulic pump', 'motor', 0.75, 'S2', 'assumed', 2)
        if c in ('hopper', 'feed'): add(u, 'screw feeder', 'motor', 0.18, 'S3', 'assumed')
        if c in ('mill', 'forming', 'tool') and u not in ('COLD_MILL', 'WIRE_DRAW', 'GAS_ATOMIZER') and ck > 0: add(u, 'main drive', 'motor', ck*0.8, 'S3', 'graph continuous_kw x 0.8 (assumed)')
        if c == 'tool' and u.startswith('LITHO'): add(u, 'wafer stage axis', 'stepper', 0.05, 'S3', 'assumed 2 axes', 2)
        if c in ('fab', 'wet_bench'): add(u, 'process vacuum pump', 'motor', 0.75, 'S1', 'assumed')
        if c == 'bmed': add(u, 'stack loop pumps (acid, base, salt)', 'motor', 0.25, 'S1', 'assumed 3 per stack', 3)
        if c == 'ew_cell': add(u, 'electrolyte circulation pump', 'motor', 0.12, 'S1', 'assumed')
        if 'agitator' in str(p.get('internals', '')): add(u, 'agitator', 'motor', 0.25, 'S1', 'graph internals; shaft assumed (A-M-119)')
        if c in FAN_CLS:
            gas = sum(e['rate']['value'] for e in E[u] if e['phase'] in ('G', 'V'))
            kw = max(0.01, gas/86400/RHO_G*DP_FAN/ETA_FAN/1000)
            add(u, 'induced-draft fan', 'motor', kw, 'S1', f'{gas:.1f} kg/d gas at {DP_FAN:.0f} Pa, eff {ETA_FAN} (assumed)')
            if c == 'baghouse': add(u, 'pulse-jet solenoid valve', 'solenoid', 0.01, 'S3', 'assumed 4 rows', 4)
        if c not in NO_PUMP and not str(c).startswith('cold'):
            for e in E[u]:
                if e['phase'] in ('L', 'S/L', 'L/S') and N.get(e['to_unit_id'], {}).get('class') not in ('header', 'boundary'):
                    kw = e['rate']['value']/86400*9.81*H_PUMP/ETA_PUMP/1000
                    add(u, f"transfer pump {e['stream_id']} to {e['to_unit_id']}", 'motor', kw, 'S1' if e['rate']['value'] > 500 else 'S3', f"{e['rate']['value']:.1f} kg/d at {H_PUMP:.0f} m, eff {ETA_PUMP} (assumed; gravity not credited)")
                    if c in ('reagent', 'dose', 'tank', 'cut_tank'): add(u, f"on/off valve {e['stream_id']}", 'solenoid', 0.008, 'S3', 'assumed one per dosed line')
            sol = [e for e in E[u] if e['phase'] == 'S' and e['rate']['value'] >= 50]
            for e in sol: add(u, f"screw conveyor {e['stream_id']} to {e['to_unit_id']}", 'motor', 0.37, 'S3', f"{e['rate']['value']:.0f} kg/d solids (>= 50 kg/d conveyed, assumed)")
    return rows

def write(rows):
    D = os.path.join(ROOT, 'docs-authority/inventory'); os.makedirs(D, exist_ok=True)
    rows.sort(key=lambda r: (r['sector'], str(r['subsystem']), r['unit'], r['device']))
    K = list(rows[0].keys())
    with open(os.path.join(D, 'MOTOR_INVENTORY.csv'), 'w', newline='') as f: w = csv.DictWriter(f, K); w.writeheader(); w.writerows(rows)
    fam = collections.OrderedDict()
    for r in rows:
        k = (r['motor_type'], r['size'], r['voltage']); x = fam.setdefault(k, dict(count=0, units=set(), kw=0.0)); x['count'] += r['qty']; x['units'].add(r['unit']); x['kw'] += r['shaft_kW']*r['qty']
    F = sorted(fam.items(), key=lambda kv: (kv[0][0], -kv[1]['count']))
    with open(os.path.join(D, 'MOTOR_FAMILIES.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['family', 'motor_type', 'size', 'voltage', 'count', 'units', 'installed_shaft_kW'])
        for i, ((mt, sz, V), x) in enumerate(F, 1): w.writerow([f'MF-{i:02d}', mt, sz, V, x['count'], len(x['units']), round(x['kw'], 2)])
    n = sum(r['qty'] for r in rows); a = sum(r['qty'] for r in rows if 'assumed' in r['basis'])
    L = ['# Motor and actuator inventory', '', 'Document number: AQS-INV-001', 'Revision: A', 'Date: 2026-10-15',
         'Authority: AQS-PLAN-007 X-INV-01 (owner programme 2026-10-15). Generated by `flow_graph/inventory/motors.py`; CSV beside this file. A-M-119.', '',
         '| Rev | Description | Date |', '| --- | --- | --- |', '| A | First issue. | 2026-10-15 |', '',
         f'{n} driven items in {len(rows)} rows across {len({r["unit"] for r in rows})} units. {a} items rest on a rule or default and are flagged "assumed" (A-M-119); they firm up as each unit gets its sizing (task 02) and mfg model.', '',
         'Rules for unsized items: one transfer pump per liquid outlet line at 10 m head and 0.4 efficiency (gravity not credited); one induced-draft fan on scrubbers, dryers, baghouse, AHUs, thermal units and fab benches at 1 kPa and 0.5; one screw conveyor per solids line >= 50 kg/d; one on/off solenoid valve per dosed line; agitators at 0.25 kW where the graph lists one. Motor type: < 60 W shaft is a 24 V DC BLDC; above, IE3 induction at the next IEC 60034-1 rating >= 1.15 x shaft with the IEC 60072-1 4-pole frame; scroll compressors are hermetic.', '',
         '## 1. Family rollup', '', '| Family | Motor type | Size | Voltage | Count | Units | Installed shaft kW |', '| --- | --- | --- | --- | --- | --- | --- |']
    L += [f'| MF-{i:02d} | {mt} | {sz} | {V} | {x["count"]} | {len(x["units"])} | {x["kw"]:.2f} |' for i, ((mt, sz, V), x) in enumerate(F, 1)]
    L += ['', '## 2. Inventory by sector > sub-system > unit', '']
    cur = None
    for r in rows:
        if r['sector'] != cur:
            cur = r['sector']; L += ['', f'### {cur}', '', '| Sub-system | Unit | Device | Motor type | Size | Shaft kW | Voltage | Duty | Qty | Basis |', '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
        L.append(f"| {r['subsystem']} | {r['unit']} | {r['device']} | {r['motor_type']} | {r['size']} | {r['shaft_kW']:g} | {r['voltage']} | {r['duty']} | {r['qty']} | {r['basis']} |")
    open(os.path.join(D, 'MOTOR_INVENTORY.md'), 'w').write('\n'.join(L) + '\n')
    return F, n, a

if __name__ == '__main__':
    F, n, a = write(build()); print(n, 'items', a, 'assumed', len(F), 'families')
    for i, ((mt, sz, V), x) in enumerate(F, 1): print(f'MF-{i:02d}', mt, sz, V, x['count'], round(x['kw'], 2))

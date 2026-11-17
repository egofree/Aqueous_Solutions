"""The inventory census family (family migration; reference writers
flow_graph/inventory/motors.py, wire.py, pipe.py, other.py,
motor_designs.py and stable_ids.py -- ledger section I rows `inventory_motors`,
`inventory_motor_designs`, `inventory_pipe`, `inventory_other`, plus the
section D row `inventory_wire`, whose motor-inventory input this family
supplies). The censuses classify and size every motor, circuit, pipe line and
building block of the plant: the NEC/IEC rating ladders, the branch-circuit
sizing, the stock-length packing, the family rollups and the stable family ids.
The census writes NO graph state (every row is `writes_graph: false` in the
manifest): the rows are the boundary data the renderer lane
(flow_graph/v2/render/inventory.py) lays out into the committed registers and
documents. The committed CSVs are the golden these functions reproduce.

Grid doctrine (owner ruling 2026-11-15; the doc-lane raw-float precedent of
render/sizing_docs.py `_scrub_liquid_raw` and functions/headers.py): the
committed census CSVs are the v1 float books -- each cell is the reference
writer's own float chain (round() at the decimals the writer published). An
exact-Decimal book floats a repr away from the committed cell, so every chain
here is a float replica of the reference writer's expression over the same
boundary inputs, constants entering as floats of their exact decimals by
flo(), every published rounding point through the writer's own round() call.
Counts and ladder indices run as native integers. No float literals; the lint
holds this.

DISPOSITION OF THE READS (the ledger's hidden-dependency map, cross-stage map
1 rows 7/8/9/16 and the soft-dependency table): the v1 censuses read files
beside the graph. Each read enters as an explicit inputs payload -- the
headers-family idiom (inputs['iso_sheets'], inputs['nozzles']) -- and the
payload absence takes the v1 absent-file branch:

- mfg BOMs and fasteners (models/mfg/*/bom.csv and fasteners.csv, the CAD
  group's committed outputs): inputs['mfg_boms'] {unit: [raw csv rows]} and
  inputs['mfg_fasteners'] {unit: [dict rows]}; a unit absent from the payload
  takes the v1 absent-directory branch (no rows).
- the unit envelope BOMs (models/units/*/bom.csv, the doc_unit_boms product)
  and the per-unit fastener line counts read from them: the PLANT_BOM rollup
  takes them from inputs['unit_boms'] {unit: [dict rows]}.
- MFG_TOOLS.md tool table (the doc_mfg_tools product): the cell parse travels
  as inputs['mfg_tools'] -- a list of (name, unit cell, nameplate kW) rows
  under the v1 `len(c) >= 3 and numeric c[2]` filter.
- placement seed + study (the hidden bus, cross-stage map 1 rows 7/8/9): only
  the block-id map the censuses use ports -- inputs['placement'] {unit:
  block_id} (seed blocks first, study rows setdefault, the v1 order).
- ISO_SHEETS.csv (soft, exists-guarded; the auto-router's retired sidecar):
  inputs['iso_sheets'] row dicts; absent or empty payload = the v1 absent-file
  branch. The committed census golden is the WITH-data branch (the committed
  sidecar still carries the routed lengths the registers were built from).
- SUPPORTS.md span table (the supports product): inputs['supports'] {line:
  support count} (the v1 `| ` row / column 6 digit parse).
- GAS_DETECTORS.csv (doc_gas_det product) and sif_list.csv (doc_sif product):
  inputs['gas_detectors'] / inputs['sif_list'] dict rows (the files are
  exists-guarded in v1; an absent payload takes that branch).
- the nozzle CSVs (nozzle_sched product, `os.path.exists` probe per unit):
  inputs['nozzle_units'] = the sorted unit ids that have a nozzle csv.
- line-list positions (the _line_list.py C dict wire.py re-ran over
  subprocess): inputs['line_positions'] {unit: ([x, y, z], description)}.
- the grounding-grid study lengths (_grounding_study.py, a physics family not
  yet landed -- the electrical-wave REMAINING notes it on the protection row):
  inputs['grounding_grid'] {'ring_m': ..., 'mesh_m': ...}; an absent payload
  takes the v1 failed-subprocess branch (no grounding row).
- COLLECTION_BUS.md CB- rows (write_graph_power's renderer half, the ledger's
  hard hidden dependency 16): composed IN MEMORY from the power family's
  sections book -- the SOL_ARK_60K params.sections counts and breaker ratings
  are the same rows the collection-bus document prints, so the parse dies and
  the book feeds the census directly (the electrical-wave in-memory
  composition idiom). No payload.
- the family-id registers (flow_graph/inventory/*_family_ids.json, the
  append-only allocation registers): inputs['family_registers'] {prefix:
  register dict}. The v1 assign() opens and rewrites the register file; here
  the register dict is a payload, assignment is in-memory, and nothing is
  written back. A payload that carries a prefix but misses a family raises,
  loud, because the committed registers are the golden and a new family is
  an enumerated reference migration; a payload with no entry for the prefix
  takes the v1 absent-file branch (the first run allocated ids from 01 in
  enumeration order, in memory).
- the motor-family CAD BOMs (models/motors/MF-*/bom.csv, cad_motors outputs,
  the PLANT_BOM rollup input): inputs['motor_family_boms'] {family: [dict
  rows]}.
- the duty-sheet section 3 texts (hand-authored pages, the duties wave's
  REMAINING census): inputs['duty_sec3'] {unit: text or None} for the EOL
  classing sweep and the unit-BOM material line.

The registered solve set does not import this family: the censuses stamp no
graph field, so they run in the renderer lane only (the renderers call the
book builders once per render and share the rows, the electrical-wave one
shared pure chain). Pure: no I/O here.
"""
import math
import re

from flow_graph.param import site as SITE          # the baseline Earth constants (X-LOC-03)

IEC = tuple((float(x), frame) for x, frame in
            [('0.09', '56'), ('0.12', '63'), ('0.18', '63'), ('0.25', '71'),
             ('0.37', '71'), ('0.55', '80'), ('0.75', '80'), ('1.1', '90S'),
             ('1.5', '90L'), ('2.2', '100L'), ('3.0', '100L'), ('4.0', '112M'),
             ('5.5', '132S'), ('7.5', '132M'), ('11.0', '160M'), ('15.0', '160L'),
             ('18.5', '180M'), ('22.0', '180L'), ('30.0', '200L'), ('37.0', '225S'),
             ('45.0', '250M'), ('55.0', '280S'), ('75.0', '280M'), ('90.0', '315S'),
             ('110.0', '315M'), ('132.0', '315L'), ('160.0', '315L'), ('200.0', '355M'),
             ('250.0', '355L'), ('315.0', '355L'), ('400.0', '400M'), ('500.0', '400L'),
             ('630.0', '450M')])                        # IEC 60034-1 preferred outputs, frames per IEC 60072-1
H_PUMP, ETA_PUMP, DP_FAN, ETA_FAN = float('10.0'), float('0.4'), float('1000.0'), float('0.5')
RHO_G = float('1.2')                                        # A-M-119 study defaults for unsized items
NO_PUMP = {'header', 'boundary', 'intra', 'recycle_pipe', 'relief', 'hx', 'heat_battery', 'pv', 'inverter',
           'rectifier', 'ghex', 'hab', 'building', 'dock'}
SPEED = {'solenoid': 'on/off', 'actuator': 'on/off', 'stepper': 'stepper driver', 'hermetic': 'fixed speed'}
FAN_CLS = {'scrubber', 'dryer', 'baghouse', 'ahu', 'thermal', 'wet_bench', 'fab'}
DAY_S = 86400                                               # s/d
W_PER_KW = 1000                                             # W/kW


def flo(s):
    """A constant as the float of its exact decimal (the no-float-literal rule)."""
    return float(s)


# ---- the graph views (the electrical-family idiom: the v1 stage read the
# committed graph file; the seed with the families' overlays composed is the
# same file state at the doc phase) -------------------------------------------

def _node_view(m):
    """The seed nodes in order, params and continuous_kw resolved (overlay
    composed)."""
    out = {}
    for uid, n in m.nodes.items():
        v = dict(n)
        if 'params' in v:
            v['params'] = m.field('node', uid, 'params')
        if 'continuous_kw' in v:
            v['continuous_kw'] = m.field('node', uid, 'continuous_kw')
        out[uid] = v
    return out


def _edges(m):
    """The seed edges in order, rates resolved (overlay first)."""
    out = []
    for e in m.data['edges']:
        if ('edge', e['stream_id'], 'rate') in m.computed:
            e2 = dict(e)
            e2['rate'] = m.field('edge', e['stream_id'], 'rate')
            out.append(e2)
        else:
            out.append(e)
    return out


def _drv(inputs, key):
    """A driver value, verbatim (the v1 DR.val read)."""
    return inputs['drivers'][key]['value']


def _gravity(inputs):
    """Apparent gravity, m/s2: the site profile entry (the v1 SITE.g() read);
    the baseline value stands when the inputs carry no profile."""
    prof = inputs.get('site_profile')
    if not prof:
        return flo(SITE.g(SITE.BASELINE))
    return prof['groups']['gravity']['entries']['g_m_s2']['value']


def _blocks(m, inputs):
    """The placement block map: seed blocks first, study rows setdefault (the
    v1 order); the payload carries exactly that merged map."""
    return inputs.get('placement') or {}


# ---- X-INV-01: the motor and actuator census (AQS-INV-001) -------------------

def _motor_size(kw, kind):
    """The v1 motors.size() rating pick: solenoid/actuator 24 V DC, hermetic
    and EC fans and induction at the next IEC rating >= 1.15 x shaft
    (A-M-117), steppers NEMA flanges, BLDC under 60 W."""
    if kind == 'solenoid':
        return 'solenoid', 'ISO 15218 coil, 22 mm', '24 V DC'
    if kind == 'actuator':
        return 'BLDC actuator', 'ISO 5211 F03 mount', '24 V DC'
    if kind == 'hermetic':
        return 'hermetic induction (scroll)', f'{next(r for r, f in IEC if r >= kw * flo("1.15")):g} kW hermetic', '480 V 3-ph'
    if kind == 'ec_fan':    # electronically commutated fan: permanent-magnet motor with built-in electronics; IEC 60034-30-1 efficiency classes do not apply
        r = next(r for r, f in IEC if r >= kw * flo('1.15'))
        return 'EC (electronically commutated, permanent-magnet) fan motor', f'{r:g} kW EC fan, integrated drive', \
            '480 V 3-ph' if r >= flo('0.37') else '208 V 3-ph'
    if kind == 'stepper':
        return 'stepper', 'NEMA 23 (57 mm)' if kw <= flo('0.1') else 'NEMA 34 (86 mm)', '48 V DC'
    if kw < flo('0.06'):
        return 'BLDC', '42 mm (NEMA 17 flange)' if kw <= flo('0.015') else '57 mm (NEMA 23 flange)', '24 V DC'
    r, f = next((r, f) for r, f in IEC if r >= kw * flo('1.15'))
    return 'induction IE3', f'IEC {f} / {r:g} kW', '480 V 3-ph' if r >= flo('0.37') else '208 V 3-ph'


def motor_rows(m, inputs):
    """The AQS-INV-001 census rows: every item that moves under electrical
    power, by sector > sub-system > unit. Sources in the v1 priority: the mfg
    BOMs (payload), the MFG_TOOLS tool list (payload), the graph sizing books,
    then the class rules (A-M-119). Rows sorted as the v1 write() sorts."""
    N = _node_view(m)
    blk = _blocks(m, inputs)
    g_m_s2 = _gravity(inputs)
    rows = []

    def add(u, dev, kind, kw, duty, basis, qty=1, speed=None):
        n = N.get(u, {})
        mt, sz, V = _motor_size(kw, kind)
        if speed is None:
            speed = SPEED.get(kind, 'fixed speed') if kind != 'motor' or kw >= flo('0.06') else 'BLDC driver'
        rows.append(dict(sector=n.get('sector_id') or 'MFG', subsystem=blk.get(u) or n.get('class') or '-', unit=u,
                         device=dev, motor_type=mt, size=sz, shaft_kW=round(kw, 4), voltage=V, duty=duty,
                         speed_control=speed, qty=qty, basis=basis))
    bomu = set()
    for u, bom in sorted((inputs.get('mfg_boms') or {}).items()):
        for r in bom:
            t = ' '.join(r)
            d = r[1] if len(r) > 1 else t
            mm = re.search(r'([\d.]+) kW (?:motor|shaft)', t) or re.search(r'[Gg]earmotor ([\d.]+) kW', t)
            q = int(r[2]) if len(r) > 2 and r[2].isdigit() else 1
            if 'heater' in t.lower():
                continue
            if mm:
                add(u, d[:60], 'motor', float(mm.group(1)), 'S1', 'BOM (sized)', q)
                bomu.add(u)
            elif re.search(r'\bpump\b', t, re.I):
                add(u, d[:60], 'solenoid' if 'solenoid' in t.lower() else 'motor',
                    flo('0.03') if 'dosing' in t.lower() else flo('0.12'),
                    'S3' if 'dosing' in t.lower() else 'S1', 'BOM; shaft assumed (A-M-119)', q)
                bomu.add(u)
            elif re.search(r'blower', t, re.I):
                add(u, d[:60], 'motor', flo('0.02'), 'S1', 'BOM; shaft assumed (A-M-119)', q)
                bomu.add(u)
            elif re.search(r'actuated|release valve', t, re.I):
                add(u, d[:60], 'actuator', flo('0.01'), 'S2', 'BOM', q)
    for name, unit_cell, kw in (inputs.get('mfg_tools') or []):     # the MFG_TOOLS.md tool table rows
        u = unit_cell if unit_cell in N else 'MFG_SHOP'
        if re.search(r'furnace|welder|atomizer', name, re.I):
            if 'atomizer' in name.lower():
                add(u, 'atomizer gas recirculation blower', 'motor', flo('1.5'), 'S1', 'MFG_TOOLS; shaft assumed (A-M-119)')
            add(u, f'{name}: cooling-water pump', 'motor', flo('0.37'), 'S1', 'MFG_TOOLS; assumed (A-M-119)')
            continue
        if 'hand tools' in name:
            add(u, 'drill press spindle', 'motor', flo('0.55'), 'S3', 'MFG_TOOLS; assumed')
            add(u, 'bench grinder', 'motor', flo('0.37'), 'S3', 'MFG_TOOLS; assumed')
            continue
        add(u, f'{name}: main drive', 'motor', kw / flo('1.15'), 'S1' if 'compressor' in name.lower() else 'S3',
            'MFG_TOOLS nameplate')
        if 'CNC' in name:
            add(u, f'{name}: axis drive', 'stepper', flo('0.4'), 'S3', 'assumed closed-loop stepper per axis (A-M-119)', 3)
    E = {}
    for e in _edges(m):
        if e.get('presence') == 'present' and e['rate'].get('unit') == 'kg/d' and (e['rate'].get('value') or 0) > 0:
            E.setdefault(e['from_unit_id'], []).append(e)
    for u in N:
        n = N[u]
        c = n.get('class')
        p = n.get('params') or {}
        kw = n.get('continuous_kw') or {}
        ck = (kw.get('value') if isinstance(kw, dict) else kw) or 0
        if u in bomu or c in ('boundary',) or n.get('presence') == 'absent':
            continue
        if u == 'EXT_HALL':
            h = p['hvac']
            mods = 8
            add(u, 'air-source heat pump compressor', 'hermetic', h['peak_c_kW'] / flo('3.22') / mods, 'S1',
                f"peak cooling {h['peak_c_kW']:.0f} kW / COP 3.22 / {mods} modules (module count assumed, A-M-119)",
                mods, speed='variable-frequency drive')
            add(u, 'heat pump condenser fan', 'ec_fan', flo('0.75'), 'S1',
                'assumed 2 per module; EC fan type assumed (A-M-119)', 2 * mods,
                speed='electronically commutated (EC) motor')
            q = h['vent_L_s'] / flo('1000') / mods
            for k in ('supply', 'exhaust'):
                add(u, f'AHU {k} fan', 'motor', q * flo('500') / flo('0.6') / flo('1000'), 'S1',
                    f"{h['vent_L_s']:.0f} L/s (ASHRAE 62.1) / {mods} AHUs at 500 Pa, fan eff 0.6 (assumed)", mods,
                    speed='variable-frequency drive')
            add(u, 'AHU damper actuator', 'actuator', flo('0.005'), 'S2', 'assumed 3 per AHU', 3 * mods)
            continue
        if c == 'cold_box' and ck >= 1:
            add(u, 'air compressor (cold box feed)', 'motor', ck * flo('0.85'), 'S1', 'graph continuous_kw x 0.85 (assumed)')
            add(u, 'expander brake / generator', 'motor', ck * flo('0.05'), 'S1', 'assumed')
        elif c == 'cold_box' and ck > 0:
            add(u, 'cryocooler compressor', 'hermetic', ck, 'S1', 'graph continuous_kw (assumed all compressor)')
        if c == 'heat_pump':
            add(u, 'heat pump compressor', 'hermetic', ck * flo('0.9'), 'S1', 'graph continuous_kw x 0.9 (assumed)')
            add(u, 'ground-loop circulator', 'motor', flo('0.1'), 'S1', 'assumed')
        if c == 'hydro':
            add(u, 'pump-turbine motor-generator', 'motor', flo('9.8') / 6, 'S2', 'AQS-ESS-001 9.8 kWh over 6 h (assumed)')
        if c in ('pem_fc', 'iem_fc'):
            add(u, 'cathode air blower', 'motor', ck * flo('0.05'), 'S1', 'assumed 5 % parasitic')
            add(u, 'coolant pump', 'motor', ck * flo('0.01'), 'S1', 'assumed 1 %')
        if c == 'flow_battery':
            add(u, 'electrolyte pump (anolyte, catholyte) per stack string', 'motor', flo('0.25'), 'S1',
                'assumed 0.25 kW per string, 2 per string, 48 strings (A-M-119)', 96)
        if c == 'genset':
            add(u, 'starter motor', 'motor', flo('1.0'), 'S2', 'assumed')
            add(u, 'radiator fan', 'motor', flo('0.25'), 'S1', 'assumed')
        if c in ('rectifier', 'inverter'):
            add(u, 'cooling fan', 'motor', flo('0.05'), 'S1', 'assumed per cabinet', 48 if c == 'inverter' else 4)
        if c == 'dock':
            add(u, 'overhead door operator', 'motor', flo('0.75'), 'S2', 'assumed', 2)
            add(u, 'dock leveller hydraulic pump', 'motor', flo('0.75'), 'S2', 'assumed', 2)
        if c in ('hopper', 'feed'):
            add(u, 'screw feeder', 'motor', flo('0.18'), 'S3', 'assumed')
        if c in ('mill', 'forming', 'tool') and u not in ('COLD_MILL', 'WIRE_DRAW', 'GAS_ATOMIZER') and ck > 0:
            add(u, 'main drive', 'motor', ck * flo('0.8'), 'S3', 'graph continuous_kw x 0.8 (assumed)')
        if c == 'tool' and u.startswith('LITHO'):
            add(u, 'wafer stage axis', 'stepper', flo('0.05'), 'S3', 'assumed 2 axes', 2)
        if c in ('fab', 'wet_bench'):
            add(u, 'process vacuum pump', 'motor', flo('0.75'), 'S1', 'assumed')
        if c == 'bmed':
            add(u, 'stack loop pumps (acid, base, salt)', 'motor', flo('0.25'), 'S1', 'assumed 3 per stack', 3)
        if c == 'ew_cell':
            add(u, 'electrolyte circulation pump', 'motor', flo('0.12'), 'S1', 'assumed')
        if 'agitator' in str(p.get('internals', '')):
            add(u, 'agitator', 'motor', flo('0.25'), 'S1', 'graph internals; shaft assumed (A-M-119)')
        if c in FAN_CLS:
            gas = sum(e['rate']['value'] for e in E.get(u, []) if e['phase'] in ('G', 'V'))
            kwf = max(flo('0.01'), gas / DAY_S / RHO_G * DP_FAN / ETA_FAN / W_PER_KW)
            add(u, 'induced-draft fan', 'motor', kwf, 'S1', f'{gas:.1f} kg/d gas at {DP_FAN:.0f} Pa, eff {ETA_FAN} (assumed)')
            if c == 'baghouse':
                add(u, 'pulse-jet solenoid valve', 'solenoid', flo('0.01'), 'S3', 'assumed 4 rows', 4)
        if c not in NO_PUMP and not str(c).startswith('cold'):
            for e in E.get(u, []):
                if e['phase'] in ('L', 'S/L', 'L/S') and N.get(e['to_unit_id'], {}).get('class') not in ('header', 'boundary'):
                    kwp = e['rate']['value'] / DAY_S * g_m_s2 * H_PUMP / ETA_PUMP / W_PER_KW
                    add(u, f"transfer pump {e['stream_id']} to {e['to_unit_id']}", 'motor', kwp,
                        'S1' if e['rate']['value'] > 500 else 'S3',
                        f"{e['rate']['value']:.1f} kg/d at {H_PUMP:.0f} m, eff {ETA_PUMP} (assumed; gravity not credited)")
                    if c in ('reagent', 'dose', 'tank', 'cut_tank'):
                        add(u, f"on/off valve {e['stream_id']}", 'solenoid', flo('0.008'), 'S3', 'assumed one per dosed line')
            sol = [e for e in E.get(u, []) if e['phase'] == 'S' and e['rate']['value'] >= 50]
            for e in sol:
                add(u, f"screw conveyor {e['stream_id']} to {e['to_unit_id']}", 'motor', flo('0.37'), 'S3',
                    f"{e['rate']['value']:.0f} kg/d solids (>= 50 kg/d conveyed, assumed)")
    rows.sort(key=lambda r: (r['sector'], str(r['subsystem']), r['unit'], r['device']))
    return rows


# ---- the stable family ids (flow_graph/inventory/stable_ids.py port) ---------

def assign_ids(registers, prefix, fields, keys):
    """The v1 stable_ids.assign(): map each key (the tuple of `fields` values)
    to its family id. A payload that carries the prefix but misses a family
    raises loud -- the committed registers are the golden and a new family is
    an enumerated reference migration, never a silent allocation. A payload
    with no entry for the prefix takes the v1 absent-file branch: the v1
    register file did not exist yet and the first run allocated the ids from
    01 in the same enumeration order -- here the allocation is in memory and
    nothing is written back."""
    fams = registers[prefix]['families'] if prefix in registers else {}
    ids = {tuple(v[f] for f in fields): k for k, v in fams.items() if all(f in v for f in fields)}
    nxt = max((int(k.split('-')[1]) for k in fams), default=0) + 1
    for k in keys:
        if k not in ids:
            if prefix in registers:
                raise KeyError(f'family {k} is not in the {prefix} register payload: a new family is an '
                               'enumerated reference migration (the register is not written back)')
            ids[k] = f'{prefix}-{nxt:02d}'
            nxt += 1
    return ids


def id_number(fid):
    """The v1 stable_ids.number()."""
    return int(fid.split('-')[1])


def motor_families(rows, inputs):
    """The AQS-INV-001 family rollup: (family id -> (motor_type, size,
    voltage)) with counts, units and installed shaft kW, ids from the register
    payload, ordered by id number as the v1 write() orders them."""
    fam = {}
    for r in rows:
        k = (r['motor_type'], r['size'], r['voltage'])
        x = fam.setdefault(k, dict(count=0, units=set(), kw=flo('0.0')))
        x['count'] += r['qty']
        x['units'].add(r['unit'])
        x['kw'] += r['shaft_kW'] * r['qty']
    ids = assign_ids(inputs.get('family_registers') or {}, 'MF', ('motor_type', 'size', 'voltage'),
                     sorted(fam, key=lambda k: (k[0], -fam[k]['count'])))
    F = sorted(fam.items(), key=lambda kv: id_number(ids[kv[0]]))
    return F, ids


# ---- X-INV-04: the pipe census (AQS-INV-003) ---------------------------------

STOCK, KERF = 6096, 3                                        # 20 ft random length, A-M-124 kerf
FIT = {'M': ('ASME B16.9 LR 90 elbow', 'ASME B16.5 Cl 150 flange', 'ASME B16.20 gasket',
             'ASTM A193 B7 stud + 2 A194 2H nuts'),
       'P1': ('ASTM D2467 socket 90 elbow', 'ASTM D2467 flange', 'EPDM full-face gasket', 'ASTM A193 B7 stud + nuts'),
       'P2': ('ASTM F439 socket 90 elbow', 'ASTM F439 flange', 'EPDM full-face gasket', 'ASTM A193 B7 stud + nuts'),
       'P3': ('ISO 10931 butt-fusion 90 elbow', 'ISO 10931 stub end + backing ring', 'PTFE envelope gasket',
              'ASTM A193 B7 stud + nuts'),
       'P4': ('ISO 15494 butt-fusion 90 elbow', 'ISO 15494 stub end + backing ring', 'EPDM gasket',
              'ASTM A193 B7 stud + nuts'),
       'P5': ('ASTM D3261 butt-fusion 90 elbow', 'ASTM D3261 stub end + backing ring', 'EPDM gasket',
              'ASTM A193 B7 stud + nuts'),
       'F1': ('ASTM D5421 FRP 90 elbow', 'ASTM D5421 FRP flange', 'EPDM full-face gasket', 'ASTM A193 B7 stud + nuts')}
NOCLASS = '—'                                                # line list: no piping class (U+2014, the v1 literal)


def pipe_fit(cls):
    """The v1 pipe.fit(): the fitting standards by piping class."""
    return FIT.get(cls, FIT['M'] if cls.startswith('M') else FIT['P1'])


def stock_pack(cuts):
    """The v1 pipe.pack(): first-fit decreasing stock-length packing."""
    bins = []
    for c in sorted(cuts, reverse=True):
        for i, b in enumerate(bins):
            if b >= c + KERF:
                bins[i] -= c + KERF
                break
        else:
            bins.append(STOCK - c - KERF)
    return len(bins), sum(bins)


def pipe_rows(m, inputs):
    """The AQS-INV-003 line rows from the isometric sheet quantities (payload;
    absent payload = the v1 retired-sidecar branch, an empty roster)."""
    N = _node_view(m)
    blk = _blocks(m, inputs)
    R = []
    for s in (inputs.get('iso_sheets') or []):
        u = s['frm'] if s['frm'] in N else s['to']
        n = N.get(u, {})
        cuts = [int(c) for c in s['cut_list_mm'].split()] if s['cut_list_mm'].strip() else []
        el, fl, gk, sb = pipe_fit(s['cls'])
        R.append(dict(sector=n.get('sector_id') or 'MFG', subsystem=blk.get(u) or n.get('class') or '-', unit=u,
                      line=s['line'], DN=int(s['DN']), cls=s['cls'], material=s['material'],
                      pipe_m=float(s['pipe_m']), pieces=int(s['pieces']), elbows_90=int(s['elbows_90']),
                      elbow_std=el, flanges=int(s['flanges']), flange_std=fl, gaskets=int(s['gaskets']),
                      gasket_std=gk, stud_bolts=int(s['stud_bolts']), stud_size=s['stud_size'], stud_std=sb,
                      joints=int(s['joints']), joint_type=s['joint_type'], cuts=cuts))
    R.sort(key=lambda r: (r['sector'], str(r['subsystem']), r['unit'], r['line']))
    return R


def pipe_families(R, inputs):
    """The AQS-INV-003 family rollup: (cls, material, DN) -> books, ids from
    the register payload, stock packing per family. Returns (out rows, total
    pipe m)."""
    F = {}
    for r in R:
        if r['cls'] == NOCLASS:
            continue                                        # not bought or made as pipe; listed in section 2a
        f = F.setdefault((r['cls'], r['material'], r['DN']),
                         dict(m=flo('0.0'), lines=0, cuts=[], el=0, fl=0, gk=0, sb=0, jt=0, jtype=set(), studs=set()))
        f['m'] += r['pipe_m']
        f['lines'] += 1
        f['cuts'] += r['cuts']
        f['el'] += r['elbows_90']
        f['fl'] += r['flanges']
        f['gk'] += r['gaskets']
        f['sb'] += r['stud_bolts']
        f['jt'] += r['joints']
        f['jtype'].add(r['joint_type'])
        f['studs'].add(r['stud_size'])
    ids = assign_ids(inputs.get('family_registers') or {}, 'PF', ('cls', 'material', 'DN'),
                     [k for k, _ in sorted(F.items(), key=lambda kv: -kv[1]['m'])])
    FF = sorted(F.items(), key=lambda kv: id_number(ids[kv[0]]))
    out = []
    for (c, mat, dn), f in FF:
        ns, waste = stock_pack(f['cuts'])
        el, fl, gk, sb = pipe_fit(c)
        out.append(dict(family=ids[(c, mat, dn)], cls=c, material=mat, DN=dn, pipe_m=round(f['m'], 1), lines=f['lines'],
                        stock_lengths_6m=ns, offcut_m=round(waste / 1000, 1), elbows_90=f['el'], elbow_std=el,
                        flanges=f['fl'], flange_std=fl, gaskets=f['gk'], stud_bolts=f['sb'],
                        stud_size='/'.join(sorted(f['studs'])), joints=f['jt'],
                        joint_type='/'.join(sorted(f['jtype']))))
    return out, sum(r['pipe_m'] for r in R)


# ---- X-INV-02: the motor family designs (AQS-INV-005) ------------------------

IEC72 = {'63': (63, 11, 23, 100, 80, 7), '71': (71, 14, 30, 112, 90, 7), '80': (80, 19, 40, 125, 100, 10),
         '90S': (90, 24, 50, 140, 100, 10), '90L': (90, 24, 50, 140, 125, 10), '100L': (100, 28, 60, 160, 140, 12),
         '112M': (112, 28, 60, 190, 140, 12), '132M': (132, 38, 80, 216, 178, 12), '180M': (180, 48, 110, 279, 241, 15),
         '200L': (200, 55, 110, 318, 305, 19), '225S': (225, 60, 140, 356, 286, 19),
         '250M': (250, 65, 140, 406, 349, 24), '280S': (280, 75, 140, 457, 368, 24),
         '280M': (280, 75, 140, 457, 419, 24), '315S': (315, 80, 170, 508, 406, 28),
         '315M': (315, 80, 170, 508, 457, 28), '315L': (315, 80, 170, 508, 508, 28),
         '355M': (355, 95, 170, 610, 560, 28), '355L': (355, 95, 170, 610, 630, 28)}   # H, D, E, A, B, K mm [IEC 60072-1]
IE3_60 = {   # IEC 60034-30-1:2025 Table for 60 Hz IE3 (kW: 2-pole, 4-pole) [IEC60034_30_1]
    float('0.12'): (float('62.0'), float('66.0')), float('0.18'): (float('65.6'), float('69.5')),
    float('0.25'): (float('69.5'), float('73.4')), float('0.37'): (float('73.4'), float('78.2')),
    float('0.55'): (float('76.8'), float('81.1')), float('0.75'): (float('77.0'), float('83.5')),
    float('1.1'): (float('84.0'), float('86.5')), float('1.5'): (float('85.5'), float('86.5')),
    float('2.2'): (float('86.5'), float('89.5')), float('3.7'): (float('88.5'), float('89.5')),
    float('5.5'): (float('89.5'), float('91.7')), float('7.5'): (float('90.2'), float('91.7')),
    float('11'): (float('91.0'), float('92.4')), float('15'): (float('91.0'), float('93.0')),
    float('18.5'): (float('91.7'), float('93.6')), float('22'): (float('91.7'), float('93.6')),
    float('30'): (float('92.4'), float('93.6')), float('37'): (float('92.9'), float('94.0')),
    float('45'): (float('93.1'), float('94.2')), float('55'): (float('93.5'), float('94.4')),
    float('75'): (float('93.9'), float('94.6')), float('90'): (float('94.0'), float('94.9')),
    float('110'): (float('94.4'), float('95.0')), float('132'): (float('94.7'), float('95.4')),
    float('160'): (float('95.0'), float('95.4')), float('200'): (float('95.4'), float('95.8')),
    float('250'): (float('95.8'), float('96.0'))}
AWG = tuple((n, flo('0.012668') * 92 ** ((36 - n) / flo('19.5')) ** 2) for n in range(8, 41))   # mm^2, ASTM B258
BRG = {'63': '6201-2Z', '71': '6202-2Z', '80': '6204-2Z', '90S': '6205-2Z', '90L': '6205-2Z', '100L': '6206-2Z',
       '112M': '6306-2Z', '132M': '6308-2Z', '180M': '6310-2Z', '200L': '6312-2Z', '225S': '6313-2Z',
       '250M': '6314-2Z', '280S': '6317-2Z', '280M': '6318-2Z', '315S': '6319-2Z', '315M': '6320-2Z',
       '315L': '6322-2Z', '355M': '6324-2Z', '355L': '6326-2Z'}   # ISO 15 deep-groove, drive end (X-INV-05 families)
B_D, KW_F, J_D, F_HZ = flo('0.75'), flo('0.92'), flo('5.0'), flo('60.0')
MAG = {'NdFeB': dict(Br=flo('1.30'), Hc=1000, rho=7500, lm=flo('3.0'),
                     grade='sintered N42, Br 1.29-1.32 T, Hcj >= 955 kA/m', RE=flo('0.31')),
       'ferrite': dict(Br=flo('0.27'), Hc=190, rho=3600, lm=flo('6.0'),
                       grade='anisotropic polymer-bonded Sr-ferrite, Br 0.25-0.29 T, HcB 180-200 kA/m', RE=flo('0.0'))}
GAP, MUR, LEAK, BSAT, PFE = flo('0.5'), flo('1.05'), flo('0.9'), flo('0.8'), flo('0.05')
MAGNET_FAMILIES = ('MF-01', 'MF-02', 'MF-03', 'MF-22', 'MF-23')
PLAN = {
    'induction': ['The stator and rotor laminations are laser-cut, and later stamped, from M400-50A electrical steel (EN 10106) 0.5 mm thick, then stacked and welded or cleated',
                  'The stator is wound with Grade 2 enamelled copper round wire (IEC 60317-13, class 200) from the plant wire line, as a single-layer concentric winding with a class F insulation system (IEC 60085) and NMN slot liners (Nomex–Mylar–Nomex laminate)',
                  'The wound stator is vacuum-pressure impregnated (VPI) with polyester resin and cured',
                  'The rotor cage is die-cast in aluminium from the in-house melt and skewed by one slot pitch',
                  'The shaft is turned and ground from C45 steel (EN 10083-2), with a keyway to IEC 60072-1',
                  'The frame is cast aluminium (A356), or cast iron above frame IEC 132, and is machined and fitted with end shields. It gives IP55 protection (IEC 60034-5) and IC 411 fan cooling (IEC 60034-6)',
                  'Bearings are taken from the bearing families of task X-INV-05, and the rotor is balanced to grade G2.5 of ISO 21940-11',
                  'Each motor receives the routine tests of IEC 60034-1: winding resistance, no-load, locked rotor, and a high-voltage (hipot) test at 2U + 1000 V. The first article is also type-tested for efficiency (IEC 60034-2-1) and noise (IEC 60034-9)'],
    'hermetic': ['The stator and rotor are made as in the induction plan, without frame, shaft or fan, as a 2-pole motor. The winding varnish and lead insulation are compatible with the refrigerant and with POE (polyol ester) oil (UL 60335-2-34 and IEC 60335-2-34 Annex AA)',
                 'The motor is shrink-fitted into the compressor shell on the scroll compressor line (task X-MFG-35)',
                 'After the shell is welded, the motor receives a high-voltage test and an insulation resistance test, and a locked-rotor and thermal protector test to IEC 60335-2-34'],
    'BLDC': ['The stator uses 0.35 mm NO20 or M270-35A laminations (EN 10106) with 12 slots and concentrated coils on each tooth',
             'The rotor has 8 poles of surface magnets. NdFeB magnets need a supply of rare earths, which is a review item; bonded ferrite is the alternative, at about 0.4 of the torque density',
             'Commutation uses Hall sensors or sensorless back-EMF detection, with a driver from the BLDC driver family of task X-INV-05',
             'The flange follows NEMA ICS 16, and the housing is extruded aluminium',
             'Each motor is tested for back-EMF constant, no-load current and torque-speed curve, with a high-voltage test at 500 V + 2U'],
    'stepper': ['The motor is a 2-phase hybrid stepper with 1.8 degree steps: an 8-pole stator and a 50-tooth rotor with an axially magnetised NdFeB ring between two toothed caps',
                'The laminations are 0.35 mm thick (EN 10106), and the bifilar or unipolar windings are wound from the plant wire line',
                'The flange follows NEMA ICS 16',
                'Each motor is tested for holding torque, step accuracy (within 5 %), resistance and inductance'],
    'solenoid': ['The coil is wound with class H enamelled wire (IEC 60317-13) on a bobbin of glass-filled polyamide (PA66-GF), with the 22 mm interface of ISO 15218',
                 'The plunger and frame are ferritic stainless steel 430F',
                 'The coil is encapsulated in epoxy and fitted with a DIN EN 175301-803 connector',
                 'Each solenoid is tested for coil resistance, pull-in at 85 % of rated voltage, and insulation at 1000 V'],
    'ec_fan': ['The fan and its EC motor are taken from the nameplate or datasheet of the selected heat-pump condenser fan (A-M-332). An in-house motor design is deferred until the fan is selected',
               'Each fan is tested for input power, speed range and response to the speed command at rated airflow, against the datasheet'],
    'actuator': ['A BLDC motor of family MF-01 drives a worm gear with a bronze wheel and a steel worm',
                 'The output is the square drive of ISO 5211 F03, with end stops and position switches',
                 'The housing is glass-filled polyamide (PA66-GF) or aluminium, with IP67 protection',
                 'Each actuator is tested for breakaway torque at the ISO 5211 F03 rating and for travel time, and a sample is tested for cycle life']}


IE3_FLOOR = min(IE3_60)                                   # the smallest rated output of the 60 Hz IE3 table


def ie3_eff(kw, p):
    """The v1 motor_designs.ie3(): the IE3 60 Hz target with linear interpolation."""
    k = sorted(IE3_60)
    c = 0 if p == 1 else 1
    if kw in IE3_60:
        return IE3_60[kw][c]
    lo = max(x for x in k if x <= kw)
    hi = min(x for x in k if x >= kw)
    return IE3_60[lo][c] + (IE3_60[hi][c] - IE3_60[lo][c]) * (kw - lo) / (hi - lo)


def awg_pick(a):
    """The v1 motor_designs.awg(): the conductor size for a wire area."""
    return next((f'{n} AWG ({s:.3f} mm2)' for n, s in reversed(AWG) if s >= a), f'{a:.2f} mm2 (parallel strands)')


def induction_design(kw, V, p, frame=None):
    """The v1 motor_designs.induction(): the output-equation sizing (PYRHONEN2014)
    with the Rev B slot-and-yoke fit (A-M-218)."""
    eta = ie3_eff(kw, p) / 100
    pf = flo('0.80') if kw < 4 else flo('0.84')
    A = flo('20e3') if kw < 1 else flo('30e3') if kw < 10 else flo('40e3')
    ns = F_HZ / p
    S = kw * flo('1e3') / (eta * pf)
    C = math.pi ** 2 / math.sqrt(2) * KW_F * B_D * A
    chi = math.pi / (4 * p) * math.sqrt(p)
    sp = flo('0.55') if p == 2 else flo('0.5')
    Dg = (S / (C * ns * chi)) ** (1 / 3)
    Dout = Dg / sp
    held = False
    if frame in IEC72 and Dout > flo('0.85') * 2 * IEC72[frame][0] / flo('1e3'):
        Dout = flo('0.85') * 2 * IEC72[frame][0] / flo('1e3')
        Dg = sp * Dout
        held = True
    L = S / (C * ns * Dg ** 2)
    tau = math.pi * Dg / (2 * p)
    Phi = 2 / math.pi * B_D * tau * L
    Vph = V / math.sqrt(3)
    N = flo('0.95') * Vph / (flo('4.44') * F_HZ * KW_F * Phi)
    I = S / (math.sqrt(3) * V)
    a = I / J_D
    Qs = 24 if (frame or '90')[:2] in ('63', '71', '80') else 36
    Qr = 22 if Qs == 24 else 28
    lengthened = flo('1.0')
    for _ in range(60):
        Phi = 2 / math.pi * B_D * tau * L
        N = flo('0.95') * Vph / (flo('4.44') * F_HZ * KW_F * Phi)
        aw = next((sz for n_, sz in reversed(AWG) if sz >= a), a)
        As = 2 * 3 * N / Qs * aw * flo('1.15') / flo('0.40')
        ts = math.pi * Dg * flo('1e3') / Qs
        bt = B_D * ts / (flo('0.97') * flo('1.6'))
        b1 = ts - bt
        k = 2 * math.pi / Qs
        hs = (-b1 + math.sqrt(b1 ** 2 + 2 * k * As)) / k
        hy = Phi / (2 * flo('0.97') * L * flo('1.5')) * flo('1e3')
        gap = flo('0.18') + flo('0.006') * (kw * flo('1e3')) ** flo('0.4') if p > 1 \
            else flo('0.2') + flo('0.01') * (kw * flo('1e3')) ** flo('0.4')
        if Dg * flo('1e3') + gap + 2 * (hs + hy) <= Dout * flo('1e3'):
            break
        L *= flo('1.02')
        lengthened *= flo('1.02')
    m_fe = math.pi / 4 * (Dout ** 2 - (Dg * flo('0.33')) ** 2) * L * flo('0.97') * 7650 * flo('0.7')
    m_cu = 3 * N * 2 * (L + flo('1.2') * tau) * a * flo('1e-6') * 8960
    out = dict(eta=eta, pf=pf, A=A, Dg=Dg * flo('1e3'), L=L * flo('1e3'), Dout=Dout * flo('1e3'), N=round(N), I=I,
               cond=awg_pick(a), Qs=Qs, Qr=Qr, m_fe=m_fe, m_cu=m_cu, rpm=round(120 * F_HZ / (2 * p)))
    out['held'] = held
    out['LD'] = L / Dg
    out['slot_fit_L_factor'] = round(lengthened, 3)
    if frame in IEC72:
        out['fits'] = L / Dg <= flo('2.5')
    return out


def pm_design(kw, rpm, Dmax):
    """The v1 motor_designs.pm(): the BLDC torque equation (HENDERSHOT2010)."""
    T = kw * flo('1e3') / (rpm * 2 * math.pi / 60)
    A, B = flo('15e3'), flo('0.8')
    DL = T / (math.pi / 2 * A * B)
    Dg = min(Dmax * flo('0.5'), (DL / flo('1.0')) ** (1 / 3))
    L = DL / Dg ** 2
    return dict(T=T, Dg=Dg * flo('1e3'), L=L * flo('1e3'), A=A, B=B)


def bg_flux(mag):
    """The v1 motor_designs.bg(): the air-gap flux of the magnet circuit."""
    M = MAG[mag]
    return min(BSAT, LEAK * M['Br'] * M['lm'] / (M['lm'] + MUR * GAP))


def pm_variant(kw, rpm, flange, mag, A=flo('15e3'), J=flo('5.0')):
    """The v1 motor_designs.pm_variant(): the magnet-comparison variant sizing."""
    T = kw * flo('1e3') / (rpm * 2 * math.pi / 60)
    B = bg_flux(mag)
    DL = T / (math.pi / 2 * A * B)
    Dg = min(flange * flo('0.5e-3'), (DL / flo('1.0')) ** (1 / 3))
    L = DL / Dg ** 2
    lt = 2 * (L + flo('1.2') * math.pi * Dg / 8)
    Pcu = flo('1.72e-8') * (J * flo('1e6')) * A * math.pi * Dg * lt / 2
    eta = kw * flo('1e3') / (kw * flo('1e3') * (1 + PFE) + Pcu)
    mm = math.pi * Dg * MAG[mag]['lm'] * flo('1e-3') * L * MAG[mag]['rho']
    nxt = 'fits' if L * flo('1e3') <= flo('2.5') * flange else ('next flange (NEMA 23)' if flange < 57
                                                               else 'next flange (NEMA 34)' if flange < 86
                                                               else 'longer than 2.5 x flange: review')
    return dict(T=T * flo('1e3'), B=B, D=Dg * flo('1e3'), L=L * flo('1e3'), eta=eta, mag_g=mm * flo('1e3'),
                RE_g=mm * flo('1e3') * MAG[mag]['RE'], frame=nxt)


def magnet_rows(fam_rows):
    """The v1 motor_designs.magnets(): the NdFeB-vs-ferrite comparison rows for
    the magnet-bearing families (X-INV-02D)."""
    out = []
    for f in fam_rows:
        if f['family'] not in MAGNET_FAMILIES:
            continue
        n = int(f['count'])
        per = float(f['installed_shaft_kW']) / n
        if f['family'] == 'MF-03':
            host = [x for x in fam_rows if x['family'] == 'MF-01'][0]
            per, fl, rpm = float(host['installed_shaft_kW']) / int(host['count']), 42, 3000
        else:
            fl = 42 if '42' in f['size'] else 57 if '57' in f['size'] else 86
            rpm = 3000 if f['motor_type'].startswith('BLDC') else 600
        for mag in ('NdFeB', 'ferrite'):
            d = pm_variant(per, rpm, fl, mag)
            out.append(dict(family=f['family'], magnet=mag, count=n, torque_mNm=round(d['T'], 1), Bg_T=round(d['B'], 2),
                            D_mm=round(d['D'], 1), L_mm=round(d['L'], 1), frame=d['frame'],
                            eta=round(d['eta'] * 100, 1), magnet_g=round(d['mag_g'], 1), RE_g=round(d['RE_g'], 1),
                            fleet_magnet_kg=round(d['mag_g'] * n / 1000, 2),
                            fleet_RE_kg=round(d['RE_g'] * n / 1000, 2)))
    return out


def motor_design_books(fam_rows):
    """The v1 motor_designs.main() computational half over the family rollup
    rows (the doc templates are the renderer lane's): the per-family design
    rows (the MOTOR_DESIGNS.csv book, one row per family) and the magnet
    comparison rows. fam_rows: the MOTOR_FAMILIES.csv-shaped dicts."""
    rows = []
    for f in fam_rows:
        t, sz, V = f['motor_type'], f['size'], f['voltage']
        fid = f['family']
        Vn = float(re.match(r'(\d+)', V).group(1))
        kw_m = re.search(r'([\d.]+) kW', sz)
        if (t.startswith('induction') or t.startswith('hermetic')) and kw_m \
                and float(kw_m.group(1)) < IE3_FLOOR:
            # a degraded census can carry a family below the smallest rating of
            # the IE3 60 Hz table (the committed tree has none): the output
            # equation has no efficiency target there, so the design is not
            # sized (the '-' face every non-sized type carries; loud by its
            # rating, never an invented efficiency)
            rows.append(dict(family=fid, type=t, rating=sz, Dg_mm='-', L_mm='-', Dout_mm='-', turns='-',
                             current_A='-', conductor='-', steel_kg='-', copper_kg='-', fits='-'))
            continue
        if t.startswith('induction') or t.startswith('hermetic'):
            kw = float(re.search(r'([\d.]+) kW', sz).group(1))
            fr = re.search(r'IEC (\d+[SLM]?)', sz)
            fr = fr.group(1) if fr else None
            p = 2 if t.startswith('induction') else 1
            d = induction_design(kw, Vn, p, fr)
            rows.append(dict(family=fid, type=t, rating=sz, Dg_mm=round(d['Dg']), L_mm=round(d['L']),
                             Dout_mm=round(d['Dout']), turns=d['N'], current_A=round(d['I'], 2), conductor=d['cond'],
                             steel_kg=round(d['m_fe'], 1), copper_kg=round(d['m_cu'], 2), fits=d.get('fits', '-')))
        elif t.startswith('BLDC') and 'actuator' not in t:
            per = float(f['installed_shaft_kW']) / int(f['count'])
            fl = 42 if '42' in sz else 57
            d = pm_design(per, 3000, fl / 1000)
            rows.append(dict(family=fid, type=t, rating=sz, Dg_mm=round(d['Dg'], 1), L_mm=round(d['L'], 1), Dout_mm=fl,
                             turns='-', current_A=round(per / Vn / flo('0.8'), 3), conductor='-', steel_kg='-', copper_kg='-',
                             fits=d['L'] < 3 * fl))
        elif t.startswith('stepper'):
            fl = 57 if '57' in sz else 86
            per = float(f['installed_shaft_kW']) / int(f['count'])
            rows.append(dict(family=fid, type=t, rating=sz, Dg_mm='-', L_mm='-', Dout_mm=fl, turns='-', current_A='-',
                             conductor='-', steel_kg='-', copper_kg='-', fits='-'))
        elif t.startswith('EC '):
            rows.append(dict(family=fid, type=t, rating=sz, Dg_mm='-', L_mm='-', Dout_mm='-', turns='-', current_A='-',
                             conductor='-', steel_kg='-', copper_kg='-', fits='-'))
        elif t.startswith('solenoid'):
            per = float(f['installed_shaft_kW']) * flo('1e3') / int(f['count'])
            rows.append(dict(family=fid, type=t, rating=sz, Dg_mm='-', L_mm='-', Dout_mm=22, turns='-',
                             current_A=round(per / Vn, 2), conductor='-', steel_kg='-', copper_kg='-', fits='-'))
        else:
            rows.append(dict(family=fid, type=t, rating=sz, Dg_mm='-', L_mm='-', Dout_mm='-', turns='-', current_A='-',
                             conductor='-', steel_kg='-', copper_kg='-', fits='-'))
    return rows, magnet_rows(fam_rows)


# ---- X-INV-03: the wire census (AQS-INV-002; ledger section D row) -----------

AMP = (('14 AWG', 15), ('12 AWG', 20), ('10 AWG', 30), ('8 AWG', 50), ('6 AWG', 65), ('4 AWG', 85), ('3 AWG', 100),
       ('2 AWG', 115), ('1 AWG', 130), ('1/0 AWG', 150), ('2/0 AWG', 175), ('3/0 AWG', 200), ('4/0 AWG', 230),
       ('250 kcmil', 255), ('300 kcmil', 285), ('350 kcmil', 310), ('400 kcmil', 335), ('500 kcmil', 380),
       ('600 kcmil', 420))                                # NEC 310.16 75 C Cu; 240.4(D)
EGC = ((15, '14 AWG'), (20, '12 AWG'), (60, '10 AWG'), (100, '8 AWG'), (200, '6 AWG'), (300, '4 AWG'),
       (400, '3 AWG'), (500, '2 AWG'), (600, '1 AWG'), (800, '1/0 AWG'), (1000, '2/0 AWG'), (1200, '3/0 AWG'))
FLC460 = ((flo('0.5'), flo('1.1')), (flo('0.75'), flo('1.6')), (1, flo('2.1')), (flo('1.5'), flo('3.0')),
          (2, flo('3.4')), (3, flo('4.8')), (5, flo('7.6')), (flo('7.5'), 11), (10, 14), (15, 21), (20, 27),
          (25, 34), (30, 40), (40, 52), (50, 65))         # NEC Table 430.250
FLC208 = ((flo('0.5'), flo('2.4')), (flo('0.75'), flo('3.5')), (1, flo('4.6')), (flo('1.5'), flo('6.6')),
          (2, flo('7.5')), (3, flo('10.6')), (5, flo('16.7')), (flo('7.5'), flo('24.2')), (10, flo('30.8')))
OCPD = (15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100, 110, 125, 150, 175, 200, 225, 250, 300, 350, 400, 450,
        500, 600, 700, 800, 1000)
RKM = {'14 AWG': flo('10.3'), '12 AWG': flo('6.33'), '10 AWG': flo('3.97'), '8 AWG': flo('2.51'), '6 AWG': flo('1.61'),
       '4 AWG': flo('1.01'), '3 AWG': flo('0.804'), '2 AWG': flo('0.636'), '1 AWG': flo('0.505'),
       '1/0 AWG': flo('0.400'), '2/0 AWG': flo('0.317'), '3/0 AWG': flo('0.251'), '4/0 AWG': flo('0.199'),
       '250 kcmil': flo('0.169'), '300 kcmil': flo('0.141'), '350 kcmil': flo('0.120'), '400 kcmil': flo('0.105'),
       '500 kcmil': flo('0.0847'), '600 kcmil': flo('0.0702')}   # ohm/km, NEC Ch. 9 Table 8 uncoated Cu
WIRE_SIZES = tuple(s for s, _ in AMP)
CUKG = {'18 AWG': flo('0.823'), '16 AWG': flo('1.31'), '14 AWG': flo('2.08'), '12 AWG': flo('3.31'),
        '10 AWG': flo('5.26'), '8 AWG': flo('8.37'), '6 AWG': flo('13.3'), '4 AWG': flo('21.2'), '3 AWG': flo('26.7'),
        '2 AWG': flo('33.6'), '1 AWG': flo('42.4'), '1/0 AWG': flo('53.5'), '2/0 AWG': flo('67.4'),
        '3/0 AWG': flo('85.0'), '4/0 AWG': 107, '250 kcmil': 127, '300 kcmil': 152, '350 kcmil': 177,
        '400 kcmil': 203, '500 kcmil': 253, '600 kcmil': 304}   # mm2
LOCAL = True                                              # X-ELS-02A: branch circuits from a local panel per sector
INV_KW = 60                                               # nameplate kW per inverter (the collection-bus basis)
INV_AMPS_BASIS = flo('72.2')                              # the NEC 705.28 basis amps the v1 basis text cites
MV_SIZE = '2 AWG'                                         # minimum practical 15 kV size


def wire_cond(I):
    """The v1 wire.cond(): the conductor for an ampacity."""
    return next(s for s, a in AMP if a >= I)


def wire_egc(ocpd):
    """The v1 wire.egc(): the EGC size for an OCPD rating."""
    return next(s for a, s in EGC if a >= ocpd)


def _vd(size, I, L, V):
    """The v1 wire.vd(): % three-phase voltage drop, resistive only."""
    return math.sqrt(3) * I * L / 1000 * RKM[size] / V * 100


def wire_upsize(size, I, L, V, lim):
    """The v1 wire.upsize(): walk the ladder until the drop holds."""
    i = WIRE_SIZES.index(size)
    while _vd(WIRE_SIZES[i], I, L, V) > lim and i < len(WIRE_SIZES) - 1:
        i += 1
    return WIRE_SIZES[i]


def wire_cu_kg(R):
    """The v1 wire.cu_kg(): the copper mass the panel merge trades."""
    return sum(r['total_m'] * CUKG.get(r['size'], 0) * flo('8.96e-3') for r in R)


def _wire_vd_ok(R):
    """The v1 wire.vd_ok(): no upsized circuit or feeder on the top rung."""
    return all(r['size'] != WIRE_SIZES[-1] for r in R if 'upsized' in r['basis'] or r['circuit'].startswith('panel feeder'))


def _wire_rows(m, inputs, mot, local=LOCAL, pmap=None):
    """The v1 wire.rows(): every circuit by sector > sub-system > unit. mot: the
    AQS-INV-001 rows (in memory -- the v1 read of MOTOR_INVENTORY.csv);
    positions and the grounding study travel as payloads; the collection-bus
    CB- rows compose from the SOL_ARK_60K params.sections book (the power
    family's sections, the committed COLLECTION_BUS table's own basis)."""
    pmap = pmap if pmap is not None else {}
    host = lambda sec: pmap.get(sec, sec)
    N = _node_view(m)
    C = inputs.get('line_positions') or {}
    er = C.get('SOL_ARK_60K', ([0, 0, 0], ''))[0]
    man = lambda a, b: (abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])) / 1000
    PAN = {}
    if local:
        pts = {}
        for mm2 in mot:
            if mm2['unit'] in C:
                pts.setdefault(host(mm2['sector']), []).append(C[mm2['unit']][0])
        for sec, P in pts.items():
            PAN[sec] = [sorted(p[k] for p in P)[len(P) // 2] for k in range(3)]   # panel at the sector median point, A-M-122 Rev B

    def run(u, sec=None):
        c = C.get(u)
        if not c:
            return flo('30.0'), 'no position: 30 m (assumed)'
        p = c[0]
        if local and host(sec) in PAN:
            return man(p, PAN[host(sec)]) * flo('1.1') + 3, f'routed tray from panel LP-{host(sec)} (Manhattan x 1.1 + 3 m drop, assumed)'
        return man(p, er) * flo('1.2') + 5, 'Manhattan to the electrical room x 1.2 + 5 m (assumed)'
    load = {}
    R = []

    def add(sec, sub, unit, circ, ctype, size, ins, V, n, L, basis, qty=1):
        R.append(dict(sector=sec, subsystem=sub, unit=unit, circuit=circ, type=ctype, size=size, insulation=ins,
                      voltage_class=V, conductors=n, length_m=round(L, 1), qty=qty, total_m=round(n * L * qty, 1),
                      basis=basis))
    for mm2 in mot:
        q = int(mm2['qty'])
        kw = float(mm2['shaft_kW'])
        u = mm2['unit']
        L, lb = run(u, mm2['sector'])
        if mm2['voltage'].startswith(('480', '208')):
            hp = kw * flo('1.341') * flo('1.15')
            tbl = FLC460 if mm2['voltage'].startswith('480') else FLC208
            flc = next((a for h, a in tbl if h >= hp), None)
            if flc is None:
                flc = hp * 746 / (math.sqrt(3) * (460 if tbl is FLC460 else 208) * flo('0.85') * flo('0.9'))
            I = flo('1.25') * flc
            s = wire_cond(I)
            oc = next(o for o in OCPD if o >= flo('2.5') * flc)          # NEC 430.52 inverse-time breaker 250 %
            Vl = 460 if tbl is FLC460 else 208
            s0 = s
            s = wire_upsize(s, flc, L, Vl, flo('3.0'))
            load.setdefault(host(mm2['sector']), []).append((flc, q, Vl))
            if s != s0:
                lb += f'; upsized from {s0} for 3 % drop'
            add(mm2['sector'], mm2['subsystem'], u, f"{mm2['device']} feeder", 'power, 3 ph + EGC', s,
                'XHHW-2 Cu, 600 V, tray cable TC-ER', '600 V', 3, L, f'NEC 430.22: 1.25 x {flc:.1f} A FLC; {lb}', q)
            add(mm2['sector'], mm2['subsystem'], u, f"{mm2['device']} EGC", 'equipment ground', wire_egc(oc),
                'green XHHW-2 Cu', '600 V', 1, L, f'NEC 250.122 at {oc} A OCPD', q)
            add(mm2['sector'], mm2['subsystem'], u, f"{mm2['device']} control", 'control', '18 AWG',
                'TFFN 3-pair, shielded', '600 V', 6, L, 'start/stop, run, fault (assumed)', q)
        else:
            Lc = flo('10.0')
            add(mm2['sector'], mm2['subsystem'], u, f"{mm2['device']} power", 'DC power pair',
                '16 AWG' if kw < flo('0.06') else '14 AWG', 'TC-ER 2-cond', '600 V', 2, Lc,
                'from the local 24/48 V DC panel at the unit, 10 m (assumed)', q)
            add(mm2['sector'], mm2['subsystem'], u, f"{mm2['device']} signal", 'control', '18 AWG', 'shielded pair',
                '300 V', 2, Lc, 'speed/position feedback (assumed)', q)
    for sec, ld in load.items():                                        # panel feeders, NEC 430.24
        if not (local and sec in PAN):
            continue
        for Vl in (460, 208):
            fl = [f for f, q, v in ld for _ in range(q) if v == Vl]
            if not fl:
                continue
            I = flo('1.25') * max(fl) + sum(fl) - max(fl)
            L = man(PAN[sec], er) * flo('1.2') + 5
            ns = math.ceil(I / 380)
            s = wire_upsize(wire_cond(I / ns), I / ns, L, Vl, flo('2.0'))
            add(sec, 'distribution', f'LP-{sec}', f'panel feeder {Vl} V', 'power, 3 ph + EGC', s,
                'XHHW-2 Cu, tray cable TC-ER', '600 V', 4 * ns, L,
                f'NEC 430.24: {I:.1f} A in {ns} parallel set(s) (310.10(G)); drop <= 2 % feeder so branch 3 % keeps total under 5 %; Manhattan to the electrical room x 1.2 + 5 m')
    # collection bus and MV: the CB- rows composed from the power family's
    # sections book (the committed COLLECTION_BUS.md table's own basis)
    sec_book = (_node_view(m).get('SOL_ARK_60K') or {}).get('params', {}).get('sections') or {}
    for i, ninv in enumerate(sec_book.get('inverters', [])):
        name = f'CB-{i + 1}'
        br = sec_book.get('breaker_A', [])[i]
        add('ELEC', 'collection bus', name, 'inverter AC output to section bus', 'power, 3 ph',
            wire_cond(flo('1.25') * (INV_KW * flo('1e3')) / (math.sqrt(3) * 480)), 'XHHW-2 Cu', '600 V', 3, flo('25.0'),
            f'NEC 705.28: 1.25 x {INV_AMPS_BASIS:g} A; 25 m inverter to section board (assumed)', ninv)
        sets = 3 if br <= 1000 else 4
        add('ELEC', 'collection bus', name, f'section main to {name} transformer LV', 'power, 3 ph parallel',
            wire_cond(br / sets), 'XHHW-2 Cu', '600 V', 3 * sets, flo('15.0'),
            f'{sets} sets for {br} A main (NEC 310.10(G)); 15 m (assumed)')
        add('ELEC', 'collection bus', name, 'section EGC', 'equipment ground', wire_egc(br), 'green XHHW-2 Cu',
            '600 V', sets, flo('15.0'), 'NEC 250.122')
        add('ELEC', 'MV', name, 'transformer MV to the PCC switchgear', 'MV power, 3 ph', MV_SIZE,
            'MV-105 Cu, 133 % insulation, tape shield', '15 kV', 3, flo('100.0'),
            '34.7 A; minimum practical 15 kV size; 100 m (assumed)')
    # PV source circuits
    pv = N['PV_ARRAY']['params']
    nmod = pv['count']
    per = 18
    ns = math.ceil(nmod / per)
    add(N['PV_ARRAY']['sector_id'], 'roof array', 'PV_ARRAY', 'PV source circuit home run (+/-)', 'PV DC', '10 AWG',
        'PV Wire, UL 4703, 2 kV', '2000 V DC', 2, flo('60.0'),
        f'{nmod} modules / {per} per string (Voc x 1.1 < 1000 V, assumed) = {ns} strings; NEC 690.8 1.56 x Isc; '
        f'60 m mean home run (assumed)', ns)
    add(N['PV_ARRAY']['sector_id'], 'roof array', 'PV_ARRAY', 'array EGC', 'equipment ground', '10 AWG', 'bare Cu', '-',
        1, flo('60.0'), 'NEC 690.45 / 250.122', ns)
    # hall lighting
    h = N['EXT_HALL']['params']['hvac']
    inst = h['light_kW'] / flo('0.10')
    nc = math.ceil(inst / (flo('0.8') * 20 * 277 / flo('1000')))
    lsz = next(z for z in WIRE_SIZES[1:]
               if 2 * flo('16.0') * flo('120.0') / flo('1000') * RKM[z] / 277 * 100 <= flo('3.0'))   # X-ELS-06
    add(N['EXT_HALL']['sector_id'], 'hall', 'EXT_HALL', 'lighting branch circuit 277 V', 'power, 1 ph + N + EGC', lsz,
        'THHN/THWN-2 Cu in EMT', '600 V', 3, flo('120.0'),
        f'installed {inst:.0f} kW (average {h["light_kW"]} kW at 10 % lit) / 4.43 kW per 20 A circuit at 80 % (16 A); '
        f'120 m mean (assumed); {lsz} for 3 % drop (X-ELS-06)', nc)
    # grounding grid (the _grounding_study.py lengths; absent payload = the v1
    # failed-subprocess branch, no row)
    gs = inputs.get('grounding_grid')
    if gs:
        add('ELEC', 'grounding', 'GROUND_GRID', 'ring and mesh conductors', 'bare grounding', '4/0 AWG',
            'bare soft-drawn Cu', '-', 1, gs['ring_m'] + gs['mesh_m'],
            f"AQS-ELEC-005 ring {gs['ring_m']:.0f} m + mesh {gs['mesh_m']:.0f} m; 4/0 assumed (IEEE 80 conductor "
            'sizing at X-ELS)')
    return R


def wire_merge_panels(m, inputs, mot):
    """The v1 wire.merge_panels(): fold the panel with the least feeder copper
    into the host that minimises copper; a merge is accepted only if the total
    copper does not rise and every drop limit still holds without the top
    rung. Returns (pmap, log, rows)."""
    pmap = {}
    R = _wire_rows(m, inputs, mot, True, pmap)
    best = wire_cu_kg(R)
    log = []
    while True:
        pans = sorted({r['unit'][3:] for r in R if r['circuit'].startswith('panel feeder')},
                      key=lambda h: sum(r['total_m'] * CUKG.get(r['size'], 0) for r in R if r['unit'] == f'LP-{h}'))
        done = False
        for small in pans:
            trial = []
            for h in pans:
                if h == small:
                    continue
                pm = {k: (h if v == small else v) for k, v in pmap.items()}
                pm[small] = h
                Rt = _wire_rows(m, inputs, mot, True, pm)
                if _wire_vd_ok(Rt):
                    trial.append((wire_cu_kg(Rt), h, pm, Rt))
            if trial:
                c, h, pm, Rt = min(trial, key=lambda t: t[0])
                if c <= best + flo('1e-6'):
                    log.append((small, h, round(best, 1), round(c, 1)))
                    best, pmap, R = c, pm, Rt
                    done = True
                    break
                log.append((small, None, round(best, 1), round(c, 1)))
        if not done:
            return pmap, log, R


def wire_census(m, inputs, mot):
    """The AQS-INV-002 census: the merged-panel wire rows, sorted as the v1
    write() sorts. Returns (rows, pmap, log, pre-merge copper/panels,
    post-merge copper/panels) -- the merge book the document's section 0
    prints."""
    c0 = wire_cu_kg(_wire_rows(m, inputs, mot, True, {}))
    n0 = len({r['unit'] for r in _wire_rows(m, inputs, mot, True, {}) if r['circuit'].startswith('panel feeder')})
    pmap, log, R = wire_merge_panels(m, inputs, mot)
    R.sort(key=lambda r: (r['sector'], str(r['subsystem']), r['unit'], r['circuit']))
    return dict(rows=R, pmap=pmap, log=log, cu0=c0, pan0=n0,
                cu1=wire_cu_kg(R),
                pan1=len({r['unit'] for r in R if r['circuit'].startswith('panel feeder')}))


def wire_families(R, inputs):
    """The AQS-INV-002 family rollup: conductor families by
    (type head, size, insulation, voltage class), ids from the register
    payload. Returns (rows, total m, assumed m)."""
    F = {}
    for r in R:
        k = (r['type'].split(',')[0], r['size'], r['insulation'], r['voltage_class'])
        x = F.setdefault(k, [flo('0.0'), 0])
        x[0] += r['total_m']
        x[1] += r['qty']
    ids = assign_ids(inputs.get('family_registers') or {}, 'WF', ('type', 'size', 'insulation', 'voltage_class'),
                     [k for k, _ in sorted(F.items(), key=lambda kv: -kv[1][0])])
    FF = sorted(F.items(), key=lambda kv: id_number(ids[kv[0]]))
    out = [dict(family=ids[k], type=k[0], size=k[1], insulation=k[2], voltage_class=k[3], conductor_m=round(m),
                circuits=n) for k, (m, n) in FF]
    return out, sum(r['total_m'] for r in R), sum(r['total_m'] for r in R if 'assumed' in r['basis'])


# ---- X-INV-05: the other building blocks census (AQS-INV-004) ----------------

VALVE = {'M1': '316L ball valve, ASME B16.34 Cl 150, RF flanged',
         'M2': 'CS A216 WCB ball valve, ASME B16.34 Cl 150, RF flanged',
         'P1': 'PVC-U true-union ball valve, MSS SP-122, EPDM seals',
         'P2': 'CPVC true-union ball valve, MSS SP-122, FKM seals',
         'P3': 'PVDF ball valve, ISO 16135, PTFE seats', 'P4': 'PP-H ball valve, ISO 16135, EPDM seals',
         'P5': 'PP ball valve with HDPE stub ends, ISO 16135',
         'F1': 'PVC-lined ball valve in FRP service, ISO 16135'}
CHECK = {k: v.replace('ball valve', 'swing/ball check valve').replace(', MSS SP-122', '').replace('ISO 16135', 'ISO 16137')
         for k, v in VALVE.items()}
HOLD = {'tank', 'vessel', 'cut_tank', 'digest', 'reagent', 'separator', 'evaporator', 'scrubber', 'bmed', 'ew_cell',
        'treat', 'farm', 'dryer', 'recycle_pipe'}
BRG_OTHER = {'63': '6201-2Z', '71': '6202-2Z', '80': '6204-2Z', '90S': '6205-2Z', '90L': '6205-2Z',
             '100L': '6206-2Z', '112M': '6306-2Z', '132M': '6308-2Z', '160': '6309-2Z', '180M': '6310-2Z'}
PRESSURE_TOPS = (10, 16, 25, 40, 60, 100, 160, 250, 400)


def other_rows(m, inputs, mot, wire_R):
    """The AQS-INV-004 census rows: valves, instruments, electronics and
    protection, bearings, seals, supports, fasteners and fabricated parts.
    mot / wire_R: the AQS-INV-001/002 rows in memory (the v1 CSV reads)."""
    N = _node_view(m)
    blk = _blocks(m, inputs)
    R = []

    def add(u, cat, item, size, spec, qty, basis, sector=None, sub=None):
        if qty <= 0:
            return
        n = N.get(u, {})
        R.append(dict(sector=sector or n.get('sector_id') or 'MFG', subsystem=sub or blk.get(u) or n.get('class') or '-',
                      unit=u, category=cat, item=item, size=size, spec=spec, qty=qty, basis=basis))
    pumped = {mm2['unit'] for mm2 in mot if 'pump' in mm2['device'].lower()}
    iso = inputs.get('iso_sheets') or []
    sup = inputs.get('supports') or {}
    for s in iso:
        u = s['frm'] if s['frm'] in N else s['to']
        dn = f"DN{s['DN']}"
        c = s['cls']
        add(u, 'valve', 'isolation valve', dn, VALVE.get(c, VALVE['M1']), 2, f"{s['line']}: one at each end nozzle (assumed)")
        if u in pumped:
            add(u, 'valve', 'check valve', dn, CHECK.get(c, CHECK['M1']), 1, f"{s['line']}: pump discharge (assumed)")
            add(u, 'instrument', 'flow transmitter', dn, 'electromagnetic, PFA liner, Hastelloy C electrodes, ISO 20456',
                1, f"{s['line']}: pumped line (assumed)")
        ns = sup.get(s['line'], 0)
        if ns:
            metal = c.startswith('M')
            add(u, 'support', 'pipe clamp' if not metal else 'U-bolt with guide', dn,
                'PP clamp with EPDM liner, MSS SP-58 Type 7' if not metal else '316 U-bolt, MSS SP-58 Type 24', ns,
                f"{s['line']}: AQS-PIP-005 span count")
            add(u, 'fastener', 'anchor bolt', 'M10', 'ISO 3506 A4-70 wedge anchor', 2 * ns,
                f"{s['line']}: 2 per support (assumed)")
    LIQ_IN = {e['to_unit_id'] for e in _edges(m) if e['presence'] == 'present' and e.get('phase') == 'L'
              and (e['rate']['value'] or 0) > 0}
    nozzle_units = set(inputs.get('nozzle_units') or [])
    for u in N:
        n = N[u]
        if n.get('class') in ('boundary', 'header', 'relief') or u.startswith(('HDR_', 'RELIEF_')):
            continue
        if u in nozzle_units or (u in LIQ_IN and n.get('class') not in ('farm', 'product', 'building', 'hab')) \
                or n.get('class') in ('hcl_synthesis', 'pem_electrolyser'):   # HAZOP HZ: liquid units without a nozzle list too
            add(u, 'instrument', 'temperature element', 'Pt100 class A', 'IEC 60751, 316L thermowell', 1,
                'duty item 5 (assumed one per unit)')
            p = n.get('params') or {}
            dk = p.get('design_kPa') or 0
            need = flo('1.25') * dk / 100                   # X-CTL-01: range from the design pressure (AQS-CTL-001)
            top = next((x for x in PRESSURE_TOPS if x >= need), 400)
            add(u, 'instrument', 'pressure transmitter', f'0-{top} bar',
                'ceramic diaphragm, IEC 61298' if top <= 16 else '316L thin-film strain gauge, IEC 61298', 1,
                'duty item 5 (one per unit); range >= 1.25 x design pressure')
            if n.get('class') in HOLD or u in LIQ_IN:       # X-SAF-01 HZ: liquid-receiving units get level and high level
                add(u, 'instrument', 'level transmitter', 'radar 80 GHz', 'IEC 62828, PTFE lens', 1,
                    'duty item 5: liquid holdup')
                add(u, 'instrument', 'high-level switch', 'vibrating fork', 'IEC 60947-5, 316L', 1,
                    'duty item 5: high level trips the inlet')
    for r in (inputs.get('gas_detectors') or []):           # X-SAF-06 (AQS-SAF-006)
        add(r['unit'], 'instrument', f"gas detector, {r['gas']}", r['type'],
            f"alarm {r['alarm']}, trip {r['trip']}, {r['mounting']}", int(r['qty']), f"AQS-SAF-006 {r['voting']}")
    sif_rows = inputs.get('sif_list') or []
    if sif_rows:                                            # X-CTL-03: SIF hardware (AQS-CTL-003)
        for r in sif_rows:
            u = r['unit'] if r['unit'] in N else 'CONTROL'
            if 'TE-90' in r['initiator']:
                add(u, 'instrument', 'temperature element (SIF, independent)', 'Pt100 class A', 'IEC 60751, own thermowell',
                    1, f"{r['id']} SIL {r['SIL']}")
            if 'ESD' in r['final_element']:
                add(u, 'valve', 'ESD valve, spring-return actuator', 'DN15', '316L, fail-safe, IEC 61511', 2,
                    f"{r['id']} one per bank half")
        add('PLC', 'electronics', 'safety PLC (SIL 2 capable), CPU and I/O rack', '-', 'IEC 61508 / IEC 61511', 2,
            f'AQS-CTL-003: {len(sif_rows)} SIFs, redundant pair', sector='CONTROL', sub='SIS')
    for mm2 in mot:
        q = int(mm2['qty'])
        u = mm2['unit']
        mt = mm2['motor_type']
        sz = mm2['size']
        kw = float(mm2['shaft_kW'])
        if mt.startswith('induction'):
            fr = re.search(r'IEC (\d+[SLM]?)', sz)
            b = BRG_OTHER.get(fr.group(1) if fr else '', '6204-2Z') if fr else '6204-2Z'
            add(u, 'bearing', 'deep-groove ball bearing', b, 'ISO 15 / ISO 492 normal class, C3', 2 * q,
                f"{mm2['device']}: drive and non-drive end, IEC 60072 frame {fr.group(1) if fr else '?'} (assumed size)")
            add(u, 'electronics', 'variable-frequency drive' if kw >= flo('0.75') else 'motor starter (contactor + overload)',
                sz.split('/')[-1].strip(), 'IEC 61800-5-1' if kw >= flo('0.75') else 'IEC 60947-4-1', q,
                f"{mm2['device']} (assumed VFD at >= 0.75 kW)")
        elif mt.startswith('BLDC') or mt.startswith('stepper'):
            add(u, 'bearing', 'deep-groove ball bearing', '608-2Z' if mt.startswith('stepper') or kw < flo('0.1') else '6000-2Z',
                'ISO 15, normal class', 2 * q, f"{mm2['device']} (assumed size)")
            add(u, 'electronics', 'BLDC driver' if mt.startswith('BLDC') else 'stepper driver', '24/48 V DC',
                'IEC 61800-5-1', q, mm2['device'])
        elif mt.startswith('solenoid'):
            add(u, 'electronics', 'solenoid driver channel', '24 V DC', 'IEC 61131-2 DO', q, mm2['device'])
        elif mt.startswith('hermetic'):
            add(u, 'electronics', 'compressor contactor + overload', sz, 'IEC 60947-4-1', q, mm2['device'])
        d = mm2['device'].lower()
        if mt.startswith('induction') and 'pump' in d and not any(k in d for k in ('magnet', 'mag drive', 'peristaltic',
                                                                                                   'diaphragm', 'hermetic', 'canned')):
            add(u, 'seal', 'mechanical seal, single', 'EN 12756', 'SiC/SiC faces, FKM', q,
                f"{mm2['device']}: induction-driven pump assumed seal-type; BLDC pumps assumed magnetic drive")
        add(u, 'electronics', 'PLC digital I/O point', '24 V DC', 'IEC 61131-2', 2 * q,
            f"{mm2['device']}: run and fault (assumed)")
    for w in wire_R:
        mmn = re.search(r'at (\d+) A OCPD', w['basis'])
        if mmn and w['type'] == 'equipment ground':
            add(w['unit'], 'protection', 'inverse-time circuit breaker, 3-pole', f'{mmn.group(1)} A',
                'UL 489 / IEC 60947-2', int(w['qty']), 'NEC 430.52, from AQS-INV-002', w['sector'], w['subsystem'])
    for u, rows in sorted((inputs.get('mfg_fasteners') or {}).items()):
        for r in rows:
            add(u, 'fastener', r['size'].split(' with')[0], r['size'], r['grade'], int(float(r['qty'])),
                f'models/mfg/{u}/fasteners.csv')
    for u, bom in sorted((inputs.get('mfg_boms') or {}).items()):
        n = sum(1 for line in bom if line) - 1              # the v1 non-empty line count less the header
        add(u, 'fabricated part', 'fabricated part set', f'{n} BOM lines',
            f'models/mfg/{u}/bom.csv and WORK_ORDER.md', 1,
            'unit work order; bought-in lines in the set are counted again in their own inventory')
    io = sum(r['qty'] for r in R if r['category'] == 'instrument')
    add('PLC', 'electronics', 'PLC analog input point', '4-20 mA HART', 'IEC 61131-2', io, 'one per instrument',
        'CONTROL', 'PLC')
    nio = sum(r['qty'] for r in R if r['item'].startswith('PLC'))
    add('PLC', 'electronics', 'PLC I/O module, 16 channel', '24 V DC', 'IEC 61131-2', math.ceil(nio / 16),
        f'{nio} points / 16', 'CONTROL', 'PLC')
    R.sort(key=lambda r: (r['sector'], str(r['subsystem']), r['unit'], r['category'], r['item']))
    return R


def other_families(R, inputs):
    """The AQS-INV-004 family rollup: (category, item, spec) -> qty/sizes/units,
    ids from the register payload. Returns (rows, category counter, assumed)."""
    F = {}
    for r in R:
        k = (r['category'], r['item'], r['spec'] if r['category'] != 'fabricated part' else 'models/mfg/<unit>/bom.csv')
        x = F.setdefault(k, [0, {}, set()])
        x[0] += r['qty']
        x[1][r['size']] = x[1].get(r['size'], 0) + r['qty']
        x[2].add(r['unit'])
    ids = assign_ids(inputs.get('family_registers') or {}, 'OF', ('category', 'item', 'spec'),
                     [k for k, _ in sorted(F.items(), key=lambda kv: (kv[0][0], -kv[1][0]))])
    FF = sorted(F.items(), key=lambda kv: id_number(ids[kv[0]]))
    out = [dict(family=ids[(c, it, sp)], category=c, item=it, spec=sp, qty=q,
                sizes='; '.join(f'{s} x{n}' for s, n in sorted(cnt.items(), key=lambda kv: -kv[1])),
                units=len(us)) for (c, it, sp), (q, cnt, us) in FF]
    C = {}
    for r in R:
        C[r['category']] = C.get(r['category'], 0) + r['qty']
    a = sum(r['qty'] for r in R if 'assumed' in r['basis'])
    return out, C, a

"""Production route sheets for the units missing docs-authority/fab/<UNIT>.md (unit task 13).

The house fab format was established by commit 3e6ac9b (one sheet per unit) and re-grounded
by the X-MFG-31 lane (fab routes for the six feed-blocked reaction chambers, grounded in duty
sections, graph design rows and nozzles). 46 roster units never got a sheet - exactly the set
whose duty sheets arrived later or whose design state is standby/pending. This generator
issues those sheets in the house format from issued registers only:

  - envelope and service: the unit's own duty sheet (section 1 basis, section 2 size, the
    graph design row) - quoted, not recomputed;
  - internals line: AQS-DSN-INT-001 (inventory/INTERNALS.json) disposition;
  - material line: the duty section 3 status verbatim - pending stays pending on the sheet;
  - nozzles: the unit's nozzle schedule (docs-authority/nozzles/<u>.csv) where it exists;
  - the fabrication hold rule: the route is issued for planning; fabrication does not start
    before unit tasks 10-12 close (CAD accepted, real BOM) and, where named, the section 3
    material selection lands.

Nothing here sizes anything. Run: python3 docs-authority/_fab_routes.py
"""
import csv, glob, json, os, re

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(R)

g = json.load(open('flow_graph/plant_flow_graph.json'))
N = {n['unit_id']: n for n in g['nodes']}
UNITS = sorted(n['unit_id'] for n in g['nodes'] if n.get('class') != 'boundary' and n.get('sector_id'))
missing = []
for u in UNITS:
    f = f'docs-authority/fab/{u}.md'
    if not os.path.exists(f):
        missing.append(u)
    elif open(f).read().startswith(f'# {u} fabrication\n\nClass: '):
        missing.append(u)   # this generator owns the sheet; regenerate in place

IN = json.load(open('docs-authority/inventory/INTERNALS.json')) if os.path.exists('docs-authority/inventory/INTERNALS.json') else {}
DISP = {}
DISP.update(IN.get('defined', {}))
DISP.update({u: 'none with basis: ' + w for u, w in IN.get('none', {}).items()})
DISP.update({u: 'open: ' + w for u, w in IN.get('open', {}).items()})

# route skeleton per graph class bucket: step 1 is the assembly route, step 2 the working
# parts, step 3 the connections, step 4 the test. Wording cites the register it rests on.
def route_for(u, cls, mat_pending):
    cell = cls in ('cell', 'furnace', 'caster', 'separator', 'cru')
    tool = cls in ('former', 'forming', 'mill', 'press', 'prep', 'coater', 'tool', 'intra',
                   'aligner', 'wet_bench', 'hydro', 'skid', 'skid2', 'digest', 'reactor',
                   'kettle', 'ferment', 'evaporator')
    if cell:
        a = 'Shell and hearth: plate or welded vessel per the section 3 material once selected; hot- or wet-face hardware is the AQS-STD-002 family material of the streams it touches'
        b = 'Working parts: the electrode/hearth/bottle hardware named on the sizing and duty sheets; electrode arrays stay per the internals register disposition below'
    elif tool:
        a = 'Machine build: welded frame plus standard drivetrain parts; sheet, plate and bar stock bought to the family standards (AQS-INV-004/006/007 desk packages)'
        b = 'Tooling and working parts per the duty sheet size line; the full part set is the unit task 10-12 deliverables (CadQuery model, real BOM)'
    elif cls in ('tank', 'cut_tank', 'store', 'product', 'reagent', 'dose', 'feed', 'hopper'):
        a = 'Shell route: welded plate or polymer vessel per the duty sheet, no agitation internals (internals register below)'
        b = 'Fittings: nozzles, manway and supports to the nozzle schedule and the duty sheet'
    elif cls in ('ahu', 'cool', 'dry_cooler', 'hx', 'heat_pump', 'orc', 'adsorption_chiller', 'dryer'):
        a = 'Machine build: frame, coil/air side and standard rotating parts; no contacting process internals (internals register below)'
        b = 'Connections and coil/media side per the duty sheet and nozzle schedule'
    else:
        a = 'Assembly route: per the unit duty sheet size line, standard first-stage parts'
        b = 'Working parts per the duty sheet; the part set is the unit task 10-12 deliverables'
    if cls == 'building' or cls == None:
        a = 'Civil build: portal frames, roof and wall panels on the grid the duty sheet states (loads per X-PAR-08); no process internals'
        b = 'Enclosure fitout per the duty sheet; nothing fabricated that the enclosure scope (X-BLD) already sizes'
    return a, b

for u in missing:
    n = N[u]; cls = n['class']
    d = open(f'docs-authority/duties/{u}.md').read()
    m = re.search(r'Envelope ([\d.,]+)\u00d7([\d.,]+)\u00d7([\d.,]+) mm, ([\d.]+) m3|Envelope ([\d.,]+)x([\d.,]+)x([\d.,]+) mm, ([\d.]+) m', d)
    env = None
    me = re.search(r'Envelope ([\d.,]+)\u00d7([\d.,]+)\u00d7([\d.,]+)\s?mm', d)
    if me: env = me.group(0)
    basis = ''
    mb = re.search(r'Graph design \(AQS-PAR-001 sizing\): (.*)', d)
    if mb: basis = re.sub(r'\s+', ' ', mb.group(1))[:140]
    m3 = re.search(r'3\. Material\. (.*)', d)
    mat = re.sub(r'\s+', ' ', m3.group(1))[:220] if m3 else 'see duty sheet section 3'
    mat_pending = 'pending' in mat.lower() or 'not chosen' in mat.lower()
    disp = DISP.get(u, 'internals register entry pending (AQS-DSN-INT-001)')
    nzf = f'docs-authority/nozzles/{u}.csv'
    nzrows = list(csv.DictReader(open(nzf))) if os.path.exists(nzf) else []
    a, b = route_for(u, cls, mat_pending)
    L = [f'# {u} fabrication', '',
         f'Class: {cls or "unclassed"}; sector {n.get("sector_id") or "-"}. Study route. Not stamped.',
         f'Envelope: {env or "not booked on the duty sheet - the physical build size is the unit task 10-11 scope"};',
         f'service line: {basis or "see the duty sheet section 1 basis"}', '',
         f'Internals: {disp}', f'Material: {mat}', '',
         f'Nozzles: {len(nzrows)} process connections per docs-authority/nozzles/{u}.csv' if nzrows
         else 'Nozzles: none scheduled yet (unit task 04); route carries the connections once scheduled', '',
         'Production route (issued ahead of the CAD build; fabrication does not start before unit',
         'tasks 10-12 close and, where named, the section 3 material selection lands):',
         f'1. {a}.',
         f'2. {b}.',
         '3. Connections: nozzle stubs to the schedule; flange faces per AQS-PIP-003 class letters' if nzrows
         else '3. Connections: per the scheduled nozzles when they exist; nothing invented here.',
         '4. Test: hydrostatic/water-fill and pressure hold per AQS-STD-001 section 4; dry-run only until',
         '    the CAD acceptance (AQS-PLAN-006 M3) and the real BOM land.',
         '']
    open(f'docs-authority/fab/{u}.md', 'w').write('\n'.join(L))
print(len(missing), 'route sheets issued:', ', '.join(missing))

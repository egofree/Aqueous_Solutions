"""engine v2: the declared input payload.

One builder for the payload every solve, check, update and renderer consumes:
the drivers, the baseline site profile, and every declared auxiliary data
file (AUXILIARY rows: key, loader). Families name the payload keys they
read; the loaders here are the single I/O boundary — data files are
declared, never opened ad hoc inside solve or render functions. Loading
happens once per process: callers load and pass the payload down.

The auxiliary faces are the committed files the v1 stage scripts read
(cross-stage map 1 of the migration ledger, the hidden-dependency rows and
the soft-dependency table, each declared here at the engine's I/O
boundary): the placement seed, report, study and blocks; the ISO_SHEETS
sidecar, the SUPPORTS span table and the piping classes; the instrument,
motor and other-inventory census CSVs; the mfg and unit BOM trees; the
family-id registers; the nozzle schedules and their unit roster; the
cause/effect column and the gas-detector and SIF lists; the duty-sheet
material and relief sections; the MFG_TOOLS tool table; the grounding-grid
study print; the system tree; the two cited front-matter document numbers;
the drawing SVG/STEP inventory. graph_sha256 is the committed graph file's
SHA-256 — the v1 file read the renderers that cite the graph provenance
inherit; update() re-pins it after the graph write so the documents
describe the graph as written.

Manifest tracking (manifest.extra_input_paths via auxiliary_files) covers
the static files; the drawing SVG/STEP inventory is not hash-tracked
because the renderer byte comparison against the committed document is
strictly stronger than an input hash of the same bytes.
"""
import collections, csv, glob, hashlib, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

GRAPH_FILE = 'flow_graph/plant_flow_graph.json'


def _read_json(path):
    with open(os.path.join(ROOT, path), encoding='utf-8') as f:
        return json.load(f)


def _rd(path):
    with open(os.path.join(ROOT, path), encoding='utf-8') as f:
        return f.read()


def _read_csv_rows(path):
    """A CSV as a list of dicts (string values), header-keyed."""
    with open(os.path.join(ROOT, path), encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def _read_csv_cells(path):
    """A CSV as raw rows (the header row first), the BOM-rollup face."""
    with open(os.path.join(ROOT, path), encoding='utf-8', newline='') as f:
        return [r for r in csv.reader(f)]


def _glob_map(pattern, loader, key_from_path):
    """{key: loader(path)} over a glob, in sorted path order (the v1 files()
    faces)."""
    return {key_from_path(p): loader(p) for p in sorted(glob.glob(os.path.join(ROOT, pattern)))}


def load(extra=()):
    """The canonical payload: drivers, site_profile, and every declared
    auxiliary file. extra: (key, value) pairs a caller adds (e.g. a site
    profile variant for a locale check); an extra key replaces the declared
    loader result."""
    payload = {
        'drivers': _read_json('flow_graph/param/drivers.json'),
        'site_profile': _read_json('flow_graph/param/sites/baseline.json'),
    }
    for key, loader in AUXILIARY:
        payload[key] = loader()
    for key, value in extra:
        payload[key] = value
    return payload


def drawing_payload():
    """The (drawing_svgs, drawing_steps) pair, loaded on demand: the two
    registry keys whose source is the committed CAD lane output (hundreds of
    files). The canonical load() omits them so a solve or check that renders
    no drawing-stamped document pays nothing; update() and the callers that
    render the pid/drawings documents add them."""
    svgs, steps = _drawing_inventory()
    return (('drawing_svgs', svgs), ('drawing_steps', steps))


# ---- the declared auxiliary faces (the v1 stage file reads) --------------------

def _graph_sha256():
    with open(os.path.join(ROOT, GRAPH_FILE), 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def _placement_seed():
    return _read_json('flow_graph/placement_seed.json')


def _line_positions():
    """The unit-centre namespace C the line-list family consumes:
    docs-authority/_line_list.py's module-level dict, rebuilt from the
    committed files it reads — duty origins, placement report moves, study
    rows, seed units, the GA relocates, the CAD moves, the riding exchanger,
    then the block centres (the v1 build order; the inventory family declares
    the same payload key)."""
    seed = _placement_seed()
    st = _read_json('flow_graph/placement_study.json')
    C = {}
    for u, o in _read_json('docs-authority/duties/_origins.json')['origins'].items():
        C[u] = ([o['origin_mm'][i] + o['size_mm'][i] / 2 for i in range(3)], 'duty origin')
    pr = _read_json('flow_graph/placement_report.json')
    for r in pr.get('moves', []) + pr.get('create_moves', []):
        o, z = r.get('origin_mm'), r.get('size_mm')
        if o and z and len(o) == 3 and len(z) >= 2:
            z = list(z) + [0] * (3 - len(z))
            C.setdefault(r['unit_id'], ([o[i] + z[i] / 2 for i in range(3)], 'placement_report'))
    for r in st['units']:
        o, z = r['origin_mm'], r['size_mm']
        C.setdefault(r['unit_id'], ([o[i] + z[i] / 2 for i in range(3)], 'placement_study (STUDY)'))
    LV = {'L-1': -6000, 'L0': 0, 'L1': 6000}
    for r in seed['units']:
        o, z = r.get('origin_mm'), r.get('size_mm')
        if o and z and len(z) >= 2:
            o = list(o) + [LV.get(r.get('level'), 0)] * (3 - len(o))
            z = list(z) + [0] * (3 - len(z))
            C.setdefault(r['unit_id'], ([o[i] + z[i] / 2 for i in range(3)], 'placement_seed'))
    sys.path.insert(0, os.path.join(ROOT, 'models/freecad'))
    try:
        import params as _FP
        for _u, (_cx, _cy) in getattr(_FP, 'RELOCATE', {}).items():
            if _u in C:
                C[_u] = ([_cx, _cy, C[_u][0][2]], C[_u][1] + ' + GA relocate')
    except Exception:
        pass
    if os.path.exists(os.path.join(ROOT, 'docs-authority/inventory/CAD_MOVES.json')):
        for _m in _read_json('docs-authority/inventory/CAD_MOVES.json'):
            if _m['unit'] in C:
                _c = C[_m['unit']][0]
                C[_m['unit']] = ([_c[0] + _m['dx_mm'], _c[1] + _m['dy_mm'], _c[2]],
                                 C[_m['unit']][1] + ' + GA move')
    if 'EVAP_ACID_VS' not in C and 'EVAP_ACID' in C:
        c = C['EVAP_ACID'][0]
        C['EVAP_ACID_VS'] = ([c[0], c[1] + 650, c[2]], 'on EVAP_ACID frame')
    for b in seed['blocks']:
        o = b['origin_mm']
        z = b['size_mm']
        c = [o[0] + z[0] / 2, o[1] + z[1] / 2, LV.get(b['level'], 0) + 500]
        for u in b.get('unit_ids', []):
            C.setdefault(u, (c, 'placement block ' + b['block_id']))
    return C


def _placement_blocks():
    """The merged placement block map: seed blocks first, study rows
    setdefault (the v1 order)."""
    seed = _placement_seed()
    st = _read_json('flow_graph/placement_study.json')
    blk = {}
    for b in seed['blocks']:
        for u in b.get('unit_ids', []):
            blk[u] = b['block_id']
    for r in st['units']:
        blk.setdefault(r['unit_id'], r.get('block_id'))
    return blk


def _nozzle_schedules():
    """The committed nozzle schedule files as the declared payload:
    {unit: bytes}. The nozzles family proves the committed tree is the merge
    fixpoint of the hand rows, so these bytes are the product."""
    out = {}
    d = os.path.join(ROOT, 'docs-authority', 'nozzles')
    for name in sorted(os.listdir(d)):
        if name.endswith('.csv'):
            with open(os.path.join(d, name), 'rb') as f:
                out[name[:-4]] = f.read()
    return out


def _nozzle_units():
    """The sorted unit ids that have a nozzle schedule (the v1 exists-probe
    set)."""
    return sorted(os.path.basename(p)[:-4]
                  for p in glob.glob(os.path.join(ROOT, 'docs-authority/nozzles/*.csv')))


def _nozzle_reservation_sizes():
    """{unit: [size column values]} over every committed nozzle schedule —
    the headers family's reservation cross-section payload."""
    out = {}
    d = os.path.join(ROOT, 'docs-authority', 'nozzles')
    for name in sorted(os.listdir(d)):
        if name.endswith('.csv'):
            with open(os.path.join(d, name), encoding='utf-8', newline='') as f:
                out[name[:-4]] = [r['size'] for r in csv.DictReader(f)]
    return out


def _cause_effect_rows():
    """The docs-authority/CAUSE_EFFECT.md '| SIF-' column lists (the boundary
    parse; the tag extraction stays in the pid renderer)."""
    out = []
    for line in _rd('docs-authority/CAUSE_EFFECT.md').splitlines():
        if line.startswith('| SIF-'):
            c = [x.strip() for x in line.strip().strip('|').split('|')]
            if len(c) >= 7:
                out.append(c)
    return out


def _drawing_inventory():
    """The stamped-SVG inventory and the STEP list (the v1 files() globs,
    repo-relative, posix)."""
    svgs = {}
    for pat in ('flow_graph/views/*.svg', 'models/motors/*/export/*.svg',
                'models/mfg/*/drawings/*.svg'):
        for p in sorted(glob.glob(os.path.join(ROOT, pat))):
            rel = p[len(ROOT) + 1:].replace(os.sep, '/')
            with open(p, encoding='utf-8') as f:
                svgs[rel] = f.read()
    steps = sorted(p[len(ROOT) + 1:].replace(os.sep, '/')
                   for p in glob.glob(os.path.join(ROOT, 'models/mfg/*/export/*.step')))
    return svgs, steps


def _duty_relief6():
    """The unit ids whose committed duty sheet carries the section-6 relief
    statement - the DUTY6 set of docs-authority/_hazop.py, read here at the
    declared I/O boundary (the pages are hand-authored; the duties family
    census)."""
    duties = os.path.join(ROOT, 'docs-authority', 'duties')
    out = []
    for name in sorted(os.listdir(duties)):
        if not name.endswith('.md') or name.startswith('_'):
            continue
        if re.search(r'^6\. Relief', _rd('docs-authority/duties/' + name), re.M):
            out.append(name[:-3])
    return out


def _duty_sec3():
    """The hand-authored duty-sheet section 3 texts, whitespace-normalized as
    the v1 _eol.py duty3() read."""
    d3 = {}
    for p in glob.glob(os.path.join(ROOT, 'docs-authority/duties/*.md')):
        s = _rd(os.path.relpath(p, ROOT))
        m = re.search(r'^3\.\s*Material\.(.*?)(?=^4\.)', s, re.M | re.S)
        d3[os.path.basename(p)[:-3]] = ' '.join(m.group(1).split()) if m else None
    return d3


def _mfg_tools_rows():
    """The MFG_TOOLS.md tool table rows, under the v1 filter (`len(c) >= 3
    and numeric c[2]` on the `|`-split cells)."""
    out = []
    for line in _rd('docs-authority/MFG_TOOLS.md').splitlines():
        c = [x.strip() for x in line.split('|')[1:-1]]
        if len(c) >= 3 and re.match(r'^[\d.]+$', c[2]):
            out.append((c[0], c[1], float(c[2])))
    return out


def _supports_counts():
    """The SUPPORTS.md span counts (the v1 `| ` row / column 6 digit parse)."""
    sup = {}
    for line in _rd('docs-authority/SUPPORTS.md').splitlines():
        if line.startswith('| ') and line.split('|')[6].strip().isdigit():
            sup[line.split('|')[1].strip()] = int(line.split('|')[6])
    return sup


def _grounding_grid():
    """The grounding-grid study lengths: the read-only AQS-ELEC-005 study
    print (the v1 wire stage ran the same script for its lengths; it writes
    nothing), the last stdout line as JSON."""
    out = subprocess.run([sys.executable, 'docs-authority/_grounding_study.py'],
                         capture_output=True, text=True, cwd=ROOT, check=True)
    return json.loads(out.stdout.strip().splitlines()[-1])


def _family_registers():
    """The append-only family-id registers (the formats are the inventory
    family's): one entry per register prefix."""
    return {pre: _read_json(f'flow_graph/inventory/{name}_family_ids.json')
            for pre, name in (('MF', 'motor'), ('WF', 'wire'), ('PF', 'pipe'), ('OF', 'other'))}


_DOCNUM_RE = re.compile(r'^Document(?: number)?:\s*\**\s*(AQS-[A-Za-z0-9-]+)', flags=re.M)


def _doc_numbers():
    """The front-matter document numbers the views family cites (the v1
    docnum() read)."""
    out = {}
    for name in ('DESIGN_TOOL_ARCHITECTURE.md', 'GLOSSARY.md'):
        got = _DOCNUM_RE.search(_rd('docs-authority/' + name))
        out[name] = got.group(1) if got else '—'
    return out


def _system_tree():
    import yaml
    with open(os.path.join(ROOT, 'flow_graph/system_tree.yaml'), encoding='utf-8') as f:
        return yaml.safe_load(f)


AUXILIARY = [
    # the census family's declared payload (test_inventory_books.auxiliary_payload,
    # moved into the engine's I/O boundary at the P4 flip)
    ('family_registers', _family_registers),
    ('mfg_boms', lambda: _glob_map('models/mfg/*/bom.csv', _read_csv_cells,
                                   lambda p: p.split('/')[-2])),
    ('mfg_fasteners', lambda: _glob_map('models/mfg/*/fasteners.csv', _read_csv_rows,
                                        lambda p: p.split('/')[-2])),
    ('mfg_tools', _mfg_tools_rows),
    ('placement', _placement_blocks),
    ('iso_sheets', lambda: _read_csv_rows('docs-authority/iso/ISO_SHEETS.csv')),
    ('supports', _supports_counts),
    ('gas_detectors', lambda: _read_csv_rows('docs-authority/inventory/GAS_DETECTORS.csv')),
    ('sif_list', lambda: _read_csv_rows('docs-authority/sif_list.csv')),
    ('nozzle_units', _nozzle_units),
    ('nozzles', _nozzle_reservation_sizes),
    ('line_positions', _line_positions),
    ('grounding_grid', _grounding_grid),
    ('motor_family_boms', lambda: _glob_map('models/motors/MF-*/bom.csv', _read_csv_cells,
                                            lambda p: p.split('/')[-2])),
    ('unit_boms', lambda: _glob_map('models/units/*/bom.csv', _read_csv_cells,
                                    lambda p: p.split('/')[-2])),
    ('duty_sec3', _duty_sec3),
    ('piping_classes', lambda: _rd('docs-authority/PIPING_CLASSES.md').splitlines()),
    # the other families' faces
    ('placement_seed', _placement_seed),
    ('graph_sha256', _graph_sha256),
    ('nozzle_schedules', _nozzle_schedules),
    ('instrument_index', lambda: _read_csv_rows('docs-authority/inventory/INSTRUMENT_INDEX.csv')),
    ('other_inventory', lambda: _read_csv_rows('docs-authority/inventory/OTHER_INVENTORY.csv')),
    ('motor_inventory', lambda: _read_csv_rows('docs-authority/inventory/MOTOR_INVENTORY.csv')),
    ('duty_relief6', _duty_relief6),
    ('cause_effect', _cause_effect_rows),
    ('system_tree', _system_tree),
    ('doc_numbers', _doc_numbers),
]

# The static data files behind the declared payload, manifest-tracked by the
# staleness rule (manifest.extra_input_paths). The drawing SVG/STEP inventory
# is deliberately absent: the renderer byte comparison against the committed
# document governs those bytes strictly more tightly than an input hash would.
AUXILIARY_FILES = [
    'flow_graph/placement_seed.json',
    'flow_graph/placement_report.json',
    'flow_graph/placement_study.json',
    'flow_graph/system_tree.yaml',
    'flow_graph/inventory/motor_family_ids.json',
    'flow_graph/inventory/wire_family_ids.json',
    'flow_graph/inventory/pipe_family_ids.json',
    'flow_graph/inventory/other_family_ids.json',
    'docs-authority/duties/_origins.json',
    'docs-authority/inventory/CAD_MOVES.json',
    'docs-authority/inventory/GAS_DETECTORS.csv',
    'docs-authority/inventory/INSTRUMENT_INDEX.csv',
    'docs-authority/iso/ISO_SHEETS.csv',
    'docs-authority/inventory/MOTOR_INVENTORY.csv',
    'docs-authority/inventory/OTHER_INVENTORY.csv',
    'docs-authority/CAUSE_EFFECT.md',
    'docs-authority/DESIGN_TOOL_ARCHITECTURE.md',
    'docs-authority/GLOSSARY.md',
    'docs-authority/MFG_TOOLS.md',
    'docs-authority/PIPING_CLASSES.md',
    'docs-authority/sif_list.csv',
    'docs-authority/SUPPORTS.md',
    'models/freecad/params.py',
]


def auxiliary_files():
    """AUXILIARY_FILES plus the glob trees behind the declared loaders: every
    committed nozzle schedule, duty sheet, mfg/motor/unit BOM and fastener
    file."""
    files = set(AUXILIARY_FILES)
    files.update('docs-authority/nozzles/' + os.path.basename(p)
                 for p in glob.glob(os.path.join(ROOT, 'docs-authority/nozzles/*.csv')))
    files.update(os.path.relpath(p, ROOT)
                 for pat in ('docs-authority/duties/*.md', 'models/mfg/*/bom.csv',
                             'models/mfg/*/fasteners.csv', 'models/motors/MF-*/bom.csv',
                             'models/units/*/bom.csv')
                 for p in glob.glob(os.path.join(ROOT, pat)))
    return sorted(files)

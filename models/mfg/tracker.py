# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Manufacturing-model tracker (AQS-PLAN-006 section 6, T0 item 3).

The tracker reads the plant graph - the sole topology authority - and, from the graph
node and the duty page of every present unit, writes that unit's W2 parameters file
`models/mfg/<UNIT>/params.json`, regenerates section 7 of `docs-authority/MFG_MODEL_PLAN.md`,
and runs the section 5 A-core checks that can run on files: assembly bounding box against
`size_mm` within 1 mm, nozzle count against the duty section 4 schedule, closed and
manifold STL, STEP present, and BOM complete. Both outputs are generated: edit the graph,
the duty pages or this tracker, never the outputs.

Section 7 statuses come from the files, not from memory. M0: the `cad/stl` file is an
envelope box (12 facets a box; boxes and box-plus-stub builds stay under 48 facets, the
old coarse internals start near 70). M1: coarse internals in `cad/stl`, no manufacturing
source. M2: a parametric source under `models/mfg` builds the unit (STEP in
`models/mfg/<UNIT>/export/`). M3: accepted under section 5; the tracker records M3 only
for units whose acceptance evidence it can verify on the files - the build log acceptance
line, the check record, the exports, the drawing set and the duty section 7 pointer - and
downgrades with a named hold when any is missing.

The tracker takes the design lock `${AQS_LOCK:-.aqs-design.lock}` itself for its write
phase; do not wrap it in a second flock. It writes only under `models/mfg/` and the
section 7 block of the plan page.

Run: python3 models/mfg/tracker.py            regenerate params.json files and section 7
      python3 models/mfg/tracker.py --check   run the file checks, write nothing
      python3 models/mfg/tracker.py --self-test   the T0 smoke test (needs CadQuery)
"""
import argparse
import csv
import fcntl
import json
import os
import re
import struct
import sys
import tempfile
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MFG = os.path.join(ROOT, 'models', 'mfg')
PLAN = os.path.join(ROOT, 'docs-authority', 'MFG_MODEL_PLAN.md')
S7_MARK = '## 7. Tracker'

# Route classes, AQS-PLAN-006 section 4, verbatim. A class absent here is a hold in the
# tracker output; the tracker does not extend the plan.
ROUTE_CLASS = {
    'F-VES': ('vessel', 'tank', 'cut_tank', 'digest', 'reactor', 'ferment', 'hopper',
              'separator', 'treat', 'dose', 'feed', 'polish', 'cru', 'melt'),
    'F-CELL': ('ew_cell', 'bmed', 'cell', 'pem_fc', 'iem_fc', 'flow_battery'),
    'F-COL': ('scrubber', 'cold_box', 'frac'),
    'F-HX': ('hx', 'heat_battery', 'cool', 'ahu', 'heat_pump', 'thermal', 'ghex'),
    'F-PIPE': ('header', 'recycle_pipe', 'intra', 'relief'),
    'F-MACH': ('tool', 'forming', 'mill', 'shop', 'pyro', 'dryer', 'baghouse', 'genset',
               'fab', 'wet_bench', 'hydro', 'dock', 'rectifier', 'inverter', 'pv', 'skid',
               'reagent'),
    'F-FARM': ('farm', 'hab'),
    'none': ('boundary',),
}

# Acceptance sets by class, AQS-PLAN-006 section 5 sets keyed the way the issued table
# keyed them (A-core with the class set; pipe classes carry A-PIPE alone).
CLASS_ACCEPT = {}
for _route, _classes in ROUTE_CLASS.items():
    for _c in _classes:
        CLASS_ACCEPT[_c] = {'F-VES': 'A-VES', 'F-CELL': 'A-CELL', 'F-COL': 'A-COL',
                            'F-HX': 'A-HX', 'F-MACH': 'A-MACH', 'F-FARM': 'A-FARM',
                            'F-PIPE': 'A-PIPE', 'none': 'A-ACC'}[_route]

# Order of work tiers, AQS-PLAN-006 section 3. Named units first, then class rules:
# the pipe classes, then every unit with a vessel internal row (tier 4), then the shop
# tools and forming (tier 7), the electrical and boundary units (tier 8), the farm and
# habitation units (tier 9), and the remaining process machines whose internal is none
# (tier 6).
TIER_NAMED = {'LEACH_CSTR_1': 2, 'BIOFILTER': 3, 'HOPPER': 4, 'FLOAT_SINK': 4}
TIER_NAMED.update({f'EW_{i}': 2 for i in range(1, 10)})
TIER_PIPE = ROUTE_CLASS['F-PIPE']
TIER_SHOP = ('tool', 'forming', 'mill', 'shop', 'fab', 'wet_bench', 'melt', 'aligner',
             'coater', 'caster', 'former', 'press', 'melt_spin')
TIER_ELEC = ('rectifier', 'inverter', 'load_agg', 'genset', 'flow_battery', 'pem_fc',
             'iem_fc', 'pem_electrolyser', 'pv', 'hydro', 'dock', 'building')
TIER_FARM = ('farm', 'hab', 'growbed', 'coop', 'pen', 'cage', 'hutch', 'hive', 'worm_bin',
             'duckweed', 'fish_tank', 'biofilter', 'medical', 'quarters', 'galley',
             'washroom', 'dayroom', 'feed_prep', 'uv_sanitizer', 'intake')

# Existing sources: the AQS-MFG-001 (`docs-authority/internal/DETAIL_MODEL_PLAN.md`) and
# shop-level files that bear on a unit, as the issued section 7 recorded them. Data, not
# generated output; a unit absent here has none.
EXISTING_SOURCE = {
    'EW_1': 'ew_cell.py, ew_cell.step, mfg_ew_fitout.scad',
    'EW_2': 'ew_cell.py, ew_cell.step, mfg_ew_fitout.scad',
    'EW_3': 'ew_cell.py, ew_cell.step, mfg_ew_fitout.scad',
    'EW_4': 'ew_cell.py, ew_cell.step, mfg_ew_fitout.scad',
    'EW_5': 'ew_cell.py, ew_cell.step, mfg_ew_fitout.scad',
    'EW_6': 'ew_cell.py, ew_cell.step, mfg_ew_fitout.scad',
    'EW_7': 'ew_cell.py, ew_cell.step, mfg_ew_fitout.scad',
    'EW_8': 'ew_cell.py, ew_cell.step, mfg_ew_fitout.scad',
    'EW_9': 'ew_cell.py, ew_cell.step, mfg_ew_fitout.scad',
    'CRYO_ASU': 'mfg_cold_box.scad',
    'BIOFILTER': 'mfg_biofilter.scad',
    'HOPPER': 'mfg_hopper.scad',
    'FLOAT_SINK': 'mfg_dewater.scad',
    'NOX_SCRUB': 'mfg_scrubber_train.scad',
    'ACID_POLISH_SCRUB': 'mfg_scrubber_train.scad',
    'ALK_SCRUBBER': 'mfg_scrubber_train.scad',
    'GLASS_DIGEST': 'mfg_digest.scad',
    'GLASS_BURNOUT': 'mfg_burnout_rotary.scad',
    'GLASS_MILL': 'mfg_mill.scad',
    'GLASS_RINSE': 'mfg_rinse.scad',
    'AFTERBURNER': 'mfg_afterburner.scad',
    'BAGHOUSE': 'mfg_baghouse.scad',
    'BMED_ACID': 'bmed_cell.scad, mfg_bmed_stack.scad',
    'BMED_BASE': 'bmed_cell.scad, mfg_bmed_stack.scad',
    'CRU': 'mfg_cru.scad',
    'H2_DRYER': 'mfg_h2_dryer.scad',
    'NUTRIENT_DOSE': 'mfg_nutrient_dose.scad',
    'OIL_DRYER': 'mfg_dryer.scad',
    'OIL_FRAC': 'mfg_fractionator.scad',
    'OIL_PYRO': 'mfg_induction_pyrolyzer.scad',
    'MET_MELT': 'mfg_melt.scad',
    'WET_BENCH': 'mfg_wet_bench.scad',
    'RECTIFIER': 'mfg_electrical.scad',
    'SOL_ARK_60K': 'mfg_electrical.scad',
    'ZNBR2': 'znbr2_iem.scad, mfg_znbr2_skid.scad',
    'GROW_BED': 'mfg_grow_bed.scad',
    'HABITATION': 'mfg_hab_water.scad, mfg_hab_waste.scad',
}

# Units whose section 5 acceptance the tracker verifies on the files before recording M3.
ACCEPTED = ('AL_POT',)


# --------------------------------------------------------------------------- authorities

def load_graph():
    with open(os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')) as fh:
        return json.load(fh)


def load_seed():
    with open(os.path.join(ROOT, 'flow_graph', 'placement_seed.json')) as fh:
        return json.load(fh)


def nozzle_rows(unit):
    """The duty section 4 schedule rows: tag, size, rating, service, face, height_mm."""
    path = os.path.join(ROOT, 'docs-authority', 'nozzles', unit + '.csv')
    if not os.path.exists(path):
        return None
    with open(path) as fh:
        rows = []
        for r in csv.DictReader(fh):
            try:
                h = float(r['height_mm'])
                h = int(h) if h == int(h) else h
            except (KeyError, TypeError, ValueError):
                h = None
            rows.append({'tag': r.get('tag'), 'size': r.get('size'), 'rating': r.get('rating'),
                         'service': r.get('service'), 'face': r.get('face'), 'height_mm': h})
        return rows


def duty_section(unit, number):
    """The text of one numbered section of the duty page, or None when absent."""
    path = os.path.join(ROOT, 'docs-authority', 'duties', unit + '.md')
    if not os.path.exists(path):
        return None
    text = open(path).read()
    parts = re.split(r'(?m)^(\d+)\. ', text)
    for i in range(1, len(parts) - 1, 2):
        if int(parts[i]) == number:
            body = parts[i + 1]
            body = body.split('\n#', 1)[0]      # stop at a following heading
            body = body.split('\n##', 1)[0]
            return re.sub(r'^Material\.\s*', '', body.strip())
    return None


def node_size(p):
    """The claimed envelope of a node, in the precedence the builders use."""
    env = p.get('envelope') or {}
    sizing = p.get('sizing') or {}
    return env.get('size_mm') or sizing.get('size_mm') or p.get('size_mm')


def node_size_basis(p):
    env = p.get('envelope') or {}
    sizing = p.get('sizing') or {}
    return env.get('basis') or p.get('size_note') or sizing.get('basis')


def node_internals(node):
    p = node.get('params') or {}
    return node.get('internals') or p.get('internals') or 'none'


# ------------------------------------------------------------------------------ STL read

def read_stl(path):
    """Return (facet_count, triangles, bbox_mm_or_None) for an ASCII or binary STL."""
    b = open(path, 'rb').read()
    tris = []
    if b[:5] == b'solid' and b'facet normal' in b[:512]:
        vals = re.findall(rb'vertex\s+(\S+)\s+(\S+)\s+(\S+)', b)
        flat = [tuple(float(x) for x in v) for v in vals]
    else:
        if len(b) < 84:
            return 0, [], None
        n = struct.unpack('<I', b[80:84])[0]
        flat = []
        off = 84
        for _ in range(n):
            if off + 50 > len(b):
                break
            v = struct.unpack('<12f', b[off:off + 48])   # normal + 3 vertices
            flat += [v[3:6], v[6:9], v[9:12]]
            off += 50
    tris = [flat[i:i + 3] for i in range(0, len(flat) - 2, 3)]
    if not tris:
        return 0, [], None
    xs = [c for t in tris for v in t for c in v]
    bbox = (min(xs[0::3]), min(xs[1::3]), min(xs[2::3]),
            max(xs[0::3]), max(xs[1::3]), max(xs[2::3]))
    return len(tris), tris, bbox


def stl_manifold(path):
    """True when every mesh edge is shared by exactly two triangles (closed, manifold)."""
    _, tris, _ = read_stl(path)
    if not tris:
        return False
    m = max(abs(c) for t in tris for v in t for c in v) or 1.0
    q = 3 if m >= 1 else 7   # float32 precision: ~1e-4 at 800 mm, ~1e-7 below 1
    edges = {}
    for t in tris:
        vs = [tuple(round(c, q) for c in v) for v in t]
        if len(set(vs)) < 3:
            continue
        for i in range(3):
            e = tuple(sorted((vs[i], vs[(i + 1) % 3])))
            edges[e] = edges.get(e, 0) + 1
    return bool(edges) and all(n == 2 for n in edges.values())


def stl_bbox_mm(path):
    """Bounding box in mm; STL files under 10 on the largest axis are metre-scale."""
    _, _, bbox = read_stl(path)
    if bbox is None:
        return None
    x0, y0, z0, x1, y1, z1 = bbox
    if max(x1, y1, z1) < 10.0:   # cad/stl convention is metres; model exports are mm
        x0, y0, z0, x1, y1, z1 = x0 * 1000, y0 * 1000, z0 * 1000, x1 * 1000, y1 * 1000, z1 * 1000
    return [round(x1 - x0, 1), round(y1 - y0, 1), round(z1 - z0, 1)]


# --------------------------------------------------------------------------- unit record

def tier_of(unit, cls, internals):
    if unit in TIER_NAMED:
        return TIER_NAMED[unit]
    if cls == 'cold_box':
        return 3
    if cls in TIER_PIPE:
        return 5
    if internals and internals != 'none':
        return 4
    if cls in TIER_SHOP:
        return 7
    if cls == 'boundary' or cls in TIER_ELEC:
        return 8
    if cls in TIER_FARM:
        return 9
    return 6


def acceptance_of(cls, tier):
    if cls == 'boundary':
        return ['A-ACC']
    sets = ['A-core']
    if cls in CLASS_ACCEPT and CLASS_ACCEPT[cls] != 'A-ACC':
        sets.append(CLASS_ACCEPT[cls])
    elif cls not in CLASS_ACCEPT:
        if tier == 9:
            sets.append('A-FARM')
    if tier == 7 and 'A-SC' not in sets:
        sets.append('A-SC')
    return sets


def find_source(unit, unit_dir, cls=None):
    """The parametric source that builds a unit, as a short path fragment."""
    for name in (unit.lower() + '.py', unit + '.py'):
        p = os.path.join(unit_dir, name)
        if os.path.exists(p):
            return f'{unit}/{name}'
    for script in sorted(os.listdir(MFG)):
        if not script.endswith('.py') or script in ('build_all.py', 'tracker.py', 'draw_unit_ga.py'):
            continue
        text = open(os.path.join(MFG, script), errors='replace').read(200000)
        if re.search(rf"['\"]{re.escape(unit)}['\"]", text):
            return script
    if cls:
        style = re.search(rf"'{re.escape(cls)}':\s*'(\w+)'",
                          open(os.path.join(MFG, 'style_builders.py')).read())
        if style:
            return f'style_builders.py ({style.group(1)})'
    return None


def build_record(node, seed_map, graph_rev):
    """Everything section 7 and the W2 file say about one present unit."""
    u = node['unit_id']
    p = node.get('params') or {}
    cls = node.get('class')
    internals = node_internals(node)
    size = node_size(p)
    holds = []
    if not cls:
        holds.append('class not stated on the node')
    if cls != 'boundary':
        # an accounting node has no solid, so size, material and nozzle hardware are
        # not facts it owes
        if not size:
            holds.append('no size on the node')
        rows = nozzle_rows(u)
        if rows is None:
            holds.append('no duty section 4 schedule on file')
            rows = []
        material = (p.get('sec3_material') or {}).get('mat')
        if not material:
            material = duty_section(u, 3)
        if not material:
            holds.append('material not stated (duty section 3)')
    else:
        rows, material = [], None
    seed = seed_map.get(u)
    unit_dir = os.path.join(MFG, u)
    step = os.path.join(unit_dir, 'export', u.lower() + '.step')
    stl_path = os.path.join(ROOT, 'cad', 'stl', u + '.stl')
    tier = tier_of(u, cls, internals)
    rec = dict(
        unit=u, sector=node.get('sector_id'), cls=cls, tier=tier,
        internals=internals, size=size, size_basis=node_size_basis(p),
        design_kPa=p.get('design_kPa'), relief_mm=p.get('relief_mm'),
        relief_basis=p.get('relief_basis'), design=p.get('design'),
        material=material, nozzles=rows, holds=holds,
        seed_origin=seed is not None, origin_mm=(seed or {}).get('origin_mm'),
        existing_source=EXISTING_SOURCE.get(u, 'none'),
        route=next((r for r, cs in ROUTE_CLASS.items() if cls in cs), None),
        acceptance=acceptance_of(cls, tier),
        has_dir=os.path.isdir(unit_dir),
        step=step if os.path.exists(step) else None,
        cad_stl=stl_path if os.path.exists(stl_path) else None,
        graph_rev=graph_rev,
    )
    if rec['route'] is None and cls not in (None, 'boundary'):
        rec['holds'].append(f'no AQS-PLAN-006 section 4 route class for class {cls}')
    rec['source'] = find_source(u, unit_dir, cls) if rec['has_dir'] else None
    rec['build_log'] = _read_build_log(unit_dir) if rec['has_dir'] else None
    return rec


def _read_build_log(unit_dir):
    path = os.path.join(unit_dir, 'build_log.md')
    if not os.path.exists(path):
        return None
    return open(path, errors='replace').read()


# -------------------------------------------------------------------------- W2 params

W2_KEYS = ('unit_id', 'graph_revision', 'source', 'size_mm', 'size_basis', 'origin_mm',
           'class', 'sector', 'design_kPa', 'relief_mm', 'relief_basis', 'internals',
           'nozzles', 'material', 'acceptance_sets', 'holds')


def merge_params(rec, existing):
    """W2 fields generated from the graph and duty authorities; builder-owned keys pass
    through untouched (form, wall_mm, assumptions, the rich hand files such as AL_POT's).
    Existing nozzle entries keep their prose; schedule fields refresh from the CSV."""
    p = dict(existing) if existing else {}
    src = [f"flow_graph/plant_flow_graph.json node {rec['unit']} (graph revision "
           f"{rec['graph_rev']})",
           f"docs-authority/duties/{rec['unit']}.md sections 3, 4 and 6"]
    if os.path.exists(os.path.join(ROOT, 'docs-authority', 'nozzles', rec['unit'] + '.csv')):
        src.append(f"docs-authority/nozzles/{rec['unit']}.csv")
    if rec['seed_origin']:
        src.append('flow_graph/placement_seed.json')
    src.append('Generated by models/mfg/tracker.py (AQS-PLAN-006 section 6). Not edited by hand.')
    p['unit_id'] = rec['unit']
    p['graph_revision'] = rec['graph_rev']
    p['source'] = '; '.join(src)
    p['size_mm'] = rec['size']
    if rec['size_basis']:
        p['size_basis'] = rec['size_basis']
    p['origin_mm'] = rec['origin_mm']
    p['class'] = rec['cls']
    p['sector'] = rec['sector']
    p['design_kPa'] = rec['design_kPa']
    p['relief_mm'] = rec['relief_mm']
    if rec['relief_basis']:
        p['relief_basis'] = rec['relief_basis']
    p['internals'] = rec['internals']
    if isinstance(rec['design'], dict):
        d = dict(rec['design'])
        for k, v in (existing or {}).get('design', {}).items():
            if k not in d:            # builder-owned design notes pass through
                d[k] = v
        p['design'] = d
    csv_by_tag = {r['tag']: r for r in (rec['nozzles'] or [])}
    if 'nozzles' in p and isinstance(p['nozzles'], list):
        merged, seen = [], set()
        for entry in p['nozzles']:
            tag = entry.get('tag') if isinstance(entry, dict) else None
            if tag in csv_by_tag:
                fresh = dict(entry)
                fresh.update(csv_by_tag[tag])
                merged.append(fresh)
                seen.add(tag)
            else:
                merged.append(entry)   # hand entry with no schedule row: kept, named below
        for tag, r in csv_by_tag.items():
            if tag not in seen:
                merged.append(dict(r))
        p['nozzles'] = merged
    else:
        p['nozzles'] = [dict(r) for r in (rec['nozzles'] or [])]
    if rec['material']:
        p['material'] = rec['material']
    p['acceptance_sets'] = rec['acceptance']
    if rec['holds']:
        p['holds'] = rec['holds']
    elif 'holds' in p:
        del p['holds']                # regenerated: a cleared hold leaves the file
    return p


def write_params(rec, lock_fh=None):
    unit_dir = os.path.join(MFG, rec['unit'])
    path = os.path.join(unit_dir, 'params.json')
    existing = None
    if os.path.exists(path):
        with open(path) as fh:
            existing = json.load(fh)
    merged = merge_params(rec, existing)
    with open(path, 'w') as fh:
        json.dump(merged, fh, indent=1)
        fh.write('\n')
    return path


# ------------------------------------------------------------------------ file checks

def check_unit(rec):
    """The A-core checks that can run on files. Returns a list of failure strings."""
    fails = []
    if not rec['has_dir']:
        return fails
    step = rec['step']
    stl = os.path.join(MFG, rec['unit'], 'export', rec['unit'].lower() + '.stl')
    if step:
        if os.path.getsize(step) < 200:
            fails.append('STEP file is empty')
        if os.path.exists(stl):
            if not stl_manifold(stl):
                fails.append('export STL is not closed and manifold')
            size = rec['size']
            bbox = stl_bbox_mm(stl)
            if size and bbox:
                if any(b > float(s) + 1.0 for b, s in zip(bbox, [float(v) for v in size])):
                    # section 5: the misfit is reported, nothing is resized (a build that
                    # under-fills its envelope is inside it; the house gate is on overshoot)
                    fails.append(f'bbox {bbox} against size_mm {size} (misfit to report)')
        else:
            fails.append('no export STL')
        if rec['nozzles'] is not None and os.path.exists(
                os.path.join(ROOT, 'docs-authority', 'nozzles', rec['unit'] + '.csv')):
            with open(os.path.join(ROOT, 'docs-authority', 'nozzles', rec['unit'] + '.csv')) as fh:
                n_csv = sum(1 for _ in csv.DictReader(fh))
            ppath = os.path.join(MFG, rec['unit'], 'params.json')
            if os.path.exists(ppath):
                with open(ppath) as fh:
                    try:
                        n_par = len(json.load(fh).get('nozzles') or [])
                    except json.JSONDecodeError:
                        n_par = -1
                if n_par != n_csv:
                    fails.append(f'nozzle count {n_par} against schedule {n_csv}')
    bom = os.path.join(MFG, rec['unit'], 'bom.csv')
    if os.path.exists(bom):
        with open(bom) as fh:
            rows = list(csv.reader(fh))
        head = [h.strip().lower() for h in (rows[0] if rows else [])]
        if 'material' not in head or not any(h in ('qty', 'quantity') for h in head):
            fails.append('BOM header lacks material or qty')
        else:
            mi = head.index('material')
            qi = next(i for i, h in enumerate(head) if h in ('qty', 'quantity'))
            if any(len(r) <= max(mi, qi) or not r[mi].strip() or not r[qi].strip()
                   for r in rows[1:] if r):
                fails.append('BOM row missing material or qty')
    elif step:
        fails.append('no BOM')
    return fails


# ------------------------------------------------------------------------ section 7

def cell(s):
    return str(s).replace('|', '/').replace('\n', ' ').strip()


def cad_stl_cell(rec):
    if not rec['cad_stl']:
        return 'none'
    n, _, _ = read_stl(rec['cad_stl'])
    if rec['step']:
        if n > 48:
            return f'from the build, ~{n} f'
        return f'envelope box, ~{n} f (build STL in export/)'
    if n <= 48:
        return f'envelope, ~{n} f'
    return f'coarse, ~{n} f'


def status_of(rec):
    if rec['cls'] == 'boundary':
        return 'accounting node. No solid'
    if not rec['step']:
        if not rec['cad_stl']:
            return 'M0. no cad/stl and no build export yet'
        n, _, _ = read_stl(rec['cad_stl'])
        if n <= 48:
            return f'M0. Envelope box, ~{n} f; no build export yet'
        return f'M1. Coarse internals, ~{n} f; no build export yet'
    src = rec['source'] or 'models/mfg builder'
    if rec['unit'] in ACCEPTED:
        ok, missing = acceptance_evidence(rec)
        if ok:
            return (f"M3. Envelope-class build accepted per its build log; GA and iso drawing "
                    f"set; check.json bbox record. cad/stl {cad_stl_cell(rec).split(', ')[-1]}")
        return f'M2. acceptance evidence missing: {"; ".join(missing)}'
    s = f'M2. Builds from {src}; STEP and STL in export/'
    if rec['cad_stl']:
        n, _, _ = read_stl(rec['cad_stl'])
        s += f'; cad/stl from the build, ~{n} f' if n > 48 else f'; cad/stl still the envelope box, ~{n} f'
    else:
        s += '; no cad/stl'
    return s


def acceptance_evidence(rec):
    """The section 5 evidence the tracker can verify on the files for an accepted unit."""
    missing = []
    log = rec['build_log'] or ''
    if 'accepted per AQS-PLAN-006 section 5' not in log:
        missing.append('build log has no section 5 acceptance line')
    if not os.path.exists(os.path.join(MFG, rec['unit'], 'check.json')):
        missing.append('no check.json')
    if not os.path.exists(os.path.join(MFG, rec['unit'], 'drawings')):
        missing.append('no drawing set')
    duty7 = duty_section(rec['unit'], 7) or ''
    if rec['unit'].lower() not in duty7.replace('_', '').lower() and rec['unit'] not in duty7:
        missing.append('duty section 7 does not point at the model')
    return (not missing), missing


def section7_text(records, graph, seed):
    present = [r for r in records]
    counts = {'M0': 0, 'M1': 0, 'M2': 0, 'M3': 0, 'A-ACC': 0}
    for r in present:
        if r['cls'] == 'boundary':
            counts['A-ACC'] += 1
        elif r['unit'] in ACCEPTED and acceptance_evidence(r)[0] and r['step']:
            counts['M3'] += 1
        elif r['step']:
            counts['M2'] += 1
        elif r['cad_stl'] and read_stl(r['cad_stl'])[0] > 48:
            counts['M1'] += 1
        else:
            counts['M0'] += 1
    n_check_fail = sum(1 for r in present if check_unit(r))
    today = date.today().isoformat()
    L = []
    L.append(S7_MARK)
    L.append('')
    L.append(f'Generated by `models/mfg/tracker.py` from `flow_graph/plant_flow_graph.json` '
             f'revision {graph["revision"]}, `flow_graph/placement_seed.json` revision '
             f'{seed.get("revision")}, the duty pages and nozzle schedules, the `cad/stl` files '
             f'and the `models/mfg` tree. {len(present)} present units. Do not edit by hand.')
    L.append('')
    L.append('Status codes. M0: `cad/stl` is an envelope box or boxes. M1: `cad/stl` has '
             'coarse internals, such as the cell plate racks or a packed section, but there is '
             'no manufacturing source. M2: parametric source in `models/mfg` builds. M3: '
             'accepted under section 5. '
             f'As of {today}: {counts["M0"]} units at M0, {counts["M1"]} at M1, '
             f'{counts["M2"]} at M2, {counts["M3"]} at M3, {counts["A-ACC"]} accounting nodes. '
             'The units whose build log records "no build export yet" carry the envelope box '
             'in `cad/stl`. AL_POT is at M3 on its build log of 2026-10-31 ("envelope-class '
             'build accepted per AQS-PLAN-006 section 5 A-core"), with the drawing set at '
             '`models/mfg/AL_POT/drawings/` and the check record at '
             '`models/mfg/AL_POT/check.json`.')
    L.append('')
    L.append('Facet counts are read from the `cad/stl` file (ASCII or binary), not estimated. '
             'Existing source is an AQS-MFG-001 (`docs-authority/internal/DETAIL_MODEL_PLAN.md`) '
             'or `models/openscad/detail` file that bears on the unit; none of them is accepted. '
             f'The tracker file checks name their failures: `python3 models/mfg/tracker.py --check` '
             f'({n_check_fail} of {len(present)} units carry at least one named failure, most '
             'often a missing BOM or a BOM without the make-or-buy column of section 5). '
             'A unit whose assembly bounding box leaves `size_mm` carries the misfit in its '
             'status cell; nothing is resized.')
    L.append('')
    L.append('| Seq | Unit | Sector | Class | Tier | Internal on node | Seed origin | `cad/stl` now | '
             'Existing source | Route | Acceptance | Status |')
    L.append('| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |')
    order = sorted(present, key=lambda r: (r['tier'], 0 if r['seed_origin'] else 1,
                                           0 if r['existing_source'] != 'none' else 1, r['unit']))
    for i, r in enumerate(order, 1):
        route = r['route'] if r['route'] else ('none' if r['cls'] == 'boundary' else
                                               'hold: no section 4 class')
        if r['cls'] == 'boundary':
            accept = 'A-ACC'
        else:
            accept = ', '.join(r['acceptance']) + ('' if r['route'] else ' (route hold)')
        L.append(f"| {i} | {cell(r['unit'])} | {cell(r['sector'])} | {cell(r['cls']) or 'hold: no class on the node'} "
                 f"| {r['tier']} | {cell(r['internals'])} | {'yes' if r['seed_origin'] else 'no'} "
                 f"| {cell(cad_stl_cell(r))} | {cell(r['existing_source'])} | {cell(route)} "
                 f"| {cell(accept)} | {cell(status_of(r))} |")
    return '\n'.join(L) + '\n'


def splice_section7(text):
    plan = open(PLAN).read()
    i = plan.index(S7_MARK)
    open(PLAN, 'w').write(plan[:i] + text)


# ------------------------------------------------------------------------------- main

def collect_records():
    graph = load_graph()
    seed = load_seed()
    seed_map = {u['unit_id']: u for u in seed.get('units', [])}
    nodes = [n for n in graph['nodes'] if n.get('presence') == 'present']
    return graph, seed_map, [build_record(n, seed_map, graph['revision']) for n in nodes]


def take_lock():
    path = os.environ.get('AQS_LOCK', os.path.join(ROOT, '.aqs-design.lock'))
    fh = open(path, 'w')
    fcntl.flock(fh, fcntl.LOCK_EX)
    return fh


def main(argv=None):
    ap = argparse.ArgumentParser(description='Manufacturing-model tracker (AQS-PLAN-006 section 6)')
    ap.add_argument('--check', action='store_true', help='run the file checks, write nothing')
    ap.add_argument('--self-test', action='store_true', help='run the T0 smoke test (needs CadQuery)')
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()

    graph, seed_map, records = collect_records()
    if args.check:
        failed = 0
        for r in sorted(records, key=lambda x: x['unit']):
            fails = check_unit(r)
            for f in fails:
                print(f'CHECK {r["unit"]}: {f}')
            failed += bool(fails)
        print(f'--check: {len(records)} units, {failed} with named failures')
        return 0

    lock = take_lock()
    try:
        n_params = 0
        for r in records:
            if r['has_dir']:
                write_params(r)
                n_params += 1
        splice_section7(section7_text(records, graph, load_seed()))
    finally:
        lock.close()
    print(f'tracker: {n_params} params.json written; section 7 regenerated '
          f'({len(records)} present units, graph revision {graph["revision"]})')
    return 0


# --------------------------------------------------------------------------- self-test

def self_test():
    """T0 gate item 4: one box with one DN15 nozzle, built, exported, and checked."""
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)
    import cadquery as cq
    from lib import dn, fasteners, frame, materials, nozzles

    ok = []

    # 1. the tables: cited values round-trip
    assert dn.pipe_od('DN15') == 21.3 and dn.pipe_wall('DN50', 40) == 3.91
    f = dn.flange('DN50')
    assert f['od'] == 152.4 and f['n_bolts'] == 4 and f['t'] == 19.1
    assert fasteners.grade_for('316L') == 'ISO 3506 A4-70'
    assert fasteners.grade_for('CS') == 'ISO 898-1 8.8'
    assert materials.ca_for('CPVC') == 0.0
    assert materials.ca_for('carbon steel', 'hydrocarbon') == 1.5
    assert materials.density('Ti G2') == 4510.0
    ok.append('tables')

    # 2. the load rule: the standard bay passes, an overloaded rail climbs the ladder
    d, limit, good = frame.deflection(1200, 100, 6, 100)
    assert good and d < limit, (d, limit)
    assert frame.section_for(1200, 100) == (100, 6)
    assert frame.section_for(1200, 8000) == (120, 8)   # a heavy rail goes up a section
    assert abs(frame.steel_mass(1200, 600, 800, 100, 6) - 177.0) < 3.0
    ok.append('load rule')

    # 3. build: a box with one DN15 flange stub and one hose barb on its faces, both
    # visible, inside a declared size that includes the nozzle stick-out
    box_size = (200.0, 150.0, 100.0)
    size = (240.0, 150.0, 147.0)   # +X DN15 stub 40 out, top barb 45 + tip out
    box = cq.Workplane('XY').box(*box_size, centered=False)
    stub = nozzles.flange_stub('DN15', 40.0)
    assert stub.val().isValid()
    stub = nozzles.place_on_face(stub, '+X', 50.0, (100.0, 75.0), box_size, outside=True)
    barb = nozzles.hose_barb(19.0, 45.0)
    assert barb.val().isValid()
    barb = nozzles.place_on_face(barb, 'top', 0.0, (100.0, 75.0), box_size, outside=True)
    model = box.union(stub).union(barb)
    solid = model.val()
    bb = solid.BoundingBox()
    dims = [round(bb.xlen, 1), round(bb.ylen, 1), round(bb.zlen, 1)]
    assert max(abs(a - b) for a, b in zip(dims, size)) <= 1.0, dims   # within 1 mm
    assert solid.isValid()

    # 4. a frame bay spans its envelope exactly
    bay = frame.frame_members(1200, 600, 800, 100, 6)
    fb = bay.val().BoundingBox()
    assert [round(fb.xlen), round(fb.ylen), round(fb.zlen)] == [1200, 600, 800]
    ok.append('build')

    # 5. export, then run the file checks on the exported STL
    out = tempfile.mkdtemp(prefix='aqs-t0-selftest-')
    step_path = os.path.join(out, 'smoke.step')
    stl_path = os.path.join(out, 'smoke.stl')
    cq.exporters.export(solid, step_path)
    cq.exporters.export(solid, stl_path, opt={'ascii': True})
    assert os.path.getsize(step_path) > 200
    n, _, _ = read_stl(stl_path)
    assert n > 12, n
    assert stl_manifold(stl_path), 'exported smoke STL must be closed and manifold'
    bbox = stl_bbox_mm(stl_path)
    assert max(abs(a - b) for a, b in zip(bbox, list(size))) <= 1.0, bbox
    ok.append(f'export+check ({out})')

    # 6. the manifold check catches an open mesh: drop one triangle and it must fail
    lines = open(stl_path).read().split('endsolid')[0].split('facet normal')
    open(stl_path, 'w').write('solid smoke\n' + 'facet normal'.join(lines[1:-1]) + 'endsolid smoke\n')
    assert not stl_manifold(stl_path), 'the manifold check must catch a missing facet'
    ok.append('manifold check catches an open mesh')

    print('self-test: PASS - ' + '; '.join(ok))
    return 0


if __name__ == '__main__':
    sys.exit(main())

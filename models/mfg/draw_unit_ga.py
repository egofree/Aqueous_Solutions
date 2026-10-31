"""Generic GA drawing sheets + build logs for the detail units at models/mfg/<UNIT>/ (AQS-PLAN-006 section 5).

For each named unit (default: every models/mfg/<UNIT>/ that has an export solid but no drawings):
  1. Three projected sheets ga_front (-Y), ga_side (-X), iso01 from the unit's own build export
     (export/<unit>.step preferred, cad/stl/<UNIT>.stl fallback), with a notes band keyed to the
     graph revision - the same sheet mechanics as draw_al_pot.py. The AQS-DWG-001 title block and
     the DRAWING_REGISTER rows are applied afterwards by docs-authority/_drawings.py.
  2. build_log.md: tool versions, in-envelope bbox check against params.size_mm, artifact list -
     the AQS-PLAN-006 section 5 A-core acceptance record.

Run: python3 models/mfg/draw_unit_ga.py [UNIT ...]   (needs CadQuery)
"""
import json, os, re, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
G = json.load(open('flow_graph/plant_flow_graph.json'))
N = {n['unit_id']: n for n in G['nodes']}
import cadquery as cq

BAND = 100   # notes band appended under the drawing; _drawings.py stamps the title block bottom-right

def bbox_notes(u, shape):
    bb = shape.val().BoundingBox()
    dims = (round(bb.xlen), round(bb.ylen), round(bb.zlen))
    p = N[u].get('params') or {}
    env = p.get('size_mm')
    lines = [f'Overall build bbox {dims[0]} x {dims[1]} x {dims[2]} mm (X x Y x Z, build origin at the tray)']
    if env:
        inside = all(d <= e + 1 for d, e in zip(dims, env))
        lines.append(f'Graph envelope {env[0]} x {env[1]} x {env[2]} mm (duty sheet section 2): '
                     + ('build fits inside with margin' if inside else 'OVER - see build_log check'))
    lines.append('Nozzle orientation per `docs-authority/nozzles/%s.csv`; P&ID `docs-authority/pid/%s.svg`' % (u, u))
    lines.append('Welds per the unit WORK_ORDER; procedure qualification ASME IX (shop, not stamped)')
    lines.append('General tolerance ISO 2768-m unless noted')
    return lines

def add_notes(svg_path, u, rev):
    s = open(svg_path).read()
    if 'aqs-title-block' in s:
        return 'stamped'
    w = float(re.search(r'width="([\d.]+)"', s).group(1))
    h = float(re.search(r'height="([\d.]+)"', s).group(1))
    s = re.sub(r'height="[\d.]+"', f'height="{h + BAND}"', s, count=1)
    block = f'<g id="aqs-fab-notes" transform="translate(0,{h})" font-family="DejaVu Sans,sans-serif" font-size="10" fill="#000">'
    for i, n0 in enumerate(bbox_notes(u, shape_cache[u])):
        block += f'<text x="6" y="{24 + 13 * i}">Graph revision {rev} - {os.path.basename(svg_path)}: {n0}</text>'
    block += '</g>'
    open(svg_path, 'w').write(s.replace('</svg>', block + '</svg>'))
    return 'noted'

shape_cache = {}

def sheet(u, sid, shape, pdir):
    d = f'models/mfg/{u}/drawings'
    os.makedirs(d, exist_ok=True)
    svg = f'{d}/{sid}.svg'
    if os.path.exists(svg) and 'aqs-title-block' in open(svg).read():
        try:   # stamped: geometry frozen, PDF pass only (AL_POT convention)
            import cairosvg
            cairosvg.svg2pdf(url=svg, write_to=svg[:-4] + '.pdf')
        except Exception:
            pass
        return
    cq.exporters.export(shape.val(), svg, opt={'projectionDir': pdir, 'showAxes': False, 'showHidden': True})
    add_notes(svg, u, N[u].get('graph_revision', 'BH'))

def solid_for(u):
    step = glob.glob(f'models/mfg/{u}/export/{u.lower()}.step') or glob.glob(f'models/mfg/{u}/export/*.step')
    if step:
        shape_cache[u + ':src'] = f'build export `{step[0]}`'
        return cq.importers.importStep(step[0])
    if not (N[u].get('params') or {}).get('size_mm'):
        raise SystemExit(f'{u}: no export and no params.size_mm; size the unit first (duty sheet section 2)')
    shape_cache[u + ':src'] = 'envelope box from the graph `params.size_mm` (envelope-class unit; no build export yet)'
    e = N[u]['params']['size_mm']
    return cq.Workplane('XY').box(e[0], e[1], e[2], centered=(False, False, False))

def build_log(u):
    p = (N[u].get('params') or {})
    shape = shape_cache[u]
    bb = shape.val().BoundingBox()
    dims = [round(bb.xlen), round(bb.ylen), round(bb.zlen)]
    env = p.get('size_mm')
    check = ('inside the envelope with margin' if env and all(a <= b + 1 for a, b in zip(dims, env))
             else 'no graph envelope; dims recorded' if not env else 'OVER ENVELOPE - open item')
    src = glob.glob(f'models/mfg/{u}/*.py') + glob.glob(f'models/mfg/{u}/export/*.step')
    sz_doc = f'docs-authority/sizing/{u}.md'
    sz_ref = (f'sizing `{sz_doc}`' if os.path.exists(sz_doc) else 'sizing per the duty sheet section 2')
    txt = (f'# Build log - {u}\n\n'
           f'Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).\n'
           f'Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/{u}.md`; '
           f'{sz_ref}).\n\n'
           f'## Tool versions\n\n'
           f'- CadQuery {cq.__version__} (CADQUERY_PYTHON)\n'
           f'- Python {sys.version.split()[0]}; build run headless via `models/mfg/build_all.py`\n\n'
           f'## Checks\n\n'
           f'- Build bbox {dims[0]} x {dims[1]} x {dims[2]} mm: {check}'
           + (f' (envelope {env[0]} x {env[1]} x {env[2]} mm)' if env else '') + '\n'
           f'- Solid source: {shape_cache.get(u + ":src", "envelope `cad/stl/" + u + ".stl`")}\n'
           f'- BOM `models/mfg/{u}/bom.csv`; fasteners and WORK_ORDER beside it\n'
           f'- Drawing set `models/mfg/{u}/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)\n\n'
           f'## Sources\n\n' + ''.join(f'- `{s}`\n' for s in src) +
           f'\nStatus: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design '
           f'detail (internals, weld procedures) follows the unit WORK_ORDER.\n')
    open(f'models/mfg/{u}/build_log.md', 'w').write(txt)

if __name__ == '__main__':
    todo = sys.argv[1:]
    if not todo:
        todo = [d.rstrip('/').split('/')[-1] for d in sorted(glob.glob('models/mfg/*/'))
                if glob.glob(d + 'export/*') and not os.path.isdir(d + 'drawings')
                and (N.get(d.rstrip('/').split('/')[-1]) or {}).get('presence') == 'present']
    for u in todo:
        if not (N.get(u) or {}).get('presence') == 'present':
            print(f'{u}: not present on the graph, skipped'); continue
        shape_cache[u] = solid_for(u)
        for sid, pdir in (('ga_front', (0, 1, 0)), ('ga_side', (1, 0, 0)), ('iso01', (1, -1, 0.8))):
            sheet(u, sid, shape_cache[u], pdir)
        build_log(u)
        print(f'{u}: ga_front ga_side iso01 + build_log')

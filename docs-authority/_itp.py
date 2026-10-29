"""AQS-QA-001 inspection and test plan per fabrication route (X-QA-01, A-M-190). Each unit is assigned a route from its BOM body
material (models/units/<U>/bom.csv) and its relief class; the route carries the inspection and test activities with H (hold), W (witness)
and R (record review) points. Writes models/units/<U>/itp.csv. Run: python3 docs-authority/_itp.py"""
import csv, glob, json, os, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(R); sys.path.insert(0, R)
from flow_graph.param.refs import cite
for k in ('ASME_B31_3', 'ASME_VIII1_UG', 'ASME_IX', 'ASTM_D2855', 'DVS_2207', 'ASME_RTP1', 'ASTM_G93', 'IEC60034_30_1', 'UL891', 'NEC2026', 'ISO_14687', 'API576_2017'): cite(k)
ROUTES = {
 'R1 high-pressure tube bank': [('material certificates and PMI of every tube', 'ASME B31.3 323, A-M-190', 'R'), ('WPS-01 welder qualification', 'ASME IX QW', 'R'),
   ('100 % visual and 100 % radiography of girth welds', 'ASME B31.3 K341 (high pressure)', 'H'), ('hydrostatic test at 1.5 x design, 10 min hold', 'ASME B31.3 345.4.2', 'H'),
   ('cleaning for oxygen service (CRYO_O2)', 'ASTM G93', 'H'), ('relief valve set and seat test', 'API 576', 'W'), ('gas purity at first fill (H2)', 'ISO 14687', 'R')],
 'R2 welded 316L': [('material certificates, PMI on wetted parts', 'A-M-190', 'R'), ('WPS-01, welder qualification', 'ASME IX', 'R'), ('visual 100 %, random 5 % RT or UT', 'ASME B31.3 Table 341.3.2 normal service', 'W'),
   ('pressure test: hydro 1.5 x design (piping) or 1.3 x MAWP (vessel), or 24 h fill test if atmospheric', 'ASME B31.3 345.4 / ASME VIII-1 UG-99', 'H'), ('passivation and ferroxyl test', 'A-M-190', 'W')],
 'R3 welded carbon steel': [('material certificates', 'ASME B31.3 323', 'R'), ('WPS-02, welder qualification', 'ASME IX', 'R'), ('visual 100 %, random 5 % RT', 'ASME B31.3 Table 341.3.2', 'W'),
   ('pressure test as R2', 'ASME B31.3 345.4 / ASME VIII-1 UG-99', 'H'), ('coating dry-film thickness', 'A-M-190', 'W')],
 'R4 thermoplastic fabrication': [('resin and pipe certificates', 'ASTM D1785 and the AQS-WLD-002 material rows', 'R'), ('WPS-03..07, fusion or solvent operator test', 'DVS 2207 / ASTM D2855', 'R'),
   ('fusion bead visual 100 %, record of heater temperature and pressure per joint', 'DVS 2207', 'W'), ('hydrostatic test 1.5 x design, or 24 h fill test if atmospheric', 'ASME B31.3 A345', 'H')],
 'R5 FRP laminate': [('resin and glass batch records', 'ASME RTP-1', 'R'), ('WPS-08 laminator demonstration laminate', 'ASME RTP-1 Part 7', 'R'), ('Barcol hardness and acetone sensitivity at cure', 'ASME RTP-1', 'W'),
   ('visual against the RTP-1 Table 6-1 imperfection limits', 'ASME RTP-1', 'W'), ('24 h fill test', 'A-M-190', 'H')],
 'R6 titanium and electrode sheet': [('Grade 2 certificates', 'A-M-190', 'R'), ('flatness and edge check of each cathode', 'A-M-190', 'W'), ('cell bus contact resistance', 'A-M-190', 'W'), ('bund and tank fill test', 'A-M-190', 'H')],
 'R7 glass, graphite and refractory': [('material batch record', 'A-M-190', 'R'), ('visual and dimensional', 'A-M-190', 'W'), ('thermal or leak test at first heat-up', 'A-M-190', 'H')],
 'R8 assembled equipment (structure, enclosures, mechanisms)': [('dimensional check against the unit drawing', 'ASME Y14.5', 'W'), ('bolting torque record', 'A-M-190', 'R'), ('function test', 'A-M-190', 'H')]}
COMMON = [('motors: routine test (winding resistance, insulation resistance, no-load run)', 'IEC 60034', 'W'), ('electrical panels: dielectric and continuity test', 'UL 891 / NEC 2026', 'H'), ('loop check of every instrument', 'A-M-190', 'W')]
g = json.load(open('flow_graph/plant_flow_graph.json')); N = {n['unit_id']: n for n in g['nodes']}
def route(u, mat):
    p = (N.get(u) or {}).get('params') or {}
    if (p.get('relief_basis') or {}).get('fire_case'): return 'R1 high-pressure tube bank'
    m = mat.lower()
    if '316l' in m: return 'R2 welded 316L'
    if 'carbon steel' in m or 'steel portal' in m: return 'R3 welded carbon steel'
    if 'frp' in m: return 'R5 FRP laminate'
    if 'titanium' in m: return 'R6 titanium and electrode sheet'
    if any(x in m for x in ('pvc', 'hdpe', 'pvdf', 'pp-h', 'polyprop')): return 'R4 thermoplastic fabrication'
    if any(x in m for x in ('glass', 'graphite', 'refractory')): return 'R7 glass, graphite and refractory'
    return 'R8 assembled equipment (structure, enclosures, mechanisms)'
asg = {}
for f in sorted(glob.glob('models/units/*/bom.csv')):
    u = f.split('/')[2]; rows = list(csv.DictReader(open(f)))
    if not rows: continue
    r = route(u, rows[0]['material']); motors = any(x['description'].startswith('Motor') for x in rows); elec = (N.get(u) or {}).get('class') in ('rectifier', 'inverter', 'genset', 'pem_fc', 'iem_fc', 'pem_electrolyser', 'hydro', 'flow_battery', 'pv')
    acts = ROUTES[r] + [c for c in COMMON if (c[0].startswith('motors') and motors) or (c[0].startswith('electrical') and elec) or c[0].startswith('loop')]
    asg[u] = r
    with open(f'models/units/{u}/itp.csv', 'w', newline='') as fh:
        w = csv.writer(fh); w.writerow(['step', 'activity', 'basis', 'point']); w.writerows([(i + 1, *a) for i, a in enumerate(acts)])
md = ['# Inspection and test plan', '', 'Document number: AQS-QA-001', 'Revision: B', 'Date: 2026-10-29',
      'Generated by `docs-authority/_itp.py`. Do not edit by hand; change the generator or its inputs and run `python3 -m flow_graph.param.regen`.',
      'Authority: AQS-PLAN-007 task X-QA-01; assumption A-M-190. Study.', '',
      '| Rev | Description | Date |', '| --- | --- | --- |',
      '| A | First issue: inspection and test routes by construction, and a plan for every unit | 2026-10-16 |',
      '| B | Record of revisions, purpose and scope added; routes numbered as sections with numbered tables | 2026-10-29 |', '',
      '## 1. Purpose and scope', '',
      'This page is the inspection and test plan (ITP) of the plant equipment. Each unit is assigned to one route according to its construction, and each route lists the inspection and test steps, the basis of each step and the inspection point. The plan for each unit is written to `models/units/<UNIT>/itp.csv`. The hold points marked A-M-190 are study practice until the owner adopts a quality manual (X-COD-01).', '',
      'An inspection point is one of three kinds. At a hold point (H) work stops until the inspector releases it. At a witness point (W) the inspector is invited, and work may proceed if the inspector does not attend after notice. At a record review (R) the inspector reviews the records.', '']
_sec = 2
for r, acts in ROUTES.items():
    us = sorted(u for u, x in asg.items() if x == r)
    md += [f'## {_sec}. Route {r}', '', f'Table {_sec}.1 gives the steps of route {r}. ' + (f'It applies to {len(us)} units: ' + ', '.join(us) + '.' if us else 'No unit is assigned to it.'), '', f'Table {_sec}.1. Route {r}', '', '| Step | Activity | Basis | Point |', '|---|---|---|---|'] + [f'| {i + 1} | {a} | {b} | {c} |' for i, (a, b, c) in enumerate(acts)] + ['']
    _sec += 1
md += [f'## {_sec}. Steps common to the routes', '', f'Table {_sec}.1 lists the steps added to every route where they apply.', '', f'Table {_sec}.1. Common steps', '', '| Activity | Basis | Point |', '|---|---|---|'] + [f'| {a} | {b} | {c} |' for a, b, c in COMMON]
md += ['', f'In all, {len(asg)} units are assigned to a route.']
open('docs-authority/ITP.md', 'w').write('\n'.join(md) + '\n'); import collections; print(collections.Counter(asg.values()))

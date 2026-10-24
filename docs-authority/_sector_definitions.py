# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Write docs-authority/SECTOR_DEFINITIONS.md (AQS-SEC-001) from its authorities.

Sectors, definitions, MVS flags and notes come from the graph's ``mvs.sectors``; units per
sector from the graph nodes; trains from ``flow_graph/system_tree.yaml``; the Sector
Definition classes, ESS peers, retired ids and aliases from
``design_tool/aqs_design_tool/sector_definitions.py``. Nothing here is hand-kept, so a
sector added, removed or renamed in the graph reaches this page on the next full regen.
Output depends only on those inputs (no run date), so a second run changes nothing.

    python3 docs-authority/_sector_definitions.py
"""
import importlib.util
import json
import os
from collections import defaultdict

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'docs-authority/SECTOR_DEFINITIONS.md')
REVISION, REV_DATE = 'H', '2026-10-24'     # bump when this generator's structure changes


def _module():
    p = os.path.join(ROOT, 'design_tool/aqs_design_tool/sector_definitions.py')
    spec = importlib.util.spec_from_file_location('aqs_sector_definitions', p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def docnum(name):
    """Document number from the page's own front matter, so this table never restates it."""
    import re
    m = re.search(r'^Document(?: number)?:\s*\**\s*(AQS-[A-Za-z0-9-]+)', open(os.path.join(ROOT, 'docs-authority', name)).read(), flags=re.M)
    return m.group(1) if m else '—'


def cell(x):
    return str(x).replace('|', '/').replace('\n', ' ').strip()


def main():
    g = json.load(open(os.path.join(ROOT, 'flow_graph/plant_flow_graph.json')))
    tree = yaml.safe_load(open(os.path.join(ROOT, 'flow_graph/system_tree.yaml')))
    mod = _module()
    sectors = g['mvs']['sectors']
    units = defaultdict(list)
    for n in g['nodes']:
        units[n['sector_id']].append(n['unit_id'])
    trains = defaultdict(list)
    desc = {}
    for n in tree['nodes']:
        if not n.get('parent'):
            desc[n['id']] = ' '.join(str(n.get('description', '')).split())
        elif '.' not in n['parent'] and not n.get('unit_id'):
            trains[n['parent']].append(n['id'].split('.', 1)[1])

    L = ['# Sector Definitions catalogue — plant sector_id map', '',
         'Document number: AQS-SEC-001  ', f'Revision: {REVISION}  ', f'Date: {REV_DATE}  ',
         f'Authority: generated from AQS-FLOW-GRAPH-001 `mvs.sectors` (graph Rev {g["revision"]}, {g["date"]}) and '
         f'AQS-SYS-TREE-001 by `docs-authority/_sector_definitions.py`. Do not edit this page; change the graph, the '
         'system tree or `design_tool/aqs_design_tool/sector_definitions.py`, then run the pipeline. The Sector '
         'Definition class list is owned by AQS-UI-001 §3.1. Not a PE stamp.', '',
         '| Rev | Change | Date |', '|---|---|---|',
         '| A–G | Hand-written catalogue and its ambiguity locks (A1–A9). Text in git history. | 2026-10-01 |',
         f'| H | Generated from the graph after the Rev AC sector pivot: WET renamed DIGESTER; ELEC_PV, ZNBR2, BACKUP_GEN '
         f'and FUEL_CELL became units in ELEC; TRR retired; FOUNDRY, POLYMERS and HEAT added. | {REV_DATE} |', '',
         'Licence: CERN-OHL-S-2.0.', '',
         '## 1. Purpose', '',
         'Map every plant `sector_id` to exactly one Sector Definition, with its MVS-closure flag, so that the design '
         'tool, the solver and the documents use one sector list. The list is the graph\'s; this page only presents it. '
         '`flow_graph/test_doc_consistency.py` fails when the design-tool catalogue or the README sector table drifts '
         'from the graph.', '',
         '## 2. Sector Definition classes', '',
         'Owned by AQS-UI-001 §3.1; do not add a class without a project decision. "In use" lists the sectors that '
         'currently carry the class.', '',
         '| Class | In use by |', '|---|---|']
    by_def = defaultdict(list)
    for s in sectors:
        by_def[s['sector_definition']].append(s['sector_id'])
    for c in mod.SectorDefinition:
        L.append(f'| {c.value} | {", ".join(by_def.get(c.value, [])) or "—"} |')
    unknown = sorted(set(by_def) - {c.value for c in mod.SectorDefinition})
    if unknown:
        raise SystemExit(f'graph uses Sector Definitions outside AQS-UI-001 §3.1: {unknown}')

    L += ['', '## 3. Catalogue', '',
          'One row per graph sector, in graph order. `required` is `required_for_mvs_closure`. Units are counted from '
          'the graph nodes; trains are the first level of the system tree.', '',
          '| sector_id | Sector Definition | required | enabled | units | trains | notes (graph) |',
          '|---|---|---|---|---|---|---|']
    for s in sectors:
        sid = s['sector_id']
        L.append(f'| {sid} | {s["sector_definition"]} | {str(s["required_for_mvs_closure"]).lower()} | '
                 f'{str(s.get("enabled", True)).lower()} | {len(units.get(sid, []))} | '
                 f'{", ".join(sorted(trains.get(sid, []))) or "—"} | {cell(s.get("notes", ""))} |')
    L += ['', '### 3.1 System tree descriptions', '', '| sector_id | Description (AQS-SYS-TREE-001) |', '|---|---|']
    for s in sectors:
        L.append(f'| {s["sector_id"]} | {cell(desc.get(s["sector_id"], "—"))} |')

    L += ['', '## 4. Energy storage peers', '',
          'MVS requires every ESS peer. Peers that are sectors: '
          + ', '.join(sorted(mod.ESS_PEER_SECTOR_IDS)) + '. Peers that are units inside a sector: '
          + ', '.join(f'{u} ({next((n["sector_id"] for n in g["nodes"] if n["unit_id"] == u), "not in graph")})'
                      for u in sorted(mod.ESS_PEER_UNIT_IDS))
          + '. A sandbox may disable a peer; the solver then reports `' + mod.UNRECLAIMED_RESOURCE_REASON
          + '` for it and does not claim closure.', '',
          '## 5. Retired sector ids', '',
          'Older documents and dated notes may use these names. Read them as the current sector shown.', '',
          '| Former id | Now | Since | Note |', '|---|---|---|---|']
    for old, r in sorted(mod.RETIRED_SECTOR_IDS.items()):
        L.append(f'| {old} | {", ".join(r["now"]) or "retired"} | {r["when"]} | {cell(r["note"])} |')
    L += ['', '## 6. Aliases and non-sector names', '',
          'Not sector ids. Reject them as `sector_id`; map them as shown.', '', '| Name | Meaning |', '|---|---|']
    for k, v in sorted(mod.NON_SECTOR_ALIASES.items()):
        L.append(f'| {k} | {cell(v)} |')
    L += ['', '## 7. Related documents', '',
          '| Doc | ID | Role |', '|---|---|---|',
          '| `flow_graph/plant_flow_graph.json` | AQS-FLOW-GRAPH-001 | Sole topology authority; `mvs.sectors` is the sector list |',
          '| `flow_graph/system_tree.yaml` | AQS-SYS-TREE-001 | Sector → train → unit decomposition |',
          f'| [DESIGN_TOOL_ARCHITECTURE.md](DESIGN_TOOL_ARCHITECTURE.md) | {docnum("DESIGN_TOOL_ARCHITECTURE.md")} | Owns the Sector Definition class list (§3.1) |',
          f'| [GLOSSARY.md](GLOSSARY.md) | {docnum("GLOSSARY.md")} | Sector and unit terms |', '']
    txt = '\n'.join(L)
    if not os.path.exists(OUT) or open(OUT).read() != txt:
        open(OUT, 'w').write(txt)
    print(f'SECTOR_DEFINITIONS.md: {len(sectors)} sectors, Rev {REVISION}')


if __name__ == '__main__':
    main()

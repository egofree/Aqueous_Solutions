"""The controls, HAZOP and operations renderer wave (the portable ledger
section J rows). Reference writers: flow_graph/param/code_basis.py
(write_std, the AQS-STD-007 page), docs-authority/_instr_index.py (the
AQS-CTL-001 page composition), docs-authority/_hazop.py and _sif.py (the
HAZOP worksheets/actions census and the SIF pass, one pipeline), and
docs-authority/_plc_arch.py (the AQS-CTL-002 page).

What ports today - the four census-fed rows, byte-exact against the
committed pages (flow_graph/v2/test_render_census_docs.py):

- render_instr_index_md: the AQS-CTL-001 page over the landed census book
  (functions/instrument_index.py instrument_book - the rows, the
  deviation-table flags, auth_rows and the boundary units; the face CSV
  alone cannot supply flags or auth_rows). The census-totals line, the PLC
  distribution, the deviation table, the per-unit extension section and the
  first-60-rows index reproduce the v1 composition. The CSV face registers
  here too (render_instr_index_csv).
- render_hazop_md / render_hazop_register_md / render_hazop_actions_csv:
  the AQS-SAF-001 worksheets, the AQS-SAF-008 register and the actions CSV.
  The census reads the graph (worksheets per unit: flow / pressure /
  temperature / level / composition deviations, safeguards read from the
  design) and dispositions every action against the artifacts the 2026-10-19
  honesty pass cites: the unit duty sheet's section 6 relief statement and
  the AQS-CTL-001 indication loops.
- render_cause_effect_md / render_sif_list_csv: the AQS-CTL-003 SIF pass -
  the trip actions of the HAZOP census, every AQS-CTL-001 high-level switch,
  the four gas/flame/area functions; the calibrated risk graph of
  IEC61511_2016 part 3 annex D is rule text, not physics. The v1
  hazop_actions.csv AMEND (closing the trip actions) composes in memory and
  the CSV registers at its committed post-SIF face - the EW_CELLS composer
  precedent of render/electrical.py; the pre-SIF face was an intermediate
  the v1 regen never kept.
- render_plc_arch_md: the AQS-CTL-002 page - the AI/DI counts from the
  census book, the electronics DO/AO/BUS points from the other inventory,
  the 16-channel module arithmetic and the 24 V loads.

Payload disposition (the inventory-family idiom: another stage's committed
product rides as an inputs face; an absent face takes the v1 absent-file
branch, soft - the sandbox render branch; a present-but-incomplete census
lane stays loud, through the family's own gate):

- inputs['other_inventory'] - the AQS-INV-004 rows (dict rows): the
  inventory lane of the instrument book AND the check-valve set of the
  HAZOP census AND the electronics point rows of the PLC page;
- inputs['motor_inventory'] - the committed MOTOR_INVENTORY.csv rows (dict
  rows, the motor census's product face): the pumped-unit set of the HAZOP
  census;
- inputs['duty_relief6'] - the unit ids whose committed duty sheet carries
  the section-6 relief statement (the hand-authored duties pages, the
  duties wave's REMAINING census; no in-memory source - the v1 stage read
  the pages): the relief-case disposition of the HAZOP census.

The instrument index itself is composed, not read: the landed census book
is the source for every page here, and flow_graph/v2/test_instrument_index.py
proves the book re-serializes to the committed CSV.

REMAINING (the section J rows NOT ported here; each becomes a renderer when
its last blocker lands, per the electrical wave's precedent):

- doc_perf_test: reads only the instrument index for the per-stream
  flow-transmitter tags - its blocker (the census family) LANDED with this
  wave, so the row is portable; it is simply not one of this wave's four
  rows;
- doc_op_proc: reads inventory/COMMISSIONING.csv (the commissioning
  family), sif_list.csv (registered here - the face can ride the payload
  exactly as gas_detectors/sif_list already do for the inventory family)
  and CAUSE_EFFECT.md (registered here - its '| SIF-' columns can compose
  in memory from the SIF book, the COLLECTION_BUS in-memory-composition
  precedent render/line_list.py already uses);
- plc_programs: reads INSTRUMENT_INDEX.csv (landed) and parses
  CONTROL_ARCH.md (registered here - the parse dies over the same io book
  this module composes) plus the graph;
- test_plan: reads docs-authority/assumptions_manual.json - a declared engine
  input file (flow_graph/v2/manifest.py INPUT_FILES) but not yet a declared
  input payload key of the solve contract, so its renderer has no pure input
  to read;
- code_basis append() half for the six amended documents whose renderers have
  not landed (ACCESS_CHECK, COLLECTION_BUS, GA_CHECK, HAZMAT_SEPARATION,
  POWER_SIZING is landed, PROTECTION is hand-authored): each composes its
  block in memory when its renderer lands, exactly as ONE_LINE and
  POWER_SIZING already do in render/electrical.py and HALL_EGRESS does in
  render/safety.py.

Cleared by this wave: doc_hazop, doc_instr_index, doc_sif and doc_plc_arch
(the census blocker the section recorded them under landed; this module
ports the four rows).

Pure: no I/O here - the registry returns bytes and file writing stays
outside.
"""
import collections
import csv
import io
import math

from flow_graph.param import code_basis as _CB
from flow_graph.v2.functions import instrument_index as _II   # the AQS-CTL-001 census book
from flow_graph.v2.functions import inventory as _INV         # the census family's graph views


# ---- AQS-STD-007: the code basis page (the pre-existing entry of this module) ----

def render_code_basis(m, inputs):
    """docs-authority/CODE_BASIS.md: the v1 write_std() page composed from the
    EDITIONS table (the single source of editions, AQS-STD-007) and the
    per-document governing-clause table - pure module data of
    flow_graph/param/code_basis.py, which the landed renderers already call
    for the X-STD-01 appends."""
    std_rows = [(c, e, st) for c, e, _, st in _CB.EDITIONS]
    lines = ['# Code basis', '', 'Document number: AQS-STD-007',
             'Former number: AQS-STD-002 (shared with MATERIALS_STD.md until 2026-10-24; that page keeps it)', 'Revision: D',
             'Date: 2026-10-24',
             'Basis: AQS-PLAN-007 task X-STD-01; project owner decision of 2026-10-15 (NFPA and ISO throughout; IBC, IFC, NEC and IEEE where they govern; '
             'the most restrictive requirement governs).',
             "Source: generated by `flow_graph/param/code_basis.py` and checked by `flow_graph/param/test_code_basis.py`. Do not edit by hand. This is a study, "
             "not a professional engineer's stamp.", '',
             '| Rev | Description | Date |', '| --- | --- | --- |',
             '| A | First issue. Editions, and the governing clause for each check document. | 2026-10-15 |',
             '| B | Renumbered AQS-STD-007 (AQS-STD-002 belongs to MATERIALS_STD.md); file renamed from AQS-STD-002_CODE_BASIS.md. | 2026-10-24 |',
             '| C | Rewritten to DOC_STYLE (AQS-DOC-002) for a reader new to the project: purpose and scope, terms, captions; sections renumbered. Editions and '
             'clauses unchanged. | 2026-10-24 |',
             '| D | Owner decision Q-018: the latest published edition of every standard applies, and the most recent revision governs a conflict. Table 3.1 is '
             'now the single source of editions for the whole repository; Table 4.1 clauses carried from earlier editions are listed as assumptions to verify. | 2026-10-24 |', '',
             '## 1. Purpose and scope', '',
             'The plant is checked against published codes and standards. This page fixes which edition of each standard applies (Table 3.1) and, for each check '
             'document, which clause governs each check (Table 4.1). Where two standards cover the same point, the most restrictive requirement governs.', '',
             'Each check document carries its own copy of its rows in a "Code basis (X-STD-01)" section, written by the same generator. A check document that lacks '
             'that section, or a check without a governing clause, fails `test_code_basis.py`.', '',
             'Table 3.1 is the single source of editions. Every citation in the repository, in any document, generator or data file, must name the edition given '
             'there; `flow_graph/param/test_code_editions.py` fails on any other. A clause number or value taken from an earlier edition is recorded as an assumption '
             'until it is checked against the edition in force.', '',
             'This page does not quote clause text, and it is not a permit or a code review by the authority having jurisdiction.', '',
             '## 2. Terms', '',
             '- Check document: a page that tests the design against a code requirement, for example a separation, access or egress check.',
             '- Governing clause: the clause, with its standard and edition, that a check is tested against.',
             f'- Edition: the year of the standard that applies. A citation such as {_CB.cite("NFPA 101")} or {_CB.cite("ISO 7010")} names the edition. '
             'Amendments to an edition apply with it.',
             '- NFPA: National Fire Protection Association. ISO: International Organization for Standardization. IEC: International Electrotechnical Commission. '
             'IEEE: Institute of Electrical and Electronics Engineers. UL: UL Standards & Engagement.',
             '- IBC, IFC: the International Building Code and the International Fire Code (International Code Council). NEC: the National Electrical Code, NFPA 70.',
             '', 'Other abbreviations are in `docs-authority/GLOSSARY.md`.', '',
             '## 3. Editions', '', 'Table 3.1. Editions in force, with how each was confirmed on 2026-10-24', '',
             '| Standard | Edition | Confirmed by |', '| --- | --- | --- |']
    lines += [f'| {a} | {b} | {c} |' for a, b, c in std_rows]
    lines += ['', "ASTM editions are the two-digit year suffix of the designation. Where the third column says to confirm, the edition comes from a search listing "
             "rather than the publisher's own page; assumption A-M-333 records it.", '',
              '## 4. Checks', '', 'Table 4.1. Governing clause for each check', '', '| Document | Check | Governing clause |', '| --- | --- | --- |']
    lines += [f'| `{_CB.PATHS[k]}` | {a} | {b} |' for k in _CB.B for a, b in _CB.B[k]]
    return ('\n'.join(lines) + '\n').encode('utf-8')


# ---- the payload faces and the census-book bridge -------------------------------

_ACTION_KEYS = ['action_id', 'node', 'parameter', 'guide_word', 'action', 'closing_task', 'status']
_SIF_KEYS = ['id', 'unit', 'initiator', 'cause', 'effect', 'final_element', 'SIL', 'voting', 'source']


def _instr_book(m, inputs):
    """The AQS-CTL-001 census book, composed from the landed census family.
    An absent inventory payload takes the v1 missing-file branch (the empty
    face: no rows, no flags, no authored loops - the sandbox render branch);
    a present-but-incomplete lane raises through the family's loud coverage
    gate, as the family's contract holds."""
    if inputs.get('other_inventory') is None:
        N = _INV._node_view(m)
        return {'rows': [], 'flags': [], 'auth_rows': 0,
                'boundary_units': sorted(u for u, n in N.items() if n.get('class') == 'boundary')}
    return _II.instrument_book(m, inputs)


def _csv_bytes(rows, keys):
    """The v1 csv.DictWriter face (CRLF rows, QUOTE_MINIMAL) as bytes - the
    serialization face of the v1 stages' sidecars."""
    s = io.StringIO()
    w = csv.DictWriter(s, keys)
    w.writeheader()
    w.writerows(rows)
    return s.getvalue().encode('utf-8')


# ---- AQS-CTL-001: the instrument index page -------------------------------------

def render_instr_index_md(book, inputs):
    """docs-authority/INSTRUMENT_INDEX.md: the v1 _instr_index.py page
    composition over the census book (rows, flags, auth_rows, boundary
    units): the census-totals line, the PLC distribution, the deviation
    table, the per-unit extension section and the first-60-rows index."""
    rows = book['rows']
    T = collections.Counter(r['type'] for r in rows)
    S = collections.Counter(r['plc'] for r in rows)
    md = ['# Instrument index', '', 'Document number: AQS-CTL-001', 'Revision: A', 'Date: 2026-10-16',
          'Authority: AQS-PLAN-007 X-CTL-01. Generated by `docs-authority/_instr_index.py`; full index in '
          '`docs-authority/inventory/INSTRUMENT_INDEX.csv`. Tags per ISA5_1_2022, signals per IEC61131_2. A-M-193.', '',
          f'{len(rows)} instruments: ' + ', '.join(f'{v} {k}' for k, v in T.most_common()) + '.', '',
          '| PLC | Instruments | AI | DI |', '|---|---|---|---|']
    md += [f"| {k} | {v} | {sum(1 for r in rows if r['plc'] == k and 'AI' in r['signal'])} | "
           f"{sum(1 for r in rows if r['plc'] == k and 'DI' in r['signal'])} |" for k, v in sorted(S.items())]
    md += ['', '## Inventory ranges below the need (should be empty: AQS-INV-004 takes its range from the design pressure)', '',
           '| Tag | Inventory range | Index range | Basis |', '|---|---|---|---|']
    md += [f'| {a} | {b} | {c} | {d} |' for a, b, c, d in book['flags']]
    auth_units = {a[0] for a in _II.AUTH}
    ext = collections.Counter(r['unit'] for r in rows if r['unit'] in auth_units)
    nauth = book['auth_rows']
    md += ['', '## Per-unit extension (2026-10-20): loops authored from the graph for units without AQS-INV-004 instrument rows', '',
           f'{nauth} loops on {len(ext)} units ({nauth - (1 if "AFTERBURNER_FLUE" in ext else 0)} of them on the 61 units that had no AQS-INV-004',
           'instrument rows at all, plus the missing AFTERBURNER_FLUE SIF element). `flow_graph/inventory/other.py` emits instrument rows only',
           'where the unit has a nozzle csv,',
           'liquid inflow (class not farm/product/building/hab), or class hcl_synthesis/pem_electrolyser, and skips the boundary/header/relief',
           'classes; the FOUNDRY/POLYMERS machines, headers, relief stacks, stores and EVAP_ACID_VS therefore had none (EVAP_ACID_VS holds only a',
           'gas-detector row, listed in AQS-SAF-006 and excluded here by rule). The loops above the inventory section are authored in this',
           'generator from node design params, edge rates and cited inventory artifacts; the citation is the basis column of the CSV. Handoff:',
           'if AQS-INV-004 later issues a row with the same tag letters for one of these units, the inventory row wins and the authored row is',
           'skipped (per-letters, no duplicate tags; asserted). Units of graph class "boundary" own no loop: they are trade and',
           f'bookkeeping boundaries (here {", ".join(book["boundary_units"])}), not process units.', '',
           '| Unit | Loops | Measured variables |', '|---|---|---|']
    md += [f"| {u} | {n} | {', '.join(sorted({r['tag'].split('-')[-2] for r in rows if r['unit'] == u}))} |"
           for u, n in sorted(ext.items())]
    md += ['', '## Index (first 60 rows; all rows in the CSV)', '',
           '| Tag | Type | Range | Signal | Loop | Basis |', '|---|---|---|---|---|---|']
    md += [f"| {r['tag']} | {r['type']} | {r['range']} | {r['signal']} | {r['loop']} | {r['basis']} |" for r in rows[:60]]
    return ('\n'.join(md) + '\n').encode('utf-8')


def render_instr_index(m, inputs):
    """The DOCS face of the AQS-CTL-001 page: the census book composed, then
    the page."""
    return render_instr_index_md(_instr_book(m, inputs), inputs)


def render_instr_index_csv(m, inputs):
    """docs-authority/inventory/INSTRUMENT_INDEX.csv: the machine face of the
    census book (the byte-exact golden flow_graph/v2/test_instrument_index.py
    already holds)."""
    return _csv_bytes(_instr_book(m, inputs)['rows'],
                      ['tag', 'unit', 'sector', 'type', 'spec', 'range', 'signal', 'loop', 'plc', 'basis'])


# ---- AQS-SAF-001: the HAZOP census (worksheets and actions) ----------------------

_GASFIRE = {'CRYO_H2', 'CRYO_O2', 'CRYO_CO2'}
_HOT = ('PYRO', 'FURNACE', 'MELT', 'AFTERBURN', 'HTC', 'SIC', 'EVAP', 'DRYER')
_KEEP = ('HNO3', 'ACEX', 'FORM', 'ALD', 'MEAM', 'HTC', 'BUCL', 'IMID')
_SKIP_CLASSES = ('boundary', 'building', 'header', 'recycle_pipe', 'farm', 'rectifier', 'inverter', 'pv', 'product')
_OPEN_ACT = {'relief case': 'state the relief case or atmospheric vent in the duty sheet (unit task 07)',
             'temperature indication': 'add the temperature indication loop to AQS-CTL-001 (unit task 08)',
             'level indication': 'add the level indication loop to AQS-CTL-001 (unit task 08)'}


def _disposition(a, duty6, INS):
    """The 2026-10-19 honesty pass: relief actions close against the unit
    duty sheet's section 6 (the payload face - the hand-authored pages),
    indication actions against the AQS-CTL-001 loop, everything else stays
    open (the trip actions then close in the SIF pass). None = tracked open
    (the AQS-SAF-008 register row)."""
    u, par, gw, act, task = a
    if act == 'relief case':
        return (f'closed: docs-authority/duties/{u}.md section 6 names the case or atmospheric statement (X-SAF-03 C7)'
                if u in duty6 else None)
    if act in ('temperature indication', 'level indication'):
        tag = 'TE' if act.startswith('temperature') else 'LT'
        return (f'closed: {tag} loop of {u} in AQS-CTL-001 (X-CTL-01)' if tag in INS[u] else None)
    return 'open'


def _hazop_census(m, inputs, duty6, index_rows):
    """The AQS-SAF-001 census: one worksheet per unit (its P&ID), the
    deviations per IEC61882_2016 with the safeguards read from the design,
    every action dispositioned. Returns the book dict:
    - nodes: (unit, class, worksheet rows) in graph order;
    - acts: (unit, parameter, guide_word, action, task) in row order;
    - actions: the hazop_actions.csv dict rows at their dispositioned
      (pre-SIF) face - the SIF pass amends the statuses in place;
    - trk: the AQS-SAF-008 register rows; st: the per-action statuses."""
    N = _INV._node_view(m)
    E = _INV._edges(m)
    INS = collections.defaultdict(set)
    for r in index_rows:
        INS[r['unit']].add(r['tag'].split('-')[-2])
    CHK = {r['unit'] for r in (inputs.get('other_inventory') or []) if r['item'] == 'check valve'}
    PUMPED = {r['unit'] for r in (inputs.get('motor_inventory') or []) if 'pump' in r['device'].lower()}
    UP = collections.defaultdict(set)
    for e in E:
        if e['presence'] == 'present' and e.get('phase') == 'L' and (e['rate']['value'] or 0) > 0:
            UP[e['to_unit_id']].add(e['from_unit_id'])
    inflow = collections.Counter(e['to_unit_id'] for e in E
                                 if e['presence'] == 'present' and (e['rate']['value'] or 0) > 0)
    liq = {e['to_unit_id'] for e in E if e['presence'] == 'present' and e.get('phase') == 'L'
           and (e['rate']['value'] or 0) > 0}
    nodes = []
    acts = []
    for uid, n in N.items():
        p = n.get('params') or {}
        c = n.get('class') or ''
        if p.get('presence') == 'absent' or c in _SKIP_CLASSES and uid not in _KEEP:
            continue
        if not inflow[uid]:
            continue
        rb = p.get('relief_basis') or {}
        I = INS[uid]
        W = []

        def row(par, gw, cause, cons, sg, act=None, task=None):
            W.append((par, gw, cause, cons, sg or 'none', act or '-'))
            if act:
                acts.append((uid, par, gw, act, task))
        press = 'P1_kPa_abs' in rb
        pm = uid in PUMPED
        row('flow', 'No/Less', 'upstream unit stopped, pump trip, blocked line',
            'loss of duty' + ('; dry-running pump' if pm else ''),
            'FT low-flow alarm' if 'FT' in I else ('no pump on this unit; loss of duty shows at the downstream flow transmitter' if not pm else None),
            None if ('FT' in I or not pm) else 'pump dry-run protection (low-flow or low-level interlock)', 'X-CTL-03')
        row('flow', 'More', 'control valve fails open, upstream surge', 'overfill or overpressure',
            ('LSH trip' if 'LSH' in I else '') + ('; PSV' if press else ('; open vent' if rb.get('case') == 'atmospheric' else '')) or None,
            None if ('LSH' in I or press or rb.get('case') == 'atmospheric') else 'high-level or high-flow protection', 'X-CTL-03')
        sg = (f"PSV {p.get('relief_mm')} mm, case: {str(rb.get('case'))[:60]}" if press
              else f"open vent DN{rb.get('vent_DN', '?')} (API 2000)") if rb else None
        row('pressure', 'High', 'blocked outlet; fire; thermal expansion', 'loss of containment', sg,
            None if sg else 'relief case', 'X-SAF-04')
        if uid in _GASFIRE:
            row('pressure', 'High', 'external fire on the tube bank', 'wall rupture before relief',
                'fire-case PSV per half; flame detection; water spray; depressuring (AQS-SAF-005)')
        if press:
            row('pressure', 'Low', 'leak, PSV lift, downstream draw', 'air ingress (H2: flammable mixture) or loss of store',
                'PT low alarm' + ('; H2 gas detection (AQS-SAF-005)' if uid == 'CRYO_H2' else ''),
                'PT low-low trip isolating the bank' if uid in _GASFIRE else None, 'X-CTL-03')
        hot = any(k in uid for k in _HOT) or (p.get('design') or {}).get('T_C', 25) > 100
        row('temperature', 'High', 'heater control failure, loss of cooling', 'overtemperature of the wall or product',
            'TE high alarm' if 'TE' in I else None,
            'independent high-temperature trip on the heater' if hot else (None if 'TE' in I else 'temperature indication'),
            'X-CTL-03' if hot else 'detail P&ID')
        if uid.startswith('CRYO') or c == 'cold_box':
            row('temperature', 'Low', 'refrigeration overrun, expansion', 'embrittlement of non-austenitic parts',
                '316L throughout (A-M-167); TE low alarm')
        if uid in liq:
            row('level', 'High', 'inflow above outflow, outlet blocked', 'overflow to the bund',
                'LSH trip of the feed' if 'LSH' in I else None,
                None if 'LSH' in I else 'high-level switch', 'X-CTL-03')
        if uid in liq:
            row('level', 'Low', 'outlet pump runs on, leak', 'pump dry-running',
                'LT low alarm' if 'LT' in I else None, None if 'LT' in I else 'level indication', 'detail P&ID')
        up_p = UP[uid] & PUMPED
        if UP[uid]:
            row('flow', 'Reverse', 'downstream pressure above upstream on a pump stop', 'back-flow of incompatible liquor',
                ('check valve at the pump discharge of ' + ', '.join(sorted(up_p & CHK))) if up_p & CHK
                else ('gravity or vented inlets: no back-pressure source' if not up_p else None),
                None if (up_p & CHK or not up_p) else 'check valve on the pumped inlet', 'X-PIP')
        row('composition', 'Other than', 'wrong reagent connected, upstream upset', 'incompatible reaction',
            'incompatible storage separation (AQS-BLD-011); dedicated couplings', None)
        nodes.append((uid, c, W))
    trk = []
    st = []
    for i, a in enumerate(acts):
        s = _disposition(a, duty6, INS)
        if s is None:
            u = a[0]
            k = '07' if a[1] == 'pressure' else '08'
            s = f"open - tracked HA-{len(trk) + 1:02d} (AQS-SAF-008)"
            trk.append((f'HA-{len(trk) + 1:02d}', f'HZ-{i + 1:03d}', u, f'{a[1]} / {a[2]}',
                        _OPEN_ACT.get(a[3], a[3]), f"{N[u]['sector_id']}-{u}-{k}"))
        st.append(s)
    actions = [dict(action_id=f'HZ-{i + 1:03d}', node=a[0], parameter=a[1], guide_word=a[2], action=a[3],
                    closing_task=a[4], status=st[i]) for i, a in enumerate(acts)]
    return {'nodes': nodes, 'acts': acts, 'actions': actions, 'trk': trk, 'st': st}


def _hazop_counts(book):
    """The disposition-pass counts the page and register print: closed at
    issue, trip actions left for the SIF pass, tracked open."""
    st = book['st']
    n_trk = len(book['trk'])
    n_cls = sum(1 for s in st if s.startswith('closed'))
    n_sif = len(st) - n_trk - n_cls
    return n_cls, n_sif, n_trk


def render_hazop_md(m, inputs):
    """docs-authority/HAZOP.md: the v1 _hazop.py page - the study worksheets,
    the actions-by-kind table and the disposition counts (the page predates
    the SIF amend: its counts are the disposition-pass counts)."""
    book = _hazop_census(m, inputs, inputs.get('duty_relief6') or (), _instr_book(m, inputs)['rows'])
    nodes = book['nodes']
    acts = book['acts']
    n_cls, n_sif, n_trk = _hazop_counts(book)
    A = collections.Counter(a[3] for a in acts)
    md = ['# HAZOP worksheets', '', 'Document number: AQS-SAF-001', 'Revision: A (study)', 'Date: 2026-10-16',
          'Authority: AQS-PLAN-007 X-SAF-01. Generated by `docs-authority/_hazop.py`; actions in `docs-authority/hazop_actions.csv`. '
          'Method IEC61882_2016. A-M-195.', '',
          '| Rev | Description | Date |', '|---|---|---|',
          '| A | First issue: study HAZOP worksheets from the generated design. | 2026-10-16 |',
          '| B | Purpose and scope added per the documentation style guide (AQS-DOC-002); sections numbered. No deviation, cause, safeguard or action changed. | 2026-10-25 |', '',
          '## 1. Purpose and scope', '',
          'This page carries the study HAZOP worksheets: for every node of the generated design, the deviations, their causes and the safeguards, with the action '
          'list. It is a design-derived study HAZOP and does not replace a facilitated team HAZOP; the team review signs off rev B of the record. Method IEC 61882 '
          '(IEC61882_2016).', '',
          'This is a design-derived study HAZOP: deviations, causes and safeguards come from the generated design. It does not replace a facilitated team HAZOP; '
          'the team review signs off rev B.', '',
          f'{len(nodes)} nodes, {sum(len(x[2]) for x in nodes)} deviations, {len(acts)} actions: {n_cls} closed at issue against cited artifacts (duty sheet '
          f'section 6 relief statements, X-SAF-03 C7; AQS-CTL-001 indication loops), {n_sif} trip actions close in the SIF pass (AQS-CTL-003, '
          f'`docs-authority/_sif.py`), {n_trk} tracked open in the action register AQS-SAF-008 (`docs-authority/HAZOP_ACTION_REGISTER.md`) with owner tasks in '
          'plan terms.', '', '## 2. Actions by kind', '', 'Table 2.1. Actions by kind', '', '| Action | Count | Closing task |', '|---|---|---|']
    md += [f'| {k} | {v} | {", ".join(sorted({a[4] for a in acts if a[3] == k}))} |' for k, v in A.most_common()]
    md += ['', '## 3. Worksheets', '']
    for u, c, W in nodes:
        md += [f'### {u} ({c})', '', '| Parameter | Guide word | Cause | Consequence | Safeguard | Action |', '|---|---|---|---|---|---|']
        md += [f'| {a} | {b} | {cc} | {d} | {e} | {f} |' for a, b, cc, d, e, f in W] + ['']
    return ('\n'.join(md) + '\n').encode('utf-8')


def render_hazop_register_md(m, inputs):
    """docs-authority/HAZOP_ACTION_REGISTER.md: the AQS-SAF-008 register of
    the tracked-open actions with their owner tasks."""
    book = _hazop_census(m, inputs, inputs.get('duty_relief6') or (), _instr_book(m, inputs)['rows'])
    trk = book['trk']
    n_cls, _n_sif, n_trk = _hazop_counts(book)
    reg = ['# HAZOP action register', '', 'Document number: AQS-SAF-008', 'Revision: A', 'Date: 2026-10-19',
           'Authority: AQS-PLAN-007 X-SAF-01. Generated by `docs-authority/_hazop.py` together with `docs-authority/hazop_actions.csv`.', '',
           'Every HAZOP action is either closed against a cited artifact (the status column of hazop_actions.csv names it) or listed here',
           'with its owner task in AQS-PLAN-007 terms. No row is silently open. A register item closes when its owner task issues the',
           'artifact - duty sheet section 6 for the relief items, the AQS-CTL-001 loop for the indication items - and this generator is',
           'rerun; the row then leaves this register.', '',
           'Handoff (not writable from the docs lane): the indication items need their TE/LT loops added to AQS-CTL-001 by the X-CTL-01',
           'lane (flow_graph/inventory/other.py) once setpoints exist; the relief items need the unit duty sheets (unit tasks 01/02 first).', '',
           '| Register id | HAZOP action | Node | Deviation | Open action | Owner task (AQS-PLAN-007) |', '|---|---|---|---|---|---|']
    reg += [f'| {a} | {b} | {c} | {d} | {e} | {f} |' for a, b, c, d, e, f in trk]
    tail = (f'{n_trk} open engineering actions on {len({r[2] for r in trk})} units: '
            + ', '.join(sorted({r[2] for r in trk})) + '.') if trk else 'No open engineering actions.'
    reg += ['', tail]
    return ('\n'.join(reg) + '\n').encode('utf-8')


# ---- AQS-CTL-003: the SIF pass ---------------------------------------------------

_SIL2_KEYS = ('PYRO', 'AFTERBURN', 'HCL', 'MELT')


def _sif_book(actions, index_rows):
    """The AQS-CTL-003 SIF pass over the dispositioned actions: one function
    per trip action (the calibrated risk graph of IEC61511_2016 part 3
    annex D is rule text), one per AQS-CTL-001 high-level switch (feed trip,
    no SIL - basic control alarm), the four gas/flame/area functions of
    AQS-SAF-005 and the ZNBR2 purge basis. The initiator-membership gate
    needs the index lane (the v1 assert); an absent lane takes the v1
    missing-file branch. The actions' statuses amend in place (the v1
    hazop_actions.csv write-back, composed here). Returns the SIF rows."""
    tags = collections.defaultdict(dict)
    for r in index_rows:
        if int(r['tag'].split('-')[-1]) < 90:
            tags[r['unit']].setdefault(r['tag'].split('-')[-2], r['tag'])
    ALL = {r['tag'] for r in index_rows}
    S = []

    def sif(unit, init, cause, effect, final, sil, src):
        S.append(dict(id=f'SIF-{len(S) + 1:03d}', unit=unit, initiator=init, cause=cause, effect=effect,
                      final_element=final, SIL=sil, voting='1oo2' if sil == 2 else '1oo1', source=src))
    for a in actions:
        if a['closing_task'] != 'X-CTL-03':
            continue
        u = a['node']
        t = tags[u]
        if a['action'].startswith('independent high-temperature'):
            sif(u, f"{u}-TE-90 (independent element; not {t.get('TE', 'the control TE')})", 'temperature high-high',
                'heater supply off', 'heater contactor, de-energise',
                2 if any(k in u for k in _SIL2_KEYS) else 1, a['action_id'])
        elif a['action'].startswith('PT low-low'):
            sif(u, t.get('PT', f'{u}-PT-01') + ' + second PT', 'pressure low-low (leak)',
                'close bank isolation valves, stop compressor, alarm',
                'bank outlet ESD valves (one per half), fail closed', 2, a['action_id'])
        else:
            sif(u, t.get('FT', t.get('LT', u)), 'flow or level low-low', 'pump stop', 'pump starter, de-energise',
                1, a['action_id'])
    for u, t in sorted(tags.items()):
        if 'LSH' in t:
            sif(u, t['LSH'], 'level high-high', 'close feed valve / stop feed pump', 'feed valve fail closed',
                0, 'AQS-CTL-001 LSH')
    sif('CRYO_H2 area', 'H2 gas detectors 2oo3', 'H2 at 25 % LFL',
        'trip H2O_ELYZ and its rectifier, close H2 bank ESD valves, purge ventilation to high',
        'rectifier breaker, ESD valves', 2, 'AQS-SAF-005, NFPA 2, NFPA 69')
    sif('CRYO_H2 / CRYO_O2', 'UV/IR flame detectors 2oo2', 'flame at a receiver',
        'water spray on, depressuring valves open (API 521 5.20)',
        'deluge valve, depressuring valves fail open', 2, 'AQS-SAF-005')
    sif('CRYO_O2 area', 'O2 detectors 2oo3', 'O2 above 23.5 %',
        'close O2 bank and IA-ELY-O2 isolation, ventilation to high', 'ESD valves fail closed', 1, 'AQS-SAF-005')
    sif('ZNBR2', 'H2 detectors in the headspace 1oo2', 'H2 at 25 % LFL in the purge',
        'stop charging, purge fan to high', 'charge contactor', 1, 'NFPA 855, NFPA 69, ess_tf purge basis')
    if ALL:
        bad = [s['initiator'].split()[0] for s in S if s['initiator'].split()[0].count('-') >= 2
               and s['initiator'].split()[0] not in ALL and 'TE-90' not in s['initiator']]
        assert not bad, f'SIF initiators missing from AQS-CTL-001: {bad[:5]}'
    closed = {s['source']: s['id'] for s in S}
    for a in actions:
        if a['action_id'] in closed:
            a['status'] = f"closed by {closed[a['action_id']]} (AQS-CTL-003)"
    return S


def _ctl_books(m, inputs):
    """The one shared chain of the two v1 stages (the electrical-wave
    one-shared-pure-chain idiom): the HAZOP census, then the SIF pass over
    it (which amends the actions' statuses to their committed face)."""
    irows = _instr_book(m, inputs)['rows']
    book = _hazop_census(m, inputs, inputs.get('duty_relief6') or (), irows)
    sifs = _sif_book(book['actions'], irows)
    return book, sifs


def render_hazop_actions_csv(m, inputs):
    """docs-authority/hazop_actions.csv at its committed post-SIF face: the
    v1 doc_hazop write amended by the doc_sif pass, composed in memory (the
    EW_CELLS composer precedent - the pre-SIF face was an intermediate the
    regen never kept)."""
    book, _sifs = _ctl_books(m, inputs)
    return _csv_bytes(book['actions'], _ACTION_KEYS)


def render_cause_effect_md(m, inputs):
    """docs-authority/CAUSE_EFFECT.md: the v1 _sif.py page - the SIF table
    with the SIL targets, voting and sources, and the open-action count
    after the SIF pass."""
    book, sifs = _ctl_books(m, inputs)
    actions = book['actions']
    K = collections.Counter(s['SIL'] for s in sifs)
    op = sum(1 for a in actions if a['status'].startswith('open'))
    md = ['# Safety instrumented functions and cause and effect', '', 'Document number: AQS-CTL-003', 'Revision: A',
          'Date: 2026-10-16',
          'Authority: AQS-PLAN-007 X-CTL-03. Generated by `docs-authority/_sif.py` from AQS-SAF-001 and AQS-CTL-001. IEC61511_2016. '
          'Study. A-M-197.', '',
          f"{len(sifs)} functions: SIL 2 {K[2]}, SIL 1 {K[1]}, no SIL (basic control trip) {K[0]}. HAZOP actions open after the SIF pass: "
          f"{op} (tracked in AQS-SAF-008 with owner tasks).", '',
          'Logic solver: a safety PLC with its own I/O, separate from the basic control PLCs; de-energise to trip; bypasses only under permit with '
          'a timer. SIL 2 loops use 1oo2 sensors; proof-test interval 1 year (AQS-OPS-002).', '',
          '| SIF | Unit | Initiator | Cause | Effect | Final element | SIL | Voting | Source |',
          '|---|---|---|---|---|---|---|---|---|']
    md += [f"| {s['id']} | {s['unit']} | {s['initiator']} | {s['cause']} | {s['effect']} | {s['final_element']} | {s['SIL'] or '-'} | "
           f"{s['voting']} | {s['source']} |" for s in sifs]
    return ('\n'.join(md) + '\n').encode('utf-8')


def render_sif_list_csv(m, inputs):
    """docs-authority/sif_list.csv: the machine face of the SIF book."""
    _book, sifs = _ctl_books(m, inputs)
    return _csv_bytes(sifs, _SIF_KEYS)


# ---- AQS-CTL-002: control philosophy and PLC architecture ------------------------

SPARE, CH, W_MOD, W_CPU = float('0.20'), 16, float('2.0'), float('12.0')
# Sectors whose PLC gets a redundant CPU pair, each with the reason. A sector is here when losing its controller would put the
# occupants, their air, water or food, or the plant power at risk before the controller can be repaired.
CRIT = {
    'HAB': 'the occupied habitat',
    'FARM': 'food and the grow-bed air loop of the habitat',
    'NUT': 'nutrient dosing of the grow beds (FARM)',
    'WTR': 'drinking water and sanitation for the occupants',
    'CRYO': 'oxygen and hydrogen storage and the habitat air handling',
    'GAS': 'the hydrogen and oxygen headers and their relief',
    'ELEC': 'plant power and the critical bus (PV, flow battery, genset and fuel cell are ELEC units)',
    'PUMPED_HYDRO': 'the backup energy store of the critical bus',
    'GEO': 'the ground-source heat pumps',
}
# Sectors kept on a single CPU by decision, with the reason (AQS-OQ-001).
SINGLE_BY_DECISION = {
    'HEAT': 'owner decision 2026-10-24 (AQS-OQ-001 Q-014): HEAT holds the insulated thermal stores (Q1 to Q4 tiers) and '
            'their heat exchangers. A controller outage stops heat moving between the stores; the stores keep their heat, '
            'losing only their standing loss. It is not a life-support or power function.',
}
_MAP = {'PLC digital I/O point': 'DI', 'motor starter (contactor + overload)': 'DO',
        'compressor contactor + overload': 'DO', 'solenoid driver channel': 'DO', 'variable-frequency drive': 'AO',
        'BLDC driver': 'BUS', 'stepper driver': 'BUS'}


def render_plc_arch_md(m, inputs):
    """docs-authority/CONTROL_ARCH.md: the v1 _plc_arch.py page - one PLC per
    sector, the I/O points from the census book (AI/DI) and the electronics
    rows of the other inventory (DO/AO/fieldbus), modules of 16 channels
    with 20 % spare, the redundant CPU pairs of the declared CRIT table and
    the single-CPU owner decision."""
    assert not set(CRIT) & set(SINGLE_BY_DECISION)
    io = collections.defaultdict(collections.Counter)
    for r in _instr_book(m, inputs)['rows']:
        io[r['sector']]['AI' if 'AI' in r['signal'] else 'DI'] += 1
    for r in inputs.get('other_inventory') or []:
        if r['category'] == 'electronics' and r['item'] in _MAP and r['sector'] != 'CONTROL':
            io[r['sector']][_MAP[r['item']]] += int(r['qty'])
    rows = []
    T = collections.Counter()
    for s in sorted(io):
        c = io[s]
        mods = {k: math.ceil(c[k] * (1 + SPARE) / CH) for k in ('AI', 'AO', 'DI', 'DO')}
        red = s in CRIT
        W = (sum(mods.values()) * W_MOD + W_CPU * (2 if red else 1))
        rows.append((s, c, mods, red, W))
        T.update(c)
        T['mods'] += sum(mods.values())
        T['W'] += W
    md = ['# Control philosophy and PLC architecture', '', 'Document number: AQS-CTL-002', 'Revision: B', 'Date: 2026-10-25',
          'Authority: AQS-PLAN-007 task X-CTL-02; assumption A-M-194. Generated by `docs-authority/_plc_arch.py` from the instrument index '
          'AQS-CTL-001 and the inventory AQS-INV-004; do not edit this page by hand. Study.', '',
          '| Rev | Description | Date |', '|---|---|---|', '| A | First issue | 2026-10-16 |',
          '| B | Purpose and scope added; text rewritten to the documentation style guide (AQS-DOC-002). No controller, point count or decision changed. | 2026-10-25 |', '',
          '## 1. Purpose and scope', '',
          'The plant is run by programmable logic controllers (PLCs), which read the instruments and drive the pumps, valves and other actuators. '
          'This page states the control philosophy: how the controllers are divided, which of them are duplicated, how safety and fire functions are '
          'kept apart from basic control, and how the controllers are networked and programmed. It then counts the input and output (I/O) points of '
          'each controller and sizes its I/O modules and its 24 V supply.', '',
          '## 2. Control philosophy', '',
          '- Each sector has its own PLC, so that a fault in one sector stays in that sector. The plant runs from the set-points in the flow graph. '
          'Every control loop is a single-input, single-output proportional-integral (PI) loop unless the design of the unit calls for a cascade.',
          '- A sector whose controller, if lost, would put the occupants, their air, water or food, or the plant power at risk before it could be repaired '
          'has a redundant pair of central processing units (CPUs). The pair switches over without a bump in the outputs, and it has two 24 V supplies fed '
          'from the critical bus, which is backed by a stored-energy supply to NFPA 111. These sectors and the reasons are listed in Table 3.1. Every other '
          'sector has a single CPU.',
          '- Safety trips are not part of the basic control PLCs. They are handled by the safety functions of task X-CTL-03, which follow the hazard and '
          'operability study (HAZOP) of task X-SAF-01. The fire alarm is a separate panel to NFPA72_2025; it sends signals to the PLCs and never receives them.',
          '- All PLCs, the operator screens (HMIs) and the data historian are on one fibre-optic ring using the Media Redundancy Protocol (MRP) of IEC62439_2. '
          'A single cut in the ring is recovered within 200 ms. Brushless DC (BLDC) motor drivers and stepper drivers are on a fieldbus within each sector.',
          '- The programs are written in IEC61131_3 structured text, kept in the repository, and simulated against the flow graph before they are loaded into '
          'the controllers (task X-CTL-04).', '',
          '## 3. Redundant CPU pairs', '',
          'Table 3.1 lists the sectors whose PLC has a redundant CPU pair.', '',
          'Table 3.1. Sectors with a redundant CPU pair', '',
          '| Sector | Why its controller is redundant |', '|---|---|'] + [f'| {s} | {why} |' for s, why in sorted(CRIT.items())] + [
          '', 'The following sectors are kept on a single CPU by decision of the project owner:', ''] + \
          [f'- {s}: {why[0].upper() + why[1:]}' for s, why in sorted(SINGLE_BY_DECISION.items())] + ['',
          '## 4. Input and output points and modules', '',
          f'Table 4.1 counts the analogue inputs (AI), analogue outputs (AO), digital inputs (DI), digital outputs (DO) and fieldbus drives of each PLC, and '
          f'the number of I/O modules needed. Each module has {CH} channels, and {SPARE * 100:.0f} % of the channels are kept spare. The last column is the '
          'load of the PLC on its 24 V supply.', '',
          'Table 4.1. I/O and modules by PLC', '',
          '| Sector PLC | AI | AO | DI | DO | Fieldbus drives | Modules AI/AO/DI/DO | CPU | 24 V load W |', '|---|---|---|---|---|---|---|---|---|']
    md += [f"| PLC-{s} | {c['AI']} | {c['AO']} | {c['DI']} | {c['DO']} | {c['BUS']} | {m['AI']}/{m['AO']}/{m['DI']}/{m['DO']} | "
           f"{'redundant pair' if red else 'single'} | {W:.0f} |" for s, c, m, red, W in rows]
    md += [f"| Total | {T['AI']} | {T['AO']} | {T['DI']} | {T['DO']} | {T['BUS']} | {T['mods']} modules | "
           f"{sum(1 for r in rows if r[3])} redundant of {len(rows)} | {T['W']:.0f} |", '',
           f"The control system draws about {T['W'] / 1000:.2f} kW from the 24 V supplies, which is within the critical load of AQS-ELEC-007.", '',
           'The module count in AQS-INV-004 (item OF-07) uses a different basis, the number of points divided by 16 with no spare, and is superseded by '
           'Table 4.1. The DI count adds the high-level switches of the instrument index to the digital points of the inventory. If the inventory already '
           'counts those switches, the DI count is 113 too high, which errs on the safe side.']
    return ('\n'.join(md) + '\n').encode('utf-8')


# ---- the registry ---------------------------------------------------------------
# The declared ordered list: the CODE_BASIS page, then the section J stage
# order (doc_hazop, doc_instr_index, doc_sif, doc_plc_arch), each stage's
# outputs in its manifest order. The render/__init__.py aggregate import
# composes these into RENDERS after the safety wave's entries.

DOCS = [
    ('docs-authority/CODE_BASIS.md', render_code_basis),
    ('docs-authority/HAZOP.md', render_hazop_md),
    ('docs-authority/HAZOP_ACTION_REGISTER.md', render_hazop_register_md),
    ('docs-authority/hazop_actions.csv', render_hazop_actions_csv),
    ('docs-authority/INSTRUMENT_INDEX.md', render_instr_index),
    ('docs-authority/inventory/INSTRUMENT_INDEX.csv', render_instr_index_csv),
    ('docs-authority/CAUSE_EFFECT.md', render_cause_effect_md),
    ('docs-authority/sif_list.csv', render_sif_list_csv),
    ('docs-authority/CONTROL_ARCH.md', render_plc_arch_md),
]

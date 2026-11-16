"""The electrical-chain renderer wave (the ledger section D document family,
plus sizing/EW_CELLS.md, the section E row the chain is coupled to). Reference
writers: docs-authority/_load_list.py, _one_line.py, _ew_busbar.py,
_power_sizing_doc.py, _ew_sizing.py, and the _rect_ew_sizing.py interlock the
one-line reads over subprocess stdout. Pure functions Model -> document bytes
(seven documents -- the five above plus the cable schedule and the hazardous
area page -- plus the LOAD_LIST and BUSBAR and ONE_LINE machine sidecars and
the HAZ_AREA.csv sidecar, the U2a interlock transports the v1 chain passed as
files), porting the v1 doc templates exactly (the same headers, document
numbers, revision lines, table shapes, number formats and basis texts). The
acceptance is byte-exact reproduction of the committed files
(flow_graph/v2/test_render_electrical.py, and the clearance acceptance of
flow_graph/v2/test_render_clearances.py).

Compositions in memory (the EVAP X-STD-01 pattern of render/sizing_docs.py):
- the load_list / one_line interlock: v1 passed LOAD_LIST.json as a file; here
  the quantised sidecar rows are composed in memory and the one-line consumes
  them, so the bus arithmetic is identical to the v1 file hand-off;
- the one-line and power-sizing X-STD-01 code-basis appends: the body is
  stripped of any code-basis block and the block is appended in memory
  (flow_graph.param.code_basis.block, the single source);
- the EW_CELLS triple-writer handshake (ew_sizing_doc + doc_test_rigs +
  parametric_model_report, both declared amenders in the manifest): the current
  reference scripts write no EW_CELLS sections (the amends are retired in the
  writers), so the committed document is the _ew_sizing write_md() body alone,
  which is what this renderer reproduces byte-exactly;
- the load_list / ew_sizing / rect_ew subprocess hand-offs (_load_list and
  _one_line and _ew_busbar each re-ran _ew_sizing.py and parsed its stdout
  JSON): the EW row book and the rectifier-channel book are one shared pure
  chain here, computed once per render.

What each function reads (Model.field resolved reads over the composed
overlay; the seed is the committed graph, so passthrough reads are the same
bytes):
- the EW row book: the IA-FEED-01 rate and its params.assay_envelope books,
  the IA-EW* product edge rates, graph revision, and the ew_*/rect_* /
  DIGESTER.ew-cascade-train.* drivers (the float replica of the reference
  writer's chain: the docs print the v1 unrounded books, which the quantised
  graph stamps double-round - the _scrub_liquid_raw pattern of sizing_docs);
- render_load_list: every present node's continuous_kw book, sector and
  electrical_role (the AQS-ELEC-003 census classifying each kW by its own
  stamp note), the SOL_ARK_60K electrical feeds for the bus-fed rows, the
  graph sha256 the Authority line cites (the serialized seed's hash - the
  graph round-trips byte-exactly through the v2 serializer), and the EW rows;
- render_one_line: the graph electrical edges, PV_ARRAY / SOL_ARK_60K params
  (inverters, sections, interconnection), the load-list book, and the
  sizing.power amps_3ph/breaker/rectifier_channel arithmetic over the
  bus_power_factor and rect_* drivers;
- render_busbar: the EW bounding currents and the ew_bar_* drivers, with the
  site gravity from inputs['site_profile'] (the v1 SITE.g() read);
- render_power_sizing: the PV_ARRAY / ZNBR2 / SOL_ARK_60K / BACKUP_GEN /
  FUEL_CELL params books, mvs.electrical (derived, seed-carried), the
  RECTIFIER stamps, the EXT_HALL continuous_kw, and the backup_fuel
  critical_list/rating_kw and sizing.power.rectifier_trims arithmetic.

- render_power_sizing: the PV_ARRAY / ZNBR2 / SOL_ARK_60K / BACKUP_GEN /
  FUEL_CELL params books, mvs.electrical (derived, seed-carried), the
  RECTIFIER stamps, the EXT_HALL continuous_kw, and the backup_fuel
  critical_list/rating_kw and sizing.power.rectifier_trims arithmetic;
- render_cable_schedule: the power circuits of the wire census (the inventory
  family's books, read through functions/inventory) with design current,
  ampacity and drop per NEC, the bus demand from the one-line book (the U2a
  sidecar value composed in memory), and the switchboard, collection-section
  and EW bars (the busbar book);
- render_haz_area_md / render_haz_area_csv: the release-source rows of
  functions/haz_area with the per-unit instrument counts (the committed
  INSTRUMENT_INDEX.csv rows, a declared inputs payload until the instrument
  index census family lands -- the gas_detectors/sif_list disposition of
  inventory_other) and the motor-and-pump counts over the other census rows.

REMAINING (the section D documents NOT ported here; each keeps its reason):
- protection (docs-authority/PROTECTION.md): the physics landed
  (flow_graph/v2/functions/protection.py, golden in test_safety_books.py),
  but the committed PROTECTION.md page is hand-authored -- its figures predate
  the current roof and inverter count and no writer exists in the tree -- so
  there is no generated reference to reproduce byte-exactly; the page refresh
  is the owner lane's and this book is its golden.

Cleared by the inventory landing (each now renders or is covered elsewhere):
- inventory_wire: the WIRE_INVENTORY/.csv and WIRE_FAMILIES.csv block is
  rendered by render/inventory.py (the section D row the section I censuses
  unlock);
- doc_wire_specs: the WIRE_SPECS.md page, the WF-nn.svg cross-sections and
  WIRE_SPECS.json render in render/inventory.py beside the wire families book
  they read;
- doc_motor_fa: MOTOR_FIRST_ARTICLE.md, the MF-nn.svg first articles and
  MOTOR_FA.json render in render/inventory.py beside the motor design books
  and MF sheets they read;
- haz_area and cable_schedule: rendered in this module (above).

Pure: no I/O here - the registry returns bytes and file writing stays outside.
"""
import collections
import csv
import hashlib
import io
import json
import math
import re

from flow_graph.param import backup_fuel as _BF
from flow_graph.param import constants as _C
from flow_graph.param import ew_cells as _EWC
from flow_graph.param import solver as _SOLVER
from flow_graph.param.code_basis import MARK as _CODE_MARK          # X-STD-01 block, single source
from flow_graph.param.code_basis import block as _code_block
from flow_graph.param.sizing import electrochem as _EC
from flow_graph.param.sizing import power as _PWS

from flow_graph.v2.functions import haz_area as _HAZ
from flow_graph.v2.functions import inventory as _INV

EW = 'DIGESTER.ew-cascade-train.'                                   # the EW module driver prefix (A-M-040)
G_BASE_FALLBACK = float('9.80665')                                  # baseline-profile gravity (site.py), when no profile is carried
DAY_MIN = 1440                                                      # min/d, the residence conversion

# NEC 240.6(A) standard ampere ratings in full (the v1 BRK list)
BRK = (15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100, 110, 125, 150, 175, 200, 225, 250, 300, 350, 400, 450, 500,
       600, 700, 800, 1000, 1200, 1600, 2000, 2500, 3000, 4000, 5000, 6000)


def _fld(m, uid, path):
    """A model field: the overlay composed (a dict field with per-key writers
    reads back as one merged dict - Model.field), then the committed seed book.
    Read-only; loud on a missing field."""
    return m.field('node', uid, path)


def _efld(m, sid, path):
    """A resolved edge field (the rates the physics families re-stamp)."""
    return m.field('edge', sid, path)


def _edges(m):
    """The seed edges in order, with each rate read resolved (overlay first):
    the v1 stage read the committed graph file, whose rates the families'
    overlays reproduce."""
    out = []
    for e in m.data['edges']:
        if ('edge', e['stream_id'], 'rate') in m.computed:
            e2 = dict(e)
            e2['rate'] = m.field('edge', e['stream_id'], 'rate')
            out.append(e2)
        else:
            out.append(e)
    return out


def _node_view(m):
    """The seed nodes in order, with params and continuous_kw resolved
    (overlay composed): the node map the v1 stage built from the graph file."""
    out = {}
    for uid, n in m.nodes.items():
        v = dict(n)
        if 'params' in v:
            v['params'] = m.field('node', uid, 'params')
        if 'continuous_kw' in v:
            v['continuous_kw'] = m.field('node', uid, 'continuous_kw')
        out[uid] = v
    return out


def _drv_of(inputs):
    """The resolved driver payload: drivers.json with every entry the site
    profile binds replaced by the profile's value (the v1 DR.load() read,
    minus the validation the solve input already passed). Without a profile in
    the inputs the driver payload is already site-resolved by the caller."""
    d = dict(inputs['drivers'])
    prof = inputs.get('site_profile')
    if prof:
        for grp in prof['groups'].values():
            for e in (grp.get('entries') or {}).values():
                k = e.get('binds')
                if k:
                    d[k] = {f: x for f, x in e.items() if f != 'binds'}
    return d


def _drv(d, key):
    """A driver value, verbatim (the v1 DR.val read)."""
    return d[key]['value']


def _gravity(inputs):
    """Apparent gravity, m/s2: the site profile entry (the v1 SITE.g() read);
    the baseline value stands when the inputs carry no profile."""
    prof = inputs.get('site_profile')
    if not prof:
        return G_BASE_FALLBACK
    return prof['groups']['gravity']['entries']['g_m_s2']['value']


def _seed_bytes(m):
    """The serialized seed graph bytes: the model's seed data through the v2
    serializer (graph_io round-trip contract - a passthrough model reproduces
    the committed file bytes exactly). The v2 serializer's per-node/edge
    `provenance` bookkeeping keys are not part of the engineering graph (v1
    never wrote them and the committed file does not carry them), so a model
    re-solved from a written graph hashes the same seed as one solved from the
    committed file."""
    data = m.data
    nodes = [{k: v for k, v in n.items() if k != 'provenance'} for n in data['nodes']]
    edges = [{k: v for k, v in e.items() if k != 'provenance'} for e in data['edges']]
    if nodes == data['nodes'] and edges == data['edges']:
        return json.dumps(data, indent=2, ensure_ascii=True).encode('utf-8')
    payload = dict(data)
    payload['nodes'] = nodes
    payload['edges'] = edges
    return json.dumps(payload, indent=2, ensure_ascii=True).encode('utf-8')


def _graph_sha(m):
    """The sha256 of the committed graph (the Authority-line citation the v1
    stage took over the graph file)."""
    return hashlib.sha256(_seed_bytes(m)).hexdigest()


def _finish(md, key):
    """The v1 write_doc composition: strip any code-basis block, then append
    the X-STD-01 rows (the composer lane; the file write stayed outside)."""
    body = re.sub(r'\n' + re.escape(_CODE_MARK) + r'.*?(?=\n## |\Z)', '', md, flags=re.S).rstrip('\n') \
        + '\n\n' + _code_block(key)
    return body.encode('utf-8')


# ---- the EW row book (docs-authority/_ew_sizing.py, AQS-DUTY-051) -------------

def _ew_book(m, d):
    """The _ew_sizing.py row book: per-cell bounding current, electrodes, tank,
    liquor, residence and DC power at the AQS-ASSAY-001 element envelope
    (Q-038), the totals, the Q-041 merged alternative, and the rectifier
    channel book of _rect_ew_sizing.py (AQS-ELEC-004). The float replica of
    the reference writer's chain over the same boundary inputs (the seed graph
    rates and the resolved drivers)."""
    R = {e['stream_id']: e['rate']['value'] for e in _edges(m)}
    feed_edge = next(e for e in _edges(m) if e['stream_id'] == 'IA-FEED-01')
    FEED = R['IA-FEED-01']                                          # design feed rate, kg/d (AQS-ASSAY-001 section 3)
    ENV = feed_edge['params']['assay_envelope']['element_envelope']
    REC = _drv(d, 'ew_leach_recovery_design')                       # AQS-ASSAY-001 section 4 upper bound
    DEP_REF = {int(k): x for k, x in _SOLVER.ew_products(d, m.data)['dep'].items()}   # booked deposit rows (X-QA-04)
    FE = _drv(d, 'ew_current_efficiency_design')
    J = _drv(d, 'ew_current_density_A_m2')                          # SCHLESINGER2011
    PH = _drv(d, EW + 'ew_plate_height_m')                          # A-M-040 (AQS-EW-MOD-001)
    PWID = _drv(d, EW + 'ew_plate_width_m')                         # A-M-040 (AQS-EW-MOD-001)
    AP = 2 * PH * PWID                                              # both faces
    PITCH = _drv(d, EW + 'ew_cathode_pitch_m')                      # A-M-038 (50 mm cathode-anode)
    V = _drv(d, 'ew_cell_voltage_V')
    WALL = _drv(d, EW + 'ew_tank_wall_m')                           # AQS-DUTY-051 Rev A
    END = _drv(d, EW + 'ew_tank_end_margin_m')
    SIDE = _drv(d, EW + 'ew_tank_side_margin_m')
    SUMP = _drv(d, EW + 'ew_tank_sump_m')
    TOP = _drv(d, EW + 'ew_tank_cover_m')
    FB = _drv(d, EW + 'ew_tank_freeboard_m')                        # A-M-038 allowances
    SHEET_TO = _drv(d, 'ew_sheet_collection_cell')                  # the forming share books on IA-EW-SHEET (write_graph.process)
    ARR = _drv(d, 'ew_minor_metal_arrangement')                     # Q-041: 'selective' or 'merged'
    assert ARR in ('selective', 'merged'), ARR
    MINOR = tuple(int(n) for n in _drv(d, 'ew_minor_metal_cells'))  # the minor-metal cells (Q-041)
    HOST = MINOR[0]                                                 # the cell that carries the blend in the merged arrangement (A-M-494)
    EL = {n: (el, _C.M[el], z, cls) for n, (el, z, cls) in _EWC.EW_CELLS.items()}
    # the selective single-element ratings, in every arrangement: the merged
    # cell's bounding current is the largest of them (nickel basis, sec. 4)
    SEL_I = {n: _EC.faraday_current_A(FEED * ENV['elements'][EL[n][3]]['fraction'] * REC, EL[n][1], EL[n][2], FE)
             for n in range(1, 10)}
    rows = []
    Hi = float(0)
    for n in range(1, 10):
        el, M, z, env_key = EL[n]
        spec = ENV['elements'][env_key]
        dep = FEED * spec['fraction'] * REC                         # the cell's bounding deposit (equipment sizing basis)
        edge = 'IA-EW-SHEET' if n == SHEET_TO else 'IA-EW-MET-' + str(n)
        booked = R[edge]                                            # the cell's product edge; the forming share books on IA-EW-SHEET
        merged_host = ARR == 'merged' and n == HOST                 # the blend cell (A-M-494)
        idle = ARR == 'merged' and n in MINOR and not merged_host
        I = float(0) if idle else (max(SEL_I[mm] for mm in MINOR) if merged_host else SEL_I[n])
        Nc = 0 if idle else _EC.cathode_count(I, J, AP)
        j = float(0) if idle else I / (Nc * AP)
        if idle:                                                    # not built in this arrangement: no tank, no electrodes
            Li = Wi = Vl = float(0)
            Lo = Wo = Ho = 0
        else:
            Li = Nc * PITCH + 2 * END
            Wi = PWID + 2 * SIDE
            Hi = SUMP + PH + TOP + FB
            Lo, Wo, Ho = [round((x + 2 * WALL) * 1000) for x in (Li, Wi)] + [round((Hi + WALL) * 1000)]
            Vl = Li * Wi * (SUMP + PH + TOP)
            Q = R[[e['stream_id'] for e in _edges(m) if e['to_unit_id'] == 'EW_' + str(n)
                   and e['stream_id'].startswith('IA-EW')][0]] / _drv(d, EW + 'ew_liquor_rho_kg_m3')   # A-M-029
        rows.append(dict(cell='EW_' + str(n), metal=('Pb/Sn/Ni/Cd/Zn blend' if merged_host else el),
                         dep_kg_d=float(0) if idle else dep, dep_ref_kg_d=DEP_REF[n], env_case=spec['case'],
                         edge=edge, booked_kg_d=booked, I_A=I, cathodes=Nc, anodes=Nc + 1, j_A_m2=j,
                         size_mm=[Lo, Wo, Ho], V_liq_m3=Vl, tau_min=Vl / Q * DAY_MIN, P_kW=_EC.dc_power_kW(I, V)))
    tot = dict(I_A=sum(r['I_A'] for r in rows), dep=sum(r['dep_kg_d'] for r in rows),
               dep_ref=sum(r['dep_ref_kg_d'] for r in rows), P_kW=sum(r['P_kW'] for r in rows))
    # Q-041 merged alternative: one combined minor-metal cell at the nickel basis
    mi = max(SEL_I[mm] for mm in MINOR)                             # the selective ratings, in every arrangement
    mc = _EC.cathode_count(mi, J, AP)
    mj = mi / (mc * AP)
    mLi = mc * PITCH + 2 * END
    mWi = PWID + 2 * SIDE
    mLo, mWo, mHo = [round((x + 2 * WALL) * 1000) for x in (mLi, mWi)] + [round((Hi + WALL) * 1000)]
    merged = dict(cell='EW_M', metal='Pb/Sn/Ni/Cd/Zn blend', I_A=mi, cathodes=mc, anodes=mc + 1, j_A_m2=mj,
                  size_mm=[mLo, mWo, mHo], P_kW=_EC.dc_power_kW(mi, V),
                  note='one tank, one channel, one bus run in place of the five minor-metal cells '
                       '(four 250 A frames, four tanks, four bus runs saved)')
    dc_bus = tot['P_kW'] + sum(r['I_A'] for r in rows) * _drv(d, 'ew_bus_drop_V') / 1000
    # the AQS-ELEC-004 rectifier channel book (docs-authority/_rect_ew_sizing.py)
    STD = _drv(d, 'rect_channel_frame_sizes_A')                     # channel frame sizes, A (A-M-044)
    MARGIN = _drv(d, 'rect_channel_margin')
    VRATED = _drv(d, 'rect_channel_rated_V')
    JBAR = _drv(d, 'rect_busbar_J_A_cm2')                           # A-M-041/042; from AQS-PWR-001
    VCELL = _drv(d, 'ew_cell_voltage_V')
    VDROP = _drv(d, 'ew_bus_drop_V')
    EFF = _drv(d, 'rect_efficiency')
    rect_rows = []
    for r in rows:
        c = _PWS.rectifier_channel(r['I_A'], VCELL, VDROP, EFF, STD, MARGIN, VRATED)
        rect_rows.append(dict(cell=r['cell'], I_A=r['I_A'], **c, bar_cm2=c['rated_A'] / JBAR))
    rect_tot = {k: sum(x[k] for x in rect_rows) for k in ('I_A', 'rated_A', 'rated_kW', 'Pdc_kW', 'Pac_kW')}
    return dict(rows=rows, tot=tot, merged=merged, sel_i=SEL_I, minor=MINOR, host=HOST, arr=ARR,
                dc_bus=dc_bus, rect_rows=rect_rows, rect_tot=rect_tot)


# ---- AQS-DUTY-051: the EW cells (sizing/EW_CELLS.md) --------------------------

def render_ew_cells(m, inputs):
    """docs-authority/sizing/EW_CELLS.md: the v1 _ew_sizing.py write_md
    template (the doc_test_rigs / parametric_model_report declared amends are
    retired in the current writers - the committed file is this body)."""
    d = _drv_of(inputs)
    b = _ew_book(m, d)
    rows, tot, merged = b['rows'], b['tot'], b['merged']
    SEL_I, MINOR, HOST, ARR = b['sel_i'], b['minor'], b['host'], b['arr']
    V = _drv(d, 'ew_cell_voltage_V')
    J = _drv(d, 'ew_current_density_A_m2')
    AP = 2 * _drv(d, EW + 'ew_plate_height_m') * _drv(d, EW + 'ew_plate_width_m')
    mi = merged['I_A']

    def v(k):
        return _drv(d, k)

    X = ['# EW_1 to EW_9 cell sizing', '', 'Document number: AQS-DUTY-051', 'Revision: I', 'Date: 2026-11-13',
         'Authority: graph Rev ' + m.data['revision'] + '; AQS-PLAN-007 MET-EW_n-02. Study. Not a PE stamp. '
         'Generated by `docs-authority/_ew_sizing.py` (writes this file). Study values in AQS-REG-002 '
         '(A-M-036 to A-M-040). Drivers from `flow_graph/param/drivers.json` (AQS-PAR-001).', '',
         '| Rev | Description | Date |', '| --- | --- | --- |',
         '| A | First issue. Current, electrodes, tank size, holdup and DC power per cell. | 2026-10-15 |',
         '| B | X-PAR acid-loop decision: current efficiency 0.85 and cell voltage 2.12 V (USBM chloride EW basis). | 2026-10-15 |',
         '| C | Rev AC regeneration: the script writes this duty sheet from the live graph; currents and tank sizes '
         'unchanged (held harvests), residence tracks the Rev AC cascade transit rates. | 2026-10-18 |',
         '| D | The sheet-mass column relabeled copper-equivalent (the bounding Faraday basis it always used); the '
         'feed-metal column marked as the cascade order, not a metal identification; finding 6 added. No per-species '
         'mass is published. | 2026-11-04 |',
         '| E | Owner ruling Q-038: the cascade rate moves to its supply basis - the S08 deposit rows '
         '(AQS-ASSAY-001 section 5) at leach recovery 1.0 - so every cell current, cathode count and tank re-solves '
         'at the element basis; the copper-equivalent bounding convention and the wear-goods closing-by-difference '
         'chain behind it are retired. Demand check and governing statement added to section 2. | 2026-11-04 |',
         '| F | Owner ruling Q-038 (2026-11-05): the equipment of every cell is rated at the AQS-ASSAY-001 element '
         'envelope (table 4.1) - the largest deposit of its own element in any feed case, at the design feed rate '
         'and leach recovery 1.0 - so no case B lot forces a resize (AGENTS.md sizing rule). The booked stream '
         'rates stay at the reference S08 rows; both deposit columns are published. | 2026-11-06 |',
         '| G | Owner ruling Q-041: the minor-metal arrangement is decided from first principles and, no clear '
         'winner existing, carried both ways as a selectable option (driver `ew_minor_metal_arrangement`); section 4 '
         'added with the analysis and the merged-cell sizing. No selective-arrangement figure changed. | 2026-11-06 |',
         '| H | X-QA-04: the booked deposit rows are computed from the feed assay (solver.ew_products: IA-FEED-01 '
         'rate x AQS-ASSAY-001 reference-point element fraction x leach recovery; the lumped other-plateable class '
         'splits evenly over the five minor metals, A-M-470) in place of the S08 booking of the retired 150 kg/d '
         'feed audit; the rows sum to 35.9637 kg/d, the plateable class of the reference feed. No equipment figure '
         'changed - the envelope basis of Rev F still governs it. | 2026-11-10 |',
         '| I | X-QA-05: the Q-041 arrangement became a live solver and sizing option (driver '
         '`ew_minor_metal_arrangement`, assumption A-M-494). `selective` stays the default and no selective figure '
         'changed; `merged` rates the blend on the first minor cell at the nickel basis, reports the other four '
         'minor cells as not built, and keeps their booked element rows (the ledger is arrangement-independent). '
         'Section 4 verdict updated; the nine cascade nodes stay in both arrangements. | 2026-11-13 |', '',
         '## 1. Basis', '',
         '- Equipment rate basis (bounding envelope): the largest fraction of each plateable element found in any '
         'case of the IA-FEED-01 envelope (graph `params.assay_envelope.element_envelope`, the machine copy of '
         'AQS-ASSAY-001 table 4.1) at the design feed rate and leach recovery 1.0 (AQS-ASSAY-001 section 4 upper '
         'bound, driver `ew_leach_recovery_design`). The five minor plateable metals each carry the lumped fraction '
         '- the all-in-one-element reading. Design current per cell I = m z F / (M t CE), current efficiency 0.85 '
         '(USBM_CL_EW chloride EW 0.85-0.90, lower bound; study, A-M-036), molar mass and valence per element.',
         '- Rate basis (booked streams): the booked deposit of each cell is computed from the feed assay (X-QA-04): '
         'IA-FEED-01 rate x reference-point element fraction x leach recovery 1.0, the five minor metals splitting '
         'the lumped other-plateable class evenly (A-M-470). The rows sum to the plateable class of the reference '
         'feed; a balance closes on one feed, the envelope sizes the equipment; no single feed loads every cell at '
         'once (the largest simultaneous load is the reference case).',
         '- Demand check: the plated metal the plant consumes is the forming routes (half the Cu deposit to wire, '
         'half to mill; the Pb/Sn/Ni/Cd/Zn blend to powder - the AQS-DUTY-010 bases) plus the crew goods issue '
         '(the roster textile line, A-M-429), together a fraction of the supply. The supply governs the cascade '
         'rate; the surplus metal exports through the shop finished-goods export (self-sustaining plant rule).',
         '- Cathode current density 200 A/m² (AQS-EW-MOD-001, study). Plate immersed 0.60 × 0.42 m, both faces '
         '0.504 m². Cathode pitch 100 mm with an anode between (50 mm cathode to anode). One more anode than '
         'cathodes.',
         '- Tank inside: length = cathodes × 100 mm + 2 × 75 mm ends; width plate + 2 × 50 mm; depth 150 mm sump + '
         '420 mm plate + 100 mm cover + 80 mm freeboard. Wall 10 mm. Liquor density 1100 kg/m³ (AQS-DUTY-050).',
         '- Cell voltage 2.12 V: USBM_CL_EW 2.1 kWh/kg Cu from cupric chloride at CE 0.85 (study, A-M-039).', '',
         '## 2. Results', '',
         'The envelope deposit column sets the equipment (current, cathodes, tank, rectifier channel, bus). The '
         'booked column is the stream-rate basis, computed from the reference feed at recovery 1.0 (X-QA-04); the '
         'product-edge column shows where the cell plated mass books: the noble and iron harvests leave on their '
         'cell edge, the forming share (Cu and the blend) books on IA-EW-SHEET at the EW_9 collection point.',
         'Under the merged arrangement (driver `ew_minor_metal_arrangement`, A-M-494) the blend plates on the first '
         'minor cell (EW_' + str(HOST) + ', nickel basis) and the other four minor cells report not built: their '
         'current, cathodes and tank are zero, while their booked element rows stay - the ledger is '
         'arrangement-independent (A-M-470).', '',
         '| Cell | Metal | Envelope deposit, kg/d | Governing case | Booked, kg/d | I bounding, A | Cathodes / '
         'anodes | j, A/m² | Tank L × W × H, mm | Liquor m³ | Residence, min | DC kW |',
         '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for r in rows:
        X.append(f"| {r['cell']} | {r['metal']} | {r['dep_kg_d']:.4f} | {r['env_case']} | {r['dep_ref_kg_d']:.4f} | "
                 f"{r['I_A']:.1f} | {r['cathodes']} / {r['anodes']} | {round(r['j_A_m2'])} |"
                 f" {r['size_mm'][0]} × {r['size_mm'][1]} × {r['size_mm'][2]} | {r['V_liq_m3']:.3f} | "
                 f"{round(r['tau_min'])} | {r['P_kW']:.2f} |")
    X += [f"| Total | | {tot['dep']:.4f} | | {tot['dep_ref']:.4f} | {tot['I_A']:.1f} | | | | | | {tot['P_kW']:.2f} |", '',
          '## 3. Findings', '',
          '1. The issued envelope 600 × 420 × 650 mm on every EW node is the cathode plate, not the cell. The sized '
          'tanks above replace it in `params.sizing.size_mm`. The graph `size_mm` and the placement rows are not '
          'changed here; the aisle layout (cell pitch 750 mm) does not hold the sized tanks and was re-placed by '
          '`flow_graph/place_ew_aisle.py` (X-RSZ-03; re-run whenever the cathode counts move).',
          f"2. DC load at the electrodes is {tot['P_kW']:.1f} kW at {tot['I_A']:.0f} A at the bounding envelope "
          f"(CE 0.85, cell 2.12 V; with the {v('ew_bus_drop_V')} V bus drop the channel DC is {b['dc_bus']:.2f} kW "
          'and the rectifier AC input re-solves at efficiency 0.80). The sum of the cell ratings is not a load that '
          'occurs at one time: no single feed case loads every cell to its envelope, and the largest simultaneous '
          'load is the reference case. The graph IA-DC-EW_n edges carry the cell plus bus drop at the bounding '
          'current, written by `flow_graph/param/write_graph.py` (AQS-ELEC-004).',
          f"3. Governing basis: supply. The supply (the booked deposits, {tot['dep_ref']:.1f} kg/d element at "
          'recovery 1.0) exceeds the plated-metal demand - the forming routes and the crew goods line - so the '
          'cascade runs at the dissolved-metal rate and the balance exports through the shop finished-goods line '
          '(IA-GOODS-SHIP). The retired basis (the wear-goods plug at 596.86 kg/d, 149 kg/person/d) booked about 7 '
          'times this current and about 8 times this rectifier load.',
          '4. Side-reaction H₂ on EW_1, EW_2, EW_4 and EW_9 (graph H₂ edges) would add Faradaic current not counted '
          'here. It is held with the AQS-DUTY-016 H₂/Cl₂ discrepancy (EDGE_RATING_DUTY) and needs an owner rate '
          'decision.',
          '5. Materials. The 316L frame in AQS-EW-MOD-001 is a wetted non-electrode metal and is withdrawn under '
          'AQS-STD-002 M3; racks are CPVC or PVC-U. Electrode materials for chloride with anodic Cl₂ (316L cathode, '
          'PbO₂ anode) were reopened as X-MAT-18 and are now titanium cathodes and mixed-metal-oxide anodes '
          '(AQS-STD-002 section 9).',
          '6. Product booking: the plated element mass of every cell books once. The forming share (Cu, Pb, Sn, Ni, '
          'Cd, Zn) rides IA-EW-SHEET from the EW_9 collection point and re-enters the ledger through the melt and '
          'forming products (wire, mill sheet, powder) on the AQS-DUTY-010 bases; the noble and iron harvests leave '
          'on their cell edges to the shop. The Rev D copper-equivalent convention (sheet mass bounding the plated '
          'rate at M_Cu, z = 2) is retired with the wear-goods chain that set it.',
          '7. The case B rows of AQS-ASSAY-001 table 4.1 were the resize trigger of the held design; at this '
          'envelope basis the trigger is closed - a case B lot runs within the sized equipment without a rebuild '
          '(the lot books its own rates on arrival, A-M-460).', '', '## 4. Minor-metal arrangement (Q-041)', '',
          'The five minor-metal cells (EW_4 lead, EW_5 tin, EW_6 nickel, EW_8 cadmium, EW_9 zinc) can stay separate '
          'or be merged into one cell. Owner ruling Q-041 (2026-11-05): decide from first principles - '
          'electrochemistry, current density, selectivity, mass transfer and energy - and if the analysis yields no '
          'clear winner, carry both arrangements as selectable options in the design data. Gold and silver stay on '
          'their own cells in either arrangement.', '',
          '- Selectivity. The published standard reduction potentials are about -0.13 V (lead), -0.14 V (tin), '
          '-0.26 V (nickel), -0.40 V (cadmium) and -0.76 V (zinc) against SHE (published tables, for example the '
          'CRC Handbook of Chemistry and Physics). Lead and tin sit 10 mV apart and co-plate in either arrangement; '
          'separation by potential is impossible. Nickel and cadmium sit 146 mV apart - the same order as the '
          'Nernst swing over the working deposit activities - so the separate arrangement needs per-cell potential '
          'control to hold purity, and without it gives mixed deposits anyway.',
          '- Hydrogen. Zinc plates below the hydrogen potential in the chloride liquor, so part of the zinc current '
          'makes H2 in both arrangements (finding 4). Not a differentiator.',
          '- Energy. The DC load is the plated metal (Faraday), identical in both arrangements.',
          '- Hardware. The merged cell saves four tanks, four rectifier channels (250 A frames, 6 kW of nameplate), '
          'four bus runs and four instrument sets, at a better space-time yield (2 cathodes in one tank against 7 '
          'across five tanks).',
          '- Cadmium. The differentiator. A merged cell carries cadmium into the powder blend; the separate cadmium '
          'cell holds it as a controlled stream (the blend basis itself books the minor metals together, '
          'AQS-DUTY-010, so the ledger is unchanged in either arrangement).',
          '- Verdict: no clear winner, so both are carried. Driver `ew_minor_metal_arrangement` selects '
          '`selective` (the nine-cell cascade as sized in section 2, the default and the graph arrangement today) '
          'or `merged` (the blend on the first minor cell, the other row below). X-QA-05 (2026-11-13, A-M-494): '
          'the option is live in solver.ew() and in this sheet - the merged arrangement rates one blend cell at the '
          'nickel basis and reports the other four minor cells as not built, with every booked element row '
          'unchanged. The graph keeps its nine cascade nodes in both arrangements: the liquor order interleaves '
          'EW_7 between the minor cells, so collapsing the idle nodes stays the held EW-topology unit task.', '',
          '| Arrangement | Current, A | Cathodes | Tanks | Channels | Nameplate, kW | DC kW |',
          '| --- | --- | --- | --- | --- | --- | --- |',
          f"| Selective ({'selected' if ARR == 'selective' else 'alternative'}) | "
          f"{sum(SEL_I[n] for n in MINOR):.1f} | {sum(_EC.cathode_count(SEL_I[n], J, AP) for n in MINOR)} | 5 | 5 | "
          f"7.5 | {sum(_EC.dc_power_kW(SEL_I[n], V) for n in MINOR):.2f} |",
          f"| Merged ({'selected' if ARR == 'merged' else 'alternative'}) | {merged['I_A']:.1f} | "
          f"{merged['cathodes']} | 1 | 1 | 1.5 | {merged['P_kW']:.2f} |", '',
          f"The merged cell's bounding current is the largest single-element current of the five ({mi:.1f} A, "
          'nickel basis): the envelope gives the lumped fraction to one element at a time, so the combined cell '
          'never sees more than that charge per unit time.']
    return ('\n'.join(X) + '\n').encode('utf-8')


# ---- AQS-ELEC-003: the load list (LOAD_LIST.md + LOAD_LIST.json) --------------

_TOK = ('AQS-DUTY-', 'AQS-DSN-', 'AQS-NOTE-PV-REBASE', 'X-PAR-', 'X-MFG-', 'X-SAN-', 'roof_close', 'Faraday', 'DLI',
        'kWh/m3', 'kWh/kg', '/ 24 h', 'house_scrubbers', 'NFPA 110', 'AQS-ELEC-008', 'AQS-ELEC-004', 'AQS-PWR-001',
        'latent', 'COP', 'AQS-EQP-FAB', 'AQS-EQP-NUT', 'CRC_SI')
# Citation tokens: a graph continuous_kw note carrying one of these names its calculation (X-ELS-02 rule, A-M-275).
_LOCKS = {
    'FUEL_CELL': 'AQS-REQ-KW-001 REQ-FC-CONT owner requirement lock; not a vendor nameplate (ELEC unit task 02)',
    'MEOH_FC': 'AQS-REQ-KW-001 REQ-MEOH-FC-CONT booked design point 0.5 kW_dc (Q-039 owner ruling 2026-11-13): '
               'fuel-supported class at the settled S76 5.0 kg/d; installed 1.0 kW stack rating stays standby '
               'capability (SI-DMFC-01 class)',
}
_NULL_OK = {'HYDRO_SET': 'charge/discharge kW model incomplete - honest incomplete (WP-A4, AQS-ESS-001)',
            'MEOH_TANK': 'inventory store; no continuous kW (fuel to MEOH_FC)'}


def _classify(u, kw, note):
    if kw is None:
        return ('null', _NULL_OK.get(u, 'no continuous kW by design'))
    if u in _LOCKS:
        return ('owner-lock', 'owner requirement lock (AQS-REQ-KW-001): ' + _LOCKS[u])
    if note and 'standby-zero on the design day' in note:
        return ('standby-zero', note)
    if note and any(t in note for t in _TOK):
        return ('calculated', note)
    return ('pending', 'study share - basis pending: no calculation cited on the graph stamp (unit task 02)')


def _load_list_book(m, d):
    """The AQS-ELEC-003 census book of docs-authority/_load_list.py: every
    present continuous_kw classified by its own stamp basis, the EW cells
    behind the rectifier, and the bus-fed rows the node stamps miss."""
    N = _node_view(m)
    ew = _ew_book(m, d)['rows']
    DC_BEHIND = {r['cell'] for r in ew}
    rows = []
    for n in m.data['nodes']:
        ck = n.get('continuous_kw')
        if n.get('presence') != 'present' or not isinstance(ck, dict):
            continue                                                # scalar bare ints were converted by X-ELS-02
        u = n['unit_id']
        kw = ck.get('value')
        note = ck.get('note') or ''
        u2 = N[u]
        cls, basis = _classify(u, kw, note)
        rows.append({'unit': u, 'sector': u2.get('sector_id') or '—', 'role': u2.get('electrical_role') or '—',
                     'kw': kw, 'calc': (kw if cls == 'calculated' else None), 'cls': cls, 'basis': basis})
    for r in ew:                                                    # EW cells: DC at the electrode, behind RECTIFIER (AQS-ELEC-004)
        rows.append({'unit': r['cell'], 'sector': (N.get(r['cell']) or {}).get('sector_id') or 'DIGESTER',
                     'role': 'load',
                     'kw': ((N.get(r['cell']) or {}).get('continuous_kw') or {}).get('value')
                           if isinstance((N.get(r['cell']) or {}).get('continuous_kw'), dict) else None,
                     'calc': r['P_kW'], 'cls': 'calculated',
                     'basis': 'AQS-DUTY-051 DC at the bounding current; fed from RECTIFIER (DC, not in the AC sum)'})
    have = {r['unit'] for r in rows}
    for e in _edges(m):                                             # bus-fed loads whose node carries no continuous_kw stamp
        u = e.get('to_unit_id')
        if (e.get('from_unit_id') != 'SOL_ARK_60K' or e.get('presence') != 'present'
                or 'elec' not in (e.get('layers') or []) or u in have or u == 'BOUNDARY_EXPORT' or u in DC_BEHIND):
            continue
        r = (e.get('rate') or {}).get('value')
        if not isinstance(r, (int, float)) or r <= 0:
            continue
        n = N.get(u) or {}
        cls, basis = _classify(u, r, (n.get('continuous_kw') or {}).get('note')
                               if isinstance(n.get('continuous_kw'), dict) else None)
        rows.append({'unit': u, 'sector': n.get('sector_id') or '—', 'role': n.get('electrical_role') or 'load',
                     'kw': float(r), 'calc': (float(r) if cls == 'calculated' else None), 'cls': cls,
                     'basis': basis + '; kW from the ' + e['stream_id'] + ' feed (node has no continuous_kw stamp)'})
        have.add(u)
    rows.sort(key=lambda r: (r['calc'] is None, -(r['calc'] if r['calc'] is not None else (r['kw'] or 0))))
    return rows, DC_BEHIND


def _load_list_summary(rows, dc_behind):
    """The census sums of _load_list.py: class counts, the connected AC load
    and its split, the graph and calculated sums."""
    nc = sum(1 for r in rows if r['cls'] == 'calculated')
    nn = sum(1 for r in rows if r['cls'] == 'null')
    cen = collections.Counter()
    cens = collections.defaultdict(collections.Counter)
    for r in rows:
        cen[r['cls']] += 1
        cens[r['sector']][r['cls']] += 1
    nsb = cen['standby-zero']
    nol = cen['owner-lock']
    npr = [r for r in rows if r['cls'] == 'pending']
    # connected AC load: non-null rows that are loads (generation/storage/bus excluded; EW DC behind RECTIFIER excluded)
    loads = [r for r in rows if r['cls'] != 'null' and r['role'] not in ('generation', 'storage', 'bus')
             and r['unit'] not in dc_behind and (r['kw'] or 0) > 0]
    conn = sum(r['kw'] for r in loads)
    ckw = sum(r['kw'] for r in loads if r['cls'] == 'calculated')
    skw = sum(r['kw'] for r in loads if r['cls'] == 'standby-zero')
    pkw = conn - ckw - skw
    if float('-0.005') < pkw < float('0.005'):
        pkw = float(0)                                              # float residue; the class split is exhaustive on the loads
    gsum = sum(r['kw'] or 0 for r in loads)
    csum = sum((r['calc'] if r['calc'] is not None else r['kw'] or 0) for r in loads)
    pct = float(100) * ckw / conn if conn else float(0)
    lock_list = '; '.join(f"{r['unit']} {r['kw']:.3f} kW"
                          for r in sorted([r for r in rows if r['cls'] == 'owner-lock'], key=lambda r: -(r['kw'] or 0)))
    return dict(nc=nc, nn=nn, cen=cen, cens=cens, nsb=nsb, nol=nol, npr=npr, conn=conn, ckw=ckw, skw=skw,
                pkw=pkw, gsum=gsum, csum=csum, pct=pct, lock_list=lock_list)


def _sidecar_rows(rows):
    """The LOAD_LIST.json machine face: kW quantised to the 3 decimals the
    markdown table publishes (the U2a transport contract; the one-line's bus
    arithmetic consumes exactly these numbers)."""
    return [{'unit': r['unit'], 'role': r['role'], 'kw': round(r['kw'] or 0, 3),
             'calc_kw': (None if r['calc'] is None else round(r['calc'], 3)),
             'basis': (r['basis'] or '').replace('|', '/'), 'class': r['cls'], 'sector': r['sector']} for r in rows]


def render_load_list(m, inputs):
    """docs-authority/LOAD_LIST.md: the v1 _load_list.py display template
    (AQS-ELEC-003 Rev C, X-ELS-02)."""
    d = _drv_of(inputs)
    rows, dc_behind = _load_list_book(m, d)
    s = _load_list_summary(rows, dc_behind)
    cen, cens = s['cen'], s['cens']
    out = [f"""# Load list

Document number: AQS-ELEC-003
Revision: C
Date: 2026-10-21
Authority: AQS-PLAN-007 X-ELS-02; graph sha256 {_graph_sha(m)[:12]}. Generated by `docs-authority/_load_list.py`. Study. Not a PE stamp.

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue. Graph values beside calculated values where a sizing exists. | 2026-10-15 |
| B | X-ELS-02 promotion pass (A-M-275): node stamps aligned to their calculations by write_graph load-basis stamping (MFG_SHOP tool list, LEACH_CSTR_1 agitator, reactor/sanitation feeds, WS_PEROX cell, ZNBR2 discharge rating, GEO_HP lift/COP, foundry notes); provenance classified from the graph notes; explicit pending residuals listed. | 2026-10-19 |
| C | X-ELS-02 closure pass (A-M-301): the 2026-10-19 pending census collapses - A-M-297/299 FAB tool-train and NUT dosing-skid calculations classify calculated; the A-M-283 standby-zero N+1 rows (incl. the RF_HEAT/VAC_IND duty-cycle alternates) classify as policy rows; FUEL_CELL/MEOH_FC are documented as owner requirement locks (AQS-REQ-KW-001), the only rows without a calculation behind them; the GEO source-loop circulator enters the load at its AQS-DUTY-076 draw (A-M-317). | 2026-10-21 |

Status. {s['nc']} of {len(rows)} rows carry a calculated basis. {s['nsb']} rows are standby-zero N+1 policy rows (A-M-283: 0 kW on the design day apart from stated controls parasitics; the connected rating rides params.design with the outage framed there). {s['nol']} rows are owner requirement locks (AQS-REQ-KW-001), the only rows without a calculation behind them (A-M-301 policy): {s['lock_list']}. {s['nn']} rows are null by design. No row remains a study share without a cited basis or owner lock. Where a row is calculated the graph continuous_kw IS the calculated value (Rev B promotion, A-M-275).

Connected AC load {s['conn']:.1f} kW: {s['ckw']:.1f} kW calculated ({s['pct']:.1f} %), {s['skw']:.2f} kW standby policy parasitics, {s['pkw']:.2f} kW study shares.

Loads: graph sum {s['gsum']:.2f} kW; calculated-substituted sum {s['csum']:.2f} kW.

## Census by sector

| Sector | calculated | standby-zero | owner-lock | pending | null | rows |
| --- | --- | --- | --- | --- | --- | --- |"""]
    for sec in sorted(cens):
        c = cens[sec]
        out.append(f"| {sec} | {c['calculated']} | {c['standby-zero']} | {c['owner-lock']} | {c['pending']} | "
                   f"{c['null']} | {sum(c.values())} |")
    out.append(f"| **total** | **{cen['calculated']}** | **{cen['standby-zero']}** | **{cen['owner-lock']}** | "
               f"**{cen['pending']}** | **{cen['null']}** | **{len(rows)}** |")
    out.append("")
    out.append("| Unit | Role | Graph kW | Calculated kW | Basis |")
    out.append("| --- | --- | --- | --- | --- |")
    for r in rows:
        cs = '' if r['calc'] is None else f"{r['calc']:.3f}"
        bs = (r['basis'] or '').replace('|', '/')               # stamp notes may carry ' | ' separators; keep the cell single-column
        out.append(f"| {r['unit']} | {r['role']} | {(r['kw'] or 0):.3f} | {cs} | {bs} |")
    return ('\n'.join(out) + '\n').encode('utf-8')


def render_load_list_json(m, inputs):
    """docs-authority/LOAD_LIST.json: the U2a machine sidecar of the census
    (the interlock transport the one-line consumed as a file)."""
    d = _drv_of(inputs)
    rows, dc_behind = _load_list_book(m, d)
    s = _load_list_summary(rows, dc_behind)
    cen, cens, npr = s['cen'], s['cens'], s['npr']
    sidecar = {'_generated_from': {'graph_sha256': _graph_sha(m), 'generator': 'docs-authority/_load_list.py'},
               'rows': _sidecar_rows(rows),
               'summary': {'calculated': s['nc'], 'pending': len(npr), 'standby_zero': s['nsb'],
                           'owner_lock': s['nol'], 'null': s['nn'], 'rows': len(rows),
                           'graph_sum_kW': round(s['gsum'], 2), 'calc_sum_kW': round(s['csum'], 2),
                           'connected_load_kW': round(s['conn'], 1), 'connected_calculated_kW': round(s['ckw'], 1),
                           'connected_standby_kW': round(s['skw'], 1), 'connected_study_kW': round(s['pkw'], 1),
                           'connected_calculated_pct': round(s['pct'], 1),
                           'by_sector': {sec: dict(cens[sec]) for sec in sorted(cens)}}}
    return json.dumps(sidecar, indent=1).encode('utf-8')


# ---- AQS-ELEC-002: the one-line (ONE_LINE.md + ONE_LINE.json) ------------------

V_BUS = float(480)                                              # the main bus volts (the v1 V=480.0)
PP_V = 208                                                      # the PP-1 panel volts
XF_KVA_LADDER = (15, 30, 45, 75, float('112.5'))                # the kVA ladder the PP-1 transformer is picked from


def _one_line_book(m, d):
    """The bus book of docs-authority/_one_line.py: the graph electrical
    edges, the load-list rows (via the quantised sidecar rows, the U2a
    interlock), the feeder table and the bus totals."""
    PF = _drv(d, 'bus_power_factor')
    rect = _ew_book(m, d)['rect_tot']
    L = {r['unit']: (r['role'], r['kw'], r['calc_kw']) for r in _sidecar_rows(_load_list_book(m, d)[0])}
    el = [e for e in _edges(m) if 'elec' in (e.get('layers') or [])]
    src = [(e['from_unit_id'], e['stream_id'], e['rate']['value']) for e in el
           if e['to_unit_id'] == 'SOL_ARK_60K' and e['rate']['value'] is not None]
    fed = {e['to_unit_id']: (e['stream_id'], e['rate']['value']) for e in el
           if e['from_unit_id'] == 'SOL_ARK_60K' and e['rate']['value'] is not None}
    PK = {n['unit_id']: n.get('params', {}).get('peak_kw') for n in m.data['nodes']
          if isinstance(n.get('params', {}).get('peak_kw'), (int, float))}

    def amps(kw, ph=3, v=V_BUS):
        return _PWS.amps_3ph(kw, v, PF) if ph == 3 else kw * 1000 / (v * PF)

    def brk(a):
        return _PWS.breaker(a, list(BRK))                       # NEC2026 125 %

    g_pv = next(n for n in m.data['nodes'] if n['unit_id'] == 'PV_ARRAY')['params']
    INV = _fld(m, 'SOL_ARK_60K', 'params')
    INVTXT = f"{INV.get('count', 1)} × 60 = {INV.get('kW', 60):.0f} kW inverters"
    rows = []
    for u, (sid, kw) in fed.items():
        if u == 'BOUNDARY_EXPORT':
            continue
        if kw is None:
            continue                                            # unrated Rev AC edge — listed loads only
        rows.append(('SOL_ARK 480 V', u, kw, 'graph ' + sid))
    if 'RECT_EW' not in fed:
        rows.append(('SOL_ARK 480 V', 'RECT-EW (EW_1–EW_9)', rect['Pac_kW'], 'AQS-ELEC-004 bounding AC'))
    skip = set(fed) | {'EW_' + str(i) for i in range(1, 10)} | {'SOL_ARK_60K'}
    for u, (role, kw, c) in L.items():
        if u in skip or role not in ('load', '—'):
            continue
        k = c if c is not None else kw
        if k is None or k <= 0:
            continue
        rows.append(('MCC-1 480 V' if k >= float(1) else 'PP-1 208/120 V', u, k,
                     'AQS-ELEC-003 ' + ('calculated' if c is not None else 'study share')))
    bus = {}
    for bb, _u, k, _bs in rows:
        if k is None:
            continue
        bus[bb] = bus.get(bb, 0) + k
    pp = bus.get('PP-1 208/120 V', 0)
    xf = next(s for s in XF_KVA_LADDER if s >= pp / PF * float('1.25'))
    gen = sum(k for _u, _sid, k in src if k is not None)
    demand = sum(bus.values())
    return dict(PF=PF, rect=rect, src=src, fed=fed, PK=PK, amps=amps, brk=brk, g_pv=g_pv, INV=INV, INVTXT=INVTXT,
                rows=rows, bus=bus, pp=pp, xf=xf, gen=gen, demand=demand)


def render_one_line(m, inputs):
    """docs-authority/ONE_LINE.md: the v1 _one_line.py template (AQS-ELEC-002
    Rev E), closed with the X-STD-01 code-basis block (ONE_LINE rows)."""
    d = _drv_of(inputs)
    b = _one_line_book(m, d)
    src, fed, bus = b['src'], b['fed'], b['bus']
    INV, IC = b['INV'], b['INV'].get('interconnection', {})
    SEC = b['INV'].get('sections', {})
    g_pv = b['g_pv']
    rect = b['rect']
    out = [f"""# Single-line diagram

Document number: AQS-ELEC-002
Former number: AQS-ELEC-001 (renumbered 2026-10-15 to clear a duplicate)
Revision: E
Date: 2026-10-24
Basis: graph Rev BH; AQS-PLAN-007 task X-ELS-03; AQS-ELEC-003 and AQS-ELEC-004.
Source: generated by `docs-authority/_one_line.py` from the electrical edges of the plant graph. Do not edit by hand. This is a study, not a document stamped by a professional engineer.

| Rev | Description | Date |
| --- | --- | --- |
| E | Rewritten to DOC_STYLE (AQS-DOC-002): purpose, terms and captions; method and values unchanged. | 2026-10-24 |
| D | D75 grid export: PV at 200 % of requirement, {b['INVTXT']}, point of common coupling, export meter and interconnection disconnect (IEEE 1547-2018, UL 1741 SB, NEC 2023 705). | 2026-10-15 |
| C | Generated one-line against the load list; buses MCC-1 and PP-1; RECT-EW feeder. | 2026-10-15 |
| B | Inverter feeder 2 AWG; 400 kW retired. | 2026-10-12 |

## Purpose and scope

A single-line (one-line) diagram shows how electrical power flows from the sources to the loads, drawing each three-phase circuit as one line. This page draws the plant's main 480 V bus, lists every load fed from it with its current and breaker size, and compares total demand with the sources and the inverter rating. It covers the main bus, the motor control centre MCC-1, the 208/120 V panel PP-1, the electrowinning rectifier and the grid connection. Cable sizes are in the cable schedule and protection settings in the protection study.

## Terms and method

- Bus: the common conductor that sources feed and loads draw from; here the 480 V bus of the Sol-Ark inverters (`SOL_ARK_60K`).
- Feeder: the circuit from the bus to one load.
- Point of common coupling (PCC): where the plant connects to the utility grid.
- OCPD: overcurrent protective device (breaker or fuse).
- Current is I = P / (√3 × V × power factor), with a study power factor of 0.90. Breakers are the next standard rating in NEC 240.6(A) at or above 125 % of the continuous current.
- A feeder marked "study share" in the Basis column carries an estimated share of a unit's power, not a calculated load.

Figure 1. Single-line diagram of the main bus (stream and edge ids from the plant graph on each line)

```mermaid
flowchart LR
"""]
    for u, sid, k in src:
        out.append(f'  {u}["{u} {k:.2f} kW"] -->|{sid}| BUS')
    out.append(f'  BUS(["SOL_ARK_60K 480 V 3φ, {b["INVTXT"]}"])')
    out.append(f'  BUS --> MCC["MCC-1 480 V {bus.get("MCC-1 480 V", 0):.1f} kW"]')
    out.append(f'  BUS --> XF["T-1 {b["xf"]} kVA 480–208/120 V"] --> PP["PP-1 {b["pp"]:.1f} kW"]')
    for u, (sid, kw) in fed.items():
        out.append(f'  BUS -->|{sid}| {u.replace("-", "_")}["{u} {kw:.2f} kW"]')
    if SEC:
        for i, (k, kva) in enumerate(zip(SEC['inverters'], SEC['xfmr_kVA']), 1):
            out.append(f'  CB{i}["CB-{i} 480 V, {k} inverters, {SEC["breaker_A"][i - 1]} A"] '
                       f'--> TX{i}["{kva:g} kVA 480 V / {SEC["mv_kV"]} kV"] --> MV')
        out.append(f'  MV(["MV collection {SEC["mv_kV"]} kV (AQS-ELEC-008)"])')
        out.append('  CB1 --- BUS')
    out.append(f'  {"MV" if SEC else "BUS"} --> PCC["705.20 disconnect, 705.30 OCPD, ANSI C12.20 bidirectional '
               f'meter"] --> GRID(["Utility PCC, export up to {IC.get("export_peak_kW", 0):.0f} kW"])')
    out.append(f'  BUS --> RECTEW["RECT-EW 9 × 6 V DC channels, {rect["Pac_kW"]:.1f} kW AC"]')
    out.append('```\n')
    out.append('Table 1. Loads on the main bus, largest first\n')
    out.append('| Bus | Load | kW | A | Breaker A | Basis |\n| --- | --- | --- | --- | --- | --- |')
    for bb, u, k, bs in sorted(b['rows'], key=lambda r: (r[0], -r[2])):
        kp = max(k, b['PK'].get(u) or 0)
        a = b['amps'](kp) if '480' in bb else b['amps'](kp, 3, PP_V)
        bs = bs + (f'; feeder on peak {kp:.1f} kW' if kp > k else '')
        out.append(f'| {bb} | {u} | {k:.2f} | {a:.1f} | {b["brk"](a)} | {bs} |')
    out.append(f"""
## Totals

Table 2. Bus totals

| Item | kW |
| --- | --- |
| Sources on the bus (graph edges) | {b['gen']:.2f} |
| Demand on the bus (this page) | {b['demand']:.2f} |
| Inverter rating (SOL_ARK_60K) | {INV.get('kW', 60):.1f} |
| Shortfall against sources | {b['demand'] - b['gen']:.2f} |
| Shortfall against inverter | {b['demand'] - INV.get('kW', 60):.2f} |

## Findings

1. Bus demand at the bounding EW case is {b['demand']:.1f} kW against {b['gen']:.1f} kW of graph sources and {b['INVTXT']}. The RECT-EW feeder alone is {rect['Pac_kW']:.1f} kW. Supply nameplates follow AQS-ELEC-007 bounding case (X-RSZ-02); the gap between graph sources and bus demand is loads without graph feeds, booked in the X-RSZ-07 sweep.
2. Feeders marked "study share" become calculated as each unit's task 02 closes (X-ELS-02).
3. Most loads have no electrical edge on the graph; only RECTIFIER (S17) and GROW_BED (S20) do. The one-line assigns the rest to MCC-1 and PP-1 by size. Graph electrical edges for them belong to X-ELS-02.
4. The 48 V shop and farm rails stay as AQS-PWR-001 behind RECTIFIER (S17). MFG_SHOP's 12 kW share may overlap the 20 kW shop rail; the overlap is resolved with MFG_SHOP task 02.
5. Grid export (D75, owner decision 2026-10-15). PV is sized at {g_pv.get('oversize_factor', 1):.1f} x the balancing nameplate ({g_pv.get('balance_kWp')} of {g_pv.get('nameplate_kw')} kWp). Inverters at the NREL PVWatts DC/AC ratio {INV.get('dc_ac_ratio')}: {b['INVTXT']}. The inverters are split into {INV.get('sections', {}).get('count', '?')} collection sections at 480 V, each through a pad-mount transformer to the {INV.get('sections', {}).get('mv_kV', '?')} kV collection bus; the plant bus hangs on {INV.get('sections', {}).get('plant_bus_on', '?')} (AQS-ELEC-008). Clear-day export at noon with storage full is up to {IC.get('export_peak_kW', 0):.0f} kW, about {IC.get('export_kWh_d_clear', 0):.0f} kWh/d. Interconnection: inverters listed to UL 1741 SB and set to IEEE 1547-2018 Category B reactive power and Category III ride-through, unintentional islanding cleared within 2 s; supply-side connection per NEC 2026 705.11 (the 705.12 120 % load-side rule cannot carry this rating); lockable visible-break disconnect at the point of common coupling per 705.20; bidirectional revenue meter ANSI C12.20 class 0.2; loss of the utility trips export per 705.40, the plant bus stays islanded on storage. Utility service size, available fault current and export limit are set by the serving utility's interconnection study (review item, A-M-110).
""")
    return _finish('\n'.join(out) + '\n', 'ONE_LINE')


def render_one_line_json(m, inputs):
    """docs-authority/ONE_LINE.json: the U2a machine sidecar of the bus table
    (bus kW at the 1 dp, gen/demand at the 2 dp the markdown publishes)."""
    d = _drv_of(inputs)
    b = _one_line_book(m, d)
    sidecar = {'_generated_from': {'graph_sha256': _graph_sha(m), 'generator': 'docs-authority/_one_line.py'},
               'bus': {bb: round(k, 1) for bb, k in b['bus'].items()}, 'xf': b['xf'],
               'gen': round(b['gen'], 2), 'demand': round(b['demand'], 2)}
    return json.dumps(sidecar, indent=1).encode('utf-8')


# ---- the registry (the declared tail; keep at the end, after the renderers) -----


# ---- AQS-BUS-001: the rectifier bus (BUSBAR.md + BUSBAR.json) ------------------

def _shed(w, t, n, dT, g_m_s2, eps):
    """Free convection (vertical-plate laminar, INCROPERA7) plus radiation on
    the outer surface only (CDA_PUB22), W/m, at the allowed rise."""
    SIG = float('5.670e-8')
    Ta = float('313.15')
    T = Ta + dT
    Tf = (T + Ta) / 2
    nu = float('1.6e-5') * (Tf / 300) ** float('1.75')
    k = float('0.0263') * (Tf / 300) ** float('0.8')
    Pr = float('0.71')                                              # air, INCROPERA7 table A.4 fit
    Ra = g_m_s2 / Tf * dT * w ** 3 / nu ** 2 * Pr
    h = float('0.59') * Ra ** float('0.25') * k / w
    P_out = 2 * (w + n * t + (n - 1) * t)
    P_conv = 2 * n * w + 2 * n * t                                  # outer surface radiates; every face convects
    return h * P_conv * dT + eps * SIG * (T ** 4 - Ta ** 4) * P_out


def _bus_size(I, d, g_m_s2):
    """The bar pack: heat balance at the rise, held to the UL891 default
    1000 A/in2 (155 A/cm2). Width steps 10 mm up to 160 mm, then another bar."""
    t = _drv(d, 'ew_bar_t_mm') / 1000
    dT = _drv(d, 'ew_bar_rise_K')
    rho = float('1.724e-8') * (1 + float('0.00393') * (float('313.15') + dT - float('293.15')))
    ul_j = float('1000') / float('6.4516')                          # the UL891 default density, A/cm2
    for n in range(1, 9):
        for wmm in range(20, 170, 10):
            w = wmm / 1000
            A = n * w * t
            if I ** 2 * rho / A <= _shed(w, t, n, dT, g_m_s2, _drv(d, 'ew_bar_emissivity')) \
                    and I / (A * float('1e4')) <= ul_j:
                return dict(n=n, w_mm=wmm, A_cm2=A * float('1e4'), J=I / (A * float('1e4')),
                            q_W_m=I ** 2 * rho / A, drop_V=I * rho * _drv(d, 'ew_bar_L_m') / A * 2)


def _busbar_book(m, inputs):
    """The BUSBAR book: cell current from the EW row book (the AQS-DUTY-051
    bounding current at the element envelope), each bar pack sized, and the
    drop checked against the ew_bus_drop_V budget."""
    d = _drv_of(inputs)
    ew = _ew_book(m, d)['rows']
    cells = [(r['cell'].replace('_', '-'), round(r['I_A'])) for r in ew]
    g_m_s2 = _gravity(inputs)
    rows = [(c, I, _bus_size(I, d, g_m_s2)) for c, I in cells]
    return d, rows, _drv(d, 'ew_bus_drop_V'), _graph_sha(m)


def render_busbar(m, inputs):
    """docs-authority/BUSBAR.md: the v1 _ew_busbar.py doc template (AQS-BUS-001
    rev D, A-M-173)."""
    d, rows, bud, _sha = _busbar_book(m, inputs)
    md = ['# Rectifier bus', '', 'Document number: AQS-BUS-001', 'Revision: D', 'Date: 2026-11-06',
          'Generated by `docs-authority/_ew_busbar.py`. Not a PE stamp. A-M-173.', '',
          '1. Basis. Cell current from `docs-authority/_ew_sizing.py` - the AQS-DUTY-051 bounding current at the '
          'AQS-ASSAY-001 element envelope (owner ruling Q-038, 2026-11-05), not from this page\'s own previous '
          f"issue. Each bar is a pack of {_drv(d, 'ew_bar_t_mm')} mm copper flats spaced one thickness apart "
          '(CDA_PUB22), sized so the I²R heat per metre is shed by free convection (INCROPERA7) and radiation '
          f"(emissivity {_drv(d, 'ew_bar_emissivity')}, painted, CDA_PUB22) at a {_drv(d, 'ew_bar_rise_K'):.0f} K "
          'rise over 40 C, and held to the UL891 default 155 A/cm² (UL891). The heat balance alone allows about '
          '220-250 A/cm² on these bars, so the density rule governs. Rev B used a flat 200 A/cm²; rev C replaces '
          'it; rev D re-solves at the envelope currents.', '',
          "2. Size. Resistivity 1.724e-8 ohm m at 20 C, 0.00393 /K (CDA_PUB22). Go and return run "
          f"{_drv(d, 'ew_bar_L_m')} m each; joints {_drv(d, 'ew_contact_drop_V') * 1000:.0f} mV. Budget "
          f"{bud * 1000:.0f} mV (ew_bus_drop_V, used by the rectifier and the graph).", '',
          '| Cell | A | cm² | Pack | A/cm² | Heat W/m | Drop mV | Within budget |',
          '|---|---:|---:|---|---:|---:|---:|---|']
    for c, I, s in rows:
        tot = s['drop_V'] + _drv(d, 'ew_contact_drop_V')
        md.append(f"| {c} | {I} | {s['A_cm2']:.1f} | {s['n']} x {s['w_mm']} x {_drv(d, 'ew_bar_t_mm')} mm | "
                  f"{s['J']:.0f} | {s['q_W_m']:.0f} | {tot * 1000:.0f} | {'yes' if tot <= bud else 'NO'} |")
    md += ['', '3. Material. Copper C101 bar, painted. No aluminum on a wet aisle.', '',
           '4. Joints. Bolted at the rectifier and at the cell bus; joint overlap at least the bar width.', '',
           '5. Instruments. Cell voltage reads at the cell bus. A thermocouple on the largest bar verifies the rise '
           'at the RECT-EW first article (A-M-173).']
    return ('\n'.join(md) + '\n').encode('utf-8')


def render_busbar_json(m, inputs):
    """docs-authority/BUSBAR.json: the U2a machine face of the busbar table
    (A_cm2 at the 1 decimal the markdown publishes)."""
    d, rows, bud, sha = _busbar_book(m, inputs)
    sidecar = {'_generated_from': {'graph_sha256': sha, 'generator': 'docs-authority/_ew_busbar.py'},
               'rows': [dict(cell=c, A=I, A_cm2=round(s['A_cm2'], 1),
                             pack=f"{s['n']} x {s['w_mm']} x {_drv(d, 'ew_bar_t_mm')} mm", J_A_cm2=round(s['J']),
                             q_W_m=round(s['q_W_m']),
                             drop_mV=round((s['drop_V'] + _drv(d, 'ew_contact_drop_V')) * 1000),
                             within_budget=bool(s['drop_V'] + _drv(d, 'ew_contact_drop_V') <= bud))
                        for c, I, s in rows],
               'budget_mV': round(bud * 1000)}
    return json.dumps(sidecar, indent=1).encode('utf-8')


# ---- AQS-ELEC-007: storage and generation sizing (POWER_SIZING.md) -------------

def _q(x):
    """The v1 q() unwrap: a {'value': v} book reads as v."""
    return (x or {}).get('value') if isinstance(x, dict) else x


def _pf(v, nd=0):
    """The v1 f(): 'not sized' for blanks, thousands-separated decimals for
    numbers, str otherwise."""
    if v is None or v == '':
        return 'not sized'
    return f'{v:,.{nd}f}' if isinstance(v, (int, float)) else str(v)


def _and(xs):
    """The v1 list join: 'a, b and c'."""
    return ', '.join(xs[:-1]) + ' and ' + xs[-1] if len(xs) > 1 else ''.join(xs)


def render_power_sizing(m, inputs):
    """docs-authority/POWER_SIZING.md: the v1 _power_sizing_doc.py template,
    closed with the X-STD-01 code-basis block (POWER_SIZING rows)."""
    d = _drv_of(inputs)
    N = _node_view(m)

    def P(u):
        return (N.get(u) or {}).get('params') or {}

    pv, es, inv, gen = P('PV_ARRAY'), P('ZNBR2'), P('SOL_ARK_60K'), P('BACKUP_GEN')
    fc = N.get('FUEL_CELL') or {}
    loop = P('FUEL_CELL').get('reversible_loop') or {}
    el = (m.data.get('mvs') or {}).get('electrical') or {}
    roof = pv.get('roof') or {}
    ic = inv.get('interconnection') or {}
    crit = _BF.critical_list(N, d)
    crit_kw = sum(crit.values())
    rule_kw = math.ceil(float('1.25') * crit_kw / 5) * 5
    gen_rating = _BF.rating_kw(N, d)
    drv_kw = gen_rating['rated_kW']
    red = inv.get('redundancy') or {}
    need_kw = _q(el.get('need_kw'))
    ext_kw = _q((N.get('EXT_HALL') or {}).get('continuous_kw'))
    rect_ew = P('RECTIFIER').get('rect_ac_input_kW')
    trims = _PWS.rectifier_trims({'edges': _edges(m)})              # the v1 call read the graph dict; the rates are the resolved ones
    tk = sum(t[2] for t in trims)
    s17 = next(((e.get('rate') or {}).get('value') for e in _edges(m) if e.get('from_unit_id') == 'SOL_ARK_60K'
                and e.get('to_unit_id') == 'RECTIFIER' and 'elec' in (e.get('layers') or [])), None)
    _num = lambda *v: all(isinstance(x, (int, float)) for x in v)
    if _num(need_kw, ext_kw, rect_ew):
        parts = (f'The plant bus demand of {need_kw:.1f} kW has ' + ('four parts' if trims else 'three parts')
                 + f'. The extension hall `EXT_HALL` takes {ext_kw:.1f} kW (`EXT_HALL.continuous_kw`). '
                 f'The rectifier input for the electrowinning cells at the bounding current is {rect_ew:.1f} kW '
                 '(`RECTIFIER.params.rect_ac_input_kW`). '
                 + (f'The {len(trims)} electric trim heaters that the rectifier feeds are counted at their rated '
                    f'load (A-M-415): ' + _and([f'{t[1]} by stream {t[0]} ({t[2]:.2f} kW)' for t in trims])
                    + f', {tk:.2f} kW in all. ' if trims else '')
                 + f'The remaining {need_kw - ext_kw - rect_ew - tk:.1f} kW is the sum of the continuous loads of '
                 'the other units and the feeds of the inverter bus, as `docs-authority/_power_sizing.py` adds '
                 'them. '
                 f'The load list AQS-ELEC-003 gives a connected load of {need_kw - rect_ew - tk:.1f} kW, which is '
                 'the bus demand less the rectifier input for the cells'
                 + (' and the trim heaters' if trims else '')
                 + ': it lists the cells as direct-current loads behind the rectifier and leaves them out of its '
                 'alternating-current sum.')
    else:
        parts = 'The parts of the plant bus demand cannot be stated because the extension hall load or the ' \
                'rectifier input is not on the graph.'
    md = ['# Storage and generation sizing', '',
          'Document number: AQS-ELEC-007', 'Revision: J', 'Date: 2026-10-29',
          'Generated by `docs-authority/_power_sizing_doc.py` from the plant graph and '
          '`flow_graph/param/drivers.json`. Do not edit by hand; change the generator or its inputs and run '
          '`python3 -m flow_graph.param.regen`.', '',
          '| Rev | Description | Date |', '|---|---|---|',
          '| A | First issue: photovoltaic array, storage, inverters and backup generator for two electrowinning '
          'cases | 2026-10-15 |',
          '| B | Bounding case written to the graph (X-RSZ-02) | 2026-10-15 |',
          '| C | Acid and base loop loads added (X-PAR acid-loop decision) | 2026-10-15 |',
          '| D | Photovoltaic array on the roof only; the building grows until its roof carries the array '
          '(X-PAR-07) | 2026-10-15 |',
          '| E | Array at the oversize factor, storage charged on a cloudy day, inverters sized for export '
          '(X-PAR-09, decision D75) | 2026-10-15 |',
          '| F | Hall heating and cooling compared; air-source heat pumps kept (X-PAR-08, decision D77) '
          '| 2026-10-15 |',
          '| G | Generated from the graph. Revision F had become a hand-kept page whose values no longer matched '
          'the graph; the page now reports the values the sizing writes | 2026-10-29 |',
          '| H | The plant bus demand split into its parts and reconciled with the connected load of AQS-ELEC-003; '
          'the rectifier feeder checked against the rectifier input | 2026-10-29 |',
          '| I | The check of the rectifier feeder corrected: the one-line diagram has two rectifier feeders, which '
          'together carry its share of the bus demand; the trim heaters it feeds are the load without a supply '
          '| 2026-10-29 |', '',
          '| J | The trim heaters fed by the rectifier counted at rated load in the plant bus demand (A-M-415); the '
          'array, storage, inverters and bus section rating follow from the new demand | 2026-10-29 |',
          '## 1. Purpose and scope', '',
          'This page reports how the plant\'s electricity is generated and stored: the photovoltaic (PV) array on '
          'the roof, the zinc-bromine flow battery `ZNBR2`, the hybrid inverters `SOL_ARK_60K`, the proton exchange '
          'membrane (PEM) fuel cell `FUEL_CELL`, the export to the grid and the standby generator `BACKUP_GEN`. It '
          'states the method and the results. The calculation is in `docs-authority/_power_sizing.py`; '
          '`flow_graph/param/write_graph.py` writes its results to the graph, and this page reads them from there. '
          'The ground-source heat pump, the organic Rankine cycle unit and the generator fuels are described in '
          'AQS-PWR-002 (`GEOTHERMAL_BACKUP.md`). Every value is a study value.', '',
          '## 2. Method', '',
          '- Demand. The plant bus demand is the converged continuous load of every unit, including the conditioned '
          'extension hall `EXT_HALL`, taken as a flat profile over the day because the process runs continuously.',
          '- Array. The balancing nameplate is the array that delivers the daily demand at the PV yield (driver '
          '`pv_yield_kWh_kWp_d`) after the system derate (`pv_system_derate`), with the night served from storage '
          'at its round-trip efficiency (`storage_round_trip`, `night_hours`). The installed array is the balancing '
          'nameplate times `pv_oversize_factor`, so that the plant has a saleable surplus. The array is on the roof '
          'only; the solver grows the building footprint on its bay grid until the roof, after fire access '
          'pathways, carries the array.',
          '- Storage. The battery carries the plant bus demand through the night (`night_hours`), so its energy is '
          'the demand times the night hours. Its charge rate is the array peak on a cloudy day less the direct '
          'load, as recorded in `ZNBR2.params.charge_basis`.',
          '- Fuel cell. The fuel cell turns stored hydrogen from the electrolyser `H2O_ELYZ` back into electricity '
          'at a set continuous output. Its round-trip efficiency, from electricity to hydrogen and back, is '
          'recorded in `FUEL_CELL.params.reversible_loop`. AQS-FC-001 (`FUEL_CELL.md`) describes it.',
          '- Inverters. The inverter count carries the array output at noon with the store full, which is when '
          'export peaks.',
          '- Backup. The generator rating is computed from the live critical-load list by '
          '`flow_graph/param/backup_fuel.py` rating_kw: 125 % of the list rounded up to a 5 kW step on the standby '
          'basis of NFPA 110 (owner ruling Q-040, 2026-11-05). Section 5 checks the stamped rating against that '
          'rule. The critical loads must be carried for `crit_autonomy_d` days without sun.', '',
          '## 3. Results', '',
          'Table 3.1 gives the sized values as the graph holds them.', '',
          'Table 3.1. Storage and generation sizing results', '',
          '| Quantity | Value | Unit | Graph field |', '|---|---|---|---|',
          f'| Plant bus demand | {_pf(_q(el.get("need_kw")), 1)} | kW | `mvs.electrical.need_kw` |',
          f'| Mean-day average generation of the installed array | {_pf(_q(el.get("target_kw")), 1)} | kW | '
          '`mvs.electrical.target_kw` |',
          f'| PV balancing nameplate | {_pf(pv.get("balance_kWp"))} | kWp | `PV_ARRAY.params.balance_kWp` |',
          f'| PV oversize factor | {_pf(pv.get("oversize_factor"), 1)} | - | `PV_ARRAY.params.oversize_factor` |',
          f'| PV installed nameplate | {_pf(pv.get("nameplate_kw"))} | kWp | `PV_ARRAY.params.nameplate_kw` |',
          f'| PV modules | {_pf(pv.get("count"))} | - | `PV_ARRAY.params.count` |',
          f'| PV array area | {_pf(pv.get("area_m2"))} | m² | `PV_ARRAY.params.area_m2` |',
          f'| Roof footprint | {_pf(roof.get("footprint_m2"))} | m² | `PV_ARRAY.params.roof.footprint_m2` |',
          f'| Roof capacity after pathways | {_pf(roof.get("roof_capacity_kWp"), 1)} | kWp | '
          '`PV_ARRAY.params.roof.roof_capacity_kWp` |',
          f'| Storage energy | {_pf(es.get("kWh"))} | kWh | `ZNBR2.params.kWh` |',
          f'| Storage charge rate | {_pf(es.get("charge_kW"))} | kW | `ZNBR2.params.charge_kW` |',
          f'| Storage discharge rate | {_pf(es.get("discharge_kW"))} | kW | `ZNBR2.params.discharge_kW` |',
          f'| Hybrid inverters | {_pf(inv.get("count"))} | - | `SOL_ARK_60K.params.count` |',
          f'| Inverter capacity | {_pf(inv.get("kW"))} | kW | `SOL_ARK_60K.params.kW` |',
          f'| Export at noon, store full | {_pf(ic.get("export_peak_kW"), 1)} | kW | '
          '`SOL_ARK_60K.params.interconnection.export_peak_kW` |',
          f'| Export energy, clear day | {_pf(ic.get("export_kWh_d_clear"))} | kWh/d | '
          '`SOL_ARK_60K.params.interconnection.export_kWh_d_clear` |',
          f'| Fuel cell continuous output | {_pf(_q(fc.get("continuous_kw")), 1)} | kW | `FUEL_CELL.continuous_kw` |',
          f'| Fuel cell loop round-trip efficiency | {_pf(loop.get("round_trip"), 3)} | - | '
          '`FUEL_CELL.params.reversible_loop.round_trip` |',
          f'| Backup generator rating | {_pf(gen.get("rated_kW"))} | kW | `BACKUP_GEN.params.rated_kW` |', '',
          parts, '',
          f'Table 3.2 lists the critical loads that the backup generator carries. They total {crit_kw:.2f} kW. '
          'They come from `flow_graph/param/backup_fuel.py`, which takes them from the drivers and the graph.', '',
          'Table 3.2. Critical loads', '', '| Load | Power (kW) |', '|---|---|']
    md += [f'| {k} | {v:.2f} |' for k, v in crit.items()] + ['',
          '## 4. Decisions', '',
          '- The array is on the roof only. A ground-mounted field was removed, and the building grows until its '
          'roof carries the array (X-PAR-07).',
          '- The array is oversized by `pv_oversize_factor` so that the plant exports a surplus (decision D75).',
          '- The extension hall is heated and cooled by air-source heat pumps. A ground-source system was compared '
          'and gave a gain inside the uncertainty of the inputs while needing a large bore field, so the '
          'air-source design was kept (decision D77).', '',
          '## 5. Checks', '',
          (f'The standby rating rule gives {rule_kw} kW for the critical loads in Table 3.2. The rating on the '
           f'graph carries {_pf(drv_kw)} kW, computed by `flow_graph/param/backup_fuel.py` rating_kw from the same '
           'live critical list (owner ruling Q-040, 2026-11-05). '
           + ('The two agree.' if abs(rule_kw - (drv_kw or 0)) < float('1e-6')
              else 'The two differ, so either the rule constants or the list are wrong; the owner decides which.')),
          '',
          (f'The bus section rating in `SOL_ARK_60K.params.redundancy` was computed for a bus demand of '
           f'{_pf(red.get("bus_demand_kW"), 1)} kW. '
           + ('This matches the plant bus demand in Table 3.1.'
              if abs((red.get('bus_demand_kW') or 0) - (_q(el.get('need_kw')) or 0)) < float('0.5')
              else f'The plant bus demand in Table 3.1 is {_pf(_q(el.get("need_kw")), 1)} kW, so the section '
                   'rating must be recomputed by the stage that writes it.')), '']
    if _num(s17, rect_ew):
        md += ([] if md[-1] == '' else ['']) + ['The rectifier is fed from the inverter bus through '
               + ('three feeders' if trims else 'two feeders')
               + f' on the one-line diagram AQS-ELEC-002: stream S17 at {s17:.1f} kW for its 48 V rails and '
               f'auxiliaries, the RECT-EW feeder at the {rect_ew:.1f} kW input for the electrowinning cells'
               + (f', and the RECT-TRIM feeder at the {tk:.1f} kW of the trim heaters' if trims else '')
               + '. The bus demand counts all of them.']
    return _finish('\n'.join(md), 'POWER_SIZING')


# ---- X-ELS-06: the cable and busbar schedule (CABLE_SCHEDULE.md) ----------------

_CABLE_J = 1000 / float('6.4516')               # A/cm2, the UL891 default density, copper
_AMP = dict(_INV.AMP)                            # the v1 AMP face of the census ampacity table (size -> A)


def _cable_book(m, inputs):
    """The cable-schedule book of docs-authority/_cable_schedule.py: every
    power circuit of the wire census (the inventory family's books in memory,
    the v1 stage read the committed WIRE_INVENTORY.csv) with design current,
    conductor ampacity (parallel sets), length and voltage drop; the bus
    demand from the one-line book (the U2a sidecar value composed in memory);
    the switchboard and collection-section bars; and the EW process bars from
    the busbar book."""
    d = _drv_of(inputs)
    mot = _INV.motor_rows(m, inputs)
    rows = []
    for r in _INV.wire_census(m, inputs, mot)['rows']:
        if not r['type'].startswith('power') or r['size'] not in _AMP:
            continue
        m1 = re.search(r'\(([0-9.]+) A\)', r['basis']) or re.search(r'([0-9.]+) A', r['basis'])
        I = float(m1.group(1)) if m1 else None
        if I is None:
            continue
        ms = re.search(r'in (\d+) parallel', r['basis']) or re.search(r'(\d+) sets', r['basis'])
        par = int(ms.group(1)) if ms else 1
        L = float(r['length_m'])
        amp = _AMP[r['size']] * par
        if '1 ph' in r['type']:
            V = float('277.0') if '277' in r['circuit'] else float('120.0')
            dv = 2 * I * L / 1000 * _INV.RKM[r['size']] / V * 100
        else:
            V = float('208.0') if '208' in r['circuit'] or '208' in r['voltage_class'] else float('460.0')
            dv = _INV._vd(r['size'], I / par, L, V)
        lim = float('2.0') if ('panel feeder' in r['circuit'] or 'section main' in r['circuit']) else float('3.0')
        rows.append(dict(unit=r['unit'], circuit=r['circuit'], size=r['size'], sets=par, I=I, amp=amp, L=L, V=V,
                         vd=dv, lim=lim, ok=I <= amp and dv <= lim + float('1e-9')))
    # bus demand from the one-line book at the quantisation the U2a sidecar
    # publishes (the v1 stage read ONE_LINE.json)
    dem = round(_one_line_book(m, d)['demand'], 2)
    I_bus = dem * 1000 / (math.sqrt(3) * V_BUS * float('0.9'))
    bars = [('SWBD-1 section A (main-tie-main, either section carries the whole plant with the tie closed)', 500, I_bus),
            ('SWBD-1 section B', 500, I_bus)]
    bars += [(f'Collection section CB-{i} (10 x 60 kW inverters, NEC 705.28 at 125 %)', 1000, 722 * float('1.25'))
             for i in range(1, 7)]
    brow = [dict(name=n, rating=a, I=i, cm2=a / _CABLE_J, ok=i <= a) for n, a, i in bars]
    ew = [(c, a, round(s['A_cm2'], 1)) for c, a, s in _busbar_book(m, inputs)[1]]   # the U2a A_cm2 quantisation
    return rows, dem, I_bus, brow, ew


def render_cable_schedule(m, inputs):
    """docs-authority/CABLE_SCHEDULE.md: the v1 _cable_schedule.py template
    (AQS-ELEC-010 rev A)."""
    rows, dem, I_bus, brow, ew = _cable_book(m, inputs)
    bad = [x for x in rows if not x['ok']]
    md = ['# Cable and busbar schedule', '', 'Document number: AQS-ELEC-010', 'Revision: A', 'Date: 2026-10-15',
          'Authority: AQS-PLAN-007 X-ELS-06. Generated by `docs-authority/_cable_schedule.py` from AQS-INV-002 '
          '(WIRE_INVENTORY.csv), AQS-ELEC-008 and AQS-BUS-001. Study; not a PE stamp.', '',
          f'{len(rows)} power circuits; {len(rows) - len(bad)} meet ampacity (NEC2026 310.16, 75 C, Cu) and the '
          f'voltage-drop limits (3 % branch, 2 % feeder, resistive three-phase); {len(bad)} do not.', '',
          '## 1. Busbars', '', '| Bus | Rating A | Design A | Cu section at 155 A/cm2, cm2 | OK |',
          '|---|---|---|---|---|']
    md += [f"| {b['name']} | {b['rating']} | {b['I']:.0f} | {b['cm2']:.2f} | {'yes' if b['ok'] else 'NO'} |"
           for b in brow]
    md += ['', f'Plant demand {dem:.1f} kW at 480 V, power factor 0.9 assumed: {I_bus:.0f} A. EW process bars '
           '(AQS-BUS-001 rev C) are sized by heat balance at a 30 K rise and held to the same 155 A/cm2 default; '
           'every bar passes.', '',
           '| EW bar | A | Cu section cm2 | A/cm2 | OK |', '|---|---|---|---|---|']
    md += [f"| {n} | {a} | {c} | {int(a) / float(c):.0f} | {'yes' if int(a) / float(c) <= _CABLE_J + float('0.5') else 'NO'} |"
           for n, a, c in ew]
    md += ['', '## 2. Cables', '',
           '| Unit | Circuit | Size | Sets | Design A | Ampacity A | Length m | V | Drop % | Limit % | OK |',
           '|---|---|---|---|---|---|---|---|---|---|---|']
    md += [f"| {x['unit']} | {x['circuit']} | {x['size']} | {x['sets']} | {x['I']:.1f} | {x['amp']} | {x['L']:.1f} | "
           f"{x['V']:.0f} | {x['vd']:.2f} | {x['lim']:.0f} | {'yes' if x['ok'] else 'NO'} |"
           for x in sorted(rows, key=lambda x: (x['unit'], x['circuit']))]
    return ('\n'.join(md) + '\n').encode('utf-8')


# ---- AQS-ELEC-009: hazardous area classification (HAZ_AREA.md + HAZ_AREA.csv) ---

def _haz_book(m, inputs):
    """The haz_area book: the release rows of functions/haz_area (the graph
    half, golden in test_safety_books.py) plus the two inventory-count columns
    the v1 stage took from the committed censuses. The instrument counts ride
    the declared INSTRUMENT_INDEX.csv rows payload (absent payload = no
    counts, the census-payload absence convention -- the golden needs the
    committed rows) until the instrument-index census family lands; the
    motor-and-pump counts run over the other census rows of the inventory
    family."""
    d = _drv_of(inputs)
    ins = collections.Counter(r['unit'] for r in (inputs.get('instrument_index') or []))
    mot = _INV.motor_rows(m, inputs)
    oth = _INV.other_rows(m, inputs, mot, _INV.wire_census(m, inputs, mot)['rows'])
    mp = collections.Counter(r['unit'] for r in oth
                             if 'motor' in r['item'].lower() or 'pump' in r['item'].lower())
    rows = []
    for r in _HAZ.release_rows(m, d):
        rows.append(dict(unit=r['unit'], sector=r['sector'], substances=r['substances'], kg_d=r['kg_d'],
                         group=r['group'], T_class=r['T_class'], zone0=r['zone0'], zone1=r['zone1'],
                         zone2=r['zone2'], instruments=ins[r['unit']], motors_pumps=mp[r['unit']],
                         protection=r['protection']))
    return rows


def render_haz_area_md(m, inputs):
    """docs-authority/HAZ_AREA.md: the v1 _haz_area.py template (AQS-ELEC-009
    rev B, A-M-210)."""
    rows = _haz_book(m, inputs)
    K = collections.Counter(r['group'] for r in rows)
    md = ['# Hazardous area classification', '', 'Document number: AQS-ELEC-009', 'Revision: B', 'Date: 2026-10-25',
          'Authority: AQS-PLAN-007 task X-ELS-09; assumption A-M-210. Generated by `docs-authority/_haz_area.py` from the '
          'plant flow graph. Do not edit this page by hand. Study.', '',
          '| Rev | Description | Date |', '|---|---|---|', '| A | First issue | 2026-10-16 |',
          '| B | Purpose and scope added; text rewritten to the documentation style guide (AQS-DOC-002). No zone changed. | 2026-10-25 |', '',
          '## 1. Purpose and scope', '',
          'Where a flammable gas or vapour can be released, the air around the release point may become explosive. '
          'Electrical equipment in that space must then be of a type that cannot ignite it. Hazardous area '
          'classification divides such spaces into zones by how often an explosive atmosphere is expected: Zone 1 where '
          'it is likely in normal operation, and Zone 2 where it is not likely and would last only a short time.', '',
          'This page lists every unit in the graph that can release a flammable substance, assigns the gas group and '
          'temperature class of that substance, and gives the extent of Zone 1 and Zone 2 around the unit. The zones '
          'follow IEC 60079-10-1 and NEC 2026 Article 505. Each gas group is given in IEC terms with the equivalent North American group in brackets. '
          'The number of instruments and motors or pumps in each zone is counted so that they can be specified as '
          'explosion-protected (Ex-rated) equipment.', '',
          '## 2. Basis', '',
          'The ventilation is taken as medium degree with good availability, provided by mechanical extract '
          '(AQS-THM-002). Loss of extract trips the release source (AQS-CTL-003), so the zone extents remain valid. '
          f'The graph has {len(rows)} release sources: ' + ', '.join(f'{v} in gas group {k}' for k, v in K.items()) + '.', '',
          '## 3. Zones', '',
          'Table 3.1 gives the classification for each release source. The flow column is the rate of the flammable '
          'substance through the unit.', '',
          'Table 3.1. Release sources and zones', '',
          '| Unit | Sector | Substances | Flow (kg/d) | Gas group | Temperature class | Zone 1 | Zone 2 | Instruments | Motors and pumps |', '|---|---|---|---|---|---|---|---|---|---|']
    md += [f"| {r['unit']} | {r['sector']} | {r['substances']} | {r['kg_d']} | {r['group']} | {r['T_class']} | {r['zone1']} | {r['zone2']} | {r['instruments']} | {r['motors_pumps']} |" for r in rows]
    md += ['', f"In total, {sum(r['instruments'] for r in rows)} instruments and {sum(r['motors_pumps'] for r in rows)} motors or pumps are in Zone 1 or Zone 2. Their specifications in the instrument index (AQS-CTL-001) and the inventories take the protection type from the protection column of `docs-authority/inventory/HAZ_AREA.csv`.",
           '', 'The headspace of the zinc–bromine flow battery (ZNBR2), where hydrogen forms by the hydrogen evolution reaction (HER), is Zone 2 inside the enclosure while the purge is running (NFPA 855; gas detection in AQS-SAF-006).',
           '', 'The zone extents are to be confirmed by a release-rate calculation (IEC 60079-10-1 Annex C) once the flange and seal schedule exists.']
    return ('\n'.join(md) + '\n').encode('utf-8')


def _csv_book(rows):
    """The v1 csv.DictWriter face (CRLF rows, QUOTE_MINIMAL) as bytes -- the
    serialization face of the inventory-census sidecars."""
    s = io.StringIO()
    w = csv.DictWriter(s, list(rows[0].keys()), extrasaction='ignore')
    w.writeheader()
    w.writerows(rows)
    return s.getvalue().encode('utf-8')


def render_haz_area_csv(m, inputs):
    """docs-authority/inventory/HAZ_AREA.csv: the machine sidecar (the columns
    in the v1 writer order; doc_hvac reads it undeclared, per the ledger)."""
    return _csv_book(_haz_book(m, inputs))


# ---- the registry ---------------------------------------------------------------
# The declared ordered list (the census order: load_list, one_line, ew_busbar,
# doc_power_sizing, ew_sizing_doc, each with its U2a sidecar where the v1 stage
# wrote one). The render/__init__.py aggregate import composes these into
# RENDERS after the sizing wave's entries.

DOCS = [
    ('docs-authority/LOAD_LIST.md', render_load_list),
    ('docs-authority/LOAD_LIST.json', render_load_list_json),
    ('docs-authority/ONE_LINE.md', render_one_line),
    ('docs-authority/ONE_LINE.json', render_one_line_json),
    ('docs-authority/BUSBAR.md', render_busbar),
    ('docs-authority/BUSBAR.json', render_busbar_json),
    ('docs-authority/POWER_SIZING.md', render_power_sizing),
    ('docs-authority/sizing/EW_CELLS.md', render_ew_cells),
    ('docs-authority/CABLE_SCHEDULE.md', render_cable_schedule),
    ('docs-authority/HAZ_AREA.md', render_haz_area_md),
    ('docs-authority/inventory/HAZ_AREA.csv', render_haz_area_csv),
]

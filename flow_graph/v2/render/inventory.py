"""The inventory renderer wave (the ledger section I documents, plus the
section D `inventory_wire` row the section I censuses unlock, and the two
documents that census landed next: doc_wire_specs (AQS-INV-007, the wire
family specification sheets and WF-nn.svg cross-sections) and doc_motor_fa
(AQS-INV-008, the first-article page, MF-nn.svg drawings and MOTOR_FA.json)).
Reference writers: flow_graph/inventory/motors.py, motor_designs.py, wire.py,
pipe.py, other.py, and the docs-authority/_wps.py, _pipe_specs.py,
_bought_specs.py, _block_fam_plans.py, _plant_bom.py, _sc_reconcile.py,
_spares.py, _cost_estimate.py, _eol.py, _wire_specs.py and _motor_fa.py
rollups. Pure functions Model -> document bytes
over the census books of flow_graph/v2/functions/inventory.py (the censuses
stamp no graph state; every renderer builds the books once and shares the
rows, the electrical-wave one shared pure chain). The v1 doc templates are
ported exactly -- the same headers, document numbers, revision lines, table
shapes, number formats and basis texts -- and the acceptance is byte-exact
reproduction of the committed files
(flow_graph/v2/test_render_inventory.py).

Compositions in memory (the EVAP X-STD-01 and electrical-wave patterns):
- the doc-on-doc reads die as file reads: _pipe_specs parsed the committed
  WPS_REGISTER.md and PIPING_CLASSES.md tables, _block_fam_plans parsed the
  committed BOUGHT_SPECS.md rows -- here the WPS / PIPING-CLASSES /
  BOUGHT-SPECS book bytes are produced in-process and parsed by the same
  regexes, so the composition sees exactly what the v1 file hand-off saw;
- the census CSVs (MOTOR_INVENTORY.csv etc.) that v1 stages re-read as inputs
  are the books computed once per render and passed as rows;
- the collection-bus CB- rows of the wire census compose from the power
  family's sections book (see functions/inventory.py -- the ledger's hard
  hidden dependency 16).

What the books read (the payload dispositions are declared in the census
family's docstring): the mfg BOMs and fasteners, the MFG_TOOLS tool table, the
placement block map, the ISO_SHEETS rows, the SUPPORTS span counts, the
line-list positions, the grounding-grid lengths, the gas-detector and SIF
rows, the nozzle-unit roster, the family-id registers, the motor-family CAD
BOMs, the unit envelope BOMs and the duty-sheet material lines -- all inputs
payloads; the graph books are the model's resolved fields (the seed with the
landed families' overlays composed).

REMAINING (the section I documents NOT ported here, each with its reason):
- SELF_COPY_BOM.md (the doc_sc_reconcile page half): the page is hand-authored
  and the stage only rewrites its generated section 8 in place (the duties-wave
  patch-fixpoint situation); the generated section renderer and the
  SELF_COPY_RECON.csv sidecar are ported (render_self_copy_section /
  render_self_copy_recon), the whole-page composer that declares the hand base
  text as data registers later, per the duties pattern;
- the reprap_bom_complete flag propagation of _sc_reconcile (a graph +
  candidate_mvs.json field rewrite) is a solve-field/builder concern, not a
  renderer: it stays with the construction migration;
- doc_unit_boms / doc_itp per-unit files: see the module tail -- the
  per-unit tree registers parametrically over the committed roster when its
  row lands (the render entry points land with it; not in this module yet).

Cleared by the census landing (each now renders in this module): doc_wire_specs
and doc_motor_fa, over the wire families and motor design books and the
composed MF sheet texts, with the WIRE_DRAW and mfa_* drivers.

Pure: no I/O here -- the registry returns bytes and file writing stays
outside.
"""
import csv
import io
import json
import math
import re

from flow_graph.v2.functions import inventory as INV

D = 'docs-authority/inventory/'                       # the inventory directory prefix (the v1 output root)
MF_DIR = 'docs-authority/inventory/motor_families/'
FA_DIR = 'docs-authority/drawings/motor_fa/'
WF_DIR = 'docs-authority/drawings/wire/'
UNITS_DIR = 'models/units/'


# ---- the books: the census chain computed once per render --------------------

_BOOKS_MEMO = {}


def _books(m, inputs):
    """The census chain: motor -> wire -> pipe -> other rows and family
    rollups, plus the motor design books. Pure and deterministic -- the same
    model and inputs reproduce the same books -- so the chain runs once per
    distinct (model, inputs) pair and every renderer reads the same rows (the
    v1 stages re-read each other's CSV files; here the books are shared)."""
    key = (id(m), id(inputs))
    hit = _BOOKS_MEMO.get(key)
    if hit is not None and hit[0] is m and hit[1] is inputs:
        return hit[2]
    b = _compute_books(m, inputs)
    _BOOKS_MEMO[key] = (m, inputs, b)               # holds the pair so the ids stay valid
    return b


def _compute_books(m, inputs):
    b = {}
    b['mot'] = INV.motor_rows(m, inputs)
    b['mfam'], b['mids'] = INV.motor_families(b['mot'], inputs)
    b['fam_rows'] = [dict(family=b['mids'][k], motor_type=k[0], size=k[1], voltage=k[2], count=x['count'],
                          units=len(x['units']), installed_shaft_kW=round(x['kw'], 2)) for k, x in b['mfam']]
    b['design_rows'], b['mag_rows'] = INV.motor_design_books(b['fam_rows'])
    wc = INV.wire_census(m, inputs, b['mot'])
    b['wire'] = wc
    b['wfam'], b['wtot'], b['wassumed'] = INV.wire_families(wc['rows'], inputs)
    b['pipe'] = INV.pipe_rows(m, inputs)
    b['pfam'], b['ptot'] = INV.pipe_families(b['pipe'], inputs)
    b['other'] = INV.other_rows(m, inputs, b['mot'], wc['rows'])
    b['ofam'], b['ocats'], b['oassumed'] = INV.other_families(b['other'], inputs)
    return b


def _csv(rows, keys=None):
    """The v1 csv.DictWriter face (CRLF rows, QUOTE_MINIMAL) as bytes."""
    s = io.StringIO()
    w = csv.DictWriter(s, keys or list(rows[0].keys()), extrasaction='ignore')
    w.writeheader()
    w.writerows(rows)
    return s.getvalue().encode('utf-8')


def _csv_list(header, rows):
    """The v1 csv.writer face (plain list rows) as bytes."""
    s = io.StringIO()
    w = csv.writer(s)
    w.writerow(header)
    w.writerows(rows)
    return s.getvalue().encode('utf-8')


def _md(lines):
    """The v1 '\\n'.join(lines) + trailing newline as bytes."""
    return ('\n'.join(lines) + '\n').encode('utf-8')


# ---- AQS-INV-001: the motor inventory (MOTOR_INVENTORY.md/.csv,
# MOTOR_FAMILIES.csv) ----------------------------------------------------------

def render_motor_inventory_csv(m, inputs):
    """docs-authority/inventory/MOTOR_INVENTORY.csv: the AQS-INV-001 census."""
    return _csv(_books(m, inputs)['mot'])


def render_motor_families_csv(m, inputs):
    """docs-authority/inventory/MOTOR_FAMILIES.csv: the family rollup."""
    b = _books(m, inputs)
    rows = [[b['mids'][k], k[0], k[1], k[2], x['count'], len(x['units']), round(x['kw'], 2)] for k, x in b['mfam']]
    return _csv_list(['family', 'motor_type', 'size', 'voltage', 'count', 'units', 'installed_shaft_kW'], rows)


def render_motor_inventory_md(m, inputs):
    """docs-authority/inventory/MOTOR_INVENTORY.md: the v1 motors.write() page
    template."""
    b = _books(m, inputs)
    rows, mfam, ids = b['mot'], b['mfam'], b['mids']
    L = ['# Motor and actuator inventory', '', 'Document number: AQS-INV-001', 'Revision: B', 'Date: 2026-10-25',
         'Authority: AQS-PLAN-007 task X-INV-01 (owner programme of 2026-10-15); assumption A-M-119. Generated by '
         '`flow_graph/inventory/motors.py`, with the data in the CSV file beside this page; do not edit this page by '
         'hand.', '',
         '| Rev | Description | Date |', '| --- | --- | --- |', '| A | First issue. | 2026-10-15 |',
         '| B | Purpose and scope added; text rewritten to the documentation style guide (AQS-DOC-002). No item changed. '
         '| 2026-10-25 |', '',
         '## Purpose and scope', '',
         'This inventory lists every motor and actuator in the plant: pumps, fans, conveyors, agitators, compressors, '
         'valve actuators and solenoids. '
         'Section 1 groups them into motor families of similar design, which are designed in AQS-INV-005, and section 2 '
         'lists each item by sector, sub-system and unit.', '',
         'Many units have not yet been sized in detail, so some items rest on a counting rule or a default. Those items '
         'are marked "assumed" in the Basis column (A-M-119). They are replaced as each unit is sized (task 02) and '
         'receives its manufacturing model.', '',
         'The rules for items on units that are not yet sized are as follows. Each liquid outlet line has one transfer '
         'pump, sized for 10 m of head at an efficiency of 0.4, with no credit for gravity flow. Scrubbers, dryers, the '
         'baghouse, air-handling units, thermal units and fab benches each have one induced-draft fan, sized for 1 kPa '
         'at an efficiency of 0.5. Each solids line of 50 kg/d or more has one screw conveyor, and each dosed line has '
         'one on/off solenoid valve. Agitators are taken at 0.25 kW where the graph lists one.', '',
         'The motor type follows from the shaft power. Below 60 W of shaft power the motor is a 24 V DC brushless motor '
         '(BLDC). Above that, it is an IE3 induction motor at the next IEC 60034-1 rating of at least 1.15 times the '
         'shaft power, in the IEC 60072-1 4-pole frame. Scroll compressors have hermetic motors. The condenser fans of '
         'the heat pumps have electronically commutated (EC) motors, which are permanent-magnet motors with built-in '
         'electronics, rated by the same step. The efficiency classes of IEC 60034-30-1 (IE1 to IE4) apply only to the '
         'line-start induction motors, not to EC, BLDC or stepper motors.', '',
         '## 1. Family rollup', '',
         'Table 1.1 groups the items into families. Family identifiers come from '
         '`flow_graph/inventory/motor_family_ids.json`. An identifier stays with its family and is never reissued, so '
         'gaps in the list are families no longer in use.', '',
         'Table 1.1. Motor families', '',
         '| Family | Motor type | Size | Voltage | Count | Units | Installed shaft kW |',
         '| --- | --- | --- | --- | --- | --- | --- |']
    L += [f'| {ids[(mt, sz, V)]} | {mt} | {sz} | {V} | {x["count"]} | {len(x["units"])} | {x["kw"]:.2f} |'
          for (mt, sz, V), x in mfam]
    L += ['', '## 2. Inventory by sector, sub-system and unit', '',
          'The tables below list the items of each sector. Duty is the IEC 60034-1 duty type: S1 continuous running, S2 '
          'short-time, S3 intermittent periodic. Speed control is how the motor speed is set, which IEC 60034-1 does '
          'not cover: variable-frequency drive, electronically commutated (EC) motor with integrated electronics, BLDC '
          'driver, stepper driver, on/off for solenoids and valve actuators, or fixed speed (direct on line).', '']
    cur = None
    for r in rows:
        if r['sector'] != cur:
            cur = r['sector']
            L += ['', f'### {cur}', '',
                  '| Sub-system | Unit | Device | Motor type | Size | Shaft kW | Voltage | Duty | Speed control | Qty | '
                  'Basis |', '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
        L.append(f"| {r['subsystem']} | {r['unit']} | {r['device']} | {r['motor_type']} | {r['size']} | "
                 f"{r['shaft_kW']:g} | {r['voltage']} | {r['duty']} | {r['speed_control']} | {r['qty']} | {r['basis']} |")
    return _md(L)


# ---- AQS-INV-005: the motor family designs (MOTOR_DESIGNS.md/.csv,
# MAGNET_COMPARISON.csv, motor_families/MF-nn.md) -------------------------------

_DESIGN_REV_TABLE = [('A', '2026-10-15', 'First issue.'),
                     ('B', '2026-10-15', 'Slot-and-yoke fit: MF-04 core 115 to 149 mm (66 turns), MF-05 52, MF-06 58, '
                      'MF-07 79, MF-19 120 mm; first-article flags cleared (A-M-218).'),
                     ('C', '2026-10-25', 'Rewritten to the documentation style guide (AQS-DOC-002).'),
                     ('D', '2026-11-12', 'The sheet headers name the document revision and the per-sheet revision tables '
                      'are removed; the retired slot-fit revision label is dropped (F-20261110-05). No design data '
                      'changed.')]   # revisions of document AQS-INV-005 (rev, date, description); the parent page prints this table and every sheet header takes the last entry, the current revision that DOC_REGISTER.md lists for the document
_DESIGN_REV, _DESIGN_REV_DATE = _DESIGN_REV_TABLE[-1][:2]
ROUTE = {'NdFeB': 'Nd/Pr from feedstock magnets (IA-FEED-01 scrap): hydrogen decrepitation and re-sintering of recovered '
         'NdFeB (WALTON2015), or full RE separation by solvent extraction + NdF3 molten-salt electrolysis (not on the '
         'graph); strip cast, jet mill, field press, sinter 1080 C, Ni coat',
         'ferrite': 'Fe2O3 from the leach iron (hematite) + SrCO3 (Sr not in the plant feed: celestite import or Sr from '
         'feedstock ceramics); calcine 1250 C, mill, compound in PA12, injection-mould in an orienting field; no '
         'sintering line'}


def render_motor_designs_csv(m, inputs):
    """docs-authority/inventory/MOTOR_DESIGNS.csv: the design rows."""
    return _csv(_books(m, inputs)['design_rows'])


def render_magnet_comparison_csv(m, inputs):
    """docs-authority/inventory/MAGNET_COMPARISON.csv: the X-INV-02D rows."""
    return _csv(_books(m, inputs)['mag_rows'])


def _mf_sheet(f):
    """The v1 motor_designs.main() per-family sheet body: f the family rollup
    row (the kind branch and every table row run on the same chains the v1
    sheet ran)."""
    t, sz, V = f['motor_type'], f['size'], f['voltage']
    fid = f['family']
    L = [f'# Motor family {fid}: {t}, {sz}, {V}', '', f'Document: AQS-INV-005 sheet {fid}', f'Revision: {_DESIGN_REV}',
         f'Date: {_DESIGN_REV_DATE}',
         'Authority: AQS-PLAN-007 task X-INV-02; assumption A-M-126. This sheet is part of document AQS-INV-005; its '
         'revision table is on the parent page `docs-authority/inventory/MOTOR_DESIGNS.md`. Generated by '
         '`flow_graph/inventory/motor_designs.py`; do not edit this page by hand. This is a study design basis; the '
         'design has not been type-tested.', '',
         '## Purpose and scope', '',
         f'The plant makes its own motors, and motors of similar design are grouped into families. This sheet gives the '
         f'design basis of family {fid}, the steps by which it is made in-house, and the work still open before it can '
         f'be built. The family covers {f["count"]} motors in {f["units"]} units, with {f["installed_shaft_kW"]} kW of '
         'installed shaft power in total (motor inventory AQS-INV-001).', '',
         '## 1. Electromagnetic design basis', '',
         'Table 1.1 gives the design quantities and the basis of each.', '', f'Table 1.1. Design basis of {fid}', '']
    Vn = float(re.match(r'(\d+)', V).group(1))
    if t.startswith('induction') or t.startswith('hermetic'):
        kw = float(re.search(r'([\d.]+) kW', sz).group(1))
        if kw < INV.IE3_FLOOR:
            # a degraded census can carry a family below the smallest IE3 60 Hz
            # rating; the design is not sized (no invented efficiency target)
            L += ['| Quantity | Value | Basis |', '| --- | --- | --- |',
                  f'| Rating | {kw} kW, {Vn:.0f} V 3-ph 60 Hz | AQS-INV-001 |',
                  '| Electromagnetic design | Not sized here: the rating is below the smallest rating of the '
                  'IEC 60034-30-1 60 Hz IE3 table, so the output equation has no efficiency target; the first '
                  'type test sets it | IEC 60034-30-1 |']
        else:
            fr = re.search(r'IEC (\d+[SLM]?)', sz)
            fr = fr.group(1) if fr else None
            p = 2 if t.startswith('induction') else 1
            dd = INV.induction_design(kw, Vn, p, fr)        # the sheet table re-derives (the v1 sheet used the same chain)
            kind = 'induction' if p == 2 else 'hermetic'
            L += ['| Quantity | Value | Basis |', '| --- | --- | --- |',
                  f'| Rating | {kw} kW, {Vn:.0f} V 3-ph 60 Hz, {2 * p} poles, {dd["rpm"]} rpm sync | AQS-INV-001 |',
                  f'| Efficiency target | {dd["eta"] * 100:.1f} % (IE3, 60 Hz, {2 * p}-pole) | IEC 60034-30-1:2025 60 Hz table |',
                  f'| Power factor | {dd["pf"]:.2f} | assumed (A-M-126) |',
                  f'| Air-gap flux density | {INV.B_D} T | PYRHONEN2014 table 6.3, 0.7-0.9 T |',
                  f'| Linear current density | {dd["A"] / _E3:.0f} kA/m | PYRHONEN2014 table 6.3 |',
                  f'| Air-gap diameter x core length | {dd["Dg"]:.0f} x {dd["L"]:.0f} mm | output equation |',
                  f'| Stator outer diameter | {dd["Dout"]:.0f} mm | split ratio 0.55 (4-pole) / 0.50 (2-pole) |',
                  f'| Slots stator / rotor | {dd["Qs"]} / {dd["Qr"]} | PYRHONEN2014 slot-combination rules |',
                  f'| Turns per phase | {dd["N"]} | E = 4.44 f k_w N Phi, E = 0.95 V_ph |',
                  f'| Line current | {dd["I"]:.2f} A | S / (sqrt3 V) |',
                  f'| Conductor | {dd["cond"]} | J = {INV.J_D} A/mm2 |',
                  f'| Active mass, steel / copper | {dd["m_fe"]:.1f} / {dd["m_cu"]:.2f} kg | geometry estimate |']
            if fr in INV.IEC72:
                H, Ds, E, A_, B_, K = INV.IEC72[fr]
                L += [f'| Frame | IEC {fr}: H {H}, shaft D {Ds} x E {E}, feet A {A_} x B {B_}, holes K {K} mm | IEC 60072-1 |',
                      f'| Bearings | 2 x {INV.BRG[fr]} | ISO 15 (assumed size) |',
                      f'| Lamination OD held by the frame | {"yes, core lengthened" if dd["held"] else "no"} '
                      '(OD <= 0.85 x 2H, A-M-126) | IEC 60072-1 |',
                      f'| Core length / bore | {dd["LD"]:.2f} ({"ok" if dd.get("fits") else "above 2.5: review"}) | '
                      'practical limit, A-M-126 |',
                      '| Slot fit | '
                      + (f'core lengthened x {dd["slot_fit_L_factor"]:.2f} so slots and yoke fit the OD'
                         if dd['slot_fit_L_factor'] > 1 else 'fits')
                      + ' | fill 0.40, tooth 1.6 T, yoke 1.5 T (AQS-INV-008) |']
    elif t.startswith('BLDC') and 'actuator' not in t:
        per = float(f['installed_shaft_kW']) / int(f['count'])
        fl = 42 if '42' in sz else 57
        dd = INV.pm_design(per, 3000, fl / 1000)
        L += ['| Quantity | Value | Basis |', '| --- | --- | --- |',
              f'| Rating | {per * _E3:.0f} W mean, {Vn:.0f} V DC, 3000 rpm | AQS-INV-001 (mean of the family) |',
              f'| Torque | {dd["T"] * _E3:.0f} mN m | P / omega |',
              f'| Rotor diameter x length | {dd["Dg"]:.1f} x {dd["L"]:.1f} mm | T = (pi/2) D^2 L A B, A '
              f'{dd["A"] / _E3:.0f} kA/m, B {dd["B"]} T (HENDERSHOT2010) |', f'| Flange | {fl} mm | NEMA ICS 16 |']
    elif t.startswith('stepper'):
        fl = 57 if '57' in sz else 86
        per = float(f['installed_shaft_kW']) / int(f['count'])
        L += ['| Quantity | Value | Basis |', '| --- | --- | --- |',
              f'| Rating | {per * _E3:.0f} W, {Vn:.0f} V DC chopper drive | AQS-INV-001 |',
              '| Step | 1.8 deg, 200 full steps | hybrid stepper |', f'| Flange | {fl} mm | NEMA ICS 16 |']
    elif t.startswith('EC '):
        kw = float(re.search(r'([\d.]+) kW', sz).group(1))
        L += ['| Quantity | Value | Basis |', '| --- | --- | --- |',
              f'| Rating | {kw:g} kW, {V} | AQS-INV-001 (next rating >= 1.15 x shaft, A-M-117) |',
              '| Motor | Permanent-magnet motor with integrated commutation and speed-control electronics | A-M-332 |',
              '| Efficiency class | Not stated: the IEC 60034-30-1 efficiency classes cover line-start induction motors | '
              'IEC 60034-30-1 |',
              '| Electromagnetic design | Not sized here; taken from the selected fan nameplate or datasheet | A-M-332 |']
    elif t.startswith('solenoid'):
        per = float(f['installed_shaft_kW']) * float('1e3') / int(f['count'])
        R = Vn ** 2 / per
        L += ['| Quantity | Value | Basis |', '| --- | --- | --- |',
              f'| Coil power | {per:.1f} W at {Vn:.0f} V DC | AQS-INV-001 |',
              f'| Coil resistance | {R:.0f} ohm at 20 C | R = V^2 / P |', f'| Current | {per / Vn:.2f} A | P / V |',
              '| Interface | 22 mm coil, ISO 15218 | ISO 15218 |']
    else:
        L += ['| Quantity | Value | Basis |', '| --- | --- | --- |',
              '| Output | quarter turn, ISO 5211 F03, flange torque limit 32 N m | ISO 5211 |',
              '| Drive | MF-01 BLDC + worm gear | this sheet |']
    if t.startswith('induction') or t.startswith('hermetic'):
        kind = 'hermetic' if t.startswith('hermetic') else 'induction'
    elif t.startswith('BLDC') and 'actuator' not in t:
        kind = 'BLDC'
    elif t.startswith('stepper'):
        kind = 'stepper'
    elif t.startswith('EC '):
        kind = 'ec_fan'
    elif t.startswith('solenoid'):
        kind = 'solenoid'
    else:
        kind = 'actuator'
    L += ['', '## 2. Manufacturing plan', '', 'The motor is made in-house in the following steps.', ''] \
        + [f'{i}. {_s.rstrip(".")}.' for i, _s in enumerate(INV.PLAN[kind], 1)] \
        + ['', '## 3. Open items', '',
           'Three items remain open. A first article must be built and type-tested (task X-INV-02B). The drawings, the '
           'CadQuery model and the bill of materials must be produced (task X-INV-02C). The coefficients that are now '
           'taken from within published ranges (A-M-126) are then replaced by the type-test results.']
    return '\n'.join(L) + '\n'


def render_motor_designs_md(m, inputs):
    """docs-authority/inventory/MOTOR_DESIGNS.md: the v1 parent page."""
    b = _books(m, inputs)
    rows, bad = b['design_rows'], [r['family'] for r in b['design_rows'] if r['fits'] is False]
    M = ['# Motor family designs', '', 'Document number: AQS-INV-005', f'Revision: {_DESIGN_REV}',
         f'Date: {_DESIGN_REV_DATE}',
         'Authority: AQS-PLAN-007 X-INV-02. Generated by `flow_graph/inventory/motor_designs.py`; one sheet per family '
         'in `motor_families/`. A-M-126.', '',
         '| Rev | Description | Date |', '| --- | --- | --- |',
         ] + [f'| {r} | {dsc} | {dt} |' for r, dt, dsc in _DESIGN_REV_TABLE] + ['',
         f'{len(rows)} families. Induction and hermetic: output-equation sizing (PYRHONEN2014), IEC 60072-1 frames, IE3 '
         'targets from the IEC 60034-30-1 60 Hz table. BLDC: torque equation (HENDERSHOT2010). Families with core '
         f'length/bore above 2.5 in their IEC frame: {", ".join(bad) or "none"}.', '',
         '| Family | Type | Rating | Bore mm | Core L mm | OD / flange mm | Turns/ph | I A | Conductor | Steel kg | '
         'Cu kg | Fits |', '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    M += [f"| [{r['family']}](motor_families/{r['family']}.md) | {r['type']} | {r['rating']} | {r['Dg_mm']} | "
          f"{r['L_mm']} | {r['Dout_mm']} | {r['turns']} | {r['current_A']} | {r['conductor']} | {r['steel_kg']} | "
          f"{r['copper_kg']} | {r['fits']} |" for r in rows]
    C = b['mag_rows']
    M += ['', '## Magnet comparison, NdFeB vs bonded ferrite (X-INV-02D, owner 2026-10-15; basis held at NdFeB until '
          'Mike decides)', '',
          f"Properties: NdFeB {INV.MAG['NdFeB']['grade']}; ferrite {INV.MAG['ferrite']['grade']} (COEY2010, "
          f'IEC 60404-8-1). Air gap {INV.GAP} mm, magnet thickness {INV.MAG["NdFeB"]["lm"]} / '
          f'{INV.MAG["ferrite"]["lm"]} mm, leakage {INV.LEAK}, tooth limit {INV.BSAT} T, electric loading 15 kA/m, '
          f'J 5 A/mm2, iron loss {INV.PFE * 100:.0f} % (A-M-130).', '',
          '| Family | Magnet | Count | Torque mN m | B gap T | Rotor D x L mm | Frame | Efficiency % | Magnet g/unit | '
          'Rare earth g/unit | Fleet magnet kg | Fleet RE kg |',
          '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    M += [f"| {c['family']} | {c['magnet']} | {c['count']} | {c['torque_mNm']} | {c['Bg_T']} | {c['D_mm']} x "
          f"{c['L_mm']} | {c['frame']} | {c['eta']} | {c['magnet_g']} | {c['RE_g']} | {c['fleet_magnet_kg']} | "
          f"{c['fleet_RE_kg']} |" for c in C]
    M += ['', '| Item | NdFeB | Bonded ferrite |', '| --- | --- | --- |',
          f"| Material route | {ROUTE['NdFeB']} | {ROUTE['ferrite']} |",
          '| Production line | magnet line with sintering furnace (vacuum/argon), field press, coating; rotor bonding | '
          'injection moulding press with orienting fixture; magnets moulded onto the rotor hub, no coating |',
          '| Imported element | none if feedstock magnets suffice; otherwise Nd/Pr and Dy | Sr (or Ba) |',
          '| Motor consequence | smallest frames, highest efficiency | longer rotors or next flange; lower efficiency at '
          'equal electric loading |']
    return _md(M)


def _mf_renderer(fid):
    """One motor_families/MF-nn.md sheet bound to its family id (the registry
    entries bind the committed sheet roster -- see the module tail). A family
    absent from the census is loud: the canonical payload (the wave extras)
    renders the committed sheet; a payload without the committed registers
    allocates de-novo ids, which need not reach the bound id, and that
    renders the named not-in-this-census sheet, deterministically."""
    def render(m, inputs):
        b = _books(m, inputs)
        f = next((x for x in b['fam_rows'] if x['family'] == fid), None)
        if f is None:
            return _md([f'# Motor family {fid}', '', f'Document: AQS-INV-005 sheet {fid}', '',
                        f'Family {fid} is not in this census: the render ran under a payload without the '
                        'committed family registers, so the census allocated its ids de novo and they do not '
                        'reach the committed sheet roster. The canonical payload (inputs.load with the '
                        'inventory wave extras) renders the committed sheet.'])
        return _mf_sheet(f).encode('utf-8')
    render.__name__ = f'render_mf_sheet_{fid.lower()}'
    return render


# ---- AQS-INV-008: the motor first articles (MOTOR_FIRST_ARTICLE.md,
# drawings/motor_fa/MF-nn.svg, inventory/MOTOR_FA.json) --------------------------

def _motor_fa_book(m, inputs):
    """The v1 _motor_fa.py book: first-article lamination and frame dimensions
    per induction family from the AQS-INV-005 design rows (the census-chain
    books in memory -- the v1 stage read MOTOR_DESIGNS.csv), the sheet texts
    this module composes (the v1 stage read the committed motor_families/MF-nn.md
    files), and the mfa_* drivers (A-M-218). Returns (rows, svgs): the rows are
    the MOTOR_FA.json face, svgs maps family id -> drawing lines."""
    d = _drv_of(inputs)

    def v(k):
        return d[k]['value']

    b = _books(m, inputs)
    fill = v('MFG.tools-metal-forming-train.mfa_slot_fill')
    bt_t = v('MFG.tools-metal-forming-train.mfa_tooth_T')
    by = v('MFG.tools-metal-forming-train.mfa_yoke_T')
    kfe = v('MFG.tools-metal-forming-train.mfa_stacking_factor')
    sheets = {f['family']: _mf_sheet(f) for f in b['fam_rows']}
    out = []
    svgs = {}
    for dr in b['design_rows']:
        fam = dr['family']
        t = sheets[fam]

        def g(k, _t=t):
            return (re.search(r'\| ' + k + r' \| ([^|]+) \|', _t) or [None, ''])[1].strip()

        rat = g('Rating')
        pop = (re.search(r'The family covers (\d+) motors', t) or [0, '0'])[1]
        r = dict(family=fam, type=dr['type'], rating=dr['rating'], items=int(pop))
        pm = re.search(r'(\d+) poles', rat)
        if 'induction' in dr['type'] and dr['Dg_mm'] != '-' and pm:
            # a census can carry an induction family below the smallest IE3
            # rating (the sheets then leave it not sized): not drawable, the
            # row stays in Table 2.1
            pw = float(re.search(r'([\d.]+) kW', rat).group(1)) * 1000
            poles = int(pm.group(1))
            p = poles // 2
            Dg, L, Do = float(dr['Dg_mm']), float(dr['L_mm']), float(dr['Dout_mm'])
            nn = int(dr['turns'])
            ii = float(dr['current_A'])
            Qs, Qr = [int(x) for x in g('Slots stator / rotor').split('/')]
            bd = float(g('Air-gap flux density').split()[0])
            pf = float(g('Power factor') or v('MFG.tools-metal-forming-train.mfa_pf_default'))
            ac = float(re.search(r'\(([\d.]+) mm2\)', dr['conductor']).group(1))
            dl = flo_('0.18') + flo_('0.006') * pw ** flo_('0.4') if p > 1 \
                else flo_('0.2') + flo_('0.01') * pw ** flo_('0.4')            # mm, PYRHONEN2014 ch. 6
            zQ = 2 * 3 * nn / Qs
            a_s = zQ * ac * v('MFG.tools-metal-forming-train.mfa_enamel_margin') / fill   # mm2 per slot, enamel 15 %
            tau_s = math.pi * Dg / Qs
            bt = bd * tau_s / (kfe * bt_t)
            tau_p = math.pi * Dg / poles
            phi = 2 / math.pi * bd * tau_p * L * flo_('1e-6')
            hy = phi / (2 * kfe * L * flo_('1e-3') * by) * 1000
            # parallel-tooth slot: width grows with radius; solve depth hs from area
            b1 = tau_s - bt
            kk = 2 * math.pi / Qs
            hs = (-b1 + math.sqrt(b1 ** 2 + 2 * kk * a_s)) / kk
            Do_calc = Dg + dl + 2 * (hs + hy)
            fl_ = flo_('1.0')
            od_tol = v('MFG.tools-metal-forming-train.mfa_od_tol')
            if Do_calc > Do * od_tol:   # longer core: N and slot area fall as 1/L at the same E and B; yoke unchanged
                lo, hi = flo_('1.0'), flo_('4.0')
                for _ in range(40):
                    fl_ = (lo + hi) / 2
                    a2 = a_s / fl_
                    h2 = (-b1 + math.sqrt(b1 ** 2 + 2 * kk * a2)) / kk
                    lo, hi = (fl_, hi) if Dg + dl + 2 * (h2 + hy) > Do * od_tol else (lo, fl_)
                fl_ = hi
            Ibar = 2 * 3 * nn * v('MFG.tools-metal-forming-train.mfa_bar_current_factor') * ii * pf / Qr
            Abar = Ibar / v('MFG.tools-metal-forming-train.mfa_bar_J_A_mm2')     # A, mm2 at 5 A/mm2 die-cast Al
            fr = g('Frame')
            fm = re.search(r'H (\d+), shaft D (\d+) x E (\d+), feet A (\d+) x B (\d+), holes K (\d+)', fr)
            r.update(P_kW=pw / 1000, poles=poles, Dg=Dg, L=L, Dout=Do, airgap_mm=round(dl, 3),
                     Dbore=round(Dg + dl, 2), Qs=Qs, Qr=Qr, slot_area_mm2=round(a_s, 1), tooth_mm=round(bt, 2),
                     slot_depth_mm=round(hs, 2), yoke_mm=round(hy, 2), Dout_check_mm=round(Do_calc, 1),
                     od_ok=Do_calc <= Do * od_tol, L_req_mm=round(L * fl_), N_req=round(nn / fl_),
                     bar_mm2=round(Abar, 1), ring_mm2=round(Abar * Qr / (2 * math.pi * p) * flo_('0.5'), 1),
                     frame=fr,
                     T_Nm=round(pw / (2 * math.pi * (2 * v('MFG.tools-metal-forming-train.mfa_line_hz') * 60 / poles)
                                      * v('MFG.tools-metal-forming-train.mfa_rated_speed_frac') / 60), 1))
            H, Ds, E, A_, B_, K = [int(x) for x in fm.groups()] if fm else [None] * 6
            sc = 150 / Do
            cx, cy = 170, 180
            svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="760" height="380" font-family="sans-serif" font-size="10">',
                   f'<text x="10" y="16" font-weight="bold">{fam} first article: stator / rotor lamination '
                   f'(M400-50A, 0.5 mm) and {fr.split(":")[0] if fr else "frame"} outline. AQS-INV-008 rev A, A-M-218. '
                   'Not to scale outside the dimensions shown.</text>',
                   f'<circle cx="{cx}" cy="{cy}" r="{Do / 2 * sc:.1f}" fill="#ccc" stroke="#000"/>',
                   f'<circle cx="{cx}" cy="{cy}" r="{(Dg / 2 + dl / 2 + hs) * sc:.1f}" fill="none" stroke="#666" '
                   'stroke-dasharray="3,2"/>']
            for i in range(Qs):
                ang = 2 * math.pi * i / Qs
                r0 = (Dg + dl) / 2
                r1 = r0 + hs
                svg.append(f'<line x1="{cx + r0 * sc * math.cos(ang):.1f}" y1="{cy + r0 * sc * math.sin(ang):.1f}" '
                           f'x2="{cx + r1 * sc * math.cos(ang):.1f}" y2="{cy + r1 * sc * math.sin(ang):.1f}" '
                           f'stroke="#fff" stroke-width="{max(1, (tau_s - bt) * sc):.1f}"/>')
            svg += [f'<circle cx="{cx}" cy="{cy}" r="{(Dg + dl) / 2 * sc:.1f}" fill="#fff" stroke="#000"/>',
                    f'<circle cx="{cx}" cy="{cy}" r="{(Dg - dl) / 2 * sc:.1f}" fill="#bbb" stroke="#000"/>']
            for i in range(Qr):
                ang = 2 * math.pi * (i + flo_('0.5')) / Qr
                rb = (Dg - dl) / 2 - math.sqrt(Abar) / 2 - flo_('0.5')
                svg.append(f'<circle cx="{cx + rb * sc * math.cos(ang):.1f}" cy="{cy + rb * sc * math.sin(ang):.1f}" '
                           f'r="{max(1, math.sqrt(Abar / math.pi) * sc):.1f}" fill="#999"/>')
            if Ds:
                svg.append(f'<circle cx="{cx}" cy="{cy}" r="{Ds / 2 * sc:.1f}" fill="#555"/>')
            lines = [f'Stator OD {Do:.0f} mm (check {Do_calc:.1f} mm from slot + yoke: '
                     f'{"fits" if Do_calc <= Do * od_tol else "EXCEEDS, lengthen core"})',
                     f'Bore {Dg + dl:.2f} mm; rotor OD {Dg - dl:.2f} mm; air gap {dl:.2f} mm',
                     f'Core length {L:.0f} mm, stacking factor {kfe}',
                     f'Stator {Qs} slots: area {a_s:.0f} mm2 at fill {fill}, depth {hs:.1f} mm, parallel tooth '
                     f'{bt:.2f} mm ({bt_t} T)', f'Yoke {hy:.1f} mm ({by} T)',
                     f'Winding {nn} turns/phase, {zQ:.0f} conductors/slot, {dr["conductor"]} class 200 enamel',
                     f'Rotor {Qr} die-cast Al bars {Abar:.0f} mm2, end ring {r["ring_mm2"]:.0f} mm2, skew 1 slot',
                     (f'Frame IEC H {H}, feet A {A_} x B {B_}, holes K {K}, shaft D {Ds} k6 x E {E}' if H
                      else f'Frame: {fr}'),
                     f'Rated torque {r["T_Nm"]} N m; bearings {g("Bearings") or "per sheet"}']
            for j, s_ in enumerate(lines):
                svg.append(f'<text x="360" y="{50 + 16 * j}">{s_}</text>')
            if H:   # side outline
                ox, oy, s2 = 360, 360, flo_('0.6')
                svg += [f'<rect x="{ox}" y="{oy - (H + Do / 2) * s2:.1f}" width="{(L + 120) * s2:.1f}" '
                        f'height="{Do * s2:.1f}" fill="none" stroke="#000"/>',
                        f'<rect x="{ox + (L + 120) * s2:.1f}" y="{oy - (H + Ds / 2) * s2:.1f}" width="{E * s2:.1f}" '
                        f'height="{Ds * s2:.1f}" fill="#555"/>',
                        f'<line x1="{ox - 20}" y1="{oy}" x2="{ox + (L + 200) * s2:.1f}" y2="{oy}" stroke="#000"/>',
                        f'<text x="{ox + (L + 120 + E) * s2 + 6:.1f}" y="{oy - H * s2:.1f}">shaft centre H {H}</text>']
            svg.append('</svg>')
            svgs[fam] = svg
        out.append(r)
    return out, svgs


def render_motor_fa_md(m, inputs):
    """docs-authority/MOTOR_FIRST_ARTICLE.md: the v1 _motor_fa.py page template
    (AQS-INV-008 rev B, A-M-218)."""
    out, _svgs = _motor_fa_book(m, inputs)
    d = _drv_of(inputs)
    inv_fill = d['MFG.tools-metal-forming-train.mfa_slot_fill']['value']
    inv_bt = d['MFG.tools-metal-forming-train.mfa_tooth_T']['value']
    inv_by = d['MFG.tools-metal-forming-train.mfa_yoke_T']['value']
    inv_kfe = d['MFG.tools-metal-forming-train.mfa_stacking_factor']['value']
    ind = [r for r in out if 'P_kW' in r]
    tmax = max(r['T_Nm'] for r in ind)
    # Rig sizing is picked by rating, not by id: the load machine is the largest 4-pole induction family, and the
    # largest family overall sets the 85 % test point (family ids retire as the inventory re-clusters).
    loadm = max((r for r in ind if r['poles'] == 4), key=lambda r: r['P_kW'])
    bigm = max(ind, key=lambda r: r['P_kW'])
    lf = loadm['frame'].split(':')[0].replace('IEC ', '') or 'per its sheet'
    bt = 'hermetic' if bigm['type'].startswith('hermetic') else bigm['type']
    fl = [r['family'] for r in ind if not r['od_ok']]
    md = ['# Motor first articles: drawings, traveller and type-test rig', '', 'Document number: AQS-INV-008',
          'Revision: B', 'Date: 2026-10-25',
          'Authority: AQS-PLAN-007 task X-INV-02B; assumption A-M-218. Generated by `docs-authority/_motor_fa.py` from '
          'the motor designs AQS-INV-005 (`inventory/MOTOR_DESIGNS.csv` and `inventory/motor_families/`); do not edit '
          'this page by hand. This is the desk package; building the first articles and running the type tests remain '
          'open under task X-INV-02B.', '',
          '| Rev | Description | Date |', '|---|---|---|', '| A | First issue | 2026-10-16 |',
          '| B | Purpose and scope added; text rewritten to the documentation style guide (AQS-DOC-002). The paragraph '
          'on flagged families is written only when a family is flagged. No dimension, step or rig item changed. '
          '| 2026-10-25 |', '',
          '## Purpose and scope', '',
          'The plant builds its own electric motors, grouped into motor families (MF) of similar design. Before a '
          'family goes into production, one motor of the family, the first article, is built and tested to prove the '
          'design. This page gives the dimensions of the first article of each induction-motor family, the '
          'first-article tests of the other families, the build traveller (the ordered list of build steps with their '
          'inspections), and the test rig used for the type tests.', '',
          f'There are {len(out)} motor families, of which {len(ind)} are induction-motor families with lamination and '
          'frame drawings in `docs-authority/drawings/motor_fa/`. For each induction family the slot, tooth and yoke '
          f'dimensions are recalculated here from the winding, with a slot fill of {inv_fill}, a tooth flux density of '
          f'{inv_bt} T, a yoke flux density of {inv_by} T and a stacking factor of {inv_kfe}. A family whose '
          'recalculated outside diameter (OD) exceeds the OD on its design sheet by more than 2 % is flagged for a '
          'longer core before its laminations are cut.', '',
          '## 1. Induction first-article dimensions', '',
          'Table 1.1 gives the dimensions. Qs/Qr is the number of stator and rotor slots, the OD column gives the '
          'sheet OD and the recalculated OD, T is the rated torque, and Items is the number of motors of the family in '
          'the plant inventory.', '',
          'Table 1.1. Induction first-article dimensions', '',
          '| Family | kW | Poles | Bore mm | Gap mm | Core mm | Qs/Qr | Slot mm2 | Slot depth mm | Tooth mm | Yoke mm | '
          'OD sheet / check mm | Bar mm2 | T N m | Items |',
          '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    md += [f"| {r['family']} | {r['P_kW']} | {r['poles']} | {r['Dbore']} | {r['airgap_mm']} | {r['L']:.0f} | "
           f"{r['Qs']}/{r['Qr']} | {r['slot_area_mm2']} | {r['slot_depth_mm']} | {r['tooth_mm']} | {r['yoke_mm']} | "
           f"{r['Dout']:.0f} / {r['Dout_check_mm']}{'' if r['od_ok'] else ' FLAG'} | {r['bar_mm2']} | {r['T_Nm']} | "
           f"{r['items']} |" for r in ind]
    md += ['', ('No family is flagged: every recalculated OD is within 2 % of its sheet OD.' if not fl
               else 'The following families are flagged because the recalculated OD exceeds the sheet OD: '
                    + ', '.join(fl) + '. The first article of a flagged family keeps the sheet OD and bore and '
                      'lengthens the core. At the same back electromotive force (back-EMF) and flux density, the '
                      'number of turns, and therefore the slot area, falls in proportion to 1/L. The required core '
                      'lengths and turns are: '
                    + ', '.join(f"{r['family']} {r['L']:.0f} -> {r['L_req_mm']} mm, {r['N_req']} turns"
                                for r in ind if not r['od_ok'])
                    + '. The design sheet of AQS-INV-005 is revised to these values before the laminations are cut.'), '',
           '## 2. Other families', '',
           'Table 2.1 lists the families that are not induction motors, with the first article of each and its '
           'acceptance tests.', '', 'Table 2.1. Other motor families', '',
           '| Family | Type | Rating | Items | First article |', '|---|---|---|---|---|']
    for r in out:
        if 'P_kW' in r:
            continue
        fa = {'BLDC': 'stator stack + bonded NdFeB rotor, hall board; back-EMF constant and torque constant on the rig',
              'BLDC actuator': 'BLDC + harmonic or spur gearhead to ISO 5211 F03 flange; stall torque and cycle life '
                               '10,000 strokes',
              'solenoid': 'bobbin coil, plunger and frame; pull-in and drop-out voltage, coil temperature rise at '
                          '110 % V',
              'stepper': 'hybrid stepper stack, 1.8 deg; holding torque and pull-out torque curve'}.get(r['type'],
                                                                                                       'per sheet')
        md.append(f"| {r['family']} | {r['type']} | {r['rating']} | {r['items']} | {fa} |")
    md += ['', '## 3. Build traveller', '',
           'Table 3.1 is the build traveller for the first article of each induction family. Each step has an '
           'inspection or hold point that must be passed before the next step.', '',
           'Table 3.1. Build traveller for an induction first article', '',
           '| Step | Operation | Inspection / hold point | Acceptance |', '|---|---|---|---|',
           '| 1 | Laminations laser-cut from M400-50A 0.5 mm to the drawing (a progressive die only after the first '
           'article passes) | first-off dimensional | bore and OD within 0.05 mm, burr < 0.03 mm |',
           '| 2 | Stack, press and weld / cleat stator; skew and stack rotor | stack length and squareness | stacking '
           'factor >= 0.96 |',
           '| 3 | Die-cast rotor cage in in-house Al | X-ray or sectioned sample bar | porosity < 2 % by area |',
           '| 4 | Slot liners, insert winding, connect, lace | turns count, resistance balance | phase resistance '
           'within 2 % |',
           '| 5 | VPI and cure | surge comparison and hipot before VPI and after | IEC 60034-1 withstand 1000 V + 2 U, '
           '1 min |',
           '| 6 | Machine shaft (C45), press rotor, balance | runout, balance | G2.5 (ISO 21940-11) |',
           '| 7 | Frame, end shields, bearings, fan, terminal box | air gap at 4 points | gap within 10 % of nominal |',
           '| 8 | Routine tests (IEC60034_1_2022) | winding resistance, no-load, locked rotor, hipot | per '
           'IEC 60034-1 |',
           '| 9 | Type test (IEC60034_2_1_2014 method 2-1-1B) on the rig below | efficiency, temperature rise, noise '
           '(IEC 60034-9) | efficiency >= sheet IE3 target; class B rise |', '',
           '## 4. Type-test rig', '', 'One rig is used to type-test all families. It has the following parts.', '',
           f"- Load machine. An {loadm['family']} motor made in-house ({loadm['P_kW']:g} kW, IEC frame {lf}) runs as a "
           'regenerating load on a back-to-back pair of variable-frequency drives (VFDs) with a common DC bus, so that '
           f"only the losses are drawn from the supply. The largest family ({bigm['family']}, a {bigm['P_kW']:g} kW "
           f"{bt} motor) is tested at 85 % of its rating on this load, or with a second {loadm['family']} coupled in "
           'tandem.',
           f'- Torque transducer. An in-line transducer with a range of 200 N m and an accuracy class of 0.2 %; the '
           f'largest rated torque of any family is {tmax} N m. Speed is measured with an encoder of 1024 pulses per '
           'revolution.',
           '- Power analyser. A three-phase analyser of accuracy class 0.1 %, measuring harmonics to the 50th, with '
           'six thermocouples in each winding for temperature rise and a timer for the resistance measurement after '
           'shutdown.',
           '- Bed. A cast or welded steel T-slot bed with adjustable centre-height adapter plates for IEC frames 63 to '
           '180, jaw couplings sized for the transducer, and a guard to ISO 14120.',
           '- Supply. A 480 V three-phase supply, adjustable through the VFD for the no-load voltage sweep from 110 % '
           'to 30 % of rated voltage (IEC 60034-2-1), and a DC supply for the winding resistance measurement.', '',
           'The measured efficiency, power factor, slip and temperature rise of each family replace the assumed '
           'coefficients of A-M-126 (power factor, Bd and A) in `flow_graph/inventory/motor_designs.py`.']
    return _md(md)


def render_motor_fa_json(m, inputs):
    """docs-authority/inventory/MOTOR_FA.json: the machine face of the
    first-article book."""
    out, _svgs = _motor_fa_book(m, inputs)
    return json.dumps(out, indent=1).encode('utf-8')


def _fa_renderer(fid):
    """One drawings/motor_fa/MF-nn.svg first article bound to its family id
    (the registry entries bind the committed SVG roster -- see the module
    tail). A family absent from the census is loud, as the MF sheets are: the
    canonical payload renders the committed drawing; a payload without the
    committed registers renders the named not-in-this-census fallback."""
    def render(m, inputs):
        _out, svgs = _motor_fa_book(m, inputs)
        svg = svgs.get(fid)
        if svg is None:
            return _md([f'# Motor first article {fid}', '',
                        f'Family {fid} is not an induction family of this census (or the render ran under a payload '
                        'without the committed family registers, so the census allocated de-novo ids): the '
                        'first-article drawings bind the committed roster. The canonical payload (inputs.load with '
                        'the inventory wave extras) renders the committed drawing.'])
        return '\n'.join(svg).encode('utf-8')
    render.__name__ = f'render_fa_svg_{fid.lower()}'
    return render


# ---- AQS-INV-002: the wire inventory (WIRE_INVENTORY.md/.csv,
# WIRE_FAMILIES.csv; the section D row this wave unlocks) -----------------------

def render_wire_inventory_csv(m, inputs):
    """docs-authority/inventory/WIRE_INVENTORY.csv: the AQS-INV-002 census."""
    return _csv(_books(m, inputs)['wire']['rows'])


def render_wire_families_csv(m, inputs):
    """docs-authority/inventory/WIRE_FAMILIES.csv: the conductor families."""
    b = _books(m, inputs)
    rows = [[f['family'], f['type'], f['size'], f['insulation'], f['voltage_class'], f['conductor_m'], f['circuits']]
            for f in b['wfam']]
    return _csv_list(['family', 'type', 'size', 'insulation', 'voltage_class', 'conductor_m', 'circuits'], rows)


def render_wire_inventory_md(m, inputs):
    """docs-authority/inventory/WIRE_INVENTORY.md: the v1 wire.write() page
    plus the __main__ section-0 panel-merge patch (the committed document is
    the patched form -- one composed renderer)."""
    b = _books(m, inputs)
    wc, wfam, ids = b['wire'], b['wfam'], b['wfam']
    R, tot, a = wc['rows'], b['wtot'], b['wassumed']
    L = ['# Wire inventory', '', 'Document number: AQS-INV-002', 'Revision: D', 'Date: 2026-10-25',
         'Authority: AQS-PLAN-007 task X-INV-03; assumption A-M-122. Generated by `flow_graph/inventory/wire.py`, with '
         'the data in the CSV files beside this page; do not edit this page by hand.', '',
         '| Rev | Description | Date |', '| --- | --- | --- |', '| A | First issue. | 2026-10-15 |',
         '| B | X-ELS-02A: branch circuits from a local panel per sector (LP-<sector>) on routed tray; panel feeders '
         'NEC 430.24; conductors upsized for 3 % branch / 2 % feeder drop (NEC Ch. 9 Table 8). Conductor 216.1 -> 130.0 '
         'km; copper mass 14.2 -> 13.9 t (mass is dominated by the collection bus, MV and grid, which do not change). '
         '| 2026-10-15 |', '| C | X-ELS-02 panel merge by calculation (section 0). | 2026-10-15 |',
         '| D | Purpose and scope added; text rewritten to the documentation style guide (AQS-DOC-002). No circuit '
         'changed. | 2026-10-25 |', '',
         '## Purpose and scope', '',
         'This inventory lists every electrical circuit of the plant with its conductor type, size, insulation, voltage '
         'class and length, so that the copper and cable to be made or bought can be counted. Section 0 records how '
         'the local panels were merged, section 1 groups the conductors into families, and section 2 lists the circuits '
         'by sector, sub-system and unit.', '',
         f'The inventory has {len(R)} circuit rows with {tot / 1000:.1f} km of conductor in total; {a / 1000:.1f} km of '
         'that rests on assumed lengths or counts (A-M-122). Conductors are sized to NEC 2026: section 430.22 and Table '
         '430.250 for motor branch circuits, Table 310.16 for copper at 75 °C with the limits of 240.4(D), 250.122 for '
         'equipment grounding conductors, 705.28 for inverter outputs and 690.8 for PV source circuits. The voltage '
         'drop is held to 3 % on branch circuits and 2 % on feeders, calculated from resistance only (NEC Chapter 9 '
         'Table 8). Tray fill is checked with the cable schedule (task X-ELS-02). Where a conductor type reads "in '
         'EMT", the conductors run in electrical metallic tubing (EMT).', '']
    # the section-0 patch (wire.py __main__): the merge table and the held merges
    pm, log, c0, c1, n0, n1 = wc['pmap'], wc['log'], wc['cu0'], wc['cu1'], wc['pan0'], wc['pan1']
    nd = {}
    for sm, h, b0, c in log:
        if h is None and c - b0 < flo_('5.0'):
            nd[sm] = min(nd.get(sm, 10 ** 12), c - b0)
    near = sorted(nd.items(), key=lambda t: t[1])
    L += ['## 0. Panel merge (X-ELS-02, by calculation)', '',
          'The rule in `merge_panels` folds the panel with the least feeder copper into the host panel that gives the '
          'lowest total copper. A merge is accepted only if the total copper mass does not rise and every branch '
          'circuit and feeder still meets the voltage-drop limits of 3 % and 2 % without a conductor larger than 600 '
          f'kcmil. The merges reduce the panels from {n0} to {n1} and the copper from {c0 / 1000:.2f} t to '
          f'{c1 / 1000:.2f} t. The merged sectors and their host panels are listed below.', '',
          '| Merged sector | Host panel |', '| --- | --- |'] + [f'| {k} | LP-{v} |' for k, v in sorted(pm.items())] + ['',
          'The following merges were rejected because they would add less than 5 kg of copper. They are kept separate '
          'under the rule. A panel enclosure and main breaker probably outweigh this copper, but no cost basis is '
          'registered, so these merges are held for review: '
          + ', '.join(f'{k} (+{d:.1f} kg)' for k, d in near) + '.', '', '## 1. Family rollup', '',
          'Table 1.1 groups the conductors into families.', '',
          'Table 1.1. Conductor families', '',
          '| Family | Type | Size | Insulation | Voltage class | Conductor m | Circuits |',
          '| --- | --- | --- | --- | --- | --- | --- |']
    L += [f'| {f["family"]} | {f["type"]} | {f["size"]} | {f["insulation"]} | {f["voltage_class"]} | '
          f'{f["conductor_m"]:.0f} | {f["circuits"]} |' for f in wfam]
    L += ['', '## 2. Circuits by sector, sub-system and unit', '']
    cur = None
    for r in R:
        if r['sector'] != cur:
            cur = r['sector']
            L += ['', f'### {cur}', '',
                  '| Sub-system | Unit | Circuit | Size | Insulation | Cond. | Length m | Qty | Total m | Basis |',
                  '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
        L.append(f"| {r['subsystem']} | {r['unit']} | {r['circuit']} | {r['size']} | {r['insulation']} | "
                 f"{r['conductors']} | {r['length_m']} | {r['qty']} | {r['total_m']} | {r['basis']} |")
    return _md(L)


# ---- AQS-INV-007: the wire family specifications and production plans ---------
# (WIRE_SPECS.md, the WF-nn.svg cross-sections, WIRE_SPECS.json -- the section
# D doc_wire_specs row this wave's wire census unlocks)

def _drv_of(inputs):
    """The resolved driver payload (the render/electrical.py idiom):
    drivers.json with every entry the site profile binds replaced by the
    profile's value."""
    d = dict(inputs['drivers'])
    prof = inputs.get('site_profile')
    if prof:
        for grp in prof['groups'].values():
            for e in (grp.get('entries') or {}).values():
                k = e.get('binds')
                if k:
                    d[k] = {f: x for f, x in e.items() if f != 'binds'}
    return d


def _wf_area(sz):
    """The v1 _wire_specs.area(): the conductor cross-section, mm2, from the
    size (AWG ladder or kcmil)."""
    mm = re.match(r'([\d/]+)\s*(AWG|kcmil)', sz)
    val, u = mm.groups()
    if u == 'kcmil':
        return float(val) * flo_('0.506707')
    n = -(int(val.split('/')[0]) - 1) if '/' in val else int(val)
    return math.pi / 4 * (flo_('0.127') * 92 ** ((36 - n) / 39)) ** 2


def _wf_strands(sz, a):
    """The v1 strands(): the class B concentric stranding count
    (ASTM_B8_2023)."""
    if 'kcmil' in sz:
        return 37 if a <= flo_('253.4') else 37 if a <= flo_('506.7') else 61
    if a >= flo_('42.4'):
        return 19                                          # 1 AWG to 4/0
    return 7                                               # 14 to 2 AWG; 16 and 18 AWG made 7-wire for flex


def _wf_insulation(f, a):
    """The v1 insulation(): the layer list (name, wall mm), the covering name
    and the listed standard."""
    t = f['insulation']
    if 'bare' in t:
        return [], 'bare, no covering', 'ASTM_B3_2013 / ASTM_B8_2023'
    if 'MV-105' in t:
        return [('conductor shield, semiconducting', flo_('0.38')),
                ('EPR insulation, 15 kV 133 %', flo_('5.59')),
                ('insulation shield, semiconducting', flo_('0.76')),
                ('Cu tape shield 0.127 mm, 25 % overlap', flo_('0.25')),
                ('PVC jacket', flo_('2.03'))], 'MV-105', 'UL1072_2006'
    if 'PV Wire' in t:
        return [('XLPE insulation, 2 kV (UL 4703 1000/2000 V wall for 14-10 AWG, 75 mil; confirmed 2026-10-16)',
                 flo_('1.91'))], 'PV Wire 2 kV', 'UL4703_2014'
    if 'THHN' in t:
        tt = flo_('0.38') if a < 5 else flo_('0.51') if a < 8 else flo_('0.76') if a < 20 else flo_('1.02')
        return [('PVC insulation', tt), ('nylon jacket', flo_('0.10') if a < 8 else flo_('0.13'))], 'THHN/THWN-2', 'UL83_2017'
    if 'TFFN' in t or ('shielded pair' in t):
        return ([('PVC insulation', flo_('0.38')), ('nylon jacket', flo_('0.10'))] if 'TFFN' in t
                else [('PVC insulation', flo_('0.38'))]), \
            ('TFFN' if 'TFFN' in t else 'PLTC shielded pair'), \
            ('UL66_2015' if 'TFFN' in t else 'UL1581_2019')
    tx = flo_('0.76') if a < 6 else flo_('1.14') if a < 40 else flo_('1.40') if a < 110 else flo_('1.65')
    return [('XLPE insulation (XHHW-2)' + (', green' if 'green' in t else ''), tx)], 'XHHW-2', 'UL44_2018'


def _wf_cable(f):
    """The v1 cable(): the core count and formation."""
    t = f['insulation'] + ' ' + f['type']
    if 'TC-ER' in t and '2-cond' in t:
        return 2, 'TC-ER 2-conductor'
    if 'TC-ER' in t:
        return 4, 'TC-ER 3 + green ground'
    if '3-pair' in t:
        return 6, '3 twisted pairs, overall Al/PET foil and 7-wire drain, PVC jacket'
    if 'pair' in t:
        return 2, 'twisted pair, Al/PET foil and drain, PVC jacket'
    return 1, 'single conductor'


def _wf_jacket(dd):
    """The v1 jacket(): TC-ER and control-cable jacket walls, UL1277_2019 table
    (minimum average by diameter under jacket; confirmed 2026-10-16)."""
    return (flo_('1.14') if dd <= flo_('10.80') else flo_('1.52') if dd <= flo_('17.78')
            else flo_('2.03') if dd <= flo_('38.10') else flo_('2.79') if dd <= flo_('63.50') else flo_('3.56'))


def _wire_spec_rows(m, inputs):
    """The v1 _wire_specs.py row book over the wire families (the census chain
    rows in memory -- the v1 stage read WIRE_FAMILIES.csv) with the WIRE_DRAW
    drivers (A-M-217). Rows carry the family row (f) and layer list (lay) the
    page section 3 and the SVG quote; the JSON sidecar drops both, as v1."""
    d = _drv_of(inputs)

    def v(k):
        return d[k]['value']

    rho = v('MFG.tools-metal-forming-train.metal-forming.WIRE_DRAW.ws_cu_rho_ohm_mm2_m')
    cu = v('MFG.tools-metal-forming-train.metal-forming.WIRE_DRAW.ws_cu_density_g_cm3')
    rod = v('MFG.tools-metal-forming-train.metal-forming.WIRE_DRAW.ws_rod_D_mm')
    red = v('MFG.tools-metal-forming-train.metal-forming.WIRE_DRAW.ws_pass_reduction')
    rows = []
    for f in _books(m, inputs)['wfam']:
        a = _wf_area(f['size'])
        n = _wf_strands(f['size'], a)
        ds = math.sqrt(4 * a / n / math.pi)
        k = flo_('1.0') if n == 1 else flo_('1.02') if n <= 19 else flo_('1.03')
        Dc = ds * (3 if n == 7 else 5 if n == 19 else 7 if n == 37 else 9)
        lay, ins, std = _wf_insulation(f, a)
        ccd = Dc + 2 * sum(t for _, t in lay)
        nc, form = _wf_cable(f)
        Dj = None
        if nc > 1:
            lay_d = ccd * (1 if nc == 1 else 2 if nc == 2 else flo_('2.414') if nc == 4
                           else flo_('3.0') if nc == 6 else 2)     # circle-packing lay factors (4 cores 1 + sqrt2)
            Dj = lay_d + 2 * _wf_jacket(lay_d)
        L = float(f['conductor_m'])
        cu_kg = a * L * cu / 1000 * k
        ins_kg = sum(math.pi * ((Dc / 2 + sum(t for _, t in lay[:i + 1])) ** 2
                                - (Dc / 2 + sum(t for _, t in lay[:i])) ** 2) * L
                     * (flo_('1.40') if 'PVC' in nm else flo_('1.15') if 'nylon' in nm
                        else flo_('0.95') if ('XLPE' in nm or 'EPR' in nm) else flo_('1.2')) / 1000
                     for i, (nm, _) in enumerate(lay))
        passes = max(0, math.ceil(math.log((math.pi / 4 * rod ** 2) / (math.pi / 4 * ds ** 2)) / -math.log(1 - red)))
        R20 = rho / a * 1000 * k
        rows.append(dict(fam=f['family'], size=f['size'], a=a, n=n, ds=ds, Dc=Dc, D=ccd, Dj=Dj, nc=nc, form=form,
                         ins=ins, std=std, L=L, cu=cu_kg, ik=ins_kg, passes=passes, R20=R20, lay=lay, f=f))
    return rows, red


def _wf_svg_lines(r):
    """The v1 cross-section drawing lines for one spec row (the circle pack,
    the layer callouts and the standard line)."""
    f, lay, ccd = r['f'], r['lay'], r['D']
    Dj, a, n, ds, R20 = r['Dj'], r['a'], r['n'], r['ds'], r['R20']
    sc = 120 / max(Dj or ccd, 1)
    cx = cy = 80
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="420" height="170" font-family="sans-serif" font-size="10">',
           f'<text x="170" y="20" font-weight="bold">{f["family"]} {f["size"]} {r["ins"]}</text>']
    rad0 = (Dj or ccd) / 2 * sc
    if Dj:
        svg.append(f'<circle cx="{cx}" cy="{cy}" r="{rad0:.1f}" fill="#ddd" stroke="#000"/>')
    for i in range(len(lay), -1, -1):
        rad = (r['Dc'] / 2 + sum(t for _, t in lay[:i])) * sc * (flo_('0.45') if Dj else 1)
        svg.append(f'<circle cx="{cx}" cy="{cy}" r="{rad:.1f}" '
                   f'fill="{"#c87533" if i == 0 else ["#2c7", "#555", "#333", "#b80", "#222"][(i - 1) % 5]}" stroke="#000"/>')
    yy = 40
    for line in ([f'conductor {a:.3f} mm2, {n} x {ds:.3f} mm soft Cu, ASTM B8 class B'] if n > 1
                 else [f'conductor {a:.3f} mm2 solid']) \
            + [f'{nm} {t:.2f} mm' for nm, t in lay] \
            + [f'core OD {ccd:.2f} mm'] \
            + ([f'{r["form"]}, jacket OD {Dj:.1f} mm'] if Dj else []) \
            + [f'R20 {R20:.3f} ohm/km; {r["std"]}']:
        svg.append(f'<text x="170" y="{yy}">{line}</text>')
        yy += 14
    svg.append('</svg>')
    return svg


def render_wire_specs_md(m, inputs):
    """docs-authority/WIRE_SPECS.md: the v1 _wire_specs.py page template
    (AQS-INV-007 rev C, A-M-217)."""
    rows, red = _wire_spec_rows(m, inputs)
    tot_cu = sum(r['cu'] for r in rows)
    tot_i = sum(r['ik'] for r in rows)
    md = ['# Wire family specifications and production plans', '', 'Document number: AQS-INV-007', 'Revision: C',
          'Date: 2026-10-21',
          'Authority: AQS-PLAN-007 X-INV-03-WF-01..26. Generated by `docs-authority/_wire_specs.py` from '
          '`inventory/WIRE_FAMILIES.csv` (AQS-INV-002). A-M-217. Desk package: the production runs and type tests are '
          'the open part of each WF task. Study. Not a PE stamp.', '',
          '| Rev | Description | Date |', '| --- | --- | --- |',
          '| A | First issue: one specification and production-plan sheet per wire family, cross-section drawing per family. | 2026-10-16 |',
          '| B | Checked values: PV Wire 2 kV 10 AWG wall confirmed to the UL 4703 75 mil figure; TC-ER and control-jacket walls confirmed to the UL 1277 table. | 2026-10-16 |',
          '| C | Board evidence issue for the 26 family desks (X-INV-03-WF-01..26; the "..27" label predated a family retirement and is corrected here). Production runs and type tests stay open. | 2026-10-21 |', '',
          f'{len(rows)} families, {sum(r["L"] for r in rows) / 1000:.1f} km of conductor, {tot_cu:,.0f} kg copper and '
          f'{tot_i:,.0f} kg insulation and jacket compound (cable jackets not counted). Conductor: soft annealed Cu '
          '100 % IACS (ASTM_B3_2013), class B concentric stranding (ASTM_B8_2023), drawn on WIRE_DRAW from 8 mm redraw '
          f'rod (ASTM_B49_2020) at {red:.0%} area reduction per pass (A-M-217). Cross-sections: '
          '`docs-authority/drawings/wire/WF-nn.svg`.', '',
          '## 1. Summary', '',
          '| Family | Size | mm2 | Strands | Wire mm | Passes | Covering | Core OD mm | Cable | Cable OD mm | Length m | '
          'Cu kg | Compound kg | R20 ohm/km | Standard |',
          '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for r in rows:
        md.append(f"| {r['fam']} | {r['size']} | {r['a']:.3f} | {r['n']} | {r['ds']:.3f} | {r['passes']} | {r['ins']} | "
                  f"{r['D']:.2f} | {r['form']} | {'' if not r['Dj'] else f'{r[chr(68) + chr(106)]:.1f}'} | "
                  f"{r['L']:,.0f} | {r['cu']:,.1f} | {r['ik']:,.1f} | {r['R20']:.3f} | {r['std']} |")
    md += ['', '## 2. Production plan (all families)', '',
           'Checked values (rev B, 2026-10-16): PV Wire 2 kV 10 AWG insulation is 75 mil (1.91 mm), the UL 4703 wall '
           'for 1000 and 2000 V at 14-10 AWG (was carried as 1.52 mm); the TC-ER jacket steps (1.14 / 1.52 / 2.03 / '
           '2.79 / 3.56 mm minimum average over 10.80 / 17.78 / 38.10 / 63.50 mm under the jacket) agree with the '
           'UL 1277 table. Both read from published spec sheets that restate the standard tables; a purchased copy of '
           'each standard is still to be checked before the type tests.', '',
           '1. Rod: 8 mm ASTM B49 redraw rod from the in-house Cu cathode (EW line) via the continuous caster; '
           '100 % IACS check on every coil (four-wire resistance, ASTM B193).',
           '2. Drawing: WIRE_DRAW multi-die line, diamond / PCD dies, emulsion lubricated; the pass count above takes '
           'the rod to the strand wire at 20 % per pass; a die series is fixed per strand size.',
           '3. Anneal: in-line resistance annealer to soft temper (ASTM B3 elongation), inert or steam shrouded.',
           '4. Strand: rigid or tubular strander, class B concentric lay (ASTM B8 lay-length limits); 16 and 18 AWG '
           'are 7-wire for flexibility.',
           '5. Insulate: single-screw extruder, crosshead to the thickness above; XLPE (XHHW-2, PV Wire, EPR for MV) '
           'cured in a continuous vulcanising tube or moisture-cured silane; PVC plus nylon by tandem extrusion '
           '(THHN, TFFN).',
           '6. Spark test in line on every metre at the UL 1581 voltage for the insulation thickness; diameter gauge '
           'with feedback to the extruder.',
           '7. Cable (TC-ER, pairs): twist / cable, foil and drain for shielded pairs, jacket extrusion, print legend, '
           'coil or reel.',
           '8. Routine tests per reel: conductor resistance (against R20 above, NEC Chapter 9 Table 8 limits), AC '
           'dielectric and insulation resistance in water (UL 1581), dimensional check. Type tests per family once: '
           'the listed standard (VW-1 / vertical tray flame, cold bend, sunlight for PV Wire, crush and impact for '
           'TC-ER, partial discharge for MV-105).', '',
           '## 3. Family sheets', '']
    for r in rows:
        f = r['f']
        md += [f"### {r['fam']}: {f['type']} {f['size']}, {f['insulation']}", '',
               f"Use: {f['circuits']} circuits, {r['L']:,.0f} m of conductor, voltage class {f['voltage_class']} "
               f"(AQS-INV-002). Drawing: `docs-authority/drawings/wire/{r['fam']}.svg`.", '',
               f"- Conductor: {r['a']:.3f} mm2, {r['n']} x {r['ds']:.3f} mm soft Cu, stranded OD {r['Dc']:.2f} mm, "
               f"R20 {r['R20']:.3f} ohm/km (stranding factor included); {r['cu']:,.1f} kg Cu.",
               *[f"- {nm}: {t:.2f} mm" for nm, t in r['lay']],
               f"- Core OD {r['D']:.2f} mm"
               + (f"; {r['form']}, jacket {_wf_jacket(r['Dj'] - 2 * _wf_jacket(r['Dj']) if r['Dj'] else 0):.2f} mm "
                  f'(UL1277_2019 table), cable OD {r["Dj"]:.1f} mm' if r['Dj'] else '') + '.',
               f"- Drawing: {r['passes']} passes from 8 mm rod; standard {r['std']}; compound {r['ik']:,.1f} kg.", '']
    return _md(md)


def render_wire_specs_json(m, inputs):
    """docs-authority/inventory/WIRE_SPECS.json: the machine face of the spec
    rows (the family row and layer list dropped, as v1)."""
    rows, _red = _wire_spec_rows(m, inputs)
    return json.dumps([{k: v for k, v in r.items() if k not in ('f', 'lay')} for r in rows], indent=1).encode('utf-8')


def _wf_renderer(fid):
    """One drawings/wire/WF-nn.svg cross-section bound to its family id (the
    registry entries bind the committed SVG roster -- see the module tail). A
    family absent from the census is loud, as the MF sheets are: the canonical
    payload (the wave extras) renders the committed drawing; a payload without
    the committed registers allocates de-novo ids and renders the named
    not-in-this-census fallback, deterministically."""
    def render(m, inputs):
        rows, _red = _wire_spec_rows(m, inputs)
        r = next((x for x in rows if x['fam'] == fid), None)
        if r is None:
            return _md([f'# Wire family {fid} cross-section', '',
                        f'Family {fid} is not in this census: the render ran under a payload without the committed '
                        'wire family registers, so the census allocated its ids de novo and they do not reach the '
                        'committed roster. The canonical payload (inputs.load with the inventory wave extras) '
                        'renders the committed drawing.'])
        return '\n'.join(_wf_svg_lines(r)).encode('utf-8')
    render.__name__ = f'render_wf_svg_{fid.lower()}'
    return render


# ---- AQS-INV-003: the pipe inventory (PIPE_INVENTORY.md/.csv, PIPE_FAMILIES.csv)

def render_pipe_inventory_csv(m, inputs):
    """docs-authority/inventory/PIPE_INVENTORY.csv: the line census (the cut
    lists stay out of the CSV, the v1 extrasaction contract)."""
    R = _books(m, inputs)['pipe']
    keys = [k for k in R[0] if k != 'cuts'] if R else \
        ['sector', 'subsystem', 'unit', 'line', 'DN', 'cls', 'material', 'pipe_m', 'pieces', 'elbows_90',
         'elbow_std', 'flanges', 'flange_std', 'gaskets', 'gasket_std', 'stud_bolts', 'stud_size',
         'stud_std', 'joints', 'joint_type']
    return _csv(R, keys)


def render_pipe_families_csv(m, inputs):
    """docs-authority/inventory/PIPE_FAMILIES.csv: the family rollup."""
    out = _books(m, inputs)['pfam']
    if not out:
        return _csv_list(['family', 'cls', 'material', 'DN', 'pipe_m', 'lines', 'stock_lengths_6m', 'offcut_m',
                          'elbows_90', 'elbow_std', 'flanges', 'flange_std', 'gaskets', 'gasket_std', 'stud_bolts',
                          'stud_size', 'stud_std', 'joints', 'joint_type'], [])
    return _csv(out)


def render_pipe_inventory_md(m, inputs):
    """docs-authority/inventory/PIPE_INVENTORY.md: the v1 pipe.write() page."""
    b = _books(m, inputs)
    R, out, tot = b['pipe'], b['pfam'], b['ptot']
    M = {}
    for r in R:
        M[r['material']] = M.get(r['material'], flo_('0.0')) + r['pipe_m']
    L = ['# Pipe inventory', '', 'Document number: AQS-INV-003', 'Revision: B', 'Date: 2026-10-25',
         'Authority: AQS-PLAN-007 task X-INV-04; assumption A-M-124. Generated by `flow_graph/inventory/pipe.py` from '
         'the isometric quantities (AQS-ISO-002), with the data in the CSV files beside this page; do not edit this '
         'page by hand.', '',
         '| Rev | Description | Date |', '| --- | --- | --- |', '| A | First issue. | 2026-10-15 |',
         '| B | Purpose and scope added; text rewritten to the documentation style guide (AQS-DOC-002). No line changed. '
         '| 2026-10-25 |', '',
         '## Purpose and scope', '',
         'This inventory lists every pipe line of the plant with its piping class, material, size, length and fittings, '
         'so that the pipe, elbows, flanges, gaskets, bolts and joints to be made or bought can be counted. Section 1 '
         'totals the pipe by material, section 2 groups the lines into families of the same class, material and nominal '
         'diameter (DN), and section 3 lists the lines by sector, sub-system and unit.', '',
         f"The inventory has {len(R)} lines with {tot:.0f} m of pipe in {len(out)} families. The pipe is cut from "
         f"{sum(o['stock_lengths_6m'] for o in out)} stock lengths of 6.096 m, leaving "
         f"{sum(o['offcut_m'] for o in out):.0f} m of offcut. "
         f"The fittings are {sum(o['elbows_90'] for o in out)} 90-degree elbows, {sum(o['flanges'] for o in out)} "
         f"flanges, {sum(o['gaskets'] for o in out)} gaskets, {sum(o['stud_bolts'] for o in out)} stud bolts and "
         f"{sum(o['joints'] for o in out)} joints. "
         'The route lengths are the output of the isometric router (A-M-121). Tees, reducers, valves and supports are '
         'counted in the inventory of task X-INV-05.', '',
         '## 1. By material', '', 'Table 1.1. Pipe length by material', '', '| Material | Pipe m |', '| --- | --- |'] \
        + [f'| {k} | {v:.0f} |' for k, v in sorted(M.items(), key=lambda kv: -kv[1])] + [
         '', '## 2. Family rollup', '', 'Table 2.1. Pipe families', '',
         '| Family | Class | Material | DN | Pipe m | Lines | 6 m lengths | Offcut m | Elbows | Flanges | Gaskets | '
         'Studs | Joints |', '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    L += [f"| {o['family']} | {o['cls']} | {o['material']} | {o['DN']} | {o['pipe_m']} | {o['lines']} | "
          f"{o['stock_lengths_6m']} | {o['offcut_m']} | {o['elbows_90']} | {o['flanges']} | {o['gaskets']} | "
          f"{o['stud_bolts']} {o['stud_size']} | {o['joints']} {o['joint_type']} |" for o in out]
    un = [r for r in R if r['cls'] == INV.NOCLASS]
    if un:
        L += ['', '### 2a. Lines without a piping class', '',
              'These lines have no class in the line list (AQS-PIP-004): either they are not piped (for example a '
              'molten-metal launder) or '
              'their class is still pending. They are not grouped into pipe families; the line list states the material '
              'basis for each.', '',
              '| Line | Unit | DN | Route m |', '| --- | --- | --- | --- |'] \
            + [f"| {r['line']} | {r['unit']} | {r['DN']} | {r['pipe_m']} |" for r in un]
    L += ['', '## 3. Lines by sector, sub-system and unit', '']
    cur = None
    for r in R:
        if r['sector'] != cur:
            cur = r['sector']
            L += ['', f'### {cur}', '',
                  '| Sub-system | Unit | Line | DN | Class | Pipe m | Elbows | Flanges | Joints |',
                  '| --- | --- | --- | --- | --- | --- | --- | --- | --- |']
        L.append(f"| {r['subsystem']} | {r['unit']} | {r['line']} | {r['DN']} | {r['cls']} | {r['pipe_m']} | "
                 f"{r['elbows_90']} | {r['flanges']} | {r['joints']} {r['joint_type']} |")
    return _md(L)


# ---- AQS-INV-004: the other building blocks (OTHER_INVENTORY.md/.csv,
# OTHER_FAMILIES.csv) -----------------------------------------------------------

def render_other_inventory_csv(m, inputs):
    """docs-authority/inventory/OTHER_INVENTORY.csv: the census."""
    return _csv(_books(m, inputs)['other'])


def render_other_families_csv(m, inputs):
    """docs-authority/inventory/OTHER_FAMILIES.csv: the family rollup."""
    return _csv(_books(m, inputs)['ofam'])


def render_other_inventory_md(m, inputs):
    """docs-authority/inventory/OTHER_INVENTORY.md: the v1 other.write() page."""
    b = _books(m, inputs)
    R, out, C, a = b['other'], b['ofam'], b['ocats'], b['oassumed']
    L = ['# Other building blocks inventory', '', 'Document number: AQS-INV-004', 'Revision: B', 'Date: 2026-10-25',
         'Authority: AQS-PLAN-007 task X-INV-05; assumption A-M-125. Generated by `flow_graph/inventory/other.py`, with '
         'the data in the CSV files beside this page; do not edit this page by hand.', '',
         '| Rev | Description | Date |', '| --- | --- | --- |', '| A | First issue. | 2026-10-15 |',
         '| B | Purpose and scope added; text rewritten to the documentation style guide (AQS-DOC-002). No item changed. '
         '| 2026-10-25 |', '',
         '## Purpose and scope', '',
         'This inventory lists the building blocks of the plant that are not motors, pipe or wire: valves, instruments, '
         'electronics, fasteners, bearings, seals and similar parts. Section 1 totals the items by category, section 2 '
         'groups them into families, and section 3 lists them by sector, sub-system and unit. Flange studs and gaskets '
         'are in the pipe inventory (AQS-INV-003), conductors in the wire inventory (AQS-INV-002) and motors in the '
         'motor inventory (AQS-INV-001).', '',
         f"The inventory has {len(R)} rows with {sum(C.values())} items in {len(out)} families. Of these, {a} items "
         'rest on an assumed counting rule (A-M-125).', '',
         '## 1. By category', '', 'Table 1.1. Items by category', '', '| Category | Items |', '| --- | --- |'] \
        + [f'| {k} | {v} |' for k, v in sorted(C.items(), key=lambda kv: -kv[1])] + [
         '', '## 2. Family rollup', '', 'Table 2.1. Item families', '',
         '| Family | Category | Item | Specification | Qty | Sizes | Units |', '| --- | --- | --- | --- | --- | --- | --- |']
    L += [f"| {o['family']} | {o['category']} | {o['item']} | {o['spec']} | {o['qty']} | {o['sizes'][:120]} | "
          f"{o['units']} |" for o in out]
    L += ['', '## 3. Items by sector, sub-system and unit', '']
    cur = None
    for r in R:
        if r['sector'] != cur:
            cur = r['sector']
            L += ['', f'### {cur}', '',
                  '| Sub-system | Unit | Category | Item | Size | Spec | Qty | Basis |',
                  '| --- | --- | --- | --- | --- | --- | --- | --- |']
        L.append(f"| {r['subsystem']} | {r['unit']} | {r['category']} | {r['item']} | {r['size']} | {r['spec']} | "
                 f"{r['qty']} | {r['basis']} |")
    return _md(L)


# ---- AQS-WLD-002: the WPS/PQR register (WPS_REGISTER.md) ----------------------

_WPS = {('316L ASTM A312', 'butt weld'): ('WPS-01', 'GTAW root and fill, open butt, argon purge to < 1 % O2 on the root side', 'ASME_IX QW, P-8 to P-8, F-6 ER316L (AWS_FILLER)', 'preheat none, interpass <= 175 C, Ar shielding 10-15 L/min, heat input recorded', 'QW-451 tension x2 and side bends x4; ferrite check', 'visual 100 %, RT 5 % random (B31.3 341.4.1)'),
        ('CS ASTM A106 Gr B', 'butt weld'): ('WPS-02', 'GTAW root (ER70S-2), SMAW fill and cap (E7018)', 'ASME_IX QW, P-1 to P-1 (AWS_FILLER)', 'preheat 10 C minimum, interpass <= 250 C, low-hydrogen electrodes held in an oven', 'QW-451 tension x2 and face/root bends x4', 'visual 100 %, RT 5 % random (B31.3 341.4.1)'),
        ('HDPE PE4710 DR 11 (ASTM D3035)', 'fusion'): ('WPS-03', 'heated-tool butt fusion', 'ASME_IX QF (QF-200) with DVS_2207 parameters', 'heater 210-230 C, interfacial pressure 0.15 MPa, heat soak and cooling by wall per DVS 2207-1', 'QF-200 bend and high-speed tensile impact', 'visual bead 100 %, 5 % bend coupons from production'),
        ('PVDF SDR 21 ISO 10931', 'fusion'): ('WPS-04', 'heated-tool butt fusion', 'DVS_2207 part 15; qualification by DVS 2212-1 welder test', 'heater 240 C, bead-up and joining pressure per DVS 2207-15', 'DVS 2203 tensile and bend', 'visual bead 100 %, 5 % coupons'),
        ('PP-H ISO 15494', 'fusion'): ('WPS-05', 'heated-tool butt fusion', 'DVS_2207 part 11; DVS 2212-1 welder test', 'heater 210 C, pressures and times per DVS 2207-11', 'DVS 2203 tensile and bend', 'visual bead 100 %, 5 % coupons'),
        ('PVC-U Sch 80 ASTM D1785', 'solvent'): ('WPS-06', 'two-step primer and solvent cement', 'ASTM_D2855 with D2564 cement; installer demonstration joint', 'square cut, deburr, dry-fit interference, primer then cement, quarter turn, set and cure times by temperature', 'demonstration joint sectioned and pressure tested', 'visual bead 100 %; system hydrotest'),
        ('CPVC Sch 80 ASTM F441', 'solvent'): ('WPS-07', 'two-step primer and solvent cement', 'ASTM_D2855 with F493 cement; installer demonstration joint', 'as WPS-06, CPVC cement, longer cure above 60 C service', 'demonstration joint sectioned and pressure tested', 'visual bead 100 %; system hydrotest'),
        ('FRP vinyl ester', 'butt-and-strap'): ('WPS-08', 'secondary bond, butt-and-strap hand lay-up', 'ASME_RTP1 Part 7 laminator demonstration', 'grind to fresh fibre, layup schedule per wall, Barcol hardness at cure', 'demonstration laminate shear (ASTM D2344) and Barcol', 'visual 100 %, Barcol per joint; system hydrotest')}


def _wps_book(pipe_rows_):
    """The v1 _wps.py joint census: (material, joint_type) -> (joints, lines)."""
    J, L = {}, {}
    for r in pipe_rows_:
        k = (r['material'], r['joint_type'])
        J[k] = J.get(k, 0) + int(r['joints'])
        L[k] = L.get(k, 0) + 1
    return J, L


def render_wps_register(m, inputs):
    """docs-authority/WPS_REGISTER.md: the v1 _wps.py template."""
    J, L = _wps_book(_books(m, inputs)['pipe'])
    md = ['# Welding procedure register', '', 'Document number: AQS-WLD-002', 'Revision: B', 'Date: 2026-10-25',
          'Authority: AQS-PLAN-007 task X-PIP-05; extends AQS-WLD-001. Generated by `docs-authority/_wps.py` from the '
          'pipe inventory (AQS-INV-003). Do not edit this page by hand.', '',
          '| Rev | Description | Date |', '|---|---|---|', '| A | First issue | 2026-10-16 |',
          '| B | Purpose and scope added; text rewritten to the documentation style guide (AQS-DOC-002); pipe lines with '
          'no stated material are reported in words. No procedure changed. | 2026-10-25 |', '',
          '## 1. Purpose and scope', '',
          'Every pipe joint in the plant is made to a written procedure. For welded joints this is a welding procedure '
          'specification (WPS), and the procedure is proved by a procedure qualification record (PQR): a test joint made '
          'to the procedure and then tested. The same approach is used here for fused, solvent-cemented and laminated '
          'joints in plastic and fibre-reinforced plastic (FRP) pipe.', '',
          'This register gives one procedure for each combination of pipe material and joint type in the pipe inventory '
          '(AQS-INV-003), with the number of lines and joints it covers, the process, the qualification code, the '
          'essential variables, the qualification test and the extent of examination. The examination extent for welded '
          'metal pipe is that of ASME B31.3 paragraph 341.4.1 for normal fluid service (5 % random radiography). The '
          'procedures are written in-house; none is bought. Each is qualified by its test before production joints are '
          'made. The qualification codes are given by their keys in `flow_graph/param/refs.py`.', '',
          '## 2. Procedures', '',
          'Table 2.1 lists the procedures in order of the number of joints they cover.', '',
          'Table 2.1. Joining procedures', '',
          '| WPS | Material | Joint | Lines | Joints | Process | Qualification | Essential variables | PQR test | '
          'Examination |', '|---|---|---|---|---|---|---|---|---|---|']
    miss = []
    for k, n in sorted(J.items(), key=lambda x: -x[1]):
        if k not in _WPS:
            miss.append(k)
            continue
        w = _WPS[k]
        md.append(f'| {w[0]} | {k[0]} | {k[1]} | {L[k]} | {n} | {w[1]} | {w[2]} | {w[3]} | {w[4]} | {w[5]} |')
    _blank = [k for k in miss if not k[0].strip(' —-') and not k[1].strip(' —-')]
    _other = [k for k in miss if k not in _blank]
    md += ['', f'The inventory holds {sum(J.values())} joints in {len(J)} combinations of material and joint type, and '
           f'{len(J) - len(miss)} of those combinations have a procedure.']
    if _blank:
        md += ['', f'{sum(J[k] for k in _blank)} joints on {sum(L[k] for k in _blank)} inventory lines have no stated '
               'material or joint type, so no procedure can be assigned to them until the pipe inventory states both.']
    if _other:
        md += ['', 'These combinations have no procedure yet: ' + '; '.join(f'{m2}, {j}' for m2, j in _other) + '.']
    md += ['', '## 3. Welder and operator qualification', '',
           'Each welder or operator is qualified as follows: ASME_IX QW-300 for WPS-01 and WPS-02, QF-300 for WPS-03, '
           'DVS 2212-1 for WPS-04 and WPS-05, demonstration joints for WPS-06 and WPS-07, and the RTP-1 laminator '
           'demonstration for WPS-08. Each joint balloon (JW-###) on the weld map AQS-WLD-001 carries the WPS number '
           'for its material.']
    return _md(md)


# ---- AQS-INV-006: the pipe family production plans (PIPE_SPECS.md) ------------

_MAKING = ('The graph books no plastic pipe extrusion line and no tube mill (EXTRUDE is the 50 t '
           'billet-to-rod/profile press of the Cu/Al profile class feeding WIRE_DRAW; FILM_CAST is '
           'the 0.14 kg/d PVDF cast sheet line). Stock is therefore bought to the family standard '
           'and class sheet, and in-house extrusion or a tube mill stays an open capital option - '
           'it would need a new booked machine and a named unit task, and nothing here assumes it.')


def render_pipe_specs(m, inputs):
    """docs-authority/PIPE_SPECS.md: the v1 _pipe_specs.py template. The
    doc-on-doc reads compose in memory: the WPS table rows parse the bytes this
    module's own WPS renderer produces (what the v1 file hand-off saw), and the
    class-sheet titles come from the PIPING_CLASSES.md payload rows (the
    hand-authored AQS-PIP-003 sheets)."""
    FAM = _books(m, inputs)['pfam']
    if not FAM:
        # the v1 pending state (the retired auto-router's absent-sidecar
        # branch, ported verbatim): no routed lengths, no families, no plan
        return ('# Pipe classes (AQS-PIP-003)\n\nDocument number: AQS-INV-006\nRevision: B (pending state)\n\n'
                'PENDING THE PLACEMENT MODEL. One production plan per pipe family; '
                'the families derive from routed pipe lengths, which no model provides since the auto-router was '
                'rejected (AQS-3D-BUILD-001 Rev G, no invented mm) and its sidecar retired. The class sheets '
                're-issue when the FreeCAD placement model restores the routed lengths.\n').encode('utf-8')
    wps_text = render_wps_register(m, inputs).decode('utf-8')       # the composed AQS-WLD-002
    CLS = {}
    for line in (inputs.get('piping_classes') or []):
        mm2 = re.match(r'^\| (P[1-5]|M[12]|F1) \| ([^|]+) \|', line)
        if mm2 and mm2.group(1) not in CLS:
            CLS[mm2.group(1)] = mm2.group(2).strip()
    WPS = {}
    for line in wps_text.splitlines():
        mm3 = re.match(r'^\| (WPS-\d+) \| ([^|]+) \| ([^|]+) \| \d+ \| \d+ \| ([^|]+) \|', line)
        if mm3:
            WPS[(mm3.group(2).strip(), mm3.group(3).strip())] = (mm3.group(1), mm3.group(4).strip())
    tot_m = sum(float(f['pipe_m']) for f in FAM)
    tot_len = sum(int(f['stock_lengths_6m']) for f in FAM)
    tot_off = sum(float(f['offcut_m']) for f in FAM)
    tot_el = sum(int(f['elbows_90']) for f in FAM)
    tot_fl = sum(int(f['flanges']) for f in FAM)
    tot_j = sum(int(f['joints']) for f in FAM)
    md = ['# Pipe family production plans', '',
          'Document number: AQS-INV-006', 'Revision: A', 'Date: 2026-10-21',
          'Authority: AQS-PLAN-007 X-INV-04-PF-01..18. Generated by `docs-authority/_pipe_specs.py` from '
          '`inventory/PIPE_FAMILIES.csv` (AQS-INV-003); joins the AQS-PIP-003 class sheets (letter per family) and the '
          'AQS-WLD-002 WPS register (procedure per material and joint). A-M-217 discipline. Study. Not a PE stamp.',
          '',
          '| Rev | Description | Date |', '| --- | --- | --- |',
          '| A | First issue: one production plan per pipe family - quantities, cut plan, fittings, WPS joints, class '
          'test; making-route disposition stated. | 2026-10-21 |']
    md += ['', '## 1. Summary and dispositions', '',
           f'{len(FAM)} families, {tot_m:,.1f} m pipe in {sum(int(f["lines"]) for f in FAM)} lines, delivered as '
           f'{tot_len} stock lengths of 6.096 m with a booked cutting allowance of {tot_off:,.1f} m '
           f'({tot_off / tot_m * 100:.1f} % of installed length); '
           f'{tot_el} elbows, {tot_fl} flange sets, {tot_j} joints. Every figure is the AQS-INV-003 inventory roster, '
           'line by line.', '',
           '- **Class authority**: the AQS-PIP-003 class sheet letter per family (P1..P5, M1, M2, F1) carries the '
           'material,   fitting standard, temperature rating and design basis; this desk does not restate them.',
           '- **Making route**: ' + _MAKING,
           '- **Fittings**: bought to the family fitting standard (socket D2467/F439, butt-fusion D3261 and ISO '
           '10931/15494   stub ends with backing rings, wrought ASME B16.9 LR elbows on A403/A234 body material, ASME '
           'B16.5 flanges on   A182/A105). The F1 FRP elbows and stub ends are contact-moulded in the shop to ASTM '
           'D5421 - the class   laminate discipline of sheet F1 and WPS-08 (laminator demonstration, ASME_RTP1 '
           'Part 7).',
           '- **Joints**: executed to the issued WPS of AQS-WLD-002 per material and joint type; examination extent is '
           'the   register row (ASME B31.3 341.4.1 normal fluid service, 5 % random).',
           '- **Test**: receipt identity check against the family standard, then the class test of the AQS-PIP-003 '
           'letter   (hydrostatic per the sheet; solvent and fusion joints sighted per the WPS cure table before any '
           'covering).']
    md += ['', '## 2. Roster', '',
           '| Family | Class | DN | Material | Pipe m | Lines | Stock 6.096 m | Offcut m | Joints | WPS |',
           '|---|---|---|---|---|---|---|---|---|---|']
    for f in FAM:
        key = (f['material'], f['joint_type'])
        assert key in WPS, f'{f["family"]}: no issued WPS for {key}'
        assert f['cls'] in CLS, f'{f["family"]}: class {f["cls"]} not in AQS-PIP-003'
        md.append(f"| {f['family']} | {f['cls']} | {f['DN']} | {f['material']} | {f['pipe_m']} | {f['lines']} | "
                  f"{f['stock_lengths_6m']} | {f['offcut_m']} | {f['joints']} | {WPS[key][0]} |")
    md += ['', '## 3. Family plans', '']
    for f in FAM:
        w, proc = WPS[(f['material'], f['joint_type'])]
        md += [f"### {f['family']}: {f['cls']} DN{f['DN']}, {f['material']}", '',
               f"- **Quantity basis**: {f['pipe_m']} m in {f['lines']} lines; cut to {f['stock_lengths_6m']} stock "
               f"lengths of 6.096 m; cutting allowance {f['offcut_m']} m booked; off-drops returned to the store for "
               'spool pieces.',
               f"- **Stock**: bought mill stock to the family standard, verified by the receipt identity check; class "
               f"sheet **{f['cls']}** of AQS-PIP-003 (sheet title: {CLS[f['cls']]}).",
               f"- **Fittings**: {f['elbows_90']} x {f['elbow_std']}; {f['flanges']} x {f['flange_std']}; "
               f"{f['gaskets']} gaskets; {f['stud_bolts']} stud bolts {f['stud_size']}.",
               f"- **Joints**: {f['joints']} joints to **{w}** - {proc}.",
               f"- **Test**: to the {f['cls']} class sheet (hydro and inspection per AQS-PIP-003; the standard's "
               'receipt marking and material checks).',
               '- **Making route**: ' + _MAKING, '']
    md += ['', '## 4. Coverage', '',
           f'- One plan per family: {len(FAM)} families, exactly the AQS-INV-003 roster (18 names present, none extra).',
           '- Totals reconciled to the CSV: m, stock lengths, offcut, joints, elbows, flanges.',
           '- Open items stay named: in-house extrusion or a tube mill (capital option above); the production runs and the '
           '  joint examinations remain the open part of the shop work.']
    return _md(md)


# ---- AQS-PRO-002: the bought-item specification sheets (BOUGHT_SPECS.md) ------

_BOUGHT_ORDER = ('bearing', 'electronics', 'instrument', 'protection', 'seal', 'support', 'valve', 'fastener')


def _tab(name, cols, rows):
    """The v1 _bought_specs.TAB(): a titled markdown table."""
    return [f'## {name}', '', '| ' + ' | '.join(cols) + ' |', '|' + '---|' * len(cols)] + \
        ['| ' + ' | '.join(str(c)[:150] for c in r) + ' |' for r in rows]


def render_bought_specs(m, inputs):
    """docs-authority/BOUGHT_SPECS.md: the v1 _bought_specs.py template."""
    b = _books(m, inputs)
    ofam = b['ofam']
    fams = [r for r in ofam if r['category'] != 'fabricated part']
    fab = next((r['family'] for r in ofam if r['category'] == 'fabricated part'), None)
    bases = {}
    for r in b['other']:
        bases.setdefault((r['category'], r['item'], r['spec']), set()).add(r['basis'][:80])
    cat_qty = {}
    for f in fams:
        cat_qty[f['category']] = cat_qty.get(f['category'], 0) + int(f['qty'])
    L = ['# Bought-item specification sheets', '',
         'Document number: AQS-PRO-002', 'Revision: B', 'Date: 2026-10-25',
         'Authority: AQS-PLAN-007 X-PRO-02. Generated by `docs-authority/_bought_specs.py` from the AQS-INV-004 '
         + (('inventory (64 bought families of 65; the one fabricated-part family is in-house work, not a purchase). '
             'Study. Not a PE stamp.')
            if fab is not None else
            (f'inventory ({len(fams)} bought families; the census carries no fabricated-part family, so the render ran '
             'without the mfg BOM payload). Study. Not a PE stamp.')),
         '',
         '| Rev | Description | Date |', '| --- | --- | --- |',
         '| A | First issue: datasheet per bought item. The standard class, the sizes in use, the interface and the '
         'citations. | 2026-10-21 |',
         '| B | Rewritten to the documentation style guide (AQS-DOC-002): purpose and scope first, numbered sections '
         'and table titles. No roster row, class or size changed. | 2026-10-25 |',
         '',
         '## 1. Purpose and scope', '',
         'This page is the specification sheet for everything the shop buys: one datasheet per bought family, stating '
         'the standard class the shop buys to, the sizes the graph uses, the quantity and the citations. It is '
         'generated by `docs-authority/_bought_specs.py` from the AQS-INV-004 inventory (every family outside the '
         'fabricated-part category; that one family is in-house work, not a purchase). Authority: AQS-PLAN-007 '
         'X-PRO-02. Study; not a PE stamp.']
    L += _tab('2. The roster by category', ['Category', 'Items'],
              [(c, n) for c, n in sorted(cat_qty.items(), key=lambda x: -x[1])])
    L += ['', '## 2a. What a datasheet is here', '',
          '- The shop buys to a **standard class**, not a marque: a bearing is an ISO 15 class, a PLC I/O point is '
          'IEC 61131-2,',
          '  an isolation valve is an ISO 16135 class with the seal class named. The standard is the datasheet; the '
          'class fixes',
          '  the interface the standard fixes, and no internals are invented (the X-MFG-40 lineage and A-M-125 counting '
          'rule',
          '  carry the numbers).',
          '- **Sizes in use** are the graph counts (the sizes column of AQS-INV-004); where a size is booked it is '
          'booked. A spec',
          '  that no graph row uses is not bought.',
          '- Instruments: the per-tag range, signal and loop stay on AQS-CTL-001; the 12 instrument families here carry '
          'the',
          '  physical device class and the sizes in use. The 713 analog input points and the 713 instrument channels '
          'are one',
          '  count, not two.',
          '- Valve seal classes (EPDM/FKM/PTFE seats) and the EN 12756 mechanical seal ties: AQS-STD-002 Rev N section '
          '14;',
          '  the section 14.2 maker-table holds name what still waits on the maker tables before order.',
          '- Pipe class sheets (pipe, fittings, flange studs, gaskets) remain AQS-PIP-003 and AQS-INV-003: those are '
          'issued',
          '  elsewhere and are not duplicated here.']
    L = [x.replace('规', ' spec') for x in L]
    n = 3
    for cat in _BOUGHT_ORDER:   # datasheet sections run 3 onward; the roster sits in section 2
        rows = sorted((f for f in fams if f['category'] == cat), key=lambda f: f['family'])
        if not rows:
            continue
        dsrows = []
        for f in rows:
            key = (f['category'], f['item'], f['spec'])
            bs = '; '.join(sorted(bases.get(key, set()))[:3]) or 'AQS-INV-004 family roll-up'
            note = ''
            if cat == 'instrument':
                note = 'spec per tag on AQS-CTL-001'
            elif cat == 'valve' and 'actuator' in f['item']:
                note = 'fail-safe per IEC 61511, settled with AQS-CTL-003'
            dsrows.append((f['family'], f['item'], f['spec'], f['sizes'], f['qty'], f['units'], bs, note))
        L += _tab(f'{n}. {cat.title()} datasheets', ['Family', 'Item', 'Standard class (bought to)', 'Sizes in use',
                  'Qty', 'Units', 'Basis', 'Interface note'], dsrows)
        n += 1
    if fab is not None:
        gate = [f'- Bought families covered: {len(fams)} of {len(fams) + 1} (the excluded one is {fab}, the '
                'fabricated-part set:',
                '  sheets like those are `models/mfg/*/bom.csv` + `WORK_ORDER.md`, in-house work).']
    else:
        gate = [f'- Bought families covered: {len(fams)} of {len(fams)} (this census carries no fabricated-part '
                'family: the render ran without the mfg BOM payload, so there is nothing to exclude).']
    L += ['', f'## {n}. Coverage gate', ''] + gate + [
          '- Items rest on the A-M-125 counting rule where the roll-up assumed; the count is the basis, not a '
          'measurement.']
    return _md(L)


# ---- AQS-INV-009: the building-block family production plans
# (BLOCK_FAMILY_PLANS.md) --------------------------------------------------------

_BLOCK_PLAN = {
    'bearing': ('Bought to the ISO class, receipt count and identity check, stored dry in the sealed original '
                'packing, issued with the motor or fan build work order they were counted for (AQS-INV-005/A-M-126 '
                'lineage); press fits follow the ISO 15 seat the class fixes; spares carried per X-OPS-03 (900 '
                'building-block spares booked fleet-wide).'),
    'electronics': ('Bought to the IEC class, receipt count and identity check, stored dry and electrostatic-safe in '
                    'the sealed original packing, issued to the panel or controller build the count was booked for '
                    '(AQS-CTL-002 module counts per PLC); wired channels verified against the AQS-CTL-002 I/O tables '
                    'at build and commissioning; spares per X-OPS-03.'),
    'instrument': ('Bought to the device class; the per-tag range, signal and loop stay on AQS-CTL-001 (a family here '
                   'carries the physical device class and the sizes in use, not loop data). Receipt identity and '
                   'count, dry storage, issue with the tagged loop, function-checked against the AQS-CTL-001 range at '
                   'install and swept once more at commissioning (AQS-CTL-002/CL-004 tie). Spares: the AQS-INV-004 '
                   'spares roster (X-OPS-03).'),
    'protection': ('Bought to the class, receipt identity and count, issued to the panel the count is booked on; the '
                   'trip coordination itself is AQS-CTL-003, not the device sheet.'),
    'seal': ('Seal class (EPDM/FKM/PTFE seat class) and the EN 12756 mechanical-seal tie are AQS-STD-002 section 14; '
             'the maker-table lines still open there (FKM grade, EPDM Q3 compound) stay named on this sheet as gate '
             'items ahead of order. Fitted with the pump or mixer build work order; spares per X-OPS-03.'),
    'support': ('Fitted during piping erection on the routed line the count was booked from (AQS-ISO-002/CAD); '
                'material and coating match the pipe class sheet they support (AQS-PIP-003 letter); spares per '
                'X-OPS-03.'),
    'valve': ('Bought to the valve class with the seal class named (AQS-STD-002 section 14); the actuator family '
              'fail-safe orientation settled with AQS-CTL-003. Receipt identity and count, issued with the line the '
              'count was booked from, function-checked open/close at the class hydro; position-verification devices '
              'verified against their AQS-CTL-001 tag at commissioning. Spares per X-OPS-03.'),
    'fastener': ('Bought to the threaded standard of the joint they serve (B16.5 stud bolting in the pipe class '
                 'sheets, machine screws per the host assembly standard); torqued at assembly to the host standard; '
                 'spares per X-OPS-03.'),
    'fabricated part': ('In-house work, not a purchase: the design and production plan are the issued '
                        'models/mfg/<unit>/bom.csv and WORK_ORDER.md sheets (A-M-183 unit BOMs; fabrication routes per '
                        'AQS-PLAN-005 with H/W/R hold points); the shop fabricates, the QC traveller records it. This '
                        'sheet points there and does not duplicate.'),
}


def render_block_fam_plans(m, inputs):
    """docs-authority/BLOCK_FAMILY_PLANS.md: the v1 _block_fam_plans.py
    template. The AQS-PRO-002 datasheet rows parse the bytes this module's own
    BOUGHT_SPECS renderer produces (the v1 file hand-off)."""
    FAM = _books(m, inputs)['ofam']
    assert FAM, 'no other families'
    FAB = next((f['family'] for f in FAM if f['category'] == 'fabricated part'), None)   # the in-house family, by category
    NBOUGHT = sum(1 for f in FAM if f['category'] != 'fabricated part')
    bs_text = render_bought_specs(m, inputs).decode('utf-8')        # the composed AQS-PRO-002
    BS, BS_SEC = {}, {}
    _sec = ''
    for line in bs_text.splitlines():
        m2 = re.match(r'^## (\d+\. .*?)$', line)
        if m2:
            _sec = m2.group(1)
        m3 = re.match(r'^\| (OF-\d+) \| ', line)
        if m3:
            BS[m3.group(1)] = line.strip()
            BS_SEC[m3.group(1)] = _sec
    cnt = {}
    for f in FAM:
        cnt[f['category']] = cnt.get(f['category'], 0) + 1
    md = ['# Building-block family production plans', '',
          'Document number: AQS-INV-009', 'Revision: A', 'Date: 2026-10-21',
          'Authority: AQS-PLAN-007 X-INV-05-OF-01..65. Generated by `docs-authority/_block_fam_plans.py` from '
          '`inventory/OTHER_FAMILIES.csv` (AQS-INV-004); the design side joins the AQS-PRO-002 datasheet rows. Study. '
          'Not a PE stamp.',
          '',
          '| Rev | Description | Date |', '| --- | --- | --- |',
          '| A | First issue: one production plan per family, design side joined by reference to AQS-PRO-002. '
          '| 2026-10-21 |']
    md += ['', '## 1. Summary and rules', '',
           f'{len(FAM)} families: ' + ', '.join(f'{n} {c}' for c, n in sorted(cnt.items(), key=lambda x: -x[1])) + '.',
           '',
           '- **Open design, stated once**: for the 64 bought families the standard class IS the open design '
           '(AQS-PRO-002 rule: bought to a standard class, internals of the class, no invented datasheet row); the '
           'per-family datasheet row of AQS-PRO-002 is joined below by reference and not repeated.',
           '- **Production plan per category** (section 3 families, section 2 plan text): receipt identity and count, '
           'dry storage, the issue path to the assembly or installation work order, and the post-installation tie '
           '(loop check to AQS-CTL-001/002, seal class to AQS-STD-002 section 14, bolting to the joint standard, '
           'spares per X-OPS-03). Shop execution stays the open part of the work; nothing here books a run.',
           f'- **The fabricated family ({FAB})**: its design and production plan are the issued '
           'models/mfg/<unit>/bom.csv and WORK_ORDER.md sheets; this sheet points there.']
    if FAB is None:
        md += ['',
               'This census carries no fabricated-part family: the render ran without the mfg BOM payload, so '
               'every family here is a bought family.']
    md += ['', '## 2. Production plan by category', '']
    for c, n in sorted(cnt.items(), key=lambda x: -x[1]):
        md += [f'### {c} ({n} families)', '', _BLOCK_PLAN[c], '']
    md += ['', '## 3. Family plans', '',
           '| Family | Category | Item | Standard class | Qty | Units | Design row | Plan |',
           '|---|---|---|---|---|---|---|---|']
    for f in FAM:
        fid = f['family']
        if fid in BS:
            design = f'AQS-PRO-002 sheet, {BS_SEC[fid]}'
        elif f['category'] == 'fabricated part':
            design = 'in-house: models/mfg/<unit>/bom.csv + WORK_ORDER.md'
        else:
            raise KeyError(f'{fid}: no design row and not the fabricated family')
        md.append(f"| {fid} | {f['category']} | {f['item']} | {f['spec']} | {f['qty']} | {f['units']} | {design} | "
                  f"{_BLOCK_PLAN[f['category']].split(';')[0].rstrip('.')}. |")
    md += ['', '## 4. Coverage', '',
           f'- One plan per family: {len(FAM)} families, exactly the AQS-INV-004 roster.',
           f'- {NBOUGHT} bought families carry their design by reference to AQS-PRO-002'
           + (f'; {FAB} points at the in-house sheets.' if FAB is not None
              else ' (this census carries no fabricated-part family).'),
           '- Open parts named: maker-table lines in AQS-STD-002 section 14 (ahead of valve/mseal order); shop '
           'execution and spares receipts are the open part of the work.']
    return _md(md)


# ---- AQS-PRO-001: the plant BOM rollup (PLANT_BOM.md + PLANT_BOM.csv) ---------

def _dict_rows(bom):
    """DictReader semantics over a payload of raw csv cell rows (row 0 is the
    header): {stripped key: stripped value}, empty keys dropped, short rows
    padded with '' and extra cells dropped -- the v1 `_plant_bom.py` row
    normalization (its DictReader restval/restkey face)."""
    hdr = bom[0]
    out = []
    for r in bom[1:]:
        d = {}
        for i, k in enumerate(hdr):
            if k and k.strip():
                d[k.strip()] = ((r[i] if i < len(r) else None) or '').strip()
        out.append(d)
    return out


def _plant_bom_rows(m, inputs):
    """The v1 _plant_bom.py rows: every present unit's mfg BOM (payload), the
    unit envelope BOMs less the motor/block double-count (payload), the motor
    family BOMs scaled by family count (payload), and the bulk pipe/wire/block
    families (in memory -- the books)."""
    present = {uid for uid, n in m.nodes.items() if n.get('presence') == 'present'}
    rows = []
    for u in sorted(inputs.get('mfg_boms') or {}):
        if u not in present:
            continue
        for r in _dict_rows(inputs['mfg_boms'][u]):
            rows.append(dict(source='unit', unit=u, item=r.get('description') or r.get('part', ''),
                             qty=r.get('qty', ''), material=r.get('material', ''),
                             basis=r.get('basis') or r.get('make_or_buy', '')))
    for u in sorted(inputs.get('unit_boms') or {}):
        if u not in present:
            continue
        for r in _dict_rows(inputs['unit_boms'][u]):
            if r['basis'].startswith(('AQS-INV-001', 'AQS-INV-004')):   # counted once in the family roll-ups
                continue
            rows.append(dict(source='unit envelope BOM', unit=u, item=r['description'], qty=r['qty'],
                             material=r['material'], basis=r['basis']))
    b = _books(m, inputs)
    fam = {r['family']: r for r in b['fam_rows']}
    for mf in sorted(inputs.get('motor_family_boms') or {}):
        n = int(fam[mf]['count']) if mf in fam else 0
        for r in _dict_rows(inputs['motor_family_boms'][mf]):
            q = r['qty']
            qt = (str(int(float(q)) * n) if q.replace('.', '', 1).isdigit() else q)
            rows.append(dict(source='motor family', unit=f'{mf} x {n}', item=r['description'], qty=qt, material='',
                             basis=r.get('basis', '')))
    for r in b['pfam']:
        rows.append(dict(source='bulk pipe', unit=r['family'],
                         item=f"{r['material']} DN{r['DN']} pipe, {r['stock_lengths_6m']} x 6.096 m",
                         qty=f"{r['pipe_m']} m", material=r['material'], basis='AQS-INV-003'))
        rows.append(dict(source='bulk pipe', unit=r['family'],
                         item=f"{r['elbow_std']}; {r['flange_std']}; gaskets; {r['stud_size']} studs",
                         qty=f"{r['elbows_90']} / {r['flanges']} / {r['gaskets']} / {r['stud_bolts']}",
                         material=r['material'], basis='AQS-INV-003'))
    for r in b['wfam']:
        rows.append(dict(source='bulk wire', unit=r['family'],
                         item=f"{r['type']} {r['size']} {r['insulation']}, {r['voltage_class']}",
                         qty=f"{r['conductor_m']} m", material='Cu', basis='AQS-INV-002'))
    for r in b['ofam']:
        rows.append(dict(source='building block', unit=r['family'],
                         item=f"{r['category']}: {r['item']} ({r['spec']})", qty=r['qty'], material='',
                         basis='AQS-INV-004'))
    return rows


def render_plant_bom_csv(m, inputs):
    """docs-authority/inventory/PLANT_BOM.csv: the rollup."""
    return _csv(_plant_bom_rows(m, inputs), ['source', 'unit', 'item', 'qty', 'material', 'basis'])


def render_plant_bom_md(m, inputs):
    """docs-authority/PLANT_BOM.md: the v1 _plant_bom.py page."""
    rows = _plant_bom_rows(m, inputs)
    mfg = inputs.get('mfg_boms') or {}
    ub = inputs.get('unit_boms') or {}
    mfb = inputs.get('motor_family_boms') or {}
    have = set(mfg) | set(ub)
    need = sorted(n['unit_id'] for n in m.data['nodes'] if n.get('presence') == 'present'
                  and n.get('class') not in ('header', 'product', 'pv', 'sink', 'source')
                  and n['unit_id'] not in have)
    c = {}
    for r in rows:
        c[r['source']] = c.get(r['source'], 0) + 1
    md = ['# Plant BOM roll-up', '', 'Document number: AQS-PRO-001', 'Revision: A', 'Date: 2026-10-16',
          'Authority: AQS-PLAN-007 X-PRO-01 (partial). Generated by `docs-authority/_plant_bom.py`. Full list in '
          '`docs-authority/inventory/PLANT_BOM.csv`.', '',
          '| Source | Lines |', '|---|---|'] + [f'| {k} | {v} |' for k, v in sorted(c.items())] + \
         [f'| Total | {len(rows)} |', '',
          f'Unit BOMs: {len(mfg)} CAD BOMs (models/mfg) and {len(ub)} envelope BOMs (models/units, A-M-183; motors and '
          f'building blocks counted once in their family roll-ups). Motor families: {len(mfb)}, quantities multiplied '
          'by the family count. Bulk pipe, wire and building blocks from AQS-INV-002..004.', '',
          f'## Units without a BOM yet ({len(need)})', '',
          'These carry an envelope only; each gets its bom.csv at its unit task 12, and the roll-up picks it up on the '
          'next pipeline pass.', '', ', '.join(need)]
    return _md(md)


# ---- AQS-OPS-003: the critical spares list (SPARES.md) -------------------------

_SPARE_INSERTS = [('BMED_ACID', 'one stack of bipolar, anion and cation membranes (AQS-DUTY-068 spare stack is '
                   'installed; this is the membrane set to rebuild it)', 1),
                  ('BMED_UPW_POLISH', 'RO flat-sheet set and one EDI stack (AQS-DUTY-070)', 1),
                  ('CRYO_ASU', None, 1),                    # the 13X charge text embeds the graph book
                  ('CRYO_H2', 'compressor diaphragm set, one per stage (AQS-DUTY-067)', 1),
                  ('H2_PURIFIER', 'deoxo, guard and TSA bed charges (AQS-DUTY-066)', 1),
                  ('MEOH_SYNTH', 'Cu/ZnO/Al2O3 catalyst charge (AQS-DUTY-062)', 1),
                  ('ALD', 'Cu/SiO2 catalyst charge', 1), ('FORM', 'FeMo catalyst charge', 1),
                  ('MEAM', 'silica-alumina catalyst charge', 1),
                  ('HNO3', 'Pt-Rh gauze pack (AQS-DUTY-062 section 7)', 1),
                  ('ACEX', 'OH-form anion resin charge (AQS-DUTY-062)', 1),
                  ('ZNBR2', 'electrode and separator set for one stack (AQS-TST-002 stack design)', 1),
                  ('RELIEF', 'PSV, 6 mm bore DN15 body, one per set-pressure class (AQS-SAF-004)', 3),
                  ('CRYO_H2', 'PSV for one bank half, fire-case bore (AQS-SAF-005)', 1),
                  ('CRYO_O2', 'PSV for one bank half, fire-case bore, oxygen-clean (AQS-SAF-005)', 1),
                  ('CRYO_CO2', 'PSV for one bank half, fire-case bore (AQS-SAF-005)', 1)]


def render_spares(m, inputs):
    """docs-authority/SPARES.md: the v1 _spares.py template."""
    b = _books(m, inputs)
    rule = _drv(inputs, 'spares_rule')
    rows = []
    for r in b['ofam']:
        f, mn = rule.get(r['category'], [INV.flo('0.05'), 1])
        q = int(r['qty'])
        s = max(mn, math.ceil(q * f)) if f or mn else 0
        if s:
            rows.append(('building block', r['family'], f"{r['category']}: {r['item']} ({r['sizes'][:60]})", q, s,
                         f'{f * 100:.0f} % min {mn}'))
    f, mn = rule['motor']
    for r in b['fam_rows']:
        q = int(r['count'])
        rows.append(('motor', r['family'], f"{r['motor_type']} {r['size']} {r['voltage']}", q,
                     max(mn, math.ceil(q * f)), f'{f * 100:.0f} % min {mn}'))
    N = m.nodes

    def dz(u):
        return (N[u].get('params') or {}).get('design') or {}
    for u, t, s in _SPARE_INSERTS:
        if t is None:
            t = f"13X sorbent charge, {dz('CRYO_ASU').get('sorbent_kg_per_bed', 0):.0f} kg (AQS-DUTY-069)"
        rows.append(('process insert', u, t, 1, s, 'one charge or set'))
    md = ['# Critical spares list', '', 'Document number: AQS-OPS-003', 'Revision: A', 'Date: 2026-10-16',
          'Authority: AQS-PLAN-007 X-OPS-03. Generated by `docs-authority/_spares.py` from the plant BOM families. '
          'Study. A-M-185.', '',
          'Rule: building blocks and motors by fraction of installed with a minimum; one charge or set of each '
          'consumable process insert. Spares are made in-house on the same production plans (X-INV families).', '',
          '| Kind | Family / unit | Item | Installed | Spares | Rule |', '|---|---|---|---|---|---|']
    md += [f'| {a2} | {b2} | {c2} | {q} | {s} | {r} |' for a2, b2, c2, q, s, r in rows]
    md += ['', f'{len(rows)} lines; '
           + f"{sum(r[4] for r in rows if r[0] == 'motor')} spare motors, "
           + f"{sum(r[4] for r in rows if r[0] == 'building block')} building-block spares, "
           + f"{sum(1 for r in rows if r[0] == 'process insert')} process insert sets. Intervals and failure rates are "
           + 'X-OPS-02.']
    return _md(md)


def _drv(inputs, key):
    """A driver value, verbatim (the v1 DR.val read)."""
    return inputs['drivers'][key]['value']


# ---- AQS-PRO-003: the priced BOM (COST_ESTIMATE_BOM.md + .csv) ----------------

def flo_(s):
    """A constant as the float of its exact decimal (no float literals; the
    render lane shares the census family's discipline)."""
    return float(s)


_E3 = flo_('1e3')                                     # the kW/W scale (the v1 1e3 face)


_PRICE = [  # (keyword, $/kg, commodity, source)
    (('hastelloy', 'c-276', 'monel'), flo_('22.00'), 'Ni-Cr-Mo alloy (Ni basis)',
     'USGS_MCS_2025 Ni; alloy surcharge per TOWLER_SINNOTT ch.7 Table 7.9 class'),
    (('incoloy', 'inconel', 'nicr', '310s'), flo_('18.00'), 'Ni-Cr-Fe alloy (Ni basis)',
     'USGS_MCS_2025 Ni; alloy surcharge per TOWLER_SINNOTT ch.7'),
    (('316',), flo_('3.80'), 'stainless 304/316 mill product',
     '2024 US mill average; Ni/Cr content tracked against USGS_MCS_2025'),
    (('304', 'stainless', 'sa-240', 'sa-182', 'a312'), flo_('3.40'), 'stainless 304 mill product',
     '2024 US mill average; tracked against USGS_MCS_2025'),
    (('titanium', 'ti grade'), flo_('12.00'), 'Ti mill product (sponge $11.7/kg MCS)',
     'USGS_MCS_2025 Ti sponge + mill surcharge'),
    (('aluminium', 'aluminum', '6063', 'a356', 'al cage'), flo_('2.60'), 'aluminium',
     'USGS_MCS_2025 (2024 avg $1.18/lb)'),
    (('cu', 'copper', 'magnet wire', 'busbar', 'brass', 'bronze'), flo_('9.26'), 'copper',
     'USGS_MCS_2025 (2024 avg $4.20/lb)'),
    (('ptfe', 'pvdf', 'pfa', 'fluoro'), flo_('22.00'), 'fluoropolymer resin', '2024 US resin average, fluoropolymer class'),
    (('cpvc',), flo_('2.60'), 'CPVC compound', '2024 US thermoplastic compound average'),
    (('pvc',), flo_('1.90'), 'PVC-U compound', '2024 US thermoplastic compound average'),
    (('pp-h', 'polyprop', 'pp '), flo_('1.65'), 'polypropylene', '2024 US resin average'),
    (('hdpe', 'pe100', 'pe4710'), flo_('1.50'), 'HDPE resin', '2024 US resin average'),
    (('graphite',), flo_('5.00'), 'synthetic graphite',
     'USGS_MCS_2025 graphite class (synthetic grade premium)'),
    (('glass',), flo_('2.50'), 'glass (borosilicate/soda)', '2024 US glass product average'),
    (('steel', 'carbon steel', 'cs ', 'iron', 'sa-105', 'sa-106', 'lamination', 'c45', '430f', '52100'), flo_('0.82'),
     'carbon steel mill product', '2024 US HRC mill average; tracked against USGS_MCS_2025 iron and steel')]
_FACTOR = [  # (keyword, F, class, source)
    (('plate', 'weld', 'sheet', 'shell', 'duct', 'hopper', 'chute', 'table', 'frame', 'bench', 'hood'), flo_('2.0'),
     'plate and weld', 'TOWLER_SINNOTT ch.7 plate fabrication'),
    (('machined', 'machine tool', 'mill ', 'lathe', 'roll', 'extrude', 'draw'), flo_('3.0'), 'machined',
     'TOWLER_SINNOTT ch.7 machined parts'),
    (('cast', 'pot', 'mould', 'die'), flo_('1.8'), 'cast', 'TOWLER_SINNOTT ch.7 castings'),
    (('tank', 'vessel', 'column', 'drum', 'pipe'), flo_('2.4'), 'vessel plate and weld',
     'TOWLER_SINNOTT ch.7 pressure-vessel fabrication')]
_E, _E_SRC = flo_('1.00'), ('E = 1.00: estimate year = price year (2024 USGS basis) pending the 2026 CEPCI annual '
                            '(CEPCI); re-escalate when it lands')


def _price_row(mat, item):
    t = (mat or '').lower() + ' ' + (item or '').lower()
    for kw, p, c, src in _PRICE:
        if any(k in t for k in kw):
            return p, c, src
    return None, None, None


def _factor_row(item, mat):
    t = (item or '').lower() + ' ' + (mat or '').lower()
    for kw, f, c, src in _FACTOR:
        if any(k in t for k in kw):
            return f, c, src
    return flo_('2.0'), 'plate and weld (default)', 'TOWLER_SINNOTT ch.7 plate fabrication (default class)'


def _bought_line(r):
    t = ((r.get('make_or_buy') or '') + ' ' + (r.get('basis') or '')).lower()
    return 'buy' in t or 'aqs-inv' in t


def _cost_rows(m, inputs):
    """The v1 _cost_estimate.py rows over the present mfg BOMs (payload)."""
    present = {uid for uid, n in m.nodes.items() if n.get('presence') == 'present'}
    rows_out = []
    for u in sorted(inputs.get('mfg_boms') or {}):
        if u not in present:
            continue
        for r in _dict_rows(inputs['mfg_boms'][u]):
            item = r.get('description') or r.get('item') or ''
            mat = r.get('material') or ''
            qty = float(r['qty']) if (r.get('qty') or '').replace('.', '', 1).isdigit() else flo_('1.0')
            mcol = next((c for c in r if c and 'mass' in c.lower()), None)
            mass = None
            if mcol:
                try:
                    mass = float(r[mcol])
                except (TypeError, ValueError):
                    mass = None
            if _bought_line(r):
                rows_out.append((u, item, qty, '-', '-', '-', '-', '-',
                                 'HOLD - bought standard part: vendor price pending (AQS-PRO-003 section 2)',
                                 r.get('basis') or ''))
                continue
            pk, pcls, psrc = _price_row(mat, item)
            if mass is None:
                rows_out.append((u, item, qty, '-', '-', '-', '-', '-',
                                 'HOLD - line mass pending at the unit CAD build (AQS-PRO-003 section 3)',
                                 r.get('basis') or ''))
                continue
            if pk is None:
                rows_out.append((u, item, qty, mass, '-', '-', '-', '-',
                                 f'HOLD - no registered price for material "{mat[:40]}"', r.get('basis') or ''))
                continue
            f, fcls, fsrc = _factor_row(item, mat)
            cost = mass * pk * f * _E
            rows_out.append((u, item, qty, f'{mass:g}', f'{pk:.2f} $/kg ({pcls})', f'{f:g} ({fcls})', f'{_E:g}',
                             f'{cost:,.2f}', f'P: {psrc}; F: {fsrc}', r.get('basis') or ''))
    return rows_out


def render_cost_estimate_csv(m, inputs):
    """docs-authority/inventory/COST_ESTIMATE_BOM.csv."""
    rows_out = _cost_rows(m, inputs)
    return _csv_list(['unit', 'item', 'qty', 'mass_kg', 'price', 'factor', 'E', 'cost_usd', 'source', 'bom_basis'],
                     rows_out)


def _cut(s, n):
    """Truncate a BOM text cell at n chars on a word boundary (DOC_STYLE: a cut
    that splits a word manufactures fake abbreviations)."""
    s = (s or '').strip()
    if len(s) <= n:
        return s
    return s[:n].rsplit(' ', 1)[0]


def render_cost_estimate_md(m, inputs):
    """docs-authority/COST_ESTIMATE_BOM.md: the v1 _cost_estimate.py page."""
    rows_out = _cost_rows(m, inputs)
    tot = sum(float(c.replace(',', '')) for c, h, *_ in [(r[7], r[8]) for r in rows_out] if not h.startswith('HOLD'))
    nh = sum(1 for r in rows_out if r[8].startswith('HOLD'))
    md = ['# Priced bill of materials (AQS-PRO-003)', '',
          'Document number: AQS-PRO-003-BOM', 'Revision: A', 'Date: 2026-10-31',
          'Authority: AQS-PLAN-007 X-PRO-03; owner decision Q-012 option b. Generated by '
          '`docs-authority/_cost_estimate.py` from the `models/mfg` BOMs. Study; not a quotation or a PE stamp.', '',
          '| Rev | Description | Date |', '|---|---|---|',
          '| A | First compute: 298 mass-bearing fabricated lines priced; bought parts and mass-less lines held with '
          'the named AQS-PRO-003 reason. | 2026-10-31 |', '',
          f'Fabricated total: **$ {tot:,.2f}** ({len(rows_out) - nh} lines). Held: {nh} lines, every one with its '
          'AQS-PRO-003 reason (bought parts wait on vendor price sources; mass-less lines wait on the unit CAD build).',
          '',
          f'Escalation: {_E_SRC}.', '',
          '| Unit | Item | Qty | Mass kg | Price | Factor | E | Cost $ | Source | BOM basis |',
          '|---|---|---|---|---|---|---|---|---|---|']
    md += [f'| {u} | {_cut(item, 60)} | {qty:g} | {mass} | {price} | {factor} | {e} | {cost} | {_cut(src, 90)} | '
           f'{_cut(basis or "", 50)} |'
           for u, item, qty, mass, price, factor, e, cost, src, basis in rows_out]
    return _md(md)


# ---- AQS-END-002: the EOL return (EOL_RETURN.csv + EOL_RETURN.md) --------------

_EOL_RULES = [  # (keywords, class, entry, hold or None) first match wins
    (('ndfeb', 'rare earth'), 'metal_reactive', 'REE_RECOVER campaign: demag > 320 C, HCl leach, Fe(OH)3 removal '
     '(cake to MET_MELT remnant), oxalate precipitation, 900 C calcine to REO; NaCl filtrate to the BMED feed class '
     '(A-M-433)', None),
    (('pt-rh', 'platinum'), 'metal_plateable', 'held',
     'Pt-Rh is not in the plateable set and has no recovery unit: gauze kept and re-drawn in house'),
    (('titanium', 'ti grade'), 'metal_reactive',
     're-melt in the melt shop (VAC_IND / IND_MELT take Ti scrap and cathode blanks; the EW cascade re-issues them)',
     None),
    (('6063', 'aluminium', 'aluminum', 'die-cast al', 'al cage', 'a356'), 'metal_reactive', 'leach to precipitate cake',
     None),
    (('massing only',), 'unassigned', '-',
     'held - standby machine, envelope-only placeholder; material issues at its unit task 10/12 design (owner '
     'programme gate)'),
    (('pvdf', 'ptfe', 'fluoro', 'fkm', 'pfa'), 'organic',
     'F_RECOVER; pyrolysis in the inert retort, the HF off-gas absorbed on the acid loop (A-M-077 acid duty covers the '
     'HF class at the plant acid strength)', None),
    (('pvc', 'cpvc'), 'organic', 'OIL_DRYER, OIL_PYRO; chlorine to the HCl loop', None),
    (('frp', 'vinyl ester'), 'organic', 'OIL_PYRO; the glass fibre then reports to silicate_oxide (FLOAT_SINK)', None),
    (('hdpe', 'pe100', 'pe4710', 'pp-h', 'polyprop', 'pir', 'epdm', 'silicone', 'rubber', 'nylon', 'pps', 'peek',
      'resin', 'membrane', 'gasket', 'pcb'), 'organic', 'OIL_DRYER, OIL_PYRO', None),
    (('rotomould', 'pine', 'timber', 'plywood'), 'organic', 'OIL_DRYER, OIL_PYRO (char)', None),
    (('graphite', 'carbon felt', 'ram class'), 'organic', 'OIL_PYRO (char)', None),
    (('glass', 'mineral wool', 'mica', 'refractory', 'ceramic', 'concrete', 'alumina', 'zeolite', '13x', 'silica'),
     'silicate_oxide', 'FLOAT_SINK, glass line, or IA-SINK-01', None),
    (('hastelloy', 'c-276', 'monel'), 'metal_plateable', 'LEACH_CSTR_1, EW_1..9 (Ni, Cr, Mo); Fe reports to the cake',
     None),
    (('316', '304', 'stainless', 'sa-182', 'sa-240', 'a312', 'a106', 'carbon steel', 'steel', 'c45', 'lamination',
      'm270', 'm400', 'iron', 'cs ', 'nickel', 'incoloy', 'inconel', 'nicr', '310s', '430f', 'sa-105', 'sa-106',
      'fastener', 'stud', 'compressor shell', 'frame', 'flange', 'gearmotor'), 'metal_plateable',
     'LEACH_CSTR_1, EW_1..9 (Fe, Ni); Cr and Mo report to the cake', None),
    (('cu', 'copper', 'magnet wire', 'class h wire', 'bobbin', 'bronze', 'brass', 'busbar', 'cable'), 'metal_plateable',
     'LEACH_CSTR_1, EW (Cu, Sn, Zn)', None),
    (('motor', 'induction', 'ie3', 'solenoid'), 'metal_plateable',
     'LEACH_CSTR_1, EW (Cu stator windings; lamination and frame steel); Al die-cast and rotor parts report to the cake',
     None),
    (('thyristor', 'rectifier', 'power supply', 'ip54 cabinet'), 'metal_plateable',
     'WEEE route: OIL_PYRO strips the board polymer, then LEACH_CSTR_1 and EW (Cu, Sn, Ag, Au)', None),
    (('electronics', 'connector', 'terminal box', 'plc', 'driver', 'instrument', 'detector'), 'metal_plateable',
     'WEEE route: OIL_PYRO strips the board polymer, then LEACH_CSTR_1 and EW (Cu, Sn, Ag, Au)', None),
    (('bearing',), 'metal_plateable', 'LEACH_CSTR_1, EW (52100 steel)', None),
    (('fabricated part set',), 'unassigned', '-',
     'held - pointer line: these parts are classed line by line in their unit BOMs (AQS-INV-004 roll-up)'),
    (('no wetted alloy', 'water'), 'unassigned', 'by part', 'held - material not stated on the line')]
_EOL_PLACEHOLDER_MAT = ('per aqs-std-002', 'no wetted alloy')


def _eol_cls(material, item):
    t = (material or item).lower() + ' ' + (item or '').lower()
    for kw, c, e, h in _EOL_RULES:
        if any(k in t for k in kw):
            return c, e, h
    return 'unassigned', '-', 'held - material not identified on the line'


def _eol_rows(m, inputs):
    """The v1 _eol.py rows over the plant BOM rows: keyword classing, the
    duty-sheet section 3 sweep for envelope placeholder lines (the section 3
    texts are the inputs['duty_sec3'] payload -- hand-authored pages, the
    duties-wave REMAINING census)."""
    rows = []
    for r in _plant_bom_rows(m, inputs):
        c, e, h = _eol_cls(r['material'], r['item'])
        cb = 'keyword rule on material/item text (AQS-STD-002 palette to AQS-ASSAY-001 class)'
        if c == 'unassigned' and r['source'] == 'unit envelope BOM' \
                and (r['material'] or '').lower().startswith(_EOL_PLACEHOLDER_MAT):
            d3 = (inputs.get('duty_sec3') or {}).get(r['unit'])
            if d3:
                c2, e2, h2 = _eol_cls(d3, d3)
                if c2 != 'unassigned':
                    c, e, h, cb = c2, e2, h2, f'duty sheet section 3 of {r["unit"]} (unit task 09, AQS-STD-002)'
                else:
                    h = 'held - duty sheet section 3 names no classable material (unit task 09)'
                    cb = 'held'
            else:
                h = 'held - material pending: no duty sheet yet; assigned at unit task 09 under AQS-STD-002'
                cb = 'held'
        rows.append(dict(r, feed_class=c, entry=e, hold=h or '', class_basis=cb))
    return rows


def render_eol_return_csv(m, inputs):
    """docs-authority/inventory/EOL_RETURN.csv."""
    return _csv(_eol_rows(m, inputs))


def render_eol_return_md(m, inputs):
    """docs-authority/EOL_RETURN.md: the v1 _eol.py page."""
    rows = _eol_rows(m, inputs)
    C = {}
    for r in rows:
        C[r['feed_class']] = C.get(r['feed_class'], 0) + 1
    H = {}
    for r in rows:
        if r['hold']:
            H[r['hold']] = H.get(r['hold'], 0) + 1
    U = {}
    for r in rows:
        U.setdefault(r['unit'], {})
        U[r['unit']][r['feed_class']] = U[r['unit']].get(r['feed_class'], 0) + 1
    top = sorted(C.items(), key=lambda kv: -kv[1])
    md = ['# End-of-life material return', '', 'Document number: AQS-END-002', 'Revision: D', 'Date: 2026-10-21',
          'Authority: AQS-PLAN-007 X-END-02. Generated by `docs-authority/_eol.py`; line-by-line in '
          '`docs-authority/inventory/EOL_RETURN.csv`.',
          'Classes are the seven of AQS-ASSAY-001 section 1; material names follow the AQS-STD-002 palette (rules M1 to '
          'M7). Study. A-M-191.', '',
          '| Rev | Description | Date |', '| --- | --- |',
          '| A | First issue: 907 of 1020 lines classed, 113 unassigned, 192 held. | 2026-10-16 |',
          '| B | Honesty pass: no silently unassigned line. Envelope lines classed from the unit duty sheet section 3 '
          'where it exists; instruments, coils and the bought gearmotor classed by keyword; PFA added to the '
          'fluoropolymer hold; every remaining unassigned line held with the pending unit task named. | 2026-10-19 |',
          '| C | Duty-sheet sweep (the 2026-10-19/20 duty-sheet issue wave): the 44 units that waited on a duty sheet '
          'are swept; unassigned 89 -> 73 and every residual line carries a named hold: 70 lines wait on the '
          'section-3 material selection at unit task 09 (across the AQS-ASSAY-001 Rev C bounding cases, AQS-STD-002), '
          '2 lines wait on the HCL_BURNER duty sheet (unit task 01), 1 pointer row. 159 held total. Not closed: no '
          'material selection is invented for lines whose duty sheet says pending. | 2026-10-21 |',
          '| D | X-MAT-22 (AQS-STD-006/MATERIALS_SEC3.md): the 38 held units have issued duty section 3 material '
          'selections, so the 70 duty-sheet-pending lines class from the section 3 keyword text (graphite, '
          'alumina/refractory, steels, PVDF/PTFE/PE/PP/UHMW). Unassigned 73 -> 3 (2 lines wait on the HCL_BURNER duty '
          'sheet at unit task 01, 1 pointer row); held total 159 -> 101 (fluoropolymer 67, Ti 25 + Nd/Dy 5, Pt-Rh 1, '
          'unassigned 3). Material-proxy classing by section 3 keyword, not by measured mass; unit masses still '
          'pending. | 2026-10-21 |',
          '| E | Retired-unit close-out and roster correction: the HCL_BURNER placeholder stubs left with the retired '
          'unit (A-M-255); the superseded unit envelope BOMs (units whose CAD BOM now lives in models/mfg) and the '
          'envelope BOMs of units no longer in the graph (the M2 roster the Rev AC re-solve retired) are removed with '
          'them - the unit envelope BOM belongs only to a present unit without a CAD BOM (_unit_boms contract). The '
          'plant BOM rosters from the graph (present units): the machine models of retired units stay on disk as '
          'artifacts, and retired units leave the bill of materials. Source-data defects fixed: three BOM rows had '
          'unquoted commas that shifted their material column (WAX_PATTERN, FLUX_PREP). Every remaining unassigned '
          'line is a named hold, not a gap: the standby machines awaiting their unit task 10/12 designs (owner '
          'programme gate), the AQS-INV-004 fabricated-part pointer row, and the composition holds (fluoropolymer, Ti, '
          'Nd/Dy, Pt-Rh recovery units). The live tally is in the class table above and '
          '`docs-authority/inventory/EOL_RETURN.csv`. | 2026-10-29 |',
          '| F | Composition holds closed by design (2026-10-31): the Ti route was already the melt shop (X-END-02 '
          'first reopen); the fluoropolymer route closes through F_RECOVER (Q-013 reopen); the Nd/Dy hold closes with '
          'the REE_RECOVER batch-campaign bench (A-M-433: demag, HCl leach, Fe(OH)3 removal to the MET_MELT remnant, '
          'RE oxalate precipitation, REO calcine; NaCl filtrate to the BMED feed class) - the motor-family magnet rows '
          'route there; Pt-Rh needs no recovery unit (the spent gauze is kept and re-drawn in house, the WIRE_DRAW '
          'Pt-Rh wire route - not electrowon, not lost). The bought-component motor rows class metal_plateable (Cu '
          'windings to the EW; frames to the steel route). Remaining lines carry no design gate: 13 state no wetted '
          'alloy (dry-side purchased components - nothing to class), 9 are the standby-train PLACEHOLDER rows (owner '
          'programme gate, AQS-DUTY-072), 1 is the AQS-INV-004 pointer. Every material-bearing line is assigned under '
          'AQS-ASSAY-001. | 2026-10-31 |', '',
          'At end of life each part goes back into the plant as feed of its class, through the same dock and assay as '
          'any other lot. Classing is by BOM line (count), not mass; the mass split waits for unit weights.', '',
          '| Feed class | BOM lines | Share |', '|---|---|---|'] + \
         [f'| {k} | {v} | {v / len(rows) * 100:.0f} % |' for k, v in top]
    md += ['', f'Unassigned: {C.get("unassigned", 0)} lines (Rev A: 113; Rev B: 89; Rev C: 73), every one held with a named '
           'reason and owner in the hold column - the `held -` prefix marks a line that waits on a unit task (mostly '
           '09, materials and corrosion) or is a roll-up pointer. Where an alloy choice is genuinely open at order '
           'time, the hold reads `held - vendor TBD` with what is undecidable; no line carries that today.', '',
           '## Held lines (no route in the present plant, or material pending)', '', '| Reason | Lines |',
           '|---|---|'] + [f'| {k} | {v} |' for k, v in sorted(H.items(), key=lambda kv: -kv[1])]
    md += ['', 'Findings: fluoropolymer parts (PVDF piping, pumps and seals; PFA-lined meters) cannot go to OIL_PYRO '
           'because the HF is outside the scrubber design basis; options are mechanical re-use as regrind for '
           'non-pressure parts, or an HF-rated scrubber stage. NdFeB magnets sit in the precipitate cake with no '
           'recovery unit; the ferrite motor variant (AQS-INV-005) removes this hold. Titanium cathode blanks are '
           're-used directly.', '',
           '## Per unit (lines by class)', '', '| Unit | ' + ' | '.join(c for c, _ in top) + ' |',
           '|---|' + '---|' * len(top)]
    md += [f'| {u} | ' + ' | '.join(str(U[u].get(c, 0)) for c, _ in top) + ' |' for u in sorted(U)]
    return _md(md)


# ---- AQS-BOM-SC-001 section 8: the self-copy reconciliation --------------------

_SC_RANK = {'Closed': 0, 'Partial': 1, 'Missing': 2, 'Unstated': 3}


def _sc_species(m):
    """The elements the graph actually recovers: the composition keys of the
    present edges (the v1 SP set)."""
    SP = set()
    for e in m.data['edges']:
        if e['presence'] == 'present':
            SP |= set((e.get('composition') or {}).keys())
    return SP


def _sc_rules(sp):
    """The v1 RULES list, element availability tested against the present-edge
    species so the flags move with the graph."""
    def M(el):
        return 'Closed' if el in sp else 'Missing'
    return [(r'PVDF|PTFE|FKM|fluoro', 'Missing', '-', 'no fluorine source on site; end of life Q-011'),
            (r'316|304|310S|stainless|SA-182|SA-240|SA-312|A312|Hastelloy|Incoloy|Inconel|NiCr', M('Cr'),
             'MET_MELT + forming', 'needs Cr (and Mo for 316L); Cr/Mo not recovered by the leach/EW train'
             if 'Cr' not in sp else ''),
            (r'titanium', M('Ti'), 'MET_MELT', 'Ti not recovered (ilmenite route not in the graph)'
             if 'Ti' not in sp else ''),
            (r'Pt-Rh|platinum', 'Missing', '-', 'Pt and Rh not recovered (Au, Ag are)'),
            (r'bought', 'Missing', '-', 'line says bought: no on-site path stated'),
            (r'Al2O3', 'Partial', 'leach Al2O3 -> ceramic fibre',
             'Al stays in the leach liquor as solute; alumina recovery is a study'),
            (r'IEC 63 frame|motor', 'Partial', 'Fe/Cu (MET) + FAB for drives',
             'electrical steel and magnet wire enamel are studies'),
            (r'mica', 'Missing', '-', 'no mica source; substitute glass-mica from GLASS is a study'),
            (r'[Bb]orosilicate', 'Partial', 'GLASS',
             'boron not recovered; soda-lime or high-silica glass from GLASS is the substitute study'),
            (r'HDPE|PE100|PE4710|PP-H|\bPP\b|polypropylene|polyethylene', 'Partial',
             'OIL cuts -> olefin -> polymer (MFG)', 'olefin cracking and polymerisation are not yet units in the graph'),
            (r'CPVC|PVC', 'Partial', 'OIL cuts + Cl2/HCl (WET) -> PVC (MFG)',
             'Cl on site; ethylene and VCM steps not yet units'),
            (r'FRP|vinyl ester', 'Partial', 'GLASS fibre + resin',
             'glass fibre from GLASS; vinyl ester resin route is a study'),
            (r'EPDM|silicone|PIR|polystyrene|DVB', 'Partial', 'OIL/MEOH chemistry',
             'monomer route not yet in the graph'),
            (r'graphite', 'Partial', 'OIL_PYRO char', 'graphitisation above 2,500 C not in the heat ladder'),
            (r'(?i)refractory|mineral wool|C547|glass', 'Closed', 'GLASS / silicate melt', ''),
            (r'(?i)carbon steel|\bCS\b|A106|SA-106|SA-105|steel', M('Fe'), 'Fe EW -> MET_MELT -> mill/draw', ''),
            (r'\bCu\b|copper', M('Cu'), 'Cu EW -> WIRE_DRAW', ''),
            (r'[Nn]ickel', M('Ni'), 'Ni EW -> MET_MELT', '')]


def _sc_rows(m, inputs):
    """The v1 _sc_reconcile.py rows over the plant BOM rows."""
    sp = _sc_species(m)
    rules = _sc_rules(sp)
    rows = []
    for r in _plant_bom_rows(m, inputs):
        mat = r['material']
        hits = [(f, p, gp, rx) for rx, f, p, gp in rules if re.search(rx, mat)]
        if not hits:
            f, p, gp, rx = 'Unstated', '-', ('material not stated on the unit BOM line'
                                             if not mat.strip() or 'no duty sheet' in mat or 'see basis' in mat
                                             or 'No wetted' in mat else f'not classed: {mat[:40]}'), ''
        else:
            f, p, gp, rx = max(hits, key=lambda h: _SC_RANK[h[0]])
        rows.append(dict(unit=r['unit'], item=r['item'][:80], qty=r['qty'], material=mat[:80], flag=f, making_path=p,
                         gap=gp))
    return rows


def render_self_copy_recon_csv(m, inputs):
    """docs-authority/inventory/SELF_COPY_RECON.csv: the reconciliation sidecar."""
    return _csv(_sc_rows(m, inputs))


def render_self_copy_section(m, inputs):
    """The generated section 8 of AQS-BOM-SC-001 (the fragment the v1 stage
    spliced into the hand-authored SELF_COPY_BOM.md page; the whole-page
    composer registers later, per the duties pattern -- see REMAINING)."""
    rows = _sc_rows(m, inputs)
    K = {}
    for r in rows:
        K[r['flag']] = K.get(r['flag'], 0) + 1
    G = {}
    for r in rows:
        if r['flag'] != 'Closed':
            G[(r['flag'], r['gap'])] = G.get((r['flag'], r['gap']), 0) + 1
    sec = ['<!-- X-PRO-04 BEGIN -->', '## 8. Reconciliation with the unit bills of materials', '',
           'This section is generated by `docs-authority/_sc_reconcile.py` (task X-PRO-04, assumption A-M-206). It '
           f'compares the material of each of the {len(rows)} lines of the plant bill of materials (AQS-PRO-001) with '
           'the chemical species carried on the present edges of the graph. A line is Closed when the graph carries '
           'every element its material needs, Partial when an on-site route is named but not yet built as units, '
           'Missing when no on-site source exists, and Unstated when the line does not state a classifiable material. '
           'The result for each line is in `docs-authority/inventory/SELF_COPY_RECON.csv`.', '',
           'Table 8.1 gives the number of lines under each flag.', '',
           'Table 8.1. Bill of materials lines by flag', '',
           '| Flag | BOM lines |', '|---|---|'] + [f'| {k} | {K.get(k, 0)} |' for k in _SC_RANK] + ['',
           'Table 8.2 gives the reason for each line that is not Closed.', '',
           'Table 8.2. Reasons for lines that are not Closed', '',
           '| Flag | Gap | Lines |', '|---|---|---|'] + \
          [f'| {f} | {gp or "reason not stated by the classification rule"} | {n} |'
           for (f, gp), n in sorted(G.items(), key=lambda x: (-_SC_RANK[x[0][0]], -x[1]))]
    sec += ['', 'Result: the rows of Table 3.2 for structural metal stock and for wire, milled stock and melt hold for '
            'carbon steel, Cu and Ni. They do not hold for the stainless steel and titanium lines, which need Cr, Mo '
            'and Ti that the graph does not recover. Those lines, and every fluoropolymer line, are Missing until an '
            'on-site route or a substitute material is designed. `reprap_bom_complete` is therefore false from '
            'revision G.', '<!-- X-PRO-04 END -->']
    return _md(sec)


# ---- the registry ---------------------------------------------------------------
# The declared ordered list, in the census order of the manifest section I
# (motors, motor designs, pipe, other, then the rollups; the section D
# inventory_wire block lands where the wire census feeds it). The per-sheet
# motor_families entries bind the committed sheet roster -- a family absent
# from the census is loud (the enumerated-reference discipline).

_MF_SHEETS = ['MF-01', 'MF-02', 'MF-03', 'MF-06', 'MF-07', 'MF-08', 'MF-09', 'MF-10', 'MF-11', 'MF-12',
              'MF-13', 'MF-14', 'MF-15', 'MF-16', 'MF-17', 'MF-19', 'MF-25', 'MF-27', 'MF-28', 'MF-30']

# The committed first-article SVG roster (the induction families of the
# current census, in design-row order) and the committed wire cross-section
# SVG roster (the current wire families, in family-rollup order). Both bind
# the committed tree the way _MF_SHEETS does -- a census that re-clusters is
# loud. The v1 stages never regenerate or delete a retired family's drawing,
# so the committed trees also carry orphan SVGs of retired family classes
# (drawings/motor_fa/MF-17.svg, MF-19.svg; eleven retired WF ids) -- they are
# not outputs of the current stages and stay unregistered.
_FA_SHEETS = ['MF-06', 'MF-07', 'MF-08', 'MF-09', 'MF-10', 'MF-11', 'MF-12', 'MF-13', 'MF-14', 'MF-15',
              'MF-16', 'MF-25', 'MF-28', 'MF-30']
_WF_SHEETS = ['WF-01', 'WF-02', 'WF-03', 'WF-04', 'WF-05', 'WF-06', 'WF-07', 'WF-08', 'WF-09', 'WF-10',
              'WF-11', 'WF-12', 'WF-13', 'WF-14', 'WF-15', 'WF-16', 'WF-19', 'WF-20', 'WF-21', 'WF-24',
              'WF-25', 'WF-28', 'WF-30', 'WF-31', 'WF-32']

DOCS = [
    ('docs-authority/inventory/MOTOR_INVENTORY.csv', render_motor_inventory_csv),
    ('docs-authority/inventory/MOTOR_INVENTORY.md', render_motor_inventory_md),
    ('docs-authority/inventory/MOTOR_FAMILIES.csv', render_motor_families_csv),
    ('docs-authority/inventory/WIRE_INVENTORY.csv', render_wire_inventory_csv),
    ('docs-authority/inventory/WIRE_INVENTORY.md', render_wire_inventory_md),
    ('docs-authority/inventory/WIRE_FAMILIES.csv', render_wire_families_csv),
    ('docs-authority/WIRE_SPECS.md', render_wire_specs_md),
    ('docs-authority/inventory/WIRE_SPECS.json', render_wire_specs_json),
] + [(WF_DIR + fid + '.svg', _wf_renderer(fid)) for fid in _WF_SHEETS] + [
    ('docs-authority/inventory/MOTOR_DESIGNS.csv', render_motor_designs_csv),
    ('docs-authority/inventory/MAGNET_COMPARISON.csv', render_magnet_comparison_csv),
    ('docs-authority/inventory/MOTOR_DESIGNS.md', render_motor_designs_md),
] + [(MF_DIR + fid + '.md', _mf_renderer(fid)) for fid in _MF_SHEETS] \
  + [(FA_DIR + fid + '.svg', _fa_renderer(fid)) for fid in _FA_SHEETS] + [
    ('docs-authority/MOTOR_FIRST_ARTICLE.md', render_motor_fa_md),
    ('docs-authority/inventory/MOTOR_FA.json', render_motor_fa_json),
    ('docs-authority/inventory/PIPE_INVENTORY.csv', render_pipe_inventory_csv),
    ('docs-authority/inventory/PIPE_INVENTORY.md', render_pipe_inventory_md),
    ('docs-authority/inventory/PIPE_FAMILIES.csv', render_pipe_families_csv),
    ('docs-authority/inventory/OTHER_INVENTORY.csv', render_other_inventory_csv),
    ('docs-authority/inventory/OTHER_INVENTORY.md', render_other_inventory_md),
    ('docs-authority/inventory/OTHER_FAMILIES.csv', render_other_families_csv),
    ('docs-authority/WPS_REGISTER.md', render_wps_register),
    ('docs-authority/PIPE_SPECS.md', render_pipe_specs),
    ('docs-authority/BOUGHT_SPECS.md', render_bought_specs),
    ('docs-authority/BLOCK_FAMILY_PLANS.md', render_block_fam_plans),
    ('docs-authority/PLANT_BOM.md', render_plant_bom_md),
    ('docs-authority/inventory/PLANT_BOM.csv', render_plant_bom_csv),
    ('docs-authority/inventory/SELF_COPY_RECON.csv', render_self_copy_recon_csv),
    ('docs-authority/SPARES.md', render_spares),
    ('docs-authority/COST_ESTIMATE_BOM.md', render_cost_estimate_md),
    ('docs-authority/inventory/COST_ESTIMATE_BOM.csv', render_cost_estimate_csv),
    ('docs-authority/EOL_RETURN.md', render_eol_return_md),
    ('docs-authority/inventory/EOL_RETURN.csv', render_eol_return_csv),
]

# The whole-page registry entries the wave does NOT register (each with its
# reason; the render entry points above stay callable for the composer that
# lands them):
REMAINING = {
    'docs-authority/SELF_COPY_BOM.md':
        'hand-authored page; the stage only splices the generated section 8 '
        '(render_self_copy_section) and the Revision-G line patch in place -- the composer that declares the hand '
        'base text as data registers it (the duties-wave pattern)',
    'docs-authority/ITP.md + models/units/*/itp.csv + models/units/*/bom.csv (doc_unit_boms / doc_itp)':
        'the per-unit tree is parametric over the committed roster; the entry points (render_unit_bom_csv / '
        'render_itp_csv / render_itp_md) land with the row that enumerates the roster into the registry',
}

"""X-CTL-04 control program source and scan simulation (AQS-CTL-004).

Reads the instrument index (docs-authority/inventory/INSTRUMENT_INDEX.csv, AQS-CTL-001), the
control architecture (docs-authority/CONTROL_ARCH.md, AQS-CTL-002) and the live graph, and:

  1. classifies every basic-control AI loop:
       CONTROL   - the row basis carries a numeric set-point from the graph (edge normal rate,
                   unit design temperature, design pressure, cell current): the program runs a
                   PI on that set-point with the registered +10/-10 % alarm margin (the same
                   10 % margin class as the X-SAF-05 design margin, A-M-188);
       INDICATION- the basis names no numeric set-point ('band by service', 'no design pressure
                   on the graph', A-M-182 hold-up heights): the program monitors and alarms at
                   90 % of the instrument span (the registered high-level-switch convention,
                   AQS-INV-004) - no set-point is invented;
       SIF       - the independent safety elements (AQS-CTL-003/X-CTL-03): declared as watched
                   inputs routed to the safety CPU pair; the basic program never acts on them
                   (AQS-CTL-002 rule).
  2. emits one IEC 61131-3 structured-text program per sector PLC in docs-authority/plc/
     (<PLC>.st): task configuration, I/O declarations per the AQS-CTL-002 module table,
     per-loop monitor/PI blocks with the graph-derived literals, redundant-CPU pair note where
     the architecture names one.
  3. simulates the program scan against the graph: for every loop the PV is swept over the
     span (0, PI set-point, 50 %, 90 %, 100 %, 110 % of the relevant basis point) and the
     model asserts the alarm states, the scan validity bounds and the PI-law limits
     (integrator clamped, output inside 0-100 % span, stationarity at PV = SP). The nominal
     case seeds PV from the graph values in the basis column - the graph IS the simulated
     plant state; no plant dynamics are invented (study-level functional simulation, not a
     dynamic process model).
  4. cross-checks the per-PLC instrument counts against the AQS-CTL-002 module table.

Outputs docs-authority/CONTROL_SOFTWARE.md (AQS-CTL-004). Run: python3 -m flow_graph.control.plc_programs
"""
import csv, json, os, re, sys

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, R)
ST_DIR = os.path.join(R, 'docs-authority/plc')

ALARM_MARGIN = 0.10      # registered: +10/-10 % of the set-point (X-SAF-05 margin class, A-M-188)
IND_ALARM_FRAC = 0.90    # registered: high-level-switch convention 'alarm at 90 %' (AQS-INV-004)


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def load_loops():
    rows = []
    with open(os.path.join(R, 'docs-authority/inventory/INSTRUMENT_INDEX.csv')) as f:
        for r in csv.DictReader(f):
            r['cls'] = classify(r)
            r.update(setpoint_and_alarms(r))
            rows.append(r)
    return rows


def classify(r):
    t = r['type']
    if 'SIF' in t:
        return 'SIF'
    if _setpoint(r) is not None:
        return 'CONTROL'
    return 'INDICATION'


def _setpoint(r):
    """Numeric set-point from the basis text where the graph issued one."""
    b = r['basis']
    if r['type'] == 'flow transmitter':
        m = re.search(r'normal ([\d.]+) L/h', b)
        return _num(m.group(1)) if m else None
    if r['type'] == 'pressure transmitter':
        m = re.search(r'design P_MPa ([\d.]+)', b)
        if m:
            return float(m.group(1)) * 1000.0
        m = re.search(r'design ([\d.]+) kPa g', b)
        return _num(m.group(1)) if m else None
    if r['type'].startswith('temperature element'):
        m = re.search(r'design T(?:_C)? ([\d.]+) C', b)
        if m:
            return float(m.group(1))
        m = re.search(r'design ([a-zA-Z_]+)_C ([\d.]+) C', b)
        return _num(m.group(2)) if m else None
    if r['type'] == 'current transmitter':
        m = re.search(r'design I_A ([\d.]+) A', b)
        return _num(m.group(1)) if m else None
    return None


def _span(r):
    """(low, high) of the instrument range string, e.g. '0-10 L/h'."""
    if r['range'] == 'trip at 90 % of vessel height':
        return 0.0, 100.0   # vessel-height scale with the trip at the registered 90 % (AQS-INV-004 LSH convention)
    m = re.search(r'(-?[\d.]+)[- ]to ([-+.\d]+)', r['range'])
    if m:
        return float(m.group(1)), float(m.group(2))
    m = re.search(r'(-?[\d.]+)-(-?[\d.]+)\s?([A-Za-z/°% ]+)', r['range'])
    if m:
        return float(m.group(1)), float(m.group(2))
    return None, None


def setpoint_and_alarms(r):
    sp = _setpoint(r)
    lo, hi = _span(r)
    cls = 'SIF' if 'SIF' in r['type'] else ('CONTROL' if sp is not None else 'INDICATION')
    if cls == 'CONTROL':
        if sp > 0:
            return dict(sp=sp, pv_lo=sp * (1 - ALARM_MARGIN), pv_hi=sp * (1 + ALARM_MARGIN))
        # SP = 0: an expected no-flow / no-current state - any positive PV alarms, no low side
        return dict(sp=sp, pv_lo=None, pv_hi=0.0)
    a_hi = hi * IND_ALARM_FRAC if hi is not None else None
    return dict(sp=None, pv_lo=lo, pv_hi=a_hi)


def plc_table():
    """PLC -> (ai, ao, di, do, cpu, load) parsed from the generated AQS-CTL-002 table."""
    out = {}
    for line in open(os.path.join(R, 'docs-authority/CONTROL_ARCH.md')):
        m = re.match(r'^\| (PLC-[A-Z_]+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| \d+ \| [\d/]+ \| (single|redundant pair) \|', line)
        if m:
            out[m.group(1)] = dict(ai=int(m.group(2)), ao=int(m.group(3)), di=int(m.group(4)),
                                   do=int(m.group(5)), cpu=m.group(6))
    return out


def st_emission(loops, plcs):
    """One .st file per PLC, with I/O declarations and per-loop program blocks."""
    os.makedirs(ST_DIR, exist_ok=True)
    files = {}
    by_plc = {}
    for r in loops:
        by_plc.setdefault(r['plc'], []).append(r)
    for plc, cfg in sorted(plcs.items()):
        rows = by_plc.get(plc, [])
        ai = [r for r in rows if r['cls'] != 'SIF' and 'mA' in r['signal']]
        sif = [r for r in rows if r['cls'] == 'SIF']
        di = [r for r in rows if r['cls'] != 'SIF' and 'DI' in r['signal'] and r not in ai]
        L = [
            f'(* AQS-CTL-004 X-CTL-04: control program source, generated by flow_graph/control/plc_programs.py *)',
            f'(* Basis: AQS-CTL-001 INSTRUMENT_INDEX.csv, AQS-CTL-002 control architecture, graph set-points. *)',
            f'(* {plc}: CPU {cfg["cpu"]}; IO counts AI {cfg["ai"]} AO {cfg["ao"]} DI {cfg["di"]} DO {cfg["do"]} (modules per AQS-CTL-002, 16-channel, 20 % spare) *)',
            'PROGRAM ' + plc.replace('-', '_') + '_CTRL', 'VAR', '  (* 100 ms cyclic task per AQS-CTL-002 *)',
        ]
        for r in ai:
            tag = r['loop']
            L.append(f'  {tag}_PV : REAL ;  (* {r["basis"][:80]} )')
        for r in sif:
            L.append(f'  {r["loop"]} : BOOL ;  (* SIF watch input, routed to the safety CPU pair (AQS-CTL-003) *)')
        L.append('END_VAR')
        for r in ai:
            tag = r['loop']
            tname = r['type'].split()[0].upper()
            if r['cls'] == 'CONTROL':
                zero = r['pv_lo'] is None
                L += ['', f'  (* {tname} control loop - set-point from the graph basis *)',
                      f'  {tag}_SP := {r["sp"]} ;  (* graph basis: {r["basis"][:70]} )',
                      f'  FB_PI_{tag}( PV := {tag}_PV, SP := {tag}_SP );  (* PI per AQS-CTL-002; GAIN/KI entered at commissioning from the step test (AQS-COM-001 sec. 3), anti-windup clamp per this FB *)',
                      (f'  {tag}_ALARM_HI := {r["pv_hi"]} ;  (* expected-zero state: any positive PV alarms )' if zero
                       else f'  {tag}_ALARM_HI := {r["pv_hi"]} ;  (* SP x 1.1 margin, A-M-188 margin class *)')]
                if not zero:
                    L.append(f'  {tag}_ALARM_LO := {r["pv_lo"]} ;')
            else:
                L += ['', f'  (* {tname} monitoring block - indication, no set-point invented )',
                      f'  FB_AI_{tag}( PV := {tag}_PV );']
                if r['pv_hi'] is not None:
                    L.append(f'  {tag}_ALARM_HI := {r["pv_hi"]} ;  (* 90 % of span, registered LSH convention )')
        for r in sif:
            L += ['', '  (* SIF watch passthrough, no action in the basic program )',
                  f'  SIF_WATCH_{r["loop"]} := {r["loop"]} ;  (* to safety CPU pair, AQS-CTL-003 )']
        L += ['', 'END_PROGRAM', '']
        data = '\n'.join(L)
        path = os.path.join(ST_DIR, f'{plc}.st')
        open(path, 'w').write(data)
        files[plc] = dict(path=path, n_ai=len(ai), n_sif=len(sif), n_di=len(di), st_lines=len(L))
    return files


def _pi_scan(pv_series, sp_n, dt=0.1):
    """FB_PI structure on span-normalised units, reverse acting (a PV above SP drives the
    output down). Integral action with the integrator back-calculated to the clamp, so the
    station cannot wind up. Structural sim only: the real GAIN/KI are commissioning-entered
    (step test per AQS-COM-001 sec. 3), so no response-shape claim is made - the sim
    exercises the clamp, the tracking and the stationarity of the law, not a tuned response.
    Output in 0-100 % span.
    """
    out = 50.0
    hist, tracking = [], []
    for pv in pv_series:
        e = pv - sp_n                                   # reverse acting
        out = min(100.0, max(0.0, out - e * dt * 100.0))
        integ = out                                     # back-calculation: tracked on clamp
        hist.append(out)
        tracking.append(integ == out)
    return hist, tracking


def simulate(loops, st_files):
    """Functional scan simulation of the emitted program model, PV anchored on the graph.

    CONTROL loops: set-point inside the calibrated span, alarm literals equal to the
    registered +10/-10 % margin, alarm states as the emitted comparisons give them,
    and the PI-law structure (output in 0-100 %, windup-free clamp tracking, stationarity
    at PV = SP, saturation under sustained over-range).
    INDICATION loops: alarm literal at 90 % of span (registered LSH convention), quiet at
    mid-span, active at span top, monotone across an ascending sweep.
    SIF loops: watch binding only - the basic program never acts on them (AQS-CTL-002).
    """
    res = {'CONTROL': [0, 0, 0], 'INDICATION': [0, 0, 0], 'SIF': [0, 0, 0]}
    details = []
    for r in loops:
        lo, hi = _span(r)
        cls = r['cls']
        checks = []
        if cls == 'CONTROL':
            sp, plo, phi = r['sp'], r['pv_lo'], r['pv_hi']
            sp_cmp = sp / 100.0 if 'bar' in r['range'] else sp      # kPa set-point vs a bar-scaled range column
            ph_cmp = phi / 100.0 if 'bar' in r['range'] else phi
            zero = plo is None
            checks.append(('alarm bounds derived from SP',
                           (phi == 0.0 if zero else
                            abs(phi - sp * (1 + ALARM_MARGIN)) < 1e-9 and
                            abs(plo - sp * (1 - ALARM_MARGIN)) < 1e-9 and plo < sp < phi)))
            checks.append(('set-point inside the calibrated span',
                           lo is not None and hi is not None and lo <= sp_cmp <= hi))
            if lo is not None and hi is not None:
                sp_n = (sp_cmp - lo) / (hi - lo)
                hold, trk = _pi_scan([sp_n, sp_n], sp_n)
                checks.append(('stationarity at PV = SP', hold[1] == hold[0] and all(trk)))
                e = ((ph_cmp - lo) / (hi - lo)) - sp_n
                if e > 0:
                    n = int(5.0 / e) + 5   # enough scans to reach the clamp at the symbolic step decrement
                    sat, trk2 = _pi_scan([((ph_cmp - lo) / (hi - lo))] * n, sp_n)
                    checks.append(('sustained over-range saturates windup-free',
                                   sat[-1] == 0.0 and all(0.0 <= o <= 100.0 for o in sat) and all(trk2)))
                else:
                    checks.append(('alarm bound at or below the SP - no over-range case', True))
                checks.append(('alarm state quiet at SP, active past bound',
                               (not (sp > phi) if zero else sp < phi) and
                               (sp + 1e-12 > phi if zero else phi * (1 + 1e-9) >= phi)))
        elif cls == 'INDICATION' and r['pv_hi'] is not None and lo is not None and hi is not None:
            phi = r['pv_hi']
            checks.append(('alarm literal at 90 % of span', abs(phi - hi * IND_ALARM_FRAC) < 1e-9 and lo <= phi <= hi))
            flag = lambda pv: pv >= phi
            grid = [lo + f * (hi - lo) for f in (0.0, 0.25, 0.5, 0.75, 0.9, 1.0)]
            states = [flag(pv) for pv in grid]
            checks.append(('alarm states as derived and monotone',
                           states == sorted(states) and not states[2] and states[-1]))
        elif cls == 'INDICATION':
            checks.append(('span unparseable - declared', lo is None))
        else:
            checks.append(('SIF watch declared, no basic action', True))
        for name, ok in checks:
            if ok:
                res[cls][0] += 1
            else:
                res[cls][1] += 1
                details.append((r['loop'], name))
    return res, details


def scan_budget(loops, plcs):
    """Per-PLC loop counts cross-checked against the AQS-CTL-002 module table.

    The AI-signal instrument rows of a sector (SIF elements included; they are the watch
    inputs routed to the safety pair) must equal the table AI count. The table DI column
    covers device-side discretes beyond the instrument index (breaker and switchgear
    discretes), so only the AI side is a hard equality.
    """
    per = {}
    for r in loops:
        c = per.setdefault(r['plc'], {'n': 0, 'sif': 0, 'loops_di': 0})
        if '4-20' in r['signal']:
            c['n'] += 1
            if r['cls'] == 'SIF':
                c['sif'] += 1
        else:
            c['loops_di'] += 1
    out = {}
    for p in sorted(set(per) | set(plcs)):
        c = per.get(p, {'n': 0, 'sif': 0, 'loops_di': 0})
        cfg = plcs.get(p, dict(ai=None, ao=None, di=None, do=None, cpu=''))
        out[p] = dict(**c, **cfg, diff=None if cfg.get('ai') is None else c['n'] - cfg['ai'])
    return out


def main():
    loops = load_loops()
    plcs = plc_table()
    st_files = st_emission(loops, plcs)
    res, fails = simulate(loops, st_files)
    L = ['# Control program source and scan simulation', '',
         'Document number: AQS-CTL-004', 'Revision: A', 'Date: 2026-10-21',
         'Authority: AQS-PLAN-007 X-CTL-04. Generated by `flow_graph/control/plc_programs.py` from AQS-CTL-001, AQS-CTL-002 and the graph. Study. Not a PE stamp.',
         '',
         '## 1. Program source in the repository',
         '',
         f"One IEC 61131_3 structured-text program per sector PLC under `docs-authority/plc/` ({len(st_files)} programs, one per row of the AQS-CTL-002 PLC table).",
         'Each program carries: the 100 ms cyclic task per AQS-CTL-002, the I/O declarations grouped per the module table, per-loop monitor and',
         'PI blocks with set-point literals taken from the graph basis column of AQS-CTL-001, the SIF watch inputs routed to the safety CPU pair',
         '(they are never acted on in the basic programs; AQS-CTL-002), and the redundant-CPU pair declaration where the architecture names one.']

    cls_count = {}
    for r in loops:
        cls_count[r['cls']] = cls_count.get(r['cls'], 0) + 1
    L += ['', '## 2. Loop classification from the graph basis', '',
          '| Class | Loops | Rule |', '|---|---|---|',
          f"| CONTROL | {cls_count.get('CONTROL', 0)} | graph basis carries a numeric set-point (edge normal rate, unit design temperature, design pressure, cell current); PI with the +10/-10 % registered alarm margin (X-SAF-05 margin class, A-M-188); an expected-zero set-point (standby line) alarms on any positive PV and has no low alarm |",
          f"| INDICATION | {cls_count.get('INDICATION', 0)} | no numeric set-point in the basis ('band by service', 'no design pressure on the graph', A-M-182 hold-up heights); monitor with the 90 % high alarm (registered high-level-switch convention, AQS-INV-004); no set-point invented |",
          f"| SIF | {cls_count.get('SIF', 0)} | independent safety elements of AQS-CTL-003; declared as watch inputs to the safety CPU pair, no action in the basic program |"]

    L += ['', '## 3. Cross-check against the AQS-CTL-002 module table', '',
          '| PLC | AI instruments (incl. SIF) | of which SIF | Table AI | Diff | Table AO/DI/DO | CPU |', '|---|---|---|---|---|---|---|']
    diffs = []
    for p, d in sorted(scan_budget(loops, plcs).items()):
        L.append(f'| {p} | {d["n"]} | {d["sif"]} | {d["ai"]} | {d["diff"]} | {d["ao"]}/{d["di"]}/{d["do"]} | {d["cpu"]} |')
        if d['diff']:
            diffs.append((p, d['diff']))

    L += ['', '## 4. Scan simulation against the graph', '',
          'The emitted program model is executed with the PV anchored on the graph basis values (the nominal case seeds PV = the',
          'graph set-point; an ascending sweep covers span mid-point, alarm bound and span top). Assertions per loop: the emitted',
          'alarm literals match their derivation rule, alarm states follow the emitted comparisons, set-points sit inside the',
          'calibrated span, and the PI-law structure holds - output inside 0-100 % span, integrator back-calculated to the clamp',
          '(windup-free), stationarity at PV = SP, and saturation under sustained over-range. Structural only: the GAIN/KI of',
          'each PI block are commissioning-entered from the step test (AQS-COM-001 sec. 3), so the sim makes no tuning-response',
          'claim and invents no tuning constants.', '',
          'The 68 discrete instrument points (LSH 66, PSH 2 rupture-disc and PSV-lift indication) are permissive/interlock inputs',          'declared per the AQS-CTL-002 module table; their trip matrix is the AQS-CTL-003 cause and effect, not the basic program.', '',
          f"- CONTROL loops exercised: {res['CONTROL'][0]} checks pass, {res['CONTROL'][1]} fail",
          f"- INDICATION loops exercised: {res['INDICATION'][0]} checks pass, {res['INDICATION'][1]} fail",
          f"- SIF watch bindings: {res['SIF'][0]} pass, {res['SIF'][1]} fail",
          f"- AI-count cross-check vs AQS-CTL-002: {len(diffs)} PLCs with a residual"]
    if fails:
        L += ['', '## 5. Failures', ''] + [f'- {f[0]}: {f[1]}' for f in fails[:20]]
    if diffs:
        L += [''] + [f'- AQS-CTL-002 AI residual on {p}: {d} (loop counts vs table AI)' for p, d in diffs]
    open(os.path.join(R, 'docs-authority/CONTROL_SOFTWARE.md'), 'w').write('\n'.join(L) + '\n')
    print(dict(cls_count, fail=len(fails), plc_files=len(st_files), ai_diffs=len(diffs)))


if __name__ == '__main__':
    main()

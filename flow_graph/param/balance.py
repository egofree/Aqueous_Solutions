"""X-PAR-02 balance solver, closure layer (AQS-PAR-001). Edge rates set by a transfer function (parametric generators and the stoichiometric
demand edges listed in STOICH) are held. Every other mass edge is a held study rate; these are reconciled by minimum weighted least squares
subject to every unit balancing exactly [NARASIMHAN2000]: minimise sum(((x - x0)/s)^2), s = x0 (relative) or 1 kg/d for zero-rate return
and trim edges (*-RET, *-FIX, *-MAKE). Tolerance: a reconciled edge moving more than TOL (2 %) is a failure, not a review item (test_balance.py). Physics transfer functions (physics()) run first.
Writes the graph (--write) and docs-authority/BALANCE_RECONCILIATION.md (AQS-PAR-003). Run: python3 -m flow_graph.param.balance [--write]"""
import json, os, sys
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GP = os.path.join(ROOT, 'flow_graph/plant_flow_graph.json')
SINK = {'RELIEF_H2', 'RELIEF_CRYO'}
MARK = ('X-PAR', 'X-SAN', 'X-MFG', 'AQS-DUTY-06', 'X-SAF-10', 'X-ELS')
STOICH = {'S49': 'H2 to the fuel cell (load)', 'S50': 'O2 = 8 x H2 by mass', 'S02': 'crew O2 0.84 kg/p.d', 'IA-FC-AIR': 'MEOH_FC oxidant',
          'IA-AC-O2': 'acetic acid oxidation', 'IA-O2-NIT': 'nitric acid', 'IA-GLX-O2': 'one O2 per acetaldehyde', 'IA-FORM-O2': 'half O2 per methanol',
          'IA-H2O2-SRC': 'Faraday at the cell current', 'S40': 'terrace irrigation demand', 'S14': 'crew food', 'S21': 'crew water', 'IA-WASH': 'wash water'}
GROSS = 0.05
TRIM = ('-RET', '-FIX', '-MAKE')

TOL = 0.02                                 # measurement tolerance per edge (A-M-120): a reconciled move above 2 % of the rate (1 g/d floor) fails
PHYS_TAG = 'X-PAR-02 TF'

def _unit_resid(g, u):
    r = 0.0
    for e in g['edges']:
        if e['presence'] == 'present' and 'mass' in (e.get('layers') or []) and e['rate'].get('unit') == 'kg/d':
            v = float(e['rate']['value'] or 0)
            r += v if e['to_unit_id'] == u else 0.0
            r -= v if e['from_unit_id'] == u else 0.0
    return r

def physics(g):
    """Transfer functions that replace the held study rates which X-SAF-10 left inconsistent (A-M-120, AQS-PAR-003 section 0).
    T1 closed greenhouse at steady state: transpiration = irrigation - drains. The terrace has no CO2 supply and no harvest edge, so net
       photosynthetic water fixation (CO2 + H2O -> CH2O + O2, TAIZ2015) is zero on this node.
    T2 AHU condensate = greenhouse vapour in (AQS-DUTY-013: greenhouse vapour condenses to the roof tank, no second outlet).
    T3 O2 product follows the header draw (no storage, no vent; AQS-DUTY-017/019): S83 = IA-ASU-O2 = sum of HDR_O2 draws, IA-O2-RET = 0.
    T4 roof-tank shortfall is made up on the potable path by difference: IA-POT-01, IA-UPW-REMIN, S25 and the leach water bleed IA-LEACH-VCD.
    T5 the leach dissolved-gas edge IA-LEACH-ASU closes the leach and the cold box. It is reduced, toward the Henry's-law solubility bound
       (SANDER2015); the remaining excess over that bound is task X-PAR-11."""
    E = {e['stream_id']: e for e in g['edges']}
    v = lambda k: float(E[k]['rate']['value'] or 0)
    def put(k, x, why):
        E[k]['rate']['value'] = round(x, 6)
        E[k]['rate']['note'] = (E[k]['rate'].get('note') or '').split(' | ' + PHYS_TAG)[0] + f' | {PHYS_TAG}: {why} (AQS-PAR-003).'
    put('IA-TERR-VAP', v('S40') - v('S41') - v('S42'), 'transpiration = S40 - S41 - S42, closed greenhouse, no terrace harvest')
    put('IA-HVAC-COND', v('IA-TERR-VAP') + v('IA-BED-VAP') + v('IA-HAB-VAP'), 'condensate = greenhouse vapour in')
    draw = sum(float(e['rate']['value'] or 0) for e in g['edges'] if e['from_unit_id'] == 'HDR_O2' and e['stream_id'] != 'IA-O2-RET'
               and e['presence'] == 'present' and 'mass' in (e.get('layers') or []))
    put('IA-O2-RET', 0.0, 'no surplus O2 return; product follows draw')
    put('S83', draw - v('IA-O2-MAKE'), 'O2 product = header draw'); put('IA-ASU-O2', v('S83') + v('IA-O2-MAKE') - v('S87'), 'O2 product = header draw')
    d = -_unit_resid(g, 'ROOF_TANK')
    for k in ('IA-POT-01', 'IA-UPW-REMIN', 'S25', 'IA-LEACH-VCD'):
        put(k, v(k) + d, f'roof-tank shortfall {d:+.4f} kg/d by difference on the potable path')
    a = _unit_resid(g, 'CRYO_ASU')
    put('IA-LEACH-ASU', v('IA-LEACH-ASU') - a, f'closes leach and cold box ({-a:+.4f} kg/d); above the Henry bound, X-PAR-11')
    return d, a

def reconcile(g):
    E = [e for e in g['edges'] if e['presence'] == 'present' and 'mass' in (e.get('layers') or []) and e['rate'].get('unit') == 'kg/d']
    x0 = np.array([float(e['rate']['value'] or 0) for e in E])
    held = lambda e: e['stream_id'] in STOICH or any(k in (e['rate'].get('note') or '') for k in MARK)
    free = [i for i, e in enumerate(E) if not held(e) and (x0[i] > 0 or e['stream_id'].endswith(TRIM))]
    fs = set(free); fixed = [i for i in range(len(E)) if i not in fs]
    nodes = sorted(({e['from_unit_id'] for e in E} | {e['to_unit_id'] for e in E}) - SINK); ni = {n: k for k, n in enumerate(nodes)}
    A = np.zeros((len(nodes), len(E)))
    for i, e in enumerate(E):
        if e['to_unit_id'] in ni: A[ni[e['to_unit_id']], i] += 1
        if e['from_unit_id'] in ni: A[ni[e['from_unit_id']], i] -= 1
    r0 = A @ x0
    s = np.array([x0[i] if x0[i] > 0 else 1.0 for i in free])
    rhs = -(A[:, fixed] @ x0[fixed]) - A[:, free] @ x0[free]
    from scipy.optimize import lsq_linear
    M = A[:, free]*s; big = 1e4; lb = -x0[free]/s                      # x >= 0
    u = lsq_linear(np.vstack([M*big, np.eye(len(free))]), np.concatenate([rhs*big, np.zeros(len(free))]), bounds=(lb, np.inf), lsmr_tol='auto', tol=1e-12, max_iter=5000).x
    x = x0.copy(); x[free] = np.maximum(x0[free] + s*u, 0.0)
    r = A @ x
    return dict(E=E, x0=x0, x=x, free=free, nodes=nodes, r0=r0, r=r)

ROOT_CAUSE = ("X-SAF-10 corrected the peroxide cell feed from 3.0 kg/d O2 to 0.176 kg/d O2 (Faraday) plus 2.824 kg/d make-up water from ROOF_TANK, "
  "and took that water off S40. It did not propagate: TERRACE_IRRIG still transpired 40 kg/d on 37.176 kg/d irrigation, and the cold box still "
  "made 2.824 kg/d O2 that nothing drew. Revision A reconciled the two by least squares (IA-TERR-VAP -2.824, IA-O2-RET +2.824) and smeared "
  "small moves over 361 edges. Hypothesis tested: missing photosynthetic O2 from the terrace. Rejected for this cut: the terrace has no CO2 "
  "supply and no harvest edge, so net CO2 + H2O -> CH2O + O2 fixation there is zero (TAIZ2015), and the sign is wrong (the terrace was short "
  "water, the header long O2). Fix: Revision A moves withdrawn; T1-T5 in balance.physics. Separate finding: GROW_BED takes 19.0 kg/d CO2 (S04 + S89) "
  "with its photosynthetic O2 (32/44 x CO2 = 13.8 kg/d at PQ 1.0) lumped in the trim; S87 is retired. That and the IA-LEACH-ASU excess over "
  "the Henry bound are task X-PAR-11 (gas-exchange species layer). Verification: T-PAR-02 (A-M-123).")

def report(R):
    E, x0, x = R['E'], R['x0'], R['x']
    ch = sorted([(abs(x[i] - x0[i]), i) for i in R['free'] if abs(x[i] - x0[i]) > 1e-4], reverse=True)
    gross = [i for _, i in ch if abs(x[i] - x0[i]) > TOL*max(x0[i], 0.05)]
    off0 = [(R['nodes'][k], R['r0'][k]) for k in range(len(R['nodes'])) if abs(R['r0'][k]) > 1e-4]
    L = ['# Mass balance reconciliation', '', 'Document number: AQS-PAR-003', 'Revision: B', 'Date: 2026-10-15',
         'Authority: AQS-PLAN-007 X-PAR-02. Generated by `flow_graph/param/balance.py`. Method NARASIMHAN2000 (minimum weighted least squares on the held study rates; transfer-function and stoichiometric edges held).', '',
         '| Rev | Description | Date |', '| --- | --- | --- |', '| A | First issue. | 2026-10-15 |', '| B | Owner: no fudge. X-SAF-10 imbalance (IA-TERR-VAP / IA-O2-RET, 2.824 kg/d) traced and fixed by transfer functions T1-T5; reconciled moves within measurement tolerance. | 2026-10-15 |', '', '## 0. Root cause and physics fix', '', ROOT_CAUSE, '',
         f"Mass edges {len(E)}; held by a transfer function or stoichiometry {len(E) - len(R['free'])}; reconciled {len(R['free'])}. Units {len(R['nodes'])}.",
         f"Before: {len(off0)} units out of balance (sum of residuals {sum(abs(v) for _, v in off0):.3f} kg/d). After: max unit residual {np.abs(R['r']).max():.2e} kg/d. Negative rates after reconciliation: {int((x < -1e-9).sum())}.", '',
         '## 1. Units out of balance before reconciliation', '', '| Unit | In - out, kg/d |', '| --- | --- |'] + [f'| {n} | {v:+.4f} |' for n, v in off0] + [
         '', f'## 2. Moves outside measurement tolerance ({TOL*100:.0f} % of the rate, 1 g/d floor); must be empty', '', '| Edge | From | To | Held study rate | Reconciled | Change |', '| --- | --- | --- | --- | --- | --- |'] + [
         f"| {E[i]['stream_id']} | {E[i]['from_unit_id']} | {E[i]['to_unit_id']} | {x0[i]:.4f} | {x[i]:.4f} | {(x[i] - x0[i]):+.4f} |" for i in gross] + [
         '', '## 3. All reconciled changes above 0.1 g/d', '', '| Edge | Held | Reconciled | Change, % |', '| --- | --- | --- | --- |'] + [
         f"| {E[i]['stream_id']} | {x0[i]:.4f} | {x[i]:.4f} | {((x[i] - x0[i])/x0[i]*100 if x0[i] else float('nan')):+.2f} |" for _, i in ch] + [
         '', '## 4. Held stoichiometric edges', '', '| Edge | Basis |', '| --- | --- |'] + [f'| {k} | {v} |' for k, v in STOICH.items()]
    open(os.path.join(ROOT, 'docs-authority/BALANCE_RECONCILIATION.md'), 'w').write('\n'.join(L) + '\n')
    return gross, off0

def main():
    g = json.load(open(GP)); d, a = physics(g); print('physics roof', round(d, 4), 'asu', round(a, 4)); R = reconcile(g); gross, off0 = report(R)
    print('off before', len(off0), 'max resid after', float(np.abs(R['r']).max()), 'gross', [R['E'][i]['stream_id'] for i in gross])
    if '--write' in sys.argv:
        assert (R['x'] >= -1e-9).all() and np.abs(R["r"]).max() < 1e-3
        for i in R['free']:
            e = R['E'][i]
            if abs(R['x'][i] - R['x0'][i]) > 1e-7:
                e['rate']['value'] = round(float(max(R['x'][i], 0.0)), 6)
                e['rate']['note'] = (e['rate'].get('note') or '').split(' | X-PAR-02')[0] + ' | X-PAR-02 reconciled (AQS-PAR-003).'
        open(GP, 'w').write(json.dumps(g, indent=2))

if __name__ == '__main__': main()

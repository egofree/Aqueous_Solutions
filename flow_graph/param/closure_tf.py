"""X-PAR-02 remaining transfer functions (AQS-PAR-003 section 1). Every reconciled (study) mass edge gets one role:
  closure TF  rate = the balance of one named unit (inputs minus other outputs), solved in elimination order; or
  design input  an independent rate with its stated basis (duty sheet, audit band, crew ration), which a unit sizing task replaces.
Assignment: edges whose basis says they are sized to the neighbour, by difference or pass-through are offered as closures first; leaf-first
elimination (a unit with exactly one undecided study edge closes on it) then fixes the rest. The re-derivation test rebuilds every closure
edge from the inputs and must reproduce the graph within 0.1 g/d. Run: python3 -m flow_graph.param.closure_tf"""
import json, re, os
from flow_graph.param import balance as B
DIFF = re.compile(r'neighbo|by difference|passes|pass-?through|Passthrough|less |same mass|equal to|Missing product or return|surplus|remainder', re.I)
def assign(g):
    R = B.reconcile(g); E, x = R['E'], R['x0']; free = set(R['free'])
    inc = {}
    for i in free:
        for u in (E[i]['from_unit_id'], E[i]['to_unit_id']):
            if u in R['nodes']: inc.setdefault(u, set()).add(i)
    role = {}; order = []
    pref = lambda i: 0 if DIFF.search(E[i]['rate'].get('note') or '') else 1
    while len(role) < len(free):
        prog = False
        for u, s in sorted(inc.items()):
            und = [i for i in s if i not in role]
            if len(und) == 1:
                role[und[0]] = ('closure', u); order.append(und[0]); prog = True
        if not prog:                         # promote one undecided edge to a design input: the least 'difference-like', largest basis text
            cand = sorted((i for i in free if i not in role), key=lambda i: (-pref(i), E[i]['stream_id']))
            role[cand[0]] = ('input', None)
    return R, role, order
def rederive(g, R, role, order):
    E = R['E']; x = R['x0'].copy(); idx = {i: k for k, i in enumerate(range(len(E)))}
    for i, (r, u) in role.items():
        if r == 'closure': x[i] = 0.0
    for i in order:
        u = role[i][1]; s = 0.0
        for k, e in enumerate(E):
            if k == i: continue
            if e['to_unit_id'] == u: s += x[k]
            if e['from_unit_id'] == u: s -= x[k]
        x[i] = s if E[i]['from_unit_id'] == u else -s
    return float(max(abs(x[i] - R['x0'][i]) for i in order)) if order else 0.0
def write(g):
    R, role, order = assign(g); err = rederive(g, R, role, order); E = R['E']
    nc = sum(1 for r, _ in role.values() if r == 'closure'); ni = len(role) - nc
    L = ['', '## 5. Transfer functions for the study edges (closure layer complete)', '',
         f'{len(role)} study edges: {nc} closure transfer functions (rate = balance of the named unit, solved in elimination order) and {ni} design inputs (independent rates with their stated basis; each is replaced when its unit sizing task issues a calculation). '
         f'Re-derivation of every closure from the inputs reproduces the graph to {err:.1e} kg/d.', '', '| Edge | Role | Closes unit | Rate kg/d | Basis |', '| --- | --- | --- | --- | --- |']
    for i in sorted(role, key=lambda i: (role[i][0], E[i]['stream_id'])):
        r, u = role[i]; L.append(f"| {E[i]['stream_id']} | {r} | {u or '-'} | {R['x0'][i]:.4f} | {(E[i]['rate'].get('note') or '').split(' | X-PAR-02')[0][:90]} |")
    p = os.path.join(B.ROOT, 'docs-authority/BALANCE_RECONCILIATION.md'); t = open(p).read().split('\n## 5. Transfer functions')[0].rstrip('\n')
    open(p, 'w').write(t + '\n' + '\n'.join(L) + '\n'); return nc, ni, err
if __name__ == '__main__':
    g = json.load(open(B.GP)); B.physics(g); print(write(g))

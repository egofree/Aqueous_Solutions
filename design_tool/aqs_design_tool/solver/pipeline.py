# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Pipeline solve: run the REAL balance stage on the sandbox-folded graph (X-UI-002 Phase 1).

The sandbox never invents closure: this module folds the live graph with the sandbox's
unit-enabled semantics, runs the actual X-PAR-02 physics + least-squares reconcile from
``flow_graph.param.balance``, and reports the true node residuals. Every number here is
the pipeline's own; a residual is reported, never smoothed away.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from flow_graph.param.balance import physics, reconcile  # noqa: E402
from aqs_design_tool.paths import FLOW_GRAPH_JSON  # noqa: E402


def solve_mass(mvs_units: list[dict], sandbox_id: str | None = None) -> dict[str, Any]:
    """Fold the live graph with the sandbox's disabled units, run the real balance.

    Returns ``{'status', 'residuals': {'mass': [ResidualItem dicts]}, 'nodes_solved',
    'max_residual', 'note'}``.
    """
    g = json.loads(FLOW_GRAPH_JSON.read_text())
    g0 = copy.deepcopy(g)
    disabled = {u['unit_id'] for u in mvs_units if not u.get('enabled', True)}
    if disabled:
        g['nodes'] = [n for n in g['nodes'] if n['unit_id'] not in disabled]
        gone = set(disabled)
        g['edges'] = [e for e in g['edges']
                      if e['from_unit_id'] not in gone and e['to_unit_id'] not in gone]
    # The X-PAR-02 physics TFs are baseline-bound: a fold that removed edges (a leo fold
    # has no ZNBR2 line for T-functions to write) breaks them. Policy: run the full
    # physics pass when the fold survives it; otherwise roll back to the pre-physics
    # graph and reconcile alone, stating the limitation. The baseline and the Earth-site
    # folds (nothing removed) therefore get the full pipeline behaviour.
    tf_note = 'full physics pass'
    try:
        physics(g)
    except (KeyError, AssertionError):
        g = copy.deepcopy(g0)
        tf_note = ('physics TF pass skipped: the fold lacks baseline edges the TFs write; '
                   'reconciliation runs on held study rates alone')
    R = reconcile(g)
    max_resid = float(max(abs(R['r'])) ) if len(R['r']) else 0.0
    items = []
    for k, n in enumerate(R['nodes']):
        r = float(R['r'][k])
        if abs(r) > 1e-3:
            items.append({'id': n, 'kind': 'node mass balance', 'residual': round(r, 6),
                          'unit': 'kg/d', 'status': 'incomplete',
                          'detail': 'held study rates the free edges could not reconcile inside tolerance'})
    # a node on a SINK boundary reports in != out by design (losses, exports): not a gap
    status = 'ok' if max_resid < 1e-3 else 'partial'
    return {'status': status, 'residuals': {'mass': items}, 'nodes_solved': len(R['nodes']),
            'max_residual': round(max_resid, 6), 'sandbox_id': sandbox_id,
            'tf_note': tf_note, 'disabled': len(disabled),
            'note': ('X-PAR-02 least squares on the sandbox fold; boundary sinks are exempt '
                     'by design (NORTH_DOCK trade, ATMOS evaporation, exports). ' + tf_note +
                     f'. {len(disabled)} units disabled: the fold can mass-close as a balanced '
                     'subset while carrying FEWER FUNCTIONS - the functional-gap analysis is the '
                     'stub solve jurisdiction (GET /flags).')}


def _graph_path() -> Path:
    return _REPO / 'flow_graph' / 'plant_flow_graph.json'

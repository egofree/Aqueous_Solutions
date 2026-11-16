"""The dock-class family (family migration; reference writer
flow_graph/param/recovery.py command `--stamp`, ledger row `dock_class`,
section B, MIXED: split the recovery solve -> this function, the task-plan
gate -> dies as bookkeeping).

The recovery-first inventory (owner decision t61u, A-M-476): for every element
the plant needs, recover it first from waste and byproduct streams anywhere on
the graph; raw ore at the dock is only a top-up for the shortfall left after
recovery. The classification rule (F-20261110-07: the class is a field, not
text) stamps every live dock input with an explicit params.dock_class - raw_ore
(a listed mineral), water (a water make-up), waste (a received waste stream) or
pending (an import the recovery-first program has not replaced yet, naming the
task that retires it) - so the recovery gate cannot be dodged by a hand-added
or seed-grown input. The reference writer restamps the classes of the named
tables every pass; the committed graph carries exactly those fields (eight live
dock inputs, all classified). That committed state is the golden this module
reproduces.

The class tables port as data: the ORE mineral table (element, mineral formula,
ore-purity driver; None where the stream rates as the pure mineral), the water
make-ups, and the waste and pending tables. X-QA-11 (2026-11-15) emptied the
pending table the way X-QA-19 retired the AlCl3 import - by sizing the on-site
route, not by exemption (A-M-495 aluminium, A-M-496 brine, A-M-497 nitrate,
A-M-498 wax, A-M-499 raw-feed class, A-M-501 grit, A-M-502 finish) - and the
waste table stands empty with it. A dock input outside every table stamps None,
which the recovery gate flags.

DISPOSITION OF THE REST OF THE STAGE:
- The params.recovery RECORDS (the per-unit need/recovered/ore/unrecovered
  books the recovery-first ore top-up consumes) are each transfer function's
  own stamps, not this stage's write: the foundry family ports the foundry and
  polymers records (SHELL_BUILD, TI_CELL, MO_CELL, CR_CELL, HOPPER, with the
  AW and ORE tables), the si_route family ports the silicon-loop records
  (SI_REDUCE, SI_REFINE). The remaining committed records belong to families
  that have not landed (HF_GEN to fluoro_train, GREASE_CA/P_CA to the grease
  lanes, NAOH_PLANT to caustic, SOLV_PLANT to the solvent family, ACID_PLANT
  to the acid lane, RESIST_SYN to the fab-resist lane); the test carries the
  ownership table. This module ports the classification stamp only.
- The TASK_PLAN.md done-checkbox parsing (the closed-task gate on pending
  imports) dies as bookkeeping: the pending table is empty and the gate read a
  generated task board, not the graph.
- The inventory flags (uncovered ore, ore over shortfall, undeclared losses)
  are the recovery gate's checks - v1's test_recovery_first.py holds them
  until the checker lane migrates; they stamp nothing.

The dock input census reads only the seed (presence, layers, rate unit and
value), so this family records regardless of the payload - the seed-only
bridge class, like the pot-cell geometry family.
"""
import re

from flow_graph.v2.registry import fn

STAGE = 'dock_class'                                           # ledger row, section B
# dock raw-ore streams: element, mineral formula, ore-purity driver (None: the
# stream is rated as the pure mineral) - the reference writer's ORE table.
ORE = {'IA-CAF2-MU': ('F', 'CaF2', 'POLYMERS.fluoropolymer-train.fluorspar_CaF2_wt'),
       'IA-TIO2-MU': ('Ti', 'TiO2', None), 'IA-MOO3-MU': ('Mo', 'MoO3', None),
       'IA-CR2O3-MU': ('Cr', 'Cr2O3', None), 'IA-QUARTZ-MU': ('Si', 'SiO2', None),
       'IA-SILICA-MU': ('Si', 'SiO2', None), 'IA-SULFUR-MU': ('S', 'S', None),
       'IA-TRONA-MU': ('Na', 'Na2CO3.NaHCO3.2H2O', 'trona_ore_purity'),
       'IA-HALITE-MU': ('Na', 'NaCl', 'halite_ore_purity'),
       'IA-LIMESTONE-MU': ('Ca', 'CaCO3', 'limestone_ore_purity'),
       'IA-FEED-MU': ('Fe', 'Fe', 'feed_fe_assay_frac')}       # X-QA-11, A-M-499: the characterized-lot make-up IS the raw feed
WASTE_IN = {}                                                  # received waste streams: none at the design basis (A-M-284)
WATER_IN = {'IA-H2O-MU'}                                       # water make-ups at the dock boundary
PENDING = {}                                                   # X-QA-11 emptied the table: every dock input is
                                                               # water, waste or a covered raw ore (A-M-495..502)
DOCK = 'NORTH_DOCK'
LIVE_RATE_RE = re.compile(r'^kg/d$')


def _live(e):
    """A live dock input: present edge, mass layer, kg/d rate, positive value
    (the reference writer's _live predicate)."""
    rate = e.get('rate') or {}
    return e.get('presence') != 'retired' and 'mass' in (e.get('layers') or []) \
        and LIVE_RATE_RE.match(str(rate.get('unit') or '')) and isinstance(rate.get('value'), (int, float)) \
        and rate.get('value') > 0


def classify(sid):
    """The dock class of a stream id from the tables, or None (which the
    recovery gate flags)."""
    if sid in ORE:
        return 'raw_ore'
    if sid in WASTE_IN:
        return 'waste'
    if sid in PENDING:
        return 'pending'
    if sid in WATER_IN:
        return 'water'
    return None


def _prov(basis, ref=None):
    from flow_graph.v2.model import Prov
    return Prov(STAGE, basis, ref)


@fn('dock_class', 'the recovery-first dock classification (owner decision t61u, A-M-476; F-20261110-07: the '
    'class is a field, not text): every live dock input stamps params.dock_class from the ORE/WATER/WASTE/PENDING '
    'tables - raw_ore, water, waste or pending (with the task that retires it); X-QA-11 emptied the pending table '
    'by sizing the on-site routes (A-M-495..502)')
def dock_class(b, inputs):
    """The recovery solve's stamp half: restamp the explicit dock class on
    every live dock input so a hand-added or seed-grown input cannot dodge the
    gate; leave every other field alone."""
    basis = ('the recovery-first dock classification (F-20261110-07): the class is a field on the edge, restamped '
             'from the reference tables every pass; raw ore is the A-M-476 top-up rule, water is a water make-up, '
             'pending names the task that retires the import')
    for e in b.data['edges']:
        if e.get('from_unit_id') != DOCK or not _live(e):
            continue
        sid = e['stream_id']
        cls = classify(sid)
        fields = {('edge', sid, 'params.dock_class'): (cls, _prov(basis))}
        if cls == 'pending':
            fields[('edge', sid, 'params.dock_pending_task')] = (PENDING[sid][0], _prov(basis))
        for key, (value, prov) in fields.items():
            b.computed[key] = (value, prov)

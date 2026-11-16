"""engine v2: the graph-shape mutations as pure, data-conditioned functions.

The model is a value; the topology changes are functions of the data. Every
mutation here is keyed to the DATA CONDITION that governs it - an edge or node
absent or present in the graph, an endpoint's presence, a driver's sign - never
to a locale id string (the site_scale/site_power_placement pattern: the
portfolio source names and the profile entries decide, no sid appears in this
module). The functions mutate the builder's parsed structure in place and
record NOTHING in the computed overlay: shape carries no provenance rows, the
values do.

Composition order (declared in solve.py, which imports this module FIRST -
the shape precedes the values): topology runs before every value family. The
boundary with the arithmetic already landed in the family modules is
"topology first, then arithmetic". The families read the POST-mutation shape:
the foundry family's value-only brine re-rate reads b.edges[sid]['rate'] on
the edges this module creates, its seed-topology asserts read the retired
presences this module books, si_route's asserts read the SI_REFINE node and
the deleted IA-SI-IMPORT this module provides, and the heat family asserts
the IA-DC-REJ edge this module clones when absent. A family run without this
module crashes loudly on a pre-mutation seed; with it, the shape is a
precondition the families may rely on.

The bridge reality: the committed seed ALREADY carries the consolidated
topology - every create-if-missing finds its edge present, every retire finds
it retired, every seed param finds itself seeded - so on the committed seed
these functions are byte-identical no-ops (test_topology.py proves both
directions: idempotent on the committed seed, restorative on a tampered seed
where the physics families re-run after the shape pass).

The mutation inventory (ported from the reference writers; the per-family
golden-value proofs pin the same inventories as structured data in
test_foundry.py and test_si_route.py):

- foundry_apply: the foundry family's creates (the 31 mass edges incl.
  IA-KROLL-CO and IA-SHELL-EXPORT, the 6 SF pot feeds, the 6 crew-textile
  edges when the spin line's POLY_FIBER node is in the graph, the BRINE_CRYS
  node + its 4 streams + SF-BRINE_CRYS where the leach and the pots run,
  AQS-SITE-010), the retirements of the replaced dock imports when present
  (with the retired carries wording and the dock-class pops the writer
  applies), the IA-WAX-CUT sector re-point and the seeded edge params the
  arithmetic reads back. The family's ARITHMETIC is functions/foundry.py;
  this module is only the shape its report inventoried.
- si_route_topology: the si_route family's create-or-rate half on the 24 fab
  and route streams and the 2 SF feeds (the rate half is
  functions/si_route.py), the SI_REFINE node creation when a seed predates
  the route, and the IA-SI-IMPORT retirement - v1 retired it when present;
  the committed tree carries the owner-decision t58u deletion outright, so
  the shape function deletes it and a seed carrying the import converges to
  the committed shape.
- heat_relief_topology: the IA-DC-REJ clone-if-absent (heat docstring:
  "edge topology ... is builder work") - a deep copy of the HL-Q4-REJ
  terminal edge re-pointed to the dry cooler, created only when the terminal
  edge and the DRY_COOLER unit exist. The v1 relief and vent commands
  themselves perform no graph-shape mutation (verified: their writers stamp
  node params only); the only clone in the heat -> relief -> vent chain is
  this one, and it is the relief chain's terminal shape.
- locale designed-source placements (FSP_40K / MMRTG): verified NO-OP.
  The v1 placement writer is "idempotent; no topology change"
  (flow_graph/param/site_units.py apply()); the placeholder units' presence
  transitions (placeholder -> present) are locale-worktree seed state, not a
  stage mutation, and the v2 site family's sizers already handle presence as
  a read (site_power_placement gates on the placeholder presence and stamps
  params.site_placement only - no presence stamp exists to port). Nothing
  here touches those nodes.

Insertion positions: the created edges and nodes carry an ANCHOR - the
committed shape's successor - and are inserted immediately before it (first
present anchor wins, else appended). On the committed seed nothing is
inserted; on a tampered seed the anchor restores the committed list position,
so the pipeline render is byte-identical in both directions. Sector fields
are derived from the endpoint nodes (the edge_sectors invariant: the copied
node sector is a graph invariant in v2, not a stage).

Grid doctrine: no float literals (the lint holds this). The template books
carry the committed JSON doubles as exact fractions - float(Fraction) is the
exact double of the decimal the committed file carries. Every created edge's
rate template books the committed rate verbatim (SEED_RATES, the integer
count on its write grid): the value families that re-stamp the rate in full
overwrite it, and the ones that READ seed rates back (the foundry float
books, the hab/shop conversions, the SI furnace feed) read the committed
book, so a tampered seed converges in one pass. Rate NOTES and param books
ride only where no family re-stamps them yet: the three brine streams and
IA-CA-CL2-SHIP are value-only updates in the foundry family (the notes are
the balance reconciler's and the photoresist netting's, AQS-PAR-003 /
A-M-482, neither landed; the si_cl2_kg_d param book is the A-M-484 seed
read) and IA-KROLL-CO is re-rated by the solvent family (A-M-479, not
landed). Everything else is re-stamped in full by its family after this
module runs.

Pure: no I/O, no wall-clock, no RNG, no float literals.
"""
import copy
from fractions import Fraction

from flow_graph.v2.registry import fn


def _f(num, den=1):
    """The exact JSON double of num/den (no float literal; the value is the
    committed decimal)."""
    return float(Fraction(num, den))


MG = 10 ** 6                                                  # the mg book of the kg/d schema
ONE = _f(MG, MG)                                              # the template composition value 1.0

# The creation rate books: every created edge's template books the committed
# rate verbatim (integer count on its write grid). The value families that
# re-stamp the rate in full overwrite it; the ones that READ seed rates back
# (the foundry float books, the hab/shop conversions, the SI furnace feed)
# read the committed book, so a tampered seed converges in one pass. The
# notes ride only where no family re-stamps them yet (see the module
# docstring): the brine three, IA-CA-CL2-SHIP (CA_SHIP_RATE below) and
# IA-KROLL-CO (KROLL_CO_RATE below).
SEED_RATES = {
    'IA-ALCL3-MU': (0, 1), 'IA-AL-CAKE': (14842429, MG), 'CHAR_TO_AL': (3428153, MG),
    'IA-AL-CO': (7994666, MG), 'IA-AL-H2O': (5141916, MG), 'IA-MGCL2-KROLL': (1949292, MG),
    'IA-KROLL-FLUX': (39781, MG), 'IA-MGCL2-MU': (0, 1), 'IA-MG-TI': (507761, MG),
    'IA-CL2-MG-TI': (1481313, MG), 'IA-CACL2-MU': (0, 1), 'IA-CA-CL2-SHIP': (63248, MG),
    'IA-TIO2-MU': (834247, MG), 'CHAR_TO_TI': (250924, MG), 'IA-KROLL-CO': (45835, 10 ** 5),
    'IA-MOO3-MU': (93766, MG), 'CHAR_TO_MO': (11736, MG), 'IA-MO-VENT': (43002, MG),
    'IA-CR2O3-MU': (365389, MG), 'CHAR_TO_CR': (86624, MG), 'IA-CR-VENT': (202013, MG),
    'IA-WAX-MU': (0, 1), 'IA-WAX-CUT': (2, 10), 'IA-SILICA-MU': (0, 1),
    'IA-SIL-SHOP': (1, 1), 'IA-BURNOUT-VENT': (2, 10), 'IA-SHELL-RECLAIM': (7, 1),
    'IA-SHELL-SHOP': (1, 1), 'IA-SHELL-EXPORT': (0, 1), 'IA-C5-POLY': (352672, MG),
    'IA-METAL-SHIP': (59465, 10 ** 4),
    'SF-AL_POT': (29567, 10 ** 4), 'SF-MG_POT': (3375, 10 ** 4), 'SF-CA_POT': (1184, 10 ** 4),
    'SF-TI_CELL': (5, 10), 'SF-MO_CELL': (1141, 10 ** 4), 'SF-CR_CELL': (16, 100),
    'IA-BRINE-SRC': (2000047, MG), 'IA-BRINE-CACL2': (116201, MG), 'IA-BRINE-MGCL2': (39782, MG),
    'IA-BRINE-ML': (1844063, MG), 'SF-BRINE_CRYS': (7, 100),
    'IA-FR-P': (1276, MG), 'IA-FR-NH3': (443, MG), 'FIBER_SCRAP': (4524, MG),
    'FLEECE_TO_MFG': (87671, MG), 'TEXTILE_HAB': (87671, MG), 'STOCK_TO_FIBER': (90476, MG),
    'IA-FAB-WAFER': (138904, MG), 'IA-LITHO-WAFER-A': (138904, MG), 'IA-LITHO-WAFER-B': (138904, MG),
    'IA-LITHO-WAFER-RET': (138904, MG), 'IA-FAB-PRODUCT': (138904, MG), 'IA-FAB-KERF': (43592, MG),
    'IA-FAB-KERF-REC': (392324, MG), 'IA-FAB-SCRAP': (431011, MG), 'IA-PV-WAFER': (408673, MG),
    'IA-PV-CELL': (408673, MG), 'IA-AR-CZ': (3348249, MG), 'IA-AR-CZ-BACK': (3348249, MG),
    'IA-QUARTZ-MU': (0, 1), 'IA-SI-BRIQ': (438274, MG), 'IA-SI-HOOD-O2': (231203, MG),
    'IA-SI-CO2': (635978, MG), 'IA-SI-FUME': (0, 1), 'IA-SI-MG': (207071, MG),
    'IA-CL2-SIREF': (9111, MG), 'IA-SI-PURGE': (33686, MG), 'IA-PV-EOL': (408673, MG),
    'IA-SI-EG': (983493, MG), 'SF-SI_REDUCE': (1122, 10 ** 4), 'SF-SI_REFINE': (24587, 10 ** 4),
    'STOCK_TO_FAB': (1414504, MG), 'CHAR_TO_SI': (173572, MG),
}


def _rate(sid, unit='kg/d'):
    """The committed rate book of a created edge, as the template dict."""
    num, den = SEED_RATES[sid]
    return {'value': _f(num, den), 'unit': unit, 'status': 'study', 'note': ''}


KW_D = {'value': _f(0), 'unit': 'kW', 'status': 'study', 'note': ''}

# the two separation books the created edges carry (the o2_close _edge
# template book and the older foundry creates' normalized book)
O2_SEP = ('HDR_O2, HDR_CO2', 'Claimed / Partial')
CLOSED_SEP = ('process aisle', 'Closed')

# the insertion anchors: each created edge goes immediately before its
# committed-shape successor; the stable non-created edge at the block edge is
# the fallback (first present anchor wins, else the edge appends).
A_SHELL_GRIT = ('SHELL_GRIT',)
A_SI_TAIL = ('IA-AL-CAKE',) + A_SHELL_GRIT

# ---- the foundry family's creates: the 31 mass edges (X-PAR-02 TF foundry) --
# (sid, from, to, phase, layers, carries, notes, comp, separation, anchors).
FOUNDRY_MASS = (
    ('IA-ALCL3-MU', 'NORTH_DOCK', 'AL_POT', 'S', ('mass',),
     'anhydrous AlCl3 top-up feed (retired dock import)', None, None, CLOSED_SEP,
     ('IA-CL2-SHIP', 'SHELL_GRIT')),
    ('IA-AL-CAKE', 'LEACH_CSTR_1', 'AL_POT', 'S', ('mass',),
     'recovered reactive-Al hydroxide cake to the aluminium line', None, None, CLOSED_SEP,
     ('CHAR_TO_AL', 'SHELL_GRIT')),
    ('CHAR_TO_AL', 'OIL_PYRO', 'AL_POT', 'S', ('mass',),
     'plant pyrolysis char reductant for the alumina chlorination', None, None, CLOSED_SEP,
     ('IA-AL-CO', 'SHELL_GRIT')),
    ('IA-AL-CO', 'AL_POT', 'NORTH_DOCK', 'G', ('mass',),
     'chlorinator CO (fuel-gas class export)', None, None, CLOSED_SEP,
     ('IA-AL-H2O', 'SHELL_GRIT')),
    ('IA-AL-H2O', 'AL_POT', 'ATMOS', 'G', ('mass',),
     'calcination steam of the hydroxide cake', None, None, CLOSED_SEP,
     ('CHAR_TO_TI', 'SHELL_GRIT')),
    ('IA-MGCL2-KROLL', 'TI_CELL', 'MG_POT', 'L', ('mass',),
     'Kroll retort MgCl2 return (net of drag-out)', None, None, CLOSED_SEP,
     ('IA-KROLL-FLUX', 'SHELL_GRIT')),
    ('IA-KROLL-FLUX', 'TI_CELL', 'FLUX_PREP', 'S', ('mass',),
     'MgCl2-class salt drag-out (flux cover source)', None, None, CLOSED_SEP,
     ('IA-MGCL2-MU', 'SHELL_GRIT')),
    ('IA-MGCL2-MU', 'NORTH_DOCK', 'MG_POT', 'L', ('mass',),
     'CaCl2-MgCl2 brine concentrate (retired dock import)', None, None, CLOSED_SEP,
     ('IA-MG-TI', 'SHELL_GRIT')),
    ('IA-MG-TI', 'MG_POT', 'TI_CELL', 'S', ('mass',),
     'Mg reductant to the Kroll retort', None, None, CLOSED_SEP,
     ('IA-CL2-MG-TI', 'SHELL_GRIT')),
    ('IA-CL2-MG-TI', 'MG_POT', 'TI_CELL', 'G', ('mass',),
     'chlorine to the Kroll chlorinator', None, None, CLOSED_SEP,
     ('IA-CACL2-MU', 'SHELL_GRIT')),
    ('IA-CACL2-MU', 'NORTH_DOCK', 'CA_POT', 'L', ('mass',),
     'CaCl2 brine concentrate (retired dock import)', None, None, CLOSED_SEP,
     ('IA-CA-CL2-SHIP', 'SHELL_GRIT')),
    ('IA-CA-CL2-SHIP', 'CA_POT', 'NORTH_DOCK', 'G', ('mass', 'energy'),
     'chlorine byproduct export (water-treatment class)', None, None, CLOSED_SEP,
     ('IA-TIO2-MU', 'SHELL_GRIT')),
    ('IA-TIO2-MU', 'NORTH_DOCK', 'TI_CELL', 'S', ('mass',),
     'TiO2-equivalent rutile concentrate (dock import class)', None, None, CLOSED_SEP,
     ('IA-C-TI', 'SHELL_GRIT')),
    ('CHAR_TO_TI', 'OIL_PYRO', 'TI_CELL', 'S', ('mass',),
     'plant pyrolysis char reductant', None, None, CLOSED_SEP,
     ('CHAR_TO_MO', 'SHELL_GRIT')),
    ('IA-KROLL-CO', 'TI_CELL', 'NORTH_DOCK', 'G', ('mass',),
     'chlorinator CO (fuel-gas class export)', None, None, CLOSED_SEP,
     ('IA-MOO3-MU', 'SHELL_GRIT')),
    ('IA-MOO3-MU', 'NORTH_DOCK', 'MO_CELL', 'S', ('mass',),
     'MoO3-equivalent concentrate (dock import class)', None, None, CLOSED_SEP,
     ('IA-C-MO', 'SHELL_GRIT')),
    ('CHAR_TO_MO', 'OIL_PYRO', 'MO_CELL', 'S', ('mass',),
     'plant pyrolysis char reductant', None, None, CLOSED_SEP,
     ('CHAR_TO_CR', 'SHELL_GRIT')),
    ('IA-MO-VENT', 'MO_CELL', 'NORTH_DOCK', 'G', ('mass',),
     'chlorinator CO2 (vent class)', None, None, CLOSED_SEP,
     ('IA-CR2O3-MU', 'SHELL_GRIT')),
    ('IA-CR2O3-MU', 'NORTH_DOCK', 'CR_CELL', 'S', ('mass',),
     'Cr2O3-equivalent chromite concentrate (dock import class)', None, None, CLOSED_SEP,
     ('IA-C-CR', 'SHELL_GRIT')),
    ('CHAR_TO_CR', 'OIL_PYRO', 'CR_CELL', 'S', ('mass',),
     'plant pyrolysis char reductant', None, None, CLOSED_SEP,
     ('IA-SIL-SHOP', 'SHELL_GRIT')),
    ('IA-CR-VENT', 'CR_CELL', 'NORTH_DOCK', 'G', ('mass',),
     'chlorinator CO (fuel-gas class export)', None, None, CLOSED_SEP,
     ('IA-WAX-MU', 'SHELL_GRIT')),
    ('IA-WAX-MU', 'NORTH_DOCK', 'WAX_PATTERN', 'S', ('mass',),
     'pattern wax make-up (retired dock import)', None, None, CLOSED_SEP,
     ('IA-SILICA-MU', 'SHELL_GRIT')),
    ('IA-WAX-CUT', 'PROD_C19_C28', 'WAX_PATTERN', 'S', ('mass',),
     'C19-C28 pattern-wax blend make-up from the plant cut', None, {'C19-C28': ONE}, CLOSED_SEP,
     ('IA-NUT-NH3', 'SHELL_GRIT')),
    ('IA-SILICA-MU', 'NORTH_DOCK', 'SHELL_BUILD', 'S', ('mass',),
     'foundry silica (flour/stucco/binder make-up)', None, None, CLOSED_SEP,
     ('IA-BURNOUT-VENT', 'SHELL_GRIT')),
    ('IA-SIL-SHOP', 'MFG_SHOP', 'SHELL_BUILD', 'S', ('mass',),
     'recovered crib and spent-shell silica, shell make-up', None, None, CLOSED_SEP,
     ('IA-SHELL-SHOP', 'SHELL_GRIT')),
    ('IA-BURNOUT-VENT', 'SHELL_BURNOUT', 'NORTH_DOCK', 'G', ('mass',),
     'dewax/burnout off-gas (burned wax + steam)', None, None, CLOSED_SEP,
     ('IA-SHELL-RECLAIM', 'SHELL_GRIT')),
    ('IA-SHELL-RECLAIM', 'SHELL_BREAK', 'SHELL_BUILD', 'S', ('mass',),
     'reclaimed shell stucco/flour', None, None, CLOSED_SEP,
     ('IA-SHELL-EXPORT', 'SHELL_GRIT')),
    ('IA-SHELL-SHOP', 'SHELL_BREAK', 'MFG_SHOP', 'S', ('mass',),
     'recovered spent-shell silica to the shop pool', None, None, CLOSED_SEP,
     ('IA-BRINE-SRC', 'SHELL_GRIT')),
    ('IA-SHELL-EXPORT', 'SHELL_BREAK', 'NORTH_DOCK', 'S', ('mass',),
     'spent foundry silica (solids return class)', None, {'SiO2': ONE}, CLOSED_SEP,
     ('SF-AL_POT', 'SHELL_GRIT')),
    ('IA-C5-POLY', 'PROD_C5_C10', 'POLY_OLEFIN', 'L', ('mass',),
     'C5-C10 naphtha olefin feed',
     'Created by the polymers sizing pass: the olefin feed draws as naphtha at the cut tank '
     '(AQS-SIZE-OIL-POLY); the fractionator-side OIL_TO_OLEFIN stays 0 so OIL_FRAC closes.',
     {'C5-C10': ONE}, O2_SEP, ('SQ-EVAP_ACID',)),
    ('IA-METAL-SHIP', 'METAL_STORE', 'NORTH_DOCK', 'S', ('mass',),
     'surplus foundry metal export (pot-line product, dispatch campaign)',
     "Created by the foundry sizing pass: the pot/cell metal is the stock loop's only net inlet, "
     'so at steady state the loop passes it and the full pot output leaves as the dock metal '
     'export (A-M-284).',
     {'O2': _f(99, 100), 'Ar': _f(1, 100)}, O2_SEP, ('SF-MET_MELT',)),
)
# The created imports that keep their dock-class books (the others' dock
# classes are popped at retirement; the writer never popped these)
CREATE_PARAMS = {'IA-ALCL3-MU': {'dock_class': 'pending', 'dock_pending_task': 'X-QA-19'},
                 'IA-TIO2-MU': {'dock_class': 'raw_ore'},
                 'IA-MOO3-MU': {'dock_class': 'raw_ore'},
                 'IA-CR2O3-MU': {'dock_class': 'raw_ore'}}
# IA-CA-CL2-SHIP is a value-only update in the foundry family (the photoresist
# netting co-authors the note, A-M-482) and its params.si_cl2_kg_d book is the
# foundry seed read (A-M-484, the si_route make-up the export is net of): the
# creation template books both verbatim (the committed v1 float book).
CA_SHIP_RATE = {'value': _f(63248, MG), 'unit': 'kg/d', 'status': 'study',
                'note': 'CA_POT Cl2 byproduct 1.769 kg/kg Ca, less the 0.0091 kg/d silicon-loop make-up on '
                        'IA-CL2-SIREF (A-M-472; the AL_POT chlorine closes on the cake chlorination, A-M-495, '
                        'so the CA_POT share carries the dock chlorine export), exports at the dock (A-M-290 '
                        'chlorine ruling); the photoresist draw of RESIST_SYN comes off this edge in the fluoro '
                        'pass (A-M-482). | X-PAR-02 TF: foundry/polymers sizing (AQS-DUTY-072/AQS-DUTY-073). '
                        'Less 0.001824 kg/d to RESIST_SYN on IA-RESIST-CL2 (A-M-482).'}
CA_SHIP_SI_CL2 = float('0.009111121123485916')     # the committed A-M-484 make-up book (v1 float book)
# IA-KROLL-CO is stamped by no value family yet (the solvent family re-rates
# it with its CO draw, A-M-479): its template books the committed rate dict.
KROLL_CO_RATE = {'value': _f(45835, 10 ** 5), 'unit': 'kg/d', 'status': 'study',
                 'note': '1.170 kg/kg Ti chlorinator CO to the dock fuel-gas class (IA-N2-VENT precedent; '
                         'no spare burner capacity at Rev AC scope - burner routing is an integration '
                         'follow-up). | X-PAR-02 TF: foundry/polymers sizing (AQS-DUTY-072/AQS-DUTY-073). '
                         'Less 0.126101 kg/d to SOLV_PLANT on IA-SOLV-CO (A-M-479). Less 0.000721 kg/d to '
                         'RESIST_SYN on IA-RESIST-CO (A-M-482).'}

# ---- the 6 SF pot feeds (foundry bus feeds) ---------------------------------
SF_POT_NOTES = 'Foundry bus feed (AQS-DUTY-072).'
SF_POT_CARRIES = '480 V or 208/120 V AC (bus per AQS-ELEC-002)'
SF_POT_FORBIDDEN = 'battery Br\u2082 into CRU'
SF_POTS = (('SF-AL_POT', 'AL_POT'), ('SF-MG_POT', 'MG_POT'), ('SF-CA_POT', 'CA_POT'),
           ('SF-TI_CELL', 'TI_CELL'), ('SF-MO_CELL', 'MO_CELL'), ('SF-CR_CELL', 'CR_CELL'))
SF_POT_ANCHORS = {'SF-AL_POT': ('SF-MG_POT', 'SF-FLUX_PREP'), 'SF-MG_POT': ('SF-CA_POT', 'SF-FLUX_PREP'),
                  'SF-CA_POT': ('SF-TI_CELL', 'SF-FLUX_PREP'), 'SF-TI_CELL': ('SF-MO_CELL', 'SF-FLUX_PREP'),
                  'SF-MO_CELL': ('SF-CR_CELL', 'SF-FLUX_PREP'), 'SF-CR_CELL': ('SF-FLUX_PREP',)}

# ---- the on-site brine recovery (X-QA-11, A-M-496; salt_recovery.py tf) -----
BRINE_HOSTS = ('LEACH_CSTR_1', 'CA_POT', 'MG_POT')            # AQS-SITE-010 locale gate
BRINE_NODE_ANCHORS = ('NUT_AN',)
BRINE_NOTES = ('Agitated flash crystallizer on a leach-liquor side-stream: crystallizes the CaCl2/MgCl2 '
               'pot make-up out of the dissolved feed-assay and salt-flux chlorides and returns the mother '
               'liquor to the leach (X-QA-11, A-M-496).')
BRINE_CARRIES = {'IA-BRINE-SRC': 'leach-liquor side-stream to the crystallizer',
                 'IA-BRINE-CACL2': 'crystallized CaCl2 to the calcium pot (recovered, was the dock import)',
                 'IA-BRINE-MGCL2': 'crystallized MgCl2 to the magnesium pot (recovered, was the dock import)',
                 'IA-BRINE-ML': 'mother liquor (residual chlorides) returned to the leach'}
BRINE_STREAMS = (('IA-BRINE-SRC', 'LEACH_CSTR_1', 'BRINE_CRYS', 'L',
                  {'water': _f(85, 100), 'CaCl2': _f(5, 100), 'MgCl2': _f(4, 100), 'NaCl': _f(4, 100),
                   'other salts': _f(2, 100)}, ('IA-BRINE-CACL2', 'IA-WAX-CUT', 'IA-NUT-NH3') + A_SHELL_GRIT),
                 ('IA-BRINE-CACL2', 'BRINE_CRYS', 'CA_POT', 'L', {'CaCl2': ONE},
                  ('IA-BRINE-MGCL2', 'IA-WAX-CUT', 'IA-NUT-NH3') + A_SHELL_GRIT),
                 ('IA-BRINE-MGCL2', 'BRINE_CRYS', 'MG_POT', 'L', {'MgCl2': ONE},
                  ('IA-BRINE-ML', 'IA-WAX-CUT', 'IA-NUT-NH3') + A_SHELL_GRIT),
                 ('IA-BRINE-ML', 'BRINE_CRYS', 'LEACH_CSTR_1', 'L',
                  {'water': _f(922, 1000), 'CaCl2': _f(27, 1000), 'MgCl2': _f(22, 1000),
                   'NaCl': _f(21, 1000), 'other salts': _f(8, 1000)},
                  ('SF-BRINE_CRYS', 'IA-WAX-CUT', 'IA-NUT-NH3') + A_SHELL_GRIT))
SF_BRINE = ('SF-BRINE_CRYS', ('IA-WAX-CUT', 'IA-NUT-NH3') + A_SHELL_GRIT)
# the foundry family re-VALUES these three without replacing the note (the
# balance reconciler owns the note, AQS-PAR-003, and has not landed): the
# creation templates book the committed note verbatim so one pass converges.
BRINE_RATE_NOTES = {'IA-BRINE-SRC': ('feed = 2.000000 kg/d', _f(2000047, MG)),
                    'IA-BRINE-CACL2': ('cacl2 = 0.116115 kg/d', _f(116201, MG)),
                    'IA-BRINE-ML': ('ml = 1.844103 kg/d', _f(1844103, MG))}
BRINE_RATE_TAIL = ' (salt_recovery.py). | X-PAR-02 reconciled (AQS-PAR-003).'
BRINE_MGCL2_RATE = {'value': _f(39782, MG), 'unit': 'kg/d', 'status': 'study',
                    'note': 'X-RTE TF: on-site Kroll brine recovery (X-QA-11, A-M-496): '
                            'mgcl2 = 0.039782 kg/d (salt_recovery.py).'}
SF_BRINE_RATE = {'value': _f(7, 100), 'unit': 'kW', 'status': 'study',
                 'note': 'X-RTE TF: on-site Kroll brine recovery (X-QA-11, A-M-496): '
                         'feed equal to BRINE_CRYS continuous_kw.'}

# ---- the crew textile line (A-M-429, A-M-502): created when the spin line ---
# node is in the graph. The committed key order is the textile group's own
# (sectors directly after the endpoints; no header/forbidden/claim book).
TEXTILE_CONDITION = 'POLY_FIBER'
TEXTILE_NOTES = 'X-POLY textile line (A-M-429)'
TEXTILE = (('STOCK_TO_FIBER', 'POLY_STOCK', 'POLY_FIBER', 'liquid',
            'PP pellet draw to the melt-spin line', ('FR_FINISH', 'SF-POLY_FIBER')),
           ('IA-FR-P', 'WS_PHOS', 'POLY_FIBER', 'L',
            'phosphoric acid of the phosphate-FR finish', ('IA-FR-NH3', 'SHELL_GRIT')),
           ('IA-FR-NH3', 'WS_AMMONIA', 'POLY_FIBER', 'L',
            'ammonia of the phosphate-FR finish', ('SHELL_GRIT',)),
           ('FIBER_SCRAP', 'POLY_FIBER', 'LEACH_CSTR_1', 'liquid',
            'spin scrap to the solids line', ('FLEECE_TO_MFG', 'SF-POLY_FIBER')),
           ('FLEECE_TO_MFG', 'POLY_FIBER', 'MFG_SHOP', 'liquid',
            'FR-finished fleece to the shop for conversion', ('TEXTILE_HAB', 'SF-POLY_FIBER')),
           ('TEXTILE_HAB', 'MFG_SHOP', 'HABITATION', 'liquid',
            'finished crew textiles to the hab issue', ('SF-POLY_FIBER',)))

# ---- retirements: the dock imports the on-site routes replaced --------------
# IA-CL2-SHIP keeps its own carries; the writer never rewrote it there.
RETIRED_CARRIES = {'IA-ALCL3-MU': 'anhydrous AlCl3 top-up feed (retired: the Al line is sized to the '
                                  'recoverable aluminium, X-QA-19)',
                   'IA-MGCL2-MU': 'CaCl2-MgCl2 brine concentrate (retired: BRINE_CRYS crystallizes the '
                                  'make-up out of the leach chlorides, X-QA-11)',
                   'IA-CACL2-MU': 'CaCl2 brine concentrate (retired: BRINE_CRYS crystallizes the make-up '
                                  'out of the leach chlorides, X-QA-11)',
                   'IA-WAX-MU': 'pattern wax make-up (retired: the C19-C28 cut blend covers it, X-QA-11)'}
RETIRED_EDGES = ('IA-ALCL3-MU', 'IA-CL2-SHIP', 'IA-MGCL2-MU', 'IA-CACL2-MU', 'IA-WAX-MU',
                 'IA-SILICA-MU', 'IA-SHELL-EXPORT', 'IA-C-TI', 'IA-C-MO', 'IA-C-CR', 'FR_FINISH')
POP_EDGES = ('IA-MGCL2-MU', 'IA-CACL2-MU', 'IA-WAX-MU', 'FR_FINISH')
POP_KEYS = ('dock_class', 'dock_pending_task')
AL_LINE_DRIVER = 'foundry_al_line_kg_d'                       # al_cake > 0 <=> this driver > 0

# ---- the SI route (X-MFG-40 family-4; fab_silicon.py + si_refine.py tf) -----
# stream id, from, to, phase, composition element (None books the null), key.
STREAMS_FAB = (('STOCK_TO_FAB', 'METAL_STORE', 'WAFER_FAB', 'S', 'Si', 'si_kg_d'),
               ('IA-FAB-WAFER', 'WAFER_FAB', 'LITHO_COAT', 'S', 'Si', 'wafer_kg_d'),
               ('IA-LITHO-WAFER-A', 'LITHO_COAT', 'LITHO_ALIGN', 'S', 'Si', 'wafer_kg_d'),
               ('IA-LITHO-WAFER-B', 'LITHO_ALIGN', 'LITHO_DEV', 'S', 'Si', 'wafer_kg_d'),
               ('IA-LITHO-WAFER-RET', 'LITHO_DEV', 'WAFER_FAB', 'S', 'Si', 'wafer_kg_d'),
               ('IA-FAB-PRODUCT', 'WAFER_FAB', 'NORTH_DOCK', 'S', 'Si', 'wafer_kg_d'),
               ('IA-FAB-KERF', 'WAFER_FAB', 'LEACH_CSTR_1', 'S', 'Si', 'kerf_leach_kg_d'),
               ('IA-FAB-KERF-REC', 'WAFER_FAB', 'SI_REFINE', 'S', 'Si', 'kerf_rec_kg_d'),
               ('IA-FAB-SCRAP', 'WAFER_FAB', 'METAL_STORE', 'S', 'Si', 'scrap_rec_kg_d'),
               ('IA-PV-WAFER', 'WAFER_FAB', 'SOLAR_PV_CELL', 'S', 'Si', 'pv_wafer_kg_d'),
               ('IA-PV-CELL', 'SOLAR_PV_CELL', 'PV_ARRAY', 'S', 'Si', 'pv_wafer_kg_d'),
               ('IA-AR-CZ', 'CRYO_ASU', 'WAFER_FAB', 'G', 'Ar', 'ar_kg_d'),
               ('IA-AR-CZ-BACK', 'WAFER_FAB', 'CRYO_ASU', 'G', 'Ar', 'ar_kg_d'))
STREAMS_SI = (('IA-QUARTZ-MU', 'NORTH_DOCK', 'SI_REDUCE', 'S', 'SiO2', 'quartz_kg_d'),
              ('IA-SI-BRIQ', 'MFG_SHOP', 'SI_REDUCE', 'S', 'SiO2', 'briq_kg_d'),
              ('CHAR_TO_SI', 'OIL_PYRO', 'SI_REDUCE', 'S', 'C', 'char_kg_d'),
              ('IA-SI-HOOD-O2', 'ATMOS', 'SI_REDUCE', 'G', 'O2', 'o2_hood_kg_d'),
              ('IA-SI-CO2', 'SI_REDUCE', 'ATMOS', 'G', 'CO2', 'co2_kg_d'),
              ('IA-SI-FUME', 'SI_REDUCE', 'LEACH_CSTR_1', 'S', 'SiO2', 'fume_leach_kg_d'),
              ('IA-SI-MG', 'SI_REDUCE', 'SI_REFINE', 'S', 'Si', 'mg_kg_d'),
              ('IA-CL2-SIREF', 'CA_POT', 'SI_REFINE', 'G', 'Cl2', 'cl2_kg_d'),
              ('IA-SI-PURGE', 'SI_REFINE', 'LEACH_CSTR_1', 'L', None, 'purge_kg_d'),
              ('IA-PV-EOL', 'PV_ARRAY', 'SI_REFINE', 'S', 'Si', 'eol_in_kg_d'),
              ('IA-SI-EG', 'SI_REFINE', 'METAL_STORE', 'S', 'Si', 'eg_kg_d'))
CARRIES = {'STOCK_TO_FAB': 'electronic-grade silicon CZ charge from the store (refinery rod plus recycled '
                           'crop and pot scrap)',
           'IA-FAB-WAFER': 'wafers to resist coat',
           'IA-LITHO-WAFER-A': 'coated wafers to exposure',
           'IA-LITHO-WAFER-B': 'exposed wafers to develop',
           'IA-LITHO-WAFER-RET': 'patterned wafers back to the fab tool row',
           'IA-FAB-PRODUCT': 'finished wafers to the dock for dispatch',
           'IA-FAB-KERF': 'unreclaimed saw kerf with the spent slurry (1 - si_kerf_recycle_frac)',
           'IA-FAB-KERF-REC': 'reclaimed saw kerf to the chlorosilane loop (si_kerf_recycle_frac, A-M-486)',
           'IA-FAB-SCRAP': 'crop, square-off and pot scrap remelted into the next charge '
                           '(si_scrap_recycle_frac, A-M-487)',
           'IA-PV-WAFER': 'solar wafers to the cell line, from the CZ ingot or the cast block by '
                          'pv_wafer_route',
           'IA-PV-CELL': 'finished cells to the replacement modules of the roof array',
           'IA-AR-CZ': 'argon blanket gas for the CZ puller and, on CAST_MC156, the cast furnace',
           'IA-AR-CZ-BACK': 'CZ argon exhaust back to the cold-box getter',
           'IA-QUARTZ-MU': 'quartz ore for the silicon furnace (raw ore), the burden shortfall only',
           'IA-SI-BRIQ': 'briquetted crib silicate recovered from the leach feed, furnace burden (A-M-490)',
           'CHAR_TO_SI': 'pyrolysis char reductant',
           'IA-SI-HOOD-O2': 'oxygen of the hood air that burns the furnace carbon monoxide',
           'IA-SI-CO2': 'carbon dioxide of the burned furnace gas',
           'IA-SI-FUME': 'silica fume not briquetted back into the burden (1 - si_fume_burden_frac)',
           'IA-SI-MG': 'metallurgical-grade silicon',
           'IA-CL2-SIREF': 'chlorine make-up of the chlorosilane loop',
           'IA-SI-PURGE': 'impurity-chloride bleed with the end-of-life separation residue',
           'IA-PV-EOL': 'silicon of the cells retired from end-of-life modules, crushed, to the '
                        'chlorosilane loop',
           'IA-SI-EG': 'electronic-grade silicon for the CZ charge'}
# the two hand-era edges the route re-rated but never recreated (their committed
# shape predates the o2_close template; the creation books that shape verbatim)
OLD_SHAPE = ('STOCK_TO_FAB', 'CHAR_TO_SI')
OLD_NOTES = {'STOCK_TO_FAB': 'Integration edge. Rate TBD.',
             'CHAR_TO_SI': '3 kg/d assumption. notes/OIL_SECTOR.md.'}
SI_ANCHORS = {'STOCK_TO_FAB': ('FOUNDRY_SLAG_TO_LEACH',),
              'IA-FAB-WAFER': ('IA-LITHO-WAFER-A',) + A_SI_TAIL,
              'IA-LITHO-WAFER-A': ('IA-LITHO-WAFER-B',) + A_SI_TAIL,
              'IA-LITHO-WAFER-B': ('IA-LITHO-WAFER-RET',) + A_SI_TAIL,
              'IA-LITHO-WAFER-RET': ('IA-FAB-PRODUCT',) + A_SI_TAIL,
              'IA-FAB-PRODUCT': ('IA-FAB-KERF',) + A_SI_TAIL,
              'IA-FAB-KERF': ('IA-PV-WAFER',) + A_SI_TAIL,
              'IA-FAB-KERF-REC': ('IA-FAB-SCRAP',) + A_SI_TAIL,
              'IA-FAB-SCRAP': ('IA-SI-BRIQ',) + A_SI_TAIL,
              'IA-PV-WAFER': ('IA-PV-CELL',) + A_SI_TAIL,
              'IA-PV-CELL': ('IA-AR-CZ',) + A_SI_TAIL,
              'IA-AR-CZ': ('IA-AR-CZ-BACK',) + A_SI_TAIL,
              'IA-AR-CZ-BACK': ('IA-QUARTZ-MU',) + A_SI_TAIL,
              'IA-QUARTZ-MU': ('IA-SI-HOOD-O2',) + A_SI_TAIL,
              'IA-SI-BRIQ': ('IA-AL-CAKE',) + A_SHELL_GRIT,
              'CHAR_TO_SI': ('CO2_TO_FARM',),
              'IA-SI-HOOD-O2': ('IA-SI-CO2',) + A_SI_TAIL,
              'IA-SI-CO2': ('IA-SI-FUME',) + A_SI_TAIL,
              'IA-SI-FUME': ('IA-SI-MG',) + A_SI_TAIL,
              'IA-SI-MG': ('IA-CL2-SIREF',) + A_SI_TAIL,
              'IA-CL2-SIREF': ('IA-SI-PURGE',) + A_SI_TAIL,
              'IA-SI-PURGE': ('IA-PV-EOL',) + A_SI_TAIL,
              'IA-PV-EOL': ('IA-SI-EG',) + A_SI_TAIL,
              'IA-SI-EG': ('SF-SI_REDUCE',) + A_SI_TAIL,
              'SF-SI_REDUCE': ('SF-SI_REFINE',) + A_SI_TAIL,
              'SF-SI_REFINE': ('IA-FAB-KERF-REC',) + A_SI_TAIL}
SF_SI = (('SF-SI_REDUCE', 'SI_REDUCE'), ('SF-SI_REFINE', 'SI_REFINE'))
SI_REFINE_NOTE = 'Electronic-grade silicon refining (A-M-472).'
SI_REFINE_NOTES = ('Electronic-grade silicon refining: chlorosilane loop on metallurgical silicon from '
                   'SI_REDUCE (A-M-472).')
SI_REFINE_ANCHORS = ('BRINE_CRYS', 'NUT_AN')
SI_IMPORT = 'IA-SI-IMPORT'                                    # the retired dock import (t58u)

# ---- the IA-DC-REJ terminal clone (heat docstring; write_graph heat) --------
DC_REJ = 'IA-DC-REJ'
DC_TEMPLATE = 'HL-Q4-REJ'
DC_HOST = 'DRY_COOLER'
DC_CARRIES = 'dry-cooler rejection to ambient air'
DC_NOTES = ('F-3 (A-M-454): terminal rejection edge - the cooler passes the duty it receives to ambient '
            'air. Written by write_graph heat.')
DC_ANCHORS = ('IA-ZNBR-H2', 'IA-MET-AIR-MU')


# --- the shape primitives ----------------------------------------------------

def _sector(b, uid):
    """The endpoint node's sector (the edge_sectors invariant: the copied node
    sector is a graph invariant). A missing endpoint fails loudly."""
    return b.nodes[uid]['sector_id']


def _insert(b, obj, ident, anchors):
    """Insert obj into the builder's data list before the first present anchor
    (identity search - dict equality would find a wrong twin), else append;
    keep the builder's index current."""
    is_edge = 'stream_id' in obj
    lst = b.data['edges'] if is_edge else b.data['nodes']
    index = b.edges if is_edge else b.nodes
    pos = None
    for cand in anchors:
        tgt = index.get(cand)
        if tgt is not None:
            pos = next(i for i, x in enumerate(lst) if x is tgt)
            break
    if pos is None:
        lst.append(obj)
    else:
        lst.insert(pos, obj)
    index[obj[ident]] = obj


def _mass_edge(sid, frm, to, phase, layers, carries, notes, comp, sep, v):
    """An o2_close-shaped edge (the _edge template's key order verbatim)."""
    return {'stream_id': sid, 'from_unit_id': frm, 'to_unit_id': to, 'phase': phase,
            'layers': list(layers), 'presence': 'present', 'carries': carries,
            'header': 'dedicated', 'forbidden': sep[0], 'claim_status': sep[1],
            'rate': dict(v), 'from_sector_id': None, 'to_sector_id': None,
            'open_boundary': False, 'namespace': 'IA', 'gap_flags': [], 'notes': notes,
            'composition': dict(comp) if comp else None}


def _sf_edge(sid, to, carries, forbidden, claim, notes, header, ns='S', tray_comp=False):
    """An SF bus feed. The pot feeds clone the SF-HF_GEN shape (namespace S,
    no composition key); the SI feeds are o2_close creates with a tray header
    (namespace IA, composition null)."""
    e = {'stream_id': sid, 'from_unit_id': 'SOL_ARK_60K', 'to_unit_id': to, 'phase': 'E',
         'layers': ['elec'], 'presence': 'present', 'carries': carries, 'header': header,
         'forbidden': forbidden, 'claim_status': claim, 'rate': _rate(sid, 'kW'),
         'from_sector_id': None, 'to_sector_id': None, 'open_boundary': False,
         'namespace': ns, 'gap_flags': [], 'notes': notes}
    if tray_comp:
        e['composition'] = None
    return e


def _textile_edge(sid, frm, to, phase, carries):
    """A crew-textile edge (the textile group's own committed key order)."""
    return {'stream_id': sid, 'from_unit_id': frm, 'to_unit_id': to,
            'from_sector_id': None, 'to_sector_id': None, 'carries': carries,
            'layers': ['mass'], 'presence': 'present', 'rate': _rate(sid),
            'notes': TEXTILE_NOTES, 'phase': phase, 'namespace': 'IA', 'open_boundary': False}


def _si_edge(sid, frm, to, phase, comp):
    """A route stream. The o2_close template shape, except the two hand-era
    edges the route re-rated but never recreated (their committed key order
    and notes are seed shape)."""
    carries = CARRIES[sid]
    if sid in OLD_SHAPE:
        return {'stream_id': sid, 'from_unit_id': frm, 'to_unit_id': to, 'phase': phase,
                'presence': 'present', 'carries': carries, 'notes': OLD_NOTES[sid],
                'namespace': 'IA', 'layers': ['mass'], 'open_boundary': False,
                'rate': _rate(sid), 'from_sector_id': None, 'to_sector_id': None,
                'composition': {comp: ONE} if comp else None}
    return _mass_edge(sid, frm, to, phase, ('mass',), carries, None,
                      {comp: ONE} if comp else None, O2_SEP, _rate(sid))


def _node(uid, sector, cls, role, note, notes):
    """The o2_close _node template (key order verbatim)."""
    return {'unit_id': uid, 'sector_id': sector, 'presence': 'present', 'class': cls, 'tags': [],
            'electrical_role': role, 'diagram_gap': None, 'notes': notes, 'enabled': True,
            'continuous_kw': None, 'modules': [],
            'params': {'presence': 'present', 'note': note}}


def _create_edge(b, sid, mk, anchors):
    """Create-if-missing: the seed carries the creation, so this is a no-op on
    the committed tree and the restore move on a pre-mutation seed."""
    if sid in b.edges:
        return
    e = mk()
    e['from_sector_id'] = _sector(b, e['from_unit_id'])
    e['to_sector_id'] = _sector(b, e['to_unit_id'])
    _insert(b, e, 'stream_id', anchors)


def _retire(b, sid):
    """Retire-if-present (a no-op on the committed tree)."""
    e = b.edges.get(sid)
    if e is not None:
        e['presence'] = 'retired'


# ---- the family shape functions ---------------------------------------------

@fn('topology_foundry', 'the foundry family graph-shape mutations (X-QA-19/X-QA-11 creates, retirements, '
    're-point, seeded edge params; the composer lane the foundry golden report inventoried): applied '
    'before the values, keyed to data conditions, idempotent on the committed seed')
def foundry_apply(b, inputs):
    # ---- creates: the 31 mass edges and the 6 SF pot feeds ------------------
    for sid, frm, to, phase, layers, carries, notes, comp, sep, anchors in FOUNDRY_MASS:
        if sid == 'IA-KROLL-CO':
            v = KROLL_CO_RATE
        elif sid == 'IA-CA-CL2-SHIP':
            v = CA_SHIP_RATE
        else:
            v = _rate(sid)
        _create_edge(b, sid, lambda sid=sid, frm=frm, to=to, phase=phase, layers=layers,
                     carries=carries, notes=notes, comp=comp, sep=sep, v=v:
                     _mass_edge(sid, frm, to, phase, layers, carries, notes, comp, sep, v), anchors)
        if sid in CREATE_PARAMS:
            p = b.edges[sid].setdefault('params', {})
            for k, val in CREATE_PARAMS[sid].items():
                p.setdefault(k, val)
    if 'IA-CA-CL2-SHIP' in b.edges:
        b.edges['IA-CA-CL2-SHIP'].setdefault('params', {}).setdefault('si_cl2_kg_d', CA_SHIP_SI_CL2)
    for sid, to in SF_POTS:
        _create_edge(b, sid, lambda sid=sid, to=to: _sf_edge(sid, to, SF_POT_CARRIES, SF_POT_FORBIDDEN,
                                                             None, SF_POT_NOTES, 'tray'),
                     SF_POT_ANCHORS[sid])
    # ---- the crew textile line: data condition - the spin line is in the graph
    if TEXTILE_CONDITION in b.nodes:
        for sid, frm, to, phase, carries, anchors in TEXTILE:
            _create_edge(b, sid, lambda sid=sid, frm=frm, to=to, phase=phase, carries=carries:
                         _textile_edge(sid, frm, to, phase, carries), anchors)
        # the S34B finish book: seeded once from the rate where the textile
        # line is live (A-M-502); the committed seed carries it
        s34 = b.edges.get('S34B')
        if s34 is not None:
            s34.setdefault('params', {}).setdefault('pre_fr_kg_d', float(s34['rate']['value'] or 0))
    # ---- the on-site brine recovery: the hosts-present locale gate ----------
    if all((b.nodes.get(u) or {}).get('presence') == 'present' for u in BRINE_HOSTS):
        if 'BRINE_CRYS' not in b.nodes:
            _insert(b, _node('BRINE_CRYS', _sector(b, 'CA_POT'), 'precip', 'load',
                             'Brine crystallizer (A-M-496).', BRINE_NOTES),
                    'unit_id', BRINE_NODE_ANCHORS)
        b.nodes['BRINE_CRYS']['class'] = 'precip'   # re-stamped every pass (the precipitation class)
        for sid, frm, to, phase, comp, anchors in BRINE_STREAMS:
            def mk(sid=sid, frm=frm, to=to, phase=phase, comp=comp):
                if sid in BRINE_RATE_NOTES:
                    head, val = BRINE_RATE_NOTES[sid]
                    note = ('X-RTE TF: on-site Kroll brine recovery (X-QA-11, A-M-496): ' + head
                            + BRINE_RATE_TAIL)
                    v = {'value': val, 'unit': 'kg/d', 'status': 'study', 'note': note}
                else:
                    v = dict(BRINE_MGCL2_RATE)          # the family re-stamps this rate in full
                return _mass_edge(sid, frm, to, phase, ('mass',), BRINE_CARRIES[sid], None, comp,
                                  O2_SEP, v)
            _create_edge(b, sid, mk, anchors)
        _create_edge(b, SF_BRINE[0],
                     lambda: _mass_edge(SF_BRINE[0], 'SOL_ARK_60K', 'BRINE_CRYS', 'E', ('elec',),
                                        '480 V AC', None, None, O2_SEP, dict(SF_BRINE_RATE)),
                     SF_BRINE[1])
        b.edges['SF-BRINE_CRYS']['header'] = 'tray'
        # the crystallizer feeds the pots in the retired imports' places
        _retire(b, 'IA-MGCL2-MU')
        _retire(b, 'IA-CACL2-MU')
    # ---- retirements: the dock imports the on-site routes replaced ----------
    for sid in RETIRED_EDGES:
        _retire(b, sid)
    for sid, wording in RETIRED_CARRIES.items():
        if sid in b.edges:
            b.edges[sid]['carries'] = wording
    for sid in POP_EDGES:
        e = b.edges.get(sid)
        if e is not None:
            p = e.setdefault('params', {})
            for k in POP_KEYS:
                p.pop(k, None)
    # ---- the IA-CL2-SHIP book: base seed in, silicon netting moved out ------
    sh = b.edges.get('IA-CL2-SHIP')
    if sh is not None:
        p = sh.setdefault('params', {})
        p['base_kg_d'] = _f(0)                     # fluoro_train reads this every pass (A-M-481 HCL_OX branch)
        p.pop('si_cl2_kg_d', None)                 # the netting moved to IA-CA-CL2-SHIP (A-M-484)
    # ---- the pre-cake bases: seeded once from the rate, if the Al line runs -
    drv = inputs.get('drivers') or {}
    line = drv.get(AL_LINE_DRIVER)
    if line is not None and Fraction(str(line['value'])) > 0:
        for sid in ('IA-SINK-01', 'IA-WET-FLOAT-01'):
            e = b.edges.get(sid)
            if e is not None:
                e.setdefault('params', {}).setdefault('pre_al_cake_kg_d',
                                                      float(e['rate']['value'] or 0))
    # ---- the wax re-point: the cut comes from the OIL train (edge_sectors) --
    cut = b.edges.get('IA-WAX-CUT')
    if cut is not None:
        cut['from_sector_id'] = _sector(b, cut['from_unit_id'])


@fn('topology_si_route', 'the si_route family create-or-rate shape (X-MFG-40/X-RTE-SI, A-M-471/472): the '
    'SI_REFINE node when a seed predates the route, the 24 fab and route streams, the 2 SF feeds, and '
    'the IA-SI-IMPORT retirement (owner decision t58u: deleted outright in the committed tree)')
def si_route_topology(b, inputs):
    # ---- the SI_REFINE node: created by v1 only when the graph predates the
    # route; the data condition is the node's absence beside the route furnace
    if 'SI_REFINE' not in b.nodes and 'SI_REDUCE' in b.nodes:
        _insert(b, _node('SI_REFINE', 'GLASS', 'reactor', None, SI_REFINE_NOTE, SI_REFINE_NOTES),
                'unit_id', SI_REFINE_ANCHORS)
    # ---- the 24 streams: create-if-missing (the family re-rates in place) ---
    for sid, frm, to, phase, comp, _key in STREAMS_FAB + STREAMS_SI:
        _create_edge(b, sid, lambda sid=sid, frm=frm, to=to, phase=phase, comp=comp:
                     _si_edge(sid, frm, to, phase, comp), SI_ANCHORS.get(sid, A_SI_TAIL))
    # ---- the SF feeds: created only when missing, header tray on creation ---
    if 'SI_REFINE' in b.nodes and 'SI_REDUCE' in b.nodes:
        for sid, to in SF_SI:
            _create_edge(b, sid, lambda sid=sid, to=to: _sf_edge(sid, to, '480 V AC', O2_SEP[0],
                                                                 O2_SEP[1], None, 'tray',
                                                                 ns='IA', tray_comp=True),
                         SI_ANCHORS[sid])
    # ---- the dock silicon import: v1 retired it when present; the committed
    # tree deleted it outright (owner decision t58u) - the shape converges by
    # deletion
    if SI_IMPORT in b.edges:
        e = b.edges.pop(SI_IMPORT)
        b.data['edges'].remove(e)              # a stream_id names one edge: equality is identity here


@fn('topology_heat_relief', 'the heat/relief chain graph-shape mutation: the IA-DC-REJ terminal clone-if-'
    'absent (F-3, A-M-454; the heat docstring builders-work row). The v1 relief and vent commands perform '
    'no shape mutation of their own - verified against their writers')
def heat_relief_topology(b, inputs):
    if DC_REJ in b.edges or DC_TEMPLATE not in b.edges or DC_HOST not in b.nodes:
        return
    rej = copy.deepcopy(b.edges[DC_TEMPLATE])
    rej.update(stream_id=DC_REJ, from_unit_id=DC_HOST, to_unit_id='ATMOS', to_sector_id='WTR',
               carries=DC_CARRIES, namespace='IA', notes=DC_NOTES)
    rej['rate'] = dict(KW_D)
    _insert(b, rej, 'stream_id', DC_ANCHORS)

"""The storage and hold-up sizing family (family migration; reference writer
docs-authority/_storage_sizing.py, ledger row `storage_sizing`, section B,
MIXED: split the sizing -> this function, the STORAGE_HOLDUP.md page and the
inventory/STORAGE_HOLDUP.json sidecar -> the renderer wave).

AQS-DUTY-064 (unit task 02 for storage-class units; A-M-225): working volume
V = Q x t_hold / rho with Q = max(design capacity, duty in) at the X-RSZ-07
bounding case, nominal volume V / fill (freeboard and dead volume) with a 0.02
m3 floor, upright cylinder at the H/D driver, D and H on the 50 mm vessel grid.
Wall: PE by hoop stress T = P OD / (2 SD) at the SD driver, minimum wall
driver [ASTM_D1998]; flammable and compressed-gas service is welded SA-240
304L by the ASME VIII-1 UG-27 line T = P R / (S - 0.6 P), minimum wall driver.
Hold times are the A-M-225 basis. The reference writer stamps per unit
params.size_mm (the sized vessel + the envelope allowance on every face),
params.size_note and params.design_storage; the committed graph carries exactly
those fields. That committed state is the golden this module reproduces.

Grid doctrine (owner ruling 2026-11-15): the solve is exact. Driver, profile
and seed values convert at the boundary by rat() (the exact Fraction of the
decimal repr); the arithmetic is Fraction over those decimals, the cube root of
the vessel sizing at 60-digit Decimal, pi as the integer scaled pair
3141592653589793/10^15. Quantisation happens only at the reference writer's own
rounding points, as integer books: book(x, dp, cite) with the dimension and
scale named at every call (the 4 dp nominal-volume book, the 2 dp wall book,
integers on the bore, height and envelope). No float literals; the lint holds
this. The hold_d driver passthrough the design book carries verbatim stays the
reference writer's own raw value, documented here.

Q books (A-M-270/A-M-278 D-DOCK product buffers derive Q from their feed/draw
edges, not a duty sheet; every other covered unit reads the X-RSZ-07 design
capacity and the duty sheet's In-rate through the reference writer's rule, and
at the committed seed neither exists, so Q books 0 and the 0.02 m3 floor
governs - recorded, not invented).

DISPOSITION: the graph stamps land here. The md page and the json sidecar are
renderer-wave work; their downstream consumers are recorded so the renderer
lane inherits the contract: docs-authority/inventory/STORAGE_HOLDUP.json is
read by the sizing-coverage registry, the task plan and the farm/hab balance
(docs-authority/_farm_hab.py). The duty-sheet envelope fit (the Size A x B x C
regex over docs-authority/duties/<unit>.md) is also renderer-wave: it reads
another stage's document and stamps nothing on the graph.

The committed stamps carry two residue classes this function does not own, the
test enumerates them per field with their owners:
- four buffer books lag the seed rates their Q draws on (the v1 lattice ran
  this stage before the writers that re-rate STOCK_TO_MFG, IA-N2-VENT,
  IA-O2-PROD and IA-MEOH-PROD; the committed tree carries the mid-loop census
  those reads saw - METAL_STORE 14.0, AIR_RECEIVER 3.1 (the A-M-273 N2
  surplus), PROD_O2 22.8768, PROD_MEOH 28.35 kg/d - the seed carries the
  end-of-loop rates). This function stamps the fresh census off the seed rates
  it sees; the power family's store-book precedent.
- the nine FAB reagent-tank size_mm envelopes carry the CAD/GA style-builder
  wave's claimed geometry (the consolidated-lane regeneration that overwrote
  44 unit size_mm books after this stage); this function's own vessel book is
  the [600, 600, 600] envelope its D/H grid carries.
"""
from decimal import Decimal, localcontext
from fractions import Fraction
import re

from flow_graph.v2.registry import fn

STAGE = 'storage_sizing'                                       # ledger row, section B
DOC = 'AQS-DUTY-064'
PI = Decimal(3141592653589793) / Decimal(10) ** 15            # pi (scale 1e-15)
V_FLOOR_M3 = Fraction(2, 100)                                 # the 0.02 m3 nominal-volume floor
GRID_MM = Fraction(50)                                        # the vessel bore/height grid, mm
# unit: driver path (hold_d, rho_kg_m3, P_MPa for gas), service, phase; the
# reference writer's B table verbatim (services are its text, carried for the
# renderer lane).
B = {'FAB_UPW_TANK': ('FAB.wet-reagent-train.bench.FAB_UPW_TANK', 'UPW buffer to the fab (1 d limits TOC pickup)', 'L'),
     'MEOH_TANK': ('MEOH.synthesis-train.MEOH_TANK', 'methanol day store, 14 d campaign', 'L'),
     'REMIN': ('WTR.potable-upw-train.REMIN', 'remineralisation contact, 1 d buffer', 'L'),
     'WS_AMMONIA': ('FAB.wet-reagent-train.reagents.WS_AMMONIA', 'aqueous NH3 25 %, 30 d resupply', 'L'),
     'WS_DOPE': ('FAB.wet-reagent-train.reagents.WS_DOPE', 'dopant solution, 30 d resupply', 'L'),
     'WS_HF_ED': ('FAB.wet-reagent-train.reagents.WS_HF_ED', 'HF etch 49 %, 30 d resupply', 'L'),
     'WS_KOH': ('FAB.wet-reagent-train.reagents.WS_KOH', 'KOH 45 %, 30 d resupply', 'L'),
     'WS_NITRIC': ('FAB.wet-reagent-train.reagents.WS_NITRIC', 'HNO3 65 %, 30 d resupply', 'L'),
     'WS_PEROX': ('FAB.wet-reagent-train.reagents.WS_PEROX', 'H2O2 30 %, 30 d resupply', 'L'),
     'WS_SLURRY': ('FAB.wet-reagent-train.reagents.WS_SLURRY', 'CMP slurry, 30 d resupply', 'L'),
     'WS_SOLV': ('FAB.wet-reagent-train.reagents.WS_SOLV', 'solvent (IPA), 30 d resupply', 'L'),
     'WS_PHOS': ('FAB.wet-reagent-train.reagents.WS_PHOS', 'H3PO4 85 %, 30 d resupply', 'L'),
     'PROD_C5_C10': ('OIL.pyro-fractionation-train.cuts-and-headers.PROD_C5_C10', 'naphtha cut, 14 d to dispatch', 'L'),
     'PROD_C11_C18': ('OIL.pyro-fractionation-train.cuts-and-headers.PROD_C11_C18', 'middle distillate cut, 14 d', 'L'),
     'PROD_C19_C28': ('OIL.pyro-fractionation-train.cuts-and-headers.PROD_C19_C28', 'heavy distillate cut, 14 d', 'L'),
     'PROD_C29': ('OIL.pyro-fractionation-train.cuts-and-headers.PROD_C29', 'C29+ to recycle, 3 d buffer', 'L'),
     'NUTRIENT_DOSE': ('NUT.dosing-train.NUTRIENT_DOSE', 'dosing solution day tank, 1 d (stock concentrate is stored dry)', 'L'),
     'HOPPER': ('OIL.pyro-fractionation-train.pyro-frac.HOPPER', 'shredded feed, 1 d (bulk density)', 'S'),
     'FOOD_STORE': ('FARM.grow-bed-train.FOOD_STORE', 'D-DOCK food buffer: fresh harvest pass-through + X-RED-08 80 d dry reserve (A-M-270)', 'S'),
     'METAL_STORE': ('FOUNDRY.form-train.METAL_STORE', 'D-DOCK metal product buffer, 14 d dispatch campaign (A-M-270)', 'S'),
     'AIR_RECEIVER': ('CRYO.cold-box-asu-recovery-train.cold-box.AIR_RECEIVER', 'D-DOCK plant-air receiver on the cold-box N2 delivery, 1 d of the ASU/vent margin (A-M-270)', 'G'),
     'PROD_O2': ('CRYO.cold-box-asu-recovery-train.feed-and-recovery.PROD_O2', 'D-DOCK surplus-O2 product bank, cylinder-bank equivalent volume, 14 d dispatch campaign (A-M-278)', 'G'),
     'PROD_MEOH': ('CRYO.cold-box-asu-recovery-train.feed-and-recovery.PROD_MEOH', 'D-DOCK methanol product store, 14 d dispatch campaign (A-M-278)', 'L')}
PHASE = {u: row[2] for u, row in B.items()}
# the D-DOCK product buffers (A-M-270/A-M-278): Q derives from the seed feed /
# draw edges (the standing inventory each buffer carries), not a duty sheet.
# FOOD_STORE: the dry-matter draw S14 x the 6 % DM share (X-RED-08 reserve).
GRAPH_Q_EDGES = {
    'FOOD_STORE': (('S14',), Fraction(6, 100)),
    'METAL_STORE': (('STOCK_TO_MFG', 'STOCK_TO_FAB', 'STOCK_TO_WIRE_DRAW'), None),
    'AIR_RECEIVER': (('IA-N2-VENT',), None),
    'PROD_O2': (('IA-O2-PROD',), None),
    'PROD_MEOH': (('IA-MEOH-PROD',), None),
}
GAS_STEEL = {'AIR_RECEIVER', 'PROD_O2'}     # compressed gas: steel at the working pressure
FLAM = {'MEOH_TANK', 'WS_SOLV', 'PROD_C5_C10', 'PROD_C11_C18', 'PROD_C19_C28', 'PROD_C29', 'PROD_MEOH'}


def rat(value):
    """A v1 driver/seed value -> its exact Fraction (the decimal the JSON carried)."""
    return Fraction(Decimal(str(value)))


def _round_half_even(x, dp):
    """An exact value -> integer count of 10^-dp units, half-even (Python
    round()'s documented tie rule - the reference writer's rounding)."""
    m = 10 ** dp
    a, b = x.numerator * m, x.denominator
    sign = -1 if a < 0 else 1
    q, r = divmod(abs(a), b)
    if 2 * r > b or (2 * r == b and q % 2 == 1):
        q += 1
    return sign * q


def unbook(cnt, dp):
    """Render an integer book count as the exact JSON number of its decimal."""
    f = float(Decimal(cnt) / (Decimal(10) ** dp))
    return float(0) if f == 0 else f


def fq(x, dp, cite):
    """book + render in one step: the exact value at `dp` decimals."""
    return unbook(_round_half_even(x, dp), dp)


def ceil_f(x):
    """math.ceil of an exact value."""
    return -((-x.numerator) // x.denominator)


def _cbrt(x):
    """The cube root of a positive exact value as a 60-digit Decimal."""
    with localcontext() as ctx:
        ctx.prec = 60
        xd = Decimal(x.numerator) / Decimal(x.denominator)
        return xd ** (Decimal(1) / Decimal(3))


def _ceil_grid_mm(x_mm, grid):
    """math.ceil(x/grid)*grid on an exact mm length: the vessel grid rule."""
    return int(ceil_f(x_mm / grid) * grid)


def _prov(basis, ref=None):
    from flow_graph.v2.model import Prov
    return Prov(STAGE, basis, ref)


def _set(b, uid, path, value, basis, ref=None):
    b.set_node_field(uid, path, value, _prov(basis, ref))


def _drv(drv, key):
    """A driver value: the flat dotted key the drivers.json tree carries."""
    return drv[key]['value']


def _duty_in(b, uid):
    """The reference writer's qin(): max(design capacity, the duty sheet's
    In-rate). Reads the node's own params only (no document I/O); at the
    committed seed neither field exists, so this books 0 - recorded, not
    invented."""
    p = b.nodes[uid].get('params') or {}
    cap = (p.get('design_capacity_kg_d') or {}).get('value') or 0
    m = re.search(r'In ([\d.]+) kg/d', p.get('duty') or '')
    return max(rat(cap), rat(m.group(1)) if m else Fraction(0))


def _graph_q(b, uid):
    """The A-M-270/A-M-278 buffer Q from the seed feed/draw edges, on the
    reference writer's 4 dp Q book."""
    edges, dm = GRAPH_Q_EDGES.get(uid, ((), None))
    q = Fraction(0)
    for sid in edges:
        e = b.edges.get(sid)
        if e is None or e.get('presence') != 'present':
            continue
        v = (e.get('rate') or {}).get('value')
        if isinstance(v, (int, float)):
            q += rat(v)
    if dm is not None:
        q = q * dm
    return fq(q, 4, 'buffer hold-up Q, kg/d, 4 dp Q book') if edges else None


def _core(b, inputs):
    """The storage chain: the port of _storage_sizing.py's row loop on exact
    rational arithmetic. Returns the per-unit books, or None without the
    drivers and the site profile (the bridge contract)."""
    drv = inputs.get('drivers')
    prof = inputs.get('site_profile')
    if drv is None or prof is None:
        return None
    g = rat(prof['groups']['gravity']['entries']['g_m_s2']['value'])   # apparent gravity (AQS-PLAN-011 3.2)
    sd = rat(_drv(drv, 'storage_pe_sd_MPa'))
    tmin = rat(_drv(drv, 'storage_pe_min_wall_mm'))
    fill = rat(_drv(drv, 'storage_tank_fill_frac'))
    hd = rat(_drv(drv, 'storage_tank_HD'))
    ss = rat(_drv(drv, 'storage_steel_allow_MPa'))
    tmin_s = rat(_drv(drv, 'storage_steel_min_wall_mm'))
    allow = int(rat(_drv(drv, 'storage_envelope_allowance_mm')))
    rows = {}
    for u, (path, svc, ph) in B.items():
        q_g = _graph_q(b, u)
        # the reference writer's `GRAPH_Q.get(u, 0.0) or qin(n)`: the buffer
        # book wins unless it rounds to 0, then the duty/capacity rule reads
        q = rat(q_g) if q_g else _duty_in(b, u)
        td = rat(_drv(drv, path + '.hold_d'))
        rho = rat(_drv(drv, path + '.rho_kg_m3'))
        v_work = q * td / rho
        v_nom = max(v_work / fill, V_FLOOR_M3)
        d_mm = _ceil_grid_mm(Fraction(_cbrt(4 * v_nom / (Fraction(PI) * hd))) * 1000, GRID_MM)
        h_mm = _ceil_grid_mm(v_nom / (Fraction(PI) * (Fraction(d_mm, 1000) ** 2) / 4) * 1000, GRID_MM)
        p = rat(_drv(drv, path + '.P_MPa')) if u in GAS_STEEL else \
            (rho * g * h_mm / 1000 / Fraction(10) ** 6 if ph == 'L' else Fraction(0))
        steel = u in FLAM or u in GAS_STEEL
        wall = max(p * Fraction(d_mm, 2) / (ss - p * Fraction(6, 10)), tmin_s) if steel \
            else max(p * d_mm / (2 * sd), tmin)
        mat = 'SA-240 304L, welded' if steel else 'PE (rotomoulded / fabricated)'
        rows[u] = dict(size_mm=[d_mm + allow, d_mm + allow, h_mm + allow],
                       size_note='L x W x H mm, set by docs-authority/_storage_sizing.py (AQS-DUTY-064)',
                       design_storage={'hold_d': _drv(drv, path + '.hold_d'),   # driver passthrough (documented)
                                       'V_nom_m3': fq(v_nom, 4, 'nominal volume, m3, 4 dp design book'),
                                       'D_mm': d_mm, 'H_mm': h_mm,
                                       'wall_mm': fq(wall, 2, 'wall thickness, mm, 2 dp design book'),
                                       'material': mat})
    return rows


@fn('storage_sizing', 'AQS-DUTY-064 storage and hold-up sizing (unit task 02, A-M-225 hold times, X-RSZ-07 '
    'bounding Q): working volume Q x hold / rho at the fill fraction, upright cylinder at the H/D driver on the '
    '50 mm vessel grid, PE hoop wall (ASTM_D1998) or welded SA-240 304L (NFPA 30 flammables, ASME VIII-1 UG-27 '
    'line; compressed gas at the working pressure); the A-M-270/A-M-278 D-DOCK buffers carry their edge-derived '
    'standing inventory')
def storage_sizing(b, inputs):
    s = _core(b, inputs)
    if s is None:
        return                                                 # bridge contract: no payloads, no stamps
    basis = (f'the storage and hold-up sizing ({DOC}): working volume Q x hold / rho at the fill driver, '
             'vessel on the 50 mm grid at the H/D driver, wall by hoop stress at the material drivers; '
             'hold times A-M-225; buffer Q from the seed feed/draw edges (A-M-270, A-M-278)')
    for u in B:
        row = s[u]
        _set(b, u, 'params.size_mm', row['size_mm'], basis)
        _set(b, u, 'params.size_note', row['size_note'], basis)
        _set(b, u, 'params.design_storage', row['design_storage'], basis)

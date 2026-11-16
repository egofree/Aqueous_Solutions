"""The PV cell-line tool sizing family (family migration; reference writers
flow_graph/param/pv_cell_line.py and the pv_wafer.need() cell rate it consumes,
ledger row `sizing_pv_cell_line`, section B, MIXED: split sizing -> this
function, the PV_CELL_LINE.md page -> the renderer wave).

X-MFG-38 (A-M-178, AQS-DUTY-071, A-M-484): SOLAR_PV_CELL runs batches of one
wafer carrier at the cell rate that replaces the roof array, through texture,
POCl3 diffusion, PSG etch, PECVD SiNx, screen print, fast firing and IV test.
Bath and furnace energy is the heat-up of the heated mass m cp dT plus the
ASTM_C680 insulated-cylinder shell loss at temperature (sizing/heat.py
insulated_cylinder, INCROPERA7); PECVD is RF power density x electrode area
plus heater and vacuum pump; print, fire and IV are drive or lamp power x
time. The reference writer stamps SOLAR_PV_CELL's continuous_kw dict,
params.avg_kw, params.design (the whole tool book including the cell-need
chain) and the SF/SQ feed rates; the committed graph carries exactly those
fields. That committed state is the golden this module reproduces.

Grid doctrine (owner ruling 2026-11-15): the quantised books are exact - the
continuous/average kW stamps are integer books on the 4 dp power scale
(book(x, dp, cite), half-even, the dimension named at every call). The
params.design tool book is a DIFFERENT class, documented here: the v1 writer
stored it unrounded - a raw float product of the driver floats through
math.acos/math.sqrt/math.pi (the semi-square cell area) and the shell-loss
ladder - so the committed repr is only reachable by the same float expression
over the same inputs. That chain ports as the v1 float replica it is: every
constant enters as an integer scaled pair floated at the boundary, every
driver and seed value enters by its exact float value, and the operation order
is the reference writer's, line for line. No float literals; the lint holds
this. The books that stay floats by necessity are confined to params.design,
continuous_kw.value/params.avg_kw and the SF feed (all v1 float books).

DISPOSITION: the graph stamps land here. The PV_CELL_LINE.md page (sections
3 and 4 re-derive the wafer routes and the cast/puller comparisons) is
renderer-wave work. The SQ-SOLAR_PV_CELL edge died with HEAT_SINK in Rev AC:
the feed update keeps the reference writer's exists-guard. The SF-SOLAR_PV_CELL
feed books value-only: its note is the X-RSZ-07 feed-edge pass's (that pass
re-notes every unfed load after this stage - the committed residue). size_mm,
size_note, equipment_id, koh and not on SOLAR_PV_CELL are other writers'
fields and stay passthrough. A solve without the drivers records nothing (the
bridge contract).
"""
import math
from decimal import Decimal
from fractions import Fraction

from flow_graph.v2.registry import fn

STAGE = 'sizing_pv_cell_line'                                  # ledger row, section B
TAG = 'X-MFG-38 (A-M-178, AQS-DUTY-071)'
PVL = 'FAB.wafer-line-train.SOLAR_PV_CELL.'                    # the driver prefixes (U4b single-sourcing)
PVW = 'FAB.pv-wafer-train.'
F = 'FAB.wafer-line-train.'
ROUTES = ('CZ_PSQ125', 'CAST_MC156')

# ---- the float boundary: exact constants floated, no float literals ---------
K1000 = float(1000)                                            # W/kW and g/kg scale
K3600 = float(3600)                                            # s/h
K24 = float(24)                                                # h/d
K60 = float(60)                                                # min/h
K2 = float(2)                                                  # pairs
K4 = float(4)                                                  # quadrants
K100 = float(100)                                              # cm2/m2 x cm2 per m2 book
K10000 = float(10000)                                          # cm2/m2
K2000 = float(2000)                                            # mm->m inside the shell loss
DAYS_YR = float(Fraction(36525, 100))                          # 365.25 d/yr (the Julian year book)
STC_W_M2 = float(1000)                                         # 1000 W/m2 standard irradiance (IEC 60904-3)


def _fl(f):
    """The float of an exact value (the float-replica boundary)."""
    return float(f)


def _round_half_even(x, dp):
    """An exact value -> integer count of 10^-dp units, half-even."""
    m = 10 ** dp
    a, b = x.numerator * m, x.denominator
    sign = -1 if a < 0 else 1
    q, r = divmod(abs(a), b)
    if 2 * r > b or (2 * r == b and q % 2 == 1):
        q += 1
    return sign * q


def book(x, dp, cite):
    """The integer book: exact value -> count of 10^-dp units, half-even.
    `cite` names the dimension and the schema scale at the call site."""
    return _round_half_even(x, dp)


def unbook(cnt, dp):
    """Render an integer book count as the exact JSON number of its decimal."""
    from decimal import Decimal as D
    f = float(D(cnt) / (D(10) ** dp))
    return float(0) if f == 0 else f


def _prov(basis, ref=None):
    from flow_graph.v2.model import Prov
    return Prov(STAGE, basis, ref)


def _set(b, uid, path, value, basis, ref=None):
    b.set_node_field(uid, path, value, _prov(basis, ref))


# ---- the v1 float-replica helpers (documented float books) ------------------

def _insulated_cylinder(T_C, D_mm, L_m, Ta_C, h, k_a, k_b, Ts_max, thk, ends):
    """sizing/heat.py insulated_cylinder [ASTM_C680], the v1 float book:
    smallest standard thickness with the surface at or under Ts_max; k =
    k_a + k_b T_mean; `ends` for heads and nozzles. Returns (thk_mm, loss_W)."""
    r1 = D_mm / K2000
    for t in thk:
        r2 = r1 + t / K1000
        k = k_a + k_b * (T_C + Ts_max) / K2
        q = (T_C - Ta_C) / (math.log(r2 / r1) / (K2 * math.pi * k) + float(1) / (K2 * math.pi * r2 * h))
        Ts = Ta_C + q / (K2 * math.pi * r2 * h)
        if Ts <= Ts_max:
            break
    return t, q * L_m * ends


def _psq_area_cm2(side_mm, D_mm):
    """pv_wafer.psq_area_cm2, the v1 float book: a square of side side_mm with
    its corners cut by a circle of diameter D_mm (a semi-square wafer)."""
    R, h = D_mm / K2, side_mm / K2
    if h >= R:
        raise SystemExit(f'pv_cell_line: a {side_mm} mm square does not fit inside a {D_mm} mm ingot')
    if h * math.sqrt(K2) <= R:
        return side_mm ** K2 / K100
    seg = R * R * math.acos(h / R) - h * math.sqrt(R * R - h * h)   # circular segment beyond each flat
    return (math.pi * R * R - K4 * seg) / K100


def _need(dv, nameplate):
    """pv_wafer.need() for the committed route, the v1 float book: the cell
    rate that replaces the roof array (A-M-484)."""
    route = dv('pv_wafer_route')
    if route not in ROUTES:
        raise SystemExit(f'pv_cell_line: pv_wafer_route {route!r} is not one of {ROUTES}')
    life = (float(1) - dv(PVW + 'eol_output_frac')) / dv(PVW + 'degradation_per_yr')
    repl = float(1) / life + dv(PVW + 'failure_per_yr')
    kw = _fl(nameplate)
    W_d = kw * K1000 * repl / DAYS_YR
    t = dv(PVW + 'wafer_t_um') / K10000
    kerf = dv(F + 'kerf_um') / K10000
    rho = dv(F + 'si_rho_g_cm3')
    if route == 'CZ_PSQ125':
        D = dv(F + 'wafer_D_mm')
        A = _psq_area_cm2(dv(PVW + 'psq_side_mm'), D)
        eff = dv(PVW + 'cell_eff_CZ')
        body = math.pi / K4 * (D / float(10)) ** K2
    else:
        A = dv(PVW + 'mc_side_mm') ** K2 / K100
        eff = dv(PVW + 'cell_eff_MC')
        body = A
    cell_W = A / K10000 * STC_W_M2 * eff
    cells = W_d / cell_W
    wafer_g = rho * A * t
    slot_g = rho * body * (t + kerf)
    return dict(route=route, array_kw=kw, life_yr=life, repl_per_yr=repl, W_d=W_d, cell_area_cm2=A,
                cell_eff=eff, cell_W=cell_W, cells_per_d=cells, wafer_g=wafer_g, slot_g=slot_g,
                wafer_kg_d=cells * wafer_g / K1000, slot_kg_d=cells * slot_g / K1000,
                t_cm=t, kerf_cm=kerf, Si_g_per_W=slot_g / cell_W)


def _core(b, inputs):
    """The tool-by-tool energy chain: the port of pv_cell_line.design() in the
    v1 float replica for the design book, exact books for the stamps. Returns
    the result dict, or None without the drivers (the bridge contract)."""
    drv = inputs.get('drivers')
    if drv is None:
        return None

    def dv(k):
        return drv[k]['value']                                 # the raw driver float, as v1 read it

    nd = _need(dv, _nameplate(b))
    cells = nd['cells_per_d']
    nb = int(dv(PVL + 'pvl_cassette_n'))
    batches = math.ceil(cells / nb)
    boat = int(dv('pvl_diff_L_m') * K1000 / dv(PVL + 'pvl_boat_pitch_mm'))
    if boat < nb:
        raise SystemExit(f'pv_cell_line: the diffusion boat holds {boat} wafers, fewer than a carrier of {nb}')
    amb = dv(PVL + 'pvl_amb_T_C')
    hot_a, hot_b = dv('pvl_hot_k_a'), dv('pvl_hot_k_b')
    thk = (13, 25, 38, 50, 65, 75, 100, 125, 150, 200)         # the mineral-wool ladder, mm (integers)
    T = []
    # texture: water bath heated once a day, held at temperature for each batch
    q = dv('pvl_tex_L') * dv(PVL + 'pvl_water_cp_kJ_kgK') * (dv('pvl_tex_C') - amb) / K3600
    _, loss = _insulated_cylinder(dv('pvl_tex_C'), dv(PVL + 'pvl_tex_tank_D_mm'), dv(PVL + 'pvl_tex_tank_H_m'),
                                  float(25), float(10), float(Fraction(37, 1000)), float(Fraction(17, 100000)),
                                  float(50), thk, float(Fraction(13, 10)))
    T.append(('PV-TEX-01', 'KOH texture bath, 10 L PP tank, immersion heater, one carrier a batch',
              q / dv('pvl_tex_heat_h') + loss / K1000, q + loss / K1000 * dv('pvl_tex_run_h') * batches))
    # diffusion tube furnace: heated once a day, one boat a batch
    q = dv('pvl_diff_mass_kg') * dv(PVL + 'pvl_diff_cp_kJ_kgK') * (dv('pvl_diff_C') - amb) / K3600
    t, loss = _insulated_cylinder(dv('pvl_diff_C'), dv('pvl_diff_D_mm'), dv('pvl_diff_L_m'),
                                  float(25), float(10), hot_a, hot_b, float(50), thk, float(Fraction(13, 10)))
    T.append(('PV-EMIT-01', f"POCl3 diffusion, quartz tube {dv('pvl_diff_D_mm'):.0f} mm x "
                            f"{dv('pvl_diff_L_m'):.1f} m, {t} mm ceramic fibre, boat of {boat} slots",
              q / dv('pvl_diff_heat_h') + loss / K1000,
              q + loss / K1000 * (dv('pvl_diff_run_h') * batches + dv('pvl_diff_heat_h') / K2)))
    T.append(('PV-PSG-01', 'HF PSG etch, room temperature PP bath', float(0), float(0)))
    # PECVD: the electrode holds one carrier of cells; platen and chamber follow from it
    area = nb * nd['cell_area_cm2'] / K10000
    chamber = math.sqrt(K4 * area / math.pi) * K1000 + K2 * dv(PVL + 'pvl_pecvd_clear_mm')
    rf = dv('pvl_pecvd_W_cm2') * area * K10000 / K1000
    qh = dv(PVL + 'pvl_pecvd_platen_kg_m2') * area * dv(PVL + 'pvl_pecvd_platen_cp_kJ_kgK') \
        * (dv('pvl_pecvd_C') - amb) / K3600
    _, lh = _insulated_cylinder(dv('pvl_pecvd_C'), chamber, dv(PVL + 'pvl_pecvd_chamber_H_m'),
                                float(25), float(10), hot_a, hot_b, float(50), thk, float(Fraction(13, 10)))
    T.append(('PV-ARC-01', f'PECVD SiNx, parallel-plate RF, {area:.2f} m2 electrode in a {chamber:.0f} mm chamber, '
                           'dry vacuum pump',
              rf + qh / dv(PVL + 'pvl_pecvd_heat_h') + lh / K1000 + dv('pvl_vac_kW'),
              (rf * dv('pvl_pecvd_dep_h') + lh / K1000 * dv('pvl_vac_h') + dv('pvl_vac_kW') * dv('pvl_vac_h')) * batches + qh))

    def h(k):
        return dv(PVL + k) * cells / K60

    T.append(('PV-CON-01', 'Screen printer and 200 C dryer', dv('pvl_print_kW') + dv('pvl_dry_kW'),
              (dv('pvl_print_kW') + dv('pvl_dry_kW')) * h('pvl_print_min_cell')))
    T.append(('PV-FIRE-01', 'IR lamp fast-firing furnace', dv('pvl_fire_kW'), dv('pvl_fire_kW') * h('pvl_fire_min_cell')))
    T.append(('PV-IV-01', 'Flash IV tester', dv('pvl_iv_kW'), dv('pvl_iv_kW') * h('pvl_iv_min_cell')))
    e = sum(t[3] for t in T)
    return dict(need=nd, cells_per_d=cells, batches=batches, carrier=nb,
                tools=[dict(id=a, design=b, peak_kW=c, kWh_d=d) for a, b, c, d in T],
                kWh_d=e, avg_kW=e / K24, peak_kW=max(t[2] for t in T), kWh_per_cell=e / cells)


def _nameplate(b):
    """The roof-array nameplate the cell line replaces (A-M-484): the seed
    PV_ARRAY params.nameplate_kw (the power family's roof-close book)."""
    p = (b.nodes.get('PV_ARRAY') or {}).get('params') or {}
    kw = p.get('nameplate_kw')
    assert isinstance(kw, (int, float)), 'pv_cell_line: the seed lacks the PV_ARRAY nameplate the line replaces'
    return kw


@fn('sizing_pv_cell_line', 'X-MFG-38 PV cell-line tool sizing (A-M-178, AQS-DUTY-071; the cell rate is the '
    'replacement need of the roof array, A-M-484): bath and furnace heat-up plus the ASTM_C680 insulated shell '
    'loss (INCROPERA7), PECVD RF + platen + vacuum, print/fire/IV drive and lamp power; the line peak is the '
    'largest tool (one tool at a time)')
def pv_cell_line(b, inputs):
    s = _core(b, inputs)
    if s is None:
        return                                                 # bridge contract: no drivers, no stamps
    avg = Fraction(Decimal(str(s['avg_kW'])))
    avg_book = unbook(book(avg, 4, 'line average load, kW, 4 dp continuous_kw book'), 4)
    note = (f"{TAG}: {s['kWh_d']:.2f} kWh/d for {s['cells_per_d']:.1f} cells/d in {s['batches']} batches of one "
            f"carrier (A-M-484); peak {s['peak_kW']:.2f} kW (one tool at a time).")
    basis = (f'{TAG} tool-by-tool energy physics: bath and furnace heat-up plus the ASTM_C680 shell loss, PECVD '
             'RF + platen + vacuum, print/fire/IV drive power; the cell rate is the roof-array replacement need '
             '(A-M-484); the design book is the reference writer\'s raw float book (documented)')
    _set(b, 'SOLAR_PV_CELL', 'continuous_kw',
         {'value': avg_book, 'unit': 'kW', 'status': 'study', 'note': note}, basis)
    _set(b, 'SOLAR_PV_CELL', 'params.avg_kw', avg_book, basis)
    _set(b, 'SOLAR_PV_CELL', 'params.design', s, basis)
    # the SF feed value is this family's book; the note is the X-RSZ-07
    # feed-edge pass's (it re-notes every unfed load after this stage - the
    # committed residue). Value-only update, the one-writer-per-field split.
    for sid in ('SF-SOLAR_PV_CELL', 'SQ-SOLAR_PV_CELL'):       # SQ-* heat edges died with HEAT_SINK in Rev AC
        if sid in b.edges:
            seed = dict(b.edges[sid]['rate'])
            seed['value'] = avg_book
            b.set_edge_rate(sid, seed, _prov(basis + '; value-only update (the X-RSZ-07 feed pass owns the note)'))

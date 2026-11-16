"""The buildings, safety and constructability renderer wave (the portable
ledger section H document rows), plus the section D haz_area book import.
Reference writers: docs-authority/_egress_hall.py, _water_tower.py,
_egress_env.py, _fire.py, _gas_det.py, _asme_class.py, _hydro_siting.py,
_relief_register.py and _znbr_test.py. Nine documents and one machine sidecar
port as pure functions Model -> document bytes, reproducing the v1 templates
exactly; the physics books they consume live in flow_graph/v2/functions/
(building, fire_book, gas_detection, protection, haz_area) with golden
equality proven in flow_graph/v2/test_safety_books.py. The acceptance is
byte-exact reproduction of the committed files
(flow_graph/v2/test_render_safety.py).

Compositions in memory (the EVAP X-STD-01 pattern of render/electrical.py):
- the HALL_EGRESS X-STD-01 code-basis append: v1 wrote the page and called
  code_basis.append; here the body is composed and the block appended in
  memory (flow_graph.param.code_basis.block, the single source);
- the FIRE_PROTECTION in-memory rebuild: v1 rebuilt the receiver design and
  relief bases in memory (flow_graph.param.receivers.design over a copied
  node map) before quoting them - the same rebuild here, without touching the
  model;
- the WATER_TOWER datum fixpoint: v1 rewrote the placement datums and then
  quoted them; the committed page sits at that fixpoint (old == new), which
  is what this renderer reproduces - the seed rewrite itself is the builder
  lane's, not a renderer's.

REMAINING (the section H rows NOT ported here; each becomes a renderer when
its family lands, per the electrical wave's precedent):
- doc_egress_hall / doc_water_tower write halves (the placement-seed
  passageway block and the datum rewrite): builder lane, not renderer;
- doc_ga_check: reads the placement seed, report and study (placement_refine,
  not landed);
- doc_hse_sep: reads the placement report and writes flow_graph/fire_rooms.json;
- doc_site_access: reads the placement seed and the hand placement study;
- doc_struct_loads: reads the placement seed, study and report (STRUCT_ROWS
  family; frame_check, foundation, lifting, install_seq and rigging_plans
  wait on it);
- doc_frame_check / doc_foundation / doc_lifting / doc_install_seq /
  doc_rigging_plans: read STRUCT_LOADS.md / STRUCT_ROWS.json /
  FRAME_CHECK.json / LIFTING.md (the struct-loads chain above);
- access_check: reads flow_graph/ga_envelopes.load() = the placement seed,
  report and study;
- sep_check: reads the placement seed (CAMEO pair separation);
- doc_hvac: reads STRUCT_ROWS.json, inventory/HAZ_AREA.csv and
  inventory/COMMISSIONING.csv;
- doc_decom: reads inventory/COMMISSIONING.csv and STRUCT_ROWS.json;
- doc_startup: reads inventory/COMMISSIONING.csv (doc_commissioning product;
  the commissioning family waits on the instrument index, sif list and ITPs);
- doc_commissioning: reads INSTRUMENT_INDEX.csv, sif_list.csv and the unit
  ITPs (instrument, sif and ITP families, not landed);
- doc_compliance: rewrites section 11 of the hand-authored COMPLIANCE_MATRIX.md
  (hand base text; the composer lane declares it, as with the duty sheets);
- haz_area (HAZ_AREA.md + HAZ_AREA.csv): the zone book is ported
  (flow_graph/v2/functions/haz_area.py, golden against the committed CSV
  fields); the document and sidecar wait on the instrument and other census
  families (INSTRUMENT_INDEX.csv, OTHER_INVENTORY.csv).

Pure: no I/O here - the registry returns bytes and file writing stays outside.
"""
import collections
import math
import re

from flow_graph.param import receivers as _RC                                   # design() (pure over a copied node map)
from flow_graph.param.code_basis import MARK as _CODE_MARK                      # X-STD-01 block, single source
from flow_graph.param.code_basis import block as _code_block
from flow_graph.param.sizing.relief import equiv_bore_mm, gas_area_in2          # API 520 helpers (pure)

from ..functions import building as _BLD
from ..functions import fire_book as _FB
from ..functions import gas_detection as _GD

G_BASE_FALLBACK = float('9.80665')                                              # baseline-profile gravity (site.py)


# ---- shared model/driver readers (the render/electrical.py payload idiom) ----

def _node_view(m):
    """The seed nodes in order, with params resolved (overlay composed)."""
    out = {}
    for uid, n in m.nodes.items():
        v = dict(n)
        if 'params' in v:
            v['params'] = m.field('node', uid, 'params')
        out[uid] = v
    return out


def _drv_of(inputs):
    """The resolved driver payload: drivers.json with every entry the site
    profile binds replaced by the profile's value (the v1 DR.load() read)."""
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
    return d[key]['value']


def _gravity(inputs):
    """Apparent gravity, m/s2: the site profile entry (the v1 SITE.g() read);
    the baseline value stands when the inputs carry no profile."""
    prof = inputs.get('site_profile')
    if not prof:
        return G_BASE_FALLBACK
    return prof['groups']['gravity']['entries']['g_m_s2']['value']


def _p_process_kPa(inputs):
    """Process-space absolute pressure, kPa (the v1 SITE.p_process_kPa read):
    the shell interior where the profile states one, else the external
    atmosphere."""
    prof = inputs.get('site_profile')
    if not prof:
        return float('101.325')                                                 # the baseline standard atmosphere
    atm = prof['groups']['atmosphere']['entries']
    shell = atm.get('shell_pressure_kPa')
    return (shell['value'] if shell else atm['pressure_Pa']['value'] / 1000)


def _finish(md, key):
    """The v1 write_doc + code_basis.append composition: strip any code-basis
    block, then append the X-STD-01 rows (the composer lane; the file write
    stayed outside)."""
    body = re.sub(r'\n' + re.escape(_CODE_MARK) + r'.*?(?=\n## |\Z)', '', md, flags=re.S).rstrip('\n') \
        + '\n\n' + _code_block(key)
    return body.encode('utf-8')


# ---- AQS-EGR-002: the extension hall egress (HALL_EGRESS.md) -------------------

_LIM = float('76.2')                                                            # NFPA 101 Table 40.2.6 travel limit, m
_LOAD = float('9.29')                                                           # occupant load factor, m2/person
_CAP = float('0.0051')                                                          # egress capacity, mm/person
_LEAF = float('0.813')                                                          # door leaf clear width, m
_PAIR = 2 * _LEAF
_BX, _BY = float('24.0'), float('18.0')                                         # base plate in the SW corner


def _hall_doors(w, big_d, s, yp):
    """Door points: perimeter (outside the base plate) every s m; passageway
    faces every s m."""
    p = []
    n = max(2, math.ceil(w / s))
    p += [(w * (i + float('0.5')) / n, big_d) for i in range(n)]                # north wall
    p += [(_BX + (w - _BX) * (i + float('0.5')) / max(1, math.ceil((w - _BX) / s)), float('0.0'))
          for i in range(max(1, math.ceil((w - _BX) / s)))]                     # south wall east of the plate
    m = max(2, math.ceil(big_d / s))
    p += [(w, big_d * (i + float('0.5')) / m) for i in range(m)]                # east wall
    p += [(float('0.0'), _BY + (big_d - _BY) * (i + float('0.5')) / max(1, math.ceil((big_d - _BY) / s)))
          for i in range(max(1, math.ceil((big_d - _BY) / s)))]                 # west wall north of the plate
    k = max(2, math.ceil(w / s))
    p += [(w * (i + float('0.5')) / k, yp) for i in range(k)]                   # passageway doors (both faces)
    return p


def _hall_worst(p, w, big_d, yp, wp):
    """Worst rectilinear travel on a 2 m grid."""
    worst = float(0)
    wpt = None
    for x in range(0, int(w) + 1, 2):
        for y in range(0, int(big_d) + 1, 2):
            if x < _BX and y < _BY:
                continue
            if abs(y - yp) < wp / 2:
                continue
            dmin = min(abs(x - a) + abs(y - b) for a, b in p)
            if dmin > worst:
                worst, wpt = dmin, (x, y)
    return worst, wpt


def render_hall_egress(m, inputs):
    """docs-authority/HALL_EGRESS.md: the v1 _egress_hall.py template from the
    converged roof (graph PV_ARRAY params.roof), closed with the X-STD-01
    code-basis block (HALL_EGRESS rows). The placement-seed passageway block
    the v1 stage also writes is the builder lane's, not a document."""
    rf = m.field('node', 'PV_ARRAY', 'params')['roof']
    w, big_d = rf['footprint_mm'][0] / 1000, rf['footprint_mm'][1] / 1000
    a = w * big_d - _BX * _BY
    occ = math.ceil(a / _LOAD)
    yp = big_d / 2
    s = 90
    for s in range(90, 20, -5):
        p = _hall_doors(w, big_d, s, yp)
        worst, _wpt = _hall_worst(p, w, big_d, yp, float('3.5'))
        if worst <= _LIM:
            break
    n_ext = len(p) - max(2, math.ceil(w / s))
    share_pw = max(2, math.ceil(w / s)) / len(p)
    occ_pw = math.ceil(occ * share_pw)
    wp = max(float('1.12'), occ_pw * _CAP / 2)                                  # NFPA 101 7.2.6.4 width, 1120 mm minimum
    wp = math.ceil(wp * 10) / 10
    occ_ext = occ - occ_pw
    need_ext = occ_ext * _CAP
    have_ext = n_ext * _PAIR
    worst, wpt = _hall_worst(_hall_doors(w, big_d, s, yp), w, big_d, yp, wp)
    md = f"""# Extension hall egress

Document number: AQS-EGR-002
Revision: A
Date: 2026-10-15
Authority: AQS-PLAN-007 X-STD-01; AQS-EGR-001 Rev C 2.1 (most restrictive code governs). Generated by `docs-authority/_egress_hall.py` from the converged roof (graph PV_ARRAY params.roof). Study. Not a PE stamp. A-M-115.

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue for the {w:.0f} x {big_d:.0f} m building (D77). | 2026-10-15 |

## 1. Basis

| Item | Value | Clause |
| --- | --- | --- |
| Occupancy | general industrial, ordinary hazard; sprinklered throughout | NFPA 101-2027 40.1.4.1.1; NFPA 13-2025; IBC 2027 306.2 F-1 |
| Occupant load factor | 9.29 m2/person gross | NFPA 101 Table 7.3.1.2; IBC Table 1004.5 |
| Travel distance | 76.2 m | NFPA 101 Table 40.2.6 (governs; IBC 1017.2.2 allows 122 m at 7.3 m clear height) |
| Common path | 30.5 m | NFPA 101 40.2.5 |
| Number of exits | 4 minimum above 1000 occupants | NFPA 101 7.4.1.2; IBC Table 1006.3.3 |
| Egress capacity | 5.1 mm/person, doors and level components | NFPA 101 Table 7.3.3.1; IBC 1005.3.2 |
| Door leaf clear width | 813 mm minimum | NFPA 101 7.2.1.2.3 |
| Exit passageway | 2 h fire barrier, width for the load served, 1120 mm minimum | NFPA 101 7.2.6, 7.3.4.1; IBC 1024 |
| Exit discharge | to grade at the exterior wall | NFPA 101 7.7; IBC 1028 |
| Lighting, marking | emergency lighting 90 min, exit signs | NFPA 101 7.9, 7.10; NFPA 70 Art. 700 |

## 2. Result

| Quantity | Value |
| --- | --- |
| Hall floor area (excluding the base plate) | {a:,.0f} m2 |
| Occupant load | {occ} |
| Door spacing on walls and passageway faces | {s} m |
| Worst rectilinear travel on a 2 m grid | {worst:.1f} m at {wpt} (limit {_LIM}) |
| Exterior exit door pairs | {n_ext} pairs, {have_ext:.1f} m clear (need {need_ext:.1f} m for {occ_ext} occupants) |
| Exit passageway | {wp} m clear x {w:.0f} m, {len(p) - n_ext} door pairs, serves {occ_pw} occupants, two discharges |
| Exits to outside | {n_ext + 2} (minimum 4) |
| Travel | {'pass' if worst <= _LIM else 'FAIL'} |
| Capacity | {'pass' if have_ext >= need_ext else 'FAIL'} |
| Number of exits | {'pass' if n_ext + 2 >= 4 else 'FAIL'} |

Door pairs give two paths from any point within about {s / 2:.0f} m along the wall line, so the common path stays inside 30.5 m in the open hall; enclosed rooms in the hall programme are checked when it is set. The base plate keeps its own egress (AQS-EGR-001). Rectilinear distance along aisles is used as a bound for the travel path.

## 3. Consequences

1. NFPA 13 sprinklers throughout the hall are a precondition of the 76.2 m limit; the water supply and design density follow the hall programme (open item).
2. The passageway adds a 2 h fire barrier across the hall; its block EXIT_PASSAGE_HALL is in the placement seed.
3. If the hall contents are classed low hazard (NFPA 101 40.1.4.1.2: no self-propagating fire), Table 40.2.6 sets no travel limit and the passageway can be dropped. That needs the owner's hall programme.
"""
    return _finish(md, 'HALL_EGRESS')


# ---- AQS-BLD-014: the water tower (WATER_TOWER.md) -----------------------------

def render_water_tower(m, inputs):
    """docs-authority/WATER_TOWER.md: the v1 _water_tower.py template over the
    building book (functions/building), the seismic-and-wind book, and the
    drivers. The placement datums the v1 stage rewrites sit at their fixpoint
    in the committed page (old == new) - the rewrite itself is the builder
    lane's."""
    d = _drv_of(inputs)
    g = _gravity(inputs)
    b = _BLD.building_book(m, d, g)
    r = b['HYDRO']
    s = _BLD.seismic_wind(r, b['PLATE_L'], b['PLATE_W'], d, g)
    v = lambda k: d[k]['value']
    k_n = r['water_t'] * g
    a = r['area_m2']
    datums = {'L-2': b['Z_Lm2'], 'ROOF': b['Z_ROOF']}
    for i in range(r['levels']):
        datums[f'R{i + 1}'] = b['HYDRO_RES_Z0'] + i * b['HYDRO_RES_CLEAR']
    old = {'L-2': b['Z_Lm2'], 'ROOF': b['Z_ROOF']}                              # the fixpoint of the v1 datum rewrite
    md = ['# Water tower: pumped-hydro reservoirs in the building', '', 'Document number: AQS-BLD-014', 'Revision: A',
          'Date: 2026-10-16',
          'Authority: AQS-PLAN-007 X-RED-02; owner decision Q-009 (closed 2026-10-16): build the top floors as the upper reservoir. Generated by `docs-authority/_water_tower.py` from `flow_graph/param/water_tower.py`. Study. A-M-187.', '',
          '## Sizing from need', '',
          f"Store: {r['E_kWh']:.1f} kWh at the bus (HYDRO_SET backup basis, NFPA 111 Class X, A-M-145). Turbine-generator {v('hydro_eta_turbine')} (DOE_PSH) less {v('wt_penstock_loss_frac') * 100:.0f} % penstock friction gives {r['eta_net']:.2f}.",
          'Head is the drop between the water centroids, upper full to lower full. It depends on the reservoir depth, so the solver iterates: V = E / (rho g h eta).', '',
          '| Item | Value |', '|---|---|',
          f"| Head (centroid to centroid) | {r['head_m']:.2f} m |",
          f"| Water | {r['V_m3']:.0f} m3 live + {r['V_fire_m3']:.0f} m3 fire reserve below the hydro outlet (AQS-SAF-005) = {r['water_t']:.0f} t |",
          f"| Reservoir plan area (plate less {v('wt_core_frac') * 100:.0f} % cores) | {a:.0f} m2 |",
          f"| Upper reservoir | {r['levels']} levels at {r['level_clear_m']:.1f} m floor-to-floor above the ROOF_TANK storey, "
          f"{r['depth_per_level_m']:.2f} m water each (max {v('wt_water_max_m')} m), {r['cells_per_level']} cells per level of {r['cell_len_m']:.1f} m |",
          f"| Upper reservoir floor / roof | +{r['z_res0_m']:.1f} m / +{r['z_roof_m']:.1f} m |",
          f"| Lower reservoir (CATCH_TANK) | {r['catch_depth_m']:.2f} m water + {v('wt_freeboard_m')} m freeboard over {a:.0f} m2, floor at {r['z_catch_floor_m']:.2f} m |",
          f"| Penstock static pressure | {1000 * g * (r['z_res0_m'] - r['z_catch_floor_m']) / 1000000:.2f} MPa at the turbine |", '',
          f"Each reservoir level is split into at least two cells, each with its own outlet valve to the penstock, so one cell can be drained for "
          f"inspection while the store keeps {100 * (r['cells_per_level'] * r['levels'] - 1) / (r['cells_per_level'] * r['levels']):.0f} % of its energy (redundancy rule).", '',
          'Building rule (owner): as the plant grows, HAB/FARM levels are added at '
          + f"{v('wt_life_per_shop')} x the rate of shop levels (LIFE_LEVELS = 1 + {v('wt_life_per_shop')} (SHOP_LEVELS - 1)). "
          f"A taller life stack raises the head and the reservoir shrinks in step. At this scale: {b['SHOP_LEVELS']} shop, {b['LIFE_LEVELS']} life level(s).", '',
          '## CATCH_TANK basis (check)', '',
          'The earlier CATCH_TANK was a fixed 12 x 8 x 4 m box scaled by plate area (384 m3; 3,916 kN test load in AQS-BLD-013 rev A). '
          'That was not from need. It is now the lower reservoir and holds the full upper volume plus freeboard; terrace rain catch uses the '
          'freeboard and overflows to the site drain. The tank is '
          + f"{b['CATCH_TANK_L'] / 1000:.1f} x {b['CATCH_TANK_W'] / 1000:.1f} x {b['CATCH_TANK_H'] / 1000:.2f} m.", '',
          '## Structural loads (ASCE7_22, ACI350_3, ACI350_20)', '',
          '| Load | Value | Basis |', '|---|---|---|',
          f"| Water weight, upper | {k_n:.0f} kN ({k_n / r['levels'] / a:.1f} kPa per reservoir slab) | operating = test (full) |",
          f"| Seismic base shear from the water mass | {s['V_seis_kN']:.0f} kN (Cs {s['Cs']:.2f}) | ASCE 7 12.8, SDS {v('wt_SDS')}, "
          f"R {v('wt_R')}, Ie {v('wt_Ie')} (Risk Cat. IV), impulsive mass taken rigid |",
          f"| Seismic overturning at grade | {s['M_seis_kNm']:.0f} kN m | water centroid height |",
          f"| Convective period, sloshing height | {s['Tc_s']:.2f} s, {s['slosh_m']:.2f} m (Sac {s['Sac']:.3f} g) | "
          'ACI 350.3 rectangular cell, ASCE 7 15.7.6.1.2 |',
          f"| Freeboard in each reservoir level | {r['level_clear_m'] - float('0.3') - r['depth_per_level_m']:.2f} m, "
          f"{'covers' if s['freeboard_ok'] else 'DOES NOT cover'} the sloshing height | soffit must not take wave impact |",
          f"| Wind on the reservoir storeys | {s['F_wind_kN']:.0f} kN (qz {s['qz_kPa']:.2f} kPa at {s['H_roof_m']:.1f} m) | "
          f"ASCE 7 ch. 26-27, exposure C, {v('wt_wind_ms')} m/s |", '',
          f"Seismic governs over wind by {s['V_seis_kN'] / s['F_wind_kN']:.0f} x. The lateral system (X-BLD-01) and the foundations (X-BLD-03) "
          'must carry it; walls and slabs that retain water follow ACI 350 crack control. Site SDS, SD1 and wind speed are assumptions until the '
          'geotechnical report (A-M-187).', '',
          '## Egress and access (IBC2027_CH10, NFPA101_2027)', '',
          'The reservoir levels are unoccupied: maintenance access only. The two exit stairs (IBC 1006.3.3) continue through the reservoir storeys '
          'to the roof for PV service (IBC 1011.12), in the core fraction above. Each cell has a hatch, ladder and confined-space entry procedure. '
          'The reservoir floors add no occupant load and no travel distance to the life floors.', '',
          '## Roof PV', '',
          f"The PV array moves to the reservoir roof at +{r['z_roof_m']:.1f} m (datum ROOF). The footprint is unchanged, so the roof area and the "
          'PV area (solver.roof_close) are unchanged; the PV dead load now lands on the reservoir roof slab.', '',
          'Placement datums changed: L-2 ' + str(old.get('L-2')) + ' -> ' + str(datums['L-2']) + ' mm, ROOF ' + str(old.get('ROOF'))
          + ' -> ' + str(datums['ROOF']) + ' mm, added '
          + ', '.join(f"R{i + 1} {datums[f'R{i + 1}']}" for i in range(r['levels'])) + ' mm.']
    return ('\n'.join(md) + '\n').encode('utf-8')


# ---- AQS-BLD-018: enclosure, floor plates, stairs and egress (ENCLOSURE_EGRESS.md)

_OCC_LV = (('L-2', 'lower reservoir and catch (maintenance only)', float('27.9'), float('0.15')),
           ('L-1', 'process (industrial)', float('9.3'), float('1.0')),
           ('L0', 'process and shop (industrial)', float('9.3'), float('1.0')),
           ('L1', 'habitation (residential) + farm (agricultural storage)', (float('18.6') + float('27.9')) / 2, float('1.0')),
           ('L2', 'farm and roof tank (storage)', float('27.9'), float('1.0')))
_RES_LV_USE = ('upper reservoir (maintenance walkway only)', float('27.9'), float('0.15'))
_ROOF_LV = ('ROOF', 'roof PV (maintenance)', float('27.9'), float('1.0'))


def render_enclosure_egress(m, inputs):
    """docs-authority/ENCLOSURE_EGRESS.md: the v1 _egress_env.py check over the
    building book (IBC 1004.5 occupant loads, IBC 1006.3.3 exits, IBC
    1005.3.1/1011.2 stair widths, 76 m travel, IECC 2021 C402 enclosure UA at
    the AQS-SITE-002 heating design point). The geometry is the
    models/freecad/params.py baseline state, which functions/building carries
    (that library loads drivers and the graph on import, so the book ports
    it)."""
    d = _drv_of(inputs)
    g = _gravity(inputs)
    b = _BLD.building_book(m, d, g)
    lp, wp = b['PLATE_L'], b['PLATE_W']
    a = lp * wp / 1000000
    z0r, clr = b['HYDRO_RES_Z0'], b['HYDRO_RES_CLEAR']
    lv = [(name, b[zkey], use, f, frac) for name, zkey, use, f, frac in
          (('L-2', 'Z_Lm2', *_OCC_LV[0][1:]), ('L-1', 'Z_Lm1', *_OCC_LV[1][1:]), ('L0', 'Z_L0', *_OCC_LV[2][1:]),
           ('L1', 'Z_L1', *_OCC_LV[3][1:]), ('L2', 'Z_L2', *_OCC_LV[4][1:]))]
    lv += [(f'R{i + 1}', z0r + i * clr, _RES_LV_USE[0], _RES_LV_USE[1], _RES_LV_USE[2]) for i in range(b['HYDRO_RES_LEVELS'])]
    lv.append((_ROOF_LV[0], b['Z_ROOF'], _ROOF_LV[1], _ROOF_LV[2], _ROOF_LV[3]))
    z_top = max(b['Z_L2'] + 2000, b['Z_ROOF'] + 2000)
    st = (('STAIR_P', b['Z_L0'], z_top, b['STAIR_BOX']),
          ('STAIR_S1', b['Z_L0'], max(b['Z_L2'], b['Z_ROOF']), b['STAIR_BOX']),
          ('STAIR_S2', b['Z_L0'], b['Z_L2'], b['STAIR_BOX']),
          ('STAIR_MAINT', b['Z_Lm2'], b['Z_L0'] + 500, b['STAIR_MAINT_W']),
          ('STAIR_SERVICE', b['Z_Lm2'], b['Z_L0'], min(b['STAIR_SERVICE_L'], b['STAIR_SERVICE_W'])))
    pos = {'STAIR_P': (b['CORE_X'] + 1300, b['CORE_Y'] + 2400), 'STAIR_S1': (1500, wp - 1500),
           'STAIR_S2': (lp - 1500, 1500), 'STAIR_MAINT': (b['CORE_X'] + 3450, b['CORE_Y'] + 4600),
           'STAIR_SERVICE': (b['STAIR_SERVICE_X'] + 1200, b['STAIR_SERVICE_Y'] + 1800)}
    rows = []
    bad = 0
    for name, z, use, f, frac in lv:
        occ = math.ceil(a * frac / f)
        s = [n for n, za, zb, w in st if za <= z <= zb]
        need_w = max(1118, float('7.6') * occ)
        cl = min(((w - 300) / 2 if w >= 2400 else w - 150) for n, za, zb, w in st if n in s) if s else 0
        corners = ((0, 0), (lp, 0), (0, wp), (lp, wp))
        td = max(min(abs(cx - pos[n][0]) + abs(cy - pos[n][1]) for n in s) for cx, cy in corners) / 1000 if s else float('inf')
        ok = len(s) >= 2 and cl >= need_w and td <= 76
        bad += not ok
        rows.append((name, z / 1000, use, occ, ', '.join(s) or '-', len(s), need_w, cl, td, 'pass' if ok else 'FAIL'))
    h_above = b['Z_ROOF'] / 1000
    per = 2 * (lp + wp) / 1000
    uw, ur = float('0.534'), float('0.199')
    dt = 21 - float('-7.2')
    ua = uw * per * h_above + ur * a
    q = ua * dt / 1000
    md = ['# Enclosure, floor plates, stairs and egress', '', 'Document number: AQS-BLD-018', 'Revision: B', 'Date: 2026-10-25',
          'Authority: AQS-PLAN-007 task X-BLD-05; method of AQS-EGR-001; assumption A-M-213. Generated by `docs-authority/_egress_env.py`; do not edit this page by hand. Study; this page is not stamped by a Professional Engineer (PE).', '',
          '| Rev | Description | Date |', '|---|---|---|', '| A | First issue | 2026-10-16 |',
          '| B | Purpose and scope added; text rewritten to the documentation style guide (AQS-DOC-002). No level, stair or value changed. | 2026-10-25 |', '',
          '## 1. Purpose and scope', '',
          'This page checks that every level of the plant building can be evacuated, and states the construction of the floors and of the outer '
          'envelope. Egress is the route by which occupants leave a building in an emergency. For each level the check counts the occupants, '
          'the stairs that serve the level, the stair width needed and provided, and the longest travel distance to a stair. It then gives the '
          'floor plate construction and the heat loss through the envelope.', '',
          '## 2. Egress from each level', '',
          'A level passes if it is served by at least two stairs, if the clear width of every flight is at least the width needed, and if the '
          'travel distance from the farthest corner of the plate to the nearest stair is no more than 76 m. The width needed is the larger of '
          '1118 mm and 7.6 mm for each occupant. Table 2.1 gives the result for each level; z is the floor elevation.', '',
          'Table 2.1. Egress by level', '',
          '| Level | z m | Use | Occupants | Stairs serving | Exits | Stair width needed mm | Clear provided mm | Travel to stair m (limit 76) | Result |', '|---|---|---|---|---|---|---|---|---|---|']
    md += [f'| {aa} | {bb:.1f} | {cc} | {dd} | {ee} | {ff} | {gg:.0f} | {hh:.0f} | {ii:.1f} | {jj} |' for aa, bb, cc, dd, ee, ff, gg, hh, ii, jj in rows]
    md += ['', ('No level fails the check.' if not bad else f'{bad} levels fail the check.'),
           '', 'Two changes were made to the model at revision A to pass the check. First, the stair boxes were widened from 2400 mm to 2600 mm (STAIR_BOX) '
           'and STAIR_MAINT from 1200 mm to 1300 mm, so that each flight has 1150 mm clear; IBC 1011.2 requires 1118 mm, and the old 2400 mm box gave '
           '1100 mm. Second, STAIR_P and STAIR_S1 were extended to the roof (`models/freecad/building_stack.py`). Before this, the stairs stopped 2 m '
           'above L2, and the reservoir levels R1 to R3 and the roof had no stair.',
           '', '## 3. Floor plates', '',
           f'Every suspended level is a {b["SLAB_THK"]} mm concrete slab carried on the steel beams of AQS-BLD-016, over the {lp / 1000:.0f} x {wp / 1000:.0f} m plate ({a:.0f} m2). '
           'The reservoir floors and walls are water-retaining concrete to ACI 350. Level L-2 bears on the foundation mat of AQS-BLD-017. The floors have a '
           'fire-resistance rating of 2 h between levels (AQS-HSE-001) and 3 h between the life-support levels and the process levels.',
           '', '## 4. Enclosure', '',
           f'Above grade the walls are insulated metal panels with a thermal transmittance (U-value) of {uw} W/m2K, over a perimeter of {per:.0f} m and a height of '
           f'{h_above:.1f} m. The roof has an area of {a:.0f} m2 and a U-value of {ur} W/m2K. Both values meet IECC 2021 section C402 for climate zone 3. The product of '
           f'U-value and area (UA) for the envelope is {ua:,.0f} W/K, which gives a design heat loss of {q:.1f} kW at a temperature difference of {dt:.1f} K (the 99.6 % winter '
           'design condition of AQS-SITE-002).',
           '', 'Below grade the basement walls are cast concrete, waterproofed and drained to the CATCH_TANK sump (AQS-BLD-017).']
    return ('\n'.join(md) + '\n').encode('utf-8')


# ---- AQS-SAF-005: fire protection and detection (FIRE_PROTECTION.md) -----------

def render_fire_protection(m, inputs):
    """docs-authority/FIRE_PROTECTION.md: the v1 _fire.py template over the
    fire book (functions/fire_book), the building book, and the in-memory
    rebuild of the receiver design and relief bases (the v1 rebuild over a
    copied node map; the model is not touched). The --write graph stamp of the
    v1 stage is a separate mode the pipeline stage does not run."""
    d = _drv_of(inputs)
    g_prof = _gravity(inputs)
    p_process = _p_process_kPa(inputs)
    b = _BLD.building_book(m, d, g_prof)
    plate = b['PLATE_L'] * b['PLATE_W'] / 1000000
    rows, vf = _FB.demand(d, plate)
    h = b['HYDRO']
    zs = _FB.zones(d)
    sup = _FB.supply(d, rows, vf, g_prof * h['z_res0_m'])
    nodes = _node_view(m)
    mg = _drv(d, 'press_design_margin')
    win = _drv(d, 'ely_window_h')
    fake_nodes = [dict(n, params=dict(n.get('params') or {})) for n in m.data['nodes']
                  if n['unit_id'] in _FB.GAS_FIRE]                               # receivers.design() writes store books on its copy
    rr = _RC.design(d, {'nodes': fake_nodes, 'edges': m.data['edges']})
    gas = _FB.gas_book(d)
    fire_rows = []
    for u in _FB.GAS_FIRE:
        c = gas[u]
        p = nodes[u]['params']
        des = c['P_bar'] * mg * 100
        w_kg_h = sum((e['rate']['value'] or 0) / (win if e['from_unit_id'] == 'H2O_ELYZ' else 24)
                     for e in m.data['edges'] if e['to_unit_id'] == u and e['presence'] == 'present'
                     and (e['rate'] or {}).get('unit') == 'kg/d')
        p1 = float('1.10') * des + p_process
        rb = {'P1_kPa_abs': round(p1, 1), 'T_K': c['T_K'], 'M_kg_kmol': c['M'], 'k': c['k'], 'Z': c['Z'],
              'W_kg_h': round(w_kg_h, 4),
              'bore_req_mm': round(equiv_bore_mm(gas_area_in2(w_kg_h * float('2.20462'), c['k'], p1 / float('6.894757'),
                                                              c['T_K'] * float('1.8'), c['Z'], c['M'])), 2)}
        p_local = dict(design=rr[u], design_kPa=round(des, 1), relief_basis=rb)
        fc = _FB.receiver_fire(p_local, p_process)                              # no stored fire_case: rebuilt fresh, as v1
        relief_mm = float(math.ceil(max(rb['bore_req_mm'], fc['bore_req_mm_per_half'])))
        fire_rows.append(f"| {u} | {rr[u]['tubes']} | {fc['exposed_m2']:.1f} | {fc['P1_kPa_abs']:.0f} | {fc['T1_K']:.0f} | "
                         f"{fc['A_req_mm2_per_half']:.1f} | {fc['bore_req_mm_per_half']:.1f} | {rb['bore_req_mm']} | {relief_mm:.0f} | "
                         f"{fc['depress_kg']:.1f} | {fc['depress_bore_mm']:.2f} |")
    gv = max(rows, key=lambda r: r['V_m3'])
    md = ['# Fire protection and detection', '', 'Document number: AQS-SAF-005', 'Revision: B', 'Date: 2026-10-20',
          'Authority: AQS-PLAN-007 X-SAF-05 and X-FIR-01. Generated by `docs-authority/_fire.py`. Study; the fire engineer of record confirms hazard '
          'classes and hydraulics. Rev A A-M-188; rev B: sprinkler zone map, pipe schedule class and the fire-water tank and fire pump as drivers '
          '(`flow_graph/param/drivers.json` fire_* keys, NFPA13_2025 / NFPA20_2025 / NFPA22_2023).', '',
          '| Rev | Description | Date |', '| --- | --- | --- |',
          '| A | Sprinkler demand per level, two water supplies, detection, receiver fire cases. | 2026-10-16 |',
          '| B | X-FIR-01: hazard zone map (density/class per zone), pipe schedule class, fire-water tank and fire pump sized from the drivers basis; '
          'hazard class flagged pending the owner hall programme; graph fire params stamped. | 2026-10-20 |', '',
          '## Sprinkler demand (NFPA13_2025 density/area, Table 19.2.3.1.1 hose allowance)', '',
          '| Level | Occupancy | Hazard | Density mm/min | Area m2 | Sprinklers L/min (+10 %) | Hose L/min | Duration min | Volume m3 |', '|---|---|---|---|---|---|---|---|---|']
    md += [f"| {r['level']} | {r['occ']} | {r['hazard']} | {r['density']} | {r['area']:.0f} | {r['sprink_Lmin']:.0f} | {r['hose_Lmin']:.0f} | "
           f"{r['dur_min']:.0f} | {r['V_m3']:.0f} |" for r in rows]
    md += ['', f"Governing: {gv['level']} {gv['hazard']}, {gv['sprink_Lmin'] + gv['hose_Lmin']:.0f} L/min for {gv['dur_min']:.0f} min = {vf:.0f} m3.", '',
           '## Hazard zones (X-FIR-01; NFPA13_2025 class per zone, flagged pending the owner hall programme)', '',
           'Zones refine the level roll-up where the hazardous-area release sources (AQS-ELEC-009) and the hazard separation layout (AQS-SAF-007) make a zone differ from its level class:', '',
           '| Zone | Level | Hazard class | System | Density mm/min | Design area m2 | Sprinklers L/min | Hose L/min | Duration min |', '|---|---|---|---|---|---|---|---|---|']
    md += [f"| {z['zone']} | {z['level']} | {z['hazard']} | {z['system']} | {z['density']} | {z['area']:.0f} | {z['sprink_Lmin']:.0f} | "
           f"{z['hose_Lmin']:.0f} | {z['dur_min']:.0f} |" for z in zs]
    md += ['Zone classes and densities come from `drivers.json` `fire_zone_hazard` / `fire_nfpa13_hazards` (NFPA13_2025 ch. 19 curves); the hazard '
           'classification stays flagged pending the owner hall programme (X-FIR-01 Done-when). '
           f"The governing zone demand equals the governing level (L0 EH1): {sup['demand_Lmin']} L/min sprinklers + hose.", '',
           '## Pipe schedule and hydraulics (NFPA13_2025)', '',
           f"{sup['pipe']}. Riser and feed mains sized at the governing {sup['demand_Lmin']} L/min at 6 m/s class: "
           f"bore {math.sqrt(4 * sup['demand_Lmin'] / 60000 / math.pi / 6) * 1000:.0f} mm -> "
           f"DN{math.ceil(math.sqrt(4 * sup['demand_Lmin'] / 60000 / math.pi / 6) * 1000 / 50) * 50} riser; "
           'branch mains per zone at the zone demand on the same velocity class. The pipe-schedule method of NFPA 13 ch. 7 is not used: it does not '
           'serve extra-hazard occupancies and the L0 zones are EH1. '
           f"Hydraulic calculation from the riser through the hydraulically most remote area stays with the fire engineer of record (the "
           f"{_drv(d, 'fire_pump_head_margin_kPa')} kPa design margin of `fire_pump_head_margin_kPa` carries it).", '',
           '## Fire water tank and fire pump (NFPA22_2023 / NFPA20_2025, drivers fire_* keys)', '',
           f"1. Tank (gravity supply): {sup['tank']}. Primary: {sup['governing_V_m3']:.0f} m3 fire reserve held as dead storage in the bottom of the water tower, "
           f"below the hydro outlet nozzles, so a hydro discharge can never draw it; static head at L0 {h['z_res0_m']:.1f} m ({g_prof * h['z_res0_m']:.0f} kPa), "
           f"at the top life floor {h['z_res0_m'] - (b['Z_L2'] - b['CLEAR_L1']) / 1000:.1f} m. Refill of the reserve within {sup['refill_h']} h (`fire_tank_refill_h`, registered).",
           f"2. Pump (boosted supply): {sup['pump']}. Rated {sup['rated_Lmin']} L/min (listed step over the governing {sup['demand_Lmin']} L/min incl. hose allowance) at "
           f"{sup['rated_head_kPa']} kPa (static shortfall + `fire_pump_head_margin_kPa`); churn <= {sup['churn_max_kPa']} kPa "
           f"({_drv(d, 'fire_pump_churn_frac'):.2f} x rated, NFPA 20 4.16); runout {sup['runout_Lmin']} L/min at >= {sup['runout_head_min_kPa']} kPa "
           f"(NFPA 20 4.18, 150 % / 65 %); motor about {sup['pump_kW']} kW at the gravity-assisted head, jockey pump and weekly churn per NFPA 25.",
           'Two independent supplies per the redundancy rule: the tower gravity reserve and the CATCH_TANK suction source for the pump (the lower '
           'reservoir also takes the sprinkler run-off), so a fire after a hydro discharge still has a full supply in one of the two reservoirs (AQS-BLD-014).', '',
           '## Water supplies (two independent sources, redundancy rule)', '',
           f"1. Gravity: {vf:.0f} m3 fire reserve held as dead storage in the bottom of the water tower, below the hydro outlet nozzles (NFPA22_2023), "
           f"so a hydro discharge can never draw it. Static head at L0 {h['z_res0_m']:.1f} m ({g_prof * h['z_res0_m']:.0f} kPa), at the top life floor "
           f"{h['z_res0_m'] - (b['Z_L2'] - b['CLEAR_L1']) / 1000:.1f} m. The reserve is split across the cells; each cell has its own fire outlet, so one cell drained for inspection leaves the rest.",
           f"2. Pumped: the NFPA20_2025 fire pump above draws from CATCH_TANK (lower reservoir, {h['catch_depth_m'] * h['area_m2']:.0f} m3 when full; it also takes the "
           'sprinkler run-off) and is fed from the critical bus with the genset as its second supply. It boosts the gravity supply where hydraulics need more than the static head.',
           'The lower reservoir is sized to hold the hydro volume plus the fire reserve (AQS-BLD-014), so a fire after a hydro discharge still has a full supply in one of the two reservoirs.', '',
           '## Detection and special hazards (NFPA72_2025)', '',
           '| Area | Detection | Suppression |', '|---|---|---|',
           '| HAB, FARM | smoke detectors, NFPA 72 spacing; HAB sleeping rooms smoke alarms | wet sprinklers |',
           '| L0 shops, pyrolysis, oils | heat (rate-of-rise) and flame detectors at the reactor | wet sprinklers, EH1 |',
           '| Electrical rooms, rectifiers, inverters | air-sampling smoke detection | pre-action sprinklers (no water in the pipes until detection) |',
           '| ZNBR2 flow battery | smoke + H2 gas detection (purge basis, ess_tf) per NFPA855_2026 | wet sprinklers; the electrolyte is aqueous and not combustible |',
           '| H2 receiver CRYO_H2 | UV/IR flame + H2 gas detectors (alarm 10 %, trip 25 % LFL) per NFPA2_2026 | NFPA15_2027 water spray 10.2 L/min/m2 on the tube bank (exposure cooling); auto depressuring on flame |',
           '| O2 receiver CRYO_O2 | O2 enrichment detector (alarm 23.5 %) and flame | water spray as for H2; oxygen-clean (ASTM G93) |',
           '| CO2 store CRYO_CO2 | CO2 detector (5,000 ppm alarm) | water spray |',
           '| Cold box, L-1 wet process | heat detectors | wet sprinklers, OH2 |', '',
           '## Gas-receiver fire case (API521_2020, carried from X-SAF-04)', '',
           "Gas-filled tubes: A = F' A'/sqrt(P1), F' = 0.1406/(C Kd) (Tw - T1)^1.25 / T1^0.6625 (US units), Tw 1100 F (593 C), P1 at 121 % of set (fire overpressure). "
           'Liquid CO2: Q = 21,000 F A^0.82 Btu/h on the wetted tube area (drainage and fire-fighting present, F 1), relieved as vapour.', '',
           '| Receiver | Tubes | Exposed m2 | P1 kPa abs | T1 K | Fire area per half mm2 | Fire bore per half mm | Blocked-outlet bore mm | Installed bore mm (2 valves) | Depressuring release kg | Depressuring bore mm |', '|---|---|---|---|---|---|---|---|---|---|---|']
    md += fire_rows
    md += ['', 'The fire case governs every receiver: the earlier 3.3 mm bore covered only the blocked outlet. Each manifolded half now has its own relief valve '
           'sized for the fire on its tubes (bore in the table, propagated to the graph relief_mm and the relief register). For gas-filled tubes API 521 warns that a '
           'relief valve alone may not prevent wall rupture in a fire, because the unwetted wall heats and loses strength while the pressure stays near set. The H2 and '
           'O2 banks therefore get automatic depressuring on flame detection to 50 % of design gauge in 15 min (API 521 5.20, wall 13.5 mm), sized in the table at twice '
           'the average rate for the initial peak, plus NFPA 15 water spray to keep the tubes cool. The depressuring vents go to the same safe-location vent stacks as the relief valves.',
           '', 'Open for the fire engineer of record: hydraulic calculation from the riser to the hydraulically most remote sprinkler, hazard-class confirmation when the '
           'owner hall programme issues, and the site fire-department connection.']
    return ('\n'.join(md) + '\n').encode('utf-8')


# ---- AQS-SAF-006: gas detection (GAS_DETECTION.md + GAS_DETECTORS.csv) ---------

def render_gas_detection(m, inputs):
    """docs-authority/GAS_DETECTION.md: the v1 _gas_det.py template over the
    detector book (functions/gas_detection)."""
    rows = _GD.detector_rows(m)
    g, q = _GD.detector_summary(rows)
    md = ['# Gas detection', '', 'Document number: AQS-SAF-006', 'Revision: B', 'Date: 2026-10-25',
          'Authority: AQS-PLAN-007 X-SAF-06. Generated by `docs-authority/_gas_det.py`; detector list in `docs-authority/inventory/GAS_DETECTORS.csv`, '
          'carried into AQS-INV-004. Study. A-M-198.', '',
          '| Gas | Source units | Detectors | Detector | Mounting | Alarm | Trip |', '|---|---|---|---|---|---|---|']
    md += [f"| {k} | {g[k]} | {q[k]} | {v[1]} | {v[2]} | {v[3]} | {v[4]} |" for k, v in _GD.SP.items()]
    md += ['', f"{sum(q.values())} detectors at {len(rows)} source points. HF: no present gas edge carries HF; no HF source in the plant while fluoropolymer "
           'end-of-life stays held (Q-011, AQS-END-002). If Q-011 picks the HF scrubber route, HF detection is added at OIL_PYRO and the scrubber.',
           'Alarms go to the fire alarm panel (NFPA72_2025) and the HMI; trips go to the safety PLC (AQS-CTL-003). Calibration and bump test intervals are in '
           'AQS-OPS-002 (quarterly bump test, 6-monthly calibration, A-M-198).', '',
           '## 3. Per-unit detector detail', '', 'Table 3.1. Per-unit detector detail', '',
           '| Unit | Gas | Qty | Voting |', '|---|---|---|---|'] + [f"| {r['unit']} | {r['gas']} | {r['qty']} | {r['voting']} |" for r in rows]
    return ('\n'.join(md) + '\n').encode('utf-8')


def render_gas_detectors_csv(m, inputs):
    """docs-authority/inventory/GAS_DETECTORS.csv: the machine census the
    inventory_other family consumes (the v1 csv.DictWriter face, CRLF rows)."""
    rows = _GD.detector_rows(m)
    fields = list(rows[0])
    out = [','.join(fields)]
    out += [','.join(str(r[f]) for f in fields) for r in rows]
    return ('\r\n'.join(out) + '\r\n').encode('utf-8')


# ---- AQS-ASME-002: in-house code intent per unit (ASME_CODE_INTENT.md) ---------

_STAMP = {'Atmospheric': ('none (API 650/620 or DVS 2205 intent; no Code stamp)', 'fill test with water to the top of the shell'),
          'B31.3 piping component': ('none (piping carries no Certification Mark, ASME_B31_3)', 'hydrostatic 1.5 x design (ASME_B31_3 345.4.2); 341 examination'),
          'Machine casing (outside Section VIII)': ('none (part of the machine, ASME_VIII1_U1 U-1(c)(2)(c))', 'casing hydrotest 1.5 x design by the builder'),
          'Section VIII-1': ('U stamp by a Certificate Holder and NB registration if the jurisdiction requires (ASME_VIII1_UG UG-116)', 'hydrostatic 1.3 x MAWP (ASME_VIII1_UG UG-99(b))'),
          'Section VIII-1 (ID not yet sized)': ('U stamp pending size', 'UG-99(b) pending size')}


def render_asme_code_intent(m, inputs):
    """docs-authority/ASME_CODE_INTENT.md: the v1 _asme_class.py classification
    of every graph unit from its resolved design pressure, temperature and
    inside diameter (ASME_VIII1_U1 scope rules; X-MFG-40)."""
    rows = []
    for n in sorted(m.data['nodes'], key=lambda n: n['unit_id']):
        p = m.field('node', n['unit_id'], 'params')
        ds = p.get('design') or {}
        pres = p.get('design_kPa')
        t = ds.get('T_C')
        dd = ds.get('D_mm')
        tw = ds.get('wall_mm') or ds.get('t_nom_mm') or 0
        if pres is None and ds.get('P_MPa'):
            pres = float(ds['P_MPa']) * float('1000.0')                        # the A-M-283 poly design wave books P in design.P_MPa
        iid = (dd - 2 * tw) if dd else None
        u = n['unit_id']
        if pres is None:
            cls, why = 'not a vessel (no design pressure on the graph)', '-'
        elif pres <= float('103.0'):
            cls, why = 'Atmospheric', 'U-1(c)(2)(h): <= 103 kPa g'
        elif iid is not None and iid <= float('152.0'):
            cls, why = 'B31.3 piping component', f'U-1(c)(2)(j): ID {iid:.0f} mm <= 152 mm'
        elif iid is None:
            cls, why = 'Section VIII-1 (ID not yet sized)', f'{pres:.0f} kPa g > 103; size from its unit design'
        else:
            cls, why = 'Section VIII-1', f'{pres:.0f} kPa g, ID {iid:.0f} mm'
        rows.append((u, n.get('sector_id'), pres, t, iid, cls, why))

    def st(cl):
        return _STAMP.get(cl, ('-', '-'))

    c = collections.Counter(r[5] for r in rows)
    ph = [n['unit_id'] for n in m.data['nodes']
          if 'hold-up' in str(((n.get('params') or {}).get('relief_basis') or {}).get('design_case', ''))]
    md = ['# In-house code intent per unit', '', 'Document number: AQS-ASME-002', 'Revision: D', 'Date: 2026-10-25', '',
          '| Rev | Description | Date |', '|---|---|---|',
          '| B | Stamp and test requirement per unit (X-COD-03); EXPANDER machine-casing rule. | 2026-10-16 |',
          '| C | Design-pressure source extended to params.design.P_MPa (the A-M-283 poly design wave booked pressure there): POLY_OLEFIN reclassifies from '
          '"not a vessel" to B31.3 piping component (ID 142 mm <= 152 mm, U-1(c)(2)(j); UG-27 3.8 mm wall already checked in AQS-DUTY-073). | 2026-10-21 |',
          '| D | Rewritten to the documentation style guide (AQS-DOC-002): purpose and scope first, numbered sections and table titles. No class, stamp or test '
          'changed. | 2026-10-25 |', '',
          '## 1. Purpose and scope', '',
          'This page assigns every graph unit an in-house code class (atmospheric, piping component, machine casing, or Section VIII Division 1), with the stamp and '
          'pressure-test requirement that follows from the class. It is generated by `docs-authority/_asme_class.py` from the graph (design pressure from '
          '`params.design_kPa` or `params.design.P_MPa`, gauge; pressure cases from `flow_graph/param/pressure_nodes.py`). Authority: AQS-PLAN-007 X-MFG-40, which '
          'replaces the "Vendor" class of AQS-ASME-001 section 3. Study; no stamp is issued.',
          '',
          '## 2. Classification rules', '',
          'Rules from the Section VIII-1 scope (ASME_VIII1_U1): design pressure at or below 103 kPa g is outside Section VIII (atmospheric tanks); a vessel of inside '
          'diameter at or below 152 mm is outside Section VIII by size and is designed as a piping component (ASME_B31_3), with the UG-27 wall check already made in '
          'AQS-DUTY-062; everything else is Section VIII Division 1, designed in-house.', '',
          'Table 2.1. Unit count per class', '', '| Class | Units |', '|---|---|'] + [f'| {k} | {v} |' for k, v in sorted(c.items())] + ['',
          'Atmospheric design pressure is set from the actual cases by the vent stage (A-M-174): 4 x the open-vent dP for the vapour space plus the full-height '
          f'hydrostatic head at SG 1.25. {len(ph)} atmospheric units have no sized height yet; their liquid head comes from a hold-up volume (A-M-182: 2 d for stores, '
          '1 d for process units, H/D 1.5) until their unit sizing replaces it. Units with no liquid inflow carry the vapour case alone. Among the X-MFG-40 named units, '
          'GLASS_BURNOUT (rotary kiln), ALK_SCRUBBER, ZNBR2_BR2_REGEN (Br2 tower) and OIL_FRAC run at or near atmospheric pressure by process and stay atmospheric; the '
          'cold box CRYO_ASU does not: its compressor and column pressures are set by X-MFG-33 and it is reclassified when that design issues.', '',
          '## 3. Stamp and test requirement (X-COD-03)', '', 'Table 3.1. Stamp and pressure test per class', '',
          '| Class | Stamp | Pressure test |', '|---|---|---|'] + [f'| {k} | {st(k)[0]} | {st(k)[1]} |' for k in sorted(c) if k in _STAMP] + ['',
          f"Pressurised nodes needing a U stamp: {sum(1 for r in rows if r[5].startswith('Section VIII-1'))}. Every pressurised node is a B31.3 component or a machine "
          'casing, so no Code stamp is required; the jurisdictional review (Texas boiler and pressure vessel rules) is an X-COD-01 item.', '',
          '## 4. Per-unit schedule', '', 'Table 4.1. Code intent per unit', '',
          '| Unit | Sector | Design kPa g | Design T C | ID mm | Code intent | Basis | Stamp | Test |', '|---|---|---|---|---|---|---|---|---|']
    md += [f"| {u} | {s} | {'' if pres is None else f'{pres:.1f}'} | {'' if t is None else t} | {'' if iid is None else f'{iid:.0f}'} | {cl} | {w} | {st(cl)[0]} | {st(cl)[1]} |"
           for u, s, pres, t, iid, cl, w in rows]
    return ('\n'.join(md) + '\n').encode('utf-8')


# ---- AQS-RED-002: pumped-hydro reservoir siting trade study (HYDRO_SITING.md) --

_SITING_OPTIONS = (('A. Roof tank (present)', (18,), 'roof carries the full water mass'),
                   ('B. Elevated tank on a tower', (25, 30, 40, 50), 'tower + foundation carry the water mass; AWWA D100 wind/seismic'),
                   ('C. Hillside upper reservoir', (50, 100, 200), 'lined pond at grade on site terrain; penstock down the slope; no elevated mass'),
                   ('D. Surface upper + deep-shaft / cavern lower reservoir', (100, 200, 300, 500),
                    'upper pond at grade; lower reservoir excavated; shaft depth = head'))


def render_hydro_siting(m, inputs):
    """docs-authority/HYDRO_SITING.md: the v1 _hydro_siting.py trade study over
    the HYDRO_SET backup basis and the site gravity (Q-009 / X-RED-02,
    A-M-145)."""
    g = _gravity(inputs)
    b = m.field('node', 'HYDRO_SET', 'params')['backup_basis']
    e = b['energy_kWh_bus']
    eta = b['eta_turbine_generator']
    rho = float('1000.0')

    def vol(h):
        return e * 3600000 / (rho * g * h * eta)

    rows = []
    for name, hs, note in _SITING_OPTIONS:
        for h in hs:
            v = vol(h)
            m_water = v * rho / 1000
            dd = (4 * v / (float('3.1416') * 10)) ** float('0.5') if name[0] in 'AB' else (v / 5) ** float('0.5')
            rows.append((name, h, v, m_water, ('%.1f m dia x 10 m' % dd) if name[0] in 'AB' else ('%.1f m square x 5 m deep' % dd),
                         rho * g * h / 1000000, note))
    md = ['# Pumped-hydro reservoir siting trade study', '', 'Document number: AQS-RED-002', 'Revision: B', 'Date: 2026-10-16',
          'Authority: AQS-PLAN-007 X-RED-02, open question Q-009 (owner decision). Generated by `docs-authority/_hydro_siting.py`. Study.', '',
          f'Backup store {e:.0f} kWh at the bus (NFPA 111 Class X, {b["class_hours"]} h x {b["critical_kW"]} kW, A-M-145), turbine-generator {eta}. '
          'Volume V = E/(rho g h eta); doubling the head halves the water. Friction in the penstock is not yet taken off the head.', '',
          '| Option | Head m | Water m3 | Water t (load) | Reservoir shape | Penstock / casing pressure MPa | Structural note |', '|---|---|---|---|---|---|---|']
    md += [f'| {aa} | {h} | {v:.0f} | {mw:.0f} | {s} | {p:.2f} | {n} |' for aa, h, v, mw, s, p, n in rows]
    md += ['', 'Reading the table:',
           '- A on the roof needs the roof to carry about 11,400 t; not credible on the hall structure.',
           '- B moves the mass onto its own tower: at 40 m about 5,100 t on a dedicated foundation (AWWA D100 tank, ASCE 7 wind and seismic).',
           '- C needs no elevated mass; it needs site relief of the stated head within penstock reach. Site survey decides.',
           '- D puts the head below grade: at 300 m the lower reservoir is about 690 m3 of excavation plus the shaft, with a 2.9 MPa casing and penstock. It is '
           'site-independent of terrain but depends on geology.',
           '', 'Owner decision (Q-009 closed 2026-10-16): none of A-D. The top floors of the building are the upper reservoir (a water tower within the building, a '
           'parametric form of B on the building structure) and CATCH_TANK is the lower reservoir. Sizing, loads, egress and roof PV are in AQS-BLD-014 '
           '(WATER_TOWER.md, A-M-187).']
    return ('\n'.join(md) + '\n').encode('utf-8')


# ---- AQS-SAF-004: relief register (RELIEF_REGISTER.md) --------------------------

_PSV_STD = (float('6.0'), float('8.0'), float('10.0'), float('12.0'), float('15.0'))   # mm in-house PSV bores (DN15 body)


def render_relief_register(m, inputs):
    """docs-authority/RELIEF_REGISTER.md: the v1 _relief_register.py register -
    every pressurised node (design_kPa > 103 kPa g) with its API 520 case from
    the graph, plus the machine interstage relief valves of the H2 compressor
    (AQS-DUTY-067) and the cold-box CO2 compressor (AQS-DUTY-069)."""
    d = _drv_of(inputs)
    p_process = _p_process_kPa(inputs)
    nodes = _node_view(m)

    def stage_rows(rows, tag, stages, w_kg_h, mm, k):
        for s in stages:
            pset = float('1.10') * s['P_out_bar'] * 100
            p1 = pset * float('1.10') + p_process
            t = s['T_out_C'] + float('273.15')
            a = gas_area_in2(w_kg_h * float('2.20462'), k, p1 / float('6.894757'), t * float('1.8'), float('1.0'), mm)
            bore = equiv_bore_mm(a)
            rows.append((f"{tag} stage {s['stage']}", 'interstage PSV', round(pset - p_process, 1),
                         f"blocked discharge at {w_kg_h:.3f} kg/h, {s['T_out_C']:.0f} C", round(w_kg_h, 3), round(bore, 2),
                         next(x for x in _PSV_STD if x >= bore), True))

    rows = []
    for n in sorted(m.data['nodes'], key=lambda n: n['unit_id']):
        p = nodes[n['unit_id']]['params']
        pres = p.get('design_kPa')
        if not (pres and pres > 103):
            continue
        rb = p.get('relief_basis') or {}
        rows.append((n['unit_id'], 'vessel', pres, rb.get('case', '-').split('. ')[0][:90], rb.get('W_kg_h'),
                     rb.get('bore_req_mm'), p.get('relief_mm'), rb.get('adequate')))
    cd = nodes['CRYO_H2']['params'].get('compressor_design') or {}
    if cd:
        stage_rows(rows, 'H2 compressor', cd['stages'], cd['H2_kg_d'] / _drv(d, 'h2c_run_h'), float('2.016'), float('1.41'))
    cb = nodes['CRYO_ASU']['params'].get('design') or {}
    if cb.get('comp_ratio_per_stage'):
        r = cb['comp_ratio_per_stage']
        st = [dict(stage=i + 1, P_out_bar=r ** (i + 1), T_out_C=cb['comp_T_out_C']) for i in range(cb['comp_stages'])]
        stage_rows(rows, 'CO2 compressor', st, cb['feed_CO2_kg_d'] / 8, float('44.01'), float('1.29'))     # one bed over 8 h
    md = ['# Relief register', '', 'Document number: AQS-SAF-004', 'Revision: A', 'Date: 2026-10-16',
          'Authority: AQS-PLAN-007 X-SAF-04. Generated by `docs-authority/_relief_register.py` from the graph. Study; set points are design values, not stamped.', '',
          'Vessel cases come from the graph (write_graph relief, API520). Machine interstage valves: blocked discharge at the stage peak flow, set 1.10 x stage outlet, '
          '10 % overpressure, API 520 critical gas flow; in-house PSV bores 6-15 mm in a DN15 body. The CO2 compressor flow is the desorption peak (one bed of CO2 released over 8 h).', '',
          '| Item | Kind | Set / design kPa g | Case | W kg/h | Bore req mm | Bore mm | Adequate |', '|---|---|---|---|---|---|---|---|']
    md += [f"| {aa} | {bb} | {cc} | {dd} | {ee if ee is not None else '-'} | {ff if ff is not None else '-'} | {hh} | {'yes' if ok else 'NO'} |"
           for aa, bb, cc, dd, ee, ff, hh, ok in rows]
    md += ['', f"{sum(1 for r in rows if r[1] == 'vessel')} pressurised vessels and {sum(1 for r in rows if r[1] != 'vessel')} interstage valves; all adequate. "
           'Atmospheric units are open-vented per API 2000 (A-M-155, A-M-174). Fire case on the gas receivers (API 521 unwetted vessel) is carried to X-SAF-05.']
    return ('\n'.join(md) + '\n').encode('utf-8')


# ---- AQS-TST-002: ZNBR2 stack test (ZNBR2_STACK_TEST.md) ------------------------

def render_znbr_stack_test(m, inputs):
    """docs-authority/ZNBR2_STACK_TEST.md: the v1 _znbr_test.py prediction and
    test plan from the znbr_* drivers (X-MFG-41, A-M-179)."""
    d = _drv_of(inputs)
    v = lambda k: _drv(d, k)
    e = v('znbr_cell_V')
    j = v('znbr_j_mA_cm2') / 1000
    eta = j * v('znbr_ASR_ohm_cm2')
    ve = (e - eta) / (e + eta)
    her = v('znbr_her_mL_h_cm2') / 1000 / float('24.465') * 2 * 96485 / 3600 / j       # fraction of charge current, 25 C molar volume
    ce = 1 - her - v('znbr_crossover_loss')
    rt = ve * ce * (1 - v('znbr_aux_frac'))
    md = ['# Zinc-bromide battery stack test', '', 'Document number: AQS-TST-002  ', 'Revision: B  ', 'Date: 2026-10-24  ',
          'Basis: AQS-PLAN-007 task X-MFG-41; assumption A-M-179, which replaces the battery-vendor basis of A-M-062.  ',
          'Source: generated by `docs-authority/_znbr_test.py`. Do not edit by hand.', '',
          '| Rev | Description | Date |', '|---|---|---|', '| A | First issue | 2026-10-16 |',
          '| B | Rewritten to DOC_STYLE (AQS-DOC-002) for a reader new to the project: purpose, scope and terms, captions. Prediction, procedure and acceptance '
          'unchanged. | 2026-10-24 |', '',
          '## 1. Purpose and scope', '',
          'The plant stores energy in an in-house zinc-bromide flow battery (`ZNBR2`). Its round-trip efficiency is predicted from published cell data, not measured. '
          'This test builds one stack to the plant cell design and measures the values the prediction rests on, so that they can replace the assumptions. It covers the '
          'prediction, the test article, the procedure and the acceptance. It does not cover the battery installation.', '',
          '## 2. Terms', '',
          '- ASR: area-specific resistance of a cell, in ohm cm2; it sets the voltage loss at a given current density.',
          '- Coulombic efficiency: charge out divided by charge in.', '- Voltage efficiency: mean discharge voltage divided by mean charge voltage.',
          '- Round trip: energy out divided by energy in, including pumps.',
          '- HER: hydrogen evolution reaction, the side reaction that wastes charge on the zinc electrode.',
          '- Strip cycle: a full discharge that removes all plated zinc.', '', 'Other abbreviations are in `docs-authority/GLOSSARY.md`.', '',
          '## 3. Prediction', '',
          f"Voltage efficiency (1.82 - {eta:.3f})/(1.82 + {eta:.3f}) = {ve:.3f} at 20 mA/cm2 and {v('znbr_ASR_ohm_cm2')} ohm cm2 (SAND2000-0893, ZBFB_REVIEW2023; "
          f"ASR assumed). Coulombic efficiency 1 - HER {her:.4f} - crossover {v('znbr_crossover_loss')} = {ce:.3f}. Auxiliaries {v('znbr_aux_frac') * 100:.0f} %. "
          f"Predicted round trip {rt:.3f}. The design value stays {v('storage_round_trip')} until the test; the gap ({(rt - v('storage_round_trip')) * 100:.0f} points) "
          'is margin, not credit.', '',
          '## 4. Test article', '',
          'One in-house 10-cell stack built to the ZNBR2 cell design (same electrode, separator, flow frame and current density), 0.1 m2 per cell, with its own '
          'electrolyte loop and Br2 complexing agent.', '',
          '## 5. Procedure', '',
          '1. Leak and hydrostatic test of the flow frames at 1.5 x pump shut-off pressure.',
          '2. Formation: three charges at 10 mA/cm2 to 50 % zinc loading.',
          '3. Polarisation: charge and discharge at 5, 10, 20, 30 and 40 mA/cm2 at 50 % state of charge; cell voltages logged at 1 Hz; ASR from the slope.',
          '4. Daily cycle: 30 cycles of 6 h charge at 20 mA/cm2 and discharge over the 14 h night at the matching current, 25 C and 40 C electrolyte.',
          '5. Self-discharge: 24 h open circuit at full charge; coulombs lost and H2 collected in a gas burette.',
          '6. Strip cycle: full zinc strip every 5 cycles, as the plant will run it.',
          '7. Auxiliaries: pump and controller power logged over the cycles.', '',
          '## 6. Measurements and acceptance', '', 'Table 6.1. Measurements', '',
          '| Quantity | Method | Prediction | Feeds |', '|---|---|---|---|',
          f"| ASR | polarisation slope | {v('znbr_ASR_ohm_cm2')} ohm cm2 | znbr_ASR_ohm_cm2 |",
          f"| Coulombic efficiency | Ah out / Ah in per cycle | {ce:.3f} | znbr_crossover_loss |",
          f"| H2 evolution | gas burette, charge and open circuit | {v('znbr_her_mL_h_cm2')} and {v('znbr_oc_corr_mL_h_cm2')} mL/h/cm2 | znbr_her_mL_h_cm2, ZNBR2 purge |",
          f"| Round trip | Wh out / Wh in including pumps, mean of cycles 11-30 | {rt:.3f} | storage_round_trip |",
          '| Derate | capacity fade over 30 cycles extrapolated to 20 years with strip cycling | none assumed | ZNBR2 kWh |', '',
          'Acceptance: the measured round trip replaces storage_round_trip and the plant re-sizes PV and storage through the pipeline. A round trip below 0.65 or fade '
          'above 1 % per 30 cycles is a design review.']
    return ('\n'.join(md) + '\n').encode('utf-8')


# ---- the module DOCS list (the declared registry block, census order) ----------

DOCS = [
    ('docs-authority/HALL_EGRESS.md', render_hall_egress),
    ('docs-authority/WATER_TOWER.md', render_water_tower),
    ('docs-authority/ENCLOSURE_EGRESS.md', render_enclosure_egress),
    ('docs-authority/FIRE_PROTECTION.md', render_fire_protection),
    ('docs-authority/GAS_DETECTION.md', render_gas_detection),
    ('docs-authority/inventory/GAS_DETECTORS.csv', render_gas_detectors_csv),
    ('docs-authority/ASME_CODE_INTENT.md', render_asme_code_intent),
    ('docs-authority/HYDRO_SITING.md', render_hydro_siting),
    ('docs-authority/RELIEF_REGISTER.md', render_relief_register),
    ('docs-authority/ZNBR2_STACK_TEST.md', render_znbr_stack_test),
]

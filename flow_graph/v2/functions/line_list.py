"""The line-list namespace family (family migration; reference writer
docs-authority/_line_list.py, ledger row `line_list`, section E, RENDER
"becomes-renderer" - the chain brief splits the compute half here because the
placement_routes, nozzle_sched and pid_sheets stages execute this namespace:
v1 ran it via `runpy docs-authority/_line_list.py` and read its module-level
`C` and `rows`).

AQS-PIP-004: every graph edge gets a line-list row - DN by velocity (PERRY9
sec. 6, d = sqrt(4 Q / (pi v)); edge `line_DN` overrides, heat-loop kW edges
size as water at the loop swing), pipe class by the AQS-STD-002 Rev L
section 12 service families (X-MAT-01, AQS-PIP-003 Rev A letters; the
fluoro/dopant/molten/brine families carry per-duty-sheet materials and class
"-" pending PIP-003 Rev B), length as the orthogonal distance between unit
centres x 1.2, and the route text naming both centres' sources.

Pure kernels, no graph state (the rows are renderer-lane data; nothing stamps
the graph), so this module registers no solve function - the scale_down
kernel precedent.

Read model: the plain committed-graph structure (the seed, verbatim - the
file every chain stage read) and two payloads read at the caller's I/O
boundary:
- inputs['line_positions']: the unit-centre namespace C, {unit_id:
  ([x, y, z] mm, source)} - the C dict the v1 stage built at module level from
  docs-authority/duties/_origins.json (duty origins), flow_graph/
  placement_report.json (moves + create_moves), flow_graph/placement_study.json
  (STUDY rows), flow_graph/placement_seed.json (issued units, then block
  centres), models/freecad/params.py RELOCATE (the GA rev C relocation,
  A-M-215), docs-authority/inventory/CAD_MOVES.json (the GA rev C2 overlap
  moves, A-M-220/222), and the EVAP_ACID_VS ride on the EVAP_ACID frame
  (X-PAR-10). The declared payload builder reproduces that build order
  verbatim (the inventory wave declares the same key for its censuses). The
  DEPRECATED duties-markdown fallback (U2a: runs only while _origins.json is
  absent) is the payload builder's concern and is not ported here.
- inputs['drivers']: the drivers the DN sizing reads (water_cp_kJ_kgK,
  heat_loop_dT_K, line_velocity_liquid_m_s, line_velocity_gas_m_s,
  line_min_DN, slurry_min_DN); the v1 DR.val read over the same file.

Float doctrine: the reference writer solves in float space ('%g' cells,
round(L, 1) lengths, a float velocity bore chain), so this is a float replica
of that chain over the same plain books - no float literals (the lint holds
this); the constants enter as the decimal strings of the v1 literals (the
orthogonal factor 1.2, the gas densities 0.09/1.2 kg/m3, the liquor densities
1100/1000 kg/m3, the 0.5 mol fraction split, the 0.97 water cut and the 60 C
PVC-U class limit). The v1 stdout ledger ("BIG" oversized-line warnings) is
session output, not a document, and does not port; its dn=500 fallback does.
Pure: no I/O, no wall-clock, no RNG.

Golden (test_render_line_list.py): the committed docs-authority/LINE_LIST.md
- byte-exact through the render lane - and, as the bridge contract, the rows
here equal the reference writer's own namespace (runpy of _line_list.py, whose
document write sits under its __main__ guard) on the committed tree.
"""
import math

# ---- the standard DN ladder and its bore table (the v1 literals) -------------
DN = (15, 20, 25, 32, 40, 50, 65, 80, 100, 150, 200, 250, 300, 400, 500)
ID = {15: float('15.8'), 20: float('20.9'), 25: float('26.6'), 32: float('35.1'),
      40: float('40.9'), 50: float('52.5'), 65: float('62.7'), 80: float('77.9'),
      100: float('102.3'), 150: float('154.1'), 200: float('202.7'), 250: float('254.5'),
      300: float('303.2'), 400: float('381.0'), 500: float('477.8')}          # mm, the v1 bore table
ORTH = float('1.2')                                                            # the orthogonal route factor, x 1.2
MM_PER_M = 1000
SEC_PER_DAY = 86400
RHO_GAS_H2 = float('0.09')          # kg/m3, hydrogen-rich gas book
RHO_GAS = float('1.2')              # kg/m3, the process-gas book
RHO_ACID = float('1100.0')          # kg/m3, HCl-carrying liquor
RHO_WATER = float('1000.0')         # kg/m3, aqueous liquor
H2_SPLIT = float('0.5')             # mol fraction: above this a gas books as H2
WATER_CUT = float('0.97')           # composition water fraction of the P5 family
PVC_U_LIMIT_C = 60                  # PVC-U service ceiling, C (class rule)

# the thermoplastic unit families (the v1 PL map; AQS-PIP-003 unit picks)
_PL_TEXT = ('BMED_ACID BMED_BASE POLISH_BANK CONTINUOUS_RECYCLE CRU SALT_FEED S13_CLASS_TREAT WS_KOH '
            'WS_PHOS WS_AMMONIA WET_BENCH GREY_TREAT BLACK_DIGEST MEOH_FERM MET_SCRUB ALK_SCRUBBER '
            'CATCH_TANK ROOF_TANK REMIN ZNBR2_BR2_REGEN EW_2 EW_3 EW_4 EW_5 EW_6 EW_7 EW_8 EW_9')
PL = {u: 'PVC-U' for u in _PL_TEXT.split()}
PL.update({u: 'CPVC' for u in 'LEACH_CSTR_1 FLOAT_SINK EW_1 ACID_POLISH_SCRUB NOX_SCRUB'.split()})
PL.update({u: 'PVDF' for u in 'HX8 WS_NITRIC WS_PEROX HNO3 WS_HF_ED'.split()})
WATER = set('ROOF_TANK CATCH_TANK TERRACE_IRRIG GROW_BED HABITATION HAB_WASH CROP_TOMATO REMIN '
            'NUTRIENT_DOSE HYDRO_SET FAB_UPW_TANK'.split())
# AQS-STD-002 Rev L section 12 (X-MAT-01) service families governed by issued
# per-unit duty-sheet materials; no AQS-PIP-003 pipe class yet
FLUORO = {'HF_GEN', 'VDF_SYN', 'TFE_SYN', 'POLY_F', 'F_RECOVER', 'PELLET', 'POWDER_RESIN',
          'FILM_CAST', 'POLY_STOCK'}
HYDRO = {'OIL_PYRO', 'OIL_FRAC', 'PROD_C5_C10', 'PROD_C11_C18', 'PROD_C19_C28', 'PROD_C29',
         'C29_RECYCLE', 'POLY_OLEFIN', 'WAX_PATTERN', 'GREASE_CA', 'GREASE_LI'}


def min_id_mm(m_kg_s, rho_kg_m3, v_m_s):
    """Velocity bore, mm [PERRY9 sec. 6]: d = sqrt(4 Q / (pi v)); the v1
    sizing/lines.py expression, ported natively (same float chain)."""
    return math.sqrt(4 * m_kg_s / rho_kg_m3 / (math.pi * v_m_s)) * 1000


def rho(e):
    """The density book of an edge's fluid, kg/m3 (the v1 rho())."""
    ph = e.get('phase')
    comp = e.get('composition') or {}
    if ph == 'G':
        return RHO_GAS_H2 if comp.get('H2', 0) > H2_SPLIT else RHO_GAS
    return RHO_ACID if comp.get('HCl') else RHO_WATER


def cls(e):
    """The AQS-PIP-003 Rev A pipe class and its service-family text (the v1
    cls(), keyed to the AQS-STD-002 Rev L section 12 families, X-MAT-01)."""
    a, b = e['from_unit_id'], e['to_unit_id']
    p = e.get('params') or {}
    T = p.get('T_C') if isinstance(p.get('T_C'), (int, float)) else None
    comp = e.get('composition') or {}
    car = (e.get('carries') or '').lower()
    sid = e['stream_id']
    ph = e.get('phase')
    if sid.startswith('HL-Q1') or sid.startswith('HL-Q2') or '-Q1-' in sid or '-Q2-' in sid:
        return 'M2', 'Q1/Q2 thermal oil'
    if sid.startswith('HL-') or 'Q3' in sid or 'Q4' in sid:
        return 'M1', 'Q3/Q4 water loop'
    if sid == 'IA-FLUE-QUENCH':
        return 'P5', 'quench water'
    if sid == 'IA-H2SO4-MU':
        return 'M2', '98 wt% H2SO4 make-up; carbon steel passivates above 93 wt% and at ambient (PERRY9_MAT)'
    if sid == 'S36':
        return '—', 'dopant concentrates (BBr₃/POCl₃ class): PTFE/PFA handling; class pending PIP-003 Rev B'
    if 'mgcl' in car or 'cacl' in car:
        if sid == 'IA-MGCL2-KROLL':
            return '—', ('molten MgCl2 salt return (Kroll retort to MG_POT, ~700 C): graphite/Ni-200 wetted '
                         'launder per AQS-STD-006 (AQS-STD-002 section 12.2)')
        return '—', ('CaCl2/MgCl2 brine concentrate import (ambient legs): PVDF wetted handling per '
                     'AQS-STD-006 (AQS-STD-002 section 12.2)')
    if ph != 'G' and ('meoh' in car or 'methanol' in car):
        return 'M1', 'wet methanol service (316L per unit duty sheets)'
    if 'slurry' in car:
        return 'P4', 'alkaline silica slurry (PP-H; SIMONA class data)'
    if 'geothermal' in car or sid == 'S43':
        return 'P5', 'propylene-glycol ground loop (HDPE DR-11 per node design)'
    if ph != 'G' and ('melt' in car or 'molten' in car):
        return '—', 'molten metal launder/pour (not piped)'
    if 'HF' in sid or 'PVDF' in car or [x for x in (a, b) if PL.get(x) == 'PVDF'] \
            or 'nitric' in car or 'perox' in car:
        return 'P3', 'oxidizer, HF or PVDF unit'
    if a in FLUORO or b in FLUORO:
        return '—', ('fluoro synthesis train; shell materials per duty sheets (Hastelloy C-276, Ni, '
                     'Inconel 600); class pending PIP-003 Rev B')
    if a == 'HDR_H2' or b == 'HDR_H2':
        return 'P1', 'wet acid H2 + sweep air header (PVC-U; AQS-REV-H2-001 M3, X-MAT-06)'
    if ph == 'G':
        if comp.get('H2', 0) > H2_SPLIT or 'H2' in sid or comp.get('O2', 0) > H2_SPLIT \
                or a.startswith('CRYO') or b.startswith('CRYO') or a.startswith('HDR_'):
            return 'M1', 'dry gas, H2/O2/N2/CO2'
        if 'FLUE' in sid or 'FLUE' in a or 'FLUE' in b or 'NOX' in b or 'SCRUB' in b:
            return 'F1', 'flue or acid gas'
        return 'P3', 'process vent gas'
    m = [PL[x] for x in (a, b) if x in PL]
    if (T and T > PVC_U_LIMIT_C) or 'CPVC' in m:
        return 'P2', 'hot leach liquor'
    if 'naoh' in car or 'koh' in car or 'base' in car:
        return 'P4', 'alkaline'
    if 'PVC-U' in m:
        return 'P1', 'acid or brine, at or below 60 C'
    if a in WATER or b in WATER or comp.get('water', 0) >= WATER_CUT and not comp.get('HCl'):
        return 'P5', 'water'
    if ph in ('L', 'S/L', 'L/G') and (a in HYDRO or b in HYDRO or 'wax' in car or 'hydrocarbon' in car):
        return 'M2', 'hydrocarbon product, fuel or wax cut (carbon steel per unit duty sheets; dry)'
    if any(x in car for x in ('oil', 'solvent', 'ethanol', 'butanol')):
        return 'M1', 'organic liquid (316L per unit duty sheets)'
    return 'P1', 'aqueous process liquor (AQS-ASSAY-001 envelope)'


def _dn_of(e, drv):
    """The DN book of one edge: edge `line_DN` override, else the velocity
    chain (heat-loop kW as water at the loop swing; mass at the phase
    velocity). Returns (dn, basis). The v1 stdout BIG ledger does not port;
    its dn=500 fallback does."""
    u = (e.get('rate') or {}).get('unit')
    ph = e.get('phase')
    p = e.get('params') or {}
    if p.get('line_DN'):
        return int(p['line_DN']), 'edge line_DN'
    val = (e.get('rate') or {}).get('value')
    if u == 'kW':
        cp, dT = drv['water_cp_kJ_kgK']['value'], drv['heat_loop_dT_K']['value']
        mw_ = (val or 0) / (cp * dT)                       # kg/s water, INCROPERA7 / ASHRAE_SYS2020
        need = min_id_mm(mw_, float('1000.0'), drv['line_velocity_liquid_m_s']['value']) if mw_ > 0 else 0
        dn = next((d for d in DN if ID[d] >= need and d >= drv['line_min_DN']['value']), None) or 500
        return dn, f'heat loop {val:g} kW at ΔT {dT:g} K, 1 m/s'
    m = (val or 0) / SEC_PER_DAY
    r = rho(e)
    v = drv['line_velocity_gas_m_s']['value'] if ph == 'G' else drv['line_velocity_liquid_m_s']['value']
    need = min_id_mm(m, r, v) if m > 0 else 0
    mn = drv['slurry_min_DN']['value'] if ph in ('S/L', 'L/S') else drv['line_min_DN']['value']
    dn = next((d for d in DN if ID[d] >= need and d >= mn), None)
    if dn is None:
        dn = 500                                           # the oversized-line fallback (the v1 BIG ledger)
    return dn, f'velocity {v:g} m/s, ρ {r:g}; min DN{mn}'


def length_m(ca, cb):
    """Orthogonal centre distance x 1.2, m (A-M-065: the v1 length book)."""
    return round(sum(abs(ca[0][i] - cb[0][i]) for i in range(3)) / MM_PER_M * ORTH, 1)


def route_text(a, b, ca, cb):
    """The route cell: the orthogonal rule naming both centres' sources, or
    the named gap (no invented mm - AQS-3D-BUILD-001 Rev G)."""
    if ca and cb:
        return f'{a} → {b}, orthogonal × 1.2 ({ca[1]}; {cb[1]})'
    return f"{a} → {b}, position missing for {', '.join(x for x, c in ((a, ca), (b, cb)) if not c)}"


def rows(g, line_positions, drivers):
    """The line-list namespace: one row per graph edge, in the seed's file
    order. Row shape (the v1 tuple): (stream_id, from, to, size, class,
    service, length_m-or-None, route, dn_basis). Cables, solids transfers and
    unpiped melts carry the classification verbatim. Pure."""
    C = line_positions
    out = []
    for e in g['edges']:
        u = (e.get('rate') or {}).get('unit')
        ph = e.get('phase')
        sid = e['stream_id']
        lay = e.get('layers') or []
        a, b = e['from_unit_id'], e['to_unit_id']
        ca, cb = C.get(a), C.get(b)
        L = length_m(ca, cb) if ca and cb else None
        route = route_text(a, b, ca, cb)
        if ph in ('E', 'electric') or 'elec' in lay or \
                (u == 'kW' and not sid.startswith('HL-') and 'thermal' not in lay):
            out.append((sid, a, b, 'cable', '—', '—', L, route, 'electrical: cable schedule X-ELS-06'))
            continue
        if ph == 'S':
            out.append((sid, a, b, 'solids', '—', '—', L, route,
                        'solids: conveyor, bin or hand transfer; not piped'))
            continue
        dn, basis = _dn_of(e, drivers)
        c, why = cls(e)
        out.append((sid, a, b, f'DN{dn}', c, why, L, route, basis))
    return out


def dn_map(rows_):
    """The (size, class) namespace the nozzle schedules and the P&ID sheets
    read: stream_id -> (size, class) - the v1 _LN parse of LINE_LIST.md,
    taken here from the rows directly (same cells)."""
    return {r[0]: (r[3], r[4]) for r in rows_}

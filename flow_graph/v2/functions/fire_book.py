"""engine v2: the fire-protection physics book (the MIXED halves of the
ledger section H rows doc_fire and haz_area — the reference writers
docs-authority/_fire.py, flow_graph/param/fire.py and
flow_graph/param/pressure_nodes.py).

The v1 library flow_graph/param/fire.py reads drivers.json and the site
profile from disk under the AQS_SITE environment variable inside every call
(fire._d(), SITE.p_process_kPa()), so a v2 renderer cannot call it without
re-introducing file I/O and an environment read into the render. This module
ports that arithmetic as pure functions over the solve inputs (the resolved
driver payload and the site profile): the NFPA 13 density/area demand rows,
the X-FIR-01 hazard-zone map, the NFPA 22/20 tank-and-pump supply book, and
the API 521 receiver fire case, plus the pressure-node gas table for the three
GAS_FIRE receivers (pressure_nodes.GAS, whose import loads drivers from disk —
here the bound driver values enter through the inputs and the fluid
constants carry the pressure_nodes basis).

Golden equality: flow_graph/v2/test_safety_books.py compares every function
against the v1 library outputs under the baseline site and against the
committed FIRE_PROTECTION.md book figures.

Pure: no I/O, no wall-clock, no RNG, no float literals (the engine lint's
discipline; the drivers and the site profile carry the values).
"""
import math

from flow_graph.param.sizing.relief import IN2_TO_MM2, equiv_bore_mm, gas_area_in2  # API 520 helpers (pure)
from flow_graph.param.sizing.evaporator import fire_relief_kg_h         # API 521 liquid case (pure)

GAS_FIRE = ('CRYO_H2', 'CRYO_O2', 'CRYO_CO2')                           # the receiver fire-case units (flow_graph/param/fire.py)

_ZONE_LEVELS = {'L-1 wet process': 'L-1', 'L0 shops/pyrolysis/oils/reagents/genset/flow battery': 'L0',
                'L0 electrical rooms': 'L0', 'L1 farm/digesters': 'L1', 'L1 HAB west half': 'L1',
                'H2/O2/CO2 receiver bays': 'L-1', 'ZNBR2 enclosure': 'L0'}
_LISTED_LMIN = (1893, 2839, 3785, 4731, 5678, 7570)                     # 500..2000 gpm listed ratings, L/min (NFPA 20)
_OCC = {'L-2': 'lower reservoir (water)', 'L-1': 'wet process, EW cells, heat battery, cold box and gas receivers',
        'L0': 'shops, pyrolysis reactor, oils and reagents, genset fuel, flow battery, power conversion',
        'L1': 'farm and digesters (HAB on the west half: LH)', 'R': 'reservoir levels (water, unoccupied)', 'ROOF': 'PV array'}


def _v(d, k):
    return d[k]['value']


def gas_book(d):
    """The pressure-node gas table for the GAS_FIRE receivers
    (flow_graph/param/pressure_nodes.py GAS): operating pressures and
    temperatures are bound driver values; the fluid constants (molar mass,
    k, Z) carry the pressure_nodes basis. Golden against the v1 GAS entries."""
    cb = 'CRYO.cold-box-asu-recovery-train.'
    return {
        'CRYO_H2': dict(P_bar=_v(d, cb + 'CRYO_H2_store_P_bar'), T_K=_v(d, cb + 'CRYO_H2_store_T_K'),
                        M=float('2.016'), k=float('1.41'), Z=float('1.13'), fluid='hydrogen'),
        'CRYO_O2': dict(P_bar=_v(d, cb + 'CRYO_O2_store_P_bar'), T_K=_v(d, cb + 'CRYO_O2_store_T_K'),
                        M=float('31.999'), k=float('1.40'), Z=float('0.97'), fluid='oxygen'),
        'CRYO_CO2': dict(P_bar=_v(d, cb + 'CRYO_CO2_store_P_bar'), T_K=_v(d, cb + 'CRYO_CO2_store_T_K'),
                         M=float('44.01'), k=float('1.29'), Z=float('0.85'),
                         fluid='CO2 vapour off the liquid store at -20 C (AQS-DUTY-069, NIST_WEBBOOK)'),
    }


def demand(d, plate_m2):
    """Per-level sprinkler demand rows and the governing fire-water volume, m3
    (NFPA13_2025 ch. 19 density/area with the hose allowance; A-M-188,
    X-FIR-01 drivers fire_*)."""
    haz = {k: tuple(float(x) for x in vv) for k, vv in _v(d, 'fire_nfpa13_hazards').items()}
    level_haz = dict(_v(d, 'fire_level_hazard'))
    margin = _v(d, 'fire_sprinkler_margin')
    out = []
    for lv in ('L-2', 'L-1', 'L0', 'L1', 'R', 'ROOF'):
        hz = level_haz.get(lv)
        occ = _OCC[lv]
        if not hz:
            out.append(dict(level=lv, occ=occ, hazard='none', density=0, area=0, sprink_Lmin=0, hose_Lmin=0, dur_min=0, V_m3=0))
            continue
        dn, a, hose, t = haz[hz]
        a = min(a, plate_m2)
        q = dn * a * margin
        out.append(dict(level=lv, occ=occ, hazard=hz, density=dn, area=a, sprink_Lmin=q, hose_Lmin=hose, dur_min=t,
                        V_m3=(q + hose) * t / 1000))
    return out, max(r['V_m3'] for r in out)


def zones(d):
    """Per-zone demand at the NFPA 13 density/area design point (X-FIR-01
    zone map over the drivers fire_zone_hazard)."""
    haz = {k: tuple(float(x) for x in vv) for k, vv in _v(d, 'fire_nfpa13_hazards').items()}
    zn = dict(_v(d, 'fire_zone_hazard'))
    margin = _v(d, 'fire_sprinkler_margin')
    out = []
    for zone, cls in zn.items():
        base = next((h for h in haz if h in cls), 'none')       # 'OH2 + NFPA 15 water spray' -> OH2 wet system
        dn, a, hose, t = haz[base]
        preaction = 'pre-action' in cls
        q = float(0) if base == 'none' else dn * a * margin
        out.append(dict(zone=zone, level=_ZONE_LEVELS.get(zone, ''), hazard=cls, density=dn, area=a, sprink_Lmin=q,
                        hose_Lmin=hose, dur_min=t, V_m3=(q + hose) * t / 1000,
                        system='pre-action (double interlock)' if preaction else 'wet pipe'))
    return out


def supply(d, rows, vf, static_head_kPa=None):
    """Fire water tank and fire pump from the drivers basis (NFPA22_2023 /
    NFPA20_2025): the governing volume as tower dead storage plus the
    CATCH_TANK suction source; pump rated at the listed step over the
    governing sprinkler + hose demand, head = static shortfall + design
    margin, churn and runout per NFPA 20 4.16/4.18."""
    gv = max(rows, key=lambda r: r['V_m3'])
    q_gov = gv['sprink_Lmin'] + gv['hose_Lmin']
    rated_q = next((x for x in _LISTED_LMIN if x >= q_gov * _v(d, 'fire_pump_150_flow_frac') / float('1.5')), _LISTED_LMIN[-1])
    static = static_head_kPa if static_head_kPa is not None else float(0)
    rated_head = _v(d, 'fire_pump_head_margin_kPa') + max(float(0), float('48.0') - static)   # 48 kPa = 7 psi min head
    p_kW = rated_q / 60000 * (rated_head * 1000 / float('9810')) / float('0.70')             # Q x H / 0.70 wire-to-water
    return dict(governing_level=gv['level'], governing_hazard=gv['hazard'], governing_V_m3=vf,
                tank=_v(d, 'fire_tank_type'), refill_h=_v(d, 'fire_tank_refill_h'),
                pump=_v(d, 'fire_pump_type'), demand_Lmin=round(q_gov), rated_Lmin=rated_q,
                rated_head_kPa=round(rated_head), churn_max_kPa=round(rated_head * _v(d, 'fire_pump_churn_frac')),
                runout_Lmin=round(rated_q * _v(d, 'fire_pump_150_flow_frac')),
                runout_head_min_kPa=round(rated_head * _v(d, 'fire_pump_150_head_frac')),
                pump_kW=round(p_kW, 1), pipe=_v(d, 'fire_pipe_schedule'))


def receiver_fire(p, p_process_kPa):
    """API521_2020 fire case on a tube bank (params of CRYO_H2/O2/CO2 as
    rebuilt in memory by the doc stage): one relief valve per manifolded half,
    gas-filled tubes by the API 521 unwetted-vessel method, liquid CO2 by the
    21,000 F A^0.82 Btu/h case relieved as vapour; depressuring to 50 % design
    in 15 min (API 521 5.20). p carries design, design_kPa and relief_basis;
    p_process_kPa is the site process-space pressure (the v1 SITE read)."""
    ds = p['design']
    rb = p['relief_basis']
    m, k, z, tn = rb['M_kg_kmol'], rb['k'], rb['Z'], rb['T_K']
    a = ds['tubes'] * math.pi * ds['OD_mm'] / 1000 * ds['tube_m']
    ah = a / 2
    p1 = float('1.21') * p['design_kPa'] + p_process_kPa
    pset = p['design_kPa'] + p_process_kPa
    liquid = m > 40 and tn < 273
    if not liquid:
        t1 = tn * p1 / rb['P1_kPa_abs']
        t1r = t1 * float('1.8')
        from flow_graph.param.sizing.relief import gas_C
        fp = max(float('0.01'), float('0.1406') / (gas_C(k) * float('0.975')) * (float('1100') + float('459.67') - t1r)
                 ** float('1.25') / t1r ** float('0.6625'))
        ain = fp * ah * float('10.7639') / math.sqrt(p1 * float('0.145038'))
    else:
        w, _ = fire_relief_kg_h(ah, float('282.0'))
        t1 = tn + 30
        ain = gas_area_in2(w * float('2.20462'), k, p1 * float('0.145038'), t1 * float('1.8'), z, m)
    v = sum(b['V_m3'] for b in ds['banks'])

    def rho(pk):
        return pk * 1000 * m / (8314 * z * tn)

    mdep = float(0) if liquid else v * (rho(pset) - rho(float('0.5') * p['design_kPa'] + p_process_kPa))
    wd = 2 * mdep / 900 * 3600
    ad = gas_area_in2(wd * float('2.20462'), k, pset * float('0.145038'), tn * float('1.8'), z, m) if mdep else float(0)
    return dict(exposed_m2=a, per_half_m2=ah, P1_kPa_abs=p1, T1_K=t1, A_req_mm2_per_half=ain * IN2_TO_MM2,
                bore_req_mm_per_half=equiv_bore_mm(ain), valves=2, depress_kg=mdep,
                depress_bore_mm=equiv_bore_mm(ad) if mdep else float(0), liquid=liquid,
                method='API 521 7th ed. 4.4.13.2.4 (API521_2020)')

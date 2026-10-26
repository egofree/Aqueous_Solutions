"""X-SAF-05 fire water demand (A-M-188); X-FIR-01 tank/pump drivers + zone map (AQS-SAF-005 rev B).
NFPA13_2025 ch. 19 density/area method per hazard class, design area capped at the level
footprint, plus the Table 19.2.3.1.1 hose allowance and duration. The governing level sets the
fire reserve, held as dead storage in the water tower below the hydro outlet (NFPA22_2023
gravity tank) so the energy store can never draw it. U4b: the hazard table, level and zone
maps, the hydraulic margin and the tank/pump basis are single-sourced from drivers.json
(fire_* keys) so X-FIR-01's Done-when - fire water tank and fire pump as drivers - holds."""
import math
from . import drivers as DR, site as SITE

# zone map (X-FIR-01): finer than the level roll-up where AQS-ELEC-009 release sources and the
# AQS-SAF-007 separation layout make a zone differ from its level class; hazard class flagged
# pending the owner hall programme (Done-when wording).
ZONE_LEVELS = {'L-1 wet process': 'L-1', 'L0 shops/pyrolysis/oils/reagents/genset/flow battery': 'L0',
               'L0 electrical rooms': 'L0', 'L1 farm/digesters': 'L1', 'L1 HAB west half': 'L1',
               'H2/O2/CO2 receiver bays': 'L-1', 'ZNBR2 enclosure': 'L0'}


def _d():
    d = DR.load()
    haz = {k: tuple(float(x) for x in v) for k, v in DR.val(d, 'fire_nfpa13_hazards').items()}
    lv = dict(DR.val(d, 'fire_level_hazard')); zn = dict(DR.val(d, 'fire_zone_hazard'))
    return d, haz, lv, zn


def demand(plate_m2, margin=None):
    """Per-level sprinkler demand rows and the governing fire-water volume, m3 (X-SAF-05)."""
    d, HAZ, LEVEL_HAZ, _z = _d()
    margin = DR.val(d, 'fire_sprinkler_margin') if margin is None else margin
    OCC = {'L-2': 'lower reservoir (water)', 'L-1': 'wet process, EW cells, heat battery, cold box and gas receivers',
           'L0': 'shops, pyrolysis reactor, oils and reagents, genset fuel, flow battery, power conversion',
           'L1': 'farm and digesters (HAB on the west half: LH)', 'R': 'reservoir levels (water, unoccupied)', 'ROOF': 'PV array'}
    out = []
    for lv in ('L-2', 'L-1', 'L0', 'L1', 'R', 'ROOF'):
        hz = LEVEL_HAZ.get(lv)
        occ = OCC[lv]
        if not hz:
            out.append(dict(level=lv, occ=occ, hazard='none', density=0, area=0, sprink_Lmin=0, hose_Lmin=0, dur_min=0, V_m3=0)); continue
        dn, a, hose, t = HAZ[hz]; a = min(a, plate_m2); q = dn * a * margin
        out.append(dict(level=lv, occ=occ, hazard=hz, density=dn, area=a, sprink_Lmin=q, hose_Lmin=hose, dur_min=t, V_m3=(q + hose) * t / 1000))
    return out, max(r['V_m3'] for r in out)


def zones():
    """Per-zone demand at the NFPA 13 density/area design point (X-FIR-01 zone map)."""
    d, HAZ, _lv, ZN = _d()
    margin = DR.val(d, 'fire_sprinkler_margin')
    out = []
    for zone, cls in ZN.items():
        base = next((h for h in HAZ if h in cls), 'none')       # 'OH2 + NFPA 15 water spray' / 'pre-action, OH2 void' -> OH2 wet system
        dn, a, hose, t = HAZ[base]
        preaction = 'pre-action' in cls
        q = 0.0 if base == 'none' else dn * a * margin
        out.append(dict(zone=zone, level=ZONE_LEVELS.get(zone, ''), hazard=cls, density=dn, area=a, sprink_Lmin=q,
                        hose_Lmin=hose, dur_min=t, V_m3=(q + hose) * t / 1000, system='pre-action (double interlock)' if preaction else 'wet pipe'))
    return out


def supply(rows, Vf, static_head_kPa=None):
    """Fire water tank and fire pump from the drivers basis (NFPA22_2023 / NFPA20_2025).
    Tank: the governing volume as gravity dead storage in the tower plus the CATCH_TANK suction
    source (two supplies). Pump: listed rating step at the governing sprinkler + hose demand,
    head = static shortfall + design margin over the remote-area hydraulics, churn <= 121 %."""
    d, _HAZ, _lv, _zn = _d()
    gv = max(rows, key=lambda r: r['V_m3'])
    q_gov = gv['sprink_Lmin'] + gv['hose_Lmin']
    listed = [1893, 2839, 3785, 4731, 5678, 7570]               # 500..2000 gpm listed ratings, L/min
    rated_q = next((x for x in listed if x >= q_gov * DR.val(d, 'fire_pump_150_flow_frac') / 1.5), listed[-1])
    static = static_head_kPa if static_head_kPa is not None else 0.0
    rated_head = DR.val(d, 'fire_pump_head_margin_kPa') + max(0.0, 48.0 - static)   # 48 kPa = 7 psi min head pressure
    p_kW = rated_q / 60000 * (rated_head * 1000 / 9810) / 0.70  # Q[m3/s] x H[m] / 0.70 wire-to-water
    return dict(governing_level=gv['level'], governing_hazard=gv['hazard'], governing_V_m3=Vf,
                tank=DR.val(d, 'fire_tank_type'), refill_h=DR.val(d, 'fire_tank_refill_h'),
                pump=DR.val(d, 'fire_pump_type'), demand_Lmin=round(q_gov), rated_Lmin=rated_q,
                rated_head_kPa=round(rated_head), churn_max_kPa=round(rated_head * DR.val(d, 'fire_pump_churn_frac')),
                runout_Lmin=round(rated_q * DR.val(d, 'fire_pump_150_flow_frac')),
                runout_head_min_kPa=round(rated_head * DR.val(d, 'fire_pump_150_head_frac')),
                pump_kW=round(p_kW, 1), pipe=DR.val(d, 'fire_pipe_schedule'))


GAS_FIRE = ('CRYO_H2', 'CRYO_O2', 'CRYO_CO2')


def receiver_fire(p):
    """API521_2020 fire case on a tube bank (params of CRYO_H2/O2/CO2). One relief valve per manifolded half; each half sized for its own tubes.
    Gas-filled: A = F' A'/sqrt(P1), F' = 0.1406/(C Kd)(Tw - T1)^1.25/T1^0.6625 (USC), Tw 1100 F, min F' 0.01. Liquid CO2: Q = 21,000 F A^0.82 Btu/h
    relieved as vapour (latent 282 kJ/kg, NIST_WEBBOOK). P1 = 121 % of design gauge + atm. Depressuring (API 521 5.20): to 50 % design in 15 min."""
    from .sizing.relief import gas_C, gas_area_in2, IN2_TO_MM2, equiv_bore_mm
    from .sizing.evaporator import fire_relief_kg_h
    ds = p['design']; rb = p['relief_basis']; M, k, Z, Tn = rb['M_kg_kmol'], rb['k'], rb['Z'], rb['T_K']
    A = ds['tubes'] * math.pi * ds['OD_mm'] / 1000 * ds['tube_m']; Ah = A / 2; P1 = 1.21 * p['design_kPa'] + SITE.p_process_kPa(); Pset = p['design_kPa'] + SITE.p_process_kPa()
    liquid = M > 40 and Tn < 273
    if not liquid:
        T1 = Tn * P1 / rb['P1_kPa_abs']; T1R = T1 * 1.8; Fp = max(0.01, 0.1406 / (gas_C(k) * 0.975) * (1100 + 459.67 - T1R) ** 1.25 / T1R ** 0.6625)
        Ain = Fp * Ah * 10.7639 / math.sqrt(P1 * 0.145038)
    else:
        W, _ = fire_relief_kg_h(Ah, 282.0); T1 = Tn + 30; Ain = gas_area_in2(W * 2.20462, k, P1 * 0.145038, T1 * 1.8, Z, M)
    V = sum(b['V_m3'] for b in ds['banks']); rho = lambda Pk: Pk * 1000 * M / (8314 * Z * Tn)
    m = 0.0 if liquid else V * (rho(Pset) - rho(0.5 * p['design_kPa'] + SITE.p_process_kPa())); Wd = 2 * m / 900 * 3600
    Ad = gas_area_in2(Wd * 2.20462, k, Pset * 0.145038, Tn * 1.8, Z, M) if m else 0.0
    return dict(exposed_m2=A, per_half_m2=Ah, P1_kPa_abs=P1, T1_K=T1, A_req_mm2_per_half=Ain * IN2_TO_MM2, bore_req_mm_per_half=equiv_bore_mm(Ain),
                valves=2, depress_kg=m, depress_bore_mm=equiv_bore_mm(Ad) if m else 0.0, liquid=liquid, method='API 521 7th ed. 4.4.13.2.4 (API521_2020)')

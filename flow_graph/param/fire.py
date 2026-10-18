"""X-SAF-05 fire water demand (A-M-188). NFPA13_2022 ch. 19 density/area method per level hazard class, design area capped at the level
footprint, plus the Table 19.2.3.1.1 hose allowance and duration. The governing level sets the fire reserve, held as dead storage in the
water tower below the hydro outlet (NFPA22_2023 gravity tank) so the energy store can never draw it."""
# (level, occupancy, hazard, density mm/min, area m2, hose L/min, duration min)
HAZ = {'LH': (4.1, 139, 380, 30), 'OH1': (6.1, 139, 950, 60), 'OH2': (8.1, 139, 950, 90), 'EH1': (12.2, 232, 1900, 90), 'EH2': (16.3, 232, 1900, 120)}
LEVELS = [('L-2', 'lower reservoir (water)', None), ('L-1', 'wet process, EW cells, heat battery, cold box and gas receivers', 'OH2'),
          ('L0', 'shops, pyrolysis reactor, oils and reagents, genset fuel, flow battery, power conversion', 'EH1'),
          ('L1', 'farm and digesters (HAB on the west half: LH)', 'OH1'), ('R', 'reservoir levels (water, unoccupied)', None), ('ROOF', 'PV array', None)]
def demand(plate_m2, margin=1.10):
    out = []
    for lv, occ, hz in LEVELS:
        if not hz: out.append(dict(level=lv, occ=occ, hazard='none', density=0, area=0, sprink_Lmin=0, hose_Lmin=0, dur_min=0, V_m3=0)); continue
        dn, a, hose, t = HAZ[hz]; a = min(a, plate_m2); q = dn*a*margin
        out.append(dict(level=lv, occ=occ, hazard=hz, density=dn, area=a, sprink_Lmin=q, hose_Lmin=hose, dur_min=t, V_m3=(q + hose)*t/1000))
    return out, max(r['V_m3'] for r in out)
import math
GAS_FIRE = ('CRYO_H2', 'CRYO_O2', 'CRYO_CO2')
def receiver_fire(p):
    """API521_2020 fire case on a tube bank (params of CRYO_H2/O2/CO2). One relief valve per manifolded half; each half sized for its own tubes.
    Gas-filled: A = F' A'/sqrt(P1), F' = 0.1406/(C Kd)(Tw - T1)^1.25/T1^0.6625 (USC), Tw 1100 F, min F' 0.01. Liquid CO2: Q = 21,000 F A^0.82 Btu/h
    relieved as vapour (latent 282 kJ/kg, NIST_WEBBOOK). P1 = 121 % of design gauge + atm. Depressuring (API 521 5.20): to 50 % design in 15 min."""
    from .sizing.relief import gas_C, gas_area_in2, IN2_TO_MM2, equiv_bore_mm
    from .sizing.evaporator import fire_relief_kg_h
    ds = p['design']; rb = p['relief_basis']; M, k, Z, Tn = rb['M_kg_kmol'], rb['k'], rb['Z'], rb['T_K']
    A = ds['tubes']*math.pi*ds['OD_mm']/1000*ds['tube_m']; Ah = A/2; P1 = 1.21*p['design_kPa'] + 101.325; Pset = p['design_kPa'] + 101.325
    liquid = M > 40 and Tn < 273
    if not liquid:
        T1 = Tn*P1/rb['P1_kPa_abs']; T1R = T1*1.8; Fp = max(0.01, 0.1406/(gas_C(k)*0.975)*(1100 + 459.67 - T1R)**1.25/T1R**0.6625)
        Ain = Fp*Ah*10.7639/math.sqrt(P1*0.145038)
    else:
        W, _ = fire_relief_kg_h(Ah, 282.0); T1 = Tn + 30; Ain = gas_area_in2(W*2.20462, k, P1*0.145038, T1*1.8, Z, M)
    V = sum(b['V_m3'] for b in ds['banks']); rho = lambda Pk: Pk*1000*M/(8314*Z*Tn)
    m = 0.0 if liquid else V*(rho(Pset) - rho(0.5*p['design_kPa'] + 101.325)); Wd = 2*m/900*3600
    Ad = gas_area_in2(Wd*2.20462, k, Pset*0.145038, Tn*1.8, Z, M) if m else 0.0
    return dict(exposed_m2=A, per_half_m2=Ah, P1_kPa_abs=P1, T1_K=T1, A_req_mm2_per_half=Ain*IN2_TO_MM2, bore_req_mm_per_half=equiv_bore_mm(Ain),
                valves=2, depress_kg=m, depress_bore_mm=equiv_bore_mm(Ad) if m else 0.0, liquid=liquid, method='API 521 7th ed. 4.4.13.2.4 (API521_2020)')

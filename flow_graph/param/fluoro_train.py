"""Fluoropolymer train activation (AQS-DUTY-073 rev B, unit task 02 for the fluoro units; Q-013 reopen, A-M-289).

Runs AFTER flow_graph.param.foundry_poly in each regen graph pass and turns the F-blocked standby train live:

  F source  : dock-imported fluorspar (acid-spar class >= 97 % CaF2) + 98 wt% H2SO4 -> HF_GEN rotary kiln
              (ULLMANN_HF), under the D-DOCK feedstock-import ruling (2026-10-19). The plant acid loop is HCl
              (BMED), so no on-site H2SO4 exists at this scope; the acid imports on the NaOH-flake precedent.
  Recovery  : the digester fluoride (IA-HF-SRC, re-pointed LEACH -> F_RECOVER) and the POLY_F off-spec reclaim
              close the fluorine inventory through F_RECOVER -> HF_GEN (AQS-DUTY-FP section 2).
  Scale     : graph reagent draw S31 (1.5 kg/d aqueous HF, WET_BENCH fork) + the AQS-RATE-FP-MET seal/gasket
              replacement rates (VDF 0.15 / TFE 0.10 / PVDF 0.14 / PTFE 0.09 kg/d, drivers).
  Chemistry : locked route AQS-SEL-FP (ULLMANN_FLUOROPOLY), net balanced per unit (chlorocarbon intermediates
              internal):  VDF: 2 CH3OH + 2 Cl2 + 2 HF -> CH2=CF2 + 4 HCl + 2 H2O
                          TFE: 2 CH3OH + 4 Cl2 + 4 HF -> C2F4     + 8 HCl + 2 H2O
              Cl2 comes from the CRU chlorate finish (NaClO3 + 6 HCl -> 3 Cl2 + NaCl + 3 H2O): the dilute HCl
              returns close the halogen loop and IA-CRU-01 re-solves on the CRU balance (A-M-289 supersedes the
              no-internal-sink wording of the A-M-290 chlorine ruling for this 0.62 kg/d Cl2 draw).
  Products  : PVDF -> FILM_CAST (gasket/lining sheet) -> POLY_STOCK; PTFE -> POWDER_RESIN -> POLY_STOCK;
              POLY_STOCK issues FLUORO_TO_MFG (0.23 kg/d) into the MFG_SHOP remnant, so the foundry_poly
              olefin draw P re-solves smaller and the shop closure, melt conservation and naphtha/ship split
              all ride (total shop polymer unchanged; A-M-257 pattern).

foundry_poly zero-rates the fluoro edges each pass from its Rev A stance; this stage re-rates them (it reads
S31/S66 and the drivers only, never foundry_poly outputs), so the regen fixed point is stable after two passes.

Run: python3 -m flow_graph.param.fluoro_train [--write]
"""
import json, math, os, sys
from . import drivers as DR

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GP = os.path.join(ROOT, 'flow_graph/plant_flow_graph.json')
DOC_P, AM = 'AQS-DUTY-073', 'A-M-289'
TAG = f'X-PAR-02 TF: fluoropolymer train activation ({DOC_P} sec. 3, {AM})'
FP = 'POLYMERS.fluoropolymer-train.'

# molar masses, kg/kmol (NIST_WEBBOOK); the kg/d close exactly per unit from these
M_HF, M_CH3OH, M_CL2, M_HCL, M_H2O = 20.008, 32.042, 70.906, 36.458, 18.015
M_VDF, M_TFE, M_CAF2, M_H2SO4, M_CASO4 = 64.034, 100.020, 78.074, 98.079, 136.141


def rate(v, note):
    return {'value': round(v, 6), 'unit': 'kg/d', 'status': 'study', 'note': note}


def solve(g=None):
    if g is None:
        g = json.load(open(GP))
    d = DR.load(); val = lambda k: DR.val(d, k)
    E = {e['stream_id']: e for e in g['edges']}
    r6 = lambda x: round(x, 6)
    vdf, tfe = val(FP + 'vdf_monomer_kg_d'), val(FP + 'tfe_monomer_kg_d')
    pvdf, ptfe = val(FP + 'pvdf_resin_kg_d'), val(FP + 'ptfe_resin_kg_d')
    hf_ed = r6(float(E['S31']['rate']['value'] or 0))                    # graph draw: fab reagent fork
    s66 = r6(float(E['S66']['rate']['value'] or 0))                      # CRU chlorate liquor in
    conc = r6(hf_ed + (vdf + tfe - pvdf - ptfe))                         # F_RECOVER out = leach F + POLY_F reclaim
    # per-kg coefficients from the net balanced route equations (kg/kg product)
    c = dict(hf_vdf=2 * M_HF / M_VDF, meoh_vdf=2 * M_CH3OH / M_VDF, cl2_vdf=2 * M_CL2 / M_VDF,
             hcl_vdf=(4 * M_HCL + 2 * M_H2O) / M_VDF,
             hf_tfe=4 * M_HF / M_TFE, meoh_tfe=2 * M_CH3OH / M_TFE, cl2_tfe=4 * M_CL2 / M_TFE,
             hcl_tfe=(8 * M_HCL + 2 * M_H2O) / M_TFE)
    r = dict(d=d, g=g, E=E, vdf=vdf, tfe=tfe, pvdf=pvdf, ptfe=ptfe, hf_ed=hf_ed, conc=conc,
             reclaim=r6(vdf + tfe - pvdf - ptfe), fluoro_shop=r6(pvdf + ptfe),
             hf_vdf=r6(vdf * c['hf_vdf']), hf_tfe=r6(tfe * c['hf_tfe']),
             meoh_vdf=r6(vdf * c['meoh_vdf']), meoh_tfe=r6(tfe * c['meoh_tfe']),
             cl2_vdf=r6(vdf * c['cl2_vdf']), cl2_tfe=r6(tfe * c['cl2_tfe']),
             hcl_vdf=r6(vdf * c['hcl_vdf']), hcl_tfe=r6(tfe * c['hcl_tfe']), c=c)
    # exact per-unit closure at the written precision: the dilute HCl return takes the rounding residue
    r['hcl_vdf'] = r6(r['meoh_vdf'] + r['hf_vdf'] + r['cl2_vdf'] - vdf)
    r['hcl_tfe'] = r6(r['meoh_tfe'] + r['hf_tfe'] + r['cl2_tfe'] - tfe)
    # kiln: HF from spar covers the product beyond the recovered concentrate
    hf_prod = r6(hf_ed + r['hf_vdf'] + r['hf_tfe'])
    caf2_conv = (hf_prod - conc) * M_CAF2 / (2 * M_HF)
    spar = r6(caf2_conv / (val(FP + 'fluorspar_CaF2_wt') * val(FP + 'hf_kiln.CaF2_conversion')))
    acid_soln = r6(caf2_conv * M_H2SO4 / M_CAF2 * val(FP + 'hf_kiln.H2SO4_stoich_frac') / val(FP + 'H2SO4_wt'))
    r.update(hf_prod=hf_prod, caf2_conv=caf2_conv, spar=spar, acid_soln=acid_soln,
             cake=r6(spar + acid_soln + conc - hf_prod),        # anhydrite cake by difference: the kiln closes exactly
             cru_01=r6(s66 + r['hcl_vdf'] + r['hcl_tfe'] - r['cl2_vdf'] - r['cl2_tfe']),
             s66=s66)
    # duties (W class at these rates): insulated-cylinder losses at temperature + sensible/reaction terms
    from .sizing import heat as HT
    T_k = val(FP + 'hf_kiln.T_C')
    _, kiln_loss = HT.insulated_cylinder(T_k, 200.0, 1.2)
    q_rxn = caf2_conv / M_CAF2 * val(FP + 'hf_kiln.dHrxn_kJ_mol') / 86400          # endotherm, kJ/d -> W
    q_sens = (spar + acid_soln) * val(FP + 'hf_kiln.feed_cp_kJ_kgK') * (T_k - 25) / 86400
    _, vdf_l1 = HT.insulated_cylinder(650.0, 150.0, 0.8); _, vdf_l2 = HT.insulated_cylinder(350.0, 150.0, 0.6)
    _, tfe_l = HT.insulated_cylinder(750.0, 100.0, 0.9)
    _, pol_l = HT.insulated_cylinder(60.0, 150.0, 0.4)
    _, film_l = HT.insulated_cylinder(220.0, 90.0, 0.6)
    r.update(hf_gen_kW=round((kiln_loss + q_rxn + q_sens) / 1000, 4),
             vdf_syn_kW=round((vdf_l1 + vdf_l2) / 1000, 4),
             tfe_syn_kW=round((tfe_l + 60.0) / 1000, 4),                 # + quench/scrub circulation class
             poly_f_kW=round((pol_l + 20.0) / 1000, 4),                  # + agitator shaft class at 0.25 kg/d
             film_kW=round((film_l + 25.0 + pvdf * 1.3 * 195 / 86400) / 1000, 4),   # + drive + melt sensible
             powder_kW=round((ptfe * 0.05 * 1000 / 24 + 15.0) / 1000, 4))           # 0.05 kWh/kg mill + classifier fan
    return r


def _mk(g, E, sid, a, b, ph, carries, v, why, layers=('mass',)):
    if sid in E:
        E[sid].update(from_unit_id=a, to_unit_id=b, presence='present', rate=rate(v, f'{why} | {TAG}.'))
    else:
        src = json.loads(json.dumps(E['F_RECOVER_TO_HF_GEN']))
        sec = {n['unit_id']: (n.get('sector_id') or 'WET') for n in g['nodes']}
        src.update(stream_id=sid, from_unit_id=a, to_unit_id=b, from_sector_id=sec.get(a, 'WET'),
                   to_sector_id=sec.get(b, 'WET'), phase=ph, layers=list(layers), carries=carries,
                   presence='present', open_boundary=False,
                   notes=f'Created by the fluoropolymer train activation (Q-013 reopen; {AM}).')
        src['rate'] = rate(v, f'{why} | {TAG}.')
        g['edges'].append(src); E[sid] = src


def apply(g=None, write=False):
    r = solve(g); g, E, d = r['g'], r['E'], r['d']
    N = {n['unit_id']: n for n in g['nodes']}

    def put(k, v, note):
        assert k in E, k
        E[k]['rate'] = rate(v, note)

    put('F_RECOVER_TO_HF_GEN', r['conc'],
        f'Fluoride concentrate to the kiln = leach fluoride {r["hf_ed"]:.3f} (IA-HF-SRC) + POLY_F off-spec reclaim '
        f'{r["reclaim"]:.3f} kg/d (depolymerization/regrind return; AQS-DUTY-FP sec. 2, {AM}).')
    put('HF_GEN_TO_VDF', r['hf_vdf'],
        f'Aqueous HF to VDF: {r["vdf"]:.2f} kg/d VDF x 2 HF/VDF (2 CH3OH + 2 Cl2 + 2 HF -> CH2=CF2 + 4 HCl + 2 H2O; '
        f'AQS-SEL-FP locked route, ULLMANN_FLUOROPOLY).')
    put('HF_GEN_TO_TFE', r['hf_tfe'],
        f'Aqueous HF to TFE: {r["tfe"]:.2f} kg/d TFE x 4 HF/TFE (R-22 route; AQS-SEL-FP, ULLMANN_FLUOROPOLY).')
    put('VDF_TO_POLY_F', r['vdf'], f'VDF monomer to polymerization (AQS-RATE-FP-MET; {AM}).')
    put('TFE_TO_POLY_F', r['tfe'], f'TFE monomer to polymerization (AQS-RATE-FP-MET; {AM}).')
    put('POLYF_TO_POWDER', r['ptfe'],
        f'PTFE resin to the powder line: {r["tfe"]:.2f} kg/d TFE -> {r["ptfe"]:.2f} kg/d at the ~90 % yield of the '
        f'AQS-RATE-FP-MET reclaim loop (suspension powder, not melt-processable; ULLMANN_FLUOROPOLY).')
    _mk(g, E, 'POLYF_TO_FILM', 'POLY_F', 'FILM_CAST', 'L', 'PVDF resin to the film/sheet line', r['pvdf'],
        f'PVDF resin to cast film for gasket/lining stock (AQS-RATE-FP-MET PVDF linings and gaskets; {AM}). '
        f'Closes the FILM_CAST feed gap named by the foundry_poly pass at Rev AC')
    put('FILM_TO_STOCK', r['pvdf'], f'PVDF cast film/sheet to stock ({AM}).')
    put('POWDER_TO_STOCK', r['ptfe'], f'PTFE fine powder to stock ({AM}).')
    put('POLYF_TO_PELLET', 0.0,
        'Pellet path rides the olefin line; the fluoropolymer products go to FILM_CAST (PVDF sheet) and POWDER_RESIN '
        f'(PTFE) per the AQS-RATE-FP-MET demand table ({AM}).')
    put('CRU_TO_VDF', r['cl2_vdf'],
        f'Cl2 to VDF: 2 Cl2 per VDF from the CRU chlorate finish on the returned dilute HCl (halogen loop closes; '
        f'AQS-SEL-FP; {AM} supersedes the A-M-290 no-internal-sink wording for this 0.62 kg/d Cl2 draw).')
    put('CRU_TO_TFE', r['cl2_tfe'], f'Cl2 to TFE: 4 Cl2 per TFE from the CRU chlorate finish (AQS-SEL-FP; {AM}).')
    put('IA-CRU-01', r['cru_01'],
        f'CRU liquor re-solved on the unit balance: S66 {r["s66"]:.4f} + dilute HCl returns '
        f'{r["hcl_vdf"] + r["hcl_tfe"]:.4f} - Cl2 drawn {r["cl2_vdf"] + r["cl2_tfe"]:.4f} = {r["cru_01"]:.4f} kg/d '
        f'(chlorate consumed, NaCl + reaction water + monomer water formed; {AM}). The leach sees '
        f'+{r["cru_01"] - r["s66"]:.4f} kg/d liquor, below the 0.5 kg/d battery limit, absorbed by its reconciliation layer.')
    _mk(g, E, 'IA-CAF2-MU', 'NORTH_DOCK', 'HF_GEN', 'S', 'fluorspar make-up, acid-spar class >= 97 % CaF2', r['spar'],
        f'D-DOCK feedstock import (mining-waste class, 2026-10-19): {r["spar"]:.4f} kg/d acid-spar at 97 % CaF2 covers '
        f'the HF product beyond the recovered fluoride (ULLMANN_HF; {AM})')
    _mk(g, E, 'IA-H2SO4-MU', 'NORTH_DOCK', 'HF_GEN', 'L', '98 wt% sulfuric acid make-up', r['acid_soln'],
        f'Reagent import on the NaOH-flake precedent (IA-NAOH-MU): {r["acid_soln"]:.4f} kg/d chamber acid at 98 wt%, '
        f'{DR.val(d, FP + "hf_kiln.H2SO4_stoich_frac"):.0%} of stoichiometric on the converted spar (ULLMANN_HF; {AM}). '
        f'The plant acid loop is HCl (BMED); no on-site H2SO4 exists at this scope.')
    _mk(g, E, 'IA-GYPSUM-SHIP', 'HF_GEN', 'NORTH_DOCK', 'S', 'fluorgypsum (anhydrite) cake byproduct', r['cake'],
        f'Kiln cake by difference = spar + acid + concentrate - HF product: anhydrite '
        f'{r["caf2_conv"] * M_CASO4 / M_CAF2:.3f} kg/d with unreacted spar, excess acid, gangue and moisture '
        f'(ULLMANN_HF); reported as a dock byproduct export (D-DOCK).')
    _mk(g, E, 'IA-HF-PROD', 'HF_GEN', 'WS_HF_ED', 'L', 'aqueous HF to the fab reagent fork', r['hf_ed'],
        f'HF_GEN supplies the reagent fork at the S31 draw {r["hf_ed"]:.3f} kg/d (AQS-DUTY-FP sec. 2: product to the '
        f'monomer units and the direct HF users; replaces the direct leach feed of IA-HF-SRC, which now runs through F_RECOVER)')
    _mk(g, E, 'MEOH_TO_VDF', 'MEOH_TANK', 'VDF_SYN', 'L', 'methanol carbon source to VDF', r['meoh_vdf'],
        f'2 CH3OH per VDF (AQS-SEL-FP) = {r["vdf"]:.2f} x {2 * M_CH3OH / M_VDF:.4f}; the tank re-closes on IA-MEOH-PROD '
        f'by difference (o2_close), so the methanol shipped falls 1:1')
    _mk(g, E, 'MEOH_TO_TFE', 'MEOH_TANK', 'TFE_SYN', 'L', 'methanol carbon source to TFE', r['meoh_tfe'],
        f'2 CH3OH per TFE (AQS-SEL-FP) = {r["tfe"]:.2f} x {2 * M_CH3OH / M_TFE:.4f}')
    _mk(g, E, 'VDF_HCL_TO_CRU', 'VDF_SYN', 'CRU', 'L', 'dilute HCl return (HCl + reaction water)', r['hcl_vdf'],
        f'(4 HCl + 2 H2O) per VDF = {r["vdf"]:.2f} x {r["c"]["hcl_vdf"]:.4f} kg/d back to the chlorate finish '
        f'(NaClO3 + 6 HCl -> 3 Cl2 + NaCl + 3 H2O regenerates the Cl2; halogen loop closes, AQS-SEL-FP)')
    _mk(g, E, 'TFE_HCL_TO_CRU', 'TFE_SYN', 'CRU', 'L', 'dilute HCl return (HCl + reaction water)', r['hcl_tfe'],
        f'(8 HCl + 2 H2O) per TFE (AQS-SEL-FP) back to the CRU chlorate finish')
    _mk(g, E, 'POLYF_RECLAIM', 'POLY_F', 'F_RECOVER', 'L', 'off-spec fluoropolymer scrap/rework', r['reclaim'],
        f'Monomer less resin = {r["reclaim"]:.3f} kg/d (AQS-RATE-FP-MET ~90 % yield class): regrind for non-pressure '
        f'parts and depolymerization return, collected at F_RECOVER per AQS-DUTY-FP sec. 2')
    _mk(g, E, 'FLUORO_TO_MFG', 'POLY_STOCK', 'MFG_SHOP', 'L', 'fluoropolymer stock issue to the shop', r['fluoro_shop'],
        f'PVDF {r["pvdf"]:.2f} + PTFE {r["ptfe"]:.2f} kg/d seal/gasket/lining replacement stock; enters the MFG_SHOP '
        f'remnant r0 (foundry_poly), so the olefin draw P re-solves smaller and total shop polymer is unchanged '
        f'(A-M-257 pattern)')
    # IA-HF-SRC re-points to F_RECOVER (the digester-side fluoride recovery unit), same rate
    if E['IA-HF-SRC']['to_unit_id'] != 'F_RECOVER':
        E['IA-HF-SRC'].update(to_unit_id='F_RECOVER', to_sector_id='DIGESTER',
                              notes=f'Re-pointed to F_RECOVER by the fluoropolymer train activation: the digester '
                                    f'fluoride recovery feeds HF_GEN (AQS-DUTY-FP sec. 2; {AM}). Was LEACH -> WS_HF_ED direct.')
    # electrical: node kW + SF feeds
    for u, kwv, why in (('HF_GEN', r['hf_gen_kW'],
                         f'rotary kiln at {DR.val(d, FP + "hf_kiln.T_C"):.0f} C: insulated shell loss + endotherm '
                         f'{DR.val(d, FP + "hf_kiln.dHrxn_kJ_mol"):.1f} kJ/mol CaF2 + feed sensible ({AM})'),
                        ('VDF_SYN', r['vdf_syn_kW'], f'chlorination 350 C + 142b cracking 650 C insulated losses ({AM})'),
                        ('TFE_SYN', r['tfe_syn_kW'], f'R-22 pyrolysis 750 C tube + quench circulation ({AM})'),
                        ('POLY_F', r['poly_f_kW'], f'emulsion kettle at 60 C: jacket loss + agitator ({AM})'),
                        ('FILM_CAST', r['film_kW'], f'extruder barrel loss at 220 C + drive + melt sensible ({AM})'),
                        ('POWDER_RESIN', r['powder_kW'], f'pin-mill class 0.05 kWh/kg + classifier fan ({AM})')):
        n = N[u]
        n['continuous_kw'] = {'value': kwv, 'unit': 'kW', 'status': 'study', 'note': f'{TAG}: {why}.'}
        sid = f'SF-{u}'
        if sid not in E:
            src = json.loads(json.dumps(E['SF-HF_GEN']))
            src.update(stream_id=sid, to_unit_id=u, to_sector_id=n.get('sector_id'), notes=f'{u} feed ({AM})')
            g['edges'].append(src); E[sid] = src
        E[sid]['rate'] = {'value': kwv, 'unit': 'kW', 'status': 'study',
                          'note': f'Feed equal to {u} continuous_kw. | {TAG}.'}
    stamp(g, r)
    if write:
        open(GP, 'w').write(json.dumps(g, indent=2) + '\n')
    return r


def stamp(g, r):
    """params.design + params.envelope for the live fluoro units (X-MFG-30 pattern; models/mfg/polymers.py reads
    these) + the F_RECOVER sizing row and the POLY_STOCK sizing refresh (its outlet grows by FLUORO_TO_MFG)."""
    N = {n['unit_id']: n for n in g['nodes']}
    E = r['E']; d = r['d']
    HD = DR.val(d, 'atm_HD')

    def st(u, **kw):
        p = N[u].setdefault('params', {})
        p['sizing'] = dict(status='study', source=DOC_P, **kw)

    def cad(u, style, size, design, why):
        p = N[u]['params']
        p['design'] = design
        p['envelope'] = dict(size_mm=size, style=style, state='live', basis=why)
        p['sizing']['size_mm'] = size

    kiln_T = DR.val(d, FP + 'hf_kiln.T_C')
    cad('HF_GEN', 'rotary_kiln', [1200, 700, 1500],
        dict(machine='indirectly heated rotary kiln, fluorspar + H2SO4 -> HF', tube_D_mm=200, tube_L_mm=1200,
             slope_deg=2.0, rpm=4, residence_min=DR.val(d, FP + 'hf_kiln.residence_min'),
             T_C=kiln_T, spar_kg_d=r['spar'], acid_kg_d=r['acid_soln'], hf_kg_d=r['hf_prod'],
             cake_kg_d=r['cake'], drive_kW=0.37,
             feed='dock acid-spar 97 % CaF2 + 98 wt% H2SO4 + F_RECOVER concentrate',
             material='carbon steel shell, dry HF service (PERRY9_MAT); Monel trunnion inserts',
             duty_kW=r['hf_gen_kW']),
        f'kiln-class study minimum at the {r["hf_prod"]:.3f} kg/d HF duty (ULLMANN_HF; {AM}); tube 200 x 1200 mm, '
        f'2 deg slope, kiln gas absorbed into the recovered-F liquor at the dissolution tank')
    cad('VDF_SYN', 'reactor', [600, 600, 1200],
        dict(machine='VDF train: chlorination + hydrofluorination reactors, 142b cracking furnace, scrub',
             chlorination_C=350, cracking_C=650, catalyst='Cr2O3 class (ULLMANN_FLUOROPOLY)',
             vdf_kg_d=r['vdf'], meoh_kg_d=r['meoh_vdf'], cl2_kg_d=r['cl2_vdf'], hf_kg_d=r['hf_vdf'],
             hcl_return_kg_d=r['hcl_vdf'], duty_kW=r['vdf_syn_kW'],
             material='Hastelloy C-276 reactors, Ni cracking tube, PTFE-lined coolers'),
        f'reactor-class study minimum; the two heated stages dominate the duty ({AM})')
    cad('TFE_SYN', 'reactor', [600, 600, 1200],
        dict(machine='TFE train: R-22 pyrolysis furnace, quench, scrub',
             pyrolysis_C=750, quenched='immediate quench (TFE autopolymerisation hazard; ULLMANN_FLUOROPOLY)',
             tfe_kg_d=r['tfe'], meoh_kg_d=r['meoh_tfe'], cl2_kg_d=r['cl2_tfe'], hf_kg_d=r['hf_tfe'],
             hcl_return_kg_d=r['hcl_tfe'], duty_kW=r['tfe_syn_kW'],
             material='Inconel 600 pyrolysis tube, Hastelloy C-276 coolers, PTFE-lined scrubber'),
        f'reactor-class study minimum; pyrolysis tube + quench at the {r["tfe"]:.2f} kg/d duty ({AM})')
    cad('POLY_F', 'reactor', [600, 600, 1200],
        dict(vessel='PVDF/PTFE emulsion polymerization kettle', D_mm=150, H_mm=225, T_C=60,
             vdf_kg_d=r['vdf'], tfe_kg_d=r['tfe'], pvdf_kg_d=r['pvdf'], ptfe_kg_d=r['ptfe'],
             reclaim_kg_d=r['reclaim'], initiator='persulfate class, emulsion/suspension (ULLMANN_FLUOROPOLY)',
             duty_kW=r['poly_f_kW'], material='Hastelloy C-276 wetted, PTFE gasketed'),
        f'reactor-class study minimum; jacketed kettle at the 0.25 kg/d monomer duty, reclaim loop to F_RECOVER ({AM})')
    cad('FILM_CAST', 'line_machine', [1500, 800, 1500],
        dict(machine='PVDF cast film/sheet line', extruder_D_mm=25, die_mm=200, chill_roll_D_mm=150,
             pvdf_kg_d=r['pvdf'], melt_C=220, duty_kW=r['film_kW'],
             product='gasket/lining sheet (AQS-RATE-FP-MET PVDF linings and gaskets)', material='316L barrel, Hastelloy die'),
        f'forming-class minimum (A-M-199); 25 mm extruder at the {r["pvdf"]:.2f} kg/d sheet duty ({AM})')
    cad('POWDER_RESIN', 'line_machine', [1500, 800, 1500],
        dict(machine='PTFE powder line: pin mill + cyclone classifier + collector', ptfe_kg_d=r['ptfe'],
             mill_kWh_kg=0.05, duty_kW=r['powder_kW'],
             product='fine powder for compression sintering (PTFE is not melt-processable; ULLMANN_FLUOROPOLY)',
             material='316L mill, PE-lined collector'),
        f'forming-class minimum (A-M-199); mill + classifier at the {r["ptfe"]:.2f} kg/d powder duty ({AM})')
    # POLY_COND: real kettle geometry, installed standby (assay-gated feed keeps state standby, design is real)
    p = N['POLY_COND']['params']
    p['design'] = dict(vessel='condensation resin kettle', D_mm=200, H_mm=300, design_case_kg_d=0.5,
                       jacket_C=160, agitator_kW=0.18, material='316L, Hastelloy option',
                       note='installed standby: DIGEST_TO_POLY stays 0 until the digester organic assay issues the recipe')
    p['envelope'] = dict(size_mm=[600, 600, 1200], style='reactor', state='standby',
                         basis=f'real kettle design at the 0.5 kg/d design case; standby envelope (recipe waits on the '
                               f'digester organic assay, AQS-DES-POLY; geometry issued {AM})')
    p.setdefault('sizing', {})['size_mm'] = [600, 600, 1200]
    # F_RECOVER: live sizing row
    st('F_RECOVER', rate_kg_d=r['conc'],
       in_leach_kg_d=r['hf_ed'], in_reclaim_kg_d=r['reclaim'],
       status_note=f'live: leach fluoride + POLY_F reclaim collected as the fluoride concentrate to HF_GEN ({AM})',
       vessel='HF-equivalent concentrate hold tank, PE, 1 d hold')
    # POLY_STOCK: outlet grows by the fluoro issue (foundry_poly owns the olefin share P)
    p_mfg = float((E['POLY_TO_MFG'].get('rate') or {}).get('value') or 0)
    st('POLY_STOCK', out_kg_d=round(p_mfg + r['fluoro_shop'], 6), fluoro_kg_d=r['fluoro_shop'],
       to_wet_kg_d=round(DR.val(d, 'poly_shop_reject_frac') * p_mfg, 6), to_fab_kg_d=0.0,
       status_note=f'olefin issue (foundry_poly P) + fluoropolymer issue {r["fluoro_shop"]:.3f} kg/d ({AM})')
    # module map note for the sizing doc
    return None


def main():
    r = apply(write='--write' in sys.argv)
    out = {k: v for k, v in r.items() if k not in ('g', 'E', 'd', 'c')}
    print(json.dumps(out, indent=1, default=float))


if __name__ == '__main__':
    main()

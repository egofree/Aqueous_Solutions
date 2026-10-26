# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""X-LOC-11 hull design check for the floating island (AQS-SITE-012).

A rectangular pontoon hull of the principal dimensions in drivers.json carries the plant. The
operating mass is the packaged plant mass - the placement blocks of flow_graph/placement_seed.json
at the packaging density (A-M-413) - plus the hull lightweight from the shell steel area. The check
computes draft from displacement (Archimedes), the metacentric height GM = KB + BM - KG for the box
hull, the freeboard, and the roll period, and fails when a class criterion is not met:

    draft     T    = M / (rho_w L B Cb)                       (rho_w 1025 kg/m3, seawater)
    KB        = T / 2                                          (box hull)
    BM        = I_wp / nabla, I_wp = L B^3 / 12                (roll, about the long axis)
    KG        = sum(m_i z_i) / M over the placement blocks     (study deck stack, A-M-412)
    GM        = KB + BM - KG  >=  gm_min                       (intact stability, A-M-414)
    freeboard = D - T          >=  freeboard_min               (A-M-414)
    roll period = 2 pi k / sqrt(g GM), k = 0.35 B              (study; model tests replace it)

The values are a study, not a PE stamp; the mooring, structural and class environmental load
designs are their own tasks.

    python3 -m flow_graph.param.hull [--write]   # docs-authority/HULL_DESIGN.md (AQS-SITE-012)"""
import json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
GP = os.path.join(ROOT, 'flow_graph/plant_flow_graph.json')
OUT = 'docs-authority/HULL_DESIGN.md'
RHO_SW = 1025.0          # kg/m3 seawater at 15 C [NIST_WEBBOOK]
K_ROLL = 0.35            # rolling radius of gyration over breadth (study, A-M-414)
LEVEL_H_M = {'L-2': 1.0, 'L-1': 4.0, 'L0': 9.0, 'L1': 14.0, 'L2': 19.0}   # study deck stack above baseline, 5 m spacing (A-M-412)


def design(d=None, seed=None):
    from . import drivers as DR, site as SITE
    d = d or DR.load()
    seed = seed or json.load(open(os.path.join(ROOT, 'flow_graph/placement_seed.json')))
    v = lambda k: DR.val(d, k)
    L, B, D = v('HULL.pontoon.L_m'), v('HULL.pontoon.B_m'), v('HULL.pontoon.D_m')
    Cb = v('HULL.pontoon.Cb'); g = SITE.g()
    blocks = seed['blocks']
    spacing = v('HULL.plant.deck_spacing_m')
    def block_h(b):
        return b['size_mm'][2] / 1000 if len(b['size_mm']) > 2 else spacing   # plan-area blocks take the deck spacing
    plant_m = sum((b['size_mm'][0] * b['size_mm'][1] / 1e6) * block_h(b) * v('HULL.plant.pkg_density_kg_m3')
                  for b in blocks)
    zs = []
    for b in blocks:
        h = LEVEL_H_M.get(b['level'], spacing)
        zs.append((h + block_h(b) / 2, b))
    M_light = v('HULL.pontoon.lightweight_t') * 1000.0
    M = M_light + plant_m
    T = M / (RHO_SW * L * B * Cb)
    nabla = L * B * Cb * T
    KB = T / 2
    I_wp = L * B ** 3 / 12
    BM = I_wp / nabla
    KG = sum(m_i * z for z, b in zs for m_i in [(b['size_mm'][0] * b['size_mm'][1] / 1e6) * block_h(b) * v('HULL.plant.pkg_density_kg_m3')]) / plant_m
    kg_all = (M_light * v('HULL.pontoon.lightweight_KG_m') + plant_m * KG) / M     # lightweight KG driver + packaged plant
    GM = KB + BM - kg_all
    fb = D - T
    k = K_ROLL * B
    T_roll = 2 * math.pi * k / math.sqrt(g * GM)
    heel = v('HULL.criteria.design_heel_deg')
    heel_imm = (B / 2) * math.tan(math.radians(heel))
    errs = []
    if T > D: errs.append(f'draft {T:.2f} m exceeds hull depth {D:g} m')
    if GM < v('HULL.criteria.gm_min_m'): errs.append(f'GM {GM:.2f} m is below the {v("HULL.criteria.gm_min_m"):g} m criterion')
    if fb < v('HULL.criteria.freeboard_min_m'): errs.append(f'freeboard {fb:.2f} m is below the {v("HULL.criteria.freeboard_min_m"):g} m criterion')
    if heel_imm > fb: errs.append(f'deck-edge immersion at the {heel:g} deg heel ({heel_imm:.2f} m) exceeds the freeboard {fb:.2f} m')
    r = dict(L_m=L, B_m=B, D_m=D, Cb=Cb, blocks=len(blocks), plant_mass_t=round(plant_m / 1000, 1),
             lightweight_t=v('HULL.pontoon.lightweight_t'), operating_mass_t=round(M / 1000, 1),
             draft_m=round(T, 2), displacement_t=round(M / 1000, 1), KB_m=round(KB, 2), BM_m=round(BM, 2),
             KG_m=round(kg_all, 2), GM_m=round(GM, 2), freeboard_m=round(fb, 2), roll_period_s=round(T_roll, 1),
             heel_immersion_m=round(heel_imm, 2), gm_min_m=v('HULL.criteria.gm_min_m'), freeboard_min_m=v('HULL.criteria.freeboard_min_m'),
             heel_deg=heel, errors=errs, ok=not errs)
    return r


def render(r):
    prof_motion = ''
    try:
        from . import site as S
        g = S.load_profile('floating_island')['groups'].get('motion', {}).get('entries', {})
        if g:
            prof_motion = (f"Profile design motions (A-M-388): static heel {g['heel_deg']['value']:g} deg, "
                           f"roll amplitude {g['roll_deg']['value']:g} deg.")
    except Exception:
        prof_motion = ''
    L = ['# Floating island hull design', '',
         'Document number: AQS-SITE-012', 'Revision: A', 'Date: 2026-10-26',
         'Licence: CERN-OHL-S-2.0.', '',
         'Generated by `flow_graph/param/hull.py` from the hull drivers, the placement blocks and the '
         'site profile (X-LOC-11). Study. Not a PE stamp. Do not edit by hand.', '',
         f"{'Check passes' if r['ok'] else 'CHECK FAILS'}: {', '.join(r['errors']) if r['errors'] else 'every criterion is met'}.", '',
         '## 1. Mass', '',
         'Table 1. Operating mass', '', '| Item | Value | Basis |', '| --- | --- | --- |',
         f"| Packaged plant | {r['plant_mass_t']:g} t | {r['blocks']} placement blocks at the packaging density (A-M-413) |",
         f"| Hull lightweight | {r['lightweight_t']:g} t | A-M-412 |",
         f"| Operating mass | {r['operating_mass_t']:g} t | sum |", '',
         '## 2. Hydrostatics and stability', '',
         'Table 2. Hydrostatics', '', '| Quantity | Value | Basis |', '| --- | --- | --- |',
         f"| Draft | {r['draft_m']:g} m | displacement / (rho L B Cb), rho 1025 kg/m3 |",
         f"| Displacement | {r['displacement_t']:g} t | operating mass |",
         f"| KB | {r['KB_m']:g} m | box hull, T/2 |",
         f"| BM | {r['BM_m']:g} m | waterplane inertia L B^3/12 over displacement |",
         f"| KG | {r['KG_m']:g} m | lightweight KG (A-M-412) with the packaged plant at the study deck stack (A-M-412) |",
         f"| GM | {r['GM_m']:g} m | criterion {r['gm_min_m']:g} m (A-M-414) |",
         f"| Freeboard | {r['freeboard_m']:g} m | criterion {r['freeboard_min_m']:g} m (A-M-414) |",
         f"| Roll period | {r['roll_period_s']:g} s | k = 0.35 B (study; model tests replace it, A-M-414) |",
         f"| Deck-edge immersion at the {r['heel_deg']:g} deg design heel | {r['heel_immersion_m']:g} m | (B/2) tan(heel) against the freeboard |", '',
         prof_motion, '',
         '## 3. Method and limits', '',
         'The hull is a rectangular pontoon; the hydrostatics are the box-hull forms above. The plant '
         'mass is the packaged placement volume at the packaging density - the unit massing study '
         'replaces it. The mooring design, the structural design and the class environmental load '
         'method are their own tasks; this page proves only that the hull carries the plant with '
         'stability and freeboard margin on the stated dimensions.', '']
    return '\n'.join(L) + '\n'


def main():
    from . import drivers as DR
    r = design(DR.load())
    print(json.dumps(r, indent=1))
    if '--write' in sys.argv:
        open(os.path.join(ROOT, OUT), 'w').write(render(r))
        print(f'{OUT}: written')


if __name__ == '__main__':
    main()

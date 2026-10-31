# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""FARM aquaponics + smallstock and HAB interior design study (X-FARM-01..03, X-HAB-01).

Computes the closed-loop farm balances from the FARM/HAB driver groups and the
reference graph, and renders the two design documents:

  docs-authority/FARM_DESIGN.md  (AQS-FARM-001) aquaponics, dual root-zone growbeds,
                                 poultry, black-soldier-fly larvae composting
  docs-authority/HAB_DESIGN.md   (AQS-HAB-002) hab interior zoning: galley, washroom,
                                 medical, recreation/common, private sleeping quarters

Every rate is a study value from the driver groups (A-M-415..419); nothing is measured.
Run: python3 docs-authority/_farm_hab.py [--write]
"""
import json, math, os, sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(R)
sys.path.insert(0, R)
from flow_graph.param import drivers as DR, site as S
from flow_graph.param import farm_balance as FB

OUT_FARM = 'docs-authority/FARM_DESIGN.md'
OUT_HAB = 'docs-authority/HAB_DESIGN.md'


def study():
    d = DR.load()
    v = lambda k: DR.val(d, k)
    # --- aquaponics loop -------------------------------------------------------
    fish_stock = v('FARM.aquaponics.fish_stock_kg')
    fish_feed = round(fish_stock * v('FARM.aquaponics.fish_feed_kg_kg'), 3)
    fish_waste = round(fish_feed * 0.5, 3)                    # half the feed leaves as waste/sludge
    # --- poultry ---------------------------------------------------------------
    birds = v('FARM.chicken.stock_birds')
    chick_feed = round(birds * v('FARM.chicken.feed_kg_bird_d'), 3)
    eggs = round(birds * v('FARM.chicken.egg_kg_bird_d'), 3)
    manure = round(birds * 0.04, 3)
    chick_water = round(birds * 0.03, 3)
    chick_vap = round(chick_feed * 0.5, 3)                    # respiration/evaporation study split
    # --- BSFL composting -------------------------------------------------------
    galley_bio = 0.5                                          # galley prep + scrap (study, A-M-418 where-used)
    bsfl_in = round(galley_bio + manure + fish_waste, 3)
    larvae = round(bsfl_in * v('FARM.bsfl.larvae_frac'), 3)
    frass = round(bsfl_in * v('FARM.bsfl.frass_frac'), 3)
    bsfl_vap = round(bsfl_in - larvae - frass, 3)
    larvae_frac = round(100 * larvae / chick_feed, 1)         # larvae meal share of the layer ration
    # --- dual root-zone growbeds ----------------------------------------------
    bed_area_total = 29.12                                    # GROW_BED live area (A-M-229)
    bed_each = round(bed_area_total / 2, 2)
    # --- feed closure: the wet-basis balance is the parametric module's output ---
    F = FB.compute(DR.load())
    dw_prod = v('FARM.duckweed.prod_kg_d')                    # 4.5 kg/d DM at 300 m2
    dw_cp = v('FARM.duckweed.CP_frac')                        # 30 % class (aquaculture.md:101; ducks.md:96 says 35-43)
    form = round(F['FORM'], 2)                                # fresh to formulation
    fish_ration = round(F['FISHF'], 2)                        # fresh to the fish
    fodder = round(F['FODDER'], 2)                            # fresh forage the ducks take
    store = F['store_dm']                                     # dried reserve draw (DM)
    greens = round(F['GREENS'], 2)                            # fresh galley greens (A-M-427)
    shell = round(F['shell_dm'], 3)                           # eggshell return (DM)
    layer_ration = v('FARM.chicken.stock_birds') * v('FARM.chicken.feed_kg_bird_d')   # 1.44 DM-eq
    quail_ration = v('FARM.quail.stock') * v('FARM.quail.feed_kg_bird_d')             # 0.5 DM-eq
    lar_meal = F['larvae_meal_dm']                            # computed fixed point (A-M-416)
    layer_dw = round(layer_ration - lar_meal - F['shell_dm'], 4)
    # TECHTREE husbandry classes: BSFL meal CP 40-45 %, Ca 5-8 % (insect-farming.md:113-116);
    # layer CP req 16-18 %, Ca 3.5-4.0 % (chickens.md:74/176); quail CP 20-22 %, Ca 2.5-3.0 %,
    # met 0.50 % (coturnix.md:60/177); chicken met class 0.38-0.45 % (turkeys.md:222 comparison).
    lar_cp, lar_ca, lar_met = 0.425, 0.065, 0.011
    shell_ca = 0.38
    dw_ca, dw_met = 0.010, 0.004                              # duckweed mineral class (unmeasured - X-FARM-04)
    blend_cp = round(100 * (layer_dw * dw_cp + lar_meal * lar_cp) / layer_ration, 1)
    blend_ca = round(100 * (layer_dw * dw_ca + lar_meal * lar_ca + shell * shell_ca) / layer_ration, 2)
    layer_met = round(100 * (layer_dw * dw_met + lar_meal * lar_met) / layer_ration, 2)
    quail_met = round(100 * dw_met, 1)
    met_gap_g_d = 9                                           # loop DL-met supplement class (declared, A-M-416)
    # --- hab rooms -------------------------------------------------------------
    rooms = {'galley': v('HAB.rooms.galley_m2'), 'washroom': v('HAB.rooms.washroom_m2'),
             'medical': 6.0, 'recreation/common': v('HAB.rooms.rec_m2'),
             'private sleeping quarters': v('HAB.rooms.sleep_quarters_m2'),
             'common circulation': v('HAB.rooms.common_m2')}
    rooms_total = round(sum(rooms.values()), 1)
    return dict(fish_stock=fish_stock, fish_feed=fish_feed, fish_waste=fish_waste,
                birds=birds, chick_feed=chick_feed, eggs=eggs, manure=manure, chick_water=chick_water,
                chick_vap=chick_vap, galley_bio=galley_bio, bsfl_in=bsfl_in, larvae=larvae, frass=frass,
                bsfl_vap=bsfl_vap, larvae_frac=larvae_frac, bed_area_total=bed_area_total,
                bed_each=bed_each, rooms=rooms, rooms_total=rooms_total, crew=int(DR.val(d, 'san_crew')),
                dw_prod=dw_prod, dw_cp=dw_cp, form=form, fish_ration=fish_ration, fodder=fodder,
                store=store, greens=greens, shell=shell, layer_ration=layer_ration,
                quail_ration=quail_ration, lar_meal=lar_meal, layer_dw=layer_dw, blend_cp=blend_cp,
                blend_ca=blend_ca, layer_met=layer_met, quail_met=quail_met, met_gap_g_d=met_gap_g_d,
                fp_in=round(F['FORM'] + F['LARVA_W'] + F['shell_dm'], 2),
                fp_out=round(F['LM'] + F['QM'] + F['DM_'] + F['store_dm'] + F['REJ'] + F['VAP'] + F['PRESS'], 2),
                larvae_fresh=round(F['LARVA_W'], 3),
                bin_wet=round(F['BININ'], 2), loop_kgd=int(F['loop_kgd']),
                lm=round(F['LM'], 2), qm=round(F['QM'], 2), dm_=round(F['DM_'], 2),
                rej=round(F['REJ'], 2), press=round(F['PRESS'], 1), vap=round(F['VAP'], 1))


def render_farm(s):
    L = ['# Farm design: aquaponics, dual root-zone growbeds, poultry, larvae composting', '',
         'Document number: AQS-FARM-001', 'Revision: A', 'Date: 2026-10-26',
         'Licence: CERN-OHL-S-2.0.', '',
         'Generated by `docs-authority/_farm_hab.py` from the `FARM` driver groups (A-M-415..418) '
         'and the reference graph. Study. Not a PE stamp.', '',
         f'The farm closes the protein loop with NO imported feed (A-M-416): the duckweed raceway is '
         'the base crop, the black-soldier-fly larvae bin turns manure, sludge and galley biowaste into '
         'the concentrate co-ingredient, recycled eggshell carries the calcium, and the one binding '
         f'supplement is methionine (~{s["met_gap_g_d"]} g/d DL-met equivalent, A-M-416). '
         'The frass stages to the solids line as compost.', '',
         '## 1. Aquaponics loop and duckweed raceway', '',
         f'{s["fish_stock"]:g} kg standing tilapia-class stock at a {s["fish_feed"]:g} kg/d ration '
         f'({s["fish_ration"]:g} kg/d fresh duckweed, 1.5 % body weight - below the 2-3 % optimal-growth '
         'class (TECHTREE aquaponics.md:155), a declared slower grow-out). About half the ration leaves '
         f'as waste, which circulates through the biofilter at {s["loop_kgd"]:g} kg/d and returns as '
         'cleaned water.', '',
         f'The raceway produces {s["dw_prod"]:g} kg/d dry matter at 300 m2 and 15 g/m2/d (A-M-420):',
         '',
         '| Duckweed allocation | kg/d DM-eq |', '| --- | --- |',
         f'| Formulation feed (layers + quail + reserve draw) | {s["form"]:g} |',
         f'| Fresh tilapia ration | {s["fish_ration"]:g} |',
         f'| Fresh duck fodder (ad lib) | {s["fodder"]:g} |',
         f'| Human-grade greens to the galley (A-M-427) | {s["greens"]:g} |',
         '| Harvest margin | 0.28 |', '',
         f'The raceway runs on loop water, so the crop is the loop polisher; CP class 30 % dry '
         '(TECHTREE aquaculture.md:101; ducks.md:96 gives 35-43 % on nutrient-rich water - the '
         'X-FARM-04 trial measures ours). Loop path: AQUA_TANK -> BIOFILTER -> AQUA_UV (normally '
         'bypassed, A-M-428) -> GROWBED_A -> GROWBED_B -> DUCKWEED -> return.', '',
         '## 2. Dual root-zone growbeds', '',
         f'The {s["bed_area_total"]:g} m2 live grow area splits into two beds of {s["bed_each"]:g} m2. Each bed '
         'carries two root zones: an aerobic top zone where the plant roots take the nitrate, and an '
         'anaerobic mineralisation layer below where the fish solids break down. The beds are the '
         'loop biofilter\'s polishing stage.', '',
         '## 3. Poultry', '',
         f'{s["birds"]:g} dual-purpose layers at a {s["chick_feed"]:g} kg/d ration produce {s["eggs"]:g} kg/d '
         f'of eggs to the food store. {s["manure"]:g} kg/d of manure feeds the larvae bin; {s["chick_water"]:g} kg/d '
         f'of drinking water and {s["chick_vap"]:g} kg/d of respiration close the flock balance.', '',
         '## 4. Black-soldier-fly larvae composting', '',
         f'The bin takes {s["bsfl_in"]:g} kg/d: {s["galley_bio"]:g} kg/d galley biowaste, {s["manure"]:g} kg/d '
         f'poultry manure and {s["fish_waste"]:g} kg/d fish sludge.', '',
         f'| Product | kg/d |', '| --- | --- |',
         f'| Larvae (wet) to the layer ration | {s["larvae"]:g} |',
         f'| Frass to the solids line (compost) | {s["frass"]:g} |',
         f'| Respiration/evaporation to the AHU | {s["bsfl_vap"]:g} |', '',
         f'The larvae cover {s["larvae_frac"]:g} % of the layer ration by mass as the concentrate '
         'co-ingredient of the formulation (A-M-426). The larvae meal routes to POULTRY ONLY, never '
         'to the fish: manure-fed larvae are the pathogen bridge the produce path must not carry '
         '(TECHTREE aquaponics.md:342 food-safety note; A-M-426). The frass stages to the solids line '
         'as compost; the root zones take their nutrient from the aquaponic loop.', '',
         '## 5. Units and streams', '',
         'Farm units: AQUA_TANK, BIOFILTER, GROWBED_A, GROWBED_B, DUCKWEED, FEED_PREP, AQUA_UV, '
         'CHICKEN_COOP, DUCK_PEN, QUAIL_CAGE, RABBIT_HUTCH, BSFL_BIN, BEE_HIVE, VERMI_BIN. '
         'The streams above are the graph edges; the rates are study values from the driver groups. '
         f'Formulation closure at FEED_PREP (wet basis): in {s["fp_in"]:g} kg/d (duckweed {s["form"]:g} + '
         f'fresh larvae {s["larvae_fresh"]:g} + eggshell {s["shell"]:g}), out {s["fp_out"]:g} (layer mash '
         f'{s["lm"]:g} + quail mash {s["qm"]:g} + duck mash {s["dm_"]:g} + reserve {s["store"]:g} + reject '
         f'{s["rej"]:g} + drying vapour {s["vap"]:g} + press water {s["press"]:g} back to the '
         'beds).', '',
         '## 6. Unit roster', '',
         '| Unit | Class | Function | Design basis |', '| --- | --- | --- | --- |',
         '| AQUA_TANK | fish_tank | Fish tanks (tilapia class) | A-M-415 |',
         '| BIOFILTER | biofilter | Nitrifying biofilter (Nitrosomonas + Nitrobacter) | A-M-415 |',
         '| GROWBED_A | growbed | Aquaponic root zone A (aerobic plant roots) | A-M-229; A-M-415 |',
         '| GROWBED_B | growbed | Aquaponic root zone B (anaerobic mineralisation) | A-M-229; A-M-415 |',
         '| DUCKWEED | duckweed | Duckweed raceway (Lemna minor, azolla co-culture) | A-M-420 |',
         '| CHICKEN_COOP | coop | Layer flock, 12 birds | A-M-417 |',
         '| DUCK_PEN | pen | Duck pen, 6 Khaki Campbells | A-M-421 |',
         '| QUAIL_CAGE | cage | Coturnix quail cage bank, 20 hens | A-M-422 |',
         '| RABBIT_HUTCH | hutch | Rabbitry, 2 does + 1 buck | A-M-423 |',
         '| BSFL_BIN | bsfl_bin | Black-soldier-fly larvae composting bin | A-M-418 |',
         '| BEE_HIVE | hive | Honey bee hive (pollination + honey) | A-M-424 |',
         '| VERMI_BIN | worm_bin | Vermiculture bin (Eisenia fetida) | A-M-425 |',
         '| FEED_PREP | feed_prep | Ration formulation + reserve drying (A-M-426) | A-M-426 |',
         '| AQUA_UV | uv_sanitizer | Optional loop sanitizer, normally bypassed (A-M-428) | A-M-428 |', '',
         '## 7. Nutrition evaluation (A-M-416/426; TECHTREE husbandry classes)', '',
         '| Species | Ration kg/d | CP req % | CP supply % | Ca req % | Ca supply % | Methionine |',
         '| --- | --- | --- | --- | --- | --- | --- |',
         f'| Tilapia | {s["fish_ration"]:g} fresh | 28-35 (aquaponics.md:155) | 30 (25-35 class) | water-borne | - | limiting; declared gap, X-FARM-01 |',
         f'| Layers (12) | {s["layer_ration"]:g} formulated | 16-18 (chickens.md:176) | {s["blend_cp"]:g} | 3.5-4.0 (chickens.md:74) | {s["blend_ca"]:g} | {s["layer_met"]:g} % vs 0.38-0.45 class - in class, thin margin |',
         '| Ducks (6) | 0.87 fodder + free-range | 16-18 (ducks.md:90) | 30-43 (ducks.md:96) | free-choice (ducks.md:99) | mineral hopper | as layers |',
         f'| Quail (20) | {s["quail_ration"]:g} formulated | 20-22 (coturnix.md:177) | 30 | 2.5-3.0 (coturnix.md:60) | mineral hopper closes | {s["quail_met"]:g} % vs 0.50 - THE BINDING CASE (~1 g/d DL-met) |',
         '| Rabbits | 0.5 forage + hay | 16-18 (rabbits.md:34) | canopy forage class | 0.6-1.0 | forage | outside the loop (canopy) |', '',
         f'Loop-wide methionine supplement class: ~{s["met_gap_g_d"]} g/d DL-met equivalent (quail binding case '
         '+ the fish gap + margin). TECHTREE names synthetic DL-methionine as the standard supplement '
         '(chickens.md:176) and states methionine limits even black-soldier-fly meal quality (insect-farming.md:117). '
         'Duckweed Ca and met are unmeasured classes on our water - the X-FARM-04 trial measures them; '
         'the layer Ca closure holds only with the full eggshell return plus the larvae Ca class '
         '(5-8 %, insect-farming.md:116).', '',
         '## 8. Open items', '',
         '- Larvae-meal ration trial (X-FARM-01), flock trial (X-FARM-02), bin trial (X-FARM-03), '
         'raceway yield/CP/Ca trial (X-FARM-04), duck flock (X-FARM-05), quail cage bank (X-FARM-06), '
         'rabbitry (X-FARM-07), hive (X-FARM-08), vermi bin (X-FARM-09), FEED_PREP ration trial '
         '(X-FARM-10), greens microbiology (X-FARM-11), UV dose validation (X-FARM-12).',
         '- Methionine route decision: chemicals-sector DL-met synthesis vs the declared production '
         'penalty - decided on the X-FARM-01/02 trial results (A-M-416).',
         '- POLY_FIBER melt-spin unit after PELLET: the FR-PP textile line (A-M-429) - next unit task.',
         '- Loop water circulation rates stay study-held at zero pending the farm water-balance pass '
         '(the 40 kg/d class is the A-M-415 note).',
         '- Tilapia harvest scheduling below the optimal-growth ration class.',
         '- Mineral CaCO3 top-up logistics from the site mineral line (~1.5-2 kg/month, quail hopper '
         '+ duckweed-Ca insurance).',
         '- The locale scaling passes (microgravity, thin atmosphere) treat the animal and insect '
         'units as their own follow-on (LOCALIZATION_PLAN).', '']
    return '\n'.join(L) + '\n'


def render_hab(s):
    L = ['# Hab interior design: zoning', '',
         'Document number: AQS-HAB-002', 'Revision: A', 'Date: 2026-10-26',
         'Licence: CERN-OHL-S-2.0.', '',
         'Generated by `docs-authority/_farm_hab.py` from the `HAB` driver group (A-M-419) and the '
         'room basis of AQS-HAB-001. Study. Not a PE stamp.', '',
         f'The {s["crew"]}-crew habitation splits into functional rooms:', '',
         '| Room | Area m2 | Basis |', '| --- | --- | --- |']
    for name, area in s['rooms'].items():
        basis = 'AQS-HAB-001 room basis' if name in ('galley', 'washroom', 'private sleeping quarters') \
                else 'A-M-419 (NASA_STD_3001 class)'
        L.append(f'| {name.capitalize()} | {area:g} | {basis} |')
    L += [f'| **Total** | **{s["rooms_total"]:g}** | |', '',
          '## 1. Rooms and functions', '',
          '- **Galley (kitchen)**: meal preparation for the crew; biowaste to the BSFL bin, grey water '
          'to the treatment train, food issued from FOOD_STORE.',
          '- **Washroom (bathroom/hygiene)**: shower, sink and hygiene fixtures; grey water to the '
          'treatment train. The composting toilet follows AQS-HAB-001.',
          '- **Recreation/common day-space**: shared day use, exercise and recreation.',
          '- **Private sleeping quarters**: one quarters per crew member (separate private quarters).',
          '- **Common circulation**: circulation and utility distribution.',
          '- **Medical (6 m2)**: carried from the AQS-HAB-001 room basis.', '',
          '## 2. Edges', '',
          'The rooms carry their own service edges: wash and galley grey water to the treatment train '
          '(WASH_GREY, GAL_GREY), galley biowaste to the BSFL bin (GALLEY_BIO), prepared meals back to '
          'the habitation unit (GALLEY_MEALS), and the food issue from FOOD_STORE splits between the '
          'galley and the habitation unit (FOOD_GALLEY, FOOD_HAB).', '',
          '## 3. Open items', '',
          'Habitability design review (X-HAB-01). The room loads stay inside the HABITATION electrical '
          'duty; no separate power edges are opened at this pass.', '']
    L += ['', '## 3. Unit roster', '',
         '| Unit | Class | Function | Design basis |', '| --- | --- | --- | --- |',
         '| GALLEY | galley | Galley (kitchen) | A-M-419; AQS-HAB-001 |',
         '| WASHROOM | washroom | Washroom (hygiene) | A-M-419; AQS-HAB-001 |',
         '| MEDICAL | medical | Medical room | A-M-419; AQS-HAB-001 |',
         '| REC_DAYROOM | dayroom | Recreation/common day-space | A-M-419 |',
         '| SLEEP_QUARTERS | quarters | Private sleeping quarters (4 x 4 m2) | A-M-419; AQS-HAB-001 |',
         '| COMMON_AREA | dayroom | Common circulation/utility area | A-M-419 |', '']
    return '\n'.join(L) + '\n'


if __name__ == '__main__':
    s = study()
    write = '--write' in sys.argv
    docs = {OUT_FARM: render_farm(s), OUT_HAB: render_hab(s)}
    for path, txt in docs.items():
        if write:
            open(path, 'w').write(txt)
        else:
            print(txt)
    if write:
        print(f'{OUT_FARM} + {OUT_HAB}: written')
    print(json.dumps(s, indent=1))

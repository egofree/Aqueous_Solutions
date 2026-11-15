"""The X-FARM wet-basis balance (family migration; reference writer
flow_graph/param/farm_balance.py + its nitrate_route.tf call, ledger row
`farm_balance`, section C, PHYSICS). AQS-FARM-001, A-M-415..430, X-QA-11
(A-M-497 nutrient skid, A-M-501 eggshell grit).

The farm/hab/aquaponics web: DUCKWEED (the raceway) feeds FEED_PREP, which
rations the animals (chicken coop, quail cage, duck pen, rabbit hutch) and the
fish (AQUA_TANK via FISHF); animal manures and fish sludge feed the insect and
worm bins (BSFL_BIN, VERMI_BIN); the bins return larvae, frass, worm tea and
vermicompost to FEED_PREP and the media beds (GROWBED_A -> GROWBED_B); the beds
return water to the raceway (AQUA_LOOP4) and the raceway returns to the tank
(AQUA_RETURN2), topped up from ROOF_TANK (IA-AQUA-TOPUP); the galley closes the
food loop (FOOD_GALLEY / GALLEY_MEALS / GALLEY_BIO). Thirteen nodes close.

Why this family existed as an iteration, and why it no longer is: the larvae
meal in the layer ration looked like a fixed point (larvae meal <-> ration <->
manure <-> bin feedstock), and the v1 writer chased it with a 50-pass float
loop. On inspection the bin feedstock (galley bio + chick manure + duck manure
+ fish sludge + reject) does not contain the larvae meal term, so the recurrence
contracts in exactly one step: larvae_meal = fs_dm * larvae_frac, exactly. The
whole balance is linear equalities over driver rationals — solved here as that
algebra, with no iteration anywhere.

Grid doctrine: the solve runs on the mass_flow dimension as an integer book of
milligrams per day (mg/d — the milli-grid of the declared g/d grid unit). The
book is chosen so the committed 6-decimal kg/d schema is exactly representable:
every rate this family stamps is an integer mg count, rendered by an exact
Decimal division at stamp time. Driver and class values enter as exact
rationals (integer pairs — Fraction over Decimal(str(value))); the fractions
v1 wrote as float literals (0.7 reject moisture complement, 0.4 duck manure
share, 1/2 sludge share, 7/25 droppings share, ...) port as integer-pair
rationals. Quantisation points are v1's own: the larvae meal, fish harvest,
quail droppings, frass and worm tea quantise at 6 dp before reuse; everything
else quantises once, at stamp. Rounding is half-up on the exact rational.

The reconciliation, made structural: in v1 the free water edges (FORM_PRESS,
AQUA_LOOP4, AQUA_RETURN2, IA-AQUA-TOPUP, and the bin vapor BSFL_VAP) were
rounded independently at write while the balance stage re-reconciled them as
node closures — the two conventions differed by one milligram on FORM_PRESS
(the recorded 25.688598 <-> 25.688599 pass-to-pass flip). In v2 there is one
convention: every closure edge is the exact integer difference of its node's
other edges on the mg book, so sum(in) == sum(out) per node, exactly, by
construction. Four committed free-edge rates carry the v1 rounding residue
(each exactly +/-1 mg; the committed graph leaks 1 mg at BSFL_BIN and GROWBED_B
— demonstrated in the test); this family stamps the closing values.

The mineral-nitrate dose (nitrate_route, X-QA-11, A-M-497) ports as exact
rational chemistry: the raceway and bed uptake less the fish-loop nitrogen
return gives the mineral gap; the Ostwald/neutralisation book (2 NH3 + 2 O2 ->
NH4NO3 + H2O) at the selectivity driver splits it into the skid streams, each
quantised once at stamp. The skid's design block and continuous_kw land on the
NUT_AN node with structured provenance; the dose text the load list parses
travels verbatim in the note field.

One writer per field — what this family owns on the committed graph, and what
it deliberately does not touch:
- STAMPED: the 49 held edge rates, the 6 free (x0) edge rates, the NUT_AQUA
  dose and the IA-NUT-O2 / IA-NUT-H2O / IA-NUT-VENT skid stream rates, the
  SF-NUT_AN feed rate, the NUT_AN design block and continuous_kw, and the note
  texts this stage authored (created-edge notes, the skid feed note, the two
  retirement notes, the dose note on NUT_AN).
- NOT STAMPED (the balance family's fields, still live on the committed graph):
  the IA-NUT-NH3 draw (the balance re-solves WS_AMMONIA's feed by difference,
  R10c — committed 0.230525 against this stage's exact 0.230527; the exact
  value stays on NUT_AN params.design.nh3_kg_d), the free-edge note texts
  (balance co-authored '[free:' / 'X-PAR-02' markers), and FOOD_EXPORT (the
  balance-owned store closure). Edge topology (created/retired edges) is
  builder-authored seed data, already carried by the committed graph.

The v1 note-freeze idempotence and the [:240] truncation cap do not migrate:
assignment replaces the field and its provenance in full, and a note is data,
not an append log. A solve without the declared drivers records nothing, so
the bridge solve and the check stay byte-faithful to the seed.
"""
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction

from flow_graph.v2.grid import Qty
from flow_graph.v2.model import Prov
from flow_graph.v2.registry import fn

STAGE = 'farm_balance'
MG_PER_KG = 1000000                    # the mg book: 10^6 mg per kg
W_PER_KW = 1000

# cited husbandry classes, as integer-pair rationals (v1 float literals port)
REJECT_WET_DEN = Fraction(3, 10)       # 1 - 0.70: the press complement of the reject DM
SLUDGE_SHARE = Fraction(1, 2)          # A-M-415: half the fish feed leaves as waste
DUCK_MANURE_SHARE = Fraction(2, 5)     # A-M-421: 40 % of the duck feed
DROPPINGS_SHARE = Fraction(7, 25)      # 28 % of the quail feed
HARVEST_SHARE = Fraction(9, 10)        # 90 % of the fish ration comes back as harvest
HAB_ISSUE = Fraction(21, 5)            # 4.2 kg/d crew issue (A-M-270)
FISH_MEAT_ISSUE = Fraction(1, 20)      # 0.05 kg/d fish issue in FIN
NECTAR = Fraction(1, 5)                # nectar draw: honey at the ~25 % sugar-yield class
HONEY = Fraction(1, 20)                # 0.05 kg/d honey
QUAIL_EGG_DEFAULT = Fraction(3, 1000)  # FARM.quail.egg_kg_bird_d absent from drivers: the 3 g/bird/d class
MN = Fraction(14007, 1000)             # N molar mass, kg/kmol basis of nitrate_route.py
MH = Fraction(1008, 1000)
MO = Fraction(15999, 1000)
M_NH3 = MN + 3 * MH                    # 17.031
M_AN = 2 * MN + 4 * MH + 3 * MO        # 80.043
M_O2 = 2 * MO                          # 31.998
M_H2O = 2 * MH + MO                    # 18.015


def rat(value):
    """A v1 driver float -> its exact rational (the decimal the JSON carried).
    Deterministic: str() of a JSON float round-trips the written decimal."""
    return Fraction(Decimal(str(value)))


def mg(x, per=MG_PER_KG):
    """An exact rational -> an integer count of mg/d book units, half-up.
    `per` selects the book: MG_PER_KG for mass rates, MG_PER_G for the
    nitrogen book (g N/d), W_PER_KW for power watts."""
    n, d = x.numerator * per, x.denominator
    q, r = divmod(n, d)
    if r * 2 >= d:
        q += 1
    return q


def kg(count):
    """The exact numeric schema value of an mg count: exact Decimal division,
    then the one float the 6-dp schema stores. No arithmetic ever happens on
    the float."""
    return float(Decimal(count) / Decimal(MG_PER_KG))


def solve_balance(drv):
    """The wet-basis balance as exact algebra on the mg/d book.

    drv: the v1 drivers.json payload (values read by path). Returns a dict:
    'rates': {stream_id: integer mg/d} — every edge rate, closures included;
    'checks': {node: (in_mg, out_mg)} — integer mass conservation per node;
    'design': the nitrate skid streams as exact rationals (kg/d, kg N/d, kW);
    'dose_mg': the NUT_AQUA dose on the mg book;
    'gmeals_mg': the galley meals closure (stamped by the hab family).
    """
    def rv(path, default):
        e = drv.get(path)
        return rat(e['value']) if e else default

    # --- roster and allocation drivers (A-M-417..423) -------------------------
    birds = rv('FARM.chicken.stock_birds', Fraction(12))
    quail_n = rv('FARM.quail.stock', Fraction(20))
    ducks_n = rv('FARM.ducks.stock', Fraction(6))
    layer_dm = birds * rv('FARM.chicken.feed_kg_bird_d', Fraction(12, 100))       # A-M-417
    quail_dm = quail_n * rv('FARM.quail.feed_kg_bird_d', Fraction(25, 1000))      # A-M-422
    duck_dm = rv('FARM.ducks.feed_kg_d', Fraction(9, 10))                          # A-M-421
    fodder_dm = rv('FARM.duckweed.fodder_dm', Fraction(1, 5))
    greens_dm = rv('FARM.duckweed.greens_dm', Fraction(12, 100))
    store_dm = rv('FARM.feed_prep.store_dm', Fraction(1, 2))
    fish_ration_dm = (rv('FARM.aquaponics.fish_stock_kg', Fraction(60)) *
                      rv('FARM.aquaponics.fish_feed_kg_kg', Fraction(15, 1000)))
    egg_kg_bird = rv('FARM.chicken.egg_kg_bird_d', Fraction(5, 100))
    quail_egg_bird = rv('FARM.quail.egg_kg_bird_d', QUAIL_EGG_DEFAULT)
    duck_eggs = rv('FARM.ducks.egg_kg_d', Fraction(34, 100))

    # --- cited husbandry classes (FARM.classes; TECHTREE refs in the drivers) --
    dw_dm_frac = rv('FARM.classes.duckweed_dm_frac', Fraction(5, 100))
    mash_dm_frac = rv('FARM.classes.mash_dm_frac', Fraction(3, 10))
    larva_dm_frac = rv('FARM.classes.larva_dm_frac', Fraction(44, 100))   # TECHTREE insect-farming.md:112
    larvae_frac = rv('FARM.bsfl.larvae_frac', Fraction(15, 100))          # A-M-418
    manure_frac = rv('FARM.classes.manure_dm_frac_of_feed', Fraction(33, 100))
    manure_moist = rv('FARM.classes.layer_manure_moisture', Fraction(87, 100))
    drop_moist = rv('FARM.classes.quail_droppings_moisture', Fraction(92, 100))
    duckman_moist = rv('FARM.classes.duck_manure_moisture', Fraction(3, 4))
    sludge_moist = rv('FARM.classes.sludge_moisture', Fraction(85, 100))
    shell_frac = rv('FARM.classes.eggshell_frac', Fraction(1, 10))
    frass_frac = rv('FARM.classes.frass_wet_frac_of_feedstock', Fraction(6, 100))
    loop = rv('FARM.classes.aqua_loop_kgd', Fraction(200))
    reject_dm = rv('FARM.feed_prep.reject_dm', Fraction(2, 100))
    galley_bio_dm = rv('FARM.bsfl.galley_bio_dm', Fraction(1, 10))
    galley_bio_wet = rv('FARM.bsfl.galley_bio_wet', Fraction(1, 2))

    eggs = birds * egg_kg_bird
    shell_dm = eggs * shell_frac
    sludge_dm = fish_ration_dm * SLUDGE_SHARE                    # A-M-415
    quail_eggs = quail_n * quail_egg_bird

    # --- the larvae loop, solved exactly ---------------------------------------
    # fs_dm (the bin feedstock DM) carries no larvae term, so the v1 fixed
    # point contracts in one step: larvae_meal = fs_dm * larvae_frac, exactly.
    chick_manure_dm = layer_dm * manure_frac
    duck_manure_dm = duck_dm * DUCK_MANURE_SHARE
    fs_dm = galley_bio_dm + chick_manure_dm + duck_manure_dm + sludge_dm + reject_dm
    larvae_meal = mg(fs_dm * larvae_frac)                        # v1 quantises here, 6 dp
    L6 = Fraction(larvae_meal, MG_PER_KG)                        # the quantised meal re-enters
    layer_dw_dm = layer_dm - L6 - shell_dm
    form_dm = layer_dw_dm + quail_dm + store_dm

    # --- wet-basis rates, integer mg/d -----------------------------------------
    R = {}
    R['DUCK_FORM'] = mg(form_dm / dw_dm_frac)
    R['DUCK_FISH'] = mg(fish_ration_dm / dw_dm_frac)
    R['DUCK_FODDER'] = mg(fodder_dm / dw_dm_frac)
    R['DUCK_GREENS'] = mg(greens_dm / dw_dm_frac)
    R['LARVAE_FRESH'] = mg(L6 / larva_dm_frac)
    R['EGGSHELL_RET'] = mg(shell_dm)
    LM = layer_dw_dm / mash_dm_frac + L6 + shell_dm - rv('FARM.classes.ca_hopper_kgd', Fraction(35, 1000))
    R['LAYER_FEED'] = mg(LM)
    R['QUAIL_RATION'] = mg(quail_dm / mash_dm_frac)
    R['DUCK_RATION'] = mg((duck_dm - fodder_dm) / mash_dm_frac)
    R['DUCK_STORE'] = mg(store_dm)
    R['FORM_REJECT'] = mg(reject_dm / REJECT_WET_DEN)
    R['FORM_VAP'] = mg(store_dm * (1 / dw_dm_frac - 1))
    R['FISH_SLUDGE'] = mg(sludge_dm / (1 - sludge_moist))
    R['FISH_HARVEST'] = mg(fish_ration_dm * HARVEST_SHARE)       # v1 quantises here
    CHW = birds * rv('FARM.classes.chicken_water_kg_bird_d', Fraction(3, 100))
    CVAP = birds * rv('FARM.classes.chicken_resp_kg_bird_d', Fraction(6, 100))
    R['IA-CHICK-H2O'] = mg(CHW)
    R['CHICK_VAP'] = mg(CVAP)
    R['EGG_HARVEST'] = mg(eggs)
    R['CHICK_MANURE'] = R['LAYER_FEED'] + R['IA-CHICK-H2O'] - R['EGG_HARVEST'] - R['CHICK_VAP']
    QW = quail_n * rv('FARM.classes.quail_water_kg_bird_d', Fraction(1, 100))
    qdrop = mg((quail_dm * DROPPINGS_SHARE) / (1 - drop_moist))  # v1 quantises here
    grit = rv('FARM.classes.ca_hopper_kgd', Fraction(35, 1000))  # X-QA-11, A-M-501 free-choice grit
    R['QUAIL_H2O'] = mg(QW)
    R['QUAIL_DROP'] = qdrop
    R['SHELL_GRIT'] = mg(grit)
    R['QUAIL_EGGS'] = mg(quail_eggs)
    R['QUAIL_VAP'] = R['QUAIL_RATION'] + R['QUAIL_H2O'] + R['SHELL_GRIT'] - R['QUAIL_EGGS'] - qdrop
    DUCKW = ducks_n * rv('FARM.classes.duck_water_kg_bird_d', Fraction(33, 100))
    DMAN = duck_manure_dm / (1 - duckman_moist)
    DVAP = rv('FARM.classes.duck_resp_kg_d', Fraction(4, 5))
    R['IA-DUCK-H2O'] = mg(DUCKW)
    R['DUCK_MANURE'] = mg(DMAN)
    R['DUCK_VAP'] = mg(DVAP)
    R['DUCK_EGGS'] = mg(duck_eggs)
    R['DUCK_GREY'] = R['DUCK_FODDER'] + R['DUCK_RATION'] + R['IA-DUCK-H2O'] - R['DUCK_EGGS'] - R['DUCK_MANURE'] - R['DUCK_VAP']
    RFOR = rv('FARM.rabbit.feed_kg_d', Fraction(9, 10))
    RMEAT = rv('FARM.rabbit.meat_kg_d', Fraction(1, 10))
    RVAP = rv('FARM.classes.rabbit_resp_kg_d', Fraction(1, 10))
    R['RABBIT_FORAGE'] = mg(RFOR)
    R['RABBIT_MEAT'] = mg(RMEAT)
    R['RABBIT_VAP'] = mg(RVAP)
    R['RABBIT_MANURE'] = R['RABBIT_FORAGE'] - R['RABBIT_MEAT'] - R['RABBIT_VAP']
    R['GALLEY_BIO'] = mg(galley_bio_wet)
    binin = R['GALLEY_BIO'] + R['CHICK_MANURE'] + R['FISH_SLUDGE'] + R['DUCK_MANURE'] + R['FORM_REJECT']
    frass = mg(Fraction(binin, MG_PER_KG) * frass_frac)          # v1 quantises here
    R['FRASS'] = frass
    R['BSFL_VAP'] = binin - R['LARVAE_FRESH'] - frass            # BSFL_BIN closure
    VFEED = rv('FARM.classes.vermi_feed_kgd', Fraction(1))
    VCOMP = rv('FARM.classes.vermicompost_kgd', Fraction(19, 10))
    R['VERMI_FEED'] = mg(VFEED)
    R['VERMICOMPOST'] = mg(VCOMP)
    R['WORM_TEA'] = R['VERMI_FEED'] + qdrop - R['VERMICOMPOST']  # VERMI_BIN closure
    R['BED_GREENS'] = mg(rv('FARM.classes.bed_greens_kgd', Fraction(4)))
    R['GAL_GREY'] = mg(rv('FARM.classes.galley_grey_kgd', Fraction(1)))
    R['FOOD_GALLEY'] = R['BED_GREENS']                           # bed greens re-issue to the galley
    gmeals = R['FOOD_GALLEY'] + R['DUCK_GREENS'] - mg(galley_bio_wet) - R['EGGSHELL_RET'] - R['GAL_GREY']
    fin = (mg(HAB_ISSUE) + R['FISH_HARVEST'] + R['EGG_HARVEST'] + R['DUCK_EGGS'] + R['QUAIL_EGGS'] +
           R['RABBIT_MEAT'] + mg(FISH_MEAT_ISSUE) + R['DUCK_STORE'] + R['BED_GREENS'])
    R['FOOD_HAB'] = fin - mg(HAB_ISSUE) - R['FOOD_GALLEY']       # FOOD_STORE closure
    R['HONEY'] = mg(HONEY)
    R['NECTAR_FORAGE'] = mg(NECTAR)
    R['BEE_VAP'] = mg(NECTAR) - mg(HONEY)                        # hive respiration remainder
    R['AQUA_LOOP1'] = mg(loop)
    R['AQUA_BYPASS'] = mg(loop)
    R['AQUA_NUT'] = 0
    R['AQUA_SAN'] = 0

    # --- mineral-nitrate closure (X-QA-11, A-M-430/497): exact rationals -------
    dm_n = rv('FARM.duckweed.dm_N_wt', Fraction(55, 1000))
    bed_dm_frac = rv('FARM.classes.bed_greens_dm_frac', Fraction(5, 100))
    fish_n = rv('FARM.aquaponics.fish_N_return_g_d', Fraction(135, 10))
    n_wt = rv('FARM.classes.nutrient_N_wt', Fraction(45, 1000))
    uptake_race_N = (Fraction(R['DUCK_FORM'] + R['DUCK_FISH'] + R['DUCK_FODDER'] + R['DUCK_GREENS'], MG_PER_KG)
                     * dw_dm_frac * dm_n * 1000)                 # g N/d, exact
    uptake_bed_N = Fraction(R['BED_GREENS'], MG_PER_KG) * bed_dm_frac * dm_n * 1000
    gap_N = max(Fraction(0), uptake_race_N + uptake_bed_N - fish_n) / 1000   # kg N/d, exact
    dose_exact = gap_N / n_wt                                    # kg/d, exact
    dose_mg = mg(dose_exact)
    R['NUT_AQUA'] = dose_mg

    # --- the loop closures on the mg book (the structural fix) -----------------
    R['AQUA_LOOP3'] = mg(loop) + R['VERMICOMPOST'] + R['WORM_TEA']             # GROWBED_A pass-through
    R['FORM_PRESS'] = (R['DUCK_FORM'] + R['LARVAE_FRESH'] + R['EGGSHELL_RET']
                       - (R['LAYER_FEED'] + R['QUAIL_RATION'] + R['DUCK_RATION']
                          + R['DUCK_STORE'] + R['FORM_REJECT'] + R['FORM_VAP'])
                       - R['SHELL_GRIT'])                                      # FEED_PREP closure
    R['BED_ET'] = mg(rv('FARM.classes.bed_et_kgd', Fraction(5)))
    R['AQUA_LOOP4'] = (R['AQUA_LOOP3'] + R['RABBIT_MANURE'] + R['FORM_PRESS']
                       - R['BED_GREENS'] - R['BED_ET'])                        # GROWBED_B closure
    R['AQUA_RETURN2'] = (R['AQUA_LOOP4'] + dose_mg
                         - (R['DUCK_FORM'] + R['DUCK_FISH'] + R['DUCK_FODDER'] + R['DUCK_GREENS']))  # DUCKWEED closure
    R['IA-AQUA-TOPUP'] = (mg(loop) + R['FISH_SLUDGE'] + R['FISH_HARVEST']
                          - R['AQUA_RETURN2'] - R['DUCK_FISH'])                # AQUA_TANK closure

    # --- nitrate skid stream book (nitrate_route.design, exact chemistry) ------
    sel = rv('nut_an_selectivity', Fraction(97, 100))
    an = gap_N * M_AN / (2 * MN)                 # product carries both nitrate and ammonium N
    nh3 = an * 2 * M_NH3 / M_AN / sel
    o2 = an * 2 * M_O2 / M_AN / sel
    rxn_h2o = an * M_H2O / M_AN                  # of reaction; stays in the solution
    vent = nh3 + o2 - an - rxn_h2o               # unconverted slip to NOX_SCRUB (by difference)
    dil = dose_exact - an - rxn_h2o              # dilution water from ROOF_TANK
    kw = rv('nut_an_kW', Fraction(6, 100))
    assert min(an, dose_exact, nh3, o2, rxn_h2o, dil) >= 0 and vent >= 0, \
        'farm_balance: negative nitrate-route stream at the computed mineral gap'
    design = {'gap_N': gap_N, 'an': an, 'dose': dose_exact, 'nh3': nh3, 'o2': o2,
              'rxn_h2o': rxn_h2o, 'dil': dil, 'vent': vent, 'kw': kw}

    # --- integer mass conservation per node (the proof, by construction) -------
    C = {
        'DUCKWEED': ([R['AQUA_LOOP4'] + dose_mg],
                     [R['DUCK_FORM'], R['DUCK_FISH'], R['DUCK_FODDER'], R['DUCK_GREENS'], R['AQUA_RETURN2']]),
        'AQUA_TANK': ([R['AQUA_RETURN2'], R['DUCK_FISH'], R['IA-AQUA-TOPUP']],
                      [mg(loop), R['FISH_SLUDGE'], R['FISH_HARVEST']]),
        'AQUA_UV': ([0], [0]),
        'FEED_PREP': ([R['DUCK_FORM'], R['LARVAE_FRESH'], R['EGGSHELL_RET']],
                      [R['LAYER_FEED'], R['QUAIL_RATION'], R['DUCK_RATION'], R['DUCK_STORE'],
                       R['FORM_REJECT'], R['FORM_VAP'], R['FORM_PRESS'], R['SHELL_GRIT']]),
        'CHICKEN_COOP': ([R['LAYER_FEED'], R['IA-CHICK-H2O']],
                         [R['EGG_HARVEST'], R['CHICK_VAP'], R['CHICK_MANURE']]),
        'QUAIL_CAGE': ([R['QUAIL_RATION'], R['QUAIL_H2O'], R['SHELL_GRIT']],
                       [R['QUAIL_EGGS'], R['QUAIL_DROP'], R['QUAIL_VAP']]),
        'DUCK_PEN': ([R['DUCK_FODDER'], R['DUCK_RATION'], R['IA-DUCK-H2O']],
                     [R['DUCK_EGGS'], R['DUCK_MANURE'], R['DUCK_VAP'], R['DUCK_GREY']]),
        'RABBIT_HUTCH': ([R['RABBIT_FORAGE']], [R['RABBIT_MEAT'], R['RABBIT_VAP'], R['RABBIT_MANURE']]),
        'BSFL_BIN': ([mg(galley_bio_wet), R['CHICK_MANURE'], R['FISH_SLUDGE'], R['DUCK_MANURE'], R['FORM_REJECT']],
                     [R['LARVAE_FRESH'], R['FRASS'], R['BSFL_VAP']]),
        'VERMI_BIN': ([R['VERMI_FEED'], R['QUAIL_DROP']], [R['VERMICOMPOST'], R['WORM_TEA']]),
        'GROWBED_A': ([mg(loop) + R['VERMICOMPOST'] + R['WORM_TEA']], [R['AQUA_LOOP3']]),
        'GROWBED_B': ([R['AQUA_LOOP3'], R['RABBIT_MANURE'], R['FORM_PRESS']],
                      [R['AQUA_LOOP4'], R['BED_GREENS'], R['BED_ET']]),
        'GALLEY': ([R['FOOD_GALLEY'], R['DUCK_GREENS']],
                   [gmeals, mg(galley_bio_wet), R['EGGSHELL_RET'], R['GAL_GREY']]),
        'FOOD_STORE': ([fin], [mg(HAB_ISSUE), R['FOOD_GALLEY'], R['FOOD_HAB']]),
    }
    residuals = {u: sum(i) - sum(o) for u, (i, o) in C.items() if sum(i) != sum(o)}
    assert not residuals, f'farm_balance: node residual on the mg book: {residuals}'
    return {'rates': R, 'checks': {u: (sum(i), sum(o)) for u, (i, o) in C.items()},
            'design': design, 'dose_mg': dose_mg, 'gmeals_mg': gmeals}


# note texts this stage authored on the committed graph (raw string fields the
# downstream stages parse; the structured provenance rides beside them)
NOTE_LARVAE = ('fresh larvae at the 44 % DM class (TECHTREE insect-farming.md:112)'
               ' (X-FARM wet-basis, farm_balance.py)')
NOTE_DUCK_RATION = 'duck mash at the mash DM class (A-M-421 x A-M-426) (X-FARM wet-basis, farm_balance.py)'
NOTE_BED_GREENS = 'bed greens class (FARM.classes.bed_greens_kgd) (X-FARM wet-basis, farm_balance.py)'
NOTE_GAL_GREY = 'galley grey class (AQS-HAB-001 services) (X-FARM wet-basis, farm_balance.py)'
NOTE_SHELL_GRIT = ('the galley shell return splits to the grit (X-QA-11, A-M-501; TECHTREE coturnix.md:60 Ca class); '
                   're-pointed from the dock by the shell-grit route (X-FARM wet-basis, farm_balance.py)')
NOTE_SF_FEED = ('X-RTE TF: on-site ammonium-nitrate nutrient skid (X-QA-11, A-M-497): feed equal to '
                'NUT_AN continuous_kw.')
NOTE_CA_HOPPER_RETIRED = ('Retired by the eggshell-grit route (X-QA-11, A-M-501): the galley shell return '
                          '(EGGSHELL_RET, baked crushed eggshell at the ~38 g Ca/d basis) splits to the free-choice '
                          'quail hopper on SHELL_GRIT. Was the dock mineral-manifest CaCO3 line (A-M-430).')
NOTE_NUT_BED_RETIRED = ('Retired by the on-site nutrient skid (X-QA-11, A-M-497): the media-bed uptake is '
                        'smaller than the fish-stock nitrogen the biofilter returns to the loop, and the '
                        'loop passes the beds before the raceway, so the loop nitrate covers the beds and '
                        'the skid doses the whole mineral gap on NUT_AQUA. Was the dock mineral-manifest '
                        'bed dose (A-M-430).')
TAG_NUT = 'X-RTE TF: on-site ammonium-nitrate nutrient skid (X-QA-11, A-M-497)'

# every edge rate this family stamps (stream_id order = the v1 held dict, then
# the free/x0 dict, then the nitrate route's stream rates)
HELD = ('DUCK_FORM', 'DUCK_FISH', 'DUCK_FODDER', 'DUCK_GREENS', 'LARVAE_FRESH', 'EGGSHELL_RET',
        'LAYER_FEED', 'QUAIL_RATION', 'DUCK_RATION', 'DUCK_STORE', 'FORM_REJECT', 'FORM_VAP',
        'FISH_SLUDGE', 'FISH_HARVEST', 'CHICK_MANURE', 'CHICK_VAP', 'IA-CHICK-H2O', 'QUAIL_DROP',
        'QUAIL_VAP', 'QUAIL_H2O', 'DUCK_MANURE', 'DUCK_VAP', 'IA-DUCK-H2O', 'DUCK_EGGS', 'DUCK_GREY',
        'QUAIL_EGGS', 'RABBIT_FORAGE', 'RABBIT_MEAT', 'RABBIT_VAP', 'RABBIT_MANURE', 'FRASS',
        'BSFL_VAP', 'GALLEY_BIO', 'EGG_HARVEST', 'BED_GREENS', 'HONEY', 'NECTAR_FORAGE', 'BEE_VAP',
        'FOOD_GALLEY', 'FOOD_HAB', 'SHELL_GRIT', 'VERMI_FEED', 'VERMICOMPOST', 'WORM_TEA', 'GAL_GREY',
        'AQUA_LOOP1', 'AQUA_BYPASS', 'AQUA_NUT', 'AQUA_SAN')
FREE = ('AQUA_RETURN2', 'IA-AQUA-TOPUP', 'AQUA_LOOP4', 'AQUA_LOOP3', 'FORM_PRESS', 'BED_ET')
NUT_RATE = ('NUT_AQUA', 'IA-NUT-O2', 'IA-NUT-H2O', 'IA-NUT-VENT')
RATE_NOTES = ('LARVAE_FRESH', 'DUCK_RATION', 'BED_GREENS', 'GAL_GREY', 'SHELL_GRIT')


def _edge_field(b, sid, path, value, prov):
    """Record a computed sub-field of an edge rate (e.g. rate.value, rate.note).
    The registry's set_edge_rate replaces the whole rate object; this family
    stamps inside the v1 rate schema ({value, unit, status, note}), so the
    untouched schema keys (unit, status) stay byte-faithful. Provenance lands
    in the edge's structured provenance list like any computed field."""
    b.edges[sid]                                  # fails loudly on an unknown stream
    b.computed[('edge', sid, path)] = (value, Prov(**prov))


def _prov(basis, ref=None):
    p = {'stage': STAGE, 'basis': basis}
    if ref:
        p['ref'] = ref
    return p


@fn('farm_balance', 'the X-FARM wet-basis balance: the farm/hab/aquaponics loop solved as exact '
    'algebra on integer mg/d (AQS-FARM-001; A-M-415..430; the larvae loop closed in one step), '
    'the mineral-nitrate dose from the crop uptake less the fish-loop return (X-QA-11, A-M-497), '
    'and the eggshell-grit shell split (X-QA-11, A-M-501)')
def farm_balance(b, inputs):
    drv = inputs.get('drivers')
    if drv is None:
        # The declared inputs are absent (a bridge solve or a check pass carries
        # no driver payload): the stage cannot invent its drivers, so it records
        # nothing and the seed stands.
        return

    S = solve_balance(drv)
    R, D = S['rates'], S['design']
    held_basis = 'the wet-basis rate from the roster, flock and class drivers (AQS-FARM-001; A-M-415..425)'
    free_basis = 'the exact closure of its node on the mg/d book: integer in == integer out (the x0 reconciliation, structural)'
    for sid in HELD:
        _edge_field(b, sid, 'rate.value', kg(R[sid]), _prov(held_basis))
    for sid in FREE:
        _edge_field(b, sid, 'rate.value', kg(R[sid]), _prov(free_basis, 'A-M-426'))

    # the notes this stage authored, verbatim raw strings beside the provenance
    note_basis = 'the stage-authored parse-able note text, carried verbatim'
    _edge_field(b, 'LARVAE_FRESH', 'rate.note', NOTE_LARVAE, _prov(note_basis, 'A-M-418'))
    _edge_field(b, 'DUCK_RATION', 'rate.note', NOTE_DUCK_RATION, _prov(note_basis, 'A-M-421'))
    _edge_field(b, 'BED_GREENS', 'rate.note', NOTE_BED_GREENS, _prov(note_basis))
    _edge_field(b, 'GAL_GREY', 'rate.note', NOTE_GAL_GREY, _prov(note_basis, 'AQS-HAB-001'))
    _edge_field(b, 'SHELL_GRIT', 'rate.note', NOTE_SHELL_GRIT, _prov(note_basis, 'A-M-501'))

    # the on-site ammonium-nitrate skid (X-QA-11, A-M-497)
    dose_mg = S['dose_mg']
    stream_mg = {'NUT_AQUA': dose_mg, 'IA-NUT-O2': mg(D['o2']),
                 'IA-NUT-H2O': mg(D['dil']), 'IA-NUT-VENT': mg(D['vent'])}
    for sid, count in stream_mg.items():
        _edge_field(b, sid, 'rate.value', kg(count),
                    _prov('the nitrate-route stream from the exact Ostwald/neutralisation book at the '
                          'selectivity driver (X-QA-11, A-M-497)', 'A-M-497'))
    watts = mg(D['kw'], W_PER_KW)
    _edge_field(b, 'SF-NUT_AN', 'rate.value', float(Decimal(watts) / Decimal(W_PER_KW)),
                _prov('the skid feed equals NUT_AN continuous_kw (X-QA-11, A-M-497)', 'A-M-497'))
    _edge_field(b, 'SF-NUT_AN', 'rate.note', NOTE_SF_FEED, _prov(note_basis, 'A-M-497'))
    _edge_field(b, 'CA_HOPPER', 'rate.value', kg(0), _prov('retired with the eggshell-grit route (A-M-501)'))
    _edge_field(b, 'CA_HOPPER', 'rate.note', NOTE_CA_HOPPER_RETIRED,
                _prov('the retirement record text (A-M-501)', 'A-M-501'))
    _edge_field(b, 'NUT_AQUA_BED', 'rate.value', kg(0), _prov('retired with the on-site nutrient skid (A-M-497)'))
    _edge_field(b, 'NUT_AQUA_BED', 'rate.note', NOTE_NUT_BED_RETIRED,
                _prov('the retirement record text (A-M-497)', 'A-M-497'))

    # the NUT_AN design block: the skid streams as exact rationals, each
    # quantised once at stamp, keys in the committed schema order
    design_schema = {
        'gap_N_kg_d': kg(mg(D['gap_N'])),
        'an_kg_d': kg(mg(D['an'])),
        'dose_kg_d': kg(dose_mg),
        'nh3_kg_d': kg(mg(D['nh3'])),
        'o2_kg_d': kg(mg(D['o2'])),
        'rxn_h2o_kg_d': kg(mg(D['rxn_h2o'])),
        'dil_kg_d': kg(mg(D['dil'])),
        'vent_kg_d': kg(mg(D['vent'])),
        'kw': float(Decimal(mg(D['kw'], W_PER_KW)) / Decimal(W_PER_KW)),
    }
    b.set_node_field('NUT_AN', 'params.design', design_schema,
                     _prov('the skid stream book: the mineral gap at the registered N strength through the '
                           'Ostwald oxidation and the neutralisation, exact rationals quantised once '
                           '(X-QA-11, A-M-497)', 'A-M-497'))
    b.set_node_field('NUT_AN', 'continuous_kw.value', Qty(watts, 'power'),
                     _prov('the oxidation starter, metering pumps and controls at the nut_an_kW class '
                           '(X-QA-11, A-M-497)', 'A-M-497'))
    dose_txt = (Decimal(dose_mg) / Decimal(MG_PER_KG)).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)
    b.set_node_field('NUT_AN', 'continuous_kw.note',
                     f'{TAG_NUT}: oxidation starter, metering pumps and controls at the {dose_txt} kg/d dose '
                     f'(nut_an_kW, A-M-497).',
                     _prov('the skid load note; the dose figure is derived from the mg book', 'A-M-497'))

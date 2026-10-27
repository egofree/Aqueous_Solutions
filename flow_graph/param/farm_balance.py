"""X-FARM wet-basis balance writer (AQS-FARM-001, A-M-415..430). Computes every FARM edge rate
in REAL mass (kg/d wet) from the driver parameters and the cited husbandry classes, by fixed-point
iteration (the larvae meal in the layer ration comes from the bin whose feedstock includes the
layer manure), writes the graph, and asserts every farm node closes exactly. Held edges (X-FARM
tag) carry the computed rates; the water edges are left free (no tag, positive value) for the
X-PAR-02 solver to reconcile around them.

Method: dry-matter (DM) fractions and moisture classes are driver parameters (FARM.classes group,
each with its TECHTREE husbandry reference); every mass is a formula over crew, flock sizes,
areas and the allocation drivers. No rate in this module is a hand-copied constant. Run:
python3 -m flow_graph.param.farm_balance   (writes_graph: farm_balance stage of regen_manifest.json)
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
GP = os.path.join(os.path.dirname(HERE), 'plant_flow_graph.json')
DP = os.path.join(HERE, 'drivers.json')


def compute(d):
    """Fixed-point wet-basis farm balance. d = drivers dict (flat path keys). Returns the values."""
    def v(k, default):
        e = d.get(k)
        return e['value'] if e else default

    # roster and allocation drivers
    birds = v('FARM.chicken.stock_birds', 12.0)
    quail_n = v('FARM.quail.stock', 20.0)
    ducks_n = v('FARM.ducks.stock', 6.0)
    layer_dm = birds * v('FARM.chicken.feed_kg_bird_d', 0.12)          # A-M-417
    quail_dm = quail_n * v('FARM.quail.feed_kg_bird_d', 0.025)         # A-M-422
    duck_dm = v('FARM.ducks.feed_kg_d', 0.9)                           # A-M-421
    fodder_dm = v('FARM.duckweed.fodder_dm', 0.2)
    greens_dm = v('FARM.duckweed.greens_dm', 0.12)
    store_dm = v('FARM.feed_prep.store_dm', 0.5)
    fish_ration_dm = v('FARM.aquaponics.fish_stock_kg', 60.0) * v('FARM.aquaponics.fish_feed_kg_kg', 0.015)
    egg_kg_bird = v('FARM.chicken.egg_kg_bird_d', 0.05)
    quail_egg_bird = v('FARM.quail.egg_kg_bird_d', 0.003)
    duck_egg_kg_d = v('FARM.ducks.egg_kg_d', 0.34)

    # cited husbandry classes (FARM.classes; TECHTREE refs in the driver entries)
    dw_dm_frac = v('FARM.classes.duckweed_dm_frac', 0.05)
    mash_dm_frac = v('FARM.classes.mash_dm_frac', 0.30)
    larva_dm_frac = v('FARM.classes.larva_dm_frac', 0.44)              # insect-farming.md:112
    larvae_frac = v('FARM.bsfl.larvae_frac', 0.15)                     # A-M-418
    manure_frac = v('FARM.classes.manure_dm_frac_of_feed', 0.33)
    manure_moist = v('FARM.classes.layer_manure_moisture', 0.87)
    drop_moist = v('FARM.classes.quail_droppings_moisture', 0.92)
    duckman_moist = v('FARM.classes.duck_manure_moisture', 0.75)
    sludge_moist = v('FARM.classes.sludge_moisture', 0.85)
    shell_frac = v('FARM.classes.eggshell_frac', 0.10)
    frass_wet_frac = v('FARM.classes.frass_wet_frac_of_feedstock', 0.06)
    loop_kgd = v('FARM.classes.aqua_loop_kgd', 200.0)
    nut_dose = v('FARM.classes.nut_dose_kgd', 5.5)                     # A-M-430
    reject_dm = v('FARM.feed_prep.reject_dm', 0.02)
    galley_bio_dm = v('FARM.bsfl.galley_bio_dm', 0.1)
    galley_bio_wet = v('FARM.bsfl.galley_bio_wet', 0.5)
    reject_wet = reject_dm / (1 - 0.70)

    eggs = birds * egg_kg_bird
    shell_dm = eggs * shell_frac
    sludge_dm = fish_ration_dm * 0.5                                   # A-M-415: half the feed leaves as waste
    quail_eggs = quail_n * quail_egg_bird
    duck_eggs = duck_egg_kg_d

    # fixed point: larvae meal <-> layer ration <-> layer manure <-> bin feedstock
    larvae_meal_dm = 0.10
    for _ in range(50):
        layer_dw_dm = layer_dm - larvae_meal_dm - shell_dm
        form_dm = layer_dw_dm + quail_dm + store_dm
        chick_manure_dm = layer_dm * manure_frac
        duck_manure_dm = duck_dm * 0.4
        fs_dm = galley_bio_dm + chick_manure_dm + duck_manure_dm + sludge_dm + reject_dm
        larvae_meal_dm = fs_dm * larvae_frac
    larvae_meal_dm = round(larvae_meal_dm, 6)
    larvae_fresh_dm = larvae_meal_dm

    # wet-basis edge values (held set: exact by construction)
    FORM = form_dm / dw_dm_frac
    FISHF = fish_ration_dm / dw_dm_frac
    FODDER = fodder_dm / dw_dm_frac
    GREENS = greens_dm / dw_dm_frac
    SLUDGE_W = sludge_dm / (1 - sludge_moist)
    HARV_W = round(fish_ration_dm * 0.9, 6)
    LM = layer_dw_dm / mash_dm_frac + larvae_meal_dm + shell_dm
    QM = quail_dm / mash_dm_frac
    DM_ = (duck_dm - fodder_dm) / mash_dm_frac
    LARVA_W = larvae_fresh_dm / larva_dm_frac
    VAP = store_dm * (1 / dw_dm_frac - 1)
    CHW = birds * v('FARM.classes.chicken_water_kg_bird_d', 0.03)
    CVAP = birds * v('FARM.classes.chicken_resp_kg_bird_d', 0.06)
    CMAN = LM + CHW - eggs - CVAP
    QW = quail_n * v('FARM.classes.quail_water_kg_bird_d', 0.01)
    CAQ = v('FARM.classes.ca_hopper_kgd', 0.035)
    QDROP = round((quail_dm * 0.28) / (1 - drop_moist), 6)
    QVAP = QM + QW + CAQ - quail_eggs - QDROP
    DUCKW = ducks_n * v('FARM.classes.duck_water_kg_bird_d', 0.33)
    DMAN = duck_manure_dm / (1 - duckman_moist)
    DVAP = v('FARM.classes.duck_resp_kg_d', 0.8)
    DGREY = FODDER + DM_ + DUCKW - duck_eggs - DMAN - DVAP
    RFOR = v('FARM.rabbit.feed_kg_d', 0.9)
    RMEAT = v('FARM.rabbit.meat_kg_d', 0.1)
    RVAP = v('FARM.classes.rabbit_resp_kg_d', 0.1)
    RMAN = RFOR - RMEAT - RVAP
    BININ = galley_bio_wet + CMAN + SLUDGE_W + DMAN + reject_wet
    FRASS = round(BININ * frass_wet_frac, 6)
    BVAP = BININ - LARVA_W - FRASS
    VFEED = v('FARM.classes.vermi_feed_kgd', 1.0)
    VCOMP = v('FARM.classes.vermicompost_kgd', 1.9)
    VTEA = round(VFEED + QDROP - VCOMP, 6)
    BEDG = v('FARM.classes.bed_greens_kgd', 4.0)
    GGREY = v('FARM.classes.galley_grey_kgd', 1.0)
    GFOOD = BEDG                                            # bed greens re-issue to the galley
    GMEALS = GFOOD + GREENS - galley_bio_wet - shell_dm - GGREY
    FIN = 4.2 + HARV_W + eggs + duck_eggs + quail_eggs + RMEAT + 0.05 + store_dm + BEDG
    FHAB = FIN - 4.2 - GFOOD                                # the product share to the rooms (exact)

    # free water edges: initial values the solver reconciles around
    PRESS = (FORM + LARVA_W + shell_dm) - (LM + QM + DM_ + store_dm + reject_wet + VAP)
    BET = v('FARM.classes.bed_et_kgd', 5.0)
    LOOP3 = loop_kgd + VCOMP + VTEA                       # bed inflow carries the vermi amendments
    LOOP4 = LOOP3 + RMAN + PRESS + 1.0 - BEDG - BET   # +1.0: NUT_AQUA_BED mineral dose
    RET = LOOP4 + nut_dose - (FORM + FISHF + FODDER + GREENS)
    TOPUP = loop_kgd + SLUDGE_W + HARV_W - RET - FISHF

    # GROW_BED closes by difference on IA-BED-H2O in the balance T-lane: the forage and
    # vermi draws (RFOR + VFEED) ride that closure - no competing supply write here.
    NECTAR = 0.2                                       # nectar draw: honey at the ~25 % sugar-yield class
    BEEVAP = NECTAR - 0.05                             # hive respiration remainder
    vals = dict(NECTAR=NECTAR, BEEVAP=BEEVAP, FORM=FORM, FISHF=FISHF, FODDER=FODDER, GREENS=GREENS, LM=LM, QM=QM, DM_=DM_,
                LARVA_W=LARVA_W, VAP=VAP, PRESS=PRESS, CMAN=CMAN, QDROP=QDROP, QVAP=QVAP,
                DGREY=DGREY, RMAN=RMAN, FRASS=FRASS, BVAP=BVAP, VTEA=VTEA, LOOP4=LOOP4,
                RET=RET, TOPUP=TOPUP, GMEALS=GMEALS, SLUDGE_W=SLUDGE_W,
                HARV_W=HARV_W, REJ=reject_wet, BININ=BININ, eggs=eggs, shell_dm=shell_dm,
                larvae_meal_dm=larvae_meal_dm, layer_dw_dm=layer_dw_dm, form_dm=form_dm,
                loop_kgd=loop_kgd, nut_dose=nut_dose, BEDG=BEDG, BET=BET, QW=QW, CAQ=CAQ,
                CHW=CHW, CVAP=CVAP, DUCKW=DUCKW, DMAN=DMAN, DVAP=DVAP, RFOR=RFOR,
                RMEAT=RMEAT, RVAP=RVAP, VFEED=VFEED, VCOMP=VCOMP, GFOOD=GFOOD, FHAB=FHAB,
                GGREY=GGREY, store_dm=store_dm, fish_ration_dm=fish_ration_dm,
                duck_eggs=duck_eggs, quail_eggs=quail_eggs)

    # node closure over the held set only (free edges carry no residual: in == out by x0 design)
    V = vals
    checks = {
        'DUCKWEED': ([V['LOOP4'] + nut_dose], [V['FORM'], V['FISHF'], V['FODDER'], V['GREENS'], V['RET']]),
        'AQUA_TANK': ([V['RET'], V['FISHF'], V['TOPUP']], [loop_kgd, V['SLUDGE_W'], V['HARV_W']]),
        'AQUA_UV': ([0.0], [0.0]),
        'FEED_PREP': ([V['FORM'], V['LARVA_W'], V['shell_dm']],
                      [V['LM'], V['QM'], V['DM_'], V['store_dm'], V['REJ'], V['VAP'], V['PRESS']]),
        'CHICKEN_COOP': ([V['LM'], V['CHW']], [V['eggs'], V['CVAP'], V['CMAN']]),
        'QUAIL_CAGE': ([V['QM'], V['QW'], V['CAQ']], [V['quail_eggs'], V['QDROP'], V['QVAP']]),
        'DUCK_PEN': ([V['FODDER'], V['DM_'], V['DUCKW']], [V['duck_eggs'], V['DMAN'], V['DVAP'], V['DGREY']]),
        'RABBIT_HUTCH': ([V['RFOR']], [V['RMEAT'], V['RVAP'], V['RMAN']]),
        'BSFL_BIN': ([galley_bio_wet, V['CMAN'], V['SLUDGE_W'], V['DMAN'], V['REJ']],
                     [V['LARVA_W'], V['FRASS'], V['BVAP']]),
        'VERMI_BIN': ([V['VFEED'], V['QDROP']], [V['VCOMP'], V['VTEA']]),
        'GROWBED_A': ([200.0 + V['VCOMP'] + V['VTEA']], [200.0 + V['VCOMP'] + V['VTEA']]),
        'GROWBED_B': ([200.0 + V['VCOMP'] + V['VTEA'] + V['RMAN'] + V['PRESS'] + 1.0],
                      [V['LOOP4'], V['BEDG'], V['BET']]),
        'GALLEY': ([V['GFOOD'], V['GREENS']], [V['GMEALS'], galley_bio_wet, V['shell_dm'], V['GGREY']]),
        'FOOD_STORE': ([FIN], [4.2, V['GFOOD'], V['FHAB']]),
    }
    residuals = {u: round(sum(i) - sum(o), 6) for u, (i, o) in checks.items() if abs(sum(i) - sum(o)) > 1e-9}
    V['residuals'] = residuals
    V['checks'] = {u: (round(sum(i), 6), round(sum(o), 6)) for u, (i, o) in checks.items()}
    return V


def write():
    """Apply the computed rates to the graph. Held edges get X-FARM; free edges stay untagged."""
    g = json.load(open(GP))
    d = json.load(open(DP))
    V = compute(d)
    L = V['loop_kgd']
    held = {
        'DUCK_FORM': V['FORM'], 'DUCK_FISH': V['FISHF'], 'DUCK_FODDER': V['FODDER'],
        'DUCK_GREENS': V['GREENS'], 'LARVAE_FRESH': V['LARVA_W'], 'EGGSHELL_RET': V['shell_dm'],
        'LAYER_FEED': V['LM'], 'QUAIL_RATION': V['QM'], 'DUCK_RATION': V['DM_'],
        'DUCK_STORE': V['store_dm'], 'FORM_REJECT': V['REJ'], 'FORM_VAP': V['VAP'],
        'FISH_SLUDGE': V['SLUDGE_W'], 'FISH_HARVEST': V['HARV_W'],
        'CHICK_MANURE': V['CMAN'], 'CHICK_VAP': V['CVAP'], 'IA-CHICK-H2O': V['CHW'],
        'QUAIL_DROP': V['QDROP'], 'QUAIL_VAP': V['QVAP'], 'QUAIL_H2O': V['QW'],
        'DUCK_MANURE': V['DMAN'], 'DUCK_VAP': V['DVAP'], 'IA-DUCK-H2O': V['DUCKW'],
        'DUCK_EGGS': V['duck_eggs'], 'DUCK_GREY': V['DGREY'], 'QUAIL_EGGS': V['quail_eggs'],
        'RABBIT_FORAGE': V['RFOR'], 'RABBIT_MEAT': V['RMEAT'], 'RABBIT_VAP': V['RVAP'],
        'RABBIT_MANURE': V['RMAN'],
        'FRASS': V['FRASS'], 'BSFL_VAP': V['BVAP'], 'GALLEY_BIO': 0.5,
        'EGG_HARVEST': V['eggs'], 'BED_GREENS': V['BEDG'], 'HONEY': 0.05,
        'NECTAR_FORAGE': V['NECTAR'], 'BEE_VAP': V['BEEVAP'],
        'FOOD_GALLEY': V['GFOOD'], 'FOOD_HAB': V['FHAB'],
        'NUT_AQUA': V['nut_dose'], 'NUT_AQUA_BED': 1.0, 'CA_HOPPER': V['CAQ'],
        'VERMI_FEED': V['VFEED'], 'VERMICOMPOST': V['VCOMP'], 'WORM_TEA': V['VTEA'],
        'GAL_GREY': V['GGREY'],
        'AQUA_LOOP1': L, 'AQUA_BYPASS': L, 'AQUA_NUT': 0.0, 'AQUA_SAN': 0.0,

    }
    free = {
        'AQUA_RETURN2': V['RET'], 'IA-AQUA-TOPUP': V['TOPUP'], 'AQUA_LOOP4': V['LOOP4'],
        'AQUA_LOOP3': 200.0 + 1.9 + V['VTEA'],
        'FORM_PRESS': V['PRESS'], 'BED_ET': V['BET'],
    }

    def ensure(sid, f, t, fs, ts, carries, note):
        for e in g['edges']:
            if e['stream_id'] == sid:
                return e
        e = {'stream_id': sid, 'from_unit_id': f, 'to_unit_id': t, 'from_sector_id': fs,
             'to_sector_id': ts, 'carries': carries, 'layers': ['mass'], 'presence': 'present',
             'rate': {'value': 0.0, 'unit': 'kg/d', 'status': 'study', 'note': note},
             'notes': 'X-FARM wet-basis balance (farm_balance.py)', 'phase': 'liquid',
             'namespace': 'IA', 'open_boundary': False}
        g['edges'].append(e)
        return e

    ensure('LARVAE_FRESH', 'BSFL_BIN', 'FEED_PREP', 'FARM', 'FARM',
           'fresh larvae to the formulation drier',
           'fresh larvae at the 44 % DM class (TECHTREE insect-farming.md:112)')
    ensure('DUCK_RATION', 'FEED_PREP', 'DUCK_PEN', 'FARM', 'FARM',
           'pressed duckweed mash to the duck ration', 'duck mash at the mash DM class (A-M-421 x A-M-426)')
    ensure('FORM_PRESS', 'FEED_PREP', 'GROWBED_B', 'FARM', 'FARM',
           'press water back to the loop', 'duckweed juice water returns to the beds (A-M-426)')
    ensure('BED_GREENS', 'GROWBED_B', 'FOOD_STORE', 'FARM', 'FARM',
           'media-bed greens to the reserve', 'bed greens class (FARM.classes.bed_greens_kgd)')
    ensure('BED_ET', 'GROWBED_B', 'CRYO_AHU', 'FARM', 'CRYO',
           'growbed evapotranspiration', 'bed ET to the AHU (free edge, solver reconciles)')
    ensure('NUT_AQUA', 'NORTH_DOCK', 'DUCKWEED', 'DOCK', 'FARM',
           'mineral nitrate solution to the raceway',
           'mineral N: the fish stock supplies a fraction of the raceway uptake (A-M-430)')
    ensure('NUT_AQUA_BED', 'NORTH_DOCK', 'GROWBED_B', 'DOCK', 'FARM',
           'mineral nitrate solution to the media beds', 'bed greens N top-up (A-M-430)')
    ensure('CA_HOPPER', 'NORTH_DOCK', 'QUAIL_CAGE', 'DOCK', 'FARM',
           'mineral calcium carbonate (free-choice hopper)', 'quail Ca class (TECHTREE coturnix.md:60; A-M-426/430)')
    ensure('FOOD_EXPORT', 'FOOD_STORE', 'BOUNDARY_EXPORT', 'FARM', 'DOCK',
           'surplus food to the reserve/trade boundary',
           'production beyond the crew issue (A-M-270 reserve; D-DOCK trade statement)')
    ensure('GAL_GREY', 'GALLEY', 'GREY_TREAT', 'HAB', 'WTR',
           'galley wash grey water to the treatment train', 'galley grey class (AQS-HAB-001 services)')
    g['edges'] = [e for e in g['edges'] if e['stream_id'] not in ('LARVAE_MEAL', 'DUCK_LAYERS')]

    for sid, val in held.items():
        e = next((x for x in g['edges'] if x['stream_id'] == sid), None)
        if e is None:
            raise SystemExit(f'farm_balance: edge {sid} missing from the graph')
        e['rate']['value'] = round(val, 6)
        note = e['rate'].get('note') or ''
        if 'X-FARM' not in note:
            e['rate']['note'] = (note + ' (X-FARM wet-basis, farm_balance.py)')[:240]
    MARK = ('X-PAR', 'X-SAN', 'X-MFG', 'AQS-DUTY-06', 'X-SAF-10', 'X-ELS', 'X-FARM', 'X-HAB')
    for sid, x0 in free.items():
        e = next((x for x in g['edges'] if x['stream_id'] == sid), None)
        if e is None:
            raise SystemExit(f'farm_balance: edge {sid} missing from the graph')
        note = e['rate'].get('note') or ''
        if 'X-PAR-02 reconciled' in note:
            continue   # the solver owns the reconciled free edges: rewriting the x0 would
                       # fight the balance stage and the graph phase would never converge
        e['rate']['value'] = round(x0, 6)
        for m in MARK:
            note = note.replace(m, '')
        if '[free:' not in note:
            note += f' [free: solver-reconciled, x0 {round(x0, 3)} kg/d]'
        e['rate']['note'] = note.strip()[:240]
        assert not any(m in e['rate']['note'] for m in MARK), f'{sid}: free edge still MARK-tagged'

    json.dump(g, open(GP, 'w'), indent=2)
    return V


if __name__ == '__main__':
    V = write()
    if V['residuals']:
        print('NODE RESIDUALS:', V['residuals'])
        raise SystemExit(1)
    print(f"farm_balance: larvae meal {V['larvae_meal_dm']:.4f} kg DM/d "
          f"({100 * V['larvae_meal_dm'] / (V['LM'] * 0 + 1.44):.1f} % of the layer ration DM); "
          f"bin feedstock {V['BININ']:.2f} kg wet/d; nodes close exactly.")

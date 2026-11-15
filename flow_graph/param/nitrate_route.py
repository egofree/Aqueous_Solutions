"""On-site ammonium-nitrate nutrient skid for the aquaponic raceway, recovery first (task X-QA-11, A-M-497).

The raceway mineral-nitrate dose rode the dock mineral manifest (NUT_AQUA, and NUT_AQUA_BED for the
media beds; A-M-430). The plant makes its own fixed nitrogen: WS_AMMONIA Haber-class ammonia from the
air-separation nitrogen (the graph's only new-N input), and the A-M-430 locale upgrade - neutralizing
the nitric-acid line - is landed here directly as the Ostwald route on the ammonia line itself:

  NUT_AN (ammonium-nitrate skid, FARM sector): half the ammonia draw is catalytically oxidized with
  plant oxygen (NH3 + 2 O2 -> HNO3 + H2O, the Ostwald class at autothermal load) and the acid is
  neutralized with the other half (HNO3 + NH3 -> NH4NO3). Net per mol of product:
  2 NH3 + 2 O2 -> NH4NO3 + H2O. The solution is diluted to the dosing strength driver
  FARM.classes.nutrient_N_wt and metered to the raceway on NUT_AQUA (re-pointed NORTH_DOCK -> NUT_AN).

The dose is sized to the measured crop uptake, not chosen: the duckweed and bed-green harvests times the
registered N classes (FARM.duckweed.dm_N_wt), less the fish-stock nitrogen the biofilter returns to the
loop (FARM.aquaponics.fish_N_return_g_d, A-M-430 basis). The media-bed uptake is smaller than the fish
return and the loop passes the beds before the raceway, so the fish-loop nitrate covers the beds and the
mineral dose is the whole gap on the raceway line; NUT_AQUA_BED retires.

Reactants are fed at the nut_an_selectivity driver (the unconverted slip vents to NOX_SCRUB, whose
nitrate liquor already feeds NUTRIENT_DOSE, so the slip nitrogen stays a booked nutrient), the dilution
water draws from ROOF_TANK (the GW intake closes the tank by difference), and the oxygen draw rides
CRYO_O2's direct draws (o2_close re-settles S83 by difference). WS_AMMONIA's nitrogen feed re-solves on
IA-NH3-SRC by difference in balance.physics R10c.

Called from flow_graph/param/farm_balance.py write() after the wet-basis doses are computed.
Run: python3 -m flow_graph.param.nitrate_route   (dry-solve at the registered drivers)
"""
import json
from . import drivers as DR

TAG = 'X-RTE TF: on-site ammonium-nitrate nutrient skid (X-QA-11, A-M-497)'
MN, MH, MO = 14.007, 1.008, 15.999
M_NH3, M_AN, M_O2, M_H2O = MN + 3 * MH, 2 * MN + 4 * MH + 3 * MO, 2 * MO, 2 * MH + MO


def design(gap_N_kg_d, d=None):
    """Stream rates (kg/d) and the skid load (kW) for one kg/d of mineral-N gap. Net chemistry per mol
    of product: 2 NH3 + 2 O2 -> NH4NO3 + H2O (NH3 + 2 O2 -> HNO3 + H2O, then HNO3 + NH3 -> NH4NO3)."""
    d = d or DR.load()
    sel = DR.val(d, 'nut_an_selectivity')
    n_wt = DR.val(d, 'FARM.classes.nutrient_N_wt')
    an = gap_N_kg_d * M_AN / (2 * MN)                 # product carries both nitrate and ammonium N
    dose = gap_N_kg_d / n_wt                          # dosing solution at the registered N strength
    nh3 = an * 2 * M_NH3 / M_AN / sel
    o2 = an * 2 * M_O2 / M_AN / sel
    rxn_h2o = an * M_H2O / M_AN                       # of reaction; stays in the solution
    vent = nh3 + o2 - an - rxn_h2o                    # unconverted slip to NOX_SCRUB (by difference)
    dil = dose - an - rxn_h2o                         # dilution water from ROOF_TANK
    assert min(an, dose, nh3, o2, rxn_h2o, dil) >= 0 and vent >= -1e-9, \
        f'nitrate_route: negative stream at gap {gap_N_kg_d} kg N/d: {dict(an=an, nh3=nh3, o2=o2, dil=dil, vent=vent)}'
    return dict(gap_N_kg_d=gap_N_kg_d, an_kg_d=an, dose_kg_d=dose, nh3_kg_d=nh3, o2_kg_d=o2,
                rxn_h2o_kg_d=rxn_h2o, dil_kg_d=dil, vent_kg_d=max(vent, 0.0),
                kw=DR.val(d, 'nut_an_kW'))


STREAMS = (('IA-NUT-NH3', 'WS_AMMONIA', 'NUT_AN', 'L', {'NH3': 0.28, 'water': 0.72},
            'nh3_kg_d', 'ammonia liquor to the nitrate skid (Ostwald feed and the neutralization base)'),
           ('IA-NUT-O2', 'CRYO_O2', 'NUT_AN', 'G', {'O2': 0.99, 'Ar': 0.01},
            'o2_kg_d', 'plant oxygen for the ammonia oxidation'),
           ('IA-NUT-H2O', 'ROOF_TANK', 'NUT_AN', 'L', {'water': 1.0},
            'dil_kg_d', 'dilution water to the dosing strength'),
           ('IA-NUT-VENT', 'NUT_AN', 'NOX_SCRUB', 'G', {'N2': 0.75, 'NOx': 0.05, 'H2O': 0.20},
            'vent_kg_d', 'unconverted slip to the NOx scrubber (its nitrate liquor feeds NUTRIENT_DOSE)'))


def tf(g, d, V):
    """Create-or-rate the NUT_AN node and streams; re-point NUT_AQUA on-site; retire NUT_AQUA_BED.
    V = the farm_balance value dict (nut_gap_N_kg_d, nut_dose)."""
    from flow_graph.param.o2_close import _edge, _node
    N = {n['unit_id']: n for n in g['nodes']}
    E = {e['stream_id']: e for e in g['edges']}
    # locale degradation (AQS-SITE-010, X-QA-11 house rule): the skid doses the raceway from the
    # ammonia line's nitrogen. A locale that eliminates the raceway or the ammonia line (leo eliminates
    # DUCKWEED with the animal chain and the loop) has neither the customer nor the fixed-N source, so
    # the skid does not land there; the raceway dose rides that locale's own nutrient arrangement.
    if not all((N.get(u) or {}).get('presence') == 'present' for u in ('DUCKWEED', 'WS_AMMONIA')):
        return None
    r = design(V['nut_gap_N_kg_d'], d)
    assert abs(r['dose_kg_d'] - V['nut_dose']) < 1e-9, (r['dose_kg_d'], V['nut_dose'])
    ins = r['nh3_kg_d'] + r['o2_kg_d'] + r['dil_kg_d']
    assert abs(ins - (r['dose_kg_d'] + r['vent_kg_d'])) < 1e-9, (ins, r['dose_kg_d'] + r['vent_kg_d'])
    if 'NUT_AN' not in N:
        n = _node('NUT_AN', N['DUCKWEED']['sector_id'], 'chemical_synthesis', 'load',
                  'Ammonium-nitrate nutrient skid (A-M-497).', {})
        n['notes'] = 'Ostwald oxidation of plant ammonia with plant oxygen, neutralized back with ammonia to ' \
                     'the dosing strength; sized to the raceway uptake less the fish-loop nitrogen (X-QA-11, ' \
                     'A-M-497; the A-M-430 in-plant route).'
        g['nodes'].append(n); N['NUT_AN'] = n
    for sid, a, b, ph, comp, key, carries in STREAMS:
        note = f"{TAG}: {key.replace('_kg_d', '')} = {r[key]:.6f} kg/d (nitrate_route.py)."
        if sid in E:
            assert (E[sid]['from_unit_id'], E[sid]['to_unit_id']) == (a, b), f'nitrate_route: {sid} names another stream'
        else:
            e = _edge(sid, a, b, ph, ['mass'], carries, r[key], 'kg/d',
                      N[a]['sector_id'], N[b]['sector_id'], comp, note)
            g['edges'].append(e); E[sid] = e
        e = E[sid]
        e.update(carries=carries, presence='present', composition=comp)
        e['rate'] = {'value': round(r[key], 6), 'unit': 'kg/d', 'status': 'study', 'note': note}
    N['NUT_AN']['params']['design'] = {k: round(v, 6) if isinstance(v, float) else v for k, v in r.items()}
    N['NUT_AN']['continuous_kw'] = {'value': round(r['kw'], 4), 'unit': 'kW', 'status': 'study',
                                    'note': f'{TAG}: oxidation starter, metering pumps and controls at the '
                                            f'{r["dose_kg_d"]:.3f} kg/d dose (nut_an_kW, A-M-497).'}
    if 'SF-NUT_AN' not in E:
        e = _edge('SF-NUT_AN', 'SOL_ARK_60K', 'NUT_AN', 'E', ['elec'], '480 V AC', r['kw'], 'kW',
                  N['SOL_ARK_60K']['sector_id'], N['NUT_AN']['sector_id'], None,
                  f'{TAG}: feed equal to NUT_AN continuous_kw.')
        e['header'] = 'tray'; g['edges'].append(e); E['SF-NUT_AN'] = e
    E['SF-NUT_AN']['rate'] = {'value': round(r['kw'], 4), 'unit': 'kW', 'status': 'study',
                              'note': f'{TAG}: feed equal to NUT_AN continuous_kw.'}
    e = E['NUT_AQUA']
    e.update(from_unit_id='NUT_AN', from_sector_id=N['NUT_AN']['sector_id'],
             carries='ammonium-nitrate nutrient solution to the raceway (on-site skid, X-QA-11)',
             composition={'NH4NO3': round(r['an_kg_d'] / r['dose_kg_d'], 6), 'water': round(1 - r['an_kg_d'] / r['dose_kg_d'], 6)})
    for k in ('dock_class', 'dock_pending_task'):
        (e.setdefault('params', {})).pop(k, None)   # no longer a dock input: the re-point retires the class with the edge
    e['rate'] = {'value': round(r['dose_kg_d'], 6), 'unit': 'kg/d', 'status': 'study',
                 'note': f'{TAG}: raceway mineral-N dose at the {DR.val(d, "FARM.classes.nutrient_N_wt"):.1%} N '
                         f'strength; gap {r["gap_N_kg_d"] * 1000:.1f} g N/d = the crop uptake less the fish-loop '
                         f'return (A-M-430/497).'}
    bed = E.get('NUT_AQUA_BED')
    if bed is not None:
        bed['presence'] = 'retired'
        for k in ('dock_class', 'dock_pending_task'):
            (bed.setdefault('params', {})).pop(k, None)
        bed['rate'] = {'value': 0.0, 'unit': 'kg/d', 'status': 'study',
                       'note': 'Retired by the on-site nutrient skid (X-QA-11, A-M-497): the media-bed uptake is '
                               'smaller than the fish-stock nitrogen the biofilter returns to the loop, and the '
                               'loop passes the beds before the raceway, so the loop nitrate covers the beds and '
                               'the skid doses the whole mineral gap on NUT_AQUA. Was the dock mineral-manifest '
                               'bed dose (A-M-430).'}
    return r


if __name__ == '__main__':
    from flow_graph.param import farm_balance
    d = DR.load()
    V = farm_balance.compute(DR.raw())
    print(json.dumps(design(V['nut_gap_N_kg_d'], d), indent=1))

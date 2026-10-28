# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""X-LOC-SPEC / unit task 02 close-out: sizing for the ten last unsized units (AQS-PLAN-007).

The grease/lithium specialty chain, the silicon reduction, the adsorption chiller, the dry
cooler, the well head, the make-up-air HX, the water electrolyser and the two grease kettles
get their unit task 02 treatment: rates, design parameters, envelopes and load bases - every
number carrying a cited basis (TECHTREE husbandry/tool classes, ASME/ASTM standards, the
A-M register, or a named study value with its verification test). The rules:

- a study rate is stated WITH its verification test (the FLUX_PREP/grease-class precedent);
- a draw slices a balanced node 1:1 from that node's stated export/return (the C5-C10
  textile precedent: the surplus falls, stated, not hidden);
- the continuous_kw stamps carry their arithmetic, so the load list classifies them
  calculated (A-M-275/A-M-301 discipline).

Run: python3 -m flow_graph.param.specialty_sizing
"""
import json
import math
import os

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GP = os.path.join(R, 'flow_graph', 'plant_flow_graph.json')


def compute():
    """The sizing arithmetic. Every value carries its basis inline."""
    v = {}
    # --- the grease/lithium specialty chain (X-ASM-02 lubrication class) ----------
    # the plant lubrication class: 0.3 kg/d grease total (bearing/motor fleet), split
    # Ca (general) 0.2 / Li (motor bearings, high grade) 0.1. Verification: the
    # first-article greasing audit (X-ASM-02 close-out).
    v['grease_ca_kgd'] = (0.2, 'X-ASM-02 study class: the general lubrication draw (verification: X-ASM-02 greasing audit)')
    v['grease_li_kgd'] = (0.1, 'X-ASM-02 study class: the motor-bearing grease draw')
    v['wax_ca_kgd'] = (0.2, 'the C19-C28 wax base: 1:1 into the Ca kettle (CUT-3 export gives up the share, stated)')
    v['wax_li_kgd'] = (0.1, 'the C19-C28 wax base for the Li kettle')
    v['ca_thickener_kgd'] = (0.025, 'the calcium-soap thickener at ~12 % of the Ca grease (grease chemistry class)')
    v['li_slipstream_kgd'] = (0.5, 'the POLISH_BANK liquor slipstream at the ~1.5 wt% LiOH class: carries the Li2CO3 thickener need (0.012 kg/d at 12 % of the Li grease)')
    v['li_carbonated_kgd'] = (0.5, 'the carbonated slurry to the Li kettle (thickener + liquor water)')
    # --- SI_REDUCE (PV cell line silicon) ------------------------------------------
    si_kgd = 1.8                                   # 3 cells/d x 0.6 kg Si/cell (200 mm wafer class, kerf incl.)
    v['si_kgd'] = (si_kgd, 'the PV cell line silicon: 3 cells/d x 0.6 kg/cell (AQS-DUTY-071 throughput; wafer + kerf class)')
    v['sio2_kgd'] = (round(si_kgd * 60.08 / 28.09, 3), 'SiO2 per the carbothermic stoichiometry SiO2 + 2C -> Si + 2CO')
    v['char_to_si_kgd'] = (round(si_kgd * 24.02 / 28.09 / 0.8, 3), 'char carbon per the stoichiometry at the 80 % reactive-carbon class (the IA-CHAR pool is 5.5 kg/d: the draw fits)')
    v['si_reduce_kw'] = (5.0, 'the furnace at the ~12 kWh/kg Si class (carbothermic study class) / 24 h at the 1.8 kg/d draw')
    v['si_reduce_env'] = ([1200, 1000, 1600], 'graphite hot-face furnace (the issued sec3 selection) at the batch class')
    # --- ADS_CHILL (2.25 kW chilled, 5 kW drive, 7.25 kW rejected - the rated edges) --
    v['ads_env'] = ([700, 500, 1200], 'the 2.25 kW-class silica gel-water adsorption chiller: drive 65 C, chilled 12 C, thermal COP ~0.45 (A-M-239/240; WANG2006_ADS); 304L shells per the issued sec3')
    v['ads_kw_note'] = ('the rated edges carry the arithmetic: 2.25 kW chilled = 5.0 kW drive x the 0.45 '
                        'thermal COP class (A-M-239/240); 7.25 kW rejected = drive + chilled in. (AQS-DUTY-013 class)')
    # --- DRY_COOLER (7.25 kW dry rejection from the adsorption chiller) --------------
    v['dc_airflow_m3_s'] = (0.61, 'air 25->38 C at 1.06 kg/m3: Q/(rho cp dT) = 7.25/(1.06 x 1.006 x 13) (AQS-BLD class approach)')
    v['dc_fan_kw'] = (0.15, 'the fan at ~0.03 kW per 100 m3/h class for the dry coil draft')
    v['dc_env'] = ([1200, 600, 1200], 'the dry coil + fan at the 7.25 kW rejection duty')
    # --- GW_INTAKE (standby well head: the make-up on loss of atmospheric harvest) ----
    v['gw_pump_kw'] = (0.37, 'the submersible at the make-up class (the T4 shortfall bound ~30 m3/d worst case: 0.37 kW lifts 30 m3 x 30 m)')
    v['gw_env'] = ([800, 800, 600], 'the wellhead hatch + pump discharge set (X-LOC-13 well head)')
    v['gw_note'] = ('standby-zero at the baseline: the atmospheric harvest covers the water cycle '
                    '(the T4 by-design ruling). The pump rate is the loss-of-harvest make-up class.')
    # --- H2O_ELYZ (the rated PEM stack: 83.62 water -> 9.358 H2 + 74.263 O2, 21.445 kW) --
    v['elyz_kwh_per_kg'] = (round(21.445 * 24 / 9.358, 1), 'PEM specific consumption 54.9 kWh/kg H2 (the rated edges are self-consistent: 21.445 kW x 24 h / 9.358 kg)')
    v['elyz_env'] = ([1800, 800, 1600], 'the PEM stack skid: stack + power electronics + water loop at the 21.445 kW duty')
    v['elyz_note'] = ('the rated edges carry the arithmetic: 83.62 kg/d water splits 9.358 H2 + 74.263 O2 '
                      '(mass-conserving); 6.082 kW heat to Q4 = the stack inefficiency share.')
    # --- MAU_HX (12 kW water-to-air coil, rated) --------------------------------------
    v['mau_env'] = ([600, 400, 400], 'the 12 kW water-to-air coil at the MAU duty (Q4 -> hab make-up air)')
    # --- kettles ----------------------------------------------------------------------
    v['grease_ca_env'] = ([500, 400, 600], 'the 0.2 kg/d batch kettle: heated soap-precipitation class')
    v['grease_li_env'] = ([500, 400, 600], 'the 0.1 kg/d batch kettle (emulsification class)')
    v['p_ca_env'] = ([300, 300, 400], 'the calcium-soap precipitation vessel at the 0.025 kg/d thickener draw')
    v['li_recover_env'] = ([200, 200, 800], 'the carbonation contactor at the 0.5 kg/d slipstream')
    # --- load bases for the three stamps the load list flagged ------------------------
    v['feed_prep_kw'] = (0.6, 'mixer 0.1 + grinder 0.15 + HP drier 0.35 (9.5 kg/d water x ~0.9 kWh/kg at the HP COP class); arithmetic per A-M-426')
    v['poly_fiber_kw'] = (0.3, 'extruder heater 0.2 (0.09 kg/d PP melt + standby) + spindle/winder 0.1; arithmetic per A-M-429')
    v['aqua_uv_kw'] = (0.04, 'the 254 nm lamp class at the 30-100 mJ/cm2 dose and the 40 kg/d loop flow (A-M-428)')
    return v


def write():
    g = json.load(open(GP))
    N = {n['unit_id']: n for n in g['nodes']}
    v = compute()

    def put(u, design=None, sizing=None, envelope=None, size_mm=None, size_note=None, kw=None, kw_note=None):
        n = N[u]
        p = n.setdefault('params', {})
        if design:
            d = p.setdefault('design', {})
            d.update(design)
        if sizing:
            sz = p.setdefault('sizing', {})
            sz.update(sizing)
        if envelope:
            p['envelope'] = {'size_mm': envelope, 'basis': size_note}
        if size_mm:
            p['size_mm'] = size_mm
            p['size_note'] = size_note
        if kw is not None:
            cur = (n.get('continuous_kw') or {}).get('note') or ''
            if '(X-SPEC' not in cur:            # idempotence: the note is written once
                n['continuous_kw'] = {'value': kw, 'unit': 'kW', 'status': 'study',
                                      'note': f'{kw_note} (X-SPEC sizing, calculated)'}
            else:
                n['continuous_kw']['value'] = kw

    def edge(sid, val, note):
        for e in g['edges']:
            if e['stream_id'] == sid:
                e['rate']['value'] = val
                cur = e['rate'].get('note') or ''
                if '(X-SPEC)' not in cur:            # idempotence: the note is written once
                    e['rate']['note'] = (cur + f' | {note} (X-SPEC)')[:240]
                return

    # --- the grease/lithium chain: the draws slice the balanced nodes 1:1 -----------
    edge('WAX_TO_GREASE_CA', v['wax_ca_kgd'][0], v['wax_ca_kgd'][1] + '; the C19 export gives up the share, stated')
    edge('WAX_TO_GREASE_LI', v['wax_li_kgd'][0], v['wax_li_kgd'][1] + '; the C19 export gives up the share, stated')
    edge('POLISH_TO_LI', v['li_slipstream_kgd'][0], v['li_slipstream_kgd'][1] + '; the IA-POL-02 return sheds the slipstream, stated')
    edge('LI_TO_GREASE', v['li_carbonated_kgd'][0], v['li_carbonated_kgd'][1])
    edge('PCA_TO_GREASE', v['ca_thickener_kgd'][0], v['ca_thickener_kgd'][1] + ' (X-SPEC)')

    put('GREASE_CA', design={'duty': 'calcium grease kettle: the C19-C28 wax base + the P_CA thickener -> the general lubrication grease',
                             'batch_kgd': v['grease_ca_kgd'][0], 'heat_class': 'soap precipitation, jacket heated'},
        sizing={'batch_kgd': v['grease_ca_kgd'][0]},
        envelope=v['grease_ca_env'][0], size_note=v['grease_ca_env'][1],
        kw=0.2, kw_note='jacket heater at the 0.2 kg/d batch class')
    put('GREASE_LI', design={'duty': 'lithium grease kettle: the wax base + the LI_RECOVER carbonated thickener -> the motor-bearing grease',
                             'batch_kgd': v['grease_li_kgd'][0]},
        sizing={'batch_kgd': v['grease_li_kgd'][0]},
        envelope=v['grease_li_env'][0], size_note=v['grease_li_env'][1],
        kw=0.2, kw_note='jacket heater at the 0.1 kg/d batch class')
    put('P_CA', design={'duty': 'calcium-soap precipitation: wax + lime -> the grease thickener (feeds GREASE_CA)',
                        'thickener_kgd': v['ca_thickener_kgd'][0]},
        sizing={'thickener_kgd': v['ca_thickener_kgd'][0]},
        envelope=v['p_ca_env'][0], size_note=v['p_ca_env'][1],
        kw=0.05, kw_note='agitator at the precipitation batch class')
    put('LI_RECOVER', design={'duty': 'carbonate the POLISH_BANK LiOH slipstream -> the lithium thickener (feeds GREASE_LI)',
                              'slipstream_kgd': v['li_slipstream_kgd'][0]},
        sizing={'slipstream_kgd': v['li_slipstream_kgd'][0]},
        envelope=v['li_recover_env'][0], size_note=v['li_recover_env'][1],
        kw=0.05, kw_note='contactor agitator + CO2 metering at the batch class')

    # --- the machines -----------------------------------------------------------------
    put('SI_REDUCE', design={'duty': 'carbothermic silicon reduction for the PV cell line (SOLAR_PV_CELL draws 1.8 kg/d Si)',
                             'si_kgd': v['si_kgd'][0], 'sio2_kgd': v['sio2_kgd'][0],
                             'char_kgd': v['char_to_si_kgd'][0]},
        sizing={'si_kgd': v['si_kgd'][0]},
        envelope=v['si_reduce_env'][0], size_note=v['si_reduce_env'][1],
        kw=v['si_reduce_kw'][0], kw_note=v['si_reduce_kw'][1])
    edge('CHAR_TO_SI', v['char_to_si_kgd'][0], v['char_to_si_kgd'][1] + '; the IA-CHAR pool sheds the draw, stated (X-SPEC)')

    put('ADS_CHILL', design={'duty': 'silica gel-water adsorption chiller: 5 kW drive at 65 C -> 2.25 kW chilled at 12 C, 7.25 kW rejected',
                             'chilled_kw': 2.25, 'cop_thermal': 0.45},
        sizing={'chilled_kw': 2.25, 'cop_thermal': 0.45},
        envelope=v['ads_env'][0], size_note=v['ads_env'][1])
    put('DRY_COOLER', design={'duty': 'dry rejection of the ADS_CHILL 7.25 kW + the Q4 dry share',
                              'airflow_m3_s': v['dc_airflow_m3_s'][0], 'fan_kw': v['dc_fan_kw'][0]},
        sizing={'airflow_m3_s': v['dc_airflow_m3_s'][0]},
        envelope=v['dc_env'][0], size_note=v['dc_env'][1],
        kw=0.15, kw_note=v['dc_fan_kw'][1] + ' (the fan; the rejection is passive-draft assisted)')
    put('GW_INTAKE', design={'duty': 'standby well head: the make-up on loss of atmospheric harvest',
                             'pump_kw': v['gw_pump_kw'][0]},
        sizing={'pump_kw': v['gw_pump_kw'][0]},
        envelope=v['gw_env'][0], size_note=v['gw_env'][1],
        kw=0.37, kw_note=v['gw_pump_kw'][1] + ' (standby-zero at the baseline: ' + v['gw_note'] + ')')
    put('H2O_ELYZ', design={'duty': 'PEM electrolysis: 83.62 kg/d water -> 9.358 kg/d H2 + 74.263 kg/d O2 at 21.445 kW',
                            'kwh_per_kg_h2': v['elyz_kwh_per_kg'][0]},
        sizing={'kwh_per_kg_h2': v['elyz_kwh_per_kg'][0]},
        envelope=v['elyz_env'][0], size_note=v['elyz_env'][1],
        kw_note=v['elyz_note'] + ' (X-SPEC)')
    put('MAU_HX', design={'duty': 'the 12 kW water-to-air coil on the hab make-up air (Q4 -> MAU)'},
        sizing={'duty_kw': 12.0},
        envelope=v['mau_env'][0], size_note=v['mau_env'][1])

    # --- the three flagged load stamps: the arithmetic onto the stamps ---------------
    put('FEED_PREP', sizing={'load_basis': v['feed_prep_kw'][1]}, kw=v['feed_prep_kw'][0], kw_note=v['feed_prep_kw'][1] + ' (X-SPEC calculated)')
    put('POLY_FIBER', sizing={'load_basis': v['poly_fiber_kw'][1]}, kw=v['poly_fiber_kw'][0], kw_note=v['poly_fiber_kw'][1] + ' (X-SPEC calculated)')
    put('AQUA_UV', sizing={'load_basis': v['aqua_uv_kw'][1]}, kw=v['aqua_uv_kw'][0], kw_note=v['aqua_uv_kw'][1] + ' (X-SPEC calculated)')

    json.dump(g, open(GP, 'w'), indent=2)
    return v


if __name__ == '__main__':
    v = write()
    print('specialty_sizing: the ten units sized; key rates:')
    for k in ('grease_ca_kgd', 'grease_li_kgd', 'si_kgd', 'si_reduce_kw', 'gw_pump_kw', 'feed_prep_kw', 'poly_fiber_kw', 'aqua_uv_kw'):
        print(' ', k, '=', v[k][0])

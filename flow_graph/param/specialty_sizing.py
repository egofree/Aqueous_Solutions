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
    v['si_reduce_kw'] = (round(si_kgd * 12.0 / 24.0, 2), f'the furnace at the ~12 kWh/kg Si class (carbothermic study class) / 24 h at the {si_kgd} kg/d draw: {si_kgd} x 12 / 24 = {round(si_kgd * 12.0 / 24.0, 2)} kW')
    v['si_reduce_env'] = ([1200, 1000, 1600], 'graphite hot-face furnace (the issued sec3 selection) at the batch class')
    # --- ADS_CHILL (2.25 kW chilled, 5 kW drive, 7.25 kW rejected - the rated edges) --
    v['ads_env'] = ([700, 500, 1200], 'the 2.25 kW-class silica gel-water adsorption chiller: drive 65 C, chilled 12 C, thermal COP ~0.45 (A-M-239/240; WANG2006_ADS); 304L shells per the issued sec3')
    v['ads_kw_note'] = ('the rated edges carry the arithmetic: 2.25 kW chilled = 5.0 kW drive x the 0.45 '
                        'thermal COP class (A-M-239/240); 7.25 kW rejected = drive + chilled in. (AQS-DUTY-013 class)')
    # --- DRY_COOLER (dry rejection terminal: ADS_CHILL 7.25 kW + the Q4 dry share + the ZNBR2 cycling heat) --
    # The rejection duty and the rating are calculated by write_graph heat (X-THM-01 F-4, A-M-244 restated /
    # A-M-455) from the terminal book; the fan electrical stamp below reads that rating (write() re-derives
    # from the graph params this pass, write_graph heat runs earlier in the regen stage order).
    v['dc_env'] = ([1200, 600, 1200], 'the dry coil + fan at the calculated rejection duty (study envelope box; design sizing per the duty sheet follows)')
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
    import math
    g = json.load(open(GP))
    N = {n['unit_id']: n for n in g['nodes']}
    E = {e['stream_id']: e for e in g['edges']}
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
    # --- DRY_COOLER: the fan electrical stamp and airside read the calculated rating written by
    # write_graph heat (X-THM-01 F-4, A-M-244 restated / A-M-455): airside at the same 13 K rise
    # class as the issued 0.61 m3/s per 7.25 kW basis, fan at the 0.05 kW_fan/kW_th class.
    _dc_rated = float(((N.get('DRY_COOLER', {}).get('params') or {}).get('rated_kW')) or 12.0)
    _dc_duty = _dc_rated / 1.25
    v['dc_airflow_m3_s'] = (round(0.61 * _dc_duty / 7.25, 2), f'air 25->38 C at 1.06 kg/m3: Q/(rho cp dT) at the rated duty {_dc_duty:.1f} kW, 0.61 m3/s per 7.25 kW class (AQS-BLD class approach)')
    v['dc_fan_kw'] = (round(0.05 * _dc_rated, 2), f'the fan at the 0.05 kW_fan/kW_th class on the rated duty {_dc_rated:.0f} kW (A-M-244 restated)')
    put('DRY_COOLER', design={'duty': 'dry rejection of the ADS_CHILL 7.25 kW + the Q4 dry share + the ZNBR2 cycling heat',
                              'airflow_m3_s': v['dc_airflow_m3_s'][0], 'fan_kw': v['dc_fan_kw'][0]},
        sizing={'airflow_m3_s': v['dc_airflow_m3_s'][0]},
        envelope=v['dc_env'][0], size_note=v['dc_env'][1])
    # the fan electrical stamp tracks the calculated rating every pass (the put() note-freeze is for
    # hand-authored texts; this note is generator-owned)
    N['DRY_COOLER']['continuous_kw'] = {'value': v['dc_fan_kw'][0], 'unit': 'kW', 'status': 'study',
        'note': f'{v["dc_fan_kw"][1]}; fan-assisted at the window bounding case (X-SPEC sizing, calculated)'}
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
    # --- BAGHOUSE (the dry-dust filter machine: housing, tubesheet, bag field, hopper,
    # pulse header and rotary-valve discharge, sized on the capture air per A-M-458) ---
    _bh_dust = {k: float((E.get(k, {}).get('rate') or {}).get('value') or 0.0)
                for k in ('IA-MILL-LOSS', 'IA-FAB-LOSS', 'IA-WIRE-LOSS')}
    _bh_hoods = {'IA-MILL-LOSS': 0.20, 'IA-FAB-LOSS': 0.12, 'IA-WIRE-LOSS': 0.10}   # m2 hood faces (A-M-458)
    _bh_u = 0.5                                                     # m/s hood face velocity (ACGIH class)
    _bh_q_m3_h = round(_bh_u * sum(_bh_hoods.values()) * 3600.0, 0)  # 756 m3/h capture air
    _bh_ac_basis = 1.2                                              # m3/min/m2 (EPA-453 practice)
    _bh_cloth_req = round(_bh_q_m3_h / 60.0 / _bh_ac_basis, 2)      # 10.5 m2
    _bh_bags = 20                                                   # D150 x 1200, 5 x 4 field at the 180 mm pitch
    _bh_bag_area = round(math.pi * 0.150 * 1.200, 4)                # 0.5655 m2 per bag
    _bh_cloth = round(_bh_bags * _bh_bag_area, 2)                   # 11.31 m2 drawn
    _bh_hop_h = int((900 - 200) / 2 * 1.732)                        # 60 deg hopper, 200 mm valve outlet
    _bh_h = 50 + _bh_hop_h + 20 + 1200 + 20 + 360 + 20         # plinth, hopper, hopper clear, bags, tubesheet, plenum, roof
    put('BAGHOUSE', design={'machine': 'pulse-jet dust baghouse: CS housing, tubesheet, 20-bag '
                            'antistatic-polyester field, 60 deg dust hopper with rotary valve to '
                            'IA-BAG-01, pulse-clean header and solenoid/diaphragm envelopes',
                            'dust_kg_d': {k: round(v, 3) for k, v in _bh_dust.items()},
                            'hoods_m2': _bh_hoods, 'hood_face_velocity_m_s': _bh_u,
                            'capture_air_m3_h': _bh_q_m3_h, 'ac_basis_m3_min_m2': _bh_ac_basis,
                            'cloth_req_m2': _bh_cloth_req, 'bags': _bh_bags,
                            'bag_mm': [150, 1200], 'bag_pitch_mm': 180,
                            'cloth_drawn_m2': _bh_cloth,
                            'ac_drawn_m3_min_m2': round(_bh_q_m3_h / 60.0 / _bh_cloth, 3),
                            'ducts': 'hood ducts DN100 (mill, 360 m3/h) and DN80 x 2 (fab 216, '
                                     'wire 180 m3/h) at the 18-20 m/s duct class; the schedule '
                                     'DN15 rows stay the duty connection table (WORK_ORDER W12)',
                            'housing_inner_mm': [900, 700], 'wall_mm': 3.0,
                            'hopper_h_mm': _bh_hop_h, 'valve_outlet_mm': 200,
                            'z_chain': {'plinth': 50, 'hopper_top': 50 + _bh_hop_h,
                                        'bags': [50 + _bh_hop_h + 20, 50 + _bh_hop_h + 20 + 1200],
                                        'tubesheet': 50 + _bh_hop_h + 20 + 1200,
                                        'plenum': [50 + _bh_hop_h + 20 + 1200 + 20,
                                                   50 + _bh_hop_h + 20 + 1200 + 20 + 360]},
                            'material': 'carbon steel housing, painted, bonded and grounded; '
                            'antistatic polyester bags (duty section 3); deflagration vent per '
                            'the combustible-dust class',
                            'basis': 'capture air = hood face velocity x hood faces (A-M-458, '
                                     'ACGIH class); cloth = air / 1.2 m3/min/m2 (EPA-453 '
                                     'practice); drawn field carries it at +8 %',
                            'computed_by': 'flow_graph/param/specialty_sizing.py (X-SPEC lane, CAD-representation audit item 5)'},
        sizing={'capture_air_m3_h': _bh_q_m3_h, 'cloth_m2': _bh_cloth},
        size_mm=[1250, 1000, _bh_h], size_note='L x W x H mm, set by flow_graph/param/specialty_sizing.py '
              '(X-SPEC): housing, inlet plenum, bag field and 60 deg hopper; the placement seed block '
              '(1500 x 1000 x 1500) under-books the height by 0.78 m - the named consequence '
              '(BAGHOUSE WORK_ORDER W12)')
    put('MAU_HX', design={'duty': 'the 12 kW water-to-air coil on the hab make-up air (Q4 -> MAU)'},
        sizing={'duty_kw': 12.0},
        envelope=v['mau_env'][0], size_note=v['mau_env'][1])

    # --- the three flagged load stamps: the arithmetic onto the stamps ---------------
    put('FEED_PREP', sizing={'load_basis': v['feed_prep_kw'][1]}, kw=v['feed_prep_kw'][0], kw_note=v['feed_prep_kw'][1] + ' (X-SPEC calculated)')
    put('POLY_FIBER', sizing={'load_basis': v['poly_fiber_kw'][1]}, kw=v['poly_fiber_kw'][0], kw_note=v['poly_fiber_kw'][1] + ' (X-SPEC calculated)')
    put('AQUA_UV', sizing={'load_basis': v['aqua_uv_kw'][1]}, kw=v['aqua_uv_kw'][0], kw_note=v['aqua_uv_kw'][1] + ' (X-SPEC calculated)')
    put('EXT_HALL', size_mm=[186000, 174000, 6000],
        size_note='building massing envelope (bounding box of the issued L-shape): EXT_HALL_E 162 x 174 m east '
                  'extension + EXT_HALL_N 24 x 156 m north extension, 6 m eave, portal frames on the 6 m grid '
                  '(31 x 29 bays, X-PAR-07, A-M-104; placement_seed blocks EXT_HALL_E/N are the authority). '
                  'Conditioned footprint per params.footprint_m2; the fitout programme stays the duty-sheet open item.')
    for uid, sz in (
        ('SI_REDUCE', [1200, 1000, 1600]),
    ):
        put(uid, size_mm=sz, size_note='envelope from the placement seed (AQS-PLACE-SEED-001); sized by need')
    # 2026-10-31 recovery: these units' study envelopes lived only in the cad/stl registry after a
    # regen dropped params.size_mm; bounds read back from the STLs (trimesh), recorded verbatim.
    for uid, sz in (
        ('AFTERBURNER', [1000, 600, 800]),
        ('AFTERBURNER_FLUE', [1000, 600, 800]),
        ('BMED_UPW_POLISH', [1000, 600, 800]),
        ('COLD_MILL', [1000, 600, 800]),
        ('CRU', [1000, 600, 800]),
        ('CRYO_AHU_COND_CONDENSABLE', [1000, 600, 800]),
        ('GAS_ATOMIZER', [1000, 600, 800]),
        ('GEO_GHEX', [1000, 600, 800]),
        ('GEO_HP_CLOSED_LOOP', [1000, 600, 800]),
        ('GROW_BED', [2000, 1000, 400]),
        ('HYDRO_SET', [1000, 600, 800]),
        ('MET_MELT', [1000, 600, 800]),
        ('MFG_SHOP', [1000, 600, 800]),
        ('OIL_DRYER', [1000, 600, 800]),
        ('PV_ARRAY', [1000, 600, 800]),
        ('WAFER_FAB', [1000, 600, 800]),
        ('WET_BENCH', [1000, 600, 800]),
        ('WIRE_DRAW', [1000, 600, 800]),
):
        put(uid, size_mm=sz, size_note='study default envelope box, read back from the cad/stl registry '
            '(M0 study envelope; design sizing per the duty sheet follows)')

    put('BLACK_DIGEST',
        design={'D_mm': 800, 'H_mm': 760, 'wall_mm': 5.0, 'V_L': 378, 'material': 'PP-H sheet, extrusion-welded (DVS 2207-11)',
                'insulation': 'PIR 50 mm, PE cladding', 'heat_W': 85, 'T_C': 55, 'SRT_d': 15, 'biogas_g_d': 99},
        size_mm=[1100, 1100, 1260],
        size_note='DN800 x 760 mm thermophilic anaerobic digester + 300 mm envelope margin, per AQS-DUTY-063 '
                  '(sizing/SANITATION.md section 2 row 1: 378 L, PP-H 5.0 mm, 50 mm PIR, 85 W, 55 C SRT 15 d METCALF5); '
                  'graph-side design restored from the governing sizing doc because the X-SAN-01 writer is R11-blocked (owner lane)')
    put('MET_SYN', size_mm=[1500, 1000, 1800],
        size_note=('bench fume-hood train: glass-lined reactor column (2 L working volume), '
                   'reagent feed tanks, Hastelloy C crystalliser; the 9 g/d DL-Met duty sets '
                   'nothing larger (A-M-416 route A; X-UI-002)'))

    json.dump(g, open(GP, 'w'), indent=2)
    return v


if __name__ == '__main__':
    v = write()
    print('specialty_sizing: the ten units sized; key rates:')
    for k in ('grease_ca_kgd', 'grease_li_kgd', 'si_kgd', 'si_reduce_kw', 'gw_pump_kw', 'feed_prep_kw', 'poly_fiber_kw', 'aqua_uv_kw'):
        print(' ', k, '=', v[k][0])

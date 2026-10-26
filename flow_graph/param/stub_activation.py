"""Stub-activation stage (X-PAR-02 / AQS-EQP-STUDY-001 rev G disposition): retires LITHO_STUB into the real
litho tools, converts the five study_stub-class units to real classes with real designs, and wires
SOLAR_PV_CELL to the existing X-MFG-38 cell-line sizing (A-M-287..296).

  LITHO_COAT  spin-coater line: spin bowl + vacuum chuck + softbake hotplate (AQS-LITH-001 rev C frame)
  LITHO_ALIGN contact aligner: 365 nm LED array, leadscrew stage (AQS-LITH-001 rev C)
  LITHO_DEV   wet develop bench on the WET_BENCH chemistry class (TMAH/KOH developer fork)
  LITHO_STUB  retired: its flows move to the real tools (presence retired, note kept)
  SOLAR_PV_CELL  class study_stub -> tool; params.design already written by pv_cell_line.py (X-MFG-38)
  REMIN       class dose: remineralization dosing skid (Ca/Mg metering + UV) from the water-train chemistry
  VCD_TRAIN   class evaporator: MVC still stack from the 17 kWh/m3 driver basis
  BLOW_MOLD   class former: continuous-extrusion blow molder at the IA-BLOW-IN wax duty
  ELECTRODE_COAT class coater: coating booth + IR cure at the IA-COAT-IN recoat duty
  GEO_ORC     class orc: real ORC geometry as INSTALLED STANDBY at the 12 kW_th dry-cooler context;
              continuous_kw stays null per the owner ruling D-GEO_ORC (study closed, endpoint 0 kW_e)
  X-LOC-09 locale-replacement units (placeholders; placed, not installed at the Earth reference):
  RAD_PANEL   class radiator: space radiator at the DRY_COOLER duty context, for sites with no air
              heat sink (Mars; also the LEO rejection mode); rated_kW carried at 12 kW (A-M-244 context)
  TANK_BLD    class press_tank: closed bladder tank inside the pressurised shell, for sites where
              ambient pressure sits at the triple point of water (replaces CATCH_TANK / ROOF_TANK)
  REC_HDR     class recovery_header: closed vent and relief recovery header, for sites with no
              vent sink (replaces the relief valves, vent scrubbers and flue junction)
  CAT_OX      class catalytic: catalytic waste-gas oxidiser on plant oxygen, for sites with no
              atmospheric oxidant (replaces the air-fired AFTERBURNER)
  E_HEAT      class resistance_heater: electric resistance trim heat, for sites with no atmospheric
              oxidant (replaces the fuel-fired COMB_HEAT N+1 at the A-M-283 30 kW connected duty)

Run: python3 -m flow_graph.param.stub_activation [--write]
"""
import json, math, os, sys
from . import drivers as DR

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GP = os.path.join(ROOT, 'flow_graph/plant_flow_graph.json')
TAG = 'X-PAR-02 stub activation (AQS-EQP-STUDY-001 rev G; A-M-287..296)'
LT = 'FAB.litho-train.'


def kwr(v, note):
    return {'value': round(v, 4), 'unit': 'kW', 'status': 'study', 'note': note}


def node(g, N, uid, sector, cls, notes, presence='present', role='load'):
    if uid not in N:
        n = {'unit_id': uid, 'sector_id': sector, 'presence': presence, 'class': cls, 'tags': [],
             'electrical_role': role, 'diagram_gap': None, 'enabled': True, 'modules': [], 'params': {}}
        g['nodes'].append(n); N[uid] = n
    N[uid].update({'class': cls, 'notes': notes, 'presence': presence})
    return N[uid]


def feed(g, E, uid, kw, note, model=None):
    sid = f'SF-{uid}'
    if sid not in E:
        src = json.loads(json.dumps(E['SF-LITHO_STUB'])) if 'SF-LITHO_STUB' in E else json.loads(json.dumps(E['SF-HF_GEN']))
        src.update(stream_id=sid, to_unit_id=uid, presence='present', notes=f'{uid} feed (stub activation)')
        g['edges'].append(src); E[sid] = src
    E[sid]['rate'] = {'value': round(kw, 4), 'unit': 'kW', 'status': 'study', 'note': note}


def apply(g=None, write=False):
    if g is None:
        g = json.load(open(GP))
    d = DR.load(); val = lambda k: DR.val(d, k)
    N = {n['unit_id']: n for n in g['nodes']}
    E = {e['stream_id']: e for e in g['edges']}

    def put(k, v, note):
        assert k in E, k
        E[k]['rate'] = {'value': round(v, 6), 'unit': 'kg/d', 'status': 'study', 'note': note}

    # ---- litho train: real tools, stub retired ------------------------------------------------
    starts = val(LT + 'starts_per_d')
    spin_kW, bake_kW, uv_W = val(LT + 'spin_peak_kW'), val(LT + 'softbake_kW'), val(LT + 'uv_wall_W')
    dev_g = starts * val(LT + 'developer_mL_per_wafer') * 1.0 / 1000        # kg/d at ~1.0 kg/L developer
    # duties: spin 2 min/wafer at peak, hotplate 5 min/wafer cycle + a 100 C hold loss, LED 20 s/wafer, bench pumps
    coat_kWh = spin_kW * starts * 2 / 60 + bake_kW * starts * 5 / 60 + 0.015 * 24
    coat_kW = coat_kWh / 24
    align_kW = uv_W * starts * 20 / 3600 / 24 / 1000 + 0.004                # LED duty + stage/controls parasitic
    dev_kW = 0.008                                                          # bench circulation + N2 puff class
    litho_kW = coat_kW + align_kW + dev_kW
    node(g, N, 'LITHO_COAT', 'FAB', 'coater',
         'Spin-coater line: spin bowl, vacuum chuck, softbake hotplate. Parent LITHO_STUB retired into the real '
         'tools (AQS-LITH-001 rev C; A-M-287).')
    node(g, N, 'LITHO_ALIGN', 'FAB', 'aligner',
         'Contact aligner: 365 nm LED array over a 100 mm field, leadscrew stage (AQS-LITH-001 rev C; A-M-287). '
         'Not a stepper.')
    node(g, N, 'LITHO_DEV', 'FAB', 'wet_bench',
         'Wet develop bench on the WET_BENCH chemistry class (TMAH/KOH developer fork, S38 resist-waste loop); '
         'developer is a share of the fab resist/solvent issue (A-M-287).')
    N['LITHO_COAT']['params'].update(
        equipment_id='LITHO-COAT-01', starts_d=starts, spin_peak_kW=spin_kW, softbake_kW=bake_kW,
        kWh_d=round(coat_kWh, 4), size_mm=[1200, 800, 1400], size_note='L x W x H mm, issued envelope (A-M-287)',
        design=dict(machine='spin-coater line', chuck_mm=150, spin_rpm=5000, dispense_mL_per_wafer=2.0,
                    softbake_C=100, chemistry='novolac resist, 1 um (AQS-LITH-001)',
                    duty_kW=round(coat_kW, 4), peak_kW=spin_kW))
    N['LITHO_ALIGN']['params'].update(
        equipment_id='LITHO-ALIGN-01', starts_d=starts,
        size_mm=[1200, 600, 800], size_note='L x W x H mm, AQS-LITH-001 rev C frame 6061',
        design=dict(machine='contact aligner', source='365 nm LED array, 1 W optical (AQS-LITH-001)',
                    dose='10 mW/cm2 x 20 s = 200 mJ/cm2', field_mm=100, stage='leadscrew 1 mm pitch, 10 um repeatability',
                    mask='chrome on glass, 100 um pattern', duty_kW=round(align_kW, 4), peak_kW=0.25))
    N['LITHO_DEV']['params'].update(
        equipment_id='LITHO-DEV-01', starts_d=starts, developer_kg_d=round(dev_g, 4),
        size_mm=[1200, 600, 900], size_note='L x W x H mm, issued envelope (A-M-287)',
        design=dict(machine='wet develop bench', developer='TMAH 2.38 % class, shared WET_BENCH chemistry fork',
                    puddle_mL_per_wafer=val(LT + 'developer_mL_per_wafer'), waste='S38-class resist/solvent loop to OIL_FRAC',
                    duty_kW=round(dev_kW, 4), peak_kW=0.05))
    for u, kw in (('LITHO_COAT', coat_kW), ('LITHO_ALIGN', align_kW), ('LITHO_DEV', dev_kW)):
        N[u]['continuous_kw'] = kwr(kw, f'{TAG}: tool duty at {starts} wafer starts/d (AQS-LITH-001 rev C; A-M-287).')
        feed(g, E, u, kw, f'Feed equal to {u} continuous_kw. | {TAG}.')
    # flows move to the real tools: fab issue -> COAT -> (wafer carry) -> DEV -> OIL_FRAC
    E['IA-LITHO-IN'].update(to_unit_id='LITHO_COAT', to_sector_id='FAB',
                            notes='Re-pointed from LITHO_STUB at its retirement: fab resist/solvent issue to the '
                                  'coat line (A-M-287).')
    E['IA-LITHO-OUT'].update(from_unit_id='LITHO_DEV', from_sector_id='FAB',
                             notes='Re-pointed from LITHO_STUB at its retirement: spent resist and solvent to the '
                                   'oil line (A-M-287).')
    if 'IA-LITHO-CARRY' not in E:
        src = json.loads(json.dumps(E['IA-LITHO-IN']))
        src.update(stream_id='IA-LITHO-CARRY', from_unit_id='LITHO_COAT', from_sector_id='FAB',
                   to_unit_id='LITHO_DEV', to_sector_id='FAB',
                   carries='resist/solvent carry (coat catch bowl + developer) to the develop bench',
                   notes='Created at the LITHO_STUB retirement so each real tool closes (A-M-287).')
        g['edges'].append(src); E['IA-LITHO-CARRY'] = src
    put('IA-LITHO-CARRY', float(E['IA-LITHO-IN']['rate']['value'] or 0),
        'Resist/solvent carry coat -> develop at the fab issue rate (the coated wafers ride the tool-to-tool '
        'handoff; wafer mass is below graph resolution). A-M-284.')
    # retire the stub
    N['LITHO_STUB'].update({'presence': 'retired', 'class': 'study_stub',
                            'notes': 'Retired 2026-10-19: parent stub replaced by the real tools LITHO_COAT / '
                                     'LITHO_ALIGN / LITHO_DEV, which carry its flows and duty (AQS-EQP-STUDY-001 '
                                     'rev G; A-M-287). Kept as a retired node for history; class value is historical.'})
    if 'SF-LITHO_STUB' in E:
        E['SF-LITHO_STUB'].update(presence='retired')
        E['SF-LITHO_STUB']['rate'] = {'value': 0.0, 'unit': 'kW', 'status': 'study',
                                      'note': 'Edge retired with LITHO_STUB; the real tools carry their own SF feeds (A-M-287).'}

    # ---- SOLAR_PV_CELL: study_stub -> real tool wired to pv_cell_line (X-MFG-38) ----------------
    pv = N['SOLAR_PV_CELL']
    pv['class'] = 'tool'
    pv['notes'] = ('In-house PV cell line (X-MFG-38, AQS-DUTY-071, A-M-178): texture, POCl3 diffusion, PSG etch, '
                   'PECVD SiNx, screen print, fast firing, IV. Tool table in params.design; not the yard array '
                   '(PV_ARRAY). Study_stub class retired at the A-M-295 disposition.')
    pv['params']['size_note'] = 'L x W x H mm, issued envelope (X-MFG-38 tool line)'

    # ---- REMIN: dosing skid from the water-train chemistry --------------------------------------
    p = N['REMIN']['params']
    drink = p.get('drink_L_d', 10)
    ca_g = drink * p.get('Ca_mg_L', 25) / 1000
    mg_g = drink * p.get('Mg_mg_L', 10) / 1000
    caoh2_g = ca_g * 74.09 / 40.078
    mgcl2_g = mg_g * 95.21 / 24.305
    remin_kW = (2 * 8 + 30) / 1000        # 2 x metering pumps 8 W + UV unit 30 W
    N['REMIN']['class'] = 'dose'
    N['REMIN']['notes'] = ('Remineralization dosing skid: Ca(OH)2 + MgCl2 metering into the potable drink stream, '
                           'then UV (WHO-class Ca 25 / Mg 10 mg/L targets on the 10 L/d drink basis; '
                           'AQS-EQP-STUDY-001 sec.4; A-M-285).')
    p['design'] = dict(machine='remineralization dosing skid', pumps='2 x metering diaphragm (Ca slurry, MgCl2)',
                       uv='UV unit after the dose (potable integrity)', ca_oh2_g_d=round(caoh2_g, 4),
                       mgcl2_g_d=round(mgcl2_g, 4), drink_L_d=drink, duty_kW=round(remin_kW, 4),
                       chemistry='hydroxide crib salts (AQS-WTR-001); no farm S07 tee')
    N['REMIN']['continuous_kw'] = kwr(remin_kW, f'{TAG}: 2 x 8 W metering pumps + 30 W UV at the 10 L/d drink basis '
                                                f'(AQS-EQP-STUDY-001 sec.4; A-M-285).')
    feed(g, E, 'REMIN', remin_kW, f'Feed equal to REMIN continuous_kw. | {TAG}.')

    # ---- VCD_TRAIN: MVC still stack from the 17 kWh/m3 basis -------------------------------------
    vcd = N['VCD_TRAIN']['params']
    feed_m3 = vcd.get('feed_m3_d', 0.3332)
    sec = val('WTR.potable-upw-train.VCD_TRAIN.sec_kWh_m3')
    dist = feed_m3 * 0.9                                     # brine 10 % of feed (IA-VCD-BD/S28 class)
    q_lat = dist * 1000 * 2257 / 86400                       # kW thermal latent at the distillate rate (IAPWS_IF97)
    a_hx = q_lat / (2.8 * 5.0)                               # m2 at U 2.8 kW/m2 K, lift 5 K (PERRY9_EVAP class)
    N['VCD_TRAIN']['class'] = 'evaporator'
    N['VCD_TRAIN']['notes'] = ('Vapor-compression distillation still stack: evaporator/condenser HX + scroll '
                               'compressor + separator, 2 x 100 % (X-RED-05); 17 kWh/m3 driver basis '
                               '(AQS-EQP-STUDY-001 sec.3; A-M-285).')
    vcd['design'] = dict(machine='MVC still stack', modules=vcd.get('units_installed', 2),
                         compressor='scroll class (small-MVC)', hx_area_m2=round(a_hx, 3),
                         q_latent_kW=round(q_lat, 3), feed_m3_d=feed_m3, distillate_m3_d=round(dist, 4),
                         sec_kWh_m3=sec, duty_kW=N['VCD_TRAIN']['continuous_kw']['value'],
                         basis='0.333 m3/d x 17 kWh/m3 / 24 h at the issued band midpoint (A-M-149)')

    # ---- BLOW_MOLD: continuous-extrusion blow molder at the wax duty ------------------------------
    blow_in = float((E['IA-BLOW-IN'].get('rate') or {}).get('value') or 0)
    rate_kg_h = 2.8                                          # Precious Plastic class throughput (SI-MFG-01)
    hours = blow_in / rate_kg_h
    ext_kW, clamp_kW, air_kW = 2.2, 0.75, 0.75               # SI-MFG-01 motor class + clamp + air (AQS-REQ-KW-001)
    blow_kWh = ext_kW * hours + (clamp_kW + air_kW) * hours * 0.5
    blow_kW = blow_kWh / 24
    N['BLOW_MOLD']['class'] = 'former'
    N['BLOW_MOLD']['notes'] = ('Continuous-extrusion blow molder (Precious Plastic class): wax/polymer articles for '
                               'the shop goods loop on IA-BLOW-IN; scrap to the oil line (AQS-EQP-MFG-001; A-M-285).')
    N['BLOW_MOLD']['params'].update(peak_kw=round(ext_kW + clamp_kW + air_kW, 2), avg_kw=round(blow_kW, 4),
                                    kWh_d=round(blow_kWh, 3),
                                    design=dict(machine='continuous-extrusion blow molder', extruder_kW=ext_kW,
                                                clamp_kW=clamp_kW, air_kW=air_kW, rate_kg_h=rate_kg_h,
                                                run_h_d=round(hours, 2), feed_kg_d=round(blow_in, 4),
                                                products='molded articles to MFG_SHOP (IA-BLOW-OUT)',
                                                duty_kW=round(blow_kW, 4)))
    N['BLOW_MOLD']['continuous_kw'] = kwr(blow_kW, f'{TAG}: extruder {ext_kW} kW + clamp/air duty over a '
                                                   f'{hours:.1f} h/d campaign at {blow_in:.2f} kg/d wax feed '
                                                   f'(AQS-EQP-MFG-001 / AQS-REQ-KW-001 SI-MFG-01; A-M-285).')
    feed(g, E, 'BLOW_MOLD', blow_kW, f'Feed equal to BLOW_MOLD continuous_kw. | {TAG}.')

    # ---- ELECTRODE_COAT: booth + IR cure at the recoat duty ----------------------------------------
    exh_kW, cure_kW = 0.35, 1.2                              # booth exhaust fan + IR cure panel (ST-ELC-01 class)
    elc_kWh = exh_kW * 2.0 + cure_kW * 1.0                   # 2 h/d booth + 1 h/d cure campaign
    elc_kW = elc_kWh / 24
    N['ELECTRODE_COAT']['class'] = 'coater'
    N['ELECTRODE_COAT']['notes'] = ('Electrode coating booth for EW/BMED replaceable electrodes (non-precious M1 '
                                    'carbon/Ni class): exhaust to MET_AHU, recoat loop IA-COAT-IN/OUT (AQS-MFG-ELC-001; '
                                    'A-M-285).')
    N['ELECTRODE_COAT']['params'].update(avg_kw=round(elc_kW, 4), kWh_d=round(elc_kWh, 3),
                                         design=dict(machine='coating booth + IR cure', exhaust_kW=exh_kW,
                                                     cure_kW=cure_kW, campaign_h_d=2.0, cure_h_d=1.0,
                                                     formulation='carbon / Ni non-precious M1 class (RuO2-IrO2 deferred)',
                                                     exhaust='MET_AHU -> MET_SCRUB (S71-S72)',
                                                     recoat_loop='IA-COAT-IN/OUT 0.02 kg/d, net zero', duty_kW=round(elc_kW, 4)))
    N['ELECTRODE_COAT']['continuous_kw'] = kwr(elc_kW, f'{TAG}: booth exhaust {exh_kW} kW x 2 h/d + IR cure '
                                                       f'{cure_kW} kW x 1 h/d campaign at the 0.02 kg/d anode recoat '
                                                       f'loop (AQS-MFG-ELC-001 Rev B; A-M-285).')
    feed(g, E, 'ELECTRODE_COAT', elc_kW, f'Feed equal to ELECTRODE_COAT continuous_kw. | {TAG}.')

    # ---- GEO_ORC: real ORC geometry, installed standby per D-GEO_ORC ------------------------------
    q_sink = val('GEO.orc-train.q_sink_kW'); eta = val('GEO.orc-train.eta_th')
    p_orc = q_sink * eta
    o = N['GEO_ORC']
    o['class'] = 'orc'
    o['notes'] = ('Binary ORC skid as INSTALLED STANDBY: owner ruling D-GEO_ORC (2026-10-18) keeps the endpoint at '
                  '0 kW_e with the Carnot study as record (AQS-HEAT-STUDY-002 Rev A); the machine is geometrically '
                  'real at the 12 kW_th dry-cooler context (A-M-244) so the day a surplus-heat source is issued the '
                  'skid is placed, not designed. presence stays placeholder; continuous_kw stays null (A-M-285).')
    o['params']['design'] = dict(machine='binary ORC skid (installed standby)', p_rated_kW_e=round(p_orc, 2),
                                 q_sink_kW_th=q_sink, eta_th=eta, working_fluid='R245fa class',
                                 expander='scroll expander + generator', evaporator_kW_th=q_sink,
                                 condenser_kW_th=round(q_sink * (1 - eta), 2), feed_pump_kW=0.05,
                                 basis='D-GEO_ORC: study endpoint 0 kW_e; geometry at the A-M-244 12 kW dry-cooler '
                                       'context so the standby is real (A-M-285)',
                                 placement='electrical_yard.py massing stands in (unit map row)')
    # ---- X-LOC-09 locale-replacement units (placeholders; sites/mars and later locales) -----------
    # Mars design pass (AQS-SITE-009 section 3): the thin CO2 atmosphere gives no vent sink, no
    # oxidant and no convective heat sink, and the surface pressure sits at the triple point of
    # water. Each unit below is the different-technology replacement the scaling actions name.
    # They stay placeholder at the Earth reference plant (endpoint 0; nothing sized from a need
    # the baseline does not have); the locale profile's scaling actions place them.
    def lnode(uid, sector, cls, role, design, note):
        n = node(g, N, uid, sector, cls, note, presence='placeholder', role=role)
        n['continuous_kw'] = None
        n['params']['design'] = design
        return n

    rad_area_per_kW = 1000.0 / (0.90 * 5.670374419e-8 * (328.0 ** 4 - 180.0 ** 4))   # Stefan-Boltzmann
    ln = lnode('RAD_PANEL', 'HEAT', 'radiator', None,
               dict(rated_kW=12.0, radiator_K=328.0, emissivity=0.90, sink_K=180.0,
                    area_m2_per_kW=round(rad_area_per_kW, 2),
                    area_m2_at_duty=round(rad_area_per_kW * 12.0, 1),
                    loop='65/45 C low-grade water loop, mean 55 C (328 K), carried from the DRY_COOLER design (AQS-THM-002)',
                    basis='A-M-396 (sky sink 180 K), A-M-397 (emissivity 0.90); duty context A-M-244'),
               'Space radiator at the DRY_COOLER duty context (X-LOC-09): rejects to the sky where the site '
               'gives no air heat sink. Area follows the Stefan-Boltzmann law (heat_rejection.radiator_m2_per_kW). '
               'presence stays placeholder at the Earth reference, which rejects through DRY_COOLER and GEO_GHEX.')
    ln['params']['rated_kW'] = 12.0   # duty at the top level: the heat_rejection level reads it (A-M-244 context)
    lnode('TANK_BLD', 'WTR', 'press_tank', None,
          dict(design_kPa_g=200.0, fluid='water', roles='pumped fire supply and treated-water buffer '
               '(replaces CATCH_TANK); gravity reserve re-pumped (replaces ROOF_TANK)',
               volume='set by the locale fire-water and buffer calculation at the design pass',
               basis='A-M-400'),
          'Closed bladder tank inside the pressurised shell (X-LOC-09): holds water under a gas pad '
          'where the ambient pressure sits at the triple point of water, so there is no free surface '
          'open to shell gas and no ambient-pressure liquid water. Low design pressure keeps the '
          'vessel light-gauge; volume follows the units it replaces.')
    lnode('REC_HDR', 'GAS', 'recovery_header', None,
          dict(service='relief discharges and process offgas return to a hold-and-reprocess skid',
               discharge='nothing vents to site atmosphere (profile capabilities.vent_sink false)',
               sizing='header and hold sized to the largest single relief contingency at the design pass',
               basis='A-M-398'),
          'Closed vent and relief recovery header (X-LOC-09): every relief valve and vent scrubber '
          'discharge returns through the header to recovery, so the site needs no vent sink.')
    lnode('CAT_OX', 'OIL', 'catalytic', None,
          dict(service='catalytic oxidation of waste CO and organics on a plant-oxygen bleed',
               bed_C=450, feed='7.097 kg/d flue class carried from the AFTERBURNER duty (X-SAN-01)',
               trim_duty='bed trim heater duty is sized at the locale design pass',
               basis='A-M-399'),
          'Catalytic waste-gas oxidiser (X-LOC-09): oxidises plant waste streams on plant oxygen '
          'where the atmosphere gives no oxidant, at catalyst temperatures far below the 850 C '
          'thermal chamber it replaces (X-SAN-01).')
    lnode('E_HEAT', 'FOUNDRY', 'resistance_heater', 'load',
          dict(connected_kW=30.0, service='N+1 melt trim heat, resistance elements, standby-zero on '
               'the design day (same dispatch discipline as the fuel-fired unit it replaces)',
               basis='A-M-283 (30 kW connected duty carried from COMB_HEAT)'),
          'Electric resistance trim heat (X-LOC-09): carries the N+1 melt heat duty on the grid '
          'where combustion has no atmospheric oxidant.')

    if write:
        open(GP, 'w').write(json.dumps(g, indent=2) + '\n')
    return dict(litho_kW=round(litho_kW, 4), coat_kW=round(coat_kW, 4), align_kW=round(align_kW, 4), dev_kW=dev_kW,
                developer_kg_d=round(dev_g, 4), remin_kW=round(remin_kW, 4), vcd_hx_m2=round(a_hx, 3),
                blow_kW=round(blow_kW, 4), blow_run_h=round(hours, 2), elc_kW=round(elc_kW, 4),
                orc_standby_kW_e=round(p_orc, 2))


def main():
    out = apply(write='--write' in sys.argv)
    print(json.dumps(out, indent=1, default=float))


if __name__ == '__main__':
    main()

"""AQS-MFG-010 MFG_SHOP tool list (rev C, X-MFG-37, A-M-177). Throughputs from the graph; the four metal tools are designed in-house from physics:
melt energy = (cp_s dT + L + cp_l superheat)/eta [CRC_CU]; atomiser = Ar recirculation work GMR x R T ln(P2/P1)/(M eta) plus tundish heat;
rolling and drawing = mean flow stress x true strain / (rho eta) [DIETER1988] plus no-load running. Nameplate from the batch rate.
Machine tools in the shop keep their study nameplate and utilisation. Rev C (X-ELS-02): metering split - the four metal tools carry their own
continuous_kw stamps (per-tool kWh/d avg, fed by their own SF circuits) and MFG_SHOP covers the six shop machine tools only; roster connected
kW and the coincident peak keep the MCC-1 framing and total roster demand is unchanged. Writes docs-authority/MFG_TOOLS.md; prints the roster
aggregates, the shop-machine-tool subtotal and the four per-tool rows for write_graph stamping."""
import json, math, os, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, R); os.chdir(R)
if '--graph' in sys.argv:
    print('DEPRECATED: _mfg_tools --graph stamping moved to flow_graph/param/write_graph.py (X-ELS-02 rev C metering split, '
          'AQS-MFG-010 rev C; the regenerator spawns this module without --graph and write_graph owns the stamps).', file=sys.stderr)
    sys.exit(2)
from flow_graph.param import drivers as DR
d = DR.load(); v = lambda k: DR.val(d, k)
g=json.load(open('flow_graph/plant_flow_graph.json'));N={n['unit_id']:n for n in g['nodes']}
def thr(u):   # R11 Rev AC regen: params.duty strings were dropped from the graph; throughput falls back to the live mass inflow
    s = (N[u].get('params') or {}).get('duty')
    if isinstance(s, str) and 'In ' in s: return float(s.split('In ')[1].split(' ')[0])
    return sum(e['rate']['value'] or 0 for e in g['edges'] if e['to_unit_id'] == u and e['presence'] == 'present' and 'mass' in (e.get('layers') or []) and (e['rate'] or {}).get('unit') == 'kg/d')
q_melt = (v('melt_cp_solid_kJ_kgK')*(v('MFG.tools-metal-forming-train.metal-forming.MET_MELT.cu_T_melt_C') - v('MFG.tools-metal-forming-train.metal-forming.MET_MELT.charge_T_from_C')) + v('melt_L_kJ_kg') + v('melt_cp_liq_kJ_kgK')*v('melt_superheat_K'))/v('melt_eta')/3600   # kWh/kg
m_melt = thr('MET_MELT'); heats = math.ceil(m_melt/v('melt_charge_kg'))
kw_melt = math.ceil(v('melt_charge_kg')*q_melt/v('melt_time_h')*2)/2
e_melt = q_melt*m_melt + v('melt_hold_kW')*v('MFG.tools-metal-forming-train.metal-forming.MET_MELT.hold_h')*heats
T_AR = v('MFG.tools-metal-forming-train.metal-forming.GAS_ATOMIZER.ar_T_K'); M_AR = 0.03995; G = 9.81
SHIFT_H = v('MFG.tools-metal-forming-train.hall-services.MFG_SHOP.shift_h')
# atomiser (A-M-416): argon is compressed once into a receiver at atom_store_bar and discharged to the nozzle supply during the pour
w_ar = 8.314*T_AR/M_AR*math.log(v('atom_store_bar'))/v('atom_comp_eta')/3.6e6*v('atom_GMR')                     # kWh/kg metal
m_at = thr('GAS_ATOMIZER'); heats_at = max(1, math.ceil(m_at/v('melt_charge_kg'))); batch_at = m_at/heats_at
mdot_at = v('atom_Cd')*math.pi/4*(v('atom_nozzle_mm')/1000)**2*v('atom_melt_rho_kg_m3')*math.sqrt(2*G*v('atom_head_mm')/1000)   # kg/s melt
pour_s = batch_at/mdot_at; gas_kg = v('atom_GMR')*batch_at
V_rx = gas_kg*8.314*T_AR/M_AR/((v('atom_store_bar') - v('atom_P_bar'))*1e5)                                  # m3 receiver
recharge_h = SHIFT_H/heats_at
kw_at = math.ceil(w_ar*batch_at/recharge_h*2)/2
# cold mill (A-M-416): cast slab of the melt charge class rolled at constant width, plane strain
m_mill = thr('COLD_MILL'); heats_mill = max(1, math.ceil(m_mill/v('melt_charge_kg'))); slab_kg = m_mill/heats_mill
RHO_CU = v('MFG.tools-metal-forming-train.metal-forming.WIRE_DRAW.ws_cu_density_g_cm3')*1000
t0 = v('mill_slab_t_mm'); L0 = v('mill_slab_L_mm'); w0 = slab_kg/(RHO_CU*t0/1000*L0/1000)*1000              # mm
tf = t0*math.exp(-v('roll_strain')); r = v('mill_pass_reduction'); n_roll = math.ceil(v('roll_strain')/-math.log(1 - r))
gauges = [round(max(t0*(1 - r)**k, tf), 3) for k in range(1, n_roll + 1)]
face_mm = math.ceil(w0*(1 + v('mill_edge_margin'))/10)*10
DESIGN = dict(atomiser=dict(heats_d=heats_at, batch_kg=round(batch_at, 3), melt_kg_min=round(mdot_at*60, 2), pour_s=round(pour_s, 1),
                            argon_kg_batch=round(gas_kg, 2), receiver_m3=round(V_rx, 3), store_bar=v('atom_store_bar'), supply_bar=v('atom_P_bar'),
                            recharge_h=round(recharge_h, 2), compressor_kW=kw_at, nozzle_mm=v('atom_nozzle_mm'), head_mm=v('atom_head_mm')),
              mill=dict(heats_d=heats_mill, slab_kg=round(slab_kg, 3), slab_t_mm=t0, slab_L_mm=L0, slab_w_mm=round(w0, 1), final_mm=round(tf, 3),
                        strip_L_m=round(L0/1000*math.exp(v('roll_strain')), 2), passes=n_roll, gauges_mm=gauges, face_mm=face_mm, pass_reduction=r))
e_at = w_ar*m_at + v('atom_tundish_kW')*v('MFG.tools-metal-forming-train.metal-forming.GAS_ATOMIZER.tundish_h')
w_def = lambda eps: v('cu_flow_stress_MPa')*1e6*eps/8960/v('deform_eta')/3.6e6                                          # kWh/kg
e_mill = w_def(v('roll_strain'))*thr('COLD_MILL') + v('mill_kW')*v('mill_idle_frac')*v('mill_run_h')
e_draw = w_def(v('draw_strain'))*thr('WIRE_DRAW') + v('draw_kW')*v('mill_idle_frac')*v('draw_run_h')
# shop machine tools: study nameplate and utilisation (A-M-177) from drivers.json
SHOP = v('MFG.tools-metal-forming-train.hall-services.MFG_SHOP.shop_tools')
def _shop(name):   # (nameplate kW, kWh/d = kW x utilisation x shift)
    t = SHOP[name]; return t['kw'], t['kw']*t['util']*SHIFT_H
# (tool, serves, nameplate kW, energy kWh/d, basis)
T=[('Induction melt furnace, coreless, 10 kg Cu crucible','MET_MELT',kw_melt,e_melt,f"{q_melt:.3f} kWh/kg x {m_melt:.2f} kg/d ((0.43 x 1060 + 208.7 + 0.516 x 100) kJ/kg / 0.55, CRC_CU) + hold 0.5 kW x 0.5 h x {heats} heat"),
   ('Close-coupled gas atomiser with Ar recirculation','GAS_ATOMIZER',kw_at,e_at,f"Ar GMR {v('atom_GMR'):g} stored at {v('atom_store_bar'):g} bar: {w_ar:.3f} kWh/kg x {m_at:.2f} kg/d + tundish {v('atom_tundish_kW'):g} kW x 1 h; nameplate recharges the receiver in {recharge_h:.1f} h"),
   ('Two-high cold rolling mill','COLD_MILL',v('mill_kW'),e_mill,f"250 MPa x strain 2.3 / 0.55 (DIETER1988) = {w_def(v('roll_strain')):.4f} kWh/kg x {thr('COLD_MILL'):.2f} kg/d + no-load 15 % x 1 h"),
   ('Bull-block wire drawer','WIRE_DRAW',v('draw_kW'),e_draw,f"250 MPa x strain 3.0 / 0.55 (DIETER1988) = {w_def(v('draw_strain')):.4f} kWh/kg x {thr('WIRE_DRAW'):.2f} kg/d + no-load 15 % x 1 h"),
   ('CNC vertical mill','shop',*_shop('CNC vertical mill'),'2.25 kW x 8 h'),
   ('Engine lathe','shop',*_shop('Engine lathe'),'1.65 kW x 8 h'),
   ('Band saw','shop',*_shop('Band saw'),'0.15 kW x 8 h'),
   ('Rotary-screw air compressor','shop',*_shop('Rotary-screw air compressor'),'2.00 kW x 8 h'),
   ('TIG/MIG welder','shop',*_shop('TIG/MIG welder'),'1.20 kW x 8 h'),
   ('Bench grinder, drill press, hand tools','shop',*_shop('Bench grinder, drill press, hand tools'),'0.40 kW x 8 h')]
E=sum(t[3] for t in T); peak=sum(t[2] for t in T); avg=E/24; coinc=round(kw_melt+kw_at+SHOP['CNC vertical mill']['kw']+SHOP['Rotary-screw air compressor']['kw'],1)
shop_e = sum(t[3] for t in T[4:]); shop_kw = sum(t[2] for t in T[4:])
metal = [(t[1], t[3]/24.0, t[3], t[2]) for t in T[:4]]
rows=[f"| {t} | {s} | {kw:.1f} | {b} | {e:.1f} |" for t,s,kw,e,b in T]
out=f"""# Manufacturing shop tool list

Document number: AQS-MFG-010
Revision: E
Date: 2026-10-29
Authority: the throughputs of MET_MELT, GAS_ATOMIZER, COLD_MILL and WIRE_DRAW in the plant flow graph; AQS-PLAN-007 task X-MFG-37 (assumption A-M-177); the metering split of task X-ELS-02. Generated by `docs-authority/_mfg_tools.py`; do not edit this page by hand. Study.

| Rev | Description | Date |
| --- | --- | --- |
| B | The four metal tools are designed in-house from their physics; revision A used energy figures per kilogram for bought tools. The method is registered as assumption A-M-177. | 2026-10-16 |
| C | Metering split of task X-ELS-02, with the tool list of A-M-177 unchanged. Each of the four metal tools carries its own continuous load (`continuous_kw`), equal to its daily energy averaged over 24 h, and is fed by its own circuit from SOL_ARK_60K. The continuous load of MFG_SHOP covers the six shop machine tools only. The connected load and the coincident peak of the list still frame the motor control centre MCC-1, and the total demand of the list is unchanged by the split. | 2026-10-21 |
| D | Purpose and scope added; text rewritten to the documentation style guide (AQS-DOC-002). No tool or value changed. | 2026-10-25 |
| E | The atomiser stores its argon in a receiver and recharges it between heats, so its nameplate follows from the recharge time rather than a fixed pour time (A-M-416). | 2026-10-29 |

## 1. Purpose and scope

The manufacturing shop (MFG_SHOP) and the metal-forming units melt, atomise, roll and draw metal, and machine and weld parts. This page lists the tools, the unit that each serves, its nameplate power, the basis of its daily energy use and that daily energy. The energy figures feed the electrical load list, and the nameplate powers feed the motor inventory (`flow_graph/inventory/motors.py` reads Table 2.1).

## 2. Tools

The shop works one 8 h shift a day. The four metal tools are designed in-house from the physics of the process: the energy to heat and melt the metal, to atomise it with gas, or to deform it. The shop machine tools keep their study utilisation, given as an average power over the shift.

Table 2.1. Tool list

| Tool | Serves | Nameplate kW | Energy basis | kWh/d |
| --- | --- | --- | --- | --- |
"""+"\n".join(rows)+f"""

## 3. Totals and metering

The tools in Table 2.1 use {E:.1f} kWh/d in total, an average of {avg:.2f} kW. Since revision C the four metal tools are metered at their own nodes, with average loads of {', '.join(f'{a:.4f} kW for {u}' for u,a,e,kwv in metal[:-1])} and {metal[-1][1]:.4f} kW for {metal[-1][0]}. MFG_SHOP carries the shop machine tools only: {shop_e:.1f} kWh/d, an average of {shop_e/24:.2f} kW, with {shop_kw:.1f} kW connected.

The connected load of the whole list is {peak:.1f} kW. The coincident peak is {coinc} kW, with the melt furnace, the atomiser, the CNC mill and the compressor running together. These two values still size the feeder to MCC-1.

The efficiencies, the flow stress and the atomising gas ratio are assumptions until trial runs are made (A-M-177).
"""
if '--json' not in sys.argv:   # --json: report only (read by docs-authority/_mfg_equipment.py), page untouched
    open('docs-authority/MFG_TOOLS.md','w').write(out)
print(json.dumps(dict(avg=round(avg,2),peak=coinc,connected=peak,
                      shop_avg=round(shop_e/24,4), shop_connected=round(shop_kw,1),
                      metal=[dict(unit=u, avg_kw=round(a,4), kwh_d=round(e,1), nameplate_kw=round(kwv,1)) for u,a,e,kwv in metal],
                      tools=[dict(tool=t, serves=sv, nameplate_kw=round(kw,1), kwh_d=round(e,1)) for t,sv,kw,e,b in T], design=DESIGN)))

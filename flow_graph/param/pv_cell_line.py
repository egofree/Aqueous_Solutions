"""X-MFG-38 in-house PV cell line tools for SOLAR_PV_CELL (AQS-DUTY-071, A-M-178). Batches of one wafer carrier, at the cells a day that replace the roof array (pv_wafer.py, A-M-437), through
texture, POCl3 diffusion, PSG etch, PECVD SiNx, screen print, fast firing and IV test. Energy from the physics of each tool:
baths and furnaces = heat-up of the heated mass m cp dT plus the insulated loss at temperature (ASTM_C680 radial method, sizing/heat.py
insulated_cylinder, INCROPERA7); PECVD = RF power density x electrode area x deposition time plus heater and vacuum pump; print, fire
and IV = drive or lamp power x time. Nameplate = the largest heat-up rate. Replaces the ST-SOLAR-01 datasheet share.
Run: python3 -m flow_graph.param.pv_cell_line [--write]"""
import json, os, sys
from . import drivers as DR
from .sizing import heat as HT
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GP = os.path.join(ROOT, 'flow_graph/plant_flow_graph.json')
PVL = 'FAB.wafer-line-train.SOLAR_PV_CELL.'   # U4b: sizing literals single-sourced from drivers.json (A-M-178)
def design(d, g=None):
    """Batches of one wafer carrier through the line; the cell rate is the replacement need of the roof array (pv_wafer.py, A-M-437)."""
    from . import pv_wafer
    import math
    v = lambda k: DR.val(d, k); T = []; nd = pv_wafer.need(d, g); cells = nd['cells_per_d']
    nb = v(PVL+'pvl_cassette_n'); batches = math.ceil(cells/nb)
    boat = int(v('pvl_diff_L_m')*1000/v(PVL+'pvl_boat_pitch_mm'))
    if boat < nb: raise SystemExit(f'pv_cell_line: the diffusion boat holds {boat} wafers, fewer than a carrier of {nb}')
    # texture: water bath heated once a day, held at temperature for each batch
    q = v('pvl_tex_L')*v(PVL+'pvl_water_cp_kJ_kgK')*(v('pvl_tex_C') - v(PVL+'pvl_amb_T_C'))/3600; _, loss = HT.insulated_cylinder(v('pvl_tex_C'), v(PVL+'pvl_tex_tank_D_mm'), v(PVL+'pvl_tex_tank_H_m'))
    T.append(('PV-TEX-01', 'KOH texture bath, 10 L PP tank, immersion heater, one carrier a batch', q/v('pvl_tex_heat_h') + loss/1000, q + loss/1000*v('pvl_tex_run_h')*batches))
    # diffusion tube furnace: heated once a day, one boat a batch
    q = v('pvl_diff_mass_kg')*v(PVL+'pvl_diff_cp_kJ_kgK')*(v('pvl_diff_C') - v(PVL+'pvl_amb_T_C'))/3600
    t, loss = HT.insulated_cylinder(v('pvl_diff_C'), v('pvl_diff_D_mm'), v('pvl_diff_L_m'), k_a=v('pvl_hot_k_a'), k_b=v('pvl_hot_k_b'))
    T.append(('PV-EMIT-01', f"POCl3 diffusion, quartz tube {v('pvl_diff_D_mm'):.0f} mm x {v('pvl_diff_L_m'):.1f} m, {t} mm ceramic fibre, boat of {boat} slots", q/v('pvl_diff_heat_h') + loss/1000, q + loss/1000*(v('pvl_diff_run_h')*batches + v('pvl_diff_heat_h')/2)))
    T.append(('PV-PSG-01', 'HF PSG etch, room temperature PP bath', 0.0, 0.0))
    # PECVD: the electrode holds one carrier of cells; platen and chamber follow from it
    area = nb*nd['cell_area_cm2']/1e4; chamber = math.sqrt(4*area/math.pi)*1000 + 2*v(PVL+'pvl_pecvd_clear_mm')
    rf = v('pvl_pecvd_W_cm2')*area*1e4/1000; qh = v(PVL+'pvl_pecvd_platen_kg_m2')*area*v(PVL+'pvl_pecvd_platen_cp_kJ_kgK')*(v('pvl_pecvd_C') - v(PVL+'pvl_amb_T_C'))/3600
    _, lh = HT.insulated_cylinder(v('pvl_pecvd_C'), chamber, v(PVL+'pvl_pecvd_chamber_H_m'), k_a=v('pvl_hot_k_a'), k_b=v('pvl_hot_k_b'))
    T.append(('PV-ARC-01', f'PECVD SiNx, parallel-plate RF, {area:.2f} m2 electrode in a {chamber:.0f} mm chamber, dry vacuum pump', rf + qh/v(PVL+'pvl_pecvd_heat_h') + lh/1000 + v('pvl_vac_kW'),
              (rf*v('pvl_pecvd_dep_h') + lh/1000*v('pvl_vac_h') + v('pvl_vac_kW')*v('pvl_vac_h'))*batches + qh))
    h = lambda k: v(PVL+k)*cells/60
    T.append(('PV-CON-01', 'Screen printer and 200 C dryer', v('pvl_print_kW') + v('pvl_dry_kW'), (v('pvl_print_kW') + v('pvl_dry_kW'))*h('pvl_print_min_cell')))
    T.append(('PV-FIRE-01', 'IR lamp fast-firing furnace', v('pvl_fire_kW'), v('pvl_fire_kW')*h('pvl_fire_min_cell')))
    T.append(('PV-IV-01', 'Flash IV tester', v('pvl_iv_kW'), v('pvl_iv_kW')*h('pvl_iv_min_cell')))
    E = sum(t[3] for t in T)
    return dict(need=nd, cells_per_d=cells, batches=batches, carrier=nb, tools=[dict(id=a, design=b, peak_kW=c, kWh_d=e) for a, b, c, e in T], kWh_d=E, avg_kW=E/24, peak_kW=max(t[2] for t in T),
                kWh_per_cell=E/cells)
def write(g, r):
    N = {n['unit_id']: n for n in g['nodes']}; E = {e['stream_id']: e for e in g['edges']}; n = N['SOLAR_PV_CELL']; TAG = 'X-MFG-38 (A-M-178, AQS-DUTY-071)'
    n['continuous_kw'] = {'value': round(r['avg_kW'], 4), 'unit': 'kW', 'status': 'study', 'note': f"{TAG}: {r['kWh_d']:.2f} kWh/d for {r['cells_per_d']:.1f} cells/d in {r['batches']} batches of one carrier (A-M-437); peak {r['peak_kW']:.2f} kW (one tool at a time)."}
    n['params']['avg_kw'] = round(r['avg_kW'], 4); n['params']['design'] = json.loads(json.dumps(r, default=float))
    for sid in ('SF-SOLAR_PV_CELL', 'SQ-SOLAR_PV_CELL'):   # R11 Rev AC regen: SQ-* heat edges died with HEAT_SINK in Rev AC; update what exists
        if sid in E: E[sid]['rate']['value'] = round(r['avg_kW'], 4)
    open(GP, 'w').write(json.dumps(g, indent=2))
    md = ['# PV cell line tools', '', 'Document number: AQS-DUTY-071', 'Revision: C', 'Date: 2026-10-30',
          'Generated by `flow_graph/param/pv_cell_line.py` from the plant graph and `flow_graph/param/drivers.json`. Do not edit by hand; change the generator or its inputs and run `python3 -m flow_graph.param.regen`.',
          'Authority: task X-MFG-38 of AQS-PLAN-007; study ST-SOLAR-01; assumptions A-M-178 and A-M-437. Study. Not a PE stamp.', '',
          '| Rev | Description | Date |', '| --- | --- | --- |',
          '| A | First issue: the tools of the photovoltaic cell line and their energy | 2026-10-16 |',
          '| B | Record of revisions, purpose and scope added; the method and notes written as sentences; tables numbered | 2026-10-29 |',
          '| C | The cell rate is the replacement need of the roof array instead of a study rate of 3 cells a day, and the wafers come from the plant by a selectable route (Sections 3 and 4, A-M-437). The tools run in batches of one wafer carrier. | 2026-10-30 |', '',
          '## 1. Purpose and scope', '',
          'This page sizes the tools of the photovoltaic (PV) cell line `SOLAR_PV_CELL` in the FAB sector, which turns wafers into solar cells. It gives the design, the peak power and the daily energy of each tool.', '',
          '## 2. Method', '',
          f"The line makes {r['cells_per_d']:.1f} cells a day on average (Section 3) in {r['batches']} batches of one wafer carrier of {r['carrier']:.0f} wafers. The baths and furnaces are heated once a day and held for each batch; printing, firing and test take a set time per cell. The tools run one after another, so the peak power of the line is that of the largest tool.", '',
          'Table 2.1 gives the tools.', '', 'Table 2.1. Cell line tools', '',
          '| Tool | Design | Peak kW | kWh/d |', '|---|---|---|---|']
    md += [f"| {t['id']} | {t['design']} | {t['peak_kW']:.2f} | {t['kWh_d']:.2f} |" for t in r['tools']]
    top = max(r['tools'], key=lambda t: t['kWh_d']) if r['tools'] else None
    md += ['', f"The peak power of the line is {r['peak_kW']:.2f} kW. The line uses {r['kWh_d']:.2f} kWh/d, an average of {r['avg_kW']:.3f} kW, or {r['kWh_per_cell']:.2f} kWh per cell."
           + (f" Tool {top['id']} uses the most energy; running a second batch in the same heat would spread its heat-up over twice as many cells." if top else ''),
           'The heat-up masses, the RF power density, the lamp power and the run times are assumptions until the first article of each tool has been run (A-M-178).', '']
    nd = r['need']; from . import pv_wafer; from .fab_silicon import design as fs_design
    md += ['## 3. Cell need', '',
           f"The line makes the cells that replace the plant's own roof array, PV_ARRAY, whose nameplate on the graph is {nd['array_kw']:.0f} kW. A module is replaced when its output has fallen to the end-of-life share of nameplate, which at the median degradation rate gives a life of {nd['life_yr']:.0f} years (JORDAN_KURTZ2013); random failures add their own share (JORDAN2017). "
           f"So {nd['repl_per_yr']*100:.2f} % of the array is replaced each year, {nd['W_d']:.0f} W of cells a day. One cell of {nd['cell_area_cm2']:.1f} cm2 at an efficiency of {nd['cell_eff']*100:.1f} % gives {nd['cell_W']:.2f} W at the standard irradiance of 1000 W/m2, so the line makes {nd['cells_per_d']:.1f} cells a day.", '',
           'The cells retired from end-of-life modules return their silicon to the chlorosilane loop of SI_REFINE on IA-PV-EOL, so in steady state the silicon of the cells installed is recovered and the quartz reduced falls by it. The finished cells go to PV_ARRAY on IA-PV-CELL. The module glass, encapsulant, ribbon and frame and the contact pastes are not yet on the graph (task X-RTE-PV-MODULE).', '',
           '## 4. Wafer route', '',
           f"The wafers come from WAFER_FAB on IA-PV-WAFER by the route that the driver pv_wafer_route selects, now {nd['route']}. Table 4.1 compares the two built routes and a larger puller that was evaluated and not built.", '',
           'Table 4.1. Wafer routes for the cell line', '', '| Route | Cell | Cells a day | Silicon, g/W | Growth furnace | Status |', '| --- | --- | --- | --- | --- | --- |']
    cz = pv_wafer.need(route='CZ_PSQ125', g=g); mcn = pv_wafer.need(route='CAST_MC156', g=g); mc = pv_wafer.cast(); m2 = pv_wafer.m2_puller(); fz = fs_design()
    md += [f"| CZ_PSQ125 | 125 mm semi-square, single crystal, {cz['cell_W']:.2f} W | {cz['cells_per_d']:.1f} | {cz['Si_g_per_W']/(1 - DR.val(DR.load(), 'FAB.wafer-line-train.cz_crop_frac')):.2f} | the existing puller; the charge is pulled every {fz['interval_d']:.0f} d on this route | built, default |",
           f"| CAST_MC156 | 156.75 mm square, multicrystalline, {mcn['cell_W']:.2f} W | {mcn['cells_per_d']:.1f} | {mcn['Si_g_per_W']/mc['usable']:.2f} | a cast furnace in WAFER_FAB: a {mc['block_cm']:.1f} cm block, {mc['height_cm']:.1f} cm high, {mc['charge_kg']:.1f} kg each {mc['interval_d']:.0f} d; held at {mc['held_kW']:.2f} kW, {mc['kWh_cast']:.0f} kWh a cast | built, selectable |",
           f"| Larger puller | 156.75 mm full square, single crystal, {m2['cell_W']:.2f} W | {nd['W_d']/m2['cell_W']:.1f} | — | a second puller for a {m2['ingot_D_cm']*10:.0f} mm ingot: a {m2['crucible_D_cm']*10:.0f} mm crucible with a least melt of {m2['min_melt_kg']:.0f} kg and a hot zone held at {m2['held_kW']:.1f} kW | evaluated, not built |", '',
           'The silicon per watt includes the kerf and what is cropped: the crown, tail and grind of the ingot, and the edges, foot and cap of the block. The semi-square route is the default on the merits: it shares the one puller, the hot zone and the refining with the fab wafers, and its single-crystal cells give more power per unit area and need less silicon per watt. The cast route is built as the second technology because it does not depend on the puller, so the array can still be renewed while the puller is down; it needs its own furnace and crops more of its charge. '
           'The larger puller would give the same cells in a larger format at the cost of a second hot zone and a least melt several times the charge of the existing puller, and the 125 mm format meets the need without it, so it is not built.', '',
           'The cell efficiencies are those of screen-printed cells with an aluminium back field (ITRPV2020) and are to be confirmed by testing the first in-house cells (A-M-437).']
    open(os.path.join(ROOT, 'docs-authority/sizing/PV_CELL_LINE.md'), 'w').write('\n'.join(md) + '\n')
def main():
    d = DR.load(); g = json.load(open(GP)); r = design(d, g); print(json.dumps(r, default=float))
    if '--write' in sys.argv: write(g, r)
if __name__ == '__main__': main()

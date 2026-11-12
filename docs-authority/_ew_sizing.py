"""AQS-DUTY-051. EW_1 to EW_9 cell sizing at the AQS-ASSAY-001 element envelope.
Basis (owner ruling Q-038, 2026-11-05; AGENTS.md sizing rule; A-M-460): the equipment of every
cell is rated for the largest deposit of its own element found in any feed case of the IA-FEED-01
envelope, at the design feed rate and leach recovery 1.0 - the five minor plateable metals each
carry the lumped fraction (the 'all in one element' reading of AQS-ASSAY-001 table 4.1). The
cell current is I = m z F / (M t CE) per element. The booked stream rates are computed from the
feed assay by solver.ew_products (X-QA-04): the IA-FEED-01 rate times the reference-point element
fraction at leach recovery 1.0 - no longer the S08 booking of the retired 150 kg/d feed audit.
A balance closes on one feed, the envelope sizes the equipment, so no case B lot forces a resize.
Study values are labeled and are in AQS-REG-002."""
import json, math, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flow_graph.param import drivers as DR
from flow_graph.param.constants import M as _M
from flow_graph.param.sizing import electrochem
from flow_graph.param.solver import ew_products
from flow_graph.param.ew_cells import EW_CELLS
_d=DR.load(); MCU=_M['Cu']
g=json.load(open('flow_graph/plant_flow_graph.json')); R={e['stream_id']:e['rate']['value'] for e in g['edges']}
EL={n:(el,_M[el],z,cls) for n,(el,z,cls) in EW_CELLS.items()}   # the cell-to-element map: flow_graph/param/ew_cells.py (single source with solver.ew_products, F-20261110-03)
FEED=R['IA-FEED-01']   # design feed rate, kg/d (AQS-ASSAY-001 section 3)
ENV=next(e for e in g['edges'] if e['stream_id']=='IA-FEED-01')['params']['assay_envelope']['element_envelope']
REC=DR.val(_d,'ew_leach_recovery_design')      # AQS-ASSAY-001 section 4 upper bound
DEP_REF={int(k):x for k,x in ew_products(_d,g)['dep'].items()}   # booked deposit rows (X-QA-04: computed from the feed assay, solver.ew_products)
FE=DR.val(_d,'ew_current_efficiency_design')   # drivers.json (needs_verification; published 0.85-0.92, SCHLESINGER2011)
J=DR.val(_d,'ew_current_density_A_m2')        # SCHLESINGER2011
PH=DR.val(_d,'DIGESTER.ew-cascade-train.ew_plate_height_m')    # A-M-040 (AQS-EW-MOD-001)
PW=DR.val(_d,'DIGESTER.ew-cascade-train.ew_plate_width_m')     # A-M-040 (AQS-EW-MOD-001)
AP=2*PH*PW       # both faces
PITCH=DR.val(_d,'DIGESTER.ew-cascade-train.ew_cathode_pitch_m')  # A-M-038 (50 mm cathode-anode)
V=DR.val(_d,'ew_cell_voltage_V')                # drivers.json (needs_verification)
WALL=DR.val(_d,'DIGESTER.ew-cascade-train.ew_tank_wall_m')       # AQS-DUTY-051 Rev A
END=DR.val(_d,'DIGESTER.ew-cascade-train.ew_tank_end_margin_m'); SIDE=DR.val(_d,'DIGESTER.ew-cascade-train.ew_tank_side_margin_m')
SUMP=DR.val(_d,'DIGESTER.ew-cascade-train.ew_tank_sump_m'); TOP=DR.val(_d,'DIGESTER.ew-cascade-train.ew_tank_cover_m'); FB=DR.val(_d,'DIGESTER.ew-cascade-train.ew_tank_freeboard_m')   # A-M-038 allowances
SHEET_TO=DR.val(_d,'ew_sheet_collection_cell')   # the forming share books on IA-EW-SHEET at the EW_9 collection point (write_graph.process)
ARR=DR.val(_d,'ew_minor_metal_arrangement')      # Q-041: 'selective' (five minor-metal cells) or 'merged' (one combined cell)
assert ARR in ('selective','merged'), ARR
MINOR=tuple(int(n) for n in DR.val(_d,'ew_minor_metal_cells'))   # the minor-metal cells (Q-041)
rows=[]
for n in range(1,10):
    el,M,z,env_key=EL[n]
    spec=ENV['elements'][env_key]
    dep=FEED*spec['fraction']*REC          # the cell's bounding deposit (equipment sizing basis)
    edge='IA-EW-SHEET' if n==SHEET_TO else f'IA-EW-MET-{n}'
    booked=R[edge]   # the cell's product edge; the forming share books on IA-EW-SHEET at the EW_9 collection point
    I=electrochem.faraday_current_A(dep,M,z,FE)   # bounding current at the element envelope deposit
    Nc=electrochem.cathode_count(I,J,AP); j=I/(Nc*AP)
    Li=Nc*PITCH+2*END; Wi=PW+2*SIDE; Hi=SUMP+PH+TOP+FB
    Lo,Wo,Ho=[round((x+2*WALL)*1000) for x in (Li,Wi)]+[round((Hi+WALL)*1000)]
    Vl=Li*Wi*(SUMP+PH+TOP); Q=R[[e['stream_id'] for e in g['edges'] if e['to_unit_id']==f'EW_{n}' and e['stream_id'].startswith('IA-EW')][0]]/DR.val(_d,'DIGESTER.ew-cascade-train.ew_liquor_rho_kg_m3')   # A-M-029
    rows.append(dict(cell=f'EW_{n}',metal=el,dep_kg_d=dep,dep_ref_kg_d=DEP_REF[n],env_case=spec['case'],
        edge=edge,booked_kg_d=booked,I_A=I,cathodes=Nc,anodes=Nc+1,j_A_m2=j,
        size_mm=[Lo,Wo,Ho],V_liq_m3=Vl,tau_min=Vl/Q*1440,P_kW=electrochem.dc_power_kW(I,V)))
tot=dict(I_A=sum(r['I_A'] for r in rows),dep=sum(r['dep_kg_d'] for r in rows),dep_ref=sum(r['dep_ref_kg_d'] for r in rows),P_kW=sum(r['P_kW'] for r in rows))
# Q-041 merged alternative: one combined minor-metal cell. The envelope gives the lumped
# fraction to a single element, so the merged cell's bounding current is the largest
# single-element current of the five (nickel basis); gold, silver, copper and iron keep
# their own cells in either arrangement.
mi=max(rows[n-1]['I_A'] for n in MINOR)
mc=electrochem.cathode_count(mi,J,AP); mj=mi/(mc*AP)
mLi=mc*PITCH+2*END; mWi=PW+2*SIDE
mLo,mWo,mHo=[round((x+2*WALL)*1000) for x in (mLi,mWi)]+[round((Hi+WALL)*1000)]
merged=dict(cell='EW_M',metal='Pb/Sn/Ni/Cd/Zn blend',I_A=mi,cathodes=mc,anodes=mc+1,j_A_m2=mj,
    size_mm=[mLo,mWo,mHo],P_kW=electrochem.dc_power_kW(mi,V),
    note='one tank, one channel, one bus run in place of the five minor-metal cells '
         '(four 250 A frames, four tanks, four bus runs saved)')
MD=os.path.join(os.path.dirname(os.path.abspath(__file__)),'sizing','EW_CELLS.md')
def write_md():
    """AQS-DUTY-051 Rev F: this duty sheet is a generator output (X-GOV-06 register clears at the commit that carries it)."""
    dc_bus=tot['P_kW']+sum(r['I_A'] for r in rows)*DR.val(_d,'ew_bus_drop_V')/1000
    X=['# EW_1 to EW_9 cell sizing','', 'Document number: AQS-DUTY-051', 'Revision: H', 'Date: 2026-11-10',
       f"Authority: graph Rev {g['revision']}; AQS-PLAN-007 MET-EW_n-02. Study. Not a PE stamp. Generated by `docs-authority/_ew_sizing.py` (writes this file). Study values in AQS-REG-002 (A-M-036 to A-M-040). Drivers from `flow_graph/param/drivers.json` (AQS-PAR-001).", '',
       '| Rev | Description | Date |', '| --- | --- | --- |',
       '| A | First issue. Current, electrodes, tank size, holdup and DC power per cell. | 2026-10-15 |',
       '| B | X-PAR acid-loop decision: current efficiency 0.85 and cell voltage 2.12 V (USBM chloride EW basis). | 2026-10-15 |',
       '| C | Rev AC regeneration: the script writes this duty sheet from the live graph; currents and tank sizes unchanged (held harvests), residence tracks the Rev AC cascade transit rates. | 2026-10-18 |',
       '| D | The sheet-mass column relabeled copper-equivalent (the bounding Faraday basis it always used); the feed-metal column marked as the cascade order, not a metal identification; finding 6 added. No per-species mass is published. | 2026-11-04 |',
       '| E | Owner ruling Q-038: the cascade rate moves to its supply basis - the S08 deposit rows (AQS-ASSAY-001 section 5) at leach recovery 1.0 - so every cell current, cathode count and tank re-solves at the element basis; the copper-equivalent bounding convention and the wear-goods closing-by-difference chain behind it are retired. Demand check and governing statement added to section 2. | 2026-11-04 |',
       '| F | Owner ruling Q-038 (2026-11-05): the equipment of every cell is rated at the AQS-ASSAY-001 element envelope (table 4.1) - the largest deposit of its own element in any feed case, at the design feed rate and leach recovery 1.0 - so no case B lot forces a resize (AGENTS.md sizing rule). The booked stream rates stay at the reference S08 rows; both deposit columns are published. | 2026-11-06 |',
       '| G | Owner ruling Q-041: the minor-metal arrangement is decided from first principles and, no clear winner existing, carried both ways as a selectable option (driver `ew_minor_metal_arrangement`); section 4 added with the analysis and the merged-cell sizing. No selective-arrangement figure changed. | 2026-11-06 |',
       '| H | X-QA-04: the booked deposit rows are computed from the feed assay (solver.ew_products: IA-FEED-01 rate x AQS-ASSAY-001 reference-point element fraction x leach recovery; the lumped other-plateable class splits evenly over the five minor metals, A-M-470) in place of the S08 booking of the retired 150 kg/d feed audit; the rows sum to 35.9637 kg/d, the plateable class of the reference feed. No equipment figure changed - the envelope basis of Rev F still governs it. | 2026-11-10 |', '',
       '## 1. Basis', '',
       '- Equipment rate basis (bounding envelope): the largest fraction of each plateable element found in any case of the IA-FEED-01 envelope (graph `params.assay_envelope.element_envelope`, the machine copy of AQS-ASSAY-001 table 4.1) at the design feed rate and leach recovery 1.0 (AQS-ASSAY-001 section 4 upper bound, driver `ew_leach_recovery_design`). The five minor plateable metals each carry the lumped fraction - the all-in-one-element reading. Design current per cell I = m z F / (M t CE), current efficiency 0.85 (USBM_CL_EW chloride EW 0.85-0.90, lower bound; study, A-M-036), molar mass and valence per element.',
       '- Rate basis (booked streams): the booked deposit of each cell is computed from the feed assay (X-QA-04): IA-FEED-01 rate x reference-point element fraction x leach recovery 1.0, the five minor metals splitting the lumped other-plateable class evenly (A-M-470). The rows sum to the plateable class of the reference feed; a balance closes on one feed, the envelope sizes the equipment; no single feed loads every cell at once (the largest simultaneous load is the reference case).',
       '- Demand check: the plated metal the plant consumes is the forming routes (half the Cu deposit to wire, half to mill; the Pb/Sn/Ni/Cd/Zn blend to powder - the AQS-DUTY-010 bases) plus the crew goods issue (the roster textile line, A-M-429), together a fraction of the supply. The supply governs the cascade rate; the surplus metal exports through the shop finished-goods export (self-sustaining plant rule).',
       '- Cathode current density 200 A/m² (AQS-EW-MOD-001, study). Plate immersed 0.60 × 0.42 m, both faces 0.504 m². Cathode pitch 100 mm with an anode between (50 mm cathode to anode). One more anode than cathodes.',
       '- Tank inside: length = cathodes × 100 mm + 2 × 75 mm ends; width plate + 2 × 50 mm; depth 150 mm sump + 420 mm plate + 100 mm cover + 80 mm freeboard. Wall 10 mm. Liquor density 1100 kg/m³ (AQS-DUTY-050).',
       '- Cell voltage 2.12 V: USBM_CL_EW 2.1 kWh/kg Cu from cupric chloride at CE 0.85 (study, A-M-039).', '',
       '## 2. Results', '',
       'The envelope deposit column sets the equipment (current, cathodes, tank, rectifier channel, bus). The booked column is the stream-rate basis, computed from the reference feed at recovery 1.0 (X-QA-04); the product-edge column shows where the cell plated mass books: the noble and iron harvests leave on their cell edge, the forming share (Cu and the blend) books on IA-EW-SHEET at the EW_9 collection point.',
       '',
       '| Cell | Metal | Envelope deposit, kg/d | Governing case | Booked, kg/d | I bounding, A | Cathodes / anodes | j, A/m² | Tank L × W × H, mm | Liquor m³ | Residence, min | DC kW |',
       '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for r in rows:
        X.append(f"| {r['cell']} | {r['metal']} | {r['dep_kg_d']:.4f} | {r['env_case']} | {r['dep_ref_kg_d']:.4f} | {r['I_A']:.1f} | {r['cathodes']} / {r['anodes']} | {round(r['j_A_m2'])} |"
                 f" {r['size_mm'][0]} × {r['size_mm'][1]} × {r['size_mm'][2]} | {r['V_liq_m3']:.3f} | {round(r['tau_min'])} | {r['P_kW']:.2f} |")
    X += [f"| Total | | {tot['dep']:.4f} | | {tot['dep_ref']:.4f} | {tot['I_A']:.1f} | | | | | | {tot['P_kW']:.2f} |", '',
       '## 3. Findings', '',
       '1. The issued envelope 600 × 420 × 650 mm on every EW node is the cathode plate, not the cell. The sized tanks above replace it in `params.sizing.size_mm`. The graph `size_mm` and the placement rows are not changed here; the aisle layout (cell pitch 750 mm) does not hold the sized tanks and was re-placed by `flow_graph/place_ew_aisle.py` (X-RSZ-03; re-run whenever the cathode counts move).',
       f"2. DC load at the electrodes is {tot['P_kW']:.1f} kW at {tot['I_A']:.0f} A at the bounding envelope (CE 0.85, cell 2.12 V; with the {DR.val(_d,'ew_bus_drop_V')} V bus drop the channel DC is {dc_bus:.2f} kW and the rectifier AC input re-solves at efficiency 0.80). The sum of the cell ratings is not a load that occurs at one time: no single feed case loads every cell to its envelope, and the largest simultaneous load is the reference case. The graph IA-DC-EW_n edges carry the cell plus bus drop at the bounding current, written by `flow_graph/param/write_graph.py` (AQS-ELEC-004).",
       f"3. Governing basis: supply. The supply (the booked deposits, {tot['dep_ref']:.1f} kg/d element at recovery 1.0) exceeds the plated-metal demand - the forming routes and the crew goods line - so the cascade runs at the dissolved-metal rate and the balance exports through the shop finished-goods line (IA-GOODS-SHIP). The retired basis (the wear-goods plug at 596.86 kg/d, 149 kg/person/d) booked about 7 times this current and about 8 times this rectifier load.",
       '4. Side-reaction H₂ on EW_1, EW_2, EW_4 and EW_9 (graph H₂ edges) would add Faradaic current not counted here. It is held with the AQS-DUTY-016 H₂/Cl₂ discrepancy (EDGE_RATING_DUTY) and needs an owner rate decision.',
       '5. Materials. The 316L frame in AQS-EW-MOD-001 is a wetted non-electrode metal and is withdrawn under AQS-STD-002 M3; racks are CPVC or PVC-U. Electrode materials for chloride with anodic Cl₂ (316L cathode, PbO₂ anode) were reopened as X-MAT-18 and are now titanium cathodes and mixed-metal-oxide anodes (AQS-STD-002 section 9).',
       '6. Product booking: the plated element mass of every cell books once. The forming share (Cu, Pb, Sn, Ni, Cd, Zn) rides IA-EW-SHEET from the EW_9 collection point and re-enters the ledger through the melt and forming products (wire, mill sheet, powder) on the AQS-DUTY-010 bases; the noble and iron harvests leave on their cell edges to the shop. The Rev D copper-equivalent convention (sheet mass bounding the plated rate at M_Cu, z = 2) is retired with the wear-goods chain that set it.',
       '7. The case B rows of AQS-ASSAY-001 table 4.1 were the resize trigger of the held design; at this envelope basis the trigger is closed - a case B lot runs within the sized equipment without a rebuild (the lot books its own rates on arrival, A-M-460).',
       '', '## 4. Minor-metal arrangement (Q-041)', '',
       'The five minor-metal cells (EW_4 lead, EW_5 tin, EW_6 nickel, EW_8 cadmium, EW_9 zinc) can stay separate or be merged into one cell. Owner ruling Q-041 (2026-11-05): decide from first principles - electrochemistry, current density, selectivity, mass transfer and energy - and if the analysis yields no clear winner, carry both arrangements as selectable options in the design data. Gold and silver stay on their own cells in either arrangement.',
       '',
       '- Selectivity. The published standard reduction potentials are about -0.13 V (lead), -0.14 V (tin), -0.26 V (nickel), -0.40 V (cadmium) and -0.76 V (zinc) against SHE (published tables, for example the CRC Handbook of Chemistry and Physics). Lead and tin sit 10 mV apart and co-plate in either arrangement; separation by potential is impossible. Nickel and cadmium sit 146 mV apart - the same order as the Nernst swing over the working deposit activities - so the separate arrangement needs per-cell potential control to hold purity, and without it gives mixed deposits anyway.',
       '- Hydrogen. Zinc plates below the hydrogen potential in the chloride liquor, so part of the zinc current makes H2 in both arrangements (finding 4). Not a differentiator.',
       '- Energy. The DC load is the plated metal (Faraday), identical in both arrangements.',
       '- Hardware. The merged cell saves four tanks, four rectifier channels (250 A frames, 6 kW of nameplate), four bus runs and four instrument sets, at a better space-time yield (2 cathodes in one tank against 7 across five tanks).',
       '- Cadmium. The differentiator. A merged cell carries cadmium into the powder blend; the separate cadmium cell holds it as a controlled stream (the blend basis itself books the minor metals together, AQS-DUTY-010, so the ledger is unchanged in either arrangement).',
       '- Verdict: no clear winner, so both are carried. Driver `ew_minor_metal_arrangement` selects `selective` (the nine-cell cascade as sized in section 2, the graph arrangement today) or `merged` (one combined cell, the alternative below). Switching the graph topology to the merged arrangement (five channels, one minor-metal unit in place of EW_4/5/6/8/9) is the EW-topology unit task, held until the owner selects it.',
       '',
       '| Arrangement | Current, A | Cathodes | Tanks | Channels | Nameplate, kW | DC kW |',
       '| --- | --- | --- | --- | --- | --- | --- |',
       f"| Selective (rated) | {sum(rows[n-1]['I_A'] for n in MINOR):.1f} | {sum(rows[n-1]['cathodes'] for n in MINOR)} | 5 | 5 | 7.5 | {sum(rows[n-1]['P_kW'] for n in MINOR):.2f} |",
       f"| Merged (alternative) | {merged['I_A']:.1f} | {merged['cathodes']} | 1 | 1 | 1.5 | {merged['P_kW']:.2f} |",
       '',
       f"The merged cell's bounding current is the largest single-element current of the five ({mi:.1f} A, nickel basis): the envelope gives the lumped fraction to one element at a time, so the combined cell never sees more than that charge per unit time."]
    open(MD,'w').write('\n'.join(X)+'\n')
if __name__=='__main__':
    write_md()
    print(json.dumps(dict(rows=rows,total=tot,merged_alt=merged,arrangement=ARR),indent=1))

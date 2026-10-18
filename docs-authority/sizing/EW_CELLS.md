# EW_1 to EW_9 cell sizing

Document number: AQS-DUTY-051
Revision: B
Date: 2026-10-15
Authority: graph Rev BH; AQS-PLAN-007 MET-EW_n-02. Study. Not a PE stamp. Script `docs-authority/_ew_sizing.py`. Study values in AQS-REG-002 (A-M-036 to A-M-040). Rev B drivers from `flow_graph/param/drivers.json` (AQS-PAR-001).

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue. Current, electrodes, tank size, holdup and DC power per cell. | 2026-10-15 |
| B | X-PAR acid-loop decision: current efficiency 0.85 and cell voltage 2.12 V (USBM chloride EW basis). | 2026-10-15 |

## 1. Basis

- Harvest: IA-EW-MET-n is a copper-equivalent sheet rate that bounds the element mass (AQS-ASSAY-001 section 4). Bounding current I = m / (M_Cu / 2F × 86 400), current efficiency 0.85 (USBM_CL_EW chloride EW 0.85-0.90, lower bound; study, A-M-036). EW_9 also books IA-EW-SHEET.
- Element current, for comparison: S08 deposits (AQS-ASSAY-001 section 5) with each metal's valence.
- Cathode current density 200 A/m² (AQS-EW-MOD-001, study). Plate immersed 0.60 × 0.42 m, both faces 0.504 m². Cathode pitch 100 mm with an anode between (50 mm cathode to anode). One more anode than cathodes.
- Tank inside: length = cathodes × 100 mm + 2 × 75 mm ends; width plate + 2 × 50 mm; depth 150 mm sump + 420 mm plate + 100 mm cover + 80 mm freeboard. Wall 10 mm. Liquor density 1100 kg/m³ (AQS-DUTY-050).
- Cell voltage 2.12 V: USBM_CL_EW 2.1 kWh/kg Cu from cupric chloride at CE 0.85 (study, A-M-039).

## 2. Results

| Cell | Metal | Edge kg/d | I bounding, A | I element, A | Cathodes / anodes | j, A/m² | Tank L × W × H, mm | Liquor m³ | Residence, min | DC kW |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EW_1 | Au | 59.87 | 2476 | 0.1 | 25 / 26 | 196 | 2670 × 720 × 760 | 1.243 | 459 | 5.25 |
| EW_2 | Ag | 59.89 | 2476 | 0.3 | 25 / 26 | 197 | 2670 × 720 × 760 | 1.243 | 466 | 5.25 |
| EW_3 | Cu | 22.48 | 930 | 308.7 | 10 / 11 | 184 | 1170 × 720 × 760 | 0.539 | 205 | 1.97 |
| EW_4 | Pb | 4.85 | 201 | 7.7 | 2 / 3 | 199 | 370 × 720 × 760 | 0.164 | 63 | 0.43 |
| EW_5 | Sn | 5.02 | 208 | 13.4 | 3 / 4 | 137 | 470 × 720 × 760 | 0.211 | 81 | 0.44 |
| EW_6 | Ni | 5.47 | 226 | 27.1 | 3 / 4 | 150 | 470 × 720 × 760 | 0.211 | 81 | 0.48 |
| EW_7 | Fe | 71.14 | 2942 | 1185.0 | 30 / 31 | 195 | 3170 × 720 × 760 | 1.477 | 568 | 6.24 |
| EW_8 | Cd | 5.05 | 209 | 14.1 | 3 / 4 | 138 | 470 × 720 × 760 | 0.211 | 83 | 0.44 |
| EW_9 | Zn | 75.33 | 3115 | 24.3 | 31 / 32 | 199 | 3270 × 720 × 760 | 1.524 | 597 | 6.60 |
| Total | | | 12781 | 1581 | | | | | | 27.10 |

## 3. Findings

1. The issued envelope 600 × 420 × 650 mm on every EW node is the cathode plate, not the cell. The sized tanks above replace it in `params.sizing.size_mm`. The graph `size_mm` and the placement rows are not changed here; the aisle layout (cell pitch 750 mm) does not hold EW_1, EW_2, EW_7 and EW_9 at 2.3–2.7 m long and was re-placed by `flow_graph/place_ew_aisle.py` (X-RSZ-03; re-run for Rev B, 370-3270 mm long).
2. Bounding DC load at the electrodes is 27.1 kW at 12781 A (Rev B). The graph IA-DC-EW_n edges carry the cell plus 0.3 V bus drop, written by `flow_graph/param/write_graph.py` (AQS-ELEC-004).
3. Element current is 1581 A, 8.1 times lower. The bounding case governs hardware; the element case is the expected operating point at the reference feed.
4. Side-reaction H₂ on EW_1, EW_2, EW_4 and EW_9 (graph H₂ edges) would add Faradaic current not counted here. It is held with the AQS-DUTY-016 H₂/Cl₂ discrepancy (EDGE_RATING_DUTY) and needs an owner rate decision.
5. Materials. The 316L frame in AQS-EW-MOD-001 is a wetted non-electrode metal and is withdrawn under AQS-STD-002 M3; racks are CPVC or PVC-U. Electrode materials for chloride with anodic Cl₂ (316L cathode, PbO₂ anode) were reopened as X-MAT-18 and are now titanium cathodes and mixed-metal-oxide anodes (AQS-STD-002 section 9).

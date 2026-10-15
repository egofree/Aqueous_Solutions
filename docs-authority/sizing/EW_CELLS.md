# EW_1 to EW_9 cell sizing

Document number: AQS-DUTY-051
Revision: A
Date: 2026-10-15
Authority: graph Rev BH; AQS-PLAN-007 MET-EW_n-02. Study. Not a PE stamp. Script `docs-authority/_ew_sizing.py`. Study values in AQS-REG-002 (A-M-036 to A-M-040).

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue. Current, electrodes, tank size, holdup and DC power per cell. | 2026-10-15 |

## 1. Basis

- Harvest: IA-EW-MET-n is a copper-equivalent sheet rate that bounds the element mass (AQS-ASSAY-001 section 4). Bounding current I = m / (M_Cu / 2F × 86 400), current efficiency 1.0 (study; bounding). EW_9 also books IA-EW-SHEET.
- Element current, for comparison: S08 deposits (AQS-ASSAY-001 section 5) with each metal's valence.
- Cathode current density 200 A/m² (AQS-EW-MOD-001, study). Plate immersed 0.60 × 0.42 m, both faces 0.504 m². Cathode pitch 100 mm with an anode between (50 mm cathode to anode). One more anode than cathodes.
- Tank inside: length = cathodes × 100 mm + 2 × 75 mm ends; width plate + 2 × 50 mm; depth 150 mm sump + 420 mm plate + 100 mm cover + 80 mm freeboard. Wall 10 mm. Liquor density 1100 kg/m³ (AQS-DUTY-050).
- Cell voltage 2.5 V (graph EW_1 cell_voltage_V, study).

## 2. Results

| Cell | Metal | Edge kg/d | I bounding, A | I element, A | Cathodes / anodes | j, A/m² | Tank L × W × H, mm | Liquor m³ | Residence, min | DC kW |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EW_1 | Au | 59.87 | 2104 | 0.1 | 21 / 22 | 199 | 2270 × 720 × 760 | 1.055 | 390 | 5.26 |
| EW_2 | Ag | 59.89 | 2105 | 0.3 | 21 / 22 | 199 | 2270 × 720 × 760 | 1.055 | 396 | 5.26 |
| EW_3 | Cu | 22.48 | 790 | 308.7 | 8 / 9 | 196 | 970 × 720 × 760 | 0.446 | 169 | 1.98 |
| EW_4 | Pb | 4.85 | 170 | 7.7 | 2 / 3 | 169 | 370 × 720 × 760 | 0.164 | 63 | 0.43 |
| EW_5 | Sn | 5.02 | 176 | 13.4 | 2 / 3 | 175 | 370 × 720 × 760 | 0.164 | 63 | 0.44 |
| EW_6 | Ni | 5.47 | 192 | 27.1 | 2 / 3 | 191 | 370 × 720 × 760 | 0.164 | 63 | 0.48 |
| EW_7 | Fe | 71.14 | 2500 | 1185.0 | 25 / 26 | 198 | 2670 × 720 × 760 | 1.243 | 478 | 6.25 |
| EW_8 | Cd | 5.05 | 177 | 14.1 | 2 / 3 | 176 | 370 × 720 × 760 | 0.164 | 64 | 0.44 |
| EW_9 | Zn | 75.33 | 2648 | 24.3 | 27 / 28 | 195 | 2870 × 720 × 760 | 1.337 | 523 | 6.62 |
| Total | | | 10864 | 1581 | | | | | | 27.16 |

## 3. Findings

1. The issued envelope 600 × 420 × 650 mm on every EW node is the cathode plate, not the cell. The sized tanks above replace it in `params.sizing.size_mm`. The graph `size_mm` and the placement rows are not changed here; the aisle layout (cell pitch 750 mm) does not hold EW_1, EW_2, EW_7 and EW_9 at 2.3–2.7 m long and is re-placed under unit task 14 / X-BLD.
2. Bounding DC load is 27.2 kW at 10864 A. The graph books 5.263 kW on EW_1 and 4.57 kW on IA-E-RECT; EW_2 to EW_9 book none. X-ELS-02 and X-ELS-04 take the bounding figure.
3. Element current is 1581 A, 6.9 times lower. The bounding case governs hardware; the element case is the expected operating point at the reference feed.
4. Side-reaction H₂ on EW_1, EW_2, EW_4 and EW_9 (graph H₂ edges) would add Faradaic current not counted here. It is held with the AQS-DUTY-016 H₂/Cl₂ discrepancy (EDGE_RATING_DUTY) and needs an owner rate decision.
5. Materials. The 316L frame in AQS-EW-MOD-001 is a wetted non-electrode metal and is withdrawn under AQS-STD-002 M3; racks are CPVC or PVC-U. Electrode materials for chloride with anodic Cl₂ (316L cathode, PbO₂ anode) were reopened as X-MAT-18 and are now titanium cathodes and mixed-metal-oxide anodes (AQS-STD-002 section 9).

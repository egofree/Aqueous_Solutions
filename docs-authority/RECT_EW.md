# EW rectifier sizing (RECT-EW)

Document number: AQS-ELEC-004
Revision: A
Date: 2026-10-15
Authority: graph Rev BH; AQS-PLAN-007 X-ELS-04. Script `docs-authority/_rect_ew_sizing.py`. Study. Not a PE stamp. Study values in AQS-REG-002 (A-M-041 to A-M-044).

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue. One DC channel per cell at the bounding current. | 2026-10-15 |

## 1. Basis

- Current per cell: AQS-DUTY-051 bounding case (copper-equivalent harvest edges, which bound the plateable-metal envelope of AQS-ASSAY-001 Rev C section 4). ELECTRICAL.md section on assays: size at the top of the envelope and turn down for lean feeds.
- One channel per cell, because the nine cells run at different currents (170 to 2650 A) and a series string carries one current.
- Channel rating ≥ 1.10 × bounding current, rounded up to a frame size (250, 500, 1000, 1500, 2000, 2500, 3000, 4000 A; study list).
- Rated voltage 6 V per channel: cell 2.5 V + bus drop 0.3 V, with room for Fe and Zn cells, anode aging and start-up (study).
- Rectifier efficiency 0.80 at this low voltage (study).
- DC bar 200 A/cm² copper (AQS-PWR-001 shop rule), per pole.

## 2. Channels

| Cell | Bounding A | Need, A | Rated A | Rated kW (6 V) | DC kW at 2.8 V | AC kW | Bar per pole, cm² |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EW_1 | 2104 | 2315 | 2500 | 15.0 | 5.89 | 7.36 | 12.50 |
| EW_2 | 2105 | 2315 | 2500 | 15.0 | 5.89 | 7.37 | 12.50 |
| EW_3 | 790 | 869 | 1000 | 6.0 | 2.21 | 2.77 | 5.00 |
| EW_4 | 170 | 188 | 250 | 1.5 | 0.48 | 0.60 | 1.25 |
| EW_5 | 176 | 194 | 250 | 1.5 | 0.49 | 0.62 | 1.25 |
| EW_6 | 192 | 211 | 250 | 1.5 | 0.54 | 0.67 | 1.25 |
| EW_7 | 2500 | 2750 | 3000 | 18.0 | 7.00 | 8.75 | 15.00 |
| EW_8 | 177 | 195 | 250 | 1.5 | 0.50 | 0.62 | 1.25 |
| EW_9 | 2648 | 2912 | 3000 | 18.0 | 7.41 | 9.27 | 15.00 |
| Total | 10864 | | 13000 | 78.0 | 30.42 | 38.02 | |

## 3. Findings

1. RECT-EW is nine channels, 13000 A total, 78 kW nameplate at 6 V. Bounding AC input is 38.0 kW. The ELECTRICAL.md row (0–36 V, 0–250 A, 5–7 kW) and the graph IA-E-RECT 4.57 kW do not cover it. They are not changed here (no rate change approved); X-ELS-02 and X-ELS-05 take the AC figure.
2. Turndown. At the element basis (AQS-DUTY-051) EW_1 and EW_2 need under 1 A against 2500 A channels. A low-range module (0–50 A) on each precious-metal cell is needed for lean feeds (study recommendation; held for X-ELS-03).
3. Side-reaction H₂ current (AQS-DUTY-051 finding 4) is not in these ratings; the 10 % margin does not cover it at the graph H₂ rates.
4. A 36 V output is not needed for one cell per channel; 6 V reduces conversion loss and bar cost. If cells are later grouped in series by equal current, the channel voltage rises with the cell count.

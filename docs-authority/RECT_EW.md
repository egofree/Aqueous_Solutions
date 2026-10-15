# EW rectifier sizing (RECT-EW)

Document number: AQS-ELEC-004
Revision: B
Date: 2026-10-15
Authority: graph Rev BH; AQS-PLAN-007 X-ELS-04. Script `docs-authority/_rect_ew_sizing.py`. Study. Not a PE stamp. Study values in AQS-REG-002 (A-M-041 to A-M-044). Rev B: cell voltage, bus drop and efficiency from `flow_graph/param/drivers.json`; channel function `flow_graph/param/sizing/power.py` (X-PAR-03).

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue. One DC channel per cell at the bounding current. | 2026-10-15 |
| B | X-PAR acid-loop decision: cell 2.12 V, CE 0.85 (USBM chloride EW basis); converted to the parametric library. | 2026-10-15 |

## 1. Basis

- Current per cell: AQS-DUTY-051 bounding case (copper-equivalent harvest edges, which bound the plateable-metal envelope of AQS-ASSAY-001 Rev C section 4). ELECTRICAL.md section on assays: size at the top of the envelope and turn down for lean feeds.
- One channel per cell, because the nine cells run at different currents (201 to 3115 A) and a series string carries one current.
- Channel rating ≥ 1.10 × bounding current, rounded up to a frame size (250, 500, 1000, 1500, 2000, 2500, 3000, 4000 A; study list).
- Rated voltage 6 V per channel: cell 2.12 V (USBM_CL_EW) + bus drop 0.3 V, with room for Fe and Zn cells, anode aging and start-up (study).
- Rectifier efficiency 0.80 at this low voltage (study).
- DC bar 200 A/cm² copper (AQS-PWR-001 shop rule), per pole.

## 2. Channels

| Cell | Bounding A | Need, A | Rated A | Rated kW (6 V) | DC kW at 2.42 V | AC kW | Bar per pole, cm² |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EW_1 | 2476 | 2723 | 3000 | 18.0 | 5.99 | 7.49 | 15.00 |
| EW_2 | 2476 | 2724 | 3000 | 18.0 | 5.99 | 7.49 | 15.00 |
| EW_3 | 930 | 1022 | 1500 | 9.0 | 2.25 | 2.81 | 7.50 |
| EW_4 | 201 | 221 | 250 | 1.5 | 0.49 | 0.61 | 1.25 |
| EW_5 | 208 | 228 | 250 | 1.5 | 0.50 | 0.63 | 1.25 |
| EW_6 | 226 | 249 | 250 | 1.5 | 0.55 | 0.68 | 1.25 |
| EW_7 | 2942 | 3236 | 4000 | 24.0 | 7.12 | 8.90 | 20.00 |
| EW_8 | 209 | 230 | 250 | 1.5 | 0.51 | 0.63 | 1.25 |
| EW_9 | 3115 | 3426 | 4000 | 24.0 | 7.54 | 9.42 | 20.00 |
| Total | 12781 | | 16500 | 99.0 | 30.93 | 38.66 | |

## 3. Findings

1. RECT-EW is nine channels, 16500 A total, 99 kW nameplate at 6 V (Rev A: 13000 A, 78 kW). Bounding AC input is 38.7 kW (Rev A 38.0 kW). The ELECTRICAL.md row (0–36 V, 0–250 A, 5–7 kW) and the graph IA-E-RECT 4.57 kW do not cover it. X-RSZ-02 books it: node RECT_EW (38.66 kW AC), S17-EW feed, IA-DC-EW_n channels, IA-RECT-EW-LOSS 7.73 kW (Rev B values written by `flow_graph/param/write_graph.py`); IA-E-RECT retired.
2. Turndown. At the element basis (AQS-DUTY-051) EW_1 and EW_2 need under 1 A against 2500 A channels. A low-range module (0–50 A) on each precious-metal cell is needed for lean feeds (study recommendation; held for X-ELS-03).
3. Side-reaction H₂ current (AQS-DUTY-051 finding 4) is not in these ratings; the 10 % margin does not cover it at the graph H₂ rates.
4. A 36 V output is not needed for one cell per channel; 6 V reduces conversion loss and bar cost. If cells are later grouped in series by equal current, the channel voltage rises with the cell count.

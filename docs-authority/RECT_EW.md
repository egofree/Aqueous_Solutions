# Electrowinning rectifier sizing (RECT-EW)

Document number: AQS-ELEC-004
Revision: E
Date: 2026-11-04
Authority: graph Rev AD; AQS-PLAN-007 task X-ELS-04. Calculation script `docs-authority/_rect_ew_sizing.py`. Assumed study values are recorded in the assumptions register AQS-REG-002 (A-M-041 to A-M-044). The cell voltage, bus drop and efficiency are read from `flow_graph/param/drivers.json`, and the channel function is `flow_graph/param/sizing/power.py` (task X-PAR-03). Study; this page is not stamped by a Professional Engineer (PE).

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue. One DC channel per cell at the bounding current. | 2026-10-15 |
| B | Acid-loop decision of the X-PAR tasks: cell voltage 2.12 V and current efficiency (CE) 0.85, on the chloride electrowinning basis of the US Bureau of Mines (USBM); converted to the parametric library. | 2026-10-15 |
| C | Purpose and scope added; text rewritten to the documentation style guide (AQS-DOC-002). Section 4 records how the flow graph now represents the rectifier. No rating changed. | 2026-10-25 |
| D | Section 4: the 12 kW graph supply stamp was removed as a double count and the AC input is reconciled; the reject edge re-books at the calculated conversion loss. No rating in Table 2.1 changed. | 2026-11-04 |
| E | Owner ruling Q-038: the cell currents re-derive from the element deposit rows of AQS-ASSAY-001 section 5 at leach recovery 1.0 (AQS-DUTY-051 Rev E, A-M-460), so every channel rating, the nameplate, the AC input and the conversion loss re-solve; the copper-equivalent bounding reading retires. | 2026-11-04 |

## Purpose and scope

Each electrowinning (EW) cell plates metal from solution using direct current (DC). The rectifier converts the alternating-current (AC) supply into DC for the nine cells EW_1 to EW_9. This page sizes the DC channel for each cell: its current rating, its voltage, its DC and AC power, and the cross-section of its copper busbar. The script `docs-authority/_rect_ew_sizing.py` reproduces Table 2.1.

## 1. Basis

- The current for each cell is the design case of AQS-DUTY-051 Rev E: the element deposit row of AQS-ASSAY-001 section 5 for that cell, at leach recovery 1.0 (section 4) and current efficiency 0.85. This is the supply basis - the dissolved metal values of the design feed - which the owner ruling Q-038 (A-M-460) made the governing rate. A leaner characterized lot turns the current down; a richer one is a resize trigger (AQS-ASSAY-001 section 4).
- Each cell has its own channel. The nine cells run at different currents, from 0.1 A to 1394 A, and cells in a series string would all carry the same current.
- Each channel is rated at no less than 1.10 times its design current, rounded up to a frame size. The study list of frame sizes is 250, 500, 1000, 1500, 2000, 2500, 3000 and 4000 A.
- Each channel is rated at 6 V. This covers the cell voltage of 2.12 V (USBM_CL_EW) and the bus drop of 0.3 V, and leaves room for anode ageing and for start-up (study value).
- The rectifier efficiency is taken as 0.80 at this low voltage (study value).
- The DC busbar is sized at 200 A/cm² of copper for each pole (shop rule of AQS-PWR-001).

## 2. Channels

Table 2.1 gives the rating of each channel. The DC power is calculated at 2.42 V, the cell voltage plus the bus drop.

Table 2.1. Rectifier channels

| Cell | Design A | Need, A | Rated A | Rated kW (6 V) | DC kW at 2.42 V | AC kW | Bar per pole, cm² |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EW_1 | 0.1 | 0.1 | 250 | 1.5 | 0.000 | 0.000 | 1.25 |
| EW_2 | 0.3 | 0.3 | 250 | 1.5 | 0.001 | 0.001 | 1.25 |
| EW_3 | 363 | 400 | 500 | 3.0 | 0.88 | 1.10 | 2.50 |
| EW_4 | 9 | 10 | 250 | 1.5 | 0.02 | 0.03 | 1.25 |
| EW_5 | 16 | 17 | 250 | 1.5 | 0.04 | 0.05 | 1.25 |
| EW_6 | 32 | 35 | 250 | 1.5 | 0.08 | 0.10 | 1.25 |
| EW_7 | 1394 | 1534 | 2000 | 12.0 | 3.37 | 4.22 | 10.00 |
| EW_8 | 17 | 18 | 250 | 1.5 | 0.04 | 0.05 | 1.25 |
| EW_9 | 29 | 31 | 250 | 1.5 | 0.07 | 0.09 | 1.25 |
| Total | 1859.5 | | 4250 | 25.5 | 4.50 | 5.63 | |

## 3. Findings

1. The rectifier has nine channels with a total rating of 4250 A and a nameplate rating of 25.5 kW at 6 V. The AC input at the design duty is 5.63 kW and the conversion loss 1.13 kW. The demand-side book is `params.rect_ac_input_kW` on the graph node RECTIFIER (A-M-255), counted once in the demand rollup.
2. Turndown is needed. Cells EW_1, EW_2 and EW_4 to EW_9 run below 40 A against 250 A channels; each of these cells needs a low-range module (0 to 50 A) so the channel operates in its efficient band. This is a study recommendation, held for task X-ELS-03.
3. The current that goes to the hydrogen side reaction (AQS-DUTY-051 finding 4) is not included in these ratings. At the hydrogen rates of the graph, the 10 % margin does not cover it.
4. With one cell per channel, a 36 V output is not needed; 6 V reduces the conversion loss and the busbar cost. If cells of equal current are later connected in series, the channel voltage rises with the number of cells.

## 4. Representation in the flow graph at this revision

The graph's rectifier is the node RECTIFIER. The former 12 kW supply stamp (S17 from SOL_ARK_60K, "48 V rails at the node basis") was removed as a double count at revision D: its cited basis, "DC to cells and induction" in POWER_DUTIES.md, is booked once as the bounding AC row (`params.rect_ac_input_kW`, A-M-255), which reconciles the 5.63 kW AC input of Table 2.1 with the graph. The conversion loss is stream IA-RECT-Q4 at the calculated rectifier loss (`params.rect_loss_kW`, 1.125 kW at the design duty) to Q4_BUS. The channel streams IA-DC-EW_1 to IA-DC-EW_9 remain and carry the DC values of Table 2.1 (for example 3.37 kW to EW_7).

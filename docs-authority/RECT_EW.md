# Electrowinning rectifier sizing (RECT-EW)

Document number: AQS-ELEC-004
Revision: C
Date: 2026-10-25
Authority: graph Rev BH; AQS-PLAN-007 task X-ELS-04. Calculation script `docs-authority/_rect_ew_sizing.py`. Assumed study values are recorded in the assumptions register AQS-REG-002 (A-M-041 to A-M-044). The cell voltage, bus drop and efficiency are read from `flow_graph/param/drivers.json`, and the channel function is `flow_graph/param/sizing/power.py` (task X-PAR-03). Study; this page is not stamped by a Professional Engineer (PE).

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue. One DC channel per cell at the bounding current. | 2026-10-15 |
| B | Acid-loop decision of the X-PAR tasks: cell voltage 2.12 V and current efficiency (CE) 0.85, on the chloride electrowinning basis of the US Bureau of Mines (USBM); converted to the parametric library. | 2026-10-15 |
| C | Purpose and scope added; text rewritten to the documentation style guide (AQS-DOC-002). Section 4 records how the flow graph now represents the rectifier. No rating changed. | 2026-10-25 |

## Purpose and scope

Each electrowinning (EW) cell plates metal from solution using direct current (DC). The rectifier RECT-EW converts the alternating-current (AC) supply into DC for the nine cells EW_1 to EW_9. This page sizes the DC channel for each cell: its current rating, its voltage, its DC and AC power, and the cross-section of its copper busbar. The script `docs-authority/_rect_ew_sizing.py` reproduces Table 2.1.

## 1. Basis

- The current for each cell is the bounding case of AQS-DUTY-051. That case uses the copper-equivalent harvest edges, which bound the range of plateable metal in AQS-ASSAY-001 Rev C section 4. The assay section of ELECTRICAL.md sets the rule: size at the top of the range and turn the current down for lean feeds.
- Each cell has its own channel. The nine cells run at different currents, from 201 A to 3115 A, and cells in a series string would all carry the same current.
- Each channel is rated at no less than 1.10 times its bounding current, rounded up to a frame size. The study list of frame sizes is 250, 500, 1000, 1500, 2000, 2500, 3000 and 4000 A.
- Each channel is rated at 6 V. This covers the cell voltage of 2.12 V (USBM_CL_EW) and the bus drop of 0.3 V, and leaves room for the iron and zinc cells, for anode ageing and for start-up (study value).
- The rectifier efficiency is taken as 0.80 at this low voltage (study value).
- The DC busbar is sized at 200 A/cm² of copper for each pole (shop rule of AQS-PWR-001).

## 2. Channels

Table 2.1 gives the rating of each channel. The DC power is calculated at 2.42 V, the cell voltage plus the bus drop.

Table 2.1. Rectifier channels

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

1. RECT-EW has nine channels with a total rating of 16500 A and a nameplate rating of 99 kW at 6 V; at revision A the totals were 13000 A and 78 kW. The bounding AC input is 38.7 kW (38.0 kW at revision A). This is not covered by the rectifier row of ELECTRICAL.md (0 to 36 V, 0 to 250 A, 5 to 7 kW) or by the 4.57 kW of the former graph stream IA-E-RECT. Task X-RSZ-02 entered it in the graph at revision B: node RECT_EW (38.66 kW AC), the feed S17-EW, the channel streams IA-DC-EW_n and the loss stream IA-RECT-EW-LOSS (7.73 kW), all written by `flow_graph/param/write_graph.py`. IA-E-RECT was retired.
2. Turndown is needed. On the element basis of AQS-DUTY-051, cells EW_1 and EW_2 need less than 1 A against channels of 2500 A. Each precious-metal cell therefore needs a low-range module (0 to 50 A) for lean feeds. This is a study recommendation, held for task X-ELS-03.
3. The current that goes to the hydrogen side reaction (AQS-DUTY-051 finding 4) is not included in these ratings. At the hydrogen rates of the graph, the 10 % margin does not cover it.
4. With one cell per channel, a 36 V output is not needed; 6 V reduces the conversion loss and the busbar cost. If cells of equal current are later connected in series, the channel voltage rises with the number of cells.

## 4. Representation in the flow graph at this revision

The graph no longer has the node RECT_EW or the streams S17-EW and IA-RECT-EW-LOSS named in finding 1. The rectifier is the node RECTIFIER. Its supply is stream S17 from SOL_ARK_60K at 12.0 kW (48 V rails at the node basis, assumption A-M-231), and its heat loss is stream IA-RECT-Q4 at 1.0 kW to Q4_BUS. The channel streams IA-DC-EW_1 to IA-DC-EW_9 remain and carry the DC values of Table 2.1 (for example 7.538 kW to EW_9). The 38.66 kW AC input of Table 2.1 and the 12.0 kW supply in the graph have not been reconciled.

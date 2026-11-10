# Electrowinning deposits computed from the feed assay

Date: 2026-11-10. Task: X-QA-04 (AQS-PLAN-007). Closes the review item of
`2026-11-04-review-work-items.md`.

## Decision

The booked electrowinning deposit of each cell is computed from the feed assay:
the IA-FEED-01 rate times the AQS-ASSAY-001 reference-point element fraction
(graph `params.assay_envelope.reference_point_elements`) times the leach recovery
(A-M-467, 1.0). The lumped `other_plateable` class splits evenly over the five
minor plateable metals (new assumption A-M-470). The computation lives in
`flow_graph/param/solver.py ew_products()`; the driver
`DIGESTER.ew-cascade-train.ew_s08_deposits_kg_d` is removed from `drivers.json`
as a derived value. `flow_graph/param/test_ew_deposit_basis.py` drops its
expected-failure marker and asserts the booked rows stay within the plateable
class of the reference feed.

## Reason

The deposit rows carried the S08 booking of the retired 150 kg/d feed audit
(AQS-AUD-001 section 4.1): 41.9996 kg/d element against a design feed of
102.68 kg/d whose plateable class is 0.35025, or 35.9637 kg/d. The booking
exceeded the metal the design feed can supply.

## New booked rows (kg/d, recovery 1.0)

| Cell | Metal | Was (audit) | Now (reference feed) |
| --- | --- | --- | --- |
| EW_1 | Au | 0.0063 | 0.005134 |
| EW_2 | Ag | 0.0251 | 0.020536 |
| EW_3 | Cu | 8.7841 | 7.1876 |
| EW_4, 5, 6, 8, 9 | Pb/Sn/Ni/Cd/Zn | 0.7111 each | 0.61608 each |
| EW_7 | Fe | 29.629 | 25.67 |
| Total | | 41.9996 | 35.96367 |

The forming chain re-solves from the new rows: S57 wire billet 3.5938,
S58 wire 3.2247, S59 mill sheet 3.5938, S60 powder 2.7724, IA-EW-SHEET 9.96
(all kg/d). No equipment figure moved: cell currents, cathode counts, tanks and
the rectifier still rate at the AQS-ASSAY-001 element envelope (AQS-DUTY-051
Rev F basis), which this change does not touch.

## Carried facts

- The S08 edge rate stays held at 41.996408 kg/d (AQS-PAR-003 reconciliation),
  so the entrained-silicate residual on it grows from 0.0021 to 6.0327 kg/d.
  AQS-ASSAY-001 Rev I states this; whether the held rate follows the deposits
  belongs to the shop-export re-derivation (X-QA-12).
- The frozen EW cell transit notes inside the graph (the "AQS-DUTY-010: EW_n in
  ... - <metal> deposit ..." lines, stamped X-PAR-02 reconciled) and the frozen
  study `EDGE_RATING_DUTY.md` still print the audit-basis deposits at their
  pinned precision. No stage owns those notes; they are reconciliation records
  of their own pass. Their withdrawal belongs to the note-hygiene and
  superseded-figure tasks (X-QA-15, X-QA-16), as does CHECKS.md AQS-DUTY-080
  and EW_MODULE.md.

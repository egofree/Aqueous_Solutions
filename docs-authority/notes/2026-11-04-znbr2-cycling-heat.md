# 2026-11-04 ZNBR2 electrolyte cycling heat ledgered and the dry cooler resized from the calculated duty (physics-audit F-4)

The ZNBR2 electrolyte heat edge (IA-ZNBR-HEAT, ZNBR2 to Q4_BUS, thermal) booked a stale 1.67 kW
Rev-N seed from a 120 kWh-class store, while the power chain books a 3596 kWh/d store cycled at
round trip 0.70 (A-M-062/179, vendor-flagged until the X-MFG-41 stack test). The round-trip
difference is heat generated in the electrolyte and none of it was ledgered: the Q4 bus and the
dry cooler never saw it. Fixed at the writer (`flow_graph/param/write_graph.py heat()`): the edge
is re-derived every pass from the store book `docs-authority/_power_sizing.py` reports, so it
tracks the power chain instead of a hand value. A-M-455 records the basis; A-M-244 is restated
(the cooler rating is now calculated from the terminal book, not the fixed 12 kW class).

## Numbers (before -> after, converged graph)

| Quantity | Before | After | Why |
| --- | --- | --- | --- |
| IA-ZNBR-HEAT (24 h average thermal) | 1.67 kW | 68.84 kW | loss 1652 kWh/d = 5507 in - 3855 out at RT 0.70; the store is larger than at audit time (3855 vs 3056 kWh/d) because the demand grew, and the writer now derives the edge from the live book |
| Charge-window thermal rate (sizing case) | - | 165.2 kW over the 10 h window | bounding case: all the daily loss lands in the charge window; sizes the electrolyte cooling loop |
| Charge electrical rate over the same window | - | 550.7 kW | stated as the cycling dynamic; it is not a heat rate |
| HL-Q4-REJ (bus to dry cooler) | 0.7384 kW | 67.90 kW | bus rejection by difference with the cycling heat counted |
| IA-DC-REJ (terminal to ambient) | 7.9884 kW | 75.15 kW | terminal closure: the cooler passes every kW it receives |
| DRY_COOLER rating | fixed 12 kW class | 215 kW calculated | ceil(1.25 x bounding duty 171.5 kW = terminal book 75.2 with the cycling heat at its window rate); AQS-DUTY-008 section 3 margin; design bulb 37.8 C and LMTD 15 K unchanged (A-M-244 restated) |
| DRY_COOLER fan | 0.15 kW | 10.75 kW | 0.05 kW_fan/kW_th class on the calculated rating; airside re-derived at the same 13 K rise class |
| Bounding demand P | 256.85 kW | 275.34 kW | fan electrical stamp + the re-solved extension chain |
| PV nameplate / storage | 3561 kWp / 3596 kWh | 3818 kWp / 3855 kWh | demand-driven re-solve through roof_close / power(); the larger store raises the cycling heat, the loop converges (marginal gain 0.064 fan-kW per demand-kW) |

## Route (no new unit)

The route existed: ZNBR2 -> IA-ZNBR-HEAT (thermal) -> Q4_BUS -> HL-Q4-REJ -> DRY_COOLER ->
IA-DC-REJ -> ATMOS (the Group A rejection path). No proposed unit needed.

## Duty basis

ZNBR2 duty sheet section 2 re-renders from `params.cycling_thermal` every pass
(`docs-authority/_duty_basis.py`), like the HVAC blocks: store, cycling loss, average and
charge-window rates, and the electrical rating, all generator-owned.

## Changed files

- `flow_graph/param/write_graph.py`: heat() F-4 block derives IA-ZNBR-HEAT and
  `ZNBR2.params.cycling_thermal` from the `_power_sizing` store book; the DRY_COOLER rating
  (rated_kW, fan_kW, basis) is calculated in the same lane and the stale "rated 12 kW" clause on
  the HL-Q4-REJ base note is restated.
- `flow_graph/param/specialty_sizing.py`: the DRY_COOLER fan electrical stamp and airside design
  read the calculated rating (write_graph heat runs earlier in the regen stage order).
- `docs-authority/_duty_basis.py`: ZNBR2 duty section 2 re-render from cycling_thermal.
- `docs-authority/assumptions_manual.json`: A-M-455 new; A-M-244 restated; ASSUMPTIONS_REGISTER.md
  regenerated.
- `flow_graph/plant_flow_graph.json` and the regenerated documents.

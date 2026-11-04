# 2026-11-03 Q4 heat ledger closed and the ladder A/B convention stated (physics-audit F-3/F-25)

The Q4 heat book had two defects. First, the MVR evaporator compressor and pump heat edges
(SQ-EVAP_ACID, SQ-EVAP_BASE, SQ-EVAP_ACID_VS, 2.85 kW total) sat on the mixed `energy` layer,
so the X-THM-01 re-solve never counted them: the bus showed a fictitious 2.11 kW deficit that
the ground-source heat pump "lifted", while an audit ledger reading every kW edge (the physics
audit's 23.67 in vs 20.81 out) saw the real picture - a bus with heat nobody rejected. Second,
the A/B ladder convention was undefined: both store-bus links book 3.896 kW and their notes
called each a single-ladder x 1.25 rating, which made the bus ledger read as a double-counted
rating. Fixed at the writer (`flow_graph/param/write_graph.py`), then regenerated. A-M-453 and
A-M-454 record the two bases.

## Q4 bus ledger (thermal kW, design day)

| Quantity | Before | After | Why |
| --- | --- | --- | --- |
| SQ-EVAP_ACID / BASE / ACID_VS layers | energy | thermal | compressor/pump work leaves as heat (A-M-086), same grade as the PEM stack heat edge; the re-solve counts it |
| GEO_HP lift S44 | 2.1114 kW | 0.0 kW (idle on the design day) | the deficit was fictitious: the bus sources cover the branches once the evaporator heat is counted |
| HL-Q4-REJ (bus to dry cooler) | 0.0 kW | 0.7384 kW | live rejection by difference; the ledger closes on the real surplus |
| IA-DC-REJ (dry cooler to ATMOS) | (absent) | 7.9884 kW | new terminal closure edge: the cooler passes every kW it receives (ADS recool 7.25 + bus 0.7384) to ambient air |

DRY_COOLER now closes on the thermal ledger like the stores; the writer's ledger check covers it.

## Ladder A/B convention (A-M-453)

The two ladders are a full-capacity N+1 pair (HEAT_LADDER.md section 3): either carries the plant
alone while the other is isolated. The graph edge rate books the design-day normal state - both
ladders on line at their per-ladder share (HX-8 50/50 split + store trim) - and the Q4_BUS ledger
sums those normal flows only. The single-ladder case (one ladder isolated, all source heat on the
other, x 1.25 per AQS-DUTY-008 section 3) sizes the link hardware and the terminal upset; it is a
rating case, not a simultaneous flow. No rate moved; the reading is now stated on the edges, in
HEAT_LADDER.md section 3 (Rev B), and in BALANCE_CLOSE.md (Rev B, the stale "surplus 10.09 kW
goes to a dry cooler" row restated).

## DRY_COOLER rating note

The 12 kW class (A-M-244) predates the live rejection book. With the ZNBR2 electrolyte
thermal-management reject landing on the terminal (physics audit F-4, next change), the class is
resized from the calculated bounding duty in the same lane; this change only makes the terminal
close.

## Changed files

- `flow_graph/param/write_graph.py`: SQ-EVAP edges thermal layer (process, and layers join the
  update set of existing edges); heat() ledger scan reads the graph instead of a fixed stream
  list, restates the N+1 store-link convention on the notes (+ params duty_normal_kw), and writes
  the IA-DC-REJ terminal closure edge; ledger check covers DRY_COOLER.
- `flow_graph/plant_flow_graph.json`: regenerated (layers, S44, HL-Q4-REJ, IA-DC-REJ, store-link
  params; downstream demand/PV/storage re-solve: GEO_HP idle on the design day).
- `docs-authority/HEAT_LADDER.md` Rev B, `docs-authority/BALANCE_CLOSE.md` Rev B.
- `docs-authority/assumptions_manual.json`: A-M-453, A-M-454; ASSUMPTIONS_REGISTER.md regenerated.

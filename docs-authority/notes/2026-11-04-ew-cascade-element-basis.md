# 2026-11-04 electrowinning cascade re-based on the feedstock assay (Q-038 owner ruling)

The change applies the default recorded for Q-038 (OPEN_QUESTIONS.md, AQS-OQ-001 Rev F; the question is not yet recorded as closed): the electrowinning cascade rate
follows the supply - the feedstock metal values times recovery - and the demand - the products
the plant actually makes and consumes; the wear-goods value that closed the goods balance by difference is withdrawn. This change set
carries the ruling through the graph, the duties, the power chain and the goods balance. The
register entry is docs-authority/OPEN_QUESTIONS.md Q-038; the assumption entry is A-M-460
(restating A-M-265).

## What governs, and the numbers

Supply basis (governing): the S08 deposit rows of AQS-ASSAY-001 section 5 at leach recovery 1.0
(section 4) - 42.0 kg/d of element metal at the 102.68 kg/d design feed. Per-cell design current
I = m z F / (M t CE) at current efficiency 0.85 and cell voltage 2.12 V plus a 0.3 V bus drop:

- total 1,859.5 A; 3.94 kW DC at the electrodes (2.12 V), 4.50 kW DC including the 0.3 V bus
  drop, and 5.63 kW AC at rectifier efficiency 0.80
  (was 12,782 A bounding and 38.66 kW AC on the retired copper-equivalent book of 309.1 kg/d);
- the rectifier re-solves to a 4,250 A, 25.5 kW DC nameplate (was 16,500 A, 99 kW).

Demand basis (computed, not governing): the plated metal the plant consumes is the forming routes -
half the Cu deposit to wire, half to mill, the Pb/Sn/Ni/Cd/Zn blend to powder (the AQS-DUTY-010
bases the graph already stated on S57/S59/S60) - plus the crew goods issue (the A-M-429 roster
textile line, 0.0877 kg/d). That demand is a fraction of the supply, so the supply governs the
cascade rate and the surplus metal leaves through the shop finished-goods export (self-sustaining
plant rule). AQS-DUTY-051 section 2 states the governing basis.

## Product booking (element rates, no copper-equivalent convention)

- IA-EW-MET-1/2/7 carry the Au, Ag and Fe deposit masses (0.0063, 0.0251, 29.629 kg/d); the Cu and
  blend cells book 0 and their harvest rides IA-EW-SHEET (11.9841 kg/d) at the EW_9 collection
  point, which re-enters the ledger through the melt and forming products.
- The forming chain re-derives from the deposits: S57 4.3921 (wire billet), S58 3.9410 (wire),
  S59 4.3921 (mill sheet), S60 3.1999 (powder), IA-WIRE-LOSS 0.4379, IA-DRAW-FUME 0.0132 (the
  AQS-DUTY-010 melt-fume basis; it was booking 2.46 kg/d as the aisle's phantom make-up).
  IA-MELT-ATOM, IA-ATOM-REMELT and IA-MELT-MILL stay owned by ess_tf and follow S60 and the melt
  book. IA-BAG-01 closes as mill loss + fab loss + draw swarf (7.7679).
- The aisle air balance closes on a stated make-up stream: IA-MET-AIR-MU 2.4468 kg/d of plant air at MET_AHU replaces
  the scrub blowdown the draw-fume edge used to carry; IA-MET-AIR-RET closes as S62 + S71 + fume
  less blowdown; the N2 header re-vents the draw (IA-N2-VENT 20.064 -> 17.618).

## Wear-goods value withdrawn, goods balance restated

- IA-WEAR books the roster line 0.0877 kg/d (the A-M-429 finished-textile issue worn out at steady
  state). IA-MFG-OUT retires at 0: the crew goods issue is the TEXTILE_HAB line. The 596.86 kg/d
  closing-by-difference pair (149 kg/person/d, A-M-265) is gone.
- The shop closes on the finished-goods dock export IA-GOODS-SHIP, 331.8541 kg/d (balance.physics
  R10c closure; write_graph seeds the derived value so the foundry stage sees the closed shop).
  The plant surplus statement is now a net export of metal, chlorine and finished goods.
- The scrap yard closes on the design feed: IA-HOP-01 retires at 0 and NORTH_DOCK make-up feedstock
  IA-FEED-MU 65.5473 kg/d closes the hopper behind the retired scrap loop (the leach feed stays the
  AQS-ASSAY-001 section 3 design feed, so the deposit basis is untouched).

## Propagation

- Plant demand 242.76 -> 186.01 kW; PV nameplate 3,366 -> 2,585 kWp (count 6,732 -> 5,170);
  ZNBR2 store 3,399 -> 2,610 kWh; DRY_COOLER rejection 10.00 -> 7.55 kW; the electrolyser grows
  19.97 -> 24.26 kW because the EW cathode-H2 credit to the H2 pool shrinks. IA-METAL-SHIP is
  unchanged at 10.8125 kg/d (foundry pot metal; the EW surplus rides IA-GOODS-SHIP).
- Leach water make-up 52.66 -> 331.35 kg/d: the retired scrap loop took 531 kg/d of phantom mass
  out of the leach and the smaller Faraday gas draw 456 -> 56 kg/d, while the cascade transit stays
  at the AQS-DUTY-008 pump rating, so the leach makes the difference up as dock water.
- Duties, sizing sheets, LOAD_LIST, ONE_LINE, PLANT_BOM, the stream register, views, CAD model
  parameters and the registers regenerate with the model. AQS-DUTY-051 moves to Rev E;
  AQS-ASSAY-001 moves to Rev G; the open-question register moves to Rev G.
- The EW manufacturing models keep their old-built geometry, so the tracker board carries the nine
  sized-envelope misfits (models/mfg/tracker.py --check, section 5 discipline: reported, nothing is
  resized); the X-MFG lane rebuilds the nine cell builders on the new tank sizes.

## Files

flow_graph/param/solver.py (ew at the element deposits, ew_products routing), flow_graph/param/
write_graph.py (element-rate product edges, wear retirement, dock make-up, goods export, aisle
make-up), flow_graph/param/balance.py (shop closes on IA-GOODS-SHIP; scrap yard closes at zero),
flow_graph/param/drivers.json (wire_melt_fume_frac), flow_graph/param/foundry_poly.py (surplus
statement), docs-authority/_ew_sizing.py (Rev E element basis), docs-authority/_power_sizing.py
(reference-case row reads the element total), docs-authority/_foundry_sizing.py (EW_9 statement
re-based), docs-authority/assumptions_manual.json (A-M-460, A-M-265 restated), docs-authority/
OPEN_QUESTIONS.md (Rev G), docs-authority/FEED_ASSAY.md (Rev G), flow_graph/plant_flow_graph.json
and every generated file that regenerates from it.

## Corrections (2026-11-04 review)

- Commit b1f7d718 states that OPEN_QUESTIONS Rev G closes Q-038. The open-question register
  is at Rev F and Q-038 is not marked closed. The question stays open until the owner's
  decision is recorded there.
- The same commit message gives 4.50 kW as DC at the electrodes. 4.50 kW includes the 0.3 V
  bus drop; the electrode load is 3.94 kW (AQS-DUTY-051 section 2 total).
- The S08 deposit rows used as the rate basis are the cathode deposits booked on S08, whose
  edge note cites a 150 kg/d wet-feed audit (AQS-AUD-001 section 4.1). They are not computed
  from the IA-FEED-01 assay at the 102.68 kg/d design feed: the reference-point element
  fractions give Fe 25.67, Cu 7.19, Au 0.0051 and Ag 0.0205 kg/d, and other plateable metals
  3.08 kg/d in total, against the deposit rows of 29.63, 8.78, 0.0063, 0.0251 and 3.56 kg/d.
  The five equal rows of 0.7111 kg/d (Pb, Sn, Ni, Cd, Zn) divide one lumped value equally.
  The work item that re-derives the deposits from the assay is in the task plan (X-QA group).

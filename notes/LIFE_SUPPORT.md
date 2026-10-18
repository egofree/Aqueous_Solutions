# Farm, nutrient, habitation, water — item 7

Document number: AQS-DES-LIFE  
Revision: A  
Date: 2026-10-17  
Authority: graph Rev Y. Not a PE stamp.  
Rates are design assumptions. Not a measured occupancy.

## Nutrient recipe (NUTRIENT_DOSE)

Fed from plant recovery, not external fertilizer.

| Nutrient | Source | Rate (assumption) |
|----------|--------|-------------------|
| N (nitrate / ammonium) | BLACK_DIGEST + nitrifying loop on GROW_BED | 0.05 kg/d N |
| P | Post-EW / AEM phosphate cut | 0.01 kg/d P |
| K | K split after AEM | 0.02 kg/d K |
| Ca, Mg | P_CA and Mg loop, diluted | trace |
| Micronutrients | Polish-bank chelates | trace |

GROW_BED and TERRACE_IRRIG are both sector FARM. Terrace takes the same nutrient solution.

## Gas and water edges (duties)

| Stream | From | To | Rate (assumption) |
|--------|------|----|-------------------|
| CO₂ enrichment | HDR_CO2 / CRYO_CO2 | GROW_BED | 1 kg/d |
| O₂ from farm | GROW_BED | HABITATION | 0.8 kg/d |
| CO₂ from habitation | HABITATION | HDR_CO2 | 1 kg/d |
| N₂ makeup | HDR_N2 / CRYO_N2 | HABITATION | as required for pressure |
| Condensate | farm / HVAC | WTR (CATCH_TANK or grey) | 5 L/d |
| Irrigation | WTR / REMIN | GROW_BED and TERRACE_IRRIG | 20 L/d recycle |
| Grey water | HABITATION | GREY_TREAT | 30 L/d |
| Black water | HABITATION | BLACK_DIGEST | 5 L/d |
| UPW | BMED_UPW_POLISH → HDR_UPW | FAB_UPW_TANK | 50 L/d (item 6) |
| Q4 heat | Q4_BUS | HABITATION / farm | existing ladder |

## Habitation load

| Item | Assumption |
|------|------------|
| Occupancy | 2 persons (pilot) |
| O₂ demand | ~0.8 kg/d |
| Food | from GROW_BED; mass not closed here |
| Heat | Q4 |
| Waste | grey to GREY_TREAT; black to BLACK_DIGEST |

Volatile-solids split on BLACK_DIGEST remains the missing measurement (plan 1.2). No composition invented.

## Graph

Edges for these streams are design duties. Mass edges that already exist are unchanged. New edges are added only where both ends exist and the stream was missing.

Stamped against graph Rev AC (closure pass, notes/CLOSURE_PASS.md).

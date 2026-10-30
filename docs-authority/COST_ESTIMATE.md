# Cost estimate method

Document number: AQS-PRO-003  
Revision: A  
Date: 2026-10-29  
Authority: AQS-PLAN-007 X-PRO-03; owner decision on open question Q-012 (2026-10-29). Study; not a quotation or a PE stamp.

| Rev | Description | Date |
|---|---|---|
| A | First issue: the price basis decided by the owner (Q-012, option b) | 2026-10-29 |

## 1. Purpose and scope

This page fixes how the plant cost estimate is built, so that every price has a stated source and no price is invented. The owner chose the **material-mass basis**: each fabricated line is priced as its material mass times a published commodity price times a fabrication factor. The estimate lands as a priced bill of materials when the unit masses exist; until then this page is the method, not the estimate.

The rules that shaped it: supplier quotations are not a design basis (AQS-GOV rules), and every value carries a published reference (AQS-PAR-001).

## 2. Method

1. **Fabricated parts.** For every BOM line with a mass and a material:
   `cost = mass x P(material) x F(class) x E`, where
   - `P(material)` is the published commodity price of the material class: metals from the USGS Mineral Commodity Summaries, monitored against the London Metal Exchange cash settlement (refs `USGS_MCS_2025`, `LME_CASH`);
   - `F(class)` is the fabrication factor of the part class (plate and weld, machined, cast, bought-machined), taken from published factored-estimating practice (ref `TOWLER_SINNOTT`) and registered as assumptions with their basis;
   - `E` escalates the commodity price date to the estimate year with the CEPCI (ref `CEPCI`).
2. **Bought standard parts** (motors, instruments, standard valves and fasteners of the AQS-INV-004 inventory): priced from published price indices for the component class at the estimate year, with the source named per line. The per-item basis is registered as the lines are priced.
3. **Every line records its source.** The priced BOM carries, per line: mass, price, factor, escalation and the reference. A line without a source is held, not estimated.

## 3. Dependencies and status

- **Unit masses are pending.** The mass column of the plant BOM fills at unit tasks 02 and 10 (sizing and CAD models with BOMs). The estimate computes as the masses land.
- The `models/units/` envelope BOMs are quantity stubs and carry no masses; their lines are priced when the unit's CAD BOM replaces them.
- The escalation date and the commodity price date are recorded in the estimate when it is first computed, so the basis is reproducible.

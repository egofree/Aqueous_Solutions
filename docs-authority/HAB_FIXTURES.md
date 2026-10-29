# Habitation fixtures

Document number: AQS-HAB-001  
Revision: C  
Date: 2026-10-29

| Rev | Description | Date |
|---|---|---|
| B | Fixture sizes, grey water line and composting toilet | 2026-10-12 |
| C | Rewritten to the style guide and to the plant graph: the composting toilet is replaced by the blackwater train, and edges that are no longer in the graph are removed | 2026-10-29 |

## 1. Purpose and scope

This page sizes the water fixtures of the habitation unit `HABITATION`: the shower, the sink and the toilet, and the lines that leave them. It does not cover drinking water treatment, which is in AQS-EQP-HAB-001 (`HAB_WATER.md`), or the treatment of blackwater, which is in AQS-DUTY-063 (`sizing/SANITATION.md`). Every value here is a study value. Nothing on this page is stamped by a licensed engineer.

## 2. Basis

The habitation has four rooms: sleeping, galley, medical and wash. The crew size is `crew_study` on the `HABITATION` node of the plant graph. The room areas of revision B (sleeping 16 m², galley 12 m², medical 6 m², wash 6 m²) have no registered basis and are kept as study values until the habitation layout in AQS-LIFE-001 (`LIFE_FITOUT_PLAN.md`) sets them.

Water leaves the habitation by two routes in the graph. Grey water from the shower, sink and galley goes to `GREY_TREAT` on stream S12. Blackwater from the toilet goes to the blackwater train `BLACK_DIGEST` on stream HAB_BLACK. Low-grade heat for the rooms arrives from `Q4_BUS` on stream IA-Q4-LIFE. The stream register AQS-STR-001 (`STREAM_REGISTER.md`) gives the rates.

## 3. Fixture and line sizes

The pipe size of a fixture is set by its peak flow, not by the daily mass, because a shower runs for minutes at a time.

- The shower flow is 6 L/min. In a DN15 line with a 15.8 mm bore this is a velocity of about 0.5 m/s, which is within the usual range for domestic water lines. The shower line is DN15.
- The sink line is DN15, the same as the shower.
- The grey water drain on S12 is DN25. The daily flow on S12 is small for that size, but the drain must carry the slug of water from a shower without backing up.
- Toilet waste does not enter the grey water drain. It goes to `BLACK_DIGEST`, and its line size is set in AQS-DUTY-063.

## 4. Materials

Grey water lines are polymer drain, waste and vent (DWV) pipe. Fixture valves are brass or 316L stainless steel. No carbon steel is used in contact with wash water.

## 5. Instruments and relief

No fixture instrument trips the plant. The fixtures are open to atmosphere, so they need no relief valve.

## 6. Code basis

No plumbing code is registered in the code basis (AQS-STD-007, `CODE_BASIS.md`). The fixture and drain sizes on this page stay study values until a plumbing code edition is added there and the sizes are checked against it.

# Enclosed greenhouse envelope

Document number: AQS-TRR-GH-001  
Revision: C  
Date: 2026-10-25  
Authority: AQS-TRR-001 (climate decision rule), AQS-SCALE-001 (terrace massing), AQS-EQP-FRM-001, and the TERRACE_* and OVERFLOW_* parameters in `models/freecad/params.py`.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Schedule of the optional greenhouse solids; no FreeCAD model at this revision | 2026-10-01 |
| B | — | FreeCAD envelopes GH_ENV_*, GH_AHU, GH_IRRIG_HDR and GH_DOOR_AIRLOCK added | 2026-10-01 |
| C | — | Purpose and scope added; text rewritten to the documentation style guide (AQS-DOC-002). Section 3 records that streams S40 and S42 are not in the plant flow graph. | 2026-10-25 |

The design is licensed under CERN-OHL-S-2.0.

## 1. Purpose and scope

The plant has planted terraces on the band of ground that faces the equator. At some sites the climate makes open beds impractical, and the terrace is then enclosed as a greenhouse. Section 3.1 of the terrace document AQS-TRR-001 sets the rule for choosing an enclosed greenhouse: frost, high latitude with low winter daylight, an arid climate, high wind, salt or dust, or a wish to grow food crops on the terrace.

This page lists the model objects (tags) that make up the enclosed greenhouse and states what each one is for. At a site where the terrace stays open, these objects are not used.

## 2. Greenhouse objects

Table 2.1 lists the tags. The solids are built by `models/freecad/building_stack.py` as part of the plant model; at an open-terrace site they may be hidden.

Table 2.1. Greenhouse model objects

| Tag | Purpose | Notes |
|---|---|---|
| GH_ENV_S | Main enclosure over the equator-facing terrace band | It covers the OVERFLOW_TERRACE_S_B* beds. |
| GH_ENV_E and GH_ENV_W | Optional enclosures around the east and west ends | They are used only if a mixed open and enclosed layout requires them. |
| GH_AHU | Air-handling unit (AHU) dedicated to the greenhouse | It is separate from the habitation return air; heat from the Q4 heat loop may be used. |
| GH_IRRIG_HDR | Drip irrigation header | It carries clean overflow water (S40) or dilute fertigation, which returns as grey water (S42). |
| GH_DOOR_AIRLOCK | Vestibule between the greenhouse and the terrace apron | It keeps fertigation water out of the catch tank (CATCH). |

## 3. Status

The decision rule is complete in AQS-TRR-001. The schedule on this page is complete. The FreeCAD envelope solids are built with every plant model rebuild.

Streams S40 and S42 are named in this page and in AQS-TRR-001, but at this revision neither is an edge of the plant flow graph (`flow_graph/plant_flow_graph.json`). The irrigation water of the greenhouse is therefore not yet part of the plant mass balance.

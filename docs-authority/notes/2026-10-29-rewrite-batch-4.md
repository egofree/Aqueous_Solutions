# Rewrite batch 4: water purification, life MEP and methanol train

Date: 2026-10-29

AQS-WTR-001 (`WATER_PURIFICATION.md`), AQS-MEP-001 (`LIFE_MEP.md`) and AQS-MeOH-001 (`MEOH_TRAIN.md`) were hand-kept pages that described equipment tags the graph does not carry and cited documents outside the repository (SLINGSHOT/ and the numbered root documents). Each is now written by a generator that reads the graph, and for the life study `models/freecad/params.py`, so the streams, rates, crew size and pipe sizes follow their sources. The generators are registered as regen stages after `write_graph_power`.

The quality targets of the water page came from documents outside the repository. They are kept, and registering a published source for each is listed as an open item on the page.

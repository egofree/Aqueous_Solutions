# EVAP_ACID work order

Plan X-MFG-30. Status M2. Study. Not a PE stamp.

W1 Source. `models/mfg/evap_mvr.py EVAP_ACID` (CadQuery) reads params.design on the graph, written by `flow_graph/param/evap_design.py`.
W2 Envelope. Graph size 1650 x 1300 x 3800 mm (body, blower, interchanger, HCl column and the EVAP_ACID_VS vent scrubber on one frame).
W3 Internals. 22 falling-film tubes ID 25.0 x 1500 mm on triangular pitch, distributor cups at the top tubesheet, mesh pad in the separator.
W4 Nozzles. Feed, product, condensate, vapour to blower, compressed vapour to shell, vent, drain; DN by the line list.
W5 Fasteners. `fasteners.csv`.
W6 Materials. AQS-DUTY-060 section 5.
W7 Pressure. Body 100 kPa g and full vacuum, shell 350 kPa g; relief per AQS-DUTY-060 section 3. Hydrotest 1.43 x design (ASME VIII-1 UG-99 / ISO 16528 practice).
W8 Exports. `export/evap_acid.step`, `export/evap_acid.stl` (watertight, three bodies).
W9 BOM. `bom.csv`.
W10 Fabrication route. `docs-authority/fab/EVAP_ACID.md`.
W11 Self-copy relevance. Graphite machining or nickel tube work, sheet lining, blower casting and balancing all on in-house lines (X-MFG-32).

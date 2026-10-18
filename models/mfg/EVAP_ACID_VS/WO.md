# EVAP_ACID_VS work order

Plan X-PAR-10. Status M2. Study. Not a PE stamp.

W1 Source. `models/mfg/vent_scrubber.py` (CadQuery) reads the EVAP_ACID_VS params on the graph, written by `flow_graph/param/write_graph.py` from `flow_graph/param/vent_scrubber.py`.
W2 Envelope. DN150 x 1400 mm, on the north edge of the EVAP_ACID frame.
W3 Internals. Support plate, 500 mm bed of 16 mm PVC rings, drip-pipe distributor, mesh demister.
W4 Nozzles. Five DN25 sockets.
W5 Fasteners. `fasteners.csv`.
W6 Materials. AQS-DUTY-061 section 2.
W7 Pressure. Atmospheric; leak test 1 m water head.
W8 Exports. `export/evap_acid_vs.step`, `export/evap_acid_vs.stl`.
W9 BOM. `bom.csv`.
W10 Fabrication route. `docs-authority/fab/EVAP_ACID_VS.md`.
W11 Self-copy relevance. PVC pipe, sheet and ring cutting on in-house lines.

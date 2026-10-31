# Sector size and MVS

Document number: AQS-DUTY-038
Revision: D
Date: 2026-10-12
Authority: graph Rev BD. Study. Not a PE stamp.

The crop floor in Revision C stands. Potato and sweet potato at 0.09 kg/m²/day fresh, 6 kg/d, is 70 m². Wheat on two layers is 40 m² of floor. Vegetables and fruit are 40 m². Duckweed is 26 m². Crop floor is 140 m².

The plate is not that floor. The module plate is sized by need: `flow_graph/param/solver.py` grows the plate from the seed bays until the roof carries the photovoltaic need and the loads close, so the issued plate is whatever that solve returns (it has grown past the fixed 24 by 24 m and 432 m² figures of earlier revisions - neither is an issued plate; the solved configuration is in the graph, EXT_HALL carries the added bays). The 470 m² figure was the calorie minimum plus process bays. It is not the issued plate.

Process bays sit on the remaining floor. Azolla is the 18 by 5 m hall, not a module frame.

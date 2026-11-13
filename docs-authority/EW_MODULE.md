# Electrowinning module

Document number: AQS-EW-MOD-001
Revision: E
Date: 2026-11-12
Not a PE stamp.

| Rev | Description | Date |
|---|---|---|
| E | The static cell sizing withdrawn: the copper-equivalent Faraday chain from the plated-sheet mass to the cell current, area and fixed plate count, the rack and frame lengths sized to that count, and the fixed cell voltage, rectifier power and bus section. Cell count, current, voltage, power and bus are sizing outputs of AQS-DUTY-051 and the graph booking. | 2026-11-12 |

1. Basis. The module covers one cell of the EW_1 to EW_9 cascade; EW_1 plates the gold harvest. The deposit, current, cathode count and tank of every cell are solved at the AQS-ASSAY-001 element envelope and booked in the graph (AQS-DUTY-051, `docs-authority/sizing/EW_CELLS.md`); the forming share of the plated metal leaves on IA-EW-SHEET at the EW_9 collection point. Liquor 4288 kg/d from the leach.

2. Size. Cathode current density 200 A/m² (study). Plate immersed 0.6 × 0.42 m, both faces 0.504 m². Cathode-to-anode pitch 50 mm. The cell count, current, cell voltage, DC power and bus section of every cell are sizing outputs of AQS-DUTY-051, not figures of this module.

3. Material. Cathode titanium Grade 2, 3 mm, plastic edge strip so the sheet peels. Anode titanium mesh, 1.5 mm, mixed-metal-oxide coat (Rev D, AQS-STD-002 section 9). Tank PVC/FRP, 10 mm. Frame CPVC (Rev D).

4. Nozzles. Liquor in −X at 20% height. Out +X at 75%. Launder +X at 600 mm. Bus −X at 400 mm. Drain bottom. Vent top to the scrubber.

5. Instruments. Current, voltage, level. High level trips the feed. Low flow trips the rectifier.

6. Relief. Atmospheric. Vent to the scrubber.

7. Code. Shop, PVC/FRP.

8. Open items. Rev D: per-cell sizing is AQS-DUTY-051; the 600 × 420 mm envelope is the plate. Electrode materials set in AQS-STD-002 section 9 (X-MAT-18). The coat life is not measured. The minor-metal arrangement is selectable (owner ruling Q-041, driver `ew_minor_metal_arrangement`): the selective cascade (five minor-metal cells) is sized in AQS-DUTY-051 section 2 and the merged alternative in its section 4; materials, nozzles and instruments of this module apply to a cell of either arrangement.

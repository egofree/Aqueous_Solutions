# Rewrite batch 24: argon blanket gas for crystal growth

Date: 2026-10-29

Owner decision of 2026-10-29: the crystal-growth blanket gas is argon from the cold box, sized from need, with the graph kept closed. Nitrogen was to stay a valid alternative if the design allows.

## Design

`flow_graph/param/fab_silicon.py` sizes the argon from the puller. The puller is under gas for the meltdown, the neck and crown, the body pull and the cool-down. The flow scales with the crucible area. The argon of a pull is averaged over the days between pulls, which batch 23 derived from the wafer need (A-M-417).

Table 1. Streams added

| Stream | From | To | Basis |
| --- | --- | --- | --- |
| IA-AR-CZ | CRYO_ASU | WAFER_FAB | puller argon per pull over the days between pulls |
| IA-AR-CZ-BACK | WAFER_FAB | CRYO_ASU | the same argon, returned to the heated getter of the cold box |

The loop is closed: the exhaust returns to the getter that the cold box already carries for the fab argon return, so the supply equals the return and the cold-box balance does not change. The getter load is already in the cold-box load, so the bus demand, the array and the storage do not change.

## Nitrogen

The design does not allow nitrogen as the blanket gas of the puller. At the melting point of silicon, nitrogen reacts with the melt and the crucible to form silicon nitride, which spoils the crystal. The driver `FAB.wafer-line-train.cz_blanket_gas` holds the choice, and `fab_silicon.py` refuses any value other than argon with that reason. Nitrogen stays the purge gas of the wafer tools on S03, and the owner can still reverse this if a nitrogen-tolerant process is meant.

The style terms file now lists the two-letter revision letters that follow Z (AA, AB, AD, AE and AF; AC already passes as alternating current) as not abbreviations, so revision tables can run past Z.

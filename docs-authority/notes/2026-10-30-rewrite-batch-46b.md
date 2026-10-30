# Rewrite batch 46b: silicon wafers for the solar cell line

Task X-RTE-PV-SI is closed (A-M-437). The cell line SOLAR_PV_CELL had a study rate of 3 cells a day of the 156 mm format and no wafer feed. It now makes the cells that replace the plant's own roof array, so its rate follows from the graph. The array nameplate is multiplied by the share replaced each year and divided by the power of one cell. A module is replaced when its output falls to the end-of-life share of nameplate at the median degradation rate, and random failures add their own share.

The wafers come from WAFER_FAB on IA-PV-WAFER by the new driver pv_wafer_route. Both valid technologies are built:

- CZ_PSQ125, the default, cuts 125 mm semi-square cells from the 150 mm ingot of the existing puller. It shares the puller, the hot zone and the refining with the fab wafers and gives the more efficient cell. The pulls come closer together because the ingot now also carries the solar wafers.
- CAST_MC156 casts a multicrystalline block by directional solidification in a cast furnace in WAFER_FAB. Its heat loss is found by the same felt method as the hot zone of A-M-436. It is the second technology because it does not depend on the puller.

A second, larger puller for 156 mm single-crystal cells was evaluated and not built. It would need a second hot zone and a least melt several times the charge of the existing puller, for cells that the 125 mm format already gives.

Recovery comes first: the cells retired from end-of-life modules return their silicon to the chlorosilane loop of SI_REFINE on IA-PV-EOL, so the quartz reduced falls by that silicon. The finished cells go to PV_ARRAY on IA-PV-CELL. The cell line runs in batches of one wafer carrier, and its PECVD electrode, platen and chamber follow from the carrier. The pot chlorine export now stays net of the loop make-up when the cell need moves it after `foundry_poly.py` has run.

The module glass, encapsulant, ribbon, frame and contact pastes are a new task, X-RTE-PV-MODULE. Both routes close the mass balance with no move of the balance fit. The plant load rises with the refining of the larger silicon need, and the PV pin of `test_system_tree.py` follows it.

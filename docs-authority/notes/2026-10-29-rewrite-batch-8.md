# Rewrite batch 8: load list and bus demand, scale-down page, matplotlib folder index

Date: 2026-10-29

The load list AQS-ELEC-003 gives a connected load of 141.1 kW, and the power sizing AQS-ELEC-007 gives a plant bus demand of 179.7 kW. The code explains the difference. `docs-authority/_power_sizing.py` sums the continuous loads of the units and the feeds of the inverter bus, adds the extension hall `EXT_HALL`, and adds the alternating-current input of the rectifier for the electrowinning cells, 38.7 kW, which the graph holds as `RECTIFIER.params.rect_ac_input_kW`. `docs-authority/_load_list.py` sums the same unit loads and the extension hall, but lists the electrowinning cells as direct-current loads behind the rectifier and leaves them out of its alternating-current sum; its `RECTIFIER` row carries only the 12 kW of the 48 V rails. The two figures agree to 0.01 kW once the rectifier input is added. Both generators now state this, computed from the graph.

The reconciliation shows a probable error that this work does not fix, because the rectifier numbers are on hold. Stream S17, which feeds the rectifier, carries 12 kW, and the one-line diagram sizes the rectifier feeder from it, while the rectifier input at the bounding current is at least 50.7 kW. This is added to the owner questions in `REWRITE_TODO.md`.

The scale-down page AQS-SCALE-UR-001 was brought to Rev F through `flow_graph/param/scale_down.py`. The matplotlib folder index was rewritten by hand: it has no generator, contrary to the earlier entry in `REWRITE_TODO.md`, and it wrongly said that none of the images is published, while the regeneration builds some of them into `media/pfd/`.

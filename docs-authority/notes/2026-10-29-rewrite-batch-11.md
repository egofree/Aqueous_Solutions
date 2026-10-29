# Rewrite batch 11: sanitation generator and the rectifier finding corrected

Date: 2026-10-29

The sanitation page AQS-DUTY-063 is generated again. Its script, `flow_graph/param/sanitation.py`, had edited the graph once on 2026-10-15 and was then listed as a retired one-time edit, so the page kept values that no longer matched the graph. The script is rewritten to read the present graph and write only the page, and it runs as regen stage `sanitation_doc`. The graph carries the train as the one node BLACK_DIGEST, so the page sizes the equipment of every barrier from the flows of that node. The revision control script no longer lists the page as an exception.

The new page shows two differences from the graph, which are recorded as an owner question in AQS-DOC-003 and not changed. The barrier units BLACK_DEWATER, BLACK_PASTEUR and BLACK_ALK_HOLD are no longer graph nodes. The feed SF-BLACK_DIGEST carries the digester load only, about half of the load of the whole train.

The rectifier finding of batch 8 was wrong in part. The one-line diagram AQS-ELEC-002 has two rectifier feeders, S17 for the 48 V rails and RECT-EW for the electrowinning cells, and together they carry what the plant bus demand counts for the rectifier. The load list AQS-ELEC-003 (Rev F) and the power sizing AQS-ELEC-007 (Rev I) now say so. The load that has no supply is the set of trim heaters that the graph feeds from the rectifier at their rated values. Whether the bus demand should carry them, and at the rated or the normal load, decides the array, storage, inverter and bus section sizes, so the owner question in AQS-DOC-003 now asks that, and no value was changed.

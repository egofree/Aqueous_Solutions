# Rewrite batch 9: four sizing pages

Date: 2026-10-29

Four sizing pages were rewritten through their generators: the hydrogen compressor AQS-DUTY-067 (`h2_compressor.py`), the headers AQS-DUTY-075 (`headers.py`), the ultrapure water polish AQS-DUTY-070 (`upw_polish.py`) and the photovoltaic cell line tools AQS-DUTY-071 (`pv_cell_line.py`), all in `flow_graph/param/`. Each page now has a record of revisions, a purpose and scope section, its method written as sentences and numbered tables.

Several figures were typed into the page text although the generators read them from the drivers: the compressor suction temperature and pressures, and the membrane permeance, design flux, EDI current efficiency, cell count and cell voltage of the polish. The text now prints the driver values. The compressor description written to the graph also takes its pressures and unit count from the drivers; the values are the same, so the graph did not change.

The headers page no longer states the life support heating load as a fixed number, and the cell line page names the tool that uses the most energy from the calculation instead of naming it in the text. No values changed.

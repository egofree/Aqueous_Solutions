# Power

Document number: AQS-PWR-001  
Former number: AQS-PWR-002 (on this page 2026-10-17 to 2026-10-24 in error; AQS-PWR-002 is GEOTHERMAL_BACKUP.md)  
Revision: B  
Date: 2026-11-04  
Authority: the live graph. Not a PE stamp.  
The demand and supply figures below are the Rev A study summary, kept for the record; the live book is the graph and `docs-authority/ONE_LINE.md`.

## Summary

| | kW |
|--|---:|
| PV nameplate | 70 |
| Fuel cell firm | 4 |
| ZnBr₂ | 60 class |
| Backup gen | 2.5 (outage) |
| EW rectifier AC input | graph `params.rect_ac_input_kW` (counted once; the former 12 kW rail stamp was removed as a double count) |
| New process average | ~20 |
| New process peak if stacked | ~67 |

Firm supply without PV is 4 kW plus storage. Average new process load is covered by PV and ZnBr₂. Peak is covered by not stacking batches.

## Not in the sum

GEO_ORC (0–2 kW_e, surplus only). HYDRO_SET (study; smaller than ZnBr₂).

## References

notes/POWER_DUTIES.md, notes/LOAD_ROLLUP.md, docs-authority/ONE_LINE.md.

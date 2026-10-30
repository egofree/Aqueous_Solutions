# Rewrite batch 42e: transfer-function rates held against the reconciliation fit

Date: 2026-10-30

## Finding

The audit of batch 42d found that the issued graph did not carry the photoresist design. POLY_TO_FAB read 0.024 kg/d instead of 0.12 kg/d, and IA-RESIST-BZ, IA-RESIST-STOCK, IA-RESIST-VENT and IA-FAB-SOLV read zero.

There were two causes.

- `balance.reconcile` holds an edge only when its rate note carries one of the markers in `balance.MARK`. The marker X-RTE was not in that list. So every rate set by an X-RTE transfer function was free for the least-squares fit to move: the bench solvent of A-M-428, the grease of A-M-429 and the photoresist of A-M-432.
- `o2_close.py` re-solves IA-C5-SHIP as the C5-C10 make less the generator fuel and the olefin feed, after `fab_resist.py` has taken the benzene feed off it. The cut tank was therefore 1.005 kg/d short. The fit closed the shortfall by setting the benzene feed to zero and moving the other resist and fab edges with it.

The reconciliation report showed no gross move because the edges were reconciled down to new values, and the next pass held those values.

## Change

- `balance.MARK` includes X-RTE, so the transfer-function rates are held as design values.
- `o2_close.py` takes the resist benzene feed IA-RESIST-BZ off IA-C5-SHIP.
- The new test `test_transfer_function_edges_are_held` in `flow_graph/param/test_balance.py` fails if the fit is free to move a transfer-function rate.

With these changes the fit moves no edge, and the largest unit residual is the 0.7 g/d that was already present at COLD_MILL.

## Values

| Quantity | Issued at batch 42d | After |
|---|---|---|
| POLY_TO_FAB | 0.0236 kg/d | 0.1200 kg/d |
| IA-RESIST-BZ | 0 | 1.0052 kg/d |
| IA-RESIST-STOCK | 0 | 0.1200 kg/d |
| IA-FAB-SOLV | 0 | 0.2195 kg/d |
| IA-FAB-N2-VENT | 0.9385 kg/d | 1.4998 kg/d, the S03 rate |
| IA-SOLV-PLANT | 0.4676 kg/d | 0.5195 kg/d |
| IA-C5-SHIP | 7.6351 kg/d | 6.6298 kg/d |

No assumption changes. The design bases stay A-M-428, A-M-429 and A-M-432.

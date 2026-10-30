# Rewrite batch 36: pattern wax from the plant wax cut

Date: 2026-10-29

## Change

Owner decision t59u: the plant imports nothing except waste or raw ore. The pattern wax make-up came from the dock on stream IA-WAX-MU, as a petroleum-wax import. It now comes from the plant's own C19-C28 pyrolysis cut, which is the paraffin-wax range and was already shipped as surplus. Task X-RTE-IMPORT-IA-WAX-MU is done, and IA-WAX-MU is retired.

- `flow_graph/param/foundry_poly.py` writes the new stream C19_TO_WAX from PROD_C19_C28 to WAX_PATTERN. Its rate is the share of the pattern wax that the dewax reclaim does not cover, so the reclaim is used first (recovery first, A-M-423).
- `flow_graph/param/ess_tf.py` takes the draw off the C19-C28 export IA-C19-SHIP and asserts that the plant draws never exceed the cut.
- The foundry edge helper now marks a new edge present and takes its source sector from the source unit. Before, it copied both from the solvent import edge.
- The basis is recorded in A-M-424. The import is gone from the recovery-first check's list of pending imports.

## Values

| Quantity | Before | After |
|---|---|---|
| IA-WAX-MU, pattern wax from the dock | 0.2 kg/d | retired |
| C19_TO_WAX, plant paraffin cut to WAX_PATTERN | none | 0.2 kg/d |
| IA-C19-SHIP, C19-C28 export | 2.2181 kg/d | 2.0181 kg/d |

## Left open

Section 4 of the FOUNDRY_LINE sizing page (`docs-authority/_foundry_sizing.py`) still describes the Ti, Mo, Cr and investment-casting trains as blocked by missing feeds, as they were at revision AC. That section is stale and needs its own rewrite.

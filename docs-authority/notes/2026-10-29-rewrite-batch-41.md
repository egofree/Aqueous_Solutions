# Rewrite batch 41: shop grease made on site

Date: 2026-10-29

## Change

Owner decisions t59u and t61u apply: the plant imports nothing except waste or raw ore, and it recovers before it makes. The grease routes were in the graph but carried no flow. Tasks X-RTE-GREASE_CA_TO_MFG, X-RTE-WAX_TO_GREASE_CA and X-RTE-PCA_TO_GREASE are done by flow, and the lithium routes are done at their rated case.

- The new module `flow_graph/param/grease.py` sizes the grease need from the grease points. These are the lubricated rotating units of the maintenance plan, two points each, at the SKF side-fill quantity for a 6205-class bearing and the lubrication interval of the maintenance plan.
- The grease is a soap in the C19-C28 base oil. The soap acid comes from air oxidation of part of the wax cut, with air from the atmosphere and not from the oxygen header, which is held.
- The driver grease_thickener selects the soap. CA, the default, slakes lime drawn from the acid-plant residue in P_CA (IA-LIME-TO-PCA) and saponifies in GREASE_CA. The insoluble part of the residue returns to the dock export (IA-PCA-REJECT). LI uses lithium from LI_RECOVER in GREASE_LI and stands by at its rated case until the lithium tenor of the polish liquor is measured.
- Spent grease returns from MFG_SHOP to oil pyrolysis (IA-GREASE-SPENT). Each kettle is sized as an insulated campaign kettle, and its supply edge carries the average load.
- The references SKF_RELUB, ULLMANN_LUBRICANTS and ULLMANN_FATTY_ACIDS are added. AQS-DUTY-GREASE is at revision B and points to the computed rates. The basis is recorded in A-M-429.

## Values

The rates are those of the regenerated graph and of `python3 -m flow_graph.param.grease`. The grease need is a few grams a day, far below the fixed rates of AQS-DUTY-GREASE revision A, which were not tied to any grease point. POLISH_TO_LI stays open because the lithium tenor is unmeasured.

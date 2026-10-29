# Rewrite batch 25: routes without flow on the task list

Date: 2026-10-29

Owner decision of 2026-10-29: every route that carries no flow is unfinished design. Each goes on the task list, and the clear ones are finished.

## Task list

`docs-authority/_task_plan_gen.py` now builds a task group X-RTE in AQS-PLAN-007 from the graph each time it runs. It takes every present mass route without a rate and sorts it as follows.

- Relief and contingency routes are closed by design and are not tasks.
- An open route gets its own task, X-RTE followed by the stream identifier. It is done when the route carries a rate sized from need with both unit balances closed, or when it is retired with its reason.
- Standby, N+1 and site-mode routes are grouped in X-RTE-STANDBY: each needs the rate of the case that puts it in service, so that its line and both units are sized for it.
- Return routes without flow are grouped in X-RTE-RETURN.
- Routes noted as retired but still present are grouped in X-RTE-RETIRED, tagged for the owner.

A route that is given its flow drops out of the open list. The routes finished in the QA pass are kept as done tasks with their evidence. Four further tasks are added: silicon wafers for the solar-cell line (X-RTE-PV-SI), in-house refining of SI_REDUCE silicon as the backup of the polysilicon import (X-RTE-SI-BACKUP), a heat-loss model of the CZ hot zone (X-RTE-CZ-HOTZONE), and the check of the remaining hand-drawn process sheets (X-RTE-LEGACY-PFD).

## Routes finished

Table 1. Routes done and routes tasked

| Route | Outcome |
| --- | --- |
| STOCK_TO_FAB | Done in batch 23: carries the silicon feed of the wafer fab. |
| S36, S39B, MO_CELL_RAFFINATE, EW9_LIQUOR_TO_MO, EW_METALS_TO_IND | Done here: set to presence retired. Each note already named the live path that replaced it, and none carried flow. |
| STOCK_TO_WIRE_DRAW, IND_TO_ATOM | Tasked as open routes. Each is a second feed to a tool whose design feed is live (S57 to WIRE_DRAW, IA-MELT-ATOM to GAS_ATOMIZER). Whether to keep it as a diverse feed with a rated case or retire it is not clear from first principles. |
| Grease line, habitation waste and CO2, farm, foundry and polymer alternates, and the other open routes | Tasked one by one in X-RTE. Most are topology from graph revision AC that the parameter pass has not yet rated; each needs its own sizing. |
| Standby and return routes | Tasked as two grouped tasks. |

None of these changes moves the bus demand, the array, the storage or the balance closure: the retired routes carried no flow.

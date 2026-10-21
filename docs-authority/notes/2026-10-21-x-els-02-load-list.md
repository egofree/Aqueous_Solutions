# 2026-10-21 - X-ELS-02 load list closure (AQS-ELEC-003 Rev C, A-M-317)

## Item

X-ELS-02 (AQS-PLAN-007, desktop P1): "Every node continuous_kw from a calculation,
not a study share. Start from `docs-authority/LOAD_LIST.md` (partial)."

## Start state (from the dead-register precursor, commit `ebaa959`)

Load census: 71/84 rows calculated, 11 "study share - basis pending" rows
(FUEL_CELL, MEOH_FC, WAFER_FAB, COMB_HEAT, NUTRIENT_DOSE, RES_HEAT, VAC_CAST,
EXTRUDE, DRAW, FORGE, SINTER). The graph stamps for all 11 were already
calculated/cited (A-M-297/299 tool train and dosing skid, A-M-283 N+1 policy, the
A-QS-REQ-KW-001 owner locks) - the stale actor was the `_load_list.py` classifier,
not the graph. The GEO source-loop circulator (125.8 W, sized by AQS-DUTY-076 at
stage `sizing_geo_loop`) was sized but stamp-less, and the GEO_HP node note still
said "Ground-loop circulator not yet sized (X-ELS-02 residual)".

## Changes

1. **`flow_graph/param/geo_loop.py`** - keeps sizing ownership; writes
   `params.design` only. A-M-317 note recorded why the demand stamp lives
   elsewhere (a stamp written at stage 15 lands after `write_graph.process()`
   captures its `before` bus-load delta at stage 0 of the pass, so the PV feeder
   could never absorb it in one pass).
2. **`flow_graph/param/write_graph.py`** (`process()`, stage 0):
   - stamps GEO_HP_CLOSED_LOOP continuous_kw = 0.1258 kW from the pre-existing
     `params.design.pump_W` (sizing stays in `geo_loop.py`), reads `head_m`,
     cites AQS-DUTY-076 + AQS-DUTY-010 dispatch + A-M-231 + A-M-317;
     sets `electrical_role='load'`;
   - creates the bus feed `SF-GEO_HP_CLOSED_LOOP` (SOL_ARK_60K, 480 V,
     "Feed equal to continuous_kw") in the `EVAP_ACID_VS` writer pattern and adds
     it to `ELEC_IN`, so `bus_load()` counts it and the SOL_ARK/IA-PV-01
     rebalance absorbs the demand change (EVAP sump-pump precedent);
   - stamps `GEO_HP`'s note: stale "not yet sized" sentence -> circulator sized at
     AQS-DUTY-076, counted on the bounding winter case (A-M-317);
   - **AQS-MFG-010 Rev C metering split**: `_mfg_tools.py` output gains
     `shop_avg/shop_connected` + per-tool rows; `MFG_SHOP` = six shop machine
     tools only (2.55 kW avg, 26.5 kW connected; roster framing kept: connected
     42.8 kW, coincident peak 24.5 kW frames MCC-1); the four metal tools
     MET_MELT 0.2369 / GAS_ATOMIZER 0.0781 / COLD_MILL 0.0191 / WIRE_DRAW
     0.0189 kW stamped at their per-tool kWh/d / 24 h, each with its own SF
     feeder and `electrical_role='load'`. Total roster demand unchanged
     (2.55 + 0.353 = 2.90; only 4-dp rounding moves the bus, +0.003 kW).
3. **`docs-authority/_load_list.py`** (AQS-ELEC-003 Rev C, 2026-10-21):
   - TOK += `AQS-EQP-FAB` / `AQS-EQP-NUT` / `CRC_SI` (A-M-297/299 citations);
   - new classes: `standby-zero` (keyed on "standby-zero on the design day",
     basis = the stamp's own A-M-283 policy text; 9 rows incl. the RF_HEAT /
     VAC_IND duty-cycle alternates) and `owner-lock` (FUEL_CELL, MEOH_FC -
     owner requirement inputs AQS-REQ-KW-001, the only census rows documented
     without a calculation, per A-M-301);
   - census/status/header rewrite for Rev C; basis cells escape the ' | '
     stamp separator so the markdown table stays single-column; connected
     sums split calculated / standby parasitic / study-share.
4. **Registers**: `A-M-317` appended (circulator counted at its 125.8 W design
   draw on the bounding winter case; sensitivity = +125.8 W only on the lift
   dispatch, replaced by first-article pump curve); `A-M-276` annotated (Rev C
   census superseded the Rev B pending record; row retained). Register
   regenerated, validation exit 0 (317 curated).
5. **Golden update**: `flow_graph/param/test_system_tree.py` generation-train
   aggregate 340.7098 -> 340.7128 (PV 336.7016 -> 336.8304 = +0.1258 circulator
   + 0.0030 split quantisation), reason recorded in the test comment.
6. **Board**: `X-ELS-02` ticked in `_task_plan_gen.py` DONE_X with evidence
   `docs-authority/LOAD_LIST.md`; TASK_PLAN regenerated (byte-true board).

## Verification (the check the plan states)

- Census: 76/89 calculated; 9 standby-zero policy rows; 2 owner locks
  (FUEL_CELL 4.000, MEOH_FC 1.000); 2 null by design; 0 pending study-share
  rows. Connected AC load 141.1 kW: 141.0 calculated (100.0 %), 0.05 kW standby
  parasitic (COMB_HEAT), 0.00 study shares.
- `pytest flow_graph/` 43/43 pass; `regen --check` 920 files 0 stale;
  `check_authority_contract.py` projection=on-disk 178/562 (+5 feeds: 4 tool
  SF + pump SF); graph multi-pass fixed point (2 passes stable).
- Demand chain: need_kw 179.62 -> 179.74 kW (+0.126); IA-PV-01 336.7016 ->
  336.8304; ONE_LINE/MODEL_WORKBOOK/CABLE_SCHEDULE/registers regenerated
  (WIRE_INVENTORY byte-unchanged - its circuits are motor-roster driven, and its
  roster already carried the per-tool metal circuits).

## Open items recorded for later waves (not silently diverged)

- **Motor-roster unit attribution** (Wave-2, X-INV-02 family):
  `MOTOR_INVENTORY.csv` row 114 puts the "ground-loop circulator" (0.12 kW,
  208 V 3-ph, assumed) on unit `GEO_HP`, while the graph carries the demand on
  the separate node `GEO_HP_CLOSED_LOOP` (0.1258 kW counted, A-M-317). Same
  physical pump; reconcile the roster/other-inventory rows (GEO_HP_CLOSED_LOOP's
  OTHER rows also label BLDC/fan devices "induced-draft fan") with the graph
  node split at first article.
- Wave-2 family sizing leftovers unchanged: MET_AHU fan airflow basis,
  BAGHOUSE flue flow, CRYO receiver-bank drivers (defer from the earlier lane
  note; they carry no pending load-list rows).

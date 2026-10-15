# Manufacturing model plan

Document number: AQS-PLAN-006
Revision: A
Date: 2026-10-15
Authority: graph Rev BH. Not a PE stamp. A plan, not a model. No unit is modeled by this revision.

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue. Work order, order of work, acceptance, tooling, tracker for the 199 present units | 2026-10-15 |

This is the sequence that turns every present unit from an envelope into a manufacturing model: a parametric source a shop can build from. It is phase 5 of AQS-PLAN-005 and step 4 of AQS-PLAN-002, written as a work order. AQS-MFG-001 (`DETAIL_MODEL_PLAN.md`) lists the shop-level OpenSCAD envelopes that already exist. They are inputs here. They are not accepted manufacturing models.

## 1. Rules

1. The graph is the plant. A model reads its dimensions, nozzles, internals, material, and design pressure from the graph node and the duty page. It does not write a new number onto them.
2. No dimension is invented. Where the node has no diameter, no holdup basis, or no machine envelope, the model is drawn to `size_mm` and the work order names the missing fact. That is a hold, not a guess.
3. Modeling does not resize. A model that does not fit its envelope is reported. The envelope, the rate, and the bore are changed only by a plan line that allows it.
4. One unit per commit. The tracker row in section 7 closes in the same commit as the model, the exports, and the duty page section 7.
5. Feedstock is not fixed. Wetted materials follow the duty section 3 and are checked against the AQS-ASSAY-001 envelope, not one feed.
6. Purchased items are named as purchased, with the rating from the node. They are drawn as their envelope and interface, not as invented internals.

## 2. Work order per unit

Each unit gets `models/mfg/<UNIT>/` with these items. The work order is complete when every item is present or carries a named hold.

| Item | Content | File |
| --- | --- | --- |
| W1 Parametric source | One script. Reads `params.json`. Builds the shell, the internals, the nozzles, the supports, and the fasteners as separate solids. Graph revision in the header | `<unit>.py` |
| W2 Parameters | Generated from the graph node and the duty page by the tracker tool. `size_mm`, `origin_mm`, `design_kPa`, `relief_mm`, internals, the nozzle list of duty section 4, material of section 3. Not edited by hand | `params.json` |
| W3 Internals | Every internal named on the node is a solid. Class row from AQS-PLAN-005 Rev C. `none` means no internal solid, and the tracker says so | in W1 |
| W4 Nozzles | Each nozzle of duty section 4: tag, face, height, bore, rating. Hose and atmospheric where the duty says so. Flange to the 110 % rule only where a process pressure is stated. Bore not calculated is drawn at DN15 and labeled as not calculated | in W1 |
| W5 Fasteners | Size, grade, length, and count for every bolted joint. Metric. Grade rule of this plan, not a calculation: A4-70 on 316L, 8.8 on carbon steel, polymer joints to the polymer supplier rule | `fasteners.csv` |
| W6 Materials | Every part names its alloy or polymer, thickness, and corrosion allowance from AQS-STD-001 | in `bom.csv` |
| W7 Drawings | General arrangement, nozzle orientation, and one sheet per fabricated part. Title block names the graph revision and this plan | `drawings/*.pdf`, `drawings/*.svg` |
| W8 Exports | STEP AP214 for each part and the assembly. STL of the assembly, closed and manifold, millimetres. The STL replaces `cad/stl/<UNIT>.stl` | `export/` |
| W9 BOM | Generated from the model. Part, quantity, material, mass, make or buy | `bom.csv` |
| W10 Fabrication route | Route class from section 4. Operations in order: cut, form, weld or join, machine, test. Which on-site tool does each operation | `WO.md` |
| W11 Self-copy relevance | Whether the unit is a shop tool that makes plant parts, and which of its parts the on-site shop can make. Cross-reference AQS-BOM-SC-001 | `WO.md` |
| W12 Holds | Every missing fact, by name, from the AQS-PLAN-005 hold table | `WO.md` |

## 3. Order of work

Tiers run in order. Inside a tier, units with a seed origin come first, then units that already have an AQS-MFG-001 source, then by name. The tracker in section 7 is in this order.

| Tier | Units | Why this place |
| --- | --- | --- |
| T0 | No unit. Tooling gate and the shared library | Nothing is modeled before the tools are recorded and the library passes its check |
| 1 | EXPANDER | The one pressurized unit. Relief is calculated (D4). Wall and relief nozzle can be checked against a stated pressure |
| 2 | LEACH_CSTR_1, EW_1 to EW_9 | The metal line. AQS-PLAN-002 section 4 names them first. The cell internals are already drawn as plate racks |
| 3 | Cold boxes, CRYO_ASU first; BIOFILTER; ETOH_STILL; BUOH_STILL | The rest of the AQS-PLAN-002 first list. CRYO_ASU is the relief destination of tier 1 |
| 4 | HOPPER, FLOAT_SINK, then every unit with a vessel internal row | The feed and solids path held under D1, then scrubbers, exchangers, tanks, cut tanks, separators, heat batteries |
| 5 | Headers, recycle pipes, relief and intra units | Line lists and spools, not vessels |
| 6 | Process machines whose internal is none | Dryer, pyrolyzer, fractionator, BMED, CRU, polish, treat, reactor, reagent skids |
| 7 | Shop tools and forming | Self-copy relevant. Modeled after the parts they make are defined |
| 8 | Electrical and boundary | Mostly purchased. Enclosure, mounting, and terminations |
| 9 | Farm and habitation | Frames, liners, beds. A bed is not shrunk to fit its block |

## 4. Fabrication route classes

| Route | Classes | Operations |
| --- | --- | --- |
| F-VES | vessel, tank, cut_tank, digest, reactor, ferment, hopper, separator, treat, dose, feed, polish, cru, melt | Plate or sheet cut, roll, weld or thermoplastic weld, nozzle set-in, hydro or leak test |
| F-CELL | ew_cell, bmed, cell, pem_fc, iem_fc, flow_battery | Tank fabrication, plate shear and punch, bus bar cut and drill, gasket cut, stack assembly |
| F-COL | scrubber, cold_box, frac | Column shell, packing support, distributor, demister, vacuum jacket where named |
| F-HX | hx, heat_battery, cool, ahu, heat_pump, thermal, ghex | Plate pack or coil, headers, frame, pressure or leak test |
| F-PIPE | header, recycle_pipe, intra, relief | Spool cut, join, support, line list |
| F-MACH | tool, forming, mill, shop, pyro, dryer, baghouse, genset, fab, wet_bench, hydro, dock, rectifier, inverter, pv, skid, reagent | Frame weldment, guards, purchased drive or electrical by rating, anchors |
| F-FARM | farm, hab | Frame, liner, bed, drainage |
| none | boundary | Accounting node. No hardware. No solid |

## 5. Acceptance

A unit is accepted when every criterion of its set passes on the files.

A-core, every unit with hardware:

1. `<unit>.py` builds headless from `params.json` with no manual step. The run is recorded with the tool versions.
2. The assembly bounding box is inside `size_mm` within 1 mm, or the misfit is reported on the board and nothing is resized.
3. Every nozzle of duty section 4 is present at its face, height, bore, and rating, and is tagged.
4. Every internal on the node is a solid. None is represented by text.
5. Every part has a material, a thickness, and a corrosion allowance that match the duty section 3.
6. The BOM is generated from the model. Every row has quantity, material, mass, and make or buy.
7. Every bolted joint has a fastener row.
8. The drawings exist and name the graph revision.
9. STEP and STL exist. The STL is closed and manifold. `cad/stl/<UNIT>.stl` is replaced.
10. The duty section 7 points at the model. The graph sentence and the duty size line still agree.
11. The work order lists every hold by name.

Class sets, in addition to A-core:

| Set | Criteria |
| --- | --- |
| A-P | Shell thickness shown against `design_kPa`. Relief connection drawn at `relief_mm` to the named destination |
| A-VES | Holdup volume from the model is reported. It is not used as a residence time unless the duty already has a holdup basis |
| A-CELL | Plate count, plate size, pitch, and active area match duty section 2. Bus bar section matches `POWER.md` where it is stated |
| A-COL | Packing height, support, distributor, and demister are solids. Stages or HTU stay a hold where the duty says so |
| A-HX | Plate or coil area from the model is reported. It is not called a calculated area where the node has no heat rate |
| A-PIPE | Line list: tag, from, to, DN or "bore not calculated", rating. Spool drawing. No new edge |
| A-MACH | Purchased items named with the rating from the node. Guard and anchor drawn |
| A-FARM | Bed area matches the node. Liner and drain drawn. Not shrunk to fit the block |
| A-SC | Self-copy: the parts the on-site shop makes are flagged in the BOM and cross-referenced to AQS-BOM-SC-001 |
| A-ACC | Accounting node. The tracker says no solid. Nothing else |

## 6. Tooling

| Tool | Where | State on 2026-10-15 |
| --- | --- | --- |
| CadQuery 2.8.0 with cadquery-ocp 8.0.1 | Agent box, Python 3.13 | Installed in a virtual environment on 2026-10-15. EXPANDER built and exported |
| FreeCAD 1.0, `freecadcmd` | Operator box | Named in AQS-STL-001 and `models/freecad/BUILD_LOCAL.md`. Not on the agent box |
| OpenSCAD | Operator box | Named in AQS-STL-001. Not on the agent box |
| Git LFS | Repository | `*.stl` and `*.FCStd` are LFS. The `models/export` STLs are LFS pointers in an API read |

Authoring is CadQuery, because it runs headless, writes STEP directly, and installs from the package index. FreeCAD on the operator box makes the TechDraw sheets and places the solids in `plant.FCStd`. The AQS-MFG-001 OpenSCAD sources are ported to CadQuery, not deleted.

T0 gate, before tier 1:

1. Install CadQuery and the OCP wheel in a project virtual environment. Record the versions in `DEPENDENCIES.md`.
2. Shared library `models/mfg/lib/`: nozzle and flange stubs DN15 to DN50, hose barbs, the AQS-MOD-001 frame members, the fastener table, the material table.
3. Tracker tool `models/mfg/tracker.py`: reads the graph, writes every `params.json`, regenerates section 7 of this page, and runs the A-core checks that can run on files: bounding box, nozzle count, manifold STL, STEP present, BOM complete.
4. Smoke test: one box with one DN15 nozzle, built, exported, and checked. The test passes before the EXPANDER is started.

## 7. Tracker

Generated from `flow_graph/plant_flow_graph.json` Rev BH, `flow_graph/placement_seed.json` Rev H, the `cad/stl` sizes, and AQS-MFG-001. 199 present units.

Status codes. M0: `cad/stl` is an envelope box or boxes. M1: `cad/stl` has coarse internals, such as the cell plate racks or a packed section, but there is no manufacturing source. M2: parametric source in `models/mfg` builds. M3: accepted under section 5. Today: 166 at M0, 30 at M1, 1 at M2 (EXPANDER), 2 accounting nodes, none at M3.

Facet counts are estimated from the ASCII STL file size. "Existing source" is an AQS-MFG-001 or `models/freecad` file that bears on the unit. None of them is accepted.

| Seq | Unit | Sector | Class | Tier | Internal on node | Seed origin | `cad/stl` now | Existing source | Route | Acceptance | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | EXPANDER | CRYO | tool | 1 | none | yes | envelope, ~23 f | `models/mfg/EXPANDER/expander.py` | F-MACH | A-core, A-MACH, A-P | M2. Builds, STEP and STL. No drawings, STL not one manifold, `cad/stl` not replaced |
| 2 | LEACH_CSTR_1 | WET | vessel | 2 | none | yes | envelope, ~23 f | mfg_leach_cstr.scad, leach_cstr.py, leach_cstr.step | F-VES | A-core, A-VES | M0 |
| 3 | EW_1 | WET | ew_cell | 2 | cathode plates, edge strips, PbO2 anodes, launder | yes | plate rack, ~260 f | ew_cell.py, ew_cell.step, mfg_ew_fitout.scad | F-CELL | A-core, A-CELL | M1 |
| 4 | EW_2 | WET | ew_cell | 2 | cathode plates, edge strips, PbO2 anodes, launder | yes | plate rack, ~260 f | ew_cell.py, ew_cell.step, mfg_ew_fitout.scad | F-CELL | A-core, A-CELL | M1 |
| 5 | EW_3 | WET | ew_cell | 2 | cathode plates, edge strips, PbO2 anodes, launder | yes | plate rack, ~106 f | ew_cell.py, ew_cell.step, mfg_ew_fitout.scad | F-CELL | A-core, A-CELL | M1 |
| 6 | EW_4 | WET | ew_cell | 2 | cathode plates, edge strips, PbO2 anodes, launder | yes | plate rack, ~35 f | ew_cell.py, ew_cell.step, mfg_ew_fitout.scad | F-CELL | A-core, A-CELL | M1 |
| 7 | EW_5 | WET | ew_cell | 2 | cathode plates, edge strips, PbO2 anodes, launder | yes | plate rack, ~35 f | ew_cell.py, ew_cell.step, mfg_ew_fitout.scad | F-CELL | A-core, A-CELL | M1 |
| 8 | EW_6 | WET | ew_cell | 2 | cathode plates, edge strips, PbO2 anodes, launder | yes | plate rack, ~35 f | ew_cell.py, ew_cell.step, mfg_ew_fitout.scad | F-CELL | A-core, A-CELL | M1 |
| 9 | EW_7 | WET | ew_cell | 2 | cathode plates, edge strips, PbO2 anodes, launder | yes | plate rack, ~308 f | ew_cell.py, ew_cell.step, mfg_ew_fitout.scad | F-CELL | A-core, A-CELL | M1 |
| 10 | EW_8 | WET | ew_cell | 2 | cathode plates, edge strips, PbO2 anodes, launder | yes | plate rack, ~35 f | ew_cell.py, ew_cell.step, mfg_ew_fitout.scad | F-CELL | A-core, A-CELL | M1 |
| 11 | EW_9 | WET | ew_cell | 2 | cathode plates, edge strips, PbO2 anodes, launder | yes | plate rack, ~260 f | ew_cell.py, ew_cell.step, mfg_ew_fitout.scad | F-CELL | A-core, A-CELL | M1 |
| 12 | CRYO_ASU | CRYO | cold_box | 3 | packed section, vacuum jacket | no | coarse internal, ~106 f | mfg_cold_box.scad | F-COL | A-core, A-COL | M1 |
| 13 | CRYO_O2 | CRYO | cold_box | 3 | packed section, vacuum jacket | no | coarse internal, ~106 f | none | F-COL | A-core, A-COL | M1 |
| 14 | CRYO_N2 | CRYO | cold_box | 3 | packed section, vacuum jacket | no | coarse internal, ~106 f | none | F-COL | A-core, A-COL | M1 |
| 15 | CRYO_AR | CRYO | cold_box | 3 | packed section, vacuum jacket | no | coarse internal, ~106 f | none | F-COL | A-core, A-COL | M1 |
| 16 | CRYO_H2 | CRYO | cold_box | 3 | packed section, vacuum jacket | no | coarse internal, ~106 f | none | F-COL | A-core, A-COL | M1 |
| 17 | CRYO_CO2 | CRYO | cold_box | 3 | packed section, vacuum jacket | no | coarse internal, ~106 f | none | F-COL | A-core, A-COL | M1 |
| 18 | CRYO_HE | CRYO | cold_box | 3 | packed section, vacuum jacket | no | coarse internal, ~106 f | none | F-COL | A-core, A-COL | M1 |
| 19 | CRYO_NE | CRYO | cold_box | 3 | packed section, vacuum jacket | no | coarse internal, ~106 f | none | F-COL | A-core, A-COL | M1 |
| 20 | CRYO_KR | CRYO | cold_box | 3 | packed section, vacuum jacket | no | coarse internal, ~106 f | none | F-COL | A-core, A-COL | M1 |
| 21 | CRYO_XE | CRYO | cold_box | 3 | packed section, vacuum jacket | no | coarse internal, ~106 f | none | F-COL | A-core, A-COL | M1 |
| 22 | BIOFILTER | FARM | farm | 3 | none | yes | envelope, ~23 f | mfg_biofilter.scad | F-FARM | A-core, A-FARM | M0 |
| 23 | ETOH_STILL | FARM | farm | 3 | none | yes | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 24 | BUOH_STILL | FARM | farm | 3 | none | yes | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 25 | HOPPER | OIL | hopper | 4 | none | no | envelope, ~11 f | mfg_hopper.scad | F-VES | A-core, A-VES | M0 |
| 26 | FLOAT_SINK | WET | separator | 4 | weir and launder | no | envelope, ~12 f | mfg_dewater.scad | F-VES | A-core, A-VES | M0 |
| 27 | NOX_SCRUB | GAS | scrubber | 4 | pall-ring bed, distributor, demister | yes | coarse internal, ~71 f | mfg_scrubber_train.scad | F-COL | A-core, A-COL | M1 |
| 28 | BLACK_DIGEST | WTR | digest | 4 | pitched-blade agitator | yes | envelope, ~23 f | none | F-VES | A-core, A-VES | M0 |
| 29 | CATCH_TANK | WTR | tank | 4 | dip pipe, stilling well | yes | envelope, ~23 f | none | F-VES | A-core, A-VES | M0 |
| 30 | CRYO_AHU_COND_CONDENSABLE | CRYO | separator | 4 | weir and launder | yes | envelope, ~12 f | none | F-VES | A-core, A-VES | M0 |
| 31 | CRYO_HX_Q4 | CRYO | hx | 4 | plate pack | yes | coarse internal, ~83 f | none | F-HX | A-core, A-HX | M1 |
| 32 | FAB_UPW_TANK | FAB | tank | 4 | dip pipe, stilling well | yes | envelope, ~23 f | none | F-VES | A-core, A-VES | M0 |
| 33 | FLUE_KO | GAS | separator | 4 | weir and launder | yes | envelope, ~11 f | none | F-VES | A-core, A-VES | M0 |
| 34 | GEO_ORC | GEO | hx | 4 | plate pack | yes | coarse internal, ~83 f | none | F-HX | A-core, A-HX | M1 |
| 35 | HX8 | WET | hx | 4 | plate pack | yes | coarse internal, ~83 f | none | F-HX | A-core, A-HX | M1 |
| 36 | MEOH_COND | ELEC | separator | 4 | weir and launder | yes | envelope, ~12 f | none | F-VES | A-core, A-VES | M0 |
| 37 | MEOH_TANK | MEOH | tank | 4 | dip pipe, stilling well | yes | envelope, ~23 f | none | F-VES | A-core, A-VES | M0 |
| 38 | MET_HX_Q4 | MFG | hx | 4 | plate pack | yes | coarse internal, ~83 f | none | F-HX | A-core, A-HX | M1 |
| 39 | MET_SCRUB | MFG | scrubber | 4 | pall-ring bed, distributor, demister | yes | coarse internal, ~71 f | none | F-COL | A-core, A-COL | M1 |
| 40 | PROD_C11_C18 | OIL | cut_tank | 4 | dip pipe, stilling well | yes | envelope, ~12 f | none | F-VES | A-core, A-VES | M0 |
| 41 | PROD_C19_C28 | OIL | cut_tank | 4 | dip pipe, stilling well | yes | envelope, ~12 f | none | F-VES | A-core, A-VES | M0 |
| 42 | PROD_C29 | OIL | cut_tank | 4 | dip pipe, stilling well | yes | envelope, ~12 f | none | F-VES | A-core, A-VES | M0 |
| 43 | PROD_C5_C10 | OIL | cut_tank | 4 | dip pipe, stilling well | yes | envelope, ~12 f | none | F-VES | A-core, A-VES | M0 |
| 44 | Q1_A | HEAT | heat_battery | 4 | stratification plate | yes | envelope, ~11 f | none | F-HX | A-core, A-HX | M0 |
| 45 | Q1_B | HEAT | heat_battery | 4 | stratification plate | yes | envelope, ~11 f | none | F-HX | A-core, A-HX | M0 |
| 46 | Q2_A | HEAT | heat_battery | 4 | stratification plate | yes | envelope, ~11 f | none | F-HX | A-core, A-HX | M0 |
| 47 | Q2_B | HEAT | heat_battery | 4 | stratification plate | yes | envelope, ~11 f | none | F-HX | A-core, A-HX | M0 |
| 48 | Q3_A | HEAT | heat_battery | 4 | stratification plate | yes | envelope, ~11 f | none | F-HX | A-core, A-HX | M0 |
| 49 | Q3_B | HEAT | heat_battery | 4 | stratification plate | yes | envelope, ~11 f | none | F-HX | A-core, A-HX | M0 |
| 50 | Q4_A | HEAT | heat_battery | 4 | stratification plate | yes | envelope, ~11 f | none | F-HX | A-core, A-HX | M0 |
| 51 | Q4_B | HEAT | heat_battery | 4 | stratification plate | yes | envelope, ~11 f | none | F-HX | A-core, A-HX | M0 |
| 52 | REMIN | WTR | tank | 4 | dip pipe, stilling well | yes | envelope, ~11 f | none | F-VES | A-core, A-VES | M0 |
| 53 | ZNBR2_BR2_REGEN | ELEC | scrubber | 4 | pall-ring bed, distributor, demister | yes | coarse internal, ~71 f | none | F-COL | A-core, A-COL | M1 |
| 54 | ACID_POLISH_SCRUB | GAS | scrubber | 4 | pall-ring bed, distributor, demister | no | coarse internal, ~71 f | mfg_scrubber_train.scad | F-COL | A-core, A-COL | M1 |
| 55 | ALK_SCRUBBER | GAS | scrubber | 4 | pall-ring bed, distributor, demister | no | coarse internal, ~71 f | mfg_scrubber_train.scad | F-COL | A-core, A-COL | M1 |
| 56 | GLASS_DIGEST | GLASS | digest | 4 | pitched-blade agitator | no | envelope, ~23 f | mfg_digest.scad | F-VES | A-core, A-VES | M0 |
| 57 | CURTAIL | GEO | hx | 4 | plate pack | no | coarse internal, ~83 f | none | F-HX | A-core, A-HX | M1 |
| 58 | HEAT_SINK | GEO | hx | 4 | plate pack | no | coarse internal, ~83 f | none | F-HX | A-core, A-HX | M1 |
| 59 | LIGNO_PRE | FARM | tank | 4 | dip pipe, stilling well | no | envelope, ~23 f | none | F-VES | A-core, A-VES | M0 |
| 60 | ROOF_TANK | WTR | tank | 4 | dip pipe, stilling well | no | envelope, ~23 f | none | F-VES | A-core, A-VES | M0 |
| 61 | GLASS_BURNOUT | GLASS | intra | 5 | none | yes | envelope, ~12 f | mfg_burnout_rotary.scad | F-PIPE | A-PIPE | M0 |
| 62 | GLASS_MILL | GLASS | intra | 5 | none | yes | envelope, ~12 f | mfg_mill.scad | F-PIPE | A-PIPE | M0 |
| 63 | GLASS_RINSE | GLASS | intra | 5 | none | yes | envelope, ~12 f | mfg_rinse.scad | F-PIPE | A-PIPE | M0 |
| 64 | C29_RECYCLE | OIL | recycle_pipe | 5 | pipe only | yes | envelope, ~12 f | none | F-PIPE | A-PIPE | M0 |
| 65 | CONTINUOUS_RECYCLE | WET | recycle_pipe | 5 | pipe only | yes | envelope, ~12 f | none | F-PIPE | A-PIPE | M0 |
| 66 | NCG_HEADER | OIL | header | 5 | pipe only | yes | envelope, ~12 f | none | F-PIPE | A-PIPE | M0 |
| 67 | Q4_BUS | HAB | header | 5 | pipe only | yes | envelope, ~11 f | none | F-PIPE | A-PIPE | M0 |
| 68 | RELIEF_CRYO | CRYO | relief | 5 | none | yes | envelope, ~12 f | none | F-PIPE | A-PIPE | M0 |
| 69 | RELIEF_H2 | GAS | relief | 5 | none | yes | envelope, ~12 f | none | F-PIPE | A-PIPE | M0 |
| 70 | TERRACE_IRRIG | TRR | header | 5 | pipe only | yes | envelope, ~12 f | none | F-PIPE | A-PIPE | M0 |
| 71 | AFTERBURNER_FLUE | WET | header | 5 | pipe only | no | envelope, ~12 f | none | F-PIPE | A-PIPE | M0 |
| 72 | HDR_CO2 | HAB | header | 5 | pipe only | no | envelope, ~11 f | none | F-PIPE | A-PIPE | M0 |
| 73 | HDR_H2 | GAS | header | 5 | pipe only | no | envelope, ~11 f | none | F-PIPE | A-PIPE | M0 |
| 74 | HDR_N2 | HAB | header | 5 | pipe only | no | envelope, ~11 f | none | F-PIPE | A-PIPE | M0 |
| 75 | HDR_O2 | GAS | header | 5 | pipe only | no | envelope, ~11 f | none | F-PIPE | A-PIPE | M0 |
| 76 | HDR_UPW | WTR | header | 5 | pipe only | no | envelope, ~11 f | none | F-PIPE | A-PIPE | M0 |
| 77 | BMED_UPW_POLISH | WTR | skid | 6 | none | yes | envelope, ~12 f | none | F-MACH | A-core, A-MACH | M0 |
| 78 | GEO_GHEX | GEO | ghex | 6 | none | yes | envelope, ~12 f | none | F-HX | A-core, A-HX | M0 |
| 79 | GEO_HP | GEO | heat_pump | 6 | none | yes | envelope, ~11 f | none | F-HX | A-core, A-HX | M0 |
| 80 | GEO_HP_CLOSED_LOOP | GEO | thermal | 6 | none | yes | envelope, ~12 f | none | F-HX | A-core, A-HX | M0 |
| 81 | GREY_TREAT | WTR | treat | 6 | none | yes | envelope, ~12 f | none | F-VES | A-core, A-VES | M0 |
| 82 | MEOH_FERM | MEOH | ferment | 6 | none | yes | envelope, ~12 f | none | F-VES | A-core, A-VES | M0 |
| 83 | MEOH_SYNTH | MEOH | reactor | 6 | none | yes | envelope, ~12 f | none | F-VES | A-core, A-VES | M0 |
| 84 | MET_AHU | MFG | ahu | 6 | none | yes | envelope, ~11 f | none | F-HX | A-core, A-HX | M0 |
| 85 | S13_CLASS_TREAT | WET | treat | 6 | none | yes | envelope, ~12 f | none | F-VES | A-core, A-VES | M0 |
| 86 | VCD_TRAIN | WTR | vessel | 6 | none | yes | envelope, ~12 f | none | F-VES | A-core, A-VES | M0 |
| 87 | WS_AMMONIA | FAB | reagent | 6 | none | yes | envelope, ~12 f | none | F-MACH | A-core, A-MACH | M0 |
| 88 | WS_DOPE | FAB | reagent | 6 | none | yes | envelope, ~11 f | none | F-MACH | A-core, A-MACH | M0 |
| 89 | WS_HF_ED | FAB | reagent | 6 | none | yes | envelope, ~12 f | none | F-MACH | A-core, A-MACH | M0 |
| 90 | WS_KOH | FAB | reagent | 6 | none | yes | envelope, ~11 f | none | F-MACH | A-core, A-MACH | M0 |
| 91 | WS_NITRIC | FAB | reagent | 6 | none | yes | envelope, ~12 f | none | F-MACH | A-core, A-MACH | M0 |
| 92 | WS_PEROX | FAB | reagent | 6 | none | yes | envelope, ~12 f | none | F-MACH | A-core, A-MACH | M0 |
| 93 | WS_PHOS | FAB | reagent | 6 | none | yes | envelope, ~11 f | none | F-MACH | A-core, A-MACH | M0 |
| 94 | WS_SLURRY | FAB | reagent | 6 | none | yes | envelope, ~12 f | none | F-MACH | A-core, A-MACH | M0 |
| 95 | WS_SOLV | FAB | reagent | 6 | none | yes | envelope, ~11 f | none | F-MACH | A-core, A-MACH | M0 |
| 96 | AFTERBURNER | OIL | thermal | 6 | none | no | envelope, ~12 f | mfg_afterburner.scad | F-HX | A-core, A-HX | M0 |
| 97 | BAGHOUSE | GAS | baghouse | 6 | none | no | envelope, ~12 f | mfg_baghouse.scad | F-MACH | A-core, A-MACH | M0 |
| 98 | BMED_ACID | WET | bmed | 6 | none | no | envelope, ~12 f | bmed_cell.scad, mfg_bmed_stack.scad | F-CELL | A-core, A-CELL | M0 |
| 99 | BMED_BASE | WET | bmed | 6 | none | no | envelope, ~12 f | bmed_cell.scad, mfg_bmed_stack.scad | F-CELL | A-core, A-CELL | M0 |
| 100 | CRU | WET | cru | 6 | none | no | envelope, ~11 f | mfg_cru.scad | F-VES | A-core, A-VES | M0 |
| 101 | H2_DRYER | GAS | dryer | 6 | none | no | envelope, ~12 f | mfg_h2_dryer.scad | F-MACH | A-core, A-MACH | M0 |
| 102 | NUTRIENT_DOSE | NUT | dose | 6 | none | no | envelope, ~12 f | mfg_nutrient_dose.scad | F-VES | A-core, A-VES | M0 |
| 103 | OIL_DRYER | OIL | dryer | 6 | none | no | envelope, ~12 f | mfg_dryer.scad | F-MACH | A-core, A-MACH | M0 |
| 104 | OIL_FRAC | OIL | frac | 6 | none | no | envelope, ~12 f | mfg_fractionator.scad | F-COL | A-core, A-COL | M0 |
| 105 | OIL_PYRO | OIL | pyro | 6 | none | no | envelope, ~12 f | mfg_induction_pyrolyzer.scad | F-MACH | A-core, A-MACH | M0 |
| 106 | CRYO_AHU | CRYO | ahu | 6 | none | no | envelope, ~12 f | none | F-HX | A-core, A-HX | M0 |
| 107 | CRYO_DED_COOL | CRYO | cool | 6 | none | no | envelope, ~12 f | none | F-HX | A-core, A-HX | M0 |
| 108 | EMETH | FARM | cell | 6 | none | no | envelope, ~11 f | none | F-CELL | A-core, A-CELL | M0 |
| 109 | POLISH_BANK | WET | polish | 6 | none | no | envelope, ~12 f | none | F-VES | A-core, A-VES | M0 |
| 110 | SALT_FEED | WET | feed | 6 | none | no | envelope, ~12 f | none | F-VES | A-core, A-VES | M0 |
| 111 | BLOW_MOLD | MFG | forming | 7 | none | yes | envelope, ~12 f | none | F-MACH | A-core, A-MACH, A-SC | M0 |
| 112 | ELECTRODE_COAT | MFG | tool | 7 | none | yes | envelope, ~12 f | none | F-MACH | A-core, A-MACH, A-SC | M0 |
| 113 | LITHO_ALIGN | FAB | tool | 7 | none | yes | envelope, ~12 f | none | F-MACH | A-core, A-MACH, A-SC | M0 |
| 114 | LITHO_COAT | FAB | tool | 7 | none | yes | envelope, ~12 f | none | F-MACH | A-core, A-MACH, A-SC | M0 |
| 115 | LITHO_DEV | FAB | tool | 7 | none | yes | envelope, ~12 f | none | F-MACH | A-core, A-MACH, A-SC | M0 |
| 116 | LITHO_STUB | FAB | tool | 7 | none | yes | envelope, ~12 f | none | F-MACH | A-core, A-MACH, A-SC | M0 |
| 117 | SIC_FURNACE | GLASS | melt | 7 | none | yes | envelope, ~23 f | none | F-VES | A-core, A-VES, A-SC | M0 |
| 118 | SOLAR_PV_CELL | FAB | tool | 7 | none | yes | envelope, ~12 f | none | F-MACH | A-core, A-MACH, A-SC | M0 |
| 119 | MET_MELT | MFG | melt | 7 | none | no | envelope, ~12 f | mfg_melt.scad | F-VES | A-core, A-VES, A-SC | M0 |
| 120 | WET_BENCH | FAB | wet_bench | 7 | none | no | envelope, ~12 f | mfg_wet_bench.scad | F-MACH | A-core, A-MACH, A-SC | M0 |
| 121 | BOARD_MILL | MFG | mill | 7 | none | no | envelope, ~12 f | none | F-MACH | A-core, A-MACH, A-SC | M0 |
| 122 | COLD_MILL | MFG | forming | 7 | none | no | envelope, ~12 f | none | F-MACH | A-core, A-MACH, A-SC | M0 |
| 123 | GAS_ATOMIZER | MFG | forming | 7 | none | no | envelope, ~12 f | none | F-MACH | A-core, A-MACH, A-SC | M0 |
| 124 | MFG_SHOP | MFG | shop | 7 | none | no | envelope, ~12 f | none | F-MACH | A-core, A-MACH, A-SC | M0 |
| 125 | WAFER_FAB | FAB | fab | 7 | none | no | envelope, ~12 f | none | F-MACH | A-core, A-MACH, A-SC | M0 |
| 126 | WIRE_DRAW | MFG | forming | 7 | none | no | envelope, ~12 f | none | F-MACH | A-core, A-MACH, A-SC | M0 |
| 127 | RECTIFIER | ELEC | rectifier | 8 | none | yes | envelope, ~12 f | mfg_electrical.scad | F-MACH | A-core, A-MACH | M0 |
| 128 | SOL_ARK_60K | ELEC | inverter | 8 | none | yes | envelope, ~12 f | mfg_electrical.scad | F-MACH | A-core, A-MACH | M0 |
| 129 | ZNBR2 | ZNBR2 | flow_battery | 8 | none | yes | envelope, ~11 f | znbr2_iem.scad, mfg_znbr2_skid.scad | F-CELL | A-core, A-CELL | M0 |
| 130 | BACKUP_GEN | BACKUP_GEN | genset | 8 | none | yes | envelope, ~12 f | none | F-MACH | A-core, A-MACH | M0 |
| 131 | BOUNDARY_EXPORT | DOCK | boundary | 8 | none | yes | envelope, ~12 f | none | none | A-ACC | accounting node. No solid |
| 132 | FUEL_CELL | FUEL_CELL | pem_fc | 8 | none | yes | envelope, ~12 f | none | F-CELL | A-core, A-CELL | M0 |
| 133 | LOAD_AGG | ELEC | boundary | 8 | none | yes | envelope, ~12 f | none | none | A-ACC | accounting node. No solid |
| 134 | MEOH_FC | MEOH | iem_fc | 8 | none | yes | envelope, ~11 f | none | F-CELL | A-core, A-CELL | M0 |
| 135 | PV_ARRAY | ELEC_PV | pv | 8 | none | yes | envelope, ~12 f | none | F-MACH | A-core, A-MACH | M0 |
| 136 | HYDRO_SET | PUMPED_HYDRO | hydro | 8 | none | no | envelope, ~12 f | none | F-MACH | A-core, A-MACH | M0 |
| 137 | NORTH_DOCK | DOCK | dock | 8 | none | no | envelope, ~12 f | none | F-MACH | A-core, A-MACH | M0 |
| 138 | ASH | FARM | farm | 9 | none | yes | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 139 | AZOLLA_BED | FARM | farm | 9 | none | yes | envelope, ~24 f | none | F-FARM | A-core, A-FARM | M0 |
| 140 | DUAL_ROOT | FARM | farm | 9 | none | yes | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 141 | IODIDE | FARM | farm | 9 | none | yes | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 142 | MISTER | FARM | farm | 9 | none | yes | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 143 | NFT | FARM | farm | 9 | none | yes | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 144 | QUAT | FARM | farm | 9 | none | yes | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 145 | SEED_BANK | FARM | farm | 9 | none | yes | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 146 | STRUVITE | FARM | farm | 9 | none | yes | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 147 | FISH | FARM | farm | 9 | none | no | envelope, ~23 f | mfg_fish_tank.scad | F-FARM | A-core, A-FARM | M0 |
| 148 | FISH_SUMP | FARM | farm | 9 | none | no | envelope, ~23 f | mfg_farm_sump.scad | F-FARM | A-core, A-FARM | M0 |
| 149 | GROW_BED | FARM | farm | 9 | none | no | envelope, ~23 f | mfg_grow_bed.scad | F-FARM | A-core, A-FARM | M0 |
| 150 | HABITATION | HAB | hab | 9 | none | no | envelope, ~12 f | mfg_hab_water.scad, mfg_hab_waste.scad | F-FARM | A-core, A-FARM | M0 |
| 151 | ABE | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 152 | ACETOX | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 153 | ACEX | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 154 | ALD | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 155 | AMF | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 156 | ANIMAL_PEN | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 157 | AZOLLA | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 158 | BEES | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 159 | BSFL | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 160 | BUCL | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 161 | CHICKENS | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 162 | CLARIFIER | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 163 | CLOVER | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 164 | COMPOST | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 165 | COMPOST_MYC | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 166 | COMPOST_TOILET | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 167 | CRAYFISH | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 168 | CROP_ALLIUM | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 169 | CROP_BASIL | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 170 | CROP_CUCUMBER | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 171 | CROP_KALE | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 172 | CROP_LETTUCE | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 173 | CROP_PEPPER | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 174 | CROP_ROSEMARY | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 175 | CROP_SPINACH | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 176 | CROP_TOMATO | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 177 | DIGESTER | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 178 | DUCKWEED | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 179 | FORM | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 180 | FRUIT_GUTTER | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 181 | GLYOXAL | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 182 | GOATS | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 183 | HAB_GALLEY | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 184 | HAB_MED | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 185 | HAB_SLEEP | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 186 | HAB_WASH | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 187 | HNO3 | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 188 | HTC | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 189 | IMID | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 190 | MEAM | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 191 | MUSHROOM | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 192 | MUSH_BLOCK | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 193 | MUSH_STRAW | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 194 | NFIX_BED | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 195 | PEANUT | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 196 | SUNFLOWER | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 197 | VEG_BED | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 198 | WORMS | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |
| 199 | YEAST | FARM | farm | 9 | none | no | envelope, ~23 f | none | F-FARM | A-core, A-FARM | M0 |

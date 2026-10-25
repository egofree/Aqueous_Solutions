# Surplus pass thresholds for the minimum viable system study

Document number: AQS-SUR-001  
Revision: D  
Date: 2026-10-25  
Authority: AQS-AUTH-001. The criteria for the minimum viable system are in AQS-UI-001 Rev C, sections 3.2 and 11.1. Other sources are listed in section 8. Not a PE stamp.

| Rev | Description | Date |
|---|---|---|
| A | First numeric study thresholds for food, water, goods and energy | 2026-10-01 |
| B | Seed model set to the upper end of the FARM food production band (S14 = 4.2 kg/d), so that the food surplus can meet the 0.5 kg/d threshold | 2026-10-01 |
| C | Sector names brought into line with graph revision AC (AQS-SEC-001 Rev H): WET became DIGESTER, and ELEC_PV became the PV_ARRAY unit in ELEC. No threshold changed. | 2026-10-24 |
| D | Rewritten to the documentation style guide (AQS-DOC-002). No threshold or driver changed. | 2026-10-25 |

Licence: CERN-OHL-S-2.0.

## 1. Purpose and scope

The plant is designed to produce more than it consumes, so that it can export food, clean water, goods and energy as well as support its own crew. The minimum viable system (MVS) is the smallest set of sectors that closes every mass, energy and life-support loop. AQS-UI-001, section 3.2, states that supporting the crew alone is not enough for the MVS: the plant must also export a surplus.

This page sets, for each of the four surplus products, the smallest daily export that counts as a pass in the current design study. These values are the study pass thresholds. The design tool's solver compares its calculated surplus against them and reports the result for each product. The page closes item 2 of AQS-UI-001, section 11.1.

The thresholds apply at the baseline scale, with the manufacturing scale factor `SCALE_M` equal to 1.0 and a crew of four. They are study values. They do not fix the design of the MVS (AQS-MVS-001), they are not taken from vendor nameplates, and no professional engineer (PE) has reviewed them. They stay study values until the number of crew berths, the site latitude and the number of wafer starts per day are fixed by the project.

This page does not set the berth count, map the solar resource at the site, or allow the solver to report that the loops are closed (`loops_closed = true`) or that the MVS design is fixed.

## 2. Where the thresholds are used

The thresholds are held in the model field `MvsCriteriaModel.surplus_thresholds` (`design_tool/aqs_design_tool/models.py`). The solver function `_surplus_stub` in `design_tool/aqs_design_tool/solver/stub.py` calculates each surplus and compares it with the threshold. If no threshold is set in the model, the function uses the values in Table 4.1.

For each product the solver reports `surplus.<key>.value`, the calculated study surplus, and `surplus.<key>.note`. The note includes `pass_study=true`, `pass_study=false` or `pass_study=unknown`. A surplus result alone never sets `mvs_equivalent=true` while any loop is open or any rate is incomplete (`rate_incomplete`).

## 3. Study inputs

Table 3.1 lists the inputs used to set the thresholds. Each is a study assumption. AQS-AUD-001 is a capacity study held in local planning files; it is not published in this repository.

Table 3.1. Study inputs

| Input | Study value | Source |
|---|---|---|
| Crew | 4 | Seed model and AQS-AUD-001 section 11; berth count not yet fixed |
| Manufacturing scale factor `SCALE_M` | 1.0 | AQS-SCALE-001 manufacturing baseline |
| Fresh food production | 1.4 kg/d to 4.2 kg/d; seed model midpoint 2.8 kg/d on stream S14 | AQS-AUD-001 section 12 |
| Food ration per crew member, as fresh-food equivalent | 0.6 kg per person per day | Study placeholder; not set by a nutritionist |
| Drinking and hygiene water | about 130 L/d | AQS-AUD-001 section 11 |
| FARM make-up water | about 50 L/d to 140 L/d | AQS-AUD-001 section 11 |
| Ultrapure water (UPW) make-up for FAB | 20 L/d to 100 L/d | AQS-AUD-001 section 11 |
| Wet feed | 150 kg/d | AQS-SCALE-001 |
| Plated metals | about 4.5 kg/d to 42 kg/d | AQS-AUD-001 |
| Electrical need and target (`ELEC_NEED`, `ELEC_TARGET`) | 50 kW and 70 kW | AQS-SCALE-001 section 9 |
| Peak sun hours | 4.0 h/d | Placeholder while the site latitude (`site_lat_deg`) is not set; not a statement about the climate |

## 4. Thresholds

Table 4.1 gives the threshold for each surplus product and how the solver calculates the surplus that is compared with it. Section 4.1 to section 4.4 explain each row.

Table 4.1. Study pass thresholds at `SCALE_M` = 1.0

| Surplus key | Unit | Pass threshold (minimum) | Surplus compared with the threshold |
|---|---|---|---|
| `food` | kg/d | 0.5 | Food produced on stream S14 less the crew ration: `max(0, S14 − crew × 0.6)` |
| `clean_water` | L/d (1 L/d is about 1 kg/d) | 50 | Water available for export above internal demand, when WTR is enabled |
| `materials_or_goods` | kg/d | 5.0 | Exportable metals, polymer and glass, when DIGESTER, MFG, FAB and GLASS are enabled |
| `energy` | kWh/d | 20 | `(ELEC_TARGET − ELEC_NEED) × peak sun hours` |

### 4.1 Food

At the midpoint of the production band, the food surplus is 2.8 kg/d less 2.4 kg/d for the crew, which is 0.4 kg/d. The threshold of 0.5 kg/d therefore needs either the upper end of the production band or a better crop yield. The stream S14 carries food from GROW_BED to FOOD_STORE.

The seed model uses the upper end of the band, S14 = 4.2 kg/d (AQS-AUD-001 section 12, band 1.4 kg/d to 4.2 kg/d). The study value for the food export stream S14X is the same residual. The study food export is then 4.2 kg/d less 4 × 0.6 kg/d, which is 1.8 kg/d, and the food surplus passes. A design study that uses the midpoint of 2.8 kg/d is valid but fails the threshold. The yield and the berth count are study assumptions; retune them when the berth count and the ration are fixed.

### 4.2 Clean water

The internal demand used in the study is 285 L/d: 130 L/d for drinking and hygiene, 95 L/d for FARM (the middle of its range) and 60 L/d for FAB (the middle of its range). The water held in the roof tank is much larger than this daily demand. The surplus passes if the make-up and storage margin is at least 50 L/d and the WTR sector is enabled.

The terrace irrigation stream S40 runs only when it is needed. The study does not assume a continuous flow on it.

### 4.3 Materials and goods

The study counts as exportable about one quarter of the midpoint plated-metal output, plus the continuous equivalent of the midpoint polymer output, plus a provisional glass value. When DIGESTER, MFG, FAB and GLASS are all enabled, the seed model uses a study envelope of 8 kg/d. A goods surplus needs both FAB and MFG (ruling A2 in AQS-SEC-001). The quantities are study values.

### 4.4 Energy

With 4 peak sun hours, the export margin is (70 kW − 50 kW) × 4 h/d, which is 80 kWh/d gross. The surplus passes at 20 kWh/d or more. Photovoltaic (PV) ratings are given at standard test conditions (STC), which are not continuous output. While the site latitude is not set, the solar resource is unknown, so this threshold is a study value only.

## 5. Unknowns

Table 5.1 lists the facts the thresholds depend on that are not yet known. Do not invent values for them.

Table 5.1. Unknowns and what they block

| Unknown | What it blocks |
|---|---|
| Number of crew berths and the food ration | Retuning the food threshold |
| Site latitude and typical meteorological year (TMY) solar data | Stating the energy surplus as a fact about the site |
| Wafer starts per day and glass output in kg/d | The size of the goods surplus |
| Power demand of the vapor-compression distillation (VCD) unit, and whether remineralization (REMIN) is in service | A claim that drinking water can be exported; water in storage is not the same as drinking water fit for export |
| A continuous flow on terrace stream S40 | Not needed; the stream runs on demand |

## 6. Next measurements and decisions

1. The project sets the berth count and the ration table.
2. The project sets the site latitude, so that the energy surplus can be stated for the site climate.
3. The equipment identifiers for VCD and REMIN are confirmed in service before any claim of drinking-water export.
4. The thresholds are retuned in a new revision of this page when the measurements are available. They keep the study label until the evidence for fixing the MVS design exists.

## 7. Regeneration

The solver results that use these thresholds are refreshed by the pipeline:

```bash
python3 -m flow_graph.param.regen
```

## 8. Related documents

Table 8.1. Related documents

| Document | Number | Role |
|---|---|---|
| `DESIGN_TOOL_ARCHITECTURE.md` | AQS-UI-001 | Sets the MVS criteria (section 3.2) and the open item closed by this page (section 11.1, item 2) |
| `SCALE_MODEL.md` | AQS-SCALE-001 | Scale factor, wet feed basis and electrical need and target |
| `AUTHORITY.md` | AQS-AUTH-001 | Authority for the CAD and design documents |
| `SECTOR_DEFINITIONS.md` | AQS-SEC-001 | Sector list and ruling A2 |
| Electrical requirement pages | AQS-REQ-KW-001, AQS-ELC-001 | Electrical demand basis |
| Stream register | AQS-STR-001 | Stream identifiers |
| Capacity study, local planning file, not published | AQS-AUD-001 | Production and demand bands (sections 4, 11 and 12) |
| Gap audit of the MVS plan, local planning file, not published | AQS-MVS-GAP-001 | Gap list (section 4.2) |

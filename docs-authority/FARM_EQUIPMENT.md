# Farm equipment and process list

Document number: AQS-EQP-FRM-001  
Revision: D  
Date: 2026-10-24  
Process flow diagrams: AQS-PFD-FRM-001 (`farm_pfd.png`); companions AQS-PFD-NUT-001 and AQS-PFD-TRR-001 (`terrace_irrigation_pfd.png`).  
Basis: `05-organic-farm-nutrient.md`; AQS-LIFE-001 §3 and §8; `freecad/farm.py`; AQS-STR-001; AQS-MF-001; AQS-SCALE-001 §9–10; AQS-TRR-001; AQS-WTR-001; AQS-PHF-001.  
Licence: CERN-OHL-S-2.0.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Basic issue with sector PFD generators | 2026-09-27 |
| B | 1 | Irrigation / terrace interfaces; unit duties; FreeCAD follow-up list | 2026-09-27 |
| C | 1 | Study food kg/d; grow trays FreeCAD | 2026-10-01 |
| D | 1 | Rewritten to DOC_STYLE (AQS-DOC-002) for a reader new to the project: purpose, scope and terms, captions; sections renumbered; working-log wording removed. Units, streams and rules unchanged. | 2026-10-24 |

## 1. Purpose and scope

The indoor farm grows food for the crew in an aquaponic loop: fish waste feeds a biofilter, the filtered water feeds plant beds under LED lighting, and the plants return food and oxygen. This page lists the farm units, the streams that enter and leave the farm block, the interfaces with the outdoor terrace irrigation, the open items and the planned FreeCAD work.

The outdoor overflow terraces are landscape, or optional greenhouse production, under AQS-TRR-001. They are not a second fish tank.

## 2. Terms

- Aquaponics: raising fish and plants in one water loop, the plants taking up the nutrients from the fish waste.
- Nitrification: the biofilter's conversion of ammonium (NH₄) to nitrite (NO₂) and nitrate (NO₃).
- Fertigation: adding nutrients to irrigation water.
- PPFD: photosynthetic photon flux density, the light reaching the plants, in µmol/(m² s).
- L1: building level 1.

Stream numbers (S01 and so on) are those of AQS-STR-001. Other abbreviations are in `docs-authority/GLOSSARY.md`.

## 3. Farm units (level 1 east plate)

The names match `freecad/farm.py`. When `LIFE_LEVELS` is greater than 1, units on further life plates take the suffix `_S2` and so on (Table 3.1).

Table 3.1. Farm units

| Tag | Duty | Interfaces | Notes |
|---|---|---|---|
| FISH_TANK | Aquaculture livestock; NH₄ source | Liquor → BIOFILTER; solids → digest / dose | No oxidizer storage in farm |
| BIOFILTER | Nitrification NH₄ → NO₂ → NO₃ | Liquor ↔ GROW_BED / FARM_SUMP | Media bed; no Salria |
| GROW_BED | Hydroponic / media beds; food + O₂ | S07 dose in; S14 food; S15 O₂; S11 waste | Photosynthetic O₂ → HDR_O2 |
| FARM_SUMP | Nutrient loop reservoir | S01/S21 makeup; S13 condensate out | Double-wall or drain to HDR_GREY only |
| NUTRIENT_DOSE | Struvite / NH₄ / chelates / pH trim | S07 in; dose to loop; optional terrace fertigation branch | See AQS-EQP-NUT-001 |
| LED_CANOPY | DC LED lighting over GROW_BED | S20 load; waste heat → Q4 | PPFD control per doc 05 §7.2 |

## 4. Streams of the farm block

Table 4.1. Streams

| ID | Role |
|---|---|
| S01 / S21 | UPW / roof clean makeup → FARM_SUMP |
| S03 | N₂ blanketing / purge as needed |
| S04 | CO₂ → grow air (CRYO + HAB AIR; never raw flue) |
| S06 | Q4 heat only into farm AHU |
| S07 | Dose salts in (precip + BMED) |
| S09 | BMED acid / base for pH trim (pipe; no sewer) |
| S11 | Plant / food waste → HOPPER / OIL |
| S12 | HAB waste liquor path toward dose / salt (companion) |
| S13 | Condensate → VCD / polish / salt (HDR_GREY) |
| S14 | Food totes → HAB |
| S15 | Photosynthetic O₂ → HDR_O2 |
| S20 | LED DC bus |
| S40 | Clean overflow / tower water → terrace irrigation (external) |
| S41 | Terrace clean drain → CATCH / DRAIN_SEC |
| S42 | Fertigated terrace / greenhouse drain → HDR_GREY (not CATCH) |

Not allowed on the level 1 farm headers: `HDR_ACID_GAS`, `HDR_H2`, `HDR_OIL_VAPOR`, or Salria into the beds. Dirty liquor never drains uphill into the farm (AQS-BLD-001 §3).

## 5. Interfaces with the terrace irrigation

Table 5.1. Terrace irrigation interfaces

| Interface | Direction | Rule |
|---|---|---|
| Clean surplus (S40) | Roof overflow path → terrace drip / flood bands | Clean tower water only; AQS-SCALE-001 §9–10 |
| Optional dilute fertigation | NUTRIENT_DOSE tote branch → enclosed greenhouse beds only | Never tee into ROOF_TANK / CATCH / S21 |
| Farm loop bleed | Not used as landscape irrigation | FARM_SUMP liquor is HDR_GREY chemistry |
| Potable S26 | Not used for terrace | Drinking remin path only (AQS-WTR-001) |
| Return clean (S41) | Band underdrain / apron → CATCH | Ornamental / rain + clean overflow only |
| Return fertigated (S42) | Greenhouse / food-bed drain → HDR_GREY → treat | Keep off roof–catch inventory |

The details, the rule for the climate option and the planting bands are in AQS-TRR-001.

## 6. Open items

1. A quantitative nutrient mass balance beyond the claim status in AQS-MF-001.
2. Duct sizes for the farm air handler (LIFE_FITOUT_PLAN §9, mechanical, electrical and plumbing).
3. FreeCAD solids for the irrigation headers and the greenhouse envelope (§7).

## 7. Planned FreeCAD work

The farm units of §3 are modelled. The terrace and greenhouse solids below are planned and not yet built. Building them does not require changing `SCALE_M`.

1. Planting media boxes and bed pans on `OVERFLOW_TERRACE_{S|N|E|W}_B{n}`.
2. Drip or flood irrigation header stubs (`TERRACE_IRRIG_HDR_*`) fed from `OVERFLOW_DOWNCOMER_*` or the spill path.
3. Underdrain collection to `OVERFLOW_APRON_*` and the tie to the catch tank (S41).
4. Optional enclosed greenhouse solids, set by the climate flag (AQS-TRR-001 §3): glazing and frame keep-out on the equator-facing bands first.
5. Greenhouse air-handler and vent stubs if the enclosed option is chosen: Q4 heat only, S04 carbon dioxide, no process gas.
6. A fertigation stub from `NUTRIENT_DOSE` only if the enclosed food option is chosen, with its drain stub to `HDR_GREY` (S42), never to the catch tank.
7. The baseline M1 model is rebuilt at `SCALE_M = 1` for release (AQS-SCALE-001 §11), separately from the terrace landscape pages.

## 8. Rebuilding the drawings

Run from the repository root:

```bash
cd flow_graph/exporters/matplotlib
python3 farm_pfd.py
python3 nutrient_pfd.py
python3 terrace_irrigation_pfd.py
```

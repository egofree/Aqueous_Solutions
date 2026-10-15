# Farm equipment / process list

Superseded copy. The current page is `docs-authority/FARM_EQUIPMENT.md`, C. This copy is history (AQS-REG-001).

Document number: AQS-EQP-FRM-001  
Revision: B  
Date: 2026-09-27  
PFD: AQS-PFD-FRM-001 (`farm_pfd.png`); companion AQS-PFD-NUT-001,
AQS-PFD-TRR-001 (`terrace_irrigation_pfd.png`)

Authority: `05-organic-farm-nutrient.md`, AQS-LIFE-001 §3 / §8,
`freecad/farm.py`, AQS-STR-001, AQS-MF-001, AQS-SCALE-001 §6–7,
AQS-TRR-001, AQS-WTR-001, AQS-PHF-001.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Basic issue with sector PFD generators | 2026-09-27 |
| B | 1 | Irrigation / terrace interfaces; unit duties; FreeCAD follow-up list | 2026-09-27 |

Licence: CERN-OHL-S-2.0.

---

## 1. Locked CAD units (L1 east plate)

Per-life-plate suffixes `_S2`… when `LIFE_LEVELS > 1`. Names match
`freecad/farm.py`.

| Tag | Duty | Interfaces | Notes |
|---|---|---|---|
| FISH_TANK | Aquaculture livestock; NH₄ source | Liquor → BIOFILTER; solids → digest / dose | No oxidizer storage in farm |
| BIOFILTER | Nitrification NH₄ → NO₂ → NO₃ | Liquor ↔ GROW_BED / FARM_SUMP | Media bed; no Salria |
| GROW_BED | Hydroponic / media beds; food + O₂ | S07 dose in; S14 food; S15 O₂; S11 waste | Photosynthetic O₂ → HDR_O2 |
| FARM_SUMP | Nutrient loop reservoir | S01/S21 makeup; S13 condensate out | Double-wall or drain to HDR_GREY only |
| NUTRIENT_DOSE | Struvite / NH₄ / chelates / pH trim | S07 in; dose to loop; optional terrace fertigation branch | See AQS-EQP-NUT-001 |
| LED_CANOPY | DC LED lighting over GROW_BED | S20 load; waste heat → Q4 | PPFD control per doc 05 §7.2 |

**NOTE**

Indoor FARM is the food / aquaponic loop. External overflow terraces are
landscape / optional greenhouse production under AQS-TRR-001 — not a
second FISH_TANK.

---

## 2. Streams (farm block)

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

Forbidden on L1 farm headers: HDR_ACID_GAS, HDR_H2, HDR_OIL_VAPOR,
Salria into beds. Dirty liquor never drains uphill into FARM
(AQS-BLD-001 §0).

---

## 3. Irrigation interfaces (to terrace)

| Interface | Direction | Rule |
|---|---|---|
| Clean surplus (S40) | Roof overflow path → terrace drip / flood bands | Clean tower water only; AQS-SCALE-001 §6–7 |
| Optional dilute fertigation | NUTRIENT_DOSE tote branch → enclosed greenhouse beds only | Never tee into ROOF_TANK / CATCH / S21 |
| Farm loop bleed | Not used as landscape irrigation | FARM_SUMP liquor is HDR_GREY chemistry |
| Potable S26 | Not used for terrace | Drinking remin path only (AQS-WTR-001) |
| Return clean (S41) | Band underdrain / apron → CATCH | Ornamental / rain + clean overflow only |
| Return fertigated (S42) | Greenhouse / food-bed drain → HDR_GREY → treat | Keep off roof–catch inventory |

Detail, climate option rule, and planting bands: AQS-TRR-001.

---

## 4. Open (later passes)

1. Quantitative nutrient mass balance beyond AQS-MF-001 claim status.
2. Farm AHU duct sizes (LIFE_FITOUT_PLAN §9 MEP).
3. FreeCAD solids for irrigation headers / greenhouse envelope — see §6
   (not this documentation pass).

---

## 5. Regenerate

```bash
cd flow_graph/exporters/matplotlib  # or local hub pfd_scripts/
python3 farm_pfd.py
python3 nutrient_pfd.py
python3 terrace_irrigation_pfd.py
```

---

## 6. FreeCAD follow-up (explicit — solids not this pass)

Do **not** rebuild `plant.FCStd` or change `SCALE_M` in this pass.
When a later CAD pass lands:

1. Planting media boxes / bed pans on `OVERFLOW_TERRACE_{S|N|E|W}_B{n}`.
2. Drip / flood irrigation header stubs (`TERRACE_IRRIG_HDR_*`) fed from
   `OVERFLOW_DOWNCOMER_*` / spill path.
3. Underdrain collection → `OVERFLOW_APRON_*` → CATCH tie (S41).
4. Optional enclosed greenhouse envelope solids gated by climate flag
   (see AQS-TRR-001 §3) — glazing / frame keep-out on equator-facing
   bands first.
5. Greenhouse AHU / vent stubs if enclosed option selected (Q4 only;
   S04 CO₂; no process gas).
6. Fertigation stub from `NUTRIENT_DOSE` only if enclosed food option
   is selected; drain stub to HDR_GREY (S42), never to CATCH.
7. Restore `SCALE_M=1` and rebuild baseline M1 when shipping
   (AQS-SCALE-001 §8) — separate from terrace landscape docs.

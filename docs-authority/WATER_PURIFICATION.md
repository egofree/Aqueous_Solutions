# Water purification — habitation and fab UPW

Document number: AQS-WTR-001  
Revision: B  
Date: 2026-10-01  
Authority: `SLINGSHOT/Water_Cycle_diagram.md`, `07-water-air-habitation.md`,
`03-silicon-wafer-fabrication.md`, AQS-BLD-001 §3, AQS-STR-001,
AQS-MF-001, AQS-LIFE-001 §5, AQS-GAP-001 §5 / §7.1.
Subordinate equipment lists: AQS-EQP-HAB-001, AQS-EQP-FAB-UPW-001.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | First issue. Habitation VCD + remineralization + grey/black; fab UPW train; SLINGSHOT keep/adapt/supersede | 2026-09-27 |

Licence: CERN-OHL-S-2.0.

---

## 0. Scope and naming

This note schedules **two purification trains** that the BLD stack had
named but not equipped:

1. **Habitation** — grey / black treatment, vapor-compression distillation
   (VCD), ED polish, remineralization, potable distribution.
2. **Wafer fab UPW** — polish of plant water to rinse resistivity / TOC
   targets for the wet bench.

**NOTE**

`polish_bank` / AQS-PFD polish sheets are **EW metal polish cells** after
EW-9. They are not potable or fab UPW. Locked water names in this note
use `UPW POLISH`, `HAB_ED_POLISH`, `FAB_UPW_POLISH`, `VCD_*`, and `REMIN`.

Roof–catch (S21–S23, AQS-PFD-WTR-001 / AQS-PFD-BLD-005) is the **clean
inventory and gravity tower**. It is not a regeneration process. VCD
regenerates distillate into that inventory. Both shall appear on campus
water sheets.

Quantitative mass rates stay **TBD** unless already locked in AQS-MF-001
or a root doc citation below. Do not invent balances.

---

## 1. What already covers vs what is new

| Layer | Already present | New in Rev A |
|---|---|---|
| Clean inventory | ROOF TANK, CATCH TANK, SHAFT_PENSTOCK, S21–S23 | — |
| Dirty returns | S12 HDR_GREY / HDR_ORG; S10 HDR_ETCH; S13 condensate | Grey / black unit ops before those headers |
| Core salts / acids | BMED, CRU, S07 nutrient dose, S09 acid/base | REMIN draw of Ca/Mg/K for drinking (separate from S07 farm path) |
| Named UPW node | “UPW POLISH” on campus / water PFDs; S01 < 1 µS/cm claim | Equipment schedule: VCD → ED polish → (remin \| fab polish) |
| Hab CAD | HAB_WATER, HAB_WASTE, WETROOM | POTABLE / GREY_TREAT / BLACK_DIGEST / VCD_* / REMIN tags |
| Fab CAD | WET_BENCH, ETCH_RETURN; S01 stub | FAB_UPW_POLISH train + S27 product |
| SLINGSHOT VCD + remin | Missing (AQS-GAP-001) | Kept and adapted into BLD stack (see §7) |
| Root-07 MED narrative | Narrative only | Adapted as grey/black membrane ED stage ahead of / beside VCD |

---

## 2. Habitation train

### 2.1 Topology (qualitative)

```
Clean condensates (S13: farm sump + HVAC)
        │
        ▼
   ┌────────────┐     grey treat product (S29)
   │  VCD_FEED  │◄──── black digest liquor (optional dilute; preferred S30 → nutrient)
   └─────┬──────┘
         ▼
   VCD_HX  →  VCD_EVAP  →  VCD_COMP  →  VCD_COND
         │                      │
         ▼                      ▼
    VCD brine (S28)        distillate (S25)
    → REGEN LEACH /           │
      SALT FEED               ▼
                        HAB_ED_POLISH / UPW POLISH
                        (BMED middle-chamber assist)
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
         HDR_UPW / S01   REMIN (Ca Mg K)   FAB_UPW feed
         (farm / fab     → potable S26     (pre-remin)
          pre-remin)       → HAB taps
```

Grey and black collection stay on HAB_WASTE → treatment units →
HDR_GREY / HDR_ORG as today. Dirty streams do **not** feed VCD as the
primary path (SLINGSHOT rule retained). Backup dirty feed to VCD is
allowed only through a screened buffer labeled as contingency — not the
normal operating line.

### 2.2 Grey water

| Tag | Duty |
|---|---|
| GREY_SCREEN | Solids / grease capture from wetroom + galley rinse |
| GREY_BIO | Biological polish (BOD / FOG); air from HAB_AIR, not process aisle |
| GREY_MED | Membrane electrodialysis stage (root-07 MED duty for grey) |
| GREY_BUFF | Buffer before VCD feed (S29) or SALT FEED if off-spec |

Return: treated grey → S29 → VCD_FEED (preferred) or SALT FEED.
Never to Salria, HDR_ETCH, or storm.

### 2.3 Black water

| Tag | Duty |
|---|---|
| BLACK_COLLECT | Toilet collect; optional urine diversion |
| BLACK_DIGEST | Anaerobic / aerobic digester; solids → HDR_ORG / HOPPER |
| BLACK_MED | Nutrient-lean liquor polish (root-07 MED / nutrient stage) |

Liquor → S30 → NUTRIENT DOSE / SALT FEED (struvite path aligned with
S07 chemistry). Solids never enter VCD evaporators.

**CAUTION**

Human waste solids do not enter LEACH without AHJ review
(AQS-LIFE-001 §6). Prefer nutrient / digest path.

### 2.4 VCD (kept from SLINGSHOT)

| Tag | Duty |
|---|---|
| VCD_HX | Counterflow feed / distillate heat recovery (Slingshot energy recovery) |
| VCD_EVAP | Evaporator; vapor out; brine out (S28) |
| VCD_COMP | Vapor compressor (DC bus / module parasitics) |
| VCD_COND | Condenser; distillate (S25) |
| VCD_FEED | Clean condensate + S29 buffer |

Primary feed: clean condensates (S13) and treated grey (S29).
Brine (S28) → REGEN LEACH or SALT FEED — same “concentrate to oxidative
leach” intent as SLINGSHOT. Distillate is not potable until ED polish
and, for drinking, remineralization.

Energy: SLINGSHOT 5–10 kW allocation is **superseded** by module
parasitics (AQS-GAP-001). Name the compressor load on the electrical
one-line later; do not hard-code kilowatts here.

### 2.5 ED polish and remineralization

| Tag | Duty |
|---|---|
| HAB_ED_POLISH / UPW POLISH | Distillate → < 1 µS/cm class water (S01 claim); BMED middle-chamber integration as assist, not a second wet-line stack |
| REMIN | Dose Ca²⁺, Mg²⁺, K⁺ (and related) from core salt inventory into drinking water |
| POTABLE_TANK | Remineralized drinking water holdup |
| HAB_BOOST | Distribution booster after gravity-first roof feed (secondary) |

Remineralization is **for drinking only**. Farm nutrient dose remains
S07 (P-Al / P-Mg / P-Ca + BMED salts). Do not tee REMIN product into
grow beds as fertilizer, and do not use S07 totes as the potable
mineral source without a dedicated food-grade path.

Potable finishing after remin (root-07): UF/NF integrity check + UV
sterilization at HAB_WATER point-of-use as required for microbiological
safety. Residual disinfectant target remains a permit decision (TBD).

### 2.6 Potable quality (grounded)

| Parameter | Target | Source |
|---|---|---|
| Conductivity (pre-remin UPW) | < 1 µS/cm | S01 / SLINGSHOT / AQS-STR-001 |
| Potable TDS (post-remin) | < 50 mg/L class | Root 07 §10.3 |
| Turbidity | < 0.1 NTU product | Root 07 §10.3 |
| pH (potable) | 6.5–8.5 | Root 07 §10.3 |
| UV dose | ≥ 40 mJ/cm² @ 254 nm | Root 07 §10.3 |
| Mass rates | Study §8 (AUD §11) | Labeled study — not permit demand |

Backflow: air gap or RPZ on HDR_UPW at potable (AQS-HSE-001 / AQS-MF-001).

---

## 3. Wafer fab UPW train

### 3.1 Topology

```
Plant water (S21 roof and/or S01 HDR_UPW, pre-remin)
        │
        ▼
  FAB_UPW_PRE  →  FAB_UPW_UF  →  FAB_UPW_IX / EDI  →  FAB_UPW_UV  →  FAB_UPW_TANK
                                                                      │
                                                                      ▼
                                                              WET_BENCH (S27)
                                                                      │
                                                    rinse reject ──────┤
                                                                      ▼
                                              clean reject → HDR_GREY / SALT FEED
                                              etch-laden → HDR_ETCH (S10 path)
```

Fab UPW takes **pre-remin** plant water. Remineralized potable shall not
feed the wet bench (minerals defeat resistivity).

### 3.2 Equipment tags

| Tag | Duty |
|---|---|
| FAB_UPW_PRE | Particulate / carbon prefilter |
| FAB_UPW_UF | Ultrafiltration |
| FAB_UPW_IX | Mixed-bed ion exchange and/or EDI polish |
| FAB_UPW_UV | TOC / microbial UV |
| FAB_UPW_TANK | Recirculating UPW loop to WET_BENCH |
| FAB_UPW_REJECT | Segregated reject header (see §3.4) |

### 3.3 Quality targets

Doc 03 rinse-station control (authority for fab water analytics):

| Parameter | Target | Label |
|---|---|---|
| Resistivity | > 18 MΩ·cm | Doc 03 rinse target |
| TOC | < 5 ppb | Doc 03 rinse target |
| Particles > 0.5 µm | < 100 / L | Doc 03 rinse target |
| Conductivity (plant S01 feed) | < 1 µS/cm class | AQS-STR-001 S01 |

Where a full SEMI Type E-1 suite is implied but not enumerated in doc 03
(dissolved silica, boron, metals), mark **industry-class placeholder —
TBD** on the equipment list. Do not invent numeric limits beyond doc 03
and S01.

### 3.4 Reject and return

| Stream | Destination | Forbidden |
|---|---|---|
| Clean UF/IX reject | HDR_GREY / SALT FEED / VCD_FEED if conductivity allows | Sewer, farm beds, Salria |
| Etch / HF-bearing rinse | HDR_ETCH → REGEN LEACH (S10) | Floor drain, HDR_GREY, hab |
| Spent wet-bench baths | S10 closed | Same |

---

## 4. Stream IDs (AQS-STR-001 extension)

Existing (unchanged duty):

| ID | Role in this note |
|---|---|
| S01 | Post-ED UPW on HDR_UPW → FARM, FAB feed, HAB pre-remin |
| S10 | Etch return |
| S12 | Hab waste collect |
| S13 | Condensate → VCD / SALT FEED |
| S21–S23 | Roof–catch clean inventory |

New (Rev A):

| ID | From | To | Ph | Carries | Header | Forbidden |
|---|---|---|---|---|---|---|
| S25 | VCD_COND | UPW POLISH / HAB_ED_POLISH | L | distillate | process UPW | potable taps without remin + UV |
| S26 | REMIN / POTABLE_TANK | HAB taps (HAB_WATER) | L | remineralized potable | potable branch + RPZ | process wet bench, etch |
| S27 | FAB_UPW_TANK | WET_BENCH | L | fab UPW > 18 MΩ·cm class | fab UPW loop | remin path, grey |
| S28 | VCD_EVAP | REGEN LEACH / SALT FEED | L | VCD brine | process | HDR_UPW, farm beds |
| S29 | GREY_TREAT | VCD_FEED / SALT FEED | L | treated grey | HDR_GREY branch | Salria, etch |
| S30 | BLACK_DIGEST | NUTRIENT DOSE / SALT FEED | L/S | digest liquor / nutrients | dose / HDR_ORG | VCD evaporators (solids), sewer |

S01 remains the shared plant UPW header. S26 is the drinking branch
after remin. S27 is the fab loop after dedicated polish.

---

## 5. Interfaces

| Interface | Habitation | Fab UPW |
|---|---|---|
| Farm | S13 condensate in; S01 / S21 makeup out; S30 nutrients toward S07 | No direct farm tie |
| Wet line / BMED | S28 brine; ED assist from BMED middle; S09 not for potable | S09 acids/bases to bench only; S10 return |
| Cryo | No direct water tie this pass (condensate if any → S13) | S03 N₂ purge on tools (unchanged) |
| Roof / catch | S21 gravity to HAB_WATER; product water may refill roof via clean path | S21 / S01 feed; no roof contamination from reject |
| Power | VCD_COMP + pumps on module bus (kW TBD) | Recirc pumps + UV (kW TBD) |
| Fuel-cell water | Deferred — no FC in CAD (AQS-GAP-001) | — |

---

## 6. Building placement (qualitative)

| Unit group | Preferred level / zone |
|---|---|
| GREY_* / BLACK_* / HAB_WATER / REMIN | L1 west (HABITATION) + CORE_LIFE util |
| VCD_* / UPW POLISH | L1 / L0 util near CORE — not inside SLEEP |
| FAB_UPW_* | L0 WAFER_FAB cassette or adjacent util chase |
| ROOF / CATCH | Unchanged (L2 / L-2) |

Dirty liquor does not drain uphill into life (AQS-BLD-001 §0).

---

## 7. SLINGSHOT decision table

| SLINGSHOT element | Decision | BLD disposition |
|---|---|---|
| Clean condensate collection (farm / HVAC / gas / FC) | **Keep** | S13; FC product water deferred until FC exists |
| Dirty black/grey + fab rinses → core / leach (primary) | **Keep** | S12 / S10; grey/black treat then leach/salt — not VCD-primary |
| Dirty backup into clean condensate | **Adapt** | Contingency only via GREY_BUFF; not normal ops |
| Roof tank / catch / penstock | **Keep** (already Present) | Inventory architecture; does **not** replace VCD regeneration |
| VCD (HX → evaporate → compress → condense) | **Keep** | Tags VCD_HX / VCD_EVAP / VCD_COMP / VCD_COND |
| ED polish + core middle chamber | **Adapt** | HAB_ED_POLISH / UPW POLISH; BMED assist; S01 claim retained |
| Remineralization (Ca / Mg / K from core) | **Keep** | REMIN + S26; separate from S07 farm dose |
| Ultra-pure tank < 1 µS/cm | **Keep** | S01 / UPW POLISH holdup; fab further polishes to S27 |
| Drinking water tank | **Keep** | POTABLE_TANK |
| Distribution pumps to FAB / MFG / HAB | **Adapt** | Gravity-first from ROOF (S21); HAB_BOOST / fab recirc secondary |
| 5–10 kW fresh-water allocation | **Supersede** | Module parasitics / ELECTRICAL.md |
| Root-07 MED as sole potable regenerator | **Adapt** | MED used on grey/black; VCD is primary distillate regenerator; NF/UV finish potable |

**CAUTION**

AQS-PFD-WTR-001 remains the roof–catch sheet. Regeneration detail lives
on AQS-PFD-HAB-WTR-001 and AQS-PFD-FAB-UPW-001. Do not treat the roof
PNG as evidence that VCD was deleted.

---

## 8. Sheets and regenerate

| Doc | Script | PNG |
|---|---|---|
| AQS-WTR-001 | this file | — |
| AQS-EQP-HAB-001 | `cad/process/HAB_WATER.md` | — |
| AQS-EQP-FAB-UPW-001 | `cad/process/FAB_UPW.md` | — |
| AQS-PFD-HAB-001 | `habitation_pfd.py` | `habitation_pfd.png` |
| AQS-PFD-HAB-WTR-001 | `hab_water_pfd.py` | `hab_water_pfd.png` |
| AQS-PFD-FAB-001 | `wafer_fab_pfd.py` | `wafer_fab_pfd.png` |
| AQS-PFD-FAB-UPW-001 | `fab_upw_pfd.py` | `fab_upw_pfd.png` |
| AQS-PFD-WTR-001 | `campus_life_hazard_pfds.py` (`water`) | `water_cycle_pfd.png` |

```bash
cd flow_graph/exporters/matplotlib  # or local hub pfd_scripts/
python3 hab_water_pfd.py
python3 fab_upw_pfd.py
python3 habitation_pfd.py
python3 wafer_fab_pfd.py
python3 campus_life_hazard_pfds.py
```

No SCALE_M change. No FreeCAD rebuild this pass.

---

## 9. Open / next forks

1. ~~Crystal forge → cut and wet-line reagent forks~~ — Done AQS-REM-BLD Rev I;
   solar-cell branch still open.
2. Fuel-cell product water into S13 when FC chemistry is chosen.
3. Quantitative VCD / UPW mass–energy balance (pilot numbers from root 07 only after scale lock).
4. ~~Terrace irrigation from clean overflow only~~ — Done AQS-TRR-001
   (S40 primary; S41→CATCH; S42 fertigated≠CATCH).
5. SCALE_M=1 restore when shipping baseline M1 again.


## 8. Study L/d balance (SCALE_M = 1.0)

Authority cross-ref: AQS-AUD-001 Rev D §11. **Study assumptions** —
crew = 4 persons (issued berth count TBD); GROW_BED ≈ 28 m².

| Loop | Study L/d | Notes |
|---|---|---|
| Potable S26 | ~130 | 4 × (2.5 drink + 30 hygiene) |
| Grey → VCD/treat | ~100–120 | Return fraction of hygiene |
| FAB UPW makeup | ~20–100 | Pending wafer/d; loop 200–500 L |
| FARM makeup | ~50–140 | 28 m² × 2–5 L/m²·d |
| Terrace S40 | Event-driven | No continuous nameplate |

Roof–catch inventory ≫ daily use (200 m³ min). VCD regeneration remains
required alongside inventory (this document §1).

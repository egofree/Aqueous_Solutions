# Nutrient dose / N-P process list

Document number: AQS-EQP-NUT-001  
Revision: B  
Date: 2026-09-27  
PFD: AQS-PFD-NUT-001 (`nutrient_pfd.png`); companion AQS-PFD-FRM-001,
AQS-PFD-TRR-001

Authority: `05-organic-farm-nutrient.md`, wet-line P-Al/P-Mg/P-Ca,
AQS-STR-001 S07/S12/S13/S30/S42, `freecad/farm.py` NUTRIENT_DOSE,
AQS-TRR-001, AQS-WTR-001.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Basic issue with sector PFD generators | 2026-09-27 |
| B | 1 | Terrace / greenhouse fertigation branch; S42 drain rule | 2026-09-27 |

Licence: CERN-OHL-S-2.0.

---

## 1. Units

| Tag | Duty |
|---|---|
| P-Al / P-Mg / P-Ca | Wet-line precip cakes (not electrowon fertilizer) |
| BMED SALTS | NH₄ / Na residual / chelating stock |
| NUTRIENT_DOSE | Dose hub — struvite, NH₄, chelates, pH trim |
| FISH_TANK / BIOFILTER / GROW_BED / FARM_SUMP | Aquaponic N loop (indoor FARM) |
| TERRACE_FERT (optional) | Dilute tote branch to **enclosed** terrace greenhouse beds only |

---

## 2. Streams

| ID | Status (AQS-MF-001) | Role |
|---|---|---|
| S07 | Closed | Precip + BMED salts → dose |
| S12 | Closed | HAB waste liquor path |
| S13 | Closed | Farm condensate → polish / salt / VCD |
| S30 | Closed | Black digest → nutrient / salt |
| S42 | Closed / Claimed | Fertigated terrace drain → HDR_GREY (not CATCH) |

Open-terrace clean irrigation is **S40** (tower overflow) — not a
nutrient stream. Do not mark S40 as consuming S07.

---

## 3. Rules

1. No Salria into GROW BED or terrace media.
2. No Li / REE aqueous EW as fertilizer path.
3. No invented kg/d balances — cite MASS_FLOW / STREAM_REGISTER only.
4. Remineralization for drinking (S26) is separate from S07 farm dose
   (AQS-WTR-001).
5. **Terrace nutrient use:** only when AQS-TRR-001 selects the enclosed
   greenhouse option for food production. Dilute from NUTRIENT_DOSE;
   drain on S42. Open landscape bands use clean overflow (S40) and
   optional solid compost / mulch from S11 paths — not continuous
   fertigation into grade.
6. Never tee nutrient liquor into ROOF_TANK, CATCH, or OVERFLOW_DOWNCOMER.

---

## 4. Regenerate

```bash
cd Diagrams/aqueous_diagrams/pfd_scripts
python3 nutrient_pfd.py
python3 terrace_irrigation_pfd.py
```

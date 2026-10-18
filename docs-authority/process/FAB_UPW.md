# Fab UPW — equipment list

Superseded copy. The current page is `docs-authority/FAB_UPW.md`, B. This copy is history (AQS-REG-001).

Document number: AQS-EQP-FAB-UPW-001  
Revision: B  
Date: 2026-09-27  
PFD: AQS-PFD-FAB-UPW-001 (`fab_upw_pfd.png`); parent sector
AQS-PFD-FAB-001 (`wafer_fab_pfd.png`)

Authority: AQS-WTR-001, `03-silicon-wafer-fabrication.md`,
AQS-EQP-FAB-001, AQS-STR-001, AQS-MF-001.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | First issue with AQS-WTR-001 fab train | 2026-09-27 |
| B | 1 | Point forge/reagent authority to FAB-001 Rev B / FAB-RGN-001 | 2026-09-27 |

## 1. Duty

Polish **pre-remin** plant water (S01 / S21) to wet-bench rinse quality.
Remineralized potable (S26) shall not feed this train.

## 2. Equipment

| Tag | Duty |
|---|---|
| FAB_UPW_PRE | Particulate / carbon prefilter |
| FAB_UPW_UF | Ultrafiltration |
| FAB_UPW_IX | Mixed-bed IX and/or EDI |
| FAB_UPW_UV | TOC / microbial UV |
| FAB_UPW_TANK | Recirculating loop to WET_BENCH (S27) |
| FAB_UPW_REJECT | Segregated reject (clean vs etch-laden) |

## 3. Quality targets

| Parameter | Target | Source |
|---|---|---|
| Resistivity | > 18 MΩ·cm | Doc 03 rinse-station control |
| TOC | < 5 ppb | Doc 03 |
| Particles > 0.5 µm | < 100 / L | Doc 03 |
| Feed conductivity | < 1 µS/cm class | S01 / AQS-STR-001 |
| Dissolved silica / boron / metals suite | TBD | Industry-class placeholder — not invented here |

Mass rates: TBD (no invented balance).

## 4. Streams

| ID | Role |
|---|---|
| S01 / S21 | Plant UPW / roof feed (pre-remin) |
| S27 | Fab UPW product → WET_BENCH |
| S10 | Etch-laden reject / spent baths → REGEN LEACH |
| S09 | HCl / NaOH to bench (not UPW minerals) |
| S03 | N₂ purge on tools |

Clean UF/IX reject → HDR_GREY / SALT FEED / VCD_FEED if conductivity
allows. Never sewer, Salria, or farm beds.

## 5. Naming

EW `POLISH BANK` ≠ `FAB_UPW_*` ≠ `WS_*` synth forks. Crystal forge →
cut and wet-line reagent forks: AQS-EQP-FAB-001 Rev B +
AQS-EQP-FAB-RGN-001 (closed doc/PFD; CAD solids TBD).

## 6. Regenerate

```bash
cd flow_graph/exporters/matplotlib  # or local hub pfd_scripts/
python3 fab_upw_pfd.py
python3 wafer_fab_pfd.py
```

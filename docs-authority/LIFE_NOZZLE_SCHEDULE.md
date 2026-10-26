# Campus unit nozzle schedule

Document number: AQS-NZ-002  
Revision: A  
Date: 2026-09-27  
Measurement: metric

Build phase 4. Origins frozen in `freecad/params.py`. These nozzles do not
sit on LEACH CSTR 1. Process-header tees are forbidden.

Valves on etch / acid makeup: GF 546 Pro V PVC-C FKM (same family as
AQS-NZ-001). UPW / grey / gas: non-vented utility valves.

## FISH TANK

| Tag | Service | DN | Dest | Wall |
|---|---|---|---|---|
| F1 | overflow | 80 | BIOFILTER | PP |
| F2 | drain | 50 | FARM SUMP | PP |
| F3 | makeup | 25 | HDR_UPW | PP-R |
| F4 | aeration | 15 | farm air (not HDR_H2) | PVC |

## BIOFILTER

| Tag | Service | DN | Dest |
|---|---|---|---|
| B1 | liquor in | 80 | FISH TANK F1 |
| B2 | liquor out | 80 | GROW BED |
| B3 | drain | 40 | FARM SUMP |

## GROW BED

| Tag | Service | DN | Dest |
|---|---|---|---|
| G1 | feed | 80 | BIOFILTER B2 |
| G2 | return | 50 | FARM SUMP |
| G3 | CO2 enrich | 25 | HDR_CO2 |
| G4 | O2 takeoff | 25 | HDR_O2 (S15) |
| G5 | solids chute | — | HDR_ORG / HOPPER |

## FARM SUMP

| Tag | Service | DN | Dest |
|---|---|---|---|
| S1 | recycle | 80 | FISH TANK |
| S2 | grey out | 50 | HDR_GREY |
| S3 | makeup | 25 | HDR_UPW |
| S4 | dose in | 20 | NUTRIENT DOSE |

## NUTRIENT DOSE

| Tag | Service | DN | Dest |
|---|---|---|---|
| D1 | tote / cake | — | S07 |
| D2 | dose | 20 | FARM SUMP S4 |
| D3 | rinse | 15 | HDR_UPW |

## WET BENCH

| Tag | Service | DN | Dest | Wall |
|---|---|---|---|---|
| W1 | UPW | 25 | HDR_UPW | PP-R |
| W2 | HCl | 20 | HCl PRODUCT | CPVC |
| W3 | NaOH | 20 | NaOH PRODUCT | PP |
| W4 | N2 purge | 15 | HDR_N2 | 316 |
| W5 | spent etch | 25 | ETCH RETURN | PVDF |
| W6 | floor | — | none — no drain |

## ETCH RETURN

| Tag | Service | DN | Dest | Wall |
|---|---|---|---|---|
| E1 | in | 25 | WET BENCH W5 | PVDF |
| E2 | out | 25 | REGEN LEACH | PVDF |
| E3 | local vent | 25 | carbon / return hood | PVDF |

E3 does not tee HDR_ACID_GAS.

## HAB WATER

| Tag | Service | DN | Dest |
|---|---|---|---|
| A1 | UPW in | 25 | HDR_UPW |
| A2 | grey out | 40 | HDR_GREY |
| A3 | potable | 20 | GALLEY / SLEEP |

## HAB WASTE

| Tag | Service | DN | Dest |
|---|---|---|---|
| J1 | liquor | 40 | SALT FEED / NUTRIENT DOSE |
| J2 | solids | — | HDR_ORG / HOPPER |

## COLD BOX

| Tag | Service | DN | Dest |
|---|---|---|---|
| C1 | H2 in | 25 | H2_DRYER (S05) |
| C2 | air / CO2 cap | 40 | S18 |
| C3 | O2 out | 25 | CRYO O2 / HDR_O2 |
| C4 | N2 out | 25 | CRYO N2 / HDR_N2 |
| C5 | CO2 out | 40 | CRYO CO2 / HDR_CO2 |
| C6 | H2 out | 25 | CRYO H2 (not HDR_H2) |
| C7 | heat reject | — | Q4 water, not Q1 flue |

# Oil and polymers — item 3 sizing

Document number: AQS-SIZE-OIL-POLY  
Revision: A  
Date: 2026-10-17  
Authority: notes/OIL_SECTOR.md, notes/GREASE_LINES.md, notes/POLYMERS_DESIGN.md. Not a PE stamp.  
Design assumptions. Not measured.

## Grease fatty-acid split

C19–C28 wax is 2.0 kg/d. Assume 40 % is saponifiable fatty acid (typical for a pyrolysis wax that has not been hydrotreated). Remainder is hydrocarbon base oil.

| Stream | Rate | To |
|--------|------|----|
| Saponifiable fatty acid | 0.8 kg/d | Split to the two kettles |
| Hydrocarbon base | 1.2 kg/d | Stays as grease oil phase |
| Fatty acid to GREASE_CA | 0.55 kg/d | ~1.2 kg/d finished Ca grease at ~10 % soap |
| Fatty acid to GREASE_LI | 0.25 kg/d | ~0.6 kg/d finished Li grease at ~10 % soap |

Soap fraction ~10 % is the design basis for both. If the assayed saponifiable yield is below 40 %, hold more of the C11–C18 cut as base oil and reduce grease rate. Do not import fatty acid.

## OIL_PYRO detail

| Parameter | Value |
|-----------|-------|
| Temperature | 450–550 °C (mid of 400–600 °C band) |
| Residence | 20–40 min solids |
| Heat | Induction, 15 kW (LOAD_ROLLUP) |
| Atmosphere | Oxygen-free; own vapor |
| Products | Oil vapor 10, NCG 2, char 3 kg/d on 15 kg/d feed |

## OIL_FRAC detail

| Parameter | Value |
|-----------|-------|
| Type | One atmospheric column |
| Reboiler | HX-3, existing concept |
| Side draws | 3 (C5–C10, C11–C18, C19–C28) + bottoms |
| Stages | 12 theoretical (assumption for this cut width) |
| Feed | 10 kg/d oil vapor, quenched |
| Reflux | ~1.5 (assumption) |

No hydrotreater. No second column.

## POLY_OLEFIN reactor

Feed: 2.0 kg/d C5–C10 + methanol co-feed from MEOH_SYNTH (rate matched to olefin demand, <1 kg/d).

| Parameter | Value |
|-----------|-------|
| Type | Small fixed-bed or slurry, batch-capable |
| Capacity | 2 kg/d resin |
| Temperature | 150–250 °C (assumption for light-cut oligomerization) |
| Pressure | 1–5 MPa (assumption) |
| Catalyst | On-site recoverable solid acid or supported metal; identity later. No external catalyst contract. |
| Product | To PELLET |

## POLY_COND

Left open. Recipe waits on the digester organic assay (BLACK_DIGEST volatile-solids and lipid split). Unit stays on the graph. No rate treated as design.

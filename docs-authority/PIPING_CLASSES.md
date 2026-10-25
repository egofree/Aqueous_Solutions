# Piping class sheets

Document number: AQS-PIP-003
Revision: C
Date: 2026-10-25
Authority: AQS-PLAN-007 task X-PIP-01. Materials are selected in accordance with AQS-STD-002 Rev N. The design code for every class is ASME B31.3 (process piping); the thermoplastic classes also follow the installation guide of the pipe manufacturer. Values marked "study" are recorded in the assumptions register AQS-REG-002 (A-M-045 to A-M-047). Study; this page is not stamped by a Professional Engineer (PE).

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue. Nine classes, service map, limits, joints, gaskets, bolting and valves. | 2026-10-15 |
| B | The held item on elastomers is resolved. Elastomer selection for each service is now given in AQS-STD-002 Rev N section 14, a decision table for each class based on the Parker O-Ring Handbook ORD 5700 (registered in AQS-STD-002 as source S23), with exceptions for some equipment families; the hold on gasket details for the wet synthesis (WS) units closes there. The class sheets stay at revision A, and task X-MAT-03 is closed. | 2026-10-21 |
| C | Purpose and scope added; text rewritten to the documentation style guide (AQS-DOC-002). No class, limit or service changed. | 2026-10-25 |

## Purpose and scope

A piping class is a named specification that fixes, for every line assigned to it, the pipe material and standard, the temperature limit, the basis of the pressure rating, the joint method, the gasket, the bolting and the valves. Assigning each line to a class means that these choices are made once for each type of service rather than line by line. This page defines the nine piping classes of the plant and maps each process service to a class.

The class letters are P for thermoplastic, M for metal, G for glass and F for fibre-reinforced plastic (FRP). References such as M2, M4, M5, M6 and M7 in the tables are the material rules of AQS-STD-002.

## 1. Class sheets

Table 1.1 gives the sheet for each class. The temperature factors are the derating factors that the manufacturers apply to the pressure rating at temperature.

Table 1.1. Piping classes

| Class | Material and standard | T limit | Pressure basis | Joints | Gasket | Bolting | Valves |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | PVC-U Sch 80, ASTM D1785 pipe, D2467 fittings, D2564 cement | 60 °C (M5) | D1785 rating for the size × manufacturer temperature factor, 0.22 at 60 °C (study) | Solvent cement; flanges Class 150 pattern | FKM; EPDM for alkaline | Non-metallic or isolated (M4) | PVC-U ball and diaphragm, FKM seats |
| P2 | CPVC Sch 80, ASTM F441 pipe, F439 fittings, F493 cement | 93 °C, operated ≤ 88 °C (M5) | F441 rating × 0.25 at 82 °C (study) | Solvent cement; flanges Class 150 pattern | FKM | Non-metallic or isolated | CPVC ball and diaphragm, FKM seats |
| P3 | PVDF SDR 21, ISO 10931 | 120 °C | ISO 10931 PN16 at 20 °C, manufacturer regression curve above (study) | Butt or IR fusion; PVDF flanges with backing rings | FKM; PTFE envelope for oxidizers | Non-metallic or isolated | PVDF ball and diaphragm, PTFE/FKM seats |
| P4 | PP-H, ISO 15494 | 80 °C | ISO 15494 PN10 at 20 °C, manufacturer curve (study) | Butt or socket fusion | EPDM | Non-metallic or isolated | PP ball |
| P5 | HDPE PE4710, ASTM D3035 / F714 | 60 °C | DR 11, ASTM F714 rating × manufacturer factor | Butt fusion | EPDM | 304 permitted (no redox service) | PE or PVC ball |
| M1 | 316L, ASTM A312 pipe, A403 fittings, A182 flanges | −196 to 400 °C | ASME B31.3 Table A-1 allowable; B16.5 Class 150/300 | Butt weld; flanged at equipment | Spiral wound 316/graphite; PTFE for O₂ | A193 B8M / A194 8M | 316 ball, PTFE seats; O₂ cleaned per ASTM G93 |
| M2 | Carbon steel, ASTM A106 Gr B, A234 WPB, A105 | −29 to 400 °C | ASME B31.3 Table A-1; B16.5 Class 150/300 | Butt weld | Spiral wound 304/graphite | A193 B7 / A194 2H | Cast steel gate or ball, graphite packing |
| G1 | Borosilicate glass 3.3, ISO 3585 | 200 °C, ΔT shock 120 K | Manufacturer rating by DN | Flanged couplings, PTFE inserts | PTFE | Isolated, sprung | Glass or PTFE-lined |
| F1 | FRP vinyl ester with C-veil liner, ASTM D2996 (filament wound) / D5421 (contact molded) | 100 °C | Manufacturer rating; ducts atmospheric | Butt-and-strap lay-up; flanged | FKM | Non-metallic or isolated | PVC or PVDF butterfly |

## 2. Service map

Table 2.1 assigns each process service to a class, with the section of AQS-STD-002 that gives the reason.

Table 2.1. Service map

| Service | Class | Basis |
| --- | --- | --- |
| Chlor-alkali, acid regeneration, HCl ≤ 60 °C, brine, bromine scrub | P1 | AQS-STD-002 M2, section 3.1 |
| Leach liquor 70–85 °C, LEACH_CSTR_1 connections, CONTINUOUS_RECYCLE above 60 °C | P2 | AQS-STD-002 section 7 |
| EW liquor at HX8, nitric (2 M, ≤ 40 °C), peroxide, oxidizer vents, HX-5 nozzles where not glass | P3 | AQS-STD-002 sections 4.5, 5 |
| NaOH, KOH, alkaline rinses ≤ 80 °C | P4 | AQS-STD-002 M1 |
| Tower water, irrigation, roof tank, flue quench water to the spool | P5 | No redox service |
| Q3 and Q4 water loops, dry H₂, dry O₂, cryogenic, methanol synthesis, H₂ vent stacks | M1 | AQS-STD-002 audit (water loops 316L), sections 6, M7; AQS-REV-H2-001 |
| Q1 and Q2 thermal oil | M2 | AQS-STD-002 section 4.4 (Q-loops) |
| HX-5 coil, FLUE_KO inlet quench spool | G1 | AQS-STD-002 sections 3.3, 4.3 |
| Flue and acid-gas ducts, NOX_SCRUB, FLUE_KO body | F1 | AQS-STD-002 section 4.3 |

Where a metal class meets a thermoplastic, glass or FRP class in an electrolyte or water service, a dielectric isolating flange is fitted at the break (rule M6).

## 3. Held items

The assignment of a class to every line of the flow graph, edge by edge, is task X-PIP-02. Elastomer selection for each service was resolved on 2026-10-21: AQS-STD-002 Rev N section 14 (task X-MAT-03) holds the elastomer decision for each class and the exceptions for equipment families, and the gasket entries in Table 1.1 remain the defaults for each class. The pressure ratings at temperature need the tables of the manufacturer of the chosen brand.

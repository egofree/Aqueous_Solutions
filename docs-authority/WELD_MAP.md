# Weld and joint map

Document number: AQS-WLD-001  
Revision: A  
Date: 2026-09-27

| Rev | Change | Date |
|---|---|---|
| A | Schedule only. Not a certified shop pack | 2026-09-27 |

This is a joint register for the fabricator to balloon against.
It is **not** an AWS / ASME stamped weld map. No WPS, PQR, or NDE
procedure lives here. Balloons are the `JW-###` tags.

## Process locks

- Salria / anolyte / acid: CPVC solvent or PVDF IR/butt. No metallic
  fillet on the wetted face.
- BMED BASE / digest: PP fusion.
- Pyro shell: Ti Grade 2 GTAW, purge both sides.
- H2 duct: 316L GTAW, purge.
- Oil-vapor jacket: 304 inner, CS outer. Do not weld the jacket to
  the pyro Ti.

## Register

| JW | Unit | Joint | Process | Filler / cement | NDE (suggested) | Code hook |
|---|---|---|---|---|---|---|
| JW-001 | LEACH CSTR 1 | wall-to-floor lap | CPVC solvent | Weld-On 724 | visual + 24 h hydro | sheet tank |
| JW-002 | LEACH CSTR 1 | wall corners | CPVC solvent | 724 | visual | |
| JW-003 | LEACH CSTR 1 | lid coaming to lid | CPVC solvent | 724 | visual | N1 |
| JW-004 | LEACH CSTR 1 | N3, N4, N5, N8, N9, N12 bosses | CPVC solvent + flange | 724 | visual + hydro | AQS-NZ-001 |
| JW-005 | LEACH CSTR 1 | N6a/b bosses | CPVC solvent | 724 | visual | HX water |
| JW-006 | CSTR 2 weir | crest plate + spout | CPVC solvent | 724 | visual | |
| JW-007 | CSTR 3 trough | trough to floor | CPVC solvent | 724 | visual | |
| JW-008 | EW-1…9 | body seams + funnel | CPVC solvent or rotomold | 724 | hydro per cell | |
| JW-009 | EW funnel | DN50 union boss | CPVC solvent | 724 | visual | 163 546 357V |
| JW-010 | EW hangers | 316L to 316L | GTAW fillet | ER316L | visual | cathodes only |
| JW-011 | DRYER | trough long seams | GTAW / GMAW | ER308L | visual + leak | jacket separately |
| JW-012 | DRYER | jacket to trough | GTAW fillet | ER308L | hydro jacket 6 bar | Q3 |
| JW-013 | INDUCTION PYROLYZER | shell long + girth | GTAW Ti | ERTi-2 | 100 % PT + RT sample | SB-338 |
| JW-014 | INDUCTION PYROLYZER | B16.5 NPS 12 Cl.150 | GTAW Ti | ERTi-2 | PT | no steel filler |
| JW-015 | QUENCH | shell + spray bosses | GTAW 304 | ER308L | hydro | |
| JW-016 | FRACTIONATOR | shell courses | GTAW 304 | ER308L | visual | pack vendor |
| JW-017 | AFTERBURNER | shell + burner plate | SMAW / GMAW CS or 304 | E7018 / ER308L | visual | Q1 |
| JW-018 | BURNOUT ROTARY | tube to tires | per SiC / Alloy 600 vendor | vendor | vendor | not oil auger |
| JW-019 | NaOH DIGEST | PP sheet seams | extrusion weld | PP rod | spark test | |
| JW-020 | BMED frames | PP | fusion | PP | leak | SEM Tech |
| JW-021 | ALK SCRUBBER | PP/FRP shell | vendor | vendor | hydro | pregnant → CRU |
| JW-022 | HDR_H2 | 316L long / girth | GTAW | ER316L | PT + purge record | arrestor up |
| JW-023 | HDR_OIL_VAPOR | 304 inner | GTAW | ER308L | visual | jacket CS fillet only |
| JW-024 | HX-7 flue jacket | CS | GMAW | ER70S-6 | visual | atmosphere isolated |
| JW-025 | ZnBr2 tanks | PP | fusion | PP | spark | Br2 tower PVDF |
| JW-026 | CRU | CPVC shell + jacket bosses | 724 + CS jacket fillet | 724 / ER308L | hydro | not PP |
| JW-027 | Pipe rack | CS beam clips | fillet | E7018 | visual | not wetted |
| JW-028 | Cable tray | splices | bolted | — | torque | no weld on Al tray |
| JW-029 | Ground ring | cadweld / exothermic | — | — | continuity &lt; 1 Ω | NEC / local |

## Balloon rule

One balloon per JW on the shop drawing. Do not balloon solvent joints
with a fillet-weld symbol. CPVC joints get a note “SW 724, full
insertion, 24 h cure” instead of an AWS weld symbol.

# Grounding and bonding

Document number: AQS-ELEC-005
Revision: A
Date: 2026-10-15
Authority: AQS-PLAN-007 X-ELS-08. Study. Not a PE stamp. Script `docs-authority/_grounding_study.py`. Study values in AQS-REG-002 (A-M-050 to A-M-052).

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue. Earthing grid, bonding rules, DC system earthing. Step and touch held. | 2026-10-15 |

## 1. Earthing grid

Bare copper ring, 4/0 AWG (107 mm²), 0.75 m deep, round the placement extents (about 35 × 20 m, assumption), with twelve 16 mm × 3 m copper-clad rods at about 10 m spacing (NEC 250.52, 250.53). Soil resistivity 50 Ω·m (assumption for the clay of AQS-SITE-002; no Wenner test yet). Grid resistance by IEEE 80-2013 equation 52 (Sverak): 1.14 Ω, below the 5 Ω commonly targeted for industrial systems (IEEE 142). Building steel and rebar are bonded to the ring (NEC 250.52(A)(2), (A)(3)).

## 2. Bonding

- Every metal piping class (AQS-PIP-003 M1, M2) and every metal skid is bonded to the ring; flanged joints carry jumpers where gaskets insulate (NFPA 77 static).
- H₂ piping, vent stacks and the CRYO_H2, FUEL_CELL, BACKUP_GEN and MEOH_SYNTH skids: bonded and earthed, resistance to earth ≤ 10 Ω for static (NFPA 77 guidance; NFPA 2).
- Dielectric isolating flanges (AQS-STD-002 M6) are not jumpered. Each side is earthed separately, so isolation against electrolyte current is kept and static still drains.
- Thermoplastic, glass and FRP equipment carries no bond; conductive parts inside (agitator shaft core, instrument wells) are bonded where they are accessible.
- Solvent and flammable areas (WS_SOLV, MEOH_TANK): containers and transfer lines bonded per NFPA 77 and NFPA 30.

## 3. DC systems

RECT-EW channels (AQS-ELEC-004) run ungrounded (floating) DC with insulation monitoring and a ground-fault alarm, so a single fault does not drive current through liquor, piping or the grid. Busbars are insulated from racks; cell tanks are non-conductive. Stray-current paths through the liquor manifolds are X-MAT-07.

## 4. Held

- Step and touch voltages (IEEE 80) need the earth-fault current, which comes from X-ELS-07 protection and the X-ELS-03 one-line.
- Soil resistivity needs a Wenner four-pin test at the parcel (X-BAS-03).
- Lightning protection (NFPA 780) is not covered here.

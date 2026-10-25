# Grounding and bonding

Document number: AQS-ELEC-005
Revision: B
Date: 2026-10-25
Authority: AQS-PLAN-007 task X-ELS-08. Calculation script `docs-authority/_grounding_study.py`. Assumed study values are recorded in the assumptions register AQS-REG-002 (A-M-050 to A-M-052). Study; this page is not stamped by a Professional Engineer (PE).

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue. Earthing grid, bonding rules, earthing of the direct-current systems. Step and touch voltages held. | 2026-10-15 |
| B | Purpose and scope added; text rewritten to the documentation style guide (AQS-DOC-002). Section 5 records that the grid of section 1 has been superseded by the grid study in AQS-ELEC-006 section 4. No value changed. | 2026-10-25 |

## Purpose and scope

Grounding (earthing) connects the electrical system and the plant structure to the soil, so that a fault current has a low-resistance path and exposed metal does not rise to a dangerous voltage. Bonding connects metal parts to each other and to the earthing grid, so that they stay at the same voltage and static charge can drain away. This page describes the earthing grid, the bonding rules for piping and equipment, and the earthing of the direct-current (DC) systems. The fault, touch and step voltage check is in the protection study AQS-ELEC-006.

## 1. Earthing grid

At revision A the earthing grid was a bare copper ring conductor of 4/0 AWG (107 mm²) buried 0.75 m deep around the placement extents of the plant, which were assumed to be about 35 × 20 m. Twelve copper-clad ground rods, each 16 mm in diameter and 3 m long, were driven at about 10 m spacing along the ring (NEC 250.52 and 250.53).

The soil resistivity is assumed to be 50 Ω·m, which is typical of the clay assumed in AQS-SITE-002; no Wenner test has yet been made. With these values the grid resistance by equation 52 of IEEE 80-2013 (the Sverak equation) is 1.14 Ω. This is below the 5 Ω commonly targeted for industrial systems (IEEE 142). The building steel and the reinforcing bar (rebar) of the slab are bonded to the ring (NEC 250.52(A)(2) and (A)(3)).

## 2. Bonding

The following bonding rules apply.

- Every metal piping class (classes M1 and M2 of AQS-PIP-003) and every metal skid is bonded to the earthing ring. Where a gasket insulates a flanged joint, the joint carries a bonding jumper so that static charge can drain (NFPA 77).
- Hydrogen piping, the vent stacks, and the CRYO_H2, FUEL_CELL, BACKUP_GEN and MEOH_SYNTH skids are bonded and earthed, with a resistance to earth of no more than 10 Ω for static drainage (NFPA 77 guidance; NFPA 2).
- Dielectric isolating flanges (class M6 of AQS-STD-002) are not jumpered. Each side of the flange is earthed separately, so that the flange still blocks current carried by the electrolyte while static charge still drains.
- Equipment made of thermoplastic, glass or fibre-reinforced plastic (FRP) is not bonded. Conductive parts inside such equipment, such as an agitator shaft core or an instrument well, are bonded where they can be reached.
- In the solvent and flammable-liquid areas (WS_SOLV and MEOH_TANK), containers and transfer lines are bonded in accordance with NFPA 77 and NFPA 30.

## 3. Direct-current systems

The rectifier channels for electrowinning (RECT-EW, AQS-ELEC-004) run as ungrounded (floating) DC systems with insulation monitoring and a ground-fault alarm. A single earth fault therefore does not drive current through the liquor, the piping or the earthing grid. The busbars are insulated from their racks, and the cell tanks are non-conductive. Stray-current paths through the liquor manifolds are covered by task X-MAT-07.

## 4. Step and touch voltages

Step voltage is the voltage between a person's feet, and touch voltage is the voltage between a person's hand and feet, during an earth fault. They are checked in section 4 of AQS-ELEC-006. At revision A of this page, that check was quoted as a ground potential rise (GPR) of 494 V (AQS-ELEC-006 Rev B), against a tolerable touch voltage of 176 V on bare soil for a fault cleared in 0.5 s, with a layer of crushed rock required on the yard. The result was recorded as safe.

## 5. Held items and open points

- The soil resistivity needs a Wenner four-pin test at the parcel (task X-BAS-03).
- Lightning protection (NFPA 780) is not covered by this page.
- The grid of section 1 and the values quoted in section 4 have been superseded. AQS-ELEC-006 section 4 now describes grid Rev B, sized from the converged building plus a 10 m west yard (196 × 174 m, 12 m mesh of 2/0 AWG at 0.75 m depth, 74 rods of 3 m), with a grid resistance of 0.128 Ω and a GPR of 887 V. The mesh voltage (140 V) and step voltage (60 V) are below the tolerable values on bare soil and on crushed rock. The script `docs-authority/_grounding_study.py` at this revision computes a grid resistance of 0.150 Ω with 65 rods. Sections 1 and 4 of this page are to be revised once these results are reconciled.

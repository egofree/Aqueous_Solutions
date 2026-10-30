# Rewrite batch 38: chlor-alkali top-up and the cell hydrogen (Q-035, Q-036)

Date: 2026-10-29

## Change

The owner delegated questions Q-034 to Q-037 to a decision on the merits (t62u). This batch closes Q-035 and Q-036 on the sodium hydroxide plant.

- Q-035: the driver naoh_route now selects CHLOR_ALKALI. At the present make-up it draws less than half the load of CAUSTICIZE, because the trona calciner and the lime kiln carry shell losses that dominate the small top-up. It also vents no carbon dioxide and takes one ore, halite, instead of trona and lime. The membrane cells that recover the purge salt already exist, so the top-up adds no unit. CAUSTICIZE stays selectable.
- Q-036: the cell hydrogen stays on the H2 header. It is the same gas as the electrowinning cathode hydrogen and goes through H2_DRYER to the hydrogen store CRYO_H2, which feeds methanol synthesis and the fuel cells. A separate consumer or store would add equipment for the same gas, and resizing the electrolyser against it is held with the O2 ownership.
- With CHLOR_ALKALI the causticiser takes no lime, so the lime residue of the acid kiln ships in full on IA-LIME-SHIP.
- AQS-PAR-001 is at revision F. Section 7.1 gives the reasons, and Table 7.1 still gives both routes.
- The basis is recorded in A-M-426. Both questions are closed in AQS-OQ-001 revision E.

## Values

| Quantity | Before | After |
|---|---|---|
| NAOH_PLANT load | 1.1929 kW | 0.5004 kW |
| IA-TRONA-MU, trona ore | 0.9196 kg/d | retired |
| IA-HALITE-MU, halite ore | retired | 0.6758 kg/d |
| IA-LIME-TO-NAOH, lime from the acid residue | 0.0224 kg/d | retired |
| IA-NAOH-VENT, kiln gases | 0.4751 kg/d | retired |
| IA-NAOH-CL2-SHIP, cell chlorine | 3.5050 kg/d | 3.8945 kg/d |
| IA-NAOH-H2, cell hydrogen to the H2 header | 0.0997 kg/d | 0.1107 kg/d |

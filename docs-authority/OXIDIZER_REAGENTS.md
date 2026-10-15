# Nitric acid and hydrogen peroxide systems

Document number: AQS-DSN-OX-001
Revision: A
Date: 2026-10-15
Authority: graph Rev BH. Study. Not a PE stamp. Materials per AQS-STD-002 Rev D. No rate change. No edge added.

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue. Concentration specs on the graph; supply route, storage, materials, vents, relief, instruments, segregation. | 2026-10-15 |

## 1. Nitric acid (HNO3 to WS_NITRIC to WET_BENCH)

Route on the graph. HNO3 takes IA-NH3-NIT from WS_AMMONIA and IA-O2-NIT from HDR_O2: ammonia oxidation to NO, oxidation to NO₂, absorption in water. WS_NITRIC also takes IA-BMED-01, 2 M HCl from BMED_ACID, for a resin exchange of NaNO₃ (balance terms on the node). S34 leaves at 2 M HNO₃, 1.064 kg/L.

Concentration spec (graph params, `product_spec`). WS_NITRIC 2.0 M, 11.8 wt% (derived from S34), stored at no more than 2.0 M and 40 °C (assumption). HNO3 absorbs to no more than 2 M (decision): weak acid only, so no concentrated or fuming nitric exists in the plant and the oxidizer hazard stays at the dilute class.

Materials.
- Storage tank and piping: PVC-U. PVC is suitable to 45 % nitric at 20 °C and limited at 60 °C [S10]; 11.8 % at 40 °C is inside that.
- Pumps, valves, and the HNO3 absorber: PVDF. Rated to 80 °C at up to 10 % and 65 °C at 11 to 70 % [S1]. The absorber runs warm from NO oxidation; PVDF covers it.
- HNO3 oxidation reactor: the catalyst gauze and its hot section are metal under M7 (hot dry gas above the dew point), ending at a dielectric flange before the gas cooler. The cooler and everything downstream that sees condensate are PVDF or borosilicate glass 3.3.
- 304L, the usual nitric metal, is not used: wet nitric is oxidizing (M3). It is allowed only in the hot dry reactor section.
- Gaskets FKM or PTFE.

Vents and relief. Atmospheric tank with a breather. The tank and absorber vents carry NOx and acid mist and must go to NOX_SCRUB; there is no vent edge on the graph, so this is held for an edge (no edge added here). No closed relief; overflow to the bund.

Instruments and trips. Level with high-high trip closing IA-HNO3 and IA-BMED-01. Temperature with a high trip at 40 °C (assumption). Density or conductivity for concentration, alarm above 2.0 M. pH in the bund sump.

## 2. Hydrogen peroxide (HDR_O2 to WS_PEROX to WET_BENCH)

Route on the graph. IA-H2O2-SRC brings oxygen from HDR_O2. The route is on-site two-electron oxygen reduction at a carbon cathode, making dilute peroxide directly. S32 leaves as dilute H₂O₂ (SC-1 and SC-2 cleans) at 1.0 kg/L.

Concentration spec (graph params). Nominal 5 wt%, maximum 6 wt%, no stabilizer (electronic grade; stabilizers contaminate the wafer clean), holdup no more than 1 day, temperature no more than 30 °C. All are assumptions. Making it at the bench strength avoids storing concentrated peroxide.

Materials.
- Tank: HDPE, cross-linked, unpigmented, UV stabilized. The producer limits HDPE to 50 % or less [S11]; 6 % is far inside.
- Piping, pump, and valves: PVDF. Kynar resists oxidants [S2].
- Seals: PTFE or FKM, which the producer lists as acceptable [S12].
- The producer also accepts passivated 304L/316L and high-purity aluminum [S11]. They are not used here because of M3. PVC is listed by the producer for temporary systems only [S12], so it is not used.
- The producing cell's electrodes are allowed under M6 and listed on the duty.

Decomposition and venting. Peroxide decomposes to water and oxygen, faster with heat, base, and metal ions (Fe, Cu, Mn). Requirements, after the producer's handling standard [S12]:
- Continuous filtered vent.
- Free-lifting manway cover as the emergency relief.
- No trapped volumes. Ball and plug valves have vented cavities.
- No metal fittings in the wetted path.
- Temperature trip at 30 °C closes the cell feed and starts the drain to the bund.

Instruments and trips. Level with high-high trip on the cell. Temperature with a high trip at 30 °C. Concentration by inline UV or titration sample, with an alarm above 6 wt%. Vent flow or tank pressure, alarm on a rise.

## 3. Incompatibilities and segregation

| Reagent | Keep apart from | Reason |
| --- | --- | --- |
| HNO₃ | WS_SOLV, WS_DOPE organics, ALD/ETOH products | Nitration and oxidation of organics |
| HNO₃ | WS_AMMONIA | Ammonium nitrate |
| HNO₃ | WS_KOH | Heat of neutralization |
| HNO₃ | WS_HF_ED | Separate acid bund for HF exposure control |
| H₂O₂ | WS_SOLV (acetone, alcohols) | Organic peroxides |
| H₂O₂ | WS_KOH, WS_AMMONIA in bulk | Base-catalyzed decomposition (the SC-1 mix is made only at the bench, in small volume) |
| H₂O₂ | Metals, rust, Cu | Catalytic decomposition |

Each class gets its own bund at 110 % of its largest tank (assumption): oxidizing acid (nitric), oxidizer (peroxide), bases (KOH, ammonia), HF, and solvents. Solvents are in a separate fire area. The bunds drain to separate sumps, not to a common pit.

## 4. Held

- Vent edges from WS_NITRIC and HNO3 to NOX_SCRUB.
- Tank volumes. The holdup basis is not on the graph.
- HNO3 absorber design at 2 M.
- Peroxide cell current and area.
- Bund sizes.

## References

[S1], [S2] as AQS-STD-002. [S10] Vinidex, Chemical Performance of PVC, https://www.vinidex.com.au/app/uploads/pdf/Chemical-Performance-of-PVC.pdf. [S11] Solvay, H₂O₂ Materials of Construction for Storage, https://www.solvay.com/sites/solvay_solvay/files/2019-10/H2O2%20Materials%20of%20Construction%20for%20the%20Storage%20of%20H2O2.pdf. [S12] Solvay, Safety and Handling of Hydrogen Peroxide, https://www.solvay.com/sites/solvay_solvay/files/2019-10/H2O2%20Safety%20and%20Handling%20of%20Hydrogen%20Peroxide.pdf.

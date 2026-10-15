# Hydrogen embrittlement review

Document number: AQS-REV-H2-001
Revision: B
Date: 2026-10-15
Authority: graph Rev BH. Study. Not a PE stamp. Materials per AQS-STD-002 Rev E, rule M6. No rate change.

| Rev | Description | Date |
| --- | --- | --- |
| B | H₂ edge conditions (X-MAT-15) and MEOH_SYNTH API 941 check (X-MAT-14). | 2026-10-15 |
| A | First issue. Every H₂-wetted unit, with conditions from the graph, material, and fixes. | 2026-10-15 |

## 1. Basis

Principles applied:
- ASME B31.12 for hydrogen piping [S14]. It requires material qualification. It adds performance factors or fracture-mechanics qualification for carbon steels and treats austenitic stainless as the low-risk class.
- ISO 11114-1 and CGA G-5.6 compatibility principles. Both are named here and were not consulted in full text.
- The Sandia Technical Reference for 316/316L [S13]. It finds little room-temperature ductility loss in gaseous H₂. Susceptibility rises with sensitization, low nickel, cold work (strain-induced martensite), and subambient temperature. Well-made welds are comparable to the base metal.
- The CSA CHMC1 screening route [S15]. It accepts 316/316L and 6061 aluminum for dry H₂. It does not establish compatibility with external environments such as warm humid air.

Conditions on the graph. No H₂ edge carries pressure, temperature, or purity. HDR_H2 and H2_DRYER have design_kPa 17.8, which is the withdrawn head-plus-10 figure (RELIEF.md), so it is not a pressure. This review therefore classifies each unit by service. It recommends material on the stated class and holds the pressure-dependent checks until the graph carries P, T, and purity (TASK_PLAN X-MAT-09).

## 2. Units

| Unit | Service from the graph | Class | Material | Fixes and holds |
| --- | --- | --- | --- | --- |
| EW_1 to EW_9 cathodes | Cathodic H₂ evolution in chloride electrolyte; H₂ plus sweep air to HDR_H2 | Wet, cathodic charging, acid chloride | 316L cathode, annealed; Ti/PbO₂ anode | No cold forming after anneal (martensite [S13]); low applied stress in the stripping fixture; record cathode life. The Ti anode must not go cathodic: reverse-current blocking at the rectifier and controlled shutdown, otherwise Ti hydrides. Dissolution basis held (X-MAT-07). |
| HDR_H2 | Wet H₂ with sweep air from the EW hoods; can carry HCl/Cl₂ mist; near atmospheric | Wet, reducing, acid (M3) | PVC-U header | Permeation is negligible near atmospheric pressure. Ignition governs, not embrittlement: the sweep-air dilution must hold the mix below 25 % of the lower flammable limit (4 vol% H₂), or keep it rich and inerted. That basis is held for the HAZOP. Bond any metal component; no isolated conductors in the plastic line. |
| H2_DRYER | Wet H₂ in, dry H₂ out to CRYO_H2 and RELIEF_H2 | Wet inlet; dry outlet | Inlet knock-out PVC-U; dryer vessel and outlet 316L, annealed | Dry H₂ on 316L is the CHMC1 screening case [S15]. Regeneration temperature and pressure are held. Sensitization: low-carbon grade, no post-weld exposure 500 to 800 °C [S13]. |
| RELIEF_H2 | H₂ contingency relief from H2_DRYER to an 8 m vent stack (NFPA 2) | Dry H₂, flame exposure | 316L, annealed, grounded | Metal under M7 (flame). Open stack with no cap that traps H₂; bonded and grounded. CGA G-5.5 vent system principles. |
| CRYO_H2 | Dry H₂ to liquid or cold storage; feeds FUEL_CELL, BACKUP_GEN, MEOH_SYNTH | Dry, cryogenic, cycling to ambient | 316L, annealed, nickel toward the top of the grade range | Susceptibility rises at subambient temperature [S13], so the warm-up range matters more than the cold end. Pressure held. No ferritic or high-strength steel. |
| MEOH_SYNTH | H₂ (S74) with CO₂ (S73) to methanol | Dry H₂ 50 bar a, 250 °C, pH₂ 37.5 bar (study, section 5) | 316L | HTHA applies (API 941). Austenitic stainless is not susceptible; carbon steel and C-0.5Mo excluded. See section 5. |
| FUEL_CELL | H₂ (S49) and O₂ (S50) to a PEM stack | Dry H₂ feed; wet stack | Feed tubing 316L, annealed; stack internals per the stack maker | Stack plates are electrodes (M6). Dielectric break between stack and plant piping. |
| BACKUP_GEN | H₂ fuel (S45) | Dry H₂ | 316L, annealed, fuel line | Engine internals per the maker. |
| ALD, LEACH_CSTR_1, ZNBR2 | Trace or dissolved H₂ (IA-ALD-H2, IA-LEACH-H2 at 0 kg/d, Zn side reaction) | Wet, polymer equipment | As AQS-STD-002 | No embrittlement case in polymer. Vent to HDR_H2 or the stack. |

## 3. General rules

1. No carbon steel, low-alloy steel, high-strength steel, or martensitic stainless in any H₂ service.
2. Austenitic 316L, annealed, is the default metal. It is used dry under M6. It is used wet only where the unit is an electrode.
3. Low-pressure dry H₂ distribution may use HDPE or PA where it is downstream of the dryer, below the polymer's rated pressure, and not in a fire zone. Copper tubing is acceptable for dry low-pressure instrument lines. Neither is used in acid mist.
4. Welds are qualified per B31.12 and inspected. No threaded joints in H₂ above atmospheric pressure.
5. Every H₂ line that crosses into an electrochemical area has a dielectric break (M6).

## 4. Held

- P, T, and purity on every H₂ edge (X-MAT-09).
- HDR_H2 dilution basis.
- H2_DRYER regeneration conditions.
- CRYO_H2 pressure.
- Cathode life record.

## 5. H₂ edge conditions and API 941, Rev B

Study values (AQS-REG-002 A-M-021 to 024), written on each edge as P_bar_a, T_C, purity_mol_pct:

| Segment | Edges | P bar a | T °C | Purity mol% |
| --- | --- | --- | --- | --- |
| Cell offgas and header, wet | IA-EW1/2/4-H2, IA-HDR-H2-01 to 04, IA-LEACH-H2, IA-ALD-H2 | 1.05 | 40 | 98, water-saturated |
| Dryer outlet to storage | S05, S64, S24, IA-H2-IN, IA-H2-AIR | 10 | 30 | 99.9, dew −40 °C |
| Storage to fuel cell and generator | S49, S45 | 1.5 | 25 | 99.97 (ISO 14687 Grade D) |
| Storage to methanol synthesis | S74 | 50 | 40 | 99.9 |

S52 and IA-E-H2 are not H₂ gas service (fuel-cell product water; electricity) and carry no conditions.

API 941 check, MEOH_SYNTH. Reactor 250 °C (482 °F), 50 bar a, H₂:CO₂ 3:1, so pH₂ = 37.5 bar a (544 psia). API 941 applies above 400 °F (204 °C) with H₂ partial pressure above 50 psia; both are exceeded. Carbon steel and C-0.5Mo are not used at this point; API 941 states austenitic stainless steels are not susceptible to HTHA at any listed condition, so 316L is chosen and the Nelson-curve reading does not govern the choice. 316L also matches the low-temperature embrittlement rules of section 3 for the S74 feed. Gas H₂ embrittlement at 50 bar and ambient applies to the feed compressor; 316L with nickel at the top of the grade range, no high-strength fasteners.

Held. A purifier for Grade D if dryer output is below grade. CRYO_H2 storage pressure.

## 6. EW titanium cathodes

Titanium blanks on EW_1, EW_2, EW_4 and EW_9 make side-reaction H₂. Hydride bend test at each strip cycle for the first year; no reverse current (AQS-STD-002 section 9).

## References

- [S13] Sandia, Technical Reference on Hydrogen Compatibility of Materials, 316/316L, https://www.sandia.gov/app/uploads/sites/158/2021/12/2103TechRef_316SS.pdf
- [S14] ASME B31.12 Hydrogen Piping and Pipelines, https://www.asme.org/codes-standards/find-codes-standards/b31-12-hydrogen-piping-pipelines
- [S15] Sandia/OSTI, Materials Qualification for Hydrogen Service using CSA CHMC1, https://www.osti.gov/servlets/purl/1673694
- S18. API RP 941, Steels for Hydrogen Service at Elevated Temperatures and Pressures in Petroleum Refineries and Petrochemical Plants, 8th ed., 2016.
- S19. ISO 14687:2019, Hydrogen fuel quality — Product specification.
- S20. Bertau M. et al. (eds.), Methanol: The Basic Chemical and Energy Feedstock of the Future, Springer, 2014.

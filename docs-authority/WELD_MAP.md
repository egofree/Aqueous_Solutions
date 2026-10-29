# Weld and joint map

Document number: AQS-WLD-001
Revision: B
Date: 2026-10-29

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue: a register of joints for the fabricator, without procedures | 2026-09-27 |
| B | Joint tags restored to JW-nnn after a text replacement on 2026-10-25 corrupted them; purpose and scope added; the electrowinning hangers and the hydrogen header brought in line with AQS-STD-002; items not found on the plant graph listed in section 5 | 2026-10-29 |

## 1. Purpose and scope

This page is a register of the welded, fused, cemented and bonded joints of the plant equipment. The fabricator marks each joint on the shop drawing with a balloon carrying its joint tag. A joint tag has the form JW-nnn, where nnn is a three-digit serial number.

The register is not a certified weld map under AWS or ASME rules. It contains no welding procedure specification (WPS), procedure qualification record (PQR) or non-destructive examination (NDE) procedure; the fabricator supplies those. The materials come from AQS-STD-002 (`MATERIALS_STD.md`), which governs where this page and that standard differ.

## 2. Joining rules by service

1. Acid and anolyte service is joined by CPVC solvent cement or by PVDF infrared or butt fusion. No metal fillet weld is made on a wetted face.
2. Base service in the bipolar membrane electrodialysis units and the digesters is joined by polypropylene (PP) fusion.
3. The pyrolysis reactor shell is titanium Grade 2, welded by gas tungsten arc welding (GTAW) with a purge on both sides.
4. The oil vapour jacket has a type 304 stainless steel inner wall and a carbon steel outer wall. The jacket is never welded to the titanium of the pyrolysis reactor.
5. The hydrogen header `HDR_H2` is unplasticized PVC (PVC-U), joined by solvent cement (AQS-STD-002, `H2_EMBRITTLEMENT_REVIEW.md`).

## 3. Register

Table 3.1 lists the joints. The examination column gives the suggested examination; the fabricator's NDE procedure governs.

Table 3.1. Joint register

| Tag | Unit or item | Joint | Process | Filler or cement | Examination | Note |
| --- | --- | --- | --- | --- | --- | --- |
| JW-001 | `LEACH_CSTR_1` | Wall to floor, lap | CPVC solvent cement | Weld-On 724 | Visual, and a 24 h hydrostatic test | Sheet tank |
| JW-002 | `LEACH_CSTR_1` | Wall corners | CPVC solvent cement | Weld-On 724 | Visual | |
| JW-003 | `LEACH_CSTR_1` | Lid coaming to lid | CPVC solvent cement | Weld-On 724 | Visual | Nozzle N1 |
| JW-004 | `LEACH_CSTR_1` | Bosses of nozzles N3, N4, N5, N8, N9 and N12 | CPVC solvent cement and flange | Weld-On 724 | Visual and hydrostatic test | AQS-NZ-001 |
| JW-005 | `LEACH_CSTR_1` | Bosses of nozzles N6a and N6b | CPVC solvent cement | Weld-On 724 | Visual | Heat exchanger water |
| JW-006 | Leach tank 2 weir | Crest plate and spout | CPVC solvent cement | Weld-On 724 | Visual | See section 5 |
| JW-007 | Leach tank 3 trough | Trough to floor | CPVC solvent cement | Weld-On 724 | Visual | See section 5 |
| JW-008 | `EW_1` to `EW_9` | Body seams and funnel | CPVC solvent cement, or rotational moulding | Weld-On 724 | Hydrostatic test of each cell | |
| JW-009 | Electrowinning funnel | DN50 union boss | CPVC solvent cement | Weld-On 724 | Visual | Union part number 163 546 357V |
| JW-010 | Electrowinning cathode hangers | To be redefined | — | — | — | Superseded: AQS-STD-002 section 9 changed the cathode blanks to titanium Grade 2 and the hanger bars to copper, so the former 316L fillet weld no longer applies |
| JW-011 | Dryer | Trough long seams | GTAW or gas metal arc welding (GMAW) | ER308L | Visual and leak test | Jacket joined separately; see section 5 |
| JW-012 | Dryer | Jacket to trough | GTAW fillet | ER308L | Hydrostatic test of the jacket at 600 kPa | Heated from the Q3 header |
| JW-013 | Pyrolysis reactor | Shell long and girth seams | GTAW, titanium | ERTi-2 | Penetrant test of every seam and a radiographic sample | ASME SB-338 |
| JW-014 | Pyrolysis reactor | Flange, ASME B16.5 NPS 12 Class 150 | GTAW, titanium | ERTi-2 | Penetrant test | No steel filler |
| JW-015 | Quench | Shell and spray bosses | GTAW, type 304 | ER308L | Hydrostatic test | |
| JW-016 | Fractionator | Shell courses | GTAW, type 304 | ER308L | Visual | Packing by the vendor |
| JW-017 | `AFTERBURNER` | Shell and burner plate | Shielded metal arc welding (SMAW) or GMAW, carbon steel or type 304 | E7018 or ER308L | Visual | Q1 header |
| JW-018 | Rotary burnout kiln | Tube to tyres | To the vendor's procedure for silicon carbide or Alloy 600 | By the vendor | By the vendor | Not the oil auger |
| JW-019 | Sodium hydroxide digester | PP sheet seams | Extrusion welding | PP rod | Spark test | |
| JW-020 | Bipolar membrane electrodialysis frames | PP | Fusion | PP | Leak test | |
| JW-021 | `ALK_SCRUBBER` | PP or fibre-reinforced plastic shell | By the vendor | By the vendor | Hydrostatic test | Bleed to `CRU` |
| JW-022 | `HDR_H2` | Pipe and fittings | PVC-U solvent cement, ASTM D2855 | PVC cement | Visual and leak test | Changed from 316L welding to match AQS-STD-002; flame arrestor upstream |
| JW-023 | Oil vapour header | Type 304 inner wall | GTAW | ER308L | Visual | Carbon steel jacket by fillet weld only |
| JW-024 | Heat exchanger HX-7, flue jacket | Carbon steel | GMAW | ER70S-6 | Visual | Isolated from the atmosphere |
| JW-025 | `ZNBR2` tanks | PP | Fusion | PP | Spark test | Bromine tower in PVDF |
| JW-026 | `CRU` | CPVC shell and jacket bosses | Weld-On 724, and a carbon steel fillet weld on the jacket | Weld-On 724 or ER308L | Hydrostatic test | Not PP |
| JW-027 | Pipe rack | Carbon steel beam clips | Fillet weld | E7018 | Visual | Not wetted |
| JW-028 | Cable tray | Splices | Bolted | — | Torque check | No welding on aluminium tray |
| JW-029 | Ground ring | Exothermic connections | Exothermic welding | — | Continuity below 1 Ω | NFPA 70 |

## 4. Balloon rule

Each joint has one balloon on the shop drawing. A solvent-cemented joint is not marked with a fillet weld symbol. A CPVC joint carries the note "SW 724, full insertion, 24 h cure" instead of an AWS weld symbol.

## 5. Open items

1. The register names some equipment by description because no graph unit has the same name: leach tanks 2 and 3, the dryer, the pyrolysis reactor, the quench, the fractionator, the rotary burnout kiln, the sodium hydroxide digester and heat exchanger HX-7. Each is to be matched to its graph unit (for example `OIL_PYRO`, `OIL_FRAC`, `OIL_DRYER`, `SHELL_BURNOUT` or `GLASS_DIGEST`) by the fabricator's drawing list, and the register updated.
2. The joints of the electrowinning cathode hangers (JW-010) are to be defined for the titanium blanks and copper hanger bars of AQS-STD-002 section 9.

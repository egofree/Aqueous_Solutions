# Materials standard

Document number: AQS-STD-002
Revision: H
Date: 2026-10-15
Authority: graph Rev BH. Study. Not a PE stamp. Feed basis AQS-ASSAY-001 Rev C. Referenced from AQS-PLAN-007 section X-MAT.

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue. Owner rule: chlor-alkali and acid-regen systems are PVC; no metal wetted part where oxidizing or reducing conditions exist. First audit of every present unit. | 2026-10-15 |
| B | Decisions for ZNBR2_BR2_REGEN (PVC-U) and LEACH_CSTR_1 HX-5 (PVDF coil). Published sources added. | 2026-10-15 |
| C | M7 cases extended. Decisions for HX8, ETOH_STILL, BUOH_STILL, AFTERBURNER_FLUE, FLUE_KO, BAGHOUSE, Q1 and Q2. | 2026-10-15 |
| D | Nitric and peroxide materials (AQS-DSN-OX-001). Sources S10 to S12. | 2026-10-15 |
| E | H2 embrittlement review AQS-REV-H2-001; M6 applied to every H2-wetted unit. | 2026-10-15 |
| F | Leach liquor temperature 70-85 C found in the repo; LEACH_CSTR_1 tank corrected from PVC-U to CPVC. | 2026-10-15 |
| G | HX-5 adopted as a borosilicate glass 3.3 coil (X-MAT-16). | 2026-10-15 |
| H | HX8 adopted as a PVDF bundle (X-MAT-17). | 2026-10-15 |

## 1. Rules

M1. Compatibility decides every material choice. A material is named only with the stream it touches. A duty sheet section 3 that names a material without its stream is not complete.

M2. Everything in the chlor-alkali and acid-regen systems is PVC. This covers the leach, the CRU oxidant loop, BMED acid and base, the polish bank, the recycle loop, the float/sink and class-treat liquors, salt feed, the acid and alkaline scrubbers, and every tank, header, pipe, and nozzle on those liquors.

M3. No metal container or wetted part where oxidizing or reducing conditions exist. Oxidizing: chlorate or hypochlorite liquor, anolyte, nitric, peroxide, Cl₂, Br₂, O₂ wet. Reducing: catholyte, anaerobic digestion, fermentation, wet H₂. A metal part in these services is a violation unless rule M6 names it.

M4. Fasteners, supports, and frames in the head space of these vessels are non-metallic, or are metal outside the wetted and vapor zone and isolated from it.

M5. Thermoplastic limits. PVC-U to 60 °C. CPVC to 93 °C. These two limits are assumptions from published PVC-U and CPVC data, not measured in this plant. Above 60 °C the choice is CPVC. Above 93 °C the case is flagged and held; the alternative is a higher-rated thermoplastic or a lined part, never bare metal in M3 service. Temperature is taken from the graph; where the graph has none, the duty says so.

M6. Electrochemistry. Metal is allowed where it is the electrode: EW cathodes and anodes, CRU and BMED electrodes, fuel-cell and flow-battery stacks. Each such metal is listed on its duty with its potential role. Required with it:
- Galvanic couples. No two dissimilar metals in one electrolyte unless that couple is the cell. No metal bolt through a metal electrode into a different metal.
- Stray current. Every pipe and header between cells at different potential is non-metallic, with a stated electrolyte path length. Rectifier busbars are isolated from the frame. The frame is grounded on its own path, not through the liquor.
- Anodic dissolution. Every electrode carries a dissolution or coating-loss basis, or the item is held.
- Hydrogen embrittlement. Metal in wet H₂ or at a cathode is austenitic stainless or titanium only where the H₂ partial pressure and temperature are stated; titanium at a cathode is held for hydriding. Carbon and high-strength steel are not used in H₂ service.

M7. Metal is permitted where no polymer survives: cryogenic service, pyrolysis and melt hot faces, dry O₂ (polymers ignite), dry hydrocarbon, non-aqueous heat-transfer oil, dry hot gas held above its acid dew point, dry combustible-dust housings that must be conductive and grounded, and H₂ vent stacks exposed to flame. Each case is isolated from any electrolyte by a dielectric flange (M6). Each such unit states which of these applies.

## 2. Audit, 2026-10-15

Every present unit's section 3 was read against M1 to M7.

Fixed in this pass (clear violations, section 3 rewritten, no rate change):
- PVC-U, acid-regen and leach liquors (M2): BMED_ACID, BMED_BASE, POLISH_BANK, CONTINUOUS_RECYCLE, CRU, FLOAT_SINK, S13_CLASS_TREAT, SALT_FEED. LEACH_CSTR_1 is changed with its model.
- PVC-U, oxidizing or reducing wet service (M3): WS_KOH, WS_PHOS, WS_AMMONIA, WS_HF_ED, WET_BENCH, GREY_TREAT, BLACK_DIGEST, MEOH_FERM.
- PVC-U scrubbers (M2, M3): ACID_POLISH_SCRUB, ALK_SCRUBBER, NOX_SCRUB, MET_SCRUB.
- PVC-U or HDPE water tanks (M1): CATCH_TANK, ROOF_TANK, REMIN.
- Glass or PVC-U, 316L removed (M3): ACETOX, ACEX, ALD, BUCL, FORM, GLYOXAL, IMID, MEAM, QUAT.
- LEACH_CSTR_1 tank: 316L withdrawn. PVC-U in Rev A, corrected to CPVC in Rev F on the liquor temperature (section 7).

Flagged on temperature (M5):
- LEACH_CSTR_1, HL-Q3-A/B-HX5 ports. Q3 supply 95 °C on the graph exceeds PVC-U and the CPVC limit. CPVC is the thermoplastic alternative. Held.

Ambiguous, not changed (each is a TASK_PLAN X-MAT-06 item):
- EW_1 to EW_9. 316L cathode, Ti/PbO₂ anode, PVC/FRP tank. Electrodes allowed under M6; dissolution and stray-current basis missing.
- HX8. Titanium plates in EW aisle liquor. Ti in reducing chloride liquor is a hydriding and crevice risk. Non-metallic exchanger not evaluated.
- ZNBR2_BR2_REGEN. 316L shell with wet Br₂. Violates M3. PVC is poor in wet Br₂; PVDF or glass not evaluated.
- GLASS_DIGEST. 316L, digest liquor not characterized; may be HF or alkali.
- WS_NITRIC, WS_PEROX. Strong oxidizers. PVC limit depends on concentration, not on the graph.
- WS_SOLV, WS_DOPE, WS_SLURRY. Solvent and dopant compatibility not stated.
- ETOH_STILL, BUOH_STILL. 316L for boiling solvent; fermentation broth may be reducing and acidic. Temperature exceeds PVC.
- VCD_TRAIN, FAB_UPW_TANK, HDR_UPW, BMED_UPW_POLISH. UPW and distillation; PVC leaching and temperature not stated.
- HDR_H2, RELIEF_H2, H2_DRYER. 316L in H₂. M6 embrittlement basis needed.
- HDR_O2. 316L. Dry O₂ is an M7 metal service; wet O₂ is not stated.
- FLUE_KO, BAGHOUSE, AFTERBURNER_FLUE. Hot flue with acid condensate. M7 vs M3 depends on temperature not on the graph.
- Q1_A to Q4_B, GEO_*, CURTAIL, HEAT_SINK, Q4_BUS, MET_HX_Q4, CRYO_HX_Q4, HYDRO_SET, TERRACE_IRRIG, NUTRIENT_DOSE. Water loops in 316L; no redox service stated. Q1/Q2 temperatures exceed thermoplastics.
- MEOH_SYNTH, MEOH_TANK, MEOH_COND. Methanol; reducing synthesis gas. M6/M7 basis needed.
- OIL sector (carbon steel). Pyrolysis is reducing but hot. M7 applies to the hot face; cut tanks and condensers need a stated temperature.
- MFG units with "316L where wet". Wet service not named.

Compliant as written: CRYO sector (M7 cryogenic), MET_MELT and SIC_FURNACE (M7 hot face), electrical nodes and stacks with no wetted alloy (M6 for the stacks), farm and habitation units already HDPE or PVC.

## 3. Decisions, Rev B

### 3.1 ZNBR2_BR2_REGEN, wet bromine scrub

Service from the graph: S69 is the ZNBR2 headspace purge, 30 m³/h at ambient humidity with 10 ppmv Br₂. The liquor (S69B) is NaBr after ORP, with 2 M NaOH make-up. Br₂ + 2 NaOH gives NaBr + NaOBr, so the liquor is a caustic hypobromite: oxidizing (M3) and above pH 12. Temperature is ambient on the edge.

| Candidate | Chemistry | Temperature | Cost and supply | Result |
| --- | --- | --- | --- | --- |
| Borosilicate glass 3.3 | Inert to Br₂; etched by hot strong caustic | Well above service | Process-glass sections, moderate cost, fragile | Not chosen: 2 M NaOH make-up point |
| Glass-lined steel | As glass; steel behind | — | Expensive at this size | Not chosen |
| PVDF homopolymer | Br₂ water rated to 100 °C, Br₂ gas to 65 °C [S1]; homopolymer limited to pH 12 at ambient [S2] | — | Sheet and pipe common | Not chosen: caustic liquor above pH 12 |
| ECTFE | Resists halogens and caustic | — | Sheet lining; costly, few fabricators | Fallback only |
| PTFE/PFA lining | Inert | — | Costly at this size | Not chosen |
| FRP vinyl ester, C-veil | Wet halogen service is common; caustic needs a synthetic veil, not C-glass | — | Shop fabrication | Not chosen: two-veil liner for one small column |
| PP | No resistance to halogens or strong oxidants [S4] | — | Cheap | Excluded |
| PVC-U | Resists NaOH and hypohalite at ambient; Br₂ at ppm level in air; limited in concentrated Br₂ | 60 °C limit [S3] | Cheapest; pipe, sheet, Pall rings common | **Chosen** |

Decision. PVC-U shell, sump, liquor piping, and Pall-ring packing. FKM gaskets. Basis: the Br₂ load is 10 ppmv in air and is converted to bromide and hypobromite in a caustic liquor, where PVC is suitable and PVDF is not. Held: the hypobromite rating at the liquor ORP is not on the cited chart; a coupon test is a TASK_PLAN X-MAT-06 item. If the S69 Br₂ concentration rises above trace, the inlet spool changes to borosilicate glass.

### 3.2 LEACH_CSTR_1, HX-5 ports at 95 °C

Service from the graph: HL-Q3-A/B-HX5 bring Q3 water at 95 °C supply and 85 °C return. The exchanger sits in leach liquor (HCl and NaClO₃, high ORP, chloride). The leach liquor itself runs at 70–85 °C (GLOSSARY Leach/Salria; 77.5 °C in the AQS-DUTY-008 HX-5 basis; graph param liquor_T_C since Rev F). The tank is therefore CPVC, not PVC-U (M5); see section 7.

| Candidate | Chemistry | Temperature | Cost and supply | Result |
| --- | --- | --- | --- | --- |
| CPVC | Good with HCl and chlorate | 93 °C limit with derating to 0.20 at 93 °C [S3, S5] | Cheap | Not chosen: 95 °C supply is above the limit |
| PP-H | Good with hot water; no resistance to strong oxidants [S4] | 100 °C, 80 °C continuous [S4] | Cheap | Not chosen: chlorate liquor on the outside |
| Borosilicate glass 3.3 coil | Inert to HCl and chlorate | Above service; thermal shock limit | Moderate cost, fragile | Fallback |
| Impregnated graphite | Inert; electrically conductive | Above service | Costly | Not chosen: conductor in an electrochemical plant |
| PVDF homopolymer | Chlorinated acid brine rated to 95 °C [S1]; hot water well above | Meets 95 °C | Tube, fittings, and flanges common | **Chosen** |
| Metal (Ti, 316L) | — | — | — | Excluded by M3 |

Design change considered. Lowering the Q3 supply is not taken: Q3 also serves HX-4 and HX-6 at the same tier (AQS-HEAT-LADDER-001), so the tier temperature stays. A blending loop to below 60 °C would need a new edge and is not taken.

Decision. HX-5 is a PVDF immersion coil with PVDF DN20 nozzles, bolted through PVDF flanges to PVC-U stub flanges on the tank, FKM gaskets. The Q3 metal piping ends at a dielectric isolating flange outside the tank (M6). A liquor high-temperature trip at 88 °C (assumption, 5 K below the CPVC limit) closes the Q3 supply. Coil area: TASK_PLAN X-MAT-11.

## References

- [S1] Arkema, Kynar PVDF Chemical Resistance Chart (maximum use temperatures), https://page.arkema.com/rs/253-HSZ-754/images/kynar-pvdf-chemical-resistance-chart.pdf
- [S2] Arkema, Kynar Chemical Resistance and Fuel Resistance (pH limits), https://hpp.arkema.com/en/product-families/kynar-fluoropolymer-family/chemical-resistance-fuel-resistance/
- [S3] Spears Manufacturing, PVC and CPVC Engineering Guide (maximum service temperature PVC 60 °C, CPVC 93 °C), https://spearsmfg.com/listings_approvals/036_IP-4-1125-Complete_web.pdf
- [S4] SIMONA, PP tech.info (service temperature, no resistance to strong oxidants and halogens), https://www.simona.de/fileadmin/user_upload/Medien/Mediacenter/Technische_Informationen/tech.info_SIMONA_PP_-english-.pdf
- [S5] PPI TN-62, CPVC piping temperature derating, https://www.plasticpipe.org/common/Uploaded%20files/Technical/PPI-TN-62.pdf

## 4. Unit decisions, Rev C

### 4.1 HX8, EW aisle liquor cooler

Graph: liquor 55 → 51 °C from EW_1 (IA-HX8), Q4 treated water 45 → 49 °C, 4.572 kW, 0.51 m². The liquor is EW catholyte-side chloride, reducing at the cathode, and the feed envelope (AQS-ASSAY-001 Rev C) admits halides including fluoride.

- Ti Grade 2 (present): crevice attack in brine is unlikely below 70 °C [S6], but reducing HCl attacks unalloyed Ti, useful only to about 7 % HCl at room temperature with resistance falling with temperature [S6]. Ti is not used where HF can be present [S7]. Violates M3.
- Ti-Pd (Grade 7): best Ti grade in reducing acid and crevices [S6, S7], but still metal in reducing chloride (M3), still attacked by fluoride, and costly.
- Impregnated graphite plate or block: inert to HCl and HF; conductive, so it is a stray-current path and a noble galvanic partner in the EW aisle; costly.
- PTFE tube bundle: inert; costly; low conductivity.
- PVDF tube or immersion coil: chlorinated acid brine to 95 °C, brine to 140 °C [S1]; insulating; tube and fittings common.

Decision. PVDF tube-in-shell exchanger, PVDF tubes and tube sheets on the liquor side, PVC-U shell on the Q4 water side (49 °C, inside M5). No metal wetted part. Held: area at the lower PVDF tube conductance is not calculated; 0.51 m² on the graph is for plates and is not reused.

### 4.2 ETOH_STILL and BUOH_STILL

Graph: 400 × 400 × 1500 mm and 300 × 300 × 1200 mm; 0.46 and 0.13 kg/d feed. Ethanol boils at 78 °C, n-butanol at 118 °C, water at 100 °C; the broth from YEAST and ABE is acidic and the fermentation is reducing. All above M5 for PVC and CPVC.

Decision. Borosilicate glass 3.3 column, reboiler, and condenser, PTFE gaskets, heated from the heat ladder through a glass or PTFE coil. At this size glass is the cheapest inert option and is standard laboratory and pilot stock. No metal wetted part. A steel guard frame outside the glass carries the load and is not wetted. Flammable vapor: area classification is X-ELS-09.

### 4.3 AFTERBURNER_FLUE, FLUE_KO, BAGHOUSE

AFTERBURNER_FLUE. Graph: S67 at 300 °C, N₂/O₂/CO₂/NOx, pipe only. Dry hot gas: M7 applies while the wall stays above the acid dew point. Decision: 316L pipe, insulated to hold the wall above the acid dew point (dew point not on the graph; held), dielectric isolating flange at FLUE_KO.

FLUE_KO. Graph: S67 at 300 °C in, S67B out at 30 °C and dew point ≤ −40 °C, plus IA-LEACH-FLUE (leach vent, acid and chlorine bearing) and S70 condensables. The vessel is where the acid condensate forms: wet, acidic, oxidizing (NOx, Cl₂). Decision: FRP vinyl ester with a C-veil liner for the vessel and mesh-pad support, PVDF mesh pad, borosilicate glass 3.3 inlet spool for the 300 °C gas. No metal wetted part. Held: the inlet quench or cooling that brings 300 °C to below the FRP limit is not on the graph; adding it needs an edge and is a TASK_PLAN item.

BAGHOUSE. Graph: dry dusts (S19 shredded feed fines, mill dust, kerf, wire scrap), ambient. The dust can be combustible metal. Dry and ambient, so M3 does not apply; the combustible-dust rules do: the housing is conductive, bonded, and grounded, with deflagration venting or suppression and isolation [S9]. Decision: carbon steel housing, painted, bonded and grounded; antistatic polyester bags; rotary valve to a dry discharge. The captured dust (IA-BAG-01) is wetted only after a dielectric break, in a PVC-U sluice into LEACH_CSTR_1.

### 4.4 Q1 and Q2 heat loops

Graph: Q1_A/B at 250 °C and Q2_A/B at 150 °C, synthetic thermal oil, hydrogenated terphenyl class (HL-AFTERBURNER-Q1-A, HL-GLASS_BURNOUT-Q2-A). No water and no electrolyte, so no galvanic cell forms in the loop. No commodity polymer survives 250 °C. Decision: carbon steel, ASTM A106 Gr B pipe, welded joints, spiral-wound 304/graphite gaskets, per the fluid maker's system guide [S8]; M7 (non-aqueous heat-transfer oil). Each Q1/Q2 loop that ends at an exchanger touching an electrolyte or a Q3/Q4 water loop has a dielectric isolating flange there (M6). Water chemistry does not apply to these loops; it applies to Q3 and Q4 (X-MAT-06).

### References, Rev C

- [S6] TIMET, Corrosion Resistance of Titanium, https://www.timet.com/assets/local/documents/technicalmanuals/corrosion.pdf
- [S7] Titanium in the Geothermal Industry (IGA, Szeged), https://pangea.stanford.edu/ERE/pdf/IGAstandard/EGC/szeged/O-7-10.pdf
- [S8] Eastman, Therminol heat transfer fluids system design (carbon steel pipe A106 Gr B, welded joints), https://www.eastman.com/content/dam/eastman/corporate/en/literature/t/tf8695a.pdf
- [S9] OSHA Technical Manual Section IV Chapter 6, Combustible Dusts; NFPA 652 and NFPA 660 Chapter 22, https://www.osha.gov/sites/default/files/otm%5FsecIV%5Fchap6.pdf

## 5. Oxidizer reagents, Rev D

WS_NITRIC, HNO3, and WS_PEROX are defined in AQS-DSN-OX-001, `docs-authority/OXIDIZER_REAGENTS.md`. Nitric at no more than 2 M: PVC-U storage, PVDF pumps and absorber, 304L excluded under M3. Peroxide at no more than 6 wt%: HDPE tank, PVDF piping, PTFE/FKM seals; passivated stainless and aluminum, though accepted by the producer, are excluded under M3.

- [S10] Vinidex, Chemical Performance of PVC, https://www.vinidex.com.au/app/uploads/pdf/Chemical-Performance-of-PVC.pdf
- [S11] Solvay, Materials of Construction for the Storage of H₂O₂, https://www.solvay.com/sites/solvay_solvay/files/2019-10/H2O2%20Materials%20of%20Construction%20for%20the%20Storage%20of%20H2O2.pdf
- [S12] Solvay, Safety and Handling of Hydrogen Peroxide, https://www.solvay.com/sites/solvay_solvay/files/2019-10/H2O2%20Safety%20and%20Handling%20of%20Hydrogen%20Peroxide.pdf

## 6. Hydrogen service, Rev E

AQS-REV-H2-001, `docs-authority/H2_EMBRITTLEMENT_REVIEW.md`, applies M6 to every H₂-wetted unit:
- No carbon, low-alloy, or high-strength steel.
- 316L, annealed, for dry H₂ and for EW cathodes.
- PVC-U for the wet acid HDR_H2 header.
- HDPE, PA, or copper only for dry low-pressure lines.
- Pressure-dependent checks are held until the graph carries P, T, and purity. Sources S13 to S15.

## 7. Leach liquor temperature, Rev F

The Rev A to E text treated the leach liquor temperature as absent from the graph. It is in the repo: GLOSSARY gives Leach / Salria at 70–85 °C, and the AQS-DUTY-008 HX-5 duty is built at 77.5 °C. It is now on the LEACH_CSTR_1 node as `liquor_T_C` (77.5 °C, band 70–85 °C, study).

Under M5 this exceeds PVC-U (60 °C). The tank, headers, and stubs are CPVC (limit 93 °C [S3], specific gravity 1.51 [S3]). This is the material AQS-NZ-001 had originally. The high-temperature trip is 88 °C (assumption). CPVC strength derates steeply with temperature (factor 0.25 at 82 °C for pressure pipe [S5]), so the wall check at 85 °C is part of the LEACH_CSTR_1 sizing task. Units on the same liquor loop with no temperature on the graph (CONTINUOUS_RECYCLE, FLOAT_SINK, S13_CLASS_TREAT) stay on PVC-U only if their liquor is at or below 60 °C. That check is X-MAT-09.

### 3.3 HX-5 glass coil, Rev G

Decision (owner approval 2026-10-15). HX-5 is a borosilicate glass 3.3 coil. Glass is inert to HCl and chlorate at 95 °C and conducts heat about six times better than PVDF (1.2 vs 0.18 W/mK), so the coil is smaller: 4.22 m² in the natural-convection case of AQS-DUTY-049, 2.65 m² if agitation is confirmed. The 4.22 m² case is built. Tube 25 × 3 mm, 53.7 m, two concentric helices D 600 and 900 mm (arrangement is an assumption, see AQS-REG-002). Glass density 2230 kg/m³ and permitted thermal shock 120 K per ISO 3585 (S17); Q3 supply 95 °C into liquor 70–85 °C is a 25 K step. The coil sits on PTFE pads. An agitator guard is held for X-MAT-09. Section 3.2's PVDF coil is superseded; the 88 °C trip stands.

S17. ISO 3585:1998, Borosilicate glass 3.3 — Properties.

### 4.5 HX8 PVDF bundle, Rev H

Decision (owner approval 2026-10-15). HX8 is a PVDF shell-and-tube bundle, 7.53 m² at U 101 W/m²K (AQS-DUTY-049). Rationale against isolated impregnated graphite (0.85 m²):
- Graphite conducts. In the EW aisle it would sit in the liquor path between cells at different potentials; isolation must hold at both liquor connections and the Q4 side for the life of the plant. A failed isolator gives a stray-current path and a noble galvanic partner (M6). PVDF has no such failure mode.
- Graphite is brittle and fails on thermal or pressure shock; PVDF tolerates handling and water hammer.
- The penalty is area and footprint (about nine times), which is acceptable at 7.5 m².
Graphite is not clearly better, so the approved default stands. Section 4.1's open graphite option is closed.

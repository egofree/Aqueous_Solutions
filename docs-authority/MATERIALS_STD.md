# Materials standard

Document number: AQS-STD-002
Revision: L
Date: 2026-10-21
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
| I | Material temperatures on thermoplastic inlets (X-MAT-09); HX-5 coil guard. | 2026-10-15 |
| J | EW electrode materials in chloride (X-MAT-18). | 2026-10-15 |
| K | Galvanic and stray-current design for the EW aisle (X-MAT-07). | 2026-10-15 |
| L | Service-class selection guide across the assay envelope added as section 12 (X-MAT-01). Line-list class rules keyed to the guide families: the "aqueous process, default thermoplastic" catchall is retired, hydrocarbon/fuel cuts go to M2 (carbon steel, dry, per the issued duties), wet methanol and solvents to M1 (316L per the issued duties), melt pours become launder rows (not piped), and the fluoro synthesis train, dopant concentrates and molten-salt pot brines carry per-duty-sheet materials pending a PIP-003 Rev B class. Section 8 checker aligned: unit map equals the issued CPVC and PVDF members, and the BMED inlets are derived from the booked X-RSZ-04 trim duties with driver heat capacities; 0 exceed, 33 rows on the registered 40 °C ambient assumption (A-M-269). Also refreshes the section 10 trim table to the X-RSZ-04 booked duty and flow basis. | 2026-10-21 |

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

## 8. Material temperatures on thermoplastic inlets, Rev I (table refreshed Rev L)

X-MAT-09. Script `docs-authority/_material_temps.py` checks every liquid edge into a thermoplastic unit against the M5 limit of its material. The unit map is the issued section 12 material basis: CPVC for LEACH_CSTR_1, FLOAT_SINK, EW_1, ACID_POLISH_SCRUB and NOX_SCRUB (the section 8 85 °C draw resolution and section 7), PVDF for HX8, WS_NITRIC, WS_PEROX, HNO3 and WS_HF_ED, PVC-U elsewhere per section 2. The IA-BMED-03/04 inlet temperatures are derived: booked X-RSZ-04 trim duty minus flow times driver heat capacity (cp_hcl20_kJ_kgK 3.0, cp_naoh20_kJ_kgK 3.6, PERRY9). Where no temperature exists on or upstream of an edge the check prints 40 °C, the 0.4 % site dry bulb 37.8 °C of AQS-SITE-002 rounded up.

| Edge | From | To | Material | T °C | Limit °C | Check | Basis |
| --- | --- | --- | --- | --- | --- | --- | --- |
| IA-SCRUB-SRC | LEACH_CSTR_1 | ACID_POLISH_SCRUB | CPVC | 85.0 | 93 | ok | edge T_C |
| IA-BLK-01 | HABITATION | BLACK_DIGEST | PVC-U | 40.0 | 60 | ok | assumption: no heat input stated upstream; 40 C, the 0.4 % site dry bulb 37.8 C (AQS-SITE-002) rounded up (A-M-269) |
| IA-URINE | HABITATION | BLACK_DIGEST | PVC-U | 40.0 | 60 | ok | assumption: no heat input stated upstream; 40 C, the 0.4 % site dry bulb 37.8 C (AQS-SITE-002) rounded up (A-M-269) |
| IA-BMED-03 | LEACH_CSTR_1 | BMED_ACID | PVC-U | 35.1 | 60 | ok | LEACH liquor band maximum 85 C (liquor_T_C band); in-line water-cooled trim IA-BMED-03-TRIM (0.78 kW, cp 3.0 kJ/(kg K) per cp_hcl20_kJ_kgK, dT 49.9 K; X-MAT-19 section 10) |
| IA-EVAP_ACID-COND | EVAP_ACID | BMED_ACID | PVC-U | 49.1 | 60 | ok | edge T_C |
| IA-VS-SPENT | EVAP_ACID_VS | BMED_ACID | PVC-U | 40.0 | 60 | ok | assumption: no heat input stated upstream; 40 C, the 0.4 % site dry bulb 37.8 C (AQS-SITE-002) rounded up (A-M-269) |
| IA-BMED-04 | LEACH_CSTR_1 | BMED_BASE | PVC-U | 35.7 | 60 | ok | LEACH liquor band maximum 85 C (liquor_T_C band); in-line water-cooled trim IA-BMED-04-TRIM (1.027 kW, cp 3.6 kJ/(kg K) per cp_naoh20_kJ_kgK, dT 49.3 K; X-MAT-19 section 10) |
| IA-EVAP_BASE-COND | EVAP_BASE | BMED_BASE | PVC-U | 50.6 | 60 | ok | edge T_C |
| IA-ESS-HYDRO-DIS | ROOF_TANK | CATCH_TANK | PVC-U | 25.0 | 60 | ok | upstream ROOF_TANK outlet IA-FLUE-QUENCH (edge conditions) |
| S22 | ROOF_TANK | CATCH_TANK | PVC-U | 25.0 | 60 | ok | upstream ROOF_TANK outlet IA-FLUE-QUENCH (edge conditions) |
| IA-POL-02 | POLISH_BANK | CONTINUOUS_RECYCLE | PVC-U | 40.0 | 60 | ok | assumption: no heat input stated upstream; 40 C, the 0.4 % site dry bulb 37.8 C (AQS-SITE-002) rounded up (A-M-269) |
| S66 | ACID_POLISH_SCRUB | CRU | PVC-U | 40.0 | 60 | ok | assumption: no heat input stated upstream; 40 C, the 0.4 % site dry bulb 37.8 C (AQS-SITE-002) rounded up (A-M-269) |
| VDF_HCL_TO_CRU | VDF_SYN | CRU | PVC-U | 40.0 | 60 | ok | assumption: no heat input stated upstream; 40 C, the 0.4 % site dry bulb 37.8 C (AQS-SITE-002) rounded up (A-M-269) |
| TFE_HCL_TO_CRU | TFE_SYN | CRU | PVC-U | 40.0 | 60 | ok | assumption: no heat input stated upstream; 40 C, the 0.4 % site dry bulb 37.8 C (AQS-SITE-002) rounded up (A-M-269) |
| IA-EW-04 | LEACH_CSTR_1 | EW_1 | CPVC | 85.0 | 93 | ok | LEACH liquor band maximum 85 C (liquor_T_C band) |
| IA-EW-01 | EW_1 | EW_2 | PVC-U | 40 | 60 | ok | upstream EW_1 outlet IA-EW1-H2 (edge T_C) |
| IA-EW-02 | EW_2 | EW_3 | PVC-U | 40 | 60 | ok | upstream EW_2 outlet IA-EW2-H2 (edge T_C) |
| IA-EW-03 | EW_3 | EW_4 | PVC-U | 40.0 | 60 | ok | assumption: no heat input stated upstream; 40 C, the 0.4 % site dry bulb 37.8 C (AQS-SITE-002) rounded up (A-M-269) |
| IA-EW-10 | EW_4 | EW_5 | PVC-U | 40 | 60 | ok | upstream EW_4 outlet IA-EW4-H2 (edge T_C) |
| IA-EW-05 | EW_5 | EW_6 | PVC-U | 40.0 | 60 | ok | assumption: no heat input stated upstream; 40 C, the 0.4 % site dry bulb 37.8 C (AQS-SITE-002) rounded up (A-M-269) |
| IA-EW-06 | EW_6 | EW_7 | PVC-U | 40.0 | 60 | ok | assumption: no heat input stated upstream; 40 C, the 0.4 % site dry bulb 37.8 C (AQS-SITE-002) rounded up (A-M-269) |
| IA-EW-07 | EW_7 | EW_8 | PVC-U | 40.0 | 60 | ok | assumption: no heat input stated upstream; 40 C, the 0.4 % site dry bulb 37.8 C (AQS-SITE-002) rounded up (A-M-269) |
| IA-EW-08 | EW_8 | EW_9 | PVC-U | 40.0 | 60 | ok | assumption: no heat input stated upstream; 40 C, the 0.4 % site dry bulb 37.8 C (AQS-SITE-002) rounded up (A-M-269) |
| IA-SINK-01 | LEACH_CSTR_1 | FLOAT_SINK | CPVC | 85.0 | 93 | ok | edge T_C |
| IA-ZNBR-BD | ZNBR2 | GREY_TREAT | PVC-U | 25.0 | 60 | ok | edge T_C |
| IA-BLK-GREY | BLACK_DIGEST | GREY_TREAT | PVC-U | 40.0 | 60 | ok | assumption: no heat input stated upstream; 40 C, the 0.4 % site dry bulb 37.8 C (AQS-SITE-002) rounded up (A-M-269) |
| IA-REC-01 | CONTINUOUS_RECYCLE | LEACH_CSTR_1 | CPVC | 40.0 | 93 | ok | assumption: no heat input stated upstream; 40 C, the 0.4 % site dry bulb 37.8 C (AQS-SITE-002) rounded up (A-M-269) |
| IA-WET-FLOAT-01 | FLOAT_SINK | LEACH_CSTR_1 | CPVC | 40.0 | 93 | ok | assumption: no heat input stated upstream; 40 C, the 0.4 % site dry bulb 37.8 C (AQS-SITE-002) rounded up (A-M-269) |
| S10 | WET_BENCH | LEACH_CSTR_1 | CPVC | 40.0 | 93 | ok | assumption: no heat input stated upstream; 40 C, the 0.4 % site dry bulb 37.8 C (AQS-SITE-002) rounded up (A-M-269) |
| S28 | VCD_TRAIN | LEACH_CSTR_1 | CPVC | 40.0 | 93 | ok | upstream VCD_TRAIN outlet IA-VCD-BD (edge T_C) |
| S68 | CRYO_AHU | LEACH_CSTR_1 | CPVC | 10.0 | 93 | ok | upstream CRYO_AHU outlet IA-HVAC-COND (edge T_C) |
| IA-GREY-01 | GREY_TREAT | LEACH_CSTR_1 | CPVC | 40.0 | 93 | ok | edge T_C |
| IA-CRU-01 | CRU | LEACH_CSTR_1 | CPVC | 40.0 | 93 | ok | edge T_C |
| IA-UPW-REJ | BMED_UPW_POLISH | LEACH_CSTR_1 | CPVC | 40.0 | 93 | ok | edge T_C |
| IA-DIG-LIQ | GLASS_DIGEST | LEACH_CSTR_1 | CPVC | 40.0 | 93 | ok | edge T_C |
| IA-VCD-BD | VCD_TRAIN | LEACH_CSTR_1 | CPVC | 40.0 | 93 | ok | edge T_C |
| IA-NUT-LEACH | NUTRIENT_DOSE | LEACH_CSTR_1 | CPVC | 40.0 | 93 | ok | edge T_C |
| IA-FEED-01 | HOPPER | LEACH_CSTR_1 | CPVC | 40.0 | 93 | ok | edge T_C |
| IA-BAG-01 | BAGHOUSE | LEACH_CSTR_1 | CPVC | 40.0 | 93 | ok | edge T_C |
| IA-FAB-SPENT | WAFER_FAB | LEACH_CSTR_1 | CPVC | 40.0 | 93 | ok | edge T_C |
| IA-FC-LEACH | FUEL_CELL | LEACH_CSTR_1 | CPVC | 60.0 | 93 | ok | edge T_C |
| IA-SIC-RET | NUTRIENT_DOSE | LEACH_CSTR_1 | CPVC | 40.0 | 93 | ok | edge T_C |
| IA-H2O-MU | NORTH_DOCK | LEACH_CSTR_1 | CPVC | 40.0 | 93 | ok | assumption: no heat input stated upstream; 40 C, the 0.4 % site dry bulb 37.8 C (AQS-SITE-002) rounded up (A-M-269) |
| IA-ACID-01 | EVAP_ACID | LEACH_CSTR_1 | CPVC | 49.1 | 93 | ok | edge T_C |
| IA-BASE-PPT | EVAP_BASE | LEACH_CSTR_1 | CPVC | 50.6 | 93 | ok | edge T_C |
| S46 | BACKUP_GEN | NOX_SCRUB | CPVC | 40.0 | 93 | ok | assumption: no heat input stated upstream; 40 C, the 0.4 % site dry bulb 37.8 C (AQS-SITE-002) rounded up (A-M-269) |
| IA-LEACH-NOX | LEACH_CSTR_1 | NOX_SCRUB | CPVC | 85.0 | 93 | ok | edge T_C |
| IA-FC-FIX | FUEL_CELL | NOX_SCRUB | CPVC | 60.0 | 93 | ok | edge T_C |
| IA-CLOSE-1 | LEACH_CSTR_1 | NOX_SCRUB | CPVC | 85.0 | 93 | ok | edge T_C |
| IA-EW-09 | EW_9 | POLISH_BANK | PVC-U | 40.0 | 60 | ok | assumption: no heat input stated upstream; 40 C, the 0.4 % site dry bulb 37.8 C (AQS-SITE-002) rounded up (A-M-269) |
| MO_CELL_RAFFINATE | MO_CELL | POLISH_BANK | PVC-U | 40.0 | 60 | ok | assumption: no heat input stated upstream; 40 C, the 0.4 % site dry bulb 37.8 C (AQS-SITE-002) rounded up (A-M-269) |
| IA-UPW-REMIN | BMED_UPW_POLISH | REMIN | PVC-U | 40.0 | 60 | ok | edge T_C |
| IA-ESS-HYDRO-CHG | CATCH_TANK | ROOF_TANK | PVC-U | 40.0 | 60 | ok | assumption: no heat input stated upstream; 40 C, the 0.4 % site dry bulb 37.8 C (AQS-SITE-002) rounded up (A-M-269) |
| S23 | CATCH_TANK | ROOF_TANK | PVC-U | 40.0 | 60 | ok | assumption: no heat input stated upstream; 40 C, the 0.4 % site dry bulb 37.8 C (AQS-SITE-002) rounded up (A-M-269) |
| IA-HVAC-COND | CRYO_AHU | ROOF_TANK | PVC-U | 10.0 | 60 | ok | edge T_C |
| IA-GREY-RET | GREY_TREAT | ROOF_TANK | PVC-U | 40.0 | 60 | ok | edge T_C |
| IA-POT-01 | REMIN | ROOF_TANK | PVC-U | 25.0 | 60 | ok | edge T_C |
| IA-NOX-H2O | NOX_SCRUB | ROOF_TANK | PVC-U | 40.0 | 60 | ok | edge T_C |
| S09 | BMED_ACID | WET_BENCH | PVC-U | 40.0 | 60 | ok | assumption: no heat input stated upstream; 40 C, the 0.4 % site dry bulb 37.8 C (AQS-SITE-002) rounded up (A-M-269) |
| S27 | FAB_UPW_TANK | WET_BENCH | PVC-U | 40.0 | 60 | ok | assumption: no heat input stated upstream; 40 C, the 0.4 % site dry bulb 37.8 C (AQS-SITE-002) rounded up (A-M-269) |
| S31 | WS_HF_ED | WET_BENCH | PVC-U | 40.0 | 60 | ok | assumption: no heat input stated upstream; 40 C, the 0.4 % site dry bulb 37.8 C (AQS-SITE-002) rounded up (A-M-269) |
| S32 | WS_PEROX | WET_BENCH | PVC-U | 40.0 | 60 | ok | assumption: no heat input stated upstream; 40 C, the 0.4 % site dry bulb 37.8 C (AQS-SITE-002) rounded up (A-M-269) |
| S33 | WS_AMMONIA | WET_BENCH | PVC-U | 40.0 | 60 | ok | assumption: no heat input stated upstream; 40 C, the 0.4 % site dry bulb 37.8 C (AQS-SITE-002) rounded up (A-M-269) |
| S35 | WS_KOH | WET_BENCH | PVC-U | 40.0 | 60 | ok | assumption: no heat input stated upstream; 40 C, the 0.4 % site dry bulb 37.8 C (AQS-SITE-002) rounded up (A-M-269) |
| S34 | WS_NITRIC | WET_BENCH | PVC-U | 40.0 | 60 | ok | assumption: no heat input stated upstream; 40 C, the 0.4 % site dry bulb 37.8 C (AQS-SITE-002) rounded up (A-M-269) |
| S34B | WS_PHOS | WET_BENCH | PVC-U | 40.0 | 60 | ok | assumption: no heat input stated upstream; 40 C, the 0.4 % site dry bulb 37.8 C (AQS-SITE-002) rounded up (A-M-269) |
| IA-SOLV-WB | WS_SOLV | WET_BENCH | PVC-U | 40.0 | 60 | ok | edge T_C |
| IA-NH3-SRC | HDR_N2 | WS_AMMONIA | PVC-U | 40.0 | 60 | ok | edge T_C |
| IA-HF-PROD | HF_GEN | WS_HF_ED | PVDF | 40.0 | 120 | ok | assumption: no heat input stated upstream; 40 C, the 0.4 % site dry bulb 37.8 C (AQS-SITE-002) rounded up (A-M-269) |
| IA-BMED-02 | BMED_BASE | WS_KOH | PVC-U | 40.0 | 60 | ok | assumption: no heat input stated upstream; 40 C, the 0.4 % site dry bulb 37.8 C (AQS-SITE-002) rounded up (A-M-269) |
| IA-BMED-01 | BMED_ACID | WS_NITRIC | PVDF | 40.0 | 120 | ok | assumption: no heat input stated upstream; 40 C, the 0.4 % site dry bulb 37.8 C (AQS-SITE-002) rounded up (A-M-269) |
| IA-H2O2-SRC | HDR_O2 | WS_PEROX | PVDF | 40.0 | 120 | ok | edge T_C |
| IA-PEROX-H2O | ROOF_TANK | WS_PEROX | PVDF | 25.0 | 120 | ok | edge T_C |
73 edges; 0 exceed; 33 on the ambient assumption.

Resolution of the former exceedances (the Rev K table ran at the Rev AC graph): the 85 °C hot-leach draws into FLOAT_SINK, EW_1, ACID_POLISH_SCRUB and NOX_SCRUB now run in CPVC (P2/M5, limit 93 °C, operated ≤88 °C); WS_HF_ED runs PVDF (limit 120 °C); BMED_ACID and BMED_BASE take the water-cooled trim exchangers of section 10 — the derived inlets 35.1 °C and 35.7 °C land at the 35 °C membrane target within the booked-duty margin of X-RSZ-04. EW_2 to EW_9 stay PVC-U at their 55 °C class temperature.

HX-5 coil guard. The impeller (D 450 mm, AQS-DUTY-050) turns inside the coil (ID 575 mm), 62 mm radial clearance. The coil is clamped to four PVDF guide posts from the pads to the lid so it cannot move into the impeller; no separate guard sleeve, which would cut the flow across the coil.

## 9. EW electrodes in chloride with anodic Cl₂, Rev J

X-MAT-18. Service: chloride liquor (HCl with metal chlorides, 55–77.5 °C), anodic Cl₂ evolution on every cell (EDGE_RATING_DUTY), side-reaction H₂ at EW_1, EW_2, EW_4 and EW_9 cathodes.

| Part | Was | Decision | Reason |
| --- | --- | --- | --- |
| Cathode blank | 316L, 3 mm | Titanium Grade 2 (ASTM B265), 3 mm, PVC edge strips | 316L pits in hot chloride with dissolved Cl₂, and the pits fix the deposit; titanium is passive in wet chlorine and hot chloride brine and is the usual blank in chloride electrowinning [S21]. |
| Anode | Ti mesh with PbO₂ | Ti mesh with mixed metal oxide (RuO₂–IrO₂–TiO₂, dimensionally stable anode) | The chlor-alkali anode; low Cl₂ overpotential and long life in chloride [S22]. PbO₂ adds lead to the liquor and the deposit and does not suit Cl₂ service. |
| Hanger bars and contacts | copper | Copper above the liquor and the vapor line, Ti-clad where in spray | M6: conductors only, not wetted |

Hydrogen. Titanium takes up hydrogen as a cathode and forms brittle hydride, mostly above about 80 °C and at high current density [S21]. Cells at 55 °C run below that; EW_1 sees 77.5 °C at the inlet (X-MAT-09). Rule: Ti blanks on the H₂-making cells (EW_1, EW_2, EW_4, EW_9) are inspected for hydride (bend test) at each strip cycle for the first year; reverse current is not applied to Ti. AQS-REV-H2-001 carries this.

S21. Schutz R.W., Thomas D.E., "Corrosion of Titanium and Titanium Alloys", ASM Handbook Vol. 13, 1987.
S22. Trasatti S., "Electrocatalysis: understanding the success of DSA", Electrochimica Acta 45 (2000) 2377–2385.

## 10. Hot LEACH draws, Rev J addendum (X-MAT-19)

Script `docs-authority/_hot_draw_coolers.py`.

| Edge | kg/d | cp kJ/(kg K) | °C | Booked trim | Cooled inlet | Target |
| --- | --- | --- | --- | --- | --- | --- |
| IA-BMED-03 | 450.164 | 3.0 (cp_hcl20_kJ_kgK, PERRY9) | 85 → 35 | IA-BMED-03-TRIM 0.780 kW | 35.1 °C | BMED_ACID membrane inlet 35 C |
| IA-BMED-04 | 500.131 | 3.6 (cp_naoh20_kJ_kgK, PERRY9) | 85 → 35 | IA-BMED-04-TRIM 1.027 kW | 35.7 °C | BMED_BASE membrane inlet 35 C |

- IA-POT-01: superseded by X-RSZ-06. The potable makeup now comes from REMIN at 25 °C; the hot leach water bleed goes to VCD_TRAIN on IA-LEACH-VCD (123.296 kg/d, 85 °C), which is an evaporator duty, not a cooler. No coil. VCD_TRAIN wetted parts on this feed are Ti Gr 2 or PVDF-lined (acid chloride at 85 °C, §9 basis); the condensate is polished by BMED_UPW_POLISH before REMIN.
- IA-BMED-03 and IA-BMED-04: air cannot reach 35 °C at the 37.8 °C design dry bulb. They take a water-cooled trim exchanger on the GEO_GHEX ground loop. X-RSZ-04 books it at the resized flows: IA-BMED-03-TRIM 0.780 kW and IA-BMED-04-TRIM 1.027 kW (1.81 kW), taken from IA-E-LEACH, rejected by IA-GHEX-REJ. Outlet 35 °C.
- The IA-BMED-03/04 conditions and the IA-POT-01 composition were corrected (5c311be, X-RSZ-06).

## 11. Galvanic and stray current, EW aisle, Rev K

X-MAT-07. Script `docs-authority/_shunt_current.py`.

Electrolyte path. Liquor runs EW_1 → EW_9 in series (IA-EW-01 to IA-EW-08). Each cell has its own floating 6 V channel (AQS-ELEC-004), so in normal service no cell is referenced to another and no shunt current flows. With two simultaneous earth faults on opposite poles of two channels, up to 6 V can appear across the liquor link. At 30 S/m (assumption) a full DN50 link has 13.1 Ω at the 0.75 m pitch, 0.46 A. To hold stray current under 0.1 A (assumption) a full pipe needs 3.4 m. Decision: every cell-to-cell transfer is a free-fall overflow launder with an air break (open drop of at least 50 mm) into the next cell's feed box, so the liquid path is broken. Pipe length is then not relied on. Drains to a common sump also fall freely.

Busbars. Copper on non-conductive standoffs (glass-polyester or porcelain), creepage per the rectifier voltage; no busbar touches a tank lip, rack or pipe. Each channel's positive and negative bars run as a pair to keep loops small.

Frames and earthing. Tanks and racks are CPVC or PVC-U (no metal frame, M3). Any metal structure near the aisle (crane rail, walkway steel) is earthed to the ring (AQS-ELEC-005) and kept 150 mm clear of liquor and bars. DC stays floating with an insulation monitor per channel; the first earth fault alarms and is cleared before a second can complete a shunt path.

Metal piping. HDR_H2 (316L, class M1) leaves each H₂-making cell through a dielectric isolating flange and a condensate trap with a free-fall drain, so wet gas cannot carry liquor current into the header. Q4 water to HX8 is isolated by the PVDF bundle (section 4.5).

Electrode dissolution. Mixed-metal-oxide anodes (section 9) wear by coating loss; life is a vendor figure at the cell current density, not assumed here. Titanium cathodes are passive. On shutdown a cell with metal on the cathode and Cl₂ on the anode is a galvanic cell; reverse current strips the deposit and damages the oxide coating. Rule: on rectifier trip, the channel holds a protection current of 1 % of rating (study) or the cell is drained within 30 minutes; anodes are never left wetted and unpolarized against a loaded cathode.


### §11 check at the re-placed aisle (X-RSZ-03, seed Rev I)

Routes from AQS-ISO-001. Required continuous electrolyte path for ≤ 1 % protection current: 3.44 m (`_shunt_current.py`). Every inter-cell liquor line keeps the free-fall air break; where the route is shorter than the required path the break is the only protection.

| Line | From | To | Route m | ≥ 3.44 m continuous path | Break |
| --- | --- | --- | --- | --- | --- |
| IA-EW-01 | EW_1 | EW_2 | 8.6 | yes | air-break launder (kept; path alone would also do) |
| IA-EW-02 | EW_2 | EW_3 | 9.8 | yes | air-break launder (kept; path alone would also do) |
| IA-EW-03 | EW_3 | EW_4 | 7.8 | yes | air-break launder (kept; path alone would also do) |
| IA-EW-04 | LEACH_CSTR_1 | EW_1 | 9.2 | yes | air-break launder (kept; path alone would also do) |
| IA-EW-05 | EW_5 | EW_6 | 6.6 | yes | air-break launder (kept; path alone would also do) |
| IA-EW-06 | EW_6 | EW_7 | 12.8 | yes | air-break launder (kept; path alone would also do) |
| IA-EW-07 | EW_7 | EW_8 | 13.8 | yes | air-break launder (kept; path alone would also do) |
| IA-EW-08 | EW_8 | EW_9 | 11.1 | yes | air-break launder (kept; path alone would also do) |
| IA-EW-10 | EW_4 | EW_5 | 10.0 | yes | air-break launder (kept; path alone would also do) |

## 12. Service-class selection guide across the assay envelope, Rev L

X-MAT-01. Done when: material per service class across the AQS-ASSAY-001 Rev C bounding cases, with source data.

Method. Every present edge that is not a cable (the wetted census, 422 edges) is classed into exactly one family below by the rules in `docs-authority/_line_list.py` (AQS-PIP-004). `docs-authority/_service_census.py` regenerates the census table and exits nonzero if a wetted line still carries the retired "aqueous process, default thermoplastic" catchall or if a class letter contradicts its family. Status at this revision: 323 piped wetted lines, 22 declared families, 0 default catchalls (2026-10-21, current graph, census run committed with this revision).

Bounding chemistry. The aqueous families are bounded by the feed envelope: phase classes per AQS-ASSAY-001 Rev C (section 1) and the leach/EW metal loading of ASSAY.md (Fe 20, Cu 8, Ni 3, Zn 4, Al 6, other 9 g/L). No family takes a vendor gauge figure. Every material statement below cites the reference set of this document ([S1] to [S12], plus [S21]/[S22] of section 9) or the registered PERRY9_MAT row (Perry's Chemical Engineers' Handbook, 9th ed., 2019, sec. 25, materials of construction, in `flow_graph/param/refs.py`). Per-unit shell materials remain governed by the unit duty sheets (section 3 of each) and, where stated, the issued graph `params.design.material`.

### 12.1 Classed families (AQS-PIP-003 Rev A class letters)

Census counts come from `_service_census.py` (regenerated with this revision). T note is the range of known edge Temperatures in the family; unstamped edges take the 40 °C ambient basis (A-M-269).

| Service family | Class | Lines | T °C (known) | Wetted material and basis | Sources |
| --- | --- | --- | --- | --- | --- |
| Hot leach liquor | P2 | 46 | 40–85 | CPVC Sch 80 (M5 limit 93 °C, operated ≤ 88 °C); the hot LEACH/CSTR draws and every P2 unit connection of section 2 | [S3], [S5] |
| Acid or brine, at or below 60 °C | P1 | 54 | 10–50.6 | PVC-U Sch 80 P1; leach/EW metal-salt liquors in the ASSAY.md envelope; inter-cell EW links are free-fall launders (section 11) | [S10] |
| Aqueous process liquor (AQS-ASSAY-001 envelope) | P1 | 13 | ambient | PVC-U Sch 80 P1; the non-keyword aqueous fallback family: every wetted line still lands in a named family, none in a catchall | [S10] |
| Oxidizer, wet HF or PVDF unit | P3 | 13 | 25–85 | PVDF (P3); nitric and peroxide make-ups (section 5) and wet-HF product and make-up legs, including IA-HF-PROD (85 °C) into WS_HF_ED | [S1], [S11], [S12] |
| Process vent gas | P3 | 31 | ambient | PVDF (P3) | [S1] |
| Flue or acid gas | F1 | 10 | ambient | FRP/composite F1 per section 4.3 | section 4.3 |
| Alkaline (NaOH/KOH base liquor) | P4 | 6 | 50.6 | PP-H to 80 °C (P4); BMED base product and caustic make-ups | [S4] |
| Alkaline silica slurry | P4 | 3 | ambient | PP-H (P4); colloidal silica carrier to the wafer fab; the WS_SLURRY vessel itself stays 316L per its duty sheet | [S4] |
| Water loops (protective, irrigation, UPW) | P5 | 13 | ambient | HDPE per PIP-003 P5 | section 2 audit |
| Flue quench water | P5 | 1 | ambient | HDPE P5 | section 2 audit |
| Propylene-glycol ground loop | P5 | 1 | ambient | HDPE DR-11 buried, 25 % PG freeze protection (node design, S43) | section 2 audit |
| Q3/Q4 water loop | M1 | 20 | ambient | 316L loops | section 4.4 basis |
| Dry gas, H₂/O₂/N₂/CO₂ | M1 | 47 | 20–30 | 316L with M6 dielectric breaks; AQS-REV-H2-001 holds the H₂ wetted basis | section 6 |
| Wet methanol service | M1 | 11 | ambient | 316L: MEOH_TANK duty ("316L if the stream is wet"), MEOH_SYNTH shell 316L (API 941, 50 bar a, 250 °C synthesis study); covers crude MeOH, MeOH fuel, dock shipment and the VDF/TFE carbon-source lines | AQS-REV-H2-001 |
| Organic liquid (solvent make-up) | M1 | 1 | ambient | 316L where wet per the WS_SOLV duty | duty sheets |
| Q1/Q2 thermal oil | M2 | 12 | hold | Carbon steel A106 Gr B per section 4.4 | [S8] |
| Hydrocarbon product, fuel or wax cut | M2 | 19 | ambient | Carbon steel, dry hydrocarbon service per the issued duties (OIL_FRAC and OIL_PYRO: "Carbon steel. Hydrocarbon. No aqueous chloride", CA 1.5 mm); covers the fractionator cuts, C29 recycle, wax reclaim and the C5–C10 generator fuel | duty sheets |
| 98 wt% H₂SO₄ make-up | M2 | 1 | ambient | Carbon steel: iron passivates above ≈ 93 wt% at ambient (PERRY9_MAT); velocity and temperature guards are unit-task-09 detail | PERRY9_MAT |

### 12.2 Families without a PIP-003 class ("—")

These families are governed by issued per-unit materials and are pending a PIP-003 Rev B class sheet (X-PIP-01 Rev B rows). Their AQS-PIP-004 rows carry class "—" with the family text, so no line is silently classed PVC where its chemistry forbids it.

| Family | Lines | Issued wetted materials | Class status |
| --- | --- | --- | --- |
| Molten metal launder/pour (S57, IND_MELT and VAC_IND melt pours) | 7 | Not piped: launder/pour hot faces (M7); ISO route rows retained for geometry only | not piped |
| Fluoro synthesis train (HF_GEN, VDF_SYN, TFE_SYN, POLY_F, F_RECOVER and their dry monomer/Cl₂ legs) | 9 | HF_GEN carbon steel shell, dry HF (PERRY9_MAT), Monel trunnions; VDF_SYN Hastelloy C-276 reactors, Ni cracking tube, PTFE-lined coolers; TFE_SYN Inconel 600 pyrolysis tube, Hastelloy C-276 coolers; POLY_F Hastelloy C-276 wetted, PTFE gasketed. The wet-HF and H₂SO₄ make-up legs into these units are classed separately (P3 and M2 above) | PIP-003 Rev B |
| Dopant concentrates (S36, BBr₃/POCl₃ class) | 1 | PTFE/PFA handling per the semiconductor-reagent practice; flow 0.0 kg/d (nominally closed), no pipe class | PIP-003 Rev B |
| CaCl₂/MgCl₂ brine concentrates to molten-salt pots | 3 | Unit task 09 wetted-material selection pending (MG_POT, CA_POT and F_RECOVER duty section 3, across the AQS-ASSAY-001 Rev C bounding cases); closes with the pot-cell material selection (X-MAT-06) | PIP-003 Rev B or unit-specific |

### 12.3 Dispositions of the section 2 ambiguous list

The 2026-10-15 audit items below were ambiguous then and are resolved by the sections shown. Not closed here: the molten-salt pot-cell wetted selection (12.2 last row) and the WS_SLURRY/WS_DOPE per-stream gasket detail (X-MAT-03).

| Section 2 item | Disposition |
| --- | --- |
| HX8 (Ti in reducing chloride) | Sections 4.1 and 4.5: PVDF bundle, not Ti |
| ZNBR2_BR2_REGEN (wet Br₂) | Section 3.1: PVC-U shell and sump with the headspace class ruling |
| GLASS_DIGEST (liquor not characterized) | Duty sheet names chloride/scrub liquor; IA-DIG-LIQ and IA-DIG-BLK class P1/P2 aqueous families above |
| WS_NITRIC, WS_PEROX (oxidizer limits) | Section 5 (Rev D) and the M1 PVDF rules of section 2 |
| WS_SOLV, WS_DOPE, WS_SLURRY (compatibility not stated) | Duties name 316L where wet; lines class P1/P4/"—" families above; gasket detail stays X-MAT-03 |
| ETOH_STILL, BUOH_STILL | Section 4.2 |
| VCD_TRAIN, FAB_UPW_TANK, HDR_UPW, BMED_UPW_POLISH | Section 10 bullet (Ti Gr 2 / PVDF on the 85 °C draw) and the P5/M1 water families |
| HDR_H2, RELIEF_H2, H2_DRYER | Section 6 (M6, AQS-REV-H2-001); HDR_H2 dielectric breaks in section 11 |
| HDR_O2 | M7 dry oxygen row of section 2 (M1 class family above) |
| FLUE_KO, BAGHOUSE, AFTERBURNER_FLUE | Section 4.3 (F1) |
| Q1_A to Q4_B, GEO_*, and the water-loop list | Sections 4.4 (Q1/Q2) and the M1/P5 water families above |
| MEOH_SYNTH, MEOH_TANK, MEOH_COND | Wet methanol family above; AQS-REV-H2-001 carries the synthesis wetted basis |
| OIL sector (reducing, hot) | M7 hot faces on the pyrolysis units; M2 hydrocarbon family above for the cut, recycle and fuel lines |
| MFG units with "316L where wet" | Duties name the wet streams per unit; classed into the families above; the pot-cell units sit in 12.2 |
| EW_1 to EW_9 (dissolution and stray current) | Sections 9 and 11 (X-MAT-18/X-MAT-07) |

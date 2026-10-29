# Hydrogen embrittlement review

Document number: AQS-REV-H2-001
Revision: C
Date: 2026-10-29
Authority: plant graph Rev AC; materials to AQS-STD-002 (`MATERIALS_STD.md`). Study. Not a PE stamp.

| Rev | Description | Date |
| --- | --- | --- |
| C | Rewritten against graph Rev AC: the electrolyser and the hydrogen compressor added; the electrowinning cathodes changed to titanium as AQS-STD-002 section 9 decided; the hydrogen store described as a compressed-gas tube bank; the statement that the hydrogen edges carry pressure, temperature and purity withdrawn, because they do not | 2026-10-29 |
| B | Hydrogen edge conditions (X-MAT-15) and the API 941 check of `MEOH_SYNTH` (X-MAT-14) | 2026-10-15 |
| A | First issue: every unit wetted by hydrogen, with its conditions from the graph, its material and the fixes | 2026-10-15 |

## 1. Purpose and scope

This review checks every unit of the plant that hydrogen wets for hydrogen embrittlement, and for high-temperature hydrogen attack (HTHA) where the temperature is high enough. It takes the units and streams from the plant graph and the materials from AQS-STD-002, and it states the material, the conditions and the precautions for each unit. Hydrogen fire, ignition and relief are outside its scope; they are covered in AQS-SAF-005 (`FIRE_PROTECTION.md`) and the relief register.

Hydrogen embrittlement is the loss of ductility and toughness of a metal that has absorbed hydrogen. HTHA is the attack of carbon and low-alloy steels by hydrogen at high temperature and pressure, in which the hydrogen reacts with the carbon in the steel to form methane.

## 2. Basis

The review applies four sources.

1. ASME B31.12 [1] governs hydrogen piping. It requires the material to be qualified, adds performance factors or a fracture-mechanics qualification for carbon steels, and treats austenitic stainless steel as the class at low risk.
2. The Sandia technical reference for 316 and 316L stainless steel [2] finds little loss of ductility at room temperature in gaseous hydrogen. The susceptibility rises with sensitization, low nickel content, cold work (which forms strain-induced martensite) and temperatures below ambient. Sound welds behave like the base metal.
3. The CSA CHMC1 screening route [3] accepts 316 and 316L stainless steel and 6061 aluminium for dry hydrogen. It does not establish compatibility with external environments such as warm humid air.
4. API RP 941 [4] sets the limits for HTHA. It applies above 204 °C (400 °F) at a hydrogen partial pressure above 345 kPa (50 psia).

ISO 11114-1 and CGA G-5.6 give further compatibility principles. They are named here but were not consulted in full text.

The hydrogen streams on the graph carry rates but not pressure, temperature or purity. The conditions in Table 3.1 are therefore the registered study assumptions A-M-021 to A-M-024 of AQS-REG-002 (`ASSUMPTIONS_REGISTER.md`), together with the design pressure of the hydrogen store and its compressor, which the graph does carry (`CRYO_H2.params`).

## 3. Conditions

Table 3.1. Hydrogen service conditions

| Segment | Streams | Pressure | Temperature | Purity | Source |
| --- | --- | --- | --- | --- | --- |
| Cell offgas and header, wet | The cathode hydrogen streams into `HDR_H2`, and `IA-HDR-H2-02` to `H2_DRYER` | 105 kPa abs | 40 °C | 98 mol%, saturated with water | A-M-021 |
| Dryer outlet and electrolyser product to the compressor | `S64`, `S24`, `IA-ELY-H2` | 1.0 MPa abs | 30 °C | 99.9 mol%, dew point −40 °C | A-M-022 |
| Compressed store | Inside `CRYO_H2` | 22 MPa design; the compressor delivers 20 MPa | Ambient; the compressor limits each stage to 135 °C | 99.9 mol% | `CRYO_H2.params.design`, `compressor_design` |
| Store to the fuel cell and the generator | `S49`, `S45` | 150 kPa abs | 25 °C | 99.97 mol% (ISO 14687 Grade D [5]) | A-M-023 |
| Store to methanol synthesis | `S74` | 5.0 MPa abs at the reactor | 250 °C in the reactor | 99.9 mol% | A-M-024 |

Assumption A-M-022 states that the compressor ahead of the store is not on the graph. The graph now carries it as the five-stage diaphragm compressor of `CRYO_H2`, so A-M-022 needs updating; this is listed in section 6.

## 4. Units

Table 4.1. Units wetted by hydrogen

| Unit | Service | Material | Precautions |
| --- | --- | --- | --- |
| Electrowinning cells that make hydrogen | Hydrogen evolved as a side reaction at the cathode in acid chloride liquor; it leaves with sweep air to `HDR_H2` | Cathode blank of titanium Grade 2, with a mixed metal oxide anode on titanium mesh (AQS-STD-002 section 9) | Titanium absorbs hydrogen at a cathode and can form brittle hydride, mostly above about 80 °C and at high current density. Each blank is bend-tested for hydride at each strip cycle in the first year. Reverse current is never applied to titanium, so the rectifier blocks reverse current and the cells shut down in a controlled sequence. |
| `HDR_H2` | Wet hydrogen with sweep air from the cell hoods, which can carry hydrochloric acid and chlorine mist, near atmospheric pressure | Unplasticized polyvinyl chloride (PVC-U) | The plastic does not embrittle, and permeation is negligible near atmospheric pressure. Ignition is the governing hazard instead. Every metal part is bonded, and the line has no isolated conductor. |
| `H2O_ELYZ` | Proton exchange membrane (PEM) water electrolyser; hydrogen leaves the cathode side wet and is dried in the unit | Titanium porous transport layers and cell hardware, deoxidizer on 316L hardware, dry product lines in 316L (`H2O_ELYZ.params.sec3_material`) | The stack metals are electrodes under rule M6 and are the maker's responsibility. The product line is dry hydrogen on 316L, the CHMC1 screening case [3]. |
| `H2_DRYER` | Wet hydrogen in, dry hydrogen out to the store and to `RELIEF_H2` | Inlet knock-out in PVC-U; vessel and outlet in annealed 316L | Dry hydrogen on 316L is the CHMC1 screening case [3]. The steel is a low-carbon grade and is not held between 500 °C and 800 °C after welding, to avoid sensitization [2]. The regeneration temperature and pressure are not yet set. |
| `RELIEF_H2` | Hydrogen relief from `H2_DRYER` to a vent stack | Annealed 316L, grounded | The stack is open, with no cap that can trap hydrogen, and it is bonded and grounded. |
| `CRYO_H2` | Compressor and tube bank storing dry hydrogen at up to 22 MPa design pressure | Annealed 316L with nickel near the top of the grade range, for the tubes, the compressor wetted parts and the fittings | This is the most severe embrittlement case in the plant, because the pressure is high and the tubes cycle on every fill. Nickel near the top of the range limits the strain-induced martensite that raises susceptibility [2]. No ferritic, martensitic or high-strength steel is used, including fasteners in contact with hydrogen. The fatigue life of the tubes under fill cycling must be qualified to ASME B31.12 [1] or the pressure vessel code. |
| `MEOH_SYNTH` | Hydrogen (`S74`) with carbon dioxide to methanol at 250 °C and 5.0 MPa abs | 316L | The hydrogen partial pressure is 3.75 MPa abs (544 psia) at a hydrogen to carbon dioxide ratio of 3 to 1, the low end of the range for the copper and zinc oxide catalyst [6]. Both the temperature and the partial pressure exceed the API 941 thresholds [4], so HTHA applies. API 941 states that austenitic stainless steels are not susceptible to HTHA at any listed condition, so 316L is used and carbon steel and carbon–0.5 molybdenum steel are excluded. |
| `FUEL_CELL` | Dry hydrogen (`S49`) and oxygen to a PEM stack | Feed tubing in annealed 316L; stack internals by the maker | The stack plates are electrodes under rule M6. A dielectric break separates the stack from the plant piping. |
| `BACKUP_GEN` | Dry hydrogen fuel (`S45`) | Fuel line in annealed 316L; engine internals by the maker | None beyond the general rules. |
| `LEACH_CSTR_1`, `ZNBR2` | Traces of hydrogen from side reactions in polymer equipment | As AQS-STD-002 | Polymer does not embrittle. The vapour space vents to `HDR_H2` or to the stack. |

## 5. General rules

1. Carbon steel, low-alloy steel, high-strength steel and martensitic stainless steel are not used in any hydrogen service.
2. Annealed 316L austenitic stainless steel is the default metal. It is used in dry hydrogen under rule M6, and in wet hydrogen only where the part is an electrode.
3. Dry hydrogen at low pressure may be carried in high-density polyethylene (HDPE) or polyamide (PA) downstream of the dryer, below the rated pressure of the polymer and outside any fire zone. Copper tubing is acceptable for dry instrument lines at low pressure. Neither material is used where there is acid mist.
4. Welds are qualified and inspected to ASME B31.12 [1]. Threaded joints are not used in hydrogen above atmospheric pressure.
5. Every hydrogen line that enters an electrochemical area has a dielectric break (rule M6).

## 6. Open items

1. Pressure, temperature and purity are to be written on every hydrogen edge of the graph (X-MAT-09), so that this review can read them instead of the assumptions.
2. Assumption A-M-022 is to be updated for the compressor that the graph now carries in `CRYO_H2`.
3. The graph sends cathode hydrogen to `HDR_H2` from EW_1 to EW_3 and EW_5 to EW_9, while AQS-STD-002 section 9 names EW_1, EW_2, EW_4 and EW_9 as the cells that make hydrogen. The hydride inspection must cover the cells the graph names until the two agree.
4. The dilution of the sweep air in `HDR_H2`, the regeneration conditions of `H2_DRYER` and a purifier, if the dryer output is below Grade D, remain to be set.
5. The life of each cathode blank is to be recorded.

## References

1. ASME B31.12, Hydrogen Piping and Pipelines. https://www.asme.org/codes-standards/find-codes-standards/b31-12-hydrogen-piping-pipelines
2. Sandia National Laboratories, Technical Reference on Hydrogen Compatibility of Materials: 316/316L. https://www.sandia.gov/app/uploads/sites/158/2021/12/2103TechRef_316SS.pdf
3. Sandia National Laboratories, Materials Qualification for Hydrogen Service using CSA CHMC1. https://www.osti.gov/servlets/purl/1673694
4. API RP 941, Steels for Hydrogen Service at Elevated Temperatures and Pressures in Petroleum Refineries and Petrochemical Plants, 8th ed., 2016.
5. ISO 14687:2025, Hydrogen fuel quality — Product specification.
6. Bertau M. et al. (eds.), Methanol: The Basic Chemical and Energy Feedstock of the Future, Springer, 2014.

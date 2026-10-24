# Sign and label schedule

Document number: AQS-SIGN-001  
Revision: A  
Date: 2026-09-26  
Measurement: metric

| Rev | Change | Description | Date |
|---|---|---|---|
| — | — | Basic issue | 2026-09-26 |
| A | — | Four-line face (signal, unit, hazard, instruction). Leaders. ±Y facing. | 2026-09-26 |

This schedule is the authority for legend text. `labels.py` `SIGN_LEGEND`
must match the Face column below. If the plate is blank, install
`fonts-liberation` and rebuild; do not invent a second legend.

WARNING, CAUTION, and NOTE follow KSC-DF-107 Rev F §3.20. The plate
geometry follows ANSI Z535 practice (signal word + short body) because
DF-107 does not specify factory sign size. The paragraph under each
sign is the document statement. The four Face lines are what get cut
into the 500 mm × 400 mm plate.

## 1. Plate layout

Four lines, top to bottom, Liberation Sans Bold (OFL-1.1):

1. Signal word — `WARNING` or `CAUTION` (size 32 mm)
2. Locked unit name (0.85 × 32 mm)
3. Hazard short title (0.65 × 32 mm)
4. Instruction (0.65 × 32 mm)

Facing (`labels.py`):

- `face="-Y"` — readable from the −Y approach (south of CSTR, south of split)
- `face="+Y"` — readable from the +Y side (north of CSTR, EW aisle looking at plates that sit south of the path)

A leader `SIGN_*_ARROW` runs from plate mid-face to the named unit when
`sign(..., to=)` is set.

Labels (`LBL_*`) stay one line at Z = 1600 mm.

## 2. Equipment labels

| Object | Face text |
|---|---|
| LBL_LEACH_CSTR_1 | LEACH CSTR 1 |
| LBL_HOPPER_SHREDDER | HOPPER / SHREDDER |
| LBL_FLOAT_DEWATER | FLOAT DEWATER |
| LBL_VIBRATORY_SPLIT | VIBRATORY SPLIT |
| LBL_EW_1_Au … LBL_EW_9_Zn | EW-n + metal |
| LBL_P_Al, LBL_P_Mg, LBL_P_Ca | P_Al / P_Mg / P_Ca |
| LBL_PK_1 … LBL_PK_9 | PK_n |
| LBL_BMED_REGEN | BMED REGEN |
| LBL_NaOH_PRODUCT | NaOH PRODUCT |
| LBL_HCl_PRODUCT | HCl PRODUCT |
| LBL_CRU | CRU |
| LBL_PROD_METALS | METALS / ELEMENTS |
| LBL_DRYER | DRYER |
| LBL_INDUCTION_PYROLYZER | INDUCTION PYROLYZER |
| LBL_FRACTIONATOR | FRACTIONATOR |
| LBL_AFTERBURNER | AFTERBURNER |
| LBL_BURNOUT_ROTARY | BURNOUT ROTARY |
| LBL_NaOH_DIGEST | NaOH DIGEST |
| LBL_RECTIFIER | RECTIFIER |
| LBL_SOL_ARK_60K | SOL-ARK 60K |
| LBL_ZNBR2 | ZnBr2 |

## 3. Safety signs

### SIGN_OXIDIZER_LEACH

Face: WARNING / LEACH CSTR 1 / OXIDIZER / SALRIA HCl + NaClO3  
Facing: −Y. Leader to CSTR body.

**WARNING**

Salria (HCl + NaClO3) is a strong oxidizer. Contact with organics or
metals other than the approved wetted list can cause fire or release
of chlorine. Wear face shield, gloves, and apron. No bare titanium,
316L, PP, or HDPE on this vessel.

### SIGN_ACID_GAS_LEACH

Face: WARNING / LEACH CSTR 1 / ACID GAS / DO NOT OPEN LID  
Facing: −Y. Leader to CSTR body.

**WARNING**

Acid-gas takeoff is live when the lid is closed. Do not open the lid
while ORP is above the standby setpoint. Atmosphere is not breathable.

### SIGN_H2_EW_AISLE

Face: WARNING / EW AISLE / HYDROGEN / NO IGNITION SOURCES  
Facing: +Y. Leader to EW-5.

**WARNING**

Hydrogen evolves at the cathodes. No ignition sources in this aisle.
Keep HDR_H2 isolated from HDR_OIL_VAPOR and HDR_ACID_GAS.

### SIGN_H2_DRYER

Face: WARNING / DRYER / HYDROGEN / NO HOT WORK  
Facing: −Y default unless the caller sets +Y. Leader to H2_DRYER.

**WARNING**

Hydrogen dryer and stack. No hot work within 3 m without a gas test.

### SIGN_SPLASH_HARVEST

Face: CAUTION / EW HARVEST / ACID SPLASH / PAIL IN BUND ONLY  
Facing: +Y. Leader to EW-9 funnel.

**CAUTION**

Funnel valves discharge acid liquor with metal powder. Open into a
pail inside the bund. Spills return to LEACH CSTR 1. Do not wash to
a drain.

### SIGN_CAUSTIC_BMED

Face: WARNING / NaOH PRODUCT / CAUSTIC / PP VESSEL ONLY  
Facing: +Y. Leader to NaOH PRODUCT tote.

**WARNING**

NaOH product is concentrated hydroxide from BMED BASE. Burns skin and
eyes. PP vessels only on this tote.

### SIGN_CAUSTIC_DIGEST

Face: WARNING / NaOH DIGEST / CAUSTIC / 80 C TO 90 C  
Leader to NaOH_DIGEST.

**WARNING**

NaOH digest, 80 °C to 90 °C. Caustic splash and steam. PP or Ni vessel
only.

### SIGN_RAD_PK9

Face: WARNING / PK-9 / RADIOACTIVE / SEALED LID ONLY  
Facing: +Y. Leader to PK-9. Authoritative placement is `labels.wet_signs`,
not `wet_products.build`.

**WARNING**

PK-9 handles residual radionuclides. Lid stays sealed. Dedicated
acid-gas hose only. No open pail harvest.

### SIGN_HOT_PYRO

Face: CAUTION / INDUCTION PYROLYZER / HOT SURFACE / 400 C TO 600 C  
Leader to pyro shell.

**CAUTION**

Induction pyrolyzer shell 400 °C to 600 °C. Coils are live. Charge
must be dry. FR-4 is forbidden in this pipe.

### SIGN_NCG_AFTERBURNER

Face: WARNING / AFTERBURNER / NCG / TAR / FLUE TO ROTARY ONLY  
Leader to AFTERBURNER.

**WARNING**

Afterburner destroys NCG and tars. Flue jackets BURNOUT ROTARY only.
Oil vapor does not enter the rotary atmosphere.

### SIGN_OIL_VAPOR

Face: WARNING / OIL LINE / OIL VAPOR / KEEP HEADERS APART  
Leader to quench / fractionator.

**WARNING**

Oil-vapor header. Keep isolated from acid gas and hydrogen.

### SIGN_HOT_ROTARY

Face: CAUTION / BURNOUT ROTARY / HOT SURFACE / 450 C TO 550 C  
Leader to rotary.

**CAUTION**

Burnout rotary 450 °C to 550 °C. Indirect flue jacket. Do not feed
this tube from the oil pyro.

### SIGN_ARC_FLASH_RECTIFIER

Face: WARNING / RECTIFIER / ARC FLASH / DC BUS LIVE  
Leader to RECTIFIER.

**WARNING**

DC bus and rectifier. Arc-flash hazard. De-energize before opening.

### SIGN_BR2_BATTERY

Face: WARNING / ZnBr2 / BROMINE / BATTERY SCRUBBER ONLY  
Leader to ZNBR2 stack.

**WARNING**

ZnBr2 stack can evolve Br2. Use the battery scrubber only. Do not
tie this header to CRU or process Cl2.

---

Building stack placements follow AQS-BLD-001 / `docs-authority/AUTHORITY.md`.
Sign faces and locked names are unchanged by the vertical re-origin.

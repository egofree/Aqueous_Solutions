# Literature compositions for missing assays

Document number: AQS-LIT-ASSAY  
Revision: A  
Date: 2026-10-16  
Authority: literature search 2026-10-16. Not a plant measurement. Not a PE stamp.  
These values may be entered on the assumptions list only with the citation. They do not close the missing-measurement lines in notes/ASSAY_TI_MO.md.

## 1. Dense grit — ilmenite / rutile (FLOAT_SINK feed to TI_CELL)

Commercial ilmenite concentrates (typical ranges):

| Source | TiO₂ wt% | Fe (as oxide) | SiO₂ | Al₂O₃ | Other |
|--------|----------|---------------|------|-------|-------|
| KMML typical | 59.9 | Fe₂O₃ 27.0 + FeO 8.4 | 0.83 | 1.16 | V₂O₅ 0.2, MgO 0.79 |
| Ukrainian (Volnogorsk / Irshansk) | 54–63 min | Fe₂O₃ 13–25, FeO 9–20 | ≤2–3 | ≤1–3 | Cr₂O₃ ≤0.5 |
| Stoichiometric FeTiO₃ | 52.7 | Fe₂O₃ eq. 47.3 | — | — | — |
| Commercial rutile | 92–96 | Fe₂O₃ ~0.5–3.4 | 0.6–1.2 | 0.4–0.7 | — |

Ideal FeTiO₃ is 31.6 % Ti by mass. Commercial ilmenite concentrates run 45–63 % TiO₂ (roughly 27–38 % Ti). Rutile concentrates run >92 % TiO₂.

Cited: KMML product sheet; Ukrainian TU specifications (Volnogorsk, Irshansk); DERA Rohstoffinformationen 47 (ilmenite/rutile differentiation).

**Use:** If a referenced assumption is required before a plant assay, take 55 % TiO₂ and 30 % Fe (as Fe₂O₃ + FeO) for an ilmenite-type dense grit, or 94 % TiO₂ and <2 % Fe for a rutile-type grit. State which.

## 2. Chromite grit (CR_CELL alternate feed)

Ideal FeCr₂O₄: 46.5 % Cr, 25.0 % Fe, 28.6 % O.  
Commercial chromite sand / ore: 46 % Cr₂O₃ minimum (metallurgical grade often ≥46–48 % Cr₂O₃), FeO ~26–30 %, Al₂O₃ 13–15 %, MgO 10–12 %, SiO₂ ≤1–7 %.

Cited: Mindat / Webmineral chromite data; Westbrook Resources chromite sand specification; MDPI Minerals 2023 (chromite ore characterization).

**Use:** 46 % Cr₂O₃ (~31 % Cr) and ~25 % Fe as a referenced assumption for chromite grit.

## 3. Post-EW liquor — Mo, Zn, Fe, Ni (EW_9 feed to MO_CELL)

No commercial zinc-electrowinning raffinate assay that reports a useful molybdenum tenor was found. Molybdenum appears in the literature mainly as:

- a trace impurity whose effect on zinc current efficiency is discussed at <1 mg/L levels, or
- a target metal in dedicated Mo recovery circuits (leach liquors of 1–1000 mg/L Mo, not zinc EW raffinate).

Residual metals in zinc EW electrolytes (general literature):

- Fe: kept below ~10–50 mg/L; above this, current efficiency drops.
- Ni: harmful at <1 mg/L; plants purify to well below 1 mg/L.
- Zn: cell electrolyte typically 40–70 g/L; spent/raffinate lower but still tens of g/L.

Cited: 911Metallurgist zinc EW impurity reviews; various zinc EW operating papers (Fe and Ni limits).

**Use:** No defensible Mo tenor can be taken from the literature for this edge. Fe and Ni residuals can be noted as “<50 mg/L Fe, <1 mg/L Ni” only as purification targets, not as measured raffinate values. The Mo measurement remains missing.

## Status

- Ilmenite/rutile and chromite literature ranges are adequate for a referenced assumption on the assumptions list.
- The EW_9 molybdenum assay has no usable literature substitute. It stays named missing.
- None of the above is a plant measurement. notes/ASSAY_TI_MO.md is unchanged.

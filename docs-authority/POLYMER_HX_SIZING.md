# Polymer exchanger sizing, HX-5 and HX8

Document number: AQS-DUTY-049
Revision: A
Date: 2026-10-15
Authority: graph Rev BH. Study. Not a PE stamp. Script `docs-authority/_polymer_hx_study.py`. Materials per AQS-STD-002. No rate change.

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue. HX-5 (X-MAT-11) and HX8 (X-MAT-12). | 2026-10-15 |

## 1. Basis

- Duties and temperatures from the graph: HL-Q3-A-HX5 rated 7.941 kW, Q3 95 → 85 °C, 0.18863 kg/s; LEACH_CSTR_1 liquor_T_C 77.5 °C; HX8 4.572 kW, liquor 55 → 51 °C at 1112.1 kg/h, Q4 water 45 → 49 °C.
- PVDF conductivity 0.17 W/mK, the low end of the Kynar 740 data sheet (0.17–0.19, ASTM D433) [S16]. Borosilicate 3.3 1.2 W/mK (ISO 3585 typical). Graphite 100 W/mK (assumption, order of magnitude only).
- Film coefficients: tube side Dittus–Boelter with water properties from steam tables. The liquor is taken as water; that is an assumption. Outside films are assumptions: leach liquor 300 W/m²K by natural convection or 1000 W/m²K agitated (the agitator is held); HX8 shell 1500 W/m²K.
- Fouling 0.0002 m²K/W (assumption).
- Tubes: HX-5 PVDF 25 × 1.9 mm. HX8 PVDF 16 × 1.5 mm, 3 tubes per pass, 0.79 m/s, Re 20 010. Both are assumptions.

## 2. Results

| Case | LMTD K | U W/m²K | Area m² | Tube length m |
| --- | --- | --- | --- | --- |
| HX-5 PVDF coil, natural convection | 11.80 | 66.9 | 10.06 | 128 |
| HX-5 PVDF coil, agitated | 11.80 | 79.3 | 8.49 | 108 |
| HX-5 borosilicate 3.3 coil, natural convection | 11.80 | 159.5 | 4.22 | 54 |
| HX-5 borosilicate 3.3 coil, agitated | 11.80 | 254.0 | 2.65 | 34 |
| HX8 PVDF tube bundle | 6.00 | 101.1 | 7.53 | — |
| HX8 impregnated graphite | 6.00 | 898.0 | 0.85 | — |

The PVDF wall is the controlling resistance in every PVDF case: 0.011 m²K/W against 0.0002 to 0.0033 for the films.

## 3. Findings

1. HX-5. A PVDF coil needs 8.5 to 10.1 m², about 110 to 130 m of 25 mm tube, inside a 2.0 × 1.08 m tank. A borosilicate glass 3.3 coil needs 2.7 to 4.2 m². Glass is inert to HCl and chlorate at 95 °C (AQS-STD-002 section 3.2 fallback). Recommendation: borosilicate glass coil. The change of choice from PVDF is for the owner to confirm.
2. HX8. The PVDF tube bundle needs 7.5 m², fifteen times the 0.51 m² plate area on the graph. Graphite needs 0.85 m², but it is a conductor in the EW aisle (M6, stray current). Recommendation: keep PVDF at 7.5 m², or confirm graphite with dielectric isolation of the whole exchanger.
3. The graph exchanger areas are recorded as params (`hx5_area_m2`, `area_m2_pvdf`). The duties are unchanged.

## References

- [S16] Arkema, Kynar 740 technical data sheet, thermal conductivity 0.17–0.19 W/mK, https://hpp.arkema.com/assets/arkema/TDS_KYNAR%C2%AE%20740_en_WW.pdf

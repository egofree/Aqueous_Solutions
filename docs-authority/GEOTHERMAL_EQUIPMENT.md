# Geothermal equipment list

Document number: AQS-EQP-GEO-001  
Revision: D  
Date: 2026-10-24  
Process flow diagram: AQS-PFD-GEO-001 (`geothermal_pfd.png`)  
Basis: AQS-PWR-002 (`GEOTHERMAL_BACKUP.md`); `POWER/Power_System_overview.md`; AQS-SCALE-001; `ELECTRICAL.md` (AQS-ELC-001, HVAC and Q4); AQS-STR-001 streams S43, S44 and S48.  
Licence: CERN-OHL-S-2.0.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Basic issue with POWER gap close | 2026-09-27 |
| C | 2 | Point to AQS-EQP-STUDY-001 Rev C Carnot-limited ORC band | 2026-10-01 |
| D | 1 | Rewritten to DOC_STYLE (AQS-DOC-002) for a reader new to the project: purpose, scope and terms, captions; the Q4 and organic Rankine cycle notes given section numbers. Tags, ratings and rules unchanged. | 2026-10-24 |

## 1. Purpose and scope

The plant uses a closed ground loop. A heat pump on that loop supplies the Q4 low-temperature water header; an organic Rankine cycle generator is held as a stub until a site survey shows whether there is surplus ground heat to convert. This page lists the geothermal units, their fluids, the mixes that are not allowed, the ratings, and the method for the generator rating.

Ratings that depend on the site survey stay to be determined. None is invented here.

## 2. Terms

- Ground heat exchanger (GHEX): a closed loop of pipe in vertical boreholes that exchanges heat with the ground.
- Organic Rankine cycle (ORC): a heat engine that uses an organic working fluid, suited to low-temperature heat.
- Q4: the lowest-temperature water header of the heat ladder, the only one that enters life-support air.
- Carnot limit: the highest efficiency any heat engine can reach between two temperatures.
- M1: the first module of the plant at the baseline size.

Stream numbers (S43 and so on) are those of AQS-STR-001. Other abbreviations are in `docs-authority/GLOSSARY.md`.

## 3. Unit tags

Table 3.1. Geothermal units

| Tag | Duty | Status |
|---|---|---|
| GEO_GHEX | Closed-loop vertical ground heat exchanger (bore field class) | Issued — site survey TBD |
| GEO_LOOP_PUMP | Circulation pump on S43 loop | Issued — rating TBD |
| GEO_HP | Water-source heat pump → Q4 (S44) | Issued — thermal path primary at M1 |
| GEO_ORC | Binary organic Rankine cycle electric stub | Stub — rating TBD |
| GEO_HDR | Yard stub header / keep-out to off-plate field | Massing |

## 4. Fluids and equipment class

Table 4.1. Fluids and equipment class

| Item | Spec intent |
|---|---|
| Loop fluid | Non-toxic inhibited water / glycol class; dedicated circuit |
| Bore field | Vertical closed-loop; count / depth TBD after conductivity test |
| Heat pump | Water-source; reject / absorb to Q4 only (< 80 °C into life air) |
| ORC working fluid | TBD (not Salria, not ZnBr2, not process Cl₂) |

## 5. Mixes not allowed

1. The S43 loop fluid shall not enter `HDR_UPW`, the catch tank, `ROOF_TANK` or the Salria circuit.
2. Condenser heat from `GEO_ORC` may join Q4 only through a named heat exchanger. Organic Rankine cycle fluid never enters a life-support header.
3. The geothermal boreholes are not a source of process make-up water.

## 6. Ratings

Table 6.1. Ratings

| Quantity | Value | Source |
|---|---|---|
| Legacy campus electric claim | 100 kW baseload | `POWER/Power_System_overview.md` (narrative) |
| M1 electric claim this pass | **TBD** — ORC stub only | AQS-PWR-002 §2.1 |
| Heat-pump thermal | **TBD** | Do not invent kW |
| HVAC AC load context | 1.5 kW class | `ELECTRICAL.md` |

## 7. Other users of the Q4 header

`FC_HX_Q4` (AQS-EQP-FC-001, S53) and `CRYO_HX_Q4` (AQS-EQP-CRY-001, S54) join the same Q4 water header as `GEO_HP` (S44) and S06. The deep heat reject of the cryogenic plant stays on S55 (`CRYO_DED_COOL`), not Q4. Generator exhaust (S46) never enters Q4 or the habitation air handler.

## 8. Method for the generator rating

The electrical rating of `GEO_ORC` remains to be determined; no nameplate is invented. The method is fixed (AQS-AUD-001 §10.4; AQS-EQP-STUDY-001 Rev C §5), study of 2026-10-01: only ground heat left over after Q4 life support can be converted, at a fraction of the Carnot limit (Figure 8.1).

Figure 8.1. Organic Rankine cycle power

```
P_ORC ≈ η_ORC × (Q_GHEX_available − Q4_life_priority)
η_ORC study class = 0.08–0.12 (binary ORC; fraction of Carnot)
```

Table 8.1. Study cases

| Study case | Q_surplus | P_ORC study |
|---|---|---|
| M1 shallow GHEX, Q4 life first | ~0 kW_th | **~0 kW_e** |
| Illustrative survey frees heat | 10–20 kW_th | **~1–2.4 kW_e** |

The method needs a site survey of the bore field and the source temperature. A fixed 100 kW on M1 is not allowed. In the plant graph, `GEO_ORC.continuous_kw` is null and carries `study_carnot_band`.

## 9. Rebuilding the drawing

Run from the repository root:

```bash
cd flow_graph/exporters/matplotlib
python3 geothermal_pfd.py
```

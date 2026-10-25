# Feed assay

Document number: AQS-ASSAY-001
Revision: F
Date: 2026-10-25
Authority: graph Rev BH. Not a PE stamp. Not a weighed sample.

| Rev | Description | Date |
| --- | --- | --- |
| B | Study fractions on IA-FEED-01, S08 and S16 | 2026-10-14 |
| C | Basis made independent of any one feedstock: class schema, bounding cases, and the list of bounded and held lines. IA-FEED-01 carries a class point and the envelope. S08 and S16 carry the entrained silicate fraction. | 2026-10-15 |
| D | Held rates recalculated at the bounding cases (X-BAS-02). No rate change. | 2026-10-15 |
| E | Acid system resized to the case A bound (X-RSZ-01); the acid line is no longer held (section 8). | 2026-10-15 |
| F | Rewritten to the documentation style guide (AQS-DOC-002); record of revisions put in order and revision E, previously recorded only in section 8, added to it. No value changed. | 2026-10-25 |

## Purpose and scope

The plant takes in mixed waste and raw materials and recovers metals, glass, polymers and other products from them. Its feed is not one material. It can be anything from a regolith-like silicate and oxide soil to a metal-rich printed circuit board (PCB), or any mixture of the two. An assay is a measurement of what a material contains.

This page defines the classes in which every feed lot is reported (section 1) and the bounding cases that span the range of possible feeds (section 2). It then checks whether the plant as currently sized, called the held design, can take every case. For each element or class it says whether the held design covers the case ("bounded") or whether the affected units would need resizing before such a feed is accepted ("held"). No rate is changed on this page and no unit is resized.

The values on this page were calculated on the dates in the record of revisions. The current rates are held in the plant flow graph and may have moved since; the graph governs.

## 1. Schema

Every feed lot is reported as mass fractions, as received, in the seven phase classes of Table 1.1. The fractions sum to 1.0. A lot that cannot be reported in this way has not been characterized and is not accepted as feed.

Table 1.1. Feed classes

| Class | What it holds | Where it goes in the plant |
| --- | --- | --- |
| `water` | Free moisture; water bound as hydrate is not included | OIL_DRYER, leach water balance |
| `metal_plateable` | Metallic or acid-soluble Fe, Cu, Ni, Zn, Sn, Pb, Cd, Co, Ag, Au | LEACH_CSTR_1, EW_1 to EW_9 |
| `metal_reactive` | Metallic Al, Mg, Ca, Ti, Li and rare earths | Precipitate cake; these metals are not recovered by electrowinning |
| `silicate_oxide` | SiO₂, silicate glass, ceramic, and oxide minerals, including oxide-bound Fe, Al, Ca, Mg, Ti | IA-SINK-01 to FLOAT_SINK, IA-CULLET to GLASS_RINSE, the glass line, BMED caustic |
| `organic` | Polymer, resin, paper, wood | OIL_DRYER, OIL_PYRO |
| `other_inorganic` | Sulfides, halides, phosphates and salts | Not included in the basis of the leach design |
| `unassigned` | The remainder | Recorded as a class but not identified |

Each lot also reports the mass fractions of these elements in the whole lot: Fe, Cu, Ni, Zn, Sn, Pb, Cd, Co, Ag, Au, Al and Si, and the fraction of the oxide-bound Fe and Al that can be leached. Si is reported as the element. SiO₂ is 0.4675 Si by mass (28.09 / 60.08).

## 2. Bounding cases

Table 2.1 lists the cases against which the held design is checked. None of them is the design feed. Waste electrical and electronic equipment (WEEE) and municipal solid waste (MSW) rows are taken from the published working averages in `ELECTRICAL.md`.

Table 2.1. Bounding cases

| Case | Source | Status |
| --- | --- | --- |
| A, silicate and oxide, regolith-like | Published Apollo soil ranges, Heiken, Vaniman and French, *Lunar Sourcebook*, 1991. SiO₂ about 0.40 to 0.48, Al₂O₃ 0.10 to 0.28, FeO 0.04 to 0.22, CaO 0.09 to 0.16, MgO 0.06 to 0.12, TiO₂ up to 0.08. Native Fe-Ni metal and troilite each taken as 0.005 | Literature range, not a sample. Class values are assumptions inside that range |
| B, metal-rich PCB | `ELECTRICAL.md`, PCB-rich WEEE row | Published working average, not a sample |
| Reference point | `ELECTRICAL.md`, mixed WEEE row. The held rates were built on it | Carried only because the held rates were built on it. It is not the feed |
| Intermediate | `ELECTRICAL.md` rows: MSW, landfill bulk, landfill WEEE cell, Cu tailings, Au tailings | Published working averages. Soil is booked to `silicate_oxide`. Tailings Fe is booked as published to `metal_plateable`; most of it is oxide |

Table 2.2 gives the class fractions of each case.

Table 2.2. Class fractions of the bounding cases

| Case | water | metal_plateable | metal_reactive | silicate_oxide | organic | other_inorganic | unassigned |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A, regolith-like | 0 | 0.005 | 0 | 0.99 | 0 | 0.005 | 0 |
| B, metal-rich PCB | 0.03 | 0.28095 | 0.04 | 0.30 | 0.25 | 0 | 0.09905 |
| Reference point | 0.05 | 0.35025 | 0.05 | 0.18 | 0.22 | 0 | 0.14975 |
| MSW | 0.25 | 0.044 | 0.015 | 0.05 | 0.30 | 0 | 0.341 |
| Landfill bulk | 0.20 | 0.028 | 0.008 | 0.53 | 0.12 | 0 | 0.114 |
| Landfill WEEE cell | 0.15 | 0.1951 | 0.03 | 0.35 | 0.18 | 0 | 0.0949 |
| Cu tailings | 0.15 | 0.0835 | 0.03 | 0.70 | 0 | 0 | 0.0365 |
| Au tailings | 0.18 | 0.0505 | 0.02 | 0.75 | 0 | 0 | 0 |

The published row for Au tailings sums to 1.0005, so its `unassigned` fraction is set to 0.

The envelope, from the minimum to the maximum over all cases, is: water 0 to 0.25, metal_plateable 0.005 to 0.35025, metal_reactive 0 to 0.05, silicate_oxide 0.05 to 0.99, organic 0 to 0.30, other_inorganic 0 to 0.005, unassigned 0 to 0.341.

## 3. IA-FEED-01

IA-FEED-01 carries the feed from HOPPER to LEACH_CSTR_1 at 102.68 kg/d. This page does not change that rate, and the earlier dock feed of 150 kg/d is not restored. The edge is labelled `plant feedstock, any class`. Its composition is the reference point, given in the seven classes. The edge parameter `params.assay_envelope` holds every case in section 2 and the envelope bounds.

## 4. Check across the range

The feed rate is held at 102.68 kg/d and every case is taken at that rate. Leach recovery is taken as 1.0, which is the upper bound on the metal that can reach a cell.

Table 4.1 lists the elements that the held design covers in every case. For each one it gives the largest fraction found in any case, the resulting mass flow, the electrowinning cell that recovers it, and the rate of that cell's sheet edge.

### Bounded by the held design

Table 4.1. Elements bounded by the held design

| Element | Largest fraction, case | kg/d | Cell | Sheet edge, kg/d | Result |
| --- | --- | --- | --- | --- | --- |
| Fe | 0.25, reference | 25.67 | EW_7 | IA-EW-MET-7, 71.14 | bounded |
| Fe, oxide-bound, if fully leached | about 0.17, A (FeO 0.22) | 17.5 | EW_7 | 71.14 | bounded |
| Cu | 0.16, B | 16.43 | EW_3 | IA-EW-MET-3, 22.48 | bounded |
| Au | 0.00015, B | 0.0154 | EW_1 | IA-EW-MET-1, 59.87 | bounded |
| Ag | 0.0008, B | 0.0821 | EW_2 | IA-EW-MET-2, 59.89 | bounded |
| Ni, Zn, Sn, Pb, Cd, all in one element | 0.04, B | 4.107 | smallest of EW_4, 5, 6, 8, 9 | IA-EW-MET-4, 4.85 | bounded |
| metal_reactive | 0.05, reference | 5.13 | precipitate | reference | bounded |

The sheet edge rates are copper-equivalent study rates, not splits by element. They bound the mass of each element but do not identify it.

### Held

Table 4.2 lists the classes for which the envelope exceeds what the held design was sized for, and the units that are not covered.

Table 4.2. Classes held

| Class | Reference kg/d | Envelope maximum kg/d | Ratio | Units not bounded |
| --- | --- | --- | --- | --- |
| silicate_oxide | 18.48 | 101.65, A | 5.5 | FLOAT_SINK, GLASS_RINSE, GLASS_MILL, GLASS_DIGEST, BMED_BASE |
| water | 5.13 | 25.67, MSW | 5.0 | OIL_DRYER, leach water balance |
| organic | 22.59 | 30.80, MSW | 1.36 | OIL_DRYER, OIL_PYRO |
| unassigned | 15.38 | 35.01, MSW | 2.3 | Not identified |
| other_inorganic | 0 | 0.51, A | — | Not in the leach basis |
| Oxide-bound Al, Ca, Mg, Ti | not on the reference | A | — | Acid consumption and BMED caustic. Leachability not measured |

These units are not resized. A class stays held until a lot is characterized against section 1 and the rate is set from that lot.

## 5. S08

S08 carries solids from LEACH_CSTR_1 to MFG_SHOP at 42.0021 kg/d. This page does not change that rate. The edge carries the harvested metals and some entrained silicate.

The source is the list of cathode deposits booked on S08 in `EDGE_RATING_DUTY.md`. The nine deposits sum to 42.0000 kg/d, and the edge carries 42.0021 kg/d. The remaining 0.0021 kg/d is booked as entrained silicate, SiO₂, carried on the harvested cathode crib.

The silicate line is an assumption, not a measurement. It rests on the rate residual and on section 2: every case of the envelope carries `silicate_oxide` at 0.05 to 0.99, and the leach solids are in contact with the cathodes. Aqueous cells do not deposit silicon, so this silicon is carried over with the solids and is not plated. Table 5.1 gives the composition.

Table 5.1. Composition of S08

| Component | kg/d | Fraction | Source |
| --- | --- | --- | --- |
| Au | 0.0063 | 0.00014999 | deposit |
| Ag | 0.0251 | 0.00059759 | deposit |
| Cu | 8.7841 | 0.20913478 | deposit |
| Pb | 0.7111 | 0.01693011 | deposit |
| Sn | 0.7111 | 0.01693011 | deposit |
| Ni | 0.7111 | 0.01693011 | deposit |
| Fe | 29.6290 | 0.70541709 | deposit |
| Cd | 0.7111 | 0.01693011 | deposit |
| Zn | 0.7111 | 0.01693011 | deposit |
| SiO₂, entrained | 0.0021 | 0.00005000 | rate residual, assumption |

The fractions are on the 42.0021 kg/d rate and sum to 1.0. Si as the element is 0.4675 × 0.0021 = 0.00098 kg/d, a fraction of 0.0000234. The entrained fraction at the regolith-like end of the envelope is not known; it is held and nothing is resized for it. The field `assay_g_L` on this edge is the generic 50 g/L liquor template and was not used.

## 6. S16

S16 returns solids from MFG_SHOP to LEACH_CSTR_1 at 12.0 kg/d. This page does not change that rate.

`EDGE_RATING_DUTY.md` states that the composition of S16 is not given and that S08 governs. The S16 fractions are therefore the S08 fractions, including the entrained silicate. The note on the rate describes the stream as a mix of polymer and metal, but no polymer fraction was added.

## 7. Limits of this page

This page is not a weighed sample and does not define a design feed. It is not a reason to change a bore, a cell or a holdup. The edge field `assay_g_L` is not this assay. When a lot is characterized, it replaces the reference point, and any resizing that follows is made in a separate change. The station that reports a lot against section 1 is described in `docs-authority/INSTRUMENT_LOOPS.md`.

## 8. Held rates at the bounding cases, Rev D

This section records task X-BAS-02, calculated by `docs-authority/_bounding_case_study.py`. The feed is held at 102.68 kg/d. Table 8.1 gives the rate each edge would carry in each case. Nothing is resized here, because the task did not approve rate changes.

Table 8.1. Edge rates at the bounding cases

| Class | Unit | Edge | Graph kg/d | Case A | Case B | MSW | Method |
| --- | --- | --- | --- | --- | --- | --- | --- |
| silicate_oxide | FLOAT_SINK | IA-SINK-01 | 376.10 | 459.27 | 388.42 | 362.75 | increment on sink solids; regolith silicate assumed to report to sink, not to the glass train |
| water | LEACH_CSTR_1 | IA-EW-04 | 4287.80 | 4282.67 | 4285.75 | 4308.34 | feed water joins the liquor |
| organic | OIL_DRYER | IA-PLAST-01 | 33.00 | 0.00 | 37.50 | 45.00 | scales with organic fraction |
| organic | OIL_PYRO | IA-OIL-01 | 33.00 | 0.00 | 37.50 | 45.00 | scales with organic fraction |

At revision D, IA-ACID-01 carried 98.27 kg/d of 20 wt% HCl, which is 19.65 kg/d of HCl. Case A, with Al₂O₃ at 0.19, CaO at 0.125, MgO at 0.09 and FeO at 0.13 of the silicate fully leached, needs 87.9 kg/d of HCl, 4.5 times what the edge carried. TiO₂ and SiO₂ are taken as not leached.

Table 8.2 gives the result for each held line at revision D.

Table 8.2. Result for each held line (revision D)

| Line | Worst case | Change | Status |
| --- | --- | --- | --- |
| FLOAT_SINK solids (IA-SINK-01) | A | +22 % | Held. FLOAT_SINK sizing must take 459 kg/d if regolith-like feed is accepted. |
| Leach liquor water (IA-EW-04) | MSW | +0.5 % | Bounded. Inside the rounding of the liquor balance. |
| OIL_DRYER, OIL_PYRO (IA-PLAST-01, IA-OIL-01) | MSW | +36 % | Held. 45 kg/d at MSW; zero at A. |
| Acid demand (IA-ACID-01) | A | ×4.5 | Held, governing. Regolith-like feed could not be leached with the BMED_ACID acid regeneration as then sized. Accepting class A feed needed either a larger BMED_ACID or a cap on the silicate fraction. Resolved at revision E. |
| Glass train (IA-CULLET, IA-GLASS-01) | — | — | Held with reason. Cullet is glass from WEEE, not class silicate; regolith silicate is taken to report to sink (assumption). |
| unassigned | MSW 35.0 kg/d | ×2.3 | Held with reason. Not identified, so no unit can be assigned. |
| other_inorganic | A 0.51 kg/d | — | Bounded. Reports to sink, inside the FLOAT_SINK line. |

Acid demand was the governing bound. At revision D the choice was either to cap the accepted feed at the silicate fraction that the acid regeneration could cover, about 0.22 of the feed at full leaching of the case A oxides (by ratio), or to resize the acid system.

At revision E (task X-RSZ-01, 2026-10-15) the acid system was resized to the case A bound. The rates set then were IA-ACID-01 at 439.52 kg/d (87.9 kg/d of HCl), IA-BMED-03 at 449.50 kg/d and IA-BMED-04 at 493.08 kg/d, with a new edge IA-BASE-PPT carrying 374.38 kg/d of 20 wt% NaOH to hydroxide precipitation, and BMED_ACID at 16.13 kW. The acid line is no longer held.

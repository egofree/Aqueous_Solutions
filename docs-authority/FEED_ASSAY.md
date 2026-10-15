# Feed assay

Document number: AQS-ASSAY-001
Revision: C
Date: 2026-10-15
Authority: graph Rev BH. Not a PE stamp. Not a weighed sample.

| Rev | Description | Date |
| --- | --- | --- |
| B | Study fractions on IA-FEED-01, S08, and S16 | 2026-10-14 |
| C | Feedstock-agnostic basis. Class schema, bounding cases, bounded and held list. IA-FEED-01 carries a class point and the envelope. | 2026-10-15 |

The plant feed is not one material. It can be anything from a silicate and oxide regolith to a metal-rich printed circuit board, and any mixture between. This page is the schema every feed is characterized against, and the check of the held design across the range. No rate changes. Nothing is resized.

## 1. Schema

Every feed lot is reported as mass fractions, as received, in these seven phase classes. The classes sum to 1.0. A lot that cannot be reported this way is not a characterized feed.

| Class | What it holds | Where it goes in the plant |
| --- | --- | --- |
| `water` | Free moisture. Not bound water of hydration | OIL_DRYER, leach water balance |
| `metal_plateable` | Metallic or acid-soluble Fe, Cu, Ni, Zn, Sn, Pb, Cd, Co, Ag, Au | LEACH_CSTR_1, EW_1 to EW_9 |
| `metal_reactive` | Metallic Al, Mg, Ca, Ti, Li, rare earths | Precipitate cake. Not electrowon |
| `silicate_oxide` | SiO₂, silicate glass, ceramic, and oxide minerals, including oxide-bound Fe, Al, Ca, Mg, Ti | IA-SINK-01 to FLOAT_SINK, IA-CULLET to GLASS_RINSE, the glass line, BMED caustic |
| `organic` | Polymer, resin, paper, wood | OIL_DRYER, OIL_PYRO |
| `other_inorganic` | Sulfide, halide, phosphate, salts | Not in the leach basis |
| `unassigned` | Remainder | Named. Not identified |

Each lot also reports, as element mass fractions of the whole lot: Fe, Cu, Ni, Zn, Sn, Pb, Cd, Co, Ag, Au, Al, Si, and the leachable fraction of the oxide-bound Fe and Al. Si is reported as the element. SiO₂ is 0.4675 Si by mass (28.09 / 60.08).

## 2. Bounding cases

These are the cases the held design is checked against. None of them is the design feed.

| Case | Source | Status |
| --- | --- | --- |
| A, silicate and oxide, regolith-like | Published Apollo soil ranges, Heiken, Vaniman and French, *Lunar Sourcebook*, 1991. SiO₂ about 0.40 to 0.48, Al₂O₃ 0.10 to 0.28, FeO 0.04 to 0.22, CaO 0.09 to 0.16, MgO 0.06 to 0.12, TiO₂ up to 0.08. Native Fe-Ni metal and troilite each taken as 0.005 | Literature range, not a sample. Class values are assumptions inside that range |
| B, metal-rich PCB | `ELECTRICAL.md`, PCB-rich WEEE row | Published working average, not a sample |
| Reference point | `ELECTRICAL.md`, mixed WEEE row. The held rates were built on it | Carried only because the held rates were built on it. It is not the feed |
| Intermediate | `ELECTRICAL.md` rows: MSW, landfill bulk, landfill WEEE cell, Cu tailings, Au tailings | Published working averages. Soil is booked to `silicate_oxide`. Tailings Fe is booked as published to `metal_plateable`; most of it is oxide |

Class fractions:

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

The published Au tailings row sums to 1.0005. Its `unassigned` is set to 0.

Envelope, minimum to maximum over all cases: water 0 to 0.25, metal_plateable 0.005 to 0.35025, metal_reactive 0 to 0.05, silicate_oxide 0.05 to 0.99, organic 0 to 0.30, other_inorganic 0 to 0.005, unassigned 0 to 0.341.

## 3. IA-FEED-01

HOPPER to LEACH_CSTR_1, 102.68 kg/d. The rate stays. The 150 kg/d dock feed is not restored. The edge carries `plant feedstock, any class`. The composition object is the reference point in the seven classes. `params.assay_envelope` on the edge holds every case above and the bounds.

## 4. Check across the range

Rate held at 102.68 kg/d. Every case is taken at that rate. Leach recovery is taken as 1.0, which is the upper bound on what reaches a cell.

### Bounded by the held design

| Element | Largest fraction, case | kg/d | Cell | Sheet edge, kg/d | Result |
| --- | --- | --- | --- | --- | --- |
| Fe | 0.25, reference | 25.67 | EW_7 | IA-EW-MET-7, 71.14 | bounded |
| Fe, oxide-bound, if fully leached | about 0.17, A (FeO 0.22) | 17.5 | EW_7 | 71.14 | bounded |
| Cu | 0.16, B | 16.43 | EW_3 | IA-EW-MET-3, 22.48 | bounded |
| Au | 0.00015, B | 0.0154 | EW_1 | IA-EW-MET-1, 59.87 | bounded |
| Ag | 0.0008, B | 0.0821 | EW_2 | IA-EW-MET-2, 59.89 | bounded |
| Ni, Zn, Sn, Pb, Cd, all in one element | 0.04, B | 4.107 | smallest of EW_4, 5, 6, 8, 9 | IA-EW-MET-4, 4.85 | bounded |
| metal_reactive | 0.05, reference | 5.13 | precipitate | reference | bounded |

The sheet edges are copper-equivalent study rates, not element splits. They bound the element mass. They do not identify it.

### Held

| Class | Reference kg/d | Envelope maximum kg/d | Ratio | Units not bounded |
| --- | --- | --- | --- | --- |
| silicate_oxide | 18.48 | 101.65, A | 5.5 | FLOAT_SINK, GLASS_RINSE, GLASS_MILL, GLASS_DIGEST, BMED_BASE |
| water | 5.13 | 25.67, MSW | 5.0 | OIL_DRYER, leach water balance |
| organic | 22.59 | 30.80, MSW | 1.36 | OIL_DRYER, OIL_PYRO |
| unassigned | 15.38 | 35.01, MSW | 2.3 | Not identified |
| other_inorganic | 0 | 0.51, A | — | Not in the leach basis |
| Oxide-bound Al, Ca, Mg, Ti | not on the reference | A | — | Acid consumption and BMED caustic. Leachability not measured |

These units are not resized. A held class stays held until a lot is characterized against section 1 and the rate is set from it.

## 5. S08

LEACH_CSTR_1 to MFG_SHOP, 42.0021 kg/d, phase S. The rate stays.

Source: `EDGE_RATING_DUTY.md` cathode deposits booked on S08. The nine deposits sum to 42.0000 kg/d. The edge is 42.0021 kg/d. The difference is left on the rate.

| Metal | kg/d | Fraction |
| --- | --- | --- |
| Au | 0.0063 | 0.00015000 |
| Ag | 0.0251 | 0.00059762 |
| Cu | 8.7841 | 0.20914524 |
| Pb | 0.7111 | 0.01693095 |
| Sn | 0.7111 | 0.01693095 |
| Ni | 0.7111 | 0.01693095 |
| Fe | 29.6290 | 0.70545239 |
| Cd | 0.7111 | 0.01693095 |
| Zn | 0.7111 | 0.01693095 |

The carries line says metals and silicon. Silicon is not in this split. None was added. `assay_g_L` on this edge is the 50 g/L liquor stencil. It was not used.

## 6. S16

MFG_SHOP to LEACH_CSTR_1, 12.0 kg/d, phase S. The rate stays.

`EDGE_RATING_DUTY.md` says the composition is unstated and S08 governs. The fractions are the S08 fractions. The rate note calls the stream a polymer and metal band. No polymer fraction was added.

## 7. What this is not

Not a weighed sample. Not a design feed. Not a reason to change a bore, a cell, or a holdup. `assay_g_L` is not this assay. A characterized lot replaces the reference point. It does not resize in the same commit.

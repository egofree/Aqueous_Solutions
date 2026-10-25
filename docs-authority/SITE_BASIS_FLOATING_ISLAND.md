# Floating island site basis

Document number: AQS-SITE-007
Revision: A
Date: 2026-10-25
Profile: `flow_graph/param/sites/floating_island.json` (site id `floating_island`)
Plan: AQS-PLAN-011 section 10; owner decisions Q-030 (moored, tropical) and Q-031 (ride out the design storm)

| Rev | Description | Date |
|---|---|---|
| A | First issue with the first locale run: profile, environment, scaling actions, design consequences and closure result | 2026-10-25 |

Licence: CERN-OHL-S-2.0.

## 1. Purpose and scope

This page records the floating-island variant: a self-contained platform moored in tropical waters deep enough for an ocean thermal gradient, designed to ride out the design storm on its moorings. It states the environment the profile claims, the scaling actions the site applies, and the first locale run's closure result. The plant is a hull here: every kilogram counts against displacement, and the centre of gravity and the free surfaces of liquids set stability and freeboard.

## 2. Environment

| Quantity | Value | Source |
|---|---|---|
| Reference seawater | salinity 35.165 g/kg; sodium 10.78, chloride 19.35, magnesium 1.284, bromide 0.067 g/kg | SEAWATER_MILLERO |
| Lithium in seawater | about 0.18 mg/kg | LI_SEAWATER |
| Ocean thermal gradient | at least about 20 K between surface and about 1000 m, year-round in the tropics | OTEC_GRADIENT |
| Design storm | Saffir-Simpson Category 5, sustained 70 m/s; the platform rides it out on the moorings (Q-031) | SAFFIR_CAT5 |
| Corrosivity | offshore category CX for exposed steel | ISO12944_CX |
| Motion envelope (interim, A-M-388) | heel 5 deg, roll 8 deg, pitch 5 deg, heave 1.5 m/s2 | class-rule order-of-magnitude placeholders; metocean data and model tests replace them |
| Thermal design (interim, A-M-389) | cooling 32 C, heating 22 C (not governing), insulation ambient 27 C | metocean record at the mooring replaces them |
| Desalination energy | least 1.06 kWh/m3 at 50 % recovery | DESAL_MIN_ENERGY |

## 3. Scaling actions as applied

- HYDRO_SET eliminated: pumped hydro on a hull has little head and costs stability. Replacement: ZNBR2 with the hydrogen bank and fuel cell - a different storage technology, per the redundancy rule.
- GEO_GHEX and GEO_HP eliminated: no ground at a floating site. Replacement: seawater-source heat exchange through a duplicated DRY_COOLER pair (mode seawater) - the second heat-rejection source the ground loop used to be.
- EXT_HALL keeps standing: the building class no longer claims ground contact as a site service (bearing is structural - foundations on land, the hull deck per class rules at sea).
- No other scaling: the profile bindings drive the sizes.

## 4. Design consequences as built

- Heat rejection: the low-grade loop rejects to seawater through the DRY_COOLER pair. Deep cold water, where the intake reaches it, remains a design option for ventilation.
- Water: the make-up source is seawater by reverse-osmosis desalination; the reject brine feeds salt, magnesium, bromine and lithium recovery, each awaiting an assay feed case. The atmospheric condensate harvest continues regardless (it is indoor-air recovery).
- Power: PV primary (deck area limits the nameplate), standby generator and fuel cell behind it. Wave and ocean thermal are flagged options, entered where their sizing exists. The first run closes the 12 h night at 174.3 kW demand with 2091.6 kWh drawn and a coverage of exactly 1.00 - no margin (Section 5).
- Motion: the profile carries the design motion envelope; the sizing checks that will consume it (settlers, flotation, open and stirred tanks, electrowinning cells, the ZNBR2 bromine phase, packed-bed heights and tank sloshing) are part of the hull design pass and do not exist yet.
- Earthing: hull as earth electrode with sea return and cathodic protection; no soil.
- Codes: the marine family (class rules, SOLAS, MARPOL, the MODU code as the model, the intact stability code); the flag or coastal state decides which apply (Q-030).

## 5. Closure result and open items

The locale run closes: the mass balance and design checks pass, and the site writes 258 outputs that differ from the baseline under `sites/floating_island/`. One finding is recorded:

1. Storage coverage has no margin: the worst-stretch energy closes at exactly 1.00. The reserve must come from a storage re-size, the flagged wave or ocean-thermal sources, or generator runtime; the choice follows the power-portfolio rules (Q-024) and is part of the X-LOC-11 remainder.

Open items, in order:

1. The hull design pass: operating mass and centre of gravity summed over the scaled units, stability and freeboard checks under the class rules, compartmentation of liquid inventories against free-surface effects, and the motion-coupled sizing checks listed in Section 4.
2. The seawater intake, desalination and mineral-recovery units join the graph (the GW_INTAKE pattern), with the seawater feed case mapped in AQS-ASSAY-001.
3. The metocean record and class environmental method replace the interim motion and thermal values (A-M-388, A-M-389).
4. The mooring site itself (Q-030); every site-bound value in this page is a generic tropical interim until it is chosen.

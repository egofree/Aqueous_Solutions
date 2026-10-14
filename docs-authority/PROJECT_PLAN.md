# Project plan

Document number: AQS-PLAN-005
Revision: C
Date: 2026-10-12
Authority: graph Rev BH until `flow_graph/plant_flow_graph.json` says otherwise. Not a PE stamp.

The status of these lines is `docs-authority/MASTER_PLAN.md` (AQS-PLAN-004).
AQS-PLAN-003 is the module order against the tech tree. It is not this sequence.
AQS-PLAN-002 is the definition of a buildable unit.
AQS-PLAN-001, AQS-REM-001, and AQS-MVS-CHK-001 are history.

## Buildable

A unit is buildable when the inlet composition is on the edge, the nozzles have a location and a rating, the internals are drawn, relief has a destination, an instrument trips or the page says there is none, and a mesh exists. The 199 duty pages do not meet that test.

## Sequence

One phase, then the next. The active item is named here.

| Phase | Work | Stops when |
| --- | --- | --- |
| 0 | Record, cut test, electrical and thermal book | No rate has changed, and the Rev N drawings are marked or replaced |
| 1 | Feed composition, sheet split, digester, then the other streams that already have parts | Nothing is resized before its inlet composition is on the edge |
| 2 | Nozzles, line lists, the four missing classes | A connection can be built |
| 3 | Internals and holdup | No residence time is an envelope divided by a flow |
| 4 | Relief | Pressurized nodes have a case. Atmospheric nodes say so |
| 5 | Solids, on the operator box | Meshes match the duties at the revision that enters the phase |
| 6 | Self-copy | Not started until 0 through 5 are accepted |

Active item: D1. The study assay is written. It is not a weighed sample. No resize.

## Limits

The graph is the plant. A duty page does not outrank an edge.

`mvs.mvs_criteria.loops_closed` stays false. On-site evidence is not in the repo. A cut-test result is not that flag.

A missing measurement stays named on the open line.

Aqueous cells do not make aluminum, magnesium, calcium, lithium, titanium, silicon, or the rare earths. Anodes do not use iridium.

The frame standard is the parameter set in AQS-MOD-001.

Section 8 of a duty is the gap list. A unit with a gap in section 8 is not finished.

The 500 kg/day moonshot is not this graph.

## Revision B

Superseded by Revision C. Kept as the record of where Rev A stopped.

Rev A stopped being a complete plant at phase 2. Lines 0.1 through 2.1 are closed on the board. 2.2 is open. Phases 3, 4, 5, and 6 are not accepted.

What the files now support:

- The cut test passes at 1% and is not the MVS flag.
- No present mass edge has a measured composition. The feed, the sheet, and the digester volatile solids stay unnamed measurements.
- No duty has a flange class or a nozzle location. A connection cannot be built.
- Twenty-six duties say an envelope divided by a flow is not a residence time. None uses that quotient as the residence. That fact does not accept phase 3 while 2.2 is open.
- EXPANDER is the one written relief case. The other design pressures are the old head-plus-10 figures.
- Solids wait on the operator box.

Next, in order. Do not skip 2.2 by naming the gap and calling the phase accepted.

| Line | Work | Stops when |
| --- | --- | --- |
| 2.2 | One connection. Location from the placement seed. Flange rating from the fluid already on the edge. | HX8 was the trial. The seed has an origin and a size and no nozzle face. The line stays open until a face is on the drawing |
| 3 | Holdup only after 2.2 is accepted | No residence time is an envelope divided by a flow |
| 4.1 | Relief cases for the nodes that are actually pressurized | Atmospheric nodes say so. The head-plus-10 figure is not used as a set point |
| 5.1 | Meshes on the operator box | The mesh matches the duty at the revision that enters the phase |
| 6 | Self-copy | Not started until 2.2 through 5.1 are accepted |

R1 and R2 are recorded defects. They are not a nozzle.

## Revision C

This is the sequence that finishes the plant. Rev A and Rev B stay above as history. A line closes only on the board, in the same commit as the proof.

Complete means every present unit passes AQS-STD-001 and the buildable test in AQS-PLAN-002, except a hold on the list below. A hold is a missing measurement or a mesh the operator box has not compiled. A hold is not a number to guess. Nothing is resized from a placeholder composition.

### Holds

These stay named. They do not block a nozzle, a class, or a vent that the files already support.

| Hold | Why it stays |
| --- | --- |
| IA-FEED-01, S08, S16 | Study fractions are on the edges. Not a weighed sample. |
| IA-EW-SHEET | `metal` 1.0. The cell sheets are undifferentiated plate. Not an element split. |
| IA-FERM-RES, IA-STILL, IA-ABE-STILL | No volatile-solids measurement. They leave on IA-DIG-GAS. The gas composition is the liquid placeholder. |
| EW-1 current | `POWER.md` says 5.3 kW. The node is 6.0 kW study. The cell duties state the 2.5 V product against the node. No conductor is sized from the page. |
| `HEAT_LADDER_DUTIES.md` | Still the Rev K note. The graph is the duty. |
| IA-HDR-H2-01, 03, 04 | 2.1333 kg/d, empty layer list. Outside the mass cut. |
| EXPANDER `relief_mm` | 3.6 mm. Not recalculated at 550 kPa. Isentropic efficiency 70% is assumed. |
| MVS flag | `mvs.mvs_criteria.loops_closed` stays false. |
| No holdup basis | The duty says so. Envelope divided by flow is not used in its place. |
| Not measured | The unit, the coat life, the methane fraction, the tray efficiency, the approach, or the coefficient. |
| No diameter | No vessel diameter or machine envelope on the node. Not invented. |
| No heat rate | No kilowatts on the node. Area is not calculated. |
| 1.2 kg/m³ | Used for a gas volume where the edge has no m³/h. Not a measurement. Not resized. |
| 1000 kg/m³ | Used for a holdup. Not a measurement. Not resized. |
| Can pressure | Working pressure is not on the node. |
| HTU | A packing figure, not a measured transfer unit. |
| Stages | Stages and reflux are not set. |
| Vessel not built | The stated volume is not a measured volume. A reservoir volume is not the two-minute holdup. |
| SiC charge | Char as carbon, and the oxygen in the CO, are not an assay. |
| Phosphoric acid | Concentration is not on the node. 316L is not confirmed. |

### Rules that were being treated as gaps

Atmospheric connections are tube or hose. No flange class. AQS-STD-001 already says so. "No flange class" on a duty is not an open item for an atmospheric joint.

Where a process pressure is stated, the connection is rated at 110% of that pressure. The expander inlet is the one stated pressure: 550 kPa.

Envelope height plus 10 kPa is not a set point.

A residence time is not an envelope divided by a flow. That census is already clean: no duty uses the quotient as the residence.

### Nozzle rule

Used for every nozzle this sequence adds. Not a new standard number.

- Only a unit with `origin_mm` and `size_mm` on `flow_graph/placement_seed.json` gets a coordinate.
- The point is the center of a face of that box, in the placement frame, millimetres.
- Inlet on the −Y face. Outlet on the +Y face. Vent on the +Z face. Drain on the −Z face.
- Height is from the bottom of the envelope. Face center is half the height. Vent is the top. Drain is the bottom.
- Rating text for an atmospheric joint is `hose, atmospheric`.
- Bore is calculated only when the edge or the node already carries a density. Liquid at 1.5 m/s, gas at 10 m/s, raised to the next standard DN, minimum DN15. If the density is not there, the nozzle is located and section 8 says the bore was not calculated. 1000 kg/m³ and 1.2 kg/m³ are not used.
- A header gets a line list: tag, from, to, DN or "bore not calculated", rating. Not a vessel nozzle table.
- No edge is added to create a drain or a vent.

### Where the units are

199 present units.

| Set | Count | What happens |
| --- | --- | --- |
| Origin on the seed | 72 | Nozzle these first. Do not move them. |
| Named in a block, no origin | 43 | Pitch inside that block. No overlap. The plate does not grow. One that does not fit is named and left unplaced. |
| In no block | 84 | 65 are farm. The farm block is 12 m by 18 m. A bed is not shrunk to fit it. Cryo, wet, hab, geo, glass, and the shop unit go to the block of that sector only if the envelope fits. |

### Internals

Replace only the two generic strings. Do not rewrite a specific internal.

| On the node now | Count | Becomes |
| --- | --- | --- |
| shell and nozzles | 80 | The class row below, or "none" if the class has no vessel |
| media or gutter | 66 | The class row below, or "none" if the class has no vessel |
| A specific string | 53 | Left as written |

| Class | Internal |
| --- | --- |
| header, recycle_pipe | pipe only |
| scrubber | pall-ring bed, distributor, demister |
| heat_battery | stratification plate |
| hx | plate pack |
| cold_box | packed section, vacuum jacket |
| tank, cut_tank | dip pipe, stilling well |
| separator | weir and launder |
| ew_cell | already drawn. Do not touch |
| farm, tool, inverter, pv, rectifier, hab | none. Not a tank |

### Sequence

| Line | Work | Stops when |
| --- | --- | --- |
| C1 | This nozzle rule, the holds, and the counts | The rule is on this page. No rate change |
| C2 | HX8 | The duty matches HL-HX8-Q4-A and HL-HX8-Q4-B, 2.286 kW each. Two nozzles use the rule. The duty currently says there is no process nozzle and no heat rate. If those edges have no mass flow, the bore is not calculated. No rate change |
| C3 | The other 71 units that already have an origin | Each connection on a placed unit has a face, a height, and a rating under the rule, or section 8 says the bore was not calculated. Headers have a line list |
| C4 | The 43 block members with no origin | Each has an origin inside its block, or the line names the one that does not fit. No plate growth. No overlap |
| C5 | The 84 with no block | Farm beds that are larger than the farm block are named, not shrunk. The others are in the sector block or named |
| C6 | Generic internals | No present node still says "shell and nozzles" or "media or gutter" |
| C7 | Relief | Each atmospheric node says so and names an existing edge as the vent, or says it has no vent edge. No new set point. No new edge. EXPANDER stays 550 kPa to CRYO_ASU |
| C8 | Section 8 | Empty, or every remaining sentence is a hold from the table above |
| C9 | Meshes | Each present unit points at an STL, or the line says the solid is still an envelope. Envelope boxes do not count where the internal matters. The nine cell racks in `cad/stl` count. FreeCAD is not here. The operator box compiles the rest |
| C10 | Self-copy | Not started until C2 through C9 are accepted |

Active item: D1. The study assay is written. It is not a weighed sample. No resize.

## After Rev C

D1 is the feed assay. `docs-authority/FEED_ASSAY.md`. The study fractions are on IA-FEED-01, S08, and S16. They are not a weighed sample. The rate stays. The bore stays. The cell stays.

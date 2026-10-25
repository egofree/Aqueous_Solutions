# Frame system

Document number: AQS-MOD-002  
Former number: AQS-MOD-001 (duplicate cleared 2026-10-15, AQS-REG-001)  
Revision: D  
Date: 2026-10-25  
Study. Not a PE stamp.

| Rev | Description | Date |
|---|---|---|
| A-C | Earlier revisions: parameter set, service classes, sizes in use, load rule, fixed interfaces. | 2026-10-11 |
| D | Rewritten to the documentation style guide (AQS-DOC-002): purpose first, numbered sections and table titles. No parameter, class, size or load rule changed. | 2026-10-25 |

## 1. Purpose and scope

This page defines the welded-steel bay frame that carries the shop's process equipment: its parameter set, its material classes, the sizes in use, the load rule and the fixed interfaces. One size is not the standard. The standard is the parameter set; a bay is built from it. The builder is `models/freecad/frame.py` (section 7).

## 2. Parameters

| Name | Unit | Meaning |
|---|---|---|
| L, W, H | mm | Outside envelope |
| section | mm | Tube outside, square |
| wall | mm | Tube wall |
| material | — | From the class table |
| load_kg | kg | Process mass the frame carries |
| power_n | — | SB350 connectors, 48 V, 100 A each |
| fluid_n | — | 12 GPM coupler pairs |

Pitch is not fixed. L, W, and H are inputs. The weld pattern is fixed: four posts, top rectangle, bottom rectangle, feet.

## 3. Material by service

| Class | Service | Material | Why |
|---|---|---|---|
| dry | shop, lathe, mill, welder | ASTM A500 | Cheap, weldable, no acid |
| wet | leach, electrowinning, scrubber | 316L tube | HCl splash. Carbon steel pits |
| hot | furnace, silicon reduction | A500, with a heat shield | Structure is not the crucible |
| cold | cold-box base | 316L | Condensation, no rust |
| farm | beds, tank frame | HDPE or painted A500 | No weld on HDPE. Timber is allowed |
| clean | aligner, electronics | 6061 aluminum | Light, no rust, no acid |

The process vessel is not the frame. A PVC tank sits on a 316L frame. The frame does not see liquor.

## 4. Sizes in use

| Module | L × W × H mm | Class | Section |
|---|---|---|---|
| Lathe, mill, welder | 1200 × 600 × 800 | dry | 100 × 100 × 6 |
| EW-1, EW-2, EW-7, EW-9 | 1400 × 600 × 800 | wet | 100 × 100 × 6 |
| EW-4 to EW-6, EW-8 | 800 × 600 × 800 | wet | 80 × 80 × 5 |
| Furnace, silicon | 1200 × 600 × 800 | hot | 100 × 100 × 6 |
| Aligner | 1200 × 600 × 800 | clean | 80 × 80 × 5 |
| Cold-box base | 600 × 600 × 800 | cold | 80 × 80 × 5 |
| Cold-box tower | 300 × 300 × 6000 | cold | pipe, not this frame |
| Farm bed | 2000 × 1000 × 400 | farm | HDPE rail |

## 5. Load

Design load is the process mass times 2. Deflection limit is L/240 on the top rails. A 1200 mm rail at L/240 is 5 mm. If the calculated deflection exceeds that, the section goes up one size. The script does that check.

Mass of a steel frame is length of tube times section mass. A 100 × 100 × 6 tube is about 17 kg/m. A 1200 × 600 × 800 frame is 4 × 1.2 + 4 × 0.6 + 4 × 0.8 = 10.4 m, 177 kg. The old 97 kg figure was the 4 × 4 × 1/4 inch tube. That section is too light for a 21-plate cell.

## 6. Interfaces, fixed

Power connector is on the −X face, 200 mm up, regardless of L. Fluid couplers are on the +X face, 300 mm up. Feet are 10 mm plate, four corners. Lift points are the top corners. These do not scale. A machine that needs a second connector adds it beside the first.

## 7. Builder script

`models/freecad/frame.py` takes L, W, H, section, wall, and material, and builds the weldment. The table above is the call list. Change a number, rebuild the bay.

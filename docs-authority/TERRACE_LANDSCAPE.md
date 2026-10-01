# Terrace landscape — planting, irrigation, open vs greenhouse

Document number: AQS-TRR-001  
Revision: B
Date: 2026-09-27  
PFD: AQS-PFD-TRR-001 (`terrace_irrigation_pfd.png`)

Authority: AQS-SCALE-001 §6–7 (overflow massing + surplus policy),
AQS-BLD-001 (DRAIN_SEC / clean overflow), AQS-WTR-001 (clean inventory
vs regeneration), AQS-STR-001 / AQS-MF-001 (S40–S42), AQS-EQP-FRM-001,
`05-organic-farm-nutrient.md` §6.4 / §7.3 (greenhouse climate energy),
`freecad/params.py` (`SITE_LAT_DEG`, `TERRACE_*`, `OVERFLOW_*`).

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Basic issue: planting bands, irrigation, climate option rule | 2026-09-27 |
| B | 1 | Life-floor balconies TERRACE_*_L* + doors; grade OVERFLOW_* subordinate | 2026-10-01 |

Licence: CERN-OHL-S-2.0.

---

## 1. Scope

This note turns overflow-terrace **massing** (already in FreeCAD /
AQS-SCALE-001) into a **landscape and irrigation authority**. It does
not change plate sizes, `SCALE_M`, or rebuild `plant.FCStd`.

| In scope | Out of scope this pass |
|---|---|
| Planting band duties | FreeCAD bed / greenhouse solids |
| Open terrace vs enclosed greenhouse decision | Quantitative L/d irrigation balance |
| Water source + drain routing | Potable S26 use for landscape |
| Qualitative streams S40–S42 | Invented mass rates |

---

## 2. Massing already locked (do not reinvent)

### 2.1 Life-floor terraces (primary balconies)

Layout lock (AQS-BLD-001 Rev F): balconies start at the **top life
floor** and step down on **South, East, West** (NH) — one terrace per
floor — with a **door from each floor onto its terrace**
(`TERRACE_{S,E,W}_L*` / `TERRACE_DOOR_*`). Not roof-only overflow beds.

### 2.2 Grade overflow (surplus irrigation receiver)

Equator-facing grade bands follow `SITE_LAT_DEG`. Wrap east and west:

| Hemisphere | Faces |
|---|---|
| Northern (`SITE_LAT_DEG` ≥ 0) | South + East + West |
| Southern (`SITE_LAT_DEG` < 0) | North + East + West |

Conceptual surplus path (clean tower water only):

```
ZnBr2 full + ROOF_TANK full
  → OVERFLOW_SPILL_ROOF
  → OVERFLOW_DOWNCOMER_{S|N}
  → OVERFLOW_OUTFALL_{S|N}
  → OVERFLOW_TERRACE_{face}_B{n}   (n = 1 inner … N outer)
  → OVERFLOW_APRON_*
```

Never to process basement bund. Grade reference `Z_L0`. Params:
`TERRACE_BANDS`, `TERRACE_RUN`, `TERRACE_DROP`, `TERRACE_WIDTH`,
`TERRACE_DOWNCOMER_D`. Default site latitude on disk: 33° (Dallas-class
N-hemisphere) — equator-facing = South.

---

## 3. Climate decision rule — open terrace vs enclosed greenhouse

Select **one** primary envelope mode per site. Mixed sites may enclose
only the equator-facing primary band and leave E/W wrap open.

### 3.1 Prefer **enclosed greenhouse** on terrace when any of:

| Driver | Threshold / evidence | Why |
|---|---|---|
| Freeze / frost | Design winter outdoor T below crop frost tolerance for a material fraction of the intended growing calendar | Doc 05 §6.4 / §7.3 treats heating as the dominant greenhouse load in temperate / severe winters |
| High latitude / low winter DLI | `|SITE_LAT_DEG|` high enough that seasonal DLI forces heavy supplemental lighting *and* an insulated envelope is cheaper than open-air crop loss | Same energy section; LED canopy already exists indoors on FARM |
| Arid / high ET | Site aridity where open-band evaporative loss would force continuous makeup beyond surplus overflow availability | Protects clean-tower inventory; drip under cover |
| High wind / salt / dust | Design wind or coastal salt spray that strips media or damages canopy | Envelope is a keep-out, not a second FARM plate |
| Food-grade outdoor production | Operator wants food crops on terrace (not only ornamental) | Enclosed volume allows controlled fertigation (S42) without contaminating CATCH |

### 3.2 Prefer **open terrace** when all of:

| Driver | Rule |
|---|---|
| Frost-free crop window | Growing season covers the intended planting without freeze kill |
| Moderate wind | No design need for windbreak glazing |
| Water | Rainfall + intermittent clean overflow (S40) meet landscape ET without potable draw |
| Duty | Ornamental / soil-building / storm buffer — not primary food production |

### 3.3 Default for current parametric site

With `SITE_LAT_DEG = 33` (N-hemisphere, temperate / subtropical class):

- **Primary recommendation:** open terrace on S/E/W bands for landscape
  and surplus-water buffer.
- **Optional enclose:** south (equator-facing) band only if the operator
  commits to winter food production or documents freeze / arid drivers
  above.
- Indoor L1 FARM remains the primary food / aquaponic loop in either
  case.

**NOTE**

The climate rule chooses the envelope. It does not authorize farm-sump
liquor or potable water as landscape irrigation.

---

## 4. Planting bands

Bands step outward with plan run `TERRACE_RUN` and drop `TERRACE_DROP`
over `TERRACE_BANDS` (massing). Planting duty by band class:

| Band | Typical duty (open) | Typical duty (enclosed option) |
|---|---|---|
| Inner B1 (at plate face) | Access / drip header / wind-tolerant shrubs | Greenhouse entry / utility strip |
| Mid B2… | Perennial / cover / pollinator | Production beds (media or soil) |
| Outer BN + apron | Splash / overflow dissipator; deep-root buffer | Same; keep apron free of fertigation |

Equator-facing face gets the productive planting. E/W wrap repeats at
reduced yield expectation. Pole-facing facade stays low-yield (PV /
planting) per roof-plan language.

Species lists are operator / AHJ choices. This authority only locks
**water and nutrient routing**, not cultivars.

---

## 5. Irrigation water source (justified)

Three candidates were considered against AQS-WTR-001 and AQS-SCALE-001:

| Candidate | Verdict | Reason |
|---|---|---|
| **Clean overflow surplus (S40)** | **Primary** | Surplus policy already routes full ZnBr2 + full ROOF_TANK to terrace; water is clean tower inventory; AQS-WTR-001 open item called for terrace irrigation from clean overflow only |
| Roof clean S21 (gravity) as makeup | **Secondary** | Allowed when overflow is intermittent and landscape ET needs a trickle; still clean tower water; metered; never grey |
| Farm recirculation (FARM_SUMP) | **Forbidden for landscape** | Sump liquor is nutrient / condensate chemistry on HDR_GREY path (S13); dumping it on open bands contaminates grade and bypasses treatment |
| Potable S26 | **Forbidden** | Remineralized drinking path; RPZ / air-gap duty; wrong use class |

**Enclosed greenhouse fertigation (optional):** dilute tote branch from
NUTRIENT_DOSE may feed covered production beds. That branch is **not**
S40. Drain is S42 → HDR_GREY → treat — never into CATCH or ROOF_TANK.

**CAUTION**

Do not cross-connect fertigation piping to the overflow downcomer or
to SHAFT_PENSTOCK. Clean inventory and nutrient liquor stay separate.

---

## 6. Drainage back to catch

| Mode | Drain ID | Destination | Forbidden |
|---|---|---|---|
| Open terrace (rain + S40 only) | S41 | CATCH via apron / DRAIN_SEC class path | L-1 process bund; Salria; etch |
| Enclosed + fertigation | S42 | HDR_GREY → GREY treat / VCD_FEED class | CATCH; ROOF_TANK; sewer as primary |
| Storm peak on apron | — | Same as S41 (clean) | Process sumps |

Underdrains sit above grade apron slabs (`OVERFLOW_APRON_*`). Clean
return is a **side effect** of surplus dissipation, not a hydro power
claim. ZnBr2 remains the electrical battery (AQS-SCALE-001 §6).

---

## 7. Relationship to indoor FARM

| Item | Indoor FARM (L1) | Terrace (external) |
|---|---|---|
| Primary food | Yes (GROW_BED) | Only if enclosed option + AHJ food rules |
| Fish / biofilter | Yes | No |
| LED_CANOPY | Yes | Optional under enclosed only |
| Clean overflow irrigation | No (makeup is S01/S21 into sump) | Yes (S40) |
| CAD envelope today | `FISH_TANK`…`LED_CANOPY` | `OVERFLOW_TERRACE_*` massing only |

---

## 8. Streams (qualitative)

| ID | From | To | Status (AQS-MF-001) |
|---|---|---|---|
| S40 | OVERFLOW_SPILL_ROOF / clean tower surplus | Terrace irrig headers | Closed (routed); intermittent |
| S41 | Terrace underdrain / apron (clean) | CATCH / DRAIN_SEC | Closed |
| S42 | Fertigated greenhouse drain | HDR_GREY → treat | Closed / Claimed when option used |

No invented L/d or kg/d on this sheet.

---

## 9. PFD and regenerate

```bash
cd flow_graph/exporters/matplotlib  # or local hub pfd_scripts/
python3 terrace_irrigation_pfd.py
python3 farm_pfd.py
python3 campus_life_hazard_pfds.py   # water_cycle / campus footnotes
python3 building_stack_pfds.py       # roof plan footnote
```

---

## 10. FreeCAD follow-up (solids not this pass)

Same list as AQS-EQP-FRM-001 §6. Add climate flag in params when
envelope solids land (e.g. `TERRACE_ENCLOSED = False` default for
`SITE_LAT_DEG = 33`). No `SCALE_M` change in the documentation pass.

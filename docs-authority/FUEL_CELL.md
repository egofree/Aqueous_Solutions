# PEM fuel cell — plant H₂ / O₂ on Sol-Ark DC bus

Document number: AQS-FC-001  
Revision: B  
Date: 2026-10-01  
PFD: AQS-PFD-FC-001 (`fuel_cell_pfd.png`)  
Equipment: AQS-EQP-FC-001  
Streams: AQS-STR-001 S49–S53 (PEM); MeOH peer S73–S82 on AQS-MeOH-001

Authority: `POWER/Power_System_overview.md` (legacy H₂/O₂ PEM narrative),
hub `ELECTRICAL.md`, `FLOW_BATTERY.md`, AQS-PWR-002 (BACKUP_GEN ≠ FC),
AQS-GAP-001 §7 item 3, AQS-SCALE-001 §6, AQS-STR-001 / AQS-MF-001,
AQS-HSE-001 / AQS-EQP-CRY-001, AQS-REQ-KW-001, AQS-MeOH-001,
`freecad/electrical_yard.py`, root `06-energy-carbon-oxygen.md`
(MeOH path = **issued** at M1 via AQS-MeOH-001 — no longer deferred).

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Basic issue: PEM FC on Sol-Ark BATT DC; heat → Q4; ≠ BACKUP_GEN | 2026-09-28 |
| B | MeOH gap | MeOH IEM-FC coexist; continuous kW requirements; PEM retained | 2026-10-01 |

Licence: CERN-OHL-S-2.0.

---

## 1. Purpose

Document the PEM fuel-cell path on plant H₂/O₂ into the Sol-Ark BATT DC bus, distinct from BACKUP_GEN.

## 2. Scope

Closes the POWER legacy gap called **Missing** in AQS-GAP-001 §4 / §7
item 3: H₂/O₂ PEM fuel-cell path on the plant DC side, distinct from
the Sol-Ark **GEN**-port AC genset (AQS-PWR-002).

| In scope | Out of scope this pass |
|---|---|
| Chemistry lock: **PEM** using plant H₂ + O₂ | Replacing PEM with MeOH-only (both coexist) |
| Fuel / oxidizer sources from CRYO / EW | Hard-coded legacy 100–200 kW as issued nameplate |
| Electrical tie to documented DC bus | Full CRYO cold-box solids (next pass) |
| Low-grade heat → **Q4** via named HX | Mixing GEN exhaust into hab HVAC |
| Streams S49–S53 + PFD + equipment list | plant.FCStd rebuild (yard stub only) |
| Continuous kW **requirements** (AQS-REQ-KW-001) | SCALE_M change / git commit |
| Peer MeOH IEM-FC (AQS-MeOH-001) | Claiming MeOH deferred |

**NOTE**

`SCALE_M` stays **1.0**. No git commit. Do not hard-code legacy
“100–200 kW modular stacks” (`POWER/Power_System_overview.md`) as an
M1 yard nameplate — that figure is **legacy study narrative only**.

---

## 3. Decisions (locked this pass)

### 2.1 Chemistry — PEM (plant H₂ + O₂)

| Option | Verdict | Why |
|---|---|---|
| **PEM** H₂ + O₂ | **Selected** (retained) | Matches POWER Mermaid “H₂/O₂ PEM”; oxidizer from CRYO_O2 / EW anodic O₂; continuous **REQ-FC-CONT ≈ 4 kW_dc** (AQS-REQ-KW-001) |
| Methanol **IEM-DMFC** (AQS-MeOH-001) | **Selected** (peer path) | Diverse MeOH sources + IEM membranes (SEM-Tech preferred); **coexists** on BATT DC via MEOH_DCDC — not a PEM replacement |
| Solid-oxide / other FC | Out of scope | No tree authority for M1 |

Anode fuel = dried process H₂ (S05 / CRYO_H2 / S24 holdup branch).  
Cathode oxidizer = CRYO_O2 (S02 class) or EW anodic O₂ after dryer —
**not** raw ambient air as the named M1 oxidizer stream (air-breathing
may be a vendor option later; do not invent it here).

### 2.2 FC ≠ BACKUP_GEN

| Path | Port | Role |
|---|---|---|
| **BACKUP_GEN** (AQS-PWR-002) | Sol-Ark **GEN** (AC, S47) | Islanded AC failover when PV + ZnBr2 + grid unavailable |
| **FUEL_CELL** (this doc) | Sol-Ark **BATT DC** bus (S51) | DC contribution into the documented 160–700 V battery window |

Do not treat the genset as a substitute for the fuel cell, or the
reverse. Size CRYO_H2 against **GEN + FC + vent contingency**
(AQS-EQP-CRY-001 §5).

### 2.3 Electrical tie — Sol-Ark BATT DC

From `ELECTRICAL.md` and AQS-GAP-001 §4:

| Candidate bus | Status on M1 | Verdict for FC |
|---|---|---|
| RECT-EW / RECT-BMED / RECT-PK DC | Process **loads** fed from plant main AC | **Not** a generation bus |
| Legacy HVDC 400–800 V | **Partial** — not issued as CAD bus | Do not invent HVDC geometry |
| Sol-Ark battery ports (160–700 V) | **Present** — ZnBr2 already couples here | **Selected** |

FC stacks shall couple through a named **DC/DC converter**
(`FC_DCDC`) into the Sol-Ark battery / BATT DC window shared with
ZnBr2 and **MEOH_DCDC** (AQS-MeOH-001). Continuous requirement:
**REQ-FC-CONT ≈ 4 kW_dc** (3–5) from process H₂ (AQS-REQ-KW-001;
stand-in SI-FC-01). Capacity class upper **≤ ~60 kW** (SI-FC-02 /
Sol-Ark / ZnBr2). Legacy POWER “100–200 kW” remains citation-only
narrative — not M1 continuous.

**CAUTION**

Do not hard-tee FC DC into RECT process busbars. Do not parallel FC
AC onto the GEN port (that port is reserved for BACKUP_GEN).

### 2.4 Heat rejection — Q4 via named HX only

Low-grade stack / coolant heat → **`FC_HX_Q4`** → **Q4** header
(same discipline as GEO_HP / S44 / S06). Heat into FARM / HAB air
shall be < 80 °C water class.

**WARNING**

Never mix BACKUP_GEN exhaust (S46) or AFTERBURNER flue (Q1) into
hab / farm AHU. GEN exhaust stays on condensate / scrubber path.

### 2.5 Product water

PEM product water → condensate class (S52 → S13 / grey-condensate
path). Do not claim potable without remin + UV (AQS-WTR-001).

---

## 4. Placement — L0 POWER yard

Yard origin remains `electrical_yard.py` west of the **north** dock / plate at
`Z_L0` (AQS-BLD-001). Proposed massing (docs + FreeCAD envelope stub):

| Tag | Placement intent |
|---|---|
| `FUEL_CELL` | L0 yard near SOL_ARK_60K / ZnBr2 DC couple; outdoors or fire-rated nook per NFPA 2 |
| `FC_H2_MANIFOLD` | Branch from CRYO_H2 / H2_DRYER with isolation + flame arrestors (≠ HDR_H2 raw) |
| `FC_O2_MANIFOLD` | Branch from CRYO_O2; keep apart from H₂ manifold (25 ft / 1 h rule) |
| `FC_HX_Q4` | On Q4 water header with GEO_HP peers |
| `FC_DCDC` | Adjacent to Sol-Ark / ZnBr2 DC tray |

Full `plant.FCStd` rebuild is **required** before these envelopes
appear in the assembled plant model — stub only this pass.

---

## 5. Streams (qualitative)

| ID | From | To | Ph | Carries | Notes |
|---|---|---|---|---|---|
| S49 | CRYO_H2 / H2_DRYER | FUEL_CELL | G | dried H₂ fuel | Branch of S05; MAQ; ≠ S45 GEN branch without isolation |
| S50 | CRYO_O2 | FUEL_CELL | G | O₂ oxidizer | S02 class; never tee HDR_H2 |
| S51 | FUEL_CELL / FC_DCDC | Sol-Ark BATT DC | E | DC in 160–700 V window | ≠ GEN AC; ≠ RECT process DC |
| S52 | FUEL_CELL | condensate / S13 class | L | product H₂O | Claimed; not potable without remin |
| S53 | FC_HX_Q4 | Q4 / FARM / HAB | E | heat < 80 °C | Same Q4 rule as S06 / S44 |

S24 (EW cathode / H2_DRYER → roof vent or CRYO) remains Open /
Recapturable. Closing path now includes **FC + GEN** consumers so
dryer holdup stays under MAQ and roof vent is contingency only
(AQS-MF-001 §5).

---

## 6. Relationship to BACKUP_GEN and CRYO_H2

```
CRYO_H2 / H2_DRYER
    ├── S45 ──► BACKUP_GEN ── S47 AC ──► Sol-Ark GEN
    ├── S49 ──► FUEL_CELL  ── S51 DC ──► Sol-Ark BATT DC (via FC_DCDC)
    └── S24 ──► roof vent (contingency) / CRYO holdup

CRYO_O2 ── S50 ──► FUEL_CELL cathode
FUEL_CELL ── S53 ──► FC_HX_Q4 ──► Q4 (with GEO_HP / S44 / S06)
FUEL_CELL ── S52 ──► condensate (S13 class)
```

CRYO_H2 inventory shall be sized for **GEN + FC + vent contingency**.
Actual cold-box column / sieve / expander solids remain the next
cryo pass; this document locks the **interface only**.

---

## 7. MAQ / HSE notes

1. H₂ inventory: CRYO_H2 + H2_DRYER + FC / GEN manifolds stay under
   AQS-HSE-001 §3 design cap (< 150 lb class holdup target).
2. Class I / Div 2 / Group B envelopes extend to FC H₂ flanges and
   manifolds (same family as H2_DRYER / CRYO_H2).
3. O₂ manifolds: keep oxidizer separation from H₂ and organics
   (NFPA 55 / 400 practice already stated for HDR_O2 × HDR_H2).
4. FC outdoor pad preferred; if enclosed, ventilation + H₂ detection
   at 25% LFL trip (NFPA 2 / 69) shall isolate FC fuel and trip
   rectifiers per existing H₂ logic.
5. ZnBr2 Br₂ tower remains isolated (NFPA 855); do not share scrubber
   with FC purge.

---

## 8. Other plant fuel consumers (inventory)

Add consumers only with tree evidence.

| Consumer | Class | Evidence | Fuel / oxidizer | Stream / note |
|---|---|---|---|---|
| **BACKUP_GEN** | **Present** | AQS-PWR-002 / AQS-EQP-GEN-001 / AQS-PFD-GEN-001 | Plant H₂ primary; diesel contingency | S45 / S47 |
| **FUEL_CELL** | **Present** (docs/PFD) | AQS-FC-001 / AQS-EQP-FC-001 / AQS-PFD-FC-001 | Plant H₂ + O₂ (PEM) | S49–S53 |
| **MEOH_FC** | **Present** (docs/PFD) | AQS-MeOH-001 / AQS-EQP-MEOH-001 / AQS-PFD-MEOH-001 | MeOH (IEM-DMFC preferred) | S73–S82 |
| **AFTERBURNER** | **Present** | `oil_line.py`, AQS-PFD oil line, FAN_STACK, S18 | Oil-line **NCG** / tar destruction (thermal oxidizer); not a named plant-H₂ power consumer | HDR_OIL_VAPOR → AFTERBURNER; flue = Q1 / SHAFT_OIL |
| Induction pyro coil | **Present** (electric) | `ELECTRICAL.md` | Electric 5–20 kHz — **not** a combustion fuel consumer | AC load |
| Dedicated electrolyzer skid | **Superseded** | AQS-GAP-001 §4 | Cathode H₂ is EW byproduct | — |
| Oxy-fuel torches / weld pilots / propane heaters | **Missing / deferred** | No dedicated fuel stream in STREAM_REGISTER or MFG equipment lists; WELD_MAP is GMAW/SMAW electric | Do not invent H₂ torch headers this pass | — |
| Biogas burner (S30) | **Deferred** | AQS-PWR-001 | Digester gas cleanup not scheduled | — |

---

## 9. Rebuild / sync

```bash
cd flow_graph/exporters/matplotlib  # or local hub pfd_scripts/
python3 fuel_cell_pfd.py
python3 electrical_sld.py
python3 geothermal_pfd.py          # Q4 peer callout if regenerated
python3 backup_gen_pfd.py          # FC ≠ GEN note if regenerated
```

Optional FreeCAD envelope only (no full plant rebuild this pass):

```bash
# edit models/freecad/electrical_yard.py stubs (FUEL_CELL, FC_*), then:
# /usr/bin/freecadcmd models/freecad/electrical_yard.py
# Full plant.FCStd rebuild REQUIRED before yard stubs appear in plant.
```

Share mirror: `share/aqueous-solutions/docs-authority/`,
`pfd/scripts/`, `pfd/images/`, `models/freecad/electrical_yard.py`.

---

## MeOH peer path (Rev B)

Methanol train is **issued** under **AQS-MeOH-001** (no longer deferred).
PEM on plant H₂ + O₂ remains the primary Faraday-limited FC path.
MeOH IEM-FC is a **peer** on BATT DC. See AQS-REQ-KW-001 for continuous
kW requirements and stand-in table.

Style: AQS-DOC-002. Compliance: AQS-COMPL-001 (NEC FC DC / NFPA 2 / NFPA 30 MeOH themes).


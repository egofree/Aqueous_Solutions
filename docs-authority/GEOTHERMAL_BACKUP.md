# Geothermal loop and backup generator — POWER gap close

Document number: AQS-PWR-002  
Renumbered 2026-10-15 from AQS-PWR-001 to clear a duplicate (AQS-REG-001).
Revision: B  
Date: 2026-09-28  
PFDs: AQS-PFD-GEO-001 (`geothermal_pfd.png`), AQS-PFD-GEN-001 (`backup_gen_pfd.png`)  
Equipment: AQS-EQP-GEO-001, AQS-EQP-GEN-001

Authority: `POWER/Power_System_overview.md`, hub `ELECTRICAL.md`,
`FLOW_BATTERY.md`, AQS-GAP-001 §4 / §7 item 4, AQS-SCALE-001 §6,
AQS-STR-001 / AQS-MF-001 (S43–S48), `freecad/electrical_yard.py`,
`electrical_sld.png`, GAS_SYSTEM exhaust-recapture intent, root
`06-energy-carbon-oxygen.md` (FC narrative remains separate).

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Basic issue: GHEX + heat pump; H₂ genset on Sol-Ark GEN | 2026-09-27 |
| B | 1 | FC relationship closed (AQS-FC-001); Q4 peer FC_HX_Q4 | 2026-09-28 |

Licence: CERN-OHL-S-2.0.

---

## 1. Purpose

Close POWER gaps for GHEX/heat pump and H₂ BACKUP_GEN on the Sol-Ark GEN port.

## 2. Scope

Closes the POWER legacy gaps called **Missing / Partial** in
AQS-GAP-001: geothermal baseload path, and backup generator on the
Sol-Ark **GEN** port (previously spare).

| In scope | Out of scope this pass |
|---|---|
| Ground heat-exchanger class + heat-pump thermal path | Invented electric kW beyond published POWER / ELECTRICAL figures |
| Backup genset fuel decision from plant streams | PEM FC issued separately (AQS-FC-001); MeOH DMFC still deferred |
| GEN port interconnect + L0 yard placement | Binary ORC electric rating lock (stub only) |
| Qualitative streams S43–S48 | FreeCAD plant rebuild / SCALE_M change |
| Equipment lists + regenerable PFDs | Site bore-field survey / AHJ permits |

**NOTE**

`SCALE_M` stays **1.0**. No git commit. Do not hard-code legacy
“400 kW solar / 100 kW geothermal / 280 kW campus” as M1 yard
nameplate — those figures stay narrative targets in
`POWER/Power_System_overview.md` until SCALE_M growth and a site
resource survey support them.

---

## 3. Decisions (locked this pass)

### 2.1 Geothermal — heat pump primary; ORC electric TBD

| Path | Decision | Rationale |
|---|---|---|
| Ground heat exchanger | **Closed-loop vertical bore field** class (`GEO_GHEX`) | Avoids producing brine / geothermal fluid that would enter process headers; matches campus closed-loop water discipline |
| Thermal use | **Water-source heat pump** (`GEO_HP`) → **Q4** (`S44`) | M1 HVAC already on Q4 (ELECTRICAL HVAC 1.5 kW class); heat pump displaces resistance / boiler without claiming new generation kW |
| Electric generation | **Binary ORC stub** (`GEO_ORC`) — **rating TBD** | Legacy Mermaid claims “Geothermal Generator 100 kW baseload”; M1 module peak is ~50 kW continuous class (`ELECTRICAL.md`). Do not claim 100 kW on the M1 yard. ORC may AC-couple later when resource + SCALE_M justify |

**CAUTION**

Do not tee geothermal loop fluid into HDR_UPW, CATCH, Salria, or
life potable. Loop fluid is a dedicated closed circuit (S43).

### 2.2 Backup genset — plant H₂ on Sol-Ark GEN

| Option | Verdict | Why |
|---|---|---|
| **H₂ AC genset** (primary) | **Selected** | Fuel from existing plant streams S05 / CRYO_H2 / S24 holdup; matches POWER Mermaid “diesel/H₂”; exhaust is primarily H₂O (→ condensate class) + air nitrogen oxides to scrubber — not an external carbon import |
| Diesel / biodiesel | Contingency only | External fuel breaks closed-loop claim; retain as emergency procurement path, not the named M1 duty |
| Biogas from S30 black digest | Deferred | Digester gas quality / cleanup not scheduled; would compete with nutrient dose |
| Methanol DMFC (root 06) | Out of scope | **PEM** FC is Present (AQS-FC-001 on BATT DC); MeOH DMFC remains deferred — neither is the Sol-Ark GEN AC port |

Sol-Ark 60K **GEN** terminal is 200 A class (`ELECTRICAL.md`). Genset
continuous rating is **TBD** — size to critical islanded load and
GEN-port limits; do not invent a kW nameplate beyond the published
module peak (~50 kW) and inverter continuous (60 kW) as **upper
bounds for study**, not issued ratings.

### 2.3 Interfaces to RECT / ZnBr2 / PV

```
PV_ARRAY*  ──PV DC──►  SOL_ARK_60K  ◄──BATT DC──  ZNBR2*
                         │
              GEN port ◄─┴── S47 AC ── BACKUP_GEN  ◄── S45 H₂
                         │
              LOAD ──► ATS S2 ──► PLANT MAIN ──► MCC + RECTIFIER*
                         │
              GRID ↔ utility / optional backfeed

GEO_GHEX ◄──S43──► GEO_HP ──S44 Q4──► FARM / HAB HVAC
GEO_ORC (stub) ──S48 TBD──► Sol-Ark AC couple (future)
```

Rectifiers remain on plant main AC after ATS. Backup does **not**
feed tankhouse DC directly. ZnBr2 stays the night / pyro peak buffer;
genset is failover when PV + ZnBr2 + grid are unavailable or for
ordered island tests.

---

## 4. Placement — L0 POWER yard

Yard origin remains `electrical_yard.py` west of the **north** dock /
plate at `Z_L0`, Y-aligned to `DOCK_Y` (AQS-BLD-001 Rev D / AQS-SITE-001). Proposed massing (docs + optional FreeCAD stub):

| Tag | Placement intent |
|---|---|
| `BACKUP_GEN` | L0 yard, immediately adjacent to `SOL_ARK_60K` (+X or +Y of inverter) so GEN feeder is short |
| `GEN_H2_BUFFER` | Small hold tank / manifold between CRYO_H2 branch and genset; outdoors or fire-rated nook per NFPA 2 — detail TBD |
| `GEO_HP` | L0 yard mechanical pad near POWER, or grade mechanical room west — keep off L1 life |
| `GEO_GHEX` | Off-plate bore field (site); CAD shows **keep-out / stub header** only at yard edge |
| `GEO_ORC` | Stub footprint south of yard; dashed until resource survey |

**WARNING**

H₂ equipment outdoors shall observe MAQ / classified-area rules already
noted for S24 (AQS-MF-001 §5). Do not route HDR_H2 process capture
header into the genset fuel manifold without flame arrestors and
isolation from the EW cathode header.

---

## 5. Streams (qualitative)

| ID | From | To | Ph | Carries | Notes |
|---|---|---|---|---|---|
| S43 | GEO_GHEX | GEO_HP (closed) | L/E | loop fluid | Dedicated; not UPW / CATCH |
| S44 | GEO_HP | Q4 / FARM / HAB | E | heat < 80 °C | Same Q4 rule as S06 |
| S45 | CRYO_H2 / H2_DRYER | BACKUP_GEN | G | dried H₂ fuel | Branch of S05; MAQ |
| S46 | BACKUP_GEN exhaust | condensate / scrubber | G/L | H₂O + NOx class | Claimed; not raw to HDR_CO2 |
| S47 | BACKUP_GEN | SOL_ARK GEN port | E | 480 V 3φ AC | Closes spare GEN |
| S48 | GEO_ORC (stub) | Sol-Ark AC | E | ORC AC | Rating TBD; dashed |

---

## 6. Relationship to fuel cell (AQS-FC-001)

PEM fuel cell is issued under **AQS-FC-001** / AQS-EQP-FC-001 /
AQS-PFD-FC-001. This genset document does **not** substitute for the
fuel cell:

| Path | Port | Stream |
|---|---|---|
| BACKUP_GEN | Sol-Ark **GEN** (AC) | S45 fuel / S47 AC |
| FUEL_CELL | Sol-Ark **BATT DC** (via FC_DCDC) | S49/S50 fuel / S51 DC |

FC low-grade heat joins **Q4** through `FC_HX_Q4` (S53) — same header
discipline as GEO_HP (S44) and S06. Never mix GEN exhaust (S46) into
hab HVAC. Size CRYO_H2 for **GEN + FC + S24 vent contingency**
(AQS-EQP-CRY-001). Methanol DMFC (root 06) remains deferred.

---

## 7. Rebuild / sync

```bash
cd flow_graph/exporters/matplotlib  # or local hub pfd_scripts/
python3 geothermal_pfd.py
python3 backup_gen_pfd.py
python3 fuel_cell_pfd.py
python3 electrical_sld.py
python3 campus_life_hazard_pfds.py   # POWER yard callout
python3 building_stack_pfds.py       # L0 POWER yard callout
```

Optional FreeCAD envelope only (no full plant rebuild required for
doc issuance):

```bash
# edit cad/freecad/electrical_yard.py stubs, then if desired:
# /usr/bin/freecadcmd cad/freecad/electrical_yard.py
```

Share mirror: `share/aqueous-solutions/docs-authority/`,
`pfd/scripts/`, `pfd/images/`.

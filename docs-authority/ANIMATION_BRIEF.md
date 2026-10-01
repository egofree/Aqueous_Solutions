# Phase D — animation brief

A–C massing exists. These shots are the next fidelity layer, not a new
process. Run them in `/usr/bin/freecad` on `plant.FCStd`. Do not use the
1.1.1 AppImage. Do not render photoreal frames.

Proxy token: a 80 mm sphere named `TOKEN` parented to the active shot
path. One token at a time.

Frame rate 12 fps. Export PNG from the 3D view (no diffusion).

## Shot list

| # | Name | Duration | Path | Notes |
|---|---|---|---|---|
| D1 | Shred drop | 4 s | HOPPER throat → vibratory conveyor deck → lid coaming → liquor | No screen. Dust hood stays put. |
| D2 | Float / sink | 6 s | Two tokens. Float: liquor surface → weir lip → FLOAT DEWATER → OIL LINE stub. Sink: floor trough → CSTR 3 lift → SINK DEWATER → VIBRATORY SPLIT. | Split then forks: plastic token to OIL stub, grit token to GLASS stub. |
| D3 | EW overflow | 8 s | TOKEN in liquor from LEACHATE PUMP → EW-1 inlet → overflow weir of each cell to EW-9 | One hop per second. Metal name on LBL_EW_n stays. |
| D4 | Powder drop | 5 s | EW-1 funnel → valve → pail (or VDF). Repeat EW-6 Fe as powder. | Bund catches a miss. Liquor does not leave the bund. |
| D5 | Pyro auger | 6 s | DRYER discharge → INDUCTION_PYROLYZER axis → QUENCH | Token stays inside the Ti pipe. Coils do not rotate with the charge; the iron auger does. No FR-4 token on this path. |
| D6 | Fractionator cuts | 8 s | QUENCH liquid → FRACTIONATOR → four cut tanks in boiling-point order. C29 token returns on C29_RECYCLE to pyro inlet. | NCG token goes AFTERBURNER, never HDR_ACID_GAS or HDR_H2. |

## Camera

- D1–D2: three-quarter from −Y, include mezz and weir.
- D3–D4: aisle long shot from −Y, bund in frame.
- D5–D6: oil train from −Y, afterburner in the far +X.

## What not to animate

Workers, flames, dirty effluent, mixed-header flow, FR-4 in the pyro,
Br₂ into CRU.

Keyframe helper: `freecad/animate_shots.py` prints the path waypoints
including D6 cuts / C29 recycle / NCG.

Schematic frames (plan token, not a GUI capture):

```
python3 cad/freecad/render_frames.py
```

Output: `cad/animation/D0_overview.png`, `D1.png`…`D6.png`, `F0_campus.png`.
Document AQS-ANM-001.

12 fps PNG from `/usr/bin/freecad` on `plant.FCStd` is still an
operator-box overlay of the same waypoints. Do not replace these
sheets with diffusion frames.

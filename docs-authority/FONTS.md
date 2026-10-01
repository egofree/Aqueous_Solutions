# Fonts for 3D sign glyphs

Document number: AQS-FONT-001  
Revision: Basic issue  
Date: 2026-09-26

The plant hardware is CERN-OHL-S-2.0. Glyphs on sign plates are cut at
build time from a system font. This repository does not ship a TTF.

## Allowed

Liberation Sans Bold, SIL Open Font License 1.1 (SPDX: OFL-1.1).
Reserved name: Liberation. Ubuntu package: `fonts-liberation`.
OFL embedding in a document or a generated solid does not change the
licence of this project.

```
sudo apt-get install -y fonts-liberation
```

`labels.py` looks only for LiberationSans-Bold.ttf.

## Not allowed as a dependency

| Font | Licence problem |
|---|---|
| DejaVu / Bitstream Vera | Bitstream-Vera licence: rename-on-modify, no standalone sale. Usable on a workstation, not a declared project dependency. |
| GNU FreeFont | GPL-3 with font exception. Stronger copyleft than we need next to CERN-OHL-S. |
| Any proprietary face (Arial, Helvetica) | Not distributable with the design. |

## Generated solids

A STEP or FCStd that contains extruded letter outlines is a document
that embedded a subset of the font. OFL FAQ 1.12–1.13: that does not
put the plant under OFL and does not require us to ship OFL.txt with
every STEP. If someone later vendors the TTF itself into `cad/`, they
must add OFL.txt and keep the reserved name Liberation.

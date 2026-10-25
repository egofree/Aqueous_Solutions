# Fonts for 3D sign glyphs

Document number: AQS-FONT-001  
Revision: A  
Date: 2026-10-25

| Rev | Description | Date |
|---|---|---|
| Basic issue | First issue | 2026-09-26 |
| A | Purpose and scope added; text rewritten to the documentation style guide (AQS-DOC-002). The font policy is unchanged. | 2026-10-25 |

## 1. Purpose and scope

The sign plates of the plant carry raised or cut letters (glyphs). The glyph outlines are taken from a font file on the build machine when the models are generated. This page states which font may be used for this and why, so that the licence of the font does not conflict with the licence of the plant design.

The plant hardware design is released under the CERN Open Hardware Licence, strongly reciprocal variant, version 2.0 (CERN-OHL-S-2.0). This repository does not contain a TrueType font file (TTF); the font is installed on the build machine as a system package.

## 2. Permitted font

The only permitted font is Liberation Sans Bold. It is released under the SIL Open Font License 1.1 (SPDX identifier OFL-1.1), and its reserved font name is "Liberation". On Ubuntu it is provided by the package `fonts-liberation`, which is installed with:

```
sudo apt-get install -y fonts-liberation
```

The label scripts `models/freecad/labels.py` and `flow_graph/exporters/matplotlib/labels.py` look only for the file LiberationSans-Bold.ttf. Embedding an OFL font in a document or in a generated solid does not change the licence of this project.

## 3. Fonts that may not be declared as dependencies

Table 3.1 lists fonts that are not permitted as declared project dependencies, with the reason for each.

Table 3.1. Excluded fonts

| Font | Reason |
|---|---|
| DejaVu and Bitstream Vera | The Bitstream Vera licence requires a modified font to be renamed and forbids selling the font on its own. These fonts may be used on a workstation but may not be declared as a project dependency. |
| GNU FreeFont | It is licensed under the GPL-3 (GNU General Public License version 3) with a font exception. This is a stronger reciprocal (copyleft) condition than the project needs alongside CERN-OHL-S. |
| Any proprietary typeface, such as Arial or Helvetica | It may not be distributed with the design. |

## 4. Generated solid models

A STEP or FreeCAD (FCStd) model that contains extruded letter outlines is a document that embeds a subset of the font. According to questions 1.12 and 1.13 of the OFL FAQ (frequently asked questions), this does not place the plant design under the OFL and does not require a copy of the licence file OFL.txt to be supplied with every STEP file. If the TTF file itself is ever copied into the repository under `cad/`, the file OFL.txt must be added beside it and the reserved name Liberation must be kept.

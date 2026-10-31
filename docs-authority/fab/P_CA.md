# P_CA fabrication

Class: precip; sector DIGESTER. Study route. Not stamped.
Envelope: Envelope 300×300×400 mm;
service line: duty calcium-soap precipitation: wax + lime -> the grease thickener (feeds GREASE_CA); thickener_kgd 0.025.

Internals: duty sheet: "0.025. 3. Material. PP-H precipitation vessel + PP agitator; PE slurry lines; steel frame and housing outside " [docs-authority/duties/P_CA.md]
Material: PP-H precipitation vessel + PP agitator; PE slurry lines; steel frame and housing outside the wetted headspace. (continues on the duty sheet)

Nozzles: 2 process connections per docs-authority/nozzles/P_CA.csv

Production route (issued ahead of the CAD build; fabrication does not start before unit
tasks 10-12 close; the section 3 material selections are issued per AQS-STD-006):
1. Assembly route: per the unit duty sheet size line, standard first-stage parts.
2. Working parts per the duty sheet; the part set is the unit task 10-12 deliverables.
3. Connections: nozzle stubs to the schedule; flange faces per AQS-PIP-003 class letters
4. Test: hydrostatic/water-fill and pressure hold per AQS-STD-001 section 4; dry-run only until
    the CAD acceptance (AQS-PLAN-006 M3) and the real BOM land.

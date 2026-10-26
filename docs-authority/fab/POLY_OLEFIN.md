# POLY_OLEFIN fabrication

Envelope 600 x 600 x 1200 mm shell over the DN150 x 225 mm reactor (reactor-class study minimum,
AQS-DUTY-073; A-M-283). Design 5 MPa gauge: ASME VIII-1 UG-27 wall 3.8 mm at the 250 C top of the
150-250 C / 1-5 MPa window (graph design; AQS-SIZE-OIL-POLY).

Production route (MFG/FAB, in-house, X-MFG-31):
1. Shell: SA-240 316L DN150 seamless pipe section x 225 mm straight side, SA-403 fittings caps,
   full-penetration welded per ASME IX (WPS-02 CS/SS class set, AQS-WLD-002); design wall 3.8 mm.
   Code intent (AQS-ASME-002 Rev C): B31.3 piping component by size, U-1(c)(2)(j), ID 142 mm
   <= 152 mm; the UG-27 wall check was made with the size in AQS-DUTY-073.
2. Feed heater: 25 -> 200 C feed preheat band charged to the 250 C reactor top (heat_W 0.0013
   study loss row; the heater basis is the Q-ladder tie, AQS-SIZE-OIL-POLY).
3. Internals: inlet distributor per the parametric source; vent line to OIL_FRAC.
4. Hydrotest 1.5 x 5 MPa = 7.5 MPa hold (ASME B31.3 345.4.2, per the AQS-ASME-002 Rev C test row
   for the piping-component class), with 341 examination on the two welded seams; then the 250 C
   shakedown on hot oil from the Q3 spare leg.
5. Interlocks: high pressure (>1 MPa x reactor setpoint), high temperature, low feed flow.

Inspect against models/mfg/POLY_OLEFIN/export/poly_olefin.step. Not stamped (shop, not code
stamped; AQS-ASME-002 runs the jurisdiction list separately). Production rate stays 0.0
(feed-blocked, A-M-267: the C5-C10 collection feed is not received at the dock on IA-C5-POLY); design case
feed_kg_d 0.2941 with the per-kg tables in AQS-DUTY-073.

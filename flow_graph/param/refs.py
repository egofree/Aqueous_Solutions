"""Citation registry for the parametric model. Code cites by key; docs print the full entry.
Only published sources: standards, textbooks, peer-reviewed papers, manufacturer data."""
REFS = {
 'CODATA2018': 'Tiesinga E. et al., CODATA recommended values of the fundamental physical constants: 2018, Rev. Mod. Phys. 93, 025010 (2021). F = 96485.33212 C/mol; R = 8.314462618 J/(mol K).',
 'CIAAW2021': 'IUPAC CIAAW, Standard atomic weights 2021, Pure Appl. Chem. 94(5), 573-600 (2022).',
 'SCHLESINGER2011': 'Schlesinger M.E., King M.J., Sole K.C., Davenport W.G., Extractive Metallurgy of Copper, 5th ed., Elsevier (2011), ch. 17 electrowinning: current density 200-350 A/m2, cell voltage about 2 V, current efficiency 0.85-0.92.',
 'INCROPERA7': 'Bergman T.L., Lavine A.S., Incropera F.P., DeWitt D.P., Fundamentals of Heat and Mass Transfer, 7th ed., Wiley (2011): sensible duty Q = m cp dT (ch. 1); LMTD method (sec. 11.3); free convection h about 2-25 W/(m2 K) for gases (table 1.1).',
 'PERRY9': 'Green D.W., Southard M.Z. (eds), Perry\'s Chemical Engineers\' Handbook, 9th ed., McGraw-Hill (2019), sec. 2 physical properties (heat capacity of aqueous HCl and NaOH solutions); sec. 6 fluid transport (line sizing by velocity).',
 'NEC2023': 'NFPA 70, National Electrical Code (2023): 210.20(A)/215.3 continuous load at 125 %; 240.6(A) standard overcurrent device ratings.',
 'IEEE80': 'IEEE Std 80-2013, Guide for Safety in AC Substation Grounding: eq. 29 (step), eq. 32 (touch), Cs eq. 27.',
 'EDBM_PILOT_2023': 'Herrero-Gonzalez M. et al., Electrodialysis with Bipolar Membranes for the Sustainable Production of Chemicals from Seawater Brines at Pilot Plant Scale, ACS Sustainable Chem. Eng. (2023), PMC9945178: SEC 1.4 kWh/kg NaOH at 200 A/m2 (CE 80 %), 1.9-2.6 kWh/kg at 300-500 A/m2.',
 'EDBM_MEMBRANES_2023': 'Analysis of Operational Parameters in Acid and Base Production Using an Electrodialysis with Bipolar Membranes Pilot Plant, Membranes 13(2), 200 (2023), https://www.mdpi.com/2077-0375/13/2/200: SEC 1.02-1.18 kWh/kg, CE 87-99 % at 200 A/m2, single pass.',
 'EDBM_WHEY_2021': 'Transforming salty whey into cleaning chemicals using electrodialysis with bipolar membranes, Desalination (2021), ScienceDirect pii S0011916420312765: maximum 3.6 M acid / 3.0 M base from NaCl; 6.7 kWh/kg to produce 2 M acid or base.',
 'NREL_PVWATTS': 'NREL PVWatts Calculator v8, site run recorded in AQS-SITE-002 (5.41 kWh/kWp/d).',
 'LUNAR_SOURCEBOOK': 'Heiken G.H., Vaniman D.T., French B.M. (eds), Lunar Sourcebook, Cambridge University Press (1991), ch. 7 lunar soil chemistry (major-oxide ranges for mare and highland soils).',
 'ASTM_D1785': 'ASTM D1785-15, Standard Specification for PVC Plastic Pipe, Schedules 40, 80 and 120; maximum service 60 C (140 F).',
 'GREENWOOD': 'Greenwood N.N., Earnshaw A., Chemistry of the Elements, 2nd ed., Butterworth-Heinemann (1997): basic oxides dissolve in HCl to chlorides and water (Al2O3 + 6 HCl, MO + 2 HCl).',
 'ASHRAE_SYS2020': 'ASHRAE Handbook, HVAC Systems and Equipment (2020), ch. 13 hydronic heating and cooling: design temperature difference about 10-11 K (20 F) for chilled/condenser water loops.',
 'WILSON2006': 'Wilson K.C., Addie G.R., Sellgren A., Clift R., Slurry Transport Using Centrifugal Pumps, 3rd ed., Springer (2006): deposition velocity and minimum bore for settling slurries.',
 'DOE_H2_COMP': 'Standard isothermal ideal-gas compression work W = (R T / M) ln(P2/P1), e.g. Perry\'s 9th ed. sec. 10; efficiency to be taken from compressor vendor data.',
}
def cite(k):
    assert k in REFS, f'unknown reference {k}'
    return k

"""Citation registry for the parametric model. Code cites by key; docs print the full entry.
Only published sources: standards, textbooks, peer-reviewed papers, manufacturer data."""
REFS = {
 'IFC2021_5003': 'International Fire Code (2021) 5003.9.8: incompatible materials in storage and use above 5 lb (2.3 kg) or 0.5 gal (2 L) separated by not less than 20 ft (6096 mm), a 1-hour fire barrier, or approved hazardous materials storage cabinets.',
 'NFPA400_2022': 'NFPA 400, Hazardous Materials Code (2022) 6.1.12.1: separation of incompatible materials, same three options as IFC 5003.9.8.',
 'CAMEO_REACT': 'NOAA CAMEO Chemicals reactivity groups: Peroxides, inorganic (H2O2) incompatible with Bases (KOH, NH3 aq) and with Hydrocarbons/solvents; Acids, strong oxidizing (HNO3) incompatible with Bases and Amines; Acids, strong non-oxidizing (HF, H3PO4) incompatible with Bases.',

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
 'USBM_CL_EW': 'U.S. Bureau of Mines, electrowinning of copper from chloride solutions (Report of Investigations), https://stacks.cdc.gov/view/cdc/237351: energy 1.1 kWh/kg from cuprous and 2.1 kWh/kg from cupric chloride electrolyte; current efficiency 85-90 %; diaphragm cell to keep anode Cl2 from the catholyte.',
 'CARLETON_HCL_2023': 'Carleton University thesis, HCl leaching of lunar regolith simulant, doi:10.22215/etd/2023-15477: 38 % HCl, 90-108 C, 4 h, 150 % of stoichiometric acid.',
 'VOGELBUSCH_MVR': 'Vogelbusch Biocommodities, mechanical vapour recompression evaporators, manufacturer data table: specific power 19-72 kWh per t water evaporated, rising with boiling-point elevation and stage count.',
 'EVAPCRYST_MVR': 'EvapCryst / manufacturer application notes on MVR evaporators: 15-25 kWh/t water for low boiling-point elevation, 30-60 kWh/t for high.',
 'PERRY9_HCL': "Perry's Chemical Engineers' Handbook, 9th ed. (2019), sec. 2 and sec. 13: HCl-water maximum-boiling azeotrope 20.2 wt% HCl at 108.6 C, 101.3 kPa; below the azeotrope the vapour is water-rich, so boiling concentrates the liquid toward 20.2 wt%; density of 2 M HCl 1.032 kg/L and of 2 M NaOH 1.081 kg/L at 20 C.",
 'ULLMANN_HCL': "Austin S., Glowacki A., Hydrochloric Acid, Ullmann's Encyclopedia of Industrial Chemistry, Wiley-VCH (2000): impregnated graphite, tantalum and fluoropolymer-lined equipment for hot HCl concentration and absorption.",
  'ROARK8': "Young W.C., Budynas R.G., Sadegh A.M., Roark's Formulas for Stress and Strain, 8th ed., McGraw-Hill (2012): table 11.4 rectangular plates (long plate, uniform load, edges simply supported: sigma = beta q b^2 / t^2, y = alpha q b^4 / (E t^3)); table 8.1 beams (simply supported, uniform load: M = w L^2 / 8, y = 5 w L^4 / (384 E I)).",
 'PERRY9_MIX': "Perry's Chemical Engineers' Handbook, 9th ed. (2019), sec. 18 liquid-solid operations and mixing: turbulent agitator power P = Np rho N^3 D^5; pitched-blade turbine Np about 1.27 (4 blades, 45 deg).",
 'PERRY9_PUMP': "Perry's Chemical Engineers' Handbook, 9th ed. (2019), sec. 10 transport of fluids: pump hydraulic power P = rho g Q H; shaft power = hydraulic / efficiency.",
  'API520': 'API Standard 520 Part I, Sizing, Selection, and Installation of Pressure-relieving Devices, 10th ed. (2020): liquid A = Q/(38 Kd Kw Kc Kv) sqrt(G/(p1-p2)) (US units, eq. 32); gas critical flow A = W/(C K P1 Kb Kc) sqrt(T Z/M) (US units, eq. 3), C = 520 sqrt(k (2/(k+1))^((k+1)/(k-1))).',
  'PERRY9_ABS': "Perry's Chemical Engineers' Handbook, 9th ed. (2019), sec. 14 equipment for gas-liquid operations: packed-column capacity by a flooding velocity u_f = C_s sqrt((rho_L - rho_G)/rho_G) with C_s from the packing correlation or vendor; design at 0.7-0.8 of flood; height Z = HTU x NTU; for absorption with negligible equilibrium back-pressure (fast reaction, m y* ~ 0) NTU = ln(y_in/y_out).",
}
def cite(k):
    assert k in REFS, f'unknown reference {k}'
    return k

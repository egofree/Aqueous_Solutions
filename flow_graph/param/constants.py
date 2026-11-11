"""Physical constants and atomic weights with references."""
from .refs import cite
F = 96485.33212          ; F_ref = cite('CODATA2018')
R = 8.314462618          ; R_ref = cite('CODATA2018')
M = {  # g/mol, CIAAW 2021 abridged standard atomic weights
 'H':1.008,'C':12.011,'O':15.999,'Na':22.990,'Mg':24.305,'Al':26.982,'Si':28.085,'P':30.974,'S':32.06,'Cl':35.45,
 'K':39.098,'Ca':40.078,'Ti':47.867,'Cr':51.996,'Mn':54.938,'Fe':55.845,'Ni':58.693,'Cu':63.546,'Zn':65.38,
 'Mo':95.95,'Ag':107.87,'Cd':112.41,'Sn':118.71,'Au':196.97,'Pb':207.2}
M_ref = cite('CIAAW2021')
CP_WATER = 4.18            # kJ/(kg K) liquid water near ambient (CRC_SI)
CP_WATER_ref = cite('CRC_SI')
def mw(formula):
    """Molar mass from a simple formula dict, e.g. {'Al':2,'O':3}."""
    return sum(M[k]*n for k,n in formula.items())

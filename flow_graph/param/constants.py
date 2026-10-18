"""Physical constants and atomic weights with references."""
from .refs import cite
F = 96485.33212          ; F_ref = cite('CODATA2018')
R = 8.314462618          ; R_ref = cite('CODATA2018')
M = {  # g/mol, CIAAW 2021 abridged standard atomic weights
 'H':1.008,'O':15.999,'Na':22.990,'Mg':24.305,'Al':26.982,'Si':28.085,'Cl':35.45,'Ca':40.078,'Ti':47.867,'Fe':55.845,
 'Ni':58.693,'Cu':63.546,'Zn':65.38,'Ag':107.87,'Cd':112.41,'Sn':118.71,'Au':196.97,'Pb':207.2}
M_ref = cite('CIAAW2021')
def mw(formula):
    """Molar mass from a simple formula dict, e.g. {'Al':2,'O':3}."""
    return sum(M[k]*n for k,n in formula.items())

"""HCl-water vapour-liquid equilibrium from the published partial-pressure tables [PERRY7_HCL_VLE]:
Perry's 7th ed. Table 2-9 (H2O over aqueous HCl) and Table 2-10 (HCl over aqueous HCl), log10 p[mmHg] = A - B/T[K] per wt% row,
interpolated linearly in log p between rows. The table notes give 2 % accuracy for 15-30 wt% HCl (0-100 C), 5-20 % below 15 wt%.
The fits put the 101.3 kPa azeotrope boiling point about 1.6 K low (107.0 C vs 108.6 C measured at 20.2 wt%) [PERRY9_HCL]; compositions are used, temperatures are taken from PERRY9_HCL."""
import math
from ..refs import cite
REF = (cite('PERRY7_HCL_VLE'),)
W = {6:(8.99156,2282),10:(8.99864,2295),14:(8.97075,2300),18:(8.98014,2323),20:(8.97877,2334),22:(9.02708,2363),24:(8.96022,2356)}
H = {2:(11.8037,4736),4:(11.6400,4471),6:(11.2144,4202),8:(11.0406,4042),10:(10.9311,3908),12:(10.7900,3765),14:(10.6954,3636),
     16:(10.6261,3516),18:(10.4957,3376),20:(10.3833,3245),22:(10.3172,3125),24:(10.2185,2995)}
MH, MW = 36.461, 18.015
def _lp(tab, w, T):
    ks = sorted(tab)
    if w <= ks[0]: a, b = tab[ks[0]]; return a - b/T
    for i in range(len(ks)-1):
        if ks[i] <= w <= ks[i+1]:
            f = (w-ks[i])/(ks[i+1]-ks[i]); l1 = tab[ks[i]][0]-tab[ks[i]][1]/T; l2 = tab[ks[i+1]][0]-tab[ks[i+1]][1]/T; return l1 + f*(l2-l1)
    a, b = tab[ks[-1]]; return a - b/T
def bubble(w_pct, P_mmHg=760.0):
    """Liquid wt% HCl -> (T_C, vapour wt% HCl) at P."""
    lo, hi = 330.0, 420.0
    for _ in range(80):
        T = (lo+hi)/2; s = 10**_lp(W, w_pct, T) + 10**_lp(H, w_pct, T)
        lo, hi = (T, hi) if s < P_mmHg else (lo, T)
    ph = 10**_lp(H, w_pct, T); pw = 10**_lp(W, w_pct, T); y = ph/(ph+pw)
    return T-273.15, 100*y*MH/(y*MH+(1-y)*MW)
def x_from_y(y_pct):
    lo, hi = 0.0, 20.0
    for _ in range(80):
        m = (lo+hi)/2
        lo, hi = (m, hi) if bubble(m)[1] < y_pct else (lo, m)
    return (lo+hi)/2
def strip_stages(F, xF, B, xB, V, yTop, nmax=60):
    """Counter-current column above the MVR body: feed liquid F (kg/s, wt% xF) enters the top, product B (xB) leaves the body,
    vapour V (yTop wt% at the top) goes to the blower. Stage-by-stage from the top on a mass basis (equimass overflow, study):
    x_n from equilibrium with y_n; y_{n+1} = (L x_n - B xB)/V. Returns ideal stages to reach xB."""
    L = F; y = yTop; n = 0
    while n < nmax:
        n += 1; x = x_from_y(y)
        if x >= xB: return n
        y = (L*x - B*xB)/V
        if y <= 0: return n
    return None

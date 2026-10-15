"""Mechanical-vapour-recompression falling-film evaporator, in-house design (X-MFG-30).
Saturation pressure of water: IAPWS-IF97 region 4 [IAPWS_IF97]. Latent heat at the body [IAPWS_IF97].
Compressor: ideal-gas isentropic work w = k/(k-1) R T1 ((p2/p1)^((k-1)/k) - 1), shaft = w / eta [PERRY9_PUMP].
Falling-film area A = Q / (U dT) [PERRY9_EVAP]. Feed/condensate/product interchanger: counter-current energy balance and LMTD [INCROPERA7].
Fire relief: Q = 21000 F A_w^0.82 Btu/h (adequate drainage and fire fighting) [ISO23251]; relieving vapour W = Q / latent; area per API 520 Part I [API520]."""
import math
from ..refs import cite
REF = tuple(cite(k) for k in ('IAPWS_IF97','PERRY9_PUMP','PERRY9_EVAP','INCROPERA7','ISO23251','API520'))
_n = [0.11670521452767e4, -0.72421316703206e6, -0.17073846940092e2, 0.12020824702470e5, -0.32325550322333e7,
      0.14915108613530e2, -0.48232657361591e4, 0.40511340542057e6, -0.23855557567849, 0.65017534844798e3]
def psat_kPa(T_C):
    T = T_C + 273.15; th = T + _n[8]/(T - _n[9])
    A = th*th + _n[0]*th + _n[1]; B = _n[2]*th*th + _n[3]*th + _n[4]; C = _n[5]*th*th + _n[6]*th + _n[7]
    return (2*C/(-B + math.sqrt(B*B - 4*A*C)))**4*1000
def tsat_C(p_kPa):
    lo, hi = 0.0, 370.0
    for _ in range(80):
        m = (lo+hi)/2
        lo, hi = (m, hi) if psat_kPa(m) < p_kPa else (lo, m)
    return (lo+hi)/2
def compressor_kW(m_kg_s, T1_C, p1_kPa, p2_kPa, k, eta, R=461.5):
    w = k/(k-1)*R*(T1_C+273.15)*((p2_kPa/p1_kPa)**((k-1)/k) - 1)
    return m_kg_s*w/eta/1000, w/1000
def interchanger(F, cpF, TF, V, cpV, TV, P, cpP, TP, approach):
    """Feed F (kg/s) heated by condensate V at TV and product P at TP. Hot outlets set to TF + approach (cold end);
    feed outlet from the energy balance, capped so the hot-end approach also holds."""
    To = TF + approach
    Q = V*cpV*(TV - To) + P*cpP*(TP - To)
    TFo = TF + Q/(F*cpF); cap = min(TV, TP) - approach
    if TFo > cap:
        TFo = cap; Q = F*cpF*(TFo - TF)
        # hot outlets rise equally so the balance still holds
        To = (V*cpV*TV + P*cpP*TP - Q)/(V*cpV + P*cpP)
    lm = ((min(TV, TP) - TFo) - (To - TF))/math.log((min(TV, TP) - TFo)/(To - TF)) if abs((min(TV, TP) - TFo) - (To - TF)) > 1e-9 else (To - TF)
    return dict(Q_kW=Q, T_feed_out_C=TFo, T_hot_out_C=To, LMTD_K=lm)
def fire_relief_kg_h(A_w_m2, latent_kJ_kg, F=1.0):
    Q_btu_h = 21000*F*(A_w_m2*10.7639)**0.82
    return Q_btu_h*0.29307107/1000*3600/latent_kJ_kg, Q_btu_h*0.29307107/1000

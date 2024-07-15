import math

cp = 1.006
cw = 1.86
L = 2501
p = 1013.25
T = 25
RH = 0.2

def saturaion_pressure(T: int) -> float:
    return 6.112 * math.exp(17.67 * T / (T + 243.5))

def calculate_enthalpy(T, RH, cp, cw, L, p) -> float:
    e_s = saturaion_pressure(T)
    w = 0.622 * (e_s * RH) / (p - e_s)
    h = cp * T + w + (cw * T + L)
    return h
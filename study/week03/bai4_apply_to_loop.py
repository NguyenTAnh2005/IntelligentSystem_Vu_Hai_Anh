import matplotlib.pyplot as plt
import numpy as np

def trimf(x, a, b, c):
    return np.maximum(np.minimum((x - a) / (b - a + 1e-6), (c - x) / (c - b + 1e-6)), 0)

x_AC = np.linspace(0, 100, 300)

def fuzzify_T_in(T_in):
    return {"cold": trimf(T_in, 20, 22, 25), "comfort": trimf(T_in, 24, 26, 28), "hot": trimf(T_in, 27, 30, 35)}

def fuzzy_rules(T_in):
    mu = fuzzify_T_in(T_in)
    return {"low": mu["cold"], "med": mu["comfort"], "high": mu["hot"]}

def defuzzify_AC(T_in):
    rules = fuzzy_rules(T_in)
    mu_ac_low, mu_ac_med, mu_ac_high = trimf(x_AC, 0, 0, 40), trimf(x_AC, 20, 50, 80), trimf(x_AC, 60, 100, 100)
    aggregated = np.maximum(np.minimum(rules["low"], mu_ac_low), 
                            np.maximum(np.minimum(rules["med"], mu_ac_med), 
                                       np.minimum(rules["high"], mu_ac_high)))
    return float(np.sum(aggregated * x_AC) / np.sum(aggregated)) if aggregated.sum() > 0 else 0.0

# Mô phỏng
T_in, T_out, occ_level = 29.0, 32.0, 2
T_in_list, ac_list = [], []

for step in range(60):
    if step < 20: occ_level = 2
    elif step < 40: occ_level = 1
    else: occ_level = 0
    
    ac_power = defuzzify_AC(T_in)
    dT = -0.15 if ac_power >= 70 else (-0.08 if ac_power >= 40 else -0.02)
    if T_out >= 31: dT += 0.10
    dT += (0.08 if occ_level == 2 else (0.04 if occ_level == 1 else 0))
    
    T_in = np.clip(T_in + dT, 20, 35)
    T_in_list.append(T_in)
    ac_list.append(ac_power)

# Vẽ đồ thị kết quả
plt.figure(figsize=(10, 6))
plt.subplot(2, 1, 1)
plt.plot(T_in_list, label="T_in (°C)", color='r')
plt.title("Mô phỏng T_in với fuzzy controller")
plt.ylabel("T_in")
plt.legend()

plt.subplot(2, 1, 2)
plt.step(range(len(ac_list)), ac_list, where="post", color='b')
plt.title("Công suất AC (fuzzy)")
plt.ylabel("AC power (%)")
plt.xlabel("Step")
plt.tight_layout()
plt.show()
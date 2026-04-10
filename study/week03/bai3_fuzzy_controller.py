import numpy as np

def trimf(x, a, b, c):
    return np.maximum(np.minimum((x - a) / (b - a + 1e-6), (c - x) / (c - b + 1e-6)), 0)

x_AC = np.linspace(0, 100, 300)

def fuzzify_T_in(T_in):
    mu_cold = trimf(T_in, 20, 22, 25)
    mu_comfort = trimf(T_in, 24, 26, 28)
    mu_hot = trimf(T_in, 27, 30, 35)
    return {"cold": float(mu_cold), "comfort": float(mu_comfort), "hot": float(mu_hot)}

def fuzzy_rules(T_in):
    mu = fuzzify_T_in(T_in)
    # Luật: Lạnh -> AC Thấp; Dễ chịu -> AC Vừa; Nóng -> AC Cao
    return {"low": mu["cold"], "med": mu["comfort"], "high": mu["hot"]}

def defuzzify_AC(T_in):
    rules = fuzzy_rules(T_in)
    mu_ac_low = trimf(x_AC, 0, 0, 40)
    mu_ac_med = trimf(x_AC, 20, 50, 80)
    mu_ac_high = trimf(x_AC, 60, 100, 100)
    
    # Kết hợp các luật (Aggregation)
    aggregated = np.zeros_like(x_AC)
    aggregated = np.maximum(aggregated, np.minimum(rules["low"], mu_ac_low))
    aggregated = np.maximum(aggregated, np.minimum(rules["med"], mu_ac_med))
    aggregated = np.maximum(aggregated, np.minimum(rules["high"], mu_ac_high))
    
    # Giải mờ trọng tâm
    if aggregated.sum() == 0:
        ac_crisp = 0.0
    else:
        ac_crisp = float(np.sum(aggregated * x_AC) / np.sum(aggregated))
    return ac_crisp, aggregated

if __name__ == "__main__":
    test_T = [22, 25, 29, 32]
    for T in test_T:
        ac, _ = defuzzify_AC(T)
        print(f"T_in = {T}°C -> AC fuzzy ~ {ac:.2f} %")
import numpy as np
import matplotlib.pyplot as plt

def trimf(x, a, b, c):
    return np.maximum(np.minimum((x - a) / (b - a + 1e-6), (c - x) / (c - b + 1e-6)), 0)

# 1. Tập mờ cho công suất AC (%)
x_AC = np.linspace(0, 100, 300)
mu_ac_low = trimf(x_AC, 0, 0, 40)      # Thấp
mu_ac_med = trimf(x_AC, 20, 50, 80)    # Trung bình
mu_ac_high = trimf(x_AC, 60, 100, 100) # Cao

plt.figure(figsize=(8, 4))
plt.plot(x_AC, mu_ac_low, label="AC Thấp")
plt.plot(x_AC, mu_ac_med, label="AC Vừa")
plt.plot(x_AC, mu_ac_high, label="AC Cao")
plt.title("Tập mờ cho công suất AC (%)")
plt.xlabel("AC power (%)")
plt.ylabel("Mức thuộc")
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()

# 2. BONUS: Tập mờ cho 'Mức thoải mái' (Comfort)
x_comfort = np.linspace(0, 10, 300)
mu_uncomfortable = trimf(x_comfort, 0, 0, 4)
mu_normal = trimf(x_comfort, 3, 5, 7)
mu_very_comfort = trimf(x_comfort, 6, 10, 10)

plt.figure(figsize=(8, 4))
plt.plot(x_comfort, mu_uncomfortable, label="Khó chịu")
plt.plot(x_comfort, mu_normal, label="Bình thường")
plt.plot(x_comfort, mu_very_comfort, label="Rất dễ chịu")
plt.title("Tập mờ cho Comfort")
plt.xlabel("Comfort score")
plt.ylabel("Mức thuộc")
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
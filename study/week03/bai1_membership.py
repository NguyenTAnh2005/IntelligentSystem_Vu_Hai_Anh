import numpy as np
import matplotlib.pyplot as plt

# Hàm thuộc hình tam giác
def trimf(x, a, b, c):
    return np.maximum(np.minimum((x - a) / (b - a + 1e-6), (c - x) / (c - b + 1e-6)), 0)

# Miền giá trị nhiệt độ trong phòng từ 20 đến 35 độ C
x_T = np.linspace(20, 35, 300)

# ĐỊNH NGHĨA TẬP MỜ CHO Tin (Có thể thay đổi tham số theo yêu cầu 3.3)
mu_cold = trimf(x_T, 20, 22, 25)      # LẠNH: [20-22-25]
mu_comfort = trimf(x_T, 24, 26, 28)   # DỄ CHỊU: [24-26-28]
mu_hot = trimf(x_T, 27, 30, 35)       # NÓNG: [27-30-35]

plt.figure(figsize=(8, 4))
plt.plot(x_T, mu_cold, label="Lạnh")
plt.plot(x_T, mu_comfort, label="Dễ chịu")
plt.plot(x_T, mu_hot, label="Nóng")

plt.title("Tập mờ cho T_in (°C)")
plt.xlabel("T_in (°C)")
plt.ylabel("Mức thuộc")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
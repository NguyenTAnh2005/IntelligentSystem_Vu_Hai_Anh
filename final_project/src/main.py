import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

# =================================================================
# BƯỚC 1: KHỞI TẠO 2 INPUT VÀ 1 OUTPUT
# =================================================================
# Input 1: Khoảng cách (từ 0m đến 50m)
khoang_cach = ctrl.Antecedent(np.arange(0, 51, 1), 'khoang_cach')

# Input 2: Kích thước động vật (từ 0 đến 100 - tỷ lệ kích thước)
kich_thuoc = ctrl.Antecedent(np.arange(0, 101, 1), 'kich_thuoc')

# Output: Mức độ nguy hiểm (từ 1 đến 10)
nguy_hiem = ctrl.Consequent(np.arange(1, 10.1, 0.1), 'nguy_hiem')

# =================================================================
# BƯỚC 2: MỜ HÓA (FUZZIFICATION) - Định nghĩa hàm thuộc (Hình thang/Tam giác)
# =================================================================
# 1. Hàm cho Khoảng cách
khoang_cach['gan'] = fuzz.trapmf(khoang_cach.universe, [0, 0, 5, 12])  # Gần: Hình thang
khoang_cach['xa']  = fuzz.trapmf(khoang_cach.universe, [8, 15, 50, 50]) # Xa: Hình thang

# 2. Hàm cho Kích thước
kich_thuoc['nho'] = fuzz.trimf(kich_thuoc.universe, [0, 0, 60])     # Nhỏ: Tam giác
kich_thuoc['to']  = fuzz.trimf(kich_thuoc.universe, [40, 100, 100]) # To: Tam giác

# 3. Hàm cho Mức độ nguy hiểm
nguy_hiem['thap'] = fuzz.trimf(nguy_hiem.universe, [1, 1, 6])
nguy_hiem['cao']  = fuzz.trimf(nguy_hiem.universe, [4, 10, 10])

# =================================================================
# BƯỚC 3: LUẬT MỜ (FUZZY RULES) - Kết hợp 2 Input
# =================================================================
# LUẬT 1: NẾU Khoảng cách GẦN (AND) Kích thước TO -> Nguy hiểm CAO
rule1 = ctrl.Rule(khoang_cach['gan'] & kich_thuoc['to'], nguy_hiem['cao'])

# LUẬT 2: NẾU Khoảng cách XA (OR) Kích thước NHỎ -> Nguy hiểm THẤP
rule2 = ctrl.Rule(khoang_cach['xa'] | kich_thuoc['nho'], nguy_hiem['thap'])

# Nạp luật vào hệ thống
he_thong = ctrl.ControlSystem([rule1, rule2])
mo_phong = ctrl.ControlSystemSimulation(he_thong)

# =================================================================
# BƯỚC 4: TÍNH TOÁN & GIẢI MỜ BẰNG TRỌNG TÂM (CENTROID)
# =================================================================
# Đưa giá trị thực tế vào (Ví dụ: Vật cách 7m và kích thước khá to là 75)
mo_phong.input['khoang_cach'] = 7
mo_phong.input['kich_thuoc'] = 75

# Chạy tính toán
mo_phong.compute()

print(f"Mức độ nguy hiểm tính được: {mo_phong.output['nguy_hiem']:.2f} / 10")

# =================================================================
# BƯỚC 5: VẼ ĐỒ THỊ TRỰC QUAN (GIỐNG ẢNH BẠN GỬI)
# =================================================================
# Lệnh này sẽ tự động vẽ đồ thị giải mờ Centroid
nguy_hiem.view(sim=mo_phong)

# Hiển thị cửa sổ đồ thị
plt.show()
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt
# -----------------------------------------------------
# ****Nhớ nhân input phải nhan hệ số 10 ví 0.5m cảm biến sẽ là 0.5 * 10 = 5m thực tế ***
# -----------------------------------------------------
# =============================================================================
# BƯỚC 1: KHỞI TẠO KHÔNG GIAN BIẾN (UNIVERSE)
# =============================================================================
# Input 1: Khoảng cách thực tế (Dreal = Dđo được * 10). Tầm xa max cảm biến là 4m -> 40m thực tế.
khoang_cach = ctrl.Antecedent(np.arange(0, 41, 1), 'khoang_cach')

# Input 2: Độ hung dữ do AI nhận diện và trả về thang điểm từ 1 đến 10.
hung_du = ctrl.Antecedent(np.arange(1, 11, 1), 'hung_du')

# Output: Mức độ báo động tính theo % (0-100). Con số này dùng để gửi MQTT điều khiển còi/đèn.
bao_dong = ctrl.Consequent(np.arange(0, 101, 1), 'bao_dong')

# =============================================================================
# BƯỚC 2: ĐỊNH NGHĨA HÀM THUỘC (MEMBERSHIP FUNCTIONS) - Cấu trúc Thang-Tam-Thang
# =============================================================================

# --- Input: Khoảng cách ---
# Gần: Hình thang [0,0,7,15]. Từ 0-7m là chắc chắn GẦN (100%), sau đó giảm dần đến 15m.
khoang_cach['gan'] = fuzz.trapmf(khoang_cach.universe, [0, 0, 7, 15])
# Vừa: Hình tam giác đỉnh tại 20m. Giúp chuyển tiếp mượt mà giữa Gần và Xa.
khoang_cach['vua'] = fuzz.trimf(khoang_cach.universe, [10, 20, 30])
# Xa: Hình thang. Từ 30m đến 40m (giới hạn cảm biến) luôn được coi là XA (An toàn tuyệt đối).
khoang_cach['xa']  = fuzz.trapmf(khoang_cach.universe, [25, 30, 40, 40])

# --- Input: Độ hung dữ (AI) ---
# Hiền: Hình thang. Từ 1-3 điểm là chắc chắn HIỀN, giảm dần sự tin tưởng khi tiến tới 5 điểm.
hung_du['hien'] = fuzz.trapmf(hung_du.universe, [1, 1, 3, 5])
# Vừa: Tam giác đỉnh 5.5. Vùng đệm để hệ thống không bị nhảy trạng thái đột ngột.
hung_du['vua']  = fuzz.trimf(hung_du.universe, [3, 5.5, 8])
# Dữ: Hình thang. Từ 8-10 điểm là cực kỳ nguy hiểm, độ thuộc tập DỮ luôn là 1.
hung_du['du']   = fuzz.trapmf(hung_du.universe, [6, 8, 10, 10])

# --- Output: Mức độ báo động (0-100%) ---
# Các tập đầu ra gối đầu lên nhau 50% (Overlap) để khi giải mờ Centroid ra số lẻ cực mịn.
bao_dong['AN_TOAN'] = fuzz.trimf(bao_dong.universe, [0, 0, 25])
bao_dong['VANG']    = fuzz.trimf(bao_dong.universe, [0, 25, 50])
bao_dong['DO']      = fuzz.trimf(bao_dong.universe, [25, 50, 75])
bao_dong['TU_THAN'] = fuzz.trimf(bao_dong.universe, [50, 100, 100])

# =============================================================================
# BƯỚC 3: HỆ LUẬT MỜ (9 LUẬT MAMDANI) - Giai đoạn Diễn dịch (Inference)
# =============================================================================
# Mỗi luật sử dụng toán tử AND (phép MIN) để cắt ngọn các hình tam giác Output.
rules = [
    ctrl.Rule(khoang_cach['gan'] & hung_du['hien'], bao_dong['VANG']),
    ctrl.Rule(khoang_cach['gan'] & hung_du['vua'],  bao_dong['DO']),
    ctrl.Rule(khoang_cach['gan'] & hung_du['du'],   bao_dong['TU_THAN']),
    
    ctrl.Rule(khoang_cach['vua'] & hung_du['hien'], bao_dong['VANG']),
    ctrl.Rule(khoang_cach['vua'] & hung_du['vua'],  bao_dong['DO']),
    ctrl.Rule(khoang_cach['vua'] & hung_du['du'],   bao_dong['DO']),
    
    ctrl.Rule(khoang_cach['xa'] & hung_du['hien'],  bao_dong['AN_TOAN']),
    ctrl.Rule(khoang_cach['xa'] & hung_du['vua'],  bao_dong['AN_TOAN']),
    ctrl.Rule(khoang_cach['xa'] & hung_du['du'],   bao_dong['VANG'])
]

# Nạp luật vào hệ thống và khởi tạo trình mô phỏng
he_thong_ctrl = ctrl.ControlSystem(rules)
mo_phong = ctrl.ControlSystemSimulation(he_thong_ctrl)

# =============================================================================
# BƯỚC 4: TÍNH TOÁN (AGGREGATION) VÀ GIẢI MỜ (DEFUZZIFICATION)
# =============================================================================
# Giả sử giá trị truyền vào từ cảm biến và AI:
khoang_cach_do = 1.2 # mét
do_du_ai = 7.5       # điểm hung dữ

# 1. Mờ hóa: Đưa giá trị thực vào hệ thống (nhân 10 cho khoảng cách)
mo_phong.input['khoang_cach'] = khoang_cach_do * 10
mo_phong.input['hung_du'] = do_du_ai

# 2. Thực hiện tính toán (Máy tính tự thực hiện toán tử MAX để tổng hợp các tập mờ)
mo_phong.compute()

# 3. Lấy kết quả giải mờ Centroid (Trọng tâm của đa giác tổng hợp)
ket_qua_percent = mo_phong.output['bao_dong']

print("=" * 40)
print(f"KẾT QUẢ PHÂN TÍCH LOGIC MỜ")
print(f"-> Khoảng cách thực tế: {khoang_cach_do * 10}m")
print(f"-> Độ hung dữ AI: {do_du_ai}/10")
print(f"-> Mức báo động đầu ra: {ket_qua_percent:.2f}%")
print("=" * 40)

# =============================================================================
# BƯỚC 5: TRỰC QUAN HÓA (Vẽ đồ thị giải thích giống ảnh mẫu)
# =============================================================================
# Vẽ đồ thị Output để thấy phần diện tích màu tím (Aggregation) và đường đỏ (Centroid)
bao_dong.view(sim=mo_phong)

plt.title("Giải mờ Trọng tâm (Centroid Defuzzification)")
plt.show()
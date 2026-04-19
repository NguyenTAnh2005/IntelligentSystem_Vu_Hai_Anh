import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


# =============================================================================
# BƯỚC 1: KHỞI TẠO KHÔNG GIAN BIẾN (UNIVERSE)
# =============================================================================
khoang_cach = ctrl.Antecedent(np.arange(0, 41, 1), 'khoang_cach')
hung_du = ctrl.Antecedent(np.arange(1, 11, 1), 'hung_du')
bao_dong = ctrl.Consequent(np.arange(0, 101, 1), 'bao_dong')

# =============================================================================
# BƯỚC 2: ĐỊNH NGHĨA HÀM THUỘC (MEMBERSHIP FUNCTIONS) - Cấu trúc Thang-Tam-Thang
# =============================================================================
khoang_cach['gan'] = fuzz.trapmf(khoang_cach.universe, [0, 0, 7, 15])
khoang_cach['vua'] = fuzz.trimf(khoang_cach.universe, [10, 20, 30])
khoang_cach['xa']  = fuzz.trapmf(khoang_cach.universe, [25, 30, 40, 40])

hung_du['hien'] = fuzz.trapmf(hung_du.universe, [1, 1, 3, 5])
hung_du['vua']  = fuzz.trimf(hung_du.universe, [3, 5.5, 8])
hung_du['du']   = fuzz.trapmf(hung_du.universe, [6, 8, 10, 10])

bao_dong['AN_TOAN'] = fuzz.trimf(bao_dong.universe, [0, 0, 25])
bao_dong['VANG']    = fuzz.trimf(bao_dong.universe, [0, 25, 50])
bao_dong['DO']      = fuzz.trimf(bao_dong.universe, [25, 50, 75])
bao_dong['TU_THAN'] = fuzz.trimf(bao_dong.universe, [50, 100, 100]) 


# =============================================================================
# BƯỚC 3: HỆ LUẬT MỜ (9 LUẬT MAMDANI) - Giai đoạn Diễn dịch (Inference)
# =============================================================================
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

# Hàm tính luật logic mờ: 
# distance: Khoảng cách, aggression: ĐỘ hung dữ 
def cal_level_of_danger(distance, aggression):
    # 1. Mờ hóa: Đưa giá trị thực vào hệ thống (nhân 10 cho khoảng cách)
    mo_phong.input['khoang_cach'] = distance * 10
    mo_phong.input['hung_du'] = aggression

    # 2. Thực hiện tính toán (Máy tính tự thực hiện toán tử MAX để tổng hợp các tập mờ)
    mo_phong.compute()

    # 3. Lấy kết quả giải mờ Centroid (Trọng tâm của đa giác tổng hợp)
    ket_qua_percent = mo_phong.output['bao_dong']

    print("=" * 40)
    print(f"KẾT QUẢ PHÂN TÍCH LOGIC MỜ")
    print(f"-> Khoảng cách thực tế: {distance * 10}m")
    print(f"-> Độ hung dữ AI: {aggression}/10")
    print(f"-> Mức báo động đầu ra: {ket_qua_percent:.2f}%")
    print("=" * 40)


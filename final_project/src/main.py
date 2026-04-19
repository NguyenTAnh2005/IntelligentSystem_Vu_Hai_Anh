import pandas as pd 
import time
import cv2
from pathlib import Path

# Import các vũ khí hạng nặng từ các file khác của sếp
from fuzy.rule import cal_level_of_danger
from comms.mqtt_client import connect_mqtt, gui_canh_bao, set_khoang_cach_callback
from ai.vision import nhan_dien_yolo 

# =============================================================================
# 1. BIẾN TOÀN CỤC & HÀM HỨNG DATA NGẦM
# =============================================================================
# Mặc định để 100cm (Khoảng cách an toàn). Rớt mạng cảm biến thì còi cũng không ré lên bậy bạ.
current_distance = 100 

def cap_nhat_khoang_cach(new_distance):
    global current_distance
    current_distance = new_distance
    # Print ngầm để debug, thấy ồn quá sếp có thể comment lại
    # print(f"\r📏 [ESP32] Khoảng cách: {current_distance} cm   ", end="")

# =============================================================================
# KHỞI ĐỘNG HỆ THỐNG
# =============================================================================
print("🚀 ĐANG KHỞI ĐỘNG HỆ THỐNG.....")

# 2. Tải Dataset chứa mức độ hung dữ
try:
    # ⚠️ CHÚ Ý 1: Đảm bảo đường dẫn này trỏ đúng vào file csv của sếp
    current_file = Path(__file__).resolve()
    ROOT_DIR = current_file.parent.parent
    csv_path = ROOT_DIR/"data"/"data_animals.csv"
    df = pd.read_csv(csv_path)

    print("\n✅ Đã nạp xong Dataset!")
except Exception as e:
    print(f"\n❌ Lỗi đọc file CSV: {e}")
    exit()

# 3. Kích hoạt mạng MQTT
set_khoang_cach_callback(cap_nhat_khoang_cach)
connect_mqtt()
time.sleep(1) # Chờ 1 giây cho mạng thông suốt

# 4. Kích hoạt Camera
# ⚠️ CHÚ Ý 2: Sếp nhớ đổi lại cái IP này theo đúng IP trên điện thoại nhé!
URL_CAM = "http://192.168.1.15:8080/video" 
cap = cv2.VideoCapture(URL_CAM)

if not cap.isOpened():
    print("❌ Không kết nối được Camera điện thoại!")
    exit()

print("🔥 HỆ THỐNG ĐÃ SẴN SÀNG! (Nhấn 'q' trên cửa sổ Camera để thoát)")

# =============================================================================
# VÒNG LẶP CHÍNH (CHẠY LIÊN TỤC 30 FPS)
# =============================================================================
try: 
    while True:
        # Bốc 1 tấm ảnh từ luồng Video
        ret, frame = cap.read()
        if not ret:
            print("❌ Mất tín hiệu Camera!")
            break

        # BƯỚC A: Đẩy ảnh cho AI quét
        ten_loai, do_tin_cay, frame_da_ve = nhan_dien_yolo(frame)

        # ---------------------------------------------------------
        # KHỞI TẠO BIẾN MẶC ĐỊNH (KHI KHÔNG CÓ THÚ)
        # ---------------------------------------------------------
        ten_hien_thi = "An toan"
        nguy_hiem_hien_thi = 0.0

        if ten_loai: 
            # BƯỚC B: Quét file CSV lấy độ hung dữ của con vật
            thong_tin = df[df['Ten_Loai'].str.lower() == ten_loai.lower()]
            
            if not thong_tin.empty:
                muc_hung_du = thong_tin.iloc[0]['Muc_Hung_Du']
                
                # BƯỚC C: Tính % nguy hiểm bằng Logic Mờ
                phan_tram_nguy_hiem = cal_level_of_danger(current_distance, muc_hung_du)
                
                # BƯỚC D: Bắn lệnh xuống MQTT cho ESP32
                gui_canh_bao(phan_tram_nguy_hiem)
                
                print(f"\r🚨 [PHÁT HIỆN]: {ten_loai.upper()} | Hung dữ: {muc_hung_du} | Cách: {current_distance:.2f}m -> BÁO ĐỘNG: {phan_tram_nguy_hiem}%", end="")
                
                # CẬP NHẬT LẠI BIẾN HIỂN THỊ VÌ CÓ THÚ
                ten_hien_thi = ten_loai.upper()
                nguy_hiem_hien_thi = phan_tram_nguy_hiem
        else:
            # Nếu không thấy thú, báo ESP32 tắt còi (Nguy hiểm = 0)
            gui_canh_bao(0)

        # ---------------------------------------------------------
        # BƯỚC E: VẼ KHUNG THÔNG SỐ CỨNG LÊN MÀN HÌNH (LUÔN LUÔN HIỆN)
        # ---------------------------------------------------------
        # Dòng 1: Đối tượng (Màu Vàng)
        cv2.putText(frame_da_ve, f"Doi tuong: {ten_hien_thi}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)

        # Dòng 2: Khoảng cách (Màu Xanh lơ)
        cv2.putText(frame_da_ve, f"Khoang cach: {current_distance:.2f} m", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 0), 2)

        # Dòng 3: Mức cảnh báo (Màu Đỏ)
        cv2.putText(frame_da_ve, f"Muc canh bao: {nguy_hiem_hien_thi:.2f}%", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

        # Chiếu bức ảnh lên màn hình
        cv2.imshow("He Thong Giam Sat - Nhom 3", frame_da_ve)

        # Phanh khẩn cấp
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    pass
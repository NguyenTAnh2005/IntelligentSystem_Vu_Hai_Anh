import cv2
from ultralytics import YOLO
from pathlib import Path


# =============================================================================
# 1. LOAD MODEL (Chỉ load 1 lần khi import file để chống giật lag)
# =============================================================================
try:
    current_file = Path(__file__).resolve()
    ROOT_DIR = current_file.parent.parent.parent
    MODEL_PATH = ROOT_DIR/"models"/ "yolov8.pt"
    model = YOLO(MODEL_PATH)
except Exception as e:
    print(f"❌ LỖI KHỞI TẠO AI: Không tìm thấy file model. Chi tiết: {e}")
    model = None

# =============================================================================
# 2. HÀM XỬ LÝ CHÍNH (Dành cho main_system.py gọi)
# =============================================================================
def nhan_dien_yolo(frame):
    """
    Quét qua khung hình, nhận diện động vật.
    Trả về: Tên loài (str), Độ tin cậy (float), Khung hình đã vẽ Box (numpy array)
    """
    if model is None:
        return None, 0, frame

    # Đưa frame vào mô hình YOLO, verbose=False để Terminal không bị rác chữ
    results = model(frame, verbose=False) 

    ten_loai_chinh = None
    do_tin_cay_max = 0
    frame_ket_qua = frame.copy()

    # Bóc tách kết quả
    for r in results:
        # YOLOv8 hỗ trợ hàm plot() để tự động vẽ Bounding Box cực đẹp
        frame_ket_qua = r.plot()
        
        boxes = r.boxes
        for box in boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            ten_loai = model.names[cls_id]

            # Nếu có nhiều vật, tạm thời chỉ lấy con có độ tin cậy cao nhất để cảnh báo
            if conf > do_tin_cay_max:
                do_tin_cay_max = conf
                ten_loai_chinh = ten_loai

    return ten_loai_chinh, do_tin_cay_max, frame_ket_qua


# =============================================================================
# 3. PHẦN TEST ĐỘC LẬP (Chỉ chạy khi test trực tiếp file này)
# =============================================================================
if __name__ == "__main__":
    print("🚀 ĐANG KHỞI ĐỘNG BỘ TEST MẮT THẦN (IP WEBCAM)...")
    
    # ⚠️ IP TRÊN ĐIỆN THOẠI 
    URL_CAM = "http://192.168.211.188:8080/video"
    
    # Kết nối Camera
    cap = cv2.VideoCapture(URL_CAM)

    if not cap.isOpened():
        print("❌ LỖI: Không nối được IP Camera! Vui lòng check lại WiFi hoặc Link IP.")
        exit()

    print("✅ Kết nối thành công! (Nhấn 'q' để tắt)")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Bị rớt mạng, mất luồng video!")
            break

        # Đẩy frame vào hàm AI
        ten_con_vat, do_tin_cay, frame_da_ve = nhan_dien_yolo(frame)

        if ten_con_vat:
            print(f"🚨 Phát hiện: {ten_con_vat.upper()} - Tỉ lệ chính xác: {do_tin_cay*100:.1f}%")

        # Show hình ảnh có Bounding Box
        cv2.imshow("TEST VISION - NHOM 3", frame_da_ve)

        # Bấm chữ 'q' trên bàn phím để thoát
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
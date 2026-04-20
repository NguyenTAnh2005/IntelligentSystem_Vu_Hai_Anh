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
    results = model(frame, verbose=False, conf = 0.55, imgsz=224) 

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

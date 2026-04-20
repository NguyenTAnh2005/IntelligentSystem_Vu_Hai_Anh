from ultralytics import YOLO
from pathlib import Path
current_file = Path(__file__).resolve()
ROOT_DIR = current_file.parent.parent.parent
MODEL_PATH = ROOT_DIR/"models"/ "yolov8.pt"
# 1. Load file weights của bạn (đổi lại đường dẫn nếu cần)
model = YOLO(MODEL_PATH)

# 2. In ra thông tin tổng quan (Số layers, tham số, GFLOPs...)
print("--- TỔNG QUAN MÔ HÌNH ---")
model.info()

# 3. In ra chi tiết cấu trúc từng block trong mạng
print("\n--- CHI TIẾT CẤU TRÚC ---")
print(model.model)
import torch
from pathlib import Path
from ultralytics import YOLO

# Lấy vị trí file train.py hiện tại 
current_file = Path(__file__).resolve()
# Lùi ra  cấp thư mục gốc, 1 parent --> src, +1 parent --> thư mục gốc final_project
ROOT_DIR = current_file.parent.parent
# Ghép lại đường dẫn file data.yaml
DATA_PATH = ROOT_DIR / "data" / "dataset_yolo" / "data.yaml"
# Nơi sẽ lưu mô hình sau khi train 
MODEL_SAVE_PATH = ROOT_DIR / "models"

def main():
    # KHỞI TẠO MODEL YOLO 
    print("🎬 Đang khởi tạo mô hình YOLOv8n...")
    model = YOLO("yolov8n.pt")

    # KIỂM TRA THIẾT BỊ (GPU OR CPU)
    device = 0 if torch.cuda.is_available() else "cpu"
    print(f"💻 Thiết bị sử dụng: {device}")

    # TIẾN HÀNH HUẤN LUYỆN 
    print("🔥 Bắt đầu quá trình huấn luyện...")
    model.train(
        data = str(DATA_PATH),
        epochs=150,
        imgsz = 224,
        batch = 32,
        device = device,
        project = str(ROOT_DIR/"reports"),
        name = "yolo_animal_train2",
        save = True,
        plots= True
    )
    print(f"✅ DONE! Kiểm tra kết quả trong: {ROOT_DIR}/reports/yolo_animal_train2")
    print(f"🚀 File 'best.pt' nằm trong thư mục weights!")
if __name__ == '__main__':
    main()
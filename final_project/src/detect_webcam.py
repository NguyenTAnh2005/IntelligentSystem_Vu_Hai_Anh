import os
from pathlib import Path
from ultralytics import YOLO

# 1. THIẾT LẬP ĐƯỜNG DẪN 
# Vị trí đứng: src/detect_webcam.py -> parent nhảy ra gốc project
current_file = Path(__file__).resolve()
ROOT_DIR = current_file.parent.parent

# Trỏ thẳng vào file 'best.pt' ní vừa lấy được
# Chú ý: Hãy chắc chắn ní đã copy file best.pt vào thư mục 'models/' cho gọn gàng nhé.
MODEL_PATH = ROOT_DIR / "models" / "best.pt" 

def main():
    # 2. KIỂM TRA FILE MÔ HÌNH
    if not MODEL_PATH.exists():
        print(f"❌ Không tìm thấy file mô hình tại: {MODEL_PATH}")
        print("Vui lòng copy file best.pt ní vừa train xong vào thư mục 'models/' và đổi tên nhé.")
        return

    # 3. KHỞI TẠO MODEL VỚI 'HÀNG XỊN' BEST.PT
    print(f"🎬 Đang tải mô hình: {MODEL_PATH}...")
    model = YOLO(MODEL_PATH)

    # 4. CHẠY NHẬN DIỆN TRỰC TIẾP TRÊN WEBCAM (SOURCE=0)
    print("🔥 Đang mở Webcam... Giơ điện thoại lên đi ní ơi!")
    
    # model.predict là hàm suy luận
    # source=0: Lấy nguồn từ Webcam đầu tiên của laptop
    # show=True: Tự động mở cửa sổ hiển thị video
    model.predict(source=0, show=True)

if __name__ == '__main__':
    main()
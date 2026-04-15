import os
import torch
from pathlib import Path
from ultralytics import YOLO

# Fix PyTorch 2.6+ weights_only security check
# Monkey-patch torch.load to use weights_only=False for loading trusted model files
_original_torch_load = torch.load
def torch_load_patched(f, *args, **kwargs):
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return _original_torch_load(f, *args, **kwargs)
torch.load = torch_load_patched

# 1. THIẾT LẬP ĐƯỜNG DẪN 
# Vị trí đứng: src/detect_webcam.py -> parent nhảy ra gốc project
current_file = Path(__file__).resolve()
ROOT_DIR = current_file.parent.parent.parent

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

    # 4. TÌM CAMERA KHẢ DỤNG
    import cv2
    camera_idx = None
    for i in range(5):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            camera_idx = i
            cap.release()
            break
    
    if camera_idx is None:
        print("❌ Không tìm thấy camera nào!")
        print("💡 Thay thế: Sử dụng file video: model.predict(source='video.mp4', show=True)")
        return
    
    # 5. CHẠY NHẬN DIỆN TRỰC TIẾP TRÊN WEBCAM
    print(f"🔥 Đang mở Camera {camera_idx}... Giơ điện thoại lên đi ní ơi!")
    
    # model.predict là hàm suy luận
    # source=camera_idx: Lấy nguồn từ camera đã tìm được
    # show=True: Tự động mở cửa sổ hiển thị video
    model.predict(source=camera_idx, show=True)

if __name__ == '__main__':
    main()
from pathlib import Path

import cv2
from ultralytics import YOLO

current_file = Path(__file__).resolve()
ROOT_DIR = current_file.parent.parent.parent

MODEL_PATH = ROOT_DIR / "models" / "best.pt"

# ================== CAMERA SOURCE ==================
# 1) Laptop webcam: set CAMERA_SOURCE = 0
# 2) Phone IP Webcam: set CAMERA_SOURCE = IP_WEBCAM_URL
#
# Với app "IP Webcam" (Android), URL hay dùng:
# - http://<ip>:8080/video  (thường chạy được với OpenCV)
# - Nếu app hiện URL khác, ưu tiên copy đúng URL từ app.
IP_WEBCAM_URL = "http://192.168.1.11:8080/video"

CAMERA_SOURCE = IP_WEBCAM_URL

IMG_SIZE = 640
CONF_THRES = 0.25
WINDOW_NAME = "YOLO - Camera"


def main() -> None:
    if not MODEL_PATH.exists():
        print(f"❌ Không tìm thấy file mô hình tại: {MODEL_PATH}")
        return

    print(f"🎬 Đang tải mô hình: {MODEL_PATH}...")
    model = YOLO(MODEL_PATH)

    print(f"📷 Đang mở camera source: {CAMERA_SOURCE}")
    cap = cv2.VideoCapture(CAMERA_SOURCE)
    if not cap.isOpened():
        print("❌ Không mở được camera. Kiểm tra lại URL/IP hoặc quyền camera.")
        return

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

    try:
        while True:
            ok, frame = cap.read()
            if not ok or frame is None:
                print("⚠️ Không đọc được frame từ camera (mất kết nối?)")
                break

            results = model.predict(
                source=frame,
                imgsz=IMG_SIZE,
                conf=CONF_THRES,
                verbose=False,
            )
            annotated = results[0].plot() if results else frame

            cv2.imshow(WINDOW_NAME, annotated)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
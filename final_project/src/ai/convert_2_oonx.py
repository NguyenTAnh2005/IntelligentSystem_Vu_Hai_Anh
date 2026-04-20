from ultralytics import YOLO
from pathlib import Path
current_file = Path(__file__).resolve()
ROOT_DIR = current_file.parent.parent.parent
MODEL_PATH = ROOT_DIR / "models" / "yolov8.pt"

model = YOLO(MODEL_PATH)
model.export(format='onnx')

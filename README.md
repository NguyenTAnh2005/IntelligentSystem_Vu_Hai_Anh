# Intelligent System – Vũ Hải Anh

Repo lưu trữ bài tập và đồ án môn **Hệ Thống Thông Minh**.

---

## Cấu trúc thư mục

```
.
├── study/
│   ├── week02/          # Bài tập tuần 2: xử lý & mô phỏng dữ liệu CSV (HVAC)
│   └── week03/          # Bài tập tuần 3: logic mờ (fuzzy logic) – hàm thành viên, bộ điều khiển
└── final_project/       # Đồ án cuối kỳ: nhận diện động vật với YOLOv8
    ├── data/            # Dataset YOLO (train/valid/test)
    ├── models/          # Lưu file best.pt sau khi train
    ├── src/
    │   ├── train.py         # Huấn luyện mô hình YOLOv8
    │   └── detect_webcam.py # Nhận diện trực tiếp qua webcam
    └── rename_dataset.py    # Chuẩn hóa tên file trong dataset
```

---

## Cài đặt

```bash
pip install -r final_project/requirements.txt
```

---

## Chạy đồ án cuối kỳ

### 1. Huấn luyện mô hình

```bash
python final_project/src/train.py
```

Kết quả được lưu trong `final_project/reports/yolo_animal_train2/`.  
Copy file `weights/best.pt` vào thư mục `final_project/models/`.

### 2. Nhận diện qua Webcam

```bash
python final_project/src/detect_webcam.py
```

---

## Bài tập học phần

| Tuần | Nội dung |
|------|----------|
| Week 02 | Tạo & xử lý dữ liệu CSV mô phỏng hệ thống HVAC |
| Week 03 | Logic mờ: hàm thành viên, luật mờ, bộ điều khiển fuzzy |

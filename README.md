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
=======
# IntelligentSystem_Vu_Hai_Anh

Bài tập và dự án cuối kỳ môn **Hệ thống Thông minh**.

---

## 📁 Cấu trúc thư mục

```
IntelligentSystem_Vu_Hai_Anh/
├── final_project/          # Dự án cuối kỳ: Nhận diện động vật bằng YOLOv8
│   ├── data/               # Dataset (quản lý bằng DVC)
│   ├── models/             # File mô hình đã huấn luyện (best.pt)
│   ├── reports/            # Kết quả và biểu đồ sau khi train
│   ├── src/
│   │   ├── train.py        # Script huấn luyện mô hình YOLOv8
│   │   └── detect_webcam.py # Script nhận diện thời gian thực qua Webcam
│   ├── rename_dataset.py   # Tiện ích đổi tên file dataset về định dạng YOLO
│   └── requirements.txt    # Các thư viện cần thiết
├── study/
│   ├── week02/             # Bài tập tuần 2: Mô phỏng HVAC & thống kê dữ liệu
│   └── week03/             # Bài tập tuần 3: Logic mờ & bộ điều khiển fuzzy
└── README.md
```

---

## 🚀 Dự án cuối kỳ — Nhận diện động vật (YOLOv8)

### Cài đặt

```bash
cd final_project
pip install -r requirements.txt
```

### Huấn luyện mô hình

```bash
python src/train.py
```

- Mô hình sử dụng: **YOLOv8n** (nano)
- Số epochs: 150, batch size: 32, imgsz: 224
- Kết quả lưu tại: `reports/yolo_animal_train2/`
- File mô hình tốt nhất: `models/best.pt`

### Nhận diện qua Webcam

```bash
python src/detect_webcam.py
```

Yêu cầu: đã có file `models/best.pt` sau khi train xong.

---

## 📚 Bài tập theo tuần

### Tuần 2 — Mô phỏng & phân tích dữ liệu HVAC

| File | Mô tả |
|------|-------|
| `bai1_generate_csv.py` | Sinh dữ liệu mô phỏng hệ thống HVAC ra file CSV |
| `bai2_read_plot.py`    | Đọc và vẽ đồ thị dữ liệu |
| `bai3_clean_outlier.py`| Làm sạch dữ liệu và loại bỏ ngoại lệ |
| `bai4_stats.py`        | Tính thống kê (số phút T_in quá nóng, dễ chịu...) |
| `bai5_loop_sim.py`     | Mô phỏng vòng lặp điều khiển nhiệt độ |

### Tuần 3 — Logic mờ (Fuzzy Logic)

| File | Mô tả |
|------|-------|
| `bai1_membership.py`      | Định nghĩa và vẽ hàm thuộc (membership functions) |
| `bai2_rules_demo.py`      | Demo các luật mờ |
| `bai3_fuzzy_controller.py`| Bộ điều khiển mờ: fuzzify → rules → defuzzify (centroid) |
| `bai4_apply_to_loop.py`   | Áp dụng bộ điều khiển mờ vào vòng lặp mô phỏng |

---

## 🛠 Yêu cầu hệ thống

- Python 3.8+
- [ultralytics](https://github.com/ultralytics/ultralytics) (YOLOv8)
- PyTorch
- numpy, matplotlib

---

## 📝 Ghi chú

- Dataset được quản lý bằng **DVC**. Chạy `dvc pull` để tải dữ liệu về trước khi train.
- Nếu có GPU, quá trình train sẽ tự động sử dụng CUDA.


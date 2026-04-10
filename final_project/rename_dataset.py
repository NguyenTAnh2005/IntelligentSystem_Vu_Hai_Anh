import os

# Tự động lấy đường dẫn tuyệt đối của thư mục chứa file script này (chính là final_project)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Từ final_project, nối thêm đường dẫn đi vào thư mục dataset_yolo
ROOT_DIR = os.path.join(BASE_DIR, "data", "dataset_yolo")

# Các thư mục con cần xử lý
SPLITS = ['train', 'test', 'valid']

def rename_yolo_dataset(root_dir, splits):
    for split in splits:
        images_dir = os.path.join(root_dir, split, 'images')
        labels_dir = os.path.join(root_dir, split, 'labels')

        # Kiểm tra xem cấu trúc thư mục có chuẩn không
        if not os.path.exists(images_dir) or not os.path.exists(labels_dir):
            print(f"Bỏ qua tập '{split}': Không tìm thấy folder 'images' hoặc 'labels' tại {images_dir}.")
            continue

        # Lấy danh sách các file ảnh
        image_files = [f for f in os.listdir(images_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        # Sắp xếp tên file để đánh số theo một thứ tự nhất định
        image_files.sort()

        print(f"Đang xử lý tập '{split}'... Tìm thấy {len(image_files)} ảnh.")

        for index, old_img_name in enumerate(image_files, start=1):
            # Tạo tên mới theo chuẩn: split_stt
            new_base_name = f"{split}_{index}"
            
            # Giữ nguyên phần mở rộng của ảnh gốc (thường là .jpg)
            img_ext = os.path.splitext(old_img_name)[1]
            new_img_name = f"{new_base_name}{img_ext}"
            new_lbl_name = f"{new_base_name}.txt"

            old_img_path = os.path.join(images_dir, old_img_name)
            new_img_path = os.path.join(images_dir, new_img_name)

            # Tìm tên file label cũ tương ứng (thay đuôi ảnh bằng .txt)
            old_lbl_name = os.path.splitext(old_img_name)[0] + ".txt"
            old_lbl_path = os.path.join(labels_dir, old_lbl_name)
            new_lbl_path = os.path.join(labels_dir, new_lbl_name)

            # Đổi tên file label (Nếu file label tồn tại thì mới đổi tên ảnh để tránh mất đồng bộ)
            if os.path.exists(old_lbl_path):
                try:
                    os.rename(old_lbl_path, new_lbl_path)
                    os.rename(old_img_path, new_img_path)
                except Exception as e:
                    print(f"Lỗi khi đổi tên {old_img_name}: {e}")
            else:
                print(f"⚠️ Cảnh báo: Ảnh '{old_img_name}' không có file label '{old_lbl_name}' đi kèm. Đã bỏ qua ảnh này.")

    print("\n✅ Hoàn tất việc chuẩn hóa tên file Dataset!")

if __name__ == "__main__":
    print(f"Đang chạy script từ gốc: {BASE_DIR}")
    print(f"Mục tiêu xử lý dữ liệu tại: {ROOT_DIR}\n")
    rename_yolo_dataset(ROOT_DIR, SPLITS)
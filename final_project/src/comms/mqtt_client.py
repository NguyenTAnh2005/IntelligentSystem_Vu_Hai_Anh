import paho.mqtt.client as mqtt

# =============================================================================
# CẤU HÌNH THÔNG SỐ MQTT
# =============================================================================
BROKER = "broker.emqx.io"
PORT = 1883

TOPIC_NHAN_KHOANG_CACH = "nhom3_httm/khoangcach"
TOPIC_GUI_BAO_DONG = "nhom3_httm/mucdo_nguyhiem"

# Biến để lưu cái hàm do main_system.py truyền vào (Dùng để hứng data)
client = mqtt.Client()
DISTANCE = None

# =============================================================================
# CÁC HÀM XỬ LÝ SỰ KIỆN TỰ ĐỘNG
# =============================================================================
def on_connect(client, userdata, flags, rc):
    """Hàm chạy khi kết nối thành công tới Broker"""
    if rc == 0:
        print("✅ [MQTT] Đã kết nối tới trạm EMQX thành công!")
        # Nối mạng xong là lập tức đăng ký nghe kênh Khoảng Cách ngay
        client.subscribe(TOPIC_NHAN_KHOANG_CACH)
        print(f"📡 [MQTT] Đang dỏng tai nghe kênh: {TOPIC_NHAN_KHOANG_CACH}")
    else:
        print(f"❌ [MQTT] Kết nối thất bại, mã lỗi: {rc}")

def on_message(client, userdata, msg):
    try:
        # Nhận được số từ ESP32
        khoang_cach_cm = int(msg.payload.decode('utf-8'))
        
        # Lập tức nhấc máy gọi báo cáo cho file main.py
        if DISTANCE:
            DISTANCE(khoang_cach_cm)
    except Exception as e:
        print(f"❌ [MQTT] LỖI DỮ LIỆU GỬI LÊN: '{msg.payload}' - Chi tiết: {e}")

client.on_connect = on_connect
client.on_message = on_message

# =============================================================================
# CÁC NÚT BẤM DÀNH CHO MAIN.PY SỬ DỤNG
# =============================================================================
def connect_mqtt():
    """Bật mạng MQTT"""
    client.connect(BROKER, PORT, 60)
    client.loop_start() 

def gui_canh_bao(muc_nguy_hiem_percent):
    """Bắn lệnh xuống ESP32"""
    payload = str(float(muc_nguy_hiem_percent))
    client.publish(TOPIC_GUI_BAO_DONG, payload)

def set_khoang_cach_callback(func):
    """Cung cấp đường dây nóng cho file mqtt"""
    global DISTANCE
    DISTANCE = func


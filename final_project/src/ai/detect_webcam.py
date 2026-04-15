from pathlib import Path
import csv
import json
import re
import time
import uuid

import cv2
import paho.mqtt.client as mqtt
from ultralytics import YOLO

current_file = Path(__file__).resolve()
ROOT_DIR = current_file.parent.parent.parent

MODEL_PATH = ROOT_DIR / "models" / "best.pt" 
CSV_PATH = ROOT_DIR / "data" / "data_new.csv"

# ESP32-CAM
ESP32_CAM_URL = "http://192.168.1.7:81/stream"

IMG_SIZE = 640
CONF_THRES = 0.25
WINDOW_NAME = "YOLO - ESP32-CAM"

# MQTT
MQTT_ENABLE = True
# MQTTX là app client; bạn vẫn cần broker. Theo cấu hình phổ biến trong MQTTX: broker.emqx.io
MQTT_BROKER_HOST = "broker.emqx.io"
MQTT_BROKER_PORT = 1883
MQTT_TOPIC_LEVEL = "nhom3_httm/mucdo_nguyhiem"  # payload: 0..3
MQTT_RETAIN = False

# Nếu connection trong MQTTX có Username/Password thì điền ở đây (không bắt buộc với broker public)
MQTT_CLIENT_ID = ""
MQTT_USERNAME = ""
MQTT_PASSWORD = ""

LEVEL_LABELS = {
    0: "An Toàn",
    1: "Vàng",
    2: "Đỏ",
    3: "Tử thần",
}

# Danger score scale
DANGER_SCORE_MAX = 10.0  # bạn nói mức hung dữ là 0..10


def normalize_key(text: str) -> str:
    """Normalize class/species names to improve CSV ↔ YOLO matching."""
    s = (text or "").strip().lower()
    s = s.replace(" ", "_").replace("-", "_")
    s = re.sub(r"[^a-z0-9_]+", "", s)
    s = re.sub(r"_+", "_", s)
    return s.strip("_")


def score_to_level(score_0_10: float) -> int:
    """Map 0..10 score to level 0..3."""
    score_0_10 = max(0.0, min(DANGER_SCORE_MAX, float(score_0_10)))
    if score_0_10 < 2.5:
        return 0
    if score_0_10 < 5.0:
        return 1
    if score_0_10 < 7.5:
        return 2
    return 3


def normalize_score(value: float) -> float:
    """Normalize score to 0..10.

    If CSV accidentally contains 0..100, convert to 0..10 by dividing by 10.
    """
    v = float(value)
    if v > DANGER_SCORE_MAX:
        v = v / 10.0
    return max(0.0, min(DANGER_SCORE_MAX, v))


def load_danger_scores(csv_path: Path) -> dict[str, float]:
    """Return dict: class_name(lower) -> max score (0..10) from CSV."""
    if not csv_path.exists():
        print(f"⚠️ Không tìm thấy CSV tại: {csv_path}")
        return {}

    scores: dict[str, float] = {}
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return {}

        # Auto-detect columns to avoid header mismatch (spaces/encoding/renames)
        field_map = {normalize_key(x): x for x in reader.fieldnames if x}
        name_col = field_map.get("ten_loai")
        score_col = None
        for k, original in field_map.items():
            if "muc_hung_du" in k:
                score_col = original
                break

        if not name_col or not score_col:
            print(f"⚠️ Không nhận diện được cột trong CSV. fieldnames={reader.fieldnames}")
            return {}

        print(f"📄 CSV columns: name_col='{name_col}' score_col='{score_col}'")
        for row in reader:
            name = normalize_key(row.get(name_col) or "")
            if not name:
                continue
            try:
                raw_str = row.get(score_col)
                raw = float((raw_str or "0").strip())
            except ValueError:
                continue
            score = normalize_score(raw)
            prev = scores.get(name, 0.0)
            scores[name] = max(prev, score)
    return scores


def danger_level_from_result(result, danger_scores: dict[str, float]) -> tuple[int, str | None, float | None]:
    """Compute max danger level from YOLO Result; returns (level, class_name, score)."""
    boxes = getattr(result, "boxes", None)
    if boxes is None or boxes.cls is None or len(boxes.cls) == 0:
        return 0, None, None

    best_level = 0
    best_name: str | None = None
    best_score: float | None = None


    for cls_idx in boxes.cls.tolist():
        try:
            name = str(result.names[int(cls_idx)])
        except Exception:
            continue
        key = normalize_key(name)
        score = danger_scores.get(key)
        if score is None:
            continue
        level = score_to_level(score)
        if level > best_level:
            best_level = level
            best_name = name
            best_score = score
            if best_level == 3:
                break

    return best_level, best_name, best_score


def yolo_debug_from_result(result) -> tuple[list[str], str | None, float | None]:
    """Return (seen_keys, top_name, top_conf) for debugging."""
    boxes = getattr(result, "boxes", None)
    if boxes is None or boxes.cls is None or len(boxes.cls) == 0:
        return [], None, None

    seen: list[str] = []
    try:
        for cls_idx in boxes.cls.tolist():
            try:
                name = str(result.names[int(cls_idx)])
            except Exception:
                continue
            key = normalize_key(name)
            if key and key not in seen:
                seen.append(key)
    except Exception:
        pass

    top_name = None
    top_conf = None
    try:
        if getattr(boxes, "conf", None) is not None and len(boxes.conf) > 0:
            confs = boxes.conf.tolist()
            clss = boxes.cls.tolist()
            best_i = max(range(len(confs)), key=lambda i: confs[i])
            top_conf = float(confs[best_i])
            top_name = str(result.names[int(clss[best_i])])
    except Exception:
        pass

    return seen, top_name, top_conf


def mqtt_connect() -> mqtt.Client | None:
    if not MQTT_ENABLE:
        return None

    client_id = MQTT_CLIENT_ID.strip() or f"yolo-{uuid.uuid4().hex[:10]}"

    # paho-mqtt 2.x khuyến nghị dùng Callback API v2
    client = None
    if hasattr(mqtt, "CallbackAPIVersion"):
        try:
            client = mqtt.Client(
                client_id=client_id,
                protocol=mqtt.MQTTv311,
                callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            )
        except TypeError:
            client = None
    if client is None:
        client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv311)

    if MQTT_USERNAME:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    try:
        client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, keepalive=30)
        client.loop_start()
        print(f"✅ MQTT connected: {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT} topic={MQTT_TOPIC_LEVEL}")
        return client
    except Exception as e:
        print(f"⚠️ MQTT connect lỗi: {e}")
        return None


def mqtt_publish_level(client: mqtt.Client | None, level: int, meta: dict) -> None:
    if client is None:
        return
    try:
        # Gửi số 0..3 để ESP32 dễ parse
        client.publish(MQTT_TOPIC_LEVEL, payload=str(int(level)), qos=0, retain=MQTT_RETAIN)
        # (Tuỳ chọn) gửi thêm metadata nếu bạn cần debug
        client.publish(MQTT_TOPIC_LEVEL + "/meta", payload=json.dumps(meta, ensure_ascii=False), qos=0, retain=False)
    except Exception as e:
        print(f"⚠️ MQTT publish lỗi: {e}")

def main():
    danger_scores = load_danger_scores(CSV_PATH)
    if danger_scores:
        print(f"📄 Đã load danger scores: {len(danger_scores)} loài từ CSV")
        print(f"📄 Ví dụ key từ CSV: {list(danger_scores.keys())[:10]}")
    else:
        print("⚠️ Chưa có danger scores từ CSV (sẽ mặc định level=0)")

    mqtt_client = mqtt_connect()

    if not MODEL_PATH.exists():
        print(f"❌ Không tìm thấy file mô hình tại: {MODEL_PATH}")
        return

    print(f"🎬 Đang tải mô hình: {MODEL_PATH}...")
    model = YOLO(MODEL_PATH)

    try:
        names = getattr(model, "names", {})
        if isinstance(names, dict):
            preview = list(names.values())[:15]
            print(f"🏷️ Model classes: {len(names)} lớp. Ví dụ: {preview}")
    except Exception:
        pass

    print("🔥 Đang kết nối ESP32-CAM...")

    # Cửa sổ có thể tự kéo để đổi kích thước
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

    try:
        last_level: int | None = None
        last_warn_ts = 0.0
        # Lưu ý: với video stream, Ultralytics trả về generator.
        # Cần iterate để chương trình chạy liên tục.
        for r in model.predict(
            source=ESP32_CAM_URL,
            stream=True,
            imgsz=IMG_SIZE,
            conf=CONF_THRES,
            verbose=False,
        ):
            level, animal, score = danger_level_from_result(r, danger_scores)

            seen_keys, top_name, top_conf = yolo_debug_from_result(r)
            top_key = normalize_key(top_name or "") if top_name else None
            top_csv_score = danger_scores.get(top_key) if top_key else None

            if level == 0 and seen_keys:
                # YOLO có detect nhưng không map được vào CSV hoặc score thấp -> level 0
                now = time.time()
                if now - last_warn_ts > 2.0:
                    last_warn_ts = now
                    print(
                        "⚠️ Level=0 nhưng YOLO đang thấy: "
                        f"seen={seen_keys} top={top_name}({top_conf}) csv_score={top_csv_score}"
                    )

            if last_level is None or level != last_level:
                label = LEVEL_LABELS.get(level, str(level))
                meta = {
                    "level": level,
                    "label": label,
                    "animal": animal,
                    "score": score,
                    "yolo_seen": seen_keys,
                    "yolo_top": {"name": top_name, "conf": top_conf},
                    "csv_score_top": top_csv_score,
                }
                print(f"📡 MQTT level={level} ({label}) animal={animal} score={score}")
                mqtt_publish_level(mqtt_client, level, meta)
                last_level = level

            frame = r.plot()
            cv2.imshow(WINDOW_NAME, frame)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord('q'), 27):  # q hoặc ESC để thoát
                break
    finally:
        if mqtt_client is not None:
            try:
                mqtt_client.loop_stop()
                mqtt_client.disconnect()
            except Exception:
                pass
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
/*
 * DỰ ÁN: HỆ THỐNG CẢNH BÁO ĐỘNG VẬT NGUY HIỂM (NHÓM 3)
 * MẠCH: ESP32 (Chế độ IoT Node - Đã fix lỗi Còi và Đèn RGB)
 */

#include <WiFi.h>
#include <PubSubClient.h>

// ================= 1. CẤU HÌNH MẠNG & MQTT =================
const char *ssid = "KTX MINH CHAU 38-42";
const char *password = "Mc270579@";
const char *mqtt_server = "broker.emqx.io";
const int mqtt_port = 1883;

// Đã dọn dẹp biến trùng lặp
const char *topic_pub_khoangcach = "khtn_nhom3_th02/khoangcach";
const char *topic_sub_baodong = "khtn_nhom3_th02/mucdo_nguyhiem";

WiFiClient espClient;
PubSubClient client(espClient);

// ================= 2. CẤU HÌNH CHÂN (PINS) =================
#define TRIG_PIN 4
#define ECHO_PIN 15

#define BUZZER_PIN 12
#define LED_RED 13
#define LED_GREEN 14
#define LED_BLUE 2 // Theo pin sếp mới đổi

// Cấu hình PWM cho Còi hú
const int buzzerFreq = 2000; // Hạ xuống 2000Hz nghe đanh và chói tai hơn
const int buzzerChannel = 0;
const int buzzerResolution = 8;

// ================= 3. BIẾN TOÀN CỤC =================
unsigned long lastMeasureTime = 0;
unsigned long lastBeepTime = 0;
int dangerPercent = 0; 
int currentLevel = 0;  
bool buzzerState = false;

// ================= HÀM ĐIỀU KHIỂN ĐÈN RGB =================
// (Code cũ của sếp bị thiếu hàm này nên không sáng đèn)
void setRGB(bool r, bool g, bool b) {
  digitalWrite(LED_RED, r);
  digitalWrite(LED_GREEN, g);
  digitalWrite(LED_BLUE, b);
}

// ================= HÀM KẾT NỐI =================
void setup_wifi() {
  Serial.print("Đang kết nối WiFi: ");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi OK!");
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Đang kết nối MQTT...");
    String clientId = "ESP32_Nhom3_" + String(random(0xffff), HEX);

    if (client.connect(clientId.c_str())) {
      Serial.println(" Thành công!");
      client.subscribe(topic_sub_baodong);
    } else {
      delay(5000);
    }
  }
}

// ================= NHẬN LỆNH TỪ LAPTOP =================
void callback(char *topic, byte *payload, unsigned int length) {
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }

  dangerPercent = message.toInt();
  Serial.print("Nhận lệnh báo động: ");
  Serial.print(dangerPercent);
  Serial.println("%");

  if (dangerPercent < 30) currentLevel = 0;
  else if (dangerPercent >= 30 && dangerPercent < 70) currentLevel = 1;
  else if (dangerPercent >= 70 && dangerPercent < 90) currentLevel = 2;
  else currentLevel = 3;
}

// ================= SETUP =================
void setup() {
  Serial.begin(115200);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  
  pinMode(LED_RED, OUTPUT);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_BLUE, OUTPUT);

  // Khởi tạo PWM cho còi
  ledcAttach(BUZZER_PIN, buzzerFreq, buzzerResolution);
  ledcWrite(BUZZER_PIN, 0);
  ledcWrite(buzzerChannel, 0); 

  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
}

// ================= VÒNG LẶP CHÍNH =================
void loop() {
  if (!client.connected()) reconnect();
  client.loop(); 

  unsigned long now = millis();

  // --- TÁC VỤ 1: ĐO SIÊU ÂM (Mỗi 500ms) ---
  if (now - lastMeasureTime >= 500) {
    lastMeasureTime = now;

    digitalWrite(TRIG_PIN, LOW); delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH); delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);

    long duration = pulseIn(ECHO_PIN, HIGH, 30000);

    if (duration > 0) {
      int distance_cm = duration * 0.034 / 2;
      char dist_str[8];
      sprintf(dist_str, "%d", distance_cm);
      client.publish(topic_pub_khoangcach, dist_str);
    }
  }

  // --- TÁC VỤ 2: HÚ CÒI & NHÁY ĐÈN ---
  if (currentLevel > 0) {
    int beepInterval = (currentLevel == 3) ? 200 : (currentLevel == 2) ? 500 : 1000;

    if (now - lastBeepTime >= beepInterval) {
      lastBeepTime = now;
      buzzerState = !buzzerState;

      if (buzzerState) {
        // VÁ LỖI: Dùng BUZZER_PIN thay vì buzzerChannel
        if (currentLevel == 1) {
          setRGB(LOW, LOW, HIGH); // XANH DƯƠNG
          ledcWrite(BUZZER_PIN, 50);
        } else if (currentLevel == 2) {
          setRGB(HIGH, LOW, HIGH); // TÍM
          ledcWrite(BUZZER_PIN, 150);
        } else if (currentLevel == 3) {
          setRGB(HIGH, LOW, LOW); // ĐỎ
          ledcWrite(BUZZER_PIN, 255);
        }
      } else {
        setRGB(LOW, LOW, LOW); // Tắt đèn
        ledcWrite(BUZZER_PIN, 0); // Tắt còi
      }
    }
  } else {
    setRGB(LOW, HIGH, LOW);
    ledcWrite(BUZZER_PIN, 0);
  }
}
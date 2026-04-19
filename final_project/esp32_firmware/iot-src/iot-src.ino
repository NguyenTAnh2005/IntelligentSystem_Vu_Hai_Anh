/*
 * DỰ ÁN: HỆ THỐNG CẢNH BÁO ĐỘNG VẬT NGUY HIỂM (NHÓM 3)
 * CẬP NHẬT: Gửi trạng thái Đèn và Còi lên MQTT
 */

#include <WiFi.h>
#include <PubSubClient.h>

// ================= 1. CẤU HÌNH MẠNG & MQTT =================
const char *ssid = "";
const char *password = "";
const char *mqtt_server = "broker.emqx.io";
const int mqtt_port = 1883;

// Các Topic Pub/Sub
const char *topic_pub_khoangcach = "nhom3_httm/khoangcach";
const char *topic_sub_baodong = "nhom3_httm/mucdo_nguyhiem";
const char *topic_pub_den = "nhom3_httm/baodongden";
const char *topic_pub_coi = "nhom3_httm/baodongcoi"; // TOPIC MỚI CHO CÒI

WiFiClient espClient;
PubSubClient client(espClient);

// ================= 2. CẤU HÌNH CHÂN (PINS) =================
#define TRIG_PIN 4
#define ECHO_PIN 15
#define BUZZER_PIN 12
#define LED_RED 13
#define LED_GREEN 14
#define LED_BLUE 2 

const int buzzerFreq = 2000;
const int buzzerResolution = 8;

// ================= 3. BIẾN TOÀN CỤC =================
unsigned long lastMeasureTime = 0;
unsigned long lastBeepTime = 0;
int dangerPercent = 0; 
int currentLevel = 0;  
int lastLevel = -1; 
bool buzzerState = false;
bool lastBuzzerState = false; // Theo dõi trạng thái còi để tránh gửi MQTT trùng lặp

// ================= HÀM ĐIỀU KHIỂN ĐÈN RGB =================
void setRGB(bool r, bool g, bool b) {
  digitalWrite(LED_RED, r);
  digitalWrite(LED_GREEN, g);
  digitalWrite(LED_BLUE, b);
}

// ================= HÀM GỬI TRẠNG THÁI LÊN MQTT =================
void publishStatus() {
  // 1. Gửi trạng thái đèn
  if (currentLevel == 0) client.publish(topic_pub_den, "green");
  else if (currentLevel == 1) client.publish(topic_pub_den, "blue");
  else if (currentLevel == 2) client.publish(topic_pub_den, "purple");
  else if (currentLevel == 3) client.publish(topic_pub_den, "red");

  // 2. Gửi trạng thái còi (Dựa trên buzzerState thực tế)
  if (buzzerState && currentLevel > 0) {
    client.publish(topic_pub_coi, "on");
  } else {
    client.publish(topic_pub_coi, "off");
  }
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
      publishStatus(); // Cập nhật trạng thái ngay khi kết nối
    } else {
      delay(5000);
    }
  }
}

// ================= NHẬN LỆNH TỪ LAPTOP =================
void callback(char *topic, byte *payload, unsigned int length) {
  String message = "";
  for (int i = 0; i < length; i++) message += (char)payload[i];

  dangerPercent = message.toInt();
  if (dangerPercent < 30) currentLevel = 0;
  else if (dangerPercent >= 30 && dangerPercent < 70) currentLevel = 1;
  else if (dangerPercent >= 70 && dangerPercent < 90) currentLevel = 2;
  else currentLevel = 3;
  
  // Gửi trạng thái đèn ngay khi nhận được mức độ mới
  if (currentLevel != lastLevel) {
    publishStatus();
    lastLevel = currentLevel;
  }
}

// ================= SETUP =================
void setup() {
  Serial.begin(115200);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(LED_RED, OUTPUT);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_BLUE, OUTPUT);

  ledcAttach(BUZZER_PIN, buzzerFreq, buzzerResolution);
  ledcWrite(BUZZER_PIN, 0);

  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
}

// ================= VÒNG LẶP CHÍNH =================
void loop() {
  if (!client.connected()) reconnect();
  client.loop(); 

  unsigned long now = millis();

  // --- TÁC VỤ 1: ĐO KHOẢNG CÁCH (500ms/lần) ---
  if (now - lastMeasureTime >= 500) {
    lastMeasureTime = now;
    digitalWrite(TRIG_PIN, LOW); delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH); delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);
    long duration = pulseIn(ECHO_PIN, HIGH, 30000);
    if (duration > 0) {
      int distance_cm = duration * 0.034 / 2;
      client.publish(topic_pub_khoangcach, String(distance_cm).c_str());
    }
  }

  // --- TÁC VỤ 2: HÚ CÒI & NHÁY ĐÈN ---
  if (currentLevel > 0) {
    int beepInterval = (currentLevel == 3) ? 200 : (currentLevel == 2) ? 500 : 1000;

    if (now - lastBeepTime >= beepInterval) {
      lastBeepTime = now;
      buzzerState = !buzzerState; // Đảo trạng thái còi (on/off)

      // Gửi trạng thái còi lên MQTT mỗi khi nó thay đổi (on <-> off)
      client.publish(topic_pub_coi, buzzerState ? "on" : "off");

      if (buzzerState) {
        if (currentLevel == 1) { setRGB(0, 0, 1); ledcWrite(BUZZER_PIN, 50); }
        else if (currentLevel == 2) { setRGB(1, 0, 1); ledcWrite(BUZZER_PIN, 150); }
        else if (currentLevel == 3) { setRGB(1, 0, 0); ledcWrite(BUZZER_PIN, 255); }
      } else {
        setRGB(0, 0, 0); 
        ledcWrite(BUZZER_PIN, 0); 
      }
    }
  } else {
    // Trạng thái an toàn
    if (buzzerState != false) { // Chỉ gửi MQTT một lần khi chuyển về an toàn
        buzzerState = false;
        client.publish(topic_pub_coi, "off");
        setRGB(0, 1, 0); // Hiện màu xanh lá
        ledcWrite(BUZZER_PIN, 0);
    }
  }
}
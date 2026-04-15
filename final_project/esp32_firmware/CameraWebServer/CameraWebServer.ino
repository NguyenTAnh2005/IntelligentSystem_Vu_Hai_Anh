#include "esp_camera.h"
#include <WiFi.h>
#include <PubSubClient.h>

#include "board_config.h"

// ================= CẤU HÌNH WIFI & MQTT =================
const char *ssid = "KTX MINH CHAU 38-42";
const char *password = "Mc270579@";

const char* mqtt_server = "broker.emqx.io"; 
const int mqtt_port = 1883;

// Các Topic MQTT
const char* mqtt_topic_sub = "nhom3_httm/mucdo_nguyhiem"; 
const char* mqtt_topic_pub = "nhom3_httm/khoangcach"; 
const char* mqtt_topic_ip  = "nhom3_httm/ip_webcam"; // 🔥 Topic IP của bạn ở đây

WiFiClient espClient;
PubSubClient client(espClient);

// ================= CẤU HÌNH CHÂN =================
const int redPin = 13;
const int greenPin = 14;
const int bluePin = 2;
const int buzzerPin = 12;

#define TRIG_PIN 4   // Chân phát siêu âm
#define ECHO_PIN 15  // Chân nhận siêu âm (RÚT RA KHI NẠP CODE)

// Cấu hình Còi PWM
const int buzzerFreq = 2000;       
const int buzzerResolution = 8;    

// Biến toàn cục
unsigned long lastBeepTime = 0;
unsigned long lastMeasureTime = 0; 
bool buzzerState = false;
int currentLevel = 0;

void startCameraServer();
void setupLedFlash();

// ================= HÀM XỬ LÝ KHI NHẬN LỆNH =================
void callback(char* topic, byte* payload, unsigned int length) {
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  message.trim();

  Serial.print("Nhận lệnh: ");
  Serial.println(message);

  digitalWrite(redPin, LOW);
  digitalWrite(greenPin, LOW);
  digitalWrite(bluePin, LOW);

  if (message == "reset") {
    Serial.println("Reset ESP32...");
    delay(100); 
    ESP.restart(); 
  }
  else if (message == "0") {
    digitalWrite(greenPin, HIGH);
    currentLevel = 0;
  }
  else if (message == "1") {
    digitalWrite(bluePin, HIGH);
    currentLevel = 1;
  } 
  else if (message == "2") {
    digitalWrite(redPin, HIGH);
    currentLevel = 2;
  } 
  else if (message == "3") {
    digitalWrite(redPin, HIGH);
    digitalWrite(bluePin, HIGH);
    currentLevel = 3;
  }
  else {
    currentLevel = 0;
  }
}

// ================= HÀM KẾT NỐI MQTT =================
void reconnect() {
  while (!client.connected()) {
    Serial.print("Đang kết nối MQTT...");
    String clientId = "ESP32CAM_Nhom3_" + String(random(0xffff), HEX);
    if (client.connect(clientId.c_str())) {
      Serial.println(" -> Thành công!");
      client.subscribe(mqtt_topic_sub); 

      // 🔥 GỬI IP LÊN MQTT NGAY KHI KẾT NỐI THÀNH CÔNG
      String ipAddress = WiFi.localIP().toString();
      // Tham số 'true' ở cuối là Retain flag: Giữ IP này trên server để bạn mở MQTTX muộn vẫn thấy
      client.publish(mqtt_topic_ip, ipAddress.c_str(), true); 
      
      Serial.print("Đã gửi IP lên MQTT: ");
      Serial.println(ipAddress);

    } else {
      Serial.print(" -> Lỗi rc=");
      Serial.print(client.state());
      Serial.println(" thử lại sau 5s");
      delay(5000);
    }
  }
}

// ================= SETUP =================
void setup() {
  Serial.begin(115200);
  Serial.println();

  pinMode(redPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(bluePin, OUTPUT);
  
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  ledcAttach(buzzerPin, buzzerFreq, buzzerResolution);
  ledcWrite(buzzerPin, 0);

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.frame_size = FRAMESIZE_UXGA;
  config.pixel_format = PIXFORMAT_JPEG; 
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 12;
  config.fb_count = 1;

  if (config.pixel_format == PIXFORMAT_JPEG) {
    if (psramFound()) {
      config.jpeg_quality = 10;
      config.fb_count = 2;
      config.grab_mode = CAMERA_GRAB_LATEST;
    } else {
      config.frame_size = FRAMESIZE_SVGA;
      config.fb_location = CAMERA_FB_IN_DRAM;
    }
  }

  esp_camera_init(&config);
  
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
  
  startCameraServer();

  // 🔥 IN IP RA SERIAL MONITOR CHO CHẮC ĂN
  Serial.print("Camera Ready! Mở trình duyệt và truy cập: http://");
  Serial.println(WiFi.localIP());

  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
}

// ================= VÒNG LẶP CHÍNH =================
void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  unsigned long now = millis();

  // 1. NHÁY CÒI
  if (currentLevel > 0) {
    if (now - lastBeepTime >= 1000) {
      lastBeepTime = now;
      buzzerState = !buzzerState;

      if (buzzerState) {
        if (currentLevel == 1) ledcWrite(buzzerPin, 30);
        else if (currentLevel == 2) ledcWrite(buzzerPin, 140);
        else if (currentLevel == 3) ledcWrite(buzzerPin, 220);
      } else {
        ledcWrite(buzzerPin, 0);
      }
    }
  } else {
    ledcWrite(buzzerPin, 0);
  }

  // 2. ĐỌC SIÊU ÂM
  if (now - lastMeasureTime >= 2000) {
    lastMeasureTime = now;

    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);

    long duration = pulseIn(ECHO_PIN, HIGH, 30000); 

    if (duration > 0) {
      float distance = duration * 0.034 / 2;
      
      Serial.print("Khoang cach: ");
      Serial.print(distance);
      Serial.println(" cm");

      String payload = String(distance);
      client.publish(mqtt_topic_pub, payload.c_str());
    }
  }
}
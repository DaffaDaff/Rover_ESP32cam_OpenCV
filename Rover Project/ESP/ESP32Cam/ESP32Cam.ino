#include <WebServer.h>
#include <WiFi.h>
#include <esp32cam.h>

const char* WIFI_SSID = "mthudaa";

WebServer server(80);
IPAddress local_IP(192, 168, 4, 131);
IPAddress gateway(192, 168, 4, 1);
IPAddress subnet(255, 255, 0, 0);

static auto loRes = esp32cam::Resolution::find(320, 240);
static auto midRes = esp32cam::Resolution::find(350, 530);
static auto hiRes = esp32cam::Resolution::find(800, 600);

void jpg(){
  auto frame = esp32cam::capture();
  if (frame == nullptr) {
    Serial.println("FOTO GAGAL");
    server.send(503, "", "");
    return;
  }
  Serial.printf("FOTO %dx%d %db\n", frame->getWidth(), frame->getHeight(),
                static_cast<int>(frame->size()));
  server.setContentLength(frame->size());
  server.send(200, "image/jpeg");
  WiFiClient client = server.client();
  frame->writeTo(client);
}

void jpgLow(){
  if (!esp32cam::Camera.changeResolution(loRes)) {
    Serial.println("gagal");
  }
  jpg();
}

void jpgHi(){
  if (!esp32cam::Camera.changeResolution(hiRes)) {
    Serial.println("gagal");
  }
  jpg();
}

void jpgMid(){
  if (!esp32cam::Camera.changeResolution(midRes)) {
    Serial.println("gagal");
  }
  jpg();
}

void  setup(){
  Serial.begin(115200);
  pinMode(4, OUTPUT);
  Serial.println();
  {
    using namespace esp32cam;
    Config cfg;
    cfg.setPins(pins::AiThinker);
    cfg.setResolution(hiRes);
    cfg.setBufferCount(2);
    cfg.setJpeg(80);
    bool ok = Camera.begin(cfg);
    Serial.println(ok ? "KAMERA OKE SIH" : "KAMERA, YAK GAGAL");
  }
  WiFi.persistent(false);
  WiFi.mode(WIFI_STA);
  WiFi.config(local_IP, gateway, subnet);
  WiFi.begin(WIFI_SSID);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
  Serial.print("Resolusi rendah : http://");
  Serial.print(WiFi.localIP());
  Serial.println("/low.jpg");
  Serial.print("Resolusi tinggi : http://");
  Serial.print(WiFi.localIP());
  Serial.println("/hi.jpg");
  Serial.print("Resolusi menengah : http://");
  Serial.print(WiFi.localIP());
  Serial.println("/mid.jpg");
  server.on("/low.jpg", jpgLow);
  server.on("/hi.jpg", jpgHi);
  server.on("/mid.jpg", jpgMid);
  server.begin();
}

void loop(){
  server.handleClient();
  digitalWrite(4, HIGH);
}

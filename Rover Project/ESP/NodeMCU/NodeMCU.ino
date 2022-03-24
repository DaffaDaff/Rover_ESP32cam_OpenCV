#define ENA   14 //D5
#define ENB   12 //D6
#define IN_1  15 //D8
#define IN_2  13 //D7
#define IN_3  2 //D4
#define IN_4  0 //D3
#define CMD 5 //D1
#define BUZ 4 //D2

#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266WebServer.h>

String command;             
int speedCar = 255;
int sts = 0;
const char* ssid = "mthudaa";
ESP8266WebServer server(80);

void setup() {
  pinMode(ENA, OUTPUT);
  pinMode(ENB, OUTPUT);
  pinMode(IN_1, OUTPUT);
  pinMode(IN_2, OUTPUT);
  pinMode(IN_3, OUTPUT);
  pinMode(IN_4, OUTPUT);
  pinMode(CMD, INPUT);
  pinMode(BUZ, OUTPUT);
  Serial.begin(115200);
  WiFi.mode(WIFI_AP);
  WiFi.softAP(ssid);
  IPAddress myIP = WiFi.softAPIP();
  Serial.print("AP IP address: ");
  Serial.println(myIP);
  server.on ( "/", HTTP_handleRoot );
  server.onNotFound ( HTTP_handleRoot );
  server.begin();
  digitalWrite(BUZ, HIGH);
  delay(1000);
  digitalWrite(BUZ, LOW);
}

void maju() {
  digitalWrite(IN_1, LOW);
  digitalWrite(IN_2, HIGH);
  analogWrite(ENA, speedCar);

  digitalWrite(IN_3, LOW);
  digitalWrite(IN_4, HIGH);
  analogWrite(ENB, speedCar);
}

void mundur(){
  digitalWrite(IN_1, HIGH);
  digitalWrite(IN_2, LOW);
  analogWrite(ENA, speedCar);

  digitalWrite(IN_3, HIGH);
  digitalWrite(IN_4, LOW);
  analogWrite(ENB, speedCar);
}

void kiri(){
  digitalWrite(IN_1, HIGH);
  digitalWrite(IN_2, LOW);
  analogWrite(ENA, speedCar-50);

  digitalWrite(IN_3, LOW);
  digitalWrite(IN_4, HIGH);
  analogWrite(ENB, speedCar-50);
}

void kanan(){
  digitalWrite(IN_1, LOW);
  digitalWrite(IN_2, HIGH);
  analogWrite(ENA, speedCar-50);

  digitalWrite(IN_3, HIGH);
  digitalWrite(IN_4, LOW);
  analogWrite(ENB, speedCar-50);
}

void setop(){
  Serial.begin(115200);
  digitalWrite(IN_1, LOW);
  digitalWrite(IN_2, LOW);
  analogWrite(ENA, speedCar);

  digitalWrite(IN_3, LOW);
  digitalWrite(IN_4, LOW);
  analogWrite(ENB, speedCar);
}

void loop(){
  sts = digitalRead(CMD);
  if (sts==0){
    server.handleClient();
    command = server.arg("State");
    if (command == "F") maju();
    else if(command == "B"){
      mundur();
    }
    else if(command == "L"){
      kiri();
    }
    else if(command == "R"){
      kanan();
    }
    else if(command == "S"){
      setop();
    }
    else if(command == "ON"){
      digitalWrite(BUZ, HIGH);
    }
    else if(command == "OFF"){
      digitalWrite(BUZ, LOW);
    }
  }
  else{
    mundur();
    delay(50);
    setop();
    sts = 0;
  }
}

void HTTP_handleRoot(void){
  if (server.hasArg("State")) {
    Serial.println(server.arg("State"));
  }
  server.send ( 200, "text/html", "" );
  delay(1);
}

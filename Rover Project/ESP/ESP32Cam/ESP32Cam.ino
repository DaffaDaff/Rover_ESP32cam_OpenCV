#include <esp32cam.h>

#include <WiFi.h>
#include <WiFiClient.h>
#include <WiFiAP.h>

static const char* WIFI_SSID = "ESP32-AP";
static const char* WIFI_PASS = "123456789";

esp32cam::Resolution initialResolution;

WiFiServer server(80);

String header;

void setup()
{
  Serial.begin(115200);
  Serial.println();

  pinMode(1, OUTPUT);
  pinMode(2, OUTPUT);
  pinMode(3, OUTPUT);
  pinMode(4, OUTPUT);
  pinMode(14, OUTPUT);

  {
    using namespace esp32cam;

    initialResolution = Resolution::find(1024, 768);

    Config cfg;
    cfg.setPins(pins::AiThinker);
    cfg.setResolution(initialResolution);
    cfg.setJpeg(80);

    bool ok = Camera.begin(cfg);
    if (!ok) {
      Serial.println("camera initialize failure");
      delay(5000);
      ESP.restart();
    }
    Serial.println("camera initialize success");
  }

  // stabilize camera before starting WiFi to reduce "Brownout detector was triggered"
  delay(2000);

  Serial.println();
  Serial.println("Configuring access point...");

  if (!WiFi.softAP(WIFI_SSID, WIFI_PASS)) {
    log_e("Soft AP creation failed.");
    while(1);
  }
  IPAddress IP = WiFi.softAPIP();
  Serial.print("AP IP address: ");
  Serial.println(IP);

  server.begin();

  Serial.println("Server started");
}

void loop()
{
  auto frame = esp32cam::capture();

  WiFiClient client = server.available();

  if (client)
  {
    // if you get a client,
    Serial.println(F("New client"));           // print a message out the serial port
    String currentLine = "";                // make a String to hold incoming data from the client

    while (client.connected())
    {
      // loop while the client's connected
      if (client.available())
      {
        // if there's bytes to read from the client,
        char c = client.read();             // read a byte, then
        Serial.write(c);                    // print it out the serial monitor

        header += c;

        if (c == '\n')
        {
          // if the byte is a newline character
          // if the current line is blank, you got two newline characters in a row.
          // that's the end of the client HTTP request, so send a response:
          if (currentLine.length() == 0)
          {
            // HTTP headers always start with a response code (e.g. HTTP/1.1 200 OK)
            // and a content-type so the client knows what's coming, then a blank line:
            client.println(F("HTTP/1.1 200 OK"));
            client.println(F("Content-type:image/jpeg"));
            client.println();

            // the content of the HTTP response follows the header:
            frame->writeTo(client);

            if (header.indexOf("GET /forward" >= 0)){
              digitalWrite(1, HIGH);
              digitalWrite(3, LOW);

              digitalWrite(2, HIGH);
              digitalWrite(14, LOW);
            }
            else if (header.indexOf("GET /right" >= 0)){
              digitalWrite(3, HIGH);
              digitalWrite(1, LOW);

              digitalWrite(2, HIGH);
              digitalWrite(14, LOW);
            }
            else if (header.indexOf("GET /left" >= 0)){
              digitalWrite(1, HIGH);
              digitalWrite(3, LOW);

              digitalWrite(14, HIGH);
              digitalWrite(2, LOW);
            }
            else if (header.indexOf("GET /back" >= 0)){
              digitalWrite(3, HIGH);
              digitalWrite(1, LOW);

              digitalWrite(14, HIGH);
              digitalWrite(2, LOW);
            }
            else{
              digitalWrite(3, LOW);
              digitalWrite(1, LOW);

              digitalWrite(14, LOW);
              digitalWrite(2, LOW);
            }

            // The HTTP response ends with another blank line:
            client.println();
            // break out of the while loop:
            break;
          }
          else
          {
            // if you got a newline, then clear currentLine:
            currentLine = "";
          }
        }
        else if (c != '\r')
        {
          // if you got anything else but a carriage return character,
          currentLine += c;      // add it to the end of the currentLine
        }
      }
    }

    // close the connection:
    client.stop();
    Serial.println(F("Client disconnected"));
  }

  delay(1000);
}
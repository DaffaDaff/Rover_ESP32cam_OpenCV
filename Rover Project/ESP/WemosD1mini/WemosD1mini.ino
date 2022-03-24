#define trig  D7
#define echo D6
#define cmd D5
long durasi, jarak;
int batas = 10;//dalam cm

void setup() {
  pinMode(trig, OUTPUT);
  pinMode(echo, INPUT);
  pinMode(cmd, OUTPUT);
  Serial.begin(115200);
}

void loop() {
  digitalWrite(trig, LOW);
  delayMicroseconds(8);
  digitalWrite(trig, HIGH);
  delayMicroseconds(8);
  digitalWrite(trig, LOW);
  delayMicroseconds(8);
  durasi = pulseIn(echo, HIGH);
  jarak = (durasi / 2) / 29.1;
  Serial.println(jarak);
  if (jarak < batas){
    digitalWrite(cmd, HIGH);
  }
  else{
    digitalWrite(cmd, LOW);
  }
}

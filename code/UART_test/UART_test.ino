#define HWSERIAL Serial7
#define LED_2 2
void setup() {
    HWSERIAL.begin(115200);
    pinMode(LED_2, OUTPUT);
    digitalWrite(LED_2, HIGH);

}

void loop() {
  
  HWSERIAL.println("working");
  delay(500);

}

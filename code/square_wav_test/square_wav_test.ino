const int testPin = 13; // Teensy 4.1 内置 LED (可以换成其他 GPIO，如 2, 3, 4)

void setup() {
    pinMode(testPin, OUTPUT);
}

void loop() {
    digitalWrite(testPin, HIGH); // 设置引脚高电平 (3.3V)
    delayMicroseconds(500);       // 保持 500 µs
    digitalWrite(testPin, LOW);  // 设置引脚低电平 (0V)
    delayMicroseconds(500);       // 保持 500 µs
}

#include <TeensyTimerTool.h>
#include <SPI.h>

using namespace TeensyTimerTool;

// Configuration
const int chipSelectPin = 10;
const int SCLK = 50000000;       // SPI Clock = 50 MHz
const float samplingRate = 2000.0; // 784 kHz = 1.275 µs interval
PeriodicTimer myTimer(GPT1);     // Use GPT1 (general purpose timer)

volatile bool toggle = false;

void timerCallback() {
    uint16_t value = toggle ? 0xFFFF : 0x0000; // Alternate 5V and 0V for square wave

    // SPI Transmission
    digitalWrite(chipSelectPin, LOW);
    SPI.transfer(highByte(value));
    SPI.transfer(lowByte(value));
    digitalWrite(chipSelectPin, HIGH);

    toggle = !toggle;
}

void setup() {
    // SPI Configuration
    SPI.begin();
    SPI.beginTransaction(SPISettings(SCLK, MSBFIRST, SPI_MODE0));
    pinMode(chipSelectPin, OUTPUT);
    digitalWrite(chipSelectPin, HIGH);

    // Configure Timer for 1.275 µs interval
    float intervalMicros = 1e6 / samplingRate; // Calculate period in µs
    myTimer.begin(timerCallback, intervalMicros);
}

void loop() {
    // Nothing needed here; everything runs in the timer callback
}
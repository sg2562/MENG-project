/*
Square wave generation
Sampling rate: can go from 1kHz to 392kHz; resolution 16-bit; SCLK = 20MHz
Given all information in code

v: 2025/2/9
allow changing sampling rate
*/

#include <SPI.h>
#include <IntervalTimer.h>

// Pin definitions
const int chipSelectPin = 10;  // CS pin
const int INT_PIN = 1;

const int SCLK = 20000000;  // SCLK = 20 MHz
const float samplingRate = 392000.0; // 392 kHz

IntervalTimer timer; // Teensy-specific high-precision timer

volatile bool toggle = false; // Toggle flag for square wave

void setup() {
  // Initialize SPI
  SPI.begin();
  SPI.beginTransaction(SPISettings(SCLK, MSBFIRST, SPI_MODE0));

  // Configure chip select pin
  pinMode(chipSelectPin, OUTPUT);
  digitalWrite(chipSelectPin, HIGH);

  pinMode(INT_PIN, OUTPUT);


  // Calculate the period in microseconds
  float periodMicros = 1e6 / samplingRate; // Convert sampling rate to period (µs)

  // Configure the IntervalTimer for the desired period
  timer.begin(timerCallback, periodMicros); // Call ISR at each period
}

void loop() {
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');  // Read input until newline
    // Serial.println(input);
    float newRate = input.toFloat();  // Convert to float
    float periodMicros = 1e6 / newRate;  //period can be floating point
    // Configure the timer for the desired period
    timer.begin(timerCallback, periodMicros);
    Serial.write(highByte(0xFFFF));
    Serial.write(lowByte(0xFFFF));

  }
}

// ISR called by IntervalTimer
void timerCallback() {
  digitalWrite(INT_PIN, HIGH);
  uint16_t value = toggle ? 0xFFFF : 0x0000; // Alternate between high/low

  // Transmit SPI data
  digitalWrite(chipSelectPin, LOW);
  SPI.transfer(highByte(value));
  SPI.transfer(lowByte(value));
  digitalWrite(chipSelectPin, HIGH);

  toggle = !toggle; // Toggle state for square wave
  digitalWrite(INT_PIN, LOW);
}
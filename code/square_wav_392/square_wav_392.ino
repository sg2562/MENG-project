/*
Square wave generation
Sampling rate: can go from 1kHz to 392kHz; resolution 16-bit; SCLK = 20MHz
Given all information in code
*/

#include <SPI.h>
#include <IntervalTimer.h>

// Pin definitions
const int chipSelectPin = 10;  // CS pin
const int SCLK = 20000000;    // SCLK = 20 MHz
const float samplingRate = 3000.0; // 392 kHz

IntervalTimer timer; // Teensy-specific high-precision timer

volatile bool toggle = false; // Toggle flag for square wave

void setup() {
  // Initialize SPI
  SPI.begin();
  SPI.beginTransaction(SPISettings(SCLK, MSBFIRST, SPI_MODE0));

  // Configure chip select pin
  pinMode(chipSelectPin, OUTPUT);
  digitalWrite(chipSelectPin, HIGH);

  // Calculate the period in microseconds
  float periodMicros = 1e6 / samplingRate; // Convert sampling rate to period (µs)

  // Configure the IntervalTimer for the desired period
  timer.begin(timerCallback, periodMicros); // Call ISR at each period
}

void loop() {
  // Main loop does nothing; everything happens in the ISR
}

// ISR called by IntervalTimer
void timerCallback() {
  uint16_t value = toggle ? 0x9CCC : 0x0000; // Alternate between high/low

  // Transmit SPI data
  digitalWrite(chipSelectPin, LOW);
  SPI.transfer(highByte(value));
  SPI.transfer(lowByte(value));
  digitalWrite(chipSelectPin, HIGH);

  toggle = !toggle; // Toggle state for square wave
}
#include <SPI.h>

// Pin definitions
const int DAC_MISO = 12; 
const int DAC_MOSI = 11;
const int DAC_SCLK = 13; 
const int DAC_CS = 10; 

// Sampling settings
const int resolution = 16;
const int samplingRate = 1000;
const int period = 1000 / samplingRate; // ms

void setup() {
  Serial.begin(115200);

  // Initialize SPI
  SPI.begin();  
  SPI.beginTransaction(SPISettings(1000000, MSBFIRST, SPI_MODE0));
  pinMode(DAC_CS, OUTPUT);
  digitalWrite(DAC_CS, HIGH);  
}

void loop() {
  int pulse_interval = 100; // Every 100 LOW, Output 1 HIGH
  int counter = 0;

  while (true) {
    uint16_t value;
    
    if (counter % pulse_interval == 0) {
      value = 0xFFFF;  // High
    } else {
      value = 0x0000;  // Low
    }

    Serial.print("DAC ");
    Serial.println(value);

    digitalWrite(DAC_CS, LOW);
    SPI.transfer(highByte(value));  
    SPI.transfer(lowByte(value));   
    digitalWrite(DAC_CS, HIGH);

    delay(period);
    counter++;
  }
}

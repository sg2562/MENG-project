/*
This script can read ADC, the input analog data is 5V/3V/GND from MCU
*/


#include <SPI.h>
//------------ DAC PART ------------
// Pin definitions
const int DAC_MISO = 12; // 
const int DAC_MOSI = 11;
const int DAC_SCLK = 13; // 
const int DAC_CS = 10 ;// 


//------------ ADC PART ------------
const int ADC_MISO = 39; // Dout
const int ADC_MOSI = 26;
const int ADC_SCLK = 27; // CLK
const int ADC_CS = 38 ;// CONVST (CS

// Constants 
const int resolution = 16;     // 16-bit resolution
const int samplingRate = 1000; // Sampling rate of 1kHz (unit is Hz)
const int period = 1000 / samplingRate; // Time each sample takes in milliseconds



void setup() {
  Serial.begin(115200);

  // Initialize SPI for DAC
  SPI.begin();  // SCLK=14, MOSI=13, MISO=11 (or your specific pins)
  SPI.beginTransaction(SPISettings(1000000, MSBFIRST, SPI_MODE0));
  pinMode(DAC_CS, OUTPUT);
  digitalWrite(DAC_CS, HIGH);  // Ensure DAC is not selected initially

  digitalWrite(DAC_CS, LOW);
  SPI.transfer16(0x9CCC); // 3V 
  digitalWrite(DAC_CS, HIGH);

  // Initialize SPI for ADC
  //NEED TO SPECIFY PIN (not sure about the standard SPI1 pins)
  SPI1.setMISO(ADC_MISO);
  SPI1.setMOSI(ADC_MOSI);
  SPI1.setSCK(ADC_SCLK);
  SPI1.begin();  

  SPI1.beginTransaction(SPISettings(1000000, MSBFIRST, SPI_MODE0));
  pinMode(ADC_CS, OUTPUT);
  digitalWrite(ADC_CS, HIGH);  // Ensure ADC is not selected initially

}

void loop() {

  digitalWrite(ADC_CS, LOW);

  int ReadData = SPI1.transfer16(0x0000); //use this one to read data, may use transfer() to increase the speed
  
  digitalWrite(ADC_CS, HIGH);

  
  Serial.println(ReadData);

  delay(period);



}
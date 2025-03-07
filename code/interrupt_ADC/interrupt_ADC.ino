/*
ADC interruptTimer
Sampling rate: can go from 1kHz to 392kHz; resolution 16-bit; SCLK = 20MHz
ATTENTION: SCLK canot go further than 20MHz, otherwise ADC output a very strange value.
*/

#include <SPI.h>
#include <IntervalTimer.h>

//------------ ADC PART ------------
const int ADC_MISO = 39; // Dout
const int ADC_MOSI = 26;
const int ADC_SCLK = 27; // CLK
const int ADC_CS = 38 ;// CONVST (CS


// Constants
const int SCLK = 20000000;    // SCLK = 20 MHz
const float samplingRate = 12000.0; // 392 kHz

// InterruptTimer
// IntervalTimer DACtimer; 
IntervalTimer ADCtimer;

volatile bool toggle = false; // Toggle flag for square wave, use volatile for shared variables
volatile bool dataReady = false; //for DAC and ADC syn
volatile bool SEND = true;

void setup() {
  Serial.begin(115200);

  SPI1.setMISO(ADC_MISO);
  SPI1.setMOSI(ADC_MOSI);
  SPI1.setSCK(ADC_SCLK);
  SPI1.begin();  
  SPI1.beginTransaction(SPISettings(SCLK, MSBFIRST, SPI_MODE0));
  pinMode(ADC_CS, OUTPUT);
  digitalWrite(ADC_CS, HIGH);  // Ensure ADC is not selected initially

  //Initialize two timers, they both have the same period 
  // Calculate the period (time for one sample) in microseconds
  float periodMicros = 1e6 / samplingRate;  //period can be floating point

  // Configure the timer for the desired period
  ADCtimer.begin(ADC_callback, periodMicros);
  // DACtimer.begin(DAC_callback, periodMicros); 
  
}

void loop() {
  // if (SEND == true){
  //   for (int i = 0; i<100; i++){
  //     Serial.write((byte*)&i, 2); 
  //   }
  //   // SEND = false;
  // }
  
  
}

// callback functions
// void DAC_callback() {
//   uint16_t value = toggle ? 0xFFFF : 0x0000; // Alternate between 5V and 0V

//   // Transmit SPI data
//   digitalWrite(DAC_CS, LOW);
//   SPI.transfer(highByte(value));
//   SPI.transfer(lowByte(value));
//   Serial.print("DAC");
//   Serial.println(value);
//   // SPI.transfer16(value);
//   digitalWrite(DAC_CS, HIGH);

//   dataReady = true;

//   toggle = !toggle; // Toggle state for square wave

// }

void ADC_callback(){

  digitalWrite(ADC_CS, LOW);
  uint16_t ReadData = SPI1.transfer16(0x0000); //use this one to read data, may use transfer() to increase the speed
  digitalWrite(ADC_CS, HIGH);
  Serial.write((byte*)&ReadData, sizeof(ReadData));

  // Serial.println(ReadData);

}

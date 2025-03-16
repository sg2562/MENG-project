#include <SPI.h>
#include <IntervalTimer.h>

#define chipSelectPin 10
#define ISR_Pin 1
#define LED_RED 33
#define LED_YELLOW 34

//buffer
#define BUFFER_SIZE 2048  // Adjust based on memory constraints
const int SCLK = 20000000;    // SCLK = 20 MHz
volatile uint16_t buffer[BUFFER_SIZE];  
volatile uint32_t readIndex = 0;
volatile uint32_t writeIndex = 0;
volatile uint32_t availableSamples = 0;
volatile bool IS_IDLE = true;
volatile bool TIMER_START = false;

IntervalTimer timer;
volatile float samplingRate = 1000.0; //default
volatile float periodMicros = 1e6 / samplingRate;
// uint16_t buffer = 0;
// bool bufferReady = false;

void setup() {

    Serial.begin(1152000);  // USB CDC Serial, 12Mbit/s
    availableSamples = 0;
    IS_IDLE = true;
    TIMER_START = false;

    pinMode(chipSelectPin, OUTPUT);
    pinMode(ISR_Pin, OUTPUT);
    pinMode(LED_RED, OUTPUT);
    pinMode(LED_YELLOW, OUTPUT);
    
    digitalWrite(LED_RED, HIGH);
    digitalWrite(chipSelectPin, HIGH);
    SPI.begin();
    SPI.beginTransaction(SPISettings(SCLK, MSBFIRST, SPI_MODE0));

      // Calculate the period in microseconds
    // float periodMicros = 1e6 / samplingRate; // Convert sampling rate to period (µs)
    // int periodMicros = 1000000 / samplingRate;

    // Configure the IntervalTimer for the desired period
    // timer.begin(timerCallback, periodMicros); // Call ISR at each period
}

void loop() {
  if (IS_IDLE){
    //clean buffer
    readIndex = 0;
    writeIndex = 0;
    availableSamples = 0;
    
    //try to recive sampling rate and send ACK to PC, and then IS_IDLE = false
    if(Serial.available()){
      String input = Serial.readStringUntil('\n');
      samplingRate = input.toFloat();
      // Serial.print("Received Sampling Rate: ");
      //   Serial.println(samplingRate);
      //   Serial.flush();

      if (samplingRate <= 392000.0){
        periodMicros = 1e6 / samplingRate;
        IS_IDLE = false;
      }
    }
  }
  else{
    //it can recieve sample from PC
    // Send "ready" signal if buffer has space, PC receives R to continue send samples
    if (availableSamples < (BUFFER_SIZE - 64)) {  // Leave margin for safety
        Serial.write('R');  
        Serial.flush();
    }

    // Read incoming samples from PC
    if ((Serial.available() >= 1) && (availableSamples < BUFFER_SIZE)) {
        digitalWrite(LED_YELLOW, HIGH);
        uint16_t sample = Serial.read() | (Serial.read() << 8);  // Read 16-bit sample
        buffer[writeIndex] = sample;
        writeIndex = (writeIndex + 1) % BUFFER_SIZE;
        availableSamples++;
    }

    //when timer is not start and there are enough samples, start timer
    if(TIMER_START == false && availableSamples >= 512){
      digitalWrite(LED_YELLOW, LOW);
      digitalWrite(LED_RED, LOW);
      delay(200);
      timer.begin(timerCallback, periodMicros);
      
      TIMER_START = true;
    }

    // if timer start, and only 64 samples left, stop timer.
    if(TIMER_START == true && availableSamples <= 64){
      digitalWrite(LED_YELLOW, LOW);
      digitalWrite(LED_RED, LOW);

      timer.end();
      TIMER_START = false;
      IS_IDLE = true;
    }
    //1. accumulate enough samples from PC in buffer, then start timer
    //2. if we have more than 512 samples, we begin to send to DAC, timer start
    //3. keep recieving data
    //4. if timer start, and only 64 samples left, stop timer.
  }
  
}

void timerCallback() {
  digitalWrite(ISR_Pin, HIGH); //Check ISR time
  digitalWrite(LED_RED, HIGH);
  if (availableSamples > 0) {  // Only send if data is available
    uint16_t sample = buffer[readIndex];
    readIndex = (readIndex + 1) % BUFFER_SIZE;
    availableSamples--;

  // Transmit SPI data
    digitalWrite(chipSelectPin, LOW);
    SPI.transfer(highByte(sample));
    SPI.transfer(lowByte(sample));
    digitalWrite(chipSelectPin, HIGH);
  }

  digitalWrite(ISR_Pin, LOW); //Check ISR time

}
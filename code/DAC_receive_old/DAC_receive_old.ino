#include <SPI.h>

#define BUFFER_SIZE 1024  // Adjust based on memory constraints
volatile uint16_t buffer[BUFFER_SIZE];  
volatile int readIndex = 0;
volatile int writeIndex = 0;
volatile int availableSamples = 0;
const int sampleRate = 100;

IntervalTimer sampleTimer;  

void setup() {
    Serial.begin(0);  // USB Serial operates at max speed (250 Mbit/s)
    pinMode(LED_BUILTIN, OUTPUT);
   
    sampleTimer.begin(dacOutput, 1000000 / sampleRate);  // DAC update interrupt
}

void loop() {
    // Send "ready" signal if buffer has space
    if (availableSamples < BUFFER_SIZE - 64) {  // Leave margin for safety
        Serial.write('R');  
    }

    // Read incoming samples from PC
    while (Serial.available() >= 2 && availableSamples < BUFFER_SIZE) {
        int16_t sample = Serial.read() | (Serial.read() << 8);  // Read 16-bit sample
        buffer[writeIndex] = sample;
        writeIndex = (writeIndex + 1) % BUFFER_SIZE;
        availableSamples++;
    }
}

// Timer interrupt for DAC output
void dacOutput() {
    if (availableSamples > 0) {  
        int16_t sample = buffer[readIndex];
        readIndex = (readIndex + 1) % BUFFER_SIZE;
        availableSamples--;

        analogWrite(A14, (sample + 32768) >> 4);  // Send sample to DAC
    } else {
        digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));  // Blink LED on buffer underrun
    }
}
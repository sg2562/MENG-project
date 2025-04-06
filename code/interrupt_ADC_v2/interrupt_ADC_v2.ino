/*
 * ADC Interrupt Timer - Teensy SPI ADC Data Acquisition
 * 
 * Sampling rate: 1kHz to 392kHz
 * Resolution: 16-bit
 * SCLK: 20MHz (Max)
 * 
 * ATTENTION: Do NOT exceed 20MHz for SCLK, or ADC output may be corrupted.
 */

#include <SPI.h>
#include <IntervalTimer.h>

//------------ ADC PART ------------
const int ADC_MISO = 39;  // Dout (MISO)
const int ADC_MOSI = 26;  // MOSI
const int ADC_SCLK = 27;  // CLK
const int ADC_CS   = 38;  // CONVST (CS)
const int LED_2  = 2;   // Status LED
const int LED_3  = 3;

// Constants
#define BUFFER_SIZE 2048
#define HWSERIAL Serial1

const int SCLK = 20000000;  // SCLK = 20 MHz

// Buffers and State Variables
volatile uint16_t buffer[BUFFER_SIZE];
volatile uint32_t readIndex = 0;
volatile uint32_t writeIndex = 0;
volatile uint32_t availableSamples = 0;
volatile bool IS_IDLE = true;
volatile bool TIMER_START = false;
volatile float samplingRate = 1000.0;  // Default 1kHz
volatile float periodMicros = 1e6 / samplingRate;

// Interrupt Timer
IntervalTimer ADCtimer;

void setup() {
    Serial.begin(115200);  // USB Serial for PC communication
    HWSERIAL.begin(115200);
    pinMode(LED_2, OUTPUT);
    pinMode(LED_3, OUTPUT);

    // SPI Configuration
    SPI1.setMISO(ADC_MISO);
    SPI1.setMOSI(ADC_MOSI);
    SPI1.setSCK(ADC_SCLK);
    SPI1.begin();
    SPI1.beginTransaction(SPISettings(SCLK, MSBFIRST, SPI_MODE0));

    pinMode(ADC_CS, OUTPUT);
    digitalWrite(ADC_CS, HIGH);  // Ensure ADC is deselected initially
    digitalWrite(LED_2, HIGH);
}

void loop() {
    if (IS_IDLE) {
        // Reset buffer indices
        readIndex = 0;
        writeIndex = 0;
        availableSamples = 0;

        // Try to receive sampling rate from PC
        if (Serial.available()) {
            String input = Serial.readStringUntil('\n');
            samplingRate = input.toFloat();
            HWSERIAL.println(samplingRate);

            if (samplingRate <= 392000.0) {
                digitalWrite(LED_2, LOW);
                digitalWrite(LED_3, HIGH);
                periodMicros = 1e6 / samplingRate;
                IS_IDLE = false;
            }
        }
    } 
    else { 
        // Send "Ready" Signal ('R') to PC (Only Once)
        Serial.write('R');
        Serial.flush();

        // Start ADC Timer if not started
        if (!TIMER_START) {
            ADCtimer.begin(ADC_callback, periodMicros);
            TIMER_START = true;
        }

        // Future feature: Stop ADC when PC sends 'C'
        // if (Serial.read() == 'C') {
        //     ADCtimer.end();
        //     TIMER_START = false;
        // }
    }
}

void ADC_callback() {
    digitalWrite(ADC_CS, LOW);
    uint16_t ReadData = SPI1.transfer16(0x0000);  // Read ADC Data
    digitalWrite(ADC_CS, HIGH);

    Serial.write((byte*)&ReadData, sizeof(ReadData));  // Send to PC
}

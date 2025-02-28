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

    // 初始化 SPI for DAC
    SPI.begin();
    SPI.beginTransaction(SPISettings(1000000, MSBFIRST, SPI_MODE0));
    pinMode(DAC_CS, OUTPUT);
    digitalWrite(DAC_CS, HIGH);

    // **写入 3V 到 DAC**
    digitalWrite(DAC_CS, LOW);
    SPI.transfer16(0x9010); // 3V 
    digitalWrite(DAC_CS, HIGH);

    // **等待 DAC 稳定**
    delay(10);

    // 初始化 SPI for ADC
    SPI1.setMISO(ADC_MISO);
    SPI1.setMOSI(ADC_MOSI);
    SPI1.setSCK(ADC_SCLK);
    SPI1.begin();
    SPI1.beginTransaction(SPISettings(1000000, MSBFIRST, SPI_MODE0));
    pinMode(ADC_CS, OUTPUT);
    digitalWrite(ADC_CS, HIGH);  // ADC 默认不选中
}

void loop() {
    // **触发 ADC 采样**
    digitalWrite(ADC_CS, LOW); // 先拉低 CS
    delayMicroseconds(1);       // 确保时间足够
    digitalWrite(ADC_CS, HIGH); // 触发转换

    delayMicroseconds(2);  // 等待转换完成

    // **读取 ADC 数据**
    digitalWrite(ADC_CS, LOW);
    int ReadData = SPI1.transfer16(0x0000);
    digitalWrite(ADC_CS, HIGH);

    // **转换为电压值**
    float Vref = 5.0; // 确保 Vref = 5V
    float voltage = (ReadData / 65535.0) * Vref;

    // **打印 ADC 结果**
    Serial.print("ADC Raw Data: ");
    Serial.print(ReadData);
    Serial.print("\tVoltage: ");
    Serial.println(voltage, 3);

    delay(1000 / samplingRate); // 1kHz 采样
}


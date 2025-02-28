#include <TeensyTimerTool.h>
#include <SPI.h>

using namespace TeensyTimerTool;

// 配置
const int DAC_CS_PIN = 10;       // DAC 片选引脚
const int SCLK = 25000000;       // SPI Clock = 20 MHz
const float samplingRate = 784000.0; // 392 kHz 采样率
PeriodicTimer myTimer(GPT1);     // 使用 GPT1 计时器

volatile bool toggle = false;    // 用于交替输出方波

void timerCallback() {
    uint16_t value = toggle ? 0xFFFF : 0x0000;  // 交替输出最大/最小值（5V - 0V 方波）

    // SPI 传输到 DAC
    digitalWriteFast(DAC_CS_PIN, LOW); // 使用 digitalWriteFast() 提高速度
    SPI.transfer16(value);
    digitalWriteFast(DAC_CS_PIN, HIGH);

    toggle = !toggle;
}

void setup() {
    // 配置 SPI
    SPI.begin();
    SPI.beginTransaction(SPISettings(SCLK, MSBFIRST, SPI_MODE0)); // 使用 SPI Mode 1

    // 配置片选引脚
    pinMode(DAC_CS_PIN, OUTPUT);
    digitalWrite(DAC_CS_PIN, HIGH); // 默认拉高

    // 设置定时器，392 kHz 触发
    float intervalMicros = (1e6 / samplingRate); // 计算周期 (2.55 µs)
    myTimer.begin(timerCallback, intervalMicros);
}

void loop() {
    // 主循环留空，所有操作由定时器完成
}

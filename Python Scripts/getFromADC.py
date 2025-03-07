'''
This code achieves the basic function to recieve samples from ADC
'''

import serial
import wave
import numpy as np
import struct

sampling_rate = 1000
num_samples = 0  # Counter for the number of samples
# output_filename = 'output.wav'

# output_file = wave.open(output_filename, 'wb')

# Set the WAV file parameters
# output_file.setnchannels(1)  # Mono audio
# output_file.setsampwidth(2)  # 16-bit samples (2 bytes per sample)
# output_file.setframerate(sampling_rate)

ser = serial.Serial("COM4")
ser.reset_input_buffer()
for i in range(10000):
    # highByte = ser.read(1)
    # lowByte = ser.read(1)
    data = ser.read(2)

    # ADC_value = highByte[0]<<8 | lowByte[0]
    ADC_value = struct.unpack('<H', data)[0]

    print("ADC value = ", ADC_value)



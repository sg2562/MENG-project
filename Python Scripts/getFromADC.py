'''
This code achieves the basic function to recieve samples from ADC
'''

import serial
import wave
import numpy as np
import struct

sampling_rate = 100000
num_samples = 0  # Counter for the number of samples
recording = True
# output_filename = 'output.wav'

# output_file = wave.open(output_filename, 'wb')

# Set the WAV file parameters
# output_file.setnchannels(1)  # Mono audio
# output_file.setsampwidth(2)  # 16-bit samples (2 bytes per sample)
# output_file.setframerate(sampling_rate)

ser_adc = serial.Serial("COM4")
ser_adc.reset_input_buffer()

"""Handles ADC communication: Sends SR, waits for 'R'."""
try:
    print("Sending sampling rate to ADC...")
    ser_adc.write(f"{sampling_rate}\n".encode())
    ser_adc.flush()

    # Wait for 'R' from ADC
    while True:
        if ser_adc.in_waiting > 0:
            response = ser_adc.read(1).decode()
            if response == 'R':
                print("Received 'R' from ADC. ADC is recording.")
                adc_ready = True
                break
    print("ADC started, receiving data...")
    # with open("adc_data.bin", "wb") as f:  # Save data to file
    # while recording:
    #     if ser_adc.in_waiting >= 2:  # Each sample is 2 bytes
    #         data = ser_adc.read(2)
    #         ADC_value = struct.unpack('<H', data)[0]  
    #         print(ADC_value)
            # Uncomment this if you want to see real-time data:
            # print(int.from_bytes(sample, "little"))
except Exception as e:
    print(f"Error in ADC thread: {e}")
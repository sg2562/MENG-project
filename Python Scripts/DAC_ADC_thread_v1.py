import threading
import serial
import wave
import numpy as np
import struct
import time
BAUD_RATE = 1152000  

def run_dac():
    SERIAL_PORT = "COM8"
    WAV_FILE = "./wavefile/12.0kHz_1000Hz_sine.wav"
    # WAV_FILE = "square_10kHz_long.wav"

    ser = serial.Serial(SERIAL_PORT, baudrate=BAUD_RATE, timeout=0.1)  # Timeout prevents blocking
    ser.reset_input_buffer()
    ser.reset_output_buffer()

    # Read WAV file
    with wave.open(WAV_FILE, "rb") as wav:
        # num_channels = wav.getnchannels()
        # sample_width = wav.getsampwidth()
        frame_rate = wav.getframerate()
        num_frames = wav.getnframes()
        raw_data = wav.readframes(num_frames)

    command = f"{frame_rate}\n"  # Convert to string and add newline
    ser.write(command.encode())  # Send to Arduino
    print(f"Sent sampling rate: {frame_rate} Hz")

    # wavfile are signed!!
    samples = [int.from_bytes(raw_data[i:i+2], byteorder="little", signed=True) + 32768 # 0-65535
           for i in range(0, len(raw_data), 2)]
    

    # shifting because DAC is outputing from -40 mV to 4.92V, where adc can only record non-negative value
    # shifted_samples = [(sample + 32768) // 2 for sample in samples]  # Scale to 16384 - 49151
    # shifted_samples = [(sample + 32768) // 2 for sample in samples]
    # samples = shifted_samples

    # Send samples with handshaking
    chunk_size = 256
    index = 0
    while index < len(samples):
        # ser.reset_input_buffer()
        if ser.in_waiting > 0:
            ready_signal = ser.read(1)  # Check if Teensy is ready
            if ready_signal == b'R':
                chunk = b''.join(sample.to_bytes(2, 'little', signed=False) for sample in samples[index:index + chunk_size])
                ser.write(chunk)
                index += chunk_size
            else:
                print(f"Ready signal not expected: {ready_signal.decode()}")

    ser.close()

def run_adc():
    ser_adc = serial.Serial("COM3", baudrate=BAUD_RATE, timeout=0.1)
    sampling_rate = 12000
    output_filename = "output_12k_1000_test.wav"
    with wave.open(output_filename, 'wb') as output_file:
        output_file.setnchannels(1)  # Mono audio
        output_file.setsampwidth(2)  # 16-bit samples (2 bytes per sample)
        output_file.setframerate(sampling_rate)
    
        i = 0
        recorded_samples = []


        for i in range(360000):
            data = ser_adc.read(2)
            ADC_value = struct.unpack('<H', data)[0]
            # print(f"when i = {i}, {ADC_value}")
            signed_value = ADC_value - 32768
            # restored_value = np.clip((ADC_value * 2) - 65536, -32768, 32767)
            # restored_value = (ADC_value - 32768) * 2
            # signed_value = restored_value - 32768
            recorded_samples.append(signed_value)
            # recorded_samples.append(np.int16(restored_value))

            # recorded_samples.append(signed_value)
        output_file.writeframes(np.array(recorded_samples, dtype=np.int16).tobytes())
        ser_adc.close()
        print(f"ADC recording completed. Saved as {output_filename}")

thread_dac = threading.Thread(target=run_dac)
thread_adc = threading.Thread(target=run_adc)

# Start threads
thread_adc.start()
thread_dac.start()
# time.sleep(1)


# Wait for completion
thread_dac.join()
thread_adc.join()
import threading
import serial
import wave
import numpy as np
import struct

def run_dac():
    SERIAL_PORT = "COM5"  # Adjust for your system
    BAUD_RATE = 1152000  # Irrelevant for USB Serial, kept for reference
    WAV_FILE = "square_1kHz_long.wav"
    # WAV_FILE = "square_10kHz_long.wav"

    ser = serial.Serial(SERIAL_PORT, baudrate=BAUD_RATE, timeout=0.1)  # Timeout prevents blocking

    # Read WAV file
    with wave.open(WAV_FILE, "rb") as wav:
        num_channels = wav.getnchannels()
        sample_width = wav.getsampwidth()
        frame_rate = wav.getframerate()
        num_frames = wav.getnframes()
        raw_data = wav.readframes(num_frames)

    command = f"{frame_rate}\n"  # Convert to string and add newline
    ser.write(command.encode())  # Send to Arduino
    print(f"Sent sampling rate: {frame_rate} Hz")

    samples = [int.from_bytes(raw_data[i:i+2], byteorder="little", signed=False)
            for i in range(0, len(raw_data), 2)]

    # Send samples with handshaking
    chunk_size = 128
    index = 0
    while index < len(samples):
        if ser.in_waiting > 0:
            ready_signal = ser.read(1)  # Check if Teensy is ready
            
            if ready_signal == b'R':
                # print(ready_signal)
                chunk = samples[index:index + chunk_size]  # Send in 512 size chunks
                for sample in chunk:
                    ser.write(sample.to_bytes(2, byteorder="little", signed=False))
                index += len(chunk)
            elif ready_signal in [b'A', b'B', b'S']:
                print(f"Debug from Teensy: {ready_signal.decode()}")

    ser.close()

def run_adc():
    sampling_rate = 1000  # Adjust to match your ADC's sampling rate
    num_samples = 0  # Counter for the number of samples
    output_filename = 'output.wav'

    # output_file = wave.open(output_filename, 'wb')

    # Set the WAV file parameters
    # output_file.setnchannels(1)  # Mono audio
    # output_file.setsampwidth(2)  # 16-bit samples (2 bytes per sample)
    # output_file.setframerate(sampling_rate)

    ser = serial.Serial("COM4")

    for i in range(100000):
        highByte = ser.read(1)
        lowByte = ser.read(1)

        ADC_value = highByte[0]<<8 | lowByte[0]

        # print("when i = ", i, " ADC highbyte = ", highByte[0], "lowbyte = ", lowByte[0])
        print(f"when i = {i}, {ADC_value}")
        # print("ADC value = ", ADC_value)

        # output_file.writeframes(struct.pack('<H', ADC_value)) #use H instead of h to accept 0-65535
        # output_file.writeframes(np.array(ADC_value, dtype=np.uint16).tobytes())



thread_dac = threading.Thread(target=run_dac)
thread_adc = threading.Thread(target=run_adc)

# Start threads
thread_dac.start()
thread_adc.start()

# Wait for completion
thread_dac.join()
thread_adc.join()
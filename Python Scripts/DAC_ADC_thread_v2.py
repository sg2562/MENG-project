import threading
import serial
import wave
import struct
import time
import numpy as np

# Global flag for stopping ADC when DAC is done
DAC_finished = False  
ADC_ready = False

def run_dac():
    global DAC_finished
    global ADC_ready
    SERIAL_PORT = "COM5"
    BAUD_RATE = 1152000  
    WAV_FILE = "./wavefile/12.0kHz_6000Hz_square.wav"
    # ser_adc = serial.Serial("COM4", baudrate=115200, timeout=0.5)

    ser = serial.Serial(SERIAL_PORT, baudrate=BAUD_RATE, timeout=0.5)  
    ser.reset_input_buffer()  
    ser.reset_output_buffer()

    # Read WAV file
    with wave.open(WAV_FILE, "rb") as wav:
        frame_rate = wav.getframerate()
        num_frames = wav.getnframes()
        raw_data = wav.readframes(num_frames)

    # Wait for ADC to be ready before sending SR
    if ADC_ready == True:
        print("ADC is ready, starting DAC...")
        command = f"{frame_rate}\n"
        ser.write(command.encode())  
        print(f"Sent sampling rate: {frame_rate} Hz")

        # Convert samples to little-endian 16-bit
        samples = [int.from_bytes(raw_data[i:i+2], byteorder="little", signed=True) + 32768
           for i in range(0, len(raw_data), 2)]

        # Send samples with handshaking
        chunk_size = 128
        index = 0
        while index < len(samples):
            if ser.in_waiting > 0:
                ready_signal = ser.read(1)  
                if ready_signal == b'R':
                    chunk = b''.join(sample.to_bytes(2, 'little', signed=False) for sample in samples[index:index + chunk_size])
                    ser.write(chunk)
                    index += chunk_size
                else:
                    print(f"Unexpected signal: {ready_signal.decode()}")
        # time.sleep(20)
        DAC_finished = True
        time.sleep(3)
        ser.close()
        print("DAC transmission completed.")

def run_adc():
    global DAC_finished
    global ADC_ready
    ser_adc = serial.Serial("COM4", baudrate=115200, timeout=0.5)

    sampling_rate = 12000
    print("Sending sampling rate to ADC...")
    ser_adc.write(f"{sampling_rate}\n".encode())
    ser_adc.flush()

    # Wait for 'R' from ADC
    while True:
        if ser_adc.in_waiting > 0:
            response = ser_adc.read(1).decode()
            if response == 'R':
                print("Received 'R' from ADC. ADC is recording.")
                ADC_ready = True
                break

    print("ADC started, receiving data...")

    # Create WAV file for ADC output
    output_filename = "output_v2.wav"
    # with wave.open(output_filename, 'wb') as output_file:
    #     output_file.setnchannels(1)  # Mono audio
    #     output_file.setsampwidth(2)  # 16-bit samples (2 bytes per sample)
    #     output_file.setframerate(sampling_rate)

    i = 0
    # recorded_samples = []

    while True:
        if ser_adc.in_waiting >= 2:  
            data = ser_adc.read(2)
            ADC_value = struct.unpack('<H', data)[0]
            print(ADC_value)  

            # # Convert to signed 16-bit format (for WAV compatibility)
            # signed_value = ADC_value - 32768  # Convert from 0-65535 to -32768 to 32767

            # # Store the sample
            # recorded_samples.append(signed_value)
            i += 1
            if i == 360000:
                break

        # Write all recorded samples to the WAV file
        # output_file.writeframes(np.array(recorded_samples, dtype=np.int16).tobytes())

    ser_adc.close()
    print("ADC recording completed. Saved as output_v2.wav.")

# Create ADC & DAC threads
thread_adc = threading.Thread(target=run_adc)
thread_dac = threading.Thread(target=run_dac)

# Start threads
thread_adc.start()
# thread_dac.start()

# Wait for completion
# thread_dac.join()
thread_adc.join()

import threading
import serial
import wave
import struct
import time
import numpy as np

# Global flag for stopping ADC when DAC is done
DAC_finished = False  
ADC_ready = False
DAC_PORT = "COM8"
ADC_PORT = "COM3"
BAUD_RATE = 1152000
WAV_FILE = "./wavefile/12.0kHz_1000Hz_sine.wav"

ADC_ready = threading.Event()
DAC_finished = threading.Event()

def run_dac():
    ser_dac = serial.Serial(DAC_PORT, baudrate=BAUD_RATE, timeout=0.5)  
    ser_dac.reset_input_buffer()  
    ser_dac.reset_output_buffer()

    # Read WAV file
    with wave.open(WAV_FILE, "rb") as wav:
        frame_rate = wav.getframerate()
        num_frames = wav.getnframes()
        raw_data = wav.readframes(num_frames)

    # Wait for ADC to be ready before sending SR
    print("[DAC] Waiting for ADC to be ready...", flush=True)
    ADC_ready.wait()  # Block until ADC is ready
    print("[DAC] ADC is ready, starting DAC...", flush=True)

    command = f"{frame_rate}\n"
    ser_dac.write(command.encode())  
    print(f"[DAC] Sent sampling rate to DAC: {frame_rate} Hz", flush=True)

    # Convert samples to little-endian 16-bit
    samples = [int.from_bytes(raw_data[i:i+2], byteorder="little", signed=True) + 32768
        for i in range(0, len(raw_data), 2)]
    
    # Step 2: Scale the amplitude
    scaled_samples = [int(s / 4) for s in samples]  # Prevent clipping

# Step 3: Shift to unsigned
    samples = [min(max(s + 32768, 0), 65535) for s in scaled_samples]


    # Send samples with handshaking
    chunk_size = 128
    index = 0
    while index < len(samples):
        if ser_dac.in_waiting > 0:
            ready_signal = ser_dac.read(1)  
            if ready_signal == b'R':
                chunk = b''.join(sample.to_bytes(2, 'little', signed=False) for sample in samples[index:index + chunk_size])
                ser_dac.write(chunk)
                index += chunk_size
            else:
                print(f"[DAC] Unexpected signal: {ready_signal.decode()}")
    DAC_finished.set()
    time.sleep(1)
    ser_dac.close()
    print("[DAC] DAC transmission completed.",flush=True)

def run_adc():
    ser_adc = serial.Serial(ADC_PORT, baudrate=BAUD_RATE, timeout=0.5)

    sampling_rate = 12000
    print("[ADC] Sending sampling rate to ADC...", flush=True)
    ser_adc.write(f"{sampling_rate}\n".encode())
    ser_adc.flush()

    # Wait for 'R' from ADC
    while True:
        if ser_adc.in_waiting > 0:
            response = ser_adc.read(1).decode()
            if response == 'R':
                print("[ADC] Received 'R' from ADC. ADC is recording.", flush=True)
                ADC_ready.set()
                break
    
    # Send 'S' to start ADC recording
    print("[ADC] Sending 'S' to start recording...", flush=True)
    ser_adc.write(b'S')
    ser_adc.flush()

    print("[ADC] ADC started, receiving data...", flush=True)

    # Create WAV file for ADC output
    output_filename = "output_v2.wav"
    with wave.open(output_filename, 'wb') as output_file:
        output_file.setnchannels(1)  # Mono audio
        output_file.setsampwidth(2)  # 16-bit samples (2 bytes per sample)
        output_file.setframerate(sampling_rate)

        i = 0
        recorded_samples = []
        while i < 360000:
            if ser_adc.in_waiting >= 2:  
                data = ser_adc.read(2)
                ADC_value = struct.unpack('<H', data)[0]
                # print("\n")
                print(ADC_value)  

                # # Convert to signed 16-bit format (for WAV compatibility)
                signed_value = ADC_value - 32768  # Convert from 0-65535 to -32768 to 32767

                # # Store the sample
                recorded_samples.append(signed_value)
                i += 1

            # Write all recorded samples to the WAV file
        output_file.writeframes(np.array(recorded_samples, dtype=np.int16).tobytes())

    ser_adc.close()
    # print("[ADC] ADC recording completed.")
    print("[ADC] ADC recording completed. Saved as output_v2.wav.")

# Create ADC & DAC threads
thread_adc = threading.Thread(target=run_adc)
thread_dac = threading.Thread(target=run_dac)

# Start threads
thread_adc.start()
thread_dac.start()

# Wait for completion
thread_adc.join()
thread_dac.join()


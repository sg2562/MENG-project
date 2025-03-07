import threading
import serial
import wave
import time
def run_dac():
    SERIAL_PORT = "COM5"
    BAUD_RATE = 1152000
    WAV_FILE = "sharp_square_50Hz.wav"

    ser = serial.Serial(SERIAL_PORT, baudrate=BAUD_RATE, timeout=0.1)
    ser_adc = serial.Serial("COM4")

    # Read WAV file
    with wave.open(WAV_FILE, "rb") as wav:
        frame_rate = wav.getframerate()
        raw_data = wav.readframes(wav.getnframes())

    ser.write(f"{frame_rate}\n".encode())  # Send sampling rate
    print(f"Sent sampling rate: {frame_rate} Hz")

    samples = [int.from_bytes(raw_data[i:i+2], byteorder="little", signed=False)
               for i in range(0, len(raw_data), 2)]
    
    ser_adc.reset_input_buffer()

    chunk_size = 128
    index = 0
    with open("adc_output.txt", "w") as f:
        while index < len(samples):
            if ser.in_waiting > 0:
                ready_signal = ser.read(1)  # Check if Teensy is ready
                if ready_signal == b'R':
                    chunk = samples[index:index + chunk_size]
                    for sample in chunk:
                        ser.write(sample.to_bytes(2, byteorder="little", signed=False))

                        # Read ADC
                        # time.sleep(0.001)

                        # PROBLEM!!! with reading
                        # highByte = ser_adc.read(1)
                        # lowByte = ser_adc.read(1)
                        # ADC_value = highByte[0] << 8 | lowByte[0]

                        # print(ADC_value)
                        # f.write(f"{ADC_value}\n")

                    index += len(chunk)
                else:
                    print(f"Unexpected signal received: {ready_signal}")

    ser.close()

# Run DAC & ADC in parallel
thread_dac = threading.Thread(target=run_dac)
thread_dac.start()
thread_dac.join()

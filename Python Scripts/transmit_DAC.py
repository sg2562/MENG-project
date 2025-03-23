import serial
import wave

SERIAL_PORT = "COM3"
BAUD_RATE = 1152000  # Irrelevant for USB Serial, kept for reference
WAV_FILE = "./wavefile/8.0kHz_100Hz_sine.wav"
# WAV_FILE = "square_10kHz_long.wav"

ser = serial.Serial(SERIAL_PORT, baudrate=BAUD_RATE, timeout=0.1)  # Timeout prevents blocking
ser.reset_input_buffer()
ser.reset_output_buffer()
# Read WAV file
with wave.open(WAV_FILE, "rb") as wav:
    num_channels = wav.getnchannels()
    sample_width = wav.getsampwidth()
    frame_rate = wav.getframerate()
    num_frames = wav.getnframes()
    raw_data = wav.readframes(num_frames)

command = f"{frame_rate}\n"  # Convert to string and add newline
ser.write(command.encode())  # Send to Arduino IDE
print(f"Sent sampling rate: {frame_rate} Hz")

samples = [int.from_bytes(raw_data[i:i+2], byteorder="little", signed=False)
           for i in range(0, len(raw_data), 2)]

# Send samples with handshaking
chunk_size = 512
index = 0
while index < len(samples):
    # ser.reset_input_buffer()
    if ser.in_waiting > 0:
        ready_signal = ser.read(1)  # Check if Teensy is ready
        if ready_signal == b'R':
            chunk = b''.join(sample.to_bytes(2, 'little', signed=False) for sample in samples[index:index + chunk_size])
            ser.write(chunk)
            index += chunk_size
        
        # if ready_signal == b'R':
        #     # print(ready_signal)
        #     chunk = samples[index:index + chunk_size]  # Send in chunks
        #     for sample in chunk:
        #         ser.write(sample.to_bytes(2, byteorder="little", signed=False))
        #         # ser.write(0xFFFF)
        #     index += len(chunk)
        else:
            print(f"Ready signal not expected: {ready_signal.decode()}")

ser.close()
print(f"{frame_rate} sampling rate file transmittion finished")

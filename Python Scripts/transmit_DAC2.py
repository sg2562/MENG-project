import wave
import serial
import struct
import time

USB_SERIAL_PORT = "COM5"
BAUD_RATE = 12000000  # Teensy USB Serial 速度可达 12Mbit/s

def send_wav_to_teensy(filename):
    try:
        print(f"Opening serial port {USB_SERIAL_PORT}...")
        ser = serial.Serial(USB_SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # 等待 Teensy 启动
        print("Serial port opened.")
        
        with wave.open(filename, 'rb') as wav_file:
            num_channels = wav_file.getnchannels()
            frame_rate = wav_file.getframerate()
            num_frames = wav_file.getnframes()
            
            print(f"Channels: {num_channels}, Sample Rate: {frame_rate}Hz, Frames: {num_frames}")

            # 发送 WAV 采样率给 Teensy
            ser.write(struct.pack('<I', frame_rate))
            time.sleep(0.1)  # 等待 Teensy 处理
            
            # 逐个发送样本，并等待 Teensy 响应
            bytes_sent = 0
            for _ in range(num_frames):
                frame_data = wav_file.readframes(1)  # 读取 16-bit PCM
                ser.write(frame_data)  # 发送样本
                ser.flush()  # 确保数据立即发送
                time.sleep(1 / frame_rate)  # 控制发送速率匹配采样率
                bytes_sent += len(frame_data)
                
                # 定期打印进度
                if _ % 1000 == 0:
                    print(f"Sent {_}/{num_frames} frames ({(bytes_sent / num_frames / 2) * 100:.2f}% done)")

        print("WAV successfully sent!")
        ser.close()
    except serial.SerialException as e:
        print(f"Error: unable to open {USB_SERIAL_PORT}. {e}")
    except FileNotFoundError:
        print(f"Error: can't find wavefile {filename}")
    except Exception as e:
        print(f"Unexpected error: {e}")

send_wav_to_teensy("square_100Hz.wav")

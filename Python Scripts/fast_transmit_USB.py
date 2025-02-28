# import os
# os.environ['PYUSB_DEBUG'] = 'debug'

import usb.core
import usb.util
# import struct
# import numpy as np
# import soundfile as sf
# import time

dev = usb.core.find(idVendor=0x16C0, idProduct=0x0483)
if dev is None:
    raise ValueError('Device not found')
else:
    print("device found")

dev.configurations()
# Set the correct interface (Use Interface 2, not 0)
INTERFACE_NUMBER = 0  # Teensy Bulk Transfer Interface

# Claim Interface 2 (Bulk Transfer)
usb.util.claim_interface(dev, INTERFACE_NUMBER)

EP_OUT = 0x3
EP_IN = 0x84

# WAV_FILE = "square_44.1kHz.wav"

# # Load WAV File
# data, sample_rate = sf.read(WAV_FILE, dtype="int16")

# # Convert stereo to mono if needed
# if len(data.shape) > 1:
#     data = data.mean(axis=1).astype(np.int16)

# # Ensure proper format
# samples = np.clip(data, -32768, 32767)  # Ensure 16-bit range

# # Send Sampling Rate
# def send_sampling_rate(rate):
#     """Send the WAV file's sampling rate to Teensy via USB Bulk"""
#     cmd_packet = struct.pack("<BI", 0xAA, rate) + b'\x00' * 59
#     dev.write(EP_OUT, cmd_packet, timeout=100)
#     print(f"Sent Sampling Rate: {rate} Hz")
#     time.sleep(1)

# # Wait for Ready Signal from Teensy
# def wait_for_ready_signal():
#     """Wait for Teensy to send 'R' indicating it's ready for more data"""
#     while True:
#         try:
#             response = dev.read(EP_IN, 1, timeout=500)  # Read 1 byte
#             if response[0] == ord('R'):
#                 print("Teensy Ready - Sending Data...")
#                 return
#         except usb.core.USBError:
#             pass  # Ignore timeout errors

# # Send WAV Audio Data via USB Bulk Transfer
# def send_audio_data(samples):
#     """Send audio samples (16-bit) to Teensy using USB Bulk Transfer"""
#     index = 0
#     chunk_size = 128  # Sending 128 samples at a time (256 bytes per packet)

#     while index < len(samples):
#         wait_for_ready_signal()  # Wait for 'R' before sending more data

#         chunk = samples[index:index + chunk_size]
#         packet = struct.pack("<B", 0xDD)  # DAC Data Packet Header

#         for sample in chunk:
#             packet += struct.pack("<H", sample)  # Convert 16-bit sample to bytes
        
#         packet += b'\x00' * (512 - len(packet))  # Pad to 512 bytes
#         dev.write(EP_OUT, packet, timeout=100)
        
#         index += chunk_size
#         print(f"Sent {index}/{len(samples)} samples.")

# # Main Function
# def main():
#     send_sampling_rate(sample_rate)
#     send_audio_data(samples)
#     print("Playback complete!")

# if __name__ == "__main__":
#     main()

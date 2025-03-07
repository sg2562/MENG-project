import wave
import numpy as np
import matplotlib.pyplot as plt
import scipy
from scipy.io import wavfile

filename = "./wavefile/1.0kHz_100Hz_square.wav"

# check samples, total samples, 
with wave.open(filename, 'rb') as wav_file:
    sample_rate = wav_file.getframerate()
    num_frames = wav_file.getnframes()
    sample_width = wav_file.getsampwidth()

    print(f"Sample Rate: {sample_rate} Hz")
    print(f"Total samples: {num_frames}")
    print(f"Resolution: {sample_width*8}-bit")

# check the inside wave frequency
def inside_wave_freq():
    Fs,Y = wavfile.read(filename)
    Y = Y/np.iinfo(np.int16).max
    N = len(Y)

    fft = np.abs(scipy.fft.fft(Y))[:N//2]
    fft_freq = scipy.fft.fftfreq(N, d = 1/Fs)[:N//2]

    # detect_freq = fft_freq[np.argmax(fft)] # for sine wave
    peak_index = np.argmax(fft[1:]) + 1  # Ignore DC component
    detect_freq = fft_freq[peak_index]
    print(f"wave frequency inside wave file: {detect_freq}")

def plot_wavfile():
    Fs, Y = wavfile.read(filename)

    # scaling the samples in Y to be in [−1, 1]
    Y = Y/np.iinfo(np.int16).max 
    time = np.arange(len(Y)) / Fs

    plt.figure(figsize=(10, 4))
    plt.plot(time, Y, label="Audio Signal")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Amplitude")
    plt.title(f"Waveform (Sampling Rate: {Fs} Hz)")
    plt.xlim((0,0.2))
    plt.legend()
    plt.grid()
    plt.show()

if __name__ == "__main__":
    inside_wave_freq()
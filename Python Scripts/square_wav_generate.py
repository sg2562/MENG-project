import numpy as np
from scipy.io import wavfile as wav

def gen_sharp_square_wave():
    # Set sampling rate and frequency
    sample_rate = 8000
    frequency = 400
    duration = 10
    
    # Compute total number of samples
    num_samples = int(sample_rate * duration)
    
    # Compute samples per cycle (one period of the square wave)
    samples_per_cycle = sample_rate // frequency

    # Create one period of the square wave (half high, half low)
    half_cycle = samples_per_cycle // 2
    square_wave = np.tile(
        np.concatenate((np.ones(half_cycle), np.zeros(half_cycle))),
        num_samples // samples_per_cycle
    )

    # Scale to 16-bit PCM format
    max_int16 = np.iinfo(np.int16).max
    scaled_wave = (square_wave * max_int16).astype(np.int16)

    # Save as a WAV file
    wav.write(f'{sample_rate/1000}kHz_{frequency}Hz_{duration}s.wav', sample_rate, scaled_wave)
    print("Created successfully.")

if __name__ == "__main__":
    gen_sharp_square_wave()

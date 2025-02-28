import numpy as np
from scipy.io import wavfile as wav

def gen_pulse_CD():
    # Three pulses 44.1 kHz, 


    # Create the base vector: 44099 zeros followed by a 1
    pulse_position = 44099  # Position of the impulse (44100th sample)
    x = np.zeros(pulse_position + 1)
    x[-1] = 1.0

    # Repeat the vector multiple times to create spaced impulses
    num_repeats = 3
    x_repeated = np.tile(x, num_repeats)

    # Scale and convert to 32-bit integers for WAV format
    # max_int32 = np.iinfo(np.int32).max  # Maximum 32-bit integer value
    # scaled_signal = (x_repeated * max_int32).astype(np.int32)
    max_int16 = np.iinfo(np.int16).max  # 16 bit resolution
    scaled_signal = (x_repeated * max_int16).astype(np.int16)
    # Save as a WAV file
    wav.write('imp16.wav', 44100, scaled_signal)

    print("imp16.wav created successfully.")

# def gen_square_CD():

if __name__ == "__main__":
    gen_pulse_CD()
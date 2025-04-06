import numpy as np
import scipy.io.wavfile as wav
import matplotlib.pyplot as plt
from numpy import polyfit

def detect_edges(signal, threshold=0):
    """Detects rising and falling edges in a square wave signal."""
    edges = np.where(np.diff(np.sign(signal - threshold)) != 0)[0]  # Find transition points
    return edges

def compute_drift(input_edges, output_edges, sample_rate):
    """Computes drift between input and output waveforms."""
    min_len = min(len(input_edges), len(output_edges))
    drift_samples = output_edges[:min_len] - input_edges[:min_len]
    drift_time = drift_samples / sample_rate  # Convert to seconds
    return drift_samples, drift_time


def square_wave_check():
    # Read WAV files
    sample_rate_in, input_signal = wav.read(input_wavfile)
    sample_rate_out, output_signal = wav.read(output_wavfile)
    # Ensure same sample rate and convert to mono if stereo
    assert sample_rate_in == sample_rate_out, "Sample rates must match!"
    # if input_signal.ndim > 1:
    #     input_signal = np.mean(input_signal, axis=1)  # Convert to mono
    # if output_signal.ndim > 1:
    #     output_signal = np.mean(output_signal, axis=1)

    # Detect rising and falling edges
    input_edges = detect_edges(input_signal)
    output_edges = detect_edges(output_signal)

    # Compute drift
    drift_samples, drift_time = compute_drift(input_edges, output_edges, sample_rate_in)

    # Plot drift over time
    plt.figure(figsize=(10, 5))
    plt.plot(drift_time, drift_samples, marker='o', linestyle='-', label="Drift (samples)")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Drift (samples)")
    plt.title("Edge Timing Drift Analysis")
    plt.legend()
    plt.grid()
    plt.show()

    # Print summary statistics
    print(f"Max drift: {np.max(drift_samples)} samples")
    print(f"Mean drift: {np.mean(drift_samples)} samples")
    print(f"Standard deviation of drift: {np.std(drift_samples)} samples")
    print(f"Detected {len(input_edges)} edges in input")
    print(f"Detected {len(output_edges)} edges in output")
    print(f"Last detected edge time: {input_edges[-1] / sample_rate_in:.2f} seconds")

def detect_zero_crossings(signal):
    """Detect zero crossings with interpolation."""
    zero_crossings = []
    for i in range(1, len(signal)):
        if signal[i - 1] <= 0 < signal[i]:
            y0, y1 = signal[i - 1], signal[i]
            x_cross = i - 1 - y0 / (y1 - y0)
            zero_crossings.append(x_cross)
    return np.array(zero_crossings)


from scipy.signal import correlate

def align_signals(ref, target):
    """Align two signals using cross-correlation."""
    corr = correlate(target, ref, mode='full')
    lag = np.argmax(corr) - len(ref) + 1
    aligned = target[lag:] if lag >= 0 else np.pad(target, (abs(lag), 0), mode='constant')
    print(f"Aligned signals with lag offset: {lag} samples")
    return aligned, lag


def sine_wave_drift_check():
    # Read WAV files
    sample_rate_in, input_signal = wav.read(input_wavfile)
    sample_rate_out, output_signal = wav.read(output_wavfile)
    assert sample_rate_in == sample_rate_out, "Sample rates must match!"
    sample_rate = sample_rate_in

    # Convert stereo to mono
    if input_signal.ndim > 1:
        input_signal = input_signal.mean(axis=1)
    if output_signal.ndim > 1:
        output_signal = output_signal.mean(axis=1)

    # Align output to input using cross-correlation
    output_signal_aligned, lag = align_signals(input_signal[:50000], output_signal[:70000])

    # Detect zero crossings
    input_crossings = detect_zero_crossings(input_signal)
    output_crossings = detect_zero_crossings(output_signal_aligned)

    # Match lengths
    min_len = min(len(input_crossings), len(output_crossings))
    input_crossings = input_crossings[:min_len]
    output_crossings = output_crossings[:min_len]

    # Compute drift
    drift_samples = output_crossings - input_crossings
    drift_time = drift_samples / sample_rate

    # Plot drift
    plt.figure(figsize=(10, 5))
    plt.plot(input_crossings / sample_rate, drift_samples)
    plt.title("Drift Over Time")
    plt.xlabel("Time (s)")
    plt.ylabel("Drift (samples)")
    plt.grid(True)
    plt.show()

    # Print stats
    print(f"Max drift: {np.max(drift_samples):.3f} samples")
    print(f"Mean drift: {np.mean(drift_samples):.3f} samples")
    print(f"Std deviation: {np.std(drift_samples):.3f} samples")
    print(f"Detected {len(input_crossings)} crossings")

    # Estimate drift rate and ppm
    t = input_crossings[:len(drift_samples)] / sample_rate
    drift_trend = np.polyfit(t, drift_samples, 1)
    slope = drift_trend[0]  # samples/sec
    signal_freq = 1000  # Adjust as needed
    samples_per_period = sample_rate / signal_freq
    rel_freq_error = slope / samples_per_period
    ppm = rel_freq_error * 1e6

    print(f"Drift rate: {slope:.3f} samples/sec")
    print(f"Estimated clock mismatch: {ppm:.2f} ppm")


if __name__ == "__main__":
    input_wavfile = "./wavefile/12.0kHz_1000Hz_sine.wav"
    output_wavfile = "output_12k_1000.wav"
    # square_wave_check()
    sine_wave_drift_check()

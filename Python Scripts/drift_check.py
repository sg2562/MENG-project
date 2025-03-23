import numpy as np
import scipy.io.wavfile as wav
import matplotlib.pyplot as plt

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


if __name__ == "__main__":
    input_wavfile = "./wavefile/12.0kHz_6000Hz_square.wav"
    output_wavfile = "output.wav"
    square_wave_check()

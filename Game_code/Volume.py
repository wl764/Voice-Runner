import sounddevice as sd
import numpy as np
import time
import frc

# Audio sampling parameters
SAMPLE_RATE = 44100  # Sample rate, 44.1 kHz
DURATION = 0.07  # Duration of each sample (seconds) to achieve 20 frames per second
N = int(SAMPLE_RATE * DURATION)  # Number of sample points per recording
LOW_FREQ_THRESHOLD = 50  # Set the low-frequency cutoff threshold (Hz)
HIGH_FREQ_THRESHOLD = 700  # Set the high-frequency cutoff threshold (Hz)
AMPLITUDE_THRESHOLD = 0.01  # Set the amplitude threshold for volume

# OpenCV window initialization
max_fft_amplitude = 1e-10  # Initialize with a very small value

# Global variable to store the max FFT amplitude observed so far



def linear_decay(array):
    length = len(array)
    if length == 0:
        return array  # 如果数组为空，直接返回

    # 创建一个线性权重，从 1 到 0.9
    weights = np.linspace(1, 0.1, length)

    # 对数组的每个元素应用线性权重
    modified_array = array * weights
    return modified_array


def apply_window_function(audio_data):
    # Apply a Hamming window to reduce boundary effects
    window = np.hamming(len(audio_data))
    return audio_data * window

def get_fft(audio_data):
    global max_fft_amplitude, max_amplitude_freq

    # Remove DC component by subtracting the mean of the audio data
    audio_data = audio_data - np.mean(audio_data)

    # Apply the window function to reduce boundary effects
    audio_data = apply_window_function(audio_data)

    # Compute the FFT
    fft_data = np.abs(np.fft.fft(audio_data))[:N // 2]

    # Compute the corresponding frequency array
    freqs = np.fft.fftfreq(N, 1 / SAMPLE_RATE)[:N // 2]

    # Mask frequencies outside the 50-400 Hz range
    mask = (freqs >= LOW_FREQ_THRESHOLD) & (freqs <= HIGH_FREQ_THRESHOLD)
    fft_data = fft_data[mask]
    fft_data = linear_decay(fft_data)
    freqs = freqs[mask]

    # Update the global max FFT amplitude and frequency if there are valid frequencies
    if len(fft_data) > 0:
        max_fft_amplitude = max(max_fft_amplitude, np.max(fft_data))
        max_amplitude_index = np.argmax(fft_data)
        frc.max_amplitude_freq_1 = freqs[max_amplitude_index]
        frc.max_amplitude_freq_2 = frc.max_amplitude_freq_1

    return fft_data, freqs


def Get_max_amp():
# Real-time audio recording and display
    print("fft start")

    try:
        last_print_time = time.time()
        while True:
            # Record audio
            audio_data = sd.rec(frames=N, samplerate=SAMPLE_RATE, channels=1, dtype='float32')
            sd.wait()  # Wait for recording to finish
            audio_data = audio_data.flatten()  # Flatten the data to one dimension

            # Check if the volume exceeds the threshold
            if np.max(np.abs(audio_data)) < AMPLITUDE_THRESHOLD:
                frc.max_amplitude_freq_1 = LOW_FREQ_THRESHOLD
                frc.max_amplitude_freq_2 = frc.max_amplitude_freq_1# Set to low frequency threshold if volume is below threshold

            else:
                # Get and plot FFT data
                fft_data, freqs = get_fft(audio_data)

            # Print the max amplitude frequency
            current_time = time.time()
            if current_time - last_print_time >= 0.5:
                print(f"Max amplitude frequency: {frc.max_amplitude_freq_1} Hz")
                last_print_time = current_time
    except KeyboardInterrupt:
        exit(0)

            # Exit if the 'q' key is pressed
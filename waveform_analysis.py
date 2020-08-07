import numpy as np
import matplotlib.pyplot as plt
from apply_noise_method import ApplyNoiseMethod
from waveform_signal_generator import \
    (
    add_noise_to_waveform,
    _multi_sine_waveforms,
    create_signal_with_load_transients,
    create_realistic_signal,
)
import pywt

SAMPLES_PER_SECOND = 150
DURATION_SEC = 15
AMPLITUDES = [1, 2, 3]
FREQUENCIES_HZ = [1, 5, 15]


def estimate_autocorrelation(waveform_samples, plot=False):
    N = len(waveform_samples)
    Rx = np.zeros(N)
    for l in range(N):
        Rx[l] = np.mean([waveform_samples[j + l] * waveform_samples[j] for j in range(N - l)])

    if plot:
        plt.plot([i for i in range(len(Rx))], Rx)
        plt.title("Autocorrelation estimation")
        plt.xlabel("samples")
        plt.show()

    return Rx


def estimate_spectrum(Rx, plot=False):
    freqs = np.fft.fftshift(np.fft.fftfreq(len(Rx)))
    Abs_Sx1_eiw = np.abs(np.fft.fftshift(np.fft.fft(Rx)))

    if plot:
        plt.plot(freqs, Abs_Sx1_eiw)
        plt.title("Spectrum corrologram estimation")
        plt.xlabel("Freqs[1/sample]")
        plt.show()

    return freqs, Abs_Sx1_eiw


def extract_delta_freqs_in_spectrum(freqs, Abs_Sx1_eiw):
    zero_index = list(freqs).index(0)
    freqs = freqs[zero_index:]
    Abs_Sx1_eiw = Abs_Sx1_eiw[zero_index:]

    return np.array([freq for (freq, value) in zip(freqs, Abs_Sx1_eiw) if (value > 500)])  # check


def find_period(waveform_samples, threshold=0.000001):
    Rx = estimate_autocorrelation(waveform_samples)
    freqs, Abs_Sx1_eiw = estimate_spectrum(Rx, plot=True)

    freqs_of_deltas = extract_delta_freqs_in_spectrum(freqs, Abs_Sx1_eiw)
    print(freqs_of_deltas)
    i = 1
    while True:
        if all(np.abs(np.rint((i * freqs_of_deltas)) - (i * freqs_of_deltas)) <= threshold):
            return i
        i += 1


signal_with_fail_trans, signal_with_load_trans_only, indices_of_load_trans = create_realistic_signal(
    num_of_load_trans=1, duration=DURATION_SEC, samples_per_second=SAMPLES_PER_SECOND)

plt.plot([i for i in range(len(signal_with_fail_trans))], signal_with_fail_trans)
plt.plot([i for i in range(len(signal_with_fail_trans))], signal_with_load_trans_only)
plt.title(f"Multi sine wave with single load transient and also single failure transient")
plt.xticks(indices_of_load_trans, indices_of_load_trans)
plt.show()
#
# plt.title(f"Multi sine wave with single load transient and failure transient")
# plt.xticks(diff_indices, diff_indices)
# plt.show()

#
# wavelet_without_trans = np.array(pywt.dwt(signal_without_trans, wavelet='haar'))
# wavelet_with_trans = np.array(pywt.dwt(signal_with_trans, wavelet='haar'))
#
# for j in range(len(wavelet_with_trans[0])):
#     if np.abs(wavelet_with_trans[1][j] - wavelet_without_trans[1][j]) > 5:
# print(f"d values without trans are {wavelet_without_trans[1][j]} in index={j}")
# print(f"d values with trans are {wavelet_with_trans[1][j]}  in index={j}")

# matrix = pywt.dwt([1, 2, 3, 4], 'haar')
# result = pywt.idwt(cA=matrix[0], cD=matrix[1], wavelet='haar')
# print(np.matrix(matrix))

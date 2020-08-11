import matplotlib.pyplot as plt
import numpy as np
from pywt import (
    wavedec,
    waverec,
    families,
    wavelist,
)

from SignalPlotter.SignalPlotter import SignalPlotter
from WaveletsManager.wavelets_manager_constats import SIGNAL_EXTENSIONS, CSS_COLORS, TRANSIENT_DETECTOR_SENSITIVITY
from WaveletsManager.wavelets_manager_exceptions import ReconstructionError, SignalExtensionError, WaveletFamilyError
from global_constants import FREQ_DOMAIN_WINDOW_SIZE, TIME_DOMAIN_WINDOW_SIZE


class WaveletsManager:
    def __init__(self, signal):
        self.signal = signal
        self.coefficients = None
        self.wavelets_family = None
        self.signal_extension = None
        self.decompose_level = None

    def decompose(self, signal_extension='symmetric', wavelets_family='haar', decompose_level=3):
        self.signal_extension, self.wavelets_family, self.decompose_level = signal_extension, wavelets_family, decompose_level
        if signal_extension not in SIGNAL_EXTENSIONS:
            raise SignalExtensionError

        if wavelets_family not in wavelist():
            raise WaveletFamilyError(wavelist())

        coefficients = wavedec(data=self.signal, wavelet=wavelets_family, mode=signal_extension, level=decompose_level)
        self.coefficients = coefficients.copy()
        return coefficients

    def reconstruct(self, coefficients=None):
        coefficients = coefficients or self.coefficients

        required_properties = [coefficients, self.wavelets_family, self.signal_extension]

        if all(required_properties):
            reconstructed_signal = waverec(coeffs=coefficients, wavelet=self.wavelets_family,
                                           mode=self.signal_extension)
            return reconstructed_signal
        else:
            raise ReconstructionError(required_properties)

    @staticmethod
    def get_available_families():
        return families()

    def _get_moving_average_high_freq(self, coefficients, window_size):
        # Note that this function doesn't return exactly the moving average but first each value is squared
        coefficients = coefficients or self.coefficients
        # We divide by factor of 2 since our highest freq coefficients halved in size
        # NOTE: If the transient is a long one, we will need a longer window_size
        window_size = window_size or FREQ_DOMAIN_WINDOW_SIZE

        highest_freq_coefficients = coefficients[-1]
        moving_avg_kernel = np.ones(window_size) / window_size

        abs_high_freq_coefficients = np.square(highest_freq_coefficients)
        moving_average_high_freq = np.convolve(abs_high_freq_coefficients, moving_avg_kernel, mode='same')

        SignalPlotter.plot_signal(moving_average_high_freq, 'moving_average', title='Moving average', linewidth=6,
                                  show=False)

        return moving_average_high_freq

    def is_transient_exist(self, coefficients=None, window_size=None):
        moving_average_high_freq = self._get_moving_average_high_freq(coefficients, window_size)
        return (np.mean(moving_average_high_freq) / np.max(moving_average_high_freq)) < TRANSIENT_DETECTOR_SENSITIVITY

    def _extract_transient_interval(self, coefficients, window_size):
        moving_average_high_freq = self._get_moving_average_high_freq(coefficients, window_size)
        transient_indices = np.where(
            moving_average_high_freq > (np.max(moving_average_high_freq) - np.mean(moving_average_high_freq)))

        transient_interval_in_time_domain = (transient_indices[0][0] * 2, transient_indices[0][-1] * 2)

        return transient_interval_in_time_domain

    def get_signal_before_after_transient(self, gap_from_transient, coefficients=None, window_size=None):
        transient_interval_in_time_domain = self._extract_transient_interval(coefficients, window_size)
        print(f'extracted trans indices:\n{transient_interval_in_time_domain}')
        signal_before = self.signal[
                        transient_interval_in_time_domain[0] - gap_from_transient - TIME_DOMAIN_WINDOW_SIZE:
                        transient_interval_in_time_domain[0] - gap_from_transient]
        signal_after = self.signal[
                       transient_interval_in_time_domain[1] + gap_from_transient:
                       transient_interval_in_time_domain[1] + gap_from_transient + TIME_DOMAIN_WINDOW_SIZE]

        return signal_before, signal_after

    def plot_decompose_summary(self, save_name=None, show=True):
        length = len(self.signal)
        reconstructed_signal = self.reconstruct()[:length]

        x_values = np.arange(length)
        num_plots = self.decompose_level + 3

        plt.figure(figsize=(30, 20))

        # 3 here is because we also with to plot cA,Original Signal, Reconstructed Signal
        plt.subplot(num_plots, 1, 1)
        plt.plot(x_values, self.signal, color=CSS_COLORS[0])
        plt.xlabel('Samples')
        plt.ylabel('Amplitude')
        plt.title('Original Signal')

        plt.subplot(num_plots, 1, 2)
        plt.plot(self.coefficients[0], color=CSS_COLORS[1])
        plt.xlabel('Samples')
        plt.ylabel('cA')
        # plt.title('Approximation Coeff. (cA)')

        for i in range(2, self.decompose_level + 2):
            plt.subplot(num_plots, 1, i + 1)
            plt.plot(self.coefficients[i - 1], color=CSS_COLORS[i % len(CSS_COLORS)])
            plt.xlabel('Samples')
            plt.ylabel(f'cD - level {self.decompose_level - (i - 2)}')
            # plt.title('Detailed Coeff. (cD)')

        plt.subplot(num_plots, 1, num_plots)
        plt.plot(x_values, reconstructed_signal, color=CSS_COLORS[(i + 1) % len(CSS_COLORS)])
        plt.xlabel('Samples')
        plt.ylabel('Amplitude')
        plt.title('Reconstructed Signal')
        if not save_name:
            plt.savefig('summary.png')
        else:
            plt.savefig(f'{save_name}.png')
        if show:
            plt.show()
        else:
            plt.close()

    def plot_coefficients(self):
        raise NotImplementedError

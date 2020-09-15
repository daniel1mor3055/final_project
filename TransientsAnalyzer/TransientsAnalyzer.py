import numpy as np

from SignalPlotter.SignalPlotter import SignalPlotter
from SignalSimilaritiesEstimator.SignalSimilaritiesEstimator import SignalSimilaritiesEstimator
from Transient.Transient import Transient, FailTransient, LoadTransient
from WaveletsManager.WaveletsManager import WaveletsManager
from WaveletsManager.wavelets_manager_constats import (
    CSS_COLORS,
    MOVING_AVG_THRESH
)
from global_constants import (
    FREQ_DOMAIN_WINDOW_SIZE,
    TIME_DOMAIN_WINDOW_SIZE, FAIL_LOAD_CLASSIFICATION_THRESH, TRIAL_NAME
)


class TransientsAnalyzer:
    @staticmethod
    def _get_moving_average_high_freq(coefficients, window_size):
        # Note that this function doesn't return exactly the moving average but first each value is squared
        # We divide by factor of 2 since our highest freq coefficients halved in size
        # NOTE: If the transient is a long one, we will need a longer window_size
        window_size = window_size or FREQ_DOMAIN_WINDOW_SIZE

        highest_freq_coefficients = coefficients[-1]
        moving_avg_kernel = np.ones(window_size) / window_size

        abs_high_freq_coefficients = np.square(highest_freq_coefficients)
        moving_average_high_freq = np.convolve(abs_high_freq_coefficients, moving_avg_kernel, mode='same')

        # TODO-need to be remove
        # SignalPlotter.plot_signal(moving_average_high_freq, f'{TRIAL_NAME}_moving_average',
        #                           title=f'{TRIAL_NAME}_Moving Average',
        #                           color=CSS_COLORS[1],
        #                           linewidth=6, show=False)

        return moving_average_high_freq

    @staticmethod
    def is_transient_exist(coefficients=None, window_size=None):
        window_size = window_size or FREQ_DOMAIN_WINDOW_SIZE

        return TransientsAnalyzer._extract_transients(coefficients, window_size) != []

    @staticmethod
    def _extract_transients_intervals(transients_indices):
        # The multiplication by factor of 2 is due to the fact that we wish to get the result in time domain
        # instead of in highest frequency domain
        transients_start_indices, transients_end_indices = list(), list()
        for i in range(1, len(transients_indices)):
            if transients_indices[i] == 1 and transients_indices[i - 1] == 0:
                transients_start_indices.append(i * 2)
            if transients_indices[i] == 0 and transients_indices[i - 1] == 1:
                transients_end_indices.append(i * 2)

        return list(zip(transients_start_indices, transients_end_indices))

    @staticmethod
    def _extract_transients(coefficients, window_size):
        moving_average_high_freq = TransientsAnalyzer._get_moving_average_high_freq(coefficients, window_size)
        bool_transients_indices = moving_average_high_freq > MOVING_AVG_THRESH

        transients_intervals_in_time_domain = TransientsAnalyzer._extract_transients_intervals(bool_transients_indices)

        return moving_average_high_freq, transients_intervals_in_time_domain

    @staticmethod
    def _get_signal_before_after_transients(signal, gap_from_transient, transients_intervals_in_time_domain):
        signals_before_transients = list()
        signals_after_transients = list()
        print(f'extracted trans indices:\n{transients_intervals_in_time_domain}')
        for interval in transients_intervals_in_time_domain:
            signal_before = signal[
                            interval[0] - gap_from_transient - TIME_DOMAIN_WINDOW_SIZE:interval[0] - gap_from_transient]
            signal_after = signal[
                           interval[1] + gap_from_transient:interval[1] + gap_from_transient + TIME_DOMAIN_WINDOW_SIZE]
            signals_before_transients.append(signal_before)
            signals_after_transients.append(signal_after)

        return signals_before_transients, signals_after_transients

    @staticmethod
    def _get_reconstrcuted_transient(coefficients, wavelets_family, transient_intervals_in_time_domain):
        current_transient_start, current_transient_finish = transient_intervals_in_time_domain
        new_coeffs = [[], []]

        new_coeffs[-1] = coefficients[-1][current_transient_start // 2:current_transient_finish // 2]
        new_coeffs[0] = np.zeros(len(new_coeffs[1]))

        reconstructed_transient = WaveletsManager.reconstruct(coefficients=new_coeffs, wavelets_family=wavelets_family)
        return reconstructed_transient

    @staticmethod
    def analyze(signal, coefficients, wavelets_family, window_size=None):
        transients = list()
        moving_average_high_freq, transients_intervals_in_time_domain = TransientsAnalyzer._extract_transients(
            coefficients, window_size)

        signals_before_transients, signals_after_transients = \
            TransientsAnalyzer._get_signal_before_after_transients(signal=signal, gap_from_transient=0,
                                                                   transients_intervals_in_time_domain=transients_intervals_in_time_domain)

        for index, before_after_signals in enumerate(list(zip(signals_before_transients, signals_after_transients))):
            before_signal, after_signal = before_after_signals
            cross_correlation = SignalSimilaritiesEstimator.align_and_get_cross_correlation(before_signal, after_signal)
            energy_of_signal_before = np.sum(np.square(before_signal))
            lower, bigger = min(abs(cross_correlation), energy_of_signal_before), \
                            max(abs(cross_correlation), energy_of_signal_before)

            if lower / bigger > FAIL_LOAD_CLASSIFICATION_THRESH:
                reconstructed_transient = \
                    TransientsAnalyzer._get_reconstrcuted_transient(coefficients=coefficients,
                                                                    wavelets_family=wavelets_family,
                                                                    transient_intervals_in_time_domain=
                                                                    transients_intervals_in_time_domain[index])
                transients.append(
                    FailTransient(indices=transients_intervals_in_time_domain[index],
                                  time_domain_samples=reconstructed_transient))
            else:
                transients.append(LoadTransient(indices=transients_intervals_in_time_domain[index]))

        return moving_average_high_freq, transients

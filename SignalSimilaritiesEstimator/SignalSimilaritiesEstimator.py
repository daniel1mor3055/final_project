import numpy as np

from global_constants import TIME_DOMAIN_WINDOW_SIZE


class SignalSimilaritiesEstimator:
    @staticmethod
    def align_and_get_cross_correlation(signal_a, signal_b):
        rolled_signal = signal_b
        max_correlation_results = []
        for i in range(TIME_DOMAIN_WINDOW_SIZE):
            rolled_signal = np.roll(rolled_signal, 1)
            corrleation = np.correlate(signal_a, rolled_signal, 'full')
            max_correlation_results.append(np.max(corrleation))

        return np.max(np.asarray(max_correlation_results))

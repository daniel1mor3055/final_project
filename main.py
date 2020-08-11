import numpy as np

from SignalGenerator.SignalGenerator import SignalGeneratorBuilder
from SignalPlotter.SignalPlotter import SignalPlotter
from SignalSimilaritiesEstimator.SignalSimilaritiesEstimator import SignalSimilaritiesEstimator
from WaveletsManager.WaveletsManager import WaveletsManager
from global_constants import (
    BASE_FREQUENCY,
    SAMPLES_PER_SECOND,
    FAIL_LOAD_CLASSIFICATION_THRESH
)

if __name__ == '__main__':
    # Note that the num of base_amplitudes determines the number of load transients
    # TODO add shuffling to harmonics
    # Even harmonics are much lower than odd harmonics in most cases
    # TODO support more than one transient
    signal_generator = SignalGeneratorBuilder(). \
        with_base_params. \
        base_amplitudes([5]). \
        base_frequency(BASE_FREQUENCY). \
        num_diff_harmonics(2). \
        with_noise_params. \
        mean(0). \
        var(0.5). \
        with_sampling_params. \
        duration(2). \
        samples_per_second(SAMPLES_PER_SECOND). \
        with_fail_transient_params. \
        mean_fail_trans(0). \
        var_fail_trans(3). \
        max_failure_trans_samples(400). \
        min_failure_trans_samples(200). \
        gap_from_start_end_samples(2000). \
        with_load_transient_params. \
        mean_load_trans(0). \
        var_load_trans(0.5). \
        samples_to_apply_noise(200).build()

    counter_mistakes = 0
    # mistaken_signals = []
    for i in range(1):
        generated_signal = signal_generator.generate()
        wmanager_generated_signal = WaveletsManager(generated_signal)
        coefficients = wmanager_generated_signal.decompose(signal_extension='symmetric', wavelets_family='db4',
                                                           decompose_level=1)
        wmanager_generated_signal.plot_decompose_summary(show=False)
        print(f'fail trans indices are:\n{signal_generator._fail_trans_indices}')

        # TODO need to create a function here that detect if there exist a transient
        if not wmanager_generated_signal.is_transient_exist():
            print("Transient doesn't exist")
            exit()

        signal_before, signal_after = wmanager_generated_signal.get_signal_before_after_transient(
            gap_from_transient=100)

        cross_correlation = SignalSimilaritiesEstimator.align_and_get_cross_correlation(signal_before, signal_after)
        energy_of_signal_before = np.sum(np.square(signal_before))

        lower, bigger = min(abs(cross_correlation), energy_of_signal_before), \
                        max(abs(cross_correlation), energy_of_signal_before)

        if lower / bigger > FAIL_LOAD_CLASSIFICATION_THRESH:
            print('Fail transient')
            # mistaken_signals.append(generated_signal)
        else:
            counter_mistakes += 1
            print('Load transient')

        SignalPlotter.plot_signal(signal_before, 'signal_before_transient', show=False)
        SignalPlotter.plot_signal(signal_after, 'signal_after_transient', show=False)

    print(counter_mistakes)
    # for index, mistaken_signal in enumerate(mistaken_signals):
    #     SignalPlotter.plot_signal(mistaken_signal, f'mistaken_signal_index{index}', show=False)

    """Reconstruction of transient only"""
    # coefficients[0] = np.zeros(len(coefficients[0]))
    # transient_reconstruct = wmanager_generated_signal.reconstruct(coefficients)
    # transient_reconstruct[:transient_interval_in_time_domain[0]] = 0
    # transient_reconstruct[transient_interval_in_time_domain[1]:] = 0
    # SignalPlotter.plot_signal(transient_reconstruct, 'transient_reconstructed', show=False)

    # print(transient_interval_in_time_domain)
    # fourier_transform_before = np.abs(
    #     (np.fft.fft(generated_signal[:transient_interval_in_time_domain[0]])))
    # SignalPlotter.plot_dft_domain(fourier_transform_before, 'fft_before_transient', show=False)
    # print('Hello')

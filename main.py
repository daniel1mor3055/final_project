from SignalGenerator.SignalGenerator import SignalGeneratorBuilder
from SignalPlotter.SignalPlotter import SignalPlotter
from TransientsAnalyzer.TransientsAnalyzer import TransientsAnalyzer
from WaveletsManager.WaveletsManager import WaveletsManager
from global_constants import (
    BASE_FREQUENCY,
    SAMPLES_PER_SECOND,
    FREQ_DOMAIN_WINDOW_SIZE, RESULTS_NAME
)

import matplotlib.pyplot as plt

if __name__ == '__main__':
    # Note that the num of base_amplitudes determines the number of load transients
    # TODO preprocessing should learn system noise and set MOVING_AVG_THRESH accordingly
    # TODO Building data base
    # TODO extract period of signal
    signal_generator = SignalGeneratorBuilder(). \
        with_base_params. \
        base_amplitudes([5, 3]). \
        base_frequency(BASE_FREQUENCY). \
        num_diff_harmonics(10). \
        with_noise_params. \
        mean(0). \
        var(0.5). \
        with_sampling_params. \
        duration(1). \
        samples_per_second(SAMPLES_PER_SECOND). \
        with_fail_transient_params. \
        min_gap_between_fail_trans(500). \
        num_fail_trans(1). \
        mean_fail_trans(0). \
        var_fail_trans(3). \
        max_failure_trans_samples(400). \
        min_failure_trans_samples(200). \
        gap_from_start_end_samples(2000). \
        with_load_transient_params. \
        mean_load_trans(0). \
        var_load_trans(3). \
        samples_to_apply_noise(200).build()

    signal_extension = 'symmetric'
    wavelets_family = 'db4'
    decompose_level = 1
    wmanager_generated_signal = WaveletsManager()

    generated_signal = signal_generator.generate()
    # SignalPlotter.plot_signal(generated_signal, 'signal_without_transients',
    #                           title='Signal Without Transients', show=False)

    coefficients = wmanager_generated_signal.decompose(signal=generated_signal, signal_extension=signal_extension,
                                                       wavelets_family=wavelets_family, decompose_level=decompose_level)
    wmanager_generated_signal.plot_decompose_summary(signal=generated_signal, coefficients=coefficients,
                                                     decompose_level=decompose_level, wavelets_family=wavelets_family,
                                                     signal_extension=signal_extension, show=False)

    print(signal_generator._fail_trans_intervals)
    transients = TransientsAnalyzer.analyze(signal=generated_signal, coefficients=coefficients,
                                            window_size=FREQ_DOMAIN_WINDOW_SIZE)

    for transient in transients:
        print(transient)

    starts_ends = []
    for transient in transients:
        starts_ends += [transient.indices[0], transient.indices[1]]

    ticks = []
    for transient in transients:
        ticks += ['start\nfail', 'end\nfail'] if transient.type == 'Fail Transient' else ['start\nload', 'end\nload']

    title = RESULTS_NAME
    plt.figure(figsize=(100, 20))
    plt.plot(generated_signal)
    plt.xticks(starts_ends, ticks)
    plt.title(title)
    plt.savefig(title)
    plt.show()

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

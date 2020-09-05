from SignalGenerator.SignalGenerator import SignalGeneratorBuilder
from TransientsAnalyzer.TransientsAnalyzer import TransientsAnalyzer
from WaveletsManager.WaveletsManager import WaveletsManager
from global_constants import (
    BASE_FREQUENCY,
    SAMPLES_PER_SECOND,
    FREQ_DOMAIN_WINDOW_SIZE
)

if __name__ == '__main__':
    # Note that the num of base_amplitudes determines the number of load transients
    # TODO preprocessing should learn system noise and set MOVING_AVG_THRESH accordingly
    # TODO Building data base
    signal_generator = SignalGeneratorBuilder(). \
        with_base_params. \
        base_amplitudes([5, 4, 3]). \
        base_frequency(BASE_FREQUENCY). \
        num_diff_harmonics(10). \
        with_noise_params. \
        mean(0). \
        var(1). \
        with_sampling_params. \
        duration(2). \
        samples_per_second(SAMPLES_PER_SECOND). \
        with_fail_transient_params. \
        min_gap_between_fail_trans(1000). \
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

from SignalGenerator.SignalGenerator import SignalGeneratorBuilder
from SignalPlotter.SignalPlotter import SignalPlotter
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
    # TODO extract period of signal
    signal_generator = SignalGeneratorBuilder(). \
        with_base_params. \
        base_amplitudes([5]). \
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
        max_failure_trans_samples(1000). \
        min_failure_trans_samples(500). \
        gap_from_start_end_samples(2000). \
        with_load_transient_params. \
        mean_load_trans(0). \
        var_load_trans(0). \
        samples_to_apply_noise(200).build()

    signal_extension = 'symmetric'
    wavelets_family = 'db4'
    decompose_level = 1

    generated_signal = signal_generator.generate()

    print(f'True transients intervals are:\n{signal_generator._fail_trans_intervals}')

    coefficients = WaveletsManager.decompose(signal=generated_signal, signal_extension=signal_extension,
                                             wavelets_family=wavelets_family, decompose_level=decompose_level)

    moving_average, transients = TransientsAnalyzer.analyze(signal=generated_signal, coefficients=coefficients,
                                                            window_size=FREQ_DOMAIN_WINDOW_SIZE,
                                                            wavelets_family=wavelets_family)

    SignalPlotter.plot_decompose_summary(signal=generated_signal, coefficients=coefficients,
                                         decompose_level=decompose_level, wavelets_family=wavelets_family,
                                         moving_average=moving_average, signal_extension=signal_extension,
                                         transients=transients, show=False)

    for transient in transients:
        print(transient)

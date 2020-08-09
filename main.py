from SignalGenerator.SignalGenerator import SignalGeneratorBuilder
from SignalPlotter.SignalPlotter import SignalPlotter
from WaveletsManager.WaveletsManager import WaveletsManager
import numpy as np

if __name__ == '__main__':
    signal_generator = SignalGeneratorBuilder(). \
        with_base_params. \
        base_amplitudes([5, 3]). \
        base_frequency(15). \
        num_diff_harmonics(10). \
        with_noise_params. \
        mean(0). \
        var(0). \
        with_sampling_params. \
        duration(1). \
        samples_per_second(300). \
        with_fail_transient_params. \
        mean_fail_trans(0). \
        var_fail_trans(10).build()

    generated_signal = signal_generator.generate()

    wmanager_generated_signal = WaveletsManager(generated_signal)
    coefficients = wmanager_generated_signal.decompose(signal_extension='symmetric', wavelets_family='sym2',
                                                       decompose_level=6)
    wmanager_generated_signal.plot_decompose_summary(show=False)

    coefficients[-1] = np.full(len(coefficients[-1]), np.median(coefficients[-1]))
    # coefficients[-2] = np.zeros(len(coefficients[-2]))
    reconstructed_signal = wmanager_generated_signal.reconstruct_with_coefficients(coefficients)
    SignalPlotter.plot_signal(generated_signal, 'generated_signal', show=False)
    SignalPlotter.plot_signal(reconstructed_signal, 'reconstructed_signal', show=False)
    diff_signal = np.abs(reconstructed_signal - generated_signal)
    SignalPlotter.plot_signal(diff_signal, 'diif_signal', show=False)
    # wmanager_generated_signal.plot_coefficients()
    # generated_signal_reconstructed = wmanager_generated_signal.reconstruct()

    # SignalPlotter.plot_signal(generated_signal,
    #                           'Multi sine wave with single load transient and also single failure transient')

    # SignalPlotter.plot_signal(generated_signal_reconstructed,
    #                           'Multi sine wave with single load transient and also single failure transient')

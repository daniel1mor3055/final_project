from SignalGenerator.SignalGenerator import SignalGeneratorBuilder
from SignalPlotter.SignalPlotter import SignalPlotter
from WaveletsManager.WaveletsManager import WaveletsManager
import numpy as np

if __name__ == '__main__':
    signal_generator = SignalGeneratorBuilder(). \
        with_base_params. \
        base_amplitudes([5, 3]). \
        base_frequency(50). \
        num_diff_harmonics(10). \
        with_noise_params. \
        mean(0). \
        var(0.5). \
        with_sampling_params. \
        duration(2). \
        samples_per_second(44100). \
        with_fail_transient_params. \
        mean_fail_trans(0). \
        var_fail_trans(4).build()

    generated_signal = signal_generator.generate()

    wmanager_generated_signal = WaveletsManager(generated_signal)
    coefficients = wmanager_generated_signal.decompose(signal_extension='symmetric', wavelets_family='db4',
                                                       decompose_level=1)
    wmanager_generated_signal.plot_decompose_summary(show=False)

    # coefficients[-1] = np.full(len(coefficients[-1]), np.median(coefficients[-1]))
    # coefficients[-2] = np.zeros(len(coefficients[-2]))
    approximation_reconstructed = wmanager_generated_signal.reconstruct_with_coefficients(coefficients[:-1])
    approximation_reconstructed = np.zeros(len(approximation_reconstructed))
    # print(approximation_reconstructed)
    reconstructed_signal = wmanager_generated_signal.reconstruct_with_coefficients(
        [approximation_reconstructed, coefficients[-1]])
    SignalPlotter.plot_signal(generated_signal, 'generated_signal', show=False)
    SignalPlotter.plot_signal(reconstructed_signal, 'reconstructed_signal', show=False)

    # new_wmanager_reconstructed_signal = WaveletsManager(reconstructed_signal)
    # new_coeffs = new_wmanager_reconstructed_signal.decompose(signal_extension='symmetric', wavelets_family='db4',
    #                                                          decompose_level=3)
    #
    # new_wmanager_reconstructed_signal.plot_decompose_summary(pathname='new_summary', show=False)
    #
    # cd1 = np.asarray(coefficients[-1])
    # cd1_abs = np.abs(cd1)
    # cd1_ma = np.convolve(cd1_abs, np.ones(5) / 5, mode='same')
    # max_index = np.argmax(cd1_ma)
    # print(max_index)
    # SignalPlotter.plot_signal(cd1_ma, 'cd1_ma', show=False)
    #
    # window_size = 40
    # cutted_cd1_ma = cd1_ma[max_index - window_size:max_index + window_size]
    # for item in np.where(cutted_cd1_ma == np.min(cutted_cd1_ma)):
    #     print(item)
    # print()
    # print(np.where(cutted_cd1_ma == np.min(cutted_cd1_ma)))

    # for i in range(int(max_index), -1, -1):
    #     if cd1_ma[i - 1] > cd1_ma[i]:
    #         print(i)
    #         break
    #
    # for j in range(int(max_index), len(cd1_ma)):
    #     if cd1_ma[j + 1] > cd1_ma[j]:
    #         print(j)
    #         break

    # def find_closest_indices_before_after_max(max_index,)
    # diff_signal = np.abs(reconstructed_signal - generated_signal)
    # SignalPlotter.plot_signal(diff_signal, 'diif_signal', show=False)
    # wmanager_generated_signal.plot_coefficients()
    # generated_signal_reconstructed = wmanager_generated_signal.reconstruct()

    # SignalPlotter.plot_signal(generated_signal,
    #                           'Multi sine wave with single load transient and also single failure transient')

    # SignalPlotter.plot_signal(generated_signal_reconstructed,
    #                           'Multi sine wave with single load transient and also single failure transient')

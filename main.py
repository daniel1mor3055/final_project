from SignalGenerator.SignalGenerator import SignalGeneratorBuilder
from SignalPlotter.SignalPlotter import SignalPlotter

if __name__ == '__main__':
    signal_generator = SignalGeneratorBuilder(). \
        with_base_params. \
        base_amplitude(5). \
        base_frequency(15). \
        num_diff_harmonics(10). \
        with_noise_params. \
        mean(0). \
        var(0.1). \
        with_sampling_params. \
        duration(2). \
        samples_per_second(150). \
        with_transient_params. \
        num_reg_trans(0). \
        mean_fail_trans(0). \
        var_fail_trans(3).build()

    generated_signal = signal_generator.generate()
    SignalPlotter.plot_signal(generated_signal,
                              'Multi sine wave with single load transient and also single failure transient')

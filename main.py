from Signal.Signal import Signal
from MultiSignal.MultiSignal import MultiSignal
from SignalGenerator.SignalGenerator import SignalGeneratorBuilder

if __name__ == '__main__':
    amplitudes = [3, 4]
    base_freqs = [5, 6]
    signal = Signal(3, 5)
    signal1 = Signal(4, 6)
    multi_signals = MultiSignal.from_params_lists(amplitudes, base_freqs)

    # base_params = {
    #     base_freq,
    #     num_diff_harmonics,
    # }
    # noise_params = {
    #     mean,
    #     var,
    # }
    # sampling_params = {
    #     duration,
    #     samples_per_seconds,
    # }
    # transients_params = {
    #     num_regular_transients,
    #     num_failure_transients,
    # }

    signal_generator = SignalGeneratorBuilder(). \
        with_base_params. \
        base_frequency(40). \
        num_diff_harmonics(10). \
        with_noise_params. \
        mean(0). \
        var(1). \
        with_sampling_params. \
        duration(2). \
        samples_per_second(1). \
        with_transient_params. \
        num_reg_trans(1). \
        num_fail_trans(1).build()

    print(signal_generator.generate())

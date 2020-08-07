from Signal.Signal import SignalBuilder
from MultiSignal.MultiSignal import MultiSignal

if __name__ == '__main__':
    amplitudes = [3, 4]
    base_freqs = [5, 6]
    signal = SignalBuilder().with_base_params.base_freq(5).amplitude(3)
    signal1 = SignalBuilder().with_base_params.base_freq(6).amplitude(4)
    multi_signals = MultiSignal.from_params_lists(amplitudes, base_freqs)
    print(multi_signals)

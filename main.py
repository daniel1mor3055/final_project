from Signal.Signal import SignalBuilder

if __name__ == '__main__':
    print(SignalBuilder().with_base_params.base_freq(5).amplitude(3).duration(2).samples_per_second(1))

class Signal:
    def __init__(self):
        self.computed_signal = None
        self.amplitude = None
        self.frequency = None
        self.duration = None
        self.samples_per_second = None

    def __str__(self):
        raise NotImplementedError


class SignalBuilder:
    def __init__(self, signal=None):
        if signal is None:
            self.signal = Signal()
        else:
            self.signal = signal

    @property
    def with_base_params(self):
        return SignalBaseBuilder(self.signal)

    @property
    def works(self):
        return SignalJobBuilder(self.signal)

    def build(self):
        return self.signal


class SignalBaseBuilder(SignalBuilder):
    def __init__(self, signal):
        super().__init__(signal)

    def base_freq(self, frequency):
        self.signal.frequency = frequency
        return self

    def amplitude(self, amplitude):
        self.signal.amplitude = amplitude
        return self

    def duration(self, duration):
        self.signal.duration = duration
        return self

    def samples_per_second(self, samples_per_second):
        self.signal.samples_per_second = samples_per_second
        return self
#
# class PersonJobBuilder(PersonBuilder):
#     def __init__(self, person):
#         super().__init__(person)
#
#     def at(self, company_name):
#         self.person.company_name = company_name
#         return self
#
#     def as_a(self, position):
#         self.person.position = position
#         return self
#
#     def earning(self, annual_income):
#         self.person.annual_income = annual_income
#         return self
#
#
# class PersonAddressBuilder(PersonBuilder):
#     def __init__(self, person):
#         super().__init__(person)
#
#     def at(self, street_address):
#         self.person.street_address = street_address
#         return self
#
#     def with_postcode(self, postcode):
#         self.person.postcode = postcode
#         return self
#
#     def in_city(self, city):
#         self.person.city = city
#         return self

class SampleRateError(ValueError):
    def __init__(self, message='duration*samples_per_second must be an integer'):
        super().__init__(message)


class MissingPropertiesError(Exception):
    def __init__(self, missing_properties, message='SignalGenerator still missing the following parameters:\n\t'):
        super().__init__(message + '\n\t'.join(missing_properties))

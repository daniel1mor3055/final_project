class MissingPropertiesError(Exception):
    def __init__(self, missing_properties, message='SignalGenerator still missing the following parameters:\n\t'):
        super().__init__(message + '\n\t'.join(missing_properties))


class FailureTransParamsError(ValueError):
    def __init__(self, message):
        super().__init__(message)


class SampleRateError(ValueError):
    def __init__(self, message):
        super().__init__(message)

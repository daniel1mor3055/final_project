SAMPLES_PER_SECOND = 44100  # TODO FURTHER RESEARCH CAN BE DONE
BASE_FREQUENCY = 50

TIME_DOMAIN_WINDOW_SIZE = SAMPLES_PER_SECOND // BASE_FREQUENCY
FREQ_DOMAIN_WINDOW_SIZE = TIME_DOMAIN_WINDOW_SIZE // 2
FAIL_LOAD_CLASSIFICATION_THRESH = 0.95

TRIAL_NAME = 'Signal With Fail Transient'

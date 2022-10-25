from util.util import *
import numpy as np


class Virus:
    _SECTION_CONFIG = "Virus"

    def __init__(self, config_file):
        self.spread_rate = float(get_value_from_config(config_file, Virus._SECTION_CONFIG, 'SPREAD_RATE'))
        # self.spread_rate = np.zeros(40)
        # self.spread_rate[0] = 2
        # for i in range(1, 40):
        #     self.spread_rate[i] = self.spread_rate[i - 1] / 1.23

        self.VIR_LOAD_THRESHOLD = int(get_value_from_config(config_file, Virus._SECTION_CONFIG, 'VIR_LOAD_THRESHOLD'))
        self.MILD_THRESHOLD = int(get_value_from_config(config_file, Virus._SECTION_CONFIG, 'MILD_THRESHOLD'))
        self.SEVERE_THRESHOLD = int(get_value_from_config(config_file, Virus._SECTION_CONFIG, 'SEVERE_THRESHOLD'))
        self.DEAD_THRESHOLD = int(get_value_from_config(config_file, Virus._SECTION_CONFIG, 'DEAD_THRESHOLD'))





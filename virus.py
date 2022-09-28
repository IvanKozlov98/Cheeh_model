from util import *
import numpy as np


class Virus:
    _SECTION_CONFIG = "Virus"
    spread_rate = None

    @staticmethod
    def init():
        # Virus.spread_rate = float(get_value_from_config(Virus._SECTION_CONFIG, 'SPREAD_RATE'))
        Virus.spread_rate = np.zeros(40)
        Virus.spread_rate[0] = 2
        for i in range(1, 40):
            Virus.spread_rate[i] = Virus.spread_rate[i - 1] / 1.23


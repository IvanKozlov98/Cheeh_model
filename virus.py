from util import *


class Virus:
    _SECTION_CONFIG = "Virus"
    spread_rate = 0

    @staticmethod
    def init():
        Virus.spread_rate = get_value_from_config(Virus._SECTION_CONFIG, 'SPREAD_RATE')



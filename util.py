import numpy as np
import configparser
import numpy.random as nprnd


config = configparser.ConfigParser()
CONFIG_FILE = "config/config.ini"
config.read(CONFIG_FILE)


def get_value_from_config(section, key):
    return config.get(section, key)

def in_range(left, num, right):
    return left <= num and num <= right
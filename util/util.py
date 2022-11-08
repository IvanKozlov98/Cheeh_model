import configparser
from scipy.stats import lognorm
import numpy as np


def get_alpha_beta(mu, sigma):
    alpha = mu**2 * ((1 - mu) / sigma**2 - 1 / mu)
    beta = alpha * (1 / mu - 1)
    return alpha, beta

def get_value_from_config(origin, section, key):
    if isinstance(origin, str):
        config = configparser.ConfigParser()
        config.read(origin)
        return config.get(section, key)
    return origin[key]


def save_dict_as_config(dict_, section, filename):
    config = configparser.ConfigParser()
    data_ = {section : dict_}
    config.read_dict(data_)
    with open(filename, 'w') as configfile:
        config.write(configfile)


def in_range(left, num, right):
    return left <= num and num <= right


def get_in_range(left, num, right):
    if num < left:
        return left
    if num > right:
        return right
    return num


def get_lognormal_dist(mean, std, size):
    a = 1 + (std / mean) ** 2
    s = np.sqrt(np.log(a))
    scale = mean / np.sqrt(a)
    return lognorm.rvs(s=s, scale=scale, size=size)
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import beta
from model.model import Model

import time
import os


def get_speed_protect(age, non_specific_immunity):
    ...

def get_start_protect_time(age, non_specific_immunity):
    ...


MAX_TIME_INFECTED = 40

means_speed = None


def make_trace_viral_load(trace_specific_immunity):
    spread_rate = np.zeros(40)
    spread_rate[0] = 2
    for i in range(1, 40):
        spread_rate[i] = spread_rate[i - 1] / 1.23
    trace_viral_load = np.zeros(len(trace_specific_immunity))
    alpha = 0.3
    trace_viral_load[0] = 800
    for t in range(1, len(trace_specific_immunity)):
        trace_viral_load[t] = (trace_viral_load[t - 1] +
                               alpha * trace_viral_load[t - 1] * spread_rate[t]
                               ) * (1 - trace_specific_immunity[t])

    return trace_viral_load

def expr():
    # t = np.arange(40)
    # a1, b1 = -0.3, 4
    # a2, b2 = -0.5, 4
    # a3, b3 = -0.7, 4
    # y1 = np.array([1 / (1+np.exp(a1*x+b1)) for x in t])
    # y2 = np.array([1 / (1+np.exp(a2*x+b2)) for x in t])
    # y3 = np.array([1 / (1+np.exp(a3*x+b3)) for x in t])
    #
    #
    # figure, axis = plt.subplots(5, 4)
    # for (i, a) in enumerate([-0.1, -0.3, -0.5, -0.7, -0.9]):
    #     for (j, b) in enumerate([1, 4, 7, 10]):
    #         y = np.array([1 / (1+np.exp(a*x+b)) for x in t])
    #         q = make_trace_viral_load(y)
    #         axis[i, j].plot(t, q, label="viral load")
    #         axis[i, j].plot(t, y * np.max(q), label="specific immunity")
    #         axis[i, j].set_title(f"a={a}, b={b}")

    y = np.array([beta.pdf(x, a=3, b=5) for x in np.linspace(0.1, 0.9, 100)])
    print(y / np.max(y))
    # plt.plot(np.arange(100), y / np.max(y))
    # plt.show()

    # cur_y = y1
    # for _ in range(2):
    #     q1 = make_trace_viral_load(cur_y)
    #     plt.plot(t, q1, label="1")
    #     plt.plot(t, cur_y * np.max(q1), label="a=-0.1, b=4")
    #     plt.legend()
    #     plt.show()



def main_run(log_time=False,
         config_model="config/model/model.ini",
         config_virus="config/viruses/covid-19.ini",
         config_cities="config/Voronesh.ini",
         use_cache_population=False,
         cache_file_population=True):
    np.random.seed(42)
    model = None
    if log_time:
        s = time.time()
        model = Model(
            config_model="config/model/model.ini",
            config_virus="config/viruses/covid-19.ini",
            config_cities="config/Voronesh.ini",
            use_cache_population=True,
            cache_file_population=True
        )
        e = time.time()
        print(f"Time: {e - s}")
    else:
        model = Model(
            config_model=os.path.join(os.path.dirname(__file__), '..', 'config', 'model', 'model.ini'),
            config_virus=os.path.join(os.path.dirname(__file__), '..', 'config', 'viruses', 'covid-19.ini'),
            config_cities=os.path.join(os.path.dirname(__file__), '..', 'config', 'cities', 'Voronesh.ini'),
            use_cache_population=True,
            cache_file_population=True
        )

    model.run(debug_mode=True)
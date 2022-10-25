from util.util import *

from collections import deque
from scipy.stats import beta
from scipy.stats import norm
import numpy as np


class Person:

    next_id = 1
    means_immunity = None
    "treatment rate parameters"
    treatment_rates = dict()
    treatment_rates_inds = dict()

    "start treatment time parameters"
    start_treatment_times = dict()
    start_treatment_times_inds = dict()

    # constant
    RANDOM_NUMBER_BY_AGE_COUNT = 1000

    # @staticmethod
    # def static_init():
    #     Person.means_immunity = np.array([beta.pdf(x, a=3, b=5) for x in np.linspace(0.1, 0.9, 100)])
    #     Person.means_immunity = Person.means_immunity / np.max(Person.means_immunity)
    #     for age in range(100):
    #         Person.treatment_rates[age] = -norm.rvs(loc=Person.means_immunity[age], scale=0.1, size=Person.RANDOM_NUMBER_BY_AGE_COUNT)
    #         Person.treatment_rates_inds[age] = 0
    #         #
    #         Person.start_treatment_times[age] = (1 - norm.rvs(loc=Person.means_immunity[age], scale=0.2, size=Person.RANDOM_NUMBER_BY_AGE_COUNT)) * 10.0
    #         Person.start_treatment_times_inds[age] = 0

    def __init__(self, age, gender):
        self.id = Person.next_id
        Person.next_id += 1

        self.gender = gender
        self.age = age

        # self.location = Person.location
        # self.treatment_period = 0
        # self.infected_period = 0

        # init non-specific immunity
        # self.non_specific_immun = get_in_range(0.1,
        #                                        Person.means_immunity[self.age], # TODO (IvanKozlov98) make random it
        #                                        1.0) / 2
        # # init treatment rate parameters
        # self.treatment_rate = get_in_range(-0.9, Person.treatment_rates[age][Person.treatment_rates_inds[age]], -0.1)
        # Person.treatment_rates_inds[age] = 0 if Person.treatment_rates_inds[age] + 1 == Person.RANDOM_NUMBER_BY_AGE_COUNT else Person.treatment_rates_inds[age] + 1
        #
        # # start treatment time parameters
        # self.start_treatment_time = get_in_range(1, Person.start_treatment_times[age][Person.start_treatment_times_inds[age]], 10)
        # Person.start_treatment_times_inds[age] = 0 if Person.start_treatment_times_inds[age] + 1 == Person.RANDOM_NUMBER_BY_AGE_COUNT else Person.start_treatment_times_inds[age] + 1
        # # init indexes in array of model's specific_immunity_traces
        # self.a_id = -1
        # self.b_id = -1

        # init specific immunity
        self.specific_immun = 0.0
        self.non_specific_immun = 0.2

        self.lag_specific_immun = 5

        self.alpha = 0.01
        # list of pairs kind of (agent, interaction with him)
        self.static_contact_list = []
        self.random_contact_list = []

        # label (may be one of 'healthy', 'infected', 'recovered')
        self.state = 'healthy'

        self.time_in_infected_state = 0
        self.viral_load = deque([0])



        # self.recovering_rate = round(self.non_specific_immun * ((100 - self.age) / 10) * (1.1 if self.gender == 'm' else 1.2))
        # self.recovering_rate = 1 if self.recovering_rate == 0 else self.recovering_rate
        # self.recovering_rate = int(self.recovering_rate)
        #
        # self.recovering_time = 0

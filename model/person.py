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

    # prob_sym_dict = dict()
    # prob_mild_dict = dict()
    # prob_severe_dict = dict()
    # prob_dead_dict = dict()
    # @staticmethod
    # def static_init():
    #     for i in range(100):
    #         if i < 10:
    #             Person.prob_sym_dict[i] = 0.5
    #             Person.prob_mild_dict[i] = 0.0005
    #             Person.prob_severe_dict[i] = 0.00003
    #             Person.prob_dead_dict[i] = 0.00002
    #         elif i < 20:
    #             Person.prob_sym_dict[i] = 0.55
    #             Person.prob_mild_dict[i] = 0.00165
    #             Person.prob_severe_dict[i] = 0.00008
    #             Person.prob_dead_dict[i] = 0.00002
    #         elif i < 30:
    #             Person.prob_sym_dict[i] = 0.6
    #             Person.prob_mild_dict[i] = 0.00720
    #             Person.prob_severe_dict[i] = 0.00036
    #             Person.prob_dead_dict[i] = 0.00010
    #         elif i < 40:
    #             Person.prob_sym_dict[i] = 0.65
    #             Person.prob_mild_dict[i] = 0.0208
    #             Person.prob_severe_dict[i] = 0.00104
    #             Person.prob_dead_dict[i] = 0.00032
    #         elif i < 50:
    #             Person.prob_sym_dict[i] = 0.7
    #             Person.prob_mild_dict[i] = 0.0343
    #             Person.prob_severe_dict[i] = 0.00216
    #             Person.prob_dead_dict[i] = 0.00098
    #         elif i < 60:
    #             Person.prob_sym_dict[i] = 0.75
    #             Person.prob_mild_dict[i] = 0.0765
    #             Person.prob_severe_dict[i] = 0.00933
    #             Person.prob_dead_dict[i] = 0.00265
    #         elif i < 70:
    #             Person.prob_sym_dict[i] = 0.8
    #             Person.prob_mild_dict[i] = 0.1328
    #             Person.prob_severe_dict[i] = 0.03639
    #             Person.prob_dead_dict[i] = 0.00766
    #         elif i < 80:
    #             Person.prob_sym_dict[i] = 0.85
    #             Person.prob_mild_dict[i] = 0.20655
    #             Person.prob_severe_dict[i] = 0.08923
    #             Person.prob_dead_dict[i] = 0.02439
    #         elif i < 90:
    #             Person.prob_sym_dict[i] = 0.9
    #             Person.prob_mild_dict[i] = 0.2457
    #             Person.prob_severe_dict[i] = 0.172
    #             Person.prob_dead_dict[i] = 0.0892
    #         else:
    #             Person.prob_sym_dict[i] = 0.9
    #             Person.prob_mild_dict[i] = 0.2457
    #             Person.prob_severe_dict[i] = 0.1742
    #             Person.prob_dead_dict[i] = 0.1619


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
        self.home_contact_list = []
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
        self.flag_check_infected = False
        self.flag_check_mild = False
        self.flag_check_severe = False
        self.flag_check_dead = False
        #
        self.small_group_id = -1
        self.big_group_id = -1


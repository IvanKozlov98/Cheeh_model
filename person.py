from util import *
from collections import deque
from scipy.stats import beta
from scipy.stats import norm
import numpy as np


class Person:

    next_id = 1
    means_immunity = None

    @staticmethod
    def static_init():
        Person.means_immunity = np.array([beta.pdf(x, a=2, b=4) for x in np.linspace(0.0, 1.0, 100)])
        Person.means_immunity = Person.means_immunity / np.max(Person.means_immunity)

    def __init__(self, age, gender):
        self.id = Person.next_id
        Person.next_id += 1
        self.gender = gender
        self.age = age

        # self.location = Person.location
        # self.treatment_period = 0
        # self.infected_period = 0
        self.non_specific_immun = get_in_range(0.1,
                                               norm.rvs(loc=Person.means_immunity[self.age], scale=0.1),
                                               1.0) / 2
        self.specific_immun = 0.0

        # list of pairs kind of (agent, interaction with him)
        self.static_contact_list = []
        self.random_contact_list = []

        # label (may be one of 'healthy', 'infected', 'infectious', 'recovered')
        self.state = 'healthy'

        self.time_in_infected_state = 0
        self.viral_load = deque([0])

        self.recovering_rate = round(self.non_specific_immun * ((100 - self.age) / 10) * (1.1 if self.gender == 'm' else 1.2))
        self.recovering_rate = 1 if self.recovering_rate == 0 else self.recovering_rate
        self.recovering_rate = int(self.recovering_rate)

        self.recovering_time = 0

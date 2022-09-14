from util import *
from collections import deque


class Person:

    next_id = 1

    def __init__(self, age, gender):
        # , nonspecific_immun_state, , contact_list_home, contact_list_work, contact_list_random, state
        self.id = get_random_id()
        self.gender = gender
        self.age = age

        # self.location = Person.location
        # self.treatment_period = 0
        # self.infected_period = 0
        self.non_specific_immun = np.random.uniform(low=0.2, high=0.5)
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

        self.recovering_time = 0

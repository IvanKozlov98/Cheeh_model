from util import *
import numpy.random as nprnd

class Person:

    next_id = 1

    def __init__(self, age, gender):
        # , nonspecific_immun_state, , contact_list_home, contact_list_work, contact_list_random, state
        self.id = get_random_id()
        self.gender = gender
        self.age = age

        # self.location = Person.location
        self.treatment_period = 0
        self.infected_period = 0
        self.non_specific_immun = 0.1
        self.specific_immun = 0.1

        # list of pairs kind of (agent, interaction with him)
        self.static_contact_list = []
        self.random_contact_list = []

        # label (may be one of 'healthy', 'infected', 'infectious', 'recovered')
        self.state = 'healthy'

        self.rest_of_hosp_period = 0
        self.viral_load = 0



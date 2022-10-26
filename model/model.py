import time

from city.location import Location
from util.util import *
from model.interaction import Interaction
from virus.virus import Virus

import numpy as np
import numpy.random as nprnd
from scipy.stats import beta


def add_if(xs, x):
    if x is not None:
        xs.append(x)

class ModelStats:
    def __init__(self):
        self.list_number_new_infected_people = []
        self.list_number_recovered_people = []
        self.list_number_all_infected_people = []
        self.list_dead_people = []
        self.list_mean_specific_immunity = []
        self.list_median_specific_immunity = []

    def add_values(self,
                   number_new_infected_people=None,
                   number_recovered_people=None,
                   number_all_infected_people=None,
                   dead_people=None,
                   mean_specific_immunity=None,
                   median_specific_immunity=None):
        add_if(self.list_number_new_infected_people, number_new_infected_people)
        add_if(self.list_number_recovered_people, number_recovered_people)
        add_if(self.list_number_all_infected_people, number_all_infected_people)
        add_if(self.list_dead_people, dead_people)
        add_if(self.list_mean_specific_immunity, mean_specific_immunity)
        add_if(self.list_median_specific_immunity, median_specific_immunity)


class Model:
    _SECTION_CONFIG = "Model"
    RANDOM_INTERACTION = Interaction(type_interaction="Random", degree=10)  # TODO(IvanKozlov98) move to another place
    TRACES_COUNT_A = 100
    TRACES_COUNT_B = 1000
    MAX_TIME_INFECTED = 40

    # def init_traces(self):
    #     """
    #     Initiation viral and specific immunity traces
    #     """
    #     self.viral_load_traces = np.zeros(shape=(Model.TRACES_COUNT_A, Model.TRACES_COUNT_B, Model.MAX_TIME_INFECTED))
    #     self.specific_immunity_traces = np.zeros(
    #         shape=(Model.TRACES_COUNT_A, Model.TRACES_COUNT_B, Model.MAX_TIME_INFECTED))
    #     for (i, a) in enumerate(np.linspace(-0.9, -0.1, Model.TRACES_COUNT_A)):
    #         for (j, b) in enumerate(np.linspace(1, 10, Model.TRACES_COUNT_B)):
    #             specific_immunity_trace = np.array(
    #                 [1 / (1 + np.exp(a * x + b)) for x in range(Model.MAX_TIME_INFECTED)])
    #             viral_load_trace = np.zeros(Model.MAX_TIME_INFECTED)
    #             alpha = 0.3
    #             viral_load_trace[0] = 800  # TODO (IvanKozlov98) maybe save viral load given person
    #             for t in range(1, Model.MAX_TIME_INFECTED):
    #                 viral_load_trace[t] = (viral_load_trace[t - 1] +
    #                                        alpha * viral_load_trace[t - 1] * self.virus.spread_rate[t]
    #                                        ) * (1 - specific_immunity_trace[t])
    #             self.viral_load_traces[i, j] = viral_load_trace
    #             self.specific_immunity_traces[i, j] = specific_immunity_trace

    def make_person_infected(self, person_id, viral_load=100):
        person = self.people[person_id]
        person.state = 'infected'
        person.viral_load[-1] = viral_load  # TODO (IvanKozlov98)
        # person.a_id = int(min(round(person.treatment_rate * Model.TRACES_COUNT_A), Model.TRACES_COUNT_A - 1))
        # person.b_id = int(min(round((person.start_treatment_time - 1) * Model.TRACES_COUNT_B / 10.0),
        #                   Model.TRACES_COUNT_B - 1))

    def _init_random_starting_infected_people(self, initial_infected_people_count):
        self.infected_people_ids = set(
            list(self.people.keys())[:initial_infected_people_count])  # ids infected persons in list of people
        for infected_person_id in self.infected_people_ids:
            self.make_person_infected(infected_person_id, nprnd.randint(self.VIR_LOAD_THRESHOLD, self.SEVERE_THRESHOLD))

    @staticmethod
    def _init_specific_immunity(mean, sigma, people):
        norm_alfa_coef = 1000
        people_count = len(people)
        a, b = get_alpha_beta(mean, sigma)
        specific_immunity_rv = np.array(beta.rvs(size=people_count, a=a, b=b)) / norm_alfa_coef
        for (i, person_id) in enumerate(people.keys()):
            people[person_id].alpha = specific_immunity_rv[i]

    @staticmethod
    def _init_non_specific_immunity(mean, sigma, people):
        people_count = len(people)
        a, b = get_alpha_beta(mean, sigma)
        non_specific_immunity_rv = np.array(beta.rvs(size=people_count, a=a, b=b))
        for (i, person_id) in enumerate(people.keys()):
            people[person_id].non_specific_immun = non_specific_immunity_rv[i]

    @staticmethod
    def _init_lag(lag, people):
        for person_id in people.keys():
            people[person_id].lag_specific_immun = lag

    def __init__(self,
                 config_model,
                 config_virus,
                 config_cities,
                 use_cache_population=True,
                 cache_file_population=True,
                 gui=False):
        """
        :param config_model: dict or file with config
        :param config_virus: dict or file with config
        :param config_cities: dict or file with config
        :param use_cache_population:
        :param cache_file_population:
        :param gui:
        """
        self.flag_run = True
        self.gui = gui
        # init model stats
        self.model_stats = ModelStats()
        # init view
        self.view = None
        # init city
        location = Location(config_cities, use_cache=use_cache_population, cache_file=cache_file_population)
        self.people = location.get_population()
        specific_immun_mean = float(get_value_from_config(config_virus, Virus._SECTION_CONFIG, 'SPECIFIC_IMMUN_MEAN'))
        specific_immun_sigma = float(get_value_from_config(config_virus, Virus._SECTION_CONFIG, 'SPECIFIC_IMMUN_SIGMA'))
        non_specific_immun_mean = float(get_value_from_config(config_virus, Virus._SECTION_CONFIG, 'NON_SPECIFIC_IMMUN_MEAN'))
        non_specific_immun_sigma = float(get_value_from_config(config_virus, Virus._SECTION_CONFIG, 'NON_SPECIFIC_IMMUN_SIGMA'))
        lag_specific_immun = float(get_value_from_config(config_virus, Virus._SECTION_CONFIG, 'LAG'))

        Model._init_specific_immunity(specific_immun_mean, specific_immun_sigma, self.people)
        Model._init_non_specific_immunity(non_specific_immun_mean, non_specific_immun_sigma, self.people)
        Model._init_lag(lag_specific_immun, self.people)
        # init virus
        self.virus = Virus(config_virus)
        # init model parameters
        self.VIR_LOAD_THRESHOLD = self.virus.VIR_LOAD_THRESHOLD
        self.MILD_THRESHOLD = self.virus.MILD_THRESHOLD
        self.SEVERE_THRESHOLD = self.virus.SEVERE_THRESHOLD
        self.DEAD_THRESHOLD = self.virus.DEAD_THRESHOLD

        self.DAYS_COUNT = int(get_value_from_config(config_model, Model._SECTION_CONFIG, 'DAYS_COUNT'))
        # init starting infected people
        initial_infected_people_count = int(get_value_from_config(config_model, Model._SECTION_CONFIG, 'INITIAL_INFECTED_PEOPLE_COUNT'))
        self._init_random_starting_infected_people(initial_infected_people_count)
        # init random values for simulation random contacts
        self.MAX_NUMBER_RANDOM_CONTACTS = 15
        self.number_random_contacts = np.random.choice(np.arange(3, self.MAX_NUMBER_RANDOM_CONTACTS),
                                                       self.DAYS_COUNT * 1 * len(self.people) // 2)
        self.ind_number_random_contacts = 0
        self.random_contacts = np.random.choice(list(self.people.keys()),
                                                self.DAYS_COUNT * self.MAX_NUMBER_RANDOM_CONTACTS * len(self.people) // 2)
        self.ind_random_contacts = 0
        # init variables for immunity traces
        # self.init_traces()
        self.R = self.VIR_LOAD_THRESHOLD / 1.5


    def _get_new_random_contacts(self):
        new_random_contacts_count = self.number_random_contacts[self.ind_number_random_contacts]
        self.ind_number_random_contacts += 1
        new_random_contacts = []
        for _ in range(new_random_contacts_count):
            new_random_contacts.append((int(self.random_contacts[self.ind_random_contacts]), Model.RANDOM_INTERACTION))
            self.ind_random_contacts += 1
        return new_random_contacts

    def set_view(self, view):
        self.view = view



    def infect(self, infected_person, contact_person, interaction):
        """
        Calculate giving virus load from self to other_person based on
            1) interaction
            2) state of infected agent
            3) state of contact agent
            4) virus characteristics
        :return: is other person became or not infected
        """
        # TODO(IvanKozlov98) write more complex formula than that
        giving_viral_load = interaction.degree * (infected_person.viral_load[-1] / self.R) * (1 - contact_person.specific_immun)
        # update virus load of contact person
        contact_person.viral_load[-1] += giving_viral_load
        # update state of contact person if needed
        if contact_person.viral_load[-1] >= self.VIR_LOAD_THRESHOLD and contact_person.state == "healthy":
            self.make_person_infected(contact_person.id)
            return True
        return False

    def stop_running(self):
        self.flag_run = False

    def _spread_infection_step(self):
        """
        Infection step
        :return: set of ids new infected people
        """
        new_infected_ids = set()
        for infected_person_id in self.infected_people_ids:
            # update new contacts infected people
            infected_person = self.people[infected_person_id]
            # infect other people
            for (contact_person_id, interaction) in self._get_contact_list_of_person(infected_person):
                if contact_person_id not in self.people or self.people[contact_person_id].state != 'healthy':
                    continue
                is_infected = self.infect(infected_person, self.people[contact_person_id], interaction)
                if is_infected:
                    self.people[contact_person_id].viral_load[-1] = self.VIR_LOAD_THRESHOLD
                    new_infected_ids.add(contact_person_id)

        return new_infected_ids


    def _update_viral_load(self, person):
        cur_viral_load = person.viral_load[-1]
        cur_viral_load *= (1 + self.virus.spread_rate)
        cur_viral_load *= (1 - (person.specific_immun / 1.57079632679))
        cur_viral_load *= (1 - person.non_specific_immun)
        # update value
        person.viral_load.append(cur_viral_load)
        if len(person.viral_load) > person.lag_specific_immun:
            person.viral_load.popleft()

    def _update_specific_immun(self, person):
        if person.time_in_infected_state > person.lag_specific_immun:
            person.specific_immun = np.arctan(
                person.viral_load[0] * person.alpha + person.specific_immun)

    def _is_mild_infected(self, person):
        return in_range(self.MILD_THRESHOLD, person.viral_load[-1], self.SEVERE_THRESHOLD)

    def _is_severe_infected(self, person):
        return in_range(self.MILD_THRESHOLD, person.viral_load[-1], 1000000)

    def _is_infected(self, person):
        return person.viral_load[-1] >= self.VIR_LOAD_THRESHOLD

    @staticmethod
    def _is_recovered(person):
        return person.viral_load[-1] < 5

    def _recovery_non_infected_people_step(self):
        for person in self.people.values():
            if person.state == "healthy":
                person.viral_load[-1] = 0

    @staticmethod
    def _get_contact_list_mild(person):
        return list(filter(lambda x: x[1].type_interaction == 'Home', person.static_contact_list))

    @staticmethod
    def _get_contact_list_severe(person):
        return []

    def _get_contact_list_of_person(self, person):
        if person.state == 'mild':
            return Model._get_contact_list_mild(person)
        elif person.state == 'severe':
            return Model._get_contact_list_severe(person)
        return person.static_contact_list + self._get_new_random_contacts()

    @staticmethod
    def _update_non_specific_immun(infected_person):
        pass

    def _update_static_contact_lists(self, dead_ids):
        for dead_id in dead_ids:
            for (person_id, _) in self.people[dead_id].static_contact_list:
                self.people[person_id].static_contact_list = [(x, interaction) for (x, interaction) in
                                                              self.people[person_id].static_contact_list if x != dead_id]

    def _get_mean_median_specific_immunity(self):
        list_sp_im = []
        for person in self.people.values():
            list_sp_im.append(person.specific_immun)
        list_sp_im = np.array(list_sp_im)
        return np.mean(list_sp_im), np.median(list_sp_im)

    def _update_state_of_infected_people_step(self):
        """
        Update state of infected people
        :return: list of ids recovered people
        """
        recovered_ids = []
        dead_ids = []
        # see to current state of agent and starting day
        for infected_person_id in self.infected_people_ids:
            infected_person = self.people[infected_person_id]
            # update different parameters
            # infected_person.viral_load = self.viral_load_traces[infected_person.a_id, infected_person.b_id][
            #     infected_person.time_in_infected_state]
            # infected_person.specific_immun = self.specific_immunity_traces[infected_person.a_id, infected_person.b_id][
            #     infected_person.time_in_infected_state]
            self._update_specific_immun(infected_person)
            self._update_viral_load(infected_person)
            # Model._update_non_specific_immun(infected_person)
            # update time in infected state
            infected_person.time_in_infected_state += 1
            # update state of the infected person
            if infected_person.viral_load[-1] > self.DEAD_THRESHOLD:
                dead_ids.append(infected_person_id)
            elif infected_person.state == 'infected' and self._is_mild_infected(infected_person):
                infected_person.state = 'mild'
            elif (infected_person.state == 'infected' or infected_person.state == 'healthy') \
                    and self._is_severe_infected(infected_person):
                infected_person.state = 'severe'
            # check if recovered
            elif Model._is_recovered(infected_person):
                infected_person.state = 'healthy'
                # print(f"Recovering time: {infected_person.time_in_infected_state}")
                infected_person.time_in_infected_state = 0
                recovered_ids.append(infected_person_id)

        return recovered_ids, dead_ids

    def update(self, num_day):
        """
        Update state of model from one day to another
        """
        # step infection
        new_infected_people_ids = self._spread_infection_step()
        # step updating params for infected people
        recovered_people_ids, dead_ids = self._update_state_of_infected_people_step()
        # step updating params for non-infected people
        self._recovery_non_infected_people_step()
        # step updating static lists by dead persons
        # self._update_static_contact_lists(dead_ids)
        number_new_infected_people = len(new_infected_people_ids.difference(self.infected_people_ids))
        number_recovered_people = len(recovered_people_ids)

        # dead update
        for dead_id in dead_ids:
            self.people.pop(dead_id, None)
        # update infection group
        self.infected_people_ids.update(new_infected_people_ids)
        self.infected_people_ids.difference_update(recovered_people_ids)
        self.infected_people_ids.difference_update(dead_ids)
        number_all_infected_people = len(self.infected_people_ids)
        mean_specific_immunity, median_specific_immunity = self._get_mean_median_specific_immunity()

        if self.gui:
            self.model_stats.add_values(
                number_new_infected_people,
                number_recovered_people,
                number_all_infected_people,
                len(dead_ids),
                mean_specific_immunity,
                median_specific_immunity
            )
            time.sleep(1)
            if self.flag_run:
                self.view.update()
        else: # if cmdline
            print(f"Day {num_day}; "
                  f"Number new infected people: {number_new_infected_people}; "
                  f"Number recovered people: {number_recovered_people}; ", end='')
            print(f"Number all infected people: {number_all_infected_people}")
            print(f"Number dead people: {len(dead_ids)}")
            print(f"Mean specific immunuty: {mean_specific_immunity}")
            print(f"Median specific immunuty: {median_specific_immunity}")

    def get_model_stats(self):
        return self.model_stats

    def run(self):
        """
        Run modeling
        """

        print(f"Number of people: {len(self.people)}")
        for num_day in range(self.DAYS_COUNT):
            if self.flag_run:
                self.update(num_day)
            else:
                print("Stop running!")
                break

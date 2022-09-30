from city.location import Location
from util.util import *
from model.interaction import Interaction
from virus.virus import Virus

import numpy as np
import numpy.random as nprnd
import matplotlib.pyplot as plt


class Model:
    _SECTION_CONFIG = "Model"
    RANDOM_INTERACTION = Interaction(type_interaction="Random", degree=10)  # TODO(IvanKozlov98) move to another place
    TRACES_COUNT_A = 100
    TRACES_COUNT_B = 1000
    MAX_TIME_INFECTED = 40

    def init_traces(self):
        """
        Initiation viral and specific immunity traces
        """
        self.viral_load_traces = np.zeros(shape=(Model.TRACES_COUNT_A, Model.TRACES_COUNT_B, Model.MAX_TIME_INFECTED))
        self.specific_immunity_traces = np.zeros(
            shape=(Model.TRACES_COUNT_A, Model.TRACES_COUNT_B, Model.MAX_TIME_INFECTED))
        for (i, a) in enumerate(np.linspace(-0.9, -0.1, Model.TRACES_COUNT_A)):
            for (j, b) in enumerate(np.linspace(1, 10, Model.TRACES_COUNT_B)):
                specific_immunity_trace = np.array(
                    [1 / (1 + np.exp(a * x + b)) for x in range(Model.MAX_TIME_INFECTED)])
                viral_load_trace = np.zeros(Model.MAX_TIME_INFECTED)
                alpha = 0.3
                viral_load_trace[0] = 800  # TODO (IvanKozlov98) maybe save viral load given person
                for t in range(1, Model.MAX_TIME_INFECTED):
                    viral_load_trace[t] = (viral_load_trace[t - 1] +
                                           alpha * viral_load_trace[t - 1] * Virus.spread_rate[t]
                                           ) * (1 - specific_immunity_trace[t])
                self.viral_load_traces[i, j] = viral_load_trace
                self.specific_immunity_traces[i, j] = specific_immunity_trace

    def make_person_infected(self, person_id, viral_load=800):
        person = self.people[person_id]
        person.state = 'infected'
        person.viral_load = viral_load  # TODO (IvanKozlov98)
        person.a_id = int(min(round(person.treatment_rate * Model.TRACES_COUNT_A), Model.TRACES_COUNT_A - 1))
        person.b_id = int(min(round((person.start_treatment_time - 1) * Model.TRACES_COUNT_B / 10.0),
                          Model.TRACES_COUNT_B - 1))

    def _init_random_starting_infected_people(self, initial_infected_people_count):
        self.infected_people_ids = set(
            list(self.people.keys())[:initial_infected_people_count])  # ids infected persons in list of people
        for infected_person_id in self.infected_people_ids:
            self.make_person_infected(infected_person_id, nprnd.randint(self.VIR_LOAD_THRESHOLD, self.SEVERE_THRESHOLD))

    def __init__(self,
                 config_model,
                 config_virus,
                 config_cities,
                 use_cache_population=False,
                 cache_file_population=True):
        # init city
        location = Location(config_cities, use_cache=use_cache_population, cache_file=cache_file_population)
        self.people = location.get_population()
        # init virus
        Virus.init(config_virus)
        # init model parameters
        self.VIR_LOAD_THRESHOLD = int(get_value_from_config(config_model, Model._SECTION_CONFIG, 'VIR_LOAD_THRESHOLD'))
        self.MILD_THRESHOLD = int(get_value_from_config(config_model, Model._SECTION_CONFIG, 'MILD_THRESHOLD'))
        self.SEVERE_THRESHOLD = int(get_value_from_config(config_model, Model._SECTION_CONFIG, 'SEVERE_THRESHOLD'))
        self.DEAD_THRESHOLD = int(get_value_from_config(config_model, Model._SECTION_CONFIG, 'DEAD_THRESHOLD'))

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
        self.init_traces()

    def _get_new_random_contacts(self):
        new_random_contacts_count = self.number_random_contacts[self.ind_number_random_contacts]
        self.ind_number_random_contacts += 1
        new_random_contacts = []
        for _ in range(new_random_contacts_count):
            new_random_contacts.append((int(self.random_contacts[self.ind_random_contacts]), Model.RANDOM_INTERACTION))
            self.ind_random_contacts += 1
        return new_random_contacts

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
        giving_viral_load = interaction.degree * (infected_person.viral_load / 610) * (1 - contact_person.specific_immun)
        # update virus load of contact person
        contact_person.viral_load += giving_viral_load
        # update state of contact person if needed
        if contact_person.viral_load >= self.VIR_LOAD_THRESHOLD and contact_person.state == "healthy":
            self.make_person_infected(contact_person.id)
            return True
        return False

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
                if contact_person_id not in self.people:
                    continue
                is_infected = self.infect(infected_person, self.people[contact_person_id], interaction)
                if is_infected:
                    new_infected_ids.add(contact_person_id)

        return new_infected_ids

    # @staticmethod
    # def _update_viral_load(person):
    #     cur_viral_load = person.viral_load[-1]
    #     cur_viral_load *= Virus.spread_rate
    #     cur_viral_load *= (1 - person.specific_immun)
    #     cur_viral_load *= (1.2 - person.non_specific_immun)
    #     # update value
    #     person.viral_load.append(cur_viral_load)
    #     if len(person.viral_load) > 5:
    #         person.viral_load.popleft()

    # @staticmethod
    # def ff(prev_viral_load, alpha, prev_specific_immun, time):
    #     return alpha * (1 - prev_specific_immun) * (1 / (time + 1))

    # def _update_specific_immun(self, person):
    #     # prev_specific_immun = person.specific_immun
    #     # person.specific_immun = min(1, prev_specific_immun +
    #     #                             Model.ff(person.viral_load[0],
    #     #                                      0.6,
    #     #                                      prev_specific_immun,
    #     #                                      person.time_in_infected_state)
    #     #                             )
    #     person.recovering_time = min(19, person.recovering_time + person.recovering_rate)
    #     person.specific_immun = self.trace_specific_immun[person.recovering_time]

    def _is_mild_infected(self, person):
        return in_range(self.MILD_THRESHOLD, person.viral_load, self.SEVERE_THRESHOLD)

    def _is_severe_infected(self, person):
        return in_range(self.MILD_THRESHOLD, person.viral_load, 1000000)

    def _is_infected(self, person):
        return person.viral_load >= self.VIR_LOAD_THRESHOLD

    @staticmethod
    def _is_recovered(person):
        return person.viral_load < 5

    def _recovery_non_infected_people_step(self):
        for person in self.people.values():
            if person.state == "healthy":
                person.viral_load = 0

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
            infected_person.viral_load = self.viral_load_traces[infected_person.a_id, infected_person.b_id][
                infected_person.time_in_infected_state]
            infected_person.specific_immun = self.specific_immunity_traces[infected_person.a_id, infected_person.b_id][
                infected_person.time_in_infected_state]
            # Model._update_viral_load(infected_person)
            # self._update_specific_immun(infected_person)
            # Model._update_non_specific_immun(infected_person)
            # update time in infected state
            infected_person.time_in_infected_state += 1
            # update state of the infected person
            if infected_person.viral_load > self.DEAD_THRESHOLD:
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

    def update(self, num_day=None, debug_mode=True):
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
        if debug_mode:
            print(f"Day {num_day}; "
                  f"Number new infected people: {number_new_infected_people}; "
                  f"Number recovered people: {number_recovered_people}; " + '\033[0m', end='')

        # dead update
        for dead_id in dead_ids:
            self.people.pop(dead_id, None)
        # update infection group
        self.infected_people_ids.update(new_infected_people_ids)
        self.infected_people_ids.difference_update(recovered_people_ids)
        self.infected_people_ids.difference_update(dead_ids)
        number_all_infected_people = len(self.infected_people_ids)
        print(f"\033[0m Number all infected people: {number_all_infected_people}")

        return number_new_infected_people, number_recovered_people, number_all_infected_people, len(dead_ids)

    def run(self, debug_mode=True):
        """
        Run modeling
        """
        list_number_new_infected_people, list_number_recovered_people, list_number_all_infected_people, list_dead_people = [], [], [], []
        if debug_mode:
            print(f"Number of people: {len(self.people)}")
        for num_day in range(self.DAYS_COUNT):
            number_new_infected_people, number_recovered_people, number_all_infected_people, number_dead_people = self.update(
                num_day, debug_mode)
            list_number_new_infected_people.append(number_new_infected_people)
            list_number_recovered_people.append(number_recovered_people)
            list_number_all_infected_people.append(number_all_infected_people)
            list_dead_people.append(number_dead_people)

        time_game = np.arange(self.DAYS_COUNT)
        plt.plot(time_game, list_number_new_infected_people, label="number new infected people")
        plt.plot(time_game, list_number_recovered_people, label="number recovered people")
        plt.plot(time_game, list_number_all_infected_people, label="number all infected people")
        plt.plot(time_game, list_dead_people, label="number dead people")
        plt.xlabel("time (per day)")
        plt.legend()
        plt.show()
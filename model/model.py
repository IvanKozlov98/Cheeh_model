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
        if x == 0:
            xs.append(x + 0.00001)
        else:
            xs.append(x)

class ModelStats:
    def __init__(self):
        self.list_number_new_infected_people = []
        self.list_number_recovered_people = []
        self.list_number_all_infected_people = []
        self.list_dead_people = []
        self.list_mean_specific_immunity = []
        self.list_median_specific_immunity = []
        #
        self.list_number_asym_people = []
        self.list_number_light_people = []
        self.list_number_mild_people = []
        self.list_number_severe_people = []

    def add_values(self,
                   number_new_infected_people=None,
                   number_recovered_people=None,
                   number_all_infected_people=None,
                   dead_people=None,
                   mean_specific_immunity=None,
                   median_specific_immunity=None,
                   number_asym_people=None,
                   number_light_people=None,
                   number_mild_people=None,
                   number_severe_people=None):
        add_if(self.list_number_new_infected_people, number_new_infected_people)
        add_if(self.list_number_recovered_people, number_recovered_people)
        add_if(self.list_number_all_infected_people, number_all_infected_people)
        add_if(self.list_dead_people, dead_people)
        add_if(self.list_mean_specific_immunity, mean_specific_immunity)
        add_if(self.list_median_specific_immunity, median_specific_immunity)
        add_if(self.list_number_asym_people, number_asym_people)
        add_if(self.list_number_light_people, number_light_people)
        add_if(self.list_number_mild_people, number_mild_people)
        add_if(self.list_number_severe_people, number_severe_people)




class Box:
    def __init__(self, data: dict):
        self.data = data
        self.data_ind = dict((age, 0) for age in range(0, 100))

    def next(self, age):
        res = self.data[age][self.data_ind[age]]
        self.data_ind[age] += 1
        return res

class Model:
    _SECTION_CONFIG = "Model"
    RANDOM_INTERACTION = Interaction(type_interaction="Random", degree=10)  # TODO(IvanKozlov98) move to another place
    SMALL_GROUP_INTERACTION = Interaction(type_interaction="Work", degree=50)
    BIG_GROUP_INTERACTION = Interaction(type_interaction="Work", degree=20)

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

    def make_person_infected(self, person_id, viral_load):
        person = self.people[person_id]
        person.state = 'asymp'
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

    @staticmethod
    def get_probs_tr():
        prob_sym_dict = dict()
        prob_mild_dict = dict()
        prob_severe_dict = dict()
        prob_dead_dict = dict()
        for i in range(100):
            if i < 10:
                prob_sym_dict[i] = 0.5
                prob_mild_dict[i] = 0.0005
                prob_severe_dict[i] = 0.00003
                prob_dead_dict[i] = 0.00002
            elif i < 20:
                prob_sym_dict[i] = 0.55
                prob_mild_dict[i] = 0.00165
                prob_severe_dict[i] = 0.00008
                prob_dead_dict[i] = 0.00002
            elif i < 30:
                prob_sym_dict[i] = 0.6
                prob_mild_dict[i] = 0.00720
                prob_severe_dict[i] = 0.00036
                prob_dead_dict[i] = 0.00010
            elif i < 40:
                prob_sym_dict[i] = 0.65
                prob_mild_dict[i] = 0.0208
                prob_severe_dict[i] = 0.00104
                prob_dead_dict[i] = 0.00032
            elif i < 50:
                prob_sym_dict[i] = 0.7
                prob_mild_dict[i] = 0.0343
                prob_severe_dict[i] = 0.00216
                prob_dead_dict[i] = 0.00098
            elif i < 60:
                prob_sym_dict[i] = 0.75
                prob_mild_dict[i] = 0.0765
                prob_severe_dict[i] = 0.00933
                prob_dead_dict[i] = 0.00265
            elif i < 70:
                prob_sym_dict[i] = 0.8
                prob_mild_dict[i] = 0.1328
                prob_severe_dict[i] = 0.03639
                prob_dead_dict[i] = 0.00766
            elif i < 80:
                prob_sym_dict[i] = 0.85
                prob_mild_dict[i] = 0.20655
                prob_severe_dict[i] = 0.08923
                prob_dead_dict[i] = 0.02439
            elif i < 90:
                prob_sym_dict[i] = 0.9
                prob_mild_dict[i] = 0.2457
                prob_severe_dict[i] = 0.172
                prob_dead_dict[i] = 0.0892
            else:
                prob_sym_dict[i] = 0.9
                prob_mild_dict[i] = 0.2457
                prob_severe_dict[i] = 0.1742
                prob_dead_dict[i] = 0.1619
        return prob_sym_dict, prob_mild_dict, prob_severe_dict, prob_dead_dict


    def _init_solve_prob(self):
        people_by_age_dict = dict((age, 0) for age in range(0, 100))
        for person in self.people.values():
            people_by_age_dict[person.age] += 1

        prob_light_dict, prob_mild_dict, prob_severe_dict, prob_dead_dict = Model.get_probs_tr()
        solve_prob_light_dict = dict()
        solve_prob_mild_dict = dict()
        solve_prob_severe_dict = dict()
        solve_prob_dead_dict = dict()
        solve_prob_infected_dict = dict()

        for (age, cnt) in people_by_age_dict.items():
            solve_prob_infected_dict[age] = np.random.choice(2, size=self.DAYS_COUNT * cnt, p=[0.4, 0.6])
            solve_prob_light_dict[age] = np.random.choice(2, size=cnt, p=[1 - prob_light_dict[age], prob_light_dict[age]])
            solve_prob_mild_dict[age] = np.random.choice(2, size=cnt, p=[1 - prob_mild_dict[age], prob_mild_dict[age]])
            solve_prob_severe_dict[age] = np.random.choice(2, size=cnt, p=[1 - prob_severe_dict[age], prob_severe_dict[age]])
            solve_prob_dead_dict[age] = np.random.choice(2, size=cnt, p=[1 - prob_dead_dict[age], prob_dead_dict[age]])

        self.solve_prob_infected = Box(solve_prob_infected_dict)
        self.solve_prob_light = Box(solve_prob_light_dict)
        self.solve_prob_mild = Box(solve_prob_mild_dict)
        self.solve_prob_severe = Box(solve_prob_severe_dict)
        self.solve_prob_dead = Box(solve_prob_dead_dict)

    @staticmethod
    def create_func_obj(func_code_str):
        g = dict()
        l = dict()
        exec(func_code_str, g, l)
        if l:
            return list(l.values())[0]

    def _init_formulas(self, config_formulas):
        next_viral_load_func_code = "def _get_next_viral_load__(cur_viral_load, virus_spread_rate, specific_immun, non_specific_immun):\n    import numpy as np \n    return " + \
                                    get_value_from_config(config_formulas, "Formulas", 'VIRAL_LOAD_NEXT')
        self.next_viral_load_func = Model.create_func_obj(next_viral_load_func_code)
        ############
        next_specific_immun_func_code = "def _get_next_specific_immun__(cur_specific_immun, cur_viral_load, alpha):\n    import numpy as np \n    return " +\
                                        get_value_from_config(config_formulas, "Formulas", 'SPECIFIC_IMMUNITY_NEXT')
        self.next_specific_immun_func = Model.create_func_obj(next_specific_immun_func_code)
    #     giving_viral_load_func
        ############
        giving_viral_load_func_code = "def _giving_viral_load__(interaction_degree, viral_load, R, specific_immun):\n    import numpy as np \n    return " + \
                                        get_value_from_config(config_formulas, "Formulas", 'GIVING_INFECTED')
        self.giving_viral_load_func = Model.create_func_obj(giving_viral_load_func_code)

    def _init_time_infect(self):
        population_count = len(self.people)
        dist_not_sym_to_sym_time = get_lognormal_dist(4.5, 1.5, size=population_count).astype(int)
        dist_sym_to_mild_time = get_lognormal_dist(6.6, 4.9, size=population_count).astype(int)
        dist_mild_to_severe_time = get_lognormal_dist(1.5, 2.0, size=population_count).astype(int)
        dist_severe_to_death_time = get_lognormal_dist(10.7, 4.8, size=population_count).astype(int)

        dist_asym_to_recovery_time = get_lognormal_dist(8.0, 2.0, size=population_count).astype(int)
        dist_mild_to_revovery_time = get_lognormal_dist(18.1, 6.3, size=population_count).astype(int)
        dist_severe_to_recovery_time = get_lognormal_dist(18.1, 6.3, size=population_count).astype(int)
        dist_sym_to_recovery_time = get_lognormal_dist(8.0, 2.5, size=population_count).astype(int)

        # print(dist_not_sym_to_sym_time.mean(), dist_not_sym_to_sym_time.std())
        # print(dist_sym_to_mild_time.mean(), dist_sym_to_mild_time.std())
        # print(dist_mild_to_severe_time.mean(), dist_mild_to_severe_time.std())
        # print(dist_severe_to_death_time.mean(), dist_severe_to_death_time.std())
        #
        # print(dist_asym_to_recovery_time.mean(), dist_asym_to_recovery_time.std())
        # print(dist_mild_to_revovery_time.mean(), dist_mild_to_revovery_time.std())
        # print(dist_severe_to_recovery_time.mean(), dist_severe_to_recovery_time.std())
        # print(dist_sym_to_recovery_time.mean(), dist_sym_to_recovery_time.std())


        # print(dist_asym_to_recovery_time[:100])
        # print(dist_mild_to_revovery_time[:100])
        # print(dist_severe_to_recovery_time[:100])
        # print(dist_sym_to_recovery_time[:100])

        for (i, person_id) in enumerate(self.people.keys()):
            self.people[person_id].not_sym_to_sym_time = dist_not_sym_to_sym_time[i]
            self.people[person_id].sym_to_mild_time = dist_sym_to_mild_time[i]
            self.people[person_id].mild_to_severe_time = dist_mild_to_severe_time[i]
            self.people[person_id].severe_to_death_time = dist_severe_to_death_time[i]

            self.people[person_id].asym_to_recovery_time = dist_asym_to_recovery_time[i]
            self.people[person_id].mild_to_revovery_time = dist_mild_to_revovery_time[i]
            self.people[person_id].severe_to_recovery_time = dist_severe_to_recovery_time[i]
            self.people[person_id].sym_to_recovery_time = dist_sym_to_recovery_time[i]

    def __init__(self,
                 config_model,
                 config_virus,
                 config_cities,
                 config_formulas,
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
        self.R = self.VIR_LOAD_THRESHOLD / 1.3

        self._init_solve_prob()

        self._init_formulas(config_formulas)

        self.id_small_group_to_group = Location.get_id_group_to_group(self.people, is_small=True)
        self.id_big_group_to_group = Location.get_id_group_to_group(self.people, is_small=False)

        self._init_time_infect()


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

    # @staticmethod
    # def giving_viral_load_func(interaction_degree, viral_load, R, specific_immun):
    #     return interaction_degree * (viral_load / R) * (1 - specific_immun)

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
        giving_viral_load = self.giving_viral_load_func(
            interaction.degree,
            infected_person.viral_load[-1],
            self.R,
            contact_person.specific_immun
        )
        # update virus load of contact person
        contact_person.viral_load[-1] += giving_viral_load
        # update state of contact person if needed
        if contact_person.viral_load[-1] >= self.VIR_LOAD_THRESHOLD and contact_person.state == "healthy" and (not contact_person.flag_check_infected):
            contact_person.flag_check_infected = True
            if self.solve_prob_infected.next(contact_person.age):
                self.make_person_infected(contact_person.id, self.VIR_LOAD_THRESHOLD)
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

    @staticmethod
    def _get_next_viral_load(cur_viral_load, virus_spread_rate, specific_immun, non_specific_immun):
        return cur_viral_load * (1 + virus_spread_rate) * (1 - (specific_immun / 1.57)) * (1 - non_specific_immun)

    def _update_viral_load(self, person):
        # update value
        person.viral_load.append(self.next_viral_load_func(
            person.viral_load[-1],
            self.virus.spread_rate,
            person.specific_immun,
            person.non_specific_immun
        ))
        if len(person.viral_load) > person.lag_specific_immun:
            person.viral_load.popleft()

    @staticmethod
    def _get_next_specific_immun(cur_specific_immun, cur_viral_load, alpha):
        return np.arctan(cur_viral_load * alpha + cur_specific_immun)

    def _update_specific_immun(self, person):
        if person.time_in_infected_state > person.lag_specific_immun:
            person.specific_immun = self.next_specific_immun_func(
                person.specific_immun,
                person.viral_load[0],
                person.alpha
            )

    def _is_mild_infected(self, person):
        return in_range(self.MILD_THRESHOLD, person.viral_load[-1], self.SEVERE_THRESHOLD)

    def _is_severe_infected(self, person):
        return in_range(self.MILD_THRESHOLD, person.viral_load[-1], 1000000)

    def _is_infected(self, person):
        return person.viral_load[-1] >= self.VIR_LOAD_THRESHOLD

    @staticmethod
    def _is_recovered(person):
        return person.cur_asym_to_recovery_time == person.asym_to_recovery_time or \
                person.cur_light_to_recovery_time == person.light_to_recovery_time or \
                person.cur_mild_to_revovery_time == person.mild_to_revovery_time or \
                person.cur_severe_to_recovery_time == person.severe_to_recovery_time

    def _recovery_non_infected_people_step(self):
        for person in self.people.values():
            if person.state == "healthy":
                person.viral_load[-1] = 0
                person.flag_check_infected = False

    @staticmethod
    def _get_contact_list_mild(person):
        return person.home_contact_list

    @staticmethod
    def _get_contact_list_severe(person):
        return []

    def _get_small_group_list(self, person):
        return [(person_id, Model.SMALL_GROUP_INTERACTION) for person_id in self.id_small_group_to_group.get(person.small_group_id, [])]

    def _get_big_group_list(self, person):
        return [(person_id, Model.BIG_GROUP_INTERACTION) for person_id in
                self.id_big_group_to_group.get(person.big_group_id, [])]

    def _get_static_contact_list(self, person):
        return self._get_small_group_list(person) + self._get_big_group_list(person)

    def _get_contact_list_of_person(self, person):
        if person.state == 'mild':
            return Model._get_contact_list_mild(person)
        elif person.state == 'severe':
            return Model._get_contact_list_severe(person)
        return self._get_static_contact_list(person) + self._get_new_random_contacts()

    @staticmethod
    def _update_non_specific_immun(infected_person):
        pass

    def _get_mean_median_specific_immunity(self):
        list_sp_im = []
        for person in self.people.values():
            list_sp_im.append(person.specific_immun)
        list_sp_im = np.array(list_sp_im)
        return np.mean(list_sp_im), np.median(list_sp_im)

    def _get_diff_cases(self):
        number_asym_people = 0
        number_light_people = 0
        number_mild_people = 0
        number_severe_people = 0
        for person in self.people.values():
            number_asym_people += (person.state == 'asymp')
            number_light_people += (person.state == 'light')
            number_mild_people += (person.state == 'mild')
            number_severe_people += (person.state == 'severe')
        return (number_asym_people,
                number_light_people,
                number_mild_people,
                number_severe_people)

    def _update_state_infected_person(self, infected_person, dead_ids, recovered_ids):
        infected_person.time_in_infected_state += 1
        age = infected_person.age
        if infected_person.state == 'asymp':
            infected_person.cur_asym_to_light_time += 1
            infected_person.cur_asym_to_recovery_time += 1
            if (not infected_person.flag_check_light) and self.solve_prob_light.next(age):
                infected_person.state = 'light'
            infected_person.flag_check_light = True
        elif infected_person.state == 'light':
            infected_person.cur_light_to_mild_time += 1
            infected_person.cur_light_to_recovery_time += 1
            if (not infected_person.flag_check_mild) and self.solve_prob_mild.next(age):
                infected_person.state = 'mild'
            infected_person.flag_check_mild = True
        elif infected_person.state == 'mild':
            infected_person.cur_mild_to_severe_time += 1
            infected_person.cur_mild_to_revovery_time += 1
            if (not infected_person.flag_check_severe) and self.solve_prob_severe.next(age):
                infected_person.state = 'severe'
            infected_person.flag_check_severe = True
        elif infected_person.state == 'severe':
            infected_person.cur_severe_to_death_time += 1
            infected_person.cur_severe_to_recovery_time += 1
            if (not infected_person.flag_check_dead) and self.solve_prob_dead.next(age):
                infected_person.state = 'dead'
            infected_person.flag_check_dead = True
        # check if recovered
        if Model._is_recovered(infected_person):
            infected_person.state = 'healthy'
            infected_person.time_in_infected_state = 0
            recovered_ids.append(infected_person.id)

    def _update_state_of_infected_people_step(self):
        """
        Update state of infected people
        :return: list of ids recovered people and list of ids dead people
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
            # update state of the infected person
            self._update_state_infected_person(infected_person, dead_ids, recovered_ids)

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
        number_asym_people, number_light_people, number_mild_people, number_severe_people = self._get_diff_cases()

        if self.gui:
            self.model_stats.add_values(
                number_new_infected_people,
                number_recovered_people,
                number_all_infected_people,
                len(dead_ids),
                mean_specific_immunity,
                median_specific_immunity,
                number_asym_people,
                number_light_people,
                number_mild_people,
                number_severe_people
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

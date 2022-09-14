from builder_city import BuilderCity
from util import *
import random
from interaction import Interaction
from virus import Virus
import numpy.random as nprnd


class Model:
    _SECTION_CONFIG = "Model"
    RANDOM_INTERACTION = Interaction(type_interaction="Random", degree=3)  # TODO(IvanKozlov98) move to another place

    def __init__(self,
                 config_file="config/config.ini"):
        self.people = BuilderCity.build_city()
        Virus.init()

        self.VIR_LOAD_THRESHOLD = int(get_value_from_config(Model._SECTION_CONFIG, 'VIR_LOAD_THRESHOLD'))
        self.num_days = int(get_value_from_config(Model._SECTION_CONFIG, 'DAYS_COUNT'))
        # init starting infected people
        initial_infected_people_count = int(get_value_from_config(Model._SECTION_CONFIG, 'INITIAL_INFECTED_PEOPLE_COUNT'))
        self.infected_people_ids = set(list(self.people.keys())[:initial_infected_people_count])  # ids infected persons in list of people
        for infected_person_id in self.infected_people_ids:
            self.people[infected_person_id].state = 'infected'
            self.people[infected_person_id].viral_load[-1] = nprnd.randint(1000, 2000)

        self.trace_specific_immun = [1 / (1+np.exp(0.5*(-x + 10))) for x in np.linspace(0, 20, 20)]
        self.trace_specific_immun[-1] = 1
        self.mild_threshold = int(get_value_from_config(Model._SECTION_CONFIG, 'MILD_THRESHOLD'))
        self.severe_threshold = int(get_value_from_config(Model._SECTION_CONFIG, 'SEVERE_THRESHOLD'))

    def _update_new_random_contacts(self, infected_person):
        new_random_contacts_count = np.random.randint(low=3, high=15) # TODO (IvanKozlov98) it should be precalculated
        new_random_contacts = []
        for _ in range(new_random_contacts_count):
            new_random_contacts.append((random.choice(list(self.people.keys())), Model.RANDOM_INTERACTION))
        infected_person.random_contact_list = new_random_contacts

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
        giving_viral_load = interaction.degree * (infected_person.viral_load[-1] / 3000)
        # update virus load of contact person
        contact_person.viral_load[-1] += giving_viral_load
        # update state of contact person if needed
        if contact_person.viral_load[-1] > self.VIR_LOAD_THRESHOLD:
            contact_person.state = "infected"
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
            self._update_new_random_contacts(infected_person)
            # infect other people
            for (contact_person_id, interaction) in \
                    (infected_person.static_contact_list + infected_person.random_contact_list):
                is_infected = self.infect(infected_person, self.people[contact_person_id], interaction)
                if is_infected:
                    new_infected_ids.add(contact_person_id)

        return new_infected_ids

    @staticmethod
    def _update_viral_load(person):
        cur_viral_load = person.viral_load[-1]
        cur_viral_load *= Virus.spread_rate
        cur_viral_load *= (1 - person.specific_immun)
        cur_viral_load *= (1.2 - person.non_specific_immun)
        # update value
        person.viral_load.append(cur_viral_load)
        if len(person.viral_load) > 5:
            person.viral_load.popleft()

    # @staticmethod
    # def ff(prev_viral_load, alpha, prev_specific_immun, time):
    #     return alpha * (1 - prev_specific_immun) * (1 / (time + 1))

    def _update_specific_immun(self, person):
        # prev_specific_immun = person.specific_immun
        # person.specific_immun = min(1, prev_specific_immun +
        #                             Model.ff(person.viral_load[0],
        #                                      0.6,
        #                                      prev_specific_immun,
        #                                      person.time_in_infected_state)
        #                             )
        person.recovering_time = min(19, person.recovering_time + person.recovering_rate)
        person.specific_immun = self.trace_specific_immun[person.recovering_time]

    @staticmethod
    def _update_non_specific_immun(person):
        pass

    @staticmethod
    def _is_recovered(person):
        return person.viral_load[-1] == 0

    def _recovery_non_infected_people_step(self):
        for person in self.people.values():
            if person.state == "healthy":
                person.viral_load[-1] = 0

    @staticmethod
    def _update_contact_list_mild(person):
        pass

    @staticmethod
    def _update_contact_list_severe(person):
        pass


    @staticmethod
    def _recover_contact_lists(person):
        pass

    @staticmethod
    def _update_person_after_treatment(person):
        person.state = 'recovered'
        # print(f"Recovering time: {infected_person.time_in_infected_state}")
        person.time_in_infected_state = 0

    def _update_state_of_infected_people_step(self):
        """
        Update state of infected people
        :return: list of ids recovered people
        """
        recovered_ids = []
        # see to current state of agent and starting day
        for infected_person_id in self.infected_people_ids:
            infected_person = self.people[infected_person_id]
            # update different parameters
            Model._update_viral_load(infected_person)
            self._update_specific_immun(infected_person)
            Model._update_non_specific_immun(infected_person)
            # update time in infected state
            infected_person.time_in_infected_state += 1
            # ...
            # update his contacts
            if infected_person.viral_load[-1] >= self.mild_threshold:
                Model._update_contact_list_mild(infected_person)
            elif infected_person.viral_load[-1] >= self.severe_threshold:
                Model._update_contact_list_severe(infected_person)
            # check if recovered
            if Model._is_recovered(infected_person):
                Model._update_person_after_treatment(infected_person)
                recovered_ids.append(infected_person_id)

        return recovered_ids

    def update(self, num_day=None, debug_mode=True):
        """
        Update state of model from one day to another
        """
        # step infection
        new_infected_people_ids = self._spread_infection_step()
        # step updating params for infected people
        recovered_people_ids = self._update_state_of_infected_people_step()
        # step updating params for non-infected people
        self._recovery_non_infected_people_step()
        # update infection group
        self.infected_people_ids.update(new_infected_people_ids)
        self.infected_people_ids.difference_update(recovered_people_ids)

        if debug_mode:
            print(f"Day {num_day}; Number infected people: {len(self.infected_people_ids)}; Number new infected people: {len(new_infected_people_ids)}; Number recovered people: {len(recovered_people_ids)}")


    def run(self, debug_mode=True):
        """
        Run modeling
        """
        if debug_mode:
            print(f"Number of people: {len(self.people)}")
        for num_day in range(self.num_days):
            self.update(num_day, debug_mode)


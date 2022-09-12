from builder_city import BuilderCity
from person import Person
from util import *
from virus import Virus

class Model:
    _SECTION_CONFIG = "Model"
    def __init__(self,
                 config_file="config/config.ini",
                 num_days=365):
        self.people = BuilderCity.build_city()
        Virus.init()

        self.VIR_LOAD_THRESHOLD = int(get_value_from_config(Model._SECTION_CONFIG, 'VIR_LOAD_THRESHOLD'))
        self.num_days = num_days
        self.infected_people_ids = set()  # ids infected persons in list of people

    # должно быть 2 способа инициализации - через параметры, и через конфиг-файл

    @staticmethod
    def _update_new_random_contacts(infected_person):
        pass

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
        giving_virus_load = infected_person.virus_load / 10
        # update virus load of contact person
        contact_person.virus_load += giving_virus_load
        # update state of contact person if needed
        if contact_person.virus_load > self.VIR_LOAD_THRESHOLD:
            contact_person.state = "infected"
            return True
        return False

    def _spread_infection_step(self):
        """
        Infection step
        :return: set of ids new infected people
        """
        new_infected_ids = []
        for infected_person_id in self.infected_people_ids:
            # update new contacts infected people
            infected_person = self.people[infected_person_id]
            Model._update_new_random_contacts(infected_person)
            # infect other people
            for (contact_person, interaction) in \
                    (infected_person.static_contact_list + infected_person.random_contact_list):
                is_infected = self.infect(infected_person, contact_person, interaction)
                if is_infected:
                    new_infected_ids.append(contact_person.id)

        return new_infected_ids

    @staticmethod
    def _update_virus_load(person):
        cur_virus_load = person.virus_load
        cur_virus_load *= Virus.spread_rate
        cur_virus_load *= person.specific_immun
        cur_virus_load *= person.non_specific_immun
        # update value
        person.virus_load = cur_virus_load


    @staticmethod
    def _update_specific_immun(person):
        pass

    @staticmethod
    def _update_non_specific_immun(person):
        pass

    @staticmethod
    def _is_recovered(person):
        return person.virus_load == 0

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
            Model._update_virus_load(infected_person)
            Model._update_specific_immun(infected_person)
            Model._update_non_specific_immun(infected_person)
            ...
            # check if recovered
            if Model._is_recovered(infected_person):
                recovered_ids.append(infected_person_id)

        return recovered_ids

    def update(self):
        """
        Update state of model from one day to another
        """
        # step infection
        new_infected_people_ids = self._spread_infection_step()
        # step updating params for infected people
        recovered_people_ids = self._update_state_of_infected_people_step()
        # update infection group
        self.infected_people_ids.update(new_infected_people_ids)
        self.infected_people_ids.difference_update(recovered_people_ids)

    def run(self, debug_mode=True):
        """
        Run modeling
        """
        if debug_mode:
            print(f"Number of people: {len(self.people)}")
        for num_day in range(self.num_days):
            self.update()
            if debug_mode:
                print(f"Number infected people: {len(self.infected_people_ids)}")

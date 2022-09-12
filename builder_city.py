from util import *
from person import Person
from scipy.stats import norminvgauss
from random import choices
import numpy.random as nprnd


class BuilderCity:
    _SECTION_CONFIG = "City"
    # _EARLIER_AGE_BEAR = 18
    # _LATE_AGE_BEAR = 35


    @staticmethod
    def get_people(age_distribution, gender):
        """
        :return: people (woman or man) with given distribution
        """
        people = dict()
        for age in age_distribution:
            person = Person(age, gender)
            people[person.id] = person
        return people

    @staticmethod
    def get_man_age_distribution(n):
        dist = np.array(list(map(int, nprnd.lognormal(3, 1, n))))
        dist[dist >= 100] = 99
        return dist

    @staticmethod
    def get_woman_age_distribution(n):
        return BuilderCity.get_man_age_distribution(n)

    @staticmethod
    def get_pairs(man, woman):
        """Simple create pairs"""
        return list(zip({k: v for k, v in sorted(man.items(), key=lambda item: item[1].age)},
                        {k: v for k, v in sorted(woman.items(), key=lambda item: item[1].age)}))


    @staticmethod
    def connect_parent_with_child(m, w, child):
        m.static_contact_list.append(child.id)
        w.static_contact_list.append(child.id)
        # TODO (IvanKozlov98) to add inheritance immunity


    @staticmethod
    def get_children_prob_by_age():
        """
        здесь предположение, что максимальное кол-во детей равно 4
        """
        ps = dict()
        ps[18] = [0.9, 0.1, 0, 0, 0]
        ps[19] = [0.8, 0.2, 0, 0, 0]
        ps[20] = [0.7, 0.3, 0, 0, 0]
        ps[21] = [0.7, 0.3, 0, 0, 0]
        ps[22] = [0.7, 0.25, 0.05, 0, 0]
        ps[23] = [0.6, 0.3, 0.1, 0, 0]
        ps[24] = [0.5, 0.3, 0.2, 0, 0]
        ps[25] = [0.4, 0.3, 0.3, 0, 0]
        for age in range(26, 100):
            ps[age] = [0.3, 0.4, 0.2, 0.07, 0.03]
        return ps


    @staticmethod
    def get_children_count_by_age(children_prob_by_age, number_girl_by_age):
        children_count_by_age = dict()
        for (age_bear, ps) in children_prob_by_age.items():
            children_count_by_age[age_bear] = nprnd.choice(5, size=number_girl_by_age[age_bear], p=ps)
        return children_count_by_age


    @staticmethod
    def build_city():
        """

        :return: dict of people with static contacts {people_id -> people}
        """
        np.random.seed(42)
        population_count = int(get_value_from_config(BuilderCity._SECTION_CONFIG, 'POPULATION_COUNT'))
        name_location = get_value_from_config(BuilderCity._SECTION_CONFIG, 'NAME_LOCATION')
        # 1 step: create man and woman with given age
        man_count = round(population_count * 0.45)
        woman_count = population_count - man_count

        man = BuilderCity.get_people(BuilderCity.get_man_age_distribution(man_count), 'm')
        woman = BuilderCity.get_people(BuilderCity.get_man_age_distribution(woman_count), 'w')

        people = dict()
        people.update(man)
        people.update(woman)

        # 2 step: make pairs
        pairs = BuilderCity.get_pairs({k: v for k, v in man.items() if v.age >= 18},
                                      {k: v for k, v in woman.items() if v.age >= 18})
        for (man_id, woman_id) in pairs:
            people[man_id].static_contact_list.append(woman_id)
            people[woman_id].static_contact_list.append(man_id)

        # 3 step: assign children
        # prepare dop.variables
        id_people_by_age = dict((age, []) for age in range(0, 100))
        number_girl_by_age = dict((age, 0) for age in range(0, 100))
        ind_children_count_by_age = dict((age, 0) for age in range(0, 100))
        ind_id_people_by_age = dict((age, 0) for age in range(0, 100))

        for (person_id, person) in people.items():
            id_people_by_age[person.age].append(person_id)
            if person.gender == 'w':
                number_girl_by_age[person.age] += 1

        children_count_by_age = BuilderCity.get_children_count_by_age(BuilderCity.get_children_prob_by_age(),
                                                                      number_girl_by_age)
        # assign children
        for (man_id, woman_id) in pairs:
            w_age = people[woman_id].age

            children_count = children_count_by_age[w_age][ind_children_count_by_age[w_age]]
            ind_children_count_by_age[w_age] += 1

            children_ages = nprnd.randint(w_age - 18 + 1, size=children_count) # TODO(IvanKozlov98) very slowly
            # assign children with given age
            for child_age in children_ages:
                if ind_id_people_by_age[child_age] >= len(id_people_by_age[child_age]):
                    continue
                child_id = id_people_by_age[child_age][ind_id_people_by_age[child_age]]
                ind_id_people_by_age[child_age] += 1
                BuilderCity.connect_parent_with_child(people[man_id], people[woman_id], people[child_id])

        return people


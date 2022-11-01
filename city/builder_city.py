from util.util import *
from model.person import Person
from model.interaction import Interaction

import numpy as np
import pandas as pd
import numpy.random as nprnd
from scipy.stats import norm


class BuilderCity:

    # TODO(IvanKozlov98) move to another place
    PARENT_CHILD_INTERACTION = Interaction(type_interaction="Home", degree=50)
    PAIR_INTERACTION = Interaction(type_interaction="Home", degree=80)
    SMALL_GROUP_INTERACTION = Interaction(type_interaction="Work", degree=30)
    BIG_GROUP_INTERACTION = Interaction(type_interaction="Work", degree=10)

    # _EARLIER_AGE_BEAR = 18
    # _LATE_AGE_BEAR = 35
    small_group_sizes_ind = None
    big_group_sizes_1_ind = None
    big_group_sizes_2_ind = None
    big_group_sizes_3_ind = None


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
    def get_man_age_distribution(n, dist):
        return np.random.choice(100, size=n, p=np.array(dist / np.sum(dist)))

    @staticmethod
    def get_pairs(man, woman):
        """Simple create pairs"""
        return list(zip({k: v for k, v in sorted(man.items(), key=lambda item: item[1].age)},
                        {k: v for k, v in sorted(woman.items(), key=lambda item: item[1].age)}))


    @staticmethod
    def connect_persons(p1, p2, interaction):
        p1.static_contact_list.append((p2.id, interaction))
        p2.static_contact_list.append((p1.id, interaction))
        # TODO (IvanKozlov98) to add inheritance immunity

    @staticmethod
    def connect_parent_with_child(m, w, child):
        BuilderCity.connect_persons(m, child, BuilderCity.PARENT_CHILD_INTERACTION)
        BuilderCity.connect_persons(w, child, BuilderCity.PARENT_CHILD_INTERACTION)
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
    def conn_group(people, group, interaction):
        group_size = len(group)
        if group_size == 0:
            return
        for ind_person_1 in range(group_size):
            for ind_person_2 in range(group_size):
                if ind_person_1 == ind_person_2:
                    continue
                BuilderCity.connect_persons(people[group[ind_person_1]], people[group[ind_person_2]], interaction)

    @staticmethod
    def group_by_workspace_impl(people, ids_people_by_age, big_group_sizes_1_ind, big_group_sizes_2_ind, big_group_sizes_3_ind, small_group_sizes):
        ind_small_group = 0
        for age in range(3, 100):
            big_group_inds = big_group_sizes_1_ind if age < 25 else big_group_sizes_2_ind if age < 60 else big_group_sizes_3_ind
            people_ids_with_same_old = ids_people_by_age[age]
            np.random.shuffle(people_ids_with_same_old)
            big_groups = np.split(people_ids_with_same_old, big_group_inds)
            for big_group in big_groups:
                BuilderCity.conn_group(people, big_group, BuilderCity.BIG_GROUP_INTERACTION)
                cur_big_group_people = 0
                while cur_big_group_people < len(big_group):
                    next_cur_big_group_people = cur_big_group_people + small_group_sizes[ind_small_group]
                    BuilderCity.conn_group(people, big_group[cur_big_group_people : next_cur_big_group_people], BuilderCity.SMALL_GROUP_INTERACTION)
                    # update indices
                    ind_small_group += 1
                    cur_big_group_people = next_cur_big_group_people


    @staticmethod
    def get_group_sizes(population_count,
                    small_group_sizes_mean,
                   small_group_sizes_sigma,
                   big_group_sizes_mean_1,
                   big_group_sizes_sigma_1,
                   big_group_sizes_mean_2,
                   big_group_sizes_sigma_2,
                   big_group_sizes_mean_3,
                   big_group_sizes_sigma_3):
        return (np.abs(norm.rvs(loc=small_group_sizes_mean, scale=small_group_sizes_sigma, size=population_count)).astype(int),
            np.add.accumulate(np.abs(norm.rvs(loc=big_group_sizes_mean_1, scale=big_group_sizes_sigma_1, size=population_count))).astype(int),
            np.add.accumulate(np.abs(norm.rvs(loc=big_group_sizes_mean_2, scale=big_group_sizes_sigma_2, size=population_count))).astype(int),
            np.add.accumulate(np.abs(norm.rvs(loc=big_group_sizes_mean_3, scale=big_group_sizes_sigma_3, size=population_count))).astype(int))

    @staticmethod
    def get_ids_people_by_age(people):
        ids_people_by_age = dict((age, []) for age in range(0, 100))
        for (person_id, person) in people.items():
            ids_people_by_age[person.age].append(person_id)
        return ids_people_by_age

    @staticmethod
    def group_by_workspace(people,
                    small_group_sizes_mean,
                   small_group_sizes_sigma,
                   big_group_sizes_mean_1,
                   big_group_sizes_sigma_1,
                   big_group_sizes_mean_2,
                   big_group_sizes_sigma_2,
                   big_group_sizes_mean_3,
                   big_group_sizes_sigma_3):
        # 1 step
        (small_group_sizes, big_group_sizes_1_ind, big_group_sizes_2_ind, big_group_sizes_3_ind) = BuilderCity.get_group_sizes(
          population_count=len(people),
          small_group_sizes_mean=small_group_sizes_mean,
          small_group_sizes_sigma=small_group_sizes_sigma,
          big_group_sizes_mean_1=big_group_sizes_mean_1,
          big_group_sizes_sigma_1=big_group_sizes_sigma_1,
          big_group_sizes_mean_2=big_group_sizes_mean_2,
          big_group_sizes_sigma_2=big_group_sizes_sigma_2,
          big_group_sizes_mean_3=big_group_sizes_mean_3,
          big_group_sizes_sigma_3=big_group_sizes_sigma_3)
        # 2 step
        ids_people_by_age = BuilderCity.get_ids_people_by_age(people)
        # 3 step
        BuilderCity.group_by_workspace_impl(people, ids_people_by_age, big_group_sizes_1_ind, big_group_sizes_2_ind,
                                big_group_sizes_3_ind, small_group_sizes)

    @staticmethod
    def build_city(population_count,
                   small_group_sizes_mean,
                   small_group_sizes_sigma,
                   big_group_sizes_mean_1,
                   big_group_sizes_sigma_1,
                   big_group_sizes_mean_2,
                   big_group_sizes_sigma_2,
                   big_group_sizes_mean_3,
                   big_group_sizes_sigma_3
                   ):
        """

        :return: dict of people with static contacts {people_id -> people}
        """
        # Person.static_init()
        np.random.seed(42)
        # 1 step: create man and woman with given age
        data_age_gender = pd.read_csv('city/age_gender_russia.csv')
        male_age = np.array(data_age_gender['Male']).astype(int)
        female_age = np.array(data_age_gender['Female']).astype(int)
        man_ratio = np.sum(male_age) / (np.sum(male_age) + np.sum(female_age))

        man_count = round(population_count * man_ratio)
        woman_count = population_count - man_count

        man = BuilderCity.get_people(BuilderCity.get_man_age_distribution(man_count, male_age), 'm')
        woman = BuilderCity.get_people(BuilderCity.get_man_age_distribution(woman_count, female_age), 'w')

        people = dict()
        people.update(man)
        people.update(woman)

        # 2 step: make pairs
        pairs = BuilderCity.get_pairs({k: v for k, v in man.items() if v.age >= 18},
                                      {k: v for k, v in woman.items() if v.age >= 18})
        for (man_id, woman_id) in pairs:
            BuilderCity.connect_persons(people[man_id], people[woman_id], BuilderCity.PAIR_INTERACTION)

        # 3 step: assign children
        # prepare dop.variables
        ids_people_by_age = dict((age, []) for age in range(0, 100))
        number_girl_by_age = dict((age, 0) for age in range(0, 100))
        ind_children_count_by_age = dict((age, 0) for age in range(0, 100))
        ind_ids_people_by_age = dict((age, 0) for age in range(0, 100))

        for (person_id, person) in people.items():
            ids_people_by_age[person.age].append(person_id)
            if person.gender == 'w':
                number_girl_by_age[person.age] += 1

        children_count_by_age = BuilderCity.get_children_count_by_age(BuilderCity.get_children_prob_by_age(),
                                                                      number_girl_by_age)
        # assign children
        for (man_id, woman_id) in pairs:
            w_age = people[woman_id].age

            children_count = children_count_by_age[w_age][ind_children_count_by_age[w_age]]
            ind_children_count_by_age[w_age] += 1

            children_ages = nprnd.randint(w_age - 18 + 1, size=children_count)  # TODO(IvanKozlov98) very slowly
            # assign children with given age
            for child_age in children_ages:
                if ind_ids_people_by_age[child_age] >= len(ids_people_by_age[child_age]):
                    continue
                child_id = ids_people_by_age[child_age][ind_ids_people_by_age[child_age]]
                ind_ids_people_by_age[child_age] += 1
                BuilderCity.connect_parent_with_child(people[man_id], people[woman_id], people[child_id])

        # 4 step: group by small/big group(kindergarten, school, work)
        # BuilderCity.group_by_workspace(people,
        #             small_group_sizes_mean,
        #            small_group_sizes_sigma,
        #            big_group_sizes_mean_1,
        #            big_group_sizes_sigma_1,
        #            big_group_sizes_mean_2,
        #            big_group_sizes_sigma_2,
        #            big_group_sizes_mean_3,
        #            big_group_sizes_sigma_3)

        return people

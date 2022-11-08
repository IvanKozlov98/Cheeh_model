from city.builder_city import BuilderCity
from util.util import *
import pickle
import os
import numpy as np


class Location:
    _SECTION_CONFIG = "City"

    @staticmethod
    def get_id_group_to_group(people, is_small):
        id_group_to_group = dict()
        for person in people.values():
            group_id = person.small_group_id if is_small else person.big_group_id
            if group_id == -1:
                continue
            if group_id in id_group_to_group:
                id_group_to_group[group_id].append(person.id)
            else:
                id_group_to_group[group_id] = [person.id]
        return id_group_to_group



    def __init__(self, config_file, use_cache=True, cache_file=True):
        population_count = int(get_value_from_config(config_file, Location._SECTION_CONFIG, 'POPULATION_COUNT'))
        self.name_location = get_value_from_config(config_file, Location._SECTION_CONFIG, 'NAME_LOCATION')

        file_with_population = Location._get_filename_city(population_count, self.name_location)
        small_group_sizes_mean = int(get_value_from_config(config_file, Location._SECTION_CONFIG, 'SMALL_GROUP_SIZE_MEAN')),
        small_group_sizes_sigma = int(get_value_from_config(config_file, Location._SECTION_CONFIG, 'SMALL_GROUP_SIZE_SIGMA')),
        big_group_sizes_mean_1 = int(get_value_from_config(config_file, Location._SECTION_CONFIG, 'BIG_GROUP_SIZE_UP_25_MEAN')),
        big_group_sizes_sigma_1 = int(get_value_from_config(config_file, Location._SECTION_CONFIG, 'BIG_GROUP_SIZE_UP_25_SIGMA')),
        big_group_sizes_mean_2 = int(get_value_from_config(config_file, Location._SECTION_CONFIG, 'BIG_GROUP_SIZE_UP_60_MEAN')),
        big_group_sizes_sigma_2 = int(get_value_from_config(config_file, Location._SECTION_CONFIG, 'BIG_GROUP_SIZE_UP_60_SIGMA')),
        big_group_sizes_mean_3 = int(get_value_from_config(config_file, Location._SECTION_CONFIG, 'BIG_GROUP_SIZE_AFTER_60_MEAN')),
        big_group_sizes_sigma_3 = int(get_value_from_config(config_file, Location._SECTION_CONFIG, 'BIG_GROUP_SIZE_AFTER_60_SIGMA'))

        # if use_cache and os.path.isfile(file_with_population):
        #     print("Loading population from cache")
        #     with open(file_with_population, 'rb') as f:
        #         self.people = pickle.load(f)
        # else:
        print("Start build population...")
        self.people = BuilderCity.build_city(
            population_count,
            small_group_sizes_mean=small_group_sizes_mean,
            small_group_sizes_sigma=small_group_sizes_sigma,
            big_group_sizes_mean_1=big_group_sizes_mean_1,
            big_group_sizes_sigma_1=big_group_sizes_sigma_1,
            big_group_sizes_mean_2=big_group_sizes_mean_2,
            big_group_sizes_sigma_2=big_group_sizes_sigma_2,
            big_group_sizes_mean_3=big_group_sizes_mean_3,
            big_group_sizes_sigma_3=big_group_sizes_sigma_3
        )
        print("End builing population.")
            # if cache_file:
            #     with open(file_with_population, 'wb') as f:
            #         pickle.dump(self.people, f)
        print("Grouping people")
        BuilderCity.group_by_workspace(self.people,
                                       small_group_sizes_mean,
                                       small_group_sizes_sigma,
                                       big_group_sizes_mean_1,
                                       big_group_sizes_sigma_1,
                                       big_group_sizes_mean_2,
                                       big_group_sizes_sigma_2,
                                       big_group_sizes_mean_3,
                                       big_group_sizes_sigma_3)

    @staticmethod
    def _get_filename_city(population_count, name_location):
        return "cache_data/" + name_location + str(population_count) + ".pkl"

    def get_population(self):
        return self.people

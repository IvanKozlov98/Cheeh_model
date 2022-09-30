from city.builder_city import BuilderCity
from util.util import *
import pickle
import os


class Location:
    _SECTION_CONFIG = "City"

    def __init__(self, config_file, use_cache=False, cache_file=True):
        population_count = int(get_value_from_config(config_file, Location._SECTION_CONFIG, 'POPULATION_COUNT'))
        self.name_location = get_value_from_config(config_file, Location._SECTION_CONFIG, 'NAME_LOCATION')

        file_with_population = Location._get_filename_city(population_count, self.name_location)
        if use_cache and os.path.isfile(file_with_population):
            print("Loading population from cache")
            with open(file_with_population, 'rb') as f:
                self.people = pickle.load(f)
        else:
            print("Start build population...")
            self.people = BuilderCity.build_city(population_count)
            print("End builing population.")
            if cache_file:
                with open(file_with_population, 'wb') as f:
                    pickle.dump(self.people, f)

    @staticmethod
    def _get_filename_city(population_count, name_location):
        return "../cache_data/" + name_location + str(population_count) + ".pkl"

    def get_population(self):
        return self.people

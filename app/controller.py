from model.model import Model
from util.util import *


class Controller:

    def __init__(self):
        self.model = None

    def create_model(self, model_config, city_config, virus_config, view):
        # here we initialize Model
        self.model = Model(
            config_model=model_config,
            config_virus=virus_config,
            config_cities=city_config,
            gui=True
        )
        self.model.set_view(view)
        return self.model

    def save_config(self, config_file, config_dict, section):
        save_dict_as_config(dict_=config_dict, filename=config_file, section=section)

    def stop(self):
        self.model.stop_running()
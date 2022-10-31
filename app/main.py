from model.model import Model
from app.controller import Controller
from gui.gui import GuiApp

import numpy as np
import argparse


def parse_cmdline():
    parser = argparse.ArgumentParser(description="TODO.")
    parser.add_argument("-v", "--virus_config", type=str, help="file with config virus", required=False)
    parser.add_argument("-m", "--model_config", type=str, help="file with config model", required=False)
    parser.add_argument("-c", "--city_config", type=str, help="file with config city", required=False)
    parser.add_argument("-f", "--formulas_config", type=str, help="file with formulas", required=False)
    args = parser.parse_args()
    return args


def run_cmdline_version(virus_config, model_config, city_config, formulas_config):
    model = Model(
        config_model=model_config,
        config_virus=virus_config,
        config_cities=city_config,
        formulas_config=formulas_config,
        use_cache_population=True,
        cache_file_population=True,
        gui=False
    )
    model.run()


def main():
    args = parse_cmdline()
    np.random.seed(42)
    if (args.virus_config is not None) or\
            (args.model_config is not None) or\
            (args.city_config is not None) or\
            (args.formulas_config is not None):
        if args.virus_config is None:
            print("Virus config must be defined")
        if args.model_config is None:
            print("Model config must be defined")
        if args.city_config is None:
            print("City config must be defined")
        if args.formulas_config is None:
            print("Formulas config must be defined")
        run_cmdline_version(
            virus_config=args.virus_config,
            model_config=args.model_config,
            city_config=args.city_config,
            formulas_config=args.formulas_config)
    else:
        controller = Controller()
        gui_app = GuiApp(controller)
        gui_app.run()


if __name__ == '__main__':
    main()


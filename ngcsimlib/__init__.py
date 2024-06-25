from . import utils
from . import controller
from . import commands

import argparse, os, json
from types import SimpleNamespace
from importlib import import_module
from ngcsimlib.configManager import init_config, get_config
from ngcsimlib.logger import warn
from pkg_resources import get_distribution

__version__ = get_distribution('ngcsimlib').version  ## set software version


###### Preload Modules
def preload_modules(path=None):
    if path is None:
        module_config = get_config("modules")
        if module_config is None:
            module_path = None
        else:
            module_path = module_config.get("module_path", None)

        if module_path is None:
            return

        if not os.path.isfile(module_path):
            warn("Missing file to preload modules from. Attempted to locate file at \"" + str(module_path) +
                          "\". No modules will be preloaded. "
                          "\nSee https://ngc-learn.readthedocs.io/en/latest/tutorials/model_basics/json_modules.html for additional information")
            return
    else:
        module_path = path

    with open(module_path, 'r') as file:
        modules = json.load(file, object_hook=lambda d: SimpleNamespace(**d))

    for module in modules:
        mod = import_module(module.absolute_path)
        utils.modules._Loaded_Modules[module.absolute_path] = mod

        for attribute in module.attributes:
            atr = getattr(mod, attribute.name)
            utils.modules._Loaded_Attributes[attribute.name] = atr

            utils.modules._Loaded_Attributes[".".join([module.absolute_path, attribute.name])] = atr
            if hasattr(attribute, "keywords"):
                for keyword in attribute.keywords:
                    utils.modules._Loaded_Attributes[keyword] = atr

    utils.set_loaded(True)

###### Initialize Config
def configure():
    parser = argparse.ArgumentParser(description='Build and run a model using ngclearn')
    parser.add_argument("--config", type=str, help='location of config.json file')

    ## ngc-sim-lib only cares about --config argument
    args, unknown = parser.parse_known_args()  # args = parser.parse_args()
    try:
        config_path = args.modules
    except:
        config_path = None

    if config_path is None:
        config_path = "json_files/config.json"

    if not os.path.isfile(config_path):
        warn("Missing configuration file. Attempted to locate file at \"" + str(config_path) +
                      "\". Default Config will be used. "
                      "\nSee https://ngc-learn.readthedocs.io/en/latest/tutorials/model_basics/configuration.html for "
                      "additional information")
        return

    init_config(config_path)

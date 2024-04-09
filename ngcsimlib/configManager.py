"""
ngc libraries have a need for global level configuration which will all be
handled here. It will also be possible to add custom configuration sections to
this file with no issues or additional setup. However, the main purpose of these
configurations are not control specific parts of the model but control ngc
libraries at a high level.
"""
import json
from types import SimpleNamespace


class ConfigManager:
    def __init__(self):
        self.loadedConfig = None

    def init_config(self, path):
        with open(path, 'r') as file:
            self.loadedConfig = json.load(file)

    def get_config(self, name):
        if self.loadedConfig is None:
            return None

        if name not in self.loadedConfig.keys():
            return None

        return self.loadedConfig.get(name, None)

    def provide_namespace(self, configName):
        config = self.get_config(configName)
        if config is None:
            return None
        else:
            return SimpleNamespace(**config)


_GlobalConfig = ConfigManager()


def init_config(path):
    _GlobalConfig.init_config(path)


def get_config(configName):
    return _GlobalConfig.get_config(configName)


def provide_namespace(configName):
    return _GlobalConfig.provide_namespace(configName)

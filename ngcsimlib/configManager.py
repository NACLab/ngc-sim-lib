"""
ngc libraries have a need for global level configuration which will all be
handled here. It will also be possible to add custom configuration sections to
this file with no issues or additional setup. However the main purpose of these
configurations are not control specific parts of the model but control ngc
libraries at a high level.
"""
import json


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


GlobalConfig = ConfigManager()

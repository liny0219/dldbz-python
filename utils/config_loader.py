import json
# import os


class ConfigLoader:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config_data = self._load_config()

    def _load_config(self):
        with open(self.config_file, 'r', encoding='utf-8') as file:
            return json.load(file)

    def get(self, key_path, default=None):
        keys = key_path.split('.')
        value = self.config_data
        try:
            for key in keys:
                value = value[key]
            return value
        except KeyError:
            return default

    def reload(self):
        self.config_data = self._load_config()


def reload_config():
    cfg_startup.reload()
    cfg_monopoly.reload()


cfg_version = ConfigLoader('./config/version.json')
cfg_engine = ConfigLoader('./config/engine.json')
cfg_startup = ConfigLoader('./config/startup.json')
cfg_monopoly = ConfigLoader('./config/monopoly.json')
cfg_recollection = ConfigLoader('./config/recollection.json')

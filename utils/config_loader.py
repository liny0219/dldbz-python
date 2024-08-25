import json
# import os
class ConfigLoader:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config_data = self._load_config()

    def _load_config(self):
        with open(self.config_file, 'r') as file:
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


cfg_startup = ConfigLoader('./config/startup.json')
cfg_common = ConfigLoader('./config/common.json')
cfg_world = ConfigLoader('./config/world.json')
cfg_battle = ConfigLoader('./config/battle.json')
cfg_monopoly = ConfigLoader('./config/monopoly.json')
cfg_recollection = ConfigLoader('./config/recollection.json')



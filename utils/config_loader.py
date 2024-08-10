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


# 创建一个全局的 ConfigLoader 实例，以便其他模块可以导入
file_name = 'D:\\Python_stuff\\game_script\\dldbz-python_ver\\python-dldbz\\config.json'
config_loader = ConfigLoader(file_name)
# config_loader = ConfigLoader('./config.json')



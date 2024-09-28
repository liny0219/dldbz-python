import json
# import os


class ConfigLoader:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config_data = self._load_config()

    def _load_config(self):
        try:
            with open(self.config_file, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            raise Exception(f"加载配置文件{self.config_file}出错': {e}")

    def get(self, key_path, default=None):
        try:
            keys = key_path.split('.')
            value = self.config_data
            try:
                for key in keys:
                    value = value[key]
                return value
            except KeyError:
                raise Exception(f"配置文件:{self.config_file}, 获取配置项{key_path}出错")
        except Exception as e:
            raise Exception(f"配置文件:{self.config_file}, 获取配置项{key_path}出错")

    def reload(self):
        self.config_data = self._load_config()


def reload_config():
    cfg_startup.reload()
    cfg_monopoly.reload()


def update_json_config(file_path, key, value):
    """
    更新 JSON 配置文件中的指定键的值。

    :param file_path: 配置文件的路径
    :param key: 要更新的键名
    :param value: 要设置的新值
    """
    try:
        # 读取 JSON 文件
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # 检查键是否存在，并更新值
        if key in data:
            data[key] = value
        else:
            print(f"键 '{key}' 不存在，已创建新的键值对。")
            data[key] = value

        # 将更新后的数据写回文件
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        print(f"'{key}' 字段值已更新为: {value}")

    except FileNotFoundError:
        print(f"文件 {file_path} 未找到。")
    except json.JSONDecodeError:
        print(f"无法解析 {file_path} 中的 JSON。")
    except Exception as e:
        print(f"发生错误: {e}")


cfg_version = ConfigLoader('./config/version.json')
cfg_engine = ConfigLoader('./config/engine.json')
cfg_startup = ConfigLoader('./config/startup.json')
cfg_monopoly = ConfigLoader('./config/monopoly.json')
cfg_recollection = ConfigLoader('./config/recollection.json')
cfg_stationary = ConfigLoader('./config/stationary.json')

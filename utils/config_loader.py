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


def update_json_config(file_path, key_path, value):
    """
    更新 JSON 配置文件中的指定嵌套键的值。支持以点分隔的键路径。

    :param file_path: 配置文件的路径
    :param key_path: 以点分隔的键路径（例如 'a.b.c'）
    :param value: 要设置的新值
    """
    try:
        # 读取 JSON 文件
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # 解析以点分隔的键路径
        keys = key_path.split('.')

        # 遍历字典找到嵌套的键
        d = data
        for key in keys[:-1]:
            if key not in d:
                print(f"键 '{key}' 不存在，已创建新的嵌套结构。")
                d[key] = {}
            d = d[key]

        # 更新最后一级键的值
        final_key = keys[-1]
        d[final_key] = value

        # 将更新后的数据写回文件
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        print(f"'{key_path}' 字段值已更新为: {value}")

    except FileNotFoundError:
        print(f"文件 {file_path} 未找到。")
    except json.JSONDecodeError:
        print(f"无法解析 {file_path} 中的 JSON。")
    except Exception as e:
        print(f"发生错误: {e}")


cfg_version = ConfigLoader('./config/version.txt')
cfg_engine = ConfigLoader('./config/engine.txt')
cfg_startup = ConfigLoader('./config/startup.txt')
cfg_monopoly = ConfigLoader('./config/monopoly.txt')
cfg_recollection = ConfigLoader('./config/recollection.txt')
cfg_stationary = ConfigLoader('./config/stationary.txt')

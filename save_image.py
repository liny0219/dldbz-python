from engine.comparator import Comparator
from engine.device_controller import DeviceController
from utils.config_loader import cfg_startup

controller = DeviceController(cfg_startup.get('adb_port'))
comparator = Comparator(controller)
comparator._cropped_screenshot([45, 463], [82, 500], save_path="./refs/battle/in_battle_refs.png")

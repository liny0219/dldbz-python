from engine.comparator import Comparator
from engine.device_controller import DeviceController
from utils.config_loader import cfg_startup

controller = DeviceController(cfg_startup.get('adb_port'))
comparator = Comparator(controller)
comparator._cropped_screenshot([310, 265], [370, 300], save_path="./refs/battle/battle_end_refs.png")

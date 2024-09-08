from engine.comparator import Comparator
from engine.device_controller import DeviceController
from utils.config_loader import cfg_startup

controller = DeviceController(cfg_startup.get('adb_port'))
comparator = Comparator(controller)
comparator._cropped_screenshot([509, 333], [706, 352], save_path="./assets/monopoly/find_reputation.png")

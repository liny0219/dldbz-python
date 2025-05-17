from engine.u2_device import u2_device
from engine.comparator import comparator

u2_device.connect()
comparator.set_device(u2_device.device)

comparator._cropped_screenshot([426, 480], [462, 500], save_path="./assets/battle/quit_0.png")

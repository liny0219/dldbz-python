from engine.u2_device import u2_device
from engine.comparator import comparator

u2_device.connect()
comparator.set_device(u2_device.device)

comparator._cropped_screenshot([771, 457], [803, 473], save_path="./assets/battle/select_switch.png")

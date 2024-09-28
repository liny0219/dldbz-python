from engine.engine import engine
from engine.comparator import comparator

engine.connect()
comparator.set_device(engine.device)

comparator._cropped_screenshot([156, 167], [171, 180], save_path="./assets/monopoly/finish.png")

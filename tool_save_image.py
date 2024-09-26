from engine.engine import engine
from engine.comparator import comparator

engine.connect()
comparator.set_device(engine.device)

comparator._cropped_screenshot([558, 300], [601, 319], save_path="./assets/monopoly/reconnect.png")

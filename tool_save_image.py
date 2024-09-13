from engine.engine import engine
from engine.comparator import comparator

engine.connect()
comparator.set_device(engine.device)
# comparator._cropped_screenshot([152, 130], [186, 151], save_path="./assets/battle/attack.png")
comparator._cropped_screenshot([163, 139], [191, 147], save_path="./image/802/1.png")

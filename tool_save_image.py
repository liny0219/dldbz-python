from engine.engine import engine
from engine.comparator import comparator

engine.connect()
comparator.set_device(engine.device)
comparator._screenshot_cropped_image([648, 364], [767, 368], save_path="./assets/battle/sp_skill.png")
# comparator._cropped_screenshot([334, 250], [473, 266], save_path="./assets/monopoly/monopoly_continue.png")
# comparator._cropped_screenshot([163, 139], [191, 147], save_path="./image/802/1.png")

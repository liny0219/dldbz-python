from engine.engine import engine_vee
from engine.comparator import comparator_vee

comparator_vee.set_device(engine_vee.device)
comparator_vee._cropped_screenshot([708, 480], [750, 500], save_path="./assets/monopoly/treasure_crossing_10.png")

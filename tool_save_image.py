from engine.engine import engine_vee
from engine.comparator import comparator_vee

comparator_vee.set_device(engine_vee.device)
comparator_vee._cropped_screenshot([220, 290], [230, 330], save_path="./assets/monopoly/btn_options.png")
# comparator_vee._cropped_screenshot([563, 468], [591, 498], save_path="./assets/battle/btn_switch.png")
# comparator_vee._cropped_screenshot([563, 468], [591, 498], save_path="./assets/battle/btn_switch.png")

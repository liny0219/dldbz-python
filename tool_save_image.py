from engine.engine import engine
from engine.comparator import comparator

comparator.set_device(engine.device)
comparator._cropped_screenshot([718, 480], [736, 500], save_path="./assets/monopoly/test.png")

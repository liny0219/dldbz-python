import time
from app_data import app_data
from engine.engine import engine
from gameplay.monopoly.action import btn_center_confirm
from gameplay.monopoly.config import config


def roll_dice(bp=0, roll_time=None):
    start_point = (846, 440)
    x, y = start_point
    if bp > 0:
        offset = 58 * bp
        end_point = (x, y - offset)
        engine.long_press_and_drag(start_point, end_point)
        time.sleep(0.5)
        engine.device.click(x, y)
    if bp == 0:
        engine.device.click(x, y)
    msg = f"第{roll_time}次投骰子, BP: {bp}"
    app_data.update_ui(msg)
    for i in range(config.cfg_check_roll_dice_time):
        time.sleep(config.cfg_check_roll_dice_interval)
        btn_center_confirm()

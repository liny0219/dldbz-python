
from __future__ import annotations
import time
from typing import TYPE_CHECKING

from app_data import app_data
from gameplay.monopoly.config import config
from gameplay.monopoly.ocr import is_number, ocr_number

if TYPE_CHECKING:
    from gameplay.monopoly.index import Monopoly


def check_map_distance(monopoly: Monopoly):
    screenshot = monopoly.screenshot
    number = None
    if (screenshot is None):
        return 0
    try:
        x, y, width, height = 708, 480, 28, 20
        currentshot = screenshot
        if len(currentshot) == 0:
            currentshot = monopoly.shot()
        app_data.update_ui(f"check-检查距离")
        current_image = currentshot[y:y+height, x:x+width]
        number = ocr_number(current_image)
        if not is_number(number):
            app_data.update_ui(f"check-检查距离失败")
            time.sleep(config.cfg_check_roll_rule_wait)
            currentshot = monopoly.shot()
            current_image = currentshot[y:y+height, x:x+width]
            number = ocr_number(current_image)
        return number
    except Exception as e:
        app_data.update_ui(f"check-距离出现异常{e} {number}")
        return None

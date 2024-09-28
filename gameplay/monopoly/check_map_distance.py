
from __future__ import annotations
import os
import time
from typing import TYPE_CHECKING

from app_data import app_data
from gameplay.monopoly.ocr import cache_distance, is_number, match_distance_template_in_directory, ocr_number, write_ocr_log

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
        app_data.update_ui(f"check-检查距离", 'debug')
        current_image = currentshot[y:y+height, x:x+width]
        number = ocr_number(current_image, type="map_distance")
        if not is_number(number):
            app_data.update_ui(f"check-检查距离失败启动备用图片识别")
            if len(cache_distance.keys()) == 0:
                app_data.update_ui(f"check-没有备用图片")
                return number
            start_time = time.time()
            currentshot = monopoly.shot()
            current_image = currentshot[y:y+height, x:x+width]
            number = match_distance_template_in_directory(currentshot)
            write_ocr_log(number, current_image, 'map_distance_faild')
            app_data.update_ui(f"check-检查结束耗时:{time.time() - start_time}", 'debug')
            if is_number(number):
                app_data.update_ui(f"check-检查距离备用图片识别成功")
            else:
                app_data.update_ui(f"check-检查距离备用图片识别失败")
        return number
    except Exception as e:
        app_data.update_ui(f"check-距离出现异常{e} {number}")
        return None

from __future__ import annotations
import time
from typing import TYPE_CHECKING

from app_data import app_data
from gameplay.monopoly.ocr import cache_move, is_number, match_move_template_in_directory, ocr_number, write_ocr_log

if TYPE_CHECKING:
    from gameplay.monopoly.index import Monopoly


def check_move_distance(monopoly: Monopoly):
    number = None
    try:
        x, y, width, height = 863, 421, 30, 20
        currentshot = monopoly.screenshot
        if len(currentshot) == 0:
            currentshot = monopoly.shot()
        app_data.update_ui(f"check-剩余步数")
        current_image = currentshot[y:y+height, x:x+width]
        number = ocr_number(current_image, crop_type="center", type="move_distance")

        if not is_number(number):
            app_data.update_ui(f"check-检查剩余步数失败启动备用图片识别")
            if len(cache_move.keys()) == 0:
                app_data.update_ui(f"check-没有备用图片")
                return number
            start_time = time.time()
            currentshot = monopoly.shot()
            current_image = currentshot[y:y+height, x:x+width]
            number = match_move_template_in_directory(currentshot)
            write_ocr_log(number, current_image, 'move_distance_faild')
            app_data.update_ui(f"check-检查结束耗时:{time.time() - start_time}", 'debug')
            if is_number(number):
                app_data.update_ui(f"check-检查剩余步数备用图片识别成功")
            else:
                app_data.update_ui(f"check-检查剩余步数备用图片识别失败")
            del current_image
        return number
    except Exception as e:
        app_data.update_ui(f"check-剩余步数异常{e},{number}")
        return None

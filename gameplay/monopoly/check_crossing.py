from __future__ import annotations
import json
from app_data import app_data
from engine.comparator import comparator
from engine.engine import engine
from typing import TYPE_CHECKING
from gameplay.monopoly.check_move_distance import check_move_distance
from gameplay.monopoly.config import config
from gameplay.monopoly.ocr import is_number
if TYPE_CHECKING:
    from gameplay.monopoly.index import Monopoly


def check_crossing(monopoly: Monopoly):
    app_data.update_ui("check-大富翁路口", 'debug')
    if (app_data.thread_stoped()):
        return -1
    current_crossing = check_crossing_index(monopoly)
    if current_crossing != -1:
        monopoly.current_crossing = current_crossing
        update_crossing_msg(monopoly, f"当前在大富翁路口格子{current_crossing}")
        return current_crossing
    return -1


def check_crossing_index(monopoly: Monopoly):
    if (app_data.thread_stoped()):
        return None
    num = None
    strType = -1

    if config.cfg_type == "801":
        num = [46, 36, 30, 15]
        strType = "power"
    if config.cfg_type == "802":
        num = [45, 34, 10]
        strType = "wealth"
    if config.cfg_type == "803":
        num = [41, 20]
        strType = "fame"
    if not num or not strType:
        return -1
    for i in range(len(num)):
        if comparator.template_compare(f"./assets/monopoly/{strType}_crossing_{num[i]}.png", screenshot=monopoly.screenshot):
            return i
    return -1


def turn_auto_crossing(monopoly: Monopoly, crossing_index):
    if app_data.thread_stoped():
        return
    if not config.cfg_crossing or not config.cfg_crossing[crossing_index]:
        return
    rule = config.cfg_crossing[crossing_index]
    move_step = check_move_distance(monopoly)
    if not is_number(move_step):
        app_data.update_ui(f"未检测到移动步数,{move_step}")
    update_crossing_msg(monopoly, f"find-大富翁路口{crossing_index}, 移动步数{move_step}")
    default = rule["default"]
    if not is_number(move_step):
        if default:
            update_crossing_msg(monopoly, f"未检测到移动步数，使用默认方向{default}")
            turn_direction(monopoly, default)
        else:
            update_crossing_msg(monopoly, f"未检测到移动步数，无默认方向")
        return

    direction_result = None

    try:
        # 遍历 rule 的键
        for direction, range_str in rule.items():
            if direction == "default":
                continue
            rule_json = f"[{range_str}]"
            ranges = json.loads(rule_json)
            for start, end in ranges:
                if start <= move_step < end:
                    update_crossing_msg(monopoly,
                                        f"find-大富翁路口{crossing_index}规则, 方向{direction}--剩余步数规则 {start}<={move_step}<{end}")
                    # 匹配到方向，执行相应的动作
                    direction_result = direction
                    break
            if direction_result is not None:
                break
        if direction_result is None:
            direction_result = default
            update_crossing_msg(monopoly, f"匹配不到任何规则使用默认转向{default}")
            if default is None:
                update_crossing_msg(monopoly, f"没有设置默认转向,将会卡住,请设置配置")
    except Exception as e:
        app_data.update_ui(f"解析选择方向自定义规则异常{e}")
        return None
    turn_direction(monopoly, direction_result)


def turn_direction(monopoly: Monopoly, direction):
    if direction == "left":
        engine.device.click(402, 243)
        update_crossing_msg(monopoly, "选择左转")
    if direction == "right":
        engine.device.click(558, 243)
        update_crossing_msg(monopoly, "选择右转")
    if direction == "up":
        engine.device.click(480, 150)
        update_crossing_msg(monopoly, "选择上转")
    if direction == "down":
        engine.device.click(480, 330)
        update_crossing_msg(monopoly, "选择下转")


def update_crossing_msg(monopoly: Monopoly, msg):
    if monopoly.current_crossing == monopoly.pre_crossing:
        return
    app_data.update_ui(msg)

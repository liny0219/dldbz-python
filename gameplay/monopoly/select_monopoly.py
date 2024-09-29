from __future__ import annotations
from typing import TYPE_CHECKING

from app_data import app_data
from engine.u2_device import u2_device
from engine.comparator import comparator
from gameplay.monopoly.check_in_select_monopoly import check_in_select_monopoly
from gameplay.monopoly.config import config

if TYPE_CHECKING:
    from gameplay.monopoly.index import Monopoly


def select_monopoly(monopoly: Monopoly):
    x = 920
    start_y = 140
    end_y = 380
    current_y = start_y
    select = False
    while not select:
        monopoly.shot()
        select = find_monopoly(monopoly)
        if select:
            x, y = select
            if check_in_select_monopoly(monopoly):
                u2_device.device.click(x, y)
                app_data.update_ui(f"选择大富翁模式:{config.cfg_type}")
            break
        if (app_data.thread_stoped()):
            return
        if current_y >= end_y:
            break
        next_y = current_y + 25
        u2_device.device.swipe(x, current_y, x, next_y, 0.1)
        current_y = next_y


def find_monopoly(monopoly: Monopoly):
    if (app_data.thread_stoped()):
        return False
    if config.cfg_type == "801":
        return find_power(monopoly)
    if config.cfg_type == "802":
        return find_wealth(monopoly)
    if config.cfg_type == "803":
        return find_fame(monopoly)


crood_range = [(474, 116), (937, 397)]


def find_fame(monopoly: Monopoly):
    template_path = "./assets/monopoly/find_fame.png"
    return comparator.template_compare(template_path, crood_range, True, screenshot=monopoly.screenshot)


def find_wealth(monopoly: Monopoly):
    template_path = "./assets/monopoly/find_wealth.png"
    return comparator.template_compare(template_path, crood_range, True, screenshot=monopoly.screenshot)


def find_power(monopoly: Monopoly):
    template_path = "./assets/monopoly/find_power.png"
    return comparator.template_compare(template_path, crood_range, True, screenshot=monopoly.screenshot)

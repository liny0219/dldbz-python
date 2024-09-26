
from __future__ import annotations
from typing import TYPE_CHECKING

from app_data import app_data
from engine.comparator import comparator

if TYPE_CHECKING:
    from gameplay.monopoly.index import Monopoly


def check_map_can_roll_dice(monopoly: Monopoly):
    app_data.update_ui("check-是否可以掷骰子", 'debug')
    if (app_data.thread_stoped()):
        return False
    if comparator.template_compare("./assets/monopoly/roll_dice.png", [(780, 400), (900, 460)], screenshot=monopoly.screenshot):
        app_data.update_ui("find-可以掷骰子", 'debug')
        return True
    else:
        return False

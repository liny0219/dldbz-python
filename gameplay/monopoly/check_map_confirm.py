from __future__ import annotations
from typing import TYPE_CHECKING

from app_data import app_data
from engine.u2_device import u2_device
from engine.comparator import comparator

if TYPE_CHECKING:
    from gameplay.monopoly.index import Monopoly


def check_map_confirm(monopoly: Monopoly):
    app_data.update_ui("check-奖励确认界面", 'debug')
    coord = comparator.template_compare(f"./assets/monopoly/btn_confirm_award.png",
                                        return_center_coord=True, screenshot=monopoly.screenshot)
    if coord:
        app_data.update_ui("find-奖励确认界面", 'debug')
        u2_device.device.click(coord[0], coord[1])
        return True
    return False

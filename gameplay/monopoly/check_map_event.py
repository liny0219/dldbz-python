from __future__ import annotations
from typing import TYPE_CHECKING

from app_data import app_data
from engine.u2_device import u2_device
from engine.comparator import comparator

if TYPE_CHECKING:
    from gameplay.monopoly.index import Monopoly


def check_map_event(monopoly: Monopoly):
    app_data.update_ui("check-事件", 'debug')
    coord = comparator.template_compare(f"./assets/monopoly/btn_options.png",
                                        return_center_coord=True, screenshot=monopoly.screenshot)
    if coord:
        app_data.update_ui("find-事件", 'debug')
        x, y = coord
        offfset = 120
        u2_device.device.click(x + offfset, y)
        return True
    return False

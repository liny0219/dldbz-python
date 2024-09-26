from __future__ import annotations
from typing import TYPE_CHECKING

from app_data import app_data
from engine.engine import engine
from engine.comparator import comparator

if TYPE_CHECKING:
    from gameplay.monopoly.index import Monopoly


def check_map_final_confirm(monopoly: Monopoly):
    app_data.update_ui("check-最终确认界面", 'debug')
    points_with_colors = [(533, 102, [168, 167, 165]), (533, 111, [168, 167, 165]),
                          (533, 121, [180, 179, 177]), (487, 106, [243, 242, 238]),
                          (487, 115, [236, 235, 233]), (441, 112, [236, 235, 233]),
                          (432, 119, [211, 210, 208])]
    if comparator.match_point_color(points_with_colors, screenshot=monopoly.screenshot):
        app_data.update_ui("find-最终确认界面", 'debug')
        return True
    return False


def btn_final_confirm():
    engine.device.click(480, 410)

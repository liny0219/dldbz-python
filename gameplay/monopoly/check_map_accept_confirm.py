from __future__ import annotations
from typing import TYPE_CHECKING

from app_data import app_data
from engine.u2_device import u2_device
from engine.comparator import comparator

if TYPE_CHECKING:
    from gameplay.monopoly.index import Monopoly


def check_accept_confirm(monopoly: Monopoly):
    app_data.update_ui("check-奖励入账确认界面", 'debug')
    points_with_colors = [(688, 55, [253, 251, 252]), (528, 59, [244, 243, 241]),
                          (533, 74, [233, 229, 226]), (513, 80, [198, 194, 191])]
    if comparator.match_point_color(points_with_colors, screenshot=monopoly.screenshot):
        app_data.update_ui("find-奖励入账确认界面", 'debug')
        btn_accept_confirm()
        return True
    return False


def btn_accept_confirm():
    u2_device.device.click(484, 470)

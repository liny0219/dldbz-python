from __future__ import annotations
from typing import TYPE_CHECKING

from app_data import app_data
from engine.comparator import comparator
from gameplay.monopoly.action import btn_center_confirm

if TYPE_CHECKING:
    from gameplay.monopoly.index import Monopoly


def check_map_info_confirm(monopoly: Monopoly):
    app_data.update_ui("check-信息确认界面", 'debug')
    flod = [(68, 483, [98, 97, 95]), (61, 472, [170, 165, 161]),
            (61, 493, [171, 170, 168]), (51, 482, [172, 171, 166])]
    unflod = [(72, 483, [183, 180, 175]), (57, 483, [149, 146, 141]),
              (57, 483, [149, 146, 141]), (63, 493, [126, 128, 125])]
    check_list = [flod, unflod]
    for check in check_list:
        if comparator.match_point_color(check, screenshot=monopoly.screenshot):
            monopoly.update_ui("find-信息确认界面", 'debug')
            btn_center_confirm()
            return True
    return False


from __future__ import annotations
from typing import TYPE_CHECKING

from app_data import app_data
from engine.comparator import comparator

if TYPE_CHECKING:
    from gameplay.monopoly.index import Monopoly


def check_map_end(monopoly: Monopoly):
    app_data.update_ui("check-是否结束", 'debug')
    points_with_colors = [
        (486, 111, [233, 232, 228]),
        (486, 111, [233, 232, 228]),
        (486, 111, [233, 232, 228]),
        (486, 111, [233, 232, 228]),
        (159, 174, [102, 96, 82]),
        (164, 175, [53, 43, 31]),
        (442, 113, [236, 235, 233])]
    if comparator.match_point_color(points_with_colors, screenshot=monopoly.screenshot):
        app_data.update_ui("find-结算")
        return True
    return False

from __future__ import annotations
from typing import TYPE_CHECKING
from engine.engine import engine_vee
from engine.comparator import comparator_vee
from utils.singleton import singleton

if TYPE_CHECKING:
    from app_data import AppData


@singleton
class WorldVee:
    def __init__(self):
        self.global_data = None
        self.debug = False

    def set(self, global_data: AppData):
        self.global_data = global_data

    def thread_stoped(self) -> bool:
        return self.global_data and self.global_data.thread_stoped()

    def update_ui(self, msg: str, type=0):
        self.global_data and self.global_data.update_ui(msg, type)

    def in_world(self):
        """检查是否在游戏世界中，通过左下角菜单的颜色来判断"""
        if (self.thread_stoped()):
            return False
        self.update_ui("开始检查是否在世界中", 3)
        ponits_with_colors = [
            (55, 432, [243, 243, 243]),
            (57, 431, [242, 243, 247]),
            (87, 464, [80, 80, 78]),
            (68, 487, [164, 150, 149])
        ]
        if comparator_vee.match_point_color(ponits_with_colors):
            self.update_ui("检测到在世界中", 3)
            return True
        else:
            return False

    def click_btn_close(self):
        if (self.thread_stoped()):
            return
        engine_vee.device.click(925, 16)
        self.update_ui("点击关闭按钮", 3)

    def check_stage(self):
        if (self.thread_stoped()):
            return
        self.update_ui("开始检查是否在小剧场中", 3)
        points_with_colors = [
            (696, 330, [146, 123, 79]),
            (634, 350, [156, 133, 83]),
            (331, 351, [155, 132, 82]),
            (278, 340, [141, 119, 70]),
        ]
        if comparator_vee.match_point_color(points_with_colors, 20):
            self.update_ui("检测到在小剧场中", 3)
            return True
        else:
            return False

    def back_world(self):
        if (self.thread_stoped()):
            return
        engine_vee.device.click(55, 432)
        self.update_ui("返回世界")


world_vee = WorldVee()

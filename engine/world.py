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

    def set(self, global_data: AppData):
        self.global_data = global_data

    def thread_stoped(self) -> bool:
        return self.global_data and self.global_data.thread_stoped()

    def update_ui(self, msg: str):
        self.global_data and self.global_data.update_ui(msg)

    def in_world(self):
        """检查是否在游戏世界中，通过左下角菜单的颜色来判断"""
        if (self.thread_stoped()):
            return False
        ponits_with_colors = [
            (55, 432, [243, 243, 243]),
            (101, 488, [6, 6, 6]),
            (68, 487, [164, 150, 149])
        ]
        if comparator_vee.match_point_color(ponits_with_colors):
            self.log("检测到在世界中")
            return True
        else:
            self.log("检测到不在世界中")
            return False

    def click_btn_close(self):
        if (self.thread_stoped()):
            return
        engine_vee.device.click(925, 16)
        self.log("点击关闭按钮")

    def back_world(self):
        if (self.thread_stoped()):
            return
        engine_vee.device.click(55, 432)
        self.log("返回世界")

    def log(self, msg):
        print(msg)
        self.update_ui(msg)


world_vee = WorldVee()

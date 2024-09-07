from __future__ import annotations
from typing import TYPE_CHECKING
from engine_vee.engine import engine_vee
from utils.singleton import singleton

if TYPE_CHECKING:
    from global_data import GlobalData


@singleton
class WorldVee:
    def __init__(self):
        self.global_data = None

    def set(self, global_data: GlobalData):
        self.global_data = global_data

    def thread_stoped(self) -> bool:
        return self.global_data and self.global_data.thread_stoped()

    def update_ui(self, msg: str):
        self.global_data and self.global_data.update_ui(msg)

    def in_world(self):
        """检查是否在游戏世界中，通过左下角菜单的颜色来判断"""
        if (self.thread_stoped()):
            return False
        if engine_vee.match_point_color(55, 432, [243, 243, 243]) and engine_vee.match_point_color(101, 488, [6, 6, 6]) and engine_vee.match_point_color(68, 487, [164, 150, 149]):
            self.log("检测到在世界中")
            return True
        else:
            self.log("检测到不在世界中")
            return False

    def log(self, msg):
        print(msg)
        self.update_ui(msg)


world_vee = WorldVee()

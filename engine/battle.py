from __future__ import annotations
from typing import TYPE_CHECKING
from engine.engine import engine_vee
from engine.comparator import comparator_vee
from utils.singleton import singleton
import time

if TYPE_CHECKING:
    from app_data import AppData


@singleton
class BattleVee:
    def __init__(self):
        self.global_data = None
        self.debug = False

    def set(self, global_data: AppData):
        self.global_data = global_data

    def thread_stoped(self) -> bool:
        return self.global_data and self.global_data.thread_stoped()

    def update_ui(self, msg: str, type=0):
        self.global_data and self.global_data.update_ui(msg, type)

    def btn_auto_battle(self):
        engine_vee.device.click(368, 482)
        time.sleep(0.4)
        engine_vee.device.click(825, 482)

    def btn_quit_battle(self):
        engine_vee.device.click(440, 482)

    def btn_attack(self):
        engine_vee.device.click(816, 487)

    def btn_all_switch(self):
        engine_vee.device.click(577, 482)

    def btn_all_bp(self):
        engine_vee.device.click(648, 482)

    def cmd_skip(self, duration=2):
        engine_vee.device.long_click(480, 254, duration)

    def is_in_battle(self):
        self.update_ui("开始检查是否在战斗界面中", 3)
        isR1 = [(788, 71, [145, 144, 142]), (791, 49, [243, 240, 233]), (784, 58, [0, 1, 0])]
        isR2 = [(787, 178, [223, 228, 224]), (791, 157, [245, 244, 242]), (784, 168, [1, 0, 0])]
        isR3 = [(786, 285, [226, 222, 219]), (790, 264, [237, 231, 231]), (784, 273, [0, 2, 1])]
        isR4 = [(787, 393, [224, 220, 211]), (789, 373, [235, 236, 231]), (785, 382, [7, 0, 10])]
        isSP = [(461, 195, [99, 99, 99]), (880, 194, [0, 0, 0]), (309, 197, [101, 101, 101]),
                (517, 195, [99, 99, 99]), (655, 195, [97, 96, 101])]
        Role = [isR1, isR2, isR3, isR4, isSP]
        for i in Role:
            if self.thread_stoped():
                return False
            if comparator_vee.match_point_color(i):
                self.update_ui("检测到在战斗界面中", 3)
                return True
        return False

    def is_in_battle_ready(self):
        self.update_ui("开始检查是否在战斗准备界面中", 3)
        result = comparator_vee.template_in_picture("./assets/battle/btn_bp.png", [(632, 469), (663, 498)], True)
        if result:
            self.update_ui("检测到在战斗准备界面中", 3)
        return result


battle_vee = BattleVee()

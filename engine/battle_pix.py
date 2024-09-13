from __future__ import annotations
from typing import TYPE_CHECKING
from engine.engine import engine
from engine.comparator import comparator
from utils.singleton import singleton
import time

if TYPE_CHECKING:
    from app_data import AppData


@singleton
class BattleVee:
    def __init__(self):
        self.app_data = None
        self.debug = False

    def set(self, app_data: AppData):
        self.app_data = app_data

    def thread_stoped(self) -> bool:
        return self.app_data and self.app_data.thread_stoped()

    def update_ui(self, msg: str, type='info'):
        self.app_data and self.app_data.update_ui(msg, type)

    def btn_auto_battle(self):
        engine.device.click(368, 482)

    def btn_auto_battle_start(self):
        engine.device.click(825, 482)

    def btn_quit_battle(self):
        engine.device.click(440, 482)

    def btn_attack(self):
        engine.device.click(816, 487)

    def btn_all_switch(self):
        engine.device.click(577, 482)

    def btn_all_bp(self):
        engine.device.click(648, 482)

    def cmd_skip(self, duration=2):
        engine.device.long_click(480, 254, duration)

    def is_in_battle(self, screenshot=None):
        self.update_ui("开始检查是否在战斗界面中", 'debug')
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
            if comparator.match_point_color(i, screenshot=screenshot):
                self.update_ui("检测到在战斗界面中", 'debug')
                return True
        return False

    def is_in_round(self):
        self.update_ui("开始检查是否在战斗准备界面中", 'debug')
        result = comparator.template_in_picture("./assets/battle/attack.png", [[784, 470], [857, 498]], True)
        if result:
            self.update_ui("检测到在战斗准备界面中", 'debug')
        return result

    def is_auto_battle_stay(self, screenshot=None):
        self.update_ui("开始检查是否在自动战斗停留界面中", 'debug')
        ck = [(882, 481, [196, 229, 218]), (857, 479, [237, 255, 239]), (857, 487, [237, 255, 240]),
              (838, 484, [244, 255, 243]), (838, 484, [244, 255, 243]), (820, 487, [242, 255, 243]),
              (792, 480, [200, 229, 201]),  (791, 486, [238, 255, 255]), (777, 481, [251, 255, 251]),
              (828, 505, [205, 235, 235])]
        cks = [ck]
        for i in cks:
            if self.thread_stoped():
                return False
            if comparator.match_point_color(i, screenshot=screenshot):
                self.update_ui("检测到在自动战斗停留界面中", 'debug')
                return True
        return False


battle_pix = BattleVee()

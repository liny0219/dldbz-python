from __future__ import annotations
from typing import TYPE_CHECKING
from engine.engine import engine
from engine.comparator import comparator
from utils.singleton import singleton

if TYPE_CHECKING:
    from app_data import AppData


@singleton
class BattleVee:
    def __init__(self):
        self.app_data = None
        self.debug = False
        self.cfg_battle_ui = './assets/battle/battle_ui.png'
        self.cfg_attack = './assets/battle/attack.png'
        self.cfg_auto_battle_stay = './assets/battle/auto_battle_stay.png'

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

    def btn_auto_battle_stop(self):
        engine.device.click(480, 472)

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
        self.update_ui("check-战斗界面中", 'debug')
        isR1 = [(788, 71, [145, 144, 142]), (791, 49, [243, 240, 233]), (784, 58, [0, 1, 0])]
        isR2 = [(787, 178, [223, 228, 224]), (791, 157, [245, 244, 242]), (784, 168, [1, 0, 0])]
        isR3 = [(786, 285, [226, 222, 219]), (790, 264, [237, 231, 231]), (784, 273, [0, 2, 1])]
        isR4 = [(787, 393, [224, 220, 211]), (789, 373, [235, 236, 231]), (785, 382, [7, 0, 10])]
        isSP = [(461, 195, [99, 99, 99]), (880, 194, [0, 0, 0]), (309, 197, [101, 101, 101]),
                (517, 195, [99, 99, 99]), (655, 195, [97, 96, 101])]
        Role = [isR1, isR2, isR3, isR4, isSP]
        result = False
        for i in Role:
            if self.thread_stoped():
                return False
            if comparator.match_point_color(i, screenshot=screenshot):
                result = True
        if not result and self.is_battle_ui(screenshot):
            result = True
        if not result and self.is_sp_skill(screenshot):
            result = True
        if result:
            self.update_ui("find-在战斗界面中", 'debug')
        return result

    def is_battle_ui(self, screenshot=None):
        return comparator.template_compare(self.cfg_battle_ui, match_threshold=0.7, screenshot=screenshot)

    def is_sp_skill(self, screenshot=None):
        self.update_ui("check-战斗待确认必杀界面中", 'debug')
        ck1 = [(786, 345, [210, 207, 198]),
               (779, 347, [213, 202, 184]),
               (637, 345, [242, 236, 210]),
               (630, 346, [213, 221, 200]),
               (627, 346, [188, 176, 160]),
               (699, 324, [176, 180, 129]),]
        cks = [ck1]
        for i in cks:
            if self.thread_stoped():
                return False
            if comparator.match_point_color(i, screenshot=screenshot):
                self.update_ui("find-在战斗待确认必杀界面中", 'debug')
                return True
        return False

    def is_in_round(self, screenshot=None):
        self.update_ui("check-战斗准备界面中", 'debug')
        result = comparator.template_compare(
            self.cfg_attack, [(702, 448), (944, 516)],  screenshot=screenshot)
        if result:
            self.update_ui("find-在战斗准备界面中", 'debug')
        return result

    def is_auto_battle_stay(self, screenshot=None):
        self.update_ui("check-自动战斗停留界面中", 'debug')
        result = comparator.template_compare(
            self.cfg_auto_battle_stay, [(705, 450), (946, 520)],  screenshot=screenshot)
        if result:
            self.update_ui("find-在自动战斗停留界面中", 'debug')
            return True
        return False

    def is_cat(self, screenshot=None):
        if self.is_cat50(screenshot):
            return True
        if self.is_cat55(screenshot):
            return True
        if self.is_cat70(screenshot):
            return True
        return False

    def is_cat55(self, screenshot=None):
        self.update_ui("check-猫55界面中", 'debug')
        result = comparator.template_compare(
            './assets/cat/55.png',  screenshot=screenshot)
        if result:
            self.update_ui("find-猫55界面中", 'debug')
            return True
        return False

    def is_cat50(self, screenshot=None):
        self.update_ui("check-猫50界面中", 'debug')
        result = comparator.template_compare(
            './assets/cat/50.png',  screenshot=screenshot)
        if result:
            self.update_ui("find-猫50界面中", 'debug')
            return True
        return False

    def is_cat70(self, screenshot=None):
        self.update_ui("check-猫70界面中", 'debug')
        result = comparator.template_compare(
            './assets/cat/70.png',  screenshot=screenshot)
        if result:
            self.update_ui("find-猫70界面中", 'debug')
            return True
        return False


battle_pix = BattleVee()

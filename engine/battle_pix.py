
import gc
import time
import app_data
from engine.world import world
from engine.battle_hook import BattleHook
from engine.u2_device import u2_device
from engine.comparator import comparator
from utils.singleton import singleton
from app_data import app_data


@singleton
class BattleVee:
    def __init__(self):
        self.debug = False
        self.screenshot = None
        self.hook_manager = BattleHook()
        self.instructions = []  # 用于存储预读取的指令列表

    def btn_auto_battle(self):
        u2_device.device.click(368, 482)

    def btn_auto_battle_start(self):
        u2_device.device.click(825, 482)

    def btn_auto_battle_stop(self):
        u2_device.device.click(602, 450)

    def btn_quit_battle(self):
        u2_device.device.click(440, 482)

    def btn_confirm_quit_battle(self):
        u2_device.device.click(600, 363)

    def btn_attack(self):
        u2_device.device.click(816, 487)

    def btn_all_switch(self):
        u2_device.device.click(577, 482)

    def btn_all_bp(self):
        u2_device.device.click(648, 482)

    def cmd_skip(self, duration=2):
        u2_device.device.long_click(480, 254, duration)

    def check_quit_battle(self, screenshot=None):
        app_data.update_ui("check-是否退出战斗", 'debug')
        result = comparator.template_compare('./assets/battle/quit_0.png', [(
            177, 462), (676, 509)], screenshot=screenshot, return_center_coord=True)
        if result:
            app_data.update_ui("find-退出战斗", 'debug')
        return result

    def check_confirm_quit_battle(self, screenshot=None):
        app_data.update_ui("check-是否确认退出战斗", 'debug')
        result = comparator.template_compare('./assets/battle/quit_confirm.png', [(
            510, 329), (692, 395)], screenshot=screenshot, return_center_coord=True)
        if result:
            app_data.update_ui("find-确认退出战斗", 'debug')
        return result

    def is_in_battle(self, screenshot=None):
        app_data.update_ui("check-战斗界面中", 'debug')
        isR1 = [(788, 71, [145, 144, 142]), (791, 49, [243, 240, 233]), (784, 58, [0, 1, 0])]
        isR2 = [(787, 178, [223, 228, 224]), (791, 157, [245, 244, 242]), (784, 168, [1, 0, 0])]
        isR3 = [(786, 285, [226, 222, 219]), (790, 264, [237, 231, 231]), (784, 273, [0, 2, 1])]
        isR4 = [(787, 393, [224, 220, 211]), (789, 373, [235, 236, 231]), (785, 382, [7, 0, 10])]
        isSP = [(461, 195, [99, 99, 99]), (880, 194, [0, 0, 0]), (309, 197, [101, 101, 101]),
                (517, 195, [99, 99, 99]), (655, 195, [97, 96, 101])]
        Role = [isR1, isR2, isR3, isR4, isSP]
        result = False
        for i in Role:
            if app_data.thread_stoped():
                return False
            if comparator.match_point_color(i, screenshot=screenshot):
                result = True
        if not result and self.is_battle_ui(screenshot):
            result = True
        if not result and self.is_sp_skill(screenshot):
            result = True
        if result:
            app_data.update_ui("find-在战斗界面中", 'debug')
        return result

    def is_battle_ui(self, screenshot=None):
        return comparator.template_compare('./assets/battle/battle_ui.png', match_threshold=0.7, screenshot=screenshot)

    def is_sp_skill(self, screenshot=None):
        app_data.update_ui("check-战斗待确认必杀界面中", 'debug')
        ck1 = [(786, 345, [210, 207, 198]),
               (779, 347, [213, 202, 184]),
               (637, 345, [242, 236, 210]),
               (630, 346, [213, 221, 200]),
               (627, 346, [188, 176, 160]),
               (699, 324, [176, 180, 129]),]
        cks = [ck1]
        for i in cks:
            if app_data.thread_stoped():
                return False
            if comparator.match_point_color(i, screenshot=screenshot):
                app_data.update_ui("find-在战斗待确认必杀界面中", 'debug')
                return True
        return False

    def is_in_round(self, screenshot=None):
        app_data.update_ui("check-战斗准备界面中", 'debug')
        ck1 = [(844, 476, [228, 255, 255]),
               (836, 474, [237, 255, 255]),
               (829, 476, [240, 255, 255]),
               (836, 484, [255, 255, 241]),
               (846, 497, [255, 253, 255]),
               (836, 498, [234, 255, 255]),
               (826, 496, [243, 255, 255]),
               (813, 478, [249, 255, 255]),
               (803, 480, [232, 255, 255]),
               (807, 491, [255, 248, 255]),
               (793, 476, [255, 249, 255]),
               (794, 491, [255, 253, 255]),]
        cks = [ck1]
        for i in cks:
            if app_data.thread_stoped():
                return False
            if comparator.match_point_color(i, screenshot=screenshot):
                app_data.update_ui("find-在战斗准备界面中", 'debug')
                return True
        return False

    def is_auto_battle_stay(self, screenshot=None):
        app_data.update_ui("check-自动战斗停留界面中", 'debug')
        ck1 = [(876, 476, [247, 255, 243]),
               (877, 482, [154, 209, 178]),
               (880, 490, [182, 233, 200]),
               (867, 479, [223, 255, 234]),
               (856, 483, [241, 255, 248]),
               (850, 485, [237, 255, 250]),
               (837, 483, [245, 255, 239]),
               (817, 483, [243, 255, 246]),
               (810, 482, [247, 255, 243]),
               (798, 482, [157, 193, 157]),
               (790, 483, [226, 248, 225]),
               (775, 481, [248, 255, 245]),
               (828, 507, [211, 244, 249])]
        cks = [ck1]
        for i in cks:
            if app_data.thread_stoped():
                return False
            if comparator.match_point_color(i, screenshot=screenshot):
                app_data.update_ui("find-在自动战斗停留界面中", 'debug')
                return True
        return False

    def is_cat(self, screenshot=None):
        if self.is_cat50(screenshot):
            app_data.update_ui("find-猫50界面中", 'debug')
            return 50
        if self.is_cat55(screenshot):
            app_data.update_ui("find-猫55界面中", 'debug')
            return 55
        if self.is_cat70(screenshot):
            app_data.update_ui("find-猫70界面中", 'debug')
            return 70
        return 0

    def is_cat55(self, screenshot=None):
        app_data.update_ui("check-猫55界面中", 'debug')
        result = comparator.template_compare(
            './assets/cat/55.png',  screenshot=screenshot)
        if result:
            app_data.update_ui("find-猫55界面中", 'debug')
            return True
        return False

    def is_cat50(self, screenshot=None):
        app_data.update_ui("check-猫50界面中", 'debug')
        result = comparator.template_compare(
            './assets/cat/50.png',  screenshot=screenshot)
        if result:
            app_data.update_ui("find-猫50界面中", 'debug')
            return True
        return False

    def is_cat70(self, screenshot=None):
        app_data.update_ui("check-猫70界面中", 'debug')
        result = comparator.template_compare(
            './assets/cat/70.png',  screenshot=screenshot, gray=False)
        if result:
            app_data.update_ui("find-猫70界面中", 'debug')
            return True
        return False

    def run(self, path):
        self._load_instructions(path)
        self._run_script()

    def _load_instructions(self, filename):
        """ 从文件中预读取指令并存储 """
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                self.instructions = [line.strip() for line in file if line.strip() and not line.startswith('#')]
            if app_data.update_ui:
                app_data.update_ui("指令加载成功。")
        except Exception as e:
            if app_data.update_ui:
                app_data.update_ui(f"读取指令出错 {filename}. {e}")

    def _execute_instruction(self, instruction):
        hook_func_cmd_start = self.hook_manager.get('CmdStart')  # 获取对应指令的 hook 函数
        if hook_func_cmd_start is not None and not hook_func_cmd_start():
            return False

        """ 解析并执行指令 """
        parts = instruction.split(',')
        command = parts[0]  # 获取指令名称
        hook_func = self.hook_manager.get(command)

        if hook_func is not None:
            # 执行对应的 hook 函数，并传递参数
            hook_func(*parts[1:])
        else:
            # 更新 UI
            if app_data.update_ui:
                app_data.update_ui(f"找不到对应战斗指令 '{command}'.")
        return True

    def _run_script(self):
        """ 执行预加载的指令 """
        for instruction in self.instructions:
            is_continue = self._execute_instruction(instruction)
            if not is_continue:
                break
        # 文件读取完毕，执行 Finish Hook
        finish_hook = self.hook_manager.get('Finish')
        if finish_hook:
            finish_hook()

    def shot(self):
        try:
            app_data.update_ui("-----------开始截图", 'debug')
            if self.screenshot is not None:
                del self.screenshot
                self.screenshot = None
                gc.collect()
            self.screenshot = u2_device.device.screenshot(format='opencv')
            app_data.update_ui("-----------截图完成", 'debug')
            return self.screenshot
        except Exception as e:
            app_data.update_ui(f"截图异常{e}")
            return None


battle = BattleVee()

from engine.battle_DSL import BattleDSL
from engine.battle_hook import BattleHook
from engine.device_controller import DeviceController
from engine.battle_vee import Battle
from engine.comparator import Comparator
from utils.config_loader import cfg_recollection
from engine.player import Player
from utils.wait import wait_limit
from functools import partial
import cv2


class recollection:
    def __init__(self, thread, device_ip="127.0.0.1:5555", team='TBD'):
        self.thread = thread
        self.loopNum = 0
        self.loop = int(cfg_recollection.get("common.loop"))
        self.controller = DeviceController(device_ip)
        self.comparator = Comparator(self.controller)
        self.player = Player(self.controller, self.comparator, team)
        self.battle_dsl = BattleDSL()
        self.battle_hook = BattleHook()

    def on_read(self):
        ui_read = cfg_recollection.get("check.check_read_ui_refs")
        # btn_read = cfg_recollection.get("coord.btn_read")
        in_read = self.comparator.template_in_picture(
            ui_read, return_center_coord=True)
        if in_read:
            self.controller.press(in_read)
            return True

    def on_confirm_read(self):
        ui_confirm_read = cfg_recollection.get(
            "check.check_confirm_read_ui_refs")
        # btn_confirm_read = cfg_recollection.get("coord.btn_confirm_read")
        in_confirm_read = self.comparator.template_in_picture(
            ui_confirm_read, return_center_coord=True)
        if in_confirm_read:
            self.controller.press(in_confirm_read)
            return True

    def on_confirm_award(self):
        ui_confirm_award = cfg_recollection.get(
            "check.check_confirm_award_ui_refs")
        in_confirm_award = self.comparator.template_in_picture(
            ui_confirm_award, return_center_coord=True)
        if in_confirm_award:
            self.controller.press(in_confirm_award)
            return True

    def on_status_close(self):
        ui_status_close = cfg_recollection.get(
            "check.check_status_close_ui_refs")
        in_status_close = self.comparator.template_in_picture(
            ui_status_close, return_center_coord=True)
        if in_status_close:
            self.controller.press(in_status_close)
            return True

    def start(self):
        self.loop = int(cfg_recollection.get("common.loop"))
        # 等待读取并确认读取
        runState = wait_limit(self.on_read,  operate_funcs=[self.on_read], thread=self.thread,
                              timeout=10, check_interval=1)
        if not runState:
            return
        runState = wait_limit(self.on_confirm_read, operate_funcs=[self.on_confirm_read],  thread=self.thread,
                              timeout=10, check_interval=1)
        btnSkipTimeout = cfg_recollection.get("common.btn_skip_timeout")
        btnSkip = cfg_recollection.get("coord.btn_skip")
        self.controller.press(btnSkip, btnSkipTimeout)

        if not runState:
            return

        with Battle(self.player, '测试') as b:
            b.SetThread(self.thread)
            b.setFinishHook(self.finish)
            self.battle_dsl.run_script('./battle_script/recollection.txt')

    def finish(self):
        self.loopNum += 1
        runState = wait_limit(self.on_confirm_award,  operate_funcs=[self.on_confirm_award], thread=self.thread,
                              timeout=10, check_interval=1)
        if not runState:
            return
        runState = wait_limit(self.on_status_close,  operate_funcs=[self.on_status_close], thread=self.thread,
                                  timeout=10, check_interval=1)
        if not runState:
            return
        if self.loop != 0 and self.loopNum >= self.loop:
            return
        self.start()

    def shot(self):
        self.comparator._cropped_screenshot(
            [462, 290], [498, 312], convert_gray=False, save_path='./refs/recollection/status_close_ui.png')

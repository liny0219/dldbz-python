from engine.battle_DSL import BattleDSL
from engine.battle_hook import BattleHook
from engine.device_controller import DeviceController
from engine.battle_vee import Battle
from engine.comparator import Comparator
from utils.config_loader import cfg_jjc
from engine.player import Player
from utils.wait import wait_limit
from functools import partial
import cv2


class JJC:
    def __init__(self, thread, device_ip="127.0.0.1:5555", team='TBD'):
        self.thread = thread
        self.controller = DeviceController(device_ip)
        self.comparator = Comparator(self.controller)
        self.player = Player(self.controller, self.comparator, team)
        self.battle_dsl = BattleDSL()
        self.battle_hook = BattleHook()

    def read(self):
        ui_read = cfg_jjc.get("check.check_read_ui_refs")
        btn_read = cfg_jjc.get("coord.btn_read")
        in_read = self.comparator.template_in_picture(ui_read)
        if in_read:
            self.controller.press(btn_read)
            return True

    def confirm_read(self):
        ui_confirm_read = cfg_jjc.get("check.check_confirm_read_ui_refs")
        btn_confirm_read = cfg_jjc.get("coord.btn_confirm_read")
        in_confirm_read = self.comparator.template_in_picture(ui_confirm_read)
        if in_confirm_read:
            self.controller.press(btn_confirm_read)
            return True

    def start(self):
        # 等待读取并确认读取
        # runState = wait_limit(self.read,  operate_funcs=[self.read], thread=self.thread,
        #                       timeout=10, check_interval=1)
        # if not runState:
        #     return
        # runState = wait_limit(self.confirm_read, operate_funcs=[self.confirm_read],  thread=self.thread,
        #                       timeout=10, check_interval=1)
        # btnSkipTimeout = cfg_jjc.get("common.btn_skip_timeout")
        # btnSkip = cfg_jjc.get("coord.btn_skip")
        # self.controller.press(btnSkip, btnSkipTimeout)

        # if not runState:
        #     return

        with Battle(self.player, '测试') as b:
            b.SetThread(self.thread)
            self.battle_dsl.run_script('./battle_script/jjc.txt')

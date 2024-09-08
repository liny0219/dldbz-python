
from __future__ import annotations
from typing import TYPE_CHECKING
from engine.comparator import comparator_vee
from utils.singleton import singleton
import uiautomator2 as u2
from utils.config_loader import cfg_startup_vee
import time

if TYPE_CHECKING:
    from app_data import AppData

appName = "com.netease.ma167"
appNameBilibili = "com.netease.ma167.bilibili"
game_activity = "com.epicgames.ue4.GameActivity"


@singleton
class EngineVee:
    def __init__(self):
        self.device = None
        self.package_name = None
        self.global_data = None
        self.debug = False
        self.connect()

    def set(self, global_data: AppData):
        self.global_data = global_data

    def thread_stoped(self) -> bool:
        return self.global_data and self.global_data.thread_stoped()

    def update_ui(self, msg: str, type=0):
        self.global_data and self.global_data.update_ui(msg, type)

    def connect(self):
        addr = cfg_startup_vee.get('adb_port')
        self.device = u2.connect(addr)
        comparator_vee.set_device(self.device)
        # // 连接设备
        self.log("连接设备")

    def check_in_app(self):
        current_app = self.device.app_current()
        self.package_name = current_app['package']
        self.log(f"当前应用包名: {self.package_name}")
        return self.package_name == appName or self.package_name == appNameBilibili

    def start_app(self):
        # 启动应用程序，需要确保已安装并可通过此包名启动
        self.device.app_start("com.netease.ma167")
        self.device.app_start("com.netease.ma167.bilibili")

    def check_in_game(self):
        activity = self.device.app_current().get('activity')
        if activity == game_activity:
            return True
        else:
            return False

    def restart_game(self):
        self.log("重启游戏")
        self.device.app_stop(self.package_name)
        time.sleep(1)
        self.device.app_start(self.package_name)
        self.log(f"{self.package_name} 重启成功")

    def long_press_and_drag(self, start, end, duration=0.5):
        start_x, start_y = start
        end_x, end_y = end
        self.device.long_click(start_x, start_y, duration / 1000)  # 注意这里duration需要转换为秒
        time.sleep(0.5)
        self.device.drag(start_x, start_y, end_x, end_y, duration=0.5)  # 滑动操作持续0.5秒

    def log(self, msg, type=0):
        if not self.debug:
            return
        print(msg)
        self.update_ui(msg, type)


engine_vee = EngineVee()

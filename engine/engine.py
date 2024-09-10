
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

    def set(self, global_data: AppData):
        self.global_data = global_data
        try:
            self.connect()
            self.update_ui("连接设备成功", 0)
        except Exception as e:
            self.update_ui(f"连接设备失败: {e}")

    def thread_stoped(self) -> bool:
        return self.global_data and self.global_data.thread_stoped()

    def update_ui(self, msg: str, type=0):
        self.global_data and self.global_data.update_ui(msg, type)

    def connect(self):
        addr = cfg_startup_vee.get('adb_port')
        self.device = u2.connect(addr)
        comparator_vee.set_device(self.device)
        # // 连接设备
        self.update_ui("连接设备")

    def check_in_app(self):
        current_app = self.device.app_current()
        self.package_name = current_app['package']
        self.update_ui(f"当前应用包名: {self.package_name}", 3)
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

    def stop_app(self):
        self.device.app_stop("com.netease.ma167")
        self.device.app_stop("com.netease.ma167.bilibili")

    def restart_game(self):
        self.update_ui("重启游戏")
        self.stop_app()
        time.sleep(1)
        self.start_app()
        self.update_ui(f"重启成功")

    def long_press_and_drag(self, start, end, duration=0.2):
        start_x, start_y = start
        end_x, end_y = end
        self.device.long_click(start_x, start_y, duration / 1000)  # 注意这里duration需要转换为秒
        self.device.drag(start_x, start_y, end_x, end_y, duration=0.1)  # 滑动操作持续0.5秒


engine_vee = EngineVee()

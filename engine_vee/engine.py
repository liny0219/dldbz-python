
from __future__ import annotations
from typing import TYPE_CHECKING
from utils.singleton import singleton
import uiautomator2 as u2
import cv2
from utils.config_loader import cfg_startup
import time

if TYPE_CHECKING:
    from global_data import GlobalData

appName = "com.netease.ma167"
appNameBilibili = "com.netease.ma167.bilibili"


@singleton
class EngineVee:
    def __init__(self):
        self.device = None
        self.package_name = None
        self.global_data = None
        self.connect()

    def set(self, global_data: GlobalData):
        self.global_data = global_data

    def thread_stoped(self) -> bool:
        return self.global_data and self.global_data.thread_stoped()

    def update_ui(self, msg: str):
        self.global_data and self.global_data.update_ui(msg)

    def connect(self):
        addr = cfg_startup.get('adb_port')
        self.device = u2.connect(addr)
        # // 连接设备
        self.log("连接设备")
        current_app = self.device.app_current()
        self.package_name = current_app['package']
        self.log(f"当前应用包名: {self.package_name}")

    def check_in_app(self):
        if self.package_name != appName and self.package_name != appNameBilibili:
            # 启动应用程序，需要确保已安装并可通过此包名启动
            self.device.app_start("com.netease.ma167")
            self.device.app_start("com.netease.ma167.bilibili")

    def restart_game(self):
        self.log("重启游戏")
        self.device.app_stop(self.package_name)
        time.sleep(1)
        self.device.app_start(self.package_name)
        self.log(f"{self.package_name} 重启成功")

    def match_point_color(self, x, y, expected_color, tolerance=5):
        """检查屏幕上的某一点颜色是否与期望颜色相匹配"""
        screenshot = self.device.screenshot(format='pillow')
        actual_color = screenshot.getpixel((x, y))
        print(f"actual_color: {actual_color} expected_color: {expected_color}")
        return all(abs(actual_color[i] - expected_color[i]) <= tolerance for i in range(3))

    def log(self, msg):
        print(msg)
        self.update_ui(msg)


engine_vee = EngineVee()

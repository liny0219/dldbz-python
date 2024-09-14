
from __future__ import annotations
import os
from typing import TYPE_CHECKING
from engine.comparator import comparator
from utils.singleton import singleton
import uiautomator2 as u2
from utils.config_loader import cfg_startup, cfg_engine
import time

if TYPE_CHECKING:
    from app_data import AppData

appName = "com.netease.ma167"
appNameBilibili = "com.netease.ma167.bilibili"
game_activity = "com.epicgames.ue4.GameActivity"


@singleton
class Engine:
    def __init__(self):
        self.device = None
        self.package_name = None
        self.app_data = None
        self.debug = False

        self.rand_press_px = 5
        self.press_duration = 300
        self.swipe_duration = 50
        self.operate_latency = 500
        self.default_sleep_ms = 10

    def set(self, app_data: AppData):
        self.app_data = app_data
        try:
            self.connect()
            self.update_ui("连接设备成功", 0)
        except Exception as e:
            self.update_ui(f"连接设备失败: {e}")

    def set_config(self):
        self.press_duration = cfg_engine.get('common.press_duration')
        self.default_sleep_ms = cfg_engine.get('common.default_sleep_ms')
        self.operate_latency = cfg_engine.get('common.operate_latency')
        self.rand_press_px = cfg_engine.get('common.rand_press_px')
        self.swipe_duration = cfg_engine.get('common.swipe_duration')

    def thread_stoped(self) -> bool:
        return self.app_data and self.app_data.thread_stoped()

    def update_ui(self, msg: str, type='info'):
        self.app_data and self.app_data.update_ui(msg, type)

    def connect(self):
        if self.device:
            return
        addr = cfg_startup.get('adb_port')
        self.device = u2.connect(addr)
        comparator.set_device(self.device)

    def check_in_app(self):
        current_app = self.device.app_current()
        self.package_name = current_app['package']
        self.update_ui(f"当前应用包名: {self.package_name}", 'debug')
        return self.package_name == appName or self.package_name == appNameBilibili

    def start_app(self):
        # 启动应用程序，需要确保已安装并可通过此包名启动
        self.update_ui("启动游戏")
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

    def write_to_file(self, str, file_path):
        try:
            # 使用 'a' 模式打开文件，追加内容
            with open(file_path, 'a', encoding='utf-8') as file:
                file.write(str)
            print(f"成功追加内容到文件：{file_path}, 内容: {str}")
        except Exception as e:
            print(f"追加内容时出错: {e}")

    def delete_file(self, file_path):
        try:
            # 检查文件是否存在
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"文件已成功删除: {file_path}")
            else:
                print(f"文件不存在: {file_path}")
        except Exception as e:
            print(f"删除文件时出错: {e}")

    def delete_files_with_prefix(self, directory, prefix):
        try:
            # 遍历指定目录中的所有文件
            for filename in os.listdir(directory):
                # 检查文件是否以指定前缀开头
                if filename.startswith(prefix):
                    file_path = os.path.join(directory, filename)
                    # 检查是否是文件（避免误删文件夹等其他项目）
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        print(f"已删除文件: {file_path}")
            print("文件删除完成。")
        except Exception as e:
            print(f"删除文件时出错: {e}")

    def delete_if_larger_than(self, file_path, size_in_mb):
        try:
            # 检查文件是否存在
            if os.path.exists(file_path):
                # 获取文件大小 (以字节为单位)
                file_size = os.path.getsize(file_path)
                # 将大小转换为MB (1MB = 1024 * 1024 字节)
                file_size_in_MB = file_size / (1024 * 1024)

                # 判断文件是否大于指定的大小
                if file_size_in_MB > size_in_mb:
                    os.remove(file_path)
                    print(f"已删除文件: {file_path}，文件大小: {file_size_in_MB:.2f} MB")
                else:
                    print(f"文件大小 {file_size_in_MB:.2f} MB, 不需要删除: {file_path}")
            else:
                print(f"文件不存在: {file_path}")
        except Exception as e:
            print(f"处理文件时出错: {e}")

    def press(self, coordinate, T=None, operate_latency=500):
        if not T:
            T = self.press_duration
        if self.device:
            x = coordinate[0]
            y = coordinate[1]
            self.device.long_click(x, y, duration=T / 1000.)
            self.sleep_ms(operate_latency)

    def light_swipe(self, start_coordinate, end_coordinate, T=None):
        if not T:
            T = self.swipe_duration
        if self.device:
            x_start, y_start = start_coordinate
            x_end, y_end = end_coordinate
            self.device.swipe(x_start, y_start, x_end, y_end, duration=T / 1000.)
            self.sleep_ms(100)

    def light_press(self, coordinate, T=None):
        self.press(coordinate, T=T, operate_latency=100)

    def sleep_ms(self, T=None):
        if not T:
            T = self.default_sleep_ms
        sleep_time_s = T / 1000.
        time.sleep(sleep_time_s)


engine = Engine()

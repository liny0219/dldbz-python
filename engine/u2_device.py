
from __future__ import annotations
import os
from typing import TYPE_CHECKING
from engine.comparator import comparator
from utils.singleton import singleton
import uiautomator2 as u2
from utils.config_loader import cfg_startup, cfg_engine
import time

from utils.status import App_Client

if TYPE_CHECKING:
    from app_data import AppData

appName = App_Client.NTES.value
appNameBilibili = App_Client.Bilibili.value
game_activity = "com.epicgames.ue4.GameActivity"


@singleton
class U2Device:
    def __init__(self):
        self.device = None
        self.package_name = None
        self.app_data = None
        self.debug = False

        self.cfg_rand_press_px = 5
        self.cfg_press_duration = 300
        self.cfg_swipe_duration = 50
        self.cfg_operate_latency = 500
        self.cfg_default_sleep_ms = 10

    def set(self, app_data: AppData):
        self.app_data = app_data
        try:
            if self.connect():
                self.update_ui("连接设备成功")
            else:
                self.update_ui("连接设备失败")
                app_data.thread.stop()
        except Exception as e:
            self.update_ui(f"连接设备失败: {e}")

    def set_config(self):
        self.cfg_press_duration = cfg_engine.get('common.press_duration')
        self.cfg_default_sleep_ms = cfg_engine.get('common.default_sleep_ms')
        self.cfg_operate_latency = cfg_engine.get('common.operate_latency')
        self.cfg_rand_press_px = cfg_engine.get('common.rand_press_px')
        self.cfg_swipe_duration = cfg_engine.get('common.swipe_duration')
        self.cfg_package_name = cfg_startup.get('package_name')

    def thread_stoped(self) -> bool:
        return self.app_data and self.app_data.thread_stoped()

    def update_ui(self, msg: str, type='info'):
        self.app_data and self.app_data.update_ui(msg, type)

    def connect(self):
        try:
            if self.device:
                return True
            addr = cfg_startup.get('adb_port')
            self.device = u2.connect(addr)
            comparator.set_device(self.device)
            return True
        except Exception as e:
            self.update_ui(f"连接设备失败: {e}")
            return False

    def reconnect(self):
        try:
            addr = cfg_startup.get('adb_port')
            self.device = u2.connect(addr)
            comparator.set_device(self.device)
            return True
        except Exception as e:
            return False

    def check_in_app(self):
        if not self.device:
            u2_device.reconnect()
        current_app = self.device.app_current()
        self.package_name = current_app['package']
        self.update_ui(f"当前应用包名: {self.package_name}", 'debug')
        self.update_ui(f"当前应用Activity: {current_app['activity']}", 'debug')
        return self.package_name == appName or self.package_name == appNameBilibili

    def start_app(self):
        # 启动应用程序，需要确保已安装并可通过此包名启动
        self.update_ui(f"启动应用程序: {self.cfg_package_name}")
        self.device.app_start(self.cfg_package_name)

    def check_in_game(self):
        if not self.device:
            return False
        activity = self.device.app_current().get('activity')
        if activity == game_activity:
            return True
        else:
            return False

    def stop_app(self):
        self.update_ui(f"停止应用程序: {self.cfg_package_name}")
        self.device.app_stop(self.cfg_package_name)

    def restart_game(self):
        self.update_ui("重启游戏")
        self.stop_app()
        time.sleep(1)
        self.start_app()
        self.update_ui(f"重启成功")

    def long_press_and_drag(self, start, end, duration=0.3):
        start_x, start_y = start
        end_x, end_y = end
        self.device.swipe(start_x, start_y, end_x, end_y, duration=duration)  # 滑动操作持续0.5秒

    def ensure_directory_exists(self, directory):
        # 检查目录是否存在
        if not os.path.exists(directory):
            try:
                # 如果目录不存在，则创建
                os.makedirs(directory)
                print(f"目录 {directory} 已创建。")
            except Exception as e:
                print(f"创建目录失败: {e}")
        else:
            print(f"目录 {directory} 已存在。")

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
                    print(f"已删除文件: {file_path}，文件大小: {file_size_in_MB:.1f} MB")
                else:
                    print(f"文件大小 {file_size_in_MB:.1f} MB, 不需要删除: {file_path}")
            else:
                print(f"文件不存在: {file_path}")
        except Exception as e:
            print(f"处理文件时出错: {e}")

    def get_directory_size(self, directory):
        total_size = 0
        # 遍历目录中的所有文件和子目录
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                if os.path.isfile(file_path):
                    total_size += os.path.getsize(file_path)
        return total_size

    def delete_files_in_directory(self, directory):
        # 遍历目录中的所有文件
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)  # 删除文件
                    print(f"已删除文件: {file_path}")
            except Exception as e:
                print(f"无法删除文件 {file_path}，错误信息: {e}")

    def check_and_delete(self, directory, size_in_mb=1):
        # 获取目录的总大小
        size_limit = size_in_mb * 1024 * 1024
        total_size = self.get_directory_size(directory)
        print(f"目录总大小: {total_size / (1024 * 1024):.2f} MB")

        # 如果目录大小超过限制，则删除目录中的所有文件
        if total_size > size_limit:
            print(f"目录大小超过 {size_limit / (1024 * 1024)} MB，正在删除目录中的所有文件...")
            self.delete_files_in_directory(directory)
        else:
            print("目录大小未超过限制，不执行删除操作。")

    def press(self, coordinate, T=None, operate_latency=500):
        if not T:
            T = self.cfg_press_duration
        if self.device:
            x = coordinate[0]
            y = coordinate[1]
            self.device.long_click(x, y, duration=T / 1000.)
            self.sleep_ms(operate_latency)

    def light_swipe(self, start_coordinate, end_coordinate, T=None):
        if not T:
            T = self.cfg_swipe_duration
        if self.device:
            x_start, y_start = start_coordinate
            x_end, y_end = end_coordinate
            self.device.swipe(x_start, y_start, x_end, y_end, duration=T / 1000.)
            self.sleep_ms(100)

    def light_press(self, coordinate, T=None):
        self.press(coordinate, T=T, operate_latency=100)

    def sleep_ms(self, T=None):
        if not T:
            T = self.cfg_default_sleep_ms
        sleep_time_s = T / 1000.
        time.sleep(sleep_time_s)

    def cleanup_large_files(self, directory, size_limit_mb=10):  # size_limit_mb默认为10MB
        """ 清理指定目录中所有超过给定大小（MB）的文件。 """
        size_limit_bytes = size_limit_mb * 1024 * 1024  # 将MB转换为字节
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    if os.path.getsize(file_path) > size_limit_bytes:
                        os.unlink(file_path)
                        print(f"Deleted {file_path} due to exceeding size limit of {size_limit_mb} MB.")
                elif os.path.isdir(file_path):
                    self.cleanup_large_files(file_path, size_limit_mb)  # 递归检查子目录
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')


u2_device = U2Device()
